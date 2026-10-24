"""RESTORAN MASALIKLARI – 45 çift yüzlü (arkalı önlü) QR'lı / NFC'li masalık önerisi; restoran isimleri uydurma.

1–30 tasarım serisi; 31–45 standart seri (yuvarlak, dikey, yatay; sade ve şık).

Masanın ortasında durur, iki yüzden de okunur. Üç tür:
  * İKİ QR   : ön yüzde MENÜ, arka yüzde GOOGLE YORUM QR'ı
  * TEK QR   : iki yüzde aynı QR → restoranın tek sayfası (menü, yorum, Wi-Fi, Instagram, sipariş)
  * NFC + QR : panelin içine gömülü NFC etiketi (telefonu dokundur) + aynı sayfaya QR; NFC iki yüzden de okunur
  (6. tasarımda arka yüz Wi-Fi QR'ı.) Çoğunda masa numarası var; her masalık kendi numarasıyla basılır.
QR'lar doğrudan Google'a / menü dosyasına değil, ortak hesaptaki sayfaya gider (`<ad>.qrsistem.workers.dev/menu`,
`/yorum`): menü ya da Google bağlantısı değişse de masalık değişmez. Örneklerdeki adresler henüz yayında değil.

Yapı (baskıya göre):
  * iki plaka sırt sırta (her biri 4 mm, 20 katman): her yüz kendi plakası, yüzü yukarı basılır; ikisi birlikte
    ayaktaki yuvaya oturur (yuva 8,3 mm). Böylece iki yüz de kabartmalı olur.
  * kabartma: geniş renk alanları (etiket, şerit, dilim) 1,2 mm kabarık zemin; yazı, çerçeve, simge, yıldız 1,6 mm
    kabartma (zeminin de üstünde), üst kenarı 0,4 mm pahlı; QR kabarık karo (1,2 mm), koyu kareler karonun üstüne
    0,6 mm gömülü: yüzeyi düz, okunur
  * panelin alt dili (8 mm) ayaktaki yuvaya oturur; ayak ayrı basılır. Bazıları çapraz ayaklı, çadır (A) ya da
    peçetelik / tuzluk-biberlik düzenleyici
  * NFC: Ø25 mm NTAG215 etiket, ön plakanın arkasında Ø26 × 0,6 mm cepte; iki plaka arasında kalır (baskıyı duraklatmak
    gerekmez). Telefon iki yüzden de okur.
  * QR karesi ≥ 0,9 mm; koyu kareler koyu renk, zemin açık renk. Her yüzün QR'ı ayrı ayrı okutulup baskı hatası
    benzetiminde de denenir. Yazıların her harfi yazı tipinde olmalı (yoksa hata). İnce yerler ölçülür.
Yazı tipleri: başlıklarda Fraunces, Playfair Display, Cinzel, Bodoni Moda, Anton, Big Shoulders, Archivo, Bricolage,
Syne, Unbounded, Barlow, Righteous, Norican, Caveat; küçük yazılarda Jost Bold. Renkler mat filament tonları + ipek
altın / bakır + ahşap PLA.
Görseller: restoran_masalik_foto.py (Blender Cycles, ahşap masada stüdyo fotoğrafı) varsa onlar kullanılır; menü
siteleri menu_siteleri.py.

Çıktı : restoran_masalik/<n>_<ad>.png (iki yüz, iki fotoğraf), musteri_NN.png / .jpg, musteri_katalog.pdf

Kullanım:
  python3 scripts/restoran_masalik.py [anahtar ...]
"""
import math
import os
import sys

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import qr_sistemi as Q  # noqa: E402
from cift_tarafli_isimlik import rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "restoran_masalik")
J = m3.JoinType.Round
T = 4.0                    # bir plaka (20 katman); masalık iki plaka sırt sırta (8 mm)
INL = 0.8                  # ayak üstündeki gömülü renk (4 katman)
PLAQUE = 1.2               # geniş renk alanları (etiket, şerit, dilim): kabarık zemin (6 katman)
RELIEF = 1.6               # yazı, çizgi, simge: kabartma (8 katman), kabarık zeminin de üstünde
QR_H, QR_INL = 1.2, 0.6    # QR karosu kabarık; koyu kareler karonun üstüne gömülü (düz, okunur)
BEVEL = 0.4                # kabartmaların üst kenarı iki basamakla yuvarlatılır (ışık yakalar)
EDGE = 0.8                 # renkli öğelerin plaka kenarına en yakın mesafesi
D = 8.0                    # panelin yuvaya giren dili
CLR = 0.3                  # yuva boşluğu
FT = 4.0                   # çapraz ayak kalınlığı
NFC_R, NFC_H = 13.0, 0.6   # NFC cebi: ön plakanın arka yüzünde, iki plaka arasında kalır
DOMAIN = "qrsistem.workers.dev"
MIN_FEAT = 0.6             # kontrol: en ince dolgu (mm)

# mat filament tonları (önizleme) ve katalog adları
COL = {"siyah": (40, 40, 42), "fildisi": (238, 232, 216), "beyaz": (246, 245, 241), "bordo": (112, 30, 40),
       "kirmizi": (190, 40, 42), "altin": (204, 168, 96), "bakir": (184, 114, 66), "sari": (238, 200, 64),
       "hardal": (222, 168, 56), "turuncu": (226, 112, 48), "lacivert": (30, 40, 74), "turkuaz": (48, 148, 156),
       "koyu_yesil": (42, 72, 54), "yesil": (88, 136, 82), "pembe": (232, 172, 180), "lila": (174, 154, 200),
       "mor": (72, 44, 100), "kahve": (80, 54, 42), "latte": (198, 164, 128), "karamel": (190, 128, 72),
       "terrakota": (176, 92, 66), "kum": (214, 192, 152), "ahsap": (170, 124, 84), "gri": (142, 144, 146),
       "mercan": (228, 120, 102), "adacayi": (150, 166, 140), "pudra": (228, 190, 182), "kobalt": (34, 68, 146),
       "zeytin": (98, 102, 64), "mermer": (236, 234, 228)}
COL_NAME = {"siyah": "siyah", "fildisi": "fildişi", "beyaz": "beyaz", "bordo": "bordo", "kirmizi": "kırmızı",
            "altin": "ipek altın", "bakir": "ipek bakır", "sari": "limon sarısı", "hardal": "hardal",
            "turuncu": "turuncu", "lacivert": "lacivert", "turkuaz": "turkuaz", "koyu_yesil": "koyu yeşil",
            "yesil": "yeşil", "pembe": "pembe", "lila": "lila", "mor": "mor", "kahve": "kahverengi",
            "latte": "latte", "karamel": "karamel", "terrakota": "terrakota", "kum": "kum beji",
            "ahsap": "ahşap (PLA Wood)", "gri": "beton gri", "mercan": "mercan", "adacayi": "adaçayı yeşili",
            "pudra": "pudra pembe", "kobalt": "kobalt mavi", "zeytin": "zeytin yeşili", "mermer": "mermer (PLA Marble)"}
METAL = {"altin", "bakir"}

FONT_FILES = {"cinzel": "Cinzel-Black.ttf", "fraunces": "Fraunces-SemiBold.ttf", "fraunces_k": "Fraunces-Black.ttf",
              "fraunces_i": "Fraunces-SemiBoldItalic.ttf", "fraunces_ki": "Fraunces-BlackItalic.ttf",
              "playfair_k": "PlayfairDisplay-Black.ttf",
              "playfair_ki": "PlayfairDisplay-BlackItalic.ttf", "bodoni": "BodoniModa-ExtraBold.ttf", "jost": "Jost-Bold.ttf", "anton": "Anton-Regular.ttf",
              "bigsh": "BigShouldersDisplay-Black.ttf", "archivo_x": "Archivo-ExpandedBold.ttf",
              "bricolage": "BricolageGrotesque-CondensedExtraBold.ttf",
              "syne": "Syne-ExtraBold.ttf", "unbounded": "Unbounded-ExtraBold.ttf", "barlow": "BarlowCondensed-Black.ttf", "norican": "Norican-Regular.ttf", "caveat": "Caveat-Bold.ttf",
              "righteous": "Righteous-Regular.ttf"}
BOLD = {"fraunces": 0.1, "fraunces_i": 0.1, "playfair_k": 0.08, "playfair_ki": 0.06, "bodoni": 0.14, "cinzel": 0.05,
        "norican": 0.14, "caveat": 0.12}          # ince serif çizgileri baskıda kaybolmasın diye dışa kalınlaştırma (mm)
_FONTS = {}


def font(k):
    if k not in _FONTS:
        _FONTS[k] = A.Font(FONT_FILES[k])
    return _FONTS[k]


# ---------------------------------------------------------------- 2B yardımcılar

def C(r, x=0.0, y=0.0, n=128):
    return A.circle(r, x, y, n)


def R(x0, y0, x1, y1):
    return A.rect(x0, y0, x1, y1)


def RR(w, h, r, cx=0.0, cy=0.0):
    return A.rrect(w, h, max(min(r, w / 2 - 0.01, h / 2 - 0.01), 0.01), cx, cy)


def P(pts):
    return A.polygon(pts)


def SM(pts, n=240):
    """Kontrol noktalarından geçen kapalı yumuşak şekil."""
    return A.polygon(A.smooth(pts, closed=True, n=n))


def ST(pts, w):
    return A.stroke(pts, w)


U = A.union


def soft(cs, r):
    """Köşeleri r yarıçapla yuvarlar (içe ve dışa)."""
    return cs.offset(-r, J).offset(2 * r, J).offset(-r, J)


def ellipse(a, b, x=0.0, y=0.0, n=160):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return P(np.c_[x + a * np.cos(t), y + b * np.sin(t)])


def ring(r, w, x=0.0, y=0.0):
    return C(r, x, y) - C(r - w, x, y)


def arc_pts(cx, cy, r, a0, a1, n=60):
    t = np.radians(np.linspace(a0, a1, n))
    return np.c_[cx + r * np.cos(t), cy + r * np.sin(t)]


def sector(r0, r1, a0, a1, x=0.0, y=0.0):
    return P(np.vstack([arc_pts(x, y, r1, a0, a1), arc_pts(x, y, r0, a1, a0)]))


def star(cx, cy, r, inner=0.46, rot=90.0):
    pts = []
    for k in range(10):
        a = math.radians(rot + 36 * k)
        rr = r if k % 2 == 0 else r * inner
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return P(pts).offset(-0.2, J).offset(0.2, J)


def stars(cx, cy, r=2.4, n=5, gap=1.2):
    step = 2 * r + gap
    return U(*[star(cx + (k - (n - 1) / 2) * step, cy, r) for k in range(n)])


def diamond(cx, cy, rx, ry=None):
    ry = ry or rx
    return P([(cx, cy + ry), (cx + rx, cy), (cx, cy - ry), (cx - rx, cy)])


def heart(cx, cy, s):
    t = np.linspace(0, 2 * np.pi, 120, endpoint=False)
    x = 16 * np.sin(t) ** 3
    y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
    return P(np.c_[cx + x * s / 32, cy + (y + 2) * s / 32])


def leaf(cx, cy, length, width, angle=90.0):
    """Sivri uçlu yaprak, (cx, cy) sapın dibi, `angle` yönünde."""
    t = np.linspace(0, 1, 40)
    up = np.c_[t * length, np.sin(np.pi * t) * width / 2 * (1 - 0.3 * t)]
    pts = np.vstack([up, up[::-1] * [1, -1]])
    a = math.radians(angle)
    rot = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    return P(pts @ rot.T + (cx, cy))


def rule(x0, x1, y, w=1.0):
    x0, x1 = min(x0, x1), max(x0, x1)
    return RR(x1 - x0, w, w / 2, (x0 + x1) / 2, y)


def arrow(x, y, length, w=1.2, head=3.0, direction=1):
    """Yatay ok (direction 1: sağa)."""
    x1 = x + direction * length
    hx = x1 - direction * head
    return U(ST([(x, y), (x1 - direction * 0.6, y)], w), ST([(hx, y + head * 0.8), (x1, y), (hx, y - head * 0.8)], w))


def tx(k, s, cap, x, y, align="c", tr=0.0, max_w=None, bold=None, angle=0.0):
    """Yazı; (x, y) büyük harf ortası. max_w: sığmazsa küçülür. Her harf yazı tipinde olmalı."""
    f = font(k)
    cmap = f.tt.getBestCmap()
    missing = sorted({ch for ch in s if ch != " " and ord(ch) not in cmap})
    if missing:
        raise ValueError(f"{FONT_FILES[k]} yazı tipinde yok: {''.join(missing)!r} ({s!r})")
    if max_w:
        cap = f.fit_cap(s, cap, max_w, tr)
    cs = f.text(s, cap, x, y, align=align, tracking=tr, angle=angle)
    b = BOLD.get(k, 0.0) if bold is None else bold
    return cs.offset(b, J) if b else cs


def arc_tx(k, s, cap, cx, cy, r, deg=90.0, top=True, tr=0.0, bold=None):
    f = font(k)
    cmap = f.tt.getBestCmap()
    missing = sorted({ch for ch in s if ch != " " and ord(ch) not in cmap})
    if missing:
        raise ValueError(f"{FONT_FILES[k]} yazı tipinde yok: {''.join(missing)!r} ({s!r})")
    cs = f.arc(s, cap, cx, cy, r, deg, top, tr)
    b = BOLD.get(k, 0.0) if bold is None else bold
    return cs.offset(b, J) if b else cs


def label(s, x, y, cap=3.8, tr=None, k="jost", align="c", max_w=None):
    """Harf aralıklı küçük büyük harf satırı (Jost Bold)."""
    return tx(k, s, cap, x, y, align=align, tr=cap * 0.32 if tr is None else tr, max_w=max_w)


def phone_waves(cx, cy, s, w=None):
    """Temassız simgesi: telefon ve yanında üç dalga (NFC: telefonu dokundur)."""
    w = w or max(1.0, s * 0.075)
    ph = RR(s * 0.42, s * 0.74, s * 0.08, cx - s * 0.2, cy)
    ph = ph - RR(s * 0.42 - 2 * w, s * 0.74 - 2 * w, max(s * 0.08 - w, 0.2), cx - s * 0.2, cy)
    ph = ph + RR(s * 0.12, w * 0.9, w * 0.4, cx - s * 0.2, cy - s * 0.27)
    waves = [ST(arc_pts(cx - s * 0.02, cy, s * (0.16 + 0.13 * k), -42, 42, 24), w) for k in range(3)]
    return U(ph, *waves)


def wifi_icon(cx, cy, s, w=None):
    w = w or max(1.0, s * 0.11)
    arcs = [ST(arc_pts(cx, cy - s * 0.38, s * (0.28 + 0.24 * k), 48, 132, 24), w) for k in range(3)]
    return U(C(w * 0.9, cx, cy - s * 0.38), *arcs)


def fork(x, y0, y1, w=8.0, tines=4):
    """Çatal (dikey): sap y0'dan, dişler y1'e."""
    L = y1 - y0
    handle = RR(w * 0.5, L * 0.62, w * 0.25, x, y0 + L * 0.31)
    neck = P([(x - w * 0.25, y0 + L * 0.56), (x + w * 0.25, y0 + L * 0.56), (x + w / 2, y0 + L * 0.68),
              (x - w / 2, y0 + L * 0.68)])
    head = RR(w, L * 0.08, w * 0.2, x, y0 + L * 0.7)
    tw = (w - (tines - 1) * 1.1) / tines
    ts = [RR(tw, L * 0.3, tw / 2 - 0.01, x - w / 2 + tw / 2 + k * (tw + 1.1), y0 + L * 0.84) for k in range(tines)]
    return U(handle, neck, head, *ts)


def knife(x, y0, y1, w=7.0):
    L = y1 - y0
    handle = RR(w * 0.6, L * 0.48, w * 0.3, x, y0 + L * 0.24)
    blade = SM([(x - w * 0.3, y0 + L * 0.46), (x - w * 0.36, y0 + L * 0.75), (x - w * 0.12, y0 + L * 0.995),
                (x + w * 0.42, y0 + L * 0.86), (x + w * 0.4, y0 + L * 0.6), (x + w * 0.3, y0 + L * 0.46)])
    return U(handle, blade)


# ---------------------------------------------------------------- yüz, panel, tasarım

def url(slug, path=""):
    return f"https://{slug}.{DOMAIN}" + (f"/{path}" if path else "")


def make_qr(content):
    import segno
    q = segno.make(content, error="m", micro=False, boost_error=True)
    return Q.Entry("qr", "", content, "", qr=q)


class Side:
    """Bir yüzün içeriği (o yüze bakan kişinin gördüğü koordinatlarla). Sonra eklenen öncekinin üstüne yazar;
    renk None → plakanın rengi. Geniş alanlar kabarık zemin, yazı / çizgi / simge kabartma, QR kabarık karo."""

    def __init__(self):
        self.items, self.qrs = [], []

    def add(self, cs, col, raised=False):
        self.items.append((cs, col, "relief" if raised else "auto"))
        return cs

    def qr(self, content, cx, cy, s, light="fildisi", dark=None, r=1.6, pad=0.0):
        e = make_qr(content)
        module = Q.module_for(e, s)
        _, dark_cs, _ = Q.shapes(e, module, cx, cy)
        self.items.append((RR(s + 2 * pad, s + 2 * pad, r, cx, cy), light, "qr_tile"))
        self.items.append((dark_cs, dark, "qr_dark"))
        self.qrs.append((e, module, dark))
        return e


def kind_of(cs, kind):
    if kind != "auto":
        return kind
    return "plaque" if cs.area() > 380 and not cs.offset(-3.2, J).is_empty() else "relief"


def regions(items, body, clip):
    """Üstten görünen renkler {renk: bölge}: üstteki öğe alttakini örter; plaka rengi dışarıda."""
    taken, out = A.empty(), {}
    for cs, col, _ in reversed(items):
        part = (cs ^ clip) - taken
        taken = taken + part
        col = col or body
        out[col] = out.get(col, A.empty()) + part
    out.pop(body, None)
    return {c: cs for c, cs in out.items() if cs.area() > 0.01}


def layers(items, body, clip):
    """Katmanlar: {tür: {renk: bölge}}. Kabarık zemini yalnız sonraki zeminler örter (yazı onun üstüne oturur);
    kabartma ve QR'ı sonraki her öğe örter."""
    out = {k: {} for k in ("plaque", "relief", "qr_tile", "qr_dark")}
    taken_all, taken_pl = A.empty(), A.empty()
    for cs, col, kind in reversed(items):
        k = kind_of(cs, kind)
        cs = cs ^ clip
        part = cs - (taken_pl if k == "plaque" else taken_all)
        if k == "plaque":
            taken_pl = taken_pl + part
        taken_all = taken_all + part
        c = col or body
        out[k][c] = out[k].get(c, A.empty()) + part
    return {k: {c: cs for c, cs in v.items() if cs.area() > 0.01} for k, v in out.items()}


def bevelled(cs, h, z0, b=BEVEL):
    """Üst kenarı iki basamakla pahlanmış kabartma (ince yerlerde basamak kalmaz, tam yükseklik korunur)."""
    lo = cs.extrude(h - b).translate((0, 0, z0))
    s1 = cs.offset(-b * 0.35, J)
    s2 = cs.offset(-b * 0.75, J)
    thin = cs - s2.offset(b * 0.75 + 0.05, J)                 # basamak sığmayan ince kısımlar tam boy
    tops = [s1.extrude(b / 2).translate((0, 0, z0 + h - b)), s2.extrude(b / 2).translate((0, 0, z0 + h - b / 2)),
            thin.extrude(b).translate((0, 0, z0 + h - b))]
    return m3.Manifold.batch_boolean([lo] + [t for t in tops if not t.is_empty()], m3.OpType.Add)


def chamfered(out, t, depth=0.4):
    """Plakanın iki yüz kenarını iki basamakla yumuşatır."""
    cuts = []
    for k in range(2):
        ring_ = out - out.offset(-depth * (2 - k) / 2, J)
        cuts.append(ring_.extrude(0.21).translate((0, 0, k * 0.2 - 0.01)))
        cuts.append(ring_.extrude(0.21).translate((0, 0, t - (k + 1) * 0.2)))
    return out.extrude(t) - m3.Manifold.batch_boolean(cuts, m3.OpType.Add)


