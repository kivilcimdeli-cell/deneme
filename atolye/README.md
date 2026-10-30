# BOYDE Atölye

Siparişten baskı dosyasına giden yerel uygulama. Bilgisayarda çalışır, tarayıcıda açılır (`http://127.0.0.1:8765`).

1. Ürün seçilir, müşteri bilgileri girilir.
2. Katalog üretilir: QR'lı isimlikte 10, anahtarlıkta 20 tasarım. PDF ve sayfa görselleri WhatsApp'tan gönderilir.
3. Müşteri beğenmezse **Yeni katalog üret** denir. Gösterilen tasarımlar tekrar gelmez.
4. Müşterinin söylediği koda (M03, A07…) tıklanır. **Baskı dosyalarını üret** ile X2D 3MF'i, önizlemeler ve web
   sayfası hazırlanır.

Katalogsuz ürünlerde (Türk bayraklı isimlik) bilgiler girilince doğrudan 3MF üretilir.

## Kurulum (Windows, bir kez)

1. [Python 3.11](https://www.python.org/downloads/) kurulur. Kurulumda **Add python.exe to PATH** işaretlenir.
2. Depo indirilir. Git ile `git clone` ya da GitHub'dan ZIP.
3. `kurulum.bat` çift tıklanır. Sanal ortamı, paketleri ve site önizlemeleri için Chromium'u kurar.
4. Her gün `BOYDE_Atolye.bat` ile açılır. Pencere kapanınca uygulama da kapanır.

**Güncelleme:** `guncelle.bat` çalıştırılır. Depodaki son sürümü çeker; müşteri kayıtları korunur.

## Ürünler

| Ürün | Katalog | Seçilen kodla üretilenler |
| --- | --- | --- |
| QR'lı masa isimliği 9 × 12 | 10 tasarım (M01…) | iki takımlı X2D 3MF, müşteri önizlemesi, tabla kontrolü, web sayfası (zip) |
| Türk bayraklı isimlik | yok | X2D 3MF (blok + sehpa), önizleme |
| Toptan anahtarlık | 20 tasarım (A01…) | dolu tabla 3MF, tek adetlik deneme 3MF'i, tabla başına adet ve kaç tabla gerektiği |

### QR'lı isimlik

- **Tasarımlar:** 10 düzen (`atolye/tasarim/isimlik9.py`), müşterinin bilgileriyle kurulur.
  - Ad uzunsa küçülür ya da iki satıra bölünür.
  - Hizmetler sığdığı kadar yazılır.
  - Simge sektöre göre seçilir. Logo yüklenirse logo izlenip kabartma olur.
- **Web sayfası:** lastikçi tarzındaki 5 şablondan sıradaki kullanılır (kural `CLAUDE.md`'de).
  - Adres `https://<sayfa adı>.qrsistem.workers.dev/`. Isimlikteki QR bu adresi açar.
  - Zip, Cloudflare'de aynı adlı Worker'a elle yüklenir.
  - Uygulamanın kullandığı şablon sırası `atolye_veri/site_sirasi.json`'da tutulur. Depodaki
    `site_sablonlari/sira.json`'dan devam eder.
- **Kontroller:** her üretimde yapılır.
  - QR üstten görünüşte ve baskı hatası benzetiminde okunuyor mu.
  - Kabartma yazıda harf içi ve harf arası en az 0,7 mm mi.
  - Parçalar iki nozulun ortak alanında mı.
  - PrusaSlicer kuruluysa ek bir dilimleyici denetimi yapılır (Windows'ta genelde atlanır).

### Toptan anahtarlık

- **Biçimler:** 8 biçim × 3 dizilim (`atolye/tasarim/anahtarlik.py`).
- **Yapı:** ön yüz 0,8 mm kabartma, arka yüz gömme yazı.
- **Sığmayan yazı:** bir biçime sığmayan alt yazı ya da arka satır yazılmaz; müşteri notlarında uyarı çıkar.

## Öğrenme

Kataloglarda gösterilen ve seçilen tasarımların özellikleri sayılır: düzen, zemin, renk, yazı tipi, simge.
Kayıt `atolye_veri/tercihler.json`'da tutulur.

- **Ağırlık:** beğenilen özellikler sonraki kataloglarda daha sık çıkar.
- **Keşif:** seçimlerin %30'u yeni şeyler denemeye ayrılır.
- **Uygunluk:** ad bir düzende küçük kalıyorsa o düzen geri düşer.

## Claude'a özel istek

Algoritmanın karşılamadığı istekler müşterinin sayfasındaki **Claude'a ilet** kutusuna yazılır. Örnekler: "logo
daha büyük olsun", "arka yüze adres ekle".

İstek bilgisayardaki Claude Code'a gider, sonuç dosyaları müşterinin çıktılarına eklenir. Bunun için
[Claude Code](https://claude.com/claude-code) kurulu ve oturum açık olmalı. `claude` komutu yolda değilse
`BOYDE_CLAUDE` ortam değişkenine tam yolu yazılır.

## Veriler

Müşteri kayıtları ve çıktılar `atolye_veri/musteriler/<tarih_ad>/` klasöründedir:

- `musteri.json`
- `katalog_N/` (PDF, sayfa JPG'leri, tasarım görselleri)
- `cikti/` (3MF ve önizlemeler)
- `web/` (site)

`atolye_veri/` kişisel bilgi içerir ve git'e girmez. Yedeği elle alınır.

**Ortam değişkenleri** (isteğe bağlı):

- `BOYDE_VERI`: veri klasörü.
- `BOYDE_PORT`: panelin portu (varsayılan 8765).

## Yeni ürün eklemek

`atolye/urunler/<ad>.py` yazılır ve `atolye/urunler/__init__.py`'deki `SIRA` listesine eklenir. Eklentinin arayüzü
o dosyanın başında anlatılıyor: `KOD`, `AD`, `ACIKLAMA`, `KATALOG_ADET`, `ALANLAR`, `ad()`, `katalog()`, `uret()`.

Ortak parçalar `atolye/tasarim/` altında:

- `ortak.py`: renkler, kabartma yazı, simgeler, QR, kontroller.
- `katalog.py`: A4 katalog sayfaları.
- `logo.py`: logo izleme.
- `atolye/site.py`: web sayfası.
