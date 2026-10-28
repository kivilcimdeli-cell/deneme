"""AUTO TUFAN – Kaporta & Boya (hasar onarım, Antalya): QR'lı masa isimliği önerileri (10). Siyah zemin, altın ve
beyaz kabartma yazı ve şekiller.

Logo müşterinin görselinden: fırça T (scripts/autotufan_logo.py ile vektöre çevrildi, altın), "Auto Tufan" Poppins
SemiBold, "KAPORTA & BOYA" Poppins (görseldeki yazılar Poppins ile birebir örtüşüyor). Şekiller işe göre: araba,
boya tabancası, fırça darbesi, boya damlaları, kalkan, parlama yıldızları, çerçeve. Her tasarımda ayrı yerleşim.

Lastikçi isimlikleriyle (Uzar, İNCE, Çalık, Soylu) aynı yapı: 120 × 90 mm (4:3), köşeler R8, siyah gövde 1 cm,
yazılar ve şekiller 2 mm kabartma, QR yüzeyle aynı hizada beyaz karo, 15° eğik sehpa. Her satırın en dar harf içi
boşluğu ölçülür (≥ 0,6 mm), öğeler arası ≥ 2 mm; QR görüntüden ve baskı hatası benzetiminden okunur.

QR: işletme sayfası (`autotufan_isimlik/bilgiler.json` → `sayfa_url`, ortak hesapta `deneme123` Worker'ı).

Çıktı : autotufan_isimlik/<tasarım>.png, musteri_1.png (1–6), musteri_2.png (7–10), musteri_katalog.pdf

Kullanım:
  python3 scripts/autotufan_logo.py <logo_görseli>     # bir kez: T harfi
  python3 scripts/autotufan_isimlik.py [anahtar ...]
"""
import json
import os
import sys

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import autotufan_logo as L  # noqa: E402
import calik_isimlik as C  # noqa: E402
import ince_isimlik as N  # noqa: E402
import qr_sistemi as Q  # noqa: E402
import uzar_isimlik as I  # noqa: E402
import uzar_isimlik_baski as B  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "autotufan_isimlik")
DATA = json.load(open(os.path.join(OUT_DIR, "bilgiler.json"), encoding="utf-8"))
PHONE = Q.phone_display(Q.phone_e164(DATA["telefon"]))
BLACK, WHITE, GOLD = A.BLACK, A.WHITE, A.GOLD
SHOW = {BLACK: (40, 40, 43), WHITE: (246, 246, 242), GOLD: (222, 182, 96)}
NAMES = {BLACK: "siyah", WHITE: "beyaz", GOLD: "altın"}
J = m3.JoinType.Round
X0, X1 = -54.0, 54.0
NAME, SUB, SERVICE, CITY = DATA["isim"], DATA["alt"], DATA["hizmet"], DATA["sehir"]
N.FONT_FILES.update({"pop5": "Poppins-Medium.ttf", "pop6": "Poppins-SemiBold.ttf", "pop7": "Poppins-Bold.ttf"})
t, Design = N.t, N.Design
SC = {"body": BLACK, "fg": WHITE, "dark": True}


def make_qr():
    """Sondaki / olmadan adres 3. sürüme (29 × 29) sığar: 30 mm'lik QR'da kare 0,91 mm."""
    import segno
    content = Q.https_url(DATA["sayfa_url"]).rstrip("/")
    q = segno.make(content, error="m", micro=False, boost_error=True)
    return Q.Entry("sayfa", "TARA", content, "TARA", qr=q)


QR = make_qr()


# ---------------------------------------------------------------- logo ve ortak öğeler

def tufan_t(h, x, y, anchor="bl"):
    """Fırça T (altın), yükseklik h mm. anchor: "bl" sol alt köşe (x, y), "c" merkez. Sivri uçlar 0,4 mm nozulla
    basılabilsin diye kenar 0,3 mm dışa alınır (dilimleyici kontrolü: uçlar en az ~0,8 mm)."""
    cs = m3.CrossSection(L.polygons(), m3.FillRule.EvenOdd).scale((h, h)).offset(0.3, J)
    b = cs.bounds()
    if anchor == "c":
        return cs.translate((x - (b[0] + b[2]) / 2, y - (b[1] + b[3]) / 2))
    return cs.translate((x - b[0], y - b[1]))


