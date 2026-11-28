"""SAVAŞ KANLIADA (otomotiv ve gayrimenkul danışmanlığı) kurumsal anahtarlık önerileri: 9 sade, kart biçimli model,
her biri üç renkte (antrasit, kırmızı, beyaz gövde); en çok 50 × 50 mm. GALERİ IŞIK kataloğunun yapısı (ön ve arka
yüz, müşteri sayfaları ve PDF).

Logo müşterinin görselinden (scripts/savas_kanliada_logo.py): kırmızı S ve K, üstte gümüş (burada beyaz) çatı ve
pencere. Çatı ile harfler arasında logodaki gibi gövde renginde boşluk (≥ 0,7 mm: 0,4 nozul ayırır). Küçük boyda dört
pencere camı tek kare + artı çizgiye sadeleşir (camlar ≥ 0,9 mm). Ad Poppins ExtraBold (logodaki kalın yazıya en
yakın). Antrasit gövdede S, K ve ad kırmızı, çatı beyaz; kırmızı gövdede S, K ve ad beyaz, çatı antrasit; beyaz
gövdede S, K ve ad kırmızı, çatı, çerçeve ve telefon antrasit.
Arka yüz: telefon 0506 101 68 97 ve logodaki alt satır (OTOMOTİV & / GAYRİMENKUL; tek satıra 3 mm'de sığmıyor).
QR'lı model yok (müşteri istemedi).

Baskı kontrolleri GALERİ IŞIK'takilerle aynı (galeri_isik_anahtarlik.check).
Çıktı : anahtarlik/savas_kanliada/<nn>_<model>_<renk>.png, hepsi.png, musteri_1.png, musteri_2.png,
        musteri_katalog.pdf, logo.png
Kullanım: python3 scripts/savas_kanliada_logo.py (bir kez); python3 scripts/savas_kanliada_anahtarlik.py [anahtar ...]
"""
import os
import sys

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import anahtarlik_konsept as K  # noqa: E402
import galeri_isik_anahtarlik as G  # noqa: E402
import savas_kanliada_logo as L  # noqa: E402
import uzar_anahtarlik as U  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "anahtarlik", "savas_kanliada")
PHONE = "0506 101 68 97"
NAME = "SAVAŞ KANLIADA"
ANT = (84, 87, 92)                                 # antrasit (koyu gri) gövde
RED = (232, 16, 26)                                # canlı kırmızı (Elas PLA kırmızısına yakın)
WHITE = (255, 255, 253)                            # saf beyaz (açık gri değil)
K.FILAMENT.update({ANT: "antrasit – PLA Basic Dark Gray", WHITE: "beyaz – PLA Basic White",
                   RED: "kırmızı – Elas PLA Kırmızı"})
J = m3.JoinType.Round
_render = K.render


def duz_render(parts, size, R, **kw):
    """Ön ve arka görünüş düz ışıkla: kameraya bakan yüzler tam parlaklıkta (beyaz gri görünmesin), kenarlar biraz
    koyu. Perspektif ve QR okuma çağrıları değişmez."""
    if "light" not in kw and "flat" not in kw and any(np.allclose(R, K.rotation(*a)) for a in ((0, 0), (180, 180))):
        kw["flat"] = 0.72
    return _render(parts, size, R, **kw)


K.render = G.render = duz_render
HOLE_R = G.HOLE_R

DARK = dict(k=RED, b=WHITE, ad=RED, alt=WHITE)     # antrasit gövde
LIGHT = dict(k=RED, b=ANT, ad=RED, alt=ANT)        # beyaz gövde
ON_RED = dict(k=WHITE, b=ANT, ad=WHITE, alt=ANT)   # kırmızı gövde


# ---------------------------------------------------------------- logo

