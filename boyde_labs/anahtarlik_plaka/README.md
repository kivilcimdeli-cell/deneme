# BOYDE LABS · kişiye özel plakalı anahtarlık

![Shopier kapağı](shopier/01_kapak.jpg)

İstek: "Shopier'e yüklememiz gereken bir ürün daha var: kişiye özel plakalı anahtarlık; STL dosyası ve bütün ürün
bilgileri burada" (Bambu Studio örneği, `Birleştir.stl`). "Kırmızı versiyonunda yap TR yazısını."

## Model (`scripts/boyde_plakali_anahtarlik.py`)

Ölçüler kullanıcının STL'inden: 70 × 22 mm, köşe R3,6; 2 mm siyah çerçeve, alt şerit (adın zemini), beyaz plaka
zemini, solda TR bandı. Örnekte TR bandı maviydi; istek üzerine **kırmızı**, TR beyaz.

| Katman (z, mm) | Renk | Ne |
| --- | --- | --- |
| 0–2,0 | siyah | çerçeve ve alt şerit |
| 0–1,0 | beyaz | plaka zemini |
| 0–1,2 | kırmızı | TR bandı |
| 1,0–2,3 | siyah | plaka yazısı, 1,3 mm kabartma (Saira SemiBold, DIN benzeri; büyük harf boyu ~6,5 mm) |
| 1,2–1,9 | beyaz | TR |
| 2,0–3,0 | beyaz | ad ya da söz, 1 mm kabartma (Outfit ExtraBold) |

- **Delik:** Ø3,5 mm, TR bandının sol üstünde (üstte 2,45, solda 3,25 mm et). Kullanıcının örneğinde kesici gövdeydi,
  birleştirince STL'e çıkmamıştı.
- **Ad:** genişliğe sığdırılır; İ noktaları ve Ğ işaretiyle şeride sığmazsa küçülür. Küçük boyda da harf içi ve İ
  noktası ≥ 0,7 mm kalsın diye Outfit ExtraBold (Montserrat'ta noktalar 0,7 mm'nin altına iniyordu).
- **Kontrol:** yazılar zeminden taşmaz (kırpılan 0), 0,7 mm'den ince kalan yer yok.

Örnek yazılar uydurma (gerçek plaka ya da kişi değil): 34 BYD 34 · BOYDE LABS, 06 BYD 06 · ADINIZ SOYADINIZ,
35 BYD 35 · İSİM SOYİSİM; kapakta ayrıca 16, 07 ve 01.

## Fotoğraflar (`fotograf/`)

| Dosya | Ne |
| --- | --- |
| `<model>_iki.jpg` | masada iki adet: biri önden, biri ters (düz arka yüz) |
| `<model>_halka.jpg` | zincirli halka takımında asılı (delik sol üstte: plaka dik asılır) |
| `kapak.jpg` | altı farklı plaka masada, önden |
| `uc.jpg` | üç örnek alt alta |

## Shopier (`shopier/`, 1200 × 1200, yükleme sırasıyla)

| Dosya | Ne |
| --- | --- |
| `01_kapak.jpg` | altı plaka, "Plakalı anahtarlık" |
| `02_uc_ornek.jpg` | üç örnek, plaka ve yazıları |
| `03_p01_onlu_arkali.jpg` … `05_p03_onlu_arkali.jpg` | her örnek önlü arkalı, BOYDE çerçevesinde |
| `06_halka.jpg` | zincirli halka takımıyla |
| `07_olcu_ozellik.jpg` | ön görünüş 70 × 22 mm, renkler, özellikler |
| `08_nasil_siparis.jpg` | dört adım, WhatsApp |

Ürün adı ve açıklaması: `boyde_labs/urunler/shopier/urun_metinleri.md` (6. ürün).

## Yeniden üretmek

```bash
python3 scripts/boyde_plakali_anahtarlik.py            # modeller, ön ve arka görünüş, kontrol
python3 scripts/boyde_plakali_anahtarlik.py --foto     # Blender fotoğrafları (bpy 4.2)
python3 scripts/boyde_plakali_anahtarlik.py --shopier  # Shopier görselleri
```
