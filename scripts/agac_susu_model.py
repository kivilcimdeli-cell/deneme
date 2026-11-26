"""Ağaç süsleri (7'li set): X2D 3MF dosyalarını okur ve asma deliğini bulur.

Kullanıcı: dikey basılan anahtarlıklar (ayakta figür) tablada devrildi; yerine düz basılan, eklemli ağaç süsleri
satılacak (7'li set). Kaynak: boyde_labs/agac_susu/3mf/<anahtar>.3mf (kullanıcının X2D tam tabla dosyaları; tek adedin
parçaları 3D/Objects/object_1.model'de, renkler proje ayarlarında).

Baskı koordinatı: figür tablada yatık, yüzü +z, başı +y; asma deliği tepede, ekseni z (yüzden arkaya).
"""
import json
import os
import re
import zipfile

import manifold3d as m3
import numpy as np

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(KOK, "boyde_labs", "agac_susu", "3mf")
KEYS = ["noel_baba", "kardan_adam", "cam_agaci", "ren_geyigi", "atkili_ayicik", "kutup_ayisi", "zencefilli_kurabiye"]
AD = {"noel_baba": "Noel Baba", "kardan_adam": "Kardan adam", "cam_agaci": "Çam ağacı", "ren_geyigi": "Ren geyiği",
      "atkili_ayicik": "Atkılı ayıcık", "kutup_ayisi": "Kutup ayısı", "zencefilli_kurabiye": "Zencefilli kurabiye"}

_V = re.compile(rb'<vertex x="([-\d.e]+)" y="([-\d.e]+)" z="([-\d.e]+)"')
_T = re.compile(rb'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"')


def var():
    return [k for k in KEYS if os.path.exists(os.path.join(SRC, f"{k}.3mf"))]


def _hex(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def oku(key):
    """[(ad, V, F, rgb)] (mm, baskı koordinatı; tek adet)."""
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
        parts.append((n, V, F, _hex(cols[e - 1][:7])))
    return parts


def delik(parts):
    """Asma deliği: (merkez x, y; yarıçap; kalınlık z0, z1). Gövdenin (en büyük parça) 1 mm yükseklikteki kesitinde en
    üstteki boşluk."""
    n, V, F, _ = max(parts, key=lambda p: len(p[1]))
    man = m3.Manifold(m3.Mesh(vert_properties=V.astype(np.float32), tri_verts=F.astype(np.uint32)))
    cs = man.slice(1.0)
    holes = []
    for q in cs.to_polygons():
        q = np.asarray(q)
        a = 0.5 * np.sum(q[:, 0] * np.roll(q[:, 1], -1) - np.roll(q[:, 0], -1) * q[:, 1])
        if a < 0:
            holes.append((q[:, 1].mean(), q))
    if not holes:
        raise ValueError(f"{n}: delik bulunamadı")
    _, q = max(holes, key=lambda h: h[0])
    c = q.mean(0)
    r = np.sqrt(np.mean(np.sum((q - c) ** 2, 1)))
    zs = V[:, 2]
    near = np.hypot(V[:, 0] - c[0], V[:, 1] - c[1]) < r + 2.5
    return c, r, zs[near].min(), zs[near].max()


def olcu(parts):
    V = np.vstack([p[1] for p in parts])
    return V.max(0) - V.min(0)
