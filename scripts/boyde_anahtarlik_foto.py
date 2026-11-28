"""Toptan anahtarlık fotoğrafları (Blender Cycles; scripts/boyde_anahtarlik_toptan.py --foto ile çağrılır).

boyde_urun_foto'nun stüdyo sahnesi ve malzemeleri: koyu anahtarlıklar beyaz fonda, beyaz gövdeli olan logodaki
siyahta (INK). Gövdede 0,2 mm katman izi baskı yönünde (nesnenin z'si); anahtarlık dünyada döndürülse de izler
gövdeyle döner.

Kullanıcı: "arkalı önlü, tek karede iki açıdan görünsün": her model karesinde iki adet; biri ön yüzü (kabartma),
biri arka yüzü (düz yazı) gösterir.

Halka takımı (kullanıcının gönderdiği görseldeki gibi): Ø25 mm çelik halka (iki tur), 4 halkalık zincir (halkalar
sırayla 90° dönük, birbirine geçmiş) ve anahtarlığın deliğinden geçen Ø7 mm ara halka. Her halka bir öncekinin
teline dik; ara halka anahtarlığın yüzüne dik, deliğin en yakın kenarından geçer; anahtarlık deliğinin üst kenarı
ara halkanın teline oturur.

Görünüşler:
  <model>_iki    masada iki adet: biri önden, biri ters çevrilmiş (arka yüz); 3/4 yukarıdan
  <model>_halka  çelik halkalarda asılı iki adet: biri önünü, biri arkasını gösterir
  kapak          12 adet K01 (yarısı önden, yarısı arkadan) ve iki boş halka takımı: toptan parti
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
RING_R, RING_W, RING_P = 12.0, 0.6, 1.3                  # çelik halka: orta yarıçap, tel yarıçapı, tur aralığı (mm)
LINK_S, LINK_E, LINK_W, LINKS = 3.0, 1.9, 0.45, 4         # zincir halkası: düz boy, uç yarıçapı, tel yarıçapı; sayı
JUMP_R, JUMP_W = 3.0, 0.5                                 # ara halka: orta yarıçap, tel yarıçapı
UP = np.array([0.0, 0.0, 1.0])
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


def tube(path, radial, side, r, seg=12):
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


def split_ring(c, a, b, n):
    """Çelik halka (iki tur): merkez c, düzlemi (a, b), turlar n boyunca kayar. Döner: tel ve alt noktası (iki turun
    ortası; b'nin tersi yönünde)."""
    th = np.linspace(0.12, 4 * np.pi - 0.12, 520)
    off = RING_P * th / (2 * np.pi) - RING_P
    radial = np.outer(np.cos(th), a) + np.outer(np.sin(th), b)
    path = c + RING_R * radial + np.outer(off, n)
    bottom = c - RING_R * b + n * (RING_P * 0.75 + RING_P * 1.75 - 2 * RING_P) / 2
    return tube(path, radial, np.tile(n, (len(th), 1)), RING_W), bottom


def link(c, axis, a):
    """Zincir halkası (stadyum biçimi): merkez c, uzun ekseni `axis`, düzlemi (a, axis)."""
    pts, rad = [], []
    half = LINK_S / 2
    for y in np.linspace(-half, half, 12, endpoint=False):           # sağ düz kenar (yukarı)
        pts.append((LINK_E, y)), rad.append((1.0, 0.0))
    for t in np.linspace(0, np.pi, 24, endpoint=False):              # üst yarım daire
        pts.append((LINK_E * np.cos(t), half + LINK_E * np.sin(t))), rad.append((np.cos(t), np.sin(t)))
    for y in np.linspace(half, -half, 12, endpoint=False):           # sol düz kenar (aşağı)
        pts.append((-LINK_E, y)), rad.append((-1.0, 0.0))
    for t in np.linspace(np.pi, 2 * np.pi, 25):                      # alt yarım daire (kapanır)
        pts.append((LINK_E * np.cos(t), -half + LINK_E * np.sin(t))), rad.append((np.cos(t), np.sin(t)))
    pts, rad = np.array(pts), np.array(rad)
    path = c + np.outer(pts[:, 0], a) + np.outer(pts[:, 1], axis)
    radial = np.outer(rad[:, 0], a) + np.outer(rad[:, 1], axis)
    return tube(path, radial, np.tile(np.cross(a, axis), (len(pts), 1)), LINK_W, seg=10)


def jump_ring(c, a, b):
    """Ara halka: merkez c, düzlemi (a, b); ağzı a yönünde (küçük boşluk)."""
    th = np.linspace(0.15, 2 * np.pi - 0.15, 90)
    radial = np.outer(np.cos(th), a) + np.outer(np.sin(th), b)
    return tube(c + JUMP_R * radial, radial, np.tile(np.cross(a, b), (len(th), 1)), JUMP_W, seg=10)


def hang(meta, yaw, top):
    """Asılı duruş: halka takımının tepesi `top` (mm); ön yüz kameraya `yaw` derece dönük (180'e yakınsa arka yüz
    görünür). Çelik halkanın düzlemi anahtarlığın yüzüne paralel; zincir sarkar; ara halka yüze dik, delikten geçer.
    Döner: anahtarlığın M'si (baskı koordinatı -> dünya) ve halka takımının telleri [(V, yüzler)] (dünya, mm)."""
    psi = math.radians(yaw)
    face = np.array([math.sin(psi), -math.cos(psi), 0.0])
    side = np.cross(face, UP)
    top = np.asarray(top, float)
    wires = []
    w, bottom = split_ring(top - UP * RING_R, side, UP, face)
    wires.append(w)
    length = LINK_S + 2 * LINK_E
    c = bottom + UP * (RING_W + LINK_W) - UP * length / 2            # ilk halka çelik halkanın teline asılı
    for i in range(LINKS):
        wires.append(link(c, UP, face if i % 2 == 0 else side))       # sırayla 90° dönük
        end = c - UP * length / 2
        c = c - UP * (length - 2 * LINK_W)
    jc = end + UP * (LINK_W + JUMP_W) - UP * JUMP_R                   # ara halka son halkanın teline asılı
    wires.append(jump_ring(jc, UP, face))
    hole_w = jc - UP * JUMP_R - UP * (meta["delik_r"] - JUMP_W)       # deliğin üst kenarı telin üstünde
    hx, hy = meta["delik"]
    d = np.array(meta["kenar_yonu"] + [0.0])
    n = np.cross(UP, d)
    rot = np.c_[UP, side, face] @ np.c_[d, n, UP].T                   # d -> yukarı, yüz normali -> face
    h = np.array([hx, hy, meta["kalinlik"] / 2])
    return np.c_[rot, hole_w - rot @ h], wires


def loose_set(x, y, angle):
    """Masada yatan boş halka takımı: çelik halka düz, zincir `angle` yönünde uzanır (halkalar sırayla yatık ve
    yan yatmış), ucunda yatık ara halka."""
    a = math.radians(angle)
    u = np.array([math.cos(a), math.sin(a), 0.0])
    v = np.cross(UP, u)
    wires = []
    w, _ = split_ring(np.array([x, y, RING_W + RING_P]), u, v, UP)
    wires.append(w)
    length = LINK_S + 2 * LINK_E
    p = np.array([x, y, 0.0]) + u * (RING_R - RING_W - LINK_W)        # ilk halkanın ucu çelik halkanın telinde
    for i in range(LINKS):
        upright = i % 2 == 0
        c = p + u * length / 2 + UP * ((LINK_E + LINK_W) if upright else LINK_W)
        wires.append(link(c, u, UP if upright else v))
        p = p + u * (length - 2 * LINK_W)
    wires.append(jump_ring(np.array([p[0], p[1], JUMP_W]) + u * (JUMP_R - JUMP_W - LINK_W), u, v))
    return wires


def put_wires(wires, name, shift=(0.0, 0.0, 0.0)):
    I = np.c_[np.eye(3), shift]
    return np.vstack([add(f"{name}_{i}", V, fc, steel(), I, smooth=True) for i, (V, fc) in enumerate(wires)])


def world(parts, M):
    """Anahtarlığın dünyadaki noktaları (mm): yerleşim hesabı için (sahneye eklemeden)."""
    return np.vstack([V for V, _, _, _ in parts]) @ M[:, :3].T + M[:, 3]


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


def halo(pts, energy=45.0):
    """Siyah fonda koyu parçalar kaybolmasın: parçaların hemen arkasında fona bakan yumuşak kenarlı spot; fonda hafif
    hale olur, parçalar önünde siluet ve kenar ışığıyla ayrılır. Işık kameraya görünmez."""
    c, top = pts.mean(0), pts.max(0)
    li = bpy.data.lights.new("hale", "SPOT")
    li.energy, li.color = energy, (1.0, 0.97, 0.93)
    li.spot_size, li.spot_blend, li.shadow_soft_size = math.radians(110), 1.0, 0.08
    ob = bpy.data.objects.new("hale", li)
    ob.location = (c[0], top[1] + 0.04, c[2])
    R.look_at(ob, (c[0], top[1] + 1.0, c[2] + 0.3))
    ob.visible_camera = False
    bpy.context.scene.collection.objects.link(ob)


def shoot(sc, corners, az, el, fill, fstop, path, dark, lens=85, glow=False):
    cam = F.camera(sc, lens)
    a, e = math.radians(az), math.radians(el)
    direction = np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])
    cam["dir"] = direction.tolist()
    res = sc.render
    F.frame(cam, corners, res.resolution_x / res.resolution_y, fill)
    cam.data.dof.aperture_fstop = fstop
    F.lights(sc, corners.mean(0), direction, "studyo")
    if glow:
        halo(corners)
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


