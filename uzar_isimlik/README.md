# UZAR OTO LASTİK – QR'lı tezgâh isimliği (site yok)

![Tasarımlar](hepsi.png)

## Sistem: QR'lar doğrudan açar

| QR | Okutunca |
| --- | --- |
| **ARA** | `TEL:+905426116987`: telefon uygulaması numarayla açılır |
| **WHATSAPP** | `https://wa.me/905426116987`: WhatsApp sohbeti açılır |
| **KAREKOD İLE ÖDE** | banka uygulamasıyla okutulunca para gönderme ekranı ENES UZAR ve IBAN'ı dolu açılır (Yapı Kredi karekodunun içeriği fotoğraftan okundu, birebir yeniden çizildi) |

Instagram adı (@enesuzar9794) ve telefon numarası yazılı. Araya internet sitesi girmez; yayınlanacak bir şey yok.

- Tüm bilgiler tek dosyada: `bilgiler.json`. IBAN mod-97 ile doğrulanır; karekodun CRC'si ve içindeki IBAN/alıcı
  bu IBAN'la karşılaştırılır (tutmazsa üretim durur).
- QR kare boyu: karekod 0,90 mm, ARA ve WHATSAPP 0,96 mm (en az 0,9). Her QR baskıya giden geometriden ve
  isimliğin ön görünüşünden okundu; siyahın ±0,15 mm taşması, bulanıklık, 35° eğik bakış, uzaktan, gölge ve gürültü
  benzetimlerinde de okundu (`qr_kontrol.png`).

## İsimlik (3 öneri, 4:3)

Panel **128 × 96 × 2,6 mm**, köşeler R8, kenarlar iki yüzde 0,6 mm basamaklı pahla yumuşatılmış. Ön yüzü tablada
basılır: yazılar ve QR'ın beyaz zemini ilk 4 katmanda yüzeye gömülü renkli dolgu (0,8 mm), QR'ın siyah kareleri
gövdenin kendisi. Tablada basılan yüz düz ve keskin; Textured PEI ile mat olur (QR parlamaz). Panel 104 mm'lik
siyah sehpanın yuvasına 15° eğik takılır; ikisi aynı tablada, tutkalsız. Filament ~44–45 g (~22–23 TL, 500 TL/kg);
seçilen tasarım PrusaSlicer'da ölçülür.

1. **Sade** – siyah; solda UZAR ve şimşek, sağda OTO LASTİK ve telefon; solda ARA ve WHATSAPP, sağda karekod.
2. **Beyaz** – aynı düzen beyaz zeminde; QR'lar beyaz gövdede siyah kare.
3. **Ödeme solda** – başlık ortada, karekod solda, etiketler kırmızı.

## Kullanılmayan: işletme sayfası

İlk denemede sol QR bir işletme sayfası açıyordu (`site/`, `uzar_site.zip`, `sayfa_artifact.html`,
`scripts/uzar_sayfa.py`). Claude sayfasında "Claude" yazısı görünüp telefon bağlantısı çalışmadığı, kendi sitesi
de yayınlanamadığı için bırakıldı; dosyalar ileride site istenirse diye duruyor.

## Yeniden üretme

```bash
pip install segno zxing-cpp opencv-python-headless
python3 scripts/qr_sistemi.py            # QR kontrolü → qr_kontrol.png
python3 scripts/qr_sistemi.py oku resim.png   # banka karekodu ekran görüntüsünü okur
python3 scripts/uzar_isimlik.py          # isimlik görselleri → <tasarım>.png, hepsi.png
```
