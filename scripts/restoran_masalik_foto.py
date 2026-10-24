"""Restoran masalıkları – gerçekçi ürün fotoğrafı (Blender Cycles).

restoran_masalik.py'deki modeller ahşap masa üstünde, stüdyo ışığında (büyük softbox + dolgu + arka ışık) çizilir:
mat PLA (hafif parlak), ipek altın / bakır (metalik), ahşap katkılı PLA (damarlı), ayakların yanlarında 0,2 mm katman
izleri, kenarlarda yuvarlatılmış ışık (bevel), arkası alan derinliğiyle bulanık.

Çıktı : restoran_masalik/foto/<tasarım>_on.png, <tasarım>_arka.png

Kullanım:
  pip install bpy==4.2.0
  python3 scripts/restoran_masalik_foto.py [anahtar ...] [--ornek 64]
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import restoran_masalik as M  # noqa: E402

OUT = os.path.join(M.OUT_DIR, "foto")
MM = 0.001
LAYER = 0.0002
SIZE = (760, 930)
LIGHT = (22.0, 6.0, 12.0)                                # ana, dolgu, arka ışık (W)
VIEW = {"on": (28.0, 11.0), "arka": (208.0, 11.0)}       # kamera açısı (derece), yükseklik açısı (derece)


def srgb(c):
    c = np.asarray(c, float) / 255.0
    return tuple(np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)) + (1.0,)


def node(nt, kind, loc=(0, 0), **inputs):
    n = nt.nodes.new(kind)
    n.location = loc
    for k, v in inputs.items():
        n.inputs[k].default_value = v
    return n


def material(name, rgb, metal=False, wood=False, layers=True):
    """PLA: hafif parlak plastik; ipek: metalik; ahşap: damarlı. Katman izi ve yuvarlatılmış kenar."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = node(nt, "ShaderNodeOutputMaterial", (900, 0))
    bsdf = node(nt, "ShaderNodeBsdfPrincipled", (600, 0))
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Base Color"].default_value = srgb(rgb)
    bsdf.inputs["Roughness"].default_value = 0.3 if metal else 0.52
    bsdf.inputs["Metallic"].default_value = 0.85 if metal else 0.0
    bsdf.inputs["Specular IOR Level"].default_value = 0.45
    if wood:
        tc = node(nt, "ShaderNodeTexCoord", (-900, 200))
        noise = node(nt, "ShaderNodeTexNoise", (-650, 200), Scale=900.0, Detail=4.0)
        nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
        ramp = node(nt, "ShaderNodeValToRGB", (-400, 200))
        ramp.color_ramp.elements[0].color = tuple(v * 0.82 for v in srgb(rgb)[:3]) + (1,)
        ramp.color_ramp.elements[1].color = srgb(rgb)
        nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.62
    bev = node(nt, "ShaderNodeBevel", (0, -300))
    bev.samples = 6
    bev.inputs["Radius"].default_value = 0.25 * MM
    normal = bev.outputs["Normal"]
    if layers:
        tc = node(nt, "ShaderNodeTexCoord", (-900, -500))
        sep = node(nt, "ShaderNodeSeparateXYZ", (-700, -500))
        nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])
        mul = node(nt, "ShaderNodeMath", (-500, -500))
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = 2 * math.pi / LAYER
        nt.links.new(sep.outputs["Z"], mul.inputs[0])
        sin = node(nt, "ShaderNodeMath", (-300, -500))
        sin.operation = "SINE"
        nt.links.new(mul.outputs["Value"], sin.inputs[0])
        bump = node(nt, "ShaderNodeBump", (300, -400), Strength=0.18, Distance=0.02 * MM)
        nt.links.new(sin.outputs["Value"], bump.inputs["Height"])
        nt.links.new(bev.outputs["Normal"], bump.inputs["Normal"])
        normal = bump.outputs["Normal"]
    nt.links.new(normal, bsdf.inputs["Normal"])
    return m


