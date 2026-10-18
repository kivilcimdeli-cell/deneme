"""BMW yuvarlak amblemi – tişört için ince, esnek, çok renkli yama: baskıya hazır Bambu Lab X2D 3MF.

Logo Simple Icons'tan (`scripts/logolar/bmw.svg`, CC0). Tek renkli simgeden renk bölgeleri çıkarılır:
  * beyaz : dış ince halka, B-M-W harfleri, iç ince halka, sağ üst ve sol alt çeyrek
  * siyah : harflerin dışındaki geniş halka
  * mavi  : sol üst ve sağ alt çeyrek
Her renk kalınlığın tamamı boyunca sürer (0,6 mm = 3 katman); iki yüzde de logo görünür, üst yüz doğru yönde.

Tül sandviç: ilk katmandan sonra baskı durur (dosyada hazır), logonun üstüne tül serilir, kalan 2 katman tülün
içinden ilk katmana kaynar. Tül plastiğin içinde kalır: yama esner ve kenarından tişörte dikilir.

Çıktı : bmw_logo/bmw_logo_tisort.3mf, bmw_logo/onizleme.png

Kullanım:
  pip install svgelements
  python3 scripts/bmw_logo.py
"""
import os
import re
import sys
import zipfile

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
from anahtarlik_kurumsal_kucuk import TOWER_MARGIN, X_AUX, tower_size  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "bmw_logo")
SVG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logolar", "bmw.svg")
D = 80.0                          # çap (göğüs logosu); Bambu Studio'da yalnız X-Y ölçeklenirse kalınlık korunur
LAYERS = 3
H = LAYERS * A.LAYER              # 0,6 mm
PAUSE_Z = 2 * A.LAYER             # 2. katmandan (z 0,4) önce dur: tül ser
TULLE = 110.0                     # önerilen tül parçası (kare, mm)
SEG = 360
# simgedeki daire yarıçapları (24 birimlik görüntü kutusu)
R_OUT, R_RING, R_INNER, R_QUAD = 12.0, 11.219, 7.115, 6.185
TOWER, TOWER_BRIM = tower_size(n_fil=3, prime=45.0, change_len=10.0, height=H)


def svg_fill():
    """Simgenin dolu bölgesi (NonZero), merkez (0, 0), y yukarı, çap D."""
    import svgelements as se
    k = D / 24.0
    loops = []
    for sp in se.Path(re.search(r' d="([^"]+)"', open(SVG).read()).group(1)).as_subpaths():
        pts = []
        for seg in se.Path(sp):
            if isinstance(seg, se.Move):
                continue
            if isinstance(seg, (se.Line, se.Close)):
                pts.append((seg.end.x, seg.end.y))
            else:
                pts += [(seg.point(t).x, seg.point(t).y) for t in np.linspace(0, 1, 24)[1:]]
        if len(pts) > 2:
            loops.append([((x - 12.0) * k, (12.0 - y) * k) for x, y in pts])
    return m3.CrossSection(loops, m3.FillRule.NonZero)


def regions():
    """Renk bölgeleri: {renk: CrossSection}."""
    k = D / 24.0
    circ = lambda r: A.circle(r * k, 0, 0, SEG)  # noqa: E731
    fill = svg_fill()
    letters = fill ^ (circ(10.9) - circ(7.4))                  # harfler halkanın ortasında (r 7,7..10,6)
    blue = fill ^ circ(R_QUAD)                                 # simgede dolu çeyrekler = mavi
    black = (circ(R_RING) - circ(R_INNER)) - letters
    white = (circ(R_OUT) - circ(R_RING)) + letters + (circ(R_INNER) - circ(R_QUAD)) + (circ(R_QUAD) - blue)
    clean = lambda cs: A.union(*[p for p in cs.decompose() if p.area() > 0.2])  # noqa: E731
    return {A.WHITE: clean(white), A.BLACK: clean(black), A.BLUE: clean(blue)}


class Logo:
    key = "bmw_logo_tisort"
    title = "BMW_logo_tisort"

    def __init__(self):
        self.regions = regions()
        # siyah ana nozulda (doğrudan sürücü); beyaz ve mavi yardımcı nozulda (her katmanda tek değişim)
        self.nozzle_map = {A.BLACK: 1, A.WHITE: 2, A.BLUE: 2}
        self.filament_profiles = {A.BLACK: A.GENERIC_PLA, A.WHITE: A.GENERIC_PLA}
        self.object_settings = {"enable_support": "0"}
        self.pause_at = PAUSE_Z
        tx = round(A.BED_CENTER[0] + TULLE / 2 + 12.0, 2)        # kule tülün dışında, sağda
        ty = round(A.BED_CENTER[1] - TOWER / 2, 2)
        self.tower_xy = (tx, ty)
        self.project_overrides = {"curr_bed_type": "Textured PEI Plate",
                                  "wipe_tower_x": [f"{tx:g}"], "wipe_tower_y": [f"{ty:g}"]}

    def solids(self):
        names = {A.WHITE: "Beyaz (harfler, halkalar, çeyrekler)", A.BLACK: "Siyah halka", A.BLUE: "Mavi çeyrekler"}
        return [(names[c], self.regions[c].extrude(H), c) for c in (A.BLACK, A.WHITE, A.BLUE)]

    def size(self):
        return D, D


