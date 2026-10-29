"""BOYDE LABS – farklı sektörlere örnek isimlikler (katalog ve Shopier için; işletme ve kişi adları uydurma).

Kullanıcı isteği: "sadece lastikçi olmasın, farklı firmalara özel de tasarım yap; sanayici, galerici, restoranları
hariç tut (onlara ayrı işlerimiz var); telefoncu ve başka aklına ne geliyorsa".

9 × 12 cm (120 × 90 mm, lastikçi isimlikleriyle aynı yapı: 1 cm gövde, 2 mm kabartma, QR yüzeyle aynı hizada):
  telefoncu  ÇAĞRI İLETİŞİM     siyah · beyaz · turkuaz   akıllı telefon, sol sütun + QR
  berber     MAKAS BERBER       siyah · beyaz · kırmızı · mavi   berber direği
  kuaför     Mira               beyaz · siyah · mor       makas, QR çerçeveli ("kuaförlere de yapabilirsin")
  güzellik   Luna               beyaz · siyah · pembe     hilal ve yıldız, ortalı sütun
  emlak      ANKA EMLAK         beyaz · mavi · turuncu    üst bant, içinde ev ve ad oyuk
  kuyumcu    SERA               siyah · beyaz · altın     pırlanta, ortalı başlık
  optik      NET OPTİK          beyaz · siyah · turkuaz   gözlük, QR çerçeveli
  veteriner  PATİ               beyaz · siyah · yeşil     sol blok, içinde pati ve ad oyuk
  spor       FORMA              siyah · beyaz · turuncu   dambıl, eğik yazı
10 × 20 cm (200 × 100 mm, Paloma'nın isimliğiyle aynı yapı: 5 mm gövde, yazılar yüzeyle aynı hizada renkli dolgu):
  avukat     Mehmet Kaya        beyaz · lacivert · altın  terazi
  dis        Zeynep Arslan      beyaz · siyah · turkuaz   sol blok, içinde diş
  musavir    Elif Demir         siyah · beyaz · yeşil     monogram
  mimar      Deniz Aydın        beyaz · siyah · turuncu   basamak işareti

Basılabilirlik (0,4 nozul): kabartmada çizgi ≥ 1,2 mm, harf içi ≥ 0,6 mm; dolguda çizgi ≥ 0,5 mm; öğeler arası
≥ 2 mm. QR'lar boyde_urunler'in örnek modunda (okunmaz) ve 34 mm'den küçük değil (kare ≥ 0,9 mm).
"""
import os
import sys

import manifold3d as m3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_urunler as U  # noqa: E402  (örnek modu: QR'lar okunmaz, telefon BOYDE'nin)
import anahtarlik as A  # noqa: E402
import qr_sistemi as Q  # noqa: E402

J = m3.JoinType.Round
BLACK, WHITE, RED, BLUE, GOLD = A.BLACK, A.WHITE, A.RED, A.BLUE, A.GOLD
TURQ, PINK, GREEN, ORANGE, NAVY, PURPLE = 21, 22, 23, 24, 25, 26   # yeni renk kimlikleri (Bambu PLA Basic tonları)
U.RGB.update({TURQ: (0, 150, 190), PINK: (238, 120, 150), GREEN: (0, 150, 80), ORANGE: (250, 110, 30),
              NAVY: (30, 44, 90), BLUE: (28, 66, 168), PURPLE: (104, 72, 178)})
NAMES = {BLACK: "siyah", WHITE: "beyaz", RED: "kırmızı", BLUE: "mavi", GOLD: "altın", TURQ: "turkuaz",
         PINK: "pembe", GREEN: "yeşil", ORANGE: "turuncu", NAVY: "lacivert", PURPLE: "mor"}
PHONE = Q.phone_display(U.TEL)
FONTS = {"outfit": "Outfit-ExtraBold.ttf", "lexend": "Lexend-ExtraBold.ttf", "bebas": "BebasNeue-Regular.ttf",
         "lora": "Lora_700Bold.ttf", "mont": "Montserrat_700Bold.ttf", "mont6": "Montserrat_600SemiBold.ttf",
         "cinzel": "Cinzel-Black.ttf", "sora": "Sora-ExtraBold.ttf", "righteous": "Righteous-Regular.ttf",
         "sairai": "Saira-CondensedBlackItalic.ttf", "jost": "Jost-Bold.ttf", "syne": "Syne-ExtraBold.ttf",
         "playfair": "PlayfairDisplay-Black.ttf"}
_F = {}


