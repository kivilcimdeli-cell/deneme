"""BOYDE LABS – ürün fotoğrafları (Blender Cycles): katalog ve Shopier için.

scripts/boyde_urunler.py'nin dışa aktardığı modeller (boyde_labs/urunler/kaynak/<ürün>.npz: sehpasında duran panel ve
sehpa) restoran_masalik_foto.py'nin malzemeleriyle çizilir: mat PLA, panel yüzünde katman izi yok (yüzü yukarı
basılır), sehpada 0,2 mm katman izi, kenarlarda yumuşak ışık.

Görünüşler (kare, 1200 × 1200; Shopier için yeterli, bir ürün ~4 dk):
  studyo  beyaz stüdyo fonu (kıvrık fon), 3/4 sağdan
  on      aynı fon, karşıdan: yazılar okunur
  masa    beyaz masa (az parlak, yansıma verir), 3/4 soldan, arkası bulanık
Kapak (--kapak): her kategoriden birkaç isimlik yan yana, beyaz masada (kategori kapağı, katalog).
Zeminler beyaz (kullanıcı: "kahverengi arka planları sil, hepsini beyaz yap"); çizimden sonra seviye ayarı (whiten).

Çıktı : boyde_labs/urunler/fotograf/<ürün>_<görünüş>.jpg, kapak_<kategori>.jpg

Kullanım:
  pip install bpy==4.2.0
  python3 scripts/boyde_urunler.py                       # önce modeller
  python3 scripts/boyde_urun_foto.py [ürün ...] [--gorunus studyo,on,masa] [--ornek 32] [--eksik]
  python3 scripts/boyde_urun_foto.py --kapak
"""
import json
import math
import os
import sys
import time

import bpy
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import restoran_masalik_foto as R  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "boyde_labs", "urunler", "kaynak")
OUT = os.path.join(ROOT, "boyde_labs", "urunler", "fotograf")
MM = R.MM
SIZE = (1200, 1200)
FON = (246, 246, 244)                                    # beyaz fon ("kahverengi arka planları sil, hepsini beyaz yap")
MASA = (244, 244, 242)                                   # beyaz masa (eskiden ahşap)
GLOW = {"studyo": 1.2, "masa": 0.7, "duvar": 1.2}       # beyaz yüzeylerin hafif ışıması: gölgede griye dönmesin
BEYAZ = 248                                              # fonun son hâli (whiten)
VIEWS = {"studyo": ("studyo", 30.0, 12.0), "on": ("studyo", 0.0, 7.0), "masa": ("masa", -28.0, 11.0)}
KAPAK = {"9x12": [["telefon", "kuafor", "kuyumcu"], ["uzar", "emlak"]],
         "10x20": [["avukat", "paloma"], ["musavir"]]}


def load(key):
    z = np.load(os.path.join(SRC, f"{key}.npz"))
    meta = json.loads(str(z["meta"]))
    return [(m, z[f"v{i}"], z[f"f{i}"]) for i, m in enumerate(meta)]


_MATS = {}


def mat(rgb, metal, layers):
    k = (tuple(rgb), metal, layers)
    if k not in _MATS:
        _MATS[k] = R.material(f"pla_{len(_MATS)}", tuple(rgb), metal=metal, layers=layers)
    return _MATS[k]


def add(name, V, F, m, shift=(0.0, 0.0, 0.0)):
    me = bpy.data.meshes.new(name)
    me.from_pydata(((V + np.asarray(shift)) * MM).tolist(), [], F.tolist())
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(m)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def white(name, rgb, rough, glow):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bs = m.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = R.srgb(rgb)
    bs.inputs["Roughness"].default_value = rough
    bs.inputs["Emission Color"].default_value = R.srgb(rgb)
    bs.inputs["Emission Strength"].default_value = glow
    return m


