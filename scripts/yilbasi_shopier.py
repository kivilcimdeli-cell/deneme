"""BOYDE LABS – yılbaşı anahtarlık SETİ'nin Shopier görselleri (1200 × 1200 JPG) ve ürün açıklaması. Görsel dil esnaf
anahtarlıklarınınki (logo, buzlu cam şerit, turuncu vurgu).

Kullanıcı: altı figür set olarak satılacak (tek tek değil). Set: 6 anahtarlık (Noel Baba, ren geyiği, atkılı ayıcık,
kutup ayısı, kardan adam, çam ağacı) + 6 zincirli halka takımı.

Önce fotoğraflar: python3 scripts/yilbasi_foto.py (Blender; "set" grup çekimi dahil). Sonra:
python3 scripts/yilbasi_shopier.py

Yükleme sırasıyla:
  01 kapak (altısı masada) · 02 sette neler var (6 figür, adlarıyla) · 03 altısı zincirli halkada ·
  04 önü ve arkası (tam 3D) · 05 süs olarak da (çubukta asılı altı figür) · 06 ölçü ve özellikler ·
  07 nasıl sipariş verilir
Çıktı: boyde_labs/yilbasi_anahtarlik/shopier/*.jpg ve aciklama.txt
"""
import os
import shutil
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_katalog as K  # noqa: E402
import boyde_marka as BM  # noqa: E402
import yilbasi_model as YM  # noqa: E402

INK, PAPER, ORANGE, GRAY = K.INK, K.PAPER, K.ORANGE, K.GRAY
FOTO = os.path.join(YM.KOK, "boyde_labs", "yilbasi_anahtarlik", "foto")
OUT = os.path.join(YM.KOK, "boyde_labs", "yilbasi_anahtarlik", "shopier")
ETIKET = "YILBAŞI ANAHTARLIK SETİ"
CEKIM = os.path.join(YM.KOK, "boyde_labs", "instagram", "yilbasi", "_cekim.jpg")   # çubukta asılı altı figür
OZELLIK = [("6'lı set", "Noel Baba, ren geyiği, atkılı ayıcık, kutup ayısı, kardan adam ve çam ağacı."),
           ("Tam 3D figür", "Önü de arkası da yuvarlak; her yönden sevimli, elde tombul."),
           ("Renkler baskıdan gelir", "Çok renkli 3D baskı; boya yok, renkler filamentin kendisi."),
           ("Avuç içi boyutunda", "Her biri yaklaşık 4–5 cm boy, 2,3 cm kalınlık; hafif PLA."),
           ("Zincirli halka takımı", "Her figürde çelik halka, kısa zincir ve ara halka takılı gelir.")]
ADIM = [("01", "Seti sepete ekleyin", "1 adet = 6 figürün hepsi. Ödeme Shopier'dan güvenle; birden çok set de olur."),
        ("02", "Basıyoruz", "Altı figürü kendi atölyemizde basıp halka takımlarını takıyoruz."),
        ("03", "Kargoya veriyoruz", "Setiniz özenle paketlenip yola çıkıyor.")]
ACIKLAMA = """Yılbaşı Anahtarlık Seti (6'lı) – Tam 3D Figür

Noel Baba, ren geyiği, atkılı ayıcık, kutup ayısı, kardan adam ve çam ağacı bir arada! Altı sevimli yılbaşı
figürü, her biri zincirli halka takımıyla.

Ürün set olarak satılır: 1 adet sipariş = 6 figürün hepsi (figürler tek tek satılmaz).

Sette neler var?
• 6 adet 3D baskı figür anahtarlık: Noel Baba, ren geyiği, atkılı ayıcık, kutup ayısı, kardan adam, çam ağacı
• 6 adet zincirli halka takımı (çelik halka, kısa zincir, ara halka); figürlere takılı gelir

Özellikler
• Tam 3D: önü de arkası da yuvarlak, her yönden sevimli
• Çok renkli 3D baskı: boya yok, renkler filamentin kendisi
• Boyut: her figür yaklaşık 4–5 cm boy, 2,3 cm kalınlık
• Malzeme: PLA; hafif ve sağlam
• Anahtarlık, çanta süsü ya da yılbaşı ağacı süsü olarak kullanılabilir

Yılbaşı hediyesi, sevdiklerinize küçük bir sürpriz ya da ofiste çekilişlik hediye için ideal.

Kendi atölyemizde tasarlayıp basıyoruz. Baskı ürünü olduğu için yüzeyde ince katman izleri görülebilir; bu, 3D
baskının doğal dokusudur.

Sorularınız için Shopier mesaj ya da Instagram @boydelabs üzerinden yazabilirsiniz.
BOYDE LABS · Her katman size özel."""


