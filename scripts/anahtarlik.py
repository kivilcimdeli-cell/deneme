"""AUTO FIRAT TUYGUN anahtarlıkları: siyah gövde + sarı kabartma, Bambu Lab 3MF.

Her tasarım iki parçadan oluşur ve tek seferde basılır:
  * Gövde      : siyah (filament 1), 3,2 mm
  * Kabartma   : sarı  (filament 2), gövdenin üstünde 1,0 mm (yazılar, çizgiler, çerçeve)

Yazıcı/filament/baskı ayarları `isimlik/orijinal/...3mf` içindeki Bambu Lab X2D
projesinden alınır; filament renkleri siyah ve sarı yapılır.

Çıktı : anahtarlik/<tasarım>.3mf, anahtarlik/onizleme/<tasarım>.png, anahtarlik/onizleme/hepsi.png

Kullanım:
  pip install numpy manifold3d pillow shapely scipy fonttools uharfbuzz
  python3 scripts/anahtarlik.py
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

BLACK = "#000000"
YELLOW = "#F4EE2A"   # Bambu PLA Basic Yellow
BASE_H = 3.2         # siyah gövde kalınlığı (mm)
RAISE_H = 1.0        # sarı kabartma yüksekliği (mm)
LINE = 1.2           # sarı çizgi kalınlığı (mm), 0.4 nozul için en az ~3 çizgi
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
        """`max_w`'ya sığacak en büyük yazı yüksekliği (en fazla `cap`)."""
        w = self.width(text, cap, tracking)
        return cap if w <= max_w else cap * max_w / w

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


def font(name):
    files = {"bebas": "BebasNeue-Regular.ttf", "mont": "Montserrat-Bold.ttf",
             "barlow": "BarlowCondensed-ExtraBold.ttf"}
    if name not in FONTS:
        FONTS[name] = Font(files[name])
    return FONTS[name]


# ---------------------------------------------------------------- tasarım

@dataclass
class Design:
    key: str                 # dosya adı
    title: str               # Bambu Studio'daki nesne adı
    base: m3.CrossSection    # siyah gövde dış hattı
    raised: m3.CrossSection  # sarı kabartma
    holes: m3.CrossSection = field(default_factory=empty)  # anahtarlık deliği

    def solids(self):
        body = self.base - self.holes
        raised = (self.raised ^ body) - self.holes.offset(0.6, m3.JoinType.Round)
        # kabartmada 0.4 nozulun basamayacağı kıl payı parçaları at
        raised = union(*[p for p in raised.decompose() if p.area() > 0.4])
        x0, y0, x1, y1 = body.bounds()
        c = (-(x0 + x1) / 2, -(y0 + y1) / 2)
        govde = body.translate(c).extrude(BASE_H)
        kabartma = raised.translate(c).extrude(RAISE_H).translate((0, 0, BASE_H))
        return govde, kabartma

    def size(self):
        x0, y0, x1, y1 = self.base.bounds()
        return x1 - x0, y1 - y0


# ---------------------------------------------------------------- araba profili

CAR_PTS = [(8, 4.4), (3.4, 5.0), (0.8, 7.6), (0.3, 11.5), (1.0, 15.6), (4.5, 18.6), (16, 21.2),
           (30, 23.4), (39, 27.8), (47.5, 31.2), (57, 32.4), (67, 31.4), (77, 28.4), (85.5, 25.8),
           (90.3, 27.0), (91.9, 24.4), (92.0, 16.0), (91.0, 9.8), (88.4, 5.6), (81, 4.4),
           (60, 4.1), (33, 4.1)]
CAR_WHEELS = [(20.0, 6.0), (71.5, 6.0)]
CAR_WR = 6.6


