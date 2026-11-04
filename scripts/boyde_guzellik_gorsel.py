"""BOYDE LABS – güzellik koleksiyonunun görselleri (Shopier ve tanıtım), 1200 × 1200 JPG.

Görsel dil BOYDE'nin öbür ürün görselleriyle aynı (scripts/boyde_katalog.py: logo, turuncu model kodu, buzlu cam
şerit; renk paleti değişmez); ürünlerin pembe, nude, lila tonları fotoğraflardan gelir.

Çıktı (boyde_labs/guzellik/shopier/):
  9x12/01_G01_<ürün>.jpg … 10    BOYDE çerçevesinde stüdyo fotoğrafı: kod, tasarım, sektör, renkler
  10x20/01_K01_<ürün>.jpg … 10
  <kat>/ek/kapak.jpg             kategori kapağı (masada birkaç isimlik, başlık)
  <kat>/ek/modeller.jpg          10 model bir arada (düz görünüşler, kodlarıyla)
  siteler/0N_<işletme>.jpg       5 site şablonu (6–10): isimliğin fotoğrafı ve telefonda QR'ın açtığı sayfa
Girdi : boyde_labs/guzellik/fotograf (scripts/boyde_guzellik.py --foto), kaynak/<ürün>_duz.png,
        boyde_labs/guzellik/siteler/<işletme>/ (örnek işletmelerin bilgileri; sablon_site ile kurulur)
Örneklerdeki işletme ve kişi adları, telefon (BOYDE'nin), IBAN ve QR'lar örnektir (QR'lar okunmaz).

  ../katalog.pdf, ../katalog.png  A4 katalog (9 sayfa) ve sayfaların önizlemesi

Kullanım: python3 scripts/boyde_guzellik_gorsel.py              # hepsi
          python3 scripts/boyde_guzellik_gorsel.py --katalog    # yalnız katalog
"""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_guzellik as G  # noqa: E402  (örnek modu: QR'lar okunmaz)
import boyde_katalog as K  # noqa: E402
import boyde_marka as BM  # noqa: E402

INK, PAPER, ORANGE, SAND = K.INK, K.PAPER, K.ORANGE, K.SAND
OUT = os.path.join(G.OUT, "shopier")
KAT = {"9x12": {"ad": "QR'lı masa isimliği", "olcu": "9 × 12 cm", "kisa": "Kuaför, güzellik salonu, tırnak, kirpik, "
                "cilt bakım, spa: masaya, tezgâha, kasaya.", "on": "g_"},
       "10x20": {"ad": "Kurumsal isimlik", "olcu": "10 × 20 cm", "kisa": "Saç tasarımcısı, nail artist, estetisyen, "
                 "makyaj ve kirpik uzmanı: ad soyad, görev, kartvizit QR'ı.", "on": "p_"}}
# örnek siteler: (işletme klasörü, şablon, isimliği)
SITELER = [("defne", 6, "g_defne"), ("sakayik", 7, "g_sakayik"), ("ela", 8, "g_ela"), ("lal", 9, "g_lal"),
           ("papatya", 10, "g_papatya")]


def foto(key, view="studyo", maxw=1200):
    return K.uri(os.path.join(G.FOTO, f"{key}_{view}.jpg"), maxw)


def acik_mi(key, view="studyo"):
    return K.light(os.path.join(G.FOTO, f"{key}_{view}.jpg"))


