"""SAVAŞ KANLIADA logosundaki SK + çatı işaretini görselden vektöre çevirir (kırmızı ve gümüş/beyaz ayrı).

Kaynak: anahtarlik/savas_kanliada/kaynak_logo.png (koyu zeminde kırmızı S ve K, üstte gümüş çatı ve pencere; altında
kırmızı SAVAŞ KANLIADA ve beyaz alt satır). Yazılar anahtarlıkta yazı tipiyle yeniden yazılır; işaret görselden alınır:
kırmızı (kırmızı − en büyük öteki kanal) ve gümüş (açık, renksiz) maskeleri 8 kat büyütülüp yumuşatılır, potrace ile
Bézier eğrilerine çevrilir (scripts/paloma_logo.py).
Çıktı: anahtarlik/savas_kanliada/logo/{kirmizi,beyaz}.json (yükseklik 1, y yukarı; ikisi aynı çerçevede), onizleme.png
Kullanım: python3 scripts/savas_kanliada_logo.py
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paloma_logo as PL  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "anahtarlik", "savas_kanliada")
OUT = os.path.join(DIR, "logo")
UP = PL.UP
BOX = (120, 30, 380, 262)                   # SK + çatı (yazılar dışarıda)


def maske(a, kind):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    if kind == "kirmizi":
        v = r - np.maximum(g, b)
        esik = 70
    else:
        v = np.minimum(np.minimum(r, g), b) - 0.6 * (np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b))
        esik = 95
    big = Image.fromarray(np.clip(v * 1.6, 0, 255).astype(np.uint8)).resize((a.shape[1] * UP, a.shape[0] * UP),
                                                                           Image.BICUBIC)
    big = big.filter(ImageFilter.GaussianBlur(5))
    m = np.asarray(big) > esik * 1.6
    e = 2 * UP
    m[:e], m[-e:], m[:, :e], m[:, -e:] = False, False, False, False
    return m


def alan(p):
    return 0.5 * np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1])


def main():
    src = Image.open(os.path.join(DIR, "kaynak_logo.png")).convert("RGB")
    crop = src.crop(BOX)
    a = np.asarray(crop).astype(float)
    os.makedirs(OUT, exist_ok=True)
    curves = {}
    for kind in ("kirmizi", "beyaz"):
        m = maske(a, kind)
        e = 3 * UP                                           # kırpma kenarına değen çerçeve eğrisi atılır
        curves[kind] = [c for c in PL.trace(m) if len(c[1]) > 8 and abs(alan(c[1])) > 6 * UP * UP
                        and c[1][:, 0].min() > e and c[1][:, 1].min() > e
                        and c[1][:, 0].max() < m.shape[1] - e and c[1][:, 1].max() < m.shape[0] - e]
    pts = np.vstack([p for cs in curves.values() for _, p in cs])
    x0, y0, x1, y1 = pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max()
    h = y1 - y0
    for kind, cs in curves.items():
        rings = [[[float((x - x0) / h), float((y1 - y) / h)] for x, y in p] for _, p in cs]
        json.dump({"halkalar": rings, "en_boy": float((x1 - x0) / h)},
                  open(os.path.join(OUT, f"{kind}.json"), "w"))
        print(kind, len(cs), "eğri")
    H = 400
    s = H / crop.height
    left = crop.resize((int(crop.width * s), H), Image.LANCZOS)
    right = Image.new("RGB", left.size, (52, 55, 60))
    for kind, col in (("kirmizi", (214, 32, 42)), ("beyaz", (236, 236, 232))):
        acc = np.zeros((H * 2, left.width * 2), bool)
        for _, p in curves[kind]:
            im = Image.new("1", (left.width * 2, H * 2), 0)
            ImageDraw.Draw(im).polygon([(x / UP * s * 2, y / UP * s * 2) for x, y in p], fill=1)
            acc ^= np.asarray(im)
        right.paste(col, (0, 0), Image.fromarray((acc * 255).astype(np.uint8)).resize(left.size, Image.LANCZOS))
    sheet = Image.new("RGB", (left.width * 2 + 30, H + 20), (236, 239, 244))
    sheet.paste(left, (10, 10))
    sheet.paste(right, (left.width + 20, 10))
    sheet.save(os.path.join(OUT, "onizleme.png"))


def polygons(kind):
    return json.load(open(os.path.join(OUT, f"{kind}.json")))["halkalar"]


if __name__ == "__main__":
    main()
