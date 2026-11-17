"""Yılbaşı anahtarlıklarının stüdyo fotoğrafları (Blender Cycles): figürler zincirli halka takımında asılı.

Halka takımı toptan anahtarlıklarınkiyle aynı (boyde_anahtarlik_foto): Ø25 mm çelik halka (iki tur), 4 halkalık
zincir, ara halka. Ara halka figürün tepesindeki halkanın deliğinden (önden arkaya) geçer, deliğin üst kenarı ara
halkanın teline oturur. Halkalar kafa rengine boyalı (yilbasi_model.boya).

Görünüşler (boyde_labs/yilbasi_anahtarlik/foto/):
  <anahtar>_halka   tek figür asılı; kamera hafif yandan (figüre ~32°), ana ışık yandan (derinlik)
  <anahtar>_iki     iki adet asılı: solda önü, sağda arkası (tam 3D)
  kapak             üç figür asılı (Noel Baba, ren geyiği, kardan adam)
  dizi              altı figür yan yana asılı
  set               altı figür zincirli halkalarıyla asılı, zikzak derinlikte (set kapağı)
Kullanım: python3 scripts/yilbasi_foto.py [anahtarlar|kapak|dizi] [--ornek N] [--deneme]
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_anahtarlik_foto as AF  # noqa: E402
import boyde_urun_foto as F  # noqa: E402
import yilbasi_model as YM  # noqa: E402

FOTO = os.path.join(YM.KOK, "boyde_labs", "yilbasi_anahtarlik", "foto")
UP = AF.UP


def parcalar(key):
    return [(V, Fc, rgb, False) for _, V, Fc, rgb, _ in YM.figur(key)]


def as_(key, yaw, top=(0.0, 0.0, 0.0)):
    """Asılı duruş: halka takımının tepesi `top` (mm); ön yüz kameraya `yaw` derece dönük (180'e yakınsa arkası).
    Döner: figürün parçaları, M (baskı koordinatı -> dünya, mm) ve halka takımının telleri."""
    parts = YM.figur(key)
    c, r_ic, _ = YM.delik(parts)
    psi = math.radians(yaw)
    face = np.array([math.sin(psi), -math.cos(psi), 0.0])
    side = np.cross(face, UP)
    top = np.asarray(top, float)
    wires = []
    w, bottom = AF.split_ring(top - UP * AF.RING_R, side, UP, face)
    wires.append(w)
    length = AF.LINK_S + 2 * AF.LINK_E
    p = bottom + UP * (AF.RING_W + AF.LINK_W) - UP * length / 2
    for i in range(AF.LINKS):
        wires.append(AF.link(p, UP, face if i % 2 == 0 else side))
        end = p - UP * length / 2
        p = p - UP * (length - 2 * AF.LINK_W)
    jc = end + UP * (AF.LINK_W + AF.JUMP_W) - UP * AF.JUMP_R
    wires.append(AF.jump_ring(jc, UP, face))                    # deliğin ekseni (figürün y'si) bu düzlemde
    hole_w = jc - UP * AF.JUMP_R - UP * (r_ic - AF.JUMP_W)        # deliğin üst kenarı telin üstünde
    rot = np.array([[math.cos(psi), -math.sin(psi), 0], [math.sin(psi), math.cos(psi), 0], [0, 0, 1]])
    M = np.c_[rot, hole_w - rot @ c]
    return [(V, Fc, rgb, False) for _, V, Fc, rgb, _ in parts], M, wires


def sira(sets, gap, dys=None):
    """Asılı takımları yan yana dizer (aralarında gap mm); çelik halkaların tepesi aynı yükseklikte. dys: her takımın
    derinlik kaydırması (mm, kameradan uzağa +): önlü arkalı dizilince grup derinlikli durur."""
    dys = dys or [0.0] * len(sets)
    spans = []
    for parts, M, wires in sets:
        q = np.vstack([AF.world(parts, M)] + [V for V, _ in wires])[:, 0]
        spans.append((q.min(), q.max()))
    xs, x = [], 0.0
    for lo, hi in spans:
        xs.append(x - lo)
        x += hi - lo + gap
    xs = np.array(xs) - (x - gap) / 2
    groups = []
    for k, ((parts, M, wires), dx, dy) in enumerate(zip(sets, xs, dys)):
        M = M.copy()
        M[0, 3] += dx
        M[1, 3] += dy
        groups += [AF.put(parts, M, f"anahtarlik{k}"), AF.put_wires(wires, f"halka{k}", (dx, dy, 0))]
    return AF.lift_all(np.vstack(groups), 0.02)


def cek(sets, gap, path, samples, size, fill, az=16.0, el=10.0, fstop=8.0, dys=None):
    """Derinlikli çekim: kamera hafif yandan ve yukarıdan; ana ışık yandan (figürde ışık-gölge geçişi, düz durmasın),
    dolgu zayıf, arkadan kenar ışığı. Fon aynı beyaz stüdyo."""
    sc = AF.studio(False, samples, size)
    pts = sira(sets, gap, dys)
    cam = F.camera(sc, 85)
    a, e = math.radians(az), math.radians(el)
    d = np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])
    cam["dir"] = d.tolist()
    res = sc.render
    F.frame(cam, pts, res.resolution_x / res.resolution_y, fill)
    cam.data.dof.aperture_fstop = fstop
    F.lights(sc, pts.mean(0), d, "yan", 1.25)
    F.shoot(sc, path, F.BEYAZ)
    AF.saturate(path)


def set_cek(samples, size, path):
    """Set kapağı: altı figür zincirli halkalarıyla asılı, zikzak derinlikte (önlü arkalı), hafif dönük; kamera yandan."""
    sira_ = [("kardan_adam", 4), ("ren_geyigi", -22), ("noel_baba", 2), ("atkili_ayicik", -20),
             ("cam_agaci", 0), ("kutup_ayisi", -24)]
    sets = [as_(k, yaw) for k, yaw in sira_]
    cek(sets, 7.0, path, samples, size, 0.94, az=12, el=11, fstop=8.0, dys=[12, -12, 12, -12, 12, -12])


def main(args):
    samples = int(args[args.index("--ornek") + 1]) if "--ornek" in args else 48
    small = "--deneme" in args
    sq = (500, 500) if small else (1200, 1200)
    os.makedirs(FOTO, exist_ok=True)
    keys = [a for a in args if not a.startswith("-") and not a.isdigit()]
    every = not keys
    for key in YM.KEYS:
        if every or key in keys:
            cek([as_(key, -16)], 0, os.path.join(FOTO, f"{key}_halka.jpg"), samples, sq, 0.92, fstop=5.6)
            cek([as_(key, -12), as_(key, 200)], 14.0, os.path.join(FOTO, f"{key}_iki.jpg"), samples, sq, 0.92,
                dys=[-6.0, 6.0])
            print(key, "tamam", flush=True)
    if every or "kapak" in keys:
        cek([as_("ren_geyigi", -18), as_("noel_baba", -6), as_("kardan_adam", 14)], 10.0,
            os.path.join(FOTO, "kapak.jpg"), samples, (600, 600) if small else (1600, 1600), 0.8)
    if every or "set" in keys:
        set_cek(samples, (600, 600) if small else (1600, 1600), os.path.join(FOTO, "set.jpg"))
    if every or "dizi" in keys:
        yaw = (-16, 12, -8, 10, -12, 14)
        cek([as_(k, yaw[i]) for i, k in enumerate(YM.KEYS)], 10.0, os.path.join(FOTO, "dizi.jpg"), samples,
            (720, 400) if small else (1800, 1000), 0.9)


if __name__ == "__main__":
    main(sys.argv[1:])
