"""BOYDE LABS – seçilen kendi isimliklerimiz: iki ölçüde B07, QR Shopier mağazamızı açar. Bambu Lab X2D 3MF.

Kullanıcı isteği: "iki üründe de B07'yi beğendik, fakat Shopier linkimize açılsın QR kodu ve üstündeki yazıları buna
göre konfigüre et ve X2D Bambu Lab baskı dosyalarını ver"; "telefon numaralarını sil, olmasın".
Tasarımlar scripts/boyde_kendi.py'de (b9_shopier, p_shopier); QR https://www.shopier.com/boyde (3. sürüm, hata
düzeltme Q; 9 × 12'de 34 mm, 10 × 20'de 38 mm: beyaz zeminde siyah kareler baskıda yayılır).

9 × 12 (B07; QR sağda, yazılar solda) – lastikçilerin basılan isimlikleriyle aynı yapı ve ayarlar (scripts/uzar_isimlik_baski.py):
  * Tablada iki takım (panel + sehpa). Panel 120 × 90 mm, siyah gövde 1 cm, köşeler R8, pahlı; yüzü yukarı, destek yok.
  * Kabartma 2 mm: işaret, BOYDE, adımlar ve TARA beyaz; işaretin üst katmanı, LABS ve çizgisi, 3. adım ve TARA
    turuncu. Kabartma yazılarda harf içi ve ara ≥ 0,7 mm (işaretin somun yarıkları 0,6 mm: süs, kaynaşsa da görünmez).
  * QR ve shopier.com/boyde yüzeyle aynı hizada beyaz dolgu (üst 4 katman).
  * Nozullar: siyah ve turuncu ana nozulda (turuncu yalnız kabartmada, siyah bitince bir kez geçer), beyaz yardımcıda.
10 × 20 (B07 · Hizmetler) – Paloma'nın basılan isimliğiyle aynı yapı (scripts/paloma_isimlik_baski.py):
  * Tek takım. Panel 200 × 100 mm, beyaz gövde 5 mm ("büyük olanın tabanı beyaz olsun"). Yazılar ve işaret 2 mm
    kabartma ("10 × 20'nin yazılarını neden kabartmalı yapmamışsın"; 9 × 12 gibi): siyah ve turuncu; harf içi ve ara
    ≥ 0,7 mm. QR kareleri yüzeyle aynı hizada siyah dolgu (üst 4 katman). Sehpa beyaz, 170 × 40 mm.
  * Nozullar: beyaz ana nozulda; siyah ve turuncu yardımcı nozulda (QR dolgusu ve kabartma).
İkisinde de: Bambu standart 0,20 mm (Standard @BBL X2D), ütüleme kapalı, destek kapalı, Textured PEI, Generic PLA.
AMS: 1 siyah · 2 beyaz · 3 turuncu (Bambu PLA Basic Orange ya da benzeri).

Kontroller (her üretimde): QR üstten görünüşte ve baskı / okutma hatası benzetiminde okunuyor; parçalar sağlam, örtüşme
yok, iki nozulun ortak alanında; PrusaSlicer'da dilimlenir (scripts/dilim.py): filament, süre ve her yazının kendi
renginde basıldığı (kabartmada ilk ve son katman, dolguda yüzey).

Çıktı : boyde_labs/kendi/baski/boyde_isimlik_9x12_b07_x2d.3mf, onizleme_9x12.png, olcum_9x12.json
        boyde_labs/kendi/baski/boyde_isimlik_10x20_b07_x2d.3mf, onizleme_10x20.png, olcum_10x20.json

Kullanım: python3 scripts/boyde_isimlik_baski.py [9x12|10x20]   (ikisi ayrı süreçte: 10 × 20 modül ölçülerini değiştirir)
"""
import json
import os
import subprocess
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

QR_SIDE = {"9x12": 34.0, "10x20": 38.0}                 # tasarımdaki QR karosu (boyde_kendi)


