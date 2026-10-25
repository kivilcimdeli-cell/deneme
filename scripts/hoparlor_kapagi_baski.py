"""Hoparlör kapağı – müşterinin seçtiği 5 numara (Türbin), Ø100 hoparlöre iki kapak: baskıya hazır Bambu Lab X2D 3MF.

Müşteri isteği: Ø70 kapaklar iptal; Ø100 hoparlöre 2 kapak; kırmızı yalnız dış çeperde; ortada NECDET EFE ÇALIK ve
CEMAL ÇALIK, yazı alanı biraz büyük. Hoparlöre yapıştırılacak: dış çeper arkaya doğru çıkıntılı, ucunda ona dik
yapıştırma flanşı.
  * Kapak Ø102,5 mm; ön plaka (ızgara) 2 mm.
  * Arka çıkıntı: dış çeper arkaya 8 mm uzar (duvar 2 mm). Duvarın düz ucu hoparlörün metal çerçevesine
    yapıştırılır (2 mm geniş halka, Ø98,5–102,5 mm); ızgara koniden 8 mm uzakta kalır. (FLANGE > 0 verilirse ucunda
    içe doğru, altı 45° pahlı bir flanş da olur.)
  * Baskı: yüzü tablaya gelecek biçimde ters basılır. Duvar yukarı büyür, destek gerekmez; yapıştırma yüzü son
    katman (düz).
  * Ön yüz düz: kırmızı dış çeper ve beyaz isimler ilk 4 katmana gömülü (0,8 mm, Textured PEI dokusunda, keskin).
  * Ortadaki rozet Ø47 mm; yazı iki satır: üstte ad (NECDET EFE / CEMAL), altta büyük ÇALIK (Saira Condensed Bold
    Italic; harf içleri ≥ 0,7 mm).
  * Türbin 28 kıvrık yarık (rozet büyüyünce yarıklar dikleşir; köprüler ≥ 1,2 mm kalsın diye öneriden seyrek).
    Delikler ≥ 2,2 mm, köprüler ≥ 1,2 mm; ızgara tek parça (kontrol edilir).
  * Nozullar: siyah ana nozulda; kırmızı ve beyaz yardımcı nozulda. AMS 1 siyah, 2 beyaz, 3 kırmızı. Renk değişimi
    yalnız ilk 4 katmanda.
  * İki kapak tek nesne, yan yana; ikisi de yardımcı nozulun ulaştığı alanda (x ≥ 20,5 mm). Bambu standart 0,20 mm,
    ütüleme kapalı, Textured PEI.

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
INL = 0.8                                          # ön yüzde gömülü renk (4 katman)
PLATE = 2.0                                        # ön plaka (ızgara)
LIP, WALL = 8.0, 2.0                               # arka çıkıntı (plakanın arkasından) ve duvar kalınlığı
FLANGE, FLANGE_T = 0.0, 1.4                        # içe doğru flanş: genişlik (0: yok, duvarın ucu yapışır), kalınlık
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


def lip_profile(Rc):
    """Arka çıkıntı ve flanşın (r, z) kesiti; flanşın altı 45° pahlı (ters baskıda destek gerekmez)."""
    r_wi = Rc - WALL
    if FLANGE <= 0:                                  # flanşsız: düz duvar, yapıştırma yüzü duvarın ucu
        return A.polygon([(r_wi, 0.0), (Rc, 0.0), (Rc, PLATE + LIP), (r_wi, PLATE + LIP)])
    r_fi = r_wi - FLANGE
    z_top = PLATE + LIP
    z_f = z_top - FLANGE_T
    z_c = z_f - (r_wi - r_fi)
    return A.polygon([(r_wi, 0.0), (Rc, 0.0), (Rc, z_top), (r_fi, z_top), (r_fi, z_f), (r_wi, z_c)])


def cover(line1, line2):
    """Bir kapak baskı yönünde: ön yüz z = 0'da (tablada), arka çıkıntı yukarı. {renk: Manifold} ve ölçümler.
    Ön görünüşte çizilen her şey x'te aynalanır (alttan bakınca düz okunsun)."""
    Rc = (D + HK.EXTRA) / 2
    Ri = Rc - HK.RIM
    badge = A.circle(RC, 0, 0, 200)
    holes = turbine(Ri, RC)
    keep = A.circle(Ri - 0.9, 0, 0, 200) - badge.offset(1.4, J)
    holes = (holes ^ keep).offset(-HK.MIN_HOLE / 2, J).offset(HK.MIN_HOLE / 2, J)
    holes = A.union(*[p for p in holes.decompose() if p.area() > 2.0])
    grille = A.circle(Rc, 0, 0, 240) - holes
    red2d = A.circle(Rc - 0.6, 0, 0, 240) - A.circle(Ri + 0.3, 0, 0, 240)        # dış çeper
    t1 = N.t("saira_bi", line1, 6.0, 0, 7.0, "c", 0.7, 35.5)
    t2 = N.t("saira_bi", line2, 9.6, 0, -7.0, "c", 0.7, 31.0)
    text = t1 + t2
    mir = lambda cs: cs.mirror((1, 0))  # noqa: E731
    lip = m3.Manifold.revolve(lip_profile(Rc), 240)
    body = mir(grille).extrude(PLATE) + lip
    red = mir(red2d).extrude(INL)
    white = mir(text).extrude(INL)
    body = body - (mir(red2d) + mir(text)).extrude(INL + 0.01).translate((0, 0, -0.01))
    m = dict(D=2 * Rc, open=100 * holes.area() / (A.circle(Ri, 0, 0, 240) - badge).area(),
             thin=sum(p.area() for p in (grille - grille.offset(-HK.MIN_BAR / 2, J).offset(HK.MIN_BAR / 2, J))
                      .decompose() if p.area() > 0.3),
             small=len([p for p in holes.decompose() if p.offset(-HK.MIN_HOLE / 2 + 0.1, J).is_empty()]),
             islands=len([p for p in grille.decompose() if p.area() > 0.05]) - 1,
             text=text, t1=t1, t2=t2)
    return {A.BLACK: body, A.RED: red, A.WHITE: white}, m


