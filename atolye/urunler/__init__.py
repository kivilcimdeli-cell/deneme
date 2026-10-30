"""Ürün eklentileri. Yeni ürün: bu klasöre bir modül ve aşağıdaki SIRA listesine adı.

Bir eklentide olması gerekenler:
  KOD           kısa ad (klasör ve öğrenme kaydında)
  AD, ACIKLAMA  arayüzde ürün kartı
  KATALOG_ADET  katalogdaki örnek sayısı; 0: katalog yok, bilgiler girilince doğrudan üretilir
  ALANLAR       form: [{"ad", "etiket", "tur": text|tel|textarea|select|renk|dosya|sayi, "zorunlu", "ipucu",
                "secenekler": [(değer, etiket)], "varsayilan", "grup"}]
  ad(bilgiler)              müşteri listesinde görünen ad
  katalog(is_)              (KATALOG_ADET > 0) is_.no'lu kataloğu üretir; döner {"tasarimlar": [{"kod", "ad",
                            "ozellikler", "onizleme"}], "pdf", "sayfalar"}
  uret(is_, kod)            seçilen tasarımın (ya da katalogsuz ürünün) dosyaları; döner {"ciktilar": [{"ad", "yol",
                            "tur"}], "uyarilar": [...]}
`is_` (isci.Is): musteri (sözlük), klasor, no, haric (bu müşteriye önceki kataloglarda gösterilen imzalar),
ilerle(yüzde, mesaj).
"""
import importlib

SIRA = ["isimlik_9x12", "kurumsal_10x20", "bayrakli", "anahtarlik"]


def hepsi():
    out = []
    for ad in SIRA:
        try:
            out.append(importlib.import_module(f"atolye.urunler.{ad}"))
        except ModuleNotFoundError as e:
            if e.name != f"atolye.urunler.{ad}":
                raise
    return out


def bul(kod):
    for m in hepsi():
        if m.KOD == kod:
            return m
    raise KeyError(kod)


def tanim(m):
    """Arayüze giden ürün tanımı."""
    return {"kod": m.KOD, "ad": m.AD, "aciklama": m.ACIKLAMA, "katalog_adet": m.KATALOG_ADET,
            "alanlar": m.ALANLAR, "simge": getattr(m, "SIMGE", "")}
