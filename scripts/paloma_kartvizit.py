"""PALOMA GRIDA – Süleyman Boylu: dikey kartvizit, 40 × 80 mm, ince (1,6 mm), hafif kabartmalı, QR'lı; 10 örnek.

Kullanıcı: "Süleyman Boylu'ya dikey kartvizitlik, 8 × 4 cm, çok kalın olmayacak, normal kartvizit gibi hafif kabartmalı,
aynı renk tonlarıyla 10 örnek, hepsi QR'lı". Renk tonları isimliğindeki gibi (scripts/paloma_isimlik.py, seçilen 3 · Mavi
kart): beyaz, siyah ve logonun mavisi (#69A1BA); PALOMA HOTELS logosu, GRIDA, ad soyad, görev; QR isimlikteki QR'la aynı
(kartvizit sayfası https://suleymanboylu.qrsistem.workers.dev).

Yapı (yüzü yukarı basılır, destek yok):
  0–1,2  gövde (beyaz ya da siyah), köşeler R3
  0,8–1,2  dolgu: logo, GRIDA, görev, çizgiler, mavi alanlar, QR (yüzeyle aynı hizada, 2 katman)
  1,2–1,6  kabartma: ad soyad (2 katman, 0,4 mm): elle hissedilir, QR düz kalır (kabartma QR'ın okunmasını bozar)
Beş düzen × iki gövde (beyaz: siyah ad, mavi ayrıntı; siyah: beyaz ad, mavi ayrıntı) = 10 örnek.

Çıktı : paloma_isimlik/kartvizit/<no>_<düzen>_<gövde>.png, katalog.pdf ve sayfa_1..2.jpg
Kullanım: python3 scripts/paloma_kartvizit.py
"""
import os
import sys

import manifold3d as m3
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paloma_isimlik as PI  # noqa: E402  (logo, yazı, QR, renkler)

A, Q, N, B = PI.A, PI.Q, PI.N, PI.B
from cift_tarafli_isimlik import render, rotation  # noqa: E402

OUT = os.path.join(PI.OUT_DIR, "kartvizit")
BLACK, WHITE, BLUE = PI.BLACK, PI.WHITE, PI.BLUE
SHOW, NAMES = PI.SHOW, PI.NAMES
J = m3.JoinType.Round
KW, KH, KR = 40.0, 80.0, 3.0                  # kart (dikey) ve köşe
T, INLAY, RELIEF = 1.2, 0.4, 0.4               # gövde, dolgu, kabartma (mm)
X0, X1, TOP, BOT = -17.0, 17.0, 77.0, 3.0      # kenar boşluğu 3 mm
QRS = 30.0                                     # QR karosu (sessiz bölge dahil): 3. sürüm, kare ~0,91 mm (en az 0,9)
t, logo = PI.t, PI.logo
FIRST, LAST, TITLE, GRIDA = PI.FIRST, PI.LAST, PI.TITLE, PI.GRIDA


def outline():
    return A.rrect(KW, KH, KR, 0.0, KH / 2)


class Kart:
    def __init__(self, no, key, ad, desc, sc):
        self.no, self.key, self.ad, self.desc, self.sc = no, key, ad, desc, sc
        self.inlay, self.relief = [], []
        self.yukseklik = {}                                     # renge göre kabartma yüksekliği (yoksa RELIEF)

    def dolgu(self, cs, col):
        if col != self.sc["body"]:
            self.inlay.append((cs, col))
        return cs

    def kabart(self, cs, col):
        self.relief.append((cs, col))
        return cs


def qr(k, cx, cy, s=QRS, zemin=None):
    """QR karosu: kareler koyu, karo açık. Döner: karo (altındaki renkli alandan çıkarılsın)."""
    _, dark, _ = Q.shapes(PI.QR, Q.module_for(PI.QR, s), cx, cy)
    tile = A.rrect(s, s, 1.2, cx, cy)
    if k.sc["body"] == WHITE:
        k.inlay.append((dark ^ tile, BLACK))                    # karo gövdenin beyazı
    else:
        k.inlay.append((tile - dark, WHITE))                    # kareler gövdenin siyahı
    return tile