def front_up(man, height):
    """Baskı yönündeki parçayı ön yüzü yukarı bakacak biçimde çevirir (görseller için)."""
    return man.rotate((0, 180, 0)).translate((0, 0, height))


class Plate:
    key = "hoparlor_kapagi_x2d"
    title = "HOPARLOR_KAPAGI_5_Turbin_x2"

    def __init__(self):
        self.covers = [cover(a, b) for a, b in NAMES]
        self.offsets = [(-PITCH / 2, 0.0), (PITCH / 2, 0.0)]
        self.height = PLATE + LIP
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


def section(w, h):
    """Kesit çizimi: ön plaka, arka çıkıntı, flanş, 45° pah; hoparlör çerçevesi kesikli."""
    Rc = (D + HK.EXTRA) / 2
    im = Image.new("RGB", (w, h), (250, 250, 248))
    dr = ImageDraw.Draw(im)
    fs = ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), 20)
    k = 30.0                                          # piksel / mm
    ox, oy = 150, h - 60                              # r = 38 mm, z = 0 (ön yüz) noktası
    r0 = 38.0

    def P(r, z):                                     # ön yüz aşağıda (tabladaki gibi), arka yukarıda
        return ox + (r - r0) * k, oy - z * k

    prof = lip_profile(Rc).to_polygons()[0]
    dr.polygon([P(r, z) for r, z in prof], fill=(52, 52, 56))
    holes_r = [(Rc - HK.RIM - 0.9 - 4.2 * j, Rc - HK.RIM - 0.9 - 4.2 * j - 2.4) for j in range(3)]
    dr.rectangle([P(r0, PLATE), P(Rc - WALL + 0.01, 0)], fill=(52, 52, 56))
    for a_, b_ in holes_r:                            # ızgara yarıkları (temsili)
        dr.rectangle([P(b_, PLATE), P(a_, 0)], fill=(250, 250, 248))
    dr.rectangle([P(Rc - HK.RIM + 0.3, INL), P(Rc - 0.6, 0)], fill=(210, 30, 38))
    z_top = PLATE + LIP
    sp = [P(r, z_top + 0.6) for r in np.linspace(r0 + 6, Rc - 1.25, 2)]
    for x in np.arange(sp[0][0], sp[1][0], 14):
        dr.line([(x, sp[0][1]), (x + 8, sp[0][1])], fill=(40, 110, 200), width=3)
    dr.text((sp[0][0], sp[0][1] - 32), "hoparlörün çerçevesi (Ø100) — buraya yapıştırılır", font=fs,
            fill=(40, 110, 200))
    dr.line([P(Rc - WALL - FLANGE, z_top + 0.25), P(Rc, z_top + 0.25)], fill=(230, 160, 40), width=4)
    lab = [((Rc + 1.0, z_top - 1.0), f"yapıştırma yüzü {WALL + FLANGE:g} mm".replace(".", ",")),
           ((Rc + 1.0, PLATE + LIP / 2), f"arka çıkıntı {LIP:.0f} mm"),
           ((Rc + 1.0, 0.6), "ön yüz tablada · kırmızı ve yazı ilk 4 katmanda")]
    if FLANGE > 0:
        lab.append(((Rc - WALL - FLANGE - 6.2, PLATE + LIP - 4.0), "45° pah: destek yok"))
    for (r, z), t in lab:
        dr.text(P(r, z), t, font=fs, fill=(40, 40, 46))
    dr.text((14, 10), "Kesit (baskı yönünde, ölçekli)", font=fs, fill=(90, 90, 96))
    return im


