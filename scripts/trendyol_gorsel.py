"""Trendyol bilgi görselleri (1200 × 1800) ve ilan metinleri: isimlikler, plakalı anahtarlık, yılbaşı seti.

Trendyol görsel kuralları (satıcı rehberleri): ilan başına en çok 8 görsel; görselde logo, web adresi, iletişim
bilgisi, fiyat olmamalı. Bu yüzden:
- BOYDE logosu, telefon, WhatsApp, Shopier yok. Örnek isimlik ve sitelerde telefon 0500 000 00 00, Instagram
  @isletmeniz (yer tutucu).
- Bilgi görselleri ilanın SON görselleri (7, 8): yazı içerir; Trendyol reddederse çıkarılır, fotoğraflar (1–6) kalır.
- Sipariş Trendyol içinden: müşteri bilgilerini sipariş detayındaki "Satıcıya Sor"dan yazar.

  7_qr_sayfa     QR'ı okutunca açılan sayfa (telefonda), yanında isimliğin fotoğrafı  (bayraklıda yok)
  8_olcu_siparis düz görünüş ve ölçüler, özellikler, nasıl sipariş verilir (Satıcıya Sor)
Metinler: boyde_labs/trendyol/<ilan>/ilan.txt (başlık, açıklama, kategori ve özellik önerileri).

Önce fotoğraflar: python3 scripts/trendyol_foto.py. Sonra: python3 scripts/trendyol_gorsel.py [ilan ...]
Çıktı: boyde_labs/trendyol/<ilan>/01..08.jpg ve ilan.txt
"""
import os
import shutil
import sys
import tempfile

# boyde_site_gorsel → boyde_urunler örnek modu telefonu her siteye BOYDE_TEL olarak basar: yer tutucu numara
os.environ.setdefault("BOYDE_TEL", "905000000000")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_katalog as K  # noqa: E402
import boyde_marka as BM  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TY = os.path.join(ROOT, "boyde_labs", "trendyol")
FOTO = os.path.join(TY, "foto")
KAYNAK = os.path.join(TY, "kaynak")
INK, PAPER, ORANGE, GRAY = BM.INK, BM.PAPER, BM.ORANGE, BM.GRAY
W, H = 1200, 1800
SAHTE = {"telefon": "0500 000 00 00", "instagram": "@isletmeniz"}
SITE_GENEL = os.path.join(ROOT, "boyde_labs", "urunler", "siteler")
SITE_GUZ = os.path.join(ROOT, "boyde_labs", "guzellik", "siteler")

