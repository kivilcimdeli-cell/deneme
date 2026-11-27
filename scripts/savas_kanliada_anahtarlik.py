"""SAVAŞ KANLIADA (otomotiv ve gayrimenkul danışmanlığı) kurumsal anahtarlık önerileri: antrasit, kırmızı, beyaz;
en çok 50 × 50 mm. GALERİ IŞIK kataloğunun yapısı (20 öneri, ön ve arka yüz, müşteri sayfaları ve PDF).

Logo müşterinin görselinden (scripts/savas_kanliada_logo.py): kırmızı S ve K, üstte gümüş (burada beyaz) çatı ve
pencere. Çatı ile harfler arasında logodaki gibi gövde renginde boşluk (≥ 0,7 mm: 0,4 nozul ayırır). Küçük boyda dört
pencere camı tek kare + artı çizgiye sadeleşir (camlar ≥ 0,9 mm). Ad Poppins ExtraBold (logodaki kalın yazıya en
yakın), kırmızı; alt satır beyaz.
Arka yüz: telefon 0506 101 68 97 ve OTOMOTİV · GAYRİMENKUL; QR'lılarda (3, 16, 19) telefon QR'ı (TEL:+905061016897),
arka yüz görüntüsünden okunarak doğrulanır.

Baskı kontrolleri GALERİ IŞIK'takilerle aynı (galeri_isik_anahtarlik.check).
Çıktı : anahtarlik/savas_kanliada/<nn>_<ad>.png, hepsi.png, musteri_1.png, musteri_2.png, musteri_katalog.pdf, logo.png
Kullanım: python3 scripts/savas_kanliada_logo.py (bir kez); python3 scripts/savas_kanliada_anahtarlik.py [anahtar ...]
"""
import math
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
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "anahtarlik", "savas_kanliada")
PHONE, SUB = "0506 101 68 97", "OTOMOTİV · GAYRİMENKUL"
QR_TEXT = "TEL:+905061016897"
NAME = "SAVAŞ KANLIADA"
ANT = (58, 61, 66)                                 # antrasit gövde
RED = (214, 32, 42)                                # logodaki kırmızı
WHITE = K.WHITE
K.FILAMENT.update({ANT: "antrasit – PLA Matte Charcoal", WHITE: "beyaz – PLA Basic White",
                   RED: "kırmızı – PLA Basic Red"})
J = m3.JoinType.Round
HOLE_R = G.HOLE_R
G.QR_TEXT = QR_TEXT                                # G.qr_check bununla karşılaştırır

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
    w = (b[2] - b[0]) * (1.25 if iki else 1.55)
    gap = max(0.12 * R, 1.0)
    if not iki:
        _, c = ad_sigdir(NAME, 0.36 * R, w)
        iki = c < 3.4                                       # tek satır çok küçük kalıyorsa iki satır
        w = (b[2] - b[0]) * (1.25 if iki else 1.55)
    if iki:
        a1, c1 = ad_sigdir("SAVAŞ", 0.42 * R, w)
        a2, _ = ad_sigdir("KANLIADA", c1, w)
        y1 = b[1] - gap - c1 / 2
        items += [(a1.translate((0, y1)), pal["ad"]), (a2.translate((0, y1 - c1 * 1.75)), pal["ad"])]
    else:
        a, c = ad_sigdir(NAME, 0.36 * R, w)
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


def back_std(c, cx, cy, w, phone_cap=4.4, col=WHITE, acc=RED):
    ph, _ = phone_lines(cx, 0, w, phone_cap)
    ph = ph.translate((0, cy + 2.9 - ph.bounds()[1]))
    c.back += [(ph, col), (rule(cx - min(w, 30) / 2, cx + min(w, 30) / 2, cy - 0.4), acc),
               (alt_satir(cx, cy - 4.8, w), acc)]


def alt_satir(cx, y, w, cap=3.2):
    """Arka yüzün alt satırı: sığarsa OTOMOTİV · GAYRİMENKUL, sığmazsa DANIŞMANLIK (yazı 3,2 mm'nin altına inmez)."""
    f = G.outfit()
    for t in (SUB, "DANIŞMANLIK"):
        if f.fit_cap(t, cap, w, 0.35) >= cap:
            return small(t, cap, cx, y, tracking=0.35).offset(0.12, J)
    return small("DANIŞMANLIK", f.fit_cap("DANIŞMANLIK", cap, w, 0.2), cx, y, tracking=0.2).offset(0.12, J)


