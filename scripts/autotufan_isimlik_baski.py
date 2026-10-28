"""AUTO TUFAN – müşterinin seçtiği isimlik (1 · Klasik logo, KAPORTA & BOYA yerine HASAR ONARIM): Bambu Lab X2D 3MF.

Lastikçilerin (Uzar, İNCE, Çalık, Soylu) basılan isimlikleriyle aynı ölçüler ve ayarlar (scripts/uzar_isimlik_baski.py):
  * Tablada iki takım (panel + sehpa). Panel 120 × 90 mm, siyah gövde 1 cm, köşeler R8, alt ve üst kenar 0,6 mm
    basamaklı pah. Yüzü yukarı basılır (arkası tablada), destek gerekmez.
  * Kabartma 2 mm (10 katman): Auto Tufan, HASAR ONARIM, ANTALYA, telefon ve TARA beyaz; fırça T, çizgi, HEMEN ARA
    ve telefon simgesi altın.
  * QR işletme sayfasını açar (https://deneme123.qrsistem.workers.dev). Yüzeyle aynı hizada: beyaz dolgu üst
    4 katmanda (0,8 mm), siyah kareler gövdenin kendisi; 32 mm, kare 0,97 mm.
  * Sehpa (siyah) aynı tablada: 100 × 40 × 10 mm; panel yuvaya (10,3 mm) 15° arkaya eğik oturur, tutkal gerekmez.
  * Nozullar: siyah ve altın ana nozulda (altın yalnız kabartmada, siyah bitince bir kez geçer), beyaz yardımcı
    nozulda. Katman başına filament değişimi yok. AMS 1 siyah, 2 beyaz, 3 altın.
  * Bambu standart profili (0,20 mm Standard @BBL X2D): ütüleme kapalı, destek kapalı, tabla Textured PEI.
    Generic PLA; altın için Bambu PLA Basic Gold ya da benzeri.
Dilimleyici kontrolü (scripts/dilim.py): dosya PrusaSlicer'da aynı ayarlarla dilimlenir; filament ve süre ölçülür,
her yazının ve şeklin kabartmanın ilk (kenar) ve son katmanında kendi renginde basıldığı denetlenir.

Çıktı : autotufan_isimlik/baski/autotufan_isimlik_x2d.3mf, onizleme.png, olcum.json;
        autotufan_isimlik/1_klasik_logo_hasar_onarim.png (önden, masada, yandan)

Kullanım:
  python3 scripts/autotufan_isimlik_baski.py
"""
import json
import os
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import autotufan_isimlik as C  # noqa: E402
import dilim  # noqa: E402
import qr_sistemi as Q  # noqa: E402
import uzar_isimlik as I  # noqa: E402
import uzar_isimlik_baski as B  # noqa: E402

OUT_DIR = os.path.join(C.OUT_DIR, "baski")
QR_SIDE = 32.0
B.SHOW[A.GOLD] = C.SHOW[A.GOLD]


class Plate(B.Plate):
    key = "autotufan_isimlik_x2d"
    title = "AUTO_TUFAN_hasar_onarim_isimlik"

    def __init__(self):
        self.design = C.secilen()
        self.panel = C.solids(self.design)
        self.module = Q.module_for(C.QR, QR_SIDE)
        self.stand, self.mount = B.stand()
        self.nozzle_map = {A.BLACK: 1, A.GOLD: 1, A.WHITE: 2}
        self.filament_profiles = {A.BLACK: A.GENERIC_PLA, A.WHITE: A.GENERIC_PLA, A.GOLD: A.GENERIC_PLA}
        self.object_settings = {"enable_support": "0", "ironing_type": "no ironing"}
        self.tower_xy = B.TOWER_XY
        self.project_overrides = {"curr_bed_type": "Textured PEI Plate",
                                  "wipe_tower_x": [f"{B.TOWER_XY[0]:g}"], "wipe_tower_y": [f"{B.TOWER_XY[1]:g}"]}

    def to_bed(self, parts):
        """Tasarım koordinatından ilk takımın tabla koordinatına: panel 90° çevrilir (B.Plate.solids), kaydırılır."""
        pb = parts[0][1].bounding_box()
        ob = I.outline().rotate(90).bounds()
        x, y, _ = self.instances[0]
        return lambda cs: cs.rotate(90).translate((pb[0] - ob[0] + x, pb[1] - ob[1] + y))


def qr_check(plate):
    """Panelin üstten görünüşünde QR'ı okur; ayrıca baskı / okutma hatası benzetiminde."""
    im = B.top_view(plate.panel).convert("L")
    ppm = im.width * (1 - 2 * 0.03) / I.PW
    sim = Q.simulate(im, ppm, plate.module, **dict(Q.SIM_CASES)["hepsi birden"])
    return C.QR.content in Q.decode(im), C.QR.content in Q.decode(sim)


