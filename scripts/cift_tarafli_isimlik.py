"""Bambu Studio isimlik 3MF dosyasını çift taraflı (arka yüzü de yazılı) yapar.

Girdi olarak MakerWorld "Parametric Model Maker" ile üretilmiş, tek parçalı ve
AMS ile boyanmış (gövde bir renk, kabartma yazı başka renk) bir isimlik alır.

Yapılanlar:
  * Ön yüzdeki kabartma yazı olduğu gibi korunur.
  * Arka yüze aynı yazı AYNALANARAK gömülür (inlay): baskı tablaya bakan ilk
    katmanlarda yazı rengiyle basılır, isimliği çevirince düz okunur.
    Destek gerekmez, yapıştırma gerekmez, tek seferde basılır.
  * Gövdenin dış hattı ve harf aralarındaki boşluklar orijinaliyle aynı kalır.
    Çevirince yazının sırası ters döndüğü için arka yazıdaki Ş'nin çengeli önden
    bakınca I-K'nın altına denk gelir; siyah eklememek için arka yazıdaki çengel
    mevcut siyah çerçevenin içine sığacak kadar küçültülür. Arka yazının gövde
    boşluklarının üstünden geçtiği küçük yerlerde harf biraz kalın basılır.
  * Model üç ayrı parça olarak kaydedilir (Gövde / Ön Yazı / Arka Yazı) ve her
    parçaya filament atanır; Bambu Studio'da renkler "Nesneler" listesinden
    parça bazında değiştirilebilir. Yazıcı/filament/baskı ayarları aynen kalır.

Girdi : Bambu Studio / MakerWorld .3mf dosyası
Çıktı : çift taraflı .3mf dosyası (+ isteğe bağlı önizleme PNG'si)

Kullanım:
  pip install numpy manifold3d pillow
  python3 scripts/cift_tarafli_isimlik.py GIRDI.3mf CIKTI.3mf [--derinlik 1.0] [--onizleme onizleme.png]
"""
import argparse
import datetime
import io
import json
import re
import xml.etree.ElementTree as ET
import zipfile

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw, ImageFont

NS_CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
NS_PROD = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
NS = {"c": NS_CORE, "p": NS_PROD}
PICK_ID = 37  # Bambu Studio'nun plaka nesne seçim görselinde kullandığı kimlik


# ---------------------------------------------------------------- 3MF okuma

def paint_to_extruder(code):
    """Bambu'nun `paint_color` kodunu filament numarasına çevirir ("4"->1, "8"->2, "0C"->3 ...)."""
    if not code:
        return None
    code = code.upper()
    if len(code) == 2 and code.endswith("C"):
        return int(code[0], 16) + 3
    if len(code) == 1:
        return int(code, 16) >> 2
    return None  # bölünmüş (karışık) üçgen, bu amaçla gerekmiyor


def read_source(path):
    z = zipfile.ZipFile(path)
    files = {n: z.read(n) for n in z.namelist()}
    root = ET.fromstring(files["3D/3dmodel.model"])
    comp = root.find(".//c:object/c:components/c:component", NS)
    sub_path = comp.get(f"{{{NS_PROD}}}path").lstrip("/")
    comp_tf = comp.get("transform")
    item_tf = root.find(".//c:build/c:item", NS).get("transform")

    sub = ET.fromstring(files[sub_path])
    mesh = sub.find(".//c:object/c:mesh", NS)
    V = np.array([[float(v.get(a)) for a in "xyz"] for v in mesh.iter(f"{{{NS_CORE}}}vertex")])
    tris = list(mesh.iter(f"{{{NS_CORE}}}triangle"))
    T = np.array([[int(t.get(a)) for a in ("v1", "v2", "v3")] for t in tris])
    paint = [paint_to_extruder(t.get("paint_color")) for t in tris]
    return files, sub_path, comp_tf, item_tf, V, T, paint


def majority(values, default):
    values = [v for v in values if v]
    return max(set(values), key=values.count) if values else default


# ---------------------------------------------------------------- geometri