def setup():
    """Ortak: renkler (turuncu) ve modüller."""
    import anahtarlik as A
    import boyde_kendi as K
    import boyde_sektor as S
    import uzar_isimlik_baski as B
    A.COLOURS[S.ORANGE] = "#FF6A13"                      # Bambu PLA Basic Orange
    A.COLOUR_NAMES[S.ORANGE] = "turuncu"
    A.SHOW[S.ORANGE] = B.SHOW[S.ORANGE] = (250, 106, 30)
    n, red = S.ORANGE, A.RED - 1                         # yıkama hacimleri (renk kimliğiyle dizinli): turuncu kırmızı gibi
    for row in A.FLUSH:
        row.extend([0] * (n - len(row)))
    A.FLUSH.extend([[0] * n for _ in range(n - len(A.FLUSH))])
    for i in range(7):
        A.FLUSH[n - 1][i], A.FLUSH[i][n - 1] = A.FLUSH[red][i], A.FLUSH[i][red]
    A.FLUSH[n - 1][red], A.FLUSH[red][n - 1] = 150, 150
    return A, K, S, B


def qr_check(plate, url):
    """QR üstten görünüşte ve baskı / okutma hatası benzetiminde okunuyor mu."""
    import qr_sistemi as Q
    import uzar_isimlik as I
    import uzar_isimlik_baski as B
    im = B.top_view(plate.panel).convert("L")
    ppm = im.width * (1 - 2 * 0.03) / I.PW
    sim = Q.simulate(im, ppm, plate.module, **dict(Q.SIM_CASES)["hepsi birden"])
    return url in Q.decode(im), url in Q.decode(sim)


def slice_check(plate, path, filaments, move, raised_z, flat_z, out_json):
    """PrusaSlicer'da dilimler; yazılar kendi renginde basılıyor mu. raised_z: kabartmanın [(z, tür)], flat_z: dolgu
    yüzeyi. Döner: (g, süre, satırlar, tamam mı)."""
    import anahtarlik as A
    import dilim
    d = plate.design
    raised = {id(cs): col for cs, col in d.raised}
    inlay = {id(cs): col for cs, col in d.inlay}
    items_r, items_f = [], []
    for k, cs in d.lines.items():
        if k == "QR":
            continue
        if id(cs) in raised:                             # İ / Ö noktaları ayrı ölçülür (küçük: kenar payı oranca büyük)
            dots = [p for p in cs.decompose() if p.area() < 2.5]
            body = cs - A.union(*dots) if dots else cs
            items_r.append((k, move(body), raised[id(cs)]))
            if dots:
                items_r.append((f"{k} (noktalar)", move(A.union(*dots)), raised[id(cs)]))
        elif id(cs) in inlay:
            items_f.append((k, move(cs), inlay[id(cs)]))
    named = {id(cs) for cs in d.lines.values()}               # adsız dolgu: QR (koyu gövdede beyaz karo, açıkta kareler)
    qr = [(cs, col) for cs, col in d.inlay if id(cs) not in named]
    qr_col = qr[0][1]
    qr_cs = move(A.union(*[cs for cs, _ in qr]))
    # QR iki kez ölçülür: büyük parçalar (≥ 2,5 mm², iki kare ve üstü) %85 kuralıyla; bütün kareler, tek kareler dahil,
    # noktalar gibi (%70). Ölçüm ızgarasında komşusuna yalnız köşeden değen kare de ayrı parçadır (dilimleyici de ayrı
    # basar); geometrideki parçalara bakarak ayrılamaz, ızgaradaki parça büyüklüğüyle (speck) ayrılır.
    qr_big = [(f"QR ({A.COLOUR_NAMES[qr_col]})", qr_cs, qr_col)]
    qr_all = [("QR tek kareler dahil (noktalar)", qr_cs, qr_col)]
    tools = {c: i for i, c in enumerate(filaments)}
    with tempfile.TemporaryDirectory() as tmp:
        gcode = os.path.join(tmp, "baski.gcode")
        m = dilim.slice(path, gcode)
        rows = dilim.coverage(gcode, items_r, tools, raised_z) if items_r else []
        if items_f:
            rows += dilim.coverage(gcode, items_f, tools, [(flat_z, "yüzey")])
        rows += dilim.coverage(gcode, qr_big, tools, [(flat_z, "yüzey")], speck=2.5)
        rows += dilim.coverage(gcode, qr_all, tools, [(flat_z, "yüzey")])
    g = {A.COLOUR_NAMES[c]: round(m["g"][i], 2) for i, c in enumerate(filaments)}
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"kaynak": "PrusaSlicer, Bambu standart 0,20 mm eşdeğeri, kule ve renk değişimi hariç",
                   "g": g, "toplam_g": m["toplam_g"], "sure": m["sure"]}, f, ensure_ascii=False)
    ok = all(row_ok(k, kind, cov, per, lost) for k, _, kind, cov, per, _, lost in rows)
    return g, m["sure"], rows, ok


