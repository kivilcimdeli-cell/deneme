"""BOYDE LABS – Yılbaşı ağaç süsü SETİ (7'li): Shopier görselleri (1200 × 1200) ve açıklaması, Trendyol fotoğrafları
(1200 × 1800, yazısız) ve ilan metni, Instagram gönderi (1080 × 1350) ve hikaye (1080 × 1920).

Kullanıcı (2. tur): "daha tasarımsal bir yılbaşı ortamı; beyaz arka plan ve yazı stillerimizden vazgeçmeyelim; ince
yazıları kaldıralım, yalnızca manşet başlıklar olsun": görsellerde yalnız başlık, logo ve 7'Lİ SET rozeti; bilgiler
açıklama metninde. Fotoğraflarda ışık zinciri, cam toplar, yıldızlar ve zeminde hediye kutuları (agac_susu_foto.susle,
zemin).

Kullanıcı: dikey basılan anahtarlıklar tablada devrildi; yerine düz basılan, eklemli ağaç süsleri 7'li set olarak
satılacak; eski anahtarlık ilanları Shopier'dan ve Trendyol'dan kaldırılacak. Görsel dil önceki yılbaşı setininki
(logo, turuncu "7'Lİ SET" rozeti, buzlu cam şerit, beyaz stüdyo).

Önce fotoğraflar:
  python3 scripts/agac_susu_kes.py                 # figürler kullanıcının görselinden
  python3 scripts/agac_susu_kompozit.py            # dala asılı çekimler
  python3 scripts/agac_susu_foto.py detay          # ayıcık yakın (3MF'den)
Sonra: python3 scripts/agac_susu_reklam.py
Çıktı: boyde_labs/agac_susu/{shopier,trendyol,instagram}/ ve boyde_labs/agac_susu/agac_susu_reklam.zip
"""
import json
import os
import shutil
import sys
import zipfile

from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agac_susu_model as M  # noqa: E402
import boyde_katalog as K  # noqa: E402
import boyde_marka as BM  # noqa: E402

INK, PAPER, ORANGE, GRAY = K.INK, K.PAPER, K.ORANGE, K.GRAY
KOK = os.path.join(M.KOK, "boyde_labs", "agac_susu")
FOTO, KESIK = os.path.join(KOK, "foto"), os.path.join(KOK, "kesik")
SIRA = ["noel_baba", "kardan_adam", "cam_agaci", "ren_geyigi", "atkili_ayicik", "kutup_ayisi", "zencefilli_kurabiye"]
INFO = json.load(open(os.path.join(KESIK, "kesik.json")))
PPM = 279.0 / 40.2
LISTE = "Noel Baba, kardan adam, çam ağacı, ren geyiği, ayıcık, kutup ayısı ve zencefilli kurabiye"
OZELLIK = [("7'li set", LISTE + "."),
           ("Eklemli figürler", "Kolları ve bacakları oynar; dalda sallandıkça canlanır."),
           ("Renkler baskıdan gelir", "Çok renkli 3D baskı; boya yok, renkler filamentin kendisi."),
           ("Hafif ve dayanıklı", "Her biri yaklaşık 4 cm boy, 1 cm kalınlık; PLA, dalı eğmez, kırılmaz."),
           ("Askıya hazır", "Her süsün kırmızı askı ipi takılı gelir; dala asmanız yeterli.")]
ADIM = [("01", "Seti sepete ekleyin", "1 adet = 7 süsün hepsi. Ödeme Shopier'dan güvenle; birden çok set de olur."),
        ("02", "Basıyoruz", "Yedi süsü kendi atölyemizde basıp askı iplerini takıyoruz."),
        ("03", "Kargoya veriyoruz", "Setiniz özenle paketlenip yola çıkıyor.")]
