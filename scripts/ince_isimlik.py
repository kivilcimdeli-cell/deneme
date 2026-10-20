"""İNCE OTO LASTİK – tek QR'lı tezgâh isimliği önerileri (10): 7 beyaz zemin (siyah, kırmızı yazı), 3 siyah zemin
(beyaz, kırmızı yazı). Her biri ayrı fikir ve ayrı yazı tipiyle: plaka (Barlow Condensed), minimal (Bebas Neue),
kırmızı blok (Archivo Black, oyma yazı), yol (Russo One, asfalt şerit), dama bayrağı (Saira Condensed), hız
çizgileri (Teko, italik), jant (Oswald, sade jant simgesi), kırmızı köşe, kırmızı çerçeve, oklar.

Uzar Oto Lastik'in basılan isimliğiyle aynı yapı: 120 × 90 mm (4:3), köşeler R8, siyah ya da beyaz gövde 1 cm,
yazılar ve şekiller 2 mm kabartma, QR yüzeyle aynı hizada (beyaz zeminde siyah kareler, siyah zeminde beyaz karo),
15° eğik sehpa. Süsler kalın ve sade (en ince yeri ≥ 1,2 mm); küçük satırlar Outfit ExtraBold; her yazı satırının
en dar harf içi boşluğu ölçülür.

QR: işletmenin sitesi henüz yok. Örneklerde QR telefonu arar (TEL:+905458533070); `ince_isimlik/bilgiler.json`
→ `sayfa_url` yazılınca site adresine döner. Yoğunluğu son hâline benzesin diye en az sürüm 4.

Çıktı : ince_isimlik/<tasarım>.png, ince_isimlik/musteri_1.png, musteri_2.png, musteri_katalog.pdf

Kullanım:
  python3 scripts/ince_isimlik.py [anahtar ...]
"""
import json
import os
import sys

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import qr_sistemi as Q  # noqa: E402
import uzar_anahtarlik as U  # noqa: E402
import uzar_isimlik as I  # noqa: E402
import uzar_isimlik_baski as B  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "ince_isimlik")
DATA = json.load(open(os.path.join(OUT_DIR, "bilgiler.json"), encoding="utf-8"))
TEL = Q.phone_e164(DATA["telefon"])
PHONE = Q.phone_display(TEL)
BLACK, WHITE, RED = A.BLACK, A.WHITE, A.RED
SHOW = B.SHOW
NAMES = {BLACK: "siyah", WHITE: "beyaz", RED: "kırmızı"}
J = m3.JoinType.Round
X0, X1 = -54.0, 54.0                     # içerik kenarları


def make_qr():
    import segno
    content = Q.https_url(DATA["sayfa_url"]) if DATA.get("sayfa_url") else f"TEL:+{TEL}"
    natural = segno.make(content, error="m", micro=False).version
    q = segno.make(content, error="m", version=max(4, natural), micro=False, boost_error=True)
    return Q.Entry("sayfa", "TARA", content, PHONE, qr=q)


QR = make_qr()


# ---------------------------------------------------------------- parçalar

def heavy():
    return I.heavy()


def bold():
    return I.bold()


SMALL = A.Font("Outfit-ExtraBold.ttf")


def word(s, f, cap, x, y, align="l", tracking=0.0, max_w=None):
    return B.loosen_dots(I.text(f, s, cap, x, y, align, tracking, max_w))


def ince(cap, x, y, align="l", max_w=None):
    return word("İNCE", heavy(), cap, x, y, align, cap * 0.05, max_w)


def scheme(dark):
    return {"body": BLACK if dark else WHITE, "fg": WHITE if dark else BLACK, "dark": dark}


def arrow(x, y, h=7.8):
    return A.polygon([(x, y - h / 2), (x + h * 0.82, y), (x, y + h / 2)])


def qr_block(cx, cy, s, sc, frame=False):
    """QR (yüzeyle aynı hizada dolgu): beyaz zeminde siyah kareler, siyah zeminde beyaz karo. frame: ince çerçeve."""
    module = Q.module_for(QR, s)
    _, dark, _ = Q.shapes(QR, module, cx, cy)
    square = A.rrect(s, s, 1.6, cx, cy)
    inlay = [(square - dark, WHITE)] if sc["dark"] else [(dark ^ square, BLACK)]
    if frame:
        g, w = 1.8, 1.1
        inlay.append((A.rrect(s + 2 * (g + w), s + 2 * (g + w), 2.6, cx, cy) - A.rrect(s + 2 * g, s + 2 * g, 1.8, cx, cy),
                      sc["fg"]))
    return inlay


