"""Çapraz blok + 12° eğik sehpası: tek tablada, baskıya hazır Bambu Lab X2D 3MF.

Blok (240 × 56 × 32 mm) ön yüzü yukarıda yatık, sehpa dik (düz tabanı tablada); ikisi de boylamasına (y yönünde),
yan yana. Destek gerekmez.

Nozullar elle sabit:
  * Siyah ve beyaz ana nozulda (doğrudan sürücü). Beyaz yalnız son 10 katmanda (kabartma): tüm baskıda tek
    filament değişimi (siyah -> beyaz).
  * Kırmızı yardımcı nozulda (Bowden). Siyah ile kırmızı her katmanda birlikte basılır; ayrı nozulda oldukları
    için katman başına temizleme yok.
Elas PLA Pro (siyah, beyaz) için Generic PLA profili (anahtarlıkla aynı); kırmızı Bambu PLA Basic. Baskı ayarları
Bambu standart profili; dosyadan yalnız tabla tipi (Textured PEI) ve kule yeri gelir.

Çıktı : masa_isimligi/capraz_blok_sehpa.3mf, masa_isimligi/onizleme/capraz_blok_sehpa_tabla.png

Kullanım:
  python3 scripts/capraz_blok_sehpa.py
"""
import os
import sys
import zipfile

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import capraz_blok as CB  # noqa: E402
import masa_isimligi_yeni as Y  # noqa: E402
from anahtarlik_kurumsal_kucuk import TOWER_MARGIN, X_AUX, tower_size  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "masa_isimligi")
GAP = 12.0                                   # blok ile sehpa arası (mm)
HEIGHT = CB.D + CB.RAISE                     # en yüksek parça: blok, ön yüz kabartmasıyla 34 mm
TOWER, TOWER_BRIM = tower_size(n_fil=3, prime=45.0, change_len=10.0, height=HEIGHT)


class Plate:
    key = "capraz_blok_sehpa"
    title = "FIRAT_TUYGUN_capraz_blok_sehpa"

    def __init__(self):
        self.block = CB.Block()
        self.stand, self.h_f = Y.block_stand(CB.D)
        self.nozzle_map = {A.BLACK: 1, A.WHITE: 1, A.RED: 2}
        self.filament_profiles = {A.BLACK: A.GENERIC_PLA, A.WHITE: A.GENERIC_PLA}
        self.object_settings = {"enable_support": "0"}   # şablonda açık; sistem profili kapalı, garanti olsun
        parts = self.solids()
        boxes = [m.bounding_box() for _, m, _ in parts]
        x1 = max(b[3] for b in boxes) + A.BED_CENTER[0]
        # kule sehpanın sağında, ortada; Bambu kuleyi kenardan 15 mm içeride tutar
        tx = round(x1 + TOWER_BRIM + 8.0, 2)
        ty = round(A.BED_CENTER[1] - TOWER / 2, 2)
        self.tower_xy = (tx, ty)
        self.project_overrides = {"curr_bed_type": "Textured PEI Plate",
                                  "wipe_tower_x": [f"{tx:g}"], "wipe_tower_y": [f"{ty:g}"]}

    def solids(self):
        """Tablada, nesne merkezi (0, 0): blok (ön yüz yukarı) solda, sehpa sağda, ikisi de boylamasına."""
        parts = self.block.solids()
        stand = self.stand.transform(CB.ROT_Y)
        bb = m3.Manifold.batch_boolean([m for _, m, _ in parts], m3.OpType.Add).bounding_box()
        sb = stand.bounding_box()
        stand = stand.translate((bb[3] + GAP - sb[0], (bb[1] + bb[4]) / 2 - (sb[1] + sb[4]) / 2, -sb[2]))
        parts.append(("Sehpa (siyah)", stand, A.BLACK))
        allb = m3.Manifold.batch_boolean([m for _, m, _ in parts], m3.OpType.Add).bounding_box()
        dx, dy = -(allb[0] + allb[3]) / 2, -(allb[1] + allb[4]) / 2
        return [(n, m.translate((dx, dy, 0)), e) for n, m, e in parts]

    def size(self):
        b = m3.Manifold.batch_boolean([m for _, m, _ in self.solids()], m3.OpType.Add).bounding_box()
        return b[3] - b[0], b[4] - b[1]


