"""UZAR OTO LASTİK (Antalya) anahtarlık konseptleri – siyah, kırmızı, beyaz; en çok 50 × 50 mm.

25 görsel öneri (yalnız görsel; seçilen sonra Bambu Lab X2D dosyasına çevrilir). Ön yüz: UZAR, OTO LASTİK ve
yarış aracı boyamasındaki gibi keskin kırmızı şeritler / lastik motifleri. Arka yüz: telefon ve ANTALYA. QR'lı
6 tasarımda arka yüzde telefon QR'ı (TEL:+905426116987, QR sürüm 1, 21 × 21, hata düzeltme M); arka yüz tablada
basılacağı için QR ilk katmanlarda beyaz zemin üstünde siyah kare olur. Her QR görüntüden okunarak doğrulanır.

Çıktı : anahtarlik/uzar/*.png, anahtarlik/uzar/hepsi.png

Kullanım:
  pip install segno zxing-cpp
  python3 scripts/uzar_anahtarlik.py [anahtar ...]
"""
import os
import sys

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import anahtarlik_konsept as K  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "anahtarlik", "uzar")
NAME, KIND, CITY = "UZAR", "OTO LASTİK", "ANTALYA"
PHONE = "0542 611 69 87"
QR_TEXT = "TEL:+905426116987"
BLACK, WHITE = K.BLACK, K.WHITE
RED = (206, 28, 38)
K.FILAMENT.update({BLACK: "siyah", WHITE: "beyaz", RED: "kırmızı"})
J = m3.JoinType.Round
HOLE_R = 2.2                                    # Ø4,4 delik (çelik halka)


# ---------------------------------------------------------------- yazı ve motifler

def heavy():
    return A.font("plate")                      # Barlow Condensed Black: kalın, dar, Türkçe harfli


def bold():
    return A.font("barlow")                     # Barlow Condensed ExtraBold


def wide():
    return A.Font("Lexend-ExtraBold.ttf")       # geniş, modern


def text(f, s, cap, x, y, align="c", tracking=0.0, max_w=None):
    if max_w:
        cap = f.fit_cap(s, cap, max_w, tracking)
    return f.text(s, cap, x, y, align=align, tracking=tracking)


def name(cap, x, y, align="c", max_w=None, f=None, tracking=None):
    f = f or heavy()
    return text(f, NAME, cap, x, y, align, cap * 0.06 if tracking is None else tracking, max_w)


def kind(cap, x, y, align="c", max_w=None, tracking=None):
    return text(bold(), KIND, cap, x, y, align, cap * 0.16 if tracking is None else tracking, max_w)


def phone(cap, x, y, align="c", max_w=None):
    return text(heavy(), PHONE, cap, x, y, align, cap * 0.05, max_w)


def city(cap, x, y, align="c", max_w=None):
    return text(bold(), CITY, cap, x, y, align, cap * 0.22, max_w)


def poly(pts):
    return A.polygon(pts)


def slash(x0, w, slope=1.2, y0=-40.0, y1=40.0):
    """Eğik şerit: alt kenarı x0'dan başlayan, `w` genişlikte, eğimi `slope` (x/y)."""
    return poly([(x0 + slope * y0, y0), (x0 + w + slope * y0, y0), (x0 + w + slope * y1, y1), (x0 + slope * y1, y1)])


def shard(pts):
    """Keskin boyama parçası (yarış aracındaki gibi)."""
    return poly(pts)


def tread_band(x0, x1, y0, y1, pitch=4.0):
    """Lastik dişi bandı: ok biçimli bloklar."""
    h = y1 - y0
    blocks = []
    x = x0
    while x < x1:
        blocks.append(poly([(x, y0), (x + pitch * 0.5, y0), (x + pitch, y0 + h / 2), (x + pitch * 0.5, y1),
                            (x, y1), (x + pitch * 0.5, y0 + h / 2)]))
        x += pitch * 1.25
    return A.union(*blocks) ^ A.rect(x0, y0, x1, y1)


