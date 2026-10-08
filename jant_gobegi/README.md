# Ford jant göbeği (Ø53, 8 tırnak, Ford logolu) – Bambu Lab X2D, desteksiz

![Jant göbeği](onizleme/jant_gobegi.png)

![Kesit ve ölçüler](onizleme/kesit_olculer.png)

| Dosya | Ne için |
| --- | --- |
| `ford_jant_gobegi.3mf` | Ford logolu jant göbeği (Ø53,3 × 15 mm). AMS: **1 siyah · 2 beyaz · 3 mavi**. Destek yok |
| `tirnak_deneme_halkasi.3mf` | **Önce bunu bas:** yalnız tırnaklar + ince halka. Jante takıp oturuşu dene (~15 dk) |

## Ölçü kontrolü

Kumpaslı fotoğraflardaki verniyeler yeniden okundu, 3MF'in içindeki ağdan aynı yerler ölçüldü:

| Yer | Kumpas | Dosyada |
| --- | --- | --- |
| En geniş dış çap (flanşın arka kenarı) | 53,30 (ön) · 53,50 (arka) · 52,90 (logolu kapak) | **53,30** |
| Tırnak dişleri dış çapı | 48,5 | **48,50** |
| Tırnak iç çapı | 42,85 | **42,90** |
| Tırnak sayısı / yarık | 8 / ~3 mm (fotoğraf) | 8 / 3,0 |

Fotoğraftaki oranlardan (kumpasla ölçülen 53 mm'ye göre):

- Kapağın yan yüzü eğimli: en geniş yer arkada (53,3), ön yüz kenarı **Ø50,2**.
- Orijinal etiket ~Ø44,7 (45 mm etiket), yuvası ~Ø46 → logo zemini **Ø46,2**.
- Ford ovali zeminin 0,93'ü, en/boy 2,55 → **41,6 × 16,3 mm**.

Fotoğraftan okunamayan yükseklikler hâlâ tahmin (kesitte turuncu); ölçülürse `OLCU` değerleri değiştirilir:

| | Ölçü | Tahmin | Nasıl ölçülür |
| --- | --- | --- | --- |
| D | Flanş kalınlığı | 5,0 mm | Ön yüzden tırnakların çıktığı arka yüze |
| E | Tırnak boyu | 10,0 mm | Arka yüzden tırnak ucuna |
| – | Toplam yükseklik | 15,0 mm | Kapağı yüzüstü koy, masadan tırnak ucuna |
| G | Jantın göbek deliği çapı | – | Jantta tırnakların girdiği delik; tırnak sıkılığını bu belirler |

## Baskı (desteksiz)

- **Yön: ön yüz tablada, tırnaklar yukarıda.** Yan yüz 30° eğimle genişler, flanşın arka yüzü ve tırnaklar üstte
  kalır; hiçbir yerde destek gerekmez. Dosyada destek kapalı.
- **Logo tabla yüzeyine basılır:** FDM'de en düzgün ve keskin yüz. Düz (pürüzsüz) PEI tabla parlak, orijinal reçineli
  etikete benzer bir yüz verir; dokulu PEI ince dokulu, mat bir yüz verir.
- **Logo yüzle aynı hizada** (orijinal etiket gibi düz): siyah kenar halkası, beyaz zemin, mavi oval, beyaz yazı ve
  oval çizgisi. Mavi ilk 2 katman; beyaz 4 katman (mavinin arkasını da doldurur, beyaz opak çıkar).
  Siyah bir nozulda, beyaz ve mavi öbüründe: bütün baskıda yalnız **2 filament değişimi**.
- Yazının ince kıvrımları 0,4 nozula göre 0,1 mm kalınlaştırıldı: 0,5 mm'den ince yer kalmadı.
- **Malzeme: ASA** (X2D kapalı kasa, sorunsuz basar). Güneşte siyah jant 60–70 °C olur; PLA yumuşar, tırnaklar gevşer.
  ASA yoksa PETG. Üç rengin hepsi aynı malzemeden olmalı. Dosyada PLA ayarı var: Bambu Studio'da filamentleri
  **Bambu ASA** (ya da PETG) seç, doğru sıcaklıklar kendiliğinden gelir.
- **Ayarlar (dosyada):** 3 duvar, %25 dolgu, Arachne, kenar (brim) yok.
- Bir araç için 4 adet: nesneye sağ tıkla → *Örnek ekle* (3 kez) → *Düzenle*.

Logo çizimi Simple Icons'tan (`scripts/logolar/ford.svg`, CC0). Ford logosu Ford Motor Company'nin markasıdır.

## Takma

Deneme halkası jantta:
- **Çok sıkıysa ya da girmiyorsa:** diş çapı (`dis_od`) 0,2–0,3 mm küçültülür.
- **Gevşekse ya da düşüyorsa:** diş çapı büyütülür, tırnak boyu (`L`) jantın deliğine göre ayarlanır.

## Yeniden üretme

```bash
pip install svgelements
python3 scripts/jant_gobegi.py
```
