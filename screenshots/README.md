# Mağaza ekran görüntüleri

| Klasör | İçerik |
| --- | --- |
| `original/` | Orijinal görseller (1080×1920) |
| `layers/` | Arka planı ayrılmış ön plan katmanları (telefon + karakterler + objeler, şeffaf PNG) |
| `enhanced/` | Yenilenmiş görseller (1080×1920, RGB PNG — App Store / Google Play'e yüklemeye hazır) |
| `once_sonra.png` | Önce / sonra karşılaştırması |

## Yapılan değişiklikler

- **Arka plan:** Her görsele kendi canlı rengi (mavi, pembe, mor, yeşil, altın) — degrade, güneş ışınları, bokeh ışıkları ve silik pati izleri. Seri yan yana dizildiğinde gökkuşağı gibi akıyor.
- **Başlıklar:** Baloo 2 ExtraBold ile yeniden dizildi; kalın kontur, 3D gövde, parlama ve hafif eğim. Anahtar kelime sarı-turuncu degradeyle vurgulandı (*canlanıyor!*, *sev!*, *9*, *altın*, *Efsanevi*).
- **Alt başlık etiketi:** Her görsele özelliği anlatan kısa bir cümle eklendi.
- **Ön plan:** Telefonun arkasına parıltı, altına yumuşak gölge, kenarlara ince beyaz hâle; renkler hafifçe canlandırıldı.
- **Süsler:** Parıltı yıldızları.

## Yeniden üretme

```bash
pip install pillow numpy
python3 scripts/enhance_screenshots.py
```

Metinler, renkler ve alt başlıklar `scripts/enhance_screenshots.py` içindeki `SLIDES` listesinden değiştirilebilir.
Ön plan katmanları `rembg` (BiRefNet modeli) ile ayrıldı, küçük objeler ve altınlar ayrıca kırpılıp maskelendi.
Yazı tipi: Baloo 2 (SIL Open Font License, `scripts/fonts/OFL.txt`).
