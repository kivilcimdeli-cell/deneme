# Hoparlör kapağı önerileri (20)

Müşteriye gönderilecek katalog: **`musteri_1.jpg`** (1–6), **`musteri_2.jpg`** (7–10), **`musteri_3.jpg`** (11–16),
**`musteri_4.jpg`** (17–20; 11–20 agresif / modern seri); PNG'leri ve dördü birlikte **`musteri_katalog.pdf`**. Ayrıntılı sayfalar: `<numara>_<ad>.png` (3/4 ve iki boyun üstten görünüşü).

**Boyut ve yapı:**
- İki boy, ikisi de tam yuvarlak. Ölçülen hoparlörler Ø100 mm (orta ses) ve Ø70 mm (tiz, REISS); kapak ölçüden
  2,5 mm büyük: **Ø102,5** ve **Ø72,5 mm**. Kenarı hoparlör halkasının üstüne oturur, kenarından yapıştırılır.
- Izgara 2 mm. Dış çerçeve 3 mm geniş ve 3,4 mm yüksek; alt yüzü tablada basılır, yapıştırma yüzeyi düzdür.
- Ortada yazı, 0,8 mm kabartma: Ø100 kapakta yuvarlak rozet, Ø70 kapakta yatay şerit (tiz kubbesinin önü açık
  kalsın). Yazı şimdilik örnek (`YAZINIZ`); `scripts/hoparlor_kapagi.py` → `YAZI` değiştirilir.
- Siyah gövde, beyaz yazı; 2, 4, 8, 10, 14, 15 ve 17'de kırmızı halka, 11, 12, 17, 18 ve 19'da kırmızı rozet çizgisi.
- Yüzü yukarı, düz basılır; destek gerekmez. Kapak başına ~12–20 g (Ø102,5), ~6–10 g (Ø72,5).

**Desenler:** 1 Delikli · 2 Petek · 3 Işınsal · 4 Halkalar · 5 Türbin · 6 Yatay çizgi · 7 Elmas · 8 Jant · 9 Dalga ·
10 Degrade.

**Agresif / modern seri:** 11 Pençe · 12 Şimşek · 13 Hücre (Voronoi) · 14 Şevron · 15 Bıçak · 16 Üçgen ·
17 Spor jant · 18 Op-art · 19 Hız çizgileri · 20 Karbon örgü. Agresiflerde (11, 12, 14, 15, 17, 19) yazı eğik
Saira Condensed Black Italic; 11, 12, 15 ve 17'de Ø100 kapakta altıgen rozet, Ø70'te eğik şerit. Modernlerde
(13, 16, 18, 20) Sora ya da Michroma.

**Kontroller** (her desen, iki boy için):
- Delik / yarık genişliği en az 2,2 mm: kenarda ya da rozette kesilip daralan uçlar atılır.
- Köprüler en az 1,2 mm.
- Açıklık oranı (sesin geçtiği alan) %21–76; 12 Şimşek en kapalı (%24 / %21), 17 Spor jant en açık.
- Izgara tek parça: çerçeveye bağlı olmayan ada kalmaz.

```bash
python3 scripts/hoparlor_kapagi.py            # 20 öneri ve katalog (4 süreçte)
python3 scripts/hoparlor_kapagi.py jant       # yalnız eşleşen
```

## Seçilen: 5 · Türbin, 2 kapak (iç Ø102,5, dış Ø106,5) — baskı dosyası `baski/`

![Önden](baski/foto.png)
![Arkadan: çıkıntı ve yapıştırma yüzü](baski/foto_arka.png)

**`baski/hoparlor_kapagi_x2d.3mf`**: Bambu Lab X2D. İki kapak tek tablada; Bambu Studio'da açılıp doğrudan dilimlenir.

| | |
| --- | --- |
| Kapak | dış çap Ø106,5 mm; arka çıkıntının iç çapı Ø102,5 mm |
| Yazı | NECDET EFE / ÇALIK ve CEMAL / ÇALIK |
| Rozet | Ø47 mm (öneride Ø36) |
| Yazı tipi | Saira Condensed Bold Italic, beyaz; harf içleri en az 0,7 mm |
| Kırmızı | yalnız dış çeper |
| Arka çıkıntı | dış çeper arkaya 8 mm uzar (duvar 2 mm); ızgarayı koniden uzak tutar |
| Yapıştırma yüzü | çıkıntının düz ucu, 2 mm geniş halka (Ø102,5–106,5) |
| Izgara | 2 mm, 28 kıvrık yarık, açıklık %44; delikler en az 2,2 mm, köprüler en az 1,2 mm, tek parça |
| AMS / nozul | 1 siyah: ana nozul<br>2 beyaz, 3 kırmızı: yardımcı nozul<br>renk değişimi yalnız ilk 4 katmanda |
| Filament (yaklaşık) | ~42,9 g (siyah 41,1, kırmızı 1,4, beyaz 0,4) + kule |
| Süre | PrusaSlicer ~1 sa 33 dk (kule ve nozul değişimi hariç) |

**Baskı (destek gerekmez):**
- Ters basılır: ön yüz tablada, çıkıntı yukarı büyür.
- Duvar düz yukarı büyür, destek gerekmez; yapıştırma yüzü son katmandır ve düzdür.
- Kırmızı çeper ve beyaz isimler ilk 4 katmana (0,8 mm) gömülüdür, ön yüzle aynı hizadadır. Textured PEI dokusunda
  keskin çıkar.
- Bambu standart 0,20 mm, ütüleme kapalı, Textured PEI.

Ø70 kapaklar iptal edildi.

Önizleme ve kesit çizimi: `baski/onizleme.png`. Arka iç çap, çıkıntı boyu, duvar kalınlığı (= yapıştırma yüzü) ve
isteğe bağlı iç flanş betiğin başında (`INNER`, `LIP`, `WALL`, `FLANGE`). Yeniden üretmek için:

```bash
python3 scripts/hoparlor_kapagi_baski.py
```
