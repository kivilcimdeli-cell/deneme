# Menü yönetim paneli – müşteri kataloğu

QR masalıkların arkasındaki sistemin yönetim panelini anlatan katalog: **`katalog.pdf`** (9 sayfa) ya da tek tek
**`katalog_01.jpg` … `katalog_09.jpg`**.

| Sayfa | İçerik |
| --- | --- |
| 1 | Kapak: gösterge paneli ve müşterinin telefonundaki menü; üç ana fayda |
| 2 | Nasıl çalışır: masalık → işletme sayfası → panel |
| 3 | Gösterge paneli: okutma, menü görüntüleme, Google yorumuna giden, saat ve şezlong bazında yoğunluk |
| 4 | Menü: kategoriler, ürünler, fotoğraf, fiyat, “tükendi”, canlı önizleme; ürün düzenleme ve toplu fiyat (telefon) |
| 5 | Müşterinin gördüğü: “Tükendi” etiketi, İngilizce menü, karşılama sayfası |
| 6 | İşletme bilgileri ve 10 hazır tema |
| 7 | Masalar ve QR: masa numaralı QR'lar, QR indirme, masa masa istatistik |
| 8 | Sipariş paketi (yakında): masadan sipariş, garson çağır, hesap; bar ve mutfak ekranı |
| 9 | Paketler (Menü Paketi, Sipariş Paketi), güvenlik, iki adımlı giriş |

Ekranlar **tasarım prototipidir** (`ekranlar/*.html`); panel henüz yazılmadı. Örnek işletme masalık kataloğundaki
Palmiye beach club; ürünler, kişiler ve rakamlar temsilîdir. Fiyat yok; paket fiyatları sonradan eklenir.
Sipariş paketi sayfasında “YAKINDA” etiketi var; o özellikler hazır olunca kaldırılır.

```bash
python3 scripts/yonetim_paneli_katalog.py     # ekranları HTML'den çizer, görüntüler ve kataloğu yazar
```
