"""AUTO FIRAT TUYGUN kurumsal anahtarlıklar: müşterinin seçtiği konseptlerin (1, 2, 3, 6, 7, 9)
baskıya hazır Bambu Lab X2D 3MF dosyaları.

Geometri scripts/anahtarlik_konsept.py'deki konseptlerden gelir (görsellerle birebir). Baskı için:
  * ön yüz (yukarı bakan): logo ve yazılar 0,8 mm (4 katman) KABARTMA
  * arka yüz (tablaya bakan): telefon ve şehir ilk 3 katmanda gömme renk; tabla yüzeyi kadar düz ve keskin
  * arka yazılar tek renk (siyah gövdede beyaz). Böylece 3 renkli tasarımlarda siyah + altın aynı nozulu,
    beyaz diğer nozulu kullanır ve bütün baskıda yalnızca 1 filament değişimi olur.
  * gövde 3,2 mm; alt ve üst kenarda 3 katmanlık pah (ilk katman 0,6 mm içeride: fil ayağı yapmaz)
  * yazılar kenardan en az 1 mm, delikten en az 0,8 mm içeride; delik çevresinde en az 3 mm et

Çıktı : anahtarlik/kurumsal_baski/<tasarım>.3mf, anahtarlik/kurumsal_baski/onizleme/*.png

Kullanım:
  python3 scripts/anahtarlik_kurumsal.py            # hepsi
  python3 scripts/anahtarlik_kurumsal.py kapsul     # yalnız adında "kapsul" geçen
"""
import itertools
import os
import sys
import zipfile

import manifold3d as m3
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import anahtarlik_konsept as K  # noqa: E402
from capraz_blok import estimate_grams  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "anahtarlik", "kurumsal_baski")
SELECTED = [K.k1_kapsul, K.k2_logo_kare, K.k3_madalyon, K.k6_tek_cizgi, K.k7_altigen, K.k9_kose_serit]
COL = {K.BLACK: A.BLACK, K.WHITE: A.WHITE, K.GOLD: A.GOLD}

BODY_H = 3.2                     # gövde (16 katman), arka gömme yazılar dahil
RAISE = A.RAISE_H                # ön kabartma 0,8 mm (4 katman)
INLAY = 0.6                      # arka gömme yazı derinliği (3 katman; beyaz siyahı göstermez)
CHAMFER_STEPS = 3                # kenar pahı: 3 katman × 0,2 mm
J = m3.JoinType.Round


def clean(man, min_vol=0.05):
    """Boolean sonrası kalan sıfır hacimli kırıntıları atar."""
    return m3.Manifold.batch_boolean([p for p in man.decompose() if p.volume() > min_vol], m3.OpType.Add)


