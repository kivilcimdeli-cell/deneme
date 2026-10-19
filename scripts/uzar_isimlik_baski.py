"""UZAR OTO LASTİK – müşterinin seçtiği isimlik (4 · Tek QR): baskıya hazır Bambu Lab X2D 3MF.

Müşteri isteği: panel ince olmasın, yazı ve logo kabartmalı ve belirgin olsun, yazılar sorunsuz basılsın, ütüleme
olmasın.

  * Panel 120 × 90 × 4 mm (önerilerde 2,6), köşeler R8, alt ve üst kenar 0,6 mm basamaklı pah. Yüzü yukarı basılır
    (arkası tablada), destek gerekmez.
  * Kabartma 1,0 mm (5 katman): UZAR, ANTALYA, TARA, BİZE ULAŞ · ÖDE ve telefon beyaz; şimşek, OTO LASTİK ve
    ok kırmızı. Küçük satırlar sitedeki yazı tipiyle (Outfit ExtraBold) ve büyütüldü: rakam ve harf içi
    boşlukları ≥ 0,7 mm (kabartmada dolmaz), İ / Ö noktaları harften ayrık; ölçümler her üretimde yazdırılır.
  * QR (TARA → işletme sayfası) yüzeyle aynı hizada: beyaz dolgu üst 4 katmanda (0,8 mm), siyah kareler gövdenin
    kendisi. Kabartma QR'da kare kenarlarının gölgesi ve köşe yuvarlanması okumayı bozar; düz QR keskin çıkar.
    Kare 1,29 mm (QR 48 mm; sol sütuna yer açmak için önerideki 54 mm'den küçültüldü).
  * Sehpa (siyah) aynı tablada; panel yuvaya (4,3 mm) 15° arkaya eğik oturur, tutkal gerekmez.
  * Nozullar elle: siyah ve kırmızı ana nozulda (siyah gövde bitince kırmızıya bir kez geçer), beyaz yardımcı
    nozulda. Katman başına filament değişimi yok; renkli katmanlarda yalnız nozul değişir (kule).
  * Bambu standart profili (0,20 mm Standard @BBL X2D): ütüleme kapalı, destek kapalı, tabla Textured PEI.
    Elas PLA Pro (siyah, beyaz) için Generic PLA, kırmızı Bambu PLA Basic.

Çıktı : uzar_isimlik/baski/uzar_isimlik_x2d.3mf, uzar_isimlik/baski/onizleme.png

Kullanım:
  python3 scripts/uzar_isimlik_baski.py
"""
import os
import sys
import zipfile

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import masa_isimligi_yeni as Y  # noqa: E402
import qr_sistemi as Q  # noqa: E402
import uzar_isimlik as I  # noqa: E402
from anahtarlik_kurumsal_kucuk import TOWER_MARGIN, X_AUX, tower_size  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "uzar_isimlik", "baski")
T = 4.0                          # panel kalınlığı (20 katman)
RELIEF = 1.0                     # kabartma (5 katman)
INLAY = 0.8                      # QR'ın beyaz dolgusu (4 katman)
GAP = 12.0                       # panel ile sehpa arası
J = m3.JoinType.Round
TOWER, TOWER_BRIM = tower_size(n_fil=3, prime=45.0, change_len=10.0, height=10.0)
SHOW = {A.BLACK: (40, 40, 43), A.WHITE: (246, 246, 242), A.RED: (206, 28, 38)}


# ---------------------------------------------------------------- yüz (2B)

def loosen_dots(cs, max_area=2.5, shrink=0.12):
    """Küçük, yuvarlağa yakın parçaları (İ ve Ö noktaları, orta nokta) biraz küçültür: harfle arası açılır,
    kabartmada noktayla harf birbirine yapışmaz."""
    out = []
    for p in cs.decompose():
        b = p.bounds()
        box = (b[2] - b[0]) * (b[3] - b[1])
        dot = p.area() < max_area and box > 0 and p.area() / box > 0.6
        out.append(p.offset(-shrink, J) if dot else p)
    return A.union(*out)