def font(k):
    if k not in _F:
        _F[k] = A.Font(FONTS[k])
    return _F[k]


def t(k, s, cap, x, y, align="l", tr=0.0, max_w=None):
    """Yazı; y büyük harflerin ortası. Küçük yazıda İ / Ö noktaları harften ayrık (loosen_dots)."""
    import uzar_isimlik_baski as B
    f = font(k)
    if max_w:
        cap = f.fit_cap(s, cap, max_w, tr)
    return B.loosen_dots(f.text(s, cap, x, y, align=align, tracking=tr))


def qr_entry(slug):
    """Örnek QR (okunmaz): 4. sürüm (33 × 33), 34 mm'lik karoda kare 0,92 mm."""
    import segno
    content = f"https://{slug}.qrsistem.workers.dev/"
    return Q.Entry("sayfa", "TARA", content, "TARA", qr=segno.make(content, error="m", version=4, micro=False))


class Design:
    def __init__(self, key, sc):
        self.key, self.sc = key, sc
        self.raised, self.inlay, self.lines = [], [], {}

    def add(self, name, cs, colour):
        self.raised.append((cs, colour))
        if name:
            self.lines[name] = cs
        return cs

    def flat(self, name, cs, colour):
        """Yüzeyle aynı hizada dolgu (gövde renginde: yalnız boşluk)."""
        if colour != self.sc["body"]:
            self.inlay.append((cs, colour))
        if name:
            self.lines[name] = cs
        return cs

    def qr(self, entry, cx, cy, s, sq=None, frame=None):
        """QR yüzeyle aynı hizada: açık gövdede koyu kareler (sq rengi), koyu gövdede beyaz karo. frame: çerçeve rengi."""
        _, dark, _ = Q.shapes(entry, Q.module_for(entry, s), cx, cy)
        tile = A.rrect(s, s, 1.6, cx, cy)
        if self.sc["dark"]:
            self.inlay.append((tile - dark, WHITE))
        else:
            self.inlay.append((dark ^ tile, sq or BLACK))
        if frame:
            g, w = 1.8, 1.2
            ring = A.rrect(s + 2 * (g + w), s + 2 * (g + w), 2.8, cx, cy) - A.rrect(s + 2 * g, s + 2 * g, 2.0, cx, cy)
            self.add(None, ring, frame)
        self.lines["QR"] = tile
        return tile


def bar(x0, x1, y, h):
    return A.rrect(x1 - x0, h, h / 2 - 0.01, (x0 + x1) / 2, y)


# ---------------------------------------------------------------- simgeler (kalın, sade: en ince yer ≥ 1,2 mm)

def ic_phone(cx, cy, h):
    w = h * 0.56
    outer = A.rrect(w, h, w * 0.2, cx, cy)
    screen = A.rrect(w - 3.2, h - 7.0, 0.8, cx, cy + 0.9)
    notch = A.rrect(w * 0.34, 1.4, 0.7, cx, cy + h / 2 - 1.6 - 1.6)
    return outer - screen + (notch ^ screen) + A.circle(1.1, cx, cy - h / 2 + 2.1)


def ic_pole(cx, cy, h, w=11.0):
    """Berber direği: beyaz çerçeve ve uçlar, içinde eğik kırmızı / mavi şeritler. Döner: (beyaz, kırmızı, mavi)."""
    inner = A.rrect(w - 3.0, h - 3.0, 1.0, cx, cy)
    frame = A.rrect(w, h, 2.0, cx, cy) - inner
    caps = A.rrect(w + 3.0, 3.2, 1.2, cx, cy + h / 2 + 2.2) + A.rrect(w + 3.0, 3.2, 1.2, cx, cy - h / 2 - 2.2)
    knob = A.circle(2.4, cx, cy + h / 2 + 5.8)
    reds, blues = [], []
    step, k = 5.4, 0
    y = cy - h / 2 - w
    while y < cy + h / 2 + w:
        band = A.polygon([(cx - w, y), (cx + w, y + w * 0.9), (cx + w, y + w * 0.9 + step * 0.5),
                          (cx - w, y + step * 0.5)])
        (reds if k % 2 == 0 else blues).append(band ^ inner.offset(-0.01, J))
        y += step
        k += 1
    return frame + caps + knob, A.union(*reds), A.union(*blues)