def tire(r, cx=0.0, cy=0.0, teeth=22, depth=1.3):
    """Lastik simgesi: dişli dış lastik halkası (döner: lastik, jant) – jant 5 kollu."""
    pts = []
    for i in range(teeth * 2):
        a0, a1 = 2 * np.pi * i / (teeth * 2), 2 * np.pi * (i + 1) / (teeth * 2)
        rr = r if i % 2 == 0 else r - depth
        pts += [(cx + rr * np.cos(a), cy + rr * np.sin(a)) for a in np.linspace(a0, a1, 4)[:-1]]
    tyre = poly(pts) - A.circle(r * 0.62, cx, cy)
    rim = A.circle(r * 0.54, cx, cy) - A.circle(r * 0.42, cx, cy)
    spokes = A.union(*[poly([(cx + r * 0.12 * np.cos(a + 0.5), cy + r * 0.12 * np.sin(a + 0.5)),
                             (cx + r * 0.45 * np.cos(a + 0.12), cy + r * 0.45 * np.sin(a + 0.12)),
                             (cx + r * 0.45 * np.cos(a - 0.12), cy + r * 0.45 * np.sin(a - 0.12)),
                             (cx + r * 0.12 * np.cos(a - 0.5), cy + r * 0.12 * np.sin(a - 0.5))])
                       for a in np.radians(np.arange(5) * 72 + 90)])
    hub = A.circle(r * 0.14, cx, cy)
    return tyre, rim + spokes + hub


def gear_outline(R, teeth=28, depth=1.4):
    """Lastik biçimli dış hat: kenarı dişli daire."""
    pts = []
    for i in range(teeth * 2):
        a0, a1 = 2 * np.pi * i / (teeth * 2), 2 * np.pi * (i + 1) / (teeth * 2)
        rr = R if i % 2 == 0 else R - depth
        pts += [(rr * np.cos(a), rr * np.sin(a)) for a in np.linspace(a0, a1, 5)[:-1]]
    return poly(pts).offset(-0.4, J).offset(0.4, J)


def hexagon(af, r=3.0):
    """Bijon somunu: düz kenarlar arası `af`, köşeler yuvarlatılmış."""
    R = af / np.sqrt(3)
    pts = [(R * np.cos(np.radians(60 * i)), R * np.sin(np.radians(60 * i))) for i in range(6)]
    return poly(pts).offset(-r, J).offset(r, J)


def shield(w, h, r=3.0):
    return poly([(-w / 2, h / 2), (w / 2, h / 2), (w / 2, -h / 2 + w * 0.42), (0, -h / 2),
                 (-w / 2, -h / 2 + w * 0.42)]).offset(-r, J).offset(r, J)


def parallelogram(w, h, skew, r=3.0):
    return poly([(-w / 2 + skew, h / 2), (w / 2, h / 2), (w / 2 - skew, -h / 2), (-w / 2, -h / 2)]).offset(-r, J).offset(r, J)


def cut_tag(w, h, cut, r=3.0):
    return poly([(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2 - cut), (w / 2 - cut, h / 2), (-w / 2, h / 2)]
                ).offset(-r, J).offset(r, J)


def checker(x0, y0, n, s, tri=True):
    """Damalı bayrak köşesi: (x0, y0) sol üst, n × n kare, `s` kenar; tri = yalnız üçgen yarısı."""
    sq = [A.rect(x0 + i * s, y0 - (j + 1) * s, x0 + (i + 1) * s, y0 - j * s)
          for i in range(n) for j in range(n) if (i + j) % 2 == 0 and (not tri or i + j < n)]
    return A.union(*sq)


def chevrons(x0, cy, h, n, pitch, w):
    out = []
    for i in range(n):
        x = x0 + i * pitch
        out.append(poly([(x, cy + h / 2), (x + w, cy + h / 2), (x + w + h / 2, cy), (x + w, cy - h / 2),
                         (x, cy - h / 2), (x + h / 2, cy)]))
    return A.union(*out)


