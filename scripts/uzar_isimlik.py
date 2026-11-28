"""UZAR OTO LASTİK – QR'lı tezgâh isimliği önerileri: 4:3 yatay (120 × 90 mm), köşeleri yuvarlak, sade.

İki QR (tek baskıda, panelin ön yüzünde):
  * TARA · BİZE ULAŞ  → işletme sayfası (ara, WhatsApp, Instagram, Google'da değerlendir, IBAN kopyala, karekod,
                        rehbere kaydet); sayfa: scripts/uzar_sayfa.py, bilgiler: uzar_isimlik/bilgiler.json
  * KAREKOD İLE ÖDE   → bankanın karekodu (ENES UZAR, Yapı Kredi IBAN'ı): banka uygulamasıyla okutunca para
                        gönderme ekranı alıcısı ve IBAN'ı dolu açılır
Sayfa adresi sabit kaldıkça bilgiler (Instagram, Google bağlantısı, IBAN) isimlik yeniden basılmadan değişebilir.

Panel 120 × 90 × 2,6 mm (4:3), köşeler R8, kenarlar iki yüzde 0,6 mm basamaklı pahla yumuşatılmış. Ön yüzü tablada
basılır: yazılar ve QR'ın beyaz zemini ilk 4 katmanda yüzeye gömülü renkli dolgu (0,8 mm); QR'ın siyah kareleri
gövdenin kendisi. Tablada basılan yüz düz ve keskin; Textured PEI ile mat (QR'da parlama olmaz). Panel 100 mm'lik
siyah sehpanın yuvasına 15° arkaya eğik takılır (ortada alttaki ~7 mm yuvada kalır); iki parça aynı tablada.
QR kare boyu en az 0,9 mm (scripts/qr_sistemi.py).

Her tasarımda QR'lar ön görünüşün görüntüsünden (ve baskı hatası benzetiminden) okunarak doğrulanır.

Çıktı : uzar_isimlik/<tasarım>.png, uzar_isimlik/hepsi.png; müşteriye: musteri_1.png, musteri_2.png,
        musteri_katalog.pdf (10 öneri)

Kullanım:
  pip install segno zxing-cpp opencv-python-headless
  python3 scripts/uzar_isimlik.py [anahtar ...]
"""
import os
import sys

import manifold3d as m3
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import masa_isimligi_yeni as Y  # noqa: E402
import qr_sistemi as Q  # noqa: E402
import uzar_anahtarlik as U  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402
from masa_isimligi import Concept, upright  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "uzar_isimlik")
BLACK, WHITE, RED = (36, 36, 39), (246, 246, 242), (206, 28, 38)
NAMES = {BLACK: "siyah", WHITE: "beyaz", RED: "kırmızı"}
PW, PH = 120.0, 90.0             # panel 4:3 (x −60..60, y 0..90)
RADIUS = 8.0                     # köşe yuvarlatma
HIDDEN = 7.5                     # ortada sehpanın yuvasında kalan alt şerit
T = 2.6                          # panel kalınlığı (13 katman)
TILT = 15.0
STAND = dict(length=100.0, depth=30.0, height=10.0, r=8.0)
TILE = 44.1                      # QR karosu (karekod 45 + 2×2 kare × 0,9 mm)
CX = 26.0                        # karoların orta noktası (±x)
J = m3.JoinType.Round
INFO = Q.load()
QRS = {e.key: e for e in Q.qr_set(INFO, ["sayfa", "karekod"])}


# ---------------------------------------------------------------- parçalar

def heavy():
    return U.heavy()


def bold():
    return U.bold()


def outline():
    return A.rrect(PW, PH, RADIUS, 0, PH / 2)


def tile(key, cx, cy, s=TILE, r=1.2):
    """QR karosu: köşeleri yuvarlak beyaz kare eksi koyu kareler. Döner: (beyaz, koyu, kare boyu)."""
    e = QRS[key]
    module = Q.module_for(e, s)
    _, dark, _ = Q.shapes(e, module, cx, cy)
    return A.rrect(s, s, r, cx, cy) - dark, dark, module


def text(f, s, cap, x, y, align="l", tracking=0.0, max_w=None):
    if max_w:
        cap = f.fit_cap(s, cap, max_w, tracking)
    return f.text(s, cap, x, y, align=align, tracking=tracking)


