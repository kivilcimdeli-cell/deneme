"""BOYDE LABS – kendi QR'lı isimliklerimiz: 9 × 12'den 10, 10 × 20'den 10 model.

Kullanıcı isteği: "BOYDE için bize de hem 9 × 12 hem 10 × 20, 10 adet ürün örneği, QR'lı masalık sunar mısın".

Marka: 3b · Katman işareti (nozul katmanların üstünde, en üst katman turuncu) ve iki katlı yazı (BOYDE, altında
turuncu çizgi ve LABS; Space Grotesk). Palet: INK siyah gövde, PAPER beyaz, ORANGE turuncu, GRAY gri (PLA tonları).
QR'lar çalışır: WhatsApp'ımızı açar (https://wa.me/905464754508); telefon 0546 475 45 08.

Yapı boyde_sektor'deki örneklerle aynı:
  9 × 12   120 × 90 mm, 1 cm gövde, yazı ve işaret 2 mm kabartma, QR yüzeyle aynı hizada; sehpa siyah
  10 × 20  200 × 100 mm, 5 mm gövde, yazı ve işaret yüzeyle aynı hizada renkli dolgu; sehpa gövde renginde

Çıktı : boyde_labs/kendi/kaynak/<model>.npz, <model>_duz.png (fotoğraf için; npz git'e girmez)
        boyde_labs/kendi/fotograf/<model>_studyo.jpg (scripts/boyde_urun_foto.py ile)
        boyde_labs/kendi/sunum_9x12.png, sunum_10x20.png, sunum.pdf

Kullanım: python3 scripts/boyde_kendi.py [model ...] [--rapor] [--foto] [--sunum]
"""
import json
import os
import sys

import numpy as np
from shapely import affinity
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_sektor as S  # noqa: E402  (boyde_urunler'i yükler: segno.make örnek moduna geçer; burada gerçeği)
import boyde_urunler as U  # noqa: E402
import anahtarlik as A  # noqa: E402
import qr_sistemi as Q  # noqa: E402

OUT = os.path.join(A.ROOT, "boyde_labs", "kendi")
SRC = os.path.join(OUT, "kaynak")
FOTO = os.path.join(OUT, "fotograf")
WA = "https://wa.me/905464754508"
BLACK, WHITE, ORANGE = S.BLACK, S.WHITE, S.ORANGE
GRAY = 27
U.RGB[GRAY] = (139, 142, 148)                            # GRAY #8B8E94
S.NAMES[GRAY] = "gri"
S.FONTS.update({"sg7": "SpaceGrotesk_700Bold.ttf", "sg6": "SpaceGrotesk_600SemiBold.ttf"})
DARK, LIGHT = S.DARK, S.LIGHT
PHONE = S.PHONE
t, bar = S.t, S.bar


def wa_qr():
    """Çalışan QR: WhatsApp'ımız (2. sürüm, 25 × 25; 34 mm'lik karoda kare 1,17 mm)."""
    import segno
    make = getattr(segno, "make_gercek", segno.make)
    return Q.Entry("whatsapp", "WHATSAPP", WA, "WHATSAPP", qr=make(WA, error="m", micro=False))


def _mark_pairs(_cache=[]):
    """3b işaretinin şekilleri (SVG koordinatı, y aşağı): [(shapely, rol)]; rol main ya da accent."""
    if not _cache:
        import boyde_marka as BM
        orig = BM._parts
        BM._parts = lambda *pairs: [(g, r) for g, r in pairs if not g.is_empty]
        try:
            _cache.extend(BM.mark_n_katman())
        finally:
            BM._parts = orig
    return _cache


def mark(h, x, y, anchor="tl", nozzle=False):
    """İşaret h mm boyunda; (x, y) sol üst (tl), üst orta (tc), orta (c) ya da sol orta (l).
    nozzle: yalnız nozul (katmanlar yok; boyu da yalnız nozulun). Döner ({rol: CrossSection}, en)."""
    pairs = _mark_pairs()
    if nozzle:                                           # sıra: nozulun parçaları, sonra katmanlar (ilki turuncu)
        pairs = pairs[:next(k for k, (_, r) in enumerate(pairs) if r == "accent")]
    x0, y0, x1, y1 = unary_union([g for g, _ in pairs]).bounds
    s = h / (y1 - y0)
    w = (x1 - x0) * s
    if anchor == "c":
        x, y = x - w / 2, y + h / 2
    elif anchor == "tc":
        x = x - w / 2
    elif anchor == "l":
        y = y + h / 2
    out = {}
    for g, r in pairs:
        cs = A.from_shapely(affinity.affine_transform(g, [s, 0, 0, -s, x - x0 * s, y + y0 * s]))
        out[r] = out.get(r, A.empty()) + cs
    return out, w


