"""Ağaç süsleri (7'li set) fotoğrafları (Blender Cycles): figürler çam dalına kırmızı iple asılı.

Sahne boyde_urun_foto'nun beyaz stüdyosu (önceki Shopier görselleriyle aynı fon). Çam dalı yöntemle kurulur: hafif
eğik kahverengi dal ve çevresinde iğne yapraklar (her iğne ince, ucu sivrilen, hafif kıvrık tüp). İp figürün tepesindeki
deliğin içinden önden arkaya geçer (deliğin üst kenarına oturur), iki kol yukarı çıkıp dalın üstünden döner.

Figür baskı koordinatında yatık (yüzü +z, başı +y); dünyada ayakta: x → x, y → z, z → −y (yüzü kameraya, −y).
Kullanım: python3 scripts/agac_susu_foto.py [deneme] [--ornek N]
"""
import math
import os
import sys

import bpy
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agac_susu_model as M  # noqa: E402
import boyde_anahtarlik_foto as AF  # noqa: E402
import boyde_urun_foto as F  # noqa: E402

FOTO = os.path.join(M.KOK, "boyde_labs", "agac_susu", "foto")
R0 = np.array([[1.0, 0, 0], [0, 0, -1.0], [0, 1.0, 0]])      # baskı → ayakta
IP_R = 0.55                                                # ip yarıçapı (mm)
DAL_R = 2.6
IP = (176, 28, 36)
IGNE = (36, 88, 52)
DAL = (92, 64, 42)
_MAT = {}


def mat(name, rgb, rough):
    if name not in _MAT:
        _MAT[name] = F.surface(name, rgb, rough)
    return _MAT[name]


def rot_z(a):
    a = math.radians(a)
    return np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1.0]])


