"""Škoda jant göbeği amblemi – Ø55 mm yuvarlak disk, çift taraflı bantla yapıştırılır; 4 adet, Bambu Lab X2D 3MF.

Yapı (kesit; z = 0 arka yüz, ön yüz z = T):
  * Ø55 × 2,6 mm disk. Ön kenarda 0,6 mm × 45° pah (tablada ilk katmanlar: fil ayağı da görünmez), arkada 0,4 mm pah.
  * Ön yüzde Škoda logosu yüzeyle aynı hizada (orijinal amblem gibi düz): siyah zemin üstünde açık renk halka ve
    kanatlı ok, okun gözü siyah; logonun dışında 1,6 mm siyah kenar. Açık renk 1,0 mm (5 katman), arkası siyah.
    Logo çizimi Simple Icons'tan (scripts/logolar/skoda.svg, CC0); Škoda logosu Škoda Auto'nun markasıdır.
  * Arka yüz düz: çift taraflı bant (3M VHB gibi otomotiv bandı) buraya.

Baskı: ÖN YÜZ TABLADA (en düzgün ve keskin yüz), destek yok. Siyah ana nozulda, açık renk yardımcı nozulda:
filament değişimi yok. Alt ve üst 5'er katman dolu: renkli yüz boşluksuz, disk sağlam ve düz.
Malzeme: ASA önerilir (güneşte jant ısınır, PLA yumuşar); dosyada PLA ayarı var, Bambu Studio'da iki filamenti de
ASA seçmek yeter. Açık renk için beyaz, gümüş ya da Škoda yeşili: yalnız 2. filamentin rengi değişir.

Çıktı : skoda_jant_gobegi/skoda_jant_gobegi_55mm.3mf, skoda_jant_gobegi/onizleme.png

Kullanım:
  pip install svgelements
  python3 scripts/skoda_jant_gobegi.py
"""
import os
import sys
import zipfile

import manifold3d as m3
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import anahtarlik_konsept as K  # noqa: E402
import anahtarlik_kurumsal as P  # noqa: E402
import bmw_logo as B  # noqa: E402
from anahtarlik_kurumsal_kucuk import TOWER_MARGIN, X_AUX, tower_size  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "skoda_jant_gobegi")
SVG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logolar", "skoda.svg")
D = 55.0                        # disk çapı
T = 2.6                         # kalınlık (13 katman)
LOGO_D = 51.8                   # logonun dış halkası; dışında 1,6 mm siyah kenar
INLAY = 1.0                     # açık renk ön yüz derinliği (5 katman): beyaz opak çıksın
FRONT_CH, BACK_CH = 0.6, 0.4    # ön ve arka kenar pahı (45°)
PITCH = 64.0                    # tablada diskler arası (merkezden merkeze)
SEG = 360
R_OUT, R_RING = 12.0, 10.964    # simgedeki dış halka (24 birimlik kutu)
J = m3.JoinType.Round
LIGHT = A.WHITE                 # açık renk (halka ve ok)
OPTIONS = [("Beyaz", (246, 246, 242)), ("Gümüş", (178, 182, 188)), ("Škoda yeşili", (72, 168, 46))]
TOWER, TOWER_BRIM = tower_size(n_fil=2, prime=45.0, change_len=10.0, height=T)


def logo_light():
    """Açık renk bölge (halka ve kanatlı ok; okun gözü boşluk), merkez (0, 0), dış çap LOGO_D."""
    k = LOGO_D / 24.0
    circ = lambda r: A.circle(r * k, 0, 0, SEG)  # noqa: E731
    fill = B.svg_fill(SVG).scale((LOGO_D / B.D, LOGO_D / B.D))    # svg_fill B.D (80 mm) ölçeğinde verir
    arrow = fill ^ circ(10.5)                                       # ok r 4,2..9,7 arasında
    light = (circ(R_OUT) - circ(R_RING)) + arrow
    return A.union(*[p for p in light.decompose() if p.area() > 0.2])


def disc():
    """Pahlı disk, kendi ekseninde: z = 0 arka yüz, z = T ön yüz."""
    R = D / 2
    sec = A.polygon([(0, 0), (R - BACK_CH, 0), (R, BACK_CH), (R, T - FRONT_CH), (R - FRONT_CH, T), (0, T)])
    return m3.Manifold.revolve(sec, SEG)


