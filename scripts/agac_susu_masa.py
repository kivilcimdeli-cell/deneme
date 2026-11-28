"""Ağaç süsleri: masaüstü (üstten) ürün fotoğrafları. Kullanıcı 3. tur: "görsellerin AI tarafından yapıldıkları
belli; daha profesyonel; uzun ipler hoşuma gitmedi; geniş açıda ürünler silik".

Sorunun kaynağı: figürler kullanıcının görselinde masada yatarken, hafif önden ve üstten (~78°) çekilmiş, ışık sol
üstten. Asılı (önden) sahnede bu ışık ve açı tutmuyordu. Burada sahne kaynak görselin kendi açısına getirilir:
süsler beyaz, hafif dokulu bir masada yatar; kamera önden 78° yukarıdan, ana ışık sol üstten (kaynakla aynı). Süslerin
gölgesi kaynak görselden aktarılır (zemine oranla çarpım: gerçek gölge). Çevrede yöntemle kurulan çam dalları, cam
toplar, yıldızlar; her süsün kısa, aynı boyda kırmızı ip ilmeği masada (deliğinden çıkar). Tek tip ince film greni
fotoğrafı birleştirir. Süsler kadrajın büyük kısmını kaplar.

masa(yerlesim, size, path, ...): yerlesim = [(anahtar, x, y, açı)] (mm; x sağa, y masada geriye).
Ürünlerin piksel kutuları <path>.json'a (reklam testi için).
"""
import json
import math
import os
import sys

import bpy
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agac_susu_foto as S  # noqa: E402
import agac_susu_model as M  # noqa: E402
import boyde_anahtarlik_foto as AF  # noqa: E402
import boyde_urun_foto as F  # noqa: E402
import restoran_masalik_foto as R  # noqa: E402

KESIK = os.path.join(M.KOK, "boyde_labs", "agac_susu", "kesik")
INFO = json.load(open(os.path.join(KESIK, "kesik.json")))
ZEMIN = np.array(INFO["_zemin"])
SRC_PPM = (INFO["atkili_ayicik"]["boyut"][1] - 6) / 40.2
EL = 78.0
MASA = (243, 241, 237)
I3 = np.c_[np.eye(3), np.zeros(3)]


def boyut(key):
    w, h = INFO[key]["boyut"]
    return w / SRC_PPM, h / SRC_PPM


def rotz(a):
    a = math.radians(a)
    return np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1.0]])


def masa_malzemesi():
    """Mat, çok hafif dokulu kâğıt/keten masa (düz plastik gibi durmasın)."""
    m = bpy.data.materials.new("masa_doku")
    m.use_nodes = True
    nt = m.node_tree
    bs = nt.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = R.srgb(MASA)
    bs.inputs["Roughness"].default_value = 0.85
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 900.0
    nz.inputs["Detail"].default_value = 6.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.08
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    return m


def ilmek(hole, yon, L=20.0, a=5.5):
    """Masada yatan kısa kırmızı ip ilmeği: deliğin içinden çıkar, yon (derece) doğrultusunda L mm."""
    t = np.linspace(0, 2 * np.pi, 120)
    x = a * np.sin(t) * np.sin(t / 2)
    y = L * (1 - np.cos(t)) / 2
    z = S.IP_R + 2.2 * np.exp(-y / 2.5)
    P = np.c_[x, y, z] @ rotz(yon).T + hole
    d = np.gradient(P, axis=0)
    d /= np.linalg.norm(d, axis=1)[:, None]
    up = np.tile([0, 0, 1.0], (len(P), 1))
    side = np.cross(d, up)
    side /= np.linalg.norm(side, axis=1)[:, None]
    return AF.tube(P, np.cross(side, d), side, S.IP_R, seg=10)


def yatik_dal(c, aci, L, seed):
    """Masada yatan çam dalı (dal yerden 3 mm yukarıda; aşağı bakan iğneler masaya gömülür, görünmez)."""
    dl = S.dal(-L / 2, L / 2, lambda x: 3.0, 0.0, seed=seed)
    Rz = rotz(aci)
    out = []
    for V, f in dl:
        out.append((V @ Rz.T + c, f))
    return out


