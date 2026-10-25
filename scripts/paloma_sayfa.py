"""PALOMA GRIDA – Süleyman Boylu'nun dijital kartviziti (isimlikteki QR bu sayfayı açar). 3. sürüm.

Yazı sistemi Paloma Hotels logosundan: logonun harfleri Google yazı tipleriyle harf harf karşılaştırıldı, en yakını
Figtree çıktı (PALOMA satırı ExtraBold, HOTELS satırı Light). Sayfada da öyle: kalın ve aralıklı büyük harf başlıklar
(SÜLEYMAN), ince ve aynı genişliğe yayılmış ikinci satırlar (B O Y L U), küçük aralıklı etiketler; tırnaklı yazı yok.

Tasarım: otel sitesi gibi tam ekran açılış (ufukta Akdeniz), altında yüzen hızlı iletişim çubuğu, numaralı bölümler
(01 İletişim, 02 Otel: yukarıdan sığ deniz, 03 Kartvizit: QR), sonda logo. Görseller Blender'da çizildi
(scripts/paloma_gorsel.py). Açık temada kum beyazı, telefon koyu moddaysa gece renkleri.

Animasyon:
  * Açılış (~2,6 sn): görsel yavaşça yaklaşır (Ken Burns), PALOMA harfleri iner, HOTELS harfleri ortadan açılır,
    ayraç ve GRIDA; SÜLEYMAN harfleri maskeden çıkar, BOYLU harfleri ortadan yerlerine yayılır, ince çizgi uzar,
    görevin harf aralığı açılır; iletişim çubuğu aşağıdan gelir, simgeler çizilir; KAYDIR işareti akar.
  * Kaydırma: açılış görseli yavaş kayar (parallax); bölüm başlıklarında numara ve çizgi, başlık soldan açılır;
    satırlar ve alt çizgiler sırayla; otel görseli alttan perde gibi açılır ve kaydırdıkça içinde kayar; QR kareleri
    çapraz dalgayla belirir; iletişim çubuğu ekrandan çıkınca altta Ara / WhatsApp şeridi.
  * Sürekli: QR'ın vizör köşeleri nefes alır, Rehbere kaydet'in üstünden ara ara ışık geçer.
  "Hareketi azalt" açıksa hiçbiri oynamaz, sayfa doğrudan son hâliyle açılır.

Dış bağlantı yok: yazı tipi (Figtree, OFL), görseller, logo ve simgeler sayfanın yanında ya da içinde.
Bilgiler `paloma_isimlik/bilgiler.json`; logo paloma_isimlik/logo/ (scripts/paloma_logo.py).

Yayın: ortak Cloudflare hesabında (`qrsistem`) `suleymanboylu` adlı Worker'a `paloma_site.zip` yüklenir; adres
`https://suleymanboylu.qrsistem.workers.dev` (isimliklerdeki QR bu adresi açar).

Çıktı : paloma_isimlik/site/, paloma_site.zip, sayfa_onizleme.png (açık, tam sayfa, koyu), sayfa_tur.gif

Kullanım:
  python3 scripts/paloma_gorsel.py           # önce görseller (bir kez)
  python3 scripts/paloma_sayfa.py            # site, zip, önizleme ve tur
  python3 scripts/paloma_sayfa.py --hizli    # GIF'siz
"""
import html
import io
import json
import os
import shutil
import sys
import zipfile

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import paloma_logo as L  # noqa: E402
import qr_sistemi as Q  # noqa: E402
from ince_sayfa import _finish, _gif, _seek  # noqa: E402

BASE = os.path.join(A.ROOT, "paloma_isimlik")
OUT = os.path.join(BASE, "site")
IMG = os.path.join(BASE, "gorsel")
ZIP = os.path.join(BASE, "paloma_site.zip")
PREVIEW = os.path.join(BASE, "sayfa_onizleme.png")
TOUR = os.path.join(BASE, "sayfa_tur.gif")
CHROMIUM = "/opt/pw-browsers/chromium"
FONTS = {"f3": "Figtree_300Light.ttf", "f4": "Figtree_400Regular.ttf", "f6": "Figtree_600SemiBold.ttf",
         "f8": "Figtree_800ExtraBold.ttf"}
LICENSES = ("OFL-figtree.txt",)
VCF = "suleyman-boylu.vcf"
OG = "paylas.jpg"
LOGO = json.load(open(L.JSON, encoding="utf-8"))

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
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
}


def icon(k, draw=False, width=1.4):
    """draw: çizgiler açılışta çizilsin diye her çizgi parçasına pathLength=1 (dolgulu parça, class="f", hariç)."""
    body = ICON[k]
    if draw:
        for tag in ("<path ", "<rect ", "<circle "):
            body = body.replace(tag + "d=", tag + 'pathLength="1" d=').replace(tag + "x=", tag + 'pathLength="1" x=')
            body = body.replace(tag + "cx=", tag + 'pathLength="1" cx=')
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{width}" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{body}</svg>')


