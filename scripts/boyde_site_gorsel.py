"""BOYDE LABS – örnek site görselleri (Shopier ve katalog): isimlikteki QR'ın açtığı sayfa, beş şablonun beşiyle.

Kullanıcı isteği: "bu görsellere ek olarak 3 adet birbirinden farklı internet sayfası görseli; örnek niyetine,
Shopier'de kullanırız"; sonra "site görsel çeşitlerini artır, hepsini aynı tarz yapmışsın; sitede 5 şablon kaydetmiştik".

Beş uydurma işletme, isimlik örnekleriyle aynı (scripts/boyde_sektor.py), her biri başka şablonla
(scripts/sablon_site.py, lastikçi tarzı beş şablon):
  cagri  Çağrı İletişim (telefoncu)   1 · Şimşek     turkuaz, şimşek yerine telefon simgesi
  anka   Anka Emlak (emlak)           2 · Lastik izi mavi, ev
  luna   Luna Güzellik (güzellik)     3 · İkaz       pembe, hilal
  sera   Sera Kuyumculuk (kuyumcu)    4 · Kurumsal   altın, pırlanta
  mira   Mira Kuaför (kuaför)         5 · Sade       mor, makas çizilerek gelir
Örnek oldukları için şablon sırasına (site_sablonlari/sira.json) yazılmaz. Telefon BOYDE'nin (0546 475 45 08),
IBAN örnek; sayfadaki banka karekodu da okunmaz (boyde_urunler'in örnek modu).

Görseller (1200 × 1200), her biri başka düzende:
  1 açık zemin, iki telefon (ilk ekran, bağlantılar), köşede isimlik
  2 koyu zemin, tek büyük telefon, yanında isimlik
  3 kum rengi zemin, üç telefon yan yana (ilk ekran, bağlantılar, ödeme), alttan taşar
  4 isimlikten siteye: büyük isimlik fotoğrafı, "QR'ı okut" oku, telefon
  5 ikiye bölünmüş: solda koyu zeminde isimlik, sağda üst üste iki telefon
Çıktı : boyde_labs/urunler/shopier/site_ornekleri/0N_<işletme>_<şablon>.jpg
        boyde_labs/urunler/siteler/<işletme>/ (bilgiler.json, logo, ekran görüntüleri: katalog da kullanır)

Kullanım: python3 scripts/boyde_site_gorsel.py
"""
import io
import json
import os
import shutil
import sys
import tempfile

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_sektor as S  # noqa: E402  (örnek modu: QR'lar okunmaz)
import boyde_urunler as U  # noqa: E402
import sablon_site as SS  # noqa: E402

OUT = os.path.join(U.OUT, "siteler")
SHOP = os.path.join(U.OUT, "shopier", "site_ornekleri")
ORTAK = {"telefon": "0546 475 45 08", "whatsapp_mesaj": "Merhaba, bilgi almak istiyorum.",
         "harita": "https://www.google.com/maps/search/?api=1&query=Antalya",
         "iban": "TR12 3456 7890 1234 5678 9012 34", "iban_ornek": True, "banka": "Örnek Bankası"}
