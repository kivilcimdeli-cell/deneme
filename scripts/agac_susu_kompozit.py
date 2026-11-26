"""Ağaç süsleri: dala asılı set fotoğrafları (Blender + kesik görseller).

3MF'si olmayan figürler kullanıcının görselinden kesildi (agac_susu_kes.py). Sahne Blender'da: çam dalı (dalları) ve
iplerin kendisi 3D (agac_susu_foto'daki gibi); figürler sonradan, ipin ucu deliğin üst kenarına gelecek biçimde
görüntünün üstüne yerleştirilir. Figür ölçeği gerçek: kesiklerde 1 mm ≈ 6,94 piksel (ayıcığın 3MF'sinden: 40,2 mm boy).
Kesikler sol üstten aydınlatılmış (yatık çekim); sahnenin ana ışığı da soldan.

sahne(dallar, size, path, ...): dallar = [{"z": yükseklik, "y": derinlik, "x": (x0, x1), "egim": mm, "suslar":
[(anahtar, x, sarkma, sallanma°)]}]
"""
import json
import math
import os
import sys

import bpy
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agac_susu_foto as S  # noqa: E402
import agac_susu_model as M  # noqa: E402
import boyde_anahtarlik_foto as AF  # noqa: E402
import boyde_urun_foto as F  # noqa: E402

KESIK = os.path.join(M.KOK, "boyde_labs", "agac_susu", "kesik")
INFO = json.load(open(os.path.join(KESIK, "kesik.json")))
SRC_PPM = 279.0 / 40.2                                     # kesik piksel / mm
KALIN = 6.4                                                # deliğin çevresinde süsün kalınlığı (mm, 3MF'den)


def ip(x, y0, z_t, drop, yaw=0.0):
    z_b = z_t - drop
    yz = S.ip_yolu(KALIN, z_b, z_t)
    path = np.c_[np.zeros(len(yz)), yz[:, 0], yz[:, 1]] @ S.rot_z(yaw).T + np.array([x, y0, 0.0])
    path = np.vstack([path, path[:1]])
    d = np.gradient(path, axis=0)
    d /= np.linalg.norm(d, axis=1)[:, None]
    side = np.tile(S.rot_z(yaw) @ np.array([1.0, 0, 0]), (len(path), 1))
    return AF.tube(path, np.cross(side, d), side, S.IP_R, seg=10)


def kutu(key, x, y0, z_b):
    """Süsün dünyadaki yaklaşık kutusu (mm): deliğin üst kenarı (x, z_b + IP_R)."""
    w, h = INFO[key]["boyut"]
    hx, hy, hr = INFO[key]["delik"]
    top = z_b + S.IP_R
    sx = 1 / SRC_PPM
    xa, xb = x - hx * sx, x + (w - hx) * sx
    za, zb = top - (h - (hy - hr)) * sx, top + (hy - hr) * sx
    return np.array([[xa, y0 - 4, za], [xb, y0 + 4, zb]])


