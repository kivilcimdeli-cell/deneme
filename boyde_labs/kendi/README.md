# BOYDE LABS · kendi QR'lı isimliklerimiz

![9 × 12](sunum_9x12.jpg)

İstek: "BOYDE için bize de hem 9 × 12 hem 10 × 20, 10 adet ürün örneği, QR'lı masalık sunar mısın".

- **Marka:**
  - 3b · Katman işareti: nozul katmanların üstünde, en üst katman turuncu.
  - İki katlı yazı: BOYDE, altında turuncu çizgi ve LABS (Space Grotesk).
  - Slogan: "Katman katman, size özel."
- **Renkler:** paletten. Siyah gövde (INK), beyaz (PAPER), turuncu (ORANGE), gri (GRAY).
- **QR'lar çalışır:** WhatsApp'ımızı açar (`https://wa.me/905464754508`). Telefon 0546 475 45 08.
  - Her model üretilirken QR'ın düz görünüşte bu adresi okuttuğu denetlenir.

## 9 × 12 cm (120 × 90 mm)

1 cm siyah ya da beyaz gövde, yazı ve işaret 2 mm kabartma, QR yüzeyle aynı hizada, siyah sehpa.

| Kod | Model | Kısaca |
| --- | --- | --- |
| B01 | Klasik | siyah; işaret ve yazı, slogan, telefon; QR sağda |
| B02 | Katman şeritleri | siyah; işaretin katmanları boydan uzar, en üstteki turuncu |
| B03 | Beyaz | beyaz; hizmetler, turuncu çizgi; QR turuncu çerçeveli |
| B04 | Büyük işaret | siyah; solda büyük işaret, sağda QR |
| B05 | Nozul | siyah; nozul, bastığı turuncu çizgi BOYDE LABS'in altından geçer |
| B06 | Slogan | beyaz; büyük "Katman katman, size özel." |
| B07 | QR solda | siyah; QR solda, sağda işaret, yazı ve üç adım (tara, yaz, sipariş ver) |
| B08 | Turuncu bant | beyaz; üstte turuncu bant, içinde işaret ve BOYDE LABS oyuk |
| B09 | Çerçeve | beyaz; kenarda turuncu çerçeve |
| B10 | Gri katman | siyah; işaret gri, altta gri hizmet satırı |

## 10 × 20 cm (200 × 100 mm)

5 mm gövde, yazı ve işaret yüzeyle aynı hizada renkli dolgu, sehpa gövde renginde.

| Kod | Model | Kısaca |
| --- | --- | --- |
| B01 | Kurumsal | beyaz; büyük işaret ve yazı, dikey gri çizgi, QR |
| B02 | Siyah | siyah; işaret, yazı, hizmetler gri |
| B03 | Alt bant | beyaz; altta siyah bant, içinde hizmetler ve telefon oyuk |
| B04 | Turuncu blok | beyaz; solda turuncu blok, içinde işaret oyuk |
| B05 | Büyük yazı | siyah; boydan BOYDE, altında turuncu çizgi ve LABS |
| B06 | Slogan | beyaz; büyük slogan, QR turuncu çerçeveli |
| B07 | Hizmetler | siyah; 01 · 02 · 03 numaralı hizmetler |
| B08 | Uzayan katmanlar | beyaz; işaretin katmanları sola boydan uzar |
| B09 | Resepsiyon | beyaz; ortada işaret ve yazı, "Hoş geldiniz" |
| B10 | Kartvizit | siyah; atölye, telefon ve WhatsApp; QR turuncu çerçeveli |

## Seçilen: iki ölçüde B07 (Shopier)

İstekler:
- "İki üründe de B07'yi beğendik; Shopier linkimize açılsın."
- "Telefon numaralarını sil."
- "Büyük olanın tabanı beyaz olsun."
- "Küçükte QR ile yazıların yerini değiştir, QR sağda."
- "10 × 20'nin yazılarını neden kabartmalı yapmamışsın, o şekilde düzelt."

- **QR:** `https://www.shopier.com/boyde`, 3. sürüm, hata düzeltme Q. Üstten görünüşte ve baskı hatası benzetiminde
  okunur.
