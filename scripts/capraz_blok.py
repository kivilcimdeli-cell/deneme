"""FIRAT TUYGUN çapraz blok masa isimliği (Türk bayraklı): baskıya hazır Bambu Lab X2D 3MF.

Blok 240 × 56 × 32 mm. Çapraz kesimle iki renk: solda kırmızı (beyaz ay-yıldız), sağda siyah
(büyük, kalın beyaz isim ve kırmızı alt çizgi); arada beyaz ince ayraç.

Baskı (desteksiz): blok ön yüzü YUKARI bakacak şekilde yatık basılır.
  * Kırmızı ve siyah kısımlar bloğun tüm derinliği boyunca sürer; X2D'de iki ayrı nozulda
    basıldıkları için katman başına temizleme atığı olmaz.
  * Beyaz (ay-yıldız, isim, ayraç) ve kırmızı alt çizgi ön yüzde 2,0 mm kabartma: yalnızca
    son 10 katman. Böylece üçüncü renk sadece en sonda devreye girer.
  * Tabla kenarında ikinci nozulun erişemediği 20,5 mm'lik şerit yüzünden blok tablaya
    boylamasına (y yönünde) yerleştirilir; ilk katman 0,3 mm içe çekik, üst kenar 0,6 mm pahlı.

Çıktı : masa_isimligi/capraz_blok.3mf, masa_isimligi/onizleme/capraz_blok_baski.png

Kullanım:
  python3 scripts/capraz_blok.py
"""
import os
import sys
import zipfile

import manifold3d as m3
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402
from masa_isimligi import flag  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "masa_isimligi")
NAME = "FIRAT TUYGUN"

W, H, D, R = 240.0, 56.0, 32.0, 6.0          # genişlik, yükseklik (ön yüz), derinlik, köşe yarıçapı
RAISE = 2.0                                   # ön yüz kabartma yüksekliği (10 katman)
SPLIT_BOT, SPLIT_TOP = -W / 2 + 62.0, -W / 2 + 84.0   # çapraz kesim: alttaki ve üstteki x
GAP = 2.4                                     # beyaz ayraç genişliği
FLAG_G = 46.0                                 # ay-yıldız, bu yükseklikteki bayrağın oranlarıyla


def xdiag(v):
    return SPLIT_BOT + (v + H / 2) * (SPLIT_TOP - SPLIT_BOT) / H


def layout():
    """Ön yüz düzeni (merkez 0,0; u genişlik, v yükseklik). Döner: dış hat, sol bölge, ayraç, kabartmalar."""
    outline = A.rrect(W, H, R)
    left = A.polygon([(-W, -H), (xdiag(-H), -H), (xdiag(H), H), (-W, H)])
    gap = A.polygon([(xdiag(-H), -H), (xdiag(-H) + GAP, -H), (xdiag(H) + GAP, H), (xdiag(H), H)])
    _, moon_star = flag(FLAG_G)
    x0, y0, x1, y1 = moon_star.bounds()
    red_cx = (-W / 2 + xdiag(0)) / 2 - 1.0
    moon_star = moon_star.translate((red_cx - (x0 + x1) / 2, -(y0 + y1) / 2))
    nx0, nx1 = xdiag(H / 2) + GAP + 9.0, W / 2 - 9.0
    f = A.font("bebas")
    cap = f.fit_cap(NAME, 21.0, nx1 - nx0, tracking=0.6)
    name = f.text(NAME, cap, (nx0 + nx1) / 2, 3.0, tracking=0.6)
    bx0, by0, bx1, by1 = name.bounds()
    underline = A.rect(bx0, by0 - 5.4, bx1, by0 - 4.0)
    raised = [(gap, A.WHITE), (moon_star, A.WHITE), (name, A.WHITE), (underline, A.RED)]
    return outline, left, gap, raised, cap