class Panel:
    """Bir plaka: yüzü yukarı basılır, içeriği `front`. İki yüzlü masalıkta `back` ikinci plakaya geçer."""

    def __init__(self, outline, body, nfc=None, vis_y=D):
        self.outline, self.body, self.nfc = outline, body, nfc        # nfc: ön yüz koordinatında etiket merkezi
        self.vis_y = vis_y                                            # bunun altı ayağın içinde
        self.front, self.back = Side(), Side()

    @property
    def outline_back(self):
        return self.outline.mirror((1, 0))

    def faces(self):
        if not hasattr(self, "_faces"):
            self._faces = (regions(self.front.items, self.body, self.outline.offset(-EDGE, J)), {})
        return self._faces

    def solids(self):
        """Baskı yönünde: plakanın arkası z = 0 (tablada), yüzü z = T, kabartmalar üstünde. [(ad, Manifold, renk)]"""
        L = layers(self.front.items, self.body, self.outline.offset(-EDGE, J))
        body = chamfered(self.outline, T)
        if self.nfc:
            body = body - C(NFC_R, *self.nfc).extrude(NFC_H + 0.01).translate((0, 0, -0.01))
        parts = [(f"Plaka ({COL_NAME[self.body]})", body, self.body)]
        pl = A.union(*L["plaque"].values())
        for col, cs in L["plaque"].items():
            parts.append((f"Kabarık zemin ({COL_NAME[col]})", bevelled(cs, PLAQUE, T), col))

        def split(cs):
            return [(r, z) for r, z in ((cs - pl, T), (cs ^ pl, T + PLAQUE)) if r.area() > 0.01]

        for col, cs in L["relief"].items():
            for r, z in split(cs):
                parts.append((f"Kabartma ({COL_NAME[col]})", bevelled(r, RELIEF, z), col))
        if L["qr_tile"] or L["qr_dark"]:
            light = next(iter(L["qr_tile"]), self.body)
            for col, cs in L["qr_tile"].items():
                for r, z in split(cs):
                    parts.append((f"QR karosu ({COL_NAME[col]})", r.extrude(QR_H).translate((0, 0, z)), col))
            for col, cs in L["qr_dark"].items():
                for r, z in split(cs):
                    parts.append((f"QR karosu ({COL_NAME[light]})", r.extrude(QR_H - QR_INL).translate((0, 0, z)),
                                  light))
                    parts.append((f"QR kareleri ({COL_NAME[col]})",
                                  r.extrude(QR_INL).translate((0, 0, z + QR_H - QR_INL)), col))
        return parts

    def colours(self):
        return {c for _, _, c in self.solids()}


def upright(z0, x0=0.0, y0=0.0, turn=False, tilt=0.0):
    """Baskı yönündeki paneli ayağa kaldırır: ön yüz −y'ye bakar (turn: +y'ye), panel y'si dünyada z + z0.
    tilt: alt kenar etrafında yatırma (derece; + üst kenar +y'ye)."""
    a = math.radians(tilt)
    c, s = math.cos(a), math.sin(a)
    sg = -1.0 if turn else 1.0
    M = np.array([[sg, 0, 0, 0], [0, 0, -sg, sg * T / 2], [0, 1, 0, 0], [0, 0, 0, 1]], float)
    Rt = np.array([[1, 0, 0, 0], [0, c, s, 0], [0, -s, c, 0], [0, 0, 0, 1]], float)
    Tr = np.array([[1, 0, 0, x0], [0, 1, 0, y0], [0, 0, 1, z0], [0, 0, 0, 1]], float)
    return (Tr @ Rt @ M)[:3].tolist()


class Design:
    def __init__(self, key, name, sub, kind, desc, masa=None):
        self.key, self.name, self.sub, self.kind, self.desc, self.masa = key, name, sub, kind, desc, masa
        self.panels = []          # [(Panel, dönüşüm)]
        self.stand = []           # [(ad, Manifold, renk)] dünya koordinatında
        self.props = []           # görselde gösterilen, baskıya dahil olmayan (peçete, tuzluk)
        self.stand_desc = ""

    def put(self, panel, M):
        self.panels.append((panel, M))
        return panel

    def scene(self, props=True):
        out = [(n, m.transform(M), c) for p, M in self.panels for n, m, c in p.solids()]
        return out + self.stand + (self.props if props else [])

    def colours(self):
        cs = set()
        for p, _ in self.panels:
            cs |= p.colours()
        return cs | {c for _, _, c in self.stand}


def double(d, p, z0, x0=0.0, y=0.0):
    """Ön plaka (p.front) ve arka plaka (p.back) sırt sırta; ortaları y'de. Arka plaka arkadan bakana göre çizilir."""
    back = Panel(p.outline_back, p.body, vis_y=p.vis_y)
    back.front = p.back
    d.put(p, upright(z0, x0, y - T / 2))
    d.put(back, upright(z0, x0, y + T / 2, turn=True))


KIND = {"2qr": "İKİ QR · menü + yorum", "1qr": "TEK QR · sayfa", "nfc": "NFC + QR", "wifi": "QR + Wi-Fi"}


# ---------------------------------------------------------------- ayaklar (dünya koordinatı; yuva x = 0, y = 0)

def box(x0, y0, z0, x1, y1, z1):
    return R(x0, y0, x1, y1).extrude(z1 - z0).translate((0, 0, z0))


def slot(tw, hb, x=0.0, y=0.0, depth=D, thick=2 * T):
    return box(x - tw / 2 - CLR, y - (thick + CLR) / 2, hb - depth, x + tw / 2 + CLR, y + (thick + CLR) / 2, hb + 1)


def solid(cs, h, z0=0.0):
    return cs.extrude(h).translate((0, 0, z0))


def top_inlay(foot, cs, hb, col, body):
    """Ayak üst yüzüne gömülü renk (son 4 katman)."""
    ins = foot ^ solid(cs, INL, hb - INL)
    return [(f"Ayak ({COL_NAME[body]})", foot - ins, body), (f"Ayak üstü ({COL_NAME[col]})", ins, col)]


def foot_plain(cs, h, tw, col, top=None, top_cs=None, x=0.0, depth=D):
    f = solid(cs, h) - slot(tw, h, x, depth=depth)
    if top:
        return top_inlay(f, top_cs if top_cs is not None else cs.offset(-2.5, J), h, top, col), h
    return [(f"Ayak ({COL_NAME[col]})", f, col)], h


def along_x(cs_xz, depth):
    """x–z düzlemindeki profili y boyunca `depth` kalınlığında uzatır (ortalı)."""
    return cs_xz.extrude(depth).transform([[1, 0, 0, 0], [0, 0, 1, -depth / 2], [0, 1, 0, 0]])


def along_y(cs_yz, length):
    """y–z düzlemindeki profili x boyunca uzatır (ortalı)."""
    return cs_yz.extrude(length).transform([[0, 0, 1, -length / 2], [1, 0, 0, 0], [0, 1, 0, 0]])


def foot_wave(w, d, h, amp, waves, tw, col, top=None):
    xs = np.linspace(-w / 2, w / 2, 200)
    top_pts = np.c_[xs, h - amp + amp * np.cos(2 * np.pi * waves * xs / w)]
    prof = P(np.vstack([[(-w / 2, 0)], top_pts, [(w / 2, 0)]]))
    f = along_x(prof, d) ^ solid(RR(w, d, min(d / 2, 10)), h + 2, -1)
    f = f - slot(tw, h)
    parts = [(f"Ayak ({COL_NAME[col]})", f, col)]
    if top:
        band = f ^ along_x(P(np.vstack([top_pts - (0, 1.2), top_pts[::-1] + (0, 1)])), d + 2)
        parts = [(f"Ayak ({COL_NAME[col]})", f - band, col), (f"Ayak dalga ({COL_NAME[top]})", band, top)]
    return parts, h


def saucer(r, slot_w, col, rim_col=None, rim_w=6.0):
    plate = solid(C(r), 3) + solid(ring(r, rim_w), 3.2, 3)
    hb = 3.8 + D
    f = plate + solid(C(max(r * 0.38, slot_w / 2 + 5)), hb - 3, 3) - slot(slot_w, hb)
    if rim_col:
        top = f ^ solid(ring(r - 1.0, rim_w - 2.0), INL, 6.2 - INL)
        return [(f"Tabak ({COL_NAME[col]})", f - top, col), (f"Tabak kenarı ({COL_NAME[rim_col]})", top, rim_col)], hb
    return [(f"Tabak ({COL_NAME[col]})", f, col)], hb


def cross_foot(length, height, col, profile=None):
    """Panele dik takılan ayak (panelde alttan, ayakta üstten yarım yuva). Döner: (ayak, panel kesiği)."""
    prof = profile or P([(-length / 2, 0), (length / 2, 0), (length / 2 - 4, height), (-length / 2 + 4, height)])
    prof = soft(prof, 2)
    f = along_y(prof, FT) - box(-FT, -(2 * T + CLR) / 2, height / 2, FT, (2 * T + CLR) / 2, height + 1)
    cut = R(-(FT + CLR) / 2, -1, (FT + CLR) / 2, height / 2 + 0.2)
    return [(f"Ayak ({COL_NAME[col]})", f, col)], cut


def standard(d, p, foot_parts, hb, desc):
    double(d, p, hb - D)
    d.stand += foot_parts
    d.stand_desc = desc
    return d


def tab(shape, tw, y_top=None, extra=0.0):
    """Görünen kısım y ≥ D'de; altına yuvaya giren dil (genişlik tw; extra: yuvadan daha derin)."""
    return (shape ^ R(-999, D, 999, 999)) + R(-tw / 2, -extra, tw / 2, max(D + 1.0, y_top or 0.0))


def mirror_fn(sg):
    return (lambda cs: cs.mirror((1, 0))) if sg < 0 else (lambda cs: cs)


def both(p):
    """(yüz, işaret): ön yüz +1, arka yüz −1 (arkadan bakınca x tersine döner)."""
    return ((p.front, 1), (p.back, -1))


# ---------------------------------------------------------------- tasarımlar

def t01_kemer():
    d = Design("01_kemer", "Kaleiçi Sofrası", "Osmanlı mutfağı", "2qr",
               "Sivri kemer: bordo zemin, ipek altın çift çerçeve ve lale, fildişi QR. Ön menü, arka Google yorumu.",
               masa=7)
    W, yb, h = 104.0, D + 78.0, 70.0
    Ra = (h ** 2 + (W / 2) ** 2) / W
    cx = -W / 2 + Ra
    al = math.degrees(math.atan2(h, -cx))
    left = arc_pts(cx, yb, Ra, 180, al, 60)
    arch = P(np.vstack([[(-W / 2, D - 2)], left, left[::-1] * [-1, 1], [(W / 2, D - 2)]]))
    p = Panel(tab(arch, 70), "bordo")
    vis = arch ^ R(-99, D, 99, 999)
    frame = (vis.offset(-4.0, J) - vis.offset(-5.4, J)) + (vis.offset(-6.6, J) - vis.offset(-7.6, J))

    def tulip(y):
        mid = SM([(0, y + 14), (3.2, y + 6), (2.6, y + 1), (0, y), (-2.6, y + 1), (-3.2, y + 6)])
        side_ = SM([(1.2, y + 0.4), (5.6, y + 1.5), (8.8, y + 6.5), (9.4, y + 12.0), (6.4, y + 7.4), (3.0, y + 4.0)])
        stem = ST([(0, y + 0.5), (0, y - 7)], 1.4)
        lv = SM([(0, y - 6.5), (5.0, y - 3.0), (7.8, y - 0.2), (3.6, y - 3.4)])
        return U(mid, side_, side_.mirror((1, 0)), stem, lv, lv.mirror((1, 0)))

    for side, sg in both(p):
        side.add(frame, "altin")
        side.add(tulip(D + 116), "altin")
        side.add(tx("cinzel", "KALEİÇİ", 9.0, 0, D + 100, tr=1.2, max_w=76), "altin")
        side.qr(url("kaleici", "menu" if sg > 0 else "yorum"), 0, D + 60, 40)
        side.add(tx("cinzel", "MASA 07", 3.8, 0, D + 17.5, tr=1.6), "fildisi")
    f, b = p.front, p.back
    f.add(tx("cinzel", "SOFRASI", 4.4, 0, D + 88.6, tr=2.4), "fildisi")
    lab = f.add(tx("cinzel", "MENÜ", 5.2, 0, D + 30.5, tr=2.6), "altin")
    hw = lab.bounds()[2] + 4.0
    for s_ in (-1, 1):
        f.add(rule(s_ * hw, s_ * (hw + 13), D + 30.5, 1.0), "altin")
    b.add(stars(0, D + 88.6, 2.4, gap=1.4), "altin")
    b.add(tx("cinzel", "DEĞERLENDİRİN", 4.2, 0, D + 30.5, tr=1.0), "altin")
    foot, hb = foot_plain(RR(124, 42, 8), 14, 70, "ahsap")
    return standard(d, p, foot, hb, "ahşap ayak 124 × 42 mm")


def t02_balik():
    d = Design("02_balik", "Mavi Lagün", "balık evi", "1qr",
               "Balık biçimli panel: lacivert gövde, ipek altın kuyruk ve pullar, kuyrukta masa numarası. İki yüz aynı "
               "sayfa.", masa=7)
    cy = D + 46.0
    body = ellipse(64, 44, -6, cy)
    tail = SM([(48, cy + 4), (70, cy + 22), (92, cy + 40), (86, cy + 14), (80, cy), (86, cy - 14), (92, cy - 40),
               (70, cy - 22), (48, cy - 4)])
    fin = SM([(-30, cy + 40), (-6, cy + 56), (24, cy + 52), (34, cy + 38), (0, cy + 42)])
    p = Panel(tab(U(body, tail, fin), 60, cy - 40), "lacivert")
    scales = U(*[ST(arc_pts(34 + 7.5 * k, cy + j * 9 + (4.5 if k % 2 else 0), 4.6, -75, 75, 20), 1.1)
                 for k in range(3) for j in range(-2, 3) if abs(j * 9 + (4.5 if k % 2 else 0)) < 28 - 4 * k])
    gill = ST(arc_pts(-48, cy, 18, -48, 48, 30), 1.4)
    for side, sg in both(p):
        mir = mirror_fn(sg)
        side.add(mir((tail - body).offset(-2.4, J)), "altin")
        side.add(mir((fin - body).offset(-2.0, J)), "altin")
        side.add(mir(scales + gill), "altin")
        side.add(C(5.2, sg * -50, cy + 12), "fildisi")
        side.add(C(2.3, sg * -50.6, cy + 12), None)
        side.add(tx("fraunces_i", "Mavi Lagün", 8.6, -2 * sg, cy + 30, max_w=74), "fildisi")
        side.qr(url("lagun"), -2 * sg, cy - 1.5, 36)
        side.add(label("BALIK EVİ" if sg > 0 else "MENÜ · YORUM", -2 * sg, cy - 26.8, 3.6), "altin")
        side.add(label("MASA", sg * 69, cy + 7.5, 3.2, tr=0.5), None)
        side.add(tx("fraunces_k", "07", 8.0, sg * 69, cy - 3.0), None)
    foot, hb = foot_wave(150, 44, 14, 2.4, 3, 60, "lacivert", top="fildisi")
    return standard(d, p, foot, hb, "lacivert dalgalı ayak 150 × 44 mm")


def t03_kurek():
    d = Design("03_kurek", "Forno Rosso", "pizzeria", "2qr",
               "Pizza küreği: ahşap gövde, fildişi daire, bordo serif yazı; sapta masa numarası. Ön menü, arka yorum.",
               masa=7)
    cy = D + 56.0
    paddle = C(56, 0, cy)
    neck = P([(-30, cy + 44), (30, cy + 44), (12, cy + 64), (-12, cy + 64)])
    handle = RR(24, 44, 9, 0, cy + 78)
    shape = soft(U(paddle, neck, handle), 4) - C(4.6, 0, cy + 90)
    p = Panel(tab(shape, 40, cy - 50), "ahsap")
    for side, sg in both(p):
        side.add(C(48.5, 0, cy), "fildisi")
        side.add(ring(45.6, 1.0, 0, cy), "bordo")
        side.add(arc_tx("playfair_k", "FORNO ROSSO", 6.4, 0, cy, 35.6, 90, True, 1.3), "bordo")
        side.qr(url("forno", "menu" if sg > 0 else "yorum"), 0, cy, 38, dark="bordo")
        word = "MENÜ" if sg > 0 else "YORUM YAP"
        side.add(arc_tx("jost", word, 4.0, 0, cy, 41.6, 270, False, 1.6), "bordo")
        if sg < 0:
            w = font("jost").width(word, 4.0, 1.6) / 39.6
            for s_ in (-1, 1):
                a = math.radians(270 + s_ * (math.degrees(w / 2) + 7))
                side.add(star(39.6 * math.cos(a), cy + 39.6 * math.sin(a), 2.4), "bordo")
        side.add(label("MASA", 0, cy + 79.2, 3.2, tr=0.6), "fildisi")
        side.add(tx("fraunces_k", "07", 8.0, 0, cy + 68.5), "fildisi")
    foot, hb = foot_plain(C(36), 12, 40, "siyah")
    return standard(d, p, foot, hb, "siyah yuvarlak ayak Ø72 mm (pizza taşı gibi)")


def t04_garaj():
    d = Design("04_garaj", "Garaj Burger", "burger & co.", "nfc",
               "Garaj kapısı biçimi: antrasit zemin, hardal çerçeve, iri Anton yazı; NFC ve QR. Hardal plakada masa no.",
               masa=12)
    top, rise = D + 124.0, 14.0
    Rg = (50 ** 2 + rise ** 2) / (2 * rise)
    a0 = math.degrees(math.atan2(top - (top + rise - Rg), 50))
    arc_ = arc_pts(0, top + rise - Rg, Rg, 180 - a0, a0, 60)
    shape = soft(P(np.vstack([[(-50, D - 2)], arc_, [(50, D - 2)]])), 3)
    p = Panel(tab(shape, 90), "siyah", nfc=(-17, D + 29))
    vis = shape ^ R(-99, D, 99, 999)
    for side, sg in both(p):
        side.add(vis.offset(-3.6, J) - vis.offset(-4.8, J), "hardal")
        side.add(tx("anton", "GARAJ", 22.0, 0, D + 107.5, tr=1.0), "fildisi")
        side.add(label("BURGER & CO.", 0, D + 89.5, 3.8, tr=1.6), "hardal")
        side.qr(url("garaj"), 0, D + 61, 38)
        side.add(phone_waves(sg * -17, D + 29, 14), "hardal")
        side.add(label("DOKUNUN", sg * -7.0, D + 29, 3.8, align="l" if sg > 0 else "r", tr=1.0), "fildisi")
        side.add(RR(40, 10.5, 1.6, 0, D + 14), "hardal")
        side.add(tx("anton", "MASA 12", 6.0, 0, D + 14, tr=1.2), None)
    foot, hb = foot_plain(RR(120, 44, 8), 12, 90, "siyah", top="hardal", top_cs=RR(112, 5, 2.5, 0, -16.5))
    return standard(d, p, foot, hb, "antrasit ayak 120 × 44 mm, hardal şerit")


