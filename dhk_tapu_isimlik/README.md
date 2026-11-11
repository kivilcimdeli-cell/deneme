# DHK Tapu Takip ve Danışmanlık: 10 × 20 kurumsal isimlik

İki danışmana birer isimlik yapılacak (aynı tasarım, ayrı isim ve telefon). Her biri için 10 örnekli katalog
Atölye uygulamasıyla üretildi; iki katalogda K01–K10 kodları aynı tasarımı gösterir.

- **Kurum:** DHK Tapu Takip ve Danışmanlık · **Unvan:** Tapu Danışmanı · **Renk:** altın (siyah ve beyaz zemin)
- **QR altı yazı:** yok (müşteri KARTVİZİT yazısını istemedi; alana `yok` yazılır)
- **QR:** bilgisi sonra gelecek; şimdilik geçici site adı. Gelince `site_adi` güncellenir ve seçilen kodla 3MF üretilir.
- Kişi bilgileri (ad, telefon) burada tutulmaz; müşteri verisi uygulamanın veri klasöründe kalır.

## Logo

Müşterinin logosu küçük bir WhatsApp görseliydi (190 × 50 piksel): ince çizgili çatı (sağda baca) ve altında ince,
serifli DHK harfleri. `scripts/dhk_logo.py` aynı biçimi büyük çizer:

- `logo/dhk_logo.png`: uygulamaya yüklenen logo (beyaz zeminde siyah)
- `logo/dhk_logo_altin.png`: önizleme (siyah zeminde altın)

Harf stili orijinaldeki gibi (müşteri ilk çizimin kalın, küt harflerini beğenmedi). Bu incelikte logo isimlikte en az
~44 mm genişlikte basılmalı. 2 cm'lik logo kutusunda çatı ve ince çizgiler 2 mm kabartmada kaybolur. Bu yüzden
uygulamaya logoyu büyük basan üç düzen eklendi; küçük kutulu düzenleri logo kaybı denetimi eler:

- Büyük logo
- Logo üstte
- Logo ortada

Yeniden üretmek için: `python3 scripts/dhk_logo.py`

## Anahtarlık (toptan)

20 örnekli katalog: sade, isimsiz (ad soyadlar uzun). Ön yüzde yalnız logo; bazılarında altında küçük TAPU TAKİP.
A01–A15'in arka yüzünde QR, A16–A20'nin arkasında "TAPU TAKİP / VE DANIŞMANLIK" yazıyor.

- **Logo:** `logo/dhk_logo_kucuk.png`, anahtarlıkta harf boyu ~11 mm. Aynı stil; ince yerleri ve çatısı kalın, yoksa
  0,8 mm kabartmada D'nin gövdesi kopuyordu.
- **QR:** bilgi gelince `qr_adres` güncellenir. Şimdilik geçici sayfa adı var. Kısa sayfa adresi anahtarlığa sığar;
  uzun bağlantı (ör. harita) sığmaz.
- **Formdaki ayarlar:**
  - Ön yüz: Yalnız logo
  - Adın altında küçük yazı: TAPU TAKİP
  - Arka yüz yazıları: TAPU TAKİP, VE DANIŞMANLIK
  - QR'lı tasarım sayısı: 15
  - Gövde: Siyah ve beyaz (ikisi) · Renk: altın (müşteri: siyah, sarı, beyaz; mavi istemedi)
- **QR görünümü:** koyu gövdede beyaz zemin oval, köşe kareler yuvarlak (keskin köşeli QR beğenilmedi).