def face():
    """Tek QR tasarımı, baskıya göre: {'qr': beyaz dolgu, 'beyaz': kabartma, 'kirmizi': kabartma, 'satirlar': ...}.
    Önerideki düzen korunur; QR 54 → 48 mm (kare 1,29 mm) küçülüp sağa kayar, sol sütun 41 → 54 mm genişler.
    Küçük satırlar sitedeki yazı tipiyle (Outfit ExtraBold): iç boşlukları Barlow Condensed'den geniş, rakamlar
    (0, 6, 8, 9) kabartmada dolmaz."""
    heavy, bold, text = I.heavy(), I.bold(), I.text
    small = A.Font("Outfit-ExtraBold.ttf")
    s, qx, qy = 48.0, 30.0, 47.0
    x0, x1 = -54.0, qx - s / 2 - 6.0
    cap = min(15.0, 10.0 * (x1 - x0) / I.wordmark_width(10.0))
    letters, bolt = I.wordmark(cap, x0, 74.0)
    qr, _, module = I.tile("sayfa", qx, qy, s, r=1.6)
    tara = text(heavy, "TARA", 10.5, x0, 33.5, "l", 0.7)
    tx = tara.bounds()[2] + 3.2
    lines = {"UZAR": letters,
             "OTO LASTİK": text(bold, "OTO LASTİK", 7.2, x0, 57.8, "l", 1.0, x1 - x0),
             "ANTALYA": loosen_dots(text(small, I.INFO.city, 4.4, x0, 48.6, "l", 1.0)),
             "TARA": tara,
             "BİZE ULAŞ · ÖDE": loosen_dots(text(small, "BİZE ULAŞ · ÖDE", 4.4, x0, 21.5, "l", 0.45, x1 - x0)),
             "telefon": text(small, I.INFO.phone, 5.0, x0, 12.5, "l", 0.4, x1 - x0)}
    lines["OTO LASTİK"] = loosen_dots(lines["OTO LASTİK"])
    white = A.union(*(lines[k] for k in ("UZAR", "ANTALYA", "TARA", "BİZE ULAŞ · ÖDE", "telefon")))
    red = A.union(bolt, lines["OTO LASTİK"], A.polygon([(tx, 29.6), (tx + 6.4, 33.5), (tx, 37.4)]))
    return {"qr": qr, "beyaz": white, "kirmizi": red, "module": module, "satirlar": lines}


def line_metrics(cs):
    """(harf içi boşluğun en dar olanının genişliği, parçalar arası en dar ara, 0,8 mm'den ince alan %)."""
    b = cs.bounds()
    comps = sorted((A.rect(b[0] - 1, b[1] - 1, b[2] + 1, b[3] + 1) - cs).decompose(), key=lambda p: -p.area())
    inner = 9.0
    for h in comps[1:]:
        w = 0.0
        for r in [x * 0.025 for x in range(1, 80)]:
            if h.offset(-r, J).is_empty():
                break
            w = 2 * r
        inner = min(inner, w)
    parts, gap = cs.decompose(), 9.0
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            if (parts[i].offset(0.6, J) ^ parts[j].offset(0.6, J)).is_empty():
                continue
            for r in [x * 0.025 for x in range(1, 48)]:
                if not (parts[i].offset(r, J) ^ parts[j].offset(r, J)).is_empty():
                    gap = min(gap, 2 * r)
                    break
    thin = cs - cs.offset(-0.4, J).offset(0.4, J)
    return (round(inner, 2), round(gap, 2),
            round(100 * sum(p.area() for p in thin.decompose() if p.area() > 0.02) / cs.area(), 1))


def thin_report(cs, limit=0.8, gap=0.5):
    """(çizgisi `limit`ten ince alan %, `gap`ten dar ara alanı mm²): açma ve kapama farkları."""
    thin = cs - cs.offset(-limit / 2, J).offset(limit / 2, J)
    narrow = cs.offset(gap / 2, J).offset(-gap / 2, J) - cs
    a = lambda x: sum(p.area() for p in x.decompose() if p.area() > 0.02)  # noqa: E731
    return round(100 * a(thin) / cs.area(), 2), round(a(narrow), 2)


# ---------------------------------------------------------------- katılar