def tapered(path, r0, r1, seg=6):
    """Ucu sivrilen tüp (iğne): path N × 3; yarıçap r0'dan r1'e."""
    d = np.gradient(path, axis=0)
    d /= np.linalg.norm(d, axis=1)[:, None]
    ref = np.array([0.0, 0.0, 1.0]) if abs(d[0, 2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    a = np.cross(d, ref)
    a /= np.linalg.norm(a, axis=1)[:, None]
    b = np.cross(d, a)
    r = np.linspace(r0, r1, len(path))
    phi = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    V = (path[:, None, :] + r[:, None, None] * (np.cos(phi)[None, :, None] * a[:, None, :]
                                                 + np.sin(phi)[None, :, None] * b[:, None, :])).reshape(-1, 3)
    n = len(path)
    faces = [(i * seg + j, i * seg + (j + 1) % seg, (i + 1) * seg + (j + 1) % seg, (i + 1) * seg + j)
             for i in range(n - 1) for j in range(seg)]
    V = np.vstack([V, path[0], path[-1]])
    c0, c1 = len(V) - 2, len(V) - 1
    faces += [(c0, (j + 1) % seg, j) for j in range(seg)] + [(c1, (n - 1) * seg + j, (n - 1) * seg + (j + 1) % seg)
                                                              for j in range(seg)]
    return V, faces


def birlestir(parcalar):
    Vs, Fs, k = [], [], 0
    for V, f in parcalar:
        Vs.append(V)
        Fs += [tuple(i + k for i in q) for q in f]
        k += len(V)
    return np.vstack(Vs), Fs


def _ignele(base_of, xs, rng, bos, yogun=7, Lr=(11.0, 19.0), egim=(0.15, 0.55)):
    """base_of(x) çevresinde iğneler; iki tonda (koyu, açık uçlar). Döner: (koyu, açık) tüp listeleri."""
    koyu, acik = [], []
    for x in xs:
        base = base_of(x)
        for _ in range(yogun + int(rng.integers(-2, 3))):
            th = rng.uniform(0, 2 * np.pi)
            v = np.array([0.0, math.cos(th), math.sin(th)]) + np.array([rng.uniform(*egim), 0, 0])
            if v[2] < -0.3 and any(abs(x - b) < 6.0 for b in bos) and v[1] < 0.3:
                continue
            v /= np.linalg.norm(v)
            L = rng.uniform(*Lr)
            t = np.linspace(0, 1, 6)[:, None]
            p = base + v * DAL_R * 0.6 + t * v * L + (t ** 2) * np.array([0, 0, -0.08 * L])
            (acik if rng.random() < 0.3 else koyu).append(tapered(p, rng.uniform(0.45, 0.6), 0.1, seg=5))
    return koyu, acik


def dal(x0, x1, z_of, y0, bos=(), seed=4):
    """Çam dalı: x0..x1 boyunca dal (yükseklik z_of(x)), yanlarında kısa yan dallar; çevresinde iki tonda iğneler.
    bos: iplerin x'leri (önlerinde aşağı sarkan iğne olmasın). Döner: (dallar, koyu iğneler, açık iğneler)."""
    rng = np.random.default_rng(seed)
    xs = np.linspace(x0, x1, 80)
    wob = np.convolve(rng.normal(0, 0.5, len(xs)), np.ones(9) / 9, "same")
    path = np.c_[xs, y0 + wob, [z_of(x) for x in xs]]
    dallar = [tapered(path, DAL_R, DAL_R * 0.7, seg=12)]
    koyu, acik = _ignele(lambda x: np.array([x, y0, z_of(x)]), np.arange(x0 + 2.0, x1 - 1.0, 0.9), rng, bos)
    for xb in np.arange(x0 + 25.0, x1 - 30.0, rng.uniform(45, 60)):      # yan dallar: geriye ve yukarı
        ang = math.radians(rng.uniform(25, 40))
        side = rng.choice([-1.0, 1.0])
        Lb = rng.uniform(28, 40)
        u = np.array([math.cos(ang), side * 0.55, math.sin(ang) * 0.5])
        u /= np.linalg.norm(u)
        b0 = np.array([xb, y0, z_of(xb)])
        bp = b0 + np.linspace(0, Lb, 20)[:, None] * u
        dallar.append(tapered(bp, DAL_R * 0.6, DAL_R * 0.35, seg=8))
        k2, a2 = _ignele(lambda x: b0 + (x - xb) / u[0] * u, np.arange(xb + 3.0, xb + Lb * u[0], 1.1), rng, bos,
                         yogun=6, Lr=(9.0, 15.0))
        koyu += k2
        acik += a2
    return birlestir(dallar), birlestir(koyu), birlestir(acik)


def ip_yolu(t_hole, z_b, z_t, n=160):
    """İp halkası (y, z düzleminde, yerel; delik merkezi y=0): altta deliğin içinden düz geçer (|y| ≤ t/2), sonra
    yukarı döner, dalın üstünden aşar. Döner: N × 2 (y, z), kapalı."""
    a, rr = t_hole / 2 + 0.2, 1.4
    w = DAL_R + IP_R
    pts = []
    for s in np.linspace(-a, a, 12):                                 # deliğin içi
        pts.append((s, z_b))
    for u in np.linspace(-math.pi / 2, 0, 8)[1:]:                    # sağ alt dönüş
        pts.append((a + rr * math.cos(u), z_b + rr + rr * math.sin(u)))
    y_side = a + rr
    for s in np.linspace(0, 1, 20)[1:]:                              # sağ kol: daralarak dala
        pts.append((y_side + (w - y_side) * s, z_b + rr + (z_t - z_b - rr) * s))
    for u in np.linspace(0, math.pi, 24)[1:-1]:                      # dalın üstü
        pts.append((w * math.cos(u), z_t + w * math.sin(u)))
    for s in np.linspace(1, 0, 20)[:-1]:                             # sol kol
        pts.append((-y_side - (w - y_side) * s, z_b + rr + (z_t - z_b - rr) * s))
    for u in np.linspace(math.pi, 3 * math.pi / 2, 8)[1:-1]:         # sol alt dönüş
        pts.append((-a + rr * math.cos(u), z_b + rr + rr * math.sin(u)))
    return np.array(pts)


def as_(key, x, z_t, y0, drop, yaw=0.0, salla=0.0):
    """Figür dalda (x, y0, z_t) asılı; delik dalın drop mm altında. yaw: dikey eksende dönüş, salla: yüz düzleminde
    hafif sallanma (derece). Döner: figür parçaları (V, F, rgb), M (3 × 4), ip (V, faces)."""
    parts = M.oku(key)
    c, r, z0, z1 = M.delik(parts)
    t = z1 - z0
    hole_p = np.array([c[0], c[1], (z0 + z1) / 2])                  # deliğin merkezi (baskı)
    sw = math.radians(salla)
    roll = np.array([[math.cos(sw), 0, -math.sin(sw)], [0, 1, 0], [math.sin(sw), 0, math.cos(sw)]])
    Rw = rot_z(yaw) @ roll @ R0
    z_b = z_t - drop
    top_w = np.array([x, y0, z_b + IP_R])                           # deliğin üst kenarı ipin üstünde
    hole_top_print = hole_p + np.array([0, r, 0])
    Mx = np.c_[Rw, top_w - Rw @ hole_top_print]
    yz = ip_yolu(t, z_b, z_t)
    path = np.c_[np.zeros(len(yz)), yz[:, 0], yz[:, 1]]
    path = path @ rot_z(yaw).T + np.array([x, y0, 0.0])
    path = np.vstack([path, path[:1]])
    d = np.gradient(path, axis=0)
    d /= np.linalg.norm(d, axis=1)[:, None]
    side = np.tile(rot_z(yaw) @ np.array([1.0, 0, 0]), (len(path), 1))
    radial = np.cross(side, d)
    ip = AF.tube(path, radial, side, IP_R, seg=10)
    return [(V, f, rgb) for _, V, f, rgb in parts], Mx, ip


IGNE_ACIK = (74, 128, 66)


def dal_ekle(name, d):
    I = np.c_[np.eye(3), np.zeros(3)]
    (dV, dF), (kV, kF), (aV, aF) = d
    p = AF.add(name, dV, dF, mat("dal", DAL, 0.8), I, smooth=True)
    AF.add(name + "_igne", kV, kF, mat("igne", IGNE, 0.45), I, smooth=True)
    AF.add(name + "_igne_acik", aV, aF, mat("igne_acik", IGNE_ACIK, 0.5), I, smooth=True)
    return p


def sahne(asililar, x0, x1, z_of, y0, samples, size):
    sc = AF.studio(False, samples, size)
    _MAT.clear()
    pts = []
    for k, (parts, Mx, ip) in enumerate(asililar):
        for i, (V, f, rgb) in enumerate(parts):
            pts.append(AF.add(f"figur{k}_{i}", V, f, F.mat(rgb, False, layers=True), Mx))
        pts.append(AF.add(f"ip{k}", ip[0], ip[1], mat("ip", IP, 0.85), np.c_[np.eye(3), np.zeros(3)], smooth=True))
    pts.append(dal_ekle("dal", dal(x0, x1, z_of, y0, bos=[Mx[0, 3] for _, Mx, _ in asililar])))
    pts = np.vstack(pts)
    return sc, AF.lift_all(pts, 0.03)


def cek(sc, pts, path, az=8.0, el=6.0, fill=0.9, fstop=6.3, kind="yan"):
    cam = F.camera(sc, 85)
    a, e = math.radians(az), math.radians(el)
    d = np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])
    cam["dir"] = d.tolist()
    res = sc.render
    F.frame(cam, pts, res.resolution_x / res.resolution_y, fill)
    cam.data.dof.aperture_fstop = fstop
    F.lights(sc, pts.mean(0), d, kind, 1.2)
    F.shoot(sc, path, F.BEYAZ)
    AF.saturate(path)