def name(cap, x, y, align="l", max_w=None):
    return t("pop6", NAME, cap, x, y, align, 0.15, max_w)


def sub(cap, x, y, align="l", width=None, tr=1.0, text=SUB):
    """Adın altındaki satır, KAPORTA & BOYA (Poppins Bold: logodaki Medium 2 mm kabartmada fazla ince kalır); width
    verilirse harf aralığı açılıp o genişliğe yayılır (logodaki gibi ad genişliğinde)."""
    cs = t("pop7", text, cap, x, y, align, tr)
    if width:
        b = cs.bounds()
        tr = max(0.5, tr + (width - (b[2] - b[0])) / (len(text) - 1))      # harfler sıkışmasın
        cs = t("pop7", text, cap, x, y, align, tr)
    return cs


def lockup(d, x, y_top, h, align="l", sub_col=WHITE, sub_text=SUB):
    """Logo: fırça T, yanında Auto Tufan ve altında KAPORTA & BOYA (ya da sub_text; adın genişliğinde). Döner: kutu
    (x0, y0, x1, y1)."""
    T = tufan_t(h, 0, 0)
    tb = T.bounds()
    cap = 0.40 * h
    gap = 0.30 * h
    nm = name(cap, tb[2] + gap, h * 0.62)
    nb = nm.bounds()
    sb_cap = max(4.4, 0.2 * h)
    sb = sub(sb_cap, nb[0], h * 0.62 - cap / 2 - 2.6 - sb_cap / 2, "l", nb[2] - nb[0], text=sub_text)
    w = max(nb[2], sb.bounds()[2]) - tb[0]
    dx = {"l": x - tb[0], "c": x - tb[0] - w / 2, "r": x - tb[0] - w}[align]
    dy = y_top - max(tb[3], nb[3])
    d.add(None, T.translate((dx, dy)), GOLD)
    d.add("Auto Tufan", nm.translate((dx, dy)), WHITE)
    d.add(sub_text, sb.translate((dx, dy)), sub_col)
    return (tb[0] + dx, min(tb[1], sb.bounds()[1]) + dy, tb[0] + dx + w, y_top)


def qr_block(cx, cy, s):
    _, dark, _ = Q.shapes(QR, Q.module_for(QR, s), cx, cy)
    return [(A.rrect(s, s, 1.6, cx, cy) - dark, WHITE)]


def scan(d, cx, cy, s, labels=True):
    """QR ve altında TARA. (Poppins kalın ve geniş: BİZE ULAŞIN QR genişliğine ancak inceltilerek sığar.)"""
    d.inlay += qr_block(cx, cy, s)
    if labels:
        d.add("TARA", t("pop7", "TARA", 4.6, cx, cy - s / 2 - 5.0, "c", 1.6), WHITE)


def phone_line(d, x, y, cap=5.2, align="l", col=WHITE, max_w=72.0, icon=True):
    """Telefon simgesi (altın) ve numara."""
    if not icon:
        d.add("telefon", t("pop7", PHONE, cap, x, y, align, 0.35, max_w), col)
        return
    ic = C.phone_icon(cap * 1.55, 0, 0).offset(0.35, J)
    b = ic.bounds()
    w_ic = b[2] - b[0]
    num = t("pop7", PHONE, cap, 0, 0, "l", 0.2, max_w - w_ic - 2.4)
    nb = num.bounds()
    total = w_ic + 2.4 + (nb[2] - nb[0])
    x0 = {"l": x, "c": x - total / 2, "r": x - total}[align]
    d.add(None, ic.translate((x0 - b[0], y)), GOLD)
    d.add("telefon", num.translate((x0 + w_ic + 2.4 - nb[0], y)), col)


def bar(x0, x1, y, h=1.4):
    return A.rrect(x1 - x0, h, h / 2 - 0.01, (x0 + x1) / 2, y)


def diamond(cx, cy, r):
    return A.polygon([(cx, cy + r), (cx + r, cy), (cx, cy - r), (cx - r, cy)])


# ---------------------------------------------------------------- şekiller (kalın, sade)