class Design:
    def __init__(self, key, title, desc, sc):
        self.key, self.title, self.desc, self.sc = key, title, desc, sc
        self.raised, self.inlay, self.lines = [], [], {}

    def add(self, name, cs, colour):
        """Kabartma; `name` verilirse yazı satırı olarak ölçülür."""
        self.raised.append((cs, colour))
        if name:
            self.lines[name] = cs
        return cs


# ---------------------------------------------------------------- yazı tipleri ve sade şekiller

FONT_FILES = {"russo": "RussoOne-Regular.ttf", "teko": "Teko-Bold.ttf", "archivo": "ArchivoBlack-Regular.ttf",
              "saira": "SairaCondensed-Black.ttf", "oswald": "Oswald-Bold.ttf", "bebas": "BebasNeue-Regular.ttf",
              "barlow": "BarlowCondensed-Black.ttf", "outfit": "Outfit-ExtraBold.ttf", "lexend": "Lexend-ExtraBold.ttf"}
_FONTS = {}


def font(k):
    if k not in _FONTS:
        _FONTS[k] = A.Font(FONT_FILES[k])
    return _FONTS[k]


def t(k, s, cap, x, y, align="l", tr=0.0, max_w=None, shear=0.0):
    """Yazı (İ / Ö noktaları harften ayrık). shear: italik (derece, yazının orta çizgisi etrafında)."""
    cs = I.text(font(k), s, cap, x, y, align, tr, max_w)
    if shear:
        cs = A.shear(cs.translate((0, -y)), shear).translate((0, y))
    return B.loosen_dots(cs)


def bar(x0, x1, y, h):
    """Yuvarlak uçlu kalın çizgi."""
    return A.rrect(x1 - x0, h, h / 2 - 0.01, (x0 + x1) / 2, y)


# ---------------------------------------------------------------- beyaz zemin (siyah, kırmızı yazı)

def d1_plaka():
    d = Design("1_plaka", "Plaka", "Araç plakası gibi: siyah çerçeve, solda kırmızı şerit, içinde İNCE OTO LASTİK.",
               scheme(False))
    cy = 68.0
    d.add(None, A.rrect(108, 32, 4.0, 0, cy) - A.rrect(104.4, 28.4, 2.4, 0, cy), BLACK)
    strip = A.rrect(12.0, 25.6, 1.6, -45.4, cy)
    d.add("7/24 şerit", strip - t("barlow", "7/24", 6.6, 0, 0, "c", 0.3).rotate(90).translate((-45.4, cy)), RED)
    d.add("plaka", t("barlow", "İNCE OTO LASTİK", 12.5, 7.0, cy, "c", 0.7, 84.0), BLACK)
    d.add("7/24 HİZMET", t("outfit", "7/24 HİZMET", 5.0, X0, 41.0, "l", 0.9), RED)
    d.add("telefon", t("outfit", PHONE, 5.6, X0, 29.0, "l", 0.4, 64.0), BLACK)
    d.add("QR'I OKUTUN", t("outfit", "QR'I OKUTUN", 4.4, X0, 17.0, "l", 0.9), BLACK)
    d.add(None, arrow(t("outfit", "QR'I OKUTUN", 4.4, X0, 17.0, "l", 0.9).bounds()[2] + 2.5, 17.0, 5.0), RED)
    d.inlay += qr_block(35.0, 29.0, 38.0, d.sc)
    return d


def d2_minimal():
    d = Design("2_minimal", "Minimal", "Bol boşluk: büyük ince uzun İNCE, kırmızı çizgi, harf aralıklı OTO LASTİK.",
               scheme(False))
    d.add("İNCE", t("bebas", "İNCE", 28.0, X0, 64.0, "l", 1.2), BLACK)
    d.add(None, bar(X0, -16.0, 43.0, 1.6), RED)
    d.add("OTO LASTİK", t("outfit", "OTO LASTİK", 5.0, X0, 35.5, "l", 2.0), RED)
    d.add("7/24 HİZMET", t("outfit", "7/24 HİZMET", 4.4, X0, 24.5, "l", 1.2), BLACK)
    d.add("telefon", t("outfit", PHONE, 5.0, X0, 15.0, "l", 0.4), BLACK)
    d.inlay += qr_block(32.0, 44.0, 44.0, d.sc)
    d.add("TARA", t("bebas", "TARA", 6.4, 32.0, 15.0, "c", 1.6), BLACK)
    return d


