"""SOYLU OTO LASTİK – QR'lı tezgâh isimliği önerileri (10): kurumsal, siyah zemin, beyaz ve kırmızı.

Önceki isimliklerden daha sade ve kurumsal: az ve düzenli öğe, ince kırmızı çizgiler, geniş harf aralıkları, simge
olarak yalnız monogram, lastik halkası ve rozet. Her tasarımda ayrı yerleşim ve yazı tipi: kırmızı çizgi (Manrope),
sol şerit (Sora), S monogramı (Michroma), geniş harf (Michroma), çerçeve (Sora), ortalı (Manrope), kırmızı başlık
(Manrope, oyma), lastik halkası (Oswald), rozet (Sora), alt bant (Archivo Black, oyma telefon).

Uzar, İNCE ve Çalık isimlikleriyle aynı yapı: 120 × 90 mm (4:3), köşeler R8, siyah gövde 1 cm, yazılar ve şekiller
2 mm kabartma, QR yüzeyle aynı hizada beyaz karo, 15° eğik sehpa. Küçük satırlar Outfit ExtraBold; her satırın en
dar harf içi boşluğu ölçülür, öğeler arası ≥ 2 mm.

QR: işletme sayfası (`soylu_isimlik/bilgiler.json` → `sayfa_url`, ortak hesapta `soyluotolastik` Worker'ı).
Telefon bilgiler.json'da boşsa yerinde "0 5XX XXX XX XX" görünür; numara yazılıp betik yeniden çalıştırılır.

Çıktı : soylu_isimlik/<tasarım>.png, musteri_1.png (1–6), musteri_2.png (7–10), musteri_katalog.pdf

Kullanım:
  python3 scripts/soylu_isimlik.py [anahtar ...]
"""
import json
import os
import sys

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import calik_isimlik as C  # noqa: E402
import ince_isimlik as N  # noqa: E402
import qr_sistemi as Q  # noqa: E402
import uzar_isimlik as I  # noqa: E402
import uzar_isimlik_baski as B  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "soylu_isimlik")
DATA = json.load(open(os.path.join(OUT_DIR, "bilgiler.json"), encoding="utf-8"))
PHONE = Q.phone_display(Q.phone_e164(DATA["telefon"])) if DATA.get("telefon") else "0 5XX XXX XX XX"
BLACK, WHITE, RED = A.BLACK, A.WHITE, A.RED
SHOW = {BLACK: (40, 40, 43), WHITE: (246, 246, 242), RED: (206, 28, 38)}
NAMES = {BLACK: "siyah", WHITE: "beyaz", RED: "kırmızı"}
J = m3.JoinType.Round
X0, X1 = -54.0, 54.0
N.FONT_FILES.update({"manrope": "Manrope-ExtraBold.ttf", "sora": "Sora-SemiBold.ttf", "michroma": "Michroma-Regular.ttf"})
t, bar, Design = N.t, N.bar, N.Design
SC = {"body": BLACK, "fg": WHITE, "dark": True}


def make_qr():
    import segno
    content = Q.https_url(DATA["sayfa_url"])
    natural = segno.make(content, error="m", micro=False).version
    q = segno.make(content, error="m", version=max(4, natural), micro=False, boost_error=True)
    return Q.Entry("sayfa", "TARA", content, "TARA", qr=q)


QR = make_qr()


def qr_block(cx, cy, s):
    _, dark, _ = Q.shapes(QR, Q.module_for(QR, s), cx, cy)
    return [(A.rrect(s, s, 1.6, cx, cy) - dark, WHITE)]


def scan(d, cx, cy, s, labels=True):
    """QR ve altında TARA (beyaz) / BİZE ULAŞIN (kırmızı)."""
    d.inlay += qr_block(cx, cy, s)
    if labels:
        y = cy - s / 2 - 4.6
        d.add("TARA", t("outfit", "TARA", 4.4, cx, y, "c", 1.2), WHITE)
        d.add("BİZE ULAŞIN", t("outfit", "BİZE ULAŞIN", 4.4, cx, y - 6.5, "c", 0.55), RED)   # harfler ≥ 0,6 mm ayrık


