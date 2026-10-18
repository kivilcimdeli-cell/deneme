"""FIRAT TUYGUN masa isimliği – ikinci tur tasarım önerileri: daha şık, daha büyük yazı, daha az filament.

Çapraz blok (240 × 56 × 32 mm, dolu) ~129 g filament harcıyor. Buradaki öneriler ince panel, içi boş
gövde ya da ayakta harf kullanır. Paneller ön yüzü tablaya gelecek şekilde basılır: yazı ve bayrak ilk
katmanlarda yüzeye gömülü renkli dolgu (0,8 mm) olur; tabla yüzeyinde basıldığı için en keskin yüz ve renk
değişimi yalnız ilk 4 katmanda (temizleme atığı az).

Filament tahmini çapraz blokla aynı yöntemle (2 duvar, üst 5 / alt 3 katman, %15 dolgu, PLA).

Çıktı : masa_isimligi/yeni/*.png, masa_isimligi/yeni/hepsi.png

Kullanım:
  python3 scripts/masa_isimligi_yeni.py [anahtar ...]
"""
import json
import os
import sys

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
from anahtarlik import FONT_DIR, fit_into, font, polygon, rect, rrect  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402
from masa_isimligi import BLACK, RED, WHITE, Concept, flag, on_face, front_face, upright  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "masa_isimligi", "yeni")
NAME = "FIRAT TUYGUN"
GOLD = (196, 160, 82)
A.FONT_FILES.setdefault("encode", "EncodeSansCondensed-Black.ttf")

CAPRAZ_BLOK_G = 129.0            # mevcut çapraz blok (siyah 85 + kırmızı 40 + beyaz 4 g)
INLAY = 0.8                      # yüzeye gömülü renk derinliği (4 katman; beyaz siyahın üstünde opak)
T = 2.6                          # panel kalınlığı (13 katman)
TILT = 12.0                      # panel arkaya eğimi (derece)


def grams(man, infill=0.15):
    """Çapraz blokla aynı kaba tahmin: 2 duvar (0,84 mm), dış yüzey kabuğu, içi %15 dolgu, PLA 1,24 g/cm³."""
    vol = man.volume()
    shell = man.surface_area() * 0.84
    return (min(vol, shell) + infill * max(0.0, vol - shell)) * 1.24 / 1000.0


def tilted(man, deg, z0=0.0, y0=0.0):
    """Ön yüzü y = 0'da duran parçayı alt kenarı etrafında arkaya yatırır (üst kenar +y'ye gider)."""
    a = np.radians(deg)
    c, s = np.cos(a), np.sin(a)
    return man.transform([[1, 0, 0, 0], [0, c, s, y0], [0, -s, c, z0]])


def inlaid_panel(outline, regions, base_col, thickness=T):
    """Ön yüzüne renkli bölgeler gömülü panel (u, v düzleminde; ön yüz y = 0). Döner: [(Manifold, renk)]."""
    parts, taken = [], A.empty()
    for cs, col in reversed(regions):                    # sonraki öğe öncekinin üstüne yazar
        part = (cs ^ outline) - taken
        taken = taken + part
        if not part.is_empty():
            parts.append((upright(part, INLAY, 0.0), col))
    body = upright(outline, thickness, 0.0) - upright(taken, INLAY + 0.01, -0.01)
    return [(body, base_col)] + parts[::-1]


def foot(x, depth=34.0, width=18.0, height=10.0):
    """Paneli eğik tutan küçük ayak (y-z profili, x'te `width`)."""
    prof = polygon([(-7.0, 0.0), (depth - 7.0, 0.0), (depth - 7.0, 3.0), (depth - 17.0, height),
                    (-3.0, height), (-7.0, height - 4.0)])
    return prof.extrude(width).transform([[0, 0, 1, x - width / 2], [1, 0, 0, 0], [0, 1, 0, 0]])


