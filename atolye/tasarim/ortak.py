"""Tasarımların ortak parçaları: renkler (filament), kabartma yazı, sektör simgeleri, QR, baskıya uygunluk.

Depodaki kodu kullanır:
  boyde_sektor        tasarım sınıfı (Design: kabartma, dolgu, QR) ve sektör simgeleri
  boyde_kendi         kabartma yazı (lifted: İ / Ö noktaları yukarı alınır ve biraz büyür; bolder: tek çizgili
                      harfler kalınlaşır; ikisi de dilimleyicide denendi)
  uzar_isimlik_baski  gövde, sehpa, harf ölçümü (line_metrics), önizleme
boyde_sektor yüklenince örnek moduna geçilir (QR'lar bozuk, telefon BOYDE'nin; Shopier görselleri için). Burada geri
alınır: müşterinin isimliğinde QR çalışır, telefon müşterinin.

Baskıya uygunluk (0,4 nozul, kabartma 2 mm): yazıda harf içi ve harf arası ≥ 0,7 mm; simgelerde 1,2 mm'den ince yer
az; öğeler kenara 3 mm'den, sehpanın örttüğü alt şeride (9,5 mm) yaklaşmaz; öğeler arası ≥ 1,5 mm.
"""
import math
import sys

from .. import SCRIPTS

if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

import qr_sistemi as Q  # noqa: E402

_TELEFON = Q.phone_e164
import boyde_sektor as S  # noqa: E402
import boyde_kendi as K  # noqa: E402
import segno  # noqa: E402

segno.make = segno.make_gercek                         # örnek modu kapalı: QR'lar çalışır
Q.phone_e164 = _TELEFON

import anahtarlik as A  # noqa: E402
import manifold3d as m3  # noqa: E402
import numpy as np  # noqa: E402
import uzar_isimlik as I  # noqa: E402,F401  (düzenler panelin dış çizgisini buradan alır)
import uzar_isimlik_baski as B  # noqa: E402
from sablonlar.ortak import tr_title, tr_upper  # noqa: E402

J = m3.JoinType.Round
MIN_IC, MIN_ARA = 0.7, 0.7                             # kabartma yazıda harf içi ve harf arası (mm)

# ---------------------------------------------------------------- renkler

BLACK, YELLOW, WHITE, BLUE, RED, GOLD = A.BLACK, A.YELLOW, A.WHITE, A.BLUE, A.RED, A.GOLD
TURQ, PINK, GREEN, ORANGE, NAVY, PURPLE, GRAY = S.TURQ, S.PINK, S.GREEN, S.ORANGE, S.NAVY, S.PURPLE, K.GRAY

# kimlik: ad, 3MF'teki renk (Bambu PLA Basic'e yakın), önizleme tonu, sitedeki vurgu rengi
RENK = {
    BLACK: ("siyah", "#000000", (36, 36, 39), "#121316"),
    WHITE: ("beyaz", "#FFFFFF", (246, 246, 242), "#F4F1EA"),
    RED: ("kırmızı", "#C12E1F", (214, 26, 36), "#E3001B"),
    YELLOW: ("sarı", "#F4EE2A", (250, 204, 24), "#F6C400"),
    BLUE: ("mavi", "#0A2989", (28, 66, 168), "#1F5BD6"),
    GOLD: ("altın", "#E4BD68", (205, 160, 78), "#D4A24C"),
    TURQ: ("turkuaz", "#00B1B7", (0, 160, 190), "#00A3C4"),
    PINK: ("pembe", "#F55A74", (238, 120, 150), "#E8668C"),
    GREEN: ("yeşil", "#00AE42", (0, 150, 80), "#14A05A"),
    ORANGE: ("turuncu", "#FF6A13", (250, 106, 30), "#FF5A1F"),
    NAVY: ("lacivert", "#1F2A56", (30, 44, 90), "#2B3C7A"),
    PURPLE: ("mor", "#5E43B7", (104, 72, 178), "#6B4BC8"),
    GRAY: ("gri", "#8E9089", (139, 142, 148), "#8B8E94"),
}
AD = {k: v[0] for k, v in RENK.items()}
KIMLIK = {v[0]: k for k, v in RENK.items()}
TON = {k: v[2] for k, v in RENK.items()}
WEB = {k: v[3] for k, v in RENK.items()}
KOYUDA = [RED, ORANGE, YELLOW, GOLD, TURQ, PINK, GREEN, GRAY]          # siyah gövdede okunan vurgular
ACIKTA = [RED, ORANGE, BLUE, NAVY, GOLD, TURQ, PINK, GREEN, PURPLE]    # beyaz gövdede