def face_down(m):
    """Ön yüzü tablaya yatırır: x ekseni etrafında 180° (aynalama değil: logo ters basılmaz)."""
    return m.rotate((180, 0, 0)).translate((0, 0, T))


def solids_face_up():
    light2d = logo_light()
    light = light2d.extrude(INLAY).translate((0, 0, T - INLAY))
    cutter = light2d.extrude(INLAY + 1.0).translate((0, 0, T - INLAY))     # ön yüzün dışına taşar: cep açık kalsın
    body = P.clean(disc() - cutter)
    return [("Gövde ve zemin (siyah)", body, A.BLACK), ("Halka ve kanatlı ok (açık renk)", light, LIGHT)]


class Emblem:
    def __init__(self):
        self.key, self.title = "skoda_jant_gobegi_55mm", "SKODA_jant_gobegi_55mm"
        self._solids = [(n, face_down(m), c) for n, m, c in solids_face_up()]
        self.man = m3.Manifold.batch_boolean([m for _, m, _ in self._solids], m3.OpType.Add)
        cx = A.BED_CENTER[0] - 12.0                              # sağda prime kulesine yer
        cy = A.BED_CENTER[1]
        h = PITCH / 2
        self.instances = [(cx - h, cy + h, 0), (cx + h, cy + h, 0), (cx - h, cy - h, 0), (cx + h, cy - h, 0)]
        tx = round(cx + h + D / 2 + 12.0, 2)
        ty = round(cy - TOWER / 2, 2)
        self.tower_xy = (tx, ty)
        self.nozzle_map = {A.BLACK: 1, LIGHT: 2}                  # siyah ana nozulda, açık renk yardımcıda
        self.filament_profiles = {A.BLACK: A.GENERIC_PLA, LIGHT: A.GENERIC_PLA}
        self.object_settings = {"wall_loops": "3", "bottom_shell_layers": "5", "top_shell_layers": "5",
                                "brim_type": "no_brim", "enable_support": "0"}
        self.project_overrides = {"curr_bed_type": "Textured PEI Plate",
                                  "wipe_tower_x": [f"{tx:g}"], "wipe_tower_y": [f"{ty:g}"]}

    def solids(self):
        return self._solids

    def size(self):
        return D, D

    def layer_colours(self):
        layers = []
        for i in range(int(round(T / A.LAYER))):
            z = (i + 0.5) * A.LAYER
            layers.append({c for _, m, c in self._solids if m.slice(z).area() > 0.01})
        return layers

    colour_changes = P.Keychain.colour_changes


def thin(cs, lim):
    """`lim` mm'den dar alan (%); sivri uçlar (her biri < 0,05 mm²) sayılmaz."""
    th = cs - cs.offset(-lim / 2, J).offset(lim / 2, J)
    return round(100 * sum(p.area() for p in th.decompose() if p.area() > 0.05) / cs.area(), 2)


def checks(e):
    light = logo_light()
    dark = A.circle(LOGO_D / 2, 0, 0, SEG) - light                 # logonun içindeki siyah (zemin ve göz)
    mans = [m for _, m, _ in e.solids()]
    overlap = (mans[0] ^ mans[1]).volume()
    tx, ty = e.tower_xy
    lim = 256 - TOWER - TOWER_MARGIN - TOWER_BRIM
    ok_tower = TOWER_MARGIN <= tx <= lim and TOWER_MARGIN <= ty <= lim and tx - TOWER_BRIM >= X_AUX
    xs = [x for x, _, _ in e.instances]
    in_reach = min(xs) - D / 2 >= X_AUX and max(xs) + D / 2 <= 256 - TOWER_MARGIN / 3
    return {
        "sağlam": all(str(m.status()).endswith("NoError") for m in mans),
        "örtüşme mm³": round(overlap, 4),
        "tek gövde": len(e.man.decompose()) == 1,
        "açık renk <0,45 mm %": thin(light, 0.45), "açık renk <0,8 mm %": thin(light, 0.8),
        "siyah ara <0,45 mm %": thin(dark, 0.45),
        "kule": f"{TOWER:.1f} mm ({tx:g}, {ty:g}) Bambu sınırında: {ok_tower}",
        "iki nozulun ortak alanında": in_reach,
    }


