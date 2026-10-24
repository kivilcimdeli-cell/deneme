"""Hoparlör kapağı önerileri (10): araç içi hoparlör yuvalarına yapıştırılan, ortası yazılı ızgara kapaklar.

İki boy, ikisi de tam yuvarlak: ölçülen Ø100 mm (orta ses) ve Ø70 mm (tiz, REISS) hoparlör; kapak ölçüden 2,5 mm
büyük (Ø102,5 ve Ø72,5 mm) ki kenarı hoparlör halkasının üstüne otursun, kenarından yapıştırılsın.

Yapı (yüzü yukarı, düz basılır; destek gerekmez):
  * ızgara 2 mm (10 katman); delik / yarık en az 2,2 mm, aralarındaki köprüler en az 1,2 mm (kontrol edilir)
  * dış çerçeve 3 mm geniş, 3,4 mm yüksek: sağlamlık ve yapıştırma yüzeyi (alt yüzü tablada: düz)
  * ortada yazı: Ø100 kapakta yuvarlak rozet, Ø70 kapakta (tiz kubbesinin önünü az kapatsın diye) yatay şerit; yazı
    0,8 mm kabartma
  * ses geçsin diye açıklık oranı hesaplanır (ızgara alanının yüzdesi)
Renk: siyah gövde, beyaz yazı; bazılarında kırmızı halka. Yazı şimdilik örnek ("YAZINIZ"): `YAZI` değiştirilip
yeniden çalıştırılır.

Çıktı : hoparlor_kapagi/<n>_<ad>.png, musteri_1.png / .jpg (1–6), musteri_2.png / .jpg (7–10), musteri_katalog.pdf

Kullanım:
  python3 scripts/hoparlor_kapagi.py [anahtar ...]
"""
import math
import os
import sys

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import ince_isimlik as N  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "hoparlor_kapagi")
YAZI = "YAZINIZ"
SIZES = {"buyuk": 100.0, "kucuk": 70.0}          # ölçülen hoparlör çapı
EXTRA = 2.5                                        # kapak ölçüden bu kadar büyük
T, H, RAISE = 2.0, 3.4, 0.8                        # ızgara, çerçeve / rozet yüksekliği, yazı kabartması
RIM = 3.0
MIN_HOLE, MIN_BAR = 2.2, 1.2
BLACK, WHITE, RED = (34, 34, 36), (240, 240, 236), (210, 30, 38)
J = m3.JoinType.Round
N.FONT_FILES.update({"michroma": "Michroma-Regular.ttf", "sora": "Sora-ExtraBold.ttf"})


# ---------------------------------------------------------------- desenler (2B: delikler)

def hex_grid(R, pitch):
    """Altıgen dizilimde nokta merkezleri (R yarıçaplı daire içinde)."""
    dy = pitch * math.sqrt(3) / 2
    out = []
    for j, y in enumerate(np.arange(-R, R + dy, dy)):
        off = pitch / 2 if j % 2 else 0.0
        for x in np.arange(-R - pitch, R + pitch, pitch):
            if math.hypot(x + off, y) < R:
                out.append((x + off, y))
    return out


def p_round(R, rc):
    return A.union(*[A.circle(1.3, x, y, 20) for x, y in hex_grid(R, 3.9)])


def p_hex(R, rc):
    s = 1.9                                                   # altıgen merkezden köşeye
    hexa = lambda x, y: A.polygon([(x + s * math.cos(math.radians(30 + 60 * k)),  # noqa: E731
                                     y + s * math.sin(math.radians(30 + 60 * k))) for k in range(6)])
    return A.union(*[hexa(x, y) for x, y in hex_grid(R, 2 * s * math.cos(math.radians(30)) + 1.3)])


def p_radial(R, rc):
    """Kama yarıklar: aralarındaki köprü her yerde 1,4 mm."""
    r0, r1, bar = max(rc + 2.4, 0.32 * R), R, 1.4
    n = int(2 * math.pi * r0 / (2.4 + bar))
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n
        half0 = (2 * math.pi * r0 / n - bar) / 2 / r0
        half1 = (2 * math.pi * r1 / n - bar) / 2 / r1
        out.append(A.polygon([(r0 * math.cos(a - half0), r0 * math.sin(a - half0)),
                              (r1 * math.cos(a - half1), r1 * math.sin(a - half1)),
                              (r1 * math.cos(a + half1), r1 * math.sin(a + half1)),
                              (r0 * math.cos(a + half0), r0 * math.sin(a + half0))]))
    return A.union(*out)


