"""BOYDE LABS – marka kimliği (Shopier mağazası ve Instagram hesabı için).

Ürün: QR'lı masa isimliği ve işletmeye özel dijital kartvizit sitesi; hepsi 3D baskı, kendi atölyesinde. Marka bir
3D baskı atölyesi ("Labs"); logo ürünün kendisinden çıkar.

Logo yönleri (secenekler.png): işaret b ve d harflerinden (BoyDe), geometrik; yazı hepsinde BOYDE kalın, LABS ince
turuncu (Unbounded). İlk taslaktaki B'li yönler yerine, istek: "b ve d harflerini kullanarak; renk paleti kalsın".
  1 Katman     b ve d yatay katmanlardan: 3D baskıda parça katman katman yükselir; en üst katman turuncu, o an
               basılan katman
  2 İki ton    b mürekkep, d turuncu; kaseler iç içe, d önde (çevresinde ince boşluk)
  3 Ayna       b ve d aynalı, kaseleri ortada değer; değdikleri yerde turuncu nokta (nozulun ucu)
  4 Tek çizgi  ince tek çizgi b ve d; b mürekkep, d turuncu

Seçilen yönle kit (varsayılan 1):
  logo/       yatay, dikey, simge; açık zemin, koyu zemin, tek renk siyah / beyaz; SVG (yazılar çizgi) ve saydam PNG
  shopier/    banner 1920 × 200 ve mobil 400 × 100 (Shopier'ın önerdiği ölçüler; önemli öğeler ortada), kare logo
              800 × 800 (en az 200 × 200, kare), Hakkında kapağı 4:3, geniş görsel 16:9 (metinsiz)
  instagram/  profil fotoğrafı (yuvarlak kırpmaya göre), öne çıkan kapakları (6), gönderi şablonları (1080 × 1350:
              tanıtım, ürün, nasıl sipariş verilir), hikâye (1080 × 1920)
  kilavuz.pdf marka kılavuzu (logo, kullanım, renkler, yazı tipleri, uygulamalar, metinler); kilavuz.png önizleme

Renkler: mürekkep #121316, kâğıt #F4F1EA, Boyde turuncusu #FF5A1F, kum #E6E0D4, gri #8B8E94.
Yazı tipleri (OFL): Unbounded (logo, başlık), Space Grotesk (metin).

Kullanım:
  python3 scripts/boyde_marka.py            # seçenekler + 1. yönle kit
  python3 scripts/boyde_marka.py --yon 3    # 3. yönle kit
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
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import polygonize, unary_union

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402

OUT = os.path.join(A.ROOT, "boyde_labs")
CHROMIUM = "/opt/pw-browsers/chromium"
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

LAYERS, GAP = 10, 0.24          # katmanlar: 10'luk bölüntüde kaselerin üstü (x yüksekliği) tam bir katman sınırında
R, S = 30.0, 16.0               # geometrik b ve d: kase yarıçapı ve çizgi kalınlığı (yükseklik 100)


def _ring(cx, cy, r, t):
    return Point(cx, cy).buffer(r, 256).difference(Point(cx, cy).buffer(r - t, 256))


def _b(x, r=R, s=S):
    """Geometrik b: solda gövde (yükseklik 100), sağda yuvarlak kase; x sol kenar."""
    return box(x, 0, x + s, 100).union(_ring(x + r, 100 - r, r, s))


def _d(x, r=R, s=S):
    """Geometrik d: solda kase, sağda gövde; x kasenin sol kenarı."""
    return box(x + 2 * r - s, 0, x + 2 * r, 100).union(_ring(x + r, 100 - r, r, s))


def _layers(g, accent=(0,)):
    """Şekil yatay katmanlara bölünür (3D baskı katmanları); accent'teki katmanlar turuncu."""
    x0, y0, x1, y1 = g.bounds
    bh = (y1 - y0) / LAYERS
    return [(geom_path(g.intersection(box(x0 - 5, y0 + k * bh, x1 + 5, y0 + k * bh + bh * (1 - GAP)))),
             "accent" if k in accent else "main") for k in range(LAYERS)]


