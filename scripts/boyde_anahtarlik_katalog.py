"""BOYDE LABS – toptan anahtarlık kataloğu (A4 PDF; scripts/boyde_anahtarlik_toptan.py --katalog ile çağrılır).

Sayfalar: kapak (toptan parti fotoğrafı), nasıl (özellikler, sipariş adımları, beş model halkalarıyla), üç model
sayfası (her modelde arkalı önlü ve halkalı fotoğraf, ölçü, renkler), teklif. Görsel dil ürün kataloğuyla aynı
(boyde_katalog: logo, renkler, yazı tipleri).

Shopier görselleri (1200 × 1200 JPG, yükleme sırasıyla; ürün çerçevesi boyde_katalog.framed gibi):
  01 kapak · 02 beş model (dizi) · 03–07 modeller zincirli halka takımıyla · 08–12 modeller arkalı önlü ·
  13 ölçü ve özellikler (biçimler gerçek oranlarıyla, ön ve arka) · 14 nasıl sipariş verilir

Çıktı : boyde_labs/anahtarlik_toptan/katalog.pdf, katalog.png (sayfaların önizlemesi)
        boyde_labs/anahtarlik_toptan/shopier/*.jpg
"""
import os
import shutil
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
           ("Zincirli halka takımı", "Çelik halka, kısa zincir ve ara halka takılı; ya da yalnız anahtarlık.")]
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
                    for v, c in (("iki", "ÖN VE ARKA YÜZ"), ("halka", "ZİNCİRLİ HALKA TAKIMIYLA")))
    return f"""<div style="display:flex;align-items:center;gap:14px">
        <span class="chip code" style="background:{ORANGE};color:#fff;font-size:15px;padding:6px 12px">{k.kod}</span>
        <p class="u" style="font-size:20px">{k.ad}</p>
        <p style="margin-left:auto;font-size:12.5px;font-weight:700;color:#55575c">{w:.0f} × {h:.0f} mm · {colours(k)}</p>
      </div>
      <div style="margin-top:12px;display:flex;gap:12px">{shots}</div>
      <p style="margin-top:8px;font-size:12px;line-height:1.5;color:#3b3d42">{k.desc}</p>"""


def scale(models, px_mm=2.4):
    """Beş biçim gerçek oranlarıyla (ön yüz), altlarında kod ve ölçü."""
    cells = []
    for k in models:
        w, h = k.size()
        img = K.uri(os.path.join(T.SRC, f"{k.key}_on.png"), 600, "PNG")
        cells.append(f"""<div style="display:flex;flex-direction:column;align-items:center;gap:8px">
          <img src="{img}" style="width:{w * px_mm:.0f}px;height:{h * px_mm:.0f}px;display:block;
            filter:drop-shadow(0 6px 10px rgba(0,0,0,.18))">
          <p style="font-size:11px;font-weight:700;color:#55575c">{k.kod} · {w:.0f} × {h:.0f} mm</p></div>""")
    return f"""<div style="margin-top:26px"><p class="k">BİÇİMLER · GERÇEK ORANLARIYLA</p>
      <div style="margin-top:16px;display:flex;justify-content:space-between;align-items:flex-end">{''.join(cells)}
      </div></div>"""


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
      <img src="{foto('dizi', 1100)}" style="margin-top:20px;width:100%;height:390px;object-fit:cover;
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
                düz yazı olarak basalım.</p></div>{scale(models)}"""
        pages.append(page(f"""<div style="display:flex;justify-content:space-between;align-items:flex-end">
          <div><p class="k">MODELLER</p><h2 class="u" style="margin-top:8px;font-size:22px">{chunk[0].kod}{'–' +
          chunk[-1].kod if len(chunk) > 1 else ''}</h2></div>{K.logo("acik", 150, 30)}</div>
          <div style="margin-top:20px">{blocks}</div>""", no=no))
        no += 1

    pages.append(page(f"""<div style="position:absolute;inset:0;background-image:{BM.stripes_bg(PAPER, .035, 22)}"></div>
      <div style="position:relative">{K.logo("koyu", 260, 52)}</div>
      <div style="position:absolute;left:48px;right:48px;top:170px">
        <p class="k">TEKLİF</p>
        <h2 class="u" style="margin-top:12px;font-size:38px;line-height:1.1">Adet arttıkça<br>birim fiyat düşer.</h2>
        <p style="margin-top:18px;font-size:15px;line-height:1.6;color:rgba(244,241,234,.8);max-width:560px">
          Logonuzu, adedi ve arka yüz yazısını gönderin; size özel teklif ve tasarım önizlemesiyle dönelim.</p>
        <div style="margin-top:28px;display:flex;gap:14px">
          <img src="{foto('k02_dikey_halka', 700)}" style="flex:1;min-width:0;aspect-ratio:1;object-fit:cover;
            border-radius:16px;display:block">
          <img src="{foto('k03_kare_iki', 700)}" style="flex:1;min-width:0;aspect-ratio:1;object-fit:cover;
            border-radius:16px;display:block"></div>
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


