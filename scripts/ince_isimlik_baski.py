"""İNCE OTO LASTİK – müşterinin seçtiği isimlik (8 · Kırmızı köşe): baskıya hazır Bambu Lab X2D 3MF.

Uzar'ın basılan isimliğiyle aynı ölçüler ve ayarlar (scripts/uzar_isimlik_baski.py):
  * Tablada iki takım (panel + sehpa). Panel 120 × 90 mm, siyah gövde 1 cm, köşeler R8, alt ve üst kenar 0,6 mm
    basamaklı pah. Yüzü yukarı basılır (arkası tablada), destek gerekmez.
  * Kabartma 2 mm (10 katman): İNCE ve telefon beyaz; köşedeki üçgen (içinde oyma 7/24) ve OTO LASTİK kırmızı.
    Yazılar sol sütunda ortalı ve QR'la aynı yükseklikte ortalı (müşteri isteği: önerideki sola yaslı yazılar
    ortalı görünmüyordu). Harf içi boşluklar ölçülür (en dar ≥ 0,6 mm), İ noktaları harften ayrık.
  * QR (TARA → https://inceotolastik.qrsistem.workers.dev/) yüzeyle aynı hizada: beyaz dolgu üst 4 katmanda
    (0,8 mm), siyah kareler gövdenin kendisi; 42 mm, kare 1,13 mm.
  * Sehpa (siyah) aynı tablada: 100 × 40 × 10 mm; panel yuvaya (10,3 mm) 15° arkaya eğik oturur, tutkal gerekmez.
  * Nozullar: siyah ve kırmızı ana nozulda, beyaz yardımcı nozulda. AMS 1 siyah, 2 beyaz, 3 kırmızı.
  * Bambu standart profili (0,20 mm Standard @BBL X2D): ütüleme kapalı, destek kapalı, tabla Textured PEI.
    Elas PLA Pro (siyah, beyaz) için Generic PLA.

Çıktı : ince_isimlik/baski/ince_isimlik_x2d.3mf, ince_isimlik/baski/onizleme.png

Kullanım:
  python3 scripts/ince_isimlik_baski.py
"""
import json
import os
import sys
import zipfile

import manifold3d as m3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import ince_isimlik as N  # noqa: E402
import masa_isimligi_yeni as Y  # noqa: E402
import qr_sistemi as Q  # noqa: E402
import uzar_isimlik as I  # noqa: E402
import uzar_isimlik_baski as B  # noqa: E402

OUT_DIR = os.path.join(N.OUT_DIR, "baski")
QR_SIDE = 42.0


class Plate(B.Plate):
    key = "ince_isimlik_x2d"
    title = "INCE_OTO_LASTIK_isimlik"

    def __init__(self):
        self.design = N.d8_kose()
        self.panel = N.solids(self.design)
        self.module = Q.module_for(N.QR, QR_SIDE)
        self.stand, self.mount = B.stand()
        self.nozzle_map = {A.BLACK: 1, A.RED: 1, A.WHITE: 2}
        self.filament_profiles = {A.BLACK: A.GENERIC_PLA, A.WHITE: A.GENERIC_PLA}
        self.object_settings = {"enable_support": "0", "ironing_type": "no ironing"}
        self.tower_xy = B.TOWER_XY
        self.project_overrides = {"curr_bed_type": "Textured PEI Plate",
                                  "wipe_tower_x": [f"{B.TOWER_XY[0]:g}"], "wipe_tower_y": [f"{B.TOWER_XY[1]:g}"]}


