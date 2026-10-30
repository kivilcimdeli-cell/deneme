"""Kurumsal isimlik 10 × 20 (kişinin adı, unvanı, kurumu; QR kartvizit sayfasını açar): 10 düzen.

Yapı BOYDE B07 10 × 20 ve Paloma'nın basılan isimliğiyle aynı (scripts/boyde_isimlik_baski.py, make_10x20):
panel 200 × 100 mm, gövde 5 mm, köşeler R8, yazı ve şekiller 2 mm kabartma, QR yüzeyle aynı hizada dolgu, sehpa
170 × 40 mm gövde renginde (15° eğik). Düzenler boyde_sektor'deki 10 × 20 örneklerden genelleştirildi (avukat, diş,
müşavir, mimar, müdür, psikolog, diyetisyen, danışman, otel) ve B07'den (QR solda).

Önce olcu() çağrılır: panel ölçülerini (I.PW, I.PH) ve gövde kalınlığını (B.T) 10 × 20'ye çevirir (paloma_isimlik_baski
gibi; o modül Windows'ta kurulamayan potrace'a bağlı olduğu için yükü burada). Ölçüler sürecin tamamında değişir:
ürün eklentisi (urunler/kurumsal_10x20.py) bunu kendi alt sürecinde yapar.
"""
import os

import manifold3d as m3

from dataclasses import dataclass

from . import ortak as O
from .isimlik9 import Icerik, _simge, ad_yaz, qr, satir, telefon
from .ortak import A, J, S

X0 = -88.0
UST = 96.0                                            # simgenin üst sınırı (panel 100 mm)
PW, PH, KALINLIK, SEHPA = 200.0, 100.0, 5.0, 170.0    # panel 20 × 10 cm, gövde 5 mm, sehpa 170 mm


def olcu():
    O.I.PW, O.I.PH = PW, PH
    O.B.T = KALINLIK


@dataclass
class Icerik20(Icerik):
    kurum: str = ""
    buyuk: object = False                             # ad: kişi adı gibi (Mehmet Kaya); True: büyük harf
    olcek: float = 1.0                                # adın boy çarpanı (yazılar sığmazsa küçülür)


def guvenli():
    return O.I.outline().offset(-3.0, J) ^ A.rect(-110, 9.5, 110, 110)


def _satirlar(d, ad, metin, x, y, w, align, cap, tr, renk, n=2):
    """Satır sığarsa tek, sığmazsa kelimelerden en çok n satır (uzun unvan, kurum adı). Döner alt kenar."""
    f = S.font(O.SATIR)
    maddeler = [m.strip() for m in metin.split("·") if m.strip()]
    if len(maddeler) > 1 and O.maddeleri_diz(maddeler, cap, w, 1, tr=min(tr, 1.2)) == [maddeler]:
        cs = O.madde_satiri(maddeler, cap, x, 0.0, align, min(tr, 1.2), w)    # orta nokta kabartmada küçük: yuvarlak
        b = cs.bounds()
        d.add(ad, cs.translate((0.0, y - b[3])), renk)
        return y - (b[3] - b[1])
    metin = " ".join(maddeler)
    if f.width(metin, O.MIN_BOY, min(tr, 0.5)) * 1.03 <= w:
        return satir(d, ad, metin, x, y, cap, w, align, tr, renk)
    tr = min(tr, 1.0)                                  # çok satırda harf aralığı daralır
    lines, cur = [], ""
    for wd in metin.split():
        t = f"{cur} {wd}".strip()
        if cur and f.width(t, cap, tr) * 1.03 > w:
            lines.append(cur)
            cur = wd
        else:
            cur = t
    lines.append(cur)
    if len(lines) > n:
        d.uyarilar.append(f"'{metin}' tamamı sığmadı")
        d.zayif.append("yazı eksik")
        lines = lines[:n]
    for i, line in enumerate(lines):
        y = satir(d, f"{ad} {i + 1}" if i else ad, line, x, y, cap, w, align, tr, renk) - 1.8
    return y + 1.8


