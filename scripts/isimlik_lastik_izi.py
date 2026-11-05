"""Hazır bir isimlik 3MF'ine lastik izi bandı ekler (beyaz kabartma), gerisine dokunmaz.

İstek (Antalya 7/24 Oto Lastik Tamiri, uzar1 M06): "isimle numara arasında çok boşluk var, oraya lastik şeritleri
çizer misin, lastik izi yani, beyaz renk olsun"; sonra "daha tasarımsal yap, İnce Oto Lastik'in internet sitesine
yaptığımız tarzda".

- **Desen:** İnce Oto Lastik'in sitesindeki lastik izi (`scripts/ince_sayfa.py`, `tread("band")`): ortada gidiş
  yönüne (sağa) bakan ok biçimli diş, üstünde ve altında omuz blokları; karo 40 × 120 birim.
- **Stiller:**
  - `ince` (varsayılan): sitedeki gibi bant 12° eğik, sağa doğru yükselir. Sitede iki ucu maskeyle soluyor
    (%14 → %34 belirir, %74 → %92 kaybolur); kabartmada saydamlık olmadığı için uçlarda dişler küçülür.
  - `duz`: yatay bant, yazı sütununun tam genişliğinde, tam karo sayısıyla.
- **Yerleşim:** yazılara 2 mm'den, QR karosuna 3 mm'den, panel kenarına 2,5 mm'den yakın düşen diş konmaz; küçülen
  dişlerde en ince çizgi 0,8 mm'nin altına inmez.
- **Baskı:** 2 mm kabartma, panelin yüzünde (z 10 → 12), "Kabartma (beyaz)" parçasına eklenir; filament ataması
  ve proje ayarları olduğu gibi kalır. Önizleme görselleri (tabla, üstten, seçim) yeniden çizilir.
- **Kontroller:** yazılara uzaklık, en ince çizgi ve ara, ağ kapalı, QR üstten görünümde okunuyor.

Okuma yönü: u = y (soldan sağa), v = -x (aşağıdan yukarı); panel 120 × 90 mm tablada yatar.

Kullanım:
  python3 scripts/isimlik_lastik_izi.py <giriş.3mf> <çıkış.3mf> --u 27.2 78.9 --v -17.7 12.3 [--stil ince|duz]
    --u: yazı sütununun soldan sağa sınırı; --v: boşluğun alt ve üst kenarı (yazıların kenarları)
    ince: --boy (bant yüksekliği, mm), --aci (derece), --bas/--son (bandın u'da başı ve sonu) [--onizleme png]
"""
import argparse
import io
import os
import re
import sys
import zipfile

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anahtarlik import R_ISO, R_TOP, SHOW, BLACK, RED, WHITE, placed  # noqa: E402
from cift_tarafli_isimlik import PICK_ID, mesh_xml, render  # noqa: E402

KABARTMA = 2.0
YUZ_Z = 10.0
YAZI_ARA, QR_ARA, KENAR_ARA = 2.0, 3.0, 2.5
MIN_CIZGI = 0.8
# sitedeki lastik izi karosu (40 × 120, y aşağı): ok biçimli diş ve iki omuz bloğu
KARO_W, KARO_H = 40.0, 120.0
DIS = [(5, 24), (17, 24), (32, 60), (17, 96), (5, 96), (20, 60)]
OMUZ = [(9, 4, 27, 16), (9, 104, 27, 116)]
DIS_KALIN = 11.08                                       # ok dişinin dik kalınlığı (12 · sin 67,4°), birim
OMUZ_KALIN = 12.0
ARA = 8.0                                              # omuz ile diş arası, birim
ICERIK_X, ICERIK_Y = (5.0, 32.0), (4.0, 116.0)       # karonun dolu kısmı
MASKE = (0.14, 0.34, 0.74, 0.92)                       # sitedeki bant maskesi (belir → tam → kaybol)


def _yuvarlak_dikdortgen(x0, y0, x1, y1, r, n=6):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        pts += [(cx + r * np.cos(np.radians(a0 + 90 * i / n)), cy + r * np.sin(np.radians(a0 + 90 * i / n)))
                for i in range(n + 1)]
    return pts


KARO = [DIS] + [_yuvarlak_dikdortgen(*r, 2.0) for r in OMUZ]


def duz_bant(u0, u1, vc, n=10):
    """Yatay bant: n karo u0..u1'e tam sığar, v ortası vc. Döner: (çokgenler, ölçek)."""
    k = (u1 - u0) / ((n - 1) * KARO_W + (ICERIK_X[1] - ICERIK_X[0]))
    yc = (ICERIK_Y[0] + ICERIK_Y[1]) / 2
    polys = [[(u0 + (x - ICERIK_X[0] + i * KARO_W) * k, vc - (y - yc) * k) for x, y in p]
             for i in range(n) for p in KARO]
    return [(p, 1.0) for p in polys], k