ILAN = {
    "masa_9x12": {
        "site_foto": "4_tek_telefon",
        "ad": "QR'lı masa isimliği", "olcu": ("120 mm", "90 mm"), "duz": "soylu", "site": (SITE_GENEL, "cagri", 1),
        "qr_baslik": "Müşteriniz okutur,<br>sayfanız açılır.",
        "cips": ["Ara", "WhatsApp", "Instagram", "Konum", "Google yorum", "IBAN"],
        "ozellik": ["120 × 90 mm, 1 cm kalın gövde", "Yazı ve logo 2 mm kabartma, renkli",
                    "QR yüzeyle aynı hizada: keskin, kolay okunur", "15° eğik sehpa dahil",
                    "QR, işletmenize özel sayfayı açar"],
        "bilgi": "işletme adı, logo (Instagram hesabınızı yazmanız yeterli), telefon, adres, IBAN, renk tercihi"},
    "kurumsal_10x20": {
        "site_foto": "3_tek_avukat",
        "ad": "Kurumsal isimlik", "olcu": ("200 mm", "100 mm"), "duz": "avukat", "site": (SITE_GENEL, "kaya", 4),
        "qr_baslik": "QR'ı okutan,<br>kartvizitinizi açar.",
        "cips": ["Ara", "WhatsApp", "E-posta", "Konum", "Rehbere kaydet"],
        "ozellik": ["200 × 100 mm, 5 mm gövde", "Yazılar yüzeyle aynı hizada, renkli",
                    "Kurum logosu ve renkleri", "Sehpa dahil", "QR, dijital kartvizit sayfanızı açar"],
        "bilgi": "ad soyad, unvan, kurum, telefon, e-posta, logo (web sitesi ya da Instagram), renk tercihi"},
    "bayrakli": {
        "ad": "Türk bayraklı masa isimliği", "olcu": ("240 mm", "56 mm"), "duz": "bayrakli", "site": None,
        "ozellik": ["Blok 240 × 56 × 32 mm, dolu ve sağlam", "Ay yıldız ve ad soyad 2 mm kabartma",
                    "Bayrak kırmızısı, siyah ve beyaz", "Siyah sehpa dahil (200 mm), 12° arkaya eğik",
                    "Uzun adlarda yazı sığacak kadar küçülür"],
        "bilgi": "isimlikte yazacak ad soyad"},
    "guzellik_9x12": {
        "site_foto": "3_tek_g_defne",
        "ad": "Kuaför ve güzellik salonu isimliği", "olcu": ("120 mm", "90 mm"), "duz": "g_sakayik",
        "site": (SITE_GUZ, "defne", 6), "qr_baslik": "Müşteriniz okutur,<br>randevu tek dokunuşla.",
        "cips": ["Ara", "Randevu (WhatsApp)", "Instagram", "Konum", "Google yorum", "IBAN"],
        "ozellik": ["120 × 90 mm, 1 cm kalın gövde", "Yazı ve çiçek motifleri 2 mm kabartma",
                    "Pembe, nude, lila, krem tonları", "15° eğik sehpa dahil",
                    "QR, salonunuza özel sayfayı açar"],
        "bilgi": "salon adı, logo (Instagram hesabınızı yazmanız yeterli), telefon, adres, IBAN, sevdiğiniz renkler"},
    "guzellik_10x20": {
        "site_foto": "1_ana",
        "ad": "Güzellik uzmanı isimliği", "olcu": ("200 mm", "100 mm"), "duz": "p_buse",
        "site": (SITE_GUZ, "kisi_buse", 9), "qr_baslik": "QR'ı okutan,<br>kartvizitinizi açar.",
        "cips": ["Ara", "Randevu (WhatsApp)", "Instagram", "Konum", "Rehbere kaydet"],
        "ozellik": ["200 × 100 mm, 5 mm gövde", "Adınız el yazısıyla, yazılar yüzeyle aynı hizada",
                    "Çiçek, oje, kirpik, ruj motifleri", "Sehpa dahil", "QR, dijital kartvizitinizi açar"],
        "bilgi": "ad soyad, unvan, salon adı, telefon, Instagram, sevdiğiniz renkler"},
    "plakali_anahtarlik": {
        "ad": "Plakalı anahtarlık", "olcu": ("70 mm", "22 mm"), "site": None,
        "duz_yol": os.path.join(TY, "kaynak_plaka", "p01_on.png"),
        "fotolar": [("plaka", f) for f in ("kapak", "p01_halka", "p01_iki", "renk", "p02_halka", "p03_halka",
                                           "p02_iki")],
        "ozellik": ["70 × 22 × 3 mm, sağlam PLA gövde", "Plaka yazısı 1,3 mm, ad soyad 1 mm kabartma",
                    "Kırmızı ya da mavi TR bandı, beyaz plaka zemini, siyah çerçeve", "Arka yüz düz siyah",
                    "Çelik halka, kısa zincir ve ara halka takılı gelir"],
        "adim": [("Siparişinizi verin", "TR bandının rengini (kırmızı ya da mavi) seçin."),
                 ("Plakanızı ve yazınızı yazın", "Sipariş detayındaki <b>“Satıcıya Sor”</b>dan: plaka ve altına "
                  "yazılacak ad soyad ya da kısa söz."),
                 ("Onaylayın", "Önizlemeyi hazırlayıp onayınıza sunuyoruz."),
                 ("Üretip gönderiyoruz", "Kendi atölyemizde 3D baskıyla üretip kargoya veriyoruz.")]},
    "yilbasi_seti": {"ad": "Yılbaşı anahtarlık seti (6'lı)", "site": None, "set": True,
                     "fotolar": [("yilbasi", "set"), ("_kolaj", "kolaj"), ("yilbasi", "noel_baba_iki"),
                                 ("yilbasi", "ren_geyigi_halka"), ("yilbasi", "atkili_ayicik_halka"),
                                 ("yilbasi", "kardan_adam_halka"), ("yilbasi", "kutup_ayisi_halka")]},
}