def d3_kirmizi_blok():
    d = Design("3_kirmizi_blok", "Kırmızı blok", "Solda kırmızı blok, içinde oyma beyaz yazılar; sağda QR ve telefon.",
               scheme(False))
    cx = -31.0
    block = A.rrect(46.0, 74.0, 4.0, cx, 47.0)
    cut = A.union(t("archivo", "İNCE", 12.0, cx, 72.0, "c", 0.4, 40.0),
                  t("archivo", "OTO", 6.6, cx, 56.5, "c", 0.6),
                  t("archivo", "LASTİK", 6.6, cx, 46.5, "c", 0.6, 40.0),
                  t("archivo", "7/24", 11.0, cx, 28.5, "c", 0.4),
                  t("outfit", "HİZMET", 4.4, cx, 17.5, "c", 1.0))
    d.add("blok yazıları", block - cut, RED)
    d.add("QR'I OKUTUN", t("outfit", "QR'I OKUTUN", 4.2, 31.0, 79.5, "c", 0.6, 44.0), RED)
    d.inlay += qr_block(31.0, 50.0, 44.0, d.sc)
    d.add("telefon", t("outfit", PHONE, 5.0, 31.0, 18.5, "c", 0.3, 47.0), BLACK)
    return d


def d4_yol():
    d = Design("4_yol", "Yol", "Altta asfalt şerit: kesik yol çizgileri arasında telefon; üstte İNCE OTO LASTİK.",
               scheme(False))
    road, y = A.rrect(108.0, 12.0, 2.6, 0, 16.0), 16.0
    phone = t("outfit", PHONE, 5.4, 0.0, y, "c", 0.5)
    w = phone.bounds()[2]
    dashes = A.union(*[A.rect(x0, y - 0.8, x0 + 6.5, y + 0.8) for x0 in (-w - 19.0, -w - 9.5, w + 3.0, w + 12.5)])
    d.add("yol + telefon", road - phone - dashes, BLACK)
    d.add("İNCE", t("russo", "İNCE", 15.0, X0, 70.0, "l", 0.6), BLACK)
    d.add("OTO LASTİK", t("russo", "OTO LASTİK", 6.0, X0, 53.5, "l", 0.6, 60.0), RED)
    d.add("7/24 HİZMET", t("outfit", "7/24 HİZMET", 4.6, X0, 42.5, "l", 0.9), BLACK)
    d.inlay += qr_block(34.0, 48.0, 40.0, d.sc)
    return d


def d5_dama():
    d = Design("5_dama", "Dama bayrağı", "Solda yarış bayrağı damaları; İNCE ve OTO LASTİK yarış yazısıyla.",
               scheme(False))
    s, n = 4.6, 16
    squares = [A.rect(X0 + i * s, 10.4 + j * s, X0 + (i + 1) * s, 10.4 + (j + 1) * s).offset(-0.12, J)
               for i in range(2) for j in range(n) if (i + j) % 2 == 0]
    d.add(None, A.union(*squares), BLACK)
    x0 = X0 + 2 * s + 4.8
    d.add("İNCE", t("saira", "İNCE", 19.0, x0, 70.0, "l", 0.6), BLACK)
    d.add("OTO LASTİK", t("saira", "OTO LASTİK", 8.0, x0, 52.5, "l", 0.8, 10.0 - x0), RED)
    d.add("7/24 HİZMET", t("outfit", "7/24 HİZMET", 4.4, x0, 34.0, "l", 0.9), RED)
    d.add("telefon", t("outfit", PHONE, 5.0, x0, 21.0, "l", 0.3, 9.0 - x0), BLACK)
    d.inlay += qr_block(34.0, 42.0, 40.0, d.sc)
    return d


