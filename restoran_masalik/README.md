# Restoran masalıkları (30 tasarım, iki yüzlü, kabartmalı)

Müşteriye gönderilecek katalog: **`musteri_katalog.pdf`** (15 sayfa) ya da tek tek **`musteri_01.jpg` … `musteri_15.jpg`**:
- 1: kapak (masada fotoğraf, türler, örnek site)
- 2–11: her sayfada 3 tasarım, önden ve arkadan fotoğraf
- 12: 30 tasarım tek sayfada
- 13–15: 10 örnek menü sitesi telefonda (`siteler/`)

Ayrıntılı sayfalar `<numara>_<ad>.png`: iki yüzün düz görünüşü ve iki fotoğraf; ölçü, QR kontrolü ve renkler.
Fotoğraflar `foto/` klasöründe.

Restoran isimleri uydurma, katalog için. Seçilen tasarım işletmenin adı, logosu, renkleri ve masa numaralarıyla
yeniden hazırlanır.

**Üç tür:**
- **İKİ QR:** ön yüzde menü, arka yüzde Google yorumu.
- **TEK QR:** iki yüzde aynı QR → işletmenin tek sayfası (menü, yorum, Wi-Fi, Instagram, rezervasyon).
- **NFC + QR:** Ø25 mm NTAG215 etiket iki plakanın arasında; telefonu dokundurmak yeter, iki yüzden de okunur.
- 6 numarada arka yüz misafir Wi-Fi QR'ıdır.

QR'lar doğrudan Google'a ya da menü dosyasına değil, ortak hesaptaki sayfaya gider
(`<ad>.qrsistem.workers.dev/menu`, `/yorum`). Menü ya da bağlantı değişse de masalık değişmez. Örneklerdeki adresler
henüz yayında değil.

| No | İsim | Tür | QR | Ölçü (en × boy, ayakla) | Ayak | Masa no |
| --- | --- | --- | --- | --- | --- | --- |
| 01 | Kaleiçi Sofrası | Osmanlı mutfağı | İKİ QR | 12,4 × 16,2 cm | ahşap ayak 124 × 42 mm | MASA 07 |
| 02 | Mavi Lagün | balık evi | TEK QR | 16,8 × 11,9 cm | lacivert dalgalı ayak 150 × 44 mm | MASA 07 |
| 03 | Forno Rosso | pizzeria | İKİ QR | 11,2 × 16,8 cm | siyah yuvarlak ayak Ø72 mm (pizza taşı gibi) | MASA 07 |
| 04 | Garaj Burger | burger & co, | NFC + QR | 12,0 × 15,0 cm | antrasit ayak 120 × 44 mm, hardal şerit | MASA 12 |
| 05 | Zeytinlik | meze evi | İKİ QR | 9,6 × 18,4 cm | ahşap oval ayak 96 × 48 mm | MASA 05 |
| 06 | Köpük | kahve & espresso | QR + Wi-Fi | 12,8 × 13,9 cm | fildişi fincan tabağı Ø124 mm, latte kenar | – |
| 07 | Lavanta | bistro | NFC + QR | 9,6 × 14,8 cm | ipek altın oval ayak 88 × 36 mm | MASA 07 |
| 08 | Ateş | ocakbaşı | İKİ QR | 9,6 × 17,5 cm | antrasit altıgen ayak, ipek bakır halka | MASA 14 |
| 09 | Limon Ağacı | kahvaltı evi | TEK QR | 12,0 × 16,0 cm | koyu yeşil yuvarlak ayak Ø68 mm | MASA 09 |
| 10 | Koi | sushi & ramen | NFC + QR | 14,0 × 12,2 cm | siyah ayak 140 × 36 mm, çubuk yuvalı | MASA 08 |
| 11 | Taş Fırın | pide & lahmacun | İKİ QR | 19,0 × 9,1 cm | ahşap ayak 160 × 38 mm | MASA 04 |
| 12 | Kar Tanesi | dondurma | TEK QR | 9,2 × 17,2 cm | pembe yuvarlak ayak Ø64 mm | – |
| 13 | Asmaaltı | çay bahçesi | İKİ QR | 9,6 × 14,5 cm | beyaz çay tabağı Ø96 mm, bordo kenar | MASA 11 |
| 14 | Kasaphane | et lokantası · 1974 | İKİ QR | 11,2 × 15,0 cm | takılır çapraz ahşap ayak | MASA 07 |
| 15 | Yayla | gözleme evi | İKİ QR | 12,6 × 15,8 cm | siyah basamaklı ayak 126 × 46 mm | MASA 07 |
| 16 | Palmiye | beach club | NFC + QR | 11,0 × 18,4 cm | kum rengi dalgalı ayak 110 × 44 mm | MASA 12 |
| 17 | Tatlı Rüya | pastane | İKİ QR | 13,2 × 11,1 cm | fildişi kademeli kek standı Ø88 mm | MASA 04 |
| 18 | Gurme Masa | fine dining | TEK QR | 15,8 × 13,4 cm | antrasit kaide 158 × 34 mm | MASA 01 |
| 19 | Bostan | vegan mutfak | NFC + QR | 9,0 × 19,9 cm | terrakota saksı Ø72 mm | MASA 06 |
| 20 | Nonna | ev yapımı makarna | İKİ QR | 10,8 × 14,2 cm | A tipi: iki panel, ahşap tepe bağlantısı | MASA 05 |
| 21 | Fıstıkzade | baklava | TEK QR | 11,9 × 16,2 cm | koyu yeşil ayak 64 × 44 mm, altın çizgi | MASA 03 |
| 22 | Taco Loco | Meksika mutfağı | NFC + QR | 12,4 × 16,5 cm | kum rengi ayak 124 × 46 mm, mercan zikzak | MASA 07 |
| 23 | Wok Ustası | noodle bar | İKİ QR | 11,1 × 16,2 cm | siyah ayak 100 × 38 mm | MASA 09 |
| 24 | Döner Sokak | dürüm & döner | TEK QR | 14,6 × 15,7 cm | gri yuvarlak ayak Ø72 mm | MASA 07 |
| 25 | Gün Batımı | teras restoran | NFC + QR | 17,6 × 9,7 cm | lacivert dalgalı ayak 176 × 46 mm (deniz) | MASA 12 |
| 26 | Liman | cafe & balık | İKİ QR | 12,8 × 14,0 cm | lacivert yuvarlak ayak Ø76 mm, halat çizgisi | MASA 03 |
| 27 | Rooftop 360 | kokteyl & mutfak | NFC + QR | 9,2 × 17,8 cm | ipek altın ince kaide 92 × 26 mm | MASA 21 |
| 28 | Tost Durağı | tost & kumru | İKİ QR | 16,0 × 9,4 cm | turkuaz ayak 150 × 34 mm | MASA 15 |
| 29 | Annemin Mutfağı | ev yemekleri | İKİ QR | 12,4 × 12,6 cm | kırmızı peçetelik ayağı 124 × 58 mm, iki yuva | MASA 02 |
| 30 | Mahalle Köftecisi | ızgara köfte | İKİ QR | 20,0 × 14,6 cm | tuzluk-biberlik, kürdan ve şeker yuvalı düzenleyici 200 × 64 mm | MASA 07 |