def chamfered(cs, height):
    """Katmanlara oturan pahlı gövde: ilk katman FOOT içe çekik, üst CHAMFER pah (anahtarlıklardaki gibi)."""
    body = cs.extrude(height)
    steps = int(round(A.CHAMFER / A.LAYER))
    cuts = [(cs - cs.offset(-A.FOOT, m3.JoinType.Round), -0.1, A.LAYER)]
    for k in range(steps):
        z0 = height - (steps - k) * A.LAYER
        top = height + 0.1 if k == steps - 1 else z0 + A.LAYER
        cuts.append((cs - cs.offset(-A.CHAMFER * (k + 1) / steps, m3.JoinType.Round), z0, top))
    rings = [ring.extrude(z1 - z0).translate((0, 0, z0)) for ring, z0, z1 in cuts]
    body = body - m3.Manifold.batch_boolean(rings, m3.OpType.Add)
    return m3.Manifold.batch_boolean([p for p in body.decompose() if p.volume() > 1.0], m3.OpType.Add)


ROT_Y = [[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0]]   # uzun kenar tablada y yönüne


class Block:
    key = "capraz_blok"
    title = "FIRAT_TUYGUN_capraz_blok"

    def __init__(self):
        self.outline, self.left, self.gap, self.raised, self.cap = layout()
        # 2B kontroller için anahtarlık Design sınıfı (kabartmaları kenardan 1 mm içeride tutar)
        self.check2d = A.Design(self.key, self.title, self.outline, self.raised)

    def flat_parts(self):
        """Baskı yönünde (ön yüz yukarıda, z = D) parçalar, döndürülmeden."""
        body = chamfered(self.outline, D)
        clean = lambda m: m3.Manifold.batch_boolean([p for p in m.decompose() if p.volume() > 0.5],  # noqa: E731
                                                    m3.OpType.Add)                # kesimden kalan sıfır hacimli artıkları at
        red_body = clean(body ^ self.left.extrude(D + 2).translate((0, 0, -1)))
        black_body = clean(body - red_body)
        raised = self.check2d.raised_parts()
        top = lambda cs: cs.extrude(RAISE).translate((0, 0, D))  # noqa: E731
        red = red_body + top(raised[A.RED]) if A.RED in raised else red_body
        return [("Gövde (siyah)", black_body, A.BLACK), ("Gövde ve alt çizgi (kırmızı)", red, A.RED),
                ("Ön yüz (beyaz)", top(raised[A.WHITE]), A.WHITE)]

    def solids(self):
        return [(n, m.transform(ROT_Y), e) for n, m, e in self.flat_parts()]

    def size(self):
        return W, H


def standing(man):
    """Baskı yönündeki parçayı masada duruş yönüne çevirir: ön yüz -y'ye bakar, yükseklik z."""
    return man.transform([[1, 0, 0, 0], [0, 0, -1, D], [0, 1, 0, H / 2]])


def estimate_grams(parts):
    """Kabaca filament tahmini: 2 duvar (0,84 mm), üst 5 / alt 3 katman, %15 dolgu, PLA 1,24 g/cm³."""
    out = {}
    for name, man, ext in parts:
        vol = man.volume()
        shell = man.surface_area() * 0.84
        printed = min(vol, shell) + 0.15 * max(0.0, vol - shell)
        out[ext] = out.get(ext, 0.0) + printed * 1.24 / 1000.0
    return out


