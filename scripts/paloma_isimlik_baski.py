"""PALOMA GRIDA – Süleyman Boylu'nun seçtiği isimlik (3 · Mavi kart, beyaz tabla, logo kartta): Bambu Lab X2D 3MF.

Müşterinin isteği: 3 numara (mavi kart), ama PALOMA HOTELS ve GRIDA mavi kartın içinde; ayrıca "Paloma Grida"
yazılmasın. Sonra: boyu 20 cm, daha ince, biraz daha yüksek: 2:1 dikdörtgen.
  * Panel 200 × 100 mm, gövde 5 mm, köşeler R8, alt ve üst kenar 0,6 mm basamaklı pah. Yüzü yukarı basılır (arkası
    tablada), destek gerekmez.
  * Yazılar kabartma değil, yüzeyle aynı hizada renkli dolgu (0,8 mm = üst 4 katman): beyaz gövde; siyah ad soyad ve
    QR kareleri; mavi kart ve görev. Kartın içindeki logo, çizgi, GRIDA, QR karosu ve KARTVİZİT kartta boşluk:
    tablanın beyazı görünür.
  * QR kartvizit sayfasını açar (https://suleymanboylu.qrsistem.workers.dev), 34 mm, 3. sürüm.
  * Sehpa (beyaz, panelle aynı) aynı tablada: 170 × 40 × 10 mm; panel yuvaya (5,3 mm) 15° eğik oturur, tutkal
    gerekmez. Panel ve sehpa birlikte tablaya bir takım sığar.
  * Nozullar: beyaz ana nozulda (gövde, sehpa); siyah ve mavi yardımcı nozulda (yalnız üst 4 katman).
  * Bambu standart profili (0,20 mm Standard @BBL X2D): ütüleme kapalı, destek kapalı, Textured PEI, Generic PLA.
    Mavi: logonun mavisi (#69A1BA); en yakın açık / çelik mavisi filament.
Diğer ayarlar her zamanki gibi (Uzar, İNCE, Çalık, Soylu; scripts/uzar_isimlik_baski.py).

Çıktı : paloma_isimlik/baski/paloma_isimlik_x2d.3mf, paloma_isimlik/baski/onizleme.png

Kullanım:
  python3 scripts/paloma_isimlik_baski.py
"""
import json
import os
import sys
import zipfile

import manifold3d as m3
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import masa_isimligi_yeni as Y  # noqa: E402
import paloma_isimlik as P  # noqa: E402
import qr_sistemi as Q  # noqa: E402
import uzar_isimlik as I  # noqa: E402
import uzar_isimlik_baski as B  # noqa: E402
from anahtarlik_kurumsal_kucuk import TOWER_MARGIN, X_AUX  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(P.OUT_DIR, "baski")
PW, PH, T = 200.0, 100.0, 5.0            # panel: 20 cm boy, 10 cm yükseklik, 5 mm kalınlık
STAND_LEN = 170.0                        # sehpa boyu (panel iki yanda 15 mm taşar)
QR_SIDE = 34.0
I.PW, I.PH = PW, PH                      # panel çevresi (I.outline), sehpa yuvası ve kontroller bu ölçüyü kullanır
B.T = T                                  # gövde kalınlığı: pah, dolgu cebi, sehpa yuvası (T + 0,3)
A.COLOURS[A.BLUE] = "#69A1BA"            # projedeki mavi filament rengi: logonun mavisi
B.SHOW[A.BLUE] = P.PALOMA_BLUE


class Plate(B.Plate):
    key = "paloma_isimlik_x2d"
    title = "PALOMA_GRIDA_Suleyman_Boylu_isimlik_200x100"
    instances = [(128.0, 100.0, 0)]      # tek takım: panel 200 mm, ikisi tablaya sığmaz

    def __init__(self):
        self.design = P.secilen_20(P.WHITE_SC)
        self.panel = P.solids(self.design)
        self.body = self.design.sc["body"]
        self.module = Q.module_for(P.QR, QR_SIDE)
        self.stand, self.mount = B.stand(length=STAND_LEN)
        self.nozzle_map = {A.WHITE: 1, A.BLACK: 2, A.BLUE: 2}
        self.filament_profiles = {c: A.GENERIC_PLA for c in (A.WHITE, A.BLACK, A.BLUE)}
        self.object_settings = {"enable_support": "0", "ironing_type": "no ironing"}
        self.tower_xy = B.TOWER_XY
        self.project_overrides = {"curr_bed_type": "Textured PEI Plate",
                                  "wipe_tower_x": [f"{B.TOWER_XY[0]:g}"], "wipe_tower_y": [f"{B.TOWER_XY[1]:g}"]}

    def solids(self):
        """Bir takım, nesne merkezi (0, 0): panel boyuna yatık (yüzü yukarı), sehpa önünde; sehpa panelle aynı renk."""
        parts = list(self.panel)
        pb = m3.Manifold.batch_boolean([m for _, m, _ in parts], m3.OpType.Add).bounding_box()
        sb = self.stand.bounding_box()
        st = self.stand.translate(((pb[0] + pb[3]) / 2 - (sb[0] + sb[3]) / 2, pb[1] - B.GAP - sb[4], -sb[2]))
        parts.append((f"Sehpa ({P.NAMES[self.body]})", st, self.body))
        allb = m3.Manifold.batch_boolean([m for _, m, _ in parts], m3.OpType.Add).bounding_box()
        dx, dy = -(allb[0] + allb[3]) / 2, -(allb[1] + allb[4]) / 2
        return [(n, m.translate((dx, dy, 0)), c) for n, m, c in parts]


