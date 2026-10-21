"""ÇALIK OTO LASTİK – tek QR'lı tezgâh isimliği önerileri (10): hepsi siyah zemin, sarı ve beyaz yazı, simgeli.

Her tasarım ayrı fikir, ayrı simge ve yazı tipi: jant (Russo One), anahtar (Archivo Black), telefon (Bebas Neue),
ikaz şeridi (Lexend), hız göstergesi (Teko), araba (Oswald), lastik izi (Barlow Condensed), şimşek (Saira
Condensed, italik), dama bayrağı (Outfit), sarı blok (Archivo Black, oyma yazı). Simgeler kalın ve sade: en ince
yeri ≥ 1,2 mm, makinede kolay basılır.

İNCE / Uzar isimlikleriyle aynı yapı: 120 × 90 mm (4:3), köşeler R8, siyah gövde 1 cm, yazılar ve simgeler 2 mm
kabartma, QR yüzeyle aynı hizada beyaz karo, 15° eğik sehpa. Küçük satırlar Outfit ExtraBold; her yazı satırının en
dar harf içi boşluğu ölçülür.

QR: Google yorum QR'ı (üstünde beş sarı yıldız, altında GOOGLE / YORUM YAP). Bağlantı `calik_isimlik/bilgiler.json`
→ `google`: işletmenin "yorum iste" bağlantısı (g.page/r/…/review) gelene kadar Google'da "çalık oto lastik"
araması.

Çıktı : calik_isimlik/<tasarım>.png, calik_isimlik/musteri_1.png, musteri_2.png, musteri_katalog.pdf

Kullanım:
  pip install svgelements
  python3 scripts/calik_isimlik.py [anahtar ... | katalog]
"""
import json
import os
import re
import sys

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import ince_isimlik as N  # noqa: E402
import qr_sistemi as Q  # noqa: E402
import uzar_anahtarlik as U  # noqa: E402
import uzar_isimlik as I  # noqa: E402
import uzar_isimlik_baski as B  # noqa: E402
import uzar_sayfa as S  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "calik_isimlik")
DATA = json.load(open(os.path.join(OUT_DIR, "bilgiler.json"), encoding="utf-8"))
TEL = Q.phone_e164(DATA["telefon"])
PHONE = Q.phone_display(TEL)
BLACK, WHITE, YELLOW = A.BLACK, A.WHITE, A.YELLOW
SHOW = {**B.SHOW, YELLOW: (250, 198, 24)}
NAMES = {BLACK: "siyah", WHITE: "beyaz", YELLOW: "sarı"}
J = m3.JoinType.Round
X0, X1 = -54.0, 54.0
t, bar, arrow, Design = N.t, N.bar, N.arrow, N.Design
SC = {"body": BLACK, "fg": WHITE, "dark": True}


def make_qr():
    """İşletme sayfası yayındaysa onun, değilse Google yorumlarının QR'ı (sürüm ≥ 4; hata düzeltmesi sığdığı kadar
    yükseltilir)."""
    import segno
    if DATA.get("sayfa_url"):
        content, key, label = Q.https_url(DATA["sayfa_url"]), "sayfa", "TARA"
    else:
        content, key, label = Q.google_url(DATA["google"]), "google", "GOOGLE YORUM"
    natural = segno.make(content, error="m", micro=False).version
    q = segno.make(content, error="m", version=max(4, natural), micro=False, boost_error=True)
    return Q.Entry(key, label, content, label, qr=q)


QR = make_qr()
SITE = QR.key == "sayfa"
SAMPLE_LINK = "/search?" in QR.content          # işletmenin yorum bağlantısı gelene kadar Google araması


def qr_block(cx, cy, s):
    """QR: yüzeyle aynı hizada beyaz karo, siyah kareler gövdenin kendisi."""
    _, dark, _ = Q.shapes(QR, Q.module_for(QR, s), cx, cy)
    return [(A.rrect(s, s, 1.6, cx, cy) - dark, WHITE)]