def qr_check(plate):
    """Panelin üstten görünüşünde QR'ı okur; ayrıca baskı / okutma hatası benzetiminde."""
    im = B.top_view(plate.panel).convert("L")
    ppm = im.width * (1 - 2 * 0.03) / I.PW
    sim = Q.simulate(im, ppm, plate.module, **dict(Q.SIM_CASES)["hepsi birden"])
    return N.QR.content in Q.decode(im), N.QR.content in Q.decode(sim)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    plate = Plate()
    template = zipfile.ZipFile(A.TEMPLATE)
    path, _, filaments = A.write_design(plate, {n: template.read(n) for n in template.namelist()}, OUT_DIR)
    parts = plate.solids()
    mans = [m for _, m, _ in parts]
    overlap = max((mans[i] ^ mans[j]).volume() for i in range(len(mans)) for j in range(i + 1, len(mans)))
    ok_place, place = B.checks(plate, parts)
    qr_ok, qr_sim = qr_check(plate)
    worst = 9.0
    for k, cs in plate.design.lines.items():
        inner, gap, thin = B.line_metrics(cs)
        worst = min(worst, inner)
        print(f"  {k:12s} en dar iç boşluk {inner:.2f} mm, en dar ara {gap:.2f} mm, 0,8 mm'den ince %{thin}, "
              f"en {cs.bounds()[2] - cs.bounds()[0]:.1f} mm")
    w, h = plate.size()
    g = {A.COLOUR_NAMES[c]: round(len(plate.instances) * sum(Y.grams(m) for _, m, cc in parts if cc == c), 1)
         for c in filaments}
    print(f"{os.path.relpath(path, A.ROOT)}  {len(plate.instances)} takım, her biri {w:.1f} × {h:.1f} mm  AMS: "
          f"{', '.join(A.COLOUR_NAMES[x] for x in filaments)}  nozul: {plate.nozzle_map}")
    print(f"  sağlam: {all(str(m.status()).endswith('NoError') for m in mans)}  örtüşme: {overlap:.4f} mm³  "
          f"parçalar: {[n for n, _, _ in parts]}")
    print(f"  {place} -> {'TAMAM' if ok_place else 'SORUN'}")
    print(f"  QR ({N.QR.content}) okundu: {qr_ok}, benzetimde: {qr_sim}, kare {plate.module:.2f} mm")
    print(f"  tahmini filament: {g}")
    meas = os.path.join(OUT_DIR, "olcum.json")
    when = ""
    if os.path.exists(meas):
        m = json.load(open(meas, encoding="utf-8"))
        g = {k: round(v, 1) for k, v in m["g"].items()}
        when = f" · PrusaSlicer ~{m['sure']}"
        print(f"  ölçüm ({m['kaynak']}): {g}, toplam {m['toplam_g']} g, {m['sure']}")
    info = [f"{len(plate.instances)} takım · panel 120 × 90 mm, siyah gövde {B.T / 10:.0f} cm, kabartma {B.RELIEF:.0f} mm "
            "(beyaz İNCE ve telefon, kırmızı köşe / 7/24 / OTO LASTİK), QR yüzeyle aynı hizada beyaz dolgu",
            "AMS: 1 siyah (Elas, ana nozul) · 2 beyaz (Elas, yardımcı nozul) · 3 kırmızı (ana nozul, siyahtan sonra)",
            "Bambu standart 0,20 mm · ütüleme kapalı · destek yok · Textured PEI · panel yüzü yukarı, sehpa yanında",
            f"Filament (iki takım) ~{sum(g.values()):.0f} g (siyah {g.get('siyah', 0):.0f}, beyaz {g.get('beyaz', 0):.1f}, "
            f"kırmızı {g.get('kirmizi', g.get('kırmızı', 0)):.1f}) + kule{when} · harf içi en dar {worst:.2f} mm · "
            f"QR okundu{' (baskı hatası benzetiminde de)' if qr_sim else ', benzetimde OKUNMADI'} · yerleşim "
            f"{'tamam' if ok_place else 'SORUN'}"]
    B.preview(plate, parts, os.path.join(OUT_DIR, "onizleme.png"), info,
              title="İNCE OTO LASTİK – İSİMLİK (8 · KIRMIZI KÖŞE) · X2D BASKI DOSYASI")


if __name__ == "__main__":
    main()
