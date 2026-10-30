"""BOYDE LABS – esnafa özel anahtarlıkların Shopier görselleri (scripts/boyde_anahtarlik_esnaf.py --shopier ile
çağrılır). Görsel dil toptan anahtarlıklarınkiyle aynı (boyde_anahtarlik_katalog: çerçeve, logo, renkler).

1200 × 1200 JPG, yükleme sırasıyla:
  01 kapak · 02 beş model (dizi) · 03–07 modeller zincirli halka takımıyla · 08–12 modeller arkalı önlü ·
  13 ölçü ve özellikler (biçimler gerçek oranlarıyla, ön ve arka) · 14 nasıl sipariş verilir

Çıktı : boyde_labs/anahtarlik_esnaf/shopier/*.jpg
"""
import os
import shutil
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_anahtarlik_esnaf as E  # noqa: E402
import boyde_anahtarlik_katalog as KT  # noqa: E402
import boyde_katalog as K  # noqa: E402
import boyde_marka as BM  # noqa: E402

T = E.T
INK, PAPER, ORANGE, GRAY = K.INK, K.PAPER, K.ORANGE, K.GRAY
MESAJ = {"e01_ev": "Yeni evinize hayırlı olsun.", "e02_araba": "Yolunuz açık olsun.",
         "e03_oda": "Anahtarınızı resepsiyona bırakınız.", "e04_dis": "Gülüşünüz bize emanet.",
         "e05_kemik": "Patili dostunuz bize emanet."}
OZELLIK = [("İşinizin şeklinde", "Ev, araba, oda anahtarlığı, diş, kemik; listede olmayan işler için size özel biçim "
                                 "çiziyoruz."),
           ("Ön yüz kabartma", "Logonuz ve yazınız 0,8 mm kabartma, renkli; elle hissedilir."),
           ("Arka yüz düz yazı", "Müşterinize bir söz, telefon ya da web adresi; yüzeyle aynı hizada, silinmez."),
           ("Sağlam gövde", "3,2 mm PLA gövde, pahlı kenarlar; delik çevresinde kalın et payı."),
           ("Zincirli halka takımı", "Çelik halka, kısa zincir ve ara halka takılı; ya da yalnız anahtarlık.")]
ADIM = [("01", "İşinizi ve logonuzu yazın", "Sektörünüz, logonuz, renkler, adet ve arka yüz sözü."),
        ("02", "Tasarımı hazırlıyoruz", "Hazır biçimlerden ya da size özel; ön ve arka yüz önizlemesi."),
        ("03", "Onaylayın", "Beğendiğiniz tasarımı onaylıyorsunuz."),
        ("04", "Basıp gönderiyoruz", "Kendi atölyemizde basıp kargoya veriyoruz.")]


def buyuk(s):
    """Türkçe büyük harf (i -> İ, ı -> I)."""
    return s.replace("i", "İ").replace("ı", "I").upper()


