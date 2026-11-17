"""BOYDE yılbaşı anahtarlıkları: tombul, tatlı 3D figürler (15 model), desteksiz; tepede halka.

Fotoğraftaki örgü yılbaşı figürleri (geyik, Noel Baba, çam, kardan adam...) tarzında, az ayrıntılı ve sevimli.
Tam 3D: önü ve arkası tombul (arka önün %60'ı kalınlığında), ayakta durarak basılır; altta küçük düz taban, halka tepede
dik (delik önden arkaya, Ø4). Göz, burun, düğme gibi ayrıntılar önde, yüzeyi 0,8 mm kabarık izler.

Sevimlilik: iri, beyaz parıltılı gözler, kırmızı yanaklar, küçük gülücük (yuz()); tombul, kısa oranlar.

Desteksiz: figür önce serbest çizilir (önden tombul katmanlar, arkası aynası), sonra ayakta duracak hâle döndürülüp
0,2 mm katmanlara ayrılır; her katman alttakinden en çok EGIM × 0,2 mm taşabilir (≈48°), taşan yer kesilir. Böylece
şapka kenarı, kol, halka deliği tepesi gibi alt yüzeyler kendiliğinden 48°'lik eğime döner: destek gerekmez.

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


def _hesapla(m):
    """Boole işlemini hemen yaptırır: ayrıntı arttıkça tembel işlem ağacı şişip belleği bitirmesin."""
    m.num_tri()
    return m


class Figur:
    """Parçalar sırayla eklenir; sonra gelen kendi izdüşümünü (sütununu) öncekilerden alır."""

    def __init__(self, kod, ad, aciklama=""):
        self.kod, self.ad, self.aciklama = kod, ad, aciklama
        self.parcalar = []                                  # [(ad, Manifold, renk)]
        self._halka = None

    def _al(self, cs):
        s = _sutun(cs)
        self.parcalar = [(n, _hesapla(m - s), c) for n, m, c in self.parcalar]

    def birlik(self):
        return m3.Manifold.batch_boolean([m for _, m, _ in self.parcalar], m3.OpType.Add)

    def tombul(self, ad, cs, h, renk, r=None):
        self._al(cs)
        self.parcalar.append((ad, tombul(cs, h, r), renk))
        self.arka = [(n, m - _sutun(cs), c) for n, m, c in getattr(self, "arka", [])]
        self.arka.append((ad, tombul(cs, h, r), renk))      # arka yüz: yalnız tombul parçalar (ayrıntısız)
        return self

    def kapla(self, ad, cs, renk, t=0.8):
        """Alttaki yüzeyi t mm kabarık izleyen ayrıntı (göz, burun, düğme, desen)."""
        k = _sutun(cs)               # her parça önce sütunla kesilir: büyük birleşim yok (bellek taşıyordu)
        dilim = [_hesapla(k ^ m) for _, m, _ in self.parcalar]
        dilim += [_hesapla(k ^ m.translate((0, 0, t))) for _, m, _ in self.parcalar]
        d = _hesapla(m3.Manifold.batch_boolean([m for m in dilim if not m.is_empty()], m3.OpType.Add))
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

    def katilar_duz(self):
        """Sırtı düz (yalnız ön yüz) renk başına katılar; halka dahil (eski biçim)."""
        out = {}
        h = self._halka_parca()
        for _, m, c in self.parcalar + ([h] if h else []):
            if m.volume() > 1e-3:
                out[c] = out[c] + m if c in out else m
        return [(f"{O.AD[c]}", m, c) for c, m in out.items()]


ARKA_OLCEK = 0.6          # arka yüz önün bu kadarı kalın (cebe sığsın)
TABAN = 2.6               # ayakta dururken alttan kesilen (oturacağı düz taban)
DZ, EGIM = 0.2, 1.1       # katman ve katman başına en çok taşma (1,1 × 0,2 mm ≈ 48°)


def _uc_boyut_ham(f):
    """Önü tombul + arkası ayna (basık); halka orta düzlemde. Renk → Manifold (yatık, z = kalınlık)."""
    out = {}
    for _, m, c in f.parcalar:
        out[c] = out[c] + m if c in out else m
    for _, m, c in getattr(f, "arka", []):
        a = m.mirror((0, 0, 1)).scale((1.0, 1.0, ARKA_OLCEK))
        out[c] = out[c] + a if c in out else a
    if f._halka:
        x, renk, dis, ic, kal, gom = f._halka
        iz = f.birlik().project()
        ust = (iz ^ RR(2.0, 200.0, 0.0, x, 0.0)).bounds()[3]
        y = ust + dis - gom
        govde = m3.Manifold.batch_boolean(list(out.values()), m3.OpType.Add)
        kalin = 3.4
        halka = (C(dis, x, y) - C(ic, x, y)).extrude(kalin).translate((0, 0, -kalin / 2 - 0.6)) - govde
        out[renk] = out[renk] + halka if renk in out else halka
    return out


def uc_boyut(f):
    """Ayakta, desteksiz basılacak tam 3D figür: [(ad, Manifold, renk)] (z yukarı, ön yüz -y)."""
    ham = {c: m.rotate((90.0, 0.0, 0.0)) for c, m in _uc_boyut_ham(f).items()}
    z0 = min(m.bounding_box()[2] for m in ham.values())
    z1 = max(m.bounding_box()[5] for m in ham.values())
    ham = {c: m.translate((0, 0, -z0 - TABAN)) for c, m in ham.items()}
    yukseklik = z1 - z0 - TABAN
    katlar = {c: [] for c in ham}
    onceki = None
    n = int(math.ceil(yukseklik / DZ))
    for i in range(n):
        z = i * DZ
        izin = onceki.simplify(0.02).offset(EGIM * DZ, m3.JoinType.Miter) if onceki is not None else None
        toplam = []
        for c, m in ham.items():
            cs = m.slice(z + DZ / 2)
            if izin is not None:
                cs = cs ^ izin
            if cs.area() > 0.01:
                katlar[c].append(cs.extrude(DZ).translate((0, 0, z)))
                toplam.append(cs)
        if not toplam:
            break
        onceki = A.union(*toplam)
    return [(O.AD[c], m3.Manifold.batch_boolean(v, m3.OpType.Add), c) for c, v in katlar.items() if v]


def yuz(f, x, y, r=1.7, cx=0.0, yanak=RED, agiz="gulus", agiz_y=None, agiz_renk=MOKA, goz_renk=MOKA):
    """Sevimli yüz: iri gözler (sol üstte beyaz parıltı), kırmızı yanaklar, küçük gülücük ya da "w" ağız."""
    for s in (-1, 1):
        f.kapla("göz", C(r, cx + s * x, y), goz_renk)
    ri = max(0.6, 0.38 * r)
    for s in (-1, 1):
        f.kapla("parıltı", C(ri, cx + s * x - 0.38 * r, y + 0.38 * r), WHITE, 0.3)
    if yanak is not None:
        for s in (-1, 1):
            f.kapla("yanak", E(1.5, 0.95, cx + s * (x + 1.7), y - r - 0.5), yanak, 0.4)
    ay = agiz_y if agiz_y is not None else y - 0.9
    if agiz == "gulus":
        f.kapla("ağız", yay(1.5, 0.7, 205, 335, cx, ay), agiz_renk, 0.6)
    elif agiz == "w":
        f.kapla("ağız", yay(1.1, 0.4, 200, 340, cx - 1.05, ay) + yay(1.1, 0.4, 200, 340, cx + 1.05, ay), agiz_renk, 0.6)
    return f


def _egik(rx, ry, aci, x, y):
    return E(rx, ry).rotate(aci).translate((x, y))


# ---------------------------------------------------------------- 15 model (y: aşağıdan yukarı)
# Hepsinde sevimli yüz (iri, parıltılı göz + yanak + gülücük), tombul oranlar; alttan taşan yer az (desteksiz).

def y01_noel_baba():
    f = Figur("Y01", "Noel Baba", "Kırmızı şapka, beyaz ponpon, tombul sakal, kırmızı yanaklar")
    f.halka(1.5, 0, WHITE)
    f.tombul("yüz", C(10.5, 0, 0), 8.0, NUDE)
    f.tombul("şapka", P([(-11.5, 7.5), (11.5, 7.5), (6.5, 16.5), (1.0, 21.0), (-6.0, 16.0)], 2.5), 9.0, RED)
    f.tombul("şapka kenarı", RR(25.0, 5.0, 2.5, 0, 7.8), 9.6, WHITE)
    f.tombul("ponpon", C(3.4, 1.5, 20.5), 9.2, WHITE)
    sakal = birlesim(E(12.5, 9.5, 0, -6.5), C(4.2, -9.0, -2.5), C(4.2, 9.0, -2.5)) - E(6.5, 4.0, 0, 1.5)
    f.tombul("sakal", sakal, 9.0, WHITE)
    f.tombul("bıyık", birlesim(E(3.8, 1.9, -3.0, -2.0), E(3.8, 1.9, 3.0, -2.0)), 9.8, WHITE)
    yuz(f, 3.6, 2.4, 1.6, agiz=None)
    f.kapla("burun", C(1.4, 0, -0.5), RED, 1.0)
    return f


def y02_kardan_adam():
    f = Figur("Y02", "Kardan adam", "Kırmızı bere, yeşil atkı, altın havuç burun")
    f.halka(0, 0, RED)
    f.tombul("gövde", C(9.5, 0, -11.0), 8.5, WHITE)
    f.tombul("kafa", C(9.0, 0, 3.5), 9.0, WHITE)
    f.tombul("bere", E(8.6, 6.5, 0, 11.0) - RR(30, 10, 0, 0, 6.0), 9.6, RED)
    f.tombul("bere kenarı", RR(18.0, 3.8, 1.9, 0, 10.6), 10.0, WHITE)
    f.tombul("ponpon", C(3.0, 0, 18.0), 9.6, WHITE)
    f.tombul("atkı", RR(17.0, 4.0, 2.0, 0, -4.6), 9.6, GREEN)
    f.tombul("atkı ucu", RR(4.0, 8.0, 1.8, 5.0, -8.5), 9.8, GREEN)
    yuz(f, 3.4, 4.6, 1.7, agiz_y=0.9)
    f.kapla("burun", ucgen(2.4, 3.6, 0, 2.0, 0.5).rotate(-90).translate((-2.0, 2.6)), GOLD, 1.2)
    for yy in (-10.0, -14.5):
        f.kapla("düğme", C(1.3, 0, yy), MOKA)
    return f


def y03_geyik():
    f = Figur("Y03", "Geyik", "Altın boynuzlar, kırmızı burun, kırmızı yanaklar")
    f.halka(0, 0, KAHVE)
    sol = birlesim(yay(9.0, 6.2, 95, 175, -3.0, 10.0),
                   RR(2.8, 6.0, 1.4).rotate(20).translate((-6.6, 18.2)),
                   RR(2.8, 5.0, 1.4).rotate(-35).translate((-11.4, 14.6)))
    f.tombul("boynuz", sol + sol.mirror((1, 0)), 6.0, GOLD)
    f.tombul("kulak", _egik(4.6, 2.5, -25, -10.5, 8.0) + _egik(4.6, 2.5, 25, 10.5, 8.0), 7.0, KAHVE)
    f.tombul("kafa", E(10.5, 10.5, 0, 1.5), 9.0, KAHVE)
    f.tombul("ağız", E(6.2, 4.3, 0, -5.2), 9.8, NUDE)
    yuz(f, 4.3, 3.0, 1.8, agiz=None)
    f.kapla("burun", E(2.4, 1.8, 0, -3.6), RED, 1.2)
    f.kapla("ağız", yay(1.3, 0.6, 205, 335, 0, -5.4), MOKA, 0.6)
    return f


def y04_cam_agaci():
    f = Figur("Y04", "Çam ağacı", "Altın yıldız, kırmızı ve altın süsler, gülen yüz")
    f.halka(0, 0, GOLD)
    agac = birlesim(ucgen(25.0, 12.0, 0, -14.0, 3.0), ucgen(20.0, 11.0, 0, -6.5, 3.0), ucgen(15.0, 10.0, 0, 0.5, 3.0))
    f.tombul("ağaç", agac, 8.5, GREEN)
    f.tombul("yıldız", yildiz(5.2, 2.5, 0, 12.5), 8.5, GOLD)
    yuz(f, 3.2, -6.0, 1.6)
    for x, y, c in ((-7.5, -11.5, RED), (7.0, -12.0, GOLD), (0.0, -12.3, RED), (-3.2, 3.0, GOLD), (3.4, 4.6, RED)):
        f.kapla("süs", C(1.3, x, y), c, 1.0)
    return f


def y05_kurabiye_adam():
    f = Figur("Y05", "Zencefilli kurabiye", "Kollarını açmış, beyaz krema, kırmızı ve yeşil düğmeler")
    f.halka(0, 0, KAHVE)
    kol_s = RR(5.6, 9.5, 2.8).rotate(45).translate((-7.6, 2.0))
    kol_d = RR(5.6, 9.5, 2.8).rotate(-45).translate((7.6, 2.0))
    govde = birlesim(C(8.0, 0, 9.5), RR(13.0, 13.0, 5.0, 0, -3.0), kol_s, kol_d,
                     RR(5.8, 10.0, 2.9, -3.6, -11.0), RR(5.8, 10.0, 2.9, 3.6, -11.0))
    f.tombul("kurabiye", govde.offset(0.6, J).offset(-0.6, J), 7.5, KAHVE)
    yuz(f, 2.9, 10.2, 1.6, agiz_renk=WHITE)
    for s in (-1, 1):
        f.kapla("krema", RR(4.4, 1.2, 0.6).rotate(-45 * s).translate((9.3 * s, 3.7)), WHITE)
        f.kapla("krema", RR(4.4, 1.2, 0.6, 3.6 * s, -13.0), WHITE)
    f.kapla("düğme", C(1.3, 0, 0.0), RED, 1.0)
    f.kapla("düğme", C(1.3, 0, -4.5), GREEN, 1.0)
    return f


def y06_hediye():
    f = Figur("Y06", "Hediye kutusu", "Yeşil kutu, kırmızı kurdele ve fiyonk, gülen yüz")
    f.halka(0, 0, RED)
    f.tombul("fiyonk", E(5.5, 3.8, -4.8, 12.5) + E(5.5, 3.8, 4.8, 12.5), 8.5, RED)
    f.tombul("düğüm", C(2.3, 0, 11.8), 9.4, GOLD)
    f.tombul("kutu", RR(23.0, 17.0, 5.0, 0, -3.5), 8.0, GREEN)
    f.tombul("kapak", RR(26.0, 5.5, 2.6, 0, 6.5), 8.6, GREEN)
    f.kapla("kurdele", RR(4.0, 24.0, 0.8, 0, -3.0), RED)
    yuz(f, 5.6, -3.0, 1.7, agiz_y=-3.6)
    return f


def y07_can():
    f = Figur("Y07", "Yılbaşı çanı", "Altın çan, kırmızı fiyonk, yeşil yapraklar, gülen yüz")
    f.halka(0, 0, GOLD)
    can = birlesim(P([(-12.0, -11.0), (12.0, -11.0), (9.0, 2.0), (6.0, 11.0), (-6.0, 11.0), (-9.0, 2.0)], 4.0),
                   RR(27.0, 5.0, 2.5, 0, -10.5))
    f.tombul("çan", can, 8.5, GOLD)
    f.tombul("yaprak", E(6.0, 2.8, -5.5, 12.6) + E(6.0, 2.8, 5.5, 12.6), 7.5, GREEN)
    f.tombul("fiyonk", E(3.6, 2.6, -3.0, 13.6) + E(3.6, 2.6, 3.0, 13.6) + C(2.0, 0, 13.3), 9.0, RED)
    yuz(f, 3.8, -1.0, 1.7)
    return f


def y08_seker_baston():
    f = Figur("Y08", "Şeker baston", "Tombul beyaz-kırmızı çizgili baston, yeşil fiyonk")
    f.halka(-2.5, 0, RED)
    baston = birlesim(yay(10.0, 3.5, 0, 180, -2.5, 11.0), C(3.25, -9.25, 11.0), RR(6.5, 30.0, 3.25, 4.25, -4.0))
    f.tombul("baston", baston, 8.0, WHITE)
    seritler = birlesim(*[RR(60.0, 2.6, 0.0, 0, y).rotate(35) for y in range(-30, 34, 5)])
    f.kapla("çizgi", seritler ^ baston.offset(-0.3, J), RED, 0.6)
    f.tombul("fiyonk", E(4.6, 2.8, 0.2, -3.0) + E(4.6, 2.8, 8.3, -3.0), 9.0, GREEN)
    f.tombul("düğüm", C(2.2, 4.25, -3.0), 9.6, RED)
    return f


def y09_corap():
    f = Figur("Y09", "Yılbaşı çorabı", "Kırmızı çorap, beyaz kenar, altın yıldız, gülen yüz")
    f.halka(-2.0, 0, WHITE)
    corap = birlesim(RR(14.0, 22.0, 5.0, -2.0, 4.0), RR(22.0, 11.0, 5.5, 2.0, -8.5))
    f.tombul("çorap", corap, 8.0, RED)
    f.tombul("kenar", RR(18.0, 7.0, 3.0, -2.0, 17.0), 9.0, WHITE)
    f.kapla("yıldız", yildiz(2.8, 1.3, -2.0, 17.0, 0.4), GOLD, 0.8)
    f.kapla("burun", (C(5.6, 13.0, -8.5) ^ corap.offset(-0.4, J)), WHITE, 0.8)
    yuz(f, 3.3, 6.5, 1.7, cx=-2.0, yanak=None)
    return f


def y10_top_susu():
    f = Figur("Y10", "Yılbaşı topu", "Yeşil top, altın başlık, gülen yüz, kar taneleri")
    f.halka(0, 0, GOLD)
    f.tombul("başlık", RR(8.0, 5.0, 1.2, 0, 15.0), 7.0, GOLD)
    f.tombul("top", C(13.0, 0, 0), 10.0, GREEN)
    yuz(f, 4.2, 1.5, 1.9)
    f.kapla("parlaklık", E(2.2, 1.3, -6.8, 7.0), WHITE, 0.6)
    for x, y in ((-7.5, -6.0), (7.0, -6.5), (-3.0, -9.5), (3.0, -10.0), (8.5, 5.0)):
        f.kapla("kar", C(0.9, x, y), WHITE, 0.6)
    return f


def y11_yildiz():
    f = Figur("Y11", "Altın yıldız", "Tombul, gülen yüzlü altın yıldız")
    f.halka(0, 0, GOLD)
    f.tombul("yıldız", yildiz(15.5, 8.5, 0, -1.0, 3.0), 8.5, GOLD)
    yuz(f, 3.4, 0.3, 1.7)
    return f


def y12_ayicik():
    f = Figur("Y12", "Ayıcık", "Noel Baba şapkalı kahverengi ayıcık")
    f.halka(4.0, 0, WHITE)
    f.tombul("kulak", C(4.2, -9.5, 8.0) + C(4.2, 9.5, 8.0), 7.0, KAHVE)
    f.tombul("kafa", E(11.5, 10.5, 0, 0), 9.0, KAHVE)
    f.tombul("şapka", P([(-11.0, 5.5), (11.0, 5.5), (7.0, 14.0), (3.5, 20.5), (-6.0, 13.5)], 2.0), 9.6, RED)
    f.tombul("şapka kenarı", RR(24.0, 4.6, 2.3, 0, 5.8), 10.0, WHITE)
    f.tombul("ponpon", C(3.0, 4.0, 20.0), 9.8, WHITE)
    f.tombul("ağız", E(4.8, 3.6, 0, -5.0), 9.8, NUDE)
    yuz(f, 4.6, 0.0, 1.7, agiz="w", agiz_y=-5.0)
    f.kapla("burun", E(1.8, 1.3, 0, -3.8), MOKA, 1.0)
    return f


def y13_kurabiye_ev():
    f = Figur("Y13", "Kurabiye ev", "Beyaz kremalı çatı, renkli şekerler, gülen yüz")
    f.halka(0, 0, WHITE)
    f.tombul("ev", RR(21.0, 17.0, 2.5, 0, -6.0), 7.5, KAHVE)
    f.tombul("çatı", P([(-14.0, 2.0), (14.0, 2.0), (0, 16.5)], 2.5), 8.6, WHITE)
    for i, x in enumerate((-7.5, -2.5, 2.5, 7.5)):
        f.kapla("şeker", C(1.1, x, 4.6), RED if i % 2 == 0 else GREEN, 0.8)
    yuz(f, 4.6, -4.0, 1.7)
    f.kapla("kapı", RR(5.0, 6.0, 2.3, 0, -11.5), RED, 1.0)
    return f


def y14_eldiven():
    f = Figur("Y14", "Eldiven", "Kırmızı eldiven, beyaz kenar, gülen yüz")
    f.halka(1.0, 0, WHITE)
    eld = birlesim(RR(16.0, 22.0, 8.0, 1.0, 5.0), _egik(3.6, 6.0, 20, -8.6, 3.0))
    f.tombul("eldiven", eld, 8.5, RED)
    f.tombul("kenar", RR(19.0, 6.5, 3.0, 1.0, -8.5), 9.2, WHITE)
    for x in (-5.0, 1.0, 7.0):
        f.kapla("benek", C(0.9, x, -8.5), GREEN, 0.6)
    yuz(f, 3.3, 6.0, 1.7, cx=1.0, yanak=None)
    return f


def y15_kutup_ayisi():
    f = Figur("Y15", "Kutup ayısı", "Yeşil bereli, kırmızı ponponlu beyaz ayı")
    f.halka(0, 0, RED)
    f.tombul("kulak", C(3.8, -9.5, 7.5) + C(3.8, 9.5, 7.5), 7.0, WHITE)
    f.tombul("kafa", E(11.5, 10.5, 0, 0), 9.0, WHITE)
    f.tombul("bere", E(10.0, 7.5, 0, 10.0) - RR(30, 10, 0, 0, 2.0), 9.6, GREEN)
    f.tombul("bere kenarı", RR(21.0, 4.0, 2.0, 0, 8.0), 10.0, GREEN)
    f.tombul("ponpon", C(3.2, 0, 18.5), 9.8, RED)
    f.tombul("ağız", E(4.6, 3.4, 0, -4.8), 9.8, WHITE)
    yuz(f, 4.6, 1.0, 1.7, agiz="w", agiz_y=-5.0)
    f.kapla("burun", E(1.8, 1.3, 0, -3.6), MOKA, 1.0)
    return f


MODELLER = [y01_noel_baba, y02_kardan_adam, y03_geyik, y04_cam_agaci, y05_kurabiye_adam, y06_hediye, y07_can,
            y08_seker_baston, y09_corap, y10_top_susu, y11_yildiz, y12_ayicik, y13_kurabiye_ev, y14_eldiven,
            y15_kutup_ayisi]


# ---------------------------------------------------------------- görünüş ve katalog

def gorunus(f, boy=600, katilar=None, azim=-28.0, elev=-72.0):
    """Ayakta duran figür, önden biraz yandan ve yukarıdan (tombulluğu görünsün): RGBA."""
    from cift_tarafli_isimlik import render, rotation
    katilar = katilar if katilar is not None else uc_boyut(f)
    mesh = [(*A.mesh_arrays(m), O.TON[c]) for _, m, c in katilar]
    return render(mesh, boy, rotation(azim, elev), margin=0.04)


def main():
    from atolye.tasarim import katalog as KT
    os.makedirs(OUT, exist_ok=True)
    sayfa = []
    for fn in MODELLER:
        f = fn()
        k = uc_boyut(f)
        im = gorunus(f, katilar=k)
        im.save(os.path.join(OUT, f"{f.kod}.png"))
        renkler = ", ".join(O.AD[c] for _, _, c in k)
        x0, y0, z0, x1, y1, z1 = _sinir(f, k)
        ad = f"{f.ad} · {x1 - x0:.0f} × {y1 - y0:.0f} × {z1 - z0:.0f} mm · {renkler}"
        sayfa.append((f.kod, ad, im))
        print(f.kod, ad)
    giris = ("BOYDE yılbaşı anahtarlıkları: tombul, sevimli tam 3D figürler. Önü de arkası da yuvarlak; "
             "ayakta desteksiz basılır. Halka tepede. Renkler: altın, yeşil, kırmızı, beyaz, kahverengi.")
    bilgi = ("Ürün", ["Yaklaşık 3–5 cm boy, 1,2–1,7 cm kalınlık; anahtarlık halkası ve zinciriyle.",
                      "Çok renkli tek parça baskı (Bambu Lab X2D): boya yok, renkler filamentten.",
                      "Destek gerekmez: figür ayakta basılır, altta küçük düz taban.",
                      "Beğendiğiniz 5 modeli seçin, X2D baskı dosyaları hazırlansın."])
    pdf, jpgs = KT.yap(OUT, "Yılbaşı anahtarlık", "15 model", 1, sayfa, giris, bilgi, sutun=3, satir=3,
                       alt_not="Beğendiğiniz modelin kodunu (ör. Y04) yazmanız yeterli.")
    print("PDF", pdf, jpgs)


def _sinir(f, katilar=None):
    katilar = katilar if katilar is not None else uc_boyut(f)
    return m3.Manifold.batch_boolean([m for _, m, _ in katilar], m3.OpType.Add).bounding_box()


if __name__ == "__main__":
    main()
