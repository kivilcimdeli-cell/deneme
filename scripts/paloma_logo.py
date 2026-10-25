"""Paloma Hotels logosunu (PALOMA / HOTELS) ekran görüntüsünden vektöre çevirir.

Otelin sitesi bu ortamdan açılmadığı için logo, Instagram profilindeki görselin ekran görüntüsünden alındı: düz mavi
zemin üzerinde beyaz harfler. Harfler zeminden ayrılır (beyazlık oranı), 8 kat büyütülüp potrace ile Bézier eğrilerine
çevrilir. Çıktı:
  paloma_isimlik/logo/kaynak.png          kırpılmış kaynak (logo bölgesi)
  paloma_isimlik/logo/paloma_hotels.svg   vektör logo (currentColor, sayfada kullanılır)
  paloma_isimlik/logo/paloma_hotels.json  çokgenler (mm değil, logo genişliği = 1): "paloma" ve "hotels" satırları
  paloma_isimlik/logo/onizleme.png        kaynak ve çizim üst üste

Kullanım:
  python3 scripts/paloma_logo.py <ekran_görüntüsü> [x0 y0 x1 y1]
"""
import json
import os
import sys

import numpy as np
import potrace
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "paloma_isimlik", "logo")
UP = 8                                   # büyütme: kenarlar yumuşak eşiklensin
BLUE = (105, 161, 186)                   # logonun zemini (Paloma mavisi)


def letters_mask(crop):
    """Beyazlık oranı (zemin 0, beyaz 1), büyütülüp 0,5'ten eşiklenir."""
    a = np.asarray(crop.convert("RGB"), float)
    bg = np.median(a.reshape(-1, 3), axis=0)
    w = np.clip(((a - bg) / (255.0 - bg)).mean(axis=2), 0, 1)
    big = Image.fromarray((w * 255).astype(np.uint8)).resize((crop.width * UP, crop.height * UP), Image.BICUBIC)
    return np.asarray(big) > 127, tuple(int(v) for v in bg)


def bezier(p0, p1, p2, p3, n=10):
    t = np.linspace(0, 1, n + 1)[1:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def trace(mask):
    """Her eğri: (svg yol verisi, çokgen noktaları); koordinatlar büyütülmüş piksel."""
    path = potrace.Bitmap(mask).trace(turdsize=20, alphamax=1.0, opticurve=True, opttolerance=0.2)
    out = []
    for curve in path:
        p = np.array([curve.start_point.x, curve.start_point.y])
        d, pts = [f"M{p[0]:.1f} {p[1]:.1f}"], [p]
        for seg in curve.segments:
            e = np.array([seg.end_point.x, seg.end_point.y])
            if seg.is_corner:
                c = np.array([seg.c.x, seg.c.y])
                d.append(f"L{c[0]:.1f} {c[1]:.1f}L{e[0]:.1f} {e[1]:.1f}")
                pts += [c, e]
            else:
                c1, c2 = np.array([seg.c1.x, seg.c1.y]), np.array([seg.c2.x, seg.c2.y])
                d.append(f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {e[0]:.1f} {e[1]:.1f}")
                pts += list(bezier(pts[-1], c1, c2, e))
            p = e
        out.append(("".join(d) + "Z", np.array(pts)))
    return out


def main():
    src = sys.argv[1]
    box = tuple(int(v) for v in sys.argv[2:6]) if len(sys.argv) >= 6 else (320, 1080, 760, 1260)
    os.makedirs(OUT, exist_ok=True)
    crop = Image.open(src).convert("RGB").crop(box)
    crop.save(os.path.join(OUT, "kaynak.png"))
    mask, bg = letters_mask(crop)
    H, W = mask.shape
    curves = [(d, p) for d, p in trace(mask)                      # kırpma kenarına değen çerçeve eğrisi atılır
              if p[:, 0].min() > 2 and p[:, 1].min() > 2 and p[:, 0].max() < W - 2 and p[:, 1].max() < H - 2]
    allp = np.vstack([p for _, p in curves])
    x0, y0 = allp.min(axis=0)
    x1, y1 = allp.max(axis=0)
    w, h = x1 - x0, y1 - y0
    mid = y0 + h / 2
    # satırlar: eğrinin dikey ortası logonun üst yarısındaysa PALOMA
    rows = {"paloma": [], "hotels": []}
    for _, p in curves:
        key = "paloma" if (p[:, 1].min() + p[:, 1].max()) / 2 < mid else "hotels"
        # y yukarı, sol alt köşe (0, 0), genişlik 1
        rows[key].append([[round((x - x0) / w, 5), round((y1 - y) / w, 5)] for x, y in p])
    meta = {"kaynak": "Instagram @palomahotels profil görseli (ekran görüntüsü)", "en_boy": round(w / h, 4),
            "zemin_rengi": "#%02X%02X%02X" % bg, **rows}
    json.dump(meta, open(os.path.join(OUT, "paloma_hotels.json"), "w"), ensure_ascii=False)
    s = 1000.0 / w
    paths = "".join(d for d, _ in curves)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 {h * s:.1f}" role="img" aria-label="Paloma Hotels">'
           f'<path fill="currentColor" fill-rule="evenodd" transform="scale({s:.6f}) translate({-x0:.1f} {-y0:.1f})" '
           f'd="{paths}"/></svg>\n')
    open(os.path.join(OUT, "paloma_hotels.svg"), "w").write(svg)
    # önizleme: kaynak büyütülmüş, üstüne çizimin kenarları
    prev = crop.resize((crop.width * 3, crop.height * 3), Image.LANCZOS)
    dr = ImageDraw.Draw(prev)
    for _, p in curves:
        q = [(x * 3 / UP, y * 3 / UP) for x, y in p]
        dr.line(q + [q[0]], fill=(230, 40, 40), width=1)
    prev.save(os.path.join(OUT, "onizleme.png"))
    print(f"{len(curves)} eğri (PALOMA {len(rows['paloma'])}, HOTELS {len(rows['hotels'])}), en/boy {w / h:.3f}, "
          f"zemin #{bg[0]:02X}{bg[1]:02X}{bg[2]:02X}")


if __name__ == "__main__":
    main()