def t05_zeytin():
    d = Design("05_zeytin", "Zeytinlik", "meze evi", "2qr",
               "Zeytinyağı şişesi: koyu yeşil gövde, fildişi etiket, ipek altın kapak ve zeytin dalı. Ön menü, arka "
               "yorum.", masa=5)
    half = [(0, D - 2), (30, D - 2), (36, D + 8), (36, D + 104), (33, D + 116), (22, D + 128), (12, D + 136),
            (11, D + 156)]
    body = soft(P(half + [(-x, y) for x, y in half[::-1]]), 2)
    lip = RR(28, 6, 2.5, 0, D + 157)
    cap = RR(24, 13, 3, 0, D + 166)
    p = Panel(tab(U(body, lip, cap), 60), "koyu_yesil")
    lab = RR(62, 84, 6, 0, D + 61)
    branch = U(ST(A.smooth([(-24, D + 113), (-6, D + 121), (14, D + 120), (26, D + 113)], n=60), 1.2),
               *[leaf(x, D + y, 9.5, 4.2, a) for x, y, a in ((-16, 118.5, 140), (-6, 121, 70), (6, 121.2, 110),
                                                             (16, 119.5, 40), (-12, 117, -150), (12, 117.5, -30))],
               ellipse(2.0, 2.8, -1, D + 114.2), ellipse(2.0, 2.8, 21.5, D + 112.2))
    for side, sg in both(p):
        side.add(lab, "fildisi")
        side.add(lab.offset(-2.0, J) - lab.offset(-3.0, J), "altin")
        side.add(cap.offset(-1.0, J) + lip.offset(-0.8, J), "altin")
        side.add(mirror_fn(sg)(branch), "altin")
        side.add(tx("fraunces", "Zeytinlik", 8.8, 0, D + 91.5), None)
        side.qr(url("zeytin", "menu" if sg > 0 else "yorum"), 0, D + 54, 36)
        side.add(label("MASA 05", 0, D + 11.2, 3.6), "fildisi")
    f, b = p.front, p.back
    f.add(label("MEZE EVİ", 0, D + 80.5, 3.6), None)
    lab_ = f.add(label("MENÜ", 0, D + 28.5, 4.0, tr=1.8), None)
    hw = lab_.bounds()[2] + 3.5
    for s_ in (-1, 1):
        f.add(rule(s_ * hw, s_ * (hw + 8), D + 28.5, 1.0), None)
    b.add(stars(0, D + 80.5, 2.2, gap=1.1), None)
    b.add(label("DEĞERLENDİRİN", 0, D + 28.5, 3.6, tr=0.8), None)
    foot, hb = foot_plain(ellipse(48, 24), 12, 60, "ahsap")
    return standard(d, p, foot, hb, "ahşap oval ayak 96 × 48 mm")


def t06_kahve():
    d = Design("06_kahve", "Köpük", "kahve & espresso", "wifi",
               "Kahve fincanı ve buhar, ayağı fincan tabağı. Ön: sayfa QR'ı (menü, yorum), arka: misafir Wi-Fi QR'ı.")
    cup = soft(P([(-48, D + 92), (48, D + 92), (40, D + 14), (28, D - 2), (-28, D - 2), (-40, D + 14)]), 5)
    rim = RR(102, 8, 4, 0, D + 92)
    handle = (ring(19, 7.5, 47, D + 54) ^ R(40, 0, 99, 999))
    steam = U(*[ST(A.smooth([(x, D + 93), (x + 6, D + 103), (x - 4, D + 113), (x + 4, D + 124)], n=50), 6.0)
                for x in (-20, 0, 20)])
    p = Panel(tab(U(cup, rim, handle, steam), 56), "kahve")
    for side, sg in both(p):
        side.add(rim.offset(-1.4, J), "fildisi")
        side.add(mirror_fn(sg)(steam).offset(-1.4, J), "fildisi")
        side.add(rule(-38, 38, D + 84.5, 1.2), "latte")
        side.qr(url("kopuk") if sg > 0 else "WIFI:T:WPA;S:Kopuk_Misafir;P:kahve2025;;", 0, D + 38, 34)
    f, b = p.front, p.back
    f.add(tx("fraunces_ki", "köpük", 12.0, 0, D + 75.5), "fildisi")
    f.add(label("KAHVE · ESPRESSO", 0, D + 61.5, 3.6, tr=1.0), "latte")
    f.add(label("MENÜ · YORUM", 0, D + 12.5, 3.6, tr=1.2), "latte")
    b.add(wifi_icon(0, D + 77.5, 15), "fildisi")
    b.add(label("MİSAFİR AĞI", 0, D + 61.5, 3.6, tr=1.4), "latte")
    b.add(label("OKUTUN, BAĞLANIN", 0, D + 12.5, 3.6, tr=0.8), "latte")
    foot, hb = saucer(62, 56, "fildisi", rim_col="latte", rim_w=9)
    return standard(d, p, foot, hb, "fildişi fincan tabağı Ø124 mm, latte kenar")


def lavender(cx, cy, s=1.0, ang=0.0):
    stem = ST(A.smooth([(-14, -12), (-4, -3), (10, 4), (20, 7)], n=40) * s, 1.2)
    buds = U(*[ellipse(1.3 * s, 2.3 * s, x * s, y * s) for x, y in ((-9, -4.5), (-4, -0.4), (2, 2.4), (8, 4.6),
                                                                      (14, 6.6), (-6, -8.0), (0, -3.2), (6, -0.4),
                                                                      (12, 2.0), (18, 4.0))])
    return (stem + buds).rotate(ang).translate((cx, cy))


def t07_bistro():
    d = Design("07_bistro", "Lavanta", "bistro", "nfc",
               "Oval panel: mor zemin, lila çift çerçeve ve lavanta dalı, Playfair italik. NFC ve QR aynı sayfaya.",
               masa=7)
    cy = D + 68.0
    ov = ellipse(48, 70, 0, cy)
    p = Panel(tab(ov, 50, D + 2), "mor", nfc=(-13, D + 35))
    vis = ov ^ R(-99, D, 99, 999)
    frame = (vis.offset(-3.6, J) - vis.offset(-5.0, J)) + (vis.offset(-6.4, J) - vis.offset(-7.4, J))
    for side, sg in both(p):
        side.add(frame, "lila")
        side.add(mirror_fn(sg)(lavender(0, D + 124, 0.95)), "lila")
        side.add(tx("playfair_ki", "Lavanta", 10.5, 0, D + 104.5), "fildisi")
        side.add(label("BİSTRO" if sg > 0 else "REZERVASYON", 0, D + 92.5, 3.6, tr=2.0 if sg > 0 else 1.0), "lila")
        side.qr(url("lavanta"), 0, D + 67.5, 34)
        nx = sg * -13
        side.add(ring(11.5, 1.3, nx, D + 35), "lila")
        side.add(phone_waves(nx + 0.5, D + 35, 12.5), "fildisi")
        side.add(label("DOKUN", nx, D + 17.6, 3.4, tr=0.8), "lila")
        side.add(label("MASA", -nx - 2, D + 40, 3.4, tr=0.8), "lila")
        side.add(tx("playfair_ki", "07", 8.0, -nx - 2, D + 30.5), "fildisi")
    foot, hb = foot_plain(ellipse(44, 18), 10, 50, "altin")
    return standard(d, p, foot, hb, "ipek altın oval ayak 88 × 36 mm")


def t08_ates():
    d = Design("08_ates", "Ateş", "ocakbaşı", "2qr",
               "Alev tepeli panel: antrasit zemin, ipek bakır çerçeve, iri Big Shoulders yazı. Ön menü, arka yorum.",
               masa=14)
    top = A.smooth([(-48, D + 96), (-43, D + 113), (-31, D + 134), (-22, D + 121), (-11, D + 136), (0, D + 161),
                    (10, D + 138), (19, D + 125), (31, D + 145), (42, D + 121), (48, D + 96)], n=200)
    shape = P(np.vstack([[(-48, D - 2)], top, [(48, D - 2)]]))
    p = Panel(tab(shape, 76), "siyah")
    vis = shape ^ R(-99, D, 99, 999)
    for side, sg in both(p):
        side.add(vis.offset(-3.4, J) - vis.offset(-4.6, J), "bakir")
        side.add(tx("bigsh", "ATEŞ", 24.0, 0, D + 100.5, tr=1.6), "fildisi")
        side.qr(url("ates", "menu" if sg > 0 else "yorum"), 0, D + 52, 38)
        side.add(label("MASA 14", 0, D + 13.0, 3.6, tr=1.4), "bakir")
    f, b = p.front, p.back
    f.add(label("OCAKBAŞI", 0, D + 79.5, 3.8, tr=2.2), "bakir")
    lab_ = f.add(label("MENÜ", 0, D + 24.5, 4.4, tr=2.0), "fildisi")
    hw = lab_.bounds()[2] + 3.5
    for s_ in (-1, 1):
        f.add(rule(s_ * hw, s_ * (hw + 12), D + 24.5, 1.0), "bakir")
    b.add(stars(0, D + 79.5, 2.3, gap=1.2), "bakir")
    b.add(label("DEĞERLENDİRİN", 0, D + 24.5, 4.0, tr=1.0), "fildisi")
    hexa = C(50, n=6).rotate(30)
    foot, hb = foot_plain(hexa, 14, 76, "siyah", top="bakir", top_cs=hexa.offset(-3, J) - hexa.offset(-5.5, J))
    return standard(d, p, foot, hb, "antrasit altıgen ayak, ipek bakır halka")


def t09_limon():
    d = Design("09_limon", "Limon Ağacı", "kahvaltı evi", "1qr",
               "Limon dilimi ve yaprak: limon sarısı kabuk, fildişi dilimler, koyu yeşil yazı; ortada QR ve masa no.",
               masa=9)
    cy = D + 61.0
    disc = C(60, 0, cy)
    lf = leaf(3, cy + 56, 36, 17, 58)
    p = Panel(tab(U(disc, lf), 40, D + 3), "sari")
    for side, sg in both(p):
        mir = mirror_fn(sg)
        side.add(ring(55.5, 2.6, 0, cy), "fildisi")
        for a in (-26, 0, 26, 154, 180, 206):
            r0, r1 = 33.5, 51.5
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            side.add(ST([(r0 * ca, cy + r0 * sa), (r1 * ca, cy + r1 * sa)], 2.0), "fildisi")
        side.add(C(31.5, 0, cy), "fildisi")
        side.add(mir(lf.offset(-1.6, J) - disc.offset(1.2, J)), "koyu_yesil")
        side.add(mir(ST(A.smooth([(5, cy + 60), (18, cy + 73), (30, cy + 84)], n=30), 1.0)), None)
        side.add(arc_tx("fraunces_k", "Limon Ağacı" if sg > 0 else "Tüm Gün Kahvaltı", 7.0 if sg > 0 else 6.0, 0, cy,
                        39.6, 90, True, 0.5), "koyu_yesil")
        side.add(arc_tx("jost", "KAHVALTI EVİ" if sg > 0 else "MENÜ · YORUM", 3.8, 0, cy, 41.6, 270, False, 1.2),
                 "koyu_yesil")
        side.qr(url("limon"), 0, cy + 3.5, 34, dark="koyu_yesil")
        side.add(label("MASA 09", 0, cy - 22.5, 3.6, tr=1.0), "koyu_yesil")
    foot, hb = foot_plain(C(34), 12, 40, "koyu_yesil")
    return standard(d, p, foot, hb, "koyu yeşil yuvarlak ayak Ø68 mm")


def brush_ring(cx, cy, r, a0, a1, w0, w1, n=90):
    """Fırça darbesi gibi kalınlığı değişen yay (enso)."""
    ts = np.linspace(0, 1, n)
    return U(*[C((w0 + (w1 - w0) * math.sin(math.pi * t) ** 0.7) / 2,
                 cx + r * math.cos(math.radians(a0 + (a1 - a0) * t)),
                 cy + r * math.sin(math.radians(a0 + (a1 - a0) * t)), 24) for t in ts]).offset(0.3, J).offset(-0.3, J)


def t10_sushi():
    d = Design("10_sushi", "Koi", "sushi & ramen", "nfc",
               "Kare fildişi panel: siyah fırça halkası (enso), dikey KOI, kırmızı güneşte NFC. Ayakta yemek çubuğu "
               "yuvası.", masa=8)
    sq = RR(110, 112, 6, 0, D + 54)
    p = Panel(tab(sq, 90), "fildisi", nfc=(-36, D + 91))
    for side, sg in both(p):
        side.add(C(14, sg * -36, D + 91), "kirmizi")
        side.add(phone_waves(sg * -35.5, D + 91, 15), "fildisi")
        side.add(label("DOKUNUN", sg * -36, D + 72.0, 3.6, tr=0.8), "kirmizi")
        for k, ch in enumerate("KOI"):
            side.add(tx("syne", ch, 11.5, sg * -36, D + 54.5 - k * 16.0), "siyah")
        side.add(brush_ring(sg * 15, D + 58, 35.5, 70 if sg > 0 else 110, 70 + 300 if sg > 0 else 110 - 300, 1.4, 4.2),
                 "siyah")
        side.qr(url("koi"), sg * 15, D + 58, 40, dark="siyah")
        side.add(label("SUSHI & RAMEN" if sg > 0 else "MENÜ · SİPARİŞ", sg * 15, D + 14.5, 3.6, tr=1.0), "kirmizi")
        side.add(label("MASA", sg * 44, D + 104.5, 3.2, tr=0.5), "siyah")
        side.add(tx("syne", "08", 6.5, sg * 44, D + 95.5), "siyah")
    plank = RR(140, 36, 6)
    f = solid(plank, 12) - slot(90, 12) - box(-62, -15.5, 12 - 2.4, 62, -9.5, 13)
    d.props = [("Yemek çubuğu", m3.Manifold.cylinder(118, 1.9, 1.2, 24).rotate((0, 90, 0)).translate(
        (-58, -12.5 + dy, 12 - 0.6)), "ahsap") for dy in (-1.4, 1.6)]
    return standard(d, p, [("Ayak (siyah)", f, "siyah")], 12, "siyah ayak 140 × 36 mm, çubuk yuvalı")


def t11_pide():
    d = Design("11_pide", "Taş Fırın", "pide & lahmacun", "2qr",
               "Pide biçimi: karamel kenar, fildişi iç, kahverengi Fraunces yazı. Ön menü, arka Google yorumu.", masa=4)
    L, Hh, cy = 95.0, 40.0, D + 41.0
    xs = np.linspace(-L, L, 161)
    hh = Hh * np.clip(1 - (xs / L) ** 2, 0, None) ** 0.75
    lens = soft(P(np.vstack([np.c_[xs, cy + hh], np.c_[xs[::-1], cy - hh[::-1]]])), 1.5)
    p = Panel(tab(lens, 70, cy - 30), "karamel")
    inner = lens.offset(-7, J)
    twists = U(*[ST([(sx * (L - 16 - 6 * k), cy - 4), (sx * (L - 12 - 6 * k), cy + 4)], 1.4)
                 for sx in (-1, 1) for k in range(2)])
    for side, sg in both(p):
        side.add(inner, "fildisi")
        side.add(twists, "kahve")
        qx, x_ = sg * 32, sg * -38
        side.qr(url("pide", "menu" if sg > 0 else "yorum"), qx, cy, 40, dark="kahve")
        side.add(tx("fraunces_k", "Taş Fırın", 9.0, x_, cy + 10.5, max_w=56), "kahve")
        side.add(label("MASA 04", x_, cy - 18.0, 3.6, tr=1.0), "karamel")
        if sg > 0:
            side.add(label("PİDE · LAHMACUN", x_, cy + 0.2, 3.6, tr=0.6), "karamel")
            side.add(label("MENÜ", x_ - 7, cy - 8.8, 4.0, tr=1.4), "kahve")
            side.add(arrow(x_ + 5, cy - 8.8, 13, 1.2, 2.6, 1), "kahve")
        else:
            side.add(stars(x_, cy + 0.2, 2.2, gap=1.0), "karamel")
            side.add(arrow(x_ - 9, cy - 8.8, 12, 1.2, 2.6, -1), "kahve")
            side.add(label("YORUM", x_ + 6, cy - 8.8, 4.0, tr=1.4), "kahve")
    foot, hb = foot_plain(RR(160, 38, 12), 10, 70, "ahsap")
    return standard(d, p, foot, hb, "ahşap ayak 160 × 38 mm")


def snowflake(cx, cy, r, w=1.3):
    arms = []
    for k in range(6):
        a = math.radians(90 + 60 * k)
        ux, uy = math.cos(a), math.sin(a)
        arms.append(ST([(cx, cy), (cx + r * ux, cy + r * uy)], w))
        bx, by = cx + r * 0.55 * ux, cy + r * 0.55 * uy
        for s_ in (-1, 1):
            b = a + s_ * math.radians(45)
            arms.append(ST([(bx, by), (bx + r * 0.32 * math.cos(b), by + r * 0.32 * math.sin(b))], w))
    return U(*arms)


def t12_dondurma():
    d = Design("12_dondurma", "Kar Tanesi", "dondurma", "1qr",
               "Külah dondurma: pembe top, karamel külah, ince kahverengi kafes, Fraunces italik. İki yüz aynı sayfa.")
    tip = D - 40.0
    cone = P([(-37, D + 88), (37, D + 88), (0, tip)])
    scoop = C(44, 0, D + 114)
    drips = U(*[RR(w, h, w / 2 - 0.01, x, D + 86 - h / 2 + 4) for x, w, h in ((-30, 10, 10), (-14, 9, 14), (4, 11, 12),
                                                                              (22, 9, 14), (36, 8, 8))])
    blob = U(scoop, drips, RR(92, 14, 7, 0, D + 88))
    p = Panel(tab(U(cone, blob), 26), "karamel")
    grid = U(*[ST([(x0, D - 10), (x0 + 120, D + 110)], 1.2) for x0 in np.arange(-130, 60, 11.0)] +
             [ST([(x0, D - 10), (x0 - 120, D + 110)], 1.2) for x0 in np.arange(-60, 130, 11.0)])
    for side, sg in both(p):
        mir = mirror_fn(sg)
        side.add(mir(grid) ^ cone.offset(-3, J) ^ R(-99, D + 6, 99, D + 51), "kahve")
        side.add(mir(blob).offset(-1.4, J), "pembe")
        side.add(snowflake(0, D + 148, 6.5), "fildisi")
        side.qr(url("kar"), 0, D + 116, 40, dark="kahve")
        if sg > 0:
            side.add(tx("fraunces_ki", "Kar Tanesi", 7.6, 0, D + 68.5), "fildisi")
            side.add(label("DONDURMA", 0, D + 58.0, 3.6, tr=1.6), "kahve")
        else:
            side.add(tx("fraunces_ki", "Bugün hangi tat?", 5.2, 0, D + 68.5), "fildisi")
            side.add(label("MENÜ · YORUM", 0, D + 58.0, 3.6, tr=0.8), "kahve")
    foot, hb = foot_plain(C(32), 14, 26, "pembe")
    return standard(d, p, foot, hb, "pembe yuvarlak ayak Ø64 mm")


def t13_cay():
    d = Design("13_cay", "Asmaaltı", "çay bahçesi", "2qr",
               "İnce belli çay bardağı, ayağı çay tabağı: bordo çay, beyaz boş kısım, ipek altın kenar ve asma yaprağı.",
               masa=11)
    half = [(0, D - 2), (22, D - 2), (29, D + 12), (34, D + 34), (32, D + 58), (27, D + 80), (30, D + 100),
            (36, D + 118), (40, D + 132)]
    glass = SM([(x, y) for x, y in half[1:]] + [(-x, y) for x, y in half[:0:-1]])
    glass = (glass ^ R(-99, -99, 99, D + 132)) + RR(82, 4, 2, 0, D + 131)
    p = Panel(tab(glass, 46), "bordo")
    vine = U(leaf(-6, D + 92, 13, 9, 150), leaf(-2, D + 94, 12, 8, 75), leaf(3, D + 92, 13, 9, 25),
             C(1.5, 8, D + 89), C(1.5, 11.2, D + 88.2), C(1.5, 9.6, D + 85.4))
    for side, sg in both(p):
        side.add(glass ^ R(-99, D + 112, 99, 999), "beyaz")
        side.add(glass ^ R(-99, D + 129.2, 99, 999), "altin")
        side.add(rule(-32, 32, D + 110.8, 1.2), "altin")
        side.add(tx("playfair_k", "ASMAALTI", 6.6, 0, D + 120.8, tr=0.8, max_w=62), None)
        side.add(mirror_fn(sg)(vine), "altin")
        side.qr(url("asma", "menu" if sg > 0 else "yorum"), 0, D + 40, 36)
        side.add(label("MASA 11", 0, D + 12.5, 3.6, tr=1.2), "fildisi")
    p.front.add(label("ÇAY BAHÇESİ", 0, D + 76, 3.6, tr=1.2), "fildisi")
    p.front.add(label("MENÜ", 0, D + 66.5, 4.0, tr=2.2), "altin")
    p.back.add(stars(0, D + 76, 2.2, gap=1.0), "altin")
    p.back.add(label("DEĞERLENDİRİN", 0, D + 66.5, 3.6, tr=0.6), "altin")
    foot, hb = saucer(48, 46, "beyaz", rim_col="bordo")
    return standard(d, p, foot, hb, "beyaz çay tabağı Ø96 mm, bordo kenar")