def car(x0, y0, length):
    """Araba (yandan): beyaz gövde, altın tekerlekler; sol alt köşe (x0, y0)."""
    shape, body, wc, wr, s = A.car_silhouette(length)
    wheels = A.union(*[A.circle(wr * 0.82, x, y) for x, y in wc])
    gaps = A.union(*[A.circle(wr * 0.82 + 1.0, x, y) for x, y in wc])
    window = A.car_window(body, s, 1.6, 23.8, 80.0, 0.6)
    b = shape.bounds()
    move = lambda cs: cs.translate((x0 - b[0], y0 - b[1]))  # noqa: E731
    return [(move(shape - gaps - window), WHITE), (move(wheels), GOLD)]


def spray_gun(cx, cy, k=1.0):
    """Boya tabancası (sağa bakan): hazne üstte, gövde, tetik ve kabza; namlunun önünde boya zerrecikleri.
    Döner: (tabanca, zerrecikler)."""
    gun = A.union(
        A.rrect(17.0, 5.6, 2.7, 0, 0),                                  # gövde
        A.rect(8.0, -1.5, 11.5, 1.5),                                   # namlu
        A.rrect(2.2, 4.4, 0.6, 12.2, 0),                                # başlık
        A.polygon([(-4.0, 2.0), (-1.0, 2.0), (-1.4, 5.6), (-3.6, 5.6)]),  # hazne boynu
        A.rrect(8.6, 7.8, 2.2, -2.5, 9.0),                              # hazne
        A.rrect(5.2, 14.0, 2.4, 0, 0).rotate(-14).translate((-5.6, -7.0)),  # kabza
    )
    trigger = A.rrect(1.8, 7.0, 0.85, 0, 0).rotate(-14).translate((0.8, -5.6))
    gun = (gun + trigger).offset(-0.4, J).offset(0.4, J)
    dots = []
    for row, (dx, n, spread) in enumerate([(16.5, 3, 2.6), (19.6, 4, 4.4), (22.8, 5, 6.2)]):
        for j in range(n):
            y = (j - (n - 1) / 2) * (2 * spread / max(n - 1, 1))
            dots.append(A.circle(0.95 + 0.12 * row, dx, y, 32))
    f = lambda cs: cs.scale((k, k)).translate((cx, cy))  # noqa: E731
    return f(gun), f(A.union(*dots))


def brush_band(x0, x1, yc, h, seed=3):
    """Fırça darbesi: dalgalı kenarlı bant; sol ucu yuvarlak, sağ ucu fırça kılı gibi üç dişe ayrılır."""
    rng = np.random.default_rng(seed)
    xs = np.linspace(x0, x1, 90)
    u = (xs - x0) / (x1 - x0)
    wob = lambda: np.convolve(rng.normal(0, 0.25, len(xs)), np.ones(7) / 7, "same")  # noqa: E731
    thick = h / 2 * (0.82 + 0.18 * np.sin(np.pi * u) + 0.0)
    top = yc + thick + wob() + 0.6 * np.sin(u * 5.0)
    bot = yc - thick + wob() + 0.6 * np.sin(u * 5.0)
    band = A.polygon(list(zip(xs, top)) + list(zip(xs[::-1], bot[::-1])))
    band = band + A.circle(h * 0.46, x0 + h * 0.3, yc + 0.2)
    slits = A.union(*[A.polygon([(x1 - L, yc + off), (x1 + 2.0, yc + off - w), (x1 + 2.0, yc + off + w)])
                      for L, off, w in ((15.0, -h * 0.30, 1.1), (10.0, -h * 0.05, 0.9), (13.0, h * 0.22, 1.0))])
    edge = A.union(*[A.circle(0.9, x1 - 0.5, yc + y) for y in (-h * 0.42, h * 0.08, h * 0.36)])   # kıl uçları
    return (band - slits - edge).offset(-0.55, J).offset(0.55, J)


def drips(x0, x1, y_top, band_h, specs):
    """Üstte altın bant ve aşağı akan boya damlaları: damla yukarıda geniş, aşağıda yuvarlak uçlu; banda bağlandığı
    köşeler içbükey yumuşar (akan boya gibi). specs: [(x, uzunluk, genişlik)]."""
    band = A.rect(x0, y_top - band_h, x1, y_top)
    out = [band]
    for x, length, w in specs:
        yb = y_top - band_h - length
        out.append(A.polygon([(x - w * 0.62, y_top - band_h + 0.5), (x + w * 0.62, y_top - band_h + 0.5),
                              (x + w / 2, yb), (x - w / 2, yb)]))
        out.append(A.circle(w * 0.56, x, yb, 48))
    cs = A.union(*out)
    cs = cs.offset(1.6, J).offset(-1.6, J)                     # içbükey köşeler: boya banttan akıyor
    return (cs ^ A.rrect(x1 - x0, 200, 2.5, (x0 + x1) / 2, y_top - 100)).offset(-0.4, J).offset(0.4, J)


