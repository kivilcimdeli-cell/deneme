"""BOYDE LABS – esnafa özel şekilli anahtarlıklar: 5 örnek, hepsi BOYDE LABS markalı, arkalı önlü, Shopier görselleri.

Kullanıcı: "emlakçılar vs. için ev şeklinde vs. böyle esnaflara özel anahtarlıklar üret, hepsi BOYDE markalı olsun;
5 örnek, kabartmalı ön yüzey, düz arka yüzey ve Shopier için hazırla".

Yapı toptan anahtarlıklarla aynı (scripts/boyde_anahtarlik_toptan.py: Key, gövde 3,2 mm pahlı, ön yüz 0,8 mm kabartma,
arka yüz yüzeyle aynı hizada gömme yazı, delik Ø5,2 mm, çevresinde en az 3,5 mm et):

  E01 Ev        emlakçılar        41 × 49  beyaz    delik çatının tepesinde; önde işaret ve BOYDE LABS,
                                                    arkada "Yeni evinize hayırlı olsun."
  E02 Araba     oto galeriler     72 × 34  siyah    delik tavanda; önde BOYDE LABS; arkada "Yolunuz açık olsun."
  E03 Oda       oteller           34 × 60  turuncu  klasik otel anahtarlığı, delik dar uçta; önde büyük oda
                                                    numarası ve BOYDE LABS; arkada "Anahtarınızı resepsiyona bırakınız."
  E04 Diş       diş klinikleri    36 × 43  beyaz    delik kronun ortasında; önde BOYDE LABS; arkada
                                                    "Gülüşünüz bize emanet."
  E05 Kemik     veteriner, pet    68 × 27  gri      delik bir uçta; önde BOYDE LABS; arkada "Patili dostunuz bize
                                                    emanet."
Markalar uydurulmaz: hepsinde kendi markamız (katalog ve Shopier için örnek; müşterininki kendi logosuyla basılır).

Çıktı : boyde_labs/anahtarlik_esnaf/kaynak/<model>.npz (git'e girmez), <model>_on.png, <model>_arka.png
        boyde_labs/anahtarlik_esnaf/fotograf/*.jpg (Blender; --foto)
        boyde_labs/anahtarlik_esnaf/shopier/*.jpg (1200 × 1200; --shopier)
Kullanım:
  python3 scripts/boyde_anahtarlik_esnaf.py              # modeller, ön ve arka görünüş, baskı kontrolü
  python3 scripts/boyde_anahtarlik_esnaf.py --foto       # fotoğraflar (bpy 4.2)
  python3 scripts/boyde_anahtarlik_esnaf.py --shopier    # Shopier görselleri
"""
import os
import sys

import manifold3d as m3
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_anahtarlik_toptan as T  # noqa: E402

A, S = T.A, T.S
J = m3.JoinType.Round
BLACK, WHITE, ORANGE, GRAY = T.BLACK, T.WHITE, T.ORANGE, T.GRAY
OUT = os.path.join(A.ROOT, "boyde_labs", "anahtarlik_esnaf")
SRC = os.path.join(OUT, "kaynak")
FOTO = os.path.join(OUT, "fotograf")
HOLE = 2.6
SEKTOR = {"e01_ev": "Emlakçılar için", "e02_araba": "Oto galeriler için", "e03_oda": "Oteller için",
          "e04_dis": "Diş klinikleri için", "e05_kemik": "Veteriner ve pet shoplar için"}


def soft(cs, r=2.0):
    """Köşeleri yuvarlar (içe ve dışa): sivri uç kalmaz."""
    return cs.offset(-r, J).offset(r, J).offset(r * 0.6, J).offset(-r * 0.6, J)


def centroid(cs):
    """Alanın ağırlık merkezi (mm)."""
    sx = sy = area = 0.0
    for p in cs.to_polygons():
        x, y = np.asarray(p)[:, 0], np.asarray(p)[:, 1]
        x1, y1 = np.roll(x, -1), np.roll(y, -1)
        c = x * y1 - x1 * y
        area += c.sum() / 2
        sx += ((x + x1) * c).sum() / 6
        sy += ((y + y1) * c).sum() / 6
    return sx / area, sy / area


