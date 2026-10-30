"""BOYDE LABS – toptan anahtarlık kataloğu: kendi markamızla 5 standart anahtarlık, arkalı önlü fotoğraflar.

Kullanıcı: "toptan anahtarlık için bir katalog hazırla, BOYDE olsun, 5 anahtarlık örneği çiz, bazı fotoğraflara
anahtarlık halkası da ekle"; ardından "hepsi standart anahtarlık şeklinde (dikdörtgen vs.) olsun, markaları sallama,
BOYDE LABS olarak yap; ön yüz kabartmalı yazı, arka yüz düz yazı; arkalı önlü, tek karede iki açıdan görünsün".

Yapı (kurumsal anahtarlıklardaki gibi, anahtarlik_kurumsal.Keychain):
  * gövde 3,2 mm; alt ve üst kenarda 3 katmanlık pah (ilk katman fil ayağı yapmaz)
  * ön yüz: logo ve yazılar 0,8 mm (4 katman) KABARTMA, renkli
  * arka yüz: yazılar yüzeyle aynı hizada gömme renk (0,6 mm, tablaya bakan ilk 3 katman): düz ve keskin
  * kabartma kenardan 1 mm, delikten 0,8 mm içeride; ince kabartma ve dar boşluk betikte ölçülür
Marka: 3b · Katman işareti ve BOYDE / LABS yazısı (boyde_kendi); palet: siyah, beyaz, turuncu, gri.

  K01 Klasik       60 × 30  siyah      delik solda; işaret ve yazı yan yana
  K02 Dikey etiket 30 × 56  beyaz      delik üstte; işaret üstte, yazı altında
  K03 Kare         40 × 40  turuncu    delik köşede; büyük işaret, altında yazı
  K04 Bar          72 × 24  siyah      delik sağda; büyük BOYDE / LABS, yanında katman şeritleri
  K05 Kesik köşe   56 × 32  gri        sağ üst köşe kesik, delik orada; işaret ve yazı

Çıktı : boyde_labs/anahtarlik_toptan/kaynak/<model>.npz (git'e girmez), <model>_on.png, <model>_arka.png
        boyde_labs/anahtarlik_toptan/fotograf/*.jpg (scripts/boyde_anahtarlik_foto.py)
        boyde_labs/anahtarlik_toptan/katalog.pdf, katalog.png (scripts/boyde_anahtarlik_katalog.py)
Kullanım:
  python3 scripts/boyde_anahtarlik_toptan.py            # modeller: npz, ön ve arka görünüş, baskı kontrolü
  python3 scripts/boyde_anahtarlik_toptan.py --foto     # Blender fotoğrafları (bpy 4.2)
  python3 scripts/boyde_anahtarlik_toptan.py --katalog  # katalog
"""
import json
import os
import sys

import manifold3d as m3
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_kendi as BK  # noqa: E402  (boyde_sektor ve boyde_urunler'i yükler)
import anahtarlik as A  # noqa: E402

S, U = BK.S, BK.U
OUT = os.path.join(A.ROOT, "boyde_labs", "anahtarlik_toptan")
SRC = os.path.join(OUT, "kaynak")
FOTO = os.path.join(OUT, "fotograf")
BLACK, WHITE, ORANGE, GRAY = A.BLACK, A.WHITE, S.ORANGE, BK.GRAY
RGB = U.RGB
NAMES = {BLACK: "siyah", WHITE: "beyaz", ORANGE: "turuncu", GRAY: "gri"}
BODY_H, RAISE, INLAY = 3.2, A.RAISE_H, 0.6
CHAMFER_STEPS = 3
J = m3.JoinType.Round
SLOGAN = ("Her katman", "size özel.")                  # kullanıcı: "katman katmanı sil, her katman size özel yaz"
WEB = "shopier.com/boyde"


