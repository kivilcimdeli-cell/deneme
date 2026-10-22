"""GALERİ IŞIK – anahtarlık dışında satılabilecek ürünler: logolu 8 örnek (yalnız görsel, X2D'de basılabilir ölçüde).

Hepsi firmanın logosuyla (scripts/galeri_isik_anahtarlik.py: G işareti, Michroma yazı, elmas İ / Ş), siyah gövde,
turuncu ve beyaz. Ölçüler Bambu Lab X2D tablasına (256 × 256 mm) sığar; gramlar gövde hacminden tahmin.
  1 SATILIK levhası   stoktaki her araca: ön cama / torpidoya, telefon QR'ı (okutunca arar)
  2 Anahtar etiketi   stoktaki araçların anahtarları: büyük numara, plaka yazılacak beyaz alan
  3 Anahtar askılığı  duvara: 6 askı, numaralı etiketlerle takım
  4 Bagaj amblemi     satılan araca: logonun kendisi, çift taraflı bantla yapıştırılır
  5 Çay altlığı       ofiste çay ikramı: ortada G, yaylarda GALERİ / IŞIK
  6 Masa standı       masaya: logo, WhatsApp QR'ı ve telefon
  7 Kartvizitlik      masaya: 45° rampada logo
  8 Duvar logosu      ofis duvarına: 24 cm logo, harfler duvardan 5 mm önde

Çıktı : galeri_isik/urunler/<n>_<ad>.png, galeri_isik/urunler/urunler.png, urunler.pdf

Kullanım:
  python3 scripts/galeri_isik_urunler.py
"""
import math
import os
import sys

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import calik_kartvizitlik as KV  # noqa: E402
import galeri_isik_anahtarlik as G  # noqa: E402
import masa_isimligi_yeni as Y  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "galeri_isik", "urunler")
BLACK, WHITE, ORANGE = G.BLACK, G.WHITE, G.ORANGE
CARD, WALL = (246, 246, 242), (214, 216, 220)
WA_TEXT = "https://wa.me/905468070700"
J = m3.JoinType.Round
LIGHT = KV.LIGHT


# ---------------------------------------------------------------- yardımcılar

def plate(outline, thick, items, body=BLACK, relief=0.6, keep=1.0):
    """Düz levha: gövde + üstünde kabartma öğeler. Döner [(katı, renk)]."""
    inner = outline.offset(-keep, J)
    out = [(outline.extrude(thick), body)]
    for cs, col in G.U.resolve(items):
        s = cs ^ inner
        if not s.is_empty():
            out.append((s.extrude(relief).translate((0, 0, thick)), col))
    return out


def tf(parts, fn):
    return [(fn(m), c) for m, c in parts]


def stand_up(parts, lean=15.0):
    """Yüzü yukarı levhayı ayağa kaldırır: yüz −y'ye bakar, `lean` derece arkaya yaslı, alt kenarı z = 0."""
    out = tf(parts, lambda m: m.rotate((90 - lean, 0, 0)))
    z0 = min(m.bounding_box()[2] for m, _ in out)
    return tf(out, lambda m: m.translate((0, 0, -z0)))


def foot(width, depth=34.0, height=12.0, lean=15.0, y0=None):
    """Levhanın arkasındaki kama ayak (siyah)."""
    t = math.tan(math.radians(lean))
    prof = A.polygon([(0, 0), (depth, 0), (depth, 3.0), (height * t + 6.0, height), (height * t, height)])
    return KV.slab(prof, width).translate((0, y0 or 0.0, 0))


def mesh(parts):
    return [(*A.mesh_arrays(m), c) for m, c in parts]


def grams(parts):
    return sum(Y.grams(m) for m, _ in parts)


def size(parts):
    b = m3.Manifold.batch_boolean([m for m, _ in parts], m3.OpType.Add).bounding_box()
    return b[3] - b[0], b[4] - b[1], b[5] - b[2]


class Product:
    def __init__(self, key, title, who, desc, parts, display=None, view=(-28, -62), dims=None, grams_=None):
        self.key, self.title, self.who, self.desc = key, title, who, desc
        self.parts = parts                              # baskıdaki parçalar (gram ve ölçü)
        self.display = display or parts                 # görselde (askıdaki etiketler, kartlar, duvar)
        self.view = view
        self.dims = dims or size(parts)
        self.g = grams_ if grams_ is not None else grams(parts)


