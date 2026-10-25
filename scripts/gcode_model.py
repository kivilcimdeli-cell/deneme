"""Dilimlenmiş Bambu dosyasından (.gcode.3mf) modeli geri çıkarır.

.gcode.3mf içinde 3B model yoktur, yalnız G-code vardır; Bambu Studio'da filament ya da ayar değişince dilim silinir ve
plaka boş kalır. Bu betik G-code'daki her nesnenin her katmanını okur:
  * tüm çizgiler (duvar, dolgu, köprü…) yarım genişlikle kalınlaştırılıp birleştirilir: modelin gerçek kenarı
  * içteki boşluklardan yalnız dış duvarla çevrili olanlar delik kalır; dolgu araları doldurulur
  * ilk katmanda fil ayağı telafisi geri alınır
Katmanlar üst üste dizilip birleştirilir (aynı olan ardışık katmanlar tek parça). Sonuç: aynı katman yüksekliğiyle
yeniden dilimlenince özgün baskıyla aynı geometriyi veren 3MF (yalnız geometri; yazıcı ve filament Bambu Studio'da
seçilir).

Kullanım:
  python3 scripts/gcode_model.py <girdi.gcode.3mf> <çıktı.3mf>
"""
import math
import re
import sys
import zipfile

import manifold3d as m3
import numpy as np
from shapely.geometry import LineString, MultiPolygon, Polygon
from shapely.ops import unary_union

SKIP = {"Brim", "Custom", "Skirt", "Prime tower", "Wipe tower", "Support", "Support interface", "Support transition"}


def parse(gcode):
    """{nesne: {z: [(özellik, genişlik, [(x, y), ...]), ...]}}, katman kalınlıkları, nesne adları"""
    objs, heights = {}, {}
    obj = feat = None
    width, z, lh = 0.42, 0.0, 0.2
    x = y = 0.0
    rel_e, absolute = True, True
    path, path_key = [], None

    def flush():
        nonlocal path, path_key
        if obj is not None and path_key and len(path) > 1:
            objs.setdefault(obj, {}).setdefault(z, []).append((*path_key, path))
        path, path_key = [], None

    for line in gcode.splitlines():
        if line.startswith(";"):
            s = line[1:].strip()
            if s.startswith("Z_HEIGHT:"):
                flush()
                z = round(float(s.split(":")[1]), 3)
            elif s.startswith("LAYER_HEIGHT:"):
                lh = float(s.split(":")[1])
                heights[z] = lh
            elif s.startswith("start printing object, unique label id:"):
                flush()
                obj = int(s.rsplit(":", 1)[1])
            elif s.startswith("stop printing object"):
                flush()
                obj = None
            elif s.startswith("FEATURE:"):
                flush()
                feat = s.split(":", 1)[1].strip()
            elif s.startswith("LINE_WIDTH:"):
                flush()
                width = float(s.split(":")[1])
            continue
        code = line.split(";", 1)[0].strip()
        if not code:
            continue
        w = code.split()
        if w[0] == "M83":
            rel_e = True
        elif w[0] == "M82":
            rel_e = False
        elif w[0] == "G90":
            absolute = True
        elif w[0] == "G91":
            absolute = False
        if w[0] not in ("G0", "G1"):
            continue
        a = {t[0]: float(t[1:]) for t in w[1:] if t[0] in "XYZEF" and len(t) > 1}
        nx = (a["X"] if absolute else x + a["X"]) if "X" in a else x
        ny = (a["Y"] if absolute else y + a["Y"]) if "Y" in a else y
        moved = (nx, ny) != (x, y)
        extruding = a.get("E", 0) > 0 and rel_e and moved
        if extruding and obj is not None and feat not in SKIP:
            key = (feat, width)
            if key != path_key or not path or path[-1] != (x, y):
                flush()
                path, path_key = [(x, y)], key
            path.append((nx, ny))
        elif moved:
            flush()
        x, y = nx, ny
    flush()
    return objs, heights


def layer_region(paths, first=False, foot=0.15):
    """Basılan malzeme (tüm çizgiler, yarım genişlikle) + içindeki boşluklardan yalnız dış duvarla çevrili olanlar
    delik sayılır; dolgu araları gibi diğer boşluklar doldurulur."""
    mat = unary_union([LineString(p).buffer(w / 2, cap_style="round", join_style="round", resolution=4)
                       for _, w, p in paths if len(p) > 1])
    walls = unary_union([LineString(p).buffer(w / 2 + 0.12, resolution=4)
                         for f, w, p in paths if f == "Outer wall" and len(p) > 1])
    out = []
    for poly in polys(mat):
        holes = []
        for ring in poly.interiors:
            line = LineString(ring.coords)
            if not walls.is_empty and line.intersection(walls).length >= 0.85 * line.length:
                holes.append(ring)
        out.append(Polygon(poly.exterior, holes))
    region = unary_union(out).buffer(0.02).buffer(-0.02)
    if first and foot:
        region = region.buffer(foot, join_style="mitre", mitre_limit=2.0)
    return region.simplify(0.02)


