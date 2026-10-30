"""BOYDE LABS – marka kimliği (Shopier mağazası ve Instagram hesabı için).

Ürün: QR'lı masa isimliği ve işletmeye özel dijital kartvizit sitesi; hepsi 3D baskı, kendi atölyesinde. Marka bir
3D baskı atölyesi ("Labs"); logo ürünün kendisinden çıkar.

Logo yönleri (secenekler.png), birbirinden farklı 8 yön, renkler aynı: 1 Küp, 2 Şişe, 3 Nozul, 4 Etiket, 5 Rozet,
6 Katmanlı yazı, 7 QR, 8 b ve d. 3 beğenildi ("logo daha estetik dursun"); alternatifleri secenekler_nozul.png:
  3a Sade, 3b Katman, 3c İlk çizgi, 3d Tek çizgi, 3e Daire, 3f Kare, 3g Yazar, 3h Sıcak uç.

Seçilen yönle kit (--yon 3a gibi):
  logo/       yatay, dikey, simge; açık zemin, koyu zemin, tek renk siyah / beyaz; SVG (yazılar çizgi) ve saydam PNG
  shopier/    banner 1920 × 200 ve mobil 400 × 100 (Shopier'ın önerdiği ölçüler; önemli öğeler ortada), kare logo
              800 × 800 (en az 200 × 200, kare), Hakkında kapağı 4:3, geniş görsel 16:9 (metinsiz)
  instagram/  profil fotoğrafı (yuvarlak kırpmaya göre), öne çıkan kapakları (6), gönderi şablonları (1080 × 1350:
              tanıtım, ürün, nasıl sipariş verilir), hikâye (1080 × 1920)
  kilavuz.pdf marka kılavuzu (logo, kullanım, renkler, yazı tipleri, uygulamalar, metinler); kilavuz.png önizleme

Renkler: mürekkep #121316, kâğıt #F4F1EA, Boyde turuncusu #FF5A1F, kum #E6E0D4, gri #8B8E94.
Yazı tipleri (OFL): Unbounded (logo, başlık), Space Grotesk (metin).

Kullanım:
  python3 scripts/boyde_marka.py             # yalnız seçenek sayfaları
  python3 scripts/boyde_marka.py --yon 3b    # seçenekler + 3b ile kit (seçilen)
"""
import base64
import contextlib
import io
import os
import re
import shutil
import sys

import numpy as np
import uharfbuzz as hb
from fontTools.pens.basePen import BasePen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import polygonize, unary_union

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402

OUT = os.path.join(A.ROOT, "boyde_labs")
CHROMIUM = "/opt/pw-browsers/chromium"                    # bulut ortamı; yoksa (Windows) Playwright'ın kendi
CHROMIUM = CHROMIUM if os.path.exists(CHROMIUM) else None  # tarayıcısı (playwright install chromium)
INK, PAPER, ORANGE, SAND, GRAY, CHAR = "#121316", "#F4F1EA", "#FF5A1F", "#E6E0D4", "#8B8E94", "#1C1D21"
SLOGAN = "Katman katman, size özel."
NAME = "BOYDE LABS"
FONT_FILES = {"ub3": ("Unbounded_300Light.ttf", "Unbounded", 300), "ub5": ("Unbounded_500Medium.ttf", "Unbounded", 500),
              "ub7": ("Unbounded_700Bold.ttf", "Unbounded", 700),
              "sg4": ("SpaceGrotesk_400Regular.ttf", "Space Grotesk", 400),
              "sg5": ("SpaceGrotesk_500Medium.ttf", "Space Grotesk", 500),
              "sg7": ("SpaceGrotesk_700Bold.ttf", "Space Grotesk", 700)}


# ---------------------------------------------------------------- yazıdan çizgiye

_fonts = {}


def _font(fn):
    if fn not in _fonts:
        path = os.path.join(A.FONT_DIR, fn)
        _fonts[fn] = (TTFont(path), hb.Font(hb.Face(open(path, "rb").read())))
    return _fonts[fn]


def _shaped(text, fn, size, track):
    """(glif adı, x, y) birim ölçekte ve toplam genişlik; harfbuzz (kerning)."""
    tt, hf = _font(fn)
    upm = tt["head"].unitsPerEm
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hf, buf, {"kern": True, "liga": True})
    order, s, cx, out = tt.getGlyphOrder(), size / upm, 0, []
    n = len(buf.glyph_infos)
    for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        out.append((order[info.codepoint], (cx + pos.x_offset) * s, pos.y_offset * s))
        cx += pos.x_advance + (track * upm if i < n - 1 else 0)
    return out, cx * s, s


def text_path(text, fn, size, x=0.0, y=0.0, track=0.0):
    """Metin → SVG yolu (taban çizgisi y, sol x). Döner (d, genişlik)."""
    tt, _ = _font(fn)
    gs = tt.getGlyphSet()
    glyphs, w, s = _shaped(text, fn, size, track)
    pen = SVGPathPen(gs)
    for name, gx, gy in glyphs:
        gs[name].draw(TransformPen(pen, (s, 0, 0, -s, x + gx, y - gy)))
    return pen.getCommands(), w


class _Flat(BasePen):
    """Glif → halkalar (eğriler küçük doğrularla)."""

    def __init__(self, gs):
        super().__init__(gs)
        self.rings, self.cur = [], []

    def _moveTo(self, p):
        self.cur = [p]

    def _lineTo(self, p):
        self.cur.append(p)

    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for t in np.linspace(0, 1, 14)[1:]:
            u = 1 - t
            self.cur.append(tuple(u ** 3 * np.array(p0) + 3 * u * u * t * np.array(p1) + 3 * u * t * t * np.array(p2)
                                  + t ** 3 * np.array(p3)))

    def _qCurveToOne(self, p1, p2):
        p0 = self.cur[-1]
        for t in np.linspace(0, 1, 10)[1:]:
            u = 1 - t
            self.cur.append(tuple(u * u * np.array(p0) + 2 * u * t * np.array(p1) + t * t * np.array(p2)))

    def _closePath(self):
        if len(self.cur) > 2:
            self.rings.append(self.cur)
        self.cur = []

    _endPath = _closePath


def _winding(pt, ring):
    """Noktanın halka etrafındaki sarım sayısı (işaretli kesişimler; halka kendini kesebilir)."""
    x, y = pt
    r = np.asarray(ring, float)
    a, b = r, np.roll(r, -1, axis=0)
    up = (a[:, 1] <= y) & (b[:, 1] > y)
    down = (a[:, 1] > y) & (b[:, 1] <= y)
    cross = (b[:, 0] - a[:, 0]) * (y - a[:, 1]) - (x - a[:, 0]) * (b[:, 1] - a[:, 1])
    return int(np.sum(up & (cross > 0)) - np.sum(down & (cross < 0)))


def _nonzero(rings):
    """Konturlar → dolu alan, sıfırdan farklı kuralıyla (yazı tiplerinde konturlar üst üste biner, kendini keser):
    halkaların böldüğü her yüzün sarım sayısı bir iç noktasından hesaplanır; sıfır değilse dolu."""
    rings = [r for r in rings if len(r) > 2]
    lines = unary_union([LineString(list(r) + [r[0]]) for r in rings])
    faces = []
    for f in polygonize(lines):
        pt = f.representative_point()
        if sum(_winding((pt.x, pt.y), r) for r in rings) != 0:
            faces.append(f)
    return unary_union(faces) if faces else Polygon()


def text_geom(text, fn, size, x=0.0, y=0.0, track=0.0):
    """Metin → shapely şekli (y aşağı), boolean işlemler için. Döner (şekil, genişlik)."""
    tt, _ = _font(fn)
    gs = tt.getGlyphSet()
    glyphs, w, s = _shaped(text, fn, size, track)
    geom = Polygon()
    for name, gx, gy in glyphs:
        pen = _Flat(gs)
        gs[name].draw(TransformPen(pen, (s, 0, 0, -s, x + gx, y - gy)))
        geom = geom.union(_nonzero(pen.rings))
    return geom, w


def geom_path(g):
    """shapely şekli → SVG yolu (dış halka saat yönü tersi, içler saat yönü: sıfırdan farklı kuralıyla doğru)."""
    polys = [g] if g.geom_type == "Polygon" else list(getattr(g, "geoms", []))
    d = ""
    for p in polys:
        if p.is_empty or p.geom_type != "Polygon":
            continue
        p = orient(p, 1.0)
        for ring in [p.exterior, *p.interiors]:
            c = list(ring.coords)[:-1]
            d += "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in c) + "Z"
    return d


def cap(fn, size):
    tt, _ = _font(fn)
    return tt["OS/2"].sCapHeight * size / tt["head"].unitsPerEm


def xh(fn, size):
    tt, _ = _font(fn)
    return tt["OS/2"].sxHeight * size / tt["head"].unitsPerEm


# ---------------------------------------------------------------- logo yönleri
# Her işaret ve yazı: [(svg yolu, rol)], sınır kutusu (x0, y0, x1, y1). Roller: main (mürekkep / kâğıt), accent
# (turuncu), sub (yazının ikinci kelimesi).

LAYERS, GAP = 7, 0.24          # katmanlı yazı: harfler yatay katmanlara bölünür


def _layers(g, accent=(0,), layers=LAYERS, gap=GAP):
    """Şekil yatay katmanlara bölünür (3D baskı katmanları); accent'teki katmanlar turuncu."""
    x0, y0, x1, y1 = g.bounds
    bh = (y1 - y0) / layers
    return [(geom_path(g.intersection(box(x0 - 5, y0 + k * bh, x1 + 5, y0 + k * bh + bh * (1 - gap)))),
             "accent" if k in accent else "main") for k in range(layers)]


def _bounds(*geoms):
    return unary_union(list(geoms)).bounds


def _word(t1, f1, t2, f2, size, gap=.3, track1=0.0, track2=.06, case_box=None):
    """İki kelimelik yazı: birinci main, ikinci sub (turuncu). Döner (parçalar, sınır)."""
    d1, w1 = text_path(t1, f1, size, track=track1)
    d2, w2 = text_path(t2, f2, size, w1 + size * gap, track=track2)
    g, _ = text_geom(t1 + t2, f1, size)
    y0 = -cap(f1, size) if case_box == "cap" else g.bounds[1]
    y1 = 0 if case_box == "cap" else g.bounds[3]
    return [(d1, "main"), (d2, "sub")], (0, y0, w1 + size * gap + w2, y1)


# 1 · Küp: izometrik küp; üst yüz turuncu (o an basılan katman), yan yüzler katman katman
def _iso(a=50.0):
    c, h = a * 0.8660254, a / 2
    top = [(0, -a), (c, -h), (0, 0), (-c, -h)]
    left = [(-c, -h), (0, 0), (0, a), (-c, h)]
    right = [(0, 0), (c, -h), (c, h), (0, a)]
    return top, left, right


def _kup_geoms():
    """Küpün parçaları: [(şekil, rol)]: üst yüz turuncu, yan yüzler dörder katman."""
    top, left, right = _iso()
    gap = 2.2
    out = [(Polygon(top).buffer(-gap / 2, join_style=2), "accent")]
    for face, role in ((left, "main"), (right, "mid")):
        p0, p1, p2, p3 = (np.array(v, float) for v in face)       # üst kenar p0-p1, alt kenar p3-p2
        n = 4
        for k in range(n):
            t0, t1 = k / n, (k + 1) / n - 0.07
            band = [p0 + (p3 - p0) * t0, p1 + (p2 - p1) * t0, p1 + (p2 - p1) * t1, p0 + (p3 - p0) * t1]
            out.append((Polygon(band).buffer(-gap / 2, join_style=2), role))
    return out


def mark_kup():
    parts = _kup_geoms()
    return [(geom_path(g), r) for g, r in parts], _bounds(*[g for g, _ in parts])


def word_kup(size):
    return _word("BOYDE", "Sora-ExtraBold.ttf", "LABS", "Sora-Regular.ttf", size, .3, -.01, .08, "cap")


# 2 · Şişe: laboratuvar şişesi (Labs); içinde turuncu katmanlar (basılan parça)
def mark_sise():
    neck_w, body_w, neck_h, body_h, t = 30.0, 96.0, 34.0, 66.0, 9.0
    outer = Polygon([(-neck_w / 2, 0), (neck_w / 2, 0), (neck_w / 2, neck_h), (body_w / 2, neck_h + body_h),
                     (-body_w / 2, neck_h + body_h), (-neck_w / 2, neck_h)]).buffer(4, join_style=1).buffer(-4)
    inner = outer.buffer(-t, join_style=2)
    rim = box(-neck_w / 2 - 7, -6, neck_w / 2 + 7, 3).buffer(2.5).buffer(-2.5 + 2.5)
    glass = outer.difference(inner).union(rim)
    liquid = inner.buffer(-4.5)
    y0, y1 = neck_h + 10, liquid.bounds[3]
    bands, n = [], 3
    bh = (y1 - y0) / n
    for k in range(n):
        piece = liquid.intersection(box(-60, y0 + k * bh + 1.6, 60, y0 + (k + 1) * bh - 1.6))
        bands.append((geom_path(piece), "accent"))
    return [(geom_path(glass), "main")] + bands, _bounds(glass)


def word_sise(size):
    return _word("boyde", "Unbounded_600SemiBold.ttf", "labs", "Unbounded_600SemiBold.ttf", size, .28, 0, 0)


# 3 · Nozul: 3D yazıcının nozulu, ucunda turuncu damla; yazının altını turuncu çizgi çizer
def mark_nozul():
    nut = Polygon([(-26, 0), (26, 0), (26, 20), (-26, 20)]).buffer(3, join_style=1)
    body = Polygon([(-15, 20), (15, 20), (15, 34), (-15, 34)])
    cone = Polygon([(-15, 34), (15, 34), (5, 58), (-5, 58)])
    tip = body.union(cone).union(nut)
    slots = unary_union([box(x - 1.6, 5, x + 1.6, 15) for x in (-13, 0, 13)])
    noz = tip.difference(slots)
    drop = Point(0, 74).buffer(9, 64).union(Polygon([(-6.5, 68), (6.5, 68), (0, 58)]))
    return [(geom_path(noz), "main"), (geom_path(drop), "accent")], _bounds(noz, drop)


