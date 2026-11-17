"""BOYDE LABS Instagram reklamları: güzellik koleksiyonu (kadınlara özel isimlikler: kuaför, güzellik, tırnak, kirpik...).

Kaydırmalı gönderi (5 kare, 1080 × 1440, 3:4; reklamda da kullanılır) ve hikâye/reklam (1080 × 1920, 9:16).
Fotoğraflar güzellik koleksiyonunun mevcut çekimlerinden (boyde_labs/guzellik/fotograf, siteler/*/ekran_ust.png);
marka renkleri değişmez (mürekkep zemin, kâğıt yazı, turuncu vurgu), pembeler ürünlerden gelir.

  1 kapak: Salonunuza özel isimlik (9 × 12 grup fotoğrafı)
  2 QR'lı masa isimliği 9 × 12: tezgâhta durur, müşteri okutur (Şakayık)
  3 kişiye özel 10 × 20: adınız el yazısıyla (Buse, nail artist)
  4 QR'ın açtığı sayfa: telefonda salon sayfası (Defne)
  5 nasıl sipariş: 4 adım, Shopier
  hikaye: tek görselde özet ve "Shopier'da" (üstte ve altta Instagram'ın arayüz payı boş)
Fiyat yazılmaz (10 × 20'nin fiyatı metinlerde boş); Shopier'da.

Kullanım: python3 scripts/boyde_guzellik_instagram.py
Çıktı: boyde_labs/instagram/guzellik/{kare_1..5.jpg, hikaye.jpg}
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_katalog as K  # noqa: E402
import boyde_marka as BM  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = os.path.join(ROOT, "boyde_labs", "guzellik")
OUT = os.path.join(ROOT, "boyde_labs", "instagram", "guzellik")
INK, PAPER, ORANGE = BM.INK, BM.PAPER, BM.ORANGE
W, H = 1080, 1440
SOLUK = "rgba(244,241,234,.74)"


def foto(rel, maxw=1400):
    return K.uri(os.path.join(G, rel), maxw)


def ekran(rel):
    return K.uri(os.path.join(G, rel), 780, "PNG")


def chip(t):
    return (f'<span style="padding:10px 18px;border-radius:99px;border:2px solid rgba(244,241,234,.24);'
            f'font-size:24px;color:{PAPER}">{t}</span>')


def kicker(t):
    return f'<p style="font-size:24px;font-weight:700;letter-spacing:.2em;color:{ORANGE}">{t}</p>'


def h(t, size=66):
    return (f'<h1 class="u" style="margin-top:16px;font-size:{size}px;line-height:1.06;font-weight:700;'
            f'letter-spacing:-.02em;color:{PAPER}">{t}</h1>')


def kare(ic, alt="", logo=True):
    lg = f'<div style="position:absolute;left:72px;top:64px">{K.logo("koyu", 420, 46)}</div>' if logo else ""
    return f"""<div style="position:relative;width:{W}px;height:{H}px;overflow:hidden;background:{INK};color:{PAPER}">
      {ic}{lg}{alt}</div>"""


def telefon(src, w=420):
    """Basit telefon çerçevesi içinde sayfanın üst kısmı."""
    return f"""<div style="width:{w}px;height:{w * 2.02:.0f}px;border-radius:{w * .14:.0f}px;background:#0b0b0d;
      padding:{w * .035:.0f}px;box-shadow:0 30px 60px rgba(0,0,0,.45),inset 0 0 0 2px rgba(255,255,255,.08)">
      <div style="width:100%;height:100%;border-radius:{w * .11:.0f}px;overflow:hidden;background:#fff">
        <img src="{src}" style="width:100%;display:block"></div></div>"""


def kareler():
    k = []
    # 1 kapak
    k.append(kare(f"""
      <img src="{foto('fotograf/kapak_9x12.jpg')}" style="position:absolute;left:-60px;top:330px;width:1200px">
      <div style="position:absolute;left:0;right:0;top:300px;height:160px;
        background:linear-gradient(180deg,{INK},rgba(18,19,22,0))"></div>
      <div style="position:absolute;left:72px;right:72px;top:150px">
        {kicker("KUAFÖR · GÜZELLİK · TIRNAK · KİRPİK")}
        {h("Salonunuza özel<br>isimlik.", 76)}</div>      <div style="position:absolute;left:0;right:0;bottom:0;height:300px;
        background:linear-gradient(0deg,{INK} 30%,rgba(18,19,22,0))"></div>""",
        f"""<div style="position:absolute;left:72px;right:72px;bottom:70px;display:flex;justify-content:space-between;
          align-items:flex-end"><p style="font-size:30px;line-height:1.4;color:{SOLUK};max-width:640px">Çiçek motifli,
          el yazısı adlı, QR'lı. Size özel 10 tasarım.</p>
          <span style="font-size:28px;font-weight:700;color:{PAPER}">Kaydırın <b style="color:{ORANGE}">→</b></span>
          </div>"""))
    # 2 9 × 12
    k.append(kare(f"""
      <img src="{foto('fotograf/g_sakayik_masa.jpg')}" style="position:absolute;left:0;top:300px;width:1080px">
      <div style="position:absolute;left:0;right:0;top:290px;height:150px;
        background:linear-gradient(180deg,{INK},rgba(18,19,22,0))"></div>
      <div style="position:absolute;left:72px;right:72px;top:150px">
        {kicker("QR'LI MASA İSİMLİĞİ · 9 × 12 CM")}
        {h("Tezgâhınızda dursun,<br>müşteriniz okutsun.", 58)}</div>      <div style="position:absolute;left:0;right:0;bottom:0;height:260px;
        background:linear-gradient(0deg,{INK} 30%,rgba(18,19,22,0))"></div>""",
        f"""<div style="position:absolute;left:72px;right:72px;bottom:70px;display:flex;flex-wrap:wrap;gap:12px">
          {"".join(chip(t) for t in ("Ara", "Randevu (WhatsApp)", "Instagram", "Konum", "Google yorum", "IBAN"))}
          </div>"""))
    # 3 10 × 20
    k.append(kare(f"""
      <img src="{foto('fotograf/p_buse_studyo.jpg')}" style="position:absolute;left:-60px;top:330px;width:1200px">
      <div style="position:absolute;left:0;right:0;top:320px;height:150px;
        background:linear-gradient(180deg,{INK},rgba(18,19,22,0))"></div>
      <div style="position:absolute;left:72px;right:72px;top:150px">
        {kicker("KİŞİYE ÖZEL · 10 × 20 CM")}
        {h("Adınız<br>el yazısıyla.", 76)}</div>      <div style="position:absolute;left:0;right:0;bottom:0;height:280px;
        background:linear-gradient(0deg,{INK} 30%,rgba(18,19,22,0))"></div>""",
        f"""<p style="position:absolute;left:72px;right:72px;bottom:70px;font-size:30px;line-height:1.4;color:{SOLUK}">
          Saç tasarımcısı, nail artist, estetisyen, makyaj ve kirpik uzmanı için; QR'ı dijital kartvizitinizi
          açar.</p>"""))
    # 4 QR'ın açtığı sayfa
    k.append(kare(f"""
      <div style="position:absolute;left:72px;top:150px;width:470px">
        {kicker("QR'I OKUTUNCA")}
        {h("Salonunuzun<br>sayfası açılır.", 58)}
        <p style="margin-top:28px;font-size:28px;line-height:1.45;color:{SOLUK}">Randevu, arama, Instagram, konum,
          Google yorumu ve IBAN; hepsi tek dokunuşla. Bilgileriniz değişirse sayfayı güncelleriz, isimlik aynı
          kalır.</p></div>
      <div style="position:absolute;right:64px;top:170px">{telefon(ekran('siteler/defne/ekran_ust.png'), 430)}</div>
      <img src="{foto('fotograf/g_defne_on.jpg', 700)}" style="position:absolute;left:40px;bottom:40px;width:520px;
        border-radius:28px">"""))
    # 5 nasıl sipariş
    adim = [("Sipariş verin", "Adedi seçin, ödemeyi Shopier'dan güvenle yapın."),
            ("Bilgilerinizi gönderin", "Salon adı, logo, sevdiğiniz renkler; WhatsApp'tan."),
            ("Size özel 10 tasarım", "Renk ve motiflerinizle 10 tasarım hazırlıyoruz."),
            ("Basıp gönderiyoruz", "Beğendiğinizi kendi atölyemizde basıp kargoluyoruz.")]
    rows = "".join(f"""<div style="display:grid;grid-template-columns:110px 1fr;gap:24px;padding:28px 0;
      border-top:2px solid rgba(244,241,234,.12)"><p class="u" style="font-size:56px;font-weight:700;color:{ORANGE};
      line-height:1">{i:02d}</p><div><h3 style="font-size:36px;font-weight:700">{a}</h3><p style="margin-top:8px;
      font-size:26px;line-height:1.4;color:{SOLUK}">{b}</p></div></div>""" for i, (a, b) in enumerate(adim, 1))
    k.append(kare(f"""
      <div style="position:absolute;left:0;right:0;bottom:0;height:300px;background-image:{BM.stripes_bg(PAPER, .05, 26)};
        -webkit-mask-image:linear-gradient(transparent,#000)"></div>
      <div style="position:absolute;left:72px;right:72px;top:170px">
        {kicker("NASIL SİPARİŞ VERİLİR")}
        {h("Dört adımda<br>isimliğiniz hazır.", 64)}
        <div style="margin-top:40px">{rows}</div></div>""",
        f"""<div style="position:absolute;left:72px;right:72px;bottom:72px;display:flex;justify-content:space-between;
          align-items:center"><span style="padding:18px 30px;border-radius:99px;background:{ORANGE};color:#fff;
          font-size:30px;font-weight:700">shopier.com/boyde →</span>
          <span style="font-size:28px;font-weight:700">{K.TEL}</span></div>"""))
    return k