def sk_mark(H, cx=0.0, cy=0.0, pal=DARK):
    """SK + çatı işareti, yükseklik H mm, (cx, cy) dış sınırların ortası. Döner [(harfler), (çatı + pencere)]."""
    k = m3.CrossSection(L.polygons("kirmizi"), m3.FillRule.EvenOdd).scale((H, H))
    b = m3.CrossSection(L.polygons("beyaz"), m3.FillRule.EvenOdd).scale((H, H))
    r = min(0.4, 0.012 * H)
    k = k.offset(-r, J).offset(r, J)
    parts = sorted(b.decompose(), key=lambda p: -p.area())
    roof = parts[0].offset(-r, J).offset(r, J)
    win = A.union(*parts[1:]) if len(parts) > 1 else A.empty()
    if not win.is_empty():                         # pencere: küçükte tek kare + artı (camlar basılabilir)
        wb = win.bounds()
        s = max(wb[2] - wb[0], wb[3] - wb[1])
        wx, wy = (wb[0] + wb[2]) / 2, (wb[1] + wb[3]) / 2
        g = max(0.6, 0.18 * s)
        s = max(s, 2 * 0.9 + g)
        win = A.rect(wx - s / 2, wy - s / 2, wx + s / 2, wy + s / 2) - A.rect(wx - g / 2, wy - s, wx + g / 2, wy + s) \
            - A.rect(wx - s, wy - g / 2, wx + s, wy + g / 2)
    beyaz = roof + win
    k = k - beyaz.offset(max(0.7, 0.02 * H), J)       # çatı ile harfler arası gövde rengi
    k = k.offset(-0.31, J).offset(0.31, J)             # kesimden kalan 0,6 mm'den ince uçlar basılamaz: atılır
    bb = (k + beyaz).bounds()
    dx, dy = cx - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2
    return [(k.translate((dx, dy)), pal["k"]), (beyaz.translate((dx, dy)), pal["b"])]


def font_ad():
    return A.Font("Poppins-ExtraBold.ttf")


def font_alt():
    return A.Font("Poppins-Bold.ttf")


def kalin(cs, cap):
    """Poppins ExtraBold küçük boyda (Ş çengeli, A tepesi) 0,6 mm'nin altına iner: hafif kalınlaştırılır."""
    return cs.offset(float(np.clip(0.34 - 0.045 * cap, 0.0, 0.2)), J)


def ad(s, cap, x=0.0, y=0.0, align="c", valign="m", tracking=None):
    tr = cap * 0.09 if tracking is None else tracking
    return kalin(font_ad().text(s, cap, x, y, align=align, valign=valign, tracking=tr), cap)


def ad_sigdir(s, cap, w, x=0.0, y=0.0, align="c", tracking=None):
    f = font_ad()
    tr = cap * 0.09 if tracking is None else tracking
    c = f.fit_cap(s, cap, w, tr)
    return kalin(f.text(s, c, x, y, align=align, valign="m", tracking=tr), c), c


def small(text, cap, x, y, align="c", tracking=0.3, max_w=None):
    return G.small(text, cap, x, y, align, tracking, max_w)


def stack(R, pal=DARK, iki=False):
    """İşaret üstte (yükseklik 2R), altında SAVAŞ KANLIADA (tek satır, işaretin 1,5 katı genişliğe kadar) ya da iki
    satır SAVAŞ / KANLIADA."""
    items = sk_mark(2 * R, 0, 0, pal)
    b = G.bounds(items)
    w = (b[2] - b[0]) * (1.25 if iki else 2.1)
    gap = max(0.12 * R, 1.0)
    if not iki:
        _, c = ad_sigdir(NAME, 0.4 * R, w)
        iki = c < 3.4                                       # tek satır çok küçük kalıyorsa iki satır
        w = (b[2] - b[0]) * (1.25 if iki else 2.1)
    if iki:
        a1, c1 = ad_sigdir("SAVAŞ", 0.42 * R, w)
        a2, _ = ad_sigdir("KANLIADA", c1, w)
        y1 = b[1] - gap - c1 / 2
        items += [(a1.translate((0, y1)), pal["ad"]), (a2.translate((0, y1 - c1 * 1.75)), pal["ad"])]
    else:
        a, c = ad_sigdir(NAME, 0.4 * R, w)
        items += [(a.translate((0, b[1] - gap - c / 2)), pal["ad"])]
    return items


def line(R, pal=DARK):
    """Yan yana: işaret solda (yükseklik 2R), sağında iki satır SAVAŞ / KANLIADA."""
    items = sk_mark(2 * R, 0, 0, pal)
    b = G.bounds(items)
    cap = 0.56 * R
    x0 = b[2] + max(0.18 * R, 1.2)
    a1 = ad("SAVAŞ", cap, x0, 0.5 * R, align="l")
    a2 = ad("KANLIADA", cap, x0, -0.5 * R, align="l")
    return items + [(a1, pal["ad"]), (a2, pal["ad"])]