def qr(cx, cy, module=1.1, quiet=2):
    """Telefon QR'ı: beyaz zemin (sessiz bölge dahil) eksi siyah kareler; siyah kareler gövdenin rengi."""
    import segno
    m = np.array(segno.make(QR_TEXT, error="m", micro=False).matrix, dtype=bool)
    n = m.shape[0]
    size = (n + 2 * quiet) * module
    x0, y1 = cx - size / 2 + quiet * module, cy + size / 2 - quiet * module
    runs = []
    for r in range(n):                                      # satır satır ardışık siyah kareleri birleştir
        c = 0
        while c < n:
            if m[r, c]:
                c1 = c
                while c1 < n and m[r, c1]:
                    c1 += 1
                runs.append(A.rect(x0 + c * module, y1 - (r + 1) * module, x0 + c1 * module, y1 - r * module))
                c = c1
            else:
                c += 1
    dark = A.union(*runs)
    return A.rect(cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2) - dark, size


# ---------------------------------------------------------------- standart arka yüzler

def back_std(c, w, h, y=0.0, red_line=True):
    c.back += [(phone(4.6, 0, y + 2.6, max_w=w - 8.0), WHITE), (city(3.0, 0, y - 4.2, max_w=w - 14.0), RED)]
    if red_line:
        c.back.append((A.rect(-w / 2 + 6.0, y - 0.6, w / 2 - 6.0, y - 0.0), RED))


def back_qr(c, cx=0.0, cy=3.0, module=1.1, text_y=None, text_w=40.0):
    q, size = qr(cx, cy, module)
    c.back.append((q, WHITE))
    if text_y is not None:
        c.back.append((phone(3.8, cx, text_y, max_w=text_w), WHITE))
    c.qr = True
    return size


def card(key, title, desc, outline, hole_xy, body=BLACK):
    return K.Concept(key, title, desc, outline, A.circle(HOLE_R, *hole_xy), body)


# ---------------------------------------------------------------- 25 tasarım

def u01():
    W, H = 50.0, 28.0
    c = card("01_kesik_serit", "Kesik şerit", "İki keskin kırmızı şerit soldan geçer; büyük beyaz UZAR, altında OTO LASTİK.",
             A.rrect(W, H, 4.0), (-W / 2 + 5.5, H / 2 - 5.5))
    c.front += [(slash(-17.0, 3.2, 0.55), RED), (slash(-11.8, 1.6, 0.55), RED),
                (name(11.0, 7.0, 3.0, max_w=30.0), WHITE), (kind(3.4, 7.0, -7.6, max_w=30.0), RED)]
    back_std(c, W, H)
    return c


def u02():
    W, H = 50.0, 28.0
    c = card("02_yaris_boyamasi", "Yarış boyaması", "Fotoğraftaki araç gibi: köşeden açılan kırmızı keskin parçalar, sağda isim.",
             A.rrect(W, H, 4.0), (-W / 2 + 5.5, -H / 2 + 5.5))
    c.front += [(shard([(-30, 20), (-6, 20), (-24, -2), (-30, -2)]), RED),
                (shard([(-30, -5), (-26, -5), (-12, 20), (-15.5, 20)]), RED),
                (shard([(-10, 20), (-7.5, 20), (-22, -20), (-24.5, -20)]), WHITE),
                (name(10.0, 9.0, 3.4, max_w=26.0), WHITE), (kind(3.2, 9.0, -6.8, max_w=26.0), WHITE)]
    back_std(c, W, H)
    return c


def u03():
    W, H = 50.0, 30.0
    c = card("03_lastik_izi", "Lastik izi", "Alt kenar boyunca beyaz lastik dişi bandı; kırmızı UZAR, beyaz OTO LASTİK.",
             A.rrect(W, H, 4.0), (-W / 2 + 5.5, H / 2 - 5.5))
    c.front += [(tread_band(-W / 2, W / 2, -H / 2 + 2.6, -H / 2 + 7.6, 4.2), WHITE),
                (name(10.5, 3.0, 5.2, max_w=34.0), RED), (kind(3.2, 3.0, -3.6, max_w=34.0), WHITE)]
    back_std(c, W, H)
    return c