ACIKLAMA = f"""Yılbaşı Ağaç Süsü Seti (7'li) – Eklemli 3D Baskı Figürler

{LISTE} bir arada! Yedi sevimli yılbaşı süsü, her biri askı ipiyle; ağacınıza asmaya hazır.

Ürün set olarak satılır: 1 adet sipariş = 7 süsün hepsi (süsler tek tek satılmaz).

Sette neler var?
• 7 adet 3D baskı ağaç süsü: Noel Baba, kardan adam, çam ağacı, ren geyiği, ayıcık, kutup ayısı, zencefilli kurabiye
• 7 adet kırmızı askı ipi; süslere takılı gelir

Özellikler
• Eklemli figürler: kolları ve bacakları oynar
• Çok renkli 3D baskı: boya yok, renkler filamentin kendisi; solmaz, dökülmez
• Boyut: her süs yaklaşık 4 cm boy, 3 cm en, 1 cm kalınlık
• Malzeme: PLA; hafif, dalı eğmez, cam süs gibi kırılmaz
• Çam ağacı, kapı süsü, hediye paketi ya da pencere süsü olarak kullanılabilir

Yılbaşı hediyesi, çocuklarla ağaç süsleme keyfi ya da ofiste çekilişlik hediye için ideal.

Kendi atölyemizde tasarlayıp basıyoruz. Baskı ürünü olduğu için yüzeyde ince katman izleri görülebilir; bu, 3D
baskının doğal dokusudur. Küçük parçalar içerdiğinden 3 yaş altı çocuklar için uygun değildir.

Sorularınız için Shopier mesaj ya da Instagram @boydelabs üzerinden yazabilirsiniz.
BOYDE LABS · Her katman size özel."""
TRENDYOL = f"""BAŞLIK
Yılbaşı Ağaç Süsü Seti 7'li – Eklemli 3D Baskı Noel Baba, Kardan Adam, Ren Geyiği, Ayıcık Süs

KATEGORİ ÖNERİSİ
Ev & Mobilya > Yılbaşı Süsleri > Yılbaşı Ağacı Süsü

AÇIKLAMA
{ACIKLAMA.split(chr(10), 2)[2].replace("Sorularınız için Shopier mesaj ya da Instagram @boydelabs üzerinden yazabilirsiniz.", "Sorularınız için Satıcıya Sor bölümünden yazabilirsiniz.").replace(chr(10) + "BOYDE LABS · Her katman size özel.", "")}

ÖZELLİKLER (ürün özellik alanları)
Adet: 7 · Malzeme: PLA (plastik) · Renk: çok renkli · Boyut: ~4 × 3 × 1 cm · Askı: kırmızı ip, takılı

GÖRSEL SIRASI (trendyol/ klasörü; görsellerde yazı, logo, fiyat yok – Trendyol kuralı)
1 set_dikey · 2 uclu_1 · 3 uclu_2 · 4 ikili · 5 ayicik_yakin · 6 set_icerigi · 7 set_genis
"""


def foto(name, maxw=1600):
    return K.uri(os.path.join(FOTO, f"{name}.jpg"), maxw)


def kesik(key):
    return K.uri(os.path.join(KESIK, f"{key}.png"), 600, "PNG")


def rozet(right=44, top=40, size=24):
    return (f'<span style="position:absolute;right:{right}px;top:{top}px;padding:12px 22px;border-radius:99px;'
            f'background:{ORANGE};color:#fff;font-size:{size}px;font-weight:800;letter-spacing:.06em">7\'Lİ SET</span>')


