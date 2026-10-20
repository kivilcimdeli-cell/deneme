# ÇALIK OTO LASTİK – tek QR'lı tezgâh isimliği önerileri

Müşteriye gönderilecek katalog: **`musteri_1.png`** (1–6), **`musteri_2.png`** (7–10), ikisi birlikte
**`musteri_katalog.pdf`**. Ayrıntılı sayfalar: `<numara>_<ad>.png` (önden, tezgâhta, yandan).

- Hepsi siyah zemin, sarı ve beyaz yazı. Her birinde ayrı simge, yerleşim ve yazı tipi:
  1 Jant · 2 Anahtar · 3 Telefon · 4 İkaz şeridi · 5 Hız göstergesi · 6 Araba · 7 Lastik izi · 8 Şimşek ·
  9 Dama bayrağı · 10 Sarı blok (oyma yazı).
- İçerik: ÇALIK, OTO LASTİK, HEMEN ARA, telefon **0543 272 16 70**, tek QR.
- Simgeler kalın ve sade (en ince yeri ≥ 1,2 mm), makinede kolay basılır.
- Yapı Uzar ve İNCE isimlikleriyle aynı: 120 × 90 mm, köşeler R8, siyah gövde 1 cm, yazılar ve simgeler 2 mm
  kabartma, QR yüzeyle aynı hizada beyaz karo, 15° eğik sehpa.
- Küçük satırlar Outfit ExtraBold ile yazılır. Her satırın en dar harf içi boşluğu ölçülür (≥ 0,6 mm).
- Satırlar arası, simge ve QR çevresi ≥ 2 mm; sehpanın örttüğü alt şerit boş bırakılır.

**QR:** işletmenin sitesi henüz yok, bu yüzden örneklerde QR telefonu arar (`TEL:+905432721670`). Site hazır olunca:

1. Adresi `bilgiler.json` → `sayfa_url` alanına yazın; QR site adresine döner.
2. Seçilen tasarım o zaman X2D dosyasına çevrilir (örnek: `scripts/uzar_isimlik_baski.py`).

```bash
pip install segno zxing-cpp svgelements
python3 scripts/calik_isimlik.py           # 10 öneri ve katalog
python3 scripts/calik_isimlik.py araba     # yalnız eşleşen tasarımlar
```
