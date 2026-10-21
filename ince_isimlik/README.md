# İNCE OTO LASTİK – tek QR'lı tezgâh isimliği önerileri

Müşteriye gönderilecek katalog: **`musteri_1.png`** (1–6), **`musteri_2.png`** (7–10), ikisi birlikte
**`musteri_katalog.pdf`**. Ayrıntılı sayfalar: `<numara>_<ad>.png` (önden, tezgâhta, yandan).

- 1–7 beyaz zemin (siyah, kırmızı yazı), 8–10 siyah zemin (beyaz, kırmızı yazı). Her biri ayrı fikir ve yazı tipi:
  1 Plaka · 2 Minimal · 3 Kırmızı blok · 4 Yol · 5 Dama bayrağı · 6 Hız çizgileri · 7 Jant · 8 Kırmızı köşe ·
  9 Kırmızı çerçeve · 10 Oklar.
- İçerik: İNCE, OTO LASTİK, 7/24 HİZMET, telefon **0545 853 30 70**, tek QR. Süsler kalın ve sade (kolay basılır).
- Yapı Uzar Oto Lastik'in basılan isimliğiyle aynı: 120 × 90 mm, köşeler R8, gövde 1 cm, yazılar ve simge 2 mm
  kabartma, QR yüzeyle aynı hizada (beyaz zeminde siyah kareler, siyah zeminde beyaz karo), 15° eğik sehpa.
- Küçük satırlar Outfit ExtraBold: harf içi boşluklar kabartmada dolmasın diye her satır ölçülür (en dar ≥ 0,6 mm).

**QR:** işletmenin sitesi henüz yok; örneklerde QR telefonu arar (`TEL:+905458533070`). Site hazır olunca adresi
`bilgiler.json` → `sayfa_url`a yazılır, QR site adresine döner (seçilen tasarım o zaman X2D dosyasına çevrilir;
`scripts/uzar_isimlik_baski.py` örnek alınır).

```bash
python3 scripts/ince_isimlik.py           # 10 öneri ve katalog
python3 scripts/ince_isimlik.py klasik    # yalnız eşleşen tasarımlar
```

## İşletme sayfası (QR'ın açacağı site)

![Sayfa](sayfa_onizleme.png)

Uzar'ın sayfasıyla aynı işleri yapar; tasarımı farklıdır. Siyah zemin, yarış havası: eğik, dar ve kalın Saira
Condensed Black Italic, tek vurgu rengi kırmızı. Lastik çizimi yok; tasarımın dili lastik izi, yani gidiş yönüne bakan
ok biçimli diş baskısı (Hemen Ara düğmesindeki desen):

- **Başlık:** logonun arkasından çapraz geçen büyük diş bandı.
- **Desen tekrarı:** kutucukların ve IBAN kartının köşesinde, altbilgide aynı baskı.
- **Ödeme:** banka kartı gibi tasarlanmış IBAN kartı (banka, IBAN, alıcı); altında Kopyala ve Karekod düğmeleri.

**Animasyon** (`sayfa_animasyon.gif`, tam tur: `sayfa_tur.gif`):

- **Açılış:** diş bandı yuvarlanarak gelip durur, İNCE harf harf yükselir, OTO LASTİK soldan açılır, düğmeler
  sırayla gelir. Hemen Ara'nın diş baskısı akıp durur, telefon bir kez çalar.
- **Kaydırma:** desenler kaydırdıkça akar. IBAN kartı göründüğünde üzerinden ışık geçer. Hemen Ara ekrandan
  çıkınca sağ altta kırmızı ara düğmesi belirir.
- **Sürekli:** yalnız küçük işaretler oynar. 7/24 noktası atar; Hemen Ara birkaç saniyede bir parlar ve telefon
  çalar.

Dönen bir şey yok. Telefonda "hareketi azalt" açıksa animasyonlar oynamaz.

**İçerik:**

- Hemen Ara: 0545 853 30 70
- WhatsApp: aynı numara, hazır mesajla açılır.
- Instagram: @enesssahin.7
- Google yorumları: işletmenin `share.google` bağlantısı.
- Ödeme: HAFİSE İNCE, DenizBank. IBAN tek dokunuşla kopyalanır; karekod kaydedilip banka uygulamasında galeriden
  okutulur.
- Rehbere Kaydet.

**Karekod:** fotoğraftaki DenizBank karekodundan okundu. CRC tutuyor, içindeki IBAN ve alıcı `bilgiler.json` ile
aynı. Sayfadaki karekod bankanınkiyle aynı baytlarla çizilir (UTF-8, hata düzeltme Q), bu yüzden İ harfleri banka
uygulamasında bozulmaz. Karekodun içinde 19.10.2029 tarihi var; geçerlilik süresi olabilir.

**Yayın:** Uzar'daki gibi işletmenin Cloudflare hesabında yeni bir Worker açılır ve `ince_site.zip` yüklenir.
Sonra:

1. Adresi (`…workers.dev`) `bilgiler.json` → `sayfa_url` alanına yaz.
2. `python3 scripts/ince_sayfa.py` çalıştır; paylaşım kartı adresi kullanır.
3. `python3 scripts/ince_isimlik.py` çalıştır; isimlikteki QR siteye döner.

`sayfa_onizleme.html` tek dosyalık önizlemedir (yazı tipleri ve karekod gömülü).

**Claude önizlemesi:** `sayfa_artifact.html` yalnız kontrol içindir; sitenin kendisi değildir.
Orada üstte Claude yazar, Hemen Ara numarayı kopyalar, karekod ve rehber indirme bağlantıları yoktur.
