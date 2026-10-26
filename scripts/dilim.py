"""Dilimleyici kontrolü: bir baskı dosyası dilimleyicide gerçekten nasıl basılacak?

Bambu Studio bu ortamda komut satırından dilimleyemediği için aynı ayarların PrusaSlicer karşılığı kullanılır
(dilim_bambu_standart.ini: 0,20 mm Standard @BBL X2D, Arachne duvarlar, 0,42 mm çizgi, ütüleme kapalı).
  * to_prusa : Bambu 3MF'teki parçalar ve tabla konumları PrusaSlicer 3MF'ine aynen aktarılır (ekstrüder = AMS yuvası).
  * slice    : PrusaSlicer ile G-code; filament (g, yuva başına) ve süre.
  * layers   : G-code'dan istenen katmanların ekstrüzyon çizgileri: (araç, genişlik, x0, y0, x1, y1).
  * paths / fill : çizgiler genişlikleriyle ve tasarım alanları (CrossSection) aynı ızgaraya resim (bool dizi) olarak.

Kullanım (örnek): scripts/paloma_isimlik_dilim.py
"""
import os
import re
import subprocess
import tempfile
import zipfile

import numpy as np
from PIL import Image, ImageDraw

INI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dilim_bambu_standart.ini")


def to_prusa(src, dst):
    """Bambu 3MF (tek nesne, parçalar) → PrusaSlicer 3MF; konumlar ağa işlenir (kimlik dönüşümü)."""
    z = zipfile.ZipFile(src)
    obj = z.read("3D/Objects/object_1.model").decode()
    cfg = z.read("Metadata/model_settings.config").decode()
    ext = [int(e) for e in re.findall(r'<part id="\d+"[^>]*>.*?key="extruder" value="(\d+)"', cfg, re.S)]
    build = z.read("3D/3dmodel.model").decode().split("<build")[1]
    items = [np.array(t.split(), float) for t in re.findall(r'transform="([^"]+)"', build)]
    meshes = []
    for body in re.findall(r'<object id="\d+"[^>]*>(.*?)</object>', obj, re.S):
        V = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', body), float)
        T = np.array(re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', body), int)
        meshes.append((V, T))
    objs, conf = [], []
    for k, m in enumerate(items):
        M, t = m[:9].reshape(3, 3), m[9:]
        verts, tris, off, tid, vols = [], [], 0, 0, []
        for (V, T), e in zip(meshes, ext):
            verts.append(V @ M + t)
            tris.append(T + off)
            off += len(V)
            vols.append((tid, tid + len(T) - 1, e))
            tid += len(T)
        Vs, Ts = np.vstack(verts), np.vstack(tris)
        objs.append(f'<object id="{k + 1}" type="model"><mesh><vertices>'
                    + "".join(f'<vertex x="{a:.5f}" y="{b:.5f}" z="{c:.5f}"/>' for a, b, c in Vs)
                    + "</vertices><triangles>"
                    + "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in Ts)
                    + "</triangles></mesh></object>")
        conf.append(f'<object id="{k + 1}" instances_count="1"><metadata type="object" key="name" value="o{k + 1}"/>'
                    + "".join(f'<volume firstid="{a}" lastid="{b}"><metadata type="volume" key="name" value="p{i}"/>'
                              f'<metadata type="volume" key="volume_type" value="ModelPart"/>'
                              f'<metadata type="volume" key="extruder" value="{e}"/></volume>'
                              for i, (a, b, e) in enumerate(vols)) + "</object>")
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources>' + "".join(objs)
             + "</resources><build>" + "".join(f'<item objectid="{k + 1}" transform="1 0 0 0 1 0 0 0 1 0 0 0" '
                                               f'printable="1"/>' for k in range(len(items))) + "</build></model>")
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as o:
        o.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.'
                   'openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/'
                   'vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/'
                   'vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        o.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.'
                   'openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" '
                   'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        o.writestr("3D/3dmodel.model", model)
        o.writestr("Metadata/Slic3r_PE_model.config", '<?xml version="1.0" encoding="utf-8"?>\n<config>'
                   + "".join(conf) + "</config>")
    return ext


