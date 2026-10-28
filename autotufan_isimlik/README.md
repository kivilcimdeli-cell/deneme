# AUTO TUFAN – Kaporta & Boya: QR'lı masa isimliği önerileri

Müşteriye gönderilecek katalog: **`musteri_1.jpg`** (1–6), **`musteri_2.jpg`** (7–10); PNG'leri ve ikisi birlikte
**`musteri_katalog.pdf`**. Ayrıntılı sayfalar: `<numara>_<ad>.png` (önden, masada, yandan).

- **Renkler:** hepsi siyah zemin, altın ve beyaz kabartma yazı ve şekil.
- **Logo:** müşterinin logosundan.
  - Fırça T görselden vektöre çevrildi (`logo/`, `scripts/autotufan_logo.py`) ve altın basılıyor.
  - "Auto Tufan" Poppins SemiBold; logodaki yazıyla birebir örtüşüyor.
  - "KAPORTA & BOYA" Poppins Bold. Logodaki Medium, 2 mm kabartmada fazla ince kalıyor.
- **Şekiller işe göre:**
  1 Klasik logo · 2 Ortalı · 3 Araba · 4 Boya tabancası · 5 Fırça darbesi (oyma Auto Tufan) · 6 Altın çerçeve ·
  7 Kalkan · 8 Boya damlaları · 9 Parlama · 10 Alt bant (oyma telefon).
- **İçerik:** Auto Tufan, KAPORTA & BOYA, HASAR ONARIM, ANTALYA, telefon **0546 475 45 08**, QR (TARA).
- **QR:** işletme sayfası `https://deneme123.qrsistem.workers.dev` (`bilgiler.json` → `sayfa_url`).
  - Ortak Cloudflare hesabında (`qrsistem`) Worker adı tam olarak `deneme123` olmalı.
  - Sondaki `/` olmadan adres 3. sürüme (29 × 29) sığıyor; 30–34 mm'de kare 0,91–1,03 mm.
  - Hepsi görüntüden ve baskı hatası benzetiminden okundu.
- **Yapı:** Uzar, İNCE, Çalık ve Soylu isimlikleriyle aynı.
  - 120 × 90 mm, köşeler R8, siyah gövde 1 cm, 15° eğik sehpa.
  - Yazılar ve şekiller 2 mm kabartma.
  - QR yüzeyle aynı hizada beyaz karo.
- **Kontroller:**
  - Küçük yazılar en az 4,6 mm büyük harf; 0,8 mm'den ince çizgi %6'dan az.
  - Harf içi boşluklar en az 0,6 mm.
  - Satırlar arası ve kenarlara en az 2 mm.
  - Oyma telefonda rakam araları en az 1 mm altın.
