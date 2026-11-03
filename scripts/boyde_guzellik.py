"""BOYDE LABS – güzellik koleksiyonu: kuaför, güzellik salonu, tırnak stüdyosu, kirpik, cilt bakım, lazer, makyaj,
spa ve gelin başı için örnek isimlikler (katalog ve Shopier için; işletme ve kişi adları uydurma).

Kullanıcı isteği: "pembe beyaz ve kadınların kullandığı tarzdaki renklerden hem 9 × 12 hem de 10 × 20 10'ar adet örnek
ürün; kuaför, beauty salonları, tırnakçılar... sadece pembe-beyaz değil, hafif ten rengi gibi güzel görünen renkler;
yazı fontları daha tatlı ve dikkat çekici, çiçek motifleri".

Yapı scripts/boyde_sektor.py'deki gibi:
  9 × 12 cm  120 × 90 mm, 1 cm gövde, yazı ve motifler 2 mm kabartma (çizgi ≥ 0,8 mm, simgelerde ≥ 1,2 mm), ince süsler
             yüzeyle aynı hizada dolgu (≥ 0,5 mm), QR yüzeyle aynı hizada; renkli gövdede QR beyaz karoda
  10 × 20 cm 200 × 100 mm, 5 mm gövde, yazı ve motifler yüzeyle aynı hizada renkli dolgu (çizgi ≥ 0,5 mm)
QR'lar örnek modunda (okunmaz), telefon BOYDE LABS'in (0546 475 45 08).

Renkler (PLA; fotoğraf tonları, Bambu karşılığı yakın renk):
  pudra pembe   Sakura Pink (PLA Matte)      gül kurusu  pembe ile mürdüm arası (dusty rose)
  fuşya         Hot Pink / Magenta (Basic)   ten (nude)  Latte Brown (PLA Matte)
  krem          Ivory / Bone White (Matte)   moka        Dark Chocolate (PLA Matte)
  mürdüm        Plum (PLA Matte)             lila        Lilac Purple (PLA Matte)
  rose gold     Rose Gold (PLA Silk, metalik) adaçayı   yumuşak yeşil (sage)
Yazı tipleri (OFL, scripts/fonts): Pacifico, Kaushan Script, Yesteryear, Norican, Caveat (el yazısı; kabartmada
büyük boyda), Fraunces (yumuşak serif), Baloo 2 ExtraBold (yuvarlak; kabartmada küçük yazı ≥ 4,3 mm: çizgi ≥ 0,75, harf
içi ≥ 0,5 mm) ve Quicksand; 10 × 20'de dolgu
olduğundan Dancing Script, Playball, Marcellus, Josefin Sans da.

Çıktı : boyde_labs/guzellik/kaynak/<ürün>.npz, <ürün>_duz.png (git'e girmez: npz)
Kullanım:
  python3 scripts/boyde_guzellik.py [ürün ...]          # modeller, QR denetimi, düz görünüşler
  python3 scripts/boyde_guzellik.py --foto [ürün ...]   # Blender fotoğrafları (bpy 4.2)
  python3 scripts/boyde_guzellik.py --gorsel            # toplu görseller ve Shopier görselleri
"""
import math
import os
import sys

import manifold3d as m3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_urunler as U  # noqa: E402  (örnek modu: QR'lar okunmaz, telefon BOYDE'nin)
import boyde_sektor as S  # noqa: E402
import anahtarlik as A  # noqa: E402
import qr_sistemi as Q  # noqa: E402

J = m3.JoinType.Round
BLACK, WHITE, YELLOW, GOLD = A.BLACK, A.WHITE, A.YELLOW, A.GOLD
PUDRA, GUL, FUSYA, NUDE, KREM, MOKA, MURDUM, LILA, ROSE, ADACAYI = range(41, 51)
RENK = {PUDRA: ("pudra pembe", (238, 178, 194)), GUL: ("gül kurusu", (192, 110, 126)),
        FUSYA: ("fuşya", (222, 52, 124)), NUDE: ("ten rengi", (218, 186, 166)), KREM: ("krem", (243, 234, 218)),
        MOKA: ("moka", (92, 62, 52)), MURDUM: ("mürdüm", (112, 38, 74)), LILA: ("lila", (184, 160, 216)),
        ROSE: ("rose gold", (214, 152, 138)), ADACAYI: ("adaçayı", (146, 170, 138))}
S.NAMES.setdefault(YELLOW, "sarı")
for _k, (_ad, _rgb) in RENK.items():
    S.NAMES[_k] = _ad
    U.RGB[_k] = _rgb
U.METAL.add(ROSE)
S.FONTS.update({"pacifico": "Pacifico-Regular.ttf", "kaushan": "KaushanScript-Regular.ttf",
                "yester": "Yesteryear-Regular.ttf", "norican": "Norican-Regular.ttf", "caveat": "Caveat-Bold.ttf",
                "fraunces": "Fraunces-Black.ttf", "frauncesi": "Fraunces-BlackItalic.ttf",
                "frauncesy": "Fraunces-SemiBoldItalic.ttf", "baloo": "Baloo2-ExtraBold.ttf",
                "quick": "Quicksand-Bold.ttf", "dancing": "DancingScript-Bold.ttf", "playball": "Playball-Regular.ttf",
                "marcellus": "Marcellus-Regular.ttf", "josefin": "JosefinSans-SemiBold.ttf"})
t, bar, qr_entry = S.t, S.bar, S.qr_entry
PHONE = S.PHONE
OUT = os.path.join(A.ROOT, "boyde_labs", "guzellik")
SRC = os.path.join(OUT, "kaynak")


class Tasarim(S.Design):
    def qr(self, entry, cx, cy, s, sq=None, frame=None, flat=False, karo=None):
        """karo: renkli gövdede QR'ın zemini (beyaz karo, kareler sq renginde); yoksa boyde_sektor'deki gibi."""
        if karo is None:
            return super().qr(entry, cx, cy, s, sq, frame, flat)
        _, dark, _ = Q.shapes(entry, Q.module_for(entry, s), cx, cy)
        tile = A.rrect(s, s, 1.6, cx, cy)
        self.inlay.append((tile - dark, karo))
        self.inlay.append((dark ^ tile, sq))
        if frame:
            g, w = 1.8, 1.2
            ring = A.rrect(s + 2 * (g + w), s + 2 * (g + w), 2.8, cx, cy) - A.rrect(s + 2 * g, s + 2 * g, 2.0, cx, cy)
            (self.flat if flat else self.add)(None, ring, frame)
        self.lines["QR"] = tile
        return tile


def koyu(body):
    return {"body": body, "fg": WHITE, "dark": True}


def acik(body):
    return {"body": body, "fg": BLACK, "dark": False}


# ---------------------------------------------------------------- motifler (kabartmada en ince yer ≥ 1,2 mm)

def elips(rx, ry, cx=0.0, cy=0.0, n=96):
    return A.circle(1.0, 0.0, 0.0, n).scale((rx, ry)).translate((cx, cy))


def mercek(L, W):
    """İki yaydan yaprak: uçları (0, 0) ve (0, L), eni W."""
    R = ((L / 2) ** 2 + (W / 2) ** 2) / W
    c = R - W / 2
    return A.circle(R, c, L / 2, 160) ^ A.circle(R, -c, L / 2, 160)


def yaprak(x, y, L, aci, W=None):
    """Sapı (x, y)'de, aci yönünde (derece, +x'ten) uzanan yaprak."""
    return mercek(L, W or L * 0.46).rotate(aci - 90.0).translate((x, y))