def mark_katman():
    g = _b(0).union(_d(2 * R + 10))
    return _layers(g), g.bounds


def mark_ikiton():
    b, d = _b(0), _d(44)
    return [(geom_path(b.difference(d.buffer(4.5))), "main"), (geom_path(d), "accent")], b.union(d).bounds


def mark_ayna():
    b, d = _b(0), _d(2 * R)
    dot = Point(2 * R, 100 - R).buffer(7, 64)
    return [(geom_path(b.union(d).difference(dot.buffer(3))), "main"), (geom_path(dot), "accent")], b.union(d).bounds


def mark_tekcizgi():
    b, d = _b(0, R, 9), _d(2 * R + 10, R, 9)
    return [(geom_path(b), "main"), (geom_path(d), "accent")], b.union(d).bounds


def word_main(size):
    """BOYDE kalın, LABS ince (Unbounded); LABS turuncu."""
    d1, w1 = text_path("BOYDE", "Unbounded_700Bold.ttf", size)
    d2, w2 = text_path("LABS", "Unbounded_300Light.ttf", size, w1 + size * .32, track=.06)
    return [(d1, "main"), (d2, "sub")], (0, -cap("Unbounded_700Bold.ttf", size), w1 + size * .32 + w2, 0)


# yön: (ad, kısa anlatım, işaret, yazı, kılavuzdaki hikâye maddeleri, katmanlı mı)
YONLER = {
    1: ("Katman", "b ve d (BoyDe) yatay katmanlardan: 3D baskıda parça katman katman yükselir; en üst katman "
                  "turuncu, o an basılan katman.", mark_katman, word_main,
        [("Harfler", "b ve d: BoyDe'nin iki harfi, birbirine bakan kaseler; geometrik, sade."),
         ("Katmanlar", f"3D yazıcı parçayı alttan üste ince katmanlarla kurar; işaret {LAYERS} katmandan."),
         ("Turuncu katman", "en üstteki, o an basılan katman: işin sıcak, yeni ve size özel olduğunu söyler."),
         ("Yazı", "BOYDE kalın, LABS ince ve turuncu: atölye (laboratuvar) yanı.")], True),
    2: ("İki ton", "b mürekkep, d turuncu; kaseler iç içe geçer: iki harf, tek işaret.", mark_ikiton, word_main,
        [("Harfler", "b ve d: BoyDe'nin iki harfi, iç içe; d önde."),
         ("İki ton", "b mürekkep (atölye), d turuncu (sıcak filament); birbirini tamamlar."),
         ("Aralık", "d'nin çevresinde ince bir boşluk: harfler karışmaz, küçük boyda da okunur."),
         ("Yazı", "BOYDE kalın, LABS ince ve turuncu.")], False),
    3: ("Ayna", "b ve d aynalı, kaseleri ortada değer; değdikleri yerde turuncu nokta: nozulun ucu.", mark_ayna,
        word_main, [("Harfler", "b ve d birbirinin aynası: BoyDe, iki yandan ortaya bakar."),
                    ("Turuncu nokta", "kaselerin değdiği yerde: nozulun ucu, işin başladığı nokta."),
                    ("Simetri", "dengeli, akılda kalan bir işaret; profil fotoğrafında ve küçük boyda güçlü."),
                    ("Yazı", "BOYDE kalın, LABS ince ve turuncu.")], False),
    4: ("Tek çizgi", "ince tek çizgi b ve d: b mürekkep, d turuncu; nozulun çektiği tek hat gibi.", mark_tekcizgi,
        word_main, [("Harfler", "b ve d, ince tek çizgiyle: sade ve modern."),
                    ("Tek hat", "3D yazıcının nozulu da parçayı tek bir sıcak çizgiyle çizer."),
                    ("İki ton", "b mürekkep, d turuncu."),
                    ("Yazı", "BOYDE kalın, LABS ince ve turuncu.")], False),
}

THEMES = {"acik": {"main": INK, "sub": ORANGE, "accent": ORANGE},
          "koyu": {"main": PAPER, "sub": ORANGE, "accent": ORANGE},
          "siyah": {"main": "#000", "sub": "#000", "accent": "#000"},
          "beyaz": {"main": "#fff", "sub": "#fff", "accent": "#fff"}}