def sliced(plate, parts, path, filaments):
    """PrusaSlicer'da dilimler: ölçüm (olcum.json) ve yazıların kontrolü. Döner: (g, süre, satırlar, tamam mı)."""
    d = plate.design
    move = plate.to_bed(parts)
    names = {id(cs): k for k, cs in d.lines.items()}
    items = [(names[id(cs)], move(cs), col) for cs, col in d.raised if id(cs) in names]
    shapes = [(cs, col) for cs, col in d.raised if id(cs) not in names]     # adsız: fırça T, çizgi, telefon simgesi
    items += [(f"şekil {k} ({C.NAMES[col]})", move(cs), col) for k, (cs, col) in enumerate(shapes, 1)]
    tools = {c: i for i, c in enumerate(filaments)}
    top = round(B.T + B.RELIEF, 2)
    with tempfile.TemporaryDirectory() as tmp:
        gcode = os.path.join(tmp, "baski.gcode")
        m = dilim.slice(path, gcode)
        rows = dilim.coverage(gcode, items, tools, [(round(B.T + 0.2, 2), "kenar"), (top, "yüzey")])
        qr = A.union(*[cs for cs, col in d.inlay if col == A.WHITE])
        rows += dilim.coverage(gcode, [("QR (beyaz karo)", move(qr), A.WHITE)], tools, [(round(B.T, 2), "yüzey")])
    g = {A.COLOUR_NAMES[c]: round(m["g"][i], 2) for i, c in enumerate(filaments)}
    with open(os.path.join(OUT_DIR, "olcum.json"), "w", encoding="utf-8") as f:
        json.dump({"kaynak": "PrusaSlicer, Bambu standart 0,20 mm eşdeğeri, iki takım, kule ve renk değişimi hariç",
                   "g": g, "toplam_g": m["toplam_g"], "sure": m["sure"]}, f, ensure_ascii=False)
    # kenar: kabartmanın ilk katmanında dış şerit tam mı (yan yüz); yüzey: üst katman dolu mu. Üst katmandaki küçük
    # açıklık altındaki aynı renkli katmanı gösterir (görünmez); düz dolguda (QR) ise başka renk görünür, sayılır.
    ok = all(per >= 0.8 if kind == "kenar" else cov >= 0.85 and per >= 0.85 and (k[:2] != "QR" or lost <= 0.2)
             for k, _, kind, cov, per, _, lost in rows)
    return g, m["sure"], rows, ok


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
    print(f"  sıkışık: {C.C.crowded(plate.design) or 'yok'}  simgelerde 1,2 mm'den ince %"
          f"{C.C.thin_shapes(plate.design)}")
    w, h = plate.size()
    print(f"{os.path.relpath(path, A.ROOT)}  {len(plate.instances)} takım, her biri {w:.1f} × {h:.1f} mm  AMS: "
          f"{', '.join(A.COLOUR_NAMES[x] for x in filaments)}  nozul: {plate.nozzle_map}")
    print(f"  sağlam: {all(str(m.status()).endswith('NoError') for m in mans)}  örtüşme: {overlap:.4f} mm³  "
          f"parçalar: {[n for n, _, _ in parts]}")
    print(f"  {place} -> {'TAMAM' if ok_place else 'SORUN'}")
    print(f"  QR ({C.QR.content}) okundu: {qr_ok}, benzetimde: {qr_sim}, kare {plate.module:.2f} mm")
    g, sure, rows, sliced_ok = sliced(plate, parts, path, filaments)
    print(f"  ölçüm (PrusaSlicer): {g}, {sure}")
    print("  dilimleyici kontrolü (ilk takım):")
    for k, z, kind, cov, per, n, lost in rows:
        print(f"    {k:22s} z {z:4.1f} {kind:5s} kaplama %{100 * cov:5.1f}  en kötü parça %{100 * per:5.1f} ({n})  "
              f"basılmayan en çok {lost:.2f} mm²")
    print(f"  -> {'bütün yazılar ve şekiller basılıyor' if sliced_ok else 'SORUN'}")
    info = [f"{len(plate.instances)} takım · panel 120 × 90 mm, siyah gövde {B.T / 10:.0f} cm, kabartma {B.RELIEF:.0f} mm "
            "(beyaz Auto Tufan / HASAR ONARIM / ANTALYA / telefon / TARA; altın fırça T / çizgi / HEMEN ARA), QR siteyi "
            "açar",
            "AMS: 1 siyah (ana nozul) · 2 beyaz (yardımcı nozul) · 3 altın (ana nozul, siyahtan sonra)",
            "Bambu standart 0,20 mm · ütüleme kapalı · destek yok · Textured PEI · panel yüzü yukarı, sehpa yanında",
            f"Filament (iki takım) ~{sum(g.values()):.0f} g (siyah {g.get('siyah', 0):.0f}, beyaz {g.get('beyaz', 0):.1f}, "
            f"altın {g.get('altın', 0):.1f}) + kule · PrusaSlicer ~{sure} · QR okundu"
            f"{' (benzetimde de)' if qr_sim else ', benzetimde OKUNMADI'} · dilimleyicide "
            f"{'bütün yazılar basılıyor' if sliced_ok else 'SORUN'} · yerleşim {'tamam' if ok_place else 'SORUN'}"]
    B.preview(plate, parts, os.path.join(OUT_DIR, "onizleme.png"), info,
              title="AUTO TUFAN – HASAR ONARIM · İSİMLİK (1 · KLASİK LOGO) · X2D BASKI DOSYASI")
    d = C.build(C.secilen)                                     # müşteriye: önden, masada, yandan
    d.metrics = {k: B.line_metrics(cs) for k, cs in d.lines.items()}
    d.qr = (qr_ok, qr_sim)
    C.sheet(d, 1)


if __name__ == "__main__":
    main()
