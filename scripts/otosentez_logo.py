"""OTO SENTEZ logosunu görselden vektöre çevirir: gri küre (üç kavisli şerit) ve mavi "OTO SENTEZ" yazısı.

Müşterinin logosu (telefondan Google görsel ekran görüntüsü, 1080 × 2340): beyaz zeminde gri, metalik, üç kavisli
şeritten küre; altında lacivert, kalın, tırnaklı "OTO SENTEZ" ve küçük "ÇIKMA - YENİ YEDEK PARÇA". Küre ve büyük yazı
görselden alınır (yazı tipi bulunamayan özel çizim); alt satır isimlikte yazı tipiyle yeniden yazılır (görselde
~25 piksel, vektöre çevrilemeyecek kadar küçük).

Maske: küre için koyuluk (255 − en parlak kanal; gri, doygunluk düşük), yazı için mavilik (mavi − kırmızı). 8 kat
büyütülüp yumuşatılır, potrace ile Bézier eğrilerine çevrilir (scripts/paloma_logo.py).

Çıktı (otosentez_isimlik/logo/):
  kaynak.png              kırpılmış logo
  kure.json, yazi.json    çokgenler (yükseklik 1, y yukarı) ve SVG yolu
  kure.svg, yazi.svg
  onizleme.png            kaynak ve çizim yan yana
Kullanım: python3 scripts/otosentez_logo.py <ekran_görüntüsü>
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paloma_logo as PL  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "otosentez_isimlik", "logo")
UP = PL.UP
KURE_BOX = (320, 215, 775, 640)          # ekran görüntüsünde kürenin çevresi (köşedeki gri düğmeler dışarıda)
YAZI_BOX = (40, 655, 1045, 818)          # OTO SENTEZ


def mask(crop, kind):
    """Sabit eşik (zemin beyaz, ~0–8 koyuluk): küre koyuluğu ≥ 16 (açık gri uçlar ~30), yazı koyuluğu ≥ 90
    (lacivert ~160–200)."""
    a = np.asarray(crop.convert("RGB"), float)
    if kind == "kure":
        g = 255 - a.max(axis=2)
        esik = 16
    else:
        g = 255 - a.mean(axis=2)
        esik = 90
    big = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).resize((crop.width * UP, crop.height * UP),
                                                                     Image.BICUBIC)
    big = big.filter(ImageFilter.GaussianBlur(4))
    m = np.asarray(big) > esik
    e = 3 * UP                                   # kırpma kenarı boş kalsın
    m[:e], m[-e:], m[:, :e], m[:, -e:] = False, False, False, False
    return m


def alan(p):
    return 0.5 * np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1])


def vektor(src, box, kind):
    crop = src.crop(box)
    crop.save(os.path.join(OUT, f"kaynak_{kind}.png"))
    m = mask(crop, kind)
    curves = [c for c in PL.trace(m) if len(c[1]) > 8]
    e = 4 * UP                                   # zeminin çerçevesi (kırpma kenarına değen eğri) atılır
    curves = [c for c in curves if c[1][:, 0].min() > e and c[1][:, 1].min() > e
              and c[1][:, 0].max() < m.shape[1] - e and c[1][:, 1].max() < m.shape[0] - e
              and abs(alan(c[1])) > 150 * UP * UP]                  # JPEG kırıntıları (< 150 piksel) atılır
    pts = np.vstack([p for _, p in curves])
    x0, y0, x1, y1 = pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max()
    h = y1 - y0
    rings = [[[float((x - x0) / h), float((y1 - y) / h)] for x, y in p] for _, p in curves]
    k = 1000.0 / h
    d = "".join(PL.path_data(segs, lambda p: ((p[0] - x0) * k, (p[1] - y0) * k)) for segs, _ in curves)
    w = (x1 - x0) / h
    json.dump({"halkalar": rings, "en_boy": w, "d": d}, open(os.path.join(OUT, f"{kind}.json"), "w", encoding="utf-8"))
    with open(os.path.join(OUT, f"{kind}.svg"), "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w * 1000:.0f} 1000" fill="currentColor" '
                f'fill-rule="evenodd"><path d="{d}"/></svg>\n')
    # önizleme
    H = 360
    s = H / crop.height
    left = crop.resize((int(crop.width * s), H), Image.LANCZOS)
    mm = Image.new("1", (left.width * 2, H * 2), 0)
    acc = np.zeros((H * 2, left.width * 2), bool)
    for _, p in curves:
        im = Image.new("1", mm.size, 0)
        ImageDraw.Draw(im).polygon([(x / UP * s * 2, y / UP * s * 2) for x, y in p], fill=1)
        acc ^= np.asarray(im)
    right = Image.new("RGB", left.size, (40, 40, 43))
    right.paste((142, 144, 137) if kind == "kure" else (246, 246, 242), (0, 0),
                Image.fromarray((acc * 255).astype(np.uint8)).resize(left.size, Image.LANCZOS))
    print(f"{kind}: {len(curves)} eğri, en/boy {w:.3f}")
    return left, right


def main():
    src = Image.open(sys.argv[1]).convert("RGB")
    os.makedirs(OUT, exist_ok=True)
    rows = [vektor(src, KURE_BOX, "kure"), vektor(src, YAZI_BOX, "yazi")]
    W = max(l.width * 2 + 30 for l, _ in rows)
    sheet = Image.new("RGB", (W, sum(l.height + 20 for l, _ in rows)), (236, 239, 244))
    y = 10
    for l, r in rows:
        sheet.paste(l, (10, y))
        sheet.paste(r, (l.width + 20, y))
        y += l.height + 20
    sheet.save(os.path.join(OUT, "onizleme.png"))


def polygons(kind):
    """Çokgenler (yükseklik 1, y yukarı)."""
    return json.load(open(os.path.join(OUT, f"{kind}.json"), encoding="utf-8"))["halkalar"]


if __name__ == "__main__":
    main()
