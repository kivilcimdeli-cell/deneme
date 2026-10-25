"""PALOMA kartvizit sitesinin görselleri (Blender, Cycles): fotoğraf siteleri bu ortamdan açılmadığı için çizilir.

  ufuk : ufukta Akdeniz, öğleden sonra güneşi ve denizde ışık yolu (açılış ekranı, 1080 × 1920)
  sig  : yukarıdan sığ, turkuaz deniz; kum dalgacıkları ve ışık desenleri (otel bölümü, 1080 × 1350)

Deniz yüzeyi büyük bir düzlem; dalgalar ses (noise) dokusundan kabartma (bump). Gökyüzü Nishita. Sığ denizde su
yüzeyi kırar; turkuaz ve derinlikle koyulaşma kumun renginde (hacimli su bu ölçekte fazla kararıyordu), kumda sahte
ışık desenleri (Voronoi). Su yüzeyi gölge düşürmez: güneş kuma doğrudan ulaşır.

Kurulum: pip install bpy==4.2.0
Kullanım:
  python3 scripts/paloma_gorsel.py [ufuk|sig] [--deneme]     # --deneme: küçük ve hızlı
Çıktı : paloma_isimlik/gorsel/<ad>.jpg
"""
import math
import os
import sys

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "paloma_isimlik", "gorsel")


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def setup(w, h, samples, exposure=0.0, look="AgX - Medium High Contrast"):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.02
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 12
    sc.cycles.transmission_bounces = 12
    sc.cycles.volume_bounces = 2
    sc.cycles.caustics_reflective = sc.cycles.caustics_refractive = False
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = look
    sc.view_settings.exposure = exposure
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 90
    return sc


def node(nt, kind, loc=(0, 0), **inputs):
    n = nt.nodes.new(kind)
    n.location = loc
    for k, v in inputs.items():
        n.inputs[k].default_value = v
    return n


def sky(sc, elev, rot, strength=1.0, dust=1.0, air=1.0, ozone=1.0):
    w = bpy.data.worlds.new("gok")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    s = nt.nodes.new("ShaderNodeTexSky")
    s.sky_type = "NISHITA"
    s.sun_elevation = math.radians(elev)
    s.sun_rotation = math.radians(rot)
    s.sun_size = math.radians(0.8)
    s.sun_intensity = 0.6
    s.dust_density = dust
    s.air_density = air
    s.ozone_density = ozone
    s.altitude = 50.0
    bg = node(nt, "ShaderNodeBackground", (300, 0), Strength=strength)
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(s.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])


def waves(nt, layers, stretch=(1.0, 2.4, 1.0), distance=0.12, strength=0.7, loc=(-900, 0)):
    """Rüzgâr dalgaları: farklı ölçekte ses dokuları toplanır, bir yönde uzatılır; Bump normali döner."""
    tc = node(nt, "ShaderNodeTexCoord", (loc[0] - 600, loc[1]))
    mp = node(nt, "ShaderNodeMapping", (loc[0] - 400, loc[1]))
    mp.inputs["Scale"].default_value = stretch
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    total = None
    for k, (scale, amp, detail) in enumerate(layers):
        n = node(nt, "ShaderNodeTexNoise", (loc[0] - 200, loc[1] - 220 * k), Scale=scale, Detail=detail,
                 Roughness=0.55)
        nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
        m = node(nt, "ShaderNodeMath", (loc[0], loc[1] - 220 * k))
        m.operation = "MULTIPLY"
        m.inputs[1].default_value = amp
        nt.links.new(n.outputs["Fac"], m.inputs[0])
        if total is None:
            total = m
        else:
            a = node(nt, "ShaderNodeMath", (loc[0] + 150, loc[1] - 220 * k))
            a.operation = "ADD"
            nt.links.new(total.outputs[0], a.inputs[0])
            nt.links.new(m.outputs[0], a.inputs[1])
            total = a
    b = node(nt, "ShaderNodeBump", (loc[0] + 350, loc[1]), Strength=strength, Distance=distance)
    nt.links.new(total.outputs[0], b.inputs["Height"])
    return b