# ---------------------------------------------------------------- Shopier (1200 × 1200)

def framed(P, photo, chip, t1, t2, path, etiket="TOPTAN ANAHTARLIK"):
    """BOYDE çerçevesi: fotoğraf tam kadraj; sol üstte logo, sağ üstte etiket; altta buzlu cam şerit (turuncu kod,
    başlık, alt satır, "tasarım ve 3D baskı BOYDE"). Renkler fotoğrafın fonuna göre."""
    acik = K.light(os.path.join(T.FOTO, f"{photo}.jpg"))
    fg, sub = (INK, "#55575c") if acik else (PAPER, "rgba(244,241,234,.7)")
    glass, edge = ("rgba(255,255,255,.62)", "rgba(18,19,22,.08)") if acik else \
        ("rgba(18,19,22,.55)", "rgba(244,241,234,.12)")
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;overflow:hidden">
      <img src="{foto(photo, 1200)}" style="position:absolute;inset:0;width:100%;height:100%;display:block">
      <div style="position:absolute;left:44px;top:40px">{K.logo("acik" if acik else "koyu", 260, 58)}</div>
      <span style="position:absolute;right:44px;top:44px;font-size:15px;font-weight:700;letter-spacing:.2em;
        color:{fg};opacity:.75">{etiket}</span>
      <div style="position:absolute;left:28px;right:28px;bottom:28px;display:flex;align-items:center;gap:22px;
        padding:18px 26px 18px 18px;border-radius:26px;background:{glass};backdrop-filter:blur(22px) saturate(1.3);
        box-shadow:inset 0 0 0 1.5px {edge};color:{fg}">
        <span class="code" style="flex:none;display:grid;place-items:center;width:84px;height:84px;border-radius:18px;
          background:{ORANGE};color:#fff;font-size:26px">{chip}</span>
        <div style="flex:1;min-width:0">
          <p class="u" style="font-size:27px;line-height:1.15;white-space:nowrap;overflow:hidden;
            text-overflow:ellipsis">{t1}</p>
          <p style="margin-top:7px;font-size:18px;color:{sub};white-space:nowrap;overflow:hidden;
            text-overflow:ellipsis">{t2}</p></div>
        <p style="flex:none;text-align:right;font-size:14px;font-weight:700;letter-spacing:.14em;line-height:1.5;
          color:{sub}">TASARIM VE<br>3D BASKI <b style="color:{ORANGE}">BOYDE</b></p></div></div>""", path)