def cerceve(P, cat, u, path, view="studyo"):
    """BOYDE çerçevesi (boyde_katalog.framed ile aynı düzen): fotoğraf tam kadraj, sol üstte logo, sağ üstte ölçü,
    altta buzlu cam şeritte turuncu kod, tasarım ve sektör, renkler."""
    key, kod, kim, sektor, tasarim, renk = u
    acik = acik_mi(key, view)
    fg, sub = (INK, "#55575c") if acik else (PAPER, "rgba(244,241,234,.72)")
    glass, edge = ("rgba(255,255,255,.62)", "rgba(18,19,22,.08)") if acik else \
        ("rgba(18,19,22,.55)", "rgba(244,241,234,.12)")
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;overflow:hidden">
      <img src="{foto(key, view)}" style="position:absolute;inset:0;width:100%;height:100%;display:block">
      <div style="position:absolute;left:44px;top:40px">{K.logo("acik" if acik else "koyu", 260, 58)}</div>
      <span style="position:absolute;right:44px;top:44px;font-size:15px;font-weight:700;letter-spacing:.2em;
        color:{fg};opacity:.75">GÜZELLİK · {KAT[cat]['olcu'].upper()}</span>
      <div style="position:absolute;left:28px;right:28px;bottom:28px;display:flex;align-items:center;gap:22px;
        padding:18px 26px 18px 18px;border-radius:26px;background:{glass};backdrop-filter:blur(22px) saturate(1.3);
        box-shadow:inset 0 0 0 1.5px {edge};color:{fg}">
        <span class="code" style="flex:none;display:grid;place-items:center;width:84px;height:84px;border-radius:18px;
          background:{ORANGE};color:#fff;font-size:26px">{kod}</span>
        <div style="flex:1;min-width:0">
          <p class="u" style="font-size:27px;line-height:1.15;white-space:nowrap;overflow:hidden;
            text-overflow:ellipsis">{sektor} · {tasarim}</p>
          <p style="margin-top:7px;font-size:18px;color:{sub};white-space:nowrap;overflow:hidden;
            text-overflow:ellipsis">{renk} · örnek: {kim}</p></div>
        <p style="flex:none;text-align:right;font-size:14px;font-weight:700;letter-spacing:.14em;line-height:1.5;
          color:{sub}">TASARIM VE<br>3D BASKI <b style="color:{ORANGE}">BOYDE</b></p></div></div>""", path)


def kapak(P, cat, path):
    k = KAT[cat]
    src = os.path.join(G.FOTO, f"kapak_{cat}.jpg")
    acik = K.light(src)
    fg, sub = (INK, "#3b3d42") if acik else (PAPER, "rgba(244,241,234,.82)")
    golge = "" if acik else """<div style="position:absolute;inset:0;background:linear-gradient(180deg,
      rgba(18,19,22,.6) 0,rgba(18,19,22,0) 24%,rgba(18,19,22,0) 58%,rgba(18,19,22,.9) 100%)"></div>"""
    cips = "".join(f'<span class="chip" style="background:{"#fff" if acik else "rgba(244,241,234,.12)"};color:{fg};'
                   f'font-size:19px;padding:8px 14px">{x}</span>' for x in
                   ("10 tasarım", "çiçek motifleri", "pembe · nude · lila", "el yazısı", "QR'lı"))
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;overflow:hidden">
      <img src="{K.uri(src, 1200)}" style="position:absolute;inset:0;width:100%;height:100%;display:block">{golge}
      <div style="position:absolute;left:60px;top:52px">{K.logo("acik" if acik else "koyu", 300, 62)}</div>
      <div style="position:absolute;left:60px;right:60px;bottom:58px;color:{fg}">
        <p class="k">GÜZELLİK KOLEKSİYONU · {k['olcu'].upper()}</p>
        <h1 class="u" style="margin-top:14px;font-size:70px;line-height:1.02;letter-spacing:-.02em">{k['ad']}</h1>
        <p style="margin-top:16px;font-size:27px;line-height:1.35;color:{sub}">{k['kisa']}</p>
        <div style="margin-top:22px;display:flex;flex-wrap:wrap;gap:10px">{cips}</div></div></div>""", path)


def modeller(P, cat, path):
    us = [u for u in G.URUNLER if u[0].startswith(KAT[cat]["on"])]
    sut = 4 if cat == "9x12" else 3
    w = (1200 - 2 * 56 - (sut - 1) * 22) // sut
    kart = "".join(f"""<div style="width:{w}px;text-align:center">
      <div style="height:{w * (0.78 if cat == '9x12' else 0.5):.0f}px;display:grid;place-items:center">
        <img src="{K.uri(os.path.join(G.SRC, f'{key}_duz.png'), 700, 'PNG')}" style="max-width:100%;max-height:100%;
        filter:drop-shadow(0 10px 16px rgba(18,19,22,.18))"></div>
      <p style="margin-top:10px;font-size:17px;font-weight:700"><span class="code" style="color:{ORANGE}">{kod}</span>
        &nbsp;{sektor}</p></div>""" for key, kod, _, sektor, _, _ in us)
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:{PAPER};padding:56px;color:{INK}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <div><p class="k">GÜZELLİK KOLEKSİYONU · {KAT[cat]['olcu'].upper()}</p>
        <h2 class="u" style="margin-top:12px;font-size:44px;line-height:1.08">10 tasarım, hepsi size özel<br>
          renk ve yazıyla.</h2></div>{K.logo("acik", 220, 44)}</div>
      <div style="margin-top:{40 if cat == '9x12' else 30}px;display:flex;flex-wrap:wrap;justify-content:center;
        gap:{30 if cat == '9x12' else 18}px 22px">{kart}</div>
      <p style="position:absolute;left:56px;right:56px;bottom:40px;font-size:16px;color:#55575c">
        Örneklerdeki işletme ve kişi adları, telefon ve QR'lar örnektir; tasarım sizin bilgilerinizle hazırlanır.</p>
      </div>""", path)