def cleaver(cx, cy, s):
    blade = RR(s, s * 0.6, s * 0.06, cx, cy) - C(s * 0.06, cx + s * 0.32, cy + s * 0.16)
    handle = RR(s * 0.62, s * 0.2, s * 0.1, cx - s * 0.75, cy + s * 0.14)
    return U(blade, handle)


def t14_kasap():
    d = Design("14_kasap", "Kasaphane", "et lokantası · 1974", "2qr",
               "Kesme tahtası: ahşap gövde, önde 1 mm kabartma siyah Bodoni yazı (yanık damga gibi), fildişi QR. "
               "Çapraz ayak.", masa=7)
    board = U(RR(112, 124, 10, 0, 62), RR(44, 38, 12, 0, 131)) - C(5.5, 0, 140.5)
    foot, cut = cross_foot(72, 24, "ahsap")
    p = Panel(board - cut, "ahsap", vis_y=0.0)
    f, b = p.front, p.back
    f.add(cleaver(6, 106.5, 24), "siyah", raised=True)
    f.add(tx("bodoni", "KASAPHANE", 8.6, 0, 90, tr=0.6, max_w=94), "siyah", raised=True)
    f.add(label("ET LOKANTASI · 1974", 0, 80.0, 3.6, tr=0.9), "siyah", raised=True)
    f.qr(url("kasap", "menu"), 0, 53, 40, dark="siyah")
    f.add(tx("bodoni", "MENÜ", 5.0, 0, 27.0, tr=1.6), "siyah", raised=True)
    f.add(label("MASA", 0, 130.0, 3.2, tr=0.6), "siyah", raised=True)
    f.add(tx("bodoni", "07", 7.0, 0, 121.0), "siyah", raised=True)
    b.add(cleaver(-6, 106.5, 24).mirror((1, 0)), "siyah")
    b.add(tx("bodoni", "KASAPHANE", 8.6, 0, 90, tr=0.6, max_w=94), "siyah")
    b.add(stars(0, 80.0, 2.3, gap=1.1), "siyah")
    b.qr(url("kasap", "yorum"), 0, 53, 40, dark="siyah")
    b.add(label("DEĞERLENDİRİN", 0, 27.0, 3.8, tr=0.8), "siyah")
    b.add(label("MASA", 0, 130.0, 3.2, tr=0.6), "siyah")
    b.add(tx("bodoni", "07", 7.0, 0, 121.0), "siyah")
    double(d, p, 0.0)
    d.stand += foot
    d.stand_desc = "takılır çapraz ahşap ayak"
    return d


def kilim_band(x0, x1, y0, y1):
    h = y1 - y0
    band = R(x0, y0, x1, y1)
    n = int((x1 - x0) // 6)
    step = (x1 - x0) / n
    teeth = []
    for k in range(n):
        a = x0 + k * step
        teeth.append(P([(a, y0), (a + step, y0), (a + step / 2, y0 + h * 0.22)]))
        teeth.append(P([(a, y1), (a + step, y1), (a + step / 2, y1 - h * 0.22)]))
    m = int((x1 - x0) // (h * 1.05))
    st = (x1 - x0) / m
    dia, core = [], []
    for k in range(m):
        cx, cy = x0 + st * (k + 0.5), (y0 + y1) / 2
        r = h * 0.3
        dia.append(diamond(cx, cy, r))
        core.append(diamond(cx, cy, r * 0.42))
    return band, U(*teeth, *dia), U(*core)


def t15_gozleme():
    d = Design("15_gozleme", "Yayla", "gözleme evi", "2qr",
               "Kilim desenli panel: kırmızı zemin, fildişi-siyah kilim şeritleri, Fraunces Black. Ön menü, arka yorum.",
               masa=7)
    pan = RR(108, 146, 4, 0, D + 71)
    p = Panel(tab(pan, 108), "kirmizi")
    bands = (kilim_band(-50.5, 50.5, D + 118, D + 139), kilim_band(-50.5, 50.5, D + 4, D + 16))
    for side, sg in both(p):
        for band, black, core in bands:
            side.add(band, "fildisi")
            side.add(black, "siyah")
            side.add(core, None)
        side.add(tx("fraunces_k", "YAYLA", 13.0, 0, D + 104, tr=1.4), "fildisi")
        side.qr(url("yayla", "menu" if sg > 0 else "yorum"), 0, D + 62, 40, dark="siyah")
        side.add(label("MASA 07", 0, D + 23.5, 3.6, tr=1.2), "fildisi")
    p.front.add(label("GÖZLEME EVİ", 0, D + 91.5, 3.8, tr=1.8), "fildisi")
    p.front.add(tx("fraunces_k", "MENÜ", 6.0, 0, D + 33, tr=1.6), "fildisi")
    p.back.add(stars(0, D + 91.5, 2.4, gap=1.2), "fildisi")
    p.back.add(label("DEĞERLENDİRİN", 0, D + 33, 3.8, tr=0.9), "fildisi")
    f = solid(RR(126, 46, 8), 7) + solid(RR(114, 34, 6), 7, 7)
    return standard(d, p, [("Ayak (siyah)", f - slot(108, 14), "siyah")], 14, "siyah basamaklı ayak 126 × 46 mm")


def t16_sorf():
    d = Design("16_sorf", "Palmiye", "beach club", "nfc",
               "Sörf tahtası: lacivert gövde, fildişi orta çizgi, kum rengi şeritler, Norican el yazısı. Şezlong "
               "numaralı.", masa=12)
    pts = [(0, D + 170), (16, D + 160), (29, D + 136), (35, D + 100), (35, D + 50), (31, D + 16), (22, D - 2),
           (-22, D - 2), (-31, D + 16), (-35, D + 50), (-35, D + 100), (-29, D + 136), (-16, D + 160)]
    board = SM(pts)
    board = (board ^ R(-99, D - 2, 99, 999))
    p = Panel(tab(board, 40), "lacivert", nfc=(0, D + 36))
    for side, sg in both(p):
        side.add(R(-0.6, D + 140, 0.6, D + 163) ^ board.offset(-4, J), "fildisi")
        for y in (D + 147.5, D + 152.5):
            side.add(R(-99, y - 1.4, 99, y + 1.4) ^ board.offset(-2.5, J), "kum")
        side.add(label("ŞEZLONG 12", 0, D + 133.5, 3.6, tr=1.0), "kum")
        side.add(tx("norican", "Palmiye", 10.0, 0, D + 117), "fildisi")
        side.add(label("BEACH CLUB" if sg > 0 else "SİPARİŞ · MENÜ", 0, D + 103.5, 3.6, tr=1.6 if sg > 0 else 0.8),
                 "kum")
        side.qr(url("palmiye"), 0, D + 76, 38)
        side.add(ring(11.5, 1.3, 0, D + 36), "kum")
        side.add(phone_waves(0.5, D + 36, 12.5), "fildisi")
        side.add(label("DOKUNUN", 0, D + 17.5, 3.6, tr=1.0), "kum")
    foot, hb = foot_wave(110, 44, 14, 2.2, 2, 40, "kum", top="fildisi")
    return standard(d, p, foot, hb, "kum rengi dalgalı ayak 110 × 44 mm")


def t17_pasta():
    d = Design("17_pasta", "Tatlı Rüya", "pastane", "2qr",
               "Pasta fanusu: pembe kubbe, fildişi tabak ve tutamak, kahverengi Norican yazı; kademeli kek standı ayak.",
               masa=4)
    dome = ellipse(60, 70, 0, D + 14) ^ R(-99, D + 14, 99, 999)
    plate = RR(132, 10, 5, 0, D + 9)
    knob = U(C(7, 0, D + 90), RR(6, 8, 2, 0, D + 84))
    p = Panel(tab(U(dome, plate, knob), 120), "pembe")
    shine = ST(arc_pts(0, D + 14, 52, 118, 152, 30), 1.6)
    for side, sg in both(p):
        side.add(plate.offset(-0.8, J), "fildisi")
        side.add(knob.offset(-0.8, J), "fildisi")
        side.add(mirror_fn(sg)(shine), "fildisi")
        side.add(tx("norican", "Tatlı Rüya", 9.0, 0, D + 66), "kahve")
        side.qr(url("ruya", "menu" if sg > 0 else "yorum"), 0, D + 33, 32, dark="kahve")
        side.add(label("MASA 04", 0, D + 9, 3.4, tr=1.2), "kahve")
    p.front.add(label("PASTANESİ", 0, D + 53.5, 3.6, tr=2.0), "kahve")
    p.front.add(heart(0, D + 76.5, 6.0), "fildisi")
    p.back.add(label("TATLI BİR YORUM BIRAKIN", 0, D + 53.5, 3.4, tr=0.4), "kahve")
    p.back.add(stars(0, D + 76.5, 2.2, gap=1.0), "fildisi")
    f = (m3.Manifold.cylinder(4, 44, 44, 128) + m3.Manifold.cylinder(6, 38, 32, 128).translate((0, 0, 4)) +
         m3.Manifold.cylinder(4, 34, 34, 128).translate((0, 0, 10)))
    return standard(d, p, [("Kek standı (fildişi)", f - slot(120, 14), "fildisi")], 14,
                    "fildişi kademeli kek standı Ø88 mm")


def t18_tabak():
    d = Design("18_tabak", "Gurme Masa", "fine dining", "1qr",
               "Tabak, çatal ve bıçak: antrasit zemin, ipek altın kenar ve çatal-bıçak, Bodoni yazı. İki yüz aynı sayfa.",
               masa=1)
    cy = D + 56.0
    plate = C(54, 0, cy)
    fk = fork(-68, D - 1, D + 124, 10)
    kn = knife(68, D - 1, D + 124, 9)
    shape = U(plate, fk, kn)
    p = Panel((shape ^ R(-999, D, 999, 999)) + R(-74, 0, 74, D + 1), "siyah")
    for side, sg in both(p):
        side.add(ring(51.5, 1.8, 0, cy), "altin")
        side.add(ring(45.5, 1.0, 0, cy), "altin")
        side.add(mirror_fn(sg)(fk.offset(-1.0, J) + kn.offset(-1.0, J)), "altin")
        side.add(arc_tx("bodoni", "GURME MASA", 6.0, 0, cy, 33.6, 90, True, 1.6), "altin")
        side.add(arc_tx("jost", "MASA 01 · OKUTUN", 3.6, 0, cy, 40.2, 270, False, 1.1), "fildisi")
        side.qr(url("gurme"), 0, cy, 34, dark="siyah")
    f = solid(RR(158, 34, 6), 10) - slot(148, 10)
    return standard(d, p, [("Ayak (siyah)", f, "siyah")], 10, "antrasit kaide 158 × 34 mm")


def t19_vegan():
    d = Design("19_vegan", "Bostan", "vegan mutfak", "nfc",
               "Saksıda büyük yaprak: koyu yeşil yaprak, açık yeşil damarlar, fildişi yazı; ayak terrakota saksı.",
               masa=6)
    half = [(0, D + 152), (22, D + 138), (38, D + 114), (45, D + 88), (42, D + 62), (30, D + 40), (14, D + 27),
            (7, D + 22)]
    lf = SM(half + [(-x, y) for x, y in half[:0:-1]])
    stem = R(-7, D - 2, 7, D + 26)
    p = Panel(tab(U(lf, stem), 14, extra=6), "koyu_yesil", nfc=(0, D + 50))
    veins = []
    for s_ in (-1, 1):
        for y0, y1, x1 in ((D + 64, D + 80, 38), (D + 96, D + 112, 36), (D + 40, D + 52, 30)):
            veins.append(ST(A.smooth([(s_ * 21, y0), (s_ * (21 + x1) / 2, (y0 + y1) / 2 - 1), (s_ * x1, y1)], n=24),
                            1.3))
    veins += [ST([(0, D + 128), (0, D + 146)], 1.4), ST([(0, D + 22), (0, D + 36)], 1.4)]
    for side, sg in both(p):
        side.add(U(*veins), "yesil")
        side.add(tx("fraunces_k", "bostan", 9.0, 0, D + 117.5), "fildisi")
        side.add(label("VEGAN MUTFAK" if sg > 0 else "MENÜ · SİPARİŞ", 0, D + 107.5, 3.4, tr=0.9), "yesil")
        side.qr(url("bostan"), 0, D + 84, 34)
        side.add(ring(11.0, 1.3, 0, D + 50), "yesil")
        side.add(phone_waves(0.5, D + 50, 12.0), "fildisi")
        side.add(label("MASA 06", 0, D + 33.5, 3.4, tr=0.8), "fildisi")
    pot = (m3.Manifold.cylinder(40, 26, 32, 128) + m3.Manifold.cylinder(9, 36, 36, 128).translate((0, 0, 38)))
    hb = 47.0
    pot = pot - slot(14, hb, depth=D + 6)
    return standard(d, p, [("Saksı (terrakota)", pot, "terrakota")], hb, "terrakota saksı Ø72 mm")


def t20_tahta():
    d = Design("20_tahta", "Nonna", "ev yapımı makarna", "2qr",
               "A tipi kara tahta: iki siyah panel, ahşap çerçeve, tebeşir gibi Caveat el yazısı; bir yüz menü, öbürü "
               "yorum.", masa=5)
    out = RR(100, 140, 4, 0, 70)
    frame = out.offset(-1.0, J) - out.offset(-7.0, J)
    p1, p2 = Panel(out, "siyah", vis_y=0.0), Panel(out, "siyah", vis_y=0.0)
    for p, menu in ((p1, True), (p2, False)):
        s = p.front
        s.add(frame, "ahsap")
        s.add(tx("caveat", "Nonna", 16.0, 0, 113), "fildisi")
        s.add(tx("caveat", "ev yapımı makarna" if menu else "nasıldı?", 6.4 if menu else 7.4, 0, 96.5), "fildisi")
        s.qr(url("nonna", "menu" if menu else "yorum"), 0, 62, 38)
        if menu:
            s.add(tx("caveat", "menü burada", 6.4, -6, 32.5), "fildisi")
            s.add(ST(A.smooth([(20, 31), (27, 35), (30, 40)], n=20), 1.2) +
                  ST([(26.5, 38.5), (30, 41.5), (31.5, 37.5)], 1.2), "fildisi")
        else:
            s.add(U(*[star(-20 + 10 * k, 33, 4.0) - star(-20 + 10 * k, 33, 4.0).offset(-1.1, J) for k in range(5)]),
                  "fildisi")
        s.add(tx("caveat", "masa 5", 6.6, 0, 19), "fildisi")
    tilt = 14.0
    reach = 140 * math.sin(math.radians(tilt))
    d.put(p1, upright(0.0, y0=-reach - 1.0, tilt=tilt))
    d.put(p2, upright(0.0, y0=reach + 1.0, turn=True, tilt=-tilt))
    zt = 140 * math.cos(math.radians(tilt))
    cap = along_y(soft(P([(-11, zt - 12), (11, zt - 12), (11, zt - 2), (0, zt + 6), (-11, zt - 2)]), 1.5), 108)
    d.stand.append(("Tepe bağlantısı (ahşap)", cap, "ahsap"))
    d.stand_desc = "A tipi: iki panel, ahşap tepe bağlantısı"
    return d


def t21_baklava():
    d = Design("21_baklava", "Fıstıkzade", "baklava", "1qr",
               "Baklava dilimi biçimi: koyu yeşil zemin, ipek altın çift çerçeve, Playfair Black. İki yüz aynı sayfa.",
               masa=3)
    dia = soft(diamond(0, D + 60, 60, 90), 3)
    p = Panel(tab(dia, 40), "koyu_yesil")
    vis = dia ^ R(-99, D, 99, 999)
    orn = U(diamond(0, D + 120, 4.5, 7.0), C(1.6, -9, D + 120), C(1.6, 9, D + 120))
    for side, sg in both(p):
        side.add((vis.offset(-3.4, J) - vis.offset(-4.6, J)) + (vis.offset(-6.2, J) - vis.offset(-7.2, J)), "altin")
        side.add(orn, "altin")
        side.add(tx("playfair_k", "FISTIKZADE", 6.0, 0, D + 88.5, tr=0.8, max_w=58), "altin")
        side.add(label("BAKLAVA" if sg > 0 else "ANTEP FISTIKLI", 0, D + 79, 3.6, tr=1.6 if sg > 0 else 0.8),
                 "fildisi")
        side.qr(url("fistik"), 0, D + 55.5, 34)
        side.add(label("MENÜ · YORUM", 0, D + 33.5, 3.4, tr=0.8), "altin")
        side.add(label("MASA 03", 0, D + 25.5, 3.6, tr=1.0), "fildisi")
    sq = RR(64, 44, 6)
    foot, hb = foot_plain(sq, 14, 40, "koyu_yesil", top="altin", top_cs=sq.offset(-2.5, J) - sq.offset(-4.5, J))
    return standard(d, p, foot, hb, "koyu yeşil ayak 64 × 44 mm, altın çizgi")


def t22_kaktus():
    d = Design("22_kaktus", "Taco Loco", "Meksika mutfağı", "nfc",
               "Kaktüs: koyu yeşil gövde, mercan çiçek, fildişi yazı ve QR; kolda masa no. Ayakta mercan zikzak.",
               masa=7)
    col = RR(56, 140, 28, 0, D + 68)
    arm_l = U(RR(30, 16, 8, -38, D + 58), RR(16, 44, 8, -46, D + 79))
    arm_r = U(RR(30, 16, 8, 38, D + 76), RR(16, 42, 8, 46, D + 94))
    flower = U(*[C(4.6, 5.2 * math.cos(math.radians(90 + 72 * k)), D + 141 + 5.2 * math.sin(math.radians(90 + 72 * k)))
                 for k in range(5)], C(4, 0, D + 141))
    p = Panel(tab(U(col, arm_l, arm_r, flower), 50), "koyu_yesil", nfc=(0, D + 34))
    dots = U(*[C(0.85, x, D + y) for x, y in ((-49, 92), (-43, 86), (-49, 72), (-30, 61), (30, 79), (-18, 128),
                                                (18, 128))])
    for side, sg in both(p):
        mir = mirror_fn(sg)
        side.add(flower.offset(-0.8, J), "mercan")
        side.add(C(2.4, 0, D + 141), "fildisi")
        side.add(mir(dots), "fildisi")
        side.add(tx("bricolage", "TACO", 11.5, 0, D + 120, tr=0.8), "fildisi")
        side.add(tx("bricolage", "LOCO", 11.5, 0, D + 104.5, tr=0.8), "mercan")
        side.qr(url("taco"), 0, D + 72, 38)
        side.add(ring(11.0, 1.3, 0, D + 34), "mercan")
        side.add(phone_waves(0.5, D + 34, 12.0), "fildisi")
        side.add(label("DOKUNUN" if sg > 0 else "SİPARİŞ", 0, D + 16.5, 3.4, tr=0.6), "fildisi")
        side.add(label("MASA", sg * 46, D + 104.5, 3.2, tr=0.3), "mercan")
        side.add(tx("bricolage", "07", 7.0, sg * 46, D + 94.5), "fildisi")
    base = RR(124, 46, 8)
    xs = np.linspace(-58, 58, 25)
    zig = ST([(x, -17.5 + (2.2 if k % 2 else -2.2)) for k, x in enumerate(xs)], 1.6)
    foot, hb = foot_plain(base, 14, 50, "kum", top="mercan", top_cs=zig)
    return standard(d, p, foot, hb, "kum rengi ayak 124 × 46 mm, mercan zikzak")


def t23_wok():
    d = Design("23_wok", "Wok Ustası", "noodle bar", "2qr",
               "Paket servis noodle kutusu ve yemek çubukları: fildişi kutu, kırmızı bant, Archivo geniş yazı.", masa=9)
    boxs = soft(P([(-52, D + 94), (52, D + 94), (40, D - 2), (-40, D - 2)]), 2.5)
    flap = soft(P([(-52, D + 93), (-28, D + 93), (-33, D + 104), (-56, D + 102)]), 1.2)
    sticks = U(ST([(6, D + 84), (30, D + 150)], 4.6), ST([(16, D + 84), (42, D + 146)], 4.6))
    shape = U(boxs, flap, flap.mirror((1, 0)), sticks)
    p = Panel(tab(shape, 76), "fildisi")
    for side, sg in both(p):
        mir = mirror_fn(sg)
        side.add(mir(sticks - boxs.offset(-1.0, J)).offset(-1.0, J), "siyah")
        side.add(R(-99, D + 66, 99, D + 91) ^ boxs, "kirmizi")
        side.add(U(flap, flap.mirror((1, 0))).offset(-1.0, J), "kirmizi")
        side.add(tx("archivo_x", "WOK USTASI", 6.0, 0, D + 82.5, tr=0.6, max_w=86), "fildisi")
        side.qr(url("wok", "menu" if sg > 0 else "yorum"), 0, D + 44, 36, dark="siyah")
        side.add(label("MASA 09", 0, D + 10.5, 3.6, tr=1.2), "siyah")
    p.front.add(label("NOODLE BAR", 0, D + 72.5, 3.6, tr=2.0), "fildisi")
    p.front.add(label("MENÜ", 0, D + 19.0, 4.0, tr=2.2), "kirmizi")
    p.back.add(stars(0, D + 72.5, 2.2, gap=1.1), "fildisi")
    p.back.add(label("DEĞERLENDİRİN", 0, D + 19.0, 3.6, tr=0.6), "kirmizi")
    foot, hb = foot_plain(RR(100, 38, 6), 10, 76, "siyah")
    return standard(d, p, foot, hb, "siyah ayak 100 × 38 mm")


def t24_tabela():
    d = Design("24_tabela", "Döner Sokak", "dürüm & döner", "1qr",
               "Sokak tabelası direkte: lacivert tabela, fildişi kenar ve Barlow yazı; direkte kapı numarası gibi masa "
               "no.", masa=7)
    sign = RR(146, 66, 4, 0, D + 110)
    pole = R(-7, D - 2, 7, D + 80)
    plate = RR(30, 24, 3, 0, D + 44)
    p = Panel(tab(U(sign, pole, plate), 14, extra=6), "lacivert")
    for side, sg in both(p):
        side.add(sign.offset(-3.0, J) - sign.offset(-4.6, J), "fildisi")
        side.add(plate.offset(-2.0, J) - plate.offset(-3.2, J), "fildisi")
        x_ = sg * -28
        side.add(tx("barlow", "DÖNER", 17.0, x_, D + 119, tr=1.2), "fildisi")
        side.add(tx("barlow", "SOKAK", 10.0, x_, D + 99.5, tr=3.0), "fildisi")
        side.add(label("DÜRÜM · DÖNER" if sg > 0 else "OKUT, SİPARİŞ VER", x_, D + 86.5, 3.4, tr=0.8), "fildisi")
        side.qr(url("doner"), sg * 44, D + 110, 44)
        side.add(label("MASA", 0, D + 50.5, 3.2, tr=0.5), "fildisi")
        side.add(tx("barlow", "7", 10.0, 0, D + 40.5), "fildisi")
    foot, hb = foot_plain(C(36), 14, 14, "gri", depth=D + 6)
    return standard(d, p, foot, hb, "gri yuvarlak ayak Ø72 mm")


def t25_gunbatimi():
    d = Design("25_gunbatimi", "Gün Batımı", "teras restoran", "nfc",
               "Ufukta batan güneş: turuncu gövde, sarı ışınlar, lacivert Fraunces yazı; ayağı lacivert dalga (deniz).",
               masa=12)
    cy = D + 2.0
    disc = C(64, 0, cy) ^ R(-99, cy, 99, 999)
    rays = []
    for k in range(9):
        a = math.radians(10 + 20 * k)
        w = math.radians(4.5)
        rays.append(P([(60 * math.cos(a - w), cy + 60 * math.sin(a - w)), (84 * math.cos(a), cy + 84 * math.sin(a)),
                       (60 * math.cos(a + w), cy + 60 * math.sin(a + w))]))
    sun = soft(U(disc, *rays), 0.8)
    p = Panel(tab(sun, 124), "turuncu", nfc=(42, D + 17))
    for side, sg in both(p):
        side.add((U(*rays) - C(63, 0, cy)).offset(-0.8, J), "sari")
        side.add(ring(59.5, 2.4, 0, cy), "sari")
        side.add(arc_tx("fraunces_k", "GÜN BATIMI", 6.4, 0, cy, 47.8, 90, True, 1.2), "lacivert")
        side.qr(url("gunbat"), 0, D + 25.5, 34, dark="lacivert")
        nx = sg * 42
        side.add(ring(10.5, 1.3, nx, D + 17), "lacivert")
        side.add(phone_waves(nx + 0.5, D + 17, 11.5), "lacivert")
        side.add(label("TERAS" if sg > 0 else "REZERVASYON", -nx + sg * 2, D + 24.5, 3.4, tr=1.0 if sg > 0 else 0.3),
                 "lacivert")
        side.add(label("MASA 12", -nx + sg * 2, D + 15.5, 3.4, tr=0.8), "fildisi")
    foot, hb = foot_wave(176, 46, 14, 2.2, 4, 124, "lacivert", top="fildisi")
    return standard(d, p, foot, hb, "lacivert dalgalı ayak 176 × 46 mm (deniz)")


def t26_liman():
    d = Design("26_liman", "Liman", "cafe & balık", "2qr",
               "Can simidi: kırmızı-fildişi dilimler, lacivert halat çizgileri, ortada QR. Ön menü, arka yorum.",
               masa=3)
    cy = D + 64.0
    disc = C(64, 0, cy)
    p = Panel(tab(disc, 50, D + 2), "fildisi")
    for side, sg in both(p):
        for a0, a1 in ((55, 125), (235, 305), (-20, 20), (160, 200)):
            side.add(sector(37.5, 63.5, a0, a1, 0, cy), "kirmizi")
        for a in (37.5, 142.5, 217.5, 322.5):
            for da in (-4.5, 4.5):
                t_ = math.radians(a + da)
                side.add(ST([(39 * math.cos(t_), cy + 39 * math.sin(t_)), (61 * math.cos(t_), cy + 61 * math.sin(t_))],
                            1.3), "lacivert")
        side.add(ring(63.4, 1.4, 0, cy), "lacivert")
        side.add(ring(38.4, 1.2, 0, cy), "lacivert")
        side.add(arc_tx("fraunces_k", "LİMAN", 7.4, 0, cy, 45.4, 90, True, 2.4), "fildisi")
        side.add(arc_tx("jost", "MENÜ" if sg > 0 else "YORUM", 4.4, 0, cy, 54.4, 270, False, 2.4), "fildisi")
        side.qr(url("liman", "menu" if sg > 0 else "yorum"), 0, cy + 2, 36, dark="lacivert")
        side.add(label("CAFE · BALIK", 0, cy + 25.6, 3.2, tr=0.6), "lacivert")
        side.add(label("MASA 03", 0, cy - 22.6, 3.4, tr=0.8), "lacivert")
    foot, hb = foot_plain(C(38), 12, 50, "lacivert", top="fildisi", top_cs=ring(33, 2.4))
    return standard(d, p, foot, hb, "lacivert yuvarlak ayak Ø76 mm, halat çizgisi")


def t27_rooftop():
    d = Design("27_rooftop", "Rooftop 360", "kokteyl & mutfak", "nfc",
               "İnce uzun kemer: antrasit zemin, ipek altın ince çerçeve ve 360°, Unbounded yazı. NFC ve QR.", masa=21)
    arch = U(R(-40, D - 2, 40, D + 128), C(40, 0, D + 128))
    p = Panel(tab(arch, 70), "siyah", nfc=(0, D + 42))
    vis = arch ^ R(-99, D, 99, 999)
    for side, sg in both(p):
        side.add(vis.offset(-3.2, J) - vis.offset(-4.2, J), "altin")
        side.add(tx("unbounded", "360°", 14.5, 0, D + 141.5), "altin")
        side.add(label("ROOFTOP" if sg > 0 else "MENÜ · REZERVASYON", 0, D + 124.5, 3.8 if sg > 0 else 3.4,
                       tr=3.0 if sg > 0 else 0.6), "fildisi")
        side.add(rule(-14, 14, D + 117, 1.0), "altin")
        side.qr(url("r360"), 0, D + 89, 40, dark="siyah")
        side.add(label("DOKUNUN · OKUTUN", 0, D + 61, 3.4, tr=0.6), "fildisi")
        side.add(ring(11.0, 1.2, 0, D + 42), "altin")
        side.add(phone_waves(0.5, D + 42, 12.0), "fildisi")
        side.add(label("MASA 21", 0, D + 19, 3.6, tr=1.6), "altin")
    foot, hb = foot_plain(RR(92, 26, 6), 10, 70, "altin")
    return standard(d, p, foot, hb, "ipek altın ince kaide 92 × 26 mm")


def t28_bilet():
    d = Design("28_bilet", "Tost Durağı", "tost & kumru", "2qr",
               "Retro bilet: fildişi zemin, turuncu-turkuaz şeritler, Righteous yazı; koparma çizgisi, bilette masa no.",
               masa=15)
    tk = soft(R(-80, D - 2, 80, D + 84), 2.5) - C(7, -80, D + 43) - C(7, 80, D + 43)
    p = Panel(tab(tk, 140), "fildisi")
    for side, sg in both(p):
        x_, sx = sg * -30, sg * 49
        side.add(tk.offset(-2.8, J) - tk.offset(-3.8, J), "turkuaz")
        side.add(U(*[C(0.95, sg * 21, D + y) for y in np.arange(8, 80, 4.4)]), "lacivert")
        side.add(tx("righteous", "TOST DURAĞI", 9.4, x_, D + 61, max_w=84), "lacivert")
        side.add(R(x_ - 43, D + 48.2, x_ + 43, D + 50.8), "turuncu")
        side.add(R(x_ - 43, D + 43.6, x_ + 43, D + 46.2), "turkuaz")
        side.add(label("MASA", x_ - 30, D + 18.5, 3.6, tr=0.8), "turuncu")
        side.add(tx("righteous", "15", 10.5, x_ - 13, D + 18.5), "lacivert")
        side.qr(url("tost", "menu" if sg > 0 else "yorum"), sx, D + 47, 38, dark="lacivert")
        side.add(label("BİLET", sx, D + 74.8, 3.4, tr=1.8), "turkuaz")
        side.add(label("MENÜ" if sg > 0 else "YORUM", sx, D + 16.5, 4.0, tr=2.0), "turuncu")
    p.front.add(label("1986'DAN BERİ · ANTALYA", -30, D + 33, 3.4, tr=0.5), "lacivert")
    p.front.add(label("TOST · KUMRU", -30 + 22, D + 18.5, 3.4, tr=0.4), "turkuaz")
    p.back.add(label("BİZİ DEĞERLENDİRİN", 30, D + 33, 3.4, tr=0.6), "lacivert")
    p.back.add(stars(30 + 22, D + 18.5, 2.0, gap=0.8), "turuncu")
    foot, hb = foot_plain(RR(150, 34, 6), 10, 140, "turkuaz")
    return standard(d, p, foot, hb, "turkuaz ayak 150 × 34 mm")


def t29_pecetelik():
    d = Design("29_pecetelik", "Annemin Mutfağı", "ev yemekleri", "2qr",
               "Peçetelik: iki fildişi panel arasında peçete; kırmızı ekose şerit, Norican el yazısı. Bir panel menü, "
               "öbürü yorum.", masa=2)
    out = RR(112, 116, 10, 0, D + 56)
    clip = out.offset(-EDGE, J)
    checks = U(*[R(-56 + 5.6 * i, D + 92 + 5.5 * j, -56 + 5.6 * (i + 1), D + 92 + 5.5 * (j + 1))
                 for i in range(20) for j in range(4) if (i + j) % 2 == 0]) ^ clip
    gap = 18.0
    p1, p2 = Panel(tab(out, 112), "fildisi"), Panel(tab(out, 112), "fildisi")
    for p, menu in ((p1, True), (p2, False)):
        s = p.front
        s.add(checks, "kirmizi")
        s.add(R(-99, D + 90.2, 99, D + 91.4) ^ clip, "kirmizi")
        s.add(tx("norican", "Annemin Mutfağı", 9.4, 0, D + 77), "kirmizi")
        s.add(label("EV YEMEKLERİ" if menu else "BEĞENDİNİZ Mİ?", 0, D + 64.5, 3.6, tr=1.4 if menu else 0.8),
              "kirmizi")
        s.qr(url("annem", "menu" if menu else "yorum"), 0, D + 40, 34, dark="kirmizi")
        s.add(label(("MENÜ" if menu else "YORUM") + " · MASA 02", 0, D + 12.5, 3.6, tr=0.8), "kirmizi")
    hb = 12.0
    d.put(p1, upright(hb - D, y0=-gap))
    d.put(p2, upright(hb - D, y0=gap, turn=True))
    base = solid(RR(124, 58, 8), hb) - slot(112, hb, y=-gap, thick=T) - slot(112, hb, y=gap, thick=T)
    d.stand.append(("Ayak (kırmızı)", base, "kirmizi"))
    d.props = [("Peçete", box(-50, -gap + 3, hb, 50, gap - 3, hb + 74), "beyaz")]
    d.stand_desc = "kırmızı peçetelik ayağı 124 × 58 mm, iki yuva"
    return d


def t30_kofte():
    d = Design("30_kofte", "Mahalle Köftecisi", "ızgara köfte", "2qr",
               "Tuzluk-biberlik ve kürdanlıklı masa düzenleyici: ortada antrasit panel, Anton yazı, kırmızı masa no.",
               masa=7)
    pan = RR(92, 124, 8, 0, D + 60)
    p = Panel(tab(pan, 92), "siyah")
    for side, sg in both(p):
        side.add(label("MAHALLE", 0, D + 109, 3.8, tr=2.6), "fildisi")
        side.add(tx("anton", "KÖFTECİSİ", 13.0, 0, D + 95, tr=0.6, max_w=78), "fildisi")
        side.add(rule(-20, 20, D + 84, 1.6), "kirmizi")
        side.qr(url("kofte", "menu" if sg > 0 else "yorum"), 0, D + 60, 36)
        side.add(tx("anton", "MASA 07", 7.5, 0, D + 20, tr=1.0), "kirmizi")
    p.front.add(label("MENÜ", 0, D + 34.5, 4.0, tr=2.2), "fildisi")
    p.back.add(stars(0, D + 34.5, 2.4, gap=1.2), "kirmizi")
    hb = 24.0
    org = solid(RR(200, 64, 8), hb) - slot(92, hb)
    for y in (-15, 15):
        org = org - m3.Manifold.cylinder(19, 16.5, 16.5, 96).translate((-74, y, hb - 18))
    org = org - m3.Manifold.cylinder(19, 11, 11, 64).translate((72, 14, hb - 18))
    org = org - solid(RR(40, 20, 4, 72, -14), 13, hb - 12)
    double(d, p, hb - D)
    d.stand.append(("Düzenleyici (siyah)", org, "siyah"))

    def shaker(x, y, col):
        body = m3.Manifold.cylinder(46, 14.5, 13.5, 96).translate((x, y, hb - 17))
        top = m3.Manifold.sphere(13.5, 96).scale((1, 1, 0.55)).translate((x, y, hb + 29))
        return [("Tuzluk/biberlik", body + top, col)]

    sticks = [("Kürdan", m3.Manifold.cylinder(46, 0.9, 0.9, 12).translate((72 + dx, 14 + dy, hb - 17)), "ahsap")
              for dx, dy in ((-4, -3), (-1, 3), (2, -2), (4, 2), (0, 0), (-3, 1), (3, -4))]
    sachets = [("Şeker", box(56 + 6 * k, -22, hb - 11, 59 + 6 * k, -6, hb + 18), "beyaz") for k in range(5)]
    d.props = shaker(-74, -15, "beyaz") + shaker(-74, 15, "kahve") + sticks + sachets
    d.stand_desc = "tuzluk-biberlik, kürdan ve şeker yuvalı düzenleyici 200 × 64 mm"
    return d


# ---------------------------------------------------------------- standart seri (31–45): yuvarlak, dikey, yatay, kare

def corners(x0, y0, x1, y1, L=10.0, w=1.2):
    """Dört köşede L biçimli süs."""
    return U(*[ST([(x + sx * L, y), (x, y), (x, y + sy * L)], w)
               for x, y, sx, sy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1))])


