"""PALOMA GRIDA – Süleyman Boylu'nun dijital kartviziti (isimlikteki QR bu sayfayı açar). 4. sürüm: tek parça kart.

Yazı sistemi Paloma Hotels logosundan: logonun harfleri Google yazı tipleriyle harf harf karşılaştırıldı, en yakını
Figtree çıktı (PALOMA satırı ExtraBold, HOTELS satırı Light). Sayfada da öyle: kalın ve aralıklı büyük harf ad
(SÜLEYMAN), ince ve aynı genişliğe yayılmış soyad (B O Y L U), küçük aralıklı etiketler; tırnaklı yazı yok.

Tasarım: tek ekran, tek parça; her bilgi bir kez geçer.
  * Arkada sabit görsel: ufukta Akdeniz (Blender, scripts/paloma_gorsel.py). Açık gökyüzünde logo | GRIDA ve isim
    koyu deniz mavisiyle; altta deniz.
  * Alttan gelen tek kart: cep (ara + WhatsApp), şirket hattı, e-posta, adres (harita); Rehbere kaydet ve Paylaş.
    Kısa ekranda kart görselin üstünden kayar.
  * Paylaş: alttan açılan pencerede isimlikteki QR'ın aynısı (DİJİTAL | KARTVİZİT), bağlantıyı kopyala / gönder.
  * Telefon koyu moddaysa kart ve pencere gece renklerine geçer.

Animasyon (sakin, tek akış):
  * Açılış (~2,6 sn): görsel yavaşça yaklaşır; PALOMA harfleri iner, HOTELS harfleri ortadan açılır, ayraç ve
    GRIDA; SÜLEYMAN harfleri maskeden çıkar, BOYLU harfleri ortadan yerlerine yayılır, ince çizgi uzar, görevin harf
    aralığı açılır; kart alttan gelir, satırlar çizgileriyle sırayla, simgeler çizilir.
  * Sürekli: deniz çok yavaş yaklaşıp uzaklaşır; Rehbere kaydet'in üstünden ara ara ışık geçer.
  * Paylaş penceresi alttan kayar, QR kareleri çapraz dalgayla belirir, vizör köşeleri nefes alır.
  "Hareketi azalt" açıksa hiçbiri oynamaz, sayfa doğrudan son hâliyle açılır.

Dış bağlantı yok: yazı tipi (Figtree, OFL), görsel, logo ve simgeler sayfanın yanında ya da içinde.
Bilgiler `paloma_isimlik/bilgiler.json`; logo paloma_isimlik/logo/ (scripts/paloma_logo.py).

Yayın: ortak Cloudflare hesabında (`qrsistem`) `suleymanboylu` adlı Worker'a `paloma_site.zip` yüklenir; adres
`https://suleymanboylu.qrsistem.workers.dev` (isimliklerdeki QR bu adresi açar). Sayfa `#qr` ile açılırsa Paylaş
penceresi açık gelir.

Çıktı : paloma_isimlik/site/, paloma_site.zip, sayfa_onizleme.png (açık, Paylaş penceresi, koyu), sayfa_tur.gif,
        sayfa_deneme.html (denemelik tek dosya: her şey içinde)

Kullanım:
  python3 scripts/paloma_gorsel.py ufuk      # önce görsel (bir kez)
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
STANDALONE = os.path.join(BASE, "sayfa_deneme.html")
CHROMIUM = "/opt/pw-browsers/chromium"
FONTS = {"f3": "Figtree_300Light.ttf", "f4": "Figtree_400Regular.ttf", "f6": "Figtree_600SemiBold.ttf",
         "f8": "Figtree_800ExtraBold.ttf"}
LICENSES = ("OFL-figtree.txt",)
VCF = "suleyman-boylu.vcf"
OG = "paylas.jpg"
LOGO = json.load(open(L.JSON, encoding="utf-8"))
SKY = "#D2E1F1"                              # görselin üstündeki gökyüzü: tarayıcı çubuğunun rengi

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
    "qr": '<rect x="4" y="4" width="6" height="6" rx="1"/><rect x="14" y="4" width="6" height="6" rx="1"/>'
          '<rect x="4" y="14" width="6" height="6" rx="1"/><path d="M14 14h2.5v2.5M20 14v.5M14 20h.5M17.5 17.5H20V20"/>',
    "copy": '<rect x="8.5" y="8.5" width="11.5" height="11.5" rx="2.5"/><path d="M15.5 5.5A2 2 0 0 0 13.5 4H6a2 2 0 0 0-2 '
            '2v7.5a2 2 0 0 0 1.5 1.94"/>',
    "close": '<path d="M6.5 6.5l11 11M17.5 6.5l-11 11"/>',
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
    """Blender görseli sayfa için: hafif renk ayarı, JPEG (ufuk 1080 × 1920)."""
    os.makedirs(os.path.join(OUT, "img"), exist_ok=True)
    im = Image.open(os.path.join(IMG, "ufuk.jpg")).convert("RGB")
    im = ImageEnhance.Color(im).enhance(1.12)
    im = ImageEnhance.Contrast(im).enhance(1.05)
    im.save(os.path.join(OUT, "img", "ufuk.jpg"), "JPEG", quality=80, optimize=True, progressive=True)


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


CSS = """
@font-face{font-family:Figtree;src:url(fonts/f3.EXT) format("FMT");font-weight:300;font-display:swap}
@font-face{font-family:Figtree;src:url(fonts/f4.EXT) format("FMT");font-weight:400;font-display:swap}
@font-face{font-family:Figtree;src:url(fonts/f6.EXT) format("FMT");font-weight:600;font-display:swap}
@font-face{font-family:Figtree;src:url(fonts/f8.EXT) format("FMT");font-weight:800;font-display:swap}
:root{--pb:#69A1BA;--pbd:#2F6F8C;--head:#17384A;--card:#FBFAF7;--ink:#14212A;--muted:#7B8790;--line:#E6E1D8;
  --tint:#EEF4F6;--btn:#17384A;--btnfg:#fff;--wa:#1E9E5A;--qr:#14212A;--shadow:rgba(16,44,58,.2);
  --e:cubic-bezier(.2,.75,.2,1);color-scheme:light}