def strip(y0, y1, x0=-1e4, x1=1e4):
    return m3.CrossSection.square((x1 - x0, y1 - y0)).translate((x0, y0))


def row_limits(let, y_min, y_max, frac=0.3, step=0.25):
    """Yazının en alt satırının taban çizgisi ile en üst satırın tepe çizgisini bulur
    (Ş'nin çengeli, İ'nin noktası gibi dar çıkıntıları hariç tutar)."""
    ys = np.arange(y_min, y_max, step)
    widths = np.array([(let ^ strip(y, y + step)).area() / step for y in ys])
    wide = ys[widths >= frac * widths.max()]
    return wide.min(), wide.max() + step


def shrink_protrusion(isl, inner, y_ref, below, aspect=2.0, step=0.25):
    """Harfin taban (ya da tepe) çizgisinden taşan çıkıntısını (Ş'nin çengeli, İ'nin
    noktası) `inner` içine sığana kadar bağlandığı yerin etrafında küçültür.
    Yükseklik sığacak kadar, genişlik en fazla `aspect` katı oranında küçülür."""
    x0, y0, x1, y1 = isl.bounds()
    if (y0 >= y_ref - 0.5) if below else (y1 <= y_ref + 0.5):
        return isl
    # çıkıntının harfe bağlandığı en dar yer ("boyun")
    ys = np.arange(y_ref - 4, y_ref + 1e-6, step) if below else np.arange(y_ref, y_ref + 4 + 1e-6, step)
    widths = np.array([(isl ^ strip(y, y + step)).area() for y in ys])
    if (widths > 1e-6).any():
        neck = ys[np.where(widths > 1e-6, widths, np.inf).argmin()] + (0 if below else step)
        lap = 0.3 if below else -0.3  # kalan harfle üst üste binsin
        piece = isl ^ (strip(-1e4, neck + lap) if below else strip(neck + lap, 1e4))
        rest = isl - (strip(-1e4, neck) if below else strip(neck, 1e4))
        row = isl ^ strip(neck - step, neck + step)
        ax, ay = (row.bounds()[0] + row.bounds()[2]) / 2, neck + lap
    else:  # harften ayrı işaret (ör. İ'nin noktası)
        piece, rest = isl, m3.CrossSection()
        ax, ay = (x0 + x1) / 2, (y1 if below else y0)
    for sy in np.arange(1.0, 0.04, -0.01):
        sx = min(1.0, aspect * sy)
        h = piece.translate((-ax, -ay)).scale((sx, sy)).translate((ax, ay))
        if (h - inner).area() < 1e-3:
            return rest + h
    print(f"uyarı: x={ax:.1f} civarındaki çıkıntı gövdeye sığdırılamadı")
    return isl


