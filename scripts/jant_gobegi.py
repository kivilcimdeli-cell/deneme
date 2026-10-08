"""Ford jant göbeği (8 tırnaklı, Ø53, Ford logolu) – Bambu Lab X2D için desteksiz baskıya hazır 3MF
ve tırnak deneme halkası.

Ölçüler: kumpaslı fotoğraflardan okunanlar (ÖLÇÜLDÜ), fotoğraftaki oranlardan çıkarılanlar (FOTOĞRAF) ve
fotoğraftan okunamayan yükseklikler (TAHMİN). Tahmin olanlar ölçülüp OLCU sözlüğünde değiştirilince betik
her şeyi yeniden üretir.

Yapı (kesit; z = 0 flanşın arka yüzü, ön yüz z = T):
  * flanş: arkada en geniş Ø D; yan yüz öne doğru daralır, ön yüz kenarı Ø `on_cap` (orijinaldeki gibi)
  * ön yüzde Ford logosu, yüzeyle aynı hizada (orijinal etiket gibi düz): siyah kenar halkası, Ø `zemin_cap`
    beyaz zemin, mavi oval, beyaz "Ford" yazısı ve oval çizgisi. Mavi 2 katman, beyaz 4 katman (mavinin arkasını da
    doldurur, böylece beyaz opak, son 2 katmanda yalnız beyaz var).
    Logo çizimi: Simple Icons (scripts/logolar/ford.svg, CC0); Ford logosu Ford Motor Company'nin markasıdır.
  * arka yüzde 8 tırnaklı halka: gövde dış çapı `tirnak_od`, iç çapı `tirnak_id`, boy `L`;
    uçta dışa doğru diş (`dis_od`): uçtaki rampa takarken içe esnetir, arkasındaki eğik yüz jant deliğine tutunur;
    tırnaklar arasında `yarik` genişliğinde 8 yarık; tırnak kökünde iç pah (kırılmaya karşı)

Baskı: ÖN YÜZ TABLADA, tırnaklar yukarıda. Hiçbir yerde destek gerekmez: yan yüz 30° eğimle genişler,
flanşın arka yüzü ve tırnaklar üstte kalır. Logo tabla yüzeyine basıldığı için en düzgün ve keskin yüz olur.
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
    "D": 53.3,           # en geniş dış çap (flanşın arkası)      ÖLÇÜLDÜ: 53,30 / 53,50 / 52,90
    "on_cap": 50.2,      # ön yüz kenarı çapı (yan yüz eğimli)    FOTOĞRAF (kenar ~1,55 mm içeride)
    "zemin_cap": 46.2,   # logo zemini (orijinal etiket yuvası)  FOTOĞRAF (etiket ~44,7, yuva ~46)
    "T": 5.0,            # flanş kalınlığı (ön yüz - arka yüz)    TAHMİN
    "tirnak_od": 47.5,   # tırnak gövdesi dış çapı               diş çapı - 2 × 0,5
    "dis_od": 48.5,      # tırnak dişleri dış çapı               ÖLÇÜLDÜ: 48,5
    "tirnak_id": 42.9,   # tırnak iç çapı                        ÖLÇÜLDÜ: 42,85
    "L": 10.0,           # tırnak boyu (arka yüzden uca)         TAHMİN
    "n": 8,              # tırnak sayısı                         FOTOĞRAF
    "yarik": 3.0,        # tırnaklar arası yarık                 FOTOĞRAF
    "logo_en": 41.6,     # Ford ovalinin eni                     FOTOĞRAF (zeminin 0,93'ü)
    "logo_boy": 16.3,    # Ford ovalinin boyu                    FOTOĞRAF (en/boy 2,55)
}
INLAY, MAVI = 0.8, 0.4                  # ön yüz renk derinliği (beyaz 4 katman), mavi oval 2 katman
ZEMIN_RENK = A.WHITE                    # logo zemini (yazı ve oval çizgisi her zaman beyaz)
YAZI_KALINLASTIR = 0.1                  # beyaz yazıyı her yandan kalınlaştır: ince kıvrımlar 0,4 nozulla basılsın
RAMPA, DUZ, TUTUNMA = 1.6, 0.4, 0.6     # diş: uçtaki rampa, düz kısım, tutunma yüzü (eksenel, mm)
SEG = 256


def section(o, flange=True, ring_ri=None):
    """Döndürülecek yarım kesit (x = yarıçap, y = z). ring_ri: deneme halkasında flanşın iç yarıçapı."""
    R, Rf, T = o["D"] / 2, o["on_cap"] / 2, o["T"]
    Rc, Rb, Ri, L = o["tirnak_od"] / 2, o["dis_od"] / 2, o["tirnak_id"] / 2, o["L"]
    parts = []
    if flange:
        rf = 0.4                                               # ön dış kenar yuvarlatma
        arc = [(Rf - rf + rf * np.cos(a), T - rf + rf * np.sin(a)) for a in np.linspace(0, np.pi / 2, 8)]
        parts.append(A.polygon([(0, 0), (R - 0.4, 0), (R, 0.4), (R, 1.2), *arc, (0, T)]))
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


def ford_logo(width, height):
    """Ford ovali: (mavi kısım, beyaz kısımlar = oval çizgisi + yazı). Merkez (0, 0), y yukarı."""
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
    blue = blue.translate((-(x0 + x1) / 2, -(y0 + y1) / 2)).scale((width / (x1 - x0), -height / (y1 - y0)))
    area = lambda p: abs(np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1]))  # noqa: E731
    oval = m3.CrossSection([max(blue.to_polygons(), key=area)])
    white = ((oval - blue).offset(YAZI_KALINLASTIR, m3.JoinType.Round) ^ oval.offset(-0.3, m3.JoinType.Round))
    return oval - white, white


def cap_parts(o):
    """Renkli parçalar, kendi ekseninde (ön yüz +z): gövde (siyah), zemin + yazı (beyaz), oval (mavi)."""
    T = o["T"]
    blue2d, _ = ford_logo(o["logo_en"], o["logo_boy"])
    disc = A.circle(o["zemin_cap"] / 2, 0, 0, SEG)
    mavi = blue2d.extrude(MAVI).translate((0, 0, T - MAVI))
    beyaz = disc.extrude(INLAY).translate((0, 0, T - INLAY)) - mavi      # zemin, yazı, çizgi ve mavinin arkası
    body = P.clean(cap(o) - disc.extrude(INLAY + 1.0).translate((0, 0, T - INLAY)))
    return [("Gövde (siyah)", body, A.BLACK), ("Zemin, Ford yazısı ve çizgi (beyaz)", P.clean(beyaz), ZEMIN_RENK),
            ("Oval (mavi)", mavi, A.BLUE)]


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


def face_down(m, z_front):
    """Ön yüzü tablaya yatırır: x ekseni etrafında 180° döndürme (aynalama değil: logo ters basılmasın)."""
    return m.rotate((180, 0, 0)).translate((0, 0, z_front))


def parts(o):
    c = [(n, face_down(m, o["T"]), e) for n, m, e in cap_parts(o)]     # ön yüz tablada, tırnaklar yukarı
    r = face_down(test_ring(o), 1.6)                                    # deneme: flanş halkası tablada
    common = {"wall_loops": "3", "sparse_infill_density": "25%", "brim_type": "no_brim", "enable_support": "0"}
    return [Part("ford_jant_gobegi", "Ford_jant_gobegi_53mm", c, common),
            Part("tirnak_deneme_halkasi", "Ford_jant_gobegi_tirnak_deneme", [("Tırnak deneme halkası", r, A.BLACK)],
                 common)]


# ---------------------------------------------------------------- görseller

def section_drawing(o, path):
    """Ölçülü kesit resmi: ölçülen ve tahmin edilen ölçüler ayrı renkte."""
    s = 13.0
    W, H = 1500, 760
    im = Image.new("RGB", (W, H), (244, 245, 247))
    dr = ImageDraw.Draw(im)
    dr.text((40, 24), "FORD JANT GÖBEĞİ – KESİT VE ÖLÇÜLER (mm)", fill=(24, 26, 30), font=K.fnt(32))
    dr.text((40, 68), "Yeşil: kumpastan okundu   ·   Mavi: fotoğraftaki oranlardan   ·   Turuncu: tahmin, kumpasla ölçün",
            fill=(96, 100, 110), font=K.fnt(20))
    cx, cy = W / 2, 400
    cs = section(o)
    for sign in (1, -1):
        for p in cs.to_polygons():
            dr.polygon([(cx + sign * x * s, cy - y * s) for x, y in p], fill=(52, 54, 60))
    zr, T0 = o["zemin_cap"] / 2, o["T"]
    dr.rectangle((cx - zr * s, cy - T0 * s, cx + zr * s, cy - (T0 - INLAY) * s), fill=(236, 236, 230))   # beyaz zemin
    dr.rectangle((cx - o["logo_en"] / 2 * s, cy - T0 * s, cx + o["logo_en"] / 2 * s, cy - (T0 - MAVI) * s),
                 fill=A.SHOW[A.BLUE])                                                                      # mavi oval
    dr.line((cx, 120, cx, 680), fill=(160, 164, 172), width=1)
    green, orange, blue = (30, 140, 70), (220, 120, 20), (40, 90, 170)
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
    hdim(-R, R, cy - T * s - 40, f"A  en geniş dış çap {o['D']:.1f} (arka kenar)", green)
    hdim(-o["on_cap"] / 2, o["on_cap"] / 2, cy - T * s - 90, f"ön yüz Ø{o['on_cap']:.1f}", blue)
    hdim(-zr, zr, cy - T * s - 140, f"logo zemini Ø{o['zemin_cap']:.1f}  ·  oval {o['logo_en']:.1f} × {o['logo_boy']:.1f}",
         blue)
    hdim(-o["dis_od"] / 2, o["dis_od"] / 2, cy + L * s + 40, f"B  tırnak dişleri {o['dis_od']:.1f}", green, up=False)
    hdim(-o["tirnak_id"] / 2, o["tirnak_id"] / 2, cy + L * s + 100, f"C  tırnak içi {o['tirnak_id']:.1f}",
         green, up=False)
    vdim(R + 2.5, 0, T, f"D  flanş kalınlığı {T:.1f}", orange)
    vdim(R + 2.5, -L, 0, f"E  tırnak boyu {L:.1f}", orange)
    vdim(-(R + 2.5), -L, T, f"toplam yükseklik {T + L:.1f}", orange, right=False)
    dr.text((40, 700), f"8 tırnak, aralarında {o['yarik']:.1f} mm yarık · logo yüzle aynı hizada (beyaz {INLAY}, mavi {MAVI} mm) · "
                       f"diş: uçta {RAMPA} mm rampa, {o['dis_od'] / 2 - o['tirnak_od'] / 2:.1f} mm dışa taşar",
            fill=(70, 74, 84), font=K.fnt(19))
    im.save(path)
    return im


def preview(o, items, path):
    cap_v = [(*A.mesh_arrays(m), A.SHOW[e]) for _, m, e in cap_parts(o)]
    bed_v = [(*A.mesh_arrays(m), A.SHOW[e]) for _, m, e in items[0].solids()]
    ring_v = [(*A.mesh_arrays(items[1].man), A.SHOW[A.BLACK])]
    views = [("ÖN YÜZ", cap_v, rotation(0, 0)), ("PERSPEKTİF", cap_v, rotation(-25, -55)),
             ("ARKA (TIRNAKLAR)", cap_v, rotation(155, 125)), ("TABLADA (desteksiz)", bed_v, rotation(-30, -60)),
             ("TIRNAK DENEME HALKASI", ring_v, rotation(-30, -60))]
    W, H = 1500, 600
    canvas = Image.new("RGB", (W, H), (244, 245, 247))
    dr = ImageDraw.Draw(canvas)
    dr.text((40, 24), "FORD JANT GÖBEĞİ – BASKIYA HAZIR, DESTEKSİZ", fill=(24, 26, 30), font=K.fnt(32))
    dr.text((40, 68), f"Ø{o['D']:.1f} × {o['T'] + o['L']:.1f} mm · 8 tırnak · ön yüz tablada basılır, destek yok · "
                      f"logo yüzle aynı hizada: beyaz zemin, mavi oval, beyaz yazı", fill=(96, 100, 110), font=K.fnt(20))
    for i, (label, mesh, R) in enumerate(views):
        box = (40 + i * 287, 120, 40 + i * 287 + 271, 500)
        K.panel(dr, box)
        img = A.fit_into(render(mesh, 1000, R, margin=0.02), 235, 300)
        K.paste_center(canvas, img, (box[0], box[1] + 30, box[2], box[3]))
        dr.text((box[0] + 18, box[1] + 16), label, fill=(120, 124, 134), font=K.fnt(15))
    _, changes, flush = items[0].colour_changes()
    ams = " · ".join(f"{i} {A.COLOUR_NAMES[f]}" for i, f in enumerate(sorted({e for _, _, e in items[0].solids()}), 1))
    dr.text((40, 530), f"AMS: {ams}   ·   filament değişimi: {changes} (~{flush} mm³)   ·   "
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