def egik_bant(merkez, aci, boy, bas, son):
    """İnce'nin sitesindeki bant: merkezden geçen, `aci` derece yükselen eksen; u'da bas..son arası.
    Her öğe (diş, omuz) eksendeki yerine göre maskeyle küçülür. Döner: ([(çokgen, ölçek)], k)."""
    k = boy / KARO_H
    a = np.radians(aci)
    d, nrm = np.array([np.cos(a), np.sin(a)]), np.array([-np.sin(a), np.cos(a)])
    mu, mv = merkez
    s0, s1 = (bas - mu) / np.cos(a), (son - mu) / np.cos(a)  # eksen boyunca (merkez 0)
    p = KARO_W * k
    out = []
    for i in range(int(np.floor(s0 / p)) - 1, int(np.ceil(s1 / p)) + 1):
        for poly in KARO:
            P = np.array([((x - 20) * k + i * p, (60 - y) * k) for x, y in poly])   # eksen koordinatı (s, n)
            c = P.mean(0)
            t = (c[0] - s0) / (s1 - s0)
            b0, b1, b2, b3 = MASKE
            f = 0.0 if t <= b0 or t >= b3 else min(1.0, (t - b0) / (b1 - b0), (b3 - t) / (b3 - b2))
            if f <= 0:
                continue
            P = c + (P - c) * f
            uv = np.array([mu, mv]) + P[:, :1] * d + P[:, 1:] * nrm
            out.append(([tuple(q) for q in uv], f))
    return out, k


def dunya(polys):
    """(u, v) → tablada (x, y) = (-v, u): 90° döndürme (yansıma değil); dış sarım saat yönünün tersine."""
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


def ust_yuz(V, T, z):
    """z yüksekliğindeki yukarı bakan yüzün (u, v) düzlemindeki alanı."""
    P = V[T]
    n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
    sec = (n[:, 2] > 1e-9) & (np.abs(P[:, :, 2] - z).max(1) < 1e-3)
    return unary_union([Polygon([(y, -x) for x, y, _ in tri]) for tri in P[sec]]).buffer(0)


def engeller(parts, bilgi):
    yazi = unary_union([ust_yuz(*parts[no], YUZ_Z + KABARTMA) for no, ad, _ in bilgi if "Kabartma" in ad])
    dolgu = unary_union([ust_yuz(*parts[no], YUZ_Z) for no, ad, _ in bilgi if "Dolgu" in ad])
    panel = ust_yuz(*parts[next(no for no, ad, _ in bilgi if ad.startswith("Panel"))], YUZ_Z)
    return yazi, dolgu, panel.buffer(-KENAR_ARA)


def yerlestir(ogeler, yazi, dolgu, alan):
    """Engellere yakın öğeleri atar. Döner: kalan [(Polygon, ölçek)]."""
    kalan = []
    for p, f in ogeler:
        g = Polygon(p)
        if alan.contains(g) and g.distance(yazi) >= YAZI_ARA and g.distance(dolgu) >= QR_ARA:
            kalan.append((g, f))
    return kalan