def d6_hiz():
    d = Design("6_hiz", "Hız çizgileri", "Eğik İNCE ve solunda kırmızı hız çizgileri; dinamik, sportif.", scheme(False))
    x0 = -37.0
    d.add(None, A.union(bar(X0, -42.0, 72.0, 2.4), bar(X0 + 4.0, -43.0, 65.0, 2.4), bar(X0, -44.0, 58.0, 2.4)), RED)
    d.add("İNCE", t("teko", "İNCE", 26.0, x0, 64.0, "l", 0.8, 41.0, shear=12.0), BLACK)
    d.add("OTO LASTİK", t("outfit", "OTO LASTİK", 6.8, x0 + 1.0, 45.0, "l", 0.8, 44.0, shear=10.0), RED)
    d.add("7/24 HİZMET", t("outfit", "7/24 HİZMET", 4.6, X0, 30.0, "l", 0.9), BLACK)
    d.add("telefon", t("outfit", PHONE, 5.2, X0, 17.5, "l", 0.4), BLACK)
    d.inlay += qr_block(33.0, 45.0, 42.0, d.sc)
    return d


def d7_jant():
    d = Design("7_jant", "Jant", "Sade, kalın jant simgesi; yanında İNCE OTO LASTİK.", scheme(False))
    cx, cy = -40.0, 66.0
    d.add(None, A.circle(13.5, cx, cy) - A.circle(8.9, cx, cy), BLACK)          # lastik
    holes = A.union(A.circle(1.5, cx, cy), *[A.circle(1.25, cx + 4.3 * np.cos(a), cy + 4.3 * np.sin(a))
                                             for a in np.radians(np.arange(5) * 72 + 90)])
    d.add(None, A.circle(7.6, cx, cy) - holes, RED)                                # jant: 5 bijon deliği
    d.add("İNCE", t("oswald", "İNCE", 16.0, -21.5, 71.5, "l", 0.6), BLACK)
    d.add("OTO LASTİK", t("oswald", "OTO LASTİK", 7.4, -21.5, 56.5, "l", 0.8), RED)
    d.add("7/24 HİZMET", t("outfit", "7/24 HİZMET", 4.8, X0, 38.0, "l", 0.9), RED)
    d.add("telefon", t("outfit", PHONE, 5.2, X0, 25.0, "l", 0.4, 66.0), BLACK)
    d.add("TARA", t("oswald", "TARA", 7.4, X0, 13.6, "l", 1.4), BLACK)
    d.inlay += qr_block(35.0, 29.0, 38.0, d.sc)
    return d


# ---------------------------------------------------------------- siyah zemin (beyaz, kırmızı yazı)

def d8_kose():
    d = Design("8_kose", "Kırmızı köşe", "Siyah zemin, sol üst köşede kırmızı üçgen ve 7/24; QR beyaz karoda.",
               scheme(True))
    tri = A.polygon([(-70, 100), (-70, 42), (-12, 100)]) ^ I.outline()
    d.add("7/24 köşe", tri - t("archivo", "7/24", 6.0, -48.5, 80.5, "c", 0.4), RED)
    d.add("İNCE", t("archivo", "İNCE", 13.0, X0, 43.5, "l", 0.5), WHITE)
    d.add("OTO LASTİK", t("archivo", "OTO LASTİK", 5.6, X0, 29.5, "l", 0.6, 60.0), RED)
    d.add("telefon", t("outfit", PHONE, 5.0, X0, 16.0, "l", 0.4, 60.0), WHITE)
    d.inlay += qr_block(33.0, 45.0, 42.0, d.sc)
    return d


def d9_cerceve():
    d = Design("9_cerceve", "Kırmızı çerçeve", "Siyah zemin, ince kırmızı çerçeve; ortalı, sade yazılar.", scheme(True))
    d.add(None, A.rrect(112.0, 78.0, 5.0, 0, 48.5) - A.rrect(109.2, 75.2, 3.6, 0, 48.5), RED)
    cx = -24.0
    d.add("İNCE", t("bebas", "İNCE", 27.0, cx, 63.0, "c", 1.2), WHITE)
    d.add("OTO LASTİK", t("outfit", "OTO LASTİK", 4.8, cx, 42.5, "c", 1.6), RED)
    d.add("7/24 HİZMET", t("outfit", "7/24 HİZMET", 4.6, cx, 32.0, "c", 1.0), WHITE)
    d.add("telefon", t("outfit", PHONE, 4.8, cx, 21.0, "c", 0.3, 54.0), WHITE)
    d.inlay += qr_block(28.0, 48.0, 42.0, d.sc)
    return d


