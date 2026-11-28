"""Müşteriye giden katalog: A4 sayfalar (JPG, WhatsApp'tan gönderilir) ve PDF.

BOYDE LABS kimliğiyle (logo, palet: mürekkep #121316, kâğıt #F4F1EA, turuncu #FF5A1F, kum #E6E0D4, gri #8B8E94).
Her tasarım kartında büyük kod (M01, M02...): müşteri beğendiğinin kodunu yazar, kod uygulamadan seçilir.
"""
import os

from PIL import Image, ImageDraw, ImageFont

from .ortak import A, tr_upper

INK, PAPER, ORANGE, SAND, GRAY, CHAR = (18, 19, 22), (244, 241, 234), (255, 90, 31), (230, 224, 212), \
    (139, 142, 148), (28, 29, 33)
W, H = 1654, 2339                                       # A4, 200 dpi
LOGO = os.path.join(A.ROOT, "boyde_labs", "logo", "boyde_yatay_koyu.png")


def font(n, kalin=700):
    ad = {700: "SpaceGrotesk_700Bold.ttf", 600: "SpaceGrotesk_600SemiBold.ttf", 500: "SpaceGrotesk_500Medium.ttf",
          400: "SpaceGrotesk_400Regular.ttf"}[kalin]
    return ImageFont.truetype(os.path.join(A.FONT_DIR, ad), n)


def sar(dr, metin, f, genislik):
    """Metni genişliğe göre satırlara böler."""
    out, cur = [], ""
    for w in metin.split():
        t = f"{cur} {w}".strip()
        if cur and dr.textlength(t, font=f) > genislik:
            out.append(cur)
            cur = w
        else:
            cur = t
    return out + ([cur] if cur else [])


def _sigdir(dr, metin, n, kalin, genislik, en_az=22):
    while n > en_az and dr.textlength(metin, font=font(n, kalin)) > genislik:
        n -= 2
    return font(n, kalin)


def _baslik(im, dr, urun, musteri, alt):
    dr.rectangle((0, 0, W, 250), fill=INK)
    if os.path.exists(LOGO):
        logo = Image.open(LOGO).convert("RGBA")
        logo.thumbnail((360, 140), Image.LANCZOS)
        im.paste(logo, (70, (250 - logo.height) // 2), logo)
    x1 = W - 70
    f = font(26, 600)
    urun = tr_upper(urun)
    dr.text((x1 - dr.textlength(urun, font=f), 52), urun, font=f, fill=ORANGE)
    f = _sigdir(dr, musteri, 54, 700, W - 560)
    dr.text((x1 - dr.textlength(musteri, font=f), 92), musteri, font=f, fill=PAPER)
    f = font(24, 400)
    dr.text((x1 - dr.textlength(alt, font=f), 170), alt, font=f, fill=(190, 186, 178))
    dr.rectangle((0, 246, W, 252), fill=ORANGE)


def _alt(dr, sol, sag):
    dr.rectangle((0, H - 120, W, H), fill=INK)
    f = _sigdir(dr, sol, 30, 600, W - 620)
    dr.text((70, H - 78), sol, font=f, fill=PAPER)
    f = font(26, 600)
    dr.text((W - 70 - dr.textlength(sag, font=f), H - 76), sag, font=f, fill=ORANGE)


def _kart(im, dr, x0, y0, w, h, kod, ad, resim):
    dr.rounded_rectangle((x0, y0, x0 + w, y0 + h), 26, fill=(255, 255, 255), outline=SAND, width=2)
    f = font(40, 700)
    kw = dr.textlength(kod, font=f) + 44
    dr.rounded_rectangle((x0 + 22, y0 + 22, x0 + 22 + kw, y0 + 86), 16, fill=ORANGE)
    dr.text((x0 + 44, y0 + 30), kod, font=f, fill=(255, 255, 255))
    fa = font(22, 500)
    lines = sar(dr, ad, fa, w - kw - 80)[:2]
    for i, line in enumerate(lines):
        dr.text((x0 + kw + 44, y0 + 30 + i * 28 + (14 if len(lines) == 1 else 0)), line, font=fa, fill=(96, 98, 106))
    img = A.fit_into(resim, w - 50, h - 130)
    im.paste(img, (x0 + (w - img.width) // 2, y0 + 108 + (h - 130 - img.height) // 2), img)


def _bilgi(dr, x0, y0, w, h, baslik, maddeler):
    dr.rounded_rectangle((x0, y0, x0 + w, y0 + h), 26, fill=(255, 255, 255), outline=SAND, width=2)
    dr.text((x0 + 40, y0 + 34), baslik, font=font(34, 700), fill=INK)
    f = font(25, 400)
    y = y0 + 100
    for m in maddeler:
        for i, line in enumerate(sar(dr, m, f, w - 120)):
            if i == 0:
                dr.ellipse((x0 + 42, y + 11, x0 + 56, y + 25), fill=ORANGE)
            dr.text((x0 + 74, y), line, font=f, fill=(70, 72, 78))
            y += 36
        y += 12
        if y > y0 + h - 40:
            break


def yap(klasor, urun, musteri, no, tasarimlar, giris, bilgi=None, sutun=2, satir=3, alt_not=None):
    """tasarimlar: [(kod, ad, RGBA görüntü)]. bilgi: (başlık, [madde]): son sayfada boş kalan yere ürün kartı.
    Döner (pdf yolu, [sayfa jpg yolları])."""
    os.makedirs(klasor, exist_ok=True)
    adet = sutun * satir
    gruplar = [tasarimlar[i:i + adet] for i in range(0, len(tasarimlar), adet)] or [[]]
    if bilgi and len(gruplar[-1]) > adet - sutun:          # ürün kartına yer kalmadı: ayrı sayfa
        gruplar.append([])
    top, gap, mx = 380, 36, 60
    cw = (W - 2 * mx - (sutun - 1) * gap) // sutun
    ch = (H - top - 170 - (satir - 1) * gap) // satir
    sayfalar, yollar = [], []
    for p, grup in enumerate(gruplar):
        im = Image.new("RGB", (W, H), PAPER)
        dr = ImageDraw.Draw(im)
        _baslik(im, dr, urun, musteri, f"Tasarım önerileri · {no}. katalog · sayfa {p + 1}/{len(gruplar)}")
        y = 284
        for line in sar(dr, giris, font(26, 400), W - 2 * mx)[:2]:
            dr.text((mx, y), line, font=font(26, 400), fill=INK)
            y += 38
        for i, (kod, ad, resim) in enumerate(grup):
            x0, y0 = mx + (i % sutun) * (cw + gap), top + (i // sutun) * (ch + gap)
            _kart(im, dr, x0, y0, cw, ch, kod, ad, resim)
        if bilgi and p == len(gruplar) - 1:
            sira = (len(grup) + sutun - 1) // sutun
            y0 = top + sira * (ch + gap)
            _bilgi(dr, mx, y0, W - 2 * mx, H - 150 - y0, *bilgi)
        _alt(dr, alt_not or "Beğendiğiniz tasarımın kodunu (ör. M03) yazmanız yeterli.", "BOYDE LABS · shopier.com/boyde")
        yol = os.path.join(klasor, f"sayfa_{p + 1}.jpg")
        im.save(yol, "JPEG", quality=88, optimize=True)
        sayfalar.append(im)
        yollar.append(yol)
    pdf = os.path.join(klasor, "katalog.pdf")
    sayfalar[0].save(pdf, save_all=True, append_images=sayfalar[1:], resolution=200)
    return pdf, yollar