def u04():
    R = 22.0
    c = card("04_lastik_madalyon", "Lastik madalyon", "Lastik biçimli dişli kenar; kırmızı jant halkası, ortada UZAR.",
             gear_outline(R), (0, R - 6.0))
    c.front += [(A.circle(R - 3.0) - A.circle(R - 4.6), RED), (name(9.5, 0, -1.0, max_w=26.0), WHITE),
                (kind(2.8, 0, -9.0, max_w=22.0), RED)]
    c.back += [(phone(4.0, 0, 1.6, max_w=32.0), WHITE), (city(2.8, 0, -5.0, max_w=22.0), RED),
               (A.circle(R - 3.0) - A.circle(R - 4.0), RED)]
    return c


def u05():
    c = card("05_bijon_somunu", "Bijon somunu", "Altıgen somun biçimi; kırmızı iç halka, beyaz UZAR.",
             hexagon(44.0), (0, 13.5))
    c.front += [(A.circle(17.5) - A.circle(15.8), RED), (name(10.0, 0, -1.4, max_w=24.0), WHITE),
                (kind(2.8, 0, -8.8, max_w=20.0), RED)]
    c.back += [(phone(4.2, 0, 0.8, max_w=34.0), WHITE), (city(2.8, 0, -6.0, max_w=22.0), RED)]
    return c


def u06():
    W, H = 50.0, 24.0
    c = card("06_hiz_oku", "Hız oku", "Eğik paralelkenar; arkada uzayan kırmızı hız çizgileri, beyaz UZAR.",
             parallelogram(W, H, 7.0), (W / 2 - 8.0, 0))
    c.front += [(A.rect(-30, 4.0, -6, 5.4), RED), (A.rect(-30, 0.2, -10, 1.6), RED), (A.rect(-30, -3.6, -14, -2.2), RED),
                (name(9.5, -1.0, 1.6, max_w=22.0), WHITE), (kind(2.8, -1.0, -6.6, max_w=22.0), RED)]
    c.front = [c.front[3], c.front[4]] + c.front[:3]
    c.front[2:] = [(cs - A.rect(-12, -12, 30, 12), col) for cs, col in c.front[2:]]
    c.back += [(phone(4.2, 3.5, 2.0, max_w=29.0), WHITE), (city(2.8, 3.5, -5.0, max_w=20.0), RED)]
    return c


def u07():
    W, H = 50.0, 28.0
    c = card("07_kirmizi_govde", "Kırmızı gövde", "Kırmızı gövde, ortadan geçen siyah keskin bant; beyaz isim.",
             A.rrect(W, H, 4.0), (-W / 2 + 5.5, H / 2 - 5.5), body=RED)
    c.front += [(slash(-8.0, 24.0, 0.45), BLACK), (name(10.5, 5.0, 2.6, max_w=26.0), WHITE),
                (kind(3.2, 5.0, -7.4, max_w=26.0), WHITE)]
    c.back += [(phone(4.6, 0, 2.6, max_w=42.0), WHITE), (city(3.0, 0, -4.2, max_w=24.0), BLACK)]
    return c


def u08():
    W, H = 50.0, 28.0
    c = card("08_beyaz_govde", "Beyaz gövde", "Beyaz gövde, köşede siyah-kırmızı şerit; siyah UZAR, kırmızı OTO LASTİK.",
             A.rrect(W, H, 4.0), (W / 2 - 5.5, H / 2 - 5.5), body=WHITE)
    c.front += [(shard([(-30, -20), (-16, -20), (-30, -4)]), RED), (shard([(-30, -2), (-13.5, -20), (-11, -20), (-30, 1)]), BLACK),
                (name(11.0, 2.0, 2.6, max_w=30.0), BLACK), (kind(3.2, 2.0, -7.6, max_w=30.0), RED)]
    c.back += [(phone(4.6, 0, 2.6, max_w=42.0), BLACK), (city(3.0, 0, -4.2, max_w=24.0), RED)]
    return c


def u09():
    c = card("09_kalkan", "Kalkan", "Kalkan biçimi; üstte kırmızı V şeridi, ortada büyük UZAR.",
             shield(40.0, 46.0), (0, 17.5))
    c.front += [(poly([(-20, 13), (0, 3.5), (20, 13), (20, 9.5), (0, 0), (-20, 9.5)]), RED),
                (name(10.0, 0, -6.0, max_w=26.0), WHITE), (kind(2.8, 0, -13.6, max_w=20.0), RED)]
    c.back += [(phone(3.8, 0, -2.0, max_w=32.0), WHITE), (city(2.6, 0, -8.0, max_w=20.0), RED)]
    return c