def stars(cx, cy, r=3.0, n=5, gap=1.0):
    """Beş sarı yıldız (Google puanı); kollar kalın, uçlar yuvarlatılmış (1,2 mm'den ince alan < %5)."""
    pitch = 2 * r * np.cos(np.radians(18)) + gap
    out = []
    for i in range(n):
        x = cx + (i - (n - 1) / 2) * pitch
        out.append(A.polygon([(x + (r if k % 2 == 0 else r * 0.58) * np.cos(np.radians(90 + 36 * k)),
                               cy + (r if k % 2 == 0 else r * 0.58) * np.sin(np.radians(90 + 36 * k)))
                              for k in range(10)]))
    return A.union(*out).offset(-0.55, J).offset(0.55, J)


def review(d, cx, cy, s, top=True):
    """QR ve altında iki satır. Site QR'ı: TARA / BİZE ULAŞIN. Google yorum QR'ı: üstünde beş sarı yıldız (top),
    altında GOOGLE / YORUM YAP."""
    d.inlay += qr_block(cx, cy, s)
    if top and not SITE:
        d.add(None, stars(cx, cy + s / 2 + 4.6), YELLOW)
    y = cy - s / 2 - 4.6
    (a, ta), (b, tb) = ((("TARA", 1.2), ("BİZE ULAŞIN", 0.3)) if SITE else (("GOOGLE", 0.8), ("YORUM YAP", 0.3)))
    cap = 4.4 if SITE else 4.2                      # BİZE ULAŞIN'ın Ş / Ğ'si 4,2'de ince kalıyor
    d.add(a, t("outfit", a, cap, cx, y, "c", ta), WHITE)
    d.add(b, t("outfit", b, cap, cx, y - 6.5, "c", tb), YELLOW)


# ---------------------------------------------------------------- simgeler (kalın, sade)

def wheel(cx, cy, R=13.5):
    """Jant: beyaz lastik halkası, sarı jant (5 bijon deliği ve göbek)."""
    holes = A.union(A.circle(R * 0.11, cx, cy), *[A.circle(R * 0.093, cx + R * 0.32 * np.cos(a),
                                                              cy + R * 0.32 * np.sin(a))
                                                     for a in np.radians(np.arange(5) * 72 + 90)])
    return [(A.circle(R, cx, cy) - A.circle(R * 0.66, cx, cy), WHITE),
            (A.circle(R * 0.56, cx, cy) - holes, YELLOW)]


def wrench(cx, cy, L=30.0, angle=-35.0):
    """İngiliz anahtarı: bir ucu açık ağız, öbür ucu halka."""
    w = 5.2
    handle = A.rrect(L - 10.0, w, w / 2 - 0.01, 0, 0)
    head = A.circle(6.6, L / 2 - 3.5, 0) - A.rect(L / 2 - 3.5, -2.4, L / 2 + 8.0, 2.4)
    ring = A.circle(5.2, -L / 2 + 3.5, 0) - A.circle(2.5, -L / 2 + 3.5, 0)
    return (handle + head + ring).rotate(angle).translate((cx, cy))


def svg_icon(path, size, cx, cy):
    """24 birimlik SVG yolundan (Material simgeleri) dolu şekil, `size` mm, merkez (cx, cy)."""
    import svgelements as se
    k, loops = size / 24.0, []
    for sp in se.Path(path).as_subpaths():
        pts = []
        for seg in se.Path(sp):
            if isinstance(seg, se.Move):
                continue
            if isinstance(seg, (se.Line, se.Close)):
                pts.append((seg.end.x, seg.end.y))
            else:
                pts += [(seg.point(u).x, seg.point(u).y) for u in np.linspace(0, 1, 16)[1:]]
        if len(pts) > 2:
            loops.append([((x - 12.0) * k + cx, (12.0 - y) * k + cy) for x, y in pts])
    return m3.CrossSection(loops, m3.FillRule.NonZero)


def phone_icon(size, cx, cy):
    return svg_icon(S.ICON["phone"], size, cx, cy)


