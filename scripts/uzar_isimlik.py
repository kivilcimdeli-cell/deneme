"""UZAR OTO LASTİK – QR'lı tezgâh isimliği önerileri (~10 × 10 cm): kırmızı, siyah, beyaz.

İki QR (tek baskıda, panelin ön yüzünde):
  * TARA · BİZE ULAŞ  → işletme sayfası (ara, WhatsApp, Instagram, Google'da değerlendir, IBAN kopyala, karekod,
                        rehbere kaydet); sayfa: scripts/uzar_sayfa.py, bilgiler: uzar_isimlik/bilgiler.json
  * KAREKOD İLE ÖDE   → bankanın karekodu (ENES UZAR, Yapı Kredi IBAN'ı): banka uygulamasıyla okutunca para
                        gönderme ekranı alıcısı ve IBAN'ı dolu açılır
Sayfa adresi sabit kaldıkça bilgiler (Instagram, Google bağlantısı, IBAN) isimlik yeniden basılmadan değişebilir.

Panel 100 × 108 × 3 mm, ön yüzü tablada basılır: yazılar, şerit ve QR'ın beyaz zemini ilk 4 katmanda yüzeye gömülü
renkli dolgu (0,8 mm); QR'ın siyah kareleri gövdenin kendisi. Tablada basılan yüz düz ve keskin; Textured PEI ile
mat (QR'da parlama olmaz). Panel siyah sehpanın yuvasına 15° arkaya eğik takılır (alttaki 8 mm yuvada kalır),
iki parça aynı tablada basılır. QR kare boyu en az 0,9 mm (scripts/qr_sistemi.py).

Her tasarımda QR'lar ön görünüşün görüntüsünden (ve baskı hatası benzetiminden) okunarak doğrulanır.

Çıktı : uzar_isimlik/<tasarım>.png, uzar_isimlik/hepsi.png

Kullanım:
  pip install segno zxing-cpp opencv-python-headless
  python3 scripts/uzar_isimlik.py [anahtar ...]
"""
import os
import sys

import manifold3d as m3
import numpy as np
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
PW, PH = 100.0, 108.0            # panel (x −50..50, y 0..108); alttaki HIDDEN mm sehpanın yuvasında
HIDDEN = 8.0
T = 2.6                          # panel kalınlığı (13 katman)
TILT = 15.0
STAND = dict(length=84.0, depth=32.0, height=10.0, r=8.0)
SLOPE = np.tan(np.radians(28))   # şeritlerin eğimi (sayfadaki gibi)
TILE = 44.1                      # QR karosu (karekod 45 + 2×2 kare × 0,9 mm)
CX = 24.6                        # karoların orta noktası (±x)
J = m3.JoinType.Round
INFO = Q.load()
QRS = {e.key: e for e in Q.qr_set(INFO, ["sayfa", "karekod"])}


# ---------------------------------------------------------------- parçalar

def heavy():
    return U.heavy()


def bold():
    return U.bold()


def outline(r=5.0):
    return A.rrect(PW, PH, r, 0, PH / 2)


def tile(key, cx, cy, s=TILE, r=1.2):
    """QR karosu: köşeleri yuvarlak beyaz kare eksi koyu kareler. Döner: (beyaz, koyu, kare boyu)."""
    e = QRS[key]
    module = Q.module_for(e, s)
    _, dark, _ = Q.shapes(e, module, cx, cy)
    return A.rrect(s, s, r, cx, cy) - dark, dark, module


def brackets(cx, cy, s=TILE, gap=0.9, w=1.0, L=6.5):
    """Karonun köşelerinde 'burayı okut' köşebentleri."""
    h = s / 2 + gap
    frame = A.rrect(2 * (h + w), 2 * (h + w), w, cx, cy) - A.rect(cx - h, cy - h, cx + h, cy + h)
    corners = A.union(*[A.rect(cx + sx * (h + w) - (L if sx > 0 else 0), cy + sy * (h + w) - (L if sy > 0 else 0),
                               cx + sx * (h + w) + (0 if sx > 0 else L), cy + sy * (h + w) + (0 if sy > 0 else L))
                        for sx in (-1, 1) for sy in (-1, 1)])
    return frame ^ corners


