"""Güzellik isimliği 10 × 20 (kişi: saç tasarımcısı, nail artist, estetisyen, makeup artist...): 10 tasarımlık
katalog → seçilen kod → X2D 3MF ve dijital kartvizit sayfası.

Tasarımlar atolye/tasarim/guzellik.py'deki 10 düzenden (Shopier'deki K01–K10 örneklerinden genelleştirildi) kişinin
bilgileriyle kurulur: el yazısı ad soyad (bazı düzenlerde büyük harfle), unvan, salon adı, telefon, dalın simgesi,
çiçek, papatya, şakayık, çelenk süsleri. Panel 200 × 100 mm, gövde 5 mm; yazılar ve süsler yüzeyle aynı hizada renkli
dolgu (örneklerdeki gibi: ince el yazıları da basılır), QR beyaz karoda ya da gövdede; sehpa 170 mm gövde renginde.
Katalog guzellik_9x12'deki gibi seçilir ve denetlenir.

Seçilen kodla (kişinin klasöründe):
  cikti/guzellik_10x20_<ad>_<kod>_x2d.3mf  tek takım (panel + sehpa), Bambu standart 0,20 mm, ütüleme ve destek yok;
                                           gövde ve sehpa ana nozulda, dolgu renkleri (üst 4 katman) yardımcıda
  cikti/onizleme.png, cikti/tabla.png
  web/<ad>_site.zip                        dijital kartvizit: 5 güzellik şablonundan (6–10) sıradaki
"""
import os
import re

from .guzellik_9x12 import RENK_ALANLARI, SAYFA_ALANLARI, _DAL

KOD = "guzellik_10x20"
AD = "Güzellik isimliği 10 × 20"
SIMGE = "💅"
ACIKLAMA = ("Saç tasarımcısı, nail artist, estetisyen için 200 × 100 mm kişiye özel isimlik: el yazısı ad, unvan, "
            "salon; yazılar ve çiçekler yüzeyle aynı hizada renkli dolgu, sehpalı. 10 tasarımlık katalog, X2D 3MF ve "
            "dijital kartvizit (5 güzellik şablonundan).")
KATALOG_ADET = 10
OLCU, HARF = "10x20", "K"

ALANLAR = [
    {"ad": "ad_soyad", "etiket": "Ad soyad", "tur": "text", "zorunlu": True, "grup": "İsimlik",
     "ornek": "Aylin Ersoy",
     "ipucu": "Yazıldığı gibi (büyük-küçük harf); el yazısıyla, bazı tasarımlarda büyük harfle."},
    {"ad": "unvan", "etiket": "Unvan / görev", "tur": "text", "ornek": "Saç Tasarımcısı"},
    {"ad": "kurum", "etiket": "Salon / işletme", "tur": "text", "ornek": "Defne Kuaför"},
    {"ad": "telefon", "etiket": "Telefon", "tur": "tel", "zorunlu": True, "ornek": "0532 123 45 67",
     "ipucu": "İsimlikte ve kartvizit sayfasında."},
    {"ad": "eposta", "etiket": "E-posta (sayfada)", "tur": "text", "ornek": "ad@salon.com"},
    {"ad": "dal", "etiket": "Dal (simge)", "tur": "select", "secenekler": _DAL, "varsayilan": "kuafor",
     "zorunlu": True},
    {"ad": "qr_yazi", "etiket": "QR'ın altındaki yazı", "tur": "text", "varsayilan": "RANDEVU"},
] + RENK_ALANLARI + [dict(a, grup="Kartvizit sayfası") if a.get("grup") == "Randevu sayfası" else
                     dict(a, ornek="aylinersoy", ipucu=a["ipucu"].replace("isimlikteki addan", "ad soyaddan"))
                     if a["ad"] == "site_adi" else a for a in SAYFA_ALANLARI] + [
    {"ad": "not", "etiket": "Sipariş notu", "tur": "textarea", "grup": "Kayıt"},
]


def ad(b):
    return " ".join(b["ad_soyad"].split())