def _kurum(d, c, p, x, y, w, align="l", renk=None, cap=4.8, tr=1.4):
    if not c.kurum:
        return y
    return _satirlar(d, "kurum", O.tr_upper(c.kurum), x, y, w, align, cap, tr, renk if renk is not None else p.yazi)


def _unvan(d, c, p, x, y, w, align="l", cap=5.6, tr=1.8):
    if not c.hizmet:
        return y
    return _satirlar(d, "unvan", O.tr_upper(c.hizmet), x, y, w, align, cap, tr, p.vurgu, n=3)


# ---------------------------------------------------------------- düzenler (x −88..88, y ~12..94)

def l_klasik(d, c, p, k):
    """Solda simge, yanında ad, unvan, çizgi, kurum; altta telefon; QR sağda (avukat)."""
    ib = _simge(d, c, p, X0, 58.0, 24.0, 32.0, hiza="l", ust=UST)
    x = ib[2] + 7.0
    w = 40.0 - x
    _, y, _ = ad_yaz(d, c, p, k, x, 88.0, 14.0, w, "l", 0.1, min_cap=9.0, cap2=10.5)
    y = _unvan(d, c, p, x, y - 4.0, w)
    d.add(None, O.bar(x, x + 34.0, y - 4.6, 1.4), p.vurgu)
    _kurum(d, c, p, x, y - 9.4, w)
    telefon(d, c, p, x, 21.0, 6.0, max_w=w)
    qr(d, c, p, 66.0, 56.0, 40.0)


def l_blok(d, c, p, k):
    """Solda renkli blok: içinden oyma simge ve kurum; yanında ad, unvan, telefon; QR sağda (diş kliniği)."""
    cx = -69.0
    block = A.rrect(40.0, 80.0, 5.0, cx, 53.0)
    icon = _simge(d, c, p, cx, 74.0, 26.0, 24.0, oyma=True, ust=88.0)
    cuts, y = [], icon.bounds()[1] - 4.0
    for r in O.maddeleri_diz(O.tr_upper(c.kurum).split(), 4.6, 32.0, 3, tr=0.8) if c.kurum else []:
        cs = O.oyma(O.SATIR, " ".join(r), 4.6, cx, 0.0, "c", 0.8, 32.0, min_cap=O.MIN_BOY)
        b = cs.bounds()
        cs = cs.translate((0.0, y - b[3]))
        if cs.bounds()[1] < 18.0:
            break
        cuts.append(cs)
        y = cs.bounds()[1] - 2.4
    if cuts:
        d.lines["blok yazısı"] = A.union(*cuts)
    d.add(None, block - A.union(icon, *cuts).offset(0.0, J), p.vurgu)
    x = -42.0
    w = 40.0 - x
    _, y, _ = ad_yaz(d, c, p, k, x, 86.0, 12.5, w, "l", 0.0, min_cap=9.0, cap2=11.0)
    _unvan(d, c, p, x, y - 4.6, w, cap=6.2, tr=1.4)
    telefon(d, c, p, x, 24.0, 5.6, max_w=w)
    qr(d, c, p, 66.0, 56.0, 40.0)


def l_monogram(d, c, p, k):
    """Sol üstte baş harf karesi (logo varsa logo), yanında ad ve unvan; boydan çizgi; kurum ve telefon; QR sağda
    (müşavir)."""
    cm = c if c.simge == "logo" else Icerik20(**{**c.__dict__, "simge": "monogram"})
    ib = _simge(d, cm, p, X0, 76.0, 28.0, 28.0, hiza="l", ust=UST)
    x = ib[2] + 6.0
    w = 40.0 - x
    _, y, _ = ad_yaz(d, c, p, k, x, 89.0, 13.5, w, "l", 0.0, min_cap=9.0, cap2=10.0)
    y = _unvan(d, c, p, x, y - 4.0, w, cap=5.6, tr=1.2)
    y = min(y, ib[1]) - 5.0
    d.add(None, O.bar(X0, 38.0, y, 1.4), p.vurgu)
    y = _kurum(d, c, p, X0, y - 5.0, 126.0)
    telefon(d, c, p, X0, 22.0, 6.0, max_w=126.0)
    qr(d, c, p, 66.0, 50.0, 38.0)