def katmanla(sekiller, ara=0.8):
    """Arkadan öne çizilen şekiller: her biri, arkasındakilerden `ara` kadar boşlukla ayrılır."""
    acc = A.empty()
    for s in sekiller:
        acc = (acc - s.offset(ara, J)) + s
    return acc


def cicek(cx, cy, r, n=5, en=0.62, gobek=0.3, aci=90.0, ara=0.8):
    """Yapraklı çiçek. Döner (taç yapraklar, göbek); yapraklar ve göbek arasında `ara` kadar boşluk."""
    yap = []
    for k in range(n):
        a = math.radians(aci + k * 360.0 / n)
        d = r * 0.56
        yap.append(elips(r * en / 2 * 1.0, r * 0.44).rotate(math.degrees(a) - 90.0)
                   .translate((cx + d * math.cos(a), cy + d * math.sin(a))))
    g = A.circle(r * gobek, cx, cy, 64)
    return katmanla(yap, ara) - g.offset(ara, J), g


def papatya(cx, cy, r, n=12, ara=0.7):
    """Papatya: ince uzun yapraklar ve iri göbek. Döner (yapraklar, göbek)."""
    yap = []
    for k in range(n):
        a = math.radians(90.0 + k * 360.0 / n)
        d = r * 0.62
        yap.append(elips(r * 0.14, r * 0.36).rotate(math.degrees(a) - 90.0)
                   .translate((cx + d * math.cos(a), cy + d * math.sin(a))))
    g = A.circle(r * 0.3, cx, cy, 64)
    return katmanla(yap, ara) - g.offset(ara, J), g


def gul(cx, cy, r, ara=0.8, tur=2.3):
    """Gül: dalgalı kenarlı disk, içinde sarmal oyuk."""
    disk = A.circle(r * 0.72, cx, cy, 96)
    for k in range(6):
        a = math.radians(30 + k * 60)
        disk = disk + A.circle(r * 0.36, cx + r * 0.62 * math.cos(a), cy + r * 0.62 * math.sin(a), 64)
    disk = disk ^ A.circle(r, cx, cy, 128)
    T = tur * 2 * math.pi
    pts = [(cx + (r * 0.08 + r * 0.74 * th / T) * math.cos(th + 1.2),
            cy + (r * 0.08 + r * 0.74 * th / T) * math.sin(th + 1.2)) for th in [T * i / 220 for i in range(221)]]
    return disk - A.stroke(pts, ara)


def sakayik(cx, cy, r, ara=0.8):
    """Şakayık: iç içe üç dalgalı halka, ortada göbek noktaları."""
    def dalga(R, n, k, faz=0.0):
        out = A.circle(R * (1 - k) * 1.02, cx, cy, 96)
        for i in range(n):
            a = math.radians(faz + i * 360.0 / n)
            out = out + A.circle(R * k, cx + R * (1 - k) * math.cos(a), cy + R * (1 - k) * math.sin(a), 64)
        return out
    dis, orta, ic = dalga(r, 9, 0.3), dalga(r * 0.66, 7, 0.34, 20), dalga(r * 0.36, 5, 0.42, 40)
    sekil = dis - (orta.offset(ara / 2, J) - orta.offset(-ara / 2, J)) - (ic.offset(ara / 2, J) - ic.offset(-ara / 2, J))
    nokta = A.union(*[A.circle(r * 0.07, cx + r * 0.13 * math.cos(math.radians(a)),
                               cy + r * 0.13 * math.sin(math.radians(a))) for a in (90, 210, 330)])
    return sekil - nokta.offset(ara * 0.6, J)


def lotus(cx, cy, h, ara=0.8):
    """Nilüfer (lotus): tabanı (cx, cy)'de, yelpaze gibi beş yaprak."""
    yap = [yaprak(cx, cy, h * 0.62, 90 + s * 64, h * 0.3) for s in (-1, 1)]
    yap += [yaprak(cx, cy, h * 0.84, 90 + s * 33, h * 0.38) for s in (-1, 1)]
    yap.append(yaprak(cx, cy, h, 90.0, h * 0.42))
    return katmanla(yap, ara)


def dal(noktalar, yaprak_say, L, en=1.2, uc=True, yon=1):
    """Kıvrık sap ve iki yanında sırayla yapraklar. noktalar: sapın kılavuz noktaları."""
    pts = A.smooth(noktalar, n=200)
    sap = A.stroke(pts, en)
    uzun = [0.0]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        uzun.append(uzun[-1] + math.hypot(x1 - x0, y1 - y0))
    out = [sap]
    for k in range(yaprak_say):
        s = uzun[-1] * (0.18 + 0.72 * k / max(1, yaprak_say - 1))
        i = next(j for j, u in enumerate(uzun) if u >= s)
        i = min(max(i, 1), len(pts) - 1)
        (x0, y0), (x1, y1) = pts[i - 1], pts[i]
        teg = math.degrees(math.atan2(y1 - y0, x1 - x0))
        taraf = (1 if k % 2 == 0 else -1) * yon
        out.append(yaprak(x1, y1, L, teg + taraf * 42.0))
    if uc:
        (x0, y0), (x1, y1) = pts[-2], pts[-1]
        out.append(yaprak(x1, y1, L * 1.05, math.degrees(math.atan2(y1 - y0, x1 - x0))))
    return A.union(*out)


def celenk(cx, cy, R, adet=9, L=None, bosluk=50.0):
    """Yapraklı çelenk: iki yay, üstte `bosluk` derece açık."""
    L = L or R * 0.38
    out = []
    for s in (-1, 1):
        bas, son = 90 + s * bosluk / 2, 90 + s * (180 - 8)
        yay = [(cx + R * math.cos(math.radians(bas + (son - bas) * i / 60)),
                cy + R * math.sin(math.radians(bas + (son - bas) * i / 60))) for i in range(61)]
        out.append(A.stroke(yay, 1.2))
        for k in range(adet):
            a = bas + (son - bas) * (k + 0.5) / adet
            x, y = cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))
            teg = a + s * 90.0                          # yay boyunca, alta doğru
            for d in (-1, 1):
                out.append(yaprak(x, y, L, teg + 180 + d * 38.0 * s * -1 + 0.0, L * 0.44))
    return A.union(*out)