def up_dir(outline, hole_xy):
    """Asılınca yukarı bakan yön: ağırlık merkezinden deliğe."""
    d = np.array(hole_xy) - np.array(centroid(outline))
    return tuple(float(v) for v in d / np.linalg.norm(d))


def key(kod, name, ad, desc, outline, hole_xy, body):
    return T.Key(name, kod, ad, desc, outline, A.circle(HOLE, *hole_xy), hole_xy, body, up_dir(outline, hole_xy))


def back_lines(lines, colour, accent):
    """Arka yüz: iki satır mesaj, kısa çizgi, shopier.com/boyde (hepsi x = 0'a ortalı)."""
    specs = [("sg6", s, 3.4, 6.0 - 5.2 * i, colour) for i, s in enumerate(lines)]
    y = 6.0 - 5.2 * len(lines)
    specs += [("bar", 10.0, 0.8, y + 0.6, accent), ("outfit", "shopier.com/boyde", 2.9, y - 3.8, colour)]
    return T.lines(specs)


# ---------------------------------------------------------------- modeller

def e01_ev():
    """Ev: gövde dikdörtgen, üstte saçaklı üçgen çatı ve baca; delik çatının tepesinde."""
    W, Hb, Hr = 40.0, 28.0, 22.0                          # gövde eni, gövde ve çatı boyu
    body = A.rect(-W / 2, -Hb / 2, W / 2, Hb / 2)
    roof = A.polygon([(-W / 2 - 2.0, Hb / 2 - 1.0), (W / 2 + 2.0, Hb / 2 - 1.0), (0.0, Hb / 2 + Hr)])
    chimney = A.rect(W / 2 - 13.0, Hb / 2 + 4.0, W / 2 - 7.0, Hb / 2 + 16.0)
    outline = soft(A.union(body, roof, chimney), 1.6)
    hx, hy = 0.0, Hb / 2 + Hr - 9.0
    k = key("E01", "e01_ev", "Ev", "Emlakçılar için ev biçimi; delik çatının tepesinde. Önde kabartma siyah işaret, "
            "BOYDE ve turuncu LABS; arkada \"Yeni evinize hayırlı olsun.\"", outline, (hx, hy), WHITE)
    mark, _ = T.logo(11.0, 0, 0, "tc", BLACK)
    word, _ = T.wordmark(6.4, 0, 0, BLACK, align="c")
    front = T.column([mark, T.below(mark, word, 2.6)])
    back = back_lines(["Yeni evinize", "hayırlı olsun."], BLACK, ORANGE)
    box = (-W / 2 + 1.6, -Hb / 2 + 1.6, W / 2 - 1.6, Hb / 2 + 3.0)
    T.place(k, front, back, box)
    return k


def e02_araba():
    """Araba (yandan), anahtarlık için biraz yüksek (boy 1,4 kat): delik ağırlık merkezinin tam üstünde, tavanın
    altında (asılınca araba düz durur); yazı gövdede, deliğin altında."""
    shape, _, wc, wr, _ = A.car_silhouette(72.0)
    b = shape.bounds()
    shape = shape.translate((-(b[0] + b[2]) / 2, -b[1])).scale((1.0, 1.4))
    outline = soft(shape, 1.2)
    b = outline.bounds()
    hx = centroid(outline)[0]
    hy = (A.rect(hx - 0.2, b[1], hx + 0.2, b[3] + 1) ^ outline).bounds()[3] - 7.0     # tavanın 7 mm altı
    k = key("E02", "e02_araba", "Araba", "Oto galeriler için araba biçimi; delik tavanda. Önde kabartma beyaz "
            "BOYDE ve turuncu LABS; arkada \"Yolunuz açık olsun.\"", outline, (hx, hy), BLACK)
    word, _ = T.wordmark(6.4, 0, 0, WHITE, align="c")
    back = T.lines([("sg6", "Yolunuz açık olsun.", 3.2, 2.6, WHITE), ("outfit", "shopier.com/boyde", 2.9, -2.6,
                                                                          ORANGE)])
    box = (b[0] + 15.0, b[1] + 7.5, b[2] - 11.0, hy - HOLE - 2.6)        # ön cam eğiminden uzak
    T.place(k, word, back, box, back_box=(b[0] + 13.0, b[1] + 6.0, b[2] - 13.0, hy - HOLE - 4.4))
    return k


