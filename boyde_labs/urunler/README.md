# BOYDE LABS · ürün kataloğu ve Shopier görselleri

![Katalog](katalog.png)

İki ürün kategorisi:

| Kategori | Ölçü | Kimin için | Model |
| --- | --- | --- | --- |
| QR'lı masa isimliği | 9 × 12 cm (120 × 90 mm) | işletmeler: masa, tezgâh, kasa | M01–M17 |
| Kurumsal isimlik | 10 × 20 cm (200 × 100 mm) | yönetici ve personel: ad soyad, görev, logo | M01–M07 |

## Modeller

- **Müşterilerin bastırdıkları:**
  - Uzar, İnce, Çalık, Soylu Oto Lastik;
  - Auto Tufan;
  - Paloma Grida.
- **Önerilerden beğenilenler** (5):
  - İnce · Plaka;
  - Çalık · İkaz şeridi;
  - Auto Tufan · Altın çerçeve;
  - Paloma · siyah;
  - Paloma · kabartmalı.
- **Farklı sektörlere örnekler** (uydurma işletmeler, `scripts/boyde_sektor.py`):
  - 9 × 12:
    - telefoncu;
    - berber;
    - kuaför;
    - güzellik salonu;
    - emlak;
    - kuyumcu;
    - optik;
    - veteriner;
    - spor salonu.
  - 10 × 20:
    - avukat;
    - diş hekimi;
    - mali müşavir;
    - mimar.
  - Sanayi, galeri ve restoran bu katalogda yok; onların ayrı işleri var.

**Örnek modu** (`scripts/boyde_urunler.py`):

- **QR'lar çalışmaz:** bulucu kareler ve zamanlama desenleri gerçek QR'daki gibi. Geri kalan kareler (biçim bilgisi dahil) rastgele: QR gibi görünür ama okunmaz. Her ürünün üstten görünüşünde iki okuyucuyla (zxing, OpenCV) denenir; okunursa üretim durur.
- **Telefonlar:** hepsinde 0546 475 45 08.
- **Kişi adları:** Paloma isimliğinde gerçek kişinin adı yerine "Ayşe Yılmaz · Ön Büro Müdürü". Sektör örneklerindeki ad ve işletmeler uydurma.

## Dosyalar

| Dosya | Ne |
| --- | --- |
| `katalog.pdf` | A4 katalog: kapak, nasıl çalışır, iki kategori (giriş ve modeller), referanslar ve sipariş |
| `shopier/9x12/`, `shopier/10x20/` | Shopier ürün görselleri, 1200 × 1200 JPG, yükleme sırasıyla numaralı |
| `fotograf/<ürün>_studyo.jpg` | stüdyo fonunda, 3/4 |
| `fotograf/<ürün>_on.jpg` | stüdyo fonunda, karşıdan |
| `fotograf/<ürün>_masa.jpg` | ahşap masada |
| `fotograf/kapak_<kategori>.jpg` | kategori kapakları |
| `kaynak/<ürün>_duz.png` | düz görünüş (saydam) |

**Shopier'e yükleme:** her kategori bir ürün. Görseller şu sırayla:

1. Kapak.
2. Model tabloları (kodlarıyla).
3. Ölçü ve özellikler.
4. Nasıl çalışır.
5. Her model tek tek.

Shopier'in ürün başına görsel sınırı yetmezse ilk dördü ve en sevilen modeller yüklenir; model tabloları hepsini gösterir. Müşteri model kodunu sipariş notuna yazar.

## Yeniden üretmek

```bash
python3 scripts/boyde_urunler.py      # modelleri kurar, QR denetler, kaynak/ (~2 dk)
pip install bpy==4.2.0
python3 scripts/boyde_urun_foto.py    # fotoğraflar (Blender Cycles, ürün başına ~4 dk)
python3 scripts/boyde_urun_foto.py --kapak --ornek 40
python3 scripts/boyde_katalog.py      # katalog.pdf ve shopier/ (~1 dk)
```
