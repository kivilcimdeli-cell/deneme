# BOYDE Atölye

Siparişten baskı dosyasına giden yerel uygulama. Bilgisayarda çalışır, tarayıcıda açılır (`http://127.0.0.1:8765`).

1. Ürün seçilir, müşteri bilgileri girilir.
2. Katalog üretilir: isimliklerde 10, anahtarlıkta 20 tasarım. PDF ve sayfa görselleri WhatsApp'tan gönderilir.
3. Müşteri beğenmezse **Yeni katalog üret** denir. Gösterilen tasarımlar tekrar gelmez.
4. Müşterinin söylediği koda (M03, G05, A07…) tıklanır ya da kod alttaki kutuya yazılır. **Baskı dosyalarını üret** ile
   X2D 3MF'i, önizlemeler ve web sayfası hazırlanır. Çıktılar müşteri sayfasının en üstünde; **Aç** / **İndir**.
   - "A07 olsun ama kırmızı": üret düğmesinin altında **Renkleri değiştir** (gövde, yazı, vurgu); boş bırakılan
     katalogdaki gibi kalır. Değişiklik geçmişe yazılır.
5. Müşteri **Sil** ile silinir: klasörü veri klasöründe `silinenler/` altına taşınır (geri alınabilir).

Katalogsuz ürünlerde (Türk bayraklı isimlik) bilgiler girilince doğrudan 3MF üretilir.

**Arayüz** (`atolye/arayuz/`):

- **Sol menü:** Yeni sipariş, Müşteriler, İşler (süren iş sayısı), son müşteriler; altta Claude durumu ve sürüm.
- **Müşteri sayfası:** adımlar (Bilgiler → Katalog → Seçim → Baskı dosyaları), kataloglar sekmeli, altta yapışık
  üretim çubuğu (kod, renk değişikliği); sağda çıktılar, Claude'a özel istek, geçmiş. **Bilgileri düzenle** sağdan
  açılan panelde (Esc kapatır).
- **Görünüm:** renkler marka paletinden; yazı tipleri uygulamayla gelir (Space Grotesk, Figtree; internet gerekmez).

## Kurulum (Windows)

**Kurulum dosyası (önerilen):** `BOYDE_Atolye_Kurulum.exe` indirilip çift tıklanır. Python ya da bat dosyası
gerekmez; yönetici izni istemez.

- Masaüstünde ve Başlat menüsünde **BOYDE Atölye** simgesi olur. Simge paneli kendi penceresinde açar (Edge'in
  uygulama penceresi, adres çubuğu yok); siyah konsol penceresi çıkmaz.
- Pencere kapanınca uygulama da kapanır. Süren bir iş varsa bitmesi beklenir.
- İlk açılışta "Windows bilgisayarınızı korudu" çıkarsa **Ek bilgi → Yine de çalıştır** (dosya imzasız).
- **Güncelleme:** yeni kurulum dosyası aynı şekilde kurulur; eskisinin üzerine yazar.
- **Nereden:** depodaki GitHub sürümleri (Releases, `atolye-1.0.N`). Her değişiklikte GitHub Actions Windows'ta yeniden
  derler (`.github/workflows/atolye-windows.yml`): kurulum klasörü (`scripts/atolye_windows.py`: gömülü Python 3.11,
  paketler, Chromium), duman testi (`scripts/atolye_duman.py`: yedi ürün baştan sona), Inno Setup
  (`paket/windows/atolye.iss`).

**ZIP ile (eski yol):**

