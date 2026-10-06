"""AUTO FIRAT TUYGUN: kurumsal / minimalist anahtarlık konseptleri (yalnız görsel).

Önceki anahtarlıklar müşteriye kalabalık geldi. Bu konseptlerde:
  * ortak bir marka sistemi: FT monogramı + belirgin "AUTO" (Outfit ExtraBold, isimle aynı boyda ya da
    rozet içinde) + Sora SemiBold isim; galeri anahtarlığı olduğu için AUTO her ön yüzde var
  * baskıya uygun ölçüler: isim en az 4,2 mm, küçük yazılar en az 3,0 mm (çizgiler ~0,6 mm+)
  * ön yüzde yalnız logo, AUTO ve isim, bol boşluk; telefon ve şehir ARKA yüzde
  * mat siyah zemin + tek vurgu (altın / gümüş / beyaz); yazılar yüzeyle aynı hizada (gömme)

Seçilen konsept daha sonra baskıya hazır 3MF'e çevrilecek (ön yüz üst katmanlarda, arka yüz
tablaya bakan ilk katmanlarda renkli basılır).

Çıktı : anahtarlik/kurumsal/marka.png, <konsept>.png, hepsi.png (marka + 1-6), hepsi_2.png (7-16), ozet.png

Kullanım:
  python3 scripts/anahtarlik_konsept.py
"""
import os
import sys

import manifold3d as m3
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "anahtarlik", "kurumsal")
NAME, PHONE, CITY = A.NAME, A.PHONE, A.CITY

# renkler (ekran tonu) ve önerilen Bambu filamenti
BLACK = (34, 34, 36)
WHITE = (236, 236, 230)
GOLD = (196, 160, 82)
SILVER = (172, 175, 180)
NAVY = (26, 44, 82)
FILAMENT = {BLACK: "siyah – PLA Matte Charcoal", WHITE: "beyaz – PLA Matte Ivory White",
            GOLD: "altın – PLA Basic Gold", SILVER: "gümüş – PLA Basic Silver", NAVY: "lacivert – PLA Matte Dark Blue"}

THICK, INLAY = 3.6, 0.6          # gövde kalınlığı, gömme renk derinliği (mm)
UI = os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf")


def sora():
    return A.Font("Sora-SemiBold.ttf")


def outfit():
    """Küçük yazılar (telefon, AUTO, şehir): ExtraBold, 3 mm'de bile çizgiler ~0,6 mm."""
    return A.Font("Outfit-ExtraBold.ttf")


# ---------------------------------------------------------------- marka

def ft_mark(h, cx=0.0, cy=0.0, slant=10.0):
    """FT monogramı: F ve T üst çizgiyi paylaşır, hız hissi için hafif eğik. h: yükseklik (mm)."""
    u = h / 14.0
    parts = [A.rect(0, 11.5, 16.5, 14), A.rect(0, 0, 2.5, 14), A.rect(0, 5.9, 8.0, 8.4), A.rect(10.0, 0, 12.5, 14)]
    cs = A.union(*parts).translate((-8.25, -7.0)).scale((u, u))
    return A.shear(cs, slant).translate((cx, cy))


def wordmark(cap, x, y, align="l"):
    return sora().text(NAME, cap, x, y, align=align, tracking=cap * 0.12)


def descriptor(text, cap, x, y, align="l"):
    return outfit().text(text, cap, x, y, align=align, tracking=cap * 0.45)


def auto_word(cap, x, y, align="l"):
    """Belirgin AUTO: Outfit ExtraBold, isimle aynı boyda ya da daha büyük, geniş harf aralıklı."""
    return outfit().text("AUTO", cap, x, y, align=align, tracking=cap * 0.2)


def auto_badge(cap, x, y, align="l"):
    """AUTO rozeti: renkli dikdörtgen içinde oyma harfler (harfler alttaki renkte görünür)."""
    word = auto_word(cap, 0, 0, align="c")
    x0, _, x1, _ = word.bounds()
    h, w = cap * 2.0, (x1 - x0) + cap * 2.0
    dx = {"l": w / 2, "c": 0.0, "r": -w / 2}[align]
    return (A.rrect(w, h, h * 0.28) - word).translate((x + dx, y))


