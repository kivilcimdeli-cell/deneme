"""İNCE OTO LASTİK – isimlikteki QR ile açılan işletme sayfası (lastik temalı, animasyonlu; telefona göre).

Uzar'ın sayfasıyla aynı işler, ayrı tasarım: açık zemin, asfalt başlık. Başlıkta yola yuvarlanarak gelen ve yolda
dönen lastik (yanağında İNCE OTO LASTİK yazısı, dönmeyen kırmızı kaliper), akan yol çizgileri, ardında kalan lastik
izi. Düğme simgeleri küçük lastiklerin içinde; dokununca döner.

Sayfada: Hemen Ara, WhatsApp (hazır mesajlı), Instagram, Google'da yorum (işletmenin paylaşım bağlantısı), ödeme
bilgileri (alıcı, banka, IBAN + tek dokunuşla kopyala, banka karekodu: kaydedip banka uygulamasında galeriden
okutulur) ve Rehbere Kaydet (vCard). Dış bağlantı yok: yazı tipleri ve simgeler sayfanın içinde.

Bilgiler `ince_isimlik/bilgiler.json`dan okunur (scripts/qr_sistemi.py doğrular: IBAN mod-97, karekodun CRC'si,
içindeki IBAN ve alıcı). Banka karekodu bankanın verdiğiyle aynı baytlarla (UTF-8, ECI'siz, hata düzeltme Q)
yeniden çizilir; "HAFİSE İNCE"deki İ harfleri banka uygulamasında da aynı okunur.

Yayın: Uzar'daki gibi işletmenin Cloudflare hesabında bir Worker'a `ince_site.zip` yüklenir (pages.dev
Türkiye'de kapalı, workers.dev açık). Kesin adres `bilgiler.json` → `sayfa_url`a yazılır, bu komut yeniden
çalıştırılır (paylaşım kartı adresi kullanır) ve isimlikteki QR o adrese döner.

Çıktı : ince_isimlik/site/ (index.html, karekod.png, ince.vcf, og.png, fonts/*.woff), ince_isimlik/ince_site.zip,
        ince_isimlik/sayfa_onizleme.png (telefon ekranı), sayfa_animasyon.gif (açılış), sayfa_onizleme.html (tek
        dosya: uygulamada önizleme)

Kullanım:
  pip install segno zxing-cpp playwright fonttools
  python3 scripts/ince_sayfa.py
"""
import base64
import html
import math
import os
import sys
import zipfile

from PIL import Image

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
STANDALONE = os.path.join(BASE, "sayfa_onizleme.html")
RED, INK = "#d0202a", "#121316"
FONTS = {"russo": "RussoOne-Regular.ttf", "outfit": "Outfit-SemiBold.ttf", "outfit-xb": "Outfit-ExtraBold.ttf"}
CHROMIUM = "/opt/pw-browsers/chromium"


# ---------------------------------------------------------------- lastik çizimleri (SVG)

def _pt(r, deg):
    a = math.radians(deg)
    return f"{r * math.cos(a):.2f},{r * math.sin(a):.2f}"