def d10_oklar():
    d = Design("10_oklar", "Oklar", "Siyah zemin, QR'ı gösteren kalın kırmızı oklar; İNCE ve OTO LASTİK.",
               scheme(True))
    d.add("İNCE", t("russo", "İNCE", 15.0, X0, 72.0, "l", 0.6), WHITE)
    d.add("OTO LASTİK", t("russo", "OTO LASTİK", 6.0, X0, 56.0, "l", 0.6, 60.0), RED)
    d.add("7/24 HİZMET", t("outfit", "7/24 HİZMET", 4.6, X0, 45.5, "l", 0.9), WHITE)
    d.add(None, U.chevrons(X0, 32.0, 9.0, 3, 10.0, 3.0), RED)
    d.add("telefon", t("outfit", PHONE, 5.0, X0, 17.0, "l", 0.4, 60.0), WHITE)
    d.inlay += qr_block(32.0, 44.0, 44.0, d.sc)
    return d


DESIGNS = [d1_plaka, d2_minimal, d3_kirmizi_blok, d4_yol, d5_dama, d6_hiz, d7_jant, d8_kose, d9_cerceve, d10_oklar]


# ---------------------------------------------------------------- katılar, kontrol, çizim

def solids(d):
    """Panel baskı yönünde (yüzü yukarı): gövde, yüzeyle aynı hizada dolgular, kabartmalar. Sonra eklenen kabartma
    öncekinin üstüne yazar."""
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
    d.shown = B.assembled(d.parts, z0, y0) + [("Sehpa", d.stand, BLACK)]
    return d


def qr_check(d):
    im = B.top_view(d.parts).convert("L")
    ppm = im.width * (1 - 2 * 0.03) / I.PW
    sim = Q.simulate(im, ppm, 1.2, **dict(Q.SIM_CASES)["hepsi birden"])
    return QR.content in Q.decode(im), QR.content in Q.decode(sim)


def mesh(parts):
    return [(*A.mesh_arrays(m), SHOW[c]) for _, m, c in parts]


def font_ui(n):
    return ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), n)


