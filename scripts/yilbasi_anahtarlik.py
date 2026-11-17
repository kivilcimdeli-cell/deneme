"""BOYDE yılbaşı anahtarlıkları: tombul, tatlı 3D figürler (15 model), desteksiz; tepede halka.

Fotoğraftaki örgü yılbaşı figürleri (geyik, Noel Baba, çam, kardan adam...) tarzında, az ayrıntılı ve sevimli.
Desteksiz basım için figürler sırtı düz, önü tombul: tablaya sırt üstü yatar, her parça tabladan başlar ve yukarı doğru
yuvarlanarak incelir (tombul kubbe: hiçbir katman alttakinden taşmaz). Göz, burun, düğme gibi ayrıntılar alttaki
yüzeyi 0,8 mm kabarık izler. Halka tepede, sırtla aynı düzlemde (3 mm kalın, Ø4 mm delik).

Renkler: altın, yeşil, kırmızı, beyaz, kahverengi (karamel); gözler koyu kahve (moka), Noel Baba'nın yüzü açık kahve
(latte). Her model en çok 5 renk.

Çıktı: boyde_labs/yilbasi_anahtarlik/<kod>.png (önden ve yandan), katalog.pdf ve sayfa jpg'leri.
Seçilen 5 model için X2D 3MF ayrıca yazılacak (müşteri seçince).
Kullanım: python3 scripts/yilbasi_anahtarlik.py
"""
import math
import os
import sys

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)
from atolye.tasarim import ortak as O  # noqa: E402

A = O.A
J = O.J
m3 = O.m3
OUT = os.path.join(KOK, "boyde_labs", "yilbasi_anahtarlik")

# ---------------------------------------------------------------- renkler
GOLD, GREEN, RED, WHITE, MOKA, NUDE = O.GOLD, O.GREEN, O.RED, O.WHITE, O.MOKA, O.NUDE
KAHVE = 51
O.RENK[KAHVE] = ("kahverengi", "#8B5A3C", (150, 98, 64), "#8B5A3C")      # PLA Basic Brown benzeri (karamel)
O.AD[KAHVE], O.TON[KAHVE] = "kahverengi", (150, 98, 64)
O._kaydet()

# ---------------------------------------------------------------- 2B şekiller


def C(r, x=0.0, y=0.0):
    return A.circle(r, x, y, 96)


def E(rx, ry, x=0.0, y=0.0):
    return A.circle(1.0, 0, 0, 96).scale((rx, ry)).translate((x, y))


def RR(w, h, r, x=0.0, y=0.0):
    return A.rrect(w, h, r, x, y)


def P(pts, yuvarla=0.0):
    cs = A.polygon(pts)
    return cs.offset(-yuvarla, J).offset(yuvarla, J) if yuvarla else cs


def ucgen(w, h, x, y, yuvarla=1.6):
    """Tabanı (x, y)'de, tepesi yukarıda yuvarlatılmış üçgen."""
    return P([(x - w / 2, y), (x + w / 2, y), (x, y + h)], yuvarla)


