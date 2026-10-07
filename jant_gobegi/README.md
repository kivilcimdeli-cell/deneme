# Ford jant göbeği (Ø53, 8 tırnak) – Bambu Lab X2D

![Jant göbeği](onizleme/jant_gobegi.png)

![Kesit ve ölçüler](onizleme/kesit_olculer.png)

| Dosya | Ne için |
| --- | --- |
| `ford_jant_gobegi.3mf` | Jant göbeği, baskıya hazır (Ø53,3 × 15 mm) |
| `tirnak_deneme_halkasi.3mf` | **Önce bunu bas:** yalnız tırnaklar + ince halka. Jante takıp oturuşu dene (~15 dk) |

## Ölçüler

Kumpaslı fotoğraflardan okundu (kesit resminde yeşil):

- Ön yüz dış çapı **53,3 mm** (üç fotoğrafta 52,9 / 53,3 / 53,5)
- Tırnak dişleri dahil dış çap **48,5 mm**, tırnakların iç çapı **42,9 mm**
- **8 tırnak**, aralarında ~3 mm yarık; ortada Ø4 delik; ön yüzde Ø49 amblem yuvası

Fotoğraftan okunamadı, şimdilik tahmin (kesit resminde turuncu):

| | Ölçü | Tahmin | Nasıl ölçülür |
| --- | --- | --- | --- |
| D | Flanş kalınlığı | 5,0 mm | Kapağı yan çevir; ön yüz kenarından tırnakların çıktığı arka yüze |
| E | Tırnak boyu | 10,0 mm | Arka yüzden tırnak ucuna |
| F | Amblem yuvası derinliği | 1,0 mm | Kenar halkasının üstünden yuva tabanına (kumpasın derinlik çubuğu) |
| – | Toplam yükseklik | 15,0 mm | Kapağı yüzüstü koy, masadan tırnak ucuna |
| G | **Jantın göbek deliği çapı** | – | Jantta tırnakların girdiği delik; tırnak sıkılığını bu belirler |

Bu ölçüler gelince `scripts/jant_gobegi.py` dosyasının başındaki `OLCU` değerleri değiştirilir, betik dosyaları
yeniden üretir.

## Baskı

- **Malzeme: ASA** (X2D kapalı kasa, sorunsuz basar). Güneşte siyah jant 60–70 °C olur; PLA bu sıcaklıkta yumuşar,
  tırnaklar gevşer. ASA yoksa PETG. Dosyada PLA ayarı var: Bambu Studio'da filamenti **Bambu ASA** (ya da PETG) seç,
  doğru sıcaklıklar kendiliğinden gelir.
- **Yön:** Ön yüz yukarıda, tırnak uçları tablada. Böylece ön yüz ve amblem yuvası desteksiz ve temiz çıkar.
- **Destek:** Dosyada açık: *ağaç destek, yalnız tabladan*. Sadece flanşın arka yüzünün altına (görünmeyen taraf,
  tırnak halkasının içi ve dışı) gelir, elle kolay sökülür.
- **Ayarlar (dosyada):** 3 duvar, %25 dolgu, Arachne, kenar (brim) yok.
- Bir araç için 4 adet: nesneye sağ tıkla → *Örnek ekle* (3 kez) → *Düzenle*.

## Takma

Ford logosunu çizmedim. Ön yüzde Ø49,1 × 1,0 mm yuva var; orijinal tip yapışkanlı amblem etiketi (~48 mm)
bu yuvaya oturur. Etiketin çapı farklıysa söyleyin, yuvayı ona göre ayarlayayım.

Deneme halkası jantta:
- **Çok sıkıysa ya da girmiyorsa:** diş çapı (`dis_od`) 0,2–0,3 mm küçültülür.
- **Gevşekse ya da düşüyorsa:** diş çapı büyütülür, tırnak boyu (`L`) jantın deliğine göre ayarlanır.

## Yeniden üretme

```bash
python3 scripts/jant_gobegi.py
```