def phone_line(d, x, y, cap=5.2, align="l", icon=True, col=WHITE, max_w=62.0):
    """Telefon simgesi (kırmızı) ve numara."""
    if icon:
        ic = C.phone_icon(cap * 1.55, 0, 0).offset(0.35, J)          # ince yerleri kalınlaşsın
        b = ic.bounds()
        w_ic = b[2] - b[0]
        num = t("outfit", PHONE, cap, 0, 0, "l", 0.4, max_w - w_ic - 2.4)
        nb = num.bounds()
        total = w_ic + 2.4 + (nb[2] - nb[0])
        x0 = {"l": x, "c": x - total / 2, "r": x - total}[align]
        d.add(None, ic.translate((x0 - b[0], y)), RED)
        d.add("telefon", num.translate((x0 + w_ic + 2.4 - nb[0], y)), col)
    else:
        d.add("telefon", t("outfit", PHONE, cap, x, y, align, 0.4, max_w), col)


def diamond(cx, cy, r):
    return A.polygon([(cx, cy + r), (cx + r, cy), (cx, cy - r), (cx - r, cy)])


# ---------------------------------------------------------------- tasarımlar

def s1_cizgi():
    d = Design("1_kirmizi_cizgi", "Kırmızı çizgi", "Büyük SOYLU, altında ince kırmızı çizgi ve OTO LASTİK; sade ve kurumsal.",
               SC)
    d.add("SOYLU", t("manrope", "SOYLU", 15.0, X0, 72.0, "l", 1.0, 60.0), WHITE)
    d.add(None, A.rect(X0, 58.2, X0 + 30.0, 59.8), RED)
    d.add("OTO LASTİK", t("outfit", "OTO LASTİK", 5.0, X0, 50.0, "l", 1.8, 60.0), WHITE)
    d.add("HEMEN ARA", t("outfit", "HEMEN ARA", 4.4, X0, 31.0, "l", 1.0), RED)
    phone_line(d, X0, 20.5)
    scan(d, X1 - 19.0, 17.0 + 6.5 + 4.6 + 19.0, 38.0)
    return d


def s2_serit():
    d = Design("2_sol_serit", "Sol şerit", "Sol kenarda boydan kırmızı şerit; yanında SOYLU, OTO LASTİK ve telefon.", SC)
    d.add(None, A.rrect(4.0, 72.0, 1.6, X0 + 2.0, 48.0), RED)
    x0 = X0 + 9.0
    d.add("SOYLU", t("sora", "SOYLU", 13.0, x0, 73.0, "l", 0.9, 54.0), WHITE)
    d.add("OTO LASTİK", t("sora", "OTO LASTİK", 5.2, x0, 57.0, "l", 1.0, 54.0), RED)
    d.add(None, A.rect(x0, 47.4, x0 + 12.0, 49.0), WHITE)
    d.add("HEMEN ARA", t("outfit", "HEMEN ARA", 4.4, x0, 33.0, "l", 1.0), WHITE)
    phone_line(d, x0, 22.0, 5.0, max_w=52.0)
    scan(d, X1 - 19.0, 17.0 + 6.5 + 4.6 + 19.0, 38.0)
    return d


def monogram(cx, cy, s):
    """Kırmızı yuvarlak kare içinde oyma S (Michroma)."""
    S = t("michroma", "S", s * 0.56, 0, 0, "c").offset(0.15, J)
    b = S.bounds()
    S = S.translate((cx - (b[0] + b[2]) / 2, cy - (b[1] + b[3]) / 2))
    return A.rrect(s, s, s * 0.22, cx, cy) - S