# ---------------------------------------------------------------- konsept

class Concept:
    def __init__(self, key, title, desc, outline, holes, body=BLACK):
        self.key, self.title, self.desc = key, title, desc
        self.outline, self.holes, self.body = outline, holes, body
        self.front, self.back = [], []          # [(şekil, renk)]; arka yüz arkadan okunur hâlde çizilir

    def colours(self):
        cols = [self.body] + [c for _, c in self.front + self.back]
        return list(dict.fromkeys(cols))

    def size(self):
        x0, y0, x1, y1 = self.outline.bounds()
        return x1 - x0, y1 - y0

    def solids(self):
        shape = self.outline - self.holes
        steps, ch = 3, 0.6
        body = shape.extrude(THICK)
        rings = []
        for k in range(steps):                   # alt ve üst kenarda katmanlı pah
            inset = ch * (steps - k) / steps
            ring = shape - shape.offset(-inset, m3.JoinType.Round)
            rings.append(ring.extrude(0.2).translate((0, 0, k * 0.2 - (0.1 if k == 0 else 0))))
            rings.append(ring.extrude(0.2).translate((0, 0, THICK - (k + 1) * 0.2 + (0.1 if k == 0 else 0))))
        body = body - m3.Manifold.batch_boolean(rings, m3.OpType.Add)
        keep = shape.offset(-1.0, m3.JoinType.Round) - self.holes.offset(0.8, m3.JoinType.Round)
        parts, pockets = [], []
        for cs, col in self.front:
            s = (cs ^ keep).extrude(INLAY).translate((0, 0, THICK - INLAY))
            parts.append((s, col))
            pockets.append(s)
        for cs, col in self.back:
            s = (cs.mirror((1, 0)) ^ keep).extrude(INLAY)
            parts.append((s, col))
            pockets.append(s)
        if pockets:
            body = body - m3.Manifold.batch_boolean(pockets, m3.OpType.Add)
        return [(body, self.body)] + parts


def k1_kapsul():
    W, H = 96.0, 26.0
    c = Concept("1_kapsul", "Kapsül", "Hap biçimi; solda altın FT, yanında iki satır: büyük altın AUTO, altında beyaz isim.",
                A.rrect(W, H, H / 2), A.circle(2.6, -W / 2 + 9.5, 0))
    c.front += [(ft_mark(12.0, -W / 2 + 26.0, 0), GOLD),
                (auto_word(4.8, -W / 2 + 37.2, 3.6), GOLD),
                (wordmark(4.6, -W / 2 + 37.0, -3.8), WHITE)]
    c.back += [(outfit().text(PHONE, 4.4, 6.0, 2.2, tracking=0.5), WHITE),
               (descriptor(CITY, 3.0, 6.0, -5.2, align="c"), GOLD)]
    return c


def k2_logo_kare():
    S = 42.0
    c = Concept("2_logo_kare", "Logo kare", "Uygulama ikonu gibi yuvarlak kare; önde büyük altın FT, altında beyaz AUTO.",
                A.rrect(S, S, 11.0), A.circle(2.5, -S / 2 + 7.5, S / 2 - 7.5))
    c.front += [(ft_mark(16.0, 1.2, 3.6), GOLD), (auto_word(4.4, 0, -11.6, align="c"), WHITE)]
    c.back += [(sora().text("FIRAT", 4.6, 0, 10.0, tracking=0.5), WHITE),
               (sora().text("TUYGUN", 4.6, 0, 3.0, tracking=0.5), WHITE),
               (A.rect(-9.0, -2.6, 9.0, -1.4), GOLD),
               (outfit().text(PHONE, outfit().fit_cap(PHONE, 3.6, 32.0, 0.3), 0, -7.6, tracking=0.3), WHITE),
               (descriptor(CITY, 3.0, 0, -13.4, align="c"), GOLD)]
    return c