def tire_svg(cls="tire"):
    """Büyük lastik, viewBox merkezde (0, 0): diş blokları, yanakta yazı, gümüş jant (5 kol), dönmeyen kaliper.
    Dönen iki katman (.spin): lastik + yanak + jant içi, kollar + göbek; kaliper aralarında sabit kalır."""
    n = 30
    blocks = "".join(f'<polygon points="{_pt(99, a - 4.1)} {_pt(99, a + 4.1)} {_pt(87, a + 3.0)} {_pt(87, a - 3.0)}"/>'
                     for a in (360 / n * i for i in range(n)))
    sipes = "".join(f'<line x1="{_pt(98, a).split(",")[0]}" y1="{_pt(98, a).split(",")[1]}" '
                    f'x2="{_pt(90, a + 2).split(",")[0]}" y2="{_pt(90, a + 2).split(",")[1]}"/>'
                    for a in (360 / n * i for i in range(n)))
    spokes = "".join(f'<polygon points="-4.2,-13 4.2,-13 9.5,-57 -9.5,-57" transform="rotate({72 * k})"/>'
                     for k in range(5))
    nuts = "".join(f'<circle cx="{_pt(8.2, 72 * k - 90).split(",")[0]}" cy="{_pt(8.2, 72 * k - 90).split(",")[1]}" '
                   f'r="2.2"/>' for k in range(5))
    word = "İNCE OTO LASTİK • 7/24 HİZMET • "
    caliper = f'M {_pt(58, 196)} A 58 58 0 0 1 {_pt(58, 244)} L {_pt(41, 240)} A 41 41 0 0 0 {_pt(41, 200)} Z'
    return f"""<svg class="{cls}" viewBox="-100 -100 200 200" aria-hidden="true">
<defs>
<linearGradient id="rim" x1="0" y1="-1" x2="0" y2="1"><stop offset="0" stop-color="#f1f2f4"/>
<stop offset=".5" stop-color="#b8bcc4"/><stop offset="1" stop-color="#e2e4e8"/></linearGradient>
<linearGradient id="spoke" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#9ca1aa"/>
<stop offset=".45" stop-color="#eef0f3"/><stop offset="1" stop-color="#a7abb3"/></linearGradient>
<path id="sw" d="M -73 0 a 73 73 0 1 1 146 0 a 73 73 0 1 1 -146 0"/>
</defs>
<g class="spin">
<circle r="99.5" fill="#0d0e10"/>
<g fill="#2b2c31">{blocks}</g>
<g stroke="#0d0e10" stroke-width="1.6">{sipes}</g>
<circle r="86" fill="#1a1b1f"/>
<circle r="84" fill="none" stroke="#2c2d33" stroke-width="1.2"/>
<text class="sidewall" font-size="10.5" fill="#76787f" letter-spacing="1.5"><textPath href="#sw" xlink:href="#sw" textLength="452"
lengthAdjust="spacing">{word}{word}</textPath></text>
<circle r="64" fill="#2a2c31"/>
<circle r="61.5" fill="none" stroke="url(#rim)" stroke-width="5"/>
<circle r="99.5" fill="none"/>
</g>
<path d="{caliper}" fill="{RED}"/>
<path d="M {_pt(54, 204)} A 54 54 0 0 1 {_pt(54, 236)}" fill="none" stroke="#ff7b80" stroke-width="2"
stroke-linecap="round" opacity=".7"/>
<g class="spin">
<circle r="60" fill="none"/>
<g fill="url(#spoke)" stroke="#7d828b" stroke-width=".6">{spokes}</g>
<circle r="14.5" fill="#dfe1e5" stroke="#8e939b" stroke-width="1"/>
<g fill="#80858e">{nuts}</g>
<circle r="4.8" fill="{RED}"/>
</g>
</svg>"""


def mini_tire(icon, cls="mt"):
    """Küçük lastik: koyu lastik (dönen diş halkası), beyaz jant, ortada simge."""
    n = 16
    notches = "".join(f'<polygon points="{_pt(49, a - 5)} {_pt(49, a + 5)} {_pt(41, a + 3.5)} {_pt(41, a - 3.5)}"/>'
                      for a in (360 / n * i for i in range(n)))
    return (f'<span class="{cls}"><svg class="mt-tire" viewBox="-50 -50 100 100" aria-hidden="true">'
            f'<g class="mt-spin"><circle r="49" fill="#141518"/><g fill="#34353b">{notches}</g>'
            f'<circle r="49" fill="none"/></g><circle r="33" fill="#fff"/></svg>{icon}</span>')


def tread_strip(cls="track"):
    """Lastik izi şeridi (ok biçimli diş blokları): başlığın altında, lastik geçince çizilir."""
    blocks = "".join(f'<path d="M{x} 3 h9 l7 9 l-7 9 h-9 l7 -9 z"/><path d="M{x + 12} 3 h3 l7 9 l-7 9 h-3 l7 -9 z"/>'
                     for x in range(0, 420, 24))
    return (f'<svg class="{cls}" viewBox="0 0 400 24" preserveAspectRatio="xMinYMid slice" aria-hidden="true">'
            f'{blocks}</svg>')