def sus_ekle(engel, bolge, rng, n_top=4, n_yildiz=3, n_dal=2):
    """Boş yerlere (ürünlerden uzak) çam dalları, cam toplar ve yıldızlar. engel: [(x, y, yarıçap)]; bolge: kadraj
    (x0, y0, x1, y1) mm."""
    x0, y0, x1, y1 = bolge
    k = 0
    for j in range(n_dal):                                   # dallar köşelerden kadraja girer
        cx = x0 - 25 if j % 2 == 0 else x1 + 25
        cy = y1 + 10 if j % 2 == 0 else y0 - 10
        aci = (-35 if j % 2 == 0 else 145) + rng.uniform(-10, 10)
        for i, (V, f) in enumerate(yatik_dal(np.array([cx, cy, 0.0]), aci, 150.0, seed=31 + j)):
            AF.add(f"m_dal{j}_{i}", V, f, [S.mat("dal", S.DAL, 0.8), S.mat("igne", S.IGNE, 0.45),
                                          S.mat("igne_acik", S.IGNE_ACIK, 0.5)][i], I3, smooth=True)
        engel.append((cx, cy, 70.0))
    yer = []
    for tur, n in (("top", n_top), ("yildiz", n_yildiz)):
        for _ in range(n):
            for _deneme in range(400):
                r = rng.uniform(8.0, 11.0) if tur == "top" else rng.uniform(6.0, 8.0)
                p = np.array([rng.uniform(x0 + r, x1 - r), rng.uniform(y0 + r, y1 - r)])
                if all(np.hypot(*(p - e[:2])) > e[2] + r + 5 for e in engel + yer):
                    yer.append((p[0], p[1], r))
                    break
            else:
                continue
            if tur == "top":
                rk = ("kirmizi", S.KIRMIZI, 0.12, 0.0) if k % 2 == 0 else ("altin_top", S.ALTIN, 0.22, 0.9)
                V, f = S.kure(np.array([p[0], p[1], r]), r, 40)
                AF.add(f"m_top{k}", V, f, S.ozel(rk[0], rk[1], rk[2], rk[3], coat=0.8), I3, smooth=True)
                a = rng.uniform(0, 360)
                V, f = S.silindir(np.zeros(3), 1.8, 2.6)
                V = V @ np.array([[1, 0, 0], [0, 0, -1.0], [0, 1.0, 0]]).T @ rotz(a).T      # yan yatık kapak
                V += np.array([p[0], p[1], r]) + rotz(a) @ np.array([0, -r + 0.4, 0])
                AF.add(f"m_kapak{k}", V, f, S.ozel("altin", S.ALTIN, 0.28, 0.95), I3, smooth=True)
            else:
                V, f = S.yildiz(np.zeros(3), r)
                V = V @ np.array([[1, 0, 0], [0, 0, -1.0], [0, 1.0, 0]]).T @ rotz(rng.uniform(0, 72)).T
                V += np.array([p[0], p[1], 1.4])
                AF.add(f"m_yildiz{k}", V, f, S.ozel("altin", S.ALTIN, 0.28, 0.95), I3)
            k += 1


def masa(yerlesim, size, path, samples=96, alt=0.0, ust=0.0, fill=0.86, sus=True, seed=5, kenar=0.0):
    sc = AF.studio(False, samples, size)
    S._MAT.clear()
    fon = bpy.data.objects["fon"]
    fon.data.materials[0] = masa_malzemesi()
    rng = np.random.default_rng(seed)
    kutular, yerler, engel = [], [], []
    for key, x, y, aci in yerlesim:
        w, h = boyut(key)
        hx, hy, hr = INFO[key]["delik"]
        W0, H0 = INFO[key]["boyut"]
        hole = np.array([x + (hx - W0 / 2) / SRC_PPM, y + (H0 / 2 - hy) / SRC_PPM, 2.0])
        V, f = ilmek(hole, aci + rng.uniform(-18, 18))
        AF.add(f"ip_{key}", V, f, S.mat("ip", S.IP, 0.85), I3, smooth=True)
        kutular.append(np.array([[x - w / 2, y - h / 2, 0], [x + w / 2, y + h / 2 + 18, 6]]))
        engel.append((x, y + 6, max(w, h) / 2 + 8))
        yerler.append((key, np.array([x, y, 4.0])))
    K = np.vstack(kutular)
    lo, hi = K.min(0), K.max(0)
    hgt = hi[1] - lo[1]
    gen = hi[0] - lo[0]
    hedef = np.vstack([K, [[lo[0] - kenar * gen, lo[1] - alt * hgt, 0], [hi[0] + kenar * gen, hi[1] + ust * hgt, 0]]])
    cam = F.camera(sc, 85)
    e = math.radians(EL)
    d = np.array([0.0, -math.cos(e), math.sin(e)])
    cam["dir"] = d.tolist()
    res = sc.render
    F.frame(cam, hedef * F.MM, res.resolution_x / res.resolution_y, fill)
    cam.data.dof.aperture_fstop = 5.6
    bpy.context.view_layer.update()
    W, H = size

    def px(q):
        u = world_to_camera_view(sc, cam, Vector((q[0] * F.MM, q[1] * F.MM, q[2] * F.MM)))
        return np.array([u.x * W, (1 - u.y) * H])

    def mm(pix):                                             # piksel -> masa düzlemi (z = 0), yaklaşık
        c = np.array([0.0, 0.0, 0.0])
        a0 = px(c)
        a1, a2 = px(c + [100, 0, 0]), px(c + [0, 100, 0])
        A = np.c_[(a1 - a0) / 100, (a2 - a0) / 100]
        return np.linalg.solve(A, np.asarray(pix) - a0)
    if sus:
        x0, y0 = mm((0, H))
        x1, y1 = mm((W, 0))
        sus_ekle(engel, (x0, y0, x1, y1), rng)
    for ob in [o for o in sc.collection.objects if o.type == "LIGHT"]:
        bpy.data.objects.remove(ob)
    c = hedef.mean(0) * F.MM
    span = float(np.ptp(hedef[:, 0])) * F.MM
    R.light("ana", 90.0 * max(1, span / 0.25) ** 2, 1.2 * max(1, span / 0.25),
            c + np.array([-0.55, 0.45, 0.75]) * max(1, span / 0.25), c, (1.0, 0.97, 0.93))
    R.light("dolgu", 18.0 * max(1, span / 0.25) ** 2, 1.4 * max(1, span / 0.25),
            c + np.array([0.6, -0.4, 0.5]) * max(1, span / 0.25), c, (0.95, 0.97, 1.0))
    konum = []
    for key, p in yerler:
        a0, a1 = px(p), px(p + np.array([10.0, 0, 0]))
        konum.append((key, a0, float(np.linalg.norm(a1 - a0)) / 10.0))
    F.shoot(sc, path, F.BEYAZ)
    AF.saturate(path)
    yapistir(path, konum)


