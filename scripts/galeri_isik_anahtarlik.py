"""GALERİ IŞIK (Kepez / Antalya, oto galeri) kurumsal anahtarlık önerileri – siyah, turuncu, beyaz; en çok 50 × 50 mm.

20 görsel öneri (yalnız görsel; seçilen sonra Bambu Lab X2D dosyasına çevrilir). Hepsinde firmanın logosu:
  * G işareti: kalın turuncu C, ortada yatay kol, sağdan geçen beyaz eğik çizgi (logodaki gibi taşan alt uç)
  * yazı: geniş, geometrik Michroma (logodaki harflere en yakın; 0,4 nozul için harf çizgileri kalınlaştırılır)
  * İ'nin noktası turuncu elmas; Ş'nin alt çizgisinde beyaz elmas (logodaki gibi)
  * GALERİ beyaz, IŞIK turuncu
Logo kilitleri: "yan yana" (logonun kendisi: G + ALERİ + IŞIK), "iki satır" (G + ALERİ, altında ALERİ genişliğinde
IŞIK) ve yalnız G işareti. Arka yüz: telefon 0546 807 07 00 ve ANTALYA; QR'lılarda (3, 16, 19) telefon QR'ı
(TEL:+905468070700, sürüm 1, 21 × 21, hata düzeltme M); her QR arka yüz görüntüsünden okunarak doğrulanır.

Baskı kontrolleri (her tasarımda): yazı ve süsler kenardan ≥ 1 mm, delikten ≥ 0,8 mm içeride (kırpılan öğe yok); delik
çevresinde ≥ 3 mm et; en ince çizgi ≥ 0,6 mm; farklı öğeler arası ≥ 0,6 mm.

Çıktı : anahtarlik/galeri_isik/<nn>_<ad>.png (ön, arka, perspektif), hepsi.png, musteri_1.png, musteri_2.png,
        musteri_katalog.pdf, logo.png (logo kilitleri, asıl logoyla karşılaştırma)

Kullanım:
  pip install segno zxing-cpp
  python3 scripts/galeri_isik_anahtarlik.py [anahtar ...]
"""
import math
import os
import sys

import manifold3d as m3
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import anahtarlik_konsept as K  # noqa: E402
import uzar_anahtarlik as U  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "anahtarlik", "galeri_isik")
PHONE, CITY = "0546 807 07 00", "ANTALYA"
QR_TEXT = "TEL:+905468070700"
BLACK, WHITE = K.BLACK, K.WHITE
ORANGE = (235, 93, 31)                          # logodaki turuncu (#EB5D1F)
K.FILAMENT.update({BLACK: "siyah – PLA Matte Charcoal", WHITE: "beyaz – PLA Basic White",
                   ORANGE: "turuncu – PLA Basic Orange"})
J = m3.JoinType.Round
HOLE_R = 2.2                                    # Ø4,4 delik (çelik halka)
SLOPE = 0.62                                    # logodaki eğik çizginin eğimi (x / y)

# renk düzenleri: G, eğik çizgi, GALERİ, IŞIK (İ noktası IŞIK renginde, Ş elması GALERİ renginde)
DARK = dict(g=ORANGE, slash=WHITE, galeri=WHITE, isik=ORANGE)
LIGHT = dict(g=ORANGE, slash=BLACK, galeri=BLACK, isik=ORANGE)
ON_ORANGE = dict(g=BLACK, slash=WHITE, galeri=WHITE, isik=BLACK)


# ---------------------------------------------------------------- logo

def michroma():
    return A.Font("Michroma-Regular.ttf")


def outfit():
    return A.Font("Outfit-ExtraBold.ttf")


def g_mark(H, cx=0.0, cy=0.0, pal=DARK):
    """G işareti: H = C'nin dış çapı; (cx, cy) C'nin merkezi. Döner [(turuncu G, renk), (eğik çizgi, renk)].
    Ölçüler logodan: halka kalınlığı 0,33 R, yatay kol 0,26 R, eğik çizgi 0,31 R geniş, C'nin altından 0,15 R taşar."""
    R = H / 2
    gap = max(0.035 * H, 0.75) * math.hypot(1, SLOPE)   # turuncu ile beyaz arası (dik ölçüde ≥ 0,75 mm)
    yt, yb, w = 0.16 * R, -1.15 * R, 0.31 * R       # eğik çizginin üstü, altı, genişliği

    def sl(y):                                      # eğik çizginin sol kenarı
        return 0.85 * R + SLOPE * (y - yt)

    ring = A.circle(R, 0, 0, 160) - A.circle(R - 0.33 * R, 0, 0, 160)
    bar = A.rect(0.03 * R, -0.16 * R, 2 * R, 0.10 * R)
    top_cut = A.polygon([(0.82 * R + SLOPE * (0.10 * R - 0.69 * R), 0.10 * R), (3 * R, 0.10 * R), (3 * R, 2 * R),
                         (0.82 * R + SLOPE * (2 * R - 0.69 * R), 2 * R)])
    slash_cut = A.polygon([(sl(-2 * R) - gap, -2 * R), (3 * R, -2 * R), (3 * R, 2 * R), (sl(2 * R) - gap, 2 * R)])
    g = ((ring + bar) - top_cut - slash_cut).offset(-0.3, J).offset(0.3, J)    # sivri uçlar 0,6 mm'ye yuvarlanır
    slash = A.polygon([(sl(yb), yb), (sl(yb) + w, yb), (sl(yt) + w, yt), (sl(yt), yt)]).offset(-0.3, J).offset(0.3, J)
    return [(g.translate((cx, cy)), pal["g"]), (slash.translate((cx, cy)), pal["slash"])]


def diamond(cx, cy, r):
    """Elmas (köşeleri 0,3 mm yuvarlatılmış: uçları 0,4 nozulla basılır)."""
    return A.polygon([(cx, cy + r), (cx + r, cy), (cx, cy - r), (cx - r, cy)]).offset(-0.3, J).offset(0.3, J)


def embolden(cap):
    """Michroma'nın çizgisi büyük harf yüksekliğinin %12,5'i; 0,4 nozul için ≥ ~0,75 mm'ye kalınlaştırılır."""
    return float(np.clip(max(0.03 * cap, (0.78 - 0.125 * cap) / 2), 0.04, 0.22))