def checks(plate, parts):
    """Parçalar iki nozulun ortak alanında mı, kule Bambu'nun izin verdiği yerde ve parçalardan uzak mı."""
    cx, cy = A.BED_CENTER
    boxes = [(b[0] + cx, b[1] + cy, b[3] + cx, b[4] + cy) for b in (m.bounding_box() for _, m, _ in parts)]
    inside = all(b[0] >= X_AUX and b[1] >= 0 and b[2] <= 256 and b[3] <= 256 for b in boxes)
    tx, ty = plate.tower_xy
    lim = 256 - TOWER - TOWER_MARGIN - TOWER_BRIM
    allowed = TOWER_MARGIN <= tx <= lim and TOWER_MARGIN <= ty <= lim and tx - TOWER_BRIM >= X_AUX
    tower = (tx - TOWER_BRIM, ty - TOWER_BRIM, tx + TOWER + TOWER_BRIM, ty + TOWER + TOWER_BRIM)
    sep = lambda a, b: max(b[0] - a[2], a[0] - b[2], b[1] - a[3], a[1] - b[3])  # noqa: E731
    clear = min(sep(tower, b) for b in boxes)
    gap = sep(boxes[0], boxes[-1])
    ok = inside and allowed and clear >= 5.0
    return (f"parçalar ortak alanda: {inside} (x {min(b[0] for b in boxes):.1f}..{max(b[2] for b in boxes):.1f}, "
            f"y {min(b[1] for b in boxes):.1f}..{max(b[3] for b in boxes):.1f}), blok-sehpa arası {gap:.1f} mm, "
            f"kule {TOWER:.1f} mm kare ({tx:g}, {ty:g}), Bambu sınırında: {allowed}, parçalara {clear:.1f} mm "
            f"-> {'TAMAM' if ok else 'SORUN'}")


def preview(plate, parts, path):
    cx, cy = A.BED_CENTER
    bed = m3.Manifold.cube((256, 256, 0.2)).translate((0, 0, -0.4))
    tx, ty = plate.tower_xy
    tower = m3.Manifold.cube((TOWER, TOWER, HEIGHT)).translate((tx, ty, 0))
    on_bed = [(*A.mesh_arrays(bed), (205, 208, 214)), (*A.mesh_arrays(tower), (150, 156, 168))]
    on_bed += [(*A.mesh_arrays(m.translate((cx, cy, 0))), A.SHOW[e]) for _, m, e in parts]
    top = A.fit_into(render(on_bed, 900, A.R_TOP, flat=0.75, margin=0.02), 530, 520)
    iso = A.fit_into(render(on_bed, 1100, rotation(-35, -55), margin=0.02), 720, 560)
    canvas = Image.new("RGB", (1400, 720), (236, 239, 244))
    dr = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(os.path.join(A.FONT_DIR, "Lexend-ExtraBold.ttf"), 30)
    fs = ImageFont.truetype(os.path.join(A.FONT_DIR, "Lexend-ExtraBold.ttf"), 19)
    for im, label, (x0, y0, x1, y1) in ((top, "Tabla (üstten, X2D 256 × 256)", (30, 120, 630, 700)),
                                        (iso, "Tabla (3/4 açı)", (650, 120, 1370, 700))):
        dr.rounded_rectangle((x0, y0, x1, y1), 22, fill=(146, 153, 166))
        canvas.paste(im, (x0 + (x1 - x0 - im.width) // 2, y0 + 20 + (y1 - y0 - 20 - im.height) // 2), im)
        dr.text((x0 + 16, y0 + 8), label, fill=(236, 239, 244), font=fs)
    dr.text((30, 18), "ÇAPRAZ BLOK + SEHPA – TEK TABLA, BASKIYA HAZIR", fill=(30, 33, 40), font=f)
    dr.text((30, 58), "Blok ön yüzü yukarıda yatık, sehpa dik; ikisi de boylamasına. Destek yok. "
                      "Gri: prime kulesi (Bambu tahmini).", fill=(80, 86, 98), font=fs)
    dr.text((30, 86), "AMS: 1 siyah · 2 beyaz · 3 kırmızı   ·   siyah + beyaz: ana nozul, kırmızı: yardımcı nozul",
            fill=(22, 120, 60), font=fs)
    canvas.save(path)


def main():
    plate = Plate()
    template = zipfile.ZipFile(A.TEMPLATE)
    template_files = {n: template.read(n) for n in template.namelist()}
    os.makedirs(os.path.join(OUT_DIR, "onizleme"), exist_ok=True)
    path, _, filaments = A.write_design(plate, template_files, OUT_DIR)
    parts = plate.solids()
    mans = [m for _, m, _ in parts]
    overlap = max((mans[i] ^ mans[j]).volume() for i in range(len(mans)) for j in range(i + 1, len(mans)))
    w, h = plate.size()
    print(f"{os.path.relpath(path, A.ROOT)}  {w:.1f} × {h:.1f} mm  AMS: "
          f"{', '.join(A.COLOUR_NAMES[f] for f in filaments)}")
    print(f"  sağlam: {all(str(m.status()).endswith('NoError') for m in mans)}  örtüşme: {overlap:.4f} mm³  "
          f"parçalar: {[n for n, _, _ in parts]}")
    print("  " + checks(plate, parts))
    preview(plate, parts, os.path.join(OUT_DIR, "onizleme", "capraz_blok_sehpa_tabla.png"))


if __name__ == "__main__":
    main()