def row_ok(k, kind, cov, per, lost):
    """kenar: kabartmanın ilk katmanında dış şerit; yüzey: üst katman dolu mu. Noktalar ve QR'ın tek kareleri (≈ 1,2 mm):
    çizginin kenar payı alanın büyük bir kısmı, kaplama oranca düşük çıkar; basılıyor mu diye bakılır (≥ %70)."""
    dots = k.endswith("(noktalar)")
    if kind == "kenar":
        return per >= (0.7 if dots else 0.8)
    return per >= 0.7 if dots else cov >= 0.85 and per >= 0.85 and (k[:2] != "QR" or lost <= 0.2)


def report(plate, parts, path, filaments, place, ok_place, qr, url):
    import anahtarlik as A
    import uzar_isimlik_baski as B
    mans = [m for _, m, _ in parts]
    overlap = max((mans[i] ^ mans[j]).volume() for i in range(len(mans)) for j in range(i + 1, len(mans)))
    for k, cs in plate.design.lines.items():
        if k != "QR":
            inner, gap, _ = B.line_metrics(cs)
            print(f"  {k:16s} en dar harf içi {inner:.2f} mm, en dar ara {gap:.2f} mm")
    w, h = plate.size()
    print(f"{os.path.relpath(path, A.ROOT)}  {len(plate.instances)} takım ({w:.1f} × {h:.1f} mm)  AMS: "
          f"{', '.join(A.COLOUR_NAMES[x] for x in filaments)}  nozul: {plate.nozzle_map}")
    print(f"  sağlam: {all(str(m.status()).endswith('NoError') for m in mans)}  örtüşme: {overlap:.4f} mm³")
    print(f"  {place} -> {'TAMAM' if ok_place else 'SORUN'}")
    print(f"  QR ({url}) okundu: {qr[0]}, benzetimde: {qr[1]}, kare {plate.module:.2f} mm")
    return overlap


def print_rows(g, sure, rows, ok):
    print(f"  ölçüm (PrusaSlicer): {g}, {sure}")
    for k, z, kind, cov, per, n, lost in rows:
        print(f"    {k:18s} z {z:4.1f} {kind:5s} kaplama %{100 * cov:5.1f}  en kötü parça %{100 * per:5.1f} ({n})  "
              f"basılmayan en çok {lost:.2f} mm²{'' if row_ok(k, kind, cov, per, lost) else '  <- SORUN'}")
    print(f"  -> {'bütün yazılar ve şekiller basılıyor' if ok else 'SORUN'}")