def u10():
    W, H = 50.0, 30.0
    c = card("10_yaris_plakasi", "Yarış numarası", "Yarış aracı numara alanı gibi beyaz oval; içinde siyah UZAR, üstte kırmızı bant.",
             A.rrect(W, H, 5.0), (-W / 2 + 5.5, H / 2 - 5.5))
    c.front += [(A.rrect(36.0, 17.0, 8.5, 3.0, -2.0), WHITE), (name(10.0, 3.0, -1.4, max_w=28.0), BLACK),
                (A.rect(-12, 8.6, 25, 10.4), RED), (kind(2.8, 3.0, -12.0, max_w=24.0), RED)]
    back_std(c, W, H)
    return c


def u11():
    W, H = 50.0, 28.0
    c = card("11_damali_kose", "Damalı köşe", "Sağ üstte damalı bayrak köşesi, alttan kırmızı şerit; beyaz UZAR.",
             A.rrect(W, H, 4.0), (-W / 2 + 5.5, H / 2 - 5.5))
    c.front += [(checker(W / 2 - 13.5, H / 2 - 1.0, 5, 2.4), WHITE), (A.rect(-W / 2, -H / 2 + 3.0, W / 2, -H / 2 + 4.6), RED),
                (name(10.5, -2.0, 1.8, max_w=28.0), WHITE), (kind(3.0, -2.0, -6.6, max_w=26.0), RED)]
    back_std(c, W, H, y=-1.2, red_line=False)
    return c


def u12():
    R = 22.0
    c = card("12_jant", "Jant", "Yuvarlak; kırmızı 5 kollu jant ve beyaz lastik, isim arka yüzde büyük.",
             A.circle(R), (0, R - 5.4))
    tyre, rim = tire(R - 1.5)
    c.front += [(tyre, WHITE), (rim, RED)]
    c.back += [(name(9.5, 0, 4.0, max_w=28.0), WHITE), (kind(2.8, 0, -3.4, max_w=24.0), RED),
               (phone(3.6, 0, -9.6, max_w=30.0), WHITE)]
    return c


def u13():
    W, H = 50.0, 28.0
    c = card("13_capraz_bolunmus", "Çapraz bölünmüş", "Gövde çapraz ikiye: sol kırmızı, sağ siyah, arada beyaz ince ayraç.",
             A.rrect(W, H, 4.0), (-W / 2 + 5.5, H / 2 - 5.5))
    c.front += [(poly([(-30, 20), (-9.0, 20), (-17.0, -20), (-30, -20)]), RED),
                (poly([(-9.0, 20), (-7.6, 20), (-15.6, -20), (-17.0, -20)]), WHITE),
                (name(10.5, 7.5, 2.6, max_w=24.0), WHITE), (kind(3.0, 7.5, -7.4, max_w=24.0), RED)]
    back_std(c, W, H)
    return c


def u14():
    W, H = 50.0, 26.0
    c = card("14_sevron", "Şevron", "Sağa bakan üç kırmızı ok; solda UZAR. Hız ve yön hissi.",
             A.rrect(W, H, 4.0), (-W / 2 + 5.5, H / 2 - 5.5))
    c.front += [(chevrons(8.0, -1.0, 13.0, 3, 5.2, 2.0), RED), (name(9.0, -7.0, 0.6, max_w=19.0), WHITE),
                (kind(2.8, -7.0, -7.0, max_w=19.0), WHITE)]
    back_std(c, W, H, y=-1.8, red_line=False)
    return c


def u15():
    W, H = 50.0, 22.0
    c = card("15_kapsul", "Kapsül", "İnce hap biçimi; solda kırmızı eğik kesim, ortada UZAR · OTO LASTİK tek satır.",
             A.rrect(W, H, H / 2), (-W / 2 + 6.0, 0))
    c.front += [(slash(-12.0, 2.6, 0.4), RED), (name(9.0, 6.5, 2.0, max_w=26.0), WHITE), (kind(2.6, 6.5, -5.8, max_w=26.0), RED)]
    c.back += [(phone(4.2, -3.0, 1.6, max_w=30.0), WHITE), (city(2.6, -3.0, -4.6, max_w=20.0), RED)]
    return c