def foto(name, maxw=1200):
    return K.uri(os.path.join(FOTO, f"{name}.jpg"), maxw)


def renkler(key):
    return ", ".join(dict.fromkeys(YM.RENK_TR.get(r, r) for _, _, _, _, r in YM.figur(key)))


def olcu(key):
    w, d, h = YM.olcu(YM.oku(key))
    return w, d, h


def framed(P, photo, chip, t1, t2, path):
    """Fotoğraf tam kadraj; sol üstte logo, sağ üstte etiket; altta buzlu cam şerit (turuncu kod, başlık, alt satır)."""
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;overflow:hidden">
      <img src="{foto(photo)}" style="position:absolute;inset:0;width:100%;height:100%;display:block">
      <div style="position:absolute;left:44px;top:40px">{K.logo("acik", 260, 58)}</div>
      {rozet()}
      <div style="position:absolute;left:28px;right:28px;bottom:28px;display:flex;align-items:center;gap:22px;
        padding:18px 26px 18px 18px;border-radius:26px;background:rgba(255,255,255,.62);
        backdrop-filter:blur(22px) saturate(1.3);box-shadow:inset 0 0 0 1.5px rgba(18,19,22,.08);color:{INK}">
        <span class="code" style="flex:none;display:grid;place-items:center;width:84px;height:84px;border-radius:18px;
          background:{ORANGE};color:#fff;font-size:26px">{chip}</span>
        <div style="flex:1;min-width:0">
          <p class="u" style="font-size:27px;line-height:1.15;white-space:nowrap;overflow:hidden;
            text-overflow:ellipsis">{t1}</p>
          <p style="margin-top:7px;font-size:18px;color:#55575c;white-space:nowrap;overflow:hidden;
            text-overflow:ellipsis">{t2}</p></div>
        <p style="flex:none;text-align:right;font-size:14px;font-weight:700;letter-spacing:.14em;line-height:1.5;
          color:#55575c">TASARIM VE<br>3D BASKI <b style="color:{ORANGE}">BOYDE</b></p></div></div>""", path)


def on_gorunus(key, path):
    """Ölçü sayfası için önden görünüş (şeffaf PNG, gerçek oranlı)."""
    from cift_tarafli_isimlik import render, rotation
    mesh = [(V, Fc, rgb) for _, V, Fc, rgb, _ in YM.figur(key)]
    im = render(mesh, 700, rotation(0, -90), margin=0.0)
    a = np.asarray(im)[:, :, 3]
    ys, xs = np.nonzero(a > 8)
    im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(path)


def rozet(right=44, top=40):
    """Her sayfada sağ üstte: 6'LI SET (ürün set olarak satılır)."""
    return (f'<span style="position:absolute;right:{right}px;top:{top}px;padding:12px 22px;border-radius:99px;'
            f'background:{ORANGE};color:#fff;font-size:24px;font-weight:800;letter-spacing:.06em">6\'LI SET</span>')


def kirp(key):
    """Asılı fotoğraftan figür ve zincirin altı (kare)."""
    from PIL import Image
    import io
    import base64
    im = Image.open(os.path.join(FOTO, f"{key}_halka.jpg")).convert("RGB")
    a = np.asarray(im, float)
    fon = np.median(np.r_[a[:20].reshape(-1, 3), a[:, :20].reshape(-1, 3)], 0)
    fark = np.abs(a - fon).max(2) > 45                      # figür (ve zincirin altı): fondan belirgin ayrılan
    h, w = fark.shape                                       # (kenarlar vinyetle koyu: eşik yüksek, kenarlar dışarıda)
    fark[: int(h * 0.3)] = False                            # çelik halka kırpmaya girmesin
    fark[int(h * 0.75):] = False                            # yerdeki gölge
    fark[:, : int(w * 0.12)] = False
    fark[:, int(w * 0.88):] = False
    ys, xs = np.nonzero(fark)
    cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    r = max(xs.max() - xs.min(), ys.max() - ys.min()) * 0.5 * 1.45
    im = im.crop((int(cx - r), int(cy - r * 1.05), int(cx + r), int(cy + r * 0.95)))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=90)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def fon_rengi(path):
    from PIL import Image
    im = np.asarray(Image.open(path).convert("RGB"), float)
    return "#%02x%02x%02x" % tuple(int(v) for v in np.r_[im[:12], im[-12:]].reshape(-1, 3).mean(0))