def word(s, cap, x=0.0, y=0.0, align="l", valign="b", tracking=None):
    """Logo yazısı (Michroma, kalınlaştırılmış). İ: noktasız I + üstünde elmas; Ş: S'nin alt çizgisinde elmas.
    Döner (harfler, elmaslar). (x, y): align'a göre sol / orta / sağ, valign 'b' taban çizgisi, 'm' harf ortası."""
    f = michroma()
    tr = cap * 0.12 if tracking is None else tracking
    plain = s.replace("İ", "I").replace("Ş", "S")
    glyphs, _ = f.layout(plain, cap, tr)
    assert len(glyphs) == len(plain)
    d = embolden(cap)
    letters = f.text(plain, cap, 0, 0, align="l", valign="b", tracking=tr).offset(d, J)
    stroke = 0.125 * cap + 2 * d
    r = 0.95 * stroke                               # elmasın yarı köşegeni
    marks, cuts = [], []
    for ch, (_, gx, _, _) in zip(s, glyphs):
        if ch not in "İŞ":
            continue
        gb = f.text("I" if ch == "İ" else "S", cap, 0, 0, align="l", valign="b").bounds()
        cx = gx + (gb[0] + gb[2]) / 2
        if ch == "İ":
            marks.append(diamond(cx, cap + d + max(0.65, 0.5 * stroke) + r, r))
        else:
            g = max(0.6, 0.45 * stroke)
            cuts.append(A.rect(cx - r - g, -d - 0.1 * cap - 0.5, cx + r + g, stroke - d + 0.35))
            marks.append(diamond(cx, stroke / 2 - d - 0.05 * cap, r))
    if cuts:
        letters = letters - A.union(*cuts)
    marks = A.union(*marks)
    b = letters.bounds()
    dx = {"l": x - b[0], "c": x - (b[0] + b[2]) / 2, "r": x - b[2]}[align]
    dy = y - (cap / 2 if valign == "m" else 0.0)
    return letters.translate((dx, dy)), marks.translate((dx, dy))


def galeri_isik_word(cap, x, y, pal=DARK, align="l", valign="b", sep=None):
    """GALERİ IŞIK tek satır, G harfiyle (yay ve dar yerler için; G işaretsiz)."""
    a, am = word("GALERİ", cap, 0, 0)
    b, bm = word("IŞIK", cap, a.bounds()[2] + (cap * 0.75 if sep is None else sep), 0)
    items = [(a, pal["galeri"]), (am, pal["isik"]), (b, pal["isik"]), (bm, pal["galeri"])]
    return place(items, x, y, align, valign, ref_cap=cap)


def lockup_line(R, pal=DARK):
    """Logonun kendisi: G işareti + ALERİ + IŞIK. Harfler 0,88 R, taban çizgisi C'nin altından 0,21 R yukarıda."""
    cap, base = 0.88 * R, -0.79 * R
    items = g_mark(2 * R, 0, 0, pal)
    x0 = 0.85 * R + SLOPE * (base - 0.16 * R) + 0.31 * R + max(0.14 * R, 1.0)
    a, am = word("ALERİ", cap, x0, base)
    b, bm = word("IŞIK", cap, a.bounds()[2] + 0.62 * cap, base)
    return items + [(a, pal["galeri"]), (am, pal["isik"]), (b, pal["isik"]), (bm, pal["galeri"])]


def lockup_stack(R, pal=DARK, isik_scale=None, gap=None):
    """İki satır: G işareti + ALERİ, altında IŞIK (ALERİ'nin solundan başlar, varsayılan: ALERİ genişliğinde)."""
    cap, base = 0.88 * R, -0.79 * R
    items = g_mark(2 * R, 0, 0, pal)
    x0 = 0.85 * R + SLOPE * (base - 0.16 * R) + 0.31 * R + max(0.14 * R, 1.0)
    a, am = word("ALERİ", cap, x0, base)
    aw = a.bounds()[2] - a.bounds()[0]
    if isik_scale is None:
        probe, _ = word("IŞIK", cap, 0, 0, tracking=cap * 0.3)
        isik_scale = aw / (probe.bounds()[2] - probe.bounds()[0])
    c2 = cap * isik_scale
    y2 = base - (gap if gap is not None else max(0.45 * cap, 1.4)) - c2
    b, bm = word("IŞIK", c2, x0, y2, tracking=c2 * 0.3)
    return items + [(a, pal["galeri"]), (am, pal["isik"]), (b, pal["isik"]), (bm, pal["galeri"])]


def bounds(items):
    return A.union(*[cs for cs, _ in items]).bounds()


def place(items, x, y, align="c", valign="m", ref_cap=None):
    """Öğeleri birlikte taşır: (x, y) dış sınırlarının align / valign noktası ('b' ise ref_cap'li taban çizgisi y=0)."""
    b = bounds(items)
    dx = {"l": x - b[0], "c": x - (b[0] + b[2]) / 2, "r": x - b[2]}[align]
    if valign == "b":
        dy = y
    else:
        dy = {"m": y - (b[1] + b[3]) / 2, "t": y - b[3], "bb": y - b[1]}[valign]
    return [(cs.translate((dx, dy)), col) for cs, col in items]


def fit(make, box, align="c", valign="m", R0=5.0):
    """make(R) ile kurulan logo kilidini kutuya (x0, y0, x1, y1) sığacak en büyük R ile kurup yerleştirir."""
    x0, y0, x1, y1 = box
    R = R0
    for _ in range(4):
        b = bounds(make(R))
        k = min((x1 - x0) / (b[2] - b[0]), (y1 - y0) / (b[3] - b[1]))
        R *= k if abs(k - 1) > 0.002 else 1.0
    R *= 0.995
    items = make(R)
    x = {"l": x0, "c": (x0 + x1) / 2, "r": x1}[align]
    y = {"m": (y0 + y1) / 2, "t": y1, "bb": y0}[valign]
    return place(items, x, y, align, valign), R


# ---------------------------------------------------------------- görsel yardımcı (2B boyama)