def word(cap, x, y, align="l"):
    """İki katlı yazı: BOYDE (y büyük harflerin ortası), altında sağa yaslı LABS ve solunda turuncu çizgi.
    Döner (BOYDE, LABS ve çizgi, sınır)."""
    b = t("sg7", "BOYDE", cap, x, y, align, 0.0)
    bx0, by0, bx1, _ = b.bounds()
    c2 = cap * 0.5
    y2 = by0 - cap * 0.26 - c2 / 2
    labs = t("sg6", "LABS", c2, bx1, y2, "r", c2 * 0.3)
    rule = bar(bx0, labs.bounds()[0] - c2 * 0.55, y2, max(1.2, c2 * 0.34))
    return b, labs + rule, (bx0, y2 - c2 / 2, bx1, by0 + cap)


def put_logo(d, add, h, x, y, main, anchor="tl"):
    parts, w = mark(h, x, y, anchor)
    add("işaret", parts["main"], main)
    add("işaret turuncu", parts["accent"], ORANGE)
    return w


def put_word(d, add, cap, x, y, main, align="l"):
    b, rest, box = word(cap, x, y, align)
    add("BOYDE", b, main)
    add("LABS", rest, ORANGE)
    return box


def lockup(d, add, h, x, y, main):
    """İşaret solda (h mm), yazı sağında ortalı; (x, y) sol orta. Döner sağ kenar."""
    w = put_logo(d, add, h, x, y, main, "l")
    cap = h * 0.42
    b, rest, (bx0, by0, bx1, by1) = word(cap, 0, 0)
    dy = y - (by0 + by1) / 2
    dx = x + w + h * 0.22 - bx0
    add("BOYDE", b.translate((dx, dy)), main)
    add("LABS", rest.translate((dx, dy)), ORANGE)
    return bx1 + dx


def layers(d, add, h, x, y_top, x_from, main):
    """İşaretin katmanları (h mm'lik işaret, sol üstü x, y_top) sola, x_from'a kadar uzar: en üstteki turuncu."""
    import boyde_marka as BM
    pairs = _mark_pairs()
    x0, y0, x1, y1 = unary_union([g for g, _ in pairs]).bounds
    s = h / (y1 - y0)
    for yc, th, role in BM.mark_n_katman.rows:
        end = x + ((12.0 + 3.5 if role == "accent" else 42.0) - x0) * s      # mark_n_katman'daki katman uçları
        add(None, bar(x_from, end, y_top - (yc - y0) * s, th * s), ORANGE if role == "accent" else main)


# ---------------------------------------------------------------- 9 × 12 (x −54..54, y ~14..84; kabartma)

X0, X1 = S.X0, S.X1


def b9_klasik():
    """Siyah gövde: solda işaret ve yazı, slogan, telefon; sağda QR."""
    d = S.Design("b9_klasik", DARK)
    lockup(d, d.add, 17.0, X0, 74.0, WHITE)
    d.add("slogan 1", t("sg7", "Katman katman,", 4.6, X0, 54.0, "l", 0.1, 62.0), WHITE)
    d.add("slogan 2", t("sg7", "size özel.", 4.6, X0, 46.5, "l", 0.1, 62.0), ORANGE)
    d.add("SİPARİŞ", t("outfit", "SİPARİŞ · BİLGİ", 3.8, X0, 28.0, "l", 1.0, 62.0), ORANGE)
    d.add("telefon", t("outfit", PHONE, 5.4, X0, 19.0, "l", 0.4, 62.0), WHITE)
    tile = d.qr(wa_qr(), 34.0, 46.0, 36.0)
    d.add("TARA", t("outfit", "WHATSAPP", 3.8, 34.0, tile.bounds()[1] - 5.2, "c", 1.4, 40.0), ORANGE)
    return d