def word_nozul(size):
    parts, (x0, y0, x1, y1) = _word("BOYDE", "SpaceGrotesk_700Bold.ttf", "LABS", "SpaceGrotesk_400Regular.ttf",
                                    size, .26, .02, .1, "cap")
    line = box(0, size * .2, x1, size * .28)
    return parts + [(geom_path(line), "accent")], (x0, y0, x1, size * .28)


# 3a–3h · Nozul alternatifleri: aynı fikir, daha oturmuş biçimler. Nozul yandan: altıgen somun (üç yüz görünür:
# ortadaki geniş, yanlar yarım), altında koni, sivri uç; isteğe bağlı üstte diş çizgileri.
def _bar(x0, x1, y, h):
    """Yuvarlak uçlu çubuk (ortası y)."""
    return LineString([(x0 + h / 2, y), (x1 - h / 2, y)]).buffer(h / 2, 48)


def _soft(g, r):
    """Dış köşeleri yuvarlatır."""
    return g.buffer(-r, join_style=2).buffer(r, 32)


def _drop(cx, cy, r, k=2.2):
    """Damla: yuvarlak alt, sivri üst (ucu cy - k·r)."""
    return Point(cx, cy).buffer(r, 96).union(Point(cx, cy - k * r)).convex_hull


def _nozul(w=56.0, nut=20.0, cone=30.0, tip=8.0, gap=3.0, faces=True, thread=0, r=3.0, x=0.0, y=0.0):
    """Nozulun parçaları: dişler, somunun yüzleri, koni; uç y'si. Somunun üstü y."""
    out = {"thread": [], "nut": [], "cone": None}
    top = y
    if thread:
        th, tg = nut * .2, nut * .14
        for k in range(thread):
            out["thread"].append(_bar(x - w * .3, x + w * .3, top + th / 2, th))
            top += th + tg
    body = _soft(box(x - w / 2, top, x + w / 2, top + nut), r)
    if faces:
        cuts = unary_union([box(x + sx * w / 4 - gap * .4, top - 1, x + sx * w / 4 + gap * .4, top + nut + 1)
                            for sx in (-1, 1)])
        body = body.difference(cuts)
        out["nut"] = sorted(getattr(body, "geoms", [body]), key=lambda g: g.bounds[0])
    else:
        out["nut"] = [body]
    c0 = top + nut + gap
    cw = w * .64
    straight = cone * .22
    out["cone"] = _soft(Polygon([(x - cw / 2, c0), (x + cw / 2, c0), (x + cw / 2, c0 + straight),
                                 (x + tip / 2, c0 + cone), (x - tip / 2, c0 + cone), (x - cw / 2, c0 + straight)]),
                        min(r, tip * .3))
    out["tip"] = c0 + cone
    out["all"] = unary_union(out["thread"] + out["nut"] + [out["cone"]])
    return out


def _parts(*pairs):
    """[(şekil, rol)] → işaret (parçalar, sınır)."""
    pairs = [(g, r) for g, r in pairs if not g.is_empty]
    return [(geom_path(g), r) for g, r in pairs], _bounds(*[g for g, _ in pairs])


def _stack(t1, f1, t2, f2, size, k2=.5, lead=.24, track2=.16):
    """İki satır: üstte t1; altta sağa yaslı t2 (turuncu), solunda t1'in başına kadar turuncu çizgi (basılan
    katman)."""
    g1, _ = text_geom(t1, f1, size)
    d1, _ = text_path(t1, f1, size)
    s2 = size * k2
    c2 = cap(f2, s2)
    y2 = size * lead + c2
    g2, _ = text_geom(t2, f2, s2, 0, y2, track2)
    dx = g1.bounds[2] - g2.bounds[2]
    d2, _ = text_path(t2, f2, s2, dx, y2, track2)
    lh = c2 * .34
    rule = _bar(g1.bounds[0], g2.bounds[0] + dx - s2 * .45, y2 - c2 / 2, lh)
    return [(d1, "main"), (d2, "sub"), (geom_path(rule), "accent")], (g1.bounds[0], -cap(f1, size), g1.bounds[2], y2)


def _nozparts(n, role="main"):
    return [(p, role) for p in n["thread"] + n["nut"]] + [(n["cone"], role)]


def mark_n_sade():
    n = _nozul(w=52, nut=19, cone=31, tip=8)
    drop = _drop(0, n["tip"] + 22.5, 8.8, 2.05)
    return _parts(*_nozparts(n), (drop, "accent"))


def word_n_sade(size):
    return word_nozul(size)


word_n_sade.ratio = .56


def mark_n_katman():
    n = _nozul(w=46, nut=17, cone=26, tip=7, x=12)
    h, g, x0, x1 = 9.0, 3.6, -42.0, 42.0
    y = n["tip"] + g + h / 2
    layers = [(_bar(x0, 12 + 3.5, y, h), "accent")]
    layers += [(_bar(x0, x1, y + k * (h + g), h), "main") for k in (1, 2)]
    mark_n_katman.rows = [(y + k * (h + g), h, "accent" if k == 0 else "main") for k in range(3)]
    return _parts(*_nozparts(n), *layers)


def word_n_katman(size):
    return _stack("BOYDE", "SpaceGrotesk_700Bold.ttf", "LABS", "SpaceGrotesk_500Medium.ttf", size)


word_n_katman.ratio = .66


def mark_n_ilk():
    n = _nozul(w=52, nut=19, cone=31, tip=8)
    line = _bar(-30, 30, n["tip"] + 10, 7.5)
    return _parts(*_nozparts(n), (line, "accent"))


def word_n_ilk(size):
    return _word("BOYDE", "Sora-ExtraBold.ttf", "LABS", "Sora-Regular.ttf", size, .3, -.01, .08, "cap")


def mark_n_cizgi():
    sw = 4.6
    w, nut, cone = 52.0, 19.0, 31.0
    hull = _nozul(w=w, nut=nut, cone=cone, tip=9, gap=0, faces=False, r=4)
    outline = hull["all"].exterior.buffer(sw / 2, 32)
    seps = unary_union([LineString([(x, 0), (x, nut)]).buffer(sw / 2, 32) for x in (-w / 4, w / 4)]
                       + [LineString([(-w / 2, nut), (w / 2, nut)]).buffer(sw / 2, 32)])
    ink = outline.union(seps.intersection(hull["all"].buffer(sw / 2)))
    drop = _drop(0, hull["tip"] + 22, 8.5, 2.05)
    return _parts((ink, "main"), (drop, "accent"))


def word_n_cizgi(size):
    return _word("boyde", "Outfit-SemiBold.ttf", "labs", "Outfit-SemiBold.ttf", size, .26, -.01, -.01)


def mark_n_daire():
    R = 50.0
    n = _nozul(w=48, nut=16, cone=26, tip=7.5, gap=2.8, y=-35)
    disc = Point(0, 0).buffer(R, 256).difference(n["all"])
    line = _bar(-24, 24, n["tip"] + 10, 7)
    return _parts((disc, "main"), (line, "accent"))


def word_n_daire(size):
    return _word("BOYDE", "Manrope-ExtraBold.ttf", "LABS", "Manrope-Medium.ttf", size, .28, .01, .1, "cap")


def mark_n_kare():
    S, rr = 100.0, 24.0
    tile = box(-S / 2, -S / 2, S / 2, S / 2).buffer(-rr).buffer(rr, 64)
    n = _nozul(w=50, nut=17, cone=27, tip=8, gap=3, y=-34)
    line = _bar(-25, 25, n["tip"] + 10, 7.5)
    return _parts((tile.difference(n["all"]).difference(line), "accent"))


def word_n_kare(size):
    return _word("boyde", "Unbounded_600SemiBold.ttf", "labs", "Unbounded_600SemiBold.ttf", size, .28, 0, 0)


def mark_n_yazar():
    n = _nozul(w=40, nut=15, cone=24, tip=7, gap=2.6)
    line = _bar(-58, 3.5, n["tip"] + 7, 6)
    return _parts(*_nozparts(n), (line, "accent"))


def word_n_yazar(size):
    """Yazının altını nozul çizer: çizgi soldan gelir, nozul sağ ucunda."""
    f1, f2 = "SpaceGrotesk_700Bold.ttf", "SpaceGrotesk_400Regular.ttf"
    parts, (x0, y0, x1, _) = _word("BOYDE", f1, "LABS", f2, size, .26, .02, .1, "cap")
    ly, lh = size * .2, size * .075
    ch = cap(f1, size)
    # nozul: üstü büyük harf boyunda, ucu çizginin hemen üstünde
    k = (ch + ly - lh / 2 - size * .04) / 41.6
    nx = x1 + size * .3 + 20 * k
    n = _nozul(w=40 * k, nut=15 * k, cone=24 * k, tip=7 * k, gap=2.6 * k, r=3 * k, x=nx, y=-ch)
    line = _bar(0, nx + 3.5 * k, ly, lh)
    noz = unary_union(n["nut"] + [n["cone"]])
    return parts + [(geom_path(noz), "main"), (geom_path(line), "accent")], (x0, y0, nx + 20 * k, ly + lh / 2)


def mark_n_sicak():
    n = _nozul(w=50, nut=18, cone=34, tip=8, thread=2)
    cone = n["cone"]
    cx0, cy0, cx1, cy1 = cone.bounds
    hot_y = cy1 - (cy1 - cy0) * .42
    upper = cone.intersection(box(cx0 - 1, cy0 - 1, cx1 + 1, hot_y - 1.5))
    hot = cone.intersection(box(cx0 - 1, hot_y + 1.5, cx1 + 1, cy1 + 1))
    left, right = (upper.intersection(box(cx0 - 1, cy0 - 1, 0, cy1)), upper.intersection(box(0, cy0 - 1, cx1 + 1, cy1)))
    nl, nm, nr = n["nut"]
    return _parts(*[(p, "main") for p in n["thread"]], (nl, "main"), (nm, "main"), (nr, "mid"),
                  (left, "main"), (right, "mid"), (hot, "accent"))


def word_n_sicak(size):
    return _word("BOYDE", "Jost-Bold.ttf", "LABS", "Jost-SemiBold.ttf", size, .3, .06, .14, "cap")


# 11–20 · Yeni yönler (nozul yok; "logo ve marka kimliğini tekrar değiştirmek istiyoruz, 10 görsel daha")

def mark_plaka():
    """İsimliğin kendisi: panel (üstünde iki yazı satırı oyuk, sağda turuncu QR karesi) ve altında sehpa."""
    plate = _soft(box(-22, -31, 22, 0), 4.5)
    lines = unary_union([_bar(-17.5, -1.5, -22.0, 3.6), _bar(-17.5, -7.0, -13.0, 3.6)])
    qr = _soft(box(3.5, -26, 17.5, -12), 1.6)
    stand = _soft(box(-16, 2.5, 16, 8.5), 2.0)
    return _parts((plate - lines.buffer(0.01) - qr.buffer(1.6), "main"), (qr, "accent"), (stand, "main"))


def word_plaka(size):
    return _word("BOYDE", "Manrope-ExtraBold.ttf", "LABS", "Manrope-Medium.ttf", size, .28, .01, .1, "cap")


def mark_tarama():
    """Telefon kamerasının tarama çerçevesi: dört köşe, ortada turuncu kare (okutulan şey)."""
    h, L, w = 20.0, 12.0, 4.4
    corners = [LineString([(sx * h, sy * (h - L)), (sx * h, sy * h), (sx * (h - L), sy * h)]).buffer(w / 2, 32)
               for sx in (-1, 1) for sy in (-1, 1)]
    return _parts((unary_union(corners), "main"), (_soft(box(-7, -7, 7, 7), 2.0), "accent"))


def word_tarama(size):
    return _word("boyde", "SpaceGrotesk_700Bold.ttf", "labs", "SpaceGrotesk_400Regular.ttf", size, .22, -.01, 0)


def mark_dokunus():
    """Tek dokunuş: turuncu nokta ve ondan yayılan üç dalga."""
    cx, cy = -14.0, 14.0
    arcs = [LineString([(cx + r * np.sin(t), cy - r * np.cos(t)) for t in np.linspace(0.08, np.pi / 2 - 0.08, 40)])
            .buffer(2.3, 32) for r in (15.0, 24.0, 33.0)]
    return _parts((unary_union(arcs), "main"), (Point(cx, cy).buffer(6.2, 64), "accent"))


def word_dokunus(size):
    return _word("boyde", "Outfit-SemiBold.ttf", "labs", "Outfit-SemiBold.ttf", size, .26, -.01, -.01)


def mark_nokta():
    """Uygulama simgesi gibi: koyu karede turuncu daire (yazıdaki o)."""
    sq = _soft(box(-21, -21, 21, 21), 10.0)
    dot = Point(0, 0).buffer(10.5, 96)
    return _parts((sq - dot.buffer(0.01), "main"), (dot, "accent"))


def word_nokta(size):
    """boyde: o turuncu bir daire; yanında labs gri."""
    fn = "Sora-ExtraBold.ttf"
    xh_ = xh(fn, size)
    d1, w1 = text_path("b", fn, size)
    r = xh_ * 0.56
    gap = size * 0.03
    cx = w1 + gap + r
    d3, w3 = text_path("yde", fn, size, cx + r + gap)
    dot = Point(cx, -xh_ / 2).buffer(r, 96)
    x4 = cx + r + gap + w3 + size * .28
    d4, w4 = text_path("labs", "Sora-Regular.ttf", size, x4, track=.01)
    g, _ = text_geom("byde", fn, size)
    return [(d1, "main"), (geom_path(dot), "accent"), (d3, "main"), (d4, "mid")], (0, g.bounds[1], x4 + w4, g.bounds[3])


PIX = {"B": ["1111.", "1...1", "1...1", "1111.", "1...1", "1...1", "1111."],
       "O": [".111.", "1...1", "1...1", "1...1", "1...1", "1...1", ".111."],
       "Y": ["1...1", "1...1", ".1.1.", "..1..", "..1..", "..1..", "..1.."],
       "D": ["111..", "1..1.", "1...1", "1...1", "1...1", "1..1.", "111.."],
       "E": ["11111", "1....", "1....", "1111.", "1....", "1....", "11111"],
       "L": ["1....", "1....", "1....", "1....", "1....", "1....", "11111"],
       "A": [".111.", "1...1", "1...1", "11111", "1...1", "1...1", "1...1"],
       "S": [".1111", "1....", "1....", ".111.", "....1", "....1", "1111."]}