def scene(kind, samples, size, glow=1.0):
    """studyo: beyaz kıvrık fon (sonsuz fon); masa: restoran_masalik_foto'nun masası ve duvarları, beyaz (az parlak
    masa, mat duvar)."""
    R.SIZE = size
    _MATS.clear()
    sc = R.setup_scene(samples)
    R._MATS.clear()
    bg = sc.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = R.srgb(FON)
    if kind == "masa":
        ob = bpy.data.objects["masa"]
        ob.data.materials[0] = white("masa_beyaz", MASA, 0.32, GLOW["masa"] * glow)
        wm = white("duvar_beyaz", FON, 0.9, GLOW["duvar"] * glow)
        for name in ("duvar0", "duvar1"):
            bpy.data.objects[name].data.materials[0] = wm
    if kind == "studyo":
        for name in ("masa", "duvar0", "duvar1"):
            bpy.data.objects.remove(bpy.data.objects[name])
        prof = [(-3.0, 0.0)] + [(0.2 + 0.35 * math.sin(a), 0.35 - 0.35 * math.cos(a))
                                for a in np.linspace(0, math.pi / 2, 24)] + [(0.55, 3.0)]
        verts, faces = [], []
        for x in (-3.0, 3.0):
            verts += [(x, y, z) for y, z in prof]
        n = len(prof)
        faces = [(i, i + 1, n + i + 1, n + i) for i in range(n - 1)]
        me = bpy.data.meshes.new("fon")
        me.from_pydata(verts, [], faces)
        for p in me.polygons:
            p.use_smooth = True
        ob = bpy.data.objects.new("fon", me)
        ob.data.materials.append(white("fon", FON, 0.9, GLOW["studyo"] * glow))
        sc.collection.objects.link(ob)
        bg.inputs["Strength"].default_value = 0.35
    return sc


def frame(cam, corners, aspect, fill):
    """Köşeler kadrajın `fill` oranına sığacak uzaklık (perspektif)."""
    tan_v = math.tan(cam.data.angle / 2) if cam.data.sensor_fit == "VERTICAL" else math.tan(cam.data.angle / 2) / aspect
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
        dist *= need / fill
    cam.location = tuple(centre + direction * dist)
    R.look_at(cam, tuple(centre))
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = float(dist)
    return dist


def lights(sc, centre, direction, kind, k=1.0):
    for ob in [o for o in sc.collection.objects if o.type == "LIGHT"]:
        bpy.data.objects.remove(ob)
    r = 0.9
    right = np.cross(-direction, [0, 0, 1])
    right /= np.linalg.norm(right)
    flat = direction * [1, 1, 0]
    flat /= np.linalg.norm(flat)
    if kind == "studyo":                                 # büyük yumuşak ışık önden solda, dolgu sağda, arka ışık
        R.light("ana", 34.0 * k, 1.3, centre + r * (0.75 * flat - 0.65 * right) + [0, 0, 0.75], centre,
                (1.0, 0.98, 0.95))
        R.light("dolgu", 9.0 * k, 1.4, centre + r * (0.8 * flat + 0.8 * right) + [0, 0, 0.3], centre, (0.95, 0.97, 1.0))
        R.light("arka", 14.0 * k, 0.6, centre - r * flat + r * 0.4 * right + [0, 0, 0.8], centre, (1.0, 0.96, 0.9))
    else:                                                # ana ışık yanda: kabartma gölge atar
        R.light("ana", 24.0 * k, 0.9, centre + r * (0.45 * flat - 0.85 * right) + [0, 0, 0.8], centre,
                (1.0, 0.97, 0.93))
        R.light("dolgu", 6.0 * k, 1.0, centre + r * (0.9 * flat + 0.7 * right) + [0, 0, 0.25], centre,
                (0.93, 0.96, 1.0))
        R.light("arka", 12.0 * k, 0.4, centre - r * flat + r * 0.5 * right + [0, 0, 0.7], centre, (1.0, 0.95, 0.88))


def place(parts, shift=(0.0, 0.0, 0.0)):
    """Parçaları sahneye koyar; döner: sınır kutusunun köşeleri (m)."""
    lo, hi = np.full(3, 1e9), np.full(3, -1e9)
    for m, V, F in parts:
        add(m["ad"], V, F, mat(m["renk"], m["metal"], layers=not m["panel"]), shift)
        lo = np.minimum(lo, V.min(0) + shift)
        hi = np.maximum(hi, V.max(0) + shift)
    lo, hi = lo * MM, hi * MM
    return np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])


