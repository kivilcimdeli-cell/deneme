"""BOYDE LABS – Türk bayraklı masa isimliği (çapraz blok + sehpa): Shopier ürün kimliği.

Fırat Tuygun için basılan çapraz blok (masa_isimligi/, scripts/capraz_blok_sehpa.py) Shopier'de ürün olarak satılır.
Üzerinde "AD SOYAD" yazar (kullanıcı: "ad soyad yazsın ürünün üzerinde"); gerçek kişinin adı pazarlamada kullanılmaz.
Blok 12° eğik sehpasına oturmuş hâliyle çizilir; fotoğraflar ve çerçeve diğer BOYDE ürünleriyle aynı
(scripts/boyde_urun_foto.py, scripts/boyde_katalog.py).

Çıktı : boyde_labs/urunler/kaynak/bayrakli.npz (git'e girmez), bayrakli_duz.png (bloğun karşıdan görünüşü)
        boyde_labs/urunler/fotograf/bayrakli_<görünüş>.jpg (studyo, on, masa, detay)
        boyde_labs/urunler/shopier/bayrakli/ (1200 × 1200 JPG, yükleme sırasıyla 01_… 07_…)
Metin : boyde_labs/urunler/shopier/urun_metinleri.md (3. ürün)

Kullanım:
  python3 scripts/bayrakli_isimlik_shopier.py             # model (npz, düz görünüş)
  python3 scripts/bayrakli_isimlik_shopier.py --foto      # Blender fotoğrafları (bpy 4.2)
  python3 scripts/bayrakli_isimlik_shopier.py --shopier   # Shopier görselleri
"""
import json
import math
import os
import shutil
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402

KEY = "bayrakli"
AD = "AD SOYAD"
OUT = os.path.join(A.ROOT, "boyde_labs", "urunler")
SRC = os.path.join(OUT, "kaynak")
FOTO = os.path.join(OUT, "fotograf")
SHOPIER = os.path.join(OUT, "shopier", KEY)
RGB = {A.BLACK: (30, 31, 35), A.WHITE: (238, 238, 233), A.RED: (227, 10, 23)}   # bayrak kırmızısı #E30A17
# fotoğrafta: AgX parlak kırmızıyı somona açar; koyu ve doygun kırmızıyla çizilir, ardından kırmızılar doyurulur
FOTO_RGB = {**RGB, A.RED: (165, 0, 10)}
DOYGUNLUK = 0.3


def model():
    """Blok (adıyla) sehpasında, 12° arkaya eğik (masa_isimligi_yeni.y7 gibi); ön yüz −y'ye bakar, mm."""
    import capraz_blok as CB
    import masa_isimligi_yeni as Y
    CB.NAME = AD
    block = CB.Block()
    base, h_f = Y.block_stand(CB.D)
    parts = [(n, Y.tilted(CB.standing(m), Y.BLOCK_TILT, h_f, 0.0), e) for n, m, e in block.flat_parts()]
    return block, parts + [("Sehpa", base, A.BLACK)]


def export():
    import capraz_blok as CB
    from cift_tarafli_isimlik import render, rotation
    block, parts = model()
    arrays = {}
    for i, (_, man, _) in enumerate(parts):
        V, T = A.mesh_arrays(man)
        arrays[f"v{i}"], arrays[f"f{i}"] = V.astype(np.float32), T.astype(np.int32)
    meta = [{"ad": n, "renk": list(FOTO_RGB[e]), "metal": False, "panel": n != "Sehpa"} for n, _, e in parts]
    os.makedirs(SRC, exist_ok=True)
    np.savez_compressed(os.path.join(SRC, f"{KEY}.npz"), meta=json.dumps(meta, ensure_ascii=False), **arrays)
    front = [(*A.mesh_arrays(CB.standing(m)), RGB[e]) for _, m, e in block.flat_parts()]
    im = render(front, 1600, rotation(0, -90), margin=0.0, ambient=0.6)
    im.crop(im.getbbox()).save(os.path.join(SRC, f"{KEY}_duz.png"), optimize=True)
    print(f"{KEY}: ad {AD!r} {block.cap:.1f} mm, {len(parts)} parça")


def saturate(path, k=DOYGUNLUK):
    """Seçici doygunluk: yalnız kırmızı tonlar (bayrak, alt çizgi) `k` oranında doyar; fon, siyah, beyaz değişmez."""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    h, s, v = [np.asarray(c, float) for c in im.convert("HSV").split()]
    d = np.minimum(h, 256 - h)                           # kırmızıya uzaklık (0..128)
    w = np.clip((14 - d) / 6, 0, 1) * np.clip((s - 60) / 40, 0, 1)
    s = np.clip(s * (1 + k * w), 0, 255)
    bands = [Image.fromarray(x.astype(np.uint8)) for x in (h, s, v)]
    Image.merge("HSV", bands).convert("RGB").save(path, quality=92)