class Key:
    """front: [(şekil, filament)] kabartma; back: arkadan bakınca okunur hâlde çizilir, gövdeye aynalanarak gömülür."""

    def __init__(self, key, kod, ad, desc, outline, hole, hole_xy, body, edge_dir):
        """edge_dir: delikten en yakın kenara doğru birim yön; ara halka buradan geçer, anahtarlık bu yönle asılır."""
        self.key, self.kod, self.ad, self.desc = key, kod, ad, desc
        self.outline, self.hole, self.hole_xy, self.body = outline, hole, hole_xy, body
        self.edge_dir = edge_dir
        self.front, self.back = [], []

    def size(self):
        x0, y0, x1, y1 = self.outline.bounds()
        return x1 - x0, y1 - y0

    def keep(self):
        return (self.outline - self.hole).offset(-A.EDGE_KEEP, J) - self.hole.offset(0.8, J)

    def regions(self, items, min_area=0.3):
        """Filament başına bölgeler; sonra gelen öncekinin üstüne yazar, kıl payı adacıklar atılır (gömme yazıda
        eşik küçük: virgül ve noktalar kalır)."""
        keep, out, taken = self.keep(), {}, A.empty()
        for cs, fil in reversed(items):
            part = (cs ^ keep) - taken
            taken = taken + cs
            out[fil] = out.get(fil, A.empty()) + part
        return {f: A.union(*[p for p in cs.decompose() if p.area() > min_area]) for f, cs in out.items()}

    def solids(self):
        """Baskı yönünde (arka yüz tablada, z = 0; ön yüz yukarıda): [(Manifold, filament)]."""
        shape = self.outline - self.hole
        body = shape.extrude(BODY_H)
        rings = []
        for k in range(CHAMFER_STEPS):
            ring = shape - shape.offset(-A.CHAMFER * (CHAMFER_STEPS - k) / CHAMFER_STEPS, J)
            lo = -0.1 if k == 0 else 0.0
            rings.append(ring.extrude(A.LAYER - lo).translate((0, 0, k * A.LAYER + lo)))
            hi = 0.1 if k == 0 else 0.0
            rings.append(ring.extrude(A.LAYER + hi).translate((0, 0, BODY_H - (k + 1) * A.LAYER)))
        body = body - m3.Manifold.batch_boolean(rings, m3.OpType.Add)
        parts = []
        for fil, cs in self.regions([(c.mirror((1, 0)), f) for c, f in self.back], 0.08).items():
            m = cs.extrude(INLAY)
            body = body - m
            parts.append((m, fil))
        for fil, cs in self.regions(self.front).items():
            parts.append((cs.extrude(RAISE).translate((0, 0, BODY_H)), fil))
        return [(body, self.body)] + parts

    def check(self):
        """Ön kabartma: MIN_FEATURE'dan ince ve MIN_GAP'ten dar alanlar (mm²), birbirine yakın öğeler; ön ve arkada
        kenar ya da delik payına taşıp kırpılan alan (mm², 0 olmalı)."""
        d = A.Design(self.key, self.key, self.outline, self.front, self.hole)
        thin, gaps, _ = d.check()
        keep = self.keep()
        self.wall = next(r for r in [x * 0.05 for x in range(1, 200)]                 # delik çevresindeki et payı
                         if not (A.circle(2.6 + r, *self.hole_xy) - self.outline).is_empty())
        clipped = sum((cs - keep).area() for cs, _ in self.front)
        clipped += sum((cs.mirror((1, 0)) - keep).area() for cs, _ in self.back)
        return thin.area(), gaps.area(), d.check_pairs(), clipped


# ---------------------------------------------------------------- marka parçaları

CLOSE = 0.36                                             # nozulun 0,7 mm'den dar yarıkları kabartmada basılmaz: kapanır
LABS_MIN = 4.2                                           # LABS en az bu boyda ve kalın (3 mm'de çizgiler 0,5 mm kalıyor)


def logo(h, x, y, anchor, main, accent=ORANGE):
    """3b · Katman işareti: [(şekil, filament)] ve eni. Kabartmada basılsın diye nozulun dar yarıkları kapanır,
    katman çizgileri 0,15 mm incelir (araları 0,7 mm'yi geçer)."""
    parts, w = BK.mark(h, x, y, anchor)
    out = []
    for role, fil in (("main", main), ("accent", accent)):
        bars, nozzle = [], []
        for p in parts[role].decompose():
            x0, y0, x1, y1 = p.bounds()
            (bars if (x1 - x0) > 4 * (y1 - y0) else nozzle).append(p)
        if nozzle:
            out.append((A.union(*nozzle).offset(CLOSE, J).offset(-CLOSE, J), fil))
        out += [(b.offset(-0.15, J), fil) for b in bars]
    return out, w


def dotted(cs, cap, grow=0.2):
    """Gömme yazıda i, ö, ü noktaları, nokta ve virgül küçük kalır (kıl payı temizliğinde silinir): büyütülür.
    Nokta: iki kenarı da büyük harf boyunun üçte birinden küçük parça."""
    out = []
    for p in cs.decompose():
        x0, y0, x1, y1 = p.bounds()
        out.append(p.offset(grow, J) if max(x1 - x0, y1 - y0) < 0.32 * cap else p)
    return A.union(*out)


