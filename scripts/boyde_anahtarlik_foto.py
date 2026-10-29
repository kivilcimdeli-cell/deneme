"""Toptan anahtarlık fotoğrafları (Blender Cycles; scripts/boyde_anahtarlik_toptan.py --foto ile çağrılır).

boyde_urun_foto'nun stüdyo sahnesi ve malzemeleri: koyu anahtarlıklar beyaz fonda, beyaz gövdeli olan logodaki
siyahta (INK). Gövdede 0,2 mm katman izi baskı yönünde (nesnenin z'si); anahtarlık dünyada döndürülse de izler
gövdeyle döner.

Kullanıcı: "arkalı önlü, tek karede iki açıdan görünsün": her model karesinde iki adet; biri ön yüzü (kabartma),
biri arka yüzü (düz yazı) gösterir.

Çelik halka (split ring): Ø25 mm, 1,4 mm tel, iki tur. İki tur da anahtarlığın deliğinden geçer (gerçekte de
anahtarlık iki teli birden sarar); halka düzlemi anahtarlığın yüzüne dik.

Görünüşler:
  <model>_iki    masada iki adet: biri önden, biri ters çevrilmiş (arka yüz); 3/4 yukarıdan
  <model>_halka  çelik halkalarda asılı iki adet: biri önünü, biri arkasını gösterir
  kapak          12 adet K01 (yarısı önden, yarısı arkadan) ve iki boş halka: toptan parti
  dizi           beş model halkalarıyla yan yana asılı (önden)
"""
import json
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_anahtarlik_toptan as T  # noqa: E402
import boyde_urun_foto as F  # noqa: E402
import restoran_masalik_foto as R  # noqa: E402

MM = F.MM
RING_R, WIRE_R, PITCH = 12.0, 0.7, 1.5                  # halka: orta yarıçap, tel yarıçapı, tur aralığı (mm)
DOYGUNLUK = 0.2                                         # AgX renkleri soldurur: renkli yüzeyler biraz doyurulur


def load(key):
    z = np.load(os.path.join(T.SRC, f"{key}.npz"))
    meta = json.loads(str(z["meta"]))
    parts = [(z[f"v{i}"].astype(float), z[f"f{i}"], p["renk"], p["metal"]) for i, p in enumerate(meta["parcalar"])]
    return meta, parts


def light_body(parts):
    return sum(parts[0][2]) / 3 > 150


_STEEL = []


def steel():
    if not _STEEL:
        m = bpy.data.materials.new("celik")
        m.use_nodes = True
        bs = m.node_tree.nodes["Principled BSDF"]
        bs.inputs["Base Color"].default_value = R.srgb((206, 207, 212))
        bs.inputs["Metallic"].default_value = 1.0
        bs.inputs["Roughness"].default_value = 0.2
        _STEEL.append(m)
    return _STEEL[0]


def add(name, V, faces, material, M, smooth=False):
    """V: mm (nesnenin kendi koordinatları); M: 3 × 4 (mm), nesneyi dünyaya koyar. Döner: dünyadaki noktalar (m)."""
    me = bpy.data.meshes.new(name)
    me.from_pydata((V * MM).tolist(), [], [tuple(int(i) for i in f) for f in faces])
    me.update()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(material)
    Mx = np.eye(4)
    Mx[:3, :4] = M
    Mx[:3, 3] *= MM
    ob.matrix_world = Matrix(Mx.tolist())
    bpy.context.scene.collection.objects.link(ob)
    return (V @ M[:, :3].T + M[:, 3]) * MM


def put(parts, M, name):
    return np.vstack([add(f"{name}_{i}", V, Fc, F.mat(rgb, metal, layers=True), M)
                      for i, (V, Fc, rgb, metal) in enumerate(parts)])


def tube(path, radial, side, r=WIRE_R, seg=12):
    """Yol boyunca tel: path (N × 3), radial ve side kesitin iki ekseni (N × 3); uçlar kapalı."""
    phi = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    V = (path[:, None, :] + r * (np.cos(phi)[None, :, None] * radial[:, None, :]
                                 + np.sin(phi)[None, :, None] * side[:, None, :])).reshape(-1, 3)
    n = len(path)
    faces = [(i * seg + j, i * seg + (j + 1) % seg, (i + 1) * seg + (j + 1) % seg, (i + 1) * seg + j)
             for i in range(n - 1) for j in range(seg)]
    V = np.vstack([V, path[0], path[-1]])
    c0, c1 = len(V) - 2, len(V) - 1
    faces += [(c0, (j + 1) % seg, j) for j in range(seg)]
    faces += [(c1, (n - 1) * seg + j, (n - 1) * seg + (j + 1) % seg) for j in range(seg)]
    return V, faces