def e03_oda():
    """Otel oda anahtarlığı: alt ucu geniş, üst ucu dar damla (iki dairenin zarfı); delik dar üst uçta."""
    outline = (A.circle(8.5, 0.0, 21.5, 96) + A.circle(17.0, 0.0, -12.5, 160)).hull()
    b = outline.bounds()
    hx, hy = 0.0, b[3] - 7.0
    k = key("E03", "e03_oda", "Oda", "Oteller için klasik oda anahtarlığı; delik dar uçta. Önde kabartma büyük siyah "
            "oda numarası ve BOYDE LABS; arkada \"Anahtarınızı resepsiyona bırakınız.\"", outline, (hx, hy), ORANGE)
    no = S.t("sg7", "204", 10.0, 0, 0, "c", 0.4)
    word, _ = T.wordmark(4.6, 0, 0, BLACK, WHITE, align="c")
    front = T.column([[(no, BLACK)], T.below([(no, BLACK)], word, 3.4)])
    back = T.lines([("sg6", "Anahtarınızı", 3.2, 7.4, BLACK), ("sg6", "resepsiyona", 3.2, 2.4, BLACK),
                    ("sg6", "bırakınız.", 3.2, -2.6, BLACK), ("bar", 10.0, 0.8, -6.6, WHITE)])
    box = (-11.5, b[1] + 8.0, 11.5, b[1] + 30.0)               # damlanın geniş alt kısmı
    T.place(k, front, back, box)
    return k


def e04_dis():
    """Diş: iki tümsekli kron, iki kök; delik kronun ortasında."""
    outline = soft(S.ic_tooth(0.0, 0.0, 43.0), 1.4)
    b = outline.bounds()
    hx, hy = 0.0, b[3] - 10.2
    k = key("E04", "e04_dis", "Diş", "Diş klinikleri için diş biçimi; delik kronun ortasında. Önde kabartma siyah "
            "BOYDE ve turuncu LABS; arkada \"Gülüşünüz bize emanet.\"", outline, (hx, hy), WHITE)
    word, _ = T.wordmark(5.6, 0, 0, BLACK, align="c")
    back = T.lines([("sg6", "Gülüşünüz", 3.2, 3.0, BLACK), ("sg6", "bize emanet.", 3.2, -2.2, BLACK),
                    ("bar", 10.0, 0.8, -6.4, ORANGE)])
    T.place(k, word, back, (-13.5, b[1] + 17.0, 13.5, hy - HOLE - 2.0),
            back_box=(-14.5, b[1] + 17.0, 14.5, hy - HOLE - 1.6))
    return k


def e05_kemik():
    """Kemik: iki ucunda ikişer yuvarlak, ortada gövde; delik sol üst yuvarlakta."""
    L, R, dy = 68.0, 7.6, 6.0
    ends = [A.circle(R, sx * (L / 2 - R), sy * dy, 96) for sx in (-1, 1) for sy in (-1, 1)]
    shaft = A.rect(-L / 2 + R, -7.0, L / 2 - R, 7.0)
    outline = soft(A.union(shaft, *ends), 1.8)
    hx, hy = -L / 2 + R, dy
    k = key("E05", "e05_kemik", "Kemik", "Veteriner ve pet shoplar için kemik biçimi; delik bir uçta. Önde kabartma "
            "siyah BOYDE ve beyaz LABS; arkada \"Patili dostunuz bize emanet.\"", outline, (hx, hy), GRAY)
    word, _ = T.wordmark(5.8, 0, 0, BLACK, WHITE, align="c")
    back = T.lines([("sg6", "Patili dostunuz", 3.2, 3.0, BLACK), ("sg6", "bize emanet.", 3.2, -2.2, BLACK)])
    box = (-L / 2 + 2 * R + 2.0, -5.6, L / 2 - 2 * R - 2.0, 5.6)
    T.place(k, word, back, box)
    return k


