"""İNCE OTO LASTİK – tek QR'lı tezgâh isimliği önerileri (10): 7 beyaz zemin (siyah, kırmızı yazı), 3 siyah zemin
(beyaz, kırmızı yazı).

Uzar Oto Lastik'in basılan isimliğiyle aynı yapı: 120 × 90 mm (4:3), köşeler R8, siyah ya da beyaz gövde 1 cm,
yazılar ve lastik simgesi 2 mm kabartma, QR yüzeyle aynı hizada (beyaz zeminde siyah kareler, siyah zeminde beyaz
karo), 15° eğik sehpa. Küçük satırlar Outfit ExtraBold (harf içi boşlukları kabartmada dolmaz); her yazı satırının
en dar iç boşluğu ölçülür.

QR: işletmenin sitesi henüz yok. Örneklerde QR telefonu arar (TEL:+905458533070); `ince_isimlik/bilgiler.json`
→ `sayfa_url` yazılınca site adresine döner. Yoğunluğu son hâline benzesin diye en az sürüm 4.

Çıktı : ince_isimlik/<tasarım>.png, ince_isimlik/musteri_1.png, musteri_2.png, musteri_katalog.pdf

Kullanım:
  python3 scripts/ince_isimlik.py [anahtar ...]
"""
import json
import os
import sys

import manifold3d as m3
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import qr_sistemi as Q  # noqa: E402
import uzar_anahtarlik as U  # noqa: E402
import uzar_isimlik as I  # noqa: E402
import uzar_isimlik_baski as B  # noqa: E402
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "ince_isimlik")
DATA = json.load(open(os.path.join(OUT_DIR, "bilgiler.json"), encoding="utf-8"))
TEL = Q.phone_e164(DATA["telefon"])
PHONE = Q.phone_display(TEL)
BLACK, WHITE, RED = A.BLACK, A.WHITE, A.RED
SHOW = B.SHOW
NAMES = {BLACK: "siyah", WHITE: "beyaz", RED: "kırmızı"}
J = m3.JoinType.Round
X0, X1 = -54.0, 54.0                     # içerik kenarları


def make_qr():
    import segno
    content = Q.https_url(DATA["sayfa_url"]) if DATA.get("sayfa_url") else f"TEL:+{TEL}"
    natural = segno.make(content, error="m", micro=False).version
    q = segno.make(content, error="m", version=max(4, natural), micro=False, boost_error=True)
    return Q.Entry("sayfa", "TARA", content, PHONE, qr=q)


QR = make_qr()


# ---------------------------------------------------------------- parçalar

def heavy():
    return I.heavy()


def bold():
    return I.bold()


SMALL = A.Font("Outfit-ExtraBold.ttf")


def word(s, f, cap, x, y, align="l", tracking=0.0, max_w=None):
    return B.loosen_dots(I.text(f, s, cap, x, y, align, tracking, max_w))


def ince(cap, x, y, align="l", max_w=None):
    return word("İNCE", heavy(), cap, x, y, align, cap * 0.05, max_w)


def scheme(dark):
    return {"body": BLACK if dark else WHITE, "fg": WHITE if dark else BLACK, "dark": dark}


def tire(r, cx, cy, sc, mono=False):
    """Lastik simgesi: dişli lastik (yazı renginde) ve 5 kollu jant (kırmızı); mono: hepsi kırmızı."""
    tyre, rim = U.tire(r, cx, cy, teeth=20, depth=r * 0.14)
    return [(tyre, RED if mono else sc["fg"]), (rim, RED)]


def arrow(x, y, h=7.8):
    return A.polygon([(x, y - h / 2), (x + h * 0.82, y), (x, y + h / 2)])


def qr_block(cx, cy, s, sc, frame=False):
    """QR (yüzeyle aynı hizada dolgu): beyaz zeminde siyah kareler, siyah zeminde beyaz karo. frame: ince çerçeve."""
    module = Q.module_for(QR, s)
    _, dark, _ = Q.shapes(QR, module, cx, cy)
    square = A.rrect(s, s, 1.6, cx, cy)
    inlay = [(square - dark, WHITE)] if sc["dark"] else [(dark ^ square, BLACK)]
    if frame:
        g, w = 1.8, 1.1
        inlay.append((A.rrect(s + 2 * (g + w), s + 2 * (g + w), 2.6, cx, cy) - A.rrect(s + 2 * g, s + 2 * g, 1.8, cx, cy),
                      sc["fg"]))
    return inlay


