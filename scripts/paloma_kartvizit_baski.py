"""PALOMA GRIDA – Süleyman Boylu'nun seçtiği kartvizit (3 · Üst bant, beyaz gövde): Bambu Lab X2D 3MF.

Kart 40 × 80 mm (dikey), yüzü yukarı basılır (destek yok): beyaz gövde 1,2 mm; üst 0,4 mm (2 katman) dolgu: mavi bant
ve siyah QR kareleri (QR düz: kabartma gölgesi okumayı bozar); bütün yazılar kabartma (kullanıcı istedi): logo ve GRIDA
bandın boşluğundan beyaz 0,4 mm, görev mavi 0,4 mm, ad soyad siyah 0,8 mm (scripts/paloma_kartvizit.py,
d3_ust_bant_kabartmali). QR kartvizit sayfasını açar (isimlikteki QR'la aynı), 30 mm, kare 0,91 mm.

Nozullar (isimlikteki gibi): beyaz ana nozulda (gövde); siyah ve mavi yardımcı nozulda (yalnız üst 4 katman).
Bambu standart 0,20 mm · ütüleme kapalı · destek kapalı · Textured PEI · Generic PLA; mavi: logonun mavisi (#69A1BA).

İki dosya:
  paloma_kartvizit_x2d_1adet.3mf   tek kart (deneme baskısı)
  paloma_kartvizit_x2d_10adet.3mf  tam tabla: iki sıra beşer kart, prime kulesinin altında
Çıktı : paloma_isimlik/kartvizit/baski/*.3mf, onizleme.png
Kullanım: python3 scripts/paloma_kartvizit_baski.py
"""
import os
import sys
import zipfile

import manifold3d as m3
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paloma_kartvizit as PK  # noqa: E402
from anahtarlik_kurumsal_kucuk import X_AUX  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

A, B, Q, PI = PK.A, PK.B, PK.Q, PK.PI
OUT = os.path.join(PK.OUT, "baski")
A.COLOURS[A.BLUE] = "#69A1BA"                   # projedeki mavi filament: logonun mavisi
B.SHOW[A.BLUE] = PI.PALOMA_BLUE
ON_ADET = [(x, y, 0) for y in (52.0, 140.0) for x in (46.0, 92.0, 138.0, 184.0, 230.0)]


class Plate:
    def __init__(self, adet):
        self.key = f"paloma_kartvizit_x2d_{adet}adet"
        self.title = f"PALOMA_GRIDA_Suleyman_Boylu_kartvizit_40x80_{adet}adet"
        self.instances = [(138.0, 100.0, 0)] if adet == 1 else ON_ADET
        self.kart = PK.d3_ust_bant_kabartmali(PI.WHITE_SC, 3)
        self.parts = PK.katilar(self.kart)
        self.nozzle_map = {A.WHITE: 1, A.BLACK: 2, A.BLUE: 2}
        self.filament_profiles = {c: A.GENERIC_PLA for c in (A.WHITE, A.BLACK, A.BLUE)}
        self.object_settings = {"enable_support": "0", "ironing_type": "no ironing"}
        self.tower_xy = B.TOWER_XY
        self.project_overrides = {"curr_bed_type": "Textured PEI Plate",
                                  "wipe_tower_x": [f"{B.TOWER_XY[0]:g}"], "wipe_tower_y": [f"{B.TOWER_XY[1]:g}"]}

    def solids(self):
        """Bir kart, nesne merkezi (0, 0), yüzü yukarı."""
        b = m3.Manifold.batch_boolean([m for _, m, _ in self.parts], m3.OpType.Add).bounding_box()
        dx, dy = -(b[0] + b[3]) / 2, -(b[1] + b[4]) / 2
        return [(n, m.translate((dx, dy, -b[2])), c) for n, m, c in self.parts]

    def size(self):
        b = m3.Manifold.batch_boolean([m for _, m, _ in self.solids()], m3.OpType.Add).bounding_box()
        return b[3] - b[0], b[4] - b[1]


def yerlesim(plate):
    w, h = plate.size()
    boxes = [(x - w / 2, y - h / 2, x + w / 2, y + h / 2) for x, y, _ in plate.instances]
    tx, ty = plate.tower_xy
    tower = (tx - B.TOWER_BRIM, ty - B.TOWER_BRIM, tx + B.TOWER + B.TOWER_BRIM, ty + B.TOWER + B.TOWER_BRIM)
    sep = lambda a, b: max(b[0] - a[2], a[0] - b[2], b[1] - a[3], a[1] - b[3])  # noqa: E731
    inside = all(b[0] >= X_AUX and b[1] >= 0 and b[2] <= 256 and b[3] <= 256 for b in boxes)
    arasi = min((sep(a, b) for i, a in enumerate(boxes) for b in boxes[i + 1:]), default=99.0)
    kule = min(sep(tower, b) for b in boxes)
    return inside and arasi >= 4.0 and kule >= 5.0, f"ortak alanda {inside}, kartlar arası {arasi:.1f} mm, kuleye {kule:.1f} mm"


