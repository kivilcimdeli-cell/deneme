# UZAR OTO LASTİK – QR'lı tezgâh isimliği ve işletme sayfası

![Tasarımlar](hepsi.png)

## Sistem

| QR | Okutunca |
| --- | --- |
| **TARA · BİZE ULAŞ** | işletme sayfası açılır: Hemen Ara (telefon uygulaması numarayla açılır), WhatsApp, Instagram (@enesuzar9794), Google'da değerlendir, IBAN (tek dokunuşla kopyala), karekod, Rehbere Kaydet |
| **KAREKOD İLE ÖDE** | banka uygulamasıyla okutulunca para gönderme ekranı ENES UZAR ve IBAN'ı dolu açılır (Yapı Kredi karekodunun içeriği fotoğraftan okundu, birebir yeniden çizildi) |

- Sayfa adresi: **https://uzarotolastik.pages.dev/** (Cloudflare Pages, işletmenin kendi ücretsiz hesabı).
- Tüm bilgiler tek dosyada: `bilgiler.json`. IBAN mod-97 ile doğrulanır; karekodun CRC'si ve içindeki IBAN/alıcı
  bu IBAN'la karşılaştırılır (tutmazsa üretim durur).
- Sayfa adresi değişmediği sürece Instagram, Google bağlantısı, IBAN vb. **isimlik yeniden basılmadan** değişebilir:
  `python3 scripts/uzar_sayfa.py`, yeni `uzar_site.zip` aynı projeye yüklenir.
- QR kare boyu: sayfa 1,33 mm, karekod 0,90 mm (en az 0,9). Her QR baskıya giden geometriden ve isimliğin ön
  görünüşünden okundu; baskı ve okutma hatası benzetimlerinde de okundu (`qr_kontrol.png`).

![Sayfa](sayfa_onizleme.png)

## Sayfayı yayınlama: Cloudflare Pages (bir kez, ücretsiz)

`uzar_site.zip` hazır (içinde `index.html` en üstte). Bilgisayardan en rahatı; telefondan da olur.

1. **Hesap:** dash.cloudflare.com → *Sign up* → e-posta ve şifre (işletmenin ya da kendi e-postan; adres hiçbir
   yerde görünmez) → e-postadaki doğrulama bağlantısına bas. Kart bilgisi gerekmez; ilk açılışta alan adı (domain)
   eklemeyi önerirse atla.
2. **Proje:** soldaki menüden **Workers & Pages** (bazen *Compute* altında) → **Create** (*Create application*) →
   **Pages** sekmesi → **Upload assets** / *Use direct upload* → **Get started**.
3. **Ad:** *Project name* kutusuna **uzarotolastik** yaz → **Create project**. Adres `uzarotolastik.pages.dev` olur;
   ad başkasındaysa Cloudflare uyarır, `uzarotolastikantalya` gibi bir ad seç ve bana yaz.
4. **Yükle:** *Drag and drop your files here* alanına `uzar_site.zip` dosyasını sürükle ya da *select from computer*
   ile seç (telefonda dosyayı Dosyalar'dan seç). Liste çıkınca **Deploy site** (ya da *Save and Deploy*).
5. **Dene:** bir iki dakika sonra telefonda `https://uzarotolastik.pages.dev` aç: Hemen Ara telefon uygulamasını
   numarayla açmalı; WhatsApp, Instagram, Google, IBAN kopyala ve karekod çalışmalı.
6. Adres farklı çıktıysa bana yaz: QR'ı o adresle yeniden üretirim. **İsimlik, site açılmadan basılmaz.**

Sonra bilgi değişirse: aynı projede **Create deployment** (*Upload new version*) → yeni zip → Deploy. Adres aynı
kalır, isimlik yeniden basılmaz.

## İsimlik (4 öneri, 4:3)

Panel **120 × 90 × 2,6 mm**, köşeler R8, kenarlar iki yüzde 0,6 mm basamaklı pahla yumuşatılmış. Ön yüzü tablada
basılır: yazılar ve QR'ın beyaz zemini ilk 4 katmanda yüzeye gömülü renkli dolgu (0,8 mm), QR'ın siyah kareleri
gövdenin kendisi. Tablada basılan yüz düz ve keskin; Textured PEI ile mat olur (QR parlamaz). Panel 100 mm'lik
siyah sehpanın yuvasına 15° eğik takılır; ikisi aynı tablada, tutkalsız. Filament ~40 g (~20 TL, 500 TL/kg);
seçilen tasarım PrusaSlicer'da ölçülür.

1. **Sade** – solda UZAR ve şimşek, sağda OTO LASTİK / ANTALYA, altta iki QR.
2. **Beyaz** – aynı düzen beyaz zeminde; QR'lar beyaz gövdede siyah kare.
3. **Ortalı** – başlık ortada, etiketler kırmızı.
4. **Tek QR** – yalnız sayfa QR'ı (karekod sayfada), solda marka, TARA ve telefon.

Claude'daki önizleme sayfası (`sayfa_artifact.html`) yalnız önizleme içindir; orada "Claude" yazısı görünür ve
telefon bağlantısı çalışmaz, isimliğe bağlanmaz.

## Yeniden üretme

```bash
pip install segno zxing-cpp opencv-python-headless playwright fonttools
python3 scripts/qr_sistemi.py            # QR kontrolü → qr_kontrol.png
python3 scripts/qr_sistemi.py oku resim.png   # banka karekodu ekran görüntüsünü okur
python3 scripts/uzar_sayfa.py            # sayfa → site/, uzar_site.zip, sayfa_onizleme.png
python3 scripts/uzar_isimlik.py          # isimlik görselleri → <tasarım>.png, hepsi.png
```