class Design:
    def __init__(self, key, title, desc, sc):
        self.key, self.title, self.desc, self.sc = key, title, desc, sc
        self.raised, self.inlay, self.lines = [], [], {}

    def add(self, name, cs, colour):
        """Kabartma; `name` verilirse yazı satırı olarak ölçülür."""
        self.raised.append((cs, colour))
        if name:
            self.lines[name] = cs
        return cs


# ---------------------------------------------------------------- ortak düzen: sol sütun yazılar, sağda QR

def left_column(d, x0=X0, x1=0.0, top=74.0, header="lastik", phone_y=13.5, hemen=True):
    sc = d.sc
    r = 9.5
    if header == "lastik":                                   # İNCE + lastik simgesi
        w = d.add("İNCE", ince(18.0, x0, top, max_w=x1 - x0 - 2 * r - 4.0), sc["fg"])
        for cs, col in tire(r, w.bounds()[2] + 4.0 + r, top, sc):
            d.add(None, cs, col)
    elif header == "rozet":                                  # kırmızı 7/24 rozeti + İNCE
        disk = A.circle(10.5, x0 + 10.5, top)
        txt = I.text(heavy(), "7/24", 7.6, x0 + 10.5, top, "c", 0.2)
        d.add("7/24 rozet", disk - txt.offset(0.05, J), RED)
        d.add("İNCE", ince(18.0, x0 + 25.0, top, max_w=x1 - x0 - 25.0), sc["fg"])
    elif header == "cizgi":                                  # İNCE + altında kalın kırmızı çizgi, kırmızı lastik
        w = d.add("İNCE", ince(18.0, x0, top + 1.5, max_w=x1 - x0 - 2 * r - 4.0), sc["fg"])
        d.add(None, A.rrect(w.bounds()[2] - x0, 2.0, 1.0, (x0 + w.bounds()[2]) / 2, w.bounds()[1] - 3.2), RED)
        for cs, col in tire(r, w.bounds()[2] + 4.0 + r, top, sc, mono=True):
            d.add(None, cs, col)
    d.add("OTO LASTİK", word("OTO LASTİK", bold(), 7.2, x0, top - 16.5, "l", 1.0, x1 - x0), RED)
    if header != "rozet":
        d.add("7/24 HİZMET", word("7/24 HİZMET", SMALL, 4.6, x0, top - 25.5, "l", 0.9), sc["fg"])
    tara = d.add("TARA", I.text(heavy(), "TARA", 10.5, x0, 33.0, "l", 0.7), sc["fg"])
    d.add(None, arrow(tara.bounds()[2] + 3.2, 33.0), RED)
    if hemen:
        d.add("HEMEN ARA", word("HEMEN ARA", SMALL, 4.4, x0, phone_y + 8.2, "l", 0.9), RED)
    d.add("telefon", word(PHONE, SMALL, 5.0, x0, phone_y, "l", 0.4, x1 - x0), sc["fg"])


def w1_klasik(dark=False):
    d = Design("1_klasik", "Klasik", "İNCE ve lastik simgesi, altında kırmızı OTO LASTİK; QR sağda.", scheme(dark))
    left_column(d)
    d.inlay += qr_block(30.0, 46.0, 48.0, d.sc)
    return d


def w2_rozet(dark=False):
    d = Design("2_rozet", "7/24 rozeti", "Solda kırmızı 7/24 rozeti, yanında İNCE; QR sağda.", scheme(dark))
    left_column(d, header="rozet")
    d.inlay += qr_block(30.0, 46.0, 48.0, d.sc)
    return d