def material(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m, m.node_tree


def plane(name, size, loc=(0, 0, 0), mat=None):
    bpy.ops.mesh.primitive_plane_add(size=size, location=loc)
    ob = bpy.context.object
    ob.name = name
    if mat:
        ob.data.materials.append(mat)
    return ob


def camera(sc, loc, rot, lens):
    cam = bpy.data.cameras.new("kamera")
    cam.lens = lens
    cam.sensor_width = 36
    ob = bpy.data.objects.new("kamera", cam)
    sc.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = [math.radians(a) for a in rot]
    sc.camera = ob
    return ob


# ---------------------------------------------------------------- sahneler

def ufuk(test=False):
    reset()
    sc = setup(*((360, 640) if test else (1080, 1920)), 24 if test else 160, exposure=-0.8)
    sky(sc, elev=30.0, rot=120.0, strength=1.0, dust=0.3, air=1.0, ozone=6.0)  # güneş arkada solda: mavi gök
    m, nt = material("deniz")
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.004, 0.03, 0.045, 1)
    p.inputs["Roughness"].default_value = 0.07
    p.inputs["IOR"].default_value = 1.33
    b = waves(nt, [(0.18, 1.0, 3.0), (1.1, 0.35, 4.0), (6.0, 0.08, 2.0)], stretch=(0.7, 2.0, 1.0),
              distance=0.35, strength=0.55)
    nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    plane("deniz", 40000.0, mat=m)
    camera(sc, (0, 0, 2.2), (88.0, 0, 0), 34)
    return sc