def gauge(cx, cy, R=14.0):
    """Hız göstergesi: sarı yay (200° → −20°), beyaz ibre ve göbek."""
    a = np.radians(np.linspace(-20, 200, 60))
    sector = A.polygon([(cx, cy)] + [(cx + (R + 1) * np.cos(x), cy + (R + 1) * np.sin(x)) for x in a])
    arc = (A.circle(R, cx, cy) - A.circle(R - 3.2, cx, cy)) ^ sector
    th = np.radians(42.0)
    tip = (cx + (R - 5.0) * np.cos(th), cy + (R - 5.0) * np.sin(th))
    nx, ny = -np.sin(th) * 1.3, np.cos(th) * 1.3
    needle = A.polygon([(cx + nx, cy + ny), tip, (cx - nx, cy - ny)]) + A.circle(2.6, cx, cy)
    ticks = A.union(*[A.rrect(1.4, 3.0, 0.5, 0, 0).rotate(np.degrees(x) - 90).translate(
        (cx + (R - 6.2) * np.cos(x), cy + (R - 6.2) * np.sin(x))) for x in np.radians([200, 145, 90, 35, -20])])
    return [(arc, YELLOW), (needle + ticks, WHITE)]


def car(x0, y0, length=46.0):
    """Araba silüeti (yandan): beyaz gövde, sarı tekerlekler; sol alt köşe (x0, y0)."""
    shape, body, wc, wr, _ = A.car_silhouette(length)
    wheels = A.union(*[A.circle(wr * 0.82, x, y) for x, y in wc])
    gaps = A.union(*[A.circle(wr * 0.82 + 1.0, x, y) for x, y in wc])
    b = shape.bounds()
    move = lambda cs: cs.translate((x0 - b[0], y0 - b[1]))  # noqa: E731
    return [(move(shape - gaps), WHITE), (move(wheels), YELLOW)]


def hazard(x0, x1, y0, y1, w=4.0):
    """İkaz şeridi: 45° sarı şeritler (aralar siyah gövde)."""
    h = y1 - y0
    stripes = A.union(*[A.polygon([(x, y0), (x + w, y0), (x + w + h, y1), (x + h, y1)])
                        for x in np.arange(x0 - h, x1, 2 * w)])
    return stripes ^ A.rrect(x1 - x0, h, 1.2, (x0 + x1) / 2, (y0 + y1) / 2)


# ---------------------------------------------------------------- tasarımlar

def c1_jant():
    d = Design("1_jant", "Jant", "Jant simgesi (beyaz lastik, sarı jant) ve ÇALIK; sağda yıldızlı Google yorum QR'ı.", SC)
    for cs, col in wheel(-42.0, 71.0, 12.0):
        d.add(None, cs, col)
    d.add("ÇALIK", t("russo", "ÇALIK", 11.0, -26.0, 74.5, "l", 0.6, 38.0), WHITE)
    d.add("OTO LASTİK", t("russo", "OTO LASTİK", 5.4, X0, 52.0, "l", 0.6, 60.0), YELLOW)
    d.add("HEMEN ARA", t("outfit", "HEMEN ARA", 4.6, X0, 37.0, "l", 0.9), YELLOW)
    d.add("telefon", t("outfit", PHONE, 5.4, X0, 26.0, "l", 0.4, 60.0), WHITE)
    review(d, 35.0, 50.0, 38.0)
    return d


def c2_anahtar():
    d = Design("2_anahtar", "Anahtar", "Solda sarı İngiliz anahtarı ve Google yorum QR'ı; sağda ÇALIK ve telefon.", SC)
    x0 = -6.0
    d.add(None, wrench(-33.0, 77.0, 40.0, 0.0), YELLOW)
    review(d, -33.0, 46.0, 40.0, top=False)
    d.add("ÇALIK", t("archivo", "ÇALIK", 12.0, x0, 74.0, "l", 0.5, X1 - x0), WHITE)
    d.add("OTO LASTİK", t("archivo", "OTO LASTİK", 5.6, x0, 57.5, "l", 0.6, X1 - x0), YELLOW)
    d.add("HEMEN ARA", t("outfit", "HEMEN ARA", 4.6, x0, 38.5, "l", 0.9), YELLOW)
    d.add("telefon", t("outfit", PHONE, 5.0, x0, 28.0, "l", 0.4, X1 - x0), WHITE)
    return d


