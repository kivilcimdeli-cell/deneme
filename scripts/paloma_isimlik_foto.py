"""PALOMA GRIDA isimliği (200 × 100 mm, sehpasında) – sunum fotoğrafı (Blender Cycles), yazısız.

Baskı dosyasındaki modelin aynısı (scripts/paloma_isimlik_baski.py) ahşap masa üstünde, stüdyo ışığında çizilir
(restoran_masalik_foto.py'nin sahnesi ve malzemeleri): beyaz PLA panel ve sehpa, siyah ad soyad ve QR, Paloma
mavisi kart; arkası alan derinliğiyle bulanık.

Çıktı : paloma_isimlik/foto/isimlik_on.jpg (3/4 önden), isimlik_karsi.jpg (karşıdan)

Kullanım:
  pip install bpy==4.2.0
  python3 scripts/paloma_isimlik_foto.py [--ornek 128]
"""
import math
import os
import sys

import bpy
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import paloma_isimlik as P  # noqa: E402
import paloma_isimlik_baski as PB  # noqa: E402  (panel ölçüsünü 200 × 100 × 5 yapar)
import restoran_masalik_foto as R  # noqa: E402
import uzar_isimlik_baski as B  # noqa: E402

OUT = os.path.join(P.OUT_DIR, "foto")
SIZE = (1800, 1100)
RGB = {A.WHITE: (240, 240, 236), A.BLACK: (30, 31, 35), A.BLUE: P.PALOMA_BLUE}
VIEWS = {"on": (24.0, 13.0), "karsi": (2.0, 9.0)}           # kamera açısı, yükseklik açısı (derece)
_MATS = {}


def mat(col, layers):
    key = (col, layers)
    if key not in _MATS:
        _MATS[key] = R.material(f"{P.NAMES[col]}_{int(layers)}", RGB[col], layers=layers)
    return _MATS[key]


def add(name, man, col, layers):
    V, T = A.mesh_arrays(man)
    me = bpy.data.meshes.new(name)
    me.from_pydata((V * R.MM).tolist(), [], T.tolist())
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(mat(col, layers))
    bpy.context.scene.collection.objects.link(ob)
    return ob


def main():
    samples = int(sys.argv[sys.argv.index("--ornek") + 1]) if "--ornek" in sys.argv else 128
    plate = PB.Plate()
    z0, y0 = plate.mount
    panel = B.assembled(plate.panel, z0, y0)                   # sehpada: yüz −y'ye bakar, 15° arkaya eğik
    R.SIZE = SIZE
    sc = R.setup_scene(samples)
    sc.view_settings.exposure = -0.75                          # beyaz panel: siyah ve mavi soluklaşmasın
    _MATS.clear()
    corners = []
    for name, man, col in panel:                               # panel yüzü yukarı basılır: katman izi yüzde değil
        add(name, man, col, layers=False)
        corners.append(man.bounding_box())
    add("sehpa", plate.stand, plate.body, layers=True)         # sehpa tabanı tablada basılır: izler yatay
    corners.append(plate.stand.bounding_box())
    bb = np.array(corners)
    lo, hi = bb[:, :3].min(0) * R.MM, bb[:, 3:].max(0) * R.MM
    box = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    cam_d = bpy.data.cameras.new("kamera")
    cam_d.lens = 85
    cam_d.sensor_fit = "VERTICAL"
    cam = bpy.data.objects.new("kamera", cam_d)
    sc.collection.objects.link(cam)
    sc.camera = cam
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 92
    os.makedirs(OUT, exist_ok=True)
    centre = box.mean(0)
    for view, (az, el) in VIEWS.items():
        a, e = math.radians(az), math.radians(el)
        direction = np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])
        cam["dir"] = direction.tolist()
        R.frame(sc, cam, box, SIZE[0] / SIZE[1])
        cam.data.dof.aperture_fstop = 4.0
        for ob in [o for o in sc.collection.objects if o.type == "LIGHT"]:
            bpy.data.objects.remove(ob)
        r = 0.9
        right = np.cross(-direction, [0, 0, 1])
        right /= np.linalg.norm(right)
        flat = direction * [1, 1, 0]
        flat /= np.linalg.norm(flat)
        # ana ışık yukarıda ve yanda: parlaması kameraya yansımaz, yazılar koyu kalır
        R.light("ana", 20.0, 0.9, centre + r * (0.45 * flat - 0.85 * right) + [0, 0, 0.85], centre, (1.0, 0.97, 0.93))
        R.light("dolgu", 5.0, 1.0, centre + r * (0.9 * flat + 0.7 * right) + [0, 0, 0.25], centre, (0.93, 0.96, 1.0))
        R.light("arka", 12.0, 0.4, centre - r * flat + r * 0.5 * right + [0, 0, 0.7], centre, (1.0, 0.95, 0.88))
        sc.render.filepath = os.path.join(OUT, f"isimlik_{view}.jpg")
        bpy.ops.render.render(write_still=True)
        print("yazıldı:", os.path.relpath(sc.render.filepath, A.ROOT))


if __name__ == "__main__":
    main()