def u16():
    W, H = 46.0, 30.0
    c = card("16_kesik_kose_etiket", "Kesik köşe etiket", "Sağ üst köşesi kesik yarış etiketi; kesik boyunca kırmızı şerit.",
             cut_tag(W, H, 9.0), (-W / 2 + 5.5, H / 2 - 5.5))
    c.front += [(poly([(W / 2 - 13.5, H / 2 + 2), (W / 2 + 2, H / 2 - 13.5), (W / 2 + 2, H / 2 - 16.5), (W / 2 - 16.5, H / 2 + 2)]), RED),
                (name(10.5, -2.0, 0.0, max_w=28.0), WHITE), (kind(3.0, -2.0, -9.0, max_w=26.0), RED)]
    back_std(c, W, H)
    return c


def u17():
    W, H = 50.0, 28.0
    c = card("17_lastik_simgesi", "Lastik simgesi", "Solda beyaz lastik + kırmızı jant simgesi, sağda iki satır isim.",
             A.rrect(W, H, 4.0), (W / 2 - 5.5, H / 2 - 5.5))
    tyre, rim = tire(10.5, -W / 2 + 13.0, 0)
    c.front += [(tyre, WHITE), (rim, RED), (name(10.0, 8.0, 1.8, max_w=18.0), WHITE), (kind(2.8, 8.0, -7.0, max_w=18.0), RED)]
    back_std(c, W, H)
    return c


def u18():
    W, H = 50.0, 24.0
    c = card("18_minimal", "Minimal", "En sade ve en ucuz: siyah gövde, beyaz UZAR, altında ince kırmızı çizgi.",
             A.rrect(W, H, 4.0), (-W / 2 + 5.5, 0))
    nm = name(11.0, 4.0, 2.0, max_w=30.0, f=wide())
    x0, y0, x1, _ = nm.bounds()
    c.front += [(nm, WHITE), (A.rect(x0, y0 - 3.4, x1, y0 - 2.2), RED), (kind(2.6, 4.0, y0 - 6.6, max_w=30.0), WHITE)]
    c.back += [(phone(4.4, -2.5, 1.6, max_w=32.0), WHITE), (city(2.8, -2.5, -4.8, max_w=22.0), RED)]
    return c


def u19():
    W, H = 50.0, 32.0
    c = card("19_serit_qr", "Kesik şerit + QR", "Ön yüz kesik şerit; arka yüzde telefon QR'ı ve numara. Okut, ara.",
             A.rrect(W, H, 4.0), (-W / 2 + 5.5, H / 2 - 5.5))
    c.front += [(slash(-17.0, 3.2, 0.55), RED), (slash(-11.8, 1.6, 0.55), RED),
                (name(11.0, 7.0, 3.4, max_w=30.0), WHITE), (kind(3.4, 7.0, -7.6, max_w=30.0), RED)]
    back_qr(c, cx=-8.0, cy=0.0, module=1.12)              # arka yüzde delik sağ üstte görünür: QR solda
    c.back += [(text(heavy(), "ARA", 3.4, 14.5, 3.6), RED), (text(heavy(), "0542", 3.0, 14.5, -1.8), WHITE),
               (text(heavy(), "611 69 87", 3.0, 14.5, -6.4, max_w=13.0), WHITE)]
    return c


def u20():
    S = 46.0
    c = card("20_kare_qr", "Kare + QR", "Kare; ön yüzde lastik simgesi ve UZAR, arka yüzde büyük QR ve telefon.",
             A.rrect(S, S, 5.0), (-S / 2 + 5.5, S / 2 - 5.5))
    tyre, rim = tire(10.0, 0, 7.0)
    c.front += [(tyre, WHITE), (rim, RED), (name(9.0, 0, -9.0, max_w=30.0), WHITE), (kind(2.8, 0, -16.4, max_w=24.0), RED)]
    back_qr(c, cx=0.0, cy=2.6, module=1.15, text_y=-16.4, text_w=34.0)
    return c