def p_rings(R, rc):
    """İç içe halka yarıklar, her halkada köprüler (halkalar kayık, tuğla gibi)."""
    out, r, k = [], rc + 2.2, 0
    while r + 2.4 <= R:
        ring = A.circle(r + 2.4, 0, 0, 160) - A.circle(r, 0, 0, 160)
        n = max(4, int(2 * math.pi * r / 14))
        bars = A.union(*[A.rect(-0.75, 0, 0.75, R + 5).rotate(360 * i / n + (180 / n if k % 2 else 0))
                         for i in range(n)])
        out.append(ring - bars)
        r += 2.4 + 1.5
        k += 1
    return A.union(*out)


def p_turbine(R, rc):
    """Kıvrık yarıklar (türbin)."""
    r0, r1 = max(rc + 2.4, 0.32 * R), R + 1.0
    n = int(2 * math.pi * r0 / 4.4)
    out = []
    for k in range(n):
        a0 = 2 * math.pi * k / n
        pts = [((r0 + (r1 - r0) * u) * math.cos(a0 + 0.9 * u), (r0 + (r1 - r0) * u) * math.sin(a0 + 0.9 * u))
               for u in np.linspace(0, 1, 30)]
        out.append(A.stroke(pts, 2.4))
    return A.union(*out)


def p_lines(R, rc):
    """Yatay yarıklar; iki dikey köprü uzun çubukları taşır."""
    out = []
    for y in np.arange(-R, R, 2.4 + 1.5):
        out.append(A.rrect(2 * R + 4, 2.4, 1.19, 0, y + 1.2))
    holes = A.union(*out)
    return holes - A.rect(-R * 0.48 - 0.8, -R - 2, -R * 0.48 + 0.8, R + 2) - A.rect(R * 0.48 - 0.8, -R - 2,
                                                                                      R * 0.48 + 0.8, R + 2)


def p_diamond(R, rc):
    """Çapraz kafes: eşkenar dörtgen delikler."""
    p, bar = 8.0, 1.6
    out = []
    for i in range(-40, 41):
        for j in range(-40, 41):
            x, y = (i + j) * p / 2, (i - j) * p / 2
            if math.hypot(x, y) < R + p:
                h = (p - bar * math.sqrt(2)) / 2
                out.append(A.polygon([(x, y + h), (x + h, y), (x, y - h), (x - h, y)]))
    return A.union(*out)


def p_spokes(R, rc):
    """Jant: altı kol, aralar geniş açık; açıklıklarda ince halka."""
    disc = A.circle(R, 0, 0, 160) - A.circle(rc + 2.4, 0, 0, 120)
    spokes = A.union(*[A.rrect(4.0, 2 * R + 6, 1.0).rotate(30 * k) for k in range(0, 6, 1)])
    mid = (rc + R) / 2
    ring = A.circle(mid + 0.8, 0, 0, 160) - A.circle(mid - 0.8, 0, 0, 160)
    return (disc - spokes - ring).offset(-0.6, J).offset(0.6, J)


def p_waves(R, rc):
    """Dalgalı yatay yarıklar; iki dikey köprü uzun çubukları taşır."""
    out = []
    xs = np.linspace(-R - 4, R + 4, 160)
    for y in np.arange(-R, R + 4.4, 4.4):            # dalgalar arası dik ölçüde ≥ 1,4 mm
        out.append(A.stroke([(x, y + 1.3 * math.sin(2 * math.pi * x / 16.0)) for x in xs], 2.5))
    holes = A.union(*out)
    for x in (-R * 0.48, R * 0.48):
        holes = holes - A.rect(x - 0.9, -R - 3, x + 0.9, R + 3)
    return holes


