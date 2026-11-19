"""Trendyol ürün fotoğrafları (Blender Cycles): 1200 × 1800 (2:3, Trendyol'un istediği), yazısız, logosuz.

Trendyol kuralları: ilan başına en çok 8 görsel; görselde logo, yazı, iletişim bilgisi, web adresi, fiyat olmamalı.
Bu yüzden fotoğraflar tamamen yazısız; bilgi görselleri (QR'ın açtığı sayfa, ölçü ve sipariş) ayrı ve en sonda
(trendyol_gorsel.py), reddedilirse çıkarılabilir.

Modeller: boyde_labs/trendyol/kaynak/ (boyde_urunler, boyde_guzellik, bayrakli_isimlik_shopier'in BOYDE_TEL=
905000000000 ile dışa aktarımı: örnek isimliklerde telefon 0500 000 00 00, BOYDE'nin numarası değil).

Fon: hepsi açık stüdyo (Trendyol'da beyaz zemin önerilir). Beyaz gövdeli isimlikler beyazda kaybolmasın diye fon
biraz gri (AÇIK_GRI) ve ışık yandan; koyu gövdeliler beyazda (Shopier fotoğraflarının beyaz fonu).

Görünüşler (boyde_labs/trendyol/foto/<ilan>/):
  1_ana      tek isimlik, 3/4 sağdan, kadrajı dolduran (ana görsel)
  2_grup     altı isimlik, üç sıra (dikey kadraja), masada
  3..5_tek   başka modeller tek tek (3/4 ya da karşıdan)
  6_detay    yakın: QR ve kabartma (sığ alan derinliği)
Kullanım: python3 scripts/trendyol_foto.py [ilan ...] [--ornek N] [--deneme]
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_urun_foto as F  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F.SRC = os.path.join(ROOT, "boyde_labs", "trendyol", "kaynak")
OUT = os.path.join(ROOT, "boyde_labs", "trendyol", "foto")
SIZE = (1200, 1800)
ACIK_GRI = (226, 226, 223)                    # beyaz gövdeli isimliklerin fonu (beyaz fonda kaybolmasın)
HEDEF_GRI = (232, 232, 229)

ILANLAR = {
    "masa_9x12": {"ana": "soylu", "tek": [("uzar", "studyo"), ("telefon", "studyo"), ("emlak", "on")],
                  "grup": [["uzar", "soylu"], ["calik", "telefon"], ["emlak", "kuyumcu"]], "detay": "uzar"},
    "kurumsal_10x20": {"ana": "mudur", "tek": [("avukat", "studyo"), ("dis", "studyo"), ("otel", "on")],
                       "grup": [["avukat", "mudur"], ["dis", "otel"], ["musavir", "vet"]], "detay": "avukat"},
    "bayrakli": {"ana": "bayrakli", "tek": [("bayrakli", "on"), ("bayrakli", "masa"), ("bayrakli", "sol")],
                 "grup": None, "detay": "bayrakli"},
    "guzellik_9x12": {"ana": "g_sakayik", "tek": [("g_defne", "studyo"), ("g_lal", "studyo"), ("g_papatya", "on")],
                      "grup": [["g_defne", "g_lal"], ["g_ipek", "g_papatya"], ["g_ela", "g_zarif"]],
                      "detay": "g_sakayik"},
    "guzellik_10x20": {"ana": "p_buse", "tek": [("p_aylin", "studyo"), ("p_nazli", "studyo"), ("p_burcu", "on")],
                       "grup": [["p_aylin", "p_gizem"], ["p_nazli", "p_ceren"], ["p_melis", "p_burcu"]],
                       "detay": "p_buse"},
}
GORUNUS = {"studyo": (30.0, 14.0, 0.96), "on": (0.0, 8.0, 0.97), "masa": (-28.0, 16.0, 0.96),
           "sol": (-38.0, 12.0, 0.96)}                # (yatay açı, yükseklik açısı, kadraj doluluğu)


def _sahne(kind, samples, size, parts_list):
    light = sum(F.light_body(p) for p in parts_list) * 2 > len(parts_list)
    sc = F.scene(kind, samples, size, dark=False)
    for n in ("duvar0", "duvar1"):                     # geniş grup çekiminde kamera duvarın arkasına düşmesin
        if n in F.bpy.data.objects:
            F.bpy.data.objects.remove(F.bpy.data.objects[n])
    if light:                                          # beyaz gövdeler: fon gri, ışık yandan (kenarlar belirsin)
        for ob in sc.collection.objects:
            if ob.name in ("fon", "masa"):
                ob.data.materials[0] = F.surface(ob.name + "_gri", ACIK_GRI, 0.35 if ob.name == "fon" else 0.15)
        sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = F.R.srgb(ACIK_GRI)
        sc.view_settings.exposure = -0.45
    else:
        sc.view_settings.exposure = -0.3
    sc.view_settings.look = F.BAKIS
    return sc, light


def _cek(sc, box, path, az, el, fill, light, fstop=5.6, lens=85, kind="studyo", odak=None):
    cam = F.camera(sc, lens)
    a, e = math.radians(az), math.radians(el)
    d = np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])
    cam["dir"] = d.tolist()
    dist = F.frame(cam, box, SIZE[0] / SIZE[1], fill)
    cam.data.dof.aperture_fstop = fstop
    if odak is not None:
        cam.data.dof.focus_distance = float(np.linalg.norm(np.asarray(cam.location) - odak))
    F.lights(sc, box.mean(0), d, "yan" if light else kind, 1.15 if light else 1.0)
    F.shoot(sc, path, HEDEF_GRI if light else F.BEYAZ)
    return dist


def tek(key, view, path, samples):
    parts = F.load(key)
    kind = "masa" if view == "masa" else "studyo"
    sc, light = _sahne(kind, samples, SIZE, [parts])
    box = F.place(parts)
    az, el, fill = GORUNUS[view]
    _cek(sc, box, path, az, el, fill, light, kind=kind)


def grup(rows, path, samples, cat):
    """Üç sıra, sırada iki isimlik; arka sıralar biraz sağa kayık (dikey kadrajda üst üste görünür)."""
    loaded = [[F.load(k) for k in r] for r in rows]
    sc, light = _sahne("masa", samples, SIZE, [p for r in loaded for p in r])
    corners = []
    gap = 18.0 if cat == "9x12" else 30.0
    derin = 120.0 if cat == "9x12" else 165.0
    for r, row in enumerate(loaded):
        widths = [max(V[:, 0].max() for _, V, _ in p) - min(V[:, 0].min() for _, V, _ in p) for p in row]
        x = -(sum(widths) + gap * (len(widths) - 1)) / 2 + (r - 1) * 0.12 * widths[0]
        y = (2 - r) * derin                             # 0: en arkadaki sıra
        for p, w in zip(row, widths):
            x0 = min(V[:, 0].min() for _, V, _ in p)
            yc = np.mean([V[:, 1].mean() for _, V, _ in p])
            corners.append(F.place(p, (x - x0, y - yc, 0.0)))
            x += w + gap
    box = np.vstack(corners)
    _cek(sc, box, path, -8.0, 34.0 if cat == "9x12" else 40.0, 0.92, light, fstop=7.1, lens=70, kind="masa")


def detay(key, path, samples):
    """Yakın: kadraj isimliğin ortasına, sığ alan derinliği (QR, kabartma ve katman izi görünür)."""
    parts = F.load(key)
    sc, light = _sahne("studyo", samples, SIZE, [parts])
    box = F.place(parts)
    panel = np.vstack([V for m, V, _ in parts if m["panel"]]) * F.MM
    odak = panel.mean(0)
    _cek(sc, box, path, 24.0, 18.0, 1.85, light, fstop=3.2, odak=odak)


def ilan(name, samples):
    cfg = ILANLAR[name]
    out = os.path.join(OUT, name)
    os.makedirs(out, exist_ok=True)
    cat = "9x12" if ("9x12" in name or name == "bayrakli") else "10x20"
    tek(cfg["ana"], "studyo", os.path.join(out, "1_ana.jpg"), samples)
    if cfg["grup"]:
        grup(cfg["grup"], os.path.join(out, "2_grup.jpg"), samples, cat)
    for i, (key, view) in enumerate(cfg["tek"]):
        tek(key, view, os.path.join(out, f"{i + 3}_tek_{key}.jpg"), samples)
    detay(cfg["detay"], os.path.join(out, "6_detay.jpg"), samples)


def main(args):
    samples = int(args[args.index("--ornek") + 1]) if "--ornek" in args else 64
    global SIZE
    if "--deneme" in args:
        SIZE = (400, 600)
    names = [a for a in args if a in ILANLAR] or list(ILANLAR)
    for n in names:
        ilan(n, samples)
        print(n, "tamam", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
