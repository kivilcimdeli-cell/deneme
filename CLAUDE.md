# Çalışma kuralları

## İşletme siteleri (isimlikteki QR'ın açtığı dijital kartvizit sayfaları)

- Kullanıcı aksini söylemedikçe her yeni işletmenin sitesi **lastikçi tarzındaki 5 şablondan biriyle** yapılır:
  `python3 scripts/sablon_site.py <işletme klasörü>`. Yeni bir tarz icat edilmez, şablonun dışına çıkılmaz.
  - Şablonlar: 1 Şimşek (Uzar), 2 Lastik izi (İnce), 3 İkaz (Çalık), 4 Kurumsal (Soylu), 5 Gösterge (Auto Tufan).
  - Ayrıntı ve katalog: `site_sablonlari/README.md`, `site_sablonlari/katalog.png`.
- **Sıra:** şablonlar sırayla döndürülür (1 → 2 → 3 → 4 → 5 → 1); sıra `site_sablonlari/sira.json`da.
  - Üretici sıradakini kendisi seçip kaydeder.
  - Bir işletme bir kez şablon aldıysa yeniden üretimde aynı şablonda kalır.
  - Sıradaki: `python3 scripts/sablon_site.py --sira`.
- **İşletmeye göre değişenler** (`bilgiler.json`): vurgu rengi (`renk`), etiket, açıklama, logo işareti (`isaret`).
  - Bunlar şablonun içinde ayarlanır; düzen değiştirilmez.
- **Şablonda düzeltme ya da iyileştirme:** `scripts/sablonlar/` altında yapılır.
  - Ardından `python3 scripts/sablon_site.py --katalog` ile beş örnek yeniden denetlenir.
