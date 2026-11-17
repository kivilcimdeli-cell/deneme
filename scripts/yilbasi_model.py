"""Yılbaşı anahtarlıkları (seçilen 6 figür): X2D 3MF dosyalarını okur, tepedeki halkayı bulur ve kafa rengine boyar.

Kaynak: boyde_labs/yilbasi_anahtarlik/3mf/<anahtar>.3mf (seçilen 6 figür, X2D tam tabla). Figürler ayakta (z yukarı),
ön yüz -y; tepede asma halkası (delik ekseni y, yani önden arkaya).

Kullanıcı: "halka kısımlarını altın yapma, hepsinin kafa rengiyle aynı yap". 3MF'lerde halka altın parçanın içinde;
burada halka bölgesindeki yüzler (deliğin çevresinde, xz düzleminde halka yarıçapı içinde) altından ayrılıp HALKA
rengine boyanır. Ren geyiğinde boynuzlar altın kalır. Çam ağacının halkası yıldızla uyumlu altın kalır (kullanıcı).
"""
import json
import os
import re
import zipfile

import numpy as np

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(KOK, "boyde_labs", "yilbasi_anahtarlik", "3mf")
KEYS = ["noel_baba", "ren_geyigi", "atkili_ayicik", "kutup_ayisi", "kardan_adam", "cam_agaci"]
AD = {"noel_baba": "Noel Baba", "ren_geyigi": "Ren geyiği", "atkili_ayicik": "Atkılı ayıcık",
      "cam_agaci": "Çam ağacı", "kardan_adam": "Kardan adam", "kutup_ayisi": "Kutup ayısı"}
HALKA = {"noel_baba": "red", "ren_geyigi": "brown", "atkili_ayicik": "brown", "kutup_ayisi": "white",
         "kardan_adam": "red", "cam_agaci": None}     # halka: kafanın (şapka, bere, kafa) rengi; çamda yıldızla altın
RENK_TR = {"red": "kırmızı", "brown": "kahverengi", "green": "yeşil", "gold": "altın", "white": "beyaz",
           "black": "siyah", "bej": "bej"}

_V = re.compile(rb'<vertex x="([-\d.e]+)" y="([-\d.e]+)" z="([-\d.e]+)"')
_T = re.compile(rb'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"')


def _hex(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def oku(key):
    """[(ad, V, F, rgb, renk_adı)] (mm, baskı koordinatı; tek adet)."""
    with zipfile.ZipFile(os.path.join(SRC, f"{key}.3mf")) as z:
        cfg = json.loads(z.read("Metadata/project_settings.config"))
        ms = z.read("Metadata/model_settings.config").decode()
        obj = z.read("3D/Objects/object_1.model")
    cols = cfg["filament_colour"]
    ext = {int(i): (n, int(e)) for i, n, e in
           re.findall(r'<part id="(\d+)".*?name" value="([^"]+)".*?extruder" value="(\d+)"', ms, re.S)}
    parts = []
    for blok in obj.split(b"<object ")[1:]:
        oid = int(re.match(rb'id="(\d+)"', blok).group(1))
        V = np.array(_V.findall(blok), float)
        F = np.array(_T.findall(blok), np.int64)
        n, e = ext[oid]
        parts.append((n, V, F, _hex(cols[e - 1]), n.split(" - ")[0].rstrip("0123456789")))
    return parts


def delik(parts):
    """Halkanın deliği: (merkez xyz, iç yarıçap, dış yarıçap). Altın parçanın tepesinde, x≈0 çizgisindeki en büyük
    boşluk delik; en üst nokta halkanın dışı."""
    zmax = max(V[:, 2].max() for _, V, _, _, _ in parts)
    V = np.vstack([V for _, V, _, _, r in parts if r == "gold"])
    ust = V[V[:, 2] > zmax - 12]
    zs = np.sort(ust[np.abs(ust[:, 0]) < 0.6, 2])
    j = np.argmax(np.diff(zs))
    z0, z1 = zs[j], zs[j + 1]
    halka = ust[(np.abs(ust[:, 0]) < 7) & (ust[:, 2] > z0 - 3)]
    yc = (halka[:, 1].min() + halka[:, 1].max()) / 2
    zc = (z0 + z1) / 2
    return np.array([0.0, yc, zc]), (z1 - z0) / 2, zmax - zc


def boya(parts, key):
    """Halkayı altından ayırıp kafa rengine boyar: altın yüzlerden ağırlık merkezi halka bölgesinde olanlar
    (xz'de deliğin merkezine uzaklığı dış yarıçap + 0,25 içinde ve deliğin alt kenarından yukarıda ya da halkanın
    yan kollarında)."""
    if HALKA[key] is None:
        return parts
    c, r_ic, r_dis = delik(parts)
    hedef = next((rgb, r) for _, _, _, rgb, r in parts if r == HALKA[key])
    out = []
    for n, V, F, rgb, r in parts:
        if r != "gold":
            out.append((n, V, F, rgb, r))
            continue
        g = V[F].mean(1)
        d = np.hypot(g[:, 0] - c[0], g[:, 2] - c[2])
        sec = (d < r_dis + 0.25) & (g[:, 2] > c[2] - r_dis * 0.8)
        if sec.any():
            out.append((n + " halka", V, F[sec], hedef[0], hedef[1]))
        if (~sec).any():
            out.append((n, V, F[~sec], rgb, r))
    return out


def figur(key, halka_boya=True):
    p = oku(key)
    return boya(p, key) if halka_boya else p


def olcu(parts):
    V = np.vstack([V for _, V, _, _, _ in parts])
    return V.max(0) - V.min(0)


def hacim(parts):
    """cm³ (kapalı kabukların toplamı; boyanmamış parçalarla)."""
    t = 0.0
    for _, V, F, _, _ in parts:
        a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
        t += np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0
    return abs(t) / 1000.0