def model_shots(key, samples, views=("iki", "halka")):
    meta, parts = load(key)
    dark = light_body(parts)
    w = max(np.ptp(V[:, 0]) for V, _, _, _ in parts)
    h = max(np.ptp(V[:, 1]) for V, _, _, _ in parts)
    big = max(w, h)
    # masada: önde ön yüz, arkada ters çevrilmiş (arka yüz)
    sc = studio(dark, samples, F.SIZE)
    axis, side = (1, 0) if w > 1.4 * h else (0, 1)          # uzunsa üst üste, değilse yan yana dizilir
    shift = np.zeros(2)
    shift[side] = big * 0.1
    Mf, Mb = flat(meta, -8, 0, 0), flat(meta, 10, 0, 0, flip=True)
    allv = np.vstack([V for V, _, _, _ in parts])
    lo_f, hi_f = (lambda q: (q.min(), q.max()))((allv @ Mf[:2, :3].T + Mf[:2, 3])[:, axis])
    lo_b, hi_b = (lambda q: (q.min(), q.max()))((allv @ Mb[:2, :3].T + Mb[:2, 3])[:, axis])
    move = hi_f - lo_b + 7.0                                 # aralarında 7 mm boşluk
    Mb[axis, 3] += move
    Mb[side, 3] += shift[side]
    Mf[side, 3] -= shift[side]
    centre = (lo_f + hi_b + move) / 2
    Mf[axis, 3] -= centre
    Mb[axis, 3] -= centre
    pts = np.vstack([put(parts, Mf, "on"), put(parts, Mb, "arka")])
    if "iki" in views:
        shoot(sc, pts, 14, 50, 0.74, 4.5, os.path.join(T.FOTO, f"{key}_iki.jpg"), dark)
    if "halka" not in views:
        return
    # halka takımında asılı: solda ön yüz, sağda arka yüz; aralarında 10 mm (gerçek enlerine göre)
    sc = studio(dark, samples, F.SIZE)
    sets = [hang(meta, yaw, (0, 0, 0)) for yaw in (22, 180 - 22)]
    spans = []
    for M, wires in sets:
        q = np.vstack([world(parts, M)] + [V for V, _ in wires])[:, 0]
        spans.append((q.min(), q.max()))
    move = spans[0][1] - spans[1][0] + 10.0
    centre = (spans[0][0] + spans[1][1] + move) / 2
    groups = []
    for (M, wires), dx, name in zip(sets, (-centre, move - centre), ("on", "arka")):
        M = M.copy()
        M[0, 3] += dx
        groups += [put(parts, M, f"anahtarlik_{name}"), put_wires(wires, f"halka_{name}", (dx, 0, 0))]
    pts = lift_all(np.vstack(groups), 0.016)
    shoot(sc, pts, 0, 7, 0.78, 6.3, os.path.join(T.FOTO, f"{key}_halka.jpg"), dark)