def slice(bambu_3mf, gcode, ini=INI):
    """Dilimler; döner {'g': [yuva başına g], 'toplam_g', 'sure': '2 sa 27 dk'}. Kule ve renk değişimi hariç."""
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "prusa.3mf")
        to_prusa(bambu_3mf, src)
        subprocess.run(["prusa-slicer", "--export-gcode", "--dont-arrange", "--load", ini, src, "--output", gcode],
                       check=True, capture_output=True, timeout=1800)
    head = open(gcode, encoding="utf-8", errors="replace").read()
    g = [float(v) for v in re.search(r"^; filament used \[g\] = (.*)$", head, re.M).group(1).split(",")]
    total = float(re.search(r"^; total filament used \[g\] = (.*)$", head, re.M).group(1))
    t = re.search(r"^; estimated printing time \(normal mode\) = (.*)$", head, re.M).group(1)
    h = re.search(r"(\d+)h", t)
    m = re.search(r"(\d+)m", t)
    sure = (f"{h.group(1)} sa " if h else "") + f"{m.group(1) if m else 0} dk"
    return {"g": g, "toplam_g": total, "sure": sure}


def layers(gcode, zs):
    """{z: [(araç, genişlik, x0, y0, x1, y1), ...]}: istenen katmanlardaki ekstrüzyon çizgileri (göreli E)."""
    want = {round(z, 2) for z in zs}
    out = {z: [] for z in want}
    tool, w, z, x, y = 0, 0.42, 0.0, 0.0, 0.0
    num = re.compile(r"([XYZE])(-?[\d.]+)")
    with open(gcode, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith(";Z:"):
                z = round(float(line[3:]), 2)
            elif line.startswith(";WIDTH:"):
                w = float(line[7:])
            elif line[0] == "T" and line[1:2].isdigit():
                tool = int(line[1:].split()[0])
            elif line.startswith(("G1 ", "G0 ")):
                v = dict((k, float(n)) for k, n in num.findall(line.split(";")[0]))
                nx, ny = v.get("X", x), v.get("Y", y)
                if z in want and v.get("E", 0) > 0 and ("X" in v or "Y" in v):
                    out[z].append((tool, w, x, y, nx, ny))
                x, y = nx, ny
    return out


class Grid:
    """Tabla koordinatında (mm) bir dikdörtgen; ppm piksel / mm. Resimde y yukarı (tabla gibi)."""

    def __init__(self, box, ppm=20.0):
        self.x0, self.y0, self.x1, self.y1 = box
        self.ppm = ppm
        self.W = int(round((self.x1 - self.x0) * ppm))
        self.H = int(round((self.y1 - self.y0) * ppm))

    def px(self, x, y):
        return (x - self.x0) * self.ppm, (self.y1 - y) * self.ppm

    def paths(self, segs, tool=None):
        """Çizgiler gerçek genişlikleriyle (yuvarlak uçlu) dolu alan olarak."""
        im = Image.new("1", (self.W, self.H), 0)
        dr = ImageDraw.Draw(im)
        for t, w, xa, ya, xb, yb in segs:
            if tool is not None and t != tool:
                continue
            a, b = self.px(xa, ya), self.px(xb, yb)
            r = w * self.ppm / 2
            dr.line([a, b], fill=1, width=max(1, int(round(2 * r))))
            for cx, cy in (a, b):
                dr.ellipse((cx - r, cy - r, cx + r, cy + r), fill=1)
        return np.array(im)

    def fill(self, cs, dx=0.0, dy=0.0):
        """CrossSection alanı (çift-tek kuralı), tasarım koordinatı + (dx, dy) = tabla koordinatı."""
        acc = np.zeros((self.H, self.W), bool)
        for p in cs.to_polygons():
            im = Image.new("1", (self.W, self.H), 0)
            ImageDraw.Draw(im).polygon([self.px(u + dx, v + dy) for u, v in p], fill=1)
            acc ^= np.array(im)
        return acc