def build_parts(V, T, depth, floor=1.0, margin=0.6):
    """Gövde, ön yazı ve arka yazı katılarını döndürür. `floor`: arka yazının gövde
    boşluklarının üstünden geçtiği yerlerde ek kalınlık; `margin`: küçültülen
    çıkıntının çevresinde kalan siyah pay (mm)."""
    M = m3.Manifold(m3.Mesh(vert_properties=V.astype(np.float32), tri_verts=T.astype(np.uint32)))
    M = max(M.decompose(), key=lambda p: p.volume())  # sıfır hacimli artıkları at
    zs = np.unique(np.round(V[:, 2], 4))
    z_bot, z_top = zs.min(), zs.max()
    # gövdenin üst yüzü: alt ve üst arasındaki en çok kullanılan z seviyesi
    mid = [z for z in zs if z_bot < z < z_top]
    z_mid = max(mid, key=lambda z: np.sum(np.isclose(V[:, 2], z)))

    sil = M.slice((z_bot + z_mid) / 2)          # gövde silueti (boşluklarıyla birlikte)
    let = M.slice((z_mid + z_top) / 2)          # ön yazı silueti
    x0, y0, x1, y1 = sil.bounds()
    cx = (x0 + x1) / 2

    def mirror(cs):  # isimlik dikey eksen etrafında çevrildiğinde görünen hâl
        return cs.translate((-cx, 0)).mirror((1, 0)).translate((cx, 0))

    # Gövde dış hattı ve boşlukları orijinaliyle aynı kalır. Aynalanan yazıda
    # dış hattan taşan çıkıntılar (Ş'nin çengeli) siyah çerçevenin içine sığacak
    # kadar küçültülür.
    lx0, ly0, lx1, ly1 = let.bounds()
    y_base, y_cap = row_limits(let, ly0, ly1)
    inner = sil.offset(-margin, m3.JoinType.Round)
    islands = []
    for isl in mirror(let).decompose():
        isl = shrink_protrusion(isl, inner, y_base, below=True)
        isl = shrink_protrusion(isl, inner, y_cap, below=False)
        islands.append(isl)
    back_let = m3.CrossSection.batch_boolean(islands, m3.OpType.Add)

    # Arka yazı, gövdedeki boşlukların (harf araları) üstünden birkaç küçük yerde
    # geçiyor. Oraları siyahla doldurmak yerine harfin kendisi (yazı rengi) biraz
    # daha kalın basılır; gövdeye siyah eklenmez, önden boşluklar yine boşluk.
    bridges = [p for p in (back_let - sil).decompose() if p.area() >= 0.5]
    bridge = m3.CrossSection.batch_boolean(bridges, m3.OpType.Add) if bridges else m3.CrossSection()
    back_let = back_let ^ (sil + bridge)  # kalan kıl payı taşmaları kırp

    height = z_mid - z_bot
    govde = sil.extrude(height).translate((0, 0, z_bot))
    govde = govde - back_let.extrude(depth + 1).translate((0, 0, z_bot - 1))
    arka = back_let.extrude(depth).translate((0, 0, z_bot))
    if bridges:
        arka = arka + bridge.extrude(depth + floor).translate((0, 0, z_bot))
    # harflerin yan yüzleri dik; trim_by_plane gövde üst yüzünü sıfır kalınlıklı
    # bir yüzey olarak da bıraktığı için ön yazıyı kesitinden yeniden çıkar
    on = let.extrude(z_top - z_mid).translate((0, 0, z_mid))
    info = dict(z_bot=z_bot, z_mid=z_mid, z_top=z_top, cx=cx,
                bridges=[p.area() for p in bridges])
    return govde, on, arka, info


def mesh_arrays(man):
    mesh = man.to_mesh()
    return np.asarray(mesh.vert_properties)[:, :3].astype(float), np.asarray(mesh.tri_verts).astype(int)


# ---------------------------------------------------------------- görsel

def parse_tf(tf):
    a = [float(v) for v in tf.split()]
    m = np.eye(4)
    m[:3, :3] = np.array(a[:9]).reshape(3, 3).T
    m[:3, 3] = a[9:12]
    return m


def rotation(azim, elev):
    a, e = np.radians(azim), np.radians(elev)
    rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    rx = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
    return rx @ rz  # kamera -z yönüne bakar; y yukarı