def w3_lastik_izi(dark=False):
    """Üstte boydan başlık, altında kırmızı lastik izi şeridi; altta solda yazılar, sağda QR."""
    d = Design("3_lastik_izi", "Lastik izi", "Boydan başlık ve kırmızı lastik izi şeridi; altta TARA, telefon ve QR.",
               scheme(dark))
    sc, r = d.sc, 9.5
    w = d.add("İNCE", ince(15.5, X0, 75.0, max_w=40.0), sc["fg"])
    xo = w.bounds()[2] + 5.0                               # İNCE'nin yanında alt alta OTO / LASTİK
    d.add("OTO", word("OTO", bold(), 7.2, xo, 79.6, "l", 1.0), RED)
    d.add("LASTİK", word("LASTİK", bold(), 7.2, xo, 70.4, "l", 1.0), RED)
    for cs, col in tire(r, X1 - r, 75.0, sc):              # lastik sağ üstte
        d.add(None, cs, col)
    d.add(None, U.tread_band(X0, X1, 61.2, 64.6, pitch=3.8), RED)
    d.add("7/24 HİZMET", word("7/24 HİZMET", SMALL, 4.6, X0, 53.5, "l", 0.9), sc["fg"])
    tara = d.add("TARA", I.text(heavy(), "TARA", 10.5, X0, 41.0, "l", 0.7), sc["fg"])
    d.add(None, arrow(tara.bounds()[2] + 3.2, 41.0), RED)
    d.add("HEMEN ARA", word("HEMEN ARA", SMALL, 4.4, X0, 27.0, "l", 0.9), RED)
    d.add("telefon", word(PHONE, SMALL, 5.0, X0, 18.5, "l", 0.4, 58.0), sc["fg"])
    d.inlay += qr_block(31.0, 33.5, 45.0, sc)
    return d


def w4_qr_solda(dark=False):
    d = Design("4_qr_solda", "QR solda", "QR solda, yazılar ve lastik simgesi sağda.", scheme(dark))
    left_column(d, x0=0.0, x1=X1)
    d.inlay += qr_block(-30.0, 46.0, 48.0, d.sc)
    return d


def w5_cerceve(dark=False):
    d = Design("5_cerceve", "Kırmızı çerçeve", "Kenardan içeride ince kırmızı çerçeve; içinde klasik düzen.",
               scheme(dark))
    w, h, cy = 114.0, 79.0, 48.1
    d.add(None, A.rrect(w, h, 5.0, 0, cy) - A.rrect(w - 2.4, h - 2.4, 3.8, 0, cy), RED)
    left_column(d, x0=-50.0, x1=0.0, top=73.0, phone_y=15.5)
    d.inlay += qr_block(28.0, 47.0, 46.0, d.sc)
    return d


def w6_buyuk_baslik(dark=False):
    """Üstte boydan büyük İNCE ve kırmızı OTO LASTİK; altta solda büyük lastik ve telefon, sağda QR."""
    d = Design("6_buyuk_baslik", "Büyük başlık", "Üstte boydan büyük İNCE OTO LASTİK; altta büyük lastik, telefon ve QR.",
               scheme(dark))
    sc = d.sc
    w = d.add("İNCE", ince(17.5, X0, 74.0), sc["fg"])
    d.add("OTO LASTİK", word("OTO LASTİK", bold(), 9.0, w.bounds()[2] + 6.0, 74.0, "l", 1.2, X1 - w.bounds()[2] - 6.0),
          RED)
    d.add(None, A.rect(X0, 62.4, X1, 63.6), RED)
    for cs, col in tire(13.0, X0 + 13.0, 41.5, sc):
        d.add(None, cs, col)
    d.add("7/24 HİZMET", word("7/24 HİZMET", SMALL, 4.6, X0 + 30.0, 45.0, "l", 0.8), sc["fg"])
    d.add("HEMEN ARA", word("HEMEN ARA", SMALL, 4.4, X0 + 30.0, 36.0, "l", 0.9), RED)
    d.add("telefon", word(PHONE, SMALL, 5.0, X0, 16.5, "l", 0.4, 58.0), sc["fg"])
    d.inlay += qr_block(32.0, 33.0, 44.0, sc)
    return d