ORNEKLER = [
    ("cagri", 1, "telefon", lambda: S.ic_phone(0, 0, 21.0), {
        "isletme": "Çağrı İletişim", "marka": "ÇAĞRI", "hizmet": "İLETİŞİM", "etiket": "TELEFON · AKSESUAR · TAMİR",
        "aciklama": "Telefon, aksesuar ve teknik servis. Tek dokunuşla arayın, yazın.", "renk": "#0096BE",
        "instagram": "@cagriiletisim", "google": "https://www.google.com/search?q=%C3%87a%C4%9Fr%C4%B1+%C4%B0leti%C5%9Fim",
        "iban_alici": "ÇAĞRI İLETİŞİM"}),
    ("anka", 2, "emlak", lambda: S.ic_house(0, 0, 15.0), {
        "isletme": "Anka Emlak", "marka": "ANKA", "hizmet": "EMLAK", "etiket": "SATILIK · KİRALIK · DANIŞMANLIK",
        "aciklama": "Satılık ve kiralık ilanlar için tek dokunuşla arayın, yazın.", "renk": "#2F64D6",
        "instagram": "@ankaemlak", "google": "https://www.google.com/search?q=Anka+Emlak",
        "iban_alici": "ANKA EMLAK"}),
    ("luna", 3, "guzellik", lambda: S.ic_moon(0, 0, 6.4), {
        "isletme": "Luna Güzellik", "marka": "LUNA", "hizmet": "GÜZELLİK", "etiket": "CİLT · KAŞ · MANİKÜR",
        "aciklama": "Randevunuzu tek dokunuşla alın.", "renk": "#E8668F",
        "instagram": "@lunaguzellik", "google": "https://www.google.com/search?q=Luna+G%C3%BCzellik",
        "iban_alici": "LUNA GÜZELLİK"}),
    ("sera", 4, "kuyumcu", lambda: S.ic_diamond(0, 0, 15.0), {
        "isletme": "Sera Kuyumculuk", "marka": "SERA", "hizmet": "KUYUMCULUK", "etiket": "ALTIN · PIRLANTA · SAAT",
        "aciklama": "Altın, pırlanta ve saat. Fiyat ve sipariş için tek dokunuşla yazın.", "renk": "#D4A64E",
        "instagram": "@serakuyumculuk", "google": "https://www.google.com/search?q=Sera+Kuyumculuk",
        "iban_alici": "SERA KUYUMCULUK"}),
    ("mira", 5, "kuafor", lambda: S.ic_scissors(0, 0, 21.0, angle=-28.0), {
        "isletme": "Mira Kuaför", "marka": "MİRA", "hizmet": "KUAFÖR", "etiket": "KESİM · FÖN · BOYA · GELİN SAÇI",
        "aciklama": "Randevunuzu tek dokunuşla alın.", "renk": "#9B7BEA",
        "instagram": "@mirakuafor", "google": "https://www.google.com/search?q=Mira+Kuaf%C3%B6r",
        "iban_alici": "MİRA KUAFÖR"}),
]

KISI = {"telefon": "0546 475 45 08", "whatsapp_mesaj": "Merhaba, bilgi almak istiyorum.",
        "harita": "https://www.google.com/maps/search/?api=1&query=Antalya"}       # kartvizit: IBAN yok
KARTVIZIT = [                                            # 10 × 20 kurumsal isimliklerin kişileri (boyde_sektor)
    ("nova", 1, "mudur", lambda: S.ic_star(0, 0, 6.4), {
        "isletme": "Kerem Aksoy", "hizmet": "GENEL MÜDÜR", "etiket": "NOVA YAZILIM · ANTALYA",
        "kurum": "Nova Yazılım", "eposta": "kerem.aksoy@ornek.com", "renk": "#F07A2A",
        "aciklama": "Bana tek dokunuşla ulaşın: arayın, yazın, rehberinize ekleyin."}),
    ("demir", 2, "musavir", lambda: S.t("mont", "ED", 11.0, 0, 0, "c", 0.4), {
        "isletme": "Elif Demir", "hizmet": "SMMM · MALİ MÜŞAVİR", "etiket": "DEMİR MALİ MÜŞAVİRLİK",
        "kurum": "Demir Mali Müşavirlik", "eposta": "elif.demir@ornek.com", "renk": "#1FA463",
        "aciklama": "Beyanname, defter ve danışmanlık için tek dokunuşla ulaşın."}),
    ("arslan", 3, "dis", lambda: S.ic_tooth(0, 0, 24.0), {
        "isletme": "Zeynep Arslan", "hizmet": "DİŞ HEKİMİ", "etiket": "ARSLAN DİŞ KLİNİĞİ",
        "kurum": "Arslan Diş Kliniği", "eposta": "zeynep.arslan@ornek.com", "renk": "#0FA3B1",
        "aciklama": "Randevu ve sorularınız için tek dokunuşla ulaşın.",
        "whatsapp_mesaj": "Merhaba, randevu almak istiyorum."}),
    ("kaya", 4, "avukat", lambda: S.ic_scales(0, 0, 30.0), {
        "isletme": "Mehmet Kaya", "hizmet": "AVUKAT · ARABULUCU", "etiket": "KAYA HUKUK BÜROSU",
        "kurum": "Kaya Hukuk Bürosu", "eposta": "mehmet.kaya@ornek.com", "renk": "#C9A45C",
        "aciklama": "Hukuki danışmanlık ve randevu için tek dokunuşla ulaşın."}),
    ("koc", 5, "psikolog", lambda: S.ic_bubble(0, 0, 16.0), {
        "isletme": "Selin Koç", "hizmet": "UZMAN KLİNİK PSİKOLOG", "etiket": "KOÇ PSİKOLOJİK DANIŞMANLIK",
        "kurum": "Koç Psikolojik Danışmanlık", "eposta": "selin.koc@ornek.com", "renk": "#8B6CE0",
        "aciklama": "Randevunuzu tek dokunuşla alın.", "whatsapp_mesaj": "Merhaba, randevu almak istiyorum."}),
]
SETS = {                                                 # kategori: örnekler ve görsellerdeki yazılar
    "9x12": {"ornekler": ORNEKLER, "ortak": ORTAK, "out": SHOP, "etiket": "ÖRNEK SİTE",
             "chips": ("Ara", "WhatsApp", "Instagram", "Konum", "Google yorum", "IBAN", "Rehbere kaydet"),
             "lede": "İsimlikteki QR'ı okutan müşteri bu sayfayı açar. Her şey tek dokunuşla:",
             "ozet": "QR'ı okutan müşteri bu sayfayı açar: ara, WhatsApp, Instagram, konum, yorum, IBAN.",
             "not": "Örnek işletme; telefon BOYDE LABS'in, IBAN ve QR örnektir.",
             "ekranlar": ("ust", "orta", "alt"), "ikinci": "orta", "son": "alt",
             "uclu": (("ust", "İlk ekran"), ("orta", "Bağlantılar"), ("alt", "Ödeme"))},
    "10x20": {"ornekler": KARTVIZIT, "ortak": KISI, "out": os.path.join(U.OUT, "shopier", "kartvizit_ornekleri"),
              "etiket": "ÖRNEK KARTVİZİT", "chips": ("Ara", "WhatsApp", "E-posta", "Konum", "Rehbere kaydet"),
              "lede": "İsimlikteki QR'ı okutan kişi dijital kartvizitinizi açar. Her şey tek dokunuşla:",
              "ozet": "QR'ı okutan kişi dijital kartvizitinizi açar: ara, WhatsApp, e-posta, konum, rehbere kaydet.",
              "not": "Örnek kişi; telefon BOYDE LABS'in, e-posta ve QR örnektir.",
              "ekranlar": ("ust", "kisi", "mesaj"), "ikinci": "kisi", "son": "kisi",   # sayfa kısa: aşağısı yerine
              "uclu": (("ust", "Kartvizit"), ("kisi", "Rehbere kaydedilince"), ("mesaj", "Hazır WhatsApp mesajı"))},
}