def _kaydet():
    """Yeni renkleri 3MF yazıcısına (anahtarlik), önizlemeye ve yıkama tablosuna tanıtır. Yıkama hacmi benzer
    renkten alınır (turkuaz mavi gibi, turuncu kırmızı gibi...)."""
    benzer = {TURQ: BLUE, PINK: RED, GREEN: BLUE, ORANGE: RED, NAVY: BLUE, PURPLE: BLUE, GRAY: GOLD}
    for k, (ad, hexc, ton, _) in RENK.items():
        A.COLOURS.setdefault(k, hexc)
        A.COLOUR_NAMES.setdefault(k, ad)
        A.SHOW[k] = B.SHOW[k] = ton
        S.NAMES[k] = ad
        S.U.RGB.setdefault(k, ton)
    n = max(RENK)
    if len(A.FLUSH) >= n:
        return
    for row in A.FLUSH:
        row.extend([0] * (n - len(row)))
    A.FLUSH.extend([[0] * n for _ in range(n - len(A.FLUSH))])
    for c, b in benzer.items():
        for i in range(7):
            A.FLUSH[i][c - 1] = A.FLUSH[i][b - 1]
    for c, b in benzer.items():
        A.FLUSH[c - 1] = list(A.FLUSH[b - 1])
    for i in range(n):
        for j in range(n):
            A.FLUSH[i][j] = 0 if i == j else (A.FLUSH[i][j] or 250)


_kaydet()


class Palet:
    """Gövde (siyah ya da beyaz), yazı (gövdenin tersi), vurgu ve isteğe bağlı ikinci vurgu."""

    def __init__(self, govde, vurgu, vurgu2=0):
        self.govde, self.vurgu, self.vurgu2 = govde, vurgu, vurgu2

    @property
    def koyu(self):
        return self.govde == BLACK

    @property
    def yazi(self):
        return WHITE if self.koyu else BLACK

    @property
    def sc(self):
        return {"body": self.govde, "fg": self.yazi, "dark": self.koyu}

    def renk(self, rol):
        return {"yazi": self.yazi, "vurgu": self.vurgu, "vurgu2": self.vurgu2 or self.vurgu,
                "govde": self.govde}[rol]

    @property
    def ad(self):
        return f"{AD[self.govde]} zemin · {AD[self.vurgu]}" + (f" · {AD[self.vurgu2]}" if self.vurgu2 else "")


# ---------------------------------------------------------------- yazı

S.FONTS.update({"oswald": "Oswald-Bold.ttf", "anton": "Anton-Regular.ttf", "russo": "RussoOne-Regular.ttf",
                "archivo": "ArchivoBlack-Regular.ttf", "poppins": "Poppins-ExtraBold.ttf",
                "poppins_i": "Poppins-ExtraBoldItalic.ttf", "michroma": "Michroma-Regular.ttf",
                "fraunces": "Fraunces-Black.ttf", "unbounded": "Unbounded-ExtraBold.ttf",
                "manrope": "Manrope-ExtraBold.ttf", "teko": "Teko-Bold.ttf"})