def preview(block, parts, path):
    stand = [(*A.mesh_arrays(standing(m)), A.SHOW[e]) for _, m, e in parts]
    flat = [(*A.mesh_arrays(m.transform(ROT_Y)), A.SHOW[e]) for _, m, e in parts]
    front = A.fit_into(render(stand, 1300, rotation(0, -90), margin=0.02), 640, 300)
    iso = A.fit_into(render(stand, 1300, rotation(-26, -70), margin=0.02), 640, 300)
    bed = A.fit_into(render(flat, 900, rotation(-35, -55), margin=0.02), 300, 300)
    Wc, Hc = 1400, 820
    canvas = Image.new("RGB", (Wc, Hc), (236, 239, 244))
    dr = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(os.path.join(A.FONT_DIR, "Lexend-ExtraBold.ttf"), 30)
    fs = ImageFont.truetype(os.path.join(A.FONT_DIR, "Lexend-ExtraBold.ttf"), 19)
    boxes = [(front, "Önden", (30, 90, 700, 440)), (iso, "Masada (3/4 açı)", (720, 90, 1370, 440)),
             (bed, "Tablada (ön yüz yukarı, boylamasına)", (30, 460, 700, 800))]
    for im, label, (x0, y0, x1, y1) in boxes:
        dr.rounded_rectangle((x0, y0, x1, y1), 22, fill=(146, 153, 166))
        canvas.paste(im, (x0 + (x1 - x0 - im.width) // 2, y0 + 20 + (y1 - y0 - 20 - im.height) // 2), im)
        dr.text((x0 + 16, y0 + 8), label, fill=(236, 239, 244), font=fs)
    dr.text((30, 20), "ÇAPRAZ BLOK – BASKIYA HAZIR", fill=(30, 33, 40), font=f)
    dr.text((30, 58), f"{W:.0f} × {D + RAISE:.0f} × {H:.0f} mm  ·  isim Bebas Neue {block.cap:.1f} mm  ·  "
                      f"kabartma {RAISE:.1f} mm  ·  kırmızı + siyah + beyaz",
            fill=(80, 86, 98), font=fs)
    grams = estimate_grams(parts)
    lines = ["Baskı bilgisi (yaklaşık):"] + [f"  {A.COLOUR_NAMES[e]}: ~{g:.0f} g" for e, g in sorted(grams.items())] + [
        f"  toplam: ~{sum(grams.values()):.0f} g", "", "AMS sırası: 1 = siyah, 2 = beyaz, 3 = kırmızı",
        f"Destek: yok   ·   Kabartma {RAISE:.1f} mm: yalnız son {round(RAISE / A.LAYER)} katman",
        "Kırmızı ve siyah ayrı nozullarda (atıksız)"]
    for i, t in enumerate(lines):
        dr.text((740, 480 + i * 34), t, fill=(40, 44, 52), font=fs)
    canvas.save(path)


def main():
    block = Block()
    thin, gaps, _ = block.check2d.check()
    pairs = block.check2d.check_pairs()
    template = zipfile.ZipFile(A.TEMPLATE)
    template_files = {n: template.read(n) for n in template.namelist()}
    os.makedirs(os.path.join(OUT_DIR, "onizleme"), exist_ok=True)
    path, _, filaments = A.write_design(block, template_files, OUT_DIR)
    parts = block.flat_parts()
    mans = [m for _, m, _ in parts]
    union = m3.Manifold.batch_boolean(mans, m3.OpType.Add)
    overlap = max((mans[i] ^ mans[j]).volume() for i in range(len(mans)) for j in range(i + 1, len(mans)))
    bb = union.transform(ROT_Y).bounding_box()
    print(f"{os.path.relpath(path, A.ROOT)}  renkler: {'+'.join(A.COLOUR_NAMES[f] for f in filaments)}  isim {block.cap:.1f} mm")
    print(f"  ince<{A.MIN_FEATURE}mm: {thin.area():.1f} mm²  dar boşluk<{A.MIN_GAP}mm: {gaps.area():.1f} mm²  "
          f"yakın öğe: {pairs or 'yok'}")
    print(f"  sağlam: {all(str(m.status()).endswith('NoError') for m in mans)}  örtüşme: {overlap:.3f} mm³  "
          f"tek gövde: {len(union.decompose()) == 1}")
    print(f"  tablada (merkez 128,128): x {bb[0] + 128:.1f}..{bb[3] + 128:.1f}  y {bb[1] + 128:.1f}..{bb[4] + 128:.1f}  "
          f"z {bb[2]:.1f}..{bb[5]:.1f}")
    print("  yaklaşık filament:", {A.COLOUR_NAMES[e]: round(g) for e, g in estimate_grams(parts).items()})
    preview(block, parts, os.path.join(OUT_DIR, "onizleme", "capraz_blok_baski.png"))


if __name__ == "__main__":
    main()