def make_9x12():
    A, K, S, B = setup()
    import qr_sistemi as Q
    import uzar_isimlik as I
    out_dir = os.path.join(K.OUT, "baski")
    os.makedirs(out_dir, exist_ok=True)

    class Plate(B.Plate):
        key = "boyde_isimlik_9x12_b07_x2d"
        title = "BOYDE_LABS_isimlik_9x12_B07_Shopier"

        def __init__(self):
            self.design = K.b9_shopier()
            self.panel = S.solids(self.design)
            self.module = Q.module_for(K.shopier_qr(), QR_SIDE["9x12"])
            self.stand, self.mount = B.stand()
            self.nozzle_map = {A.BLACK: 1, S.ORANGE: 1, A.WHITE: 2}
            self.filament_profiles = {c: A.GENERIC_PLA for c in (A.BLACK, A.WHITE, S.ORANGE)}
            self.object_settings = {"enable_support": "0", "ironing_type": "no ironing"}
            self.tower_xy = B.TOWER_XY
            self.project_overrides = {"curr_bed_type": "Textured PEI Plate",
                                      "wipe_tower_x": [f"{B.TOWER_XY[0]:g}"], "wipe_tower_y": [f"{B.TOWER_XY[1]:g}"]}

        def to_bed(self, parts):
            """Tasarım koordinatından ilk takımın tabla koordinatına (panel 90° çevrik; autotufan_isimlik_baski)."""
            pb = parts[0][1].bounding_box()
            ob = I.outline().rotate(90).bounds()
            x, y, _ = self.instances[0]
            return lambda cs: cs.rotate(90).translate((pb[0] - ob[0] + x, pb[1] - ob[1] + y))

    plate = Plate()
    template = zipfile.ZipFile(A.TEMPLATE)
    path, _, filaments = A.write_design(plate, {n: template.read(n) for n in template.namelist()}, out_dir)
    parts = plate.solids()
    ok_place, place = B.checks(plate, parts)
    qr = qr_check(plate, K.SHOPIER)
    overlap = report(plate, parts, path, filaments, place, ok_place, qr, K.SHOPIER)
    raised_z = [(round(B.T + 0.2, 2), "kenar"), (round(B.T + B.RELIEF, 2), "yüzey")]
    g, sure, rows, ok = slice_check(plate, path, filaments, plate.to_bed(parts), raised_z, round(B.T, 2),
                                    os.path.join(out_dir, "olcum_9x12.json"))
    print_rows(g, sure, rows, ok)
    info = [f"{len(plate.instances)} takım · panel 120 × 90 mm, siyah gövde 1 cm, kabartma {B.RELIEF:.0f} mm (beyaz "
            "işaret, BOYDE, adımlar, TARA; turuncu katman, LABS, 3. adım); QR ve shopier.com/boyde beyaz dolgu",
            "AMS: 1 siyah (ana nozul) · 2 beyaz (yardımcı nozul) · 3 turuncu (ana nozul, siyahtan sonra)",
            "Bambu standart 0,20 mm · ütüleme kapalı · destek yok · Textured PEI · panel yüzü yukarı, sehpa yanında",
            f"Filament (iki takım) ~{sum(g.values()):.0f} g (siyah {g.get('siyah', 0):.0f}, beyaz "
            f"{g.get('beyaz', 0):.1f}, turuncu {g.get('turuncu', 0):.1f}) + kule · PrusaSlicer ~{sure} · QR Shopier'i "
            f"açar{' (benzetimde de)' if qr[1] else ', benzetimde OKUNMADI'} · dilimleyicide "
            f"{'bütün yazılar basılıyor' if ok else 'SORUN'} · yerleşim {'tamam' if ok_place else 'SORUN'}"]
    B.preview(plate, parts, os.path.join(out_dir, "onizleme_9x12.png"), info,
              title="BOYDE LABS – İSİMLİK 9 × 12 (B07 · SHOPIER) · X2D BASKI DOSYASI")
    return all(qr) and ok and ok_place and overlap < 1e-3