# ---------------------------------------------------------------- dosyalar

def subset_fonts():
    from fontTools import subset
    os.makedirs(os.path.join(OUT, "fonts"), exist_ok=True)
    for key, fn in FONTS.items():
        opts = subset.Options()
        opts.flavor = "woff"
        opts.layout_features = ["kern", "liga", "locl"]
        f = subset.load_font(os.path.join(A.FONT_DIR, fn), opts)
        s = subset.Subsetter(opts)
        s.populate(text=S.CHARS + "★")
        s.subset(f)
        subset.save_font(f, os.path.join(OUT, "fonts", key + ".woff"), opts)
    for lic in ("OFL-russoone.txt", "OFL-outfit.txt"):
        with open(os.path.join(A.FONT_DIR, lic), "rb") as src, open(os.path.join(OUT, "fonts", lic), "wb") as dst:
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


# ---------------------------------------------------------------- sayfa

CSS = """
@font-face{font-family:"Russo One";font-weight:400;font-display:swap;src:url(fonts/russo.woff) format("woff")}
@font-face{font-family:"Outfit";font-weight:600;font-display:swap;src:url(fonts/outfit.woff) format("woff")}
@font-face{font-family:"Outfit";font-weight:800;font-display:swap;src:url(fonts/outfit-xb.woff) format("woff")}
:root{color-scheme:light;--red:#d0202a;--red2:#a3141c;--ink:#121316;--asphalt:#1c1d21;--paper:#f1f0ec;--card:#fff;
  --line:#e2e0da;--muted:#6c6e75;--star:#f2a900;
  --head:"Russo One","Arial Black",sans-serif;--ui:"Outfit",system-ui,-apple-system,"Segoe UI",sans-serif}
*{box-sizing:border-box;margin:0}
html{background:var(--paper);-webkit-text-size-adjust:100%}
body{background:var(--paper);color:var(--ink);font:600 16px/1.35 var(--ui);min-height:100vh;overflow-x:hidden;
  padding-bottom:env(safe-area-inset-bottom)}
.wrap{--gl:max(16px,env(safe-area-inset-left,0px));--gr:max(16px,env(safe-area-inset-right,0px));
  max-width:460px;margin:0 auto;padding:0 var(--gr) 26px var(--gl)}
a{color:inherit;-webkit-tap-highlight-color:transparent}
/* ---- başlık: asfalt, lastik, yol ---- */
.hero{position:relative;overflow:hidden;min-height:380px;margin:0 calc(var(--gr) * -1) 0 calc(var(--gl) * -1);
  padding:40px 22px 0;color:#fff;isolation:isolate;
  background:radial-gradient(circle at 1px 1px,rgba(255,255,255,.05) 1px,transparent 1.6px) 0 0/7px 7px,
             radial-gradient(120% 90% at 85% 70%,#2a2b30 0,#1c1d21 55%,#141518 100%)}
.logo{font:400 clamp(66px,24vw,104px)/.9 var(--head);letter-spacing:.02em;position:relative;z-index:2;
  text-shadow:0 6px 24px rgba(0,0,0,.5)}
.kind{margin-top:10px;font:400 21px/1 var(--head);letter-spacing:.3em;color:var(--red);position:relative;z-index:2}
.badge{display:inline-flex;align-items:center;gap:9px;margin-top:18px;padding:7px 13px 7px 11px;border-radius:99px;
  border:1.5px solid rgba(255,255,255,.22);background:rgba(0,0,0,.25);font:800 13px/1 var(--ui);letter-spacing:.2em;
  position:relative;z-index:2}
.badge .dot{width:9px;height:9px;border-radius:50%;background:#2fd36b;box-shadow:0 0 0 0 rgba(47,211,107,.6)}
.road{position:absolute;left:0;right:0;bottom:0;height:46px;background:linear-gradient(#2e2f35,#25262b);
  border-top:2px solid #3a3b42}
.road::before{content:"";position:absolute;left:0;right:0;top:20px;height:4px;
  background:repeating-linear-gradient(90deg,#e9e7e1 0 46px,transparent 46px 80px)}
.tire-wrap{position:absolute;right:-58px;bottom:24px;width:min(64vw,250px);aspect-ratio:1;z-index:1}
.tire-wrap::after{content:"";position:absolute;left:12%;right:12%;bottom:-7px;height:14px;border-radius:50%;
  background:rgba(0,0,0,.55);filter:blur(5px);z-index:-1}
.tire{display:block;width:100%;height:100%;overflow:visible;filter:drop-shadow(0 8px 14px rgba(0,0,0,.45))}
.tire .spin{transform-box:fill-box;transform-origin:center}
.tire .sidewall{font-family:var(--head)}
.wind{position:absolute;right:calc(min(64vw,250px) - 40px);bottom:60px;width:90px;height:70px;z-index:0}
.wind i{position:absolute;right:0;height:3px;border-radius:3px;background:rgba(255,255,255,.35)}
.wind i:nth-child(1){top:6px;width:70px}.wind i:nth-child(2){top:30px;width:46px}.wind i:nth-child(3){top:54px;width:60px}
.track{display:block;width:calc(100% + var(--gl) + var(--gr));height:24px;margin:0 calc(var(--gr) * -1) 0 calc(var(--gl) * -1);
  fill:#d4d2cb}
/* ---- bölümler ---- */
.label{display:flex;align-items:center;gap:10px;margin:22px 2px 12px;font:800 12px/1 var(--ui);letter-spacing:.3em;
  color:var(--muted)}
.label::before{content:"";width:22px;height:4px;border-radius:2px;background:var(--red)}
.mt{position:relative;flex:none;display:grid;place-items:center;width:58px;height:58px}
.mt-tire{position:absolute;inset:0;width:100%;height:100%}
.mt-spin{transform-box:fill-box;transform-origin:center}
.mt .ic{position:relative;width:24px;height:24px;fill:var(--ink)}
.call{position:relative;overflow:hidden;display:flex;align-items:center;gap:14px;padding:14px 16px 14px 12px;
  border-radius:22px;text-decoration:none;color:#fff;background:linear-gradient(115deg,var(--red),var(--red2));
  box-shadow:0 14px 30px -14px rgba(208,32,42,.8)}
.call .mt .ic{fill:var(--red)}
.call .t{flex:1;min-width:0}
.call b{display:block;font:400 25px/1 var(--head);letter-spacing:.04em}
.call small{display:block;margin-top:6px;font:800 19px/1 var(--ui);letter-spacing:.05em;color:#ffe3e5}
.call .go{flex:none;width:12px;height:12px;border:solid #fff;border-width:3px 3px 0 0;transform:rotate(45deg);
  margin-right:6px}
.call::after{content:"";position:absolute;top:0;bottom:0;left:0;width:40%;pointer-events:none;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.26),transparent)}
.tiles{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:12px}
.tile{display:flex;flex-direction:column;align-items:center;gap:8px;padding:14px 6px 13px;border-radius:18px;
  background:var(--card);border:1px solid var(--line);text-decoration:none;text-align:center;
  box-shadow:0 6px 16px -12px rgba(0,0,0,.35);transition:transform .12s}
.tile:active{transform:scale(.97)}
.tile b{font:400 clamp(13px,3.9vw,16px)/1 var(--head);letter-spacing:.02em}
.tile small{max-width:100%;font-size:12px;line-height:1.1;color:var(--muted);overflow:hidden;text-overflow:ellipsis;
  white-space:nowrap}
.mt .ic.star{fill:var(--star)}
.mt .hub{position:relative;width:8px;height:8px;border-radius:50%;background:var(--red)}
.pay{position:relative;margin-top:24px;background:var(--card);border:1px solid var(--line);border-radius:22px;
  overflow:hidden;container-type:inline-size;box-shadow:0 10px 26px -18px rgba(0,0,0,.4)}
.pay .strip{display:block;width:100%;height:16px;background:var(--asphalt);fill:#4a4b52}
.pay .in{padding:18px 18px 18px}
.pay h2{display:flex;align-items:center;gap:9px;font:400 17px/1 var(--head);letter-spacing:.08em}
.pay h2 .ic{width:22px;height:22px;fill:var(--red)}
.rows{margin:16px 0 4px;display:grid;grid-template-columns:auto 1fr;gap:6px 14px;font-size:15px}
.rows dt{color:var(--muted)}
.iban{margin:12px 0 14px;padding:14px 8px;border-radius:14px;background:#f7f6f3;border:1.5px dashed #c8c5bd;
  font:800 18px/1.1 var(--ui);font-size:min(22px,4.8cqi);letter-spacing:.01em;word-spacing:.06em;text-align:center;
  white-space:nowrap;user-select:all;-webkit-user-select:all}
.copy,.kk-open,.ghost{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;min-height:54px;
  border-radius:16px;font:400 17px/1 var(--head);letter-spacing:.06em;cursor:pointer;text-decoration:none}
.copy{border:0;background:var(--ink);color:#fff}
.copy .ic{width:20px;height:20px;fill:#fff}
.copy.ok{background:#1d7a3a}
details.kk{margin-top:10px}
details.kk summary{list-style:none}
details.kk summary::-webkit-details-marker{display:none}
.kk-open{border:2px solid var(--ink);background:transparent;color:var(--ink)}
.kk-open .ic{width:20px;height:20px;fill:var(--ink)}
.kk-body{padding-top:14px;text-align:center}
.kk-body img{width:min(250px,72vw);height:auto;image-rendering:pixelated;border-radius:8px}
.kk-body p{margin:10px 4px 12px;font-size:14px;color:#4a4b52}
.kk-body a{color:var(--red);font-weight:800}
.ghost{margin-top:14px;border:2px solid var(--ink);color:var(--ink);background:transparent}
.ghost .ic{width:22px;height:22px;fill:var(--ink)}
footer{display:flex;align-items:center;justify-content:center;gap:10px;margin-top:26px;color:var(--muted);
  font:800 11px/1 var(--ui);letter-spacing:.28em}
footer .mt{width:26px;height:26px}
.toast{position:fixed;left:50%;bottom:calc(22px + env(safe-area-inset-bottom));transform:translate(-50%,140%);
  background:var(--ink);color:#fff;border-left:6px solid var(--red);padding:12px 18px;border-radius:12px;
  font-weight:600;box-shadow:0 12px 30px rgba(0,0,0,.35);transition:transform .25s,opacity .25s;width:max-content;
  max-width:calc(100vw - 28px);text-align:center;
  opacity:0;pointer-events:none}
.toast.show{transform:translate(-50%,0);opacity:1}
/* ---- animasyonlar: lastik yola yuvarlanarak gelir ve döner, yol akar, iz çizilir, düğmeler sırayla gelir ---- */
@keyframes rollin{from{transform:translateX(calc(-100vw - 110%))}to{transform:none}}
@keyframes rollspin{from{transform:rotate(-560deg)}to{transform:none}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes drive{to{background-position:-80px 0}}
@keyframes draw{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@keyframes drop{0%{opacity:0;transform:translateY(-30px) scale(1.15)}60%{opacity:1;transform:translateY(4px)}
  100%{opacity:1;transform:none}}
@keyframes spread{from{opacity:0;letter-spacing:0}to{opacity:1;letter-spacing:.3em}}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(47,211,107,.6)}70%,100%{box-shadow:0 0 0 9px rgba(47,211,107,0)}}
@keyframes gust{0%{opacity:0;transform:translateX(30px)}30%{opacity:1}100%{opacity:0;transform:translateX(-50px)}}
@keyframes shine{0%{transform:translateX(-130%) skewX(-20deg)}30%,100%{transform:translateX(260%) skewX(-20deg)}}
@keyframes wheelin{from{opacity:0;transform:translateX(-26px) rotate(-300deg)}to{opacity:1;transform:none}}
@keyframes ring{0%,8%,100%{transform:none}1%,5%{transform:rotate(-16deg)}3%,7%{transform:rotate(16deg)}}
@keyframes once{to{transform:rotate(360deg)}}
@keyframes pop{0%{transform:scale(1)}40%{transform:scale(1.05)}100%{transform:scale(1)}}
@keyframes flash{0%{background:#ffe3e5;border-color:var(--red)}100%{background:#f7f6f3}}
@keyframes open{from{opacity:0;transform:translateY(-8px) scale(.96)}to{opacity:1;transform:none}}
.tire-wrap{animation:rollin 1.3s cubic-bezier(.12,.7,.25,1) both}
.tire .spin{animation:rollspin 1.3s cubic-bezier(.12,.7,.25,1) both,spin 4s 1.3s linear infinite}
.road::before{animation:drive .44s linear infinite}
.wind i{opacity:0;animation:gust 1.3s 1.3s ease-out infinite}
.wind i:nth-child(2){animation-delay:1.7s}.wind i:nth-child(3){animation-delay:2.1s}
.logo{animation:drop .7s .2s cubic-bezier(.2,.8,.2,1) both}
.kind{animation:spread .8s .45s cubic-bezier(.2,.8,.2,1) both}
.badge{animation:rise .6s .65s cubic-bezier(.2,.8,.2,1) both}
.badge .dot{animation:pulse 1.8s 1.2s infinite}
.track{animation:draw 1.3s cubic-bezier(.12,.7,.25,1) both}
.label{animation:rise .5s .8s both}
.call{animation:rise .6s .9s cubic-bezier(.2,.8,.2,1) both}
.call::after{animation:shine 4.5s 2s infinite}
.call .ic{animation:ring 4.5s 2s infinite}
.mt-spin{animation:spin 6s linear infinite}
.tile{animation:rise .5s cubic-bezier(.2,.8,.2,1) both}
.tile .mt{animation:wheelin .8s cubic-bezier(.2,.8,.2,1) both}
.tile:nth-child(1),.tile:nth-child(1) .mt{animation-delay:1s}
.tile:nth-child(2),.tile:nth-child(2) .mt{animation-delay:1.1s}
.tile:nth-child(3),.tile:nth-child(3) .mt{animation-delay:1.2s}
.mt.go .mt-spin{animation:once .5s cubic-bezier(.2,.8,.2,1)}
.copy.ok{animation:pop .35s}
.iban.flash{animation:flash .9s ease-out}
details.kk[open] .kk-body{animation:open .35s cubic-bezier(.2,.8,.2,1)}
footer .mt-spin{animation-duration:3s}
@media (prefers-reduced-motion:no-preference){
  .js .reveal{transition:opacity .6s,transform .6s cubic-bezier(.2,.8,.2,1)}
  .js .reveal:not(.seen){opacity:0;transform:translateY(26px)}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}
  .wind{display:none}}
"""