def l_buyuk(d, c, p, k):
    """Üstte simge ve uzun çizgi; büyük harflerle geniş ad; unvan, kurum, telefon; QR sağda (mimar)."""
    ib = _simge(d, c, p, X0, 84.0, 22.0, 16.0, hiza="l", ust=UST)
    d.add(None, O.bar(ib[2] + 5.0, 36.0, (ib[1] + ib[3]) / 2, 1.4), p.vurgu)
    _, y, _ = ad_yaz(d, c, p, k, X0, ib[1] - 6.0, 13.0, 126.0, "l", 0.6, min_cap=8.0, cap2=9.5)
    y = _unvan(d, c, p, X0, y - 4.4, 126.0, cap=6.0, tr=2.4)
    y = _kurum(d, c, p, X0, y - 4.0, 126.0, cap=4.6, tr=1.0)
    telefon(d, c, p, X0, 22.0, 5.6, max_w=126.0)
    qr(d, c, p, 66.0, 54.0, 40.0)


def l_alt_bant(d, c, p, k):
    """Altta boydan bant: içinden oyma simge, kurum ve telefon; üstte büyük ad, unvan, kısa çizgi; QR sağ üstte
    (müdür)."""
    band = A.rrect(184.0, 21.0, 4.0, 0.0, 23.5)
    icon = _simge(d, c, p, -82.0, 23.5, 14.0, 12.0, oyma=True, hiza="l")
    cuts = [icon]
    yazilar = []
    tel_x0 = 84.0
    if c.telefon:
        tel = O.oyma(O.SATIR, c.telefon, 5.2, 84.0, 23.5, "r", 0.8, 70.0, min_cap=O.MIN_BOY)
        yazilar.append(tel)
        tel_x0 = tel.bounds()[0]
    if c.kurum:
        x = icon.bounds()[2] + 4.0
        w = tel_x0 - 6.0 - x
        rows = O.maddeleri_diz(O.tr_upper(c.kurum).split(), 4.6, w, 3, tr=1.0)
        if len(rows) > 2 or not rows:
            d.uyarilar.append("kurum adı banda sığmadı")
            d.zayif.append("kurum yok")
            rows = []
        for i, r in enumerate(rows):
            yc = 23.5 + (len(rows) - 1) * 4.1 - i * 8.2               # Ü'nün noktası üst satıra değmesin
            yazilar.append(O.oyma(O.SATIR, " ".join(r), 4.6 if len(rows) > 1 else 5.0, x, yc, "l",
                                  1.0 if len(rows) > 1 else 2.4, w, min_cap=O.MIN_BOY))
    if yazilar:
        d.lines["bant yazısı"] = A.union(*yazilar)
    d.add(None, band - A.union(*cuts, *yazilar).offset(0.0, J), p.yazi)
    _, y, _ = ad_yaz(d, c, p, k, -86.0, 88.0, 14.0, 131.0, "l", 0.0, min_cap=9.0, cap2=10.5)
    y = _unvan(d, c, p, -86.0, y - 4.6, 131.0, cap=7.0, tr=1.2)
    d.add(None, O.bar(-86.0, -56.0, y - 4.0, 1.6), p.vurgu)
    qr(d, c, p, 68.0, 65.0, 34.0)


def l_cerceve(d, c, p, k):
    """Simge üstte solda, zarif ad, unvan, kurum, telefon; QR renkli çerçeveli (psikolog)."""
    ib = _simge(d, c, p, X0 + 2.0, 83.0, 22.0, 15.0, hiza="l", ust=UST)
    _, y, _ = ad_yaz(d, c, p, k, -86.0, ib[1] - 5.0, 15.0, 126.0, "l", 0.1, min_cap=9.5, cap2=11.0)
    y = _unvan(d, c, p, -86.0, y - 4.4, 126.0, cap=6.0, tr=1.2)
    y = _kurum(d, c, p, -86.0, y - 4.0, 126.0, cap=4.6, tr=1.2)
    telefon(d, c, p, -86.0, 21.0, 5.4, max_w=126.0)
    qr(d, c, p, 66.0, 58.0, 36.0, cerceve=True, tr=1.6)


