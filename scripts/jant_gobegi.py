"""Ford jant göbeği (8 tırnaklı, Ø53, Ford logolu) – Bambu Lab X2D için baskıya hazır 3MF ve tırnak deneme halkası.

Ölçüler kumpaslı fotoğraflardan okundu (aşağıda ÖLÇÜLDÜ), fotoğraftan okunamayanlar tahmin (TAHMİN).
Tahmin olanlar kumpasla ölçülüp OLCU sözlüğünde değiştirilince betik her şeyi yeniden üretir.

Yapı (kesit; z = 0 flanşın arka yüzü):
  * flanş: Ø D, kalınlık T; ön yüzde amblem yuvası (kenar halkası `rim` genişliğinde, `cep` derinliğinde),
    ön dış kenar yuvarlatılmış
  * Ford logosu yuvanın içinde, katman katman (rozet gibi): ten rengi zemin (yuva tabanına gömülü, 3 katman),
    üstünde 0,4 mm kabarık mavi oval, onun üstünde beyaz "Ford" yazısı ve oval çizgisi (kenar halkasıyla aynı hizada).
    Renkler üst üste bindiği için her katmanda en fazla iki renk var: baskıda yalnız 2 filament değişimi.
    Logo çizimi: Simple Icons (scripts/logolar/ford.svg, CC0); Ford logosu Ford Motor Company'nin markasıdır.
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
import re
import sys
import zipfile

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import anahtarlik_konsept as K  # noqa: E402
import anahtarlik_kurumsal as P  # noqa: E402
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
    "delik": 0.0,        # orta delik (orijinalde Ø4; logolu yüzde kapalı)
    "logo_en": 45.5,     # Ford ovalinin eni                     fotoğraftan (46 × 17 mm)
}
ZEMIN, MAVI = 0.6, 0.4                  # zemin derinliği, mavi oval kabartması (mm); beyaz yazı: cep - MAVI
ZEMIN_RENK = A.SKIN                     # yuva zemini: ten rengi (yazı ve oval çizgisi beyaz kalır)
YAZI_KALINLASTIR = 0.08                 # beyaz yazıyı her yandan kalınlaştır: ince kıvrımlar 0,4 nozulla basılsın
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
    """Jant göbeği gövdesi (tek renk), kendi ekseninde: z = 0 arka yüz, ön yüz +T, tırnak uçları -L."""
    return m3.Manifold.revolve(section(o), SEG) - slots(o)


def ford_logo(width):
    """Ford ovali: (oval dış hattı, beyaz kısımlar = oval çizgisi + yazı). Merkez (0, 0), y yukarı."""
    svg = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logolar", "ford.svg")).read()
    import svgelements as se
    loops = []
    for sp in se.Path(re.search(r' d="([^"]+)"', svg).group(1)).as_subpaths():
        pts = []
        for seg in se.Path(sp):
            if isinstance(seg, se.Move):
                continue
            if isinstance(seg, (se.Line, se.Close)):
                pts.append((seg.end.x, seg.end.y))
            else:
                pts += [(seg.point(t).x, seg.point(t).y) for t in np.linspace(0, 1, 16)[1:]]
        if len(pts) > 2:
            loops.append(pts)
    blue = m3.CrossSection(loops, m3.FillRule.NonZero)          # simgede dolu = mavi, boşluk = beyaz
    x0, y0, x1, y1 = blue.bounds()
    k = width / (x1 - x0)
    blue = blue.translate((-(x0 + x1) / 2, -(y0 + y1) / 2)).scale((k, -k))
    area = lambda p: abs(np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1]))  # noqa: E731
    oval = m3.CrossSection([max(blue.to_polygons(), key=area)])
    white = ((oval - blue).offset(YAZI_KALINLASTIR, m3.JoinType.Round) ^ oval.offset(-0.3, m3.JoinType.Round))
    return oval, white


def cap_parts(o):
    """Renkli parçalar: gövde (siyah), zemin (ten rengi), oval (mavi), yazı ve çizgi (beyaz). Kendi ekseninde."""
    T, cep, Rp = o["T"], o["cep"], o["D"] / 2 - o["rim"]
    floor = T - cep
    oval, white = ford_logo(o["logo_en"])
    disc = A.circle(Rp, 0, 0, SEG)
    zemin = disc.extrude(ZEMIN).translate((0, 0, floor - ZEMIN))
    mavi = oval.extrude(MAVI).translate((0, 0, floor))
    yazi = white.extrude(cep - MAVI).translate((0, 0, floor + MAVI))
    body = P.clean(cap(o) - zemin)
    return [("Gövde (siyah)", body, A.BLACK), (f"Zemin ({A.COLOUR_NAMES[ZEMIN_RENK]})", zemin, ZEMIN_RENK),
            ("Oval (mavi)", mavi, A.BLUE),
            ("Ford yazısı ve çizgi (beyaz)", yazi, A.WHITE)]


def test_ring(o):
    """Tırnak deneme halkası: yalnız tırnaklar ve 1,6 mm ince flanş halkası (hızlı, ~2 g)."""
    return m3.Manifold.revolve(section(o, flange=False, ring_ri=o["tirnak_id"] / 2 - 1.0), SEG) - slots(o)


class Part:
    def __init__(self, key, title, solids, settings):
        self.key, self.title, self._solids, self.object_settings = key, title, solids, settings
        self.man = m3.Manifold.batch_boolean([m for _, m, _ in solids], m3.OpType.Add)

    def solids(self):
        return self._solids

    def size(self):
        b = self.man.bounding_box()
        return b[3] - b[0], b[4] - b[1]

    def layer_colours(self):
        """Katman başına filamentler (renk değişimi hesabı için)."""
        top = self.man.bounding_box()[5]
        layers = []
        for i in range(int(round(top / A.LAYER))):
            z = (i + 0.5) * A.LAYER
            layers.append({e for _, m, e in self._solids if m.slice(z).area() > 0.01})
        return layers

    colour_changes = P.Keychain.colour_changes


def parts(o):
    up = lambda m: m.translate((0, 0, o["L"]))  # noqa: E731  baskı: ön yüz yukarıda, tırnak uçları tablada
    c = [(n, up(m), e) for n, m, e in cap_parts(o)]
    r = test_ring(o).mirror((0, 0, 1)).translate((0, 0, 1.6))  # deneme: flanş halkası tablada, tırnaklar yukarı
    common = {"wall_loops": "3", "sparse_infill_density": "25%", "brim_type": "no_brim"}
    return [Part("ford_jant_gobegi", "Ford_jant_gobegi_53mm", c,
                 {**common, "enable_support": "1", "support_type": "tree(auto)", "support_on_build_plate_only": "1"}),
            Part("tirnak_deneme_halkasi", "Ford_jant_gobegi_tirnak_deneme", [("Tırnak deneme halkası", r, A.BLACK)],
                 {**common, "enable_support": "0"})]


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
    dr.text((40, 700), f"8 tırnak, aralarında {o['yarik']:.1f} mm yarık · yuvada Ford logosu ({o['logo_en']:.1f} mm) · "
                       f"diş: uçta {RAMPA} mm rampa, {o['dis_od'] / 2 - o['tirnak_od'] / 2:.1f} mm dışa taşar",
            fill=(70, 74, 84), font=K.fnt(19))
    im.save(path)
    return im


def preview(o, items, path):
    cap_v = [(*A.mesh_arrays(m), A.SHOW[e]) for _, m, e in cap_parts(o)]
    ring_v = [(*A.mesh_arrays(items[1].man), A.SHOW[A.BLACK])]
    views = [("ÖN YÜZ", cap_v, rotation(0, 0)), ("PERSPEKTİF", cap_v, rotation(-25, -55)),
             ("ARKA (TIRNAKLAR)", cap_v, rotation(155, 125)), ("TIRNAK DENEME HALKASI", ring_v, rotation(-30, -60))]
    W, H = 1500, 620
    canvas = Image.new("RGB", (W, H), (244, 245, 247))
    dr = ImageDraw.Draw(canvas)
    dr.text((40, 24), "FORD JANT GÖBEĞİ – BASKIYA HAZIR", fill=(24, 26, 30), font=K.fnt(32))
    dr.text((40, 68), f"Ø{o['D']:.1f} × {o['T'] + o['L']:.1f} mm · 8 tırnak · logo: {A.COLOUR_NAMES[ZEMIN_RENK]} zemin, {MAVI} mm kabarık "
                      f"mavi oval, üstünde beyaz yazı · ön yüz yukarıda, arka yüz ağaç destekli",
            fill=(96, 100, 110), font=K.fnt(20))
    for i, (label, mesh, R) in enumerate(views):
        box = (40 + i * 362, 120, 40 + i * 362 + 342, 520)
        K.panel(dr, box)
        img = A.fit_into(render(mesh, 1000, R, margin=0.02), 300, 320)
        K.paste_center(canvas, img, (box[0], box[1] + 30, box[2], box[3]))
        dr.text((box[0] + 20, box[1] + 16), label, fill=(120, 124, 134), font=K.fnt(16))
    _, changes, flush = items[0].colour_changes()
    ams = " · ".join(f"{i} {A.COLOUR_NAMES[f]}" for i, f in enumerate(sorted({e for _, _, e in items[0].solids()}), 1))
    dr.text((40, 548), f"AMS: {ams}   ·   filament değişimi: {changes} (~{flush} mm³)   ·   "
                       "malzeme: ASA (güneşe ve ısıya dayanır), yoksa PETG", fill=(70, 74, 84), font=K.fnt(19))
    canvas.save(path)
    return canvas


def main():
    o = OLCU
    template = zipfile.ZipFile(A.TEMPLATE)
    template_files = {n: template.read(n) for n in template.namelist()}
    os.makedirs(os.path.join(OUT_DIR, "onizleme"), exist_ok=True)
    items = parts(o)
    for p in items:
        path, _, filaments = A.write_design(p, template_files, OUT_DIR)
        b = p.man.bounding_box()
        mans = [m for _, m, _ in p.solids()]
        overlap = max([(mans[i] ^ mans[j]).volume() for i in range(len(mans)) for j in range(i + 1, len(mans))] or [0])
        print(f"{os.path.relpath(path, A.ROOT)}  {b[3] - b[0]:.1f} × {b[4] - b[1]:.1f} × {b[5] - b[2]:.1f} mm  "
              f"AMS: {', '.join(A.COLOUR_NAMES[f] for f in filaments)}  hacim {p.man.volume() / 1000:.1f} cm³  "
              f"sağlam: {all(str(m.status()).endswith('NoError') for m in mans)}  örtüşme: {overlap:.4f} mm³  "
              f"tek gövde: {len(p.man.decompose()) == 1}  z {b[2]:.2f}..{b[5]:.2f}")
    section_drawing(o, os.path.join(OUT_DIR, "onizleme", "kesit_olculer.png"))
    preview(o, items, os.path.join(OUT_DIR, "onizleme", "jant_gobegi.png"))


if __name__ == "__main__":
    main()