def back_qr(c, cx, cy, module=1.0, phone_y=None, phone_w=40.0, phone_cap=3.6):
    q, size = U.qr(cx, cy, module, data=QR_TEXT)
    c.back.append((q, WHITE))
    c.qr_box = A.rect(-cx - size / 2, cy - size / 2, -cx + size / 2, cy + size / 2)
    if phone_y is not None:
        c.back.append((small(PHONE, phone_cap, cx, phone_y, max_w=phone_w), WHITE))
    c.qr = True
    return size


def card(key, title, desc, outline, hole_xy, body=ANT, holes=None):
    return K.Concept(key, title, desc, outline, holes if holes is not None else A.circle(HOLE_R, *hole_xy), body)


rounded, with_lug, fit, place = G.rounded, G.with_lug, G.fit, G.place


def ev(w, h, roof):
    """Ev silueti: dikdörtgen gövde + üçgen çatı (köşeler yuvarlatılmış). Taban y = -h/2."""
    return rounded(A.polygon([(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2 - roof), (0, h / 2),
                              (-w / 2, h / 2 - roof)]), 2.4)


def car_line():
    return G.car_line()


# ---------------------------------------------------------------- 20 tasarım

def s01():
    W, H = 50.0, 32.0
    c = card("01_logo_kart", "Logo kart", "Sade antrasit kart; işaret ve altında SAVAŞ KANLIADA.",
             A.rrect(W, H, 4.0), (W / 2 - 5.5, H / 2 - 5.5))
    c.front += fit(stack, (-W / 2 + 3.6, -H / 2 + 3.2, W / 2 - 9.0, H / 2 - 2.6))[0]
    back_std(c, 0, -1.0, W - 12)
    return c


def s02():
    W, H = 50.0, 22.0
    c = card("02_kapsul", "Kapsül", "Hap biçimi; solda delik, sağda işaret ve iki satır ad.", A.rrect(W, H, H / 2),
             (-W / 2 + 6.5, 0))
    c.front += fit(line, (-W / 2 + 12.0, -H / 2 + 2.4, W / 2 - 4.0, H / 2 - 2.4))[0]
    c.back += [(small(PHONE, 3.3, -4.6, 3.2, tracking=0.25), WHITE), (rule(-18.0, 9.0, -0.6), RED),
               (alt_satir(-4.6, -5.2, 30), RED)]
    return c


def s03():
    S = 44.0
    c = card("03_uygulama_ikonu", "Uygulama ikonu", "Yuvarlak kare; büyük işaret, altında ad. Arkada telefon QR'ı.",
             A.rrect(S, S, 11.0), (-S / 2 + 7.6, S / 2 - 7.6))
    c.front += place(sk_mark(24.0), 2.0, 4.6)
    a, _ = ad_sigdir(NAME, 4.0, S - 7.0, 0, -15.4)
    c.front += [(a, RED)]
    back_qr(c, -2.0, 3.0, 1.0, phone_y=-15.4, phone_w=35.6, phone_cap=3.4)
    return c


def s04():
    R = 21.0
    outline = with_lug(A.circle(R, 0, 0, 200), (0, R + 2.3))
    c = card("04_madalyon", "Madalyon", "Yuvarlak madalyon; ortada işaret, üst yayda SAVAŞ, alt yayda KANLIADA.",
             outline, (0, R + 2.5))
    c.front += place(sk_mark(15.0), 0, 0.4)
    c.front += [(G.bend(ad("SAVAŞ", 3.6, 0, 0, valign="b", tracking=0.9), 0, 0, 14.6, 90, top=True), RED),
                (G.bend(ad("KANLIADA", 3.6, 0, 0, valign="b", tracking=0.7), 0, 0, 18.2, -90, top=False), RED)]
    back_std(c, 0, -0.6, 32)
    return c


