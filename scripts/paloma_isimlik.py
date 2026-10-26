"""PALOMA GRIDA – Süleyman Boylu (Satın Alma Müdürü) için QR'lı masa isimliği önerileri, 2. tur.

Beş düzen, her biri iki renkte: beyaz tabla (siyah ve mavi yazı) ve siyah tabla (beyaz ve mavi detay); 10 öneri.
İsimlikte otelin logosu (PALOMA HOTELS), ad soyad, görev ve otel (Paloma Grida) yazar; telefonlar, e-posta ve adres
QR'ın açtığı kartvizit sayfasındadır (scripts/paloma_sayfa.py).

İlk turdan farklar:
  * Gerçek logo: Instagram profilindeki logodan vektöre çevrildi (scripts/paloma_logo.py). Mavi, logonun mavisi.
  * Yazılar ve logo kabartma değil, yüzeyle aynı hizada renkli dolgu (0,8 mm): baskı gibi düz ve net, gölge yok;
    logodaki ince HOTELS harfleri de basılabiliyor.
  * Ad soyad büyük-küçük harf (Montserrat SemiBold ya da Lora Bold), görev ve otel daha küçük ve sakin; az öğe.
  * QR 3. sürüm (29 × 29): aynı alanda daha iri kareler.

Basılabilirlik (0,4 nozul, düz dolgu): çizgiler ≥ 0,5 mm, harf içleri ve aralar ≥ 0,4 mm, öğeler arası ≥ 2 mm.

Çıktı : paloma_isimlik/<tasarım>.png, musteri_1..3.png/.jpg (öneriler), musteri_4 (sayfa), musteri_katalog.pdf

Kullanım:
  python3 scripts/paloma_isimlik.py [anahtar ...]      # anahtar: tasarım adından bir parça (ör. bant)
  python3 scripts/paloma_isimlik.py katalog            # yalnız katalog
"""
import json
import os
import sys

import manifold3d as m3
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import ince_isimlik as N  # noqa: E402
import paloma_logo as L  # noqa: E402
import qr_sistemi as Q  # noqa: E402
import uzar_isimlik as I  # noqa: E402
import uzar_isimlik_baski as B  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "paloma_isimlik")
DATA = json.load(open(os.path.join(OUT_DIR, "bilgiler.json"), encoding="utf-8"))
LOGO = json.load(open(os.path.join(OUT_DIR, "logo", "paloma_hotels.json"), encoding="utf-8"))
BLACK, WHITE, BLUE = A.BLACK, A.WHITE, A.BLUE
PALOMA_BLUE = (105, 161, 186)                                   # logonun mavisi (#69A1BA)
SHOW = {BLACK: (34, 35, 39), WHITE: (246, 246, 243), BLUE: PALOMA_BLUE}
NAMES = {BLACK: "siyah", WHITE: "beyaz", BLUE: "mavi"}
J = m3.JoinType.Round
X0, X1 = -52.0, 52.0                                            # yan boşluklar 8 mm
TOP, BOTTOM = 83.0, 12.0                                        # üst boşluk 7 mm; altta sehpa (~9,5 mm) örter
MIN_LINE, MIN_GAP = 0.5, 0.4
N.FONT_FILES.update({"ms6": "Montserrat_600SemiBold.ttf", "ms7": "Montserrat_700Bold.ttf",
                     "lora": "Lora_700Bold.ttf"})
WHITE_SC = {"key": "beyaz", "body": WHITE, "fg": BLACK, "logo": BLUE, "dark": False}
BLACK_SC = {"key": "siyah", "body": BLACK, "fg": WHITE, "logo": WHITE, "dark": True}