def b9_katman():
    """Siyah gövde, üstte boydan katman şeritleri (en üstteki turuncu), altında yazı; QR sağ altta."""
    d = S.Design("b9_katman", DARK)
    w = mark(20.0, 0, 0)[1]
    put_logo(d, d.add, 20.0, X1 - w, 86.0, WHITE)
    layers(d, d.add, 20.0, X1 - w, 86.0, X0, GRAY)
    put_word(d, d.add, 10.0, X0, 55.0, WHITE)
    d.add("hizmet", t("outfit", "QR'LI İSİMLİK", 4.0, X0, 33.0, "l", 0.8, 56.0), WHITE)
    d.add("hizmet 2", t("outfit", "3D BASKI", 4.0, X0, 26.0, "l", 0.8, 56.0), ORANGE)
    d.add("telefon", t("outfit", PHONE, 5.0, X0, 17.0, "l", 0.4, 56.0), WHITE)
    d.qr(wa_qr(), 36.0, 37.0, 32.0)
    return d


def b9_beyaz():
    """Beyaz gövde, siyah yazı, turuncu çizgi; QR turuncu çerçeveli."""
    d = S.Design("b9_beyaz", LIGHT)
    lockup(d, d.add, 16.0, X0, 74.0, BLACK)
    d.add(None, bar(X0, X0 + 18.0, 59.0, 1.4), ORANGE)
    d.add("hizmet 1", t("outfit", "QR'LI İSİMLİK", 4.2, X0, 50.0, "l", 0.6, 56.0), BLACK)
    d.add("hizmet 2", t("outfit", "DİJİTAL KARTVİZİT", 4.2, X0, 43.0, "l", 0.6, 56.0), BLACK)
    d.add("hizmet 3", t("outfit", "3D BASKI", 4.2, X0, 36.0, "l", 0.6, 56.0), ORANGE)
    d.add("telefon", t("outfit", PHONE, 5.2, X0, 19.0, "l", 0.4, 56.0), BLACK)
    tile = d.qr(wa_qr(), 33.0, 46.0, 34.0, frame=ORANGE)
    d.add("TARA", t("outfit", "TARA · YAZ", 3.8, 33.0, tile.bounds()[1] - 7.0, "c", 1.2, 40.0), BLACK)
    return d


def b9_simge():
    """Siyah gövde, solda büyük işaret; sağda QR; altta yazı ve telefon."""
    d = S.Design("b9_simge", DARK)
    put_logo(d, d.add, 38.0, -31.0, 65.0, WHITE, "c")
    put_word(d, d.add, 7.4, X0, 37.0, WHITE)
    d.add("telefon", t("outfit", PHONE, 5.0, X0, 18.0, "l", 0.4, 56.0), WHITE)
    tile = d.qr(wa_qr(), 34.0, 52.0, 36.0)
    d.add("TARA", t("outfit", "TARA", 4.2, 34.0, tile.bounds()[1] - 5.4, "c", 1.8, 40.0), ORANGE)
    return d


def b9_nozul():
    """Siyah gövde: sağ üstte nozul, bastığı turuncu çizgi yazının altından boydan geçer."""
    d = S.Design("b9_nozul", DARK)
    parts, w = mark(17.0, X1 - 15.0, 86.0, "tc", nozzle=True)
    d.add("nozul", parts["main"], WHITE)
    d.add(None, bar(X0, X1 - 15.0 + 1.0, 66.6, 2.6), ORANGE)              # nozulun bastığı çizgi
    d.add("BOYDE LABS", t("sg7", "BOYDE LABS", 8.4, X0, 75.0, "l", 0.3, 76.0), WHITE)
    d.add("slogan", t("sg7", "Katman katman, size özel.", 4.0, X0, 54.0, "l", 0.1, 66.0), WHITE)
    d.add("telefon", t("outfit", PHONE, 5.2, X0, 19.0, "l", 0.4, 56.0), WHITE)
    d.add("SİPARİŞ", t("outfit", "SİPARİŞ İÇİN TARA", 3.6, X0, 28.0, "l", 0.9, 56.0), ORANGE)
    d.qr(wa_qr(), 36.0, 30.5, 30.0)
    return d