ORTAK_SON = """
SİPARİŞTEN SONRA
Sipariş detayınızdaki "Satıcıya Sor" bölümünden bilgilerinizi yazın. Tasarımınızı hazırlayıp yine buradan onayınıza
sunuyoruz; onayınızdan sonra kendi atölyemizde 3D baskıyla üretip kargoya veriyoruz.

Görsellerdeki işletme adları, kişi adları, telefon numaraları ve QR kodlar örnektir; ürününüz kendi bilgilerinizle
hazırlanır.
Ürün kişiye özel üretildiği için cayma hakkı kapsamında değildir (Mesafeli Sözleşmeler Yönetmeliği m. 15)."""

METIN = {
    "masa_9x12": ("QR Kodlu Masa İsimliği 9x12 cm Kişiye Özel İşletme Tabelası Logolu 3D Baskı Sehpalı", """
İŞLETMENİZE ÖZEL QR KODLU MASA İSİMLİĞİ · 9 × 12 cm

Kasanıza, tezgâhınıza ya da masanıza: işletmenizin adı, logosu, telefonu ve büyük bir QR kod. Müşteriniz QR'ı
telefonuyla okutur, işletmenize özel sayfanız açılır: tek dokunuşla arama, WhatsApp, Instagram, konum (yol tarifi),
Google yorum ve IBAN.

ÖZELLİKLER
• Ölçü: 120 × 90 mm, 1 cm kalın gövde
• Yazı ve logo 2 mm kabartma, renkli (3–4 renk)
• QR kod yüzeyle aynı hizada: keskin ve kolay okunur
• 15° eğik sehpa dahil, tutkal gerekmez
• QR'ın açtığı sayfa isimlikle birlikte hazırlanır; bilgileriniz değişirse sayfayı güncelleriz, isimlik aynı kalır

BİZE YAZMANIZ GEREKENLER
İşletme adı, logo (Instagram hesabınızı yazmanız yeterli, logonuzu oradan alırız), telefon, adres, IBAN (isteğe
bağlı), renk tercihi. Görsellerdeki modellerden birini beğendiyseniz görsel numarasını yazın.""",
                  ["Kategori önerisi: Kırtasiye & Ofis > Ofis Malzemeleri > Masa İsimliği (panelde \"isimlik\" diye aratın)",
                   "Kargoya veriliş süresi: en az 5 iş günü (tasarım onayı + üretim)",
                   "Renk özelliği: Çok renkli · Malzeme: Plastik (PLA)"]),
    "kurumsal_10x20": ("Kurumsal Masa İsimliği 10x20 cm Kişiye Özel QR Kartvizitli Ad Soyad Unvan Logolu 3D Baskı", """
KİŞİYE ÖZEL KURUMSAL MASA İSİMLİĞİ · 10 × 20 cm

Yönetici, avukat, doktor, mali müşavir, mimar, danışman ve personel için: ad soyad, unvan, kurum logosu ve dijital
kartvizit QR'ı. Masanıza gelen kişi QR'ı okutur, kartvizitiniz açılır: arama, WhatsApp, e-posta, konum ve tek
dokunuşla rehbere kaydet.

ÖZELLİKLER
• Ölçü: 200 × 100 mm, 5 mm gövde
• Yazılar yüzeyle aynı hizada renkli (baskı silinmez, kazınmaz)
• Kurum logonuz ve renkleriniz
• Sehpa dahil
• Kartvizit sayfası isimlikle birlikte hazırlanır; bilgileriniz değişirse sayfayı güncelleriz

BİZE YAZMANIZ GEREKENLER
Ad soyad, unvan, kurum adı, telefon, e-posta, logo (web sitenizi ya da Instagram hesabınızı yazmanız yeterli),
renk tercihi.""",
                       ["Kategori önerisi: Kırtasiye & Ofis > Ofis Malzemeleri > Masa İsimliği",
                        "Kargoya veriliş süresi: en az 5 iş günü",
                        "Renk özelliği: Çok renkli · Malzeme: Plastik (PLA)"]),
    "bayrakli": ("Türk Bayraklı Masa İsimliği Kişiye Özel Ad Soyad Kabartma Makam İsimliği Sehpalı 3D Baskı", """
TÜRK BAYRAKLI KİŞİYE ÖZEL MASA İSİMLİĞİ · 240 × 56 mm

Solda kabartma ay yıldızlı bayrak, sağda siyah zeminde büyük beyaz harflerle adınız soyadınız ve altında kırmızı
çizgi. Makam masasına, ofise, bankoya; hediye için de güzel bir seçenek.

ÖZELLİKLER
• Blok: 240 × 56 × 32 mm, dolu ve sağlam
• Ay yıldız ve ad soyad 2 mm kabartma
• 3 renk: bayrak kırmızısı, siyah, beyaz
• Siyah sehpa dahil (200 mm): blok 12° arkaya eğik durur
• Ad soyad tek satırda, büyük harf; uzun adlarda yazı sığacak kadar küçülür

BİZE YAZMANIZ GEREKENLER
İsimlikte yazacak ad soyad. Görsellerdeki "AD SOYAD" örnektir.""",
                 ["Kategori önerisi: Kırtasiye & Ofis > Ofis Malzemeleri > Masa İsimliği",
                  "Kargoya veriliş süresi: 3–5 iş günü",
                  "Renk özelliği: Kırmızı / Siyah · Malzeme: Plastik (PLA)"]),
    "guzellik_9x12": ("Kuaför Güzellik Salonu İsimliği 9x12 cm QR Kodlu Çiçek Motifli Kişiye Özel Tabela 3D Baskı", """
KUAFÖR VE GÜZELLİK SALONU İSİMLİĞİ · 9 × 12 cm

Kuaför, güzellik salonu, tırnak, kirpik, cilt bakım, lazer, makyaj ve spa için: salonunuzun renginde, çiçek motifli,
el yazısı adlı QR'lı masa isimliği. Müşteriniz QR'ı okutur, salonunuza özel sayfa açılır: arama, randevu
(WhatsApp, hazır mesajlı), Instagram, konum, Google yorum ve IBAN.

ÖZELLİKLER
• Ölçü: 120 × 90 mm, 1 cm kalın gövde
• Yazı ve çiçek motifleri 2 mm kabartma, 3–4 renk
• Gövde: beyaz, pudra pembe, ten rengi (nude), krem, lila, adaçayı, fuşya ya da siyah
• Motifler: çiçek, papatya, gül, şakayık, nilüfer, kirpik, oje, ruj, fiyonk, gelin tacı
• 15° eğik sehpa dahil

BİZE YAZMANIZ GEREKENLER
Salon adı, logo (Instagram hesabınızı yazmanız yeterli), telefon, adres, IBAN (isteğe bağlı), sevdiğiniz renkler ve
motif. Görsellerdeki modellerden birini beğendiyseniz görsel numarasını yazın.""",
                      ["Kategori önerisi: Kırtasiye & Ofis > Ofis Malzemeleri > Masa İsimliği",
                       "Kargoya veriliş süresi: en az 5 iş günü",
                       "Renk özelliği: Pembe / Çok renkli · Malzeme: Plastik (PLA)"]),
    "guzellik_10x20": ("Güzellik Uzmanı Masa İsimliği 10x20 cm Kişiye Özel El Yazısı İsimli QR Kartvizitli 3D Baskı", """
GÜZELLİK UZMANI İSİMLİĞİ · 10 × 20 cm

Saç tasarımcısı, nail artist, estetisyen, makyaj ve kirpik uzmanı, salon sahibi için: el yazısıyla adınız, unvanınız,
salonunuz ve dijital kartvizit QR'ı. QR'ı okutan müşteriniz kartvizitinizi açar: arama, randevu (WhatsApp),
Instagram, konum, rehbere kaydet.

ÖZELLİKLER
• Ölçü: 200 × 100 mm, 5 mm gövde
• Yazı ve motifler yüzeyle aynı hizada renkli: el yazısı adlar ince ayrıntısıyla
• Pembe, nude, lila, krem tonları; çiçek, oje, kirpik, ruj motifleri
• Salonunuzun isimliğiyle aynı renk ve motiflerle yapılabilir
• Sehpa dahil

BİZE YAZMANIZ GEREKENLER
Ad soyad, unvan, salon adı, telefon, Instagram, sevdiğiniz renkler.""",
                       ["Kategori önerisi: Kırtasiye & Ofis > Ofis Malzemeleri > Masa İsimliği",
                        "Kargoya veriliş süresi: en az 5 iş günü",
                        "Renk özelliği: Pembe / Çok renkli · Malzeme: Plastik (PLA)"]),
    "plakali_anahtarlik": ("Kişiye Özel Plakalı Anahtarlık Türk Plakası Ad Soyad Yazılı Zincirli Halkalı 3D Baskı", """
KİŞİYE ÖZEL PLAKALI ANAHTARLIK · 70 × 22 mm

Kendi plakanız, altında adınız ya da kısa bir sözünüz. Türk plakası görünümünde: kırmızı ya da mavi TR bandı, beyaz
plaka zemini, siyah çerçeve. Plaka ve yazı kabartma; elle hissedilir. Araba anahtarınıza, kendinize ya da hediye
olarak.

ÖZELLİKLER
• Ölçü: 70 × 22 × 3 mm, sağlam PLA gövde
• Plaka yazısı 1,3 mm, ad soyad ya da söz 1 mm kabartma
• TR bandı: kırmızı ya da mavi (seçenekten seçin)
• Arka yüz düz siyah
• Çelik halka, kısa zincir ve ara halka takılı gelir

BİZE YAZMANIZ GEREKENLER
Plaka (ör. 34 ABC 123) ve altına yazılacak ad soyad ya da kısa söz. Türkçe karakterler (İ, Ş, Ğ...) kullanılabilir.""",
                           ["Kategori önerisi: Aksesuar > Anahtarlık (panelde \"anahtarlık\" diye aratın)",
                            "Varyant: Renk = Kırmızı / Mavi (TR bandı)",
                            "Kargoya veriliş süresi: 3–5 iş günü",
                            "Malzeme: Plastik (PLA)"]),
    "yilbasi_seti": ("Yılbaşı Anahtarlık Seti 6'lı Noel Baba Ren Geyiği Kardan Adam 3D Figür Zincirli Halkalı Hediyelik", """
YILBAŞI ANAHTARLIK SETİ (6'LI) · TAM 3D FİGÜR

Noel Baba, ren geyiği, atkılı ayıcık, kutup ayısı, kardan adam ve çam ağacı bir arada! Altı sevimli yılbaşı
figürü, her biri zincirli halka takımıyla.

Ürün set olarak satılır: 1 adet = 6 figürün hepsi (figürler tek tek satılmaz).

SETTE NELER VAR?
• 6 adet 3D baskı figür anahtarlık: Noel Baba, ren geyiği, atkılı ayıcık, kutup ayısı, kardan adam, çam ağacı
• 6 adet zincirli halka takımı (çelik halka, kısa zincir, ara halka); figürlere takılı gelir

ÖZELLİKLER
• Tam 3D: önü de arkası da yuvarlak, her yönden sevimli
• Çok renkli 3D baskı: boya yok, renkler filamentin kendisi
• Boyut: her figür yaklaşık 4–5 cm boy, 2,3 cm kalınlık
• Malzeme: PLA; hafif ve sağlam
• Anahtarlık, çanta süsü ya da yılbaşı ağacı süsü olarak kullanılabilir

Yılbaşı hediyesi, sevdiklerinize küçük bir sürpriz ya da ofiste çekilişlik hediye için ideal.
Kendi atölyemizde tasarlayıp basıyoruz. 3D baskı ürünü olduğu için yüzeyde ince katman izleri görülebilir; bu,
3D baskının doğal dokusudur.""",
                     ["Kategori önerisi: Aksesuar > Anahtarlık ya da Hediyelik Eşya > Yılbaşı Hediyeleri",
                      "Adet: 1 adet = 6'lı set (stok setten girilir)",
                      "Kargoya veriliş süresi: 2–3 iş günü (stoktaysa 1 gün)",
                      "Malzeme: Plastik (PLA)"]),
}


