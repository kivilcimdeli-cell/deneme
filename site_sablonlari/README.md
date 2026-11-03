# Site şablonları: lastikçi tarzı, 5 şablon, sırayla

![Katalog](katalog.png)

İsimliklerdeki QR'ın açtığı işletme siteleri (dijital kartvizit) bu beş şablondan biriyle yapılır.

- **Kural:** aksi söylenmedikçe tarz değişmez; yeni bir tasarım icat edilmez.
- **Süs yok:** "diğerleri gibi sade, modern olsun; değişik şeyler ekliyorsun". Gösterge, konsol tuşu, sayaç gibi
  ek süsler eklenmez; ilk denenen 5. şablon (Gösterge) bu yüzden kaldırıldı, yerine Sade geldi.
- **Sıra:** her yeni işletme bir sonraki şablonu alır: 1 → 2 → 3 → 4 → 5 → 1 …
- **Kayıt:** sıra `sira.json`da tutulur. Bir işletme bir kez şablon aldıysa yeniden üretimde aynı şablonda kalır.

| | Şablon | Nereden | Kısaca |
| --- | --- | --- | --- |
| 1 | **Şimşek** | Uzar Oto Lastik | dar kalın ad + şimşek (ya da işletmenin işareti), eğik şeritler, ok dişli şerit, büyük liste düğmeleri, açık renk ödeme kartı |
| 2 | **Lastik izi** | İnce Oto Lastik | eğik dar ad, lastik izi bandı, Hemen Ara'da diş baskısı, 3'erli kutucuklar, koyu banka kartı, sağ altta ara düğmesi |
| 3 | **İkaz** | Çalık Oto Lastik | ikaz şeridi, harf harf yükselen ad ve renkli nokta, 2 sütun kutucuk, altta arama şeridi |
| 4 | **Kurumsal** | Soylu Oto Lastik | sağ üstte eğik şerit, ızgara, numaralı liste (01, 02 …), üst çizgili ödeme kartı, altta arama şeridi |
| 5 | **Sade** | yeni (ilk: Auto Tufan) | süssüz ve modern: logo çizilerek gelir, solda büyük ad (harfler sırayla), kısa renkli çizgi, bağlantılar tek kartta liste, ödeme kartı, altta arama şeridi |

**Hepsinde aynı içerik:**

- Hemen Ara.
- Bağlantılar:
  - WhatsApp, hazır mesajlı;
  - Instagram;
  - Google yorumları;
  - konum ve web sitesi, varsa;
  - Rehbere kaydet (vCard).
- Ödeme bilgileri:
  - banka, alıcı;
  - IBAN, tek dokunuşla kopyalanır;
  - banka karekodu: kaydedilip banka uygulamasında galeriden okutulur.

**Dijital kartvizit (10 × 20 kurumsal isimlik):** aynı beş şablon bir kişinin kartviziti olarak da çalışır.

- `bilgiler.json`da `isletme` yerine kişinin adı, `hizmet` görevi, `etiket` kurum; ek alanlar `kurum` ve `eposta`.
- Bağlantılara E-posta eklenir; Rehbere kaydet kişiyi adı, görevi, kurumu ve e-postasıyla ekler.
- `iban` verilmezse ödeme bölümü çıkmaz.
- Örnekler: `boyde_labs/urunler/shopier/kartvizit_ornekleri/` (`scripts/boyde_site_gorsel.py 10x20`).

**Ortak davranış:**

- **Renk:** vurgu rengi işletmeye göre (`renk`); üstündeki yazı rengi kendiliğinden seçilir (açık renkte koyu yazı).
- **Uzun adlar:** büyük ad genişliğe sığdırılır; iki kelimeli uzun adlar alt alta yazılır.
- **Bağlantılar aynı sekmede açılır.** Yeni sekme, QR okuyucuların uygulama içi tarayıcılarında çoğu zaman açılmıyor.
- **Karekod kutusu:** JavaScript'siz de açılır (`#kk`).
- **Hareketi azalt:** telefonda açıksa animasyonlar oynamaz.
- **Dış bağlantı yok:** yazı tipleri ve simgeler sayfanın içinde.

**Denetim:** her üretimde önizleme alınır ve şunlar kontrol edilir:

- yazı tipleri yüklü;
- yatay taşma yok;
- yazılar sığıyor;
- büyük ad başlığa sığıyor;
- karekod okunuyor;
- sayfa hatası yok.

Her şablonun klasöründe örnek işletmesiyle `sayfa_onizleme.png` (ilk ekran ve tüm sayfa) ve `sayfa_deneme.html` (tek
dosya, telefonda açılır) var. 1–4 lastikçilerin kendi bilgileriyle. Lastikçilerin yayındaki siteleri kendi
betikleriyle (`scripts/uzar_sayfa.py` …) üretilmeye devam eder; şablonlar onların genelleştirilmiş kopyası.

## Güzellik şablonları (6–10)

![Güzellik şablonları](guzellik/katalog.png)

- **İstek:** "kuaför, beauty salonları, tırnakçılar ... 5 adet farklı internet sitesi tasarla, bu ürünlerimize uygun".
  Güzellik koleksiyonunun isimlikleri: `boyde_labs/guzellik/`.
