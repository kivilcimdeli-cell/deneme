# Örnek menü siteleri (10)

Masalıktaki QR ya da NFC bu sayfayı açar. Her site masalığıyla aynı renk ve yazı tipindedir. İşletmeler, ürünler,
fiyatlar ve puanlar örnektir; gerçek siteler işletmenin kendi menüsüyle hazırlanır ve ortak hesapta yayınlanır
(`<ad>.qrsistem.workers.dev`).

| Site | Masalık | Öne çıkan |
| --- | --- | --- |
| `kaleici/` | 01 Kaleiçi Sofrası | garson çağır, şefin önerisi |
| `lagun/` | 02 Mavi Lagün | günün balığı (kg fiyatı) |
| `forno/` | 03 Forno Rosso | paket sipariş, ayın pizzası |
| `garaj/` | 04 Garaj Burger | masadan sipariş, hesap öde |
| `kopuk/` | 06 Köpük | Wi-Fi'ye tek dokunuşla bağlan |
| `koi/` | 10 Koi | omakase, masadan sipariş |
| `asma/` | 13 Asmaaltı | "çay söyle" düğmesi |
| `kasap/` | 14 Kasaphane | gramla fiyat, rezervasyon |
| `palmiye/` | 16 Palmiye | şezlonga sipariş, gün planı |
| `r360/` | 27 Rooftop 360 | imza kokteyller, rezervasyon |

Her klasörde:
- `index.html`: karşılama, masa numarası, düğmeler (menü, Google yorumu, Wi-Fi, Instagram, rezervasyon, sipariş) ve
  Google puanı.
- `menu.html`: kategoriler, açıklamalı ürünler, fiyatlar ve etiketler (şef, acı, vegan…).
- `ekran_ana.png` ve `ekran_menu.png`: 390 × 844 telefon ekranı, 2×.

Yazı tipleri `fonts/` klasöründe (OFL).

```bash
python3 scripts/menu_siteleri.py            # 10 siteyi yazar ve ekran görüntülerini alır
python3 scripts/menu_siteleri.py koi asma   # yalnız bunlar
```
