"""ÇALIK OTO LASTİK – kartvizitlik önerileri (6 model): siyah gövde, sarı yazı ve süs; X2D'de dik basılır.

Her model ayrı biçim (gövde şekli), ayrı süs:
  1 Sade        alçak L: ön dudakta ÇALIK OTO LASTİK
  2 Rampa       önü 45° eğimli rampa: üstünde ÇALIK ve lastik izi okları (isimlikteki 7 numarayla takım)
  3 Blok        dolu blok, kartlar üstteki eğik yarıkta; önde büyük ÇALIK ve telefon
  4 QR'lı       yanında QR levhası (siteyi açar, TARA): kartı almayan da okutur
  5 İkaz        dört duvarlı tepsi, önde sarı-siyah ikaz şeridi ve ÇALIK
  6 Lastik      iki yanı diş izli lastik, yan yüzünde sarı jant; önde ÇALIK OTO LASTİK

Ortak ölçüler: kart cebi 92 mm geniş (85 × 55 ve 90 × 50 kartlar sığar), kartlar 15° arkaya yaslanır, cep ~50 kart
alır. Yazılar ve süsler 1 mm kabartma (QR yüzeyle aynı hizada). Tabana oturarak (dik) basılır, destek gerekmez.

Renk: iki renk. Siyah gövde ana nozulda, sarı yardımcı nozulda; dik yüzeydeki yazı her katmanda yalnız nozul
değiştirir (filament değişimi yok, fire az). İstenirse sarı yerine beyaz.

Çıktı : calik_isimlik/kartvizitlik/<n>_<ad>.png (3/4, önden, yandan), kartvizitlik/musteri_kartvizitlik.png ve .pdf

Kullanım:
  python3 scripts/calik_kartvizitlik.py
"""
import math
import os
import sys

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import calik_isimlik as C  # noqa: E402
import ince_isimlik as N  # noqa: E402
import masa_isimligi_yeni as Y  # noqa: E402
import qr_sistemi as Q  # noqa: E402
import uzar_anahtarlik as U  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(C.OUT_DIR, "kartvizitlik")
BLACK, YELLOW, CARD = A.BLACK, A.YELLOW, "kart"
SHOW = {BLACK: (40, 40, 43), YELLOW: (250, 198, 24), CARD: (246, 246, 242)}
J = m3.JoinType.Round
W_IN = 92.0            # kart cebi genişliği
CHEEK = 6.0            # yan duvar
W = W_IN + 2 * CHEEK   # dış genişlik 104
LEAN = 15.0            # kartların yaslanma açısı
RELIEF = 1.0
SINK = 0.2             # kabartma gövdeye bu kadar girer; Model.parts gövdeyi çıkarır (eğik yüzeyde arada boşluk kalmaz)
LIGHT = dict(ldir=(-0.45, 0.1, 0.89), ambient=0.42)   # 3/4 görünüş: ışık önden, yazılı ön yüz aydınlık
t = C.t                # yazı (İ / Ö noktaları ayrık)


# ---------------------------------------------------------------- geometri yardımcıları

def slab(cs, width=W, x0=None):
    """(y, z) düzlemindeki 2B şekli x boyunca uzatır; ortası x = 0 (x0 verilirse sol kenarı x0)."""
    left = -width / 2 if x0 is None else x0
    return cs.extrude(width).transform([[0, 0, 1, left], [1, 0, 0, 0], [0, 1, 0, 0]])


def prism(pts, width=W, x0=None):
    """(y, z) düzlemindeki çokgen profili x boyunca uzatır."""
    return slab(A.polygon(pts), width, x0)


def on_front(cs, y, relief=RELIEF, sink=SINK):
    """(x, z) düzlemindeki 2B şekli y düzleminden öne (−y) doğru kabartır (gövdeye `sink` kadar girer)."""
    return cs.extrude(relief + sink).translate((0, 0, -sink)).transform([[1, 0, 0, 0], [0, 0, -1, y], [0, 1, 0, 0]])


