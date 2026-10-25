"""PALOMA GRIDA – Süleyman Boylu (Satın Alma Müdürü) için QR'lı masa isimliği önerileri (10).

1–5 beyaz tabla, siyah ve mavi yazı; 6–10 siyah tabla, beyaz ve mavi detay. İsimlikte yalnız otel (logo + GRIDA),
ad soyad ve görev yazar; telefonlar, e-posta ve adres QR'ın açtığı kartvizit sayfasındadır (scripts/paloma_sayfa.py).

Logo: `paloma_isimlik/logo.png` (ya da .jpg) varsa çizilip kabartmaya çevrilir (koyu ya da saydam olmayan yerler
logo sayılır); yoksa yerine geçici "PALOMA" yazısı (Cinzel) konur.

Yapı Uzar, İNCE, Çalık ve Soylu isimlikleriyle aynı: 120 × 90 mm, köşeler R8, gövde 1 cm, yazılar 2 mm kabartma,
QR yüzeyle aynı hizada dolgu, 15° eğik sehpa. Her satırın en dar harf içi boşluğu ölçülür, öğeler arası ≥ 2 mm.

Çıktı : paloma_isimlik/<tasarım>.png, musteri_1.png (1–5), musteri_2.png (6–10), musteri_3.png (sayfa),
        musteri_katalog.pdf

Kullanım:
  python3 scripts/paloma_isimlik.py [anahtar ...]
"""
import json
import os
import sys

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import calik_isimlik as C  # noqa: E402
import ince_isimlik as N  # noqa: E402
import qr_sistemi as Q  # noqa: E402
import uzar_isimlik as I  # noqa: E402
import uzar_isimlik_baski as B  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "paloma_isimlik")
DATA = json.load(open(os.path.join(OUT_DIR, "bilgiler.json"), encoding="utf-8"))
BLACK, WHITE, BLUE = A.BLACK, A.WHITE, A.BLUE
SHOW = {BLACK: (36, 36, 40), WHITE: (246, 246, 242), BLUE: (30, 82, 196)}
NAMES = {BLACK: "siyah", WHITE: "beyaz", BLUE: "mavi"}
J = m3.JoinType.Round
X0, X1 = -54.0, 54.0
N.FONT_FILES.update({"cinzel": "Cinzel-Black.ttf", "sora": "Sora-SemiBold.ttf", "jost": "Jost-Bold.ttf",
                     "manrope": "Manrope-ExtraBold.ttf", "fraunces": "Fraunces-SemiBold.ttf",
                     "playfair": "PlayfairDisplay-Black.ttf", "michroma": "Michroma-Regular.ttf"})
t, Design = N.t, N.Design
WHITE_SC = {"body": WHITE, "fg": BLACK, "dark": False}
BLACK_SC = {"body": BLACK, "fg": WHITE, "dark": True}