def tr_upper(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


FIRST, LAST = DATA["isim"].split()
NAME = DATA["isim"]
TITLE = DATA["gorev"]                                           # Satın Alma Müdürü
TITLE_CAPS = tr_upper(TITLE)
HOTEL = DATA["otel"]                                            # Paloma Grida
GRIDA = HOTEL.split()[-1].upper()                               # marka adı: GRIDA (noktasız I)
HOTEL_CAPS = HOTEL.upper()                                      # PALOMA GRIDA


def make_qr():
    """Sondaki / olmadan adres 42 bayt: 3. sürüm M (29 × 29) sığar; tarayıcılar / ekler."""
    import segno
    content = Q.https_url(DATA["sayfa_url"]).rstrip("/")
    q = segno.make(content, error="m", micro=False, boost_error=True)
    return Q.Entry("sayfa", "KARTVİZİT", content, "KARTVİZİT", qr=q)


QR = make_qr()


# ---------------------------------------------------------------- tasarım ve öğeler

class Design:
    """Bütün öğeler düz dolgu (yüzeyle aynı hizada). `lines`: ölçülen ve aralığı denetlenen adlı öğeler."""

    def __init__(self, key, title, desc, sc):
        self.key, self.title, self.desc, self.sc = key, title, desc, sc
        self.inlay, self.lines = [], {}

    def add(self, name, cs, colour):
        if colour != self.sc["body"]:                           # gövde renginde öğe: dolgu yok, yalnız boşluk
            self.inlay.append((cs, colour))
        if name:
            self.lines[name] = cs
        return cs


def t(font, s, cap, x, y, align="l", tr=0.0, max_w=None):
    """Yazı; y büyük harflerin ortası. (B.loosen_dots küçük yazıda I'yı da nokta sanıp incelttiği için
    kullanılmaz; noktalar küçültülmez, biraz yukarı alınır.)"""
    cs = I.text(N.font(font), s, cap, x, y, align, tr, max_w)
    out = []
    for p in cs.decompose():                    # İ / Ü noktaları 0,15 mm yukarı: harfle arası ≥ 0,4 mm
        b = p.bounds()
        w, h = b[2] - b[0], b[3] - b[1]
        dot = p.area() < 2.5 and w * h > 0 and p.area() / (w * h) > 0.6 and 0.6 < w / h < 1.7 and b[1] > y
        out.append(p.translate((0.0, 0.15)) if dot else p)
    return A.union(*out)


def logo(x, y_top, w, align="l"):
    """PALOMA HOTELS logosu, genişlik w mm, üst kenarı y_top. HOTELS'in ince çizgileri (dikeyler genişliğin ~%1,1'i,
    yataylar ~%0,85'i) en az 0,56 mm'ye kalınlaştırılır. Döner: (çokgen, alt kenarın y'si)."""
    rows = []
    for k in ("paloma", "hotels"):
        cs = m3.CrossSection(LOGO[k], m3.FillRule.EvenOdd).scale((w, w))
        if k == "hotels":
            off = max(0.0, (0.56 - 0.0085 * w) / 2)
            cs = cs.offset(off, J) if off > 0.005 else cs
        rows.append(cs)
    cs = rows[0] + rows[1]
    b = cs.bounds()
    dx = {"l": x - b[0], "c": x - (b[0] + b[2]) / 2, "r": x - b[2]}[align]
    cs = cs.translate((dx, y_top - b[3]))
    return cs, cs.bounds()[1]


def qr(d, cx, cy, s):
    """QR karo (sessiz bölge dahil) s mm. Beyaz tablada siyah kareler, siyah tablada beyaz karo (kareler gövde
    rengi). Döner: karo (altındaki renkli alandan çıkarılsın)."""
    _, dark, _ = Q.shapes(QR, Q.module_for(QR, s), cx, cy)
    tile = A.rrect(s, s, 1.4, cx, cy)
    if d.sc["dark"]:
        d.inlay.append((tile - dark, WHITE))
    else:
        d.inlay.append((dark ^ tile, BLACK))
    d.lines["QR"] = tile
    return tile


def caption(d, text, cap, x, y, align="c", col=None, tr=1.2, max_w=None):
    return d.add(text, t("ms7", text, cap, x, y, align, tr, max_w), d.sc["fg"] if col is None else col)


def name_lines(d, font, cap, x, y_top, align="l", lead=1.62, col=None, max_w=None):
    """Ad ve soyad alt alta (y_top: ilk satırın büyük harf üstü). Döner: soyadın taban çizgisi."""
    col = d.sc["fg"] if col is None else col
    y1 = y_top - cap
    d.add("ad", t(font, FIRST, cap, x, y1, align, 0.0, max_w), col)
    y2 = y1 - cap * lead
    d.add("soyad", t(font, LAST, cap, x, y2, align, 0.0, max_w), col)
    return y2


def lockup(x, y_top, w, align="l", gap=4.2, cap=4.0, tr=2.4):
    """Logo | GRIDA: logonun yanında ince dikey çizgi ve otelin adı (logonun ortasına hizalı).
    Döner: (logo, çizgi, GRIDA)."""
    lg, yb = logo(0.0, y_top, w)
    mid, h = (y_top + yb) / 2, y_top - yb
    bar = vrule(w + gap, mid - h * 0.42, mid + h * 0.42, 0.6)
    gr = t("ms6", GRIDA, cap, w + 2 * gap + 0.3, mid - cap / 2, "l", tr)
    total = gr.bounds()[2]
    dx = {"l": x, "c": x - total / 2, "r": x - total}[align]
    return lg.translate((dx, 0.0)), bar.translate((dx, 0.0)), gr.translate((dx, 0.0))


def rule(x0, x1, y, w=0.7):
    return A.rect(x0, y - w / 2, x1, y + w / 2)


def vrule(x, y0, y1, w=0.7):
    return A.rect(x - w / 2, y0, x + w / 2, y1)


# ---------------------------------------------------------------- beş düzen

def m1_sutun(sc):
    """Solda logo, iki satır ad soyad, görev ve otel; ince mavi dikey çizgi; sağda QR."""
    d = Design(f"{sc['key']}_1_sutun", "Sütun", "Solda logo, iki satır ad soyad, görev ve otel; ince mavi dikey "
               "çizgiyle ayrılmış sağ sütunda QR.", sc)
    lg, _ = logo(X0, TOP, 42.0)
    d.add("logo", lg, sc["logo"])
    y = name_lines(d, "ms6", 7.4, X0, 56.0)
    d.add("görev", t("ms6", TITLE, 4.2, X0, y - 11.0, "l", 0.1), BLUE)
    d.add("otel", t("ms6", HOTEL, 4.2, X0, y - 18.6, "l", 0.1), sc["fg"])
    d.add(None, vrule(13.0, 18.0, 78.0), BLUE)
    tile = qr(d, 33.5, 47.5, 31.0)
    caption(d, "KARTVİZİT", 3.0, 33.5, tile.bounds()[1] - 6.6)
    return d


def m2_genis(sc):
    """Üstte boydan tek satır ad soyad ve görev; ince mavi çizgi; altta logo ve QR."""
    d = Design(f"{sc['key']}_2_genis", "Geniş isim", "Üstte boydan tek satır ad soyad ve görev; ince mavi çizgi; "
               "altta solda logo | GRIDA, sağda QR.", sc)
    d.add("ad soyad", t("ms6", NAME, 7.2, X0, TOP - 7.6, "l", 0.0, X1 - X0), sc["fg"])
    d.add("görev", t("ms6", TITLE_CAPS, 3.6, X0, 63.4, "l", 1.1, X1 - X0), BLUE)
    d.add(None, rule(X0, X1, 54.0), BLUE)
    lg, bar, gr = lockup(X0, 37.4, 34.0, cap=3.8, tr=2.2)
    d.add("logo", lg, sc["logo"])
    d.add(None, bar, BLUE)
    d.add("GRIDA", gr, sc["fg"])
    qr(d, X1 - 15.0, 29.0, 30.0)
    caption(d, "KARTVİZİT", 3.0, X1 - 15.0, 47.8)
    return d


def m3_mavi_kart(sc):
    """Sağda içe çekik mavi kart, içinde QR ve KARTVİZİT; solda logo, ad soyad (Lora), görev ve otel."""
    d = Design(f"{sc['key']}_3_mavi_kart", "Mavi kart", "Sağda içe çekik mavi kart, içinde beyaz QR; solda logo, "
               "iki satır ad soyad (Lora), görev ve otel.", sc)
    card = A.rrect(38.0, 73.0, 4.0, 37.0, 49.5)                 # x 18..56, y 13..86: sehpanın üstünde biter
    tile = qr(d, 37.0, 54.5, 30.0)
    cap = t("ms7", "KARTVİZİT", 3.0, 37.0, tile.bounds()[1] - 7.0, "c", 1.2)
    d.lines["KARTVİZİT"] = cap
    if sc["dark"]:
        d.inlay.append((cap, WHITE))
    d.add(None, card - tile.offset(0.0, J) - cap.offset(0.0, J), BLUE)
    lg, _ = logo(X0, TOP, 40.0)
    d.add("logo", lg, sc["logo"])
    y = name_lines(d, "lora", 7.6, X0, 56.0, lead=1.58)
    d.add("görev", t("ms6", TITLE, 4.2, X0, y - 10.8, "l", 0.1, 64.0), BLUE)
    d.add("otel", t("ms6", HOTEL, 4.2, X0, y - 18.4, "l", 0.1, 64.0), sc["fg"])
    return d


def m4_ust_bant(sc):
    """Üstte boydan mavi bant: içinde beyaz logo ve GRIDA (Instagram'daki gibi); altta ad soyad, görev, QR."""
    d = Design(f"{sc['key']}_4_ust_bant", "Üst bant", "Üstte boydan mavi bant, içinde beyaz logo ve GRIDA; altında iki "
               "satır ad soyad ve görev, sağda QR.", sc)
    band = A.rrect(112.0, 25.0, 4.0, 0.0, 73.5)                 # x −56..56, y 61..86
    lg, _ = logo(-50.0, 73.5 + 7.05, 44.0)
    gr = t("ms6", GRIDA, 4.2, 50.0, 73.5 - 2.1, "r", 2.4)
    bar = vrule(9.0, 67.5, 79.5, 0.6)
    white = lg + gr + bar
    d.lines["logo"], d.lines["GRIDA"] = lg, gr
    d.add(None, band - white.offset(0.0, J), BLUE)
    if sc["dark"]:
        d.inlay.append((white, WHITE))
    y = name_lines(d, "ms6", 7.0, X0, 53.0)
    d.add("görev", t("ms6", TITLE, 4.2, X0, y - 10.4, "l", 0.1), BLUE)
    tile = qr(d, X1 - 15.0, 39.0, 30.0)
    caption(d, "KARTVİZİT", 3.0, X1 - 15.0, tile.bounds()[1] - 6.4)
    return d


def m5_ortali(sc):
    """Ortalı: logo | GRIDA, ad soyad (Lora), kısa mavi çizgi, görev; altta ortada QR, iki yanında DİJİTAL KARTVİZİT."""
    d = Design(f"{sc['key']}_5_ortali", "Ortalı", "Her şey ortada: logo | GRIDA, tek satır ad soyad (Lora), kısa mavi "
               "çizgi ve görev; altta QR, iki yanında DİJİTAL · KARTVİZİT.", sc)
    lg, bar, gr = lockup(0.0, TOP + 0.5, 34.0, "c", cap=3.8, tr=2.2)
    d.add("logo", lg, sc["logo"])
    d.add(None, bar, BLUE)
    d.add("GRIDA", gr, sc["fg"])
    yb = lg.bounds()[1]
    d.add("ad soyad", t("lora", NAME, 6.8, 0.0, yb - 11.0, "c", 0.1, X1 - X0), sc["fg"])
    d.add("çizgi", rule(-6.0, 6.0, yb - 19.6), BLUE)
    d.add("görev", t("ms6", TITLE_CAPS, 3.4, 0.0, yb - 24.8, "c", 1.0, X1 - X0), BLUE)
    qr(d, 0.0, 26.5, 30.0)
    caption(d, "DİJİTAL", 3.0, -20.0, 25.0, "r")
    caption(d, "KARTVİZİT", 3.0, 20.0, 25.0, "l")
    return d


def secilen(sc=WHITE_SC):
    """Müşterinin seçtiği: 3 · Mavi kart (beyaz tabla), PALOMA HOTELS logosu ve GRIDA mavi kartın içinde; solda
    yalnız ad soyad ve görev (ayrıca "Paloma Grida" satırı yok)."""
    d = Design(f"{sc['key']}_3_mavi_kart_logolu", "Mavi kart (logo kartta)", "Sağda mavi kart: içinde beyaz PALOMA "
               "HOTELS logosu, GRIDA, QR ve KARTVİZİT; solda iki satır ad soyad (Lora) ve görev.", sc)
    cx = 32.0
    card = A.rrect(48.0, 73.0, 4.0, cx, 49.5)                   # x 8..56, y 13..86 (sehpanın üstünde biter)
    lg, yb = logo(cx, 81.5, 38.0, "c")
    div = rule(cx - 6.0, cx + 6.0, yb - 3.2, 0.6)
    gr = t("ms6", GRIDA, 3.6, cx, yb - 7.6, "c", 2.2)
    tile = qr(d, cx, 41.0, 30.0)
    cap = t("ms7", "KARTVİZİT", 3.0, cx, tile.bounds()[1] - 6.6, "c", 1.2)
    white = lg + div + gr + cap
    d.lines.update({"logo": lg, "çizgi": div, "GRIDA": gr, "KARTVİZİT": cap})
    d.add(None, card - tile - white, BLUE)                      # beyazlar kartta oyuk: tablanın beyazı görünür
    if sc["dark"]:
        d.inlay.append((white, WHITE))
    y = name_lines(d, "lora", 7.8, X0, 64.0, lead=1.58)
    d.add("görev", t("ms6", TITLE, 4.2, X0, y - 11.0, "l", 0.1, 54.0), BLUE)
    return d


LAYOUTS = [m1_sutun, m2_genis, m3_mavi_kart, m4_ust_bant, m5_ortali]
DESIGNS = [(fn, sc) for fn in LAYOUTS for sc in (WHITE_SC, BLACK_SC)]   # 1 beyaz, 2 siyah, 3 beyaz, ...


# ---------------------------------------------------------------- katılar, kontroller, görseller

def solids(d):
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
    return parts


def build(item):
    fn, sc = item
    d = fn(sc)
    d.parts = solids(d)
    d.stand, (z0, y0) = B.stand()
    d.shown = B.assembled(d.parts, z0, y0) + [("Sehpa", d.stand, d.sc["body"])]
    return d


def mesh(parts):
    return [(*A.mesh_arrays(m), SHOW[c]) for _, m, c in parts]


def thin(cs, lim=MIN_LINE):
    """`lim` mm'den ince alan (%). Sivri köşelerin ucu (her biri < 0,2 mm²) sayılmaz; ince şeritler sayılır."""
    th = cs - cs.offset(-lim / 2, J).offset(lim / 2, J)
    return round(100 * sum(p.area() for p in th.decompose() if p.area() > 0.2) / max(cs.area(), 1e-9), 1)


def problems(d):
    """Dolgular üst üste binmesin; adlı öğeler arası ≥ 2 mm, kenara ve sehpaya ≥ 3 mm; çizgi ve aralar basılabilsin."""
    found = []
    cols = [(cs, col) for cs, col in d.inlay]
    for k, (a, ca) in enumerate(cols):
        for b, cb in cols[k + 1:]:
            if ca != cb and (a ^ b).area() > 0.01:
                found.append(f"{NAMES[ca]}/{NAMES[cb]} dolgu çakışıyor")
    safe = I.outline().offset(-3.0, J) ^ A.rect(-70, 10.0, 70, 100)
    items = list(d.lines.items())
    for k, (n, cs) in enumerate(items):
        if (cs - safe).area() > 0.05:
            found.append(f"{n} kenarda")
        for n2, cs2 in items[k + 1:]:
            if (cs.offset(2.0, J) ^ cs2).area() > 0.01:
                found.append(f"{n} ~ {n2}")
    for n, cs in items:
        if n == "QR":
            continue
        inner, gap, _ = B.line_metrics(cs)
        p = thin(cs)
        if p > 3.0 or inner < MIN_GAP or gap < MIN_GAP:
            found.append(f"{n}: ince %{p}, iç {inner:.2f}, ara {gap:.2f}")
    return found


def qr_check(d):
    im = render(mesh(d.parts), 1600, A.R_TOP, light=False, margin=0.03)
    bg = Image.new("RGB", im.size, (150, 152, 158))
    bg.paste(im, (0, 0), im)
    im = bg.convert("L")
    ppm = im.width * (1 - 2 * 0.03) / I.PW
    sim = Q.simulate(im, ppm, 1.0, **dict(Q.SIM_CASES)["hepsi birden"])
    return QR.content in Q.decode(im), QR.content in Q.decode(sim)


def font_ui(n, f="Outfit-SemiBold.ttf"):
    return ImageFont.truetype(os.path.join(A.FONT_DIR, f), n)


def front(d, width):
    return A.fit_into(render(mesh(d.shown), 1600, rotation(0, -90), flat=0.85, margin=0.02), width, 10 ** 4)


def sheet(d, i):
    W, H = 1500, 700
    canvas = Image.new("RGB", (W, H), (236, 239, 244))
    dr = ImageDraw.Draw(canvas)
    views = [(rotation(0, -90), "Önden, sehpada (120 × 90 mm)", 0.85), (rotation(-28, -68), "Masada (3/4)", None),
             (rotation(-90, -90), "Yandan: 15° eğik", None)]
    boxes = [(30, 130, 700, 630), (720, 130, 1240, 630), (1260, 130, 1470, 630)]
    parts = mesh(d.shown)
    for (R, label, flat), (x0, y0, x1, y1) in zip(views, boxes):
        dr.rounded_rectangle((x0, y0, x1, y1), 22, fill=(146, 153, 166))
        im = A.fit_into(render(parts, 1200, R, flat=flat, margin=0.02), x1 - x0 - 40, y1 - y0 - 60)
        canvas.paste(im, (x0 + (x1 - x0 - im.width) // 2, y0 + 40 + (y1 - y0 - 40 - im.height) // 2), im)
        dr.text((x0 + 16, y0 + 10), label, fill=(236, 239, 244), font=font_ui(18))
    dr.text((30, 18), f"{i}. {d.title.upper()} · {d.sc['key'].upper()} TABLA", fill=(24, 26, 30), font=font_ui(32))
    dr.text((30, 62), d.desc, fill=(80, 86, 98), font=font_ui(19))
    ok = d.qr[0] and not d.problems
    dr.text((30, 94), f"Gövde 1 cm · yazılar ve logo yüzeyle aynı hizada 0,8 mm renkli dolgu · QR "
                      f"{'okundu' if d.qr[0] else 'OKUNMADI'}{', benzetimde de' if d.qr[1] else ''}"
                      f"{'' if not d.problems else ' · ' + '; '.join(d.problems)}",
            fill=(22, 120, 60) if ok else (200, 30, 38), font=font_ui(19))
    canvas.save(os.path.join(OUT_DIR, d.key + ".png"))


# ---------------------------------------------------------------- katalog

NAVY, PAPER, INK, MUTED = (20, 44, 62), (246, 247, 249), (20, 26, 34), (98, 106, 118)


def header(im, dr, W, page, n, sub):
    dr.rectangle((0, 0, W, 230), fill=PALOMA_BLUE)
    lg = L.raster(118)
    im.paste(lg, (70, 56), lg)
    dr.text((70 + lg.width + 46, 66), "GRIDA", font=font_ui(46), fill=(255, 255, 255))
    dr.text((70 + lg.width + 46, 128), "Belek · Antalya", font=font_ui(28), fill=(232, 242, 247))
    s = f"{page}/{n}"
    dr.text((W - 80 - dr.textlength(s, font=font_ui(36)), 96), s, font=font_ui(36), fill=(232, 242, 247))
    dr.text((70, 262), sub, font=font_ui(34), fill=INK)


def footer(dr, W, H, text):
    dr.rounded_rectangle((60, H - 140, W - 60, H - 64), 20, fill=NAVY)
    dr.text((W / 2 - dr.textlength(text, font=font_ui(29)) / 2, H - 120), text, font=font_ui(29), fill=(244, 246, 248))


def catalog(ds):
    """Her sayfada düzenler satır satır: solda beyaz tabla, sağda siyah tabla (numaralı). Sonra kartvizit sayfası."""
    W, H = 1654, 2339
    f = font_ui
    rows = [ds[k:k + 2] for k in range(0, len(ds), 2)]
    groups = [rows[:2], rows[2:4], rows[4:]]
    n = len(groups) + 1
    pages = []
    for p, group in enumerate(groups):
        im = Image.new("RGB", (W, H), PAPER)
        dr = ImageDraw.Draw(im)
        header(im, dr, W, p + 1, n, f"{DATA['isim']} · {DATA['gorev']} · QR'lı masa isimliği")
        y = 330
        if p == 0:
            for line in ("Beyaz tablada siyah ve mavi yazı, siyah tablada beyaz ve mavi detay. Logo, yazılar ve QR "
                         "yüzeyle aynı hizada renkli dolgu: baskı gibi düz ve net.",
                         "İsimlikte otel, ad soyad ve görev yazar; telefonlar, e-posta ve adres QR'ın açtığı "
                         "kartvizit sayfasındadır."):
                for row in N.wrap(dr, line, f(27), W - 140):
                    dr.text((70, y), row, font=f(27), fill=MUTED)
                    y += 38
                y += 6
            y += 14
        rh = (H - 170 - y) // len(group) if len(group) > 1 else 860
        for row in group:
            m = ds.index(row[0]) // 2 + 1
            dr.text((70, y), f"Model {m} · {row[0].title}", font=f(40), fill=INK)
            for line in N.wrap(dr, row[0].desc, f(25), W - 140)[:1]:
                dr.text((70, y + 54), line, font=f(25), fill=MUTED)
            cw = (W - 3 * 60) // 2
            for k, d in enumerate(row):
                x0, y0 = 60 + k * (cw + 60), y + 100
                ch = rh - 130
                dr.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 26, fill=(255, 255, 255), outline=(222, 226, 234))
                img = front(d, cw - 60)
                img = A.fit_into(img, cw - 60, ch - 80)
                im.paste(img, (x0 + (cw - img.width) // 2, y0 + 20 + (ch - 80 - img.height) // 2), img)
                num = ds.index(d) + 1
                dr.ellipse((x0 + 24, y0 + ch - 66, x0 + 76, y0 + ch - 14), fill=NAVY)
                dr.text((x0 + 50 - dr.textlength(str(num), font=f(28)) / 2, y0 + ch - 58), str(num), font=f(28),
                        fill=(255, 255, 255))
                dr.text((x0 + 92, y0 + ch - 56), "Beyaz tabla" if not d.sc["dark"] else "Siyah tabla", font=f(27),
                        fill=MUTED)
            y += rh
        if p == len(groups) - 1:
            x0, y0, cw = 60, y + 20, W - 120
            ch = H - 170 - y0
            if ch > 300:
                dr.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 26, fill=(255, 255, 255), outline=(222, 226, 234))
                for k, d in enumerate(ds[:2]):
                    img = A.fit_into(render(mesh(d.shown), 1200, rotation(-28, -68), margin=0.02), 560, ch - 60)
                    im.paste(img, (x0 + 30 + k * 520, y0 + (ch - img.height) // 2), img)
                ty = y0 + 60
                for line in ("12 × 9 cm, gövde 1 cm, köşeler yuvarlak", "Logo ve yazılar düz renkli dolgu",
                             "QR telefonla okutulur, kartvizit açılır", "Masa sehpası dahil, 15° eğik durur"):
                    dr.ellipse((x0 + 1110, ty + 10, x0 + 1124, ty + 24), fill=PALOMA_BLUE)
                    for j, part in enumerate(N.wrap(dr, line, f(26), cw - 1160)):
                        dr.text((x0 + 1140, ty + j * 34), part, font=f(26), fill=MUTED)
                    ty += 34 * len(N.wrap(dr, line, f(26), cw - 1160)) + 22
        footer(dr, W, H, "Beğendiğiniz tasarımın numarasını yazmanız yeterli." if p == len(groups) - 1 else
               "Ölçü 12 × 9 cm · 1 cm kalın · masa sehpası dahil")
        pages.append(im)
    shot = os.path.join(OUT_DIR, "sayfa_onizleme.png")
    im = Image.new("RGB", (W, H), PAPER)
    dr = ImageDraw.Draw(im)
    header(im, dr, W, n, n, "QR'ı okutunca açılan kartvizit sayfası")
    y = 330
    for line in ("Telefonla QR okutulunca Süleyman Bey'in kartviziti açılır: tek dokunuşla arama (cep ve şirket hattı), "
                 "WhatsApp, e-posta, otelin konumu ve rehbere kaydetme.",
                 "Yazılar Paloma Hotels logosunun yazı sisteminde: ad PALOMA gibi kalın, soyad HOTELS gibi ince. Tam "
                 "ekran Akdeniz görseli ve numaralı bölümler; açılışta logo ve isim harf harf gelir. Telefon koyu "
                 "moddaysa sayfa gece renklerine geçer (sağda).",
                 "Bilgiler değişirse yalnız sayfa güncellenir; isimlik ve QR aynı kalır."):
        for row in N.wrap(dr, line, f(28), W - 140):
            dr.text((70, y), row, font=f(28), fill=INK)
            y += 42
        y += 10
    if os.path.exists(shot):
        s = Image.open(shot).convert("RGB")
        s = A.fit_into(s, W - 140, H - y - 230)
        im.paste(s, ((W - s.width) // 2, y + 20))
    footer(dr, W, H, f"Sayfa adresi: {DATA['sayfa_url'].replace('https://', '').rstrip('/')}")
    pages.append(im)
    for k, pg in enumerate(pages, 1):
        pg.save(os.path.join(OUT_DIR, f"musteri_{k}.png"), optimize=True)
        pg.convert("RGB").save(os.path.join(OUT_DIR, f"musteri_{k}.jpg"), "JPEG", quality=90, optimize=True)
    pages[0].save(os.path.join(OUT_DIR, "musteri_katalog.pdf"), save_all=True, append_images=pages[1:], resolution=200)


def check(i):
    d = build(DESIGNS[i - 1])
    d.problems = problems(d)
    d.qr = qr_check(d)
    sheet(d, i)
    return f"{i:2d} {d.key:22s} QR {d.qr}  sorun: {d.problems or 'yok'}"


def main():
    from multiprocessing import Pool
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"QR: {Q.describe(QR, Q.module_for(QR, 30.0)) if hasattr(Q, 'describe') else QR.qr.version}")
    only = sys.argv[1:]
    if only == ["katalog"]:
        catalog([build(x) for x in DESIGNS])
        return
    todo = [i for i, (fn, sc) in enumerate(DESIGNS, 1) if not only or any(o in fn.__name__ for o in only)]
    with Pool(4) as pool:
        for line in pool.map(check, todo):
            print(line)
    if not only:
        catalog([build(x) for x in DESIGNS])


if __name__ == "__main__":
    main()
