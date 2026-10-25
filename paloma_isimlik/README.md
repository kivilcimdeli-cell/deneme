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

- **Üst:** Paloma mavisi, beyaz Paloma Hotels logosu, altında GRIDA; altta kayan dalgalar.
- **Kart:** SB rozeti, ad soyad (Lora), görev, Paloma Grida · Paloma Hotels.
- **Düğmeler:** Ara, WhatsApp (cep numarası), E-posta, Konum (Google Haritalar).
- **Liste:** cep 0536 458 79 25, şirket hattı 0553 277 94 86, e-posta, adres (İskele Mevkii, Belek, Serik / Antalya).
- **Rehbere kaydet:** `suleyman-boylu.vcf` iner; bütün bilgiler tek dokunuşla telefonun rehberine eklenir.
- **Kartviziti paylaş:** telefonun paylaş menüsünü açar; o yoksa bağlantıyı kopyalar.
- **Yazı tipleri:** isimliklerle aynı, Montserrat ve Lora. `site/fonts` içinde, yalnız kullanılan harfler (OFL).

**Bilgiler:** hepsi `bilgiler.json` içinde. Değişince iki betik yeniden çalıştırılır.

**Yayın:** ortak Cloudflare hesabında (`qrsistem`) yeni bir Worker açılır, adı tam olarak `suleymanboylu` olur ve
`paloma_site.zip` yüklenir. Adres `https://suleymanboylu.qrsistem.workers.dev` olur; isimliklerdeki QR bu adresi
açar.

```bash
python3 scripts/paloma_sayfa.py
```
