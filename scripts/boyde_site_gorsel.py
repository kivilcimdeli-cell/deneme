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


def bg_of(path):
    """Sayfanın zemin rengi: ilk ekranın sol üst köşesi (şablonların süsleri sağda)."""
    im = Image.open(path).convert("RGB")
    r, g, b = im.getpixel((8, 60))                      # en üstteki ince vurgu çizgisinin altı
    return f"#{r:02x}{g:02x}{b:02x}"


CHIPS = ("Ara", "WhatsApp", "Instagram", "Konum", "Google yorum", "IBAN", "Rehbere kaydet")
NOT = "Örnek işletme; telefon BOYDE LABS'in, IBAN ve QR örnektir."


def head(K, i, site, T, dark=False, align="left"):
    ink, sub = (K.PAPER, "rgba(244,241,234,.7)") if dark else (K.INK, "#55575c")
    return f"""<div style="text-align:{align}"><p class="k">ÖRNEK SİTE · {i}/{len(ORNEKLER)}</p>
      <h1 class="u" style="margin-top:14px;font-size:46px;line-height:1.08;color:{ink}">{site.isletme}</h1>
      <p style="margin-top:12px;font-size:22px;color:{sub}">Şablon: <b style="color:{ink}">{T.AD}</b></p></div>"""


def chips(K, dark=False, size=19):
    bg, fg = ("rgba(244,241,234,.1)", K.PAPER) if dark else ("#fff", K.INK)
    return "".join(f'<span class="chip" style="background:{bg};color:{fg};font-size:{size}px;padding:8px 14px">{c}'
                   f'</span>' for c in CHIPS)


def lede(dark=False, size=24):
    col = "rgba(244,241,234,.82)" if dark else "#3b3d42"
    return (f'<p style="font-size:{size}px;line-height:1.45;color:{col}">İsimlikteki QR\'ı okutan müşteri bu '
            f'sayfayı açar. Her şey tek dokunuşla:</p>')


def l_iki(K, c):
    """1 · açık zemin, iki telefon (ilk ekran ve bağlantılar), köşede isimlik."""
    return f"""<div style="position:relative;width:1200px;height:1200px;background:{K.PAPER};overflow:hidden">
      <div style="position:absolute;left:64px;top:60px;width:480px">{head(K, c['i'], c['site'], c['T'])}
        <div style="margin-top:24px">{lede()}</div>
        <div style="margin-top:16px;display:flex;flex-wrap:wrap;gap:8px">{chips(K)}</div></div>
      <div style="position:absolute;left:64px;bottom:150px;width:430px;border-radius:24px;overflow:hidden;
        background:#fff;box-shadow:0 20px 40px rgba(18,19,22,.12)">
        <img src="{c['foto']('studyo', 520)}" style="width:430px;height:300px;object-fit:cover;display:block"></div>
      <p style="position:absolute;left:64px;bottom:108px;font-size:19px;color:#55575c">İsimlik ve sitesi birlikte
        hazırlanır.</p>
      <div style="position:absolute;left:520px;top:300px">{phone(c['ust'], 300, c['bg'])}</div>
      <div style="position:absolute;left:846px;top:236px">{phone(c['orta'], 300, c['bg'])}</div>
      <div style="position:absolute;left:64px;bottom:40px">{K.logo("acik", 230, 46)}</div>
      <p style="position:absolute;right:64px;bottom:50px;font-size:17px;color:#8b8e94">{NOT}</p></div>"""