def svg_of(cs, path):
    """CrossSection → SVG (y aşağı): şablonların logo işareti."""
    x0, y0, x1, y1 = cs.bounds()
    pad = 0.5
    d = ""
    for ring in cs.to_polygons():
        d += "M" + "L".join(f"{x - x0 + pad:.2f} {y1 - y + pad:.2f}" for x, y in ring) + "Z"
    w, h = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}"><path d="{d}"/></svg>\n')


def capture(out):
    """Telefon ekranı (390 × 844, 2×, hareketsiz son hâl): ilk ekran, ortası (bağlantılar) ve sonu (ödeme)."""
    from playwright.sync_api import sync_playwright
    errors, shots = [], []
    with sync_playwright() as p, SS.served(out) as url:
        b = p.chromium.launch(executable_path=SS.CHROMIUM)
        pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, reduced_motion="reduce")
        pg.on("pageerror", lambda x: errors.append(str(x)))
        pg.goto(url)
        pg.wait_for_timeout(700)
        shots.append(Image.open(io.BytesIO(pg.screenshot())))
        h = pg.evaluate("document.documentElement.scrollHeight")
        for y in (round((h - 844) / 2), h - 844):
            pg.evaluate(f"window.scrollTo(0, {max(0, y)})")
            pg.wait_for_timeout(500)
            shots.append(Image.open(io.BytesIO(pg.screenshot())))
        b.close()
    assert not errors, errors
    return shots


