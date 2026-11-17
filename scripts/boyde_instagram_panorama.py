"""BOYDE LABS Instagram: markanın genel tanıtımı, 3 kareli kaydırmalı gönderi (yan yana tek görsel, panorama).

Logodaki katmanlar üç karenin altından boydan boya geçer (Shopier "hakkında" görselindeki gibi); en üstteki turuncu
katman 3. karede nozulun altında biter. Kaydırdıkça katmanlar kareden kareye devam eder.
  1. kare: Merhaba, biz BOYDE LABS · Katman katman, size özel.
  2. kare: Neler yapıyoruz? (QR'lı masa isimliği, kurumsal isimlik, logolu anahtarlık, plakalı anahtarlık)
  3. kare: Tasarımdan 3D baskıya, kendi atölyemizde · sipariş (Shopier, DM, telefon) · nozul
Her kare 1080 × 1350 (Instagram 4:5). Ürün fotoğrafları mevcut çekimlerden (boyde_labs/*/fotograf).

Kullanım: python3 scripts/boyde_instagram_panorama.py
Çıktı: boyde_labs/instagram/tanitim_panorama/{panorama.jpg, kare_1..3.jpg}
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_katalog as K  # noqa: E402
import boyde_marka as BM  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABS = os.path.join(ROOT, "boyde_labs")
OUT = os.path.join(LABS, "instagram", "tanitim_panorama")
W, H, KARE = 3240, 1350, 1080
INK, PAPER, ORANGE, CHAR = BM.INK, BM.PAPER, BM.ORANGE, BM.CHAR
URUNLER = [("QR'lı masa isimliği", "urunler/fotograf/kapak_9x12.jpg", "50% 50%"),
           ("Kurumsal isimlik", "urunler/fotograf/kapak_10x20.jpg", "50% 52%"),
           ("Logolu anahtarlık", "anahtarlik_esnaf/fotograf/kapak.jpg", "50% 42%"),
           ("Plakalı anahtarlık", "anahtarlik_plaka/fotograf/kapak.jpg", "50% 50%")]
DAHA = ["İşletmenize özel web sitesi", "Promosyon ürünleri", "Hediyelik figürler"]


def katmanlar():
    """Nozul 3. karede sağda; katmanları sola, ilk karenin başına kadar uzar. (wide_graphic'in katmanlı biçimi.)"""
    n = K.LOGO
    sim, sw, sh = BM.lockup(n, "simge", "koyu")
    mark = BM.DIRS[n][2]
    _, (_, y0, _, y1) = mark()
    rows = mark.rows
    ih = 480
    iw = ih * sw / sh
    k = ih / (y1 - y0)
    top = 1222 - (rows[-1][0] - y0) * k                     # en alttaki katmanın ortası 1222 pikselde
    left = W - 120 - iw
    bars = "".join(
        f'<i style="position:absolute;left:-40px;width:{left + 40 + h * k:.0f}px;top:{top + (yc - y0 - h / 2) * k:.1f}px;'
        f'height:{h * k:.1f}px;background:linear-gradient(90deg,transparent 2%,rgba({BM._rgb(ORANGE if r == "accent" else PAPER)},'
        f'1) 80%)"></i>' for yc, h, r in rows)
    return (f'{bars}<div style="position:absolute;left:{left:.0f}px;top:{top:.0f}px">'
            f'{BM.inline(sim, height=f"{ih}px")}</div>'), top


def panorama():
    lay, nozul_top = katmanlar()
    kart = "".join(f"""<div style="position:relative;border-radius:26px;overflow:hidden;background:{CHAR}">
        <img src="{K.uri(os.path.join(LABS, f), 900)}" style="width:100%;height:100%;object-fit:cover;
          object-position:{pos};display:block">
        <span style="position:absolute;left:16px;bottom:16px;padding:10px 18px;border-radius:99px;background:{INK};
          color:{PAPER};font-size:22px;font-weight:700">{ad}</span></div>""" for ad, f, pos in URUNLER)
    daha = "".join(f'<span style="padding:10px 18px;border-radius:99px;border:2px solid rgba(244,241,234,.22);'
                   f'font-size:22px">{d}</span>' for d in DAHA)
    k2, k3 = KARE, 2 * KARE
    return f"""<div style="position:relative;width:{W}px;height:{H}px;overflow:hidden;background:{INK};color:{PAPER}">
      {lay}
      <!-- 1. kare -->
      <div style="position:absolute;left:80px;top:76px">{K.logo("koyu", 696, 58)}</div>
      <div style="position:absolute;left:80px;top:290px;width:900px">
        <p style="font-size:26px;font-weight:700;letter-spacing:.2em;color:{ORANGE}">MERHABA, BİZ BOYDE LABS</p>
        <h1 class="u" style="margin-top:30px;font-size:100px;line-height:1.02;font-weight:700;letter-spacing:-.02em">
          Katman<br>katman,<br><span style="color:{ORANGE}">size özel.</span></h1>
        <p style="margin-top:38px;font-size:32px;line-height:1.4;color:rgba(244,241,234,.78)">İşletmenize özel
          isimlik, anahtarlık ve daha fazlası; tasarımdan 3D baskıya.</p>
        <p style="margin-top:34px;font-size:26px;font-weight:700;color:rgba(244,241,234,.6)">Kaydırın
          <span style="color:{ORANGE}">→</span></p></div>
      <!-- 2. kare -->
      <div style="position:absolute;left:{k2 + 80}px;top:96px;width:920px">
        <p style="font-size:26px;font-weight:700;letter-spacing:.2em;color:{ORANGE}">NELER YAPIYORUZ?</p>
        <h2 class="u" style="margin-top:18px;font-size:58px;line-height:1.06;font-weight:700;letter-spacing:-.02em">
          Logonuz, yazınız,<br>sizin tasarımınız.</h2></div>
      <div style="position:absolute;left:{k2 + 80}px;top:340px;width:920px;height:560px;display:grid;
        grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:20px">{kart}</div>
      <div style="position:absolute;left:{k2 + 80}px;top:928px;width:920px;display:flex;flex-wrap:wrap;gap:10px;
        color:rgba(244,241,234,.86)">{daha}</div>
      <!-- 3. kare -->
      <div style="position:absolute;left:{k3 + 80}px;top:96px;width:920px">
        <p style="font-size:26px;font-weight:700;letter-spacing:.2em;color:{ORANGE}">KENDİ ATÖLYEMİZDE</p>
        <h2 class="u" style="margin-top:18px;font-size:64px;line-height:1.06;font-weight:700;letter-spacing:-.02em">
          Tasarımdan<br>3D baskıya,<br>tek elden.</h2>
        <p style="margin-top:30px;font-size:30px;line-height:1.45;color:rgba(244,241,234,.78);max-width:640px">
          Size özel tasarımlar hazırlıyoruz; beğendiğinizi basıp kargoya veriyoruz.</p></div>
      <div style="position:absolute;left:{k3 + 80}px;top:{nozul_top + 20:.0f}px">
        <span style="display:inline-block;padding:16px 28px;border-radius:99px;background:{ORANGE};color:#fff;
          font-size:28px;font-weight:700">Shopier'da →</span>
        <p style="margin-top:22px;font-size:26px;line-height:1.5;color:rgba(244,241,234,.8)">DM'den yazın ya da arayın<br>
          <b style="color:{PAPER};font-size:30px">{K.TEL}</b></p></div>
    </div>"""


def main():
    from PIL import Image
    os.makedirs(OUT, exist_ok=True)
    png = os.path.join(OUT, "panorama.png")
    with BM.painter() as P:
        P.png(panorama(), W, H, png, css=K.CSS)
    im = Image.open(png).convert("RGB")
    im.save(os.path.join(OUT, "panorama.jpg"), quality=93)
    os.remove(png)
    for i in range(3):
        im.crop((i * KARE, 0, (i + 1) * KARE, H)).save(os.path.join(OUT, f"kare_{i + 1}.jpg"), quality=93)
    print("yazıldı:", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
