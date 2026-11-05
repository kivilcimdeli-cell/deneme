"""Hazır bir isimlik 3MF'ine lastik izi bandı ekler (beyaz kabartma), gerisine dokunmaz.

İstek (Antalya 7/24 Oto Lastik Tamiri, uzar1 M06): "isimle numara arasında çok boşluk var, oraya lastik şeritleri
çizer misin, lastik izi yani, beyaz renk olsun".

- **Desen:** sitedeki lastik izi bandı (şablon 2 · Lastik izi, `tread("band")`): ortada gidiş yönüne (sağa) bakan
  ok biçimli diş, üstünde ve altında omuz blokları. Karo 40 × 120 birim; bant yazı sütununun tam genişliğinde, tam
  karo sayısıyla.
- **Baskı:** 2 mm kabartma, panelin yüzünde (z 10 → 12), "Kabartma (beyaz)" parçasına eklenir; filament ataması ve
  proje ayarları olduğu gibi kalır. Önizleme görselleri (tabla, üstten, seçim) yeniden çizilir.
- **Kontroller:**
  - bant yazılara en az 2 mm uzak (kırmızı ve beyaz kabartma);
  - çizgiler en az 0,8 mm, aralar en az 0,8 mm;
  - QR üstten görünümde okunuyor.

Okuma yönü: u = y (soldan sağa), v = -x (aşağıdan yukarı); panel 120 × 90 mm tablada dik durur.

Kullanım:
  python3 scripts/isimlik_lastik_izi.py <giriş.3mf> <çıkış.3mf> --u 27.2 78.9 --v -17.7 12.3 [--karo 10]
  (--u: bandın soldan sağa sınırı; --v: boşluğun alt ve üst kenarı, yazıların kenarları; bant ortalanır)
"""
import argparse
import io
import os
import re
import sys
import zipfile

import manifold3d as m3
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anahtarlik import R_ISO, R_TOP, SHOW, BLACK, RED, WHITE, placed  # noqa: E402
from cift_tarafli_isimlik import PICK_ID, mesh_xml, render  # noqa: E402

KABARTMA = 2.0
YUZ_Z = 10.0
# sitedeki lastik izi karosu (40 × 120, y aşağı): ok biçimli diş ve iki omuz bloğu
KARO_W, KARO_H = 40.0, 120.0
DIS = [(5, 24), (17, 24), (32, 60), (17, 96), (5, 96), (20, 60)]
OMUZ = [(9, 4, 27, 16), (9, 104, 27, 116)]
ICERIK_X, ICERIK_Y = (5.0, 32.0), (4.0, 116.0)       # karonun dolu kısmı


def _yuvarlak_dikdortgen(x0, y0, x1, y1, r, n=6):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        pts += [(cx + r * np.cos(np.radians(a0 + 90 * i / n)), cy + r * np.sin(np.radians(a0 + 90 * i / n)))
                for i in range(n + 1)]
    return pts


def bant(u0, u1, vc, n):
    """Okuma düzleminde (u, v) çokgenler ve ölçek: n karo u0..u1'e tam sığar, v ortası vc."""
    uzun = (n - 1) * KARO_W + (ICERIK_X[1] - ICERIK_X[0])
    k = (u1 - u0) / uzun
    yc = (ICERIK_Y[0] + ICERIK_Y[1]) / 2

    def uv(x, y, i):
        return u0 + (x - ICERIK_X[0] + i * KARO_W) * k, vc - (y - yc) * k

    polys = []
    for i in range(n):
        polys.append([uv(x, y, i) for x, y in DIS])
        for x0, y0, x1, y1 in OMUZ:
            polys.append([uv(x, y, i) for x, y in _yuvarlak_dikdortgen(x0, y0, x1, y1, 2.0)])
    return polys, k


def dunya(polys):
    """(u, v) → tablada (x, y) = (-v, u): 90° döndürme (yansıma değil, sarım yönü korunur)."""
    out = []
    for p in polys:
        q = [(-v, u) for u, v in p]
        a = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(q, q[1:] + q[:1]))
        out.append(q if a > 0 else q[::-1])
    return out