def wordmark(cap, x, y, align="l"):
    """UZAR + kırmızı şimşek. Döner: (harfler, şimşek)."""
    f = heavy()
    letters = f.text("UZAR", cap, 0, y, align="l", tracking=cap * 0.04)
    b = U.bolt(cap * 1.15, 0, 0)
    b = b.translate((letters.bounds()[2] + cap * 0.1 - b.bounds()[0], y))
    w = b.bounds()[2] - letters.bounds()[0]
    dx = {"l": x, "c": x - w / 2, "r": x - w}[align] - letters.bounds()[0]
    return letters.translate((dx, 0)), b.translate((dx, 0))


def wordmark_width(cap):
    letters, b = wordmark(cap, 0, 0)
    return b.bounds()[2] - letters.bounds()[0]


def header_lr(fg):
    """Solda UZAR + şimşek, sağda OTO LASTİK / şehir (karoların dış kenarlarına hizalı, arada en az 7 mm)."""
    x0, x1 = -CX - TILE / 2, CX + TILE / 2
    letters, b = wordmark(14.0, x0, 76.5)
    room = x1 - (b.bounds()[2] + 7.0)
    return [(letters, fg), (b, RED),
            (text(bold(), "OTO LASTİK", 5.0, x1, 80.0, "r", 1.2, room), RED),
            (text(bold(), INFO.city, 3.6, x1, 72.2, "r", 1.3, room), fg)]


def two_tiles(y0, light=True):
    """Yan yana iki QR karosu (alt kenar y0). light: beyaz karo (siyah gövdede); False: siyah kareler (beyaz gövdede)."""
    out = []
    for key, cx in (("sayfa", -CX), ("karekod", CX)):
        white, dark, _ = tile(key, cx, y0 + TILE / 2)
        out.append(white if light else dark)
    return out


def labels(y, cap=3.8, cx=(-CX, CX)):
    f = bold()
    return [text(f, "TARA · BİZE ULAŞ", cap, cx[0], y, "c", cap * 0.1, TILE),
            text(f, "KAREKOD İLE ÖDE", cap, cx[1], y, "c", cap * 0.1, TILE)]


def soften(body, out, depth=0.6, steps=3):
    """Kenarları iki yüzde basamaklı pahla yumuşatır (katman başına 0,2 mm)."""
    rings = []
    for k in range(steps):
        ring = out - out.offset(-depth * (steps - k) / steps, J)
        rings.append(upright(ring, 0.2 + (0.01 if k == 0 else 0), k * 0.2 - (0.01 if k == 0 else 0)))
        rings.append(upright(ring, 0.2 + (0.01 if k == 0 else 0), T - (k + 1) * 0.2))
    return body - m3.Manifold.batch_boolean(rings, m3.OpType.Add)


# ---------------------------------------------------------------- tasarımlar

def s1_sade():
    """Siyah zemin; solda UZAR + şimşek, sağda OTO LASTİK / ANTALYA; altta iki QR."""
    c = Concept("1_sade", "Sade", "Siyah zemin, beyaz UZAR ve kırmızı şimşek; altta iki QR. Süs yok, bol boşluk.", "")
    reg = header_lr(WHITE)
    reg += [(t, WHITE) for t in two_tiles(16.5)]
    reg += [(t, WHITE) for t in labels(12.0)]
    return c, reg, BLACK


def s2_beyaz():
    """Beyaz zemin; siyah UZAR, kırmızı şimşek; QR'lar beyaz gövde üstünde siyah kare."""
    c = Concept("2_beyaz", "Beyaz", "Beyaz zemin, siyah UZAR ve kırmızı şimşek; QR'lar beyaz gövdede siyah kare.", "")
    reg = header_lr(BLACK)
    reg += [(t, BLACK) for t in two_tiles(16.5, light=False)]
    reg += [(t, BLACK) for t in labels(12.0)]
    return c, reg, WHITE