def e(s):
    return html.escape(str(s))


def tr_upper(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


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
    os.makedirs(fdir, exist_ok=True)
    chars = text + "ABCÇDEFGĞHIİJKLMNOÖPQRSŞTUÜVWXYZabcçdefgğhıijklmnoöpqrsştuüvwxyz0123456789 .,:;·+-–—/@&()'\"!?→"
    for key, fn in FONTS.items():
        opts = subset.Options()
        opts.flavor = "woff2" if _has_brotli() else "woff"
        opts.layout_features = ["kern", "liga", "locl", "tnum", "lnum"]
        f = subset.load_font(os.path.join(A.FONT_DIR, fn), opts)
        s = subset.Subsetter(opts)
        s.populate(text=chars)
        s.subset(f)
        subset.save_font(f, os.path.join(fdir, f"{key}.{opts.flavor}"), opts)
    for lic in LICENSES:
        shutil.copy(os.path.join(A.FONT_DIR, lic), os.path.join(fdir, lic))


def _has_brotli():
    """woff2 için fontTools brotli ister; yoksa woff."""
    import importlib.util
    return importlib.util.find_spec("brotli") is not None


def images():
    """Blender görselleri sayfa için: hafif renk ayarı, JPEG (ufuk 1080 × 1920, sığ 1080 × 1350)."""
    os.makedirs(os.path.join(OUT, "img"), exist_ok=True)
    for name in ("ufuk", "sig"):
        im = Image.open(os.path.join(IMG, name + ".jpg")).convert("RGB")
        im = ImageEnhance.Color(im).enhance(1.12)
        im = ImageEnhance.Contrast(im).enhance(1.05)
        im.save(os.path.join(OUT, "img", name + ".jpg"), "JPEG", quality=80, optimize=True, progressive=True)


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


def spaced(dr, x, y, text, font, gap, fill, anchor="l"):
    """Harf aralıklı yazı; anchor "c": ortası x'te. Döner: genişlik."""
    w = sum(dr.textlength(ch, font=font) for ch in text) + gap * (len(text) - 1)
    x = x - w / 2 if anchor == "c" else x
    for ch in text:
        dr.text((x, y), ch, font=font, fill=fill)
        x += dr.textlength(ch, font=font) + gap
    return w


def og_image(d):
    """Bağlantı paylaşılınca görünen görsel (1200 × 630): ufuk görselinden kesit, logo | GRIDA, ad ve görev."""
    W, H = 1200, 630
    src = Image.open(os.path.join(IMG, "ufuk.jpg")).convert("RGB")
    k = W / src.width
    src = src.resize((W, int(src.height * k)), Image.LANCZOS)
    top = int(src.height * 0.38)
    im = src.crop((0, top, W, top + H))
    shade = Image.new("RGBA", (W, H), (12, 34, 44, 0))
    sd = ImageDraw.Draw(shade)
    for y in range(H):
        sd.line([(0, y), (W, y)], fill=(12, 34, 44, int(70 + 110 * y / H)))
    im = Image.alpha_composite(im.convert("RGBA"), shade)
    dr = ImageDraw.Draw(im)
    lg = L.raster(96)
    f = lambda key, size: ImageFont.truetype(os.path.join(A.FONT_DIR, FONTS[key]), size)  # noqa: E731
    gfont = f("f6", 30)
    gw = sum(dr.textlength(ch, font=gfont) for ch in "GRIDA") + 4 * 14
    x = (W - (lg.width + 30 + 2 + 30 + gw)) / 2
    im.paste(lg, (int(x), 92), lg)
    bx = x + lg.width + 30
    dr.rectangle((bx, 100, bx + 2, 180), fill=(255, 255, 255))
    spaced(dr, bx + 32, 122, "GRIDA", gfont, 14, (255, 255, 255))
    first, last = tr_upper(d["isim"]).split(" ", 1)
    bf = f("f8", 64)
    wb = spaced(dr, W / 2, 300, first, bf, 26, (255, 255, 255), "c")
    lf = f("f3", 64)
    xs = W / 2 - wb / 2
    widths = [dr.textlength(ch, font=lf) for ch in last]
    gap = (wb - sum(widths)) / (len(last) - 1)
    for ch, cw in zip(last, widths):
        dr.text((xs, 384), ch, font=lf, fill=(255, 255, 255))
        xs += cw + gap
    dr.rectangle((W / 2 - 28, 486, W / 2 + 28, 488), fill=(255, 255, 255))
    spaced(dr, W / 2, 510, tr_upper(d["gorev"]), f("f6", 24), 9, (230, 241, 246), "c")
    im.convert("RGB").save(os.path.join(OUT, OG), "JPEG", quality=86, optimize=True)


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


def lockup(cls, hotel, animated=False):
    return (f'<div class="{cls}">{logo_svg("logo", animated)}<i class="bar"></i>'
            f'<span class="grida">{e(hotel)}</span></div>')


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


def letters(text, cls=""):
    return "".join(f'<span class="{cls}" style="--i:{k}">{e(ch)}</span>' for k, ch in enumerate(text))


def head(no, title):
    return (f'<div class="sh rv"><span class="no">{no}</span><i></i><h2>{e(title)}</h2></div>')


CSS = """
@font-face{font-family:Figtree;src:url(fonts/f3.EXT) format("FMT");font-weight:300;font-display:swap}
@font-face{font-family:Figtree;src:url(fonts/f4.EXT) format("FMT");font-weight:400;font-display:swap}
@font-face{font-family:Figtree;src:url(fonts/f6.EXT) format("FMT");font-weight:600;font-display:swap}
@font-face{font-family:Figtree;src:url(fonts/f8.EXT) format("FMT");font-weight:800;font-display:swap}
:root{--pb:#69A1BA;--pbd:#2F6F8C;--deep:#16303C;--bg:#F5F2EC;--surface:#FFFFFF;--ink:#14212A;--ink2:#41505A;
  --muted:#7B8790;--line:#E2DDD3;--tint:#EAF2F5;--btn:#16303C;--btnfg:#fff;--qr:#14212A;--shadow:rgba(22,48,60,.14);
  --e:cubic-bezier(.2,.75,.2,1);--tr:.34em;color-scheme:light}
@media (prefers-color-scheme:dark){:root{--bg:#0F1519;--surface:#162027;--ink:#EEF2F4;--ink2:#C3CDD3;--muted:#8796A0;
  --line:#26333B;--tint:#1E2C35;--pbd:#8EC2D8;--btn:#69A1BA;--btnfg:#0B1A21;--shadow:rgba(0,0,0,.45);color-scheme:dark}}
*{box-sizing:border-box;margin:0;padding:0}
html{background:#0E1A20}
body{font-family:Figtree,system-ui,sans-serif;font-weight:400;color:var(--ink);-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.wrap{position:relative;max-width:440px;margin:0 auto;min-height:100vh;background:var(--bg);overflow:hidden;
  padding-bottom:90px;box-shadow:0 0 80px rgba(0,0,0,.35)}
.caps{text-transform:uppercase;letter-spacing:var(--tr)}

/* ---------------- açılış: tam ekran görsel */
.hero{position:relative;height:100svh;min-height:620px;max-height:980px;color:#fff;overflow:hidden}
.hero .bg{position:absolute;inset:-6% 0;width:100%;height:112%;object-fit:cover;object-position:50% 46%;
  transform:translateY(calc(var(--sy,0)*.32px));will-change:transform}
.hero .bg img{width:100%;height:100%;object-fit:cover;display:block}
.hero:after{content:"";position:absolute;inset:0;pointer-events:none;
  background:linear-gradient(180deg,rgba(14,40,52,.3) 0%,rgba(14,40,52,0) 20%,rgba(14,40,52,0) 54%,
  rgba(10,44,58,.3) 70%,rgba(8,34,46,.64) 100%)}
.lock{position:relative;z-index:1;display:flex;align-items:center;gap:13px}
.lock .logo{width:118px;height:auto;display:block;overflow:visible}
.lock .bar{width:1.2px;height:31px;background:currentColor;opacity:.9}
.lock .grida{font-weight:600;font-size:11px;letter-spacing:.42em;margin-right:-.42em}
.hero .lock{position:absolute;top:30px;left:28px}
.who{position:absolute;z-index:1;left:28px;right:28px;bottom:148px}
.kick{font-weight:600;font-size:10.5px;letter-spacing:.42em;opacity:.85}
h1{display:inline-grid;margin-top:16px;font-size:clamp(28px,8.6vw,36px);line-height:1;text-transform:uppercase}
h1 .b{display:block;font-weight:800;letter-spacing:.3em;overflow:hidden;padding:.12em 0 .04em;margin-top:-.12em}
h1 .b span{display:inline-block}
h1 .b span:last-child{letter-spacing:0}
h1 .l{display:flex;justify-content:space-between;font-weight:300;margin-top:.2em}
h1 .l span{display:inline-block}
.who .rule{display:block;width:44px;height:1.5px;background:#fff;margin:22px 0 14px;transform-origin:left}
.role{font-weight:600;font-size:12px;letter-spacing:.3em}
.cue{position:absolute;z-index:1;right:26px;bottom:150px;display:flex;flex-direction:column;align-items:center;gap:10px;
  font-weight:600;font-size:9.5px;letter-spacing:.34em;writing-mode:vertical-rl}
.cue i{position:relative;width:1px;height:46px;background:rgba(255,255,255,.35);overflow:hidden}
.cue i:after{content:"";position:absolute;left:0;top:-40%;width:1px;height:40%;background:#fff}

/* ---------------- yüzen iletişim çubuğu */
.dock{position:relative;z-index:2;margin:-104px 16px 0;display:grid;grid-template-columns:repeat(4,1fr);
  background:var(--surface);border-radius:18px;box-shadow:0 20px 50px var(--shadow);padding:18px 6px 16px}
.dock a{display:flex;flex-direction:column;align-items:center;gap:10px;font-weight:600;font-size:9.5px;
  letter-spacing:.2em;color:var(--ink);position:relative}
.dock a+a:before{content:"";position:absolute;left:0;top:6px;bottom:6px;width:1px;background:var(--line)}
.dock a span{width:44px;height:44px;border-radius:50%;display:grid;place-items:center;
  border:1px solid var(--line);color:var(--pbd);transition:transform .15s,background .15s}
.dock a:active span{transform:scale(.92);background:var(--tint)}
.dock a span svg{width:21px;height:21px}
.dock a.wa span{color:#1E9E5A}

/* ---------------- bölümler */
.sec{padding:54px 26px 0}
.sh{display:flex;align-items:center;gap:14px;margin-bottom:26px}
.sh .no{font-weight:300;font-size:13px;letter-spacing:.12em;color:var(--pbd)}
.sh i{width:34px;height:1px;background:var(--pb);transform-origin:left}
.sh h2{font-weight:800;font-size:13px;letter-spacing:var(--tr);text-transform:uppercase}
.rows a{position:relative;display:flex;align-items:center;gap:14px;padding:18px 0}
.rows a:after{content:"";position:absolute;left:0;right:0;bottom:0;height:1px;background:var(--line);transform-origin:left}
.rows small{display:block;font-weight:600;font-size:9.5px;letter-spacing:.3em;color:var(--muted);text-transform:uppercase}
.rows b{display:block;margin-top:6px;font-weight:300;font-size:25px;letter-spacing:.02em;font-variant-numeric:lining-nums}
.rows a.em b{font-size:18.5px;letter-spacing:0}
.rows a.ad b{font-size:19px;line-height:1.25}
.rows .go{margin-left:auto;width:20px;height:20px;color:var(--pb);flex:none;transition:transform .2s}
.rows a:active .go{transform:translateX(4px)}

.pic{position:relative;margin:0 -26px;height:420px;overflow:hidden;color:#fff}
.pic img{position:absolute;inset:-12% 0;width:100%;height:124%;object-fit:cover;
  transform:translateY(calc(var(--p,0)*-34px))}
.pic:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,30,40,0) 40%,rgba(10,30,40,.55))}
.pic .cap{position:absolute;z-index:1;left:26px;right:26px;bottom:26px}
.pic .cap .t{display:inline-grid;font-size:24px;line-height:1;text-transform:uppercase}
.pic .cap .t b{font-weight:800;letter-spacing:.3em;margin-right:-.3em}
.pic .cap .t span{display:flex;justify-content:space-between;font-weight:300;margin-top:.22em}
.pic .cap p{margin-top:12px;font-weight:600;font-size:10px;letter-spacing:.34em}
.addr{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;padding:26px 0 4px}
.addr p{font-weight:300;font-size:19px;line-height:1.4}
.link{display:inline-flex;align-items:center;gap:10px;flex:none;font-weight:600;font-size:10px;letter-spacing:.28em;
  color:var(--pbd);padding-bottom:6px;border-bottom:1px solid var(--pb)}
.link svg{width:16px;height:16px}

.qcard{position:relative;display:flex;flex-direction:column;align-items:center;padding:34px 20px 24px;border-radius:20px;
  background:linear-gradient(160deg,#86B8CD,#69A1BA 55%,#5690AA);color:#fff;box-shadow:0 16px 36px var(--shadow)}
.tile{position:relative;width:196px;padding:10px;background:#fff;border-radius:10px}
.tile svg{display:block;width:100%;height:auto}
.tile .m{fill:var(--qr);transform-box:fill-box;transform-origin:center}
.tile:after{content:"";position:absolute;left:0;right:0;top:0;height:22%;border-radius:10px;opacity:0;pointer-events:none;
  background:linear-gradient(transparent,rgba(105,161,186,.45),transparent)}
.vf{position:absolute;inset:-12px;pointer-events:none}
.vf i{position:absolute;width:22px;height:22px;border:2px solid #fff}
.vf i:nth-child(1){left:0;top:0;border-right:0;border-bottom:0}
.vf i:nth-child(2){right:0;top:0;border-left:0;border-bottom:0}
.vf i:nth-child(3){left:0;bottom:0;border-right:0;border-top:0}
.vf i:nth-child(4){right:0;bottom:0;border-left:0;border-top:0}
.qcap{display:flex;align-items:center;gap:14px;margin-top:26px;font-weight:600;font-size:11px;letter-spacing:.34em}
.qcap span:last-child{margin-right:-.34em}
.qcap i{width:1.2px;height:15px;background:#fff}
.qtxt{margin-top:16px;color:var(--muted);font-size:13.5px;line-height:1.55;text-align:center}
.btns{display:grid;gap:12px;margin-top:26px}
.save{position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;gap:12px;padding:19px;
  border-radius:14px;background:var(--btn);color:var(--btnfg);font-weight:600;font-size:11.5px;letter-spacing:.28em}
.save svg{width:20px;height:20px}
.save:after{content:"";position:absolute;top:0;bottom:0;left:-45%;width:40%;
  background:linear-gradient(100deg,transparent,rgba(255,255,255,.28),transparent)}
.share{display:flex;align-items:center;justify-content:center;gap:12px;padding:17px;border-radius:14px;
  border:1px solid var(--line);background:transparent;color:var(--ink);font-family:inherit;font-weight:600;font-size:11.5px;
  letter-spacing:.28em;cursor:pointer}
.share svg{width:18px;height:18px}
.share b{font-weight:600}

footer{display:flex;flex-direction:column;align-items:center;gap:16px;margin-top:62px;padding:40px 0 10px;
  border-top:1px solid var(--line);color:var(--pbd)}
footer .lock .logo{width:104px}
footer p{font-weight:600;font-size:9.5px;letter-spacing:.38em;color:var(--muted)}

.callbar{position:fixed;left:50%;bottom:0;width:min(440px,100%);transform:translate(-50%,110%);display:flex;gap:10px;
  padding:10px 14px calc(10px + env(safe-area-inset-bottom));background:var(--surface);border-top:1px solid var(--line);
  box-shadow:0 -8px 24px var(--shadow);transition:transform .35s var(--e);z-index:5}
.callbar.show{transform:translate(-50%,0)}
.callbar a{flex:1;display:flex;align-items:center;justify-content:center;gap:9px;padding:14px;border-radius:12px;
  font-weight:600;font-size:11px;letter-spacing:.24em;background:var(--btn);color:var(--btnfg)}
.callbar a.wa{background:#1E9E5A;color:#fff}
.callbar svg{width:19px;height:19px}

/* ---------------- açılış animasyonu */
.hero .bg img{animation:kb 3.2s cubic-bezier(.15,.7,.25,1) both}
.hero:after{animation:fade 1.2s ease-out both}
.pl{transform-box:fill-box;transform-origin:50% 100%;animation:drop .65s var(--e) calc(.35s + var(--i)*.07s) both}
.ht{animation:spread 1s var(--e) calc(.6s + var(--i)*.02s) both}
.hero .lock .bar{animation:grow-y .5s var(--e) 1s both}
.hero .lock .grida{animation:wipe .8s var(--e) 1.1s both}
.kick{animation:fade-up .7s var(--e) .9s both}
h1 .b span{animation:rise .8s var(--e) calc(1s + var(--i)*.045s) both}
h1 .l span{animation:spread2 1.1s var(--e) calc(1.35s + var(--i)*.03s) both}
.who .rule{animation:grow-x .8s var(--e) 1.7s both}
.role{animation:track 1.1s var(--e) 1.8s both}
.cue{animation:fade .8s ease-out 2.4s both}
.cue i:after{animation:flow 2.2s ease-in-out 2.6s infinite}
.dock{animation:lift .9s var(--e) 1.9s both}
.mo .dock [pathLength]{stroke-dasharray:1;stroke-dashoffset:1;animation:draw .8s ease-out calc(2.2s + var(--i)*.08s) forwards}
.dock .f{animation:fade .4s ease-out calc(2.7s + var(--i)*.08s) both}
.save:after{animation:shine 4.8s ease-in-out 3s infinite}
.vf i{animation:breathe 2.8s ease-in-out infinite}
.vf i:nth-child(2),.vf i:nth-child(3){animation-delay:.2s}

/* ---------------- kaydırınca (yalnız hareket açıksa gizli başlar; ilk ekrandakiler açılıştan sonra, --b) */
.mo .rv{opacity:0}
.mo .rv.in{opacity:1}
.mo .sh.in .no{animation:fade .6s ease-out var(--b,0s) both}
.mo .sh.in i{animation:grow-x .7s var(--e) calc(var(--b,0s) + .1s) both}
.mo .sh.in h2{animation:wipe .8s var(--e) calc(var(--b,0s) + .25s) both}
.mo .rows.in a{animation:slide .65s var(--e) calc(var(--b,0s) + var(--i)*.09s) both}
.mo .rows.in a:after{animation:grow-x .9s var(--e) calc(var(--b,0s) + .15s + var(--i)*.09s) both}
.mo .pic.in{animation:curtain 1.1s cubic-bezier(.6,0,.2,1) var(--b,0s) both}
.mo .pic.in img{animation:kb2 1.6s var(--e) var(--b,0s) both}
.mo .pic.in .cap{animation:fade-up .8s var(--e) calc(var(--b,0s) + .7s) both}
.mo .addr.in,.mo .btns.in,.mo footer.in,.mo .qtxt.in{animation:fade-up .8s var(--e) var(--b,0s) both}
.mo .qcard.in{animation:lift .8s var(--e) var(--b,0s) both}
.mo .qcard .m{opacity:0}
.mo .qcard.in .m{animation:px .45s var(--e) calc(var(--b,0s) + .3s + var(--d)*1ms) both}
.mo .qcard.in .tile:after{animation:sweep 1.5s ease-in-out calc(var(--b,0s) + 1.25s)}

@keyframes kb{from{transform:scale(1.16)}to{transform:none}}
@keyframes kb2{from{transform:scale(1.18)}to{transform:none}}
@keyframes drop{from{opacity:0;transform:translateY(-38%)}to{opacity:1;transform:none}}
@keyframes spread{from{opacity:0;transform:translateX(var(--dx))}to{opacity:1;transform:none}}
@keyframes spread2{from{opacity:0;transform:translateX(calc((2 - var(--i))*.95em))}to{opacity:1;transform:none}}
@keyframes rise{from{transform:translateY(115%)}to{transform:none}}
@keyframes grow-y{from{transform:scaleY(0)}to{transform:none}}
@keyframes grow-x{from{transform:scaleX(0)}to{transform:none}}
@keyframes wipe{from{clip-path:inset(0 100% 0 0);transform:translateX(-8px)}to{clip-path:inset(0);transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes fade-up{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes lift{from{opacity:0;transform:translateY(40px)}to{opacity:1;transform:none}}
@keyframes track{from{opacity:0;letter-spacing:.9em}to{opacity:1;letter-spacing:.3em}}
@keyframes flow{0%{top:-40%}100%{top:100%}}
@keyframes draw{to{stroke-dashoffset:0}}
@keyframes slide{from{opacity:0;transform:translateX(-18px)}to{opacity:1;transform:none}}
@keyframes curtain{from{clip-path:inset(100% 0 0 0)}to{clip-path:inset(0)}}
@keyframes px{from{opacity:0;transform:scale(.2)}to{opacity:1;transform:none}}
@keyframes sweep{0%{opacity:0;top:0}15%{opacity:1}85%{opacity:1}100%{opacity:0;top:78%}}
@keyframes breathe{0%,100%{transform:none;opacity:1}50%{transform:scale(1.12);opacity:.6}}
@keyframes shine{0%,78%{left:-45%}100%{left:125%}}
@media (prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}
  .hero .bg,.pic img{transform:none}}
"""

JS = """
(()=>{const R=document.documentElement,mo=R.classList.contains('mo');
const px=[...document.querySelectorAll('.pic')];
if(mo){let q=0;const f=()=>{R.style.setProperty('--sy',Math.min(scrollY,900).toFixed(0));
  px.forEach(el=>{const r=el.getBoundingClientRect();
    el.style.setProperty('--p',Math.max(-1,Math.min(1,(r.top+r.height/2-innerHeight/2)/innerHeight)).toFixed(3))});q=0};
  addEventListener('scroll',()=>{if(!q)q=requestAnimationFrame(f)},{passive:true});f()}
const rv=[...document.querySelectorAll('.rv')];
if(mo&&'IntersectionObserver' in window){const io=new IntersectionObserver(es=>es.forEach(x=>{
  if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}}),{threshold:.18,rootMargin:'0px 0px -6% 0px'});
  rv.forEach(el=>{if(el.getBoundingClientRect().top<innerHeight){el.style.setProperty('--b','2.3s');
    el.classList.add('in')}else io.observe(el)})}
else rv.forEach(el=>el.classList.add('in'));
const bar=document.querySelector('.callbar'),dock=document.querySelector('.dock');
if('IntersectionObserver' in window)new IntersectionObserver(([x])=>bar.classList.toggle('show',
  !x.isIntersecting&&x.boundingClientRect.top<0)).observe(dock);
if(document.hidden){const as=document.getAnimations();as.forEach(a=>a.pause());
  addEventListener('visibilitychange',()=>{if(!document.hidden)as.forEach(a=>a.play())},{once:true})}
document.getElementById('share').onclick=async ev=>{const u=location.href.split('#')[0],t=document.title,
  b=ev.currentTarget.querySelector('b');
  if(navigator.share){try{await navigator.share({title:t,url:u})}catch(x){}}
  else{try{await navigator.clipboard.writeText(u);b.textContent='BAĞLANTI KOPYALANDI';
    setTimeout(()=>b.textContent='KARTVİZİTİ PAYLAŞ',2200)}catch(x){}}}})();
"""


def page(d):
    first, last = tr_upper(d["isim"]).split(" ", 1)
    wa = f"https://wa.me/{d['cep_e164']}?text=" + d["whatsapp_mesaj"].replace(" ", "%20").replace(",", "%2C")
    hotel = d["otel"].split()[-1].upper()
    ext = lambda h: " target=_blank rel=noopener" if h.startswith("http") else ""  # noqa: E731
    dock = [("phone", "ARA", f"tel:+{d['cep_e164']}", ""), ("whatsapp", "WHATSAPP", wa, "wa"),
            ("mail", "E-POSTA", f"mailto:{d['eposta']}", ""), ("pin", "KONUM", d["harita"], "")]
    dk = "".join(f'<a class="{c}" style="--i:{k}" href="{e(h)}"{ext(h)}><span>{icon(ic, True)}</span>{e(t)}</a>'
                 for k, (ic, t, h, c) in enumerate(dock))
    rows = [("Cep telefonu", d["cep_txt"], f"tel:+{d['cep_e164']}", ""),
            ("Şirket hattı", d["sirket_txt"], f"tel:+{d['sirket_e164']}", ""),
            ("E-posta", d["eposta"], f"mailto:{d['eposta']}", "em")]
    r = "".join(f'<a class="{c}" style="--i:{k}" href="{e(h)}"><span><small>{e(lab)}</small><b>{e(v)}</b></span>'
                f'{icon("arrow", width=1.3).replace("<svg ", "<svg class=go ", 1)}</a>'
                for k, (lab, v, h, c) in enumerate(rows))
    street, district, city, _ = d["adres"]
    body = (
        f'<div class="wrap"><header class="hero"><picture class="bg"><img src="img/ufuk.jpg" alt="" '
        f'fetchpriority="high"></picture>{lockup("lock", hotel, True)}'
        f'<div class="who"><p class="kick">BELEK · ANTALYA</p>'
        f'<h1 aria-label="{e(d["isim"])}"><span class="b" aria-hidden="true">{letters(first)}</span>'
        f'<span class="l" aria-hidden="true">{letters(last)}</span></h1>'
        f'<i class="rule"></i><p class="role">{e(tr_upper(d["gorev"]))}</p></div>'
        f'<a class="cue" href="#iletisim" aria-label="Aşağı kaydır">KAYDIR<i></i></a></header>'
        f'<nav class="dock" aria-label="Hızlı iletişim">{dk}</nav>'
        f'<main><section class="sec" id="iletisim">{head("01", "İletişim")}<div class="rows rv">{r}</div></section>'
        f'<section class="sec">{head("02", "Otel")}'
        f'<figure class="pic rv"><img src="img/sig.jpg" alt="Belek kıyısında sığ, turkuaz deniz" loading="lazy">'
        f'<figcaption class="cap"><span class="t"><b>PALOMA</b><span>{letters(hotel)}</span></span>'
        f'<p>{e(tr_upper(d["grup"]))}</p></figcaption></figure>'
        f'<div class="addr rv"><p>{e(street)}<br>{e(district)} / {e(city)}</p>'
        f'<a class="link" href="{e(d["harita"])}" target=_blank rel=noopener>YOL TARİFİ{icon("arrow")}</a></div>'
        f'</section>'
        f'<section class="sec">{head("03", "Kartvizit")}'
        f'<div class="qcard rv"><div class="tile">{qr_svg(d["qr"])}<span class="vf" aria-hidden="true">'
        f'<i></i><i></i><i></i><i></i></span></div><p class="qcap"><span>DİJİTAL</span><i></i><span>KARTVİZİT</span>'
        f'</p></div><p class="qtxt rv">Masadaki isimlikte de aynı kod var.<br>Ekrandan okutarak kartviziti '
        f'paylaşabilirsiniz.</p>'
        f'<div class="btns rv"><a class="save" href="{VCF}" download>{icon("save")}REHBERE KAYDET</a>'
        f'<button class="share" id="share" type="button">{icon("share")}<b>KARTVİZİTİ PAYLAŞ</b></button></div>'
        f'</section></main>'
        f'<footer class="rv">{lockup("lock", hotel)}<p>BELEK · ANTALYA</p></footer></div>'
        f'<nav class="callbar" aria-label="Hemen iletişim"><a href="tel:+{d["cep_e164"]}">{icon("phone")}ARA</a>'
        f'<a class="wa" href="{e(wa)}" target=_blank rel=noopener>{icon("whatsapp")}WHATSAPP</a></nav>')
    title = f"{d['isim']} · {d['gorev']} · {d['otel']}"
    desc = f"{d['isim']} – {d['gorev']}, {d['otel']} ({d['grup']}). Ara, WhatsApp, e-posta, rehbere kaydet."
    og = d["sayfa_url"].rstrip("/") + "/" + OG
    ext_, fmt = ("woff2", "woff2") if _has_brotli() else ("woff", "woff")
    css = CSS.replace("EXT", ext_).replace("FMT", fmt)
    return (f'<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" '
            f'content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#16303C">'
            f'<title>{e(title)}</title><meta name="description" content="{e(desc)}">'
            f'<meta property="og:type" content="profile"><meta property="og:title" content="{e(title)}">'
            f'<meta property="og:description" content="{e(desc)}"><meta property="og:image" content="{e(og)}">'
            f'<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
            f'<meta name="twitter:card" content="summary_large_image">'
            f'<link rel="preload" as="image" href="img/ufuk.jpg">'
            f'<link rel="preload" as="font" type="font/{fmt}" href="fonts/f8.{ext_}" crossorigin>'
            f"<script>matchMedia('(prefers-reduced-motion: reduce)').matches||"
            f"document.documentElement.classList.add('mo')</script>"
            f'<style>{css}</style></head><body>{body}<script>{JS}</script></body></html>')


# ---------------------------------------------------------------- önizlemeler

def screenshot(path=PREVIEW):
    """Telefon ekranında (390 × 844): açık tema üst görünüm, açık tema tüm sayfa, koyu tema üst görünüm."""
    from playwright.sync_api import sync_playwright
    shots = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        for scheme, full in (("light", False), ("light", True), ("dark", False)):
            pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, reduced_motion="reduce",
                            color_scheme=scheme)
            pg.goto("file://" + os.path.join(OUT, "index.html"))
            pg.wait_for_timeout(500)
            assert pg.evaluate("[300,400,600,800].every(w=>document.fonts.check(w+' 20px Figtree'))"), \
                "yazı tipi yüklenmedi"
            assert pg.evaluate("document.documentElement.scrollWidth") <= 390, "yatay taşma"
            assert pg.evaluate("[...document.querySelectorAll('.rows b,.rows small,.role,h1,.dock a,.addr p')]"
                               ".every(e=>e.scrollWidth<=e.clientWidth+1)"), "yazı sığmadı"
            assert pg.evaluate("[...document.images].every(i=>i.complete&&i.naturalWidth>0)"), "görsel yüklenmedi"
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
    """Tur (390 × 844): açılış zamanda adım adım, sonra aşağı kaydırma."""
    from playwright.sync_api import sync_playwright
    frames, durs = [], []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)

        def shot(ms):
            frames.append(Image.open(io.BytesIO(pg.screenshot())).convert("RGB"))
            durs.append(ms)

        pg.goto("file://" + os.path.join(OUT, "index.html"))
        pg.wait_for_timeout(300)
        _seek(pg, 0)
        for k in range(0, 3000, 85):
            _seek(pg, k)
            shot(85)
        _finish(pg)
        shot(1100)
        h = pg.evaluate("document.documentElement.scrollHeight - innerHeight")
        for y in range(0, h + 1, 52):
            pg.evaluate(f"scrollTo(0,{y})")
            pg.wait_for_timeout(70)
            shot(75)
        for _ in range(8):
            pg.wait_for_timeout(160)
            shot(160)
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
    images()
    vcard(d)
    og_image(d)
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(doc)
    pack()
    size = sum(os.path.getsize(os.path.join(dp, fn)) for dp, _, fs in os.walk(OUT) for fn in fs)
    print("sayfa:", os.path.relpath(os.path.join(OUT, "index.html"), A.ROOT), f"(toplam {size // 1024} KB) →",
          d["sayfa_url"])
    print("önizleme:", os.path.relpath(screenshot(), A.ROOT))
    if "--hizli" not in sys.argv:
        print("tur:", os.path.relpath(tour_gif(), A.ROOT))


if __name__ == "__main__":
    main()