def k3_madalyon():
    R = 20.0
    outline = (A.circle(R, 0, 0, 160) + A.circle(6.0, 0, R + 2.2)).offset(1.4, m3.JoinType.Round).offset(-1.4, m3.JoinType.Round)
    c = Concept("3_madalyon", "Madalyon", "Beyaz yuvarlak madalyon; ince siyah halka içinde siyah FT ve AUTO.",
                outline, A.circle(2.5, 0, R + 2.4), body=WHITE)
    c.front += [(A.outline(A.circle(R, 0, 0, 160), 1.1, inset=2.2), BLACK), (ft_mark(12.5, 0.6, 3.4), BLACK),
                (auto_word(4.2, 0, -8.8, align="c"), BLACK)]
    c.back += [(sora().text("FIRAT", 4.4, 0, 8.4, tracking=0.5), BLACK),
               (sora().text("TUYGUN", 4.4, 0, 1.8, tracking=0.5), BLACK),
               (outfit().text(PHONE, outfit().fit_cap(PHONE, 3.4, 33.0, 0.2), 0, -4.6, tracking=0.2), BLACK),
               (descriptor(CITY, 3.0, 0, -10.6, align="c"), BLACK)]
    return c


def k4_deri_etiket():
    body = A.rrect(30.0, 46.0, 7.0, 0, -6.0)
    neck = A.polygon([(-15, 14), (15, 14), (9, 25), (-9, 25)])
    loop = A.circle(8.4, 0, 25.5)
    outline = (body + neck + loop).offset(2.0, m3.JoinType.Round).offset(-2.0, m3.JoinType.Round)
    c = Concept("4_deri_etiket", "Deri etiket formu", "Bayi anahtarlığı biçimi; gümüş FT ve AUTO, altında iki satır beyaz isim.",
                outline, A.rrect(9.0, 5.2, 2.6, 0, 26.6))
    c.front += [(ft_mark(12.0, 0.5, 6.4), SILVER),
                (auto_word(4.4, 0, -4.8, align="c"), SILVER),
                (sora().text("FIRAT", 4.4, 0, -12.6, tracking=0.4), WHITE),
                (sora().text("TUYGUN", 4.4, 0, -19.4, tracking=0.4), WHITE)]
    c.back += [(outfit().text("0535 278", 3.8, 0, 4.0, tracking=0.4), WHITE),
               (outfit().text("35 29", 3.8, 0, -2.4, tracking=0.4), WHITE),
               (descriptor(CITY, 3.0, 0, -10.0, align="c"), SILVER)]
    return c


def k5_ince_bar():
    W, H = 18.0, 86.0
    c = Concept("5_ince_bar", "İnce bar", "Gümüş ince dikey bar; dikey AUTO ve isim (yan yana), üstte küçük FT.",
                A.rrect(W, H, W / 2), A.circle(2.6, 0, H / 2 - 8.0), body=SILVER)
    y0 = -H / 2 + 5.0                                   # yazıların başladığı alt nokta
    c.front += [(ft_mark(7.0, 0.3, H / 2 - 19.5), BLACK),
                (auto_word(4.0, 0, 0).rotate(90).translate((-3.4, y0)), BLACK),
                (wordmark(4.6, 0, 0).rotate(90).translate((2.6, y0)), BLACK)]
    c.back += [(outfit().text(PHONE, 3.8, 0, 0, tracking=0.5).rotate(90).translate((-2.0, -8.0)), BLACK),
               (descriptor(CITY, 3.0, 0, 0, align="c").rotate(90).translate((4.0, -8.0)), BLACK)]
    return c