def b9_slogan():
    """Beyaz gövde: büyük slogan iki satır, küçük işaret ve yazı; QR sağda."""
    d = S.Design("b9_slogan", LIGHT)
    d.add("slogan 1", t("sg7", "Katman", 9.0, X0, 77.0, "l", 0.0, 60.0), BLACK)
    d.add("slogan 2", t("sg7", "katman,", 9.0, X0, 64.0, "l", 0.0, 60.0), BLACK)
    d.add("slogan 3", t("sg7", "size özel.", 9.0, X0, 51.0, "l", 0.0, 60.0), ORANGE)
    lockup(d, d.add, 13.0, X0, 33.0, BLACK)
    d.add("telefon", t("outfit", PHONE, 4.8, X0, 18.0, "l", 0.4, 56.0), BLACK)
    tile = d.qr(wa_qr(), 36.0, 46.0, 32.0)
    d.add("TARA", t("outfit", "WHATSAPP", 3.6, 36.0, tile.bounds()[1] - 5.0, "c", 1.2, 36.0), ORANGE)
    return d


def b9_ortali():
    """Siyah gövde, QR solda; sağ sütunda işaret, yazı ve üç adım."""
    d = S.Design("b9_ortali", DARK)
    tile = d.qr(wa_qr(), -33.0, 48.0, 38.0)
    d.add("TARA", t("outfit", "TARA", 4.4, -33.0, tile.bounds()[1] - 5.6, "c", 1.8, 40.0), ORANGE)
    cx = 27.0
    put_logo(d, d.add, 18.0, cx, 84.0, WHITE, "tc")
    put_word(d, d.add, 7.6, cx, 56.0, WHITE, "c")
    for k, s in enumerate(("TARA", "YAZ", "SİPARİŞ VER")):
        d.add(f"adım {k}", t("outfit", f"{k + 1} · {s}", 3.8, 6.0, 39.0 - k * 6.6, "l", 0.6, 48.0),
              ORANGE if k == 2 else WHITE)
    d.add("telefon", t("outfit", PHONE, 4.4, cx, 15.5, "c", 0.3, 48.0), WHITE)
    return d


def b9_bant():
    """Beyaz gövde, üstte turuncu bant: içinde işaret ve BOYDE LABS oyuk (gövde rengi görünür)."""
    d = S.Design("b9_bant", LIGHT)
    band = A.rrect(110.0, 24.0, 4.0, 0.0, 72.0)
    parts, w = mark(15.0, -49.0, 72.0, "l")
    wtxt = t("sg7", "BOYDE LABS", 8.4, -49.0 + w + 4.0, 72.0, "l", 0.4, 74.0)
    cut = A.union(parts["main"], parts["accent"], wtxt)
    d.lines["bant yazısı"] = wtxt
    d.add(None, band - cut.offset(0.0, S.J), ORANGE)
    d.add("hizmet 1", t("outfit", "QR'LI İSİMLİK", 4.4, X0, 50.0, "l", 0.6, 56.0), BLACK)
    d.add("hizmet 2", t("outfit", "3D BASKI ATÖLYESİ", 4.4, X0, 42.5, "l", 0.6, 56.0), BLACK)
    d.add("SİPARİŞ", t("outfit", "SİPARİŞ · BİLGİ", 3.8, X0, 28.0, "l", 1.0, 56.0), ORANGE)
    d.add("telefon", t("outfit", PHONE, 5.2, X0, 19.0, "l", 0.4, 56.0), BLACK)
    d.qr(wa_qr(), 36.0, 37.0, 32.0)
    return d


def b9_cerceve():
    """Beyaz gövde, kenarda turuncu çerçeve; ortada işaret, yazı ve QR yan yana."""
    d = S.Design("b9_cerceve", LIGHT)
    ring = A.rrect(110.0, 76.0, 6.0, 0.0, 50.0) - A.rrect(106.4, 72.4, 4.4, 0.0, 50.0)
    d.add(None, ring, ORANGE)
    put_logo(d, d.add, 16.0, -46.0, 80.0, BLACK)
    put_word(d, d.add, 8.0, -46.0, 54.0, BLACK)
    d.add("slogan", t("sg7", "size özel.", 4.4, -46.0, 33.0, "l", 0.1, 50.0), ORANGE)
    d.add("telefon", t("outfit", PHONE, 4.6, -46.0, 22.0, "l", 0.3, 50.0), BLACK)
    tile = d.qr(wa_qr(), 29.0, 52.0, 34.0)
    d.add("TARA", t("outfit", "TARA", 4.0, 29.0, tile.bounds()[1] - 5.2, "c", 1.8, 36.0), ORANGE)
    return d