def stripe(xb, w, y0, y1):
    """Eğik şerit (alt kenarı xb'de, sağa yatık)."""
    d = SLOPE * (y1 - y0)
    return A.polygon([(xb, y0), (xb + w, y0), (xb + w + d, y1), (xb + d, y1)])


def text(f, s, cap, x, y, align="l", tracking=0.0, max_w=None):
    if max_w:
        cap = f.fit_cap(s, cap, max_w, tracking)
    return f.text(s, cap, x, y, align=align, tracking=tracking)


def wordmark(cap, x, y, gap=None):
    """UZAR + şimşek. Döner: (harfler, şimşek, sağ kenar)."""
    f = heavy()
    letters = f.text("UZAR", cap, x, y, align="l", tracking=cap * 0.04)
    x1 = letters.bounds()[2]
    g = cap * 0.12 if gap is None else gap
    b = U.bolt(cap * 1.15, 0, 0)
    bx0 = b.bounds()[0]
    b = b.translate((x1 + g - bx0, y))
    return letters, b, b.bounds()[2]


def labels(y, colour, left="TARA · BİZE ULAŞ", right="KAREKOD İLE ÖDE", cap=4.2, cx=None):
    f = bold()
    cx = cx or (-CX, CX)
    return [(text(f, left, cap, cx[0], y, "c", cap * 0.1, TILE), colour),
            (text(f, right, cap, cx[1], y, "c", cap * 0.1, TILE), colour)]


def phone_line(cap=4.0):
    return f"{INFO.phone}  ·  {INFO.city}"


# ---------------------------------------------------------------- tasarımlar

def d1_gece():
    """Siyah panel, sayfadaki gibi başlık: UZAR + şimşek, sağ üstte kırmızı eğik şeritler; altta iki QR."""
    c = Concept("1_gece", "Gece", "Sayfayla aynı görünüm: siyah zemin, beyaz UZAR, kırmızı şimşek ve eğik şeritler. "
                "Altta iki QR: sayfa ve banka karekodu.", "")
    reg = []
    for xb, w in ((13.5, 1.6), (20.0, 4.0), (30.0, 10.0)):
        reg.append((stripe(xb, w, 64.5, PH + 1) ^ outline(), RED))
    letters, b, _ = wordmark(19.0, -45.0, 90.5)
    reg += [(letters, WHITE), (b, RED)]
    reg.append((text(bold(), "OTO LASTİK", 5.6, -45.0, 75.2, tracking=1.9), RED))
    reg.append((text(bold(), phone_line(), 4.0, -45.0, 68.2, tracking=0.5), WHITE))
    for key, cx in (("sayfa", -CX), ("karekod", CX)):
        light, _, _ = tile(key, cx, 18.0 + TILE / 2)
        reg += [(light, WHITE), (brackets(cx, 18.0 + TILE / 2), RED)]
    reg += labels(12.4, WHITE)
    return c, outline(), reg, BLACK


def d2_beyaz():
    """Beyaz panel: siyah UZAR, kırmızı şimşek ve şeritler; altta siyah bant içinde beyaz etiketler."""
    c = Concept("2_beyaz", "Beyaz", "Beyaz zemin, siyah yazı, kırmızı şimşek ve şeritler; QR'lar beyaz gövde üstünde "
                "siyah kare. Altta siyah bantta etiketler.", "")
    reg = []
    for xb, w in ((13.5, 1.6), (20.0, 4.0), (30.0, 10.0)):
        reg.append((stripe(xb, w, 64.5, PH + 1) ^ outline(), RED))
    letters, b, _ = wordmark(19.0, -45.0, 90.5)
    reg += [(letters, BLACK), (b, RED)]
    reg.append((text(bold(), "OTO LASTİK", 5.6, -45.0, 75.2, tracking=1.9), RED))
    reg.append((text(bold(), phone_line(), 4.0, -45.0, 68.2, tracking=0.5), BLACK))
    for key, cx in (("sayfa", -CX), ("karekod", CX)):
        _, dark, _ = tile(key, cx, 19.0 + TILE / 2)
        reg += [(dark, BLACK), (brackets(cx, 19.0 + TILE / 2), RED)]
    band = A.rect(-60, -1, 60, 16.2) ^ outline()
    words = A.union(*[cs for cs, _ in labels(12.0, WHITE)])
    reg.append((band - words, BLACK))
    return c, outline(), reg, WHITE