def _g(parts, theme, dx=0.0, dy=0.0, s=1.0):
    col = THEMES[theme]
    body = "".join(f'<path d="{d}" fill="{col[r]}"/>' for d, r in parts)
    return f'<g transform="translate({dx:.2f} {dy:.2f}) scale({s:.4f})">{body}</g>'


def lockup(n, kind, theme, pad=0.0):
    """Logo (SVG metni, en, boy). kind: yatay, dikey, simge, yazi."""
    _, _, mark, word, *_ = YONLER[n]
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
            ws = (H * .46) / (wy1 - wy0)                # yazının boyu simgenin %46'sı, ortalı
            gap = H * .3
            W, Ht = mw * ms + gap + (wx1 - wx0) * ws, H
            inner = (_g(mp, theme, -mx0 * ms, -my0 * ms, ms)
                     + _g(wp, theme, mw * ms + gap - wx0 * ws, (H - (wy1 - wy0) * ws) / 2 - wy0 * ws, ws))
        else:                                           # dikey: simge üstte, yazı altta ortalı
            ws = (H * .26) / (wy1 - wy0)
            ww = (wx1 - wx0) * ws
            W = max(mw * ms, ww)
            gap = H * .26
            Ht = H + gap + (wy1 - wy0) * ws
            inner = (_g(mp, theme, (W - mw * ms) / 2 - mx0 * ms, -my0 * ms, ms)
                     + _g(wp, theme, (W - ww) / 2 - wx0 * ws, H + gap - wy0 * ws, ws))
    p = pad * Ht
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-p:.2f} {-p:.2f} {W + 2 * p:.2f} {Ht + 2 * p:.2f}" '
            f'width="{W + 2 * p:.1f}" height="{Ht + 2 * p:.1f}">{inner}</svg>'), W + 2 * p, Ht + 2 * p


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
        pg = self.b.new_page(viewport={"width": w, "height": h}, device_scale_factor=scale)
        pg.set_content(f"<!doctype html><meta charset=utf-8><style>{self.fonts}{BASE_CSS}{css}</style>"
                       f'<body style="width:{w}px;height:{h}px;overflow:hidden">{body}</body>')
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(150)
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

def options_sheet(P, path):
    rows = []
    for n, (name, desc, *_) in YONLER.items():
        icon_k = inline(lockup(n, "simge", "koyu")[0], height="96px")
        icon_a = inline(lockup(n, "simge", "acik")[0], height="96px")
        yat_a = inline(lockup(n, "yatay", "acik")[0], height="74px")
        yat_k = inline(lockup(n, "yatay", "koyu")[0], height="74px")
        prof = inline(lockup(n, "simge", "koyu")[0], height="62px")
        rows.append(f"""<div class="row"><div class="lab"><b class="u">{n}</b><h2 class="u">{name}</h2><p>{desc}</p>
          {'<em>önerilen</em>' if n == 1 else ''}</div>
          <div class="tile dark">{icon_k}</div><div class="tile light">{icon_a}</div>
          <div class="wide light">{yat_a}</div><div class="wide dark">{yat_k}</div>
          <div class="ig"><span class="ring"><span class="pp">{prof}</span></span><small>profil</small></div></div>""")
    css = f"""
    body{{background:{SAND};color:{INK};padding:60px}}
    h1{{font:700 40px Unbounded;letter-spacing:-.01em}} .top p{{margin-top:10px;font-size:20px;color:#55575c}}
    .row{{display:grid;grid-template-columns:330px 170px 170px 1fr 1fr 150px;gap:18px;align-items:center;margin-top:28px;
      padding:22px;border-radius:24px;background:#EFEBE3}}
    .lab b{{display:inline-grid;place-items:center;width:40px;height:40px;border-radius:50%;background:{INK};color:{PAPER};
      font-size:18px}} .lab h2{{margin-top:12px;font-size:26px}} .lab p{{margin-top:6px;font-size:16px;line-height:1.4;color:#55575c}}
    .lab em{{display:inline-block;margin-top:10px;padding:4px 12px;border-radius:99px;background:{ORANGE};color:#fff;
      font-style:normal;font-weight:700;font-size:14px}}
    .tile,.wide{{height:170px;border-radius:20px;display:grid;place-items:center}}
    .dark{{background:{INK}}} .light{{background:{PAPER}}} .wide{{padding:0 26px}} .wide svg{{max-width:100%}}
    .ig{{display:flex;flex-direction:column;align-items:center;gap:8px}} .ig small{{font-size:14px;color:#55575c}}
    .ring{{padding:4px;border-radius:50%;background:linear-gradient(45deg,#f9a53b,#e1306c,#833ab4)}}
    .pp{{display:grid;place-items:center;width:112px;height:112px;border-radius:50%;background:{INK};border:4px solid #EFEBE3}}
    """
    body = (f'<div class="top"><h1>BOYDE LABS · b + d logo yönleri</h1><p>Dört yön, hepsi b ve d harflerinden; birini seçin, bütün kit (logo dosyaları, '
            f'Shopier, Instagram, kılavuz) ona göre üretilir. Kit şimdi 1 · Katman ile hazır.</p></div>{"".join(rows)}')
    return P.png(body, 1880, 1300, path, css=css)


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