def _icerik(is_, b):
    """Döner (Icerik20, sayfa adı, uyarılar). Panel ölçüleri 10 × 20'ye çevrilir."""
    from atolye import site
    from atolye.tasarim import isimlik20 as T
    from atolye.tasarim import ortak as O
    from atolye.urunler.guzellik_9x12 import sayfa_adi
    T.olcu()
    from atolye.tasarim import guzellik as GZ
    uyar = []
    adi = sayfa_adi(b, ad(b), uyar)
    c = T.Icerik20(marka=ad(b), hizmet=" ".join((b.get("unvan") or "").split()), hizmetler=[],
                   telefon=O.telefon_yazisi(b["telefon"]), cagri="", qr_yazi=(b.get("qr_yazi") or "RANDEVU").strip(),
                   simge=GZ.DALLAR.get(b.get("dal"), GZ.DALLAR["genel"])[1], url=site.sayfa_url(adi),
                   kurum=" ".join((b.get("kurum") or "").split()))
    return c, adi, uyar


def katalog(is_):
    from atolye.urunler.guzellik_9x12 import katalog_kur, katalog_sayfalari
    b = is_.bilgiler
    c, _, uyar = _icerik(is_, b)
    liste, renk_uyar = katalog_kur(is_, c, OLCU, HARF, KOD, en_fazla=30)
    if not liste:
        raise SystemExit("Bu bilgilerle baskıya uygun tasarım çıkmadı: unvan ya da salon adını kısaltıp yeniden "
                         "deneyin.")
    giris = (f"{ad(b)} için isimlik önerileri: 20 × 10 cm, yazılar ve çiçekler yüzeyle aynı hizada renkli; QR "
             "telefonla okutunca dijital kartvizit açılır (arama, WhatsApp'tan randevu, Instagram, rehbere kaydet).")
    bilgi = ("Ürün", ["Ölçü 20 × 10 cm, gövde 5 mm, köşeler yuvarlak.",
                      "Ad el yazısıyla; yazılar, simge ve çiçekler yüzeyle aynı hizada renkli dolgu (pürüzsüz yüzey).",
                      "Renkler: pudra, ten rengi, krem, lila, adaçayı, fuşya, beyaz, siyah; mürdüm, moka, gül kurusu, "
                      "rose gold.",
                      "Masa sehpası dahil (gövde renginde): isimlik 15° eğik durur.",
                      "QR dijital kartvizitinizi açar: arama, WhatsApp'tan randevu, Instagram, rehbere kaydet."])
    out = katalog_sayfalari(is_, liste, "Güzellik isimliği 20 × 10", ad(b), giris, bilgi,
                            alt_not="Beğendiğiniz tasarımın kodunu (ör. K03) yazmanız yeterli.")
    out["uyarilar"] = uyar + renk_uyar
    return out


def _plaka(d, key, title):
    """isimlik20.Plaka gibi (panel yüzü yukarı, sehpa önünde, gövde renginde); panel dolgulu (kabartma yok)."""
    from atolye.tasarim import guzellik as GZ
    from atolye.tasarim import isimlik20 as T
    from atolye.tasarim import ortak as O
    from atolye.urunler.guzellik_9x12 import nozullar

    class Plaka(T.Plaka):
        def __init__(self):
            self.key, self.title, self.design = key, title, d
            self.relief, self.relief_h = False, 0.0
            self.panel = GZ.katilar(d)
            self.body = d.palet.govde
            self.module = O.qr_modul(d.qr_entry, d.qr_side)
            self.stand, self.mount = O.B.stand(length=T.SEHPA)
            self.nozzle_map = nozullar(d, [d.palet.govde])        # gövde ve sehpa ana nozulda, dolgular yardımcıda
            self.filament_profiles = {c: O.A.GENERIC_PLA for c in self.nozzle_map}
            self.object_settings = {"enable_support": "0", "ironing_type": "no ironing"}
            self.tower_xy = O.B.TOWER_XY
            self.project_overrides = {"curr_bed_type": "Textured PEI Plate",
                                      "wipe_tower_x": [f"{O.B.TOWER_XY[0]:g}"],
                                      "wipe_tower_y": [f"{O.B.TOWER_XY[1]:g}"]}

    return Plaka()