def panel_on_feet(c, outline, regions, base_col, feet_x, foot_col=BLACK):
    """Paneli 3 mm yukarıda, ayakların yuvasında, arkaya `TILT` derece eğik yerleştirir; ayaklarda yuva açılır."""
    z0, y0 = 3.0, 2.0
    flat = inlaid_panel(outline, regions, base_col)
    face_down = [[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0]]          # baskı yönü: ön yüz tablada
    c.print_parts = [(m.transform(face_down), col) for m, col in flat]
    c.print_parts += [(foot(0.0).translate((fx, -40.0, 0)), foot_col) for fx in (-30.0, 30.0)]
    parts = [(tilted(m, TILT, z0, y0), col) for m, col in flat]
    slot = tilted(upright(outline, T + 0.3, -0.15), TILT, z0, y0)
    for fx in feet_x:
        c.add(foot(fx) - slot, foot_col)
    for m, col in parts:
        c.add(m, col)
    c.grams = sum(grams(m) for m, _ in c.parts)
    return c


def name_shape(fnt, cap, max_w, x, y, tracking=0.0):
    f = font(fnt)
    cap = f.fit_cap(NAME, cap, max_w, tracking)
    return f.text(NAME, cap, x, y, tracking=tracking), cap


# ---------------------------------------------------------------- tasarımlar

def y1_ince_capraz():
    """Seçilen çapraz bloğun görünüşü; derinlik 32 -> 18 mm, yazı 21 -> 30 mm."""
    W, H, D = 240.0, 60.0, 18.0
    c = Concept("1_ince_capraz_blok", "İnce çapraz blok",
                "Beğenilen çapraz blok; derinlik 32 yerine 18 mm, kırmızı bölüm daraldı, isim büyüdü. %5 dolgu, tek parça.",
                f"{W:.0f} × {D:.0f} × {H:.0f} mm")
    sb, st = -W / 2 + 44.0, -W / 2 + 62.0
    rounded = rrect(W, H, 6.0, 0, H / 2)
    left = polygon([(-W, 0), (sb, 0), (st, H), (-W, H)]) ^ rounded
    gap = polygon([(sb, 0), (sb + 2.4, 0), (st + 2.4, H), (st, H)]) ^ rounded
    right = rounded - left - gap
    c.add(upright(left, D), RED).add(upright(right, D), BLACK).add(upright(gap, D), WHITE)
    _, ms = flag(40.0)
    x0, y0, x1, y1 = ms.bounds()
    ms = ms.translate(((-W / 2 + (sb + st) / 2) / 2 - (x0 + x1) / 2 + 1.0, H / 2 - (y0 + y1) / 2))
    nx0, nx1 = st + 2.4 + 9.0, W / 2 - 9.0
    nm, cap = name_shape("bebas", 34.0, nx1 - nx0, (nx0 + nx1) / 2, H / 2 + 4.0, tracking=0.6)
    bx0, by0, bx1, _ = nm.bounds()
    line = rect(bx0, by0 - 6.0, bx1, by0 - 4.4)
    for cs, col in ((ms, WHITE), (nm, WHITE), (line, RED)):
        c.add(on_face(cs, front_face(0.0), 1.2), col)
    c.grams = sum(grams(m, 0.05) for m, _ in c.parts)
    c.infill = 0.05                                      # dekoratif blok: %5 dolgu yeter
    c.print_parts = [(m.transform([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, D]]), col) for m, col in c.parts]
    c.cap = cap
    return c


