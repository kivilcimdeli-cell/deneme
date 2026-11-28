"""OTO SENTEZ – Çıkma ve yeni yedek parça (Kepez, Antalya): QR'lı masa isimliği önerileri (10).

Renkler (kullanıcı): logo gri, yazı beyaz, gövde siyah (1–7); 8–10 aynı düzenlerin beyaz gövdeli hali (yazı siyah,
logo yine gri). OTO SENTEZ yazısı logodaki gibi lacivert (kullanıcı: "çok renksiz olmuş, laciverte çevir").

Logo müşterinin görselinden (scripts/otosentez_logo.py): gri küre (üç kavisli şerit) ve "OTO SENTEZ" yazısı vektöre
çevrildi; alt satır "ÇIKMA - YENİ YEDEK PARÇA" Oswald Bold ile (görselde vektöre çevrilemeyecek kadar küçük), logodaki
gibi adın genişliğine yayılır. Şekiller işe göre ve sade: dişli, İngiliz anahtarı, çerçeve, alt bant.

Auto Tufan ve lastikçi isimlikleriyle aynı yapı: 120 × 90 mm (4:3), köşeler R8, gövde 1 cm, yazılar ve logo 2 mm
kabartma, QR yüzeyle aynı hizada (siyah gövdede beyaz karo, beyaz gövdede siyah kareler), 15° eğik sehpa. Her satırın
en dar harf içi boşluğu ölçülür (≥ 0,6 mm), öğeler arası ≥ 2 mm; QR görüntüden ve baskı hatası benzetiminden okunur.

QR: `otosentez_isimlik/bilgiler.json` → `sayfa_url`; şimdilik deneme sitesi (deneme123, kullanıcı istedi). OTO SENTEZ'in
kendi sayfası tasarım seçilince şablonla yapılır.
Telefon numarası henüz yok: isimliklerde web adresi, Instagram ve konum yazar.

Çıktı : otosentez_isimlik/<tasarım>.png, musteri_1.png (1–6), musteri_2.png (7–10), musteri_katalog.pdf
Kullanım:
  python3 scripts/otosentez_logo.py <logo_görseli>     # bir kez: küre ve yazı
  python3 scripts/otosentez_isimlik.py [anahtar ...]   # ya da: katalog
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
import otosentez_logo as L  # noqa: E402
import qr_sistemi as Q  # noqa: E402
import uzar_isimlik as I  # noqa: E402
import uzar_isimlik_baski as B  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "otosentez_isimlik")
DATA = json.load(open(os.path.join(OUT_DIR, "bilgiler.json"), encoding="utf-8"))
BLACK, WHITE, NAVY = A.BLACK, A.WHITE, A.BLUE    # lacivert: Bambu PLA Basic Blue (#0A2989)
GRAY = 8                                                   # Bambu PLA Basic Gray
A.COLOURS.setdefault(GRAY, "#8E9089")
A.COLOUR_NAMES.setdefault(GRAY, "gri")
A.SHOW.setdefault(GRAY, (150, 152, 148))
SHOW = {BLACK: (40, 40, 43), WHITE: (246, 246, 242), GRAY: (150, 152, 148), NAVY: (30, 58, 168)}
NAMES = {BLACK: "siyah", WHITE: "beyaz", GRAY: "gri", NAVY: "lacivert"}
J = m3.JoinType.Round
X0, X1 = -54.0, 54.0
SUB, CITY, WEB, INSTA = DATA["alt"], "KEPEZ / ANTALYA", DATA["web"].replace("www.", ""), DATA["instagram"]
N.FONT_FILES.update({"pop7": "Poppins-Bold.ttf"})
t, Design = N.t, N.Design
SIYAH = {"body": BLACK, "fg": WHITE, "dark": True, "ad": "siyah"}
BEYAZ = {"body": WHITE, "fg": BLACK, "dark": False, "ad": "beyaz"}


def make_qr():
    import segno
    content = Q.https_url(DATA["sayfa_url"]).rstrip("/")
    q = segno.make(content, error="m", micro=False, boost_error=True)
    return Q.Entry("sayfa", "TARA", content, "TARA", qr=q)


QR = make_qr()


# ---------------------------------------------------------------- logo

def kure(h, cx, cy):
    """Gri küre, yükseklik h mm, merkez (cx, cy). Şeritlerin sivri uçları basılabilsin diye 0,25 mm dışa alınır."""
    cs = m3.CrossSection(L.polygons("kure"), m3.FillRule.EvenOdd).scale((h, h)).offset(0.25, J)
    b = cs.bounds()
    return cs.translate((cx - (b[0] + b[2]) / 2, cy - (b[1] + b[3]) / 2))


def ad(h, x, y, align="l"):
    """OTO SENTEZ (logodaki çizim), harf yüksekliği h mm, (x, y) dikey orta. Logoda harf araları dar (~0,05 h): harfler
    ~0,7 mm açılır; çizilen kenarın JPEG pürüzü yumuşatılıp 0,1 mm kalınlaştırılır (ince serif uçları basılsın)."""
    cs = m3.CrossSection(L.polygons("yazi"), m3.FillRule.EvenOdd).scale((h, h))
    tr = max(0.3, 1.0 - 0.06 * h)
    parts = sorted(cs.decompose(), key=lambda p: p.bounds()[0])
    cs = A.union(*[p.translate((k * tr, 0)) for k, p in enumerate(parts)]).offset(-0.15, J).offset(0.25, J)
    b = cs.bounds()
    dx = {"l": x - b[0], "c": x - (b[0] + b[2]) / 2, "r": x - b[2]}[align]
    return cs.translate((dx, y - (b[1] + b[3]) / 2))


def ad_w(w, x, y, align="l"):
    """OTO SENTEZ, genişliği w mm."""
    h = w / 7.9
    for _ in range(4):
        b = ad(h, 0, 0).bounds()
        h *= w / (b[2] - b[0])
    return ad(h, x, y, align)


def satir(parcalar, cap, x, y, align="l", width=None, tr=0.8):
    """Poppins Bold satır; parçalar arasına "-" yerine kalın çizgi (yazı tipinin tiresi 2 mm kabartmada ince kalır).
    width verilirse harf aralığı o genişliğe yayılır."""
    def kur(tr):
        out, xx = [], 0.0
        for k, s in enumerate(parcalar):
            if k:
                out.append(A.rrect(cap * 0.55, 1.1, 0.5, xx + tr + 1.0 + cap * 0.275, 0.0))
                xx += 2 * (tr + 1.0) + cap * 0.55
            cs = t("pop7", s, cap, xx, 0.0, "l", tr)
            out.append(cs)
            xx = cs.bounds()[2]
        return A.union(*out)
    cs = kur(tr)
    if width:
        n = sum(len(s) for s in parcalar) + 2 * (len(parcalar) - 1) - 1
        for _ in range(3):
            b = cs.bounds()
            tr = max(0.0, tr + (width - (b[2] - b[0])) / n)
            cs = kur(tr)
    b = cs.bounds()
    dx = {"l": x - b[0], "c": x - (b[0] + b[2]) / 2, "r": x - b[2]}[align]
    return cs.translate((dx, y))


def alt_tek(cap, x, y, align="l", width=None):
    """ÇIKMA - YENİ YEDEK PARÇA tek satır (Poppins Bold 4,4: ~86 mm; tam genişlikte)."""
    return satir(["ÇIKMA", "YENİ YEDEK PARÇA"], cap, x, y, align, width, 0.6)


def alt_iki(d, x, y, align="l", width=None, col=None):
    """ÇIKMA - YENİ / YEDEK PARÇA iki satır (ilk satırın ortası y). Döner: alt kenar."""
    col = col or d.sc["fg"]
    a1 = satir(["ÇIKMA", "YENİ"], 4.4, x, y, align, width, 0.8)
    a2 = satir(["YEDEK PARÇA"], 4.4, x, y - 8.3, align, width, 0.8)
    d.add("ÇIKMA - YENİ", a1, col)
    d.add("YEDEK PARÇA", a2, col)
    return a2.bounds()[1]


def yazi(s, cap, x, y, align="l", tr=0.8, max_w=None):
    return t("pop7", s, cap, x, y, align, tr, max_w)


# ---------------------------------------------------------------- ortak öğeler

def qr_block(d, cx, cy, s):
    """QR yüzeyle aynı hizada: siyah gövdede beyaz karo (kareler gövdenin siyahı), beyaz gövdede siyah kareler."""
    _, dark, _ = Q.shapes(QR, Q.module_for(QR, s), cx, cy)
    tile = A.rrect(s, s, 1.6, cx, cy)
    if d.sc["body"] == BLACK:
        d.inlay.append((tile - dark, WHITE))
    else:
        d.inlay.append((dark ^ tile, BLACK))


def bar(x0, x1, y, h=1.4):
    return A.rrect(x1 - x0, h, h / 2 - 0.01, (x0 + x1) / 2, y)


def diamond(cx, cy, r):
    return A.polygon([(cx, cy + r), (cx + r, cy), (cx, cy - r), (cx - r, cy)])


def disli(R, cx, cy, teeth=10, ring=2.4):
    """Dişli halkası (dış yarıçap R): kalın, yuvarlak köşeli dişler."""
    body = A.circle(R - 2.6, 0, 0, 96)
    tooth = A.rrect(4.6, 3.4, 0.9, 0, R - 1.7)
    cs = A.union(body, *[tooth.rotate(360.0 * k / teeth) for k in range(teeth)])
    cs = cs.offset(-0.6, J).offset(0.6, J)
    return (cs - A.circle(R - 2.6 - ring, 0, 0, 96)).translate((cx, cy))


def ingiliz(cx, cy, L_, angle=0.0):
    return C.wrench(cx, cy, L_, angle)


WEB_UP = WEB.upper()


def bilgi(d, x, ys, align="l", col=None, tr_web=0.25):
    """Konum ve web satırları (verilen y'lerde; None atlanır)."""
    col = col or d.sc["fg"]
    for (s, tr), y in zip([(CITY, 0.5), (WEB_UP, tr_web)], ys):
        if y is not None:
            d.add(s, yazi(s, 4.4, x, y, align, tr, 66.0), col)


def tara(d, cx, y):
    d.add("TARA", yazi("TARA", 4.4, cx, y, "c", 1.6), d.sc["fg"])


# ---------------------------------------------------------------- tasarımlar

def d1_klasik(sc=SIYAH, key="1_klasik_logo", no=""):
    d = Design(key, "Klasik logo" + no, "Logonun aynısı solda: gri küre, OTO SENTEZ ve ÇIKMA - YENİ YEDEK PARÇA; "
               "sağda QR, altta konum ve web.", sc)
    cx = -17.5
    d.add(None, kure(18.0, cx, 77.5), GRAY)
    nm = ad_w(64.0, cx, 60.5, "c")
    d.add("OTO SENTEZ", nm, NAVY)
    yb = alt_iki(d, cx, nm.bounds()[1] - 5.8, "c")
    d.add(None, bar(cx - 12.0, cx + 12.0, yb - 4.0), GRAY)
    bilgi(d, cx, [yb - 10.5, yb - 19.5], "c")
    s = 31.0
    qr_block(d, X1 - s / 2, 50.0, s)
    tara(d, X1 - s / 2, 50.0 - s / 2 - 5.0)
    return d


def d2_yan(sc=SIYAH, key="2_yan_logo", no=""):
    d = Design(key, "Yan logo" + no, "Üstte geniş logo: küre, iri OTO SENTEZ ve tam boy alt satır; altta konum, web "
               "ve QR.", sc)
    d.add(None, kure(18.0, X0 + 9.0, 77.0), GRAY)
    d.add("OTO SENTEZ", ad_w(X1 - (X0 + 21.0), X0 + 21.0, 77.0), NAVY)
    d.add("ÇIKMA - YENİ YEDEK PARÇA", alt_tek(4.4, 0.0, 62.0, "c", X1 - X0), sc["fg"])
    bilgi(d, X0, [40.0, 30.5])
    s = 31.0
    qr_block(d, X1 - s / 2, 13.5 + s / 2, s)
    return d


def d3_ortali(sc=SIYAH, key="3_ortali", no=""):
    d = Design(key, "Ortalı" + no, "Logo ortada: küre, OTO SENTEZ ve tam boy alt satır; altta ortada QR, yanlarında "
               "TARA ve web.", sc)
    d.add(None, kure(15.0, 0.0, 78.5), GRAY)
    nm = ad_w(70.0, 0.0, 63.0, "c")
    d.add("OTO SENTEZ", nm, NAVY)
    d.add("ÇIKMA - YENİ YEDEK PARÇA", alt_tek(4.4, 0.0, nm.bounds()[1] - 6.0, "c", X1 - X0), sc["fg"])
    s = 31.0
    cy = 13.0 + s / 2
    qr_block(d, 0, cy, s)
    tara(d, -38.0, cy)
    d.add(None, N.arrow(-24.6, cy, 6.0).offset(-0.4, J).offset(0.4, J), GRAY)
    d.add("OTOSENTEZ", yazi("OTOSENTEZ", 4.4, 36.5, cy + 3.8, "c", 0.15), sc["fg"])
    d.add(".COM.TR", yazi(".COM.TR", 4.4, 36.5, cy - 3.8, "c", 0.6), GRAY)
    return d


def d4_disli(sc=SIYAH, key="4_disli", no=""):
    d = Design(key, "Dişli" + no, "Solda beyaz dişli içinde gri küre; yanında OTO SENTEZ ve ÇIKMA - YENİ YEDEK PARÇA; "
               "altta konum, web ve QR.", sc)
    cx, cy = X0 + 15.5, 70.0
    d.add(None, disli(15.5, cx, cy), sc["fg"])
    d.add(None, kure(14.0, cx, cy), GRAY)
    x = X0 + 35.0
    nm = ad_w(X1 - x, x, 78.0)
    d.add("OTO SENTEZ", nm, NAVY)
    alt_iki(d, x, nm.bounds()[1] - 5.8)
    bilgi(d, X0, [43.0, 33.5])
    s = 31.0
    qr_block(d, X1 - s / 2, 13.5 + s / 2, s)
    return d


def d5_anahtar(sc=SIYAH, key="5_ingiliz_anahtari", no=""):
    d = Design(key, "İngiliz anahtarı" + no, "Üstte iri OTO SENTEZ ve yanında küre; altında tam boy alt satır ve gri "
               "İngiliz anahtarı; altta konum, web ve QR.", sc)
    d.add(None, kure(16.0, X1 - 8.0, 78.0), GRAY)
    nm = ad_w(84.0, X0, 78.0)
    d.add("OTO SENTEZ", nm, NAVY)
    d.add("ÇIKMA - YENİ YEDEK PARÇA", alt_tek(4.4, 0.0, 63.5, "c", X1 - X0), sc["fg"])
    d.add(None, ingiliz(X0 + 25.0, 50.5, 50.0, 0.0), GRAY)
    bilgi(d, X0, [34.5, 25.0])
    s = 31.0
    qr_block(d, X1 - s / 2, 13.5 + s / 2, s)
    return d


def d6_cerceve(sc=SIYAH, key="6_cerceve", no=""):
    d = Design(key, "Çerçeve" + no, "İnce gri çerçeve, üst kenarında araya giren küre; içinde ortalı yazılar, sağda QR.",
               sc)
    frame = A.rrect(108.0, 68.0, 5.0, 0, 46.0)                 # y 12..80
    ring = frame - frame.offset(-1.3, J)
    cx = -20.0
    k = kure(11.0, cx, 80.0)
    d.add(None, ring - k.offset(2.4, J), GRAY)
    d.add(None, k, GRAY)
    nm = ad_w(56.0, cx, 66.0, "c")
    d.add("OTO SENTEZ", nm, NAVY)
    yb = alt_iki(d, cx, nm.bounds()[1] - 5.8, "c")
    bilgi(d, cx + 1.5, [yb - 8.6, yb - 17.0], "c", tr_web=0.0)
    s = 31.0
    qr_block(d, 33.0, 52.0, s)
    tara(d, 33.0, 52.0 - s / 2 - 5.0)
    return d


def d7_alt_bant(sc=SIYAH, key="7_alt_bant", no=""):
    d = Design(key, "Alt bant" + no, "Üstte logo; altta gri bant içinde oyma ÇIKMA - YENİ YEDEK PARÇA; ortada konum, web "
               "ve QR.", sc)
    d.add(None, kure(17.0, X0 + 8.5, 77.5), GRAY)
    d.add("OTO SENTEZ", ad_w(80.0, X0 + 20.0, 77.5), NAVY)
    band = A.rrect(X1 - X0, 12.5, 3.0, 0, 18.5)
    d.add("bant", band - alt_tek(4.6, 0.0, 18.5, "c", X1 - X0 - 10.0), GRAY)
    bilgi(d, X0, [58.5, 49.0])
    s = 31.0
    qr_block(d, X1 - s / 2, 30.0 + s / 2, s)
    tara(d, -1.5, 36.0)
    d.add(None, N.arrow(13.4, 36.0, 5.6).offset(-0.4, J).offset(0.4, J), GRAY)
    return d


DESIGNS = [d1_klasik, d2_yan, d3_ortali, d4_disli, d5_anahtar, d6_cerceve, d7_alt_bant,
           lambda: d1_klasik(BEYAZ, "8_klasik_logo_beyaz", " (beyaz)"),
           lambda: d3_ortali(BEYAZ, "9_ortali_beyaz", " (beyaz)"),
           lambda: d2_yan(BEYAZ, "10_yan_logo_beyaz", " (beyaz)")]
ADLAR = ["klasik", "yan", "ortali", "disli", "anahtar", "cerceve", "bant", "klasik_beyaz", "ortali_beyaz", "yan_beyaz"]


# ---------------------------------------------------------------- katılar, kontrol, çizim

def solids(d):
    out = I.outline()
    govde = d.sc["body"]
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
    return [(f"Panel ({NAMES[govde]})", body, govde)] + parts


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


def font_ui(n, w="SemiBold"):
    return ImageFont.truetype(os.path.join(A.FONT_DIR, f"Poppins-{w}.ttf"), n)


def raster(kind, h, colour):
    """Logo parçası (küre ya da yazı), h piksel yüksekliğinde RGBA."""
    ss = 4
    rings = L.polygons(kind)
    w = int(np.ceil(max(x for r in rings for x, _ in r) * h)) + 2
    m = np.zeros((h * ss, w * ss), bool)
    for r in rings:
        im = Image.new("1", (w * ss, h * ss), 0)
        ImageDraw.Draw(im).polygon([(x * h * ss, (1 - y) * h * ss) for x, y in r], fill=1)
        m ^= np.asarray(im)
    a = Image.fromarray((m * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), colour + (0,))
    out.putalpha(a)
    return out


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
    dr.text((30, 14), f"{i}. {d.title.upper()}", fill=(24, 26, 30), font=font_ui(32))
    dr.text((30, 62), d.desc, fill=(80, 86, 98), font=font_ui(18, "Regular"))
    worst = min((v[0] for v in d.metrics.values()), default=9)
    dr.text((30, 94), f"{NAMES[d.sc['body']].capitalize()} gövde 1 cm, kabartma 2 mm · en dar harf içi boşluk "
                      f"{worst:.2f} mm · QR {'okundu' if d.qr[0] else 'OKUNMADI'}{', benzetimde de' if d.qr[1] else ''}",
            fill=(22, 120, 60) if d.qr[0] and worst >= 0.6 else (200, 30, 38), font=font_ui(18))
    canvas.save(os.path.join(OUT_DIR, d.key + ".png"))


def header(im, dr, W, page):
    """Beyaz başlık: logo (gri küre, lacivert OTO SENTEZ, alt satır) logodaki gibi; altında gri çizgi."""
    dr.rectangle((0, 0, W, 250), fill=(255, 255, 255))
    k = raster("kure", 170, (150, 152, 148))
    im.paste(k, (70, 40), k)
    y = raster("yazi", 92, (30, 52, 170))
    x = 70 + k.width + 40
    im.paste(y, (x, 62), y)
    f = font_ui(30, "Medium")
    xx = x + 6
    for ch in SUB:
        dr.text((xx, 172), ch, font=f, fill=(60, 62, 70))
        xx += dr.textlength(ch, font=f) + (y.width - 12 - sum(dr.textlength(c, font=f) for c in SUB)) / (len(SUB) - 1)
    lab = "QR'lı masa isimliği"
    dr.text((W - 70 - dr.textlength(lab, font=font_ui(30)), 70), lab, font=font_ui(30), fill=(110, 112, 108))
    sub = f"tasarım önerileri · {page}/2"
    dr.text((W - 70 - dr.textlength(sub, font=font_ui(26, "Regular")), 120), sub, font=font_ui(26, "Regular"),
            fill=(120, 122, 128))
    dr.rectangle((0, 246, W, 254), fill=(150, 152, 148))


def catalog(ds):
    W, H = 1654, 2339
    f = font_ui
    ink, muted, paper, gray = (20, 20, 22), (96, 98, 106), (245, 244, 240), (150, 152, 148)
    pages = []
    for p, group in enumerate([ds[:6], ds[6:]]):
        im = Image.new("RGB", (W, H), paper)
        dr = ImageDraw.Draw(im)
        header(im, dr, W, p + 1)
        y = 285
        for line in ("QR: telefonla okutunca işletmenin sayfası açılır (arama, WhatsApp, konum, yorum).",
                     "Logodaki gibi gri küre ve lacivert OTO SENTEZ · 1–7 siyah zemin, beyaz yazı · 8–10 beyaz zemin, siyah yazı."):
            dr.text((70, y), line, font=f(27, "Regular"), fill=ink)
            y += 42
        top, gap, cw = 395, 50, (W - 3 * 60) // 2
        ch = (H - top - 190 - 2 * gap) // 3
        for k, d in enumerate(group):
            x0, y0 = 60 + (k % 2) * (cw + 60), top + (k // 2) * (ch + gap)
            dr.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 28, fill=(255, 255, 255), outline=(226, 224, 218))
            n = ds.index(d) + 1
            dr.ellipse((x0 + 26, y0 + 24, x0 + 86, y0 + 84), fill=(22, 22, 24))
            dr.text((x0 + 56 - dr.textlength(str(n), font=f(32)) / 2, y0 + 30), str(n), font=f(32), fill=(246, 246, 242))
            dr.text((x0 + 104, y0 + 28), d.title, font=f(36), fill=ink)
            img = A.fit_into(render(mesh(d.shown), 1300, rotation(0, -90), flat=0.85, margin=0.02), cw - 70, ch - 190)
            im.paste(img, (x0 + (cw - img.width) // 2, y0 + 100 + (ch - 190 - img.height) // 2), img)
            ty = y0 + ch - 78
            for line in N.wrap(dr, d.desc, f(24, "Regular"), cw - 60)[:2]:
                dr.text((x0 + 30, ty), line, font=f(24, "Regular"), fill=muted)
                ty += 34
        if p == 1:
            y0, y1 = top + 2 * (ch + gap), H - 190
            dr.rounded_rectangle((60, y0, W - 60, y1), 28, fill=(255, 255, 255), outline=(226, 224, 218))
            dr.text((100, y0 + 40), "Ürün", font=f(36), fill=ink)
            ty = y0 + 110
            for line in ("Ölçü 12 × 9 cm, gövde 1 cm kalınlığında, köşeler yuvarlak",
                         "Logo ve yazılar 2 mm kabartma; QR düz ve keskin",
                         "Masa sehpası dahil, panel 15° eğik durur",
                         "QR işletme sayfasını açar"):
                dr.ellipse((100, ty + 12, 114, ty + 26), fill=gray)
                dr.text((130, ty), line, font=f(28, "Regular"), fill=muted)
                ty += 56
            img = A.fit_into(render(mesh(ds[0].shown), 1200, rotation(-28, -68), margin=0.02), 520, y1 - y0 - 60)
            im.paste(img, (W - 100 - img.width, y0 + (y1 - y0 - img.height) // 2), img)
        foot = ("Beğendiğiniz tasarımın numarasını yazmanız yeterli." if p == 1 else
                "Ölçü 12 × 9 cm · 1 cm kalın · kabartma logo ve yazı · masa sehpası dahil")
        dr.rounded_rectangle((60, H - 150, W - 60, H - 70), 22, fill=(22, 22, 24))
        dr.text((W / 2 - dr.textlength(foot, font=f(28)) / 2, H - 128), foot, font=f(28), fill=(246, 246, 242))
        im.save(os.path.join(OUT_DIR, f"musteri_{p + 1}.png"), optimize=True)
        im.convert("RGB").save(os.path.join(OUT_DIR, f"musteri_{p + 1}.jpg"), "JPEG", quality=90, optimize=True)
        pages.append(im)
    pages[0].save(os.path.join(OUT_DIR, "musteri_katalog.pdf"), save_all=True, append_images=pages[1:],
                  resolution=200)


def check(i):
    d = build(DESIGNS[i - 1])
    d.metrics = {k: B.line_metrics(cs) for k, cs in d.lines.items()}
    d.qr = qr_check(d)
    sheet(d, i)
    bad = {k: tuple(round(x, 2) for x in v) for k, v in d.metrics.items() if v[0] < 0.6 or v[2] > 6.0}
    return (f"{d.key:22s} QR {d.qr}  simgelerde 1,2 mm'den ince %{C.thin_shapes(d)}  dar/ince satırlar: "
            f"{bad or 'yok'}  sıkışık: {C.crowded(d) or 'yok'}")


def main():
    from multiprocessing import Pool
    only = sys.argv[1:]
    if only == ["katalog"]:
        catalog([build(fn) for fn in DESIGNS])
        return
    todo = [i for i, a in enumerate(ADLAR, 1) if not only or any(o in a for o in only)]
    with Pool(4) as pool:
        for line in pool.map(check, todo):
            print(line)
    if not only:
        catalog([build(fn) for fn in DESIGNS])


if __name__ == "__main__":
    main()