def shopier(P):
    out = os.path.join(T.OUT, "shopier")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    name = lambda i, s: os.path.join(out, f"{i:02d}_{s}.jpg")              # noqa: E731
    models = [fn() for fn in T.MODELS]

    # 01 kapak: toptan parti, beyaz fonda koyu yazı
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:#fff">
      <img src="{foto('kapak', 1200)}" style="width:1200px;height:1200px;display:block">
      <div style="position:absolute;left:64px;top:56px">{K.logo("acik", 330, 66)}</div>
      <div style="position:absolute;left:64px;right:64px;bottom:64px;color:{INK}">
        <p class="k">TOPTAN · LOGONUZLA · ARKALI ÖNLÜ</p>
        <h1 class="u" style="margin-top:14px;font-size:76px;line-height:1.02;letter-spacing:-.02em">Toptan<br>
          anahtarlık</h1>
        <p style="margin-top:18px;font-size:30px;line-height:1.35;color:#3b3d42">Ön yüz kabartma, arka yüz düz yazı;
          zincirli halka takımıyla.</p></div></div>""", name(1, "kapak"))

    # 02 beş model: yatay fotoğraf kareye, üstü ve altı fona karışır
    im = Image.open(os.path.join(T.FOTO, "dizi.jpg")).convert("RGB")
    mid, edge = im.getpixel((im.width // 2, 12)), im.getpixel((6, 6))
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;overflow:hidden;
      background:radial-gradient(ellipse 85% 60% at 50% 46%,rgb{mid} 0,rgb{mid} 40%,rgb{edge} 100%)">
      <img src="{foto('dizi', 1200)}" style="position:absolute;left:0;top:50%;width:1200px;transform:translateY(-44%);
        -webkit-mask-image:linear-gradient(180deg,transparent 0,#000 14%,#000 84%,transparent 100%)">
      <div style="position:absolute;left:64px;top:56px">{K.logo("acik", 260, 52)}</div>
      <div style="position:absolute;left:64px;right:64px;top:150px;color:{INK}">
        <p class="k">5 STANDART BİÇİM</p>
        <h2 class="u" style="margin-top:12px;font-size:46px;line-height:1.08">Hepsi logonuzla,<br>arkalı önlü.</h2></div>
      <div style="position:absolute;left:64px;right:64px;bottom:60px;display:flex;flex-wrap:wrap;gap:10px">
        {''.join(f'<span class="chip" style="background:#fff;color:{INK};font-size:19px;padding:8px 14px;box-shadow:0 0 0 1.5px rgba(18,19,22,.08)"><b style="color:{ORANGE}">{k.kod}</b>&nbsp;{k.ad}</span>' for k in models)}
      </div></div>""", name(2, "bes_model"))

    # 03–07 halka takımıyla, 08–12 arkalı önlü
    for i, k in enumerate(models):
        w, h = k.size()
        framed(P, f"{k.key}_halka", k.kod, f"{k.ad} · zincirli halka takımıyla",
               f"{w:.0f} × {h:.0f} mm · solda ön yüz, sağda arka yüz", name(3 + i, f"{k.kod}_{k.key[4:]}_halka"))
    for i, k in enumerate(models):
        w, h = k.size()
        framed(P, f"{k.key}_iki", k.kod, f"{k.ad} · ön yüz kabartma, arka düz yazı",
               f"{w:.0f} × {h:.0f} mm · {colours(k)}", name(8 + i, f"{k.kod}_{k.key[4:]}_arkali_onlu"))

    # 13 ölçü ve özellikler: biçimler gerçek oranlarıyla, ön ve arka
    px = 3.7
    cells = ""
    for k in models:
        w, h = k.size()
        imgs = "".join(f"""<img src="{K.uri(os.path.join(T.SRC, f'{k.key}_{v}.png'), 600, 'PNG')}"
          style="width:{w * px:.0f}px;height:{h * px:.0f}px;display:block;
          filter:drop-shadow(0 6px 10px rgba(0,0,0,.18))">""" for v in ("on", "arka"))
        cells += f"""<div style="display:flex;flex-direction:column;align-items:center;gap:12px">{imgs}
          <p style="font-size:17px;font-weight:700;color:#55575c">{k.kod} · {w:.0f} × {h:.0f} mm</p></div>"""
    feats = "".join(f"""<li style="display:flex;gap:12px"><b style="color:{ORANGE}">—</b><span><b>{a}.</b> {b}</span></li>"""
                    for a, b in OZELLIK)
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:{PAPER};padding:60px 56px;
      color:{INK}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <div><p class="k">ÖLÇÜ VE ÖZELLİKLER</p>
        <h2 class="u" style="margin-top:12px;font-size:44px;line-height:1.08">Önde kabartma,<br>arkada düz yazı.</h2></div>
        {K.logo("acik", 220, 44)}</div>
      <div style="margin-top:44px;display:flex;justify-content:space-between;align-items:flex-end">{cells}</div>
      <p style="margin-top:10px;font-size:15px;color:{GRAY}">Üst sıra ön yüz, alt sıra arka yüz; gerçek oranlarıyla.</p>
      <ul style="margin-top:40px;list-style:none;display:grid;gap:16px;font-size:24px;line-height:1.35">{feats}</ul>
      </div>""", name(13, "olcu_ozellik"))

    # 14 nasıl sipariş verilir
    rows = "".join(f"""<div style="display:flex;gap:28px;padding:18px 0;border-top:2px solid rgba(244,241,234,.14)">
      <b class="u" style="font-size:44px;color:{ORANGE};width:90px">{a}</b><div><p style="font-size:32px;
      font-weight:700">{b}</p><p style="margin-top:8px;font-size:23px;color:rgba(244,241,234,.72)">{c}</p></div>
      </div>""" for a, b, c in ADIM)
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:{INK};color:{PAPER};padding:64px;
      background-image:{BM.stripes_bg(PAPER, .035, 30)}">
      <p class="k">NASIL SİPARİŞ VERİLİR</p>
      <h2 class="u" style="margin-top:12px;font-size:48px;line-height:1.1">Logonuzu gönderin,<br>gerisini biz yapalım.</h2>
      <p style="margin-top:20px;font-size:25px;color:rgba(244,241,234,.8)">Adet arttıkça birim fiyat düşer.</p>
      <div style="margin-top:30px">{rows}</div>
      <img src="{foto('kapak', 1200)}" style="margin-top:14px;width:100%;height:190px;object-fit:cover;
        object-position:50% 52%;border-radius:22px;display:block">
      <div style="position:absolute;left:64px;bottom:50px">{K.logo("koyu", 300, 60)}</div>
      <p style="position:absolute;right:64px;bottom:60px;font-size:26px;font-weight:700">{K.TEL}</p></div>""",
         name(14, "nasil_siparis"))
    return out


def main(which="hepsi"):
    with BM.painter() as P:
        if which in ("hepsi", "katalog"):
            path, n = catalog(P)
            print(f"{os.path.relpath(path, T.A.ROOT)}: {n} sayfa")
        if which in ("hepsi", "shopier"):
            out = shopier(P)
            print(f"{os.path.relpath(out, T.A.ROOT)}: {len(os.listdir(out))} görsel")