def photos(samples=32):
    """Stüdyo, karşıdan, masa (boyde_urun_foto) ve yakın çekim: bayrak, ayraç, adın başı; arkası bulanık.
    Ürün uzun ve alçak: kadrajda diğerlerinden büyük."""
    import boyde_urun_foto as F
    F.SRC, F.OUT = SRC, FOTO
    F.render(KEY, ["studyo", "on", "masa"], samples, fill=1.18)
    parts = F.load(KEY)
    sc = F.scene("studyo", samples, F.SIZE)
    sc.view_settings.exposure = -0.3
    sc.view_settings.look = F.BAKIS
    box = F.place(parts)
    lo = box.min(0)
    near = box.copy()
    near[:, 0] = np.minimum(near[:, 0], lo[0] + 0.12)    # sol yarı (m)
    cam = F.camera(sc, 100)
    a, e = math.radians(28.0), math.radians(9.0)
    direction = np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])
    cam["dir"] = direction.tolist()
    F.frame(cam, near, 1.0, 0.92)
    cam.data.dof.aperture_fstop = 2.8
    F.lights(sc, near.mean(0), direction, "studyo")
    F.shoot(sc, os.path.join(FOTO, f"{KEY}_detay.jpg"), F.BEYAZ)
    for v in ("studyo", "on", "masa", "detay"):
        saturate(os.path.join(FOTO, f"{KEY}_{v}.jpg"))


# ---------------------------------------------------------------- Shopier (1200 × 1200)

BASLIK = "Türk bayraklı masa isimliği"
OLCU = "240 × 56 mm"
KARELER = [  # (görünüş, başlık, alt satır)
    ("studyo", BASLIK, "Adınız soyadınızla · 12° eğik sehpa dahil"),
    ("on", "Adınız soyadınız, büyük ve okunaklı", "Ay yıldız ve ad soyad 2 mm kabartma"),
    ("masa", "Makam masanıza yakışır", f"Blok {OLCU} · siyah sehpa 200 mm"),
    ("detay", "Kabartma ay yıldız", "Bayrak kırmızısı, siyah ve beyaz: 3 renk 3D baskı"),
]
OZELLIK = ["Blok 240 × 56 × 32 mm; sehpa 200 mm, 12° arkaya eğik",
           "Ay yıldız ve ad soyad 2 mm kabartma",
           "3 renk: bayrak kırmızısı, siyah, beyaz",
           "Ad soyad tek satırda, büyük harf; uzun adlar sığacak kadar küçülür",
           "Tutkal yok: blok sehpaya oturur, arkadaki duvara yaslanır"]
ADIMLAR = [("01", "Sipariş verin", "Shopier'dan adedi seçin, ödemeyi güvenle yapın."),
           ("02", "Adınızı yazın", "Ad soyadı sipariş notuna ya da WhatsApp'tan yazın."),
           ("03", "Önizlemeyi onaylayın", "Adınızla hazırladığımız görseli gönderiyoruz."),
           ("04", "Basıp gönderiyoruz", "3D basıp özenle paketleyip kargoya veriyoruz.")]