def y2_capraz_panel():
    """Çapraz blok çizgisi, 3 mm ince panelde; iki küçük ayak."""
    W, H = 240.0, 74.0
    c = Concept("2_capraz_panel", "Çapraz panel",
                "Çapraz bloğun aynı deseni 2,6 mm panelde; renkler yüzeye gömülü, 12° eğik, iki küçük ayak.",
                f"{W:.0f} × 74 mm panel, 41 mm derinlik")
    outline = rrect(W, H, 6.0, 0, H / 2)
    sb, st = -W / 2 + 46.0, -W / 2 + 66.0
    left = polygon([(-W, -1), (sb, -1), (st, H + 1), (-W, H + 1)])
    gap = polygon([(sb, -1), (sb + 2.6, -1), (st + 2.6, H + 1), (st, H + 1)])
    _, ms = flag(46.0)
    x0, y0, x1, y1 = ms.bounds()
    ms = ms.translate(((-W / 2 + (sb + st) / 2) / 2 - (x0 + x1) / 2 + 1.0, H / 2 - (y0 + y1) / 2))
    nx0, nx1 = st + 2.6 + 9.0, W / 2 - 9.0
    nm, cap = name_shape("bebas", 38.0, nx1 - nx0, (nx0 + nx1) / 2, H / 2 + 5.0, tracking=0.6)
    bx0, by0, bx1, _ = nm.bounds()
    regions = [(left, RED), (gap, WHITE), (ms, WHITE), (nm, WHITE), (rect(bx0, by0 - 7.0, bx1, by0 - 5.2), RED)]
    c.cap = cap
    return panel_on_feet(c, outline, regions, BLACK, (-W / 2 + 40.0, W / 2 - 40.0))


def y3_altin():
    """Siyah panel: üstte amblem gibi küçük bayrak ve boydan ince altın çizgi, altında boydan büyük altın isim."""
    W, H = 240.0, 78.0
    c = Concept("3_siyah_altin_panel", "Siyah – altın panel",
                "Siyah panel; üstte küçük bayrak ve ince altın çizgi, altında boydan büyük altın (silk) isim. Kurumsal.",
                f"{W:.0f} × 78 mm panel, 41 mm derinlik")
    outline = rrect(W, H, 5.0, 0, H / 2)
    fh, m = 16.0, 12.0
    field, ms = flag(fh, -W / 2 + m, H - m - fh)
    line = rect(-W / 2 + m + fh * 1.5 + 6.0, H - m - fh / 2 - 0.6, W / 2 - m, H - m - fh / 2 + 0.6)
    nm, cap = name_shape("bebas", 40.0, W - 2 * m, 0.0, (H - m - fh) / 2 + 1.0, tracking=1.4)
    regions = [(field, RED), (ms, WHITE), (line, GOLD), (nm, GOLD)]
    c.cap = cap
    return panel_on_feet(c, outline, regions, BLACK, (-W / 2 + 40.0, W / 2 - 40.0))


def y4_beyaz():
    """Beyaz panel, iki satır kalın siyah isim (en okunaklı: koyu yazı açık zemin), solda kırmızı bayrak şeridi."""
    W, H = 240.0, 84.0
    c = Concept("4_beyaz_panel", "Beyaz panel – iki satır",
                "Beyaz zeminde iki satır kalın siyah isim (en okunaklı), solda boydan kırmızı bayrak şeridi.",
                f"{W:.0f} × 84 mm panel, 41 mm derinlik")
    outline = rrect(W, H, 5.0, 0, H / 2)
    band_w = 64.0
    band = rect(-W, -1, -W / 2 + band_w, H + 1)
    _, ms = flag(50.0)
    x0, y0, x1, y1 = ms.bounds()
    ms = ms.translate((-W / 2 + band_w / 2 - (x0 + x1) / 2 + 2.0, H / 2 - (y0 + y1) / 2))
    f = font("plate")
    nx0 = -W / 2 + band_w + 14.0
    cap = f.fit_cap("TUYGUN", 30.0, W / 2 - 12.0 - nx0, 0.8)
    l1 = f.text("FIRAT", cap, nx0, H / 2 + cap / 2 + 5.0, align="l", tracking=0.8)
    l2 = f.text("TUYGUN", cap, nx0, H / 2 - cap / 2 + 1.0, align="l", tracking=0.8)
    regions = [(band, RED), (ms, WHITE), (l1, BLACK), (l2, BLACK)]
    c.cap = cap
    return panel_on_feet(c, outline, regions, WHITE, (-W / 2 + 34.0, W / 2 - 26.0))