YAZI_AD = {"lexend": "Lexend", "outfit": "Outfit", "bebas": "Bebas Neue", "lora": "Lora", "mont": "Montserrat",
           "cinzel": "Cinzel", "sora": "Sora", "righteous": "Righteous", "sairai": "Saira eğik",
           "playfair": "Playfair", "oswald": "Oswald", "anton": "Anton", "russo": "Russo One",
           "archivo": "Archivo Black", "poppins": "Poppins", "poppins_i": "Poppins eğik", "michroma": "Michroma",
           "fraunces": "Fraunces", "unbounded": "Unbounded", "manrope": "Manrope", "teko": "Teko", "jost": "Jost",
           "syne": "Syne", "sg7": "Space Grotesk"}
KUCUK_HARFLI = {"lora", "playfair", "fraunces"}       # adı büyük harfe çevrilmeyen (zarif) yazı tipleri
SATIR = "outfit"                                       # küçük satırlar (hizmetler, telefon): kabartmada denenmiş


def font(k):
    return S.font(k)


def genislik(k, s, cap, tr=0.0):
    return S.font(k).width(s, cap, tr)


def sigan(k, s, cap, max_w, tr=0.0):
    """max_w'ya sığan en büyük büyük-harf boyu (en çok cap)."""
    return S.font(k).fit_cap(s, cap, max_w, tr) if max_w else cap


MIN_BOY = 4.4                                          # küçük satırların en küçük boyu: Outfit'te harf içi ≥ 0,7 mm


def sigdir(k, s, cap, max_w, tr=0.0, min_cap=MIN_BOY, min_tr=0.5):
    """Yazı max_w'ya sığsın: önce harf aralığı (en az min_tr), sonra boy daralır; boy min_cap'in altına inmez
    (inerse yazı taşar, kontrol yakalar). Döner (boy, harf aralığı)."""
    f = S.font(k)
    if not max_w or f.width(s, cap, tr) <= max_w:
        return cap, tr
    n = max(len(s) - 1, 1)
    t = (max_w - f.width(s, cap, 0.0)) / n
    if t >= min_tr:
        return cap, min(tr, t)
    tr = min(tr, min_tr)
    return max(f.fit_cap(s, cap, max_w, tr), min(min_cap, cap)), tr


def _noktalar(g, cap, ara=0.8, grow=0.08):
    """Bir harfin işaretleri (İ, Ö, Ü'nün noktaları, Ğ'nin şapkası; taban çizgisi 0): harfle arası `ara` olana kadar
    yukarı alınır, küçükse biraz büyür (boyde_kendi.lifted gibi: küçülen nokta dilimleyicide basılmıyor); iki nokta
    arası da en az `ara`. Harfin gövdesi birden çok parçaysa (Cinzel K'nın bacağı kılcal araklı) birleşir."""
    body, marks = [], []
    for p in g.decompose():
        b = p.bounds()
        (marks if b[1] > cap * 0.55 and p.area() < 0.06 * cap * cap else body).append(p)
    if not marks:
        return g if len(body) < 2 else A.union(*body).offset(0.45, J).offset(-0.45, J)
    body = A.union(*body)
    if len(body.decompose()) > 1:
        body = body.offset(0.45, J).offset(-0.45, J)
    r = ara / 2 - 0.005
    marks = [p.offset(grow, J) if p.area() < 2.5 else p for p in sorted(marks, key=lambda p: p.bounds()[0])]
    if len(marks) == 2:
        for _ in range(20):
            if (marks[0].offset(r, J) ^ marks[1].offset(r, J)).is_empty():
                break
            marks = [marks[0].translate((-0.05, 0.0)), marks[1].translate((0.05, 0.0))]
    out = []
    for p in marks:
        for _ in range(20):
            if (p.offset(r, J) ^ body.offset(r, J)).is_empty():
                break
            p = p.translate((0.0, 0.1))
        out.append(p)
    return A.union(body, *out)


