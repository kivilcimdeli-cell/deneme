# Antalya 7/24 Oto Lastik Tamiri – işletme sitesi

- **İsimlik:** QR'lı masa isimliği 9 × 12, Atölye uygulamasında yapıldı (`baski/isimlik_9x12_uzar1_m06_x2d_v2.3mf`):
  ANTALYA, OTO LASTİK TAMİRİ, 0542 831 41 07, QR (TARA).
- **QR:** `https://uzar1.qrsistem.workers.dev/` (3MF'in önizlemesinden okundu).
  - Ortak Cloudflare hesabında (`qrsistem`) Worker adı tam olarak `uzar1` olmalı.
- **Site:** şablon 1 · Şimşek (sıradaki; `site_sablonlari/sira.json`).
  - Cloudflare'e `antalya_site.zip` yüklenir.
  - Önizleme: `sayfa_onizleme.png`, tur: `sayfa_tur.gif`, telefonda deneme: `sayfa_deneme.html`.
- **Bilgiler** (`bilgiler.json`):
  - telefon ve WhatsApp 0542 831 41 07;
  - Instagram @07antalyaotolastiktamiri;
  - Google yorumları (işletmenin arama bağlantısı);
  - ödeme: Ziraat Bankası, Yusuf Uzar, IBAN TR18 0001 0000 5860 4032 1550 01.
  - Banka karekodu yok: bankanın karekodu gelirse `iban_karekod`a yazılır, site yeniden üretilir.
- **Yeniden üretmek:** `python3 scripts/sablon_site.py antalya_lastik_isimlik`.