def _kalin(cs, kal, nokta=None):
    """Harfler kal mm kalınlaşır; Ü'nün noktaları (küçük parçalar) tersine biraz incelir: aralarındaki boşluk açılır.
    nokta=(en, boy) verilirse noktalar o ölçüde yuvarlak köşeli kareye büyür (alt kenarı yerinde, yukarı doğru):
    0,45 mm'lik nokta 0,4 nozulla basılmıyor, dilimleyici onu atıyor ve Ü'nün noktası gövdenin beyazı kalıyordu."""
    out, dots = [], []
    for p in cs.decompose():
        if p.area() > 1.6:
            out.append(p.offset(kal, J))
        elif nokta:
            b = p.bounds()
            dots.append([(b[0] + b[2]) / 2, b[1]])
        else:
            out.append(p.offset(-0.1, J))
    if dots:                                            # Ü'nün iki noktası arası ≥ 0,5 mm: büyüyünce dışa açılır
        w, h = nokta
        dots.sort()
        for a, b in zip(dots, dots[1:]):
            if b[0] - a[0] < w + 1.0:                   # aynı harfin noktaları
                d = (w + 0.5 - (b[0] - a[0])) / 2
                if d > 0:
                    a[0] -= d
                    b[0] += d
        out += [A.rrect(w, h, min(w, h) * 0.3, cx, y0 - 0.05 + h / 2) for cx, y0 in dots]
    return A.union(*out)


def ad(k, font, cap, x, y_top, align="c", lead=1.5, max_w=X1 - X0, nokta=None):
    """Ad ve soyad alt alta, kabartma. Döner: soyadın taban çizgisi."""
    # kabartmada harf arası ≥ 0,45 mm (aralık açılır), ince çizgiler 0,5 mm'ye (Lora'nın kıl çizgileri kalınlaşır)
    # Ü'nün noktaları harften daha uzak (kalınlaşınca da ≥ 0,45 mm kalsın)
    tr, kal = (0.45, 0.09) if font == "lora" else (0.3, 0.05)
    eski, PI.DOT_LIFT = PI.DOT_LIFT, 0.5
    try:
        y1 = y_top - cap
        k.kabart(_kalin(t(font, FIRST, cap, x, y1, align, tr, max_w), kal, nokta), k.sc["fg"])
        y2 = y1 - cap * lead
        k.kabart(_kalin(t(font, LAST, cap, x, y2, align, tr, max_w), kal, nokta), k.sc["fg"])
    finally:
        PI.DOT_LIFT = eski
    return y2


def gorev(k, y, x=0.0, align="c", cap=2.5, col=BLUE, max_w=X1 - X0):
    return k.dolgu(t("ms7", TITLE, cap, x, y, align, 0.15, max_w), col)


def yazi(k, s, cap, x, y, align="c", col=None, tr=1.2, max_w=X1 - X0):
    return k.dolgu(t("ms7", s, cap, x, y, align, tr, max_w), k.sc["fg"] if col is None else col)


def cizgi(x0, x1, y, w=0.5):
    return A.rect(x0, y - w / 2, x1, y + w / 2)


# ---------------------------------------------------------------- beş düzen

def d1_ortali(sc, no):
    k = Kart(no, "ortali", "Ortalı", "Her şey ortada: logo, GRIDA, iki satır ad soyad (Lora), kısa mavi çizgi, görev; "
             "altta QR.", sc)
    lg, yb = logo(0.0, TOP, 24.0, "c")
    k.dolgu(lg, sc["logo"])
    yazi(k, GRIDA, 2.2, 0.0, yb - 3.8, col=sc["fg"], tr=1.8)
    y = ad(k, "lora", 4.4, 0.0, yb - 8.6, lead=1.45)
    k.dolgu(cizgi(-4.0, 4.0, y - 5.4), BLUE)                  # y'nin kuyruğunun altında
    gorev(k, y - 9.6)
    qr(k, 0.0, 18.0)
    return k


def d2_mavi_kart(sc, no):
    k = Kart(no, "mavi_kart", "Mavi kart", "Altta mavi kart, içinde QR ve KARTVİZİT (isimlikteki gibi); üstte sola "
             "yaslı logo, ad soyad (Lora) ve görev.", sc)
    blok = A.rrect(KW - 6.0, 39.0, 2.6, 0.0, 22.5)            # y 3..42
    tile = qr(k, 0.0, 25.8)
    cap = t("ms7", "KARTVİZİT", 1.9, 0.0, 6.6, "c", 1.2)
    if sc["body"] != WHITE:
        k.inlay.append((cap, WHITE))
    k.dolgu(blok - tile.offset(0.0, J) - cap.offset(0.0, J), BLUE)
    lg, yb = logo(X0, TOP, 22.0)
    k.dolgu(lg, sc["logo"])
    y = ad(k, "lora", 4.4, X0, yb - 6.0, "l", lead=1.45)
    gorev(k, y - 5.6, X0, "l")
    return k