def logo_sheet(path):
    W, H = 1500, 640
    canvas = Image.new("RGB", (W, H), (244, 245, 247))
    dr = ImageDraw.Draw(canvas)
    dr.text((40, 26), "LOGO", fill=(24, 26, 30), font=K.fnt(34))
    dr.text((40, 72), "Solda firmanın logosu, sağda anahtarlıklar için çizilen hâli (baskıya uygun kalınlık ve aralıklar).",
            fill=(96, 100, 110), font=K.fnt(20))
    src = Image.open(os.path.join(OUT_DIR, "kaynak_logo.png")).convert("RGBA")
    src = A.fit_into(src, 460, 460)
    canvas.paste(src, (40 + (460 - src.width) // 2, 130 + (460 - src.height) // 2), src)
    for k, (fn, bg) in enumerate(((lambda: stack(10.0), ANT), (lambda: line(8.0), ANT),
                                  (lambda: stack(10.0, LIGHT), (250, 250, 248)))):
        im = A.fit_into(G.paint(fn(), bg, 10.0, pad=3).convert("RGBA"), 290, 420)
        x0 = 540 + k * 315
        dr.rounded_rectangle((x0, 130, x0 + 295, 590), 24, fill=bg)
        canvas.paste(im, (x0 + 147 - im.width // 2, 360 - im.height // 2))
    canvas.save(path)


# ---------------------------------------------------------------- arka yüz

def phone_lines(cx, top, w, cap=4.4, min_cap=3.2, lead=1.7):
    f = G.outfit()
    c1 = f.fit_cap(PHONE, cap, w, 0.3)
    if c1 >= min_cap:
        return small(PHONE, c1, cx, top - c1 / 2), top - c1
    c2 = min(cap, f.fit_cap("0506 101", cap, w, 0.3))
    return (small("0506 101", c2, cx, top - c2 / 2) + small("68 97", c2, cx, top - c2 * 1.5 - lead),
            top - 2 * c2 - lead)


def rule(x0, x1, y, t=0.8):
    """Ortasında küçük çatı (^) olan ince çizgi."""
    cx = (x0 + x1) / 2
    roof = A.stroke([(cx - 2.2, y - 0.2), (cx, y + 1.7), (cx + 2.2, y - 0.2)], 1.0)
    return A.rect(x0, y - t / 2, cx - 3.0, y + t / 2) + A.rect(cx + 3.0, y - t / 2, x1, y + t / 2) + roof





def card(key, title, desc, outline, hole_xy, body=ANT, holes=None):
    return K.Concept(key, title, desc, outline, holes if holes is not None else A.circle(HOLE_R, *hole_xy), body)


rounded, with_lug, fit, place = G.rounded, G.with_lug, G.fit, G.place




# ---------------------------------------------------------------- 10 model × 2 renk

V = {
    "ant": dict(body=ANT, pal=DARK, acc=RED, txt=WHITE, cizgi=WHITE, ad="antrasit", dosya="antrasit"),
    "red": dict(body=RED, pal=ON_RED, acc=ANT, txt=WHITE, cizgi=WHITE, ad="kırmızı", dosya="kirmizi"),
    "wht": dict(body=WHITE, pal=LIGHT, acc=RED, txt=ANT, cizgi=ANT, ad="beyaz", dosya="beyaz"),
}
TAG = ("OTOMOTİV &", "GAYRİMENKUL")                    # logodaki alt satır (tek satıra 3 mm'de sığmıyor)


def tagline(cx, y, w, cap=3.2):
    """OTOMOTİV & / GAYRİMENKUL, iki satır; y üst satırın ortası. Döner (şekil, alt kenar)."""
    f = G.outfit()
    c = min(cap, f.fit_cap(TAG[1], cap, w, 0.35))
    cs = small(TAG[0], c, cx, y, tracking=0.35) + small(TAG[1], c, cx, y - c - 1.7, tracking=0.35)
    return cs.offset(0.12, J), y - 1.5 * c - 1.7


def arka(c, v, cx, cy, w, tag=True, phone_cap=4.4):
    """Arka yüz (arka yüz görünümünün koordinatlarında): telefon, ortasında çatı olan çizgi, OTOMOTİV & GAYRİMENKUL.
    Blok dikeyde cy'ye ortalanır."""
    v = V[v]
    ph, bot = phone_lines(cx, 0.0, w, phone_cap)
    ry = bot - 3.0
    parts = [(ph, v["txt"]), (rule(cx - min(w, 30) / 2, cx + min(w, 30) / 2, ry), v["acc"])]
    low = ry - 0.9
    if tag:
        t, low = tagline(cx, ry - 4.4, w)
        parts.append((t, v["acc"]))
    dy = cy - low / 2
    c.back += [(cs.translate((0, dy)), col) for cs, col in parts]


def kart_logo(box, pal, cap_max=4.6, gap=1.6):
    """Kartlar için: SAVAŞ KANLIADA tek satır, kutunun tam genişliğinde (okunaklı), üstünde kalan yüksekliği dolduran
    işaret."""
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2
    a, cap = ad_sigdir(NAME, cap_max, x1 - x0, cx, 0.0)
    a = a.translate((0, y0 + 0.9 - a.bounds()[1]))             # Ş çengeli dahil alt kenar kutuda
    top = a.bounds()[3] + gap
    items = sk_mark(y1 - top, cx, (y1 + top) / 2, pal)
    return items + [(a, pal["ad"])]


def model(n, fn, v):
    def make():
        c = fn(v)
        c.key = f"{n:02d}_{c.key}_{V[v]['dosya']}"
        c.title = f"{c.title} · {V[v]['ad']}"
        return c
    return make


def m01(v):
    W, H = 50.0, 30.0
    c = card("klasik_kart", "Klasik kart", "Yatay kart; ortada logo, altında SAVAŞ KANLIADA. Arkada telefon ve "
             "OTOMOTİV & GAYRİMENKUL.", A.rrect(W, H, 4.0), (-W / 2 + 5.5, H / 2 - 5.5), body=V[v]["body"])
    c.front += kart_logo((-W / 2 + 3.6, -H / 2 + 2.2, W / 2 - 3.6, H / 2 - 2.2), V[v]["pal"])
    arka(c, v, 0.0, -2.6, 38.0)
    return c


def m02(v):
    W, H = 50.0, 26.0
    c = card("yatay_logo", "Yatay logo", "İnce yatay kart; solda delik, logo ve iki satır ad yan yana.",
             A.rrect(W, H, 4.0), (-W / 2 + 5.5, 0.0), body=V[v]["body"])
    c.front += fit(lambda R: line(R, V[v]["pal"]), (-W / 2 + 10.4, -H / 2 + 2.4, W / 2 - 2.8, H / 2 - 2.4))[0]
    arka(c, v, -3.0, 0.4, 36.0, tag=False, phone_cap=4.6)
    return c


def m03(v):
    W, H = 50.0, 30.0
    shape = A.rrect(W, H, 4.0)
    hole = (W / 2 - 5.4, H / 2 - 5.4)
    c = card("cerceveli_kart", "Çerçeveli kart", "Yatay kart; iki yüzde de ince beyaz çerçeve, ortada logo ve ad.",
             shape, hole, body=V[v]["body"])
    frame = A.outline(shape, 0.9, inset=1.8)
    c.front += [(frame - A.circle(HOLE_R + 3.2, *hole), V[v]["cizgi"])]
    c.front += kart_logo((-W / 2 + 4.6, -H / 2 + 3.4, W / 2 - 4.6, H / 2 - 3.4), V[v]["pal"], cap_max=4.2)
    c.back += [(frame - A.circle(HOLE_R + 3.2, -hole[0], hole[1]), V[v]["cizgi"])]
    arka(c, v, 0.0, -1.6, 36.0)
    return c


def m04(v):
    W, H = 50.0, 32.0
    c = card("seritli_kart", "Şeritli kart", "Yatay kart; logo ve ad üstte, altta renkli şerit içinde telefon numarası.",
             A.rrect(W, H, 4.0), (W / 2 - 5.5, H / 2 - 5.5), body=V[v]["body"])
    by = -H / 2 + 1.4 + 4.2
    band = A.rrect(W - 2.8, 8.4, 2.6, 0.0, by)
    ph = small(PHONE, 4.0, 0.0, by, tracking=0.6, max_w=W - 10)
    kalan = band - ph                                   # Outfit'in 5'indeki dar çentik şeritte 0,6 mm'den ince kalır:
    ince = kalan - kalan.offset(-0.31, J).offset(0.31, J)   # o çentik yazı rengiyle doldurulur
    ph = A.union(ph, *[q for q in ince.decompose() if q.area() > 0.2]).offset(0.02, J)
    c.front += [(band, V[v]["acc"]), (ph, WHITE)]
    c.front += kart_logo((-W / 2 + 3.6, by + 4.6, W / 2 - 3.6, H / 2 - 2.0), V[v]["pal"])
    arka(c, v, 0.0, -2.0, 38.0)
    return c


def m05(v):
    W, H = 50.0, 28.0
    hole = (-W / 2 + 6.9, H / 2 - 6.6)
    c = card("yan_seritli_kart", "Yan şeritli kart", "Yatay kart; solda delikli renkli şerit, sağda logo ve ad.", A.rrect(W, H, 4.0), hole, body=V[v]["body"])
    band = A.rrect(11.0, H - 2.8, 2.6, -W / 2 + 6.9, 0.0) - A.circle(HOLE_R + 1.4, *hole)
    c.front += [(band, V[v]["acc"])]
    c.front += kart_logo((-W / 2 + 14.4, -H / 2 + 2.2, W / 2 - 2.6, H / 2 - 2.2), V[v]["pal"], cap_max=4.2)
    arka(c, v, -4.0, 0.0, 36.0)
    return c


def m06(v):
    W, H = 50.0, 30.0
    shape = rounded(A.polygon([(-W / 2, -H / 2), (W / 2, -H / 2), (W / 2, H / 2 - 9), (W / 2 - 9, H / 2),
                               (-W / 2, H / 2)]), 3.0)
    c = card("cati_kart", "Çatı kart", "Sağ üst köşesi çatı eğiminde kesik kart; kesiğe paralel beyaz çizgi, logo ve "
             "iki satır ad.", shape, (-W / 2 + 5.5, H / 2 - 5.5), body=V[v]["body"])
    c.front += [(A.polygon([(W / 2 - 1.4, H / 2 - 12.6), (W / 2 - 1.4, H / 2 - 10.8), (W / 2 - 10.8, H / 2 - 1.4),
                            (W / 2 - 12.6, H / 2 - 1.4)]), V[v]["cizgi"])]
    c.front += fit(lambda R: line(R, V[v]["pal"]), (-W / 2 + 3.4, -H / 2 + 3.0, W / 2 - 8.0, H / 2 - 10.0))[0]
    arka(c, v, 1.0, -1.4, 30.0)
    return c


def m07(v):
    W, H = 30.0, 48.0
    c = card("dikey_kart", "Dikey kart", "Dikey kart; üstte delik, logo ve iki satır ad. Arkada telefon ve küçük logo.",
             A.rrect(W, H, 4.0), (0.0, H / 2 - 5.6), body=V[v]["body"])
    c.front += fit(lambda R: stack(R, V[v]["pal"], iki=True), (-W / 2 + 3.4, -H / 2 + 3.4, W / 2 - 3.4, H / 2 - 11.2))[0]
    ph, bot = phone_lines(0.0, H / 2 - 12.0, W - 6.0, 4.4)
    c.back += [(ph, V[v]["txt"]), (rule(-9.0, 9.0, bot - 3.0), V[v]["acc"])]
    c.back += place(sk_mark(12.0, pal=V[v]["pal"]), 0.0, bot - 13.0)
    return c


def m08(v):
    W, H = 32.0, 48.0
    tag = A.rrect(W, H, 7.0)
    hole = (0, H / 2 - 6.4)
    c = card("kunye", "Künye", "Künye biçimi; iki yüzde de ince beyaz çerçeve, logo ve iki satır ad. Arkada telefon.",
             tag, hole, body=V[v]["body"])
    frame = A.outline(tag, 0.9, inset=1.7) - A.circle(HOLE_R + 3.4, *hole)
    c.front += [(frame, V[v]["cizgi"])]
    c.front += fit(lambda R: stack(R, V[v]["pal"], iki=True), (-W / 2 + 4.4, -H / 2 + 4.0, W / 2 - 4.4, H / 2 - 12.4))[0]
    ph, bot = phone_lines(0.0, H / 2 - 13.0, W - 8.0, 4.4)
    c.back += [(frame, V[v]["cizgi"]), (ph, V[v]["txt"]), (rule(-9.0, 9.0, bot - 3.0), V[v]["acc"])]
    c.back += place(sk_mark(11.0, pal=V[v]["pal"]), 0.0, bot - 12.6)
    return c


def m09(v):
    S = 44.0
    c = card("kare_kart", "Kare kart", "Kare kart; önde büyük logo ve ad, arkada telefon ve OTOMOTİV & GAYRİMENKUL.",
             A.rrect(S, S, 6.0), (S / 2 - 6.0, S / 2 - 6.0), body=V[v]["body"])
    c.front += kart_logo((-S / 2 + 3.4, -S / 2 + 3.4, S / 2 - 3.4, S / 2 - 9.6), V[v]["pal"])
    arka(c, v, 0.0, -2.0, S - 8.0)
    return c


MODELS = [m01, m02, m03, m04, m05, m06, m07, m08, m09]
RENKLER = ("ant", "red", "wht")
CONCEPTS = [model(len(RENKLER) * k + j + 1, fn, v) for k, fn in enumerate(MODELS) for j, v in enumerate(RENKLER)]


# ---------------------------------------------------------------- sayfalar

def header(dr, im, W, title, sub):
    dr.rectangle((0, 0, W, 260), fill=(50, 53, 58))
    for x in range(W - 560, W + 200, 52):                     # çatı eğiminde ince çizgiler
        dr.polygon([(x, 260), (x + 14, 260), (x + 14 + 150, 110), (x + 150, 110)], fill=(60, 63, 69))
    logo = A.fit_into(G.paint(line(10.0), (50, 53, 58), 14.0, pad=1.0).convert("RGBA"), 760, 130)
    im.paste(logo, (70, 36))
    dr.text((72, 186), title, font=K.fnt(34), fill=(240, 240, 238))
    dr.text((72 + dr.textlength(title, font=K.fnt(34)) + 20, 194), sub, font=K.fnt(24), fill=RED)
    dr.rectangle((0, 256, W, 262), fill=RED)


def customer_pages(concepts, per_page=10, start_page=1, total=None):
    total = total or len(CONCEPTS)
    G.header = header                                         # G.customer_pages sayfa başlığını bundan çizer
    G.ORANGE = RED
    G.OUT_DIR = OUT_DIR
    paths = G.customer_pages(concepts, per_page, start_page, total, kart_bg=(232, 234, 238))   # beyaz gövde seçilsin
    for p in paths:                                           # alt bilgi satırı bu firmaya göre
        im = Image.open(p)
        dr = ImageDraw.Draw(im)
        dr.rectangle((60, 284, 1640, 330), fill=(244, 244, 242))
        dr.text((70, 290), "Her model üç renkte: antrasit, kırmızı ve beyaz gövde · en çok 50 × 50 mm · arka yüzde "
                           "telefon numarası", font=K.fnt(24), fill=(40, 40, 44))
        im.save(p, optimize=True)
    return paths


def build(i):
    c = CONCEPTS[i - 1]()
    c.front, c.back = U.resolve(c.front), U.resolve(c.back)
    issues, wall = G.check(c)
    G.sheet(c, os.path.join(OUT_DIR, c.key + ".png"), i)
    w, h = c.size()
    return (f"{c.key:22s} {w:4.1f} × {h:4.1f} mm  renk {len(c.colours())}  delik eti {wall}  "
            f"{'; '.join(issues) or 'kontroller tamam'}",
            bool(issues))


def build_pages(args):
    kind, items = args
    concepts = []
    for i in items:
        c = CONCEPTS[i - 1]()
        c.front, c.back = U.resolve(c.front), U.resolve(c.back)
        concepts.append((i, c))
    if kind == "genel":
        U.overview([c for _, c in concepts], os.path.join(OUT_DIR, "hepsi.png"),
                   title="SAVAŞ KANLIADA – ANAHTARLIK ÖNERİLERİ (9 model × antrasit, kırmızı, beyaz)")
        return [os.path.join(OUT_DIR, "hepsi.png")]
    return customer_pages(concepts, start_page=kind)


def main():
    from multiprocessing import Pool
    os.makedirs(OUT_DIR, exist_ok=True)
    only = sys.argv[1:]
    if only == ["logo"]:
        logo_sheet(os.path.join(OUT_DIR, "logo.png"))
        return
    todo = [i for i, fn in enumerate(CONCEPTS, 1) if not only or any(o in fn().key for o in only)]
    with Pool(3) as pool:
        rows = pool.map(build, todo)
        for ln, _ in rows:
            print(ln)
        bad = sum(b for _, b in rows)
        if not only:
            logo_sheet(os.path.join(OUT_DIR, "logo.png"))
            for eski in os.listdir(OUT_DIR):
                if eski.startswith("musteri_") and eski.endswith(".png"):
                    os.remove(os.path.join(OUT_DIR, eski))
            jobs = [("genel", todo)] + [(k // 10 + 1, todo[k:k + 10]) for k in range(0, len(todo), 10)]
            pages = pool.map(build_pages, jobs)
            pdf = [Image.open(p).convert("RGB") for ps in pages[1:] for p in ps]
            pdf[0].save(os.path.join(OUT_DIR, "musteri_katalog.pdf"), save_all=True, append_images=pdf[1:],
                        resolution=200)
    print("sorunlu:", bad)


if __name__ == "__main__":
    main()