def c3_telefon():
    d = Design("3_telefon", "Telefon", "Büyük ince uzun ÇALIK; altta sarı telefon simgesiyle büyük numara.", SC)
    d.add("ÇALIK", t("bebas", "ÇALIK", 28.0, X0, 66.5, "l", 1.2, 64.0), WHITE)
    d.add(None, bar(X0, -14.0, 45.8, 1.6), YELLOW)
    d.add("OTO LASTİK", t("outfit", "OTO LASTİK", 5.0, X0, 38.5, "l", 1.9), YELLOW)
    d.add(None, phone_icon(10.0, X0 + 5.0, 17.0), YELLOW)
    d.add("telefon", t("outfit", PHONE, 6.0, X0 + 12.0, 17.0, "l", 0.4, 56.0), WHITE)
    review(d, 35.0, 52.0, 38.0)
    return d


def c4_ikaz():
    d = Design("4_ikaz", "İkaz şeridi", "Üstte ve altta sarı-siyah ikaz şeridi; geniş, sağlam yazılar.", SC)
    d.add(None, hazard(X0, X1, 79.0, 86.0), YELLOW)
    d.add("ÇALIK", t("lexend", "ÇALIK", 12.0, X0, 65.0, "l", 0.6, 62.0), WHITE)
    d.add("OTO LASTİK", t("lexend", "OTO LASTİK", 5.0, X0, 48.5, "l", 0.6, 62.0), YELLOW)
    d.add("HEMEN ARA", t("outfit", "HEMEN ARA", 4.6, X0, 35.5, "l", 0.9), YELLOW)
    d.add("telefon", t("outfit", PHONE, 5.2, X0, 25.0, "l", 0.4, 62.0), WHITE)
    d.add(None, hazard(X0, 9.0, 10.0, 15.0), YELLOW)
    review(d, 35.0, 49.0, 38.0)
    return d


def c5_gosterge():
    d = Design("5_gosterge", "Hız göstergesi", "Solda sarı hız göstergesi simgesi; uzun, sportif ÇALIK.", SC)
    for cs, col in gauge(-40.0, 66.0):
        d.add(None, cs, col)
    d.add("ÇALIK", t("teko", "ÇALIK", 20.0, -22.0, 72.0, "l", 0.8, 36.0), WHITE)
    d.add("OTO LASTİK", t("teko", "OTO LASTİK", 6.8, X0, 46.5, "l", 1.0, 60.0), YELLOW)
    d.add("HEMEN ARA", t("outfit", "HEMEN ARA", 4.6, X0, 34.0, "l", 0.9), YELLOW)
    d.add("telefon", t("outfit", PHONE, 5.2, X0, 23.5, "l", 0.4, 62.0), WHITE)
    review(d, 35.0, 44.0, 38.0)
    return d


def c6_araba():
    d = Design("6_araba", "Araba", "Sarı yolda giden araba; sağda yıldızlı Google yorum QR'ı.", SC)
    d.add("ÇALIK", t("oswald", "ÇALIK", 14.0, X0, 76.0, "l", 1.2, 60.0), WHITE)
    d.add("OTO LASTİK", t("oswald", "OTO LASTİK", 7.0, X0, 56.8, "l", 1.0, 60.0), YELLOW)
    for cs, col in car(X0, 37.0, 40.0):
        d.add(None, cs, col)
    d.add(None, A.union(*[bar(x, x + 6.0, 34.0, 1.4) for x in np.arange(X0, -8.0, 9.0)]), YELLOW)
    d.add("HEMEN ARA", t("outfit", "HEMEN ARA", 4.4, X0, 26.5, "l", 0.9), YELLOW)
    d.add("telefon", t("outfit", PHONE, 5.2, X0, 17.0, "l", 0.4, 62.0), WHITE)
    review(d, 35.0, 49.0, 38.0)
    return d