def b9_gri():
    """Siyah gövde, gri ve turuncu: işaret gri katmanlı, yazı beyaz; altta gri bilgi satırı."""
    d = S.Design("b9_gri", DARK)
    put_logo(d, d.add, 20.0, X0, 84.0, GRAY)
    put_word(d, d.add, 9.0, X0, 52.0, WHITE)
    d.add("hizmet", t("outfit", "QR'LI İSİMLİK · 3D BASKI", 3.6, X0, 29.0, "l", 0.4, 62.0), GRAY)
    d.add("telefon", t("outfit", PHONE, 5.2, X0, 19.0, "l", 0.4, 62.0), WHITE)
    tile = d.qr(wa_qr(), 34.0, 52.0, 36.0)
    d.add("TARA", t("outfit", "WHATSAPP", 3.8, 34.0, tile.bounds()[1] - 5.2, "c", 1.4, 40.0), ORANGE)
    return d


# ---------------------------------------------------------------- 10 × 20 (x −88..88, y ~14..92; dolgu)

def p_kurumsal():
    """Beyaz: solda büyük işaret ve yazı, dikey çizgi, sağda QR."""
    d = S.Design("p_kurumsal", LIGHT)
    lockup(d, d.flat, 34.0, -86.0, 62.0, BLACK)
    d.flat("slogan", t("sg7", "Katman katman, size özel.", 5.4, -86.0, 34.0, "l", 0.1, 110.0), BLACK)
    d.flat("telefon", t("mont6", PHONE, 5.2, -86.0, 21.0, "l", 0.4, 110.0), ORANGE)
    d.flat(None, A.rect(36.4, 24.0, 37.6, 86.0), GRAY)
    tile = d.qr(wa_qr(), 64.0, 60.0, 34.0)
    d.flat("TARA", t("mont6", "WHATSAPP", 3.6, 64.0, tile.bounds()[1] - 5.2, "c", 1.6), ORANGE)
    return d


def p_siyah():
    """Siyah gövde: beyaz yazı, turuncu katman; QR beyaz karo."""
    d = S.Design("p_siyah", DARK)
    put_logo(d, d.flat, 30.0, -86.0, 90.0, WHITE)
    put_word(d, d.flat, 13.0, -48.0, 79.0, WHITE)
    d.flat("hizmet", t("mont6", "QR'LI İSİMLİK · 3D BASKI", 4.6, -86.0, 40.0, "l", 1.0, 116.0), GRAY)
    d.flat("telefon", t("mont6", PHONE, 6.0, -86.0, 25.0, "l", 0.4, 110.0), WHITE)
    tile = d.qr(wa_qr(), 66.0, 60.0, 34.0)
    d.flat("TARA", t("mont6", "TARA · YAZ", 3.8, 66.0, tile.bounds()[1] - 5.2, "c", 1.4), ORANGE)
    return d


def p_bant():
    """Beyaz: altta siyah bant, içinde hizmetler ve telefon oyuk; üstte işaret ve yazı; QR sağ üstte."""
    d = S.Design("p_bant", LIGHT)
    band = A.rrect(184.0, 21.0, 4.0, 0.0, 23.5)
    left = t("mont", "QR'LI İSİMLİK · 3D BASKI", 4.4, -84.0, 23.5, "l", 1.0, 100.0)
    tel = t("mont6", PHONE, 5.0, 84.0, 23.5, "r", 0.5, 70.0)
    d.lines.update({"bant": left, "telefon": tel})
    d.flat(None, band - left.offset(0.0, S.J) - tel.offset(0.0, S.J), BLACK)
    lockup(d, d.flat, 30.0, -86.0, 66.0, BLACK)
    tile = d.qr(wa_qr(), 66.0, 66.0, 34.0)
    d.flat("TARA", t("mont6", "WHATSAPP", 3.4, 66.0, tile.bounds()[1] - 4.6, "c", 1.4), ORANGE)
    return d


def p_blok():
    """Beyaz: solda turuncu blok, içinde işaret oyuk (beyaz); sağda yazı, slogan, telefon ve QR."""
    d = S.Design("p_blok", LIGHT)
    blk = A.rrect(52.0, 76.0, 5.0, -62.0, 52.0)
    parts, _ = mark(34.0, -62.0, 56.0, "c")
    cut = parts["main"] + parts["accent"]
    d.lines["işaret"] = cut
    d.flat(None, blk - cut.offset(0.0, S.J), ORANGE)
    put_word(d, d.flat, 11.0, -28.0, 78.0, BLACK)
    d.flat("slogan", t("sg7", "Katman katman, size özel.", 4.6, -28.0, 48.0, "l", 0.1, 72.0), BLACK)
    d.flat("hizmet", t("mont6", "QR'lı isimlik · 3D baskı", 4.2, -28.0, 38.0, "l", 0.2, 72.0), GRAY)
    d.flat("telefon", t("mont6", PHONE, 5.2, -28.0, 22.0, "l", 0.4, 72.0), BLACK)
    d.qr(wa_qr(), 68.0, 58.0, 32.0, frame=ORANGE, flat=True)
    return d