def sahne(dallar, size, path, samples=64, az=6.0, el=5.0, fill=0.9, ekstra=None, fstop=7.1, odak_kaydir=0.0, yer=True, yer_alt=55.0, yer_sag=False):
    sc = AF.studio(False, samples, size)
    S._MAT.clear()
    pts, yerler = [], []
    for k, dl in enumerate(dallar):
        x0, x1 = dl["x"]
        z, y0, eg = dl["z"], dl["y"], dl.get("egim", 0.0)
        z_of = (lambda z, eg, x0, x1: (lambda x: z + eg * ((x - x0) / (x1 - x0) - 0.5) - 0.0016 * (x - (x0 + x1) / 2) ** 2
                                        * 0.5))(z, eg, x0, x1)
        bos = []
        for i, (key, x, drop, sal) in enumerate(dl["suslar"]):
            zt = z_of(x)
            V, f = ip(x, y0, zt, drop, yaw=dl.get("yaw", 12.0) * (1 if i % 2 else -1))
            AF.add(f"ip{k}_{i}", V, f, S.mat("ip", S.IP, 0.85), np.c_[np.eye(3), np.zeros(3)], smooth=True)
            b = kutu(key, x, y0, zt - drop)
            pts += [b * F.MM]
            yerler.append((key, np.array([x, y0, zt - drop + S.IP_R]), sal, b))
            bos.append(x)
        S.dal_ekle(f"dal{k}", S.dal(x0, x1, z_of, y0, bos=bos, seed=4 + k))
        S.susle(x0, x1, z_of, y0, bos, seed=7 + k)
        pts.append(np.array([[x0, y0, z_of(x0)], [x1, y0, z_of(x1) + 12]]) * F.MM)
    icerik = np.vstack(pts)
    if ekstra is not None:
        pts.append(np.asarray(ekstra) * F.MM)
    pts = np.vstack(pts)
    zmin = pts[:, 2].min()
    if yer:                                                  # zemin süsleri: içeriğin en altından yer_alt mm aşağıda
        xs = icerik[:, 0] / F.MM
        z0 = icerik[:, 2].min() / F.MM - yer_alt
        S.zemin(xs.min(), xs.max(), z0, -3.2, sag=yer_sag)
        pts = np.vstack([pts, np.array([[xs.min(), 60.0, z0 - 4], [xs.max(), 60.0, z0 + 34]]) * F.MM])  # kadraja
        zmin = pts[:, 2].min()
    dz = 0.04 - zmin
    for ob in bpy.context.scene.collection.objects:
        if ob.type == "MESH" and ob.name != "fon":
            ob.location.z += dz
    pts[:, 2] += dz
    cam = F.camera(sc, 85)
    a, e = math.radians(az), math.radians(el)
    d = np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])
    cam["dir"] = d.tolist()
    res = sc.render
    F.frame(cam, pts, res.resolution_x / res.resolution_y, fill)
    cam.data.dof.aperture_fstop = fstop
    cam.data.dof.focus_distance += odak_kaydir
    F.lights(sc, pts.mean(0), d, "yan", 1.2)
    bpy.context.view_layer.update()
    W, H = size
    konum = []
    for key, p, sal, b in yerler:
        def px(q):
            u = world_to_camera_view(sc, cam, Vector((q[0] * F.MM, q[1] * F.MM, q[2] * F.MM + dz)))
            return np.array([u.x * W, (1 - u.y) * H])
        a0, a1 = px(p), px(p + np.array([10.0, 0, 0]))
        konum.append((key, a0, float(np.linalg.norm(a1 - a0)) / 10.0, sal))
    F.shoot(sc, path, F.BEYAZ)
    AF.saturate(path)
    yapistir(path, konum)
    return konum


def yapistir(path, konum):
    """Kesikleri yerleştirir: deliğin üst kenarı ipin ucuna; ölçek gerçek boy; hafif sallanma (delik çevresinde)."""
    im = Image.open(path).convert("RGBA")
    for key, p, ppm, sal in konum:
        k = Image.open(os.path.join(KESIK, f"{key}.png"))
        s = ppm / SRC_PPM
        k = k.resize((max(1, round(k.width * s)), max(1, round(k.height * s))), Image.LANCZOS)
        hx, hy, hr = INFO[key]["delik"]
        ax, ay = hx * s, (hy - hr) * s
        if sal:                                             # delik çevresinde döndür
            pad = int(max(k.size))
            big = Image.new("RGBA", (k.width + 2 * pad, k.height + 2 * pad), (0, 0, 0, 0))
            big.paste(k, (pad, pad))
            k = big.rotate(sal, resample=Image.BICUBIC, center=(ax + pad, ay + pad))
            ax, ay = ax + pad, ay + pad
        golge = Image.new("RGBA", k.size, (40, 36, 30, 0))
        golge.putalpha(k.split()[3].point(lambda v: int(v * 0.16)))
        from PIL import ImageFilter
        golge = golge.filter(ImageFilter.GaussianBlur(ppm * 1.6))
        im.alpha_composite(golge, (int(round(float(p[0] - ax + ppm * 2.2))), int(round(float(p[1] - ay + ppm * 2.6)))))
        im.alpha_composite(k, (int(round(float(p[0] - ax))), int(round(float(p[1] - ay)))))
    im.convert("RGB").save(path, quality=93)


