"""BOYDE LABS Instagram: markanın genel tanıtımı, 3 kareli kaydırmalı gönderi (yan yana tek görsel, panorama).

Logodaki katmanlar üç karenin altından boydan boya geçer (Shopier "hakkında" görselindeki gibi); en üstteki turuncu
katman 3. karede nozulun altında biter. Kaydırdıkça katmanlar kareden kareye devam eder.
Kullanıcı: fotoğrafsız, sade, büyük yazılar, tek bir anlatım; "Her katman size özel". Tek cümle üç kareye yayılır,
kelimeler aynı hizada (kaydırdıkça cümle tamamlanır), her karede altında tek kısa satır:
  1. kare: "Her katman" · Merhaba, biz BOYDE LABS.
  2. kare: "size" · İsimlik, anahtarlık, promosyon; logonuzla, yazınızla.
  3. kare: "özel." (turuncu, turuncu katmanla) · Tasarımdan 3D baskıya, kendi atölyemizde. · nozul
Her kare 1080 × 1350 (Instagram 4:5).

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
BUYUK = 196                                         # büyük kelimelerin punto boyu (px)
SATIR = 640                                         # cümlenin satır tabanı (px): üç karede aynı hiza


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
    lay, _ = katmanlar()

    def kelime(x, metin, alt, renk=PAPER, ust=""):
        """Büyük kelime (tabanı SATIR'da) ve altında tek kısa satır."""
        ust = (f'<span style="display:block">{ust}</span>') if ust else ""
        return f"""<div style="position:absolute;left:{x + 80}px;bottom:{H - SATIR}px">
          <h1 class="u" style="font-size:{BUYUK}px;line-height:.98;font-weight:700;letter-spacing:-.035em;
            color:{renk}">{ust}{metin}</h1></div>
          <p style="position:absolute;left:{x + 86}px;top:{SATIR + 44}px;width:880px;font-size:32px;line-height:1.4;
            color:rgba(244,241,234,.72)">{alt}</p>"""

    return f"""<div style="position:relative;width:{W}px;height:{H}px;overflow:hidden;background:{INK};color:{PAPER}">
      {lay}
      <div style="position:absolute;left:80px;top:76px">{K.logo("koyu", 520, 46)}</div>
      {kelime(0, "katman", "Merhaba, biz BOYDE LABS.", ust="Her")}
      {kelime(KARE, "size", "İsimlik, anahtarlık, promosyon;<br>logonuzla, yazınızla.")}
      {kelime(2 * KARE, "özel.", "Tasarımdan 3D baskıya,<br>kendi atölyemizde.", ORANGE)}
      <p style="position:absolute;right:80px;top:84px;font-size:24px;font-weight:700;letter-spacing:.16em;
        color:rgba(244,241,234,.55)">SHOPIER · DM · {K.TEL}</p>
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