_MATS = {}


def mat_for(col, layers=True):
    key = (col, layers)
    if key not in _MATS:
        _MATS[key] = material(f"{col}_{int(layers)}", M.COL[col], metal=col in M.METAL, wood=col == "ahsap",
                              layers=layers)
    return _MATS[key]


def add_mesh(name, man, col, matrix=None, layers=True):
    V, T = A.mesh_arrays(man)
    me = bpy.data.meshes.new(name)
    me.from_pydata((V * MM).tolist(), [], T.tolist())
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(mat_for(col, layers))
    if matrix is not None:
        Mx = np.eye(4)
        Mx[:3, :4] = np.asarray(matrix, float)
        Mx[:3, 3] *= MM
        ob.matrix_world = Matrix(Mx.tolist())
    bpy.context.scene.collection.objects.link(ob)
    return ob


def table_material():
    m = bpy.data.materials.new("masa")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = node(nt, "ShaderNodeOutputMaterial", (1000, 0))
    bsdf = node(nt, "ShaderNodeBsdfPrincipled", (700, 0), Roughness=0.42)
    bsdf.inputs["Specular IOR Level"].default_value = 0.5
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    tc = node(nt, "ShaderNodeTexCoord", (-1000, 0))
    mapping = node(nt, "ShaderNodeMapping", (-800, 0))
    mapping.inputs["Scale"].default_value = (1.0, 7.0, 1.0)
    nt.links.new(tc.outputs["Object"], mapping.inputs["Vector"])
    noise = node(nt, "ShaderNodeTexNoise", (-600, 200), Scale=6.0, Detail=6.0, Distortion=0.4)
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    wave = node(nt, "ShaderNodeTexWave", (-350, 0), Scale=26.0, Distortion=9.0, Detail=4.0)
    wave.wave_type = "BANDS"
    wave.bands_direction = "Y"
    nt.links.new(mapping.outputs["Vector"], wave.inputs["Vector"])
    mix = node(nt, "ShaderNodeMix", (-120, 0))
    mix.data_type = "FLOAT"
    mix.inputs["Factor"].default_value = 0.35
    nt.links.new(wave.outputs["Fac"], mix.inputs["A"])
    nt.links.new(noise.outputs["Fac"], mix.inputs["B"])
    ramp = node(nt, "ShaderNodeValToRGB", (120, 0))
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = srgb((74, 46, 28))
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = srgb((170, 122, 80))
    nt.links.new(mix.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bump = node(nt, "ShaderNodeBump", (450, -250), Strength=0.12)
    nt.links.new(mix.outputs["Result"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def setup_scene(samples):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _MATS.clear()
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.02
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.render.resolution_x, sc.render.resolution_y = SIZE
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.view_settings.exposure = -0.25
    world = bpy.data.worlds.new("dunya")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = srgb((236, 226, 212))
    bg.inputs["Strength"].default_value = 0.28
    sc.world = world
    me = bpy.data.meshes.new("masa")
    s = 3.0
    me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    ob = bpy.data.objects.new("masa", me)
    ob.data.materials.append(table_material())
    sc.collection.objects.link(ob)
    wm = bpy.data.materials.new("duvar")
    wm.use_nodes = True
    wm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = srgb((222, 210, 194))
    wm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
    for k, y in enumerate((1.4, -1.4)):
        wall = bpy.data.meshes.new(f"duvar{k}")
        wall.from_pydata([(-s, y, 0), (s, y, 0), (s, y, 2), (-s, y, 2)], [], [(0, 1, 2, 3)])
        wo = bpy.data.objects.new(f"duvar{k}", wall)
        wo.data.materials.append(wm)
        sc.collection.objects.link(wo)
    return sc


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def light(name, energy, size, pos, target, color=(1, 1, 1)):
    li = bpy.data.lights.new(name, "AREA")
    li.energy = energy
    li.size = size
    li.color = color
    ob = bpy.data.objects.new(name, li)
    ob.location = pos
    look_at(ob, target)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def frame(sc, cam, corners, aspect):
    """Kamerayı, tüm köşeler kadraja sığacak uzaklığa getirir (perspektif)."""
    fov = cam.data.angle
    tan_v = math.tan(fov / 2)
    tan_h = tan_v * aspect
    centre = corners.mean(0)
    direction = np.asarray(cam["dir"], float)
    dist = 0.5
    for _ in range(30):
        pos = centre + direction * dist
        fwd = -direction
        right = np.cross(fwd, [0, 0, 1])
        right /= np.linalg.norm(right)
        up = np.cross(right, fwd)
        rel = corners - pos
        z = rel @ fwd
        need = max(np.max(np.abs(rel @ right) / (z * tan_h)), np.max(np.abs(rel @ up) / (z * tan_v)))
        dist *= need / 0.84
    cam.location = tuple(centre + direction * dist)
    look_at(cam, tuple(centre))
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = float(dist)
    cam.data.dof.aperture_fstop = 3.2


def render_design(fn, samples):
    d = fn()
    sc = setup_scene(samples)
    corners = []
    for p, Mx in d.panels:
        for name, man, col in p.solids():
            add_mesh(name, man, col, Mx)
            b = man.transform(Mx).bounding_box()
            corners.append(b)
    for name, man, col in d.stand:
        add_mesh(name, man, col)
        corners.append(man.bounding_box())
    for name, man, col in d.props:
        add_mesh(name, man, col, layers=False)
        corners.append(man.bounding_box())
    bb = np.array(corners)
    lo, hi = bb[:, :3].min(0) * MM, bb[:, 3:].max(0) * MM
    box = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    cam_d = bpy.data.cameras.new("kamera")
    cam_d.lens = 85
    cam_d.sensor_fit = "VERTICAL"
    cam = bpy.data.objects.new("kamera", cam_d)
    sc.collection.objects.link(cam)
    sc.camera = cam
    os.makedirs(OUT, exist_ok=True)
    centre = box.mean(0)
    for view, (az, el) in VIEW.items():
        a, e = math.radians(az), math.radians(el)
        direction = np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])
        cam["dir"] = direction.tolist()
        frame(sc, cam, box, SIZE[0] / SIZE[1])
        for ob in [o for o in sc.collection.objects if o.type == "LIGHT"]:
            bpy.data.objects.remove(ob)
        R = 0.9
        right = np.cross(-direction, [0, 0, 1])
        right /= np.linalg.norm(right)
        flat = direction * [1, 1, 0]
        flat /= np.linalg.norm(flat)
        key = centre + R * (0.75 * flat - 0.55 * right) + [0, 0, 0.75]
        fill = centre + R * (0.8 * flat + 0.7 * right) + [0, 0, 0.35]
        rim = centre - R * flat + R * 0.5 * right + [0, 0, 0.7]
        light("ana", LIGHT[0], 0.7, key, centre, (1.0, 0.97, 0.92))
        light("dolgu", LIGHT[1], 0.9, fill, centre, (0.92, 0.95, 1.0))
        light("arka", LIGHT[2], 0.4, rim, centre, (1.0, 0.95, 0.88))
        sc.render.filepath = os.path.join(OUT, f"{d.key}_{view}.png")
        bpy.ops.render.render(write_still=True)
    return d.key


def hero(keys, samples, size=(1800, 900)):
    """Birkaç masalık yan yana, aynı masada (katalog kapağı)."""
    global SIZE
    sc = setup_scene(samples)
    fns = {fn.__name__.split("_", 1)[1]: fn for fn in M.DESIGNS}
    x, corners = 0.0, []
    for k in keys:
        d = fns[k]()
        parts = [(n, m.transform(Mx), c) for p, Mx in d.panels for n, m, c in p.solids()] + d.stand + d.props
        b = np.array([m.bounding_box() for _, m, _ in parts])
        lo, hi = b[:, :3].min(0), b[:, 3:].max(0)
        dx = x - lo[0]
        for n, m, c in parts:
            add_mesh(n, m.translate((dx, -(lo[1] + hi[1]) / 2, 0)), c, layers=c not in ("beyaz",))
        corners.append([lo[0] + dx, lo[1], lo[2], hi[0] + dx, hi[1], hi[2]])
        x += hi[0] - lo[0] + 26.0
    bb = np.array(corners) * MM
    shift = -(bb[:, 0].min() + bb[:, 3].max()) / 2
    for ob in sc.collection.objects:
        if ob.type == "MESH" and ob.name not in ("masa", "duvar0", "duvar1"):
            ob.location.x += shift
    lo, hi = bb[:, :3].min(0) + [shift, 0, 0], bb[:, 3:].max(0) + [shift, 0, 0]
    box = np.array([[a, b_, c] for a in (lo[0], hi[0]) for b_ in (lo[1], hi[1]) for c in (lo[2], hi[2])])
    cam_d = bpy.data.cameras.new("kamera")
    cam_d.lens = 70
    cam_d.sensor_fit = "HORIZONTAL"
    cam = bpy.data.objects.new("kamera", cam_d)
    sc.collection.objects.link(cam)
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = size
    a, e = math.radians(12), math.radians(10)
    direction = np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])
    cam["dir"] = direction.tolist()
    frame_h(cam, box, size[0] / size[1])
    centre = box.mean(0)
    flat = direction * [1, 1, 0]
    flat /= np.linalg.norm(flat)
    right = np.cross(-direction, [0, 0, 1])
    right /= np.linalg.norm(right)
    light("ana", LIGHT[0] * 2.2, 1.2, centre + 1.1 * (0.75 * flat - 0.55 * right) + [0, 0, 0.9], centre,
          (1.0, 0.97, 0.92))
    light("dolgu", LIGHT[1] * 2.2, 1.4, centre + 1.1 * (0.8 * flat + 0.7 * right) + [0, 0, 0.4], centre,
          (0.92, 0.95, 1.0))
    light("arka", LIGHT[2] * 2.0, 0.8, centre - 1.0 * flat + [0, 0, 0.8], centre, (1.0, 0.95, 0.88))
    sc.render.filepath = os.path.join(OUT, "kapak.png")
    bpy.ops.render.render(write_still=True)