def product_photo():
    """Ürün görseli (şablonlarda): Auto Tufan isimliğinin 3/4 görünüşü, büyük çizim (saydam; bir kez çizilip
    kaynak/ klasöründe saklanır)."""
    path = os.path.join(OUT, "kaynak", "urun_ornek.png")
    if not os.path.exists(path):
        import autotufan_isimlik as C
        d = C.build(C.secilen)
        im = C.render(C.mesh(d.shown), 1600, C.rotation(-28, -68), margin=0.02)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        im.crop(im.getbbox()).save(path, optimize=True)
    buf = io.BytesIO()
    im = Image.open(path)
    im.thumbnail((1100, 1100))
    im.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def wide_graphic(sim_k, aspect, W=1920, H=1080):
    """Metinsiz geniş görsel: işaretin katmanları sola doğru uzar (yazıcının çizdiği çizgiler gibi), en üstteki
    turuncu."""
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
    yat_k = lockup(n, "yatay", "koyu")[0]
    dik_k = lockup(n, "dikey", "koyu")[0]
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
      {inline(yat_k, height="74px")}<i style="width:2px;height:64px;background:rgba(244,241,234,.25)"></i>
      <div><p class="u" style="font-size:26px;font-weight:500;color:{PAPER}">{SLOGAN}</p>
      <p style="margin-top:8px;font-size:17px;letter-spacing:.14em;color:{ORANGE};font-weight:700">QR'LI İSİMLİK · DİJİTAL
      KARTVİZİT · 3D BASKI</p></div></div>""", 1920, 200, os.path.join(sh, "banner_1920x200.png"))
    for sc, fn in ((1, "banner_mobil_400x100.png"), (2, "banner_mobil_800x200.png")):
        P.png(f"""<div style="{dark};height:100px;display:grid;place-items:center">{inline(yat_k, height="44px")}</div>""",
              400, 100, os.path.join(sh, fn), scale=sc)
    P.png(f"""<div style="{dark};height:800px;display:grid;place-items:center">{inline(sim_k, height="400px")}</div>""",
          800, 800, os.path.join(sh, "logo_kare_800.png"))
    P.png(f"""<div style="{dark};height:1200px;display:flex;flex-direction:column;align-items:center;justify-content:center;
      gap:70px;background-image:{stripes_bg(PAPER, .04, 30)}">{inline(dik_k, height="430px")}
      <p class="u" style="font-size:52px;font-weight:500;color:{PAPER}">{SLOGAN}</p></div>""",
          1600, 1200, os.path.join(sh, "hakkinda_kapak_4x3.png"))
    _, sw, shh = lockup(n, "simge", "koyu")
    P.png(wide_graphic(sim_k, sw / shh), 1920, 1080, os.path.join(sh, "hakkinda_genis_16x9.png"))

    # ---- Instagram: profil ve öne çıkanlar
    P.png(f"""<div style="{dark};height:1080px;display:grid;place-items:center">{inline(sim_k, height="520px")}</div>""",
          1080, 1080, os.path.join(ig, "profil_1080.png"))
    for key, (_, label) in ICONS.items():
        P.png(f"""<div style="{dark};height:1920px;display:grid;place-items:center">
          <div style="width:620px;height:620px;border-radius:50%;background:{CHAR};display:grid;place-items:center;
          box-shadow:inset 0 0 0 6px rgba(255,90,31,.9)"><div style="width:300px">{icon_svg(key, ORANGE, 1.5)}</div>
          </div></div>""", 1080, 1920, os.path.join(hl, f"{key}.png"))

    # ---- Instagram: gönderiler (1080 × 1350)
    head = f'<div style="position:absolute;left:80px;top:76px">{inline(yat_k, height="58px")}</div>'
    stripe = (f'<div style="position:absolute;left:0;right:0;bottom:0;height:300px;background-image:'
              f'{stripes_bg(PAPER, .06, 26)};-webkit-mask-image:linear-gradient(transparent,#000)"></div>')
    P.png(f"""<div style="{dark};height:1350px;position:relative;overflow:hidden">{stripe}{head}
      <div style="position:absolute;right:-190px;bottom:-330px;opacity:.1">{inline(sim_k, height="700px")}</div>
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
        <p class="u" style="margin-top:6px;font-size:40px;font-weight:700">1 adet <span style="color:{ORANGE}">1.200 TL
        </span> · 2 adet <span style="color:{ORANGE}">1.500 TL</span></p></div></div></div>""",
          1080, 1350, os.path.join(ig, "gonderi_2_urun.png"))

    steps = [("Shopier'dan sipariş verin", "Adet seçin, ödemeyi güvenle Shopier'dan yapın."),
             ("Bilgilerinizi gönderin", "Logo, telefon, Instagram, konum ve IBAN: hepsi tek QR'a."),
             ("Onaylayın, basalım", "Tasarımı onayınıza sunarız; 3D basıp kargoya veririz.")]
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
      <div style="position:absolute;left:0;right:0;top:170px;display:grid;place-items:center">{inline(yat_k, height="70px")}</div>
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
    name, desc, _, _, story, _ = YONLER[n]
    yat_a, yat_k = lockup(n, "yatay", "acik")[0], lockup(n, "yatay", "koyu")[0]
    dik_a = lockup(n, "dikey", "acik")[0]
    sim_a, sim_k = lockup(n, "simge", "acik")[0], lockup(n, "simge", "koyu")[0]
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
      <div style="position:absolute;left:96px;top:96px">{inline(yat_k, height="70px")}</div>
      <div style="position:absolute;left:96px;bottom:110px"><p class="k">MARKA KILAVUZU · 2026</p>
      <h1 class="u" style="margin-top:20px;font-size:92px;line-height:1.02;font-weight:700;letter-spacing:-.02em">
      Katman<br>katman,<br><span style="color:{ORANGE}">size özel.</span></h1></div>
      <div style="position:absolute;right:-90px;top:150px">{inline(sim_k, height="600px")}</div></div>""")
    pages.append(f"""<div class="pg"><p class="k">01 · HİKÂYE VE LOGO</p><h2>Ürünün kendisinden bir logo</h2>
      <p class="lead">BOYDE LABS bir 3D baskı atölyesi: QR'lı akıllı isimlikleri ve işletmelere özel dijital kartvizit
      sitelerini tasarlayıp kendi yazıcılarında basıyor. Logo ({name}): {desc}</p>
      <div class="grid" style="grid-template-columns:1.1fr 1fr">
        <div class="box" style="height:430px;background:{INK}">{inline(sim_k, height="300px")}<small>simge</small></div>
        <div style="display:flex;flex-direction:column;justify-content:center;gap:26px;font-size:20px;line-height:1.5">
          {"".join(f"<p><b>{k}:</b> {v}</p>" for k, v in story)}
          <p><b>Söz:</b> “{SLOGAN}”</p></div></div>{no(1)}</div>""")
    pages.append(f"""<div class="pg"><p class="k">02 · LOGO KULLANIMLARI</p><h2>Yatay, dikey, simge</h2>
      <p class="lead">Önce yatay logo; dar ve kare alanlarda dikey; profil fotoğrafı, uygulama simgesi ve küçük
      boyutlarda yalnız simge. Açık zeminde mürekkep, koyu zeminde kâğıt rengi.</p>
      <div class="grid" style="grid-template-columns:1.6fr 1fr 1fr;grid-template-rows:200px 200px">
        <div class="box" style="background:#fff">{inline(yat_a, height="78px")}<small>yatay · açık</small></div>
        <div class="box" style="background:#fff;grid-row:span 2">{inline(dik_a, height="210px")}<small>dikey</small></div>
        <div class="box" style="background:#fff">{inline(sim_a, height="110px")}<small>simge</small></div>
        <div class="box" style="background:{INK}">{inline(yat_k, height="78px")}<small>yatay · koyu</small></div>
        <div class="box" style="background:{INK}">{inline(sim_k, height="110px")}<small>simge · koyu</small></div>
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
    pages.append(f"""<div class="pg"><p class="k">04 · YAZI TİPLERİ</p><h2>Unbounded ve Space Grotesk</h2>
      <p class="lead">İkisi de ücretsiz (SIL Open Font License) ve Türkçe harflerin hepsi var; Google Fonts'ta bulunur.</p>
      <div class="grid" style="grid-template-columns:1fr 1fr">
        <div class="box" style="background:#fff;place-items:start;padding:36px;height:440px;align-content:start">
          <p class="k" style="color:{GRAY}">BAŞLIK · LOGO</p><p class="u" style="margin-top:14px;font-size:68px;font-weight:700;
          line-height:1">Unbounded</p><p class="u" style="margin-top:22px;font-size:30px;font-weight:500;line-height:1.3">
          Katman katman,<br>size özel.</p><p class="u" style="margin-top:22px;font-size:20px;font-weight:300">
          ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ 0123456789</p><p style="margin-top:16px;font-size:16px;color:{GRAY}">Light 300 ·
          Medium 500 · Bold 700</p></div>
        <div class="box" style="background:#fff;place-items:start;padding:36px;height:440px;align-content:start">
          <p class="k" style="color:{GRAY}">METİN</p><p style="margin-top:14px;font-size:68px;font-weight:700;line-height:1">
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
        {''.join(f'<div class="box" style="background:#fff;overflow:hidden"><div style="{st}">{inline(yat_a, height="40px")}</div>'
                 f'<small style="color:#c0392b">✕ {t}</small></div>' for st, t in (
                     ("transform:scaleX(1.5)", "esnetmeyin"), ("filter:hue-rotate(160deg)", "rengini değiştirmeyin"),
                     ("filter:drop-shadow(6px 6px 0 #888)", "gölge, efekt eklemeyin"),
                     ("transform:rotate(-12deg)", "döndürmeyin")))}</div>
      <div class="grid" style="grid-template-columns:1fr 1fr;grid-template-rows:200px;margin-top:22px">
        <div class="box" style="background:{INK}">{inline(yat_k, height="70px")}<small style="color:#2e9b57">✓ koyu zeminde kâğıt rengi</small></div>
        <div class="box" style="background:{SAND}">{inline(yat_a, height="70px")}<small style="color:#2e9b57">✓ açık zeminde mürekkep</small></div>
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
    n = int(sys.argv[sys.argv.index("--yon") + 1]) if "--yon" in sys.argv else 1
    for d in ("logo", "shopier", "instagram"):
        shutil.rmtree(os.path.join(OUT, d), ignore_errors=True)
    os.makedirs(OUT, exist_ok=True)
    with painter() as P:
        options_sheet(P, os.path.join(OUT, "secenekler.png"))
        print("seçenekler:", os.path.relpath(os.path.join(OUT, "secenekler.png"), A.ROOT))
        kit(P, n)
        guide(P, n)
    print(f"kit ({n} · {YONLER[n][0]}):", os.path.relpath(OUT, A.ROOT))


if __name__ == "__main__":
    main()