def p_buyuk():
    """Siyah gövde: boydan büyük BOYDE, altında turuncu çizgi ve LABS; sağda QR."""
    d = S.Design("p_buyuk", DARK)
    put_word(d, d.flat, 26.0, -86.0, 70.0, WHITE)
    d.flat("telefon", t("mont6", PHONE, 5.4, -86.0, 22.0, "l", 0.4, 110.0), GRAY)
    put_logo(d, d.flat, 15.0, 68.0, 91.0, WHITE, "tc")
    tile = d.qr(wa_qr(), 68.0, 52.0, 32.0)
    d.flat("TARA", t("mont6", "TARA", 3.8, 68.0, tile.bounds()[1] - 5.0, "c", 1.6), ORANGE)
    return d


def p_slogan():
    """Beyaz: büyük slogan iki satır, altında küçük logo ve telefon; QR sağda turuncu çerçeve."""
    d = S.Design("p_slogan", LIGHT)
    d.flat("slogan 1", t("sg7", "Katman katman,", 11.0, -86.0, 78.0, "l", 0.0, 120.0), BLACK)
    d.flat("slogan 2", t("sg7", "size özel.", 11.0, -86.0, 61.0, "l", 0.0, 120.0), ORANGE)
    lockup(d, d.flat, 15.0, -86.0, 35.0, BLACK)
    d.flat("telefon", t("mont6", PHONE, 4.8, -86.0, 17.5, "l", 0.4, 110.0), GRAY)
    d.qr(wa_qr(), 66.0, 56.0, 34.0, frame=ORANGE, flat=True)
    return d


def p_liste():
    """Siyah gövde: üstte işaret ve yazı, altında üç hizmet turuncu numaralı; QR sağda."""
    d = S.Design("p_liste", DARK)
    lockup(d, d.flat, 22.0, -86.0, 80.0, WHITE)
    for k, s in enumerate(("QR'lı masa isimliği", "Kurumsal isimlik ve kartvizit", "Size özel 3D baskı")):
        y = 53.0 - k * 11.0
        d.flat(f"no {k}", t("sg7", f"0{k + 1}", 5.0, -86.0, y, "l", 0.2), ORANGE)
        d.flat(f"hizmet {k}", t("mont6", s, 5.0, -72.0, y, "l", 0.1, 90.0), WHITE)
    d.flat("telefon", t("mont6", PHONE, 4.6, 66.0, 20.0, "c", 0.4, 60.0), GRAY)
    d.qr(wa_qr(), 66.0, 58.0, 34.0)
    return d


def p_cizgi():
    """Beyaz: işaretin katmanları sola doğru boydan uzar (banner gibi); yazı katmanların altında; QR sağda."""
    d = S.Design("p_cizgi", LIGHT)
    put_logo(d, d.flat, 30.0, 6.0, 92.0, BLACK)
    layers(d, d.flat, 30.0, 6.0, 92.0, -86.0, BLACK)
    put_word(d, d.flat, 11.0, -86.0, 46.0, BLACK)
    d.flat("telefon", t("mont6", PHONE, 5.0, -86.0, 20.0, "l", 0.4, 90.0), ORANGE)
    d.qr(wa_qr(), 68.0, 50.0, 32.0)
    return d


def p_resepsiyon():
    """Beyaz: ortada işaret, altında yazı ve "Hoş geldiniz"; iki yanda ince gri çizgi; QR sağda küçük."""
    d = S.Design("p_resepsiyon", LIGHT)
    put_logo(d, d.flat, 26.0, -24.0, 90.0, BLACK, "tc")
    put_word(d, d.flat, 10.0, -24.0, 50.0, BLACK, "c")
    d.flat("hoş geldiniz", t("sg7", "Hoş geldiniz", 6.0, -24.0, 26.0, "c", 0.2, 90.0), ORANGE)
    d.flat(None, A.rect(-86.0, 25.6, -66.0, 26.4), GRAY)
    d.flat(None, A.rect(18.0, 25.6, 38.0, 26.4), GRAY)
    tile = d.qr(wa_qr(), 68.0, 56.0, 32.0)
    d.flat("telefon", t("mont6", PHONE, 4.2, 68.0, tile.bounds()[1] - 5.2, "c", 0.3, 40.0), GRAY)
    return d