def _dizi(f, s, cap, tr, ara, kabartma):
    """Harfleri tek tek dizer; iki harf arası `ara`dan darsa (kerning, eğik yazı) sağdaki harf kaydırılır.
    Döner (taban çizgisi 0'da, sol kenarı 0'da şekil, genişlik)."""
    glyphs, _ = f.layout(s, cap, tr)
    k = cap / f.cap_units
    placed, prev, shift, end = [], None, 0.0, 0.0
    for gid, gx, gy, adv in glyphs:
        cont = f._outline(gid)
        if not cont:
            end = gx + shift + adv
            continue
        g = m3.CrossSection([c * k + (gx + shift, gy) for c in cont], m3.FillRule.NonZero)
        g = _noktalar(g, cap)
        if kabartma:
            g = K.bolder(g)
        if prev is not None:
            r = ara / 2 - 0.005
            for _ in range(40):
                if (prev.offset(r, J) ^ g.offset(r, J)).is_empty():
                    break
                g = g.translate((0.1, 0.0))
                shift += 0.1
        placed.append(g)
        prev = g
        end = gx + shift + adv
    return (A.union(*placed) if placed else A.empty()), end


def yazi(k, s, cap, x, y, align="l", tr=0.0, max_w=None, ara=0.8, kabartma=True, min_cap=0.0):
    """Kabartma yazı; y büyük harflerin ortası. Harf arası en az `ara` mm (dar düşen çiftler açılır); İ / Ö noktaları
    yukarı alınır ve büyür, Ğ'nin şapkası da; tek çizgili harfler (ı, l, 1) 0,06 mm kalınlaşır (dilimleyicide kenarı
    zayıf basılıyordu). max_w: sığmazsa küçülür (min_cap'e kadar)."""
    f = S.font(k)
    if max_w:
        cap = max(f.fit_cap(s, cap, max_w, tr), min(min_cap, cap))
    for _ in range(3):
        cs, w = _dizi(f, s, cap, tr, ara, kabartma)
        if not max_w or w <= max_w + 0.05 or cap <= min_cap:
            break
        cap = max(cap * max_w / w, min_cap)
    dx = {"l": 0.0, "c": -w / 2, "r": -w}[align]
    return cs.translate((x + dx, y - cap / 2))


def oyma(k, s, cap, x, y, align="l", tr=0.0, max_w=None, min_cap=0.0):
    """Renkli bant ya da bloğun içinden oyulan yazı (gövde rengi görünür): harf arası ve noktayla harf arası (bantta
    kalan köprü) ≥ 0,8 mm; harfler kalınlaşmaz (köprü incelmesin)."""
    return yazi(k, s, cap, x, y, align, tr, max_w, kabartma=False, min_cap=min_cap)


def ad_metni(s, k):
    """Ad yazı tipine göre: zarif yazı tiplerinde yazıldığı gibi (hepsi büyükse baş harfler büyük), ötekilerde büyük."""
    s = " ".join(s.split())
    if k in KUCUK_HARFLI:
        return tr_title(s) if s == tr_upper(s) else s
    return tr_upper(s)


def madde_satiri(items, cap, x, y, align="l", tr=0.8, max_w=None, k=SATIR):
    """Maddeler arasında yuvarlak nokta (yazı tipinin orta noktası kabartmada çok küçük kalıyor). Her madde ayrı
    dizilir (harf arası ≥ 0,8 mm), genişliği ölçülerek yan yana konur. Döner şekil."""
    gap = cap * 1.25
    shapes = [yazi(k, s, cap, 0.0, y, "l", tr) for s in items]
    ws = [cs.bounds()[2] - cs.bounds()[0] for cs in shapes]
    total = sum(ws) + gap * (len(items) - 1)
    x0 = {"l": x, "c": x - total / 2, "r": x - total}[align]
    parts = []
    for i, (cs, w) in enumerate(zip(shapes, ws)):
        parts.append(cs.translate((x0 - cs.bounds()[0], 0.0)))
        x0 += w
        if i < len(items) - 1:
            parts.append(A.circle(max(0.75, cap * 0.19), x0 + gap / 2, y, 48))
            x0 += gap
    return A.union(*parts)


