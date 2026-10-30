"""Toptan anahtarlık: müşterinin markasıyla 8 biçim × 3 dizilim; ön yüz kabartma, arka yüz gömme yazı.

Yapı BOYDE'nin toptan anahtarlıklarıyla aynı (scripts/boyde_anahtarlik_toptan.py):
  * gövde 3,2 mm; alt ve üst kenarda 3 katmanlık pah (ilk katman fil ayağı yapmaz)
  * ön yüz: simge (sektör simgesi, logo ya da baş harfler) ve yazılar 0,8 mm (4 katman) KABARTMA
  * arka yüz: yazılar yüzeyle aynı hizada gömme renk (0,6 mm, tablaya bakan 3 katman): arkadan okunur, düz ve keskin
  * öğeler kenardan 1,5 mm, delikten 1,2 mm içeride; delik Ø5,2 mm, çevresinde en az 3,5 mm et
Yazılar ve simge kutuya sığacak boyda yeniden dizilir (geometrik küçültme yok: harf arası ve noktalar korunur).
Baskıya uygunluk: ön kabartmada harf içi ve ara ≥ 0,6 mm (A.MIN_GAP), arka gömme yazıda ≥ 0,5; kenara ya da deliğe
taşan (kırpılan) alan yok.
"""
import math

import manifold3d as m3

from . import ortak as O
from .ortak import A, J

BODY_H, RAISE, INLAY, CHAMFER_STEPS = 3.2, A.RAISE_H, 0.6, 3
HOLE_R = 2.6
MIN_ON, MIN_ARKA = 0.6, 0.45


class Anahtarlik:
    """outline, hole_xy, kutu (ön yüz öğelerinin alanı), arka_kutu; front: [(şekil, renk)] kabartma; back: arkadan
    bakınca okunur hâlde çizilir, gövdeye aynalanarak gömülür."""

    def __init__(self, bicim, outline, hole_xy, kutu, arka_kutu=None):
        self.bicim, self.outline, self.hole_xy = bicim, outline, hole_xy
        self.hole = A.circle(HOLE_R, *hole_xy)
        self.kutu, self.arka_kutu = kutu, arka_kutu or kutu
        self.front, self.back, self.lines = [], [], {}

    def size(self):
        x0, y0, x1, y1 = self.outline.bounds()
        return x1 - x0, y1 - y0

    def keep(self):
        return (self.outline - self.hole).offset(-1.0, J) - self.hole.offset(0.8, J)

    def regions(self, items, min_area=0.3):
        """Filament başına bölgeler; sonra gelen öncekinin üstüne yazar, kıl payı adacıklar atılır."""
        keep, out, taken = self.keep(), {}, A.empty()
        for cs, fil in reversed(items):
            part = (cs ^ keep) - taken
            taken = taken + cs
            out[fil] = out.get(fil, A.empty()) + part
        return {f: A.union(*[p for p in cs.decompose() if p.area() > min_area]) for f, cs in out.items()}

    def solids(self):
        """Baskı yönünde (arka yüz tablada, z = 0; ön yüz yukarıda): [(ad, Manifold, renk)]."""
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
            parts.append((f"Arka yazı ({O.AD[fil]})", m, fil))
        for fil, cs in self.regions(self.front).items():
            parts.append((f"Ön kabartma ({O.AD[fil]})", cs.extrude(RAISE).translate((0, 0, BODY_H)), fil))
        return [(f"Gövde ({O.AD[self.govde]})", body, self.govde)] + parts


# ---------------------------------------------------------------- biçimler: (dış çizgi, delik, ön kutu, arka kutu)

def _klasik():
    W, H = 60.0, 30.0
    hx = -W / 2 + 6.5
    return A.rrect(W, H, 5.0), (hx, 0.0), (hx + HOLE_R + 1.2, -H / 2 + 1.5, W / 2 - 1.5, H / 2 - 1.5), None


def _dikey():
    W, H = 30.0, 56.0
    hy = H / 2 - 6.5
    return A.rrect(W, H, 4.0), (0.0, hy), (-W / 2 + 1.5, -H / 2 + 1.5, W / 2 - 1.5, hy - HOLE_R - 1.2), None


def _kare():
    S_ = 40.0
    hx, hy = -S_ / 2 + 7.0, S_ / 2 - 7.0
    return A.rrect(S_, S_, 7.0), (hx, hy), (-S_ / 2 + 1.5, -S_ / 2 + 1.5, S_ / 2 - 1.5, hy - HOLE_R - 1.2), None