def _pixels(text, p, x=0.0):
    """Piksel harfler (5 × 7, kare p, aralık bir kare): döner (şekil, sağ kenar)."""
    sq = []
    for ch in text:
        for r, row in enumerate(PIX[ch]):
            for c, v in enumerate(row):
                if v == "1":
                    sq.append(box(x + c * p, -(7 - r) * p, x + (c + 1) * p, -(6 - r) * p).buffer(p * .02,
                                                                                                    join_style=2))
        x += 6 * p
    return unary_union(sq).buffer(-p * .06, join_style=2), x - p          # bitişik pikseller kaynaşır


def mark_piksel():
    """Üç basamak piksel (voksel): en üstteki turuncu."""
    p = 13.0
    cells = [(0, 2), (1, 2), (2, 2), (1, 1), (2, 1)]
    sq = lambda c, r: _soft(box(c * p + 1, r * p + 1, (c + 1) * p - 1, (r + 1) * p - 1), 2.2)  # noqa: E731
    return _parts((unary_union([sq(c, r) for c, r in cells]), "main"), (sq(2, 0), "accent"))


def word_piksel(size):
    g1, x1 = _pixels("BOYDE", size / 7)
    g2, x2 = _pixels("LABS", size / 7, x1 + size * .6)
    return [(geom_path(g1), "main"), (geom_path(g2), "sub")], (0, -size, x2, 0)


def mark_serif():
    """B ve turuncu nokta (Fraunces)."""
    g, w = text_geom("B", "Fraunces-Black.ttf", 100)
    dot = Point(w + 9, -9).buffer(9, 64)
    return _parts((g, "main"), (dot, "accent"))


def word_serif(size):
    """Boyde (Fraunces), yanında küçük LABS: x yüksekliğinin ortasında."""
    f1, f2 = "Fraunces-Black.ttf", "SpaceGrotesk_700Bold.ttf"
    d1, w1 = text_path("Boyde", f1, size)
    s2 = size * .3
    y2 = -xh(f1, size) / 2 + cap(f2, s2) / 2
    d2, w2 = text_path("LABS", f2, s2, w1 + size * .2, y2, .3)
    g, _ = text_geom("Boyde", f1, size)
    return [(d1, "main"), (d2, "sub")], (0, g.bounds[1], w1 + size * .2 + w2, g.bounds[3])


def mark_imza():
    """Turuncu dairede imza B'si (oyuk)."""
    g, w = text_geom("B", "Norican-Regular.ttf", 74)
    gx0, gy0, gx1, gy1 = g.bounds
    g = affinity.translate(g, -(gx0 + gx1) / 2, -(gy0 + gy1) / 2 + 1)
    disc = Point(0, 0).buffer(36, 128)
    return _parts((disc - g.buffer(0.01), "accent"))


def word_imza(size):
    """Boyde el yazısı (Norican); altında, sağa yaslı, aralıklı turuncu LABS."""
    f1, f2 = "Norican-Regular.ttf", "SpaceGrotesk_700Bold.ttf"
    s1 = size * 1.25
    d1, w1 = text_path("Boyde", f1, s1)
    g1, _ = text_geom("Boyde", f1, s1)
    s2 = size * .36
    gl, _ = text_geom("LABS", f2, s2, 0, 0, .42)
    y2 = g1.bounds[3] + s2 * .25 + cap(f2, s2)
    x2 = g1.bounds[2] - gl.bounds[2]
    d2, _ = text_path("LABS", f2, s2, x2, y2, .42)
    return [(d1, "main"), (d2, "sub")], (g1.bounds[0], g1.bounds[1], g1.bounds[2], y2)


word_imza.ratio = .62


def _brackets(x0, x1, y0, y1, t, arm):
    left = LineString([(x0 + arm, y0), (x0, y0), (x0, y1), (x0 + arm, y1)]).buffer(t / 2, 8, join_style=2, cap_style=2)
    right = LineString([(x1 - arm, y0), (x1, y0), (x1, y1), (x1 - arm, y1)]).buffer(t / 2, 8, join_style=2,
                                                                                    cap_style=2)
    return unary_union([left, right])


def mark_parantez():
    """[ ■ ]: köşeli parantez içinde turuncu kare."""
    return _parts((_brackets(-24, 24, -24, 24, 5.0, 11.0), "main"), (_soft(box(-8, -8, 8, 8), 1.6), "accent"))


def word_parantez(size):
    """[boyde] labs: parantezler turuncu."""
    fn = "Unbounded_500Medium.ttf"
    pad = size * .2
    d1, w1 = text_path("boyde", fn, size, pad + size * .12)
    g, _ = text_geom("boyde", fn, size, pad + size * .12)
    gx0, gy0, gx1, gy1 = g.bounds
    t = size * .11
    br = _brackets(t / 2, gx1 + pad, gy0 - size * .1, gy1 + size * .1, t, size * .24)
    x2 = gx1 + pad + t + size * .3
    d2, w2 = text_path("labs", "Unbounded_300Light.ttf", size, x2)
    return [(geom_path(br), "accent"), (d1, "main"), (d2, "mid")], (0, gy0 - size * .1 - t / 2, x2 + w2,
                                                                      gy1 + size * .1 + t / 2)


def mark_tente():
    """Dükkân tentesi: üstte çubuk, aşağı doğru açılan beş şerit (koyu ve turuncu sırayla), uçları dalgalı."""
    n, top_w, bot_w, y0, y1 = 5, 40.0, 50.0, -18.0, 2.0
    bar = _soft(box(-top_w / 2 - 3, -25, top_w / 2 + 3, -19.6), 2.0)
    main, acc = [], []
    for k in range(n):
        xt0, xt1 = -top_w / 2 + k * top_w / n, -top_w / 2 + (k + 1) * top_w / n
        xb0, xb1 = -bot_w / 2 + k * bot_w / n, -bot_w / 2 + (k + 1) * bot_w / n
        stripe = Polygon([(xt0, y0), (xt1, y0), (xb1, y1), (xb0, y1)]).union(
            Point((xb0 + xb1) / 2, y1).buffer((xb1 - xb0) / 2, 48))
        (acc if k % 2 else main).append(stripe.buffer(-0.45, join_style=2))
    return _parts((bar, "main"), (unary_union(main), "main"), (unary_union(acc), "accent"))


def word_tente(size):
    return _word("BOYDE", "Jost-Bold.ttf", "LABS", "Jost-Bold.ttf", size, .3, .1, .1, "cap")


def mark_yorunge():
    """Halka ve üzerinde turuncu uydu."""
    R, w = 21.0, 4.6
    ring = Point(0, 0).buffer(R + w / 2, 128).difference(Point(0, 0).buffer(R - w / 2, 128))
    a = np.radians(-40)
    sat = Point(R * np.cos(a), R * np.sin(a)).buffer(6.4, 64)
    core = Point(0, 0).buffer(5.0, 64)
    return _parts((ring - sat.buffer(2.6), "main"), (core, "main"), (sat, "accent"))


def word_yorunge(size):
    return _word("BOYDE", "Unbounded_300Light.ttf", "LABS", "Unbounded_300Light.ttf", size, .32, .16, .16, "cap")


# 4 · Etiket: boyde yazısı, labs turuncu bir etiketin içinde (harfler oyuk)
def _pill(text, fn, size, x):
    g, w = text_geom(text, fn, size, 0, 0)
    gx0, gy0, gx1, gy1 = g.bounds
    ph, pw = size * .95, (gx1 - gx0) + size * .7
    r = ph / 2
    pill = box(r, -r, pw - r, r).union(Point(r, 0).buffer(r, 64)).union(Point(pw - r, 0).buffer(r, 64))
    tg = affinity.translate(g, (pw - (gx1 - gx0)) / 2 - gx0, -(gy0 + gy1) / 2)
    out = affinity.translate(pill.difference(tg), x, 0)
    return out, pw, ph


def mark_etiket():
    g, _ = text_geom("b", "Unbounded_700Bold.ttf", 100, 0, 0)
    gx0, gy0, gx1, gy1 = g.bounds
    side = 120.0
    sq = box(0, 0, side, side).buffer(-22).buffer(22)
    tg = affinity.translate(g, (side - (gx1 - gx0)) / 2 - gx0, (side - (gy1 - gy0)) / 2 - gy0)
    return [(geom_path(sq.difference(tg)), "accent")], (0, 0, side, side)


def word_etiket(size):
    d1, w1 = text_path("boyde", "Unbounded_700Bold.ttf", size)
    g1, _ = text_geom("boyde", "Unbounded_700Bold.ttf", size)
    pill, pw, ph = _pill("labs", "Unbounded_500Medium.ttf", size * .72, w1 + size * .2)
    xh_ = xh("Unbounded_700Bold.ttf", size)
    pill = affinity.translate(pill, 0, -xh_ / 2)
    return [(d1, "main"), (geom_path(pill), "accent")], _bounds(g1, pill)


# 5 · Rozet: yuvarlak mühür; çevresinde BOYDE LABS · 3D BASKI ATÖLYESİ, ortada küp
def _arc_text(text, fn, size, R, top=True, track=.12):
    tt, _ = _font(fn)
    gs = tt.getGlyphSet()
    glyphs, w, s = _shaped(text, fn, size, track)
    adv = []
    for i, (name, gx, _) in enumerate(glyphs):
        nxt = glyphs[i + 1][1] if i + 1 < len(glyphs) else w
        adv.append(nxt - gx)
    span = w / R
    pen = SVGPathPen(gs)
    geoms = []
    for (name, gx, gy), a in zip(glyphs, adv):
        mid = gx + a / 2
        if top:
            th = -span / 2 + mid / R
            px, py, rot = R * np.sin(th), -R * np.cos(th), th
        else:                                       # alt yay: soldan sağa, harfler dik (üstleri merkeze)
            th = -span / 2 + mid / R
            rr = R + cap(fn, size)
            px, py, rot = rr * np.sin(th), rr * np.cos(th), -th
        m = a / 2                                   # glif ortası taban çizgisinde, yay üstündeki noktaya
        mat = (s * np.cos(rot), s * np.sin(rot), s * np.sin(rot), -s * np.cos(rot),
               px - m * np.cos(rot), py - m * np.sin(rot))
        gs[name].draw(TransformPen(pen, mat))
        fp = _Flat(gs)
        gs[name].draw(TransformPen(fp, mat))
        geoms.append(_nonzero(fp.rings))
    return pen.getCommands(), unary_union(geoms)


def mark_rozet():
    R = 100.0
    ring = Point(0, 0).buffer(R, 256).difference(Point(0, 0).buffer(R - 5, 256))
    inner = Point(0, 0).buffer(R - 44, 256).difference(Point(0, 0).buffer(R - 47, 256))
    d1, g1 = _arc_text("BOYDE LABS", "SpaceGrotesk_700Bold.ttf", 19, R - 32, True, .16)
    d2, g2 = _arc_text("3D BASKI ATÖLYESİ", "SpaceGrotesk_500Medium.ttf", 13, R - 36, False, .14)
    dots = unary_union([Point(sx * (R - 25), 3).buffer(3.4, 32) for sx in (-1, 1)])
    cube = [(affinity.translate(affinity.scale(g, .62, .62, origin=(0, 0)), 0, 0), r) for g, r in _kup_geoms()]
    return ([(geom_path(ring.union(inner)), "main"), (d1, "main"), (d2, "main"), (geom_path(dots), "accent")]
            + [(geom_path(g), r) for g, r in cube], (-R, -R, R, R))


def word_rozet(size):
    return _word("BOYDE", "SpaceGrotesk_700Bold.ttf", "LABS", "SpaceGrotesk_400Regular.ttf", size, .26, .02, .1, "cap")


# 6 · Katmanlı yazı: BOYDE harfleri katman katman, en üst katman turuncu; simgesi aynı kesimle B
def mark_katmanli():
    g, _ = text_geom("B", "Unbounded_800ExtraBold.ttf", 140, 0, 0)
    return _layers(g), g.bounds


def word_katmanli(size):
    g, w = text_geom("BOYDE", "Unbounded_800ExtraBold.ttf", size, track=-.01)
    parts = _layers(g)
    x0, y0, x1, y1 = g.bounds
    _, w2 = text_path("LABS", "Unbounded_300Light.ttf", size * .42, track=.5)
    d2, _ = text_path("LABS", "Unbounded_300Light.ttf", size * .42, x1 - w2, y1 + size * .52, track=.5)
    return parts + [(d2, "sub")], (x0, y0, x1, y1 + size * .52)


# 7 · QR: üç QR köşe işareti ve turuncu bir kare: ürünün kendisi
def mark_qr():
    m = 10.0
    def finder(x, y):
        o = box(x, y, x + 7 * m, y + 7 * m).buffer(-3).buffer(3)
        i = box(x + m, y + m, x + 6 * m, y + 6 * m)
        c = box(x + 2 * m, y + 2 * m, x + 5 * m, y + 5 * m).buffer(-2).buffer(2)
        return o.difference(i).union(c)
    g = 8 * m
    f = unary_union([finder(0, 0), finder(g, 0), finder(0, g)])
    sq = box(g + 1.2 * m, g + 1.2 * m, g + 5.8 * m, g + 5.8 * m).buffer(-6).buffer(6)
    return [(geom_path(f), "main"), (geom_path(sq), "accent")], (0, 0, g + 7 * m, g + 7 * m)


def word_qr(size):
    return _word("BOYDE", "Manrope-ExtraBold.ttf", "LABS", "Manrope-Medium.ttf", size, .28, .01, .1, "cap")


# 8 · b ve d: yazıda boyde'nin b ve d harfleri turuncu; simge bd
def mark_bd():
    fn = "SpaceGrotesk_700Bold.ttf"
    d1, w1 = text_path("b", fn, 140, 0, 0)
    d2, _ = text_path("d", fn, 140, w1 - 6, 0)
    gb, _ = text_geom("b", fn, 140, 0, 0)
    gd, _ = text_geom("d", fn, 140, w1 - 6, 0)
    return [(d1, "main"), (d2, "accent")], _bounds(gb, gd)