def framed(P, photo, chip, t1, t2, path):
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;overflow:hidden">
      <img src="{foto(photo)}" style="position:absolute;inset:0;width:100%;height:100%;display:block">
      <div style="position:absolute;left:44px;top:40px">{K.logo("acik", 260, 58)}</div>
      {rozet()}
      <div style="position:absolute;left:28px;right:28px;bottom:28px;display:flex;align-items:center;gap:22px;
        padding:26px 30px 26px 26px;border-radius:26px;background:rgba(255,255,255,.62);
        backdrop-filter:blur(22px) saturate(1.3);box-shadow:inset 0 0 0 1.5px rgba(18,19,22,.08);color:{INK}">
        <span style="flex:none;width:12px;height:64px;border-radius:6px;background:{ORANGE}"></span>
        <p class="u" style="flex:1;font-size:40px;line-height:1.1">{t1}</p></div></div>""", path)


def shopier(P):
    out = os.path.join(KOK, "shopier")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    name = lambda i, s: os.path.join(out, f"{i:02d}_{s}.jpg")              # noqa: E731
    head = lambda: f'<div style="position:absolute;left:56px;top:48px">{K.logo("acik", 260, 54)}</div>'  # noqa: E731

    # 01 kapak
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:#fff">
      <img src="{foto('kapak')}" style="width:1200px;height:1200px;display:block">
      <div style="position:absolute;left:64px;top:56px">{K.logo("acik", 330, 66)}</div>
      {rozet(64, 60)}
      <div style="position:absolute;left:64px;right:64px;bottom:60px;color:{INK}">
        <h1 class="u" style="font-size:80px;line-height:1.02;letter-spacing:-.02em">Yılbaşı<br>
          ağaç süsü seti</h1></div></div>""", name(1, "kapak"))

    # 02 sette neler var: 4 + 3 süs, gerçek oranlarıyla
    def hucre(i, k):
        w, h = INFO[k]["boyut"]
        s = 0.95
        return f"""<div style="position:relative;border-radius:22px;background:#fff;display:grid;place-items:center;
          box-shadow:0 2px 10px rgba(0,0,0,.05)">
          <img src="{kesik(k)}" style="width:{w * s:.0f}px;height:{h * s:.0f}px;
            filter:drop-shadow(0 8px 12px rgba(0,0,0,.18))"></div>"""
    ust = "".join(hucre(i, k) for i, k in enumerate(SIRA[:4]))
    alt = "".join(hucre(i + 4, k) for i, k in enumerate(SIRA[4:]))
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:{PAPER};color:{INK}">{head()}
      {rozet(56, 48)}
      <div style="position:absolute;left:56px;right:56px;top:140px">
        <h2 class="u" style="font-size:60px;line-height:1.08">7 süs, tek sette.</h2>
      </div>
      <div style="position:absolute;left:56px;right:56px;top:290px;height:400px;display:grid;
        grid-template-columns:repeat(4,1fr);gap:18px">{ust}</div>
      <div style="position:absolute;left:170px;right:170px;top:712px;height:400px;display:grid;
        grid-template-columns:repeat(3,1fr);gap:18px">{alt}</div></div>""", name(2, "sette_neler_var"))

    # 03, 04, 05
    framed(P, "uclu_1", "", "Dala asın, ağacınız şenlensin", "", name(3, "dala_asin"))
    framed(P, "detay_ayicik", "", "Kolları, bacakları oynar", "", name(4, "eklemli"))
    framed(P, "uclu_2", "", "Renkler boyadan değil, baskıdan", "", name(5, "renkli_baski"))

    # 06 ölçü ve özellikler
    px = 4.6
    cells = ""
    for k in SIRA:
        w, h = INFO[k]["boyut"]
        cells += f"""<div style="display:flex;flex-direction:column;align-items:center;gap:10px">
          <img src="{kesik(k)}" style="width:{w / PPM * px:.0f}px;height:{h / PPM * px:.0f}px;display:block;
            filter:drop-shadow(0 6px 10px rgba(0,0,0,.16))">
          </div>"""
    feats = "".join(f"""<li style="display:flex;gap:12px"><b style="color:{ORANGE}">—</b><span><b>{a}.</b> {b}</span>
      </li>""" for a, b in OZELLIK)
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:{PAPER};padding:56px 56px;
      color:{INK}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <h2 class="u" style="font-size:56px;line-height:1.06">Avuç içi kadar,<br>ağacınızın neşesi.</h2>
        {K.logo("acik", 220, 44)}</div>
      <div style="margin-top:56px;display:flex;justify-content:space-between;align-items:flex-end">{cells}</div>
      <img src="{foto('genis', 1800)}" style="margin-top:56px;width:100%;height:520px;object-fit:cover;
        object-position:50% 46%;border-radius:22px;display:block"></div>""", name(6, "olcu_ozellik"))

    # 07 nasıl sipariş verilir
    rows = "".join(f"""<div style="display:flex;gap:28px;padding:18px 0;border-top:2px solid rgba(244,241,234,.14)">
      <b class="u" style="font-size:44px;color:{ORANGE};width:90px">{a}</b><p class="u" style="font-size:40px;
      line-height:1.2">{b}</p></div>""" for a, b, c in ADIM)
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:{INK};color:{PAPER};padding:64px;
      background-image:{BM.stripes_bg(PAPER, .035, 30)}">
      {rozet(64, 56)}
      <h2 class="u" style="margin-top:8px;font-size:56px;line-height:1.1">Sepete ekleyin;<br>gerisi bizde.</h2>
      <div style="margin-top:34px">{rows}</div>
      <img src="{foto('genis', 1800)}" style="margin-top:18px;width:100%;height:360px;object-fit:cover;
        object-position:50% 45%;border-radius:22px;display:block">
      <div style="position:absolute;left:64px;bottom:50px">{K.logo("koyu", 300, 60)}</div>
      </div>""",
         name(7, "nasil_siparis"))
    with open(os.path.join(out, "aciklama.txt"), "w", encoding="utf-8") as f:
        f.write(ACIKLAMA + "\n")
    return out


def set_icerigi(path):
    """Trendyol: yedi süs beyaz zeminde dizili (yazısız), yumuşak gölgeli; 4 + 3."""
    W, H = 1200, 1800
    im = Image.new("RGBA", (W, H), (246, 246, 244, 255))
    s = 1.12
    rows = [SIRA[:2], SIRA[2:5], SIRA[5:]]
    y = 190
    for row in rows:
        ims = [Image.open(os.path.join(KESIK, f"{k}.png")) for k in row]
        ims = [k.resize((int(k.width * s), int(k.height * s)), Image.LANCZOS) for k in ims]
        gap = 60
        tw = sum(k.width for k in ims) + gap * (len(ims) - 1)
        x = (W - tw) // 2
        for k in ims:
            g = Image.new("RGBA", k.size, (30, 28, 24, 0))
            g.putalpha(k.split()[3].point(lambda v: int(v * 0.22)))
            g = g.filter(ImageFilter.GaussianBlur(12))
            im.alpha_composite(g, (x + 14, y + 20))
            im.alpha_composite(k, (x, y))
            x += k.width + gap
        y += max(k.height for k in ims) + 140
    im.convert("RGB").save(path, quality=92)


def trendyol():
    out = os.path.join(KOK, "trendyol")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    for i, (src, ad) in enumerate([("dikey", "set_dikey"), ("uclu_1_dikey", "uclu_1"), ("uclu_2_dikey", "uclu_2"),
                                   ("ikili_dikey", "ikili"), ("detay_ayicik_dikey", "ayicik_yakin")], 1):
        Image.open(os.path.join(FOTO, f"{src}.jpg")).convert("RGB").save(os.path.join(out, f"{i}_{ad}.jpg"),
                                                                           quality=92)
    set_icerigi(os.path.join(out, "6_set_icerigi.jpg"))
    g = Image.open(os.path.join(FOTO, "kapak.jpg")).convert("RGB").resize((1200, 1200), Image.LANCZOS)
    c = Image.new("RGB", (1200, 1800))                                    # kare kapak dikey tuvalde: kenar uzatılır
    c.paste(g.crop((0, 0, 1200, 1)).resize((1200, 300)), (0, 0))
    c.paste(g.crop((0, 1199, 1200, 1200)).resize((1200, 300)), (0, 1500))
    c.paste(g, (0, 300))
    c.save(os.path.join(out, "7_set_genis.jpg"), quality=92)
    with open(os.path.join(out, "ilan.txt"), "w", encoding="utf-8") as f:
        f.write(TRENDYOL)
    return out


def instagram(P):
    out = os.path.join(KOK, "instagram")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    tmp = os.path.join(out, "_g.png")
    from PIL import Image as _I
    k = _I.open(os.path.join(FOTO, "kapak.jpg")).convert("RGB")
    alt = "#%02x%02x%02x" % k.crop((0, k.height - 20, k.width, k.height)).resize((1, 1), _I.BOX).getpixel((0, 0))
    P.png(f"""<div style="position:relative;width:1080px;height:1350px;overflow:hidden;background:{alt};color:{INK}">
      <img src="{foto('kapak')}" style="position:absolute;left:0;top:0;width:1080px;height:1080px;
        -webkit-mask-image:linear-gradient(180deg,#000 88%,transparent 100%)">
      <div style="position:absolute;left:56px;top:52px">{K.logo("acik", 300, 60)}</div>{rozet(56, 54, 26)}
      <div style="position:absolute;left:56px;right:56px;bottom:56px">
        <h1 class="u" style="font-size:88px;line-height:1;letter-spacing:-.02em">Ağacınıza<br>7 yeni dost.</h1>
        </div></div>""", 1080, 1350, tmp,
          css=K.CSS)
    Image.open(tmp).convert("RGB").save(os.path.join(out, "gonderi.jpg"), quality=92)
    from PIL import Image as _I
    d = _I.open(os.path.join(FOTO, "dikey.jpg")).convert("RGB")
    fon = "#%02x%02x%02x" % d.resize((1, 1), _I.BOX).getpixel((0, 0))
    fon = "#%02x%02x%02x" % d.crop((0, 0, 1200, 20)).resize((1, 1), _I.BOX).getpixel((0, 0))
    P.png(f"""<div style="position:relative;width:1080px;height:1920px;overflow:hidden;background:{fon};color:{INK}">
      <img src="{foto('dikey')}" style="position:absolute;left:0;top:420px;width:1000px;height:1500px;left:40px;
        -webkit-mask-image:linear-gradient(180deg,transparent 0,#000 9%)">
      <div style="position:absolute;left:64px;top:90px">{K.logo("acik", 300, 60)}</div>{rozet(64, 96, 26)}
      <div style="position:absolute;left:64px;right:64px;top:200px">
        <h1 class="u" style="font-size:92px;line-height:1;letter-spacing:-.02em">7 süs,<br>tek sette.</h1></div>
      </div>""", 1080, 1920, tmp, css=K.CSS)
    Image.open(tmp).convert("RGB").save(os.path.join(out, "hikaye.jpg"), quality=92)
    os.remove(tmp)
    return out


def main():
    with BM.painter() as P:
        dirs = [shopier(P), instagram(P)]
    dirs.append(trendyol())
    zp = os.path.join(KOK, "agac_susu_reklam.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for d in dirs:
            for f in sorted(os.listdir(d)):
                z.write(os.path.join(d, f), os.path.join(os.path.basename(d), f))
    for d in dirs:
        print(os.path.relpath(d, M.KOK), len(os.listdir(d)))
    print(os.path.relpath(zp, M.KOK), os.path.getsize(zp) // 1024, "KB")


if __name__ == "__main__":
    main()
