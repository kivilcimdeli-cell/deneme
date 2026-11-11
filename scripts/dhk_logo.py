"""DHK Tapu Takip logosu: isimlikte basılabilir yeniden çizim (çatı + DHK), orijinalin harf stiliyle.

Müşterinin logosu (WhatsApp görseli, 190 × 50 piksel): altın rengi, ince çizgili çatı (sağda baca) ve altında ince,
yüksek kontrastlı serif (Didone) DHK harfleri; yanında TAPU TAKİP. Bu boyutta izlenince kenarlar tırtıklı çıkar.

Burada aynı biçim büyük çizilir. Müşteri harf stilinin orijinaldeki gibi olmasını istedi (ilk çizim, Marcellus'un her
yandan kalınlaştırılmışı, küt ve kalın duruyordu):
- **Harfler:** Playfair Display (serifli Didone; K'nin bacağı orijinaldeki gibi uzun, kıvrık), %70'e daraltılmış, sıkı
  aralıklı. Black kesimin dik gövdeleri yatayda inceltilir (orijinal ince harfli); yatay ince çizgiler (serifler, H'nin
  köprüsü, D'nin kavisi) dikeyde biraz kalınlaştırılır: en ince yer büyük harf boyunun ~0,07'si.
- **Çatı:** orijinaldeki gibi ince (büyük harf boyunun 0,085'i), harflerin biraz dışına taşan saçak, sağ eğimde baca.
- TAPU TAKİP logoya katılmaz: isimlikte kurum satırı olarak yazılır.

**Boyut:** bu incelikte logo isimlikte en az ~44 mm genişlikte basılmalı (16–17 mm harf boyu: en ince yer 1,2 mm).
2 cm'lik logo kutularında çatı ve ince çizgiler baskıda kaybolur; uygulama bu düzenleri logo kaybı denetimiyle eler,
"Büyük logo", "Logo üstte", "Logo ortada" düzenleri logoyu bu boyda basar (atolye/tasarim/isimlik20.py).

Çıktı: dhk_tapu_isimlik/logo/dhk_logo.png (beyaz zeminde siyah, uygulamanın logo izleyicisi için, uzun kenar 1800 piksel)
ve dhk_logo_altin.png (önizleme: siyah zeminde altın).
Kullanım: python3 scripts/dhk_logo.py
"""
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(KOK, "dhk_tapu_isimlik", "logo")
FONT = os.path.join(KOK, "scripts", "fonts", "PlayfairDisplay-Black.ttf")

CAP = 600                      # büyük harf boyu (piksel)
DAR = 0.70                     # harflerin daraltılması (orijinaldeki gibi uzun, dar)
INCELT = 0.04                  # dik gövdeleri her yandan inceltme (daraltmadan önce, büyük harf boyunun oranı)
KOL = 0.075                    # K'nin kolu (büyük harf boyunun oranı; daraltmadan önce)
INCE = 0.06                    # yatay ince çizgileri dikeyde kalınlaştırma (büyük harf boyunun oranı)
ARA = 0.06                     # harfler arası (büyük harf boyunun oranı): orijinaldeki gibi sıkı
CATI_H = 0.60                  # çatının harflerin üstündeki yüksekliği (büyük harf boyunun oranı)
TASMA = 0.08                   # çatı saçağının harflerin dışına taşması (büyük harf boyunun oranı)
CIZGI = 0.085                  # çatı çizgisi (büyük harf boyunun oranı): orijinaldeki gibi ince


def _k_kolu(m):
    """K'nin kolu: gövdenin sağ kenarında, harfin ~%58'inden sağ üstteki serifin ortasına uzanan çizgi."""
    h = m.shape[0]
    satir = np.nonzero(m[int(h * 0.75)])[0]               # bacağın altında gövde tek başına
    sag = satir[0]
    while sag + 1 < m.shape[1] and m[int(h * 0.75), sag + 1]:
        sag += 1
    ust = np.nonzero(m[int(h * 0.03)])[0]
    ust = ust[ust > sag + h * 0.1]                        # sağ üstteki serif
    return (sag - 2, int(h * 0.6)), (int(ust.mean()), int(h * 0.05))


