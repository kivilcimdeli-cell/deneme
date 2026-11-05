# Antalya 7/24 Oto Lastik Tamiri – işletme sitesi

- **İsimlik:** QR'lı masa isimliği 9 × 12, Atölye uygulamasında yapıldı (`baski/isimlik_9x12_uzar1_m06_x2d_v2.3mf`):
  ANTALYA, OTO LASTİK TAMİRİ, 0542 831 41 07, QR (TARA).
- **Sade, ortalı (v5, müşterinin seçtiği):** "müşteri sade tasarımı istedi ama yazıları biraz ortalayalım" →
  `baski/isimlik_9x12_uzar1_m06_x2d_v5.3mf` (önden: `baski/onden_v5.png`).
  - v2'nin sağ sütunu: üst öbek (ANTALYA, OTO LASTİK TAMİRİ) 16,4 mm aşağı, alt öbek (HEMEN ARA, telefon) 7,7 mm
    yukarı; aralarında 30 mm yerine 6 mm.
  - Sütun soldaki QR + TARA bloğuyla aynı hizada: ANTALYA QR'ın üstüyle, telefon TARA'nın altıyla.
  - QR, TARA, panel, sehpa ve baskı ayarları aynı; ağ kapalı, QR okunuyor.
  - `python3 scripts/isimlik_ortala.py baski/…_v2.3mf baski/…_v5.3mf --ara 6`
- **Lastik izi (v4):** "daha tasarımsal yap, İnce Oto Lastik'in internet sitesine yaptığımız tarzda" →
  `baski/isimlik_9x12_uzar1_m06_x2d_v4.3mf` (önden: `baski/onden_v4.png`).
  - İnce'nin sitesindeki lastik izi: ok biçimli dişler ve omuz blokları, 12° eğik, sağa doğru yükselir; sitede
    uçları maskeyle soluyor, burada dişler uçlara doğru küçülür.
  - Beyaz 2 mm kabartma, 18 mm boyunda, yazı sütunu boyunca (u 27 … 79).
  - Yazılara en az 2,1 mm; en ince çizgi 0,82 mm, en dar ara 1,2 mm; ağ kapalı, QR okunuyor; iki takım +1,1 g beyaz.
  - `python3 scripts/isimlik_lastik_izi.py baski/…_v2.3mf baski/…_v4.3mf --u 27.2 78.9 --v -17.7 12.3 --boy 18
    --bas 8 --son 96`
- **v3:** aynı desen yatay, düz sıra (`--stil duz`); kullanıcı "daha tasarımsal" istedi, yerine v4 geldi.
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