def yay(r_dis, r_ic, a0, a1, x=0.0, y=0.0):
    """Halka dilimi (gülümseme, şeker baston kıvrımı): a0..a1 derece."""
    n = 40
    dis = [(x + r_dis * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
            y + r_dis * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    ic = [(x + r_ic * math.cos(math.radians(a1 - (a1 - a0) * i / n)),
           y + r_ic * math.sin(math.radians(a1 - (a1 - a0) * i / n))) for i in range(n + 1)]
    return A.polygon(dis + ic)


def yildiz(r_dis, r_ic, x=0.0, y=0.0, yuvarla=0.8, kol=5):
    pts = []
    for i in range(kol * 2):
        a = math.radians(90 + i * 180 / kol)
        r = r_dis if i % 2 == 0 else r_ic
        pts.append((x + r * math.cos(a), y + r * math.sin(a)))
    return P(pts, yuvarla)


def birlesim(*cs):
    return A.union(*cs)


# ---------------------------------------------------------------- 3B: tombul parçalar


def tombul(cs, h, r=None, dz=0.2):
    """Tabladan h yüksekliğe tombul kubbe: duvar dik çıkar, üstte r yarıçaplı yuvarlanarak içe kıvrılır. Katmanlar
    yukarı doğru hep küçülür: desteksiz basılır."""
    r = min(h, r if r is not None else h * 0.85)
    katlar, z = [], 0.0
    while z < h - 1e-6:
        z1 = min(h, z + dz)
        u = z1 - (h - r)
        ice = 0.0 if u <= 0 else r - math.sqrt(max(0.0, r * r - u * u))
        dilim = cs.offset(-ice, J) if ice > 0 else cs
        if dilim.area() > 0.05:
            katlar.append(dilim.extrude(z1 - z + 0.01).translate((0, 0, z)))
        z = z1
    return m3.Manifold.batch_boolean(katlar, m3.OpType.Add)


def _sutun(cs):
    return cs.extrude(80.0).translate((0, 0, -1.0))


class Figur:
    """Parçalar sırayla eklenir; sonra gelen kendi izdüşümünü (sütununu) öncekilerden alır."""

    def __init__(self, kod, ad, aciklama=""):
        self.kod, self.ad, self.aciklama = kod, ad, aciklama
        self.parcalar = []                                  # [(ad, Manifold, renk)]
        self._halka = None

    def _al(self, cs):
        s = _sutun(cs)
        self.parcalar = [(n, m - s, c) for n, m, c in self.parcalar]

    def birlik(self):
        return m3.Manifold.batch_boolean([m for _, m, _ in self.parcalar], m3.OpType.Add)

    def tombul(self, ad, cs, h, renk, r=None):
        self._al(cs)
        self.parcalar.append((ad, tombul(cs, h, r), renk))
        return self

    def kapla(self, ad, cs, renk, t=0.8):
        """Alttaki yüzeyi t mm kabarık izleyen ayrıntı (göz, burun, düğme, desen)."""
        u = self.birlik()
        d = _sutun(cs) ^ (u + u.translate((0, 0, t)))
        self._al(cs)
        self.parcalar.append((ad, d, renk))
        return self

    def halka(self, x, y, renk, dis=4.4, ic=2.0, kal=3.0, gom=1.8):
        """Tepede anahtarlık halkası: x'te figürün en üst noktasına gom mm gömülür (y yok sayılır, figür bitince
        hesaplanır). Halkanın figürün üstünde kalan kısmı kesilir: figüre yandan kaynar, deliği dışarıda kalır."""
        self._halka = (x, renk, dis, ic, kal, gom)
        return self

    def _halka_parca(self):
        if not self._halka:
            return None
        x, renk, dis, ic, kal, gom = self._halka
        iz = self.birlik().project()
        ust = (iz ^ RR(2.0, 200.0, 0.0, x, 0.0)).bounds()[3]
        y = ust + dis - gom
        return ("halka", ((C(dis, x, y) - C(ic, x, y)) - iz).extrude(kal), renk)

    def katilar(self):
        """Renk başına birleşik katılar (3MF: renk başına bir parça), halka dahil."""
        out = {}
        h = self._halka_parca()
        for _, m, c in self.parcalar + ([h] if h else []):
            if m.volume() > 1e-3:
                out[c] = out[c] + m if c in out else m
        return [(f"{O.AD[c]}", m, c) for c, m in out.items()]


def goz(f, x, y, r=1.25, renk=MOKA):
    f.kapla("göz", C(r, x, y), renk).kapla("göz", C(r, -x, y), renk)
    return f


# ---------------------------------------------------------------- 15 model (y: aşağıdan yukarı; tepe ~+21)

def y01_noel_baba():
    f = Figur("Y01", "Noel Baba", "Kırmızı şapka, beyaz ponpon ve tombul sakal")
    f.halka(0, 24.0, WHITE)
    f.tombul("yüz", C(11.5, 0, 2.0), 8.0, NUDE)
    f.tombul("şapka", P([(-12.5, 6.0), (12.5, 6.0), (7.0, 17.0), (0.5, 21.5), (-7.0, 16.5)], 2.5), 9.0, RED)
    f.tombul("şapka kenarı", RR(27.0, 5.6, 2.8, 0, 6.5), 9.6, WHITE)
    f.tombul("ponpon", C(3.6, 1.0, 21.0), 9.2, WHITE)
    f.tombul("sakal", birlesim(E(13.0, 9.0, 0, -6.0), C(5.5, -8.0, -1.5), C(5.5, 8.0, -1.5)) - E(6.5, 3.2, 0, 1.6),
             9.0, WHITE)
    f.tombul("bıyık", birlesim(E(4.2, 2.0, -3.2, -0.6), E(4.2, 2.0, 3.2, -0.6)), 9.8, WHITE)
    goz(f, 3.6, 3.0)
    f.kapla("burun", C(1.7, 0, 1.0), RED, 1.0)
    return f


def y02_kardan_adam():
    f = Figur("Y02", "Kardan adam", "Kırmızı bere, yeşil atkı, altın havuç burun")
    f.halka(0, 25.0, RED)
    f.tombul("gövde", C(10.5, 0, -10.0), 8.5, WHITE)
    f.tombul("kafa", C(8.5, 0, 5.5), 9.0, WHITE)
    f.tombul("bere", birlesim(E(8.8, 6.0, 0, 13.0) - RR(30, 10, 0, 0, 5.0)), 9.6, RED)
    f.tombul("bere kenarı", RR(18.5, 3.6, 1.8, 0, 12.0), 10.0, RED)
    f.tombul("ponpon", C(3.0, 0, 20.5), 9.6, RED)
    f.tombul("atkı", RR(18.0, 4.0, 2.0, 0, -1.6), 9.6, GREEN)
    f.tombul("atkı ucu", RR(4.0, 9.0, 1.8, 5.0, -6.0), 9.8, GREEN)
    goz(f, 3.0, 7.0)
    f.kapla("burun", ucgen(2.6, 5.0, 0, 3.0, 0.5).rotate(-90).translate((-0.5, 4.3)), GOLD, 1.2)
    for yy in (-8.0, -13.0):
        f.kapla("düğme", C(1.3, 0, yy), MOKA)
    return f


def y03_geyik():
    f = Figur("Y03", "Geyik", "Altın boynuzlar, kırmızı burun")
    f.halka(0, 25.5, KAHVE)
    sol = birlesim(yay(9.0, 6.2, 95, 175, -3.0, 10.0),                      # kafadan dışa kıvrılan dal
                   RR(2.8, 6.0, 1.4).rotate(20).translate((-6.6, 18.2)),     # üst çatal
                   RR(2.8, 5.0, 1.4).rotate(-35).translate((-11.4, 14.6)))   # yan çatal
    f.tombul("boynuz", sol + sol.mirror((1, 0)), 6.0, GOLD)
    f.tombul("kulak", E(4.5, 2.6, -11.0, 7.0).rotate(0) + E(4.5, 2.6, 11.0, 7.0), 7.0, KAHVE)
    f.tombul("kafa", E(10.5, 11.0, 0, 2.0), 9.0, KAHVE)
    f.tombul("ağız", E(6.5, 4.6, 0, -5.0), 9.8, NUDE)
    goz(f, 4.0, 4.0)
    f.kapla("burun", E(2.6, 2.0, 0, -3.3), RED, 1.2)
    return f


def y04_cam_agaci():
    f = Figur("Y04", "Çam ağacı", "Altın yıldız, kırmızı ve altın süsler, sevimli yüz")
    f.halka(0, 26.0, GOLD)
    f.tombul("gövde", RR(5.0, 6.0, 1.0, 0, -15.5), 4.0, KAHVE)
    f.tombul("dal 1", ucgen(26.0, 14.0, 0, -13.0, 2.0), 7.0, GREEN)
    f.tombul("dal 2", ucgen(21.0, 12.5, 0, -4.5, 2.0), 8.0, GREEN)
    f.tombul("dal 3", ucgen(15.0, 11.0, 0, 3.5, 2.0), 9.0, GREEN)
    f.tombul("yıldız", yildiz(5.4, 2.4, 0, 16.5), 8.0, GOLD)
    goz(f, 2.8, -1.5, 1.15)
    for x, y, c in ((-6.5, -9.0, RED), (6.0, -7.0, GOLD), (-3.5, 5.0, GOLD), (4.0, 1.8, RED), (0.5, -10.0, RED)):
        f.kapla("süs", C(1.4, x, y), c, 1.0)
    return f


def y05_kurabiye_adam():
    f = Figur("Y05", "Zencefilli kurabiye", "Beyaz krema, kırmızı düğmeler")
    f.halka(0, 24.0, KAHVE)
    govde = birlesim(C(7.5, 0, 12.0), RR(13.0, 15.0, 5.0, 0, -1.0), RR(28.0, 6.5, 3.2, 0, 3.0),
                     RR(6.5, 15.0, 3.2, -4.5, -10.0).rotate(0), RR(6.5, 15.0, 3.2, 4.5, -10.0))
    f.tombul("kurabiye", govde.offset(0.6, J).offset(-0.6, J), 7.5, KAHVE)
    goz(f, 2.6, 13.5, 1.15, WHITE)
    f.kapla("gülüş", yay(3.6, 2.6, 200, 340, 0, 11.6), WHITE)
    for x in (-11.5, 11.5):
        f.kapla("krema", RR(1.2, 4.6, 0.6, x, 3.0), WHITE)
    for x in (-4.5, 4.5):
        f.kapla("krema", RR(4.6, 1.2, 0.6, x, -15.0), WHITE)
    for y in (3.5, -1.5):
        f.kapla("düğme", C(1.4, 0, y), RED, 1.0)
    return f


def y06_hediye():
    f = Figur("Y06", "Hediye kutusu", "Kırmızı kutu, altın kurdele ve fiyonk")
    f.halka(0, 22.5, GOLD)
    f.tombul("fiyonk", E(5.5, 3.6, -4.8, 13.0).rotate(0) + E(5.5, 3.6, 4.8, 13.0) + C(2.4, 0, 12.0), 8.5, GOLD)
    f.tombul("kutu", RR(24.0, 20.0, 3.5, 0, -2.0), 8.0, RED)
    f.tombul("kapak", RR(27.0, 6.0, 2.5, 0, 9.0), 8.6, RED)
    f.kapla("kurdele", RR(4.2, 26.0, 0.8, 0, -0.5), GOLD)
    goz(f, 5.0, -2.0)
    f.kapla("gülüş", yay(2.4, 1.3, 205, 335, 0, -3.5), MOKA)
    return f


def y07_can():
    f = Figur("Y07", "Yılbaşı çanı", "Altın çan, kırmızı fiyonk, yeşil yapraklar")
    f.halka(0, 24.0, GOLD)
    can = birlesim(P([(-12.0, -10.0), (12.0, -10.0), (8.0, 4.0), (5.0, 12.0), (-5.0, 12.0), (-8.0, 4.0)], 3.0),
                   RR(28.0, 4.5, 2.2, 0, -10.5))
    f.tombul("çan", can, 8.5, GOLD)
    f.tombul("dil", C(3.0, 0, -14.0), 7.0, GOLD)
    f.tombul("yaprak", E(6.0, 2.8, -5.5, 13.6) + E(6.0, 2.8, 5.5, 13.6), 7.5, GREEN)
    f.tombul("fiyonk", E(3.6, 2.6, -3.0, 14.6) + E(3.6, 2.6, 3.0, 14.6) + C(2.0, 0, 14.3), 9.0, RED)
    goz(f, 3.6, 0.0)
    f.kapla("gülüş", yay(2.4, 1.3, 205, 335, 0, -1.6), MOKA)
    return f


def y08_seker_baston():
    f = Figur("Y08", "Şeker baston", "Beyaz-kırmızı çizgili, yeşil fiyonk")
    f.halka(-5.0, 23.5, RED)
    baston = birlesim(yay(9.5, 3.5, 0, 180, -2.0, 11.0), RR(6.0, 30.0, 3.0, 4.5, -4.0))
    f.tombul("baston", baston, 8.0, WHITE)
    seritler = birlesim(*[RR(60.0, 2.4, 0.0, 0, y).rotate(35) for y in range(-30, 34, 5)])
    f.kapla("çizgi", seritler ^ baston.offset(-0.3, J), RED, 0.6)
    f.tombul("fiyonk", E(4.6, 2.8, 0.6, -2.0) + E(4.6, 2.8, 8.4, -2.0) + C(2.2, 4.5, -2.0), 9.0, GREEN)
    return f


def y09_corap():
    f = Figur("Y09", "Yılbaşı çorabı", "Kırmızı çorap, beyaz kenar, altın yıldız")
    f.halka(-2.0, 25.0, WHITE)
    corap = birlesim(RR(14.0, 24.0, 4.0, -2.0, 5.0), RR(22.0, 11.0, 5.5, 2.0, -8.5))
    f.tombul("çorap", corap, 8.0, RED)
    f.tombul("kenar", RR(18.0, 7.0, 3.0, -2.0, 18.5), 9.0, WHITE)
    f.kapla("yıldız", yildiz(4.2, 1.9, -2.0, 5.0), GOLD, 1.0)
    f.kapla("burun", (C(5.6, 13.0, -8.5) ^ corap.offset(-0.4, J)), WHITE, 0.8)
    return f


def y10_top_susu():
    f = Figur("Y10", "Yılbaşı topu", "Yeşil top, altın başlık, beyaz kar tanesi")
    f.halka(0, 22.5, GOLD)
    f.tombul("başlık", RR(8.0, 5.0, 1.2, 0, 15.5), 7.0, GOLD)
    f.tombul("top", C(13.0, 0, 0), 10.0, GREEN)
    kol = birlesim(*[RR(1.4, 13.0, 0.7).rotate(a) for a in (0, 60, 120)])
    uc = birlesim(*[C(1.2, 6.2 * math.cos(math.radians(a)), 6.2 * math.sin(math.radians(a))) for a in range(0, 360, 60)])
    f.kapla("kar tanesi", (kol + uc).translate((0, -1.0)), WHITE)
    f.kapla("parıltı", E(2.0, 1.2, -6.5, 6.0), WHITE, 0.6)
    return f


def y11_yildiz():
    f = Figur("Y11", "Altın yıldız", "Gülen yüzlü altın yıldız")
    f.halka(0, 22.5, GOLD)
    f.tombul("yıldız", yildiz(16.5, 7.5, 0, -1.0, 2.2), 8.5, GOLD)
    goz(f, 3.2, 0.5)
    f.kapla("gülüş", yay(2.6, 1.4, 205, 335, 0, -1.6), MOKA)
    f.kapla("yanak", C(1.5, -6.0, -2.2) + C(1.5, 6.0, -2.2), RED, 0.6)
    return f


def y12_ayicik():
    f = Figur("Y12", "Ayıcık", "Noel Baba şapkalı kahverengi ayıcık")
    f.halka(4.0, 25.0, WHITE)
    f.tombul("kulak", C(4.2, -9.5, 8.0) + C(4.2, 9.5, 8.0), 7.0, KAHVE)
    f.tombul("kafa", E(11.5, 10.5, 0, 0), 9.0, KAHVE)
    f.tombul("şapka", P([(-11.0, 5.5), (11.0, 5.5), (7.0, 14.0), (3.5, 20.5), (-6.0, 13.5)], 2.0), 9.6, RED)
    f.tombul("şapka kenarı", RR(24.0, 4.6, 2.3, 0, 5.8), 10.0, WHITE)
    f.tombul("ponpon", C(3.0, 4.0, 20.0), 9.8, WHITE)
    f.tombul("ağız", E(5.0, 3.8, 0, -4.6), 9.8, NUDE)
    goz(f, 4.3, 0.2)
    f.kapla("burun", E(1.9, 1.4, 0, -3.4), MOKA, 1.0)
    return f


def y13_kurabiye_ev():
    f = Figur("Y13", "Kurabiye ev", "Beyaz kremalı çatı, kırmızı kapı")
    f.halka(0, 24.0, WHITE)
    f.tombul("ev", RR(22.0, 18.0, 2.0, 0, -6.0), 7.5, KAHVE)
    f.tombul("çatı", P([(-15.0, 2.5), (15.0, 2.5), (0, 18.0)], 2.2), 8.6, WHITE)
    f.kapla("kapı", RR(6.0, 9.0, 2.6, 0, -10.0), RED, 1.0)
    f.kapla("pencere", RR(4.6, 4.6, 1.0, -6.5, -3.0) + RR(4.6, 4.6, 1.0, 6.5, -3.0), GOLD, 0.8)
    for x in (-8.0, -2.8, 2.8, 8.0):
        f.kapla("şeker", C(1.2, x, 5.5), RED if x < 0 else GREEN, 0.8)
    return f


def y14_eldiven():
    f = Figur("Y14", "Eldiven", "Kırmızı eldiven, beyaz kenar, yeşil çam deseni")
    f.halka(0, 25.0, WHITE)
    eld = birlesim(RR(17.0, 24.0, 8.0, 1.0, 4.0), E(4.0, 6.5, -9.5, 2.0).rotate(0))
    f.tombul("eldiven", eld, 8.5, RED)
    f.tombul("kenar", RR(19.0, 6.5, 3.0, 1.0, -10.5), 9.2, WHITE)
    f.kapla("çam", ucgen(8.0, 9.0, 1.0, 0.5, 1.0), GREEN)
    f.kapla("çam yıldızı", C(1.2, 1.0, 11.5), GOLD, 1.0)
    return f


def y15_kutup_ayisi():
    f = Figur("Y15", "Kutup ayısı", "Yeşil bereli, kırmızı ponponlu beyaz ayı")
    f.halka(0, 25.5, RED)
    f.tombul("kulak", C(3.8, -9.5, 7.5) + C(3.8, 9.5, 7.5), 7.0, WHITE)
    f.tombul("kafa", E(11.5, 10.5, 0, 0), 9.0, WHITE)
    f.tombul("bere", birlesim(E(10.0, 7.5, 0, 10.0) - RR(30, 10, 0, 0, 2.0)), 9.6, GREEN)
    f.tombul("bere kenarı", RR(21.0, 4.0, 2.0, 0, 8.0), 10.0, GREEN)
    f.tombul("ponpon", C(3.2, 0, 18.5), 9.8, RED)
    goz(f, 4.2, 1.0)
    f.kapla("burun", E(2.0, 1.5, 0, -3.0), MOKA, 1.0)
    f.kapla("ağız", yay(2.2, 1.2, 205, 335, 0, -4.2), MOKA)
    return f


MODELLER = [y01_noel_baba, y02_kardan_adam, y03_geyik, y04_cam_agaci, y05_kurabiye_adam, y06_hediye, y07_can,
            y08_seker_baston, y09_corap, y10_top_susu, y11_yildiz, y12_ayicik, y13_kurabiye_ev, y14_eldiven,
            y15_kutup_ayisi]


# ---------------------------------------------------------------- görünüş ve katalog

def gorunus(f, boy=600):
    """Önden (biraz yandan, tombulluğu görünsün) RGBA."""
    from cift_tarafli_isimlik import render, rotation
    mesh = [(*A.mesh_arrays(m), O.TON[c]) for _, m, c in f.katilar()]
    return render(mesh, boy, rotation(-14, 26), margin=0.04)


def main():
    from atolye.tasarim import katalog as KT
    os.makedirs(OUT, exist_ok=True)
    sayfa = []
    for fn in MODELLER:
        f = fn()
        im = gorunus(f)
        im.save(os.path.join(OUT, f"{f.kod}.png"))
        renkler = ", ".join(O.AD[c] for _, _, c in f.katilar())
        x0, y0, z0, x1, y1, z1 = _sinir(f)
        ad = f"{f.ad} · {x1 - x0:.0f} × {y1 - y0:.0f} × {z1 - z0:.0f} mm · {renkler}"
        sayfa.append((f.kod, ad, im))
        print(f.kod, ad)
    giris = ("BOYDE yılbaşı anahtarlıkları: tombul, sevimli 3D figürler. Sırtı düz, önü tombul; desteksiz basılır. "
             "Halka tepede. Renkler: altın, yeşil, kırmızı, beyaz, kahverengi.")
    bilgi = ("Ürün", ["Yaklaşık 4,5–5 cm, en kalın yeri ~1 cm; anahtarlık halkası ve zinciriyle.",
                      "Çok renkli tek parça baskı (Bambu Lab X2D): boya yok, renkler filamentten.",
                      "Destek gerekmez: sırt üstü basılır, temiz ve hızlı.",
                      "Beğendiğiniz 5 modeli seçin, X2D baskı dosyaları hazırlansın."])
    pdf, jpgs = KT.yap(OUT, "Yılbaşı anahtarlık", "15 model", 1, sayfa, giris, bilgi, sutun=3, satir=3,
                       alt_not="Beğendiğiniz modelin kodunu (ör. Y04) yazmanız yeterli.")
    print("PDF", pdf, jpgs)


def _sinir(f):
    return m3.Manifold.batch_boolean([m for _, m, _ in f.katilar()], m3.OpType.Add).bounding_box()


if __name__ == "__main__":
    main()