def _harf(ch):
    f = ImageFont.truetype(FONT, int(CAP * 1.6))
    im = Image.new("L", (int(CAP * 3), int(CAP * 2.4)), 0)
    ImageDraw.Draw(im).text((CAP // 2, CAP // 4), ch, font=f, fill=255)
    im = im.crop(im.getbbox())
    k = CAP / im.height                                  # büyük harf boyu tam CAP
    m = (np.asarray(im.resize((int(im.width * k), CAP), Image.LANCZOS)) > 127).astype(np.uint8)
    e = int(round(INCELT * CAP))                         # dik gövdeler incelir (yalnız yatayda aşındırma)
    kol = _k_kolu(m) if ch == "K" else None
    if e:
        m = np.pad(m, ((0, 0), (e, e)))
        m = cv2.erode(m, np.ones((1, 2 * e + 1), np.uint8))
    if kol is not None:                                  # K'nin ince kolu aşınmada kaybolur: yeniden çizilir
        (x0, y0), (x1, y1) = kol
        cv2.line(m, (x0 + e, y0), (x1 + e, y1), 1, max(3, int(KOL * CAP)), cv2.LINE_8)
    # yatay ince çizgiler kalınlaşır: yalnız dikeyde genişletme (gövdelerin eni değişmez, boyları sonra CAP'e döner)
    r = int(round(INCE * CAP * 0.56))
    m = np.pad(m, ((r + 2, r + 2), (2, 2)))
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (max(3, r // 4) | 1, 2 * r + 1)))
    ys, xs = np.nonzero(m)
    m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    m = cv2.resize(m * 255, (max(1, int(m.shape[1] * CAP / m.shape[0] * DAR)), CAP), interpolation=cv2.INTER_AREA)
    return (m > 127).astype(np.uint8)


def harfler():
    """D, H, K tek tek, aralarında ARA (orijinaldeki gibi sıkı)."""
    parca = [_harf(ch) for ch in "DHK"]
    ara = int(ARA * CAP)
    m = np.zeros((CAP, sum(p.shape[1] for p in parca) + ara * 2), np.uint8)
    x = 0
    for p in parca:
        m[:, x:x + p.shape[1]] |= p
        x += p.shape[1] + ara
    return m


def logo():
    h = harfler()
    hh, hw = h.shape
    pay = int(CAP * 0.4)
    cati = int(CAP * CATI_H)
    c = max(3, int(CAP * CIZGI))
    t = int(CAP * TASMA)
    W, H = hw + 2 * pay, hh + cati + c + 2 * pay
    m = np.zeros((H, W), np.uint8)
    y0 = pay + cati + c                                  # harflerin üstü
    m[y0:y0 + hh, pay:pay + hw] |= h
    # saçaklar harflerin üstüne oturur (çizgi harfin üst kenarına değer, üstünden geçmez: K'nin kolu kaybolmasın)
    sol, sag, tepe = (pay - t, y0 - c // 2), (pay + hw + t, y0 - c // 2), (pay + hw // 2, pay + c // 2 - c)
    cv2.line(m, sol, tepe, 1, c, cv2.LINE_AA)
    cv2.line(m, tepe, sag, 1, c, cv2.LINE_AA)
    cv2.circle(m, tepe, c // 2, 1, -1, cv2.LINE_AA)    # tepe yuvarlak birleşsin
    # baca: sağ eğimin üstünde, tepeden eğimin %62'sinde (orijinaldeki gibi saçağa yakın)
    k = 0.62
    bx = int(tepe[0] + (sag[0] - tepe[0]) * k)
    by = int(tepe[1] + (sag[1] - tepe[1]) * k)
    bw, bh = int(c * 1.25), int(CAP * 0.30)
    m[by - bh:by, bx - bw // 2:bx + bw // 2] = 1
    return m


def main():
    os.makedirs(OUT, exist_ok=True)
    m = logo()
    ys, xs = np.nonzero(m)
    m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = 1800 / max(m.shape)
    m = cv2.resize(m * 255, (int(m.shape[1] * k), int(m.shape[0] * k)), interpolation=cv2.INTER_AREA)
    pad = 60
    beyaz = np.full((m.shape[0] + 2 * pad, m.shape[1] + 2 * pad), 255, np.uint8)
    beyaz[pad:-pad, pad:-pad] = 255 - m
    Image.fromarray(beyaz).save(os.path.join(OUT, "dhk_logo.png"))
    altin = Image.new("RGB", (beyaz.shape[1], beyaz.shape[0]), (18, 18, 20))
    altin.paste(Image.new("RGB", altin.size, (214, 176, 98)), (0, 0), Image.fromarray(255 - beyaz))
    altin.save(os.path.join(OUT, "dhk_logo_altin.png"))
    print("yazıldı:", os.path.join(OUT, "dhk_logo.png"), beyaz.shape[::-1])


if __name__ == "__main__":
    main()