def main(args):
    samples = int(args[args.index("--ornek") + 1]) if "--ornek" in args else 64
    os.makedirs(FOTO, exist_ok=True)
    if "detay" in args:                                   # ayıcık (3MF'den): yakın, hafif yandan (eklemler görünsün)
        for ad, size, drop, fill in (("detay_ayicik", (1200, 1200), 24.0, 0.86),
                                     ("detay_ayicik_dikey", (1200, 1800), 40.0, 0.9)):
            z_of = lambda x: 60.0 - 0.006 * x * x  # noqa: E731
            sc, pts = sahne([as_("atkili_ayicik", 0.0, z_of(0.0), -3.2, drop, yaw=-24, salla=4)], -34, 34, z_of,
                            -3.2, samples, size)
            cek(sc, pts, os.path.join(FOTO, f"{ad}.jpg"), az=14.0, el=8.0, fill=fill, fstop=4.0)
    if "deneme" in args:
        z_of = lambda x: 60.0 - 0.004 * x * x + 0.03 * x  # noqa: E731
        sc, pts = sahne([as_("atkili_ayicik", 0.0, z_of(0.0), -3.2, 26.0, yaw=-14, salla=3)], -45, 45, z_of, -3.2,
                        samples, (900, 900))
        cek(sc, pts, os.path.join(FOTO, "deneme_ayicik.jpg"))


if __name__ == "__main__":
    main(sys.argv[1:])