def p_kartvizit():
    """Siyah gövde: solda işaret, sağında yazı ve iletişim satırları; QR turuncu çerçeveli."""
    d = S.Design("p_kartvizit", DARK)
    put_logo(d, d.flat, 26.0, -86.0, 88.0, WHITE)
    put_word(d, d.flat, 10.0, -52.0, 80.0, WHITE)
    d.flat("atölye", t("mont6", "Tasarım ve 3D baskı atölyesi", 4.6, -86.0, 50.0, "l", 0.1, 116.0), WHITE)
    d.flat("tel etiketi", t("mont6", "TELEFON · WHATSAPP", 3.4, -86.0, 36.0, "l", 1.4, 80.0), ORANGE)
    d.flat("telefon", t("mont6", PHONE, 6.4, -86.0, 26.0, "l", 0.4, 110.0), WHITE)
    d.qr(wa_qr(), 64.0, 56.0, 34.0, frame=ORANGE, flat=True)
    return d


S9 = {f.__name__: f for f in (b9_klasik, b9_katman, b9_beyaz, b9_simge, b9_nozul, b9_slogan, b9_ortali, b9_bant,
                               b9_cerceve, b9_gri)}
S20 = {f.__name__: f for f in (p_kurumsal, p_siyah, p_bant, p_blok, p_buyuk, p_slogan, p_liste, p_cizgi,
                                p_resepsiyon, p_kartvizit)}
AD = {"b9_klasik": "Klasik", "b9_katman": "Katman şeritleri", "b9_beyaz": "Beyaz", "b9_simge": "Büyük işaret",
      "b9_nozul": "Nozul", "b9_slogan": "Slogan", "b9_ortali": "QR solda", "b9_bant": "Turuncu bant",
      "b9_cerceve": "Çerçeve", "b9_gri": "Gri katman",
      "p_kurumsal": "Kurumsal", "p_siyah": "Siyah", "p_bant": "Alt bant", "p_blok": "Turuncu blok",
      "p_buyuk": "Büyük yazı", "p_slogan": "Slogan", "p_liste": "Hizmetler", "p_cizgi": "Uzayan katmanlar",
      "p_resepsiyon": "Resepsiyon", "p_kartvizit": "Kartvizit"}


def build(key):
    """Döner: boyde_urunler.Parcalar (boyde_sektor.build gibi)."""
    import uzar_isimlik_baski as B
    if key in S9:
        d = S9[key]()
        stand, mount = B.stand()
        p = U.Parcalar(S.solids(d), stand, BLACK, mount)
    else:
        import paloma_isimlik_baski as PB                      # 200 × 100 × 5 (modül ölçüleri değişir)
        d = S20[key]()
        stand, mount = B.stand(length=PB.STAND_LEN)
        p = U.Parcalar(S.solids_20(d), stand, d.sc["body"], mount)
    p.design = d
    return p


def export(key):
    """Kendi sürecinde (10 × 20 modül ölçülerini değiştirir): npz, düz görünüş; QR WhatsApp'ımızı okutmalı."""
    import uzar_isimlik_baski as B
    p = build(key)
    top = U.top_view(p.panel)
    reads = U.qr_reads(top)
    assert reads and set(reads) == {WA}, f"{key}: QR okunmadı ya da yanlış: {reads!r}"
    z0, y0 = p.mount
    parts = B.assembled(p.panel, z0, y0) + [("Sehpa", p.stand, p.stand_col)]
    arrays = {}
    for i, (name, man, col) in enumerate(parts):
        V, T = A.mesh_arrays(man)
        arrays[f"v{i}"], arrays[f"f{i}"] = V.astype(np.float32), T.astype(np.int32)
    meta = [{"ad": n, "renk": list(U.RGB[c]), "metal": False, "panel": n != "Sehpa"} for n, _, c in parts]
    os.makedirs(SRC, exist_ok=True)
    np.savez_compressed(os.path.join(SRC, f"{key}.npz"), meta=json.dumps(meta, ensure_ascii=False), **arrays)
    top.crop(top.getbbox()).save(os.path.join(SRC, f"{key}_duz.png"), optimize=True)
    return key, S.report(p.design)