def word_bd(size):
    fn = "SpaceGrotesk_700Bold.ttf"
    parts, x = [], 0.0
    for ch, role in (("b", "accent"), ("oy", "main"), ("d", "accent"), ("e", "main")):
        d, w = text_path(ch, fn, size, x, track=-.02)
        parts.append((d, role))
        x += w - size * .02
    d, w = text_path("labs", "SpaceGrotesk_400Regular.ttf", size, x + size * .26)
    parts.append((d, "main"))
    g, _ = text_geom("boydelabs", fn, size)
    return parts, (0, g.bounds[1], x + size * .26 + w, g.bounds[3])


# yön: (ad, kısa anlatım, işaret, yazı, kılavuzdaki hikâye maddeleri, katmanlı mı, yalnız yazı mı)
YONLER = {
    1: ("Küp", "İzometrik küp: 3D'nin en bilinen işareti. Yan yüzler katman katman, üst yüz turuncu: o an basılan "
               "katman.", mark_kup, word_kup,
        [("Küp", "3D'nin en bilinen işareti: üç yüz, üç boyut."), ("Katmanlar", "yan yüzler ince katmanlardan: "
         "3D yazıcı parçayı alttan üste böyle kurar."), ("Turuncu üst yüz", "o an basılan katman: sıcak, yeni, size "
         "özel."), ("Yazı", "BOYDE kalın, LABS ince ve turuncu (Sora).")], False, False),
    2: ("Şişe", "Laboratuvar şişesi (Labs), içi turuncu katmanlarla dolu: deneyen, üreten atölye.", mark_sise,
        word_sise, [("Şişe", "Labs: deneyen, yeni şeyler üreten bir atölye."), ("Katmanlar", "şişenin içi turuncu "
                    "katmanlar: basılan parça."), ("Yazı", "boyde labs, küçük harf; labs turuncu (Unbounded).")],
        False, False),
    3: ("Nozul", "3D yazıcının nozulu ve ucunda turuncu damla; yazının altını aynı turuncu çizgi çizer.",
        mark_nozul, word_nozul, [("Nozul", "3D yazıcının sıcak ucu: her şey buradan çıkar."),
                                 ("Damla ve çizgi", "nozuldan çıkan turuncu filament yazının altını çizer."),
                                 ("Yazı", "BOYDE LABS (Space Grotesk).")], False, False),
    4: ("Etiket", "boyde yazısı ve turuncu bir etiketin içinde labs; simge turuncu karede b. Modern, sade.",
        mark_etiket, word_etiket, [("Yazı", "boyde, küçük harf ve kalın (Unbounded)."), ("Etiket", "labs turuncu "
                                   "bir etiketin içinde: ürün etiketleri gibi."), ("Simge", "turuncu karede b.")],
        False, False),
    5: ("Rozet", "Yuvarlak mühür: çevresinde BOYDE LABS ve 3D BASKI ATÖLYESİ, ortada küp. Paket ve etiket için.",
        mark_rozet, word_rozet, [("Rozet", "atölye mührü: kutulara, etiketlere, isimliklerin arkasına."),
                                 ("Küp", "ortada 3D'nin işareti, üst yüzü turuncu."),
                                 ("Yazı", "BOYDE LABS · 3D BASKI ATÖLYESİ (Space Grotesk).")], False, False),
    6: ("Katmanlı yazı", "BOYDE harfleri katman katman basılmış gibi, en üst katman turuncu; simge aynı kesimle B.",
        mark_katmanli, word_katmanli, [("Yazı", "BOYDE harfleri yatay katmanlardan: 3D baskı gibi."),
                                       ("Turuncu katman", "en üstteki, o an basılan katman."),
                                       ("Simge", "aynı kesimle B.")], True, True),
    7: ("QR", "Üç QR köşe işareti ve turuncu bir kare: ürünün (QR'lı isimlik) kendisi.", mark_qr, word_qr,
        [("QR", "isimliklerimizin kalbi: üç köşe işareti."), ("Turuncu kare", "dördüncü köşe: size özel olan."),
         ("Yazı", "BOYDE kalın, LABS ince ve turuncu (Manrope).")], False, False),
    8: ("b ve d", "boyde yazısında b ve d turuncu; simge bd. İsmin iki harfi öne çıkar.", mark_bd, word_bd,
        [("Harfler", "boyde'nin b ve d'si turuncu: ismin iki ucu."), ("Simge", "bd: b mürekkep, d turuncu."),
         ("Yazı", "boyde labs, küçük harf (Space Grotesk).")], False, False),
}

# Nozul alternatifleri (3. yön beğenildi; "logo daha estetik dursun")
NOZUL = {
    "3a": ("Sade", "3'ün kendisi, toparlanmış: altıgen somun, koni, ucunda damla; yazının altında turuncu çizgi.",
           mark_n_sade, word_n_sade, [("Nozul", "3D yazıcının sıcak ucu: altıgen somun ve koni."),
                                      ("Damla ve çizgi", "nozuldan çıkan turuncu filament yazının altını çizer."),
                                      ("Yazı", "BOYDE kalın, LABS ince ve turuncu (Space Grotesk).")], False, False),
    "3b": ("Katman", "Nozul katmanların üstünde; en üst katman turuncu, nozul onu hâlâ basıyor. Yazı da iki kat.",
           mark_n_katman, word_n_katman, [("Nozul", "3D yazıcının ucu, katmanın üstünde."),
                                          ("Katmanlar", "parça katman katman yükselir; en üstteki turuncu: o an "
                                           "basılan katman."),
                                          ("Yazı", "iki kat: BOYDE, altında turuncu çizgi ve LABS (Space Grotesk).")],
           False, False),
    "3c": ("İlk çizgi", "Nozul ve altında bastığı ilk turuncu çizgi. Yazı Sora: yuvarlak, dengeli.",
           mark_n_ilk, word_n_ilk, [("Nozul", "3D yazıcının sıcak ucu: altıgen somun ve koni."),
                                    ("Turuncu çizgi", "nozulun bastığı ilk çizgi: her parça böyle başlar."),
                                    ("Yazı", "BOYDE kalın, LABS ince ve turuncu (Sora).")], False, False),
    "3d": ("Tek çizgi", "Tek kalınlıkta çizgiyle nozul ve turuncu damla; hafif, zarif. Yazı küçük harf, yumuşak.",
           mark_n_cizgi, word_n_cizgi, [("Nozul", "tek kalınlıkta çizgiyle: hafif ve zarif."),
                                        ("Damla", "ucundan çıkan turuncu filament."),
                                        ("Yazı", "boyde labs, küçük harf (Outfit).")], False, False),
    "3e": ("Daire", "Koyu dairenin içinde boşluk olarak nozul, altında turuncu çizgi. Profil fotoğrafına hazır.",
           mark_n_daire, word_n_daire, [("Daire", "koyu daire; nozul içinde boşluk olarak."),
                                        ("Turuncu çizgi", "nozulun bastığı çizgi."),
                                        ("Yazı", "BOYDE kalın, LABS ince ve turuncu (Manrope).")], False, False),
    "3f": ("Kare", "Turuncu yuvarlak kare, nozul ve çizgi içinde boşluk. Uygulama simgesi gibi, uzaktan seçilir.",
           mark_n_kare, word_n_kare, [("Kare", "turuncu yuvarlak kare: uygulama simgesi gibi."),
                                      ("Nozul", "karenin içinde boşluk olarak; altında bastığı çizgi."),
                                      ("Yazı", "boyde labs, küçük harf; labs turuncu (Unbounded).")], False, False),
    "3g": ("Yazar", "Nozul yazının sonunda; altındaki turuncu çizgiyi o çizmiş gibi. 3'ün çizgisinin hikâyeli hâli.",
           mark_n_yazar, word_n_yazar, [("Nozul", "yazının sonunda duran 3D yazıcı ucu."),
                                        ("Çizgi", "yazının altındaki turuncu çizgiyi nozul basmış."),
                                        ("Yazı", "BOYDE LABS (Space Grotesk).")], False, True),
    "3h": ("Sıcak uç", "Dişli nozul iki tonlu (ışık sağdan), ucu turuncu: ısınmış, basmaya hazır. Yazı Jost.",
           mark_n_sicak, word_n_sicak, [("Nozul", "dişleri ve somunuyla; sağ yüzler gri, ışık alıyor."),
                                        ("Sıcak uç", "nozulun ucu turuncu: ısınmış, basmaya hazır."),
                                        ("Yazı", "BOYDE kalın, LABS turuncu, aralıklı (Jost).")], False, False),
}
# 21–30 · Yeni yönler, ikinci tur ("bi 10 tane daha üret")

def _extrude(g, d, n=24):
    """Sağ alta doğru derinlik: şeklin d kadar kaydırılmış kopyalarının birleşimi (3D blok görünüşü)."""
    return unary_union([affinity.translate(g, d * k / n, d * k / n) for k in range(1, n + 1)])


def mark_golge():
    """Turuncu derinlikli kare: 3D baskı."""
    face = _soft(box(-20, -20, 16, 16), 3.0)
    return _parts((_extrude(face, 7.5).difference(face), "accent"), (face, "main"))


def _word3d(text, size, labs=True):
    """Kalın yazı, turuncu derinlikle; labs: yanında küçük düz LABS (Archivo Black)."""
    fn = "ArchivoBlack-Regular.ttf"
    g, w = text_geom(text, fn, size, 0, 0, .02)
    d1, _ = text_path(text, fn, size, 0, 0, .02)
    depth = _extrude(g, size * .07).difference(g)
    parts, x1 = [(geom_path(depth), "accent"), (d1, "main")], w + size * .07
    if labs:
        s2 = size * .56
        x2 = x1 + size * .24
        d2, w2 = text_path("LABS", fn, s2, x2, 0, .06)
        parts.append((d2, "main"))
        x1 = x2 + w2
    return parts, (0, -cap(fn, size), x1, size * .07)


def word_golge(size):
    return _word3d("BOYDE", size)


# 21a–21d · 3D gölge, simge B&D ("21'in logosunu B&D yapar mısın")
BD_FONT = "ArchivoBlack-Regular.ttf"


def _bd(size=100.0):
    """B, & ve D ayrı ayrı (çizimde aralıkları korunur)."""
    full, w = text_geom("B&D", BD_FONT, size, 0, 0, .02)
    gb, _ = text_geom("B", BD_FONT, size, 0, 0, .02)
    gba, _ = text_geom("B&", BD_FONT, size, 0, 0, .02)
    return gb, gba.difference(gb), full.difference(gba), full


def mark_bd3d():
    """B&D, turuncu derinlikle."""
    *_, g = _bd()
    return _parts((_extrude(g, 7.0).difference(g), "accent"), (g, "main"))


def mark_bd3d_amp():
    """B ve D turuncu derinlikle, & düz turuncu."""
    b, amp, d, _ = _bd()
    bd = unary_union([b, d])
    return _parts((_extrude(bd, 7.0).difference(bd).difference(amp.buffer(1.2)), "accent"), (bd, "main"),
                  (amp, "accent"))


def mark_bd3d_kare():
    """Derinlikli koyu kart, içinde oyuk B&D."""
    *_, g = _bd()
    gx0, gy0, gx1, gy1 = g.bounds
    k = 70.0 / (gx1 - gx0)                                     # harfler kartın %76'sı
    g = affinity.scale(affinity.translate(g, -(gx0 + gx1) / 2, -(gy0 + gy1) / 2), k, k, origin=(0, 0))
    card = _soft(box(-46, -28, 46, 28), 8.0)
    return _parts((_extrude(card, 7.5).difference(card), "accent"), (card.difference(g.buffer(0.01)), "main"))


def word_bd3d_labs(size):
    return _word3d("B&D", size)


def mark_imlec():
    """Komut satırı: koyu karede > ve turuncu imleç."""
    sq = _soft(box(-22, -22, 22, 22), 9.0)
    chev = LineString([(-12, -9), (-3, 0), (-12, 9)]).buffer(2.6, 16, join_style=2)
    cur = box(1, 6, 14, 11)
    return _parts((sq - chev.buffer(0.01) - cur.buffer(2.0), "main"), (cur, "accent"))


def word_imlec(size):
    fn1, fn2 = "Poppins-SemiBold.ttf", "Poppins-Regular.ttf"
    d1, w1 = text_path("boyde", fn1, size)
    x2 = w1 + size * .26
    d2, w2 = text_path("labs", fn2, size, x2)
    x3 = x2 + w2 + size * .08
    cur = box(x3, -xh(fn1, size), x3 + size * .34, 0)
    g, _ = text_geom("boydelabs", fn1, size)
    return [(d1, "main"), (d2, "main"), (geom_path(cur), "accent")], (0, g.bounds[1], x3 + size * .34, g.bounds[3])


def mark_bauhaus():
    """Dört karede daire, çeyrek daire, üçgen, kare; daire turuncu."""
    s, gap = 21.0, 2.4
    tl = Point(-s / 2 - gap / 2, -s / 2 - gap / 2).buffer(s / 2, 96)
    q0 = (gap / 2, -s - gap / 2)
    tr = Point(q0[0], q0[1] + s).buffer(s, 128).intersection(box(q0[0], q0[1], q0[0] + s, q0[1] + s))
    bl = Polygon([(-s - gap / 2, gap / 2 + s), (-gap / 2, gap / 2 + s), (-gap / 2, gap / 2)])
    br = box(gap / 2, gap / 2, gap / 2 + s, gap / 2 + s)
    return _parts((tl, "accent"), (unary_union([tr, bl, br]), "main"))


def word_bauhaus(size):
    return _word("BOYDE", "Lexend-ExtraBold.ttf", "LABS", "Lexend-ExtraBold.ttf", size, .3, 0, .04, "cap")


def mark_blok():
    """BO / YD / E ve turuncu kare: harfler ızgarada."""
    fn, c = "ArchivoBlack-Regular.ttf", 20.0
    cells = []
    for i, ch in enumerate("BOYDE"):
        col, row = i % 2, i // 2
        g, _ = text_geom(ch, fn, 25.0)
        gx0, gy0, gx1, gy1 = g.bounds
        cells.append(affinity.translate(g, col * c + c / 2 - (gx0 + gx1) / 2, row * c + c / 2 - (gy0 + gy1) / 2))
    sq = _soft(box(c + 3, 2 * c + 3, 2 * c - 3, 3 * c - 3), 1.5)
    return _parts((unary_union(cells), "main"), (sq, "accent"))