def _bar():
    W, H = 72.0, 24.0
    hx = W / 2 - 6.0
    return A.rrect(W, H, 3.0), (hx, 0.0), (-W / 2 + 1.5, -H / 2 + 1.5, hx - HOLE_R - 1.2, H / 2 - 1.5), None


def _kesik():
    W, H, C = 56.0, 32.0, 11.0
    card = A.rrect(W, H, 4.0) - A.polygon([(W / 2 - C, H / 2 + 1), (W / 2 + 1, H / 2 + 1), (W / 2 + 1, H / 2 - C)])
    hx, hy = W / 2 - 9.4, H / 2 - 10.2                    # kesik kenara 3,5 mm et payı
    return (card.offset(-1.0, J).offset(1.0, J), (hx, hy), (-W / 2 + 1.5, -H / 2 + 1.5, hx - HOLE_R - 1.2,
                                                             H / 2 - 1.5), None)


def _kapsul():
    W, H = 64.0, 26.0
    hx = -W / 2 + 8.5
    return A.rrect(W, H, H / 2 - 0.01), (hx, 0.0), (hx + HOLE_R + 1.5, -H / 2 + 3.0, W / 2 - 6.5, H / 2 - 3.0), None


def _daire():
    R = 22.0
    hy = R - 6.5
    return A.circle(R, 0, 0, 160), (0.0, hy), (-15.5, -15.5, 15.5, hy - HOLE_R - 1.2), None


def _etiket():
    W, H, U = 62.0, 28.0, 9.0
    tag = A.polygon([(-W / 2 + U, H / 2), (W / 2, H / 2), (W / 2, -H / 2), (-W / 2 + U, -H / 2), (-W / 2, -H / 2 + U),
                     (-W / 2, H / 2 - U)])
    hx = -W / 2 + 7.0
    return (tag.offset(-2.5, J).offset(2.5, J), (hx, 0.0), (hx + HOLE_R + 1.2, -H / 2 + 1.5, W / 2 - 1.5, H / 2 - 1.5),
            None)


# anahtar: (ad, kurucu, uygun dizilimler)
BICIMLER = {"klasik": ("Klasik 60 × 30", _klasik, ["yan", "yazi", "ust"]),
            "dikey": ("Dikey etiket 30 × 56", _dikey, ["ust", "yazi"]),
            "kare": ("Kare 40 × 40", _kare, ["ust", "yazi"]),
            "bar": ("Bar 72 × 24", _bar, ["yan", "yazi"]),
            "kesik": ("Kesik köşe 56 × 32", _kesik, ["yan", "yazi", "ust"]),
            "kapsul": ("Kapsül 64 × 26", _kapsul, ["yan", "yazi"]),
            "daire": ("Yuvarlak Ø44", _daire, ["ust", "yazi"]),
            "etiket": ("Bavul etiketi 62 × 28", _etiket, ["yan", "yazi", "ust"])}
DIZILIMLER = {"yan": "simge solda, ad yanında", "ust": "simge üstte, ad altında", "yazi": "yalnız ad"}


# ---------------------------------------------------------------- yerleşim

def _kutu_ortasi(items, kutu):
    """Öğeleri ortak sınır kutularıyla kutunun ortasına taşır. Döner (öğeler, kayma)."""
    x0, y0, x1, y1 = A.union(*[cs for cs, _ in items]).bounds()
    d = ((kutu[0] + kutu[2]) / 2 - (x0 + x1) / 2, (kutu[1] + kutu[3]) / 2 - (y0 + y1) / 2)
    return [(cs.translate(d), f) for cs, f in items], d


def _simge(c, h, w):
    """Simge parçaları (rol ile), ortası (0, 0)."""
    key = "makas" if c.simge == "direk" else c.simge
    if key == "logo" and c.logo is not None:
        return [(O.temizle(cs, 1.0, 0.7), r) for cs, r in O.olcekle([(c.logo, "vurgu")], 0.0, 0.0, w, h)]
    if key in O.SIMGE:
        return O.simge_kur(key, w, h)
    parts, _ = O.monogram(O.monogram_harfleri(c.marka), 0.0, 0.0, min(w, h))
    return parts