def on_slope(cs, y0, z0, deg, relief=RELIEF, sink=SINK):
    """Öne bakan eğik yüzey (yataydan `deg` derece): 2B (x, s) – s eğim boyunca yukarı – (y0, z0) noktasından.
    Yüzeyden `relief` kadar çıkar, içine `sink` kadar girer (relief 0 ise yüzeyle aynı hizada dolgu)."""
    a = math.radians(deg)
    dy, dz = math.cos(a), math.sin(a)          # eğim boyunca (arkaya ve yukarı)
    ny, nz = -math.sin(a), math.cos(a)         # yüzey normali (öne ve yukarı)
    return cs.extrude(relief + sink).translate((0, 0, -sink)).transform([[1, 0, 0, 0], [0, dy, ny, y0],
                                                                         [0, dz, nz, z0]])


def cards(y_bottom, z_bottom, n=40, lean=LEAN, w=85.0, h=55.0):
    """Kart destesi (yalnız görüntü): alt arka kenarı (y_bottom, z_bottom), arkaya `lean` derece yaslı."""
    th = n * 0.32
    box = m3.Manifold.cube((w, th, h)).translate((-w / 2, -th, 0))
    return box.rotate((-lean, 0, 0)).translate((0, y_bottom, z_bottom))


def back_rest(y, z, height, thick=5.0, lean=LEAN):
    """Arkaya yaslı sırt: ön alt kenarı (y, z)."""
    d = height * math.tan(math.radians(lean))
    return [(y, z), (y + thick, z), (y + thick + d, z + height), (y + d, z + height)]


def cheeks(depth, height, y0=0.0, z0=0.0):
    """İki yan duvar (kart cebini 92 mm'de tutar)."""
    one = lambda x: prism([(y0, z0), (y0 + depth, z0), (y0 + depth, z0 + height), (y0, z0 + height)],  # noqa: E731
                          CHEEK, x)
    return one(-W / 2) + one(W_IN / 2)


class Model:
    def __init__(self, key, title, desc):
        self.key, self.title, self.desc = key, title, desc
        self.body, self.yellow, self.stack, self.qr = None, [], None, None

    def parts(self):
        out = [("Gövde (siyah)", self.body, BLACK)]
        if self.yellow:
            out.append(("Yazı ve süs (sarı)", m3.Manifold.batch_boolean(self.yellow, m3.OpType.Add) - self.body, YELLOW))
        return out


# ---------------------------------------------------------------- modeller

def k1_sade():
    m = Model("1_sade", "Sade", "Alçak, sağlam gövde; ön dudakta ÇALIK OTO LASTİK.")
    depth, lip_h, base = 44.0, 16.0, 4.0
    body = prism([(0, 0), (depth, 0), (depth, base), (0, base)])
    body += prism([(0, 0), (6, 0), (6, lip_h), (0, lip_h)])
    body += prism(back_rest(26, 0, 42))
    body += cheeks(depth - 6, 14)
    m.body = body
    m.yellow = [on_front(t("barlow", "ÇALIK OTO LASTİK", 8.0, 0, 8.4, "c", 0.8), 0)]
    m.stack = cards(26, base)
    return m


def k2_rampa():
    m = Model("2_rampa", "Rampa", "Önü 45° rampa; üstünde ÇALIK ve isimlikteki gibi lastik izi okları.")
    base, ramp = 5.0, 24.0
    body = prism([(0, 0), (52, 0), (52, base), (ramp + 3, base), (ramp + 3, ramp), (ramp, ramp)])
    body += prism(back_rest(46, 0, 44))
    body += cheeks(25, 18, ramp + 3)
    m.body = body
    L = ramp * math.sqrt(2)
    marks = U.chevrons(-41.0, L - 8.0, 6.0, 9, 9.6, 2.2).offset(-0.4, J).offset(0.4, J)
    m.yellow = [on_slope(t("barlow", "ÇALIK", 13.0, 0, 13.0, "c", 0.8), 0, 0, 45),
                on_slope(marks, 0, 0, 45)]
    m.stack = cards(46, base)
    return m


def k3_blok():
    m = Model("3_blok", "Blok", "Dolu blok; kartlar üstteki eğik yarıkta. Önde büyük ÇALIK ve telefon.")
    depth, h = 38.0, 32.0
    body = prism([(0, 0), (depth, 0), (depth, h), (0, h)])
    slot = prism(back_rest(14, 8, 40, thick=13), W_IN)          # eğik yarık (13 mm), tabanı 8 mm yukarıda
    body = body - slot
    m.body = body
    m.yellow = [on_front(t("barlow", "ÇALIK", 14.0, 0, 21.0, "c", 1.2), 0),
                on_front(t("outfit", C.PHONE, 4.8, 0, 6.0, "c", 0.4), 0)]
    m.stack = cards(27 - 0.3, 8, n=36)
    return m