def k6_tek_cizgi():
    W, H = 82.0, 28.0
    c = Concept("6_tek_cizgi", "Tek çizgi", "Dikdörtgen kart; beyaz isim, altında altın çizgi ve çizginin bittiği yerde AUTO rozeti.",
                A.rrect(W, H, 4.0), A.circle(2.5, W / 2 - 6.5, H / 2 - 6.5))
    badge = auto_badge(3.8, W / 2 - 5.5, -5.6, align="r")
    bx0 = badge.bounds()[0]
    c.front += [(wordmark(5.0, -W / 2 + 5.5, 3.6), WHITE),
                (A.rect(-W / 2 + 5.5, -6.2, bx0 + 1.0, -5.0) + badge, GOLD)]
    c.back += [(outfit().text(PHONE, 4.4, -W / 2 + 5.5, 2.4, align="l", tracking=0.5), WHITE),
               (descriptor(CITY, 3.0, -W / 2 + 5.5, -5.2), GOLD)]
    return c


CONCEPTS = [k1_kapsul, k2_logo_kare, k3_madalyon, k4_deri_etiket, k5_ince_bar, k6_tek_cizgi]

# ---------------------------------------------------------------- ikinci seri (7-16)

def k7_altigen():
    R = 22.0
    hexa = A.polygon([(R * np.cos(np.radians(90 + 60 * i)), R * np.sin(np.radians(90 + 60 * i))) for i in range(6)])
    outline = hexa.offset(-2.5, m3.JoinType.Round).offset(2.5, m3.JoinType.Round)
    c = Concept("7_altigen", "Altıgen", "Sivri tepeli altıgen; ortada altın FT, altında beyaz AUTO, tepede delik.",
                outline, A.circle(2.5, 0, R - 7.0))
    c.front += [(ft_mark(13.0, 0.6, 1.2), GOLD), (auto_word(4.2, 0, -10.6, align="c"), WHITE)]
    c.back += [(sora().text("FIRAT", 4.4, 0, 7.8, tracking=0.5), WHITE),
               (sora().text("TUYGUN", 4.4, 0, 1.4, tracking=0.5), WHITE),
               (outfit().text(PHONE, outfit().fit_cap(PHONE, 3.6, 33.0, 0.2), 0, -5.2, tracking=0.2), WHITE),
               (descriptor(CITY, 3.0, 0, -10.8, align="c"), GOLD)]
    return c


def k8_kesik_disk():
    R = 24.0
    outline = (A.circle(R, 0, 0, 180) + A.circle(5.6, 0, R + 2.0)).offset(1.4, m3.JoinType.Round).offset(-1.4, m3.JoinType.Round)
    cut = ft_mark(13.0, 0.6, 3.4)
    c = Concept("8_kesik_disk", "Kesik disk", "Siyah disk; FT işareti boydan boya kesik (içinden görünür), altında altın AUTO.",
                outline, A.circle(2.5, 0, R + 2.4) + cut)
    c.front += [(auto_word(4.6, 0, -10.4, align="c"), GOLD)]
    c.back += [(sora().arc(NAME, 3.6, 0, 0, R - 2.0, -90.0, top=False, tracking=0.5), WHITE),
               (outfit().arc(PHONE, 3.4, 0, 0, R - 7.6, -90.0, top=False, tracking=0.25), WHITE)]
    return c


def k9_kose_serit():
    W, H = 66.0, 40.0
    card = A.rrect(W, H, 6.0)
    band = A.polygon([(-10, 48), (-2, 48), (56, -10), (48, -10)])          # x + y = 38 … 46: sağ üst köşe
    c = Concept("9_kose_serit", "Köşe şerit", "Kart; sağ üst köşede çapraz altın şerit, solda büyük altın AUTO ve beyaz isim.",
                card, A.circle(2.5, -W / 2 + 7.0, H / 2 - 7.0))
    c.front += [(band ^ card, GOLD),
                (auto_word(5.0, -W / 2 + 6.2, -2.2), GOLD),
                (wordmark(4.6, -W / 2 + 6.0, -10.2), WHITE)]
    c.back += [(outfit().text(PHONE, 4.4, -W / 2 + 6.0, -4.0, align="l", tracking=0.5), WHITE),
               (descriptor(CITY, 3.0, -W / 2 + 6.0, -11.0), GOLD)]
    return c