def shopier():
    import boyde_katalog as K
    import boyde_marka as BM
    INK, PAPER, ORANGE = K.INK, K.PAPER, K.ORANGE
    shutil.rmtree(SHOPIER, ignore_errors=True)
    os.makedirs(SHOPIER)
    foto = lambda v, w=1200: K.uri(os.path.join(FOTO, f"{KEY}_{v}.jpg"), w)  # noqa: E731
    out = lambda i, s: os.path.join(SHOPIER, f"{i:02d}_{s}.jpg")              # noqa: E731
    with BM.painter() as P:
        # kapak: beyaz fonda koyu yazı (katalogdaki kategori kapağı gibi)
        K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:#fff">
          <img src="{foto('studyo')}" style="width:1200px;height:1200px;display:block">
          <div style="position:absolute;left:64px;top:56px">{K.logo("acik", 330, 66)}</div>
          <div style="position:absolute;left:64px;right:64px;bottom:64px;color:{INK}">
            <p class="k">{OLCU.upper()} · SEHPA DAHİL · KİŞİYE ÖZEL</p>
            <h1 class="u" style="margin-top:14px;font-size:72px;line-height:1.04;letter-spacing:-.02em">Türk bayraklı<br>
              masa isimliği</h1>
            <p style="margin-top:18px;font-size:30px;line-height:1.35;color:#3b3d42">Adınız soyadınız kabartma,
              3 renk 3D baskı.</p></div></div>""", out(1, "kapak"))

        # fotoğraflar: BOYDE çerçevesi (boyde_katalog.framed ile aynı; kod yerine TR)
        for i, (view, t1, t2) in enumerate(KARELER, 2):
            K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;overflow:hidden">
              <img src="{foto(view)}" style="position:absolute;inset:0;width:100%;height:100%;display:block">
              <div style="position:absolute;left:44px;top:40px">{K.logo("acik", 260, 58)}</div>
              <span style="position:absolute;right:44px;top:44px;font-size:15px;font-weight:700;letter-spacing:.2em;
                color:{INK};opacity:.75">{OLCU.upper()}</span>
              <div style="position:absolute;left:28px;right:28px;bottom:28px;display:flex;align-items:center;gap:22px;
                padding:18px 26px 18px 18px;border-radius:26px;background:rgba(255,255,255,.62);
                backdrop-filter:blur(22px) saturate(1.3);box-shadow:inset 0 0 0 1.5px rgba(18,19,22,.08);color:{INK}">
                <span class="code" style="flex:none;display:grid;place-items:center;width:84px;height:84px;
                  border-radius:18px;background:{ORANGE};color:#fff;font-size:26px">TR</span>
                <div style="flex:1;min-width:0">
                  <p class="u" style="font-size:27px;line-height:1.15;white-space:nowrap;overflow:hidden;
                    text-overflow:ellipsis">{t1}</p>
                  <p style="margin-top:7px;font-size:18px;color:#55575c;white-space:nowrap;overflow:hidden;
                    text-overflow:ellipsis">{t2}</p></div>
                <p style="flex:none;text-align:right;font-size:14px;font-weight:700;letter-spacing:.14em;
                  line-height:1.5;color:#55575c">TASARIM VE<br>3D BASKI <b style="color:{ORANGE}">BOYDE</b></p></div>
              </div>""", out(i, view))

        # ölçü ve özellikler (boyde_katalog'daki gibi)
        iw = 900
        duz = K.uri(os.path.join(SRC, f"{KEY}_duz.png"), 1400, "PNG")
        feats = "".join(f'<li style="display:flex;gap:14px;align-items:flex-start"><b style="color:{ORANGE}">—</b>'
                        f"<span>{f}</span></li>" for f in OZELLIK)
        K.sq(P, f"""<div style="width:1200px;height:1200px;background:{PAPER};padding:64px">
          <p class="k">ÖLÇÜ VE ÖZELLİKLER</p>
          <h2 class="u" style="margin-top:12px;font-size:56px">{OLCU}</h2>
          <div style="margin-top:70px;display:flex;justify-content:center">
            <div style="position:relative;width:{iw}px">
              <img src="{duz}" style="width:{iw}px;display:block;filter:drop-shadow(0 18px 28px rgba(0,0,0,.18))">
              <div style="position:absolute;left:0;right:0;top:-30px;border-top:2px solid {INK}"></div>
              <span style="position:absolute;left:50%;top:-30px;transform:translate(-50%,-50%);background:{PAPER};
                padding:0 12px;font-weight:700;font-size:24px">240 mm</span>
              <div style="position:absolute;top:0;bottom:0;right:-30px;border-right:2px solid {INK}"></div>
              <span style="position:absolute;right:-30px;top:50%;transform:translate(50%,-50%) rotate(90deg);
                background:{PAPER};padding:0 12px;font-weight:700;font-size:24px">56 mm</span></div></div>
          <ul style="margin-top:70px;list-style:none;display:grid;gap:14px;font-size:27px;line-height:1.35">{feats}</ul>
          <div style="position:absolute;right:64px;bottom:56px">{K.logo("acik", 260, 52)}</div></div>""",
             out(6, "olcu_ozellik"))

        # nasıl sipariş verilir (katalogdaki "nasıl çalışır" gibi)
        rows = "".join(f"""<div style="display:flex;gap:28px;padding:20px 0;border-top:2px solid rgba(244,241,234,.14)">
          <b class="u" style="font-size:44px;color:{ORANGE};width:90px">{a}</b><div><p style="font-size:34px;
          font-weight:700">{b}</p><p style="margin-top:8px;font-size:24px;color:rgba(244,241,234,.72)">{c}</p></div>
          </div>""" for a, b, c in ADIMLAR)
        K.sq(P, f"""<div style="width:1200px;height:1200px;background:{INK};color:{PAPER};padding:64px;
          background-image:{BM.stripes_bg(PAPER, .035, 30)}">
          <p class="k">NASIL SİPARİŞ VERİLİR</p>
          <h2 class="u" style="margin-top:12px;font-size:50px;line-height:1.1">Adınızı yazın,<br>gerisini biz yapalım.</h2>
          <p style="margin-top:22px;font-size:26px;color:rgba(244,241,234,.8)">Her isimlik sipariş üzerine, adınızla
            basılır.</p>
          <div style="margin-top:34px">{rows}</div>
          <img src="{foto('masa', 1100)}" style="margin-top:18px;width:100%;height:170px;object-fit:cover;
            border-radius:22px;display:block">
          <div style="position:absolute;left:64px;bottom:50px">{K.logo("koyu", 300, 60)}</div>
          <p style="position:absolute;right:64px;bottom:60px;font-size:26px;font-weight:700">{K.TEL}</p></div>""",
             out(7, "nasil_siparis"))
    print(f"{os.path.relpath(SHOPIER, A.ROOT)}: {len(os.listdir(SHOPIER))} görsel")


def main():
    args = sys.argv[1:]
    if "--foto" in args:
        photos()
    elif "--shopier" in args:
        shopier()
    else:
        export()


if __name__ == "__main__":
    main()
