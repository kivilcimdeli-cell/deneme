"""BOYDE LABS Instagram: yılbaşı anahtarlıkları, 3 kareli kaydırmalı gönderi (yan yana tek görsel, panorama).

Üç karenin üstünden boydan boya tahta çubuk geçer; altı figür çelik halkalarıyla çubuğa asılı. Kaydırdıkça çubuk
kareden kareye devam eder. Figürler kare sınırlarına denk gelmez:
  1. kare: başlık ve Noel Baba · 2. kare: ren geyiği, atkılı ayıcık, kutup ayısı · 3. kare: kardan adam, çam ağacı ve
  sipariş bilgisi.
Çekim ortografik kamerayla (3240 × 1350, mm başına PX piksel): figürlerin yeri yazılarla birebir hizalanır.

Kullanım: python3 scripts/yilbasi_instagram.py --foto   (Blender çekimi)
          python3 scripts/yilbasi_instagram.py          (yazılar ve üç kare)
Çıktı: boyde_labs/instagram/yilbasi/{panorama.jpg, kare_1..3.jpg}
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yilbasi_model as YM  # noqa: E402

OUT = os.path.join(YM.KOK, "boyde_labs", "instagram", "yilbasi")
FOTO = os.path.join(OUT, "_cekim.jpg")
W, H, KARE = 3240, 1350, 1080
PX = 8.5                                           # piksel / mm
CUBUK_Y = 302                                      # çubuğun görüntüdeki yüksekliği (piksel)
CUBUK_R = 3.0                                      # Ø6 mm tahta çubuk
YER = [("noel_baba", 0.70, -8), ("ren_geyigi", 1.22, 10), ("atkili_ayicik", 1.50, -6), ("kutup_ayisi", 1.78, 8),
       ("kardan_adam", 2.24, -10), ("cam_agaci", 2.52, 6)]   # (anahtar, kare birimi cinsinden x, dönüş)


def x_mm(u):
    return (u * KARE - W / 2) / PX


# ---------------------------------------------------------------- çekim (Blender)

def foto(samples=64):
    import bpy
    import boyde_anahtarlik_foto as AF
    import boyde_urun_foto as F
    import restoran_masalik_foto as R

    UP = AF.UP
    face0, side0 = np.array([0.0, -1.0, 0.0]), np.array([1.0, 0.0, 0.0])

    def asili(key, x, yaw):
        """Çelik halka çubukta (halkanın düzlemi çubuğa dik), 3 halkalık zincir, ara halka figürün deliğinde."""
        parts = YM.figur(key)
        c, r_ic, _ = YM.delik(parts)
        top = np.array([x, 0.0, CUBUK_R + AF.RING_W])        # halkanın teli çubuğun üstüne oturur
        psi = math.radians(yaw)
        face = np.array([math.sin(psi), -math.cos(psi), 0.0])
        wires = []
        w, bottom = AF.split_ring(top - UP * AF.RING_R, face0, UP, side0)
        wires.append(w)
        length = AF.LINK_S + 2 * AF.LINK_E
        p = bottom + UP * (AF.RING_W + AF.LINK_W) - UP * length / 2
        for i in range(3):
            wires.append(AF.link(p, UP, side0 if i % 2 == 0 else face0))
            end = p - UP * length / 2
            p = p - UP * (length - 2 * AF.LINK_W)
        jc = end + UP * (AF.LINK_W + AF.JUMP_W) - UP * AF.JUMP_R
        wires.append(AF.jump_ring(jc, UP, face))
        hole_w = jc - UP * AF.JUMP_R - UP * (r_ic - AF.JUMP_W)
        rot = np.array([[math.cos(psi), -math.sin(psi), 0], [math.sin(psi), math.cos(psi), 0], [0, 0, 1]])
        M = np.c_[rot, hole_w - rot @ c]
        return [(V, Fc, rgb, False) for _, V, Fc, rgb, _ in parts], M, wires

    F.VINYET = 0.05                                          # panoramada köşeler az kararsın (kareler eşit)
    sc = AF.studio(False, samples, (W, H))
    groups = []
    for k, (key, u, yaw) in enumerate(YER):
        parts, M, wires = asili(key, x_mm(u), yaw)
        groups += [AF.put(parts, M, f"figur{k}"), AF.put_wires(wires, f"halka{k}")]
    # tahta çubuk: karelerin dışına taşar
    n = 200
    xs = np.linspace(-W / PX, W / PX, n)
    path = np.c_[xs, np.zeros(n), np.zeros(n)]
    V, fc = AF.tube(path, np.tile([0.0, 0.0, 1.0], (n, 1)), np.tile([0.0, 1.0, 0.0], (n, 1)), CUBUK_R, seg=32)
    tahta = R.material("tahta", (176, 132, 92), wood=True, layers=False)
    groups.append(AF.add("cubuk", V, fc, tahta, np.c_[np.eye(3), np.zeros(3)], smooth=True))
    pts = np.vstack(groups)
    dz = 0.075 - pts[:, 2].min()
    AF.lift_all(pts, 0.075)                                  # yer kadrajın altında kalsın (fonun kıvrımı görünür)
    cubuk_z = dz                                             # çubuğun ekseni (m)
    cam = F.camera(sc)
    cam.data.type = "ORTHO"
    cam.data.sensor_fit = "HORIZONTAL"
    cam.data.ortho_scale = W / PX * F.MM
    zc = cubuk_z - (H / 2 - CUBUK_Y) / PX * F.MM            # görüntünün ortası
    cam.location = (0.0, -1.0, zc)
    R.look_at(cam, (0.0, 0.0, zc))
    F.lights(sc, np.array([0.0, 0.0, zc]), np.array([0.0, -1.0, 0.08]), "studyo")
    F.shoot(sc, FOTO, F.BEYAZ)
    AF.saturate(FOTO)


# ---------------------------------------------------------------- yazılar ve kareler

def kareler():
    from PIL import Image
    import boyde_katalog as K
    import boyde_marka as BM
    INK, ORANGE = K.INK, K.ORANGE
    etiket = ""
    for key, u, _ in YER:
        etiket += f"""<p style="position:absolute;left:{u * KARE - 150:.0f}px;width:300px;top:1172px;text-align:center;
          font-size:24px;font-weight:700;color:{INK}">{YM.AD[key]}</p>"""
    body = f"""<div style="position:relative;width:{W}px;height:{H}px;overflow:hidden;background:#fff">
      <img src="{K.uri(FOTO, W)}" style="position:absolute;inset:0;width:{W}px;height:{H}px">
      <div style="position:absolute;left:64px;top:44px">{K.logo("acik", 260, 52)}</div>
      <div style="position:absolute;left:64px;top:118px;color:{INK}">
        <p class="k">YENİ · YILBAŞI KOLEKSİYONU</p>
        <h1 class="u" style="margin-top:10px;font-size:54px;line-height:1.0;letter-spacing:-.02em">Yılbaşı<br>
          anahtarlıkları</h1></div>
      <p style="position:absolute;left:64px;top:1246px;width:700px;font-size:26px;line-height:1.35;color:#3b3d42">
        Altı sevimli figür. Kaydırın, hepsini görün <b style="color:{ORANGE}">→</b></p>
      {etiket}
      <div style="position:absolute;left:{KARE + 64}px;right:{KARE + 64}px;top:1236px;text-align:center;color:{INK}">
        <p class="k">TAM 3D · RENKLİ BASKI</p>
        <p style="margin-top:10px;font-size:26px;color:#3b3d42">Önü de arkası da tombul; boya yok, renkler baskıdan.</p>
      </div>
      <div style="position:absolute;left:{2 * KARE + 690}px;top:118px;width:330px;color:{INK}">
        <p class="k">6 MODEL</p>
        <p class="u" style="margin-top:10px;font-size:32px;line-height:1.1">Zincirli halka takımıyla.</p></div>
      <div style="position:absolute;left:{2 * KARE + 64}px;right:64px;top:1236px;display:flex;
        justify-content:space-between;align-items:flex-end;color:{INK}">
        <div><p class="k">SİPARİŞ</p>
          <p style="margin-top:10px;font-size:30px;font-weight:700">DM ya da shopier.com/boyde</p></div>
        <p style="font-size:26px;font-weight:700">{K.TEL}</p></div>
      <div style="position:absolute;right:64px;top:44px">{K.logo("acik", 200, 40)}</div>
    </div>"""
    os.makedirs(OUT, exist_ok=True)
    pano = os.path.join(OUT, "panorama.png")
    with BM.painter() as P:
        P.png(body, W, H, pano, css=K.CSS)
    im = Image.open(pano).convert("RGB")
    im.save(os.path.join(OUT, "panorama.jpg"), quality=92)
    os.remove(pano)
    for i in range(3):
        im.crop((i * KARE, 0, (i + 1) * KARE, H)).save(os.path.join(OUT, f"kare_{i + 1}.jpg"), quality=92)
    print("yazıldı:", OUT)


if __name__ == "__main__":
    if "--foto" in sys.argv:
        os.makedirs(OUT, exist_ok=True)
        foto(int(sys.argv[sys.argv.index("--ornek") + 1]) if "--ornek" in sys.argv else 64)
    else:
        kareler()