def shield(cx, cy, w, h, ring=1.8):
    """Kalkan halkası: üstü düz, altı sivri (yuvarlatılmış)."""
    pts = [(-w / 2, h / 2), (w / 2, h / 2), (w / 2, h * 0.08)]
    for a in np.linspace(0, 1, 24)[1:]:                         # sağ yan → alt uç (yay)
        pts.append((w / 2 * (1 - a) ** 1.4, h * 0.08 - (h * 0.58) * np.sin(a * np.pi / 2)))
    for a in np.linspace(0, 1, 24)[1:-1][::-1]:
        pts.append((-w / 2 * (1 - a) ** 1.4, h * 0.08 - (h * 0.58) * np.sin(a * np.pi / 2)))
    pts.append((-w / 2, h * 0.08))
    outer = A.polygon(pts).offset(-1.0, J).offset(1.0, J).translate((cx, cy))
    return outer - outer.offset(-ring, J)


def sparkle(cx, cy, r):
    """Dört kollu parlama yıldızı (kollar içbükey)."""
    pts = []
    for k in range(4):
        a = np.radians(90 * k)
        pts.append((cx + r * np.cos(a), cy + r * np.sin(a)))
        for u in np.linspace(0.2, 0.8, 5):                      # kol arası içbükey eğri
            b = np.radians(90 * k + 90 * u)
            rr = r * 0.3 + r * 0.55 * (abs(u - 0.5) * 2) ** 2.4
            pts.append((cx + rr * np.cos(b), cy + rr * np.sin(b)))
    return A.polygon(pts).offset(-0.6, J).offset(0.6, J)


# ---------------------------------------------------------------- tasarımlar

def d1_klasik():
    d = Design("1_klasik_logo", "Klasik logo", "Logonun aynısı: altın fırça T, Auto Tufan ve KAPORTA & BOYA; altta "
               "hasar onarım, telefon ve QR.", SC)
    lockup(d, X0, 84.0, 18.0)
    d.add(None, bar(X0, X0 + 22.0, 59.0), GOLD)
    d.add("HASAR ONARIM", t("pop7", SERVICE, 4.6, X0, 50.0, "l", 1.0), WHITE)
    d.add("ANTALYA", t("pop7", CITY, 4.6, X0, 41.5, "l", 1.4), GOLD)
    phone_line(d, X0, 22.0, 5.2, max_w=72.0)
    scan(d, X1 - 16.0, 17.0 + 6.5 + 4.6 + 16.0, 32.0)
    return d


def d2_ortali():
    d = Design("2_ortali", "Ortalı", "Altın T ortada; altında Auto Tufan, KAPORTA & BOYA ve telefon; en altta ortada "
               "QR.", SC)
    d.add(None, tufan_t(14.0, 0, 79.0, "c"), GOLD)
    d.add("Auto Tufan", name(8.0, 0, 65.0, "c"), WHITE)
    nb = d.lines["Auto Tufan"].bounds()
    d.add("KAPORTA & BOYA", sub(4.4, 0, 56.0, "c", nb[2] - nb[0]), GOLD)
    phone_line(d, 0, 48.5, 5.0, align="c", max_w=72.0, icon=False)
    s = 30.0
    d.inlay += qr_block(0, 12.0 + s / 2, s)
    d.add("TARA", t("pop7", "TARA", 4.4, -36.0, 30.5, "c", 1.4), WHITE)
    d.add(None, N.arrow(-23.0, 30.5, 6.0).offset(-0.4, J).offset(0.4, J), GOLD)
    d.add("BİZE", t("pop7", "BİZE", 4.8, 35.5, 33.5, "c", 0.8), GOLD)
    d.add("ULAŞIN", t("pop7", "ULAŞIN", 4.8, 35.5, 26.5, "c", 0.6), GOLD)
    return d