def s05():
    W, H = 40.0, 48.0
    shape = ev(W, H, 15.0)
    c = card("05_ev", "Ev", "Anahtarlığın kendisi ev biçiminde (gayrimenkul); çatının altında işaret, altında iki satır ad.",
             shape, (0, H / 2 - 7.6))
    c.front += fit(lambda R: stack(R, iki=True), (-W / 2 + 3.6, -H / 2 + 3.4, W / 2 - 3.6, H / 2 - 13.4))[0]
    back_std(c, 0, -3.0, 30)
    return c


def s06():
    W, H = 50.0, 32.0
    slope = 0.78
    top = rounded(A.polygon([(-W / 2, -H / 2), (W / 2, -H / 2), (W / 2, H / 2 - 9), (W / 2 - 9 / slope * 0 - 9, H / 2),
                             (-W / 2, H / 2)]), 3.0)
    c = card("06_cati_kart", "Çatı kart", "Sağ üst köşe çatı eğimiyle kesik; kesiğe paralel beyaz çizgi (çatıdan), yanında ad.",
             top, (-W / 2 + 5.5, H / 2 - 5.5))
    c.front += [(A.polygon([(W / 2 - 1.4, H / 2 - 12.6), (W / 2 - 1.4, H / 2 - 10.8), (W / 2 - 10.8, H / 2 - 1.4),
                            (W / 2 - 12.6, H / 2 - 1.4)]), WHITE)]
    c.front += fit(line, (-W / 2 + 3.4, -H / 2 + 3.0, W / 2 - 8.0, H / 2 - 10.6))[0]
    back_std(c, -2.0, -1.0, 34)
    return c


def s07():
    R = 24.0
    hexa = A.polygon([(R * math.cos(math.radians(90 + 60 * i)), R * math.sin(math.radians(90 + 60 * i))) for i in range(6)])
    c = card("07_altigen", "Altıgen", "Sivri tepeli altıgen; ortada işaret, altında ad.", rounded(hexa, 3.0), (0, R - 7.2))
    c.front += fit(lambda R: stack(R, iki=True), (-12.0, -15.0, 12.0, 12.6))[0]
    back_std(c, 0, -1.6, 30)
    return c


def s08():
    W, H = 42.0, 48.0
    c = card("08_kalkan", "Kalkan", "Kalkan biçimi; üstte delik, ortada işaret ve iki satır ad, sivri uçta kırmızı şevron.",
             U.shield(W, H, 3.0), (0, H / 2 - 6.0))
    c.front += fit(lambda R: stack(R, iki=True), (-W / 2 + 4.0, -9.4, W / 2 - 4.0, H / 2 - 10.4))[0]
    c.front += [(rounded(A.polygon([(-8, -13.4), (-5.6, -13.4), (0, -17.8), (5.6, -13.4), (8, -13.4), (0, -19.8)]), 0.3),
                 RED)]
    back_std(c, 0, -1.0, 32)
    return c


def s09():
    body = A.rrect(32.0, 40.0, 10.0, 0, -5.0)
    outline = with_lug(body, (0, 17.0), 6.4, 2.4)
    c = card("09_kumanda", "Araç kumandası", "Araç kumandası biçimi (otomotiv); düğme gibi beyaz halka içinde işaret, altında ad.",
             outline, (0, 18.0))
    c.front += [(A.outline(A.circle(11.6, 0, 1.0, 160), 1.0), WHITE)]
    c.front += place(sk_mark(12.6), 0.0, 1.0)
    c.front += [(ad_sigdir("SAVAŞ", 3.6, 22.0, 0, -14.0)[0], RED), (ad_sigdir("KANLIADA", 3.6, 22.0, 0, -19.8)[0], RED)]
    c.back += [(small("0506 101", 4.4, 0, 4.2, tracking=0.3), WHITE), (small("68 97", 4.4, 0, -2.6, tracking=0.3), WHITE),
               (rule(-10, 10, -7.6), RED)]
    return c


def s10():
    W, H = 50.0, 34.0
    c = card("10_araba_ev", "Araba ve ev", "Üstte tek çizgiyle kırmızı araba, altında işaret ve ad: otomotiv + gayrimenkul.",
             A.rrect(W, H, 4.0), (-W / 2 + 5.5, H / 2 - 5.5))
    c.front += [(car_line().translate((3.4, H / 2 - 12.6)), RED)]
    c.front += fit(line, (-W / 2 + 4.0, -H / 2 + 3.0, W / 2 - 4.0, H / 2 - 14.6))[0]
    back_std(c, 0, -1.0, W - 12)
    return c