def yapistir(path, konum, gren=2.2):
    """Süsler kaynak görseldeki çevreleriyle (gölgeleri dahil) yerleşir: çevre bölgesi masaya, kaynak zemine oranla
    çarpılır (gerçek gölge, kenara doğru yumuşar); süsün kendisi üstüne. Sonra bütün kareye ince film greni."""
    im = np.asarray(Image.open(path).convert("RGB")).astype(float)
    H, W = im.shape[:2]
    kutular = []
    for key, p, ppm in konum:
        s = ppm / SRC_PPM
        cev = Image.open(os.path.join(KESIK, "cevre", f"{key}.png"))
        cw, ch = max(1, round(cev.width * s)), max(1, round(cev.height * s))
        rgb_im = cev.convert("RGB").resize((cw, ch), Image.LANCZOS)   # RGB ve alfa ayrı (önçarpım yok)
        if s > 1.15:
            rgb_im = rgb_im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=50, threshold=2))
        rgb = np.asarray(rgb_im).astype(float)
        al = np.asarray(cev.getchannel("A").resize((cw, ch), Image.LANCZOS)).astype(float)[..., None] / 255.0
        ox_, oy_ = INFO[key]["cevre"]
        w0, h0 = INFO[key]["boyut"]
        cx = (ox_ + w0 / 2) * s
        cy = (oy_ + h0 / 2) * s
        x0, y0 = int(round(p[0] - cx)), int(round(p[1] - cy))
        xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + cw), min(H, y0 + ch)
        if xa >= xb or ya >= yb:
            continue
        sub = (slice(ya - y0, yb - y0), slice(xa - x0, xb - x0))
        oran = np.clip(rgb[sub] / ZEMIN, 0.35, 1.0).mean(2, keepdims=True)    # gölge (renksiz)
        from scipy import ndimage as ndi
        uzak = ndi.distance_transform_edt(al[..., 0] < 0.5)           # süsten uzaklık (piksel)
        wgt = np.clip(1.0 - (uzak - 4 * s) / (26 * s), 0, 1) ** 1.5   # gölge yalnız süsün çevresinde, yumuşak biter
        wgt = wgt[sub][..., None]
        bolge = im[ya:yb, xa:xb]
        bolge = bolge * (1 - wgt * (1 - oran))
        a = al[sub]
        im[ya:yb, xa:xb] = bolge * (1 - a) + rgb[sub] * a
        ys, xs = np.nonzero(a[..., 0] > 0.5)
        kutular.append([xa + int(xs.min()), ya + int(ys.min()), xa + int(xs.max()), ya + int(ys.max())])
    rng = np.random.default_rng(3)
    im = im + rng.normal(0, gren, im.shape[:2])[..., None]
    Image.fromarray(np.clip(im + 0.5, 0, 255).astype(np.uint8)).save(path, quality=93)
    json.dump({"urunler": kutular, "boyut": [W, H]}, open(path[:-4] + ".json", "w"))


SIRA = ["noel_baba", "kardan_adam", "cam_agaci", "ren_geyigi", "atkili_ayicik", "kutup_ayisi", "zencefilli_kurabiye"]


