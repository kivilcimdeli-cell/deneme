# Örnek menü siteleri (10)

Masalıktaki QR ya da NFC bu sayfayı açar. Her site masalığıyla aynı renk ve yazı tipinde, ama düzeni kendine özgü;
çoğunda menü fotoğraflı. İşletmeler, ürünler, fiyatlar ve puanlar örnektir; gerçek siteler işletmenin kendi menüsü ve
fotoğraflarıyla hazırlanır ve ortak hesapta yayınlanır (`<ad>.qrsistem.workers.dev`).

| Site | Masalık | Düzen | Öne çıkan |
| --- | --- | --- | --- |
| `kaleici/` | 01 Kaleiçi Sofrası | saray menüsü: kemerli fotoğraf, noktalı fiyat satırları | garson çağır, şefin önerisi |
| `lagun/` | 02 Mavi Lagün | tam genişlikte fotoğraf, küçük resimli liste | günün balığı (kg fiyatı) |
| `forno/` | 03 Forno Rosso | büyük fotoğraf kartı, 2 sütun fotoğraflı ızgara | paket sipariş |
| `garaj/` | 04 Garaj Burger | poster: dev yazı, büyük fotoğraf kartları, sepet çubuğu | masadan sipariş, hesap öde |
| `kopuk/` | 06 Köpük | uygulama: kaydırmalı kartlar, alt menü, yuvarlak fotoğraflı liste | Wi-Fi'ye tek dokunuş, sepet |
| `koi/` | 10 Koi | Japon minimali: numaralı satırlar, zikzak fotoğraflar | omakase, masadan sipariş |
| `asma/` | 13 Asmaaltı | kara tahta: el yazısı, polaroid fotoğraflar | "çay söyle" düğmesi |
| `kasap/` | 14 Kasaphane | tam ekran fotoğraf, cam düğmeler; dergi menüsü | gramla fiyat, rezervasyon |
| `palmiye/` | 16 Palmiye | gün batımı, taşlı (masonry) kartlar | şezlonga sipariş, gün planı |
| `r360/` | 27 Rooftop 360 | gece: altın halka, hikâye halkaları, tam boy kartlar | imza kokteyller, rezervasyon |

Her klasörde:
- `index.html`: karşılama, masa numarası, düğmeler (menü, Google yorumu, Wi-Fi, Instagram, rezervasyon, sipariş) ve
  Google puanı.
- `menu.html`: kategoriler, açıklamalı ürünler, fiyatlar, etiketler (şef, acı, vegan…) ve fotoğraflar.
- `ekran_ana.png` ve `ekran_menu.png`: 390 × 844 telefon ekranı, 2×.

`img/`: 36 yemek ve içecek fotoğrafı (640 × 640). Fotoğraf siteleri bu ortamdan erişilemediği için hepsi Blender'da
modellenip çizildi (`scripts/menu_yemek_foto.py`); telif sorunu yok. Yazı tipleri `fonts/` klasöründe (OFL).

```bash
python3 scripts/menu_yemek_foto.py          # yemek fotoğrafları (~1 dk / fotoğraf)
python3 scripts/menu_siteleri.py            # 10 siteyi yazar ve ekran görüntülerini alır
python3 scripts/menu_siteleri.py koi asma   # yalnız bunlar
```