def flat_chamfer(body, out, depth=0.6, steps=3):
    """Alt (tabla) ve üst kenarı basamaklı pahla yumuşatır."""
    rings = []
    for k in range(steps):
        ring = out - out.offset(-depth * (steps - k) / steps, J)
        rings.append(ring.extrude(0.2 + (0.01 if k == 0 else 0)).translate((0, 0, k * 0.2 - (0.01 if k == 0 else 0))))
        rings.append(ring.extrude(0.21 if k == 0 else 0.2).translate((0, 0, T - (k + 1) * 0.2)))
    return body - m3.Manifold.batch_boolean(rings, m3.OpType.Add)


def panel(f):
    """Panel baskı yönünde (yüzü yukarıda, arkası z = 0): [(ad, Manifold, renk)]."""
    out = I.outline()
    inlay = f["qr"].extrude(INLAY).translate((0, 0, T - INLAY))
    body = flat_chamfer(out.extrude(T), out) - f["qr"].extrude(INLAY + 0.01).translate((0, 0, T - INLAY))
    return [("Panel (siyah)", body, A.BLACK),
            ("QR beyaz zemin", inlay, A.WHITE),
            ("Kabartma yazılar (beyaz)", f["beyaz"].extrude(RELIEF).translate((0, 0, T)), A.WHITE),
            ("Kabartma şimşek, OTO LASTİK, ok (kırmızı)", f["kirmizi"].extrude(RELIEF).translate((0, 0, T)),
             A.RED)]


def stand():
    """Sehpa (baskı yönünde, tabanı tablada) ve paneli sehpada gösteren dönüşüm."""
    z0, y0 = 3.0, 2.0
    slot = Y.tilted(I.upright(I.outline(), T + 0.3, -0.15), I.TILT, z0, y0)
    return Y.stand(**I.STAND) - slot, (z0, y0)


def assembled(parts, z0, y0):
    """Panel parçalarını sehpadaki yerine taşır: yüz −y'ye bakar, kabartma önde, 15° arkaya eğik."""
    M = [[1, 0, 0, 0], [0, 0, -1, T], [0, 1, 0, 0]]          # (x, y, z) → (x, T − z, y)
    return [(n, Y.tilted(m.transform(M), I.TILT, z0, y0), c) for n, m, c in parts]


class Plate:
    key = "uzar_isimlik_x2d"
    title = "UZAR_OTO_LASTIK_isimlik"

    def __init__(self):
        self.face = face()
        self.panel = panel(self.face)
        self.stand, self.mount = stand()
        self.nozzle_map = {A.BLACK: 1, A.RED: 1, A.WHITE: 2}
        self.filament_profiles = {A.BLACK: A.GENERIC_PLA, A.WHITE: A.GENERIC_PLA}
        self.object_settings = {"enable_support": "0", "ironing_type": "no ironing"}
        parts = self.solids()
        x1 = max(m.bounding_box()[3] for _, m, _ in parts) + A.BED_CENTER[0]
        tx = round(x1 + TOWER_BRIM + 10.0, 2)
        ty = round(A.BED_CENTER[1] - TOWER / 2, 2)
        self.tower_xy = (tx, ty)
        self.project_overrides = {"curr_bed_type": "Textured PEI Plate",
                                  "wipe_tower_x": [f"{tx:g}"], "wipe_tower_y": [f"{ty:g}"]}

    def solids(self):
        """Tablada, nesne merkezi (0, 0) civarı: panel üstte, sehpa altta; grup tablanın solunda (kuleye yer)."""
        parts = list(self.panel)
        pb = m3.Manifold.batch_boolean([m for _, m, _ in parts], m3.OpType.Add).bounding_box()
        sb = self.stand.bounding_box()
        st = self.stand.translate(((pb[0] + pb[3]) / 2 - (sb[0] + sb[3]) / 2, pb[1] - GAP - sb[4], -sb[2]))
        parts.append(("Sehpa (siyah)", st, A.BLACK))
        allb = m3.Manifold.batch_boolean([m for _, m, _ in parts], m3.OpType.Add).bounding_box()
        dx = -allb[0] + (X_AUX + 12.0) - A.BED_CENTER[0]          # sol kenar x = 32,5 (yardımcı nozul sınırı + pay)
        dy = -(allb[1] + allb[4]) / 2
        return [(n, m.translate((dx, dy, 0)), c) for n, m, c in parts]

    def size(self):
        b = m3.Manifold.batch_boolean([m for _, m, _ in self.solids()], m3.OpType.Add).bounding_box()
        return b[3] - b[0], b[4] - b[1]