def car_profile(length=100.0):
    """Yandan spor coupe silueti (ön solda), 92 birimlik çizimden `length` mm'ye ölçeklenir.
    Döner: gövde (tekerleksiz), tekerlekler, tekerlek merkezleri, yarıçap, ölçek."""
    s = length / 92.0
    body = polygon(smooth(np.array(CAR_PTS) * s, closed=True, n=400))
    wheels_c = [(x * s, y * s) for x, y in CAR_WHEELS]
    wr = CAR_WR * s
    wheels = union(*[circle(wr, x, y) for x, y in wheels_c])
    return body, wheels, wheels_c, wr, s


def car_silhouette(length=100.0):
    body, wheels, wc, wr, s = car_profile(length)
    shape = (body + wheels).offset(1.6 * s, m3.JoinType.Round).offset(-1.6 * s, m3.JoinType.Round)
    return shape, body, wc, wr, s


def car_lineart(length):
    """Çizgi araba: gövde konturu + açık tekerlek kemerleri + tekerlekler + cam çizgisi."""
    body, _, wc, wr, s = car_profile(length)
    arches = union(*[circle(wr + 1.3 * s, x, y) for x, y in wc])
    lines = outline(body - arches, 1.05)
    window = smooth(np.array([(34.5, 23.6), (44.0, 27.4), (56.5, 28.8), (67.5, 27.6), (80.5, 23.9)]) * s)
    lines = lines + stroke(window, 1.05)
    wheels = union(*[outline(circle(wr - 0.4 * s, x, y), 1.05) for x, y in wc])
    return lines + wheels, s


# ---------------------------------------------------------------- tasarımlar

def d1_klasik():
    """Fotoğraf 1: yuvarlak köşeli kart, çerçeve, çizgi araba, AUTO, isim, telefon, şehir."""
    W, H = 84.0, 58.0
    base = rrect(W, H, 6.0)
    frame = outline(rrect(W - 4.2, H - 4.2, 4.4), 1.4)
    holes = circle(2.4, W / 2 - 7.8, H / 2 - 7.8)
    art, s = car_lineart(62.0)
    ax0, ay0, ax1, ay1 = art.bounds()
    dx, dy = -(ax0 + ax1) / 2 - 2.0, H / 2 - 5.2 - ay1
    art = art.translate((dx, dy))
    auto = font("bebas").text("AUTO", 5.8, 46.0 * s + dx, 14.2 * s + dy)
    name = font("bebas").text(NAME, font("bebas").fit_cap(NAME, 11.0, W - 16), 0, -3.4)
    phone = font("mont").text(PHONE, 4.2, 0, -13.6)
    city = font("mont").text(CITY, 3.6, 0, -19.8)
    raised = union(frame, art, auto, name, phone, city)
    return Design("1_klasik_kart", "AUTO_FIRAT_TUYGUN_klasik", base, raised, holes)


def _car_common(length):
    shape, body, wc, wr, s = car_silhouette(length)
    hole_c = (84.6 * s, 18.0 * s)
    holes = circle(2.5, *hole_c)
    # iç kontur çizgisi: deliğin etrafından dolaşır, alttaki tekerlek hizasında biter
    inner = shape.offset(-1.9, m3.JoinType.Round) - circle(2.5 + 2.2, *hole_c)
    ring = outline(inner, LINE) ^ rect(-50, 11.0 * s, 200, 100)
    name = font("bebas").text(NAME, 8.4, 41.5 * s, 13.6 * s)
    phone = font("mont").text(PHONE, 3.3, 41.5 * s, 6.9 * s)
    city = font("mont").text(CITY, 2.8, 78.0 * s, 8.6 * s)
    return shape, holes, union(ring, name, phone, city), s