MIN_AD = {"bebas": 5.2, "oswald": 5.0, "anton": 5.6}    # dar yazı tiplerinde harf içi daha çabuk kapanır
MIN_ALT, MIN_ARKA_BOY = 3.8, 3.0                         # ön alt yazı ve arka gömme yazı en küçük boyu
ARKA = "man6"                                            # arka gömme yazı: Manrope SemiBold (küçük boyda harf içi en geniş)


def _ust_koy(cs, y):
    b = cs.bounds()
    return cs.translate((0.0, y - b[3])), y - (b[3] - b[1])


def _ad_satirlari(ad, yazi_tipi, cap_max, w, tr=0.3):
    """Ad bir satır (sığarsa) ya da iki satır; döner (satırlar, boy) ya da boy en küçüğün altındaysa (.., 0)."""
    en_az = MIN_AD.get(yazi_tipi, 4.2)
    c1 = O.sigan(yazi_tipi, ad, cap_max, w, tr)
    words = ad.split()
    if c1 >= en_az * 1.25 or len(words) < 2:
        return [ad], (c1 if c1 >= en_az else 0.0)
    best = ([ad], c1)
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        cc = min(O.sigan(yazi_tipi, a, cap_max * 0.78, w, tr), O.sigan(yazi_tipi, b, cap_max * 0.78, w, tr))
        if cc > best[1] * 1.1:
            best = ([a, b], cc)
    return best[0], (best[1] if best[1] >= en_az else 0.0)


def _on(c, p, dizilim, yazi_tipi, kutu, uyar):
    """Ön yüz: ad (bir ya da iki satır), altında küçük yazı, simge (yanda ya da üstte). Her satır kutuya kendi
    boyunda sığdırılır (en küçük boyun altına inmez). Döner (öğeler, satırlar, kalite)."""
    W, H = kutu[2] - kutu[0], kutu[3] - kutu[1]
    renk = {"yazi": p.yazi, "vurgu": p.vurgu, "vurgu2": p.vurgu2 or p.vurgu}
    ad = O.ad_metni(c.marka, yazi_tipi)
    sim, sw = None, 0.0
    if dizilim == "yan":
        sim = _simge(c, H * 0.62, min(H * 1.1, W * 0.3))
        sb = A.union(*[cs for cs, _ in sim]).bounds()
        sw = sb[2] - sb[0] + 2.4
    aw = W - sw
    pay = {"yazi": 0.56, "yan": 0.46, "ust": 0.3}[dizilim] * H      # adın boyu için ayrılan yükseklik
    if c.alt:
        pay *= 0.82
    satirlar, cap = _ad_satirlari(ad, yazi_tipi, pay, aw)
    if not cap:
        return None, None, 0.0
    alt_cap, alt_satir, alt_tr = 0.0, [c.alt], 0.8
    if c.alt:                     # tek satır; sığmazsa iki satır (boy büyük kalır), en son daha dar harf aralığı
        kelime = c.alt.split()
        iki = min(([" ".join(kelime[:i]), " ".join(kelime[i:])] for i in range(1, len(kelime))),
                  key=lambda x: max(len(x[0]), len(x[1])), default=None)
        for satir_, tr in [([c.alt], 0.8)] + ([(iki, 0.8)] if iki else []) + [([c.alt], 0.5)]:
            alt_cap = min([4.6] + [O.sigan(O.SATIR, x, cap * 0.75, aw, tr) for x in satir_])
            if alt_cap >= MIN_ALT:
                alt_satir, alt_tr = satir_, tr
                break
        if alt_cap < MIN_ALT:
            alt_cap = 0.0
            uyar.append(f"'{c.alt}' bu biçime sığmadı")
    for _ in range(3):                                   # yükseklik taşarsa ad küçülür
        y, yazilar = 0.0, []
        for s in satirlar:
            cs, y = _ust_koy(O.yazi(yazi_tipi, s, cap, 0.0, 0.0, "c", 0.3, aw), y)
            yazilar.append(cs)
            y -= max(1.0, cap * 0.22)
        ad_cs = A.union(*yazilar)
        blok, lines = [(ad_cs, p.yazi)], {"ad": ad_cs}
        if alt_cap:
            y, altlar = ad_cs.bounds()[1] - max(1.3, cap * 0.2), []
            for s in alt_satir:
                cs, y = _ust_koy(O.yazi(O.SATIR, s, alt_cap, 0.0, 0.0, "c", alt_tr, aw), y)
                altlar.append(cs)
                y -= max(1.0, alt_cap * 0.3)
            alt = A.union(*altlar)
            lines["alt"] = alt
            blok.append((alt, p.vurgu))
        bb = A.union(*[cs for cs, _ in blok]).bounds()
        items = list(blok)
        if dizilim == "ust":
            ih = min(H - (bb[3] - bb[1]) - 2.2, H * 0.42)
            if ih >= 7.0:
                sim = _simge(c, ih, W * 0.8)
                sb = A.union(*[cs for cs, _ in sim]).bounds()
                d = ((bb[0] + bb[2]) / 2 - (sb[0] + sb[2]) / 2, bb[3] + 2.2 - sb[1])
                items = [(cs.translate(d), renk[r]) for cs, r in sim] + blok
        elif dizilim == "yan":
            sb = A.union(*[cs for cs, _ in sim]).bounds()
            d = (bb[0] - 2.4 - sb[2], (bb[1] + bb[3]) / 2 - (sb[1] + sb[3]) / 2)
            items = [(cs.translate(d), renk[r]) for cs, r in sim] + blok
        x0, y0, x1, y1 = A.union(*[cs for cs, _ in items]).bounds()
        f = min(W / (x1 - x0), H / (y1 - y0))
        if f >= 0.99:
            break
        cap = max(cap * f * 0.98, MIN_AD.get(yazi_tipi, 4.2))
        alt_cap = alt_cap and max(alt_cap * f * 0.98, MIN_ALT)
    return items, lines, min(1.0, cap / (0.8 * pay)) * (1.0 if not c.alt or alt_cap else 0.85)