def cover(samples, size=(1600, 1600)):
    """Toptan parti: 12 adet K01 4 × 3 dizili (yarısı önden, yarısı arkadan), hafif dönük; yanında iki boş halka
    takımı."""
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
    for k, (x, y, a) in enumerate(((-1.5 * w - 32.0, -h * 0.4, -100.0), (1.5 * w + 32.0, h * 0.4, 80.0))):
        pts.append(put_wires(loose_set(x, y, a), f"takim{k}"))                     # dizinin dışında
    shoot(sc, np.vstack(pts), -12, 42, 0.96, 6.3, os.path.join(T.FOTO, "kapak.jpg"), False, lens=70)


def lineup(samples, size=(1800, 1000), dark=False):
    """Beş model halka takımlarıyla yan yana asılı (önden); çelik halkaların tepesi aynı yükseklikte. dark: siyah fon,
    arkada hale (siyah anahtarlık fonda kaybolmasın)."""
    sc = studio(dark, samples, size)
    loaded = [load(k) for k in T.KEYS]
    sets = [hang(meta, (-16, 12, -8, 14, -14)[k], (0, 0, 0)) for k, (meta, _) in enumerate(loaded)]
    spans = []
    for (M, wires), (_, parts) in zip(sets, loaded):
        q = np.vstack([world(parts, M)] + [V for V, _ in wires])[:, 0]
        spans.append((q.min(), q.max()))
    xs, x = [], 0.0
    for lo, hi in spans:                                                    # aralarında 12 mm
        xs.append(x - lo)
        x += hi - lo + 12.0
    xs = np.array(xs) - (x - 12.0) / 2
    groups = []
    for k, ((M, wires), (_, parts), dx) in enumerate(zip(sets, loaded, xs)):
        M = M.copy()
        M[0, 3] += dx
        groups += [put(parts, M, f"anahtarlik{k}"), put_wires(wires, f"halka{k}", (dx, 0, 0))]
    pts = lift_all(np.vstack(groups), 0.02)
    shoot(sc, pts, 0, 6, 0.88, 8.0, os.path.join(T.FOTO, "dizi.jpg"), dark, glow=dark)


def main(args):
    """args: model anahtarları, kapak, dizi (boşsa hepsi); --ornek N (örnek sayısı), --deneme (küçük çizim),
    --yalniz iki|halka (modellerde yalnız o görünüş)."""
    samples = 32
    if "--ornek" in args:
        samples = int(args[args.index("--ornek") + 1])
    small = "--deneme" in args
    if small:
        F.SIZE = (500, 500)
    os.makedirs(T.FOTO, exist_ok=True)
    views = ("iki", "halka")
    if "--yalniz" in args:
        views = (args.pop(args.index("--yalniz") + 1),)
    keys = [a for a in args if not a.startswith("-") and not a.isdigit()]
    every = not keys
    for key in T.KEYS:
        if every or key in keys:
            model_shots(key, samples, views)
    if every or "kapak" in keys:
        cover(samples, (600, 600) if small else (1600, 1600))
    if every or "dizi" in keys:
        lineup(samples, (720, 400) if small else (1800, 1000))