def make_10x20():
    import paloma_isimlik_baski as PB                    # önce: modül ölçüleri 200 × 100 × 5
    A, K, S, B = setup()
    import qr_sistemi as Q
    out_dir = os.path.join(K.OUT, "baski")
    os.makedirs(out_dir, exist_ok=True)
    PB.P.NAMES[S.ORANGE] = "turuncu"

    class Plate(PB.Plate):
        key = "boyde_isimlik_10x20_b07_x2d"
        title = "BOYDE_LABS_isimlik_10x20_B07_Shopier"

        def __init__(self):
            self.relief, self.relief_h = True, PB.RELIEF       # önizlemede eğik bakış: kabartma ışıkla görünsün
            self.design = K.p_shopier()
            self.panel = S.solids_20(self.design)
            self.body = self.design.sc["body"]
            self.module = Q.module_for(K.shopier_qr(), QR_SIDE["10x20"])
            self.stand, self.mount = B.stand(length=PB.STAND_LEN)
            self.nozzle_map = {self.body: 1, S.ORANGE: 2, A.BLACK if self.body == A.WHITE else A.WHITE: 2}
            self.filament_profiles = {c: A.GENERIC_PLA for c in (A.BLACK, A.WHITE, S.ORANGE)}
            self.object_settings = {"enable_support": "0", "ironing_type": "no ironing"}
            self.tower_xy = B.TOWER_XY
            self.project_overrides = {"curr_bed_type": "Textured PEI Plate",
                                      "wipe_tower_x": [f"{B.TOWER_XY[0]:g}"], "wipe_tower_y": [f"{B.TOWER_XY[1]:g}"]}

    plate = Plate()
    template = zipfile.ZipFile(A.TEMPLATE)
    path, _, filaments = A.write_design(plate, {n: template.read(n) for n in template.namelist()}, out_dir)
    parts = plate.solids()                               # plate.offset: tasarımdan tablaya kayma
    ok_place, place = PB.checks(plate, parts)
    qr = qr_check(plate, K.SHOPIER)
    overlap = report(plate, parts, path, filaments, place, ok_place, qr, K.SHOPIER)
    dx, dy = plate.offset
    raised_z = [(round(B.T + 0.2, 2), "kenar"), (round(B.T + PB.RELIEF, 2), "yüzey")]
    g, sure, rows, ok = slice_check(plate, path, filaments, lambda cs: cs.translate((dx, dy)), raised_z,
                                    round(B.T, 2), os.path.join(out_dir, "olcum_10x20.json"))
    print_rows(g, sure, rows, ok)
    body = A.COLOUR_NAMES[plate.body]
    ink = "siyah" if plate.body == A.WHITE else "beyaz"
    info = [f"Tek takım (panel + sehpa) · panel 200 × 100 mm, {body} gövde 5 mm · yazılar ve işaret {PB.RELIEF:.0f} mm "
            f"kabartma ({ink} ve turuncu) · QR yüzeyle aynı hizada {ink} dolgu",
            f"AMS: 1 siyah · 2 beyaz · 3 turuncu   ·   {body} ana nozulda (gövde, sehpa); {ink} ve turuncu yardımcı "
            f"nozulda (QR dolgusu ve kabartma) · sehpa {body}, {PB.STAND_LEN:.0f} × 40 mm",
            "Bambu standart 0,20 mm · ütüleme kapalı · destek yok · Textured PEI · panel yüzü yukarı, sehpa önünde",
            f"Filament ~{sum(g.values()):.0f} g (siyah {g.get('siyah', 0):.1f}, beyaz {g.get('beyaz', 0):.1f}, turuncu "
            f"{g.get('turuncu', 0):.1f}) + kule · PrusaSlicer ~{sure} · QR Shopier'i açar"
            f"{' (benzetimde de)' if qr[1] else ', benzetimde OKUNMADI'} · dilimleyicide "
            f"{'bütün yazılar basılıyor' if ok else 'SORUN'} · yerleşim {'tamam' if ok_place else 'SORUN'}"]
    PB.preview(plate, parts, os.path.join(out_dir, "onizleme_10x20.png"), info,
               "BOYDE LABS – İSİMLİK 10 × 20 (B07 · SHOPIER) · X2D BASKI DOSYASI")
    return all(qr) and ok and ok_place and overlap < 1e-3


def main():
    which = [a for a in sys.argv[1:] if a in ("9x12", "10x20")]
    if len(which) == 1:
        ok = make_9x12() if which[0] == "9x12" else make_10x20()
        print(f"== {which[0]}: {'TAMAM' if ok else 'SORUN'}", flush=True)
        sys.exit(0 if ok else 1)
    codes = [subprocess.call([sys.executable, os.path.abspath(__file__), k]) for k in ("9x12", "10x20")]
    sys.exit(max(codes))


if __name__ == "__main__":
    main()