def frame2(vis, a=3.6, w1=1.2, b=5.8, w2=0.9):
    return (vis.offset(-a, J) - vis.offset(-a - w1, J)) + (vis.offset(-b, J) - vis.offset(-b - w2, J))


def frame1(vis, a=3.8, w=1.1):
    return vis.offset(-a, J) - vis.offset(-a - w, J)


def olive_branch(cx, cy, s=1.0):
    stem = ST((A.smooth([(-14, -4), (-4, 1), (6, 2), (15, -1)], n=40) * s + (cx, cy)), 1.2)
    lv = [leaf(cx + x * s, cy + y * s, 8.5 * s, 3.8 * s, a) for x, y, a in ((-9, -1.5, 135), (-3, 1.0, 65),
                                                                            (3, 1.6, 110), (9, 1.2, 50),
                                                                            (-6, -0.5, -140), (6, 1.0, -40))]
    return U(stem, *lv, ellipse(1.8 * s, 2.5 * s, cx + 15.5 * s, cy - 2.5 * s), ellipse(1.8 * s, 2.5 * s, cx - 1 * s,
                                                                                    cy - 2.8 * s))


def pomegranate(cx, cy, r):
    crown = P([(cx - r * 0.42, cy + r * 0.8), (cx - r * 0.36, cy + r * 1.25), (cx - r * 0.14, cy + r * 1.05),
               (cx, cy + r * 1.32), (cx + r * 0.14, cy + r * 1.05), (cx + r * 0.36, cy + r * 1.25),
               (cx + r * 0.42, cy + r * 0.8)])
    return U(C(r, cx, cy), crown)


def crescent(cx, cy, r):
    return C(r, cx, cy) - C(r * 0.8, cx + r * 0.42, cy + r * 0.18)


def thyme(cx, cy, s=1.0):
    stem = ST([(cx, cy - 13 * s), (cx, cy + 13 * s)], 1.2)
    lv = []
    for k, y in enumerate(np.linspace(-9, 11, 6)):
        L = (6.5 - abs(y) * 0.18) * s
        lv.append(leaf(cx, cy + y * s, L, 3.0 * s, 35 + 4 * k))
        lv.append(leaf(cx, cy + y * s, L, 3.0 * s, 145 - 4 * k))
    return U(stem, *lv)


def waves(x0, x1, y, n=3, amp=1.6, wl=11.0, gap=5.0, w=1.2):
    xs = np.linspace(x0, x1, 80)
    return U(*[ST(np.c_[xs, y - k * gap + amp * np.sin(2 * np.pi * (xs - x0) / wl)], w) for k in range(n)])


def sun_horizon(cx, cy, r):
    sun = (C(r, cx, cy) ^ R(cx - r, cy + 1.6, cx + r, cy + r))
    return U(sun, rule(cx - r * 1.6, cx + r * 1.6, cy, 1.4), rule(cx - r * 1.1, cx + r * 1.1, cy - 3.2, 1.2),
             rule(cx - r * 0.6, cx + r * 0.6, cy - 6.2, 1.2))