def ring_hole_frame():
    """Halka, deliğin çerçevesinde (a: delikten dışa, b: yüzde a'ya dik, c: yüz normali); iki tur da delikten geçer."""
    th = np.linspace(0.12, 4 * np.pi - 0.12, 520)
    off = PITCH * th / (2 * np.pi) - PITCH
    path = np.c_[RING_R * (1 + np.cos(th)), off, RING_R * np.sin(th)]
    radial = np.c_[np.cos(th), np.zeros_like(th), np.sin(th)]
    return tube(path, radial, np.tile([0.0, 1.0, 0.0], (len(th), 1)))


def ring_flat():
    """Masada yatan boş halka (eksen düşey), alt yüzü z = 0'da."""
    th = np.linspace(0.12, 4 * np.pi - 0.12, 520)
    path = np.c_[RING_R * np.cos(th), RING_R * np.sin(th), WIRE_R + PITCH * th / (2 * np.pi)]
    radial = np.c_[np.cos(th), np.sin(th), np.zeros_like(th)]
    return tube(path, radial, np.tile([0.0, 0.0, 1.0], (len(th), 1)))


def hang(meta, yaw, top):
    """Asılı duruş: delik yukarıda, ön yüz kameraya `yaw` derece dönük (180'e yakınsa arka yüz görünür); halkanın
    tepesi `top` noktasında (mm). Döner: anahtarlığın M'si (baskı koordinatı -> dünya), halkanın M'si."""
    hx, hy = meta["delik"]
    cx, cy = meta["merkez"]
    d = np.array([hx - cx, hy - cy, 0.0])
    d /= np.linalg.norm(d)
    n = np.cross([0, 0, 1.0], d)
    psi = math.radians(yaw)
    face = np.array([math.sin(psi), -math.cos(psi), 0.0])
    up = np.array([0, 0, 1.0])
    Rw = np.c_[up, np.cross(face, up), face]
    rot = Rw @ np.c_[d, n, up].T
    h = np.array([hx, hy, meta["kalinlik"] / 2])
    origin = np.asarray(top, float) - up * (2 * RING_R + WIRE_R)   # halkanın tepesi deliğin 2R üstünde
    return np.c_[rot, origin - rot @ h], np.c_[Rw, origin]


def flat(meta, alpha, x, y, flip=False):
    """Masada yatık, merkezi (x, y)'de, z ekseni etrafında `alpha` derece; flip: soldan sağa çevrilmiş (arka yüz
    yukarıda, kabartma masada)."""
    a = math.radians(alpha)
    rot = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
    z0 = 0.0
    if flip:
        rot = rot @ np.diag([-1.0, 1.0, -1.0])
        z0 = meta["toplam"]
    c = np.array(meta["merkez"] + [0.0])
    return np.c_[rot, np.array([x, y, z0]) - rot @ c]


def studio(dark, samples, size):
    sc = F.scene("studyo", samples, size, dark=dark)
    sc.view_settings.exposure = -0.15 if dark else -0.3
    if not dark:
        sc.view_settings.look = F.BAKIS
    _STEEL.clear()
    return sc


def lift_all(pts, clearance):
    """Asılı sahne: en alt nokta yerden `clearance` metre yukarıda (yere gölge düşer)."""
    dz = clearance - pts[:, 2].min()
    for ob in bpy.context.scene.collection.objects:
        if ob.type == "MESH" and ob.name != "fon":
            ob.location.z += dz
    pts[:, 2] += dz
    return pts


def shoot(sc, corners, az, el, fill, fstop, path, dark, lens=85):
    cam = F.camera(sc, lens)
    a, e = math.radians(az), math.radians(el)
    direction = np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])
    cam["dir"] = direction.tolist()
    res = sc.render
    F.frame(cam, corners, res.resolution_x / res.resolution_y, fill)
    cam.data.dof.aperture_fstop = fstop
    F.lights(sc, corners.mean(0), direction, "studyo")
    F.shoot(sc, path, F.KOYU if dark else F.BEYAZ)
    saturate(path)


def saturate(path, k=DOYGUNLUK):
    """Seçici doygunluk: yalnız renkli yüzeyler; fon, siyah, beyaz, gri ve çelik değişmez."""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    h, s, v = [np.asarray(c, float) for c in im.convert("HSV").split()]
    w = np.clip((s - 50) / 40, 0, 1) * np.clip((v - 40) / 40, 0, 1)
    s = np.clip(s * (1 + k * w), 0, 255)
    Image.merge("HSV", [Image.fromarray(x.astype(np.uint8)) for x in (h, s, v)]).convert("RGB").save(path, quality=92)