def y5_cadir():
    """İçi boş üçgen (çadır) isimlik: eşkenar kesit, 1,2 mm duvar, ayak gerekmez."""
    L, S, t = 240.0, 62.0, 1.2
    h = S * np.sqrt(3) / 2
    c = Concept("5_ucgen_cadir", "Üçgen çadır (içi boş)",
                "İçi boş üçgen gövde, 1,2 mm duvar; ön yüz 30° eğik, ayak gerekmez. Ön yüz tablada basılır.",
                f"{L:.0f} × {S:.0f} × {h:.0f} mm")
    outer = polygon([(0, 0), (S, 0), (S / 2, h)])
    inner = outer.offset(-t, m3.JoinType.Miter)           # iç üçgen: her kenardan t içeride
    shell2d = outer - inner
    cap_t = 1.6
    prism = (shell2d.extrude(L - 2 * cap_t).translate((0, 0, cap_t)) + outer.extrude(cap_t)
             + outer.extrude(cap_t).translate((0, 0, L - cap_t)))
    # kesit (y, z), uzunluk x
    prism = prism.transform([[0, 0, 1, -L / 2], [1, 0, 0, 0], [0, 1, 0, 0]])
    # ön yüz: (0,0) -> (S/2, h); u = x, v = eğik yüz boyunca, w = içe
    M = [[1, 0, 0, 0], [0, 0.5, np.sqrt(3) / 2, 0], [0, np.sqrt(3) / 2, -0.5, 0]]
    fh = 24.0
    field, ms = flag(fh, -L / 2 + 12.0, S / 2 - fh / 2)
    nx0, nx1 = -L / 2 + 12.0 + fh * 1.5 + 10.0, L / 2 - 12.0
    nm, cap = name_shape("bebas", 34.0, nx1 - nx0, (nx0 + nx1) / 2, S / 2, tracking=0.6)
    regions = [(field, RED), (ms, WHITE), (nm, WHITE)]
    taken = A.empty()
    inl = []
    for cs, col in reversed(regions):
        part = cs - taken
        taken = taken + part
        inl.append((part.extrude(INLAY).transform(M), col))
    body = prism - taken.extrude(INLAY + 0.01).translate((0, 0, -0.01)).transform(M)
    c.add(body, BLACK)
    for m, col in inl[::-1]:
        c.add(m, col)
    c.grams = sum(grams(m) for m, _ in c.parts)
    rx = np.radians(120.0)                               # ön yüz normali (0, -0,87, 0,5) -> (0, 0, -1)
    R = [[1, 0, 0, 0], [0, np.cos(rx), -np.sin(rx), 0], [0, np.sin(rx), np.cos(rx), 0]]
    c.print_parts = [(m.transform(R), col) for m, col in c.parts]
    c.cap = cap
    return c


def y6_ayakta_harfler():
    """İnce kaide üstünde ayakta duran kalın harfler; solda küçük bayrak levhası."""
    W, BD, BH = 240.0, 22.0, 5.0
    c = Concept("6_ayakta_harfler", "Ayakta harfler",
                "İnce siyah kaide üstünde ayakta beyaz harfler, solda küçük bayrak levhası. En az filament.",
                f"{W:.0f} × {BD:.0f} × 45 mm")
    c.add(rrect(W, BD, 5.0, 0, BD / 2).extrude(BH), BLACK)
    fh = 22.0
    fx0 = -W / 2 + 6.0
    field, ms = flag(fh, fx0, 0.0)
    c.add(upright(field - ms, 3.0, BD / 2 - 1.5).translate((0, 0, BH)), RED)
    c.add(upright(ms, 3.0, BD / 2 - 1.5).translate((0, 0, BH)), WHITE)
    lx0 = fx0 + fh * 1.5 + 6.0
    f = font("bebas")
    cap = f.fit_cap(NAME, 40.0, W / 2 - 5.0 - lx0, 1.0)
    letters = f.text(NAME, cap, lx0, cap / 2, align="l", tracking=1.0)
    c.add(upright(letters, 6.0, BD / 2 - 3.0).translate((0, 0, BH)), WHITE)
    c.grams = sum(grams(m) for m, _ in c.parts)
    c.print_parts = list(c.parts)
    c.cap = cap
    c.size = f"{W:.0f} × {BD:.0f} × {BH + cap:.0f} mm"
    return c