def mocks(site, msg):
    """Kartvizit (10 × 20) sayfası kısa: aşağısı yerine kartvizitin işini gösteren iki ekran (390 × 844, 2×):
    rehbere kaydedilince telefondaki kişi kartı ve WhatsApp'ta hazır gelen mesaj. Sade, markasız telefon arayüzü."""
    from playwright.sync_api import sync_playwright
    import boyde_marka as BM
    from sablonlar.ortak import svg
    ac = site.renk
    ini = "".join(w[0] for w in site.isletme.split()[:2]).upper()
    rows = [("cep", site.phone, True), ("iş e-posta", site.eposta, True), ("görev", SS.tr_title(site.hizmet), False),
            ("kurum", site.kurum, False), ("adres", SS.tr_title(site.sehir) or "Antalya", False)]
    rows = "".join(f"""<div style="padding:12px 16px;border-top:{'0' if k == 0 else '1px solid #e6e6ea'}">
      <p style="font-size:13px;color:#8b8e94">{a}</p><p style="margin-top:3px;font-size:17px;font-weight:600;
      color:{ac if link else '#121316'}">{v}</p></div>""" for k, (a, v, link) in enumerate(rows) if v)
    acts = "".join(f"""<div style="display:flex;flex-direction:column;align-items:center;gap:6px;flex:1;padding:10px 0;
      background:#fff;border-radius:12px">{svg(i)}<span style="font-size:12px;color:{ac};font-weight:600">{t}</span>
      </div>""" for i, t in (("whatsapp", "mesaj"), ("phone", "ara"), ("mail", "e-posta"), ("pin", "konum")))
    css = f"""{BM.font_css()}*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:"Space Grotesk",sans-serif;
      -webkit-font-smoothing:antialiased}}.ic{{width:22px;height:22px;fill:{ac}}}"""
    kisi = f"""<div style="width:390px;height:844px;background:#f2f2f5;color:#121316">
      <div style="display:flex;justify-content:space-between;align-items:center;padding:22px 18px 6px;font-size:16px">
        <span style="color:{ac}">İptal</span><b>Yeni kişi</b><b style="color:{ac}">Kaydet</b></div>
      <div style="margin:22px auto 0;width:112px;height:112px;border-radius:50%;background:{ac};display:grid;
        place-items:center;color:#fff;font-size:42px;font-weight:700">{ini}</div>
      <p style="margin-top:16px;text-align:center;font-size:28px;font-weight:700">{site.isletme}</p>
      <p style="margin-top:4px;text-align:center;font-size:15px;color:#55575c">{SS.tr_title(site.hizmet)} ·
        {site.kurum}</p>
      <div style="display:flex;gap:8px;margin:22px 16px 0">{acts}</div>
      <div style="margin:16px 16px 0;background:#fff;border-radius:14px;overflow:hidden">{rows}</div>
      <p style="margin:18px 24px 0;text-align:center;font-size:13px;color:#8b8e94">Kartvizit sayfasındaki
        <b style="color:#55575c">Rehbere kaydet</b> ile tek dokunuşta eklenir.</p></div>"""
    mesaj = f"""<div style="width:390px;height:844px;background:#ecebe8;color:#121316;position:relative">
      <div style="display:flex;align-items:center;gap:12px;padding:18px 16px 12px;background:#fff">
        <span style="font-size:26px;color:{ac};line-height:1">‹</span>
        <span style="width:40px;height:40px;border-radius:50%;background:{ac};display:grid;place-items:center;
          color:#fff;font-size:16px;font-weight:700">{ini}</span>
        <div><b style="font-size:17px">{site.isletme}</b><p style="font-size:13px;color:#8b8e94">{site.kurum}</p></div>
      </div>
      <p style="margin:22px auto 0;width:max-content;padding:5px 12px;border-radius:8px;background:#fff;
        font-size:12px;color:#8b8e94">Bugün</p>
      <p style="position:absolute;left:40px;right:40px;bottom:150px;padding:10px 14px;border-radius:12px;
        background:#fff;text-align:center;font-size:14px;line-height:1.4;color:#55575c">Kartvizitteki
        <b style="color:{ac}">WhatsApp</b>'a dokunan kişiye mesaj hazır gelir; göndermesi yeterli.</p>
      <div style="position:absolute;left:10px;right:10px;bottom:40px;display:flex;align-items:flex-end;gap:8px">
        <div style="flex:1;padding:13px 16px;border-radius:24px;background:#fff;font-size:16px;line-height:1.35">
          {msg}<span style="display:inline-block;width:2px;height:18px;margin-left:2px;vertical-align:-3px;
          background:{ac}"></span></div>
        <span style="flex:none;width:48px;height:48px;border-radius:50%;background:{ac};display:grid;
          place-items:center"><svg viewBox="0 0 24 24" style="width:22px;height:22px;fill:#fff;margin-left:3px">
          <path d="M2.01 21 23 12 2.01 3 2 10l15 2-15 2z"/></svg></span></div></div>"""
    out = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=SS.CHROMIUM)
        pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        for body in (kisi, mesaj):
            pg.set_content(f"<!doctype html><meta charset=utf-8><style>{css}</style><body>{body}</body>")
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(150)
            out.append(Image.open(io.BytesIO(pg.screenshot())))
        b.close()
    return out


