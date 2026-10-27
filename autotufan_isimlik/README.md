# AUTO TUFAN – Kaporta & Boya: QR'lı masa isimliği önerileri

Müşteriye gönderilecek katalog: **`musteri_1.jpg`** (1–6), **`musteri_2.jpg`** (7–10); PNG'leri ve ikisi birlikte
**`musteri_katalog.pdf`**. Ayrıntılı sayfalar: `<numara>_<ad>.png` (önden, masada, yandan).

- **Renkler:** hepsi siyah zemin, altın ve beyaz kabartma yazı ve şekil.
- **Logo:** müşterinin logosundan.
  - Fırça T görselden vektöre çevrildi (`logo/`, `scripts/autotufan_logo.py`) ve altın basılıyor.
  - "Auto Tufan" Poppins SemiBold; logodaki yazıyla birebir örtüşüyor.
  - "KAPORTA & BOYA" Poppins Bold. Logodaki Medium, 2 mm kabartmada fazla ince kalıyor.
- **Şekiller işe göre:**
  1 Klasik logo · 2 Ortalı · 3 Araba · 4 Boya tabancası · 5 Fırça darbesi (oyma Auto Tufan) · 6 Altın çerçeve ·
  7 Kalkan · 8 Boya damlaları · 9 Parlama · 10 Alt bant (oyma telefon).
- **İçerik:** Auto Tufan, KAPORTA & BOYA, HASAR ONARIM, ANTALYA, telefon **0546 475 45 08**, QR (TARA).
- **QR:** işletme sayfası `https://deneme123.qrsistem.workers.dev` (`bilgiler.json` → `sayfa_url`).
  - Ortak Cloudflare hesabında (`qrsistem`) Worker adı tam olarak `deneme123` olmalı.
  - Sondaki `/` olmadan adres 3. sürüme (29 × 29) sığıyor; 30–34 mm'de kare 0,91–1,03 mm.
  - Hepsi görüntüden ve baskı hatası benzetiminden okundu.
- **Yapı:** Uzar, İNCE, Çalık ve Soylu isimlikleriyle aynı.
  - 120 × 90 mm, köşeler R8, siyah gövde 1 cm, 15° eğik sehpa.
  - Yazılar ve şekiller 2 mm kabartma.
  - QR yüzeyle aynı hizada beyaz karo.
- **Kontroller:**
  - Küçük yazılar en az 4,6 mm büyük harf; 0,8 mm'den ince çizgi %6'dan az.
  - Harf içi boşluklar en az 0,6 mm.
  - Satırlar arası ve kenarlara en az 2 mm.
  - Oyma telefonda rakam araları en az 1 mm altın.
- **Filament:** altın için Bambu PLA Basic Gold (#E4BD68) ya da benzeri.

```bash
python3 scripts/autotufan_logo.py <logo_görseli>   # bir kez: fırça T (logo/)
python3 scripts/autotufan_isimlik.py               # 10 öneri ve katalog (4 süreçte)
python3 scripts/autotufan_isimlik.py kalkan        # yalnız eşleşen tasarımlar
python3 scripts/autotufan_isimlik.py katalog       # yalnız katalog sayfaları
```