def d3_ust_bant(sc, no):
    k = Kart(no, "ust_bant", "Üst bant", "Üstte mavi bant, içinde beyaz logo ve GRIDA (Instagram'daki gibi); ortada "
             "ad soyad ve görev; altta QR.", sc)
    bant = A.rrect(KW - 6.0, 20.0, 2.6, 0.0, 67.0)            # y 57..77
    lg, yb = logo(0.0, 74.0, 22.0, "c")
    gr = t("ms6", GRIDA, 2.2, 0.0, yb - 3.6, "c", 1.8)
    beyaz = lg + gr
    k.dolgu(bant - beyaz.offset(0.0, J), BLUE)
    if sc["body"] != WHITE:
        k.inlay.append((beyaz, WHITE))
    y = ad(k, "ms6", 4.2, 0.0, 52.5)
    gorev(k, y - 5.6, col=BLUE)
    qr(k, 0.0, 18.0)
    return k


NOKTA_AD, NOKTA_G = (0.9, 0.9), (0.8, 0.9)                 # kabartmalı kartta Ü noktaları (en, boy mm)


def d3_ust_bant_kabartmali(sc, no):
    """Seçilen kart (3 · Üst bant), kullanıcı: "yazıları kabartmalı yap". Logo ve GRIDA mavi bandın boşluğundan beyaz,
    görev mavi 0,4 mm, ad soyad siyah 0,8 mm kabarır; QR düz kalır (kabartma gölgesi okumayı bozar). Kabartmada en ince yer
    0,5 mm: logo 24 mm (HOTELS kalınlaştırılmış), GRIDA 2,6 mm Bold, görev iki satır 3,2 mm Bold (tek satır 34 mm'ye
    sıkışınca çizgiler inceliyordu)."""
    k = Kart(no, "ust_bant_kabartmali", "Üst bant (kabartmalı)", "Seçilen 3 numara; bütün yazılar kabartma.", sc)
    bant = A.rrect(KW - 6.0, 18.0, 2.6, 0.0, 68.0)            # y 59..77
    lg, yb = logo(0.0, 74.6, 24.0, "c")
    eski, PI.DOT_LIFT = PI.DOT_LIFT, 0.45
    try:
        gr = t("ms7", GRIDA, 2.6, 0.0, yb - 3.7, "c", 1.9)
        g1 = _kalin(t("ms7", "Satın Alma", 3.2, 0.0, 0.0, "c", 0.4), 0.04)
        g2 = _kalin(t("ms7", "Müdürü", 3.2, 0.0, 0.0, "c", 0.4), 0.04, NOKTA_G)
    finally:
        PI.DOT_LIFT = eski
    beyaz = lg + gr
    k.dolgu(bant - beyaz.offset(0.0, J), BLUE)
    k.kabart(beyaz, WHITE if sc["body"] == WHITE else WHITE)
    y = ad(k, "ms6", 4.0, 0.0, 55.2, nokta=NOKTA_AD)
    k.yukseklik[BLACK] = 0.8                                # kullanıcı: "siyahları da daha kabart" (ad soyad 4 katman)
    k.kabart(g1.translate((0.0, y - 5.6)), BLUE)
    k.kabart(g2.translate((0.0, y - 10.0)), BLUE)
    qr(k, 0.0, 17.6)
    return k


def d4_yan_serit(sc, no):
    k = Kart(no, "yan_serit", "Yan şerit", "Solda boydan ince mavi şerit; sağında sola yaslı logo, ad soyad, görev; "
             "altta QR.", sc)
    k.dolgu(A.rrect(2.4, KH - 6.0, 1.2, -15.8, KH / 2), BLUE)  # x −17..−14,6
    x = -11.0
    lg, yb = logo(x, TOP, 22.0)
    k.dolgu(lg, sc["logo"])
    yazi(k, GRIDA, 2.1, x, yb - 3.6, "l", sc["fg"], 1.8, 28.0)
    y = ad(k, "ms6", 4.4, x, yb - 9.8, "l", max_w=28.0)
    gorev(k, y - 5.8, x, "l", max_w=28.0)
    qr(k, 1.5, 18.0)
    return k


