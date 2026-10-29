# BOYDE LABS · ürün kataloğu ve Shopier görselleri

![Katalog](katalog.png)

İki ürün kategorisi, her birinde 10 model ("10 adet küçük, 10 adet büyük boy"):

| Kategori | Ölçü | Kimin için | Modeller |
| --- | --- | --- | --- |
| QR'lı masa isimliği | 9 × 12 cm (120 × 90 mm) | işletmeler: masa, tezgâh, kasa | M01–M10 |
| Kurumsal isimlik | 10 × 20 cm (200 × 100 mm) | yönetici ve personel: ad soyad, görev, logo | M01–M10 |

## Modeller

**9 × 12 cm**

- **Müşterilerin bastırdıkları:** Uzar, İnce, Çalık, Soylu Oto Lastik ve Auto Tufan.
- **Farklı sektörlere örnekler:** telefoncu, kuaför, güzellik salonu, emlak, kuyumcu.
  - İşletmeler uydurma (`scripts/boyde_sektor.py`).
  - Sanayi, galeri ve restoran bu katalogda yok; onların ayrı işleri var.
  - Berber, optik, veteriner ve spor salonu tasarımları da betikte duruyor (yedek).

**10 × 20 cm**

- Hepsi örnek (uydurma kişi ve kurumlar):
  - avukat;
  - diş hekimi;
  - mali müşavir;
  - mimar;
  - şirket yöneticisi;
  - psikolog;
  - diyetisyen;
  - emlak danışmanı;
  - otel ön büro (Lina Otel);
  - veteriner (Pati Veteriner Kliniği).
- Paloma Grida'nın isimliği katalogda ve görsellerde yok: "Paloma Hotels özel ve gerçek bir yer, onun yerine farklı bir
  kart koyar mısın".

**Örnek modu** (`scripts/boyde_urunler.py`):

- **QR'lar çalışmaz:** bulucu kareler ve zamanlama desenleri gerçek QR'daki gibi. Geri kalan kareler (biçim bilgisi dahil) rastgele: QR gibi görünür ama okunmaz. Her ürünün üstten görünüşünde iki okuyucuyla (zxing, OpenCV) denenir; okunursa üretim durur.
- **Telefonlar:** hepsinde 0546 475 45 08.
- **Kişi adları:** sektör örneklerindeki ad ve işletmeler uydurma.

## Dosyalar

