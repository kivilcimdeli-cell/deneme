"""BOYDE LABS – yılbaşı anahtarlıklarının Shopier görselleri (1200 × 1200 JPG). Görsel dil esnaf anahtarlıklarınınki
(boyde_anahtarlik_esnaf_shopier: logo, buzlu cam şerit, turuncu kod).

Önce fotoğraflar: python3 scripts/yilbasi_foto.py (Blender). Sonra: python3 scripts/yilbasi_shopier.py

Yükleme sırasıyla:
  01 kapak (üç figür zincirli halkada) · 02 altı model yan yana · 03–08 modeller tek tek, halka takımıyla ·
  09–14 modeller önü ve arkası (tam 3D) · 15 ölçü ve özellikler · 16 nasıl sipariş verilir
Çıktı: boyde_labs/yilbasi_anahtarlik/shopier/*.jpg
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
ETIKET = "YILBAŞI ANAHTARLIK"
OZELLIK = [("Tam 3D figür", "Önü de arkası da yuvarlak; her yönden sevimli, elde tombul."),
           ("Renkler baskıdan gelir", "Çok renkli 3D baskı; boya yok, solmaz, kazınmaz."),
           ("Avuç içi boyutunda", "Yaklaşık 4–5 cm boy, 2,3 cm kalınlık; hafif PLA."),
           ("Zincirli halka takımı", "Çelik halka, kısa zincir ve ara halka takılı gelir."),
           ("Hediyelik", "Yılbaşı hediyesi, çam süsü ya da çanta süsü olarak.")]
ADIM = [("01", "Modelinizi seçin", "Noel Baba, ren geyiği, ayıcık, kutup ayısı, kardan adam ya da çam ağacı."),
        ("02", "Adedi yazın", "Birden çok alımda modelleri karışık seçebilirsiniz; sipariş notuna yazmanız yeterli."),
        ("03", "Basıp gönderiyoruz", "Kendi atölyemizde basıp halka takımını takıyor, kargoya veriyoruz.")]


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
      <span style="position:absolute;right:44px;top:44px;font-size:15px;font-weight:700;letter-spacing:.2em;
        color:{INK};opacity:.75">{ETIKET}</span>
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


def shopier(P):
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    name = lambda i, s: os.path.join(OUT, f"{i:02d}_{s}.jpg")              # noqa: E731

    # 01 kapak
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:#fff">
      <img src="{foto('kapak')}" style="width:1200px;height:1200px;display:block">
      <div style="position:absolute;left:64px;top:56px">{K.logo("acik", 330, 66)}</div>
      <div style="position:absolute;left:64px;right:64px;bottom:64px;color:{INK}">
        <p class="k">TAM 3D · RENKLİ BASKI · ZİNCİRLİ HALKA</p>
        <h1 class="u" style="margin-top:14px;font-size:76px;line-height:1.02;letter-spacing:-.02em">Yılbaşı<br>
          anahtarlık</h1>
        <p style="margin-top:18px;font-size:30px;line-height:1.35;color:#3b3d42">Noel Baba, ren geyiği, kardan adam ve
          dostları; önü de arkası da tombul.</p></div></div>""", name(1, "kapak"))

    # 02 altı model
    chips = "".join(f'<span class="chip" style="background:#fff;color:{INK};font-size:19px;padding:8px 14px;'
                    f'box-shadow:inset 0 0 0 1.5px rgba(18,19,22,.12)"><b style="color:{ORANGE}">{i + 1:02d}</b>'
                    f'&nbsp;{YM.AD[k]}</span>' for i, k in enumerate(YM.KEYS))
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;overflow:hidden;background:#f6f6f4">
      <img src="{foto('dizi', 1600)}" style="position:absolute;left:-60px;top:50%;width:1320px;
        transform:translateY(-46%)">
      <div style="position:absolute;left:64px;top:56px">{K.logo("acik", 260, 52)}</div>
      <div style="position:absolute;left:64px;right:64px;top:150px;color:{INK}">
        <p class="k">6 MODEL</p>
        <h2 class="u" style="margin-top:12px;font-size:46px;line-height:1.08">Hangisi sizin<br>yılbaşınız?</h2></div>
      <div style="position:absolute;left:64px;right:64px;bottom:60px;display:flex;flex-wrap:wrap;gap:10px">{chips}
      </div></div>""", name(2, "alti_model"))

    # 03–08 tek tek, 09–14 önü ve arkası
    for i, k in enumerate(YM.KEYS):
        w, d, h = olcu(k)
        framed(P, f"{k}_halka", f"{i + 1:02d}", f"{YM.AD[k]} · yılbaşı anahtarlığı",
               f"{h:.0f} × {w:.0f} × {d:.0f} mm · {renkler(k)} · zincirli halka takımıyla",
               name(3 + i, f"{k}_halka"))
    for i, k in enumerate(YM.KEYS):
        framed(P, f"{k}_iki", f"{i + 1:02d}", f"{YM.AD[k]} · önü ve arkası",
               "Tam 3D figür: arkası da yuvarlak, her yönden sevimli", name(9 + i, f"{k}_onu_arkasi"))

    # 15 ölçü ve özellikler: önden görünüşler gerçek oranlarıyla
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
      <ul style="margin-top:34px;list-style:none;display:grid;gap:16px;font-size:24px;line-height:1.35">{feats}</ul>
      </div>""", name(15, "olcu_ozellik"))
    shutil.rmtree(tmp)

    # 16 nasıl sipariş verilir
    rows = "".join(f"""<div style="display:flex;gap:28px;padding:18px 0;border-top:2px solid rgba(244,241,234,.14)">
      <b class="u" style="font-size:44px;color:{ORANGE};width:90px">{a}</b><div><p style="font-size:32px;
      font-weight:700">{b}</p><p style="margin-top:8px;font-size:23px;color:rgba(244,241,234,.72)">{c}</p></div>
      </div>""" for a, b, c in ADIM)
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:{INK};color:{PAPER};padding:64px;
      background-image:{BM.stripes_bg(PAPER, .035, 30)}">
      <p class="k">NASIL SİPARİŞ VERİLİR</p>
      <h2 class="u" style="margin-top:12px;font-size:48px;line-height:1.1">Seçin, sepete ekleyin;<br>gerisi bizde.</h2>
      <div style="margin-top:34px">{rows}</div>
      <img src="{foto('dizi', 1600)}" style="margin-top:18px;width:100%;height:300px;object-fit:cover;
        object-position:50% 62%;border-radius:22px;display:block">
      <div style="position:absolute;left:64px;bottom:50px">{K.logo("koyu", 300, 60)}</div>
      <p style="position:absolute;right:64px;bottom:60px;font-size:26px;font-weight:700">{K.TEL}</p></div>""",
         name(16, "nasil_siparis"))
    return OUT


def main():
    with BM.painter() as P:
        out = shopier(P)
    print(f"{os.path.relpath(out, YM.KOK)}: {len(os.listdir(out))} görsel")


if __name__ == "__main__":
    main()