MEASURED = os.path.join(OUT_DIR, "olcum.json")   # PrusaSlicer'da baskı yönünde dilimlenen gram ve süre


CONCEPTS = [y1_ince_capraz, y2_capraz_panel, y3_altin, y4_beyaz, y5_cadir, y6_ayakta_harfler]


# ---------------------------------------------------------------- önizleme

def draw(c, path):
    parts = [(*A.mesh_arrays(m), col) for m, col in c.parts]
    front = fit_into(render(parts, 1100, rotation(0, -90), margin=0.02), 600, 330)
    iso = fit_into(render(parts, 1100, rotation(-28, -68), margin=0.02), 600, 330)
    W, H = 1340, 540
    canvas = Image.new("RGB", (W, H), (236, 239, 244))
    dr = ImageDraw.Draw(canvas)
    lab = ImageFont.truetype(os.path.join(FONT_DIR, "Lexend-ExtraBold.ttf"), 18)
    for i, (im, label) in enumerate(((front, "Önden"), (iso, "Maket (3/4 açı)"))):
        x = 30 + i * 655
        dr.rounded_rectangle((x, 120, x + 625, 120 + 390), 22, fill=(146, 153, 166))
        canvas.paste(im, (x + (625 - im.width) // 2, 120 + (390 - im.height) // 2), im)
        dr.text((x + 16, 128), label, fill=(236, 239, 244), font=lab)
    f = ImageFont.truetype(os.path.join(FONT_DIR, "Lexend-ExtraBold.ttf"), 30)
    fs = ImageFont.truetype(os.path.join(FONT_DIR, "Lexend-ExtraBold.ttf"), 19)
    dr.text((30, 14), c.title.replace("i", "İ").upper(), fill=(30, 33, 40), font=f)
    dr.text((30, 54), c.desc, fill=(80, 86, 98), font=fs)
    g, base, extra = c.grams, CAPRAZ_BLOK_G, ""
    meas = json.load(open(MEASURED)) if os.path.exists(MEASURED) else {}
    if c.key in meas:
        g, base = meas[c.key]["g"], meas["capraz_blok"]["g"]
        extra = f", {meas[c.key]['sure']} (çapraz blok {meas['capraz_blok']['sure']})"
    info = (f"İsim {c.cap:.0f} mm (çapraz blok 21)  ·  {g:.0f} g filament (çapraz blok {base:.0f} g, "
            f"%{100 * (1 - g / base):.0f} az){extra}")
    dr.text((30, 84), info, fill=(22, 120, 60), font=fs)
    dr.text((W - 30 - dr.textlength(c.size, font=fs), 22), c.size, fill=(80, 86, 98), font=fs)
    canvas.save(path)
    return canvas


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    only = sys.argv[1:]
    sheets = []
    for fn in CONCEPTS:
        c = fn()
        if only and not any(o in c.key for o in only):
            continue
        sheets.append(draw(c, os.path.join(OUT_DIR, c.key + ".png")))
        bad = [i for i, (m, _) in enumerate(c.parts) if not str(m.status()).endswith("NoError") or m.volume() <= 0]
        print(f"{c.key:24s} {c.size:32s} isim {c.cap:4.1f} mm  ~{c.grams:5.1f} g  bozuk parça: {bad}")
    if not only:
        W = sheets[0].width
        sheet = Image.new("RGB", (W, sum(s.height for s in sheets) + 16 * (len(sheets) - 1)), (250, 250, 252))
        y = 0
        for s in sheets:
            sheet.paste(s, (0, y))
            y += s.height + 16
        sheet.save(os.path.join(OUT_DIR, "hepsi.png"))


if __name__ == "__main__":
    main()