def d3_kirmizi_baslik():
    """Kırmızı başlık bandı (alt kenarı eğik), içinde beyaz UZAR ve siyah şimşek; altta iki QR."""
    c = Concept("3_kirmizi_baslik", "Kırmızı başlık", "Üstte eğik kesilmiş kırmızı bant: beyaz UZAR, gövde renginde "
                "(siyah) şimşek. Altta beyaz karolarda iki QR.", "")
    reg = []
    band = A.polygon([(-60, 73.0), (60, 62.0), (60, 120), (-60, 120)]) ^ outline()
    letters, b, x1 = wordmark(19.0, -45.0, 93.5)
    reg.append((band - b, RED))
    reg += [(letters, WHITE), (text(bold(), "OTO LASTİK", 5.6, -45.0, 79.0, tracking=1.9), WHITE)]
    reg.append((text(bold(), INFO.phone, 4.4, 46.0, 69.6, "r", 0.5), WHITE))
    reg.append((text(bold(), INFO.city, 3.4, 46.0, 79.0, "r", 1.3), WHITE))
    for key, cx in (("sayfa", -CX), ("karekod", CX)):
        light, _, _ = tile(key, cx, 15.5 + TILE / 2)
        reg.append((light, WHITE))
    reg += labels(11.6, RED)
    return c, outline(), reg, BLACK


def d4_tek_qr():
    """Tek büyük QR (sayfa) ve yanında sayfada olanların listesi; altta IBAN yazılı. En sade, en ucuz."""
    c = Concept("4_tek_qr", "Tek QR", "Tek büyük QR: sayfayı açar (karekod sayfada). Yanında sayfada olanların "
                "listesi, altta alıcı ve IBAN yazılı.", "")
    c.uses = ("sayfa",)
    reg = []
    letters, b, _ = wordmark(15.5, -45.0, 94.5)
    reg += [(letters, WHITE), (b, RED)]
    reg.append((text(bold(), "OTO", 5.8, 46.0, 99.6, "r", 1.1), RED))
    reg.append((text(bold(), "LASTİK", 5.8, 46.0, 91.8, "r", 1.1), RED))
    reg.append((text(bold(), INFO.city, 3.4, 46.0, 84.2, "r", 1.25), WHITE))
    s = 54.0
    cx, cy = -45.0 + s / 2, 21.0 + s / 2
    light, _, _ = tile("sayfa", cx, cy, s, r=1.6)
    reg += [(light, WHITE), (brackets(cx, cy, s, 0.9, 1.0, 8.0), RED)]
    x0 = cx + s / 2 + 5.0
    reg.append((text(heavy(), "TARA", 9.0, x0, 70.0, tracking=0.5), WHITE))
    items = ["ARA", "WHATSAPP", "INSTAGRAM", "GOOGLE", "ÖDEME"]
    for i, it in enumerate(items):
        y = 59.0 - i * 8.4
        reg.append((A.polygon([(x0, y - 1.8), (x0 + 2.7, y), (x0, y + 1.8)]), RED))
        reg.append((text(bold(), it, 4.2, x0 + 4.4, y, tracking=0.35, max_w=46.0 - x0 - 4.4), WHITE))
    reg.append((text(bold(), f"{INFO.holder}  ·  {Q.iban_display(INFO.iban)}", 4.0, 0.5, 13.0, "c", 0.3, 91.0),
                WHITE))
    return c, outline(), reg, BLACK


