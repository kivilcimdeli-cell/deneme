"""İNCE OTO LASTİK – isimlikteki QR ile açılan işletme sayfası (siyah, sade; telefona göre).

Uzar'ın sayfasıyla aynı işler, ayrı tasarım: siyah zemin, geniş ve kalın yazı (Archivo Expanded), tek vurgu rengi
kırmızı. Çizim yok; başlıkta yazının altından geçen ince kırmızı ışık çizgisi (gece geçen bir aracın stop lambası
izi). Animasyon yalnız açılışta, bir kez: yazı maskeden yükselir, ışık soldan geçip yerinde kalır, düğmeler sırayla
gelir. Sonra sayfa durur; dokunuşlarda yalnız düğme tepkileri.

Sayfada: Hemen Ara, WhatsApp (hazır mesajlı), Instagram, Google yorumları (işletmenin paylaşım bağlantısı), ödeme
bilgileri (alıcı, banka, IBAN + tek dokunuşla kopyala, banka karekodu: kaydedip banka uygulamasında galeriden
okutulur) ve Rehbere Kaydet (vCard). Dış bağlantı yok: yazı tipleri ve simgeler sayfanın içinde.

Bilgiler `ince_isimlik/bilgiler.json`dan okunur (scripts/qr_sistemi.py doğrular: IBAN mod-97, karekodun CRC'si,
içindeki IBAN ve alıcı). Banka karekodu bankanın verdiğiyle aynı baytlarla (UTF-8, ECI'siz, hata düzeltme Q)
yeniden çizilir; "HAFİSE İNCE"deki İ harfleri banka uygulamasında da aynı okunur.

Yayın: Uzar'daki gibi işletmenin Cloudflare hesabında bir Worker'a `ince_site.zip` yüklenir (pages.dev
Türkiye'de kapalı, workers.dev açık). Kesin adres `bilgiler.json` → `sayfa_url`a yazılır, bu komut yeniden
çalıştırılır (paylaşım kartı adresi kullanır) ve isimlikteki QR o adrese döner.

Çıktı : ince_isimlik/site/ (index.html, karekod.png, ince.vcf, og.png, fonts/*.woff), ince_isimlik/ince_site.zip,
        ince_isimlik/sayfa_onizleme.png (telefon ekranı), sayfa_animasyon.gif (açılış), sayfa_tur.gif (kaydırma,
        IBAN kopyala, karekod), sayfa_onizleme.html (tek dosya), sayfa_artifact.html (Claude önizlemesi)

Kullanım:
  pip install segno zxing-cpp playwright fonttools
  python3 scripts/ince_sayfa.py
"""
import base64
import html
import io
import math
import os
import random
import sys
import zipfile

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import qr_sistemi as Q  # noqa: E402
import uzar_sayfa as S  # noqa: E402

BASE = os.path.join(A.ROOT, "ince_isimlik")
DATA = os.path.join(BASE, "bilgiler.json")
OUT = os.path.join(BASE, "site")
ZIP = os.path.join(BASE, "ince_site.zip")
PREVIEW = os.path.join(BASE, "sayfa_onizleme.png")
GIF = os.path.join(BASE, "sayfa_animasyon.gif")
TOUR = os.path.join(BASE, "sayfa_tur.gif")
STANDALONE = os.path.join(BASE, "sayfa_onizleme.html")
ARTIFACT = os.path.join(BASE, "sayfa_artifact.html")
# Archivo (OFL): değişken yazı tipinden sabit kesimler (genişlik 125 / 100), latin + latin-ext birleşik
FONTS = {"display": "Archivo-ExpandedExtraBold.ttf", "display-sb": "Archivo-ExpandedSemiBold.ttf",
         "text": "Archivo-Medium.ttf", "text-sb": "Archivo-SemiBold.ttf"}
CHROMIUM = "/opt/pw-browsers/chromium"


# ---------------------------------------------------------------- dosyalar

def subset_fonts():
    from fontTools import subset
    os.makedirs(os.path.join(OUT, "fonts"), exist_ok=True)
    for key, fn in FONTS.items():
        opts = subset.Options()
        opts.flavor = "woff"
        opts.layout_features = ["kern", "liga", "locl", "tnum"]
        f = subset.load_font(os.path.join(A.FONT_DIR, fn), opts)
        s = subset.Subsetter(opts)
        s.populate(text=S.CHARS)
        s.subset(f)
        subset.save_font(f, os.path.join(OUT, "fonts", key + ".woff"), opts)
    with open(os.path.join(A.FONT_DIR, "OFL-archivo.txt"), "rb") as src, \
            open(os.path.join(OUT, "fonts", "OFL-archivo.txt"), "wb") as dst:
        dst.write(src.read())


