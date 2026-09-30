# Çift taraflı isimlik (Bambu Lab)

![Önizleme](onizleme.png)

| Dosya | İçerik |
| --- | --- |
| `BERKE_ISIK_cift_tarafli.3mf` | **Basılacak dosya.** Bambu Studio'da açıp doğrudan dilimleyebilirsin. |
| `orijinal/Two_line_Customizable_Name_Plate.3mf` | MakerWorld Parametric Model Maker'dan gelen tek taraflı orijinal |
| `onizleme.png` | Orijinal ön yüz ile yeni ön yüz, arka yüz (çevrilmiş hâli) ve perspektif görünüm |

## Ne değişti?

- **Ön yüz orijinaliyle aynı:** 6 mm kabartma beyaz yazı, 20 mm siyah gövde, dış hat, harf aralarındaki boşluklar,
  Ş'nin altındaki çıkıntı ve tabladaki konum değişmedi. I ve K'nın altına siyah **eklenmedi**.
- **Arka yüze yazı eklendi:** Aynı yazı, tablaya bakan alt yüze **1 mm derinliğinde gömülü (inlay)** olarak basılıyor.
  Aynalanmış olarak yerleştirildi, isimliği çevirdiğinde **"BERKE / IŞIK" düz okunuyor**.
- **Arka yüzdeki Ş'nin çengeli küçük:** İsimlik çevrilince yazının sırası ters döner; arka yazıdaki Ş'nin çengeli
  önden bakınca I ile K'nın altına denk gelir. Oraya siyah eklememek için arka yüzdeki çengel, mevcut siyah
  çerçevenin içine sığacak kadar küçültüldü (yaklaşık 6 × 2,4 mm).
- **Arka harfler boşlukların üstünden geçiyor:** Arka yazı birkaç küçük yerde gövdedeki boşlukların üstünden geçiyor.
  Oralar siyahla doldurulmadı; harfin kendisi (beyaz) orada 2 mm kalınlıkta basılıyor. Önden bakınca bu boşlukların
  dibinde ince beyaz parçalar görünür, boşluklar yine açık kalır.
- **Arkadan bakınca siyah çerçeve harfleri öndeki kadar düzgün sarmaz:** Çerçeve ön yazının dış hattıdır; arkadan
  bakınca aynalanmış görünür. Örneğin arka yüzde I–K'nın altındaki siyah çıkıntı, ön yüzdeki Ş'nin çengelinin arkasıdır.
- **Model 3 parçaya ayrıldı** (Bambu Studio'da *Nesneler* listesinde görünür):
  | Parça | Filament |
  | --- | --- |
  | Gövde | 1 (siyah) |
  | Ön Yazı | 2 (beyaz) |
  | Arka Yazı | 2 (beyaz) |

  Rengi değiştirmek istersen parçaya sağ tıklayıp filamentini değiştirmen yeterli.
- Yazıcı, filament ve baskı ayarları (Bambu Lab X2D 0.4, Bambu PLA Basic, 0.20 mm Standard) orijinal dosyadan aynen alındı.

## Baskı

1. `BERKE_ISIK_cift_tarafli.3mf` dosyasını Bambu Studio ile aç (proje olarak yükle), filament 1 = siyah, filament 2 = beyaz olacak şekilde AMS eşleşmesini kontrol et.
2. **Dilimle → Yazdır.** Destek gerekmez (modelde hiç sarkma yok), yapıştırma gerekmez; tek seferde, tek parça basılır.
3. Arka yazı ilk 5 katmanda (0–1 mm) basıldığı için **ilk katmanın temiz yapışması önemli**: tablayı yağsız tut.
   Arka yüzün görünümü tablanın yüzeyini alır — pürüzsüz tabla (Cool Plate / Smooth PEI) parlak ve düz,
   Textured PEI ise mat, dokulu bir arka yüz verir.
4. Baskı bitince isimliği çevir: arka yüzde de yazı düz okunur.

> Not: Dosyada MakerLab bilgileri duruyor; modeli MakerLab'da yeniden düzenlersen tek taraflı hâline döner.
> Farklı bir isim için MakerLab'da yeni isimliği oluşturup aşağıdaki betikle yeniden çift taraflı yapabilirsin.

## Yeniden üretme / başka isim

```bash
pip install numpy manifold3d pillow
python3 scripts/cift_tarafli_isimlik.py isimlik/orijinal/Two_line_Customizable_Name_Plate.3mf \
    isimlik/BERKE_ISIK_cift_tarafli.3mf --onizleme isimlik/onizleme.png
```

- `--derinlik 0.6` gibi bir değerle arka yazının gömülme derinliği değiştirilebilir (katman yüksekliğinin katı olmalı; varsayılan 1.0 mm).
- Betik, MakerWorld "Parametric Model Maker" ile üretilmiş boyalı (gövde + kabartma yazı) isimlik 3MF'lerinde çalışır;
  gövde ve yazı filamentlerini dosyadaki boyamadan kendisi bulur.
