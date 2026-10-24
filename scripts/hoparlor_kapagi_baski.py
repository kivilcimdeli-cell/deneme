"""Hoparlör kapağı – müşterinin seçtiği 5 numara (Türbin), Ø100 hoparlöre iki kapak: baskıya hazır Bambu Lab X2D 3MF.

Müşteri isteği: Ø70 kapaklar iptal; Ø100 hoparlöre 2 kapak; kırmızı yalnız dış çeperde; ortada NECDET EFE ÇALIK ve
CEMAL ÇALIK, yazı alanı biraz büyük.
  * Kapak Ø102,5 mm (hoparlörden 2,5 mm büyük, kenarından yapıştırılır); ızgara 2 mm, dış çerçeve 3 mm geniş ve
    3,4 mm yüksek, alt yüzü tablada düz.
  * Ortadaki rozet Ø36 → Ø47 mm; yazı iki satır: üstte ad (NECDET EFE / CEMAL), altta büyük ÇALIK (Saira Condensed
    Bold Italic, beyaz, 0,8 mm kabartma; harf içleri ≥ 0,85 mm).
  * Kırmızı: yalnız dış çeper; 3 mm'lik çerçevenin üst yüzü kırmızı (son 3 katmana gömülü, kenardan 0,6 mm içeride).
  * Türbin 28 kıvrık yarık (rozet büyüyünce yarıklar dikleşir; köprüler ≥ 1,2 mm kalsın diye öneriden seyrek).
    Delikler ≥ 2,2 mm, köprüler ≥ 1,2 mm; ızgara tek parça (kontrol edilir).
  * Nozullar: siyah ana nozulda; kırmızı ve beyaz yardımcı nozulda. AMS 1 siyah, 2 beyaz, 3 kırmızı. Kırmızı
    3,4 mm'nin altında, beyaz yazı üstünde: yardımcı nozulda tek filament değişimi (kırmızı → beyaz).
  * İki kapak tek nesne, yan yana; ikisi de yardımcı nozulun ulaştığı alanda (x ≥ 20,5 mm). Yüzü yukarı, düz basılır,
    destek gerekmez. Bambu standart 0,20 mm, ütüleme kapalı, Textured PEI.

Çıktı : hoparlor_kapagi/baski/hoparlor_kapagi_x2d.3mf, onizleme.png

Kullanım:
  python3 scripts/hoparlor_kapagi_baski.py
"""
import json
import math
import os
import sys
import zipfile

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import hoparlor_kapagi as HK  # noqa: E402
import ince_isimlik as N  # noqa: E402
import uzar_isimlik_baski as B  # noqa: E402
from anahtarlik_kurumsal_kucuk import TOWER_MARGIN, X_AUX, tower_size  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(HK.OUT_DIR, "baski")
J = m3.JoinType.Round
NAMES = [("NECDET EFE", "ÇALIK"), ("CEMAL", "ÇALIK")]
D = 100.0                                          # hoparlör çapı
RC = 23.5                                          # rozet yarıçapı (öneride 18)
SLOTS, TWIST = 28, 0.9                             # türbin yarığı sayısı ve kıvrımı (rad)
INL = 0.6                                          # kırmızı gömülü dolgu (3 katman)
CENTER = (128.0, 100.0)                            # nesne merkezi (tabla)
PITCH = 110.0                                      # iki kapağın merkezleri arası
GAP = 8.0                                          # kapaklar ile kule arası
SHOW = {A.BLACK: HK.BLACK, A.WHITE: HK.WHITE, A.RED: HK.RED}
N.FONT_FILES["saira_bi"] = "Saira-CondensedBoldItalic.ttf"


def spiral(a0, r0, r1):
    return [((r0 + (r1 - r0) * u) * math.cos(a0 + TWIST * u), (r0 + (r1 - r0) * u) * math.sin(a0 + TWIST * u))
            for u in np.linspace(0, 1, 30)]


def turbine(R, rc):
    """Öneri 5'in kıvrık yarıkları; büyük rozette yarıklar dikleştiği için 28 yarık (köprüler ≥ 1,2 mm)."""
    r0, r1 = rc + 2.4, R + 1.0
    return A.union(*[A.stroke(spiral(2 * math.pi * k / SLOTS, r0, r1), 2.4) for k in range(SLOTS)])