def tr_upper(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


FIRST, LAST = (tr_upper(w) for w in DATA["isim"].split())
NAME = f"{FIRST} {LAST}"
TITLE = tr_upper(DATA["gorev"])
HOTEL = DATA["otel"].split()[-1].upper()                 # GRIDA (logo PALOMA'nın altında)
LOGO_FILE = next((os.path.join(OUT_DIR, f) for f in ("logo.png", "logo.jpg", "logo.jpeg")
                  if os.path.exists(os.path.join(OUT_DIR, f))), None)


def make_qr():
    import segno
    content = Q.https_url(DATA["sayfa_url"])
    natural = segno.make(content, error="m", micro=False).version
    q = segno.make(content, error="m", version=max(4, natural), micro=False, boost_error=True)
    return Q.Entry("sayfa", "KARTVİZİT", content, "KARTVİZİT", qr=q)


QR = make_qr()


# ---------------------------------------------------------------- logo

def traced_logo():
    """logo.png → çokgenler (saydam zeminde opak yerler, düz zeminde koyu yerler); 1 mm yüksekliğe ölçekli."""
    import cv2
    im = cv2.imread(LOGO_FILE, cv2.IMREAD_UNCHANGED)
    if im.ndim == 3 and im.shape[2] == 4 and im[:, :, 3].min() < 200:
        mask = im[:, :, 3] > 128
    else:
        g = cv2.cvtColor(im[:, :, :3], cv2.COLOR_BGR2GRAY) if im.ndim == 3 else im
        _, th = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        mask = th > 0
    cnts, hier = cv2.findContours(mask.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    h = mask.shape[0]
    rings = [[(float(x), float(h - y)) for x, y in c[:, 0]] for c in cnts if len(c) >= 3 and cv2.contourArea(c) > 4]
    cs = m3.CrossSection(rings, m3.FillRule.EvenOdd)
    b = cs.bounds()
    return cs.translate((-(b[0] + b[2]) / 2, -(b[1] + b[3]) / 2)).scale((1 / (b[3] - b[1]),) * 2)


_LOGO = {}


def logo(cx, cy, w, align="c", max_h=None):
    """Otel logosu, genişliği w mm (yükseklik max_h'yi aşmaz). Logo dosyası yoksa geçici PALOMA yazısı."""
    if "cs" not in _LOGO:
        _LOGO["cs"] = traced_logo() if LOGO_FILE else None
    if _LOGO["cs"] is None:
        cs = t("cinzel", "PALOMA", 10.0, 0, 0, "c", 2.2)
    else:
        cs = _LOGO["cs"]
    b = cs.bounds()
    k = w / (b[2] - b[0])
    if max_h:
        k = min(k, max_h / (b[3] - b[1]))
    cs = cs.scale((k, k))
    b = cs.bounds()
    dx = {"l": cx - b[0], "c": cx - (b[0] + b[2]) / 2, "r": cx - b[2]}[align]
    out = cs.translate((dx, cy - (b[1] + b[3]) / 2))
    return out.offset(0.12, J) if LOGO_FILE else out          # çizilen logoda ince yerler biraz kalınlaşsın


# ---------------------------------------------------------------- ortak öğeler

def qr_block(cx, cy, s, sc):
    """Beyaz tablada siyah kareler; siyah tablada beyaz karo (kareler gövde rengi)."""
    _, dark, _ = Q.shapes(QR, Q.module_for(QR, s), cx, cy)
    square = A.rrect(s, s, 1.6, cx, cy)
    return [(square - dark, WHITE)] if sc["dark"] else [(dark ^ square, BLACK)]


def small(text, cap, x, y, align="l", tr=0.6, max_w=None):
    """Küçük satırlar Manrope ExtraBold (4,8 mm'den küçük değil: çizgiler ≥ 0,8 mm, harf içleri ≥ 0,6 mm)."""
    return t("manrope", text, cap, x, y, align, tr, max_w)


def scan(d, cx, cy, s, col=BLUE, label="KARTVİZİT"):
    d.inlay += qr_block(cx, cy, s, d.sc)
    if label:
        d.add(label, small(label, 4.8, cx, cy - s / 2 - 7.2, "c", 0.5, s + 8), col)


# ad soyad yazı tipleri ve ince yerleri kalınlaştırma (mm, dışa)
NAME_FONT = {"cinzel": 0.1, "sora_xb": 0.0, "manrope": 0.0, "fraunces_b": 0.06, "jost": 0.0, "archivo": 0.0}
N.FONT_FILES.update({"sora_xb": "Sora-ExtraBold.ttf", "fraunces_b": "Fraunces-Black.ttf"})


def loosen(cs, shrink=0.15):
    """Ü ve İ noktaları (Cinzel'de baklava biçimli) küçültülür: noktalar arası ve harfle arası ≥ 0,5 mm kalsın."""
    return A.union(*[p.offset(-shrink, J) if p.area() < 2.5 else p for p in cs.decompose()])


def name_block(d, x, y_top, font, cap, align="l", col=None, two_lines=True, max_w=62.0, gap=None, tr=0.6):
    """Ad soyad (iki satır ya da tek satır). Döner: alt kenarın y'si."""
    col = d.sc["fg"] if col is None else col
    off = NAME_FONT.get(font, 0.0)
    th = (lambda cs: loosen(cs.offset(off, J), 0.12 + off)) if off else loosen  # noqa: E731
    if two_lines:
        l1 = th(t(font, FIRST, cap, x, y_top - cap, align, tr, max_w))
        g = gap if gap is not None else cap * 0.42
        l2 = th(t(font, LAST, cap, x, l1.bounds()[1] - g - cap, align, tr, max_w))
        d.add("ad", l1, col)
        d.add("soyad", l2, col)
        return l2.bounds()[1]
    l1 = th(t(font, NAME, cap, x, y_top - cap, align, tr, max_w))
    d.add("ad soyad", l1, col)
    return l1.bounds()[1]


def title_block(d, x, y_top, col, align="l", cap=4.8, one_line=False, max_w=62.0):
    """Görev: SATIN ALMA / MÜDÜRÜ (iki satır; tek satır yalnız genişlik yetiyorsa). Döner: alt kenarın y'si."""
    words = TITLE.split()
    lines = [TITLE] if one_line else [" ".join(words[:-1]), words[-1]]
    y = y_top - cap
    for k, ln in enumerate(lines):
        cs = small(ln, cap, x, y, align, 0.5, max_w)
        d.add("görev" if k == 0 else "görev 2", cs, col)
        y = cs.bounds()[1] - 2.2 - cap
    return cs.bounds()[1]


def hotel_line(d, x, y, col, align="l", cap=4.8):
    d.add("GRIDA", small(HOTEL, cap, x, y, align, 2.0), col)


def wave(x0, x1, y, amp, period, w, phase=0.0):
    xs = np.linspace(x0, x1, 120)
    pts = [(x, y + amp * np.sin(2 * np.pi * (x - x0) / period + phase)) for x in xs]
    return A.stroke(pts, w)


# ---------------------------------------------------------------- 1–5: beyaz tabla, siyah ve mavi

def p1_cizgi():
    d = Design("1_mavi_cizgi", "Mavi çizgi", "Mavi PALOMA ve GRIDA; iki satır büyük ad soyad (Cinzel), altında mavi "
               "çizgi ve görev; sağda QR.", WHITE_SC)
    d.add(None, logo(X0, 81.0, 34.0, "l", 7.0), BLUE)
    hotel_line(d, X0, 70.0, BLUE)
    yb = name_block(d, X0, 63.0, "cinzel", 7.0, max_w=62.0, tr=1.6)
    d.add(None, A.rect(X0, yb - 4.4, X0 + 24.0, yb - 2.8), BLUE)
    title_block(d, X0, yb - 7.4, BLACK)
    scan(d, X1 - 17.5, 46.0, 35.0)
    return d


def p2_serit():
    d = Design("2_sol_serit", "Sol şerit", "Sol kenarda boydan mavi şerit; yanında logo, ad soyad (Sora) ve mavi görev; "
               "sağda QR.", WHITE_SC)
    d.add(None, A.rrect(4.0, 70.0, 1.6, X0 + 2.0, 48.0), BLUE)
    x0 = X0 + 9.0
    d.add(None, logo(x0, 79.5, 30.0, "l", 6.0), BLUE)
    hotel_line(d, x0, 69.5, BLACK)
    yb = name_block(d, x0, 62.0, "sora_xb", 6.6, max_w=52.0)
    title_block(d, x0, yb - 4.6, BLUE, max_w=52.0)
    scan(d, X1 - 17.5, 46.0, 35.0)
    return d


def p3_bant():
    d = Design("3_mavi_bant", "Mavi üst bant", "Üstte boydan mavi bant, içinde oyma PALOMA · GRIDA; altında ad soyad ve "
               "görev, sağda QR.", WHITE_SC)
    band = A.rrect(108.0, 15.0, 3.0, 0, 76.0)
    lg = logo(-8.0, 76.0, 36.0, "r", 7.5).offset(0.15, J)
    gr = small(HOTEL, 4.4, 0.0, 76.0 - 2.2, "l", 2.2).offset(0.12, J)
    d.add(None, band - lg - gr - A.rect(-4.8, 72.2, -3.2, 79.8), BLUE)       # logo, ayraç ve GRIDA oyma
    d.lines["GRIDA (oyma)"] = gr
    yb = name_block(d, X0, 62.5, "manrope", 6.8, max_w=60.0)
    title_block(d, X0, yb - 4.6, BLUE)
    scan(d, X1 - 17.5, 42.5, 35.0)
    return d


def p4_cerceve():
    d = Design("4_ince_cerceve", "İnce çerçeve", "Panelin içinde ince mavi çerçeve; logo, ad soyad (Fraunces) ve görev "
               "solda, QR sağda.", WHITE_SC)
    fr = A.rrect(108.0, 74.0, 5.0, 0, 49.0) - A.rrect(104.8, 70.8, 3.4, 0, 49.0)
    d.add(None, fr, BLUE)
    x0 = X0 + 5.0
    d.add(None, logo(x0, 78.0, 30.0, "l", 6.0), BLUE)
    hotel_line(d, x0, 68.0, BLUE)
    yb = name_block(d, x0, 61.5, "fraunces_b", 6.8, max_w=50.0)
    title_block(d, x0, yb - 4.6, BLACK, max_w=50.0)
    scan(d, X1 - 24.0, 46.0, 34.0)
    return d


def p5_minimal():
    d = Design("5_minimal", "Minimal", "Bol boşluk: tek satır ad soyad (Jost), mavi görev; logo küçük, altta; sağda QR.",
               WHITE_SC)
    yb = name_block(d, X0, 74.0, "jost", 6.6, two_lines=False, max_w=64.0, tr=0.5)
    d.add(None, A.rect(X0, yb - 4.6, X0 + 10.0, yb - 3.0), BLUE)
    title_block(d, X0, yb - 7.6, BLUE, max_w=60.0)
    d.add(None, logo(X0, 24.5, 26.0, "l", 5.4), BLACK)
    hotel_line(d, X0, 13.0, BLUE)
    scan(d, X1 - 17.5, 46.0, 35.0, col=BLACK)
    return d


# ---------------------------------------------------------------- 6–10: siyah tabla, beyaz ve mavi

def p6_gece():
    d = Design("6_gece", "Gece", "Siyah tablada beyaz PALOMA, mavi GRIDA; iki satır ad soyad (Cinzel), mavi çizgi ve "
               "görev; sağda QR.", BLACK_SC)
    d.add(None, logo(X0, 81.0, 34.0, "l", 7.0), WHITE)
    hotel_line(d, X0, 70.0, BLUE)
    yb = name_block(d, X0, 63.0, "cinzel", 7.0, max_w=62.0, tr=1.6)
    d.add(None, A.rect(X0, yb - 4.4, X0 + 24.0, yb - 2.8), BLUE)
    title_block(d, X0, yb - 7.4, BLUE)
    scan(d, X1 - 17.5, 46.0, 35.0)
    return d


def p7_kose():
    d = Design("7_mavi_kose", "Mavi köşe", "Sağ üst köşede mavi eğik şerit; solda QR, sağda logo, ad soyad (Sora) ve görev.",
               BLACK_SC)
    d.add(None, A.polygon([(30.0, 88.0), (44.0, 88.0), (60.0, 72.0), (60.0, 58.0)]) ^ I.outline().offset(-3.2, J), BLUE)
    cx = 17.0
    d.add(None, logo(cx, 75.0, 30.0, "c", 6.2), WHITE)
    hotel_line(d, cx, 65.0, BLUE, "c")
    yb = name_block(d, cx, 57.5, "sora_xb", 6.4, align="c", max_w=56.0)
    title_block(d, cx, yb - 4.6, BLUE, align="c", max_w=56.0)
    scan(d, X0 + 17.5, 46.0, 35.0, col=WHITE)
    return d


def p8_alt_bant():
    d = Design("8_alt_bant", "Alt bant", "Altta boydan mavi bant, içinde oyma görev; üstte logo ve büyük ad soyad "
               "(Manrope); sağda QR.", BLACK_SC)
    band = A.rrect(108.0, 11.0, 2.6, 0, 16.5)
    title = small(TITLE, 4.6, X0 + 6.0, 16.5 - 2.3, "l", 0.8, 96.0).offset(0.12, J)
    d.add(None, band - title, BLUE)
    d.lines["görev (oyma)"] = title
    d.add(None, logo(X0, 81.0, 32.0, "l", 6.6), WHITE)
    hotel_line(d, X0, 70.5, BLUE)
    name_block(d, X0, 62.5, "manrope", 7.0, max_w=60.0)
    scan(d, X1 - 17.0, 53.0, 34.0, label=None)
    d.add("KARTVİZİT", small("KARTVİZİT", 4.8, X1 - 17.0, 53.0 - 17.0 - 7.2, "c", 0.5, 42.0), WHITE)
    return d


def badge(cx, cy, r):
    """Mavi yuvarlak rozet, içinde oyma baş harfler."""
    ini = t("cinzel", FIRST[0] + LAST[0], r * 0.62, 0, 0, "c", 0.6).offset(0.25, J)
    b = ini.bounds()
    ini = ini.translate((cx - (b[0] + b[2]) / 2, cy - (b[1] + b[3]) / 2))
    ring = A.circle(r, cx, cy, 120) - A.circle(r - 1.6, cx, cy, 120)
    inner = A.circle(r - 3.0, cx, cy, 120) - ini
    return ring + inner


def p9_rozet():
    d = Design("9_rozet", "Rozet", "Solda mavi rozette oyma SB; yanında logo, ad soyad ve görev; sağda QR.", BLACK_SC)
    d.add(None, badge(X0 + 12.0, 70.0, 12.0), BLUE)
    x0 = X0 + 29.0
    d.add(None, logo(x0, 74.5, 26.0, "l", 5.4), WHITE)
    hotel_line(d, x0, 63.0, BLUE)
    yb = name_block(d, X0, 52.0, "sora_xb", 6.0, two_lines=False, max_w=64.0, tr=0.4)
    title_block(d, X0, yb - 4.6, BLUE, max_w=60.0)
    scan(d, X1 - 17.5, 44.0, 35.0, col=WHITE)
    return d


def p10_dalga():
    d = Design("10_dalga", "Dalga", "Belek'in denizi: altta boydan iki mavi dalga; üstte logo, ad soyad (Archivo) ve görev; "
               "sağda QR.", BLACK_SC)
    for k in range(2):                                                   # en altta, boydan iki dalga
        d.add(None, wave(X0, X1, 11.8 + 3.6 * k, 0.9, 13.0, 1.4, phase=1.1 * k) ^ I.outline().offset(-3.2, J), BLUE)
    d.add(None, logo(X0, 81.0, 32.0, "l", 6.6), WHITE)
    hotel_line(d, X0, 70.5, BLUE)
    yb = name_block(d, X0, 63.0, "archivo", 6.0, max_w=60.0, tr=0.6)
    title_block(d, X0, yb - 4.0, WHITE)
    scan(d, X1 - 17.5, 49.0, 35.0)
    return d


DESIGNS = [p1_cizgi, p2_serit, p3_bant, p4_cerceve, p5_minimal, p6_gece, p7_kose, p8_alt_bant, p9_rozet, p10_dalga]


# ---------------------------------------------------------------- katılar, kontroller, görseller

def solids(d):
    out = I.outline()
    body = B.flat_chamfer(out.extrude(B.T), out)
    parts, pockets = [], []
    for cs, col in d.inlay:
        cs = cs ^ out.offset(-1.0, J)
        parts.append((f"Dolgu ({NAMES[col]})", cs.extrude(B.INLAY).translate((0, 0, B.T - B.INLAY)), col))
        pockets.append(cs)
    if pockets:
        body = body - A.union(*pockets).extrude(B.INLAY + 0.01).translate((0, 0, B.T - B.INLAY))
    taken, by_col = A.empty(), {}
    for cs, col in reversed(d.raised):
        part = (cs ^ out.offset(-1.0, J)) - taken
        taken = taken + cs
        by_col[col] = by_col.get(col, A.empty()) + part
    for col, cs in by_col.items():
        parts.append((f"Kabartma ({NAMES[col]})", cs.extrude(B.RELIEF).translate((0, 0, B.T)), col))
    return [(f"Panel ({NAMES[d.sc['body']]})", body, d.sc["body"])] + parts


def build(fn):
    d = fn()
    d.parts = solids(d)
    d.stand, (z0, y0) = B.stand()
    d.shown = B.assembled(d.parts, z0, y0) + [("Sehpa", d.stand, d.sc["body"])]
    return d


def mesh(parts):
    return [(*A.mesh_arrays(m), SHOW[c]) for _, m, c in parts]


def qr_check(d):
    im = render(mesh(d.parts), 1600, A.R_TOP, light=False, margin=0.03)
    bg = Image.new("RGB", im.size, (150, 152, 158))
    bg.paste(im, (0, 0), im)
    im = bg.convert("L")
    ppm = im.width * (1 - 2 * 0.03) / I.PW
    sim = Q.simulate(im, ppm, 1.0, **dict(Q.SIM_CASES)["hepsi birden"])
    return QR.content in Q.decode(im), QR.content in Q.decode(sim)


def font_ui(n, f="Outfit-SemiBold.ttf"):
    return ImageFont.truetype(os.path.join(A.FONT_DIR, f), n)


def sheet(d, i):
    W, H = 1500, 700
    canvas = Image.new("RGB", (W, H), (236, 239, 244))
    dr = ImageDraw.Draw(canvas)
    views = [(rotation(0, -90), "Önden, sehpada (120 × 90 mm)", 0.85), (rotation(-28, -68), "Masada (3/4)", None),
             (rotation(-90, -90), "Yandan: 15° eğik", None)]
    boxes = [(30, 130, 700, 630), (720, 130, 1240, 630), (1260, 130, 1470, 630)]
    parts = mesh(d.shown)
    for (R, label, flat), (x0, y0, x1, y1) in zip(views, boxes):
        dr.rounded_rectangle((x0, y0, x1, y1), 22, fill=(146, 153, 166))
        im = A.fit_into(render(parts, 1200, R, flat=flat, margin=0.02), x1 - x0 - 40, y1 - y0 - 60)
        canvas.paste(im, (x0 + (x1 - x0 - im.width) // 2, y0 + 40 + (y1 - y0 - 40 - im.height) // 2), im)
        dr.text((x0 + 16, y0 + 10), label, fill=(236, 239, 244), font=font_ui(18))
    dr.text((30, 18), f"{i}. {d.title.upper()}", fill=(24, 26, 30), font=font_ui(32))
    dr.text((30, 62), d.desc, fill=(80, 86, 98), font=font_ui(19))
    worst = min((v[0] for v in d.metrics.values()), default=9)
    dr.text((30, 94), f"Gövde 1 cm, kabartma 2 mm · en dar harf içi boşluk {worst:.2f} mm · QR "
                      f"{'okundu' if d.qr[0] else 'OKUNMADI'}{', benzetimde de' if d.qr[1] else ''}",
            fill=(22, 120, 60) if d.qr[0] and worst >= 0.6 else (200, 30, 38), font=font_ui(19))
    canvas.save(os.path.join(OUT_DIR, d.key + ".png"))


NAVY, BLUE_UI, PAPER, INK, MUTED = (14, 26, 56), SHOW[BLUE], (246, 247, 250), (18, 22, 32), (96, 102, 116)


def header(dr, W, page, n, sub):
    dr.rectangle((0, 0, W, 250), fill=NAVY)
    big = ImageFont.truetype(os.path.join(A.FONT_DIR, "Cinzel-Black.ttf"), 84)
    dr.text((70, 40), "PALOMA", font=big, fill=(244, 244, 246))
    x = 76 + dr.textlength("PALOMA", font=big) + 28
    dr.text((x, 74), HOTEL, font=font_ui(40), fill=(120, 160, 240))
    dr.text((70, 168), sub, font=font_ui(30), fill=(200, 208, 228))
    s = f"{page}/{n}"
    dr.text((W - 90 - dr.textlength(s, font=font_ui(40)), 96), s, font=font_ui(40), fill=(170, 180, 204))
    dr.rectangle((0, 246, W, 254), fill=BLUE_UI)


def footer(dr, W, H, text):
    dr.rounded_rectangle((60, H - 150, W - 60, H - 70), 22, fill=NAVY)
    dr.text((W / 2 - dr.textlength(text, font=font_ui(30)) / 2, H - 128), text, font=font_ui(30), fill=(244, 244, 246))


def catalog(ds):
    """musteri_1 (1–5, beyaz tabla), musteri_2 (6–10, siyah tabla), musteri_3 (QR'ın açtığı sayfa), PDF."""
    W, H = 1654, 2339
    f = font_ui
    pages = []
    groups = [(ds[:5], "Beyaz tabla · siyah ve mavi yazı"), (ds[5:], "Siyah tabla · beyaz ve mavi detay")]
    n = 3
    for p, (group, sub) in enumerate(groups):
        im = Image.new("RGB", (W, H), PAPER)
        dr = ImageDraw.Draw(im)
        header(dr, W, p + 1, n, f"{DATA['isim']} · {DATA['gorev']} · QR'lı masa isimliği · {sub}")
        y = 285
        for line in ("İsimlikte otel, ad soyad ve görev yazar; telefonlar, e-posta ve adres QR'ın açtığı kartvizit "
                     "sayfasındadır.",):
            for row in N.wrap(dr, line, f(27), W - 140):
                dr.text((70, y), row, font=f(27), fill=INK)
                y += 40
        top, gap, cw = 395, 50, (W - 3 * 60) // 2
        ch = (H - top - 190 - 2 * gap) // 3
        for k, d in enumerate(group):
            x0, y0 = 60 + (k % 2) * (cw + 60), top + (k // 2) * (ch + gap)
            dr.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 28, fill=(255, 255, 255), outline=(222, 226, 234))
            num = ds.index(d) + 1
            dr.ellipse((x0 + 26, y0 + 24, x0 + 86, y0 + 84), fill=NAVY)
            dr.text((x0 + 56 - dr.textlength(str(num), font=f(32)) / 2, y0 + 35), str(num), font=f(32),
                    fill=(244, 244, 246))
            dr.text((x0 + 104, y0 + 30), d.title, font=f(38), fill=INK)
            img = A.fit_into(render(mesh(d.shown), 1300, rotation(0, -90), flat=0.85, margin=0.02), cw - 70, ch - 190)
            im.paste(img, (x0 + (cw - img.width) // 2, y0 + 100 + (ch - 190 - img.height) // 2), img)
            ty = y0 + ch - 78
            for line in N.wrap(dr, d.desc, f(25), cw - 60)[:2]:
                dr.text((x0 + 30, ty), line, font=f(25), fill=MUTED)
                ty += 33
        x0, y0 = 60 + cw + 60, top + 2 * (ch + gap)
        dr.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 28, fill=(255, 255, 255), outline=(222, 226, 234))
        img = A.fit_into(render(mesh(group[0].shown), 1200, rotation(-28, -68), margin=0.02), cw - 80, ch - 230)
        im.paste(img, (x0 + (cw - img.width) // 2, y0 + 30), img)
        ty = y0 + ch - 190
        for line in ("12 × 9 cm, gövde 1 cm, köşeler yuvarlak", "Yazılar 2 mm kabartma, QR düz ve keskin",
                     "Masa sehpası dahil, 15° eğik durur"):
            dr.ellipse((x0 + 34, ty + 9, x0 + 48, ty + 23), fill=BLUE_UI)
            dr.text((x0 + 64, ty), line, font=f(26), fill=MUTED)
            ty += 50
        footer(dr, W, H, "Beğendiğiniz tasarımın numarasını yazmanız yeterli." if p else
               "Ölçü 12 × 9 cm · 1 cm kalın · kabartma yazı · masa sehpası dahil")
        pages.append(im)
    shot = os.path.join(OUT_DIR, "sayfa_onizleme.png")
    im = Image.new("RGB", (W, H), PAPER)
    dr = ImageDraw.Draw(im)
    header(dr, W, 3, n, "QR'ı okutunca açılan kartvizit sayfası")
    y = 300
    for line in ("Telefonla QR okutulunca Süleyman Bey'in kartviziti açılır: tek dokunuşla arama (cep ve şirket hattı), "
                 "WhatsApp, e-posta, otelin konumu ve rehbere kaydetme.",
                 "Bilgiler değişirse yalnız sayfa güncellenir; isimlik ve QR aynı kalır."):
        for row in N.wrap(dr, line, f(28), W - 140):
            dr.text((70, y), row, font=f(28), fill=INK)
            y += 42
        y += 10
    if os.path.exists(shot):
        s = Image.open(shot).convert("RGB")
        s = A.fit_into(s, W - 140, H - y - 260)
        im.paste(s, ((W - s.width) // 2, y + 30))
    footer(dr, W, H, f"Sayfa adresi: {DATA['sayfa_url'].replace('https://', '').rstrip('/')}")
    pages.append(im)
    for k, pg in enumerate(pages, 1):
        pg.save(os.path.join(OUT_DIR, f"musteri_{k}.png"), optimize=True)
        pg.convert("RGB").save(os.path.join(OUT_DIR, f"musteri_{k}.jpg"), "JPEG", quality=90, optimize=True)
    pages[0].save(os.path.join(OUT_DIR, "musteri_katalog.pdf"), save_all=True, append_images=pages[1:], resolution=200)


def check(i):
    d = build(DESIGNS[i - 1])
    d.metrics = {k: B.line_metrics(cs) for k, cs in d.lines.items()}
    d.qr = qr_check(d)
    sheet(d, i)
    bad = {k: v for k, v in d.metrics.items() if v[0] < 0.6 or v[2] > 6.0}
    return (f"{d.key:18s} QR {d.qr}  simgelerde 1,2 mm'den ince %{C.thin_shapes(d)}  dar/ince satırlar: {bad or 'yok'}"
            f"  sıkışık: {C.crowded(d) or 'yok'}")


def main():
    from multiprocessing import Pool
    os.makedirs(OUT_DIR, exist_ok=True)
    print("logo:", os.path.relpath(LOGO_FILE, A.ROOT) if LOGO_FILE else "yok (geçici PALOMA yazısı)")
    only = sys.argv[1:]
    if only == ["katalog"]:
        catalog([build(fn) for fn in DESIGNS])
        return
    todo = [i for i, fn in enumerate(DESIGNS, 1) if not only or any(o in fn.__name__ for o in only)]
    with Pool(4) as pool:
        for line in pool.map(check, todo):
            print(line)
    if not only:
        catalog([build(fn) for fn in DESIGNS])


if __name__ == "__main__":
    main()