def word_blok(size):
    return _word("BOYDE", "ArchivoBlack-Regular.ttf", "LABS", "ArchivoBlack-Regular.ttf", size, .3, .02, .04, "cap")


def mark_ok():
    """Turuncu dairede sağ üste ok (oyuk): aç, ulaş."""
    disc = Point(0, 0).buffer(21, 128)
    arrow = unary_union([LineString([(-7, 7), (7.5, -7.5)]).buffer(2.4, 16),
                         LineString([(-3.5, -7.5), (7.5, -7.5), (7.5, 3.5)]).buffer(2.4, 16, join_style=2)])
    return _parts((disc - arrow, "accent"))


def word_ok(size):
    return _word("boyde", "Figtree_800ExtraBold.ttf", "labs", "Figtree_800ExtraBold.ttf", size, .24, -.01, -.01)


def mark_acik():
    """Açık konumda düğme: koyu hap, sağda turuncu topuz."""
    pill = _soft(box(-25, -13, 25, 13), 12.99)
    knob = Point(12, 0).buffer(9.0, 96)
    return _parts((pill - knob.buffer(2.2), "main"), (knob, "accent"))


def word_acik(size):
    return _word("BOYDE", "Poppins-Bold.ttf", "LABS", "Poppins-Bold.ttf", size, .3, .02, .06, "cap")


def mark_baglanti():
    """İç içe iki halka (bağlantı): biri koyu, biri turuncu; kesişimlerde biri üstten, biri alttan geçer."""
    def link(dx):
        out = _soft(box(-15, -8.5, 15, 8.5), 8.49)
        ring = out.difference(out.buffer(-4.6))
        return affinity.translate(affinity.rotate(ring, -40, origin=(0, 0)), dx * 0.77, -dx * 0.64)
    r1, r2 = link(-8.5), link(8.5)
    parts = list(getattr(r1.intersection(r2), "geoms", [r1.intersection(r2)]))
    parts.sort(key=lambda g: g.centroid.y)
    if len(parts) >= 2:
        r2 = r2.difference(r1.buffer(1.4).intersection(parts[0].buffer(5)))
        r1 = r1.difference(r2.buffer(1.4).intersection(parts[-1].buffer(5)))
    return _parts((r1, "main"), (r2, "accent"))


def word_baglanti(size):
    return _word("BOYDE", "Syne-ExtraBold.ttf", "LABS", "Syne-ExtraBold.ttf", size, .3, .02, .04, "cap")


def mark_konum():
    """Konum iğnesi, ortasında turuncu nokta."""
    head = Point(0, -6).buffer(16, 128)
    pin = unary_union([head, Point(0, 22)]).convex_hull
    pin = _soft(pin, 1.2).difference(Point(0, -6).buffer(8.0, 96))
    return _parts((pin, "main"), (Point(0, -6).buffer(5.4, 96), "accent"))


def word_konum(size):
    return _word("BOYDE", "Righteous-Regular.ttf", "LABS", "Righteous-Regular.ttf", size, .3, .02, .04, "cap")


def mark_ampul():
    """Ampul: turuncu cam, koyu duy, üstte üç ışık çizgisi."""
    glass = unary_union([Point(0, -4).buffer(13, 128), Polygon([(-7.5, 4), (7.5, 4), (5.5, 13), (-5.5, 13)])])
    base = unary_union([_bar(-6, 6, 16.0, 3.0), _bar(-5, 5, 20.0, 3.0), _bar(-2.5, 2.5, 23.6, 2.6)])
    rays = unary_union([LineString([(np.sin(a) * 17, -4 - np.cos(a) * 17), (np.sin(a) * 23, -4 - np.cos(a) * 23)])
                        .buffer(1.6, 16) for a in np.radians([-48, 0, 48])])
    return _parts((glass, "accent"), (unary_union([base, rays]), "main"))


def word_ampul(size):
    return _word("BOYDE", "BigShouldersDisplay-Black.ttf", "LABS", "BigShouldersDisplay-Black.ttf", size, .22, .03,
                 .06, "cap")


def mark_kose():
    """Köşesi kıvrık kare: kıvrılan köşe turuncu."""
    s, c = 21.0, 14.0
    body = Polygon([(-s, -s), (s - c, -s), (s, -s + c), (s, s), (-s, s)])
    fold = Polygon([(s - c, -s), (s - c, -s + c), (s, -s + c)])
    body = _soft(body, 2.5).difference(fold.buffer(2.2, join_style=2))
    return _parts((body, "main"), (_soft(fold, 0.8), "accent"))


def word_kose(size):
    return _word("BOYDE", "BarlowCondensed-Black.ttf", "LABS", "BarlowCondensed-Black.ttf", size, .26, .06, .1,
                 "cap")


# Yeni yönler (nozuldan vazgeçildi: "logo ve marka kimliğini tekrar değiştirmek istiyoruz, 10 adet daha görsel")
YENI = {
    11: ("İsimlik", "Ürünün kendisi: panel, üstünde iki yazı satırı ve turuncu QR karesi, altında sehpa. Yazı Manrope.",
         mark_plaka, word_plaka, [("İsimlik", "sattığımız şeyin kendisi: panel ve sehpa."),
                                  ("Turuncu kare", "QR: okutulan, size özel olan."),
                                  ("Yazı", "BOYDE kalın, LABS ince ve turuncu (Manrope).")], False, False),
    12: ("Tarama", "Telefon kamerasının tarama çerçevesi, ortada turuncu kare: okut, ulaş. Yazı küçük harf.",
         mark_tarama, word_tarama, [("Çerçeve", "telefon kamerasının tarama köşeleri."),
                                    ("Turuncu kare", "okutulan isimlik."),
                                    ("Yazı", "boyde labs, küçük harf (Space Grotesk).")], False, False),
    13: ("Dokunuş", "Turuncu nokta ve yayılan dalgalar: tek dokunuşla ara, yaz, bul. Yumuşak, küçük harf yazı.",
         mark_dokunus, word_dokunus, [("Nokta", "tek dokunuş."), ("Dalgalar", "dokununca açılan sayfa: ara, "
                                      "WhatsApp, konum."), ("Yazı", "boyde labs, küçük harf (Outfit).")],
         False, False),
    14: ("Turuncu o", "Yazıdaki o turuncu bir daire; simge koyu karede aynı daire. Sade, akılda kalır.",
         mark_nokta, word_nokta, [("Turuncu o", "boyde'nin o'su: markanın noktası."),
                                  ("Simge", "uygulama simgesi gibi: koyu karede turuncu daire."),
                                  ("Yazı", "boyde kalın, labs gri (Sora).")], False, False),
    15: ("Piksel", "Harfler kare piksellerden: 3D yazıcı da parçayı küçük birimlerle kurar. Simge üç basamak.",
         mark_piksel, word_piksel, [("Piksel", "harfler kare birimlerden: üretim, teknoloji."),
                                    ("Basamaklar", "üst üste kurulan parça; en üstteki turuncu."),
                                    ("Yazı", "BOYDE ve turuncu LABS, piksel harf.")], False, False),
    16: ("Serif", "Boyde klasik harflerle, yanında küçük turuncu LABS; simge B ve turuncu nokta. Butik, kaliteli.",
         mark_serif, word_serif, [("Yazı", "Boyde klasik, kalın harflerle (Fraunces): özenli işçilik."),
                                  ("LABS", "küçük, aralıklı, turuncu."), ("Simge", "B ve turuncu nokta.")],
         False, True),
    17: ("İmza", "Boyde el yazısı gibi, altında aralıklı turuncu LABS; simge turuncu dairede imza B'si. Kişisel.",
         mark_imza, word_imza, [("İmza", "Boyde el yazısıyla: kişiye özel iş."),
                                ("LABS", "küçük, aralıklı, turuncu."), ("Simge", "turuncu dairede imza B'si.")],
         False, True),
    18: ("Parantez", "Köşeli parantez içinde boyde: isimliğin çerçevesi gibi. Simge parantez içinde turuncu kare.",
         mark_parantez, word_parantez, [("Parantez", "çerçeve: isimlik, tabela, ekran."),
                                        ("Turuncu", "parantezler ve içindeki kare."),
                                        ("Yazı", "boyde ve ince labs (Unbounded).")], False, False),
    19: ("Tente", "Dükkân tentesi: esnafın simgesi. Koyu ve turuncu şeritler; yazı geniş aralıklı Jost.",
         mark_tente, word_tente, [("Tente", "dükkânın simgesi: esnafla çalışıyoruz."),
                                  ("Şeritler", "koyu ve turuncu, sırayla."),
                                  ("Yazı", "BOYDE LABS, geniş aralıklı (Jost).")], False, False),
    20: ("Yörünge", "Halka ve üzerinde turuncu uydu: Labs, merak, teknoloji. İnce, ferah yazı.",
         mark_yorunge, word_yorunge, [("Halka", "merkezde işletmeniz."), ("Uydu", "turuncu: etrafında dönen "
                                      "müşteri."), ("Yazı", "BOYDE LABS, ince ve aralıklı (Unbounded).")],
         False, False),
}
# İkinci tur ("bi 10 tane daha üret")
YENI2 = {
    21: ("3D gölge", "Yazının turuncu derinliği: 3D baskı gibi yüzeyden yükselir. Simge derinlikli kare. Kalın, güçlü.",
         mark_golge, word_golge, [("Derinlik", "harfler turuncu derinlikle yükselir: 3D baskı."),
                                  ("Simge", "turuncu derinlikli kare."), ("Yazı", "BOYDE LABS (Archivo Black).")],
         False, False),
    22: ("İmleç", "Komut satırı: koyu karede > ve turuncu imleç; yazının sonunda yanıp sönen imleç. Dijital.",
         mark_imlec, word_imlec, [("İmleç", "turuncu imleç: dijital, her an yazılmaya hazır."),
                                  ("Simge", "koyu karede > ve imleç."), ("Yazı", "boyde labs, küçük harf (Poppins).")],
         False, False),
    23: ("Bauhaus", "Dört karede daire, çeyrek daire, üçgen ve kare; daire turuncu. Tasarım atölyesi havası.",
         mark_bauhaus, word_bauhaus, [("Biçimler", "daire, çeyrek, üçgen, kare: tasarım atölyesi."),
                                      ("Turuncu daire", "markanın noktası."), ("Yazı", "BOYDE LABS (Lexend).")],
         False, False),
    24: ("Blok", "Harfler ızgarada: BO / YD / E ve turuncu kare. Simgesi kendi adı; yazı kalın ve sıkı.",
         mark_blok, word_blok, [("Izgara", "BOYDE beş karede, altıncı kare turuncu."),
                                ("Simge", "adın kendisi: kare kare."), ("Yazı", "BOYDE LABS (Archivo Black).")],
         False, False),
    25: ("Ok", "Turuncu dairede sağ üste ok: okut, sayfan açılsın. Sade, küçük harf yazı.",
         mark_ok, word_ok, [("Ok", "bağlantı açılır: okut ve ulaş."), ("Daire", "turuncu, oyuk ok."),
                            ("Yazı", "boyde labs, küçük harf (Figtree).")], False, False),
    26: ("Açık", "Açık konumda düğme: işletmeniz her an açık, bir dokunuşla ulaşılır.",
         mark_acik, word_acik, [("Düğme", "açık konumda: işletmeniz her an ulaşılır."),
                                ("Topuz", "turuncu: açık."), ("Yazı", "BOYDE LABS (Poppins).")], False, False),
    27: ("Bağlantı", "İç içe iki halka: isimlik ile sayfa, işletme ile müşteri. Koyu ve turuncu.",
         mark_baglanti, word_baglanti, [("Halkalar", "iç içe: isimlik ve sayfası, işletme ve müşterisi."),
                                        ("Renkler", "biri koyu, biri turuncu."), ("Yazı", "BOYDE LABS (Syne).")],
         False, False),
    28: ("Konum", "Harita iğnesi, ortasında turuncu nokta: müşteriniz sizi bulsun. Yuvarlak hatlı yazı.",
         mark_konum, word_konum, [("İğne", "haritada işletmeniz."), ("Turuncu nokta", "tam yeri."),
                                  ("Yazı", "BOYDE LABS (Righteous).")], False, False),
    29: ("Ampul", "Turuncu cam, koyu duy ve ışık çizgileri: Labs, fikir. Uzun, dar yazı.",
         mark_ampul, word_ampul, [("Ampul", "fikir: Labs."), ("Turuncu cam", "yanan fikir."),
                                  ("Yazı", "BOYDE LABS, uzun dar (Big Shoulders).")], False, False),
    30: ("Köşe", "Köşesi kıvrık kare, kıvrılan köşe turuncu: etiket, kart, isimlik. Dar, sağlam yazı.",
         mark_kose, word_kose, [("Kare", "isimlik, kart, etiket."), ("Kıvrık köşe", "turuncu: size özel."),
                                ("Yazı", "BOYDE LABS, dar (Barlow Condensed).")], False, False),
}
# 21'in B&D çeşitleri
B_D = {
    "21a": ("B&D simge", "Simge B&D, turuncu derinlikle; yazı BOYDE LABS aynı stilde.", mark_bd3d, word_golge,
            [("B&D", "simge: B ve D, aralarında &; turuncu derinlikle yükselir (3D baskı)."),
             ("Yazı", "BOYDE kalın, turuncu derinlikli; yanında LABS (Archivo Black)."),
             ("Renk", "derinlik turuncu, harfler koyu.")], False, False),
    "21b": ("B&D LABS", "Yazının kendisi B&D LABS: B&D turuncu derinlikle, yanında LABS. Kısa ve akılda kalır.",
            mark_bd3d, word_bd3d_labs, [("B&D", "markanın kısa adı, turuncu derinlikle."),
                                        ("LABS", "yanında düz, koyu."), ("Simge", "B&D tek başına.")],
            False, True),
    "21c": ("Turuncu &", "B ve D turuncu derinlikle, & düz turuncu: iki harfi turuncu bağ birleştirir.",
            mark_bd3d_amp, word_golge, [("B ve D", "koyu, turuncu derinlikle."), ("&", "düz turuncu: bağ."),
                                        ("Yazı", "BOYDE LABS, turuncu derinlikli.")], False, False),
    "21d": ("Kart", "Derinlikli koyu kart, içinde oyuk B&D: isimlik gibi masada duran bir blok.",
            mark_bd3d_kare, word_golge, [("Kart", "turuncu derinlikli koyu blok: isimlik gibi."),
                                         ("B&D", "kartta oyuk."), ("Yazı", "BOYDE LABS, turuncu derinlikli.")],
            False, False),
}
DIRS = {**YONLER, **NOZUL, **YENI, **YENI2, **B_D}