def maddeleri_diz(items, cap, max_w, n_max, tr=0.8, k=SATIR):
    """Maddeleri satırlara dağıtır (her satır max_w'ya sığdığı kadar); en çok n_max satır. Tek başına sığmayan madde
    atlanır. Döner [[madde]]."""
    f = S.font(k)
    gap = cap * 1.25
    lines, cur, w = [], [], 0.0
    for it in items:
        iw = f.width(it, cap, tr) * 1.03                  # harf aralığı düzeltmesine pay
        if iw > max_w:
            continue
        if cur and w + gap + iw > max_w:
            lines.append(cur)
            cur, w = [], 0.0
        w += (gap if cur else 0.0) + iw
        cur.append(it)
    if cur:
        lines.append(cur)
    return lines[:n_max]


def telefon_yazisi(s):
    try:
        return Q.phone_display(Q.phone_e164(s))
    except Q.QRError:
        return " ".join(s.split())


def bar(x0, x1, y, h):
    return S.bar(x0, x1, y, h)


# ---------------------------------------------------------------- simgeler: [(şekil, rol)], rol yazi / vurgu / vurgu2

def _jant(R=12.0):
    holes = A.union(A.circle(R * 0.11), *[A.circle(R * 0.093, R * 0.32 * math.cos(a), R * 0.32 * math.sin(a))
                                          for a in np.radians(np.arange(5) * 72 + 90)])
    return [(A.circle(R) - A.circle(R * 0.66), "yazi"), (A.circle(R * 0.56) - holes, "vurgu")]


def _araba(length=40.0):
    shape, _, wc, wr, _ = A.car_silhouette(length)
    wheels = A.union(*[A.circle(wr * 0.82, x, y) for x, y in wc])
    gaps = A.union(*[A.circle(wr * 0.82 + 1.0, x, y) for x, y in wc])
    return [(shape - gaps, "yazi"), (wheels, "vurgu")]


def _anahtar(L=30.0, angle=-35.0):
    """İngiliz anahtarı: bir ucu açık ağız, öbür ucu halka (calik_isimlik.wrench)."""
    w = 5.2
    handle = A.rrect(L - 10.0, w, w / 2 - 0.01, 0, 0)
    head = A.circle(6.6, L / 2 - 3.5, 0) - A.rect(L / 2 - 3.5, -2.4, L / 2 + 8.0, 2.4)
    ring = A.circle(5.2, -L / 2 + 3.5, 0) - A.circle(2.5, -L / 2 + 3.5, 0)
    return [((handle + head + ring).rotate(angle), "vurgu")]


def _fincan():
    """Fincan: gövde, kulp, tabak ve iki buhar çizgisi (çizgiler ≥ 1,4 mm)."""
    body = A.rrect(15.0, 13.0, 3.2, 0.0, 0.0) + A.rect(-7.5, 2.0, 7.5, 6.5)
    handle = A.circle(4.4, 8.2, 1.2) - A.circle(2.4, 8.2, 1.2)
    saucer = A.rrect(23.0, 2.4, 1.2, 1.0, -8.6)
    steam = A.union(*[A.stroke(A.smooth([(x, 9.0), (x + 1.4, 11.2), (x, 13.4), (x + 1.4, 15.6)], n=40), 1.5)
                      for x in (-3.2, 1.6)])
    return [(body + handle + saucer + steam, "vurgu")]


def _direk():
    white, red, blue = S.ic_pole(0.0, 0.0, 50.0)
    return [(white, "yazi"), (red, "vurgu"), (blue, "vurgu2")]


def _olcekli(fn, dogal_boy):
    """Yalnız ölçeklenerek küçülen simge: küçüldükçe çizgileri kalınlaşır (1,2 mm'nin altına inmesin)."""
    def kur(boy):
        k = boy / dogal_boy
        parts = [(cs.scale((k, k)), r) for cs, r in fn()]
        return [(cs.offset((1 - k) * 0.5, J), r) for cs, r in parts] if k < 1 else parts
    return kur