# ---------------------------------------------------------------- ürünler

def u1_satilik():
    W, H = 160.0, 100.0
    outline = A.rrect(W, H, 6.0)
    band = A.rect(-W / 2, H / 2 - 27.0, W / 2, H / 2) ^ outline
    sat, _ = G.word("SATILIK", 13.0, 0, H / 2 - 13.5, align="c", valign="m", tracking=3.0)
    items = [(band - sat.offset(0.2, J), ORANGE)]
    items += G.fit(G.lockup_stack, (-W / 2 + 7, -H / 2 + 22, 12, H / 2 - 34), align="l")[0]
    q, s = G.U.qr(52.0, -6.0, 1.3, data=G.QR_TEXT)
    items += [(q, WHITE), (G.small("TARA · ARA", 4.2, 52.0, -6.0 - s / 2 - 4.6, tracking=0.6), ORANGE)]
    items += [(G.small(G.PHONE, 8.0, -W / 2 + 7 + 46, -H / 2 + 11.0, tracking=0.5, max_w=92), WHITE)]
    panel = plate(outline, 4.0, items)
    shown = stand_up(panel)
    b = m3.Manifold.batch_boolean([m for m, _ in shown], m3.OpType.Add).bounding_box()
    ft = foot(W - 40, y0=b[4] - 26.0)
    return Product("1_satilik", "SATILIK levhası", "Stoktaki her araca",
                   "Ön cama ya da torpidoya; telefon QR'ı okutunca arar. Arkasındaki ayakla kendi durur.",
                   panel + [(ft, BLACK)], shown + [(ft, BLACK)], dims=(W, H, 4.0))


def key_tag(n, cx=0.0, cy=0.0):
    """Numaralı anahtar etiketi (30 × 56): üstte delik ve küçük G, ortada büyük numara, altta plaka için beyaz alan."""
    W, H = 30.0, 56.0
    outline = A.rrect(W, H, 6.0)
    hole = A.circle(3.0, 0, H / 2 - 6.5)
    items = G.place(G.g_mark(8.0), 0.2, H / 2 - 16.6)
    num = G.small(f"{n:02d}", 12.0, 0, -1.0, tracking=0.6, max_w=W - 6)
    items += [(num, WHITE), (A.rrect(W - 6, 9.0, 2.0, 0, -H / 2 + 8.5), WHITE)]
    items += [(G.small("PLAKA", 2.8, 0, -H / 2 + 16.6, tracking=0.8), ORANGE)]
    parts = plate(outline - hole, 3.0, [(cs - hole.offset(0.8, J), c) for cs, c in items])
    return tf(parts, lambda m: m.translate((cx, cy, 0)))


def u2_etiket():
    tags = []
    for i, n in enumerate((1, 2, 3, 4)):
        tags += tf(key_tag(n), lambda m, i=i: m.rotate((0, 0, -6 + 4 * i)).translate((-51 + 34 * i, 4.0 * (i % 2), 0)))
    one = key_tag(7)
    return Product("2_anahtar_etiketi", "Numaralı anahtar etiketi", "Galerinin kendi işi",
                   "Stoktaki araçların anahtarları karışmaz: büyük numara, altta plaka yazılacak beyaz alan "
                   "(kalemle yazılır, silinir).", one, tags, view=(-14, -52), dims=(30, 56, 3.0), grams_=grams(one))