def p_square(R, rc):
    s, bar = 4.0, 1.6
    return A.union(*[A.rect(x - s / 2, y - s / 2, x + s / 2, y + s / 2)
                     for x in np.arange(-R, R + 1, s + bar) for y in np.arange(-R, R + 1, s + bar)
                     if math.hypot(x, y) < R + s])


def p_gradient(R, rc):
    """Degrade: halkalar hâlinde yuvarlak delikler, içeriden dışa Ø2,4'ten Ø4,2'ye büyür."""
    r0 = max(rc + 3.0, 0.3 * R)
    out, r = [], r0
    while True:
        d = 2.4 + 1.8 * min(1.0, (r - r0) / max(R - r0, 1.0))
        if r + d / 2 > R + 0.5:
            break
        n = int(2 * math.pi * r / (d + 1.4))
        out += [A.circle(d / 2, r * math.cos(2 * math.pi * k / n + r), r * math.sin(2 * math.pi * k / n + r), 24)
                for k in range(n)]
        r += d + 1.3
    return A.union(*out)


# ---------------------------------------------------------------- tasarımlar

class Design:
    def __init__(self, key, title, desc, pattern, font="outfit", ring=False, bar=False):
        self.key, self.title, self.desc = key, title, desc
        self.pattern, self.font, self.ring, self.bar = pattern, font, ring, bar


DESIGNS = [
    Design("1_delikli", "Delikli", "Klasik yuvarlak delikli ızgara; ortada yazı.", p_round),
    Design("2_petek", "Petek", "Bal peteği altıgen delikler; kırmızı iç halka.", p_hex, "sora", ring=True),
    Design("3_isinsal", "Işınsal", "Merkezden dışa açılan kama yarıklar.", p_radial, "michroma"),
    Design("4_halkalar", "Halkalar", "İç içe halka yarıklar, köprüler tuğla gibi kaydırılmış.", p_rings, ring=True),
    Design("5_turbin", "Türbin", "Kıvrık yarıklar; dönen türbin görüntüsü.", p_turbine, "saira"),
    Design("6_yatay", "Yatay çizgi", "Yatay yarıklar; yazı ortada yatay şeritte.", p_lines, "michroma", bar=True),
    Design("7_elmas", "Elmas", "Çapraz kafes, eşkenar dörtgen delikler.", p_diamond, "sora"),
    Design("8_jant", "Jant", "Jant gibi altı kol, aralar açık; ortası jant göbeği.", p_spokes, ring=True),
    Design("9_dalga", "Dalga", "Dalgalı yatay yarıklar; iki ince köprü taşır.", p_waves, "outfit"),
    Design("10_degrade", "Degrade", "Delikler içeriden dışa büyür; kırmızı halka.", p_gradient, "saira", ring=True),
]


def center(design, D):
    """Ortadaki yazı alanı: Ø100 kapakta yuvarlak rozet, Ø70'te yatay şerit (tiz kubbesi açık kalsın).
    Döner (alan, yazı, yarıçap — desenin başladığı iç sınır)."""
    big = D >= 90
    if big and not design.bar:
        rc = 18.0
        badge = A.circle(rc, 0, 0, 160)
        txt = text(design.font, 6.0, 2 * rc - 7.0, 0.8)
        return badge, txt, rc
    w = (34.0 if not big else 2 * (D / 2 + EXTRA / 2 - RIM) - 10.0)
    h = 9.0 if not big else 12.0
    badge = A.rrect(w, h, h / 2 - 0.01)
    txt = text(design.font, 4.6 if not big else 6.4, w - h, 0.6)
    return badge, txt, h / 2 + 0.0


def text(font, cap, max_w, tr):
    """Ortadaki yazı; Michroma ince olduğundan 0,4 nozul için kalınlaştırılır."""
    cs = N.t(font, YAZI, cap, 0, 0, "c", tr, max_w)
    return cs.offset(0.14, J) if font == "michroma" else cs


