"""PALOMA isimliği: yazılar dilimleyici çıktısında gerçekten basılıyor mu? (paloma_isimlik_baski.py çağırır)

Baskı dosyası PrusaSlicer'da Bambu standart ayarlarıyla dilimlenir (scripts/dilim.py). Renkli katmanlarda G-code'daki
ekstrüzyon çizgileri gerçek genişlikleriyle resme dökülür ve tasarımın renk alanlarıyla karşılaştırılır:
  * kaplama : her öğenin (ad, soyad, görev, logo, GRIDA, KARTVİZİT, QR) alanının yüzde kaçı kendi renginde basılıyor;
              her harf ve nokta ayrı ayrı da ölçülür (en kötüsü yazılır).
  * kayıp   : basılmayan en büyük parça (mm²); ince çizginin ya da noktanın düşmesi burada görünür. Kabartmanın alt
              katmanında yalnız kenar şeridi sayılır (içi üstteki katmanlarla örtülür, görünmez).
  * aralar  : harf içleri ve aralar. Düz sürümde çevre renkle (ör. KARTVİZİT harflerinin arası mavi) dolu mu;
              kabartmada boş mu (harfin kendi renginde çizgi araya taşıyorsa harfler kaynaşır).
Katmanlar: görünen katmanlar. Düz sürümde yüzey (z = T); kabartmada kabartmanın ilk ve son katmanı (yanı ve üstü),
kart ve QR için yüzey. (Dolgunun alt katmanlarında renk sınırı dilimleyicide biraz kayabilir; görünmez.)
Yakın görünümler: baski/dilim_kontrol*.png (solda tasarım, sağda dilimleyicinin çizgileri; aralar gri).
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

import anahtarlik as A
import dilim
import paloma_isimlik as P
import uzar_isimlik as I
import uzar_isimlik_baski as B

PPM = 20.0                                # ölçüm ızgarası: 0,05 mm
LIMITS = {"kaplama": 0.90, "harf": 0.85, "kayip": 0.20, "ara": 0.85, "tasma": 0.03}
EDGE = 0.45                               # mm: kabartmanın yan katmanlarında görünen kenar şeridi (dış duvar)
SPECK = 0.05                              # mm²: bundan küçük parçalar ızgara kırıntısı (çapraz değen QR kareleri)
TEXTS = ("ad", "soyad", "görev", "logo", "çizgi", "GRIDA", "KARTVİZİT")
BG = (118, 122, 130)                      # yol görünümünde boşluk rengi


def regions(plate):
    """Tasarımın renk alanları (tasarım koordinatı): {renk: alan} ve öğeler {ad: (alan, renk, çevre renk)}."""
    d = plate.design
    out = I.outline().offset(-1.0, P.J)
    col = {}
    for cs, c in d.inlay:
        col[c] = col.get(c, A.empty()) + (cs ^ out)
    col[d.sc["body"]] = I.outline() - A.union(*col.values())
    card = max(col[A.BLUE].decompose(), key=lambda p: p.area()).hull()      # mavi kartın dış çizgisi
    elems = {}
    for k in TEXTS:
        cs = d.lines[k]
        c = next(c for c, area in col.items() if (cs ^ area).area() > 0.5 * cs.area())
        around = A.BLUE if (cs ^ card).area() > 0.5 * cs.area() and c != A.BLUE else d.sc["body"]
        elems[k] = (cs, c, around)
    elems["QR"] = (d.lines["QR"] ^ col[A.BLACK], A.BLACK, d.sc["body"])
    return col, elems


def measure(plate, gcode, tools):
    """Döner: [(öğe, katman z, kenar mi, kaplama, en kötü harf, kayıp mm², ara dolu, taşma, tamam)], tamam mı,
    katmanların çizgileri."""
    dx, dy = plate.offset
    x0, y0 = -I.PW / 2 + dx - 2, dy - 2
    grid = dilim.Grid((x0, y0, x0 + I.PW + 4, y0 + I.PH + 4), PPM)
    col, elems = regions(plate)
    T, H = B.T, 0.2
    if plate.relief:
        raised = [round(T + H, 2), round(T + plate.relief_h, 2)]
        zs = {k: (raised if k in TEXTS else [round(T, 2)]) for k in elems}
    else:
        zs = {k: [round(T, 2)] for k in elems}
    segs = dilim.layers(gcode, {z for v in zs.values() for z in v})
    px_cache = {}

    def printed(z, c):
        if (z, c) not in px_cache:
            px_cache[(z, c)] = grid.paths(segs[z], tools[c])
        return px_cache[(z, c)]

    one = np.ones((3, 3), bool)
    r1, r8, re_ = int(round(0.1 * PPM)), int(round(0.8 * PPM)), int(round(EDGE * PPM))
    rows, ok = [], True
    for k, (cs, c, around) in elems.items():
        M = grid.fill(cs, dx, dy)
        near = ndimage.binary_dilation(M, iterations=r8) & ~ndimage.binary_dilation(M, iterations=r1)
        if k == "QR":
            near &= grid.fill(plate.design.lines["QR"], dx, dy)       # QR: yalnız karonun içi
        for z in zs[k]:
            X = printed(z, c)
            side = z < max(zs[k]) and len(zs[k]) > 1                   # kabartmanın alt katmanı: yalnız kenar
            S = M & ~ndimage.binary_erosion(M, iterations=re_) if side else M
            cov = (S & X).sum() / S.sum()
            lab, n = ndimage.label(M)
            area = ndimage.sum(M, lab, range(1, n + 1))
            big = area >= SPECK * PPM ** 2
            per = (ndimage.sum(X & S, lab, range(1, n + 1)) / np.maximum(ndimage.sum(S, lab, range(1, n + 1)), 1))[big]
            n = int(big.sum())
            lost = ndimage.binary_opening(S & ~X, one)
            ll, nl = ndimage.label(lost)
            worst_lost = (ndimage.sum(lost, ll, range(1, nl + 1)).max() / PPM ** 2) if nl else 0.0
            spill = (near & X).sum() / max(near.sum(), 1)
            if plate.relief and k in TEXTS:
                gap = None                                           # kabartmada ara boş kalmalı: taşma ölçülür
            else:
                gap = (near & printed(z, around)).sum() / max(near.sum(), 1)
            good = (cov >= LIMITS["kaplama"] and per.min() >= LIMITS["harf"] and worst_lost <= LIMITS["kayip"]
                    and (gap is None or gap >= LIMITS["ara"]) and spill <= LIMITS["tasma"])
            ok &= bool(good)
            rows.append((k, z, side, cov, per.min(), n, worst_lost, gap, spill, good))
    return rows, ok, segs


def report(rows):
    out = []
    for k, z, side, cov, worst, n, lost, gap, spill, good in rows:
        g = f"ara {'boş' if gap is None else f'dolu %{100 * gap:.0f}'}"
        out.append(f"  {k:10s} z {z:4.1f} {'kenar' if side else 'yüzey'}  kaplama %{100 * cov:5.1f}  en kötü parça %{100 * worst:5.1f} ({n} parça)  "
                   f"kayıp en çok {lost:.2f} mm²  {g}  taşma %{100 * spill:.1f}  -> {'TAMAM' if good else 'SORUN'}")
    return out


def views(plate, segs, tools, path, rows, ok):
    """Yakın görünümler: tasarım | dilimleyici. Kabartmada yüzey katmanı soluk, kabartmanın üst katmanı üstte."""
    d = plate.design
    dx, dy = plate.offset
    col, elems = regions(plate)
    cx = (d.lines["QR"].bounds()[0] + d.lines["QR"].bounds()[2]) / 2
    ad, gv, gr, kv, qr = (d.lines[k].bounds() for k in ("ad", "görev", "GRIDA", "KARTVİZİT", "QR"))
    crops = [("Ad: SÜ", (ad[0] - 1, ad[1] - 1.5, ad[0] + 25, ad[3] + 1.5)),
             ("Görev: Satın Alma", (gv[0] - 1, gv[1] - 1.5, gv[0] + 32, gv[3] + 1.5)),
             ("Logo, çizgi, GRIDA", (cx - 25, gr[1] - 1.5, cx + 25, d.lines["logo"].bounds()[3] + 1.5)),
             ("KARTVİZİT", (kv[0] - 1.5, kv[1] - 1.5, kv[2] + 1.5, kv[3] + 1.5)),
             ("QR köşesi", (qr[0], qr[3] - 11, qr[0] + 16, qr[3]))]
    T = B.T
    top = round(T + plate.relief_h, 2)
    rgb = {c: B.SHOW[c] for c in tools}
    scale = 24.0
    tiles = []
    for label, (a, b, c_, e) in crops:
        g = dilim.Grid((a + dx, b + dy, c_ + dx, e + dy), scale)
        des = np.zeros((g.H, g.W, 3), np.uint8)
        for c, area in col.items():
            des[g.fill(area, dx, dy)] = rgb[c]
        if plate.relief:
            for k in TEXTS:
                cs, c, _ = elems[k]
                m = g.fill(cs, dx, dy)
                edge = m & ~ndimage.binary_erosion(m, iterations=2)
                des[m] = rgb[c]
                des[edge] = (np.array(rgb[c]) * 0.55).astype(np.uint8)
        im = Image.new("RGB", (g.W, g.H), BG)
        layers_ = [(round(T, 2), 1.0 if not plate.relief else 0.8)] + ([(top, 1.0)] if plate.relief else [])
        for z, k in layers_:
            dr = ImageDraw.Draw(im)
            for t, w, xa, ya, xb, yb in segs.get(z, []):
                cc = next((c for c, tt in tools.items() if tt == t), None)
                if cc is None:
                    continue
                fill = tuple(int(v * k + BG[i] * (1 - k)) for i, v in enumerate(rgb[cc]))
                pa, pb = g.px(xa, ya), g.px(xb, yb)
                r = w * scale / 2
                dr.line([pa, pb], fill=fill, width=max(1, int(round(2 * r))))
                for qx, qy in (pa, pb):
                    dr.ellipse((qx - r, qy - r, qx + r, qy + r), fill=fill)
        tiles.append((label, Image.fromarray(des), im))
    W = 1500
    f = ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), 30)
    fs = ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), 19)
    fm = ImageFont.truetype(os.path.join(A.FONT_DIR, "Figtree_400Regular.ttf"), 17)
    colw = (W - 90) // 2
    blocks = []
    for label, des, im in tiles:
        k = min(colw / des.width, 300 / des.height)
        size = (int(des.width * k), int(des.height * k))
        blocks.append((label, des.resize(size, Image.LANCZOS), im.resize(size, Image.LANCZOS)))
    lines = report(rows)
    Hh = 176 + sum(b[1].height + 56 for b in blocks) + 26 * len(lines) + 40
    canvas = Image.new("RGB", (W, Hh), (236, 239, 244))
    dr = ImageDraw.Draw(canvas)
    kind = "KABARTMALI" if plate.relief else "DÜZ (yüzeyle aynı hizada)"
    dr.text((30, 22), f"PALOMA isimlik – {kind}: dilimleyici kontrolü", fill=(24, 26, 30), font=f)
    dr.text((30, 66), "PrusaSlicer (Bambu standart 0,20 mm eşdeğeri, Arachne). Solda tasarım, sağda G-code'daki çizgiler "
            "gerçek genişlikleriyle; gri: boşluk.", fill=(70, 74, 84), font=fs)
    zt = lambda z: f"{z:.1f}".replace(".", ",")  # noqa: E731
    dr.text((30, 92), f"Kabartmanın üst katmanı (z = {zt(top)} mm) parlak, yüzey katmanı (z = {zt(T)} mm: kart, QR) "
            "biraz soluk." if plate.relief else f"Görünen yüzey katmanı (z = {zt(T)} mm).", fill=(70, 74, 84), font=fs)
    dr.text((30, 122), f"Sonuç: {'bütün yazılar basılıyor, kayıp ya da kaynaşma yok' if ok else 'SORUN VAR (aşağıda)'}",
            fill=(22, 120, 60) if ok else (190, 30, 30), font=fs)
    y = 166
    for label, des, im in blocks:
        dr.text((30, y), label, fill=(24, 26, 30), font=fs)
        canvas.paste(des, (30, y + 30))
        canvas.paste(im, (60 + colw, y + 30))
        y += des.height + 56
    for line in lines:
        dr.text((30, y), line.strip(), fill=(22, 120, 60) if line.endswith("TAMAM") else (190, 30, 30), font=fm)
        y += 26
    canvas.save(path)
    return path


def check(plate, gcode, tools, path):
    rows, ok, segs = measure(plate, gcode, tools)
    views(plate, segs, tools, path, rows, ok)
    return rows, ok