def d5_qr_ustte(sc, no):
    k = Kart(no, "qr_ustte", "QR üstte", "Üstte QR ve DİJİTAL KARTVİZİT; ince mavi çizgi; ad soyad (Lora) ve görev; "
             "altta logo ve GRIDA.", sc)
    tile = qr(k, 0.0, 61.5)
    yazi(k, "DİJİTAL KARTVİZİT", 1.8, 0.0, tile.bounds()[1] - 3.0, col=BLUE, tr=0.9)
    k.dolgu(cizgi(-12.0, 12.0, 39.6), BLUE)
    y = ad(k, "lora", 4.4, 0.0, 36.4, lead=1.45)
    gorev(k, y - 5.0)
    lg, yb = logo(0.0, 15.0, 18.0, "c")
    k.dolgu(lg, sc["logo"])
    yazi(k, GRIDA, 1.8, 0.0, yb - 2.8, col=sc["fg"], tr=1.5)
    return k


DUZENLER = [d1_ortali, d2_mavi_kart, d3_ust_bant, d4_yan_serit, d5_qr_ustte]
GOVDE = [PI.WHITE_SC, PI.BLACK_SC]


# ---------------------------------------------------------------- katılar, kontroller

def katilar(k):
    out = outline()
    clip = out.offset(-1.0, J)
    by = {}
    for cs, col in k.inlay:
        by[col] = by.get(col, A.empty()) + (cs ^ clip)
    body = out.extrude(T)
    if by:
        body = body - A.union(*by.values()).extrude(INLAY + 0.01).translate((0, 0, T - INLAY))
    parts = [(f"Gövde ({NAMES[k.sc['body']]})", body, k.sc["body"])]
    for col, cs in by.items():
        parts.append((f"Dolgu ({NAMES[col]})", cs.extrude(INLAY).translate((0, 0, T - INLAY)), col))
    rel = {}
    for cs, col in k.relief:
        rel[col] = rel.get(col, A.empty()) + (cs ^ clip)
    for col, cs in rel.items():
        parts.append((f"Kabartma ({NAMES[col]})", cs.extrude(k.yukseklik.get(col, RELIEF)).translate((0, 0, T)), col))
    return parts


def sorunlar(k):
    found = []
    safe = outline().offset(-2.6, J)
    for cs, col in k.inlay + k.relief:
        if (cs - safe).area() > 0.05:
            found.append(f"{NAMES[col]} öğe kenarda")
    for cs, col in k.relief:
        p = PI.thin(cs, 0.5)
        inner, gap, _ = B.line_metrics(cs)
        if p > 3.0 or inner < 0.45 or gap < 0.45:
            found.append(f"kabartma ince %{p}, iç {inner:.2f}, ara {gap:.2f}")
    cols = k.inlay
    for i, (a, ca) in enumerate(cols):
        for b, cb in cols[i + 1:]:
            if ca != cb and (a ^ b).area() > 0.01:
                found.append(f"{NAMES[ca]}/{NAMES[cb]} dolgu çakışıyor")
    return found


def mesh(parts):
    return [(*A.mesh_arrays(m), SHOW[c]) for _, m, c in parts]


def qr_okunur(parts):
    im = render(mesh(parts), 1400, A.R_TOP, light=False, margin=0.03)
    bg = Image.new("RGB", im.size, (150, 152, 158))
    bg.paste(im, (0, 0), im)
    return PI.QR.content in Q.decode(bg.convert("L"))


# ---------------------------------------------------------------- görseller