def camera(sc, lens=85):
    cd = bpy.data.cameras.new("kamera")
    cd.lens = lens
    cd.sensor_fit = "VERTICAL"
    cam = bpy.data.objects.new("kamera", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    return cam


def whiten(src, dst, target=BEYAZ):
    """Seviye ayarı: kenarlardaki fon (üst, sol, sağ şerit) `target` beyazına çekilir; koyular neredeyse değişmez.
    Cycles'ta beyaz fon AgX'le açık griye düşer; fotoğrafçının "beyaz noktası"."""
    from PIL import Image
    im = np.asarray(Image.open(src).convert("RGB")).astype(float)
    edge = np.concatenate([im[:12].reshape(-1, 3), im[:, :12].reshape(-1, 3), im[:, -12:].reshape(-1, 3)])
    bg = np.median(edge, 0)
    out = np.clip(im * (target / bg) + 0.5, 0, 255).astype(np.uint8)
    Image.fromarray(out).save(dst, quality=92)
    os.remove(src)


def shoot(sc, path, target=BEYAZ):
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = path[:-4] + "_ham.png"
    t = time.time()
    bpy.ops.render.render(write_still=True)
    whiten(sc.render.filepath, path, target)
    print(f"{os.path.basename(path)[:-4]}: {time.time() - t:.0f} sn", flush=True)


def light_body(parts):
    """Gövdesi açık renkli mi (pozlama: beyaz yüz soluklaşmasın)."""
    body = parts[0][0]["renk"]
    return sum(body) / 3 > 150


def render(key, views, samples, missing=False):
    """missing: yalnız henüz çizilmemiş görünüşler."""
    if missing:
        views = [v for v in views if not os.path.exists(os.path.join(OUT, f"{key}_{v}.jpg"))]
        if not views:
            return
    parts = load(key)
    os.makedirs(OUT, exist_ok=True)
    by_kind = {}
    for v in views:
        by_kind.setdefault(VIEWS[v][0], []).append(v)
    light = light_body(parts)
    for kind, vs in by_kind.items():                     # açık gövde: fon az ışır, gövde fondan açık kalır (kenarı seçilir)
        sc = scene(kind, samples, SIZE, 0.5 if light else 1.0)
        sc.view_settings.exposure = -0.55 if light else -0.3
        box = place(parts)
        cam = camera(sc)
        centre = box.mean(0)
        for v in vs:
            _, az, el = VIEWS[v]
            a, e = math.radians(az), math.radians(el)
            direction = np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])
            cam["dir"] = direction.tolist()
            frame(cam, box, SIZE[0] / SIZE[1], 0.78 if v == "on" else 0.72)
            cam.data.dof.aperture_fstop = 5.6 if kind == "studyo" else 3.5
            lights(sc, centre, direction, kind)
            shoot(sc, os.path.join(OUT, f"{key}_{v}.jpg"), 242 if light else BEYAZ)


def cover(cat, samples, size=(1600, 1600)):
    """Kategori kapağı: arka sırada üç, ön sırada iki isimlik (beyaz masa)."""
    sc = scene("masa", samples, size, 0.8)
    sc.view_settings.exposure = -0.45
    rows = KAPAK[cat]
    corners = []
    for r, keys in enumerate(rows):
        loaded = [load(k) for k in keys]
        widths = [max(V[:, 0].max() for _, V, _ in p) - min(V[:, 0].min() for _, V, _ in p) for p in loaded]
        gap = 22.0 if cat == "9x12" else 50.0
        x = -(sum(widths) + gap * (len(widths) - 1)) / 2
        y = 0.0 if r == 0 else -125.0 if cat == "9x12" else -150.0          # sıralar arası: arkadakiler görünsün
        for p, w in zip(loaded, widths):
            x0 = min(V[:, 0].min() for _, V, _ in p)
            yc = np.mean([V[:, 1].mean() for _, V, _ in p])
            corners.append(place(p, (x - x0, y - yc, 0.0)))
            x += w + gap
    box = np.vstack(corners)
    cam = camera(sc, 70)
    a, e = math.radians(-10.0), math.radians(25.0)
    direction = np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])
    cam["dir"] = direction.tolist()
    frame(cam, box, size[0] / size[1], 0.86)
    cam.data.dof.aperture_fstop = 6.3
    lights(sc, box.mean(0), direction, "masa", 1.8)
    shoot(sc, os.path.join(OUT, f"kapak_{cat}.jpg"), 246)


def main():
    args = sys.argv[1:]
    samples = 32
    views = list(VIEWS)
    if "--ornek" in args:
        k = args.index("--ornek")
        samples = int(args[k + 1])
        del args[k:k + 2]
    if "--gorunus" in args:
        k = args.index("--gorunus")
        views = args[k + 1].split(",")
        del args[k:k + 2]
    missing = "--eksik" in args
    args = [a for a in args if a != "--eksik"]
    if "--kapak" in args:
        for cat in KAPAK:
            cover(cat, samples)
        return
    keys = args or sorted(f[:-4] for f in os.listdir(SRC) if f.endswith(".npz"))
    for key in keys:
        render(key, views, samples, missing)


if __name__ == "__main__":
    main()
