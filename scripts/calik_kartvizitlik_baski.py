"""ÇALIK OTO LASTİK – müşterinin seçtiği kartvizitlik (6 · Lastik yanaklı): baskıya hazır Bambu Lab X2D 3MF.

Müşteri isteği: biraz büyük olsun, kartlar kesin sığsın; cep, kart eninin 1 cm üstünde.
  * Kart cebi 100 mm geniş: yaygın kartlar 85 × 55 ve 90 × 50 mm, en genişi 90 mm + 1 cm (85'lik kartta iki yanda
    7,5 mm boşluk). Diğer ölçüler öneriden %10 büyük: lastik Ø61,6 mm, cep tabanda ~25 mm derin (~60 kart),
    arka sırt 48 mm (55 mm'lik kartın üstü dışarıda kalır, kolay alınır), ön dudak 15,4 mm.
  * Dış ölçü 114 × 61,6 × 59,4 mm (jantlarla 116); yan yanaklar 7 mm, diş izli lastik biçiminde, altı dolu (alt yay
    desteksiz basılır).
  * Sarı: iki yanda jant (5 bijon deliği ve göbek), önde ÇALIK OTO LASTİK (Saira Condensed Black; harf içi ve
    aralar ≥ 0,85 mm, dik yüzeyde dolmaz); 1 mm kabartma.
  * Tabana oturarak dik basılır (önizlemedeki gibi), destek gerekmez; en dik çıkıntı 45°'nin altında.
  * Nozullar: siyah ana nozulda, sarı yardımcı nozulda. AMS 1 siyah, 2 sarı. Yazılı katmanlarda filament değişmez,
    yalnız nozul değişir (kule).
  * Bambu standart profili (0,20 mm Standard @BBL X2D): ütüleme kapalı, destek kapalı, tabla Textured PEI.

Çıktı : calik_isimlik/kartvizitlik/baski/calik_kartvizitlik_x2d.3mf, onizleme.png

Kullanım:
  python3 scripts/calik_kartvizitlik_baski.py
"""
import json
import os
import sys
import zipfile

import manifold3d as m3
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import calik_kartvizitlik as KV  # noqa: E402
import masa_isimligi_yeni as Y  # noqa: E402
import uzar_isimlik_baski as B  # noqa: E402
from anahtarlik_kurumsal_kucuk import TOWER_MARGIN, X_AUX, tower_size  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(KV.OUT_DIR, "baski")
W_IN, K, CHEEK = 100.0, 1.1, 7.0                   # kart cebi, büyütme katı, yan yanak
CENTER = (128.0, 112.0)                            # nesne merkezi (tabla)
GAP = 8.0                                          # nesne ile kule arası


class Plate:
    key = "calik_kartvizitlik_x2d"
    title = "CALIK_OTO_LASTIK_kartvizitlik"

    def __init__(self):
        self.model = KV.k6_lastik(W_IN, K, CHEEK)
        parts = self.model.parts()
        b = m3.Manifold.batch_boolean([m for _, m, _ in parts], m3.OpType.Add).bounding_box()
        self.shift = (-(b[0] + b[3]) / 2, -(b[1] + b[4]) / 2)
        self.height = b[5]
        self.tower, self.brim = tower_size(n_fil=2, prime=45.0, change_len=10.0, height=self.height)
        depth = b[4] - b[1]
        self.tower_xy = (CENTER[0] - self.tower / 2, CENTER[1] + depth / 2 + GAP + self.brim)
        self.instances = [(*CENTER, 0)]
        self.nozzle_map = {A.BLACK: 1, A.YELLOW: 2}
        self.filament_profiles = {A.BLACK: A.GENERIC_PLA, A.YELLOW: A.GENERIC_PLA}
        self.object_settings = {"enable_support": "0", "ironing_type": "no ironing"}
        self.project_overrides = {"curr_bed_type": "Textured PEI Plate",
                                  "wipe_tower_x": [f"{self.tower_xy[0]:g}"], "wipe_tower_y": [f"{self.tower_xy[1]:g}"]}

    def solids(self):
        """Nesne merkezi (0, 0), tabanı z = 0: gövde (siyah) ve sarı kabartma."""
        dx, dy = self.shift
        names = {A.BLACK: "Gövde (siyah)", A.YELLOW: "Jant ve yazı (sarı)"}
        return [(names[c], m.translate((dx, dy, 0)), c) for _, m, c in self.model.parts()]

    def size(self):
        b = m3.Manifold.batch_boolean([m for _, m, _ in self.solids()], m3.OpType.Add).bounding_box()
        return b[3] - b[0], b[4] - b[1]