def site_ekrani(klasor, n):
    """Örnek işletmenin sitesi (sablon_site, kayda yazılmaz) ve telefondaki ilk ekranı. Playwright'ı kendisi açar:
    görseller çizilmeden önce çağrılır. Döner (işletme, şablon adı, ekran görüntüsü PNG yolu, zemin rengi)."""
    import boyde_site_gorsel as SG
    import sablon_site as SS
    tmp = tempfile.mkdtemp()
    try:
        site, T, _ = SS.build(os.path.join(G.OUT, "siteler", klasor), n, out=tmp, previews=False, record=False)
        ekran = SG.capture(os.path.join(tmp, "site"))[0]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    yol = os.path.join(G.OUT, "siteler", klasor, "ekran_ust.png")
    ekran.save(yol, optimize=True)
    return site.isletme, T.AD, yol, SG.bg_of(yol)


def site_gorseli(P, i, ekran, key, path):
    """İsimlikten siteye: solda isimliğin fotoğrafı (karşıdan), sağda telefonda QR'ın açtığı sayfa (ilk ekran)."""
    import boyde_site_gorsel as SG
    isletme, sablon, yol, zemin = ekran
    tel = SG.phone(K.uri(yol, 780, "PNG"), 330, zemin)
    cips = "".join(f'<span class="chip" style="background:#fff;color:{INK};font-size:18px;padding:8px 13px">{x}</span>'
                   for x in ("Ara", "Randevu (WhatsApp)", "Instagram", "Google yorum", "Konum", "IBAN", "Rehbere kaydet"))
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:{PAPER};overflow:hidden;color:{INK}">
      <div style="position:absolute;left:56px;top:50px;right:56px;display:flex;justify-content:space-between">
        <div><p class="k">ÖRNEK SİTE · GÜZELLİK · {i}/{len(SITELER)}</p>
          <h1 class="u" style="margin-top:12px;font-size:44px;line-height:1.08">{isletme}</h1>
          <p style="margin-top:10px;font-size:22px;color:#55575c">Şablon: <b style="color:{INK}">{sablon}</b></p></div>
        {K.logo("acik", 210, 44)}</div>
      <div style="position:absolute;left:56px;top:250px;width:620px;height:620px;border-radius:34px;overflow:hidden;
        box-shadow:0 30px 60px -30px rgba(18,19,22,.45)">
        <img src="{foto(key, 'on', 900)}" style="width:100%;height:100%;object-fit:cover;display:block"></div>
      <div style="position:absolute;right:70px;top:196px">{tel}</div>
      <div style="position:absolute;left:56px;right:56px;bottom:52px">
        <p style="font-size:24px;line-height:1.4;color:#3b3d42;max-width:640px">İsimlikteki QR'ı okutan müşteri bu
          sayfayı açar. Her şey tek dokunuşla:</p>
        <div style="margin-top:16px;display:flex;flex-wrap:wrap;gap:10px">{cips}</div></div></div>""", path)


# ---------------------------------------------------------------- katalog (A4, boyde_katalog.catalog düzeninde)

W, H = 794, 1123
FILAMENT = {G.PUDRA: "PLA Matte Sakura Pink", G.GUL: "dusty rose", G.FUSYA: "PLA Basic Hot Pink",
            G.NUDE: "PLA Matte Latte Brown", G.KREM: "PLA Matte Ivory White", G.MOKA: "PLA Matte Dark Chocolate",
            G.MURDUM: "PLA Matte Plum", G.LILA: "PLA Matte Lilac Purple", G.ROSE: "PLA Silk Rose Gold",
            G.ADACAYI: "sage (adaçayı)"}
OZELLIK = {"9x12": ["120 × 90 mm, 1 cm gövde; gövde rengi size göre (beyaz, pudra, nude, lila, siyah…)",
                    "Yazı ve çiçek motifleri 2 mm kabartma, 3–4 renk",
                    "QR yüzeyle aynı hizada (renkli gövdede beyaz karoda): keskin, kolay okunur",
                    "15° eğik sehpa dahil, tutkal gerekmez",
                    "QR salonunuza özel sayfayı açar: randevu (WhatsApp), Instagram, konum, yorum, IBAN"],
           "10x20": ["200 × 100 mm, 5 mm gövde", "Yazı ve motifler yüzeyle aynı hizada renkli: el yazısı adlar ince "
                     "ayrıntısıyla", "Ad soyad, unvan, salon adı ve telefon", "Sehpa dahil",
                     "QR dijital kartvizitinizi açar: ara, randevu, Instagram, rehbere kaydet"]}


def sayfa(body, dark=False, no=None):
    bg = f"background:{INK};color:{PAPER}" if dark else f"background:{PAPER};color:{INK}"
    foot = (f'<p style="position:absolute;left:48px;right:48px;bottom:26px;display:flex;justify-content:space-between;'
            f'font-size:10px;letter-spacing:.2em;color:{K.GRAY}"><span>BOYDE LABS · GÜZELLİK KOLEKSİYONU</span>'
            f'<span>{no:02d}</span></p>') if no else ""
    return f'<div class="pg" style="{bg};padding:48px">{body}{foot}</div>'


def kart(u):
    key, kod, kim, sektor, tasarim, renk = u
    return f"""<div style="background:#fff;border-radius:14px;overflow:hidden;display:flex;flex-direction:column">
      <img src="{foto(key, maxw=560)}" style="width:100%;aspect-ratio:16/10;object-fit:cover;display:block">
      <div style="padding:10px 12px 12px"><div style="display:flex;justify-content:space-between;align-items:center">
        <b class="code" style="font-size:13px">{kod}</b><span style="font-size:9.5px;font-weight:700;color:{K.GRAY};
        letter-spacing:.06em">ÖRNEK TASARIM</span></div>
        <p style="margin-top:5px;font-size:13px;font-weight:700">{sektor} · {tasarim}</p>
        <p style="margin-top:2px;font-size:11px;color:#55575c;white-space:nowrap;overflow:hidden;
          text-overflow:ellipsis">{kim} · {renk}</p></div></div>"""