- **Ne zaman:** kuaför, güzellik salonu, tırnak, kirpik ve kaş, cilt bakım, lazer, makyaj, spa ve gelin başı
  işletmeleri bu beş şablondan birini alır.
  - Kendi içinde sırayla döner (6 → 7 → … → 10 → 6).
  - Lastikçi sırası (1–5) değişmez.
- **İçerik ve ortak davranış yukarıdakiyle aynı:** bilgiler, bağlantılar, ödeme, denetim, dış bağlantı yok, hareketi
  azalt.
  - Farkı: WhatsApp satırı "Randevu al".
  - Ad el yazısıyla, büyük-küçük harfle yazılır (DEFNE → Defne) ve yazılır gibi soldan açılır. Harfler tek tek
    gelmez: el yazısında harfler birbirine bağlı.
- **Süsler:** çiçek, şakayık, papatya, parıltı.
  - İsimliklerdeki motiflerle aynı aile; sade kalır.
  - Gösterge, sayaç gibi ek düzenekler yok.

| | Şablon | Örnek | Kısaca |
| --- | --- | --- | --- |
| 6 | **Pudra** | Defne Kuaför | pudra zemin, köşelerde çiçekli dallar, ortalı el yazısı ad (Dancing Script), beyaz kartta liste |
| 7 | **Şakayık** | Şakayık Güzellik Salonu | vurgu renginin açığı zemin, sağ üstte iri şakayık, italik ad (Fraunces), koyu Hemen Ara, iki sütun kutucuk |
| 8 | **Gece** | Ela Lash & Brow | koyu zemin, rose gold geçişli ad (Yesteryear) ve parıltılar, altın çerçeveli satırlar |
| 9 | **Kemer** | Lâl Nails | nude zemin, kemer çerçevede logo, fırça yazısıyla ad (Kaushan), üçerli kemer kutucuklar |
| 10 | **Papatya** | Papatya Kuaför & Güzellik | vurgu renginde dalgalı başlık, papatyalar, ad (Pacifico), sarı Hemen Ara, renkli simgeli kartlar |

```bash
python3 scripts/sablon_site.py <klasör> --guzellik    # 6–10 arasında sıradaki (kayıt sira.json'da)
python3 scripts/sablon_site.py <klasör> --sablon 8    # elle
python3 scripts/sablon_site.py --katalog-guzellik     # guzellik/: örnekler ve katalog.png
```

Kod: `scripts/sablonlar/g1_pudra.py` … `g5_papatya.py`, ortak parçalar `g_ortak.py`. Örnek işletmeler uydurma
(`boyde_labs/guzellik/siteler/`); sıraya yazılmaz.

## Yeni işletmenin sitesi

1. İşletme klasöründe `bilgiler.json`:

   ```json
   {
     "isletme": "KARDEŞLER OTO YIKAMA",
     "hizmet": "OTO YIKAMA",
     "etiket": "MURATPAŞA · ANTALYA",
     "aciklama": "Aracınız pırıl pırıl. Tek dokunuşla arayın, yazın.",
     "renk": "#1E88E5",
     "telefon": "0532 123 45 67",
     "whatsapp_mesaj": "Merhaba, bilgi almak istiyorum.",
     "instagram": "@kardeslerotoyikama",
     "google": "https://g.page/r/…/review",
     "harita": "https://maps.app.goo.gl/…",
     "web": "https://…",
     "iban": "TR…",
     "iban_alici": "MEHMET KARDEŞLER",
     "banka": "Ziraat Bankası",
     "iban_karekod": "…",
     "karekod_hata": "m",
     "sayfa_url": "https://<worker adı>.qrsistem.workers.dev/"
   }
   ```

   - **Zorunlu:** `isletme` (ya da `isim`), `telefon`, `iban`.
   - **İsteğe bağlı:**
     - `marka`: büyük yazılan ad; yoksa işletme adından hizmet çıkarılır.
     - `isaret`: logo işaretinin SVG'si, klasöre göre (`logo/…svg`).
     - `isaret_cizgi`: logonun fırça darbeleri (orta çizgi ve kalınlık, JSON). Verilirse 5 · Sade'de logo yazılır
       gibi çizilir; verilmezse dış hattı çizilip içi dolar. Örnek: `autotufan_isimlik/logo/tufan_t_cizgi.json`.
     - `iban_ornek: true`: gerçek IBAN gelene kadar.
     - `sablon`: şablonu sabitlemek için.
2. Çalıştır:

   ```bash
   python3 scripts/sablon_site.py <klasör>              # sıradaki şablonla
   python3 scripts/sablon_site.py <klasör> --sablon 3   # şablonu elle seç (kayıt güncellenir)
   python3 scripts/sablon_site.py --sira                # kayıtlı işletmeler ve sıradaki şablon
   python3 scripts/sablon_site.py --katalog             # bu klasör: örnekler ve katalog.png
   ```

3. **Çıktı** (işletme klasöründe):
   - `site/`;
   - `<ad>_site.zip`;
   - `sayfa_onizleme.png`, `sayfa_tur.gif`;
   - `sayfa_deneme.html`.

   **Yayın:** ortak Cloudflare hesabında (`qrsistem`) işletmenin Worker'ına zip yüklenir.

Kod: `scripts/sablon_site.py` (üretici), `scripts/sablonlar/` (her şablon bir dosya, `ortak.py` ortak parçalar).