def s3_ortali():
    """Ortalanmış başlık: UZAR + şimşek, altında kırmızı OTO LASTİK · ANTALYA; etiketler kırmızı."""
    c = Concept("3_ortali", "Ortalı", "Başlık ortada: UZAR ve şimşek, altında kırmızı OTO LASTİK · ANTALYA; "
                "etiketler kırmızı.", "")
    letters, b = wordmark(14.0, 0.0, 78.0, "c")
    reg = [(letters, WHITE), (b, RED),
           (text(bold(), f"OTO LASTİK  ·  {INFO.city}", 4.2, 0.0, 66.4, "c", 1.25), RED)]
    reg += [(t, WHITE) for t in two_tiles(16.0)]
    reg += [(t, RED) for t in labels(11.6)]
    return c, reg, BLACK


def s4_tek_qr():
    """Tek büyük QR (sayfa) sağda; solda marka, TARA ve telefon. Karekod sayfada."""
    c = Concept("4_tek_qr", "Tek QR", "Tek büyük QR sağda (sayfayı açar, karekod sayfada); solda marka, TARA ve "
                "telefon. En sade.", "")
    c.uses = ("sayfa",)
    s, qx, qy = 54.0, 25.0, 47.0
    x0, x1 = -50.0, qx - s / 2 - 7.0
    cap = min(13.0, 10.0 * (x1 - x0) / wordmark_width(10.0))
    letters, b = wordmark(cap, x0, 71.0)
    white, _, _ = tile("sayfa", qx, qy, s, r=1.6)
    reg = [(letters, WHITE), (b, RED),
           (text(bold(), "OTO LASTİK", 4.6, x0, 58.6, "l", 1.25, x1 - x0), RED),
           (text(bold(), INFO.city, 3.4, x0, 52.2, "l", 1.2), WHITE),
           (text(heavy(), "TARA", 8.5, x0, 35.0, "l", 0.5), WHITE)]
    tx = reg[-1][0].bounds()[2] + 3.0
    reg.append((A.polygon([(tx, 31.8), (tx + 5.2, 35.0), (tx, 38.2)]), RED))
    reg += [(text(bold(), "BİZE ULAŞ · ÖDE", 3.8, x0, 25.5, "l", 0.45, x1 - x0), WHITE),
            (text(bold(), INFO.phone, 4.4, x0, 15.0, "l", 0.45, x1 - x0), WHITE),
            (white, WHITE)]
    return c, reg, BLACK


def s5_kirmizi_bant():
    """Üstte boydan kırmızı bant: beyaz UZAR, gövde renginde (siyah) şimşek; altta iki QR."""
    c = Concept("5_kirmizi_bant", "Kırmızı bant", "Üstte boydan kırmızı bant, içinde beyaz UZAR ve siyah şimşek; "
                "altta iki QR.", "")
    x0, x1 = -CX - TILE / 2, CX + TILE / 2
    letters, b = wordmark(14.0, x0, 78.5)
    room = x1 - (b.bounds()[2] + 7.0)
    band = A.rect(-70, 66.0, 70, 100) ^ outline()
    reg = [(band - b, RED), (letters, WHITE),
           (text(bold(), "OTO LASTİK", 5.0, x1, 82.0, "r", 1.2, room), WHITE),
           (text(bold(), INFO.city, 3.6, x1, 74.2, "r", 1.3, room), WHITE)]
    reg += [(t, WHITE) for t in two_tiles(16.5)]
    reg += [(t, WHITE) for t in labels(12.0)]
    return c, reg, BLACK


def s6_cerceve():
    """İnce kırmızı çerçeve (görünen yüzün içinde); solda UZAR, sağda OTO LASTİK; iki QR."""
    c = Concept("6_cerceve", "Kırmızı çerçeve", "Kenardan içeride ince kırmızı çerçeve; içinde UZAR, OTO LASTİK ve "
                "iki QR.", "")
    w, h, cy = 114.0, 79.0, 48.1
    frame = A.rrect(w, h, 5.0, 0, cy) - A.rrect(w - 1.8, h - 1.8, 4.1, 0, cy)
    x0, x1 = -CX - TILE / 2, CX + TILE / 2
    letters, b = wordmark(13.0, x0, 75.5)
    room = x1 - (b.bounds()[2] + 7.0)
    reg = [(frame, RED), (letters, WHITE), (b, RED),
           (text(bold(), "OTO LASTİK", 4.8, x1, 78.6, "r", 1.15, room), RED),
           (text(bold(), INFO.city, 3.4, x1, 71.4, "r", 1.25, room), WHITE)]
    reg += [(t, WHITE) for t in two_tiles(17.5)]
    reg += [(t, WHITE) for t in labels(13.1, 3.6)]
    return c, reg, BLACK