def metin_yaz(name, out):
    baslik, aciklama, notlar = METIN[name]
    gorseller = sorted(f for f in os.listdir(out) if f.endswith(".jpg"))
    with open(os.path.join(out, "ilan.txt"), "w", encoding="utf-8") as f:
        f.write(f"ÜRÜN ADI ({len(baslik)} karakter)\\n{baslik}\\n\\nAÇIKLAMA\\n{aciklama.strip()}\\n{ORTAK_SON}\\n\\n"
                "PANEL NOTLARI (ilana yazılmaz)\\n" + "\\n".join(f"• {n}" for n in notlar) +
                "\\n• Görseller sırayla yüklenir: " + ", ".join(gorseller) +
                "\\n• Son görseller (QR sayfası, ölçü ve sipariş) yazı içerir; Trendyol reddederse çıkarın, ilk görseller "
                "yazısızdır.\\n")


def ekran(klasor, n):
    """Örnek sitenin telefondaki ilk ekranı; telefon ve Instagram yer tutucu (BOYDE'nin numarası değil)."""
    import boyde_site_gorsel as SG
    import sablon_site as SS
    tmp = tempfile.mkdtemp()
    try:
        SS.build(klasor, n, out=tmp, previews=False, gif=False, overrides=dict(SAHTE), record=False)
        im = SG.capture(os.path.join(tmp, "site"))[0]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    path = os.path.join(TY, "_ekran", f"{os.path.basename(klasor)}.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, optimize=True)
    return path, SG.bg_of(path)


def telefon(src, w, bg):
    h = round(w * 844 / 390)
    sb = round(w * 0.1)
    return f"""<div style="width:{w + 24}px;height:{h + 24}px;padding:12px;border-radius:{w * .14:.0f}px;
      background:#0b0b0d;box-shadow:0 40px 80px rgba(18,19,22,.28),inset 0 0 0 2px #2a2b30">
      <div style="width:{w}px;height:{h}px;border-radius:{w * .11:.0f}px;overflow:hidden;background:{bg}">
        <div style="height:{sb}px;position:relative"><span style="position:absolute;left:50%;top:{sb * .3:.0f}px;
          transform:translateX(-50%);width:{w * .3:.0f}px;height:{sb * .5:.0f}px;border-radius:12px;
          background:#0b0b0d"></span></div>
        <img src="{src}" style="width:{w}px;display:block"></div></div>"""


def kicker(t):
    return f'<p style="font-size:24px;font-weight:700;letter-spacing:.18em;color:{ORANGE}">{t}</p>'


def qr_sayfa(P, name, cfg, path, ekr):
    yol, zemin = ekr
    foto = K.uri(os.path.join(FOTO, name, f"{cfg['site_foto']}.jpg"), 900)     # sitedeki işletmenin isimliği
    cips = "".join(f'<span style="padding:12px 20px;border-radius:99px;background:#fff;color:{INK};font-size:24px;'
                   f'font-weight:600;box-shadow:inset 0 0 0 2px rgba(18,19,22,.1)">{c}</span>' for c in cfg["cips"])
    P.png(f"""<div style="position:relative;width:{W}px;height:{H}px;background:#f4f3ef;color:{INK};overflow:hidden">
      <div style="position:absolute;left:80px;right:80px;top:90px">
        {kicker("QR'I OKUTUN")}
        <h1 class="u" style="margin-top:18px;font-size:64px;line-height:1.08;font-weight:700;letter-spacing:-.02em">
          {cfg['qr_baslik']}</h1></div>
      <div style="position:absolute;left:60px;top:470px;width:560px;height:840px;border-radius:36px;overflow:hidden;
        box-shadow:0 30px 60px rgba(18,19,22,.14)"><img src="{foto}" style="width:100%;height:100%;object-fit:cover;
        object-position:50% 50%;transform:scale(1.3)"></div>
      <svg viewBox="0 0 120 60" style="position:absolute;left:560px;top:820px;width:150px;fill:none;stroke:{ORANGE};
        stroke-width:5;stroke-linecap:round;stroke-linejoin:round"><path d="M8 30 H104 M86 12 L106 30 L86 48"/></svg>
      <div style="position:absolute;right:70px;top:430px">{telefon(K.uri(yol, 780, 'PNG'), 420, zemin)}</div>
      <div style="position:absolute;left:80px;right:80px;bottom:110px;display:flex;flex-wrap:wrap;gap:12px">{cips}</div>
      <p style="position:absolute;left:80px;right:80px;bottom:56px;font-size:20px;color:{GRAY}">Görsellerdeki işletme
        adları, telefon ve QR'lar örnektir; sizinki kendi bilgilerinizle hazırlanır.</p></div>""", W, H, path,
          css=K.CSS)


def olcu_siparis(P, name, cfg, path):
    duz_yol = cfg.get("duz_yol") or os.path.join(KAYNAK, f"{cfg['duz']}_duz.png")
    duz = K.uri(duz_yol, 1400, "PNG")
    from PIL import Image
    w0, h0 = Image.open(duz_yol).size
    gw = 640 if w0 / h0 < 1.6 else 820 if w0 / h0 < 3 else 960     # 9 × 12 daha dar: alttaki yazılara yer kalsın
    gh = gw * h0 / w0
    ozellik = "".join(f'<li style="display:flex;gap:14px"><b style="color:{ORANGE}">—</b><span>{o}</span></li>'
                      for o in cfg["ozellik"])
    adim = cfg.get("adim") or [
        ("Siparişinizi verin", ""),
        ("Bilgilerinizi yazın", f"Sipariş detayındaki <b>“Satıcıya Sor”</b>dan: {cfg['bilgi']}."),
        ("Onaylayın", "Tasarımınızı hazırlayıp onayınıza sunuyoruz."),
        ("Üretip gönderiyoruz", "Kendi atölyemizde 3D baskıyla üretip kargoya veriyoruz.")]
    adim_html = "".join(f"""<div style="display:grid;grid-template-columns:76px 1fr;gap:18px;padding:20px 0;
      border-top:2px solid rgba(18,19,22,.08)"><p class="u" style="font-size:44px;font-weight:700;color:{ORANGE};
      line-height:1">{i}</p><div><p style="font-size:30px;font-weight:700">{a}</p>{f'<p style="margin-top:6px;font-size:24px;line-height:1.4;color:#55575c">{b}</p>' if b else ''}
      </div></div>""" for i, (a, b) in enumerate(adim, 1))
    P.png(f"""<div style="width:{W}px;height:{H}px;background:#fff;color:{INK};overflow:hidden;padding:80px;
      display:flex;flex-direction:column">
      {kicker("ÖLÇÜLER")}
      <h1 class="u" style="margin-top:14px;font-size:52px;line-height:1.08;font-weight:700">{cfg['ad']}</h1>
      <div style="position:relative;margin:56px auto 0;width:{gw}px">
        <img src="{duz}" style="width:{gw}px;height:{gh:.0f}px;display:block;filter:drop-shadow(0 10px 18px rgba(0,0,0,.18))">
        <div style="margin-top:24px;height:2px;background:{INK};position:relative">
          <span style="position:absolute;left:50%;top:-20px;transform:translateX(-50%);background:#fff;padding:0 14px;
            font-size:28px;font-weight:700">{cfg['olcu'][0]}</span></div>
        <div style="position:absolute;right:-56px;top:0;width:2px;height:{gh:.0f}px;background:{INK}">
          <span style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%) rotate(-90deg);
            background:#fff;padding:0 12px;font-size:28px;font-weight:700;white-space:nowrap">{cfg['olcu'][1]}</span>
          </div></div>
      <ul style="margin-top:56px;list-style:none;display:grid;gap:10px;font-size:28px;line-height:1.35">{ozellik}</ul>
      <div style="margin-top:auto">{kicker("NASIL SİPARİŞ VERİLİR")}<div style="margin-top:14px">{adim_html}</div></div>
      </div>""", W, H, path, css=K.CSS)


def kolaj(path):
    """Yılbaşı: altı figür yakın, 2 × 3 (yazısız); asılı fotoğraflardan figür kırpılır (yilbasi_shopier.kirp)."""
    import base64
    import io
    from PIL import Image
    import yilbasi_model as YM
    import yilbasi_shopier as YS
    im = Image.new("RGB", (W, H), (255, 255, 255))
    g = 14
    cw, ch = (W - g) // 2, (H - 2 * g) // 3
    for i, k in enumerate(YM.KEYS):
        kare = Image.open(io.BytesIO(base64.b64decode(YS.kirp(k).split(",", 1)[1])))
        s = max(cw, ch) / min(kare.size)
        kare = kare.resize((int(kare.width * s), int(kare.height * s)))
        x0, y0 = (kare.width - cw) // 2, (kare.height - ch) // 2
        im.paste(kare.crop((x0, y0, x0 + cw, y0 + ch)), ((i % 2) * (cw + g), (i // 2) * (ch + g)))
    im.save(path, quality=93)


def set_bilgi(P, path):
    """Yılbaşı: sette neler var (altı figürün önden görünüşü, gerçek oranlarıyla, adları ve boyları) ve özellikler."""
    import yilbasi_model as YM
    import yilbasi_shopier as YS
    tmp = tempfile.mkdtemp()
    px = 7.4
    hucre = ""
    for k in YM.KEYS:
        w, d, h = YS.olcu(k)
        f = os.path.join(tmp, f"{k}.png")
        YS.on_gorunus(k, f)
        hucre += f"""<div style="display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:14px">
          <img src="{K.uri(f, 600, 'PNG')}" style="width:{w * px:.0f}px;height:{h * px:.0f}px;display:block;
            filter:drop-shadow(0 8px 12px rgba(0,0,0,.16))">
          <p style="font-size:24px;font-weight:700;text-align:center">{YM.AD[k]}<br>
            <span style="font-weight:500;color:#55575c">{h:.0f} × {w:.0f} mm</span></p></div>"""
    oz = ["Set olarak satılır: 6 figür + 6 zincirli halka takımı", "Tam 3D: önü de arkası da yuvarlak",
          "Çok renkli 3D baskı; boya yok, renkler filamentin kendisi", "Her figür yaklaşık 4–5 cm, kalınlık ~23 mm",
          "Halkalar figürlere takılı gelir"]
    ozl = "".join(f'<li style="display:flex;gap:14px"><b style="color:{ORANGE}">—</b><span>{o}</span></li>' for o in oz)
    P.png(f"""<div style="width:{W}px;height:{H}px;background:#fff;color:{INK};padding:80px;display:flex;
      flex-direction:column">
      {kicker("SETTE NELER VAR")}
      <h1 class="u" style="margin-top:14px;font-size:52px;line-height:1.08;font-weight:700">6 figür,<br>6 halka takımı.</h1>
      <div style="margin-top:60px;display:grid;grid-template-columns:repeat(3,1fr);row-gap:50px;align-items:end">{hucre}</div>
      <ul style="margin-top:auto;list-style:none;display:grid;gap:12px;font-size:28px;line-height:1.35">{ozl}</ul>
      </div>""", W, H, path, css=K.CSS)
    shutil.rmtree(tmp, ignore_errors=True)


def ilan(P, name, ekr):
    cfg = ILAN[name]
    out = os.path.join(TY, name)
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    if cfg.get("fotolar"):                                  # sıralı liste: (foto alt klasörü, ad)
        for i, (kl, f) in enumerate(cfg["fotolar"], 1):
            hedef = os.path.join(out, f"{i:02d}_{f}.jpg")
            if kl == "_kolaj":
                kolaj(hedef)
            else:
                shutil.copy(os.path.join(FOTO, kl, f"{f}.jpg"), hedef)
        k = len(cfg["fotolar"])
    else:
        fotos = sorted(f for f in os.listdir(os.path.join(FOTO, name)) if f.endswith(".jpg"))
        for i, f in enumerate(fotos, 1):
            shutil.copy(os.path.join(FOTO, name, f), os.path.join(out, f"{i:02d}_{f[2:]}"))
        k = len(fotos)
    if cfg["site"]:
        k += 1
        qr_sayfa(P, name, cfg, os.path.join(out, f"{k:02d}_qr_sayfa.png"), ekr)
    k += 1
    if cfg.get("set"):
        set_bilgi(P, os.path.join(out, f"{k:02d}_sette_neler_var.png"))
    else:
        olcu_siparis(P, name, cfg, os.path.join(out, f"{k:02d}_olcu_siparis.png"))
    from PIL import Image
    for f in os.listdir(out):
        if f.endswith(".png"):
            Image.open(os.path.join(out, f)).convert("RGB").save(os.path.join(out, f[:-4] + ".jpg"), quality=92)
            os.remove(os.path.join(out, f))
    metin_yaz(name, out)
    return out


def main(args):
    names = [a for a in args if a in ILAN] or list(ILAN)
    # site ekranları önce (Playwright'ı kendileri açar; ressam açıkken iç içe açılamaz)
    ekr = {n: ekran(os.path.join(ILAN[n]["site"][0], ILAN[n]["site"][1]), ILAN[n]["site"][2])
           for n in names if ILAN[n]["site"]}
    with BM.painter() as P:
        for n in names:
            print(os.path.relpath(ilan(P, n, ekr.get(n)), ROOT), sorted(os.listdir(os.path.join(TY, n))), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