def onizleme(parts, bilgi, ek, yol, s=10):
    """Panelin önden düz görünümü (okuma yönünde)."""
    U0, U1, V0, V1 = -36, 88, -47, 47
    im = Image.new("RGB", (int((U1 - U0) * s), int((V1 - V0) * s)), (226, 226, 230))
    d = ImageDraw.Draw(im)
    tr = lambda u, v: ((u - U0) * s, (V1 - v) * s)  # noqa: E731
    for no, ad, _ in bilgi:
        if "Sehpa" in ad:
            continue
        V, T = parts[no]
        P = V[T]
        n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
        zt = P[:, :, 2].max()
        sec = (n[:, 2] > 1e-9) & ((np.abs(P[:, :, 2] - zt).max(1) < 1e-3) | ad.startswith("Panel"))
        for tri in P[sec]:
            d.polygon([tr(y, -x) for x, y, _ in tri], fill=renk(ad))
    for g in ek:
        d.polygon([tr(*q) for q in g.exterior.coords], fill=SHOW[WHITE])
    im.save(yol)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("giris")
    ap.add_argument("cikis")
    ap.add_argument("--u", nargs=2, type=float, required=True)
    ap.add_argument("--v", nargs=2, type=float, required=True)
    ap.add_argument("--stil", choices=("ince", "duz"), default="ince")
    ap.add_argument("--karo", type=int, default=10, help="duz: karo sayısı")
    ap.add_argument("--boy", type=float, default=16.0, help="ince: bant yüksekliği (mm)")
    ap.add_argument("--aci", type=float, default=12.0, help="ince: eğim (derece, sağa doğru yükselir)")
    ap.add_argument("--bas", type=float, default=None, help="ince: bandın u'da başı (varsayılan sütun − 14)")
    ap.add_argument("--son", type=float, default=None, help="ince: bandın u'da sonu (varsayılan panel kenarı)")
    ap.add_argument("--kay", type=float, default=0.0, help="ince: bandı v'de kaydır (mm)")
    ap.add_argument("--onizleme", default=None)
    a = ap.parse_args()

    z = zipfile.ZipFile(a.giris)
    obj_s, parts = oku(z)
    cfg = z.read("Metadata/model_settings.config").decode()
    bilgi = parca_bilgisi(cfg)
    hedef = next(no for no, ad, _ in bilgi if ad == "Kabartma (beyaz)")
    yazi, dolgu, alan = engeller(parts, bilgi)

    vc = (a.v[0] + a.v[1]) / 2 + a.kay
    uc = (a.u[0] + a.u[1]) / 2
    if a.stil == "duz":
        ogeler, k = duz_bant(a.u[0], a.u[1], vc, a.karo)
    else:
        bas = a.u[0] - 14 if a.bas is None else a.bas
        son = alan.bounds[2] + 4 if a.son is None else a.son
        ogeler, k = egik_bant((uc, vc), a.aci, a.boy, bas, son)
    fmin = MIN_CIZGI / (min(DIS_KALIN, OMUZ_KALIN) * k)
    ogeler = [(p, f) for p, f in ogeler if f >= fmin]
    kalan = yerlestir(ogeler, yazi, dolgu, alan)
    atilan = len(ogeler) - len(kalan)
    birlesik = unary_union([g for g, _ in kalan])
    geoms = list(birlesik.geoms) if isinstance(birlesik, MultiPolygon) else [birlesik]
    cizgi = min(DIS_KALIN, OMUZ_KALIN) * k * min(f for _, f in kalan)
    ara = min(ARA * k, min((g1.distance(g2) for i, (g1, _) in enumerate(kalan) for g2, _ in kalan[i + 1:]
                            if g1.distance(g2) > 0), default=99))
    yakin = min(g.distance(yazi) for g, _ in kalan)
    print(f"bant ({a.stil}): {len(kalan)} öğe ({atilan} öğe yazıya / kenara yakın diye konmadı), "
          f"ölçek {k:.4f} mm/birim; u {birlesik.bounds[0]:.1f} … {birlesik.bounds[2]:.1f}, "
          f"v {birlesik.bounds[1]:.1f} … {birlesik.bounds[3]:.1f}")
    print(f"kontrol: yazılara en yakın {yakin:.1f} mm (≥ {YAZI_ARA:g}), en ince çizgi {cizgi:.2f} mm, en dar ara "
          f"{ara:.2f} mm (≥ {MIN_CIZGI:g})")
    assert yakin >= YAZI_ARA and cizgi >= MIN_CIZGI - 1e-6 and ara >= MIN_CIZGI, "bant baskı kurallarına uymuyor"
    if a.onizleme:
        onizleme(parts, bilgi, [g for g, _ in kalan], a.onizleme)

    cs = m3.CrossSection([np.array(p) for p in dunya([list(g.exterior.coords)[:-1] for g in geoms])],
                         m3.FillRule.NonZero)
    man = cs.extrude(KABARTMA).translate((0, 0, YUZ_Z))
    mesh = man.to_mesh()
    Vb = np.asarray(mesh.vert_properties)[:, :3].astype(float)
    Tb = np.asarray(mesh.tri_verts).astype(int)
    print(f"kabartma: {man.volume():.0f} mm³ (~{man.volume() * 1.24e-3:.1f} g beyaz, iki takım "
          f"~{2 * man.volume() * 1.24e-3:.1f} g)")
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

    # denetim: ağ kapalı, QR okunuyor
    from collections import Counter
    kenar = Counter(tuple(sorted(e)) for a_, b_, c_ in parts[hedef][1] for e in ((a_, b_), (b_, c_), (c_, a_)))
    acik = sum(1 for v in kenar.values() if v != 2)
    import zxingcpp
    top = images["Metadata/top_1.png"].convert("L")
    qr = {r.text for r in zxingcpp.read_barcodes(top.resize((top.width * 2, top.height * 2), Image.NEAREST))}
    print(f"ağ: açık kenar {acik}; QR (üstten): {', '.join(sorted(qr)) or 'OKUNMADI'}")
    assert acik == 0 and qr, "ağ açık ya da QR okunmadı"
    print("yazıldı:", a.cikis)


if __name__ == "__main__":
    main()