def w7_kirmizi_cizgi(dark=False):
    d = Design("7_kirmizi_cizgi", "Kırmızı çizgi", "İNCE'nin altında kalın kırmızı çizgi, kırmızı lastik; QR çerçeveli.",
               scheme(dark))
    left_column(d, header="cizgi")
    d.inlay += qr_block(30.0, 46.0, 46.0, d.sc, frame=True)
    return d


def b1_gece():
    d = w1_klasik(dark=True)
    d.key, d.title, d.desc = "8_gece", "Gece", "Siyah zemin: beyaz İNCE ve lastik, kırmızı OTO LASTİK; QR beyaz karoda."
    return d


def b2_rozet_siyah():
    d = w2_rozet(dark=True)
    d.key, d.title, d.desc = "9_rozet_siyah", "Siyah, 7/24 rozeti", "Siyah zemin, kırmızı 7/24 rozeti; QR beyaz karoda."
    return d


def b3_lastik_izi_siyah():
    d = w3_lastik_izi(dark=True)
    d.key, d.title, d.desc = "10_lastik_izi_siyah", "Siyah, lastik izi", "Siyah zemin, kırmızı lastik izi şeridi."
    return d


DESIGNS = [w1_klasik, w2_rozet, w3_lastik_izi, w4_qr_solda, w5_cerceve, w6_buyuk_baslik, w7_kirmizi_cizgi,
           b1_gece, b2_rozet_siyah, b3_lastik_izi_siyah]


# ---------------------------------------------------------------- katılar, kontrol, çizim

def solids(d):
    """Panel baskı yönünde (yüzü yukarı): gövde, yüzeyle aynı hizada dolgular, kabartmalar. Sonra eklenen kabartma
    öncekinin üstüne yazar."""
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


def build(fn):
    d = fn()
    d.parts = solids(d)
    d.stand, (z0, y0) = B.stand()
    d.shown = B.assembled(d.parts, z0, y0) + [("Sehpa", d.stand, BLACK)]
    return d


def qr_check(d):
    im = B.top_view(d.parts).convert("L")
    ppm = im.width * (1 - 2 * 0.03) / I.PW
    sim = Q.simulate(im, ppm, 1.2, **dict(Q.SIM_CASES)["hepsi birden"])
    return QR.content in Q.decode(im), QR.content in Q.decode(sim)


def mesh(parts):
    return [(*A.mesh_arrays(m), SHOW[c]) for _, m, c in parts]


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