def word(cap, x, y, align="l"):
    """boyde_kendi.word gibi; LABS kalın (Space Grotesk Bold) ve en az LABS_MIN mm."""
    b = S.t("sg7", "BOYDE", cap, x, y, align)
    bx0, by0, bx1, _ = b.bounds()
    c2 = max(cap * 0.5, LABS_MIN)
    y2 = by0 - cap * 0.26 - c2 / 2
    labs = S.t("sg7", "LABS", c2, bx1, y2, "r", c2 * 0.24)
    rule = S.bar(bx0, labs.bounds()[0] - c2 * 0.55, y2, max(1.2, c2 * 0.3))
    return b, labs + rule, (bx0, y2 - c2 / 2, bx1, by0 + cap)


def wordmark(cap, x, y, main, accent=ORANGE, align="l"):
    """BOYDE, altında çizgi ve LABS: [(şekil, filament)] ve sınır kutusu."""
    b, rest, box = word(cap, x, y, align)
    return [(b, main), (rest, accent)], box


def lockup(h, x, y, main, accent=ORANGE):
    """İşaret solda (h mm), yazı sağında; (x, y) sol orta. Döner öğeler ve sağ kenar."""
    items, w = logo(h, x, y, "l", main, accent)
    cap = h * 0.42
    _, _, (bx0, by0, bx1, by1) = word(cap, 0, 0)
    dx, dy = x + w + h * 0.22 - bx0, y - (by0 + by1) / 2
    more, _ = wordmark(cap, dx, dy, main, accent)
    return items + more, bx1 + dx


def text(k, s, cap, x, y, align="c", tr=0.0, max_w=None):
    """Arka yüz (gömme) yazısı; noktalar büyütülür."""
    real = S.font(k).fit_cap(s, cap, max_w, tr) if max_w else cap
    return dotted(S.t(k, s, cap, x, y, align, tr, max_w), real)


# ---------------------------------------------------------------- hizalama ("yazılar hizalanmamış gibi")

def bbox(items):
    return A.union(*[cs for cs, _ in items]).bounds()


def row(items, cx=0.0):
    """Bir satır (öğe listesi) kendi sınır kutusuyla x = cx'e ortalanır; y'si olduğu gibi kalır."""
    x0, _, x1, _ = bbox(items)
    return [(cs.translate((cx - (x0 + x1) / 2, 0.0)), f) for cs, f in items]


def column(rows):
    """Satırlar aynı dikey eksende (x = 0) ortalanır."""
    return [item for r in rows for item in row(r)]


def centred(items, cx, cy):
    """Öğeler ortak sınır kutularının ortası (cx, cy)'ye taşınır."""
    x0, y0, x1, y1 = bbox(items)
    return [(cs.translate((cx - (x0 + x1) / 2, cy - (y0 + y1) / 2)), f) for cs, f in items]


def below(upper, lower, gap):
    """lower öğelerini upper'ın `gap` mm altına taşır."""
    _, uy0, _, _ = bbox(upper)
    _, _, _, ly1 = bbox(lower)
    return [(cs.translate((0.0, uy0 - gap - ly1)), f) for cs, f in lower]


def lines(specs):
    """Arka yüz satırları [(yazı tipi, yazı, boy, y, renk[, harf aralığı])] ya da [("bar", en, kalınlık, y, renk)];
    hepsi x = 0'a ortalı (sınır kutusuyla)."""
    out = []
    for k, s, cap, y, f, *tr in specs:
        cs = S.bar(-s / 2, s / 2, y, cap) if k == "bar" else text(k, s, cap, 0, y, tr=tr[0] if tr else 0.0)
        out.append([(cs, f)])
    return column(out)


def place(k, front, back, box, back_box=None):
    """Ön yüz grubu `box`un (delik payı çıkınca kalan alan, ön yüz koordinatı) ortasına; arka yüz grubu aynı alanın
    (ya da back_box'ın) aynasının ortasına (arkadan bakınca delik öbür yanda)."""
    x0, y0, x1, y1 = box
    k.front += centred(front, (x0 + x1) / 2, (y0 + y1) / 2)
    x0, y0, x1, y1 = back_box or box
    k.back += centred(back, -(x0 + x1) / 2, (y0 + y1) / 2)


# ---------------------------------------------------------------- modeller (öğeler kenardan ≥ 1,5 mm, delikten ≥ 1,2 mm)