def d3_araba():
    d = Design("3_araba", "Araba", "Solda beyaz araba silüeti, altın tekerlekler ve altında altın çizgi; yanında Auto "
               "Tufan.", SC)
    for cs, col in car(X0, 68.0, 42.0):
        d.add(None, cs, col)
    d.add(None, bar(X0, X0 + 42.0, 64.5, 1.6), GOLD)
    x = X0 + 48.0
    d.add("Auto Tufan", name(7.6, x, 79.0, "l", X1 - x), WHITE)
    nb = d.lines["Auto Tufan"].bounds()
    d.add("KAPORTA & BOYA", sub(4.4, x, 69.5, "l", nb[2] - nb[0]), GOLD)
    d.add("HASAR ONARIM", t("pop7", SERVICE, 4.6, X0, 46.0, "l", 1.0), WHITE)
    d.add("HEMEN ARA", t("pop7", "HEMEN ARA", 4.6, X0, 33.0, "l", 1.2), GOLD)
    phone_line(d, X0, 22.0, 5.2, max_w=72.0)
    scan(d, X1 - 16.0, 17.0 + 6.5 + 4.6 + 16.0, 32.0)
    return d


def d4_tabanca():
    d = Design("4_boya_tabancasi", "Boya tabancası", "Solda QR; sağda altın boya tabancası ve beyaz boya zerrecikleri, "
               "altında Auto Tufan.", SC)
    gun, dots = spray_gun(6.0, 74.0, 0.95)
    d.add(None, gun, GOLD)
    d.add(None, dots, WHITE)
    cx = 19.5
    d.add("Auto Tufan", name(7.4, cx, 55.5, "c", 56.0), WHITE)
    nb = d.lines["Auto Tufan"].bounds()
    d.add("KAPORTA & BOYA", sub(4.4, cx, 46.5, "c", nb[2] - nb[0]), GOLD)
    d.add("HASAR ONARIM", t("pop7", SERVICE, 4.6, cx, 33.0, "c", 0.9), WHITE)
    phone_line(d, cx, 22.0, 5.0, align="c", max_w=72.0)
    scan(d, X0 + 17.0, 17.0 + 6.5 + 4.6 + 17.0, 34.0)
    return d


def d5_firca():
    d = Design("5_firca_darbesi", "Fırça darbesi", "Üstte altın fırça darbesi, içinde oyma Auto Tufan; altında "
               "KAPORTA & BOYA.", SC)
    band = brush_band(X0, X1 - 4.0, 73.0, 17.0)
    cut = name(9.4, -2.0, 73.0, "c", 92.0)
    d.add("fırça", band - cut.offset(0.1, J), GOLD)
    d.add("KAPORTA & BOYA", sub(4.6, X0, 55.0, "l", 66.0), WHITE)
    d.add("HASAR ONARIM", t("pop7", SERVICE, 4.6, X0, 40.0, "l", 1.0), GOLD)
    phone_line(d, X0, 25.0, 5.2, max_w=72.0)
    s = 30.0
    d.inlay += qr_block(X1 - s / 2, 17.0 + s / 2 + 6.0, s)
    d.add("TARA", t("pop7", "TARA", 4.4, X1 - s / 2, 17.5, "c", 1.4), WHITE)
    return d


def d6_cerceve():
    d = Design("6_altin_cerceve", "Altın çerçeve", "İnce altın çerçeve, üst kenarında araya giren fırça T; içinde "
               "ortalı yazılar, sağda QR.", SC)
    frame = A.rrect(108.0, 68.0, 5.0, 0, 46.0)                 # y 12..80
    ring = frame - frame.offset(-1.3, J)
    T = tufan_t(11.5, -20.0, 80.0, "c")
    d.add(None, ring - T.offset(2.4, J), GOLD)
    d.add(None, T, GOLD)
    cx = -20.0
    d.add("Auto Tufan", name(7.0, cx, 65.0, "c", 60.0), WHITE)
    nb = d.lines["Auto Tufan"].bounds()
    d.add("KAPORTA & BOYA", sub(4.4, cx, 56.5, "c", nb[2] - nb[0]), GOLD)
    d.add(None, diamond(cx, 48.8, 1.8), GOLD)
    d.add("HASAR ONARIM", t("pop7", SERVICE, 4.6, cx, 41.0, "c", 0.9), WHITE)
    phone_line(d, cx, 27.0, 5.0, align="c", max_w=60.0, icon=False)      # simgeyle çerçeveye yaklaşır
    s = 30.0
    d.inlay += qr_block(30.5, 52.0, s)
    d.add("TARA", t("pop7", "TARA", 4.6, 30.5, 52.0 - s / 2 - 5.2, "c", 1.6), WHITE)
    return d