def u21():
    R = 24.0
    c = card("21_lastik_qr", "Lastik + QR", "Lastik biçimli dişli kenar; arka yüzün ortasında QR.",
             gear_outline(R), (0, R - 6.0))
    c.front += [(A.circle(R - 3.0) - A.circle(R - 4.6), RED), (name(10.0, 0, -1.0, max_w=28.0), WHITE),
                (kind(3.0, 0, -9.4, max_w=24.0), RED)]
    back_qr(c, cx=0.0, cy=-1.6, module=1.02)
    return c


def u22():
    c = card("22_somun_qr", "Bijon somunu + QR", "Altıgen somun; ön yüzde isim ve telefon, arka yüzde QR.",
             hexagon(43.0), (18.3, 0))
    c.front += [(A.circle(15.6, -1.5, 0) - A.circle(14.0, -1.5, 0), RED), (name(9.5, -1.5, 3.0, max_w=20.0), WHITE),
                (kind(2.6, -1.5, -4.4, max_w=18.0), RED), (phone(2.6, -1.5, -9.2, max_w=18.0), WHITE)]
    back_qr(c, cx=2.0, cy=0.0, module=1.0)
    return c


def u23():
    W, H = 50.0, 30.0
    c = card("23_onde_qr", "Önde QR", "QR ön yüzde, solda; sağda UZAR. (Arka yüz QR'ı daha keskin basılır.)",
             A.rrect(W, H, 4.0), (W / 2 - 5.0, -H / 2 + 5.0))
    q, size = qr(-W / 2 + 15.0, 0.0, 1.05, 2)
    c.front += [(q, WHITE), (name(9.5, 12.5, 4.0, max_w=18.0), WHITE), (kind(2.6, 12.5, -3.4, max_w=18.0), RED),
                (A.rect(5.0, -8.6, 20.0, -7.4), RED)]
    c.back += [(phone(4.6, 0, 2.6, max_w=42.0), WHITE), (city(3.0, 0, -4.2, max_w=24.0), RED)]
    c.qr = True
    return c


def u24():
    W, H = 50.0, 34.0
    c = card("24_lastik_izi_qr", "Lastik izi + QR", "Ön yüzde lastik dişi bandı; arka yüzde QR ve yanında telefon.",
             A.rrect(W, H, 4.0), (-W / 2 + 5.5, H / 2 - 5.5))
    c.front += [(tread_band(-W / 2, W / 2, -H / 2 + 2.6, -H / 2 + 7.6, 4.2), WHITE),
                (name(12.0, 2.0, 6.4, max_w=34.0), RED), (kind(3.4, 2.0, -3.2, max_w=34.0), WHITE)]
    back_qr(c, cx=-9.0, cy=0.0, module=1.12)              # arka yüzde delik sağ üstte görünür: QR solda
    c.back += [(text(heavy(), "0542", 3.2, 14.0, 2.6), WHITE), (text(heavy(), "611 69 87", 3.2, 14.0, -2.4, max_w=13.5), WHITE),
               (city(2.4, 14.0, -7.6, max_w=13.0), RED)]
    return c


def u25():
    W, H = 50.0, 28.0
    c = card("25_iki_ton", "İki ton", "Üst yarı kırmızı, alt yarı siyah, ortadan beyaz ince çizgi; isim ikisinin üstünde.",
             A.rrect(W, H, 4.0), (-W / 2 + 5.5, H / 2 - 5.5))
    c.front += [(A.rect(-30, 2.4, 30, 20), RED), (A.rect(-30, 1.0, 30, 2.4), WHITE),
                (name(9.5, 4.0, 7.2, max_w=30.0), WHITE), (kind(3.2, 4.0, -5.6, max_w=30.0), WHITE)]
    back_std(c, W, H)
    return c


CONCEPTS = [u01, u02, u03, u04, u05, u06, u07, u08, u09, u10, u11, u12, u13, u14, u15, u16, u17, u18, u19, u20,
            u21, u22, u23, u24, u25]


# ---------------------------------------------------------------- QR doğrulama ve sayfalar