def oku(z):
    s = z.read("3D/Objects/object_1.model").decode()
    parts = {}
    for m in re.finditer(r'<object id="(\d+)"[^>]*>(.*?)</object>', s, re.S):
        V = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', m.group(2)), float)
        T = np.array(re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', m.group(2)), int)
        parts[int(m.group(1))] = (V, T)
    return s, parts


def parca_bilgisi(cfg):
    """model_settings.config → [(parça no, ad, ekstrüder)]"""
    return [(int(i), ad, int(e)) for i, ad, e in re.findall(
        r'<part id="(\d+)"[^>]*>\s*<metadata key="name" value="([^"]+)"/>.*?key="extruder" value="(\d+)"', cfg, re.S)]


def renk(ad):
    return SHOW[WHITE] if "beyaz" in ad else SHOW[RED] if "kırmızı" in ad else SHOW[BLACK]


def kontrol(polys_uv, parts, bilgi, k):
    """Bandın yazılara uzaklığı ve en ince çizgi / ara."""
    from shapely.geometry import MultiPoint, Polygon
    from shapely.ops import unary_union
    band = unary_union([Polygon(p) for p in polys_uv])
    en_yakin = 99.0
    for no, ad, _ in bilgi:
        if "Kabartma" not in ad:
            continue
        V, T = parts[no]
        P = V[T]
        ust = P[:, :, 2].min(1) > YUZ_Z + KABARTMA - 1e-3      # üst yüz üçgenleri
        for tri in P[ust]:
            en_yakin = min(en_yakin, band.distance(MultiPoint([(y, -x) for x, y, _ in tri]).convex_hull))
    cizgi = 11.08 * k                                      # ok dişinin dik kalınlığı (12 · sin 67,4°)
    ara = min(8.0, KARO_W - 12.0) * k                      # omuz ile diş arası (8 birim)
    omuz = 12.0 * k
    return en_yakin, min(cizgi, omuz), ara


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("giris")
    ap.add_argument("cikis")
    ap.add_argument("--u", nargs=2, type=float, required=True)
    ap.add_argument("--v", nargs=2, type=float, required=True)
    ap.add_argument("--karo", type=int, default=10)
    a = ap.parse_args()

    z = zipfile.ZipFile(a.giris)
    obj_s, parts = oku(z)
    cfg = z.read("Metadata/model_settings.config").decode()
    bilgi = parca_bilgisi(cfg)
    hedef = next(no for no, ad, _ in bilgi if ad == "Kabartma (beyaz)")

    vc = (a.v[0] + a.v[1]) / 2
    polys_uv, k = bant(a.u[0], a.u[1], vc, a.karo)
    yuk = (ICERIK_Y[1] - ICERIK_Y[0]) * k
    cs = m3.CrossSection([np.array(p) for p in dunya(polys_uv)], m3.FillRule.NonZero)
    man = cs.extrude(KABARTMA).translate((0, 0, YUZ_Z))
    mesh = man.to_mesh()
    Vb = np.asarray(mesh.vert_properties)[:, :3].astype(float)
    Tb = np.asarray(mesh.tri_verts).astype(int)
    print(f"bant: {a.karo} karo, ölçek {k:.4f} mm/birim, {a.u[1] - a.u[0]:.1f} × {yuk:.1f} mm, "
          f"v {vc - yuk / 2:.1f} … {vc + yuk / 2:.1f}; hacim {man.volume():.0f} mm³ (~{man.volume() * 1.24e-3:.1f} g)")

    yakin, cizgi, ara = kontrol(polys_uv, parts, bilgi, k)
    print(f"kontrol: yazılara en yakın {yakin:.1f} mm (≥ 2), en ince çizgi {cizgi:.2f} mm, en dar ara {ara:.2f} mm "
          "(≥ 0,8)")
    assert yakin >= 2.0 and cizgi >= 0.8 and ara >= 0.8, "bant baskı kurallarına uymuyor"

    V, T = parts[hedef]
    parts[hedef] = (np.vstack([V, Vb]), np.vstack([T, Tb + len(V)]))

    # nesne dosyası: yalnız hedef parçanın ağı değişir
    uuid = re.search(rf'<object id="{hedef}" p:UUID="([^"]+)"', obj_s).group(1)
    yeni_obj = re.sub(rf'  <object id="{hedef}" .*?</object>\n', lambda _: mesh_xml(hedef, uuid, *parts[hedef]),
                      obj_s, count=1, flags=re.S)
    # ayarlar: üçgen sayıları
    yeni_cfg = re.sub(rf'(<part id="{hedef}" .*?<mesh_stat face_count=")\d+', rf"\g<1>{len(parts[hedef][1])}", cfg,
                      count=1, flags=re.S)
    yeni_cfg = re.sub(r'<metadata face_count="\d+"/>',
                      f'<metadata face_count="{sum(len(t) for _, t in parts.values())}"/>', yeni_cfg, count=1)

    # önizlemeler (anahtarlik.write_design ile aynı)
    items = re.findall(r'<item objectid="\d+"[^>]*transform="([^"]+)"', z.read("3D/3dmodel.model").decode())
    inst = []
    for tf in items:
        m = [float(x) for x in tf.split()]
        inst.append((m[9], m[10], float(np.degrees(np.arctan2(m[1], m[0])))))
    shaded = [(parts[no][0], parts[no][1], renk(ad)) for no, ad, _ in bilgi]
    world = [(placed(V, *i), T, c) for i in inst for V, T, c in shaded]
    pick = [(placed(V, *i), T, (PICK_ID + n, 0, 0)) for n, i in enumerate(inst) for V, T, _ in shaded]
    plate = render(world, 512, R_ISO)
    images = {
        "Metadata/plate_1.png": plate,
        "Metadata/plate_1_small.png": plate.resize((128, 128), Image.LANCZOS),
        "Metadata/plate_no_light_1.png": render(world, 512, R_ISO, light=False),
        "Metadata/pick_1.png": render(pick, 512, R_ISO, light=False, ss=1),
        "Metadata/top_1.png": render(world, 512, R_TOP, flat=0.7, margin=0.2),
    }

    with zipfile.ZipFile(a.cikis, "w", zipfile.ZIP_DEFLATED) as out:
        for info in z.infolist():
            if info.filename == "3D/Objects/object_1.model":
                data = yeni_obj.encode()
            elif info.filename == "Metadata/model_settings.config":
                data = yeni_cfg.encode()
            elif info.filename in images:
                buf = io.BytesIO()
                images[info.filename].save(buf, "PNG")
                data = buf.getvalue()
            else:
                data = z.read(info.filename)
            out.writestr(info.filename, data)

    import zxingcpp
    top = images["Metadata/top_1.png"].convert("L")
    qr = {r.text for r in zxingcpp.read_barcodes(top.resize((top.width * 2, top.height * 2), Image.NEAREST))}
    print("QR (üstten):", ", ".join(sorted(qr)) or "OKUNMADI")
    assert qr, "QR okunmadı"
    print("yazıldı:", a.cikis)


if __name__ == "__main__":
    main()