def shopier(P):
    out = os.path.join(E.OUT, "shopier")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    name = lambda i, s: os.path.join(out, f"{i:02d}_{s}.jpg")              # noqa: E731
    models = [fn() for fn in E.MODELS]
    foto = KT.foto

    # 01 kapak: beş model masada karışık, beyaz fonda koyu yazı
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:#fff">
      <img src="{foto('kapak', 1200)}" style="width:1200px;height:1200px;display:block">
      <div style="position:absolute;left:64px;top:56px">{K.logo("acik", 330, 66)}</div>
      <div style="position:absolute;left:64px;right:64px;bottom:64px;color:{INK}">
        <p class="k">İŞİNİZİN ŞEKLİNDE · LOGONUZLA · ARKALI ÖNLÜ</p>
        <h1 class="u" style="margin-top:14px;font-size:76px;line-height:1.02;letter-spacing:-.02em">Esnafa özel<br>
          anahtarlık</h1>
        <p style="margin-top:18px;font-size:30px;line-height:1.35;color:#3b3d42">Emlakçıya ev, galeriye araba, otele
          oda anahtarlığı; önde logonuz, arkada müşterinize bir söz.</p></div></div>""", name(1, "kapak"))

    # 02 beş model: yatay fotoğraf kareye, üstü ve altı fona karışır
    im = Image.open(os.path.join(E.FOTO, "dizi.jpg")).convert("RGB")
    mid, edge = im.getpixel((im.width // 2, 12)), im.getpixel((6, 6))
    chips = "".join(f'<span class="chip" style="background:#fff;color:{INK};font-size:19px;padding:8px 14px;'
                    f'box-shadow:0 0 0 1.5px rgba(18,19,22,.08)"><b style="color:{ORANGE}">{k.kod}</b>&nbsp;{k.ad}'
                    f'<span style="color:{GRAY}">&nbsp;· {E.SEKTOR[k.key].removesuffix(" için")}</span></span>'
                    for k in models)
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;overflow:hidden;
      background:radial-gradient(ellipse 85% 60% at 50% 46%,rgb{mid} 0,rgb{mid} 40%,rgb{edge} 100%)">
      <img src="{foto('dizi', 1200)}" style="position:absolute;left:0;top:50%;width:1200px;transform:translateY(-44%);
        -webkit-mask-image:linear-gradient(180deg,transparent 0,#000 14%,#000 84%,transparent 100%)">
      <div style="position:absolute;left:64px;top:56px">{K.logo("acik", 260, 52)}</div>
      <div style="position:absolute;left:64px;right:64px;top:150px;color:{INK}">
        <p class="k">5 SEKTÖR · 5 BİÇİM</p>
        <h2 class="u" style="margin-top:12px;font-size:46px;line-height:1.08">İşinizin şeklinde,<br>arkalı önlü.</h2>
      </div>
      <div style="position:absolute;left:64px;right:64px;bottom:60px;display:flex;flex-wrap:wrap;gap:10px">{chips}
      </div></div>""", name(2, "bes_model"))

    # 03–07 halka takımıyla, 08–12 arkalı önlü; sağ üstte sektör
    for i, k in enumerate(models):
        w, h = k.size()
        KT.framed(P, f"{k.key}_halka", k.kod, f"{k.ad} · {E.SEKTOR[k.key].lower()}",
                  f"{w:.0f} × {h:.0f} mm · zincirli halka takımıyla; solda ön, sağda arka yüz",
                  name(3 + i, f"{k.kod}_{k.key[4:]}_halka"), buyuk(E.SEKTOR[k.key]))
    for i, k in enumerate(models):
        w, h = k.size()
        KT.framed(P, f"{k.key}_iki", k.kod, f"{k.ad} · ön yüz kabartma, arka düz yazı",
                  f"{w:.0f} × {h:.0f} mm · arkada “{MESAJ[k.key]}”",
                  name(8 + i, f"{k.kod}_{k.key[4:]}_arkali_onlu"), buyuk(E.SEKTOR[k.key]))

    # 13 ölçü ve özellikler: biçimler gerçek oranlarıyla, ön ve arka
    px = 3.9
    cells = ""
    for k in models:
        w, h = k.size()
        imgs = "".join(f"""<img src="{K.uri(os.path.join(E.SRC, f'{k.key}_{v}.png'), 600, 'PNG')}"
          style="width:{w * px:.0f}px;height:{h * px:.0f}px;display:block;
          filter:drop-shadow(0 6px 10px rgba(0,0,0,.18))">""" for v in ("on", "arka"))
        cells += f"""<div style="display:flex;flex-direction:column;align-items:center;gap:12px">{imgs}
          <p style="font-size:17px;font-weight:700;color:#55575c">{k.kod} · {w:.0f} × {h:.0f} mm</p></div>"""
    feats = "".join(f"""<li style="display:flex;gap:12px"><b style="color:{ORANGE}">—</b><span><b>{a}.</b> {b}</span></li>"""
                    for a, b in OZELLIK)
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:{PAPER};padding:56px 56px;
      color:{INK}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <div><p class="k">ÖLÇÜ VE ÖZELLİKLER</p>
        <h2 class="u" style="margin-top:12px;font-size:44px;line-height:1.08">Önde kabartma,<br>arkada düz yazı.</h2></div>
        {K.logo("acik", 220, 44)}</div>
      <div style="margin-top:36px;display:flex;justify-content:space-between;align-items:flex-end">{cells}</div>
      <p style="margin-top:10px;font-size:15px;color:{GRAY}">Üst sıra ön yüz, alt sıra arka yüz; gerçek oranlarıyla.</p>
      <ul style="margin-top:40px;list-style:none;display:grid;gap:18px;font-size:24px;line-height:1.35">{feats}</ul>
      </div>""", name(13, "olcu_ozellik"))

    # 14 nasıl sipariş verilir
    rows = "".join(f"""<div style="display:flex;gap:28px;padding:18px 0;border-top:2px solid rgba(244,241,234,.14)">
      <b class="u" style="font-size:44px;color:{ORANGE};width:90px">{a}</b><div><p style="font-size:32px;
      font-weight:700">{b}</p><p style="margin-top:8px;font-size:23px;color:rgba(244,241,234,.72)">{c}</p></div>
      </div>""" for a, b, c in ADIM)
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:{INK};color:{PAPER};padding:64px;
      background-image:{BM.stripes_bg(PAPER, .035, 30)}">
      <p class="k">NASIL SİPARİŞ VERİLİR</p>
      <h2 class="u" style="margin-top:12px;font-size:48px;line-height:1.1">İşinizi söyleyin,<br>gerisini biz yapalım.</h2>
      <p style="margin-top:20px;font-size:25px;color:rgba(244,241,234,.8)">Adet arttıkça birim fiyat düşer.</p>
      <div style="margin-top:30px">{rows}</div>
      <img src="{foto('kapak', 1200)}" style="margin-top:14px;width:100%;height:250px;object-fit:cover;
        object-position:50% 27%;border-radius:22px;display:block">
      <div style="position:absolute;left:64px;bottom:50px">{K.logo("koyu", 300, 60)}</div>
      <p style="position:absolute;right:64px;bottom:60px;font-size:26px;font-weight:700">{K.TEL}</p></div>""",
         name(14, "nasil_siparis"))
    return out


def main():
    E.bagla()
    with BM.painter() as P:
        out = shopier(P)
    print(f"{os.path.relpath(out, T.A.ROOT)}: {len(os.listdir(out))} görsel")


if __name__ == "__main__":
    main()