def _arka_parcalari(s, ust, W):
    """Bir arka satırın yerleşimi: [(metin, boy, harf aralığı)]. Tek satır; sığmazsa daha dar harf aralığı; o da
    olmazsa kelimelerden iki satır (telefon: "0546 475" / "45 08"). Hiçbiri olmazsa []."""
    for tr in (0.5, 0.2):
        cap = O.sigan(ARKA, s, ust, W, tr)
        if cap >= MIN_ARKA_BOY:
            return [(s, cap, tr)]
    kelime = s.split()
    if len(kelime) > 1:
        iki = min(([" ".join(kelime[:j]), " ".join(kelime[j:])] for j in range(1, len(kelime))),
                  key=lambda x: max(len(x[0]), len(x[1])))
        cap = min(O.sigan(ARKA, x, ust, W, 0.5) for x in iki)
        if cap >= MIN_ARKA_BOY:
            return [(x, cap, 0.5) for x in iki]
    return []


def _arka(p, satirlar, kutu, uyar):
    """Arka yüz gömme satırları (arkadan okunur hâlde), alt alta ortalı; tek renk (yazı rengi: tablaya bakan
    katmanlarda tek filament). Genişe sığmayan satır daralır ya da ikiye bölünür; yine sığmayan ya da yükseklikte
    taşan satır (yarım kalmasın diye bütünüyle) atlanır, uyarı verilir."""
    W, H = kutu[2] - kutu[0], kutu[3] - kutu[1]
    out, y = [], 0.0
    for i, s in enumerate(satirlar):
        parca = _arka_parcalari(s, 3.6 if i == 0 else 3.2, W)
        yeni, y2 = [], y
        for metin, cap, tr in parca:
            cs, a = _ust_koy(O.yazi(ARKA, metin, cap, 0.0, 0.0, "c", tr, W, kabartma=False), y2)
            yeni.append((cs, p.yazi))
            y2 = a - 1.6
        if not parca or -(y2 + 1.6) > H:
            uyar.append(f"arka yüze '{s}' sığmadı")
            continue
        out += yeni
        y = y2
    return out


def tasarla(bicim, dizilim, c, palet, yazi_tipi, arka):
    """Döner Anahtarlik: front, back, lines (ön yüz yazıları, ölçülür), kalite (0: ad bu biçime sığmadı),
    uyarilar."""
    outline, hole_xy, kutu, arka_kutu = BICIMLER[bicim][1]()
    k = Anahtarlik(bicim, outline, hole_xy, kutu, arka_kutu)
    k.govde, k.palet, k.dizilim, k.yazi_tipi, k.uyarilar = palet.govde, palet, dizilim, yazi_tipi, []
    on, lines, k.kalite = _on(c, palet, dizilim, yazi_tipi, kutu, k.uyarilar)
    if on is None:
        k.uyarilar.append("ad bu biçime sığmadı")
        return k
    k.front, _ = _kutu_ortasi(on, kutu)
    adlar = {id(cs): n for n, cs in lines.items()}
    k.lines = {adlar[id(o)]: cs for (cs, _), (o, _) in zip(k.front, on) if id(o) in adlar}
    back = _arka(palet, arka, k.arka_kutu, k.uyarilar) if arka else []
    if back:
        x0, y0, x1, y1 = k.arka_kutu
        k.back, _ = _kutu_ortasi(back, (-x1, y0, -x0, y1))       # arkadan bakınca delik öbür yanda
    return k