- **Telefon numarası yok.**
- **9 × 12:** siyah gövde, kabartma.
  - Solda işaret, BOYDE LABS, "1 TARA · 2 SİPARİŞ VER · 3 TASARIM SEÇ", shopier.com/boyde.
  - Sağda QR (34 mm), altında TARA.
- **10 × 20:** beyaz gövde ve sehpa; yazılar ve işaret 2 mm kabartma, siyah ve turuncu (9 × 12 gibi).
  - İşaret ve yazı, 01 · 02 · 03 hizmetler, shopier.com/boyde.
  - Sağda QR, altında TARA. QR yüzeyle aynı hizada siyah dolgu: kabartma QR'da kare kenarlarının gölgesi okumayı
    bozar. Beyaz zeminde siyah kareler baskıda yayılır; QR bu yüzden 38 mm (34 mm benzetimde okunmadı).
  - Kabartmada harf içi ve ara ≥ 0,7 mm: hizmetler kalın Montserrat, harf aralığı açık; İ, Ö, Ğ işaretleri yukarı
    alınır, Ö'nün iki noktası yana açılır; tek çizgili harfler (ı, l, i) 0,06 mm kalın. Adres 5,8 mm.
- **Fotoğraflar:** `fotograf/b9_shopier_studyo.jpg`, `fotograf/p_shopier_studyo.jpg`.
- **Baskı dosyaları** (`baski/`, `scripts/boyde_isimlik_baski.py`), Bambu Lab X2D:

| Dosya | Ne | AMS | Filament · süre (PrusaSlicer eşdeğeri) |
| --- | --- | --- | --- |
| `boyde_isimlik_9x12_b07_x2d.3mf` | iki takım; siyah gövde 1 cm, kabartma 2 mm, QR ve adres dolgu | 1 siyah · 2 beyaz · 3 turuncu | ~117 g · ~3 sa 23 dk |
| `boyde_isimlik_10x20_b07_x2d.3mf` | tek takım; beyaz gövde 5 mm, yazılar ve işaret 2 mm kabartma, QR dolgu | 1 siyah · 2 beyaz · 3 turuncu | ~85 g · ~2 sa 29 dk |

- **Ayarlar:** Bambu standart 0,20 mm, ütüleme ve destek kapalı, Textured PEI, Generic PLA.
  - 9 × 12: siyah ve turuncu ana nozulda, beyaz yardımcıda.
  - 10 × 20: beyaz ana nozulda; siyah ve turuncu yardımcıda (QR dolgusu ve kabartma).
- **Denetim:** her üretimde dilimlenir. Her yazı, nokta ve QR kendi renginde basılıyor mu bakılır.
  - Noktalar ayrı ölçülür. QR iki kez: büyük parçaları %85, tek kareler dahil bütün kareleri %70 kuralıyla
    (komşusuna yalnız köşeden değen kare de tek kare sayılır).
  - Önizleme `onizleme_*.png`, ölçüm `olcum_*.json`.
- **9 × 12 kabartma:** harf içi ve ara ≥ 0,7 mm. İ noktaları yukarı alındı; adımlarda orta nokta yok.

## Dosyalar

| Dosya | Ne |
| --- | --- |
| `sunum_9x12.jpg`, `sunum_10x20.jpg` | 10 modelin fotoğrafları bir arada (kodlu) |
| `sunum.pdf` | iki sayfa: iki ölçü |
| `fotograf/<model>_studyo.jpg` | stüdyo fotoğrafı (beyaz gövde logodaki siyahta, siyah gövde beyaz fonda) |
| `kaynak/<model>_duz.png` | düz görünüş (saydam); `kaynak/*.npz` git'e girmez |

## Yeniden üretmek

```bash
python3 scripts/boyde_kendi.py --rapor   # modeller, QR denetimi, basılabilirlik (harf içi ve ara, mm)
python3 scripts/boyde_kendi.py --foto    # stüdyo fotoğrafları (Blender, model başına ~1,5 dk)
python3 scripts/boyde_kendi.py --sunum   # sunum görselleri ve PDF
```