def sheet(d, i):
    W, H = 1500, 700
    canvas = Image.new("RGB", (W, H), (236, 239, 244))
    dr = ImageDraw.Draw(canvas)
    views = [(rotation(0, -90), "Önden, sehpada (120 × 90 mm)", 0.85), (rotation(-28, -68), "Tezgâhta (3/4)", None),
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


def wrap(dr, s, font, width):
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if dr.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + [cur] if cur else lines


def catalog(ds):
    """Müşteriye: musteri_1.png (1–6), musteri_2.png (7–10), musteri_katalog.pdf."""
    W, H = 1654, 2339
    big = ImageFont.truetype(os.path.join(A.FONT_DIR, "BarlowCondensed-Black.ttf"), 118)
    mid = ImageFont.truetype(os.path.join(A.FONT_DIR, "BarlowCondensed-ExtraBold.ttf"), 44)
    f = font_ui
    ink, muted, paper, red = (20, 20, 22), (96, 98, 106), (245, 245, 243), SHOW[RED]
    pages = []
    for p, group in enumerate([ds[:6], ds[6:]]):
        im = Image.new("RGB", (W, H), paper)
        dr = ImageDraw.Draw(im)
        dr.rectangle((0, 0, W, 250), fill=(250, 250, 248))
        dr.rectangle((0, 246, W, 254), fill=red)
        dr.text((70, 40), "İNCE", font=big, fill=ink)
        x = 76 + dr.textlength("İNCE", font=big) + 18
        dr.text((x, 70), "OTO LASTİK", font=mid, fill=red)
        dr.text((x, 128), "7/24 HİZMET", font=f(26), fill=muted)
        dr.text((70, 186), "Tek QR'lı tezgâh isimliği · tasarım önerileri", font=f(30), fill=muted)
        dr.text((W - 70 - dr.textlength(f"{p + 1}/2", font=f(28)), 196), f"{p + 1}/2", font=f(28), fill=muted)
        y = 285
        for line in ("TARA: telefonla okutunca işletme sayfası açılır (site hazırlanınca). Örneklerde şimdilik arar.",
                     "1–7 beyaz zemin (siyah, kırmızı yazı) · 8–10 siyah zemin (beyaz, kırmızı yazı)"):
            dr.text((70, y), line, font=f(27), fill=ink)
            y += 40
        top, gap, cw = 395, 50, (W - 3 * 60) // 2
        ch = (H - top - 190 - 2 * gap) // 3
        for k, d in enumerate(group):
            x0, y0 = 60 + (k % 2) * (cw + 60), top + (k // 2) * (ch + gap)
            dr.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 28, fill=(255, 255, 255), outline=(226, 226, 230))
            n = ds.index(d) + 1
            dr.ellipse((x0 + 26, y0 + 24, x0 + 86, y0 + 84), fill=red)
            dr.text((x0 + 56 - dr.textlength(str(n), font=f(34)) / 2, y0 + 34), str(n), font=f(34),
                    fill=(255, 255, 255))
            dr.text((x0 + 104, y0 + 30), d.title, font=f(38), fill=ink)
            img = A.fit_into(render(mesh(d.shown), 1300, rotation(0, -90), flat=0.85, margin=0.02), cw - 70, ch - 190)
            im.paste(img, (x0 + (cw - img.width) // 2, y0 + 100 + (ch - 190 - img.height) // 2), img)
            ty = y0 + ch - 78
            for line in wrap(dr, d.desc, f(26), cw - 60)[:2]:
                dr.text((x0 + 30, ty), line, font=f(26), fill=muted)
                ty += 34
        if p == 1:                                          # boş kalan yere: ürün bilgisi
            y0, y1 = top + 2 * (ch + gap), H - 190
            dr.rounded_rectangle((60, y0, W - 60, y1), 28, fill=(255, 255, 255), outline=(226, 226, 230))
            dr.text((100, y0 + 40), "Ürün", font=f(38), fill=ink)
            ty = y0 + 110
            for line in ("Ölçü 12 × 9 cm, gövde 1 cm kalınlığında, köşeler yuvarlak",
                         "Yazılar ve şekiller 2 mm kabartma; QR düz ve keskin",
                         "Tezgâh sehpası dahil, panel 15° eğik durur",
                         f"Telefon: {PHONE}"):
                dr.ellipse((100, ty + 10, 114, ty + 24), fill=red)
                dr.text((130, ty), line, font=f(30), fill=muted)
                ty += 56
            pick = ds[0]
            img = A.fit_into(render(mesh(pick.shown), 1200, rotation(-28, -68), margin=0.02), 520, y1 - y0 - 60)
            im.paste(img, (W - 100 - img.width, y0 + (y1 - y0 - img.height) // 2), img)
        foot = ("Beğendiğiniz tasarımın numarasını yazmanız yeterli." if p == 1 else
                "Ölçü 12 × 9 cm · 1 cm kalın · kabartma yazı · tezgâh sehpası dahil")
        dr.rounded_rectangle((60, H - 150, W - 60, H - 70), 22, fill=(16, 16, 18))
        dr.text((W / 2 - dr.textlength(foot, font=f(30)) / 2, H - 128), foot, font=f(30), fill=(244, 244, 242))
        im.save(os.path.join(OUT_DIR, f"musteri_{p + 1}.png"), optimize=True)
        pages.append(im)
    pages[0].save(os.path.join(OUT_DIR, "musteri_katalog.pdf"), save_all=True, append_images=pages[1:],
                  resolution=200)


def main():
    only = sys.argv[1:]
    if only == ["katalog"]:                              # yalnız müşteri kataloğu
        catalog([build(fn) for fn in DESIGNS])
        return
    ds = []
    for i, fn in enumerate(DESIGNS, 1):
        d = build(fn)
        if only and not any(o in d.key for o in only):
            continue
        d.metrics = {k: B.line_metrics(cs) for k, cs in d.lines.items()}
        d.qr = qr_check(d)
        sheet(d, i)
        ds.append(d)
        bad = {k: v for k, v in d.metrics.items() if v[0] < 0.6 or v[2] > 6.0}
        print(f"{d.key:22s} QR {d.qr}  dar/ince satırlar: {bad or 'yok'}")
    if not only:
        catalog(ds)


if __name__ == "__main__":
    main()