def sig(test=False):
    reset()
    sc = setup(*((360, 450) if test else (1080, 1350)), 24 if test else 192, exposure=-2.6)
    sky(sc, elev=55.0, rot=150.0, strength=0.9, dust=0.6)
    # kum: dalgacıklı, sahte ışık desenli (kırılan güneşin kumdaki ağı)
    m, nt = material("kum")
    p = nt.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = 0.9
    tc = node(nt, "ShaderNodeTexCoord", (-1400, 0))
    warp = node(nt, "ShaderNodeTexNoise", (-1200, -300), Scale=1.6, Detail=2.0)
    nt.links.new(tc.outputs["Object"], warp.inputs["Vector"])
    mix = node(nt, "ShaderNodeMix", (-1000, -200))
    mix.data_type = "VECTOR"
    mix.inputs["Factor"].default_value = 0.9
    nt.links.new(tc.outputs["Object"], mix.inputs["A"])
    nt.links.new(warp.outputs["Color"], mix.inputs["B"])
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.location = (-800, -200)
    vor.feature = "DISTANCE_TO_EDGE"
    vor.inputs["Scale"].default_value = 3.6
    nt.links.new(mix.outputs["Result"], vor.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.location = (-600, -200)
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (1, 1, 1, 1)
    ramp.color_ramp.elements[1].position = 0.028
    ramp.color_ramp.elements[1].color = (0, 0, 0, 1)
    nt.links.new(vor.outputs["Distance"], ramp.inputs["Fac"])
    grain = node(nt, "ShaderNodeTexNoise", (-800, 200), Scale=60.0, Detail=2.0)
    nt.links.new(tc.outputs["Object"], grain.inputs["Vector"])
    sand = nt.nodes.new("ShaderNodeValToRGB")
    sand.location = (-600, 200)
    sand.color_ramp.elements[0].color = (0.62, 0.52, 0.38, 1)
    sand.color_ramp.elements[1].color = (0.80, 0.71, 0.55, 1)
    nt.links.new(grain.outputs["Fac"], sand.inputs["Fac"])
    caus = node(nt, "ShaderNodeMath", (-400, -200))
    caus.operation = "MULTIPLY_ADD"
    caus.inputs[1].default_value = 1.5
    caus.inputs[2].default_value = 0.8
    nt.links.new(ramp.outputs["Color"], caus.inputs[0])
    col = node(nt, "ShaderNodeVectorMath", (-200, 100))
    col.operation = "SCALE"
    nt.links.new(sand.outputs["Color"], col.inputs[0])
    nt.links.new(caus.outputs[0], col.inputs["Scale"])
    # derinlik: kum aşağı indikçe turkuaza, sonra koyu maviye döner (suyun soğurması yerine)
    geo = node(nt, "ShaderNodeNewGeometry", (-600, 800))
    sep = node(nt, "ShaderNodeSeparateXYZ", (-400, 800))
    nt.links.new(geo.outputs["Position"], sep.inputs["Vector"])
    deep = nt.nodes.new("ShaderNodeValToRGB")
    deep.location = (-200, 800)
    els = deep.color_ramp.elements
    els[0].position, els[0].color = 0.0, (0.03, 0.17, 0.25, 1)
    els[1].position, els[1].color = 1.0, (0.55, 0.88, 0.86, 1)
    mid = els.new(0.55)
    mid.color = (0.12, 0.52, 0.6, 1)
    rng = node(nt, "ShaderNodeMapRange", (-300, 650))
    rng.inputs["From Min"].default_value = -1.9
    rng.inputs["From Max"].default_value = -0.5
    nt.links.new(sep.outputs["Z"], rng.inputs["Value"])
    nt.links.new(rng.outputs["Result"], deep.inputs["Fac"])
    tint = nt.nodes.new("ShaderNodeMix")
    tint.location = (0, 300)
    tint.data_type = "RGBA"
    tint.blend_type = "MULTIPLY"
    tint.inputs["Factor"].default_value = 1.0
    nt.links.new(col.outputs["Vector"], tint.inputs["A"])
    nt.links.new(deep.outputs["Color"], tint.inputs["B"])
    nt.links.new(tint.outputs["Result"], p.inputs["Base Color"])
    rip = nt.nodes.new("ShaderNodeTexWave")
    rip.location = (-600, 500)
    rip.inputs["Scale"].default_value = 1.6
    rip.inputs["Distortion"].default_value = 6.0
    rip.inputs["Detail"].default_value = 3.0
    nt.links.new(tc.outputs["Object"], rip.inputs["Vector"])
    bump = node(nt, "ShaderNodeBump", (-300, 500), Strength=0.35, Distance=0.05)
    nt.links.new(rip.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0, 0, -0.9))
    kum = bpy.context.object
    kum.rotation_euler = (math.radians(-14.0), 0, 0)             # yukarı doğru derinleşir
    kum.data.materials.append(m)
    # su: kıran yüzey (renk ve derinlik kumda)
    w, nt = material("su")
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.9, 1.0, 1.0, 1)
    p.inputs["Roughness"].default_value = 0.0
    p.inputs["IOR"].default_value = 1.333
    p.inputs["Transmission Weight"].default_value = 1.0
    b = waves(nt, [(0.6, 1.0, 2.0), (2.2, 0.4, 3.0)], stretch=(1.0, 1.4, 1.0), distance=0.06, strength=0.5)
    nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    su = plane("su", 40.0, mat=w)
    su.visible_shadow = False                                     # güneş kuma ulaşsın (kırılan ışık yolu yerine)
    sun = bpy.data.lights.new("gunes", "SUN")
    sun.energy = 4.5
    sun.angle = math.radians(1.0)
    so = bpy.data.objects.new("gunes", sun)
    sc.collection.objects.link(so)
    so.rotation_euler = (math.radians(32), math.radians(-18), math.radians(25))
    camera(sc, (0, -1.2, 7.0), (10.0, 0, 0), 42)
    return sc


def main():
    test = "--deneme" in sys.argv
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or ["ufuk", "sig"]
    os.makedirs(OUT, exist_ok=True)
    for name in names:
        sc = {"ufuk": ufuk, "sig": sig}[name](test)
        sc.render.filepath = os.path.join(OUT, name + ("_deneme" if test else "") + ".jpg")
        bpy.ops.render.render(write_still=True)
        print("yazıldı:", os.path.relpath(sc.render.filepath, ROOT))


if __name__ == "__main__":
    main()
