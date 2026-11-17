"""BOYDE LABS Instagram: markanın genel tanıtımı, profil ızgarasında yan yana birleşen 3 gönderi (ızgara bulmacası).

Kullanıcı: fotoğrafsız, sade, büyük yazılar, tek bir anlatım: "Her katman size özel"; yazılım da yazılsın. Önceki
sürümde her karede ayrı yazı vardı, kareler yalnız alttaki katmanlarla birleşiyordu ("çok birleşik değil"). Şimdi tek
bir tuval: büyük cümle iki satır hâlinde karelerin arasından geçer, katmanlar boydan boya akar, nozul 3. karede.

Izgara: Instagram yüklerken kare (1:1) kırpıyor, ızgara onun ortasından 3:4 alıyor; her karenin ortadaki 810 × 1080'i
görünür (x 135–945, y 180–1260). Tuval, ızgarada görünen üç bölge kesintisiz yan yana gelecek biçimde çizilir
(2430 × 1080 görünen bant); her kare tuvalden 1080 × 1440 kesilir, kenar payında komşu karenin devamı görünür. Böylece
ızgarada cümle ve katmanlar kareden kareye birebir akar; tek tek açınca da kesik durmaz.
Not: üç gönderide de aynı kırpma (kare) seçilmeli. Izgarada en yeni gönderi solda: önce 3. kare, en son 1. kare.

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
GX, GY, GW, GH = 135, 180, 810, 1080                  # karenin ızgarada görünen kısmı
CW, CH = 3 * GW + 2 * GX, KH                          # tuval: görünen bant 135..2565, üstte ve altta pay
X0, X1, Y0, Y1 = GX, GX + 3 * GW, GY, GY + GH         # görünen bant (tuvalde)
INK, PAPER, ORANGE = BM.INK, BM.PAPER, BM.ORANGE
SATIR1 = ("Her katman", PAPER)
SATIR2 = ("size özel.", ORANGE)
BOY = 236                                             # büyük cümlenin punto boyu


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
      <div style="position:absolute;left:{X0 + 40}px;top:{Y0 + 40}px">{K.logo("koyu", 420, 44)}</div>
      <p style="position:absolute;right:{CW - X1 + 40}px;top:{Y0 + 46}px;font-size:24px;font-weight:700;
        letter-spacing:.16em;color:rgba(244,241,234,.6)">SHOPIER · DM · {K.TEL}</p>
      <h1 class="u" style="position:absolute;left:{X0 + 30}px;top:{Y0 + 170}px;{h1};color:{SATIR1[1]}">{SATIR1[0]}</h1>
      <h1 class="u" style="position:absolute;right:{CW - X1 + 30}px;top:{Y0 + 170 + BOY * 1.02:.0f}px;{h1};
        color:{SATIR2[1]}">{SATIR2[0]}</h1>
      <p style="position:absolute;left:{X0 + 40}px;top:{Y0 + 170 + BOY * 2.02 + 40:.0f}px;font-size:34px;
        letter-spacing:.02em;color:rgba(244,241,234,.78)">İsimlik · anahtarlık · promosyon · yazılım
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
    for i in range(3):                                       # i. karenin görünen kısmı tuvalde X0 + i*GW'den başlar
        im.crop((i * GW, 0, i * GW + KW, KH)).save(os.path.join(OUT, f"kare_{i + 1}.jpg"), quality=93)
    # ızgaradaki görünüş: her kareden ortadaki 810 × 1080, aralarında 3 px
    g = Image.new("RGB", (3 * GW + 6, GH), (0, 0, 0))
    for i in range(3):
        g.paste(Image.open(os.path.join(OUT, f"kare_{i + 1}.jpg")).crop((GX, GY, GX + GW, GY + GH)), (i * (GW + 3), 0))
    g.save(os.path.join(OUT, "izgara.jpg"), quality=90)
    print("yazıldı:", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
