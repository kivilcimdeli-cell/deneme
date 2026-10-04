# AUTO FIRAT TUYGUN anahtarlıkları (siyah + sarı, Bambu Lab)

![Tüm tasarımlar](onizleme/hepsi.png)

Her `.3mf` dosyası Bambu Studio'da doğrudan açılıp dilimlenebilir. Hepsi aynı yapıda:

| Parça | Filament | Kalınlık |
| --- | --- | --- |
| Gövde | 1 – siyah | 0 – 3,2 mm |
| Kabartma (yazılar, çizgiler, çerçeve) | 2 – sarı | 3,2 – 4,2 mm |

Yazıcı/baskı ayarları önceki projedeki gibi: **Bambu Lab X2D 0.4, Bambu PLA Basic, 0.20 mm Standard**.
Renk değişimi tek bir yerde (3,2 mm) olur; destek gerekmez.

## Tasarımlar

| Dosya | Ölçü (mm) | Açıklama |
| --- | --- | --- |
| `1_klasik_kart.3mf` | 84 × 58 | Fotoğraf 1'in siyah-sarı hâli: çerçeve, çizgi araba, AUTO, isim, telefon, şehir |
| `2_araba_silueti.3mf` | 100 × 36 | Fotoğraf 2'nin siyah-sarı hâli: araba biçimi, büyük cam içinde AUTO |
| `3_araba_yan_cam.3mf` | 100 × 36 | Fotoğraf 3'ün siyah-sarı hâli: direkli yan cam, köşeli farlar |
| `4_plaka.3mf` | 96 × 30 | **Yeni** – plaka görünümü: TR şeridi, "07" (Antalya) + isim, altta telefon ve şehir |
| `5_araba_anahtari.3mf` | 104 × 34 | **Yeni** – araba anahtarı: kumanda gövdesinde isim, anahtar dilinde telefon |
| `6_lastik_rozet.3mf` | 62 × 71 | **Yeni** – dişli lastik halkası, kavisli ANTALYA ve telefon |
| `7_kilometre_saati.3mf` | 62 × 66 | **Yeni** – kilometre saati: çentikli kadran ve ibre |

Her tasarımın ayrı önizlemesi `onizleme/` klasöründe (üstten ve perspektif görünüm).

## Baskı

1. Dosyayı Bambu Studio'da aç, AMS'te **1 = siyah, 2 = sarı** eşleşmesini kontrol et.
2. Çok adet basmak için nesneye sağ tıkla → *Örnek ekle* (veya `+` tuşu), sonra *Düzenle* ile tablaya yerleştir.
3. Dilimle → Yazdır.

## Yeniden üretme / değiştirme

```bash
pip install numpy manifold3d pillow shapely scipy fonttools uharfbuzz
python3 scripts/anahtarlik.py          # hepsi
python3 scripts/anahtarlik.py plaka    # yalnızca adında "plaka" geçen tasarım
```

İsim, telefon ve şehir `scripts/anahtarlik.py` dosyasının başındaki `NAME`, `PHONE`, `CITY` değişkenlerinden değiştirilebilir;
renkler `BLACK` / `YELLOW`, kalınlıklar `BASE_H` / `RAISE_H` ile ayarlanır.

Yazı tipleri: Bebas Neue, Montserrat, Barlow Condensed (SIL Open Font License, `scripts/fonts/OFL-*.txt`).