THEMES = {"acik": {"main": INK, "sub": ORANGE, "accent": ORANGE, "mid": GRAY},
          "koyu": {"main": PAPER, "sub": ORANGE, "accent": ORANGE, "mid": GRAY},
          "siyah": {"main": "#000", "sub": "#000", "accent": "#000", "mid": "#000"},
          "beyaz": {"main": "#fff", "sub": "#fff", "accent": "#fff", "mid": "#fff"}}


def _g(parts, theme, dx=0.0, dy=0.0, s=1.0):
    col = THEMES[theme]
    body = "".join(f'<path d="{d}" fill="{col[r]}"/>' for d, r in parts)
    return f'<g transform="translate({dx:.2f} {dy:.2f}) scale({s:.4f})">{body}</g>'


def lockup(n, kind, theme, pad=0.0):
    """Logo (SVG metni, en, boy). kind: yatay, dikey, simge, yazi."""
    _, _, mark, word, _, _, only_word = DIRS[n]
    if only_word and kind in ("yatay", "dikey"):
        kind = "yazi"
    mp, (mx0, my0, mx1, my1) = mark()
    mw, mh = mx1 - mx0, my1 - my0
    H = 100.0                                       # simge boyu
    ms = H / mh
    if kind == "simge":
        W, Ht = mw * ms, H
        inner = _g(mp, theme, -mx0 * ms, -my0 * ms, ms)
    else:
        size = 100.0
        wp, (wx0, wy0, wx1, wy1) = word(size)
        if kind == "yazi":
            ws = 1.0
            W, Ht = (wx1 - wx0), (wy1 - wy0)
            inner = _g(wp, theme, -wx0, -wy0)
        elif kind == "yatay":
            ws = (H * getattr(word, "ratio", .46)) / (wy1 - wy0)   # yazının boyu simgenin %46'sı, ortalı
            gap = H * .3
            W, Ht = mw * ms + gap + (wx1 - wx0) * ws, H
            inner = (_g(mp, theme, -mx0 * ms, -my0 * ms, ms)
                     + _g(wp, theme, mw * ms + gap - wx0 * ws, (H - (wy1 - wy0) * ws) / 2 - wy0 * ws, ws))
        else:                                           # dikey: simge üstte, yazı altta ortalı
            ws = (H * .26 * getattr(word, "ratio", .46) / .46) / (wy1 - wy0)
            ww = (wx1 - wx0) * ws
            W = max(mw * ms, ww)
            gap = H * .26
            Ht = H + gap + (wy1 - wy0) * ws
            inner = (_g(mp, theme, (W - mw * ms) / 2 - mx0 * ms, -my0 * ms, ms)
                     + _g(wp, theme, (W - ww) / 2 - wx0 * ws, H + gap - wy0 * ws, ws))
    p = pad * Ht
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-p:.2f} {-p:.2f} {W + 2 * p:.2f} {Ht + 2 * p:.2f}" '
            f'width="{W + 2 * p:.1f}" height="{Ht + 2 * p:.1f}">{inner}</svg>'), W + 2 * p, Ht + 2 * p


def fitted(n, kind, theme, maxw, maxh):
    """Logo, verilen kutuya sığacak boyda (sayfa içi SVG)."""
    svg, w, h = lockup(n, kind, theme)
    k = min(maxw / w, maxh / h)
    return inline(svg, height=f"{h * k:.1f}px")


def inline(svg, height=None, width=None, cls=""):
    """Sayfa içinde kullanmak için: boyutu CSS'e bırakılmış SVG."""
    s = svg.replace(' xmlns="http://www.w3.org/2000/svg"', "")
    s = s.split(">", 1)
    head = s[0]
    head = re.sub(r' width="[^"]*" height="[^"]*"', "", head)
    style = ";".join(x for x in (f"height:{height}" if height else "", f"width:{width}" if width else "") if x)
    return f'{head} class="{cls}" style="{style}">{s[1]}'


# ---------------------------------------------------------------- çizim (tarayıcı)

def font_css():
    css = ""
    for fn, fam, wt in FONT_FILES.values():
        b64 = base64.b64encode(open(os.path.join(A.FONT_DIR, fn), "rb").read()).decode()
        css += f'@font-face{{font-family:"{fam}";font-weight:{wt};src:url(data:font/ttf;base64,{b64}) format("truetype")}}\n'
    return css


BASE_CSS = f"""
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:transparent}}
body{{font-family:"Space Grotesk",sans-serif;color:{PAPER};-webkit-font-smoothing:antialiased}}
.u{{font-family:Unbounded,sans-serif}}
"""


class Painter:
    """Tek tarayıcı: HTML → PNG (saydam olabilir) ya da PDF."""

    def __init__(self, pw):
        self.b = pw.chromium.launch(executable_path=CHROMIUM)
        self.fonts = font_css()

    def png(self, body, w, h, path, transparent=False, css="", scale=1):
        """h=None: yükseklik içeriğe göre."""
        pg = self.b.new_page(viewport={"width": w, "height": h or 800}, device_scale_factor=scale)
        size = f"width:{w}px;height:{h}px" if h else f"width:{w}px"
        pg.set_content(f"<!doctype html><meta charset=utf-8><style>{self.fonts}{BASE_CSS}{css}</style>"
                       f'<body style="{size};overflow:hidden">{body}</body>')
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(150)
        if not h:
            h = pg.evaluate("Math.ceil(document.body.getBoundingClientRect().height)")
            pg.set_viewport_size({"width": w, "height": h})
        pg.screenshot(path=path, omit_background=transparent, clip={"x": 0, "y": 0, "width": w, "height": h})
        pg.close()
        return path

    def pdf(self, pages, w, h, path, css=""):
        pg = self.b.new_page(viewport={"width": w, "height": h})
        body = "".join(pages)                              # her sayfa kök öğesi .pg
        pg.set_content(f"<!doctype html><meta charset=utf-8><style>{self.fonts}{BASE_CSS}{css}"
                       f"@page{{size:{w}px {h}px;margin:0}} .pg{{width:{w}px;height:{h}px;overflow:hidden;"
                       f"position:relative;page-break-after:always}}</style><body>{body}</body>")
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(300)
        pg.pdf(path=path, width=f"{w}px", height=f"{h}px", print_background=True)
        shots = []
        for k in range(len(pages)):
            el = pg.locator("body > .pg").nth(k)
            shots.append(Image.open(io.BytesIO(el.screenshot())).convert("RGB"))
        pg.close()
        return shots

    def close(self):
        self.b.close()


@contextlib.contextmanager
def painter():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        p = Painter(pw)
        try:
            yield p
        finally:
            p.close()


# ---------------------------------------------------------------- seçenekler

def options_sheet(P, path, recommended=None, dirs=None, title="logo yönleri", sub=None):
    dirs = dirs or YONLER
    sub = sub or (f"Birbirinden farklı {len(dirs)} yön, renkler aynı. Birini seçin; bütün kit (logo dosyaları, "
                  "Shopier, Instagram, kılavuz) ona göre üretilir.")
    cards = []
    for n, (name, desc, *_) in dirs.items():
        icon_k = fitted(n, "simge", "koyu", 112, 104)
        yat_a = fitted(n, "yatay", "acik", 520, 76)
        yat_k = fitted(n, "yatay", "koyu", 640, 64)
        prof = fitted(n, "simge", "koyu", 74, 62)
        tag = '<em>önerilen</em>' if n == recommended else ''
        cards.append(f"""<div class="card"><div class="lab"><b class="u">{n}</b><div><h2 class="u">{name}{tag}</h2>
          <p>{desc}</p></div></div>
          <div class="r1"><div class="tile dark">{icon_k}</div><div class="wide light">{yat_a}</div>
          <div class="ig"><span class="ring"><span class="pp">{prof}</span></span><small>profil</small></div></div>
          <div class="wide dark low">{yat_k}</div></div>""")
    css = f"""
    body{{background:{SAND};color:{INK};padding:56px 60px}}
    h1{{font:700 40px Unbounded;letter-spacing:-.01em}} .top p{{margin-top:10px;font-size:20px;color:#55575c}}
    .grid{{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:30px}}
    .card{{padding:22px;border-radius:26px;background:#EFEBE3;display:flex;flex-direction:column;gap:16px}}
    .lab{{display:flex;gap:14px;align-items:flex-start;min-height:74px}}
    .lab b{{flex:none;display:grid;place-items:center;min-width:40px;height:40px;padding:0 9px;border-radius:20px;
      background:{INK};
      color:{PAPER};font-size:18px}} .lab h2{{font-size:24px;display:flex;align-items:center;gap:10px}}
    .lab p{{margin-top:6px;font-size:16px;line-height:1.4;color:#55575c}}
    .lab em{{padding:3px 11px;border-radius:99px;background:{ORANGE};color:#fff;font:700 13px "Space Grotesk";
      font-style:normal}}
    .r1{{display:grid;grid-template-columns:160px 1fr 130px;gap:14px;align-items:center}}
    .tile,.wide{{height:160px;border-radius:20px;display:grid;place-items:center}}
    .dark{{background:{INK}}} .light{{background:{PAPER}}} .wide{{padding:0 24px}} .wide svg{{max-width:100%}}
    .low{{height:120px}}
    .ig{{display:flex;flex-direction:column;align-items:center;gap:8px}} .ig small{{font-size:14px;color:#55575c}}
    .ring{{padding:4px;border-radius:50%;background:linear-gradient(45deg,#f9a53b,#e1306c,#833ab4)}}
    .pp{{display:grid;place-items:center;width:112px;height:112px;border-radius:50%;background:{INK};border:4px solid #EFEBE3}}
    """
    body = (f'<div class="top"><h1>BOYDE LABS · {title}</h1><p>{sub}</p></div>'
            f'<div class="grid">{"".join(cards)}</div>')
    return P.png(body, 1880, None, path, css=css)


# ---------------------------------------------------------------- kit

def stripes_bg(color, alpha=.08, step=26, thick=.62):
    """Marka deseni: yatay katman çizgileri."""
    t = step * thick
    return (f"repeating-linear-gradient(180deg,rgba({_rgb(color)},{alpha}) 0 {t:.0f}px,transparent {t:.0f}px "
            f"{step}px)")


def _rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def logo_files(P, n, out):
    """SVG (yazılar çizgi) ve saydam PNG: yatay, dikey, simge, yazı × açık, koyu, siyah, beyaz."""
    os.makedirs(out, exist_ok=True)
    widths = {"yatay": 2400, "dikey": 1400, "simge": 1024, "yazi": 2000}
    made = []
    for kind, W in widths.items():
        for theme in THEMES:
            svg, w, h = lockup(n, kind, theme, pad=0.12)
            base = os.path.join(out, f"boyde_{kind}_{theme}")
            with open(base + ".svg", "w", encoding="utf-8") as f:
                f.write(svg)
            Hpx = round(W * h / w)
            P.png(inline(svg, width=f"{W}px"), W, Hpx, base + ".png", transparent=True)
            made.append(base)
    return made


ICONS = {   # öne çıkan kapakları: çizgi simgeler (24 × 24)
    "urunler": ('<path d="M12 2.8l8.2 4.6v9.2L12 21.2l-8.2-4.6V7.4z"/><path d="M3.8 7.4L12 12l8.2-4.6M12 12v9.2"/>',
                "Ürünler"),
    "siparis": ('<path d="M5 8.5h14l-1.1 12H6.1z"/><path d="M9 8.5V7a3 3 0 0 1 6 0v1.5"/>', "Sipariş"),
    "qr": ('<rect x="3.5" y="3.5" width="7" height="7" rx="1.2"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.2"/>'
           '<rect x="3.5" y="13.5" width="7" height="7" rx="1.2"/><path d="M13.5 13.5h3v3M20.5 13.5v.01M13.5 20.5h.01M17 17h3.5v3.5'
           '"/>', "QR isimlik"),
    "yorumlar": ('<path d="M12 3.6l2.6 5.3 5.8.8-4.2 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8-4.2-4.1 5.8-.8z"/>', "Yorumlar"),
    "kargo": ('<path d="M2.8 6.5h11v9.5h-11zM13.8 9.5h3.8l3 3.2V16h-6.8"/><circle cx="7" cy="17.6" r="1.9"/>'
              '<circle cx="17.2" cy="17.6" r="1.9"/>', "Kargo"),
    "iletisim": ('<path d="M4 5.2h16v10.6H9.2L4 19.8z"/><path d="M8 9.6h8M8 12.4h5"/>', "İletişim"),
}


def icon_svg(key, color, width=1.6):
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" '
            f'stroke-linejoin="round">{ICONS[key][0]}</svg>')