def fiyonk(cx, cy, w):
    """Fiyonk: iki ilmek (ortaları oyuk), düğüm ve iki kuyruk."""
    h = w * 0.5
    ilmek = A.polygon(A.smooth([(0.0, 0.0), (-0.2 * w, 0.42 * h), (-0.48 * w, 0.5 * h), (-0.5 * w, 0.0),
                                 (-0.48 * w, -0.5 * h), (-0.2 * w, -0.42 * h)], closed=True))
    ic = A.polygon(A.smooth([(-0.12 * w, 0.0), (-0.24 * w, 0.22 * h), (-0.4 * w, 0.26 * h), (-0.4 * w, 0.0),
                              (-0.4 * w, -0.26 * h), (-0.24 * w, -0.22 * h)], closed=True))
    sol = ilmek - ic
    sag = sol.transform([[-1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    kuyruk = A.polygon([(-0.04 * w, -0.1 * h), (-0.24 * w, -0.95 * h), (-0.14 * w, -0.86 * h), (-0.08 * w, -1.0 * h),
                        (0.06 * w, -0.12 * h)])
    kuyruklar = kuyruk + kuyruk.transform([[-1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    dugum = A.rrect(0.2 * w, 0.42 * h, 0.08 * w)
    sekil = katmanla([sol + sag, kuyruklar, dugum], 0.8)
    return sekil.translate((cx, cy))


def oje(cx, cy, h):
    """Oje şişesi. Döner (şişe, kapak)."""
    sise = A.rrect(h * 0.64, h * 0.5, h * 0.13, cx, cy - h * 0.25) + A.rrect(h * 0.3, h * 0.1, h * 0.03, cx, cy + h * 0.02)
    parilti = A.stroke([(cx - h * 0.2, cy - h * 0.12), (cx - h * 0.2, cy - h * 0.34)], 1.0)
    kapak = A.rrect(h * 0.22, h * 0.42, h * 0.05, cx, cy + h * 0.29)
    return sise - parilti, kapak


def ruj(cx, cy, h):
    """Ruj. Döner (uç, gövde)."""
    w = h * 0.32
    uc = A.polygon(A.smooth([(-w * 0.36, 0.0), (-w * 0.36, h * 0.2), (-w * 0.1, h * 0.36), (w * 0.36, h * 0.46),
                             (w * 0.36, 0.0)], closed=False, n=60) + [(w * 0.36, 0.0)])
    govde = A.rrect(w * 0.9, h * 0.2, 0.6, 0.0, -h * 0.13) + A.rrect(w, h * 0.42, 1.0, 0.0, -h * 0.47)
    govde = govde - A.rect(-w, -h * 0.26 - 0.45, w, -h * 0.26 + 0.45)
    return uc.translate((cx, cy + 0.9)), govde.translate((cx, cy))


def kirpik(cx, cy, w, kas=False):
    """Kapalı göz ve kirpikler (kirpik stüdyosu); kas: üstte kaş."""
    yay = [(cx + w / 2 * math.cos(math.radians(a)), cy - w * 0.22 * math.sin(math.radians(a)) + w * 0.0)
           for a in range(190, 351, 4)]
    yay = [(cx - (cx - x), y) for x, y in yay]
    out = [A.stroke([(cx + w / 2 * math.cos(math.radians(a)), cy + w * 0.2 * math.sin(math.radians(a)))
                     for a in range(185, 356, 5)], 1.4)]
    for k in range(7):
        a = math.radians(205 + k * 21.5)
        x, y = cx + w / 2 * math.cos(a), cy + w * 0.2 * math.sin(a)
        nx, ny = math.cos(a), math.sin(a) * 1.6
        n = math.hypot(nx, ny)
        nx, ny = nx / n, ny / n
        L = w * (0.15 if k in (0, 6) else 0.2)
        out.append(A.stroke([(x, y), (x + nx * L * 0.55 - 0.4 * ny, y + ny * L * 0.55),
                             (x + nx * L - ny * L * 0.25 * (1 if k < 3 else -1 if k > 3 else 0), y + ny * L)], 1.2))
    if kas:
        kp = [(cx - w * 0.5 + w * i / 30, cy + w * 0.3 + w * 0.16 * math.sin(math.pi * (i / 30) ** 0.8)) for i in range(31)]
        out.append(A.union(*[A.circle(0.65 + 0.9 * math.sin(math.pi * (i / 30) ** 0.7), x, y, 24)
                             for i, (x, y) in enumerate(kp)]))
    return A.union(*out)


def tac(cx, cy, w):
    """Gelin tacı: beş sivri uç, uçlarda inci, altta bant."""
    h = w * 0.42
    pts = [(-w / 2, 0.0), (-w / 2, h * 0.5), (-w * 0.28, h * 0.25), (-w * 0.16, h * 0.78), (0.0, h * 0.4),
           (w * 0.16, h * 0.78), (w * 0.28, h * 0.25), (w / 2, h * 0.5), (w / 2, 0.0)]
    govde = A.polygon(pts).offset(-0.5, J).offset(0.5, J)
    inci = A.union(*[A.circle(w * 0.055, x, y + w * 0.06) for x, y in ((-w / 2, h * 0.5), (-w * 0.16, h * 0.78),
                                                                        (w * 0.16, h * 0.78), (w / 2, h * 0.5))])
    inci = inci + A.circle(w * 0.07, 0.0, h * 0.4 + w * 0.08)
    bant = A.rrect(w * 1.04, h * 0.2, h * 0.06, 0.0, -h * 0.02)
    tas = A.union(*[A.circle(w * 0.035, x, -h * 0.02) for x in (-w * 0.3, 0.0, w * 0.3)])
    return katmanla([govde + inci, bant - tas.offset(0.0, J)], 0.7).translate((cx, cy))


def parilti(cx, cy, r, k=0.2):
    """Dört kollu parıltı."""
    return A.polygon([(0, r), (r * k, r * k), (r, 0), (r * k, -r * k), (0, -r), (-r * k, -r * k), (-r, 0),
                      (-r * k, r * k)]).translate((cx, cy))


def kalp(cx, cy, w):
    pts = [(16 * math.sin(a) ** 3, 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
           for a in [2 * math.pi * i / 160 for i in range(160)]]
    k = w / 32.0
    return A.polygon([(cx + x * k, cy + y * k) for x, y in pts])


def kelebek(cx, cy, w):
    """Kelebek: dört kanat, gövde ve iki anten."""
    ust = elips(w * 0.24, w * 0.17).rotate(28).translate((-w * 0.22, w * 0.1))
    alt = elips(w * 0.16, w * 0.12).rotate(-30).translate((-w * 0.17, -w * 0.15))
    kanat = katmanla([alt, ust], 0.7)
    kanatlar = kanat + kanat.transform([[-1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    govde = elips(w * 0.045, w * 0.24)
    anten = A.stroke([(-0.6, w * 0.2), (-w * 0.12, w * 0.38)], 1.0) + A.stroke([(0.6, w * 0.2), (w * 0.12, w * 0.38)], 1.0)
    return ((kanatlar - govde.offset(0.8, J)) + govde + anten).translate((cx, cy))


def damla(cx, cy, h):
    """Serum damlası."""
    pts = [(0.0, h / 2)] + [(h * 0.32 * math.cos(a), -h * 0.18 + h * 0.32 * math.sin(a))
                            for a in [math.radians(20 - i * 4) for i in range(46)]]
    return A.polygon(A.smooth(pts, closed=True, n=120)).translate((cx, cy))


def makas(cx, cy, h, aci=-28.0):
    return S.ic_scissors(cx, cy, h, aci)


# ---------------------------------------------------------------- 9 × 12 cm (x −54..54, y ~12..86)

X0, X1 = -54.0, 54.0


def g_defne():
    """Bayan kuaförü: beyaz gövde, pudra çiçekler, mürdüm yazı; üç çiçekli dal sol üstte, solda yazılar, sağda QR."""
    d = Tasarim("g_defne", acik(WHITE))
    q = qr_entry("defnekuafor")
    d.add(None, dal([(-54.0, 66.0), (-46.0, 74.0), (-34.0, 79.0), (-20.0, 80.0)], 4, 5.2), GUL)
    for x, y, r in ((-49.0, 77.0, 5.6), (-33.0, 84.0, 4.2), (-20.0, 80.0, 4.8)):
        yap, gob = cicek(x, y, r)
        d.add(None, yap, PUDRA)
        d.add(None, gob, GUL)
    d.add("Defne", t("pacifico", "Defne", 14.0, X0, 62.5, "l", 0.0, 62.0), MURDUM)
    d.add("KUAFÖR", t("baloo", "BAYAN KUAFÖRÜ", 4.4, X0, 44.0, "l", 1.2, 60.0), GUL)
    d.add("hizmet 1", t("baloo", "KESİM · FÖN · BOYA", 4.4, X0, 35.6, "l", 0.4, 60.0), MURDUM)
    d.add("hizmet 2", t("baloo", "GELİN SAÇI · BAKIM", 4.4, X0, 29.0, "l", 0.4, 60.0), MURDUM)
    d.add("telefon", t("baloo", PHONE, 5.4, X0, 19.0, "l", 0.4, 60.0), MURDUM)
    tile = d.qr(q, 34.0, 52.0, 36.0, sq=MURDUM)
    d.add("RANDEVU", t("baloo", "RANDEVU", 4.2, 34.0, tile.bounds()[1] - 5.8, "c", 1.8, 40.0), GUL)
    d.add(None, kalp(34.0, tile.bounds()[1] - 12.4, 4.2), GUL)
    return d


def g_sakayik():
    """Güzellik salonu: pudra gövde, beyaz şakayık ve yapraklar, mürdüm yazı; QR beyaz karoda."""
    d = Tasarim("g_sakayik", acik(PUDRA))
    q = qr_entry("sakayikguzellik")
    d.add(None, sakayik(-37.0, 64.0, 15.5), WHITE)
    for a in (205.0, 250.0, 330.0):
        x, y = -37.0 + 14.6 * math.cos(math.radians(a)), 64.0 + 14.6 * math.sin(math.radians(a))
        d.add(None, yaprak(x, y, 9.0, a, 4.2), WHITE)
    d.add("Şakayık", t("frauncesi", "Şakayık", 12.0, -16.0, 70.0, "l", 0.2, 34.0), MURDUM)
    d.add("GÜZELLİK", t("baloo", "GÜZELLİK", 4.6, -15.0, 58.0, "l", 1.0, 32.0), MURDUM)
    d.add("SALONU", t("baloo", "SALONU", 4.6, -15.0, 51.0, "l", 1.0, 32.0), MURDUM)
    d.add("hizmet", t("baloo", "CİLT · KAŞ · MANİKÜR", 4.4, X0, 35.0, "l", 0.3, 64.0), MURDUM)
    d.add(None, bar(X0, -10.0, 27.8, 1.2), WHITE)
    d.add("telefon", t("baloo", PHONE, 5.4, X0, 19.0, "l", 0.4, 62.0), MURDUM)
    tile = d.qr(q, 36.0, 49.0, 34.0, sq=MURDUM, karo=WHITE)
    d.add("RANDEVU", t("baloo", "RANDEVU", 4.2, 36.0, tile.bounds()[1] - 5.6, "c", 1.8, 36.0), MURDUM)
    return d


def g_lal():
    """Tırnak stüdyosu: ten rengi gövde, fuşya oje, moka yazı; QR solda beyaz karoda."""
    d = Tasarim("g_lal", acik(NUDE))
    q = qr_entry("lalnails")
    tile = d.qr(q, -34.0, 50.0, 36.0, sq=MOKA, karo=WHITE)
    d.add("TARA", t("baloo", "RANDEVU AL", 4.4, -34.0, tile.bounds()[1] - 5.8, "c", 1.0, 40.0), FUSYA)
    x = -8.0
    sise, kapak = oje(x + 8.0, 70.0, 20.0)
    d.add(None, sise, FUSYA)
    d.add(None, kapak, MOKA)
    for i, (px, py, r) in enumerate(((x + 21.0, 78.0, 2.6), (x + 25.0, 71.5, 1.7), (x - 2.0, 77.0, 1.8))):
        d.add(None, parilti(px, py, r * 1.4), FUSYA if i else MOKA)
    d.add("Lâl", t("kaushan", "Lâl", 14.0, x + 32.0, 66.0, "l", 0.0, 30.0), MOKA)
    d.add("NAIL", t("baloo", "TIRNAK STÜDYOSU", 4.2, x, 49.0, "l", 1.0, 62.0), FUSYA)
    d.add("hizmet 1", t("baloo", "MANİKÜR · PEDİKÜR", 4.4, x, 40.0, "l", 0.4, 62.0), MOKA)
    d.add("hizmet 2", t("baloo", "PROTEZ · NAIL ART", 4.4, x, 33.2, "l", 0.4, 62.0), MOKA)
    d.add("telefon", t("baloo", PHONE, 5.4, x, 20.0, "l", 0.4, 62.0), MOKA)
    return d


def g_ela():
    """Kirpik ve kaş stüdyosu: siyah gövde, rose gold göz ve kirpik, pudra el yazısı; ortalı başlık."""
    d = Tasarim("g_ela", koyu(BLACK))
    q = qr_entry("elalashbrow")
    cx = -24.0
    d.add("simge", kirpik(cx, 73.5, 24.0, kas=True), ROSE)
    d.add("Ela", t("yester", "Ela", 16.0, cx, 52.5, "c", 0.0, 56.0), PUDRA)
    d.add("LASH", t("baloo", "LASH & BROW", 4.4, cx, 39.0, "c", 2.0, 58.0), ROSE)
    d.add("hizmet", t("baloo", "KİRPİK · KAŞ · LİFTİNG", 4.3, cx, 30.6, "c", 0.3, 58.0), WHITE)
    d.add("telefon", t("baloo", PHONE, 5.2, cx, 19.5, "c", 0.4, 58.0), WHITE)
    tile = d.qr(q, 33.0, 51.0, 36.0)
    d.add("RANDEVU", t("baloo", "RANDEVU", 4.2, 33.0, tile.bounds()[1] - 5.8, "c", 1.8, 40.0), ROSE)
    return d


def g_gulce():
    """Cilt bakım: krem gövde, solda dikey güllü dal (gül kurusu ve adaçayı), moka yazı; sağda QR."""
    d = Tasarim("g_gulce", acik(KREM))
    q = qr_entry("gulceciltbakim")
    d.add(None, dal([(-49.0, 14.0), (-47.0, 34.0), (-50.0, 54.0), (-47.0, 72.0)], 6, 6.4, uc=False), ADACAYI)
    for x, y, r in ((-46.5, 79.0, 6.6), (-50.0, 58.0, 4.6), (-46.0, 37.0, 5.2)):
        d.add(None, gul(x, y, r), GUL)
    x = -36.0
    d.add("Gülce", t("fraunces", "Gülce", 13.0, x, 70.0, "l", 0.2, 46.0), MOKA)
    d.add("CİLT BAKIM", t("baloo", "CİLT BAKIM", 4.6, x, 56.0, "l", 2.0, 46.0), GUL)
    d.add("hizmet 1", t("baloo", "CİLT ANALİZİ", 4.4, x, 46.2, "l", 0.4, 46.0), MOKA)
    d.add("hizmet 2", t("baloo", "LEKE · AKNE · NEM", 4.4, x, 39.2, "l", 0.4, 46.0), MOKA)
    d.add("telefon", t("baloo", PHONE, 5.0, x, 20.0, "l", 0.4, 48.0), MOKA)
    d.add(None, damla(x + 2.0, 29.0, 6.4), ADACAYI)
    d.add("RANDEVU", t("baloo", "RANDEVU", 4.0, x + 7.0, 29.0, "l", 1.4), ADACAYI)
    d.qr(q, 34.0, 50.0, 36.0, sq=MOKA)
    return d


def g_ipek():
    """Lazer epilasyon: lila gövde, beyaz parıltılar ve el yazısı, mürdüm küçük yazı; QR beyaz karoda, ortada üstte."""
    d = Tasarim("g_ipek", acik(LILA))
    q = qr_entry("ipeklazer")
    d.add("İpek", t("pacifico", "İpek", 15.0, -27.0, 64.0, "c", 0.0, 50.0), WHITE)
    for px, py, r in ((-50.0, 80.0, 4.6), (-43.0, 72.5, 2.6), (-4.0, 80.0, 3.6), (-8.0, 50.0, 2.2)):
        d.add(None, parilti(px, py, r), WHITE)
    d.add("LAZER", t("baloo", "LAZER EPİLASYON", 4.6, -27.0, 45.6, "c", 0.8, 56.0), MURDUM)
    d.add(None, bar(-38.0, -16.0, 39.0, 1.2), WHITE)
    d.add("hizmet", t("baloo", "BUZ LAZER · BÖLGESEL", 4.4, -27.0, 32.4, "c", 0.4, 56.0), MURDUM)
    d.add("telefon", t("baloo", PHONE, 5.2, -27.0, 20.0, "c", 0.4, 54.0), MURDUM)
    tile = d.qr(q, 33.0, 53.0, 36.0, sq=MURDUM, karo=WHITE)
    d.add("İLK SEANS", t("baloo", "RANDEVU", 4.2, 33.0, tile.bounds()[1] - 5.8, "c", 1.8, 40.0), WHITE)
    return d


def g_duru():
    """Makyaj stüdyosu: beyaz gövde, rose gold ruj ve fiyonk, siyah el yazısı; sağda rose gold çerçeveli QR."""
    d = Tasarim("g_duru", acik(WHITE))
    q = qr_entry("durumakeup")
    uc, govde = ruj(-48.0, 67.0, 19.0)
    d.add(None, uc, PUDRA)
    d.add("simge", govde, ROSE)
    d.add("Duru", t("norican", "Duru", 18.0, -40.0, 66.0, "l", 0.0, 46.0), BLACK)
    d.add("MAKEUP", t("baloo", "MAKEUP STUDIO", 4.6, X0, 47.0, "l", 1.8, 62.0), ROSE)
    d.add("hizmet 1", t("baloo", "GELİN · NİŞAN · ÖZEL GÜN", 4.3, X0, 37.6, "l", 0.3, 62.0), BLACK)
    d.add("hizmet 2", t("baloo", "MAKYAJ EĞİTİMİ", 4.3, X0, 31.0, "l", 0.3, 62.0), BLACK)
    d.add("telefon", t("baloo", PHONE, 5.4, X0, 19.0, "l", 0.4, 62.0), BLACK)
    tile = d.qr(q, 34.0, 51.0, 34.0, sq=BLACK, frame=ROSE)
    d.add(None, fiyonk(34.0, tile.bounds()[3] + 9.5, 15.0), PUDRA)
    d.add("RANDEVU", t("baloo", "RANDEVU", 4.0, 34.0, tile.bounds()[1] - 8.4, "c", 1.6, 40.0), ROSE)
    return d


def g_lotus():
    """Spa ve masaj: adaçayı gövde, beyaz nilüfer ve yazı, moka küçük yazı; nilüferin altında ortalı ad."""
    d = Tasarim("g_lotus", acik(ADACAYI))
    q = qr_entry("lotusspa")
    cx = -25.0
    d.add("simge", lotus(cx, 66.0, 19.0), WHITE)
    d.add(None, bar(cx - 14.0, cx + 14.0, 64.4, 1.2), WHITE)
    d.add("LOTUS", t("fraunces", "Lotus", 12.5, cx, 52.0, "c", 0.4, 54.0), WHITE)
    d.add("SPA", t("baloo", "SPA & MASAJ", 4.6, cx, 40.0, "c", 2.0, 56.0), MOKA)
    d.add("hizmet", t("baloo", "MASAJ · HAMAM · KESE", 4.4, cx, 31.0, "c", 0.3, 58.0), MOKA)
    d.add("telefon", t("baloo", PHONE, 5.2, cx, 19.5, "c", 0.4, 58.0), WHITE)
    tile = d.qr(q, 33.0, 51.0, 36.0, sq=MOKA, karo=WHITE)
    d.add("RANDEVU", t("baloo", "RANDEVU", 4.2, 33.0, tile.bounds()[1] - 5.8, "c", 1.8, 40.0), WHITE)
    return d


def g_zarif():
    """Gelin saçı ve makyaj: beyaz gövde, rose gold taç ve çelenk, pudra çiçek, siyah el yazısı; çelenkli rozet solda."""
    d = Tasarim("g_zarif", acik(WHITE))
    q = qr_entry("zarifgelin")
    cx, cy, R = -30.0, 59.0, 17.5
    d.add(None, celenk(cx, cy, R, adet=6, L=5.6, bosluk=64.0), ROSE)
    yap, gob = cicek(cx, cy - R, 4.6)
    d.add(None, yap, PUDRA)
    d.add(None, gob, ROSE)
    d.add("simge", tac(cx, cy + R - 1.0, 12.0), ROSE)
    d.flat("Zarif", t("dancing", "Zarif", 10.0, cx - 0.8, cy + 2.0, "c", 0.0, 22.0), BLACK)   # ince el yazısı: dolgu
    d.flat("GELİN", t("baloo", "GELİN BAŞI", 3.4, cx, cy - 6.8, "c", 0.4, 18.0), ROSE)   # küçük: dolgu
    d.add("hizmet", t("baloo", "SAÇ · MAKYAJ · NİŞAN", 4.4, cx, 29.0, "c", 0.3, 52.0), BLACK)
    d.add("telefon", t("baloo", PHONE, 5.0, cx, 19.5, "c", 0.4, 48.0), BLACK)
    tile = d.qr(q, 34.0, 53.0, 36.0, sq=BLACK)
    d.add("RANDEVU", t("baloo", "RANDEVU", 4.2, 34.0, tile.bounds()[1] - 5.8, "c", 1.8, 40.0), ROSE)
    d.add(None, kalp(34.0, tile.bounds()[1] - 12.6, 4.0), PUDRA)
    return d


def g_papatya():
    """Kuaför ve güzellik: fuşya gövde, beyaz papatyalar (sarı göbek), beyaz el yazısı; QR beyaz karoda."""
    d = Tasarim("g_papatya", koyu(FUSYA))
    q = qr_entry("papatyaguzellik")
    for x, y, r in ((-50.0, 80.0, 7.0), (-38.0, 83.0, 4.6), (5.0, 19.0, 5.4)):
        yap, gob = papatya(x, y, r)
        d.add(None, yap, WHITE)
        d.add(None, gob, YELLOW)
    d.add("Papatya", t("pacifico", "Papatya", 12.5, X0, 62.0, "l", 0.0, 62.0), WHITE)
    d.add("KUAFÖR", t("baloo", "KUAFÖR & GÜZELLİK", 4.6, X0, 46.0, "l", 0.5, 60.0), YELLOW)
    d.add("hizmet", t("baloo", "SAÇ · MAKYAJ · TIRNAK", 4.4, X0, 37.4, "l", 0.3, 60.0), WHITE)
    d.add("telefon", t("baloo", PHONE, 5.2, X0, 27.0, "l", 0.4, 46.0), WHITE)
    tile = d.qr(q, 34.0, 53.0, 36.0, sq=BLACK, karo=WHITE)
    d.add("RANDEVU", t("baloo", "RANDEVU", 4.2, 34.0, tile.bounds()[1] - 5.8, "c", 1.8, 40.0), YELLOW)
    return d


# ---------------------------------------------------------------- 10 × 20 cm (x −90..90, y ~12..94; dolgu)

def p_aylin():
    """Saç tasarımcısı (Defne Kuaför): beyaz gövde, üstte boydan boya çiçekli dal, el yazısı ad; mürdüm, gül kurusu,
    pudra."""
    d = Tasarim("p_aylin", acik(WHITE))
    q = qr_entry("defnekuafor-aylin")
    d.flat(None, dal([(-88.0, 84.0), (-60.0, 89.0), (-30.0, 86.0), (-2.0, 90.0), (24.0, 87.0)], 8, 6.0, en=1.0), GUL)
    for x, y, r in ((-74.0, 87.5, 4.6), (-44.0, 88.5, 3.6), (-16.0, 87.5, 4.2), (24.0, 87.0, 5.0)):
        yap, gob = cicek(x, y, r, ara=0.6)
        d.flat(None, yap - A.circle(r * 0.3, x, y).offset(0.6, J), PUDRA)
        d.flat(None, gob, GUL)
    d.flat("ad", t("dancing", "Aylin Ersoy", 16.0, -86.0, 64.0, "l", 0.0, 112.0), MURDUM)
    d.flat("unvan", t("josefin", "SAÇ TASARIMCISI", 5.6, -86.0, 45.0, "l", 2.2, 112.0), GUL)
    d.flat(None, bar(-86.0, -56.0, 37.0, 1.0), PUDRA)
    d.flat("büro", t("josefin", "DEFNE KUAFÖR", 4.8, -86.0, 29.0, "l", 1.6, 112.0), MURDUM)
    d.flat("telefon", t("josefin", PHONE, 5.6, -86.0, 19.0, "l", 0.6, 112.0), MURDUM)
    d.flat("simge", makas(14.0, 26.0, 16.0, -20.0), GUL)
    tile = d.qr(q, 66.0, 50.0, 38.0, sq=MURDUM, frame=GUL, flat=True)
    d.flat("RANDEVU", t("josefin", "RANDEVU", 4.4, 66.0, tile.bounds()[1] - 9.0, "c", 2.0, 44.0), GUL)
    return d


def p_buse():
    """Nail artist (Lâl Nails): ten rengi gövde, solda üç oje, el yazısı ad; moka, fuşya, beyaz karo."""
    d = Tasarim("p_buse", acik(NUDE))
    q = qr_entry("lalnails-buse")
    for i, (x, h) in enumerate(((-80.0, 16.0), (-68.0, 20.0), (-56.0, 16.0))):
        sise, kapak = oje(x, 74.0 + (h - 16.0) * 0.3, h)
        d.flat(None, sise, (FUSYA, PUDRA, FUSYA)[i])
        d.flat(None, kapak, MOKA)
    d.flat(None, parilti(-44.0, 84.0, 3.6) + parilti(-38.5, 77.0, 2.2), WHITE)
    d.flat("ad", t("playball", "Buse Yalçın", 15.0, -86.0, 52.0, "l", 0.0, 118.0), MOKA)
    d.flat("unvan", t("josefin", "NAIL ARTIST", 6.0, -86.0, 35.0, "l", 2.6, 112.0), FUSYA)
    d.flat("büro", t("quick", "Lâl Nails · Tırnak Stüdyosu", 5.0, -86.0, 26.0, "l", 0.2, 112.0), MOKA)
    d.flat("telefon", t("quick", PHONE, 5.6, -86.0, 16.5, "l", 0.4, 112.0), MOKA)
    tile = d.qr(q, 66.0, 56.0, 38.0, sq=MOKA, karo=WHITE)
    d.flat("RANDEVU", t("josefin", "RANDEVU", 4.4, 66.0, tile.bounds()[1] - 6.4, "c", 2.0, 44.0), FUSYA)
    return d


def p_gizem():
    """Uzman estetisyen (Şakayık Güzellik): pudra gövde, solda iri beyaz şakayık, klasik harfli ad; mürdüm."""
    d = Tasarim("p_gizem", acik(PUDRA))
    q = qr_entry("sakayikguzellik-gizem")
    d.flat(None, sakayik(-68.0, 56.0, 19.0, 0.7), WHITE)
    for a in (200.0, 240.0, 320.0, 140.0):
        x, y = -68.0 + 18.0 * math.cos(math.radians(a)), 56.0 + 18.0 * math.sin(math.radians(a))
        d.flat(None, yaprak(x, y, 11.0, a, 5.0), WHITE)
    x = -40.0
    d.flat("ad", t("marcellus", "GİZEM AKSU", 10.0, x, 72.0, "l", 0.8, 80.0), MURDUM)
    d.flat("unvan", t("frauncesy", "Uzman Estetisyen", 7.0, x, 57.0, "l", 0.0, 90.0), MURDUM)
    d.flat(None, bar(x, x + 26.0, 47.0, 1.0), WHITE)
    d.flat("büro", t("josefin", "ŞAKAYIK GÜZELLİK SALONU", 4.6, x, 37.0, "l", 0.6, 80.0), MURDUM)
    d.flat("telefon", t("josefin", PHONE, 5.6, x, 25.0, "l", 0.6, 76.0), MURDUM)
    tile = d.qr(q, 66.0, 56.0, 36.0, sq=MURDUM, karo=WHITE)
    d.flat("RANDEVU", t("josefin", "RANDEVU", 4.2, 66.0, tile.bounds()[1] - 6.2, "c", 2.0, 40.0), MURDUM)
    return d


def p_ceren():
    """Makeup artist: beyaz gövde, siyah el yazısı ad, rose gold ruj ve fiyonk; rose gold çerçeveli QR."""
    d = Tasarim("p_ceren", acik(WHITE))
    q = qr_entry("cerenuysal")
    uc, govde = ruj(-79.0, 70.0, 26.0)
    d.flat(None, uc, PUDRA)
    d.flat("simge", govde, ROSE)
    d.flat("ad", t("norican", "Ceren Uysal", 15.0, -66.0, 70.0, "l", 0.0, 104.0), BLACK)
    d.flat("unvan", t("josefin", "MAKEUP ARTIST", 6.0, -86.0, 46.0, "l", 2.8, 116.0), ROSE)
    d.flat("büro", t("josefin", "GELİN · NİŞAN · ÖZEL GÜN · EĞİTİM", 4.2, -86.0, 35.0, "l", 0.8, 116.0), BLACK)
    d.flat("telefon", t("josefin", PHONE, 5.6, -86.0, 22.0, "l", 0.6, 116.0), BLACK)
    tile = d.qr(q, 66.0, 50.0, 36.0, sq=BLACK, frame=ROSE, flat=True)
    d.flat(None, fiyonk(66.0, tile.bounds()[3] + 11.0, 18.0), PUDRA)
    d.flat("PORTFOLYO", t("josefin", "PORTFOLYO", 4.0, 66.0, tile.bounds()[1] - 8.8, "c", 1.8, 44.0), ROSE)
    return d


def p_melis():
    """Lash & brow artist (Ela Lash & Brow): siyah gövde, rose gold göz ve kirpik, pudra el yazısı ad; ortalı sol blok."""
    d = Tasarim("p_melis", koyu(BLACK))
    q = qr_entry("elalashbrow-melis")
    cx = -34.0
    d.flat("simge", kirpik(cx, 80.0, 30.0), ROSE)
    d.flat("ad", t("dancing", "Melis Tan", 16.0, cx, 59.0, "c", 0.0, 100.0), PUDRA)
    d.flat("unvan", t("josefin", "LASH & BROW ARTIST", 5.4, cx, 41.0, "c", 2.0, 104.0), ROSE)
    d.flat("büro", t("josefin", "KİRPİK LİFTİNG · KAŞ LAMİNASYON", 4.2, cx, 31.0, "c", 0.6, 104.0), WHITE)
    d.flat("telefon", t("josefin", PHONE, 5.6, cx, 19.5, "c", 0.6, 104.0), WHITE)
    tile = d.qr(q, 66.0, 54.0, 38.0)
    d.flat("RANDEVU", t("josefin", "RANDEVU", 4.4, 66.0, tile.bounds()[1] - 6.4, "c", 2.0, 44.0), ROSE)
    return d


def p_derya():
    """Cilt bakım uzmanı (Gülce Cilt Bakım): beyaz gövde, solda adaçayı çelenk içinde monogram, klasik harfli ad; moka."""
    d = Tasarim("p_derya", acik(WHITE))
    q = qr_entry("gulceciltbakim-derya")
    cx, cy = -70.0, 56.0
    d.flat(None, celenk(cx, cy, 17.0, adet=6, L=5.4, bosluk=56.0), ADACAYI)
    d.flat(None, gul(cx, cy + 17.0, 4.4, 0.6), GUL)
    d.flat("monogram", t("marcellus", "DI", 12.0, cx, cy - 1.0, "c", 0.6, 22.0), MOKA)
    x = -46.0
    d.flat("ad", t("marcellus", "DERYA ILGIN", 9.6, x, 72.0, "l", 1.0, 82.0), MOKA)
    d.flat("unvan", t("frauncesy", "Cilt Bakım Uzmanı", 6.8, x, 57.0, "l", 0.0, 82.0), ADACAYI)
    d.flat("büro", t("josefin", "GÜLCE CİLT BAKIM", 4.4, x, 41.0, "l", 1.6, 82.0), MOKA)
    d.flat("telefon", t("josefin", PHONE, 5.6, x, 29.0, "l", 0.6, 82.0), MOKA)
    d.flat(None, damla(x + 2.0, 18.0, 6.0), GUL)
    d.flat("cilt", t("josefin", "CİLT ANALİZİ · BAKIM PROGRAMI", 4.2, x + 7.0, 18.0, "l", 0.5, 80.0), GUL)
    tile = d.qr(q, 66.0, 56.0, 36.0, sq=MOKA)
    d.flat("RANDEVU", t("josefin", "RANDEVU", 4.2, 66.0, tile.bounds()[1] - 6.2, "c", 2.0, 40.0), ADACAYI)
    return d


def p_nazli():
    """Lazer epilasyon uzmanı (İpek Lazer): lila gövde, beyaz parıltılar ve el yazısı ad, mürdüm yazılar."""
    d = Tasarim("p_nazli", acik(LILA))
    q = qr_entry("ipeklazer-nazli")
    for px, py, r in ((-84.0, 86.0, 4.4), (-76.0, 80.0, 2.4), (28.0, 84.0, 3.4), (20.0, 40.0, 2.4)):
        d.flat(None, parilti(px, py, r), WHITE)
    d.flat("ad", t("pacifico", "Nazlı Erdem", 13.0, -64.0, 72.0, "l", 0.0, 96.0), WHITE)
    d.flat("unvan", t("josefin", "LAZER EPİLASYON UZMANI", 5.2, -86.0, 50.0, "l", 1.6, 112.0), MURDUM)
    d.flat(None, bar(-86.0, -56.0, 42.0, 1.0), WHITE)
    d.flat("büro", t("josefin", "İPEK LAZER · BUZ LAZER", 4.4, -86.0, 33.0, "l", 1.0, 112.0), MURDUM)
    d.flat("telefon", t("josefin", PHONE, 5.6, -86.0, 21.0, "l", 0.6, 112.0), MURDUM)
    tile = d.qr(q, 66.0, 56.0, 38.0, sq=MURDUM, karo=WHITE)
    d.flat("RANDEVU", t("josefin", "RANDEVU", 4.4, 66.0, tile.bounds()[1] - 6.4, "c", 2.0, 44.0), WHITE)
    return d


def p_pinar():
    """Kalıcı makyaj ve microblading: krem gövde, moka kaş ve göz, rose gold çizgi; altta moka bant (oyma yazı)."""
    d = Tasarim("p_pinar", acik(KREM))
    q = qr_entry("pinarates")
    band = A.rrect(184.0, 18.0, 4.0, 0.0, 20.0)
    yazi = A.union(t("josefin", "MICROBLADING · DUDAK · DİPLİNER", 4.2, -84.0, 20.0, "l", 0.8, 104.0),
                   t("josefin", PHONE, 4.8, 84.0, 20.0, "r", 0.6, 52.0))
    d.lines["bant"] = yazi
    d.flat(None, band - yazi.offset(0.0, J), MOKA)
    d.flat("simge", kirpik(-74.0, 76.0, 22.0, kas=True), MOKA)
    d.flat("ad", t("playball", "Pınar Ateş", 15.0, -58.0, 72.0, "l", 0.0, 90.0), MOKA)
    d.flat("unvan", t("josefin", "KALICI MAKYAJ SANATÇISI", 5.2, -86.0, 51.0, "l", 1.6, 112.0), ROSE)
    d.flat(None, bar(-86.0, 30.0, 42.0, 0.9), ROSE)
    d.flat("not", t("frauncesy", "Doğal, kalıcı, size özel.", 5.4, -86.0, 35.0, "l", 0.0, 112.0), MOKA)
    tile = d.qr(q, 66.0, 63.0, 34.0, sq=MOKA)
    d.flat("RANDEVU", t("josefin", "RANDEVU", 4.0, 66.0, tile.bounds()[1] - 5.6, "c", 1.8, 40.0), ROSE)
    return d


def p_ezgi():
    """Spa ve masaj terapisti (Lotus Spa): adaçayı gövde, beyaz nilüfer ve ad, moka yazılar."""
    d = Tasarim("p_ezgi", acik(ADACAYI))
    q = qr_entry("lotusspa-ezgi")
    d.flat("simge", lotus(-74.0, 66.0, 22.0, 0.7), WHITE)
    d.flat(None, bar(-90.0, -58.0, 64.4, 1.0), WHITE)
    x = -50.0
    d.flat("ad", t("fraunces", "Ezgi Polat", 11.5, x, 76.0, "l", 0.3, 90.0), WHITE)
    d.flat("unvan", t("josefin", "SPA & MASAJ TERAPİSTİ", 5.0, x, 60.0, "l", 1.6, 90.0), MOKA)
    d.flat("büro", t("josefin", "LOTUS SPA · AROMATERAPİ", 4.4, -86.0, 40.0, "l", 1.0, 110.0), MOKA)
    d.flat("telefon", t("josefin", PHONE, 5.6, -86.0, 27.0, "l", 0.6, 110.0), WHITE)
    tile = d.qr(q, 66.0, 56.0, 38.0, sq=MOKA, karo=WHITE)
    d.flat("RANDEVU", t("josefin", "RANDEVU", 4.4, 66.0, tile.bounds()[1] - 6.4, "c", 2.0, 44.0), WHITE)
    return d


def p_burcu():
    """Kurucu (Papatya Güzellik Merkezi): fuşya gövde, beyaz papatyalar (sarı göbek), beyaz el yazısı ad."""
    d = Tasarim("p_burcu", koyu(FUSYA))
    q = qr_entry("papatyaguzellik-burcu")
    for x, y, r in ((-82.0, 84.0, 7.4), (-68.0, 88.0, 4.6), (36.0, 18.0, 5.6), (24.0, 14.5, 3.6)):
        yap, gob = papatya(x, y, r, ara=0.6)
        d.flat(None, yap, WHITE)
        d.flat(None, gob, YELLOW)
    d.flat("ad", t("pacifico", "Burcu Demirel", 12.0, -86.0, 62.0, "l", 0.0, 116.0), WHITE)
    d.flat("unvan", t("josefin", "KURUCU · GÜZELLİK UZMANI", 5.2, -86.0, 43.0, "l", 1.4, 116.0), YELLOW)
    d.flat("büro", t("josefin", "PAPATYA KUAFÖR & GÜZELLİK", 4.4, -86.0, 32.0, "l", 1.0, 116.0), WHITE)
    d.flat("telefon", t("josefin", PHONE, 5.6, -86.0, 20.0, "l", 0.6, 116.0), WHITE)
    tile = d.qr(q, 66.0, 58.0, 38.0, sq=BLACK, karo=WHITE)
    d.flat("RANDEVU", t("josefin", "RANDEVU", 4.4, 66.0, tile.bounds()[1] - 6.4, "c", 2.0, 44.0), YELLOW)
    return d


G9X12 = {"g_defne": g_defne, "g_sakayik": g_sakayik, "g_lal": g_lal, "g_ela": g_ela, "g_gulce": g_gulce,
         "g_ipek": g_ipek, "g_duru": g_duru, "g_lotus": g_lotus, "g_zarif": g_zarif, "g_papatya": g_papatya}
G10X20 = {"p_aylin": p_aylin, "p_buse": p_buse, "p_gizem": p_gizem, "p_ceren": p_ceren, "p_melis": p_melis,
          "p_derya": p_derya, "p_nazli": p_nazli, "p_pinar": p_pinar, "p_ezgi": p_ezgi, "p_burcu": p_burcu}


# ---------------------------------------------------------------- ürün bilgileri (görseller ve README)

# (anahtar, kod, işletme ya da kişi, sektör ya da görev, tasarımın adı, renkler)
URUNLER = [
    ("g_defne", "G01", "Defne Kuaför", "Bayan kuaförü", "Çiçekli dal", "beyaz · pudra · gül kurusu · mürdüm"),
    ("g_sakayik", "G02", "Şakayık Güzellik Salonu", "Güzellik salonu", "Şakayık", "pudra · beyaz · mürdüm"),
    ("g_lal", "G03", "Lâl Nails", "Tırnak stüdyosu", "Oje", "ten rengi · fuşya · moka · beyaz"),
    ("g_ela", "G04", "Ela Lash & Brow", "Kirpik ve kaş", "Kirpik", "siyah · rose gold · pudra · beyaz"),
    ("g_gulce", "G05", "Gülce Cilt Bakım", "Cilt bakım", "Güllü dal", "krem · gül kurusu · adaçayı · moka"),
    ("g_ipek", "G06", "İpek Lazer", "Lazer epilasyon", "Parıltı", "lila · beyaz · mürdüm"),
    ("g_duru", "G07", "Duru Makeup Studio", "Makyaj stüdyosu", "Ruj ve fiyonk", "beyaz · siyah · rose gold · pudra"),
    ("g_lotus", "G08", "Lotus Spa & Masaj", "Spa ve masaj", "Nilüfer", "adaçayı · beyaz · moka"),
    ("g_zarif", "G09", "Zarif Gelin Başı", "Gelin saçı ve makyaj", "Çelenk ve taç", "beyaz · rose gold · pudra · siyah"),
    ("g_papatya", "G10", "Papatya Kuaför & Güzellik", "Kuaför ve güzellik", "Papatya", "fuşya · beyaz · sarı · siyah"),
    ("p_aylin", "K01", "Aylin Ersoy", "Saç tasarımcısı", "Çiçekli dal", "beyaz · pudra · gül kurusu · mürdüm"),
    ("p_buse", "K02", "Buse Yalçın", "Nail artist", "Üç oje", "ten rengi · fuşya · pudra · moka"),
    ("p_gizem", "K03", "Gizem Aksu", "Uzman estetisyen", "Şakayık", "pudra · beyaz · mürdüm"),
    ("p_ceren", "K04", "Ceren Uysal", "Makeup artist", "Ruj ve fiyonk", "beyaz · siyah · rose gold · pudra"),
    ("p_melis", "K05", "Melis Tan", "Lash & brow artist", "Kirpik", "siyah · rose gold · pudra · beyaz"),
    ("p_derya", "K06", "Derya Ilgın", "Cilt bakım uzmanı", "Çelenk monogram", "beyaz · adaçayı · moka · gül kurusu"),
    ("p_nazli", "K07", "Nazlı Erdem", "Lazer epilasyon uzmanı", "Parıltı", "lila · beyaz · mürdüm"),
    ("p_pinar", "K08", "Pınar Ateş", "Kalıcı makyaj sanatçısı", "Kaş ve alt bant", "krem · moka · rose gold"),
    ("p_ezgi", "K09", "Ezgi Polat", "Spa ve masaj terapisti", "Nilüfer", "adaçayı · beyaz · moka"),
    ("p_burcu", "K10", "Burcu Demirel", "Kurucu, güzellik merkezi", "Papatya", "fuşya · beyaz · sarı · siyah"),
]


# ---------------------------------------------------------------- kurulum, dışa aktarma

def _potrace_yoksa():
    """paloma_isimlik, logo çıkarma betiği üzerinden potrace'ı yükler; ölçüler için gerekmez (kurulu değilse boş modül)."""
    try:
        import potrace  # noqa: F401
    except ImportError:
        import types
        sys.modules["potrace"] = types.ModuleType("potrace")


def build(key):
    import uzar_isimlik_baski as B
    if key in G9X12:
        d = G9X12[key]()
        stand, mount = B.stand()
        p = U.Parcalar(S.solids(d), stand, d.sc["body"], mount)
    else:
        _potrace_yoksa()
        import paloma_isimlik_baski as PB                      # 200 × 100 × 5 (modül ölçüleri değişir)
        d = G10X20[key]()
        stand, mount = B.stand(length=PB.STAND_LEN)
        p = U.Parcalar(S.solids_20(d), stand, d.sc["body"], mount)
    p.design = d
    return p


def export(key):
    """Kendi sürecinde: kaynak/<key>.npz (sehpasında panel ve sehpa) ve <key>_duz.png (düz görünüş)."""
    U.BUILDERS[key] = lambda: build(key)
    U.SRC = SRC
    return U.export(key)


FOTO = os.path.join(OUT, "fotograf")
KAPAK = {"9x12": [["g_defne", "g_lal", "g_ipek"], ["g_sakayik", "g_papatya"]],
         "10x20": [["p_aylin", "p_gizem"], ["p_nazli"]]}


def fotograflar(args):
    """boyde_urun_foto'nun stüdyosu (gövdesi açık isimlikler koyu fonda, koyular beyazda): her ürün stüdyo, karşıdan,
    masa; iki kategori kapağı."""
    import boyde_urun_foto as F
    F.SRC, F.OUT, F.KAPAK = SRC, FOTO, KAPAK
    samples = int(args[args.index("--ornek") + 1]) if "--ornek" in args else 32
    keys = [a for a in args if not a.startswith("-") and not a.isdigit()]
    if "--kapak" not in args or keys:
        for key in keys or list(G9X12) + list(G10X20):
            if "--eksik" in args and all(os.path.exists(os.path.join(FOTO, f"{key}_{v}.jpg")) for v in F.VIEWS):
                continue
            F.render(key, list(F.VIEWS), samples, fill=1.0)
            print(f"{key}: fotoğraflar hazır", flush=True)
    if "--kapak" in args or not keys:
        for cat in KAPAK:
            F.cover(cat, samples)
            print(f"kapak_{cat}: hazır", flush=True)


def main():
    if "--foto" in sys.argv:
        return fotograflar([a for a in sys.argv[1:] if a != "--foto"])
    import multiprocessing as mp
    keys = [k for k in sys.argv[1:] if not k.startswith("-")] or list(G9X12) + list(G10X20)
    with mp.get_context("spawn").Pool(4, maxtasksperchild=1) as pool:
        for key, _ in pool.imap_unordered(export, keys):
            print(f"{key:16s} dışa aktarıldı, QR okunmuyor ✓", flush=True)


if __name__ == "__main__":
    import boyde_guzellik                                   # tek modül nesnesi (alt süreçler de bunu yükler)
    boyde_guzellik.main()