def u3_askilik():
    W, H, T = 220.0, 74.0, 6.0
    outline = A.rrect(W, H, 8.0)
    holes = A.circle(2.4, -W / 2 + 9, H / 2 - 9) + A.circle(2.4, W / 2 - 9, H / 2 - 9)
    items = G.fit(G.lockup_line, (-W / 2 + 20, H / 2 - 24, W / 2 - 20, H / 2 - 5))[0]
    xs = [-W / 2 + 22 + i * (W - 44) / 5 for i in range(6)]
    items += [(G.small(f"{i + 1:02d}", 5.0, x, -H / 2 + 33.0, tracking=0.4), WHITE) for i, x in enumerate(xs)]
    items += [(G.rule(-W / 2 + 14, W / 2 - 14, H / 2 - 28.6), ORANGE)]
    board = plate(outline - holes, T, [(cs - holes.offset(0.8, J), c) for cs, c in items])
    pegs = []
    for x in xs:
        peg = m3.Manifold.cylinder(18.0, 2.2, 2.2, 48).translate((x, -H / 2 + 16.0, T))
        cap = m3.Manifold.cylinder(1.6, 2.8, 2.8, 48).translate((x, -H / 2 + 16.0, T + 18.0))
        pegs += [(peg, BLACK), (cap, ORANGE)]
    parts = board + pegs
    upright = tf(parts, lambda m: m.rotate((90, 0, 0)))
    hang = []
    for i in (0, 2, 3):                                   # 3 askıda numaralı etiket
        tag = tf(key_tag((1, 2, 3, 4)[i % 4]), lambda m: m.rotate((90, 0, 0)))
        hang += tf(tag, lambda m, x=xs[i]: m.translate((x, -T - 5.0, -H / 2 + 16.0 - 0.8 - (28.0 - 6.5))))
    wall = m3.Manifold.cube((W + 24, 2.0, H + 62)).translate((-W / 2 - 12, 0.0, -H / 2 - 50))
    return Product("3_anahtar_askiligi", "Anahtar askılığı", "Galerinin kendi işi",
                   "Duvara iki vidayla; numaralı 6 askı, ucu turuncu başlıklı. Numaralı etiketlerle takım.",
                   parts, upright + hang + [(wall, WALL)], view=(-24, -78), dims=(W, H, T + 20.4))


def u4_amblem():
    items, R = G.fit(G.lockup_line, (-60, -14, 60, 14))
    sil = A.union(*[cs for cs, _ in items]).offset(1.6, J).offset(-0.2, J)
    parts = [(sil.extrude(2.0), BLACK)] + [(cs.extrude(1.4).translate((0, 0, 2.0)), c) for cs, c in items]
    return Product("4_bagaj_amblemi", "Bagaj amblemi", "Satılan her araca",
                   "Logonun kendisi, 12 cm; harfler 1,4 mm kabartma. Arkası düz, çift taraflı 3M bantla bagaja "
                   "yapışır: her satılan araç galerinin reklamı olur.", parts, view=(-18, -48))


def coaster(cx=0.0, cy=0.0, z=0.0):
    R = 45.0
    outline = A.circle(R, 0, 0, 200)
    items = G.place(G.g_mark(26.0), 0.6, 0.6)
    items += G.arc_word("GALERİ", 5.0, 0, 0, 25.6, 90, top=True)
    items += G.arc_word("IŞIK", 5.6, 0, 0, 33.4, -90, top=False, col=ORANGE, mark_col=WHITE, tracking=2.0)
    items += [(G.diamond(-31.0, 0.6, 1.8) + G.diamond(31.0, 0.6, 1.8), ORANGE)]
    rim = (A.circle(R, 0, 0, 200) - A.circle(R - 2.6, 0, 0, 200)).extrude(1.4).translate((0, 0, 3.0))
    parts = plate(outline, 3.0, items, relief=0.6) + [(rim, BLACK)]
    return tf(parts, lambda m: m.translate((cx, cy, z)))


def u5_altlik():
    one = coaster()
    shown = coaster(-30, 6) + coaster(32, -4) + coaster(32, -4, 4.4) + coaster(32, -4, 8.8)
    return Product("5_cay_altligi", "Çay altlığı", "Ofiste ikram",
                   "Ø90 mm, kenarı çerçeveli; ortada G, yaylarda GALERİ / IŞIK. Galeride çay ikramında masada "
                   "logo durur. 4'lü ya da 6'lı set.", one, shown, view=(-20, -50), grams_=grams(one))