def k10_damla():
    drop = A.circle(18.0, 0, -6.0, 160) + A.polygon([(-16.3, 1.6), (0, 27.0), (16.3, 1.6)])
    outline = drop.offset(-2.0, m3.JoinType.Round).offset(2.0, m3.JoinType.Round)
    c = Concept("10_damla", "Damla", "Altın damla biçimi; yuvarlak kısımda siyah FT ve AUTO, sivri uçta delik.",
                outline, A.circle(2.5, 0, 18.0), body=GOLD)
    c.front += [(ft_mark(12.0, 0.6, -1.6), BLACK), (auto_word(4.2, 0, -14.2, align="c"), BLACK)]
    c.back += [(sora().text("FIRAT", 4.4, 0, 4.6, tracking=0.5), BLACK),
               (sora().text("TUYGUN", 4.4, 0, -2.0, tracking=0.5), BLACK),
               (outfit().text(PHONE, outfit().fit_cap(PHONE, 3.6, 31.0, 0.2), 0, -8.6, tracking=0.2), BLACK),
               (descriptor(CITY, 3.0, 0, -14.6, align="c"), BLACK)]
    return c


def k11_ikiye_bolunmus():
    R = 21.0
    disc = A.circle(R, 0, 0, 180)
    outline = (disc + A.circle(5.6, 0, R + 2.0)).offset(1.4, m3.JoinType.Round).offset(-1.4, m3.JoinType.Round)
    top = disc ^ A.rect(-30, 1.0, 30, 30)
    c = Concept("11_ikiye_bolunmus", "İkiye bölünmüş", "Yuvarlak; üst yarı altın (siyah FT), alt yarı siyah (büyük beyaz AUTO).",
                outline, A.circle(2.5, 0, R + 2.4))
    ft = ft_mark(11.0, 0.5, 10.4)
    c.front += [(top - ft, GOLD), (ft, BLACK), (auto_word(5.2, 0, -8.4, align="c"), WHITE)]
    c.back += [(sora().text("FIRAT", 4.2, 0, 9.0, tracking=0.5), WHITE),
               (sora().text("TUYGUN", 4.2, 0, 2.6, tracking=0.5), WHITE),
               (outfit().text(PHONE, outfit().fit_cap(PHONE, 3.4, 33.0, 0.2), 0, -4.2, tracking=0.2), WHITE),
               (descriptor(CITY, 3.0, 0, -10.0, align="c"), GOLD)]
    return c


def k12_kunye():
    W, H = 34.0, 54.0
    tag = A.rrect(W, H, 7.0)
    c = Concept("12_kunye", "Künye", "Gümüş askeri künye biçimi; siyah kenar çizgisi, FT, iki satır isim ve siyah AUTO rozeti.",
                tag, A.circle(2.6, 0, H / 2 - 6.5), body=SILVER)
    c.front += [(A.outline(tag, 1.0, inset=1.6) - A.circle(2.6 + 3.0, 0, H / 2 - 6.5), BLACK),
                (ft_mark(10.0, 0.4, 9.4), BLACK),
                (sora().text("FIRAT", 4.2, 0, -1.4, tracking=0.3), BLACK),
                (sora().text("TUYGUN", 4.2, 0, -7.8, tracking=0.3), BLACK),
                (auto_badge(3.6, 0, -17.0, align="c"), BLACK)]
    c.back += [(outfit().text("0535 278", 3.8, 0, 6.0, tracking=0.4), BLACK),
               (outfit().text("35 29", 3.8, 0, -0.4, tracking=0.4), BLACK),
               (descriptor(CITY, 3.0, 0, -8.0, align="c"), BLACK)]
    return c


def k13_halka():
    Ro, Ri = 24.0, 11.5
    c = Concept("13_halka", "Halka", "Simit biçimi; anahtarlık ortadan geçer; halkanın üstünde kavisli isim, altında büyük AUTO.",
                A.circle(Ro, 0, 0, 200), A.circle(Ri, 0, 0, 160))
    rm = (Ro + Ri) / 2
    c.front += [(sora().arc(NAME, 4.0, 0, 0, rm - 2.0, 90.0, top=True, tracking=0.6), WHITE),
                (outfit().arc("AUTO", 4.8, 0, 0, rm + 2.4, -90.0, top=False, tracking=1.6), GOLD)]
    c.back += [(outfit().arc(PHONE, 3.4, 0, 0, rm - 1.7, 90.0, top=True, tracking=0.3), WHITE),
               (outfit().arc(CITY, 3.0, 0, 0, rm + 1.5, -90.0, top=False, tracking=1.2), GOLD)]
    return c