def k4_qr():
    m = Model("4_qr", "QR'lı", "Yanında QR levhası: siteyi açar. Kartı almayan da okutup kaydeder.")
    depth, lip_h, base, wing = 44.0, 14.0, 4.0, 44.0
    dx = -wing / 2                                              # kart cebi sola, QR levhası sağa
    body = prism([(0, 0), (depth, 0), (depth, base), (0, base)], W + wing)
    body += prism([(0, 0), (6, 0), (6, lip_h), (0, lip_h)], W, -W / 2 + dx)
    body += prism(back_rest(26, 0, 40), W, -W / 2 + dx)
    body += cheeks(depth - 6, 12).translate((dx, 0, 0))
    # QR levhası 15° arkaya yaslı; ön yüzünde sarı QR (siyah kareler gövde, yüzeyle aynı hizada), üstünde TARA
    s, ph, y0 = 36.0, 52.0, 8.0
    x0 = W / 2 + dx + 3.0
    pw = (W + wing) / 2 - x0
    d = ph * math.tan(math.radians(LEAN))
    body += prism([(y0, base), (y0 + 5, base), (y0 + 5 + d, base + ph), (y0 + d, base + ph)], pw, x0)
    cx, cs_ = x0 + pw / 2, 4.0 + s / 2
    m.qr = Q.module_for(C.QR, s)
    _, dark, _ = Q.shapes(C.QR, m.qr, cx, cs_)
    face = lambda cs, relief, sink=SINK: on_slope(cs, y0, base, 90 - LEAN, relief, sink)  # noqa: E731
    light = A.rrect(s, s, 1.6, cx, cs_) - dark
    m.body = body - face(light, 1.0, 0.8)                          # oyuk yüzün önüne taşar: eğik yüzde zar kalmaz
    m.yellow = [face(light, 0, 0.8), face(t("outfit", "TARA", 5.0, cx, cs_ + s / 2 + 5.5, "c", 1.2), RELIEF),
                on_front(t("barlow", "ÇALIK", 8.6, dx, 8.2, "c", 1.0), 0)]
    m.stack = cards(26, base).translate((dx, 0, 0))
    return m


def k5_ikaz():
    m = Model("5_ikaz", "İkaz şeridi", "Dört duvarlı tepsi; önde sarı-siyah ikaz şeridi ve ÇALIK.")
    depth, front_h, base = 40.0, 22.0, 4.0
    body = prism([(0, 0), (depth, 0), (depth, base), (0, base)])
    body += prism([(0, 0), (5, 0), (5, front_h), (0, front_h)])
    body += prism(back_rest(depth - 12, 0, 40, thick=6))
    body += cheeks(depth - 5, front_h)
    m.body = body
    stripes = C.hazard(-W / 2 + 2, W / 2 - 2, 2.5, 8.5, 3.2)
    m.yellow = [on_front(stripes, 0), on_front(t("barlow", "ÇALIK", 9.0, 0, 15.2, "c", 1.4), 0)]
    m.stack = cards(depth - 12, base)
    return m


def tire(cy, cz, R, notch=2.4, pitch=12.0):
    """Yandan lastik: yere basan düz taban (z ≥ 0), çevresinde diş oyukları."""
    disc = A.circle(R, cy, cz, 180) ^ A.rect(cy - R, 0, cy + R, cz + R)
    cuts = [A.rect(-1.6, R - notch, 1.6, R + 1).rotate(a).translate((cy, cz))
            for a in np.arange(0, 360, pitch) if cz + (R - notch) * math.cos(math.radians(a)) > 3.0]
    return disc - A.union(*cuts)


def lip_text(lip_h, max_w, cap):
    """Ön dudaktaki ÇALIK OTO LASTİK (Saira Condensed Black: harf içleri ve aralar ≥ 0,8 mm), dudağın ortasında."""
    cs = t("saira", "ÇALIK OTO LASTİK", cap, 0, 0, "c", 0.8, max_w)
    b = cs.bounds()
    return cs.translate((0, lip_h / 2 - (b[1] + b[3]) / 2))