def shopier(P):
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    name = lambda i, s: os.path.join(OUT, f"{i:02d}_{s}.jpg")              # noqa: E731
    head = lambda: f'<div style="position:absolute;left:56px;top:48px">{K.logo("acik", 260, 54)}</div>'  # noqa: E731

    # 01 kapak: altısı masada
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:#fff">
      <img src="{foto('set')}" style="width:1200px;height:1200px;display:block">
      <div style="position:absolute;left:64px;top:56px">{K.logo("acik", 330, 66)}</div>
      {rozet(64, 60)}
      <div style="position:absolute;left:64px;right:64px;bottom:64px;color:{INK}">
        <p class="k">TAM 3D · RENKLİ BASKI · ZİNCİRLİ HALKA</p>
        <h1 class="u" style="margin-top:14px;font-size:72px;line-height:1.02;letter-spacing:-.02em">Yılbaşı<br>
          anahtarlık seti</h1>
        <p style="margin-top:18px;font-size:28px;line-height:1.35;color:#3b3d42">Set olarak satılır: <b>6 figür + 6
          zincirli halka takımı</b>. Noel Baba, ren geyiği, ayıcık, kutup ayısı, kardan adam ve çam ağacı.</p>
        </div></div>""", name(1, "kapak"))

    # 02 sette neler var: 3 × 2 figür
    cells = "".join(f"""<div style="position:relative;border-radius:22px;overflow:hidden;background:#f3f3f1">
        <img src="{kirp(k)}" style="width:100%;height:100%;object-fit:cover;display:block">
        <span style="position:absolute;left:12px;bottom:12px;padding:8px 14px;border-radius:99px;background:#fff;
          color:{INK};font-size:19px;font-weight:700;box-shadow:0 2px 8px rgba(0,0,0,.08)"><b style="color:{ORANGE}">
          {i + 1}</b>&nbsp;{YM.AD[k]}</span></div>""" for i, k in enumerate(YM.KEYS))
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:{PAPER};color:{INK}">{head()}
      {rozet(56, 48)}
      <div style="position:absolute;left:56px;right:56px;top:140px">
        <p class="k">SETTE NELER VAR</p>
        <h2 class="u" style="margin-top:12px;font-size:46px;line-height:1.08">6 figür, 6 halka takımı.</h2>
        <p style="margin-top:12px;font-size:24px;color:#55575c">Tek tek değil, altısı birlikte set olarak satılır.</p>
      </div>
      <div style="position:absolute;left:56px;right:56px;top:330px;bottom:56px;display:grid;
        grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(2,1fr);gap:18px">{cells}</div></div>""",
         name(2, "sette_neler_var"))

    # 03 altısı zincirli halkada
    fon = fon_rengi(os.path.join(FOTO, "dizi.jpg"))
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;overflow:hidden;background:{fon}">
      <img src="{foto('dizi', 1600)}" style="position:absolute;left:-60px;top:50%;width:1320px;
        transform:translateY(-44%);-webkit-mask-image:linear-gradient(180deg,transparent 0,#000 16%,#000 84%,
        transparent 100%)">
      <div style="position:absolute;left:64px;top:56px">{K.logo("acik", 260, 52)}</div>{rozet(64, 56)}
      <div style="position:absolute;left:64px;right:64px;top:150px;color:{INK}">
        <p class="k">ALTISI BİR ARADA · SET</p>
        <h2 class="u" style="margin-top:12px;font-size:46px;line-height:1.08">Her birine<br>zincirli halka takılı.</h2>
      </div>
      <p style="position:absolute;left:64px;right:64px;bottom:64px;font-size:26px;color:#3b3d42">Çelik halka, kısa
        zincir ve ara halka; anahtarınıza takmaya hazır.</p></div>""", name(3, "zincirli_halka"))

    # 04 önü ve arkası
    framed(P, "noel_baba_iki", "3D", "Önü de arkası da tombul",
           "Setteki altı figür de tam 3D: arkası da yuvarlak (soldaki önü, sağdaki arkası)", name(4, "onu_arkasi"))

    # 05 süs olarak da: çubukta asılı altı figür
    fon = fon_rengi(CEKIM)
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;overflow:hidden;background:{fon}">
      <img src="{K.uri(CEKIM, 2000)}" style="position:absolute;left:-205px;top:236px;width:1500px;
        -webkit-mask-image:linear-gradient(180deg,transparent 0,#000 12%,#000 88%,transparent 100%)">
      <div style="position:absolute;left:64px;top:56px">{K.logo("acik", 260, 52)}</div>{rozet(64, 56)}
      <div style="position:absolute;left:64px;right:64px;bottom:64px;color:{INK}">
        <p class="k">HEDİYELİK SET</p>
        <h2 class="u" style="margin-top:12px;font-size:46px;line-height:1.08">Anahtarlığa takın,<br>ağaca asın,
          hediye edin.</h2></div></div>""", name(5, "susleme"))

    # 06 ölçü ve özellikler: önden görünüşler gerçek oranlarıyla
    tmp = os.path.join(OUT, "_on")
    os.makedirs(tmp)
    px = 4.6
    cells = ""
    for k in YM.KEYS:
        w, d, h = olcu(k)
        p = os.path.join(tmp, f"{k}.png")
        on_gorunus(k, p)
        cells += f"""<div style="display:flex;flex-direction:column;align-items:center;gap:12px">
          <img src="{K.uri(p, 500, 'PNG')}" style="width:{w * px:.0f}px;height:{h * px:.0f}px;display:block;
            filter:drop-shadow(0 6px 10px rgba(0,0,0,.16))">
          <p style="font-size:16px;font-weight:700;color:#55575c;text-align:center">{YM.AD[k]}<br>
            <span style="font-weight:500">{h:.0f} × {w:.0f} mm</span></p></div>"""
    feats = "".join(f"""<li style="display:flex;gap:12px"><b style="color:{ORANGE}">—</b><span><b>{a}.</b> {b}</span>
      </li>""" for a, b in OZELLIK)
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:{PAPER};padding:56px 56px;
      color:{INK}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <div><p class="k">ÖLÇÜ VE ÖZELLİKLER</p>
        <h2 class="u" style="margin-top:12px;font-size:44px;line-height:1.08">Avuç içi kadar,<br>her yönden tombul.</h2>
        </div>{K.logo("acik", 220, 44)}</div>
      <div style="margin-top:40px;display:flex;justify-content:space-between;align-items:flex-end">{cells}</div>
      <p style="margin-top:10px;font-size:15px;color:{GRAY}">Önden görünüş, gerçek oranlarıyla (boy × en; kalınlık
        ~23 mm). Halka takımı hariç.</p>
      <ul style="margin-top:30px;list-style:none;display:grid;gap:14px;font-size:23px;line-height:1.35">{feats}</ul>
      </div>""", name(6, "olcu_ozellik"))
    shutil.rmtree(tmp)

    # 07 nasıl sipariş verilir
    rows = "".join(f"""<div style="display:flex;gap:28px;padding:18px 0;border-top:2px solid rgba(244,241,234,.14)">
      <b class="u" style="font-size:44px;color:{ORANGE};width:90px">{a}</b><div><p style="font-size:32px;
      font-weight:700">{b}</p><p style="margin-top:8px;font-size:23px;color:rgba(244,241,234,.72)">{c}</p></div>
      </div>""" for a, b, c in ADIM)
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:{INK};color:{PAPER};padding:64px;
      background-image:{BM.stripes_bg(PAPER, .035, 30)}">
      <p class="k">NASIL SİPARİŞ VERİLİR</p>{rozet(64, 56)}
      <h2 class="u" style="margin-top:12px;font-size:48px;line-height:1.1">Sepete ekleyin;<br>gerisi bizde.</h2>
      <div style="margin-top:34px">{rows}</div>
      <img src="{foto('set', 1600)}" style="margin-top:18px;width:100%;height:290px;object-fit:cover;
        object-position:50% 40%;border-radius:22px;display:block">
      <div style="position:absolute;left:64px;bottom:50px">{K.logo("koyu", 300, 60)}</div>
      <p style="position:absolute;right:64px;bottom:60px;font-size:26px;font-weight:700">{K.TEL}</p></div>""",
         name(7, "nasil_siparis"))
    with open(os.path.join(OUT, "aciklama.txt"), "w", encoding="utf-8") as f:
        f.write(ACIKLAMA + "\n")
    return OUT


def main():
    with BM.painter() as P:
        out = shopier(P)
    print(f"{os.path.relpath(out, YM.KOK)}: {len(os.listdir(out))} görsel")


if __name__ == "__main__":
    main()
