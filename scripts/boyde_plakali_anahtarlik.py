"""BOYDE LABS – kişiye özel plakalı anahtarlık: Türk plakası biçiminde; plaka ve ad soyad kabartma; Shopier görselleri.

Kullanıcının örneği (Bambu Studio, Birleştir.stl, 70 × 22 × 3 mm): siyah çerçeve ve alt şerit, beyaz plaka zemini, solda
TR bandı; plaka yazısı 1,3 mm (Anek Latin SemiBold, 10 mm), ad 1 mm (Arial, 6 mm) kabartma. Ölçüler STL'den alındı.
Kullanıcı: "kırmızı versiyonunda yap TR yazısını": bant kırmızı, TR beyaz. Delik bandın sol üstünde (örnekte kesici
gövde olarak duruyor; birleştirince STL'e çıkmamış).

Katmanlar (baskı yönünde, z mm; arka yüz tablada, düz):
  0–2,0    siyah    çerçeve (2 mm) ve alt şerit (adın zemini)
  0–1,0    beyaz    plaka zemini (çerçevenin 1 mm içinde)
  0–1,2    kırmızı  TR bandı
  1,0–2,3  siyah    plaka yazısı (1,3 mm; DIN benzeri Saira SemiBold)
  1,2–1,9  beyaz    TR
  2,0–3,0  beyaz    ad soyad (Outfit ExtraBold: küçük boyda da harf içi ve İ noktası ≥ 0,7 mm)
Örnek yazılar uydurma (gerçek plaka ya da kişi değil); görsellerde markamız BOYDE LABS.

Çıktı : boyde_labs/anahtarlik_plaka/kaynak/<model>.npz (git'e girmez), <model>_on.png, <model>_arka.png
        boyde_labs/anahtarlik_plaka/fotograf/*.jpg (Blender; --foto)
        boyde_labs/anahtarlik_plaka/shopier/*.jpg (1200 × 1200; --shopier)
Kullanım:
  python3 scripts/boyde_plakali_anahtarlik.py              # modeller, ön ve arka görünüş, ölçüler
  python3 scripts/boyde_plakali_anahtarlik.py --foto       # fotoğraflar (bpy 4.2)
  python3 scripts/boyde_plakali_anahtarlik.py --shopier    # Shopier görselleri
"""
import json
import os
import sys

import manifold3d as m3
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_anahtarlik_toptan as T  # noqa: E402

A, S = T.A, T.S
J = m3.JoinType.Round
S.FONTS.update({"saira6": "Saira-SemiBold.ttf"})
OUT = os.path.join(A.ROOT, "boyde_labs", "anahtarlik_plaka")
SRC = os.path.join(OUT, "kaynak")
FOTO = os.path.join(OUT, "fotograf")

SIYAH, BEYAZ, KIRMIZI = T.U.RGB[A.BLACK], T.U.RGB[A.WHITE], T.U.RGB[5]
W, H, R = 70.0, 22.0, 3.6                         # dış ölçü ve köşe
IC = (2.05, 1.6, 67.95, 20.45)                    # çerçevenin içi
SERIT_UST = 7.8                                   # alt şeridin üstü (adın zemini)
BANT_SAG = 12.1                                   # TR bandının sağ kenarı
DELIK, DELIK_R = (5.0, 17.8), 1.75                # Ø3,5; üstte 2,45, solda 3,25 mm et
Z_GOVDE, Z_ZEMIN, Z_BANT = 2.0, 1.0, 1.2
PLAKA_H, TR_H, AD_H = 1.3, 0.7, 1.0
ORNEK = [("p01", "34 BYD 34", "BOYDE LABS"), ("p02", "06 BYD 06", "ADINIZ SOYADINIZ"),
         ("p03", "35 BYD 35", "İSİM SOYİSİM")]
KAPAK_EK = [("p04", "16 BYD 16", "BOYDE LABS"), ("p05", "07 BYD 07", "ADINIZ SOYADINIZ"),
            ("p06", "01 BYD 01", "İSİM SOYİSİM")]          # yalnız kapakta (altı farklı plaka)


def _ortala(cs, cx, cy):
    b = cs.bounds()
    return cs.translate((cx - (b[0] + b[2]) / 2, cy - (b[1] + b[3]) / 2))


def _yazi(font, s, cap, cx, cy, max_w, tr=0.3):
    return _ortala(S.t(font, s, cap, 0.0, 0.0, "c", tr, max_w), cx, cy)


