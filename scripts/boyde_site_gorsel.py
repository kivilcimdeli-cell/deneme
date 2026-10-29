"""BOYDE LABS – örnek site görselleri (Shopier ve katalog): isimlikteki QR'ın açtığı sayfa, üç ayrı şablonla.

Kullanıcı isteği: "bu görsellere ek olarak 3 adet birbirinden farklı internet sayfası görseli; örnek niyetine,
Shopier'de kullanırız".

Üç uydurma işletme, isimlik örnekleriyle aynı (scripts/boyde_sektor.py), her biri başka şablonla
(scripts/sablon_site.py; lastikçi tarzı beş şablondan otomotiv süsü olmayan üçü):
  cagri  Çağrı İletişim (telefoncu)   1 · Şimşek    turkuaz, şimşek yerine telefon simgesi
  sera   Sera Kuyumculuk (kuyumcu)    4 · Kurumsal  altın, pırlanta
  mira   Mira Kuaför (kuaför)         5 · Sade      mor, makas çizilerek gelir
Örnek oldukları için şablon sırasına (site_sablonlari/sira.json) yazılmaz. Telefon BOYDE'nin (0546 475 45 08),
IBAN örnek; sayfadaki banka karekodu da okunmaz (boyde_urunler'in örnek modu).

Görsel (1200 × 1200): iki telefonda sayfa (ilk ekran ve aşağısı: bağlantılar, ödeme), yanında isimliğin fotoğrafı.
Çıktı : boyde_labs/urunler/shopier/site_ornekleri/0N_<işletme>.jpg
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
    """Telefon ekranı (390 × 844, 2×, hareketsiz son hâl): ilk ekran ve aşağısı."""
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
        pg.evaluate(f"window.scrollTo(0, {max(0, min(h - 844, 760))})")
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


def visual(P, i, key, T, isim, shots, site):
    import boyde_katalog as K
    ust, alt = (K.uri(s, 700) for s in shots)
    foto = os.path.join(K.FOTO, f"{isim}_studyo.jpg")
    img = K.uri(foto, 520) if os.path.exists(foto) else K.duz(isim, 520)
    chips = "".join(f'<span class="chip" style="background:#fff;color:{K.INK};font-size:19px;padding:8px 14px">{c}</span>'
                    for c in ("Ara", "WhatsApp", "Instagram", "Konum", "Google yorum", "IBAN", "Rehbere kaydet"))
    body = f"""<div style="position:relative;width:1200px;height:1200px;background:{K.PAPER};overflow:hidden">
      <div style="position:absolute;left:64px;top:60px;width:480px">
        <p class="k">ÖRNEK SİTE · {i}/3</p>
        <h1 class="u" style="margin-top:14px;font-size:46px;line-height:1.08;color:{K.INK}">{site.isletme}</h1>
        <p style="margin-top:12px;font-size:22px;color:#55575c">Şablon: <b style="color:{K.INK}">{T.AD}</b></p>
        <p style="margin-top:24px;font-size:24px;line-height:1.45;color:#3b3d42">İsimlikteki QR'ı okutan müşteri bu
          sayfayı açar. Her şey tek dokunuşla:</p>
        <div style="margin-top:16px;display:flex;flex-wrap:wrap;gap:8px">{chips}</div></div>
      <div style="position:absolute;left:64px;bottom:150px;width:430px;border-radius:24px;overflow:hidden;
        background:#fff;box-shadow:0 20px 40px rgba(18,19,22,.12)">
        <img src="{img}" style="width:430px;height:300px;object-fit:cover;display:block"></div>
      <p style="position:absolute;left:64px;bottom:108px;font-size:19px;color:#55575c">İsimlik ve sitesi birlikte
        hazırlanır.</p>
      <div style="position:absolute;left:520px;top:300px">{phone(ust, 300, bg_of(shots[0]))}</div>
      <div style="position:absolute;left:846px;top:236px">{phone(alt, 300, bg_of(shots[0]))}</div>
      <div style="position:absolute;left:64px;bottom:40px">{K.logo("acik", 230, 46)}</div>
      <p style="position:absolute;right:64px;bottom:50px;font-size:17px;color:#8b8e94">Örnek işletme; telefon
        BOYDE LABS'in, IBAN ve QR örnektir.</p></div>"""
    path = os.path.join(SHOP, f"{i:02d}_{key}_{T.SLUG}.jpg")
    K.sq(P, body, path)
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
        for k, s in zip(("ust", "alt"), shots):
            p = os.path.join(folder, f"ekran_{k}.png")
            s.save(p, optimize=True)
            paths.append(p)
        done.append((key, T, isim, paths, site))
    with BM.painter() as P:
        for i, (key, T, isim, paths, site) in enumerate(done, 1):
            print(os.path.relpath(visual(P, i, key, T, isim, paths, site), U.A.ROOT), flush=True)


if __name__ == "__main__":
    main()