def d2_araba():
    """Fotoğraf 2: araba silueti, büyük cam içinde AUTO, kavisli far çizgileri."""
    shape, holes, common, s = _car_common(100.0)
    win = stroke(smooth(np.array([(36.0, 23.9), (44.5, 28.6), (56.0, 30.0), (67.0, 29.2), (76.5, 26.2),
                                  (68.5, 24.0), (52.0, 23.4)]) * s, closed=True), LINE, closed=True)
    auto = font("bebas").text("AUTO", 3.8, 56.5 * s, 26.6 * s)
    head1 = stroke(smooth(np.array([(3.6, 16.2), (7.4, 16.9), (11.6, 15.8)]) * s), LINE)
    head2 = stroke(np.array([(3.2, 10.6), (6.6, 10.8), (7.8, 8.2)]) * s, LINE)
    raised = union(common, win, auto, head1, head2)
    return Design("2_araba_silueti", "AUTO_FIRAT_TUYGUN_araba", shape, raised, holes)


def d3_araba_cam():
    """Fotoğraf 3: araba silueti, direkli yan cam içinde küçük AUTO, köşeli far çizgileri."""
    shape, holes, common, s = _car_common(100.0)
    win = stroke(np.array([(41.0, 24.0), (48.5, 29.0), (58.5, 30.1), (68.0, 29.1), (75.0, 25.6),
                           (41.0, 24.0)]) * s, LINE, closed=True)
    pillar = stroke(np.array([(55.6, 24.6), (53.2, 29.8)]) * s, LINE)
    auto = font("bebas").text("AUTO", 3.1, 64.6 * s, 26.9 * s)
    head1 = stroke(np.array([(3.2, 16.0), (8.6, 17.8), (13.0, 17.8)]) * s, LINE)
    head2 = stroke(np.array([(4.4, 13.6), (10.2, 15.0)]) * s, LINE)
    head3 = stroke(np.array([(3.0, 10.2), (6.9, 10.4), (8.4, 7.8)]) * s, LINE)
    raised = union(common, win, pillar, auto, head1, head2, head3)
    return Design("3_araba_yan_cam", "AUTO_FIRAT_TUYGUN_araba_2", shape, raised, holes)


def d4_plaka():
    """Yeni: Türk plakası görünümü; solda TR şeridi, 07 (Antalya) + isim, altta telefon."""
    W, H = 96.0, 30.0
    base = rrect(W, H, 3.6)
    frame = outline(rrect(W - 3.2, H - 3.2, 2.4), 1.2)
    sx0, sx1 = -W / 2 + 1.6, -W / 2 + 13.6
    strip = rrect(sx1 - sx0, H - 3.2, 2.4, (sx0 + sx1) / 2, 0) ^ rect(sx0, -H, sx1 - 0.0, H)
    tr = font("barlow").text("TR", 5.2, (sx0 + sx1) / 2, -6.6)
    holes = circle(2.4, (sx0 + sx1) / 2, 5.6)
    strip = strip - tr.offset(0.05, m3.JoinType.Round)
    main_w = W / 2 - 3.6 - (sx1 + 2.0)
    main = "07 " + NAME
    cap = font("barlow").fit_cap(main, 10.5, main_w)
    name = font("barlow").text(main, cap, (sx1 + 2.0 + W / 2 - 3.6) / 2, 3.4)
    line2 = f"{PHONE}  ·  {CITY}"
    phone = font("mont").text(line2, font("mont").fit_cap(line2, 3.3, main_w), (sx1 + 2.0 + W / 2 - 3.6) / 2, -8.2)
    raised = union(frame, strip, name, phone)
    return Design("4_plaka", "AUTO_FIRAT_TUYGUN_plaka", base, raised, holes)


