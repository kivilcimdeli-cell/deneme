"""BOYDE LABS – ürün kataloğu (PDF) ve Shopier ürün görselleri, iki kategori: 9 × 12 cm ve 10 × 20 cm isimlik.

Girdi : scripts/boyde_urunler.py (ürünler, kategoriler), boyde_labs/urunler/fotograf/ (scripts/boyde_urun_foto.py),
        boyde_labs/urunler/kaynak/<ürün>_duz.png (düz görünüş). Marka: scripts/boyde_marka.py (logo 3a, renkler,
        yazı tipleri).
Çıktı : boyde_labs/urunler/katalog.pdf (A4), katalog.png (sayfaların önizlemesi)
        boyde_labs/urunler/shopier/<kategori>/ (1200 × 1200 JPG): 10 model, yükleme sırasıyla 01_M01_… 10_M10_…,
          BOYDE çerçevesinde ("BOYDE ürünü olarak pazarlamamız gerekiyor; çerçeve ekler misin")
        boyde_labs/urunler/cerceveli/<kategori>/: her ürünün üç fotoğrafı (stüdyo, karşıdan, masa) çerçevede
          ("10 adet küçük, 10 adet büyük boy"); ek/: kapak, modeller (hepsi bir arada), olcu_ozellik, nasil_calisir

Model kodları kategoride sırayla: önce müşterilerin bastırdıkları, sonra farklı sektörlere örnekler, en son
önerilerden beğenilenler. Örneklerdeki işletme ve kişi adları, telefon ve QR'lar örnektir (QR'lar okunmaz).

Kullanım: python3 scripts/boyde_katalog.py
"""
import base64
import io
import os
import shutil
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_marka as BM  # noqa: E402
import boyde_urunler as U  # noqa: E402

INK, PAPER, ORANGE, SAND, GRAY, CHAR = BM.INK, BM.PAPER, BM.ORANGE, BM.SAND, BM.GRAY, BM.CHAR
OUT = U.OUT
FOTO = os.path.join(OUT, "fotograf")
LOGO = "3b"
TEL = "0546 475 45 08"
TUR = {"musteri": "Müşterimizin seçtiği", "oneri": "Müşterimize çizilen öneri", "ornek": "Örnek tasarım"}
# sipariş akışı: "10 adet örnek çalışma yapacağız; size özel 10 tasarım gönderiyoruz, en beğendiğinizi üretiyoruz"
SIPARIS = [("01", "Sipariş verin", "Shopier'dan adet seçin, ödemeyi güvenle yapın."),
           ("02", "Bilgilerinizi gönderin", "Ad, logo, renkler, telefon, Instagram, konum, IBAN."),
           ("03", "Size özel 10 tasarım", "Bilgilerinizle 10 farklı tasarım hazırlayıp gönderiyoruz."),
           ("04", "En beğendiğinizi basalım", "Seçtiğiniz tasarımı 3D basıp kargoya veriyoruz.")]
NOT_ORNEK = "Örneklerdeki işletme adları, telefon ve QR'lar örnektir; tasarım sizin bilgilerinizle hazırlanır."


def models(cat):
    """Kategorinin modelleri, kodlarıyla: [(kod, ürün)]."""
    us = [u for u in U.URUNLER if u.kat == cat]
    order = {"musteri": 0, "ornek": 1, "oneri": 2}
    us = sorted(us, key=lambda u: order[u.tur])                  # sıralama kararlı: aynı türde liste sırası
    return [(f"M{i:02d}", u) for i, u in enumerate(us, 1)]


def uri(path, maxw=None, fmt="JPEG", crop=None):
    im = Image.open(path)
    if crop:
        im = im.crop(crop)
    if maxw and im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    if fmt == "JPEG":
        im.convert("RGB").save(buf, "JPEG", quality=86)
    else:
        im.save(buf, "PNG", optimize=True)
    return f"data:image/{fmt.lower()};base64," + base64.b64encode(buf.getvalue()).decode()