def l_cizgi(d, c, p, k):
    """Solda boydan ince renkli çizgi; simge, ad, unvan, kurum, telefon; QR sağda (diyetisyen)."""
    d.add(None, A.rrect(3.0, 72.0, 1.5, -90.0, 54.0), p.vurgu)
    x = -82.0
    ib = _simge(d, c, p, x, 82.0, 22.0, 14.0, hiza="l", ust=UST)
    _, y, _ = ad_yaz(d, c, p, k, x, ib[1] - 4.5, 13.0, 122.0, "l", 0.0, min_cap=9.0, cap2=10.0)
    y = _unvan(d, c, p, x, y - 4.4, 122.0, cap=6.6, tr=1.0)
    y = _kurum(d, c, p, x, y - 4.0, 122.0, cap=4.6, tr=0.8)
    telefon(d, c, p, x, 21.0, 5.4, max_w=122.0)
    qr(d, c, p, 66.0, 57.0, 38.0)


def l_ust_bant(d, c, p, k):
    """Üstte boydan renkli bant: içinden oyma simge ve kurum (yoksa unvan); altında ad, unvan, telefon; QR sağ altta
    (danışman)."""
    band = A.rrect(184.0, 22.0, 4.0, 0.0, 82.0)
    icon = _simge(d, c, p, -86.0, 81.5, 16.0, 14.0, oyma=True, hiza="l")
    x = icon.bounds()[2] + 5.0
    bant = c.kurum or c.hizmet
    yazilar = [O.oyma("mont", O.tr_upper(bant), 7.4, x, 82.0, "l", 0.8, 86.0 - x, min_cap=O.MIN_BOY)] if bant else []
    if yazilar:
        d.lines["bant yazısı"] = yazilar[0]
    d.add(None, band - A.union(icon, *yazilar).offset(0.0, J), p.vurgu)
    _, y, _ = ad_yaz(d, c, p, k, -86.0, 64.0, 12.5, 131.0, "l", 0.2, min_cap=9.0, cap2=10.0)
    if c.kurum:
        y = _unvan(d, c, p, -86.0, y - 4.4, 131.0, cap=6.0, tr=1.0)
    telefon(d, c, p, -86.0, 24.0, 6.0, max_w=131.0)
    qr(d, c, p, 68.0, 45.0, 34.0)


def l_zarif(d, c, p, k):
    """Üstte küçük simge, zarif büyük ad, unvan, kısa çizgi, harf aralıklı kurum, telefon; QR çerçeveli (otel)."""
    ib = _simge(d, c, p, -86.0, 86.0, 26.0, 11.0, hiza="l", ust=UST)
    _, y, _ = ad_yaz(d, c, p, k, -86.0, ib[1] - 4.0, 14.0, 126.0, "l", 0.1, min_cap=9.5, cap2=11.0)
    y = _unvan(d, c, p, -86.0, y - 4.4, 126.0, cap=6.0, tr=1.2)
    d.add(None, O.bar(-86.0, -56.0, y - 4.0, 1.4), p.vurgu)
    y = _kurum(d, c, p, -86.0, y - 8.4, 126.0, cap=5.0, tr=2.4)
    telefon(d, c, p, -86.0, 21.0, 5.2, max_w=126.0)
    qr(d, c, p, 66.0, 60.0, 34.0, cerceve=True, tr=1.6)