def karekod_png(info):
    """Banka karekodu: bankanınkiyle aynı baytlar (UTF-8, ECI yok) ve aynı hata düzeltme (Q)."""
    import segno
    import zxingcpp
    path = os.path.join(OUT, "karekod.png")
    segno.make(info.karekod, error="q", mode="byte", encoding="utf-8", eci=False, micro=False,
               boost_error=False).save(path, scale=12, border=4)
    r = zxingcpp.read_barcodes(Image.open(path).convert("L"))
    assert len(r) == 1 and r[0].text == info.karekod and r[0].bytes == info.karekod.encode("utf-8"), "karekod"
    return path


def vcard(info):
    lines = ["BEGIN:VCARD", "VERSION:3.0", "N:;İnce Oto Lastik;;;", "FN:İnce Oto Lastik", "ORG:İnce Oto Lastik",
             f"TEL;TYPE=CELL,VOICE:+{info.tel}"] + ([f"URL:{info.page}"] if info.page else []) + [
             f"X-SOCIALPROFILE;TYPE=instagram:https://www.instagram.com/{info.instagram}/",
             f"NOTE:7/24 hizmet. IBAN {Q.iban_display(info.iban)} ({info.holder.title()}\\, {info.bank})",
             "END:VCARD"]
    with open(os.path.join(OUT, "ince.vcf"), "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(lines) + "\n")


def data_uri(fn, mime):
    return f"data:{mime};base64," + base64.b64encode(open(os.path.join(OUT, fn), "rb").read()).decode()


def embed_fonts(css):
    for key in FONTS:
        css = css.replace(f"url(fonts/{key}.woff)", f"url({data_uri('fonts/' + key + '.woff', 'font/woff')})")
    return css


# ---------------------------------------------------------------- lastik izi ve yol (çizim yok, yalnız iz)

def _along(P, step):
    """Bezier eğrisi (4 nokta) üzerinde `step` aralıklı noktalar: (x, y, tx, ty), t birim teğet."""
    def bz(t):
        u = 1 - t
        return tuple(u ** 3 * P[0][i] + 3 * u * u * t * P[1][i] + 3 * u * t * t * P[2][i] + t ** 3 * P[3][i]
                     for i in (0, 1))
    pts = [bz(i / 3000) for i in range(3001)]
    out, acc, nxt = [], 0.0, 0.0
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        d = math.hypot(xb - xa, yb - ya)
        while d and acc + d >= nxt:
            f = (nxt - acc) / d
            out.append((xa + (xb - xa) * f, ya + (yb - ya) * f, (xb - xa) / d, (yb - ya) / d))
            nxt += step
        acc += d
    return out


def tracks_svg(cls, P, size, gap=54.0, width=23.0, step=9.0, alpha=(0.22, 0.07), draw=False, seed=7):
    """İki teker izi (yandan çizim yok, yalnız asfalttaki baskı): altta koyu lastik sürtmesi, üstünde eğri
    boyunca gidiş yönüne bakan ok biçimli dişler ve omuz blokları; baştan sona soluklaşır, yer yer aşınmış.
    draw: açılışta iz eğri boyunca çizilir."""
    rnd = random.Random(seed)
    w = width
    k_ = w / 19.0
    shapes = [[(-1.6 * k_, -w * .30), (1.4 * k_, -w * .30), (4.6 * k_, 0), (1.4 * k_, w * .30), (-1.6 * k_, w * .30),
               (1.5 * k_, 0)],
              [(-1.8 * k_, -w / 2), (1.8 * k_, -w / 2), (1.8 * k_, -w * .38), (-1.8 * k_, -w * .38)],
              [(-1.8 * k_, w * .38), (1.8 * k_, w * .38), (1.8 * k_, w / 2), (-1.8 * k_, w / 2)]]
    pts = _along(P, step)
    polys = []
    smear = {-1: [], 1: []}
    for k, (x, y, tx, ty) in enumerate(pts):
        nx, ny = -ty, tx
        a = alpha[0] + (alpha[1] - alpha[0]) * k / max(1, len(pts) - 1)
        for side in (-1, 1):
            cx, cy = x + nx * side * gap / 2, y + ny * side * gap / 2
            smear[side].append(f"{cx:.1f} {cy:.1f}")
            o = a * rnd.uniform(.5, 1.0)
            for sh in shapes:
                q = " ".join(f"{cx + tx * u + nx * v:.1f},{cy + ty * u + ny * v:.1f}" for u, v in sh)
                polys.append(f'<polygon points="{q}" fill-opacity="{o:.3f}"/>')
    W, H = size
    d = "M{:.0f} {:.0f} C{:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f}".format(*[c for p in P for c in p])
    mask = (f'<defs><mask id="m-{cls}" maskUnits="userSpaceOnUse" x="-50" y="-50" width="{W + 100}" '
            f'height="{H + 100}"><path class="draw" d="{d}" pathLength="1" fill="none" stroke="#fff" '
            f'stroke-width="{gap + width + 40:.0f}"/></mask></defs>') if draw else ""
    m = f' mask="url(#m-{cls})"' if draw else ""
    (x0, y0), (x1, y1) = P[0], P[3]
    fade = (f'<linearGradient id="f-{cls}" gradientUnits="userSpaceOnUse" x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}">'
            f'<stop offset="0" stop-color="#000" stop-opacity=".55"/><stop offset="1" stop-color="#000" '
            f'stop-opacity=".12"/></linearGradient>')
    rubber = "".join(f'<path d="M{" L".join(v)}" fill="none" stroke="url(#f-{cls})" stroke-width="{w * .9:.0f}" '
                     f'stroke-linecap="round"/>' for v in smear.values())
    return (f'<svg class="{cls}" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" aria-hidden="true">'
            f'<defs>{fade}</defs>{mask}<g{m}>{rubber}<g fill="#fff">{"".join(polys)}</g></g></svg>')


def tread_tile(color="%23000"):
    """Lastik baskısı (Hemen Ara düğmesi, ödeme kartı): tek sıra ok biçimli diş, döşenir (data URI)."""
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' width='22' height='30' viewBox='0 0 22 30'>"
           f"<path d='M3 3h6l8 12-8 12H3l8-12z' fill='{color}'/></svg>")
    return "url(\"data:image/svg+xml," + svg + "\")"