def s3_monogram():
    d = Design("3_monogram", "S monogramı", "Solda QR; sağda kırmızı karede oyma S monogramı, geniş harfli SOYLU, ortalı.",
               SC)
    cx = 23.0
    d.add(None, monogram(cx, 76.0, 18.0), RED)
    d.add("SOYLU", t("michroma", "SOYLU", 7.6, cx, 57.0, "c", 0.4, 58.0).offset(0.1, J), WHITE)
    d.add("OTO LASTİK", t("outfit", "OTO LASTİK", 4.4, cx, 47.0, "c", 1.2, 58.0), RED)
    d.add("HEMEN ARA", t("outfit", "HEMEN ARA", 4.4, cx, 32.0, "c", 1.0), WHITE)
    phone_line(d, cx, 22.0, 5.0, align="c", max_w=58.0)
    scan(d, X0 + 19.0, 17.0 + 6.5 + 4.6 + 19.0, 38.0)
    return d


def s4_genis():
    d = Design("4_genis_harf", "Geniş harf", "Boydan boya geniş harfli SOYLU ve kırmızı çizgi; altta telefon ve QR.", SC)
    d.add("SOYLU", t("michroma", "SOYLU", 12.0, 0, 76.0, "c", 1.0, X1 - X0).offset(0.1, J), WHITE)
    d.add(None, A.rect(X0, 64.1, X1, 65.7), RED)
    d.add("OTO LASTİK", t("outfit", "OTO LASTİK", 5.2, X0, 54.0, "l", 2.2, 62.0), WHITE)
    d.add("HEMEN ARA", t("outfit", "HEMEN ARA", 4.4, X0, 33.0, "l", 1.0), RED)
    phone_line(d, X0, 22.0, 5.2)
    s = 34.0
    scan(d, X1 - s / 2, 17.0 + 6.5 + 4.6 + s / 2, s)
    return d


def s5_cerceve():
    d = Design("5_cerceve", "Çerçeve", "İnce beyaz çerçeve, iki köşesinde kırmızı köşebent; içinde düzenli yerleşim.", SC)
    frame = A.rrect(108.0, 74.0, 5.0, 0, 49.5)
    d.add(None, frame - frame.offset(-1.4, J), WHITE)
    L, w = 15.0, 2.6
    x0, y0, x1, y1 = -54.0, 12.5, 54.0, 86.5
    tl = A.rect(x0, y1 - w, x0 + L, y1) + A.rect(x0, y1 - L, x0 + w, y1)
    br = A.rect(x1 - L, y0, x1, y0 + w) + A.rect(x1 - w, y0, x1, y0 + L)
    d.add(None, (tl + br) ^ frame, RED)
    xl = -47.0
    d.add("SOYLU", t("sora", "SOYLU", 12.0, xl, 71.0, "l", 0.9, 50.0), WHITE)
    d.add("OTO LASTİK", t("outfit", "OTO LASTİK", 4.6, xl, 57.5, "l", 1.4, 50.0), RED)
    d.add("HEMEN ARA", t("outfit", "HEMEN ARA", 4.2, xl, 34.0, "l", 1.0), WHITE)
    phone_line(d, xl, 24.0, 5.0, max_w=54.0)
    s, cx = 34.0, 29.0
    scan(d, cx, 52.0, s, labels=False)
    d.add("TARA", t("outfit", "TARA", 4.4, cx, 52.0 - s / 2 - 5.0, "c", 1.4), WHITE)
    return d