# simge: boy (mm) → [(şekil, rol)], ortası yaklaşık (0, 0). Çizgi kalınlıkları sabit çizilenler boyla yeniden kurulur.
SIMGE = {
    "jant": lambda boy: _jant(boy / 2),
    "araba": lambda boy: _araba(boy / 0.325),
    "anahtar": _olcekli(_anahtar, 25.0),
    "fincan": _olcekli(_fincan, 26.1),
    "direk": lambda boy: [(cs.scale((boy / 62.0, boy / 62.0)), r) for cs, r in _direk()],
    "telefon": lambda boy: [(S.ic_phone(0, 0, max(boy, 12.0)), "vurgu")],
    "makas": _olcekli(lambda: [(S.ic_scissors(0, 0, 21.0), "vurgu")], 22.8),
    "hilal": lambda boy: [(S.ic_moon(0, 0, boy / 1.97), "vurgu")],
    "ev": lambda boy: [(S.ic_house(0, 0, boy / 1.17), "vurgu")],
    "pirlanta": lambda boy: [(S.ic_diamond(0, 0, boy / 0.757), "vurgu")],
    "gozluk": lambda boy: [(S.ic_glasses(0, 0, max(boy / 0.385, 22.0)), "vurgu")],
    "pati": lambda boy: [(S.ic_paw(0, 0, boy / 0.888), "vurgu")],
    "dambil": lambda boy: [(S.ic_dumbbell(0, 0, max(boy / 0.419, 20.0)), "vurgu")],
    "dis": lambda boy: [(S.ic_tooth(0, 0, boy / 0.99), "vurgu")],
    "yaprak": lambda boy: [(S.ic_leaf(0, 0, boy / 0.973), "vurgu")],
    "yildiz": lambda boy: [(S.ic_star5(0, 0, boy / 1.81), "vurgu")],
}
SIMGE_AD = {"jant": "jant", "araba": "araba", "anahtar": "İngiliz anahtarı", "fincan": "fincan", "direk": "berber direği",
            "telefon": "telefon", "makas": "makas", "hilal": "hilal ve yıldız", "ev": "ev", "pirlanta": "pırlanta",
            "gozluk": "gözlük", "pati": "pati", "dambil": "dambıl", "dis": "diş", "yaprak": "yaprak",
            "yildiz": "yıldız", "monogram": "baş harfler", "logo": "logo"}


def simge_kur(key, w, h):
    """Simge (w × h) kutuya sığacak boyda, ortası (0, 0): [(şekil, rol)]."""
    boy = h
    for _ in range(3):
        parts = SIMGE[key](boy)
        b = A.union(*[cs for cs, _ in parts]).bounds()
        f = min(w / (b[2] - b[0]), h / (b[3] - b[1]))
        if 0.97 <= f <= 1.0:
            break
        boy *= min(f, 1.0) if f < 1 else f
    mx, my = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    return [(cs.translate((-mx, -my)), r) for cs, r in parts]


def olcekle(parcalar, cx, cy, w, h):
    """[(şekil, rol)]'ü (w × h) kutuya sığdırır, ortası (cx, cy) (logo)."""
    u = A.union(*[cs for cs, _ in parcalar])
    b = u.bounds()
    k = min(w / (b[2] - b[0]), h / (b[3] - b[1]))
    mx, my = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    return [(cs.translate((-mx, -my)).scale((k, k)).translate((cx, cy)), rol) for cs, rol in parcalar]


def monogram_harfleri(marka):
    w = [x for x in tr_upper(marka).split() if x[:1].isalnum()]
    return "".join(x[0] for x in w[:2]) or "B"


def monogram(harfler, cx, cy, s, k="mont"):
    """Vurgu renginde yuvarlak kare, içinden oyma baş harfler. Döner ([(şekil, rol)], oyma yazı)."""
    txt = oyma(k, harfler, s * (0.5 if len(harfler) == 1 else 0.42), cx, cy, "c", 0.4, s * 0.8)
    b = txt.bounds()
    txt = txt.translate((cx - (b[0] + b[2]) / 2, cy - (b[1] + b[3]) / 2))
    return [(A.rrect(s, s, s * 0.22, cx, cy) - txt.offset(0.15, J), "vurgu")], txt