MODELS = [e01_ev, e02_araba, e03_oda, e04_dis, e05_kemik]
KEYS = ["e01_ev", "e02_araba", "e03_oda", "e04_dis", "e05_kemik"]


def bagla():
    """Toptan anahtarlık betiklerini (kaydet, görünüş, fotoğraf, Shopier) bu klasöre ve modellere çevirir."""
    T.OUT, T.SRC, T.FOTO, T.MODELS, T.KEYS = OUT, SRC, FOTO, MODELS, KEYS


# ---------------------------------------------------------------- fotoğraf

# kapak dizilişi: sıra sıra (model, ters çevrili mi, açı)
KAPAK = [[("e01_ev", False, -7), ("e02_araba", False, 4), ("e03_oda", False, -5), ("e04_dis", True, 6)],
         [("e04_dis", False, 5), ("e05_kemik", False, -4), ("e01_ev", True, 6), ("e03_oda", True, -4)]]


def kapak(samples, size=(1600, 1600)):
    """Kapak: beş model masada karışık (her biri önden, üçü bir de arkadan), iki sıra, aralarında 8 mm; beyaz fon.
    Parçalar kadrajın üst yarısında (Shopier kapağında başlık alta gelir)."""
    import boyde_anahtarlik_foto as AF
    sc = AF.studio(False, samples, size)
    loaded = {k: AF.load(k) for k in KEYS}
    rows = []
    for row in KAPAK:
        items = []
        for key, flip, a in row:
            meta, parts = loaded[key]
            M = AF.flat(meta, a, 0, 0, flip)
            q = AF.world(parts, M)
            items.append((key, M, q[:, :2].min(0), q[:, :2].max(0)))
        rows.append(items)
    heights = [max(hi[1] - lo[1] for _, _, lo, hi in r) for r in rows]
    y = (sum(heights) + 8.0 * (len(rows) - 1)) / 2
    pts = []
    for r, h in zip(rows, heights):
        x = -(sum(hi[0] - lo[0] for _, _, lo, hi in r) + 8.0 * (len(r) - 1)) / 2
        for key, M, lo, hi in r:
            M = M.copy()
            M[0, 3] += x - lo[0]
            M[1, 3] += y - h / 2 - (lo[1] + hi[1]) / 2
            pts.append(AF.put(loaded[key][1], M, f"{key}_{len(pts)}"))
            x += hi[0] - lo[0] + 8.0
        y -= h + 8.0
    make = AF.F.camera

    def camera(sc, lens=85):                                   # mercek kaydırma: parçalar kadrajda yukarı çıkar
        cam = make(sc, lens)
        cam.data.shift_y = -0.1
        return cam
    AF.F.camera = camera
    try:
        AF.shoot(sc, np.vstack(pts), -12, 42, 0.94, 6.3, os.path.join(FOTO, "kapak.jpg"), False, lens=70)
    finally:
        AF.F.camera = make


def export():
    bagla()
    os.makedirs(SRC, exist_ok=True)
    for fn in MODELS:
        k = fn()
        parts = T.save(k)
        T.views(k, parts)
        w, h = k.size()
        thin, gaps, pairs, clipped = k.check()
        cols = "+".join(dict.fromkeys(T.NAMES[f] for _, f in parts))
        print(f"{k.kod} {k.key:10s} {w:.0f} × {h:.0f} mm  {cols:22s} ince<{A.MIN_FEATURE}: {thin:.1f} mm²  "
              f"dar<{A.MIN_GAP}: {gaps:.1f} mm²  yakın öğe: {pairs or 'yok'}  kırpılan: {clipped:.2f} mm²  "
              f"delik et payı: {k.wall:.1f} mm", flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    bagla()
    if "--foto" in args:
        import boyde_anahtarlik_foto as AF
        AF.cover = kapak
        dizi = AF.lineup
        AF.lineup = lambda samples, size: dizi(samples, size, dark=True)        # beş model siyah fonda
        AF.main([a for a in args if a != "--foto"])
    elif "--shopier" in args:
        import boyde_anahtarlik_esnaf_shopier as ES
        ES.main()
    else:
        export()