JS = S.JS + """
const io='IntersectionObserver' in window?new IntersectionObserver(es=>es.forEach(e=>{
  if(e.isIntersecting){e.target.classList.add('seen');io.unobserve(e.target)}}),{threshold:.15}):null;
document.querySelectorAll('.reveal').forEach(el=>io?io.observe(el):el.classList.add('seen'));
document.querySelectorAll('.tile,.call').forEach(a=>a.addEventListener('pointerdown',()=>{
  const m=a.querySelector('.mt');m.classList.remove('go');void m.offsetWidth;m.classList.add('go')}));
document.querySelectorAll('.mt').forEach(m=>m.addEventListener('animationend',()=>m.classList.remove('go')));
"""


def page(info, standalone=False):
    """Site (`ince_isimlik/site`) ya da tek dosya önizleme (standalone=True: yazı tipleri ve karekod gömülü)."""
    e = html.escape
    wa = Q.whatsapp_link(info)
    insta = f"https://www.instagram.com/{info.instagram}/"
    title = "İnce Oto Lastik – 7/24 Hizmet"
    desc = "İnce Oto Lastik: hemen arayın, WhatsApp'tan yazın, Instagram, Google yorumları ve ödeme bilgileri."
    css, kk = CSS, "karekod.png"
    if standalone:
        for key in FONTS:
            css = css.replace(f"url(fonts/{key}.woff)", f"url({data_uri('fonts/' + key + '.woff', 'font/woff')})")
        kk = data_uri("karekod.png", "image/png")
    # aynı sekmede açılır: yeni sekme QR okuyucuların iç tarayıcılarında çoğu zaman açılmaz
    tile = lambda href, icon, t, s: (  # noqa: E731
        f'<a class="tile" href="{e(href)}">{mini_tire(icon)}<b>{e(t)}</b><small>{s}</small></a>')
    og = (f'<meta property="og:url" content="{e(info.page)}">\n<meta property="og:image" content="{e(info.page)}og.png">'
          if info.page else "")
    favicon = ("data:image/svg+xml," + "<svg xmlns='http://www.w3.org/2000/svg' viewBox='-50 -50 100 100'>"
               "<circle r='48' fill='%23121316'/><circle r='30' fill='%23d4d6da'/><circle r='9' fill='%23d0202a'/>"
               "</svg>")
    body = f"""<div class="wrap">
<header class="hero">
  <h1 class="logo" aria-label="İnce">İNCE</h1>
  <p class="kind">OTO LASTİK</p>
  <p class="badge"><span class="dot"></span>7/24 HİZMET</p>
  <div class="road"></div>
  <div class="wind" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="tire-wrap">{tire_svg()}</div>
</header>
{tread_strip()}
<p class="label">BİZE ULAŞIN</p>
<a class="call" href="tel:+{info.tel}">{mini_tire(S.svg(S.ICON["phone"]))}<span class="t"><b>HEMEN ARA</b>
  <small>{e(info.phone)}</small></span><span class="go"></span></a>
<nav class="tiles">
  {tile(wa, S.svg(S.logo_path("whatsapp")), "WhatsApp", "Mesaj yazın")}
  {tile(insta, S.svg(S.logo_path("instagram")), "Instagram", "@" + e(info.instagram))}
  {tile(info.google, S.svg(S.ICON["star"], "ic star"), "Google", "Yorum yapın")}
</nav>
<section class="pay reveal" aria-labelledby="odeme">
  {tread_strip("strip")}
  <div class="in">
  <h2 id="odeme">{S.svg(S.ICON["bank"])}ÖDEME BİLGİLERİ</h2>
  <dl class="rows"><dt>Alıcı</dt><dd>{e(info.holder)}</dd><dt>Banka</dt><dd>{e(info.bank)}</dd></dl>
  <div class="iban" aria-label="IBAN">{e(Q.iban_display(info.iban))}</div>
  <button class="copy" type="button" data-copy="{e(info.iban)}">{S.svg(S.ICON["copy"])}<span>IBAN'I KOPYALA</span></button>
  <details class="kk">
    <summary class="kk-open">{S.svg(S.ICON["qr"])}KAREKOD İLE ÖDE</summary>
    <div class="kk-body">
      <img src="{kk}" width="732" height="732" alt="{e(info.bank)} karekodu – {e(info.holder)}">
      <p>Karekodu kaydedin; banka uygulamanızda <b>Karekod ile Öde</b> → <b>Galeriden seç</b>.</p>
      <a href="{kk}" download="ince-karekod.png">Karekodu kaydet</a>
    </div>
  </details>
  </div>
</section>
<a class="ghost reveal" href="ince.vcf" download="İnce Oto Lastik.vcf">{S.svg(S.ICON["person"])}REHBERE KAYDET</a>
<footer class="reveal">{mini_tire('<i class="hub"></i>')}İNCE OTO LASTİK · 7/24 HİZMET</footer>
</div>
<div class="toast" role="status" aria-live="polite"></div>
<script>{JS}</script>
"""
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#1c1d21">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
{og}
<link rel="icon" href="{favicon}">
<script>document.documentElement.classList.add("js")</script>
<style>{css}</style>
</head>
<body>
{body}</body>
</html>
"""


# ---------------------------------------------------------------- görseller

def og_image():
    """Bağlantı paylaşılınca görünen kapak (1200 × 630): başlıktaki gibi asfalt, yol ve lastik."""
    from playwright.sync_api import sync_playwright
    css = CSS
    for key in FONTS:
        css = css.replace(f"url(fonts/{key}.woff)", f"url({data_uri('fonts/' + key + '.woff', 'font/woff')})")
    doc = f"""<!doctype html><meta charset="utf-8"><style>{css}