def resolve(items):
    """Aynı yüzdeki renkli alanlar: sonra gelen öncekinin üstüne yazar (örtüşme kalmaz)."""
    out, taken = [], A.empty()
    for cs, col in reversed(items):
        part = cs - taken
        taken = taken + cs
        if part.area() > 0.05:
            out.append((part, col))
    return out[::-1]


def qr_check(c):
    """QR'ı içeren yüzü render edip okur; okunan metni döner (okunamazsa None)."""
    import zxingcpp
    parts = K.mesh_parts(c)
    R = rotation(0, 0) if "onde" in c.key else rotation(180, 180)
    im = render(parts, 900, R, light=False, margin=0.05).convert("L")
    bg = Image.new("L", im.size, 255)
    bg.paste(im, (0, 0), render(parts, 900, R, light=False, margin=0.05).split()[-1])
    res = zxingcpp.read_barcodes(bg)
    return res[0].text if res else None


def sheet(c, path, i):
    title = c.title
    c.title = f"{i:02d}  " + title.replace("i", "İ")
    canvas = K.concept_sheet(c, path)
    c.title = title
    dr = ImageDraw.Draw(canvas)
    if getattr(c, "qr", False):
        txt = getattr(c, "qr_read", None)
        dr.text((1060, 586), f"QR okundu: {txt}" if txt else "QR OKUNAMADI", fill=(22, 120, 60) if txt else (200, 30, 30),
                font=K.fnt(18))
    canvas.save(path)
    return canvas


def overview(concepts, path, cols=5):
    cw, ch = 300, 300
    rows = (len(concepts) + cols - 1) // cols
    W, H = cols * cw + (cols + 1) * 18, rows * ch + (rows + 1) * 18 + 90
    canvas = Image.new("RGB", (W, H), (244, 245, 247))
    dr = ImageDraw.Draw(canvas)
    dr.text((24, 24), "UZAR OTO LASTİK – ANAHTARLIK ÖNERİLERİ (ön yüz · QR'lılarda arka yüz)", fill=(24, 26, 30),
            font=K.fnt(30))
    for i, c in enumerate(concepts):
        x, y = 18 + (i % cols) * (cw + 18), 90 + (i // cols) * (ch + 18)
        K.panel(dr, (x, y, x + cw, y + ch))
        parts = K.mesh_parts(c)
        im = A.fit_into(render(parts, 700, rotation(-22, -50), margin=0.02), cw - 50, ch - 100)
        K.paste_center(canvas, im, (x, y + 10, x + cw, y + ch - 60))
        dr.text((x + 14, y + ch - 46), c.title, fill=(30, 33, 40), font=K.fnt(20))
        w, h = c.size()
        tag = f"{w:.0f}×{h:.0f} mm" + ("  · QR" if getattr(c, "qr", False) else "")
        dr.text((x + 14, y + ch - 22), tag, fill=(200, 30, 38) if getattr(c, "qr", False) else (110, 114, 124),
                font=K.fnt(15))
        dr.text((x + 14, y + 10), f"{i + 1:02d}", fill=(150, 154, 162), font=K.fnt(20))
    canvas.save(path)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    only = sys.argv[1:]
    concepts = []
    for i, fn in enumerate(CONCEPTS, 1):
        c = fn()
        if only and not any(o in c.key for o in only):
            continue
        c.front, c.back = resolve(c.front), resolve(c.back)
        w, h = c.size()
        assert w <= 50.01 and h <= 50.01, (c.key, w, h)
        if getattr(c, "qr", False):
            c.qr_read = qr_check(c)
        sheet(c, os.path.join(OUT_DIR, c.key + ".png"), i)
        concepts.append(c)
        hole = c.holes.bounds()
        wall = min(abs(b) for b in (hole[0] - c.outline.bounds()[0], c.outline.bounds()[2] - hole[2],
                                    hole[1] - c.outline.bounds()[1], c.outline.bounds()[3] - hole[3]))
        print(f"{c.key:24s} {w:4.1f} × {h:4.1f} mm  renk: {len(c.colours())}  delik kenara {wall:.1f} mm"
              + (f"  QR: {c.qr_read}" if getattr(c, "qr", False) else ""))
    if not only:
        overview(concepts, os.path.join(OUT_DIR, "hepsi.png"))


if __name__ == "__main__":
    main()
