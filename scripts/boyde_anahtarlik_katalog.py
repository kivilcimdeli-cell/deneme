"""BOYDE LABS – toptan anahtarlık kataloğu (A4 PDF; scripts/boyde_anahtarlik_toptan.py --katalog ile çağrılır).

Sayfalar: kapak (toptan parti fotoğrafı), nasıl (özellikler, sipariş adımları, beş model halkalarıyla), üç model
sayfası (her modelde arkalı önlü ve halkalı fotoğraf, ölçü, renkler), teklif. Görsel dil ürün kataloğuyla aynı
(boyde_katalog: logo, renkler, yazı tipleri).

Çıktı : boyde_labs/anahtarlik_toptan/katalog.pdf, katalog.png (sayfaların önizlemesi)
"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_anahtarlik_toptan as T  # noqa: E402
import boyde_katalog as K  # noqa: E402
import boyde_marka as BM  # noqa: E402

INK, PAPER, ORANGE, SAND, GRAY = K.INK, K.PAPER, K.ORANGE, K.SAND, K.GRAY
W, H = K.W, K.H
OZELLIK = [("Ön yüz kabartma", "Logonuz ve yazınız 0,8 mm kabartma, renkli; elle hissedilir."),
           ("Arka yüz düz yazı", "Slogan, telefon ya da web adresi yüzeyle aynı hizada; boya değil, baskının "
                                 "kendisi: silinmez."),
           ("Standart biçimler", "Dikdörtgen, kare, dikey etiket, bar, kesik köşe; ölçü ve renkler sizden."),
           ("Sağlam gövde", "3,2 mm PLA gövde, pahlı kenarlar; delik çevresinde kalın et payı."),
           ("Halkalı ya da halkasız", "Çelik anahtarlık halkası takılı ya da yalnız anahtarlık.")]
ADIM = [("01", "Logonuzu gönderin", "Logo, renkler, adet ve arka yüz yazısı."),
        ("02", "Tasarımı hazırlıyoruz", "Ön ve arka yüzün önizlemesini gönderiyoruz."),
        ("03", "Onaylayın", "Beğendiğiniz tasarımı onaylıyorsunuz."),
        ("04", "Basıp gönderiyoruz", "Kendi atölyemizde basıp kargoya veriyoruz.")]
NOT = "Katalogdaki anahtarlıklarda kendi markamız BOYDE LABS var; sizinkiler sizin logonuz ve yazınızla basılır."


def foto(name, maxw=900):
    return K.uri(os.path.join(T.FOTO, f"{name}.jpg"), maxw)


def page(body, dark=False, no=None):
    bg = f"background:{INK};color:{PAPER}" if dark else f"background:{PAPER};color:{INK}"
    foot = (f'<p style="position:absolute;left:48px;right:48px;bottom:26px;display:flex;justify-content:space-between;'
            f'font-size:10px;letter-spacing:.2em;color:{GRAY}"><span>BOYDE LABS · TOPTAN ANAHTARLIK</span>'
            f'<span>{no:02d}</span></p>') if no else ""
    return f'<div class="pg" style="position:relative;width:{W}px;height:{H}px;{bg};padding:48px">{body}{foot}</div>'


def colours(k):
    return " · ".join(dict.fromkeys(T.NAMES[f] for _, f in k.solids()))


def model_block(k):
    w, h = k.size()
    shots = "".join(f"""<figure style="flex:1;margin:0">
      <img src="{foto(f'{k.key}_{v}', 700)}" style="width:100%;aspect-ratio:1;object-fit:cover;border-radius:14px;
        display:block">
      <figcaption style="margin-top:6px;font-size:10.5px;letter-spacing:.14em;color:{GRAY}">{c}</figcaption></figure>"""
                    for v, c in (("iki", "ÖN VE ARKA YÜZ"), ("halka", "ÇELİK HALKAYLA")))
    return f"""<div style="display:flex;align-items:center;gap:14px">
        <span class="chip code" style="background:{ORANGE};color:#fff;font-size:15px;padding:6px 12px">{k.kod}</span>
        <p class="u" style="font-size:20px">{k.ad}</p>
        <p style="margin-left:auto;font-size:12.5px;font-weight:700;color:#55575c">{w:.0f} × {h:.0f} mm · {colours(k)}</p>
      </div>
      <div style="margin-top:12px;display:flex;gap:12px">{shots}</div>
      <p style="margin-top:8px;font-size:12px;line-height:1.5;color:#3b3d42">{k.desc}</p>"""


def catalog(P):
    pages, no = [], 1
    models = [fn() for fn in T.MODELS]

    kapak = os.path.join(T.FOTO, "kapak.jpg")
    im = Image.open(kapak).convert("RGB")
    mid, edge = im.getpixel((im.width // 2, 24)), im.getpixel((8, 8))
    pages.append(page(f"""<div style="position:absolute;inset:0;background:radial-gradient(ellipse 80% 62% at 50% 46%,
        rgb{mid} 0,rgb{mid} 45%,rgb{edge} 100%)"><img src="{foto('kapak', 1100)}"
        style="position:absolute;left:0;top:46%;width:100%;transform:translateY(-52%);
        -webkit-mask-image:linear-gradient(180deg,transparent 0,#000 16%,#000 82%,transparent 100%)"></div>
      <div style="position:relative">{K.logo("acik", 260, 52)}</div>
      <div style="position:absolute;left:48px;right:48px;bottom:64px">
        <p class="k">TOPTAN KATALOG · 2026</p>
        <h1 class="u" style="margin-top:12px;font-size:50px;line-height:1.04">Toptan<br>anahtarlık</h1>
        <p style="margin-top:16px;font-size:16px;line-height:1.5;opacity:.85">Logonuzla, arkalı önlü 3D baskı: ön yüz
          kabartma, arka yüz düz yazı. Tasarımdan baskıya kendi atölyemizde.</p></div>"""))
    no += 1

    feats = "".join(f"""<div style="padding:10px 0;border-top:1px solid #ddd6ca"><p style="font-weight:700;
      font-size:14px">{a}</p><p style="margin-top:3px;font-size:12px;line-height:1.45;color:#55575c">{b}</p></div>"""
                    for a, b in OZELLIK)
    steps = "".join(f"""<div style="display:flex;gap:14px;padding:10px 0;border-top:1px solid #ddd6ca">
      <b class="u" style="color:{ORANGE};font-size:18px;width:36px">{a}</b><div><p style="font-weight:700;
      font-size:14px">{b}</p><p style="margin-top:3px;font-size:12px;color:#55575c">{c}</p></div></div>"""
                    for a, b, c in ADIM)
    pages.append(page(f"""<p class="k">ARKALI ÖNLÜ</p>
      <h2 class="u" style="margin-top:10px;font-size:28px;line-height:1.15">Önde kabartma,<br>arkada düz yazı.</h2>
      <img src="{foto('dizi', 1100)}" style="margin-top:20px;width:100%;height:300px;object-fit:cover;
        border-radius:14px;display:block">
      <div style="margin-top:18px;display:grid;grid-template-columns:1fr 1fr;gap:0 28px">
        <div>{feats}</div><div>{steps}</div></div>
      <p style="margin-top:14px;font-size:11px;color:{GRAY}">{NOT}</p>""", no=no))
    no += 1

    for chunk in (models[0:2], models[2:4], models[4:5]):
        blocks = "".join(f'<div style="margin-top:{0 if i == 0 else 26}px">{model_block(k)}</div>'
                         for i, k in enumerate(chunk))
        if len(chunk) == 1:                                  # son sayfanın boş yarısı: sizin logonuz
            blocks += f"""<div style="margin-top:26px;border-radius:18px;background:{ORANGE};color:#fff;padding:26px 28px">
              <p class="u" style="font-size:22px;line-height:1.2">Sizin logonuz,<br>sizin renkleriniz.</p>
              <p style="margin-top:10px;font-size:13px;line-height:1.55;max-width:560px">Beş biçimden birini seçin ya
                da ölçüyü söyleyin; ön yüze logonuzu kabartma, arka yüze telefonunuzu, adresinizi ya da sloganınızı
                düz yazı olarak basalım.</p></div>"""
        pages.append(page(f"""<div style="display:flex;justify-content:space-between;align-items:flex-end">
          <div><p class="k">MODELLER</p><h2 class="u" style="margin-top:8px;font-size:22px">{chunk[0].kod}{'–' +
          chunk[-1].kod if len(chunk) > 1 else ''}</h2></div>{K.logo("acik", 150, 30)}</div>
          <div style="margin-top:20px">{blocks}</div>""", no=no))
        no += 1

    pages.append(page(f"""<div style="position:absolute;inset:0;background-image:{BM.stripes_bg(PAPER, .035, 22)}"></div>
      <div style="position:relative">{K.logo("koyu", 260, 52)}</div>
      <div style="position:absolute;left:48px;right:48px;top:250px">
        <p class="k">TEKLİF</p>
        <h2 class="u" style="margin-top:12px;font-size:38px;line-height:1.1">Adet arttıkça<br>birim fiyat düşer.</h2>
        <p style="margin-top:18px;font-size:15px;line-height:1.6;color:rgba(244,241,234,.8);max-width:560px">
          Logonuzu, adedi ve arka yüz yazısını gönderin; size özel teklif ve tasarım önizlemesiyle dönelim.</p>
        <img src="{foto('k01_klasik_halka', 900)}" style="margin-top:28px;width:100%;height:330px;object-fit:cover;
          border-radius:16px;display:block">
        <div style="margin-top:28px;display:flex;justify-content:space-between;align-items:flex-end">
          <div><p class="k">WHATSAPP</p><p style="margin-top:6px;font-size:28px;font-weight:700">{K.TEL}</p></div>
          <div style="text-align:right"><p class="k">MAĞAZA</p><p style="margin-top:6px;font-size:20px;
            font-weight:700">shopier.com/boyde</p></div></div></div>""", dark=True, no=no))

    path = os.path.join(T.OUT, "katalog.pdf")
    shots = P.pdf(pages, W, H, path, css=K.CSS)
    cols, tw, th = 3, 397, 562
    rows = (len(shots) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * 16, rows * th + (rows + 1) * 16), SAND)
    for i, s in enumerate(shots):
        sheet.paste(s.resize((tw, th), Image.LANCZOS), (16 + (i % cols) * (tw + 16), 16 + (i // cols) * (th + 16)))
    sheet.save(os.path.join(T.OUT, "katalog.png"), optimize=True)
    return path, len(pages)


def main():
    with BM.painter() as P:
        path, n = catalog(P)
    print(f"{os.path.relpath(path, T.A.ROOT)}: {n} sayfa")
