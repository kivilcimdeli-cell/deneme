"""AUTO FIRAT TUYGUN (oto galeri) anahtarlıkları: Bambu Lab X2D için 3MF.

Her tasarım tek parça basılır, destek gerekmez:
  * Gövde   : siyah (filament 1), 3,0 mm; alt kenarda 0,3 mm fil ayağı payı,
              üst kenarda katman katman 0,6 mm pah
  * Kabartma: gövdenin üstünde 0,8 mm (4 katman); tasarıma göre sarı, beyaz
              ve/veya mavi

Baskı için optimize edildi (0,4 nozul):
  * küçük yazılar Lexend ExtraBold (küçük boyda kalın, rakam içleri açık), en az ~3,4 mm;
    isim en az 7,5 mm
  * çizgiler en az 1,0 mm, kabartmalar arası boşluk en az 0,6 mm (kontrol edilir)
  * nesne ayarı olarak Arachne duvar üretici (ince yazıları daha düzgün basar)

Yazıcı/filament/baskı ayarları `isimlik/orijinal/...3mf` içindeki Bambu Lab X2D
projesinden alınır; filament sayısı ve renkleri tasarıma göre ayarlanır.

Çıktı : anahtarlik/<tasarım>.3mf, anahtarlik/onizleme/<tasarım>.png, anahtarlik/onizleme/hepsi.png,
        anahtarlik/onizleme/yeni_tasarimlar.png (8-12)

Kullanım:
  pip install numpy manifold3d pillow shapely scipy fonttools uharfbuzz segno opencv-python-headless
  python3 scripts/anahtarlik.py            # hepsi
  python3 scripts/anahtarlik.py plaka      # adında "plaka" geçenler
"""
import datetime
import io
import json
import os
import sys
import zipfile
from dataclasses import dataclass, field

import manifold3d as m3
import numpy as np
import uharfbuzz as hb
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
from scipy.interpolate import splev, splprep
from shapely.geometry import LinearRing, LineString, MultiPolygon, Polygon
from shapely.geometry.polygon import orient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cift_tarafli_isimlik import PICK_ID, mesh_xml, render, rotation  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "scripts", "fonts")
TEMPLATE = os.path.join(ROOT, "isimlik", "orijinal", "Two_line_Customizable_Name_Plate.3mf")
OUT_DIR = os.path.join(ROOT, "anahtarlik")

BLACK, YELLOW, WHITE, BLUE = 1, 2, 3, 4                                   # renk kimlikleri
COLOURS = {BLACK: "#000000", YELLOW: "#F4EE2A", WHITE: "#FFFFFF", BLUE: "#0A2989"}   # Bambu PLA Basic renkleri
COLOUR_NAMES = {BLACK: "siyah", YELLOW: "sarı", WHITE: "beyaz", BLUE: "mavi"}
SHOW = {BLACK: (40, 40, 43), YELLOW: (255, 222, 40), WHITE: (246, 246, 242), BLUE: (28, 66, 168)}  # önizleme tonları

LAYER = 0.2
BASE_H = 3.0         # siyah gövde (15 katman)
RAISE_H = 0.8        # kabartma (4 katman)
FOOT = 0.3           # ilk katmanda içe çekme (fil ayağı)
CHAMFER = 0.6        # üst kenar pahı (3 katman)
LINE = 1.2           # standart çizgi kalınlığı
EDGE_KEEP = 1.0      # kabartmanın gövde kenarına en yakın mesafesi
MIN_FEATURE = 0.7    # kontrol: en ince kabartma (mm)
MIN_GAP = 0.6        # kontrol: kabartmalar arası en dar boşluk (mm)
BED_CENTER = (128.0, 128.0)

NAME = "FIRAT TUYGUN"
PHONE = "0535 278 35 29"
CITY = "ANTALYA"


# ---------------------------------------------------------------- 2B yardımcılar

def empty():
    return m3.CrossSection()


def union(*parts):
    parts = [p for p in parts if p is not None and not p.is_empty()]
    return m3.CrossSection.batch_boolean(parts, m3.OpType.Add) if parts else empty()


def from_shapely(geom):
    polys = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
    contours = []
    for p in polys:
        if p.is_empty:
            continue
        p = orient(p, 1.0)
        contours.append(np.asarray(p.exterior.coords)[:-1])
        contours += [np.asarray(i.coords)[:-1] for i in p.interiors]
    return m3.CrossSection(contours, m3.FillRule.Positive) if contours else empty()


def stroke(points, width=LINE, closed=False):
    """Bir çizgiyi (açık ya da kapalı) yuvarlak uçlu, `width` kalınlığında bir şekle çevirir."""
    pts = np.asarray(points, float)
    line = LinearRing(pts) if closed else LineString(pts)
    return from_shapely(line.buffer(width / 2, quad_segs=10, cap_style="round", join_style="round"))


def outline(shape, width=LINE, inset=0.0):
    """Bir şeklin içinden `inset` kadar içeride, `width` kalınlığında kontur çizgisi."""
    outer = shape.offset(-inset, m3.JoinType.Round) if inset else shape
    return outer - outer.offset(-width, m3.JoinType.Round)


def smooth(points, closed=False, n=240):
    """Kontrol noktalarından geçen yumuşak eğri (kübik spline)."""
    pts = np.asarray(points, float)
    if closed:
        pts = np.vstack([pts, pts[:1]])
    tck, _ = splprep([pts[:, 0], pts[:, 1]], s=0, per=closed, k=min(3, len(pts) - 1))
    x, y = splev(np.linspace(0, 1, n, endpoint=not closed), tck)
    return np.c_[x, y]


def polygon(points):
    return from_shapely(Polygon(points).buffer(0))


def rrect(w, h, r, cx=0.0, cy=0.0):
    core = m3.CrossSection.square((w - 2 * r, h - 2 * r), True)
    return core.offset(r, m3.JoinType.Round, 2.0, 96).translate((cx, cy))


def circle(r, cx=0.0, cy=0.0, n=96):
    return m3.CrossSection.circle(r, n).translate((cx, cy))


def rect(x0, y0, x1, y1):
    return m3.CrossSection.square((x1 - x0, y1 - y0)).translate((x0, y0))


def shear(cs, deg):
    """İtalik/eğik görünüm: x += y * tan(deg)."""
    return cs.transform([[1.0, np.tan(np.radians(deg)), 0.0], [0.0, 1.0, 0.0]])


def qr_matrix(data, error="m"):
    import segno
    q = segno.make(data, error=error, micro=False)
    return np.array([[bool(v) for v in row] for row in q.matrix], bool)


def qr_light(data, module, cx, cy, quiet=2):
    """QR kodun açık (beyaz) alanı: sessiz bölge dahil kare, koyu modüller oyuk.
    Köşeden değen koyu modüller birleşsin diye 0,05 mm büyütülür; beyazdaki kıl payı köprüler temizlenir."""
    m = qr_matrix(data)
    n = m.shape[0]
    size = (n + 2 * quiet) * module
    x0, y0 = cx - n * module / 2, cy + n * module / 2
    dark = union(*[rect(x0 + j * module, y0 - (i + 1) * module, x0 + (j + 1) * module, y0 - i * module)
                   for i in range(n) for j in range(n) if m[i, j]])
    light = rect(cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2) - dark.offset(0.05, m3.JoinType.Miter)
    return light.offset(-0.25, m3.JoinType.Round).offset(0.25, m3.JoinType.Round), size