# ---------------------------------------------------------------- kontroller ve önizleme

def checks(plate, parts):
    cx, cy = A.BED_CENTER
    boxes = [(b[0] + cx, b[1] + cy, b[3] + cx, b[4] + cy) for b in (m.bounding_box() for _, m, _ in parts)]
    inside = all(b[0] >= X_AUX and b[1] >= 0 and b[2] <= 256 and b[3] <= 256 for b in boxes)
    tx, ty = plate.tower_xy
    lim = 256 - TOWER - TOWER_MARGIN - TOWER_BRIM
    allowed = TOWER_MARGIN <= tx <= lim and TOWER_MARGIN <= ty <= lim and tx - TOWER_BRIM >= X_AUX
    tower = (tx - TOWER_BRIM, ty - TOWER_BRIM, tx + TOWER + TOWER_BRIM, ty + TOWER + TOWER_BRIM)
    sep = lambda a, b: max(b[0] - a[2], a[0] - b[2], b[1] - a[3], a[1] - b[3])  # noqa: E731
    clear = min(sep(tower, b) for b in boxes)
    ok = inside and allowed and clear >= 5.0
    return ok, (f"parçalar iki nozulun ortak alanında: {inside} (x {min(b[0] for b in boxes):.1f}.."
                f"{max(b[2] for b in boxes):.1f}, y {min(b[1] for b in boxes):.1f}..{max(b[3] for b in boxes):.1f}), "
                f"kule {TOWER:.1f} mm ({tx:g}, {ty:g}), Bambu sınırında: {allowed}, parçalara {clear:.1f} mm")


def top_view(parts, size=1600):
    im = render([(*A.mesh_arrays(m), SHOW[c]) for _, m, c in parts], size, A.R_TOP, light=False, margin=0.03)
    bg = Image.new("RGB", im.size, (150, 152, 158))
    bg.paste(im, (0, 0), im)
    return bg


def qr_check(plate):
    """Panelin üstten görünüşünde QR'ı okur; ayrıca baskı / okutma hatası benzetiminde."""
    im = top_view(plate.panel).convert("L")
    ppm = im.width * (1 - 2 * 0.03) / I.PW
    want = I.QRS["sayfa"].content
    sim = Q.simulate(im, ppm, plate.face["module"], **dict(Q.SIM_CASES)["hepsi birden"])
    return want in Q.decode(im), want in Q.decode(sim)