class Keychain:
    def __init__(self, concept, keep_back_colours=False):
        """keep_back_colours: arka yüz konseptteki renklerle basılır (yoksa tek renk: daha az renk değişimi)."""
        c = self.concept = concept
        self.key, self.title, self.desc = c.key, "AUTO_FIRAT_TUYGUN_" + c.key, c.desc
        self.body_col = COL[c.body]
        back_col = A.WHITE if self.body_col == A.BLACK else A.BLACK
        x0, y0, x1, y1 = (c.outline - c.holes).bounds()
        self.shift = (-(x0 + x1) / 2, -(y0 + y1) / 2)          # tablada ortalamak için
        self.outline, self.holes = c.outline, c.holes
        self.front = [(cs, COL[col]) for cs, col in c.front]
        self.back = [(cs.mirror((1, 0)), COL[col] if keep_back_colours else back_col)
                     for cs, col in c.back]                                   # tablaya bakan hâli (alttan)
        self.keep = (self.outline - self.holes).offset(-A.EDGE_KEEP, J) - self.holes.offset(0.8, J)

    def size(self):
        return self.concept.size()

    def regions(self, items):
        """Filament başına bölgeler; sonra gelen öğe öncekinin üstüne yazar, kıl payı adacıklar atılır."""
        out, taken = {}, A.empty()
        for cs, ext in reversed(items):
            part = (cs ^ self.keep) - taken
            taken = taken + cs
            out[ext] = out.get(ext, A.empty()) + part
        return {e: A.union(*[p for p in cs.decompose() if p.area() > 0.3]) for e, cs in out.items()}

    def body(self):
        shape = self.outline - self.holes
        body = shape.extrude(BODY_H)
        rings = []
        for k in range(CHAMFER_STEPS):          # alt ve üst kenarda katmanlara oturan pah
            ring = shape - shape.offset(-A.CHAMFER * (CHAMFER_STEPS - k) / CHAMFER_STEPS, J)
            lo = -0.1 if k == 0 else 0.0
            rings.append(ring.extrude(A.LAYER - lo).translate((0, 0, k * A.LAYER + lo)))
            hi = 0.1 if k == 0 else 0.0
            rings.append(ring.extrude(A.LAYER + hi).translate((0, 0, BODY_H - (k + 1) * A.LAYER)))
        return body - m3.Manifold.batch_boolean(rings, m3.OpType.Add)

    def solids(self):
        body = self.body()
        parts = []
        back = self.regions(self.back)
        for ext, cs in sorted(back.items()):
            m = cs.extrude(INLAY)
            body = body - m
            parts.append((f"Arka yazı ({A.COLOUR_NAMES[ext]})", m, ext))
        for ext, cs in sorted(self.regions(self.front).items()):
            parts.append((f"Ön kabartma ({A.COLOUR_NAMES[ext]})", cs.extrude(RAISE).translate((0, 0, BODY_H)), ext))
        parts.insert(0, (f"Gövde ({A.COLOUR_NAMES[self.body_col]})", clean(body), self.body_col))
        dx, dy = self.shift
        return [(n, m.translate((dx, dy, 0)), e) for n, m, e in parts]

    # ------------------------------------------------------------ kontroller

    def layer_colours(self):
        """Katman başına kullanılan filamentler."""
        n_body, n_back, n_top = round(BODY_H / A.LAYER), round(INLAY / A.LAYER), round(RAISE / A.LAYER)
        back = set(self.regions(self.back))
        front = set(self.regions(self.front))
        return [{self.body_col} | (back if i < n_back else set()) for i in range(n_body)] + [front] * n_top

    def colour_changes(self):
        """En iyi nozul gruplaması (X2D: 2 nozul) ve o gruplamada filament değişimi sayısı / temizleme hacmi."""
        layers = self.layer_colours()
        fils = sorted(set().union(*layers))
        best = None
        for mask in itertools.product((1, 2), repeat=len(fils)):
            group = dict(zip(fils, mask))
            changes, flush = 0, 0
            for nozzle in (1, 2):
                loaded = None
                seq = [[f for f in L if group[f] == nozzle] for L in layers]
                for i, need in enumerate(seq):
                    if not need:
                        continue
                    nxt = next((s for s in seq[i + 1:] if s), [])
                    order = sorted(need, key=lambda f: (f != loaded, f in nxt))   # yüklü olan önce, sonra lazım olan sona
                    for f in order:
                        if loaded is not None and f != loaded:
                            changes += 1
                            flush += A.FLUSH[loaded - 1][f - 1]
                        loaded = f
            if best is None or (changes, flush) < best[1:]:
                best = (group, changes, flush)
        return best

    def checks(self):
        d = A.Design(self.key, self.title, self.outline, self.front, self.holes)
        thin, gaps, _ = d.check()
        back = A.union(*self.regions(self.back).values())
        back_thin = back - back.offset(-0.25, J).offset(0.25, J)        # ilk katmanda 0,5 mm'den ince çizgi
        lost = [i for i, (cs, _) in enumerate(self.front + self.back)
                if (cs ^ self.keep).area() + 0.01 < cs.area() * 0.98]
        return {"ince kabartma": thin.area(), "dar boşluk": gaps.area(), "yakın öğe": d.check_pairs(),
                "arka ince": sum(p.area() for p in back_thin.decompose() if p.area() > 0.05),
                "delik et payı": d.hole_wall(), "kırpılan": lost}


# ---------------------------------------------------------------- önizleme