- **Filament:** altın için Bambu PLA Basic Gold (#E4BD68) ya da benzeri.

```bash
python3 scripts/autotufan_logo.py <logo_görseli>   # bir kez: fırça T (logo/)
python3 scripts/autotufan_isimlik.py               # 10 öneri ve katalog (4 süreçte)
python3 scripts/autotufan_isimlik.py kalkan        # yalnız eşleşen tasarımlar
python3 scripts/autotufan_isimlik.py katalog       # yalnız katalog sayfaları
```

## Baskı dosyası: seçilen 1 · Klasik logo, HASAR ONARIM (X2D)

![Baskı](baski/onizleme.png)

![Seçilen](1_klasik_logo_hasar_onarim.png)

**Müşterinin isteği:** 1 numara, ama KAPORTA & BOYA yazmasın, yalnız HASAR ONARIM yazsın. Logonun altındaki satır
HASAR ONARIM oldu; alttaki ayrı HASAR ONARIM satırı tekrar etmesin diye kalktı. Yerine ANTALYA ve HEMEN ARA geldi.

**`baski/autotufan_isimlik_x2d.3mf`**: Bambu Studio'da proje olarak açılıp doğrudan basılır. Ölçüler ve ayarlar
lastikçilerin isimlikleriyle aynı.

| | |
| --- | --- |
| Tabla | 2 takım (panel + sehpa) |
| Panel | 120 × 90 mm, siyah gövde 1 cm, köşeler R8, kenarlar basamaklı pahlı; yüzü yukarı basılır |
| Kabartma | 2 mm (10 katman). Beyaz: Auto Tufan, HASAR ONARIM, ANTALYA, telefon, TARA. Altın: fırça T, çizgi, HEMEN ARA, telefon simgesi |
| QR | siteyi açar (**https://deneme123.qrsistem.workers.dev**); 32 mm, kare 0,96 mm; yüzeyle aynı hizada beyaz karo |
| AMS | 1 siyah · 2 beyaz · 3 altın. Siyah ve altın ana nozulda (altın yalnız kabartmada, siyah bitince bir kez geçer); beyaz yardımcı nozulda |
| Ayarlar | Bambu standart 0,20 mm; **ütüleme kapalı**; destek yok; Textured PEI; Generic PLA |
| Filament | iki takım ~117 g (siyah 112, beyaz 3,9, altın 1,4) + kule; PrusaSlicer ~3 sa 22 dk |
| Sehpa | 100 × 40 × 10 mm, siyah, aynı tablada; panel yuvaya (10,3 mm) 15° eğik takılır |

**Dilimleyici kontrolü:** dosya PrusaSlicer'da aynı ayarlarla dilimlendi (`scripts/dilim.py`).

- Her yazı kabartmanın ilk katmanında (kenar) ve son katmanında kendi renginde basılıyor: %94–97 dolu.
- Fırça T, çizgi ve telefon simgesi de basılıyor.
- T'nin sivri uçları nozuldan ince kalmasın diye kenarı 0,3 mm kalınlaştırıldı.
- QR'ın beyaz karosu %98 dolu.

```bash
python3 scripts/autotufan_isimlik_baski.py   # 3MF, önizleme, ölçüm, dilimleyici kontrolü (~2 dk)
```

## Dijital kartvizit sayfası (isimlikteki QR'ın açtığı site)

![Sayfa](sayfa_onizleme.png)

![Tur](sayfa_tur.gif)

Solda ilk ekran, sağda tüm sayfa (karekod ve paylaş kutuları açık).

**2. sürüm.** İlk sürüm (sakin, tek kart) beğenilmedi: "lastikçilere yaptığımız gibi, havalı olsun". Soylu ve
İNCE'nin sayfalarının dili, Auto Tufan'ın renkleri ve işiyle kuruldu: siyah zemin, tek vurgu rengi altın, kaporta &
boya havası.

- **Başlık:**
  - karbon fiber zemin, üzerinden ara ara ışık geçer;
  - altın fırça T, AUTO ve dev, eğik, gümüş TUFAN; HASAR ONARIM;
  - altın çizgilerle kendini çizen araba: tekerlekler dönerek gelir, far yanar, gövdesinden ara ara boya parlaması
    geçer. Arkasından iki altın boya şeridi geçer.
- **Hemen Ara:** altın blok, numara büyük. Ekrandan çıkınca sağ altta altın ara düğmesi belirir.
- **Kutucuklar:** WhatsApp (hazır mesajlı), Instagram @autotufan1, Google yorumları (beş yıldız), konum (Kepez /
  Antalya, haritada), web sitesi autotufan.com.
- **Ödeme bilgileri:**
  - IBAN; Kopyala düğmesi.
  - Karekod: açılır, kaydedilir; banka uygulamasında galeriden okutulur.
- **Sonda:** Rehbere kaydet, Kartviziti paylaş (isimlikteki QR, Kopyala / Gönder), altbilgi.
- **Bağlantılar aynı sekmede açılır.** Yeni sekme, QR okuyucuların uygulama içi tarayıcılarında ve önizlemelerde
  çoğu zaman açılmıyor.
- **Karekod ve paylaş kutuları `<details>`:** JavaScript kapalıyken de açılır. Telefon taklidinde, JavaScript
  kapalıyken ve uygulama önizlemesinde (sandbox) denendi.
- **Hareketi azalt:** telefonda açıksa animasyonlar oynamaz, sayfa son hâliyle açılır.
- **Boyut:** ~140 KB.

**Bilgiler** (`bilgiler.json`):

- **IBAN şimdilik örnek:** `TR12 3456 7890 1234 5678 9012 34` (`iban_ornek: true`). Sayfada küçük "Örnek IBAN"
  notu var.
  - Gerçeği gelince `iban` alanına yazılır ve `iban_ornek` silinir; IBAN mod-97 ile doğrulanır.
  - Alıcı adı istenirse `iban_alici` alanına yazılır.
- **Banka karekodu:** şimdilik karekod yalnız IBAN'ı içeriyor.
  - Bankanın "karekod ile para gönder" ekran görüntüsünün içeriği `iban_karekod` alanına yazılınca (Uzar'daki gibi;
    CRC ve IBAN doğrulanır) banka uygulaması okutunca alıcı ve IBAN dolu açılır.
- **Google yorumları:** şimdilik "auto tufan kepez yorumları" araması.
  - İşletme profilindeki **Yorum iste** bağlantısı (`https://g.page/r/…/review`) `google` alanına yazılırsa doğrudan
    yorum penceresi açılır.

**Denemek için:** `sayfa_deneme.html` tek dosya (yazı tipleri, karekod, simge ve rehber kartı içinde); en iyisi
Chrome ile açmak.

**Yayın:** ortak Cloudflare hesabında (`qrsistem`) yeni bir Worker açılır, adı tam olarak `deneme123` olur ve
`autotufan_site.zip` yüklenir. Adres `https://deneme123.qrsistem.workers.dev` olur; isimlikteki QR bu adresi açar.

```bash
python3 scripts/autotufan_sayfa.py            # site, zip, önizleme ve tur GIF'i
python3 scripts/autotufan_sayfa.py --hizli    # GIF'siz
```