def d5_araba_anahtari():
    """Yeni (galeri): araba anahtarı; kumanda gövdesinde isim, anahtar dilinde telefon."""
    fob = rrect(60.0, 34.0, 11.0, -25.0, 0)
    shoulder = rrect(9.0, 19.0, 3.0, 8.0, 0)
    bottom = [(4, -6.2), (12, -6.2), (14, -4.6), (17, -6.2), (21, -6.2), (23.5, -4.4), (26.5, -6.2),
              (30, -6.2), (32, -4.8), (35, -6.2), (38.5, -6.2), (40.5, -4.8), (42.5, -6.2)]
    blade = polygon([(4, 6.2), (44.0, 6.2), (49.5, 2.4), (49.5, -2.4), (46.5, -6.2)] + bottom[::-1])
    base = union(fob, shoulder, blade)
    holes = circle(2.6, -48.6, 0.0)
    panel = rrect(45.5, 27.6, 7.5, -19.6, 0)
    ring = outline(panel, LINE)
    collar = outline(shoulder, LINE, inset=1.1)
    groove = stroke(np.array([(11.5, 3.9), (43.0, 3.9)]), 0.9)
    auto = font("bebas").text("AUTO", 4.6, -19.6, 7.9)
    name = font("bebas").text(NAME, font("bebas").fit_cap(NAME, 7.8, 39.0), -19.6, -0.6)
    city = font("mont").text(CITY, 2.8, -19.6, -8.4)
    phone = font("mont").text(PHONE, font("mont").fit_cap(PHONE, 3.3, 31.0), 29.2, -1.0)
    raised = union(ring, collar, groove, auto, name, city, phone)
    return Design("5_araba_anahtari", "AUTO_FIRAT_TUYGUN_anahtar", base, raised, holes)


def d7_kilometre_saati():
    """Yeni (galeri): kilometre saati; çentikli kadran, ibre, AUTO, isim, telefon, şehir."""
    cy = 4.0
    dial = circle(31.0, 0, cy, 160) ^ rect(-40, -22.0, 40, 50)
    tab = circle(6.2, 0, cy + 33.4)
    base = (dial + tab).offset(1.5, m3.JoinType.Round).offset(-3.0, m3.JoinType.Round).offset(1.5, m3.JoinType.Round)
    holes = circle(2.4, 0, cy + 33.6)
    edge = outline(dial.offset(-1.5, m3.JoinType.Round).offset(1.5, m3.JoinType.Round), LINE, inset=1.6)
    edge = edge - circle(6.2 + 1.2, 0, cy + 33.4)
    ticks = []
    for i, a in enumerate(np.arange(180, -0.1, -15)):
        r0 = 21.0 if i % 2 == 0 else 23.5
        u = np.array([np.cos(np.radians(a)), np.sin(np.radians(a))])
        ticks.append(stroke([u * r0 + (0, cy), u * 28.8 + (0, cy)], 1.25 if i % 2 == 0 else 1.0))
    na = np.radians(38.0)
    tip = np.array([np.cos(na), np.sin(na)]) * 19.5 + (0, cy)
    side = np.array([-np.sin(na), np.cos(na)]) * 1.4
    needle = polygon([(0, cy) + side, tip, (0, cy) - side, (0, cy) - np.array([np.cos(na), np.sin(na)]) * 4.0])
    hub = circle(3.4, 0, cy) - circle(1.2, 0, cy)
    auto = font("bebas").text("AUTO", 5.6, -1.0, cy + 13.0)
    name = font("bebas").text(NAME, font("bebas").fit_cap(NAME, 7.6, 46.0), 0, cy - 8.4)
    phone = font("mont").text(PHONE, 3.2, 0, cy - 16.1)
    city = font("mont").text(CITY, 2.7, 0, cy - 21.0)
    raised = union(edge, union(*ticks), needle, hub, auto, name, phone, city)
    return Design("7_kilometre_saati", "AUTO_FIRAT_TUYGUN_kilometre", base, raised, holes)


