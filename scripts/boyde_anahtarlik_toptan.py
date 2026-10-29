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

    def __init__(self, key, kod, ad, desc, outline, hole, hole_xy, body):
        self.key, self.kod, self.ad, self.desc = key, kod, ad, desc
        self.outline, self.hole, self.hole_xy, self.body = outline, hole, hole_xy, body
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
        """Ön kabartma: MIN_FEATURE'dan ince ve MIN_GAP'ten dar alanlar (mm²), birbirine yakın öğeler."""
        d = A.Design(self.key, self.key, self.outline, self.front, self.hole)
        thin, gaps, _ = d.check()
        return thin.area(), gaps.area(), d.check_pairs()


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


# ---------------------------------------------------------------- modeller

def k01_klasik():
    W, H = 60.0, 30.0
    hx = -W / 2 + 6.5
    k = Key("k01_klasik", "K01", "Klasik", "Siyah dikdörtgen; delik solda. Önde kabartma beyaz işaret ve BOYDE, "
            "turuncu LABS. Arkada slogan ve shopier.com/boyde.",
            A.rrect(W, H, 5.0), A.circle(2.6, hx, 0), (hx, 0.0), BLACK)
    items, right = lockup(15.0, -W / 2 + 13.0, 0.0, WHITE)
    dx = (W / 2 - 3.0 - right) / 2                         # delikten sağ kenara kadar ortala
    k.front += [(cs.translate((dx, 0)), f) for cs, f in items]
    bx = -3.6                                              # arkadan bakınca delik sağda
    k.back += [(text("sg6", SLOGAN[0], 3.6, bx, 6.4), WHITE), (text("sg6", SLOGAN[1], 3.6, bx, 1.0), WHITE),
               (S.bar(bx - 9.0, bx + 9.0, -3.8, 0.8), ORANGE),
               (text("outfit", WEB, 3.0, bx, -8.6, tr=0.2, max_w=40.0), ORANGE)]
    return k


def k02_dikey():
    W, H = 30.0, 56.0
    hy = H / 2 - 6.5
    k = Key("k02_dikey", "K02", "Dikey etiket", "Beyaz dikey etiket; delik üstte. Önde kabartma siyah işaret, BOYDE "
            "ve turuncu LABS. Arkada slogan ve adres.",
            A.rrect(W, H, 4.0), A.circle(2.6, 0, hy), (0.0, hy), WHITE)
    items, _ = logo(15.0, 0, 14.6, "tc", BLACK)
    more, _ = wordmark(6.4, 0, -8.2, BLACK, align="c")
    k.front += items + more
    k.back += [(text("sg6", SLOGAN[0], 3.6, 0, 6.4), BLACK), (text("sg6", SLOGAN[1], 3.6, 0, 1.0), BLACK),
               (S.bar(-6.0, 6.0, -4.6, 0.8), ORANGE),
               (text("outfit", "shopier.com", 3.0, 0, -10.2, tr=0.2), ORANGE),
               (text("outfit", "/boyde", 3.0, 0, -15.2, tr=0.2), ORANGE)]
    return k


def k03_kare():
    S_ = 40.0
    hx, hy = -S_ / 2 + 7.0, S_ / 2 - 7.0
    k = Key("k03_kare", "K03", "Kare", "Turuncu kare; delik köşede. Önde kabartma büyük siyah işaret (en üst katmanı "
            "beyaz), altında siyah BOYDE ve beyaz LABS. Arkada BOYDE LABS ve adres.",
            A.rrect(S_, S_, 7.0), A.circle(2.6, hx, hy), (hx, hy), ORANGE)
    items, _ = logo(16.0, 2.0, 15.4, "tc", BLACK, WHITE)
    more, _ = wordmark(6.0, 0.6, -7.6, BLACK, WHITE, align="c")
    k.front += items + more
    k.back += [(text("sg7", "BOYDE", 5.0, -2.0, 9.0, tr=0.4), BLACK), (text("sg6", "LABS", 3.4, -2.0, 2.6, tr=1.0), WHITE),
               (S.bar(-8.0, 4.0, -2.2, 0.8), BLACK),
               (text("outfit", "shopier.com", 3.0, 0, -7.4, tr=0.2), BLACK),
               (text("outfit", "/boyde", 3.0, 0, -12.4, tr=0.2), BLACK)]
    return k


def k04_bar():
    W, H = 72.0, 24.0
    hx = W / 2 - 6.0
    k = Key("k04_bar", "K04", "Bar", "Siyah uzun bar; delik sağda. Önde kabartma büyük beyaz BOYDE ve turuncu LABS, "
            "yanında işaretin katmanları gibi üç şerit (üstteki turuncu). Arkada slogan ve adres.",
            A.rrect(W, H, 3.0), A.circle(2.6, hx, 0), (hx, 0.0), BLACK)
    items, (bx0, by0, bx1, by1) = wordmark(9.0, -W / 2 + 5.5, 0.0, WHITE)
    dy = -(by0 + by1) / 2
    k.front += [(cs.translate((0, dy)), f) for cs, f in items]
    x0, x1 = bx1 + 4.0, hx - 6.0
    for i, (y, f) in enumerate(((4.6, ORANGE), (0.0, WHITE), (-4.6, WHITE))):
        k.front.append((S.bar(x0 + 2.4 * i, x1, y, 2.0), f))
    bx = 4.0                                               # arkadan bakınca delik solda
    k.back += [(text("sg6", " ".join(SLOGAN), 3.6, bx, 3.4, max_w=50.0), WHITE),
               (text("outfit", WEB, 3.0, bx, -4.4, tr=0.3), ORANGE)]
    return k


def k05_kesik():
    W, H, C = 56.0, 32.0, 11.0
    card = A.rrect(W, H, 4.0) - A.polygon([(W / 2 - C, H / 2 + 1), (W / 2 + 1, H / 2 + 1), (W / 2 + 1, H / 2 - C)])
    outline = card.offset(-1.0, J).offset(1.0, J)
    hx, hy = W / 2 - 7.6, H / 2 - 7.6
    k = Key("k05_kesik", "K05", "Kesik köşe", "Gri dikdörtgen, sağ üst köşesi kesik; delik orada. Önde kabartma siyah "
            "işaret ve BOYDE, turuncu LABS. Arkada beyaz slogan ve adres.",
            outline, A.circle(2.6, hx, hy), (hx, hy), GRAY)
    items, right = lockup(14.0, -W / 2 + 5.0, -2.0, BLACK)
    k.front += items
    bx = 2.0
    k.back += [(text("sg6", SLOGAN[0], 3.6, bx, 2.6), WHITE), (text("sg6", SLOGAN[1], 3.6, bx, -2.8), WHITE),
               (text("outfit", WEB, 3.0, bx, -9.6, tr=0.2), WHITE)]
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
            "delik": list(k.hole_xy), "merkez": [(x0 + x1) / 2, (y0 + y1) / 2],
            "kalinlik": BODY_H, "toplam": BODY_H + RAISE}
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
        thin, gaps, pairs = k.check()
        cols = "+".join(dict.fromkeys(NAMES[f] for _, f in parts))
        print(f"{k.kod} {k.key:11s} {w:.0f} × {h:.0f} mm  {cols:22s} ince<{A.MIN_FEATURE}: {thin:.1f} mm²  "
              f"dar<{A.MIN_GAP}: {gaps:.1f} mm²  yakın öğe: {pairs or 'yok'}", flush=True)


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