def katalog(P):
    """boyde_labs/guzellik/katalog.pdf ve katalog.png (sayfaların önizlemesi): kapak, nasıl çalışır, renkler ve
    motifler, iki kategori (giriş ve 10 model), siteler, sipariş."""
    import json
    import sablonlar
    import boyde_site_gorsel as SG
    from PIL import Image
    pages, no = [], 1
    kp = os.path.join(G.FOTO, "kapak_9x12.jpg")                # koyu gölgeli: yazılar açık
    pages.append(sayfa(f"""<div style="position:absolute;inset:0;background:url({K.uri(kp, 1100)}) center/cover"></div>
      <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(18,19,22,.72) 0,rgba(18,19,22,0) 28%,
        rgba(18,19,22,0) 50%,rgba(18,19,22,.96) 100%)"></div>
      <div style="position:relative">{K.logo("koyu", 260, 52)}</div>
      <div style="position:absolute;left:48px;right:48px;bottom:64px">
        <p class="k">ÜRÜN KATALOĞU · GÜZELLİK KOLEKSİYONU</p>
        <h1 class="u" style="margin-top:12px;font-size:50px;line-height:1.04">Kuaför ve güzellik<br>salonlarına
          isimlik</h1>
        <p style="margin-top:16px;font-size:16px;line-height:1.5;opacity:.85">Pembe, nude, lila tonlarında; çiçek
          motifli, el yazısı adlı QR'lı isimlikler. Salonunuz için 9 × 12 cm masa isimliği, ekibiniz için 10 × 20 cm
          kurumsal isimlik. Tasarımdan 3D baskıya, kendi atölyemizde.</p></div>""", dark=True))
    no += 1

    cats = "".join(f"""<div style="background:#fff;border-radius:16px;overflow:hidden">
      <img src="{foto(k, 'on', 600)}" style="width:100%;height:210px;object-fit:cover;display:block">
      <div style="padding:14px 16px"><p class="k" style="font-size:10px">{KAT[cat]['olcu'].upper()} ·
        SİZE ÖZEL 10 TASARIM</p><p class="u" style="margin-top:6px;font-size:17px">{KAT[cat]['ad']}</p>
        <p style="margin-top:6px;font-size:12px;line-height:1.45;color:#55575c">{KAT[cat]['kisa']}</p></div>
      </div>""" for cat, k in (("9x12", "g_sakayik"), ("10x20", "p_aylin")))
    steps = "".join(f"""<div style="display:flex;gap:14px;padding:12px 0;border-top:1px solid #ddd6ca">
      <b class="u" style="color:{ORANGE};font-size:18px;width:36px">{a}</b><div><p style="font-weight:700;
      font-size:14px">{b}</p><p style="margin-top:3px;font-size:12px;color:#55575c">{c}</p></div></div>"""
                    for a, b, c in K.SIPARIS)
    pages.append(sayfa(f"""<p class="k">NASIL ÇALIŞIR</p>
      <h2 class="u" style="margin-top:10px;font-size:28px;line-height:1.15">Tezgâhınızda durur,<br>müşteriniz
        okutur, randevu alır.</h2>
      <p style="margin-top:14px;font-size:13.5px;line-height:1.6;color:#3b3d42;max-width:620px">İsimlikteki QR'ı
        okutan müşteriniz salonunuza özel sayfayı açar: tek dokunuşla arar, WhatsApp'tan randevu ister, Instagram'ınıza
        ve konumunuza ulaşır, Google'da yorum yapar, IBAN'ınızı kopyalar. Kurumsal isimlikte QR dijital kartvizittir.
        Bilgileriniz değişirse sayfayı güncelleriz; isimlik aynı kalır.</p>
      <div style="margin-top:24px;display:grid;grid-template-columns:1fr 1fr;gap:16px">{cats}</div>
      <div style="margin-top:22px">{steps}</div>
      <img src="{K.uri(os.path.join(G.FOTO, 'kapak_10x20.jpg'), 900)}" style="margin-top:14px;width:100%;height:190px;
        object-fit:cover;object-position:50% 46%;border-radius:14px;display:block">
      <p style="margin-top:12px;font-size:11px;color:{K.GRAY}">{K.NOT_ORNEK}</p>""", no=no))
    no += 1

    sw = "".join(f"""<div style="display:flex;align-items:center;gap:12px;padding:10px 12px;background:#fff;
      border-radius:12px"><i style="flex:none;width:40px;height:40px;border-radius:10px;background:rgb{rgb};
      box-shadow:inset 0 0 0 1px rgba(18,19,22,.1)"></i><div><p style="font-weight:700;font-size:13.5px">
      {ad.capitalize()}</p><p style="font-size:11px;color:#55575c">{FILAMENT[k]}</p></div></div>"""
                 for k, (ad, rgb) in G.RENK.items())
    yaz = "".join(f"""<div style="padding:10px;background:#fff;border-radius:12px"><img src="{K.uri(
        os.path.join(G.SRC, f'{k}_duz.png'), 500, 'PNG')}" style="width:100%;height:150px;object-fit:contain;
        display:block"><p style="margin-top:6px;font-size:11.5px;color:#55575c">{t}</p></div>"""
                  for k, t in (("g_defne", "Pacifico ve çiçekli dal"), ("g_ela", "Yesteryear ve kirpik"),
                               ("g_gulce", "Fraunces ve güllü dal"), ("g_sakayik", "Fraunces italik ve şakayık"),
                               ("g_papatya", "Pacifico ve papatya"), ("g_lotus", "Fraunces ve nilüfer")))
    pages.append(sayfa(f"""<p class="k">RENKLER VE DOKUNUŞLAR</p>
      <h2 class="u" style="margin-top:10px;font-size:28px;line-height:1.15">Salonunuzun renginde,<br>çiçekli ve el
        yazısıyla.</h2>
      <p style="margin-top:14px;font-size:13.5px;line-height:1.6;color:#3b3d42;max-width:620px">Gövde ve yazı
        renklerini salonunuza göre seçiyoruz: pudra pembe, ten rengi, lila, krem ya da siyah gövde; beyaz, mürdüm,
        moka, rose gold yazılar. Adınız el yazısı ya da yumuşak harflerle; yanında çiçek, papatya, şakayık, nilüfer,
        kirpik, oje, ruj, fiyonk gibi motifler.</p>
      <div style="margin-top:22px;display:grid;grid-template-columns:repeat(2,1fr);gap:10px">{sw}</div>
      <div style="margin-top:22px;display:grid;grid-template-columns:repeat(3,1fr);gap:10px">{yaz}</div>
      <p style="margin-top:14px;font-size:11px;color:{K.GRAY}">Renkler fotoğraftaki tonlardır; baskıda yakın renkte
        filament kullanılır. Beyaz, siyah, sarı ve altın da var.</p>""", no=no))
    no += 1

    for cat in KAT:
        k = KAT[cat]
        us = [u for u in G.URUNLER if u[0].startswith(k["on"])]
        feats = "".join(f'<li style="padding:7px 0;border-top:1px solid rgba(244,241,234,.14)">{f}</li>'
                        for f in OZELLIK[cat])
        pages.append(sayfa(f"""<p class="k">KATEGORİ · {k['olcu'].upper()}</p>
          <h2 class="u" style="margin-top:10px;font-size:34px;line-height:1.1">{k['ad']}</h2>
          <p style="margin-top:10px;font-size:14px;color:rgba(244,241,234,.78)">{k['kisa']} Size özel 10 tasarım; en
            beğendiğinizi basıyoruz.</p>
          <img src="{K.uri(os.path.join(G.FOTO, f'kapak_{cat}.jpg'), 900)}" style="margin-top:22px;width:100%;
            height:520px;object-fit:cover;border-radius:16px;display:block;box-shadow:0 0 0 1.5px rgba(244,241,234,.16)">
          <ul style="margin-top:20px;list-style:none;font-size:13.5px;line-height:1.4">{feats}</ul>""",
                           dark=True, no=no))
        no += 1
        grid = "".join(kart(u) for u in us) + f"""<div style="border-radius:14px;background:{ORANGE};color:#fff;
          padding:14px;display:flex;flex-direction:column;justify-content:flex-end"><p class="u" style="font-size:15px">
          Size özel 10 tasarım</p><p style="margin-top:5px;font-size:11.5px;line-height:1.4">Sizin adınız ve
          renklerinizle; en beğendiğinizi basıyoruz.</p></div>
          <div style="border-radius:14px;background:{INK};color:{PAPER};padding:14px;display:flex;
          flex-direction:column;justify-content:space-between">{K.logo("koyu", 150, 30)}<p style="font-size:14px;
          font-weight:700">{K.TEL}</p></div>"""
        pages.append(sayfa(f"""<div style="display:flex;justify-content:space-between;align-items:flex-end">
          <div><p class="k">{k['olcu'].upper()} · {k['ad'].upper()}</p><h2 class="u" style="margin-top:8px;
          font-size:22px">{us[0][1]}–{us[-1][1]}</h2></div>{K.logo("acik", 150, 30)}</div>
          <div style="margin-top:18px;display:grid;grid-template-columns:repeat(3,1fr);gap:10px">{grid}</div>""",
                           no=no))
        no += 1

    tel = []
    for klasor, n, _ in SITELER:
        shot = os.path.join(G.OUT, "siteler", klasor, "ekran_ust.png")
        d = json.load(open(os.path.join(G.OUT, "siteler", klasor, "bilgiler.json"), encoding="utf-8"))
        tel.append(f"""<div style="display:flex;flex-direction:column;align-items:center;gap:12px">
          {SG.phone(K.uri(shot, 500, "PNG"), 132, SG.bg_of(shot))}
          <p style="font-weight:700;font-size:14px;text-align:center">{d['isletme']}</p>
          <p style="margin-top:-8px;font-size:11.5px;color:rgba(244,241,234,.65)">Şablon: {sablonlar.get(n).AD}</p>
          </div>""")
    pages.append(sayfa(f"""<p class="k">İSİMLİKLE GELEN SİTE</p>
      <h2 class="u" style="margin-top:10px;font-size:28px;line-height:1.15">Her isimliğe<br>salonunuza özel sayfa.</h2>
      <p style="margin-top:14px;font-size:13.5px;line-height:1.6;color:rgba(244,241,234,.78);max-width:620px">QR'ı
        okutan müşteriniz bu sayfayı açar: ara, randevu (WhatsApp), Instagram, Google yorum, konum, rehbere kaydet ve
        IBAN (tek dokunuşla kopyalanır). Güzellik salonları için beş şablondan biri, sizin renginiz ve logonuzla;
        uygulama gerekmez.</p>
      <div style="margin-top:26px;display:flex;flex-wrap:wrap;justify-content:center;gap:12px 40px">{''.join(tel)}
      </div>
      <p style="margin-top:22px;font-size:11px;color:{K.GRAY}">Örnek işletmeler; telefon BOYDE LABS'in, IBAN ve QR
        örnektir.</p>""", dark=True, no=no))
    no += 1

    kolaj = "".join(f'<img src="{foto(k, v, 500)}" style="width:100%;aspect-ratio:1;object-fit:cover;border-radius:12px;'
                    f'display:block">' for k, v in (("g_papatya", "studyo"), ("g_lal", "masa"), ("p_melis", "studyo"),
                                                    ("g_ipek", "on"), ("p_gizem", "masa"), ("g_lotus", "studyo")))
    pages.append(sayfa(f"""<p class="k">SİPARİŞ</p>
      <h2 class="u" style="margin-top:10px;font-size:26px">Salonunuza özel tasarım</h2>
      <p style="margin-top:10px;font-size:13px;color:#3b3d42;max-width:620px">Adınızı, logonuzu, renklerinizi,
        telefonunuzu ve Instagram'ınızı gönderin; size özel 10 tasarım hazırlayalım. Ekibiniz için kurumsal
        isimlikleri de aynı renk ve motiflerle yapıyoruz.</p>
      <div style="margin-top:18px;display:grid;grid-template-columns:repeat(3,1fr);gap:10px">{kolaj}</div>
      <div style="margin-top:28px;background:{INK};color:{PAPER};border-radius:18px;padding:30px 32px;
        background-image:{BM.stripes_bg(PAPER, .035, 22)}">
        <p class="k">SİPARİŞ</p>
        <p class="u" style="margin-top:10px;font-size:24px;line-height:1.2">Shopier mağazamızdan<br>ya da telefonla.</p>
        <p style="margin-top:14px;font-size:28px;font-weight:700">{K.TEL}</p>
        <p style="margin-top:6px;font-size:13px;color:rgba(244,241,234,.75)">Siparişten sonra size özel 10 tasarım
          gönderiyoruz; en beğendiğinizi basıyoruz.</p>
        <div style="margin-top:22px">{K.logo("koyu", 240, 48)}</div></div>""", no=no))

    path = os.path.join(G.OUT, "katalog.pdf")
    shots = P.pdf(pages, W, H, path, css=K.CSS)
    cols, tw, th = 4, 397, 562
    rows = (len(shots) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * 16, rows * th + (rows + 1) * 16), SAND)
    for i, s in enumerate(shots):
        sheet.paste(s.resize((tw, th), Image.LANCZOS), (16 + (i % cols) * (tw + 16), 16 + (i // cols) * (th + 16)))
    sheet.save(os.path.join(G.OUT, "katalog.png"), optimize=True)
    return path, len(pages)


def main():
    if "--katalog" in sys.argv:                          # yalnız katalog (görseller ve site ekranları hazırsa)
        with BM.painter() as P:
            path, n = katalog(P)
        print(f"{os.path.relpath(path, G.A.ROOT)}: {n} sayfa", flush=True)
        return
    shutil.rmtree(OUT, ignore_errors=True)
    ekranlar = [site_ekrani(klasor, n) for klasor, n, _ in SITELER]
    with BM.painter() as P:
        for cat in KAT:
            out = os.path.join(OUT, cat)
            os.makedirs(os.path.join(out, "ek"))
            us = [u for u in G.URUNLER if u[0].startswith(KAT[cat]["on"])]
            for k, u in enumerate(us, 1):
                cerceve(P, cat, u, os.path.join(out, f"{k:02d}_{u[1]}_{u[0][2:]}.jpg"))
            kapak(P, cat, os.path.join(out, "ek", "kapak.jpg"))
            modeller(P, cat, os.path.join(out, "ek", "modeller.jpg"))
            print(f"shopier/{cat}: {len(us)} model, kapak, modeller", flush=True)
        os.makedirs(os.path.join(OUT, "siteler"))
        for i, ((klasor, _, key), ekran) in enumerate(zip(SITELER, ekranlar), 1):
            site_gorseli(P, i, ekran, key, os.path.join(OUT, "siteler", f"{i:02d}_{klasor}.jpg"))
            print(f"siteler/{i:02d}_{klasor}.jpg: {ekran[0]} · {ekran[1]}", flush=True)
        path, n = katalog(P)
        print(f"{os.path.relpath(path, G.A.ROOT)}: {n} sayfa", flush=True)


if __name__ == "__main__":
    main()