def polys(geom):
    if isinstance(geom, Polygon):
        return [geom] if not geom.is_empty else []
    if isinstance(geom, MultiPolygon):
        return list(geom.geoms)
    return [g for g in getattr(geom, "geoms", []) if isinstance(g, Polygon)]


def to_cross_section(geom):
    rings = []
    for p in polys(geom):
        if p.area < 0.05:
            continue
        ext = list(p.exterior.coords)[:-1]
        if not p.exterior.is_ccw:
            ext = ext[::-1]
        rings.append(ext)
        for h in p.interiors:
            r = list(h.coords)[:-1]
            if h.is_ccw:
                r = r[::-1]
            rings.append(r)
    return m3.CrossSection(rings, m3.FillRule.NonZero) if rings else None


def build(layers, heights):
    zs = sorted(layers)
    slabs, cur, z0 = [], None, None
    for k, z in enumerate(zs):
        reg = layer_region(layers[z], first=k == 0)
        bot = round(z - heights.get(z, 0.2), 3)
        # aynı kesit: farkın alanı / çevre (ortalama kenar sapması) 0,03 mm'den küçük
        if cur is not None and k > 1 and reg.symmetric_difference(cur).area < 0.03 * max(cur.length, 1.0):
            top = z
            slabs[-1] = (slabs[-1][0], top, cur)
            continue
        cur = reg
        slabs.append((bot, z, reg))
    solids = []
    for bot, top, reg in slabs:
        cs = to_cross_section(reg)
        if cs is not None:
            solids.append(m3.Manifold.extrude(cs, top - bot).translate((0, 0, bot)))
    man = m3.Manifold.batch_boolean(solids, m3.OpType.Add)
    keep = [c for c in man.decompose() if c.volume() > 0.5]       # birleşimden kalan sıfır hacimli kırıntılar
    return m3.Manifold.compose(keep), len(slabs)


def mesh_xml(oid, man):
    mesh = man.to_mesh()
    V = np.asarray(mesh.vert_properties)[:, :3]
    T = np.asarray(mesh.tri_verts)
    vs = "".join(f'<vertex x="{a:.4f}" y="{b:.4f}" z="{c:.4f}"/>' for a, b, c in V)
    ts = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in T)
    return (f'<object id="{oid}" type="model"><mesh><vertices>{vs}</vertices><triangles>{ts}</triangles></mesh>'
            f'</object>'), len(T)


def write_3mf(path, parts):
    """Yalnız geometri: nesneler G-code'daki konumlarında (plaka koordinatı)."""
    objs, items = [], []
    for k, (name, man) in enumerate(parts, 1):
        xml, _ = mesh_xml(k, man)
        objs.append(xml.replace('type="model">', f'type="model" name="{name}">', 1))
        items.append(f'<item objectid="{k}"/>')
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n<resources>'
             + "".join(objs) + "</resources>\n<build>" + "".join(items) + "</build>\n</model>\n")
    ct = ('<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/'
          'content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.'
          'relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-'
          '3dmodel+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/'
            '2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/'
            '3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)


def main():
    src, dst = sys.argv[1], sys.argv[2]
    with zipfile.ZipFile(src) as z:
        gname = next(n for n in z.namelist() if n.endswith(".gcode"))
        gcode = z.read(gname).decode("utf-8", "replace")
        info = z.read("Metadata/slice_info.config").decode() if "Metadata/slice_info.config" in z.namelist() else ""
    names = {int(i): n.rsplit(".", 1)[0] for i, n in re.findall(r'identify_id="(\d+)" name="([^"]+)"', info)}
    objs, heights = parse(gcode)
    parts = []
    for oid, layers in sorted(objs.items()):
        man, nslab = build(layers, heights)
        lo, hi = np.asarray(man.bounding_box()[:3]), np.asarray(man.bounding_box()[3:])
        name = names.get(oid, f"nesne_{oid}")
        print(f"{name}: {len(layers)} katman → {nslab} dilim, {hi[0] - lo[0]:.2f} × {hi[1] - lo[1]:.2f} × "
              f"{hi[2] - lo[2]:.2f} mm, hacim {man.volume() / 1000:.2f} cm³, {man.num_tri()} üçgen")
        parts.append((name, man))
    write_3mf(dst, parts)
    print("yazıldı:", dst)


if __name__ == "__main__":
    main()