def d6_lastik_rozet():
    """Yeni: lastik/jant rozeti; dişli lastik halkası, üstte ANTALYA, ortada isim, altta telefon."""
    R = 31.0
    base = circle(R, 0, 0, 160) + circle(6.2, 0, R + 2.6) 
    base = base.offset(1.2, m3.JoinType.Round).offset(-1.2, m3.JoinType.Round)
    holes = circle(2.4, 0, R + 2.8)
    tire = circle(R - 1.4, 0, 0, 160) - circle(R - 5.0, 0, 0, 160)
    grooves = union(*[rect(-0.75, R - 3.2, 0.75, R + 2).rotate(a) for a in np.arange(0, 360, 360 / 36)])
    tire = tire - grooves - circle(6.2 + 1.0, 0, R + 2.6)
    rim = outline(circle(R - 6.2, 0, 0, 160), LINE)
    city = font("mont").arc(CITY, 3.2, 0, 0, R - 11.6, 90.0, top=True, tracking=0.6)
    phone = font("mont").arc(PHONE, 3.0, 0, 0, R - 8.4, -90.0, top=False, tracking=0.25)
    auto = font("bebas").text("AUTO", 5.0, 0, 11.2)
    first = font("bebas").text("FIRAT", 9.0, 0, 3.0)
    last = font("bebas").text("TUYGUN", font("bebas").fit_cap("TUYGUN", 9.0, 33.0), 0, -8.6)
    raised = union(tire, rim, city, phone, auto, first, last)
    return Design("6_lastik_rozet", "AUTO_FIRAT_TUYGUN_rozet", base, raised, holes)


DESIGNS = [d1_klasik, d2_araba, d3_araba_cam, d4_plaka, d5_araba_anahtari, d6_lastik_rozet, d7_kilometre_saati]


# ---------------------------------------------------------------- 3MF

def project_settings(template_files):
    cfg = json.loads(template_files["Metadata/project_settings.config"])
    cfg["filament_colour"] = [BLACK + "FF", YELLOW + "FF"]
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


SHOW = {1: (40, 40, 43), 2: (255, 226, 46)}  # önizlemede siyah ve sarının ekrandaki tonu


def shaded_parts(parts):
    return [(V, T, SHOW[ext]) for _, V, T, ext in parts]


def fit_into(im, w, h):
    """Şeffaf kenarları kırpıp görseli w x h kutusuna sığdırır."""
    im = im.crop(im.getbbox())
    k = min(w / im.width, h / im.height)
    return im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)


def write_design(d, template_files, out_dir):
    govde, kabartma = d.solids()
    parts = [("Gövde (siyah)", *mesh_arrays(govde), 1), ("Kabartma (sarı)", *mesh_arrays(kabartma), 2)]
    shaded = shaded_parts(parts)
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
    for k in ("Metadata/slice_info.config", "Metadata/filament_sequence.json", "Metadata/cut_information.xml"):
        files[k] = template_files[k]
    files["Metadata/project_settings.config"] = project_settings(template_files)
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
    return path, shaded


# ---------------------------------------------------------------- önizleme

def preview(d, shaded, path):
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
        f = ImageFont.truetype(os.path.join(FONT_DIR, "Montserrat-Bold.ttf"), 30)
        fs = ImageFont.truetype(os.path.join(FONT_DIR, "Montserrat-Bold.ttf"), 22)
    except OSError:
        f = fs = ImageFont.load_default()
    w, h = d.size()
    dr.text((40, 18), d.key.replace("_", " ").upper(), fill=(30, 33, 40), font=f)
    info = f"{w:.0f} × {h:.0f} × {BASE_H + RAISE_H:.1f} mm   ·   siyah + sarı"
    dr.text((W - 40 - dr.textlength(info, font=fs), 24), info, fill=(70, 76, 88), font=fs)
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
        path, shaded = write_design(d, template_files, OUT_DIR)
        w, h = d.size()
        print(f"{d.key:24s} {w:5.1f} x {h:5.1f} mm  -> {os.path.relpath(path, ROOT)}")
        previews.append(preview(d, shaded, os.path.join(OUT_DIR, "onizleme", d.key + ".png")))
    if not only:
        contact_sheet(previews, os.path.join(OUT_DIR, "onizleme", "hepsi.png"))


if __name__ == "__main__":
    main()