def izgara(keys, sutun, ax=40.0, ay=50.0, kay=0.5):
    """Süsler satır satır (alt satır yarım aralık kayık, hafif açılı): (anahtar, x, y, açı)."""
    out, i = [], 0
    rows = [keys[k:k + sutun] for k in range(0, len(keys), sutun)]
    for r, row in enumerate(rows):
        n = len(row)
        for j, k in enumerate(row):
            x = (j - (n - 1) / 2) * ax
            y = ((len(rows) - 1) / 2 - r) * ay
            out.append((k, x, y, (-6, 4, -3, 7, -5, 3, -4)[i % 7]))
            i += 1
    return out


def satirlar(rows, ax=44.0, ay=54.0, kay=0.0):
    """rows: [[anahtar, ...], ...] üstten alta; her satır ortalı; kay: satırlar dönüşümlü sağa sola kayık (mm)."""
    out, i = [], 0
    n = len(rows)
    for r, row in enumerate(rows):
        for j, k in enumerate(row):
            x = (j - (len(row) - 1) / 2) * ax + (kay if r % 2 else -kay) * (1 if n > 1 else 0)
            y = ((n - 1) / 2 - r) * ay
            out.append((k, x, y, (-6, 4, -3, 7, -5, 3, -4)[i % 7]))
            i += 1
    return out


T1 = ["noel_baba", "kardan_adam", "cam_agaci"]
T2 = ["ren_geyigi", "atkili_ayicik", "kutup_ayisi"]
T3 = ["kutup_ayisi", "zencefilli_kurabiye", "noel_baba"]
IKI = ["zencefilli_kurabiye", "kardan_adam"]
YAKIN = ["ren_geyigi", "atkili_ayicik"]


def cekimler(out, samples):
    j = lambda n: os.path.join(out, n + ".jpg")  # noqa: E731
    sq, ig, st, ty = (1600, 1600), (1080, 1350), (1080, 1920), (1200, 1800)
    BAS = dict(alt=0.34, ust=0.20)                           # kare / gönderi: başlık şeridi ve logo payı
    yield "kapak", lambda: masa(satirlar([SIRA[:4], SIRA[4:]]), sq, j("kapak"), samples, seed=1, **BAS)
    yield "set_kare", lambda: masa(satirlar([SIRA[4:][::-1], SIRA[:4][::-1]]), sq, j("set_kare"), samples, seed=2,
                                   **BAS)
    yield "gonderi", lambda: masa(satirlar([SIRA[:4], SIRA[4:]]), ig, j("gonderi"), samples, seed=3, alt=0.40,
                                  ust=0.22)
    yield "hikaye", lambda: masa(satirlar([SIRA[:2], SIRA[2:5], SIRA[5:]]), st, j("hikaye"), samples, seed=4,
                                 alt=0.30, ust=0.16)
    yield "dikey", lambda: masa(satirlar([SIRA[:2], SIRA[2:5], SIRA[5:]]), ty, j("dikey"), samples, seed=5,
                                alt=0.06, ust=0.06)
    for k, (ad, keys) in enumerate((("uclu_1", T1), ("uclu_2", T2), ("uclu_3", T3))):
        yield ad, (lambda keys=keys, ad=ad, k=k: masa(satirlar([keys]), sq, j(ad), samples, seed=10 + k, **BAS))
        yield ad + "_dikey", (lambda keys=keys, ad=ad, k=k: masa(
            satirlar([[keys[0]], [keys[1]], [keys[2]]], ay=52.0, kay=13.0), ty, j(ad + "_dikey"), samples,
            seed=20 + k, alt=0.10, ust=0.10))
    for k, (ad, keys) in enumerate((("ikili", IKI), ("yakin", YAKIN))):
        yield ad, (lambda keys=keys, ad=ad, k=k: masa(satirlar([keys], ax=46.0), sq, j(ad), samples, seed=30 + k,
                                                      **BAS))
        yield ad + "_dikey", (lambda keys=keys, ad=ad, k=k: masa(
            satirlar([[keys[0]], [keys[1]]], ay=56.0, kay=12.0), ty, j(ad + "_dikey"), samples, seed=40 + k,
            alt=0.14, ust=0.14))


def main(args):
    out = os.path.join(M.KOK, "boyde_labs", "agac_susu", "foto")
    os.makedirs(out, exist_ok=True)
    samples = int(args[args.index("--ornek") + 1]) if "--ornek" in args else 96
    sec = [a for a in args if not a.startswith("-") and not a.isdigit()]
    if "deneme" in sec:
        masa(satirlar([SIRA[:3]]), (1200, 1200), os.path.join(out, "masa_deneme.jpg"), samples, alt=0.25, ust=0.15)
        return
    for ad, f in cekimler(out, samples):
        if not sec or ad in sec:
            f()


if __name__ == "__main__":
    main(sys.argv[1:])