def s11():
    head = A.circle(15.0, -10.0, 0, 160)
    blade = A.rect(4.0, -3.4, 23.0, 3.4) + A.rect(14.0, -3.4, 16.6, -7.2) + A.rect(19.0, -3.4, 21.6, -6.0)
    shape = rounded(head + blade, 1.2)
    c = card("11_anahtar", "Ev anahtarı", "Anahtar biçimi; başında işaret, dilinde ad kısaltması SK.",
             shape, (-19.6, 0))
    c.front += place(sk_mark(15.0), -7.6, 0.4)
    c.front += [(ad("SK", 3.4, 15.0, 0.0, tracking=0.6), WHITE)]
    c.back += [(small("0506 101", 3.2, 7.0, 3.4, tracking=0.2), WHITE), (small("68 97", 3.2, 7.0, -2.4, tracking=0.2),
                                                                       WHITE)]          # arka yüzde baş sağda
    return c


def s12():
    H = 36.0
    items = sk_mark(H)
    sil = A.union(*[cs for cs, _ in items]).offset(2.2, J)
    sil = rounded(sil, 1.0).offset(1.6, J).offset(-1.6, J)
    b = sil.bounds()
    lug = (b[0] + 6.4, b[3] - 7.4)                              # sol üst boşluk (S'nin üstü, çatının solu)
    outline = rounded(with_lug(sil, lug, 5.6, 2.0), 0.8).simplify(0.01)   # ardışık ofsetler 37 bin nokta üretiyor
    c = card("12_logo_silueti", "Logo silueti", "Anahtarlığın kendisi logo: kırmızı S ve K, beyaz çatı; antrasit kenar.",
             outline, lug)
    c.front += items
    kb = items[0][0].bounds()                                  # arka yüzde K solda (aynalı): telefon K'nin üstünde
    kx = -(kb[0] + kb[2]) / 2 - 2.2
    c.back += [(small("0506 101", 3.4, kx, -3.2, tracking=0.2), WHITE), (small("68 97", 3.4, kx, -8.6, tracking=0.2),
                                                                         WHITE)]
    return c


def s13():
    W, H = 46.0, 30.0
    c = card("13_kirmizi_govde", "Kırmızı gövde", "Gövde kırmızı; S ve K beyaz, çatı ve ad antrasit.",
             A.rrect(W, H, 5.0), (W / 2 - 5.5, H / 2 - 5.5), body=RED)
    c.front += fit(lambda R: stack(R, ON_RED), (-W / 2 + 3.4, -H / 2 + 3.0, W / 2 - 8.6, H / 2 - 2.6))[0]
    c.back += [(small(PHONE, 3.6, -1.0, 2.8, max_w=W - 9), WHITE), (rule(-15, 13, -1.8), ANT),
               (alt_satir(-1.0, -6.4, W - 12), ANT)]
    return c


def s14():
    W, H = 46.0, 30.0
    c = card("14_beyaz_govde", "Beyaz gövde", "Gövde beyaz; S, K ve ad kırmızı, çatı antrasit; altta antrasit şerit.",
             A.rrect(W, H, 5.0), (W / 2 - 5.5, H / 2 - 5.5), body=WHITE)
    c.front += fit(lambda R: stack(R, LIGHT), (-W / 2 + 3.4, -H / 2 + 5.6, W / 2 - 8.6, H / 2 - 2.6))[0]
    c.front += [(A.rect(-W / 2, -H / 2, W / 2, -H / 2 + 4.2) ^ A.rrect(W, H, 5.0).offset(-1.0, J), ANT)]
    c.back += [(small(PHONE, 3.6, 1.0, 3.2, max_w=W - 9), ANT), (rule(-13, 15, -1.5), RED),
               (alt_satir(1.0, -6.1, W - 12), RED)]
    return c