def l_tek(K, c):
    """2 · koyu zemin, tek büyük telefon, solda yazı ve isimlik."""
    return f"""<div style="position:relative;width:1200px;height:1200px;background:{K.INK};overflow:hidden;
      background-image:{c['BM'].stripes_bg(K.PAPER, .03, 30)}">
      <div style="position:absolute;left:64px;top:64px;width:500px">{head(K, c['i'], c['site'], c['T'], True)}
        <div style="margin-top:24px">{lede(True)}</div>
        <div style="margin-top:16px;display:flex;flex-wrap:wrap;gap:8px">{chips(K, True)}</div></div>
      <div style="position:absolute;left:64px;top:612px;width:500px;height:360px;border-radius:24px;overflow:hidden;
        box-shadow:0 0 0 1.5px rgba(244,241,234,.14)">
        <img src="{c['foto']('studyo', 600)}" style="width:100%;height:100%;object-fit:cover;display:block"></div>
      <div style="position:absolute;left:650px;top:84px">{phone(c['ust'], 410, c['bg'])}</div>
      <div style="position:absolute;left:64px;bottom:48px">{K.logo("koyu", 230, 46)}</div>
      <p style="position:absolute;right:64px;bottom:26px;font-size:16px;color:#8b8e94">{NOT}</p></div>"""


def l_uc(K, c):
    """3 · kum rengi zemin, üç telefon yan yana (ilk ekran, bağlantılar, ödeme), alttan taşar."""
    tags = ("İlk ekran", "Bağlantılar", "Ödeme")
    cols = "".join(f"""<div style="position:absolute;left:{48 + k * 380}px;top:{470 if k != 1 else 420}px">
        <span class="chip" style="position:absolute;left:0;top:-52px;background:{K.INK};color:{K.PAPER};
          font-size:17px;padding:7px 14px">{tags[k]}</span>{phone(c[s], 320, c['bg'])}</div>"""
                   for k, s in enumerate(("ust", "orta", "alt")))
    return f"""<div style="position:relative;width:1200px;height:1200px;background:{K.SAND};overflow:hidden">
      <div style="position:absolute;left:64px;top:56px">{K.logo("acik", 210, 42)}</div>
      <div style="position:absolute;right:64px;top:48px;width:190px;height:190px;border-radius:28px;overflow:hidden;
        box-shadow:0 16px 32px rgba(18,19,22,.18)">
        <img src="{c['foto']('studyo', 400)}" style="width:100%;height:100%;object-fit:cover;display:block"></div>
      <div style="position:absolute;left:300px;right:300px;top:56px">{head(K, c['i'], c['site'], c['T'], align="center")}
        <p style="margin-top:14px;font-size:19px;line-height:1.45;color:#3b3d42;text-align:center">QR'ı okutan
          müşteri bu sayfayı açar: ara, WhatsApp, Instagram, konum, yorum, IBAN.</p></div>
      {cols}
      <p style="position:absolute;right:64px;top:268px;font-size:15px;color:#6b6e74">{NOT}</p></div>"""


def l_akis(K, c):
    """4 · isimlikten siteye: büyük isimlik fotoğrafı, "QR'ı okut" oku, telefon."""
    return f"""<div style="position:relative;width:1200px;height:1200px;background:{K.PAPER};overflow:hidden">
      <div style="position:absolute;left:64px;top:60px;width:600px">{head(K, c['i'], c['site'], c['T'])}</div>
      <div style="position:absolute;left:64px;top:300px;width:540px;height:540px;border-radius:32px;overflow:hidden;
        box-shadow:0 24px 50px rgba(18,19,22,.16)">
        <img src="{c['foto']('studyo', 700)}" style="width:100%;height:100%;object-fit:cover;display:block"></div>
      <div style="position:absolute;left:560px;top:520px;display:flex;flex-direction:column;align-items:center;gap:10px">
        <span style="font-size:17px;font-weight:700;letter-spacing:.14em;color:{K.ORANGE}">QR'I OKUT</span>
        <span style="display:grid;place-items:center;width:96px;height:96px;border-radius:50%;background:{K.ORANGE};
          color:#fff;font-size:48px;font-weight:700;box-shadow:0 0 0 10px {K.PAPER}">→</span></div>
      <div style="position:absolute;left:760px;top:150px">{phone(c['ust'], 340, c['bg'])}</div>
      <div style="position:absolute;left:64px;top:890px;width:640px;display:flex;flex-wrap:wrap;gap:8px">
        {chips(K, size=18)}</div>
      <div style="position:absolute;left:64px;bottom:48px">{K.logo("acik", 230, 46)}</div>
      <p style="position:absolute;right:64px;bottom:58px;font-size:17px;color:#8b8e94">{NOT}</p></div>"""