def s6_ortali():
    d = Design("6_ortali", "Ortalı", "Her şey ortada: SOYLU, iki yanında kırmızı elmas OTO LASTİK, altta QR.", SC)
    d.add("SOYLU", t("manrope", "SOYLU", 13.0, 0, 77.0, "c", 1.4, 80.0), WHITE)
    ol = d.add("OTO LASTİK", t("outfit", "OTO LASTİK", 4.8, 0, 64.0, "c", 1.6, 60.0), WHITE)
    b = ol.bounds()
    d.add(None, (diamond(b[0] - 5.0, 64.0, 2.1) + diamond(b[2] + 5.0, 64.0, 2.1)).offset(-0.4, J).offset(0.4, J), RED)
    s = 34.0
    scan(d, 0, 13.0 + s / 2, s, labels=False)
    d.add("TARA", t("outfit", "TARA", 4.6, -41.0, 30.0, "c", 1.2), WHITE)
    d.add(None, N.arrow(-26.0, 30.0, 6.0).offset(-0.4, J).offset(0.4, J), RED)
    d.add("BİZE", t("outfit", "BİZE", 4.6, 36.0, 33.5, "c", 0.8), RED)
    d.add("ULAŞIN", t("outfit", "ULAŞIN", 4.6, 36.0, 26.5, "c", 0.6), RED)
    phone_line(d, 0, 53.0, 5.0, align="c")
    return d


def s7_baslik():
    d = Design("7_kirmizi_baslik", "Kırmızı başlık", "Üstte kırmızı başlık bandı, içinde oyma SOYLU; altta telefon ve QR.", SC)
    band = A.rrect(X1 - X0, 21.0, 3.0, 0, 75.0)
    cut = A.union(t("manrope", "SOYLU", 11.0, X0 + 6.0, 75.0, "l", 1.2, 50.0),
                  t("outfit", "OTO LASTİK", 4.6, X1 - 6.0, 75.0, "r", 1.2, 40.0))
    d.add("başlık", band - cut, RED)
    d.add("HEMEN ARA", t("outfit", "HEMEN ARA", 4.6, X0, 42.0, "l", 1.0), RED)
    phone_line(d, X0, 31.0, 5.4)
    s = 34.0
    scan(d, X1 - s / 2, 42.0, s)
    return d


def tire_ring(cx, cy, R):
    """Sade jant: beyaz lastik halkası, kırmızı jant (5 bijon deliği ve göbek)."""
    return [(cs, RED if col == A.YELLOW else col) for cs, col in C.wheel(cx, cy, R)]


def s8_lastik():
    d = Design("8_jant", "Jant", "Sade jant simgesi (beyaz lastik, kırmızı jant); yanında uzun, dar SOYLU.", SC)
    for cs, col in tire_ring(X0 + 12.0, 71.0, 12.0):
        d.add(None, cs, col)
    x0 = X0 + 28.0
    d.add("SOYLU", t("oswald", "SOYLU", 15.0, x0, 74.0, "l", 1.6, 34.0), WHITE)
    d.add("OTO LASTİK", t("outfit", "OTO LASTİK", 4.4, x0, 59.0, "l", 0.4, 37.0), RED)
    d.add("HEMEN ARA", t("outfit", "HEMEN ARA", 4.4, X0, 33.0, "l", 1.0), RED)
    phone_line(d, X0, 22.0, 5.2)
    scan(d, X1 - 19.0, 17.0 + 6.5 + 4.6 + 19.0, 38.0)
    return d


def s9_rozet():
    d = Design("9_rozet", "Rozet", "Solda kırmızı halkalı rozet: ortada SOYLU, alt yayda OTO LASTİK.", SC)
    cx, cy, R = -31.0, 60.0, 23.0
    d.add(None, A.circle(R, cx, cy, 160) - A.circle(R - 2.4, cx, cy, 160), RED)
    d.add("SOYLU", t("sora", "SOYLU", 8.0, cx, cy + 3.0, "c", 0.6, 30.0), WHITE)
    d.add(None, A.rect(cx - 7.0, cy - 4.3, cx + 7.0, cy - 2.7), RED)
    arc = N.font("outfit").arc("OTO LASTİK", 4.2, cx, cy, R - 4.6, -90.0, top=False, tracking=0.9)
    d.add("OTO LASTİK", B.loosen_dots(arc), WHITE)
    d.add(None, diamond(cx, cy + R - 6.0, 1.6), WHITE)
    phone_line(d, X0, 23.0, 5.0, max_w=52.0)
    scan(d, X1 - 19.0, 17.0 + 6.5 + 4.6 + 19.0, 38.0)
    return d