def d7_kalkan():
    d = Design("7_kalkan", "Kalkan", "Solda altın kalkan, içinde beyaz fırça T (hasar onarımda güvence); yanında Auto Tufan.",
               SC)
    cx, cy = X0 + 13.0, 72.0
    d.add(None, shield(cx, cy, 26.0, 26.0, 1.6), GOLD)
    d.add(None, tufan_t(8.6, cx, cy + 1.2, "c"), WHITE)
    x = X0 + 30.0
    d.add("Auto Tufan", name(7.6, x, 78.0, "l", X1 - x), WHITE)
    nb = d.lines["Auto Tufan"].bounds()
    d.add("KAPORTA & BOYA", sub(4.4, x, 68.5, "l", nb[2] - nb[0]), GOLD)
    d.add("HASAR ONARIM", t("pop7", SERVICE, 4.6, X0, 46.0, "l", 1.0), WHITE)
    d.add("ANTALYA", t("pop7", CITY, 4.6, X0, 37.5, "l", 1.4), GOLD)
    phone_line(d, X0, 22.0, 5.2, max_w=72.0)
    scan(d, X1 - 16.0, 17.0 + 6.5 + 4.6 + 16.0, 32.0)
    return d


def d8_damla():
    d = Design("8_boya_damlasi", "Boya damlaları", "Üst kenardan akan altın boya damlaları; altında iri Auto Tufan.", SC)
    d.add(None, drips(X0, X1, 87.0, 4.0, [(-43.0, 9.0, 3.6), (-30.0, 4.5, 3.0), (-8.0, 7.0, 3.4), (16.0, 11.0, 3.8),
                                          (38.0, 5.5, 3.2)]), GOLD)
    d.add("Auto Tufan", name(9.6, X0, 62.0, "l", 70.0), WHITE)
    nb = d.lines["Auto Tufan"].bounds()
    d.add("KAPORTA & BOYA", sub(4.4, X0, 51.0, "l", nb[2] - nb[0]), GOLD)
    d.add("HASAR ONARIM", t("pop7", SERVICE, 4.6, X0, 37.0, "l", 1.0), WHITE)
    phone_line(d, X0, 23.0, 5.2, max_w=72.0)
    s = 30.0
    d.inlay += qr_block(X1 - s / 2, 22.5 + s / 2, s)
    d.add("TARA", t("pop7", "TARA", 4.4, X1 - s / 2, 16.5, "c", 1.4), WHITE)
    return d


def d9_parlama():
    d = Design("9_parlama", "Parlama", "Solda QR; sağda altın T ve çevresinde parlama yıldızları (pırıl pırıl boya); "
               "altında Auto Tufan.", SC)
    cx = 19.5
    d.add(None, tufan_t(16.0, cx, 74.0, "c"), GOLD)
    d.add(None, sparkle(cx + 19.5, 80.5, 5.0) + sparkle(cx - 19.5, 69.0, 3.8), WHITE)
    d.add("Auto Tufan", name(7.4, cx, 53.0, "c", 56.0), WHITE)
    nb = d.lines["Auto Tufan"].bounds()
    d.add("KAPORTA & BOYA", sub(4.4, cx, 44.0, "c", nb[2] - nb[0]), GOLD)
    d.add("HEMEN ARA", t("pop7", "HEMEN ARA", 4.6, cx, 33.0, "c", 1.0), WHITE)
    phone_line(d, cx, 22.0, 5.0, align="c", max_w=72.0)
    scan(d, X0 + 17.0, 17.0 + 6.5 + 4.6 + 17.0, 34.0)
    return d