def phone(src, w, bg="#121316"):
    """Telefon çerçevesi: üstte durum çubuğu (sayfanın zemin renginde, ortasında çentik), altında ekran görüntüsü
    (alt kenarı kırpılır)."""
    h = round(w * 844 / 390)
    sb = round(w * 0.1)
    return f"""<div style="position:relative;width:{w + 24}px;height:{h + 24}px;padding:12px;border-radius:{w * .14:.0f}px;
      background:#0b0b0d;box-shadow:0 40px 70px rgba(18,19,22,.35),inset 0 0 0 2px #2a2b30">
      <div style="width:{w}px;height:{h}px;border-radius:{w * .11:.0f}px;overflow:hidden;background:{bg}">
        <div style="height:{sb}px;position:relative"><span style="position:absolute;left:50%;top:{sb * .3:.0f}px;
          transform:translateX(-50%);width:{w * .3:.0f}px;height:{sb * .5:.0f}px;border-radius:12px;
          background:#0b0b0d"></span></div>
        <img src="{src}" style="width:{w}px;display:block"></div></div>"""


def ph(c, name, w):
    """Görseldeki telefon: c[name] ekranı, durum çubuğu o ekranın zemin renginde."""
    return phone(c[name], w, c["bgs"][name])


def bg_of(path):
    """Sayfanın zemin rengi: ilk ekranın sol üst köşesi (şablonların süsleri sağda)."""
    im = Image.open(path).convert("RGB")
    r, g, b = im.getpixel((8, 60))                      # en üstteki ince vurgu çizgisinin altı
    return f"#{r:02x}{g:02x}{b:02x}"


def head(K, c, dark=False, align="left"):
    ink, sub = (K.PAPER, "rgba(244,241,234,.7)") if dark else (K.INK, "#55575c")
    cfg = c["cfg"]
    return f"""<div style="text-align:{align}"><p class="k">{cfg['etiket']} · {c['i']}/{len(cfg['ornekler'])}</p>
      <h1 class="u" style="margin-top:14px;font-size:46px;line-height:1.08;color:{ink}">{c['site'].isletme}</h1>
      <p style="margin-top:12px;font-size:22px;color:{sub}">Şablon: <b style="color:{ink}">{c['T'].AD}</b></p></div>"""


def chips(K, c, dark=False, size=19):
    bg, fg = ("rgba(244,241,234,.1)", K.PAPER) if dark else ("#fff", K.INK)
    return "".join(f'<span class="chip" style="background:{bg};color:{fg};font-size:{size}px;padding:8px 14px">{x}'
                   f'</span>' for x in c["cfg"]["chips"])


def lede(c, dark=False, size=24):
    col = "rgba(244,241,234,.82)" if dark else "#3b3d42"
    return f'<p style="font-size:{size}px;line-height:1.45;color:{col}">{c["cfg"]["lede"]}</p>'


def l_iki(K, c):
    """1 · açık zemin, iki telefon (ilk ekran ve bağlantılar), köşede isimlik."""
    return f"""<div style="position:relative;width:1200px;height:1200px;background:{K.PAPER};overflow:hidden">
      <div style="position:absolute;left:64px;top:60px;width:480px">{head(K, c)}
        <div style="margin-top:24px">{lede(c)}</div>
        <div style="margin-top:16px;display:flex;flex-wrap:wrap;gap:8px">{chips(K, c)}</div></div>
      <div style="position:absolute;left:64px;bottom:150px;width:430px;border-radius:24px;overflow:hidden;
        background:#fff;box-shadow:0 20px 40px rgba(18,19,22,.12)">
        <img src="{c['foto']('studyo', 520)}" style="width:430px;height:300px;object-fit:cover;display:block"></div>
      <p style="position:absolute;left:64px;bottom:108px;font-size:19px;color:#55575c">İsimlik ve sitesi birlikte
        hazırlanır.</p>
      <div style="position:absolute;left:520px;top:300px">{ph(c, 'ust', 300)}</div>
      <div style="position:absolute;left:846px;top:236px">{ph(c, c['cfg']['ikinci'], 300)}</div>
      <div style="position:absolute;left:64px;bottom:40px">{K.logo("acik", 230, 46)}</div>
      <p style="position:absolute;right:64px;bottom:50px;font-size:17px;color:#8b8e94">{c['cfg']['not']}</p></div>"""