def road(cls="road", tracks=""):
    """Yol şeridi: iki yanda düz kenar çizgisi, ortada kesik şerit (kaydırdıkça akar)."""
    return f'<div class="{cls}" aria-hidden="true">{tracks}<i class="lane"></i></div>'


HERO_TRACKS = dict(P=[(150, 440), (232, 360), (258, 190), (440, 40)], size=(390, 440))
MID_TRACKS = dict(P=[(-30, 74), (120, 40), (260, 22), (420, -16)], size=(390, 62), gap=30, width=12, step=6,
                  alpha=(0.24, 0.08), seed=3)


# ---------------------------------------------------------------- sayfa

CSS = """
@font-face{font-family:"Archivo Expanded";font-weight:800;font-display:swap;src:url(fonts/display.woff) format("woff")}
@font-face{font-family:"Archivo Expanded";font-weight:600;font-display:swap;src:url(fonts/display-sb.woff) format("woff")}
@font-face{font-family:"Archivo";font-weight:500;font-display:swap;src:url(fonts/text.woff) format("woff")}
@font-face{font-family:"Archivo";font-weight:600;font-display:swap;src:url(fonts/text-sb.woff) format("woff")}
/* gece yolu: asfalt başlık (savrulan iki lastik izi, stop lambası ışığı), altında yol; bölümler yolla ayrılır */
:root{color-scheme:dark;--bg:#09090a;--surface:#111113;--raise:#18181b;--line:#232327;--line2:#34343a;
  --text:#f3f2ef;--muted:#8f8f97;--dim:#5f5f66;--red:#d0202a;--glow:#ff3a44;--ok:#1f9d55;--paper:#ffffff;
  --lane:#dedcd5;--asphalt:#141417;
  --display:"Archivo Expanded","Archivo","Arial Black",sans-serif;
  --ui:"Archivo",system-ui,-apple-system,"Segoe UI",sans-serif;
  --grain:radial-gradient(circle at 1px 1px,rgba(255,255,255,.045) 1px,transparent 1.5px) 0 0/5px 5px,
          radial-gradient(circle at 3px 3px,rgba(0,0,0,.45) 1.2px,transparent 1.8px) 0 0/7px 7px}
*{box-sizing:border-box;margin:0}
html{background:var(--bg);-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--text);font:500 16px/1.4 var(--ui);min-height:100vh;overflow-x:hidden;
  padding-bottom:env(safe-area-inset-bottom)}
.wrap{--gl:max(16px,env(safe-area-inset-left,0px));--gr:max(16px,env(safe-area-inset-right,0px));
  max-width:480px;margin:0 auto;padding-left:var(--gl);padding-right:var(--gr);padding-block:0 30px}
a{color:inherit;-webkit-tap-highlight-color:transparent}
:focus-visible{outline:2px solid var(--glow);outline-offset:3px}
.bleed{margin-left:calc(var(--gl) * -1);margin-right:calc(var(--gr) * -1)}
/* ---- başlık: asfalt ---- */
.hero{position:relative;overflow:hidden;isolation:isolate;padding:52px var(--gr) 96px var(--gl);
  background:radial-gradient(60% 45% at 92% 4%,rgba(208,32,42,.24),transparent 70%),
             radial-gradient(70% 50% at 20% 0%,rgba(255,244,230,.07),transparent 70%),var(--grain),var(--asphalt);
  box-shadow:inset 0 -40px 60px -30px rgba(0,0,0,.6)}
.hero .tracks{position:absolute;inset:0;width:100%;height:100%;z-index:-1}
.eyebrow{display:flex;align-items:center;gap:10px;font:600 11px/1 var(--display);letter-spacing:.32em;color:var(--muted)}
.eyebrow::before{content:"";width:18px;height:2px;background:var(--red)}
.logo{margin-top:22px;overflow:hidden;padding-top:.1em;font:800 clamp(70px,24vw,124px)/.9 var(--display);
  letter-spacing:-.025em;text-shadow:0 10px 30px rgba(0,0,0,.55)}
.logo span{display:block}
.streak{position:relative;height:2px;margin:18px calc(var(--gr) * -1) 0 0;
  background:linear-gradient(90deg,rgba(208,32,42,0),var(--red) 35%,var(--glow) 80%,#ffd2d4);
  box-shadow:0 0 12px 1px rgba(255,58,68,.55),0 0 34px 4px rgba(208,32,42,.35);transform-origin:left center}
.streak::after{content:"";position:absolute;top:-7px;right:0;width:90px;height:16px;border-radius:50%;
  background:radial-gradient(closest-side,rgba(255,220,222,.95),rgba(255,58,68,.5) 45%,transparent);filter:blur(2px)}
.kind{margin-top:16px;font:600 15px/1 var(--display);letter-spacing:.46em}
.note{margin-top:12px;color:var(--muted);font-size:15px;max-width:30ch}
/* ---- yol: kenar çizgileri, ortada kesik şerit ---- */
.road{position:relative;height:62px;overflow:hidden;
  background:linear-gradient(var(--lane),var(--lane)) 0 8px/100% 2px no-repeat,
             linear-gradient(var(--lane),var(--lane)) 0 calc(100% - 8px)/100% 2px no-repeat,var(--grain),#18181b;
  border-block:1px solid #000}
.road .lane{position:absolute;left:-80px;right:-80px;top:calc(50% - 2px);height:4px;
  background:repeating-linear-gradient(90deg,var(--lane) 0 40px,transparent 40px 76px);
  background-position:calc(var(--drive,0px) * -1) 0;opacity:.92}
.road .tracks{position:absolute;inset:0;width:100%;height:100%}
.hero .road{position:absolute;left:0;right:0;bottom:0;z-index:1}
.mid{margin-top:34px}
/* ---- bölümler ---- */
.label{display:flex;align-items:center;gap:12px;margin:30px 0 12px;font:600 11px/1 var(--display);
  letter-spacing:.3em;color:var(--dim)}
.label::after{content:"";flex:1;height:1px;background:var(--line)}
.call{position:relative;overflow:hidden;isolation:isolate;display:flex;align-items:center;gap:16px;
  padding:18px 18px 18px 20px;border-radius:14px;text-decoration:none;color:#fff;
  background:linear-gradient(115deg,#d6252f,#b3141d);box-shadow:0 18px 40px -22px rgba(255,58,68,.75);
  transition:transform .12s,filter .12s}
.call::before{content:"";position:absolute;inset:-2px;z-index:-1;background:TREAD 0 0/22px 30px;opacity:.16;
  -webkit-mask-image:linear-gradient(100deg,transparent 35%,#000 92%);mask-image:linear-gradient(100deg,transparent 35%,#000 92%);
  background-position:right -6px top 0}
.call:active{transform:scale(.985);filter:brightness(1.08)}
.call .t{flex:1;min-width:0}
.call small{display:block;font:600 11px/1 var(--display);letter-spacing:.3em;color:rgba(255,255,255,.8)}
.call b{display:block;margin-top:9px;font:800 clamp(19px,6.2vw,25px)/1 var(--display);letter-spacing:-.01em;
  font-variant-numeric:tabular-nums;white-space:nowrap}
.call .ib{flex:none;display:grid;place-items:center;width:46px;height:46px;border-radius:50%;background:#fff;
  box-shadow:0 0 0 6px rgba(255,255,255,.12)}
.call .ib .ic{width:22px;height:22px;fill:var(--red)}
.links{margin-top:12px;border:1px solid var(--line);border-radius:14px;background:var(--surface);overflow:hidden}
.row{display:flex;align-items:center;gap:14px;padding:14px 16px;text-decoration:none;transition:background .12s}
.row+.row{border-top:1px solid var(--line)}
.row:active{background:var(--raise)}
.row .ib{flex:none;display:grid;place-items:center;width:42px;height:42px;border-radius:11px;background:var(--raise);
  border:1px solid var(--line2)}
.row .ic{width:21px;height:21px;fill:var(--text)}
.row .t{flex:1;min-width:0}
.row b{display:block;font:600 16px/1.2 var(--ui)}
.row small{display:block;margin-top:2px;font-size:13.5px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;
  white-space:nowrap}
.stars{color:#f2b01e;letter-spacing:.08em;margin-right:4px}
.chev{flex:none;width:9px;height:9px;border:solid var(--dim);border-width:2px 2px 0 0;transform:rotate(45deg);
  margin-right:4px}
.pay{position:relative;overflow:hidden;isolation:isolate;padding:20px;border:1px solid var(--line);border-radius:14px;
  background:var(--surface);container-type:inline-size}
.pay::before{content:"";position:absolute;z-index:-1;top:-40px;right:-34px;width:66px;height:260px;
  background:TREAD_LIGHT 0 0/22px 30px;opacity:.07;transform:rotate(-24deg);
  -webkit-mask-image:linear-gradient(transparent,#000 30%,#000 60%,transparent);
  mask-image:linear-gradient(transparent,#000 30%,#000 60%,transparent)}
.rows{display:grid;grid-template-columns:auto 1fr;gap:8px 18px;font-size:15px}
.rows dt{color:var(--muted)}
.rows dd{font-weight:600}
.iban{margin:18px 0 12px;padding:12px 8px 14px;border-radius:10px;background:var(--bg);border:1px solid var(--line2);
  text-align:center}
.iban span{display:block;font:600 10px/1 var(--display);letter-spacing:.3em;color:var(--dim)}
.iban output{display:block;margin-top:9px;font:600 18px/1.1 var(--ui);font-size:min(20px,5cqi);
  letter-spacing:.01em;word-spacing:.1em;font-variant-numeric:tabular-nums;white-space:nowrap;user-select:all;
  -webkit-user-select:all}
.btn{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;min-height:52px;border-radius:12px;
  font:600 13px/1 var(--display);letter-spacing:.14em;cursor:pointer;text-decoration:none;transition:transform .12s}
.btn:active{transform:scale(.985)}
.btn .ic{width:19px;height:19px}
.copy{border:0;background:var(--paper);color:var(--bg)}
.copy .ic{fill:var(--bg)}
.copy.ok{background:var(--ok);color:#fff}
.copy.ok .ic{fill:#fff}
details.kk{margin-top:10px}
details.kk summary{list-style:none}
details.kk summary::-webkit-details-marker{display:none}
.ghost{border:1px solid var(--line2);background:transparent;color:var(--text)}
.ghost .ic{fill:var(--text)}
.kk-body{margin-top:14px;text-align:center}
.kk-body .qr{display:inline-block;padding:12px;border-radius:12px;background:var(--paper)}
.kk-body img{display:block;width:min(230px,64vw);height:auto;image-rendering:pixelated}
.kk-body p{margin:12px 6px 10px;font-size:14px;color:var(--muted)}
.kk-body p b{color:var(--text);font-weight:600}
.kk-body a{color:var(--text);font-weight:600;text-underline-offset:3px}
.save{margin-top:12px}
footer{position:relative;margin-top:36px;padding-top:22px;display:flex;justify-content:space-between;
  align-items:baseline;gap:12px;color:var(--dim);font-size:12.5px}
footer::before{content:"";position:absolute;top:0;left:0;right:0;height:3px;
  background:repeating-linear-gradient(90deg,var(--line2) 0 26px,transparent 26px 46px)}
footer b{font:800 12px/1 var(--display);letter-spacing:.2em;color:var(--muted)}
.toast{position:fixed;left:50%;bottom:calc(22px + env(safe-area-inset-bottom));transform:translate(-50%,140%);
  width:max-content;max-width:calc(100vw - 28px);text-align:center;background:var(--raise);color:var(--text);
  border:1px solid var(--line2);border-left:4px solid var(--red);padding:12px 18px;border-radius:12px;font-weight:600;
  box-shadow:0 14px 34px rgba(0,0,0,.6);transition:transform .25s,opacity .25s;opacity:0;pointer-events:none}
.toast.show{transform:translate(-50%,0);opacity:1}
/* ---- açılış: araç geçer (iz çizilir, stop lambası ışığı), yazı yükselir, yol şeridi akıp durur; bir kez ---- */
@keyframes up{from{transform:translateY(105%)}to{transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
@keyframes sweep{from{transform:scaleX(0);opacity:.2}to{transform:none;opacity:1}}
@keyframes head{0%{opacity:0;transform:translateX(-120vw)}25%{opacity:1}100%{opacity:1;transform:none}}
@keyframes track{from{letter-spacing:.9em;opacity:0}to{letter-spacing:.46em;opacity:1}}
@keyframes drawn{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
@keyframes lanes{from{transform:translateX(150px)}to{transform:none}}
@keyframes flash{0%{border-color:var(--glow);background:#1b0b0c}100%{border-color:var(--line2);background:var(--bg)}}
@keyframes open{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}
.draw{stroke-dasharray:1 1;stroke-dashoffset:0;animation:drawn 1.25s .05s cubic-bezier(.45,.1,.25,1) both}
.hero .lane{animation:lanes 1.4s cubic-bezier(.15,.7,.2,1) both}
.eyebrow{animation:fade .6s .2s both}
.logo span{animation:up .85s .3s cubic-bezier(.2,.75,.15,1) both}
.streak{animation:sweep 1.05s .55s cubic-bezier(.3,.6,.1,1) both}
.streak::after{animation:head 1.05s .55s cubic-bezier(.3,.6,.1,1) both}
.kind{animation:track .9s .65s cubic-bezier(.2,.8,.2,1) both}
.note{animation:fade .6s .9s both}
.label,.call,.links,.mid,.pay,.save,footer{animation:rise .6s cubic-bezier(.2,.8,.2,1) both}
.label{animation-delay:.95s}.call{animation-delay:1.02s}.links{animation-delay:1.1s}.mid{animation-delay:1.14s}
.label.late{animation-delay:1.18s}.pay{animation-delay:1.22s}.save,footer{animation-delay:1.28s}
.iban.flash{animation:flash .9s ease-out}
details.kk[open] .kk-body{animation:open .3s cubic-bezier(.2,.8,.2,1)}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
""".replace("TREAD_LIGHT", tread_tile("%23fff")).replace("TREAD", tread_tile())