def build(design, D):
    """Bir kapak: [(katı, renk)] ve ölçümler."""
    Rc = (D + EXTRA) / 2                                  # kapak yarıçapı
    Ri = Rc - RIM                                         # ızgara alanı
    badge, txt, rc = center(design, D)
    holes = design.pattern(Ri, rc)
    keep = A.circle(Ri - 0.9, 0, 0, 200) - badge.offset(1.4, J)
    # kenarda / rozette kesilen deliklerden 2,2 mm'den dar kalan uçlar ve kırıntılar atılır (açma işlemi)
    holes = (holes ^ keep).offset(-MIN_HOLE / 2, J).offset(MIN_HOLE / 2, J)
    holes = A.union(*[p for p in holes.decompose() if p.area() > 2.0])
    grille = A.circle(Rc, 0, 0, 240) - holes
    rim = A.circle(Rc, 0, 0, 240) - A.circle(Ri, 0, 0, 240)
    body = grille.extrude(T) + (rim + badge).extrude(H)
    parts = [(body, BLACK), (txt.extrude(RAISE).translate((0, 0, H)), WHITE)]
    if design.ring:
        ring = A.circle(Rc - 0.8, 0, 0, 240) - A.circle(Rc - 2.2, 0, 0, 240)
        parts.append((ring.extrude(0.6).translate((0, 0, H)), RED))
    open_pct = 100 * holes.area() / (A.circle(Ri, 0, 0, 240) - badge).area()
    thin = grille - grille.offset(-MIN_BAR / 2, J).offset(MIN_BAR / 2, J)
    small = [p for p in holes.decompose() if p.offset(-MIN_HOLE / 2 + 0.1, J).is_empty()]
    m = dict(D=2 * Rc, open=open_pct, thin=sum(p.area() for p in thin.decompose() if p.area() > 0.3),
             small=len(small), grams=sum(Y_grams(s) for s, _ in parts))
    return parts, m


def Y_grams(man, density=1.24, infill=1.0):
    return man.volume() / 1000 * density * infill


# ---------------------------------------------------------------- çizim

def mesh(parts):
    return [(*A.mesh_arrays(m), c) for m, c in parts]


def font_ui(n):
    return ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), n)


LIGHT = dict(ldir=(-0.3, 0.45, 0.84), ambient=0.42)


def pair_image(design, size=1200, view=(-18, -40)):
    """İki kapak yan yana, gerçek oranda (büyük solda)."""
    (pb, mb), (ps, ms) = build(design, SIZES["buyuk"]), build(design, SIZES["kucuk"])
    off = mb["D"] / 2 + ms["D"] / 2 + 12.0
    shown = pb + [(m.translate((off, -8.0, 0)), c) for m, c in ps]
    im = render(mesh(shown), size, rotation(*view), margin=0.03, **LIGHT)
    return im, mb, ms


