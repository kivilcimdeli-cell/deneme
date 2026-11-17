"""BOYDE LABS Instagram: markanın genel tanıtımı, 3 kareli kaydırmalı gönderi (yan yana tek görsel, panorama).

Logodaki katmanlar üç karenin altından boydan boya geçer (Shopier "hakkında" görselindeki gibi); en üstteki turuncu
katman 3. karede nozulun altında biter. Kaydırdıkça katmanlar kareden kareye devam eder.
Kullanıcı: fotoğrafsız, sade, büyük yazılar, tek bir anlatım; "Her katman size özel". Kareler profil ızgarasında yan
yana (üç ayrı gönderi, ızgara bulmacası) birleşir. Ekran görüntüsünde Instagram yüklerken kare (1:1) kırpmış, ızgara da
onun ortasından 3:4 almış: her karenin ortadaki 810 × 1080'i görünüyor. Bu yüzden yazılar, logo ve nozul her karenin
GUVENLI alanında (x 135–945, y 180–1260); 3:4 yüklense de kare kırpılsa da ızgarada kesilmez. Katmanlar boydan boya:
  1. kare: Her katman / size özel. · Merhaba, biz BOYDE LABS.
  2. kare: İsimlik, / anahtarlık, / promosyon. · Logonuzla, yazınızla; işletmenize özel.
  3. kare: Tasarımdan / 3D baskıya. · Kendi atölyemizde. · Shopier, DM, telefon · nozul
Izgarada en yeni gönderi solda: önce 3. kare, sonra 2., en son 1. kare paylaşılır.

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
GX0, GY0, GX1, GY1 = 135, 180, 945, 1260            # güvenli alan (karenin içinde): ızgarada görünen kısım
SOL = GX0 + 32                                      # yazıların sol hizası
UST = GY0 + 150                                     # büyük yazıların üst hizası: üç karede aynı


def katmanlar():
    """Nozul 3. karede sağda; katmanları sola, ilk karenin başına kadar uzar. (wide_graphic'in katmanlı biçimi.)"""
    n = K.LOGO
    sim, sw, sh = BM.lockup(n, "simge", "koyu")
    mark = BM.DIRS[n][2]
    _, (_, y0, _, y1) = mark()
    rows = mark.rows
    ih = 400
    iw = ih * sw / sh
    k = ih / (y1 - y0)
    top = GY1 - 50 - (rows[-1][0] - y0) * k                 # en alttaki katman güvenli alanın içinde
    left = 2 * KARE + GX1 - 10 - iw                          # nozul 3. karenin güvenli alanında
    bars = "".join(
        f'<i style="position:absolute;left:-40px;width:{left + 40 + h * k:.0f}px;top:{top + (yc - y0 - h / 2) * k:.1f}px;'
        f'height:{h * k:.1f}px;background:linear-gradient(90deg,transparent 2%,rgba({BM._rgb(ORANGE if r == "accent" else PAPER)},'
        f'1) 80%)"></i>' for yc, h, r in rows)
    return (f'{bars}<div style="position:absolute;left:{left:.0f}px;top:{top:.0f}px">'
            f'{BM.inline(sim, height=f"{ih}px")}</div>'), top


def panorama():
    lay, _ = katmanlar()

    def blok(x, satirlar, alt, boy, ek=""):
        """Büyük yazı (UST hizasında) ve altında kısa satır; hepsi güvenli alanda. satirlar: [(metin, renk)]."""
        h = "".join(f'<span style="display:block;color:{c}">{t}</span>' for t, c in satirlar)
        return f"""<div style="position:absolute;left:{x + SOL}px;top:{UST}px;width:{GX1 - SOL}px">
          <h1 class="u" style="font-size:{boy}px;line-height:1.0;font-weight:700;letter-spacing:-.035em">{h}</h1>
          <p style="margin-top:36px;font-size:30px;line-height:1.4;color:rgba(244,241,234,.72)">{alt}</p>{ek}</div>"""

    return f"""<div style="position:relative;width:{W}px;height:{H}px;overflow:hidden;background:{INK};color:{PAPER}">
      {lay}
      <div style="position:absolute;left:{SOL}px;top:{GY0 + 28}px">{K.logo("koyu", 420, 44)}</div>
      {blok(0, [("Her", PAPER), ("katman", PAPER), ("size", ORANGE), ("özel.", ORANGE)],
            "Merhaba, biz BOYDE LABS.", 128)}
      {blok(KARE, [("İsimlik,", PAPER), ("anahtarlık,", PAPER), ("promosyon.", PAPER)],
            "Logonuzla, yazınızla;<br>işletmenize özel.", 96)}
      {blok(2 * KARE, [("Tasarımdan", PAPER), ("3D baskıya.", PAPER)], "Kendi atölyemizde.", 96,
            f'''<p style="margin-top:30px;font-size:26px;line-height:1.6;color:rgba(244,241,234,.6)">Shopier · DM<br>
            <b style="color:{PAPER};font-size:32px">{K.TEL}</b></p>''')}
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