def checks(plate, parts):
    """Takım iki nozulun ortak alanında ve tablada; kule Bambu'nun izin verdiği yerde ve parçalardan uzak."""
    x, y, _ = plate.instances[0]
    boxes = [(b[0] + x, b[1] + y, b[3] + x, b[4] + y) for b in (m.bounding_box() for _, m, _ in parts)]
    inside = all(b[0] >= X_AUX and b[1] >= 0 and b[2] <= 256 and b[3] <= 256 for b in boxes)
    tx, ty = plate.tower_xy
    lim = 256 - B.TOWER - TOWER_MARGIN - B.TOWER_BRIM
    allowed = TOWER_MARGIN <= tx <= lim and TOWER_MARGIN <= ty <= lim and tx - B.TOWER_BRIM >= X_AUX
    tower = (tx - B.TOWER_BRIM, ty - B.TOWER_BRIM, tx + B.TOWER + B.TOWER_BRIM, ty + B.TOWER + B.TOWER_BRIM)
    sep = lambda a, b: max(b[0] - a[2], a[0] - b[2], b[1] - a[3], a[1] - b[3])  # noqa: E731
    clear = min(sep(tower, b) for b in boxes)
    ok = inside and allowed and clear >= 5.0
    return ok, (f"parçalar iki nozulun ortak alanında: {inside} (x {min(b[0] for b in boxes):.1f}.."
                f"{max(b[2] for b in boxes):.1f}, y {min(b[1] for b in boxes):.1f}..{max(b[3] for b in boxes):.1f}), "
                f"kule {B.TOWER:.1f} mm ({tx:g}, {ty:g}), Bambu sınırında: {allowed}, parçalara {clear:.1f} mm")


def qr_check(plate):
    """Panelin üstten görünüşünde QR'ı okur; ayrıca baskı / okutma hatası benzetiminde."""
    im = B.top_view(plate.panel).convert("L")
    ppm = im.width * (1 - 2 * 0.03) / I.PW
    sim = Q.simulate(im, ppm, plate.module, **dict(Q.SIM_CASES)["hepsi birden"])
    return P.QR.content in Q.decode(im), P.QR.content in Q.decode(sim)