def k6_lastik(w_in=W_IN, k=1.0, cheek=CHEEK):
    """w_in: kart cebi genişliği; k: diğer ölçülerin büyütme katı (baskı dosyası: w_in 100, k 1,1)."""
    m = Model("6_lastik", "Lastik yanaklı", "İki yanı diş izli lastik, yan yüzünde sarı jant; önde ÇALIK OTO LASTİK.")
    depth, base, lip_h, rest_y = 46.0 * k, 4.0, 14.0 * k, 28.0 * k
    cy, cz, R = 24.0 * k, 26.0 * k, 28.0 * k
    w = w_in + 2 * cheek
    body = prism([(0, 0), (depth, 0), (depth, base), (0, base)], w_in + 0.02)
    body += prism([(0, 0), (6, 0), (6, lip_h), (0, lip_h)], w_in + 0.02)
    body += prism(back_rest(rest_y, 0, 44.0 * k), w_in + 0.02)
    side = tire(cy, cz, R) + A.rect(0, 0, depth, 8.0 * k)          # altı dolu: lastiğin alt yayı desteksiz basılır
    body += slab(side, cheek, w_in / 2) + slab(side, cheek, -w / 2)
    rim = C.wheel(cy, cz, 15.0 * k / 0.56)[1][0]                   # sarı jant (5 bijon deliği ve göbek)
    right = slab(rim, RELIEF + SINK, w / 2 - SINK)
    m.body = body
    m.text = lip_text(lip_h, w_in - 8, 8.0 * k)
    m.yellow = [right, right.mirror((1, 0, 0)), on_front(m.text, 0)]
    m.stack = cards(rest_y, base)
    return m


MODELS = [k1_sade, k2_rampa, k3_blok, k4_qr, k5_ikaz, k6_lastik]


# ---------------------------------------------------------------- görüntüler

def meshes(m, with_cards=True):
    out = [(*A.mesh_arrays(man), SHOW[c]) for _, man, c in m.parts()]
    if with_cards and m.stack is not None:
        out.append((*A.mesh_arrays(m.stack), SHOW[CARD]))
    return out


def font_ui(n):
    return ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), n)