def d10_alt_bant():
    d = Design("10_alt_bant", "Alt bant", "Üstte logo; altta altın bant içinde oyma telefon; ortada hasar onarım ve QR.",
               SC)
    lockup(d, X0, 85.0, 15.0)
    d.add("HASAR ONARIM", t("pop7", SERVICE, 4.6, X0, 52.0, "l", 1.0, 70.0), WHITE)
    d.add("HEMEN ARA", t("pop7", "HEMEN ARA", 4.6, X0, 42.5, "l", 1.2), GOLD)
    d.add(None, bar(X0, X0 + 16.0, 35.0), WHITE)
    band = A.rrect(X1 - X0, 13.0, 3.0, 0, 19.0)
    ic = C.phone_icon(7.6, X0 + 9.0, 19.0).offset(0.25, J)
    num = t("pop7", PHONE, 5.6, X0 + 16.0, 19.0, "l", 1.1, 76.0)       # oyma: rakam araları ≥ 1 mm altın
    d.add("bant", band - ic - num, GOLD)
    s = 30.0
    d.inlay += qr_block(X1 - s / 2, 29.0 + s / 2, s)
    return d


def secilen():
    """Müşterinin seçtiği: 1 · Klasik logo, ama KAPORTA & BOYA yazmasın, yalnız HASAR ONARIM: logonun altındaki satır
    HASAR ONARIM olur (alttaki ayrı satır kalkar, tekrar etmez); altta ANTALYA, HEMEN ARA, telefon ve QR."""
    d = Design("1_klasik_logo_hasar_onarim", "Klasik logo (seçilen)", "Logo: altın fırça T, Auto Tufan ve altında "
               "HASAR ONARIM; altta Antalya, hemen ara, telefon ve QR.", SC)
    lockup(d, X0, 84.0, 18.0, sub_text=SERVICE)
    d.add(None, bar(X0, X0 + 22.0, 59.0), GOLD)
    d.add("ANTALYA", t("pop7", CITY, 4.6, X0, 50.0, "l", 1.4), WHITE)
    d.add("HEMEN ARA", t("pop7", "HEMEN ARA", 4.6, X0, 33.0, "l", 1.2), GOLD)
    phone_line(d, X0, 22.0, 5.2, max_w=72.0)
    scan(d, X1 - 16.0, 17.0 + 6.5 + 4.6 + 16.0, 32.0)
    return d


DESIGNS = [d1_klasik, d2_ortali, d3_araba, d4_tabanca, d5_firca, d6_cerceve, d7_kalkan, d8_damla, d9_parlama,
           d10_alt_bant]


# ---------------------------------------------------------------- katılar, kontrol, çizim

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
    return [("Panel (siyah)", body, BLACK)] + parts


def build(fn):
    d = fn()
    d.parts = solids(d)
    d.stand, (z0, y0) = B.stand()
    d.shown = B.assembled(d.parts, z0, y0) + [("Sehpa", d.stand, BLACK)]
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


def t_raster(h, colour):
    """Fırça T, h piksel yüksekliğinde RGBA."""
    ss = 4
    rings = L.polygons()
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
    dr.text((30, 94), f"Gövde 1 cm, kabartma 2 mm · en dar harf içi boşluk {worst:.2f} mm · QR "
                      f"{'okundu' if d.qr[0] else 'OKUNMADI'}{', benzetimde de' if d.qr[1] else ''}",
            fill=(22, 120, 60) if d.qr[0] and worst >= 0.6 else (200, 30, 38), font=font_ui(18))
    canvas.save(os.path.join(OUT_DIR, d.key + ".png"))


def header(im, dr, W, page):
    """Siyah başlık: logo (altın T, Auto Tufan, KAPORTA & BOYA) ve ince altın çizgi."""
    gold = SHOW[GOLD]
    dr.rectangle((0, 0, W, 250), fill=(22, 22, 24))
    T = t_raster(130, gold)
    im.paste(T, (70, 60), T)
    x = 70 + T.width + 46
    dr.text((x, 52), NAME, font=font_ui(92), fill=(246, 246, 242))
    f = font_ui(36, "Medium")
    xx = x + 4
    for ch in SUB:
        dr.text((xx, 162), ch, font=f, fill=(200, 200, 204))
        xx += dr.textlength(ch, font=f) + 12
    dr.text((W - 100 - dr.textlength("QR'lı masa isimliği", font=font_ui(30)), 70), "QR'lı masa isimliği",
            font=font_ui(30), fill=gold)
    dr.text((W - 100 - dr.textlength(f"tasarım önerileri · {page}/2", font=font_ui(26, "Regular")), 120),
            f"tasarım önerileri · {page}/2", font=font_ui(26, "Regular"), fill=(200, 200, 204))
    dr.rectangle((0, 246, W, 254), fill=gold)