def s10_alt_bant():
    d = Design("10_alt_bant", "Alt bant", "Üstte iri SOYLU; altta kırmızı bant içinde oyma telefon.", SC)
    d.add("SOYLU", t("archivo", "SOYLU", 13.0, X0, 74.0, "l", 0.6, 58.0), WHITE)
    d.add("OTO LASTİK", t("outfit", "OTO LASTİK", 4.8, X0, 59.0, "l", 1.6, 58.0), RED)
    d.add(None, A.rect(X0, 50.4, X0 + 14.0, 52.0), WHITE)
    band = A.rrect(X1 - X0, 14.0, 3.0, 0, 19.5)
    ic = C.phone_icon(8.0, X0 + 9.0, 19.5).offset(0.25, J)
    num = t("outfit", PHONE, 5.6, X0 + 16.0, 19.5, "l", 0.5, 60.0)
    d.add("bant", band - ic - num, RED)
    d.add("HEMEN ARA", t("outfit", "HEMEN ARA", 4.4, X0, 36.0, "l", 1.0), WHITE)
    s = 34.0
    scan(d, X1 - s / 2, 31.0 + 6.5 + 4.6 + s / 2 - 4.0, s, labels=False)
    d.add("TARA", t("outfit", "TARA", 4.2, X1 - s / 2, 33.4, "c", 1.2), WHITE)
    return d


DESIGNS = [s1_cizgi, s2_serit, s3_monogram, s4_genis, s5_cerceve, s6_ortali, s7_baslik, s8_lastik, s9_rozet,
           s10_alt_bant]


# ---------------------------------------------------------------- katılar, kontrol, çizim

def solids(d):
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
    return [("Panel (siyah)", body, BLACK)] + parts


def build(fn):
    d = fn()
    d.parts = solids(d)
    d.stand, (z0, y0) = B.stand()
    d.shown = B.assembled(d.parts, z0, y0) + [("Sehpa", d.stand, BLACK)]
    return d


def mesh(parts):
    return [(*A.mesh_arrays(m), SHOW[c]) for _, m, c in parts]


def qr_check(d):
    im = render(mesh(d.parts), 1600, A.R_TOP, light=False, margin=0.03)
    bg = Image.new("RGB", im.size, (150, 152, 158))
    bg.paste(im, (0, 0), im)
    im = bg.convert("L")
    ppm = im.width * (1 - 2 * 0.03) / I.PW
    sim = Q.simulate(im, ppm, 1.0, **dict(Q.SIM_CASES)["hepsi birden"])
    return QR.content in Q.decode(im), QR.content in Q.decode(sim)


def font_ui(n):
    return ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), n)


