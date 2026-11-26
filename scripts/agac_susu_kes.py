"""Ağaç süslerini kullanıcının görselinden keser (3MF'leri gelmeyen figürler için).

Kaynak: boyde_labs/agac_susu/kaynak_set.webp (kullanıcının 7 figürlük çizimi, 2000 × 498; gri zeminde yatık, ışık sol
üstten, gölge sağ alta). Zemin (#AEACA8 civarı) ve gölgeler (aynı renk tonunda, daha koyu) atılır: renkli ya da
zeminden belirgin açık ya da çok koyu pikseller figür. Figürün içindeki boşluklar (eklem araları) doldurulur; tepedeki
asma deliği açık kalır. Kenar 1 piksel yumuşatılır.

Çıktı: boyde_labs/agac_susu/kesik/<anahtar>.png (RGBA) ve kesik.json (her figürün deliği: merkez, yarıçap; piksel)
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agac_susu_model as M  # noqa: E402

KAYNAK = os.path.join(M.KOK, "boyde_labs", "agac_susu", "kaynak_set.webp")
OUT = os.path.join(M.KOK, "boyde_labs", "agac_susu", "kesik")
DELIK = {"noel_baba": (87.0, 21.7, 7.0), "kardan_adam": (96.7, 20.0, 5.5), "cam_agaci": (106.7, 21.7, 6.0),
         "ren_geyigi": (110.5, 25.0, 7.5), "atkili_ayicik": (113.8, 25.0, 7.0), "kutup_ayisi": (106.8, 21.7, 6.0),
         "zencefilli_kurabiye": (125.0, 25.0, 7.0)}   # asma deliği (kesikte merkez x, y, yarıçap; gözle büyütülüp okundu)
SIRA = ["noel_baba", "kardan_adam", "cam_agaci", "ren_geyigi", "atkili_ayicik", "kutup_ayisi", "zencefilli_kurabiye"]


def maske(a):
    bg = np.median(np.r_[a[:8].reshape(-1, 3), a[-8:].reshape(-1, 3)], 0)
    l = a.mean(2)
    lb = bg.mean()
    chroma = np.abs((a - a.mean(2, keepdims=True)) - (bg - lb)).max(2)      # zeminin tonundan sapma
    m = (chroma > 16) | (l > lb + 14) | (l < lb - 62)
    m = ndi.binary_opening(m, iterations=1)
    m = ndi.binary_closing(m, iterations=2)
    return m, bg


def main():
    a = np.asarray(Image.open(KAYNAK).convert("RGB"), float)
    m, bg = maske(a)
    lab, n = ndi.label(m)
    sizes = ndi.sum(m, lab, range(1, n + 1))
    big = [i + 1 for i in np.argsort(sizes)[::-1][:7]]
    sls = ndi.find_objects(lab)
    objs = sorted(((sls[i - 1], i) for i in big), key=lambda t: t[0][1].start)
    os.makedirs(OUT, exist_ok=True)
    info = {}
    for key, (sl, i) in zip(SIRA, objs):
        fm = lab == i
        dolu = ndi.binary_fill_holes(fm)
        ys, xs = np.nonzero(dolu)
        fy0, fy1, fx0, fx1 = ys.min(), ys.max(), xs.min(), xs.max()
        lb = bg.mean()
        l = a.mean(2)
        chroma = np.abs((a - a.mean(2, keepdims=True)) - (bg - lb)).max(2)
        aday = dolu & (chroma < 14) & (l < lb + 8)              # deliğin içi: zemin ya da gölgesi (gri)
        bolge = np.zeros_like(dolu)
        cx = (fx0 + fx1) / 2
        bolge[fy0:fy0 + int(0.22 * (fy1 - fy0)), int(cx - 0.22 * (fx1 - fx0)):int(cx + 0.22 * (fx1 - fx0))] = True
        aday &= bolge
        aday = ndi.binary_opening(aday, iterations=1)
        hl, k = ndi.label(aday)
        hole, best = None, None
        for j in range(1, k + 1):
            h = hl == j
            if h.sum() < 12:
                continue
            yy, xx = np.nonzero(h)
            sk = abs(xx.mean() - cx) + 0.5 * (yy.mean() - fy0)
            if best is None or sk < best:
                best, hole = sk, (xx.mean(), yy.mean(), np.sqrt(h.sum() / np.pi), h)
        if hole is not None:
            dolu &= ~ndi.binary_dilation(hole[3], iterations=1)
            hole = hole[:3]
        y0, y1, x0, x1 = sl[0].start - 3, sl[0].stop + 3, sl[1].start - 3, sl[1].stop + 3
        hx, hy, hr = DELIK[key]                                   # delik saydam: ip içinden görünür
        yy, xx = np.mgrid[0:dolu.shape[0], 0:dolu.shape[1]]
        dolu &= np.hypot(xx - (hx + x0), yy - (hy + y0)) > hr * 0.85
        hole = (hx + x0, hy + y0, hr)
        alpha = Image.fromarray((dolu[y0:y1, x0:x1] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7))
        rgb = Image.fromarray(a[y0:y1, x0:x1].astype(np.uint8))
        rgb.putalpha(alpha)
        rgb.save(os.path.join(OUT, f"{key}.png"))
        info[key] = {"boyut": [x1 - x0, y1 - y0],
                     "delik": None if hole is None else [float(hole[0] - x0), float(hole[1] - y0), float(hole[2])]}
        print(key, info[key])
    json.dump(info, open(os.path.join(OUT, "kesik.json"), "w"), indent=1)
    # denetim: beyaz ve koyu zeminde yan yana
    W = sum(Image.open(os.path.join(OUT, f"{k}.png")).width + 10 for k in SIRA) + 10
    sheet = Image.new("RGB", (W, 2 * 300), (255, 255, 255))
    sheet.paste((40, 60, 45), (0, 300, W, 600))
    x = 10
    for k in SIRA:
        im = Image.open(os.path.join(OUT, f"{k}.png"))
        sheet.paste(im, (x, 10), im)
        sheet.paste(im, (x, 310), im)
        x += im.width + 10
    sheet.save(os.path.join(OUT, "_denetim.png"))


if __name__ == "__main__":
    main()