def model_shots(key, samples):
    meta, parts = load(key)
    dark = light_body(parts)
    w = max(np.ptp(V[:, 0]) for V, _, _, _ in parts)
    h = max(np.ptp(V[:, 1]) for V, _, _, _ in parts)
    big = max(w, h)
    # masada: önde ön yüz, arkada ters çevrilmiş (arka yüz)
    sc = studio(dark, samples, F.SIZE)
    wide = w > 1.4 * h
    dx, dy = (big * 0.08, big * 0.36) if wide else (big * 0.36, big * 0.12)
    pts = np.vstack([put(parts, flat(meta, -8, -dx, -dy), "on"),
                     put(parts, flat(meta, 10, dx, dy, flip=True), "arka")])
    shoot(sc, pts, 14, 50, 0.74, 4.5, os.path.join(T.FOTO, f"{key}_iki.jpg"), dark)
    # halkalarda asılı: solda ön yüz, sağda arka yüz
    sc = studio(dark, samples, F.SIZE)
    hx, hy = meta["delik"]
    cx, cy = meta["merkez"]
    hang_w = h if abs(hx - cx) > abs(hy - cy) else w        # asılıyken eni: delik yandaysa boyu
    gap = hang_w / 2 + 8.0
    groups = []
    for x, yaw, name in ((-gap, 22, "on"), (gap, 180 - 22, "arka")):
        M, Mr = hang(meta, yaw, (x, 0, 0))
        V, faces = ring_hole_frame()
        groups += [put(parts, M, f"anahtarlik_{name}"), add(f"halka_{name}", V, faces, steel(), Mr, smooth=True)]
    pts = lift_all(np.vstack(groups), 0.016)
    shoot(sc, pts, 0, 7, 0.76, 6.3, os.path.join(T.FOTO, f"{key}_halka.jpg"), dark)


def cover(samples, size=(1600, 1600)):
    """Toptan parti: 12 adet K01 4 × 3 dizili (yarısı önden, yarısı arkadan), hafif dönük; yanında iki boş halka."""
    sc = studio(False, samples, size)
    meta, parts = load(T.KEYS[0])
    w, h = (np.ptp(np.vstack([V for V, _, _, _ in parts])[:, i]) for i in (0, 1))
    rng = np.random.default_rng(11)
    pts = []
    for k in range(12):
        i, j = k % 3, k // 3
        x = (i - 1) * (w + 7.0) + (5.0 if j % 2 else -5.0)
        y = (1.5 - j) * (h + 7.0)
        flip = (i + j) % 2 == 1
        pts.append(put(parts, flat(meta, float(rng.uniform(-6, 6)), x, y, flip), f"k{k}"))
    V, faces = ring_flat()
    for x, y in ((-1.5 * w - 32.0, -h * 0.9), (1.5 * w + 32.0, h * 0.7)):     # dizinin dışında
        pts.append(add("halka", V, faces, steel(), np.c_[np.eye(3), [x, y, 0.0]], smooth=True))
    shoot(sc, np.vstack(pts), -12, 42, 0.96, 6.3, os.path.join(T.FOTO, "kapak.jpg"), False, lens=70)


def lineup(samples, size=(1800, 1000)):
    """Beş model halkalarıyla yan yana asılı (önden); halkaların tepesi aynı yükseklikte."""
    sc = studio(False, samples, size)
    loaded = [load(k) for k in T.KEYS]
    widths = []
    for meta, parts in loaded:
        (hx, hy), (cx, cy) = meta["delik"], meta["merkez"]
        V = np.vstack([V for V, _, _, _ in parts])
        widths.append(np.ptp(V[:, 1]) if abs(hx - cx) > abs(hy - cy) else np.ptp(V[:, 0]))
    gap = 16.0
    xs = np.cumsum([0.0] + [(a + b) / 2 + gap for a, b in zip(widths, widths[1:])])
    xs -= xs.mean()
    groups = []
    for k, ((meta, parts), x) in enumerate(zip(loaded, xs)):
        M, Mr = hang(meta, (-16, 12, -8, 14, -14)[k], (x, 0, 0))
        V, faces = ring_hole_frame()
        groups += [put(parts, M, f"anahtarlik{k}"), add(f"halka{k}", V, faces, steel(), Mr, smooth=True)]
    pts = lift_all(np.vstack(groups), 0.02)
    shoot(sc, pts, 0, 6, 0.88, 8.0, os.path.join(T.FOTO, "dizi.jpg"), False)


def main(args):
    """args: model anahtarları, kapak, dizi (boşsa hepsi); --ornek N (örnek sayısı), --deneme (küçük çizim)."""
    samples = 32
    if "--ornek" in args:
        samples = int(args[args.index("--ornek") + 1])
    small = "--deneme" in args
    if small:
        F.SIZE = (500, 500)
    os.makedirs(T.FOTO, exist_ok=True)
    keys = [a for a in args if not a.startswith("-") and not a.isdigit()]
    every = not keys
    for key in T.KEYS:
        if every or key in keys:
            model_shots(key, samples)
    if every or "kapak" in keys:
        cover(samples, (600, 600) if small else (1600, 1600))
    if every or "dizi" in keys:
        lineup(samples, (720, 400) if small else (1800, 1000))
