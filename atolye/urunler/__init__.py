"""Ürün eklentileri. Yeni ürün: bu klasöre bir modül ve aşağıdaki SIRA listesine adı.

Bir eklentide olması gerekenler:
  KOD           kısa ad (klasör ve öğrenme kaydında)
  AD, ACIKLAMA  arayüzde ürün kartı
  KATALOG_ADET  katalogdaki örnek sayısı; 0: katalog yok, bilgiler girilince doğrudan üretilir
  ALANLAR       form: [{"ad", "etiket", "tur": text|tel|textarea|select|renk|dosya|sayi, "zorunlu", "ipucu",
                "secenekler": [(değer, etiket)], "varsayilan", "grup"}]
  KATEGORI      ana sayfadaki kategorisi (KATEGORILER'den: isimlik, anahtarlik; tanımsızsa "Diğer")
  ALT           kategori sayfasındaki alt başlığı (ör. "Güzellik koleksiyonu"; boşsa başlıksız)
  ALANLAR'da "ileri": True olan (ya da ILERI'deki adlı, zorunlu olmayan) alanlar formda kapalı "Diğer ayarlar"
  kutusunda durur: boş bırakılınca kendiliğinden dolanlar ve nadiren değişenler
  ad(bilgiler)              müşteri listesinde görünen ad
  katalog(is_)              (KATALOG_ADET > 0) is_.no'lu kataloğu üretir; döner {"tasarimlar": [{"kod", "ad",
                            "ozellikler", "onizleme"}], "pdf", "sayfalar"}
  uret(is_, kod)            seçilen tasarımın (ya da katalogsuz ürünün) dosyaları; döner {"ciktilar": [{"ad", "yol",
                            "tur"}], "uyarilar": [...]}
`is_` (isci.Is): musteri (sözlük), klasor, no, haric (bu müşteriye önceki kataloglarda gösterilen imzalar),
ilerle(yüzde, mesaj).
"""
import importlib

# ana sayfadaki kategoriler (sırayla). Kullanıcı: "isimliklerin tamamını isimlik kategorisi altında topla, açılan
# sayfadan ürünü seçip sonra bilgileri doldurayım; anahtarlıklar için de aynısı". Yeni kategori buraya eklenir.
KATEGORILER = [
    {"kod": "isimlik", "ad": "İsimlikler", "ikon": "qr",
     "aciklama": "QR'lı işletme isimliği, kurumsal ve bayraklı kişi isimlikleri, güzellik koleksiyonu"},
    {"kod": "anahtarlik", "ad": "Anahtarlıklar", "ikon": "anahtar",
     "aciklama": "Markalı toptan anahtarlık, kişiye özel plakalı anahtarlık"},
]
# formda kapalı "Diğer ayarlar" kutusuna inen alanlar (kullanıcı: "doldurmam gereken yerleri sadeleştir"): boş
# bırakılınca kendiliğinden dolar (ad işletme adından, renkler otomatik, WhatsApp telefondan, sayfa adresi addan,
# şablon sıradan) ya da nadiren değişir. Bölümde başka alan yoksa (ör. anahtarlıkta Renkler) normal görünür.
ILERI = {"marka", "cagri", "qr_yazi", "zemin", "yazi_renk", "renk", "whatsapp", "whatsapp_mesaj", "harita", "web",
         "aciklama", "site_adi", "sablon"}

SIRA = ["isimlik_9x12", "kurumsal_10x20", "guzellik_9x12", "guzellik_10x20", "bayrakli", "anahtarlik", "plakali"]


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
    alanlar = [dict(a, ileri=a.get("ileri", a["ad"] in ILERI and not a.get("zorunlu"))) for a in m.ALANLAR]
    return {"kod": m.KOD, "ad": m.AD, "aciklama": m.ACIKLAMA, "katalog_adet": m.KATALOG_ADET,
            "alanlar": alanlar, "simge": getattr(m, "SIMGE", ""), "kategori": getattr(m, "KATEGORI", "diger"),
            "alt": getattr(m, "ALT", "")}