DESIGNS = [d1_gece, d2_beyaz, d3_kirmizi_baslik, d4_tek_qr]


# ---------------------------------------------------------------- yapım, kontrol, çizim

def build(fn):
    c, out, reg, body = fn()
    flat = Y.inlaid_panel(out, reg, body, thickness=T)
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
    """Ön görünüş (düz, gölgesiz) – QR okuma için."""
    parts = [(*A.mesh_arrays(m), col) for m, col in c.flat]
    im = render(parts, size, rotation(0, -90), light=False, margin=0.03)
    bg = Image.new("RGB", im.size, (150, 152, 158))
    bg.paste(im, (0, 0), im)
    return bg


def qr_check(c):
    """Ön görünüşteki QR'ları okur; ayrıca 'hepsi birden' baskı / okutma benzetiminde."""
    im = front(c).convert("L")
    ppm = im.width * (1 - 2 * 0.03) / PH
    got = set(Q.decode(im))
    sim = Q.simulate(im, ppm, 0.9, **dict(Q.SIM_CASES)["hepsi birden"])
    got_sim = set(Q.decode(sim))
    return [(t, t in got, t in got_sim) for t in c.expected]


def thin(c, limit=0.8):
    """Renkli dolgularda `limit` mm'den ince kısım (%), renk başına."""
    out = {}
    for cs, col in c.regions:
        cs = cs ^ c.outline
        k = cs - cs.offset(-limit / 2, J).offset(limit / 2, J)
        a = sum(p.area() for p in k.decompose() if p.area() > 0.02)
        out[NAMES[col]] = out.get(NAMES[col], 0.0) + a
    total = {NAMES[col]: 0.0 for _, col in c.regions}
    for cs, col in c.regions:
        total[NAMES[col]] += (cs ^ c.outline).area()
    return {k: round(100 * v / total[k], 1) for k, v in out.items() if total[k] > 0}


def font_ui(size):
    return ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), size)