def render(parts, size, R, light=True, flat=None, margin=0.08, ss=3):
    """Basit z-buffer rasterleştirici. parts: [(V, T, rgb)]. Şeffaf arka planlı RGBA döner."""
    W = size * ss
    allv = np.vstack([V for V, _, _ in parts]) @ R.T
    lo, hi = allv[:, :2].min(0), allv[:, :2].max(0)
    scale = (1 - 2 * margin) * W / (hi - lo).max()
    off = W / 2 - scale * (lo + hi) / 2
    zbuf = np.full((W, W), -np.inf)
    img = np.zeros((W, W, 3))
    ldir = np.array([0.35, 0.55, 0.76])
    ldir /= np.linalg.norm(ldir)
    for V, T, rgb in parts:
        P = V @ R.T
        S = np.c_[P[:, 0] * scale + off[0], W - (P[:, 1] * scale + off[1]), P[:, 2]]
        tri = P[T]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        vis = n[:, 2] > 1e-3  # arkaya dönük ve kameraya yan duran yüzleri atla
        T, n = T[vis], n[vis]
        if flat is not None:
            shade = np.where(np.abs(n[:, 2]) > 0.5, 1.0, flat)
        elif light:
            shade = 0.38 + 0.62 * np.clip(n @ ldir, 0, 1)
        else:
            shade = np.ones(len(T))
        col = np.asarray(rgb) / 255.0
        for (a, b, c), s in zip(S[T], shade):
            xmin, xmax = int(max(min(a[0], b[0], c[0]), 0)), int(min(max(a[0], b[0], c[0]) + 1, W))
            ymin, ymax = int(max(min(a[1], b[1], c[1]), 0)), int(min(max(a[1], b[1], c[1]) + 1, W))
            if xmin >= xmax or ymin >= ymax:
                continue
            den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(den) < 1e-12:
                continue
            gx, gy = np.meshgrid(np.arange(xmin, xmax) + 0.5, np.arange(ymin, ymax) + 0.5)
            w0 = ((b[1] - c[1]) * (gx - c[0]) + (c[0] - b[0]) * (gy - c[1])) / den
            w1 = ((c[1] - a[1]) * (gx - c[0]) + (a[0] - c[0]) * (gy - c[1])) / den
            w2 = 1 - w0 - w1
            inside = (w0 >= -1e-9) & (w1 >= -1e-9) & (w2 >= -1e-9)
            if not inside.any():
                continue
            z = w0 * a[2] + w1 * b[2] + w2 * c[2]
            zb = zbuf[ymin:ymax, xmin:xmax]
            upd = inside & (z > zb)
            zb[upd] = z[upd]
            img[ymin:ymax, xmin:xmax][upd] = col * s
    alpha = np.isfinite(zbuf).astype(float)
    rgba = np.dstack([img, alpha]).reshape(size, ss, size, ss, 4).mean((1, 3))
    rgb = np.where(rgba[..., 3:] > 0, rgba[..., :3] / np.maximum(rgba[..., 3:], 1e-9), 0)
    out = np.dstack([rgb, rgba[..., 3]])
    return Image.fromarray((out * 255).round().astype(np.uint8), "RGBA")


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def display_rgb(rgb):
    # siyah/beyaz filamentleri görselde biraz yumuşat ki gölgeler seçilsin
    return tuple(int(40 + v * (225 - 40) / 255) for v in rgb)


# ---------------------------------------------------------------- 3MF yazma

def fmt(v):
    return f"{v:.9g}"