def c7_lastik_izi():
    d = Design("7_lastik_izi", "Lastik izi", "Üstte boydan kalın sarı lastik izi okları; altında ÇALIK OTO LASTİK.", SC)
    # hiza: okların ucu QR'ın sağ kenarında (X1); QR'ın üstü ÇALIK'ın üstüyle, alt satırı telefonla aynı hizada
    s = 44.0
    n, w, h = 12, 2.6, 8.0
    pitch = (X1 - X0 - w - h / 2) / (n - 1)
    d.add(None, U.chevrons(X0, 80.5, h, n, pitch, w).offset(-0.5, J).offset(0.5, J), YELLOW)   # uçlar yuvarlak
    d.add("ÇALIK", t("barlow", "ÇALIK", 18.0, X0, 64.0, "l", 0.8, 60.0), WHITE)
    d.add("OTO LASTİK", t("barlow", "OTO LASTİK", 8.6, X0, 40.6, "l", 0.7, 61.0), YELLOW)
    d.add("HEMEN ARA", t("outfit", "HEMEN ARA", 4.6, X0, 27.0, "l", 0.9), YELLOW)
    d.add("telefon", t("outfit", PHONE, 5.2, X0, 17.0, "l", 0.4, 60.0), WHITE)
    review(d, X1 - s / 2, 17.0 + 6.5 + 4.6 + s / 2, s)
    return d


def c8_simsek():
    d = Design("8_simsek", "Şimşek", "Solda büyük sarı şimşek; eğik, hızlı ÇALIK yazısı.", SC)
    d.add(None, U.bolt(27.0, -44.0, 59.0), YELLOW)
    d.add("ÇALIK", t("saira", "ÇALIK", 19.0, -31.0, 66.0, "l", 0.8, 41.0, shear=10.0), WHITE)
    d.add("OTO LASTİK", t("saira", "OTO LASTİK", 6.4, -31.0, 49.0, "l", 0.6, 43.0, shear=10.0), YELLOW)
    d.add("HEMEN ARA", t("outfit", "HEMEN ARA", 4.6, X0, 31.0, "l", 0.9), YELLOW)
    d.add("telefon", t("outfit", PHONE, 5.2, X0, 20.0, "l", 0.4, 60.0), WHITE)
    review(d, 35.0, 44.0, 38.0)
    return d


def c9_dama():
    d = Design("9_dama", "Dama bayrağı", "Üstte beyaz dama şeridi; QR solda, yazılar sağda ortalı.", SC)
    s = 4.5
    squares = [A.rect(X0 + i * s, 77.0 + j * s, X0 + (i + 1) * s, 77.0 + (j + 1) * s).offset(-0.12, J)
               for i in range(24) for j in range(2) if (i + j) % 2 == 0]
    d.add(None, A.union(*squares), WHITE)
    cx = 24.0
    review(d, -33.0, 44.0, 40.0)
    d.add("ÇALIK", t("outfit", "ÇALIK", 12.0, cx, 63.0, "c", 1.0, 58.0), WHITE)
    d.add("OTO LASTİK", t("outfit", "OTO LASTİK", 5.0, cx, 47.5, "c", 1.6, 58.0), YELLOW)
    d.add(None, bar(cx - 10.0, cx + 10.0, 39.5, 1.4), WHITE)
    d.add("HEMEN ARA", t("outfit", "HEMEN ARA", 4.6, cx, 31.0, "c", 0.9), YELLOW)
    d.add("telefon", t("outfit", PHONE, 5.0, cx, 21.0, "c", 0.3, 58.0), WHITE)
    return d


