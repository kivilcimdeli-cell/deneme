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


def sahne(dallar, size, path, samples=64, alt=0.0, ust=0.0, fill=0.84, fstop=2.0):
    """Bütün görsellerde aynı düzen: önde dal(lar), iplerde ürünler; arkada flu ikinci dal, toplar ve ışıklar
    (S.arka_plan). Kamera önden (el 4°), 85 mm, odak ürün düzleminde, f/2.8. Kadraj ürünlere göre: alt / ust, ürün
    yüksekliğinin o oranı kadar boşluk (başlık şeridi, logo için). Ürünlerin piksel kutuları <path>.json'a yazılır."""
    sc = AF.studio(False, samples, size)
    S._MAT.clear()
    kutular, yerler, dal_ust = [], [], []
    for k, dl in enumerate(dallar):
        x0, x1 = dl["x"]
        z, y0, eg = dl["z"], dl["y"], dl.get("egim", 0.0)
        z_of = (lambda z, eg, x0, x1: (lambda x: z + eg * ((x - x0) / (x1 - x0) - 0.5) - 0.0008 * (x - (x0 + x1) / 2)
                                        ** 2))(z, eg, x0, x1)
        bos = []
        for i, (key, x, drop, sal) in enumerate(dl["suslar"]):
            zt = z_of(x)
            V, f = ip(x, y0, zt, drop, yaw=dl.get("yaw", 12.0) * (1 if i % 2 else -1))
            AF.add(f"ip{k}_{i}", V, f, S.mat("ip", S.IP, 0.85), np.c_[np.eye(3), np.zeros(3)], smooth=True)
            b = kutu(key, x, y0, zt - drop)
            kutular.append(b)
            dal_ust.append([x, y0, zt + 7.0])
            yerler.append((key, np.array([x, y0, zt - drop + S.IP_R]), sal, b))
            bos.append(x)
        S.dal_ekle(f"dal{k}", S.dal(x0, x1, z_of, y0, bos=bos, seed=4 + k))
    K = np.vstack(kutular)
    lo, hi = K.min(0), K.max(0)
    h = hi[2] - lo[2]
    gen = hi[0] - lo[0]
    S.arka_plan(lo[0] - 0.9 * gen - 120, hi[0] + 0.9 * gen + 120, hi[2] + 2.0, lo[2] - alt * h * 0.5,
                derin=max(S.ARKA_Y, 1.1 * gen))
    hedef = np.vstack([K, dal_ust, [[lo[0], -3.2, lo[2] - alt * h], [lo[0], -3.2, max(hi[2], max(
        d[2] for d in dal_ust)) + ust * h]]]) * F.MM
    zmin = -0.3                                              # sahne yerden yüksekte (zemin kadraja girmez)
    dz = 0.25 - (lo[2] - alt * h) * F.MM
    for ob in bpy.context.scene.collection.objects:
        if ob.type == "MESH" and ob.name != "fon":
            ob.location.z += dz
    hedef[:, 2] += dz
    cam = F.camera(sc, 85)
    e = math.radians(4.0)
    d = np.array([0.0, -math.cos(e), math.sin(e)])
    cam["dir"] = d.tolist()
    res = sc.render
    F.frame(cam, hedef, res.resolution_x / res.resolution_y, fill)
    cam.data.dof.aperture_fstop = fstop
    F.lights(sc, hedef.mean(0), d, "yan", 1.2)
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
    kutular = []
    for key, p, ppm, sal in konum:
        k = Image.open(os.path.join(KESIK, f"{key}.png"))
        s = ppm / SRC_PPM
        k = k.resize((max(1, round(k.width * s)), max(1, round(k.height * s))), Image.LANCZOS)
        if s > 1.1:                                          # büyütülen kesik: kenarlar yumuşamasın
            from PIL import ImageFilter as _F
            k = k.filter(_F.UnsharpMask(radius=1.4, percent=int(min(90, 60 * s)), threshold=2))
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
        ox, oy = int(round(float(p[0] - ax))), int(round(float(p[1] - ay)))
        im.alpha_composite(k, (ox, oy))
        bb = k.split()[3].getbbox()
        kutular.append([ox + bb[0], oy + bb[1], ox + bb[2], oy + bb[3]])
    im.convert("RGB").save(path, quality=93)
    json.dump({"urunler": kutular, "boyut": list(im.size)}, open(path[:-4] + ".json", "w"))