def cover(line1, line2):
    """Bir kapak, merkezi (0, 0), tabanı z = 0: {renk: Manifold} ve ölçümler."""
    Rc = (D + HK.EXTRA) / 2
    Ri = Rc - HK.RIM
    badge = A.circle(RC, 0, 0, 200)
    holes = turbine(Ri, RC)
    keep = A.circle(Ri - 0.9, 0, 0, 200) - badge.offset(1.4, J)
    holes = (holes ^ keep).offset(-HK.MIN_HOLE / 2, J).offset(HK.MIN_HOLE / 2, J)
    holes = A.union(*[p for p in holes.decompose() if p.area() > 2.0])
    grille = A.circle(Rc, 0, 0, 240) - holes
    rim = A.circle(Rc, 0, 0, 240) - A.circle(Ri, 0, 0, 240)
    # kırmızı yalnız dış çeper: çerçevenin üst yüzü (z 2,8–3,4)
    top_red = A.circle(Rc - 0.6, 0, 0, 240) - A.circle(Ri + 0.3, 0, 0, 240)
    t1 = N.t("saira_bi", line1, 6.0, 0, 7.0, "c", 0.7, 35.5)
    t2 = N.t("saira_bi", line2, 9.6, 0, -7.0, "c", 0.7, 31.0)
    text = t1 + t2
    red = top_red.extrude(INL).translate((0, 0, HK.H - INL))
    body = grille.extrude(HK.T) + (rim + badge).extrude(HK.H)
    body = body - top_red.extrude(INL + 0.01).translate((0, 0, HK.H - INL))
    white = text.extrude(HK.RAISE).translate((0, 0, HK.H))
    m = dict(D=2 * Rc, open=100 * holes.area() / (A.circle(Ri, 0, 0, 240) - badge).area(),
             thin=sum(p.area() for p in (grille - grille.offset(-HK.MIN_BAR / 2, J).offset(HK.MIN_BAR / 2, J))
                      .decompose() if p.area() > 0.3),
             small=len([p for p in holes.decompose() if p.offset(-HK.MIN_HOLE / 2 + 0.1, J).is_empty()]),
             islands=len([p for p in grille.decompose() if p.area() > 0.05]) - 1,
             text=text, t1=t1, t2=t2)
    return {A.BLACK: body, A.RED: red, A.WHITE: white}, m


class Plate:
    key = "hoparlor_kapagi_x2d"
    title = "HOPARLOR_KAPAGI_5_Turbin_x2"

    def __init__(self):
        self.covers = [cover(a, b) for a, b in NAMES]
        self.offsets = [(-PITCH / 2, 0.0), (PITCH / 2, 0.0)]
        self.height = HK.H + HK.RAISE
        self.tower, self.brim = tower_size(n_fil=3, prime=45.0, change_len=10.0, height=self.height)
        r = (D + HK.EXTRA) / 2
        self.tower_xy = (CENTER[0] - self.tower / 2, CENTER[1] + r + GAP + self.brim)
        self.instances = [(*CENTER, 0)]
        self.nozzle_map = {A.BLACK: 1, A.RED: 2, A.WHITE: 2}
        self.filament_profiles = {c: A.GENERIC_PLA for c in (A.BLACK, A.RED, A.WHITE)}
        self.object_settings = {"enable_support": "0", "ironing_type": "no ironing"}
        self.project_overrides = {"curr_bed_type": "Textured PEI Plate",
                                  "wipe_tower_x": [f"{self.tower_xy[0]:g}"], "wipe_tower_y": [f"{self.tower_xy[1]:g}"]}

    def solids(self):
        """İki kapak tek nesnede; nesne merkezi (0, 0)."""
        names = {A.BLACK: "Kapaklar (siyah)", A.RED: "Kırmızı detaylar", A.WHITE: "Yazılar (beyaz)"}
        out = []
        for c in (A.BLACK, A.RED, A.WHITE):
            man = m3.Manifold.batch_boolean([cv[0][c].translate((dx, dy, 0))
                                             for cv, (dx, dy) in zip(self.covers, self.offsets)], m3.OpType.Add)
            out.append((names[c], man, c))
        return out