def preview(plate, parts, path, info_lines, title):
    """Tabla, panel önden ve masada sehpada."""
    show = lambda items: [(*A.mesh_arrays(m), B.SHOW[c]) for _, m, c in items]  # noqa: E731
    bed = m3.Manifold.cube((256, 256, 0.2)).translate((0, 0, -0.4))
    tx, ty = plate.tower_xy
    tower = m3.Manifold.cube((B.TOWER, B.TOWER, 10.0)).translate((tx, ty, 0))
    on_bed = [(*A.mesh_arrays(bed), (205, 208, 214)), (*A.mesh_arrays(tower), (150, 156, 168))]
    on_bed += [(*A.mesh_arrays(m.translate((x, y, 0))), B.SHOW[c]) for x, y, _ in plate.instances for _, m, c in parts]
    bed_im = A.fit_into(render(on_bed, 1000, A.R_TOP, flat=0.75, margin=0.02), 420, 420)
    face = A.fit_into(render(show(plate.panel), 1600, rotation(0, 0), flat=0.85, margin=0.02), 560, 420)
    z0, y0 = plate.mount
    stood = B.assembled(plate.panel, z0, y0) + [("s", plate.stand, plate.body)]
    stand_im = A.fit_into(render(show(stood), 1300, rotation(-28, -62), margin=0.02), 400, 420)
    W, H = 1500, 740
    canvas = Image.new("RGB", (W, H), (236, 239, 244))
    dr = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), 32)
    fs = ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), 18)
    boxes = [(bed_im, "Tabla (üstten, gri: prime kulesi)", (30, 200, 480, 700)),
             (face, f"Panel (önden) {PW:.0f} × {PH:.0f} mm", (500, 200, 1090, 700)),
             (stand_im, "Masada, sehpada", (1110, 200, 1470, 700))]
    for im, label, (x0, y0_, x1, y1) in boxes:
        dr.rounded_rectangle((x0, y0_, x1, y1), 22, fill=(146, 153, 166))
        canvas.paste(im, (x0 + (x1 - x0 - im.width) // 2, y0_ + 30 + (y1 - y0_ - 30 - im.height) // 2), im)
        dr.text((x0 + 16, y0_ + 10), label, fill=(236, 239, 244), font=fs)
    dr.text((30, 18), title, fill=(24, 26, 30), font=f)
    for k, line in enumerate(info_lines):
        dr.text((30, 66 + k * 28), line, fill=(22, 120, 60) if k == len(info_lines) - 1 else (70, 74, 84), font=fs)
    canvas.save(path)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    plate = Plate()
    template = zipfile.ZipFile(A.TEMPLATE)
    path, _, filaments = A.write_design(plate, {n: template.read(n) for n in template.namelist()}, OUT_DIR)
    parts = plate.solids()
    mans = [m for _, m, _ in parts]
    overlap = max((mans[i] ^ mans[j]).volume() for i in range(len(mans)) for j in range(i + 1, len(mans)))
    ok_place, place = checks(plate, parts)
    qr_ok, qr_sim = qr_check(plate)
    problems = P.problems(plate.design)
    worst = 9.0
    for k, cs in plate.design.lines.items():
        if k == "QR":
            continue
        inner, gap, _ = B.line_metrics(cs)
        worst = min(worst, inner)
        print(f"  {k:10s} en dar iç boşluk {inner:.2f} mm, en dar ara {gap:.2f} mm, 0,5 mm'den ince %{P.thin(cs)}, "
              f"en {cs.bounds()[2] - cs.bounds()[0]:.1f} mm")
    w, h = plate.size()
    g = {A.COLOUR_NAMES[c]: round(len(plate.instances) * sum(Y.grams(m) for _, m, cc in parts if cc == c), 1)
         for c in filaments}
    pb = plate.panel[0][1].bounding_box()
    print(f"{os.path.relpath(path, A.ROOT)}  {len(plate.instances)} takım ({w:.1f} × {h:.1f} mm); panel "
          f"{pb[3] - pb[0]:.1f} × {pb[4] - pb[1]:.1f} × {pb[5] - pb[2]:.1f} mm  AMS: "
          f"{', '.join(A.COLOUR_NAMES[x] for x in filaments)}  nozul: {plate.nozzle_map}")
    print(f"  sağlam: {all(str(m.status()).endswith('NoError') for m in mans)}  örtüşme: {overlap:.4f} mm³  "
          f"parçalar: {[n for n, _, _ in parts]}")
    print(f"  tasarım kontrolü (çizgi ≥ 0,5, ara ≥ 0,4, öğeler arası ≥ 2 mm): {problems or 'sorun yok'}")
    print(f"  {place} -> {'TAMAM' if ok_place else 'SORUN'}")
    print(f"  QR ({P.QR.content}) okundu: {qr_ok}, benzetimde: {qr_sim}, kare {plate.module:.2f} mm")
    print(f"  tahmini filament: {g}")
    meas = os.path.join(OUT_DIR, "olcum.json")
    when = ""
    if os.path.exists(meas):
        m = json.load(open(meas, encoding="utf-8"))
        g = {k: round(v, 1) for k, v in m["g"].items()}
        when = f" · PrusaSlicer ~{m['sure']}"
        print(f"  ölçüm ({m['kaynak']}): {g}, toplam {m['toplam_g']} g, {m['sure']}")
    info = [f"Tek takım (panel + sehpa) · panel {PW:.0f} × {PH:.0f} mm, beyaz gövde {T:g} mm · yazılar, logo ve QR "
            f"yüzeyle aynı hizada (üst {B.INLAY:g} mm) · sehpa {STAND_LEN:.0f} × 40 mm, yuva {T + 0.3:g} mm",
            "AMS: 1 siyah · 2 beyaz · 3 mavi   ·   beyaz ana nozulda (gövde, sehpa); siyah ve mavi yardımcı nozulda "
            "(yalnız üst 4 katman)",
            "Bambu standart 0,20 mm · ütüleme kapalı · destek yok · Textured PEI · panel yüzü yukarı, sehpa önünde",
            f"Filament ~{sum(g.values()):.0f} g (beyaz {g.get('beyaz', 0):.0f}, siyah {g.get('siyah', 0):.1f}, "
            f"mavi {g.get('mavi', 0):.1f}) + kule{when} · harf içi en dar {worst:.2f} mm · QR {QR_SIDE:.0f} mm "
            f"okundu{' (baskı hatası benzetiminde de)' if qr_sim else ', benzetimde OKUNMADI'} · yerleşim "
            f"{'tamam' if ok_place else 'SORUN'}"]
    preview(plate, parts, os.path.join(OUT_DIR, "onizleme.png"), info,
            f"PALOMA GRIDA – SÜLEYMAN BOYLU · İSİMLİK {PW:.0f} × {PH:.0f} mm (3 · MAVİ KART) · X2D BASKI DOSYASI")


if __name__ == "__main__":
    main()
