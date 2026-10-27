"""Auto Tufan logosundaki fırça T harfini görselden vektöre çevirir.

Müşterinin gönderdiği logo görselinde koyu zemin üzerinde turuncu-altın fırça T, yanında beyaz "Auto Tufan" ve
"KAPORTA & BOYA". Yazılar isimlikte yazı tipiyle (Poppins) yeniden yazılır; T ise el yazısı olduğu için görselden
alınır: altın piksellerin oranı (kırmızı − mavi) zeminden ayrılır, 8 kat büyütülüp yumuşatılır, potrace ile Bézier
eğrilerine çevrilir. Çıktı:
  autotufan_isimlik/logo/kaynak.png    kırpılmış kaynak
  autotufan_isimlik/logo/tufan_t.svg   vektör T (currentColor)
  autotufan_isimlik/logo/tufan_t.json  çokgenler (T'nin yüksekliği = 1, y yukarı) ve SVG yolu
  autotufan_isimlik/logo/onizleme.png  kaynak ve çizim yan yana

Kullanım:
  python3 scripts/autotufan_logo.py <logo_görseli>
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paloma_logo as PL  # noqa: E402  (bezier, trace, path_data)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "autotufan_isimlik", "logo")
JSON = os.path.join(OUT, "tufan_t.json")
UP = PL.UP


def gold_mask(crop):
    """Altınlık oranı: (kırmızı − mavi), zeminde ~0, T'de ~1; büyütülüp yumuşatılır ve 0,5'ten eşiklenir."""
    a = np.asarray(crop.convert("RGB"), float)
    g = a[..., 0] - a[..., 2]
    lo, hi = np.percentile(g, 50), np.percentile(g, 99.5)
    w = np.clip((g - lo) / (hi - lo), 0, 1)
    big = Image.fromarray((w * 255).astype(np.uint8)).resize((crop.width * UP, crop.height * UP), Image.BICUBIC)
    big = big.filter(ImageFilter.GaussianBlur(5))
    return np.asarray(big) > 127


def main():
    src = Image.open(sys.argv[1]).convert("RGB")
    a = np.asarray(src, int)
    ys, xs = np.where(a[..., 0] - a[..., 2] > 60)              # altın pikseller (beyaz yazıda kırmızı ≈ mavi)
    pad = 8
    box = (max(0, xs.min() - pad), max(0, ys.min() - pad), min(src.width, xs.max() + pad + 1),
           min(src.height, ys.max() + pad + 1))
    crop = src.crop(box)
    os.makedirs(OUT, exist_ok=True)
    crop.save(os.path.join(OUT, "kaynak.png"))
    mask = gold_mask(crop)
    edge = 2 * UP                                            # kırpma kenarına değen eğri (zeminin çerçevesi) atılır
    curves = [c for c in PL.trace(mask) if c[1][:, 0].min() > edge and c[1][:, 1].min() > edge
              and c[1][:, 0].max() < mask.shape[1] - edge and c[1][:, 1].max() < mask.shape[0] - edge]
    pts = np.vstack([p for _, p in curves])
    x0, y0, x1, y1 = pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max()
    h = y1 - y0
    rings = [[[float((x - x0) / h), float((y1 - y) / h)] for x, y in p] for _, p in curves]   # yükseklik 1, y yukarı
    vb_h = 1000.0
    k = vb_h / h
    d = "".join(PL.path_data(segs, lambda p: ((p[0] - x0) * k, (p[1] - y0) * k)) for segs, _ in curves)
    w = (x1 - x0) / h
    json.dump({"t": rings, "en_boy": w, "svg_boyut": [w * vb_h, vb_h], "d": d},
              open(JSON, "w", encoding="utf-8"))
    with open(os.path.join(OUT, "tufan_t.svg"), "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w * vb_h:.0f} {vb_h:.0f}" '
                f'fill="currentColor" fill-rule="evenodd"><path d="{d}"/></svg>\n')
    # önizleme: kaynak (büyütülmüş) ve çizim
    H = 400
    s = H / crop.height
    left = crop.resize((int(crop.width * s), H), Image.LANCZOS)
    right = Image.new("RGB", left.size, (30, 30, 32))
    m = Image.new("1", (left.width * 2, H * 2), 0)
    for ring in curves:
        mm = Image.new("1", m.size, 0)
        ImageDraw.Draw(mm).polygon([(x / UP * s * 2, y / UP * s * 2) for x, y in ring[1]], fill=1)
        m = Image.fromarray(np.asarray(m) ^ np.asarray(mm))
    m = m.convert("L").resize(left.size, Image.LANCZOS)
    right.paste((228, 189, 104), (0, 0), m)
    sheet = Image.new("RGB", (left.width * 2 + 30, H + 20), (236, 239, 244))
    sheet.paste(left, (10, 10))
    sheet.paste(right, (left.width + 20, 10))
    sheet.save(os.path.join(OUT, "onizleme.png"))
    print(f"{len(curves)} eğri, en/boy {w:.3f} -> {os.path.relpath(JSON, ROOT)}")


def polygons():
    """Çokgenler (T yüksekliği 1)."""
    return json.load(open(JSON, encoding="utf-8"))["t"]


if __name__ == "__main__":
    main()