JS = S.JS + """
if(!matchMedia('(prefers-reduced-motion: reduce)').matches){let f=0;const r=document.documentElement.style;
  addEventListener('scroll',()=>{if(!f){f=requestAnimationFrame(()=>{r.setProperty('--drive',(scrollY*.9).toFixed(1)+'px');f=0})}},{passive:true})}
"""


def page(info, standalone=False, artifact=False):
    """Site (`ince_isimlik/site`), tek dosya önizleme (standalone: yazı tipleri ve karekod gömülü) ya da Claude
    önizleme sayfası (artifact: belge iskeleti yayında eklenir; oradaki çerçeve indirmeyi engellediği için
    karekod ve rehber indirme bağlantısı yok; telefon bağlantısı her izleyicide çalışmayabildiği için Hemen Ara
    numarayı da kopyalar)."""
    standalone = standalone or artifact
    e = html.escape
    wa = Q.whatsapp_link(info)
    insta = f"https://www.instagram.com/{info.instagram}/"
    title = "İnce Oto Lastik – 7/24 Hizmet"
    desc = "İnce Oto Lastik: hemen arayın, WhatsApp'tan yazın, Instagram, Google yorumları ve ödeme bilgileri."
    css, kk = (embed_fonts(CSS), data_uri("karekod.png", "image/png")) if standalone else (CSS, "karekod.png")
    # aynı sekmede açılır: yeni sekme QR okuyucuların iç tarayıcılarında çoğu zaman açılmaz
    row = lambda href, icon, t, s: (  # noqa: E731
        f'<a class="row" href="{e(href)}"><span class="ib">{icon}</span>'
        f'<span class="t"><b>{e(t)}</b><small>{s}</small></span><span class="chev"></span></a>')
    tel_extra = f' data-tel="{e(info.phone)}"' if artifact else ""
    save = "Karekoda basılı tutup kaydedin," if artifact else "Karekodu kaydedin,"
    save_link = "" if artifact else f'\n        <a href="{kk}" download="ince-karekod.png">Karekodu kaydet</a>'
    vcf = "" if artifact else (f'<a class="btn ghost save" href="ince.vcf" download="İnce Oto Lastik.vcf">'
                               f'{S.svg(S.ICON["person"])}REHBERE KAYDET</a>\n')
    og = (f'<meta property="og:url" content="{e(info.page)}">\n<meta property="og:image" content="{e(info.page)}og.png">'
          if info.page else "")
    favicon = ("data:image/svg+xml," + "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>"
               "<rect width='64' height='64' rx='14' fill='%2309090a'/>"
               "<rect x='10' y='38' width='44' height='4' rx='2' fill='%23d0202a'/>"
               "<rect x='27' y='14' width='10' height='20' rx='2' fill='%23f3f2ef'/></svg>")
    body = f"""<div class="wrap">
<header class="hero bleed">
  {tracks_svg("tracks", draw=True, **HERO_TRACKS)}
  <p class="eyebrow">7/24 HİZMET</p>
  <h1 class="logo" aria-label="İnce"><span>İNCE</span></h1>
  <div class="streak" aria-hidden="true"></div>
  <p class="kind">OTO LASTİK</p>
  <p class="note">Günün her saatinde bir telefon uzağınızdayız.</p>
  {road()}
</header>
<main>
<p class="label">İLETİŞİM</p>
<a class="call" href="tel:+{info.tel}"{tel_extra}><span class="t"><small>HEMEN ARA</small><b>{e(info.phone)}</b></span>
  <span class="ib">{S.svg(S.ICON["phone"])}</span></a>
<nav class="links" aria-label="Bağlantılar">
  {row(wa, S.svg(S.logo_path("whatsapp")), "WhatsApp", "Mesaj gönderin")}
  {row(insta, S.svg(S.logo_path("instagram")), "Instagram", "@" + e(info.instagram))}
  {row(info.google, S.svg(S.ICON["star"]), "Google yorumları", '<span class="stars">★★★★★</span>Bizi değerlendirin')}
</nav>
{road("road mid bleed", tracks_svg("tracks", **MID_TRACKS))}
<p class="label late">ÖDEME</p>
<section class="pay" aria-label="Ödeme bilgileri">
  <dl class="rows"><dt>Alıcı</dt><dd>{e(info.holder)}</dd><dt>Banka</dt><dd>{e(info.bank)}</dd></dl>
  <div class="iban"><span>IBAN</span><output class="iban-no">{e(Q.iban_display(info.iban))}</output></div>
  <button class="btn copy" type="button" data-copy="{e(info.iban)}">{S.svg(S.ICON["copy"])}<span>IBAN'I KOPYALA</span></button>
  <details class="kk">
    <summary class="btn ghost">{S.svg(S.ICON["qr"])}KAREKOD İLE ÖDE</summary>
    <div class="kk-body">
      <span class="qr"><img src="{kk}" width="732" height="732" alt="{e(info.bank)} karekodu – {e(info.holder)}"></span>
      <p>{save} banka uygulamanızda <b>Karekod ile Öde</b>, ardından <b>Galeriden seç</b>.</p>{save_link}
    </div>
  </details>
</section>
{vcf}</main>
<footer><b>İNCE OTO LASTİK</b><span>7/24 hizmet</span></footer>
</div>
<div class="toast" role="status" aria-live="polite"></div>
<script>{JS}</script>
"""
    if artifact:
        return f"""<title>İnce Oto Lastik</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>{css}</style>
{body}"""
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#141417">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
{og}
<link rel="icon" href="{favicon}">
<style>{css}</style>
</head>
<body>
{body}</body>
</html>
"""


# ---------------------------------------------------------------- görseller

def og_image():
    """Bağlantı paylaşılınca görünen kapak (1200 × 630): başlığın aynısı, büyük."""
    from playwright.sync_api import sync_playwright
    doc = f"""<!doctype html><meta charset="utf-8"><style>{embed_fonts(CSS)}