def hikaye():
    return f"""<div style="position:relative;width:1080px;height:1920px;overflow:hidden;background:{INK};color:{PAPER}">
      <img src="{foto('fotograf/kapak_9x12.jpg')}" style="position:absolute;left:0;top:470px;width:1080px;
        -webkit-mask-image:linear-gradient(180deg,transparent 0,#000 22%,#000 74%,transparent 100%)">
      <div style="position:absolute;left:0;right:0;bottom:0;height:640px;
        background:linear-gradient(0deg,{INK} 45%,rgba(18,19,22,0))"></div>
      <div style="position:absolute;left:0;right:0;top:250px;text-align:center">
        <div style="display:inline-block">{K.logo("koyu", 460, 52)}</div>
        <p style="margin-top:44px;font-size:24px;font-weight:700;letter-spacing:.2em;color:{ORANGE}">KUAFÖR · GÜZELLİK ·
          TIRNAK · KİRPİK</p>
        <h1 class="u" style="margin-top:18px;font-size:78px;line-height:1.04;font-weight:700;letter-spacing:-.02em">
          Salonunuza<br>özel isimlik.</h1></div>
      <div style="position:absolute;left:0;right:0;bottom:230px;text-align:center">
        <p style="font-size:32px;line-height:1.4;color:{SOLUK}">Çiçek motifli, el yazısı adlı, QR'lı.<br>Size özel 10
          tasarım; kendi atölyemizde 3D baskı.</p>
        <span style="display:inline-block;margin-top:36px;padding:20px 36px;border-radius:99px;background:{ORANGE};
          color:#fff;font-size:32px;font-weight:700">Shopier'da →</span></div></div>"""


def main():
    from PIL import Image
    os.makedirs(OUT, exist_ok=True)
    with BM.painter() as P:
        for i, body in enumerate(kareler(), 1):
            png = os.path.join(OUT, f"kare_{i}.png")
            P.png(body, W, H, png, css=K.CSS)
            Image.open(png).convert("RGB").save(png[:-4] + ".jpg", quality=93)
            os.remove(png)
        png = os.path.join(OUT, "hikaye.png")
        P.png(hikaye(), 1080, 1920, png, css=K.CSS)
        Image.open(png).convert("RGB").save(png[:-4] + ".jpg", quality=93)
        os.remove(png)
    print("yazıldı:", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
