# PALOMA GRIDA – Süleyman Boylu, QR'lı masa isimliği önerileri

Müşteriye gönderilecek katalog: **`musteri_1.jpg`** (1–5, beyaz tabla), **`musteri_2.jpg`** (6–10, siyah tabla),
**`musteri_3.jpg`** (dijital kartvizit sayfası); PNG'leri ve üçü birlikte **`musteri_katalog.pdf`**. Ayrıntılı
sayfalar: `<numara>_<ad>.png` (önden, masada, yandan).

- **Beyaz tabla (1–5):** yazılar siyah ve mavi. **Siyah tabla (6–10):** yazılar beyaz, ayrıntılar mavi.
- **Üzerinde yalnız:** ad soyad (SÜLEYMAN BOYLU), görev (SATIN ALMA MÜDÜRÜ), otel (PALOMA, GRIDA) ve QR
  (KARTVİZİT). Telefon, e-posta ve adres isimlikte yok; QR'ın açtığı sayfada.
- **Tasarımlar:**
  1 Mavi çizgi (Cinzel) · 2 Sol şerit (Sora) · 3 Mavi bant (oyma PALOMA · GRIDA) · 4 İnce çerçeve (Fraunces) ·
  5 Minimal (Jost) · 6 Gece (Cinzel) · 7 Mavi köşe (QR solda) · 8 Alt bant (oyma görev) · 9 SB rozeti ·
  10 Dalga (Archivo, altta iki mavi dalga).
- **Logo:** otelin logosu bu ortamdan indirilemedi (site erişilemiyor), yerinde geçici olarak Cinzel ile "PALOMA"
  yazıyor. Logo dosyası `paloma_isimlik/logo.png` (ya da .jpg) olarak konup betik yeniden çalıştırılınca logo
  çizgilerinden kabartmaya çevrilir ve bütün tasarımlara ve sayfaya girer. En iyisi tek renk, şeffaf zeminli PNG ya
  da SVG.
- **QR:** dijital kartvizit `https://suleymanboylu.qrsistem.workers.dev/` (`bilgiler.json` → `sayfa_url`). QR sürüm
  4, hata düzeltme M, 34–35 mm (kare ≥ 0,9 mm); hepsi görüntüden okundu.
- **Yapı:** Uzar, İNCE, Çalık ve Soylu isimlikleriyle aynı: 120 × 90 mm, gövde 1 cm, yazılar 2 mm kabartma, QR
  yüzeyle aynı hizada karo, 15° eğik sehpa.
- **Kontroller:** satırlar arasında ve kenarlarda ≥ 2 mm boşluk. Küçük yazılar Manrope ExtraBold, büyük harf boyu
  4,8 mm.

```bash
python3 scripts/paloma_isimlik.py            # 10 öneri ve katalog (4 süreçte)
python3 scripts/paloma_isimlik.py dalga      # yalnız eşleşen tasarımlar
python3 scripts/paloma_isimlik.py katalog    # yalnız katalog sayfaları
```

## Dijital kartvizit sayfası

![Sayfa](sayfa_onizleme.png)

- **Üst:** lacivert, yıldızlı zemin, PALOMA ve GRIDA (logo gelince logo), altta kayan dalgalar.
- **Kart:** SB rozeti, ad soyad, görev, Paloma Grida · Paloma Hotels.
- **Düğmeler:** Ara, WhatsApp (cep numarası), E-posta, Konum (Google Haritalar).
- **Liste:** cep 0536 458 79 25, şirket hattı 0553 277 94 86, e-posta, adres (İskele Mevkii, Belek, Serik / Antalya).
- **Rehbere kaydet:** `suleyman-boylu.vcf` iner, telefonun rehberine bütün bilgiler tek dokunuşla eklenir.
- **Kartviziti paylaş:** telefonun paylaş menüsü; yoksa bağlantıyı kopyalar.
- **Yazı tipleri:** Cinzel, Fraunces, Jost; `site/fonts` içinde, yalnız kullanılan harfler (OFL).

**Bilgiler:** hepsi `bilgiler.json` içinde. Değişince iki betik yeniden çalıştırılır.

**Yayın:** ortak Cloudflare hesabında (`qrsistem`) yeni bir Worker açılır, adı tam olarak `suleymanboylu` olur ve
`paloma_site.zip` yüklenir. Adres `https://suleymanboylu.qrsistem.workers.dev/` olur; isimliklerdeki QR bu adresi
açar.

```bash
python3 scripts/paloma_sayfa.py
```