1. [Python 3.11](https://www.python.org/downloads/) kurulur. Kurulumda **Add python.exe to PATH** işaretlenir.
2. `BOYDE_Atolye.zip` bir klasöre açılır (ör. `C:\BOYDE_Atolye`). Git ile de indirilebilir (depo ~370 MB).
3. `kurulum.bat` çift tıklanır: sanal ortam, paketler, site önizlemeleri için Chromium (birkaç dakika).
4. Her gün `BOYDE_Atolye.bat` ile açılır. Pencere kapanınca uygulama da kapanır.
5. Güncelleme: git ile kurulduysa `guncelle.bat`; ZIP ile kurulduysa yeni ZIP aynı klasöre açılıp `kurulum.bat` bir
   kez çalıştırılır. ZIP depodan `python3 scripts/atolye_paket.py` ile yapılır (`dist/BOYDE_Atolye.zip`).

**Kayıtlar** ayrı klasörde durur (aşağıda), güncellemeden ve kaldırmadan etkilenmez.

## Ürünler

| Ürün | Katalog | Seçilen kodla üretilenler |
| --- | --- | --- |
| QR'lı masa isimliği 9 × 12 | 10 tasarım (M01…) | iki takımlı X2D 3MF, müşteri önizlemesi, tabla kontrolü, web sayfası (zip) |
| Kurumsal isimlik 10 × 20 | 10 tasarım (K01…) | tek takımlı X2D 3MF, önizlemeler, dijital kartvizit sayfası (zip) |
| Güzellik isimliği 9 × 12 | 10 tasarım (G01…) | iki takımlı X2D 3MF, önizlemeler, randevu sayfası (zip, güzellik şablonu) |
| Güzellik isimliği 10 × 20 | 10 tasarım (K01…) | tek takımlı X2D 3MF, önizlemeler, kartvizit sayfası (zip, güzellik şablonu) |
| Türk bayraklı isimlik | yok | X2D 3MF (blok + sehpa), önizleme |
| Toptan anahtarlık | 20 tasarım (A01…) | dolu tabla 3MF, tek adetlik deneme 3MF'i, tabla başına adet ve kaç tabla gerektiği |
| Plakalı anahtarlık | yok | sipariş adedi kadar tabla 3MF'i (çoksa dolu tabla), deneme 3MF'i, ön ve arka önizleme |

### QR'lı isimlik

- **Tasarımlar:** 10 düzen (`atolye/tasarim/isimlik9.py`), müşterinin bilgileriyle kurulur.
  - Renkler: gövde (siyah ya da beyaz), yazı, vurgu; seçilmeyen otomatik. QR her zaman siyah-beyaz (okunsun diye).
  - Ad uzunsa küçülür ya da iki satıra bölünür.
  - Hizmetler sığdığı kadar yazılır.
  - Simge sektöre göre seçilir. Logo yüklenirse logo izlenip kabartma olur.
  - **Genel** sektörde simge yok, baş harf de konmaz; ad ve yazılar simgenin yerine kayar (blokta ortalanır).
- **Web sayfası:** lastikçi tarzındaki 5 şablondan sıradaki kullanılır (kural `CLAUDE.md`'de).
  - Adres `https://<sayfa adı>.qrsistem.workers.dev/`. Isimlikteki QR bu adresi açar.
  - Zip, Cloudflare'de aynı adlı Worker'a elle yüklenir.
  - Uygulamanın kullandığı şablon sırası veri klasöründe `site_sirasi.json`'da tutulur. Depodaki
    `site_sablonlari/sira.json`'dan devam eder.
- **Kontroller:** her üretimde yapılır.
  - QR üstten görünüşte ve baskı hatası benzetiminde okunuyor mu.
  - Kabartma yazıda harf içi ve harf arası en az 0,7 mm mi.
  - Parçalar iki nozulun ortak alanında mı.
  - PrusaSlicer kuruluysa ek bir dilimleyici denetimi yapılır (Windows'ta genelde atlanır).

### Kurumsal isimlik 10 × 20

- **Tasarımlar:** 10 düzen (`atolye/tasarim/isimlik20.py`): ad soyad, unvan, kurum, telefon; simge sektöre göre ya da
  logo. Genel sektörde simge yok: baş harf konmaz, monogram düzeni katalogda çıkmaz.
- **Renkler:** gövde, yazı, vurgu (9 × 12'deki gibi); QR her zaman siyah-beyaz.
- **Uzun yazılar:** uzun unvan ve kurum iki satıra iner, gerekirse ad küçülür. Yine sığmazsa telefon isimlikten
  çıkar; telefon sayfada kalır, notlarda uyarı çıkar.
- **Kartvizit sayfası:** aynı 5 şablonla, kişinin kartviziti olarak yapılır. E-posta bağlantısı eklenir; **Rehbere
  kaydet** kişiyi kurumuyla ekler.

### Güzellik isimlikleri (9 × 12 ve 10 × 20)

Kuaför, güzellik salonu, tırnak, kirpik, cilt bakım, lazer, makyaj, spa, gelin başı için; Shopier'deki güzellik
koleksiyonunun (`boyde_labs/guzellik/`) uygulamadaki karşılığı.

- **Tasarımlar:** 9 × 12'de 10, 10 × 20'de 10 düzen (`atolye/tasarim/guzellik.py`), örnek ürünlerden (G01–G10,
  K01–K10) genelleştirildi.
  - Ad el yazısıyla (Pacifico, Kaushan, Yesteryear, Norican, Dancing Script, Playball) ya da yumuşak serifle
    (Fraunces, Marcellus); el yazısında harfler bağlı kalır.
  - Süsler: çiçekli dal, şakayık, gül, papatya, nilüfer, çelenk, parıltı, fiyonk. Simge formdaki **dala** göre:
    makas, şakayık, oje, kirpik, ruj, gül, parıltı, nilüfer, taç, çiçek (simge yuvaya küçük kalırsa çiçek).
  - Uzun ad iki satıra iner, süslerin altında kalır; uzun iş türü (GÜZELLİK SALONU) iki satıra iner. Çelenkte ad
    sığmazsa o düzen katalogda çıkmaz.
- **Renkler:** paletler gövdeye göre: pudra, ten rengi, krem, lila, adaçayı, fuşya, beyaz, siyah; yazı ve süslerde
  mürdüm, moka, gül kurusu, rose gold, sarı… Formda gövde, yazı, vurgu seçilebilir; katalogda düzenin kendi paleti
  öne çıkar, aynı gövde rengi en çok üç kez. Renkli gövdede QR beyaz karoda (ya da koyu kareler doğrudan gövdede).
- **9 × 12:** isimlik9 yapısı: gövde 1 cm, yazı ve süsler 2 mm kabartma, siyah sehpa, iki takım. Kabartmada harf
  içi ve satırlar en az 0,7 mm; süslerin uçları 0,9 mm'ye yuvarlanır.
- **10 × 20:** isimlik20 yapısı (200 × 100 mm, gövde 5 mm, sehpa gövde renginde); yazılar ve süsler yüzeyle aynı
  hizada renkli dolgu (üst 0,8 mm), dolguda harf içi ve ara en az 0,45 mm. Gövde ve sehpa ana nozulda, dolgular
  yardımcıda.
- **Sayfa:** 5 güzellik şablonundan (6 Pudra, 7 Şakayık, 8 Gece, 9 Kemer, 10 Papatya) sıradaki; güzellik sırası
  lastikçi sırasından ayrı döner. WhatsApp satırı "Randevu al"; 10 × 20'de kişinin kartviziti (kurum, e-posta,
  rehbere kaydet).

### Toptan anahtarlık

- **Biçimler:** 8 biçim × 3 dizilim (`atolye/tasarim/anahtarlik.py`).
- **Yapı:** ön yüz 0,8 mm kabartma, arka yüz gömme yazı.
- **3 renk:** gövde, yazı (ad ve arka yüz), vurgu (simge, alt yazı). Seçilmeyen renk otomatik; seçilen yazı rengi
  gövdede zor okunuyorsa (sarı gövdede beyaz gibi) uyarı çıkar.
- **Sığmayan yazı:** alt yazı ve arka satırlar önce harf aralığını daraltır, sonra iki satıra iner ("0546 475" /
  "45 08"). Yine sığmayan yazılmaz, müşteri notlarında uyarı çıkar; arka yazısı eksik kalan tasarım katalogda ancak
  tam olanlar yetmezse gösterilir.

### Plakalı anahtarlık

- **Tasarım:** Shopier'deki ürün (`scripts/boyde_plakali_anahtarlik.py`, `tasarla()`): 70 × 22 × 3 mm, siyah
  çerçeve ve alt şerit, beyaz plaka zemini, kırmızı ya da mavi TR bandı; plaka 1,3 mm, alttaki yazı 1 mm kabartma.
- **Form:** plaka (zorunlu), alttaki yazı (ad soyad ya da söz; boş olabilir), TR bandının rengi, adet; müşterinin
  adı ve telefonu yalnız kayıt için.
- **Plaka:** büyük harfe çevrilir, boşluklar yerine konur (`34abc123` → `34 ABC 123`). İl kodu 01–81, 1–3 harf,
  2–4 rakam değilse yazıldığı gibi basılır, uyarı çıkar.
- **Alttaki yazı:** şeride sığacak kadar küçülür; İ noktası, Ş/Ç çengeli taşarsa önce şeritte kayar. 4 mm'nin
  altına inerse ya da 0,7 mm'den ince yerler kalırsa uyarı çıkar (kısaltma ya da önce deneme baskısı).
- **Tabla:** sipariş adedi kadar kopya (tek adette yalnız `_tek.3mf`); dolu tablaya 24 adet sığar, fazlası için kaç
  tabla gerektiği yazılır. AMS siyah, beyaz, bant rengi; siyah ve bant ana nozulda, beyaz yardımcıda.

## Öğrenme

Kataloglarda gösterilen ve seçilen tasarımların özellikleri sayılır: düzen, zemin, renk, yazı tipi, simge.
Kayıt veri klasöründe `tercihler.json`'da tutulur.

- **Ağırlık:** beğenilen özellikler sonraki kataloglarda daha sık çıkar.
- **Keşif:** seçimlerin %30'u yeni şeyler denemeye ayrılır.
- **Uygunluk:** ad bir düzende küçük kalıyorsa o düzen geri düşer.

## Claude'a özel istek

Algoritmanın karşılamadığı istekler müşterinin sayfasındaki **Claude'a ilet** kutusuna yazılır. Örnekler: "logo
daha büyük olsun", "arka yüze adres ekle".

İstek bilgisayardaki Claude Code'a gider (tek seferlik iş: dosya düzenleme ve uygulamanın Python'uyla komutlar
serbest), sonuç dosyaları müşterinin çıktılarına eklenir.

- **Gerekli:** komut satırındaki [Claude Code](https://claude.com/claude-code); Claude'un sohbet uygulaması yetmez.
  Windows'ta PowerShell'de `irm https://claude.ai/install.ps1 | iex`, sonra yeni pencerede `claude` ile bir kez giriş.
- **Bulma:** PATH, Windows'un güncel PATH'i (kayıt defteri) ve bilinen kurulum yerleri (`~/.local/bin`, npm, winget)
  aranır. Başka yerdeyse `BOYDE_CLAUDE` ortam değişkenine tam yolu yazılır.
- Bulunamazsa kutuda kurulum adımları ve **Yeniden dene** düğmesi çıkar (uygulamayı yeniden açmak gerekmez).

## Veriler

Veri klasörü Windows'ta **Belgeler\BOYDE Atolye**, başka sistemlerde depo içinde `atolye_veri/`. Müşteri
kayıtları ve çıktılar `musteriler/<tarih_ad>/` altındadır (müşteri sayfasında **Klasörü aç**):

- `musteri.json`
- `katalog_N/` (PDF, sayfa JPG'leri, tasarım görselleri)
- `cikti/` (3MF ve önizlemeler)
- `web/` (site)

Veri klasörü kişisel bilgi içerir ve git'e girmez. Yedeği elle alınır.

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
