"""BOYDE LABS Instagram: markanın genel tanıtımı, profil ızgarasında yan yana birleşen 3 gönderi (ızgara bulmacası).

Kullanıcı: fotoğrafsız, sade, büyük yazılar, tek bir anlatım: "Her katman size özel"; yazılım da yazılsın. Önceki
sürümde her karede ayrı yazı vardı, kareler yalnız alttaki katmanlarla birleşiyordu ("çok birleşik değil"). Şimdi tek
bir tuval: solda üstte büyük BOYDE LABS logosu (ızgarada okunsun), büyük cümle iki satır hâlinde karelerin arasından geçer, katmanlar boydan boya akar, nozul 3. karede.

Izgara: gönderiler 3:4 (1080 × 1440) olduğu gibi yüklenir (kırpma ekranında 3:4 / orijinal); ızgara karenin tamamını
gösterir. Tuval 3240 × 1440, üç kareye bindirmeden bölünür: cümle ve katmanlar ızgarada kareden kareye birebir akar.
(Bir önceki sürüm kare kırpmaya göreydi; 3:4 yüklenince kenarlar iki kez görünüyordu: "Her kakatman".)
Yazılar yine dikeyde ortadaki bantta (y 120–1320): kare kırpılsa da kesilmez, yalnız kareler arası akış bozulur.
Izgarada en yeni gönderi solda: önce 3. kare, en son 1. kare paylaşılır.

Kullanım: python3 scripts/boyde_instagram_panorama.py
Çıktı: boyde_labs/instagram/tanitim_panorama/{kare_1..3.jpg, izgara.jpg (ızgaradaki görünüş)}
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_katalog as K  # noqa: E402
import boyde_marka as BM  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "boyde_labs", "instagram", "tanitim_panorama")
KW, KH = 1080, 1440                                   # bir kare (3:4)
CW, CH = 3 * KW, KH                                   # tuval: üç kare yan yana, bindirmesiz
X0, X1, Y0, Y1 = 40, CW - 40, 120, 1320               # yazı alanı (tuvalde)
INK, PAPER, ORANGE = BM.INK, BM.PAPER, BM.ORANGE
SATIR1 = ("Her katman", PAPER)
SATIR2 = ("size özel.", ORANGE)
BOY = 280                                             # büyük cümlenin punto boyu


def katmanlar():
    """Logodaki katmanlar tuvalin solundan akar; en üstteki turuncu, 3. karede nozulun altında biter."""
    n = K.LOGO
    sim, sw, sh = BM.lockup(n, "simge", "koyu")
    mark = BM.DIRS[n][2]
    _, (_, y0, _, y1) = mark()
    rows = mark.rows
    ih = 360
    iw = ih * sw / sh
    k = ih / (y1 - y0)
    top = Y1 - 46 - (rows[-1][0] - y0) * k
    left = X1 - 24 - iw
    bars = "".join(
        f'<i style="position:absolute;left:-40px;width:{left + 40 + h * k:.0f}px;top:{top + (yc - y0 - h / 2) * k:.1f}px;'
        f'height:{h * k:.1f}px;background:linear-gradient(90deg,transparent 3%,rgba({BM._rgb(ORANGE if r == "accent" else PAPER)},'
        f'1) 70%)"></i>' for yc, h, r in rows)
    return (f'{bars}<div style="position:absolute;left:{left:.0f}px;top:{top:.0f}px">'
            f'{BM.inline(sim, height=f"{ih}px")}</div>'), top, left


def tuval():
    lay, nozul_top, nozul_left = katmanlar()
    h1 = f"font-size:{BOY}px;line-height:1;font-weight:700;letter-spacing:-.04em;white-space:nowrap"
    return f"""<div style="position:relative;width:{CW}px;height:{CH}px;overflow:hidden;background:{INK};color:{PAPER}">
      {lay}
      <div style="position:absolute;left:{X0 + 40}px;top:{Y0 + 44}px">{K.logo("koyu", 900, 128)}</div>
      <p style="position:absolute;right:{CW - X1 + 40}px;top:{Y0 + 80}px;font-size:26px;font-weight:700;
        letter-spacing:.16em;color:rgba(244,241,234,.6)">SHOPIER · DM · {K.TEL}</p>
      <h1 class="u" style="position:absolute;left:{X0 + 30}px;top:{Y0 + 210}px;{h1};color:{SATIR1[1]}">{SATIR1[0]}</h1>
      <h1 class="u" style="position:absolute;right:{CW - X1 + 30}px;top:{Y0 + 210 + BOY * 1.02:.0f}px;{h1};
        color:{SATIR2[1]}">{SATIR2[0]}</h1>
      <p style="position:absolute;left:{X0 + 40}px;top:{Y0 + 210 + BOY * 2.02 + 40:.0f}px;font-size:34px;
        letter-spacing:.02em;color:rgba(244,241,234,.78)"><b style="color:{PAPER};letter-spacing:.08em">BOYDE LABS</b>&nbsp; İsimlik · anahtarlık · promosyon · yazılım
        <span style="color:rgba(244,241,234,.45)">— tasarımdan 3D baskıya, kendi atölyemizde.</span></p>
    </div>"""


def main():
    from PIL import Image
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        os.remove(os.path.join(OUT, f))
    png = os.path.join(OUT, "_tuval.png")
    with BM.painter() as P:
        P.png(tuval(), CW, CH, png, css=K.CSS)
    im = Image.open(png).convert("RGB")
    os.remove(png)
    for i in range(3):
        im.crop((i * KW, 0, (i + 1) * KW, KH)).save(os.path.join(OUT, f"kare_{i + 1}.jpg"), quality=93)
    # ızgaradaki görünüş: kareler yan yana, aralarında 3 px
    g = Image.new("RGB", (3 * KW + 6, KH), (0, 0, 0))
    for i in range(3):
        g.paste(Image.open(os.path.join(OUT, f"kare_{i + 1}.jpg")), (i * (KW + 3), 0))
    g.save(os.path.join(OUT, "izgara.jpg"), quality=90)
    print("yazıldı:", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