def kontrol(k):
    """Ön kabartmada harf içi ve ara (≥ 0,6 mm), arka gömme yazıda (≥ 0,5), simgede ince alan, kırpılan alan."""
    import uzar_isimlik_baski as B
    sorun = []
    for n, cs in k.lines.items():
        inner, gap, _ = B.line_metrics(cs)
        if inner < MIN_ON or gap < MIN_ON:
            sorun.append(f"ön {n}: harf içi {inner:.2f}, ara {gap:.2f}")
    for i, (cs, _) in enumerate(k.back):
        inner, gap, _ = B.line_metrics(cs)
        if inner < MIN_ARKA or gap < MIN_ARKA:
            sorun.append(f"arka {i + 1}. satır: harf içi {inner:.2f}, ara {gap:.2f}")
    keep = k.keep()
    kirp = sum((cs - keep).area() for cs, _ in k.front) + sum((cs.mirror((1, 0)) - keep).area() for cs, _ in k.back)
    if kirp > 0.05:
        sorun.append(f"kenara ya da deliğe taşan alan {kirp:.1f} mm²")
    yazilar = {id(v) for v in k.lines.values()}
    simge = [cs for cs, _ in k.front if id(cs) not in yazilar]
    if simge:
        u = A.union(*simge)
        thin = u - u.offset(-0.45, J).offset(0.45, J)
        oran = 100 * sum(p.area() for p in thin.decompose() if p.area() > 0.02) / max(u.area(), 1e-6)
        if oran > 15.0:
            sorun.append(f"simgede 0,9 mm'den ince alan %{oran:.0f}")
    return sorun


# ---------------------------------------------------------------- tabla

X_AUX, TABLA = 20.5, 256.0                             # X2D yardımcı nozulu x < 20,5 mm'ye ulaşamaz
KULE = (24.0, 200.0)                                   # prime kulesi sol arkada (Bambu sınırı: kenardan 15 mm)
KULE_KUTU = (20.5, 192.0, 72.0, 248.0)


def tabla_yerleri(w, h, aralik=4.0):
    """Tablada kopyaların yerleri [(x, y, açı)]: iki nozulun ortak alanında ızgara, kulenin yeri boş."""
    out = []
    nx = int((TABLA - 2.0 - X_AUX - 1.0 + aralik) // (w + aralik))
    ny = int((TABLA - 8.0 + aralik) // (h + aralik))
    x0 = X_AUX + 1.0 + (TABLA - 2.0 - X_AUX - 1.0 - (nx * w + (nx - 1) * aralik)) / 2
    y0 = 4.0 + (TABLA - 8.0 - (ny * h + (ny - 1) * aralik)) / 2
    for j in range(ny):
        for i in range(nx):
            cx, cy = x0 + i * (w + aralik) + w / 2, y0 + j * (h + aralik) + h / 2
            if (cx + w / 2 + 4 > KULE_KUTU[0] and cx - w / 2 - 4 < KULE_KUTU[2] and
                    cy + h / 2 + 4 > KULE_KUTU[1] and cy - h / 2 - 4 < KULE_KUTU[3]):
                continue
            out.append((round(cx, 3), round(cy, 3), 0))
    return out


def gram(parcalar, adet=1):
    """PLA (1,24 g/cm³) tahmini gram, renk başına."""
    out = {}
    for _, m, c in parcalar:
        out[c] = round(out.get(c, 0.0) + adet * m.volume() * 1.24 / 1000, 1)
    return out


def kac_tabla(adet, tabla_basi):
    return max(1, math.ceil(adet / max(tabla_basi, 1)))


def gorunus(k, boy=700, arka=False):
    """Önden (üstten) ya da arkadan görünüş: RGBA."""
    from cift_tarafli_isimlik import render, rotation
    mesh = [(*A.mesh_arrays(m), O.TON[c]) for _, m, c in k.solids()]
    return render(mesh, boy, rotation(180, 180) if arka else A.R_TOP, margin=0.03)