# ---------------------------------------------------------------- yazı

class _FlattenPen(BasePen):
    def __init__(self, glyphset, steps=10):
        super().__init__(glyphset)
        self.steps = steps
        self.contours, self.cur = [], []

    def _moveTo(self, p):
        self.cur = [p]

    def _lineTo(self, p):
        self.cur.append(p)

    def _curveToOne(self, p1, p2, p3):
        p0 = np.array(self.cur[-1]); p1, p2, p3 = map(np.array, (p1, p2, p3))
        for t in np.linspace(0, 1, self.steps + 1)[1:]:
            self.cur.append(tuple((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3))

    def _qCurveToOne(self, p1, p2):
        p0 = np.array(self.cur[-1]); p1, p2 = np.array(p1), np.array(p2)
        for t in np.linspace(0, 1, self.steps + 1)[1:]:
            self.cur.append(tuple((1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2))

    def _closePath(self):
        if len(self.cur) > 2:
            self.contours.append(np.array(self.cur, float))
        self.cur = []

    _endPath = _closePath


class Font:
    def __init__(self, filename):
        path = os.path.join(FONT_DIR, filename)
        self.tt = TTFont(path)
        self.glyphset = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.upem = self.tt["head"].unitsPerEm
        self.cap_units = self.tt["OS/2"].sCapHeight or 0.7 * self.upem
        self.hb = hb.Font(hb.Face(hb.Blob.from_file_path(path)))
        self._outlines = {}

    def _outline(self, gid):
        if gid not in self._outlines:
            pen = _FlattenPen(self.glyphset)
            self.glyphset[self.order[gid]].draw(pen)
            self._outlines[gid] = pen.contours
        return self._outlines[gid]

    def layout(self, text, cap, tracking=0.0):
        """Harf dizilimi: [(gid, x_mm, y_mm, advance_mm)], toplam genişlik (mm)."""
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": False})
        k = cap / self.cap_units
        x, out = 0.0, []
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            adv = pos.x_advance * k
            out.append((info.codepoint, x + pos.x_offset * k, pos.y_offset * k, adv))
            x += adv + tracking
        return out, x - tracking

    def width(self, text, cap, tracking=0.0):
        return self.layout(text, cap, tracking)[1]

    def fit_cap(self, text, cap, max_w, tracking=0.0):
        """`max_w`'ya sığacak en büyük yazı yüksekliği (en fazla `cap`); harf aralığı ölçeklenmez."""
        glyphs, w = self.layout(text, cap, 0.0)
        extra = tracking * (len(glyphs) - 1)
        return cap if w + extra <= max_w else cap * (max_w - extra) / w

    def text(self, text, cap, x=0.0, y=0.0, align="c", valign="m", tracking=0.0, angle=0.0):
        """Yazıyı şekle çevirir. (x, y): hizalama noktası; valign 'm' = büyük harf ortası, 'b' = taban çizgisi."""
        glyphs, w = self.layout(text, cap, tracking)
        k = cap / self.cap_units
        dx = {"l": 0.0, "c": -w / 2, "r": -w}[align]
        dy = -cap / 2 if valign == "m" else 0.0
        contours = []
        for gid, gx, gy, _ in glyphs:
            for c in self._outline(gid):
                contours.append(c * k + (gx + dx, gy + dy))
        cs = m3.CrossSection(contours, m3.FillRule.NonZero) if contours else empty()
        return cs.rotate(angle).translate((x, y)) if angle else cs.translate((x, y))

    def arc(self, text, cap, cx, cy, r, center_deg=90.0, top=True, tracking=0.0):
        """Yazıyı bir çember yayına dizer. top=True: üst yayda dışa bakan; False: alt yayda okunur hâlde.
        r: taban çizgisinin yarıçapı."""
        glyphs, w = self.layout(text, cap, tracking)
        k = cap / self.cap_units
        r_mid = r + cap / 2 if top else r - cap / 2
        parts = []
        for gid, gx, gy, adv in glyphs:
            contours = self._outline(gid)
            if not contours:
                continue
            gc = gx + adv / 2 - w / 2                      # harfin yazı ortasına uzaklığı
            th = np.radians(center_deg) + (-gc if top else gc) / r_mid
            u = np.array([np.cos(th), np.sin(th)])        # dışa doğru
            t = np.array([np.sin(th), -np.cos(th)]) if top else np.array([-np.sin(th), np.cos(th)])
            pts = []
            for c in contours:
                lx = c[:, 0] * k + gx - (gx + adv / 2)
                ly = c[:, 1] * k + gy
                rad = (r + ly) if top else (r - ly)
                pts.append(np.outer(rad, u) + np.outer(lx, t) + (cx, cy))
            parts.append(m3.CrossSection(pts, m3.FillRule.NonZero))
        return union(*parts)


FONTS = {}
FONT_FILES = {"bebas": "BebasNeue-Regular.ttf",            # isim (fotoğraftakine en yakın)
              "barlow": "BarlowCondensed-ExtraBold.ttf",   # AUTO
              "plate": "BarlowCondensed-Black.ttf",        # plaka harfleri (07 FT 29, TR)
              "small": "Lexend-ExtraBold.ttf"}             # telefon, şehir: küçük boyda kalın, iç boşlukları açık


def font(name):
    if name not in FONTS:
        FONTS[name] = Font(FONT_FILES[name])
    return FONTS[name]


def name_text(cap, x, y, max_w=None, **kw):
    f = font("bebas")
    return f.text(NAME, f.fit_cap(NAME, cap, max_w) if max_w else cap, x, y, **kw)


def small_text(text, cap, x, y, max_w=None, tracking=0.0, **kw):
    f = font("small")
    return f.text(text, f.fit_cap(text, cap, max_w, tracking) if max_w else cap, x, y, tracking=tracking, **kw)


def auto_text(cap, x, y, tracking=None, **kw):
    return font("barlow").text("AUTO", cap, x, y, tracking=cap * 0.12 if tracking is None else tracking, **kw)


# ---------------------------------------------------------------- tasarım

@dataclass
class Design:
    key: str                   # dosya adı
    title: str                 # Bambu Studio'daki nesne adı
    base: m3.CrossSection      # siyah gövde dış hattı
    raised: list               # [(şekil, filament)], sonraki öncekinin üstüne yazar
    holes: m3.CrossSection = field(default_factory=lambda: m3.CrossSection())
    note: str = ""

    def body(self):
        return self.base - self.holes

    def raised_parts(self):
        """Filament başına, gövdeye kırpılmış ve çakışmaları çözülmüş kabartmalar."""
        allowed = self.body().offset(-EDGE_KEEP, m3.JoinType.Round) - self.holes.offset(0.8, m3.JoinType.Round)
        out, taken = {}, empty()
        for shape, ext in reversed(self.raised):        # en son eklenen en üstte
            part = (shape ^ allowed) - taken
            taken = taken + shape
            out[ext] = out.get(ext, empty()) + part
        for ext in list(out):
            keep = [p for p in out[ext].decompose() if p.area() > 0.5]   # kıl payı adacıkları at
            out[ext] = union(*keep)
            if out[ext].is_empty():
                del out[ext]
        return out

    def solids(self):
        body = self.body()
        x0, y0, x1, y1 = body.bounds()
        c = (-(x0 + x1) / 2, -(y0 + y1) / 2)
        # gövde tek katı; ilk katmandan ve üst 3 katmandan kenar halkaları kesilir (katmanlara oturan pah)
        body = body.translate(c)
        govde = body.extrude(BASE_H)
        n = int(round(BASE_H / LAYER))
        steps = int(round(CHAMFER / LAYER))
        cuts = [((body - body.offset(-FOOT, m3.JoinType.Round)), -0.1, LAYER)]
        for k in range(steps):
            z0 = BASE_H - (steps - k) * LAYER
            inset = CHAMFER * (k + 1) / steps
            top = BASE_H + 0.1 if k == steps - 1 else z0 + LAYER
            cuts.append((body - body.offset(-inset, m3.JoinType.Round), z0, top))
        rings = [ring.extrude(z1 - z0).translate((0, 0, z0)) for ring, z0, z1 in cuts]
        govde = govde - m3.Manifold.batch_boolean(rings, m3.OpType.Add)
        govde = m3.Manifold.batch_boolean([p for p in govde.decompose() if p.volume() > 1.0], m3.OpType.Add)
        assert n > steps + 1
        parts = [("Gövde (siyah)", govde, BLACK)]
        for ext, cs in sorted(self.raised_parts().items()):
            parts.append((f"Kabartma ({COLOUR_NAMES[ext]})", cs.translate(c).extrude(RAISE_H).translate((0, 0, BASE_H)), ext))
        return parts

    def size(self):
        x0, y0, x1, y1 = self.base.bounds()
        return x1 - x0, y1 - y0

    def check(self):
        """Baskı kontrolü: çok ince kabartma ve çok dar boşluk alanları (mm²)."""
        parts = self.raised_parts()
        allr = union(*parts.values())

        def spots(cs):  # harf köşelerindeki kıl payı pürüzleri sayma
            return union(*[p for p in cs.decompose() if p.area() > 0.25])

        thin = union(*[spots(cs - cs.offset(-MIN_FEATURE / 2).offset(MIN_FEATURE / 2)) for cs in parts.values()])
        gaps = spots(allr.offset(MIN_GAP / 2).offset(-MIN_GAP / 2) - allr)
        return thin, gaps, allr.area()

    def check_pairs(self):
        """Ayrı tasarım öğeleri (yazı, çizgi, çerçeve...) arasında MIN_GAP'ten yakın olan çiftler."""
        allowed = self.body().offset(-EDGE_KEEP, m3.JoinType.Round) - self.holes.offset(0.8, m3.JoinType.Round)
        feats = [shape ^ allowed for shape, _ in self.raised]
        bad = []
        for i, a in enumerate(feats):
            for j in range(i + 1, len(feats)):
                b = feats[j]
                if a.is_empty() or b.is_empty():
                    continue
                if (a.offset(0.05) ^ b).area() > 0.01:
                    continue            # bitişik (ör. mavi şerit + beyaz zemin): sorun değil
                if (a.offset(MIN_GAP / 2) ^ b.offset(MIN_GAP / 2)).area() > 0.02:
                    bad.append((i, j))
        return bad

    def hole_wall(self):
        """Deliklerin çevresindeki en ince et payı (mm, 0,1 hassasiyet)."""
        if self.holes.is_empty():
            return None
        for w in np.arange(0.5, 6.01, 0.1):
            if (self.holes.offset(w, m3.JoinType.Round) - self.base).area() > 1e-3:
                return round(w - 0.1, 1)
        return 6.0


def qr_decodes(d, data, px_per_mm=12):
    """Üstten görünüşü (siyah gövde, beyaz kabartma) çizip QR kodu OpenCV ile okur."""
    import cv2
    from PIL import ImageDraw as _D
    body, light = d.body(), d.raised_parts().get(WHITE, empty())
    x0, y0, x1, y1 = body.bounds()
    W, H = int((x1 - x0 + 20) * px_per_mm), int((y1 - y0 + 20) * px_per_mm)
    img = Image.new("L", (W, H), 150)
    dr = _D.Draw(img)

    def fill(cs, val):
        for p in cs.to_polygons():
            x, y = p[:, 0], p[:, 1]
            hole = np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y) < 0
            dr.polygon([((u - x0 + 10) * px_per_mm, (y1 - v + 10) * px_per_mm) for u, v in p],
                       fill=(40 if val == 246 else 150) if hole else val)

    fill(body, 40)
    fill(light, 246)
    text, _, _ = cv2.QRCodeDetector().detectAndDecode(np.array(img))
    return text == data, text


# ---------------------------------------------------------------- araba profili

CAR_PTS = [(5.5, 4.4), (2.0, 5.6), (0.2, 8.6), (0.0, 12.4), (1.6, 15.8), (6.4, 18.0), (20, 20.4),
           (33, 22.4), (40.5, 26.8), (47.5, 31.0), (54, 33.2), (62, 33.9), (71, 32.8), (80, 29.6),
           (88.5, 26.6), (93.4, 26.4), (96.6, 27.6), (98.8, 25.2), (99.7, 21.0), (99.8, 15.6),
           (98.9, 10.4), (96.8, 6.0), (93, 4.2), (86, 3.6), (64, 3.5), (36, 3.5), (14, 3.6)]
CAR_WHEELS = [(22.0, 7.2), (78.5, 7.2)]
CAR_WR = 7.2


def car_profile(length=100.0):
    """Yandan coupe silueti (ön solda); çizim 100 mm, `length`'e ölçeklenir.
    Döner: gövde (tekerleksiz), tekerlek merkezleri, yarıçap, ölçek."""
    s = length / 100.0
    body = polygon(smooth(np.array(CAR_PTS) * s, closed=True, n=500))
    return body, [(x * s, y * s) for x, y in CAR_WHEELS], CAR_WR * s, s


def car_silhouette(length=100.0):
    body, wc, wr, s = car_profile(length)
    wheels = union(*[circle(wr, x, y) for x, y in wc])
    r = 1.8 * s
    shape = (body + wheels).offset(r, m3.JoinType.Round).offset(-r, m3.JoinType.Round)
    return shape, body, wc, wr, s


def car_window(body, s, inset, belt, rear, slope=0.9):
    """Gövde konturundan sabit `inset` içeride, `belt` hizasının üstünde, arkası eğik kesilmiş cam alanı."""
    region = body.offset(-inset, m3.JoinType.Round) ^ rect(-50, belt * s, 300, 100)
    cut = polygon([(rear * s, belt * s), ((rear + 60 * slope) * s, (belt + 60) * s), (400, 100), (400, belt * s)])
    r = 1.0  # sivri köşeleri yuvarla (dar siyah kama kalmasın)
    return (region - cut).offset(-r, m3.JoinType.Round).offset(r, m3.JoinType.Round)


def car_lineart(length, width=1.1):
    """Çizgi araba: gövde konturu, açık tekerlek kemerleri, tekerlekler ve cam."""
    body, wc, wr, s = car_profile(length)
    arches = union(*[circle(wr + 2.0 * s, x, y) for x, y in wc])
    lines = outline(body - arches, width)
    window = outline(car_window(body, s, width + 1.6, 23.8, 80.0, 0.6), width)
    wheels = union(*[outline(circle(wr - 0.6 * s, x, y), width) for x, y in wc])
    hubs = union(*[circle(1.4 * s, x, y) for x, y in wc])
    return lines + window + wheels + hubs, s


# ---------------------------------------------------------------- tasarımlar

def d1_klasik():
    """Fotoğraf 1 (mavi→sarı): sarı çerçeve ve AUTO; beyaz çizgi araba, isim, telefon, şehir."""
    W, H = 84.0, 56.0
    base = rrect(W, H, 7.0)
    frame = outline(rrect(W - 4.4, H - 4.4, 5.0), 1.4)
    holes = circle(2.6, W / 2 - 8.0, H / 2 - 8.0)
    art, s = car_lineart(58.0)
    ax0, ay0, ax1, ay1 = art.bounds()
    dx, dy = -(ax0 + ax1) / 2 - 2.5, H / 2 - 5.4 - ay1
    art = art.translate((dx, dy))
    auto = auto_text(4.8, 50.0 * s + dx, 15.8 * s + dy)
    name = name_text(11.0, 0, -4.0, max_w=W - 14)
    phone = small_text(PHONE, 4.2, 0, -13.4)
    city = small_text(CITY, 3.4, 0, -19.6, tracking=0.9)
    raised = [(frame, YELLOW), (art, WHITE), (auto, YELLOW), (name, WHITE), (phone, WHITE), (city, WHITE)]
    return Design("1_klasik_kart", "AUTO_FIRAT_TUYGUN_klasik", base, raised, holes, "3 renk")


def _car_common(length=100.0):
    shape, body, wc, wr, s = car_silhouette(length)
    hole_c = (91.0 * s, 17.4 * s)
    holes = circle(2.6, *hole_c)
    # iç kontur: deliğin etrafından dolaşır, tekerlek hizasında biter
    inner = shape.offset(-1.7, m3.JoinType.Round) - circle(2.6 + 2.4, *hole_c)
    ring = outline(inner, 1.1) ^ rect(-50, 10.6 * s, 200, 100)
    name = name_text(8.4, 54.0 * s, 13.4 * s)
    info = small_text(f"{PHONE}  {CITY}", 3.3, 54.0 * s, 6.1 * s)
    return shape, body, holes, ring, name, info, s


def d2_araba():
    """Fotoğraf 2 (mavi→sarı): sarı kontur, cam ve AUTO; beyaz farlar, isim ve bilgi satırı."""
    shape, body, holes, ring, name, info, s = _car_common()
    win = outline(car_window(body, s, 1.7 + 1.1 + 1.0, 22.2, 81.0, 0.55), 1.1)
    auto = auto_text(3.8, 61.5 * s, 26.0 * s)
    head1 = stroke(smooth(np.array([(5.2, 12.6), (9.0, 13.2), (13.0, 12.0)]) * s), 1.1)
    head2 = stroke(np.array([(3.6, 9.0), (7.2, 9.2), (8.8, 6.6)]) * s, 1.1)
    raised = [(ring, YELLOW), (win, YELLOW), (auto, YELLOW), (head1, WHITE), (head2, WHITE),
              (name, WHITE), (info, WHITE)]
    return Design("2_araba_silueti", "AUTO_FIRAT_TUYGUN_araba", shape, raised, holes, "3 renk")


def d3_araba_cam():
    """Fotoğraf 3 (mavi→sarı): direkli yan cam ve AUTO sarı; köşeli farlar, isim ve bilgi beyaz."""
    shape, body, holes, ring, name, info, s = _car_common()
    area = car_window(body, s, 1.7 + 1.1 + 1.0, 22.2, 79.0, 0.35)
    pillar = polygon([(52.2 * s, 21.0 * s), (54.6 * s, 21.0 * s), (50.6 * s, 40 * s), (48.2 * s, 40 * s)])
    win = outline(area, 1.1) + (pillar ^ area)
    auto = auto_text(3.8, 66.5 * s, 26.0 * s)
    head1 = stroke(np.array([(4.4, 14.0), (9.2, 15.4), (14.2, 15.4)]) * s, 1.1)
    head2 = stroke(np.array([(5.4, 11.4), (10.8, 12.6)]) * s, 1.1)
    head3 = stroke(np.array([(3.6, 8.6), (7.2, 8.8), (8.8, 6.4)]) * s, 1.1)
    raised = [(ring, YELLOW), (win, YELLOW), (auto, YELLOW),
              (head1, WHITE), (head2, WHITE), (head3, WHITE), (name, WHITE), (info, WHITE)]
    return Design("3_araba_yan_cam", "AUTO_FIRAT_TUYGUN_araba_2", shape, raised, holes, "3 renk")


def _plate(W, H, face_bottom, strip_gap):
    """Plaka anahtarlık iskeleti: solda delikli kulak, siyah çerçeve, plaka zemini ve TR şeridi.
    Döner: base, holes, face (yazı alanı), strip (TR şeridi), border (gerçek plakalardaki ince siyah çizgi),
    şerit ve yazı alanı sınırları."""
    tab = circle(6.4, -W / 2 - 1.5, 0)
    base = (rrect(W, H, 4.0) + tab).offset(1.5, m3.JoinType.Round).offset(-3.0, m3.JoinType.Round).offset(1.5, m3.JoinType.Round)
    holes = circle(2.6, -W / 2 - 2.0, 0)
    px0, px1, py0, py1 = -W / 2 + 3.2, W / 2 - 3.2, face_bottom, H / 2 - 3.2
    plate = rrect(px1 - px0, py1 - py0, 2.0, (px0 + px1) / 2, (py0 + py1) / 2)
    sx1 = px0 + 9.6
    strip = plate ^ rect(px0 - 1, py0 - 1, sx1, py1 + 1)
    face = plate - rect(px0 - 1, py0 - 1, sx1 + strip_gap, py1 + 1)
    border = outline(plate, 0.8, inset=1.1)
    return base, holes, face, strip, border, (px0, sx1, px1, py0, py1)


def d4_plaka():
    """Galeri plaka çerçevesi: beyaz plakada büyük oyma "AUTO FIRAT TUYGUN", sarı TR şeridi,
    çerçevede büyük telefon ve şehir."""
    W, H = 106.0, 40.0
    base, holes, face, strip, border, (px0, sx1, px1, py0, py1) = _plate(W, H, -5.0, 0.8)
    tr = font("plate").text("TR", 4.0, (px0 + 1.9 + sx1) / 2, py0 + 5.0, tracking=0.4)
    text = "AUTO " + NAME
    cx, cy = (sx1 + 0.8 + px1) / 2, (py0 + py1) / 2
    cap = font("bebas").fit_cap(text, 11.0, px1 - sx1 - 6.4, tracking=0.35)
    plate_text = font("bebas").text(text, cap, cx, cy, tracking=0.35)
    face = face - border - plate_text
    strip = strip - border - tr
    info_y = (-H / 2 + py0) / 2 - 0.1
    phone = small_text(PHONE, 4.6, -W / 2 + 5.4, info_y, align="l")
    city = small_text(CITY, 4.2, W / 2 - 5.4, info_y, align="r", tracking=0.9)
    raised = [(strip, YELLOW), (face, WHITE), (phone, YELLOW), (city, YELLOW)]
    return Design("4_plaka", "AUTO_FIRAT_TUYGUN_plaka", base, raised, holes, "3 renk")


def d13_plaka_klasik():
    """Klasik Türk plakası (sarısız): beyaz zeminde büyük "07 FT 29", mavi şeritte beyaz TR,
    altta çerçevede beyaz "FIRAT TUYGUN"."""
    W, H = 100.0, 44.0
    base, holes, face, strip, border, (px0, sx1, px1, py0, py1) = _plate(W, H, -4.4, 0.0)
    tr = font("plate").text("TR", 4.2, (px0 + 1.9 + sx1) / 2, py0 + 5.2, tracking=0.4)
    cx, cy = (sx1 + px1) / 2, (py0 + py1) / 2
    plate_text = font("plate").text("07 FT 29", font("plate").fit_cap("07 FT 29", 14.5, px1 - sx1 - 8.0, 1.2),
                                    cx, cy, tracking=1.2)
    face = face - border - plate_text
    strip = strip - border
    name = name_text(9.0, 0, (-H / 2 + py0) / 2 - 0.1, max_w=W - 16.0, tracking=0.5)
    raised = [(strip, BLUE), (tr, WHITE), (face, WHITE), (name, WHITE)]
    return Design("13_plaka_klasik", "FIRAT_TUYGUN_plaka_07FT29", base, raised, holes, "3 renk")


def d5_araba_anahtari():
    """Yeni (galeri): araba anahtarı; kumanda gövdesinde isim, anahtar dilinde telefon."""
    fob = rrect(60.0, 35.0, 11.5, -25.0, 0)
    shoulder = rrect(9.0, 20.0, 3.0, 8.0, 0)
    bottom = [(4, -6.6), (13, -6.6), (15, -5.0), (18, -6.6), (22, -6.6), (24.5, -4.8), (27.5, -6.6),
              (31, -6.6), (33, -5.2), (36, -6.6), (40, -6.6), (42, -5.2), (44, -6.6)]
    blade = polygon([(4, 6.6), (46.0, 6.6), (51.5, 2.6), (51.5, -2.6), (48.0, -6.6)] + bottom[::-1])
    base = union(fob, shoulder, blade)
    holes = circle(2.7, -48.4, 0.0)
    panel = rrect(45.0, 28.4, 8.0, -19.2, 0)
    ring = outline(panel, 1.2)
    collar = outline(shoulder, 1.1, inset=1.2)
    groove = stroke(np.array([(12.5, 4.1), (44.5, 4.1)]), 1.0)
    auto = auto_text(4.4, -19.2, 8.6)
    name = name_text(8.0, -19.2, 0.2, max_w=39.0)
    phone = small_text(PHONE, 3.6, -19.2, -8.4, max_w=39.0)
    city = small_text(CITY, 3.6, 29.4, -0.8, max_w=31.0, tracking=0.7)
    raised = [(ring, YELLOW), (collar, YELLOW), (groove, YELLOW), (auto, YELLOW), (name, YELLOW),
              (city, YELLOW), (phone, YELLOW)]
    return Design("5_araba_anahtari", "AUTO_FIRAT_TUYGUN_anahtar", base, raised, holes, "2 renk")


def d6_lastik_rozet():
    """Yeni: lastik rozeti; tok blok dişli lastik, iç halka, kavisli şehir ve telefon."""
    R = 31.0
    tab_c = (0, R + 2.6)
    base = (circle(R, 0, 0, 180) + circle(6.4, *tab_c)).offset(1.2, m3.JoinType.Round).offset(-1.2, m3.JoinType.Round)
    holes = circle(2.6, 0, R + 2.9)
    band = circle(R - EDGE_KEEP, 0, 0, 180) - circle(R - 5.4, 0, 0, 180)
    grooves = union(*[rect(-0.65, R - 3.4, 0.65, R + 2).rotate(a) for a in np.arange(5, 360, 10.0)])
    tire = band - grooves - circle(6.4 + 1.2, *tab_c)
    tire = tire.offset(-0.45, m3.JoinType.Round).offset(0.45, m3.JoinType.Round)   # kesilen ince parçaları at
    ring = outline(circle(R - 6.2, 0, 0, 180), 1.2)
    city = font("small").arc(CITY, 3.5, 0, 0, R - 11.8, 90.0, top=True, tracking=1.0)
    phone = font("small").arc(PHONE, 3.4, 0, 0, R - 8.2, -90.0, top=False, tracking=0.3)
    auto = auto_text(4.8, 0, 12.6)
    first = font("bebas").text("FIRAT", 9.4, 0, 3.6)
    last = font("bebas").text("TUYGUN", font("bebas").fit_cap("TUYGUN", 9.4, 28.0), 0, -7.2)
    raised = [(tire, YELLOW), (ring, YELLOW), (city, YELLOW), (phone, YELLOW), (auto, YELLOW),
              (first, YELLOW), (last, YELLOW)]
    return Design("6_lastik_rozet", "AUTO_FIRAT_TUYGUN_rozet", base, raised, holes, "2 renk")


def d7_kilometre_saati():
    """Yeni (galeri): kilometre saati; beyaz çentikler ve yazılar, sarı ibre, göbek, kenar ve AUTO."""
    cy = 4.0
    dial = circle(31.0, 0, cy, 180) ^ rect(-40, -22.5, 40, 50)
    tab_c = (0, cy + 33.4)
    base = (dial + circle(6.4, *tab_c)).offset(1.5, m3.JoinType.Round).offset(-3.0, m3.JoinType.Round).offset(1.5, m3.JoinType.Round)
    holes = circle(2.6, 0, cy + 33.6)
    rounded = dial.offset(-1.5, m3.JoinType.Round).offset(1.5, m3.JoinType.Round)
    edge = outline(rounded, 1.3, inset=1.4) - circle(6.4 + 1.4, *tab_c)
    ticks = []
    for i, a in enumerate(np.arange(180, -0.1, -15)):
        major = i % 2 == 0
        u = np.array([np.cos(np.radians(a)), np.sin(np.radians(a))])
        ticks.append(stroke([u * (20.6 if major else 23.2) + (0, cy), u * 26.2 + (0, cy)], 1.4 if major else 1.1))
    na = np.radians(36.0)
    d = np.array([np.cos(na), np.sin(na)])
    side = np.array([-np.sin(na), np.cos(na)]) * 1.5
    needle = polygon([(0, cy) + side, d * 18.5 + (0, cy), (0, cy) - side, (0, cy) - d * 4.5])
    needle = needle + stroke([(0, cy), d * 18.2 + (0, cy)], 1.0)   # uç en az 1 mm
    hub = circle(3.6, 0, cy) - circle(1.3, 0, cy)
    auto = auto_text(5.4, -1.5, cy + 12.4)
    name = name_text(8.0, 0, cy - 8.6, max_w=46.0)
    phone = small_text(PHONE, 3.6, 0, cy - 16.4)
    city = small_text(CITY, 3.0, 0, cy - 21.6, tracking=0.9)
    raised = [(edge, YELLOW), (union(*ticks), WHITE), (needle, YELLOW), (hub, YELLOW), (auto, YELLOW),
              (name, WHITE), (phone, WHITE), (city, WHITE)]
    return Design("7_kilometre_saati", "AUTO_FIRAT_TUYGUN_kilometre", base, raised, holes, "3 renk")


QR_DATA = "TEL:+905352783529"   # okutunca galeriyi arar (büyük harf: QR'da daha az modül)


def d8_qr_kart():
    """Modern: okutunca arayan QR kodlu dikey kart; beyaz QR zemini, siyah oyma modüller."""
    W, H = 54.0, 90.0
    base = rrect(W, H, 7.0)
    holes = circle(2.6, 0, H / 2 - 7.2)
    frame = outline(rrect(W - 4.2, H - 4.2, 5.0), 1.3)
    auto = auto_text(4.8, 0, 29.0)
    name = name_text(8.0, 0, 19.6, max_w=W - 9.0)
    light, size = qr_light(QR_DATA, 1.6, 0, -6.6)
    phone = small_text(PHONE, 3.8, 0, -31.2, max_w=W - 10.0)
    city = small_text(CITY, 3.2, 0, -37.0, tracking=0.9)
    raised = [(frame, YELLOW), (auto, YELLOW), (name, WHITE), (light, WHITE), (phone, YELLOW), (city, WHITE)]
    d = Design("8_qr_kart", "AUTO_FIRAT_TUYGUN_qr", base, raised, holes, "3 renk")
    d.qr = (QR_DATA, size)
    return d


def d9_direksiyon():
    """Modern: üç kollu direksiyon; gerçek açıklıklar (anahtarlık halkası üst açıklıktan geçer)."""
    R, Ri = 33.0, 24.6
    band = rect(-R, -7.6, R, 7.6)
    spoke = rect(-7.4, -R, 7.4, 0)
    hub = circle(10.5, 0, 0)
    openings = circle(Ri, 0, 0, 180) - band - spoke - hub
    holes = openings.offset(-2.2, m3.JoinType.Round).offset(2.2, m3.JoinType.Round)
    base = circle(R, 0, 0, 180)
    rim_line = outline(circle(R, 0, 0, 180), 1.1, inset=1.1)
    city = font("small").arc(CITY, 3.6, 0, 0, Ri + 1.6, 90.0, top=True, tracking=1.0)
    phone = font("small").arc(PHONE, 3.6, 0, 0, R - 3.6, -90.0, top=False, tracking=0.25)
    name = name_text(7.8, 0, 0.0, max_w=2 * Ri - 3.0)
    auto = auto_text(4.4, 0, -15.0)
    raised = [(rim_line, YELLOW), (city, YELLOW), (phone, YELLOW), (name, YELLOW), (auto, YELLOW)]
    return Design("9_direksiyon", "AUTO_FIRAT_TUYGUN_direksiyon", base, raised, holes, "2 renk")


def d10_hiz_cizgileri():
    """Modern: eğik (paralelkenar) kart; hız çizgileri, italik isim, telefon."""
    k = 14.0
    W, H = 92.0, 32.0
    base = shear(rrect(W, H, 5.0), k)
    holes = circle(2.6, -38.0, 0.0)
    lines = union(*[stroke([(x0, y), (x1, y)], 1.5) for x0, x1, y in
                    [(-31.0, -17.0, 6.0), (-31.5, -13.5, 0.0), (-30.0, -19.5, -6.0)]])
    lines = shear(lines, k)
    auto = shear(auto_text(4.2, -8.6, 10.0, align="l"), k)
    city = shear(small_text(CITY, 3.4, 37.2, 10.0, align="r", tracking=0.8), k)
    name = shear(name_text(9.4, -9.0, 1.2, max_w=48.0, align="l"), k)
    phone = shear(small_text(PHONE, 3.7, -8.6, -9.4, align="l", max_w=46.0), k)
    edge = shear(outline(rrect(W, H, 5.0), 1.2, inset=1.4), k) - circle(2.6 + 2.4, -38.0, 0.0)
    raised = [(edge, YELLOW), (lines, YELLOW), (auto, YELLOW), (city, WHITE), (name, WHITE), (phone, YELLOW)]
    return Design("10_hiz_cizgileri", "AUTO_FIRAT_TUYGUN_hiz", base, raised, holes, "3 renk")


def d11_damali_bayrak():
    """Modern: sağa doğru pikselleşerek açılan damalı bayrak; solda iki satır isim."""
    W, H = 86.0, 48.0
    base = rrect(W, H, 6.0)
    holes = circle(2.6, W / 2 - 7.4, H / 2 - 7.4)
    frame = outline(rrect(W - 3.6, H - 3.6, 4.4), 1.2)
    pitch, x_start, x_end = 3.6, 2.0, W / 2 - 3.4
    cells = []
    for i, y in enumerate(np.arange(-H / 2 + 3.4 + pitch / 2, H / 2 - 3.4, pitch)):
        for j, x in enumerate(np.arange(x_start + pitch / 2, x_end, pitch)):
            if (i + j) % 2:
                continue
            t = (x - x_start) / (x_end - x_start)            # 0 solda, 1 sağda
            side = pitch * (0.32 + 0.48 * t)                   # sola doğru küçülen kareler
            if side < 1.3:
                continue
            cells.append(rect(x - side / 2, y - side / 2, x + side / 2, y + side / 2))
    flag = union(*cells) ^ rrect(W - 3.6 - 2.6 - 1.6, H - 3.6 - 2.6 - 1.6, 3.0)
    flag = flag - circle(2.6 + 2.2, W / 2 - 7.4, H / 2 - 7.4)
    flag = union(*[p for p in flag.decompose() if p.area() > 1.2])
    x0 = -W / 2 + 6.0
    auto = auto_text(4.4, x0, 15.6, align="l")
    first = font("bebas").text("FIRAT", 10.6, x0, 5.0, align="l")
    last = font("bebas").text("TUYGUN", 10.6, x0, -8.0, align="l")
    phone = small_text(PHONE, 3.6, x0, -17.4, align="l")
    raised = [(frame, YELLOW), (flag, YELLOW), (auto, YELLOW), (first, YELLOW), (last, YELLOW), (phone, YELLOW)]
    return Design("11_damali_bayrak", "AUTO_FIRAT_TUYGUN_bayrak", base, raised, holes, "2 renk")


def d12_kalkan_amblem():
    """Modern: kalkan amblem; büyük FT monogramı, yan şeritler, isim ve telefon; üstte askı kulağı."""
    half = [(0, 33.4), (14, 32.6), (25.6, 30.6), (29.2, 26.4), (29.6, 12.0), (28.6, -6.0), (25.8, -20.0),
            (19.6, -31.0), (10.4, -38.6), (0, -42.4)]
    pts = half + [(-x, y) for x, y in reversed(half[1:-1])]
    shield = polygon(smooth(np.array(pts), closed=True, n=400))
    tab_c = (0, 37.6)
    base = (shield + circle(6.4, *tab_c)).offset(1.4, m3.JoinType.Round).offset(-1.4, m3.JoinType.Round)
    holes = circle(2.6, 0, 38.0)
    edge = outline(shield, 1.3, inset=1.6)
    auto = auto_text(4.8, 0, 22.4)
    mono = font("bebas").text("FT", 19.0, 0, 6.6, tracking=0.6)
    mx0, _, mx1, _ = mono.bounds()
    stripes = union(*[stroke([(sgn * (mx1 + 2.6), y), (sgn * 21.5, y)], 1.4)
                      for sgn in (-1, 1) for y in (9.8, 6.6, 3.4)])
    name = name_text(7.8, 0, -9.8, max_w=46.0)
    phone = small_text(PHONE, 3.5, 0, -20.0, max_w=40.0)
    city = small_text(CITY, 3.0, 0, -27.0, tracking=0.9)
    raised = [(edge, YELLOW), (auto, YELLOW), (mono, WHITE), (stripes, YELLOW), (name, WHITE),
              (phone, YELLOW), (city, WHITE)]
    return Design("12_kalkan_amblem", "AUTO_FIRAT_TUYGUN_kalkan", base, raised, holes, "3 renk")


DESIGNS = [d1_klasik, d2_araba, d3_araba_cam, d4_plaka, d5_araba_anahtari, d6_lastik_rozet, d7_kilometre_saati,
           d8_qr_kart, d9_direksiyon, d10_hiz_cizgileri, d11_damali_bayrak, d12_kalkan_amblem, d13_plaka_klasik]


# ---------------------------------------------------------------- 3MF

# X2D proje ayarlarında filament başına değil, ekstrüder başına olan 2 elemanlı listeler
EXTRUDER_KEYS = {"default_nozzle_volume_type", "extruder_colour", "extruder_max_nozzle_count", "extruder_offset",
                 "extruder_printable_area", "extruder_printable_height", "extruder_type", "extruder_variant_list",
                 "flush_multiplier", "flush_multiplier_fast", "grab_length", "machine_min_extruding_rate",
                 "machine_min_travel_rate", "max_layer_height", "min_layer_height", "nozzle_diameter",
                 "nozzle_volume_type", "physical_extruder_map", "start_end_points"}
# filament değiştirirken temizleme hacmi (mm³): [kimden][kime] siyah, sarı, beyaz, mavi
FLUSH = [[0, 700, 900, 500], [90, 0, 300, 200], [90, 200, 0, 150], [90, 600, 600, 0]]


def project_settings(template_files, filaments):
    """Şablon (2 filamentli X2D) ayarlarını `filaments` listesindeki filamentlere uyarlar.
    Ek filamentler 2. filamentin (Bambu PLA Basic) ayarlarını kopyalar."""
    cfg = json.loads(template_files["Metadata/project_settings.config"])
    n_old, n = len(cfg["filament_colour"]), len(filaments)
    self_idx = [int(v) for v in cfg["filament_self_index"]]
    n_var = len(self_idx)
    src = [i for i, v in enumerate(self_idx) if v == n_old]          # son filamentin varyant blokları
    for k, v in list(cfg.items()):
        if not isinstance(v, list) or k in EXTRUDER_KEYS:
            continue
        if len(v) == n_old:
            cfg[k] = (v + [v[-1]] * n)[:n]
        elif len(v) == n_var and k != "filament_self_index" and not k.startswith(("machine_", "flush_")):
            blocks = [[v[i] for i, s in enumerate(self_idx) if s == f] for f in range(1, n_old + 1)]
            blocks += [[v[i] for i in src]] * max(0, n - n_old)
            cfg[k] = [x for b in blocks[:n] for x in b]
    per = len(src)
    cfg["filament_self_index"] = [str(f) for f in range(1, n + 1) for _ in range(per)]
    nozzles = len(cfg["nozzle_diameter"])
    one = [str(FLUSH[a - 1][b - 1]) for a in filaments for b in filaments]
    cfg["flush_volumes_matrix"] = one * nozzles
    cfg["filament_colour"] = [COLOURS[f] + "FF" for f in filaments]
    return json.dumps(cfg, indent=4).encode()


def model_xml(title, parts, today):
    comps = "".join(
        f'    <component p:path="/3D/Objects/object_1.model" objectid="{i}" '
        f'p:UUID="000{i}0000-b206-40ff-9872-83e8017abed1" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n'
        for i in range(1, len(parts) + 1))
    pid = len(parts) + 1
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">
 <metadata name="Application">BambuStudio-02.07.01.57</metadata>
 <metadata name="BambuStudio:3mfVersion">1</metadata>
 <metadata name="CreationDate">{today}</metadata>
 <metadata name="ModificationDate">{today}</metadata>
 <metadata name="Title">{title}</metadata>
 <resources>
  <object id="{pid}" p:UUID="0000000{pid}-61cb-4c03-9d28-80fed5dfa1dc" type="model">
   <components>
{comps}   </components>
  </object>
 </resources>
 <build p:UUID="2c7c17d8-22b5-4d84-8835-1976022ea369">
  <item objectid="{pid}" p:UUID="00000002-b1ec-4553-aec9-835e5b724bb4" transform="1 0 0 0 1 0 0 0 1 {BED_CENTER[0]} {BED_CENTER[1]} 0" printable="1"/>
 </build>
</model>
"""


def settings_xml(title, parts):
    pid = len(parts) + 1
    out = ['<?xml version="1.0" encoding="UTF-8"?>\n<config>\n', f'  <object id="{pid}">\n',
           f'    <metadata key="name" value="{title}"/>\n', '    <metadata key="extruder" value="1"/>\n',
           '    <metadata key="wall_generator" value="arachne"/>\n',
           f'    <metadata face_count="{sum(len(t) for _, _, t, _ in parts)}"/>\n']
    for i, (name, V, T, ext) in enumerate(parts, 1):
        out += [f'    <part id="{i}" subtype="normal_part">\n',
                f'      <metadata key="name" value="{name}"/>\n',
                '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n',
                f'      <metadata key="extruder" value="{ext}"/>\n',
                f'      <mesh_stat face_count="{len(T)}" edges_fixed="0" degenerate_facets="0" '
                'facets_removed="0" facets_reversed="0" backwards_edges="0"/>\n', '    </part>\n']
    out += ['  </object>\n', '  <plate>\n', '    <metadata key="plater_id" value="1"/>\n',
            '    <metadata key="plater_name" value="Plate 1"/>\n', '    <metadata key="locked" value="false"/>\n',
            '    <metadata key="filament_map_mode" value="Auto For Flush"/>\n',
            '    <metadata key="gcode_file" value=""/>\n',
            '    <metadata key="thumbnail_file" value="Metadata/plate_1.png"/>\n',
            '    <metadata key="thumbnail_no_light_file" value="Metadata/plate_no_light_1.png"/>\n',
            '    <metadata key="top_file" value="Metadata/top_1.png"/>\n',
            '    <metadata key="pick_file" value="Metadata/pick_1.png"/>\n',
            '    <model_instance>\n', f'      <metadata key="object_id" value="{pid}"/>\n',
            '      <metadata key="instance_id" value="0"/>\n',
            f'      <metadata key="identify_id" value="{PICK_ID}"/>\n', '    </model_instance>\n',
            '  </plate>\n', '  <assemble>\n  </assemble>\n</config>\n']
    return "".join(out)


def mesh_arrays(man):
    mesh = man.to_mesh()
    return np.asarray(mesh.vert_properties)[:, :3].astype(float), np.asarray(mesh.tri_verts).astype(int)


R_ISO = rotation(0, -52)
R_TOP = rotation(0, 0)


def fit_into(im, w, h):
    """Şeffaf kenarları kırpıp görseli w x h kutusuna sığdırır."""
    im = im.crop(im.getbbox())
    k = min(w / im.width, h / im.height)
    return im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)


def write_design(d, template_files, out_dir):
    solids = d.solids()
    used = [ext for _, _, ext in solids]
    filaments = sorted(set(used))
    fil_no = {f: i + 1 for i, f in enumerate(filaments)}            # projedeki filament sırası
    parts = [(name, *mesh_arrays(m), fil_no[ext]) for name, m, ext in solids]
    shaded = [(V, T, SHOW[ext]) for (_, V, T, _), ext in zip(parts, used)]
    plate = render(shaded, 512, R_ISO)
    world = [(V + (*BED_CENTER, 0), T, c) for V, T, c in shaded]
    images = {
        "Metadata/plate_1.png": plate,
        "Metadata/plate_1_small.png": plate.resize((128, 128), Image.LANCZOS),
        "Metadata/plate_no_light_1.png": render(shaded, 512, R_ISO, light=False),
        "Metadata/pick_1.png": render([(V, T, (PICK_ID, 0, 0)) for V, T, _ in shaded], 512, R_ISO, light=False, ss=1),
        "Metadata/top_1.png": render(world, 512, R_TOP, flat=0.7, margin=0.2),
    }
    today = datetime.date.today().isoformat()
    files = {k: v for k, v in template_files.items() if k.startswith(("[Content_Types]", "_rels/", "3D/_rels/"))}
    for k in ("Metadata/slice_info.config", "Metadata/cut_information.xml"):
        files[k] = template_files[k]
    files["Metadata/filament_sequence.json"] = b'{"plate_1":{"nozzle_sequence":[],"optimal_assignment":[],"sequence":[]}}'
    files["Metadata/project_settings.config"] = project_settings(template_files, filaments)
    files["3D/3dmodel.model"] = model_xml(d.title, parts, today).encode()
    head = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
            'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
            'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
            'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n'
            ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n <resources>\n')
    body = "".join(mesh_xml(i, f"000{i}0000-81cb-4c03-9d28-80fed5dfa1dc", V, T)
                   for i, (_, V, T, _) in enumerate(parts, 1))
    files["3D/Objects/object_1.model"] = (head + body + " </resources>\n <build/>\n</model>\n").encode()
    files["Metadata/model_settings.config"] = settings_xml(d.title, parts).encode()
    for name, im in images.items():
        buf = io.BytesIO()
        im.save(buf, "PNG")
        files[name] = buf.getvalue()
    order = ["[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model", "3D/_rels/3dmodel.model.rels"]
    path = os.path.join(out_dir, d.key + ".3mf")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for k in order + sorted(k for k in files if k not in order):
            z.writestr(k, files[k])
    return path, shaded, filaments


# ---------------------------------------------------------------- önizleme

def preview(d, shaded, filaments, path):
    W, H = 1400, 620
    canvas = Image.new("RGB", (W, H), (236, 239, 244))
    dr = ImageDraw.Draw(canvas)
    top = fit_into(render(shaded, 900, R_TOP, margin=0.02), 580, 460)
    iso = fit_into(render(shaded, 900, R_ISO, margin=0.02), 580, 460)
    for i, im in enumerate((top, iso)):
        x = 40 + i * 680
        dr.rounded_rectangle((x, 70, x + 640, 70 + 520), 22, fill=(126, 134, 148))
        canvas.paste(im, (x + (640 - im.width) // 2, 70 + (520 - im.height) // 2), im)
    try:
        f = ImageFont.truetype(os.path.join(FONT_DIR, "Lexend-ExtraBold.ttf"), 30)
        fs = ImageFont.truetype(os.path.join(FONT_DIR, "Lexend-ExtraBold.ttf"), 21)
    except OSError:
        f = fs = ImageFont.load_default()
    w, h = d.size()
    dr.text((40, 18), d.key.replace("_", " ").upper(), fill=(30, 33, 40), font=f)
    x = W - 40
    for ext in reversed(filaments):                          # renk kutucukları
        label = f"{filaments.index(ext) + 1}: {COLOUR_NAMES[ext]}"
        x -= dr.textlength(label, font=fs)
        dr.text((x, 24), label, fill=(70, 76, 88), font=fs)
        x -= 30
        dr.rounded_rectangle((x, 24, x + 22, 46), 5, fill=SHOW[ext], outline=(90, 96, 108), width=2)
        x -= 22
    info = f"{w:.0f} × {h:.0f} × {BASE_H + RAISE_H:.1f} mm"
    x -= dr.textlength(info, font=fs) + 10
    dr.text((x, 24), info, fill=(70, 76, 88), font=fs)
    canvas.save(path)
    return canvas


def contact_sheet(images, path, cols=2):
    tw = 700
    thumbs = [im.resize((tw, int(im.height * tw / im.width)), Image.LANCZOS) for im in images]
    th = thumbs[0].height
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * 20, rows * th + (rows + 1) * 20), (250, 250, 252))
    for i, im in enumerate(thumbs):
        sheet.paste(im, (20 + (i % cols) * (tw + 20), 20 + (i // cols) * (th + 20)))
    sheet.save(path)


def main():
    only = sys.argv[1:]
    template = zipfile.ZipFile(TEMPLATE)
    template_files = {n: template.read(n) for n in template.namelist()}
    os.makedirs(os.path.join(OUT_DIR, "onizleme"), exist_ok=True)
    previews = []
    for fn in DESIGNS:
        d = fn()
        if only and not any(o in d.key for o in only):
            continue
        path, shaded, filaments = write_design(d, template_files, OUT_DIR)
        w, h = d.size()
        thin, gaps, area = d.check()
        thin, gaps = thin.area(), gaps.area()
        pairs, wall = d.check_pairs(), d.hole_wall()
        extra = ""
        if getattr(d, "qr", None):
            ok, text = qr_decodes(d, d.qr[0])
            extra = f"  QR {'okundu' if ok else 'OKUNAMADI'} ({text!r}, {d.qr[1]:.1f} mm)"
        print(f"{d.key:20s} {w:5.1f} x {h:5.1f} mm  {'+'.join(COLOUR_NAMES[f] for f in filaments):18s} "
              f"ince<{MIN_FEATURE}mm: {thin:4.1f} mm²  dar boşluk<{MIN_GAP}mm: {gaps:4.1f} mm²  "
              f"yakın öğe: {pairs or 'yok'}  delik et payı: {wall} mm{extra}")
        previews.append(preview(d, shaded, filaments, os.path.join(OUT_DIR, "onizleme", d.key + ".png")))
    if not only:
        contact_sheet(previews, os.path.join(OUT_DIR, "onizleme", "hepsi.png"))
        contact_sheet(previews[7:], os.path.join(OUT_DIR, "onizleme", "yeni_tasarimlar.png"))
        plates = [im for d_, im in zip(DESIGNS, previews) if "plaka" in d_.__name__]
        contact_sheet(plates, os.path.join(OUT_DIR, "onizleme", "plakalar.png"), cols=1)


if __name__ == "__main__":
    main()