def uret(is_, secilen):
    import zipfile

    from atolye.tasarim import guzellik as GZ
    from atolye.tasarim import isimlik20 as T
    from atolye.tasarim import ortak as O
    from atolye.urunler.guzellik_9x12 import dilim, kur, sayfa
    from atolye.urunler.kurumsal_10x20 import _musteri_onizleme
    import boyde_isimlik_baski as BI
    A, B = O.A, O.B
    b = is_.bilgiler
    kod = secilen["kod"]
    c, adi, uyar = _icerik(is_, b)
    d = kur(c, secilen["parametreler"], OLCU)
    sorun, _ = GZ.kontrol(d)
    if sorun:
        uyar.append("Baskıya uygunluk: " + "; ".join(sorun))
    uyar += d.uyarilar

    is_.ilerle(10, "3MF yazılıyor")
    plate = _plaka(d, f"guzellik_10x20_{adi}_{kod.lower()}_x2d", f"BOYDE_guzellik_10x20_{adi}_{kod}")
    out = is_.yol("cikti", "x")[:-2]
    template = zipfile.ZipFile(A.TEMPLATE)
    path, _, filaments = A.write_design(plate, {n: template.read(n) for n in template.namelist()}, out)
    parts = plate.solids()
    ok_place, place = T.tabla_kontrol(plate, parts)
    is_.ilerle(30, "QR okunuyor (üstten görünüş ve baskı hatası benzetimi)")
    qr = BI.qr_check(plate, c.url)
    is_.ilerle(40, "Dilimleyici denetimi")
    dx, dy = plate.offset
    g_txt = dilim(plate, path, filaments, lambda cs: cs.translate((dx, dy)), [], round(B.T, 2), out, uyar)
    if not all(qr):
        uyar.append(f"QR denetimi: okundu {qr[0]}, baskı hatası benzetiminde {qr[1]} — önizlemeyi okutun")
    if not ok_place:
        uyar.append("Tabla yerleşimi: " + place)

    is_.ilerle(55, "Önizlemeler çiziliyor")
    p = d.palet
    renk = " · ".join(f"{i + 1} {A.COLOUR_NAMES[f]}" for i, f in enumerate(filaments))
    noz = plate.nozzle_map
    info = [f"Tek takım (panel + sehpa) · panel 200 × 100 mm, {O.AD[p.govde]} gövde 5 mm · yazılar ve süsler yüzeyle "
            f"aynı hizada dolgu (üst {B.INLAY:g} mm) · tasarım {kod} ({d.duzen})",
            f"AMS: {renk} · ana nozul: {O.AD[p.govde]} (gövde, sehpa) · yardımcı nozul: "
            f"{', '.join(O.AD[c] for c in noz if noz[c] == 2)}",
            "Bambu standart 0,20 mm · ütüleme kapalı · destek yok · Textured PEI · panel yüzü yukarı, sehpa önünde",
            f"{g_txt}QR {c.url} {'okunuyor' if all(qr) else 'SORUNLU'} · dolgu yazılarda harf içi ve ara en az "
            f"0,45 mm {'tamam' if not sorun else 'SORUNLU'} · yerleşim {'tamam' if ok_place else 'SORUNLU'}"]
    T.tabla_resmi(plate, parts, os.path.join(out, "tabla.png"), info,
                  f"{O.tr_upper(ad(b))} – GÜZELLİK İSİMLİĞİ 20 × 10 ({kod}) · X2D BASKI DOSYASI")
    _musteri_onizleme(d, plate.panel, os.path.join(out, "onizleme.png"), ad(b),
                      "20 × 10 cm · 5 mm gövde · renkli dolgu yazı ve çiçekler · masa sehpası dahil · BOYDE LABS",
                      ust="GÜZELLİK İSİMLİĞİ 20 × 10")

    is_.ilerle(70, "Kartvizit sayfası hazırlanıyor")
    ek = {}
    if c.kurum:
        ek = {"kurum": c.kurum, "etiket": GZ.buyuk_harf(c.kurum)}
    eposta = (b.get("eposta") or "").strip()
    if eposta:
        if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", eposta):
            ek["eposta"] = eposta
        else:
            uyar.append(f"E-posta geçersiz, sayfaya konmadı: {eposta}")
    site_cikti = sayfa(is_, b, ad(b), ad(b), GZ.buyuk_harf(c.hizmet), d, adi, uyar, ek)
    is_.ilerle(96, "Bitti")
    return {"ciktilar": [{"ad": f"X2D baskı dosyası (3MF, tek takım) · {kod}", "yol": is_.goreli(path), "tur": "3mf"},
                         {"ad": "Müşteri önizlemesi", "yol": is_.goreli(os.path.join(out, "onizleme.png")),
                          "tur": "resim"},
                         {"ad": "Tabla yerleşimi ve kontroller", "yol": is_.goreli(os.path.join(out, "tabla.png")),
                          "tur": "resim"}] + site_cikti,
            "uyarilar": uyar}