def s15():
    W, H = 22.0, 50.0
    c = card("15_dikey_etiket", "Dikey etiket", "İnce dikey etiket; üstte işaret, altında alt alta S-A-V-A-Ş.",
             A.rrect(W, H, 5.0), (0, H / 2 - 5.6))
    c.front += place(sk_mark(14.6), 0.0, 10.4)
    for i, ch in enumerate("SAVAŞ"):
        c.front += [(ad(ch, 3.8, 0, -0.2 - i * 5.0), RED)]
    c.back += [(A.union(small("0506", 4.2, 0, 10.0), small("101", 4.2, 0, 3.8), small("68 97", 4.2, 0, -2.4)), WHITE),
               (rule(-7, 7, -8.6), RED)] + place(sk_mark(10.4, pal=DARK), 0.0, -16.8)
    return c


def s16():
    W, H = 32.0, 48.0
    tag = A.rrect(W, H, 7.0)
    hole = (0, H / 2 - 6.4)
    c = card("16_kunye", "Künye", "Künye biçimi; ince beyaz çerçeve, işaret ve iki satır ad. Arkada telefon QR'ı.", tag, hole)
    c.front += [(A.outline(tag, 0.9, inset=1.7) - A.circle(HOLE_R + 3.4, *hole), WHITE)]
    c.front += fit(lambda R: stack(R, iki=True), (-W / 2 + 4.4, -H / 2 + 4.0, W / 2 - 4.4, H / 2 - 12.4))[0]
    back_qr(c, 0, 1.8, 0.98)
    ph, _ = phone_lines(0, -12.0, W - 6.0, 3.6)
    c.back.append((ph, WHITE))
    return c


def s17():
    Ro, Ri = 23.4, 9.0
    c = card("17_halka", "Halka", "Simit biçimi; halka ortadan geçer. Üst yayda SAVAŞ, alt yayda KANLIADA, yanlarda çatı.",
             A.circle(Ro, 0, 0, 220), None, holes=A.circle(Ri, 0, 0, 160))
    rm = (Ro + Ri) / 2
    c.front += [(G.bend(ad("SAVAŞ", 4.2, 0, 0, valign="b", tracking=1.0).translate((0, -2.1)), 0, 0, rm, 90, top=True), RED),
                (G.bend(ad("KANLIADA", 4.0, 0, 0, valign="b", tracking=0.6).translate((0, -2.0)), 0, 0, rm, -90, top=False),
                 RED)]
    roof = lambda x: rounded(A.polygon([(x - 2.4, -0.8), (x, 1.6), (x + 2.4, -0.8), (x + 1.4, -0.8), (x, 0.4),  # noqa: E731
                                        (x - 1.4, -0.8)]), 0.2)
    c.front += [(roof(-rm) + roof(rm), WHITE)]
    c.back += [(G.bend(small(PHONE, 3.3, 0, 0, align="c", tracking=0.25).translate((0, -1.65)), 0, 0, rm - 1.65, 90,
                       top=True), WHITE),
               (G.bend(small("DANIŞMANLIK", 3.0, 0, 0, align="c", tracking=0.8).offset(0.12, J).translate((0, -1.5)), 0, 0, rm + 1.5, -90,
                       top=False), RED)]
    return c


def s18():
    D = 24.0
    rh = rounded(A.polygon([(0, D), (D - 2, 0), (0, -D), (-(D - 2), 0)]), 3.0)
    c = card("18_elmas", "Elmas", "Eşkenar dörtgen gövde; ortada işaret, altında ad.", rh, (0, D - 8.4))
    c.front += place(sk_mark(15.6), 0.0, 1.2)
    a, _ = ad_sigdir("KANLIADA", 3.4, 16.4, 0, -10.8)
    c.front += [(a, RED)]
    c.back += [(small("0506 101", 3.8, 0, 4.4, tracking=0.3), WHITE), (small("68 97", 3.8, 0, -1.4, tracking=0.3), WHITE),
               (rule(-7, 7, -6.6), RED)]
    return c


def s19():
    S = 44.0
    c = card("19_qr_kart", "QR kart", "Kare kart; önde işaret ve ad, arkada telefon QR'ı (okutunca arar) ve numara.",
             A.rrect(S, S, 6.0), (S / 2 - 6.0, S / 2 - 6.0))
    c.front += fit(stack, (-S / 2 + 3.4, -S / 2 + 4.0, S / 2 - 3.4, S / 2 - 11.8))[0]
    back_qr(c, 2.4, 3.2, 1.0, phone_y=-15.0, phone_w=S - 9.0, phone_cap=3.6)
    return c