def k01_klasik():
    W, H = 60.0, 30.0
    hx = -W / 2 + 6.5
    k = Key("k01_klasik", "K01", "Klasik", "Siyah dikdörtgen; delik solda. Önde kabartma beyaz işaret ve BOYDE, "
            "turuncu LABS. Arkada slogan ve shopier.com/boyde.",
            A.rrect(W, H, 5.0), A.circle(2.6, hx, 0), (hx, 0.0), BLACK, (-1.0, 0.0))
    front, _ = lockup(15.0, 0.0, 0.0, WHITE)
    back = lines([("sg6", SLOGAN[0], 3.6, 6.4, WHITE), ("sg6", SLOGAN[1], 3.6, 1.0, WHITE),
                  ("bar", 18.0, 0.8, -3.8, ORANGE), ("outfit", WEB, 3.0, -8.6, ORANGE)])
    place(k, front, back, (hx + 2.6 + 1.2, -H / 2 + 1.5, W / 2 - 1.5, H / 2 - 1.5))
    return k


def k02_dikey():
    W, H = 30.0, 56.0
    hy = H / 2 - 6.5
    k = Key("k02_dikey", "K02", "Dikey etiket", "Beyaz dikey etiket; delik üstte. Önde kabartma siyah işaret, BOYDE "
            "ve turuncu LABS, ikisi aynı eksende. Arkada slogan ve adres.",
            A.rrect(W, H, 4.0), A.circle(2.6, 0, hy), (0.0, hy), WHITE, (0.0, 1.0))
    mark, _ = logo(15.0, 0, 0, "tc", BLACK)
    word_, _ = wordmark(6.0, 0, 0, BLACK, align="c")
    front = column([mark, below(mark, word_, 3.6)])
    back = lines([("sg6", SLOGAN[0], 3.6, 6.4, BLACK), ("sg6", SLOGAN[1], 3.6, 1.0, BLACK),
                  ("bar", 12.0, 0.8, -3.8, ORANGE), ("outfit", "shopier.com", 3.0, -8.6, ORANGE),
                  ("outfit", "/boyde", 3.0, -13.6, ORANGE)])
    place(k, front, back, (-W / 2 + 1.5, -H / 2 + 1.5, W / 2 - 1.5, hy - 2.6 - 1.2))
    return k


def k03_kare():
    S_ = 40.0
    hx, hy = -S_ / 2 + 7.0, S_ / 2 - 7.0
    k = Key("k03_kare", "K03", "Kare", "Turuncu kare; delik köşede. Önde kabartma büyük siyah işaret (en üst katmanı "
            "beyaz), altında aynı eksende siyah BOYDE ve beyaz LABS. Arkada BOYDE LABS ve adres.",
            A.rrect(S_, S_, 7.0), A.circle(2.6, hx, hy), (hx, hy), ORANGE, (-0.7071, 0.7071))
    mark, _ = logo(15.0, 0, 0, "tc", BLACK, WHITE)
    word_, _ = wordmark(6.0, 0, 0, BLACK, WHITE, align="c")
    front = column([mark, below(mark, word_, 3.2)])
    back = lines([("sg7", "BOYDE", 5.0, 7.6, BLACK, 0.4), ("sg6", "LABS", 3.4, 1.6, WHITE, 1.0),
                  ("bar", 12.0, 0.8, -2.6, BLACK), ("outfit", "shopier.com", 3.0, -7.4, BLACK),
                  ("outfit", "/boyde", 3.0, -12.4, BLACK)])
    box = (-S_ / 2 + 1.5, -S_ / 2 + 1.5, S_ / 2 - 1.5, S_ / 2 - 1.5)                    # delik köşede, işarete değmez
    place(k, front, back, box, back_box=box[:3] + (hy - 2.6 - 1.2,))                    # arka yazılar deliğin altında
    return k


def k04_bar():
    W, H = 72.0, 24.0
    hx = W / 2 - 6.0
    k = Key("k04_bar", "K04", "Bar", "Siyah uzun bar; delik sağda. Önde kabartma büyük beyaz BOYDE ve turuncu LABS, "
            "yanında işaretin katmanları gibi üç şerit (üstteki turuncu). Arkada slogan ve adres.",
            A.rrect(W, H, 3.0), A.circle(2.6, hx, 0), (hx, 0.0), BLACK, (1.0, 0.0))
    word_, (bx0, by0, bx1, by1) = wordmark(9.0, 0.0, 0.0, WHITE)
    cy = (by0 + by1) / 2
    stripes = [(S.bar(bx1 + 4.0 + 2.4 * i, bx1 + 18.0, cy + y, 2.0), f)
               for i, (y, f) in enumerate(((4.6, ORANGE), (0.0, WHITE), (-4.6, WHITE)))]
    back = lines([("sg6", " ".join(SLOGAN), 3.6, 3.4, WHITE), ("outfit", WEB, 3.0, -4.4, ORANGE)])
    place(k, word_ + stripes, back, (-W / 2 + 1.5, -H / 2 + 1.5, hx - 2.6 - 1.2, H / 2 - 1.5))
    return k


