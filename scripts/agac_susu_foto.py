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


def dal(x0, x1, z_of, y0, bos=(), seed=4):
    """Çam dalı: x0..x1 boyunca dal (yükseklik z_of(x)), çevresinde iğneler. bos: iplerin x'leri (önlerinde aşağı
    sarkan iğne az olsun). Döner: (dal tüpü, iğneler)."""
    rng = np.random.default_rng(seed)
    xs = np.linspace(x0, x1, 80)
    path = np.c_[xs, np.full_like(xs, y0), [z_of(x) for x in xs]]
    dal_m = tapered(path, DAL_R, DAL_R * 0.75, seg=12)
    igne = []
    for x in np.arange(x0 + 2.0, x1 - 1.0, 0.9):
        base = np.array([x, y0, z_of(x)])
        for _ in range(7):
            th = rng.uniform(0, 2 * np.pi)                          # dalın çevresinde
            v = np.array([0.0, math.cos(th), math.sin(th)])
            v += np.array([rng.uniform(0.15, 0.55), 0, 0])          # dalın ucuna doğru yatık
            if v[2] < -0.3 and any(abs(x - b) < 6.0 for b in bos) and v[1] < 0.3:
                continue                                            # ipin önünde aşağı sarkan iğne yok
            v /= np.linalg.norm(v)
            L = rng.uniform(13.0, 20.0)
            bend = np.array([0, 0, -0.08]) * L                      # hafif sarkma
            t = np.linspace(0, 1, 6)[:, None]
            p = base + v * DAL_R * 0.6 + t * v * L + (t ** 2) * bend
            igne.append(tapered(p, 0.55, 0.12, seg=5))
    return dal_m, birlestir(igne)


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


def sahne(asililar, x0, x1, z_of, y0, samples, size):
    sc = AF.studio(False, samples, size)
    _MAT.clear()
    pts = []
    for k, (parts, Mx, ip) in enumerate(asililar):
        for i, (V, f, rgb) in enumerate(parts):
            pts.append(AF.add(f"figur{k}_{i}", V, f, F.mat(rgb, False, layers=True), Mx))
        pts.append(AF.add(f"ip{k}", ip[0], ip[1], mat("ip", IP, 0.85), np.c_[np.eye(3), np.zeros(3)], smooth=True))
    dal_m, igne = dal(x0, x1, z_of, y0, bos=[Mx[0, 3] for _, Mx, _ in asililar])
    pts.append(AF.add("dal", dal_m[0], dal_m[1], mat("dal", DAL, 0.8), np.c_[np.eye(3), np.zeros(3)], smooth=True))
    AF.add("igne", igne[0], igne[1], mat("igne", IGNE, 0.45), np.c_[np.eye(3), np.zeros(3)], smooth=True)
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
    if "deneme" in args:
        z_of = lambda x: 60.0 - 0.004 * x * x + 0.03 * x  # noqa: E731
        sc, pts = sahne([as_("atkili_ayicik", 0.0, z_of(0.0), -3.2, 26.0, yaw=-14, salla=3)], -45, 45, z_of, -3.2,
                        samples, (900, 900))
        cek(sc, pts, os.path.join(FOTO, "deneme_ayicik.jpg"))


if __name__ == "__main__":
    main(sys.argv[1:])
