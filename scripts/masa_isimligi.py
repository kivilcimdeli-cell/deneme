"""FIRAT TUYGUN masa isimliği tasarımları (Türk bayraklı): önden görünüş + 3B maket önizlemeleri.

Bu aşama tasarım seçimi içindir; seçilen tasarım daha sonra baskıya hazır Bambu Lab
3MF dosyasına çevrilecek. Geometri yine de gerçek ölçülerle (mm) ve baskıya uygun
kalınlıklarla kurulur, böylece 3B'ye çevirmek kolay olur.

Türk bayrağı resmi oranlarla çizilir (yükseklik G, boy 1,5 G; ay dış dairesi 0,5 G,
iç dairesi 0,4 G ve 1/16 G kaydırılmış; yıldız 1/4 G çaplı çembere oturur, bir ucu hilale bakar).

Çıktı : masa_isimligi/onizleme/<tasarım>.png, masa_isimligi/tasarimlar.png

Kullanım:
  pip install numpy manifold3d pillow shapely scipy fonttools uharfbuzz
  python3 scripts/masa_isimligi.py
"""
import os
import sys

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anahtarlik import FONT_DIR, circle, fit_into, font, polygon, rect, rrect  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "masa_isimligi")

NAME = "FIRAT TUYGUN"
RED, WHITE, BLACK, STEEL = (222, 22, 34), (246, 246, 242), (36, 36, 39), (170, 172, 178)
RAISE = 0.8          # ön yüz kabartması (mm)


# ---------------------------------------------------------------- Türk bayrağı

def star(cx, cy, R, first_deg=180.0):
    """Düzgün beş köşeli yıldız; ilk uç `first_deg` yönünde."""
    pts = []
    for i in range(10):
        a = np.radians(first_deg + i * 36.0)
        r = R if i % 2 == 0 else R * 0.381966
        pts.append((cx + r * np.cos(a), cy + r * np.sin(a)))
    return polygon(pts)


def flag(h, x0=0.0, y0=0.0):
    """Resmi oranlarla Türk bayrağı; sol alt köşe (x0, y0), yükseklik h.
    Döner: (kırmızı zemin, beyaz ay-yıldız)."""
    k = h / 800.0
    field = rect(0, 0, 1200, 800)
    crescent = circle(200, 425, 400, 256) - circle(160, 475, 400, 256)
    moon_star = crescent + star(683.334, 400, 100)
    t = lambda cs: cs.scale((k, k)).translate((x0, y0))  # noqa: E731
    return t(field), t(moon_star)