def checks(logo):
    """En ince çizgi ve en dar boşluk (0,4 nozul: çizgi ≥ 0,8, boşluk ≥ 0,5 mm), kule ve tül yeri."""
    out = {}
    for c, cs in logo.regions.items():
        thin = cs - cs.offset(-0.4, m3.JoinType.Round).offset(0.4, m3.JoinType.Round)
        out[A.COLOUR_NAMES[c]] = round(100 * sum(p.area() for p in thin.decompose() if p.area() > 0.05) / cs.area(), 2)
    tx, ty = logo.tower_xy
    lim = 256 - TOWER - TOWER_MARGIN - TOWER_BRIM
    allowed = TOWER_MARGIN <= tx <= lim and TOWER_MARGIN <= ty <= lim and tx - TOWER_BRIM >= X_AUX
    tulle_x1 = A.BED_CENTER[0] + TULLE / 2
    return (f"0,8 mm'den ince kısım (%): {out}  ·  kule {TOWER:.1f} mm ({tx:g}, {ty:g}), Bambu sınırında: {allowed}, "
            f"tülün kenarına {tx - TOWER_BRIM - tulle_x1:.1f} mm")


def preview(logo, parts, path):
    shaded = [(*A.mesh_arrays(m), A.SHOW[e]) for _, m, e in parts]
    face = A.fit_into(render(shaded, 1100, A.R_TOP, flat=0.85, margin=0.02), 520, 520)
    cx, cy = A.BED_CENTER
    bed = m3.Manifold.cube((256, 256, 0.2)).translate((0, 0, -0.4))
    tx, ty = logo.tower_xy
    tower = m3.Manifold.cube((TOWER, TOWER, 1.0)).translate((tx, ty, 0))
    t0, t1, w = cx - TULLE / 2, cx + TULLE / 2, 1.2
    frame = A.union(A.rect(t0, t0, t1, t0 + w), A.rect(t0, t1 - w, t1, t1), A.rect(t0, t0, t0 + w, t1),
                    A.rect(t1 - w, t0, t1, t1)).extrude(0.05).translate((0, 0, H + 0.5))
    items = [(*A.mesh_arrays(bed), (205, 208, 214)), (*A.mesh_arrays(tower), (150, 156, 168)),
             (*A.mesh_arrays(frame), (225, 70, 140))]
    items += [(*A.mesh_arrays(m.translate((cx, cy, 0))), A.SHOW[e]) for _, m, e in parts]
    plate = A.fit_into(render(items, 1000, A.R_TOP, flat=0.8, margin=0.02), 520, 520)
    canvas = Image.new("RGB", (1240, 740), (236, 239, 244))
    dr = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(os.path.join(A.FONT_DIR, "Lexend-ExtraBold.ttf"), 30)
    fs = ImageFont.truetype(os.path.join(A.FONT_DIR, "Lexend-ExtraBold.ttf"), 19)
    for im, label, (x0, y0, x1, y1) in ((face, f"Logo (üstten) – Ø{D:.0f} mm, {H:.1f} mm kalın", (30, 130, 610, 720)),
                                        (plate, "Tabla: pembe çerçeve = tül yeri, gri = prime kulesi",
                                         (630, 130, 1210, 720))):
        dr.rounded_rectangle((x0, y0, x1, y1), 22, fill=(146, 153, 166))
        canvas.paste(im, (x0 + (x1 - x0 - im.width) // 2, y0 + 30 + (y1 - y0 - 30 - im.height) // 2), im)
        dr.text((x0 + 16, y0 + 8), label, fill=(236, 239, 244), font=fs)
    dr.text((30, 18), "BMW LOGOSU – TİŞÖRT İÇİN İNCE YAMA (X2D)", fill=(30, 33, 40), font=f)
    dr.text((30, 58), f"3 katman (0,6 mm), renkler boydan boya · 1. katmandan sonra durur: tülü ser, devam et · "
                      "destek yok", fill=(80, 86, 98), font=fs)
    dr.text((30, 88), "AMS: 1 siyah · 2 beyaz · 3 mavi   ·   siyah: ana nozul, beyaz + mavi: yardımcı nozul",
            fill=(22, 120, 60), font=fs)
    canvas.save(path)


def main():
    logo = Logo()
    template = zipfile.ZipFile(A.TEMPLATE)
    template_files = {n: template.read(n) for n in template.namelist()}
    os.makedirs(OUT_DIR, exist_ok=True)
    path, _, filaments = A.write_design(logo, template_files, OUT_DIR)
    parts = logo.solids()
    mans = [m for _, m, _ in parts]
    overlap = max((mans[i] ^ mans[j]).volume() for i in range(len(mans)) for j in range(i + 1, len(mans)))
    union = m3.Manifold.batch_boolean(mans, m3.OpType.Add)
    print(f"{os.path.relpath(path, A.ROOT)}  Ø{D:.0f} × {H:.1f} mm  AMS: {', '.join(A.COLOUR_NAMES[f] for f in filaments)}")
    print(f"  sağlam: {all(str(m.status()).endswith('NoError') for m in mans)}  örtüşme: {overlap:.4f} mm³  "
          f"tek gövde: {len(union.decompose()) == 1}  hacim: {union.volume():.0f} mm³ (dolu disk "
          f"{np.pi * (D / 2) ** 2 * H:.0f})")
    print("  " + checks(logo))
    preview(logo, parts, os.path.join(OUT_DIR, "onizleme.png"))


if __name__ == "__main__":
    main()