def preview(kc, parts, filaments, path, title=None):
    shaded = [(*A.mesh_arrays(m), A.SHOW[e]) for _, m, e in parts]
    views = [("ÖN YÜZ (kabartma)", rotation(0, 0)), ("ARKA YÜZ (tablaya bakan)", rotation(180, 180)),
             ("PERSPEKTİF", rotation(-22, -50))]
    W, H = 1500, 700
    canvas = Image.new("RGB", (W, H), (244, 245, 247))
    dr = ImageDraw.Draw(canvas)
    dr.text((40, 26), title or kc.concept.title.upper() + " – BASKIYA HAZIR", fill=(24, 26, 30), font=K.fnt(34))
    w, h = kc.size()
    dr.text((40, 72), f"{w:.0f} × {h:.0f} × {BODY_H + RAISE:.1f} mm  ·  ön yüz {RAISE:.1f} mm kabartma  ·  "
                      f"arka yüz ilk {round(INLAY / A.LAYER)} katmanda gömme renk",
            fill=(96, 100, 110), font=K.fnt(20))
    for i, (label, R) in enumerate(views):
        box = (40 + i * 480, 120, 40 + i * 480 + 460, 120 + 440)
        K.panel(dr, box)
        im = A.fit_into(render(shaded, 1000, R, margin=0.02), 380, 340)
        K.paste_center(canvas, im, (box[0], box[1] + 30, box[2], box[3]))
        dr.text((box[0] + 22, box[1] + 18), label, fill=(120, 124, 134), font=K.fnt(17))
    group, changes, flush = kc.colour_changes()
    grams = estimate_grams(parts)
    x = 40
    for i, f in enumerate(filaments, 1):
        label = f"AMS {i}: {A.COLOUR_NAMES[f]} (~{grams.get(f, 0):.1f} g)"
        dr.rounded_rectangle((x, 590, x + 22, 612), 6, fill=A.SHOW[f], outline=(150, 154, 162), width=1)
        dr.text((x + 32, 590), label, fill=(70, 74, 84), font=K.fnt(18))
        x += 70 + dr.textlength(label, font=K.fnt(18))
    nozzles = " · ".join(f"nozul {n}: " + " + ".join(A.COLOUR_NAMES[f] for f in filaments if group[f] == n)
                         for n in (1, 2) if any(group[f] == n for f in filaments))
    dr.text((40, 634), f"Önerilen nozul grubu: {nozzles}  ·  filament değişimi: {changes} "
                       f"(~{flush} mm³ temizleme)  ·  destek yok", fill=(70, 74, 84), font=K.fnt(18))
    canvas.save(path)
    return canvas


def main():
    only = sys.argv[1:]
    template = zipfile.ZipFile(A.TEMPLATE)
    template_files = {n: template.read(n) for n in template.namelist()}
    os.makedirs(os.path.join(OUT_DIR, "onizleme"), exist_ok=True)
    sheets = []
    for fn in SELECTED:
        kc = Keychain(fn())
        if only and not any(o in kc.key for o in only):
            continue
        path, _, filaments = A.write_design(kc, template_files, OUT_DIR)
        parts = kc.solids()
        mans = [m for _, m, _ in parts]
        union = m3.Manifold.batch_boolean(mans, m3.OpType.Add)
        overlap = max((mans[i] ^ mans[j]).volume() for i in range(len(mans)) for j in range(i + 1, len(mans)))
        bb = union.bounding_box()
        group, changes, flush = kc.colour_changes()
        print(f"{os.path.relpath(path, A.ROOT)}  {kc.size()[0]:.0f}×{kc.size()[1]:.0f} mm  "
              f"AMS: {', '.join(A.COLOUR_NAMES[f] for f in filaments)}")
        print("  " + "  ".join(f"{k}: {v:.1f}" if isinstance(v, float) else f"{k}: {v}" for k, v in kc.checks().items()))
        print(f"  sağlam: {all(str(m.status()).endswith('NoError') for m in mans)}  örtüşme: {overlap:.4f} mm³  "
              f"tek gövde: {len(union.decompose()) == 1}  z {bb[2]:.1f}..{bb[5]:.1f}  "
              f"filament değişimi: {changes} (~{flush} mm³)")
        sheets.append(preview(kc, parts, filaments, os.path.join(OUT_DIR, "onizleme", kc.key + ".png")))
    if not only:
        K.stack(sheets, os.path.join(OUT_DIR, "onizleme", "hepsi.png"))


if __name__ == "__main__":
    main()