def k14_pencereli():
    W, H = 64.0, 36.0
    window = A.rrect(11.0, 22.0, 4.0, W / 2 - 11.5, 0)
    c = Concept("14_pencereli", "Pencereli kart", "Sağda halkanın geçtiği yuvarlak pencere; solda altın FT + AUTO, altında iki satır isim.",
                A.rrect(W, H, 6.0), window)
    x0 = -W / 2 + 6.0
    c.front += [(ft_mark(9.0, x0 + 6.6, 8.6), GOLD),
                (auto_word(4.6, x0 + 15.6, 8.6), GOLD),
                (sora().text("FIRAT", 4.6, x0, -0.8, align="l", tracking=0.5), WHITE),
                (sora().text("TUYGUN", 4.6, x0, -8.0, align="l", tracking=0.5), WHITE)]
    c.back += [(outfit().text(PHONE, outfit().fit_cap(PHONE, 4.0, 38.0, 0.4), 0, 0, align="l", tracking=0.4).translate((-W / 2 + 21.0, 2.0)), WHITE),
               (descriptor(CITY, 3.0, -W / 2 + 21.0, -5.0), GOLD)]
    return c


def k15_logo_silueti():
    mark = ft_mark(38.0, 0, 0)
    mx0, my0, mx1, my1 = mark.bounds()
    ring = A.circle(6.0, mx1 + 2.0, my1 - 3.4)
    outline = (mark.offset(3.4, m3.JoinType.Round) + ring).offset(1.0, m3.JoinType.Round).offset(-1.0, m3.JoinType.Round)
    c = Concept("15_logo_silueti", "Logo silueti", "Anahtarlığın kendisi FT logosu; altın FT, T'nin gövdesinde oyma dikey AUTO.",
                outline, A.circle(2.6, mx1 + 2.4, my1 - 3.4))
    u = 38.0 / 14.0
    t10 = np.tan(np.radians(10.0))
    # T gövdesi (eğik): ortası x = 3.0u (eğimsiz), y -7u … 4.5u; AUTO ortada, aşağıdan yukarı okunur
    auto = A.shear(auto_word(4.0, 0, 0, align="c").rotate(90), 10.0)
    c.front += [(mark - auto.translate((3.0 * u - 1.25 * u * t10, -1.25 * u)), GOLD)]
    # arka: logonun kollarına yazılar (arkadan bakınca sağ-sol yer değiştirir)
    bar_y = my1 - 1.25 * u                          # üst çizginin ortası
    phone = A.shear(outfit().text(PHONE, 3.0, 0, 0, tracking=0.2).rotate(90), -10.0)
    py = -4.3                                       # F gövdesinde, üst çizgideki isme değmeden
    c.back += [(sora().text(NAME, 3.8, 0, 0, tracking=0.3).translate((-0.5 - bar_y * t10, bar_y)), WHITE),
               (phone.translate((7.0 * u - py * t10, py)), WHITE)]
    return c


def k16_lacivert():
    W, H = 60.0, 38.0
    c = Concept("16_lacivert", "Lacivert kart", "Lacivert kart; ortada gümüş FT, beyaz isim, gümüş AUTO rozeti (ortalanmış dizilim).",
                A.rrect(W, H, 7.0), A.circle(2.5, -W / 2 + 7.0, H / 2 - 7.0), body=NAVY)
    c.front += [(ft_mark(9.0, 0.4, 10.6), SILVER),
                (wordmark(4.6, 0, 0.2, align="c"), WHITE),
                (auto_badge(3.6, 0, -9.8, align="c"), SILVER)]
    c.back += [(outfit().text(PHONE, 4.4, 0, 2.6, tracking=0.5), WHITE),
               (descriptor(CITY, 3.0, 0, -4.6, align="c"), SILVER)]
    return c