def onizleme(plates, path):
    show = lambda items: [(*A.mesh_arrays(m), B.SHOW[c]) for _, m, c in items]  # noqa: E731
    p = plates[-1]
    parts = p.solids()
    bed = m3.Manifold.cube((256, 256, 0.2)).translate((0, 0, -0.4))
    tx, ty = p.tower_xy
    tower = m3.Manifold.cube((B.TOWER, B.TOWER, 6.0)).translate((tx, ty, 0))
    on_bed = [(*A.mesh_arrays(bed), (205, 208, 214)), (*A.mesh_arrays(tower), (150, 156, 168))]
    on_bed += [(*A.mesh_arrays(m.translate((x, y, 0))), B.SHOW[c]) for x, y, _ in p.instances for _, m, c in parts]
    bed_im = A.fit_into(render(on_bed, 1000, A.R_TOP, flat=0.75, margin=0.02), 460, 460)
    face = A.fit_into(render(show(parts), 1400, A.R_TOP, ambient=0.85, margin=0.03), 300, 470)
    tilt = A.fit_into(render(show(parts), 1400, rotation(-24, -58), margin=0.02), 420, 470)
    W, H = 1400, 700
    c = Image.new("RGB", (W, H), (236, 239, 244))
    dr = ImageDraw.Draw(c)
    f = ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), 32)
    fs = ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), 19)
    dr.text((30, 18), "PALOMA GRIDA – SÜLEYMAN BOYLU · KARTVİZİT 40 × 80 mm (3 · ÜST BANT) · X2D", font=f,
            fill=(24, 26, 30))
    for k, line in enumerate(["Beyaz gövde 1,2 mm + 0,4 mm dolgu (mavi bant, düz QR) · kabartma: logo, GRIDA ve görev "
                              "0,4 mm, ad soyad 0,8 mm; en kalın yer 2,0 mm",
                              "AMS: beyaz (ana nozul, gövde ve logo) · siyah ve mavi (yardımcı nozul, yalnız üst katmanlar) · "
                              "Bambu 0,20 mm · destek yok · ütüleme yok · Textured PEI",
                              "Dosyalar: 1 adet (deneme) ve 10 adet (tam tabla, iki sıra beşer)"]):
        dr.text((30, 66 + k * 28), line, fill=(70, 74, 84), font=fs)
    for im, label, (x0, y0, x1, y1) in [(bed_im, "Tabla, 10 adet (gri: prime kulesi)", (30, 170, 520, 680)),
                                         (face, "Kart, üstten", (540, 170, 880, 680)),
                                         (tilt, "Kart, eğik (kabartma)", (900, 170, 1370, 680))]:
        dr.rounded_rectangle((x0, y0, x1, y1), 22, fill=(146, 153, 166))
        c.paste(im, (x0 + (x1 - x0 - im.width) // 2, y0 + 30 + (y1 - y0 - 30 - im.height) // 2), im)
        dr.text((x0 + 16, y0 + 8), label, fill=(236, 239, 244), font=fs)
    c.save(path)


def main():
    os.makedirs(OUT, exist_ok=True)
    template = zipfile.ZipFile(A.TEMPLATE)
    files = {n: template.read(n) for n in template.namelist()}
    plates = []
    for adet in (1, 10):
        p = Plate(adet)
        path, _, fil = A.write_design(p, files, OUT)
        ok, msg = yerlesim(p)
        mans = [m for _, m, _ in p.solids()]
        overlap = max((mans[i] ^ mans[j]).volume() for i in range(len(mans)) for j in range(i + 1, len(mans)))
        print(f"{os.path.relpath(path, A.ROOT)}  kart {p.size()[0]:.1f} × {p.size()[1]:.1f} mm  AMS: "
              f"{', '.join(A.COLOUR_NAMES[x] for x in fil)}  nozul {p.nozzle_map}")
        print(f"  {msg} -> {'TAMAM' if ok else 'SORUN'}; örtüşme {overlap:.4f} mm³; parçalar {[n for n, _, _ in p.parts]}")
        plates.append(p)
    k = plates[0]
    print(f"  QR okunuyor: {PK.qr_okunur(k.parts)}; tasarım: {PK.sorunlar(k.kart) or 'sorun yok'}")
    onizleme(plates, os.path.join(OUT, "onizleme.png"))
    print("önizleme:", os.path.relpath(os.path.join(OUT, "onizleme.png"), A.ROOT))


if __name__ == "__main__":
    main()