def checks(plate, parts):
    """Nesne iki nozulun ortak alanında; kule Bambu'nun izin verdiği yerde ve nesneden uzak."""
    x, y, _ = plate.instances[0]
    b = m3.Manifold.batch_boolean([m for _, m, _ in parts], m3.OpType.Add).bounding_box()
    box = (b[0] + x, b[1] + y, b[3] + x, b[4] + y)
    inside = box[0] >= X_AUX and box[1] >= 0 and box[2] <= 256 and box[3] <= 256
    tx, ty = plate.tower_xy
    lim = 256 - plate.tower - TOWER_MARGIN - plate.brim
    allowed = TOWER_MARGIN <= tx <= lim and TOWER_MARGIN <= ty <= lim and tx - plate.brim >= X_AUX
    tower = (tx - plate.brim, ty - plate.brim, tx + plate.tower + plate.brim, ty + plate.tower + plate.brim)
    clear = max(tower[0] - box[2], box[0] - tower[2], tower[1] - box[3], box[1] - tower[3])
    ok = inside and allowed and clear >= 5.0
    return ok, (f"nesne iki nozulun ortak alanında: {inside} (x {box[0]:.1f}..{box[2]:.1f}, y {box[1]:.1f}..{box[3]:.1f}), "
                f"kule {plate.tower:.1f} mm ({tx:.1f}, {ty:.1f}), Bambu sınırında: {allowed}, nesneye {clear:.1f} mm")


