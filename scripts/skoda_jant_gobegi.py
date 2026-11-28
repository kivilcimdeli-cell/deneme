"""Škoda jant göbeği amblemi – Ø55 mm, hafif bombeli, çift taraflı bantla yapıştırılır; 4 adet, Bambu Lab X2D 3MF.

Yapı (kesit; z = 0 arka yüz):
  * Ø55 mm. Kenarda 1,8 mm, ortada 2,8 mm: ön yüz 1,0 mm bombeli (küre kapağı, orijinal reçineli amblemler gibi);
    üst kenar R0,8 yuvarlatılmış, tabladaki alt kenarda 0,4 mm pah (fil ayağı görünmez).
  * Ön yüzde Škoda logosu bombeyi izler, yüzeyle aynı hizada: siyah zemin üstünde açık renk halka ve kanatlı ok, okun
    gözü siyah; logonun dışında 1,6 mm siyah kenar. Açık renk yüzeyin 1,0 mm altına kadar (düşey), arkası siyah.
    Logo çizimi Simple Icons'tan (scripts/logolar/skoda.svg, CC0); Škoda logosu Škoda Auto'nun markasıdır.
  * Arka yüz düz: çift taraflı bant (3M VHB gibi otomotiv bandı) buraya.

Baskı: ARKA YÜZ TABLADA, bombe yukarıda: hiçbir yerde sarkma yok, destek gerekmez; arka yüz kusursuz düz çıkar.
Katman 0,12 mm: bombedeki basamaklar ince kalır. Üst 9 katman dolu: renkli kısım boşluksuz, beyaz opak.
Siyah ana nozulda, açık renk yardımcı nozulda: filament değişimi yok.
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
import numpy as np
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
EDGE = 1.8                      # kenar yüksekliği (bombenin başladığı yer)
RISE = 1.0                      # bombe: kenardan ortaya yükselme
T = EDGE + RISE                 # ortada kalınlık
FILLET = 0.8                    # üst kenar yuvarlatma
BACK_CH = 0.4                   # tabladaki alt kenar pahı
LAYER_H = 0.12                  # ince katman: bombedeki basamaklar küçük
LOGO_D = 51.8                   # logonun dış halkası; dışında 1,6 mm siyah kenar
INLAY = 1.0                     # açık renk yüzeyden aşağı (düşey): beyaz opak çıksın
PITCH = 64.0                    # tablada diskler arası (merkezden merkeze)
SEG = 360
R_OUT, R_RING = 12.0, 10.964    # simgedeki dış halka (24 birimlik kutu)
J = m3.JoinType.Round
LIGHT = A.WHITE                 # açık renk (halka ve ok)
OPTIONS = [("Beyaz", (246, 246, 242)), ("Gümüş", (178, 182, 188)), ("Škoda yeşili", (72, 168, 46))]
TOWER, TOWER_BRIM = tower_size(n_fil=2, prime=45.0, change_len=10.0, layer=LAYER_H, height=T)
R = D / 2
RS = (R ** 2 + RISE ** 2) / (2 * RISE)                 # bombenin küre yarıçapı


def top(r):
    """Ön yüzün yüksekliği (küre kapağı): kenarda EDGE, ortada T."""
    return EDGE + np.sqrt(RS ** 2 - r ** 2) - np.sqrt(RS ** 2 - R ** 2)


def section():
    """Döndürülecek yarım kesit (x = yarıçap, y = z): alt pah, dik yan yüz, R FILLET kenar, bombe."""
    r0 = R - FILLET
    cz = top(r0) - FILLET                              # kenar yuvarlatmanın merkezi (r0, cz)
    arc = [(r0 + FILLET * np.cos(a), cz + FILLET * np.sin(a)) for a in np.linspace(0, np.pi / 2, 12)]
    dome = [(r, top(r)) for r in np.linspace(r0, 0, 60)[1:]]
    return [(0, 0), (R - BACK_CH, 0), (R, BACK_CH), *arc, *dome]


def logo_light():
    """Açık renk bölge (halka ve kanatlı ok; okun gözü boşluk), merkez (0, 0), dış çap LOGO_D."""
    k = LOGO_D / 24.0
    circ = lambda r: A.circle(r * k, 0, 0, SEG)  # noqa: E731
    fill = B.svg_fill(SVG).scale((LOGO_D / B.D, LOGO_D / B.D))    # svg_fill B.D (80 mm) ölçeğinde verir
    arrow = fill ^ circ(10.5)                                       # ok r 4,2..9,7 arasında
    light = (circ(R_OUT) - circ(R_RING)) + arrow
    return A.union(*[p for p in light.decompose() if p.area() > 0.2])


def solids():
    """Siyah gövde ve açık renk logo; z = 0 arka yüz (tabla), bombe yukarıda."""
    body = m3.Manifold.revolve(A.polygon(section()), SEG)
    prism = logo_light().extrude(T + 2.0).translate((0, 0, -0.5))
    cutter = prism - body.translate((0, 0, -INLAY))     # logo izinde, yüzeyin INLAY altından yukarısı (dışa taşar)
    light = body ^ cutter
    black = P.clean(body - cutter)
    return [("Gövde ve zemin (siyah)", black, A.BLACK), ("Halka ve kanatlı ok (açık renk)", light, LIGHT)]


class Emblem:
    def __init__(self):
        self.key, self.title = "skoda_jant_gobegi_55mm", "SKODA_jant_gobegi_55mm"
        self._solids = solids()
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
        self.object_settings = {"layer_height": f"{LAYER_H:g}", "wall_loops": "3", "bottom_shell_layers": "4",
                                "top_shell_layers": "9", "brim_type": "no_brim", "enable_support": "0"}
        self.project_overrides = {"curr_bed_type": "Textured PEI Plate",
                                  "wipe_tower_x": [f"{tx:g}"], "wipe_tower_y": [f"{ty:g}"]}

    def solids(self):
        return self._solids

    def size(self):
        return D, D

    def layer_colours(self):
        layers = []
        for i in range(int(np.ceil(T / LAYER_H))):
            z = min((i + 0.5) * LAYER_H, T - 0.01)
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
    # sarkma: her katman bir alttakinden en çok bir katman yüksekliği kadar taşabilir (45°, destek gerekmez)
    zs = np.arange(LAYER_H / 2, T, LAYER_H)
    over = max((e.man.slice(z1) - e.man.slice(z0).offset(LAYER_H + 0.005, J)).area() for z0, z1 in zip(zs, zs[1:]))
    under_light = min(m.slice(0.6).area() for m in mans[1:]) if mans[1].slice(0.6).area() else 0.0
    return {
        "sağlam": all(str(m.status()).endswith("NoError") for m in mans),
        "örtüşme mm³": round(overlap, 4),
        "tek gövde": sum(p.volume() > 0.01 for p in e.man.decompose()) == 1,     # renk sınırında 0 hacimli kırıntılar
        "45°'den fazla sarkan alan mm²": round(over, 3),
        "açık renk z": f"{mans[1].bounding_box()[2]:.2f}..{mans[1].bounding_box()[5]:.2f}",
        "z 0,6'da açık renk mm²": round(under_light, 2),
        "açık renk <0,45 mm %": thin(light, 0.45), "açık renk <0,8 mm %": thin(light, 0.8),
        "siyah ara <0,45 mm %": thin(dark, 0.45),
        "kule": f"{TOWER:.1f} mm ({tx:g}, {ty:g}) Bambu sınırında: {ok_tower}",
        "iki nozulun ortak alanında": in_reach,
    }


def section_drawing(dr, box):
    """Kesit, dikeyde büyütülmüş (kutuya sığacak kadar): siyah gövde, açık renk katman, ölçüler."""
    x0, y0, x1, y1 = box
    sx = (x1 - x0 - 360) / D
    ex = round((y1 - y0 - 130) / (T * sx) * 2) / 2                   # dikey büyütme, 0,5'in katı
    cx, base = (x0 + x1) / 2, y1 - 70
    pts = section()
    poly = [(cx + r * sx, base - z * sx * ex) for r, z in pts] + [(cx - r * sx, base - z * sx * ex) for r, z in pts[::-1]]
    dr.polygon(poly, fill=A.SHOW[A.BLACK])
    band = [(r, top(r)) for r in np.linspace(-LOGO_D / 2, LOGO_D / 2, 120)]
    up = [(cx + r * sx, base - z * sx * ex) for r, z in band]
    down = [(cx + r * sx, base - (z - INLAY) * sx * ex) for r, z in band[::-1]]
    dr.polygon(up + down, fill=(214, 216, 212))
    f, grey, ink = K.fnt(17), (110, 114, 124), (60, 64, 74)
    dr.line((cx - R * sx, base + 22, cx + R * sx, base + 22), fill=grey, width=2)
    for x in (cx - R * sx, cx + R * sx):
        dr.line((x, base + 14, x, base + 30), fill=grey, width=2)
    lab = f"Ø{D:.0f} mm"
    dr.text((cx - dr.textlength(lab, font=f) / 2, base + 30), lab, fill=ink, font=f)
    xr = cx + R * sx + 14
    dr.text((xr, base - EDGE * sx * ex - 10), f"kenar {EDGE:.1f} mm", fill=ink, font=f)
    dr.text((cx + 8, base - T * sx * ex - 30), f"ortası {T:.1f} mm (bombe {RISE:.1f} mm)", fill=ink, font=f)
    dr.text((x0 + 20, y0 + 14), f"KESİT (dikey {ex:g}× büyütülmüş) · açık gri: logonun renkli katmanı, yüzeyden "
            f"{INLAY:.1f} mm · alt yüz düz: bant", fill=grey, font=K.fnt(15))


def preview(e, path, stats):
    shaded = lambda col: [(*A.mesh_arrays(m), A.SHOW[c] if c != LIGHT else col) for _, m, c in e.solids()]  # noqa: E731
    W, H = 1500, 960
    canvas = Image.new("RGB", (W, H), (244, 245, 247))
    dr = ImageDraw.Draw(canvas)
    dr.text((40, 24), "ŠKODA JANT GÖBEĞİ AMBLEMİ – Ø55 mm, HAFİF BOMBELİ, 4 ADET (X2D)", fill=(24, 26, 30),
            font=K.fnt(32))
    dr.text((40, 68), f"Ø{D:.0f} mm · kenarda {EDGE:.1f}, ortada {T:.1f} mm · logo bombeyi izler · arka yüz düz: "
                      "çift taraflı bant · arka yüz tablada basılır, destek yok", fill=(96, 100, 110), font=K.fnt(20))
    panels = [(f"{name.upper()} (2. filament)", shaded(col), rotation(0, 0), 0.9) for name, col in OPTIONS]
    panels.append(("BOMBE", shaded(OPTIONS[0][1]), rotation(-62, -30), None))
    for i, (label, mesh, Rm, flat) in enumerate(panels):
        box = (40 + i * 287, 120, 40 + i * 287 + 271, 470)
        K.panel(dr, box)
        img = A.fit_into(render(mesh, 1000, Rm, flat=flat, margin=0.04), 235, 280)
        K.paste_center(canvas, img, (box[0], box[1] + 30, box[2], box[3]))
        dr.text((box[0] + 18, box[1] + 16), label, fill=(120, 124, 134), font=K.fnt(15))
    box = (40 + 4 * 287, 120, 40 + 4 * 287 + 271, 470)                 # tabla: 4 disk ve prime kulesi
    K.panel(dr, box)
    bed = m3.Manifold.cube((256, 256, 0.2)).translate((0, 0, -0.4))
    tx, ty = e.tower_xy
    tower = m3.Manifold.cube((TOWER, TOWER, T)).translate((tx, ty, 0))
    items = [(*A.mesh_arrays(bed), (205, 208, 214)), (*A.mesh_arrays(tower), (150, 156, 168))]
    for x, y, _ in e.instances:
        items += [(*A.mesh_arrays(m.translate((x, y, 0))), A.SHOW[c]) for _, m, c in e.solids()]
    img = A.fit_into(render(items, 1000, A.R_TOP, flat=0.8, margin=0.02), 235, 280)
    K.paste_center(canvas, img, (box[0], box[1] + 30, box[2], box[3]))
    dr.text((box[0] + 18, box[1] + 16), "TABLADA (bombe yukarıda)", fill=(120, 124, 134), font=K.fnt(15))
    sbox = (40, 490, W - 40, 790)
    K.panel(dr, sbox)
    section_drawing(dr, sbox)
    lines = [f"AMS: 1 siyah · 2 beyaz (ya da gümüş / yeşil)   ·   siyah ana nozulda, açık renk yardımcı nozulda: "
             f"filament değişimi {stats['değişim']}   ·   katman {LAYER_H:g} mm",
             f"Malzeme: ASA önerilir (güneşte jant ısınır)   ·   ~{stats['g']:.0f} g (4 adet)   ·   "
             f"açık renk çizgiler ve siyah aralar en az 0,45 mm"]
    for k, line in enumerate(lines):
        dr.text((40, 816 + 36 * k), line, fill=(70, 74, 84), font=K.fnt(19))
    dr.text((40, 900), "Logo: Simple Icons (CC0). Škoda logosu Škoda Auto'nun markasıdır; kişisel kullanım içindir.",
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