def frame_h(cam, corners, aspect):
    """Yatay kadraj (sensör yatay): köşeler sığacak uzaklık."""
    tan_h = math.tan(cam.data.angle / 2)
    tan_v = tan_h / aspect
    centre = corners.mean(0)
    direction = np.asarray(cam["dir"], float)
    dist = 0.8
    for _ in range(30):
        pos = centre + direction * dist
        fwd = -direction
        right = np.cross(fwd, [0, 0, 1])
        right /= np.linalg.norm(right)
        up = np.cross(right, fwd)
        rel = corners - pos
        z = rel @ fwd
        need = max(np.max(np.abs(rel @ right) / (z * tan_h)), np.max(np.abs(rel @ up) / (z * tan_v)))
        dist *= need / 0.9
    cam.location = tuple(centre + direction * dist)
    look_at(cam, tuple(centre))
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = float(dist)
    cam.data.dof.aperture_fstop = 5.6


def main():
    args = sys.argv[1:]
    samples = 32
    if "--kapak" in args:
        hero(["kemer", "bistro", "rooftop", "cay", "kahve"], 48)
        return
    if "--ornek" in args:
        k = args.index("--ornek")
        samples = int(args[k + 1])
        del args[k:k + 2]
    todo = [fn for fn in M.DESIGNS if not args or any(o in fn.__name__ for o in args)]
    import time
    for fn in todo:
        t = time.time()
        key = render_design(fn, samples)
        print(f"{key:16s} {time.time() - t:5.1f} sn", flush=True)


if __name__ == "__main__":
    main()
