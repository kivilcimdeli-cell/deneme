# OTO SENTEZ – Çıkma ve yeni yedek parça: QR'lı masa isimliği önerileri

Müşteriye gönderilecek katalog: **`musteri_1.jpg`** (1–6), **`musteri_2.jpg`** (7–10); ikisi birlikte
**`musteri_katalog.pdf`**. Ayrıntılı sayfalar: `<numara>_<ad>.png` (önden, masada, yandan).

- **Renkler:**
  - Küre gri, OTO SENTEZ yazısı logodaki gibi lacivert.
  - 1–7: siyah gövde, beyaz yazı.
  - 8–10: 1, 3 ve 2'nin beyaz gövdeli hali, siyah yazı.
  - Filament: siyah, beyaz, Bambu PLA Basic Gray (#8E9089), Blue (#0A2989).
- **Logo:** müşterinin görselinden.
  - Küre ve OTO SENTEZ vektöre çevrildi (`logo/`, `scripts/otosentez_logo.py`).
  - Harf araları 2 mm kabartma için ~0,7 mm açıldı.
  - "ÇIKMA - YENİ YEDEK PARÇA" Poppins Bold ile yazıldı. Tire yerine kalın çizgi var, çünkü yazı tipinin tiresi kabartmada ince kalıyor.
- **Tasarımlar:** 1 Klasik logo · 2 Yan logo · 3 Ortalı · 4 Dişli · 5 İngiliz anahtarı · 6 Çerçeve ·
  7 Alt bant (oyma alt satır) · 8–10 beyaz.
- **İçerik:** logo, KEPEZ / ANTALYA, OTOSENTEZ.COM.TR, QR. Telefon yok (numara gelince eklenir).
- **QR:** şimdilik deneme sitesi `https://deneme123.qrsistem.workers.dev`.
  - OTO SENTEZ'in kendi sayfası seçimden sonra şablonla yapılır.
  - QR 31 mm.
  - Hepsi görüntüden okundu; baskı hatası benzetiminde 8 ve 10 sınırda.
- **Yapı:** Auto Tufan ve lastikçi isimlikleriyle aynı.
  - 120 × 90 mm, gövde 1 cm, 15° eğik sehpa.
  - Kabartma 2 mm.
  - QR yüzeyle aynı hizada.
- **Kontroller:**
  - Harf içleri ≥ 0,75 mm.
  - Öğeler arası ve kenara ≥ 2 mm.

```bash
python3 scripts/otosentez_logo.py <logo_görseli>   # bir kez
python3 scripts/otosentez_isimlik.py               # 10 öneri ve katalog
```