def photos(keys, samples=32):
    """Stüdyo fotoğrafı (boyde_urun_foto): beyaz gövde logodaki siyahta, siyah gövde beyaz fonda."""
    import boyde_urun_foto as F
    F.SRC, F.OUT = SRC, FOTO
    for key in keys:
        F.render(key, ["studyo"], samples)


def presentation():
    """Sunum: her ölçü için kare görsel (10 model fotoğrafı, numaralı) ve iki sayfalık PDF."""
    import boyde_katalog as K
    import boyde_marka as BM
    cats = (("9x12", "9 × 12 cm", "QR'lı masa isimliği", list(S9)), ("10x20", "10 × 20 cm", "Kurumsal isimlik",
                                                                          list(S20)))
    pages = []
    with BM.painter() as P:
        for cat, olcu, ad, keys in cats:
            cells = "".join(f"""<div style="position:relative;border-radius:16px;overflow:hidden;background:#fff">
              <img src="{K.uri(os.path.join(FOTO, f'{k}_studyo.jpg'), 420)}" style="width:100%;aspect-ratio:1;
                object-fit:cover;display:block">
              <span class="chip code" style="position:absolute;left:10px;top:10px;background:{K.ORANGE};color:#fff;
                font-size:15px;padding:5px 10px">B{i:02d}</span>
              <span class="chip" style="position:absolute;left:10px;bottom:10px;font-size:14px;padding:4px 10px;
                background:rgba(244,241,234,.92);color:{K.INK}">{AD[k]}</span></div>""" for i, k in enumerate(keys, 1))
            cells += f"""<div style="border-radius:16px;background:{K.INK};color:{K.PAPER};padding:18px;
              display:flex;flex-direction:column;justify-content:space-between">{K.logo("koyu", 200, 40)}
              <p style="font-size:15px;line-height:1.4;color:rgba(244,241,234,.75)">QR'lar çalışır:
              WhatsApp'ımızı açar.</p></div>
              <div style="border-radius:16px;background:{K.ORANGE};color:#fff;padding:18px;display:flex;
              flex-direction:column;justify-content:flex-end"><p class="u" style="font-size:20px;line-height:1.15">
              Hangisi?</p><p style="margin-top:6px;font-size:15px;line-height:1.35">Beğendiğimizi basıyoruz.</p></div>"""
            body = f"""<div class="pg" style="position:relative;width:1200px;height:1200px;background:{K.PAPER};
              padding:56px 60px;color:{K.INK}">
              <div style="display:flex;justify-content:space-between;align-items:flex-end">
                <div><p class="k">BOYDE LABS · KENDİ İSİMLİĞİMİZ · {olcu.upper()}</p>
                <h2 class="u" style="margin-top:10px;font-size:40px">{ad}: 10 model</h2></div>
                {K.logo("acik", 250, 50)}</div>
              <div style="margin-top:40px;display:grid;grid-template-columns:repeat(4,1fr);gap:16px">{cells}</div>
              <p style="position:absolute;left:60px;right:60px;bottom:44px;font-size:18px;color:#55575c">
                Yazılar ve işaret 3D baskıda {'2 mm kabartma' if cat == '9x12' else 'yüzeyle aynı hizada renkli'};
                QR WhatsApp'ımızı açar (0546 475 45 08).</p></div>"""
            pages.append(body)
            K.sq(P, body.replace('class="pg" ', ""), os.path.join(OUT, f"sunum_{cat}.jpg"))
        P.pdf(pages, 1200, 1200, os.path.join(OUT, "sunum.pdf"), css=K.CSS + ".pg{page-break-after:always}")


def main():
    import multiprocessing as mp
    args = sys.argv[1:]
    keys = [k for k in args if not k.startswith("-")] or list(S9) + list(S20)
    if "--foto" in args:
        photos(keys)
        return
    if "--sunum" in args:
        presentation()
        return
    with mp.get_context("spawn").Pool(4, maxtasksperchild=1) as pool:
        for key, rep in pool.imap_unordered(export, keys):
            print(f"{key:14s} QR → WhatsApp ✓", flush=True)
            if "--rapor" in args:
                print("   " + " | ".join(rep), flush=True)


if __name__ == "__main__":
    import boyde_kendi                                   # tek modül nesnesi (boyde_urunler gibi)
    boyde_kendi.main()