def l_bolunmus(K, c):
    """5 · ikiye bölünmüş: solda koyu zeminde isimlik, sağda üst üste iki telefon."""
    return f"""<div style="position:relative;width:1200px;height:1200px;background:{K.PAPER};overflow:hidden">
      <div style="position:absolute;left:0;top:0;width:560px;height:1200px;background:{K.INK};overflow:hidden">
        <div style="position:absolute;left:56px;top:60px;width:460px">{head(K, c['i'], c['site'], c['T'], True)}</div>
        <img src="{c['foto']('masa', 620)}" style="position:absolute;left:-10px;top:330px;width:580px;height:580px;
          display:block;-webkit-mask-image:radial-gradient(closest-side,#000 72%,transparent 100%)">
        <p style="position:absolute;left:56px;top:930px;width:440px;font-size:21px;line-height:1.45;
          color:rgba(244,241,234,.8)">İsimlik ve sitesi birlikte hazırlanır; QR doğrudan bu sayfayı açar.</p>
        <div style="position:absolute;left:56px;bottom:48px">{K.logo("koyu", 230, 46)}</div></div>
      <div style="position:absolute;left:612px;top:96px">{phone(c['ust'], 270, c['bg'])}</div>
      <div style="position:absolute;left:880px;top:330px">{phone(c['alt'], 270, c['bg'])}</div>
      <p style="position:absolute;right:56px;bottom:40px;font-size:15px;color:#8b8e94">{NOT}</p></div>"""


LAYOUTS = (l_iki, l_tek, l_uc, l_akis, l_bolunmus)


def visual(P, i, key, T, isim, shots, site):
    import boyde_katalog as K
    import boyde_marka as BM

    def foto(view, w):
        path = os.path.join(K.FOTO, f"{isim}_{view}.jpg")
        return K.uri(path, w) if os.path.exists(path) else K.duz(isim, w)

    c = dict(zip(("ust", "orta", "alt"), (K.uri(s, 700) for s in shots)), i=i, site=site, T=T, foto=foto,
             bg=bg_of(shots[0]), BM=BM)
    path = os.path.join(SHOP, f"{i:02d}_{key}_{T.SLUG}.jpg")
    K.sq(P, LAYOUTS[(i - 1) % len(LAYOUTS)](K, c), path)
    return path


def main():
    import boyde_marka as BM
    shutil.rmtree(SHOP, ignore_errors=True)
    os.makedirs(SHOP)
    done = []
    for key, n, isim, mark, data in ORNEKLER:
        folder = os.path.join(OUT, key)
        os.makedirs(folder, exist_ok=True)
        svg_of(mark(), os.path.join(folder, "logo", "isaret.svg"))
        d = dict(ORTAK, **data, isaret="logo/isaret.svg")
        with open(os.path.join(folder, "bilgiler.json"), "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
            f.write("\n")
        with tempfile.TemporaryDirectory() as tmp:
            site, T, _ = SS.build(folder, n, out=tmp, previews=False, gif=False, record=False)
            shots = capture(os.path.join(tmp, "site"))
        paths = []
        for k, s in zip(("ust", "orta", "alt"), shots):
            p = os.path.join(folder, f"ekran_{k}.png")
            s.save(p, optimize=True)
            paths.append(p)
        done.append((key, T, isim, paths, site))
    with BM.painter() as P:
        for i, (key, T, isim, paths, site) in enumerate(done, 1):
            print(os.path.relpath(visual(P, i, key, T, isim, paths, site), U.A.ROOT), flush=True)


if __name__ == "__main__":
    main()
