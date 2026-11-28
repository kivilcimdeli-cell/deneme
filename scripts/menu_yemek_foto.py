"""Örnek menü siteleri için yemek ve içecek fotoğrafları (Blender Cycles, tamamen prosedürel modeller).

Fotoğraf siteleri bu ortamdan erişilemediği için her tabak burada modellenir: pizza, burger, kahve, suşi, et, kokteyl,
çay… Her biri kendi zemininde (ahşap, arduvaz, mermer, keten, kum), yumuşak stüdyo ışığında ve alan derinliğiyle
çizilir.

Çıktı : restoran_masalik/siteler/img/<ad>.jpg (kare, 720 × 720)

Kullanım:
  pip install bpy==4.2.0
  python3 scripts/menu_yemek_foto.py [ad ...] [--ornek 48] [--boyut 720]
"""
import math
import os
import sys

import bpy
import bmesh  # noqa: E402  (bpy'den sonra yüklenir)
import numpy as np
from mathutils import Vector
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "restoran_masalik", "siteler", "img")
TEX = os.path.join(OUT, ".doku")
SIZE = 720
RNG = np.random.default_rng(7)


def srgb(c):
    c = np.asarray(c[:3], float) / 255.0
    return tuple(np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)) + (1.0,)


# ---------------------------------------------------------------- ağ (mesh) yardımcıları

def revolve(prof, n=96, closed=False):
    """(r, z) profilini z ekseni etrafında döndürür. r = 0 olan uçlar tek köşeye iner."""
    prof = [tuple(p) for p in prof]
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    V, rings = [], []
    for r, z in prof:
        if r == 0:
            rings.append([len(V)])
            V.append((0.0, 0.0, z))
        else:
            rings.append(list(range(len(V), len(V) + n)))
            V.extend((r * math.cos(t), r * math.sin(t), z) for t in a)
    F = []
    pairs = list(zip(rings[:-1], rings[1:])) + ([(rings[-1], rings[0])] if closed else [])
    for r0, r1 in pairs:
        for j in range(n):
            k = (j + 1) % n
            if len(r0) == 1:
                F.append((r0[0], r1[k], r1[j]))
            elif len(r1) == 1:
                F.append((r0[j], r0[k], r1[0]))
            else:
                F.append((r0[j], r0[k], r1[k], r1[j]))
    return np.array(V), F


def sphere(r=1.0, nu=48, nv=24):
    t = np.linspace(-math.pi / 2, math.pi / 2, nv + 1)
    return revolve([(0, -r)] + [(r * math.cos(v), r * math.sin(v)) for v in t[1:-1]] + [(0, r)], nu)


def superquad(sx, sy, sz, e=0.25, nu=48, nv=24):
    """Yuvarlatılmış kutu (süper elipsoit): e küçüldükçe köşeler keskinleşir."""
    V, F = sphere(1.0, nu, nv)
    s = lambda x: np.sign(x) * np.abs(x) ** e
    return np.c_[s(V[:, 0]) * sx, s(V[:, 1]) * sy, s(V[:, 2]) * sz], F


def prism(poly, h, z0=0.0):
    """Dışbükey 2B çokgenden prizma."""
    poly = np.asarray(poly, float)
    n = len(poly)
    V = np.r_[np.c_[poly, np.full(n, z0)], np.c_[poly, np.full(n, z0 + h)]]
    F = [tuple(range(n))[::-1], tuple(range(n, 2 * n))]
    F += [(j, (j + 1) % n, n + (j + 1) % n, n + j) for j in range(n)]
    return V, F


def grid(sx, sy, nx, ny):
    xs, ys = np.linspace(-sx / 2, sx / 2, nx + 1), np.linspace(-sy / 2, sy / 2, ny + 1)
    V = np.array([(x, y, 0.0) for y in ys for x in xs])
    F = [(j * (nx + 1) + i, j * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i)
         for j in range(ny) for i in range(nx)]
    return V, F


def disc(r, n=64, rings=12):
    return revolve([(0, 0)] + [(r * (k / rings), 0) for k in range(1, rings + 1)], n)


class Noise:
    """Düzgün 3B gürültü: rastgele düzlem dalgaların toplamı (tekrarlanabilir)."""

    def __init__(self, freq, seed, k=9, octaves=3):
        g = np.random.default_rng(seed)
        self.w = []
        for o in range(octaves):
            d = g.normal(size=(k, 3))
            d /= np.linalg.norm(d, axis=1)[:, None]
            self.w.append((d * freq * 2 ** o, g.uniform(0, 2 * np.pi, k), 0.5 ** o))

    def __call__(self, P):
        P = np.asarray(P, float)
        out = np.zeros(len(P))
        tot = 0
        for d, ph, amp in self.w:
            out += amp * np.sin(P @ d.T + ph).sum(1) / math.sqrt(len(ph))
            tot += amp
        return out / tot


def normals(V, F):
    N = np.zeros_like(V)
    for f in F:
        p = V[list(f)]
        n = np.cross(p[1] - p[0], p[2] - p[0])
        if len(f) == 4:
            n += np.cross(p[2] - p[0], p[3] - p[0])
        N[list(f)] += n
    L = np.linalg.norm(N, axis=1)
    L[L == 0] = 1
    return N / L[:, None]


def wobble(V, F, amp, freq, seed, octaves=3):
    """Organik yüzey: köşeleri normal boyunca gürültüyle oynatır."""
    return V + normals(V, F) * (amp * Noise(freq, seed, octaves=octaves)(V))[:, None]