def k05_kesik():
    W, H, C = 56.0, 32.0, 11.0
    card = A.rrect(W, H, 4.0) - A.polygon([(W / 2 - C, H / 2 + 1), (W / 2 + 1, H / 2 + 1), (W / 2 + 1, H / 2 - C)])
    outline = card.offset(-1.0, J).offset(1.0, J)
    # delik kesik kenara dik doğrultuda, kenardan 3,5 mm et payıyla (önceki yer kesik kenara 0,4 mm kalıyordu)
    hx, hy = W / 2 - 9.4, H / 2 - 10.2                    # kesik kenar x + y = 33: delik merkezi 6,1 mm içeride
    k = Key("k05_kesik", "K05", "Kesik köşe", "Gri dikdörtgen, sağ üst köşesi kesik; delik orada. Önde kabartma siyah "
            "işaret ve BOYDE, turuncu LABS. Arkada beyaz slogan ve adres.",
            outline, A.circle(2.6, hx, hy), (hx, hy), GRAY, (0.7071, 0.7071))
    front, _ = lockup(12.6, 0.0, 0.0, BLACK)
    back = lines([("sg6", SLOGAN[0], 3.6, 2.6, WHITE), ("sg6", SLOGAN[1], 3.6, -2.8, WHITE),
                  ("outfit", WEB, 3.0, -9.6, WHITE)])
    place(k, front, back, (-W / 2 + 1.5, -H / 2 + 1.5, hx - 2.6 - 1.2, H / 2 - 1.5))
    return k


MODELS = [k01_klasik, k02_dikey, k03_kare, k04_bar, k05_kesik]
KEYS = ["k01_klasik", "k02_dikey", "k03_kare", "k04_bar", "k05_kesik"]


# ---------------------------------------------------------------- dışa aktarma

def save(k):
    """npz: parçalar baskı yönünde (arka yüz z = 0, ön kabartma üstte), mm; meta: renk, delik, merkez, kalınlık."""
    parts = k.solids()
    arrays = {}
    for i, (man, _) in enumerate(parts):
        V, T = A.mesh_arrays(man)
        arrays[f"v{i}"], arrays[f"f{i}"] = V.astype(np.float32), T.astype(np.int32)
    x0, y0, x1, y1 = k.outline.bounds()
    meta = {"parcalar": [{"renk": list(RGB[f]), "metal": False} for _, f in parts],
            "delik": list(k.hole_xy), "delik_r": 2.6, "kenar_yonu": list(k.edge_dir),
            "merkez": [(x0 + x1) / 2, (y0 + y1) / 2], "kalinlik": BODY_H, "toplam": BODY_H + RAISE}
    np.savez_compressed(os.path.join(SRC, f"{k.key}.npz"), meta=json.dumps(meta), **arrays)
    return parts


def views(k, parts):
    """Ön ve arka görünüş (saydam PNG): katalogdaki çizimler için."""
    from cift_tarafli_isimlik import render, rotation
    mesh = [(*A.mesh_arrays(man), RGB[f]) for man, f in parts]
    for name, R in (("on", A.R_TOP), ("arka", rotation(180, 180))):     # arka: soldan sağa çevrilmiş
        im = render(mesh, 1000, R, margin=0.0, ambient=0.62)
        im.crop(im.getbbox()).save(os.path.join(SRC, f"{k.key}_{name}.png"), optimize=True)


def export():
    os.makedirs(SRC, exist_ok=True)
    for fn in MODELS:
        k = fn()
        parts = save(k)
        views(k, parts)
        w, h = k.size()
        thin, gaps, pairs, clipped = k.check()
        cols = "+".join(dict.fromkeys(NAMES[f] for _, f in parts))
        print(f"{k.kod} {k.key:11s} {w:.0f} × {h:.0f} mm  {cols:22s} ince<{A.MIN_FEATURE}: {thin:.1f} mm²  "
              f"dar<{A.MIN_GAP}: {gaps:.1f} mm²  yakın öğe: {pairs or 'yok'}  kırpılan: {clipped:.2f} mm²  "
              f"delik et payı: {k.wall:.1f} mm", flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--foto" in args:
        import boyde_anahtarlik_foto as AF
        AF.main(args)
    elif "--katalog" in args:
        import boyde_anahtarlik_katalog as AK
        AK.main()
    else:
        export()