def sheet(d, i):
    W, H = 1500, 700
    canvas = Image.new("RGB", (W, H), (236, 239, 244))
    dr = ImageDraw.Draw(canvas)
    views = [(rotation(0, -90), "Önden, sehpada (120 × 90 mm)", 0.85), (rotation(-28, -68), "Tezgâhta (3/4)", None),
             (rotation(-90, -90), "Yandan: 15° eğik", None)]
    boxes = [(30, 130, 700, 630), (720, 130, 1240, 630), (1260, 130, 1470, 630)]
    parts = mesh(d.shown)
    for (R, label, flat), (x0, y0, x1, y1) in zip(views, boxes):
        dr.rounded_rectangle((x0, y0, x1, y1), 22, fill=(146, 153, 166))
        im = A.fit_into(render(parts, 1200, R, flat=flat, margin=0.02), x1 - x0 - 40, y1 - y0 - 60)
        canvas.paste(im, (x0 + (x1 - x0 - im.width) // 2, y0 + 40 + (y1 - y0 - 40 - im.height) // 2), im)
        dr.text((x0 + 16, y0 + 10), label, fill=(236, 239, 244), font=font_ui(18))
    dr.text((30, 18), f"{i}. {d.title.upper()}", fill=(24, 26, 30), font=font_ui(32))
    dr.text((30, 62), d.desc, fill=(80, 86, 98), font=font_ui(19))
    worst = min((v[0] for v in d.metrics.values()), default=9)
    dr.text((30, 94), f"Gövde 1 cm, kabartma 2 mm · en dar harf içi boşluk {worst:.2f} mm · QR "
                      f"{'okundu' if d.qr[0] else 'OKUNMADI'}{', benzetimde de' if d.qr[1] else ''}",
            fill=(22, 120, 60) if d.qr[0] and worst >= 0.6 else (200, 30, 38), font=font_ui(19))
    canvas.save(os.path.join(OUT_DIR, d.key + ".png"))


def header(im, dr, W, page):
    """Siyah başlık: SOYLU (Manrope), kırmızı OTO LASTİK, altında ince kırmızı çizgi."""
    big = ImageFont.truetype(os.path.join(A.FONT_DIR, "Manrope-ExtraBold.ttf"), 100)
    mid = ImageFont.truetype(os.path.join(A.FONT_DIR, "Manrope-ExtraBold.ttf"), 34)
    red = SHOW[RED]
    dr.rectangle((0, 0, W, 250), fill=(14, 14, 16))
    dr.rectangle((W - 360, 0, W, 250), fill=(22, 22, 25))
    dr.rectangle((W - 360, 0, W - 352, 250), fill=red)
    dr.text((70, 34), "SOYLU", font=big, fill=(244, 244, 242))
    x = 76 + dr.textlength("SOYLU", font=big) + 26
    dr.text((x, 64), "OTO LASTİK", font=mid, fill=red)
    dr.text((70, 178), "QR'lı tezgâh isimliği · tasarım önerileri", font=font_ui(30), fill=(210, 210, 214))
    dr.text((W - 180 - dr.textlength(f"{page}/2", font=font_ui(40)) / 2, 100), f"{page}/2", font=font_ui(40),
            fill=(200, 200, 206))
    dr.rectangle((0, 246, W, 254), fill=red)


def catalog(ds):
    """Müşteriye: musteri_1.png (1–6), musteri_2.png (7–10), musteri_katalog.pdf."""
    W, H = 1654, 2339
    f = font_ui
    ink, muted, paper, red = (20, 20, 22), (96, 98, 106), (245, 245, 243), SHOW[RED]
    pages = []
    for p, group in enumerate([ds[:6], ds[6:]]):
        im = Image.new("RGB", (W, H), paper)
        dr = ImageDraw.Draw(im)
        header(im, dr, W, p + 1)
        y = 285
        for line in ("QR: telefonla okutunca işletmenin sayfası açılır (arama, WhatsApp, konum, yorum).",
                     "Hepsi siyah zemin, beyaz ve kırmızı kabartma yazı; her birinde ayrı yerleşim ve yazı tipi."):
            dr.text((70, y), line, font=f(27), fill=ink)
            y += 40
        top, gap, cw = 395, 50, (W - 3 * 60) // 2
        ch = (H - top - 190 - 2 * gap) // 3
        for k, d in enumerate(group):
            x0, y0 = 60 + (k % 2) * (cw + 60), top + (k // 2) * (ch + gap)
            dr.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 28, fill=(255, 255, 255), outline=(226, 226, 230))
            n = ds.index(d) + 1
            dr.ellipse((x0 + 26, y0 + 24, x0 + 86, y0 + 84), fill=(16, 16, 18))
            dr.text((x0 + 56 - dr.textlength(str(n), font=f(34)) / 2, y0 + 34), str(n), font=f(34), fill=red)
            dr.text((x0 + 104, y0 + 30), d.title, font=f(38), fill=ink)
            img = A.fit_into(render(mesh(d.shown), 1300, rotation(0, -90), flat=0.85, margin=0.02), cw - 70, ch - 190)
            im.paste(img, (x0 + (cw - img.width) // 2, y0 + 100 + (ch - 190 - img.height) // 2), img)
            ty = y0 + ch - 78
            for line in N.wrap(dr, d.desc, f(26), cw - 60)[:2]:
                dr.text((x0 + 30, ty), line, font=f(26), fill=muted)
                ty += 34
        if p == 1:
            y0, y1 = top + 2 * (ch + gap), H - 190
            dr.rounded_rectangle((60, y0, W - 60, y1), 28, fill=(255, 255, 255), outline=(226, 226, 230))
            dr.text((100, y0 + 40), "Ürün", font=f(38), fill=ink)
            ty = y0 + 110
            for line in ("Ölçü 12 × 9 cm, gövde 1 cm kalınlığında, köşeler yuvarlak",
                         "Yazılar ve şekiller 2 mm kabartma; QR düz ve keskin",
                         "Tezgâh sehpası dahil, panel 15° eğik durur",
                         "QR işletme sayfasını açar"):
                dr.ellipse((100, ty + 10, 114, ty + 24), fill=red)
                dr.text((130, ty), line, font=f(30), fill=muted)
                ty += 56
            img = A.fit_into(render(mesh(ds[0].shown), 1200, rotation(-28, -68), margin=0.02), 520, y1 - y0 - 60)
            im.paste(img, (W - 100 - img.width, y0 + (y1 - y0 - img.height) // 2), img)
        foot = ("Beğendiğiniz tasarımın numarasını yazmanız yeterli." if p == 1 else
                "Ölçü 12 × 9 cm · 1 cm kalın · kabartma yazı · tezgâh sehpası dahil")
        dr.rounded_rectangle((60, H - 150, W - 60, H - 70), 22, fill=(16, 16, 18))
        dr.text((W / 2 - dr.textlength(foot, font=f(30)) / 2, H - 128), foot, font=f(30), fill=(244, 244, 242))
        im.save(os.path.join(OUT_DIR, f"musteri_{p + 1}.png"), optimize=True)
        im.convert("RGB").save(os.path.join(OUT_DIR, f"musteri_{p + 1}.jpg"), "JPEG", quality=90, optimize=True)
        pages.append(im)
    pages[0].save(os.path.join(OUT_DIR, "musteri_katalog.pdf"), save_all=True, append_images=pages[1:],
                  resolution=200)


def check(i):
    """i. tasarım (ayrı süreçte): ölçümler, QR okuma, ayrıntı sayfası. Döner satır."""
    d = build(DESIGNS[i - 1])
    d.metrics = {k: B.line_metrics(cs) for k, cs in d.lines.items()}
    d.qr = qr_check(d)
    sheet(d, i)
    bad = {k: v for k, v in d.metrics.items() if v[0] < 0.6 or v[2] > 6.0}
    return (f"{d.key:18s} QR {d.qr}  simgelerde 1,2 mm'den ince %{C.thin_shapes(d)}  dar/ince satırlar: {bad or 'yok'}"
            f"  sıkışık: {C.crowded(d) or 'yok'}")


def main():
    from multiprocessing import Pool
    os.makedirs(OUT_DIR, exist_ok=True)
    if not DATA.get("telefon"):
        print("Not: telefon bilgiler.json'da boş; tasarımlarda yer tutucu (0 5XX XXX XX XX) var.")
    only = sys.argv[1:]
    if only == ["katalog"]:
        catalog([build(fn) for fn in DESIGNS])
        return
    todo = [i for i, fn in enumerate(DESIGNS, 1) if not only or any(o in fn.__name__ for o in only)]
    with Pool(4) as pool:
        for line in pool.map(check, todo):
            print(line)
    if not only:
        catalog([build(fn) for fn in DESIGNS])


if __name__ == "__main__":
    main()