CONCEPTS2 = [k7_altigen, k8_kesik_disk, k9_kose_serit, k10_damla, k11_ikiye_bolunmus, k12_kunye, k13_halka,
             k14_pencereli, k15_logo_silueti, k16_lacivert]


# ---------------------------------------------------------------- çizim

def mesh_parts(c):
    return [(*A.mesh_arrays(m), col) for m, col in c.solids()]


def fnt(size):
    return ImageFont.truetype(UI, size)


def panel(dr, box, fill=(226, 228, 232)):
    dr.rounded_rectangle(box, 26, fill=fill)


def paste_center(canvas, im, box):
    x0, y0, x1, y1 = box
    canvas.paste(im, (x0 + (x1 - x0 - im.width) // 2, y0 + (y1 - y0 - im.height) // 2), im)


def concept_sheet(c, path):
    parts = mesh_parts(c)
    views = [("ÖN YÜZ", rotation(0, 0)), ("ARKA YÜZ", rotation(180, 180)), ("PERSPEKTİF", rotation(-22, -50))]
    W, H = 1500, 640
    canvas = Image.new("RGB", (W, H), (244, 245, 247))
    dr = ImageDraw.Draw(canvas)
    dr.text((40, 26), c.title.upper(), fill=(24, 26, 30), font=fnt(34))
    dr.text((40, 72), c.desc, fill=(96, 100, 110), font=fnt(20))
    w, h = c.size()
    dr.text((W - 40 - dr.textlength(f"{w:.0f} × {h:.0f} × {THICK:.1f} mm", font=fnt(20)), 34),
            f"{w:.0f} × {h:.0f} × {THICK:.1f} mm", fill=(96, 100, 110), font=fnt(20))
    for i, (label, R) in enumerate(views):
        box = (40 + i * 480, 120, 40 + i * 480 + 460, 120 + 440)
        panel(dr, box)
        im = A.fit_into(render(parts, 1000, R, margin=0.02), 380, 340)
        paste_center(canvas, im, (box[0], box[1] + 30, box[2], box[3]))
        dr.text((box[0] + 22, box[1] + 18), label, fill=(120, 124, 134), font=fnt(17))
    x = 40
    for col in c.colours():
        dr.rounded_rectangle((x, 586, x + 22, 608), 6, fill=col, outline=(150, 154, 162), width=1)
        dr.text((x + 32, 586), FILAMENT[col], fill=(70, 74, 84), font=fnt(18))
        x += 60 + dr.textlength(FILAMENT[col], font=fnt(18))
    canvas.save(path)
    return canvas


def brand_sheet(path):
    """Marka sistemi: yatay logo (koyu ve açık zemin), işaret + AUTO rozeti."""
    W, H = 1500, 560
    canvas = Image.new("RGB", (W, H), (244, 245, 247))
    dr = ImageDraw.Draw(canvas)
    dr.text((40, 26), "MARKA SİSTEMİ", fill=(24, 26, 30), font=fnt(34))
    dr.text((40, 72), "FT monogramı + büyük AUTO (Outfit ExtraBold, altın) + Sora SemiBold isim. "
                      "Küçük yüzeylerde AUTO rozeti. Tüm anahtarlıklarda aynı.",
            fill=(96, 100, 110), font=fnt(20))
    k = 9.0

    def draw_cs(items, bg, box):
        x0, y0, x1, y1 = box
        dr.rounded_rectangle(box, 26, fill=bg)
        allc = A.union(*[cs for cs, _ in items])
        bx0, by0, bx1, by1 = allc.bounds()
        s = min((x1 - x0 - 80) / ((bx1 - bx0) * k), (y1 - y0 - 80) / ((by1 - by0) * k), 1.6) * k
        ox = (x0 + x1) / 2 - (bx0 + bx1) / 2 * s
        oy = (y0 + y1) / 2 + (by0 + by1) / 2 * s
        for cs, col in items:                        # tek-çift kuralıyla doldur (oyma harfler, delikler)
            mask = Image.new("1", canvas.size, 0)
            for p in cs.to_polygons():
                layer = Image.new("1", canvas.size, 0)
                ImageDraw.Draw(layer).polygon([(ox + u * s, oy - v * s) for u, v in p], fill=1)
                mask = ImageChops.logical_xor(mask, layer)
            canvas.paste(col, mask=mask)

    lock = [(ft_mark(14.0, 0, 0), GOLD), (auto_word(5.4, 12.7, 3.5), GOLD), (wordmark(5.0, 12.5, -3.9), WHITE)]
    draw_cs(lock, BLACK, (40, 120, 760, 520))
    lock_l = [(ft_mark(14.0, 0, 0), BLACK), (auto_word(5.4, 12.7, 3.5), GOLD), (wordmark(5.0, 12.5, -3.9), BLACK)]
    draw_cs(lock_l, (250, 250, 248), (780, 120, 1180, 520))
    draw_cs([(ft_mark(14.0, 0, 5.0), GOLD), (auto_badge(3.6, 0, -10.0, align="c"), GOLD)], BLACK, (1200, 120, 1460, 520))
    canvas.save(path)
    return canvas


def stack(sheets, path):
    W = max(s.width for s in sheets)
    sheet = Image.new("RGB", (W, sum(s.height for s in sheets) + 20 * (len(sheets) - 1)), (255, 255, 255))
    y = 0
    for s in sheets:
        sheet.paste(s, (0, y))
        y += s.height + 20
    sheet.save(path)


def overview(concepts, path, cols=4):
    """Tüm konseptler tek sayfada: perspektif görünüş + numara + ad."""
    cw, ch = 360, 330
    rows = (len(concepts) + cols - 1) // cols
    W, H = cols * cw + (cols + 1) * 20, rows * ch + (rows + 1) * 20 + 90
    canvas = Image.new("RGB", (W, H), (244, 245, 247))
    dr = ImageDraw.Draw(canvas)
    dr.text((24, 24), "AUTO FIRAT TUYGUN – ANAHTARLIK KONSEPTLERİ", fill=(24, 26, 30), font=fnt(32))
    for i, c in enumerate(concepts):
        x, y = 20 + (i % cols) * (cw + 20), 90 + (i // cols) * (ch + 20)
        panel(dr, (x, y, x + cw, y + ch))
        im = A.fit_into(render(mesh_parts(c), 800, rotation(-22, -50), margin=0.02), cw - 60, ch - 90)
        paste_center(canvas, im, (x, y + 10, x + cw, y + ch - 50))
        dr.text((x + 18, y + ch - 44), c.title, fill=(30, 33, 40), font=fnt(22))
        w, h = c.size()
        dr.text((x + cw - 18 - dr.textlength(f"{w:.0f}×{h:.0f} mm", font=fnt(16)), y + ch - 40), f"{w:.0f}×{h:.0f} mm",
                fill=(110, 114, 124), font=fnt(16))
        dr.text((x + 18, y + 14), str(i + 1), fill=(150, 154, 162), font=fnt(22))
    canvas.save(path)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    only = sys.argv[1:]
    sheets1 = [brand_sheet(os.path.join(OUT_DIR, "marka.png"))]
    sheets2, all_c = [], []
    for group, sheets in ((CONCEPTS, sheets1), (CONCEPTS2, sheets2)):
        for fn in group:
            c = fn()
            all_c.append(c)
            if only and not any(o in c.key for o in only):
                continue
            sheets.append(concept_sheet(c, os.path.join(OUT_DIR, c.key + ".png")))
            print(c.key, "%.0f × %.0f mm" % c.size())
    if not only:
        stack(sheets1, os.path.join(OUT_DIR, "hepsi.png"))
        stack(sheets2, os.path.join(OUT_DIR, "hepsi_2.png"))
        overview(all_c, os.path.join(OUT_DIR, "ozet.png"))


if __name__ == "__main__":
    main()
