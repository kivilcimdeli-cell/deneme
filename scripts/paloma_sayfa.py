"""PALOMA GRIDA – Süleyman Boylu'nun dijital kartviziti (isimlikteki QR bu sayfayı açar).

İsimliklerle aynı konsept ve aynı yazı tipleri: Paloma mavisi bant içinde PALOMA HOTELS | GRIDA, Lora ad soyad,
yanında ince mavi dikey çizgi, aralıklı büyük harf görev, mavi kart içinde QR (DİJİTAL | KARTVİZİT). Açık temada
beyaz tabla, telefon koyu moddaysa siyah tabla renkleri.

Animasyon:
  * Açılış (~2 sn): PALOMA harfleri sırayla iner, HOTELS harfleri ortadan yerlerine açılır, ayraç uzar, GRIDA
    soldan belirir; kart yükselir, ad ve soyad maskeden çıkar, yanındaki mavi çizgi yukarıdan aşağı uzar, görevin
    harf aralığı açılır, düğmeler sırayla gelir ve simgeleri çizilir.
  * Kaydırma: logo yavaş kayar ve solar; iletişim satırları soldan, alt çizgileri uzayarak gelir; QR kareleri
    çapraz dalgayla belirir, üstünden bir kez tarama ışığı geçer; ara düğmeleri ekrandan çıkınca altta
    Ara / WhatsApp şeridi açılır.
  * Sürekli: dalgalar akar, QR'ın vizör köşeleri nefes alır, Rehbere kaydet'in üstünden ara ara ışık geçer.
  "Hareketi azalt" açıksa hiçbiri oynamaz, sayfa doğrudan son hâliyle açılır.

Dış bağlantı yok: yazı tipleri (Montserrat, Lora; OFL) sayfanın yanında, logo ve simgeler sayfanın içinde.
Logo: paloma_isimlik/logo/paloma_hotels.json (scripts/paloma_logo.py). Bilgiler `paloma_isimlik/bilgiler.json`.

Yayın: ortak Cloudflare hesabında (`qrsistem`) `suleymanboylu` adlı Worker'a `paloma_site.zip` yüklenir; adres
`https://suleymanboylu.qrsistem.workers.dev` (isimliklerdeki QR bu adresi açar).

Çıktı : paloma_isimlik/site/, paloma_isimlik/paloma_site.zip, sayfa_onizleme.png (açık, tam sayfa, koyu),
        sayfa_tur.gif (açılış ve kaydırma)

Kullanım:
  python3 scripts/paloma_sayfa.py            # site, zip, önizleme ve tur
  python3 scripts/paloma_sayfa.py --hizli    # GIF'siz
"""
import html
import io
import json
import math
import os
import shutil
import sys
import zipfile

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import paloma_logo as L  # noqa: E402
import qr_sistemi as Q  # noqa: E402
from ince_sayfa import _finish, _gif, _seek  # noqa: E402

BASE = os.path.join(A.ROOT, "paloma_isimlik")
OUT = os.path.join(BASE, "site")
ZIP = os.path.join(BASE, "paloma_site.zip")
PREVIEW = os.path.join(BASE, "sayfa_onizleme.png")
TOUR = os.path.join(BASE, "sayfa_tur.gif")
CHROMIUM = "/opt/pw-browsers/chromium"
FONTS = {"sans": "Montserrat_600SemiBold.ttf", "sans-b": "Montserrat_700Bold.ttf", "serif": "Lora_700Bold.ttf"}
LICENSES = ("OFL-montserrat.txt", "OFL-lora.txt")
VCF = "suleyman-boylu.vcf"
OG = "paylas.png"
LOGO = json.load(open(L.JSON, encoding="utf-8"))
PALOMA_BLUE = (105, 161, 186)