def s7_dikey_serit():
    """Solda dikey kırmızı şerit, içinde yukarı doğru beyaz UZAR ve siyah şimşek; sağda iki QR."""
    c = Concept("7_dikey_serit", "Dikey şerit", "Solda dikey kırmızı şerit, içinde yukarı doğru UZAR; sağda başlık "
                "ve iki QR.", "")
    band = A.rect(-70, -1, -45.0, 100) ^ outline()
    up = text(heavy(), "UZAR", 10.5, 0, 0, "c", 0.6).rotate(90).translate((-52.5, 54.0))
    b = U.bolt(12.0, -52.5, 25.0)
    xl, xr = -40.5, 53.5
    cl, cr = xl + TILE / 2, xr - TILE / 2
    reg = [(band - b, RED), (up, WHITE),
           (text(heavy(), "OTO LASTİK", 9.0, xl, 77.5, "l", 0.6), WHITE),
           (text(bold(), f"{INFO.city}  ·  {INFO.phone}", 3.6, xl, 68.4, "l", 0.8), RED)]
    for key, cx in (("sayfa", cl), ("karekod", cr)):
        white, _, _ = tile(key, cx, 16.5 + TILE / 2)
        reg.append((white, WHITE))
    reg += [(t, WHITE) for t in labels(12.0, cx=(cl, cr))]
    return c, reg, BLACK


def s8_beyaz_siyah_bant():
    """Beyaz panel, üstte boydan siyah bant: içinde beyaz UZAR, kırmızı şimşek; QR'lar beyaz gövdede siyah kare."""
    c = Concept("8_beyaz_siyah_bant", "Beyaz, siyah başlık", "Beyaz panel, üstte siyah bant içinde beyaz UZAR ve "
                "kırmızı şimşek; QR'lar beyaz gövdede siyah kare.", "")
    x0, x1 = -CX - TILE / 2, CX + TILE / 2
    letters, b = wordmark(14.0, x0, 78.5)
    room = x1 - (b.bounds()[2] + 7.0)
    band = A.rect(-70, 66.0, 70, 100) ^ outline()
    city = text(bold(), INFO.city, 3.6, x1, 74.2, "r", 1.3, room)
    reg = [(band - letters - city, BLACK), (b, RED),
           (text(bold(), "OTO LASTİK", 5.0, x1, 82.0, "r", 1.2, room), RED)]
    reg += [(t, BLACK) for t in two_tiles(16.5, light=False)]
    reg += [(t, BLACK) for t in labels(12.0)]
    return c, reg, WHITE


def s9_lastik_izi():
    """Sade düzen; başlığın altında sitedeki gibi kırmızı lastik dişi şeridi."""
    c = Concept("9_lastik_izi", "Lastik izi", "Sade düzen; başlıkla QR'lar arasında sitedeki gibi kırmızı lastik "
                "dişi şeridi.", "")
    reg = header_lr(WHITE)
    x0, x1 = -CX - TILE / 2, CX + TILE / 2
    reg.append((U.tread_band(x0, x1, 63.0, 66.2, pitch=3.6), RED))
    reg += [(t, WHITE) for t in two_tiles(16.5)]
    reg += [(t, WHITE) for t in labels(12.0)]
    return c, reg, BLACK


def s10_site_gibi():
    """Sitenin üst kısmı gibi: UZAR + şimşek, altında kırmızı OTO LASTİK, sağ üstte üç eğik kırmızı şerit."""
    c = Concept("10_site_gibi", "Siteyle aynı", "Sitenin açılışındaki gibi: UZAR, şimşek, kırmızı OTO LASTİK ve sağ "
                "üstte üç eğik şerit.", "")
    x0 = -CX - TILE / 2
    letters, b = wordmark(13.5, x0, 80.0)
    k = 0.53                                         # şerit eğimi (sitedeki 28°)
    stripes = []
    for xb, w in ((22.0, 1.8), (29.0, 4.0), (39.0, 9.0)):
        y0, y1 = 64.0, 100.0
        stripes.append(A.polygon([(xb, y0), (xb + w, y0), (xb + w + k * (y1 - y0), y1), (xb + k * (y1 - y0), y1)]))
    reg = [(A.union(*stripes) ^ outline(), RED), (letters, WHITE), (b, RED),
           (text(bold(), "OTO LASTİK", 4.6, x0, 68.8, "l", 1.6), RED)]
    reg += [(t, WHITE) for t in two_tiles(16.5)]
    reg += [(t, WHITE) for t in labels(12.0)]
    return c, reg, BLACK