def checks(plate, parts):
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
    on_bed += [(*A.mesh_arrays(m.translate((x, y, 0))), SHOW[c]) for _, m, c in parts]
    bed_im = A.fit_into(render(on_bed, 1000, A.R_TOP, flat=0.75, margin=0.02), 440, 440)
    shown = [(*A.mesh_arrays(m), SHOW[c]) for _, m, c in parts]
    iso = A.fit_into(render(shown, 1400, rotation(-12, -38), margin=0.02, **HK.LIGHT), 960, 440)
    W, H = 1500, 760
    canvas = Image.new("RGB", (W, H), (236, 239, 244))
    dr = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), 32)
    fs = ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), 18)
    for im, label, (x0, y0, x1, y1) in ((bed_im, "Tabla (üstten, gri: prime kulesi)", (30, 230, 500, 740)),
                                        (iso, "İki kapak (Ø102,5 mm)", (520, 230, 1470, 740))):
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
    overlap = max((mans[i] ^ mans[j]).volume() for i in range(3) for j in range(i + 1, 3))
    ok_place, place = checks(plate, parts)
    print(f"{os.path.relpath(path, A.ROOT)}  AMS: {', '.join(A.COLOUR_NAMES[x] for x in filaments)}  "
          f"nozul: {plate.nozzle_map}")
    print(f"  sağlam: {all(str(m.status()).endswith('NoError') for m in mans)}  örtüşme: {overlap:.4f} mm³  "
          f"parçalar: {[n for n, _, _ in parts]}")
    print(f"  {place} -> {'TAMAM' if ok_place else 'SORUN'}")
    ok_all = ok_place and overlap < 0.01
    for (a, b), (_, m) in zip(NAMES, plate.covers):
        ok = m["thin"] < 1.0 and m["small"] == 0 and m["islands"] == 0
        ok_all &= ok
        lines = []
        for k, cs in (("üst", m["t1"]), ("alt", m["t2"])):
            inner, gap, thin = B.line_metrics(cs)
            bb = cs.bounds()
            lines.append(f"{k} satır {bb[2] - bb[0]:.1f} × {bb[3] - bb[1]:.1f} mm, iç boşluk {inner:.2f}, ara {gap:.2f}")
        print(f"  {a} {b}: Ø{m['D']:.1f}, açıklık %{m['open']:.0f}, ince köprü {m['thin']:.1f} mm², küçük delik "
              f"{m['small']}, kopuk parça {m['islands']} · {'; '.join(lines)}"
              f" -> {'TAMAM' if ok else 'SORUN'}")
    g = {A.COLOUR_NAMES[c]: round(sum(HK.Y_grams(m, infill=1.0) for _, m, cc in parts if cc == c), 1)
         for c in filaments}
    when = ""
    meas = os.path.join(OUT_DIR, "olcum.json")
    if os.path.exists(meas):
        mm = json.load(open(meas, encoding="utf-8"))
        g = {k: round(v, 1) for k, v in mm["g"].items()}
        when = f" · PrusaSlicer ~{mm['sure']}"
        print(f"  ölçüm ({mm['kaynak']}): {g}, toplam {mm['toplam_g']} g, {mm['sure']}")
    else:
        print(f"  dolu hacimden filament: {g}")
    o = plate.covers[0][1]["open"]
    info = ["5 · Türbin · Ø100 hoparlöre iki kapak Ø102,5 mm (kenardan yapıştırılır) · rozet Ø47 mm, iki satır yazı "
            "(NECDET EFE / CEMAL + ÇALIK), 0,8 mm beyaz kabartma",
            "Kırmızı yalnız dış çeperde (çerçevenin üst yüzü, son 3 katmana gömülü) · AMS: 1 siyah (ana nozul), "
            "2 beyaz ve 3 kırmızı (yardımcı nozul)",
            "Yüzü yukarı, düz basılır, destek yok · Bambu standart 0,20 mm · ütüleme kapalı · Textured PEI · Generic PLA",
            f"Filament ~{sum(g.values()):.0f} g ({', '.join(f'{k} {v:g}' for k, v in g.items())}){when} · açıklık "
            f"%{o:.0f} · delikler en az 2,2 mm, köprüler en az 1,2 mm · yerleşim {'tamam' if ok_all else 'SORUN'}"]
    preview(plate, parts, os.path.join(OUT_DIR, "onizleme.png"), info,
            "HOPARLÖR KAPAĞI – 5 · TÜRBİN · NECDET EFE ÇALIK / CEMAL ÇALIK · X2D BASKI DOSYASI")


if __name__ == "__main__":
    main()