body{{margin:0;background:#1c1d21}} .hero{{width:1200px;height:630px;margin:0;padding:90px 80px 0}}
.logo{{font-size:230px}} .kind{{font-size:50px;margin-top:22px}} .badge{{font-size:28px;padding:14px 26px;margin-top:40px}}
.badge .dot{{width:18px;height:18px}} .tire-wrap{{width:560px;right:-60px;bottom:52px}} .road{{height:96px}}
.road::before{{top:44px;height:8px}} .wind{{display:none}}</style>
<div class="hero"><h1 class="logo">İNCE</h1><p class="kind">OTO LASTİK</p>
<p class="badge"><span class="dot"></span>7/24 HİZMET</p><div class="road"></div>
<div class="tire-wrap">{tire_svg()}</div></div>"""
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
    url = "file://" + os.path.join(OUT, "index.html")
    top, full = path.replace(".png", "_ust.png"), path.replace(".png", "_tam.png")
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, reduced_motion="reduce")
        pg.goto(url)
        pg.wait_for_timeout(400)
        assert pg.evaluate("document.fonts.check('20px \"Russo One\"')"), "yazı tipi yüklenmedi"
        assert pg.evaluate("document.documentElement.scrollWidth") <= 390, "yatay taşma"
        assert pg.evaluate("(e=>e.scrollWidth<=e.clientWidth)(document.querySelector('.iban'))"), "IBAN sığmadı"
        assert pg.evaluate("[...document.querySelectorAll('.tile small,.tile b')].every(e=>e.scrollWidth<=e.clientWidth)"), \
            "kutucuk yazısı sığmadı"
        pg.screenshot(path=top)
        pg.click("details.kk summary")
        pg.wait_for_timeout(200)
        pg.screenshot(path=full, full_page=True)
        b.close()
    shots = [Image.open(top), Image.open(full)]
    h = max(s.height for s in shots)
    canvas = Image.new("RGB", (sum(s.width for s in shots) + 120, h + 120), (214, 216, 220))
    x = 40
    for s in shots:
        canvas.paste(s, (x, 60))
        x += s.width + 40
    canvas.save(path)
    for f in (top, full):
        os.remove(f)
    return path


def animation_gif(path=GIF, seconds=3.2, step=0.08):
    """Açılış animasyonu: tüm animasyonlar durdurulup zamanda adım adım ilerletilerek çekilir (kare kare aynı)."""
    from playwright.sync_api import sync_playwright
    frames = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        pg = b.new_page(viewport={"width": 390, "height": 700}, device_scale_factor=1)
        pg.goto("file://" + os.path.join(OUT, "index.html"))
        pg.evaluate("document.getAnimations().forEach(a=>a.pause())")
        pg.wait_for_timeout(300)
        for k in range(int(seconds / step) + 1):
            pg.evaluate(f"document.getAnimations().forEach(a=>{{a.pause();a.currentTime={k * step * 1000:.0f}}})")
            frames.append(Image.open(__import__("io").BytesIO(pg.screenshot())).convert("RGB"))
        b.close()
    pal = [f.quantize(colors=128, method=Image.Quantize.MEDIANCUT) for f in frames]
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=int(step * 1000), loop=0, optimize=True)
    return path


def pack():
    """Yüklemeye hazır zip: index.html en üstte."""
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for d, _, files in os.walk(OUT):
            for fn in sorted(files):
                full = os.path.join(d, fn)
                z.write(full, os.path.relpath(full, OUT))


def main():
    info = Q.load(DATA)
    os.makedirs(OUT, exist_ok=True)
    subset_fonts()
    karekod_png(info)
    vcard(info)
    og_image()
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(page(info))
    with open(STANDALONE, "w", encoding="utf-8") as f:
        f.write(page(info, standalone=True))
    pack()
    print("sayfa:", os.path.relpath(os.path.join(OUT, "index.html"), A.ROOT), "→", info.page or "(adres yayından sonra)")
    print("önizleme:", os.path.relpath(screenshot(), A.ROOT), os.path.relpath(animation_gif(), A.ROOT))


if __name__ == "__main__":
    main()