def s20():
    R = 21.0
    outline = with_lug(A.circle(R, 0, 0, 200), (0, R + 2.3))
    c = card("20_direksiyon", "Direksiyon", "Direksiyon simidi: beyaz simit, göbek halkası ve üç kol; göbekte işaret.",
             outline, (0, R + 2.5))
    rim = A.circle(18.8, 0, 0, 200) - A.circle(15.6, 0, 0, 200)
    hub = A.circle(10.2, 0, -0.6, 160) - A.circle(8.6, 0, -0.6, 160)
    side = A.polygon([(-9.4, 1.4), (-9.4, -4.4), (-16.6, -6.6), (-16.6, 0.4)])
    spokes = side + side.mirror((1, 0)) + A.polygon([(-2.6, -9.6), (2.6, -9.6), (3.2, -16.4), (-3.2, -16.4)])
    c.front += [(rounded(rim + hub + spokes, 0.6), WHITE)]
    c.front += place(sk_mark(12.2), 0.0, -0.4)
    back_std(c, 0, -0.6, 32)
    return c


CONCEPTS = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13, s14, s15, s16, s17, s18, s19, s20]


# ---------------------------------------------------------------- sayfalar

def header(dr, im, W, title, sub):
    dr.rectangle((0, 0, W, 260), fill=ANT)
    for x in range(W - 560, W + 200, 52):                     # çatı eğiminde ince çizgiler
        dr.polygon([(x, 260), (x + 14, 260), (x + 14 + 150, 110), (x + 150, 110)], fill=(66, 69, 75))
    logo = A.fit_into(G.paint(line(10.0), ANT, 14.0, pad=1.0).convert("RGBA"), 760, 130)
    im.paste(logo, (70, 36))
    dr.text((72, 186), title, font=K.fnt(34), fill=(240, 240, 238))
    dr.text((72 + dr.textlength(title, font=K.fnt(34)) + 20, 194), sub, font=K.fnt(24), fill=RED)
    dr.rectangle((0, 256, W, 262), fill=RED)


def customer_pages(concepts, per_page=10, start_page=1, total=20):
    G.header = header                                         # G.customer_pages sayfa başlığını bundan çizer
    G.ORANGE = RED
    G.OUT_DIR = OUT_DIR
    paths = G.customer_pages(concepts, per_page, start_page, total)
    for p in paths:                                           # alt bilgi satırı bu firmaya göre
        im = Image.open(p)
        dr = ImageDraw.Draw(im)
        dr.rectangle((60, 284, 1640, 330), fill=(244, 244, 242))
        dr.text((70, 290), "Antrasit gövde, kırmızı ve beyaz logo · en çok 50 × 50 mm · arka yüzde telefon "
                           "(QR'lılarda okutunca arar)", font=K.fnt(26), fill=(40, 40, 44))
        im.save(p, optimize=True)
    return paths


def build(i):
    c = CONCEPTS[i - 1]()
    c.front, c.back = U.resolve(c.front), U.resolve(c.back)
    issues, wall = G.check(c)
    if getattr(c, "qr", False):
        c.qr_read = G.qr_check(c)
        if c.qr_read != QR_TEXT:
            issues.append(f"QR okunamadı ({c.qr_read})")
    G.sheet(c, os.path.join(OUT_DIR, c.key + ".png"), i)
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
                   title="SAVAŞ KANLIADA – ANAHTARLIK ÖNERİLERİ (ön yüz · QR'lılarda arka yüz)")
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
            pages = pool.map(build_pages, [("genel", todo), (1, todo[:10]), (2, todo[10:])])
            pdf = [Image.open(p).convert("RGB") for p in pages[1] + pages[2]]
            pdf[0].save(os.path.join(OUT_DIR, "musteri_katalog.pdf"), save_all=True, append_images=pdf[1:],
                        resolution=200)
    print("sorunlu:", bad)


if __name__ == "__main__":
    main()