def l_qr_solda(d, c, p, k):
    """QR solda, altında yazı; sağda simge, ad, unvan, kurum, telefon (B07)."""
    qr(d, c, p, -64.0, 56.0, 40.0)
    x = -34.0
    ib = _simge(d, c, p, x, 84.0, 24.0, 16.0, hiza="l", ust=UST)
    _, y, _ = ad_yaz(d, c, p, k, x, ib[1] - 4.5, 14.0, 126.0, "l", 0.0, min_cap=9.0, cap2=10.5)
    y = _unvan(d, c, p, x, y - 4.4, 126.0, cap=6.0, tr=1.4)
    y = _kurum(d, c, p, x, y - 4.0, 126.0, cap=4.8, tr=1.0)
    telefon(d, c, p, x, 21.0, 5.6, max_w=126.0)


def l_ortali(d, c, p, k):
    """Solda ortalı sütun: simge, ad, unvan, kısa çizgi, kurum, telefon; QR sağda."""
    cx, w = -24.0, 126.0
    ib = _simge(d, c, p, cx, 86.0, 26.0, 13.0, ust=UST)
    _, y, _ = ad_yaz(d, c, p, k, cx, ib[1] - 4.0, 14.0, w, "c", 0.1, min_cap=9.0, cap2=10.5)
    y = _unvan(d, c, p, cx, y - 4.0, w, "c", cap=5.6, tr=1.6)
    d.add(None, O.bar(cx - 8.0, cx + 8.0, y - 3.6, 1.4), p.vurgu)
    y = _kurum(d, c, p, cx, y - 7.6, w, "c", cap=4.6, tr=1.2)
    telefon(d, c, p, cx, 21.0, 5.4, "c", max_w=w)
    qr(d, c, p, 66.0, 56.0, 40.0)


# anahtar: (ad, kurucu, adın yazı tipleri, ad büyük harfle mi)
DUZENLER = {
    "klasik": ("Klasik", l_klasik, ["lora", "mont6", "playfair"], False),
    "blok": ("Renk blok", l_blok, ["mont6", "outfit", "jost"], False),
    "monogram": ("Monogram", l_monogram, ["mont6", "sora", "lora"], False),
    "buyuk": ("Büyük ad", l_buyuk, ["syne", "mont", "unbounded"], True),
    "alt_bant": ("Alt bant", l_alt_bant, ["mont6", "outfit", "manrope"], False),
    "cerceve": ("Çerçeveli QR", l_cerceve, ["lora", "playfair", "fraunces"], False),
    "cizgi": ("İnce çizgi", l_cizgi, ["mont6", "jost", "outfit"], False),
    "ust_bant": ("Üst bant", l_ust_bant, ["mont", "outfit", "sora"], False),
    "zarif": ("Zarif", l_zarif, ["playfair", "lora", "cinzel"], False),
    "qr_solda": ("QR solda", l_qr_solda, ["outfit", "mont6", "sora"], False),
}


def tasarla(duzen, c, palet, yazi_tipi):
    """Düzeni kurar; yazılar çakışırsa ad küçülerek yeniden (en çok iki kez)."""
    g = guvenli()
    # yazılar çakışırsa sırayla: ad küçülür; telefon isimlikten çıkar (sayfada var); kurum çıkar
    for olcek, tel, kurum in ((1.0, 1, 1), (0.86, 1, 1), (0.74, 1, 1), (0.86, 0, 1), (0.74, 0, 1), (0.74, 0, 0)):
        if (not tel and not c.telefon) or (not kurum and not c.kurum):
            continue
        d = S.Design(duzen, palet.sc)
        d.duzen, d.palet, d.yazi_tipi, d.uyarilar, d.zayif = duzen, palet, yazi_tipi, [], []
        d.ad_oran, d.gosterilen = 1.0, 0
        d.qr_entry = d.qr_side = None
        cc = Icerik20(**{**c.__dict__, "buyuk": DUZENLER[duzen][3], "olcek": olcek,
                         "telefon": c.telefon if tel else "", "kurum": c.kurum if kurum else ""})
        DUZENLER[duzen][1](d, cc, palet, yazi_tipi)
        if not O.sikisik(d, g):
            break
    if c.telefon and not tel:
        d.uyarilar.append("telefon isimliğe sığmadı (sayfada var)")
    if c.kurum and not kurum:
        d.uyarilar.append("kurum adı isimliğe sığmadı")
    d.ad_oran *= olcek * (1.0 if tel or not c.telefon else 0.9) * (1.0 if kurum or not c.kurum else 0.8)
    return d