def l_tek(K, c):
    """2 · koyu zemin, tek büyük telefon, solda yazı ve isimlik."""
    return f"""<div style="position:relative;width:1200px;height:1200px;background:{K.INK};overflow:hidden;
      background-image:{c['BM'].stripes_bg(K.PAPER, .03, 30)}">
      <div style="position:absolute;left:64px;top:64px;width:500px">{head(K, c, True)}
        <div style="margin-top:24px">{lede(c, True)}</div>
        <div style="margin-top:16px;display:flex;flex-wrap:wrap;gap:8px">{chips(K, c, True)}</div></div>
      <div style="position:absolute;left:64px;top:612px;width:500px;height:360px;border-radius:24px;overflow:hidden;
        box-shadow:0 0 0 1.5px rgba(244,241,234,.14)">
        <img src="{c['foto']('studyo', 600)}" style="width:100%;height:100%;object-fit:cover;display:block"></div>
      <div style="position:absolute;left:650px;top:84px">{ph(c, 'ust', 410)}</div>
      <div style="position:absolute;left:64px;bottom:48px">{K.logo("koyu", 230, 46)}</div>
      <p style="position:absolute;right:64px;bottom:26px;font-size:16px;color:#8b8e94">{c['cfg']['not']}</p></div>"""


def l_uc(K, c):
    """3 · kum rengi zemin, üç telefon yan yana (ilk ekran, bağlantılar, ödeme), alttan taşar."""
    cols = "".join(f"""<div style="position:absolute;left:{48 + k * 380}px;top:{470 if k != 1 else 420}px">
        <span class="chip" style="position:absolute;left:0;top:-52px;background:{K.INK};color:{K.PAPER};
          font-size:17px;padding:7px 14px">{tag}</span>{ph(c, s, 320)}</div>"""
                   for k, (s, tag) in enumerate(c["cfg"]["uclu"]))
    return f"""<div style="position:relative;width:1200px;height:1200px;background:{K.SAND};overflow:hidden">
      <div style="position:absolute;left:64px;top:56px">{K.logo("acik", 210, 42)}</div>
      <div style="position:absolute;right:64px;top:48px;width:190px;height:190px;border-radius:28px;overflow:hidden;
        box-shadow:0 16px 32px rgba(18,19,22,.18)">
        <img src="{c['foto']('studyo', 400)}" style="width:100%;height:100%;object-fit:cover;display:block"></div>
      <div style="position:absolute;left:300px;right:300px;top:56px">{head(K, c, align="center")}
        <p style="margin-top:14px;font-size:19px;line-height:1.45;color:#3b3d42;text-align:center">{c['cfg']['ozet']}
          </p></div>
      {cols}
      <p style="position:absolute;right:64px;top:268px;font-size:15px;color:#6b6e74">{c['cfg']['not']}</p></div>"""


def l_akis(K, c):
    """4 · isimlikten siteye: büyük isimlik fotoğrafı, "QR'ı okut" oku, telefon."""
    return f"""<div style="position:relative;width:1200px;height:1200px;background:{K.PAPER};overflow:hidden">
      <div style="position:absolute;left:64px;top:60px;width:600px">{head(K, c)}</div>
      <div style="position:absolute;left:64px;top:300px;width:540px;height:540px;border-radius:32px;overflow:hidden;
        box-shadow:0 24px 50px rgba(18,19,22,.16)">
        <img src="{c['foto']('studyo', 700)}" style="width:100%;height:100%;object-fit:cover;display:block"></div>
      <div style="position:absolute;left:560px;top:520px;display:flex;flex-direction:column;align-items:center;gap:10px">
        <span style="font-size:17px;font-weight:700;letter-spacing:.14em;color:{K.ORANGE}">QR'I OKUT</span>
        <span style="display:grid;place-items:center;width:96px;height:96px;border-radius:50%;background:{K.ORANGE};
          color:#fff;font-size:48px;font-weight:700;box-shadow:0 0 0 10px {K.PAPER}">→</span></div>
      <div style="position:absolute;left:760px;top:150px">{ph(c, 'ust', 340)}</div>
      <div style="position:absolute;left:64px;top:890px;width:640px;display:flex;flex-wrap:wrap;gap:8px">
        {chips(K, c, size=18)}</div>
      <div style="position:absolute;left:64px;bottom:48px">{K.logo("acik", 230, 46)}</div>
      <p style="position:absolute;right:64px;bottom:58px;font-size:17px;color:#8b8e94">{c['cfg']['not']}</p></div>"""


