"""AUTO FIRAT TUYGUN: kurumsal / minimalist anahtarlık konseptleri (yalnız görsel).

Önceki anahtarlıklar müşteriye kalabalık geldi. Bu konseptlerde:
  * ortak bir marka sistemi: FT monogramı + Sora SemiBold isim + Outfit ExtraBold "AUTO"
  * baskıya uygun ölçüler: isim en az 4,4 mm, küçük yazılar en az 3,0 mm (çizgiler ~0,6 mm+)
  * ön yüzde yalnız logo/isim, bol boşluk; telefon ve şehir ARKA yüzde
  * mat siyah zemin + tek vurgu (altın / gümüş / beyaz); yazılar yüzeyle aynı hizada (gömme)

Seçilen konsept daha sonra baskıya hazır 3MF'e çevrilecek (ön yüz üst katmanlarda, arka yüz
tablaya bakan ilk katmanlarda renkli basılır).

Çıktı : anahtarlik/kurumsal/marka.png, anahtarlik/kurumsal/<konsept>.png, anahtarlik/kurumsal/hepsi.png

Kullanım:
  python3 scripts/anahtarlik_konsept.py
"""
import os
import sys

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "anahtarlik", "kurumsal")
NAME, PHONE, CITY = A.NAME, A.PHONE, A.CITY

# renkler (ekran tonu) ve önerilen Bambu filamenti
BLACK = (34, 34, 36)
WHITE = (236, 236, 230)
GOLD = (196, 160, 82)
SILVER = (172, 175, 180)
FILAMENT = {BLACK: "siyah – PLA Matte Charcoal", WHITE: "beyaz – PLA Matte Ivory White",
            GOLD: "altın – PLA Basic Gold", SILVER: "gümüş – PLA Basic Silver"}

THICK, INLAY = 3.6, 0.6          # gövde kalınlığı, gömme renk derinliği (mm)
UI = os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf")


def sora():
    return A.Font("Sora-SemiBold.ttf")


def outfit():
    """Küçük yazılar (telefon, AUTO, şehir): ExtraBold, 3 mm'de bile çizgiler ~0,6 mm."""
    return A.Font("Outfit-ExtraBold.ttf")


# ---------------------------------------------------------------- marka

def ft_mark(h, cx=0.0, cy=0.0, slant=10.0):
    """FT monogramı: F ve T üst çizgiyi paylaşır, hız hissi için hafif eğik. h: yükseklik (mm)."""
    u = h / 14.0
    parts = [A.rect(0, 11.5, 16.5, 14), A.rect(0, 0, 2.5, 14), A.rect(0, 5.9, 8.0, 8.4), A.rect(10.0, 0, 12.5, 14)]
    cs = A.union(*parts).translate((-8.25, -7.0)).scale((u, u))
    return A.shear(cs, slant).translate((cx, cy))


def wordmark(cap, x, y, align="l"):
    return sora().text(NAME, cap, x, y, align=align, tracking=cap * 0.12)


def descriptor(text, cap, x, y, align="l"):
    return outfit().text(text, cap, x, y, align=align, tracking=cap * 0.45)


# ---------------------------------------------------------------- konsept

class Concept:
    def __init__(self, key, title, desc, outline, holes, body=BLACK):
        self.key, self.title, self.desc = key, title, desc
        self.outline, self.holes, self.body = outline, holes, body
        self.front, self.back = [], []          # [(şekil, renk)]; arka yüz arkadan okunur hâlde çizilir

    def colours(self):
        cols = [self.body] + [c for _, c in self.front + self.back]
        return list(dict.fromkeys(cols))

    def size(self):
        x0, y0, x1, y1 = self.outline.bounds()
        return x1 - x0, y1 - y0

    def solids(self):
        shape = self.outline - self.holes
        steps, ch = 3, 0.6
        body = shape.extrude(THICK)
        rings = []
        for k in range(steps):                   # alt ve üst kenarda katmanlı pah
            inset = ch * (steps - k) / steps
            ring = shape - shape.offset(-inset, m3.JoinType.Round)
            rings.append(ring.extrude(0.2).translate((0, 0, k * 0.2 - (0.1 if k == 0 else 0))))
            rings.append(ring.extrude(0.2).translate((0, 0, THICK - (k + 1) * 0.2 + (0.1 if k == 0 else 0))))
        body = body - m3.Manifold.batch_boolean(rings, m3.OpType.Add)
        keep = shape.offset(-1.0, m3.JoinType.Round) - self.holes.offset(0.8, m3.JoinType.Round)
        parts, pockets = [], []
        for cs, col in self.front:
            s = (cs ^ keep).extrude(INLAY).translate((0, 0, THICK - INLAY))
            parts.append((s, col))
            pockets.append(s)
        for cs, col in self.back:
            s = (cs.mirror((1, 0)) ^ keep).extrude(INLAY)
            parts.append((s, col))
            pockets.append(s)
        if pockets:
            body = body - m3.Manifold.batch_boolean(pockets, m3.OpType.Add)
        return [(body, self.body)] + parts


