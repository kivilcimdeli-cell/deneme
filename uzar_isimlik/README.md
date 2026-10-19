# UZAR OTO LASTİK – QR'lı tezgâh isimliği ve işletme sayfası

![Tasarımlar](hepsi.png)

## Sistem

| QR | Okutunca | Not |
| --- | --- | --- |
| **TARA · BİZE ULAŞ** | işletme sayfası açılır: Hemen Ara, WhatsApp, Instagram (@enesuzar9794), Google'da değerlendir, IBAN (tek dokunuşla kopyala), karekod, Rehbere Kaydet | sayfa dosyaları: `site/` (yüklemeye hazır: `uzar_site.zip`) |
| **KAREKOD İLE ÖDE** | banka uygulamasıyla okutulunca para gönderme ekranı ENES UZAR ve IBAN'ı dolu açılır | Yapı Kredi karekodunun içeriği fotoğraftan okundu, birebir yeniden çizildi |

- Tüm bilgiler tek dosyada: `bilgiler.json`. IBAN mod-97 ile doğrulanır; karekodun CRC'si ve içindeki IBAN/alıcı
  bu IBAN'la karşılaştırılır (tutmazsa üretim durur).
- Sayfa adresi değişmediği sürece Instagram, Google bağlantısı, IBAN vb. **isimlik yeniden basılmadan** sayfadan
  değiştirilebilir (`python3 scripts/uzar_sayfa.py`, yeni zip yüklenir).
- QR kare boyu: sayfa 1,33 mm, karekod 0,90 mm (en az 0,9). Her QR baskıya giden geometriden ve isimliğin ön
  görünüşünden okundu; siyahın ±0,15 mm taşması, bulanıklık, 35° eğik bakış, uzaktan, gölge ve gürültü
  benzetimlerinde de okundu (`qr_kontrol.png`).

![Sayfa](sayfa_onizleme.png)

Hareketler: açılışta şeritler kayarak gelir, UZAR yükselir, şimşek çakar (sonra arada bir yeniden çakar),
OTO LASTİK açılır, düğmeler sırayla gelir; lastik dişi şeridi döner, Hemen Ara düğmesinde parıltı ve telefon
simgesi titrer, aşağıdakiler kaydırınca belirir, IBAN kopyalanınca kutu parlar. Telefonda "hareketi azalt" açıksa
hepsi kapanır. Kayıt: `sayfa_animasyon.gif`.

## Yayında: Claude sayfası

`sayfa_artifact.html` → https://claude.ai/artifact/HUbQzyvbWQyaWsyoYZ6x9C (önce özel; sayfanın **Paylaş**
menüsünden bağlantıya sahip herkese açılır). Bu biçimde yazı tipleri ve karekod sayfanın içinde; oradaki çerçeve
dosya indirmeyi engellediği için "Rehbere Kaydet" yok, karekod basılı tutularak kaydedilir; telefon bağlantısı her
izleyicide çalışmayabildiği için "Hemen Ara" numarayı da panoya kopyalar. Herkese açılınca adres isimlik QR'ına
yazılır (`bilgiler.json` → `sayfa_url`).

## Başka yol: kendi sitesi (bu depodan bağımsız, işletmenin kendi hesabıyla)

Sayfa, isimliği yapanın hesabıyla bağlantılı olmasın diye işletmenin kendi ücretsiz hesabında yayınlanır:

1. `uzar_site.zip` dosyasını bilgisayara indir, aç: içinden `uzar_site` klasörü çıkar.
2. Bilgisayar tarayıcısında **app.netlify.com/drop** sayfasını aç, `uzar_site` klasörünü sayfaya sürükle.
3. Site birkaç saniyede açılır. Kalıcı olması için işletmenin e-postasıyla ücretsiz hesap açıp siteyi sahiplen
   (sahiplenilmeyen site bir süre sonra silinir).
4. Site ayarlarında adı **uzarotolastik** yap → `https://uzarotolastik.netlify.app/`.
5. Kesin adres `bilgiler.json` → `sayfa_url`a yazılır, isimlik QR'ı o adresle yeniden üretilir.

Diğer yol: Cloudflare Pages → "Direct Upload" (zip ya da klasör) → `uzarotolastik.pages.dev`.
İsimlik, sayfa açıldığı doğrulanmadan basılmamalı (QR bu adresi taşır). Görsellerdeki QR şimdilik
`https://uzarotolastik.netlify.app/` adresini taşır.

## İsimlik (4 öneri, 4:3)

Panel **120 × 90 × 2,6 mm**, köşeler R8, kenarlar iki yüzde 0,6 mm basamaklı pahla yumuşatılmış. Ön yüzü tablada
basılır: yazılar ve QR'ın beyaz zemini ilk 4 katmanda yüzeye gömülü renkli dolgu (0,8 mm), QR'ın siyah kareleri
gövdenin kendisi. Tablada basılan yüz düz ve keskin; Textured PEI ile mat olur (QR parlamaz). Panel 100 mm'lik
siyah sehpanın yuvasına 15° eğik takılır; ikisi aynı tablada, tutkalsız. Filament ~39–41 g (~20 TL, 500 TL/kg);
seçilen tasarım PrusaSlicer'da ölçülür.

1. **Sade** – solda UZAR ve şimşek, sağda OTO LASTİK / ANTALYA, altta iki QR.
2. **Beyaz** – aynı düzen beyaz zeminde; QR'lar beyaz gövdede siyah kare.
3. **Ortalı** – başlık ortada, etiketler kırmızı.
4. **Tek QR** – yalnız sayfa QR'ı (karekod sayfada), solda marka, TARA ve telefon.

## Yeniden üretme

```bash
pip install segno zxing-cpp opencv-python-headless playwright fonttools
python3 scripts/qr_sistemi.py            # QR kontrolü → qr_kontrol.png
python3 scripts/qr_sistemi.py oku resim.png   # banka karekodu ekran görüntüsünü okur
python3 scripts/uzar_sayfa.py            # sayfa → site/, uzar_site.zip, sayfa_onizleme.png
python3 scripts/uzar_isimlik.py          # isimlik görselleri → <tasarım>.png, hepsi.png
```
