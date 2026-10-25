"""Paloma Hotels logosunu (PALOMA / HOTELS) ekran görüntüsünden vektöre çevirir.

Otelin sitesi bu ortamdan açılmadığı için logo, Instagram profilindeki görselin ekran görüntüsünden alındı: düz mavi
zemin üzerinde beyaz harfler. Harfler zeminden ayrılır (beyazlık oranı), 8 kat büyütülüp potrace ile Bézier eğrilerine
çevrilir. Çıktı:
  paloma_isimlik/logo/kaynak.png          kırpılmış kaynak (logo bölgesi)
  paloma_isimlik/logo/paloma_hotels.svg   vektör logo (currentColor)
  paloma_isimlik/logo/paloma_hotels.json  çokgenler (logo genişliği = 1; "paloma" ve "hotels" satırları) ve harf harf
                                          SVG yolları ("harfler", 1000 birim genişlikte; sayfadaki animasyon için)
  paloma_isimlik/logo/onizleme.png        kaynak ve çizim üst üste

Kullanım:
  python3 scripts/paloma_logo.py <ekran_görüntüsü> [x0 y0 x1 y1]
"""
import json
import os
import sys

import numpy as np
import potrace
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "paloma_isimlik", "logo")
JSON = os.path.join(OUT, "paloma_hotels.json")
UP = 8                                   # büyütme: kenarlar yumuşak eşiklensin
VB = 1000.0                              # SVG genişliği (birim)


def letters_mask(crop):
    """Beyazlık oranı (zemin 0, beyaz 1), büyütülüp yumuşatılır (JPEG pürüzü kenarı tırtıklamasın) ve 0,5'ten
    eşiklenir."""
    a = np.asarray(crop.convert("RGB"), float)
    bg = np.median(a.reshape(-1, 3), axis=0)
    w = np.clip(((a - bg) / (255.0 - bg)).mean(axis=2), 0, 1)
    big = Image.fromarray((w * 255).astype(np.uint8)).resize((crop.width * UP, crop.height * UP), Image.BICUBIC)
    big = big.filter(ImageFilter.GaussianBlur(5))
    return np.asarray(big) > 127, tuple(int(v) for v in bg)


