"""Müşterinin logosu: görüntü (PNG / JPG) → kabartma şekil (CrossSection) ve sitenin işareti (SVG).

Tek renkli, düz zeminli logo en iyi sonucu verir. Zemin ile logo ayrılır: saydam zeminde saydamlıktan, değilse
Otsu eşiğiyle (zemin rengi kenar piksellerinden: açık zeminde koyu kısımlar logodur, koyu zeminde açık kısımlar).
Konturlar ve delikleri (cv2.RETR_CCOMP) çokgene çevrilir, sadeleştirilir. Şekil boyu 1 birim, ortası (0, 0);
isimlikte istenen boya ölçeklenir, baskıya gelmeyen incelikler (1,2 mm'den ince çizgi, 0,8 mm'den dar boşluk) kapanır
(ortak.temizle).
"""
import cv2
import manifold3d as m3
import numpy as np
from PIL import Image

PIKSEL = 900                                           # izlemeden önce uzun kenar


class LogoHatasi(ValueError):
    pass


def maske(yol):
    """Logonun piksel maskesi (True: logo), boşluklar kırpılmış, uzun kenarı PIKSEL."""
    im = Image.open(yol)
    im.load()
    m = None
    if im.mode in ("RGBA", "LA", "PA") or "transparency" in im.info:
        a = np.asarray(im.convert("RGBA"))[:, :, 3]
        if (a < 128).mean() > 0.05:
            m = a >= 128
    if m is None:
        g = np.asarray(im.convert("L"))
        kenar = np.concatenate([g[0], g[-1], g[:, 0], g[:, -1]])
        t, _ = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        m = g < t if kenar.mean() > 127 else g > t
    ys, xs = np.nonzero(m)
    if len(xs) < 50:
        raise LogoHatasi("Logoda şekil bulunamadı (zemin ile logo ayrılmadı)")
    m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = PIKSEL / max(m.shape)
    m = cv2.resize(m.astype(np.uint8) * 255, (max(1, round(m.shape[1] * k)), max(1, round(m.shape[0] * k))),
                   interpolation=cv2.INTER_AREA) > 127
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0   # kırıntılar
    return m


def konturlar(m):
    """Maskenin konturları (dış ve delikler), piksel koordinatı, sadeleştirilmiş."""
    cs, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cs:
        if cv2.contourArea(c) < 12:
            continue
        c = cv2.approxPolyDP(c, 0.8, True)
        if len(c) >= 3:
            out.append(c[:, 0, :].astype(float))
    if not out:
        raise LogoHatasi("Logonun konturu çıkarılamadı")
    return out


def izle(yol):
    """Döner (CrossSection: boyu 1, ortası 0; SVG metni)."""
    m = maske(yol)
    h, w = m.shape
    polys = konturlar(m)
    cs = m3.CrossSection([np.column_stack([p[:, 0], h - p[:, 1]]) for p in polys], m3.FillRule.EvenOdd)
    b = cs.bounds()
    k = 1.0 / (b[3] - b[1])
    cs = cs.translate((-(b[0] + b[2]) / 2, -(b[1] + b[3]) / 2)).scale((k, k))
    d = " ".join("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in p) + " Z" for p in polys)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">'
           f'<path fill-rule="evenodd" d="{d}"/></svg>\n')
    return cs, svg