**Yapı (baskıya göre):**
- **İki plaka sırt sırta:** her biri 3 mm, her yüz kendi plakası. Yüzü yukarı basılır; ikisi birlikte ayaktaki
  yuvaya oturur (yuva 6,3 mm, 8 mm derin).
- **Kabartma:**
  - geniş renk alanları (etiket, şerit, dilim) 0,8 mm kabarık zemin;
  - yazı, çerçeve, simge, yıldız 1 mm kabartma, zeminin de üstünde;
  - QR 0,8 mm kabarık karoda, koyu kareler karonun üstüne 0,6 mm gömülü. Yüzeyi düz kalır, okunur.
- **NFC:** etiket, ön plakanın arkasındaki Ø26 × 0,6 mm cebe konur ve iki plaka arasında kalır. Baskıyı duraklatmak
  gerekmez.
- **Özel ayaklar:**
  - 14: takılır çapraz ayak;
  - 20: A tipi, iki tek plaka ve ahşap tepe bağlantısı;
  - 29: peçetelik, iki plaka iki yuvada;
  - 30: tuzluk-biberlik, kürdan ve şeker yuvalı düzenleyici.

**Kontroller:**
- 60 QR'ın hepsi düz görünüşte ve baskı hatası benzetiminde okundu; en küçük QR karesi 0,96 mm.
- Yazıların her harfinin yazı tipinde olduğu denetlenir.
- 0,6 mm'den ince yerler ölçülür.

**Görseller:**
- `scripts/restoran_masalik_foto.py`: Blender 4.2 Cycles ile ahşap masada stüdyo fotoğrafı. Mat PLA, ipek altın ve
  bakır, ahşap PLA; ayaklarda 0,2 mm katman izleri; alan derinliği.
- `scripts/menu_siteleri.py`: masalıklarla aynı stilde 10 telefon sitesi.

**Yazı tipleri (OFL):**
- Başlıklar: Fraunces, Playfair Display, Cinzel, Bodoni Moda, Anton, Big Shoulders, Archivo, Bricolage, Syne,
  Unbounded, Barlow, Righteous, Norican, Caveat.
- Küçük yazılar: Jost.

```bash
pip install bpy==4.2.0                                # bir kez
python3 scripts/restoran_masalik_foto.py --kapak      # kapak fotoğrafı
python3 scripts/restoran_masalik_foto.py [ad ...]     # tasarım fotoğrafları (~1,5 dk / tasarım)
python3 scripts/menu_siteleri.py                      # 10 site ve ekran görüntüleri
python3 scripts/restoran_masalik.py                   # kontroller, ayrıntı sayfaları ve katalog
python3 scripts/restoran_masalik.py katalog           # yalnız katalog (önbellekten)
```
