# İNCE OTO LASTİK – tek QR'lı tezgâh isimliği önerileri

Müşteriye gönderilecek katalog: **`musteri_1.png`** (1–6), **`musteri_2.png`** (7–10), ikisi birlikte
**`musteri_katalog.pdf`**. Ayrıntılı sayfalar: `<numara>_<ad>.png` (önden, tezgâhta, yandan).

- 1–7 beyaz zemin (siyah, kırmızı yazı), 8–10 siyah zemin (beyaz, kırmızı yazı). Her biri ayrı fikir ve yazı tipi:
  1 Plaka · 2 Minimal · 3 Kırmızı blok · 4 Yol · 5 Dama bayrağı · 6 Hız çizgileri · 7 Jant · 8 Kırmızı köşe ·
  9 Kırmızı çerçeve · 10 Oklar.
- İçerik: İNCE, OTO LASTİK, 7/24 HİZMET, telefon **0545 853 30 70**, tek QR. Süsler kalın ve sade (kolay basılır).
- Yapı Uzar Oto Lastik'in basılan isimliğiyle aynı: 120 × 90 mm, köşeler R8, gövde 1 cm, yazılar ve simge 2 mm
  kabartma, QR yüzeyle aynı hizada (beyaz zeminde siyah kareler, siyah zeminde beyaz karo), 15° eğik sehpa.
- Küçük satırlar Outfit ExtraBold: harf içi boşluklar kabartmada dolmasın diye her satır ölçülür (en dar ≥ 0,6 mm).

**QR:** işletmenin sitesi henüz yok; örneklerde QR telefonu arar (`TEL:+905458533070`). Site hazır olunca adresi
`bilgiler.json` → `sayfa_url`a yazılır, QR site adresine döner (seçilen tasarım o zaman X2D dosyasına çevrilir;
`scripts/uzar_isimlik_baski.py` örnek alınır).

```bash
python3 scripts/ince_isimlik.py           # 10 öneri ve katalog
python3 scripts/ince_isimlik.py klasik    # yalnız eşleşen tasarımlar
```