def k1_kapsul():
    W, H = 96.0, 26.0
    c = Concept("1_kapsul", "Kapsül", "Hap biçimi; solda altın FT işareti, yanında beyaz isim ve altın AUTO.",
                A.rrect(W, H, H / 2), A.circle(2.6, -W / 2 + 9.5, 0))
    c.front += [(ft_mark(12.0, -W / 2 + 26.0, 0), GOLD),
                (wordmark(4.6, -W / 2 + 37.0, 2.6), WHITE),
                (descriptor("AUTO", 3.0, -W / 2 + 37.2, -4.8), GOLD)]
    c.back += [(outfit().text(PHONE, 4.4, 6.0, 2.2, tracking=0.5), WHITE),
               (descriptor(CITY, 3.0, 6.0, -5.2, align="c"), GOLD)]
    return c


def k2_logo_kare():
    S = 42.0
    c = Concept("2_logo_kare", "Logo kare", "Uygulama ikonu gibi yuvarlak kare; önde yalnız büyük altın FT işareti.",
                A.rrect(S, S, 11.0), A.circle(2.5, -S / 2 + 7.5, S / 2 - 7.5))
    c.front += [(ft_mark(19.0, 1.5, -1.5), GOLD)]
    c.back += [(sora().text("FIRAT", 4.6, 0, 10.0, tracking=0.5), WHITE),
               (sora().text("TUYGUN", 4.6, 0, 3.0, tracking=0.5), WHITE),
               (A.rect(-9.0, -2.6, 9.0, -1.4), GOLD),
               (outfit().text(PHONE, outfit().fit_cap(PHONE, 3.6, 32.0, 0.3), 0, -7.6, tracking=0.3), WHITE),
               (descriptor(CITY, 3.0, 0, -13.4, align="c"), GOLD)]
    return c


def k3_madalyon():
    R = 20.0
    outline = (A.circle(R, 0, 0, 160) + A.circle(5.6, 0, R + 2.0)).offset(1.4, m3.JoinType.Round).offset(-1.4, m3.JoinType.Round)
    c = Concept("3_madalyon", "Madalyon", "Beyaz yuvarlak madalyon; ince siyah halka içinde siyah FT işareti.",
                outline, A.circle(2.5, 0, R + 2.4), body=WHITE)
    c.front += [(A.outline(A.circle(R, 0, 0, 160), 1.1, inset=2.2), BLACK), (ft_mark(15.0, 0.6, 0), BLACK)]
    c.back += [(sora().text("FIRAT", 4.4, 0, 8.4, tracking=0.5), BLACK),
               (sora().text("TUYGUN", 4.4, 0, 1.8, tracking=0.5), BLACK),
               (outfit().text(PHONE, outfit().fit_cap(PHONE, 3.4, 33.0, 0.2), 0, -4.6, tracking=0.2), BLACK),
               (descriptor(CITY, 3.0, 0, -10.6, align="c"), BLACK)]
    return c