def preview(plate, parts, path, info_lines):
    cx, cy = A.BED_CENTER
    bed = m3.Manifold.cube((256, 256, 0.2)).translate((0, 0, -0.4))
    tx, ty = plate.tower_xy
    tower = m3.Manifold.cube((TOWER, TOWER, 6.0)).translate((tx, ty, 0))
    on_bed = [(*A.mesh_arrays(bed), (205, 208, 214)), (*A.mesh_arrays(tower), (150, 156, 168))]
    on_bed += [(*A.mesh_arrays(m.translate((cx, cy, 0))), SHOW[c]) for _, m, c in parts]
    bed_im = A.fit_into(render(on_bed, 1000, A.R_TOP, flat=0.75, margin=0.02), 470, 470)
    close = A.fit_into(render([(*A.mesh_arrays(m), SHOW[c]) for _, m, c in plate.panel], 1300, rotation(-18, -42),
                              margin=0.02), 520, 470)
    z0, y0 = plate.mount
    stood = assembled(plate.panel, z0, y0) + [("s", plate.stand, A.BLACK)]
    stand_im = A.fit_into(render([(*A.mesh_arrays(m), SHOW[c]) for _, m, c in stood], 1200, rotation(-28, -68),
                                 margin=0.02), 400, 470)
    W, H = 1500, 780
    canvas = Image.new("RGB", (W, H), (236, 239, 244))
    dr = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), 32)
    fs = ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), 18)
    boxes = [(bed_im, "Tabla (üstten, gri: prime kulesi)", (30, 200, 530, 730)),
             (close, "Panel: kabartma yazılar, düz QR", (550, 200, 1090, 730)),
             (stand_im, "Tezgâhta, sehpada", (1110, 200, 1470, 730))]
    for im, label, (x0, y0_, x1, y1) in boxes:
        dr.rounded_rectangle((x0, y0_, x1, y1), 22, fill=(146, 153, 166))
        canvas.paste(im, (x0 + (x1 - x0 - im.width) // 2, y0_ + 30 + (y1 - y0_ - 30 - im.height) // 2), im)
        dr.text((x0 + 16, y0_ + 10), label, fill=(236, 239, 244), font=fs)
    dr.text((30, 18), "UZAR OTO LASTİK – İSİMLİK (4 · TEK QR) · X2D BASKI DOSYASI", fill=(24, 26, 30), font=f)
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
    tw, tn = thin_report(plate.face["beyaz"])
    rw, rn = thin_report(plate.face["kirmizi"])
    for k, cs in plate.face["satirlar"].items():
        inner, gap, thin = line_metrics(cs)
        print(f"  {k:16s} en dar iç boşluk {inner:.2f} mm, en dar ara {gap:.2f} mm, 0,8 mm'den ince %{thin}, "
              f"en {cs.bounds()[2] - cs.bounds()[0]:.1f} mm")
    w, h = plate.size()
    g = {A.COLOUR_NAMES[c]: round(sum(Y.grams(m) for _, m, cc in parts if cc == c), 1) for c in filaments}
    print(f"{os.path.relpath(path, A.ROOT)}  tabla {w:.1f} × {h:.1f} mm  AMS: "
          f"{', '.join(A.COLOUR_NAMES[x] for x in filaments)}  nozul: {plate.nozzle_map}")
    print(f"  sağlam: {all(str(m.status()).endswith('NoError') for m in mans)}  örtüşme: {overlap:.4f} mm³  "
          f"parçalar: {[n for n, _, _ in parts]}")
    print(f"  {place} -> {'TAMAM' if ok_place else 'SORUN'}")
    print(f"  QR okundu: {qr_ok}, benzetimde: {qr_sim}, kare {plate.face['module']:.2f} mm")
    print(f"  kabartma beyaz: 0,8 mm'den ince %{tw}, 0,5 mm'den dar ara {tn} mm²  ·  kırmızı: %{rw}, {rn} mm²")
    print(f"  tahmini filament: {g}")
    meas = os.path.join(OUT_DIR, "olcum.json")
    if os.path.exists(meas):
        import json
        m = json.load(open(meas, encoding="utf-8"))
        g = {k: round(v, 1) for k, v in m["g"].items()}
        print(f"  ölçüm ({m['kaynak']}): {g}, toplam {m['toplam_g']} g, {m['sure']}")
    info = [f"Panel 120 × 90 × {T:.0f} mm, kabartma {RELIEF:.1f} mm (beyaz yazılar, kırmızı şimşek / OTO LASTİK / ok), "
            "QR yüzeyle aynı hizada beyaz dolgu",
            "AMS: 1 siyah (Elas, ana nozul) · 2 beyaz (Elas, yardımcı nozul) · 3 kırmızı (ana nozul, siyahtan sonra)",
            "Bambu standart 0,20 mm · ütüleme kapalı · destek yok · Textured PEI · panel yüzü yukarı, sehpa yanında",
            f"Filament ~{sum(g.values()):.0f} g (siyah {g.get('siyah', 0):.0f}, beyaz {g.get('beyaz', 0):.1f}, kırmızı "
            f"{g.get('kirmizi', g.get('kırmızı', 0)):.1f}) + kule · QR okundu"
            f"{' (baskı hatası benzetiminde de)' if qr_sim else ', benzetimde OKUNMADI'} · yerleşim "
            f"{'tamam' if ok_place else 'SORUN'}"]
    preview(plate, parts, os.path.join(OUT_DIR, "onizleme.png"), info)


if __name__ == "__main__":
    main()