def u6_masa():
    W, H = 120.0, 90.0
    outline = A.rrect(W, H, 8.0)
    items = G.fit(G.lockup_stack, (-W / 2 + 7, 4.0, W / 2 - 7, H / 2 - 6))[0]
    import segno
    qd = np.array(segno.make(WA_TEXT, error="m", micro=False).matrix, bool)
    module = 34.0 / (qd.shape[0] + 4)
    q, s = G.U.qr(W / 2 - 24.0, -H / 2 + 23.0, module, data=WA_TEXT)
    items += [(q, WHITE)]
    x0 = -W / 2 + 8.0
    items += [(G.small("WHATSAPP", 5.0, x0, -H / 2 + 33.0, align="l", tracking=0.8), ORANGE),
              (G.small("YAZIN, ARAYIN", 4.2, x0, -H / 2 + 25.0, align="l", tracking=0.5), WHITE),
              (G.small(G.PHONE, 6.0, x0, -H / 2 + 12.0, align="l", tracking=0.3, max_w=60), WHITE)]
    panel = plate(outline, 4.0, items)
    shown = stand_up(panel)
    b = m3.Manifold.batch_boolean([m for m, _ in shown], m3.OpType.Add).bounding_box()
    ft = foot(W - 30, y0=b[4] - 26.0)
    return Product("6_masa_standi", "Masa standı", "Masaya / tezgâha",
                   "Logo, WhatsApp QR'ı ve telefon; müşteri okutup yazar. İstenirse QR Google yorum ya da Instagram "
                   "bağlantısı olur.", panel + [(ft, BLACK)], shown + [(ft, BLACK)], dims=(W, H, 4.0))


def u7_kartvizitlik():
    base, ramp, w_in, ch = 5.0, 30.0, 100.0, 7.0
    w = w_in + 2 * ch
    body = KV.prism([(0, 0), (56, 0), (56, base), (ramp + 3, base), (ramp + 3, ramp), (ramp, ramp)], w)
    body += KV.prism(KV.back_rest(50, 0, 46), w)
    cheek = [(ramp + 3, 0), (56, 0), (56, 20), (ramp + 3, 20)]
    body += KV.prism(cheek, ch, -w / 2) + KV.prism(cheek, ch, w_in / 2)
    L = ramp * math.sqrt(2)
    items, _ = G.fit(G.lockup_stack, (-46, 5.0, 46, L - 4.0))
    parts = [(body, BLACK)] + [(KV.on_slope(cs, 0, 0, 45, 0.8), c) for cs, c in items]
    parts = [parts[0]] + [(m - body, c) for m, c in parts[1:]]
    shown = parts + [(KV.cards(50, base), CARD)]
    return Product("7_kartvizitlik", "Kartvizitlik", "Masaya / tezgâha",
                   "Önü 45° rampa, rampada logo; cep 100 mm: 85 × 55 ve 90 × 50 kartlar rahat sığar.", parts, shown,
                   view=(-30, -64))


def u8_duvar():
    items, R = G.fit(G.lockup_line, (-120, -30, 120, 30))
    sil = A.union(*[cs for cs, _ in items]).offset(2.0, J).offset(-0.4, J)
    parts = [(sil.extrude(3.0), BLACK)] + [(cs.extrude(5.0).translate((0, 0, 3.0)), c) for cs, c in items]
    upright = tf(parts, lambda m: m.rotate((90, 0, 0)).translate((0, -0.01, 0)))
    b = m3.Manifold.batch_boolean([m for m, _ in upright], m3.OpType.Add).bounding_box()
    wall = m3.Manifold.cube((300, 2.0, 120)).translate((-150, 0.0, (b[2] + b[5]) / 2 - 60))
    return Product("8_duvar_logosu", "Duvar logosu", "Ofis duvarına",
                   "24 cm logo; harfler 5 mm kalın, arkası siyah taban. İki vidayla ya da bantla asılır.",
                   parts, upright + [(wall, WALL)], view=(-24, -80))


PRODUCTS = [u1_satilik, u2_etiket, u3_askilik, u4_amblem, u5_altlik, u6_masa, u7_kartvizitlik, u8_duvar]


# ---------------------------------------------------------------- sayfalar