DESIGNS = [s1_sade, s2_beyaz, s3_ortali, s4_tek_qr, s5_kirmizi_bant, s6_cerceve, s7_dikey_serit,
           s8_beyaz_siyah_bant, s9_lastik_izi, s10_site_gibi]


# ---------------------------------------------------------------- yapım, kontrol, çizim

def build(fn):
    c, reg, body = fn()
    out = outline()
    flat = Y.inlaid_panel(out, reg, body, thickness=T)
    flat[0] = (soften(flat[0][0], out), flat[0][1])
    z0, y0 = 3.0, 2.0
    slot = Y.tilted(upright(out, T + 0.3, -0.15), TILT, z0, y0)
    base = Y.stand(**STAND) - slot
    c.add(base, BLACK)
    for m, col in flat:
        c.add(Y.tilted(m, TILT, z0, y0), col)
    c.flat, c.regions, c.body, c.outline = flat, reg, body, out
    g = {}
    for m, col in c.parts:
        g[col] = g.get(col, 0.0) + Y.grams(m)
    c.g = g
    c.expected = [QRS[k].content for k in getattr(c, "uses", ("sayfa", "karekod"))]
    return c


def front(c, size=1500):
    """Panelin düz ön görünüşü (gölgesiz) – QR okuma için."""
    parts = [(*A.mesh_arrays(m), col) for m, col in c.flat]
    im = render(parts, size, rotation(0, -90), light=False, margin=0.03)
    bg = Image.new("RGB", im.size, (150, 152, 158))
    bg.paste(im, (0, 0), im)
    return bg


def qr_check(c):
    """Ön görünüşteki QR'ları okur; ayrıca 'hepsi birden' baskı / okutma benzetiminde."""
    im = front(c).convert("L")
    ppm = im.width * (1 - 2 * 0.03) / PW
    got = set(Q.decode(im))
    sim = Q.simulate(im, ppm, 0.9, **dict(Q.SIM_CASES)["hepsi birden"])
    got_sim = set(Q.decode(sim))
    return [(t, t in got, t in got_sim) for t in c.expected]


def thin(c, limit=0.8):
    """Renkli dolgularda `limit` mm'den ince kısım (%), renk başına."""
    out, total = {}, {}
    for cs, col in c.regions:
        cs = cs ^ c.outline
        k = cs - cs.offset(-limit / 2, J).offset(limit / 2, J)
        out[NAMES[col]] = out.get(NAMES[col], 0.0) + sum(p.area() for p in k.decompose() if p.area() > 0.02)
        total[NAMES[col]] = total.get(NAMES[col], 0.0) + cs.area()
    return {k: round(100 * v / total[k], 1) for k, v in out.items() if total[k] > 0}


def font_ui(size):
    return ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), size)


def mesh(parts):
    return [(*A.mesh_arrays(m), col) for m, col in parts]