def bezier(p0, p1, p2, p3, n=10):
    t = np.linspace(0, 1, n + 1)[1:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def trace(mask):
    """Her eğri: (bölümler, çokgen noktaları). Bölüm: ("L", köşe, uç) ya da ("C", k1, k2, uç); büyütülmüş piksel."""
    path = potrace.Bitmap(mask).trace(turdsize=20, alphamax=1.0, opticurve=True, opttolerance=0.5)
    out = []
    for curve in path:
        start = np.array([curve.start_point.x, curve.start_point.y])
        segs, pts = [("M", start)], [start]
        for seg in curve.segments:
            e = np.array([seg.end_point.x, seg.end_point.y])
            if seg.is_corner:
                c = np.array([seg.c.x, seg.c.y])
                segs.append(("L", c, e))
                pts += [c, e]
            else:
                c1, c2 = np.array([seg.c1.x, seg.c1.y]), np.array([seg.c2.x, seg.c2.y])
                segs.append(("C", c1, c2, e))
                pts += list(bezier(pts[-1], c1, c2, e))
        out.append((segs, np.array(pts)))
    return out


def path_data(segs, f):
    """SVG yol verisi; f: nokta dönüşümü."""
    out = []
    for kind, *ps in segs:
        q = [f(p) for p in ps]
        out.append(kind + " ".join(f"{x:.1f} {y:.1f}" for x, y in q))
    return "".join(out) + "Z"


def letters(curves):
    """Eğrileri harflere toplar: başka bir eğrinin kutusu içinde kalan eğri (P, A, O'nun içi) o harfin deliğidir."""
    boxes = [(p[:, 0].min(), p[:, 1].min(), p[:, 0].max(), p[:, 1].max()) for _, p in curves]
    inside = lambda a, b: a[0] > b[0] and a[1] > b[1] and a[2] < b[2] and a[3] < b[3]  # noqa: E731
    outer = [k for k, b in enumerate(boxes) if not any(inside(b, o) for j, o in enumerate(boxes) if j != k)]
    groups = {k: [k] for k in outer}
    for k, b in enumerate(boxes):
        if k not in groups:
            groups[next(o for o in outer if inside(b, boxes[o]))].append(k)
    return sorted(groups.values(), key=lambda g: (boxes[g[0]][1] > np.mean([b[1] for b in boxes]), boxes[g[0]][0]))


def raster(height, colour=(255, 255, 255)):
    """Logoyu (çift-tek kuralıyla delikli) RGBA görsele çizer; yükseklik piksel."""
    d = json.load(open(JSON, encoding="utf-8"))
    ss = 4
    w = int(round(height * d["en_boy"]))
    mask = Image.new("1", (w * ss, height * ss), 0)
    k = w * ss
    for key in ("paloma", "hotels"):
        for ring in d[key]:
            m = Image.new("1", mask.size, 0)
            ImageDraw.Draw(m).polygon([(x * k, height * ss - y * k) for x, y in ring], fill=1)
            mask = Image.fromarray(np.asarray(mask) ^ np.asarray(m))
    a = mask.convert("L").resize((w, height), Image.LANCZOS)
    im = Image.new("RGBA", (w, height), tuple(colour) + (0,))
    im.putalpha(a)
    return im


def main():
    src = sys.argv[1]
    box = tuple(int(v) for v in sys.argv[2:6]) if len(sys.argv) >= 6 else (320, 1080, 760, 1260)
    os.makedirs(OUT, exist_ok=True)
    crop = Image.open(src).convert("RGB").crop(box)
    crop.save(os.path.join(OUT, "kaynak.png"))
    mask, bg = letters_mask(crop)
    H, W = mask.shape
    curves = [(s, p) for s, p in trace(mask)                      # kırpma kenarına değen çerçeve eğrisi atılır
              if p[:, 0].min() > 2 and p[:, 1].min() > 2 and p[:, 0].max() < W - 2 and p[:, 1].max() < H - 2]
    allp = np.vstack([p for _, p in curves])
    x0, y0 = allp.min(axis=0)
    x1, y1 = allp.max(axis=0)
    w, h = x1 - x0, y1 - y0
    mid = y0 + h / 2
    s = VB / w
    svg_pt = lambda p: ((p[0] - x0) * s, (p[1] - y0) * s)  # noqa: E731
    # satırlar: eğrinin dikey ortası logonun üst yarısındaysa PALOMA
    rows = {"paloma": [], "hotels": []}
    row_of = lambda p: "paloma" if (p[:, 1].min() + p[:, 1].max()) / 2 < mid else "hotels"  # noqa: E731
    for _, p in curves:
        # y yukarı, sol alt köşe (0, 0), genişlik 1
        rows[row_of(p)].append([[round((x - x0) / w, 5), round((y1 - y) / w, 5)] for x, y in p])
    harfler = []
    for g in letters(curves):
        p = np.vstack([curves[k][1] for k in g])
        harfler.append({"satir": row_of(curves[g[0]][1]), "d": "".join(path_data(curves[k][0], svg_pt) for k in g),
                        "x": round(((p[:, 0].min() + p[:, 0].max()) / 2 - x0) * s, 1)})
    meta = {"kaynak": "Instagram @palomahotels profil görseli (ekran görüntüsü)", "en_boy": round(w / h, 4),
            "zemin_rengi": "#%02X%02X%02X" % bg, "svg_boyut": [VB, round(h * s, 1)], "harfler": harfler, **rows}
    json.dump(meta, open(JSON, "w", encoding="utf-8"), ensure_ascii=False)
    paths = "".join(path_data(sg, svg_pt) for sg, _ in curves)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VB:.0f} {h * s:.1f}" role="img" '
           f'aria-label="Paloma Hotels"><path fill="currentColor" fill-rule="evenodd" d="{paths}"/></svg>\n')
    open(os.path.join(OUT, "paloma_hotels.svg"), "w").write(svg)
    # önizleme: kaynak büyütülmüş, üstüne çizimin kenarları
    prev = crop.resize((crop.width * 3, crop.height * 3), Image.LANCZOS)
    dr = ImageDraw.Draw(prev)
    for _, p in curves:
        q = [(x * 3 / UP, y * 3 / UP) for x, y in p]
        dr.line(q + [q[0]], fill=(230, 40, 40), width=1)
    prev.save(os.path.join(OUT, "onizleme.png"))
    print(f"{len(curves)} eğri, {len(harfler)} harf (PALOMA {len(rows['paloma'])} eğri, HOTELS {len(rows['hotels'])}), "
          f"en/boy {w / h:.3f}, zemin #{bg[0]:02X}{bg[1]:02X}{bg[2]:02X}")


if __name__ == "__main__":
    main()