def mesh_xml(obj_id, uuid, V, T):
    out = [f'  <object id="{obj_id}" p:UUID="{uuid}" type="model">\n   <mesh>\n    <vertices>\n']
    out += [f'     <vertex x="{fmt(x)}" y="{fmt(y)}" z="{fmt(z)}"/>\n' for x, y, z in V]
    out.append("    </vertices>\n    <triangles>\n")
    out += [f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>\n' for a, b, c in T]
    out.append("    </triangles>\n   </mesh>\n  </object>\n")
    return "".join(out)


def matrix_meta(tf):
    m = parse_tf(tf)
    return " ".join(fmt(v) for v in m.reshape(-1))


def write_3mf(src_files, sub_path, comp_tf, item_tf, parts, obj_name, out_path, images):
    today = datetime.date.today().isoformat()
    n = len(parts)
    parent_id = n + 1

    # alt model: her parça ayrı bir mesh nesnesi
    head = re.search(rb"^.*?<resources>", src_files[sub_path], re.S).group(0).decode()
    sub = [head + "\n"]
    for i, (name, V, T, ext) in enumerate(parts, 1):
        sub.append(mesh_xml(i, f"000{i}0000-81cb-4c03-9d28-80fed5dfa1dc", V, T))
    sub.append(" </resources>\n <build/>\n</model>\n")

    # ana model: parçaları bileşen olarak toplayan tek nesne
    main = src_files["3D/3dmodel.model"].decode()
    main = re.sub(r'(<metadata name="ModificationDate">)[^<]*', rf"\g<1>{today}", main)
    main = re.sub(r'(<metadata name="Title">)[^<]*', rf"\g<1>{obj_name}", main)
    comps = "".join(
        f'    <component p:path="/{sub_path}" objectid="{i}" '
        f'p:UUID="000{i}0000-b206-40ff-9872-83e8017abed1" transform="{comp_tf}"/>\n'
        for i in range(1, n + 1))
    resources = (f' <resources>\n  <object id="{parent_id}" p:UUID="0000000{parent_id}-61cb-4c03-9d28-80fed5dfa1dc" '
                 f'type="model">\n   <components>\n{comps}   </components>\n  </object>\n </resources>')
    main = re.sub(r" <resources>.*?</resources>", lambda _: resources, main, flags=re.S)
    main = re.sub(r'(<item objectid=")\d+', rf"\g<1>{parent_id}", main)

    # Bambu Studio nesne/parça ayarları: parça adları ve filament atamaları
    total_faces = sum(len(T) for _, _, T, _ in parts)
    cfg = ['<?xml version="1.0" encoding="UTF-8"?>\n<config>\n',
           f'  <object id="{parent_id}">\n',
           f'    <metadata key="name" value="{obj_name}"/>\n',
           f'    <metadata key="extruder" value="{parts[0][3]}"/>\n',
           f'    <metadata face_count="{total_faces}"/>\n']
    for i, (name, V, T, ext) in enumerate(parts, 1):
        cfg += [f'    <part id="{i}" subtype="normal_part">\n',
                f'      <metadata key="name" value="{name}"/>\n',
                f'      <metadata key="matrix" value="{matrix_meta(comp_tf)}"/>\n',
                f'      <metadata key="extruder" value="{ext}"/>\n',
                f'      <mesh_stat face_count="{len(T)}" edges_fixed="0" degenerate_facets="0" '
                'facets_removed="0" facets_reversed="0" backwards_edges="0"/>\n',
                '    </part>\n']
    cfg.append("  </object>\n")
    old_cfg = src_files["Metadata/model_settings.config"].decode()
    plate = re.search(r"  <plate>.*?</plate>\n", old_cfg, re.S).group(0)
    plate = re.sub(r'(<metadata key="object_id" value=")\d+', rf"\g<1>{parent_id}", plate)
    cfg.append(plate)
    cfg.append("  <assemble>\n  </assemble>\n</config>\n")

    new = dict(src_files)
    new[sub_path] = "".join(sub).encode()
    new["3D/3dmodel.model"] = main.encode()
    new["Metadata/model_settings.config"] = "".join(cfg).encode()
    for name, im in images.items():
        buf = io.BytesIO()
        im.save(buf, "PNG")
        new[name] = buf.getvalue()
    order = ["[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model", "3D/_rels/3dmodel.model.rels"]
    names = [k for k in order if k in new] + sorted(k for k in new if k not in order)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for k in names:
            z.writestr(k, new[k])


# ---------------------------------------------------------------- ana akış

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("girdi")
    ap.add_argument("cikti")
    ap.add_argument("--derinlik", type=float, default=1.0,
                    help="arka yazının gömülme derinliği, mm (katman yüksekliğinin katı olsun; varsayılan 1.0)")
    ap.add_argument("--ad", default="Cift_Tarafli_Isimlik", help="Bambu Studio'daki nesne adı")
    ap.add_argument("--onizleme", help="ön/arka yüz önizleme PNG'si yolu")
    args = ap.parse_args()

    files, sub_path, comp_tf, item_tf, V, T, paint = read_source(args.girdi)
    z = V[T][:, :, 2]
    top = np.isclose(z, z.max()).all(1)
    bottom = np.isclose(z, z.min()).all(1)
    ext_text = majority([p for p, t in zip(paint, top) if t], 2)
    ext_body = majority([p for p, b in zip(paint, bottom) if b], 1)

    govde, on, arka, info = build_parts(V, T, args.derinlik)
    parts = [("Gövde", *mesh_arrays(govde), ext_body),
             ("Ön Yazı", *mesh_arrays(on), ext_text),
             ("Arka Yazı", *mesh_arrays(arka), ext_text)]
    for name, v, t, ext in parts:
        print(f"{name:10s} filament {ext}  üçgen {len(t):6d}  z {v[:, 2].min():.2f}..{v[:, 2].max():.2f}")
    print(f"arka yazı derinliği {args.derinlik} mm; boşluk üstünden geçen arka yazı parçaları (mm²): "
          + ", ".join(f"{a:.1f}" for a in info["bridges"]))

    cfg = json.loads(files["Metadata/project_settings.config"])
    colours = cfg.get("filament_colour", ["#000000", "#FFFFFF"])

    def colour(ext):
        return display_rgb(hex_rgb(colours[ext - 1] if ext - 1 < len(colours) else "#808080"))

    shaded = [(v, t, colour(ext)) for _, v, t, ext in parts]
    R_iso = rotation(0, -50)                     # önden ve yukarıdan bakış
    R_back = rotation(180, 180)                  # dikey eksen etrafında çevrilmiş: arka yüz
    R_top = rotation(0, 0)
    plate = render(shaded, 512, R_iso)
    images = {
        "Metadata/plate_1.png": plate,
        "Metadata/plate_1_small.png": plate.resize((128, 128), Image.LANCZOS),
        "Metadata/plate_no_light_1.png": render(shaded, 512, R_iso, light=False),
        "Metadata/pick_1.png": render([(v, t, (PICK_ID, 0, 0)) for _, v, t, _ in parts], 512, R_iso, light=False, ss=1),
    }
    # tabla üstten görünümü: nesneyi tablada durduğu açıyla çiz
    tf = parse_tf(item_tf) @ parse_tf(comp_tf)
    world = [((np.c_[v, np.ones(len(v))] @ tf.T)[:, :3], t, c) for v, t, c in shaded]
    images["Metadata/top_1.png"] = render(world, 512, R_top, flat=0.7, margin=0.2)
    write_3mf(files, sub_path, comp_tf, item_tf, [(n, v, t, e) for n, v, t, e in parts],
              args.ad, args.cikti, images)
    print("yazıldı:", args.cikti)

    if args.onizleme:
        # orijinal model, boyamasına göre renklendirilmiş (karşılaştırma için)
        is_text = np.array([p == ext_text for p in paint])
        original = [(V, T[~is_text], colour(ext_body)), (V, T[is_text], colour(ext_text))]
        panels = [(render(original, 760, R_top, margin=0.04), "Orijinal - ön yüz"),
                  (render(shaded, 760, R_top, margin=0.04), "Yeni - ön yüz"),
                  (render(shaded, 760, R_back, margin=0.04), "Yeni - arka yüz (çevrilmiş)"),
                  (render(shaded, 760, R_iso, margin=0.04), "Yeni - perspektif")]
        PW, PH, TOP, GAP = 760, 470, 70, 24
        canvas = Image.new("RGB", (2 * PW + 3 * GAP, 2 * (PH + TOP) + 2 * GAP), (244, 246, 250))
        d = ImageDraw.Draw(canvas)
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 32)
        except OSError:
            font = ImageFont.load_default()
        for i, (im, title) in enumerate(panels):
            px, py = GAP + (i % 2) * (PW + GAP), GAP + (i // 2) * (PH + TOP)
            # renkli zemin: harf aralarındaki boşluklar zeminden seçilsin
            d.rounded_rectangle((px, py + TOP - 10, px + PW, py + TOP + PH - 10), 18, fill=(196, 210, 228))
            canvas.paste(im, (px, py + TOP - 10 + (PH - PW) // 2), im)
            tw = d.textlength(title, font=font)
            d.text((px + PW / 2 - tw / 2, py + 12), title, fill=(40, 44, 52), font=font)
        canvas.save(args.onizleme)
        print("önizleme:", args.onizleme)


if __name__ == "__main__":
    main()