def preview(e, path, stats):
    up = solids_face_up()
    shaded = lambda col: [(*A.mesh_arrays(m), A.SHOW[c] if c != LIGHT else col) for _, m, c in up]  # noqa: E731
    W, H = 1500, 700
    canvas = Image.new("RGB", (W, H), (244, 245, 247))
    dr = ImageDraw.Draw(canvas)
    dr.text((40, 24), "ŠKODA JANT GÖBEĞİ AMBLEMİ – Ø55 mm, 4 ADET (X2D)", fill=(24, 26, 30), font=K.fnt(32))
    dr.text((40, 68), f"Ø{D:.0f} × {T:.1f} mm düz disk · logo yüzle aynı hizada · arka yüz düz: çift taraflı bant · "
                      "ön yüz tablada basılır, destek yok", fill=(96, 100, 110), font=K.fnt(20))
    panels = [(f"{name.upper()} (2. filament)", shaded(col), rotation(0, 0), 0.9) for name, col in OPTIONS]
    panels.append(("KENAR VE KALINLIK", shaded(OPTIONS[0][1]), rotation(-25, -55), None))
    for i, (label, mesh, R, flat) in enumerate(panels):
        box = (40 + i * 287, 120, 40 + i * 287 + 271, 470)
        K.panel(dr, box)
        img = A.fit_into(render(mesh, 1000, R, flat=flat, margin=0.04), 235, 280)
        K.paste_center(canvas, img, (box[0], box[1] + 30, box[2], box[3]))
        dr.text((box[0] + 18, box[1] + 16), label, fill=(120, 124, 134), font=K.fnt(15))
    # tabla: 4 disk ve prime kulesi
    box = (40 + 4 * 287, 120, 40 + 4 * 287 + 271, 470)
    K.panel(dr, box)
    bed = m3.Manifold.cube((256, 256, 0.2)).translate((0, 0, -0.4))
    tx, ty = e.tower_xy
    tower = m3.Manifold.cube((TOWER, TOWER, T)).translate((tx, ty, 0))
    items = [(*A.mesh_arrays(bed), (205, 208, 214)), (*A.mesh_arrays(tower), (150, 156, 168))]
    for x, y, _ in e.instances:
        items += [(*A.mesh_arrays(m.translate((x, y, 0))), A.SHOW[c]) for _, m, c in e.solids()]
    img = A.fit_into(render(items, 1000, A.R_TOP, flat=0.8, margin=0.02), 235, 280)
    K.paste_center(canvas, img, (box[0], box[1] + 30, box[2], box[3]))
    dr.text((box[0] + 18, box[1] + 16), "TABLADA (ön yüzler aşağıda)", fill=(120, 124, 134), font=K.fnt(15))
    lines = [f"AMS: 1 siyah · 2 beyaz (ya da gümüş / yeşil)   ·   siyah ana nozulda, açık renk yardımcı nozulda: "
             f"filament değişimi {stats['değişim']}",
             f"Malzeme: ASA önerilir (güneşte jant ısınır)   ·   ~{stats['g']:.0f} g (4 adet)   ·   "
             f"açık renk çizgiler ve siyah aralar en az 0,45 mm"]
    for k, line in enumerate(lines):
        dr.text((40, 510 + 36 * k), line, fill=(70, 74, 84), font=K.fnt(19))
    dr.text((40, 600), "Logo: Simple Icons (CC0). Škoda logosu Škoda Auto'nun markasıdır; kişisel kullanım içindir.",
            fill=(140, 144, 154), font=K.fnt(16))
    canvas.save(path)


def main():
    e = Emblem()
    template = zipfile.ZipFile(A.TEMPLATE)
    template_files = {n: template.read(n) for n in template.namelist()}
    os.makedirs(OUT_DIR, exist_ok=True)
    path, _, filaments = A.write_design(e, template_files, OUT_DIR)
    _, changes, _ = e.colour_changes(fixed=e.nozzle_map)
    grams = e.man.volume() / 1000 * 1.24 * len(e.instances)
    b = e.man.bounding_box()
    print(f"{os.path.relpath(path, A.ROOT)}  {b[3] - b[0]:.2f} × {b[4] - b[1]:.2f} × {b[5] - b[2]:.2f} mm, "
          f"{len(e.instances)} adet  AMS: {', '.join(A.COLOUR_NAMES[f] for f in filaments)}  "
          f"filament değişimi: {changes}  ~{grams:.1f} g (PLA)")
    for k, v in checks(e).items():
        print(f"  {k}: {v}")
    preview(e, os.path.join(OUT_DIR, "onizleme.png"), {"değişim": changes, "g": grams})


if __name__ == "__main__":
    main()