def sheet(m, i):
    Wd, Hd = 1500, 640
    canvas = Image.new("RGB", (Wd, Hd), (236, 239, 244))
    dr = ImageDraw.Draw(canvas)
    views = [(rotation(-30, -64), "3/4, kartlarla", LIGHT), (rotation(0, -90), "Önden", dict(flat=0.85)),
             (rotation(-90, -90), "Yandan", dict(flat=0.85))]
    boxes = [(30, 120, 700, 610), (720, 120, 1180, 610), (1200, 120, 1470, 610)]
    for (R, label, kw), (x0, y0, x1, y1) in zip(views, boxes):
        dr.rounded_rectangle((x0, y0, x1, y1), 22, fill=(146, 153, 166))
        im = A.fit_into(render(meshes(m), 1100, R, margin=0.04, **kw), x1 - x0 - 40, y1 - y0 - 60)
        canvas.paste(im, (x0 + (x1 - x0 - im.width) // 2, y0 + 40 + (y1 - y0 - 40 - im.height) // 2), im)
        dr.text((x0 + 16, y0 + 10), label, fill=(236, 239, 244), font=font_ui(18))
    b = m3.Manifold.batch_boolean([man for _, man, _ in m.parts()], m3.OpType.Add).bounding_box()
    g = sum(Y.grams(man) for _, man, _ in m.parts())
    dr.text((30, 18), f"{i}. {m.title.upper()}", fill=(24, 26, 30), font=font_ui(32))
    dr.text((30, 62), m.desc, fill=(80, 86, 98), font=font_ui(19))
    dr.text((30, 90), f"{b[3] - b[0]:.0f} × {b[4] - b[1]:.0f} × {b[5] - b[2]:.0f} mm · ~{g:.0f} g · siyah + sarı",
            fill=(22, 120, 60), font=font_ui(19))
    canvas.save(os.path.join(OUT_DIR, m.key + ".png"))
    return b, g


def catalog(ms, infos):
    W_, H_ = 1654, 2339
    big = ImageFont.truetype(os.path.join(A.FONT_DIR, "RussoOne-Regular.ttf"), 104)
    mid = ImageFont.truetype(os.path.join(A.FONT_DIR, "RussoOne-Regular.ttf"), 40)
    f = font_ui
    ink, muted, paper, yellow = (20, 20, 22), (96, 98, 106), (245, 245, 243), SHOW[YELLOW]
    im = Image.new("RGB", (W_, H_), paper)
    dr = ImageDraw.Draw(im)
    dr.rectangle((0, 0, W_, 250), fill=(16, 16, 18))
    for x in range(1100, W_ + 200, 64):
        dr.polygon([(x, 250), (x + 30, 250), (x + 30 - 120, 130), (x - 120, 130)], fill=yellow)
    dr.rectangle((0, 246, W_, 254), fill=yellow)
    dr.text((70, 40), "ÇALIK", font=big, fill=(244, 244, 242))
    x = 76 + dr.textlength("ÇALIK", font=big) + 22
    dr.text((x, 72), "OTO LASTİK", font=mid, fill=yellow)
    dr.text((70, 180), "Kartvizitlik · model önerileri", font=f(30), fill=(210, 210, 214))
    y = 285
    for line in ("Hepsi siyah gövde, sarı yazı; kart cebi 85 × 55 ve 90 × 50 kartlara uyar, ~50 kart alır.",
                 "4 numaradaki QR, isimlikteki gibi Çalık Oto Lastik'in sitesini açar."):
        dr.text((70, y), line, font=f(27), fill=ink)
        y += 40
    top, gap, cw = 395, 44, (W_ - 3 * 60) // 2
    ch = (H_ - top - 170 - 2 * gap) // 3
    for k, (m, (b, g)) in enumerate(zip(ms, infos)):
        x0, y0 = 60 + (k % 2) * (cw + 60), top + (k // 2) * (ch + gap)
        dr.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 28, fill=(255, 255, 255), outline=(226, 226, 230))
        dr.ellipse((x0 + 26, y0 + 24, x0 + 86, y0 + 84), fill=(16, 16, 18))
        n = str(k + 1)
        dr.text((x0 + 56 - dr.textlength(n, font=f(34)) / 2, y0 + 34), n, font=f(34), fill=yellow)
        dr.text((x0 + 104, y0 + 30), m.title, font=f(38), fill=ink)
        img = A.fit_into(render(meshes(m), 1400, rotation(-30, -64), margin=0.03, **LIGHT), cw - 60, ch - 190)
        im.paste(img, (x0 + (cw - img.width) // 2, y0 + 100 + (ch - 190 - img.height) // 2), img)
        ty = y0 + ch - 80
        for line in N.wrap(dr, m.desc, f(25), cw - 60)[:2]:
            dr.text((x0 + 30, ty), line, font=f(25), fill=muted)
            ty += 33
    foot = "Beğendiğiniz modelin numarasını yazmanız yeterli."
    dr.rounded_rectangle((60, H_ - 140, W_ - 60, H_ - 60), 22, fill=(16, 16, 18))
    dr.text((W_ / 2 - dr.textlength(foot, font=f(30)) / 2, H_ - 118), foot, font=f(30), fill=yellow)
    im.save(os.path.join(OUT_DIR, "musteri_kartvizitlik.png"), optimize=True)
    im.save(os.path.join(OUT_DIR, "musteri_kartvizitlik.pdf"), resolution=200)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    only = sys.argv[1:]
    ms, infos = [], []
    for i, fn in enumerate(MODELS, 1):
        m = fn()
        if only and not any(o in m.key for o in only):
            continue
        parts = m.parts()
        ok = all(str(man.status()).endswith("NoError") and not man.is_empty() for _, man, _ in parts)
        b, g = sheet(m, i)
        qr = ""
        if m.qr:
            qr_ok, _ = Q.verify(C.QR, m.qr)
            qr = f"  QR ({C.QR.content}) kare {m.qr:.2f} mm, tüm benzetimlerde okundu: {qr_ok}"
        print(f"{m.key:12s} sağlam {ok}  {b[3] - b[0]:.0f} × {b[4] - b[1]:.0f} × {b[5] - b[2]:.0f} mm  ~{g:.0f} g{qr}")
        ms.append(m)
        infos.append((b, g))
    if not only:
        catalog(ms, infos)


if __name__ == "__main__":
    main()