def obj(name, VF, mat, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), smooth=True, subsurf=0, solid=0.0,
        bevel=0.0, parent=None):
    V, F = VF
    me = bpy.data.meshes.new(name)
    me.from_pydata(np.asarray(V, float).tolist(), [], [tuple(int(i) for i in f) for f in F])
    me.update()
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    ob = bpy.data.objects.new(name, me)
    ob.location, ob.rotation_euler, ob.scale = loc, [math.radians(r) for r in rot], scale
    if parent is not None:
        ob.parent = parent
    if solid:
        m = ob.modifiers.new("kalinlik", "SOLIDIFY")
        m.thickness = solid
        m.offset = -1
    if bevel:
        m = ob.modifiers.new("pah", "BEVEL")
        m.width = bevel
        m.segments = 3
        m.limit_method = "ANGLE"
    if subsurf:
        m = ob.modifiers.new("yumusak", "SUBSURF")
        m.levels = m.render_levels = subsurf
    ob.data.materials.append(mat)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def tube(name, pts, r, mat, res=6):
    """Nokta dizisinden yuvarlak kesitli tüp (erişte, sap, sos çizgisi)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = res
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts):
        p.co = (*q, 1.0)
    ob = bpy.data.objects.new(name, cu)
    cu.materials.append(mat)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def scatter_disc(n, r, minsep, seed, r0=0.0):
    g = np.random.default_rng(seed)
    pts = []
    for _ in range(n * 60):
        a, rr = g.uniform(0, 2 * np.pi), r * math.sqrt(g.uniform((r0 / r) ** 2, 1))
        p = np.array([rr * math.cos(a), rr * math.sin(a)])
        if all(np.linalg.norm(p - q) >= minsep for q in pts):
            pts.append(p)
        if len(pts) == n:
            break
    return pts


# ---------------------------------------------------------------- malzemeler

def node(nt, kind, loc=(0, 0), **inputs):
    n = nt.nodes.new(kind)
    n.location = loc
    for k, v in inputs.items():
        n.inputs[k].default_value = v
    return n


def mat(name, base, rough=0.5, var=None, var_scale=40.0, bump=0.0, bump_scale=60.0, sss=0.0, sss_r=(1, 0.4, 0.2),
        trans=0.0, ior=1.45, coat=0.0, metal=0.0, spec=0.5, sheen=0.0, ramp=None, coord="Object", stretch=(1, 1, 1),
        voronoi=0.0, emit=0.0):
    """Principled: base rengi; var=(ikinci renk, oran) ile gürültülü renk; bump ile pürüz; sss, cam, vernik.
    ramp=[(konum, renk), ...] verilirse renk gürültü yerine bu rampadan gelir."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = node(nt, "ShaderNodeOutputMaterial", (900, 0))
    b = node(nt, "ShaderNodeBsdfPrincipled", (600, 0))
    nt.links.new(b.outputs["BSDF"], out.inputs["Surface"])
    b.inputs["Base Color"].default_value = srgb(base)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["IOR"].default_value = ior
    b.inputs["Specular IOR Level"].default_value = spec
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Radius"].default_value = sss_r
        b.inputs["Subsurface Scale"].default_value = 0.004
    if trans:
        b.inputs["Transmission Weight"].default_value = trans
    if coat:
        b.inputs["Coat Weight"].default_value = coat
        b.inputs["Coat Roughness"].default_value = 0.05
    if sheen:
        b.inputs["Sheen Weight"].default_value = sheen
    if emit:
        b.inputs["Emission Color"].default_value = srgb(base)
        b.inputs["Emission Strength"].default_value = emit
    tc = node(nt, "ShaderNodeTexCoord", (-1100, 0))
    mp = node(nt, "ShaderNodeMapping", (-900, 0))
    mp.inputs["Scale"].default_value = stretch
    nt.links.new(tc.outputs[coord], mp.inputs["Vector"])
    if var or ramp:
        nz = node(nt, "ShaderNodeTexNoise", (-650, 250), Scale=var_scale, Detail=6.0, Roughness=0.6)
        nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
        r = node(nt, "ShaderNodeValToRGB", (-350, 250))
        els = r.color_ramp.elements
        stops = ramp or [(0.35, base), (0.65, var[0])]
        els[0].position, els[0].color = stops[0][0], srgb(stops[0][1])
        els[1].position, els[1].color = stops[-1][0], srgb(stops[-1][1])
        for p, c in stops[1:-1]:
            els.new(p).color = srgb(c)
        if var and not ramp:
            els[1].position = 0.35 + 0.3 * var[1] * 2
        nt.links.new(nz.outputs["Fac"], r.inputs["Fac"])
        nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
    if bump:
        if voronoi:
            bz = node(nt, "ShaderNodeTexVoronoi", (-650, -250), Scale=bump_scale)
            bz.feature = "SMOOTH_F1" if voronoi == 1 else "DISTANCE_TO_EDGE"
            h = bz.outputs["Distance"]
        else:
            bz = node(nt, "ShaderNodeTexNoise", (-650, -250), Scale=bump_scale, Detail=8.0, Roughness=0.65)
            h = bz.outputs["Fac"]
        nt.links.new(mp.outputs["Vector"], bz.inputs["Vector"])
        bp = node(nt, "ShaderNodeBump", (300, -250), Strength=bump, Distance=0.002)
        nt.links.new(h, bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    if trans >= 0.5:
        c = srgb(base)
        clear_shadow(m, tuple(0.35 + 0.65 * v for v in c[:3]) + (1.0,))
    return m


def mat_tex(name, path, rough=0.4, coat=0.0, sss=0.0, bump=0.0, size=1.0, alpha=False):
    """PIL ile çizilmiş dokuyu nesnenin XY'sine (−size/2 … size/2) yayar."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = node(nt, "ShaderNodeOutputMaterial", (900, 0))
    b = node(nt, "ShaderNodeBsdfPrincipled", (600, 0), Roughness=rough)
    nt.links.new(b.outputs["BSDF"], out.inputs["Surface"])
    if coat:
        b.inputs["Coat Weight"].default_value = coat
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Scale"].default_value = 0.003
    tc = node(nt, "ShaderNodeTexCoord", (-900, 0))
    mp = node(nt, "ShaderNodeMapping", (-700, 0))
    mp.inputs["Scale"].default_value = (1 / size, 1 / size, 1)
    mp.inputs["Location"].default_value = (0.5, 0.5, 0)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    im = node(nt, "ShaderNodeTexImage", (-400, 0))
    im.image = bpy.data.images.load(path)
    im.extension = "EXTEND"
    nt.links.new(mp.outputs["Vector"], im.inputs["Vector"])
    nt.links.new(im.outputs["Color"], b.inputs["Base Color"])
    if alpha:
        nt.links.new(im.outputs["Alpha"], b.inputs["Alpha"])
    if bump:
        bp = node(nt, "ShaderNodeBump", (300, -250), Strength=bump, Distance=0.001)
        nt.links.new(im.outputs["Color"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def mat_cut(name, inner, mid, outer, half, edge=(0.78, 0.9), rough=0.45, coat=0.0, bump=0.4, sss=0.0, radial=None):
    """Kesit rengi: nesne koordinatında max(|x|/hx, …) ile içten dışa (pembe et → gri → kızarmış kabuk).
    radial=R verilirse xy düzlemindeki uzaklık da (ρ/R) hesaba katılır (dilim pasta, chashu)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = node(nt, "ShaderNodeOutputMaterial", (1100, 0))
    b = node(nt, "ShaderNodeBsdfPrincipled", (800, 0), Roughness=rough)
    if coat:
        b.inputs["Coat Weight"].default_value = coat
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Scale"].default_value = 0.003
    nt.links.new(b.outputs["BSDF"], out.inputs["Surface"])
    tc = node(nt, "ShaderNodeTexCoord", (-1200, 0))
    sep = node(nt, "ShaderNodeSeparateXYZ", (-1000, 0))
    nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])
    vals = []
    for k, ax in enumerate("XYZ"):
        if half[k] is None:
            continue
        ab = node(nt, "ShaderNodeMath", (-800, 150 - 150 * k))
        ab.operation = "ABSOLUTE"
        nt.links.new(sep.outputs[ax], ab.inputs[0])
        dv = node(nt, "ShaderNodeMath", (-650, 150 - 150 * k))
        dv.operation = "DIVIDE"
        dv.inputs[1].default_value = half[k]
        nt.links.new(ab.outputs[0], dv.inputs[0])
        vals.append(dv.outputs[0])
    if radial:
        ln = node(nt, "ShaderNodeVectorMath", (-800, 400))
        ln.operation = "LENGTH"
        mk = node(nt, "ShaderNodeVectorMath", (-1000, 400))
        mk.operation = "MULTIPLY"
        mk.inputs[1].default_value = (1, 1, 0)
        nt.links.new(tc.outputs["Object"], mk.inputs[0])
        nt.links.new(mk.outputs[0], ln.inputs[0])
        dv = node(nt, "ShaderNodeMath", (-650, 400))
        dv.operation = "DIVIDE"
        dv.inputs[1].default_value = radial
        nt.links.new(ln.outputs["Value"], dv.inputs[0])
        vals.append(dv.outputs[0])
    cur = vals[0]
    for v in vals[1:]:
        mx = node(nt, "ShaderNodeMath", (-450, 0))
        mx.operation = "MAXIMUM"
        nt.links.new(cur, mx.inputs[0])
        nt.links.new(v, mx.inputs[1])
        cur = mx.outputs[0]
    nz = node(nt, "ShaderNodeTexNoise", (-450, -300), Scale=300.0, Detail=6.0)
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    ad = node(nt, "ShaderNodeMath", (-250, 0))
    ad.operation = "MULTIPLY_ADD"
    ad.inputs[1].default_value = 0.08
    nt.links.new(nz.outputs["Fac"], ad.inputs[0])
    nt.links.new(cur, ad.inputs[2])
    r = node(nt, "ShaderNodeValToRGB", (0, 0))
    els = r.color_ramp.elements
    els[0].position, els[0].color = edge[0] - 0.05, srgb(inner)
    els[1].position, els[1].color = edge[1] + 0.06, srgb(outer)
    els.new(edge[1] - 0.02).color = srgb(mid)
    nt.links.new(ad.outputs[0], r.inputs["Fac"])
    nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
    if bump:
        bz = node(nt, "ShaderNodeTexNoise", (300, -300), Scale=500.0, Detail=8.0)
        nt.links.new(tc.outputs["Object"], bz.inputs["Vector"])
        bp = node(nt, "ShaderNodeBump", (550, -300), Strength=bump, Distance=0.001)
        nt.links.new(bz.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def mat_zgrad(name, stops, z0, z1, trans=1.0, rough=0.05, ior=1.34, sss=0.0):
    """Yüksekliğe göre renk geçişi (gün batımı kokteyli, katmanlı latte)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    b.inputs["IOR"].default_value = ior
    b.inputs["Transmission Weight"].default_value = trans
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Scale"].default_value = 0.004
    tc = node(nt, "ShaderNodeTexCoord", (-900, 0))
    sep = node(nt, "ShaderNodeSeparateXYZ", (-700, 0))
    nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])
    mr = node(nt, "ShaderNodeMapRange", (-500, 0))
    mr.inputs["From Min"].default_value = z0
    mr.inputs["From Max"].default_value = z1
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    r = node(nt, "ShaderNodeValToRGB", (-250, 0))
    els = r.color_ramp.elements
    els[0].position, els[0].color = stops[0][0], srgb(stops[0][1])
    els[1].position, els[1].color = stops[-1][0], srgb(stops[-1][1])
    for p, c in stops[1:-1]:
        els.new(p).color = srgb(c)
    nt.links.new(mr.outputs["Result"], r.inputs["Fac"])
    nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
    if trans >= 0.5:
        clear_shadow(m, (0.9, 0.7, 0.5, 1.0))
    return m


def mat_stripes(name, base, stripe, scale, rough=0.4, coat=0.0, sss=0.0, direction=(1, 1, 0), width=0.18):
    """Çizgili yüzey: somon yağ çizgileri, ızgara izleri."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    if coat:
        b.inputs["Coat Weight"].default_value = coat
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Scale"].default_value = 0.003
    tc = node(nt, "ShaderNodeTexCoord", (-1100, 0))
    dot = node(nt, "ShaderNodeVectorMath", (-900, 0))
    dot.operation = "DOT_PRODUCT"
    dot.inputs[1].default_value = direction
    nt.links.new(tc.outputs["Object"], dot.inputs[0])
    nz = node(nt, "ShaderNodeTexNoise", (-900, -250), Scale=120.0, Detail=4.0)
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    ad = node(nt, "ShaderNodeMath", (-700, 0))
    ad.operation = "MULTIPLY_ADD"
    ad.inputs[1].default_value = 1.0 / scale * 0.15
    nt.links.new(nz.outputs["Fac"], ad.inputs[0])
    nt.links.new(dot.outputs["Value"], ad.inputs[2])
    mul = node(nt, "ShaderNodeMath", (-550, 0))
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = scale
    nt.links.new(ad.outputs[0], mul.inputs[0])
    fr = node(nt, "ShaderNodeMath", (-400, 0))
    fr.operation = "PINGPONG"
    fr.inputs[1].default_value = 0.5
    nt.links.new(mul.outputs[0], fr.inputs[0])
    r = node(nt, "ShaderNodeValToRGB", (-200, 0))
    els = r.color_ramp.elements
    els[0].position, els[0].color = width * 0.5, srgb(stripe)
    els[1].position, els[1].color = width * 0.5 + 0.12, srgb(base)
    nt.links.new(fr.outputs[0], r.inputs["Fac"])
    nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
    bp = node(nt, "ShaderNodeBump", (300, -250), Strength=0.3, Distance=0.001)
    nt.links.new(fr.outputs[0], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def clear_shadow(m, tint=None):
    """Cam ve sıvılar gölge ışınlarına saydam görünür (yakıcı ışık olmadan içi kararmasın diye)."""
    nt = m.node_tree
    out = [n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"][0]
    src = out.inputs["Surface"].links[0].from_socket
    lp = node(nt, "ShaderNodeLightPath", (500, 400))
    tr = node(nt, "ShaderNodeBsdfTransparent", (500, 250))
    if tint:
        tr.inputs["Color"].default_value = tint
    mx = node(nt, "ShaderNodeMixShader", (780, 200))
    nt.links.new(lp.outputs["Is Shadow Ray"], mx.inputs["Fac"])
    nt.links.new(src, mx.inputs[1])
    nt.links.new(tr.outputs["BSDF"], mx.inputs[2])
    nt.links.new(mx.outputs["Shader"], out.inputs["Surface"])
    return m


_M = {}


def M(key):
    """Ortak malzemeler (her sahnede bir kez yaratılır)."""
    if key in _M:
        return _M[key]
    f = {
        "porselen": lambda: mat("porselen", (246, 244, 239), rough=0.12, coat=0.6, spec=0.6),
        "porselen_krem": lambda: mat("porselen_krem", (238, 230, 214), rough=0.15, coat=0.5),
        "seramik_siyah": lambda: mat("seramik_siyah", (32, 31, 30), rough=0.35, var=((48, 46, 44), 0.5), var_scale=90,
                                     bump=0.05, bump_scale=300),
        "seramik_lacivert": lambda: mat("seramik_lacivert", (30, 44, 78), rough=0.18, coat=0.5,
                                        var=((44, 62, 104), 0.5), var_scale=30),
        "seramik_tas": lambda: mat("seramik_tas", (196, 186, 170), rough=0.55, var=((168, 156, 140), 0.5),
                                   var_scale=80, bump=0.1, bump_scale=400),
        "toprak": lambda: mat("toprak", (166, 82, 48), rough=0.6, var=((128, 60, 34), 0.5), var_scale=40, bump=0.1,
                              bump_scale=200),
        "cam": lambda: mat("cam", (255, 255, 255), rough=0.0, trans=1.0, ior=1.5, spec=0.5),
        "buz": lambda: mat("buz", (245, 250, 255), rough=0.08, trans=1.0, ior=1.31, bump=0.15, bump_scale=30),
        "metal": lambda: mat("metal", (220, 218, 214), rough=0.18, metal=1.0),
        "altin": lambda: mat("altin", (214, 170, 92), rough=0.25, metal=1.0),
        "hamur": lambda: mat("hamur", (226, 186, 128), rough=0.6, sss=0.15, sss_r=(1, 0.6, 0.3),
                             ramp=[(0.30, (236, 204, 150)), (0.55, (204, 140, 72)), (0.72, (150, 84, 36)),
                                   (0.80, (52, 30, 18))], var_scale=26, bump=0.25, bump_scale=90),
        "ekmek": lambda: mat("ekmek", (176, 96, 38), rough=0.38, coat=0.25, sss=0.1,
                             ramp=[(0.3, (190, 112, 46)), (0.7, (140, 70, 26))], var_scale=12, bump=0.12,
                             bump_scale=60),
        "ekmek_ic": lambda: mat("ekmek_ic", (234, 210, 168), rough=0.8, var=((214, 186, 140), 0.5), bump=0.3,
                                bump_scale=200),
        "susam": lambda: mat("susam", (240, 226, 192), rough=0.45, sss=0.2),
        "maydanoz": lambda: mat("maydanoz", (52, 112, 38), rough=0.35, var=((78, 140, 52), 0.5), sss=0.25,
                                sss_r=(0.3, 1, 0.2), coat=0.2),
        "feslegen": lambda: mat("feslegen", (40, 104, 36), rough=0.25, coat=0.4, var=((66, 132, 44), 0.5), sss=0.3,
                                sss_r=(0.3, 1, 0.2)),
        "nane": lambda: mat("nane", (58, 132, 52), rough=0.35, var=((86, 160, 66), 0.5), sss=0.3, bump=0.2,
                            bump_scale=150, sss_r=(0.3, 1, 0.2)),
        "limon": lambda: mat("limon", (238, 206, 64), rough=0.35, coat=0.3, bump=0.25, bump_scale=300,
                             var=((246, 222, 90), 0.5)),
        "portakal_kabuk": lambda: mat("portakal_kabuk", (236, 118, 26), rough=0.4, bump=0.3, bump_scale=300,
                                      var=((248, 142, 40), 0.5)),
        "kiraz": lambda: mat("kiraz", (96, 8, 18), rough=0.12, coat=1.0, sss=0.2),
        "domates": lambda: mat("domates", (196, 36, 24), rough=0.2, coat=0.6, sss=0.25, var=((222, 64, 32), 0.5)),
        "tuz": lambda: mat("tuz", (250, 250, 250), rough=0.3, trans=0.4, ior=1.5),
        "biber_yesil": lambda: mat("biber_yesil", (58, 118, 32), rough=0.15, coat=0.8, var=((44, 84, 24), 0.4),
                                   var_scale=20, sss=0.2),
        "biberiye": lambda: mat("biberiye", (54, 84, 46), rough=0.5),
        "dal": lambda: mat("dal", (92, 74, 50), rough=0.7),
        "sos_kahve": lambda: mat("sos_kahve", (60, 30, 14), rough=0.15, coat=0.8),
        "turuncu_sos": lambda: mat("turuncu_sos", (236, 118, 50), rough=0.25, sss=0.3, coat=0.4),
        "pipet": lambda: mat("pipet", (30, 30, 30), rough=0.4),
    }[key]
    _M[key] = f()
    return _M[key]


# ---------------------------------------------------------------- dokular (PIL)

def tex_path(name):
    os.makedirs(TEX, exist_ok=True)
    return os.path.join(TEX, name + ".png")


def tex_latte(name, seed=1, base=(158, 96, 50), foam=(246, 236, 220), kind="rosetta"):
    p = tex_path(name)
    S = 1024
    im = Image.new("RGB", (S, S), base)
    dr = ImageDraw.Draw(im)
    g = np.random.default_rng(seed)
    c = S / 2
    if kind == "rosetta":
        for k in range(11):
            y = c + 290 - k * 52
            w = 300 - k * 22 + g.uniform(-8, 8)
            h = 40 - k * 1.5
            dr.ellipse((c - w / 2, y - h, c + w / 2, y + h), fill=foam)
            dr.ellipse((c - w / 2 + 16, y - h + 18, c + w / 2 - 16, y + h + 10), fill=base)
        dr.line((c, c + 330, c, c - 290), fill=foam, width=14)
        dr.ellipse((c - 60, c - 360, c + 60, c - 250), fill=foam)
    else:                                                   # kalp: iki daire + aşağı bakan üçgen, ortadan akış izi
        for dx in (-118, 118):
            dr.ellipse((c + dx - 138, c - 210, c + dx + 138, c + 66), fill=foam)
        dr.polygon([(c - 252, c - 40), (c + 252, c - 40), (c, c + 290)], fill=foam)
        dr.ellipse((c - 70, c - 150, c + 70, c - 40), fill=base)
        dr.ellipse((c - 50, c - 140, c + 50, c - 60), fill=foam)
        dr.line((c, c - 230, c, c + 300), fill=base, width=10)
    im = im.filter(ImageFilter.GaussianBlur(7))
    a = np.asarray(im).astype(float)
    yy, xx = np.mgrid[0:S, 0:S]
    rr = np.hypot(xx - c, yy - c) / (S / 2)
    ring = np.clip((rr - 0.80) / 0.2, 0, 1)[..., None]
    a = a * (1 - ring * 0.55) + np.array(base) * 0.55 * ring * 0.75
    a += g.normal(0, 4, a.shape)
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(p)
    return p


def tex_citrus(name, rind=(232, 110, 20), pith=(250, 236, 200), flesh=(246, 140, 40), seg=10):
    p = tex_path(name)
    S = 1024
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    c = S / 2
    dr.ellipse((4, 4, S - 4, S - 4), fill=rind + (255,))
    dr.ellipse((36, 36, S - 36, S - 36), fill=pith + (255,))
    R = c - 60
    for k in range(seg):
        a0, a1 = 2 * math.pi * k / seg + 0.05, 2 * math.pi * (k + 1) / seg - 0.05
        pts = [(c + 18 * math.cos((a0 + a1) / 2), c + 18 * math.sin((a0 + a1) / 2))]
        pts += [(c + R * math.cos(a), c + R * math.sin(a)) for a in np.linspace(a0, a1, 12)]
        dr.polygon(pts, fill=flesh + (255,))
    im = im.filter(ImageFilter.GaussianBlur(3))
    a = np.asarray(im).astype(float)
    g = np.random.default_rng(3)
    a[..., :3] += g.normal(0, 7, a[..., :3].shape)
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(p)
    return p


# ---------------------------------------------------------------- sahne: zemin, ışık, kamera

SURF = {
    "ceviz": ((74, 46, 28), (150, 104, 66), 0.45),
    "mese": ((176, 136, 92), (214, 178, 132), 0.5),
    "arduvaz": ((36, 38, 40), (58, 60, 62), 0.6),
    "mermer": ((236, 234, 230), (190, 188, 186), 0.3),
    "keten": ((222, 212, 194), (236, 228, 214), 0.85),
    "kum": ((226, 204, 168), (240, 222, 190), 0.9),
    "beton": ((120, 118, 114), (150, 148, 144), 0.8),
    "siyah_mermer": ((22, 22, 24), (70, 66, 62), 0.25),
    "terrakota": ((178, 92, 60), (204, 120, 84), 0.8),
    "yesil_kadife": ((34, 58, 44), (46, 74, 56), 0.9),
}


def surface(kind):
    a, b, rough = SURF[kind]
    m = bpy.data.materials.new("zemin")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = node(nt, "ShaderNodeOutputMaterial", (1000, 0))
    bs = node(nt, "ShaderNodeBsdfPrincipled", (700, 0), Roughness=rough)
    nt.links.new(bs.outputs["BSDF"], out.inputs["Surface"])
    tc = node(nt, "ShaderNodeTexCoord", (-1000, 0))
    mp = node(nt, "ShaderNodeMapping", (-800, 0))
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    r = node(nt, "ShaderNodeValToRGB", (200, 0))
    els = r.color_ramp.elements
    els[0].color, els[1].color = srgb(a), srgb(b)
    if kind in ("ceviz", "mese"):
        mp.inputs["Scale"].default_value = (1.0, 9.0, 1.0)
        wave = node(nt, "ShaderNodeTexWave", (-350, 0), Scale=18.0, Distortion=10.0, Detail=5.0)
        wave.bands_direction = "Y"
        nt.links.new(mp.outputs["Vector"], wave.inputs["Vector"])
        h = wave.outputs["Fac"]
        els[0].position, els[1].position = 0.25, 0.8
    elif kind in ("mermer", "siyah_mermer"):
        nz = node(nt, "ShaderNodeTexNoise", (-350, 0), Scale=3.0, Detail=10.0, Distortion=5.0)
        nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
        h = nz.outputs["Fac"]
        els[0].color, els[1].color = srgb(a), srgb(a)
        els[0].position, els[1].position = 0.49, 0.51
        els.new(0.5).color = srgb(b)
        bs.inputs["Coat Weight"].default_value = 0.6
    elif kind == "keten":
        mp.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
        w1 = node(nt, "ShaderNodeTexWave", (-350, 100), Scale=220.0, Distortion=1.5)
        w1.bands_direction = "X"
        w2 = node(nt, "ShaderNodeTexWave", (-350, -100), Scale=220.0, Distortion=1.5)
        w2.bands_direction = "Y"
        for w in (w1, w2):
            nt.links.new(mp.outputs["Vector"], w.inputs["Vector"])
        mx = node(nt, "ShaderNodeMath", (-100, 0))
        mx.operation = "MULTIPLY"
        nt.links.new(w1.outputs["Fac"], mx.inputs[0])
        nt.links.new(w2.outputs["Fac"], mx.inputs[1])
        h = mx.outputs[0]
        bs.inputs["Sheen Weight"].default_value = 0.5
    else:
        nz = node(nt, "ShaderNodeTexNoise", (-350, 0), Scale=14.0 if kind != "kum" else 400.0, Detail=10.0,
                  Roughness=0.65)
        nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
        h = nz.outputs["Fac"]
    nt.links.new(h, r.inputs["Fac"])
    nt.links.new(r.outputs["Color"], bs.inputs["Base Color"])
    bp = node(nt, "ShaderNodeBump", (450, -250), Strength=0.15 if kind != "kum" else 0.5)
    nt.links.new(h, bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], bs.inputs["Normal"])
    return m


def setup(surf, samples, world=(240, 232, 220), wstr=0.12, exposure=0.0, glass=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _M.clear()
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.02
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 32 if glass else 8
    sc.cycles.transmission_bounces = 32 if glass else 8
    sc.cycles.transparent_max_bounces = 32
    sc.cycles.caustics_reflective = sc.cycles.caustics_refractive = False
    sc.cycles.blur_glossy = 1.0
    sc.render.resolution_x = sc.render.resolution_y = SIZE
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
    sc.view_settings.exposure = exposure
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 88
    w = bpy.data.worlds.new("dunya")
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = srgb(world)
    bg.inputs["Strength"].default_value = wstr
    sc.world = w
    s = 2.0
    me = bpy.data.meshes.new("zemin")
    me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    ob = bpy.data.objects.new("zemin", me)
    ob.data.materials.append(surface(surf))
    sc.collection.objects.link(ob)
    return sc


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def camera(target, dist, elev, azim=0.0, lens=85, fstop=4.0, roll=0.0):
    cd = bpy.data.cameras.new("kamera")
    cd.lens = lens
    cd.dof.use_dof = True
    cd.dof.focus_distance = dist
    cd.dof.aperture_fstop = fstop
    cam = bpy.data.objects.new("kamera", cd)
    e, a = math.radians(elev), math.radians(azim)
    t = np.asarray(target, float)
    cam.location = tuple(t + dist * np.array([math.cos(e) * math.sin(a), -math.cos(e) * math.cos(a), math.sin(e)]))
    if elev >= 89.9:
        cam.rotation_euler = (0, 0, math.radians(azim))
    else:
        look_at(cam, target)
        cam.rotation_euler.rotate_axis("Z", math.radians(roll))
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


def light(name, power, size, azim, elev, dist, target=(0, 0, 0.03), color=(255, 248, 238), spot=False):
    ld = bpy.data.lights.new(name, "SPOT" if spot else "AREA")
    ld.energy = power
    if spot:
        ld.shadow_soft_size = size
        ld.spot_size = math.radians(60)
    else:
        ld.size = size
    ld.color = srgb(color)[:3]
    ob = bpy.data.objects.new(name, ld)
    e, a = math.radians(elev), math.radians(azim)
    t = np.asarray(target, float)
    ob.location = tuple(t + dist * np.array([math.cos(e) * math.sin(a), -math.cos(e) * math.cos(a), math.sin(e)]))
    look_at(ob, target)
    ob.visible_camera = False
    bpy.context.scene.collection.objects.link(ob)
    return ob


def studio(key=(-120, 40), power=22.0, warm=(255, 244, 228), fill=0.2, rim=0.5, target=(0, 0, 0.03), dist=0.9,
           size=0.6):
    """Pencere ışığı (yan-arka), yumuşak dolgu ve arka parlama: yemek fotoğrafçılığının klasik düzeni."""
    light("ana", power, size, key[0], key[1], dist, target, warm)
    light("dolgu", power * fill, 1.2, key[0] + 160, 30, dist * 1.2, target, (236, 242, 255))
    if rim:
        light("arka", power * rim, 0.4, key[0] - 70, 25, dist, target, (255, 236, 210))


def bokeh(n, z, spread, dist, cols, seed=1, power=6.0, size=0.012):
    """Arka planda bulanık ışık noktaları (gece, teras)."""
    g = np.random.default_rng(seed)
    for k in range(n):
        m = mat(f"bokeh{k}", cols[k % len(cols)], emit=power)
        obj(f"bokeh{k}", sphere(size * g.uniform(0.6, 1.3), 12, 6), m,
            loc=(g.uniform(-spread, spread), dist + g.uniform(-0.2, 0.3), z + g.uniform(-0.15, 0.25)))


def glow(color, power, y=0.35, w=0.4, h=0.22, z=0.0, x=0.0):
    """Arkadan aydınlatan yumuşak ışık paneli (bar arkası): sıvıyı içinden parlatır, alan derinliğiyle bulanır."""
    m = mat("isik_panel", color, emit=power, rough=1.0)
    ob = obj("isik_panel", ([(x - w / 2, y, z), (x + w / 2, y, z), (x + w / 2, y, z + h), (x - w / 2, y, z + h)],
                            [(0, 1, 2, 3)]), m, smooth=False)
    ob.visible_camera = False                               # yalnız camın ardından (kırılarak) görünür


def backdrop(color, dist=0.7, rough=0.9, h=3.0, var=None):
    """Arka fon duvarı (alçak açılı çekimlerde ufuk görünmesin)."""
    m = mat("fon", color, rough=rough, var=(var, 0.5) if var else None, var_scale=3)
    obj("fon", ([(-3, dist, 0), (3, dist, 0), (3, dist, h), (-3, dist, h)], [(0, 1, 2, 3)]), m, smooth=False)


def render(name):
    sc = bpy.context.scene
    sc.render.filepath = os.path.join(OUT, name + ".jpg")
    bpy.ops.render.render(write_still=True)


# ---------------------------------------------------------------- servis: tabak, kase, tahta, fincan, bardak

def plate(r=0.14, mat_key="porselen", z=0.0, rim=0.25, depth=0.016, name="tabak"):
    ri = r * (1 - rim)
    prof = [(0, z + 0.004), (ri, z + 0.004), (ri + (r - ri) * 0.5, z + depth * 0.7), (r, z + depth),
            (r + 0.002, z + depth - 0.002), (r - 0.004, z + depth - 0.006), (ri + (r - ri) * 0.4, z + 0.003),
            (ri * 0.7, z), (0, z)]
    obj(name, revolve(prof, 128), M(mat_key))
    return z + 0.004


def bowl(r=0.09, h=0.06, mat_key="seramik_siyah", z=0.0, t=0.006, foot=0.4, name="kase"):
    fr = r * foot
    out = [(0, z), (fr, z), (fr, z + 0.006)] + [
        (fr + (r - fr) * math.sin(u * math.pi / 2), z + 0.006 + (h - 0.006) * (1 - math.cos(u * math.pi / 2)))
        for u in np.linspace(0.05, 1, 14)]
    inner = [(r - t, z + h)] + [
        ((r - t) * math.sin(u * math.pi / 2) * 0.98, z + t * 1.5 + (h - t * 1.5) * (1 - math.cos(u * math.pi / 2)))
        for u in np.linspace(0.95, 0.02, 12)] + [(0, z + t * 1.5)]
    prof = out + [(r - t * 0.3, z + h + 0.002)] + inner
    obj(name, revolve(prof, 128), M(mat_key))
    return lambda frac: (z + t * 1.5 + (h - t * 1.5) * frac, (r - t) * math.sin(math.acos(1 - frac) if frac < 1
                                                                                  else math.pi / 2) * 0.98)


def board(w, d, h=0.022, kind="ceviz", r=0.03, loc=(0, 0, 0), rot=0, handle=False, name="tahta"):
    col = {"ceviz": ((96, 62, 38), (138, 94, 58)), "mese": ((190, 148, 100), (214, 176, 128)),
           "zeytin": ((168, 132, 86), (120, 86, 52)), "arduvaz": ((40, 42, 44), (52, 54, 56))}[kind]
    m = mat(name, col[0], rough=0.55 if kind != "arduvaz" else 0.7, var=(col[1], 0.5), var_scale=8,
            stretch=(1, 12, 1), bump=0.15, bump_scale=40)
    a = np.linspace(0, 2 * np.pi, 64, endpoint=False)
    pts = []
    for cx, cy, a0 in ((w / 2 - r, d / 2 - r, 0), (-w / 2 + r, d / 2 - r, 90), (-w / 2 + r, -d / 2 + r, 180),
                       (w / 2 - r, -d / 2 + r, 270)):
        pts += [(cx + r * math.cos(math.radians(a0 + t)), cy + r * math.sin(math.radians(a0 + t)))
                for t in np.linspace(0, 90, 8)]
    if handle:
        pts = [p for p in pts]
    ob = obj(name, prism(pts, h), m, loc=loc, rot=(0, 0, rot), smooth=False, bevel=0.003)
    if handle:
        hm = prism([(w / 2 - 0.004, -0.018), (w / 2 + 0.07, -0.016), (w / 2 + 0.07, 0.016), (w / 2 - 0.004, 0.018)], h)
        obj(name + "_sap", hm, m, loc=loc, rot=(0, 0, rot), smooth=False, bevel=0.003)
        obj(name + "_delik", revolve([(0, -0.001), (0.007, -0.001), (0.007, h + 0.001), (0, h + 0.001)], 32),
            mat("delik", (20, 16, 12), rough=0.9), loc=(loc[0] + (w / 2 + 0.05) * math.cos(math.radians(rot)),
                                                         loc[1] + (w / 2 + 0.05) * math.sin(math.radians(rot)),
                                                         loc[2] - 0.0005 + 0.0))
    return loc[2] + h


def cup(r=0.042, h=0.07, mat_key="porselen", z=0.0, t=0.004, handle=True, loc=(0, 0), rot=0.0, flare=1.12,
        name="fincan"):
    """Fincan: dış ve iç profil, kulp. Sıvı yüzeyi için (z_yuzey, r_yuzey) fonksiyonu döner."""
    rb = r * 0.62
    out = [(0, z), (rb, z), (rb + 0.002, z + 0.004)] + [
        (rb + (r * flare - rb) * (u ** 0.6), z + 0.004 + (h - 0.004) * u) for u in np.linspace(0.08, 1, 14)]
    rt = r * flare
    inner = [(rt - t, z + h)] + [(rb - t + (rt - rb) * (u ** 0.6), z + t + (h - t) * u)
                                 for u in np.linspace(0.97, 0.05, 12)] + [(0, z + t)]
    prof = out + [(rt - t * 0.4, z + h + 0.0015)] + inner
    parts = [obj(name, revolve(prof, 128), M(mat_key), loc=(*loc, 0))]
    if handle:
        hp = [(r * 0.95 + 0.019 * math.sin(u), 0, z + h * 0.55 + 0.022 * math.cos(u)) for u in np.linspace(0.2, 2.9, 20)]
        hp = [(x * math.cos(math.radians(rot)) + loc[0], x * math.sin(math.radians(rot)) + loc[1], zz) for x, _, zz in hp]
        tb = tube(name + "_kulp", hp, 0.0042, M(mat_key))
        tb.data.bevel_resolution = 6
    surf = lambda frac: (z + t + (h - t) * frac, rb - t + (rt - rb) * (frac ** 0.6) - 0.0005)
    return surf


def saucer(r=0.075, z=0.0, mat_key="porselen", loc=(0, 0), name="tabak_alti"):
    prof = [(0, z + 0.004), (r * 0.42, z + 0.004), (r * 0.48, z + 0.0055), (r * 0.8, z + 0.009), (r, z + 0.014),
            (r + 0.0015, z + 0.0125), (r * 0.8, z + 0.006), (r * 0.5, z + 0.002), (r * 0.4, z), (0, z)]
    obj(name, revolve(prof, 128), M(mat_key), loc=(*loc, 0))
    return z + 0.0055


def glass(prof_out, t=0.0022, bottom=0.012, n=128, loc=(0, 0, 0), name="bardak"):
    """Cam: dış profil (r, z) yukarı doğru; iç profil t kadar içeriden; dip kalın. Sıvı için iç profil döner."""
    prof_out = np.asarray(prof_out, float)
    zs = sorted({bottom, *[z for z in prof_out[:, 1] if z > bottom]}
                | set(np.linspace(bottom, prof_out[-1, 1], 12)))
    rz = [(max(np.interp(z, prof_out[:, 1], prof_out[:, 0]) - t, 0.0005), z) for z in zs]
    inner = rz[::-1] + [(0, bottom)]
    prof = [(0, 0)] + [tuple(p) for p in prof_out] + [(prof_out[-1][0] - t * 0.5, prof_out[-1][1] + 0.001)] + inner
    obj(name, revolve(prof, n), M("cam"), loc=loc)
    return [(r, z) for r, z in inner[::-1] if r > 0]


def liquid(inner, level, m, loc=(0, 0, 0), shrink=0.0004, name="sivi", meniscus=True):
    """Bardağın iç profilinden sıvı gövdesi; level: sıvının yüksekliği."""
    pts = [(r - shrink, z) for r, z in inner if z <= level]
    rl = np.interp(level, [z for _, z in inner], [r for r, _ in inner]) - shrink
    prof = [(0, pts[0][1])] + pts + [(rl, level)]
    if meniscus:
        prof.append((rl * 0.96, level - 0.0008))
    prof.append((0, level - 0.0008 if meniscus else level))
    obj(name, revolve(prof, 128), m, loc=loc)
    return rl


def leaf(L, W, curl=0.25, nu=16, nv=6, tip=0.8, seed=0, ruffle=0.0):
    """Yaprak: boyu L, eni W; ortası damar boyunca kıvrık."""
    us, vs = np.linspace(0, 1, nu + 1), np.linspace(-1, 1, nv + 1)
    V = []
    for u in us:
        w = W * (math.sin(math.pi * min(u * (1 + (1 - tip)), 1.0)) ** 0.75) / 2 + 1e-4
        for v in vs:
            z = curl * W * v * v + 0.15 * L * (u - 0.4) ** 2
            if ruffle:
                z += ruffle * W * math.sin(9 * u + 3 * v + seed) * abs(v)
            V.append((u * L - L * 0.15, v * w, z))
    F = [(i * (nv + 1) + j, i * (nv + 1) + j + 1, (i + 1) * (nv + 1) + j + 1, (i + 1) * (nv + 1) + j)
         for i in range(nu) for j in range(nv)]
    return np.array(V), F


def leaves(n, center, spread, L, W, m, seed, z, curl=0.25, tilt=12):
    g = np.random.default_rng(seed)
    for k in range(n):
        a = g.uniform(0, 360)
        p = np.asarray(center[:2]) + g.normal(0, spread, 2)
        obj(f"yaprak{seed}_{k}", leaf(L * g.uniform(0.8, 1.15), W * g.uniform(0.85, 1.1), curl, seed=k), m,
            loc=(p[0], p[1], z + g.uniform(0, 0.002)), rot=(g.uniform(-tilt, tilt), g.uniform(-tilt, tilt), a),
            solid=0.0004)


def blob(name, r, sz, m, loc, amp=0.25, freq=None, seed=0, nu=40, nv=20, rot=(0, 0, 0), sx=1.0, sy=1.0, subsurf=0):
    V, F = sphere(1.0, nu, nv)
    V = V * [r * sx, r * sy, r * sz]
    V = wobble(V, F, r * amp, freq or 2.5 / r, seed)
    return obj(name, (V, F), m, loc=loc, rot=rot, subsurf=subsurf)


def round_board(r=0.17, h=0.02, kind="zeytin", handle=True):
    col = {"zeytin": ((176, 138, 92), (132, 96, 58)), "ceviz": ((96, 62, 38), (138, 94, 58)),
           "mese": ((196, 154, 104), (220, 182, 134))}[kind]
    m = mat("tahta_yuvarlak", col[0], rough=0.5, var=(col[1], 0.5), var_scale=6, stretch=(1, 14, 1), bump=0.15,
            bump_scale=40)
    obj("tahta", revolve([(0, 0), (r, 0), (r + 0.002, 0.002), (r + 0.002, h - 0.002), (r, h), (0, h)], 160), m)
    if handle:
        obj("tahta_sap", prism([(r - 0.01, -0.022), (r + 0.09, -0.02), (r + 0.1, -0.012), (r + 0.1, 0.012),
                                (r + 0.09, 0.02), (r - 0.01, 0.022)], h), m, rot=(0, 0, 35), smooth=False,
            bevel=0.003)
    return h


# ---------------------------------------------------------------- yemekler

def pizza(kind="margherita", samples=48):
    setup("mermer" if kind != "diavola" else "arduvaz", samples, world=(236, 228, 216))
    z0 = round_board(0.175, 0.02)
    R = 0.145
    g = np.random.default_rng({"margherita": 1, "diavola": 2, "formaggi": 3, "tartufo": 4}[kind])
    crust = mat("kabuk", (226, 186, 128), rough=0.55, sss=0.15, sss_r=(1, 0.6, 0.3),
                ramp=[(0.36, (236, 200, 146)), (0.47, (212, 146, 78)), (0.55, (164, 92, 40)), (0.6, (64, 36, 20)),
                      (0.64, (36, 24, 18))], var_scale=26, bump=0.5, bump_scale=70)
    obj("taban", revolve([(0, z0), (R - 0.01, z0), (R - 0.01, z0 + 0.005), (0, z0 + 0.005)], 128), crust)
    prof = [(R - 0.016 + 0.017 * math.cos(t), z0 + 0.011 + 0.0125 * math.sin(t))
            for t in np.linspace(0, 2 * np.pi, 28, endpoint=False)]
    V, F = revolve(prof, 180, closed=True)
    V = wobble(V, F, 0.0035, 45, 11)
    obj("kenar", (V, F), crust, subsurf=1)
    zs = z0 + 0.0065
    if kind == "tartufo":
        sauce = mat("krema", (238, 226, 200), rough=0.3, sss=0.3, var=((222, 204, 168), 0.5), var_scale=30,
                    coat=0.3)
    else:
        sauce = mat("domates_sos", (150, 22, 12), rough=0.3, coat=0.35,
                    ramp=[(0.4, (128, 16, 10)), (0.6, (186, 44, 18))], var_scale=35, bump=0.25, bump_scale=120)
    V, F = disc(R - 0.024, 96, 16)
    V[:, 2] = zs + 0.0012 * Noise(70, 5)(V)
    obj("sos", (V, F), sauce, solid=0.002)
    cheese = mat("mozzarella", (247, 242, 228), rough=0.35, sss=0.45, sss_r=(1, 0.9, 0.7), coat=0.2,
                 ramp=[(0.45, (246, 241, 228)), (0.57, (232, 206, 150)), (0.63, (184, 134, 72))], var_scale=40,
                 bump=0.2, bump_scale=90)
    if kind in ("margherita", "diavola"):
        for k, (x, y) in enumerate(scatter_disc(8 if kind == "margherita" else 6, R - 0.05, 0.05, 3 + len(kind))):
            blob(f"peynir{k}", g.uniform(0.02, 0.028), 0.14, cheese, (x, y, zs + 0.0015), amp=0.45, seed=k,
                 sx=g.uniform(0.9, 1.3), freq=60, rot=(0, 0, g.uniform(0, 360)))
    if kind == "margherita":
        for k, (x, y) in enumerate(scatter_disc(5, R - 0.06, 0.06, 9)):
            obj(f"feslegen{k}", leaf(0.045, 0.028, 0.3, seed=k), M("feslegen"), loc=(x, y, zs + 0.0065),
                rot=(g.uniform(-8, 8), g.uniform(-8, 8), g.uniform(0, 360)), solid=0.0005)
        obj("yag", revolve([(0, 0), (0.002, 0), (0, 0.0005)], 8), M("cam"))
    if kind == "diavola":
        sal = mat("salam", (150, 28, 26), rough=0.3, coat=0.5,
                  ramp=[(0.0, (128, 22, 22)), (0.6, (164, 34, 30)), (0.66, (230, 196, 180)), (1.0, (236, 204, 190))],
                  var_scale=420)
        for k, (x, y) in enumerate(scatter_disc(13, R - 0.035, 0.044, 21)):
            V, F = disc(0.021, 40, 5)
            rr = np.hypot(V[:, 0], V[:, 1])
            V[:, 2] = 0.006 * (rr / 0.021) ** 2
            obj(f"salam{k}", (V, F), sal, loc=(x, y, zs + 0.0035), rot=(g.uniform(-6, 6), g.uniform(-6, 6), 0),
                solid=0.0018)
        chili = mat("aci_biber", (196, 40, 20), rough=0.3, coat=0.5)
        for k in range(40):
            a, rr = g.uniform(0, 2 * np.pi), (R - 0.03) * math.sqrt(g.uniform())
            obj(f"pul{k}", superquad(0.0016, 0.001, 0.0004), chili, loc=(rr * math.cos(a), rr * math.sin(a), zs + 0.008),
                rot=(0, 0, g.uniform(0, 360)))
        for k, (x, y) in enumerate(scatter_disc(4, R - 0.06, 0.07, 30)):
            obj(f"feslegen{k}", leaf(0.04, 0.024, 0.3, seed=k), M("feslegen"), loc=(x, y, zs + 0.01),
                rot=(g.uniform(-8, 8), g.uniform(-8, 8), g.uniform(0, 360)), solid=0.0005)
    if kind == "formaggi":
        blue = mat("gorgonzola", (236, 232, 214), rough=0.45, sss=0.3,
                   ramp=[(0.5, (238, 234, 216)), (0.62, (150, 160, 150)), (0.75, (92, 104, 100))], var_scale=200)
        yellow = mat("cheddar", (238, 196, 92), rough=0.3, sss=0.4, coat=0.3, var=((226, 168, 64), 0.5))
        for k, (x, y) in enumerate(scatter_disc(16, R - 0.035, 0.034, 41)):
            m = [cheese, blue, yellow][k % 3]
            blob(f"peynir{k}", g.uniform(0.017, 0.023), 0.22, m, (x, y, zs + 0.002), amp=0.35, seed=k)
        walnut = mat("ceviz_ici", (128, 82, 42), rough=0.5, bump=0.8, bump_scale=600, var=((162, 112, 62), 0.5))
        for k, (x, y) in enumerate(scatter_disc(9, R - 0.045, 0.04, 51)):
            blob(f"ceviz{k}", 0.008, 0.6, walnut, (x, y, zs + 0.006), amp=0.35, seed=k + 9)
        honey = mat("bal", (226, 150, 30), rough=0.05, trans=0.6, coat=1.0)
        pts = [(0.1 * math.cos(t) * (0.4 + 0.5 * u), 0.1 * math.sin(t * 1.3) * (0.4 + 0.5 * u), zs + 0.0075)
               for u, t in zip(np.linspace(0, 1, 80), np.linspace(0, 5 * np.pi, 80))]
        tube("bal", pts, 0.0014, honey)
    if kind == "tartufo":
        mush = mat("mantar", (196, 168, 134), rough=0.5, sss=0.2,
                   ramp=[(0.4, (206, 182, 150)), (0.7, (150, 116, 80))], var_scale=200, bump=0.2, bump_scale=300)
        shape = [(0.014 * math.cos(t), 0.006 + 0.011 * math.sin(t)) for t in np.linspace(0, np.pi, 16)]
        shape += [(-0.012, 0.006), (-0.0045, 0.005), (-0.004, -0.012), (0.004, -0.012), (0.0045, 0.005),
                  (0.012, 0.006)]
        for k, (x, y) in enumerate(scatter_disc(18, R - 0.03, 0.032, 61)):
            obj(f"mantar{k}", prism(shape[::-1], 0.003), mush, loc=(x, y, zs + 0.004),
                rot=(g.uniform(-8, 8), g.uniform(-8, 8), g.uniform(0, 360)), bevel=0.0008)
        truf = mat("truf", (54, 42, 34), rough=0.5, ramp=[(0.4, (46, 36, 30)), (0.55, (150, 132, 112)),
                                                           (0.6, (52, 40, 32))], var_scale=600)
        for k, (x, y) in enumerate(scatter_disc(10, R - 0.04, 0.04, 71)):
            V, F = disc(0.012, 24, 3)
            V = V * [1, 0.8, 1]
            V[:, 2] = 0.002 * (np.hypot(V[:, 0], V[:, 1]) / 0.012) ** 2
            obj(f"truf{k}", (V, F), truf, loc=(x, y, zs + 0.009), rot=(g.uniform(-15, 15), g.uniform(-15, 15),
                                                                      g.uniform(0, 360)), solid=0.0006)
        parm = mat("parmesan", (240, 224, 170), rough=0.6, sss=0.3, bump=0.3, bump_scale=300)
        for k in range(14):
            a, rr = g.uniform(0, 2 * np.pi), (R - 0.04) * math.sqrt(g.uniform())
            obj(f"parmesan{k}", superquad(0.009, 0.005, 0.0006, 0.4), parm,
                loc=(rr * math.cos(a), rr * math.sin(a), zs + 0.011), rot=(g.uniform(-15, 15), 0, g.uniform(0, 360)))
        for k, (x, y) in enumerate(scatter_disc(6, R - 0.06, 0.06, 81)):
            obj(f"roka{k}", leaf(0.04, 0.012, 0.2, ruffle=0.3, seed=k), M("maydanoz"), loc=(x, y, zs + 0.012),
                rot=(g.uniform(-8, 8), g.uniform(-8, 8), g.uniform(0, 360)), solid=0.0004)
    camera((0.03, 0.0, z0), 0.8, 62, azim=-18, lens=78, fstop=4.0)
    studio(key=(-125, 38), target=(0, 0, z0))
    render(f"pizza_{kind}")


def bun_top(x, y, z, r, h, m, seeds=True, seed=0, s=1.0):
    t = np.linspace(0, np.pi / 2, 18)
    prof = [(0, z), (r * 0.96, z), (r, z + 0.004 * s)] + [(r * math.cos(u), z + 0.004 * s + h * math.sin(u)) for u in t[1:]]
    prof[-1] = (0, prof[-1][1])
    V, F = revolve(prof, 96)
    V = wobble(V, F, 0.0012 * s, 30 / s, seed)
    obj(f"ust_ekmek{seed}", (V, F), m, loc=(x, y, 0))
    if seeds:
        g = np.random.default_rng(seed)
        sm = M("susam")
        for k in range(int(46)):
            u = g.uniform(0.25, 1.35)
            a = g.uniform(-2.0, 2.0)                     # yalnız kameraya bakan yarı
            rr, zz = r * math.cos(u * 0.85), z + 0.004 * s + h * math.sin(u * 0.85)
            nx, nz = math.cos(u * 0.85) * h, math.sin(u * 0.85) * r
            tilt = math.degrees(math.atan2(nx, nz))
            obj(f"susam{seed}_{k}", superquad(0.0021 * s, 0.0012 * s, 0.0006 * s, 0.6, 16, 8), sm,
                loc=(x + rr * math.sin(a), y - rr * math.cos(a), zz + 0.0004),
                rot=(tilt * math.cos(a), tilt * math.sin(a), g.uniform(0, 180)))


def patty(x, y, z, r, h, m, seed, lacy=0.0):
    prof = [(0, z), (r - 0.004, z), (r, z + h * 0.25), (r + 0.001, z + h * 0.5), (r, z + h * 0.75), (r - 0.004, z + h),
            (0, z + h)]
    V, F = revolve(prof, 96)
    rr = np.hypot(V[:, 0], V[:, 1])
    V = wobble(V, F, 0.0012 + lacy * (rr / r) ** 6, 60, seed)
    V = wobble(V, F, 0.0007, 300, seed + 99, octaves=2)
    obj(f"kofte{seed}", (V, F), m, loc=(x, y, 0), subsurf=1)
    return z + h


def cheese_slice(x, y, z, r, size, m, seed, droop=1.0):
    """Erimiş dilim peynir: köşeleri yuvarlak kare, köftenin kenarından aşağı sarkar."""
    g = np.random.default_rng(seed)
    V, F = disc(1.0, 96, 18)
    th = np.arctan2(V[:, 1], V[:, 0]) + math.radians(g.uniform(20, 70))
    rho = np.hypot(V[:, 0], V[:, 1])
    sq = (size / 2) / (np.abs(np.cos(th)) ** 5 + np.abs(np.sin(th)) ** 5) ** 0.2
    rr = rho * sq
    over = np.clip(rr - r * 0.95, 0, None)
    rr = rr - 0.35 * over
    V = np.c_[rr * np.cos(th), rr * np.sin(th), -droop * np.minimum(0.6 * over + 40 * over ** 2, 0.009)]
    V[:, 2] += 0.0005 * Noise(200, seed)(V)
    obj(f"peynir{seed}", (V, F), m, loc=(x, y, z + 0.0012), solid=0.0018, subsurf=1)
    return z + 0.002


def lettuce(x, y, z, r, m, seed):
    V, F = disc(r, 96, 14)
    th = np.arctan2(V[:, 1], V[:, 0])
    rho = np.hypot(V[:, 0], V[:, 1])
    k = np.clip((rho - r * 0.6) / (r * 0.4), 0, 1)
    V[:, 2] = 0.006 * np.sin(13 * th + 2 * np.sin(5 * th + seed)) * k ** 1.5 - 0.004 * k ** 2
    V[:, :2] *= (1 + 0.06 * np.sin(7 * th + seed))[:, None]
    obj(f"marul{seed}", (V, F), m, loc=(x, y, z + 0.002), solid=0.0012, subsurf=1)
    return z + 0.003


def burger_stack(x, y, z0, kind, s=1.0, seed=0):
    g = np.random.default_rng(seed)
    bun = mat("brioche", (196, 116, 46), rough=0.38, coat=0.22, sss=0.25, sss_r=(1, 0.6, 0.3),
              ramp=[(0.38, (214, 140, 62)), (0.52, (184, 102, 38)), (0.62, (150, 74, 24))], var_scale=10, bump=0.12,
              bump_scale=80)
    crumb = M("ekmek_ic")
    beef = mat("dana", (92, 54, 32), rough=0.45, coat=0.3,
               ramp=[(0.38, (122, 74, 42)), (0.5, (84, 48, 28)), (0.6, (46, 28, 18))], var_scale=160, bump=0.8,
               bump_scale=220)
    ched = mat("cheddar", (255, 168, 18), rough=0.22, sss=0.5, sss_r=(1, 0.6, 0.2), coat=0.4,
               var=((250, 150, 12), 0.4), var_scale=20)
    green = mat("marul", (102, 160, 52), rough=0.3, sss=0.4, sss_r=(0.4, 1, 0.2), coat=0.3,
                ramp=[(0.4, (124, 178, 64)), (0.6, (84, 140, 40))], var_scale=60, bump=0.4, bump_scale=90)
    R = 0.056 * s
    z = z0
    # alt ekmek
    prof = [(0, z), (R * 0.93, z), (R, z + 0.004 * s), (R * 1.01, z + 0.014 * s), (R * 0.98, z + 0.02 * s),
            (0, z + 0.02 * s)]
    V, F = revolve(prof, 96)
    obj(f"alt_ekmek{seed}", (wobble(V, F, 0.001 * s, 40 / s, seed + 1), F), bun, loc=(x, y, 0))
    obj(f"alt_ic{seed}", disc(R * 0.97, 64, 6), crumb, loc=(x, y, z + 0.0202 * s))
    z += 0.02 * s
    if kind in ("truffle", "veggie", "chick"):
        z = lettuce(x, y, z, R * 1.12, green, seed + 2)
    if kind == "smash":
        for k in range(2):
            z = patty(x, y, z, R * 1.08, 0.01 * s, beef, seed + 10 + k, lacy=0.003 * s)
            z = cheese_slice(x, y, z, R * 1.1, 0.112 * s, ched, seed + 20 + k)
        onion = mat("karamel_sogan", (150, 92, 40), rough=0.2, coat=0.6, sss=0.3)
        for k in range(14):
            a = g.uniform(0, 2 * np.pi)
            rr = g.uniform(0, R * 0.8)
            pts = [(x + rr * math.cos(a) + 0.012 * s * math.cos(a + t), y + rr * math.sin(a) + 0.012 * s * math.sin(a + t),
                    z + 0.0015 * s) for t in np.linspace(0, 2.4, 8)]
            tube(f"sogan{seed}_{k}", pts, 0.0012 * s, onion)
        z += 0.003 * s
        pick = mat("tursu", (110, 128, 40), rough=0.25, coat=0.6, sss=0.3,
                   ramp=[(0.4, (128, 146, 54)), (0.6, (92, 108, 30))], var_scale=300)
        for k in range(3):
            a = g.uniform(-1.2, 1.2)
            obj(f"tursu{seed}_{k}", revolve([(0, 0), (0.014 * s, 0), (0.014 * s, 0.002 * s), (0, 0.002 * s)], 40), pick,
                loc=(x + R * 0.55 * math.sin(a), y - R * 0.55 * math.cos(a), z - 0.001),
                rot=(g.uniform(-10, 10), g.uniform(-10, 10), 0))
    elif kind == "truffle":
        z = patty(x, y, z, R * 1.04, 0.018 * s, beef, seed + 10)
        grav = mat("gravyer", (242, 220, 150), rough=0.3, sss=0.5, coat=0.3, var=((232, 204, 128), 0.4))
        z = cheese_slice(x, y, z, R * 1.06, 0.108 * s, grav, seed + 20, droop=0.8)
        mush = mat("mantar_sote", (112, 72, 40), rough=0.2, coat=0.7, sss=0.2, var=((150, 104, 62), 0.5),
                   var_scale=150)
        for k, (px, py) in enumerate(scatter_disc(9, R * 0.75, 0.016 * s, seed + 5)):
            blob(f"mantar{seed}_{k}", 0.009 * s, 0.4, mush, (x + px, y + py, z + 0.003 * s), amp=0.3, seed=k)
        z += 0.007 * s
        mayo = mat("truf_mayo", (232, 222, 196), rough=0.15, sss=0.4, coat=0.6)
        for k in range(5):
            a = g.uniform(-1.4, 1.4)
            blob(f"mayo{seed}_{k}", 0.006 * s, 1.6, mayo, (x + R * 0.95 * math.sin(a), y - R * 0.95 * math.cos(a),
                                                          z - 0.006 * s), amp=0.2, seed=k + 3)
    elif kind == "chick":
        chick = mat("citir_tavuk", (200, 120, 40), rough=0.35, coat=0.6,
                    ramp=[(0.4, (222, 148, 56)), (0.55, (176, 96, 30)), (0.62, (140, 64, 20))], var_scale=90, bump=1.2,
                    bump_scale=350)
        V, F = superquad(R * 1.25, R * 1.05, 0.013 * s, 0.6, 64, 32)
        V = wobble(V, F, 0.004 * s, 60 / s, seed + 7)
        obj(f"tavuk{seed}", (V, F), chick, loc=(x, y, z + 0.012 * s), rot=(0, 0, g.uniform(0, 90)), subsurf=1)
        z += 0.024 * s
        hot = mat("aci_bal", (214, 70, 20), rough=0.05, coat=1.0, trans=0.4)
        for k in range(4):
            a0 = g.uniform(0, np.pi * 2)
            pts = [(x + 0.04 * s * math.cos(a0 + t), y + 0.03 * s * math.sin(a0 + 1.7 * t), z + 0.0005)
                   for t in np.linspace(0, 1.6, 20)]
            tube(f"aci_bal{seed}_{k}", pts, 0.0016 * s, hot)
        pick = mat("tursu", (110, 128, 40), rough=0.25, coat=0.6, sss=0.3)
        for k in range(3):
            a = g.uniform(-1.0, 1.0)
            obj(f"tursu{seed}_{k}", revolve([(0, 0), (0.015 * s, 0), (0.015 * s, 0.002 * s), (0, 0.002 * s)], 40), pick,
                loc=(x + R * 0.6 * math.sin(a), y - R * 0.6 * math.cos(a), z), rot=(g.uniform(-8, 8), g.uniform(-8, 8), 0))
        z += 0.002 * s
    elif kind == "veggie":
        nohut = mat("nohut_kofte", (150, 120, 60), rough=0.6, coat=0.2,
                    ramp=[(0.35, (176, 146, 80)), (0.5, (128, 98, 46)), (0.62, (96, 70, 30))], var_scale=200, bump=1.2,
                    bump_scale=300)
        z = patty(x, y, z, R * 1.0, 0.018 * s, nohut, seed + 10)
        avo = mat("avokado", (176, 196, 72), rough=0.3, coat=0.5, sss=0.4, sss_r=(0.6, 1, 0.3),
                  ramp=[(0.4, (196, 206, 92)), (0.6, (150, 176, 60))], var_scale=40)
        for k in range(5):
            a = -0.9 + k * 0.45
            obj(f"avokado{seed}_{k}", superquad(0.03 * s, 0.009 * s, 0.003 * s, 0.6), avo,
                loc=(x + R * 0.35 * math.sin(a), y - R * 0.35 * math.cos(a), z + 0.003 * s),
                rot=(0, 6, math.degrees(a) + 90))
        z += 0.006 * s
        onion = mat("mor_sogan", (160, 60, 120), rough=0.2, coat=0.6, sss=0.4)
        for k in range(3):
            a = g.uniform(-1.2, 1.2)
            prof = [(0.012 * s + 0.0015 * s * math.cos(t), 0.0015 * s * math.sin(t)) for t in np.linspace(0, 2 * np.pi, 10,
                                                                                                         endpoint=False)]
            obj(f"sogan{seed}_{k}", revolve(prof, 48, closed=True), onion,
                loc=(x + R * 0.5 * math.sin(a), y - R * 0.5 * math.cos(a), z), rot=(g.uniform(-10, 10), 0, 0),
                scale=(1, 1, 0.5))
    if kind in ("truffle", "veggie", "smash"):
        tom = mat("domates_dilim", (210, 44, 30), rough=0.2, coat=0.6, sss=0.4,
                  ramp=[(0.45, (220, 60, 36)), (0.6, (186, 30, 22))], var_scale=60)
        if kind != "smash":
            obj(f"domates{seed}", revolve([(0, 0), (R * 0.8, 0), (R * 0.82, 0.003 * s), (R * 0.8, 0.006 * s), (0, 0.006 * s)], 64),
                tom, loc=(x + 0.006 * s, y - 0.004 * s, z))
            z += 0.006 * s
    bun_top(x, y, z, R * 1.02, 0.036 * s, bun, seeds=kind != "truffle", seed=seed + 30, s=s)
    return z + 0.036 * s


def fries(cx, cy, z, n, seed, s=1.0):
    g = np.random.default_rng(seed)
    m = mat("patates", (232, 176, 72), rough=0.35, coat=0.3, sss=0.3,
            ramp=[(0.4, (240, 192, 90)), (0.55, (214, 150, 52)), (0.62, (176, 112, 36))], var_scale=60, bump=0.3,
            bump_scale=200)
    for k in range(n):
        L = g.uniform(0.045, 0.07) * s
        zz = z + 0.004 * s + 0.007 * s * (k / n) * 2
        obj(f"patates{seed}_{k}", superquad(L / 2, 0.0042 * s, 0.0042 * s, 0.35, 24, 12), m,
            loc=(cx + g.normal(0, 0.016) * s, cy + g.normal(0, 0.016) * s, zz),
            rot=(g.uniform(-12, 12), g.uniform(-15, 15), g.uniform(0, 180)))
    salt = M("tuz")
    for k in range(30):
        obj(f"tuz{seed}_{k}", superquad(0.0007, 0.0007, 0.0007, 0.3, 8, 4), salt,
            loc=(cx + g.normal(0, 0.02) * s, cy + g.normal(0, 0.02) * s, z + 0.012 * s + g.uniform(0, 0.006)))


def burger(kind="smash", samples=48):
    setup("arduvaz", samples, world=(40, 38, 36), wstr=0.15)
    backdrop((30, 30, 32), 0.55, var=(44, 42, 40))
    z0 = board(0.36, 0.24, 0.024, "ceviz", loc=(0.0, 0.03, 0), rot=4)
    top = burger_stack(0.0, 0.0, z0, kind, 1.0, seed={"smash": 1, "truffle": 2, "chick": 3, "veggie": 4}[kind])
    fries(0.105, 0.07, z0, 16, 5)
    paper = mat("kagit", (236, 228, 210), rough=0.8, bump=0.2, bump_scale=60)
    V, F = grid(0.14, 0.14, 24, 24)
    V[:, 2] = 0.003 * Noise(25, 3)(V) + 0.003
    obj("kagit", (V, F), paper, loc=(0.0, 0.0, z0 - 0.002), rot=(0, 0, 18))
    cz = (z0 + top) / 2
    camera((0.018, 0.0, cz), 0.52, 13, azim=-14, lens=88, fstop=3.2)
    light("ana", 40, 0.6, -110, 32, 0.8, (0, 0, cz), (255, 240, 222))
    light("dolgu", 8, 1.2, 40, 18, 1.0, (0, 0, cz), (226, 236, 255))
    light("arka", 22, 0.35, 165, 30, 0.7, (0, 0, cz), (255, 226, 190))
    render(f"burger_{kind}")


def slider(samples=48):
    setup("siyah_mermer", samples, world=(22, 20, 20), wstr=0.08)
    backdrop((14, 14, 16), 1.8)
    bokeh(24, 0.22, 0.8, 1.3, [(255, 196, 120), (255, 170, 90), (220, 180, 255)], seed=4, power=18, size=0.016)
    glow((255, 176, 110), 0.8, y=0.4, w=0.4, h=0.12, z=0.0)
    z0 = board(0.32, 0.12, 0.02, "arduvaz", loc=(0, 0.0, 0), rot=-6)
    tops = [burger_stack(x, 0.0, z0, "truffle", 0.58, seed=10 + k) for k, x in enumerate((-0.09, 0.0, 0.09))]
    cz = (z0 + max(tops)) / 2
    camera((0.0, 0.0, cz), 0.62, 14, azim=-10, lens=78, fstop=2.8)
    light("ana", 18, 0.5, -120, 32, 0.8, (0, 0, cz), (255, 232, 204))
    light("dolgu", 3, 1.0, 50, 18, 1.0, (0, 0, cz), (210, 220, 255))
    light("arka", 26, 0.3, 170, 32, 0.7, (0, 0, cz), (255, 210, 160))
    render("slider")


def beans(n, cx, cy, z, spread, seed):
    g = np.random.default_rng(seed)
    m = mat("kahve_cekirdegi", (70, 40, 24), rough=0.25, coat=0.6, var=((96, 58, 34), 0.5), var_scale=200)
    for k in range(n):
        V, F = superquad(0.0062, 0.0045, 0.003, 0.7, 24, 12)
        V[:, 2] -= 0.0012 * np.exp(-(V[:, 1] / 0.0007) ** 2) * (V[:, 2] > 0)
        obj(f"cekirdek{seed}_{k}", (V, F), m, loc=(cx + g.normal(0, spread), cy + g.normal(0, spread), z + 0.003),
            rot=(g.uniform(-20, 20), g.uniform(-20, 20), g.uniform(0, 360)))


def spoon(x, y, z, rot, s=1.0, mat_key="metal"):
    V, F = superquad(0.012 * s, 0.008 * s, 0.003 * s, 0.9, 32, 16)
    V[:, 2] = np.where(V[:, 2] > 0, V[:, 2] * 0.3, V[:, 2])
    a = math.radians(rot)
    obj("kasik", (V, F), M(mat_key), loc=(x, y, z + 0.003), rot=(0, 0, rot))
    pts = [(x + (0.012 + t) * s * math.cos(a), y + (0.012 + t) * s * math.sin(a), z + 0.003 + 0.12 * t * s)
           for t in np.linspace(0, 0.07, 12)]
    tube("kasik_sap", pts, 0.0016 * s, M(mat_key))


def coffee(kind="flatwhite", samples=48):
    surf = {"flatwhite": "mese", "espresso": "arduvaz", "turk": "ceviz", "fistik": "mermer"}[kind]
    setup(surf, samples, world=(236, 226, 210), wstr=0.15)
    backdrop((196, 180, 160) if surf != "arduvaz" else (40, 40, 42), 0.6)
    if kind == "flatwhite":
        zs = saucer(0.08)
        f = cup(0.04, 0.058, z=zs, rot=-30)
        zl, rl = f(0.9)
        obj("latte", disc(rl, 96, 12), mat_tex("latte_sanat", tex_latte("kalp", kind="kalp"), rough=0.35, sss=0.2,
                                               size=2 * rl), loc=(0, 0, zl))
        spoon(0.03, -0.055, zs, -20)
        beans(14, -0.12, 0.05, 0, 0.03, 3)
        camera((0.0, 0.0, 0.05), 0.55, 48, azim=-18, lens=85, fstop=3.2)
    elif kind == "espresso":
        zs = saucer(0.06)
        f = cup(0.028, 0.045, z=zs, rot=-30, t=0.0035)
        zl, rl = f(0.8)
        crema = mat("krema_espresso", (176, 104, 50), rough=0.3, coat=0.4,
                    ramp=[(0.38, (196, 128, 66)), (0.5, (160, 88, 40)), (0.6, (112, 58, 26))], var_scale=180,
                    bump=0.2, bump_scale=300)
        obj("crema", disc(rl, 64, 8), crema, loc=(0, 0, zl))
        spoon(0.026, -0.04, zs, -20, 0.75)
        beans(18, -0.09, 0.04, 0, 0.03, 4)
        camera((0.0, 0.0, 0.04), 0.45, 40, azim=-18, lens=90, fstop=3.2)
    elif kind == "turk":
        zs = saucer(0.065, mat_key="porselen")
        f = cup(0.03, 0.05, z=zs, rot=-30, t=0.0032, flare=1.04)
        zl, rl = f(0.9)
        foam = mat("kopuk_turk", (170, 120, 76), rough=0.5, ramp=[(0.4, (186, 140, 92)), (0.6, (140, 92, 54))],
                   var_scale=60, bump=0.6, bump_scale=900, voronoi=1)
        obj("kopuk", disc(rl, 64, 8), foam, loc=(0, 0, zl))
        lokum = mat("lokum", (232, 150, 170), rough=0.85, sss=0.4, sheen=0.8, var=((246, 214, 222), 0.5),
                    var_scale=300)
        for k, (dx, dy, rz) in enumerate(((0.045, -0.02, 10), (0.052, 0.008, 40))):
            obj(f"lokum{k}", superquad(0.0085, 0.0085, 0.0085, 0.35), lokum, loc=(dx, dy, zs + 0.006), rot=(0, 0, rz))
        gin = glass([(0.025, 0.0), (0.026, 0.004), (0.027, 0.09)], t=0.0018, bottom=0.008, loc=(-0.085, 0.05, 0))
        liquid(gin, 0.07, mat("su", (250, 252, 255), rough=0.0, trans=1.0, ior=1.33), loc=(-0.085, 0.05, 0))
        camera((0.0, 0.0, 0.04), 0.5, 32, azim=-14, lens=85, fstop=3.2)
    elif kind == "fistik":
        prof = [(0.036, 0.0), (0.038, 0.004), (0.04, 0.11)]
        inner = glass(prof, t=0.0026, bottom=0.012, name="latte_bardak")
        lat = mat_zgrad("katmanli_latte", [(0.0, (150, 172, 90)), (0.30, (176, 190, 110)), (0.36, (238, 228, 206)),
                                           (0.62, (204, 160, 110)), (0.70, (150, 96, 54)), (0.86, (236, 224, 204)),
                                           (1.0, (248, 244, 236))], 0.012, 0.1, trans=0.0, rough=0.3, sss=0.4)
        rl = liquid(inner, 0.1, lat)
        nut = mat("fistik", (120, 150, 56), rough=0.4, var=((176, 170, 80), 0.5), var_scale=400, bump=0.4,
                  bump_scale=500)
        for k, (dx, dy) in enumerate(scatter_disc(22, rl * 0.85, 0.004, 7)):
            obj(f"fistik{k}", superquad(0.0022, 0.0016, 0.0012, 0.6, 12, 6), nut, loc=(dx, dy, 0.1 + 0.0008),
                rot=(20 * k, 0, 37 * k))
        pist = mat("fistik_butun", (150, 168, 70), rough=0.4, sss=0.3, var=((190, 150, 110), 0.5))
        for k, (dx, dy) in enumerate(((0.07, -0.03), (0.08, 0.0), (0.06, 0.02), (0.09, -0.02))):
            blob(f"butun{k}", 0.006, 0.5, pist, (dx, dy, 0.003), amp=0.1, seed=k, sx=1.4)
        camera((0.0, 0.0, 0.06), 0.55, 18, azim=-12, lens=85, fstop=3.2)
    studio(key=(-115, 38), target=(0, 0, 0.04), power=26)
    render(f"kahve_{kind}")


def cheesecake(samples=48):
    setup("mese", samples, world=(236, 226, 210), wstr=0.15)
    backdrop((200, 186, 168), 0.6)
    zp = plate(0.11, "seramik_tas", depth=0.01)
    R, h, ang = 0.09, 0.05, math.radians(42)
    pts = [(0, 0)] + [(R * math.cos(t), R * math.sin(t)) for t in np.linspace(-ang / 2, ang / 2, 18)]
    V, F = prism(pts, h, -h / 2)
    m = mat_cut("san_sebastian", (246, 222, 170), (214, 160, 92), (64, 34, 18), (None, None, h / 2), edge=(0.8, 0.92),
                rough=0.35, bump=0.6, radial=R * 1.0)
    c = 0.6 * R
    obj("pasta", (V, F), m, loc=(-c * math.cos(math.radians(200)), -c * math.sin(math.radians(200)), zp + h / 2),
        rot=(0, 0, 200), smooth=False, bevel=0.004)
    sauce = mat("bogurtlen", (90, 16, 40), rough=0.05, coat=1.0, sss=0.2)
    pts = [(0.03 + 0.05 * t, -0.05 + 0.02 * math.sin(t * 9), zp + 0.0015) for t in np.linspace(0, 1, 30)]
    tube("sos", pts, 0.003, sauce)
    berry = mat("bogurtlen_tane", (60, 10, 40), rough=0.15, coat=0.8, bump=0.6, bump_scale=900, voronoi=1)
    for k, (dx, dy) in enumerate(((0.05, -0.035), (0.062, -0.022), (0.04, -0.05))):
        blob(f"meyve{k}", 0.0075, 0.9, berry, (dx, dy, zp + 0.007), amp=0.1, seed=k)
    leaves(2, (0.055, -0.03), 0.005, 0.02, 0.011, M("nane"), 3, zp + 0.012)
    camera((0.0, 0.0, 0.035), 0.5, 26, azim=-20, lens=85, fstop=3.2)
    studio(key=(-115, 36), target=(0, 0, 0.03), power=26)
    render("kahve_cheesecake")


# ---- suşi ve ramen

def rice_mat():
    return mat("pirinc", (246, 244, 236), rough=0.45, sss=0.4, sss_r=(1, 1, 0.9), bump=0.9, bump_scale=700,
               voronoi=1, stretch=(1, 2.2, 1), var=((232, 230, 220), 0.5), var_scale=600)


def nigiri(x, y, z, fish, rot, seed, s=1.0):
    V, F = superquad(0.024 * s, 0.0115 * s, 0.009 * s, 0.55, 40, 20)
    V = wobble(V, F, 0.0008 * s, 300, seed)
    obj(f"pilav{seed}", (V, F), rice_mat(), loc=(x, y, z + 0.009 * s), rot=(0, 0, rot))
    V, F = superquad(0.029 * s, 0.0135 * s, 0.0028 * s, 0.45, 48, 16)
    V[:, 2] += 0.0205 * s - 22 * V[:, 0] ** 2 / s - 20 * V[:, 1] ** 2 / s
    obj(f"balik{seed}", (V, F), fish, loc=(x, y, z), rot=(0, 0, rot), subsurf=1)


def maki(x, y, z, fill, top, seed, s=1.0):
    nori = mat("nori", (24, 32, 24), rough=0.6, bump=0.4, bump_scale=300, var=((40, 48, 34), 0.5), var_scale=200)
    h = 0.02 * s
    obj(f"nori{seed}", revolve([(0.0148 * s, 0), (0.0148 * s, h)], 64), nori, loc=(x, y, z), solid=0.0007 * s)
    obj(f"pilav{seed}", revolve([(0, 0), (0.0142 * s, 0), (0.0142 * s, h), (0, h + 0.001 * s)], 64), rice_mat(),
        loc=(x, y, z))
    obj(f"ic{seed}", revolve([(0, 0), (0.0062 * s, 0), (0.0062 * s, h + 0.0012 * s), (0, h + 0.0012 * s)], 32), fill,
        loc=(x, y, z))
    if top is not None:
        blob(f"ust{seed}", 0.0065 * s, 0.45, top, (x, y, z + h + 0.0018 * s), amp=0.15, seed=seed)


def sushi(kind="nigiri", samples=48):
    setup("arduvaz", samples, world=(40, 40, 42), wstr=0.12)
    backdrop((26, 26, 28), 0.6)
    g = np.random.default_rng(5)
    zb = board(0.3, 0.12, 0.012, "arduvaz", loc=(0, 0, 0), rot=-8)
    salmon = mat_stripes("somon", (242, 112, 58), (252, 214, 190), 160, rough=0.2, coat=0.7, sss=0.5,
                         direction=(1, 0.7, 0), width=0.22)
    tuna = mat("ton", (176, 30, 44), rough=0.2, coat=0.7, sss=0.5, sss_r=(1, 0.3, 0.3), var=((150, 22, 36), 0.5),
               var_scale=80)
    if kind == "nigiri":
        for k, x in enumerate((-0.05, 0.0, 0.05)):
            nigiri(x, 0.0, zb, salmon, -8 + 4 * k, k)
    elif kind == "spicy":
        mayo = M("turuncu_sos")
        for k in range(6):
            maki(-0.075 + 0.03 * k, 0.004 * (k % 2), zb, tuna, mayo, k)
        chili = mat("aci_pul", (200, 40, 20), rough=0.3)
        for k in range(18):
            obj(f"pul{k}", superquad(0.0012, 0.0008, 0.0004), chili, loc=(-0.075 + 0.15 * g.uniform(), g.normal(0, 0.004),
                                                                       zb + 0.025), rot=(0, 0, g.uniform(0, 180)))
    elif kind == "dragon":
        shrimp = mat("tempura", (232, 160, 70), rough=0.4, bump=0.8, bump_scale=300)
        avo = mat("avokado", (170, 196, 76), rough=0.25, coat=0.6, sss=0.4, sss_r=(0.6, 1, 0.3),
                  ramp=[(0.35, (196, 210, 96)), (0.62, (120, 160, 50)), (0.7, (56, 80, 30))], var_scale=30)
        for k in range(6):
            x = -0.08 + 0.032 * k
            maki(x, 0.0, zb, shrimp, None, k + 10, s=1.08)
            V, F = superquad(0.017, 0.0105, 0.0025, 0.5, 32, 12)
            V[:, 2] += -60 * V[:, 0] ** 2
            obj(f"avo{k}", (V, F), avo, loc=(x, 0.0, zb + 0.0245), rot=(0, 0, 70))
        pts = [(-0.09 + 0.18 * t, 0.009 * math.sin(t * 40), zb + 0.03) for t in np.linspace(0, 1, 120)]
        tube("unagi", pts, 0.0011, M("sos_kahve"))
        tob = mat("tobiko", (246, 110, 30), rough=0.1, coat=1.0, sss=0.5, bump=0.8, bump_scale=2500, voronoi=1)
        for k in range(6):
            blob(f"tobiko{k}", 0.004, 0.5, tob, (-0.08 + 0.032 * k, -0.003, zb + 0.03), amp=0.2, seed=k)
    if kind in ("nigiri", "spicy"):
        wasabi = mat("wasabi", (150, 176, 60), rough=0.5, bump=0.4, bump_scale=300)
        blob("wasabi", 0.008, 0.7, wasabi, (0.105, 0.025, zb + 0.005), amp=0.3, seed=2)
        ging = mat("zencefil", (240, 186, 170), rough=0.25, sss=0.6, trans=0.2, coat=0.4)
        for k in range(4):
            V, F = disc(0.013, 32, 4)
            V[:, 2] = 0.003 * (V[:, 0] / 0.013) ** 2
            obj(f"zencefil{k}", (V, F), ging, loc=(0.1 + 0.004 * k, -0.025 + 0.002 * k, zb + 0.004 + 0.0015 * k),
                rot=(15, 10 * k, 30 * k), solid=0.0008)
    obj("cubuk1", superquad(0.11, 0.0028, 0.0028, 0.6, 24, 8), M("dal"), loc=(0.0, 0.085, 0.003), rot=(0, 0, 4))
    obj("cubuk2", superquad(0.11, 0.0028, 0.0028, 0.6, 24, 8), M("dal"), loc=(0.004, 0.096, 0.003), rot=(0, 0, 2))
    camera((0.0, 0.0, 0.02), 0.5, 30, azim=-14, lens=85, fstop=3.2)
    studio(key=(-115, 36), target=(0, 0, 0.02), power=26)
    render(f"susi_{kind}")


def ramen(samples=48):
    setup("arduvaz", samples, world=(40, 40, 42), wstr=0.12)
    g = np.random.default_rng(8)
    fill = bowl(0.1, 0.07, "seramik_siyah")
    zl, rl = fill(0.8)
    broth = mat("tonkotsu", (214, 172, 112), rough=0.12, coat=0.8, sss=0.6, sss_r=(1, 0.8, 0.5),
                var=((196, 148, 88), 0.5), var_scale=30)
    obj("et_suyu", disc(rl, 96, 12), broth, loc=(0, 0, zl))
    noodle = mat("eriste", (240, 214, 150), rough=0.3, sss=0.4, coat=0.4)
    for k in range(26):
        y0 = -0.03 + 0.06 * (k / 26)
        pts = [(-0.06 + 0.12 * t, y0 + 0.006 * math.sin(t * 18 + k), zl + 0.0012 + 0.0008 * math.sin(t * 7 + k))
               for t in np.linspace(0, 1, 40)]
        pts = [p for p in pts if p[0] ** 2 + p[1] ** 2 < (rl - 0.012) ** 2 and p[0] > -0.005]
        if len(pts) > 2:
            tube(f"eriste{k}", pts, 0.0016, noodle)
    chashu = mat_cut("chashu", (236, 196, 176), (200, 140, 110), (120, 62, 36), (None, None, None), edge=(0.75, 0.9),
                     rough=0.25, coat=0.6, radial=0.032)
    for k, (dx, dy, a) in enumerate(((-0.035, 0.025, 20), (-0.045, -0.01, -30))):
        obj(f"chashu{k}", revolve([(0, 0), (0.032, 0), (0.032, 0.006), (0, 0.006)], 64), chashu,
            loc=(dx, dy, zl - 0.001), rot=(8, -10, a))
    white = mat("yumurta_ak", (250, 248, 240), rough=0.15, sss=0.5, coat=0.5)
    yolk = mat("yumurta_sarisi", (244, 140, 24), rough=0.1, sss=0.6, coat=0.8)
    for k, (dx, dy) in enumerate(((0.035, -0.035), (0.05, -0.008))):
        V, F = sphere(1, 40, 20)
        V = V[:, :] * [0.022, 0.016, 0.016]
        V[:, 2] = np.minimum(V[:, 2], 0)
        obj(f"yumurta{k}", (V, F), white, loc=(dx, dy, zl + 0.004), rot=(0, 0, 30 + 40 * k))
        obj(f"sari{k}", disc(0.009, 32, 4), yolk, loc=(dx, dy, zl + 0.0042), rot=(0, 0, 30 + 40 * k),
            scale=(1.1, 0.9, 1))
    green = mat("yesil_sogan", (96, 160, 56), rough=0.3, sss=0.3, coat=0.4)
    for k in range(26):
        p = g.normal(0, 0.016, 2) + [0.01, 0.025]
        prof = [(0.0032 + 0.0008 * math.cos(t), 0.0008 * math.sin(t)) for t in np.linspace(0, 2 * np.pi, 8,
                                                                                          endpoint=False)]
        obj(f"sogan{k}", revolve(prof, 16, closed=True), green, loc=(p[0], p[1], zl + 0.002),
            rot=(g.uniform(-30, 30), g.uniform(-30, 30), 0))
    nori = mat("nori", (24, 32, 24), rough=0.6, bump=0.4, bump_scale=300)
    obj("nori", prism([(-0.025, -0.0006), (0.025, -0.0006), (0.025, 0.0006), (-0.025, 0.0006)], 0.06), nori,
        loc=(0.0, 0.07, zl - 0.02), rot=(-16, 0, 0), smooth=False)
    menma = mat("menma", (196, 160, 90), rough=0.4, coat=0.4, stretch=(1, 8, 1), var=((170, 130, 60), 0.5))
    for k in range(5):
        obj(f"menma{k}", superquad(0.012, 0.003, 0.002, 0.4), menma, loc=(0.02 + 0.006 * k, 0.04 - 0.003 * k, zl + 0.002),
            rot=(0, 0, 60 + 8 * k))
    sesame = M("susam")
    for k in range(40):
        p = g.normal(0, 0.03, 2)
        if np.hypot(*p) < rl - 0.01:
            obj(f"susam{k}", superquad(0.0011, 0.0007, 0.0003, 0.6, 8, 4), sesame, loc=(p[0], p[1], zl + 0.0025),
                rot=(0, 0, g.uniform(0, 180)))
    obj("cubuk1", superquad(0.11, 0.0028, 0.0028, 0.6, 24, 8), M("dal"), loc=(0.09, -0.06, 0.003), rot=(0, 0, 70))
    camera((0.0, 0.0, 0.04), 0.62, 56, azim=-10, lens=80, fstop=4.0)
    studio(key=(-115, 40), target=(0, 0, 0.04), power=26)
    render("susi_ramen")


# ---- et

def rosemary(x, y, z, rot, seed, L=0.09):
    g = np.random.default_rng(seed)
    a = math.radians(rot)
    d = np.array([math.cos(a), math.sin(a)])
    nrm = np.array([-d[1], d[0]])
    pts = [(x + d[0] * t, y + d[1] * t, z + 0.002 + 0.01 * (t / L) ** 2) for t in np.linspace(0, L, 10)]
    tube(f"biberiye_sap{seed}", pts, 0.0011, M("dal"))
    for k in range(34):
        t = g.uniform(0.08, 1.0) * L
        side = 1 if k % 2 else -1
        base = np.array([x, y]) + d * t
        obj(f"biberiye{seed}_{k}", superquad(0.0075, 0.0012, 0.0006, 0.7, 12, 6), M("biberiye"),
            loc=(base[0] + nrm[0] * side * 0.005, base[1] + nrm[1] * side * 0.005, z + 0.003 + 0.01 * (t / L) ** 2),
            rot=(g.uniform(-20, 20), g.uniform(-10, 10), rot + side * g.uniform(35, 70)))


def coarse_salt(cx, cy, z, n, spread, seed):
    g = np.random.default_rng(seed)
    for k in range(n):
        obj(f"tuz{seed}_{k}", superquad(0.0012, 0.001, 0.0009, 0.3, 8, 4), M("tuz"),
            loc=(cx + g.normal(0, spread), cy + g.normal(0, spread), z + 0.001),
            rot=(g.uniform(0, 90), g.uniform(0, 90), g.uniform(0, 90)))


def ramekin(x, y, z, r, sauce, name="ramekin"):
    f = bowl(r, r * 0.8, "seramik_tas", z=z, t=0.004, foot=0.85, name=name)
    zl, rl = f(0.85)
    obj(name + "_sos", disc(rl, 48, 6), sauce, loc=(x, y, zl))
    ob = bpy.data.objects[name]
    ob.location = (x, y, 0)


def steak(kind="antrikot", samples=48):
    setup("ceviz", samples, world=(30, 26, 22), wstr=0.1)
    backdrop((22, 18, 16), 0.55)
    g = np.random.default_rng(11)
    zb = board(0.34, 0.22, 0.03, "zeytin", loc=(0, 0, 0), rot=-6, handle=True)
    crust = mat("kabuk_et", (70, 38, 22), rough=0.35, coat=0.5,
                ramp=[(0.38, (98, 56, 30)), (0.5, (60, 32, 18)), (0.6, (30, 18, 12))], var_scale=120, bump=1.0,
                bump_scale=250)
    if kind == "antrikot":
        m = mat_cut("antrikot", (196, 70, 74), (150, 90, 70), (64, 34, 20), (None, 0.034, 0.014), edge=(0.8, 0.9),
                    rough=0.3, coat=0.5, bump=0.5, sss=0.2)
        for k in range(8):
            V, F = superquad(0.006, 0.034, 0.014, 0.35, 32, 16)
            obj(f"dilim{k}", (V, F), m, loc=(-0.075 + 0.019 * k, 0.003 * math.sin(k), zb + 0.0125),
                rot=(0, -58 - 3 * (k % 3), 8))
        rosemary(0.04, 0.06, zb, -150, 1)
        coarse_salt(0.0, 0.0, zb + 0.028, 40, 0.03, 2)
        ramekin(0.11, 0.06, zb, 0.032, mat("chimichurri", (70, 100, 30), rough=0.2, coat=0.8,
                                            var=((140, 40, 20), 0.3), var_scale=400, bump=0.5, bump_scale=400))
    elif kind == "pirzola":
        lamb = mat_stripes("pirzola", (150, 90, 52), (58, 32, 18), 70, rough=0.35, coat=0.5, direction=(1, 1, 0),
                           width=0.25)
        bone = mat("kemik", (236, 222, 196), rough=0.35, sss=0.3, var=((214, 188, 150), 0.5))
        for k in range(3):
            a = 70 + 22 * k
            ar = math.radians(a)
            cx, cy = -0.04 + 0.04 * k, -0.02 + 0.006 * k
            V, F = superquad(0.03, 0.023, 0.011, 0.6, 40, 20)
            V = wobble(V, F, 0.0015, 120, k)
            obj(f"pirzola{k}", (V, F), lamb, loc=(cx, cy, zb + 0.011 + 0.006 * k), rot=(0, 0, a))
            pts = [(cx + math.cos(ar) * t, cy + math.sin(ar) * t, zb + 0.012 + 0.006 * k + 0.15 * (t - 0.02) * (t > 0.02))
                   for t in np.linspace(0.02, 0.085, 8)]
            tube(f"kemik{k}", pts, 0.0042, bone)
        rosemary(-0.1, -0.06, zb, 20, 3)
        obj("limon", sphere(1, 32, 16), M("limon"), loc=(0.1, -0.05, zb + 0.012), scale=(0.03, 0.022, 0.012))
        coarse_salt(0.0, 0.0, zb + 0.028, 40, 0.04, 4)
    elif kind == "kofte":
        kof = mat_stripes("izgara_kofte", (138, 82, 48), (60, 34, 20), 90, rough=0.35, coat=0.45, direction=(1, 0, 0),
                          width=0.22)
        for k in range(6):
            V, F = superquad(0.028, 0.012, 0.0095, 0.75, 40, 20)
            V = wobble(V, F, 0.0012, 150, k)
            obj(f"kofte{k}", (V, F), kof, loc=(-0.08 + 0.032 * k, 0.012 * (k % 2) - 0.006, zb + 0.009),
                rot=(0, 0, 90 + g.uniform(-8, 8)))
        for k in range(2):
            pts = [(-0.06 + 0.13 * t, 0.055 + 0.01 * k + 0.01 * math.sin(t * 3), zb + 0.008) for t in np.linspace(0, 1, 16)]
            ob = tube(f"biber{k}", pts, 0.008, M("biber_yesil"))
        tom = mat("kozlenmis_domates", (176, 40, 24), rough=0.2, coat=0.8, ramp=[(0.4, (196, 52, 30)),
                                                                                 (0.62, (60, 24, 16))], var_scale=60)
        for k in range(2):
            blob(f"domates{k}", 0.02, 0.7, tom, (0.09 + 0.03 * k, -0.05, zb + 0.012), amp=0.08, seed=k)
        leaves(10, (-0.05, -0.06), 0.015, 0.018, 0.012, M("maydanoz"), 5, zb + 0.004)
    elif kind == "adana":
        lav = mat("lavas", (232, 206, 160), rough=0.7, ramp=[(0.45, (236, 214, 170)), (0.58, (200, 150, 90)),
                                                              (0.64, (120, 76, 40))], var_scale=40, bump=0.3,
                  bump_scale=60)
        V, F = superquad(0.15, 0.08, 0.002, 0.3, 64, 8)
        V[:, 2] += 0.004 * Noise(30, 3)(V)
        obj("lavas", (V, F), lav, loc=(0, 0, zb + 0.002), rot=(0, 0, -4))
        keb = mat_stripes("adana", (156, 74, 40), (66, 30, 16), 60, rough=0.35, coat=0.5, direction=(1, 0.3, 0),
                          width=0.2)
        for k in range(2):
            V, F = superquad(0.11, 0.0135, 0.0115, 0.8, 80, 20)
            V[:, 1:] *= (1 + 0.12 * np.sin(V[:, 0] * 260))[:, None]
            V = wobble(V, F, 0.001, 200, k)
            obj(f"kebap{k}", (V, F), keb, loc=(0.0, -0.022 + 0.04 * k, zb + 0.016), rot=(0, 0, -4))
        onion = mat("sumakli_sogan", (200, 120, 150), rough=0.3, coat=0.5, sss=0.5, var=((150, 40, 60), 0.5),
                    var_scale=500)
        for k in range(12):
            p = g.normal(0, 0.015, 2) + [0.1, -0.06]
            prof = [(0.009 + 0.0012 * math.cos(t), 0.0012 * math.sin(t)) for t in np.linspace(0, 2 * np.pi, 8,
                                                                                            endpoint=False)]
            obj(f"sogan{k}", revolve(prof, 24, closed=True), onion, loc=(p[0], p[1], zb + 0.005),
                rot=(g.uniform(-30, 30), g.uniform(-30, 30), 0), scale=(1.3, 0.7, 1))
        leaves(9, (0.1, -0.06), 0.015, 0.016, 0.011, M("maydanoz"), 6, zb + 0.008)
        pts = [(-0.11 + 0.2 * t, 0.07 + 0.006 * math.sin(t * 3), zb + 0.008) for t in np.linspace(0, 1, 16)]
        tube("biber", pts, 0.007, M("biber_yesil"))
    camera((0.0, 0.0, zb + 0.01), 0.62, 34, azim=-14, lens=78, fstop=3.5)
    light("ana", 36, 0.6, -120, 36, 0.8, (0, 0, zb), (255, 236, 214))
    light("dolgu", 6, 1.2, 50, 22, 1.0, (0, 0, zb), (220, 230, 255))
    light("arka", 22, 0.3, 170, 28, 0.7, (0, 0, zb), (255, 220, 180))
    render(f"et_{kind}")


# ---- içecek

GLASS = {
    "rocks": [(0.038, 0.0), (0.04, 0.003), (0.041, 0.012), (0.043, 0.088)],
    "highball": [(0.027, 0.0), (0.029, 0.003), (0.03, 0.01), (0.031, 0.15)],
    "wine": [(0.036, 0.0), (0.036, 0.003), (0.006, 0.006), (0.0036, 0.012), (0.0036, 0.085), (0.012, 0.092),
             (0.03, 0.105), (0.044, 0.13), (0.047, 0.15), (0.044, 0.175), (0.039, 0.2)],
    "hurricane": [(0.03, 0.0), (0.03, 0.003), (0.006, 0.008), (0.005, 0.03), (0.02, 0.045), (0.035, 0.08),
                  (0.03, 0.12), (0.036, 0.16), (0.042, 0.19)],
    "tulip": [(0.022, 0.0), (0.0225, 0.003), (0.0205, 0.02), (0.0175, 0.042), (0.019, 0.06), (0.024, 0.085),
              (0.0265, 0.1)],
}
BOTTOM = {"rocks": 0.012, "highball": 0.01, "wine": 0.094, "hurricane": 0.04, "tulip": 0.006}


def ice_cube(name, x, y, z, a, rot, seed):
    V, F = superquad(a, a, a, 0.32, 24, 12)
    V = wobble(V, F, a * 0.03, 3 / a, seed)
    obj(name, (V, F), M("buz"), loc=(x, y, z), rot=rot)


def citrus_slice(name, x, y, z, r, rot, kind="portakal", th=0.004):
    col = {"portakal": ((232, 110, 20), (250, 236, 200), (246, 140, 40)),
           "limon": ((236, 200, 40), (250, 244, 214), (246, 224, 90)),
           "lime": ((90, 150, 40), (226, 240, 196), (170, 206, 80))}[kind]
    tex = tex_citrus(kind, *col)
    face = mat_tex(name + "_yuz", tex, rough=0.25, coat=0.6, sss=0.3, size=2 * r)
    obj(name, revolve([(0, -th / 2), (r, -th / 2), (r, th / 2), (0, th / 2)], 64), face, loc=(x, y, z), rot=rot)


def cocktail(kind="negroni", samples=64):
    night = kind in ("negroni", "oldfashioned", "gunbatimi")
    if night:
        setup("siyah_mermer", samples, world=(20, 18, 18), wstr=0.06, glass=True)
        backdrop((12, 12, 14), 1.8)
        bokeh(30, 0.2, 0.8, 1.3, [(255, 190, 110), (255, 150, 80), (250, 214, 160), (210, 170, 255)], seed=3,
              power=18, size=0.016)
        glow((255, 168, 96), 1.2, y=0.3, w=0.2, h=0.2, z=0.0)
    else:
        setup("kum", samples, world=(250, 240, 222), wstr=0.5, glass=True, exposure=0.2)
        backdrop((240, 228, 204), 0.5, var=(226, 210, 180))
    g = np.random.default_rng(13)
    gl = {"negroni": "rocks", "oldfashioned": "rocks", "gunbatimi": "highball", "aperol": "wine", "mojito": "highball",
          "colada": "hurricane"}[kind]
    inner = glass(GLASS[gl], t=0.0022, bottom=BOTTOM[gl])
    top = GLASS[gl][-1][1]
    if kind == "negroni":
        rl = liquid(inner, 0.062, mat("negroni", (196, 24, 26), rough=0.0, trans=1.0, ior=1.34))
        ice_cube("buz", 0.0, 0.0, 0.05, 0.024, (8, 10, 22), 1)
        V, F = grid(0.07, 0.016, 30, 6)
        V[:, 2] = 0.012 * np.sin(V[:, 0] / 0.07 * np.pi) + 0.006 * (V[:, 1] / 0.008) ** 2
        obj("kabuk", (V, F), M("portakal_kabuk"), loc=(0.004, -0.004, 0.074), rot=(10, -14, 28), solid=0.0016)
    elif kind == "oldfashioned":
        liquid(inner, 0.055, mat("burbon", (196, 108, 26), rough=0.0, trans=1.0, ior=1.34))
        obj("buz_kure", sphere(0.027, 48, 24), M("buz"), loc=(0, 0, 0.045))
        V, F = grid(0.06, 0.014, 30, 6)
        V[:, 2] = 0.01 * np.sin(V[:, 0] / 0.06 * np.pi) + 0.006 * (V[:, 1] / 0.007) ** 2
        obj("kabuk", (V, F), M("portakal_kabuk"), loc=(-0.01, 0.006, 0.08), rot=(0, -20, -40), solid=0.0015)
        obj("kiraz", sphere(0.0085, 32, 16), M("kiraz"), loc=(0.016, -0.012, 0.07))
        tube("cop", [(0.016, -0.012, 0.07), (0.03, -0.022, 0.11)], 0.0012, M("altin"))
    elif kind == "gunbatimi":
        liquid(inner, 0.13, mat_zgrad("gunbatimi", [(0.0, (176, 10, 30)), (0.25, (224, 40, 30)), (0.45, (246, 110, 20)),
                                                     (1.0, (252, 172, 40))], 0.01, 0.13, trans=0.85))
        for k in range(4):
            ice_cube(f"buz{k}", g.uniform(-0.008, 0.008), g.uniform(-0.008, 0.008), 0.05 + 0.024 * k, 0.0125,
                     (g.uniform(0, 40), g.uniform(0, 40), g.uniform(0, 90)), k)
        citrus_slice("dilim", 0.03, -0.004, 0.15, 0.027, (90, 0, 80))
        tube("pipet", [(0.004, 0.006, 0.02), (0.016, 0.02, 0.2)], 0.003, M("pipet"))
    elif kind == "aperol":
        liquid(inner, 0.165, mat("aperol", (255, 112, 8), rough=0.0, trans=0.55, sss=0.25, sss_r=(1, 0.5, 0.2),
                                 ior=1.34))
        for k in range(5):
            ice_cube(f"buz{k}", g.uniform(-0.016, 0.016), g.uniform(-0.016, 0.016), 0.118 + 0.012 * k, 0.012,
                     (g.uniform(0, 40), g.uniform(0, 40), g.uniform(0, 90)), k)
        citrus_slice("dilim", 0.0, -0.022, 0.14, 0.026, (82, 0, 8))
        bub = mat("kabarcik", (255, 255, 255), rough=0.0, trans=1.0, ior=1.0)
        for k in range(40):
            a, rr = g.uniform(0, 2 * np.pi), g.uniform(0, 0.03)
            obj(f"kabarcik{k}", sphere(0.0007, 8, 4), bub, loc=(rr * math.cos(a), rr * math.sin(a), g.uniform(0.1, 0.16)))
    elif kind == "mojito":
        liquid(inner, 0.13, mat("mojito", (232, 246, 214), rough=0.0, trans=1.0, ior=1.34))
        for k in range(12):
            V, F = superquad(0.009, 0.008, 0.006, 0.6, 12, 6)
            V = wobble(V, F, 0.0015, 300, k)
            obj(f"kirik_buz{k}", (V, F), M("buz"), loc=(g.uniform(-0.014, 0.014), g.uniform(-0.014, 0.014),
                                                       0.03 + 0.11 * k / 12), rot=(k * 20, k * 33, k * 41))
        for k in range(9):
            p = (g.uniform(-0.015, 0.015), g.uniform(-0.015, 0.015), g.uniform(0.03, 0.12))
            obj(f"nane_ic{k}", leaf(0.022, 0.014, 0.3, seed=k), M("nane"), loc=p,
                rot=(g.uniform(0, 360), g.uniform(0, 360), g.uniform(0, 360)), solid=0.0004)
        leaves(6, (0.0, 0.0), 0.006, 0.026, 0.016, M("nane"), 21, 0.15, curl=0.35, tilt=35)
        citrus_slice("lime", 0.012, -0.01, 0.06, 0.016, (70, 10, 30), "lime", 0.008)
        tube("pipet", [(0.006, 0.008, 0.02), (0.018, 0.022, 0.2)], 0.003, M("pipet"))
    elif kind == "colada":
        cream = mat("colada", (248, 240, 214), rough=0.25, sss=0.7, sss_r=(1, 0.9, 0.7), coat=0.4)
        liquid(inner, 0.17, cream, meniscus=False)
        pine = mat("ananas", (250, 206, 70), rough=0.3, sss=0.5, coat=0.5, stretch=(1, 1, 4),
                   var=((240, 186, 40), 0.5), var_scale=200)
        V, F = prism([(0, 0), (0.05, -0.012), (0.05, 0.012)], 0.012, -0.006)
        obj("ananas", (V, F), pine, loc=(0.03, -0.01, 0.19), rot=(90, 0, 60), smooth=False, bevel=0.002)
        obj("kiraz", sphere(0.0085, 32, 16), mat("kiraz_kirmizi", (210, 16, 30), rough=0.08, coat=1.0, sss=0.3),
            loc=(-0.012, -0.01, 0.195))
        tube("pipet", [(0.004, 0.006, 0.05), (0.02, 0.024, 0.24)], 0.003, mat("pipet_beyaz", (246, 246, 246),
                                                                               rough=0.3))
        leaves(3, (0.03, 0.012), 0.004, 0.06, 0.014, M("biber_yesil"), 31, 0.19, curl=0.2, tilt=60)
    cz = top * 0.55
    camera((0.0, 0.0, cz), 0.6, 9, azim=-12, lens=95, fstop=2.8)
    if night:
        light("ana", 14, 0.4, -110, 28, 0.6, (0, 0, cz), (255, 226, 190))
        light("arka", 30, 0.25, 175, 18, 0.5, (0, 0, cz), (255, 200, 150))
        light("dolgu", 2, 1.0, 60, 15, 0.8, (0, 0, cz), (200, 210, 255))
    else:
        light("gunes", 90, 0.12, -140, 38, 1.2, (0, 0, cz), (255, 238, 210))
        light("dolgu", 14, 1.4, 40, 20, 1.0, (0, 0, cz), (224, 236, 255))
        light("arka", 20, 0.4, 175, 22, 0.6, (0, 0, cz), (255, 230, 200))
    render(f"icki_{kind}")


def poke(samples=48):
    setup("keten", samples, world=(244, 236, 222), wstr=0.2)
    g = np.random.default_rng(17)
    fill = bowl(0.1, 0.06, "seramik_tas")
    zl, rl = fill(0.85)
    V, F = disc(rl, 96, 12)
    V[:, 2] = 0.003 * Noise(120, 2)(V)
    obj("pilav", (V, F), rice_mat(), loc=(0, 0, zl), solid=0.004)
    sal = mat_stripes("somon_kup", (242, 112, 58), (252, 214, 190), 160, rough=0.2, coat=0.7, sss=0.5, width=0.22)
    for k, (dx, dy) in enumerate(scatter_disc(12, 0.03, 0.013, 3)):
        obj(f"somon{k}", superquad(0.0065, 0.0065, 0.006, 0.35), sal, loc=(dx - 0.03, dy + 0.025, zl + 0.007),
            rot=(g.uniform(-15, 15), g.uniform(-15, 15), g.uniform(0, 90)))
    avo = mat("avokado", (176, 200, 80), rough=0.25, coat=0.6, sss=0.4, sss_r=(0.6, 1, 0.3),
              ramp=[(0.35, (200, 212, 100)), (0.62, (130, 168, 56)), (0.7, (56, 80, 30))], var_scale=30)
    for k in range(6):
        obj(f"avo{k}", superquad(0.03, 0.009, 0.004, 0.5, 32, 12), avo, loc=(0.035, 0.01 + 0.012 * (k - 2.5) * 0.9,
                                                                            zl + 0.006 + 0.001 * k), rot=(0, 8, 70))
    eda = mat("edamame", (120, 176, 60), rough=0.3, coat=0.4, sss=0.3)
    for k, (dx, dy) in enumerate(scatter_disc(16, 0.022, 0.008, 5)):
        obj(f"edamame{k}", superquad(0.0055, 0.0042, 0.0035, 0.8, 16, 8), eda, loc=(dx - 0.01, dy - 0.04, zl + 0.004),
            rot=(0, 0, g.uniform(0, 180)))
    mango = mat("mango", (250, 170, 30), rough=0.2, coat=0.6, sss=0.5)
    for k, (dx, dy) in enumerate(scatter_disc(9, 0.02, 0.011, 7)):
        obj(f"mango{k}", superquad(0.0055, 0.0055, 0.005, 0.35), mango, loc=(dx + 0.04, dy - 0.035, zl + 0.006),
            rot=(g.uniform(-15, 15), g.uniform(-15, 15), g.uniform(0, 90)))
    cab = mat("mor_lahana", (120, 30, 90), rough=0.3, coat=0.4, sss=0.3)
    for k in range(18):
        p0 = g.normal(0, 0.008, 2) + [-0.045, -0.01]
        a = g.uniform(0, np.pi)
        pts = [(p0[0] + 0.012 * t * math.cos(a), p0[1] + 0.012 * t * math.sin(a), zl + 0.006 + 0.002 * math.sin(t * 3))
               for t in np.linspace(-1, 1, 6)]
        tube(f"lahana{k}", pts, 0.0011, cab)
    cuc = mat("salatalik", (150, 196, 100), rough=0.25, coat=0.5, ramp=[(0.0, (210, 230, 170)), (0.6, (180, 214, 130)),
                                                                        (1.0, (40, 90, 30))])
    for k, (dx, dy) in enumerate(((0.0, 0.05), (0.014, 0.045), (-0.013, 0.048))):
        obj(f"salatalik{k}", revolve([(0, 0), (0.011, 0), (0.011, 0.003), (0, 0.003)], 32),
            mat_cut(f"salatalik_k{k}", (214, 232, 176), (170, 210, 120), (40, 92, 30), (None, None, None),
                    edge=(0.8, 0.92), radial=0.011, rough=0.25, coat=0.5),
            loc=(dx, dy, zl + 0.005), rot=(12, 0, 0))
    sesame = M("susam")
    for k in range(70):
        p = g.normal(0, 0.035, 2)
        if np.hypot(*p) < rl - 0.01:
            obj(f"susam{k}", superquad(0.0011, 0.0007, 0.0003, 0.6, 8, 4), sesame, loc=(p[0], p[1], zl + 0.013),
                rot=(0, 0, g.uniform(0, 180)))
    camera((0.0, 0.0, 0.04), 0.62, 62, azim=-10, lens=78, fstop=4.0)
    light("gunes", 60, 0.15, -140, 40, 1.2, (0, 0, 0.04), (255, 240, 214))
    light("dolgu", 10, 1.4, 40, 30, 1.0, (0, 0, 0.04), (226, 236, 255))
    render("poke_bowl")


# ---- balık, meze

def fish_skin():
    """Levrek derisi: sırtı koyu, karnı gümüş; ızgara izleri çapraz koyu bant; ince benekler."""
    m = bpy.data.materials.new("levrek_deri")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.28
    b.inputs["Coat Weight"].default_value = 0.6
    b.inputs["Metallic"].default_value = 0.25
    tc = node(nt, "ShaderNodeTexCoord", (-1200, 0))
    sep = node(nt, "ShaderNodeSeparateXYZ", (-1000, 0))
    nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])
    mr = node(nt, "ShaderNodeMapRange", (-800, 0))
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = -0.02, 0.03
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    r = node(nt, "ShaderNodeValToRGB", (-600, 0))
    els = r.color_ramp.elements
    els[0].position, els[0].color = 0.2, srgb((226, 220, 204))
    els[1].position, els[1].color = 0.95, srgb((96, 92, 76))
    els.new(0.6).color = srgb((176, 164, 132))
    nt.links.new(mr.outputs["Result"], r.inputs["Fac"])
    dot = node(nt, "ShaderNodeVectorMath", (-1000, -300))
    dot.operation = "DOT_PRODUCT"
    dot.inputs[1].default_value = (1.0, 0.0, 0.55)
    nt.links.new(tc.outputs["Object"], dot.inputs[0])
    mul = node(nt, "ShaderNodeMath", (-800, -300))
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = 24.0
    nt.links.new(dot.outputs["Value"], mul.inputs[0])
    pp = node(nt, "ShaderNodeMath", (-650, -300))
    pp.operation = "PINGPONG"
    pp.inputs[1].default_value = 0.5
    nt.links.new(mul.outputs[0], pp.inputs[0])
    sr = node(nt, "ShaderNodeValToRGB", (-450, -300))
    sr.color_ramp.elements[0].position, sr.color_ramp.elements[0].color = 0.025, srgb((84, 56, 34))
    sr.color_ramp.elements[1].position, sr.color_ramp.elements[1].color = 0.085, (1, 1, 1, 1)
    nt.links.new(pp.outputs[0], sr.inputs["Fac"])
    nz = node(nt, "ShaderNodeTexNoise", (-650, -550), Scale=60.0, Detail=6.0)
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    nr = node(nt, "ShaderNodeValToRGB", (-450, -550))
    nr.color_ramp.elements[0].position, nr.color_ramp.elements[0].color = 0.45, (1, 1, 1, 1)
    nr.color_ramp.elements[1].position, nr.color_ramp.elements[1].color = 0.75, srgb((176, 120, 70))
    nt.links.new(nz.outputs["Fac"], nr.inputs["Fac"])
    m1 = node(nt, "ShaderNodeMix", (-200, 0))
    m1.data_type, m1.blend_type = "RGBA", "MULTIPLY"
    m1.inputs["Factor"].default_value = 1.0
    nt.links.new(r.outputs["Color"], m1.inputs["A"])
    nt.links.new(sr.outputs["Color"], m1.inputs["B"])
    m2 = node(nt, "ShaderNodeMix", (0, 0))
    m2.data_type, m2.blend_type = "RGBA", "MULTIPLY"
    m2.inputs["Factor"].default_value = 0.8
    nt.links.new(m1.outputs["Result"], m2.inputs["A"])
    nt.links.new(nr.outputs["Color"], m2.inputs["B"])
    nt.links.new(m2.outputs["Result"], b.inputs["Base Color"])
    bp = node(nt, "ShaderNodeBump", (200, -300), Strength=0.25, Distance=0.001)
    nt.links.new(pp.outputs[0], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def fish(samples=48):
    setup("mese", samples, world=(236, 230, 222), wstr=0.15)
    backdrop((214, 220, 226), 0.6)
    g = np.random.default_rng(19)
    zp = plate(0.15, "seramik_lacivert", depth=0.014)
    rot = -12
    ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    W = lambda x, y: (x * ca - y * sa, x * sa + y * ca)
    V, F = sphere(1, 64, 32)
    x = V[:, 0]
    taper = np.where(x > 0, 1 - 0.78 * np.abs(x) ** 1.6, 1 - 0.25 * np.abs(x) ** 2.2)
    V = np.c_[x * 0.12, V[:, 1] * 0.026 * taper, V[:, 2] * 0.03 * taper]
    V = wobble(V, F, 0.0006, 200, 3)
    zc = zp + 0.024
    obj("balik", (V, F), fish_skin(), loc=(0, 0, zc), rot=(0, 0, rot))
    fin = mat("yuzgec", (150, 140, 120), rough=0.4, trans=0.3, var=((90, 80, 66), 0.5), var_scale=200,
              stretch=(1, 20, 1))
    tail = prism([(0, 0), (0.042, -0.026), (0.034, 0), (0.042, 0.026)], 0.002, -0.001)
    obj("kuyruk", tail, fin, loc=(*W(0.112, 0), zc), rot=(90, 0, rot), smooth=False)
    dorsal = prism([(-0.04, 0), (0.03, 0), (0.0, 0.016), (-0.035, 0.012)], 0.0016, -0.0008)
    obj("sirt", dorsal, fin, loc=(*W(0.0, 0), zc + 0.026), rot=(90, 0, rot), smooth=False)
    ex, ey = W(-0.088, -0.0205)
    obj("goz", sphere(0.0058, 24, 12), mat("goz", (232, 226, 210), rough=0.1, coat=1.0), loc=(ex, ey, zc + 0.011))
    bx, by = W(-0.088, -0.0245)
    obj("bebek", sphere(0.0032, 16, 8), mat("bebek", (16, 16, 16), rough=0.05, coat=1.0), loc=(bx, by, zc + 0.011))
    gx = [W(-0.07 + 0.002 * t, -0.022 + 0.0) for t in range(1)]
    pts = [(*W(-0.072 + 0.006 * math.sin(t), -0.0215 + 0.002 * t), zc - 0.012 + 0.024 * t) for t in np.linspace(0, 1, 10)]
    tube("solungac", pts, 0.0008, mat("solungac_iz", (90, 70, 50), rough=0.5))
    for k, (dx, dy) in enumerate(((0.06, -0.08), (0.095, -0.062))):
        citrus_slice(f"limon{k}", dx, dy, zp + 0.012, 0.022, (12, 0, 20 * k), "limon", 0.016)
    roka = mat("roka", (60, 110, 40), rough=0.35, coat=0.3, sss=0.3, var=((90, 140, 60), 0.5))
    for k in range(10):
        p = g.normal(0, 0.016, 2) + [-0.06, 0.075]
        obj(f"roka{k}", leaf(0.05, 0.014, 0.25, ruffle=0.4, seed=k), roka, loc=(p[0], p[1], zp + 0.004 + 0.002 * k),
            rot=(g.uniform(-12, 12), g.uniform(-12, 12), g.uniform(0, 360)), solid=0.0004)
    onion = mat("mor_sogan", (170, 70, 130), rough=0.25, coat=0.5, sss=0.4)
    for k in range(6):
        prof = [(0.012 + 0.0012 * math.cos(t), 0.0012 * math.sin(t)) for t in np.linspace(0, 2 * np.pi, 8, endpoint=False)]
        obj(f"sogan{k}", revolve(prof, 32, closed=True), onion, loc=(-0.03 + g.normal(0, 0.01), 0.08 + g.normal(0, 0.006),
                                                                      zp + 0.01), rot=(g.uniform(-30, 30), 0, 0))
    camera((0.0, 0.0, 0.03), 0.6, 36, azim=-8, lens=80, fstop=4.0)
    studio(key=(-115, 38), target=(0, 0, 0.03), power=26)
    render("balik_levrek")


def calamari(samples=48):
    setup("mese", samples, world=(236, 230, 222), wstr=0.15)
    backdrop((214, 220, 226), 0.6)
    g = np.random.default_rng(23)
    zp = plate(0.13, "porselen", depth=0.014)
    batter = mat("pane", (226, 168, 82), rough=0.45, coat=0.3,
                 ramp=[(0.38, (236, 190, 110)), (0.52, (210, 146, 64)), (0.6, (170, 104, 40))], var_scale=200, bump=1.2,
                 bump_scale=420)
    for k in range(16):
        rr = g.uniform(0.012, 0.017)
        prof = [(rr + 0.0048 * math.cos(t), 0.004 * math.sin(t)) for t in np.linspace(0, 2 * np.pi, 14, endpoint=False)]
        V, F = revolve(prof, 48, closed=True)
        V = wobble(V, F, 0.0012, 300, k)
        a, d = g.uniform(0, 2 * np.pi), 0.055 * math.sqrt(g.uniform())
        obj(f"kalamar{k}", (V, F), batter, loc=(d * math.cos(a) - 0.015, d * math.sin(a), zp + 0.006 + 0.008 * (k > 9)),
            rot=(g.uniform(-30, 30), g.uniform(-30, 30), 0))
    ramekin(0.07, 0.07, zp, 0.03, mat("tarator", (238, 232, 214), rough=0.3, sss=0.4, bump=0.3, bump_scale=200))
    for k in range(2):
        V, F = sphere(1, 32, 16)
        V = V * [0.03, 0.017, 0.016]
        V[:, 2] = np.maximum(V[:, 2], -0.002)
        obj(f"limon_dilim{k}", (V, F), M("limon"), loc=(0.07 - 0.02 * k, -0.07 + 0.01 * k, zp + 0.005), rot=(0, 0, 30 + 40 * k))
    leaves(6, (-0.06, -0.06), 0.012, 0.02, 0.013, M("maydanoz"), 8, zp + 0.008)
    camera((0.0, 0.0, 0.03), 0.6, 46, azim=-10, lens=80, fstop=4.0)
    studio(key=(-115, 38), target=(0, 0, 0.03), power=26)
    render("balik_kalamar")


def guvec(samples=48):
    setup("ceviz", samples, world=(236, 226, 212), wstr=0.14)
    backdrop((60, 44, 34), 0.6)
    g = np.random.default_rng(29)
    fill = bowl(0.07, 0.045, "toprak", t=0.006, foot=0.6)
    zl, rl = fill(0.92)
    cheese = mat("eriyen_kasar", (240, 200, 120), rough=0.3, coat=0.5, sss=0.4,
                 ramp=[(0.38, (246, 220, 150)), (0.5, (226, 168, 80)), (0.58, (160, 96, 40)), (0.64, (110, 60, 26))],
                 var_scale=50, bump=0.6, bump_scale=120)
    V, F = disc(rl, 96, 12)
    V[:, 2] = 0.004 * np.maximum(Noise(80, 3)(V), -0.2)
    obj("kasar", (V, F), cheese, loc=(0, 0, zl), solid=0.004)
    shrimp = mat("karides", (240, 120, 80), rough=0.2, coat=0.7, sss=0.5, ramp=[(0.4, (250, 150, 110)),
                                                                                 (0.6, (226, 90, 60))], var_scale=200)
    for k in range(4):
        a0 = k * 1.4 + 0.3
        c = np.array([0.03 * math.cos(a0), 0.03 * math.sin(a0)])
        pts = [(c[0] + 0.012 * math.cos(a0 + t), c[1] + 0.012 * math.sin(a0 + t), zl + 0.003 + 0.003 * math.sin(t))
               for t in np.linspace(0, 3.2, 12)]
        tube(f"karides{k}", pts, 0.0045, shrimp)
    leaves(8, (0.0, 0.0), 0.02, 0.014, 0.01, M("maydanoz"), 9, zl + 0.006)
    camera((0.0, 0.0, 0.04), 0.5, 48, azim=-10, lens=82, fstop=3.5)
    studio(key=(-115, 38), target=(0, 0, 0.04), power=26)
    render("balik_guvec")


# ---- çay bahçesi

def tea(samples=64):
    setup("ceviz", samples, world=(236, 226, 212), wstr=0.12, glass=True)
    backdrop((70, 90, 60), 0.7, var=(90, 110, 70))
    bokeh(14, 0.25, 0.6, 1.0, [(255, 236, 170), (230, 255, 190)], seed=5, power=6, size=0.02)
    g = np.random.default_rng(31)
    zs = saucer(0.055, mat_key="porselen")
    gold = M("altin")
    obj("altin_serit", revolve([(0.0545, zs + 0.0084), (0.0555, zs + 0.0086), (0.0555, zs + 0.0094),
                                (0.0545, zs + 0.0092)], 96, closed=True), gold)
    inner = glass(GLASS["tulip"], t=0.0015, bottom=BOTTOM["tulip"], loc=(0, 0, zs))
    liquid(inner, 0.088, mat("cay", (178, 46, 12), rough=0.0, trans=0.92, ior=1.33), loc=(0, 0, zs))
    for k, (dx, dy) in enumerate(((0.035, -0.02), (0.04, 0.0))):
        obj(f"seker{k}", superquad(0.0055, 0.0055, 0.0055, 0.3), mat("kesme_seker", (250, 250, 248), rough=0.9,
                                                                      bump=0.5, bump_scale=1200),
            loc=(dx, dy, zs + 0.006), rot=(0, 0, 20 * k))
    spoon(-0.03, -0.035, zs, -60, 0.7)
    zb = 0.0
    simit = mat("simit", (170, 90, 40), rough=0.4, coat=0.3, ramp=[(0.4, (190, 110, 50)), (0.6, (140, 70, 28))],
                var_scale=40, bump=0.3)
    prof = [(0.05 + 0.014 * math.cos(t), 0.012 + 0.012 * math.sin(t)) for t in np.linspace(0, 2 * np.pi, 16,
                                                                                         endpoint=False)]
    V, F = revolve(prof, 96, closed=True)
    V = wobble(V, F, 0.0015, 60, 3)
    obj("simit", (V, F), simit, loc=(-0.11, 0.06, 0))
    for k in range(120):
        t, a = g.uniform(0, np.pi), g.uniform(0, 2 * np.pi)
        rr = 0.05 + 0.0145 * math.cos(t)
        obj(f"susam{k}", superquad(0.0018, 0.001, 0.0005, 0.6, 8, 4), M("susam"),
            loc=(-0.11 + rr * math.cos(a), 0.06 + rr * math.sin(a), 0.012 + 0.0145 * math.sin(t)),
            rot=(g.uniform(-30, 30), g.uniform(-30, 30), g.uniform(0, 180)))
    camera((0.0, 0.0, 0.05), 0.5, 14, azim=-14, lens=90, fstop=2.8)
    light("ana", 22, 0.5, -110, 30, 0.6, (0, 0, 0.05), (255, 236, 210))
    light("arka", 26, 0.3, 170, 20, 0.5, (0, 0, 0.05), (255, 220, 170))
    light("dolgu", 3, 1.0, 50, 15, 0.8, (0, 0, 0.05), (210, 220, 255))
    render("cay")


def gozleme(samples=48):
    setup("keten", samples, world=(244, 236, 222), wstr=0.15)
    g = np.random.default_rng(37)
    zb = round_board(0.16, 0.02, "zeytin", handle=False)
    dough = mat("gozleme", (232, 206, 156), rough=0.6, sss=0.2,
                ramp=[(0.4, (238, 216, 170)), (0.52, (214, 170, 110)), (0.58, (168, 112, 56)), (0.62, (110, 70, 34))],
                var_scale=30, bump=0.4, bump_scale=80)
    for k, (a, dx, dy) in enumerate(((10, -0.01, 0.02), (-25, 0.02, -0.03))):
        pts = [(0.12 * math.cos(t), 0.12 * math.sin(t)) for t in np.linspace(0, np.pi, 30)]
        V, F = prism(pts, 0.012, -0.006)
        V[:, 2] *= 1 - 0.3 * (V[:, 1] / 0.12)
        V = wobble(V, F, 0.0015, 60, k)
        obj(f"gozleme{k}", (V, F), dough, loc=(dx, dy, zb + 0.006 + 0.012 * k), rot=(0, 0, a), bevel=0.004, subsurf=1)
    spin = mat("ispanak_peynir", (90, 120, 50), rough=0.4, var=((236, 230, 210), 0.5), var_scale=300)
    obj("ic", superquad(0.1, 0.004, 0.003, 0.6), spin, loc=(0.02, -0.03, zb + 0.018), rot=(0, 0, -25))
    citrus_slice("limon", 0.1, 0.08, zb + 0.004, 0.022, (0, 0, 0), "limon", 0.008)
    ay = cup(0.03, 0.08, "porselen", z=0.0, handle=False, loc=(0.16, -0.08), flare=1.05)
    zl, rl = ay(0.85)
    obj("ayran", disc(rl, 48, 6), mat("ayran", (250, 248, 242), rough=0.3, sss=0.4, bump=0.3, bump_scale=600,
                                      voronoi=1), loc=(0.16, -0.08, zl))
    camera((0.02, 0.0, zb), 0.66, 52, azim=-12, lens=78, fstop=4.0)
    light("gunes", 60, 0.2, -135, 40, 1.2, (0, 0, zb), (255, 238, 212))
    light("dolgu", 10, 1.4, 40, 30, 1.0, (0, 0, zb), (226, 236, 255))
    render("gozleme")


def toast(samples=48):
    setup("keten", samples, world=(244, 236, 222), wstr=0.15)
    zb = board(0.3, 0.2, 0.02, "mese", rot=-5)
    bread = mat_stripes("tost", (214, 160, 90), (120, 72, 34), 70, rough=0.55, direction=(1, 1, 0), width=0.26)
    cheese = mat("kasar", (246, 200, 90), rough=0.2, coat=0.6, sss=0.5)
    for k, (dx, dy, a) in enumerate(((-0.045, 0.0, 20), (0.05, 0.01, 200))):
        tri = [(-0.06, -0.06), (0.06, -0.06), (-0.06, 0.06)]
        ar = math.radians(a)
        V, F = prism(tri, 0.008, 0)
        V = wobble(V, F, 0.0008, 80, k)
        obj(f"ekmek_alt{k}", (V, F), bread, loc=(dx, dy, zb), rot=(0, 0, a), bevel=0.004)
        obj(f"ekmek_ust{k}", (V, F), bread, loc=(dx, dy, zb + 0.011), rot=(0, 0, a), bevel=0.004)
        for j in range(3):
            t = 0.2 + 0.3 * j
            px, py = 0.06 - 0.12 * t, -0.06 + 0.12 * t
            px, py = 0.06 * (1 - t) - 0.06 * t, -0.06 * (1 - t) + 0.06 * t
            rx, ry = px * math.cos(ar) - py * math.sin(ar), px * math.sin(ar) + py * math.cos(ar)
            blob(f"kasar{k}_{j}", 0.009, 0.35, cheese, (dx + rx * 1.02, dy + ry * 1.02, zb + 0.0095), amp=0.2, seed=j,
                 sx=1.4, rot=(0, 0, a - 45))
    ramekin(0.0, 0.075, zb, 0.026, mat("tursu_kase", (120, 140, 50), rough=0.2, coat=0.6, bump=0.5, bump_scale=200))
    camera((0.0, 0.0, zb + 0.01), 0.6, 42, azim=-12, lens=80, fstop=4.0)
    light("gunes", 60, 0.2, -135, 40, 1.2, (0, 0, zb), (255, 238, 212))
    light("dolgu", 10, 1.4, 40, 30, 1.0, (0, 0, zb), (226, 236, 255))
    render("tost")


# ---- Osmanlı

def hunkar(samples=48):
    setup("keten", samples, world=(236, 226, 212), wstr=0.14)
    backdrop((120, 40, 44), 0.7)
    g = np.random.default_rng(41)
    zp = plate(0.14, "porselen_krem", depth=0.016)
    obj("altin_kenar", revolve([(0.1395, 0.0155), (0.1415, 0.0162), (0.1415, 0.0172), (0.1395, 0.0166)], 128,
                               closed=True), M("altin"))
    beg = mat("begendi", (232, 214, 182), rough=0.35, sss=0.4, coat=0.2,
              ramp=[(0.4, (236, 220, 190)), (0.55, (214, 188, 146)), (0.62, (186, 150, 100))], var_scale=60, bump=0.6,
              bump_scale=90)
    V, F = disc(0.098, 96, 14)
    rr = np.hypot(V[:, 0], V[:, 1])
    V[:, 2] = 0.014 * (1 - (rr / 0.098) ** 2) + 0.0025 * Noise(60, 4)(V)
    obj("begendi", (V, F), beg, loc=(0, 0, zp), solid=0.002, subsurf=1)
    stew = mat("tas_kebap", (138, 66, 34), rough=0.3, coat=0.3, ramp=[(0.4, (156, 80, 42)), (0.6, (96, 44, 22))],
               var_scale=90, bump=0.8, bump_scale=250)
    for k, (dx, dy) in enumerate(scatter_disc(14, 0.045, 0.019, 3)):
        blob(f"et{k}", 0.016, 0.7, stew, (dx, dy, zp + 0.018 + 0.004 * (k > 8)), amp=0.45, seed=k, freq=90,
             sx=g.uniform(0.9, 1.3), rot=(0, 0, g.uniform(0, 180)))
    sauce = mat("salca_sos", (150, 40, 18), rough=0.05, coat=1.0, sss=0.2)
    V, F = disc(0.06, 64, 8)
    V[:, :2] *= (1 + 0.15 * np.sin(5 * np.arctan2(V[:, 1], V[:, 0])))[:, None]
    obj("sos", (V, F), sauce, loc=(0, 0, zp + 0.0135), solid=0.002)
    leaves(9, (0.0, 0.0), 0.022, 0.014, 0.01, M("maydanoz"), 10, zp + 0.03)
    pep = mat("kozbiber", (60, 110, 30), rough=0.15, coat=0.8)
    pts = [(0.06 + 0.04 * t, -0.07 + 0.02 * math.sin(t * 2), zp + 0.012) for t in np.linspace(0, 1, 10)]
    tube("kozbiber", pts, 0.006, pep)
    camera((0.0, 0.0, 0.03), 0.52, 42, azim=-10, lens=80, fstop=4.0)
    studio(key=(-115, 38), target=(0, 0, 0.03), power=26)
    render("hunkar")


DISHES = {
    "pizza_margherita": lambda s: pizza("margherita", s),
    "pizza_diavola": lambda s: pizza("diavola", s),
    "pizza_formaggi": lambda s: pizza("formaggi", s),
    "pizza_tartufo": lambda s: pizza("tartufo", s),
    "burger_smash": lambda s: burger("smash", s),
    "burger_truffle": lambda s: burger("truffle", s),
    "burger_chick": lambda s: burger("chick", s),
    "burger_veggie": lambda s: burger("veggie", s),
    "kahve_flatwhite": lambda s: coffee("flatwhite", s),
    "kahve_espresso": lambda s: coffee("espresso", s),
    "kahve_turk": lambda s: coffee("turk", s),
    "kahve_fistik": lambda s: coffee("fistik", s),
    "kahve_cheesecake": cheesecake,
    "susi_nigiri": lambda s: sushi("nigiri", s),
    "susi_dragon": lambda s: sushi("dragon", s),
    "susi_spicy": lambda s: sushi("spicy", s),
    "susi_ramen": ramen,
    "et_antrikot": lambda s: steak("antrikot", s),
    "et_pirzola": lambda s: steak("pirzola", s),
    "et_kofte": lambda s: steak("kofte", s),
    "et_adana": lambda s: steak("adana", s),
    "icki_negroni": lambda s: cocktail("negroni", s + 16),
    "icki_oldfashioned": lambda s: cocktail("oldfashioned", s + 16),
    "icki_gunbatimi": lambda s: cocktail("gunbatimi", s + 16),
    "icki_aperol": lambda s: cocktail("aperol", s + 16),
    "icki_mojito": lambda s: cocktail("mojito", s + 16),
    "icki_colada": lambda s: cocktail("colada", s + 16),
    "slider": slider,
    "poke_bowl": poke,
    "balik_levrek": fish,
    "balik_kalamar": calamari,
    "balik_guvec": guvec,
    "cay": tea,
    "gozleme": gozleme,
    "tost": toast,
    "hunkar": hunkar,
}


def main():
    global SIZE
    args = sys.argv[1:]
    samples = 48
    if "--ornek" in args:
        k = args.index("--ornek")
        samples = int(args[k + 1])
        del args[k:k + 2]
    if "--boyut" in args:
        k = args.index("--boyut")
        SIZE = int(args[k + 1])
        del args[k:k + 2]
    os.makedirs(OUT, exist_ok=True)
    import time
    for name, fn in DISHES.items():
        if args and not any(a in name for a in args):
            continue
        t = time.time()
        try:
            fn(samples)
        except Exception as ex:                      # biri bozulsa da diğerleri çizilsin
            import traceback
            traceback.print_exc()
            print(f"{name:24s} HATA {ex!r}", flush=True)
            continue
        print(f"{name:24s} {time.time() - t:5.1f} sn", flush=True)


if __name__ == "__main__":
    main()