def sheet(design, i):
    top = A.fit_into(render(mesh(build(design, SIZES["buyuk"])[0]), 1100, rotation(0, 0), flat=0.9, margin=0.02),
                     560, 560)
    top_s = A.fit_into(render(mesh(build(design, SIZES["kucuk"])[0]), 900, rotation(0, 0), flat=0.9, margin=0.02),
                       int(560 * 72.5 / 102.5), int(560 * 72.5 / 102.5))
    iso, mb, ms = pair_image(design, 1300)
    iso = A.fit_into(iso, 620, 560)
    W, Hh = 1500, 760
    canvas = Image.new("RGB", (W, Hh), (236, 239, 244))
    dr = ImageDraw.Draw(canvas)
    boxes = [(30, 150, 640, 740), (660, 150, 1060, 740), (1080, 150, 1470, 740)]
    dr.rounded_rectangle(boxes[0], 22, fill=(146, 153, 166))
    canvas.paste(iso, (30 + (610 - iso.width) // 2, 180 + (560 - iso.height) // 2), iso)
    dr.text((46, 160), "3/4: Ø100 ve Ø70 kapak", fill=(236, 239, 244), font=font_ui(18))
    for (im, label), (x0, y0, x1, y1) in zip(((top, f"Üstten Ø{mb['D']:.1f} mm · açıklık %{mb['open']:.0f}"),
                                             (top_s, f"Üstten Ø{ms['D']:.1f} mm · açıklık %{ms['open']:.0f}")),
                                            boxes[1:]):
        dr.rounded_rectangle((x0, y0, x1, y1), 22, fill=(146, 153, 166))
        im2 = A.fit_into(im, x1 - x0 - 30, y1 - y0 - 70) if im.width > x1 - x0 - 30 else im
        canvas.paste(im2, (x0 + (x1 - x0 - im2.width) // 2, y0 + 40 + (y1 - y0 - 40 - im2.height) // 2), im2)
        dr.text((x0 + 16, y0 + 10), label, fill=(236, 239, 244), font=font_ui(18))
    dr.text((30, 18), f"{i}. {design.title.upper()}", fill=(24, 26, 30), font=font_ui(34))
    dr.text((30, 66), design.desc, fill=(80, 86, 98), font=font_ui(20))
    ok = mb["thin"] < 1.0 and ms["thin"] < 1.0 and mb["small"] == 0 and ms["small"] == 0
    dr.text((30, 104), f"Izgara 2 mm, çerçeve 3 mm · ~{mb['grams']:.0f} g + ~{ms['grams']:.0f} g · delikler ≥ {MIN_HOLE} mm, "
                       f"köprüler ≥ {MIN_BAR} mm: {'tamam' if ok else 'KONTROL'}",
            fill=(22, 120, 60) if ok else (200, 30, 38), font=font_ui(19))
    canvas.save(os.path.join(OUT_DIR, design.key + ".png"))
    return mb, ms, ok


def catalog(images, infos):
    W, Hh = 1654, 2339
    f = font_ui
    ink, muted, paper, red = (20, 20, 22), (96, 98, 106), (245, 245, 243), RED
    big = ImageFont.truetype(os.path.join(A.FONT_DIR, "Sora-ExtraBold.ttf"), 80)
    pages = []
    for p, group in enumerate([list(range(0, 6)), list(range(6, 10))]):
        im = Image.new("RGB", (W, Hh), paper)
        dr = ImageDraw.Draw(im)
        dr.rectangle((0, 0, W, 250), fill=(14, 14, 16))
        for k in range(7):                                        # sağ üstte ızgara deseni
            for j in range(4):
                cx, cy = W - 330 + k * 44 + (22 if j % 2 else 0), 50 + j * 44
                dr.ellipse((cx - 13, cy - 13, cx + 13, cy + 13), fill=(40, 40, 44))
        dr.text((70, 46), "HOPARLÖR KAPAĞI", font=big, fill=(244, 244, 242))
        dr.text((72, 172), "Tasarım önerileri · Ø100 ve Ø70 mm hoparlör · ortada yazı", font=f(30), fill=(200, 200, 206))
        dr.rectangle((0, 246, W, 254), fill=red)
        dr.text((W - 70 - dr.textlength(f"{p + 1}/2", font=f(28)), 196), f"{p + 1}/2", font=f(28), fill=(170, 170, 176))
        y = 285
        for line in ("Kapaklar hoparlörden 2,5 mm büyük (Ø102,5 ve Ø72,5 mm): kenarı halkaya oturur, kenardan yapıştırılır.",
                     f"Yazı örnek (\"{YAZI}\"); istediğiniz yazı ve renkle hazırlanır. Delikler sesi geçirir."):
            dr.text((70, y), line, font=f(25), fill=ink)
            y += 38
        top, gap, cw = 395, 44, (W - 3 * 60) // 2
        ch = (Hh - top - 190 - 2 * gap) // 3
        for k, idx in enumerate(group):
            d, (mb, ms) = DESIGNS[idx], infos[idx]
            x0, y0 = 60 + (k % 2) * (cw + 60), top + (k // 2) * (ch + gap)
            dr.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 28, fill=(255, 255, 255), outline=(226, 226, 230))
            dr.ellipse((x0 + 26, y0 + 24, x0 + 86, y0 + 84), fill=(16, 16, 18))
            n = str(idx + 1)
            dr.text((x0 + 56 - dr.textlength(n, font=f(32)) / 2, y0 + 35), n, font=f(32), fill=(244, 244, 242))
            dr.text((x0 + 104, y0 + 30), d.title, font=f(38), fill=ink)
            tag = f"açıklık %{mb['open']:.0f}"
            dr.text((x0 + cw - 30 - dr.textlength(tag, font=f(22)), y0 + 42), tag, font=f(22), fill=muted)
            img = A.fit_into(images[idx], cw - 50, ch - 160)
            im.paste(img, (x0 + (cw - img.width) // 2, y0 + 96 + (ch - 160 - img.height) // 2), img)
            dr.text((x0 + 30, y0 + ch - 50), d.desc, font=f(23), fill=muted)
        if p == 1:
            y0, y1 = top + 2 * (ch + gap), Hh - 190
            dr.rounded_rectangle((60, y0, W - 60, y1), 28, fill=(255, 255, 255), outline=(226, 226, 230))
            dr.text((100, y0 + 40), "Ürün", font=f(38), fill=ink)
            ty = y0 + 110
            for line in ("İki boy: Ø102,5 mm (Ø100 hoparlör) ve Ø72,5 mm (Ø70 tiz)",
                         "Izgara 2 mm, dış çerçeve 3 mm geniş: yapıştırma yüzeyi düz",
                         "Ø70 kapakta yazı ince şeritte: tiz kubbesinin önü açık kalır",
                         "Siyah gövde, beyaz yazı; istenirse kırmızı halka ya da başka renk"):
                dr.ellipse((100, ty + 10, 114, ty + 24), fill=red)
                dr.text((130, ty), line, font=f(28), fill=muted)
                ty += 54
            pair = []
            for key in ("buyuk", "kucuk"):
                pair.append(render(mesh(build(DESIGNS[0], SIZES[key])[0]), 900, rotation(0, 0), flat=0.9, margin=0.01))
            hb = y1 - y0 - 330
            big_im = A.fit_into(pair[0], hb, hb)
            small_im = A.fit_into(pair[1], int(hb * 72.5 / 102.5), int(hb * 72.5 / 102.5))
            x = W - 110 - big_im.width - small_im.width - 30
            im.paste(big_im, (x, y1 - 40 - big_im.height), big_im)
            im.paste(small_im, (x + big_im.width + 30, y1 - 40 - small_im.height), small_im)
            dr.text((x, y1 - 40 - big_im.height - 40), "Üstten, gerçek oranda: Ø102,5 ve Ø72,5 mm", font=f(22), fill=muted)
        foot = "Beğendiğiniz modelin numarasını ve yazıyı yazmanız yeterli."
        dr.rounded_rectangle((60, Hh - 150, W - 60, Hh - 70), 22, fill=(16, 16, 18))
        dr.text((W / 2 - dr.textlength(foot, font=f(30)) / 2, Hh - 128), foot, font=f(30), fill=(244, 244, 242))
        im.save(os.path.join(OUT_DIR, f"musteri_{p + 1}.png"), optimize=True)
        im.convert("RGB").save(os.path.join(OUT_DIR, f"musteri_{p + 1}.jpg"), "JPEG", quality=90, optimize=True)
        pages.append(im)
    pages[0].save(os.path.join(OUT_DIR, "musteri_katalog.pdf"), save_all=True, append_images=pages[1:], resolution=200)


def work(i):
    d = DESIGNS[i - 1]
    mb, ms, ok = sheet(d, i)
    im, _, _ = pair_image(d, 1300)
    line = (f"{d.key:12s} Ø{mb['D']:.1f}: açıklık %{mb['open']:.0f}, ince köprü {mb['thin']:.1f} mm², küçük delik "
            f"{mb['small']}, ~{mb['grams']:.0f} g  |  Ø{ms['D']:.1f}: açıklık %{ms['open']:.0f}, ince {ms['thin']:.1f} mm², "
            f"küçük {ms['small']}, ~{ms['grams']:.0f} g  {'tamam' if ok else 'KONTROL'}")
    return im, (mb, ms), line


def main():
    from multiprocessing import Pool
    os.makedirs(OUT_DIR, exist_ok=True)
    only = sys.argv[1:]
    todo = [i for i, d in enumerate(DESIGNS, 1) if not only or any(o in d.key for o in only)]
    with Pool(4) as pool:
        rows = pool.map(work, todo)
    for _, _, line in rows:
        print(line)
    if not only:
        catalog([r[0] for r in rows], [r[1] for r in rows])


if __name__ == "__main__":
    main()