def l_bolunmus(K, c):
    """5 · ikiye bölünmüş: solda koyu zeminde isimlik, sağda üst üste iki telefon."""
    return f"""<div style="position:relative;width:1200px;height:1200px;background:{K.PAPER};overflow:hidden">
      <div style="position:absolute;left:0;top:0;width:560px;height:1200px;background:{K.INK};overflow:hidden">
        <div style="position:absolute;left:56px;top:60px;width:460px">{head(K, c, True)}</div>
        <img src="{c['foto']('masa', 620)}" style="position:absolute;left:-10px;top:330px;width:580px;height:580px;
          display:block;-webkit-mask-image:radial-gradient(closest-side,#000 72%,transparent 100%)">
        <p style="position:absolute;left:56px;top:930px;width:440px;font-size:21px;line-height:1.45;
          color:rgba(244,241,234,.8)">İsimlik ve sitesi birlikte hazırlanır; QR doğrudan bu sayfayı açar.</p>
        <div style="position:absolute;left:56px;bottom:48px">{K.logo("koyu", 230, 46)}</div></div>
      <div style="position:absolute;left:612px;top:96px">{ph(c, 'ust', 270)}</div>
      <div style="position:absolute;left:880px;top:330px">{ph(c, c['cfg']['son'], 270)}</div>
      <p style="position:absolute;right:56px;bottom:40px;font-size:15px;color:#8b8e94">{c['cfg']['not']}</p></div>"""


LAYOUTS = (l_iki, l_tek, l_uc, l_akis, l_bolunmus)


def visual(P, cfg, i, key, T, isim, shots, site):
    import boyde_katalog as K
    import boyde_marka as BM

    def foto(view, w):
        path = os.path.join(K.FOTO, f"{isim}_{view}.jpg")
        return K.uri(path, w) if os.path.exists(path) else K.duz(isim, w)

    c = dict(zip(cfg["ekranlar"], (K.uri(s, 700) for s in shots)), i=i, site=site, T=T, foto=foto, BM=BM, cfg=cfg,
             bgs=dict(zip(cfg["ekranlar"], map(bg_of, shots))))
    path = os.path.join(cfg["out"], f"{i:02d}_{key}_{T.SLUG}.jpg")
    K.sq(P, LAYOUTS[(i - 1) % len(LAYOUTS)](K, c), path)
    return path


def main(cats=None):
    import boyde_marka as BM
    done = []
    for cat in cats or SETS:
        cfg = SETS[cat]
        shutil.rmtree(cfg["out"], ignore_errors=True)
        os.makedirs(cfg["out"])
        for i, (key, n, isim, mark, data) in enumerate(cfg["ornekler"], 1):
            done.append((cfg, i, key, n, isim, mark, data))
    for j, (cfg, i, key, n, isim, mark, data) in enumerate(done):
        folder = os.path.join(OUT, key)
        os.makedirs(folder, exist_ok=True)
        svg_of(mark(), os.path.join(folder, "logo", "isaret.svg"))
        d = dict(cfg["ortak"], **data, isaret="logo/isaret.svg")
        with open(os.path.join(folder, "bilgiler.json"), "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
            f.write("\n")
        with tempfile.TemporaryDirectory() as tmp:
            site, T, _ = SS.build(folder, n, out=tmp, previews=False, gif=False, record=False)
            shots = capture(os.path.join(tmp, "site"))
        if "kisi" in cfg["ekranlar"]:                    # kartvizit: ilk ekran, kişi kartı, hazır mesaj
            shots = shots[:1] + mocks(site, d["whatsapp_mesaj"])
        paths = []
        for k, s in zip(cfg["ekranlar"], shots):
            p = os.path.join(folder, f"ekran_{k}.png")
            s.save(p, optimize=True)
            paths.append(p)
        done[j] = (cfg, i, key, T, isim, paths, site)
    with BM.painter() as P:
        for cfg, i, key, T, isim, paths, site in done:
            print(os.path.relpath(visual(P, cfg, i, key, T, isim, paths, site), U.A.ROOT), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