def sheet(c, i):
    views = [(rotation(0, -90), "Önden, sehpada (120 × 90 mm)"), (rotation(-28, -68), "Tezgâhta (3/4)"),
             (rotation(-90, -90), f"Yandan: {TILT:.0f}° eğik")]
    W, H = 1500, 700
    canvas = Image.new("RGB", (W, H), (236, 239, 244))
    dr = ImageDraw.Draw(canvas)
    boxes = [(30, 130, 700, 630), (720, 130, 1240, 630), (1260, 130, 1470, 630)]
    parts = mesh(c.parts)
    for (R, label), (x0, y0, x1, y1) in zip(views, boxes):
        dr.rounded_rectangle((x0, y0, x1, y1), 22, fill=(146, 153, 166))
        im = A.fit_into(render(parts, 1200, R, flat=0.85 if label.startswith("Önden") else None, margin=0.02),
                        x1 - x0 - 40, y1 - y0 - 60)
        canvas.paste(im, (x0 + (x1 - x0 - im.width) // 2, y0 + 40 + (y1 - y0 - 40 - im.height) // 2), im)
        dr.text((x0 + 16, y0 + 10), label, fill=(236, 239, 244), font=font_ui(18))
    dr.text((30, 18), f"{i}. {c.title.upper()}", fill=(24, 26, 30), font=font_ui(32))
    dr.text((30, 62), c.desc, fill=(80, 86, 98), font=font_ui(19))
    total = sum(c.g.values())
    g = "  ·  ".join(f"{NAMES[k]} {v:.0f} g" for k, v in sorted(c.g.items(), key=lambda kv: -kv[1]))
    dr.text((30, 94), f"~{total:.0f} g filament ({g}; panel + sehpa)  ·  ~{total * 0.5:.0f} TL filament",
            fill=(22, 120, 60), font=font_ui(19))
    y = 644
    for content, ok, ok_sim in c.qr:
        label = "sayfa" if content == QRS["sayfa"].content else "banka karekodu"
        dr.text((30, y), f"QR {label}: " + ("okundu" if ok else "OKUNMADI") +
                (", baskı hatası benzetiminde de okundu" if ok_sim else ", benzetimde OKUNMADI"),
                fill=(22, 120, 60) if ok and ok_sim else (200, 30, 38), font=font_ui(17))
        y += 24
    canvas.save(os.path.join(OUT_DIR, c.key + ".png"))
    return canvas


def overview(cs, path):
    cw, ch, gap = 760, 500, 20
    rows = (len(cs) + 1) // 2
    W, H = 2 * cw + 3 * gap, rows * ch + (rows + 1) * gap + 110
    canvas = Image.new("RGB", (W, H), (244, 245, 247))
    dr = ImageDraw.Draw(canvas)
    dr.text((24, 20), "UZAR OTO LASTİK – QR'LI TEZGÂH İSİMLİĞİ (4:3, 120 × 90 mm)", fill=(24, 26, 30),
            font=font_ui(34))
    dr.text((24, 66), "Sol QR: sayfa (ara · WhatsApp · Instagram · Google · IBAN)  ·  sağ QR: banka karekodu "
                      "(ENES UZAR, Yapı Kredi)  ·  hepsi görüntüden okundu", fill=(110, 114, 124), font=font_ui(19))
    for k, c in enumerate(cs):
        x, y = gap + (k % 2) * (cw + gap), 110 + gap + (k // 2) * (ch + gap)
        dr.rounded_rectangle((x, y, x + cw, y + ch), 24, fill=(226, 228, 232))
        parts = mesh(c.parts)
        f = A.fit_into(render(parts, 1100, rotation(0, -90), flat=0.85, margin=0.02), 420, 360)
        p = A.fit_into(render(parts, 1000, rotation(-28, -68), margin=0.02), 280, 360)
        canvas.paste(f, (x + 20 + (420 - f.width) // 2, y + 64 + (360 - f.height) // 2), f)
        canvas.paste(p, (x + 460 + (280 - p.width) // 2, y + 64 + (360 - p.height) // 2), p)
        dr.text((x + 20, y + 14), f"{k + 1}. {c.title}", fill=(30, 33, 40), font=font_ui(26))
        ok = all(a and b for _, a, b in c.qr)
        dr.text((x + 20, y + ch - 52), f"~{sum(c.g.values()):.0f} g  ·  ~{sum(c.g.values()) * 0.5:.0f} TL filament  ·  "
                                      + ("QR'lar okundu" if ok else "QR OKUNMADI"),
                fill=(22, 120, 60) if ok else (200, 30, 38), font=font_ui(19))
    canvas.save(path)


CUSTOMER = {"1_sade": "Siyah zemin, beyaz yazı, kırmızı şimşek. En sade hâli.",
            "2_beyaz": "Beyaz zemin, siyah yazı, kırmızı şimşek.",
            "3_ortali": "Başlık ortada, etiketler kırmızı.",
            "4_tek_qr": "Tek büyük QR: sayfayı açar, ödeme (IBAN, karekod) sayfanın içinde.",
            "5_kirmizi_bant": "Üstte kırmızı bant, içinde beyaz UZAR.",
            "6_cerceve": "İnce kırmızı çerçeve, dengeli ve şık.",
            "7_dikey_serit": "Solda dikey kırmızı şerit, yukarı doğru UZAR.",
            "8_beyaz_siyah_bant": "Beyaz zemin, üstte siyah bant.",
            "9_lastik_izi": "Başlığın altında kırmızı lastik izi şeridi.",
            "10_site_gibi": "Web sitesiyle aynı görünüm: eğik kırmızı şeritler."}


def wrap(dr, s, font, width):
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if dr.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + [cur] if cur else lines


def phone_shots(width=390):
    """Sitenin telefon görüntüleri (hareketsiz son hâl): üst kısım ve ödeme kartı (karekod açık)."""
    import io
    from playwright.sync_api import sync_playwright
    url = "file://" + os.path.join(OUT_DIR, "site", "index.html")
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = b.new_page(viewport={"width": width, "height": 760}, device_scale_factor=2, reduced_motion="reduce")
        pg.goto(url)
        pg.wait_for_timeout(300)
        top = Image.open(io.BytesIO(pg.screenshot()))
        pg.click("details.kk summary")
        pg.wait_for_timeout(200)
        pay = Image.open(io.BytesIO(pg.locator("section.pay").screenshot()))
        b.close()
    return top, pay


def rounded(im, r):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255)
    out = im.convert("RGBA")
    out.putalpha(mask)
    return out


def catalog(cs):
    """Müşteriye gönderilecek sayfalar (A4 dikey, 200 dpi): musteri_1.png (1–6), musteri_2.png (7–10) ve
    ikisi birlikte musteri_katalog.pdf. Teknik bilgi yok; yalnız tasarım, numara ve QR'ların ne yaptığı."""
    W, H = 1654, 2339
    big = ImageFont.truetype(os.path.join(A.FONT_DIR, "BarlowCondensed-Black.ttf"), 118)
    mid = ImageFont.truetype(os.path.join(A.FONT_DIR, "BarlowCondensed-ExtraBold.ttf"), 44)
    f = lambda n: ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), n)  # noqa: E731
    ink, muted, paper = (20, 20, 22), (96, 98, 106), (245, 245, 243)
    groups = [cs[:6], cs[6:]]
    pages = []
    for p, group in enumerate(groups):
        im = Image.new("RGB", (W, H), paper)
        dr = ImageDraw.Draw(im)
        dr.rectangle((0, 0, W, 250), fill=(16, 16, 18))
        for x, w in ((1180, 22), (1250, 50), (1350, 120)):
            dr.polygon([(x, 250), (x + w, 250), (x + w + 133, 0), (x + 133, 0)], fill=RED)
        dr.text((70, 40), "UZAR", font=big, fill=(244, 244, 242))
        dr.text((76 + dr.textlength("UZAR", font=big) + 18, 70), "OTO LASTİK", font=mid, fill=RED)
        dr.text((76 + dr.textlength("UZAR", font=big) + 18, 128), "ANTALYA", font=f(26), fill=(170, 170, 176))
        dr.text((70, 186), "QR'lı tezgâh isimliği · tasarım önerileri", font=f(30), fill=(220, 220, 224))
        dr.text((W - 70 - dr.textlength(f"{p + 1}/2", font=f(28)), 196), f"{p + 1}/2", font=f(28),
                fill=(170, 170, 176))
        y = 285
        for line in ("TARA · BİZE ULAŞ: telefonla okutunca işletme sayfası açılır (ara, WhatsApp, Instagram, Google, IBAN).",
                     "KAREKOD İLE ÖDE: banka uygulamasıyla okutunca ödeme ekranı ENES UZAR adına hazır açılır."):
            dr.text((70, y), line, font=f(27), fill=ink)
            y += 40
        top, gap, cw = 395, 50, (W - 3 * 60) // 2
        ch = (H - top - 190 - 2 * gap) // 3
        for k, c in enumerate(group):
            x0, y0 = 60 + (k % 2) * (cw + 60), top + (k // 2) * (ch + gap)
            dr.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 28, fill=(255, 255, 255), outline=(226, 226, 230))
            n = cs.index(c) + 1
            dr.ellipse((x0 + 26, y0 + 24, x0 + 86, y0 + 84), fill=RED)
            num = str(n)
            dr.text((x0 + 56 - dr.textlength(num, font=f(34)) / 2, y0 + 34), num, font=f(34), fill=(255, 255, 255))
            dr.text((x0 + 104, y0 + 30), c.title, font=f(38), fill=ink)
            img = A.fit_into(render(mesh(c.parts), 1300, rotation(0, -90), flat=0.85, margin=0.02), cw - 70, ch - 190)
            im.paste(img, (x0 + (cw - img.width) // 2, y0 + 100 + (ch - 190 - img.height) // 2), img)
            ty = y0 + ch - 78
            for line in wrap(dr, CUSTOMER.get(c.key, c.desc), f(26), cw - 60)[:2]:
                dr.text((x0 + 30, ty), line, font=f(26), fill=muted)
                ty += 34
        rows = (len(group) + 1) // 2
        if p == 1 and rows < 3:                         # boş kalan yere: okutunca açılan sayfa
            y0, y1 = top + rows * (ch + gap), H - 190
            dr.rounded_rectangle((60, y0, W - 60, y1), 28, fill=(255, 255, 255), outline=(226, 226, 230))
            dr.text((100, y0 + 40), "TARA ile telefonda", font=f(38), fill=ink)
            dr.text((100, y0 + 88), "açılan sayfa", font=f(38), fill=ink)
            ty = y0 + 170
            for line in ("Hemen Ara: telefon uygulaması açılır", "WhatsApp: hazır mesajla yazışma",
                         "Instagram ve Google yorumları", "IBAN tek dokunuşla kopyalanır",
                         "Karekod ile ödeme"):
                dr.ellipse((100, ty + 10, 114, ty + 24), fill=RED)
                dr.text((130, ty), line, font=f(27), fill=muted)
                ty += 48
            top_shot, pay_shot = phone_shots()
            top_shot = top_shot.crop((0, 0, top_shot.width, min(top_shot.height, 1240)))
            box_h = y1 - y0 - 60
            x = W - 100
            for shot in (pay_shot, top_shot):           # sağdan sola
                k = box_h / shot.height
                sh = rounded(shot.resize((int(shot.width * k), int(shot.height * k)), Image.LANCZOS), 22)
                x -= sh.width
                im.paste(sh, (x, y0 + 30), sh)
                x -= 40
        foot = ("Ölçü 12 × 9 cm · tezgâh sehpası dahil · siyah, kırmızı, beyaz" if p == 0 else
                "Beğendiğiniz tasarımın numarasını yazmanız yeterli. Ölçü 12 × 9 cm, tezgâh sehpası dahil.")
        dr.rounded_rectangle((60, H - 150, W - 60, H - 70), 22, fill=(16, 16, 18))
        dr.text((W / 2 - dr.textlength(foot, font=f(30)) / 2, H - 128), foot, font=f(30), fill=(244, 244, 242))
        path = os.path.join(OUT_DIR, f"musteri_{p + 1}.png")
        im.save(path, optimize=True)
        pages.append(im)
    pages[0].save(os.path.join(OUT_DIR, "musteri_katalog.pdf"), save_all=True, append_images=pages[1:],
                  resolution=200)
    return pages


def main():
    only = sys.argv[1:]
    if only == ["katalog"]:                              # yalnız müşteri kataloğu (QR denetimi ve sayfalar yok)
        catalog([build(fn) for fn in DESIGNS])
        return
    cs = []
    for i, fn in enumerate(DESIGNS, 1):
        c = build(fn)
        if only and not any(o in c.key for o in only):
            continue
        c.qr = qr_check(c)
        sheet(c, i)
        cs.append(c)
        bad = [k for k, (m, _) in enumerate(c.parts) if not str(m.status()).endswith("NoError") or m.volume() <= 0]
        mods = {k: float(Q.module_for(e, TILE)) for k, e in QRS.items()}
        print(f"{c.key:12s} ~{sum(c.g.values()):4.0f} g  QR: {[(ok, sim) for _, ok, sim in c.qr]}  "
              f"0,8 mm'den ince (%): {thin(c)}  kare: {mods}  bozuk: {bad}")
    if not only:
        overview(cs, os.path.join(OUT_DIR, "hepsi.png"))
        catalog(cs)


if __name__ == "__main__":
    main()