def sheet(p, i):
    im = A.fit_into(render(mesh(p.display), 1400, rotation(*p.view), margin=0.03, **LIGHT), 1000, 560)
    W, H = 1500, 680
    canvas = Image.new("RGB", (W, H), (244, 245, 247))
    dr = ImageDraw.Draw(canvas)
    dr.rounded_rectangle((40, 100, W - 40, H - 30), 26, fill=(226, 228, 232))
    canvas.paste(im, ((W - im.width) // 2, 100 + (H - 130 - im.height) // 2), im)
    dr.text((40, 24), f"{i}. {p.title.upper()}", fill=(24, 26, 30), font=G.K.fnt(34))
    w, h, t = p.dims
    dr.text((40, 68), f"{p.who} · {p.desc}", fill=(96, 100, 110), font=G.K.fnt(19))
    tag = f"{w:.0f} × {h:.0f} × {t:.0f} mm · ~{p.g:.0f} g"
    dr.text((W - 40 - dr.textlength(tag, font=G.K.fnt(20)), 34), tag, fill=(96, 100, 110), font=G.K.fnt(20))
    canvas.save(os.path.join(OUT_DIR, p.key + ".png"))
    return im


def catalog(products, renders):
    W, H = 1654, 2339
    im = Image.new("RGB", (W, H), (244, 244, 242))
    dr = ImageDraw.Draw(im)
    G.header(dr, im, W, "Logolu ürünler", "anahtarlığın yanında")
    dr.text((70, 290), "Hepsi firmanın logosuyla, siyah · turuncu · beyaz; Bambu Lab X2D'de basılır.", font=G.K.fnt(26),
            fill=(40, 40, 44))
    top, gap, cw = 350, 26, (W - 3 * 50) // 2
    ch = (H - top - 150 - 3 * gap) // 4
    f = G.K.fnt
    for k, (p, r) in enumerate(zip(products, renders)):
        x0, y0 = 50 + (k % 2) * (cw + 50), top + (k // 2) * (ch + gap)
        dr.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 26, fill=(255, 255, 255), outline=(222, 222, 226))
        dr.ellipse((x0 + 22, y0 + 20, x0 + 78, y0 + 76), fill=(16, 16, 18))
        n = str(k + 1)
        dr.text((x0 + 50 - dr.textlength(n, font=f(28)) / 2, y0 + 30), n, font=f(28), fill=ORANGE)
        dr.text((x0 + 94, y0 + 22), p["title"], font=f(32), fill=(20, 20, 22))
        dr.text((x0 + 94, y0 + 62), p["who"], font=f(21), fill=ORANGE)
        tag = p["size"]
        dr.text((x0 + cw - 28 - dr.textlength(tag, font=f(20)), y0 + 32), tag, font=f(20), fill=(110, 112, 120))
        img = A.fit_into(r, cw - 60, ch - 210)
        G.K.paste_center(im, img, (x0 + 30, y0 + 96, x0 + cw - 30, y0 + ch - 104))
        ty = y0 + ch - 96
        for line in wrap(dr, p["desc"], f(21), cw - 60)[:3]:
            dr.text((x0 + 30, ty), line, font=f(21), fill=(96, 98, 106))
            ty += 28
    foot = "Logolu ürünlerin hepsi istenen adette basılabilir; QR'lar telefon, WhatsApp ya da web sayfasını açar."
    dr.rounded_rectangle((50, H - 130, W - 50, H - 50), 22, fill=(10, 10, 11))
    dr.text((W / 2 - dr.textlength(foot, font=f(24)) / 2, H - 104), foot, font=f(24), fill=ORANGE)
    path = os.path.join(OUT_DIR, "urunler.png")
    im.save(path, optimize=True)
    im.convert("RGB").save(os.path.join(OUT_DIR, "urunler.pdf"), resolution=200)
    return path


def wrap(dr, text, font, width):
    out, line = [], ""
    for wd in text.split():
        cand = (line + " " + wd).strip()
        if dr.textlength(cand, font=font) <= width:
            line = cand
        else:
            out.append(line)
            line = wd
    return out + [line]


def build(i):
    """i. ürün (ayrı süreçte): ayrıntı sayfası; döner (bilgi, görsel, satır)."""
    p = PRODUCTS[i - 1]()
    ok = all(str(m.status()).endswith("NoError") for m, _ in p.parts)
    r = sheet(p, i)
    w, h, t = p.dims
    info = dict(title=p.title, who=p.who, desc=p.desc, size=f"{w:.0f} × {h:.0f} mm · ~{p.g:.0f} g")
    return info, r, f"{p.key:20s} {w:5.0f} × {h:4.0f} × {t:4.1f} mm  ~{p.g:4.0f} g  sağlam {ok}"


def main():
    from multiprocessing import Pool
    os.makedirs(OUT_DIR, exist_ok=True)
    only = sys.argv[1:]
    todo = [i for i, fn in enumerate(PRODUCTS, 1) if not only or any(o in fn.__name__ for o in only)]
    with Pool(4) as pool:
        rows = pool.map(build, todo)
    for _, _, line in rows:
        print(line)
    if not only:
        print(catalog([p for p, _, _ in rows], [r for _, r, _ in rows]))


if __name__ == "__main__":
    main()