def catalog(ds):
    """Müşteriye: musteri_1.png (1–6), musteri_2.png (7–10), musteri_katalog.pdf."""
    W, H = 1654, 2339
    big = ImageFont.truetype(os.path.join(A.FONT_DIR, "BarlowCondensed-Black.ttf"), 118)
    mid = ImageFont.truetype(os.path.join(A.FONT_DIR, "BarlowCondensed-ExtraBold.ttf"), 44)
    f = font_ui
    ink, muted, paper, red = (20, 20, 22), (96, 98, 106), (245, 245, 243), SHOW[RED]
    pages = []
    for p, group in enumerate([ds[:6], ds[6:]]):
        im = Image.new("RGB", (W, H), paper)
        dr = ImageDraw.Draw(im)
        dr.rectangle((0, 0, W, 250), fill=(250, 250, 248))
        dr.rectangle((0, 246, W, 254), fill=red)
        dr.text((70, 40), "İNCE", font=big, fill=ink)
        x = 76 + dr.textlength("İNCE", font=big) + 18
        dr.text((x, 70), "OTO LASTİK", font=mid, fill=red)
        dr.text((x, 128), "7/24 HİZMET", font=f(26), fill=muted)
        dr.text((70, 186), "Tek QR'lı tezgâh isimliği · tasarım önerileri", font=f(30), fill=muted)
        dr.text((W - 70 - dr.textlength(f"{p + 1}/2", font=f(28)), 196), f"{p + 1}/2", font=f(28), fill=muted)
        y = 285
        for line in ("TARA: telefonla okutunca işletme sayfası açılır (site hazırlanınca). Örneklerde şimdilik arar.",
                     "1–7 beyaz zemin (siyah, kırmızı yazı) · 8–10 siyah zemin (beyaz, kırmızı yazı)"):
            dr.text((70, y), line, font=f(27), fill=ink)
            y += 40
        top, gap, cw = 395, 50, (W - 3 * 60) // 2
        ch = (H - top - 190 - 2 * gap) // 3
        for k, d in enumerate(group):
            x0, y0 = 60 + (k % 2) * (cw + 60), top + (k // 2) * (ch + gap)
            dr.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 28, fill=(255, 255, 255), outline=(226, 226, 230))
            n = ds.index(d) + 1
            dr.ellipse((x0 + 26, y0 + 24, x0 + 86, y0 + 84), fill=red)
            dr.text((x0 + 56 - dr.textlength(str(n), font=f(34)) / 2, y0 + 34), str(n), font=f(34),
                    fill=(255, 255, 255))
            dr.text((x0 + 104, y0 + 30), d.title, font=f(38), fill=ink)
            img = A.fit_into(render(mesh(d.shown), 1300, rotation(0, -90), flat=0.85, margin=0.02), cw - 70, ch - 190)
            im.paste(img, (x0 + (cw - img.width) // 2, y0 + 100 + (ch - 190 - img.height) // 2), img)
            ty = y0 + ch - 78
            for line in wrap(dr, d.desc, f(26), cw - 60)[:2]:
                dr.text((x0 + 30, ty), line, font=f(26), fill=muted)
                ty += 34
        if p == 1:                                          # boş kalan yere: ürün bilgisi
            y0, y1 = top + 2 * (ch + gap), H - 190
            dr.rounded_rectangle((60, y0, W - 60, y1), 28, fill=(255, 255, 255), outline=(226, 226, 230))
            dr.text((100, y0 + 40), "Ürün", font=f(38), fill=ink)
            ty = y0 + 110
            for line in ("Ölçü 12 × 9 cm, gövde 1 cm kalınlığında, köşeler yuvarlak",
                         "Yazılar ve lastik simgesi 2 mm kabartma; QR düz ve keskin",
                         "Tezgâh sehpası dahil, panel 15° eğik durur",
                         f"Telefon: {PHONE}"):
                dr.ellipse((100, ty + 10, 114, ty + 24), fill=red)
                dr.text((130, ty), line, font=f(30), fill=muted)
                ty += 56
            pick = ds[0]
            img = A.fit_into(render(mesh(pick.shown), 1200, rotation(-28, -68), margin=0.02), 520, y1 - y0 - 60)
            im.paste(img, (W - 100 - img.width, y0 + (y1 - y0 - img.height) // 2), img)
        foot = ("Beğendiğiniz tasarımın numarasını yazmanız yeterli." if p == 1 else
                "Ölçü 12 × 9 cm · 1 cm kalın · kabartma yazı · tezgâh sehpası dahil")
        dr.rounded_rectangle((60, H - 150, W - 60, H - 70), 22, fill=(16, 16, 18))
        dr.text((W / 2 - dr.textlength(foot, font=f(30)) / 2, H - 128), foot, font=f(30), fill=(244, 244, 242))
        im.save(os.path.join(OUT_DIR, f"musteri_{p + 1}.png"), optimize=True)
        pages.append(im)
    pages[0].save(os.path.join(OUT_DIR, "musteri_katalog.pdf"), save_all=True, append_images=pages[1:],
                  resolution=200)


def main():
    only = sys.argv[1:]
    ds = []
    for i, fn in enumerate(DESIGNS, 1):
        d = build(fn)
        if only and not any(o in d.key for o in only):
            continue
        d.metrics = {k: B.line_metrics(cs) for k, cs in d.lines.items()}
        d.qr = qr_check(d)
        sheet(d, i)
        ds.append(d)
        bad = {k: v for k, v in d.metrics.items() if v[0] < 0.6 or v[2] > 6.0}
        print(f"{d.key:22s} QR {d.qr}  dar/ince satırlar: {bad or 'yok'}")
    if not only:
        catalog(ds)


if __name__ == "__main__":
    main()