def ic_scissors(cx, cy, h, angle=-28.0):
    """Makas: iki halka, çapraz iki ağız (uçlar yuvarlatılır: en ince yer ≥ 1,2 mm). Ölçü: boy h."""
    k = h / 22.0
    rings = A.union(*[A.circle(3.6, sx * 3.3, -7.0) - A.circle(2.0, sx * 3.3, -7.0) for sx in (-1, 1)])
    blade = A.polygon([(-4.6, -5.4), (-1.6, -4.4), (3.6, 13.2), (2.5, 13.4)])
    mirror = blade.transform([[-1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    blades = (blade + mirror).offset(-0.6, J).offset(0.6, J)
    pivot = A.circle(1.0, 0.0, 1.2)
    return (rings + blades - pivot).scale((k, k)).rotate(angle).translate((cx, cy))


def ic_moon(cx, cy, r):
    c = A.circle(r, cx, cy, 128) - A.circle(r * 0.86, cx + r * 0.42, cy + r * 0.26, 128)
    c = c.offset(-0.6, J).offset(0.6, J)                       # sivri uçlar: en ince yer ≥ 1,2 mm
    s = r * 0.42
    star = A.polygon([(0, s), (s * 0.28, s * 0.28), (s, 0), (s * 0.28, -s * 0.28), (0, -s), (-s * 0.28, -s * 0.28),
                      (-s, 0), (-s * 0.28, s * 0.28)]).translate((cx + r * 0.62, cy + r * 0.55))
    return c + star


def ic_house(cx, cy, s):
    roof = A.stroke([(cx - s * 0.62, cy + s * 0.02), (cx, cy + s * 0.56), (cx + s * 0.62, cy + s * 0.02)], s * 0.16)
    walls = A.stroke([(cx - s * 0.42, cy + s * 0.08), (cx - s * 0.42, cy - s * 0.46), (cx + s * 0.42, cy - s * 0.46),
                      (cx + s * 0.42, cy + s * 0.08)], s * 0.14)
    door = A.rrect(s * 0.22, s * 0.32, s * 0.04, cx, cy - s * 0.3)
    chimney = A.rect(cx + s * 0.24, cy + s * 0.2, cx + s * 0.38, cy + s * 0.52)
    return roof + walls + door + chimney


def ic_diamond(cx, cy, w):
    h1, h2 = w * 0.26, w * 0.52
    gem = A.polygon([(-w / 2, 0), (-w * 0.3, h1), (w * 0.3, h1), (w / 2, 0), (0, -h2)])
    cuts = A.union(A.stroke([(-w / 2, 0), (w / 2, 0)], 0.8), A.stroke([(-w * 0.12, h1), (-w * 0.22, 0), (0, -h2)], 0.8),
                   A.stroke([(w * 0.12, h1), (w * 0.22, 0), (0, -h2)], 0.8))
    return (gem - cuts).translate((cx, cy))


def ic_glasses(cx, cy, w):
    r = w * 0.2
    dx = w * 0.27
    rings = A.union(*[A.circle(r, cx + sx * dx, cy) - A.circle(r - 1.8, cx + sx * dx, cy) for sx in (-1, 1)])
    bridge = A.stroke([(cx - dx + r - 0.6, cy + 0.6), (cx, cy + r * 0.5), (cx + dx - r + 0.6, cy + 0.6)], 1.6)
    arms = A.union(*[A.stroke([(cx + sx * (dx + r - 0.4), cy + 0.8), (cx + sx * (w / 2), cy + r * 0.9)], 1.6)
                     for sx in (-1, 1)])
    return rings + bridge + arms


def ic_paw(cx, cy, s):
    pad = A.circle(1.0, 0, 0, 96).scale((s * 0.3, s * 0.25)).translate((cx, cy - s * 0.16))
    toes = []
    for ang, rr, sz in ((-58, 0.36, 0.11), (-20, 0.42, 0.125), (20, 0.42, 0.125), (58, 0.36, 0.11)):
        import math
        a = math.radians(ang)
        toes.append(A.circle(1.0, 0, 0, 64).scale((s * sz, s * sz * 1.25)).rotate(-ang)
                    .translate((cx + s * rr * math.sin(a), cy + s * 0.08 + s * rr * math.cos(a) * 0.62)))
    return pad + A.union(*toes)


def ic_dumbbell(cx, cy, w):
    h = w * 0.42
    parts = [A.rect(cx - w * 0.49, cy - 1.3, cx + w * 0.49, cy + 1.3)]
    for sx in (-1, 1):
        parts.append(A.rrect(w * 0.1, h, 0.8, cx + sx * w * 0.27, cy))
        parts.append(A.rrect(w * 0.08, h * 0.7, 0.7, cx + sx * w * 0.39, cy))
        parts.append(A.rrect(w * 0.06, 2.6, 0.6, cx + sx * w * 0.47, cy))
    return A.union(*parts)


def ic_scales(cx, cy, s):
    """Terazi (dolgu için: çizgiler ≥ 0,9 mm)."""
    post = A.rect(cx - 0.7, cy - s * 0.44, cx + 0.7, cy + s * 0.36)
    base = A.rrect(s * 0.5, 1.6, 0.6, cx, cy - s * 0.45)
    beam = bar(cx - s * 0.42, cx + s * 0.42, cy + s * 0.3, 1.3)
    knob = A.circle(1.4, cx, cy + s * 0.42)
    out = [post, base, beam, knob]
    for sx in (-1, 1):
        px = cx + sx * s * 0.4
        out += [A.stroke([(px, cy + s * 0.3), (px - s * 0.13, cy - s * 0.09)], 0.9),
                A.stroke([(px, cy + s * 0.3), (px + s * 0.13, cy - s * 0.09)], 0.9),
                A.circle(s * 0.16, px, cy - s * 0.06) ^ A.rect(px - s, cy - s, px + s, cy - s * 0.06)]
    return A.union(*out)


def ic_tooth(cx, cy, s):
    pts = [(-7, 4), (-6.6, 7), (-4.2, 8.4), (-1.6, 7.8), (0, 7.0), (1.6, 7.8), (4.2, 8.4), (6.6, 7), (7, 4), (6.2, 0),
           (5.3, -4.2), (4.3, -7.6), (3.0, -8.4), (2.0, -7.0), (1.1, -3.2), (0, -2.2), (-1.1, -3.2), (-2.0, -7.0),
           (-3.0, -8.4), (-4.3, -7.6), (-5.3, -4.2), (-6.2, 0)]
    k = s / 17.0
    return A.polygon(A.smooth([(x * k + cx, y * k + cy) for x, y in pts], closed=True))


def ic_steps(cx, cy, s):
    """Mimar: üç basamak (artan çubuklar)."""
    w = s * 0.24
    return A.union(*[A.rect(cx - s / 2 + k * (w + s * 0.14), cy - s / 2, cx - s / 2 + k * (w + s * 0.14) + w,
                            cy - s / 2 + s * (0.42 + 0.29 * k)) for k in range(3)])


# ---------------------------------------------------------------- 9 × 12 cm (x −54..54, y ~12..86)

X0, X1 = -54.0, 54.0
DARK = {"body": BLACK, "fg": WHITE, "dark": True}
LIGHT = {"body": WHITE, "fg": BLACK, "dark": False}


def s_telefon():
    d = Design("telefon", DARK)
    q = qr_entry("cagriiletisim")
    d.add("simge", ic_phone(-48.0, 71.0, 21.0), TURQ)
    d.add("ÇAĞRI", t("lexend", "ÇAĞRI", 11.0, -39.0, 75.0, "l", 0.3, 47.0), WHITE)
    d.add("İLETİŞİM", t("outfit", "İLETİŞİM", 5.0, -39.0, 62.6, "l", 1.6, 47.0), TURQ)
    d.add(None, bar(X0, -26.0, 51.0, 1.6), TURQ)
    d.add("hizmet 1", t("outfit", "TELEFON · AKSESUAR", 4.0, X0, 43.0, "l", 0.5, 60.0), WHITE)
    d.add("hizmet 2", t("outfit", "TAMİR · TEKNİK SERVİS", 4.0, X0, 36.0, "l", 0.5, 60.0), WHITE)
    d.add("HEMEN ARA", t("outfit", "HEMEN ARA", 4.2, X0, 26.0, "l", 1.2), TURQ)
    d.add("telefon", t("outfit", PHONE, 5.4, X0, 17.0, "l", 0.4, 60.0), WHITE)
    tile = d.qr(q, 34.0, 48.0, 38.0)
    d.add("TARA", t("outfit", "TARA", 4.4, 34.0, tile.bounds()[1] - 5.6, "c", 1.8, 40.0), TURQ)
    return d


def s_berber():
    d = Design("berber", DARK)
    q = qr_entry("makasberber")
    white, red, blue = ic_pole(-47.0, 47.0, 50.0)
    d.add("direk", white, WHITE)
    d.add(None, red, RED)
    d.add(None, blue, BLUE)
    x = -36.0
    d.add("MAKAS", t("bebas", "MAKAS", 19.0, x, 69.0, "l", 0.8, 44.0), WHITE)
    d.add("BERBER", t("outfit", "BERBER", 5.2, x, 53.6, "l", 2.6, 44.0), RED)
    d.add("hizmet", t("outfit", "SAÇ · SAKAL · BAKIM", 4.0, x, 44.0, "l", 0.3, 44.0), WHITE)
    d.add("RANDEVU", t("outfit", "RANDEVU", 4.2, x, 29.0, "l", 1.4), RED)
    d.add("telefon", t("outfit", PHONE, 4.6, x, 20.0, "l", 0.3, 44.0), WHITE)
    tile = d.qr(q, 34.0, 50.0, 36.0)
    d.add("TARA", t("outfit", "TARA", 4.2, 34.0, tile.bounds()[1] - 6.0, "c", 1.6), WHITE)
    return d


def s_guzellik():
    d = Design("guzellik", LIGHT)
    q = qr_entry("lunaguzellik")
    cx = -24.0
    d.add("simge", ic_moon(cx - 1.5, 77.0, 6.4), PINK)
    d.add("Luna", t("lora", "Luna", 14.0, cx, 60.5, "c", 0.2, 56.0), BLACK)
    d.add("GÜZELLİK", t("outfit", "GÜZELLİK SALONU", 4.2, cx, 46.6, "c", 1.0, 58.0), PINK)
    d.add(None, bar(cx - 6.0, cx + 6.0, 39.6, 1.3), PINK)
    d.add("hizmet", t("outfit", "CİLT · KAŞ · MANİKÜR", 4.0, cx, 32.6, "c", 0.3, 58.0), BLACK)
    d.add("telefon", t("outfit", PHONE, 5.0, cx, 19.5, "c", 0.4, 58.0), BLACK)
    tile = d.qr(q, 33.0, 50.0, 36.0)
    d.add("RANDEVU", t("outfit", "RANDEVU", 4.2, 33.0, tile.bounds()[1] - 5.6, "c", 1.4, 40.0), PINK)
    return d


def s_kuafor():
    d = Design("kuafor", LIGHT)
    q = qr_entry("mirakuafor")
    d.add("simge", ic_scissors(-46.0, 74.0, 21.0), PURPLE)
    d.add("Mira", t("playfair", "Mira", 15.0, -34.0, 72.0, "l", 0.3, 40.0), BLACK)
    d.add("KUAFÖR", t("outfit", "KUAFÖR", 5.2, X0, 54.6, "l", 3.2, 60.0), PURPLE)
    d.add("hizmet 1", t("outfit", "KESİM · FÖN · BOYA", 4.0, X0, 44.0, "l", 0.5, 60.0), BLACK)
    d.add("hizmet 2", t("outfit", "GELİN SAÇI · BAKIM", 4.0, X0, 37.0, "l", 0.5, 60.0), BLACK)
    d.add("RANDEVU", t("outfit", "RANDEVU", 4.0, X0, 27.0, "l", 1.4), PURPLE)
    d.add("telefon", t("outfit", PHONE, 5.2, X0, 18.4, "l", 0.4, 60.0), BLACK)
    tile = d.qr(q, 34.0, 49.0, 36.0, sq=BLACK, frame=PURPLE)
    d.add("TARA", t("outfit", "TARA", 4.0, 34.0, tile.bounds()[1] - 8.6, "c", 1.6), PURPLE)
    return d


def s_emlak():
    d = Design("emlak", LIGHT)
    q = qr_entry("ankaemlak")
    band = A.rrect(112.0, 23.0, 4.0, 0.0, 74.0)
    cut = A.union(ic_house(-45.0, 73.4, 15.0), t("mont", "ANKA EMLAK", 9.0, -30.0, 74.0, "l", 0.6, 82.0))
    d.lines["ANKA EMLAK"] = cut
    d.add(None, band - cut.offset(0.0, J), BLUE)
    d.add("SATILIK", t("outfit", "SATILIK · KİRALIK", 4.6, X0, 52.0, "l", 0.8, 62.0), ORANGE)
    d.add("hizmet", t("outfit", "GAYRİMENKUL DANIŞMANLIĞI", 3.8, X0, 44.4, "l", 0.2, 62.0), BLACK)
    d.add("HEMEN ARA", t("outfit", "HEMEN ARA", 4.0, X0, 30.0, "l", 1.2), BLUE)
    d.add("telefon", t("outfit", PHONE, 5.4, X0, 20.6, "l", 0.4, 60.0), BLACK)
    tile = d.qr(q, 36.0, 40.0, 34.0, sq=BLUE)
    d.add("TARA", t("outfit", "TARA", 3.8, 36.0, tile.bounds()[1] - 4.8, "c", 1.4), ORANGE)
    return d


def s_kuyumcu():
    d = Design("kuyumcu", DARK)
    q = qr_entry("serakuyumculuk")
    d.add("simge", ic_diamond(0.0, 81.0, 15.0), GOLD)
    d.add("SERA", t("cinzel", "SERA", 12.0, 0.0, 66.5, "c", 2.4, 80.0), WHITE)
    sub = d.add("KUYUMCULUK", t("outfit", "KUYUMCULUK", 4.0, 0.0, 55.6, "c", 2.4, 70.0), GOLD)
    hw = (sub.bounds()[2] - sub.bounds()[0]) / 2
    d.add(None, bar(-48.0, -hw - 4.0, 55.6, 1.3) + bar(hw + 4.0, 48.0, 55.6, 1.3), GOLD)
    d.add("hizmet", t("outfit", "ALTIN · PIRLANTA · SAAT", 4.0, X0, 40.0, "l", 0.3, 60.0), WHITE)
    d.add("HEMEN ARA", t("outfit", "HEMEN ARA", 4.0, X0, 29.0, "l", 1.2), GOLD)
    d.add("telefon", t("outfit", PHONE, 5.2, X0, 20.0, "l", 0.4, 60.0), WHITE)
    d.qr(q, 36.0, 29.5, 34.0)
    return d


def s_optik():
    d = Design("optik", LIGHT)
    q = qr_entry("netoptik")
    d.add("simge", ic_glasses(-40.0, 77.0, 28.0), TURQ)
    d.add("NET", t("sora", "NET", 17.0, X0, 57.5, "l", 0.4, 58.0), BLACK)
    d.add("OPTİK", t("outfit", "OPTİK", 6.0, X0, 41.6, "l", 2.6, 58.0), TURQ)
    d.add("hizmet", t("outfit", "GÖZLÜK · LENS · GÜNEŞ", 4.0, X0, 32.4, "l", 0.3, 60.0), BLACK)
    d.add("telefon", t("outfit", PHONE, 5.2, X0, 19.5, "l", 0.4, 60.0), BLACK)
    tile = d.qr(q, 33.0, 50.0, 34.0, frame=TURQ)
    d.add("TARA", t("outfit", "TARA", 4.0, 33.0, tile.bounds()[1] - 8.4, "c", 1.6), TURQ)
    return d


def s_veteriner():
    d = Design("veteriner", LIGHT)
    q = qr_entry("pativeteriner")
    cx = -30.0
    block = A.rrect(48.0, 74.0, 5.0, cx, 49.0)
    cut = A.union(ic_paw(cx, 72.0, 17.0), t("righteous", "PATİ", 12.5, cx, 51.0, "c", 0.5, 42.0),
                  t("outfit", "VETERİNER", 4.4, cx, 38.0, "c", 0.8, 42.0),
                  t("outfit", "KLİNİĞİ", 4.4, cx, 31.0, "c", 0.8, 42.0),
                  t("outfit", "7/24 ACİL", 4.0, cx, 19.5, "c", 0.8, 42.0))
    d.lines["blok"] = cut
    d.add(None, block - cut.offset(0.0, J), GREEN)
    d.add("RANDEVU", t("outfit", "RANDEVU", 4.2, 30.0, 80.0, "c", 1.4), GREEN)
    d.qr(q, 30.0, 55.0, 38.0)
    d.add("telefon", t("outfit", PHONE, 4.8, 30.0, 23.0, "c", 0.3, 47.0), BLACK)
    return d


def s_spor():
    d = Design("spor", DARK)
    q = qr_entry("formaspor")
    d.add("simge", ic_dumbbell(-41.0, 80.0, 26.0), ORANGE)
    d.add("FORMA", t("sairai", "FORMA", 17.0, X0, 62.0, "l", 0.3, 64.0), WHITE)
    d.add("SPOR", t("outfit", "SPOR SALONU", 4.6, X0, 47.0, "l", 1.6, 62.0), ORANGE)
    d.add("hizmet", t("outfit", "FITNESS · PİLATES · BOKS", 4.0, X0, 38.6, "l", 0.2, 62.0), WHITE)
    d.add("HEMEN ARA", t("outfit", "HEMEN ARA", 4.0, X0, 28.0, "l", 1.2), ORANGE)
    d.add("telefon", t("outfit", PHONE, 5.2, X0, 19.0, "l", 0.4, 60.0), WHITE)
    tile = d.qr(q, 35.0, 50.0, 36.0)
    d.add("TARA", t("sairai", "TARA", 6.8, 35.0, tile.bounds()[1] - 7.0, "c", 1.2), ORANGE)
    return d


def solids(d):
    """lastikçi isimlikleriyle aynı (ince_isimlik.solids): gövde, dolgular, kabartmalar."""
    import uzar_isimlik as I
    import uzar_isimlik_baski as B
    out = I.outline()
    body = B.flat_chamfer(out.extrude(B.T), out)
    parts, pockets = [], []
    for cs, col in d.inlay:
        cs = cs ^ out.offset(-1.0, J)
        parts.append((f"Dolgu ({NAMES[col]})", cs.extrude(B.INLAY).translate((0, 0, B.T - B.INLAY)), col))
        pockets.append(cs)
    if pockets:
        body = body - A.union(*pockets).extrude(B.INLAY + 0.01).translate((0, 0, B.T - B.INLAY))
    taken, by_col = A.empty(), {}
    for cs, col in reversed(d.raised):
        part = (cs ^ out.offset(-1.0, J)) - taken
        taken = taken + cs
        by_col[col] = by_col.get(col, A.empty()) + part
    for col, cs in by_col.items():
        parts.append((f"Kabartma ({NAMES[col]})", cs.extrude(B.RELIEF).translate((0, 0, B.T)), col))
    return [(f"Panel ({NAMES[d.sc['body']]})", body, d.sc["body"])] + parts


# ---------------------------------------------------------------- 10 × 20 cm (x −90..90, y ~12..94; dolgu)

def p_avukat():
    d = Design("avukat", LIGHT)
    q = qr_entry("kayahukuk")
    x = -56.0
    d.flat("simge", ic_scales(-76.0, 60.0, 30.0), GOLD)
    d.flat("ad", t("lora", "Mehmet Kaya", 14.0, x, 78.0, "l", 0.1, 94.0), NAVY)
    d.flat("unvan", t("mont6", "AVUKAT · ARABULUCU", 5.4, x, 61.0, "l", 2.0, 94.0), GOLD)
    d.flat(None, bar(x, 34.0, 51.0, 0.9), GOLD)
    d.flat("büro", t("mont6", "KAYA HUKUK BÜROSU", 4.8, x, 40.0, "l", 1.6, 94.0), NAVY)
    d.flat("telefon", t("mont6", PHONE, 6.0, x, 26.0, "l", 0.4, 94.0), NAVY)
    tile = d.qr(q, 66.0, 56.0, 42.0, sq=NAVY)
    d.flat("KARTVİZİT", t("mont6", "KARTVİZİT", 4.2, 66.0, tile.bounds()[1] - 6.4, "c", 1.8), GOLD)
    return d


def p_dis():
    d = Design("dis", LIGHT)
    q = qr_entry("arslandis")
    cx = -67.0
    block = A.rrect(44.0, 82.0, 5.0, cx, 53.0)
    cut = A.union(ic_tooth(cx, 72.0, 24.0), t("mont", "ARSLAN", 6.0, cx, 46.0, "c", 1.0, 38.0),
                  t("mont6", "DİŞ KLİNİĞİ", 4.0, cx, 36.4, "c", 0.9, 38.0))
    d.lines["blok"] = cut
    d.flat(None, block - cut.offset(0.0, J), TURQ)
    x = -34.0
    d.flat("ad", t("mont6", "Dt. Zeynep", 12.5, x, 78.0, "l", 0.0, 68.0), BLACK)
    d.flat("soyad", t("mont6", "Arslan", 12.5, x, 58.0, "l", 0.0, 68.0), BLACK)
    d.flat("unvan", t("mont6", "Diş Hekimi", 6.8, x, 41.0, "l", 0.2, 68.0), TURQ)
    d.flat("telefon", t("mont6", f"Randevu: {PHONE}", 5.0, x, 24.0, "l", 0.3, 68.0), BLACK)
    tile = d.qr(q, 68.0, 56.0, 40.0)
    d.flat("RANDEVU", t("mont6", "RANDEVU", 4.2, 68.0, tile.bounds()[1] - 6.4, "c", 1.8), TURQ)
    return d


def p_musavir():
    d = Design("musavir", DARK)
    q = qr_entry("demirmusavir")
    sq = A.rrect(30.0, 30.0, 5.0, -73.0, 74.0)
    mono = t("mont", "ED", 11.0, -73.0, 74.0, "c", 0.4)
    d.lines["monogram"] = mono
    d.flat(None, sq - mono.offset(0.0, J), GREEN)
    x = -48.0
    d.flat("ad", t("mont6", "Elif Demir", 13.5, x, 80.0, "l", 0.0, 86.0), WHITE)
    d.flat("unvan", t("mont6", "SMMM · Mali Müşavir", 6.2, x, 64.0, "l", 0.3, 86.0), GREEN)
    d.flat(None, bar(-88.0, 34.0, 51.0, 0.9), GREEN)
    d.flat("büro", t("mont6", "DEMİR MALİ MÜŞAVİRLİK", 4.8, -88.0, 39.0, "l", 1.4, 120.0), WHITE)
    d.flat("telefon", t("mont6", PHONE, 6.0, -88.0, 25.0, "l", 0.4, 120.0), WHITE)
    tile = d.qr(q, 66.0, 56.0, 42.0)
    d.flat("KARTVİZİT", t("mont6", "KARTVİZİT", 4.2, 66.0, tile.bounds()[1] - 6.4, "c", 1.8), GREEN)
    return d


def p_mimar():
    d = Design("mimar", LIGHT)
    q = qr_entry("aydinmimarlik")
    d.flat("simge", ic_steps(-79.0, 79.0, 20.0), ORANGE)
    d.flat(None, bar(-62.0, 34.0, 79.0, 0.9), ORANGE)
    d.flat("ad", t("syne", "DENİZ AYDIN", 13.0, -88.0, 57.0, "l", 0.6, 122.0), BLACK)
    d.flat("unvan", t("jost", "YÜKSEK MİMAR", 5.8, -88.0, 41.0, "l", 2.4, 120.0), ORANGE)
    d.flat("büro", t("jost", "AYDIN MİMARLIK · İÇ MİMARLIK", 4.6, -88.0, 30.0, "l", 1.0, 120.0), BLACK)
    d.flat("telefon", t("jost", PHONE, 5.6, -88.0, 19.5, "l", 0.6, 120.0), BLACK)
    tile = d.qr(q, 66.0, 54.0, 42.0)
    d.flat("PORTFOLYO", t("jost", "PORTFOLYO", 4.4, 66.0, tile.bounds()[1] - 6.4, "c", 2.0), ORANGE)
    return d


def solids_20(d):
    """Paloma'nın isimliğiyle aynı (paloma_isimlik.solids): gövde ve yüzeyle aynı hizada dolgular."""
    import uzar_isimlik as I
    import uzar_isimlik_baski as B
    out = I.outline()
    clip = out.offset(-1.0, J)
    by_col = {}
    for cs, col in d.inlay:
        by_col[col] = by_col.get(col, A.empty()) + (cs ^ clip)
    body = B.flat_chamfer(out.extrude(B.T), out)
    if by_col:
        body = body - A.union(*by_col.values()).extrude(B.INLAY + 0.01).translate((0, 0, B.T - B.INLAY))
    parts = [(f"Panel ({NAMES[d.sc['body']]})", body, d.sc["body"])]
    for col, cs in by_col.items():
        parts.append((f"Dolgu ({NAMES[col]})", cs.extrude(B.INLAY).translate((0, 0, B.T - B.INLAY)), col))
    for cs, col in d.raised:
        parts.append((f"Kabartma ({NAMES[col]})", cs.extrude(2.0).translate((0, 0, B.T)), col))
    return parts


S9X12 = {"telefon": s_telefon, "berber": s_berber, "kuafor": s_kuafor, "guzellik": s_guzellik, "emlak": s_emlak, "kuyumcu": s_kuyumcu,
         "optik": s_optik, "veteriner": s_veteriner, "spor": s_spor}
S10X20 = {"avukat": p_avukat, "dis": p_dis, "musavir": p_musavir, "mimar": p_mimar}


def build(key):
    """Döner: boyde_urunler.Parcalar."""
    import uzar_isimlik_baski as B
    if key in S9X12:
        d = S9X12[key]()
        stand, mount = B.stand()
        p = U.Parcalar(solids(d), stand, BLACK, mount)
    else:
        import paloma_isimlik_baski as PB                      # 200 × 100 × 5 (modül ölçüleri değişir)
        d = S10X20[key]()
        stand, mount = B.stand(length=PB.STAND_LEN)
        p = U.Parcalar(solids_20(d), stand, d.sc["body"], mount)
    p.design = d
    return p


def report(d):
    """Satırların en dar harf içi ve arası (mm)."""
    import uzar_isimlik_baski as B
    out = []
    for k, cs in d.lines.items():
        if k == "QR":
            continue
        inner, gap, thin = B.line_metrics(cs)
        out.append(f"{k}: iç {inner:.2f} ara {gap:.2f}")
    return out