def temizle(cs, cizgi=1.2, delik=0.8):
    """İzlenmiş logoda baskıya gelmeyen incelikler: `cizgi`den ince yerler ve `delik`ten dar boşluklar kapanır."""
    cs = cs.offset(-cizgi / 2, J).offset(cizgi / 2, J)
    return cs.offset(delik / 2, J).offset(-delik / 2, J)


# ---------------------------------------------------------------- QR

def qr_girdi(url, koyu):
    """Çalışan QR. Siyah gövdede beyaz karo (M); beyaz gövdede siyah kareler baskıda yayılır: Q (B07'de M düzeyi baskı
    hatası benzetiminde okunmadı). Aynı sürümde yer kalırsa segno düzeyi yükseltir. Q ile 5. sürüme çıkan uzun
    adreste M (4. sürüm, 33 × 33: 34 mm'lik karoda kare ≥ 0,9 mm)."""
    q = segno.make(url, error="m" if koyu else "q", micro=False, boost_error=True)
    if q.version > 4:
        q = segno.make(url, error="m", micro=False, boost_error=True)
    return Q.Entry("sayfa", "TARA", url, "TARA", qr=q)


def qr_modul(entry, s):
    return Q.module_for(entry, s)


# ---------------------------------------------------------------- kontroller

def ince_alan(d, sinir=1.2):
    """Simge ve süslerde (yazı olmayan kabartma) `sinir` mm'den ince alan (%)."""
    yazilar = {id(v) for v in d.lines.values()}
    shapes = [cs for cs, _ in d.raised if id(cs) not in yazilar]
    if not shapes:
        return 0.0
    cs = A.union(*shapes)
    thin = cs - cs.offset(-sinir / 2, J).offset(sinir / 2, J)
    return round(100 * sum(p.area() for p in thin.decompose() if p.area() > 0.02) / max(cs.area(), 1e-6), 1)


def sikisik(d, guvenli, bosluk=1.5, yazi_arasi=0.9):
    """Kenara taşan öğeler ve birbirine `bosluk` mm'den yakın öğeler; iki yazı satırı arasında `yazi_arasi` (Ç'nin
    çengeli ile alttaki İ'nin noktası arası). Simge parçaları kendi aralarında serbest; QR ile çerçevesi de."""
    adlar = {id(v): k for k, v in d.lines.items()}
    items = [(adlar.get(id(cs)), cs) for cs, _ in d.raised] + [("QR", cs) for cs, _ in d.inlay]
    found = [f"{n or 'simge'} kenarda" for n, cs in items if (cs - guvenli).area() > 0.05]
    for k, (n, cs) in enumerate(items):
        for n2, cs2 in items[k + 1:]:
            if not (n or n2) or {n, n2} == {"QR", "çerçeve"} or n == n2:
                continue
            g = yazi_arasi if n and n2 and "QR" not in (n, n2) and "çerçeve" not in (n, n2) else bosluk
            if (cs.offset(g, J) ^ cs2).area() > 0.01:
                found.append(f"{n or 'simge'} ~ {n2 or 'simge'}")
    return found


def olc(d, guvenli, atla=("QR", "çerçeve")):
    """Baskıya uygunluk: (sorunlar, {satır: (harf içi, ara)}). Kabartma ve oyma yazıların hepsi ölçülür."""
    olcu, sorun = {}, []
    for k, cs in d.lines.items():
        if k in atla:
            continue
        inner, gap, _ = B.line_metrics(cs)
        olcu[k] = (inner, gap)
        if inner < MIN_IC or gap < MIN_ARA:
            sorun.append(f"{k}: harf içi {inner:.2f}, ara {gap:.2f} mm")
    ince = ince_alan(d)
    if ince > 12.0:
        sorun.append(f"simgede 1,2 mm'den ince alan %{ince}")
    sorun += sikisik(d, guvenli)
    return sorun, olcu