def tasarla(plaka, ad):
    """Döner [(Manifold, rgb)] (baskı yönünde) ve ölçüler: plaka ve ad yazısının boyu, kırpılan alan."""
    dis = A.rrect(W, H, R, W / 2, H / 2)
    ic = A.rrect(IC[2] - IC[0], IC[3] - IC[1], 2.3, (IC[0] + IC[2]) / 2, (IC[1] + IC[3]) / 2)
    delik = A.circle(DELIK_R, *DELIK)
    ust = ic ^ A.rect(IC[0], SERIT_UST, IC[2], IC[3] + 1)                   # plaka alanı (bant dahil)
    bant = ust ^ A.rect(IC[0] - 1, SERIT_UST, BANT_SAG, IC[3] + 1)
    zemin = ust - bant
    siyah = dis - ust - delik

    plaka_cs = _yazi("saira6", plaka.upper(), 6.5, (BANT_SAG + IC[2]) / 2, (SERIT_UST + IC[3]) / 2,
                     IC[2] - BANT_SAG - 5.0, 0.4)
    tr_cs = _yazi("saira6", "TR", 4.0, (IC[0] + BANT_SAG) / 2, 10.9, BANT_SAG - IC[0] - 2.0, 0.3)
    serit = ((IC[1] + SERIT_UST) / 2, SERIT_UST - IC[1] - 1.3)              # şeridin ortası, yazıya kalan boy
    ad_cs = _yazi("outfit", ad, 4.3, W / 2, serit[0], IC[2] - IC[0] - 4.0, 0.6)
    cap = 4.3
    for _ in range(4):                             # İ noktaları, Ğ işareti şeride sığmazsa ad küçülür
        b = ad_cs.bounds()
        if b[3] - b[1] <= serit[1]:
            break
        cap *= serit[1] / (b[3] - b[1]) * 0.99
        ad_cs = _yazi("outfit", ad, cap, W / 2, serit[0], IC[2] - IC[0] - 4.0, 0.6)
    kirp = (plaka_cs - zemin.offset(-0.8, J)).area() + (ad_cs - (siyah - ust).offset(-0.6, J)).area()

    def kat(cs, z0, z1):
        return cs.extrude(z1 - z0).translate((0, 0, z0))
    parcalar = [(kat(siyah, 0, Z_GOVDE), SIYAH), (kat(zemin - delik, 0, Z_ZEMIN), BEYAZ),
                (kat(bant - delik, 0, Z_BANT), KIRMIZI),
                (kat(plaka_cs, Z_ZEMIN, Z_ZEMIN + PLAKA_H), SIYAH), (kat(tr_cs, Z_BANT, Z_BANT + TR_H), BEYAZ),
                (kat(ad_cs, Z_GOVDE, Z_GOVDE + AD_H), BEYAZ)]
    olcu = {"plaka_boy": plaka_cs.bounds()[3] - plaka_cs.bounds()[1], "ad_boy": ad_cs.bounds()[3] - ad_cs.bounds()[1],
            "kirpilan": kirp, "ince": _ince(ad_cs) + _ince(plaka_cs)}
    return parcalar, olcu


def _ince(cs, en=0.7):
    """Kabartma yazıda en'den ince kalan alan (mm²; 0,15 mm²'den küçük harf köşesi kırıntıları sayılmaz: 0 olmalı)."""
    return sum(p.area() for p in (cs - cs.offset(-en / 2, J).offset(en / 2, J)).decompose() if p.area() > 0.15)


def yon():
    """Asılınca yukarı bakan yön: ağırlık merkezinden (gövdenin ortası) deliğe."""
    d = np.array(DELIK) - np.array([W / 2, H / 2])
    return [float(v) for v in d / np.linalg.norm(d)]


def kaydet(anahtar, parcalar):
    """npz: anahtarlık fotoğraf betiğinin (boyde_anahtarlik_foto) okuduğu biçim."""
    arr = {}
    for i, (man, _) in enumerate(parcalar):
        V, F = A.mesh_arrays(man)
        arr[f"v{i}"], arr[f"f{i}"] = V.astype(np.float32), F.astype(np.int32)
    meta = {"parcalar": [{"renk": list(rgb), "metal": False} for _, rgb in parcalar], "delik": list(DELIK),
            "delik_r": DELIK_R, "kenar_yonu": yon(), "merkez": [W / 2, H / 2], "kalinlik": Z_GOVDE,
            "toplam": Z_GOVDE + AD_H}
    np.savez_compressed(os.path.join(SRC, f"{anahtar}.npz"), meta=json.dumps(meta), **arr)


def gorunus(anahtar, parcalar):
    from cift_tarafli_isimlik import render, rotation
    mesh = [(*A.mesh_arrays(man), rgb) for man, rgb in parcalar]
    for ad, rot in (("on", A.R_TOP), ("arka", rotation(180, 180))):
        im = render(mesh, 1400, rot, margin=0.0, ambient=0.62)
        im.crop(im.getbbox()).save(os.path.join(SRC, f"{anahtar}_{ad}.png"), optimize=True)