def katalog(ks):
    """İki sayfa: 1) on örnek önden (üst sıra beyaz, alt sıra siyah gövde); 2) ikisi masada 3/4 ve ölçüler."""
    W, H = 1654, 2339
    PAPER, INK, MUTED = (244, 241, 234), (18, 19, 22), (85, 87, 92)
    f = PI.font_ui
    sayfalar = []
    im = Image.new("RGB", (W, H), PAPER)
    dr = ImageDraw.Draw(im)
    dr.text((70, 70), "Süleyman Boylu · dikey kartvizit", font=f(54), fill=INK)
    dr.text((70, 150), "40 × 80 mm · 1,6 mm ince · ad soyad hafif kabartma · QR kartvizit sayfasını açar",
            font=f(28), fill=MUTED)
    y = 250
    for row, sc in enumerate(GOVDE):
        dr.text((70, y), "Beyaz gövde: siyah ad, mavi ayrıntı" if row == 0 else "Siyah gövde: beyaz ad, mavi ayrıntı",
                font=f(32), fill=INK)
        y += 60
        cw = (W - 140) // 5
        for i, k in enumerate([k for k in ks if k.sc is sc]):
            img = A.fit_into(render(mesh(k.parts), 1100, A.R_TOP, margin=0.02, ambient=0.85), cw - 30, 820)
            x = 70 + i * cw + (cw - img.width) // 2
            im.paste(img, (x, y), img)
            ny = y + img.height + 24
            dr.ellipse((70 + i * cw + cw // 2 - 26, ny, 70 + i * cw + cw // 2 + 26, ny + 52), fill=(105, 161, 186))
            dr.text((70 + i * cw + cw // 2 - dr.textlength(str(k.no), font=f(28)) / 2, ny + 8), str(k.no), font=f(28),
                    fill=(255, 255, 255))
            dr.text((70 + i * cw + cw // 2 - dr.textlength(k.ad, font=f(24)) / 2, ny + 64), k.ad, font=f(24),
                    fill=MUTED)
        y = ny + 150
    dr.text((70, H - 90), "Beğendiğiniz kartvizitin numarasını yazmanız yeterli.", font=f(30), fill=INK)
    sayfalar.append(im)
    im = Image.new("RGB", (W, H), PAPER)
    dr = ImageDraw.Draw(im)
    dr.text((70, 70), "Yakından: masada, 3/4", font=f(54), fill=INK)
    for i, k in enumerate([ks[1], ks[6]]):
        img = A.fit_into(render(mesh(k.parts), 1400, rotation(-24, -58), margin=0.02), 740, 1150)
        im.paste(img, (70 + i * 780 + (740 - img.width) // 2, 220), img)
        dr.text((70 + i * 780, 1390), f"{k.no} · {k.ad} · {'beyaz' if k.sc['body'] == WHITE else 'siyah'} gövde",
                font=f(30), fill=INK)
    yy = 1500
    for line in ("Ölçü 40 × 80 mm (dikey), köşeler yuvarlak; toplam 1,6 mm: normal kartvizit gibi ince",
                 "Ad soyad 0,4 mm kabartma: parmakla hissedilir",
                 "Logo, görev ve QR yüzeyle aynı hizada renkli: net ve düz, QR kolay okunur",
                 "QR, isimlikteki kartvizit sayfasını açar: arama, WhatsApp, e-posta, konum, rehbere kaydet",
                 "Renkler isimlikteki gibi: beyaz, siyah ve Paloma mavisi"):
        dr.ellipse((80, yy + 12, 96, yy + 28), fill=(105, 161, 186))
        for j, part in enumerate(N.wrap(dr, line, f(30), W - 220)):
            dr.text((116, yy + j * 40), part, font=f(30), fill=MUTED)
        yy += 40 * len(N.wrap(dr, line, f(30), W - 220)) + 24
    sayfalar.append(im)
    pdf = os.path.join(OUT, "katalog.pdf")
    sayfalar[0].save(pdf, save_all=True, append_images=sayfalar[1:], resolution=200)
    for i, s in enumerate(sayfalar, 1):
        s.save(os.path.join(OUT, f"sayfa_{i}.jpg"), quality=90)
    return pdf


def main():
    os.makedirs(OUT, exist_ok=True)
    ks = []
    no = 1
    for sc in GOVDE:
        for fn in DUZENLER:
            k = fn(sc, no)
            k.parts = katilar(k)
            ok = qr_okunur(k.parts)
            s = sorunlar(k)
            print(f"{no:2d} {k.ad:10s} {sc['key']:5s} QR {'okunuyor' if ok else 'OKUNMUYOR'}"
                  + (f"  sorun: {s}" if s else ""), flush=True)
            img = render(mesh(k.parts), 1200, rotation(-24, -58), margin=0.03)
            img.save(os.path.join(OUT, f"{no:02d}_{k.key}_{sc['key']}.png"))
            ks.append(k)
            no += 1
    print("katalog:", katalog(ks))


if __name__ == "__main__":
    main()