def wine_glass(cx, cy, s=1.0):
    bowl = ellipse(6.5 * s, 7.5 * s, cx, cy + 6 * s) ^ R(cx - 9 * s, cy - 2 * s, cx + 9 * s, cy + 9 * s)
    bowl = bowl - (ellipse(5.2 * s, 6.2 * s, cx, cy + 6 * s) ^ R(cx - 9 * s, cy + 1.5 * s, cx + 9 * s, cy + 9 * s))
    return U(bowl, R(cx - 0.7 * s, cy - 9 * s, cx + 0.7 * s, cy - 1 * s), RR(10 * s, 1.4 * s, 0.6 * s, cx, cy - 9.4 * s))


def salt_pepper(cx, cy, r=6.0):
    a = C(r, cx - r - 1.5, cy) - U(*[C(0.9, cx - r - 1.5 + dx, cy + dy) for dx, dy in ((-2, 1), (2, 1), (0, -2))])
    b = ring(r, 1.3, cx + r + 1.5, cy) + U(*[C(0.9, cx + r + 1.5 + dx, cy + dy) for dx, dy in ((-2, 1), (2, 1),
                                                                                           (0, -2))])
    return a + b


def macaron(cx, cy, s=1.0):
    return U(RR(18 * s, 5 * s, 2.5 * s, cx, cy + 4 * s), RR(16 * s, 2.0 * s, 1.0 * s, cx, cy),
             RR(18 * s, 5 * s, 2.5 * s, cx, cy - 4 * s))


def round_panel(r):
    cy = D + r - 1.0
    return C(r, 0, cy), cy


def t31_mira():
    d = Design("31_mira", "Mira", "modern bistro", "2qr",
               "Yuvarlak, antrasit zemin, ipek altın çift halka ve monogram; Bodoni harf aralıklı isim. Ön menü, arka "
               "yorum.", masa=4)
    disc, cy = round_panel(56)
    p = Panel(tab(disc, 50, D + 2), "siyah")
    for side, sg in both(p):
        side.add(ring(53, 1.2, 0, cy) + ring(50.6, 0.8, 0, cy), "altin")
        side.add(ring(8.6, 1.1, 0, cy + 37) + tx("bodoni", "M", 8.0, 0, cy + 37), "altin")
        side.add(tx("bodoni", "MİRA", 7.4, 0, cy + 22, tr=3.4), "fildisi")
        side.qr(url("mira", "menu" if sg > 0 else "yorum"), 0, cy - 6, 32, dark="siyah")
    p.front.add(label("MENÜ", 0, cy - 28.5, 3.8, tr=2.4), "altin")
    p.front.add(label("MASA 04", 0, cy - 37.5, 3.4, tr=1.4), "fildisi")
    p.back.add(stars(0, cy - 28.5, 2.2, gap=1.2), "altin")
    p.back.add(label("DEĞERLENDİRİN", 0, cy - 37.5, 3.4, tr=0.8), "fildisi")
    foot, hb = foot_plain(RR(84, 26, 6), 10, 50, "altin")
    return standard(d, p, foot, hb, "ipek altın ince kaide 84 × 26 mm")


def t32_saffron():
    d = Design("32_saffron", "Saffron", "fine dining", "2qr",
               "Dikey menü kartı: fildişi zemin, siyah Bodoni, ipek altın köşe süsleri ve çizgi. Ön menü, arka yorum.",
               masa=2)
    pan = RR(96, 146, 5, 0, D + 71)
    p = Panel(tab(pan, 96), "fildisi")
    for side, sg in both(p):
        side.add(corners(-41.5, D + 5.5, 41.5, D + 135.5, 11, 1.2), "altin")
        side.add(tx("bodoni", "SAFFRON", 9.4, 0, D + 117, tr=2.4, max_w=78), "siyah")
        side.add(rule(-14, 14, D + 106.5, 1.0), "altin")
        side.add(label("RESTORAN · ANTALYA", 0, D + 98.5, 3.4, tr=1.0), "siyah")
        side.qr(url("saffron", "menu" if sg > 0 else "yorum"), 0, D + 66, 40, dark="siyah")
    p.front.add(label("MENÜ", 0, D + 35, 4.0, tr=2.6), "altin")
    p.front.add(label("MASA 02", 0, D + 25, 3.4, tr=1.4), "siyah")
    p.back.add(stars(0, D + 35, 2.3, gap=1.3), "altin")
    p.back.add(label("BİZİ DEĞERLENDİRİN", 0, D + 25, 3.4, tr=0.6), "siyah")
    p.back.add(label("MASA 02", 0, D + 16, 3.4, tr=1.4), "siyah")
    foot, hb = foot_plain(RR(108, 30, 5), 10, 96, "siyah")
    return standard(d, p, foot, hb, "siyah ince kaide 108 × 30 mm")


def t33_olea():
    d = Design("33_olea", "Olea", "Akdeniz mutfağı", "1qr",
               "Yatay kart: adaçayı yeşili zemin, fildişi çerçeve, zeytin dalı ve Fraunces; sağda QR. İki yüz aynı sayfa.",
               masa=6)
    pan = RR(152, 100, 6, 0, D + 48)
    p = Panel(tab(pan, 140), "adacayi")
    vis = pan ^ R(-99, D, 99, 999)
    for side, sg in both(p):
        x_ = sg * -32
        side.add(frame1(vis, 4.0, 1.1), "fildisi")
        side.add(olive_branch(x_, D + 80, 1.05), "fildisi")
        side.add(tx("fraunces_k", "Olea", 15.0, x_, D + 58), "fildisi")
        side.add(label("AKDENİZ MUTFAĞI", x_, D + 41, 3.4, tr=1.0), "koyu_yesil")
        side.add(label("MASA 06", x_, D + 20, 3.4, tr=1.4), "fildisi")
        side.qr(url("olea"), sg * 40, D + 48, 44, dark="koyu_yesil")
    foot, hb = foot_plain(RR(150, 36, 10), 10, 140, "ahsap")
    return standard(d, p, foot, hb, "ahşap ayak 150 × 36 mm")


def t34_nar():
    d = Design("34_nar", "Nar", "Anadolu mutfağı", "2qr",
               "Yuvarlak, bordo zemin, pudra pembe nar simgesi ve iri Fraunces; ipek altın halka; mermer ayak.", masa=9)
    disc, cy = round_panel(55)
    p = Panel(tab(disc, 50, D + 2), "bordo")
    for side, sg in both(p):
        side.add(ring(52, 1.3, 0, cy), "altin")
        side.add(pomegranate(0, cy + 33, 7.5), "pudra")
        side.add(tx("fraunces_k", "NAR", 13.0, 0, cy + 15, tr=3.0), "pudra")
        side.qr(url("nar", "menu" if sg > 0 else "yorum"), 0, cy - 17, 30)
        side.add(label("MASA 09", 0, cy - 40.5, 3.4, tr=1.4), "pudra")
    p.front.add(label("MENÜ", 0, cy + 3.2, 3.6, tr=2.4), "altin")
    p.back.add(stars(0, cy + 3.2, 2.0, gap=1.1), "altin")
    foot, hb = foot_plain(C(34), 12, 50, "mermer")
    return standard(d, p, foot, hb, "mermer yuvarlak ayak Ø68 mm")


def t35_atolye():
    d = Design("35_atolye", "Atölye 7", "et & ızgara", "nfc",
               "Dikey, antrasit zemin, iri bakır 7, Anton yazı; NFC ve QR. Beton gri kaide.", masa=7)
    pan = RR(92, 150, 4, 0, D + 73)
    p = Panel(tab(pan, 92), "siyah", nfc=(0, D + 25))
    vis = pan ^ R(-99, D, 99, 999)
    for side, sg in both(p):
        side.add(frame1(vis, 3.4, 1.0), "bakir")
        side.add(tx("anton", "ATÖLYE", 12.0, 0, D + 131, tr=2.4), "fildisi")
        side.add(tx("bigsh", "7", 26.0, 0, D + 106), "bakir")
        side.add(label("ET · IZGARA · ŞARAP", 0, D + 87.5, 3.4, tr=0.8), "fildisi")
        side.qr(url("atolye7"), 0, D + 60, 38)
        side.add(ring(10.0, 1.2, 0, D + 25), "bakir")
        side.add(phone_waves(0.5, D + 25, 11.0), "fildisi")
        side.add(label("MASA 07" if sg > 0 else "DOKUN · OKUT", 0, D + 9.5, 3.4, tr=1.2 if sg > 0 else 0.6), "bakir")
    foot, hb = foot_plain(RR(104, 40, 3), 14, 92, "gri")
    return standard(d, p, foot, hb, "beton gri kaide 104 × 40 mm")


def t36_beyaz():
    d = Design("36_beyaz", "Beyaz Masa", "modern mutfak", "1qr",
               "Yatay, yalın: beyaz zemin, siyah Syne küçük harf, ince çizgi ve iri masa numarası; sağda QR.", masa=12)
    pan = RR(150, 96, 3, 0, D + 46)
    p = Panel(tab(pan, 140), "beyaz")
    for side, sg in both(p):
        x0 = -66 if sg > 0 else 14
        side.add(tx("syne", "beyaz masa", 8.0, x0, D + 76, align="l", max_w=58), "siyah")
        side.add(rule(x0, x0 + 52, D + 64.5, 1.0), "siyah")
        side.add(label("MODERN MUTFAK" if sg > 0 else "MENÜ · YORUM · SİPARİŞ", x0, D + 56, 3.4,
                       tr=1.0 if sg > 0 else 0.4, align="l", max_w=56), "siyah")
        side.add(label("MASA", x0, D + 36, 3.4, tr=1.4, align="l"), "siyah")
        side.add(tx("syne", "12", 18.0, x0, D + 20, align="l"), "siyah")
        side.qr(url("beyazmasa"), sg * 40, D + 46, 46, dark="siyah")
    foot, hb = foot_plain(RR(150, 28, 4), 10, 140, "siyah")
    return standard(d, p, foot, hb, "siyah ince kaide 150 × 28 mm")


def t37_lune():
    d = Design("37_lune", "Lune", "cafe · bistro", "nfc",
               "Yuvarlak, lacivert zemin, ipek altın hilal ve yıldızlar, Playfair italik; QR ve NFC.", masa=5)
    disc, cy = round_panel(55)
    p = Panel(tab(disc, 50, D + 2), "lacivert", nfc=(24, cy - 17.5))
    for side, sg in both(p):
        side.add(ring(52, 1.2, 0, cy), "altin")
        side.add(crescent(-2, cy + 33, 8.5) + star(9, cy + 40, 2.2) + star(13, cy + 30, 1.6) + star(-15, cy + 39, 1.4),
                 "altin")
        side.add(tx("playfair_ki", "Lune", 12.0, 0, cy + 15), "fildisi")
        side.add(label("CAFE · BİSTRO", 0, cy + 3, 3.2, tr=1.4), "altin")
        side.qr(url("lune"), sg * -8, cy - 17.5, 31)
        side.add(ring(8.6, 1.1, sg * 24, cy - 17.5), "altin")
        side.add(phone_waves(sg * 24 + 0.4, cy - 17.5, 9.5), "fildisi")
        side.add(label("MASA 05", 0, cy - 40.5, 3.4, tr=1.4), "fildisi")
    foot, hb = foot_plain(RR(80, 24, 6), 10, 50, "altin")
    return standard(d, p, foot, hb, "ipek altın ince kaide 80 × 24 mm")


def t38_kekik():
    d = Design("38_kekik", "Kekik", "ev yemekleri", "2qr",
               "Dikey, zeytin yeşili zemin, fildişi kekik dalı, çerçeve ve Fraunces; ahşap ayak. Ön menü, arka yorum.",
               masa=3)
    pan = RR(96, 140, 12, 0, D + 68)
    p = Panel(tab(pan, 96), "zeytin")
    vis = pan ^ R(-99, D, 99, 999)
    for side, sg in both(p):
        side.add(frame1(vis, 4.0, 1.1), "fildisi")
        side.add(thyme(0, D + 117, 0.9), "fildisi")
        side.add(tx("fraunces_k", "Kekik", 13.0, 0, D + 96), "fildisi")
        side.add(label("EV YEMEKLERİ", 0, D + 84, 3.6, tr=1.6), "fildisi")
        side.qr(url("kekik", "menu" if sg > 0 else "yorum"), 0, D + 58, 36)
        side.add(label("MASA 03", 0, D + 19, 3.4, tr=1.4), "fildisi")
    p.front.add(label("MENÜ", 0, D + 30, 4.0, tr=2.4), "fildisi")
    p.back.add(stars(0, D + 30, 2.3, gap=1.2), "fildisi")
    foot, hb = foot_plain(RR(104, 34, 8), 12, 96, "ahsap")
    return standard(d, p, foot, hb, "ahşap ayak 104 × 34 mm")


def t39_coral():
    d = Design("39_coral", "Coral", "deniz ürünleri", "2qr",
               "Yatay, mercan zemin, lacivert Archivo geniş yazı ve dalga çizgileri; sağda QR. Ön menü, arka yorum.",
               masa=8)
    pan = RR(150, 100, 6, 0, D + 48)
    p = Panel(tab(pan, 140), "mercan")
    for side, sg in both(p):
        x_ = sg * -32
        side.add(tx("archivo_x", "CORAL", 11.0, x_, D + 70, tr=1.6), "lacivert")
        side.add(label("DENİZ ÜRÜNLERİ", x_, D + 57, 3.4, tr=1.0), "lacivert")
        side.add(waves(x_ - 26, x_ + 26, D + 41, 3, 1.5, 13.0, 5.0, 1.2), "fildisi")
        side.add(label("MASA 08", x_, D + 17, 3.4, tr=1.4), "lacivert")
        side.qr(url("coral", "menu" if sg > 0 else "yorum"), sg * 42, D + 48, 42, dark="lacivert")
    foot, hb = foot_plain(RR(150, 34, 6), 10, 140, "lacivert")
    return standard(d, p, foot, hb, "lacivert ayak 150 × 34 mm")


def t40_mavikapi():
    d = Design("40_mavikapi", "Mavi Kapı", "Ege mutfağı", "1qr",
               "Dikey, kobalt mavi zemin, beyaz kapı kemeri çizgisi ve Cinzel; mermer kaide. İki yüz aynı sayfa.",
               masa=11)
    pan = RR(96, 146, 5, 0, D + 71)
    p = Panel(tab(pan, 96), "kobalt")
    door = U(R(-36, D + 4, 36, D + 104), C(36, 0, D + 104))
    door_line = door - door.offset(-1.4, J)
    for side, sg in both(p):
        side.add(door_line, "beyaz")
        side.add(tx("cinzel", "MAVİ KAPI", 7.0, 0, D + 114, tr=1.4, max_w=58), "beyaz")
        side.add(label("EGE MUTFAĞI", 0, D + 102.5, 3.4, tr=1.6), "beyaz")
        side.qr(url("mavikapi"), 0, D + 70, 40, light="beyaz")
        side.add(label("MENÜ · YORUM" if sg > 0 else "OKUTUN", 0, D + 36, 3.6, tr=1.0), "beyaz")
        side.add(label("MASA 11", 0, D + 26, 3.4, tr=1.4), "beyaz")
    foot, hb = foot_plain(RR(108, 36, 4), 12, 96, "mermer")
    return standard(d, p, foot, hb, "mermer kaide 108 × 36 mm")


def t41_tuzbiber():
    d = Design("41_tuzbiber", "Tuz & Biber", "ızgara evi", "2qr",
               "Kare, siyah zemin, beyaz tuz-biber simgesi ve Anton yazı; ahşap ayak. Ön menü, arka yorum.", masa=1)
    pan = RR(112, 112, 8, 0, D + 54)
    p = Panel(tab(pan, 112), "siyah")
    vis = pan ^ R(-99, D, 99, 999)
    for side, sg in both(p):
        side.add(frame1(vis, 3.6, 1.0), "beyaz")
        side.add(salt_pepper(0, D + 95, 5.6), "beyaz")
        side.add(tx("anton", "TUZ & BİBER", 11.0, 0, D + 79, tr=1.2), "beyaz")
        side.add(label("IZGARA EVİ", 0, D + 68.5, 3.4, tr=2.0), "beyaz")
        side.qr(url("tuzbiber", "menu" if sg > 0 else "yorum"), 0, D + 42, 34)
    p.front.add(label("MENÜ · MASA 01", 0, D + 13, 3.4, tr=1.0), "beyaz")
    p.back.add(stars(0, D + 19.5, 2.0, gap=1.0), "beyaz")
    p.back.add(label("DEĞERLENDİRİN", 0, D + 12, 3.4, tr=0.6), "beyaz")
    foot, hb = foot_plain(RR(120, 34, 6), 12, 112, "ahsap")
    return standard(d, p, foot, hb, "ahşap ayak 120 × 34 mm")


def t42_ada():
    d = Design("42_ada", "Ada", "bistro · plaj", "1qr",
               "Yuvarlak, kum beji zemin, kahverengi güneş-ufuk simgesi ve harf aralıklı Fraunces; kahverengi ayak.",
               masa=14)
    disc, cy = round_panel(55)
    p = Panel(tab(disc, 50, D + 2), "kum")
    for side, sg in both(p):
        side.add(ring(52, 1.2, 0, cy), "kahve")
        side.add(sun_horizon(0, cy + 33, 8.0), "kahve")
        side.add(tx("fraunces_k", "ADA", 12.0, 0, cy + 15, tr=4.0), "kahve")
        side.add(label("BİSTRO · PLAJ", 0, cy + 3, 3.2, tr=1.6), "kahve")
        side.qr(url("ada"), 0, cy - 17.5, 31, dark="kahve")
        side.add(label("MASA 14", 0, cy - 39.5, 3.4, tr=1.4), "kahve")
    foot, hb = foot_plain(C(32), 12, 50, "kahve")
    return standard(d, p, foot, hb, "kahverengi yuvarlak ayak Ø64 mm")


def t43_bakir():
    d = Design("43_bakir", "Bakır", "şarap & meze", "2qr",
               "Yatay, antrasit zemin, ipek bakır çift çerçeve ve kadeh, Bodoni; bakır ince kaide. Ön menü, arka yorum.",
               masa=6)
    pan = RR(150, 98, 4, 0, D + 47)
    p = Panel(tab(pan, 140), "siyah")
    vis = pan ^ R(-99, D, 99, 999)
    for side, sg in both(p):
        x_ = sg * -32
        side.add(frame2(vis, 3.4, 1.1, 5.4, 0.8), "bakir")
        side.add(wine_glass(x_, D + 77, 0.95), "bakir")
        side.add(tx("bodoni", "BAKIR", 11.0, x_, D + 56, tr=3.0), "fildisi")
        side.add(label("ŞARAP · MEZE", x_, D + 44, 3.4, tr=1.6), "bakir")
        side.add(label("MASA 06", x_, D + 21, 3.4, tr=1.4), "fildisi")
        side.qr(url("bakir", "menu" if sg > 0 else "yorum"), sg * 40, D + 47, 42)
    foot, hb = foot_plain(RR(150, 24, 4), 9, 140, "bakir")
    return standard(d, p, foot, hb, "ipek bakır ince kaide 150 × 24 mm")


def t44_yesilev():
    d = Design("44_yesilev", "Yeşil Ev", "bahçe cafe", "nfc",
               "Dikey, koyu yeşil zemin, köşelerde açık yeşil yapraklar, Fraunces italik; NFC ve QR; terrakota ayak.",
               masa=10)
    pan = RR(94, 142, 14, 0, D + 69)
    p = Panel(tab(pan, 94), "koyu_yesil", nfc=(0, D + 33))
    leaves = U(leaf(40, D + 134, 16, 7, 205), leaf(40, D + 134, 13, 6, 240), leaf(40, D + 134, 11, 5, 180),
               leaf(-40, D + 6, 16, 7, 25), leaf(-40, D + 6, 13, 6, 60), leaf(-40, D + 6, 11, 5, 0))
    for side, sg in both(p):
        side.add(mirror_fn(sg)(leaves) ^ pan.offset(-2.0, J), "yesil")
        side.add(tx("fraunces_i", "Yeşil Ev", 11.0, 0, D + 110), "fildisi")
        side.add(label("BAHÇE CAFE", 0, D + 98, 3.4, tr=2.0), "yesil")
        side.qr(url("yesilev"), 0, D + 70, 36)
        side.add(ring(10.0, 1.2, 0, D + 33), "yesil")
        side.add(phone_waves(0.5, D + 33, 11.0), "fildisi")
        side.add(label("MASA 10" if sg > 0 else "DOKUN · OKUT", 0, D + 15, 3.4, tr=1.2 if sg > 0 else 0.6), "fildisi")
    foot, hb = foot_plain(RR(100, 36, 8), 12, 94, "terrakota")
    return standard(d, p, foot, hb, "terrakota ayak 100 × 36 mm")