body{{margin:0}} .hero{{width:1200px;height:630px;margin:0;padding:96px 90px 0}}
.eyebrow{{font-size:22px;gap:18px}} .eyebrow::before{{width:36px;height:4px}} .logo{{font-size:220px;margin-top:40px}}
.streak{{height:4px;margin:30px -90px 0 0}} .kind{{font-size:34px;margin-top:34px}} .road{{height:90px}}</style>
<div class="hero">{tracks_svg("tracks", **HERO_TRACKS)}<p class="eyebrow">7/24 HİZMET</p>
<h1 class="logo"><span>İNCE</span></h1><div class="streak"></div><p class="kind">OTO LASTİK</p>{road()}</div>"""
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        pg = b.new_page(viewport={"width": 1200, "height": 630}, reduced_motion="reduce")
        pg.set_content(doc)
        pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(OUT, "og.png"))
        b.close()


def screenshot(path=PREVIEW):
    """Telefon ekranında (390 px): üst görünüm ve tüm sayfa (karekod açık) yan yana."""
    from playwright.sync_api import sync_playwright
    top, full = path.replace(".png", "_ust.png"), path.replace(".png", "_tam.png")
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, reduced_motion="reduce")
        pg.goto("file://" + os.path.join(OUT, "index.html"))
        pg.wait_for_timeout(400)
        assert pg.evaluate("document.fonts.check('800 20px \"Archivo Expanded\"')"), "yazı tipi yüklenmedi"
        assert pg.evaluate("document.documentElement.scrollWidth") <= 390, "yatay taşma"
        assert pg.evaluate("(e=>e.scrollWidth<=e.clientWidth)(document.querySelector('.iban-no'))"), "IBAN sığmadı"
        assert pg.evaluate("[...document.querySelectorAll('.call b,.row small')]"
                           ".every(e=>e.scrollWidth<=e.clientWidth)"), "yazı sığmadı"
        pg.screenshot(path=top)
        pg.click("details.kk summary")
        pg.wait_for_timeout(200)
        pg.screenshot(path=full, full_page=True)
        b.close()
    shots = [Image.open(top), Image.open(full)]
    h = max(s.height for s in shots)
    canvas = Image.new("RGB", (sum(s.width for s in shots) + 120, h + 120), (52, 52, 58))
    x = 40
    for s in shots:
        canvas.paste(s, (x, 60))
        x += s.width + 40
    canvas.save(path)
    for f in (top, full):
        os.remove(f)
    return path


def _gif(frames, durs, path):
    pal = [f.quantize(colors=160, method=Image.Quantize.MEDIANCUT) for f in frames]
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=durs, loop=0, optimize=True)
    return path


def _seek(pg, ms):
    pg.evaluate(f"document.getAnimations().forEach(a=>{{a.pause();a.currentTime={ms:.0f}}})")


def animation_gif(path=GIF, seconds=2.0, step=0.06):
    """Açılış: tüm animasyonlar durdurulup zamanda adım adım ilerletilerek çekilir (kare kare aynı)."""
    from playwright.sync_api import sync_playwright
    frames = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        pg = b.new_page(viewport={"width": 390, "height": 700}, device_scale_factor=1)
        pg.goto("file://" + os.path.join(OUT, "index.html"))
        _seek(pg, 0)
        pg.wait_for_timeout(300)
        for k in range(int(seconds / step) + 1):
            _seek(pg, k * step * 1000)
            frames.append(Image.open(io.BytesIO(pg.screenshot())).convert("RGB"))
        b.close()
    durs = [int(step * 1000)] * len(frames)
    durs[-1] = 1800
    return _gif(frames, durs, path)


def tour_gif(path=TOUR):
    """Tam tur (390 × 844): açılış, aşağı kaydırma, IBAN'ı kopyala, karekod; dokunulan yer halkayla gösterilir."""
    from playwright.sync_api import sync_playwright
    frames, durs = [], []

    def shot(pg, ms=100, tap=None):
        im = Image.open(io.BytesIO(pg.screenshot())).convert("RGB")
        if tap:
            d = ImageDraw.Draw(im, "RGBA")
            d.ellipse((tap[0] - 22, tap[1] - 22, tap[0] + 22, tap[1] + 22), fill=(255, 255, 255, 70),
                      outline=(255, 255, 255, 230), width=3)
        frames.append(im)
        durs.append(ms)

    def tap_on(pg, sel):
        box = pg.locator(sel).bounding_box()
        return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2

    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=1,
                            permissions=["clipboard-read", "clipboard-write"])
        pg = ctx.new_page()
        pg.goto("file://" + os.path.join(OUT, "index.html"))
        _seek(pg, 0)
        pg.wait_for_timeout(300)
        for k in range(0, 1800, 80):
            _seek(pg, k)
            shot(pg, 80)
        pg.evaluate("document.getAnimations().forEach(a=>a.finish())")
        shot(pg, 1200)
        h = pg.evaluate("document.documentElement.scrollHeight - innerHeight")
        for y in range(0, h + 1, 40):
            pg.evaluate(f"scrollTo(0,{y})")
            shot(pg, 60)
        pg.evaluate(f"scrollTo(0,{h})")
        shot(pg, 500)
        tap = tap_on(pg, ".copy")
        shot(pg, 300, tap)
        pg.mouse.click(*tap)
        for _ in range(5):
            pg.wait_for_timeout(120)
            shot(pg, 160)
        durs[-1] = 1000
        pg.wait_for_timeout(2300)
        tap = tap_on(pg, "details.kk summary")
        shot(pg, 300, tap)
        pg.mouse.click(*tap)
        pg.wait_for_timeout(350)
        h2 = pg.evaluate("document.documentElement.scrollHeight - innerHeight")
        for y in range(h, h2 + 1, 40):
            pg.evaluate(f"scrollTo(0,{y})")
            shot(pg, 60)
        pg.evaluate(f"scrollTo(0,{h2})")
        shot(pg, 2400)
        b.close()
    return _gif(frames, durs, path)


def pack():
    """Yüklemeye hazır zip: index.html en üstte."""
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for d, _, files in os.walk(OUT):
            for fn in sorted(files):
                full = os.path.join(d, fn)
                z.write(full, os.path.relpath(full, OUT))


def main():
    info = Q.load(DATA)
    if os.path.isdir(os.path.join(OUT, "fonts")):           # eski yazı tipleri zip'e girmesin
        for fn in os.listdir(os.path.join(OUT, "fonts")):
            os.remove(os.path.join(OUT, "fonts", fn))
    os.makedirs(OUT, exist_ok=True)
    subset_fonts()
    karekod_png(info)
    vcard(info)
    og_image()
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(page(info))
    with open(ARTIFACT, "w", encoding="utf-8") as f:
        f.write(page(info, artifact=True))
    with open(STANDALONE, "w", encoding="utf-8") as f:
        f.write(page(info, standalone=True))
    pack()
    print("sayfa:", os.path.relpath(os.path.join(OUT, "index.html"), A.ROOT), "→", info.page or "(adres yayından sonra)")
    print("önizleme:", *(os.path.relpath(f(), A.ROOT) for f in (screenshot, animation_gif, tour_gif)))


if __name__ == "__main__":
    main()
