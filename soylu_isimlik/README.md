# SOYLU OTO LASTİK – QR'lı tezgâh isimliği önerileri

Müşteriye gönderilecek katalog: **`musteri_1.jpg`** (1–6), **`musteri_2.jpg`** (7–10); PNG'leri ve ikisi birlikte
**`musteri_katalog.pdf`**. Ayrıntılı sayfalar: `<numara>_<ad>.png` (önden, tezgâhta, yandan).

- Kurumsal: siyah zemin, beyaz ve kırmızı; az ve düzenli öğe, ince kırmızı çizgiler, geniş harf aralıkları.
- Her birinde ayrı yerleşim ve yazı tipi:
  1 Kırmızı çizgi (Manrope) · 2 Sol şerit (Sora) · 3 S monogramı (Michroma, QR solda) · 4 Geniş harf (Michroma) ·
  5 Çerçeve (Sora) · 6 Ortalı (Manrope) · 7 Kırmızı başlık (oyma SOYLU) · 8 Jant (Oswald) · 9 Rozet (Sora) ·
  10 Alt bant (Archivo Black, oyma telefon).
- İçerik: SOYLU, OTO LASTİK, HEMEN ARA, telefon **0541 487 30 03**, QR (TARA / BİZE ULAŞIN).
- **QR: işletme sayfası** `https://soyluotolastik.qrsistem.workers.dev/` (`bilgiler.json` → `sayfa_url`). Ortak
  Cloudflare hesabında (`qrsistem`) Worker adı tam olarak `soyluotolastik` olmalı. QR sürüm 4, hata düzeltme Q,
  34–38 mm (kare ≥ 0,91 mm); hepsi görüntüden ve baskı hatası benzetiminden okundu.
- Yapı Uzar, İNCE ve Çalık isimlikleriyle aynı: 120 × 90 mm, köşeler R8, siyah gövde 1 cm, yazılar 2 mm kabartma, QR
  yüzeyle aynı hizada beyaz karo, 15° eğik sehpa.
- Kontroller: satırlar arası ve kenarlara ≥ 2 mm; harf içi boşluklar ≥ 0,6 mm; simgelerde 1,2 mm'den ince yer
  < %4.

```bash
python3 scripts/soylu_isimlik.py            # 10 öneri ve katalog (4 süreçte)
python3 scripts/soylu_isimlik.py rozet      # yalnız eşleşen tasarımlar
```