def catalog(ds):
    """Müşteriye: musteri_1.png (1–6), musteri_2.png (7–10), musteri_katalog.pdf."""
    W, H = 1654, 2339
    f = font_ui
    ink, muted, paper, gold = (20, 20, 22), (96, 98, 106), (245, 244, 240), SHOW[GOLD]
    pages = []
    for p, group in enumerate([ds[:6], ds[6:]]):
        im = Image.new("RGB", (W, H), paper)
        dr = ImageDraw.Draw(im)
        header(im, dr, W, p + 1)
        y = 285
        for line in ("QR: telefonla okutunca işletmenin sayfası açılır (arama, WhatsApp, konum, yorum).",
                     "Hepsi siyah zemin, altın ve beyaz kabartma yazı ve şekil; her birinde ayrı yerleşim."):
            dr.text((70, y), line, font=f(27, "Regular"), fill=ink)
            y += 42
        top, gap, cw = 395, 50, (W - 3 * 60) // 2
        ch = (H - top - 190 - 2 * gap) // 3
        for k, d in enumerate(group):
            x0, y0 = 60 + (k % 2) * (cw + 60), top + (k // 2) * (ch + gap)
            dr.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 28, fill=(255, 255, 255), outline=(226, 224, 218))
            n = ds.index(d) + 1
            dr.ellipse((x0 + 26, y0 + 24, x0 + 86, y0 + 84), fill=(22, 22, 24))
            dr.text((x0 + 56 - dr.textlength(str(n), font=f(32)) / 2, y0 + 30), str(n), font=f(32), fill=gold)
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
                         "Yazılar ve şekiller 2 mm kabartma; QR düz ve keskin",
                         "Masa sehpası dahil, panel 15° eğik durur",
                         "QR işletme sayfasını açar"):
                dr.ellipse((100, ty + 12, 114, ty + 26), fill=gold)
                dr.text((130, ty), line, font=f(28, "Regular"), fill=muted)
                ty += 56
            img = A.fit_into(render(mesh(ds[0].shown), 1200, rotation(-28, -68), margin=0.02), 520, y1 - y0 - 60)
            im.paste(img, (W - 100 - img.width, y0 + (y1 - y0 - img.height) // 2), img)
        foot = ("Beğendiğiniz tasarımın numarasını yazmanız yeterli." if p == 1 else
                "Ölçü 12 × 9 cm · 1 cm kalın · kabartma yazı · masa sehpası dahil")
        dr.rounded_rectangle((60, H - 150, W - 60, H - 70), 22, fill=(22, 22, 24))
        dr.text((W / 2 - dr.textlength(foot, font=f(28)) / 2, H - 128), foot, font=f(28), fill=(246, 246, 242))
        im.save(os.path.join(OUT_DIR, f"musteri_{p + 1}.png"), optimize=True)
        im.convert("RGB").save(os.path.join(OUT_DIR, f"musteri_{p + 1}.jpg"), "JPEG", quality=90, optimize=True)
        pages.append(im)
    pages[0].save(os.path.join(OUT_DIR, "musteri_katalog.pdf"), save_all=True, append_images=pages[1:],
                  resolution=200)


def check(i):
    """i. tasarım (ayrı süreçte): ölçümler, QR okuma, ayrıntı sayfası. Döner satır."""
    d = build(DESIGNS[i - 1])
    d.metrics = {k: B.line_metrics(cs) for k, cs in d.lines.items()}
    d.qr = qr_check(d)
    sheet(d, i)
    bad = {k: tuple(round(x, 2) for x in v) for k, v in d.metrics.items() if v[0] < 0.6 or v[2] > 6.0}
    return (f"{d.key:20s} QR {d.qr}  simgelerde 1,2 mm'den ince %{C.thin_shapes(d)}  dar/ince satırlar: "
            f"{bad or 'yok'}  sıkışık: {C.crowded(d) or 'yok'}")


def main():
    from multiprocessing import Pool
    os.makedirs(OUT_DIR, exist_ok=True)
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
