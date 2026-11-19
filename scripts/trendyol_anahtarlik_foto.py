"""Trendyol fotoğrafları: plakalı anahtarlık ve yılbaşı anahtarlık seti (Blender Cycles, 1200 × 1800, yazısız).

Plakalı: boyde_plakali_anahtarlik'in modelleri BOYDE_PLAKA_AD="AD SOYAD" ile (görselde marka adı yok) dışa aktarılır:
  BOYDE_KAYNAK=boyde_labs/trendyol/kaynak_plaka BOYDE_PLAKA_AD="AD SOYAD" python3 scripts/boyde_plakali_anahtarlik.py
Fotoğraflar aynı sahne ve halka takımıyla (boyde_anahtarlik_foto), dikey kadraj:
  plaka/kapak   altı plaka masada (tek sütun: dikey kadrajı doldurur), plaka/p0X_halka, p0X_iki, plaka/renk (kırmızı ve mavi bant)
Yılbaşı seti (yilbasi_foto'nun derinlikli çekimi; halkalar takılı):
  yilbasi/set    altı figür iki katta asılı (dikey kadraja), önlü arkalı
  yilbasi/<figür>_halka, noel_baba_iki
Kullanım: python3 scripts/trendyol_anahtarlik_foto.py [plaka] [yilbasi] [--ornek N] [--deneme]
"""
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TY = os.path.join(ROOT, "boyde_labs", "trendyol", "foto")
os.environ.setdefault("BOYDE_KAYNAK", os.path.join(ROOT, "boyde_labs", "trendyol", "kaynak_plaka"))
os.environ.setdefault("BOYDE_FOTO", os.path.join(TY, "plaka"))
os.environ.setdefault("BOYDE_PLAKA_AD", "AD SOYAD")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SIZE = (1200, 1800)


def plaka(samples, size):
    import boyde_anahtarlik_foto as AF
    import boyde_plakali_anahtarlik as PL
    PL.bagla()
    os.makedirs(PL.FOTO, exist_ok=True)
    AF.F.SIZE = size
    for a in ("p01", "p02", "p03"):
        AF.model_shots(a, samples)
    PL.masa([[("p01", False, -4)], [("p04", False, 3)], [("p02", False, -2)], [("p05", False, 4)],
             [("p03", False, -3)], [("p06", False, 2)]], "kapak.jpg", samples, size, adim=6.0, kaydir=0.0)  # tek sütun
    PL.masa([[("p01", False, -3)], [("p07", False, 2)]], "renk.jpg", samples, size, adim=9.0, kaydir=0.0)


def iki_kat(sets_ust, sets_alt, path, samples, size, kat=104.0):
    """Altı figür iki katta asılı (üstte üç, altta üç; alt kat kat mm aşağıda ve yarım aralık kayık), önlü arkalı."""
    import boyde_anahtarlik_foto as AF
    import yilbasi_foto as YF
    sc = AF.studio(False, samples, size)
    groups = []
    for r, sets in enumerate((sets_ust, sets_alt)):
        spans = []
        for parts, M, wires in sets:
            q = np.vstack([AF.world(parts, M)] + [V for V, _ in wires])[:, 0]
            spans.append((q.min(), q.max()))
        xs, x = [], 0.0
        for lo, hi in spans:
            xs.append(x - lo)
            x += hi - lo + 8.0
        xs = np.array(xs) - (x - 8.0) / 2 + (14.0 if r else -14.0)
        for k, ((parts, M, wires), dx) in enumerate(zip(sets, xs)):
            dy, dz = (-14.0 if r else 14.0) + (6.0 if k % 2 else -6.0), -kat * r
            M = M.copy()
            M[:, 3] += (dx, dy, dz)
            groups += [AF.put(parts, M, f"f{r}{k}"), AF.put_wires(wires, f"h{r}{k}", (dx, dy, dz))]
    pts = AF.lift_all(np.vstack(groups), 0.02)
    cam = AF.F.camera(sc, 85)
    import math
    a, e = math.radians(14), math.radians(10)
    d = np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])
    cam["dir"] = d.tolist()
    AF.F.frame(cam, pts, size[0] / size[1], 0.97)
    cam.data.dof.aperture_fstop = 8.0
    AF.F.lights(sc, pts.mean(0), d, "yan", 1.25)
    AF.F.shoot(sc, path, AF.F.BEYAZ)
    AF.saturate(path)
    del YF


def yilbasi(samples, size):
    import yilbasi_foto as YF
    out = os.path.join(TY, "yilbasi")
    os.makedirs(out, exist_ok=True)
    ust = [YF.as_("kardan_adam", 6), YF.as_("noel_baba", -18), YF.as_("ren_geyigi", 4)]
    alt = [YF.as_("atkili_ayicik", -14), YF.as_("cam_agaci", 4), YF.as_("kutup_ayisi", -20)]
    iki_kat(ust, alt, os.path.join(out, "set.jpg"), samples, size)
    for key in ("ren_geyigi", "atkili_ayicik", "kardan_adam", "kutup_ayisi"):
        YF.cek([YF.as_(key, -16)], 0, os.path.join(out, f"{key}_halka.jpg"), samples, size, 0.9, fstop=5.6)
    YF.cek([YF.as_("noel_baba", -12), YF.as_("noel_baba", 200)], 14.0, os.path.join(out, "noel_baba_iki.jpg"),
           samples, size, 0.94, dys=[-6.0, 6.0])


def main(args):
    samples = int(args[args.index("--ornek") + 1]) if "--ornek" in args else 64
    size = (400, 600) if "--deneme" in args else SIZE
    secim = [a for a in args if a in ("plaka", "yilbasi")] or ["plaka", "yilbasi"]
    if "plaka" in secim:
        plaka(samples, size)
    if "yilbasi" in secim:
        yilbasi(samples, size)


if __name__ == "__main__":
    main(sys.argv[1:])