def preview(plate, parts, path, info, title):
    bed = m3.Manifold.cube((256, 256, 0.2)).translate((0, 0, -0.4))
    tx, ty = plate.tower_xy
    tower = m3.Manifold.cube((plate.tower, plate.tower, plate.height)).translate((tx, ty, 0))
    x, y, _ = plate.instances[0]
    on_bed = [(*A.mesh_arrays(bed), (205, 208, 214)), (*A.mesh_arrays(tower), (150, 156, 168))]
    on_bed += [(*A.mesh_arrays(m.translate((x, y, 0))), KV.SHOW[c]) for _, m, c in parts]
    bed_im = A.fit_into(render(on_bed, 1000, A.R_TOP, flat=0.75, margin=0.02), 440, 440)
    dx, dy = plate.shift
    with_cards = [(*A.mesh_arrays(m), KV.SHOW[c]) for _, m, c in parts]
    with_cards.append((*A.mesh_arrays(plate.model.stack.translate((dx, dy, 0))), KV.SHOW[KV.CARD]))
    iso = A.fit_into(render(with_cards, 1300, rotation(-30, -64), margin=0.02, **KV.LIGHT), 560, 440)
    side = A.fit_into(render(with_cards, 1100, rotation(-90, -90), margin=0.04, flat=0.85), 380, 440)
    W, H = 1500, 760
    canvas = Image.new("RGB", (W, H), (236, 239, 244))
    dr = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), 32)
    fs = ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), 18)
    boxes = [(bed_im, "Tabla (üstten, gri: prime kulesi)", (30, 230, 500, 740)),
             (iso, "85 × 55 kartlarla (cep 100 mm)", (520, 230, 1100, 740)),
             (side, "Yandan", (1120, 230, 1470, 740))]
    for im, label, (x0, y0, x1, y1) in boxes:
        dr.rounded_rectangle((x0, y0, x1, y1), 22, fill=(146, 153, 166))
        canvas.paste(im, (x0 + (x1 - x0 - im.width) // 2, y0 + 30 + (y1 - y0 - 30 - im.height) // 2), im)
        dr.text((x0 + 16, y0 + 10), label, fill=(236, 239, 244), font=fs)
    dr.text((30, 18), title, fill=(24, 26, 30), font=f)
    for k, line in enumerate(info):
        dr.text((30, 66 + k * 28), line, fill=(22, 120, 60) if k == len(info) - 1 else (70, 74, 84), font=fs)
    canvas.save(path)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    plate = Plate()
    template = zipfile.ZipFile(A.TEMPLATE)
    path, _, filaments = A.write_design(plate, {n: template.read(n) for n in template.namelist()}, OUT_DIR)
    parts = plate.solids()
    mans = [m for _, m, _ in parts]
    overlap = (mans[0] ^ mans[1]).volume()
    ok_place, place = checks(plate, parts)
    inner, gap, thin = B.line_metrics(plate.model.text)
    tb = plate.model.text.bounds()
    clash = (plate.model.stack ^ plate.model.body).volume()
    w, h = plate.size()
    g = {A.COLOUR_NAMES[c]: round(sum(Y.grams(m) for _, m, cc in parts if cc == c), 1) for c in filaments}
    print(f"{os.path.relpath(path, A.ROOT)}  {w:.1f} × {h:.1f} × {plate.height:.1f} mm  AMS: "
          f"{', '.join(A.COLOUR_NAMES[x] for x in filaments)}  nozul: {plate.nozzle_map}")
    print(f"  sağlam: {all(str(m.status()).endswith('NoError') for m in mans)}  örtüşme: {overlap:.4f} mm³  "
          f"parçalar: {[n for n, _, _ in parts]}")
    print(f"  {place} -> {'TAMAM' if ok_place else 'SORUN'}")
    print(f"  ÇALIK OTO LASTİK: en dar iç boşluk {inner:.2f} mm, en dar ara {gap:.2f} mm, 0,8 mm'den ince %{thin}, "
          f"en {tb[2] - tb[0]:.1f} mm, z {tb[1]:.1f}..{tb[3]:.1f} (dudak {14 * K:.1f} mm)")
    print(f"  kart destesi (40 kart, 85 × 55) gövdeye değiyor mu: {clash:.3f} mm³")
    print(f"  tahmini filament: {g}")
    meas = os.path.join(OUT_DIR, "olcum.json")
    when = ""
    if os.path.exists(meas):
        m = json.load(open(meas, encoding="utf-8"))
        g = {k: round(v, 1) for k, v in m["g"].items()}
        when = f" · PrusaSlicer ~{m['sure']}"
        print(f"  ölçüm ({m['kaynak']}): {g}, toplam {m['toplam_g']} g, {m['sure']}")
    info = [f"Kart cebi {W_IN:.0f} mm (90 mm kart + 1 cm) · dış ölçü {w:.0f} × {h:.0f} × {plate.height:.0f} mm · "
            "yanaklar diş izli lastik, iki yanda sarı jant, önde ÇALIK OTO LASTİK (1 mm kabartma)",
            "AMS: 1 siyah (ana nozul) · 2 sarı (yardımcı nozul) · tabana oturarak dik basılır, destek yok",
            "Bambu standart 0,20 mm · ütüleme kapalı · Textured PEI · Generic PLA",
            f"Filament ~{sum(g.values()):.0f} g (siyah {g.get('siyah', 0):.0f}, sarı {g.get('sari', g.get('sarı', 0)):.1f}) "
            f"+ kule{when} · yazı içi en dar {inner:.2f} mm · yerleşim {'tamam' if ok_place else 'SORUN'}"]
    preview(plate, parts, os.path.join(OUT_DIR, "onizleme.png"), info,
            "ÇALIK OTO LASTİK – KARTVİZİTLİK (6 · LASTİK YANAKLI) · X2D BASKI DOSYASI")


if __name__ == "__main__":
    main()
