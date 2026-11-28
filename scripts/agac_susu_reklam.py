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
PPM = (INFO["atkili_ayicik"]["boyut"][1] - 6) / 40.2
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
1 set (7 süs) · 2–4 üçlüler · 5 ikili · 6 ren geyiği ve ayıcık yakın
"""


def foto(name, maxw=1600):
    return K.uri(os.path.join(FOTO, f"{name}.jpg"), maxw)


LOGO = (44, 40, 44 + 260, 40 + 58)                       # sayfadaki yerleri (1200 × 1200'e göre): test için
ROZET_W, ROZET_H = 190, 54
SERIT_H = 120                                            # başlık şeridi: alttan 28 px yukarıda


def rozet(right=44, top=40, size=24):
    return (f'<span style="position:absolute;right:{right}px;top:{top}px;padding:12px 22px;border-radius:99px;'
            f'background:{ORANGE};color:#fff;font-size:{size}px;font-weight:800;letter-spacing:.06em">7\'Lİ SET</span>')


def sayfa(photo, baslik, W=1200, H=1200, k=1.0):
    """Bütün sayfaların tek düzeni: fotoğraf tam kadraj; sol üstte logo, sağ üstte 7'Lİ SET; altta buzlu cam şeritte
    yalnız başlık (turuncu çizgi + manşet)."""
    return f"""<div style="position:relative;width:{W}px;height:{H}px;overflow:hidden">
      <img src="{foto(photo, 1800)}" style="position:absolute;inset:0;width:100%;height:100%;display:block">
      <div style="position:absolute;left:{30 * k:.0f}px;top:{28 * k:.0f}px;padding:{12 * k:.0f}px {16 * k:.0f}px;
        border-radius:{18 * k:.0f}px;background:rgba(255,255,255,.66);backdrop-filter:blur(18px)">
        {K.logo("acik", int(250 * k), int(56 * k))}</div>
      {rozet(int(44 * k), int(40 * k), int(24 * k))}
      <div style="position:absolute;left:{28 * k:.0f}px;right:{28 * k:.0f}px;bottom:{28 * k:.0f}px;height:{SERIT_H * k:.0f}px;
        display:flex;align-items:center;gap:{22 * k:.0f}px;padding:0 {32 * k:.0f}px 0 {28 * k:.0f}px;border-radius:{26 * k:.0f}px;
        background:rgba(255,255,255,.66);backdrop-filter:blur(22px) saturate(1.3);
        box-shadow:inset 0 0 0 1.5px rgba(18,19,22,.08);color:{INK}">
        <span style="flex:none;width:{12 * k:.0f}px;height:{64 * k:.0f}px;border-radius:6px;background:{ORANGE}"></span>
        <p class="u" style="flex:1;font-size:{46 * k:.0f}px;line-height:1.05;letter-spacing:-.01em">{baslik}</p></div></div>"""


SHOPIER = [("kapak", "Yılbaşı ağaç süsü seti"), ("set_kare", "7 süs, tek sette."),
           ("uclu_1", "Dala asın, ağacınız şenlensin"), ("yakin", "Kolları, bacakları oynar"),
           ("uclu_2", "Renkler boyadan değil, baskıdan"), ("ikili", "Avuç içi kadar, ağacın neşesi"),
           ("uclu_3", "Sepete ekleyin, gerisi bizde")]
TRENDYOL_SIRA = ["dikey", "uclu_1_dikey", "uclu_2_dikey", "uclu_3_dikey", "ikili_dikey", "yakin_dikey"]
INSTAGRAM = [("gonderi", "Ağacınıza 7 yeni dost.", 1080, 1350), ("hikaye", "7 süs, tek sette.", 1080, 1920)]


def shopier(P):
    out = os.path.join(KOK, "shopier")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    for i, (ph, t) in enumerate(SHOPIER, 1):
        K.sq(P, sayfa(ph, t), os.path.join(out, f"{i:02d}_{ph}.jpg"))
    with open(os.path.join(out, "aciklama.txt"), "w", encoding="utf-8") as f:
        f.write(ACIKLAMA + "\n")
    return out


def trendyol():
    out = os.path.join(KOK, "trendyol")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    for i, src in enumerate(TRENDYOL_SIRA, 1):
        Image.open(os.path.join(FOTO, f"{src}.jpg")).convert("RGB").save(os.path.join(out, f"{i}_{src}.jpg"),
                                                                           quality=92)
    with open(os.path.join(out, "ilan.txt"), "w", encoding="utf-8") as f:
        f.write(TRENDYOL)
    return out


def instagram(P):
    out = os.path.join(KOK, "instagram")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    for ph, t, W, H in INSTAGRAM:
        tmp = os.path.join(out, "_g.png")
        P.png(sayfa(ph, t, W, H, W / 1200), W, H, tmp, css=K.CSS)
        Image.open(tmp).convert("RGB").save(os.path.join(out, f"{ph}.jpg"), quality=92)
        os.remove(tmp)
    return out


def test():
    """Kendi içinde sınama: her görselde ürünler (piksel kutuları) logo, rozet ve başlık şeridiyle çakışmıyor, kadrajdan
    taşmıyor; ürünlerin görsel içindeki payı (ön planda mı) ve sayfalar arası tutarlılık (aynı düzen) raporlanır."""
    sorun, satir = [], []
    isler = [(ph, 1200, 1200, True) for ph, _ in SHOPIER] + [(ph, W, H, True) for ph, _, W, H in INSTAGRAM] + \
            [(ph, 1200, 1800, False) for ph in TRENDYOL_SIRA]
    for ph, W, H, yazili in isler:
        j = json.load(open(os.path.join(FOTO, f"{ph}.json")))
        sx, sy = W / j["boyut"][0], H / j["boyut"][1]
        k = W / 1200
        kutular = [(a * sx, b * sy, c * sx, d * sy) for a, b, c, d in j["urunler"]]
        engel = []
        if yazili:
            engel = [("logo", (LOGO[0] * k, LOGO[1] * k, LOGO[2] * k, LOGO[3] * k)),
                     ("rozet", (W - (44 + ROZET_W) * k, 40 * k, W - 44 * k, (40 + ROZET_H) * k)),
                     ("şerit", (28 * k, H - (28 + SERIT_H) * k, W - 28 * k, H - 28 * k))]
        for a, b, c, d in kutular:
            if a < 4 or b < 4 or c > W - 4 or d > H - 4:
                sorun.append(f"{ph}: ürün kadrajdan taşıyor")
            for ad, (e, f, g, h) in engel:
                if a < g and c > e and b < h and d > f:
                    sorun.append(f"{ph}: ürün {ad} altında")
        x0, y0 = min(q[0] for q in kutular), min(q[1] for q in kutular)
        x1, y1 = max(q[2] for q in kutular), max(q[3] for q in kutular)
        pay = sum((c - a) * (d - b) for a, b, c, d in kutular) / (W * H)
        en = max((x1 - x0) / W, (y1 - y0) / H)                 # grubun kapladığı en büyük boyut (en ya da boy)
        boy = min(d - b for a, b, c, d in kutular) / H
        if len(kutular) == 1:                                    # tek ürün: yakın çekim, boyu yeter
            en = max(en, 1.6 * boy)
        satir.append(f"{ph:20s} ürün sayısı {len(kutular)}  ürünlerin alanı %{100 * pay:4.1f}  grubun kapladığı %{100 * en:3.0f}"
                     f"  en küçük ürün boyu %{100 * boy:4.1f}")
        if en < 0.45 or boy < 0.09:
            sorun.append(f"{ph}: ürünler küçük kalıyor (grup %{100 * en:.0f}, en küçük ürün %{100 * boy:.0f})")
    return satir, sorun


def main():
    satir, sorun = test()
    print("\n".join(satir))
    print("SORUN:", sorun or "yok")
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
