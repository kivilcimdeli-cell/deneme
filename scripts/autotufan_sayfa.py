"""AUTO TUFAN – Hasar Onarım (Kepez, Antalya): isimlikteki QR ile açılan işletme sayfası. 3. sürüm.

1. sürüm (sakin, tek kart) beğenilmedi: "lastikçilere yaptığımız gibi, havalı olsun". 2. sürüm (lastikçi dili, çizgi
araba) için: "hizalamalar iyi değil, arabayı sil, boyama animasyonu gibi bir şey ekle, daha havalı". Bu sürüm:
  * Başlık ortalı: karbon fiber zemin, altın fırça T, sonra açılışın gösterisi: boya tabancası soldan sağa geçip
    altın fırça darbesini boyar (isimliğin 5 numarasındaki bantın aynısı; içinde oyma AUTO TUFAN), etrafa boya
    zerrecikleri saçılır, sonunda bantın altından boya damlaları akar; havada ince altın toz kalır.
  * Altın HEMEN ARA bloğu; kutucuklar aynı iskelette (simge ve ok, başlık, alt satır): başlıklar ve alt satırlar
    hizalı; hepsi aynı kenar payında (20 px). Ara düğmesi ekrandan çıkınca sağ altta altın ara düğmesi belirir.
  * Ödeme bilgileri: IBAN, Kopyala, Karekod (açılır: kaydedilir, banka uygulamasında galeriden okutulur).
    IBAN şimdilik örnek (`iban_ornek`). Rehbere ekle ve Paylaş (isimlikteki QR) yan yana; altbilgi ortalı.
Bağlantılar aynı sekmede açılır (yeni sekme QR okuyucuların iç tarayıcılarında ve önizlemelerde çoğu zaman
açılmaz). Açılır kutular JavaScript'siz de açılır (#karekod, #paylas bağlantısı, CSS :target).
Zerrecikler canvas'ta; zamanlarını bantın CSS animasyonundan okur: tabanca, boya ve zerrecikler hep aynı anda.
"Hareketi azalt" açıksa hiçbiri oynamaz, sayfa son hâliyle açılır.

Yayın: ortak Cloudflare hesabında (`qrsistem`) `deneme123` adlı Worker'a `autotufan_site.zip` yüklenir; adres
`https://deneme123.qrsistem.workers.dev` (isimlikteki QR bu adresi açar).

Çıktı : autotufan_isimlik/site/, autotufan_site.zip, sayfa_onizleme.png (ilk ekran, tüm sayfa), sayfa_tur.gif,
        sayfa_deneme.html (denemelik tek dosya: her şey içinde)

Kullanım:
  python3 scripts/autotufan_sayfa.py            # site, zip, önizleme ve tur
  python3 scripts/autotufan_sayfa.py --hizli    # GIF'siz
"""
import contextlib
import html
import io
import json
import os
import re
import shutil
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import autotufan_isimlik as AT  # noqa: E402
import autotufan_logo as L  # noqa: E402
import qr_sistemi as Q  # noqa: E402
from ince_sayfa import _seek  # noqa: E402

BASE = os.path.join(A.ROOT, "autotufan_isimlik")
OUT = os.path.join(BASE, "site")
ZIP = os.path.join(BASE, "autotufan_site.zip")
PREVIEW = os.path.join(BASE, "sayfa_onizleme.png")
TOUR = os.path.join(BASE, "sayfa_tur.gif")
STANDALONE = os.path.join(BASE, "sayfa_deneme.html")
CHROMIUM = "/opt/pw-browsers/chromium"
FONTS = {"p4": ("Poppins-Regular.ttf", 400, "normal"), "p5": ("Poppins-Medium.ttf", 500, "normal"),
         "p6": ("Poppins-SemiBold.ttf", 600, "normal"), "p7": ("Poppins-Bold.ttf", 700, "normal"),
         "p8": ("Poppins-ExtraBold.ttf", 800, "normal"), "p8i": ("Poppins-ExtraBoldItalic.ttf", 800, "italic"),
         "p6i": ("Poppins-SemiBoldItalic.ttf", 600, "italic")}
LICENSES = ("OFL-poppins.txt",)
VCF = "auto-tufan.vcf"
OG = "paylas.jpg"
ICON_PNG = "simge.png"
KAREKOD = "karekod.png"
LOGO = json.load(open(L.JSON, encoding="utf-8"))
GOLD = (232, 182, 90)

ICON = {
    "phone": '<path d="M6.6 3.5h2.6l1.4 4.2-2 1.4a12 12 0 0 0 6.3 6.3l1.4-2 4.2 1.4v2.6a2 2 0 0 1-2.2 2A16.5 16.5 0 0 1 '
             '4.6 5.7a2 2 0 0 1 2-2.2z"/>',
    "whatsapp": '<path d="M4.5 19.5l1.2-4A8 8 0 1 1 9 18.6z"/><path fill="currentColor" stroke="none" '
                'd="M9.2 8.6c.2-.5.6-.6.9-.6.4 0 .6.6.9 1.4.2.5-.4.9-.6 1.2.6 1.2 1.6 2.2 2.9 2.8.3-.3.7-.9 1.2-.7.8.3 '
                '1.4.6 1.4 1 0 .3-.1.7-.6.9-.7.4-1.7.4-3-.2a8 8 0 0 1-3.4-3.3c-.5-1.1-.5-1.9.3-2.5z"/>',
    "instagram": '<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/>'
                 '<circle fill="currentColor" stroke="none" cx="17.2" cy="6.8" r="1.1"/>',
    "globe": '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.5 2.6 3.6 5.4 3.6 8.5s-1.1 5.9-3.6 8.5M12 '
             '3.5C9.5 6.1 8.4 8.9 8.4 12s1.1 5.9 3.6 8.5"/>',
    "pin": '<path d="M12 21s-6.5-6-6.5-11a6.5 6.5 0 0 1 13 0c0 5-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.4"/>',
    "star": '<path fill="currentColor" stroke="none" d="M12 3.8l2.5 5.2 5.6.7-4.1 3.9 1 5.6L12 16.5l-5 2.7 1-5.6-4.1-3.9 '
            '5.6-.7z"/>',
    "save": '<circle cx="9" cy="8.5" r="3.5"/><path d="M3.5 19c.8-3.2 3-4.8 5.5-4.8 1.4 0 2.7.4 3.7 1.3M17.5 13v7M14 16.5h7"/>',
    "share": '<circle cx="17.5" cy="5.5" r="2.5"/><circle cx="6.5" cy="12" r="2.5"/><circle cx="17.5" cy="18.5" r="2.5"/>'
             '<path d="M8.7 10.8l6.6-4M8.7 13.2l6.6 4"/>',
    "qr": '<rect x="4" y="4" width="6" height="6" rx="1"/><rect x="14" y="4" width="6" height="6" rx="1"/>'
          '<rect x="4" y="14" width="6" height="6" rx="1"/><path d="M14 14h2.5v2.5M20 14v.5M14 20h.5M17.5 17.5H20V20"/>',
    "copy": '<rect x="8.5" y="8.5" width="11.5" height="11.5" rx="2.5"/><path d="M15.5 5.5A2 2 0 0 0 13.5 4H6a2 2 0 0 0-2 '
            '2v7.5a2 2 0 0 0 1.5 1.94"/>',
    "arrow": '<path d="M7 17L17 7M9 7h8v8"/>',
    "down": '<path d="M12 4v12M6 11l6 6 6-6M5 20h14"/>',
}


