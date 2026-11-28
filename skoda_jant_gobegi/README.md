# Škoda jant göbeği amblemi – Ø55 mm, hafif bombeli, 4 adet (Bambu Lab X2D)

![Önizleme](onizleme.png)

**`skoda_jant_gobegi_55mm.3mf`**: Bambu Studio'da proje olarak açılır; tablada 4 disk hazır, doğrudan basılır.

| | |
| --- | --- |
| Ölçü | **Ø55,0 mm**; kenarda 1,8 mm, ortada 2,8 mm: ön yüz **1,0 mm bombeli**, üst kenar R0,8 yuvarlak |
| Logo | bombeyi izler, yüzeyle aynı hizada: siyah zemin, açık renk halka ve kanatlı ok, okun gözü siyah, dışta 1,6 mm siyah kenar |
| Arka yüz | tamamen düz: çift taraflı bant; tırnak yok |
| Renkler (AMS) | 1 siyah · 2 beyaz. Gümüş ya da Škoda yeşili istenirse yalnız 2. filament değiştirilir |
| Nozullar | siyah ana nozulda, açık renk yardımcı nozulda: **filament değişimi yok** |
| Baskı | **arka yüz tablada, bombe yukarıda**: **destek yok**, kenar (brim) yok; katman 0,12 mm |
| Filament | ~27 g (4 adet, PLA hesabı; ASA biraz daha hafif) |

- **Neden arka yüz tablada?** Bombeli yüz tablaya oturmaz. Ters çevirince bombe yukarıda kalır ve her katman
  alttakinden küçüktür, hiçbir yer sarkmaz. Kontrol ettim: 45°'den fazla sarkan yer yok (tabladaki 0,4 mm pah 45°).
  Arka yüz tabla yüzeyinde basıldığı için kusursuz düz çıkar, bant tam oturur.
- **Katman 0,12 mm:** bombe yüzeyi ince katmanlarla daha pürüzsüz çıkar; dosyada nesne ayarı olarak hazır.
- **Açık renk yüzeyden 1,0 mm aşağı iner:** beyaz opak çıkar, arkasındaki siyah gölge yapmaz. Üst 9 katman dolu:
  renkli kısımda boşluk kalmaz.
- **En ince yerler:** açık renk çizgiler ve siyah aralar en az 0,45 mm (okun sivri uçları hariç).
- **Malzeme: ASA.** Güneşte jant çok ısınır; PLA yumuşar, eğilir. Dosyada PLA ayarı var: Bambu Studio'da iki
  filamenti de **Bambu ASA** (ya da kullandığın ASA) seç, doğru sıcaklıklar kendiliğinden gelir. ASA yoksa PETG.

## Yapıştırma

- **Bant:** otomotiv için çift taraflı köpük bant (3M VHB / 3M otomotiv bandı gibi), 0,8–1,1 mm. Diskin arka yüzü
  düz; bandı Ø52–53 mm yuvarlak kes ya da 3–4 şerit yapıştır.
- **Yüzeyi hazırla:** göbek yüzeyini alkolle sil ve kurut; 15 °C'nin altındaysa yüzeyi biraz ısıt.
- **Bastır:** amblemi ortalayıp 30 sn bastır. Bant tam gücüne 24 saatte ulaşır; o süre yıkama yapma.

Logo çizimi Simple Icons'tan (`scripts/logolar/skoda.svg`, CC0). Škoda logosu Škoda Auto'nun tescilli markasıdır;
kişisel kullanım dışında (satış) marka sahibinin izni gerekir.

## Yeniden üretme

```bash
pip install svgelements
python3 scripts/skoda_jant_gobegi.py
```

Çap, kalınlık ve bombe betiğin başında: `D`, `EDGE` (kenar), `RISE` (bombe), `LOGO_D`, `INLAY`, `LAYER_H`.
