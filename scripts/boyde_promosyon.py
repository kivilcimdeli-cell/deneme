"""BOYDE LABS – nail art ve güzellik stüdyoları için promosyon ürünleri: 3D modeller, fotoğraflar, A4 katalog.

Kullanıcının gönderdiği örnek türler (MakerWorld'deki modeller yalnız tür örneği; geometri buradan, kendi çizimimiz):
fiyonk çanta süsü, oje şişesi kutu açacağı, fiyonk kutu açacağı, makyaj fırçası NFC anahtarlık, ruj kutusu. Her türden
dört çeşit, BOYDE tarzında: güzellik koleksiyonunun renkleri (pudra, fuşya, lila, ten rengi, krem, moka, mürdüm, rose
gold ipek), salonun baş harfi ya da adı, kalp, parıltı, inci gibi dokunuşlar. Örnek işletme adları uydurma.

Yapı (baskı yönünde, z mm; arka yüz tablada):
  fiyonk çanta süsü   gövde 3,2 mm + yumuşak kubbe (1,2), düğüm ayrı renk ve üstünde kabartma baş harf; arka yüzde
                      gömme salon adı; tepede halka kulağı
  kutu açacakları     4 mm gövde; üstteki oval delik hem anahtarlık halkası hem açacak (ucu 1,2 mm'ye incelir, kutunun
                      dilinin altına girer); kabartma yazı ve süsler 0,8 mm
  NFC fırça           5,6 mm gövde, fırça başında Ø 26 × 1,2 mm NFC cebi (baskıda duraklatılıp etiket konur); dokununca
                      salonun randevu sayfası açılır
  ruj kutusu          iç Ø 23 mm, iki parça (gövde ve sürtmeli kapak), kapakta halka kulağı

Çıktı : boyde_labs/promosyon/kaynak/<model>.npz (git'e girmez), <model>_on.png, <model>_aci.png
        boyde_labs/promosyon/fotograf/*.jpg (Blender; --foto)
        boyde_labs/promosyon/katalog.pdf, katalog.png (--katalog)
Kullanım:
  python3 scripts/boyde_promosyon.py                 # modeller ve önizlemeler
  python3 scripts/boyde_promosyon.py --foto [model]  # fotoğraflar (bpy 4.2)
  python3 scripts/boyde_promosyon.py --katalog       # A4 katalog
"""
import json
import math
import os
import sys

import manifold3d as m3
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_guzellik as G  # noqa: E402  (renkler, motifler, yazı tipleri; boyde_urunler örnek modu)

A, S, U = G.A, G.S, G.U
J = m3.JoinType.Round
OUT = os.path.join(A.ROOT, "boyde_labs", "promosyon")
SRC = os.path.join(OUT, "kaynak")
FOTO = os.path.join(OUT, "fotograf")
BEYAZ, SIYAH, SARI = A.WHITE, A.BLACK, A.YELLOW
PUDRA, GUL, FUSYA, NUDE, KREM, MOKA, MURDUM, LILA, ROSE, ADACAYI = (G.PUDRA, G.GUL, G.FUSYA, G.NUDE, G.KREM, G.MOKA,
                                                                    G.MURDUM, G.LILA, G.ROSE, G.ADACAYI)
KIRMIZI = A.RED
RGB = U.RGB
DELIK_R = 1.75                                         # anahtarlık halkası deliği Ø 3,5


# ---------------------------------------------------------------- katı yardımcıları

def birlestir(ms):
    ms = [m for m in ms if m is not None and not m.is_empty()]
    return m3.Manifold.batch_boolean(ms, m3.OpType.Add) if ms else m3.Manifold()


def kat(cs, z0, z1):
    return cs.extrude(z1 - z0).translate((0.0, 0.0, z0))


def kubbe(cs, z0, z1, r=None, n=8):
    """cs, z0'dan z1'e; üst kenarı r yarıçaplı çeyrek daireyle yuvarlanır (basamaklı: her basamak bir iki katman)."""
    r = min(r if r is not None else z1 - z0, z1 - z0)
    zb = z1 - r
    out, prev = [], zb
    if zb > z0 + 1e-6:
        out.append(kat(cs, z0, zb))
    else:
        prev = z0
    for i in range(1, n + 1):
        z = zb + r * i / n
        zm = zb + r * (i - 0.5) / n
        d = r - math.sqrt(max(r * r - (zm - zb) ** 2, 0.0))
        c = cs.offset(-d, J)
        if c.is_empty():
            break
        out.append(kat(c, prev, z))
        prev = z
    return birlestir(out)


def ortala(cs, cx, cy):
    b = cs.bounds()
    return cs.translate((cx - (b[0] + b[2]) / 2, cy - (b[1] + b[3]) / 2))


def yazi(font, s, cap, cx, cy, max_w=None, tr=0.3):
    return ortala(S.t(font, s, cap, 0.0, 0.0, "c", tr, max_w), cx, cy)