def foto(key, view="studyo", maxw=900):
    return uri(os.path.join(FOTO, f"{key}_{view}.jpg"), maxw)


def light(path):
    """Fotoğrafın fonu açık mı (koyu isimlikler beyaz fonda, beyazlar logodaki siyahta): üst şeridin parlaklığı."""
    im = Image.open(path).convert("L")
    return sum(im.crop((0, 0, im.width, im.height // 10)).getdata()) / (im.width * (im.height // 10)) > 128


def duz(key, maxw=900):
    return uri(os.path.join(U.SRC, f"{key}_duz.png"), maxw, "PNG")


def logo(theme, w, h, kind="yatay"):
    return BM.fitted(LOGO, kind, theme, w, h)


def caption(u):
    who = u.musteri if u.tur != "ornek" else f"{u.musteri} (örnek)"
    return f"{u.sektor} · {u.ad}", who


CSS = f"""
body{{color:{INK}}}
.k{{font-size:13px;font-weight:700;letter-spacing:.22em;color:{ORANGE}}}
.chip{{display:inline-flex;align-items:center;gap:8px;padding:6px 12px;border-radius:99px;font-weight:700}}
.code{{font-family:Unbounded;font-weight:700}}
"""


# ---------------------------------------------------------------- Shopier (1200 × 1200)

def sq(P, body, path, css=""):
    tmp = path[:-4] + ".png"
    P.png(body, 1200, 1200, tmp, css=CSS + css)
    Image.open(tmp).convert("RGB").save(path, "JPEG", quality=90)
    os.remove(tmp)


def shopier(P, cat):
    K = U.KATEGORI[cat]
    ms = models(cat)
    out = os.path.join(OUT, "shopier", cat)
    ek = os.path.join(out, "ek")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(ek)

    def name(s):
        return os.path.join(ek, f"{s}.jpg")

    # kapak: beyaz fonda koyu yazı, koyu fonda açık yazı (fonu karartan gölge yalnız koyuda)
    kapak = os.path.join(FOTO, f"kapak_{cat}.jpg")
    acik = light(kapak)
    shade = "" if acik else """<div style="position:absolute;inset:0;background:linear-gradient(180deg,
      rgba(18,19,22,.55) 0,rgba(18,19,22,0) 22%,rgba(18,19,22,0) 56%,rgba(18,19,22,.92) 100%)"></div>"""
    sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:#000">
      <img src="{uri(kapak, 1200)}" style="width:1200px;height:1200px;display:block">{shade}
      <div style="position:absolute;left:64px;top:56px">{logo("acik" if acik else "koyu", 330, 66)}</div>
      <div style="position:absolute;left:64px;right:64px;bottom:64px;color:{INK if acik else PAPER}">
        <p class="k">{K['olcu'].upper()} · SİZE ÖZEL 10 TASARIM</p>
        <h1 class="u" style="margin-top:14px;font-size:76px;line-height:1.02;letter-spacing:-.02em">{K['ad']}</h1>
        <p style="margin-top:18px;font-size:30px;line-height:1.35;color:{'#3b3d42' if acik else 'rgba(244,241,234,.86)'}">
          {K['kisa']} Size özel 10 tasarım hazırlıyoruz, en beğendiğinizi basıyoruz.</p></div></div>""",
       name("kapak"))

    # modeller: 4 × 3 ızgara, 10 model ve iki kutu
    cells = "".join(f"""<div style="position:relative;border-radius:16px;overflow:hidden;background:#fff">
      <img src="{foto(u.key, maxw=420)}" style="width:100%;aspect-ratio:1;object-fit:cover;display:block">
      <span class="chip code" style="position:absolute;left:10px;top:10px;background:{INK};color:{PAPER};
        font-size:15px;padding:5px 10px">{c}</span>
      <span class="chip" style="position:absolute;left:10px;bottom:10px;max-width:calc(100% - 20px);font-size:14px;
        padding:4px 10px;background:rgba(244,241,234,.92);color:{INK}">{u.sektor}</span></div>""" for c, u in ms)
    cells += f"""<div style="border-radius:16px;background:{ORANGE};color:#fff;padding:18px;display:flex;
      flex-direction:column;justify-content:flex-end"><p class="u" style="font-size:20px;line-height:1.15">Size
      özel 10 tasarım</p><p style="margin-top:6px;font-size:15px;line-height:1.35">Sizin adınız, logonuz ve
      renklerinizle. En beğendiğinizi basıyoruz.</p></div>
      <div style="border-radius:16px;background:{INK};color:{PAPER};padding:18px;display:flex;flex-direction:column;
      justify-content:space-between">{logo("koyu", 200, 40)}<p style="font-size:19px;font-weight:700">{TEL}</p></div>"""
    sq(P, f"""<div style="width:1200px;height:1200px;background:{PAPER};padding:56px 60px">
      <div style="display:flex;justify-content:space-between;align-items:flex-end">
        <div><p class="k">{K['olcu'].upper()} · {K['ad'].upper()}</p>
        <h2 class="u" style="margin-top:10px;font-size:42px">Örnek çalışmalar</h2></div>
        {logo("acik", 250, 50)}</div>
      <div style="margin-top:44px;display:grid;grid-template-columns:repeat(4,1fr);gap:16px">{cells}</div>
      <p style="position:absolute;left:60px;right:60px;bottom:48px;font-size:19px;line-height:1.45;color:#55575c">
        Siparişten sonra size özel 10 tasarım hazırlıyoruz; en beğendiğinizi basıyoruz. {NOT_ORNEK}</p></div>""",
       name("modeller"))

    # ölçü ve özellikler
    ex = ms[0][1].key if cat == "10x20" else "telefon"
    w_mm, h_mm = (200, 100) if cat == "10x20" else (120, 90)
    iw = 760 if cat == "10x20" else 600
    feats = "".join(f'<li style="display:flex;gap:14px;align-items:flex-start"><b style="color:{ORANGE}">—</b>'
                    f"<span>{f}</span></li>" for f in K["ozellik"])
    sq(P, f"""<div style="width:1200px;height:1200px;background:{PAPER};padding:64px">
      <p class="k">ÖLÇÜ VE ÖZELLİKLER</p>
      <h2 class="u" style="margin-top:12px;font-size:56px">{K['olcu']}</h2>
      <div style="margin-top:40px;display:flex;justify-content:center">
        <div style="position:relative;width:{iw}px">
          <img src="{duz(ex)}" style="width:{iw}px;display:block;filter:drop-shadow(0 18px 28px rgba(0,0,0,.18))">
          <div style="position:absolute;left:0;right:0;top:-30px;border-top:2px solid {INK}"></div>
          <span style="position:absolute;left:50%;top:-50px;transform:translate(-50%,-50%);background:{PAPER};
            padding:0 12px;font-weight:700;font-size:24px">{w_mm} mm</span>
          <div style="position:absolute;top:0;bottom:0;right:-30px;border-right:2px solid {INK}"></div>
          <span style="position:absolute;right:-48px;top:50%;transform:translate(50%,-50%) rotate(90deg);
            background:{PAPER};padding:0 12px;font-weight:700;font-size:24px">{h_mm} mm</span></div></div>
      <ul style="margin-top:56px;list-style:none;display:grid;gap:14px;font-size:27px;line-height:1.35">{feats}</ul>
      <div style="position:absolute;right:64px;bottom:56px">{logo("acik", 260, 52)}</div></div>""",
       name("olcu_ozellik"))

    # nasıl çalışır
    steps = SIPARIS
    rows = "".join(f"""<div style="display:flex;gap:28px;padding:20px 0;border-top:2px solid rgba(244,241,234,.14)">
      <b class="u" style="font-size:44px;color:{ORANGE};width:90px">{a}</b><div><p style="font-size:34px;
      font-weight:700">{b}</p><p style="margin-top:8px;font-size:24px;color:rgba(244,241,234,.72)">{c}</p></div>
      </div>""" for a, b, c in steps)
    links = "Ara · WhatsApp · Instagram · Konum · Google yorum · IBAN" if cat == "9x12" else \
        "Telefon · WhatsApp · E-posta · Adres · Rehbere kaydet"
    sq(P, f"""<div style="width:1200px;height:1200px;background:{INK};color:{PAPER};padding:64px;
      background-image:{BM.stripes_bg(PAPER, .035, 30)}">
      <p class="k">NASIL ÇALIŞIR</p>
      <h2 class="u" style="margin-top:12px;font-size:50px;line-height:1.1">Okutan müşteriniz<br>sizin sayfanızı açar.</h2>
      <p style="margin-top:22px;font-size:26px;color:rgba(244,241,234,.8)">{links}: hepsi tek QR'da.</p>
      <div style="margin-top:34px">{rows}</div>
      <img src="{foto('musavir' if cat == '10x20' else 'telefon', 'masa', 1100)}" style="margin-top:18px;width:100%;
        height:170px;object-fit:cover;border-radius:22px;display:block">
      <div style="position:absolute;left:64px;bottom:50px">{logo("koyu", 300, 60)}</div>
      <p style="position:absolute;right:64px;bottom:60px;font-size:26px;font-weight:700">{TEL}</p></div>""",
       name("nasil_calisir"))

    # her model: BOYDE çerçevesinde
    for c, u in ms:
        framed(P, cat, c, u, "studyo", os.path.join(out, f"{int(c[1:]):02d}_{c}_{u.key}.jpg"))
    return out


def framed(P, cat, c, u, view, path):
    """BOYDE çerçevesi (1200 × 1200; "daha modern"): fotoğraf tam kadraj; sol üstte logo, sağ üstte ölçü; altta buzlu
    cam şerit: turuncu model kodu, ad, kategori ve kimin için, "tasarım ve 3D baskı BOYDE". Renkler fotoğrafın fonuna
    göre: beyaz fonda koyu yazı, siyah fonda açık."""
    K = U.KATEGORI[cat]
    t1, _ = caption(u)
    who = f"{u.musteri} için ürettik" if u.tur != "ornek" else "Örnek tasarım · sizin bilgilerinizle"
    acik = light(os.path.join(FOTO, f"{u.key}_{view}.jpg"))
    fg, sub = (INK, "#55575c") if acik else (PAPER, "rgba(244,241,234,.7)")
    glass, edge = ("rgba(255,255,255,.62)", "rgba(18,19,22,.08)") if acik else \
        ("rgba(18,19,22,.55)", "rgba(244,241,234,.12)")
    sq(P, f"""<div style="position:relative;width:1200px;height:1200px;overflow:hidden">
      <img src="{foto(u.key, view, 1200)}" style="position:absolute;inset:0;width:100%;height:100%;display:block">
      <div style="position:absolute;left:44px;top:40px">{logo("acik" if acik else "koyu", 260, 58)}</div>
      <span style="position:absolute;right:44px;top:44px;font-size:15px;font-weight:700;letter-spacing:.2em;
        color:{fg};opacity:.75">{K['olcu'].upper()}</span>
      <div style="position:absolute;left:28px;right:28px;bottom:28px;display:flex;align-items:center;gap:22px;
        padding:18px 26px 18px 18px;border-radius:26px;background:{glass};backdrop-filter:blur(22px) saturate(1.3);
        box-shadow:inset 0 0 0 1.5px {edge};color:{fg}">
        <span class="code" style="flex:none;display:grid;place-items:center;width:84px;height:84px;border-radius:18px;
          background:{ORANGE};color:#fff;font-size:26px">{c}</span>
        <div style="flex:1;min-width:0">
          <p class="u" style="font-size:27px;line-height:1.15;white-space:nowrap;overflow:hidden;
            text-overflow:ellipsis">{t1}</p>
          <p style="margin-top:7px;font-size:18px;color:{sub};white-space:nowrap;overflow:hidden;
            text-overflow:ellipsis">{K['ad']} · {who}</p></div>
        <p style="flex:none;text-align:right;font-size:14px;font-weight:700;letter-spacing:.14em;line-height:1.5;
          color:{sub}">TASARIM VE<br>3D BASKI <b style="color:{ORANGE}">BOYDE</b></p></div></div>""", path)


def framed_all(P):
    """Her ürünün üç fotoğrafı (stüdyo, karşıdan, masa) BOYDE çerçevesinde: cerceveli/<kategori>/."""
    for cat in U.KATEGORI:
        out = os.path.join(OUT, "cerceveli", cat)
        shutil.rmtree(out, ignore_errors=True)
        os.makedirs(out)
        for c, u in models(cat):
            for view in ("studyo", "on", "masa"):
                framed(P, cat, c, u, view, os.path.join(out, f"{c}_{u.key}_{view}.jpg"))


# ---------------------------------------------------------------- katalog (A4)

W, H = 794, 1123


def page(body, dark=False, no=None):
    bg = f"background:{INK};color:{PAPER}" if dark else f"background:{PAPER};color:{INK}"
    foot = (f'<p style="position:absolute;left:48px;right:48px;bottom:26px;display:flex;justify-content:space-between;'
            f'font-size:10px;letter-spacing:.2em;color:{GRAY}"><span>BOYDE LABS · ÜRÜN KATALOĞU</span>'
            f'<span>{no:02d}</span></p>') if no else ""
    return f'<div class="pg" style="{bg};padding:48px">{body}{foot}</div>'


def card(c, u):
    t1, t2 = caption(u)
    badge = TUR[u.tur]
    col = ORANGE if u.tur == "musteri" else GRAY
    return f"""<div style="background:#fff;border-radius:14px;overflow:hidden;display:flex;flex-direction:column">
      <img src="{foto(u.key, maxw=560)}" style="width:100%;aspect-ratio:16/10;object-fit:cover;display:block">
      <div style="padding:10px 12px 12px"><div style="display:flex;justify-content:space-between;align-items:center">
        <b class="code" style="font-size:13px">{c}</b><span style="font-size:9.5px;font-weight:700;color:{col};
        letter-spacing:.06em">{badge.upper()}</span></div>
        <p style="margin-top:5px;font-size:13px;font-weight:700">{t1}</p>
        <p style="margin-top:2px;font-size:11px;color:#55575c;white-space:nowrap;overflow:hidden;
          text-overflow:ellipsis">{t2} · {u.renk}</p></div></div>"""


SITE_YAZI = {
    "9x12": ("İSİMLİKLE GELEN SİTE", "Her isimliğe<br>işletmenize özel sayfa.",
             "QR'ı okutan müşteriniz bu sayfayı açar: ara, WhatsApp, Instagram, Google yorum, konum, rehbere kaydet ve "
             "IBAN (tek dokunuşla kopyalanır)."),
    "10x20": ("KURUMSAL İSİMLİKLE GELEN KARTVİZİT", "Her isimliğe<br>dijital kartvizit.",
              "QR'ı okutan kişi kartvizit sayfanızı açar: ara, WhatsApp, e-posta, konum ve rehbere kaydet (adınız, "
              "göreviniz, kurumunuz tek dokunuşla telefonuna eklenir)."),
}


def site_pages(cat="9x12"):
    """Örnek siteler (scripts/boyde_site_gorsel.py'nin ekran görüntüleri): beş şablon, beş telefon (3 + 2);
    10 × 20'de kişilerin dijital kartvizitleri."""
    import json
    import boyde_site_gorsel as SG
    import sablonlar
    cols = []
    for key, n, _, _, _ in SG.SETS[cat]["ornekler"]:
        shot = os.path.join(SG.OUT, key, "ekran_ust.png")
        if not os.path.exists(shot):
            return ""
        d = json.load(open(os.path.join(SG.OUT, key, "bilgiler.json"), encoding="utf-8"))
        cols.append(f"""<div style="display:flex;flex-direction:column;align-items:center;gap:12px">
          {SG.phone(uri(shot, 500, "PNG"), 132, SG.bg_of(shot))}
          <p style="font-weight:700;font-size:14px">{d['isletme']}</p>
          <p style="margin-top:-8px;font-size:11.5px;color:rgba(244,241,234,.65)">Şablon: {sablonlar.get(n).AD}</p>
          </div>""")
    k, h, txt = SITE_YAZI[cat]
    return f"""<p class="k">{k}</p>
      <h2 class="u" style="margin-top:10px;font-size:28px;line-height:1.15">{h}</h2>
      <p style="margin-top:14px;font-size:13.5px;line-height:1.6;color:rgba(244,241,234,.78);max-width:620px">{txt}
        Beş şablondan biri, sizin renginiz ve logonuzla; uygulama gerekmez.</p>
      <div style="margin-top:26px;display:flex;flex-wrap:wrap;justify-content:center;gap:12px 40px">{''.join(cols)}
      </div>
      <p style="margin-top:22px;font-size:11px;color:{GRAY}">{SG.SETS[cat]['not']}</p>"""


def catalog(P):
    pages, no = [], 1
    kapak = os.path.join(FOTO, "kapak_9x12.jpg")
    cover9 = uri(kapak, 1100)
    if light(kapak):                                     # beyaz fon: fotoğraf sayfa genişliğinde, kenarı fona karışır
        im = Image.open(kapak).convert("RGB")                # fotoğrafın ışık havuzu sayfaya yayılır: ortası açık
        mid, edge = im.getpixel((im.width // 2, 24)), im.getpixel((8, 8))
        art = f"""<div style="position:absolute;inset:0;background:radial-gradient(ellipse 80% 62% at 50% 47%,
          rgb{mid} 0,rgb{mid} 45%,rgb{edge} 100%)"><img src="{cover9}"
          style="position:absolute;left:0;top:50%;width:100%;transform:translateY(-52%);
          -webkit-mask-image:linear-gradient(180deg,transparent 0,#000 18%,#000 80%,transparent 100%)"></div>"""
    else:
        art = f"""<div style="position:absolute;inset:0;background:url({cover9}) center/cover"></div>
          <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(18,19,22,.7) 0,
          rgba(18,19,22,0) 30%,rgba(18,19,22,0) 52%,rgba(18,19,22,.95) 100%)"></div>"""
    pages.append(page(f"""{art}
      <div style="position:relative">{logo("acik" if light(kapak) else "koyu", 260, 52)}</div>
      <div style="position:absolute;left:48px;right:48px;bottom:64px">
        <p class="k">ÜRÜN KATALOĞU · 2026</p>
        <h1 class="u" style="margin-top:12px;font-size:50px;line-height:1.04">QR'lı<br>isimlikler</h1>
        <p style="margin-top:16px;font-size:16px;line-height:1.5;opacity:.85">İşletmeler için
          9 × 12 cm masa isimliği, yönetici ve personel için 10 × 20 cm kurumsal isimlik. Tasarımdan 3D baskıya,
          kendi atölyemizde.</p></div>""", dark=not light(kapak)))
    no += 1

    cats = "".join(f"""<div style="background:#fff;border-radius:16px;overflow:hidden">
      <img src="{foto(models(cat)[0][1].key if cat == '10x20' else 'kuafor', maxw=600)}"
        style="width:100%;height:210px;object-fit:cover;display:block">
      <div style="padding:14px 16px"><p class="k" style="font-size:10px">{U.KATEGORI[cat]['olcu'].upper()} ·
        SİZE ÖZEL 10 TASARIM</p><p class="u" style="margin-top:6px;font-size:17px">{U.KATEGORI[cat]['ad']}</p>
        <p style="margin-top:6px;font-size:12px;line-height:1.45;color:#55575c">{U.KATEGORI[cat]['kisa']}</p></div>
      </div>""" for cat in U.KATEGORI)
    steps = "".join(f"""<div style="display:flex;gap:14px;padding:12px 0;border-top:1px solid #ddd6ca">
      <b class="u" style="color:{ORANGE};font-size:18px;width:36px">{a}</b><div><p style="font-weight:700;
      font-size:14px">{b}</p><p style="margin-top:3px;font-size:12px;color:#55575c">{c}</p></div></div>"""
                    for a, b, c in SIPARIS)
    pages.append(page(f"""<p class="k">NASIL ÇALIŞIR</p>
      <h2 class="u" style="margin-top:10px;font-size:28px;line-height:1.15">Masanızda durur,<br>müşteriniz okutur.</h2>
      <p style="margin-top:14px;font-size:13.5px;line-height:1.6;color:#3b3d42;max-width:620px">İsimlikteki QR'ı
        okutan müşteriniz size özel sayfayı açar: ara, WhatsApp, Instagram, konum, Google yorum, IBAN. Kurumsal
        isimlikte QR dijital kartvizittir: telefon, e-posta, adres, rehbere kaydet. Bilgileriniz değişirse sayfayı
        güncelleriz; isimlik aynı kalır.</p>
      <div style="margin-top:24px;display:grid;grid-template-columns:1fr 1fr;gap:16px">{cats}</div>
      <div style="margin-top:22px">{steps}</div>
      <img src="{foto('kuyumcu', 'masa', 900)}" style="margin-top:14px;width:100%;height:190px;object-fit:cover;
        border-radius:14px;display:block">
      <p style="margin-top:12px;font-size:11px;color:{GRAY}">{NOT_ORNEK}</p>""", no=no))
    no += 1

    sites = site_pages()
    if sites:
        pages.append(page(sites, dark=True, no=no))
        no += 1

    for cat in U.KATEGORI:
        K, ms = U.KATEGORI[cat], models(cat)
        feats = "".join(f'<li style="padding:7px 0;border-top:1px solid rgba(244,241,234,.14)">{f}</li>'
                        for f in K["ozellik"])
        hero = uri(os.path.join(FOTO, f"kapak_{cat}.jpg"), 900)
        pages.append(page(f"""<p class="k">KATEGORİ · {K['olcu'].upper()}</p>
          <h2 class="u" style="margin-top:10px;font-size:34px;line-height:1.1">{K['ad']}</h2>
          <p style="margin-top:10px;font-size:14px;color:rgba(244,241,234,.78)">{K['kisa']} Size özel 10 tasarım; en beğendiğinizi basıyoruz.</p>
          <img src="{hero}" style="margin-top:22px;width:100%;height:520px;object-fit:cover;border-radius:16px;
            display:block;box-shadow:0 0 0 1.5px rgba(244,241,234,.16)">
          <ul style="margin-top:20px;list-style:none;font-size:13.5px;line-height:1.4">{feats}</ul>""",
                          dark=True, no=no))
        no += 1
        for i in range(0, len(ms), 10):
            chunk = ms[i:i + 10]
            grid = "".join(card(c, u) for c, u in chunk)
            if len(chunk) == 10:                                 # 3 × 4 ızgaranın son iki yeri
                grid += f"""<div style="border-radius:14px;background:{ORANGE};color:#fff;padding:14px;display:flex;
                  flex-direction:column;justify-content:flex-end"><p class="u" style="font-size:15px">Size özel 10
                  tasarım</p><p style="margin-top:5px;font-size:11.5px;line-height:1.4">Sizin bilgilerinizle; en
                  beğendiğinizi basıyoruz.</p></div>
                  <div style="border-radius:14px;background:{INK};color:{PAPER};padding:14px;display:flex;
                  flex-direction:column;justify-content:space-between">{logo("koyu", 150, 30)}<p style="font-size:14px;
                  font-weight:700">{TEL}</p></div>"""
            pages.append(page(f"""<div style="display:flex;justify-content:space-between;align-items:flex-end">
              <div><p class="k">{K['olcu'].upper()} · {K['ad'].upper()}</p><h2 class="u" style="margin-top:8px;
              font-size:22px">{chunk[0][0]}–{chunk[-1][0]}</h2></div>{logo("acik", 150, 30)}</div>
              <div style="margin-top:18px;display:grid;grid-template-columns:repeat(3,1fr);gap:10px">{grid}</div>""",
                              no=no))
            no += 1
        kv = site_pages(cat) if cat != "9x12" else ""      # 10 × 20: kişilerin dijital kartvizitleri
        if kv:
            pages.append(page(kv, dark=True, no=no))
            no += 1

    refs = [u for u in U.URUNLER if u.tur == "musteri"]
    ref_cells = "".join(f"""<div style="display:flex;gap:12px;align-items:center;background:#fff;border-radius:12px;
      padding:8px"><img src="{foto(u.key, 'on', 240)}" style="width:76px;height:76px;object-fit:cover;
      border-radius:8px"><div><p style="font-weight:700;font-size:13px">{u.musteri}</p><p style="font-size:11px;
      color:#55575c">{u.sektor} · {U.KATEGORI[u.kat]['olcu']} · {u.ad}</p></div></div>""" for u in refs)
    pages.append(page(f"""<p class="k">REFERANSLAR</p>
      <h2 class="u" style="margin-top:10px;font-size:26px">Bastığımız isimlikler</h2>
      <p style="margin-top:10px;font-size:13px;color:#3b3d42">Bu işletmeler isimliklerini kendi seçtikleri
        tasarımla bastırdı. Katalogdaki görsellerde telefon numarası ve QR örnektir.</p>
      <div style="margin-top:18px;display:grid;grid-template-columns:1fr 1fr;gap:10px">{ref_cells}</div>
      <div style="margin-top:34px;background:{INK};color:{PAPER};border-radius:18px;padding:30px 32px;
        background-image:{BM.stripes_bg(PAPER, .035, 22)}">
        <p class="k">SİPARİŞ</p>
        <p class="u" style="margin-top:10px;font-size:24px;line-height:1.2">Shopier mağazamızdan<br>ya da telefonla.</p>
        <p style="margin-top:14px;font-size:28px;font-weight:700">{TEL}</p>
        <p style="margin-top:6px;font-size:13px;color:rgba(244,241,234,.75)">Siparişten sonra size özel 10 tasarım
          gönderiyoruz; en beğendiğinizi basıyoruz.</p>
        <div style="margin-top:22px">{logo("koyu", 240, 48)}</div></div>""", no=no))

    path = os.path.join(OUT, "katalog.pdf")
    shots = P.pdf(pages, W, H, path, css=CSS)
    cols = 4
    tw, th = 397, 562
    rows = (len(shots) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * 16, rows * th + (rows + 1) * 16), SAND)
    for k, s in enumerate(shots):
        sheet.paste(s.resize((tw, th), Image.LANCZOS), (16 + (k % cols) * (tw + 16), 16 + (k // cols) * (th + 16)))
    sheet.save(os.path.join(OUT, "katalog.png"), optimize=True)
    return path, len(pages)


def main():
    with BM.painter() as P:
        for cat in U.KATEGORI:
            out = shopier(P, cat)
            n = len([f for f in os.listdir(out) if f.endswith(".jpg")])
            print(f"shopier/{cat}: {n} model görseli, ek/ {len(os.listdir(os.path.join(out, 'ek')))}", flush=True)
        framed_all(P)
        print("cerceveli/: her ürünün üç fotoğrafı çerçevede", flush=True)
        path, n = catalog(P)
        print(f"{os.path.relpath(path, U.A.ROOT)}: {n} sayfa", flush=True)


if __name__ == "__main__":
    main()