def export():
    os.makedirs(SRC, exist_ok=True)
    for anahtar, plaka, ad in ORNEK + KAPAK_EK:
        parcalar, o = tasarla(plaka, ad)
        kaydet(anahtar, parcalar)
        gorunus(anahtar, parcalar)
        print(f"{anahtar} {plaka:10s} {ad:18s} plaka {o['plaka_boy']:.1f} mm, ad {o['ad_boy']:.1f} mm  "
              f"ince<0.7: {o['ince']:.2f} mm²  kırpılan: {o['kirpilan']:.2f} mm²", flush=True)


# ---------------------------------------------------------------- fotoğraf

def bagla():
    """Anahtarlık fotoğraf betiğini (yükleme, sahne, halka takımı) bu klasöre ve örneklere çevirir."""
    T.OUT, T.SRC, T.FOTO, T.KEYS = OUT, SRC, FOTO, [a for a, _, _ in ORNEK]


def masa(dizilis, yol, samples, size, adim=8.0, kaydir=-0.1, takim=()):
    """Masada dizili plakalar: dizilis sıra sıra [(model, ters mi, açı)]; takim: boş halka takımları [(x, y, açı)]
    (dizinin ortasına göre, mm). kaydir: mercek kaydırma (parçalar kadrajda yukarı; Shopier'de alta yazı gelir)."""
    import boyde_anahtarlik_foto as AF
    sc = AF.studio(False, samples, size)
    yuk = {a: AF.load(a) for a in {a for sira in dizilis for a, _, _ in sira}}
    siralar = []
    for sira in dizilis:
        ogeler = []
        for a, ters, aci in sira:
            meta, parts = yuk[a]
            M = AF.flat(meta, aci, 0, 0, ters)
            q = AF.world(parts, M)
            ogeler.append((a, M, q[:, :2].min(0), q[:, :2].max(0)))
        siralar.append(ogeler)
    boylar = [max(hi[1] - lo[1] for _, _, lo, hi in s) for s in siralar]
    y = (sum(boylar) + adim * (len(siralar) - 1)) / 2
    pts = []
    for s, h in zip(siralar, boylar):
        x = -(sum(hi[0] - lo[0] for _, _, lo, hi in s) + adim * (len(s) - 1)) / 2
        for a, M, lo, hi in s:
            M = M.copy()
            M[0, 3] += x - lo[0]
            M[1, 3] += y - h / 2 - (lo[1] + hi[1]) / 2
            pts.append(AF.put(yuk[a][1], M, f"{a}_{len(pts)}"))
            x += hi[0] - lo[0] + adim
        y -= h + adim
    for i, (x, y, aci) in enumerate(takim):
        pts.append(AF.put_wires(AF.loose_set(x, y, aci), f"takim{i}"))
    yap = AF.F.camera

    def kamera(sc, lens=85):
        cam = yap(sc, lens)
        cam.data.shift_y = kaydir
        return cam
    AF.F.camera = kamera
    try:
        AF.shoot(sc, np.vstack(pts), -12, 42, 0.94, 6.3, os.path.join(FOTO, yol), False, lens=70)
    finally:
        AF.F.camera = yap


def fotograflar(args):
    """Her örnek: masada önlü arkalı (iki) ve halka takımında asılı (halka; delik sol üstte, plaka dik asılır);
    kapak: altı farklı plaka önden; uc: üç örnek alt alta."""
    import boyde_anahtarlik_foto as AF
    samples = 32
    if "--ornek" in args:
        samples = int(args[args.index("--ornek") + 1])
    kucuk = "--deneme" in args
    if kucuk:
        AF.F.SIZE = (500, 500)
    os.makedirs(FOTO, exist_ok=True)
    secili = [a for a in args if not a.startswith("-") and not a.isdigit()]
    for a, _, _ in ORNEK:
        if not secili or a in secili:
            AF.model_shots(a, samples)
    if not secili or "kapak" in secili:
        masa([[("p01", False, -4), ("p04", False, 3)], [("p02", False, 3), ("p05", False, -3)],
              [("p03", False, -2), ("p06", False, 4)]], "kapak.jpg", samples, (600, 600) if kucuk else (1600, 1600))
    if not secili or "uc" in secili:
        masa([[("p01", False, -3)], [("p02", False, 2)], [("p03", False, -2)]], "uc.jpg", samples,
             (600, 600) if kucuk else (1600, 1600), adim=7.0, kaydir=0.0)


if __name__ == "__main__":
    args = sys.argv[1:]
    bagla()
    if "--foto" in args:
        fotograflar([a for a in args if a != "--foto"])
    elif "--shopier" in args:
        import boyde_plakali_shopier as PS
        PS.main()
    else:
        export()
