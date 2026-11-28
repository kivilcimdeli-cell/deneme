# Trendyol ilanları

Her klasör bir Trendyol ilanı: 1200 × 1800 görseller (yükleme sırasıyla 01, 02, …; en çok 8) ve `ilan.txt` (ürün adı,
açıklama, panel notları).

| Klasör | Ürün | Görsel |
| --- | --- | --- |
| `masa_9x12/` | QR'lı masa isimliği 9 × 12 | 8 |
| `kurumsal_10x20/` | Kurumsal isimlik 10 × 20 | 8 |
| `bayrakli/` | Türk bayraklı masa isimliği | 6 |
| `guzellik_9x12/` | Kuaför ve güzellik salonu isimliği 9 × 12 | 8 |
| `guzellik_10x20/` | Güzellik uzmanı isimliği 10 × 20 | 8 |
| `plakali_anahtarlik/` | Kişiye özel plakalı anahtarlık | 8 |
| `yilbasi_seti/` | Yılbaşı anahtarlık seti (6'lı) | 8 |

**Trendyol kuralları (satıcı rehberleri):** görselde logo, web adresi, iletişim bilgisi, fiyat yok; müşteri platform
dışına (telefon, WhatsApp, Shopier) yönlendirilmez.
- İlk görseller yazısız ürün fotoğrafı. Son 1–2 görsel (QR'ın açtığı sayfa, ölçü ve sipariş, sette neler var) yazı
  içerir: Trendyol reddederse çıkarılır.
- Örnek isimliklerde telefon **0500 000 00 00** (BOYDE'nin numarası değil), sitelerde Instagram `@isletmeniz`;
  plakalı anahtarlıklarda "BOYDE LABS" yerine "AD SOYAD".
- Kişiye özel ürünlerde müşteri bilgilerini sipariş detayındaki **Satıcıya Sor**'dan yazar (açıklamada ve son
  görselde anlatılır). Logo için Instagram hesabı istenir, dosya yüklemesi gerekmez.

**Yeniden üretmek:**

```bash
export BOYDE_TEL=905000000000 BOYDE_KAYNAK=$PWD/boyde_labs/trendyol/kaynak
python3 scripts/boyde_urunler.py && python3 scripts/boyde_guzellik.py && python3 scripts/bayrakli_isimlik_shopier.py
unset BOYDE_KAYNAK
BOYDE_KAYNAK=$PWD/boyde_labs/trendyol/kaynak_plaka BOYDE_PLAKA_AD="AD SOYAD" python3 scripts/boyde_plakali_anahtarlik.py
python3 scripts/trendyol_foto.py              # isimlik fotoğrafları (~75 dk)
python3 scripts/trendyol_anahtarlik_foto.py   # plakalı ve yılbaşı fotoğrafları (~30 dk)
python3 scripts/trendyol_gorsel.py            # bilgi görselleri, ilan klasörleri ve metinler
```