def preview(plate, parts, path, info, title):
    bed = m3.Manifold.cube((256, 256, 0.2)).translate((0, 0, -0.4))
    tx, ty = plate.tower_xy
    tower = m3.Manifold.cube((plate.tower, plate.tower, plate.height)).translate((tx, ty, 0))
    x, y, _ = plate.instances[0]
    on_bed = [(*A.mesh_arrays(bed), (205, 208, 214)), (*A.mesh_arrays(tower), (150, 156, 168))]
    on_bed += [(*A.mesh_arrays(m.translate((x, y, 0))), SHOW[c]) for _, m, c in parts]
    bed_im = A.fit_into(render(on_bed, 1000, A.R_TOP, flat=0.75, margin=0.02), 420, 400)
    front = [(*A.mesh_arrays(front_up(m, plate.height)), SHOW[c]) for _, m, c in parts]
    front_im = A.fit_into(render(front, 1300, rotation(-12, -40), margin=0.02, **HK.LIGHT), 560, 400)
    one = [(n, m ^ m3.Manifold.cube((115, 120, 30)).translate((-115, -60, -1)), c) for n, m, c in parts]
    back_im = A.fit_into(render([(*A.mesh_arrays(m), SHOW[c]) for _, m, c in one if not m.is_empty()], 1100,
                                rotation(-20, -50), margin=0.03, **HK.LIGHT), 400, 400)
    W, H = 1500, 1160
    canvas = Image.new("RGB", (W, H), (236, 239, 244))
    dr = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), 32)
    fs = ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), 18)
    for im, label, (x0, y0, x1, y1) in ((bed_im, "Tabla (üstten; ters basılır, gri: kule)", (30, 210, 470, 660)),
                                        (front_im, "Ön yüz (taktıktan sonra)", (490, 210, 1070, 660)),
                                        (back_im, "Arka: çıkıntı ve yapıştırma yüzü", (1090, 210, 1470, 660))):
        dr.rounded_rectangle((x0, y0, x1, y1), 22, fill=(146, 153, 166))
        canvas.paste(im, (x0 + (x1 - x0 - im.width) // 2, y0 + 30 + (y1 - y0 - 30 - im.height) // 2), im)
        dr.text((x0 + 16, y0 + 10), label, fill=(236, 239, 244), font=fs)
    sec = section(1440, 460)
    canvas.paste(sec, (30, 680))
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
    back = (f"ucunda içe {FLANGE:g} mm flanş, yapıştırma yüzü {WALL + FLANGE:g} mm" if FLANGE > 0 else
            f"ucu {WALL:g} mm yapıştırma yüzü".replace(".", ","))
    support = "flanşın altı 45°" if FLANGE > 0 else "düz duvar"
    info = [f"5 · Türbin · Ø100 hoparlöre iki kapak Ø102,5 mm · arka çıkıntı {LIP:.0f} mm, {back} · rozet Ø47, "
            f"iki satır yazı",
            f"Ters basılır (ön yüz tablada): kırmızı dış çeper ve beyaz isimler ilk 4 katmana gömülü · {support}, "
            "destek yok · AMS: 1 siyah (ana), 2 beyaz ve 3 kırmızı (yardımcı)",
            "Bambu standart 0,20 mm · ütüleme kapalı · Textured PEI · Generic PLA",
            f"Filament ~{sum(g.values()):.0f} g ({', '.join(f'{k} {v:g}' for k, v in g.items())}){when} · açıklık "
            f"%{o:.0f} · delikler en az 2,2 mm, köprüler en az 1,2 mm · yerleşim {'tamam' if ok_all else 'SORUN'}"]
    preview(plate, parts, os.path.join(OUT_DIR, "onizleme.png"), info,
            "HOPARLÖR KAPAĞI – 5 · TÜRBİN · NECDET EFE ÇALIK / CEMAL ÇALIK · X2D BASKI DOSYASI")


if __name__ == "__main__":
    main()