def dense_rect(x0, y0, x1, y1, n=200):
    """Kenarları sık noktalı dikdörtgen (dalga bükmesi için)."""
    xs = np.linspace(x0, x1, n)
    ys = np.linspace(y0, y1, max(8, n // 3))
    pts = ([(x, y0) for x in xs] + [(x1, y) for y in ys[1:]] + [(x, y1) for x in xs[::-1][1:]]
           + [(x0, y) for y in ys[::-1][1:-1]])
    return polygon(pts)


# ---------------------------------------------------------------- 3B yardımcılar

def on_face(cs, M, h=RAISE):
    """2B şekli kabartıp bir yüzeye yerleştirir. M: (u, v, w) -> dünya için 3x4 matris."""
    return cs.extrude(h).transform(M)


def front_face(y0):
    """Ön yüz y = y0 düzleminde, -y yönüne bakar: u -> x, v -> z, w -> -y."""
    return [[1, 0, 0, 0], [0, 0, -1, y0], [0, 1, 0, 0]]


def upright(cs, depth, y0=0.0):
    """2B şekli (x, z düzleminde) ayağa kaldırıp y yönünde `depth` kalınlık verir (önü y0'da)."""
    return cs.extrude(depth).transform([[1, 0, 0, 0], [0, 0, 1, y0], [0, 1, 0, 0]])


def box(x0, y0, z0, x1, y1, z1, r=0.0):
    base = rrect(x1 - x0, y1 - y0, r, (x0 + x1) / 2, (y0 + y1) / 2) if r else rect(x0, y0, x1, y1)
    return base.extrude(z1 - z0).translate((0, 0, z0))


class Concept:
    def __init__(self, key, title, desc, size):
        self.key, self.title, self.desc, self.size = key, title, desc, size
        self.parts = []            # [(Manifold, renk)]

    def add(self, man, colour):
        self.parts.append((man, colour))
        return self


# ---------------------------------------------------------------- tasarımlar

def t1_kama():
    """Klasik kama masa isimliği: eğik ön yüzde solda bayrak, sağda isim."""
    W, L, ang = 220.0, 54.0, 62.0                      # genişlik, ön yüz eğik boyu, eğim
    a = np.radians(ang)
    top = (L * np.cos(a), L * np.sin(a))
    depth = 2 * L * np.cos(a) + 8
    prof = polygon([(0, 0), top, (depth, 0)])          # (y, z) kesiti
    body = prof.extrude(W).transform([[0, 0, 1, -W / 2], [1, 0, 0, 0], [0, 1, 0, 0]])
    c = Concept("1_kama", "Kama isimlik", "Klasik üçgen masa isimliği; eğik ön yüzde bayrak ve isim.",
                f"{W:.0f} × {depth:.0f} × {top[1]:.0f} mm")
    c.add(body, BLACK)
    d = np.array([0, np.cos(a), np.sin(a)])            # yüz boyunca yukarı
    n = np.array([0, -np.sin(a), np.cos(a)])           # yüz normali (dışa)
    M = [[1, 0, 0, 0], [0, d[1], n[1], 0], [0, d[2], n[2], 0]]
    fh = 34.0
    field, ms = flag(fh, -W / 2 + 9.0, (L - fh) / 2)
    field = rrect(fh * 1.5, fh, 2.5, -W / 2 + 9.0 + fh * 0.75, L / 2) ^ field
    name = font("bebas").text(NAME, font("bebas").fit_cap(NAME, 23.0, W - fh * 1.5 - 30.0),
                              (-W / 2 + 9.0 + fh * 1.5 + W / 2 - 8.0) / 2, L / 2 + 1.5)
    line = rect(-W / 2 + 9.0 + fh * 1.5 + 8.0, L / 2 - 15.5, W / 2 - 9.0, L / 2 - 14.3)
    c.add(on_face(field - ms, M), RED).add(on_face(ms, M), WHITE)
    c.add(on_face(name, M), WHITE).add(on_face(line, M), RED)
    return c


def t2_dalgalanan():
    """Kaide üstünde gerçekten kıvrımlı (dalgalı) duran bayrak + direk; kaidenin önünde isim."""
    BW, BD, BH = 190.0, 46.0, 24.0
    c = Concept("2_dalgalanan_bayrak", "Dalgalanan bayrak",
                "Kaide üstünde kıvrımlı duran bayrak ve direk; kaidenin önünde isim.", f"{BW:.0f} × {BD:.0f} × 130 mm")
    c.add(box(-BW / 2, 0, 0, BW / 2, BD, BH, r=4.0), BLACK)
    name = font("bebas").text(NAME, font("bebas").fit_cap(NAME, 14.0, BW - 20.0), 0, BH / 2)
    c.add(on_face(name, front_face(0.0)), WHITE)
    # dalgalı bayrak: üstten bakışta dalgalı şerit, 4 mm kalın, 72 mm yüksek
    fh, fw, th = 72.0, 108.0, 4.0
    x0 = -BW / 2 + 32.0
    xs = np.linspace(0, fw, 160)
    wave = lambda x: 5.0 * np.sin(2 * np.pi * x / 72.0) * (x / fw) ** 0.8  # noqa: E731
    yc = BD / 2
    front = [(x0 + x, yc - th / 2 + wave(x)) for x in xs]
    back = [(x0 + x, yc + th / 2 + wave(x)) for x in xs[::-1]]
    panel2d = polygon(front + back)
    z0 = BH + 34.0
    panel = panel2d.extrude(fh).translate((0, 0, z0))
    field, ms = flag(fh, x0, z0)
    # ay-yıldız: önden (x, z) çizilip y boyunca uzatılır, bayrağın ön yüzündeki ince kabukla kesilir
    shell = (panel2d.offset(RAISE, m3.JoinType.Round) - panel2d).extrude(fh).translate((0, 0, z0))
    shell = shell ^ box(-500, -500, z0, 500, yc, z0 + fh)          # yalnızca ön yüz
    ms3 = upright(ms, 200.0, -100.0) ^ shell
    pole = m3.Manifold.cylinder(z0 + fh + 6 - BH, 2.6, 2.6, 48).translate((x0 - 2.6, yc, BH))
    knob = m3.Manifold.sphere(4.0, 48).translate((x0 - 2.6, yc, z0 + fh + 8))
    c.add(panel, RED).add(ms3, WHITE).add(pole, STEEL).add(knob, STEEL)
    return c


def t3_ay_yildiz():
    """Kaide üstünde ayakta duran büyük ay ve yıldız; kaidenin önünde isim."""
    BW, BD, BH = 170.0, 40.0, 20.0
    c = Concept("3_ay_yildiz_heykel", "Ay yıldız heykel",
                "Kaide üstünde ayakta duran kırmızı ay ve yıldız; kaidenin önünde beyaz isim.", f"{BW:.0f} × {BD:.0f} × 125 mm")
    c.add(box(-BW / 2, 0, 0, BW / 2, BD, BH, r=4.0), BLACK)
    name = font("bebas").text(NAME, font("bebas").fit_cap(NAME, 13.0, BW - 20.0), 0, BH / 2)
    c.add(on_face(name, front_face(0.0)), WHITE)
    k = 200.0 / 800.0                                  # 200 mm'lik bayrağın ay-yıldızı
    crescent = circle(200 * k, 425 * k, 400 * k, 256) - circle(160 * k, 475 * k, 400 * k, 256)
    st = star(683.334 * k, 400 * k, 100 * k)
    x0, y0, x1, y1 = (crescent + st).bounds()
    dx, dy = -(x0 + x1) / 2, BH - y0 - 2.0             # ay kaideye 2 mm gömülü otursun
    crescent, st = crescent.translate((dx, dy)), st.translate((dx, dy))
    sx0, sy0, sx1, sy1 = st.bounds()
    rod_h = (sy0 + sy1) / 2 - BH                       # yıldızı taşıyan ince çelik çubuk
    rod = m3.Manifold.cylinder(rod_h, 1.6, 1.6, 40).translate(((sx0 + sx1) / 2, BD / 2, BH))
    c.add(upright(crescent, 10.0, BD / 2 - 5.0), RED).add(upright(st, 10.0, BD / 2 - 5.0), RED).add(rod, STEEL)
    return c


def t4_ayakta_harfler():
    """Ayakta duran büyük harfler; sağ uçta direkli küçük bayrak; ince kaide."""
    BW, BD, BH = 236.0, 34.0, 5.0
    c = Concept("4_ayakta_harfler", "Ayakta harfler",
                "İnce kaide üstünde ayakta duran büyük beyaz harfler ve direkli küçük bayrak.", f"{BW:.0f} × {BD:.0f} × 75 mm")
    c.add(box(-BW / 2, 0, 0, BW / 2, BD, BH, r=6.0), BLACK)
    f = font("plate")
    cap = f.fit_cap(NAME, 34.0, BW - 52.0, tracking=1.0)
    letters = f.text(NAME, cap, -BW / 2 + 8.0, BH + cap / 2, align="l", tracking=1.0)
    c.add(upright(letters, 6.0, BD / 2 - 7.0), WHITE)
    lx1 = letters.bounds()[2]
    px = lx1 + 12.0
    fh = 22.0
    pole = m3.Manifold.cylinder(66.0, 1.8, 1.8, 40).translate((px, BD / 2, BH))
    field, ms = flag(fh, px + 1.8, BH + 66.0 - fh - 2.0)
    c.add(pole, STEEL)
    c.add(upright(field - ms, 2.4, BD / 2 - 1.2), RED).add(upright(ms, RAISE, BD / 2 - 1.2 - RAISE), WHITE)
    return c


def t5_capraz_blok():
    """Çapraz kesimle ikiye bölünmüş modern blok: solda bayrak, sağda geniş aralıklı isim."""
    W, H, D = 210.0, 56.0, 32.0
    c = Concept("5_capraz_blok", "Çapraz blok",
                "Çapraz kesimle bölünmüş iki renkli blok; solda bayrak, sağda geniş harf aralıklı isim.",
                f"{W:.0f} × {D:.0f} × {H:.0f} mm")
    split_top, split_bot = -W / 2 + 92.0, -W / 2 + 70.0
    left2d = polygon([(-W / 2, 0), (split_bot, 0), (split_top, H), (-W / 2, H)])
    gap2d = polygon([(split_bot, 0), (split_bot + 2.4, 0), (split_top + 2.4, H), (split_top, H)])
    right2d = polygon([(split_bot + 2.4, 0), (W / 2, 0), (W / 2, H), (split_top + 2.4, H)])
    rounded = rrect(W, H, 5.0, 0, H / 2)
    left = upright(left2d ^ rounded, D, 0.0)
    right = upright(right2d ^ rounded, D, 0.0)
    c.add(upright(gap2d ^ rounded, D, 0.0), WHITE)       # iki rengi ayıran beyaz ince ayraç
    fh = 34.0
    field, ms = flag(fh, -W / 2 + 12.0, (H - fh) / 2)
    c.add(left, RED).add(right, BLACK)
    c.add(on_face(ms, front_face(0.0)), WHITE)
    f = font("small")
    x0 = split_top + 10.0
    cap = f.fit_cap(NAME, 12.0, W / 2 - 10.0 - x0, tracking=2.2)
    c.add(on_face(f.text(NAME, cap, (x0 + W / 2 - 10.0) / 2, H / 2 + 3.0, tracking=2.2), front_face(0.0)), WHITE)
    c.add(on_face(rect(x0 + 6.0, H / 2 - 9.4, W / 2 - 16.0, H / 2 - 8.2), front_face(0.0)), RED)
    return c


CONCEPTS = [t1_kama, t2_dalgalanan, t3_ay_yildiz, t4_ayakta_harfler, t5_capraz_blok]


# ---------------------------------------------------------------- önizleme

def mesh(man):
    m = man.to_mesh()
    return np.asarray(m.vert_properties)[:, :3].astype(float), np.asarray(m.tri_verts).astype(int)


def draw(c, path):
    parts = [(*mesh(m), col) for m, col in c.parts]
    front = fit_into(render(parts, 1100, rotation(0, -90), margin=0.02), 600, 360)
    iso = fit_into(render(parts, 1100, rotation(-26, -70), margin=0.02), 600, 360)
    W, H = 1340, 520
    canvas = Image.new("RGB", (W, H), (236, 239, 244))
    dr = ImageDraw.Draw(canvas)
    for i, (im, label) in enumerate(((front, "Önden"), (iso, "Maket (3/4 açı)"))):
        x = 30 + i * 655
        dr.rounded_rectangle((x, 90, x + 625, 90 + 400), 22, fill=(146, 153, 166))
        canvas.paste(im, (x + (625 - im.width) // 2, 90 + (400 - im.height) // 2), im)
        dr.text((x + 16, 98), label, fill=(236, 239, 244), font=ImageFont.truetype(os.path.join(FONT_DIR, "Lexend-ExtraBold.ttf"), 18))
    f = ImageFont.truetype(os.path.join(FONT_DIR, "Lexend-ExtraBold.ttf"), 30)
    fs = ImageFont.truetype(os.path.join(FONT_DIR, "Lexend-ExtraBold.ttf"), 19)
    dr.text((30, 16), c.title.upper(), fill=(30, 33, 40), font=f)
    dr.text((30, 56), c.desc, fill=(80, 86, 98), font=fs)
    dr.text((W - 30 - dr.textlength(c.size, font=fs), 24), c.size, fill=(80, 86, 98), font=fs)
    canvas.save(path)
    return canvas


def main():
    os.makedirs(os.path.join(OUT_DIR, "onizleme"), exist_ok=True)
    only = sys.argv[1:]
    sheets = []
    for fn in CONCEPTS:
        c = fn()
        if only and not any(o in c.key for o in only):
            continue
        sheets.append(draw(c, os.path.join(OUT_DIR, "onizleme", c.key + ".png")))
        print(c.key, c.size)
    if not only:
        W = sheets[0].width
        sheet = Image.new("RGB", (W, sum(s.height for s in sheets) + 16 * (len(sheets) - 1)), (250, 250, 252))
        y = 0
        for s in sheets:
            sheet.paste(s, (0, y))
            y += s.height + 16
        sheet.save(os.path.join(OUT_DIR, "tasarimlar.png"))


if __name__ == "__main__":
    main()
