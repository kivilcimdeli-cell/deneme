# Hoparlör kapağı önerileri (10)

Müşteriye gönderilecek katalog: **`musteri_1.jpg`** (1–6), **`musteri_2.jpg`** (7–10); PNG'leri ve ikisi birlikte
**`musteri_katalog.pdf`**. Ayrıntılı sayfalar: `<numara>_<ad>.png` (3/4 ve iki boyun üstten görünüşü).

**Boyut ve yapı:**
- İki boy, ikisi de tam yuvarlak. Ölçülen hoparlörler Ø100 mm (orta ses) ve Ø70 mm (tiz, REISS); kapak ölçüden
  2,5 mm büyük: **Ø102,5** ve **Ø72,5 mm**. Kenarı hoparlör halkasının üstüne oturur, kenarından yapıştırılır.
- Izgara 2 mm. Dış çerçeve 3 mm geniş ve 3,4 mm yüksek; alt yüzü tablada basılır, yapıştırma yüzeyi düzdür.
- Ortada yazı, 0,8 mm kabartma: Ø100 kapakta yuvarlak rozet, Ø70 kapakta yatay şerit (tiz kubbesinin önü açık
  kalsın). Yazı şimdilik örnek (`YAZINIZ`); `scripts/hoparlor_kapagi.py` → `YAZI` değiştirilir.
- Siyah gövde, beyaz yazı; 2, 4, 8 ve 10'da kırmızı halka.
- Yüzü yukarı, düz basılır; destek gerekmez. Kapak başına ~13–19 g (Ø102,5), ~6–10 g (Ø72,5).

**Desenler:** 1 Delikli · 2 Petek · 3 Işınsal · 4 Halkalar · 5 Türbin · 6 Yatay çizgi · 7 Elmas · 8 Jant · 9 Dalga ·
10 Degrade.

**Kontroller** (her desen, iki boy için):
- Delik / yarık genişliği en az 2,2 mm: kenarda ya da rozette kesilip daralan uçlar atılır.
- Köprüler en az 1,2 mm.
- Açıklık oranı (sesin geçtiği alan) %29–71.

```bash
python3 scripts/hoparlor_kapagi.py            # 10 öneri ve katalog (4 süreçte)
python3 scripts/hoparlor_kapagi.py jant       # yalnız eşleşen
```
