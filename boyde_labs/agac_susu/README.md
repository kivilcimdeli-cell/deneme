# Yılbaşı ağaç süsü seti (7'li): reklam görselleri

Kullanıcı: dikey basılan anahtarlıklar tablada devrildi; yerine düz basılan, eklemli ağaç süsleri 7'li set olarak
satılacak; eski yılbaşı anahtarlık ilanları Shopier ve Trendyol'dan kaldırılacak.

**`agac_susu_reklam.zip`**
- `shopier/`: 7 görsel (1200 × 1200) ve `aciklama.txt`.
  - Görseller: kapak · sette neler var · dala asın · eklemli · renkli baskı · ölçü ve özellikler · nasıl sipariş.
- `trendyol/`: 7 fotoğraf (1200 × 1800) ve `ilan.txt` (başlık, kategori önerisi, açıklama, özellikler).
  - Fotoğraflarda yazı, logo ve fiyat yok.
- `instagram/`: gönderi (1080 × 1350) ve hikaye (1080 × 1920).

**Figürler**
- Ayıcık kullanıcının 3MF'inden alındı (`3mf/atkili_ayicik.3mf`; yakın çekim tam 3D).
- Diğer altısı kullanıcının görselinden kesildi (`kaynak_set.webp`, `scripts/agac_susu_kes.py`).
- Çam dalı ve kırmızı askı ipleri Blender'da 3D çizildi; kesik figürler ipin ucuna, gerçek boyda yerleştirildi
  (`scripts/agac_susu_kompozit.py`).
- 3MF'ler gelince aynı çekimler figürlerin kendisiyle yenilenebilir.

**Metinlerde varsayılanlar (kullanıcı onaylamalı)**
- Her süsün kırmızı askı ipi takılı gelir.
- Boyut ~4 × 3 × 1 cm.
- Eklemli: kollar ve bacaklar oynar (ayıcığın 3MF'inde kollar ve bacaklar ayrı parça).
- 3 yaş altına uygun değil.

```bash
python3 scripts/agac_susu_kes.py
python3 scripts/agac_susu_kompozit.py      # dala asılı çekimler (yazısız)
python3 scripts/agac_susu_foto.py detay    # ayıcık yakın (3MF)
python3 scripts/agac_susu_reklam.py        # Shopier, Trendyol, Instagram ve zip
```