def k4_deri_etiket():
    body = A.rrect(30.0, 46.0, 7.0, 0, -6.0)
    neck = A.polygon([(-15, 14), (15, 14), (9, 25), (-9, 25)])
    loop = A.circle(8.4, 0, 25.5)
    outline = (body + neck + loop).offset(2.0, m3.JoinType.Round).offset(-2.0, m3.JoinType.Round)
    c = Concept("4_deri_etiket", "Deri etiket formu", "Bayi anahtarlığı biçimi; gümüş FT işareti, iki satır beyaz isim.",
                outline, A.rrect(9.0, 5.2, 2.6, 0, 26.6))
    c.front += [(ft_mark(13.0, 0.5, 4.0), SILVER),
                (A.rect(-7.0, -6.4, 7.0, -5.2), SILVER),
                (sora().text("FIRAT", 4.4, 0, -11.8, tracking=0.4), WHITE),
                (sora().text("TUYGUN", 4.4, 0, -18.6, tracking=0.4), WHITE)]
    c.back += [(descriptor("AUTO", 3.0, 0, 6.4, align="c"), SILVER),
               (outfit().text("0535 278", 3.8, 0, -1.4, tracking=0.4), WHITE),
               (outfit().text("35 29", 3.8, 0, -7.8, tracking=0.4), WHITE),
               (descriptor(CITY, 3.0, 0, -15.0, align="c"), SILVER)]
    return c


def k5_ince_bar():
    W, H = 18.0, 86.0
    c = Concept("5_ince_bar", "İnce bar", "Gümüş ince dikey bar; dikey siyah isim ve küçük FT işareti.",
                A.rrect(W, H, W / 2), A.circle(2.6, 0, H / 2 - 8.0), body=SILVER)
    c.front += [(ft_mark(7.0, 0.3, H / 2 - 19.5), BLACK),
                (wordmark(4.6, 0, 0, align="c").rotate(90).translate((0.3, -9.0)), BLACK)]
    c.back += [(outfit().text(PHONE, 3.8, 0, 0, tracking=0.5).rotate(90).translate((-2.0, -8.0)), BLACK),
               (descriptor(CITY, 3.0, 0, 0, align="c").rotate(90).translate((4.0, -8.0)), BLACK)]
    return c


def k6_tek_cizgi():
    W, H = 82.0, 28.0
    c = Concept("6_tek_cizgi", "Tek çizgi", "Dikdörtgen kart; beyaz isim, altında boydan boya altın çizgi ve AUTO.",
                A.rrect(W, H, 4.0), A.circle(2.5, W / 2 - 6.5, H / 2 - 6.5))
    c.front += [(wordmark(5.0, -W / 2 + 5.5, 4.0), WHITE),
                (A.rect(-W / 2 + 5.5, -3.4, W / 2 - 5.5, -2.2), GOLD),
                (descriptor("AUTO", 3.0, W / 2 - 5.5, -8.0, align="r"), GOLD)]
    c.back += [(outfit().text(PHONE, 4.4, -W / 2 + 5.5, 2.4, align="l", tracking=0.5), WHITE),
               (descriptor(CITY, 3.0, -W / 2 + 5.5, -5.2), GOLD)]
    return c


CONCEPTS = [k1_kapsul, k2_logo_kare, k3_madalyon, k4_deri_etiket, k5_ince_bar, k6_tek_cizgi]


# ---------------------------------------------------------------- çizim

def mesh_parts(c):
    return [(*A.mesh_arrays(m), col) for m, col in c.solids()]


def fnt(size):
    return ImageFont.truetype(UI, size)


def panel(dr, box, fill=(226, 228, 232)):
    dr.rounded_rectangle(box, 26, fill=fill)