ICON = {
    "phone": '<path d="M6.6 3.5h2.6l1.4 4.2-2 1.4a12 12 0 0 0 6.3 6.3l1.4-2 4.2 1.4v2.6a2 2 0 0 1-2.2 2A16.5 16.5 0 0 1 '
             '4.6 5.7a2 2 0 0 1 2-2.2z"/>',
    "office": '<path d="M4 20V6.5L12 3l8 3.5V20"/><path d="M9 20v-5h6v5M8 9h1M11.5 9h1M15 9h1M8 12h1M11.5 12h1M15 12h1"/>',
    "whatsapp": '<path d="M4.5 19.5l1.2-4A8 8 0 1 1 9 18.6z"/><path class="f" fill="currentColor" stroke="none" '
                'd="M9.2 8.6c.2-.5.6-.6.9-.6.4 0 .6.6.9 1.4.2.5-.4.9-.6 1.2.6 1.2 1.6 2.2 2.9 2.8.3-.3.7-.9 1.2-.7.8.3 '
                '1.4.6 1.4 1 0 .3-.1.7-.6.9-.7.4-1.7.4-3-.2a8 8 0 0 1-3.4-3.3c-.5-1.1-.5-1.9.3-2.5z"/>',
    "mail": '<rect x="3.5" y="5.5" width="17" height="13" rx="2.5"/><path d="M4 7l8 6 8-6"/>',
    "pin": '<path d="M12 21s-6.5-6-6.5-11a6.5 6.5 0 0 1 13 0c0 5-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.4"/>',
    "save": '<circle cx="9" cy="8.5" r="3.5"/><path d="M3.5 19c.8-3.2 3-4.8 5.5-4.8 1.4 0 2.7.4 3.7 1.3M17.5 13v7M14 16.5h7"/>',
    "share": '<circle cx="17.5" cy="5.5" r="2.5"/><circle cx="6.5" cy="12" r="2.5"/><circle cx="17.5" cy="18.5" r="2.5"/>'
             '<path d="M8.7 10.8l6.6-4M8.7 13.2l6.6 4"/>',
    "arrow": '<path d="M9 5l7 7-7 7"/>',
}


def icon(k, draw=False):
    """draw: çizgiler açılışta çizilsin diye her çizgi parçasına pathLength=1 (dolgulu parça, class="f", hariç)."""
    body = ICON[k]
    if draw:
        for tag in ("<path ", "<rect ", "<circle "):
            body = body.replace(tag + "d=", tag + 'pathLength="1" d=').replace(tag + "x=", tag + 'pathLength="1" x=')
            body = body.replace(tag + "cx=", tag + 'pathLength="1" cx=')
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{body}</svg>')


def e(s):
    return html.escape(str(s))


def load():
    d = json.load(open(os.path.join(BASE, "bilgiler.json"), encoding="utf-8"))
    d["cep_e164"] = Q.phone_e164(d["cep"])
    d["sirket_e164"] = Q.phone_e164(d["sirket_tel"])
    d["cep_txt"] = Q.phone_display(d["cep_e164"])
    d["sirket_txt"] = Q.phone_display(d["sirket_e164"])
    d["qr"] = Q.https_url(d["sayfa_url"]).rstrip("/")             # isimlikteki QR ile aynı içerik
    return d


# ---------------------------------------------------------------- dosyalar

def subset_fonts(text):
    from fontTools import subset
    fdir = os.path.join(OUT, "fonts")
    shutil.rmtree(fdir, ignore_errors=True)
    os.makedirs(fdir)
    chars = text + "ABCÇDEFGĞHIİJKLMNOÖPQRSŞTUÜVWXYZabcçdefgğhıijklmnoöpqrsştuüvwxyz0123456789 .,:;·+-–—/@&()'\"!?"
    for key, fn in FONTS.items():
        opts = subset.Options()
        opts.flavor = "woff"
        opts.layout_features = ["kern", "liga", "locl", "tnum"]
        f = subset.load_font(os.path.join(A.FONT_DIR, fn), opts)
        s = subset.Subsetter(opts)
        s.populate(text=chars)
        s.subset(f)
        subset.save_font(f, os.path.join(fdir, key + ".woff"), opts)
    for lic in LICENSES:
        shutil.copy(os.path.join(A.FONT_DIR, lic), os.path.join(fdir, lic))