def t45_seker():
    d = Design("45_seker", "Şeker", "patiseri", "2qr",
               "Yuvarlak, pudra pembe zemin, fildişi makaron simgesi, kahverengi Norican yazı; mermer ayak.", masa=2)
    disc, cy = round_panel(55)
    p = Panel(tab(disc, 50, D + 2), "pudra")
    for side, sg in both(p):
        side.add(ring(52, 1.3, 0, cy), "fildisi")
        side.add(macaron(0, cy + 34, 0.9), "fildisi")
        side.add(tx("norican", "Şeker", 12.0, 0, cy + 15), "kahve")
        side.qr(url("seker", "menu" if sg > 0 else "yorum"), 0, cy - 18, 31, dark="kahve")
        side.add(label("MASA 02", 0, cy - 39.5, 3.4, tr=1.4), "kahve")
    p.front.add(label("PATİSERİ", 0, cy + 2.4, 3.2, tr=2.2), "kahve")
    p.back.add(stars(0, cy + 2.4, 2.0, gap=1.0), "kahve")
    foot, hb = foot_plain(C(32), 12, 50, "mermer")
    return standard(d, p, foot, hb, "mermer yuvarlak ayak Ø64 mm")


# ---------------------------------------------------------------- görüntü: stüdyo ışığı ve masa gölgesi

KEY = np.array([0.42, 0.58, 0.70]) / np.linalg.norm([0.42, 0.58, 0.70])
FILL = np.array([-0.75, 0.15, 0.64]) / np.linalg.norm([-0.75, 0.15, 0.64])
HALF = (KEY + [0, 0, 1]) / np.linalg.norm(KEY + [0, 0, 1])
RAYS = np.array([0.30, -0.70, -0.65]) / np.linalg.norm([0.30, -0.70, -0.65])   # kameraya göre ışık ışınları


def render_pro(parts, size, R, margin=0.05, ss=3, shadow=True):
    """z-tamponlu çizim: ana ışık + dolgu ışığı, ipek filamentte parlama, masaya düşen yumuşak gölge.
    parts: [(V, T, renk adı)]. Şeffaf arka planlı RGBA (gölge yarı saydam)."""
    W = size * ss
    Ps = [(V @ R.T, T, col) for V, T, col in parts]
    Lw = R.T @ RAYS
    if Lw[2] > -0.2:
        Lw = Lw + [0, 0, -0.2 - Lw[2]]
    sh = []
    for V, T, _ in parts:
        Vs = V - np.outer(V[:, 2] / Lw[2], Lw)
        Vs[:, 2] = 0.0
        Vc = np.c_[V[:, :2], np.zeros(len(V))]
        sh.append(((Vs @ R.T)[:, :2], (Vc @ R.T)[:, :2], T))
    pts = np.vstack([p[:, :2] for p, _, _ in Ps] + ([s for s, _, _ in sh] if shadow else []))
    lo, hi = pts.min(0), pts.max(0)
    scale = (1 - 2 * margin) * W / (hi - lo).max()
    off = W / 2 - scale * (lo + hi) / 2

    def px(P2):
        return np.c_[P2[:, 0] * scale + off[0], W - (P2[:, 1] * scale + off[1])]

    zbuf = np.full((W, W), -np.inf)
    img = np.zeros((W, W, 3))
    for Pv, T, col in Ps:
        S = np.c_[px(Pv[:, :2]), Pv[:, 2]]
        tri = Pv[T]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        vis = n[:, 2] > 1e-3
        T, n = T[vis], n[vis]
        shade = 0.44 + 0.50 * np.clip(n @ KEY, 0, 1) + 0.12 * np.clip(n @ FILL, 0, 1)
        spec = np.clip(n @ HALF, 0, 1) ** 28 * (0.5 if col in METAL else 0.08)
        base = np.asarray(COL[col]) / 255.0
        cols = np.clip(base[None, :] * shade[:, None] + spec[:, None], 0, 1)
        for (a, b, c), cc in zip(S[T], cols):
            xmin, xmax = int(max(min(a[0], b[0], c[0]), 0)), int(min(max(a[0], b[0], c[0]) + 1, W))
            ymin, ymax = int(max(min(a[1], b[1], c[1]), 0)), int(min(max(a[1], b[1], c[1]) + 1, W))
            if xmin >= xmax or ymin >= ymax:
                continue
            den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(den) < 1e-12:
                continue
            gx, gy = np.meshgrid(np.arange(xmin, xmax) + 0.5, np.arange(ymin, ymax) + 0.5)
            w0 = ((b[1] - c[1]) * (gx - c[0]) + (c[0] - b[0]) * (gy - c[1])) / den
            w1 = ((c[1] - a[1]) * (gx - c[0]) + (a[0] - c[0]) * (gy - c[1])) / den
            w2 = 1 - w0 - w1
            inside = (w0 >= -1e-9) & (w1 >= -1e-9) & (w2 >= -1e-9)
            if not inside.any():
                continue
            z = w0 * a[2] + w1 * b[2] + w2 * c[2]
            zb = zbuf[ymin:ymax, xmin:xmax]
            upd = inside & (z > zb)
            zb[upd] = z[upd]
            img[ymin:ymax, xmin:xmax][upd] = cc
    obj_a = np.isfinite(zbuf).astype(float)
    sh_a = np.zeros((W, W))
    if shadow:
        soft_m, cont_m = Image.new("L", (W, W), 0), Image.new("L", (W, W), 0)
        ds, dc = ImageDraw.Draw(soft_m), ImageDraw.Draw(cont_m)
        for S2, C2, T in sh:
            p1, p2 = px(S2), px(C2)
            for t in T:
                ds.polygon([tuple(p1[i]) for i in t], fill=255)
                dc.polygon([tuple(p2[i]) for i in t], fill=255)
        soft_m = soft_m.filter(ImageFilter.GaussianBlur(W * 0.014))
        cont_m = cont_m.filter(ImageFilter.GaussianBlur(W * 0.004))
        sh_a = np.clip(0.30 * np.asarray(soft_m, float) / 255 + 0.34 * np.asarray(cont_m, float) / 255, 0, 0.55)
    shc = np.array([34, 26, 20]) / 255.0
    a = obj_a + sh_a * (1 - obj_a)
    rgb_p = img * obj_a[..., None] + shc * (sh_a * (1 - obj_a))[..., None]
    a_s = a.reshape(size, ss, size, ss).mean((1, 3))
    rgb_s = rgb_p.reshape(size, ss, size, ss, 3).mean((1, 3))
    rgb = np.where(a_s[..., None] > 0, rgb_s / np.maximum(a_s[..., None], 1e-9), 0)
    return Image.fromarray((np.dstack([rgb, a_s]) * 255).round().astype(np.uint8), "RGBA")


def mesh(parts):
    return [(*A.mesh_arrays(m), c) for _, m, c in parts]


def studio(w, h, top=(248, 246, 242), bottom=(228, 223, 215)):
    """Stüdyo fonu: yukarıdan aşağı sıcak gri geçiş, ortası hafif aydınlık."""
    y = np.linspace(0, 1, h)[:, None]
    x = np.linspace(-1, 1, w)[None, :]
    t = np.clip(y ** 1.4, 0, 1)
    base = np.array(top)[None, None, :] * (1 - t[..., None]) + np.array(bottom)[None, None, :] * t[..., None]
    glow = np.exp(-((x / 0.9) ** 2 + ((y - 0.45) / 0.6) ** 2))[..., None] * 8
    return Image.fromarray(np.clip(base + glow, 0, 255).astype(np.uint8), "RGB")


def raster_face(outline, regs, body, ppm=10.0, pad=6.0, bg=(150, 152, 158)):
    """Yüzün düz görünüşü (renk bölgeleriyle)."""
    x0, y0, x1, y1 = outline.bounds()
    x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    W, H = int((x1 - x0) * ppm), int((y1 - y0) * ppm)

    def mask(cs):
        acc = np.zeros((H, W), bool)
        for poly in cs.to_polygons():
            im = Image.new("1", (W, H), 0)
            ImageDraw.Draw(im).polygon([((u - x0) * ppm, (y1 - v) * ppm) for u, v in poly], fill=1)
            acc ^= np.array(im)
        return acc

    img = np.zeros((H, W, 3), np.uint8)
    img[:] = bg
    img[mask(outline)] = COL[body]
    for col, cs in regs.items():
        img[mask(cs)] = COL[col]
    return Image.fromarray(img)


def face_checks(p):
    """Plakanın yüzü: [([(düz okundu, benzetimde okundu, sürüm, kare)], ince alan mm², üstten görüntü)]."""
    regs, outline = p.faces()[0], p.outline
    vis = outline ^ R(-999, p.vis_y, 999, 999)
    im = raster_face(vis, {c: cs ^ vis for c, cs in regs.items()}, p.body, ppm=12.0)
    g = im.convert("L")
    got = Q.decode(g)
    ok = []
    for e, module, _ in p.front.qrs:
        sim = Q.simulate(g, 12.0, module, **dict(Q.SIM_CASES)["hepsi birden"])
        ok.append((e.content in got, e.content in Q.decode(sim), e.qr.version, module))
    thin = 0.0
    parts = list(regs.values()) + [outline - A.union(*regs.values())] if regs else []
    for cs in parts:
        th = cs - cs.offset(-MIN_FEAT / 2, J).offset(MIN_FEAT / 2, J)
        thin += sum(q.area() for q in th.decompose() if q.area() > 0.4)
    return [(ok, thin, im)]


def size_mm(d):
    parts = d.scene(props=False)
    b = m3.Manifold.batch_boolean([m for _, m, _ in parts], m3.OpType.Add).bounding_box()
    return b[3] - b[0], b[4] - b[1], b[5] - b[2]


def font_ui(n, w="semi"):
    f = {"semi": "Jost-SemiBold.ttf", "bold": "Jost-Bold.ttf", "serif": "Fraunces-SemiBold.ttf",
         "serif_k": "Fraunces-Black.ttf", "serif_i": "Fraunces-SemiBoldItalic.ttf"}[w]
    return ImageFont.truetype(os.path.join(A.FONT_DIR, f), n)


VIEWS = {"on": rotation(-26, -79), "arka": rotation(154, -79)}


def views(d, size=1000):
    """Blender fotoğrafları (restoran_masalik_foto.py) varsa onlar, yoksa hızlı çizim."""
    f = os.path.join(OUT_DIR, "foto", d.key + "_{}.png")
    if all(os.path.exists(f.format(v)) for v in VIEWS):
        return {v: Image.open(f.format(v)).convert("RGB") for v in VIEWS}
    parts = mesh(d.scene())
    return {k: render_pro(parts, size, R_) for k, R_ in VIEWS.items()}