def dal_(z, x, suslar, y=-3.2, egim=6.0, yaw=12.0):
    return {"z": z, "y": y, "x": x, "egim": egim, "suslar": suslar, "yaw": yaw}


def cekimler(out, samples):
    """Görsellerin fotoğrafları (yazısız)."""
    j = lambda n: os.path.join(out, n + ".jpg")  # noqa: E731
    yield "kapak", lambda: sahne([
        dal_(150, (-128, 128), [("noel_baba", -96, 30, -3), ("kardan_adam", -32, 42, 3), ("cam_agaci", 32, 30, -2),
                                ("ren_geyigi", 96, 42, 3)]),
        dal_(48, (-112, 112), [("atkili_ayicik", -64, 26, 3), ("kutup_ayisi", 0, 34, -3),
                               ("zencefilli_kurabiye", 64, 26, 2)], y=26.0, egim=-5)],
        (1600, 1600), j("kapak"), samples, fill=0.9, ekstra=[[0, 0, -92]], el=4, yer_alt=34.0, yer_sag=True)
    yield "dikey", lambda: sahne([
        dal_(250, (-95, 95), [("noel_baba", -60, 28, -3), ("cam_agaci", 0, 40, 2), ("kardan_adam", 60, 28, 3)]),
        dal_(158, (-80, 80), [("ren_geyigi", -36, 30, 3), ("atkili_ayicik", 36, 38, -3)], y=18.0, egim=-5),
        dal_(66, (-80, 80), [("kutup_ayisi", -36, 36, -2), ("zencefilli_kurabiye", 36, 28, 3)], y=6.0, egim=4)],
        (1200, 1800), j("dikey"), samples, fill=0.9, el=3)
    yield "genis", lambda: sahne([dal_(120, (-160, 160), [
        (k, -126 + 42 * i, 30 + (12 if i % 2 else 0), (-4, 3)[i % 2]) for i, k in enumerate(M_SIRA)])],
        (1800, 1000), j("genis"), samples, fill=0.94)
    for ad, trio in (("uclu_1", ["noel_baba", "kardan_adam", "cam_agaci"]),
                     ("uclu_2", ["ren_geyigi", "atkili_ayicik", "kutup_ayisi"])):
        yield ad, (lambda trio=trio, ad=ad: sahne([dal_(110, (-80, 80), [
            (trio[0], -46, 32, -3), (trio[1], 0, 44, 2), (trio[2], 46, 32, 3)])], (1200, 1200), j(ad), samples,
            fill=0.9, ekstra=[[0, 0, 20]]))
        yield ad + "_dikey", (lambda trio=trio, ad=ad: sahne([dal_(170, (-70, 70), [
            (trio[0], -40, 30, -3), (trio[1], 0, 78, 2), (trio[2], 40, 46, 3)])], (1200, 1800), j(ad + "_dikey"),
            samples, fill=0.9))
    yield "ikili", lambda: sahne([dal_(110, (-62, 62), [("zencefilli_kurabiye", -24, 30, -3),
                                                         ("kardan_adam", 24, 42, 3)])], (1200, 1200), j("ikili"),
                                 samples, fill=0.86, ekstra=[[0, 0, 30]])
    yield "ikili_dikey", lambda: sahne([dal_(150, (-56, 56), [("zencefilli_kurabiye", -22, 30, -3),
                                                               ("kardan_adam", 22, 62, 3)])], (1200, 1800),
                                       j("ikili_dikey"), samples, fill=0.9)


M_SIRA = ["noel_baba", "kardan_adam", "cam_agaci", "ren_geyigi", "atkili_ayicik", "kutup_ayisi", "zencefilli_kurabiye"]


def main(args):
    out = os.path.join(M.KOK, "boyde_labs", "agac_susu", "foto")
    os.makedirs(out, exist_ok=True)
    samples = int(args[args.index("--ornek") + 1]) if "--ornek" in args else 64
    sec = [a for a in args if not a.startswith("-") and not a.isdigit()]
    for ad, f in cekimler(out, samples):
        if not sec or ad in sec:
            f()


if __name__ == "__main__":
    main(sys.argv[1:])