def paint(items, bg, px_per_mm, pad=4.0, size=None):
    """2B öğeleri düz renkle boyar (tek-çift kuralı)."""
    b = bounds(items)
    if size is None:
        size = (int((b[2] - b[0] + 2 * pad) * px_per_mm), int((b[3] - b[1] + 2 * pad) * px_per_mm))
    im = Image.new("RGB", size, bg)
    ox = size[0] / 2 - (b[0] + b[2]) / 2 * px_per_mm
    oy = size[1] / 2 + (b[1] + b[3]) / 2 * px_per_mm
    for cs, col in items:
        mask = Image.new("1", size, 0)
        for p in cs.to_polygons():
            layer = Image.new("1", size, 0)
            ImageDraw.Draw(layer).polygon([(ox + u * px_per_mm, oy - v * px_per_mm) for u, v in p], fill=1)
            mask = ImageChops.logical_xor(mask, layer)
        im.paste(col, mask=mask)
    return im


def logo_sheet(path):
    """Asıl logo ile yeniden çizilen logo yan yana; altında iki satırlı kilit ve yalnız G işareti."""
    W, H = 1500, 760
    canvas = Image.new("RGB", (W, H), (244, 245, 247))
    dr = ImageDraw.Draw(canvas)
    dr.text((40, 26), "LOGO", fill=(24, 26, 30), font=K.fnt(34))
    dr.text((40, 72), "Üstte firmanın logosu, altında anahtarlıklar için yeniden çizilen hâli (baskıya uygun kalınlıkta).",
            fill=(96, 100, 110), font=K.fnt(20))
    src = os.path.join(os.path.dirname(OUT_DIR), "galeri_isik", "kaynak_logo.png")
    dr.rounded_rectangle((40, 120, W - 40, 300), 24, fill=(0, 0, 0))
    if os.path.exists(src):
        im = Image.open(src).convert("RGB")
        im = A.fit_into(im.convert("RGBA"), 1100, 140)
        canvas.paste(im, ((W - im.width) // 2, 140), im)
    line = paint(lockup_line(10.0), (0, 0, 0), 12.0)
    dr.rounded_rectangle((40, 320, W - 40, 500), 24, fill=(0, 0, 0))
    line = A.fit_into(line.convert("RGBA"), 1100, 140)
    canvas.paste(line, ((W - line.width) // 2, 340))
    st = A.fit_into(paint(lockup_stack(10.0), (0, 0, 0), 12.0).convert("RGBA"), 520, 200)
    dr.rounded_rectangle((40, 520, 740, 740), 24, fill=(0, 0, 0))
    canvas.paste(st, (390 - st.width // 2, 630 - st.height // 2))
    for k, (pal, bg) in enumerate(((DARK, (0, 0, 0)), (LIGHT, (250, 250, 248)), (ON_ORANGE, ORANGE))):
        g = A.fit_into(paint(g_mark(20.0, pal=pal), bg, 8.0, pad=6).convert("RGBA"), 200, 200)
        x0 = 770 + k * 235
        dr.rounded_rectangle((x0, 520, x0 + 215, 740), 24, fill=bg)
        canvas.paste(g, (x0 + 107 - g.width // 2, 630 - g.height // 2))
    canvas.save(path)



def bend(cs, cx, cy, r, center_deg, top=True, seg=0.25):
    """Düz yazıyı (orta x = 0, taban çizgisi y = 0) çember yayına büker. r: taban çizgisinin yarıçapı.
    top=True: üst yayda dışa bakan; False: alt yayda okunur hâlde."""
    out = []
    for p in cs.to_polygons():
        p = np.asarray(p, float)
        q = np.roll(p, -1, axis=0)
        pts = []
        for a, b in zip(p, q):                       # kenarları sık böl (bükülünce düz kalmasın)
            n = max(1, int(np.ceil(np.hypot(*(b - a)) / seg)))
            pts.append(a + (b - a) * np.linspace(0, 1, n, endpoint=False)[:, None])
        p = np.vstack(pts)
        x, y = p[:, 0], p[:, 1]
        th = np.radians(center_deg) + (-x if top else x) / r
        rad = r + y if top else r - y
        out.append(np.c_[cx + rad * np.cos(th), cy + rad * np.sin(th)])
    return m3.CrossSection(out, m3.FillRule.EvenOdd)


def arc_word(s, cap, cx, cy, r, center_deg, top=True, col=WHITE, mark_col=ORANGE, tracking=None):
    letters, marks = word(s, cap, 0, 0, align="c", tracking=tracking)
    return [(bend(letters, cx, cy, r, center_deg, top), col), (bend(marks, cx, cy, r, center_deg, top), mark_col)]


def small(text, cap, x, y, align="c", tracking=0.3, max_w=None):
    """Küçük yazılar (telefon, şehir): Outfit ExtraBold, 3 mm'de bile çizgiler ~0,6 mm."""
    f = outfit()
    if max_w:
        cap = f.fit_cap(text, cap, max_w, tracking)
    return f.text(text, cap, x, y, align=align, tracking=tracking)


def rule(x0, x1, y, t=0.8, r=1.1):
    """Ortasında elmas olan ince çizgi (logodaki elmas noktaya gönderme)."""
    cx = (x0 + x1) / 2
    g = 0.7
    return (A.rect(x0, y - t / 2, cx - r - g, y + t / 2) + A.rect(cx + r + g, y - t / 2, x1, y + t / 2)
            + diamond(cx, y, r))


def phone_lines(cx, top, w, cap=4.4, min_cap=3.2, lead=1.7):
    """Telefon: sığarsa tek satır (en az 3,2 mm), sığmazsa iki satır "0546 807" / "07 00". top: üst kenar.
    Döner (şekil, alt kenar)."""
    f = outfit()
    c1 = f.fit_cap(PHONE, cap, w, 0.3)
    if c1 >= min_cap:
        return small(PHONE, c1, cx, top - c1 / 2), top - c1
    c2 = min(cap, f.fit_cap("0546 807", cap, w, 0.3))
    return (small("0546 807", c2, cx, top - c2 / 2) + small("07 00", c2, cx, top - c2 * 1.5 - lead),
            top - 2 * c2 - lead)


def back_std(c, cx, cy, w, phone_cap=4.4):
    """Standart arka yüz: telefon (beyaz), elmaslı çizgi ve ANTALYA (turuncu). (cx, cy): telefonun altındaki çizgi."""
    r, g = 1.1, 0.9
    ph, _ = phone_lines(cx, 0, w, phone_cap)
    ph = ph.translate((0, cy + r + g - ph.bounds()[1]))
    c.back += [(ph, WHITE), (rule(cx - min(w, 30) / 2, cx + min(w, 30) / 2, cy, r=r), ORANGE),
               (small(CITY, 3.2, cx, cy - r - g - 1.6, tracking=1.0), ORANGE)]


def back_qr(c, cx, cy, module=1.0, phone_y=None, phone_w=40.0, phone_cap=3.6):
    q, size = U.qr(cx, cy, module, data=QR_TEXT)
    c.back.append((q, WHITE))
    c.qr_box = A.rect(-cx - size / 2, cy - size / 2, -cx + size / 2, cy + size / 2)   # öne göre (aynalı)
    if phone_y is not None:
        c.back.append((small(PHONE, phone_cap, cx, phone_y, max_w=phone_w), WHITE))
    c.qr = True
    return size


def card(key, title, desc, outline, hole_xy, body=BLACK, holes=None):
    return K.Concept(key, title, desc, outline, holes if holes is not None else A.circle(HOLE_R, *hole_xy), body)


def rounded(cs, r):
    return cs.offset(-r, J).offset(r, J)


def with_lug(shape, lug_xy, lug_r=5.6, fillet=1.6):
    return (shape + A.circle(lug_r, *lug_xy)).offset(fillet, J).offset(-fillet, J)


# ---------------------------------------------------------------- 20 tasarım

def g01():
    W, H = 50.0, 30.0
    c = card("01_logo_kart", "Logo kart", "Sade siyah kart; ortada iki satırlı logo: G + ALERİ, altında ALERİ genişliğinde IŞIK.",
             A.rrect(W, H, 4.0), (W / 2 - 5.5, H / 2 - 5.5))
    c.front += fit(lockup_stack, (-W / 2 + 3.6, -H / 2 + 3.4, W / 2 - 9.0, H / 2 - 2.6))[0]
    back_std(c, 0, -2.0, W - 12)
    return c


def g02():
    W, H = 50.0, 22.0
    c = card("02_kapsul", "Kapsül", "Hap biçimi; solda delik, sağda iki satırlı logo.", A.rrect(W, H, H / 2), (-W / 2 + 6.5, 0))
    c.front += fit(lockup_stack, (-W / 2 + 12.6, -H / 2 + 2.6, W / 2 - 4.8, H / 2 - 2.4))[0]
    c.back += [(small(PHONE, 3.3, -4.6, 3.0, tracking=0.25), WHITE), (rule(-18.0, 9.0, -1.0), ORANGE),
               (small(CITY, 3.2, -4.6, -5.4, tracking=1.0), ORANGE)]
    return c


def g03():
    S = 44.0
    c = card("03_uygulama_ikonu", "Uygulama ikonu", "Telefon uygulaması ikonu gibi yuvarlak kare; büyük G işareti, altında IŞIK. Arkada QR.",
             A.rrect(S, S, 11.0), (-S / 2 + 7.6, S / 2 - 7.6))
    g = place(g_mark(21.0), 1.8, 4.8)
    isik, im = word("IŞIK", 5.0, 1.4, -14.8, align="c", valign="m", tracking=1.5)
    c.front += g + [(isik, ORANGE), (im, WHITE)]
    back_qr(c, -2.0, 3.0, 1.0, phone_y=-15.4, phone_w=35.6, phone_cap=3.4)
    return c


def g04():
    R = 21.0
    outline = with_lug(A.circle(R, 0, 0, 200), (0, R + 2.3))
    c = card("04_madalyon", "Madalyon", "Yuvarlak madalyon; ortada G işareti, üst yayda GALERİ, alt yayda IŞIK, yanlarda turuncu elmas.",
             outline, (0, R + 2.5))
    c.front += place(g_mark(13.6), 0, 0.2)
    c.front += arc_word("GALERİ", 3.6, 0, 0, 14.2, 90, top=True)
    c.front += arc_word("IŞIK", 4.0, 0, 0, 18.0, -90, top=False, col=ORANGE, mark_col=WHITE, tracking=1.2)
    c.front += [(diamond(-15.8, 0.4, 1.3) + diamond(15.8, 0.4, 1.3), ORANGE)]
    back_std(c, 0, -1.0, 32)
    return c


def g05():
    W, H, k = 50.0, 28.0, 9.0
    cut = A.polygon([(-W / 2 - 1, H / 2 + 1), (-W / 2 + k + SLOPE, H / 2 + 1), (-W / 2 - 1 - SLOPE * (k / SLOPE), H / 2 - k / SLOPE - 1)])
    tl = A.polygon([(-W / 2, H / 2 - k / SLOPE * 0.62 * 1.0), (-W / 2 + k, H / 2), (-W / 2 - 5, H / 2 + 5)])
    shape = A.rrect(W, H, 3.0) - A.polygon([(-W / 2 - 2, H / 2 - 9.0), (-W / 2 + 9.0 * SLOPE, H / 2 + 0.0),
                                            (-W / 2 - 2, H / 2 + 2)])
    shape = shape - A.polygon([(W / 2 + 2, -H / 2 + 9.0), (W / 2 - 9.0 * SLOPE, -H / 2), (W / 2 + 2, -H / 2 - 2)])
    shape = rounded(shape, 2.0)
    c = card("05_kesik_kose", "Kesik köşe", "İki köşesi logodaki eğik çizgiyle aynı açıda kesik; kesiğe paralel turuncu çizgi.",
             shape, (-W / 2 + 6.0, -H / 2 + 6.0))
    del cut, tl
    c.front += [(A.polygon([(-W / 2 + 1.0, H / 2 - 12.2), (-W / 2 + 1.0 + 1.2, H / 2 - 12.2),
                            (-W / 2 + 9.0 * SLOPE + 3.2, H / 2 - 1.0), (-W / 2 + 9.0 * SLOPE + 2.0, H / 2 - 1.0)]), ORANGE)]
    c.front += fit(lockup_stack, (-W / 2 + 11.0, -H / 2 + 2.8, W / 2 - 3.2, H / 2 - 2.6))[0]
    back_std(c, -3.0, -1.4, 32)
    return c


def g06():
    W, H = 50.0, 28.0
    shape = A.rrect(W, H, 4.0)
    c = card("06_capraz_bolunmus", "Çapraz bölünmüş", "Sol yanı turuncu, logodaki eğik çizgi kartı boydan boya böler; turuncunun içinde siyah G.",
             shape, (W / 2 - 5.5, H / 2 - 5.5))
    items, R = fit(lockup_stack, (-W / 2 + 6.0, -H / 2 + 3.4, W / 2 - 9.4, H / 2 - 3.0))
    gb = items[0][0].bounds()
    gx, gy = gb[0] + R, gb[3] - R                    # C'nin merkezi
    gap = 0.75 * math.hypot(1, SLOPE)
    x_at = lambda y: gx + 0.85 * R + SLOPE * (y - gy - 0.16 * R)  # noqa: E731
    inner = shape.offset(-1.0, J)
    band = A.polygon([(x_at(-H), -H), (x_at(-H) + 0.31 * R, -H), (x_at(H) + 0.31 * R, H), (x_at(H), H)]) ^ inner
    zone = A.polygon([(-W, -H), (x_at(-H) - gap, -H), (x_at(H) - gap, H), (-W, H)]) ^ inner
    c.front += [(zone - items[0][0].offset(0.8, J), ORANGE), (band, WHITE)] + items[2:]
    back_std(c, 2.0, -1.4, 34)
    return c


def g07():
    R = 24.0
    hexa = A.polygon([(R * math.cos(math.radians(90 + 60 * i)), R * math.sin(math.radians(90 + 60 * i))) for i in range(6)])
    c = card("07_altigen", "Altıgen", "Sivri tepeli altıgen (bijon somunu gibi); ortada G işareti, altında IŞIK.",
             rounded(hexa, 3.0), (0, R - 7.2))
    c.front += place(g_mark(16.0), 0.0, 0.4)
    isik, im = word("IŞIK", 4.4, 0, -13.4, align="c", valign="m", tracking=1.3)
    c.front += [(isik, ORANGE), (im, WHITE)]
    back_std(c, 0, -2.0, 30)
    return c


def g08():
    W, H = 42.0, 48.0
    c = card("08_kalkan", "Kalkan", "Kalkan biçimi; üstte delik, ortada iki satırlı logo, sivri uçta turuncu şevron.",
             U.shield(W, H, 3.0), (0, H / 2 - 6.0))
    c.front += fit(lockup_stack, (-W / 2 + 3.4, -6.0, W / 2 - 3.4, H / 2 - 10.4))[0]
    c.front += [(rounded(A.polygon([(-9, -12.2), (-6.4, -12.2), (0, -17.6), (6.4, -12.2), (9, -12.2), (0, -19.8)]), 0.3),
                 ORANGE)]
    back_std(c, 0, -1.0, 32)
    return c


def g09():
    body = A.rrect(32.0, 40.0, 10.0, 0, -5.0)
    outline = with_lug(body, (0, 17.0), 6.4, 2.4)
    c = card("09_kumanda", "Araç kumandası", "Araç anahtarı kumandası biçimi; düğme gibi beyaz halka içinde G işareti, altında IŞIK.",
             outline, (0, 18.0))
    c.front += [(A.outline(A.circle(11.6, 0, 1.0, 160), 1.0), WHITE)]
    c.front += place(g_mark(13.0), 0.2, 1.2)
    isik, im = word("IŞIK", 4.6, 0, -16.6, align="c", valign="m", tracking=1.2)
    c.front += [(isik, ORANGE), (im, WHITE)]
    c.back += [(small("0546 807", 4.4, 0, 4.2, tracking=0.3), WHITE), (small("07 00", 4.4, 0, -2.6, tracking=0.3), WHITE),
               (rule(-10, 10, -7.8), ORANGE), (small(CITY, 3.2, 0, -12.4, tracking=0.8), ORANGE)]
    return c


def car_line():
    """Sade araba silueti: tavan, cam ve kaput çizgisi (tek çizgi)."""
    pts = [(-18, 0.0), (-17.4, 2.6), (-13.5, 3.6), (-8.0, 7.6), (2.0, 7.9), (8.2, 4.4), (16.4, 3.2), (18.2, 1.2), (18.4, 0.0)]
    return A.stroke(A.smooth(pts, n=200), 1.2)


def g10():
    W, H = 50.0, 34.0
    c = card("10_araba_cizgisi", "Araba çizgisi", "Üstte tek çizgiyle turuncu araba silueti, altında iki satırlı logo.",
             A.rrect(W, H, 4.0), (-W / 2 + 5.5, H / 2 - 5.5))
    car = car_line().translate((3.4, H / 2 - 12.6))
    c.front += [(car, ORANGE)]
    c.front += fit(lockup_stack, (-W / 2 + 4.0, -H / 2 + 3.0, W / 2 - 4.0, H / 2 - 14.6))[0]
    back_std(c, 0, -2.0, W - 12)
    return c


def g11():
    W, H = 50.0, 24.0
    c = card("11_hiz_cizgileri", "Hız çizgileri", "G işaretinin solunda hızı anlatan üç beyaz çizgi; sağda delik.",
             A.rrect(W, H, 4.0), (W / 2 - 5.5, 0))
    items, R = fit(lockup_stack, (-W / 2 + 10.4, -H / 2 + 2.6, W / 2 - 10.2, H / 2 - 2.4))
    gb = items[0][0].bounds()
    cy = (gb[1] + gb[3]) / 2
    lines = [A.rrect(L, 1.2, 0.59, gb[0] - 1.6 - L / 2, cy + dy) for L, dy in ((5.0, 3.0), (7.4, 0.0), (5.0, -3.0))]
    c.front += items + [(A.union(*lines), WHITE)]
    back_std(c, 4.0, -1.4, 37)
    return c


def g12():
    H = 34.0
    R = H / 2
    g, sl = g_mark(H)
    sil = (g[0] + sl[0]).offset(2.4, J)
    lug_xy = ((R + 3.2) * math.cos(math.radians(140)), (R + 3.2) * math.sin(math.radians(140)))
    outline = rounded(with_lug(sil, lug_xy, 5.6, 2.0), 1.0)
    c = card("12_logo_silueti", "Logo silueti", "Anahtarlığın kendisi G işareti: turuncu G, beyaz eğik çizgi; arkada yay üstünde telefon.",
             outline, lug_xy)
    c.front += [g, sl]
    c.back += [(bend(small(PHONE, 3.2, 0, 1.6, align="c", tracking=0.25), 0, 0, 17.2, -62, top=False), WHITE)]
    return c


def g13():
    W, H = 46.0, 28.0
    c = card("13_turuncu_govde", "Turuncu gövde", "Gövde turuncu; G siyah, eğik çizgi ve GALERİ beyaz, IŞIK siyah.",
             A.rrect(W, H, 5.0), (W / 2 - 5.5, H / 2 - 5.5), body=ORANGE)
    c.front += fit(lambda R: lockup_stack(R, ON_ORANGE), (-W / 2 + 3.4, -H / 2 + 3.0, W / 2 - 8.6, H / 2 - 2.6))[0]
    c.back += [(small(PHONE, 3.6, -1.0, 2.6, max_w=W - 9), BLACK), (rule(-15, 13, -1.6), WHITE),
               (small(CITY, 3.2, -1.0, -6.2, tracking=1.0), BLACK)]
    return c


def g14():
    W, H = 46.0, 28.0
    c = card("14_beyaz_govde", "Beyaz gövde", "Gövde beyaz; GALERİ ve eğik çizgi siyah, G ve IŞIK turuncu; altta turuncu şerit.",
             A.rrect(W, H, 5.0), (W / 2 - 5.5, H / 2 - 5.5), body=WHITE)
    c.front += fit(lambda R: lockup_stack(R, LIGHT), (-W / 2 + 3.4, -H / 2 + 5.2, W / 2 - 8.6, H / 2 - 2.6))[0]
    c.front += [(A.rect(-W / 2, -H / 2, W / 2, -H / 2 + 4.2) ^ A.rrect(W, H, 5.0).offset(-1.0, J), ORANGE)]
    c.back += [(small(PHONE, 3.6, 1.0, 3.2, max_w=W - 9), BLACK), (rule(-13, 15, -1.0), ORANGE),
               (small(CITY, 3.2, 1.0, -5.6, tracking=1.0), BLACK)]
    return c


def g15():
    W, H = 22.0, 50.0
    c = card("15_dikey_etiket", "Dikey etiket", "İnce dikey etiket; üstte G işareti, altında alt alta I-Ş-I-K.",
             A.rrect(W, H, 5.0), (0, H / 2 - 5.6))
    c.front += place(g_mark(12.2), 0.3, 9.2)
    cap, step = 4.6, 6.3
    for i, ch in enumerate("IŞIK"):
        l, m = word(ch, cap, 0, -2.2 - i * step, align="c", valign="m")
        c.front += [(l, ORANGE), (m, WHITE)]
    back = [small("0546", 4.4, 0, 9.0), small("807", 4.4, 0, 2.6), small("07 00", 4.4, 0, -3.8)]
    c.back += [(A.union(*back), WHITE), (rule(-7, 7, -9.4), ORANGE)] + place(g_mark(8.4), 0.2, -17.0)
    return c


def g16():
    W, H = 32.0, 48.0
    tag = A.rrect(W, H, 7.0)
    hole = (0, H / 2 - 6.4)
    c = card("16_kunye", "Künye", "Askeri künye biçimi; ince beyaz çerçeve, G işareti ve IŞIK. Arkada telefon QR'ı.",
             tag, hole)
    c.front += [(A.outline(tag, 0.9, inset=1.7) - A.circle(HOLE_R + 3.4, *hole), WHITE)]
    c.front += place(g_mark(14.0), 0.4, 4.0)
    isik, im = word("IŞIK", 4.6, 0, -12.6, align="c", valign="m", tracking=1.0)
    c.front += [(isik, ORANGE), (im, WHITE)]
    back_qr(c, 0, 1.8, 0.98)
    ph, _ = phone_lines(0, -12.0, W - 6.0, 3.6)
    c.back.append((ph, WHITE))
    return c


def g17():
    Ro, Ri = 23.4, 9.0
    c = card("17_halka", "Halka", "Simit biçimi; anahtar halkası ortadan geçer. Üst yayda GALERİ, alt yayda IŞIK, aralarında elmas.",
             A.circle(Ro, 0, 0, 220), None, holes=A.circle(Ri, 0, 0, 160))
    rm = (Ro + Ri) / 2
    c.front += arc_word("GALERİ", 4.0, 0, 0, rm - 2.0, 90, top=True)
    c.front += arc_word("IŞIK", 4.4, 0, 0, rm + 2.2, -90, top=False, col=ORANGE, mark_col=WHITE, tracking=1.6)
    c.front += [(diamond(-rm, 0, 1.4) + diamond(rm, 0, 1.4), ORANGE)]
    c.back += [(bend(small(PHONE, 3.3, 0, 0, align="c", tracking=0.25).translate((0, -1.65)), 0, 0, rm - 1.65, 90, top=True), WHITE),
               (bend(small(CITY, 3.2, 0, 0, align="c", tracking=1.2).translate((0, -1.6)), 0, 0, rm + 1.6, -90, top=False), ORANGE)]
    return c


def g18():
    D = 24.0
    rh = rounded(A.polygon([(0, D), (D - 2, 0), (0, -D), (-(D - 2), 0)]), 3.0)
    c = card("18_elmas", "Elmas", "Logodaki elmas noktadan: eşkenar dörtgen gövde; ortada G işareti, altında IŞIK, iki yanda elmas.",
             rh, (0, D - 8.4))
    c.front += place(g_mark(14.4), 0.2, 0.6)
    isik, im = word("IŞIK", 3.8, 0, -11.6, align="c", valign="m", tracking=1.0)
    c.front += [(isik, ORANGE), (im, WHITE), (diamond(-13.6, 0.6, 1.3) + diamond(13.6, 0.6, 1.3), ORANGE)]
    c.back += [(small("0546 807", 3.8, 0, 4.4, tracking=0.3), WHITE), (small("07 00", 3.8, 0, -1.4, tracking=0.3), WHITE),
               (small(CITY, 3.2, 0, -7.6, tracking=0.5), ORANGE)]
    return c


def g19():
    S = 44.0
    c = card("19_qr_kart", "QR kart", "Kare kart; önde iki satırlı logo, arkada telefon QR'ı (okutunca arar) ve numara.",
             A.rrect(S, S, 6.0), (S / 2 - 6.0, S / 2 - 6.0))
    c.front += fit(lockup_stack, (-S / 2 + 3.4, -S / 2 + 4.0, S / 2 - 3.4, S / 2 - 12.4))[0]
    c.front += [(rule(-S / 2 + 4.0, S / 2 - 12.0, S / 2 - 6.0), ORANGE)]
    back_qr(c, 2.4, 3.2, 1.0, phone_y=-15.0, phone_w=S - 9.0, phone_cap=3.6)
    return c


def g20():
    R = 21.0
    outline = with_lug(A.circle(R, 0, 0, 200), (0, R + 2.3))
    c = card("20_direksiyon", "Direksiyon", "Direksiyon simidi: beyaz simit, göbek halkası ve üç kol; göbekte G işareti.",
             outline, (0, R + 2.5))
    rim = A.circle(18.8, 0, 0, 200) - A.circle(15.6, 0, 0, 200)
    hub = A.circle(10.2, 0, -0.6, 160) - A.circle(8.6, 0, -0.6, 160)
    side = A.polygon([(-9.4, 1.4), (-9.4, -4.4), (-16.6, -6.6), (-16.6, 0.4)])
    spokes = side + side.mirror((1, 0)) + A.polygon([(-2.6, -9.6), (2.6, -9.6), (3.2, -16.4), (-3.2, -16.4)])
    c.front += [(rounded(rim + hub + spokes, 0.6), WHITE)]
    c.front += place(g_mark(11.4), 0.3, -0.6)
    back_std(c, 0, -1.0, 32)
    return c


CONCEPTS = [g01, g02, g03, g04, g05, g06, g07, g08, g09, g10, g11, g12, g13, g14, g15, g16, g17, g18, g19, g20]


# ---------------------------------------------------------------- kontroller

def check(c):
    """Kırpılan öğe, delik çevresi et payı, öğelerde 0,6 mm'den ince yer (QR hariç), farklı öğeler arası 0,6 mm."""
    shape = c.outline - c.holes
    keep = shape.offset(-1.0, J) - c.holes.offset(0.8, J)
    issues = []

    def spots(cs):
        return sum(p.area() for p in cs.decompose() if p.area() > 0.2)

    for side, items in (("ön", c.front), ("arka", c.back)):
        faces = []
        for i, (cs, col) in enumerate(items):
            s = cs.mirror((1, 0)) if side == "arka" else cs
            out = (s - keep).area()
            if out > 0.02:
                issues.append(f"{side}[{i}] kırpılıyor {out:.2f} mm²")
            s = s ^ keep
            thin = s - s.offset(-0.3, J).offset(0.3, J)
            if side == "arka" and getattr(c, "qr_box", None) is not None:
                thin = thin - c.qr_box
            if spots(thin):
                issues.append(f"{side}[{i}] 0,6 mm'den ince {spots(thin):.1f} mm²")
            faces.append(s)
        for i, a in enumerate(faces):
            for j in range(i + 1, len(faces)):
                b = faces[j]
                if a.is_empty() or b.is_empty() or (a.offset(0.05, J) ^ b).area() > 0.01:
                    continue                            # bitişik öğeler (ör. turuncu alan + beyaz şerit)
                if (a.offset(0.3, J) ^ b.offset(0.3, J)).area() > 0.02:
                    issues.append(f"{side}[{i}]-[{j}] arası 0,6 mm'den dar")
    wall = None
    if c.holes.area() < 400:
        for w in np.arange(1.0, 6.01, 0.1):
            if (c.holes.offset(w, J) - c.outline).area() > 1e-3:
                wall = round(w - 0.1, 1)
                break
        if wall is not None and wall < 3.0:
            issues.append(f"delik çevresi {wall} mm")
    w, h = c.size()
    if w > 50.01 or h > 50.01:
        issues.append(f"boyut {w:.1f} × {h:.1f}")
    return issues, wall


def qr_check(c):
    import zxingcpp
    parts = K.mesh_parts(c)
    R = rotation(180, 180)
    rgba = render(parts, 900, R, light=False, margin=0.05)
    bg = Image.new("L", rgba.size, 255)
    bg.paste(rgba.convert("L"), (0, 0), rgba.split()[-1])
    res = zxingcpp.read_barcodes(bg)
    return res[0].text if res else None



# ---------------------------------------------------------------- sayfalar

def sheet(c, path, i):
    title = c.title
    c.title = f"{i:02d}  " + title.replace("i", "İ")
    canvas = K.concept_sheet(c, path)
    c.title = title
    if getattr(c, "qr", False):
        dr = ImageDraw.Draw(canvas)
        txt = getattr(c, "qr_read", None)
        dr.text((1060, 586), f"QR okundu: {txt}" if txt else "QR OKUNAMADI", fill=(22, 120, 60) if txt else (200, 30, 30),
                font=K.fnt(18))
        canvas.save(path)
    return canvas


def header(dr, im, W, title, sub):
    """Siyah başlık: solda logonun kendisi (geometriden), sağda turuncu eğik çizgiler."""
    dr.rectangle((0, 0, W, 260), fill=(10, 10, 11))
    for x in range(W - 520, W + 200, 46):
        dr.polygon([(x, 260), (x + 16, 260), (x + 16 + 0.62 * 150, 110), (x + 0.62 * 150, 110)], fill=(26, 26, 28))
    logo = A.fit_into(paint(lockup_line(10.0), (10, 10, 11), 14.0, pad=1.0).convert("RGBA"), 760, 110)
    im.paste(logo, (70, 46))
    dr.text((72, 182), title, font=K.fnt(34), fill=(240, 240, 238))
    dr.text((72 + dr.textlength(title, font=K.fnt(34)) + 20, 190), sub, font=K.fnt(24), fill=ORANGE)
    dr.rectangle((0, 256, W, 262), fill=ORANGE)


def customer_pages(concepts, per_page=10, start_page=1, total=20):
    """Müşteriye gönderilecek sayfalar: her önerinin ön ve arka yüzü, numarası ve adı (A4, 10'ar)."""
    W, H = 1654, 2339
    paths = []
    for p0 in range(0, len(concepts), per_page):
        page = concepts[p0:p0 + per_page]
        n0 = page[0][0]
        im = Image.new("RGB", (W, H), (244, 244, 242))
        dr = ImageDraw.Draw(im)
        header(dr, im, W, "Anahtarlık önerileri", f"{n0}–{page[-1][0]} / {total}")
        dr.text((70, 290), "Siyah gövde, turuncu ve beyaz logo · en çok 50 × 50 mm · arka yüzde telefon "
                           "(QR'lılarda okutunca arar)", font=K.fnt(26), fill=(40, 40, 44))
        top, gap, cw = 350, 26, (W - 3 * 50) // 2
        ch = (H - top - 150 - 4 * gap) // 5
        for k, (n, c) in enumerate(page):
            x0, y0 = 50 + (k % 2) * (cw + 50), top + (k // 2) * (ch + gap)
            dr.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 26, fill=(255, 255, 255), outline=(222, 222, 226))
            dr.ellipse((x0 + 22, y0 + 20, x0 + 78, y0 + 76), fill=(16, 16, 18))
            num = str(n)
            dr.text((x0 + 50 - dr.textlength(num, font=K.fnt(28)) / 2, y0 + 30), num, font=K.fnt(28), fill=ORANGE)
            dr.text((x0 + 94, y0 + 26), c.title, font=K.fnt(32), fill=(20, 20, 22))
            w, h = c.size()
            tag = f"{w:.0f} × {h:.0f} mm" + ("  ·  QR" if getattr(c, "qr", False) else "")
            dr.text((x0 + cw - 28 - dr.textlength(tag, font=K.fnt(22)), y0 + 34), tag, font=K.fnt(22),
                    fill=ORANGE if getattr(c, "qr", False) else (110, 112, 120))
            parts = K.mesh_parts(c)
            for j, (R, label) in enumerate(((rotation(0, 0), "ÖN"), (rotation(180, 180), "ARKA"))):
                img = A.fit_into(render(parts, 900, R, margin=0.02), cw // 2 - 60, ch - 120)
                bx = x0 + 30 + j * (cw // 2 - 15)
                K.paste_center(im, img, (bx, y0 + 96, bx + cw // 2 - 45, y0 + ch - 16))
                dr.text((bx, y0 + 90), label, font=K.fnt(18), fill=(150, 152, 160))
            dr.line((x0 + cw // 2, y0 + 110, x0 + cw // 2, y0 + ch - 24), fill=(232, 232, 236), width=2)
        foot = "Beğendiğiniz modelin numarasını yazmanız yeterli."
        dr.rounded_rectangle((50, H - 130, W - 50, H - 50), 22, fill=(10, 10, 11))
        dr.text((W / 2 - dr.textlength(foot, font=K.fnt(30)) / 2, H - 108), foot, font=K.fnt(30), fill=ORANGE)
        path = os.path.join(OUT_DIR, f"musteri_{start_page + p0 // per_page}.png")
        im.save(path, optimize=True)
        paths.append(path)
    return paths


def build(i):
    """i. tasarım: kontroller, QR okuma ve ayrıntı sayfası (ayrı süreçte çalışır). Döner (satır, sorunlu mu)."""
    c = CONCEPTS[i - 1]()
    c.front, c.back = U.resolve(c.front), U.resolve(c.back)
    issues, wall = check(c)
    if getattr(c, "qr", False):
        c.qr_read = qr_check(c)
        if c.qr_read != QR_TEXT:
            issues.append(f"QR okunamadı ({c.qr_read})")
    sheet(c, os.path.join(OUT_DIR, c.key + ".png"), i)
    w, h = c.size()
    return (f"{c.key:22s} {w:4.1f} × {h:4.1f} mm  renk {len(c.colours())}  delik eti {wall}  "
            f"{'; '.join(issues) or 'kontroller tamam'}" + (f"  QR: {c.qr_read}" if getattr(c, "qr", False) else ""),
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
                   title="GALERİ IŞIK – ANAHTARLIK ÖNERİLERİ (ön yüz · QR'lılarda arka yüz)")
        return [os.path.join(OUT_DIR, "hepsi.png")]
    return customer_pages(concepts, start_page=kind)


def main():
    """Argümansız: 20 öneri, genel görünüm, müşteri sayfaları (4 süreçte). Anahtar verilirse yalnız o sayfalar;
    "logo": logo sayfası."""
    from multiprocessing import Pool
    os.makedirs(OUT_DIR, exist_ok=True)
    only = sys.argv[1:]
    if only == ["logo"]:
        logo_sheet(os.path.join(OUT_DIR, "logo.png"))
        return
    todo = [i for i, fn in enumerate(CONCEPTS, 1) if not only or any(o in fn().key for o in only)]
    with Pool(4) as pool:
        rows = pool.map(build, todo)
        for line, _ in rows:
            print(line)
        bad = sum(b for _, b in rows)
        if not only:
            logo_sheet(os.path.join(OUT_DIR, "logo.png"))
            pages = pool.map(build_pages, [("genel", todo), (1, todo[:10]), (2, todo[10:])])
            print(pages)
            pdf = [Image.open(p).convert("RGB") for p in pages[1] + pages[2]]
            pdf[0].save(os.path.join(OUT_DIR, "musteri_katalog.pdf"), save_all=True, append_images=pdf[1:],
                        resolution=200)
    print("sorunlu:", bad)


if __name__ == "__main__":
    main()