def icon(k, width=1.7, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON[k]}</svg>')


def e(s):
    return html.escape(str(s))


def tr_title(s):
    """Türkçe baş harfler: HASAR ONARIM → Hasar Onarım (Python'un title()'ı I'yı i yapar)."""
    low = s.replace("I", "ı").replace("İ", "i").lower()
    return " ".join(w[:1].replace("i", "İ").replace("ı", "I").upper() + w[1:] for w in low.split())


def load():
    d = json.load(open(os.path.join(BASE, "bilgiler.json"), encoding="utf-8"))
    d["tel_e164"] = Q.phone_e164(d["telefon"])
    d["tel_txt"] = Q.phone_display(d["tel_e164"])
    d["qr"] = Q.https_url(d["sayfa_url"]).rstrip("/")             # isimlikteki QR ile aynı içerik
    d["insta"] = Q.instagram_handle(d["instagram"])
    raw = re.sub(r"\s", "", d["iban"]).upper()
    if d.get("iban_ornek"):
        print(f"Not: IBAN örnek ({d['iban']}); gerçeği bilgiler.json'a yazılıp iban_ornek kaldırılmalı.")
        d["iban_raw"] = raw
    else:
        d["iban_raw"] = Q.iban_normalize(raw)                    # mod-97 doğrulanır
    d["iban_txt"] = " ".join(d["iban_raw"][i:i + 4] for i in range(0, len(d["iban_raw"]), 4))
    if d.get("iban_karekod"):
        Q.karekod_check(d["iban_karekod"], None if d.get("iban_ornek") else d["iban_raw"])
    d["pay_qr"] = d.get("iban_karekod") or d["iban_raw"]
    d["web_txt"] = re.sub(r"^https?://(www\.)?", "", d["web"]).rstrip("/")
    d["wa"] = f"https://wa.me/{d['tel_e164']}?text=" + d["whatsapp_mesaj"].replace(" ", "%20").replace(",", "%2C")
    return d


# ---------------------------------------------------------------- dosyalar

def _has_brotli():
    """woff2 için fontTools brotli ister; yoksa woff."""
    import importlib.util
    return importlib.util.find_spec("brotli") is not None


def subset_fonts(text):
    from fontTools import subset
    fdir = os.path.join(OUT, "fonts")
    os.makedirs(fdir, exist_ok=True)
    chars = text + "ABCÇDEFGĞHIİJKLMNOÖPQRSŞTUÜVWXYZabcçdefgğhıijklmnoöpqrsştuüvwxyz0123456789 .,:;·+-–—/@&()'\"!?→"
    for key, (fn, _, _) in FONTS.items():
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


def vcard(d):
    lines = ["BEGIN:VCARD", "VERSION:3.0", f"N:;{d['isim']};;;", f"FN:{d['isim']}", f"ORG:{d['isim']}",
             f"TITLE:{tr_title(d['hizmet'])}", f"TEL;TYPE=WORK,CELL,VOICE:+{d['tel_e164']}",
             f"ADR;TYPE=WORK:;;;{d['konum'].split(',')[0].strip()};{d['sehir'].title()};;Türkiye",
             f"URL:{d['web']}", f"URL:{d['sayfa_url']}",
             f"X-SOCIALPROFILE;TYPE=instagram:https://instagram.com/{d['insta']}", "END:VCARD"]
    with open(os.path.join(OUT, VCF), "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(lines) + "\n")


def karekod_png(d):
    """Ödeme karekodu PNG (kaydedilip banka uygulamasında galeriden okutulur)."""
    import segno
    segno.make(d["pay_qr"], error="m", micro=False).save(os.path.join(OUT, KAREKOD), scale=12, border=3)


def carbon(W, H):
    """Karbon fiber dokusu (paylaşım görseli ve simge için)."""
    y, x = np.mgrid[0:H, 0:W]
    cell = 12
    u, v = (x % (2 * cell)) / cell, (y % (2 * cell)) / cell
    weave = np.where((u < 1) ^ (v < 1), 0.6 + 0.4 * np.sin(np.pi * (y % cell) / cell),
                     0.6 + 0.4 * np.sin(np.pi * (x % cell) / cell))
    base = 16 + 14 * weave
    img = np.stack([base, base, base * 1.04], -1)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))


def og_image(d):
    """Bağlantı paylaşılınca görünen görsel (1200 × 630): karbon zemin, altın şeritler, T, AUTO TUFAN."""
    W, H = 1200, 630
    im = carbon(W, H).convert("RGBA")
    dr = ImageDraw.Draw(im)
    dr.polygon([(860, 0), (1040, 0), (760, H), (580, H)], fill=GOLD + (255,))
    dr.polygon([(1080, 0), (1120, 0), (840, H), (800, H)], fill=(180, 130, 50, 255))
    shade = Image.new("RGBA", (W, H))
    sd = ImageDraw.Draw(shade)
    for x in range(W):
        sd.line([(x, 0), (x, H)], fill=(10, 10, 12, int(235 * max(0, 1 - x / 820) ** 0.6)))
    im = Image.alpha_composite(im, shade)
    T = AT.t_raster(150, GOLD)
    im.paste(T, (70, 70), T)
    dr = ImageDraw.Draw(im)
    f = lambda fn, n: ImageFont.truetype(os.path.join(A.FONT_DIR, fn), n)  # noqa: E731
    dr.text((76, 250), "AUTO", font=f("Poppins-Bold.ttf", 46), fill=GOLD)
    dr.text((66, 290), "TUFAN", font=f("Poppins-ExtraBoldItalic.ttf", 150), fill=(246, 246, 242))
    dr.text((78, 488), "HASAR ONARIM", font=f("Poppins-SemiBold.ttf", 34), fill=(246, 246, 242))
    dr.text((78, 538), f"{d['konum'].replace(', ', ' · ')}  ·  {d['tel_txt']}", font=f("Poppins-Regular.ttf", 28),
            fill=(190, 190, 194))
    im.convert("RGB").save(os.path.join(OUT, OG), "JPEG", quality=86, optimize=True)