def c10_sari_blok():
    d = Design("10_sari_blok", "Sarı blok", "Solda sarı blok, içinde oyma yazılar ve telefon; sağda Google yorum QR'ı.",
               SC)
    cx = -31.0
    block = A.rrect(46.0, 75.0, 4.0, cx, 47.5)
    cut = A.union(t("archivo", "ÇALIK", 10.5, cx, 74.0, "c", 0.4, 40.0),
                  t("archivo", "OTO", 6.6, cx, 58.5, "c", 0.6),
                  t("archivo", "LASTİK", 6.6, cx, 48.5, "c", 0.6, 40.0),
                  phone_icon(11.0, cx, 33.5),
                  t("outfit", "HEMEN ARA", 4.2, cx, 22.0, "c", 0.8),
                  t("outfit", PHONE, 4.2, cx, 15.0, "c", 0.0, 41.0))
    d.add("blok yazıları", block - cut, YELLOW)
    review(d, 31.0, 50.0, 42.0)
    return d


DESIGNS = [c1_jant, c2_anahtar, c3_telefon, c4_ikaz, c5_gosterge, c6_araba, c7_lastik_izi, c8_simsek, c9_dama,
           c10_sari_blok]


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


def thin_shapes(d, limit=1.2):
    """Simge ve süslerde `limit` mm'den ince alan (%): yazı olmayan kabartmalar."""
    shapes = [cs for cs, _ in d.raised if not any(cs is v for v in d.lines.values())]
    if not shapes:
        return 0.0
    cs = A.union(*shapes)
    thin = cs - cs.offset(-limit / 2, J).offset(limit / 2, J)
    return round(100 * sum(p.area() for p in thin.decompose() if p.area() > 0.02) / cs.area(), 1)


def crowded(d, gap=2.0):
    """Yazı satırları arasında, satırlarla simgeler / QR arasında `gap` mm'den dar aralık ve kenara taşma."""
    out = I.outline()
    safe = out.offset(-3.0, J) ^ A.rect(-70, 9.5, 70, 100)        # sehpa alt ~7 mm'yi örter
    names = {id(v): k for k, v in d.lines.items()}
    items = [(names.get(id(cs)), cs) for cs, _ in d.raised] + [("QR", cs) for cs, _ in d.inlay]
    found = [f"{n or 'simge'} kenarda" for n, cs in items if (cs - safe).area() > 0.05]
    for k, (n, cs) in enumerate(items):
        for n2, cs2 in items[k + 1:]:
            if (n or n2) and (cs.offset(gap, J) ^ cs2).area() > 0.01:      # simge parçaları kendi aralarında serbest
                found.append(f"{n or 'simge'} ~ {n2 or 'simge'}")
    return found


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