def sheet(d, i, faces, imgs, info):
    W, H = 1800, 880
    canvas = Image.new("RGB", (W, H), (244, 242, 238))
    dr = ImageDraw.Draw(canvas)
    dr.text((34, 20), f"{i:02d}  {d.name}", fill=(24, 24, 26), font=font_ui(40, "serif_k"))
    dr.text((34, 76), f"{d.sub} · {d.desc}", fill=(90, 90, 96), font=font_ui(21))
    dr.text((34, 108), info, fill=(30, 110, 60) if "KONTROL" not in info else (190, 30, 36), font=font_ui(19))
    boxes = [(34, 150, 434, 860, "Ön yüz"), (450, 150, 850, 860, "Arka yüz"), (866, 150, 1316, 860, "Önden"),
             (1332, 150, 1782, 860, "Arkadan")]
    for (x0, y0, x1, y1, lab), im in zip(boxes, [faces[0], faces[1], imgs["on"], imgs["arka"]]):
        bg = studio(x1 - x0, y1 - y0)
        if im.mode == "RGB":
            fit = im.copy()
            fit.thumbnail((x1 - x0 - 40, y1 - y0 - 80), Image.LANCZOS)
            bg.paste(fit, ((x1 - x0 - fit.width) // 2, 50 + (y1 - y0 - 50 - fit.height) // 2))
        else:
            fit = A.fit_into(im, x1 - x0 - 30, y1 - y0 - 70)
            bg.paste(fit, ((x1 - x0 - fit.width) // 2, 50 + (y1 - y0 - 50 - fit.height) // 2), fit)
        mask = Image.new("L", bg.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, bg.width - 1, bg.height - 1), 22, fill=255)
        canvas.paste(bg, (x0, y0), mask)
        dr.text((x0 + 18, y0 + 14), lab, fill=(70, 70, 76), font=font_ui(20, "bold"))
    canvas.save(os.path.join(OUT_DIR, d.key + ".png"))


def work(i):
    d = DESIGNS[i - 1]()
    checks = [face_checks(p) for p, _ in d.panels]
    rows = [r for pc in checks for ok, _, _ in pc for r in ok]
    qr_ok = all(a and b for a, b, _, _ in rows)
    thin = max(t for pc in checks for _, t, _ in pc)
    w, dep, h = size_mm(d)
    faces = [pc[0][2] for pc in checks][:2]
    imgs = views(d)
    cols = sorted(d.colours(), key=list(COL).index)
    info = (f"{w / 10:.1f} × {h / 10:.1f} cm (en × boy, ayakla) · {KIND[d.kind]} · {len(rows)} QR "
            f"{'okundu, benzetimde de' if qr_ok else 'KONTROL'} · en küçük QR karesi {min(m for *_, m in rows):.2f} mm · "
            f"0,6 mm'den ince dolgu {thin:.1f} mm² · {', '.join(COL_NAME[c] for c in cols)}")
    sheet(d, i, faces, imgs, info)
    return dict(i=i, key=d.key, name=d.name, sub=d.sub, kind=d.kind, desc=d.desc, size=(w, dep, h), cols=cols,
                masa=d.masa, ok=qr_ok, thin=thin, on=imgs["on"], arka=imgs["arka"], stand=d.stand_desc,
                font=NAME_FONT.get(d.key[3:], "fraunces"), line=f"{d.key:16s} {info}")


DESIGNS = [t01_kemer, t02_balik, t03_kurek, t04_garaj, t05_zeytin, t06_kahve, t07_bistro, t08_ates, t09_limon,
           t10_sushi, t11_pide, t12_dondurma, t13_cay, t14_kasap, t15_gozleme, t16_sorf, t17_pasta, t18_tabak,
           t19_vegan, t20_tahta, t21_baklava, t22_kaktus, t23_wok, t24_tabela, t25_gunbatimi, t26_liman, t27_rooftop,
           t28_bilet, t29_pecetelik, t30_kofte, t31_mira, t32_saffron, t33_olea, t34_nar, t35_atolye, t36_beyaz,
           t37_lune, t38_kekik, t39_coral, t40_mavikapi, t41_tuzbiber, t42_ada, t43_bakir, t44_yesilev, t45_seker]
NAME_FONT = {"kemer": "cinzel", "balik": "fraunces_i", "kurek": "playfair_k", "garaj": "anton", "zeytin": "fraunces",
             "kahve": "fraunces_ki", "bistro": "playfair_ki", "ates": "bigsh", "limon": "fraunces_k", "sushi": "syne",
             "pide": "fraunces_k", "dondurma": "fraunces_ki", "cay": "playfair_k", "kasap": "bodoni",
             "gozleme": "fraunces_k", "sorf": "norican", "pasta": "norican", "tabak": "bodoni", "vegan": "fraunces_k",
             "tahta": "caveat", "baklava": "playfair_k", "kaktus": "bricolage", "wok": "archivo_x", "tabela": "barlow",
             "gunbatimi": "fraunces_k", "liman": "fraunces_k", "rooftop": "unbounded", "bilet": "righteous",
             "pecetelik": "norican", "kofte": "anton", "mira": "bodoni", "saffron": "bodoni", "olea": "fraunces_k",
             "nar": "fraunces_k", "atolye": "anton", "beyaz": "syne", "lune": "playfair_ki", "kekik": "fraunces_k",
             "coral": "archivo_x", "mavikapi": "cinzel", "tuzbiber": "anton", "ada": "fraunces_k", "bakir": "bodoni",
             "yesilev": "fraunces_i", "seker": "norican"}


# ---------------------------------------------------------------- müşteri kataloğu

PAGE = (1654, 2339)
INK, MUTED, PAPER, GOLD = (28, 26, 24), (112, 106, 98), (247, 244, 238), (176, 138, 70)
CHIP = {"2qr": (40, 72, 54), "1qr": (30, 40, 74), "nfc": (112, 30, 40), "wifi": (80, 54, 42)}


def tr_upper(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


def wrap(dr, s, f, width):
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if dr.textlength(t, font=f) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + [cur] if cur else lines


def rounded(im, r):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255)
    return mask


def header(im, dr, p, n, title="Masalık Koleksiyonu"):
    dr.text((80, 64), title, font=font_ui(30, "serif_i"), fill=INK)
    s = f"{p} / {n}"
    dr.text((PAGE[0] - 80 - dr.textlength(s, font=font_ui(26)), 70), s, font=font_ui(26), fill=MUTED)
    dr.rectangle((80, 118, PAGE[0] - 80, 120), fill=(214, 206, 192))


def footer(dr, text="Beğendiğiniz tasarımın numarasını yazmanız yeterli; isim, logo, renk ve masa numarası size göre."):
    f = font_ui(25)
    dr.rectangle((80, PAGE[1] - 128, PAGE[0] - 80, PAGE[1] - 126), fill=(214, 206, 192))
    dr.text((PAGE[0] / 2 - dr.textlength(text, font=f) / 2, PAGE[1] - 104), text, font=f, fill=MUTED)


def shadowed(canvas, im, xy, mask=None, blur=22, off=(0, 18), alpha=0.32):
    """Görseli yumuşak gölgeyle yapıştırır."""
    a = (mask if mask is not None else im.split()[-1]).point(lambda v: int(v * alpha))
    pad = blur * 3
    sh = Image.new("L", (im.width + 2 * pad, im.height + 2 * pad), 0)
    sh.paste(a, (pad, pad))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    dark = Image.new("RGB", sh.size, (40, 30, 22))
    canvas.paste(dark, (xy[0] - pad + off[0], xy[1] - pad + off[1]), sh)
    canvas.paste(im, xy, mask if mask is not None else im)


def photo_box(im, w, h, focus=0.52):
    """Fotoğrafı w × h kutuyu dolduracak biçimde kırpar (nesne ortada)."""
    k = max(w / im.width, h / im.height)
    r = im.resize((int(im.width * k + 0.5), int(im.height * k + 0.5)), Image.LANCZOS)
    x = (r.width - w) // 2
    y = int((r.height - h) * focus)
    return r.crop((x, y, x + w, y + h))


def phone(screen, w=360):
    """Ekran görüntüsünü telefon çerçevesine koyar (RGBA)."""
    bez = max(8, int(w * 0.034))
    screen = screen.convert("RGB")
    bar = int(screen.width * 0.13)                                   # durum çubuğu (saat, pil)
    top = screen.getpixel((screen.width // 2, 4))
    tall = Image.new("RGB", (screen.width, screen.height + bar), top)
    tall.paste(screen, (0, bar))
    tdr = ImageDraw.Draw(tall)
    ink = (20, 20, 22) if sum(top) > 380 else (245, 245, 245)
    fb = font_ui(int(bar * 0.36), "bold")
    tdr.text((screen.width * 0.12, bar * 0.36), "9:41", font=fb, fill=ink)
    bx, by, bw, bh = screen.width * 0.80, bar * 0.42, screen.width * 0.075, bar * 0.24
    tdr.rounded_rectangle((bx, by, bx + bw, by + bh), bh * 0.3, outline=ink, width=3)
    tdr.rounded_rectangle((bx + 4, by + 4, bx + bw * 0.7, by + bh - 4), bh * 0.2, fill=ink)
    for k in range(4):
        hh = bh * (0.35 + 0.22 * k)
        tdr.rectangle((bx - 70 + k * 13, by + bh - hh, bx - 62 + k * 13, by + bh), fill=ink)
    screen = tall
    inner_w = w - 2 * bez
    inner_h = int(inner_w * screen.height / screen.width)
    h = inner_h + 2 * bez
    r = int(w * 0.15)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle((0, 0, w - 1, h - 1), r, fill=(22, 22, 24, 255), outline=(70, 70, 76, 255), width=2)
    scr = screen.convert("RGB").resize((inner_w, inner_h), Image.LANCZOS)
    m = Image.new("L", scr.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, inner_w - 1, inner_h - 1), r - bez, fill=255)
    im.paste(scr, (bez, bez), m)
    iw, ih = int(w * 0.28), int(w * 0.075)
    dr.rounded_rectangle((w / 2 - iw / 2, bez + int(w * 0.03), w / 2 + iw / 2, bez + int(w * 0.03) + ih), ih // 2,
                         fill=(12, 12, 14, 255))
    return im


def site_shots():
    """menu_siteleri.py'nin ekran görüntüleri (varsa)."""
    import menu_siteleri as MS
    out = []
    for s in MS.SITES:
        d = os.path.join(MS.OUT, s["slug"])
        a, b = os.path.join(d, "ekran_ana.png"), os.path.join(d, "ekran_menu.png")
        if os.path.exists(a) and os.path.exists(b):
            out.append((s, Image.open(a), Image.open(b)))
    return out


SITE_FONT = {"kaleici": "Cinzel-Black.ttf", "lagun": "Fraunces-SemiBoldItalic.ttf", "forno": "PlayfairDisplay-Black.ttf",
             "garaj": "Anton-Regular.ttf", "kopuk": "Fraunces-BlackItalic.ttf", "koi": "Syne-ExtraBold.ttf",
             "asma": "PlayfairDisplay-Black.ttf", "kasap": "BodoniModa-ExtraBold.ttf", "palmiye": "Norican-Regular.ttf",
             "r360": "Unbounded-ExtraBold.ttf"}


def icon_box(kind, s=110):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.ellipse((0, 0, s - 1, s - 1), fill=CHIP[kind])
    c = (247, 244, 238)
    if kind in ("2qr", "1qr"):
        q = s * 0.46
        x0, y0 = (s - q) / 2, (s - q) / 2
        for (i, j) in ((0, 0), (1, 0), (0, 1)):
            a = q * 0.42
            xx, yy = x0 + i * (q - a), y0 + j * (q - a)
            dr.rectangle((xx, yy, xx + a, yy + a), outline=c, width=4)
            dr.rectangle((xx + a * 0.3, yy + a * 0.3, xx + a * 0.7, yy + a * 0.7), fill=c)
        dr.rectangle((x0 + q * 0.62, y0 + q * 0.62, x0 + q, y0 + q), fill=c)
        if kind == "2qr":
            dr.text((s * 0.66, s * 0.6), "2", font=font_ui(int(s * 0.3), "bold"), fill=c)
    else:
        dr.rounded_rectangle((s * 0.3, s * 0.24, s * 0.52, s * 0.76), 6, outline=c, width=5)
        for r in (0.14, 0.22, 0.30):
            bb = (s * 0.5 - s * r, s * 0.5 - s * r, s * 0.5 + s * r, s * 0.5 + s * r)
            dr.arc((bb[0] + s * 0.14, bb[1], bb[2] + s * 0.14, bb[3]), -40, 40, fill=c, width=5)
    return im


def cover(rows, n_pages, shots):
    im = Image.new("RGB", PAGE, PAPER)
    dr = ImageDraw.Draw(im)
    dr.text((80, 110), "Masalık", font=font_ui(170, "serif_k"), fill=INK)
    dr.text((86, 308), "Koleksiyonu", font=font_ui(96, "serif_i"), fill=GOLD)
    dr.text((90, 440), f"QR menü · Google yorumu · NFC   —   {len(rows)} tasarım, iki yüzlü, kabartmalı",
            font=font_ui(34), fill=MUTED)
    kapak = os.path.join(OUT_DIR, "foto", "kapak.png")
    W_ = PAGE[0] - 160
    if os.path.exists(kapak):
        ph = photo_box(Image.open(kapak).convert("RGB"), W_, 720, 0.6)
    else:
        ph = studio(W_, 720)
    m = rounded(ph, 36)
    shadowed(im, ph, (80, 520), m, blur=26, off=(0, 20), alpha=0.25)
    y = 520 + 720 + 80
    cols = [("2qr", "İki QR", "Ön yüzde menü, arka yüzde Google yorumu. Masanın iki tarafından da okunur."),
            ("1qr", "Tek QR", "Tek bağlantı, sizin sayfanız: menü, yorum, Wi-Fi, Instagram, rezervasyon."),
            ("nfc", "NFC + QR", "Telefonu dokundurmak yeter. Etiket iki plakanın arasında, iki yüzden okunur.")]
    cw = 330
    for k, (kind, title, desc) in enumerate(cols):
        x = 80 + k * (cw + 30)
        ic = icon_box(kind, 96)
        im.paste(ic, (x, y), ic)
        dr.text((x, y + 116), title, font=font_ui(40, "serif_k"), fill=INK)
        ty = y + 172
        for line in wrap(dr, desc, font_ui(25), cw - 10):
            dr.text((x, ty), line, font=font_ui(25), fill=MUTED)
            ty += 36
    if shots:
        home = next((h for s_, h, _ in shots if s_["slug"] == "forno"), shots[0][1])
        ph_im = phone(home, 330)
        shadowed(im, ph_im, (PAGE[0] - 80 - 330, y - 40), blur=24, off=(0, 22), alpha=0.35)
    y += 400
    dr.text((80, y), "Neden bu masalıklar?", font=font_ui(40, "serif_k"), fill=INK)
    y += 66
    for line in ("Kabartmalı: yazılar, çerçeveler ve QR karosu yüzeyden yükselir; ışıkta derinlik kazanır.",
                 "İki yüzlü: iki plaka sırt sırta, masanın her iki tarafına da hitap eder.",
                 "İki seri: 30 tasarım serisi ve yuvarlak, dikey, yatay 15 sade standart model.",
                 "Renkler baskının içinde: sticker değil; silinmez, solmaz, yıkanır.",
                 "QR adresi bizim sistemimizde: menü ya da bağlantı değişse de masalık değişmez.",
                 "Masa numarası her masalığa ayrı basılır; işletmeye özel menü sitesi dahil."):
        dr.ellipse((84, y + 12, 98, y + 26), fill=GOLD)
        ty = y
        for ln in wrap(dr, line, font_ui(26), 1030):
            dr.text((118, ty), ln, font=font_ui(26), fill=INK)
            ty += 36
        y = ty + 12
    footer(dr)
    return im


def design_page(group, p, n, title="Masalık Koleksiyonu"):
    im = Image.new("RGB", PAGE, PAPER)
    dr = ImageDraw.Draw(im)
    header(im, dr, p, n, title)
    top, ch, gap = 160, 660, 36
    pw, ph = 490, 600
    for k, r in enumerate(group):
        y0 = top + k * (ch + gap)
        x0, x1 = 80, PAGE[0] - 80
        for j, (img, lab) in enumerate(((r["on"], "ÖN"), (r["arka"], "ARKA"))):
            px, py = x0 + j * (pw + 18), y0 + 20
            if img.mode == "RGBA":
                box_ = studio(pw, ph)
                fit = A.fit_into(img, pw - 30, ph - 40)
                box_.paste(fit, ((pw - fit.width) // 2, ph - 20 - fit.height), fit)
            else:
                box_ = photo_box(img, pw, ph)
            m = rounded(box_, 26)
            shadowed(im, box_, (px, py), m, blur=16, off=(0, 12), alpha=0.22)
            f = font_ui(20, "bold")
            tw = dr.textlength(lab, font=f)
            dr.rounded_rectangle((px + 18, py + 18, px + 18 + tw + 28, py + 52), 17, fill=(250, 248, 244))
            dr.text((px + 32, py + 22), lab, font=f, fill=(90, 82, 72))
        tx0 = x0 + 2 * pw + 18 + 46
        dr.text((tx0, y0 + 12), f"{r['i']:02d}", font=font_ui(64, "serif_k"), fill=GOLD)
        name = tr_upper(r["name"]) if r["font"] == "cinzel" else r["name"]
        size = 58
        nf = ImageFont.truetype(os.path.join(A.FONT_DIR, FONT_FILES[r["font"]]), size)
        while dr.textlength(name, font=nf) > x1 - tx0 and size > 28:
            size -= 2
            nf = ImageFont.truetype(os.path.join(A.FONT_DIR, FONT_FILES[r["font"]]), size)
        dr.text((tx0, y0 + 100), name, font=nf, fill=INK)
        dr.text((tx0, y0 + 178), r["sub"], font=font_ui(27), fill=MUTED)
        chip = KIND[r["kind"]].split(" · ")[0]
        f = font_ui(21, "bold")
        cw_ = dr.textlength(chip, font=f) + 34
        dr.rounded_rectangle((tx0, y0 + 228, tx0 + cw_, y0 + 264), 18, fill=CHIP[r["kind"]])
        dr.text((tx0 + 17, y0 + 233), chip, font=f, fill=(247, 244, 238))
        ty = y0 + 288
        for line in wrap(dr, r["desc"], font_ui(23), x1 - tx0)[:5]:
            dr.text((tx0, ty), line, font=font_ui(23), fill=INK)
            ty += 32
        ty += 10
        w, _, h = r["size"]
        specs = [f"Ölçü: {w / 10:.1f} × {h / 10:.1f} cm".replace(".", ","), r["stand"][0].upper() + r["stand"][1:]]
        if r["masa"]:
            specs.append(f"Masa numaralı (örnek: {r['masa']:02d})")
        for line in specs:
            for ln in wrap(dr, line, font_ui(22), x1 - tx0):
                dr.text((tx0, ty), ln, font=font_ui(22), fill=MUTED)
                ty += 30
        ty += 12
        x = tx0
        for c in r["cols"]:
            dr.ellipse((x, ty, x + 28, ty + 28), fill=COL[c], outline=(200, 194, 184), width=2)
            x += 38
    footer(dr)
    return im


def overview(rows, p, n, title="Tüm tasarımlar", sub=None, cols=5, head="Masalık Koleksiyonu"):
    im = Image.new("RGB", PAGE, PAPER)
    dr = ImageDraw.Draw(im)
    header(im, dr, p, n, head)
    dr.text((80, 150), title, font=font_ui(56, "serif_k"), fill=INK)
    top = 250
    if sub:
        dr.text((82, 228), sub, font=font_ui(25), fill=MUTED)
        top = 300
    nrows = -(-len(rows) // cols)
    cw = (PAGE[0] - 160 - (cols - 1) * 15) // cols
    chh = min((PAGE[1] - 150 - top) // nrows - 14, int(cw * 1.07))
    for k, r in enumerate(rows):
        x0, y0 = 80 + (k % cols) * (cw + 15), top + (k // cols) * (chh + 14)
        if r["on"].mode == "RGBA":
            cell = studio(cw, chh)
            fit = A.fit_into(r["on"], cw - 20, chh - 70)
            cell.paste(fit, ((cw - fit.width) // 2, chh - 50 - fit.height), fit)
        else:
            cell = Image.new("RGB", (cw, chh), (250, 248, 244))
            cell.paste(photo_box(r["on"], cw, chh - 46), (0, 0))
        cd = ImageDraw.Draw(cell)
        fn_ = font_ui(24, "serif_k")
        cd.rounded_rectangle((10, 10, 22 + cd.textlength(f"{r['i']:02d}", font=fn_) + 12, 46), 18,
                             fill=(250, 248, 244))
        cd.text((22, 13), f"{r['i']:02d}", font=fn_, fill=GOLD)
        nm = r["name"]
        f = font_ui(21, "bold")
        cd.text((cw / 2 - cd.textlength(nm, font=f) / 2, chh - 37), nm, font=f, fill=INK)
        im.paste(cell, (x0, y0), rounded(cell, 18))
    footer(dr)
    return im


def sites_page(group, p, n, last=False):
    im = Image.new("RGB", PAGE, PAPER)
    dr = ImageDraw.Draw(im)
    header(im, dr, p, n)
    dr.text((80, 150), "Masalıktan açılan sayfa", font=font_ui(56, "serif_k"), fill=INK)
    dr.text((82, 228), "Her işletmeye kendi tarzında site: fotoğraflı menü, masa numarası, Google yorumu, Wi-Fi, sipariş.",
            font=font_ui(25), fill=MUTED)
    cw, chh = (PAGE[0] - 160 - 40) // 2, 960
    for k, (s, home, menu) in enumerate(group):
        x0, y0 = 80 + (k % 2) * (cw + 40), 300 + (k // 2) * (chh + 20)
        back = phone(menu, 288)
        front = phone(home, 312)
        shadowed(im, back, (x0 + cw - 288 - 40, y0 + 10), blur=20, off=(0, 16), alpha=0.28)
        shadowed(im, front, (x0 + 40, y0 + 70), blur=22, off=(0, 20), alpha=0.34)
        cy = y0 + 70 + front.height + 26
        try:
            nf = ImageFont.truetype(os.path.join(A.FONT_DIR, SITE_FONT[s["slug"]]), 40)
        except OSError:
            nf = font_ui(40, "serif_k")
        dr.text((x0 + 40, cy), tr_upper(s["name"]) if s["slug"] == "kaleici" else s["name"], font=nf, fill=INK)
        dr.text((x0 + 40, cy + 54), f"Masalık {s['no']:02d} · {s['slug']}.{DOMAIN}", font=font_ui(21), fill=MUTED)
        if s.get("stil"):
            dr.text((x0 + 40, cy + 86), s["stil"][0].upper() + s["stil"][1:], font=font_ui(21, "bold"), fill=GOLD)
    if last:
        y0 = 300 + chh + 20
        box_ = (80, y0, PAGE[0] - 80, y0 + 330)
        dr.rounded_rectangle(box_, 30, fill=(255, 253, 249), outline=(226, 218, 204))
        dr.text((120, y0 + 40), "Sayfada neler var?", font=font_ui(40, "serif_k"), fill=INK)
        items = ["Masa numaralı karşılama, menü ve fiyatlar", "Google yorumlarına tek dokunuşla yönlendirme",
                 "Wi-Fi'ye bağlanma, Instagram, rezervasyon, yol tarifi", "Masadan sipariş ve garson çağırma (isteğe bağlı)",
                 "Türkçe, İngilizce, Rusça, Almanca (isteğe bağlı)", "Menü ve fiyat güncellemeleri bizden; masalık değişmez"]
        ty = y0 + 110
        for k, line in enumerate(items):
            x = 120 + (k % 2) * 700
            yy = ty + (k // 2) * 56
            dr.ellipse((x, yy + 10, x + 14, yy + 24), fill=GOLD)
            dr.text((x + 30, yy), line, font=font_ui(24), fill=INK)
        y1 = y0 + 390
        dr.text((80, y1), "Nasıl çalışır?", font=font_ui(40, "serif_k"), fill=INK)
        steps = [("1", "Okut ya da dokun", "Müşteri masalıktaki QR'ı okutur ya da telefonunu NFC'ye dokundurur."),
                 ("2", "Sayfa açılır", "Masa numarasıyla işletmenin sayfası açılır; uygulama gerekmez."),
                 ("3", "Menü, yorum, sipariş", "Menüye bakar, Google'da yorum bırakır, garsonu çağırır.")]
        sw = (PAGE[0] - 160 - 2 * 30) // 3
        for k, (num, t, dsc) in enumerate(steps):
            x = 80 + k * (sw + 30)
            dr.rounded_rectangle((x, y1 + 70, x + sw, y1 + 330), 26, fill=(255, 253, 249), outline=(226, 218, 204))
            dr.ellipse((x + 28, y1 + 98, x + 92, y1 + 162), fill=GOLD)
            fnum = font_ui(36, "serif_k")
            dr.text((x + 60 - dr.textlength(num, font=fnum) / 2, y1 + 104), num, font=fnum, fill=(255, 253, 249))
            dr.text((x + 110, y1 + 108), t, font=font_ui(28, "bold"), fill=INK)
            ty = y1 + 186
            for ln in wrap(dr, dsc, font_ui(23), sw - 56):
                dr.text((x + 28, ty), ln, font=font_ui(23), fill=MUTED)
                ty += 32
    footer(dr, "Örnek sitelerdeki işletmeler, ürünler ve fiyatlar örnektir; siteniz kendi menünüzle hazırlanır.")
    return im


def catalog(rows):
    shots = site_shots()
    main_, std = [r for r in rows if r["i"] <= 30], [r for r in rows if r["i"] > 30]
    groups = [main_[k:k + 3] for k in range(0, len(main_), 3)]
    sgroup = [std[k:k + 3] for k in range(0, len(std), 3)]
    sgroups = [shots[k:k + 4] for k in range(0, len(shots), 4)]
    n = 1 + len(groups) + 1 + (1 + len(sgroup) if std else 0) + len(sgroups)
    pages = [cover(rows, n, shots)] + [design_page(g, k + 2, n) for k, g in enumerate(groups)]
    pages.append(overview(main_, len(pages) + 1, n, "Tasarım serisi · 01–30"))
    if std:
        pages.append(overview(std, len(pages) + 1, n, f"Standart seri · 31–{30 + len(std)}",
                              "Yuvarlak, dikey ve yatay; sade, modern ve şık. Her işletmeye uyan zamansız modeller.",
                              cols=3, head="Masalık Koleksiyonu · Standart seri"))
        for g in sgroup:
            pages.append(design_page(g, len(pages) + 1, n, "Masalık Koleksiyonu · Standart seri"))
    for k, g in enumerate(sgroups):
        pages.append(sites_page(g, len(pages) + 1, n, last=k == len(sgroups) - 1 and len(g) <= 2))
    for f in os.listdir(OUT_DIR):
        if f.startswith("musteri_") and f[8:10].isdigit():
            os.remove(os.path.join(OUT_DIR, f))
    for k, pg in enumerate(pages, 1):
        pg.save(os.path.join(OUT_DIR, f"musteri_{k:02d}.png"), optimize=True)
        pg.save(os.path.join(OUT_DIR, f"musteri_{k:02d}.jpg"), "JPEG", quality=88, optimize=True)
    pages[0].save(os.path.join(OUT_DIR, "musteri_katalog.pdf"), save_all=True, append_images=pages[1:], resolution=200)


def pack(r):
    """Önbellek için görüntüleri PNG baytına çevirir."""
    import io
    out = dict(r)
    for k in ("on", "arka"):
        buf = io.BytesIO()
        r[k].save(buf, "PNG")
        out[k] = buf.getvalue()
    return out


def unpack(r):
    import io
    out = dict(r)
    for k in ("on", "arka"):
        if isinstance(r[k], bytes):
            out[k] = Image.open(io.BytesIO(r[k]))
            out[k].load()
    return out


def main():
    import pickle
    from multiprocessing import Pool
    os.makedirs(OUT_DIR, exist_ok=True)
    cache = os.path.join(OUT_DIR, ".onbellek.pkl")
    only = sys.argv[1:]
    if only == ["katalog"]:
        catalog([unpack(r) for r in pickle.load(open(cache, "rb"))])
        return
    todo = [i for i, fn in enumerate(DESIGNS, 1) if not only or any(o in fn.__name__ for o in only)]
    with Pool(4) as pool:
        rows = pool.map(work, todo)
    for r in rows:
        print(r["line"])
    old = {}
    if os.path.exists(cache):
        old = {r["i"]: r for r in pickle.load(open(cache, "rb"))}
    old.update({r["i"]: pack(r) for r in rows})
    pickle.dump([old[k] for k in sorted(old)], open(cache, "wb"))
    if len(old) == len(DESIGNS):
        catalog([unpack(old[k]) for k in sorted(old)])


if __name__ == "__main__":
    main()