def kalite(d):
    return d.ad_oran


def kontrol(d):
    return O.olc(d, guvenli())


def ad(d):
    p = d.palet
    return f"{DUZENLER[d.duzen][0]} · {O.AD[p.govde]} zemin, {O.AD[p.yazi]} yazı, {O.AD[p.vurgu]} · {O.YAZI_AD[d.yazi_tipi]}"


def gorunus(parcalar, govde, boy=900, aci=(0, -90), duz=0.85):
    """Sehpasında (170 mm, gövde renginde), önden ya da açıyla: RGBA."""
    from cift_tarafli_isimlik import render, rotation
    stand, (z0, y0) = O.B.stand(length=SEHPA)
    shown = O.B.assembled(parcalar, z0, y0) + [("Sehpa", stand, govde)]
    mesh = [(*A.mesh_arrays(m), O.TON[c]) for _, m, c in shown]
    return render(mesh, boy, rotation(*aci), flat=duz, margin=0.02)


# ---------------------------------------------------------------- tabla (paloma_isimlik_baski.Plate, checks, preview)

class Plaka(O.B.Plate):
    """Tek takım: panel boyuna yatık (yüzü yukarı), sehpa önünde, gövde renginde."""
    instances = [(128.0, 100.0, 0)]

    def __init__(self, d, key, title):
        A_ = O.A
        self.key, self.title, self.design = key, title, d
        self.relief, self.relief_h = True, O.B.RELIEF
        self.panel = S.solids(d)
        self.body = d.palet.govde
        self.module = O.qr_modul(d.qr_entry, d.qr_side)
        self.stand, self.mount = O.B.stand(length=SEHPA)
        p = d.palet
        self.nozzle_map = {p.govde: 1, p.vurgu: 2, p.yazi: 2}         # gövde ve sehpa ana nozulda
        if p.vurgu2:
            self.nozzle_map[p.vurgu2] = 2
        self.filament_profiles = {c: A_.GENERIC_PLA for c in self.nozzle_map}
        self.object_settings = {"enable_support": "0", "ironing_type": "no ironing"}
        self.tower_xy = O.B.TOWER_XY
        self.project_overrides = {"curr_bed_type": "Textured PEI Plate",
                                  "wipe_tower_x": [f"{O.B.TOWER_XY[0]:g}"], "wipe_tower_y": [f"{O.B.TOWER_XY[1]:g}"]}

    def solids(self):
        parts = list(self.panel)
        pb = m3.Manifold.batch_boolean([m for _, m, _ in parts], m3.OpType.Add).bounding_box()
        sb = self.stand.bounding_box()
        st = self.stand.translate(((pb[0] + pb[3]) / 2 - (sb[0] + sb[3]) / 2, pb[1] - O.B.GAP - sb[4], -sb[2]))
        parts.append((f"Sehpa ({O.AD[self.body]})", st, self.body))
        allb = m3.Manifold.batch_boolean([m for _, m, _ in parts], m3.OpType.Add).bounding_box()
        dx, dy = -(allb[0] + allb[3]) / 2, -(allb[1] + allb[4]) / 2
        x, y, _ = self.instances[0]
        self.offset = (dx + x, dy + y)
        return [(n, m.translate((dx, dy, 0)), c) for n, m, c in parts]