| Dosya | Ne |
| --- | --- |
| `katalog.pdf` | A4 katalog: kapak, nasıl çalışır, iki kategori (giriş ve modeller), referanslar ve sipariş |
| `shopier/9x12/`, `shopier/10x20/` | Shopier ürün görselleri, 1200 × 1200 JPG: 10 model (01_M01 … 10_M10), BOYDE çerçevesinde |
| `cerceveli/<kategori>/` | her ürünün üç fotoğrafı (stüdyo, karşıdan, masa) BOYDE çerçevesinde: Instagram ve Shopier'e ek görsel |
| `shopier/<kategori>/ek/` | isteğe bağlı: kapak, 10 model bir arada, ölçü ve özellikler, nasıl çalışır |
| `shopier/urun_metinleri.md` | Shopier ürün adları ve açıklamaları (üç ürün) |
| `shopier/bayrakli/` | Türk bayraklı masa isimliği (Fırat Tuygun'a yaptığımız çapraz blok + sehpa), üzerinde "AD SOYAD": 01 kapak, 02–05 fotoğraflar BOYDE çerçevesinde (stüdyo, karşıdan, masa, yakın), 06 ölçü ve özellikler, 07 nasıl sipariş verilir (`scripts/bayrakli_isimlik_shopier.py`) |
| `shopier/site_ornekleri/` | 5 örnek site görseli (1200 × 1200), isimliğin QR'ının açtığı sayfa; beş şablonun beşi, her görsel başka düzende: Çağrı İletişim · Şimşek, Anka Emlak · Lastik izi, Luna Güzellik · İkaz, Sera Kuyumculuk · Kurumsal, Mira Kuaför · Sade (`scripts/boyde_site_gorsel.py`) |
| `shopier/kartvizit_ornekleri/` | 10 × 20 için 5 dijital kartvizit görseli: beş şablonun beşi, kişilerin kartvizit sayfası, rehbere kaydedilince kişi kartı, hazır WhatsApp mesajı (Kerem Aksoy · Şimşek, Elif Demir · Lastik izi, Zeynep Arslan · İkaz, Mehmet Kaya · Kurumsal, Selin Koç · Sade; uydurma kişiler, e-postalar ornek.com) |
| `siteler/<işletme>/` | örnek sitelerin bilgileri, logo işareti ve ekran görüntüleri (uydurma işletmeler; şablon sırasına yazılmaz) |
| `fotograf/<ürün>_studyo.jpg` | stüdyo fonunda (beyaz ya da INK), 3/4 |
| `fotograf/<ürün>_on.jpg` | aynı fonda, karşıdan |
| `fotograf/<ürün>_masa.jpg` | beyaz ya da siyah masada (yansımalı) |
| `fotograf/kapak_<kategori>.jpg` | kategori kapakları |
| `kaynak/<ürün>_duz.png` | düz görünüş (saydam) |

**Zeminler** ("kahverengi arka planları sil, hepsini beyaz yap"; "ürün beyazsa logomuzdaki renk"): ahşap masa ve bej
fon kaldırıldı.

- **Koyu isimlikler:** beyaz fon ve beyaz masa. "Kontrast yok gibi, siyahlardaki gibi derinlik" üzerine:
  - siyahlar derin (AgX Punchy);
  - fon ve masa parlak, isimliğin yansıması düşer;
  - fon ortada beyaz (~244), köşelere doğru yumuşakça kararır.
- **Beyaz isimlikler:** logodaki siyah (INK #121316), masa parlak siyah; fon kenarlarda tam INK.
- **Kapaklar:** isimliklerin çoğu hangi renkse ona göre (9 × 12 beyaz, 10 × 20 koyu).

**BOYDE çerçevesi:** ürünlerin bizim olduğu anlaşılsın diye ("BOYDE ürünü olarak pazarlamamız gerekiyor"); "daha
modern" isteğiyle sade:

- Fotoğraf tam kadraj; sol üstte BOYDE LABS logosu, sağ üstte ölçü.
- Altta buzlu cam şerit: turuncu model kodu (M01 …), ad, kategori, kimin için, "tasarım ve 3D baskı BOYDE".
- Renkler fotoğrafın fonuna göre: beyaz fonda koyu yazı, siyah fonda açık.
- Müşteri ürünlerinde şerit "… için ürettik" der.

**Shopier'e yükleme:**

- Her kategori bir ürün; 10 model görseli sırasıyla yüklenir.
- Görsel sınırı izin verirse `ek/kapak.jpg` ilk görsel olur.
- `ek/modeller.jpg` 10 modeli bir arada gösterir.
- Müşteri model seçmez: siparişten sonra ona özel 10 tasarım hazırlanır, en beğendiği basılır ("10 adet örnek
  çalışma yapacağız"). M01 … M10 örnek çalışmalar; beğendiğinin kodunu not olarak yazabilir.

## Yeniden üretmek

```bash
python3 scripts/boyde_urunler.py      # modelleri kurar, QR denetler, kaynak/ (~2 dk)
pip install bpy==4.2.0
python3 scripts/boyde_urun_foto.py    # fotoğraflar (Blender Cycles, ürün başına ~4 dk)
python3 scripts/boyde_urun_foto.py --kapak --ornek 40
python3 scripts/boyde_site_gorsel.py  # örnek site görselleri (~2 dk; isimlik fotoğrafları çizildikten sonra)
python3 scripts/boyde_katalog.py      # katalog.pdf ve shopier/ (~1 dk)
python3 scripts/bayrakli_isimlik_shopier.py && python3 scripts/bayrakli_isimlik_shopier.py --foto && \
  python3 scripts/bayrakli_isimlik_shopier.py --shopier   # bayraklı isimlik (~5 dk)
```
