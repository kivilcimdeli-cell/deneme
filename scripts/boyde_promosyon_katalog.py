"""BOYDE LABS – promosyon kataloğu (A4 PDF): nail art ve güzellik stüdyolarının müşterilerine hediye ürünler.

Sayfalar: kapak, nasıl çalışır (beş ürün, dört adım), her ürün türü bir sayfa (masada dört çeşit, çeşitler halkada,
özellikler), renkler ve kişiselleştirme, NFC fırça ve randevu sayfası (güzellik şablonları telefonda), sipariş.
Görsel dil BOYDE'nin öbür kataloglarıyla aynı (scripts/boyde_katalog.py: logo, renk paleti, yazı tipleri).

Girdi : boyde_labs/promosyon/fotograf (scripts/boyde_promosyon.py --foto), boyde_labs/guzellik/siteler/*/ekran_ust.png
Çıktı : boyde_labs/promosyon/katalog.pdf, katalog.png (sayfaların önizlemesi)
Kullanım: python3 scripts/boyde_promosyon.py --katalog
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_promosyon as PR  # noqa: E402
import boyde_katalog as K  # noqa: E402
import boyde_marka as BM  # noqa: E402

INK, PAPER, ORANGE, SAND = K.INK, K.PAPER, K.ORANGE, K.SAND
W, H = 794, 1123
GUZ = os.path.join(PR.A.ROOT, "boyde_labs", "guzellik")
NOT_ORNEK = ("Örneklerdeki salon adları uydurmadır; ürün sizin adınız, baş harfiniz, logonuz ve renklerinizle "
             "hazırlanır.")

TUR = {
    "fiyonk": {
        "ad": "Fiyonk çanta süsü", "kisa": "Çantaya, anahtara takılan kabarık fiyonk; düğümde baş harfiniz.",
        "metin": "Çantaya, anahtarlığa, fermuara takılan, kabarık kenarlı fiyonk. Düğümünde salonunuzun baş harfi, "
                 "arkasında adınız. Müşteriniz her gün yanında taşır, her baktığında sizi hatırlar.",
        "ozellik": ["59 × 48 mm, 7 mm kalınlık; yumuşak, kabarık kenarlar ve kurdele kıvrımları",
                    "Düğüm ayrı renkte, üstünde kabartma baş harf (kalp düğüm de olur)",
                    "Arka yüzde gömme salon adınız",
                    "Halka ve zincirle; çanta için karabina da takılabilir",
                    "İnci, çift ilmek gibi dokunuşlar; mat ve ipek (rose gold) renkler"],
        "renk": {"f1": "pudra pembe · rose gold düğüm", "f2": "fuşya · beyaz kalp düğüm", "f3": "lila · beyaz inciler",
                 "f4": "beyaz · pudra düğüm · rose gold ilmek"}},
    "oje": {
        "ad": "Oje şişesi kutu açacağı", "kisa": "Kapağındaki ince uçla kutu açar: yeni tırnaklar kırılmaz.",
        "metin": "Oje şişesi biçiminde anahtarlık. Kapağındaki oval delik hem halka deliği hem kutu açacağı: ince "
                 "ucunu içecek kutusunun dilinin altına sokup kaldırın. Yeni yapılmış tırnaklar kırılmaz; müşteriniz "
                 "her kutu açışında salonunuzu hatırlar.",
        "ozellik": ["34 × 70 mm (uzun şişe 26 × 84 mm), 4,8 mm kalınlık",
                    "Açacak ucu 1,2 mm'ye incelir: kutunun dilinin altına girer",
                    "Şişede kabartma salon adı ya da kalpli baş harf; ışık çizgisi",
                    "Kapak ayrı renkte ve oluklu; arka yüzde Instagram adınız",
                    "Dört şişe biçimi: klasik, damla, kare, uzun"],
        "renk": {"o1": "pudra pembe · rose gold kapak", "o2": "fuşya · beyaz kapak ve kalp",
                 "o3": "lila · mürdüm kapak", "o4": "ten rengi · moka kapak"}},
    "acacak": {
        "ad": "Fiyonk kutu açacağı", "kisa": "Düz, iki renkli fiyonk; üstündeki oval delikle kutu açar.",
        "metin": "Düz, iki ya da üç renkli fiyonk anahtarlık. Çerçevesi ve düğümü bir renk, içi başka renk; düğümde "
                 "kalp ya da baş harf. Üstündeki oval delikle kutu açar, tırnakları korur; arkasında salonunuzun adı.",
        "ozellik": ["58 × 40 mm, 4,6 mm kalınlık",
                    "Çerçeve, iç dolgu ve düğüm ayrı renklerde",
                    "Puantiye, dikiş izi, kalp düğüm gibi desenler",
                    "Arka yüzde iki ilmeğe bölünmüş salon adı",
                    "Açacak ucu 1,2 mm; halka aynı delikten geçer"],
        "renk": {"b1": "pudra pembe · fuşya çerçeve · beyaz kalp", "b2": "beyaz · fuşya puantiye",
                 "b3": "lila · mürdüm · beyaz dikiş", "b4": "ten rengi · rose gold çerçeve"}},
    "firca": {
        "ad": "Makyaj fırçası NFC anahtarlık", "kisa": "Telefona dokununca randevu sayfanızı açar.",
        "metin": "Fırça biçiminde anahtarlık; başının içinde NFC etiketi var. Müşteriniz telefonunu dokundurur, "
                 "salonunuzun randevu sayfası açılır: tek dokunuşla arar, WhatsApp'tan randevu ister, Instagram'ınıza "
                 "ve konumunuza ulaşır. Uygulama gerekmez.",
        "ozellik": ["34–53 × 80–88 mm, 6 mm kalınlık",
                    "Fırça başında Ø 25 mm NFC etiketi, baskının içine gömülü (görünmez, düşmez)",
                    "NFC'li akıllı telefonların çoğunda çalışır (iPhone XS ve sonrası, NFC'li Android)",
                    "Kıl uçları ayrı renkte, bilezik rose gold ya da beyaz; sapta salon adı ve kalp",
                    "Dört fırça: kabuki, yelpaze, pudra, eğik kontür"],
        "renk": {"n1": "pudra pembe · fuşya uç · rose gold bilezik", "n2": "lila · mürdüm uç ve sap",
                 "n3": "ten rengi · moka uç · rose gold bilezik", "n4": "fuşya · pudra uç ve sap"}},
    "ruj": {
        "ad": "Ruj kutusu anahtarlık", "kisa": "İçine ruj giren, kapaklı kutu; çantaya takılır.",
        "metin": "Rujunuz çantada kaybolmasın: içine standart bir ruj giren, sürtmeli kapaklı kutu. Kapağındaki kulakla "
                 "anahtarlığa, çantaya takılır; gövdesinde salonunuzun adı. Kalp pencereli olanda ruj görünür.",
        "ozellik": ["Ø 28 × 92 mm (kapak ve kulakla); altıgende köşeden köşeye 31 mm",
                    "İç Ø 22,6 mm: Ø 22 mm'ye, 78 mm boya kadar rujlar girer",
                    "İki parça: gövde ve sürtmeli kapak (iki ayrı renk)",
                    "Gövdede kabartma salon adı; kalp pencere, oluklar, kapakta fiyonk",
                    "Halka, zincir ya da püskülle"],
        "renk": {"r1": "pudra pembe · rose gold kapak", "r2": "fuşya · beyaz kapak · kalp pencere",
                 "r3": "lila · mürdüm kapak · oluklu", "r4": "ten rengi · moka kapak · pudra fiyonk"}},
}
KODLAR = {k: f"P{i:02d}" for i, k in enumerate(PR.URUNLER, 1)}
SIPARIS = [("01", "Ürünü ve çeşidi seçin", "Bu katalogdan kodu yazın (ör. P06); karışık paket de olur."),
           ("02", "Bilgilerinizi gönderin", "Salon adı, baş harf, logo, renkler; NFC için sayfanızın bilgileri."),
           ("03", "Tasarımı onaylayın", "Size özel çizimi ve renkleri görün; değişiklik isteyin."),
           ("04", "Basıp gönderiyoruz", "Kendi atölyemizde 3D baskı; halkası takılı, kargoyla.")]
FILAMENT = [("pudra pembe", "PLA Matte Sakura Pink"), ("fuşya", "PLA Basic Hot Pink"),
            ("gül kurusu", "dusty rose"), ("lila", "PLA Matte Lilac Purple"), ("mürdüm", "PLA Matte Plum"),
            ("ten rengi", "PLA Matte Latte Brown"), ("krem", "PLA Matte Ivory White"),
            ("moka", "PLA Matte Dark Chocolate"), ("rose gold", "PLA Silk Rose Gold (ipek)"),
            ("adaçayı", "yumuşak yeşil"), ("beyaz", "PLA Basic White"), ("siyah", "PLA Basic Black")]
RGB = {PR.S.NAMES[k]: PR.RGB[k] for k in PR.RGB if k in PR.S.NAMES}


def foto(ad, maxw=900, crop=None):
    return K.uri(os.path.join(PR.FOTO, ad), maxw, crop=crop)


def sayfa(body, dark=False, no=None):
    bg = f"background:{INK};color:{PAPER}" if dark else f"background:{PAPER};color:{INK}"
    foot = (f'<p style="position:absolute;left:48px;right:48px;bottom:26px;display:flex;justify-content:space-between;'
            f'font-size:10px;letter-spacing:.2em;color:{K.GRAY}"><span>BOYDE LABS · PROMOSYON KOLEKSİYONU</span>'
            f'<span>{no:02d}</span></p>') if no else ""
    return f'<div class="pg" style="{bg};padding:48px">{body}{foot}</div>'


def kesit(path, oran=1.0):
    """Fotoğrafın ortasından `oran` (en / boy) kırpma kutusu: parçalar kadrajın ortasında."""
    from PIL import Image
    im = Image.open(path)
    w, h = im.size
    if w / h > oran:
        nw = round(h * oran)
        return ((w - nw) // 2, 0, (w - nw) // 2 + nw, h)
    nh = round(w / oran)
    return (0, (h - nh) // 2, w, (h - nh) // 2 + nh)


def cesit_karti(k, tur, dark):
    _, ad, _ = PR.URUNLER[k]
    p = os.path.join(PR.FOTO, f"{k}_{'iki' if tur == 'ruj' else 'halka'}.jpg")     # uzun kutular asılıyken küçük
    alt = "rgba(244,241,234,.65)" if dark else "#55575c"
    kutu = "rgba(244,241,234,.06)" if dark else "#fff"
    return f"""<div style="background:{kutu};border-radius:14px;overflow:hidden">
      <img src="{K.uri(p, 420, crop=kesit(p, 1.0))}" style="width:100%;aspect-ratio:1;object-fit:cover;display:block">
      <div style="padding:9px 11px 11px"><b class="code" style="font-size:12px;color:{ORANGE}">{KODLAR[k]}</b>
        <p style="margin-top:4px;font-size:12.5px;font-weight:700;line-height:1.25">{ad}</p>
        <p style="margin-top:3px;font-size:10.5px;line-height:1.35;color:{alt}">{TUR[tur]['renk'][k]}</p></div></div>"""


def tur_sayfasi(i, tur, no, dark):
    t = TUR[tur]
    ks = [k for k, v in PR.URUNLER.items() if v[0] == tur]
    alt = "rgba(244,241,234,.78)" if dark else "#3b3d42"
    cizgi = "rgba(244,241,234,.14)" if dark else "#ddd6ca"
    feats = "".join(f'<li style="padding:6px 0;border-top:1px solid {cizgi}">{f}</li>' for f in t["ozellik"])
    grup = os.path.join(PR.FOTO, f"grup_{tur}.jpg")
    kartlar = "".join(cesit_karti(k, tur, dark) for k in ks)
    return sayfa(f"""<div style="display:flex;justify-content:space-between;align-items:flex-end">
      <div><p class="k">{i:02d} · {t['ad'].upper()}</p>
      <h2 class="u" style="margin-top:8px;font-size:30px;line-height:1.1">{t['ad']}</h2></div>
      <b class="code" style="font-size:15px;color:{ORANGE}">{KODLAR[ks[0]]}–{KODLAR[ks[-1]]}</b></div>
      <p style="margin-top:10px;font-size:13px;line-height:1.55;color:{alt}">{t['metin']}</p>
      <img src="{K.uri(grup, 1100, crop=kesit(grup, 698 / 330))}" style="margin-top:16px;width:100%;height:330px;
        object-fit:cover;border-radius:16px;display:block">
      <div style="margin-top:14px;display:grid;grid-template-columns:repeat(4,1fr);gap:10px">{kartlar}</div>
      <ul style="margin-top:14px;list-style:none;font-size:12.5px;line-height:1.4">{feats}</ul>""", dark=dark, no=no)


def katalog(P):
    from PIL import Image
    import sablonlar
    import boyde_site_gorsel as SG
    pages, no = [], 1
    kp = os.path.join(PR.FOTO, "kapak.jpg")
    pages.append(sayfa(f"""<div style="position:absolute;inset:0;background:url({K.uri(kp, 1200)}) center/cover"></div>
      <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(18,19,22,.78) 0,rgba(18,19,22,0) 26%,
        rgba(18,19,22,0) 48%,rgba(18,19,22,.97) 100%)"></div>
      <div style="position:relative">{K.logo("koyu", 260, 52)}</div>
      <div style="position:absolute;left:48px;right:48px;bottom:64px">
        <p class="k">ÜRÜN KATALOĞU · PROMOSYON KOLEKSİYONU</p>
        <h1 class="u" style="margin-top:12px;font-size:46px;line-height:1.05">Nail art ve güzellik<br>stüdyolarına
          promosyon</h1>
        <p style="margin-top:16px;font-size:16px;line-height:1.5;opacity:.86">Müşterinize hediye edin, sizi her gün
          hatırlasın: fiyonk çanta süsü, oje ve fiyonk kutu açacağı, NFC'li makyaj fırçası, ruj kutusu. Salonunuzun
          adı ve renkleriyle, kendi atölyemizde 3D baskı.</p></div>""", dark=True))
    no += 1

    turler = "".join(f"""<div style="background:#fff;border-radius:14px;overflow:hidden">
      <img src="{K.uri(os.path.join(PR.FOTO, f'dizi_{tur}.jpg'), 520, crop=kesit(os.path.join(PR.FOTO,
        f'dizi_{tur}.jpg'), 1.3))}" style="width:100%;aspect-ratio:1.3;object-fit:cover;display:block">
      <div style="padding:10px 12px 12px"><p class="k" style="font-size:10px">{i:02d}</p>
        <p class="u" style="margin-top:4px;font-size:14px;line-height:1.2">{TUR[tur]['ad']}</p>
        <p style="margin-top:4px;font-size:11px;line-height:1.4;color:#55575c">{TUR[tur]['kisa']}</p></div></div>"""
                     for i, tur in enumerate(PR.TURLER, 1))
    turler += f"""<div style="border-radius:14px;background:{ORANGE};color:#fff;padding:16px;display:flex;
      flex-direction:column;justify-content:flex-end"><p class="u" style="font-size:17px;line-height:1.2">20 çeşit,
      sınırsız renk</p><p style="margin-top:6px;font-size:11.5px;line-height:1.45">Her ürün sizin adınız, baş
      harfiniz ve renklerinizle; karışık paket de hazırlıyoruz.</p></div>"""
    steps = "".join(f"""<div style="display:flex;gap:14px;padding:10px 0;border-top:1px solid #ddd6ca">
      <b class="u" style="color:{ORANGE};font-size:18px;width:36px">{a}</b><div><p style="font-weight:700;
      font-size:13.5px">{b}</p><p style="margin-top:2px;font-size:11.5px;color:#55575c">{c}</p></div></div>"""
                    for a, b, c in SIPARIS)
    pages.append(sayfa(f"""<p class="k">NASIL ÇALIŞIR</p>
      <h2 class="u" style="margin-top:10px;font-size:28px;line-height:1.15">Hediyeniz çantada,<br>salonunuz akılda.
      </h2>
      <p style="margin-top:12px;font-size:13px;line-height:1.6;color:#3b3d42;max-width:640px">Randevu sonrası küçük
        bir hediye, müşterinizin her gün elinde: kutu açarken, çantasını alırken, rujunu sürerken. Hepsi salonunuzun
        adı, baş harfi ve renkleriyle; NFC'li fırça telefona dokununca randevu sayfanızı açar.</p>
      <div style="margin-top:18px;display:grid;grid-template-columns:repeat(3,1fr);gap:10px">{turler}</div>
      <div style="margin-top:16px">{steps}</div>
      <p style="margin-top:10px;font-size:10.5px;color:{K.GRAY}">{NOT_ORNEK}</p>""", no=no))
    no += 1

    for i, tur in enumerate(PR.TURLER, 1):
        pages.append(tur_sayfasi(i, tur, no, dark=i % 2 == 0))
        no += 1

    sw = "".join(f"""<div style="display:flex;align-items:center;gap:12px;padding:9px 12px;background:#fff;
      border-radius:12px"><i style="flex:none;width:36px;height:36px;border-radius:10px;background:rgb{RGB.get(ad,
        (200, 200, 200))};box-shadow:inset 0 0 0 1px rgba(18,19,22,.1)"></i><div><p style="font-weight:700;
      font-size:13px">{ad[:1].upper() + ad[1:]}</p><p style="font-size:10.5px;color:#55575c">{fil}</p></div></div>"""
                 for ad, fil in FILAMENT)
    kisi = [("Baş harf", "Düğümde, kalpte ya da şişede kabartma; Marcellus gibi zarif harfler."),
            ("Salon adı", "Ön yüzde kabartma ya da arka yüzde gömme; el yazısı da olur."),
            ("Instagram adı", "Açacakların arka yüzünde: @salonunuz."),
            ("Logo", "Tek renk logonuz düğümde ya da şişede (çizimini biz hazırlarız)."),
            ("NFC sayfası", "Fırçadaki etiket randevu sayfanızı açar; bilgileriniz değişirse güncelleriz.")]
    kl = "".join(f"""<div style="padding:10px 0;border-top:1px solid #ddd6ca"><p style="font-weight:700;
      font-size:13px">{a}</p><p style="margin-top:2px;font-size:11.5px;color:#55575c">{b}</p></div>""" for a, b in kisi)
    p_ = os.path.join(PR.FOTO, "f1_iki.jpg")
    q_ = os.path.join(PR.FOTO, "o2_iki.jpg")
    pages.append(sayfa(f"""<p class="k">RENKLER VE KİŞİSELLEŞTİRME</p>
      <h2 class="u" style="margin-top:10px;font-size:28px;line-height:1.15">Salonunuzun renginde,<br>sizin adınızla.</h2>
      <p style="margin-top:12px;font-size:13px;line-height:1.6;color:#3b3d42;max-width:640px">Gövde, düğüm, kapak ve
        yazı renklerini salonunuza göre seçiyoruz: pudra, fuşya, lila, ten rengi tonları; moka, mürdüm yazılar; rose
        gold ipek dokunuşlar. Bir üründe iki ile dört renk.</p>
      <div style="margin-top:18px;display:grid;grid-template-columns:repeat(3,1fr);gap:8px">{sw}</div>
      <div style="margin-top:18px;display:grid;grid-template-columns:1fr 1fr;gap:18px;align-items:start">
        <div>{kl}</div>
        <div style="display:grid;gap:10px"><img src="{K.uri(p_, 600, crop=kesit(p_, 1.5))}" style="width:100%;
          aspect-ratio:1.5;object-fit:cover;border-radius:14px;display:block"><img src="{K.uri(q_, 600,
          crop=kesit(q_, 1.5))}" style="width:100%;aspect-ratio:1.5;object-fit:cover;border-radius:14px;display:block">
          <p style="font-size:10.5px;color:{K.GRAY}">Ön yüzde baş harf, arka yüzde salon adı ya da Instagram adı.</p>
        </div></div>""", no=no))
    no += 1

    tel = []
    for klasor, n in (("lal", 9), ("defne", 6), ("ela", 8)):
        shot = os.path.join(GUZ, "siteler", klasor, "ekran_ust.png")
        if not os.path.exists(shot):
            continue
        d = json.load(open(os.path.join(GUZ, "siteler", klasor, "bilgiler.json"), encoding="utf-8"))
        tel.append(f"""<div style="display:flex;flex-direction:column;align-items:center;gap:10px">
          {SG.phone(K.uri(shot, 500, "PNG"), 132, SG.bg_of(shot))}
          <p style="font-weight:700;font-size:13px;text-align:center">{d['isletme']}</p>
          <p style="margin-top:-7px;font-size:11px;color:rgba(244,241,234,.65)">Şablon: {sablonlar.get(n).AD}</p>
          </div>""")
    nf = os.path.join(PR.FOTO, "dizi_firca.jpg")
    pages.append(sayfa(f"""<p class="k">NFC FIRÇA · RANDEVU SAYFASI</p>
      <h2 class="u" style="margin-top:10px;font-size:28px;line-height:1.15">Dokununca açılır,<br>randevu tek
        dokunuşta.</h2>
      <p style="margin-top:12px;font-size:13px;line-height:1.6;color:rgba(244,241,234,.78);max-width:640px">Fırçanın
        başındaki NFC etiketine telefon dokundurulunca salonunuzun sayfası açılır: Hemen Ara, WhatsApp'tan Randevu al,
        Instagram, Google yorum, konum, rehbere kaydet. Sayfa güzellik salonları için tasarladığımız beş şablondan
        biri; sizin renginiz ve adınızla. Bilgileriniz değişirse sayfayı güncelleriz, fırça aynı kalır.</p>
      <img src="{K.uri(nf, 1100, crop=kesit(nf, 698 / 300))}" style="margin-top:18px;width:100%;height:300px;
        object-fit:cover;border-radius:16px;display:block">
      <div style="margin-top:24px;display:flex;flex-wrap:wrap;justify-content:center;gap:12px 46px">{''.join(tel)}</div>
      <p style="margin-top:16px;font-size:10.5px;color:{K.GRAY}">Örnek işletmeler; telefon BOYDE LABS'in. NFC'li
        akıllı telefonların çoğunda çalışır; QR'lı isimliklerimizle aynı sayfayı açar.</p>""", dark=True, no=no))
    no += 1

    kolaj = "".join(f'<img src="{foto(f"{k}_iki.jpg", 500, kesit(os.path.join(PR.FOTO, f"{k}_iki.jpg"), 1.0))}" '
                    f'style="width:100%;aspect-ratio:1;object-fit:cover;border-radius:12px;display:block">'
                    for k in ("f3", "b2", "n2", "o3", "r2", "b4"))
    paket = [("Hediye paketi", "Tek ürün, tek renk: randevu sonrası küçük bir teşekkür."),
             ("Karışık paket", "Aynı renk ailesinden birkaç ürün: çanta süsü, açacak, ruj kutusu."),
             ("Ekip ve VIP", "NFC fırça ve ruj kutusu: ekibinize ve sadık müşterilerinize.")]
    pk = "".join(f"""<div style="background:#fff;border-radius:14px;padding:14px"><p class="u" style="font-size:14px">
      {a}</p><p style="margin-top:5px;font-size:11.5px;line-height:1.45;color:#55575c">{b}</p></div>"""
                 for a, b in paket)
    pages.append(sayfa(f"""<p class="k">SİPARİŞ</p>
      <h2 class="u" style="margin-top:10px;font-size:26px">Salonunuza özel promosyon</h2>
      <p style="margin-top:10px;font-size:13px;color:#3b3d42;max-width:640px">Ürün kodlarını, adedi, salon adınızı,
        baş harfinizi, logonuzu ve renklerinizi gönderin; size özel çizimi hazırlayıp onayınıza sunalım. Fiyat adede,
        ürüne ve renk sayısına göre; teklif için yazın.</p>
      <div style="margin-top:16px;display:grid;grid-template-columns:repeat(3,1fr);gap:10px">{kolaj}</div>
      <div style="margin-top:14px;display:grid;grid-template-columns:repeat(3,1fr);gap:10px">{pk}</div>
      <div style="margin-top:20px;background:{INK};color:{PAPER};border-radius:18px;padding:28px 32px;
        background-image:{BM.stripes_bg(PAPER, .035, 22)}">
        <p class="k">SİPARİŞ VE TEKLİF</p>
        <p class="u" style="margin-top:10px;font-size:22px;line-height:1.2">WhatsApp'tan ya da telefonla.</p>
        <p style="margin-top:12px;font-size:28px;font-weight:700">{K.TEL}</p>
        <p style="margin-top:6px;font-size:12.5px;color:rgba(244,241,234,.75)">Kodu yazmanız yeterli (ör. P06 ve
          P14); tasarımı onayınızdan sonra basıyoruz.</p>
        <div style="margin-top:18px">{K.logo("koyu", 220, 44)}</div></div>""", no=no))

    path = os.path.join(PR.OUT, "katalog.pdf")
    shots = P.pdf(pages, W, H, path, css=K.CSS)
    cols, tw, th = 5, 318, 450
    rows = (len(shots) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * 16, rows * th + (rows + 1) * 16), SAND)
    for i, s in enumerate(shots):
        sheet.paste(s.resize((tw, th), Image.LANCZOS), (16 + (i % cols) * (tw + 16), 16 + (i // cols) * (th + 16)))
    sheet.save(os.path.join(PR.OUT, "katalog.png"), optimize=True)
    return path, len(pages)


def main():
    with BM.painter() as P:
        path, n = katalog(P)
    print(f"{os.path.relpath(path, PR.A.ROOT)}: {n} sayfa", flush=True)


if __name__ == "__main__":
    main()
