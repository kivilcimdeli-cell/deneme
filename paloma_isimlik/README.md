# PALOMA GRIDA – Süleyman Boylu, QR'lı masa isimliği önerileri

Müşteriye gönderilecek katalog: **`musteri_1.jpg`**, **`musteri_2.jpg`** ve **`musteri_3.jpg`** (öneriler),
**`musteri_4.jpg`** (kartvizit sayfası); PNG'leri ve hepsi birlikte **`musteri_katalog.pdf`**. Ayrıntılı sayfalar:
`<renk>_<numara>_<ad>.png` (önden, masada, yandan).

## 2. tur

İlk tur estetik ve kurumsal bulunmadı, yazılar okunaksız göründü; logo da yoktu. Bu turda:

- **Gerçek logo:** Paloma Hotels logosu (PALOMA / HOTELS). Otelin sitesi bu ortamdan açılmadığı için Instagram
  profilinin ekran görüntüsünden vektöre çevrildi (`logo/`, `scripts/paloma_logo.py`). Mavi, logonun mavisi
  (#69A1BA).
- **Düz renkli dolgu:** logo, yazılar ve QR kabartma değil, yüzeyle aynı hizada 0,8 mm dolgu. Baskı gibi düz ve net
  görünür, kenar gölgesi olmaz. Logodaki ince HOTELS harfleri de böyle basılabiliyor: en az 0,56 mm'ye
  kalınlaştırıldı.
- **Yazılar:** ad soyad büyük-küçük harfle Montserrat SemiBold ya da Lora Bold. Görev Montserrat'la, mavi; otel
  "Paloma Grida" ya da logonun yanında "| GRIDA". Az öğe, geniş boşluk.
- **QR:** sondaki `/` olmadan adres 42 bayt, 3. sürüme (29 × 29) sığıyor. 30–31 mm karoda kare 0,90–0,93 mm.

## Öneriler (5 düzen × 2 renk)

Tek numaralar beyaz tabla (siyah ve mavi yazı), çift numaralar siyah tabla (beyaz ve mavi detay).

| No | Düzen | Ne var |
| --- | --- | --- |
| 1, 2 | Sütun | Solda logo, iki satır ad soyad, görev ve otel; ince mavi dikey çizgi; sağda QR |
| 3, 4 | Geniş isim | Üstte boydan ad soyad ve görev, mavi çizgi; altta logo, GRIDA ve QR |
| 5, 6 | Mavi kart | Sağda mavi kart içinde beyaz QR; solda logo, ad soyad (Lora), görev ve otel |
| 7, 8 | Üst bant | Üstte mavi bant içinde beyaz logo ve GRIDA (Instagram'daki gibi); altta ad soyad, görev, QR |
| 9, 10 | Ortalı | Logo ve GRIDA, ad soyad (Lora), kısa mavi çizgi, görev; altta ortada QR |

- **QR:** dijital kartvizit `https://suleymanboylu.qrsistem.workers.dev` (`bilgiler.json` → `sayfa_url`). Hepsi
  görüntüden ve baskı hatası benzetiminden okundu.
- **Yapı:** 120 × 90 mm, köşeler R8, gövde 1 cm, 15° eğik sehpa (Uzar, İNCE, Çalık ve Soylu isimlikleriyle aynı).
  Dolgular 0,8 mm (4 katman); renk değişimi yalnız üst 4 katmanda.
- **Kontroller:** çizgiler ≥ 0,5 mm, harf içleri ve aralar ≥ 0,4 mm, öğeler arası ≥ 2 mm, kenara ve sehpaya ≥ 3 mm.
- **Filament:** mavi için logonun mavisine (#69A1BA) en yakın açık mavi / çelik mavisi seçilmeli; görsellerde bu
  renk kullanıldı.

```bash
python3 scripts/paloma_logo.py <ekran_görüntüsü>   # logoyu vektöre çevirir (logo/)
python3 scripts/paloma_isimlik.py                  # 10 öneri ve katalog (4 süreçte)
python3 scripts/paloma_isimlik.py bant             # yalnız eşleşen düzenler
python3 scripts/paloma_isimlik.py katalog          # yalnız katalog sayfaları
```

## Dijital kartvizit sayfası

![Sayfa](sayfa_onizleme.png)

![Tur](sayfa_tur.gif)

Soldan sağa: açılış ekranı, tüm sayfa, koyu tema.

**Yazı sistemi Paloma Hotels'ten:**

- Otelin sitesi bu ortamdan açılmadığı için logonun harfleri (PALOMA / HOTELS) Google yazı tipleriyle harf harf
  karşılaştırıldı. En yakını **Figtree**: PALOMA satırı ExtraBold, HOTELS satırı Light ile örtüşüyor; Montserrat
  daha geniş kalıyor.
- Sayfada da aynı düzen: büyük harf, geniş aralık; ad PALOMA gibi kalın (SÜLEYMAN), soyad HOTELS gibi ince ve aynı
  genişliğe yayılmış (B O Y L U). Etiketler küçük ve aralıklı; tırnaklı yazı tipi yok.

**Tasarım (otel sitesi gibi):**

- **Açılış:** tam ekran görsel, ufukta Akdeniz. Üstte PALOMA HOTELS | GRIDA, altta ad, soyad ve görev; sağda KAYDIR
  işareti.
- **Yüzen çubuk:** Ara, WhatsApp, E-posta ve Konum, ince çizgili yuvarlak simgelerle.
- **01 İletişim:** cep, şirket hattı ve e-posta; değerler büyük ve ince harfle.
- **02 Otel:** yukarıdan sığ, turkuaz deniz görseli üstünde PALOMA / G R I D A; adres ve Yol tarifi.
- **03 Kartvizit:** mavi kart içinde isimlikteki QR'ın aynısı, Rehbere kaydet ve Kartviziti paylaş.
- **Sonda:** logo. Telefon koyu moddaysa sayfa gece renklerine geçer.
- **Görseller:** Blender'da çizildi (`gorsel/`, `scripts/paloma_gorsel.py`), telif sorunu yok.
- **Paylaşım görseli:** bağlantı WhatsApp'ta paylaşılınca deniz, logo, ad ve görev görünür (`site/paylas.jpg`).
- **Boyut:** sayfanın tamamı yaklaşık 460 KB.

**Animasyon** (`sayfa_tur.gif`):

- **Açılış (~2,6 sn):**
  - Görsel yavaşça yaklaşır; PALOMA harfleri iner, HOTELS harfleri ortadan açılır, ayraç ve GRIDA gelir.
  - SÜLEYMAN harfleri maskeden çıkar, B O Y L U ortadan yerlerine yayılır; ince çizgi uzar, görevin harf aralığı
    açılır.
  - İletişim çubuğu aşağıdan gelir, simgeleri çizilir.
- **Kaydırma:**
  - Açılış görseli yavaş kayar.
  - Bölüm başlıklarında numara, çizgi ve başlık açılır; satırlar alt çizgileriyle sırayla gelir.
  - Otel görseli alttan perde gibi açılır ve içinde kayar; QR kareleri çapraz dalgayla belirir.
  - İletişim çubuğu ekrandan çıkınca altta Ara / WhatsApp şeridi açılır.
- **Sürekli:** KAYDIR çizgisi akar, QR'ın vizör köşeleri nefes alır, Rehbere kaydet'in üstünden ışık geçer.

Telefonda "hareketi azalt" açıksa animasyonlar oynamaz; sayfa doğrudan son hâliyle açılır.

**Denemek için:** `sayfa_deneme.html` tek dosya; yazı tipleri, görseller ve rehber kartı içinde. Yüklemeye gerek
yok, telefonda ya da tarayıcıda açılır. Yayına giden sürüm `site/` klasörü ve zip.

**Bilgiler:** hepsi `bilgiler.json` içinde. Değişince sayfa betiği yeniden çalıştırılır.

**Yayın:** ortak Cloudflare hesabında (`qrsistem`) yeni bir Worker açılır, adı tam olarak `suleymanboylu` olur ve
`paloma_site.zip` yüklenir. Adres `https://suleymanboylu.qrsistem.workers.dev` olur; isimliklerdeki QR bu adresi
açar.

```bash
python3 scripts/paloma_gorsel.py           # deniz görselleri (Blender, ~9 dk)
python3 scripts/paloma_sayfa.py            # site, zip, önizleme ve tur GIF'i
python3 scripts/paloma_sayfa.py --hizli    # GIF'siz
```