def paste_center(canvas, im, box):
    x0, y0, x1, y1 = box
    canvas.paste(im, (x0 + (x1 - x0 - im.width) // 2, y0 + (y1 - y0 - im.height) // 2), im)


def concept_sheet(c, path):
    parts = mesh_parts(c)
    views = [("ÖN YÜZ", rotation(0, 0)), ("ARKA YÜZ", rotation(180, 180)), ("PERSPEKTİF", rotation(-22, -50))]
    W, H = 1500, 640
    canvas = Image.new("RGB", (W, H), (244, 245, 247))
    dr = ImageDraw.Draw(canvas)
    dr.text((40, 26), c.title.upper(), fill=(24, 26, 30), font=fnt(34))
    dr.text((40, 72), c.desc, fill=(96, 100, 110), font=fnt(20))
    w, h = c.size()
    dr.text((W - 40 - dr.textlength(f"{w:.0f} × {h:.0f} × {THICK:.1f} mm", font=fnt(20)), 34),
            f"{w:.0f} × {h:.0f} × {THICK:.1f} mm", fill=(96, 100, 110), font=fnt(20))
    for i, (label, R) in enumerate(views):
        box = (40 + i * 480, 120, 40 + i * 480 + 460, 120 + 440)
        panel(dr, box)
        im = A.fit_into(render(parts, 1000, R, margin=0.02), 380, 340)
        paste_center(canvas, im, (box[0], box[1] + 30, box[2], box[3]))
        dr.text((box[0] + 22, box[1] + 18), label, fill=(120, 124, 134), font=fnt(17))
    x = 40
    for col in c.colours():
        dr.rounded_rectangle((x, 586, x + 22, 608), 6, fill=col, outline=(150, 154, 162), width=1)
        dr.text((x + 32, 586), FILAMENT[col], fill=(70, 74, 84), font=fnt(18))
        x += 60 + dr.textlength(FILAMENT[col], font=fnt(18))
    canvas.save(path)
    return canvas


def brand_sheet(path):
    """Marka sistemi: işaret, yatay logo (koyu ve açık zemin)."""
    W, H = 1500, 560
    canvas = Image.new("RGB", (W, H), (244, 245, 247))
    dr = ImageDraw.Draw(canvas)
    dr.text((40, 26), "MARKA SİSTEMİ", fill=(24, 26, 30), font=fnt(34))
    dr.text((40, 72), "FT monogramı + Sora SemiBold isim + Outfit ExtraBold AUTO. Tüm anahtarlıklarda aynı.",
            fill=(96, 100, 110), font=fnt(20))
    k = 9.0

    def draw_cs(items, bg, box):
        x0, y0, x1, y1 = box
        dr.rounded_rectangle(box, 26, fill=bg)
        allc = A.union(*[cs for cs, _ in items])
        bx0, by0, bx1, by1 = allc.bounds()
        s = min((x1 - x0 - 80) / ((bx1 - bx0) * k), (y1 - y0 - 80) / ((by1 - by0) * k), 1.6) * k
        ox = (x0 + x1) / 2 - (bx0 + bx1) / 2 * s
        oy = (y0 + y1) / 2 + (by0 + by1) / 2 * s
        for cs, col in items:
            for p in cs.to_polygons():
                xs, ys = p[:, 0], p[:, 1]
                hole = np.sum(xs * np.roll(ys, -1) - np.roll(xs, -1) * ys) < 0
                dr.polygon([(ox + u * s, oy - v * s) for u, v in p], fill=bg if hole else col)

    lock = [(ft_mark(14.0, 0, 0), GOLD), (wordmark(6.2, 12.5, 2.4), WHITE), (descriptor("AUTO", 3.6, 12.7, -5.6), GOLD)]
    draw_cs(lock, BLACK, (40, 120, 760, 520))
    lock_l = [(ft_mark(14.0, 0, 0), BLACK), (wordmark(6.2, 12.5, 2.4), BLACK), (descriptor("AUTO", 3.6, 12.7, -5.6), GOLD)]
    draw_cs(lock_l, (250, 250, 248), (780, 120, 1180, 520))
    draw_cs([(ft_mark(14.0, 0, 0), GOLD)], BLACK, (1200, 120, 1460, 520))
    canvas.save(path)
    return canvas


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    sheets = [brand_sheet(os.path.join(OUT_DIR, "marka.png"))]
    for fn in CONCEPTS:
        c = fn()
        sheets.append(concept_sheet(c, os.path.join(OUT_DIR, c.key + ".png")))
        print(c.key, "%.0f × %.0f mm" % c.size())
    W = max(s.width for s in sheets)
    sheet = Image.new("RGB", (W, sum(s.height for s in sheets) + 20 * (len(sheets) - 1)), (255, 255, 255))
    y = 0
    for s in sheets:
        sheet.paste(s, (0, y))
        y += s.height + 20
    sheet.save(os.path.join(OUT_DIR, "hepsi.png"))


if __name__ == "__main__":
    main()
