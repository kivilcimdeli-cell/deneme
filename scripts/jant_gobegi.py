"""Ford jant göbeği (8 tırnaklı, Ø53) – Bambu Lab X2D için baskıya hazır 3MF ve tırnak deneme halkası.

Ölçüler kumpaslı fotoğraflardan okundu (aşağıda ÖLÇÜLDÜ), fotoğraftan okunamayanlar tahmin (TAHMİN).
Tahmin olanlar kumpasla ölçülüp OLCU sözlüğünde değiştirilince betik her şeyi yeniden üretir.

Yapı (kesit; z = 0 flanşın arka yüzü):
  * flanş: Ø D, kalınlık T; ön yüzde amblem/etiket yuvası (kenar halkası `rim` genişliğinde, `cep` derinliğinde),
    ön dış kenar yuvarlatılmış, ortada Ø4 delik (orijinaldeki gibi)
  * arka yüzde 8 tırnaklı halka: gövde dış çapı `tirnak_od`, iç çapı `tirnak_id`, boy `L`;
    uçta dışa doğru diş (`dis_od`): uçtaki rampa takarken içe esnetir, arkasındaki eğik yüz jant deliğine tutunur;
    tırnaklar arasında `yarik` genişliğinde 8 yarık; tırnak kökünde iç pah (kırılmaya karşı)

Baskı: ön yüz yukarıda, tırnak uçları tablada. Flanşın arka yüzü (görünmeyen taraf) ağaç destekle basılır;
ön yüz ve amblem yuvası desteksiz, temiz çıkar.
Malzeme: ASA önerilir (güneşte siyah jant 60-70 °C olur, PLA yumuşar). PETG de olur.

Çıktı : jant_gobegi/ford_jant_gobegi.3mf, jant_gobegi/tirnak_deneme_halkasi.3mf, jant_gobegi/onizleme/*.png

Kullanım:
  python3 scripts/jant_gobegi.py
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
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "jant_gobegi")

OLCU = {
    "D": 53.3,           # ön yüz dış çapı                      ÖLÇÜLDÜ (53,0-53,5)
    "T": 5.0,            # flanş kalınlığı (ön kenar - arka yüz) TAHMİN
    "rim": 2.1,          # ön kenar halkası genişliği            fotoğraftan (amblem Ø ~49)
    "cep": 1.0,          # amblem yuvası derinliği               TAHMİN
    "tirnak_od": 47.6,   # tırnak gövdesi dış çapı               ölçülen 48,5 (dişler dahil) - 2 × 0,5
    "dis_od": 48.6,      # tırnak dişi dış çapı                  ÖLÇÜLDÜ ~48,5
    "tirnak_id": 43.6,   # tırnak iç çapı                        ölçülen 42,9; baskıda duvar 2,0 mm
    "L": 10.0,           # tırnak boyu (arka yüzden uca)         TAHMİN
    "n": 8,              # tırnak sayısı                         fotoğraftan
    "yarik": 3.0,        # tırnaklar arası yarık                 fotoğraftan
    "delik": 4.0,        # orta delik çapı                       fotoğraftan
}
RAMPA, DUZ, TUTUNMA = 1.6, 0.4, 0.6     # diş: uçtaki rampa, düz kısım, tutunma yüzü (eksenel, mm)
SEG = 256


def section(o, flange=True, ring_ri=None):
    """Döndürülecek yarım kesit (x = yarıçap, y = z). ring_ri: deneme halkasında flanşın iç yarıçapı."""
    R, T, rim, cep = o["D"] / 2, o["T"], o["rim"], o["cep"]
    Rc, Rb, Ri, L = o["tirnak_od"] / 2, o["dis_od"] / 2, o["tirnak_id"] / 2, o["L"]
    parts = []
    if flange:
        rf = 1.0                                               # ön dış kenar yuvarlatma
        arc = [(R - rf + rf * np.cos(a), T - rf + rf * np.sin(a)) for a in np.linspace(0, np.pi / 2, 10)]
        Rp = R - rim
        parts.append(A.polygon([(o["delik"] / 2, 0), (R - 0.4, 0), (R, 0.4), *arc, (Rp + 0.3, T), (Rp, T - 0.3),
                                (Rp, T - cep), (o["delik"] / 2, T - cep)]))
    else:
        parts.append(A.polygon([(ring_ri, 0), (R - 0.4, 0), (R, 0.4), (R, 1.6), (ring_ri, 1.6)]))
    tip = 0.5
    parts.append(A.polygon([(Ri, 0.05), (Ri, -L + tip), (Ri + tip, -L), (Rc, -L), (Rb, -L + RAMPA),
                            (Rb, -L + RAMPA + DUZ), (Rc, -L + RAMPA + DUZ + TUTUNMA), (Rc, 0.05)]))
    parts.append(A.polygon([(Ri - 1.0, 0.05), (Ri + 0.1, 0.05), (Ri + 0.1, -1.0)]))   # kök pahı (iç)
    return A.union(*parts)


def slots(o):
    """Tırnakları ayıran yarıklar (flanşın arka yüzüne kadar)."""
    L, w = o["L"], o["yarik"]
    r0, r1 = o["tirnak_id"] / 2 - 1.5, o["dis_od"] / 2 + 1.0
    box = m3.Manifold.cube((r1 - r0, w, L + 1.0)).translate((r0, -w / 2, -L - 1.0))
    return m3.Manifold.batch_boolean([box.rotate((0, 0, 360.0 / o["n"] * (k + 0.5))) for k in range(o["n"])],
                                     m3.OpType.Add)


def cap(o):
    """Jant göbeği, kendi ekseninde: z = 0 arka yüz, ön yüz +T, tırnak uçları -L."""
    return m3.Manifold.revolve(section(o), SEG) - slots(o)


def test_ring(o):
    """Tırnak deneme halkası: yalnız tırnaklar ve 1,6 mm ince flanş halkası (hızlı, ~2 g)."""
    return m3.Manifold.revolve(section(o, flange=False, ring_ri=o["tirnak_id"] / 2 - 1.0), SEG) - slots(o)


class Part:
    def __init__(self, key, title, man, settings):
        self.key, self.title, self.man, self.object_settings = key, title, man, settings

    def solids(self):
        return [(self.title, self.man, A.BLACK)]

    def size(self):
        b = self.man.bounding_box()
        return b[3] - b[0], b[4] - b[1]


def parts(o):
    c = cap(o).translate((0, 0, o["L"]))                     # baskı: ön yüz yukarıda, tırnak uçları tablada
    r = test_ring(o).mirror((0, 0, 1)).translate((0, 0, 1.6))  # deneme: flanş halkası tablada, tırnaklar yukarı
    common = {"wall_loops": "3", "sparse_infill_density": "25%", "brim_type": "no_brim"}
    return [Part("ford_jant_gobegi", "Ford_jant_gobegi_53mm", c,
                 {**common, "enable_support": "1", "support_type": "tree(auto)", "support_on_build_plate_only": "1"}),
            Part("tirnak_deneme_halkasi", "Ford_jant_gobegi_tirnak_deneme", r, {**common, "enable_support": "0"})]


# ---------------------------------------------------------------- görseller

def section_drawing(o, path):
    """Ölçülü kesit resmi: ölçülen ve tahmin edilen ölçüler ayrı renkte."""
    s = 13.0
    W, H = 1500, 760
    im = Image.new("RGB", (W, H), (244, 245, 247))
    dr = ImageDraw.Draw(im)
    dr.text((40, 24), "FORD JANT GÖBEĞİ – KESİT VE ÖLÇÜLER (mm)", fill=(24, 26, 30), font=K.fnt(32))
    dr.text((40, 68), "Yeşil: fotoğraftaki kumpastan okundu   ·   Turuncu: tahmin, lütfen kumpasla ölçün",
            fill=(96, 100, 110), font=K.fnt(20))
    cx, cy = W / 2, 400
    cs = section(o)
    for sign in (1, -1):
        for p in cs.to_polygons():
            dr.polygon([(cx + sign * x * s, cy - y * s) for x, y in p], fill=(52, 54, 60))
    dr.line((cx, 120, cx, 680), fill=(160, 164, 172), width=1)
    green, orange = (30, 140, 70), (220, 120, 20)
    f = K.fnt(19)

    def hdim(x0, x1, y, label, col, up=True):
        dr.line((cx + x0 * s, y, cx + x1 * s, y), fill=col, width=2)
        for x in (x0, x1):
            dr.line((cx + x * s, y - 8, cx + x * s, y + 8), fill=col, width=2)
        tw = dr.textlength(label, font=f)
        dr.text((cx + (x0 + x1) / 2 * s - tw / 2, y - 30 if up else y + 8), label, fill=col, font=f)

    def vdim(x, z0, z1, label, col, right=True):
        X = cx + x * s
        dr.line((X, cy - z0 * s, X, cy - z1 * s), fill=col, width=2)
        for z in (z0, z1):
            dr.line((X - 8, cy - z * s, X + 8, cy - z * s), fill=col, width=2)
        tw = dr.textlength(label, font=f)
        dr.text((X + 12 if right else X - 12 - tw, cy - (z0 + z1) / 2 * s - 12), label, fill=col, font=f)

    R, T, L = o["D"] / 2, o["T"], o["L"]
    hdim(-R, R, cy - T * s - 40, f"A  dış çap {o['D']:.1f}", green)
    hdim(-(R - o["rim"]), R - o["rim"], cy - T * s - 90, f"amblem yuvası Ø{o['D'] - 2 * o['rim']:.1f}", green)
    hdim(-o["dis_od"] / 2, o["dis_od"] / 2, cy + L * s + 40, f"B  tırnak dişleri {o['dis_od']:.1f}", green, up=False)
    hdim(-o["tirnak_id"] / 2, o["tirnak_id"] / 2, cy + L * s + 100, f"C  tırnak içi {o['tirnak_id']:.1f}  (ölçülen 42,9)",
         green, up=False)
    vdim(R + 2.5, 0, T, f"D  flanş kalınlığı {T:.1f}", orange)
    vdim(R + 2.5, -L, 0, f"E  tırnak boyu {L:.1f}", orange)
    vdim(-(R + 2.5), T - o["cep"], T, f"F  yuva derinliği {o['cep']:.1f}", orange, right=False)
    vdim(-(R + 2.5), -L, T, f"toplam yükseklik {T + L:.1f}", orange, right=False)
    dr.text((40, 700), f"8 tırnak, aralarında {o['yarik']:.1f} mm yarık · ortada Ø{o['delik']:.0f} delik · "
                       f"diş: uçta {RAMPA} mm rampa, {o['dis_od'] / 2 - o['tirnak_od'] / 2:.1f} mm dışa taşar",
            fill=(70, 74, 84), font=K.fnt(19))
    im.save(path)
    return im


def preview(o, items, path):
    cap_v = [(*A.mesh_arrays(cap(o)), (52, 54, 60))]
    ring_v = [(*A.mesh_arrays(items[1].man), (52, 54, 60))]
    views = [("ÖN YÜZ", cap_v, rotation(-25, -55)), ("ARKA (TIRNAKLAR)", cap_v, rotation(155, 125)),
             ("TABLADA (ön yüz yukarı)", [(*A.mesh_arrays(items[0].man), (52, 54, 60))], rotation(-30, -60)),
             ("TIRNAK DENEME HALKASI", ring_v, rotation(-30, -60))]
    W, H = 1500, 560
    canvas = Image.new("RGB", (W, H), (244, 245, 247))
    dr = ImageDraw.Draw(canvas)
    dr.text((40, 24), "FORD JANT GÖBEĞİ – BASKIYA HAZIR", fill=(24, 26, 30), font=K.fnt(32))
    dr.text((40, 68), f"Ø{o['D']:.1f} × {o['T'] + o['L']:.1f} mm · 8 tırnak · ön yüz yukarıda basılır, "
                      "arka yüz ağaç destekli · ASA (ya da PETG) önerilir", fill=(96, 100, 110), font=K.fnt(20))
    for i, (label, mesh, R) in enumerate(views):
        box = (40 + i * 362, 120, 40 + i * 362 + 342, 520)
        K.panel(dr, box)
        img = A.fit_into(render(mesh, 900, R, margin=0.02), 290, 320)
        K.paste_center(canvas, img, (box[0], box[1] + 30, box[2], box[3]))
        dr.text((box[0] + 20, box[1] + 16), label, fill=(120, 124, 134), font=K.fnt(16))
    canvas.save(path)
    return canvas


def main():
    o = OLCU
    template = zipfile.ZipFile(A.TEMPLATE)
    template_files = {n: template.read(n) for n in template.namelist()}
    os.makedirs(os.path.join(OUT_DIR, "onizleme"), exist_ok=True)
    items = parts(o)
    for p in items:
        path, _, _ = A.write_design(p, template_files, OUT_DIR)
        b = p.man.bounding_box()
        print(f"{os.path.relpath(path, A.ROOT)}  {b[3] - b[0]:.1f} × {b[4] - b[1]:.1f} × {b[5] - b[2]:.1f} mm  "
              f"hacim {p.man.volume() / 1000:.1f} cm³  sağlam: {str(p.man.status()).endswith('NoError')}  "
              f"parça: {len(p.man.decompose())}  z {b[2]:.2f}..{b[5]:.2f}")
    section_drawing(o, os.path.join(OUT_DIR, "onizleme", "kesit_olculer.png"))
    preview(o, items, os.path.join(OUT_DIR, "onizleme", "jant_gobegi.png"))


if __name__ == "__main__":
    main()
