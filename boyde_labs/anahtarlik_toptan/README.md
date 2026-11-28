# BOYDE LABS · toptan anahtarlık kataloğu

![Katalog](katalog.png)

İstekler:
- "Toptan anahtarlık için bir katalog hazırla, BOYDE olsun, 5 anahtarlık örneği çiz, bazı fotoğraflara anahtarlık
  halkası da ekle."
- "Hepsi standart anahtarlık şeklinde (dikdörtgen vs.) olsun, markaları sallama, BOYDE LABS olarak yap."
- "Ön yüz kabartmalı yazı, arka yüz düz yazı; arkalı önlü, tek karede iki açıdan görünsün."
- "Katman katmanı sil, 'Her katman size özel' yaz."
- "Yazılar hizalanmamış gibi; anahtarlık halkaları gönderdiğim görseldeki gibi olmalı" (çelik halka, kısa zincir,
  ara halka).

## Modeller

| Kod | Model | Ölçü | Renkler | Kısaca |
| --- | --- | --- | --- | --- |
| K01 | Klasik | 60 × 30 mm | siyah · beyaz · turuncu | delik solda; işaret ve BOYDE LABS yan yana |
| K02 | Dikey etiket | 30 × 56 mm | beyaz · siyah · turuncu | delik üstte; işaret üstte, yazı altında |
| K03 | Kare | 40 × 40 mm | turuncu · siyah · beyaz | delik köşede; büyük işaret, altında yazı |
| K04 | Bar | 72 × 24 mm | siyah · beyaz · turuncu | delik sağda; büyük BOYDE LABS, yanında katman şeritleri |
| K05 | Kesik köşe | 56 × 32 mm | gri · siyah · turuncu · beyaz | sağ üst köşe kesik, delik orada (kesik kenardan 3,5 mm et payıyla) |

- **Ön yüz:** 3b · Katman işareti ve BOYDE / LABS 0,8 mm (4 katman) kabartma, renkli.
- **Arka yüz:** "Her katman size özel." ve shopier.com/boyde; yüzeyle aynı hizada gömme renk (0,6 mm, tablaya
  bakan ilk 3 katman).
- **Gövde:** 3,2 mm, alt ve üst kenarda 3 katmanlık pah; delik Ø5,2 mm, çevresinde en az 3,5 mm et.
- **Hizalama:** deliğin payı çıkınca kalan alan bulunur; ön yüz grubu bu alanın tam ortasında, alt alta olanlar
  (işaret ve yazı, arka satırlar) aynı dikey eksende, sınır kutularıyla ortalı. Arka yüz aynı alanın aynasında
  ortalı (arkadan bakınca delik öbür yanda). Kenara ya da deliğe taşan öğe yok (betik ölçer: kırpılan alan 0).
- **Baskıya uygunluk:** kabartma kenardan 1 mm, delikten 0,8 mm içeride.
  - LABS en az 4,2 mm ve kalın; 3 mm'de çizgileri 0,5 mm kalıyordu.
  - İşaretteki nozulun 0,7 mm'den dar yarıkları kapalı. Katman çizgileri 0,15 mm ince, araları 0,7 mm'nin
    üstünde.
  - Arka yüzdeki i, ö noktaları ve noktalama biraz büyütüldü (silinmesin).
  - Ölçülen: 0,7 mm'den ince ya da 0,6 mm'den dar kalan alan model başına ≤ 1,1 mm² (harf köşeleri).

## Fotoğraflar (`fotograf/`)

| Dosya | Ne |
| --- | --- |
| `<model>_iki.jpg` | masada iki adet: biri önden (kabartma), biri ters çevrilmiş (arka yüz) |
| `<model>_halka.jpg` | zincirli halka takımında asılı iki adet: biri önünü, biri arkasını gösterir |
| `kapak.jpg` | 12 adet K01 (yarısı önden, yarısı arkadan) ve iki boş halka takımı: toptan parti |
| `dizi.jpg` | beş model halka takımlarıyla yan yana |

- Halka takımı (gönderilen görseldeki gibi): Ø25 mm çelik halka (iki tur), 4 halkalık zincir (halkalar sırayla
  90° dönük) ve deliğin içinden geçen Ø7 mm ara halka. Her halka bir öncekinin teline dik; ara halka yüze dik,
  deliğin en yakın kenarından geçer.
- Fon: koyu anahtarlıklar beyaz fonda, beyaz gövdeli K02 logodaki siyahta.

## Shopier (`shopier/`, 1200 × 1200, yükleme sırasıyla)

| Dosya | Ne |
| --- | --- |
| `01_kapak.jpg` | toptan parti fotoğrafı, "Toptan anahtarlık" |
| `02_bes_model.jpg` | beş model halka takımlarıyla, kodları |
| `03_K01_…_halka.jpg` … `07_K05_…_halka.jpg` | her model zincirli halka takımıyla (solda ön, sağda arka yüz), BOYDE çerçevesinde |
| `08_K01_…_arkali_onlu.jpg` … `12_K05_…_arkali_onlu.jpg` | her model masada arkalı önlü, BOYDE çerçevesinde |
| `13_olcu_ozellik.jpg` | beş biçim gerçek oranlarıyla (ön ve arka), özellikler |
| `14_nasil_siparis.jpg` | dört adım, WhatsApp |

Ürün adı ve açıklaması: `boyde_labs/urunler/shopier/urun_metinleri.md` (4. ürün).

## Katalog

`katalog.pdf` (A4, 6 sayfa):
1. Kapak
2. Arkalı önlü: özellikler ve sipariş adımları
3–5. Modeller: her biri arkalı önlü ve halkalı fotoğrafıyla
6. Teklif: WhatsApp ve shopier.com/boyde

Fiyat yazılmadı; "adet arttıkça birim fiyat düşer, teklif alın".

## Yeniden üretmek

```bash
python3 scripts/boyde_anahtarlik_toptan.py            # modeller, ön ve arka görünüş, baskı kontrolü
python3 scripts/boyde_anahtarlik_toptan.py --foto     # Blender fotoğrafları (~15 dk)
python3 scripts/boyde_anahtarlik_toptan.py --katalog  # katalog.pdf ve katalog.png
python3 scripts/boyde_anahtarlik_toptan.py --shopier  # Shopier görselleri
```
