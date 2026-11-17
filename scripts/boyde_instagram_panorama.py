"""BOYDE LABS Instagram: markanın genel tanıtımı, 3 kareli kaydırmalı gönderi (yan yana tek görsel, panorama).

Logodaki katmanlar üç karenin altından boydan boya geçer (Shopier "hakkında" görselindeki gibi); en üstteki turuncu
katman 3. karede nozulun altında biter. Kaydırdıkça katmanlar kareden kareye devam eder.
Kullanıcı: fotoğrafsız, sade, büyük yazılar, tek bir anlatım; "Her katman size özel". Profil ızgarasında yalnız ilk kare
görünür ve 3:4 kırpılır ("ızgarada yarım görünüyor"): kareler 1080 × 1440 (3:4, kırpılmaz) ve ilk kare tek başına
bütün (sloganın tamamı). Büyük yazılar üç karede aynı hizada başlar:
  1. kare: Her katman / size özel. · Merhaba, biz BOYDE LABS.
  2. kare: İsimlik, / anahtarlık, / promosyon. · Logonuzla, yazınızla; işletmenize özel.
  3. kare: Tasarımdan / 3D baskıya. · Kendi atölyemizde. · Shopier, DM, telefon · nozul

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
W, H, KARE = 3240, 1440, 1080
INK, PAPER, ORANGE, CHAR = BM.INK, BM.PAPER, BM.ORANGE, BM.CHAR
BUYUK = 150                                         # büyük yazının punto boyu (px)
UST = 300                                           # büyük yazıların üst hizası (px): üç karede aynı


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
    top = H - 120 - (rows[-1][0] - y0) * k                  # en alttaki katmanın ortası alttan 120 piksel
    left = W - 120 - iw
    bars = "".join(
        f'<i style="position:absolute;left:-40px;width:{left + 40 + h * k:.0f}px;top:{top + (yc - y0 - h / 2) * k:.1f}px;'
        f'height:{h * k:.1f}px;background:linear-gradient(90deg,transparent 2%,rgba({BM._rgb(ORANGE if r == "accent" else PAPER)},'
        f'1) 80%)"></i>' for yc, h, r in rows)
    return (f'{bars}<div style="position:absolute;left:{left:.0f}px;top:{top:.0f}px">'
            f'{BM.inline(sim, height=f"{ih}px")}</div>'), top


def panorama():
    lay, _ = katmanlar()

    def blok(x, satirlar, alt, boy=BUYUK, ek=""):
        """Büyük yazı (UST hizasında) ve altında kısa satır. satirlar: [(metin, renk)]; uzun kelimelerde boy küçülür
        (en uzun satır karenin içinde kalsın)."""
        h = "".join(f'<span style="display:block;color:{c}">{t}</span>' for t, c in satirlar)
        return f"""<div style="position:absolute;left:{x + 80}px;top:{UST}px;width:{KARE - 140}px">
          <h1 class="u" style="font-size:{boy}px;line-height:1.0;font-weight:700;letter-spacing:-.035em">{h}</h1>
          <p style="margin-top:46px;font-size:34px;line-height:1.4;color:rgba(244,241,234,.72)">{alt}</p>{ek}</div>"""

    return f"""<div style="position:relative;width:{W}px;height:{H}px;overflow:hidden;background:{INK};color:{PAPER}">
      {lay}
      <div style="position:absolute;left:80px;top:84px">{K.logo("koyu", 600, 54)}</div>
      {blok(0, [("Her", PAPER), ("katman", PAPER), ("size", ORANGE), ("özel.", ORANGE)], "Merhaba, biz BOYDE LABS.")}
      {blok(KARE, [("İsimlik,", PAPER), ("anahtarlık,", PAPER), ("promosyon.", PAPER)],
            "Logonuzla, yazınızla;<br>işletmenize özel.", 118)}
      {blok(2 * KARE, [("Tasarımdan", PAPER), ("3D baskıya.", PAPER)], "Kendi atölyemizde.", 118,
            f'''<p style="margin-top:40px;font-size:28px;line-height:1.6;color:rgba(244,241,234,.6)">Shopier · DM<br>
            <b style="color:{PAPER};font-size:34px">{K.TEL}</b></p>''')}
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