def product_photo(key="uzar"):
    """Ürün görseli (gönderi, şablonlar): örnek modundaki isimliğin 3/4 görünüşü, saydam (QR okunmaz, telefon
    BOYDE'nin; model boyde_urunler'in dışa aktardığı kaynak/<ürün>.npz). Bir kez çizilip kaynak/ klasöründe saklanır."""
    path = os.path.join(OUT, "kaynak", f"urun_{key}.png")
    if not os.path.exists(path):
        import json
        from cift_tarafli_isimlik import render, rotation
        z = np.load(os.path.join(OUT, "urunler", "kaynak", f"{key}.npz"))
        meta = json.loads(str(z["meta"]))
        meshes = [(z[f"v{i}"].astype(float), z[f"f{i}"], tuple(m["renk"])) for i, m in enumerate(meta)]
        im = render(meshes, 1600, rotation(-28, -68), margin=0.02)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        im.crop(im.getbbox()).save(path, optimize=True)
    buf = io.BytesIO()
    im = Image.open(path)
    im.thumbnail((1100, 1100))
    im.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def wide_graphic(sim_k, aspect, W=1920, H=1080, nozul=False, rows=None, y0=0.0, mh=1.0):
    """Metinsiz geniş görsel: işaretin katmanları sola doğru uzar (yazıcının çizdiği çizgiler gibi), en üstteki
    turuncu. Nozulda: nozul sağda, altında basılan katmanlar; en üstteki turuncu, nozulun altında biter.
    rows: işaretin kendi katmanları varsa [(orta y, kalınlık, rol)] (işaret koordinatında; y0, mh: işaretin üst
    kenarı ve boyu): katmanlar işaretten sola doğru uzar, başka çizgi eklenmez."""
    if rows:
        ih = 640
        iw = ih * aspect
        left, top = W - 300 - iw, (H - ih) / 2
        k = ih / mh
        bars = "".join(
            f'<i style="position:absolute;left:-40px;width:{left + 40 + h * k:.0f}px;'
            f'top:{top + (yc - y0 - h / 2) * k:.1f}px;height:{h * k:.1f}px;'
            f'background:linear-gradient(90deg,transparent,rgba({_rgb(ORANGE if r == "accent" else PAPER)},'
            f'1) 85%)"></i>' for yc, h, r in rows)
        return (f'<div style="background:{INK};height:{H}px;position:relative;overflow:hidden">{bars}'
                f'<div style="position:absolute;left:{left:.0f}px;top:{top:.0f}px">{inline(sim_k, height=f"{ih}px")}'
                f'</div></div>')
    if nozul:
        ih = 560
        iw = ih * aspect
        left, top = W - 330 - iw, 110
        cx = left + iw / 2
        bt, bh = top + ih + 34, 40
        bars = "".join(
            f'<i style="position:absolute;left:-40px;width:{cx + (24 if k == 0 else 260) + 40:.0f}px;'
            f'top:{bt + k * (bh + 16)}px;height:{bh}px;border-radius:{bh / 2}px;'
            f'background:linear-gradient(90deg,transparent,rgba({_rgb(ORANGE if k == 0 else PAPER)},'
            f'{1 if k == 0 else .2 - k * .03:.2f}) 70%)"></i>' for k in range(4))
        return (f'<div style="background:{INK};height:{H}px;position:relative;overflow:hidden">{bars}'
                f'<div style="position:absolute;left:{left:.0f}px;top:{top}px">{inline(sim_k, height=f"{ih}px")}</div>'
                f'</div>')
    ih = 700
    iw = ih * aspect
    top, left = (H - ih) / 2, W - 250 - iw
    bh = ih / LAYERS
    t = bh * (1 - GAP)
    bars = "".join(
        f'<i style="position:absolute;left:0;width:{left + 60:.0f}px;top:{top + k * bh:.1f}px;height:{t:.1f}px;'
        f'background:linear-gradient(90deg,transparent,rgba({_rgb(ORANGE if k == 0 else PAPER)},'
        f'{.9 if k == 0 else .22}))"></i>' for k in range(LAYERS))
    return (f'<div style="background:{INK};height:{H}px;position:relative;overflow:hidden">{bars}'
            f'<div style="position:absolute;left:{left:.0f}px;top:{top:.0f}px">{inline(sim_k, height=f"{ih}px")}</div>'
            f'</div>')


def kit(P, n):
    sim_k = lockup(n, "simge", "koyu")[0]
    made = {"logo": logo_files(P, n, os.path.join(OUT, "logo"))}
    sh = os.path.join(OUT, "shopier")
    ig = os.path.join(OUT, "instagram")
    hl = os.path.join(ig, "one_cikan")
    for d in (sh, ig, hl):
        os.makedirs(d, exist_ok=True)
    dark = f"background:{INK}"

    # ---- Shopier
    P.png(f"""<div style="{dark};height:200px;display:flex;align-items:center;justify-content:center;gap:44px;
      background-image:{stripes_bg(PAPER, .05, 20)};background-size:100% 20px">
      {fitted(n, "yatay", "koyu", 888, 74)}<i style="width:2px;height:64px;background:rgba(244,241,234,.25)"></i>
      <div><p class="u" style="font-size:26px;font-weight:500;color:{PAPER}">{SLOGAN}</p>
      <p style="margin-top:8px;font-size:17px;letter-spacing:.14em;color:{ORANGE};font-weight:700">QR'LI İSİMLİK · DİJİTAL
      KARTVİZİT · 3D BASKI</p></div></div>""", 1920, 200, os.path.join(sh, "banner_1920x200.png"))
    for sc, fn in ((1, "banner_mobil_400x100.png"), (2, "banner_mobil_800x200.png")):
        P.png(f"""<div style="{dark};height:100px;display:grid;place-items:center">{fitted(n, "yatay", "koyu", 528, 44)}</div>""",
              400, 100, os.path.join(sh, fn), scale=sc)
    P.png(f"""<div style="{dark};height:800px;display:grid;place-items:center">{fitted(n, "simge", "koyu", 500, 400)}</div>""",
          800, 800, os.path.join(sh, "logo_kare_800.png"))
    P.png(f"""<div style="{dark};height:1200px;display:flex;flex-direction:column;align-items:center;justify-content:center;
      gap:70px;background-image:{stripes_bg(PAPER, .04, 30)}">{fitted(n, "dikey", "koyu", 1290, 430)}
      <p class="u" style="font-size:52px;font-weight:500;color:{PAPER}">{SLOGAN}</p></div>""",
          1600, 1200, os.path.join(sh, "hakkinda_kapak_4x3.png"))
    _, sw, shh = lockup(n, "simge", "koyu")
    mark = DIRS[n][2]
    _, (_, my0, _, my1) = mark()
    P.png(wide_graphic(sim_k, sw / shh, nozul=n in NOZUL, rows=getattr(mark, "rows", None), y0=my0, mh=my1 - my0),
          1920, 1080, os.path.join(sh, "hakkinda_genis_16x9.png"))

    # ---- Instagram: profil ve öne çıkanlar
    P.png(f"""<div style="{dark};height:1080px;display:grid;place-items:center">{fitted(n, "simge", "koyu", 650, 520)}</div>""",
          1080, 1080, os.path.join(ig, "profil_1080.png"))
    for key, (_, label) in ICONS.items():
        P.png(f"""<div style="{dark};height:1920px;display:grid;place-items:center">
          <div style="width:620px;height:620px;border-radius:50%;background:{CHAR};display:grid;place-items:center;
          box-shadow:inset 0 0 0 6px rgba(255,90,31,.9)"><div style="width:300px">{icon_svg(key, ORANGE, 1.5)}</div>
          </div></div>""", 1080, 1920, os.path.join(hl, f"{key}.png"))

    # ---- Instagram: gönderiler (1080 × 1350)
    head = f'<div style="position:absolute;left:80px;top:76px">{fitted(n, "yatay", "koyu", 696, 58)}</div>'
    stripe = (f'<div style="position:absolute;left:0;right:0;bottom:0;height:300px;background-image:'
              f'{stripes_bg(PAPER, .06, 26)};-webkit-mask-image:linear-gradient(transparent,#000)"></div>')
    P.png(f"""<div style="{dark};height:1350px;position:relative;overflow:hidden">{stripe}{head}
      <div style="position:absolute;right:-190px;bottom:-330px;opacity:.1">{fitted(n, "simge", "koyu", 875, 700)}</div>
      <div style="position:absolute;left:80px;top:330px;right:80px">
        <p style="font-size:26px;font-weight:700;letter-spacing:.2em;color:{ORANGE}">MERHABA, BİZ BOYDE LABS</p>
        <h1 class="u" style="margin-top:34px;font-size:104px;line-height:1.02;font-weight:700;letter-spacing:-.02em">
          Katman<br>katman,<br><span style="color:{ORANGE}">size özel.</span></h1>
        <p style="margin-top:44px;font-size:34px;line-height:1.4;color:rgba(244,241,234,.78);max-width:820px">
          QR'lı akıllı isimlikler ve işletmenize özel dijital kartvizit siteleri. Tasarımdan 3D baskıya, kendi
          atölyemizde.</p></div>
      <div style="position:absolute;left:80px;bottom:80px;display:flex;gap:14px">
        <span style="padding:16px 28px;border-radius:99px;background:{ORANGE};color:#fff;font-size:28px;font-weight:700">
        Shopier'da →</span></div></div>""", 1080, 1350, os.path.join(ig, "gonderi_1_tanitim.png"))

    photo = product_photo()
    chips = ["Tek QR: ara, WhatsApp, konum, IBAN", "İşletmenize özel site", "Kabartmalı 3D baskı", "Size özel tasarım"]
    chip_html = "".join(f'<span style="padding:12px 20px;border-radius:99px;border:2px solid rgba(244,241,234,.22);'
                        f'font-size:25px">{c}</span>' for c in chips)
    P.png(f"""<div style="{dark};height:1350px;position:relative;overflow:hidden">{head}
      <div style="position:absolute;left:80px;right:80px;top:180px">
        <p style="font-size:26px;font-weight:700;letter-spacing:.2em;color:{ORANGE}">QR'LI AKILLI İSİMLİK</p>
        <h1 class="u" style="margin-top:22px;font-size:64px;line-height:1.08;font-weight:700;letter-spacing:-.02em">
          Masanızda dursun,<br>müşteriniz okutsun.</h1>
        <div style="margin-top:40px;height:520px;border-radius:32px;overflow:hidden;background:{SAND};display:grid;
          place-items:center"><img src="{photo}" style="height:500px;width:auto;filter:drop-shadow(0 26px 30px
          rgba(0,0,0,.25))"></div>
        <div style="margin-top:34px;display:flex;flex-wrap:wrap;gap:12px">{chip_html}</div></div>
      <div style="position:absolute;left:80px;right:80px;bottom:70px;display:flex;justify-content:space-between;
        align-items:flex-end"><div><p style="font-size:24px;color:rgba(244,241,234,.6)">site dahil</p>
        <p class="u" style="margin-top:6px;font-size:40px;font-weight:700">1 adet <span style="color:{ORANGE}">1.700 TL
        </span> · 2 adet <span style="color:{ORANGE}">2.000 TL</span></p></div></div></div>""",
          1080, 1350, os.path.join(ig, "gonderi_2_urun.png"))

    steps = [("Shopier'dan sipariş verin", "Adet seçin, ödemeyi güvenle Shopier'dan yapın."),
             ("Bilgilerinizi gönderin", "Logo, telefon, Instagram, konum ve IBAN: hepsi tek QR'a."),
             ("Size özel 10 tasarım", "10 tasarım gönderiyoruz; en beğendiğinizi 3D basıp kargoya veriyoruz.")]
    st = "".join(f"""<div style="display:grid;grid-template-columns:120px 1fr;gap:28px;padding:36px 0;
      border-top:2px solid rgba(244,241,234,.12)"><p class="u" style="font-size:64px;font-weight:700;color:{ORANGE};
      line-height:1">{k:02d}</p><div><h3 style="font-size:40px;font-weight:700">{t}</h3><p style="margin-top:10px;
      font-size:28px;line-height:1.4;color:rgba(244,241,234,.7)">{s}</p></div></div>""" for k, (t, s) in enumerate(steps, 1))
    P.png(f"""<div style="{dark};height:1350px;position:relative;overflow:hidden">{stripe}{head}
      <div style="position:absolute;left:80px;right:80px;top:230px">
        <p style="font-size:26px;font-weight:700;letter-spacing:.2em;color:{ORANGE}">NASIL SİPARİŞ VERİLİR?</p>
        <h1 class="u" style="margin:22px 0 46px;font-size:72px;line-height:1.05;font-weight:700;letter-spacing:-.02em">
          Üç adımda<br>isimliğiniz hazır.</h1>{st}</div></div>""", 1080, 1350, os.path.join(ig, "gonderi_3_nasil.png"))

    # ---- Instagram: hikâye
    P.png(f"""<div style="{dark};height:1920px;position:relative;overflow:hidden;background-image:{stripes_bg(PAPER, .05, 30)}">
      <div style="position:absolute;left:0;right:0;top:170px;display:grid;place-items:center">{fitted(n, "yatay", "koyu", 840, 70)}</div>
      <div style="position:absolute;left:90px;right:90px;top:560px">
        <p style="font-size:30px;font-weight:700;letter-spacing:.22em;color:{ORANGE}">DUYURU</p>
        <h1 class="u" style="margin-top:30px;font-size:128px;line-height:1;font-weight:700;letter-spacing:-.02em">
          Siparişler<br><span style="color:{ORANGE}">açık.</span></h1>
        <p style="margin-top:50px;font-size:42px;line-height:1.4;color:rgba(244,241,234,.8)">QR'lı isimliğinizi
          Shopier mağazamızdan sipariş edin. Tasarım bizden, 3D baskı atölyemizden.</p></div>
      <div style="position:absolute;left:90px;right:90px;bottom:300px;height:170px;border-radius:30px;
        border:3px dashed rgba(244,241,234,.35);display:grid;place-items:center;font-size:32px;
        color:rgba(244,241,234,.55)">bağlantı çıkartması buraya</div></div>""",
          1080, 1920, os.path.join(ig, "hikaye_siparis.png"))
    return made


# ---------------------------------------------------------------- kılavuz