def tabla_kontrol(plate, parts):
    """Takım iki nozulun ortak alanında ve tablada; kule Bambu'nun izin verdiği yerde ve parçalardan uzak."""
    from anahtarlik_kurumsal_kucuk import TOWER_MARGIN, X_AUX
    B = O.B
    x, y, _ = plate.instances[0]
    boxes = [(b[0] + x, b[1] + y, b[3] + x, b[4] + y) for b in (m.bounding_box() for _, m, _ in parts)]
    inside = all(b[0] >= X_AUX and b[1] >= 0 and b[2] <= 256 and b[3] <= 256 for b in boxes)
    tx, ty = plate.tower_xy
    lim = 256 - B.TOWER - TOWER_MARGIN - B.TOWER_BRIM
    allowed = TOWER_MARGIN <= tx <= lim and TOWER_MARGIN <= ty <= lim and tx - B.TOWER_BRIM >= X_AUX
    tower = (tx - B.TOWER_BRIM, ty - B.TOWER_BRIM, tx + B.TOWER + B.TOWER_BRIM, ty + B.TOWER + B.TOWER_BRIM)
    sep = lambda a, b: max(b[0] - a[2], a[0] - b[2], b[1] - a[3], a[1] - b[3])  # noqa: E731
    clear = min(sep(tower, b) for b in boxes)
    return inside and allowed and clear >= 5.0, (f"ortak alanda: {inside}, kule Bambu sınırında: {allowed}, "
                                                 f"kule parçalara {clear:.1f} mm")


def tabla_resmi(plate, parts, path, info_lines, title):
    """Tabla, panel (eğik bakış: kabartma görünsün) ve masada sehpada."""
    from PIL import Image, ImageDraw, ImageFont

    from cift_tarafli_isimlik import render, rotation
    A_, B = O.A, O.B
    show = lambda items: [(*A_.mesh_arrays(m), O.TON[c]) for _, m, c in items]  # noqa: E731
    bed = m3.Manifold.cube((256, 256, 0.2)).translate((0, 0, -0.4))
    tx, ty = plate.tower_xy
    tower = m3.Manifold.cube((B.TOWER, B.TOWER, 10.0)).translate((tx, ty, 0))
    on_bed = [(*A_.mesh_arrays(bed), (205, 208, 214)), (*A_.mesh_arrays(tower), (150, 156, 168))]
    on_bed += [(*A_.mesh_arrays(m.translate((x, y, 0))), O.TON[c]) for x, y, _ in plate.instances for _, m, c in parts]
    bed_im = A_.fit_into(render(on_bed, 1000, A_.R_TOP, flat=0.75, margin=0.02), 420, 420)
    face = A_.fit_into(render(show(plate.panel), 1600, rotation(-8, -42), margin=0.02), 560, 420)
    z0, y0 = plate.mount
    stood = B.assembled(plate.panel, z0, y0) + [("s", plate.stand, plate.body)]
    stand_im = A_.fit_into(render(show(stood), 1300, rotation(-28, -62), margin=0.02), 400, 420)
    canvas = Image.new("RGB", (1500, 740), (236, 239, 244))
    dr = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(os.path.join(A_.FONT_DIR, "Outfit-SemiBold.ttf"), 32)
    fs = ImageFont.truetype(os.path.join(A_.FONT_DIR, "Outfit-SemiBold.ttf"), 18)
    boxes = [(bed_im, "Tabla (üstten, gri: prime kulesi)", (30, 200, 480, 700)),
             (face, f"Panel (eğik bakış) {PW:.0f} × {PH:.0f} mm", (500, 200, 1090, 700)),
             (stand_im, "Masada, sehpada", (1110, 200, 1470, 700))]
    for im, label, (x0, y0_, x1, y1) in boxes:
        dr.rounded_rectangle((x0, y0_, x1, y1), 22, fill=(146, 153, 166))
        canvas.paste(im, (x0 + (x1 - x0 - im.width) // 2, y0_ + 30 + (y1 - y0_ - 30 - im.height) // 2), im)
        dr.text((x0 + 16, y0_ + 10), label, fill=(236, 239, 244), font=fs)
    dr.text((30, 18), title, fill=(24, 26, 30), font=f)
    for k, line in enumerate(info_lines):
        dr.text((30, 66 + k * 28), line, fill=(22, 120, 60) if k == len(info_lines) - 1 else (70, 74, 84), font=fs)
    canvas.save(path)