def touch_icon():
    """Ana ekran / sekme simgesi (180 × 180): karbon zeminde altın fırça T."""
    im = carbon(180, 180).convert("RGBA")
    T = AT.t_raster(84, GOLD)
    im.paste(T, ((180 - T.width) // 2, (180 - T.height) // 2), T)
    im.convert("RGB").save(os.path.join(OUT, ICON_PNG), optimize=True)


# ---------------------------------------------------------------- çizimler

def t_svg(cls):
    """Fırça T (altın degrade)."""
    w, h = LOGO["svg_boyut"]
    return (f'<svg class="{cls}" viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="Auto Tufan logosu">'
            f'<defs><linearGradient id="tg{cls}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F9D27E"/>'
            f'<stop offset=".55" stop-color="#E8AE4C"/><stop offset="1" stop-color="#C98526"/></linearGradient></defs>'
            f'<path d="{LOGO["d"]}" fill="url(#tg{cls})" fill-rule="evenodd"/></svg>')


def _path(poly, top):
    """Çokgen → SVG yolu (y aşağı: top − y)."""
    return "M" + "L".join(f"{x:.2f} {top - y:.2f}" for x, y in poly) + "Z"


BAND_H, DRIP_ROOM = 22.0, 13.0
DRIPS = [(9.0, 7.5, 2.4), (31.0, 4.0, 1.9), (58.0, 10.0, 2.8), (79.0, 5.5, 2.1), (93.0, 8.0, 2.3)]


def band_svg(name):
    """Fırça darbesi (isimliğin 5 numarasındaki gibi, aynı geometri): altın degrade, içinde oyma AUTO TUFAN (maske);
    altından boya damlaları akar. viewBox 100 birim genişlik."""
    band = AT.brush_band(0.0, 100.0, 0.0, BAND_H, seed=5)
    b = band.bounds()
    top = b[3]
    W, H = b[2] - b[0], b[3] - b[1]
    d = "".join(_path(p, top) for p in band.to_polygons())
    drips = []
    for k, (x, length, w) in enumerate(DRIPS):
        yb = top - (band ^ A.rect(x - 0.2, -50, x + 0.2, 50)).bounds()[1]      # bantın alt kenarı (svg)
        drips.append(f'<g class="drip" style="--i:{k}"><path d="M{x - w / 2:.2f} {yb - 1.5:.2f}H{x + w / 2:.2f}'
                     f'V{yb + length:.2f}H{x - w / 2:.2f}Z"/><circle cx="{x:.2f}" cy="{yb + length:.2f}" '
                     f'r="{w * 0.62:.2f}"/></g>')
    cx = (b[0] + b[2]) / 2
    return (f'<svg class="band" viewBox="{b[0]:.2f} 0 {W:.2f} {H + DRIP_ROOM:.2f}" role="img" aria-label="{e(name)}">'
            f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FADB8E"/>'
            f'<stop offset=".45" stop-color="#E8AE4C"/><stop offset="1" stop-color="#C47F22"/></linearGradient>'
            f'<linearGradient id="dg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D99A3A"/>'
            f'<stop offset="1" stop-color="#B8741C"/></linearGradient>'
            f'<mask id="cut" maskUnits="userSpaceOnUse" x="{b[0]:.2f}" y="0" width="{W:.2f}" height="{H:.2f}">'
            f'<rect x="{b[0]:.2f}" y="0" width="{W:.2f}" height="{H:.2f}" fill="#fff"/>'
            f'<text x="{cx - 2.6:.2f}" y="{H / 2 + 4.1:.2f}" text-anchor="middle" font-family="Poppins" font-weight="800" '
            f'font-style="italic" font-size="11.8" letter-spacing=".25" fill="#000">{e(name.upper())}</text></mask>'
            f'</defs><g class="drips" fill="url(#dg)">{"".join(drips)}</g>'
            f'<path class="paintp" d="{d}" fill="url(#bg)" mask="url(#cut)"/></svg>')


def gun_svg():
    """Boya tabancası (isimliğin 4 numarasındaki şekil), aşağı-sağa eğik; namlunun ucunda boya konisi. Ucu SVG'nin
    (0, 0) noktasında: sayfada tam bantın boyanan kenarına oturur."""
    gun, _ = AT.spray_gun(0, 0, 1.0)
    ang = -38.0                                                  # namlu aşağı-sağa (y yukarı koordinatta)
    gun = gun.rotate(ang)
    tip = np.array([13.3, 0.0]) @ np.array([[np.cos(np.radians(ang)), np.sin(np.radians(ang))],
                                             [-np.sin(np.radians(ang)), np.cos(np.radians(ang))]])
    gun = gun.translate((-tip[0], -tip[1]))
    b = gun.bounds()
    d = "".join(_path(p, 0.0) for p in gun.to_polygons())
    return (f'<svg class="gunsvg" viewBox="{b[0] - 1:.1f} {-b[3] - 1:.1f} {b[2] - b[0] + 14:.1f} {b[3] - b[1] + 14:.1f}" '
            f'aria-hidden="true" style="--x:{(b[0] - 1):.2f};--y:{(-b[3] - 1):.2f};--w:{b[2] - b[0] + 14:.2f}">'
            f'<defs><linearGradient id="gg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFE3A3"/>'
            f'<stop offset="1" stop-color="#C98526"/></linearGradient><radialGradient id="cone" cx="0" cy="0" r="1">'
            f'<stop offset="0" stop-color="#FADB8E" stop-opacity=".85"/><stop offset="1" stop-color="#FADB8E" '
            f'stop-opacity="0"/></radialGradient></defs>'
            f'<path class="spray" d="M0 0L13 7.5L6 12Z" fill="url(#cone)"/>'
            f'<path d="{d}" fill="url(#gg)" stroke="#16120B" stroke-width=".5"/></svg>')


def stars(n=5):
    return '<span class="stars">' + "".join(icon("star", 0) for _ in range(n)) + "</span>"


def qr_svg(content, label):
    import segno
    q = segno.make(content, error="m", micro=False, boost_error=True)
    m = [[bool(v) for v in row] for row in q.matrix]
    n, qz = len(m), 2
    rects = "".join(f'<rect x="{x + qz}" y="{y + qz}" width="1" height="1"/>'
                    for y, row in enumerate(m) for x, v in enumerate(row) if v)
    s = n + 2 * qz
    return (f'<svg viewBox="0 0 {s} {s}" shape-rendering="crispEdges" role="img" aria-label="{e(label)}">'
            f'<rect width="{s}" height="{s}" fill="#fff"/><g fill="#111">{rects}</g></svg>')


# ---------------------------------------------------------------- sayfa

PAINT = (1.0, 1.4)                         # boyama: başlangıç ve süre (sn); CSS ve zerrecikler aynı zamanlamayla
EASE = (0.45, 0.05, 0.55, 0.95)            # boyamanın hız eğrisi (cubic-bezier)

CSS = """
FONTFACES
:root{--gold:#E8B65A;--gold2:#F7CB72;--gold3:#C98526;--ink:#F4F2EE;--muted:#9A978F;--line:rgba(255,255,255,.08);
  --tile:#141416;--edge:rgba(232,182,90,.2);--wa:#3CC57F;--g:20px;--e:cubic-bezier(.2,.75,.2,1);
  --paint:cubic-bezier(EASE);color-scheme:dark}
*{box-sizing:border-box;margin:0;padding:0}
html{background:#08080A}
body{font-family:Poppins,system-ui,sans-serif;color:var(--ink);background:#0B0B0D;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
button,summary{font:inherit;color:inherit;background:none;border:0;cursor:pointer}
summary{list-style:none}summary::-webkit-details-marker{display:none}
.wrap{position:relative;max-width:440px;margin:0 auto;min-height:100vh;background:#0B0B0D;overflow:hidden;
  box-shadow:0 0 80px rgba(0,0,0,.6)}

/* ---------------- başlık (ortalı): karbon fiber, T, boya tabancasının boyadığı fırça darbesi, HASAR ONARIM */
.hero{position:relative;padding:26px var(--g) 6px;text-align:center}
.carbon{position:absolute;inset:0;z-index:0;background:
  linear-gradient(27deg,#151517 5px,transparent 5px) 0 5px,linear-gradient(207deg,#151517 5px,transparent 5px) 10px 0,
  linear-gradient(27deg,#1f1f22 5px,transparent 5px) 0 10px,linear-gradient(207deg,#1f1f22 5px,transparent 5px) 10px 5px,
  linear-gradient(90deg,#1a1a1c 10px,transparent 10px),
  linear-gradient(#1c1c1f 25%,#18181a 25%,#18181a 50%,transparent 50%,transparent 75%,#222226 75%,#222226);
  background-color:#131315;background-size:20px 20px;
  -webkit-mask-image:linear-gradient(#000 0,#000 60%,transparent 100%);mask-image:linear-gradient(#000 0,#000 60%,transparent 100%)}
.carbon:after{content:"";position:absolute;inset:0;background:radial-gradient(70% 45% at 50% 46%,rgba(232,170,70,.16),
  transparent 70%)}
.dust{position:absolute;inset:0;z-index:2;width:100%;height:100%;pointer-events:none}
.hero>*:not(.carbon):not(.dust){position:relative;z-index:1}
.kick{display:flex;align-items:center;justify-content:center;gap:12px;font-weight:600;font-size:11px;letter-spacing:.32em;
  color:var(--muted)}
.kick span{margin-right:-.32em}
.kick i{width:24px;height:2px;background:var(--gold)}
.tlogo{display:block;width:104px;height:auto;margin:18px auto 4px;overflow:visible;filter:drop-shadow(0 6px 16px rgba(232,170,70,.3))}
.paint{position:relative;margin:10px -6px 0}
.band{display:block;width:100%;height:auto;overflow:visible;filter:drop-shadow(0 10px 22px rgba(232,170,70,.22))}
.drip{transform-box:fill-box;transform-origin:50% 0}
.gun{position:absolute;left:0;top:14%;width:0;height:0;pointer-events:none;opacity:0}
.gunsvg{position:absolute;width:86px;height:auto;left:calc(var(--x) / var(--w) * 86px);
  top:calc(var(--y) / var(--w) * 86px);overflow:visible;filter:drop-shadow(0 6px 10px rgba(0,0,0,.6))}
.svc{display:flex;align-items:center;justify-content:center;gap:14px;margin-top:6px}
.svc b{font-weight:700;font-size:15px;letter-spacing:.38em;margin-right:-.38em;white-space:nowrap}
.svc i{width:30px;height:2px;background:var(--gold)}
.tag{max-width:300px;margin:12px auto 0;font-size:13.5px;line-height:1.5;color:var(--muted)}

/* ---------------- hemen ara */
.call{position:relative;display:flex;align-items:center;justify-content:space-between;gap:12px;margin:22px var(--g) 0;
  padding:16px 14px 16px 22px;border-radius:18px;overflow:hidden;color:#16120B;
  background:linear-gradient(120deg,#F9D27E,#E8AE4C 55%,#D4902E);box-shadow:0 16px 40px rgba(232,170,70,.25)}
.call:before{content:"";position:absolute;inset:0;background:repeating-linear-gradient(-60deg,rgba(255,255,255,0) 0 14px,
  rgba(255,255,255,.08) 14px 22px);pointer-events:none}
.call:after{content:"";position:absolute;top:0;bottom:0;left:-40%;width:35%;
  background:linear-gradient(100deg,transparent,rgba(255,255,255,.55),transparent)}
.call>span{position:relative;min-width:0}
.call small{display:block;font-weight:700;font-size:11px;letter-spacing:.3em}
.call b{display:block;margin-top:2px;font-weight:800;font-style:italic;font-size:clamp(27px,8.2vw,34px);
  letter-spacing:-.005em;white-space:nowrap}
.call .ph{position:relative;flex:none;width:56px;height:56px;border-radius:50%;display:grid;place-items:center;
  background:#141416;color:var(--gold)}
.call .ph svg{width:25px;height:25px}
.call .ph:before{content:"";position:absolute;inset:-4px;border-radius:50%;border:2px solid #141416;opacity:0}

/* ---------------- kutucuklar: hepsi aynı iskelet (simge + ok, başlık, alt satır), satırlar hizalı */
.tiles{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;margin:12px var(--g) 0}
.tile{position:relative;grid-column:span 2;display:grid;grid-template-rows:24px 1fr 18px 17px;row-gap:2px;height:104px;
  padding:13px 12px 12px;border-radius:16px;background:var(--tile);border:1px solid var(--edge);overflow:hidden}
.tile.wide{grid-column:span 3}
.tile:after{content:"";position:absolute;right:-18px;bottom:-18px;width:60px;height:60px;transform:rotate(45deg);
  background:linear-gradient(135deg,rgba(232,182,90,.12),transparent);pointer-events:none}
.tile .top{display:flex;justify-content:space-between;align-items:flex-start}
.tile svg.i{width:24px;height:24px;color:var(--gold)}
.tile.wa svg.i{color:var(--wa)}
.tile .go{width:14px;height:14px;color:var(--muted)}
.tile b{grid-row:3;align-self:center;font-weight:700;font-style:italic;font-size:12.5px;letter-spacing:.02em;
  text-transform:uppercase;white-space:nowrap}
.tile small{grid-row:4;display:flex;align-items:center;font-size:11.5px;line-height:1;color:var(--muted);white-space:nowrap;
  overflow:hidden;text-overflow:ellipsis}
.tile:active{transform:scale(.97)}
.stars{display:flex;gap:2px}
.stars svg{width:12px;height:12px;color:var(--gold)}

/* ---------------- bölüm başlığı */
.sh{display:flex;align-items:center;gap:12px;margin:34px var(--g) 14px}
.sh i{width:14px;height:20px;background:linear-gradient(var(--gold2),var(--gold3));transform:skewX(-18deg)}
.sh h2{font-weight:800;font-style:italic;font-size:17px;letter-spacing:.08em;white-space:nowrap}
.sh:after{content:"";flex:1;height:1px;background:var(--line)}

/* ---------------- ödeme */
.pay{position:relative;margin:0 var(--g);padding:18px 16px 16px;border-radius:18px;
  background:linear-gradient(160deg,#1a1814,#121214 60%);border:1px solid var(--edge);overflow:hidden}
.pay:before{content:"";position:absolute;left:0;right:0;top:0;height:3px;background:linear-gradient(90deg,var(--gold2),var(--gold3))}
.pay .row{display:flex;justify-content:space-between;gap:12px;font-size:13px;color:var(--muted);margin-bottom:10px}
.pay .row b{color:var(--ink);font-weight:600}
.iban{padding:12px 14px;border-radius:12px;background:#0d0d0f;border:1px solid var(--line)}
.iban small{display:block;font-weight:600;font-size:10px;letter-spacing:.3em;color:var(--gold)}
.iban b{display:block;margin-top:4px;font-weight:600;font-size:15px;letter-spacing:.03em;white-space:nowrap;
  -webkit-user-select:all;user-select:all}
.pbtn{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:10px;margin-top:12px}
.btn{display:flex;align-items:center;justify-content:center;gap:9px;height:50px;border-radius:12px;font-weight:700;
  font-style:italic;font-size:13px;letter-spacing:.08em;text-transform:uppercase;white-space:nowrap}
.btn svg{width:18px;height:18px;flex:none}
.btn.gold{background:linear-gradient(120deg,#F9D27E,#E3A447);color:#16120B}
.btn.out{border:1px solid rgba(232,182,90,.45)}
/* açılır kutular: JavaScript .on ile açar; JavaScript yoksa bağlantı (#karekod, #paylas) :target ile */
.drop{display:none;grid-column:1/-1}
.drop:target,.drop.on{display:block}
.btn.act{background:rgba(232,182,90,.12)}
.qrbox{padding:16px;border-radius:14px;background:#0d0d0f;border:1px solid var(--line);text-align:center}
.qrbox>img,.qrbox>svg{display:block;width:190px;height:auto;margin:0 auto;border-radius:10px;background:#fff;padding:8px}
.qrbox p{margin-top:12px;font-size:12.5px;line-height:1.55;color:var(--muted)}
.qrbox p b{color:var(--ink);font-weight:600}
.qrbox a.dl{display:inline-flex;align-items:center;gap:6px;margin-top:10px;font-weight:600;font-size:13px;color:var(--gold);
  border-bottom:1px solid var(--gold);padding-bottom:2px}
.qrbox a.dl svg{width:15px;height:15px}
.note{margin-top:10px;font-size:11px;color:#6f6c66;text-align:center}

/* ---------------- kaydet, paylaş, altbilgi */
.acts{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:10px;margin:22px var(--g) 0}
.acts .btn{height:54px}
footer{margin:36px var(--g) 0;padding:24px 0 calc(34px + env(safe-area-inset-bottom));border-top:1px solid var(--line);
  display:flex;flex-direction:column;align-items:center;gap:6px;text-align:center}
footer svg{width:58px;height:auto}
footer p{font-weight:800;font-style:italic;font-size:17px;letter-spacing:.04em}
footer small{font-size:12px;color:var(--muted)}
.fab{position:fixed;right:max(18px,calc(50vw - 202px));bottom:calc(18px + env(safe-area-inset-bottom));z-index:9;
  width:60px;height:60px;border-radius:50%;display:grid;place-items:center;color:#16120B;
  background:linear-gradient(135deg,#F9D27E,#E3A447);box-shadow:0 10px 30px rgba(232,170,70,.35);
  transform:scale(0);transition:transform .35s var(--e)}
.fab.on{transform:none}
.fab svg{width:26px;height:26px}
.toast{position:fixed;left:50%;bottom:calc(92px + env(safe-area-inset-bottom));z-index:20;transform:translate(-50%,20px);
  opacity:0;visibility:hidden;padding:12px 18px;border-radius:12px;background:#1b1a17;border:1px solid var(--edge);
  font-size:13px;white-space:nowrap;transition:all .3s var(--e)}
.toast.on{opacity:1;visibility:visible;transform:translate(-50%,0)}

/* ---------------- açılış: T, boya tabancası soldan sağa geçip bantı boyar (zerrecikler JS), damlalar akar */
.kick{animation:fade .6s ease-out .2s both}
.tlogo{animation:brush .9s cubic-bezier(.6,.05,.3,1) .3s both}
.paintp{animation:reveal PAINTDs var(--paint) PAINTSs both}
.mo .gun{animation:gun PAINTDs var(--paint) PAINTSs both,gunout .5s ease-in PAINTENDs forwards}
.mo .spray{animation:spray .12s linear infinite alternate}
.drip{animation:drip 2.2s cubic-bezier(.5,0,.6,1) calc(PAINTENDs + var(--i)*.12s) both}
.svc{animation:fade-up .7s var(--e) PAINTENDs both}
.tag{animation:fade-up .7s var(--e) calc(PAINTENDs + .15s) both}
.call{animation:up .7s var(--e) calc(PAINTENDs + .25s) both}
.call:after{animation:shine 4.5s ease-in-out 4.5s infinite}
.mo .call .ph:before{animation:ring 2.4s ease-out 4s infinite}
.tiles .tile{animation:pop .55s var(--e) calc(PAINTENDs + .4s + var(--i)*.07s) both}
.mo .rv{opacity:0;transform:translateY(24px);transition:opacity .7s var(--e),transform .7s var(--e)}
.mo .rv.in{opacity:1;transform:none}

@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes brush{from{clip-path:inset(0 100% 0 0);opacity:.2}to{clip-path:inset(0);opacity:1}}
@keyframes reveal{from{clip-path:inset(-20% 100% -20% 0)}to{clip-path:inset(-20% 0 -20% 0)}}
@keyframes gun{from{left:0;opacity:1}to{left:100%;opacity:1}}
@keyframes gunout{from{left:100%;opacity:1;transform:none}to{left:100%;opacity:0;transform:translate(40px,-50px) rotate(20deg)}}
@keyframes spray{from{opacity:.55}to{opacity:1}}
@keyframes drip{from{transform:scaleY(0)}to{transform:none}}
@keyframes fade-up{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
@keyframes up{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:none}}
@keyframes shine{0%,75%{left:-40%}100%{left:120%}}
@keyframes ring{0%{opacity:.7;transform:scale(1)}100%{opacity:0;transform:scale(1.5)}}
@keyframes pop{from{opacity:0;transform:translateY(16px) scale(.96)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}
  .mo .rv{opacity:1;transform:none}.dust{display:none}}
"""

# Boya zerrecikleri ve havadaki altın toz (canvas). Zaman bantın CSS animasyonundan okunur (currentTime): tabanca,
# bant ve zerrecikler hep aynı anda; tur kaydında animasyonlar durdurulup ilerletilince zerrecikler de aynı kare.
JS = """
(()=>{const R=document.documentElement,mo=R.classList.contains('mo');
if(document.hidden){const as=document.getAnimations();as.forEach(a=>a.pause());
  addEventListener('visibilitychange',()=>{if(!document.hidden)as.forEach(a=>a.play())},{once:true})}
const toast=document.querySelector('.toast');let tt=0;
const say=s=>{toast.textContent=s;toast.classList.add('on');clearTimeout(tt);tt=setTimeout(()=>toast.classList.remove('on'),2200)};
const copy=async s=>{try{await navigator.clipboard.writeText(s);return true}catch(x){}const t=document.createElement('textarea');
  t.value=s;t.setAttribute('readonly','');t.style.cssText='position:fixed;opacity:0';document.body.appendChild(t);t.select();
  let ok=false;try{ok=document.execCommand('copy')}catch(y){}t.remove();return ok};
document.querySelectorAll('[data-copy]').forEach(b=>b.addEventListener('click',async ev=>{ev.preventDefault();
  if(await copy(b.dataset.copy))say(b.dataset.msg);else say('Kopyalanamadı: yazıya basılı tutun')}));
document.querySelectorAll('[data-toggle]').forEach(a=>a.addEventListener('click',ev=>{ev.preventDefault();
  const el=document.getElementById(a.dataset.toggle),on=el.classList.toggle('on');a.classList.toggle('act',on);
  if(on)el.scrollIntoView({block:'nearest',behavior:mo?'smooth':'auto'})}));
const sh=document.getElementById('send');if(sh&&!navigator.share)sh.hidden=true;
if(sh)sh.onclick=async()=>{try{await navigator.share({title:document.title,url:sh.dataset.url})}catch(x){}};
const fab=document.querySelector('.fab'),call=document.querySelector('.call');
if('IntersectionObserver' in window){new IntersectionObserver(([x])=>fab.classList.toggle('on',!x.isIntersecting&&
  x.boundingClientRect.top<0)).observe(call);
  const rv=[...document.querySelectorAll('.rv')];
  if(mo){const io=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting){x.target.classList.add('in');
    io.unobserve(x.target)}}),{threshold:.15});
    rv.forEach(el=>{if(el.getBoundingClientRect().top<innerHeight)el.style.transitionDelay='3.2s';io.observe(el)})}
  else rv.forEach(el=>el.classList.add('in'))}
else document.querySelectorAll('.rv').forEach(el=>el.classList.add('in'));
if(!mo)return;
try{const hero=document.querySelector('.hero'),cv=document.querySelector('.dust'),cx=cv.getContext('2d'),
  bandEl=document.querySelector('.band'),pp=document.querySelector('.paintp'),S=__S__,D=__D__,E=[__E__];
  const bz=(u,a,b)=>3*(1-u)*(1-u)*u*a+3*(1-u)*u*u*b+u*u*u;
  const ease=x=>{if(x<=0)return 0;if(x>=1)return 1;let u=x;for(let i=0;i<8;i++){const d=3*(1-u)*(1-u)*E[0]+
    6*(1-u)*u*(E[2]-E[0])+3*u*u*(1-E[2]);u-=(bz(u,E[0],E[2])-x)/(d||1e-6);u=Math.min(1,Math.max(0,u))}return bz(u,E[1],E[3])};
  let seed=7;const rnd=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296};
  const P=[...Array(460)].map(()=>({tb:S+D*rnd(),dx:(rnd()-.5)*10,yr:rnd(),vx:(rnd()-.3)*80,vy:(rnd()-.5)*110,
    l:.45+.9*rnd(),s:.6+1.7*rnd(),st:rnd()<.22,c:rnd()}));
  const A=[...Array(34)].map(()=>({x:rnd(),y:rnd(),v:6+14*rnd(),w:.5+rnd(),ph:rnd()*6.28,s:.6+1.3*rnd()}));
  const anim=()=>pp.getAnimations()[0];
  const draw=t=>{const k=Math.min(devicePixelRatio||1,2),W=hero.clientWidth,H=hero.clientHeight;
    if(cv.width!==Math.round(W*k)||cv.height!==Math.round(H*k)){cv.width=Math.round(W*k);cv.height=Math.round(H*k)}
    cx.setTransform(k,0,0,k,0,0);cx.clearRect(0,0,W,H);
    const hr=hero.getBoundingClientRect(),br=bandEl.getBoundingClientRect(),bx=br.left-hr.left,by=br.top-hr.top,
      bw=br.width,bh=br.height*.62;
    const amb=Math.min(1,Math.max(0,(t-S-D)/1.5));
    for(const a of A){const y=(a.y*H-t*a.v)%H,yy=y<0?y+H:y,x=a.x*W+Math.sin(t*a.w+a.ph)*8;
      cx.globalAlpha=amb*.35*(.5+.5*Math.sin(t*1.7+a.ph));cx.fillStyle='#F2C46A';cx.beginPath();cx.arc(x,yy,a.s,0,6.283);cx.fill()}
    for(const p of P){const age=t-p.tb;if(age<0)continue;const x0=bx+bw*ease((p.tb-S)/D)+p.dx,y0=by+bh*(.08+.84*p.yr);
      let x,y,al,sz=p.s;if(age<p.l){const f=age*(1-age/(2*p.l));x=x0+p.vx*f;y=y0+p.vy*f;al=Math.pow(1-age/p.l,1.2)*.9}
      else if(p.st){const f=p.l/2;x=x0+p.vx*f;y=y0+p.vy*f;al=.5;sz=p.s*.7}else continue;
      cx.globalAlpha=al;cx.fillStyle=p.c<.75?'#F2C46A':'#FFF0C8';cx.beginPath();cx.arc(x,y,sz,0,6.283);cx.fill()}
    cx.globalAlpha=1};
  const now=()=>{const a=anim();return a&&a.currentTime!=null?a.currentTime/1000:performance.now()/1000};
  let t0=null;const loop=ts=>{const a=anim();let t;if(a&&a.playState!=='finished')t=a.currentTime/1000;
    else{if(t0===null)t0=ts/1000-(S+D);t=ts/1000-t0}draw(t);if(!document.hidden)requestAnimationFrame(loop)};
  addEventListener('visibilitychange',()=>{if(!document.hidden)requestAnimationFrame(loop)});
  window.__paintDraw=()=>draw(now());requestAnimationFrame(loop)}catch(x){}})();
"""


def page(d):
    ext_, fmt = ("woff2", "woff2") if _has_brotli() else ("woff", "woff")
    faces = "".join(f'@font-face{{font-family:Poppins;src:url(fonts/{k}.{ext_}) format("{fmt}");font-weight:{w};'
                    f'font-style:{st};font-display:swap}}' for k, (_, w, st) in FONTS.items())
    start, dur = PAINT
    css = (CSS.replace("FONTFACES", faces).replace("PAINTDs", f"{dur:g}s").replace("PAINTSs", f"{start:g}s")
           .replace("PAINTENDs", f"{start + dur:g}s").replace("EASE", ",".join(f"{v:g}" for v in EASE)))
    js = JS.replace("__S__", f"{start:g}").replace("__D__", f"{dur:g}").replace("__E__", ",".join(f"{v:g}" for v in EASE))
    tel = f"tel:+{d['tel_e164']}"
    tiles = [("wa", d["wa"], "whatsapp", "WhatsApp", "Mesaj atın"),
             ("", f"https://instagram.com/{d['insta']}", "instagram", "Instagram", f"@{d['insta']}"),
             ("", d["google"], "star", "Google", stars()),
             ("wide", d["harita"], "pin", "Konum", d["konum"].replace(", ", " / ")),
             ("wide", d["web"], "globe", "Web sitesi", d["web_txt"])]
    tl = "".join(f'<a class="tile {c}" href="{e(h)}" style="--i:{k}"><span class="top">{icon(ic, 1.7, "i")}'
                 f'{icon("arrow", 1.8, "go")}</span><b>{e(t)}</b><small>{s if s.startswith("<") else e(s)}</small></a>'
                 for k, (c, h, ic, t, s) in enumerate(tiles))
    holder = (f'<div class="row"><span>Alıcı</span><b>{e(d["iban_alici"])}</b></div>' if d.get("iban_alici") else "")
    note = '<p class="note">Örnek IBAN: gerçek bilgiler eklenecek.</p>' if d.get("iban_ornek") else ""
    url = d["qr"]
    body = (
        f'<div class="wrap"><header class="hero"><div class="carbon"></div><canvas class="dust"></canvas>'
        f'<p class="kick"><i></i><span>{e(d["konum"].replace(", ", " · ").upper())}</span><i></i></p>'
        f'{t_svg("tlogo")}'
        f'<h1 class="paint">{band_svg(d["isim"])}<span class="gun">{gun_svg()}</span></h1>'
        f'<p class="svc"><i></i><b>{e(AT.SERVICE)}</b><i></i></p>'
        f'<p class="tag">Aracınızdaki hasarı ustalıkla onarıyoruz. Tek dokunuşla arayın, yazın.</p></header>'
        f'<a class="call" href="{tel}"><span><small>HEMEN ARA</small><b>{e(d["tel_txt"])}</b></span>'
        f'<i class="ph">{icon("phone", 1.9)}</i></a>'
        f'<nav class="tiles" aria-label="Bağlantılar">{tl}</nav>'
        f'<div class="sh rv"><i></i><h2>ÖDEME BİLGİLERİ</h2></div>'
        f'<section class="pay rv">{holder}<div class="iban" id="iban"><small>IBAN</small><b>{e(d["iban_txt"])}</b></div>'
        f'<div class="pbtn"><a class="btn gold" href="#iban" data-copy="{e(d["iban_raw"])}" data-msg="IBAN kopyalandı – '
        f'banka uygulamanıza yapıştırın">{icon("copy", 1.9)}Kopyala</a>'
        f'<a class="btn out" href="#karekod" data-toggle="karekod">{icon("qr", 1.9)}Karekod</a>'
        f'<div class="qrbox drop" id="karekod"><img src="{KAREKOD}" alt="IBAN karekodu" width="190" height="190">'
        f'<p>Karekodu kaydedin, banka uygulamanızda <b>Karekod ile Öde</b>, ardından <b>Galeriden seç</b>.</p>'
        f'<a class="dl" href="{KAREKOD}" download="auto-tufan-karekod.png">{icon("down", 1.9)}Karekodu kaydet</a>'
        f'</div></div>{note}</section>'
        f'<div class="acts rv"><a class="btn out" href="{VCF}" download>{icon("save", 1.9)}Rehbere ekle</a>'
        f'<a class="btn out" href="#paylas" data-toggle="paylas">{icon("share", 1.9)}Paylaş</a>'
        f'<div class="qrbox drop" id="paylas">{qr_svg(url, "Kartvizit QR kodu")}<p>Kodu kamerayla okutun ya da bağlantıyı gönderin.<br>'
        f'<b>{e(url.replace("https://", ""))}</b></p><div class="pbtn"><a class="btn out" href="{e(url)}" '
        f'data-copy="{e(url)}" data-msg="Bağlantı kopyalandı">{icon("copy", 1.9)}Kopyala</a>'
        f'<button class="btn gold" id="send" type="button" data-url="{e(url)}">{icon("share", 1.9)}Gönder</button>'
        f'</div></div></div>'
        f'<footer class="rv">{t_svg("ft")}<p>AUTO TUFAN</p><small>{e(tr_title(AT.SERVICE))} · '
        f'{e(d["konum"].replace(", ", " / "))} · @{e(d["insta"])}</small></footer></div>'
        f'<a class="fab" href="{tel}" aria-label="Hemen ara">{icon("phone", 2)}</a>'
        f'<div class="toast" role="status" aria-live="polite"></div>')
    title = f"{d['isim']} · {tr_title(AT.SERVICE)} · {d['konum']}"
    desc = f"{d['isim']} – hasar onarım, {d['konum']}. Hemen arayın, WhatsApp'tan yazın, Instagram, konum, ödeme."
    og = d["sayfa_url"].rstrip("/") + "/" + OG
    return (f'<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" '
            f'content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#131315">'
            f'<title>{e(title)}</title><meta name="description" content="{e(desc)}">'
            f'<meta property="og:type" content="website"><meta property="og:title" content="{e(title)}">'
            f'<meta property="og:description" content="{e(desc)}"><meta property="og:image" content="{e(og)}">'
            f'<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
            f'<meta name="twitter:card" content="summary_large_image">'
            f'<link rel="icon" href="{ICON_PNG}"><link rel="apple-touch-icon" href="{ICON_PNG}">'
            f'<link rel="preload" as="font" type="font/{fmt}" href="fonts/p8i.{ext_}" crossorigin>'
            f"<script>matchMedia('(prefers-reduced-motion: reduce)').matches||"
            f"document.documentElement.classList.add('mo')</script>"
            f'<style>{css}</style></head><body>{body}<script>{js}</script></body></html>')


# ---------------------------------------------------------------- önizlemeler

@contextlib.contextmanager
def served():
    """site/ yerel sunucuda (telefondaki gibi http)."""
    import functools
    import http.server
    import threading

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=OUT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{srv.server_port}/index.html"
    finally:
        srv.shutdown()


def screenshot(d, path=PREVIEW):
    """Telefon ekranında (390 × 844, son hâli): ilk ekran ve tüm sayfa (karekod ve paylaş kutuları açık).
    Kutucuk başlıkları aynı hizada mı da denetlenir.
    Kontroller: yazı tipleri yüklü, yatay taşma yok, yazılar sığıyor, iki QR okunuyor, sayfa hatası yok."""
    from playwright.sync_api import sync_playwright
    errors, shots = [], []
    fits = "[...document.querySelectorAll('SEL')].every(e=>e.offsetParent===null||e.scrollWidth<=e.clientWidth+1)"
    with sync_playwright() as p, served() as url:
        b = p.chromium.launch(executable_path=CHROMIUM)
        for full in (False, True):
            pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, reduced_motion="reduce")
            pg.add_init_script("navigator.share=async()=>{}")
            pg.on("pageerror", lambda x: errors.append(str(x)))
            pg.goto(url)
            pg.wait_for_timeout(600)
            pg.evaluate("Promise.all(['400','500','600','700','800','italic 800','italic 600'].map(w=>"
                        "document.fonts.load(w+' 20px Poppins')))")
            assert pg.evaluate("['400','500','600','700','800','italic 800'].every(w=>"
                               "document.fonts.check(w+' 20px Poppins'))"), "yazı tipi yüklenmedi"
            assert pg.evaluate("document.documentElement.scrollWidth") <= 390, "yatay taşma"
            assert pg.evaluate(fits.replace("SEL", ".call b,.tile b,.tile small,.svc b,.iban b,.sh h2,.btn")), \
                "yazı sığmadı"
            assert pg.evaluate("document.querySelector('.band').getBoundingClientRect().right") <= 390, "bant taştı"
            assert pg.evaluate("new Set([...document.querySelectorAll('.tiles .tile b')].map(b=>"
                               "Math.round(b.getBoundingClientRect().top-b.closest('.tile').getBoundingClientRect().top)"
                               ")).size") == 1, "kutucuk başlıkları hizasız"
            if full:
                pg.evaluate("document.querySelectorAll('.drop').forEach(x=>x.classList.add('on'))")
                pg.wait_for_timeout(300)
                img = Image.open(io.BytesIO(pg.locator("#karekod img").screenshot()))
                assert d["pay_qr"] in Q.decode(img), "karekod okunmadı"
                svg = Image.open(io.BytesIO(pg.locator("#paylas > svg").screenshot()))
                assert d["qr"] in Q.decode(svg), "paylaş QR'ı okunmadı"
            shots.append(Image.open(io.BytesIO(pg.screenshot(full_page=full))))
            pg.close()
        b.close()
    assert not errors, errors
    h = max(s.height for s in shots)
    canvas = Image.new("RGB", (sum(s.width for s in shots) + 120, h + 120), (52, 52, 56))
    x = 40
    for s in shots:
        canvas.paste(s, (x, 60))
        x += s.width + 40
    canvas.save(path)
    return path


def tour_gif(path=TOUR):
    """Tur (390 × 844), zamanda adım adım: açılış (boyama, zerrecikler, damlalar), aşağı kaydırma, karekod açılır."""
    from playwright.sync_api import sync_playwright
    frames, durs, errors = [], [], []
    with sync_playwright() as p, served() as url:
        b = p.chromium.launch(executable_path=CHROMIUM)
        pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
        pg.on("pageerror", lambda x: errors.append(str(x)))

        def shot(ms):
            frames.append(Image.open(io.BytesIO(pg.screenshot())).convert("RGB"))
            durs.append(ms)

        pg.goto(url)
        pg.wait_for_timeout(300)
        for k in range(0, 4600, 80):                          # boyama (1,0–2,4 sn) sık kare
            _seek(pg, k)
            pg.evaluate("window.__paintDraw&&__paintDraw()")
            shot(80)
        for k in range(4600, 7000, 300):
            _seek(pg, k)
            pg.evaluate("window.__paintDraw&&__paintDraw()")
            shot(300)
        pg.evaluate("document.getAnimations().forEach(a=>a.play())")
        h = pg.evaluate("document.documentElement.scrollHeight - innerHeight")
        for y in range(0, h + 1, 60):
            pg.evaluate(f"scrollTo(0,{y})")
            pg.wait_for_timeout(60)
            shot(70)
        pg.evaluate("scrollTo(0,0);document.querySelector('.pay').scrollIntoView({block:'center'})")
        pg.wait_for_timeout(500)
        pg.evaluate("document.getElementById('karekod').classList.add('on');"
                    "document.getElementById('karekod').scrollIntoView({block:'center'})")
        pg.wait_for_timeout(400)
        shot(2600)
        b.close()
    assert not errors, errors
    # ortak palet, dağıtmasız (dither'sız): GIF küçük kalır
    frames = [f.resize((312, 675), Image.LANCZOS) for f in frames]
    pal = frames[len(frames) // 3].quantize(colors=160, method=Image.Quantize.MEDIANCUT)
    out = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    out[0].save(path, save_all=True, append_images=out[1:], duration=durs, loop=0, optimize=True)
    return path


def standalone(doc, path=STANDALONE):
    """Denemelik tek dosya: yazı tipleri, karekod, simge ve rehber kartı sayfanın içine gömülü."""
    import base64

    def data(rel, mime):
        with open(os.path.join(OUT, rel), "rb") as f:
            return f"data:{mime};base64," + base64.b64encode(f.read()).decode()

    doc = re.sub(r'<link rel="preload"[^>]*>', "", doc)
    for rel in sorted(set(re.findall(r"fonts/p\d+i?\.woff2?", doc))):
        doc = doc.replace(f"url({rel})", f"url({data(rel, 'font/' + rel.rsplit('.', 1)[1])})")
    doc = doc.replace(f'href="{ICON_PNG}"', f'href="{data(ICON_PNG, "image/png")}"')
    doc = doc.replace(f'src="{KAREKOD}"', f'src="{data(KAREKOD, "image/png")}"')
    doc = doc.replace(f'href="{KAREKOD}"', f'href="{data(KAREKOD, "image/png")}"')
    doc = doc.replace(f'href="{VCF}" download', f'href="{data(VCF, "text/vcard")}" download="{VCF}"')
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    return path


def pack():
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for dp, _, files in os.walk(OUT):
            for fn in sorted(files):
                full = os.path.join(dp, fn)
                z.write(full, os.path.relpath(full, OUT))


def main():
    d = load()
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    doc = page(d)
    subset_fonts(html.unescape(doc))
    vcard(d)
    karekod_png(d)
    og_image(d)
    touch_icon()
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(doc)
    pack()
    standalone(doc)
    size = sum(os.path.getsize(os.path.join(dp, fn)) for dp, _, fs in os.walk(OUT) for fn in fs)
    print("sayfa:", os.path.relpath(os.path.join(OUT, "index.html"), A.ROOT), f"(toplam {size // 1024} KB) →",
          d["sayfa_url"])
    print("deneme:", os.path.relpath(STANDALONE, A.ROOT), f"({os.path.getsize(STANDALONE) // 1024} KB, tek dosya)")
    print("önizleme:", os.path.relpath(screenshot(d), A.ROOT))
    if "--hizli" not in sys.argv:
        print("tur:", os.path.relpath(tour_gif(), A.ROOT))


if __name__ == "__main__":
    main()