def catalog(ds):
    """Müşteriye: musteri_1.png (1–6), musteri_2.png (7–10), musteri_katalog.pdf."""
    W, H = 1654, 2339
    big = ImageFont.truetype(os.path.join(A.FONT_DIR, "RussoOne-Regular.ttf"), 104)
    mid = ImageFont.truetype(os.path.join(A.FONT_DIR, "RussoOne-Regular.ttf"), 40)
    f = font_ui
    ink, muted, paper, yellow = (20, 20, 22), (96, 98, 106), (245, 245, 243), SHOW[YELLOW]
    pages = []
    for p, group in enumerate([ds[:6], ds[6:]]):
        im = Image.new("RGB", (W, H), paper)
        dr = ImageDraw.Draw(im)
        dr.rectangle((0, 0, W, 250), fill=(16, 16, 18))
        for k, x in enumerate(range(1100, W + 200, 64)):                 # sağ üstte ikaz şeridi
            dr.polygon([(x, 250), (x + 30, 250), (x + 30 - 120, 130), (x - 120, 130)], fill=yellow)
        dr.rectangle((0, 246, W, 254), fill=yellow)
        dr.text((70, 40), "ÇALIK", font=big, fill=(244, 244, 242))
        x = 76 + dr.textlength("ÇALIK", font=big) + 22
        dr.text((x, 72), "OTO LASTİK", font=mid, fill=yellow)
        dr.text((70, 180), "Google yorum QR'lı tezgâh isimliği · tasarım önerileri", font=f(30), fill=(210, 210, 214))
        dr.text((W - 70 - dr.textlength(f"{p + 1}/2", font=f(28)), 40), f"{p + 1}/2", font=f(28), fill=(170, 170, 176))
        y = 285
        for line in ("QR: telefonla okutunca Google'da işletmenin yorum sayfası açılır (beş yıldız, yorum yaz).",
                     "Hepsi siyah zemin, sarı ve beyaz yazı; her birinde farklı simge"):
            dr.text((70, y), line, font=f(27), fill=ink)
            y += 40
        top, gap, cw = 395, 50, (W - 3 * 60) // 2
        ch = (H - top - 190 - 2 * gap) // 3
        for k, d in enumerate(group):
            x0, y0 = 60 + (k % 2) * (cw + 60), top + (k // 2) * (ch + gap)
            dr.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 28, fill=(255, 255, 255), outline=(226, 226, 230))
            n = ds.index(d) + 1
            dr.ellipse((x0 + 26, y0 + 24, x0 + 86, y0 + 84), fill=(16, 16, 18))
            dr.text((x0 + 56 - dr.textlength(str(n), font=f(34)) / 2, y0 + 34), str(n), font=f(34), fill=yellow)
            dr.text((x0 + 104, y0 + 30), d.title, font=f(38), fill=ink)
            img = A.fit_into(render(mesh(d.shown), 1300, rotation(0, -90), flat=0.85, margin=0.02), cw - 70, ch - 190)
            im.paste(img, (x0 + (cw - img.width) // 2, y0 + 100 + (ch - 190 - img.height) // 2), img)
            ty = y0 + ch - 78
            for line in N.wrap(dr, d.desc, f(26), cw - 60)[:2]:
                dr.text((x0 + 30, ty), line, font=f(26), fill=muted)
                ty += 34
        if p == 1:
            y0, y1 = top + 2 * (ch + gap), H - 190
            dr.rounded_rectangle((60, y0, W - 60, y1), 28, fill=(255, 255, 255), outline=(226, 226, 230))
            dr.text((100, y0 + 40), "Ürün", font=f(38), fill=ink)
            ty = y0 + 110
            for line in ("Ölçü 12 × 9 cm, gövde 1 cm kalınlığında, köşeler yuvarlak",
                         "Yazılar ve simgeler 2 mm kabartma; Google yorum QR'ı düz ve keskin",
                         "Tezgâh sehpası dahil, panel 15° eğik durur",
                         f"Telefon: {PHONE}"):
                dr.ellipse((100, ty + 10, 114, ty + 24), fill=(16, 16, 18))
                dr.text((130, ty), line, font=f(30), fill=muted)
                ty += 56
            img = A.fit_into(render(mesh(ds[0].shown), 1200, rotation(-28, -68), margin=0.02), 520, y1 - y0 - 60)
            im.paste(img, (W - 100 - img.width, y0 + (y1 - y0 - img.height) // 2), img)
        foot = ("Beğendiğiniz tasarımın numarasını yazmanız yeterli." if p == 1 else
                "Ölçü 12 × 9 cm · 1 cm kalın · kabartma yazı ve simge · tezgâh sehpası dahil")
        dr.rounded_rectangle((60, H - 150, W - 60, H - 70), 22, fill=(16, 16, 18))
        dr.text((W / 2 - dr.textlength(foot, font=f(30)) / 2, H - 128), foot, font=f(30), fill=yellow)
        im.save(os.path.join(OUT_DIR, f"musteri_{p + 1}.png"), optimize=True)
        pages.append(im)
    pages[0].save(os.path.join(OUT_DIR, "musteri_katalog.pdf"), save_all=True, append_images=pages[1:],
                  resolution=200)


def main():
    if SAMPLE_LINK:
        print("Not: Google bağlantısı şimdilik arama sayfası; işletmenin yorum bağlantısı bilgiler.json → google")
    only = sys.argv[1:]
    if only == ["katalog"]:
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
        print(f"{d.key:16s} QR {d.qr}  simgelerde 1,2 mm'den ince %{thin_shapes(d)}  dar/ince satırlar: {bad or 'yok'}"
              f"  sıkışık: {crowded(d) or 'yok'}")
    if not only:
        catalog(ds)


if __name__ == "__main__":
    main()