def guide(P, n):
    story = DIRS[n][4]
    W, H = 1600, 900
    css = f"""
    .pg{{background:{PAPER};color:{INK};padding:80px 96px}}
    .pg.dark{{background:{INK};color:{PAPER}}}
    .k{{font-size:16px;font-weight:700;letter-spacing:.24em;color:{ORANGE}}}
    h2{{margin-top:14px;font:700 46px/1.1 Unbounded;letter-spacing:-.01em}}
    .lead{{margin-top:16px;max-width:880px;font-size:20px;line-height:1.5;color:#55575c}}
    .dark .lead{{color:rgba(244,241,234,.7)}}
    .no{{position:absolute;right:96px;bottom:56px;font-size:14px;letter-spacing:.2em;color:{GRAY}}}
    .grid{{display:grid;gap:22px;margin-top:40px}}
    .box{{border-radius:22px;display:grid;place-items:center;position:relative}}
    .box small{{position:absolute;left:20px;bottom:16px;font-size:14px;color:{GRAY}}}
    .sw{{border-radius:22px;padding:22px;height:300px;display:flex;flex-direction:column;justify-content:flex-end}}
    .sw b{{font:700 22px Unbounded}} .sw span{{margin-top:8px;font-size:16px;line-height:1.5;opacity:.85}}
    """
    no = lambda k: f'<p class="no">BOYDE LABS · MARKA KILAVUZU · {k:02d}</p>'  # noqa: E731
    pages = []
    pages.append(f"""<div class="pg dark" style="padding:0;background-image:{stripes_bg(PAPER, .05, 30)}">
      <div style="position:absolute;left:96px;top:96px">{fitted(n, "yatay", "koyu", 840, 70)}</div>
      <div style="position:absolute;left:96px;bottom:110px"><p class="k">MARKA KILAVUZU · 2026</p>
      <h1 class="u" style="margin-top:20px;font-size:92px;line-height:1.02;font-weight:700;letter-spacing:-.02em">
      Katman<br>katman,<br><span style="color:{ORANGE}">size özel.</span></h1></div>
      <div style="position:absolute;right:-90px;top:150px">{fitted(n, "simge", "koyu", 750, 600)}</div></div>""")
    pages.append(f"""<div class="pg"><p class="k">01 · HİKÂYE VE LOGO</p><h2>Ürünün kendisinden bir logo</h2>
      <p class="lead">BOYDE LABS bir 3D baskı atölyesi: QR'lı akıllı isimlikleri ve işletmelere özel dijital kartvizit
      sitelerini tasarlayıp kendi yazıcılarında basıyor. Logo da bu işten çıkıyor; her parçası bir şey anlatıyor.</p>
      <div class="grid" style="grid-template-columns:1.1fr 1fr">
        <div class="box" style="height:430px;background:{INK}">{fitted(n, "simge", "koyu", 375, 300)}<small>simge</small></div>
        <div style="display:flex;flex-direction:column;justify-content:center;gap:26px;font-size:20px;line-height:1.5">
          {"".join(f"<p><b>{k}:</b> {v}</p>" for k, v in story)}
          <p><b>Söz:</b> “{SLOGAN}”</p></div></div>{no(1)}</div>""")
    pages.append(f"""<div class="pg"><p class="k">02 · LOGO KULLANIMLARI</p><h2>Yatay, dikey, simge</h2>
      <p class="lead">Önce yatay logo; dar ve kare alanlarda dikey; profil fotoğrafı, uygulama simgesi ve küçük
      boyutlarda yalnız simge. Açık zeminde mürekkep, koyu zeminde kâğıt rengi.</p>
      <div class="grid" style="grid-template-columns:1.6fr 1fr 1fr;grid-template-rows:200px 200px">
        <div class="box" style="background:#fff">{fitted(n, "yatay", "acik", 936, 78)}<small>yatay · açık</small></div>
        <div class="box" style="background:#fff;grid-row:span 2">{fitted(n, "dikey", "acik", 630, 210)}<small>dikey</small></div>
        <div class="box" style="background:#fff">{fitted(n, "simge", "acik", 138, 110)}<small>simge</small></div>
        <div class="box" style="background:{INK}">{fitted(n, "yatay", "koyu", 936, 78)}<small>yatay · koyu</small></div>
        <div class="box" style="background:{INK}">{fitted(n, "simge", "koyu", 138, 110)}<small>simge · koyu</small></div>
      </div>
      <p style="margin-top:26px;font-size:17px;color:#55575c">Boşluk: logonun çevresinde en az simgenin yarısı kadar boş alan
      bırakın. En küçük boy: yatay logo 120 px (baskıda 25 mm), simge 24 px (5 mm).</p>{no(2)}</div>""")
    sw = [("Mürekkep", INK, PAPER, "#121316 · RGB 18 19 22<br>Ana renk: yazılar, zeminler"),
          ("Kâğıt", PAPER, INK, "#F4F1EA · RGB 244 241 234<br>Açık zemin, koyuda yazı"),
          ("Boyde turuncusu", ORANGE, "#fff", "#FF5A1F · RGB 255 90 31<br>Vurgu: tek katman, düğmeler, öne çıkanlar"),
          ("Kum", SAND, INK, "#E6E0D4 · RGB 230 224 212<br>Kartlar, ikinci zemin"),
          ("Gri", GRAY, "#fff", "#8B8E94 · RGB 139 142 148<br>Açıklamalar, ince çizgiler")]
    pages.append(f"""<div class="pg"><p class="k">03 · RENKLER</p><h2>Az renk, tek vurgu</h2>
      <p class="lead">Zeminler mürekkep ya da kâğıt; turuncu yalnız vurgu için (bir kelime, bir düğme, bir katman).
      Bir görselde turuncu alan yüzeyin onda birini geçmesin.</p>
      <div class="grid" style="grid-template-columns:repeat(5,1fr)">{''.join(
        f'<div class="sw" style="background:{bg};color:{fg};{"box-shadow:inset 0 0 0 2px #ddd8cd" if bg == PAPER else ""}">'
        f'<b>{nm}</b><span>{tx}</span></div>' for nm, bg, fg, tx in sw)}</div>{no(3)}</div>""")
    yazi = dict(story).get("Yazı", "")
    logo_font = yazi[yazi.rfind("(") + 1:yazi.rfind(")")] if "(" in yazi else "Unbounded"
    other = "" if logo_font in ("Unbounded", "Space Grotesk") else f" Logo yazısı {logo_font}; o da ücretsiz."
    pages.append(f"""<div class="pg"><p class="k">04 · YAZI TİPLERİ</p><h2>Unbounded ve Space Grotesk</h2>
      <p class="lead">İkisi de ücretsiz (SIL Open Font License) ve Türkçe harflerin hepsi var; Google Fonts'ta bulunur.
      {other}</p>
      <div class="grid" style="grid-template-columns:1fr 1fr">
        <div class="box" style="background:#fff;place-items:start;padding:36px;height:440px;align-content:start">
          <p class="k" style="color:{GRAY}">BAŞLIK{" · LOGO" if logo_font == "Unbounded" else ""}</p><p class="u" style="margin-top:14px;font-size:68px;font-weight:700;
          line-height:1">Unbounded</p><p class="u" style="margin-top:22px;font-size:30px;font-weight:500;line-height:1.3">
          Katman katman,<br>size özel.</p><p class="u" style="margin-top:22px;font-size:20px;font-weight:300">
          ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ 0123456789</p><p style="margin-top:16px;font-size:16px;color:{GRAY}">Light 300 ·
          Medium 500 · Bold 700</p></div>
        <div class="box" style="background:#fff;place-items:start;padding:36px;height:440px;align-content:start">
          <p class="k" style="color:{GRAY}">{"LOGO · " if logo_font == "Space Grotesk" else ""}METİN</p><p style="margin-top:14px;font-size:68px;font-weight:700;line-height:1">
          Space Grotesk</p><p style="margin-top:22px;font-size:24px;line-height:1.5">QR'lı akıllı isimlik: arama, WhatsApp,
          konum ve IBAN tek kodda. İşletmenize özel site dahil.</p><p style="margin-top:18px;font-size:20px">
          abcçdefgğhıijklmnoöprsştuüvyz 0123456789</p><p style="margin-top:16px;font-size:16px;color:{GRAY}">
          Regular 400 · Medium 500 · Bold 700</p></div></div>{no(4)}</div>""")
    shot = lambda fn, h: (f'<img src="data:image/png;base64,{base64.b64encode(open(os.path.join(OUT, fn), "rb").read()).decode()}" '  # noqa: E501,E731
                          f'style="height:{h}px;border-radius:14px;display:block">')
    pages.append(f"""<div class="pg"><p class="k">05 · UYGULAMALAR</p><h2>Instagram ve Shopier</h2>
      <div style="display:flex;gap:26px;margin-top:34px;align-items:flex-start">
        {shot("instagram/gonderi_1_tanitim.png", 340)}{shot("instagram/gonderi_2_urun.png", 340)}
        {shot("instagram/gonderi_3_nasil.png", 340)}{shot("instagram/hikaye_siparis.png", 340)}
        <div style="display:flex;flex-direction:column;gap:20px;align-items:center">
          {shot("instagram/profil_1080.png", 150).replace("border-radius:14px", "border-radius:50%")}
          <div style="display:grid;grid-template-columns:repeat(3,56px);gap:10px">{''.join(
            f'<div style="width:56px;height:56px;border-radius:50%;overflow:hidden"><img src="data:image/png;base64,'
            f'{base64.b64encode(open(os.path.join(OUT, "instagram", "one_cikan", k + ".png"), "rb").read()).decode()}" '
            f'style="width:56px;margin-top:-22px;display:block"></div>' for k in ICONS)}</div></div></div>
      <div style="margin-top:26px">{shot("shopier/banner_1920x200.png", 140)}</div>{no(5)}</div>""")
    pages.append(f"""<div class="pg"><p class="k">06 · DOĞRU KULLANIM</p><h2>Logoya dokunmayın</h2>
      <p class="lead">Logo dosyalarını olduğu gibi kullanın (logo/ klasörü): SVG baskı ve büyük işler için, PNG
      sosyal medya için.</p>
      <div class="grid" style="grid-template-columns:repeat(4,1fr);grid-template-rows:230px">
        {''.join(f'<div class="box" style="background:#fff;overflow:hidden"><div style="{st}">{fitted(n, "yatay", "acik", 480, 40)}</div>'
                 f'<small style="color:#c0392b">✕ {t}</small></div>' for st, t in (
                     ("transform:scaleX(1.5)", "esnetmeyin"), ("filter:hue-rotate(160deg)", "rengini değiştirmeyin"),
                     ("filter:drop-shadow(6px 6px 0 #888)", "gölge, efekt eklemeyin"),
                     ("transform:rotate(-12deg)", "döndürmeyin")))}</div>
      <div class="grid" style="grid-template-columns:1fr 1fr;grid-template-rows:200px;margin-top:22px">
        <div class="box" style="background:{INK}">{fitted(n, "yatay", "koyu", 840, 70)}<small style="color:#2e9b57">✓ koyu zeminde kâğıt rengi</small></div>
        <div class="box" style="background:{SAND}">{fitted(n, "yatay", "acik", 840, 70)}<small style="color:#2e9b57">✓ açık zeminde mürekkep</small></div>
      </div>{no(6)}</div>""")
    pages.append(f"""<div class="pg dark"><p class="k">07 · SES VE METİNLER</p><h2>Samimi, kısa, net</h2>
      <p class="lead">Esnafla konuşur gibi: kısa cümleler, “siz” dili, abartı yok. Fiyat ve süre açık yazılır.</p>
      <div class="grid" style="grid-template-columns:1fr 1fr;font-size:19px;line-height:1.55">
        <div style="padding:30px;border-radius:22px;background:{CHAR}"><p class="k">INSTAGRAM BİO</p><p style="margin-top:14px">
          BOYDE LABS · 3D baskı atölyesi<br>QR'lı akıllı isimlik + işletmenize özel site<br>Tasarım bizden, baskı
          atölyemizden<br>Sipariş: Shopier ↓</p></div>
        <div style="padding:30px;border-radius:22px;background:{CHAR}"><p class="k">SHOPIER MAĞAZA AÇIKLAMASI</p>
          <p style="margin-top:14px">QR'lı akıllı masa isimlikleri: müşteriniz okutunca arama, WhatsApp, Instagram,
          konum ve IBAN tek sayfada. Her isimlikle işletmenize özel dijital kartvizit sitesi. Kendi atölyemizde,
          kabartmalı 3D baskı.</p></div>
        <div style="padding:30px;border-radius:22px;background:{CHAR}"><p class="k">ETİKETLER</p><p style="margin-top:14px">
          #boydelabs #3dbaskı #qrkod #isimlik #masaisimliği #dijitalkartvizit #esnaf #işletme</p></div>
        <div style="padding:30px;border-radius:22px;background:{CHAR}"><p class="k">SÖZ</p><p class="u" style="margin-top:14px;
          font-size:30px;font-weight:500">{SLOGAN}</p></div></div>{no(7)}</div>""")
    shots = P.pdf(pages, W, H, os.path.join(OUT, "kilavuz.pdf"), css=css)
    cols = 2
    th = [s.resize((800, 450), Image.LANCZOS) for s in shots]
    sheet = Image.new("RGB", (cols * 800 + 3 * 30, ((len(th) + 1) // cols) * 480 + 30), SAND)
    for k, t in enumerate(th):
        sheet.paste(t, (30 + (k % cols) * 830, 30 + (k // cols) * 480))
    sheet.save(os.path.join(OUT, "kilavuz.png"), optimize=True)


def main():
    n = sys.argv[sys.argv.index("--yon") + 1] if "--yon" in sys.argv else 0
    n = int(n) if str(n).isdigit() else n
    os.makedirs(OUT, exist_ok=True)
    with painter() as P:
        options_sheet(P, os.path.join(OUT, "secenekler.png"), n or None)
        options_sheet(P, os.path.join(OUT, "secenekler_nozul.png"), n or None, NOZUL, "nozul alternatifleri",
                      "3 · Nozul fikri, daha oturmuş biçimlerle. Renkler aynı. Birini seçin; bütün kit ona göre "
                      "üretilir.")
        options_sheet(P, os.path.join(OUT, "secenekler_yeni.png"), n or None, YENI, "yeni logo yönleri",
                      "Nozul yok: birbirinden farklı 10 yeni yön (11–20), renkler aynı. Birini seçin; bütün kit "
                      "(logo dosyaları, Shopier, Instagram, kılavuz, katalog) ona göre üretilir.")
        options_sheet(P, os.path.join(OUT, "secenekler_21_bd.png"), n or None, B_D, "21 · B&D",
                      "21'in 3D gölge stili, simgede B&D: dört çeşit. Renkler aynı. Birini seçin; bütün kit ona göre "
                      "üretilir.")
        options_sheet(P, os.path.join(OUT, "secenekler_yeni_2.png"), n or None, YENI2, "yeni logo yönleri 2",
                      "İkinci tur: 10 yön daha (21–30), öncekilerin hiçbiri değil; renkler aynı. Birini seçin; bütün "
                      "kit ona göre üretilir.")
        print("seçenekler:", os.path.relpath(os.path.join(OUT, "secenekler.png"), A.ROOT),
              "secenekler_nozul.png, secenekler_yeni.png, secenekler_yeni_2.png, secenekler_21_bd.png")
        if not n:
            return
        for d in ("logo", "shopier", "instagram"):
            shutil.rmtree(os.path.join(OUT, d), ignore_errors=True)
        kit(P, n)
        guide(P, n)
    print(f"kit ({n} · {DIRS[n][0]}):", os.path.relpath(OUT, A.ROOT))


if __name__ == "__main__":
    main()