def vcard(d):
    first, last = d["isim"].split(" ", 1)
    street, district, city, country = d["adres"]
    lines = ["BEGIN:VCARD", "VERSION:3.0", f"N:{last};{first};;;", f"FN:{d['isim']}",
             f"ORG:{d['grup']};{d['otel']}", f"TITLE:{d['gorev']}",
             f"TEL;TYPE=CELL,VOICE:+{d['cep_e164']}", f"TEL;TYPE=WORK,VOICE:+{d['sirket_e164']}",
             f"EMAIL;TYPE=INTERNET:{d['eposta']}",
             f"ADR;TYPE=WORK:;;{street};{district};{city};;{country}", f"URL:{d['sayfa_url']}", "END:VCARD"]
    with open(os.path.join(OUT, VCF), "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(lines) + "\n")


def spaced(dr, xy, text, font, gap, fill, anchor="l"):
    """Harf aralıklı yazı; anchor "c": ortası x'te. Döner: genişlik."""
    w = sum(dr.textlength(ch, font=font) for ch in text) + gap * (len(text) - 1)
    x, y = xy
    x = x - w / 2 if anchor == "c" else x
    for ch in text:
        dr.text((x, y), ch, font=font, fill=fill)
        x += dr.textlength(ch, font=font) + gap
    return w


def og_image(d):
    """Bağlantı paylaşılınca görünen görsel (1200 × 630): mavi zeminde logo | GRIDA, ad soyad ve görev."""
    W, H = 1200, 630
    k = [[y / H] for y in range(H)]
    top, bot = (134, 184, 205), (86, 144, 170)
    col = Image.new("RGB", (1, H))
    col.putdata([tuple(int(a * (1 - t[0]) + b * t[0]) for a, b in zip(top, bot)) for t in k])
    im = col.resize((W, H))
    dr = ImageDraw.Draw(im)
    lg = L.raster(116)
    gfont = ImageFont.truetype(os.path.join(A.FONT_DIR, FONTS["sans"]), 38)
    gw = sum(dr.textlength(ch, font=gfont) for ch in "GRIDA") + 4 * 17
    x = (W - (lg.width + 36 + 3 + 36 + gw)) / 2
    im.paste(lg, (int(x), 112), lg)
    bx = x + lg.width + 36
    dr.rectangle((bx, 124, bx + 3, 216), fill=(255, 255, 255))
    spaced(dr, (bx + 39, 149), "GRIDA", gfont, 17, (255, 255, 255))
    name = ImageFont.truetype(os.path.join(A.FONT_DIR, FONTS["serif"]), 84)
    dr.text((W / 2, 372), d["isim"], font=name, fill=(255, 255, 255), anchor="mm")
    dr.rectangle((W / 2 - 30, 438, W / 2 + 30, 441), fill=(255, 255, 255))
    role = ImageFont.truetype(os.path.join(A.FONT_DIR, FONTS["sans-b"]), 30)
    spaced(dr, (W / 2, 466), d["gorev"].replace("i", "İ").replace("ı", "I").upper(), role, 8, (236, 245, 249), "c")
    im.save(os.path.join(OUT, OG), optimize=True)


# ---------------------------------------------------------------- parçalar

def logo_svg(cls, animated=False):
    """Logo harf harf (açılışta PALOMA iner, HOTELS ortadan açılır). --dx: harfin ortaya uzaklığının bir kısmı."""
    w, h = LOGO["svg_boyut"]
    out, ip, ih = [], 0, 0
    for hf in LOGO["harfler"]:
        if hf["satir"] == "paloma":
            st, ip, c = f' style="--i:{ip}"', ip + 1, "pl"
        else:
            st, ih, c = f' style="--i:{ih};--dx:{(w / 2 - hf["x"]) * 0.6:.0f}px"', ih + 1, "ht"
        out.append(f'<path class="{c}"{st if animated else ""} d="{hf["d"]}"/>')
    return (f'<svg class="{cls}" viewBox="0 0 {w:.0f} {h:.1f}" role="img" aria-label="Paloma Hotels" '
            f'fill="currentColor" fill-rule="evenodd">{"".join(out)}</svg>')


def wave_svg(cls, amp, y):
    pts = [f"{k},{y + amp * math.sin(k / 400 * 2 * math.pi * 2):.1f}" for k in range(0, 801, 20)]
    return (f'<svg class="{cls}" viewBox="0 0 800 110" preserveAspectRatio="none" aria-hidden="true">'
            f'<path d="M0,110 L{" L".join(pts)} L800,110 Z"/></svg>')


def qr_svg(content):
    """İsimlikteki QR (3. sürüm M): koyu kareler ayrı ayrı; --d çapraz dalganın gecikmesi (ms)."""
    import segno
    q = segno.make(content, error="m", micro=False, boost_error=True)
    m = [[bool(v) for v in row] for row in q.matrix]
    n, qz = len(m), 2
    rects = "".join(f'<rect class="m" x="{x + qz}" y="{y + qz}" width="1" height="1" style="--d:{(x + y) * 13}"/>'
                    for y, row in enumerate(m) for x, v in enumerate(row) if v)
    s = n + 2 * qz
    return (f'<svg viewBox="0 0 {s} {s}" shape-rendering="crispEdges" role="img" aria-label="Kartvizit QR kodu">'
            f'<rect width="{s}" height="{s}" fill="#fff"/>{rects}</svg>')


CSS = """
@font-face{font-family:Montserrat;src:url(fonts/sans.woff) format("woff");font-weight:600;font-display:swap}
@font-face{font-family:Montserrat;src:url(fonts/sans-b.woff) format("woff");font-weight:700;font-display:swap}
@font-face{font-family:Lora;src:url(fonts/serif.woff) format("woff");font-weight:700;font-display:swap}
:root{--pb:#69A1BA;--pb1:#86B8CD;--pb2:#5690AA;--bg:#F2F5F6;--surface:#fff;--ink:#16222B;--ink2:#3B4952;
  --muted:#6A7780;--line:#E2E8EB;--tint:#EAF3F7;--acc:#2F6F8C;--btn:#1C2329;--btnfg:#fff;--qr:#16222B;
  --shadow:rgba(23,53,67,.16);--e:cubic-bezier(.2,.75,.2,1);color-scheme:light}
@media (prefers-color-scheme:dark){:root{--bg:#141619;--surface:#1F2226;--ink:#F3F6F7;--ink2:#C8D1D6;--muted:#8E9AA2;
  --line:#2E3338;--tint:#273038;--acc:#8EC2D8;--btn:#69A1BA;--btnfg:#0E1A20;--shadow:rgba(0,0,0,.45);color-scheme:dark}}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:var(--bg)}
body{font-family:Montserrat,system-ui,sans-serif;font-weight:600;color:var(--ink);-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.wrap{max-width:440px;margin:0 auto;min-height:100vh;background:var(--bg);overflow:hidden;padding-bottom:84px}

/* mavi bant: logo | GRIDA (isimliklerdeki gibi) */
.band{position:relative;overflow:hidden;color:#fff;text-align:center;padding:62px 22px 172px;
  background:linear-gradient(165deg,var(--pb1) 0%,var(--pb) 45%,var(--pb2) 100%)}
.band:before{content:"";position:absolute;inset:-60% -30% auto;height:140%;
  background:radial-gradient(closest-side,#ffffff40,transparent);pointer-events:none}
.lock{position:relative;display:flex;align-items:center;justify-content:center;gap:16px;
  transform:translateY(calc(var(--sy,0)*.35px));opacity:calc(1 - var(--sy,0)/300)}
.lock .logo{width:166px;height:auto;display:block;overflow:visible}
.lock .bar{width:1.5px;height:44px;background:#fff;border-radius:1px}
.lock .grida{font-size:15px;font-weight:600;letter-spacing:.42em;margin-right:-.42em}
.where{position:relative;margin-top:18px;font-size:11px;letter-spacing:.36em;color:#ffffffd9;
  transform:translateY(calc(var(--sy,0)*.35px))}
.sea{position:absolute;left:0;right:0;bottom:-1px;height:110px}
.sea svg{position:absolute;bottom:0;width:200%;height:100%;left:0}
.sea .w1 path{fill:#B5D6E3}.sea .w2 path{fill:#4D86A0}.sea .w3 path{fill:var(--bg)}
.sea .w1{opacity:.4;animation:drift 14s linear infinite}
.sea .w2{opacity:.5;animation:drift 9s linear infinite reverse}
.sea .w3{animation:drift 18s linear infinite}

/* kart: isimlik gibi; solda ince mavi dikey çizgi */
.card{position:relative;margin:-104px 16px 0;background:var(--surface);border-radius:22px;padding:28px 22px 22px;
  box-shadow:0 18px 50px var(--shadow)}
.who{position:relative;padding-left:20px}
.who:before{content:"";position:absolute;left:0;top:4px;bottom:4px;width:2px;border-radius:1px;background:var(--pb);
  transform-origin:top}
h1{font-family:Lora;font-weight:700;font-size:40px;line-height:1.04;letter-spacing:-.005em}
h1 .ln{display:block;overflow:hidden;padding:.14em 0 .08em;margin:-.14em 0 -.08em}
h1 .ln>span{display:inline-block}
.role{margin-top:14px;color:var(--acc);font-size:12.5px;font-weight:700;letter-spacing:.22em;text-transform:uppercase}
.org{margin-top:6px;color:var(--ink2);font-size:15px}
.acts{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:24px;padding-top:20px;
  border-top:1px solid var(--line)}
.acts a{display:flex;flex-direction:column;align-items:center;gap:8px;font-size:12px;color:var(--ink)}
.acts a span{width:54px;height:54px;border-radius:16px;display:grid;place-items:center;background:var(--tint);
  color:var(--acc);transition:transform .15s}
.acts a:active span{transform:scale(.93)}
.acts a span svg{width:24px;height:24px}
.acts a.wa span{background:#E5F6EC;color:#1E9E5A}
@media (prefers-color-scheme:dark){.acts a.wa span{background:#1D3327;color:#4CD08A}}

/* iletişim satırları */
.list{margin:16px 16px 0;background:var(--surface);border-radius:20px;padding:4px 18px;box-shadow:0 8px 24px var(--shadow)}
.row{position:relative;display:flex;align-items:center;gap:14px;padding:15px 0}
.row:after{content:"";position:absolute;left:54px;right:0;bottom:0;height:1px;background:var(--line);transform-origin:left}
.row:last-child:after{display:none}
.row .i{width:40px;height:40px;border-radius:12px;background:var(--tint);color:var(--acc);display:grid;place-items:center;
  flex:none}
.row .i svg{width:20px;height:20px}
.row small{display:block;color:var(--muted);font-size:11.5px;letter-spacing:.05em}
.row b{display:block;font-weight:700;font-size:15.5px;font-variant-numeric:tabular-nums}
.row.em b{font-size:14px;letter-spacing:-.01em}
.row .go{margin-left:auto;color:var(--muted);opacity:.6;width:18px;height:18px;flex:none}

/* düğmeler */
.save{position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;gap:10px;
  margin:16px 16px 0;padding:17px;border-radius:18px;background:var(--btn);color:var(--btnfg);font-weight:700;
  font-size:16px;box-shadow:0 12px 26px var(--shadow)}
.save svg{width:22px;height:22px}
.save:after{content:"";position:absolute;top:0;bottom:0;left:-45%;width:40%;
  background:linear-gradient(100deg,transparent,rgba(255,255,255,.3),transparent)}
.share{display:flex;align-items:center;justify-content:center;gap:8px;margin:12px 16px 0;padding:14px;border-radius:16px;
  border:1.5px solid var(--line);color:var(--ink);font-weight:700;font-size:15px;background:var(--surface);
  width:calc(100% - 32px);font-family:inherit;cursor:pointer}
.share svg{width:19px;height:19px}
.share b{font-weight:700}

/* QR: mavi kart içinde beyaz karo, DİJİTAL | KARTVİZİT */
.qr{margin:30px 16px 0;text-align:center}
.qcard{position:relative;background:linear-gradient(160deg,var(--pb1),var(--pb) 55%,var(--pb2));border-radius:22px;
  padding:30px 20px 22px;color:#fff;box-shadow:0 14px 34px var(--shadow)}
.tile{position:relative;width:208px;margin:0 auto;padding:10px;background:#fff;border-radius:12px}
.tile svg{display:block;width:100%;height:auto}
.tile .m{fill:var(--qr);transform-box:fill-box;transform-origin:center}
.tile:after{content:"";position:absolute;left:0;right:0;top:0;height:22%;border-radius:12px;opacity:0;pointer-events:none;
  background:linear-gradient(transparent,rgba(105,161,186,.45),transparent)}
.vf{position:absolute;inset:-12px;pointer-events:none}
.vf i{position:absolute;width:24px;height:24px;border:2.5px solid #fff}
.vf i:nth-child(1){left:0;top:0;border-right:0;border-bottom:0;border-radius:10px 0 0 0}
.vf i:nth-child(2){right:0;top:0;border-left:0;border-bottom:0;border-radius:0 10px 0 0}
.vf i:nth-child(3){left:0;bottom:0;border-right:0;border-top:0;border-radius:0 0 0 10px}
.vf i:nth-child(4){right:0;bottom:0;border-left:0;border-top:0;border-radius:0 0 10px 0}
.qcap{display:flex;align-items:center;justify-content:center;gap:14px;margin-top:24px;font-size:12px;font-weight:700;
  letter-spacing:.3em}
.qcap span:last-child{margin-right:-.3em}
.qcap i{width:1.5px;height:16px;background:#fff}
.qtxt{margin-top:14px;color:var(--muted);font-size:13px;line-height:1.5}

footer{display:flex;flex-direction:column;align-items:center;gap:12px;padding:34px 0 8px;color:var(--muted);
  font-size:11.5px;letter-spacing:.14em}
footer .flock{display:flex;align-items:center;gap:10px;color:var(--pb)}
footer .flogo{width:92px;height:auto}
footer .flock i{width:1.5px;height:24px;background:var(--pb)}
footer .flock b{font-size:10.5px;letter-spacing:.4em;margin-right:-.4em}

/* altta Ara / WhatsApp şeridi (ara düğmeleri ekrandan çıkınca) */
.callbar{position:fixed;left:50%;bottom:0;width:min(440px,100%);transform:translate(-50%,110%);display:flex;gap:10px;
  padding:10px 14px calc(10px + env(safe-area-inset-bottom));background:var(--surface);border-top:1px solid var(--line);
  box-shadow:0 -8px 24px var(--shadow);transition:transform .35s var(--e);z-index:5}
.callbar.show{transform:translate(-50%,0)}
.callbar a{flex:1;display:flex;align-items:center;justify-content:center;gap:8px;padding:13px;border-radius:14px;
  font-weight:700;font-size:15px;background:var(--btn);color:var(--btnfg)}
.callbar a.wa{background:#1E9E5A;color:#fff}
.callbar svg{width:20px;height:20px}

/* ---------------- açılış */
.pl{transform-box:fill-box;transform-origin:50% 100%;animation:drop .65s var(--e) calc(.1s + var(--i)*.07s) both}
.ht{animation:spread 1s var(--e) calc(.4s + var(--i)*.02s) both}
.lock .bar{animation:grow-y .5s var(--e) .8s both}
.lock .grida{animation:wipe .8s var(--e) .9s both}
.where{animation:fade .6s ease-out 1.15s both}
.card{animation:lift .8s var(--e) .55s both}
.who:before{animation:grow-y .8s var(--e) .95s both}
h1 .ln>span{animation:rise .85s var(--e) .85s both}
h1 .ln+.ln>span{animation-delay:1s}
.role{animation:track 1s var(--e) 1.15s both}
.org{animation:fade .6s ease-out 1.35s both}
.acts{animation:line .7s var(--e) 1.2s both}
.acts a{animation:pop .55s var(--e) calc(1.3s + var(--i)*.08s) both}
.mo .acts [pathLength]{stroke-dasharray:1;stroke-dashoffset:1;animation:draw .8s ease-out calc(1.45s + var(--i)*.08s) forwards}
.acts .f{animation:fade .4s ease-out calc(1.9s + var(--i)*.08s) both}
.save:after{animation:shine 4.6s ease-in-out 2.6s infinite}

/* ---------------- kaydırınca (yalnız hareket açıksa gizli başlar; ilk ekrandakiler açılıştan sonra, --b) */
.mo .rv{opacity:0}
.mo .rv.in{animation:lift .7s var(--e) var(--b,0s) both}
.mo .list .row{opacity:0;transform:translateX(-14px)}
.mo .list .row:after{transform:scaleX(0)}
.mo .list.in .row{animation:slide .6s var(--e) calc(var(--b,0s) + var(--i)*.09s) forwards}
.mo .list.in .row:after{animation:grow-x .8s var(--e) calc(var(--b,0s) + .15s + var(--i)*.09s) forwards}
.mo .qr .m{opacity:0}
.mo .qr.in .m{animation:px .45s var(--e) calc(var(--b,0s) + var(--d)*1ms) forwards}
.mo .qr.in .tile:after{animation:sweep 1.5s ease-in-out calc(var(--b,0s) + .95s)}
.vf i{animation:breathe 2.8s ease-in-out infinite}
.vf i:nth-child(2),.vf i:nth-child(3){animation-delay:.2s}

@keyframes drop{from{opacity:0;transform:translateY(-38%)}to{opacity:1;transform:none}}
@keyframes spread{from{opacity:0;transform:translateX(var(--dx))}to{opacity:1;transform:none}}
@keyframes grow-y{from{transform:scaleY(0)}to{transform:none}}
@keyframes grow-x{from{transform:scaleX(0)}to{transform:none}}
@keyframes wipe{from{clip-path:inset(0 100% 0 0);transform:translateX(-8px)}to{clip-path:inset(0);transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes lift{from{opacity:0;transform:translateY(34px)}to{opacity:1;transform:none}}
@keyframes rise{from{transform:translateY(112%)}to{transform:none}}
@keyframes track{from{opacity:0;letter-spacing:.7em}to{opacity:1;letter-spacing:.22em}}
@keyframes line{from{border-top-color:transparent}to{border-top-color:var(--line)}}
@keyframes pop{from{opacity:0;transform:translateY(10px) scale(.9)}to{opacity:1;transform:none}}
@keyframes draw{to{stroke-dashoffset:0}}
@keyframes slide{to{opacity:1;transform:none}}
@keyframes px{from{opacity:0;transform:scale(.2)}to{opacity:1;transform:none}}
@keyframes sweep{0%{opacity:0;top:0}15%{opacity:1}85%{opacity:1}100%{opacity:0;top:78%}}
@keyframes breathe{0%,100%{transform:none;opacity:1}50%{transform:scale(1.12);opacity:.65}}
@keyframes shine{0%,78%{left:-45%}100%{left:125%}}
@keyframes drift{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@media (prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}
  .lock,.where{transform:none;opacity:1}}
"""

JS = """
(()=>{const R=document.documentElement,mo=R.classList.contains('mo');
if(mo){let q=0;addEventListener('scroll',()=>{if(!q)q=requestAnimationFrame(()=>{
  R.style.setProperty('--sy',Math.min(scrollY,300).toFixed(0));q=0})},{passive:true})}
const rv=[...document.querySelectorAll('.rv')];
if(mo&&'IntersectionObserver' in window){const io=new IntersectionObserver(es=>es.forEach(x=>{
  if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}}),{threshold:.2});
  rv.forEach(el=>{if(el.getBoundingClientRect().top<innerHeight*.9){el.style.setProperty('--b','1.55s');
    el.classList.add('in')}else io.observe(el)})}
else rv.forEach(el=>el.classList.add('in'));
const bar=document.querySelector('.callbar'),acts=document.querySelector('.acts');
if('IntersectionObserver' in window)new IntersectionObserver(([x])=>bar.classList.toggle('show',
  !x.isIntersecting&&x.boundingClientRect.top<0)).observe(acts);
if(document.hidden){const as=document.getAnimations();as.forEach(a=>a.pause());
  addEventListener('visibilitychange',()=>{if(!document.hidden)as.forEach(a=>a.play())},{once:true})}
document.getElementById('share').onclick=async ev=>{const u=location.href.split('#')[0],t=document.title,
  b=ev.currentTarget.querySelector('b');
  if(navigator.share){try{await navigator.share({title:t,url:u})}catch(x){}}
  else{try{await navigator.clipboard.writeText(u);b.textContent='Bağlantı kopyalandı';
    setTimeout(()=>b.textContent='Kartviziti paylaş',2200)}catch(x){}}}})();
"""


def page(d):
    first, last = d["isim"].split(" ", 1)
    wa = f"https://wa.me/{d['cep_e164']}?text=" + d["whatsapp_mesaj"].replace(" ", "%20").replace(",", "%2C")
    addr = ", ".join(d["adres"][:2]) + " / " + d["adres"][2]
    hotel = d["otel"].split()[-1].upper()
    ext = lambda h: " target=_blank rel=noopener" if h.startswith("http") else ""  # noqa: E731
    acts = [("phone", "Ara", f"tel:+{d['cep_e164']}", ""), ("whatsapp", "WhatsApp", wa, "wa"),
            ("mail", "E-posta", f"mailto:{d['eposta']}", ""), ("pin", "Konum", d["harita"], "")]
    a = "".join(f'<a class="{c}" style="--i:{k}" href="{e(h)}"{ext(h)}><span>{icon(ic, True)}</span>{e(t)}</a>'
                for k, (ic, t, h, c) in enumerate(acts))
    rows = [("phone", "Cep telefonu", d["cep_txt"], f"tel:+{d['cep_e164']}"),
            ("office", "Şirket hattı", d["sirket_txt"], f"tel:+{d['sirket_e164']}"),
            ("mail", "E-posta", d["eposta"], f"mailto:{d['eposta']}"),
            ("pin", "Adres", addr, d["harita"])]
    r = "".join(f'<a class="row{" em" if ic == "mail" else ""}" style="--i:{k}" href="{e(h)}"{ext(h)}>'
                f'<span class="i">{icon(ic)}</span><span><small>{e(lab)}</small><b>{e(v)}</b></span>'
                f'<svg class="go" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
                f'stroke-linecap="round" aria-hidden="true">{ICON["arrow"]}</svg></a>'
                for k, (ic, lab, v, h) in enumerate(rows))
    sea = wave_svg("w1", 10, 40) + wave_svg("w2", 8, 58) + wave_svg("w3", 7, 78)
    body = (
        f'<div class="wrap"><header class="band"><div class="lock">{logo_svg("logo", True)}<i class="bar"></i>'
        f'<span class="grida">{e(hotel)}</span></div><p class="where">BELEK · ANTALYA</p>'
        f'<div class="sea">{sea}</div></header>'
        f'<main><section class="card"><div class="who"><h1 aria-label="{e(d["isim"])}">'
        f'<span class="ln" aria-hidden="true"><span>{e(first)}</span></span>'
        f'<span class="ln" aria-hidden="true"><span>{e(last)}</span></span></h1>'
        f'<p class="role">{e(d["gorev"])}</p><p class="org">{e(d["otel"])}</p></div>'
        f'<nav class="acts" aria-label="Hızlı iletişim">{a}</nav></section>'
        f'<section class="list rv" aria-label="İletişim bilgileri">{r}</section>'
        f'<a class="save rv" href="{VCF}" download>{icon("save")}Rehbere kaydet</a>'
        f'<button class="share rv" id="share" type="button">{icon("share")}<b>Kartviziti paylaş</b></button>'
        f'<section class="qr rv" aria-label="Dijital kartvizit QR kodu"><div class="qcard"><div class="tile">'
        f'{qr_svg(d["qr"])}<span class="vf" aria-hidden="true"><i></i><i></i><i></i><i></i></span></div>'
        f'<p class="qcap"><span>DİJİTAL</span><i></i><span>KARTVİZİT</span></p></div>'
        f'<p class="qtxt">Masadaki isimlikte de aynı kod var.<br>Ekrandan okutarak kartviziti paylaşabilirsiniz.</p>'
        f'</section></main>'
        f'<footer><span class="flock">{logo_svg("flogo")}<i></i><b>{e(hotel)}</b></span>'
        f'<span>BELEK · ANTALYA</span></footer></div>'
        f'<nav class="callbar" aria-label="Hemen iletişim"><a href="tel:+{d["cep_e164"]}">{icon("phone")}Ara</a>'
        f'<a class="wa" href="{e(wa)}" target=_blank rel=noopener>{icon("whatsapp")}WhatsApp</a></nav>')
    title = f"{d['isim']} · {d['gorev']} · {d['otel']}"
    desc = f"{d['isim']} – {d['gorev']}, {d['otel']} ({d['grup']}). Ara, WhatsApp, e-posta, rehbere kaydet."
    og = d["sayfa_url"].rstrip("/") + "/" + OG
    return (f'<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" '
            f'content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#69A1BA">'
            f'<title>{e(title)}</title><meta name="description" content="{e(desc)}">'
            f'<meta property="og:type" content="profile"><meta property="og:title" content="{e(title)}">'
            f'<meta property="og:description" content="{e(desc)}"><meta property="og:image" content="{e(og)}">'
            f'<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
            f'<meta name="twitter:card" content="summary_large_image">'
            f"<script>matchMedia('(prefers-reduced-motion: reduce)').matches||"
            f"document.documentElement.classList.add('mo')</script>"
            f'<style>{CSS}</style></head><body>{body}<script>{JS}</script></body></html>')


# ---------------------------------------------------------------- önizlemeler

def screenshot(path=PREVIEW):
    """Telefon ekranında (390 px): açık tema üst görünüm, açık tema tüm sayfa, koyu tema üst görünüm."""
    from playwright.sync_api import sync_playwright
    shots = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        for scheme, full in (("light", False), ("light", True), ("dark", False)):
            pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, reduced_motion="reduce",
                            color_scheme=scheme)
            pg.goto("file://" + os.path.join(OUT, "index.html"))
            pg.wait_for_timeout(400)
            assert pg.evaluate("document.fonts.check('700 20px \"Lora\"') && "
                               "document.fonts.check('600 20px \"Montserrat\"')"), "yazı tipi yüklenmedi"
            assert pg.evaluate("document.documentElement.scrollWidth") <= 390, "yatay taşma"
            assert pg.evaluate("[...document.querySelectorAll('.row b,.row small,.role,.org,h1 .ln')]"
                               ".every(e=>e.scrollWidth<=e.clientWidth+1)"), "yazı sığmadı"
            if full:
                pg.add_style_tag(content=".callbar{display:none}")
            shots.append(Image.open(io.BytesIO(pg.screenshot(full_page=full))))
            pg.close()
        b.close()
    h = max(s.height for s in shots)
    canvas = Image.new("RGB", (sum(s.width for s in shots) + 160, h + 120), (52, 56, 64))
    x = 40
    for s in shots:
        canvas.paste(s, (x, 60))
        x += s.width + 40
    canvas.save(path)
    return path