@media (prefers-color-scheme:dark){:root{--card:#111A20;--ink:#EEF2F4;--muted:#8796A0;--line:#24323A;--tint:#1B2932;
  --pbd:#8EC2D8;--btn:#69A1BA;--btnfg:#0B1A21;--wa:#3CC57F;--shadow:rgba(0,0,0,.5);color-scheme:dark}}
*{box-sizing:border-box;margin:0;padding:0}
html{background:#0E1A20}
html.hold{overflow:hidden}
body{font-family:Figtree,system-ui,sans-serif;font-weight:400;color:var(--ink);-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
button{font:inherit;color:inherit;background:none;border:0;cursor:pointer}
[hidden]{display:none!important}
.wrap{position:relative;max-width:440px;margin:0 auto;min-height:100vh;min-height:100svh;display:flex;flex-direction:column;
  box-shadow:0 0 80px rgba(0,0,0,.35)}

/* ---------------- arka plan: ufukta Akdeniz, sabit; kart üstünden kayar */
.bg{position:fixed;top:0;left:50%;width:min(440px,100%);height:100vh;height:100lvh;transform:translateX(-50%);
  overflow:hidden;background:#BCD3E2}
.bg img{width:100%;height:100%;object-fit:cover;display:block}

/* ---------------- üst: logo ve isim (açık gökyüzünde koyu deniz mavisi) */
.top{position:relative;flex:1 0 auto;min-height:350px;padding:30px 28px 64px;color:var(--head)}
.lock{display:flex;align-items:center;gap:13px}
.lock .logo{width:118px;height:auto;display:block;overflow:visible}
.lock .bar{width:1.2px;height:31px;background:currentColor;opacity:.75}
.lock .grida{font-weight:600;font-size:11px;letter-spacing:.42em;margin-right:-.42em}
.who{margin-top:clamp(34px,6.5vh,64px)}
h1{display:inline-grid;font-size:clamp(28px,8.6vw,36px);line-height:1;text-transform:uppercase}
h1 .b{display:block;font-weight:800;letter-spacing:.3em;overflow:hidden;padding:.12em 0 .04em;margin-top:-.12em}
h1 .b span{display:inline-block}
h1 .b span:last-child{letter-spacing:0}
h1 .l{display:flex;justify-content:space-between;font-weight:300;margin-top:.2em}
h1 .l span{display:inline-block}
.who .rule{display:block;width:44px;height:1.5px;background:var(--pb);margin:20px 0 13px;transform-origin:left}
.role{font-weight:600;font-size:12px;letter-spacing:.3em;color:var(--pbd)}
@media (prefers-color-scheme:dark){.role{color:#2F6F8C}}

/* ---------------- kart: her bilgi bir kez */
.card{position:relative;z-index:1;margin-top:-26px;background:var(--card);border-radius:26px 26px 0 0;
  padding:8px 24px calc(24px + env(safe-area-inset-bottom));box-shadow:0 -12px 36px var(--shadow)}
.rows{list-style:none}
.rows li{position:relative;display:flex;align-items:center;gap:14px;padding:16px 0}
.rows li:after{content:"";position:absolute;left:0;right:0;bottom:0;height:1px;background:var(--line);transform-origin:left}
.v{flex:1;min-width:0}
.v:after{content:"";position:absolute;inset:0}
.v small{display:block;font-weight:600;font-size:9.5px;letter-spacing:.3em;color:var(--muted);text-transform:uppercase}
.v b{display:block;margin-top:6px;font-weight:300;font-size:23px;letter-spacing:.02em;font-variant-numeric:lining-nums;
  white-space:nowrap}
.em b,.ad b{font-size:17.5px;letter-spacing:0}
.ad b{line-height:1.3;white-space:normal}
.acts{display:flex;gap:8px;flex:none}
.ic{position:relative;width:44px;height:44px;border-radius:50%;display:grid;place-items:center;border:1px solid var(--line);
  color:var(--pbd);transition:transform .15s,background .15s}
span.ic{pointer-events:none}
a.ic{z-index:1}
.ic svg{width:20px;height:20px}
.ic.wa{color:var(--wa)}
.v:active~.acts span.ic,a.ic:active{transform:scale(.92);background:var(--tint)}
@media (hover:hover){.rows li:hover span.ic,a.ic:hover{background:var(--tint)}}
.btns{display:grid;grid-template-columns:1.55fr 1fr;gap:10px;margin-top:22px}
.save,.share{position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;gap:10px;height:56px;
  border-radius:14px;font-weight:600;font-size:11px;letter-spacing:.22em;white-space:nowrap}
.save{background:var(--btn);color:var(--btnfg)}
.share{border:1px solid var(--line);color:var(--ink)}
.save svg{width:20px;height:20px}
.share svg{width:19px;height:19px}
.save b,.share b{font-weight:600;margin-right:-.22em}
.save:after{content:"";position:absolute;top:0;bottom:0;left:-45%;width:40%;
  background:linear-gradient(100deg,transparent,rgba(255,255,255,.28),transparent)}

/* ---------------- paylaş penceresi: isimlikteki QR */
dialog{position:fixed;inset:0;width:100%;height:100%;max-width:none;max-height:none;margin:0;padding:0;border:0;
  background:transparent;color:var(--ink);overflow:hidden}
dialog::backdrop{background:transparent}
.scrim{position:absolute;inset:0;background:rgba(6,20,28,.55);opacity:0;transition:opacity .35s ease}
.panel{position:absolute;left:50%;bottom:0;width:min(440px,100%);max-height:100%;overflow:auto;
  transform:translate(-50%,104%);transition:transform .5s var(--e);background:var(--card);border-radius:26px 26px 0 0;
  padding:18px 24px calc(24px + env(safe-area-inset-bottom));box-shadow:0 -12px 36px var(--shadow)}
dialog.on .scrim{opacity:1}
dialog.on .panel{transform:translate(-50%,0)}
dialog.on.out .scrim{opacity:0}
dialog.on.out .panel{transform:translate(-50%,104%)}
.ph{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}
.ph p{font-weight:800;font-size:12px;letter-spacing:.34em}
.x{width:40px;height:40px;margin-right:-8px;border-radius:50%;display:grid;place-items:center;color:var(--muted)}
.x svg{width:20px;height:20px}
.qcard{display:flex;flex-direction:column;align-items:center;padding:34px 20px 24px;border-radius:20px;
  background:linear-gradient(160deg,#86B8CD,#69A1BA 55%,#5690AA);color:#fff}
.tile{position:relative;width:200px;padding:10px;background:#fff;border-radius:10px}
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
.qcap{display:flex;align-items:center;gap:14px;margin-top:26px;padding-left:.34em;font-weight:600;font-size:11px;
  letter-spacing:.34em}
.qcap i{width:1.2px;height:15px;background:#fff}
.hint{margin-top:16px;text-align:center;color:var(--muted);font-size:13.5px;line-height:1.5}
.hint b{display:block;font-weight:600;color:var(--pbd)}
.pbtns{display:flex;gap:10px;margin-top:18px}
.pbtns>*{flex:1}

/* ---------------- açılış: görsel yaklaşır, logo ve isim harf harf, kart alttan gelir */
.bg img{animation:kb 3.2s cubic-bezier(.15,.7,.25,1) both,drift 20s ease-in-out 3.2s infinite alternate}
.pl{transform-box:fill-box;transform-origin:50% 100%;animation:drop .65s var(--e) calc(.35s + var(--i)*.07s) both}
.ht{animation:spread 1s var(--e) calc(.6s + var(--i)*.02s) both}
.top .lock .bar{animation:grow-y .5s var(--e) 1s both}
.top .lock .grida{animation:wipe .8s var(--e) 1.1s both}
h1 .b span{animation:rise .8s var(--e) calc(.85s + var(--i)*.045s) both}
h1 .l span{animation:spread2 1.1s var(--e) calc(1.2s + var(--i)*.03s) both}
.who .rule{animation:grow-x .8s var(--e) 1.55s both}
.role{animation:track 1.1s var(--e) 1.65s both}
.card{animation:up 1s var(--e) 1.3s both}
.rows li{animation:slide .65s var(--e) calc(1.8s + var(--i)*.09s) both}
.rows li:after{animation:grow-x .9s var(--e) calc(1.9s + var(--i)*.09s) both}
.mo .ic [pathLength]{stroke-dasharray:1;stroke-dashoffset:1;animation:draw .8s ease-out calc(2.05s + var(--i)*.09s) forwards}
.ic .f{animation:fade .4s ease-out calc(2.55s + var(--i)*.09s) both}
.btns{animation:fade-up .8s var(--e) 2.25s both}
.save:after{animation:shine 5s ease-in-out 3.4s infinite}
.mo dialog .m{opacity:0}
.mo dialog.on .m{animation:px .45s var(--e) calc(.25s + var(--d)*1ms) both}
.mo dialog.on .tile:after{animation:sweep 1.5s ease-in-out 1.2s}
.vf i{animation:breathe 2.8s ease-in-out infinite}
.vf i:nth-child(2),.vf i:nth-child(3){animation-delay:.2s}

@keyframes kb{from{transform:scale(1.14)}to{transform:none}}
@keyframes drift{from{scale:1}to{scale:1.05}}
@keyframes drop{from{opacity:0;transform:translateY(-38%)}to{opacity:1;transform:none}}
@keyframes spread{from{opacity:0;transform:translateX(var(--dx))}to{opacity:1;transform:none}}
@keyframes spread2{from{opacity:0;transform:translateX(calc((2 - var(--i))*.95em))}to{opacity:1;transform:none}}
@keyframes rise{from{transform:translateY(115%)}to{transform:none}}
@keyframes grow-y{from{transform:scaleY(0)}to{transform:none}}
@keyframes grow-x{from{transform:scaleX(0)}to{transform:none}}
@keyframes wipe{from{clip-path:inset(0 100% 0 0);transform:translateX(-8px)}to{clip-path:inset(0);transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes fade-up{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes up{from{transform:translateY(100%)}to{transform:none}}
@keyframes track{from{opacity:0;letter-spacing:.9em}to{opacity:1;letter-spacing:.3em}}
@keyframes draw{to{stroke-dashoffset:0}}
@keyframes slide{from{opacity:0;transform:translateX(-18px)}to{opacity:1;transform:none}}
@keyframes px{from{opacity:0;transform:scale(.2)}to{opacity:1;transform:none}}
@keyframes sweep{0%{opacity:0;top:0}15%{opacity:1}85%{opacity:1}100%{opacity:0;top:78%}}
@keyframes breathe{0%,100%{transform:none;opacity:1}50%{transform:scale(1.12);opacity:.6}}
@keyframes shine{0%,78%{left:-45%}100%{left:125%}}
@media (prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}}
"""

JS = """
(()=>{const R=document.documentElement,D=document.getElementById('qr'),P=D.querySelector('.panel'),U=D.dataset.url,
  send=document.getElementById('send'),copy=document.getElementById('copy'),
  calm=()=>matchMedia('(prefers-reduced-motion: reduce)').matches;
if(document.hidden){const as=document.getAnimations();as.forEach(a=>a.pause());
  addEventListener('visibilitychange',()=>{if(!document.hidden)as.forEach(a=>a.play())},{once:true})}
const open=()=>{if(D.open)return;D.showModal();R.classList.add('hold');void P.offsetWidth;D.classList.add('on')};
const close=()=>{if(!D.open||D.classList.contains('out'))return;D.classList.add('out');
  const done=()=>{D.classList.remove('on','out');D.close();R.classList.remove('hold')};calm()?done():setTimeout(done,420)};
document.getElementById('share').onclick=open;
D.addEventListener('cancel',ev=>{ev.preventDefault();close()});
D.querySelectorAll('[data-close]').forEach(el=>el.onclick=close);
if(!navigator.share)send.hidden=true;
send.onclick=async()=>{try{await navigator.share({title:document.title,url:U})}catch(x){}};
copy.onclick=async()=>{const b=copy.querySelector('b');let ok=false;
  try{await navigator.clipboard.writeText(U);ok=true}catch(x){const t=document.createElement('textarea');t.value=U;
    t.setAttribute('readonly','');t.style.cssText='position:fixed;opacity:0';P.appendChild(t);t.select();
    try{ok=document.execCommand('copy')}catch(y){}t.remove()}
  if(ok){b.textContent='KOPYALANDI';setTimeout(()=>b.textContent='KOPYALA',2000)}};
if(location.hash==='#qr')open();})();
"""


def page(d):
    first, last = tr_upper(d["isim"]).split(" ", 1)
    wa = f"https://wa.me/{d['cep_e164']}?text=" + d["whatsapp_mesaj"].replace(" ", "%20").replace(",", "%2C")
    hotel = d["otel"].split()[-1].upper()
    street, district, city, _ = d["adres"]
    deco = lambda k: f'<span class="ic" aria-hidden="true">{icon(k, True)}</span>'  # noqa: E731
    rows = [("", "Cep telefonu", e(d["cep_txt"]), f"tel:+{d['cep_e164']}",
             f'<a class="ic wa" href="{e(wa)}" target=_blank rel=noopener aria-label="WhatsApp ile yazın">'
             f'{icon("whatsapp", True)}</a>{deco("phone")}'),
            ("", "Şirket hattı", e(d["sirket_txt"]), f"tel:+{d['sirket_e164']}", deco("phone")),
            ("em", "E-posta", e(d["eposta"]), f"mailto:{d['eposta']}", deco("mail")),
            ("ad", "Adres", f"{e(street)}<br>{e(district)} / {e(city)}", d["harita"], deco("pin"))]
    li = "".join(f'<li class="{c}" style="--i:{k}"><a class="v" href="{e(h)}"'
                 f'{" target=_blank rel=noopener" if h.startswith("http") else ""}><small>{lab}</small><b>{v}</b></a>'
                 f'<span class="acts">{acts}</span></li>' for k, (c, lab, v, h, acts) in enumerate(rows))
    url = d["qr"]
    body = (
        f'<div class="bg" aria-hidden="true"><img src="img/ufuk.jpg" alt="" fetchpriority="high"></div>'
        f'<div class="wrap"><header class="top">{lockup("lock", hotel, True)}'
        f'<div class="who"><h1 aria-label="{e(d["isim"])}"><span class="b" aria-hidden="true">{letters(first)}</span>'
        f'<span class="l" aria-hidden="true">{letters(last)}</span></h1>'
        f'<i class="rule"></i><p class="role">{e(tr_upper(d["gorev"]))}</p></div></header>'
        f'<main class="card"><ul class="rows">{li}</ul>'
        f'<div class="btns"><a class="save" href="{VCF}" download>{icon("save")}<b>REHBERE KAYDET</b></a>'
        f'<button class="share" id="share" type="button" aria-haspopup="dialog">{icon("qr")}<b>PAYLAŞ</b></button>'
        f'</div></main></div>'
        f'<dialog id="qr" aria-labelledby="qrt" data-url="{e(url)}"><div class="scrim" data-close></div>'
        f'<div class="panel"><div class="ph"><p id="qrt">KARTVİZİTİ PAYLAŞ</p>'
        f'<button class="x" type="button" data-close aria-label="Kapat">{icon("close", width=1.6)}</button></div>'
        f'<div class="qcard"><div class="tile">{qr_svg(url)}<span class="vf" aria-hidden="true"><i></i><i></i><i></i>'
        f'<i></i></span></div><p class="qcap"><span>DİJİTAL</span><i></i><span>KARTVİZİT</span></p></div>'
        f'<p class="hint">Kodu kamerayla okutun ya da bağlantıyı gönderin.'
        f'<b>{e(url.replace("https://", ""))}</b></p>'
        f'<div class="pbtns"><button class="share" id="copy" type="button">{icon("copy")}<b>KOPYALA</b></button>'
        f'<button class="save" id="send" type="button">{icon("share")}<b>GÖNDER</b></button></div></div></dialog>')
    title = f"{d['isim']} · {d['gorev']} · {d['otel']}"
    desc = f"{d['isim']} – {d['gorev']}, {d['otel']} ({d['grup']}). Ara, WhatsApp, e-posta, rehbere kaydet."
    og = d["sayfa_url"].rstrip("/") + "/" + OG
    ext_, fmt = ("woff2", "woff2") if _has_brotli() else ("woff", "woff")
    css = CSS.replace("EXT", ext_).replace("FMT", fmt)
    return (f'<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" '
            f'content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="{SKY}">'
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
    """Telefon ekranında (390 × 844): açık tema, Paylaş penceresi (QR), koyu tema. Kontroller: yazı tipleri yüklü,
    yatay taşma yok, yazılar kutularına sığıyor, kart tek ekrana sığıyor, penceredeki QR okunuyor."""
    from playwright.sync_api import sync_playwright
    url = load()["qr"]
    fits = ("[...document.querySelectorAll('SEL')].every(e=>e.offsetParent===null||e.scrollWidth<=e.clientWidth+1)")
    shots = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        for scheme, share in (("light", False), ("light", True), ("dark", False)):
            pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, reduced_motion="reduce",
                            color_scheme=scheme)
            pg.add_init_script("navigator.share=async()=>{}")      # telefondaki gibi: Gönder düğmesi görünür
            pg.goto("file://" + os.path.join(OUT, "index.html"))
            pg.wait_for_timeout(500)
            assert pg.evaluate("[300,400,600,800].every(w=>document.fonts.check(w+' 20px Figtree'))"), \
                "yazı tipi yüklenmedi"
            assert pg.evaluate("document.documentElement.scrollWidth") <= 390, "yatay taşma"
            assert pg.evaluate(fits.replace("SEL", ".v b,.v small,.role,h1,.save,.share,.lock")), "yazı sığmadı"
            assert pg.evaluate("[...document.images].every(i=>i.complete&&i.naturalWidth>0)"), "görsel yüklenmedi"
            assert pg.evaluate("document.querySelector('.card').getBoundingClientRect().bottom") <= 845, \
                "kart tek ekrana sığmadı"
            if share:
                pg.click("#share")
                pg.wait_for_timeout(300)
                assert pg.evaluate(fits.replace("SEL", ".ph p,.qcap,.hint b,.pbtns button")), "pencerede yazı sığmadı"
                tile = Image.open(io.BytesIO(pg.locator(".tile").screenshot()))
                assert url in Q.decode(tile), "penceredeki QR okunmadı"
            shots.append(Image.open(io.BytesIO(pg.screenshot())))
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
    """Tur (390 × 844): açılış zamanda adım adım, bekleme, sonra Paylaş penceresi (QR dalgası) adım adım."""
    from playwright.sync_api import sync_playwright
    frames, durs = [], []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
        pg.add_init_script("navigator.share=async()=>{}")

        def shot(ms):
            frames.append(Image.open(io.BytesIO(pg.screenshot())).convert("RGB"))
            durs.append(ms)

        pg.goto("file://" + os.path.join(OUT, "index.html"))
        pg.wait_for_timeout(300)
        _seek(pg, 0)
        for k in range(0, 3000, 90):
            _seek(pg, k)
            shot(90)
        _finish(pg)
        shot(1600)
        pg.evaluate("document.getElementById('share').click();window._dl=document.getAnimations().filter(a=>{"
                    "const t=a.effect&&a.effect.target;return t&&t.closest&&t.closest('dialog')});"
                    "_dl.forEach(a=>{a.pause();a.currentTime=0})")
        for k in range(0, 1700, 85):
            pg.evaluate(f"_dl.forEach(a=>a.currentTime={k})")
            shot(85)
        pg.evaluate("_dl.forEach(a=>{try{a.finish()}catch(e){a.play()}})")
        shot(2600)
        b.close()
    return _gif(frames, durs, path)


def standalone(doc, path=STANDALONE):
    """Denemelik tek dosya: yazı tipleri, görsel ve rehber kartı (vCard) sayfanın içine gömülü; hiçbir yere
    yüklemeden telefonda ya da tarayıcıda açılır. (Asıl yayın site/ klasörü ve zip.)"""
    import base64
    import re

    def data(rel, mime):
        with open(os.path.join(OUT, rel), "rb") as f:
            return f"data:{mime};base64," + base64.b64encode(f.read()).decode()

    doc = re.sub(r'<link rel="preload"[^>]*>', "", doc)
    for rel in sorted(set(re.findall(r"fonts/f\d\.woff2?", doc))):
        doc = doc.replace(f"url({rel})", f"url({data(rel, 'font/' + rel.rsplit('.', 1)[1])})")
    doc = doc.replace('src="img/ufuk.jpg"', f'src="{data("img/ufuk.jpg", "image/jpeg")}"')
    doc = doc.replace(f'href="{VCF}" download', f'href="{data(VCF, "text/vcard")}" download="{VCF}"')
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    return path


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
    standalone(doc)
    size = sum(os.path.getsize(os.path.join(dp, fn)) for dp, _, fs in os.walk(OUT) for fn in fs)
    print("sayfa:", os.path.relpath(os.path.join(OUT, "index.html"), A.ROOT), f"(toplam {size // 1024} KB) →",
          d["sayfa_url"])
    print("deneme:", os.path.relpath(STANDALONE, A.ROOT), f"({os.path.getsize(STANDALONE) // 1024} KB, tek dosya)")
    print("önizleme:", os.path.relpath(screenshot(), A.ROOT))
    if "--hizli" not in sys.argv:
        print("tur:", os.path.relpath(tour_gif(), A.ROOT))


if __name__ == "__main__":
    main()