def sheet(c, i):
    parts = [(*A.mesh_arrays(m), col) for m, col in c.parts]
    views = [(None, "Ön yüz (100 × 108 mm)"), (rotation(-28, -68), "Tezgâhta, sehpada (3/4)"),
             (rotation(-90, -90), f"Yandan: {TILT:.0f}° eğik")]
    W, H = 1500, 760
    canvas = Image.new("RGB", (W, H), (236, 239, 244))
    dr = ImageDraw.Draw(canvas)
    boxes = [(30, 120, 640, 690), (660, 120, 1180, 690), (1200, 120, 1470, 690)]
    for (R, label), (x0, y0, x1, y1) in zip(views, boxes):
        dr.rounded_rectangle((x0, y0, x1, y1), 22, fill=(146, 153, 166))
        if R is None:
            im = front(c, 1200)
            im = A.fit_into(render([(*A.mesh_arrays(m), col) for m, col in c.flat], 1200, rotation(0, -90),
                                   flat=0.85, margin=0.02), x1 - x0 - 40, y1 - y0 - 60)
        else:
            im = A.fit_into(render(parts, 1100, R, margin=0.02), x1 - x0 - 30, y1 - y0 - 60)
        canvas.paste(im, (x0 + (x1 - x0 - im.width) // 2, y0 + 40 + (y1 - y0 - 40 - im.height) // 2), im)
        dr.text((x0 + 16, y0 + 10), label, fill=(236, 239, 244), font=font_ui(18))
    dr.text((30, 18), f"{i}. {c.title.upper()}", fill=(24, 26, 30), font=font_ui(32))
    dr.text((30, 62), c.desc, fill=(80, 86, 98), font=font_ui(19))
    total = sum(c.g.values())
    g = "  ·  ".join(f"{NAMES[k]} {v:.0f} g" for k, v in sorted(c.g.items(), key=lambda kv: -kv[1]))
    dr.text((30, 92), f"~{total:.0f} g filament ({g}; panel + sehpa)  ·  ~{total * 0.5:.0f} TL filament",
            fill=(22, 120, 60), font=font_ui(19))
    y = 706
    for content, ok, ok_sim in c.qr:
        label = "sayfa" if content == QRS["sayfa"].content else "banka karekodu"
        dr.text((30, y), f"QR {label}: " + ("okundu" if ok else "OKUNMADI") +
                (", baskı hatası benzetiminde de okundu" if ok_sim else ", benzetimde OKUNMADI"),
                fill=(22, 120, 60) if ok and ok_sim else (200, 30, 38), font=font_ui(17))
        y += 24
    canvas.save(os.path.join(OUT_DIR, c.key + ".png"))
    return canvas


def overview(cs, path):
    cw, ch, gap = 720, 560, 20
    W, H = 2 * cw + 3 * gap, 2 * ch + 3 * gap + 110
    canvas = Image.new("RGB", (W, H), (244, 245, 247))
    dr = ImageDraw.Draw(canvas)
    dr.text((24, 20), "UZAR OTO LASTİK – QR'LI TEZGÂH İSİMLİĞİ (~10 × 10 cm)", fill=(24, 26, 30), font=font_ui(34))
    dr.text((24, 66), "Sol QR: sayfa (ara · WhatsApp · Instagram · Google · IBAN)  ·  sağ QR: banka karekodu "
                      "(ENES UZAR, Yapı Kredi)  ·  hepsi görüntüden okundu", fill=(110, 114, 124), font=font_ui(19))
    for k, c in enumerate(cs):
        x, y = gap + (k % 2) * (cw + gap), 110 + gap + (k // 2) * (ch + gap)
        dr.rounded_rectangle((x, y, x + cw, y + ch), 24, fill=(226, 228, 232))
        f = A.fit_into(render([(*A.mesh_arrays(m), col) for m, col in c.flat], 1000, rotation(0, -90), flat=0.85,
                              margin=0.02), 330, 420)
        p = A.fit_into(render([(*A.mesh_arrays(m), col) for m, col in c.parts], 1000, rotation(-28, -68),
                              margin=0.02), 330, 420)
        canvas.paste(f, (x + 20 + (330 - f.width) // 2, y + 60 + (420 - f.height) // 2), f)
        canvas.paste(p, (x + 370 + (330 - p.width) // 2, y + 60 + (420 - p.height) // 2), p)
        dr.text((x + 20, y + 14), f"{k + 1}. {c.title}", fill=(30, 33, 40), font=font_ui(26))
        ok = all(a and b for _, a, b in c.qr)
        dr.text((x + 20, y + ch - 52), f"~{sum(c.g.values()):.0f} g  ·  ~{sum(c.g.values()) * 0.5:.0f} TL filament  ·  "
                                      + ("QR'lar okundu" if ok else "QR OKUNMADI"),
                fill=(22, 120, 60) if ok else (200, 30, 38), font=font_ui(19))
    canvas.save(path)


def main():
    only = sys.argv[1:]
    cs = []
    for i, fn in enumerate(DESIGNS, 1):
        c = build(fn)
        if only and not any(o in c.key for o in only):
            continue
        c.qr = qr_check(c)
        sheet(c, i)
        cs.append(c)
        bad = [k for k, (m, _) in enumerate(c.parts) if not str(m.status()).endswith("NoError") or m.volume() <= 0]
        mods = {k: Q.module_for(e, TILE) for k, e in QRS.items()}
        print(f"{c.key:18s} ~{sum(c.g.values()):4.0f} g  QR: {[(ok, sim) for _, ok, sim in c.qr]}  "
              f"0,8 mm'den ince (%): {thin(c)}  kare: {mods}  bozuk: {bad}")
    if not only:
        overview(cs, os.path.join(OUT_DIR, "hepsi.png"))


if __name__ == "__main__":
    main()