def tour_gif(path=TOUR):
    """Tur (390 × 844): açılış zamanda adım adım, sonra aşağı kaydırma (satırlar, QR, alt şerit)."""
    from playwright.sync_api import sync_playwright
    frames, durs = [], []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)

        def shot(ms):
            frames.append(Image.open(io.BytesIO(pg.screenshot())).convert("RGB"))
            durs.append(ms)

        pg.goto("file://" + os.path.join(OUT, "index.html"))
        _seek(pg, 0)
        pg.wait_for_timeout(300)
        for k in range(0, 2400, 60):
            _seek(pg, k)
            shot(60)
        _finish(pg)
        shot(1000)
        h = pg.evaluate("document.documentElement.scrollHeight - innerHeight")
        for y in range(0, h + 1, 30):
            pg.evaluate(f"scrollTo(0,{y})")
            pg.wait_for_timeout(45)
            shot(55)
        pg.evaluate(f"scrollTo(0,{h})")
        for _ in range(16):
            pg.wait_for_timeout(100)
            shot(100)
        durs[-1] = 2200
        b.close()
    return _gif(frames, durs, path)


def pack():
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for d, _, files in os.walk(OUT):
            for fn in sorted(files):
                full = os.path.join(d, fn)
                z.write(full, os.path.relpath(full, OUT))


def main():
    d = load()
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    doc = page(d)
    subset_fonts(html.unescape(doc))
    vcard(d)
    og_image(d)
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(doc)
    pack()
    print("sayfa:", os.path.relpath(os.path.join(OUT, "index.html"), A.ROOT), f"({len(doc) // 1024} KB) →",
          d["sayfa_url"])
    print("önizleme:", os.path.relpath(screenshot(), A.ROOT))
    if "--hizli" not in sys.argv:
        print("tur:", os.path.relpath(tour_gif(), A.ROOT))


if __name__ == "__main__":
    main()