def ayna(cs):
    """Arka yüzde okunsun diye soldan sağa çevrilir (baskıda tabla yüzü)."""
    return cs.transform([[-1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])


def yansit(cs):
    return cs + cs.transform([[-1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])


def yumusak(pts, n=160):
    return A.polygon(A.smooth(pts, closed=True, n=n))


def inci(x, y, z, r):
    """Yarım küre inci (z: tabanı)."""
    return m3.Manifold.sphere(r, 48).translate((x, y, z)) ^ m3.Manifold.cube((4 * r, 4 * r, 2 * r)).translate(
        (x - 2 * r, y - 2 * r, z))


# ---------------------------------------------------------------- 1. fiyonk çanta süsü

def _fiyonk_cizgi(cift=False):
    """Fiyonk çanta süsünün parçaları (2B): ilmekler, kuyruklar, düğüm, halka kulağı, katlanma çizgileri."""
    sag = yumusak([(4.5, 4.0), (11.0, 12.0), (20.0, 16.5), (27.5, 12.5), (29.5, 3.5), (27.0, -4.5), (19.0, -7.0),
                   (11.0, -6.0), (4.5, -3.5)])
    ilmek = yansit(sag)
    ic = None
    if cift:                                           # arkada ikinci ilmek: biraz büyük, yukarı kalkık
        arka = yumusak([(4.0, 5.0), (9.0, 15.0), (16.0, 21.0), (24.0, 21.5), (28.5, 16.0), (27.0, 8.0), (16.0, 3.0)])
        ic = yansit(arka)
    kuyruk = yumusak([(1.5, -4.0), (6.5, -5.5), (11.5, -15.0), (17.5, -27.0), (15.0, -30.5), (12.0, -26.5),
                      (8.5, -31.5), (5.5, -27.5), (3.5, -14.0), (0.5, -8.0)], n=200)
    kuyruklar = yansit(kuyruk)
    dugum = A.rrect(11.0, 13.5, 3.6, 0.0, -0.8)
    kulak = A.rrect(7.4, 9.0, 3.6, 0.0, 9.0)
    delik = A.circle(DELIK_R, 0.0, 10.4, 48)
    kat_ = []
    for s in (1, -1):                                  # ilmeklerde katlanma çizgisi (düğümden dışa)
        kat_.append(A.stroke([(s * 8.0, 1.0), (s * 14.0, 3.8), (s * 20.0, 4.6), (s * 24.0, 3.2)], 1.2))
        kat_.append(A.stroke([(s * 4.5, -11.0), (s * 8.5, -19.5), (s * 10.5, -24.0)], 1.0))
    return ilmek, ic, kuyruklar, dugum, kulak, delik, A.union(*kat_)


def fiyonk_suslu(govde, dugum_renk, harf, harf_renk, arka_yazi, arka_renk, tur="klasik", ikinci=None,
                 inci_renk=None):
    """Fiyonk çanta süsü. tur: klasik, kalp (düğüm kalp), inci (kuyruklarda inciler), cift (arkada ikinci ilmek,
    `ikinci` renginde). Döner (parçalar, meta)."""
    ilmek, ic, kuyruklar, dugum, kulak, delik, kivrim = _fiyonk_cizgi(tur == "cift")
    if tur == "kalp":
        dugum = G.kalp(0.0, -0.6, 15.0)
    govde_cs = A.union(ilmek, kuyruklar, dugum.offset(0.6, J), kulak) - delik
    Z0, Z1 = 3.4, 5.0
    parts = []
    if ic is not None:                                 # arka ilmek: gövdeden aşağıda (2,4 mm) ikinci renk
        arka_cs = ic - ilmek.offset(0.0, J) - delik
        parts.append(("arka ilmek", kubbe(arka_cs, 0.0, 3.0, 1.0), ikinci))
    g = kubbe(govde_cs - kulak, 0.0, Z1, 2.2, n=10)
    g = birlestir([g, kat(kulak - delik, 0.0, 3.0)])
    g = g - kat(kivrim - dugum.offset(1.2, J), Z1 - 0.8, Z1 + 1.0)
    d = kubbe(dugum, Z0 - 0.4, 6.6, 1.6)
    g = g - kat(dugum, Z0 - 0.4, 10.0)
    if arka_yazi:
        ay = ayna(yazi("josefin", arka_yazi, 4.2, 0.0, 2.6, 46.0, 0.8)) ^ govde_cs.offset(-1.0, J)
        g = g - kat(ay, 0.0, 0.6)
        parts.append(("arka yazı", kat(ay, 0.0, 0.6), arka_renk))
    parts.insert(0, ("gövde", g, govde))
    if harf:
        h = yazi("marcellus", harf, 7.2, 0.0, -0.8 if tur != "kalp" else 0.4, 8.0, 0.0)
        hm = kat(h, 6.2, 7.2)
        d = d - kat(h, 6.2, 10.0)
        parts.append(("harf", hm, harf_renk))
    parts.insert(1, ("düğüm", d, dugum_renk))
    if tur == "inci":
        ps = []
        for s in (1, -1):
            for x, y, r in ((7.5, -12.0, 1.3), (10.5, -18.5, 1.3), (13.2, -24.5, 1.2), (24.0, 9.0, 1.1),
                            (26.5, 2.5, 1.1), (21.5, 14.0, 1.0)):
                ps.append(inci(s * x, y, Z1 - 1.6, r))
        im = birlestir(ps)
        parts[0] = (parts[0][0], parts[0][1] - im, parts[0][2])
        parts.append(("inci", im, inci_renk or BEYAZ))
    return parts, {"delik": [0.0, 10.4], "delik_r": DELIK_R, "kalinlik": 3.0}


# ---------------------------------------------------------------- açacak ucu (oje ve fiyonk kutu açacakları)

def kama(x0, x1, y0, y1, z_ic, z_uc):
    """Üst yüzden kesilen eğim: y0'da z_ic, y1'de z_uc yüksekliğe iner (y1 uç). Döner kesilecek katı."""
    cs = A.polygon([(y0, z_ic), (y1, z_uc), (y1, 30.0), (y0, 30.0)])
    m = cs.extrude(x1 - x0)
    return m.transform([[0.0, 0.0, 1.0, x0], [1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]])


def acacak_kulagi(cx, y_alt, w, h, yuva_w=9.0, yuva_h=3.2, T=4.0, uc=1.2):
    """Üstte açacak kulağı: (şekil, oval yuva, kesilecek eğim). Yuva hem halka deliği hem açacak; yuvanın üstündeki
    dil ucunda 1,2 mm'ye incelir (kutunun dilinin altına girer)."""
    kulak = A.rrect(w, h, min(w, h) * 0.32, cx, y_alt + h / 2)
    yc = y_alt + h - 2.6 - yuva_h / 2
    yuva = A.rrect(yuva_w, yuva_h, yuva_h / 2, cx, yc)
    egim = kama(cx - w, cx + w, yc - yuva_h / 2 - 0.5, y_alt + h + 0.01, T, uc)
    return kulak, yuva, egim, (cx, yc)


# ---------------------------------------------------------------- 2. oje şişesi kutu açacağı

def oje_acacak(sekil, govde, kapak, ust, yazi1, yazi1_k, yazi2, arka, arka_renk, kalp=None, parilti=True):
    """Oje şişesi biçimli kutu açacağı (4 mm). sekil: klasik (yuvarlak köşeli), damla (yuvarlak), kare (pahlı), uzun
    (ince uzun). ust: etiket/yazı rengi. Döner (parçalar, meta)."""
    T, Z = 4.0, 4.8
    if sekil == "klasik":
        sise = A.rrect(34.0, 36.0, 9.0, 0.0, 0.0)
        boyun = A.rrect(16.0, 5.0, 1.6, 0.0, 19.5)
        kap = A.rrect(14.0, 22.0, 2.6, 0.0, 32.0)
    elif sekil == "damla":
        sise = A.circle(18.5, 0.0, -1.0, 128)
        boyun = A.rrect(14.0, 5.0, 1.6, 0.0, 18.5)
        kap = A.rrect(12.0, 22.0, 5.0, 0.0, 31.0)
    elif sekil == "kare":
        sise = A.polygon([(-13.0, -18.0), (13.0, -18.0), (17.0, -14.0), (17.0, 10.0), (12.0, 17.0), (-12.0, 17.0),
                          (-17.0, 10.0), (-17.0, -14.0)]).offset(-1.5, J).offset(1.5, J)
        boyun = A.rrect(13.0, 4.0, 1.2, 0.0, 18.5)
        kap = A.polygon([(-7.0, 20.0), (7.0, 20.0), (6.0, 42.0), (-6.0, 42.0)]).offset(-1.0, J).offset(1.0, J)
    else:                                              # uzun
        sise = A.rrect(26.0, 44.0, 6.0, 0.0, -4.0)
        boyun = A.rrect(12.0, 4.0, 1.2, 0.0, 19.5)
        kap = A.rrect(10.0, 28.0, 2.0, 0.0, 35.0)
    kb = kap.bounds()
    kulak, yuva, egim, hc = acacak_kulagi(0.0, kb[3] - 3.0, max(kb[2] - kb[0], 15.0), 12.0)
    sise_cs = A.union(sise, boyun)
    kap_cs = A.union(kap, kulak) - yuva
    parts = []
    g = kubbe(sise_cs - kap_cs, 0.0, T, 1.0)
    k = kubbe(kap_cs, 0.0, T, 0.8) - egim
    oluk = []                                          # kapakta dikey oluklar
    for x in (-0.36, 0.0, 0.36):
        cx = (kb[0] + kb[2]) / 2 + x * (kb[2] - kb[0])
        oluk.append(A.rrect(1.1, kb[3] - kb[1] - 9.0, 0.55, cx, (kb[1] + kb[3]) / 2 - 3.0))
    k = k - kat(A.union(*oluk), T - 0.6, T + 1.0)
    ust_parca = []
    sb = sise.bounds()
    sx, sy = (sb[0] + sb[2]) / 2, (sb[1] + sb[3]) / 2
    if parilti:                                        # şişenin sol üstünde ışık çizgisi
        y0, y1 = sb[1] + (sb[3] - sb[1]) * 0.6, sb[1] + (sb[3] - sb[1]) * 0.86
        xl = sb[0] + (3.8 if sekil != "damla" else 6.5)
        ust_parca.append(A.stroke([(xl, y0), (xl - 0.3, (y0 + y1) / 2), (xl + 0.8, y1)], 1.6))
    if kalp:
        ust_parca.append(G.kalp(sx, sy + 1.0, kalp))
    ic = A.union(*ust_parca) if ust_parca else None
    yz = []
    if yazi1:
        k1 = yazi1_k
        if kalp:
            h = yazi(k1, yazi1, 8.0, sx, sy + 1.6, kalp * 0.62, 0.0)
            yz.append(("harf", h, govde))
        else:
            h = yazi(k1, yazi1, 8.5, sx + 1.0, sy + (2.6 if yazi2 else 0.0), sb[2] - sb[0] - 15.0, 0.4)
            yz.append(("yazı", h, ust))
    if yazi2:
        if kalp:
            h2 = yazi("baloo", yazi2, 3.8, sx, sy - 11.0, 22.0, 0.8)
        else:
            h2 = yazi("baloo", yazi2, 3.8, sx + 1.0, sy - 6.8, sb[2] - sb[0] - 13.0, 0.8)
        yz.append(("alt yazı", h2, ust))
    if ic is not None:
        im = kat(ic, T - 0.4, Z)
        g = g - im
        parts.append(("süs", im, ust if not kalp else BEYAZ))
    for ad, cs, renk in yz:
        if ad == "harf":                               # kalbin üstünde kabartma (gövde renginde)
            m = kat(cs, Z - 0.2, Z + 0.6)
            parts[-1] = (parts[-1][0], parts[-1][1] - m, parts[-1][2])
            parts.append((ad, m, renk))
            continue
        m = kat(cs, T - 0.4, Z)
        g = g - m
        parts.append((ad, m, renk))
    if arka:
        satir = arka.split("\n")
        ay = ayna(A.union(*[yazi("josefin", t, 3.8, sx, sy + 3.0 * (len(satir) - 1) - 6.0 * i,
                                 sb[2] - sb[0] - 8.0, 0.4) for i, t in enumerate(satir)]))
        g = g - kat(ay, 0.0, 0.6)
        parts.append(("arka yazı", kat(ay, 0.0, 0.6), arka_renk))
    parts = [("şişe", g, govde), ("kapak", k, kapak)] + parts
    return parts, {"delik": list(hc), "delik_r": DELIK_R, "kalinlik": T}


# ---------------------------------------------------------------- 3. fiyonk kutu açacağı

def fiyonk_acacak(dolgu, cerceve, dugum_renk, sus, harf=None, arka=None, arka_renk=None):
    """Düz fiyonk kutu açacağı (4 mm): dolgu 3,2 mm, çerçeve ve düğüm 4 mm; sus: "kalp" (düğüm kalp), "puan"
    (puantiye), "dikis" (iç kenarda kesik çizgi), "harf" (düğümde baş harf). Üstte açacak kulağı."""
    T = 4.0
    sag = yumusak([(4.0, 3.5), (12.0, 13.0), (22.0, 15.0), (28.0, 9.0), (28.5, -2.0), (24.0, -9.5), (14.0, -8.0),
                   (4.0, -3.5)])
    kuyruk = yumusak([(1.0, -4.0), (7.5, -5.5), (14.0, -15.0), (17.0, -22.0), (13.0, -21.0), (10.0, -24.5),
                      (7.5, -19.5), (3.0, -12.0), (0.0, -8.0)], n=180)
    ilmek, kuyruklar = yansit(sag), yansit(kuyruk)
    dugum = G.kalp(0.0, -1.0, 15.5) if sus == "kalp" else A.rrect(12.0, 14.0, 4.0, 0.0, -1.0)
    kulak, yuva, egim, hc = acacak_kulagi(0.0, 2.0, 15.0, 13.0)
    sekil = A.union(ilmek, kuyruklar, dugum.offset(0.8, J), kulak)
    dis = sekil - yuva
    ic = (ilmek + kuyruklar).offset(-1.8, J) - dugum.offset(1.6, J) - kulak.offset(0.6, J)
    cer = dis - ic - dugum
    parts = []
    cm = kubbe(cer, 0.0, T, 0.8) - egim
    dm = kubbe(dugum, 0.0, T + 0.4, 1.0)
    fm = kat(ic, 0.0, T - 0.8)
    if sus == "puan":
        noktalar = []
        for x in range(-28, 29, 5):
            for y in range(-24, 18, 5):
                xx = x + (2.5 if (y // 5) % 2 else 0.0)
                noktalar.append(A.circle(1.15, xx, y + 0.5, 40))
        nk = A.union(*noktalar) ^ ic.offset(-0.9, J)
        fm = fm - kat(nk, T - 1.4, T)
        parts.append(("puantiye", kat(nk, T - 1.4, T - 0.6), cerceve))
    if sus == "dikis":
        izler = []
        for parca in (ilmek, kuyruklar):
            for poly in parca.offset(-3.2, J).to_polygons():
                pts = [tuple(p) for p in poly] + [tuple(poly[0])]
                L = 0.0
                for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                    L0, d = L, math.hypot(x1 - x0, y1 - y0)
                    L += d
                    t = (math.floor(L0 / 3.2) + 1) * 3.2
                    while t < L:
                        u = (t - L0) / d
                        x, y = x0 + u * (x1 - x0), y0 + u * (y1 - y0)
                        izler.append(A.stroke([(x - 0.6 * (x1 - x0) / d, y - 0.6 * (y1 - y0) / d),
                                               (x + 0.6 * (x1 - x0) / d, y + 0.6 * (y1 - y0) / d)], 0.9))
                        t += 3.2
        iz = A.union(*izler) - dugum.offset(2.0, J)
        parts.append(("dikiş", kat(iz, T - 0.8, T - 0.2), BEYAZ))
    if harf:
        h = yazi("marcellus", harf, 7.6, 0.0, -1.0 if sus != "kalp" else 0.2, 8.5, 0.0)
        dm = dm - kat(h, T - 0.2, T + 2.0)
        parts.append(("harf", kat(h, T - 0.2, T + 0.6), BEYAZ if dugum_renk != BEYAZ else cerceve))
    if arka:                                           # arka yüzde iki ilmeğe bölünmüş ad (düğüm araya girmez)
        w = arka.split()
        k = min(range(1, len(w)), key=lambda i: abs(len(" ".join(w[:i])) - len(" ".join(w[i:])))) if len(w) > 1 else 1
        parcalar_ = []
        for kel, x in ((w[:k], -18.0), (w[k:], 18.0)):  # her ilmekte kelimeler alt alta
            for j, t in enumerate(kel):
                parcalar_.append(yazi("josefin", t, 3.8, x, 2.0 + 2.9 * (len(kel) - 1) - 5.8 * j, 16.0, 0.6))
        ay = A.union(*parcalar_)
        ay = ayna(ay) ^ ic.offset(-0.6, J)
        fm = fm - kat(ay, 0.0, 0.6)
        parts.append(("arka yazı", kat(ay, 0.0, 0.6), arka_renk))
    parts = [("dolgu", fm, dolgu), ("çerçeve", cm, cerceve), ("düğüm", dm, dugum_renk)] + parts
    return parts, {"delik": list(hc), "delik_r": 1.6, "kalinlik": T}


# ---------------------------------------------------------------- 4. makyaj fırçası NFC anahtarlık

def nfc_simge(cx, cy, s):
    """NFC dokun simgesi: üç yay."""
    yaylar = []
    for k, r in enumerate((0.28, 0.52, 0.76)):
        pts = [(cx - s * 0.3 + r * s * math.cos(math.radians(a)), cy + r * s * math.sin(math.radians(a)))
               for a in range(-48, 49, 6)]
        yaylar.append(A.stroke(pts, max(1.0, s * 0.11)))
    return A.union(*yaylar, A.circle(max(0.9, s * 0.08), cx - s * 0.3, cy, 32))


def firca_nfc(bas_turu, bas, bilezik, sap, sus_renk, sap_yazi=None, harf=None, kalp=False, uc=None):
    """Makyaj fırçası NFC anahtarlık: baş (kabuki, yelpaze, pudra, egik), bilezik, sap; baş ortasında Ø 26 NFC cebi
    (z 2,8–4,0; baskıda duraklat). Baş 5,6 mm, bilezik 5,2, sap 4,6 mm. Döner (parçalar, meta)."""
    if bas_turu == "kabuki":
        bas_cs = yumusak([(-17.0, 0.0), (-17.5, 12.0), (-12.0, 25.0), (0.0, 31.0), (12.0, 25.0), (17.5, 12.0),
                          (17.0, 0.0)], n=200)
    elif bas_turu == "yelpaze":
        pts = [(0.0, -6.0)] + [(36.0 * math.cos(math.radians(a)), -6.0 + 36.0 * math.sin(math.radians(a)))
                               for a in range(40, 141, 4)]
        bas_cs = A.polygon(pts).offset(-2.0, J).offset(2.0, J) ^ A.rect(-40.0, 0.0, 40.0, 40.0)
    elif bas_turu == "pudra":
        bas_cs = (A.circle(19.5, 0.0, 17.0, 160) + A.rrect(30.0, 10.0, 4.0, 0.0, 4.0)) ^ A.rect(-30, 0.0, 30, 40)
    else:                                              # egik: eğik kesilmiş kontür fırçası
        bas_cs = A.polygon([(-16.0, 0.0), (16.0, 0.0), (17.0, 14.0), (13.0, 30.0), (-15.0, 21.0),
                            (-17.0, 12.0)]).offset(-3.5, J).offset(3.5, J)
    bas_cs = bas_cs ^ A.rect(-40.0, 0.4, 40.0, 50.0)
    bil = A.polygon([(-13.0, 1.0), (13.0, 1.0), (8.5, -12.0), (-8.5, -12.0)]).offset(-1.0, J).offset(1.0, J)
    sap_cs = yumusak([(-7.0, -11.0), (7.0, -11.0), (6.0, -30.0), (5.4, -46.0), (0.0, -51.0), (-5.4, -46.0),
                      (-6.0, -30.0)], n=160)
    delik = A.circle(DELIK_R, 0.0, -46.0, 48)
    sap_cs = sap_cs - bil - delik
    bas_cs = bas_cs - bil
    bb = bas_cs.bounds()
    cep = A.circle(13.0, 0.0, (bb[1] + bb[3]) / 2 + 1.0, 96)
    hb = kubbe(bas_cs, 0.0, 5.6, 2.0, n=10)
    hb = hb - kat(cep, 2.8, 4.0)
    uc_m = None
    if uc:                                             # kıl uçları başka renkte (boyalı uç gibi)
        uc_cs = bas_cs - bas_cs.translate((0.0, -6.0)) - bas_cs.offset(-1.0, J).translate((0.0, -6.0))
        uc_m = hb ^ kat(uc_cs.offset(0.01, J), -1.0, 10.0)
        hb = hb - kat(uc_cs.offset(0.01, J), -1.0, 10.0)
    oluk = []                                          # kıl dokusu: başta ince oluklar
    cy0 = -8.0 if bas_turu == "yelpaze" else bb[1] - 6.0
    for a in range(-60, 61, 12):
        r0, r1 = (bb[3] - bb[1]) * 0.42, (bb[3] - bb[1]) * 1.4
        oluk.append(A.stroke([(r0 * math.sin(math.radians(a)), cy0 + r0 * math.cos(math.radians(a))),
                              (r1 * math.sin(math.radians(a)), cy0 + r1 * math.cos(math.radians(a)))], 0.9))
    ns = nfc_simge(1.5, (bb[1] + bb[3]) / 2 + (0.0 if uc else 1.0), 13.0)
    hb = hb - kat(ns, 5.0, 7.0)
    if bas_turu == "yelpaze":
        oluk_cs = (A.union(*oluk) ^ bas_cs.offset(-1.2, J)) - ns.offset(2.2, J)
        hb = hb - kat(oluk_cs, 4.9, 7.0)
        if uc_m is not None:
            uc_m = uc_m - kat(oluk_cs, 4.9, 7.0)
    parts = [("baş", hb, bas)]
    if uc_m is not None:
        parts.append(("uç", uc_m, uc))
    parts.append(("NFC simgesi", kat(ns, 5.0, 6.2), sus_renk))
    bm = kubbe(bil, 0.0, 5.2, 1.2)
    for y in (-3.0, -7.0):                              # bilezikte iki çizgi
        bm = bm - kat(A.rect(-14.0, y - 0.45, 14.0, y + 0.45), 4.7, 6.0)
    parts.append(("bilezik", bm, bilezik))
    sm = kubbe(sap_cs, 0.0, 4.6, 1.6)
    if kalp:
        kc = G.kalp(0.0, -40.0, 7.0)
        sm = sm - kat(kc, 4.0, 6.0)
        parts.append(("kalp", kat(kc, 4.0, 5.2), sus_renk))
    if sap_yazi:
        t = S.t("baloo", sap_yazi, 4.4, 0.0, 0.0, "c", 0.6, 25.0).rotate(90.0)
        t = ortala(t, 0.0, -26.0 if kalp else -29.0)
        sm = sm - kat(t, 4.0, 6.0)
        parts.append(("sap yazısı", kat(t, 4.0, 5.2), sus_renk))
    if harf:
        h = yazi("marcellus", harf, 6.0, 0.0, -38.5, 8.0, 0.0)
        sm = sm - kat(h, 4.0, 6.0)
        parts.append(("harf", kat(h, 4.0, 5.2), sus_renk))
    parts.insert(2, ("sap", sm, sap))
    return parts, {"delik": [0.0, -46.0], "delik_r": DELIK_R, "kalinlik": 4.6}


# ---------------------------------------------------------------- 5. ruj kutusu

def _cokgen(r, n, z0, z1, faz=0.0):
    pts = [(r * math.cos(math.radians(faz + 360.0 * k / n)), r * math.sin(math.radians(faz + 360.0 * k / n)))
           for k in range(n)]
    return kat(A.polygon(pts), z0, z1)


def _silindir(r, z0, z1, n=96):
    return m3.Manifold.cylinder(z1 - z0, r, r, n).translate((0.0, 0.0, z0))


def ruj_kutusu(bicim, govde, kapak, yazi_renk=None, yazi_=None, pencere=False, oluk=False, fiyonk_renk=None,
               ici=False):
    """Ruj kutusu (kapalı hâli, ekseni dik): gövde (iç Ø 22,6, dip 2 mm, boyun 14 mm, dış Ø 25), kapak (sürtmeli,
    iç Ø 25,2; tepesinde halka kulağı). bicim: silindir (Ø 28) ya da altigen (köşeden köşeye 31). Döner (parçalar,
    meta). Parçalar masada yatık (ekseni x, ön yüzü yukarı): fotoğraf ve önizleme için; baskıda dik basılır. ici: içinde
    ruj (kalp penceresinden görünsün)."""
    R_ic, R_boyun, R_dis = 11.3, 12.5, 14.0
    H, H_boyun, H_kap = 66.0, 14.0, 30.0
    if bicim == "altigen":
        dis_g = _cokgen(15.6, 6, 0.0, H - H_boyun, 0.0)
        dis_k = _cokgen(15.6, 6, H - H_boyun + 0.4, H - H_boyun + 0.4 + H_kap, 0.0)
    else:
        dis_g = _silindir(R_dis, 0.0, H - H_boyun)
        dis_k = _silindir(R_dis, H - H_boyun + 0.4, H - H_boyun + 0.4 + H_kap)
    g = birlestir([dis_g, _silindir(R_boyun, 0.0, H)]) - _silindir(R_ic, 2.0, H + 1.0)
    k0 = H - H_boyun + 0.4
    k = dis_k - _silindir(R_boyun + 0.1, k0 - 1.0, k0 + H_kap - 2.0)
    kulak = A.rrect(10.0, 12.0, 4.0, 0.0, 0.0) - A.circle(2.0, 0.0, 1.5, 48)
    kul = kat(kulak, -1.5, 1.5).rotate((90.0, 0.0, 0.0)).translate((0.0, 0.0, k0 + H_kap + 3.6))
    k = birlestir([k, kul])
    parts = []
    if oluk:                                           # dikey oluklar (yazı bandı boş)
        ol = []
        for i in range(16):
            a = 360.0 * i / 16
            if abs(((a - 90.0) + 180.0) % 360.0 - 180.0) < 30.0:
                continue
            ol.append(_silindir(1.2, 6.0, H - H_boyun - 4.0, 24).translate(
                (R_dis * math.cos(math.radians(a)), R_dis * math.sin(math.radians(a)), 0.0)))
        g = g - birlestir(ol)
    if pencere:                                        # kalp pencere (önde, +y yönünde)
        kc = G.kalp(0.0, 0.0, 16.0).rotate(-90.0)
        pm = kat(kc, -9.0, 9.0).rotate((-90.0, 0.0, 0.0)).translate((0.0, 8.0, 37.0))
        g = g - pm
    if yazi_:
        t = S.t("baloo" if bicim != "altigen" else "josefin", yazi_, 4.6, 0.0, 0.0, "c", 0.8, 40.0).rotate(-90.0)
        t = ortala(t, 0.0, 0.0)
        if bicim == "altigen":
            yuz = 15.6 * math.cos(math.radians(30.0))
            tm = kat(t, -0.6, 0.6).rotate((-90.0, 0.0, 0.0)).translate((0.0, yuz, 26.0))
        else:
            tm = kat(t, -0.6, 0.6).rotate((-90.0, 0.0, 0.0)).translate((0.0, R_dis, 26.0))
        g = g - tm
        parts.append(("yazı", tm, yazi_renk))
    if fiyonk_renk:
        f = G.fiyonk(0.0, 0.0, 16.0)
        fm = kat(f, -0.8, 1.2).rotate((-90.0, 0.0, 0.0)).translate((0.0, R_dis, k0 + H_kap * 0.5))
        k = k - kat(f, -3.0, 0.0).rotate((-90.0, 0.0, 0.0)).translate((0.0, R_dis, k0 + H_kap * 0.5))
        parts.append(("fiyonk", fm, fiyonk_renk))
    parts = [("gövde", g, govde), ("kapak", k, kapak)] + parts
    if ici:
        parts += [(ad, m.translate((0.0, 0.0, 2.2)), c) for ad, m, c in ruj()]
    alt = 13.51 if bicim == "altigen" else R_dis       # yatırınca alttaki yüz (altıgende iç teğet)
    yat = [(ad, m.transform([[0.0, 0.0, 1.0, 0.0], [1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, alt]]), c)
           for ad, m, c in parts]
    return yat, {"delik": [k0 + H_kap + 5.1, 0.0], "delik_r": 2.0, "kalinlik": 2 * alt, "dik_boy": k0 + H_kap + 9.6}


def ruj(boy=48.0):
    """Ruj (sahne nesnesi): altın kılıf ve kırmızı eğik uç (Ø 20, kutuya girer)."""
    kil = _silindir(10.0, 0.0, boy * 0.72)
    uc = _silindir(6.4, boy * 0.72, boy + 6.0) - kat(A.rect(-10, -10, 10, 10), 0, 30).rotate((35.0, 0.0, 0.0)).translate(
        (0.0, -3.0, boy + 2.0))
    return [("kılıf", kil, A.GOLD), ("ruj", uc, KIRMIZI)]


# ---------------------------------------------------------------- kaydetme ve önizleme

def meta_tamamla(parts, meta):
    allv = np.vstack([A.mesh_arrays(m)[0] for _, m, _ in parts])
    lo, hi = allv.min(0), allv.max(0)
    merkez = [(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2]
    meta = dict(meta, merkez=merkez, toplam=float(hi[2]), olcu=[float(hi[0] - lo[0]), float(hi[1] - lo[1]),
                                                                float(hi[2] - lo[2])])
    if "delik" in meta:
        d = np.array(meta["delik"]) - np.array(merkez)
        meta["kenar_yonu"] = [float(v) for v in d / np.linalg.norm(d)]
    return meta


def kaydet(anahtar, parts, meta):
    os.makedirs(SRC, exist_ok=True)
    meta = meta_tamamla(parts, meta)
    arr = {}
    for i, (_, man, _) in enumerate(parts):
        V, F = A.mesh_arrays(man)
        arr[f"v{i}"], arr[f"f{i}"] = V.astype(np.float32), F.astype(np.int32)
    meta["parcalar"] = [{"ad": n, "renk": list(RGB[c]), "metal": c in U.METAL, "renk_id": int(c)}
                        for n, _, c in parts]
    np.savez_compressed(os.path.join(SRC, f"{anahtar}.npz"), meta=json.dumps(meta), **arr)
    return meta


def gorunus(anahtar, parts, boy=1200):
    from cift_tarafli_isimlik import render, rotation
    mesh = [(*A.mesh_arrays(man), RGB[c]) for _, man, c in parts]
    for ad, rot in (("on", A.R_TOP), ("aci", rotation(-30, -35)), ("arka", rotation(180, 180))):
        im = render(mesh, boy, rot, margin=0.0, ambient=0.6)
        im.crop(im.getbbox()).save(os.path.join(SRC, f"{anahtar}_{ad}.png"), optimize=True)


# ---------------------------------------------------------------- ürünler

URUNLER = {
    "f1": ("fiyonk", "Saten fiyonk", lambda: fiyonk_suslu(PUDRA, ROSE, "L", BEYAZ, "LÂL NAILS", MOKA)),
    "f2": ("fiyonk", "Kalp düğümlü fiyonk", lambda: fiyonk_suslu(FUSYA, BEYAZ, "M", FUSYA, "MİNA NAIL BAR", BEYAZ,
                                                                 "kalp")),
    "f3": ("fiyonk", "İncili fiyonk", lambda: fiyonk_suslu(LILA, BEYAZ, "P", MURDUM, "PERA NAIL ART", MURDUM, "inci")),
    "f4": ("fiyonk", "Çift ilmekli fiyonk", lambda: fiyonk_suslu(BEYAZ, PUDRA, "E", BEYAZ, "ELA LASH & BROW", PUDRA,
                                                                 "cift", ROSE)),
    "o1": ("oje", "Klasik oje", lambda: oje_acacak("klasik", PUDRA, ROSE, FUSYA, "LÂL", "fraunces", "NAILS",
                                                     "@lalnails", MOKA)),
    "o2": ("oje", "Kalpli damla oje", lambda: oje_acacak("damla", FUSYA, BEYAZ, BEYAZ, "M", "marcellus", "NAIL BAR",
                                                           "@minanailbar", BEYAZ, kalp=17.0)),
    "o3": ("oje", "Kare oje", lambda: oje_acacak("kare", LILA, MURDUM, BEYAZ, "PERA", "marcellus", "NAIL ART",
                                                   "@peranailart", MURDUM)),
    "o4": ("oje", "Uzun oje", lambda: oje_acacak("uzun", NUDE, MOKA, MOKA, "Ela", "pacifico", "LASH",
                                                   "ELA\nLASH", MOKA)),
    "b1": ("acacak", "Kalp düğümlü açacak", lambda: fiyonk_acacak(PUDRA, FUSYA, BEYAZ, "kalp", "L", "LÂL NAILS",
                                                                    FUSYA)),
    "b2": ("acacak", "Puantiyeli açacak", lambda: fiyonk_acacak(BEYAZ, FUSYA, FUSYA, "puan", "M", "MİNA NAIL BAR",
                                                                  FUSYA)),
    "b3": ("acacak", "Dikişli açacak", lambda: fiyonk_acacak(LILA, MURDUM, MURDUM, "dikis", "P", "PERA NAIL ART",
                                                               MURDUM)),
    "b4": ("acacak", "Rose gold açacak", lambda: fiyonk_acacak(NUDE, ROSE, ROSE, "harf", "D", "DURU MAKEUP", MOKA)),
    "n1": ("firca", "Kabuki fırça", lambda: firca_nfc("kabuki", PUDRA, ROSE, FUSYA, BEYAZ, kalp=True,
                                                        sap_yazi="LÂL", uc=FUSYA)),
    "n2": ("firca", "Yelpaze fırça", lambda: firca_nfc("yelpaze", LILA, BEYAZ, MURDUM, BEYAZ, sap_yazi="PERA",
                                                         uc=MURDUM)),
    "n3": ("firca", "Pudra fırçası", lambda: firca_nfc("pudra", NUDE, ROSE, MOKA, KREM, sap_yazi="DURU", kalp=True,
                                                         uc=MOKA)),
    "n4": ("firca", "Eğik fırça", lambda: firca_nfc("egik", FUSYA, BEYAZ, PUDRA, BEYAZ, sap_yazi="MİNA", kalp=True,
                                                      uc=PUDRA)),
    "r1": ("ruj", "Altıgen ruj kutusu", lambda: ruj_kutusu("altigen", PUDRA, ROSE, MURDUM, "LÂL NAILS")),
    "r2": ("ruj", "Kalp pencereli ruj kutusu", lambda: ruj_kutusu("silindir", FUSYA, BEYAZ, pencere=True, ici=True)),
    "r3": ("ruj", "Oluklu ruj kutusu", lambda: ruj_kutusu("silindir", LILA, MURDUM, BEYAZ, "PERA", oluk=True)),
    "r4": ("ruj", "Fiyonklu ruj kutusu", lambda: ruj_kutusu("silindir", NUDE, MOKA, MOKA, "DURU", fiyonk_renk=PUDRA)),
}


def export(keys=None):
    for k, (tur, ad, fn) in URUNLER.items():
        if keys and k not in keys:
            continue
        parts, meta = fn()
        meta = kaydet(k, parts, meta)
        gorunus(k, parts)
        o = meta["olcu"]
        print(f"{k} {ad:24s} {o[0]:.1f} × {o[1]:.1f} × {o[2]:.1f} mm  renkler: "
              f"{', '.join(dict.fromkeys(S.NAMES[c] for _, _, c in parts))}", flush=True)


# ---------------------------------------------------------------- fotoğraf (Blender)

def bagla():
    """Anahtarlık fotoğraf betiğini (yükleme, stüdyo, halka takımı) bu klasöre çevirir."""
    import boyde_anahtarlik_toptan as T
    T.OUT, T.SRC, T.FOTO = OUT, SRC, FOTO
    T.KEYS = list(URUNLER)


def masa(dizilis, yol, samples, size, adim=8.0, kaydir=0.0, takim=(), el=42, az=-12, fill=0.94, dark=False):
    """Masada dizili ürünler: dizilis sıra sıra [(model, ters mi, açı)]; takim: boş halka takımları [(x, y, açı)]."""
    import boyde_anahtarlik_foto as AF
    sc = AF.studio(dark, samples, size)
    yuk = {a: AF.load(a) for a in {a for sira in dizilis for a, _, _ in sira}}
    siralar = []
    for sira in dizilis:
        ogeler = []
        for a, ters, aci in sira:
            meta, parts = yuk[a]
            M = AF.flat(meta, aci, 0, 0, ters)
            q = AF.world(parts, M)
            ogeler.append((a, M, q[:, :2].min(0), q[:, :2].max(0)))
        siralar.append(ogeler)
    boylar = [max(hi[1] - lo[1] for _, _, lo, hi in s_) for s_ in siralar]
    y = (sum(boylar) + adim * (len(siralar) - 1)) / 2
    pts = []
    for s_, h in zip(siralar, boylar):
        x = -(sum(hi[0] - lo[0] for _, _, lo, hi in s_) + adim * (len(s_) - 1)) / 2
        for a, M, lo, hi in s_:
            M = M.copy()
            M[0, 3] += x - lo[0]
            M[1, 3] += y - h / 2 - (lo[1] + hi[1]) / 2
            pts.append(AF.put(yuk[a][1], M, f"{a}_{len(pts)}"))
            x += hi[0] - lo[0] + adim
        y -= h + adim
    for i, (x, y, aci) in enumerate(takim):
        pts.append(AF.put_wires(AF.loose_set(x, y, aci), f"takim{i}"))
    yap = AF.F.camera

    def kamera(sc, lens=85):
        cam = yap(sc, lens)
        cam.data.shift_y = kaydir
        return cam
    AF.F.camera = kamera
    try:
        AF.shoot(sc, np.vstack(pts), az, el, fill, 6.3, os.path.join(FOTO, yol), dark, lens=70)
    finally:
        AF.F.camera = yap


def asili(anahtarlar, yol, samples, size=(1800, 1100), dark=False, yaw=(-14, 12, -10, 14)):
    """Ürünler halka takımlarıyla yan yana asılı (önden)."""
    import boyde_anahtarlik_foto as AF
    sc = AF.studio(dark, samples, size)
    yuk = [AF.load(k) for k in anahtarlar]
    sets = [AF.hang(meta, yaw[i % len(yaw)], (0, 0, 0)) for i, (meta, _) in enumerate(yuk)]
    spans = []
    for (M, wires), (_, parts) in zip(sets, yuk):
        q = np.vstack([AF.world(parts, M)] + [V for V, _ in wires])[:, 0]
        spans.append((q.min(), q.max()))
    xs, x = [], 0.0
    for lo, hi in spans:
        xs.append(x - lo)
        x += hi - lo + 12.0
    xs = np.array(xs) - (x - 12.0) / 2
    groups = []
    for k, ((M, wires), (_, parts), dx) in enumerate(zip(sets, yuk, xs)):
        M = M.copy()
        M[0, 3] += dx
        groups += [AF.put(parts, M, f"urun{k}"), AF.put_wires(wires, f"halka{k}", (dx, 0, 0))]
    pts = AF.lift_all(np.vstack(groups), 0.02)
    AF.shoot(sc, pts, 0, 6, 0.9, 8.0, os.path.join(FOTO, yol), dark, glow=dark)


TURLER = ["fiyonk", "oje", "acacak", "firca", "ruj"]


def fotograflar(args):
    """Her model: masada önlü arkalı (iki) ve halkada asılı (halka); her tür: dört çeşit masada (grup) ve asılı
    (dizi); kapak: türlerden seçme."""
    import boyde_anahtarlik_foto as AF
    samples = int(args[args.index("--ornek") + 1]) if "--ornek" in args else 32
    kucuk = "--deneme" in args
    if kucuk:
        AF.F.SIZE = (500, 500)
    os.makedirs(FOTO, exist_ok=True)
    sec = [a for a in args if not a.startswith("-") and not a.isdigit()]
    for k in URUNLER:
        if (not sec and "--tur" not in args and "--kapak" not in args) or k in sec:
            AF.model_shots(k, samples)
            print(f"{k}: iki, halka", flush=True)
    boy = (600, 600) if kucuk else (1600, 1600)
    for tur in TURLER:
        if sec and tur not in sec and "--tur" not in args:
            continue
        if not sec and "--tur" not in args and "--kapak" in args:
            continue
        ks = [k for k, v in URUNLER.items() if v[0] == tur]
        if tur == "ruj":
            masa([[(ks[0], False, -4)], [(ks[1], False, 3)], [(ks[2], False, -2)], [(ks[3], False, 4)]],
                 f"grup_{tur}.jpg", samples, boy, adim=6.0)
        else:
            masa([[(ks[0], False, -6), (ks[1], False, 5)], [(ks[2], False, 4), (ks[3], False, -5)]],
                 f"grup_{tur}.jpg", samples, boy, adim=9.0)
        asili(ks, f"dizi_{tur}.jpg", samples, (900, 550) if kucuk else (1800, 1100))
        print(f"{tur}: grup, dizi", flush=True)
    if (not sec and "--tur" not in args) or "--kapak" in args or "kapak" in sec:
        masa([[("f1", False, -8), ("n1", False, 6), ("o2", False, -4)],
              [("b2", False, 5), ("r1", False, -3), ("f3", False, 8)],
              [("o1", False, 4), ("n4", False, -6), ("b1", False, -3)]], "kapak.jpg", samples,
             (600, 600) if kucuk else (1800, 1800), adim=7.0)
        print("kapak", flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--foto" in args:
        bagla()
        fotograflar([a for a in args if a != "--foto"])
    elif "--katalog" in args:
        import boyde_promosyon_katalog as PK
        PK.main()
    else:
        export([a for a in args if not a.startswith("-")] or None)