def dal_(z, x, suslar, y=-3.2, egim=4.0, yaw=12.0):
    return {"z": z, "y": y, "x": x, "egim": egim, "suslar": suslar, "yaw": yaw}


T1 = ["noel_baba", "kardan_adam", "cam_agaci"]
T2 = ["ren_geyigi", "atkili_ayicik", "kutup_ayisi"]
T3 = ["kutup_ayisi", "zencefilli_kurabiye", "noel_baba"]
IKI = ["zencefilli_kurabiye", "kardan_adam"]


def iki_sira(ust, alt_, z=150.0, dz=84.0):
    """4 + 3 (ya da 3 + 2...) iki sıra; alt sıra yarım aralık kayık."""
    def sira(keys, z, kay):
        n = len(keys)
        xs = (np.arange(n) - (n - 1) / 2) * 44.0 + kay
        return dal_(z, (xs[0] - 40, xs[-1] + 40), [(k, x, 26 + (8 if i % 2 else 0), (-3, 3)[i % 2])
                                                    for i, (k, x) in enumerate(zip(keys, xs))])
    out = [sira(ust, z, 0.0), sira(alt_, z - dz, 0.0)]
    out[1]["y"] = 26.0
    return out


def uc_sira(r1, r2, r3, z=250.0, dz=86.0):
    out = []
    for j, keys in enumerate((r1, r2, r3)):
        n = len(keys)
        xs = (np.arange(n) - (n - 1) / 2) * 48.0
        out.append(dal_(z - j * dz, (xs[0] - 44, xs[-1] + 44), [(k, x, 24 + (8 if i % 2 else 0), (-3, 3)[i % 2])
                                                                 for i, (k, x) in enumerate(zip(keys, xs))],
                        y=-3.2 + 22.0 * j))
    return out


def uclu(keys, dikey=False):
    drops = (30, 84, 54) if dikey else (26, 36, 28)
    return [dal_(110, (-82, 82), [(keys[0], -46, drops[0], -3), (keys[1], 0, drops[1], 2), (keys[2], 46, drops[2], 3)])]


def ikili(keys, dikey=False):
    drops = (30, 76) if dikey else (26, 34)
    return [dal_(110, (-60, 60), [(keys[0], -24, drops[0], -3), (keys[1], 24, drops[1], 3)])]


def cekimler(out, samples):
    """Görsellerin fotoğrafları (yazısız). Kare ve gönderi: altta başlık şeridi, üstte logo için boşluk (alt, ust)."""
    j = lambda n: os.path.join(out, n + ".jpg")  # noqa: E731
    sq, ig, st, ty = (1600, 1600), (1080, 1350), (1080, 1920), (1200, 1800)
    BAS = dict(alt=0.30, ust=0.20)                             # Shopier / gönderi: başlık şeridi ve logo payı
    yield "kapak", lambda: sahne(iki_sira(M_SIRA[:4], M_SIRA[4:]), sq, j("kapak"), samples, **BAS)
    yield "set_kare", lambda: sahne(iki_sira(M_SIRA[4:][::-1], M_SIRA[:4][::-1]), sq, j("set_kare"),
                                    samples, **BAS)
    yield "gonderi", lambda: sahne(iki_sira(M_SIRA[:4], M_SIRA[4:]), ig, j("gonderi"), samples, alt=0.34, ust=0.18)
    yield "hikaye", lambda: sahne(uc_sira(M_SIRA[:3], M_SIRA[3:5], M_SIRA[5:]), st, j("hikaye"), samples,
                                  alt=0.16, ust=0.12)
    yield "dikey", lambda: sahne(uc_sira(M_SIRA[:3], M_SIRA[3:5], M_SIRA[5:]), ty, j("dikey"), samples,
                                 alt=0.04, ust=0.04, fill=0.88)
    for ad, keys in (("uclu_1", T1), ("uclu_2", T2), ("uclu_3", T3)):
        yield ad, (lambda keys=keys, ad=ad: sahne(uclu(keys), sq, j(ad), samples, **BAS))
        yield ad + "_dikey", (lambda keys=keys, ad=ad: sahne(uclu(keys, True), ty, j(ad + "_dikey"), samples,
                                                              alt=0.08, ust=0.08, fill=0.86))
    yield "ikili", lambda: sahne(ikili(IKI), sq, j("ikili"), samples, **BAS)
    yield "ikili_dikey", lambda: sahne(ikili(IKI, True), ty, j("ikili_dikey"), samples, alt=0.08, ust=0.08,
                                       fill=0.86)


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
