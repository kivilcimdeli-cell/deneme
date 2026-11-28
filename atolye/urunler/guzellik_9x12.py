"""Güzellik isimliği 9 × 12 (kuaför, güzellik salonu, tırnak, kirpik, cilt bakım, lazer, makyaj, spa, gelin başı):
10 tasarımlık katalog → müşterinin seçtiği kod → X2D 3MF (iki takım) ve randevu sayfası.

Tasarımlar atolye/tasarim/guzellik.py'deki 10 düzenden (Shopier'deki G01–G10 örneklerinden genelleştirildi) müşterinin
bilgileriyle kurulur: el yazısı ad, iş türü, hizmetler, telefon, dalın simgesi (makas, oje, kirpik, ruj...), çiçek,
papatya, gül, şakayık süsleri. Renkler güzellik paletlerinden (pudra, ten rengi, krem, lila, adaçayı, fuşya, siyah,
beyaz gövde; mürdüm, moka, gül kurusu, rose gold...). Katalogda her düzenden bir tasarım (yenilemede en çok iki), aynı
gövde renginden en çok üç; düzenin kendi paleti ve ilk yazı tipi öne çıkar, öğrenmeye göre sıralanır; bu müşteriye
gösterilenler tekrar edilmez; baskı denetiminden geçemeyen gösterilmez.

Seçilen kodla (isimlik_9x12 gibi):
  cikti/guzellik_<ad>_<kod>_x2d.3mf   tablada iki takım (panel + siyah sehpa), Bambu standart 0,20 mm, ütüleme ve
                                      destek yok; gövde, sehpa, vurgu ve süs ana nozulda, yazı rengi yardımcı nozulda
  cikti/onizleme.png, cikti/tabla.png
  web/<ad>_site.zip                   randevu sayfası: 5 güzellik şablonundan (6–10) sıradaki
"""
import os
import re

KOD = "guzellik_9x12"
KATEGORI = "isimlik"                     # ana sayfadaki kategorisi (urunler.KATEGORILER)
ALT = "Güzellik koleksiyonu"                  # kategori sayfasındaki alt başlığı
AD = "Güzellik isimliği 9 × 12"
SIMGE = "🌸"
ACIKLAMA = ("Kuaför, güzellik salonu, tırnak, kirpik, cilt bakım için 120 × 90 mm QR'lı isimlik: el yazısı ad, çiçek "
            "süsleri, pudra · ten rengi · krem · lila tonları; 2 mm kabartma, sehpalı. 10 tasarımlık katalog, X2D 3MF "
            "ve randevu sayfası (5 güzellik şablonundan).")
KATALOG_ADET = 10
OLCU, HARF = "9x12", "G"
SABLONLAR = [("0", "Sıradaki (otomatik)"), ("6", "6 · Pudra"), ("7", "7 · Şakayık"), ("8", "8 · Gece"),
             ("9", "9 · Kemer"), ("10", "10 · Papatya")]


def secenekler():
    from atolye.tasarim import guzellik as GZ
    from atolye.tasarim import ortak as O
    oto = [("otomatik", "Otomatik (katalogda farklı renkler)")]

    def sec(cs):
        return oto + [(O.AD[c], O.AD[c][:1].upper() + O.AD[c][1:]) for c in cs]
    return [(k, v[0]) for k, v in GZ.DALLAR.items()], sec(GZ.GOVDELER), sec(GZ.YAZILAR), sec(GZ.VURGULAR)


try:
    _DAL, _ZEMIN, _YAZI, _RENK = secenekler()
except Exception:                                      # noqa: BLE001 (tasarım modülleri yüklenemezse form yine açılır)
    _DAL = [("genel", "Genel")]
    _ZEMIN = _YAZI = _RENK = [("otomatik", "Otomatik")]

RENK_ALANLARI = [
    {"ad": "zemin", "etiket": "Gövde rengi", "tur": "select", "secenekler": _ZEMIN, "varsayilan": "otomatik",
     "ipucu": "Otomatik: pudra, ten rengi, krem, lila, adaçayı, fuşya, beyaz ve siyah gövdeler karışık."},
    {"ad": "yazi_renk", "etiket": "Yazı rengi (ad, hizmetler, telefon)", "tur": "select", "secenekler": _YAZI,
     "varsayilan": "otomatik", "ipucu": "QR koyu karelerle beyaz karoda kalır (okunsun diye)."},
    {"ad": "renk", "etiket": "Vurgu rengi (simge, süsler, iş türü)", "tur": "select", "secenekler": _RENK,
     "varsayilan": "otomatik"},
]
SAYFA_ALANLARI = [
    {"ad": "whatsapp", "etiket": "WhatsApp numarası", "tur": "tel", "grup": "Randevu sayfası",
     "ipucu": "Boşsa telefon. Sayfada 'Randevu al' düğmesi."},
    {"ad": "whatsapp_mesaj", "etiket": "WhatsApp hazır mesajı", "tur": "text",
     "varsayilan": "Merhaba, randevu almak istiyorum."},
    {"ad": "instagram", "etiket": "Instagram", "tur": "text", "ornek": "@kullaniciadi"},
    {"ad": "google", "etiket": "Google yorum bağlantısı", "tur": "text", "ornek": "https://g.page/r/…/review"},
    {"ad": "harita", "etiket": "Konum bağlantısı (Haritalar)", "tur": "text", "ornek": "https://maps.app.goo.gl/…"},
    {"ad": "konum", "etiket": "Semt, şehir", "tur": "text", "ornek": "Muratpaşa, Antalya"},
    {"ad": "web", "etiket": "Web sitesi", "tur": "text"},
    {"ad": "aciklama", "etiket": "Sayfadaki kısa tanıtım", "tur": "textarea",
     "ornek": "Saçınız, tırnaklarınız, cildiniz için randevu alın."},
    {"ad": "site_adi", "etiket": "Sayfa adresi (Worker adı)", "tur": "text", "ornek": "defnekuafor",
     "ipucu": "https://<ad>.qrsistem.workers.dev/ · boşsa isimlikteki addan (en çok 20 harf, a-z ve rakam)."},
    {"ad": "sablon", "etiket": "Sayfa şablonu", "tur": "select", "varsayilan": "0", "secenekler": SABLONLAR},
    {"ad": "iban", "etiket": "IBAN", "tur": "text", "grup": "Ödeme bilgileri (sayfada, isteğe bağlı)",
     "ornek": "TR…"},
    {"ad": "iban_alici", "etiket": "Alıcı adı", "tur": "text"},
    {"ad": "banka", "etiket": "Banka", "tur": "text"},
    {"ad": "karekod", "etiket": "Banka karekodu (ekran görüntüsü)", "tur": "dosya", "kabul": "image/*",
     "ipucu": "Bankanın IBAN karekodu: okunup sayfaya eklenir."},
]

ALANLAR = [
    {"ad": "isletme", "etiket": "İşletme adı", "tur": "text", "zorunlu": True, "grup": "İsimlik",
     "ornek": "Defne Kuaför", "ipucu": "Tam adı (sayfada ve kayıtta)."},
    {"ad": "marka", "etiket": "İsimlikte el yazısıyla yazılacak ad", "tur": "text", "ornek": "Defne",
     "ipucu": "Boşsa işletme adından iş türü çıkarılır. Kısa ad (1–2 kelime) en güzel durur."},
    {"ad": "hizmet", "etiket": "İş türü (adın altında)", "tur": "text", "ornek": "BAYAN KUAFÖRÜ"},
    {"ad": "dal", "etiket": "Dal (simge)", "tur": "select", "secenekler": _DAL, "varsayilan": "kuafor",
     "zorunlu": True, "ipucu": "Simge: makas, şakayık, oje, kirpik, ruj, gül, parıltı, nilüfer, taç ya da çiçek."},
    {"ad": "telefon", "etiket": "Telefon", "tur": "tel", "zorunlu": True, "ornek": "0532 123 45 67",
     "ipucu": "İsimlikte ve sayfada (Hemen Ara)."},
    {"ad": "hizmetler", "etiket": "Hizmetler", "tur": "textarea", "ornek": "Kesim, Fön, Boya, Gelin saçı",
     "ipucu": "Virgülle ya da satır satır. İsimliğe sığanlar yazılır (genelde 1–3 madde)."},
    {"ad": "qr_yazi", "etiket": "QR'ın altındaki yazı (kaldırmak için: yok)", "tur": "text", "varsayilan": "RANDEVU"},
] + RENK_ALANLARI + SAYFA_ALANLARI + [
    {"ad": "yetkili", "etiket": "Yetkili", "tur": "text", "grup": "Kayıt (isimliğe ve sayfaya yazılmaz)"},
    {"ad": "yetkili_tel", "etiket": "Yetkilinin telefonu", "tur": "tel"},
    {"ad": "not", "etiket": "Sipariş notu", "tur": "textarea"},
]


def ad(b):
    return " ".join(b["isletme"].split())


# ---------------------------------------------------------------- içerik, adaylar, kurulum (10 × 20 de kullanır)

def sayfa_adi(b, kaynak, uyar):
    from atolye import site
    adi = site.sayfa_adi(b.get("site_adi") or kaynak)
    if b.get("site_adi") and adi != b["site_adi"].strip().lower():
        uyar.append(f"Sayfa adı '{adi}' olarak düzeltildi (yalnız a-z ve rakam, en çok {site.EN_UZUN} harf)")
    return adi


def _icerik(is_, b):
    """Formdan tasarım içeriği. Döner (Icerik, sayfa adı, uyarılar)."""
    from atolye import site
    from atolye.tasarim import guzellik as GZ
    from atolye.tasarim import isimlik9 as T
    from atolye.tasarim import ortak as O
    uyar = []
    isletme = ad(b)
    hizmet = GZ.buyuk_harf((b.get("hizmet") or "").strip())
    marka = " ".join((b.get("marka") or "").split())
    if not marka:
        u = GZ.buyuk_harf(isletme)
        marka = isletme[:len(u) - len(hizmet)].strip() if hizmet and u.endswith(hizmet) and u != hizmet else isletme
    maddeler = [GZ.buyuk_harf(x.strip(" .")) for x in re.split(r"[,;\n·•]+", b.get("hizmetler") or "") if x.strip(" .")]
    adi = sayfa_adi(b, marka, uyar)
    c = T.Icerik(marka=marka, hizmet=hizmet, hizmetler=maddeler, telefon=O.telefon_yazisi(b["telefon"]), cagri="",
                 qr_yazi=O.qr_yazisi(b, "RANDEVU"),
                 simge=GZ.DALLAR.get(b.get("dal"), GZ.DALLAR["genel"])[1], url=site.sayfa_url(adi))
    return c, adi, uyar


def adaylar(b, olcu):
    """[(imza, özellikler, parametreler, ağırlık)] ve renk uyarıları. Düzenin kendi paleti ve ilk yazı tipi öne
    çıkar (örneklerdeki gibi); seçilen renkler her paleti değiştirir."""
    from atolye.tasarim import guzellik as GZ
    from atolye.tasarim import ortak as O
    z, y, v = (O.KIMLIK.get(b.get(k) or "", 0) for k in ("zemin", "yazi_renk", "renk"))
    paletler, uyar = GZ.paletler(z, y, v)
    out = []
    for duzen, (_, _, fonts, kendi) in (GZ.DUZEN9 if olcu == "9x12" else GZ.DUZEN20).items():
        for pad, (g, yy, vv, ss) in paletler.items():
            for i, f in enumerate(fonts):
                oz = {"sablon": duzen, "zemin": O.AD[g], "metin": O.AD[yy], "renk": O.AD[vv], "yazi": f}
                par = {"duzen": duzen, "govde": g, "metin": yy, "vurgu": vv, "sus": ss, "yazi": f}
                w = (1.0 if pad == kendi else 0.15) * (1.0 if i == 0 else 0.6)
                out.append((f"{duzen}|{pad}|{f}|{O.AD[yy]}|{O.AD[vv]}", oz, par, w))
    return out, uyar


def kur(c, par, olcu):
    from atolye.tasarim import guzellik as GZ
    sus = GZ.sus_rengi(par["govde"], par["vurgu"], par.get("sus", 0))
    return GZ.tasarla(olcu, par["duzen"], c, GZ.palet(par["govde"], par["metin"], par["vurgu"], sus), par["yazi"])


def katalog_kur(is_, c, olcu, harf, kod, en_fazla=36):
    """Adaylar sıralanır, kurulur, denetlenir. Döner ([(kod, parametreler, Design, özellikler, imza)], uyarılar)."""
    import random

    from atolye import ogrenme
    from atolye.tasarim import guzellik as GZ
    aday, uyar = adaylar(is_.bilgiler, olcu)
    by = {a[0]: a for a in aday}
    en_cok = 1 if is_.no == 1 else 2                    # ilk katalogda her düzenden bir tasarım

    def uygun(secilen, a):                              # aynı düzenden en_cok, aynı gövde renginden en çok üç
        return (sum(1 for _, oz in secilen if oz["sablon"] == a[1]["sablon"]) < en_cok and
                sum(1 for _, oz in secilen if oz["zemin"] == a[1]["zemin"]) < 3)

    sira = ogrenme.sec(kod, [(i, oz) for i, oz, _, _ in aday], len(aday), haric=is_.haric,
                       tohum=random.randrange(1 << 30), uygun=uygun, agirlik=lambda imza: by[imza][3])
    is_.ilerle(8, f"{len(aday)} aday sıralandı; tasarımlar kuruluyor ve denetleniyor")
    kabul, yedek, denenen, denendi, kotu = [], [], 0, set(), set()
    for sinir in (en_cok, en_cok + 1):                  # bir düzen hiç geçemezse eksik yer ikinci turda dolar
        for imza in sira:
            if len(kabul) + len(yedek) >= KATALOG_ADET or denenen >= en_fazla:
                break
            par = by[imza][2]
            if (imza in denendi or (par["duzen"], par["yazi"]) in kotu or
                    sum(1 for _, p_, _ in kabul + yedek if p_["duzen"] == par["duzen"]) >= sinir):
                continue
            denendi.add(imza)
            denenen += 1
            d = kur(c, par, olcu)
            if GZ.kontrol(d)[0]:                        # yerleşim sorunu renge bağlı değil: bu düzen ve yazı tipi geçer
                kotu.add((par["duzen"], par["yazi"]))
                continue
            (yedek if d.zayif or GZ.kalite(d, c) < 0.6 else kabul).append((imza, par, d))
            is_.ilerle(8 + 47 * (len(kabul) + len(yedek)) / KATALOG_ADET,
                       f"{len(kabul) + len(yedek)} tasarım hazır ({denenen} denendi)")
    kabul += yedek[:KATALOG_ADET - len(kabul)]
    bas = len(is_.haric) + 1
    return [(f"{harf}{bas + i:02d}", par, d, by[imza][1], imza) for i, (imza, par, d) in enumerate(kabul)], uyar


def gorunus(d, boy):
    from atolye.tasarim import guzellik as GZ
    if d.olcu == "9x12":
        from atolye.tasarim import isimlik9 as T
        return T.gorunus(GZ.katilar(d), boy)
    from atolye.tasarim import isimlik20 as T20
    return T20.gorunus(GZ.katilar(d), d.palet.govde, boy)


def katalog_sayfalari(is_, liste, baslik, ad_, giris, bilgi, alt_not=None):
    from atolye.tasarim import guzellik as GZ
    from atolye.tasarim import katalog as KT
    klasor = is_.yol(f"katalog_{is_.no}", "x")[:-2]
    tasarimlar, sayfa = [], []
    for i, (kod, par, d, oz, imza) in enumerate(liste):
        is_.ilerle(55 + 37 * i / len(liste), f"{kod} çiziliyor")
        im = gorunus(d, 760 if d.olcu == "9x12" else 900)
        yol = os.path.join(klasor, f"{kod}.png")
        im.save(yol)
        tasarimlar.append({"kod": kod, "ad": GZ.ad(d), "ozellikler": oz, "onizleme": is_.goreli(yol), "imza": imza,
                           "parametreler": par, "uyarilar": d.uyarilar + d.zayif})
        sayfa.append((kod, GZ.ad(d), im))
    is_.ilerle(93, "Katalog sayfaları yapılıyor")
    ek = {"alt_not": alt_not} if alt_not else {}
    pdf, jpgs = KT.yap(klasor, baslik, ad_, is_.no, sayfa, giris, bilgi, **ek)
    return {"tasarimlar": tasarimlar, "pdf": is_.goreli(pdf), "sayfalar": [is_.goreli(j) for j in jpgs]}


def katalog(is_):
    b = is_.bilgiler
    c, _, uyar = _icerik(is_, b)
    liste, renk_uyar = katalog_kur(is_, c, OLCU, HARF, KOD)
    if not liste:
        raise SystemExit("Bu bilgilerle baskıya uygun tasarım çıkmadı (ad çok uzun olabilir): 'İsimlikte el yazısıyla "
                         "yazılacak ad' alanına kısa bir ad yazıp yeniden deneyin.")
    giris = (f"QR'ı telefonla okutunca {ad(b)} randevu sayfası açılır: arama, WhatsApp'tan randevu, Instagram, konum. "
             "Hepsi 12 × 9 cm, 1 cm kalın, yazılar ve çiçekler kabartma, masa sehpası dahil.")
    bilgi = ("Ürün", ["Ölçü 12 × 9 cm, gövde 1 cm, köşeler yuvarlak.",
                      "Ad el yazısıyla; yazılar, simge ve çiçekler 2 mm kabartma; QR düz ve keskin.",
                      "Renkler: pudra, ten rengi, krem, lila, adaçayı, fuşya, beyaz, siyah; mürdüm, moka, gül kurusu, "
                      "rose gold.",
                      "Masa sehpası dahil: isimlik 15° eğik durur.",
                      "QR randevu sayfanızı açar: tek dokunuşla arama, WhatsApp'tan randevu, Instagram, konum."])
    out = katalog_sayfalari(is_, liste, "Güzellik isimliği", ad(b), giris, bilgi,
                            alt_not="Beğendiğiniz tasarımın kodunu (ör. G03) yazmanız yeterli.")
    out["uyarilar"] = uyar + renk_uyar
    return out


# ---------------------------------------------------------------- baskı dosyası ve sayfa

def nozullar(d, ana):
    """Kullanılan her renk bir nozulda: `ana` renkler (gövde, sehpa...) ana nozulda, öbürleri yardımcıda."""
    from atolye.tasarim import guzellik as GZ
    m = {c: 1 for c in ana}
    for c in GZ.renkler(d):
        m.setdefault(c, 2)
    return m


def _plaka(d, key, title):
    from atolye.tasarim import ortak as O
    A, B = O.A, O.B
    p = d.palet

    class Plaka(B.Plate):
        def __init__(self):
            self.key, self.title, self.design = key, title, d
            self.panel = O.S.solids(d)
            self.module = O.qr_modul(d.qr_entry, d.qr_side)
            self.stand, self.mount = B.stand()
            # gövde, sehpa (siyah), vurgu ve süs ana nozulda; yazı ve QR'ın öbür rengi yardımcıda
            ana = [p.govde, O.BLACK] + [c for c in (p.vurgu, p.vurgu2) if c and c != p.yazi]
            self.nozzle_map = nozullar(d, ana)
            self.filament_profiles = {c: A.GENERIC_PLA for c in self.nozzle_map}
            self.object_settings = {"enable_support": "0", "ironing_type": "no ironing"}
            self.tower_xy = B.TOWER_XY
            self.project_overrides = {"curr_bed_type": "Textured PEI Plate",
                                      "wipe_tower_x": [f"{B.TOWER_XY[0]:g}"], "wipe_tower_y": [f"{B.TOWER_XY[1]:g}"]}

        def to_bed(self, parts):
            pb = parts[0][1].bounding_box()
            ob = O.I.outline().rotate(90).bounds()
            x, y, _ = self.instances[0]
            return lambda cs: cs.rotate(90).translate((pb[0] - ob[0] + x, pb[1] - ob[1] + y))

    return Plaka()


def dilim(plate, path, filaments, move, raised_z, flat_z, out, uyar):
    """PrusaSlicer kuruluysa yazıların kendi renginde basıldığı denetlenir. Döner metin (filament ve süre)."""
    import shutil

    from atolye.tasarim import guzellik as GZ
    import boyde_isimlik_baski as BI
    if not shutil.which("prusa-slicer"):
        uyar.append("PrusaSlicer kurulu değil: dilimleyici denetimi atlandı (harf ölçüleri ve QR denetlendi)")
        return ""
    d = plate.design
    plate.design = GZ.dilim_tasarimi(d)
    try:
        g, sure, rows, ok = BI.slice_check(plate, path, filaments, move, raised_z, flat_z,
                                           os.path.join(out, "olcum.json"))
    finally:
        plate.design = d
    if not ok:
        bad = [r[0] for r in rows if not BI.row_ok(r[0], r[2], r[3], r[4], r[6])]
        uyar.append("Dilimleyici: şu yazılar tam basılmıyor olabilir: " + ", ".join(sorted(set(bad))))
    return f"Filament ~{sum(g.values()):.0f} g + kule · ~{sure} · "


def sayfa(is_, b, isletme, baslik, hizmet, d, adi, uyar, ek=None):
    """Randevu sayfası (ya da kişinin kartviziti): 5 güzellik şablonundan sıradaki. Döner çıktılar."""
    from atolye import site
    from atolye.tasarim import guzellik as GZ
    sb, uy = site.bilgiler(dict(b, isletme=isletme), is_.klasor, baslik, hizmet, GZ.site_rengi(d.palet), adi)
    uyar += uy
    if not sb["renk"]:
        sb.pop("renk")
    sb.update(ek or {})
    try:
        ws = site.yap(is_, sb, int(b.get("sablon") or 0), guzellik=True)
        uyar += ws["uyarilar"]
        uyar.append(f"Yayın: Cloudflare'de (hesap {site.HESAP}) '{ws['ad']}' adlı Worker'a zip'i yükleyin → "
                    f"{ws['url']} (QR bu adresi açar; şablon {ws['sablon']} · {ws['sablon_ad']})")
        return ws["ciktilar"]
    except Exception as e:                           # noqa: BLE001 (sayfa olmadan da 3MF teslim edilir)
        uyar.append(f"Sayfa üretilemedi: {e}")
        return []


def uret(is_, secilen):
    import zipfile

    from atolye.tasarim import guzellik as GZ
    from atolye.tasarim import ortak as O
    from atolye.urunler.isimlik_9x12 import _musteri_onizleme
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

    is_.ilerle(8, "3MF yazılıyor")
    plate = _plaka(d, f"guzellik_9x12_{adi}_{kod.lower()}_x2d", f"BOYDE_guzellik_9x12_{adi}_{kod}")
    out = is_.yol("cikti", "x")[:-2]
    template = zipfile.ZipFile(A.TEMPLATE)
    path, _, filaments = A.write_design(plate, {n: template.read(n) for n in template.namelist()}, out)
    parts = plate.solids()
    ok_place, place = B.checks(plate, parts)
    is_.ilerle(30, "QR okunuyor (üstten görünüş ve baskı hatası benzetimi)")
    qr = BI.qr_check(plate, c.url)
    mans = [m for _, m, _ in parts]
    overlap = max((mans[i] ^ mans[j]).volume() for i in range(len(mans)) for j in range(i + 1, len(mans)))
    is_.ilerle(40, "Dilimleyici denetimi")
    g_txt = dilim(plate, path, filaments, plate.to_bed(parts),
                  [(round(B.T + 0.2, 2), "kenar"), (round(B.T + B.RELIEF, 2), "yüzey")], round(B.T, 2), out, uyar)
    if not all(qr):
        uyar.append(f"QR denetimi: okundu {qr[0]}, baskı hatası benzetiminde {qr[1]} — dosyayı göndermeden önce "
                    "önizlemeyi okutun")
    if not ok_place:
        uyar.append("Tabla yerleşimi: " + place)
    if overlap > 1e-3:
        uyar.append(f"Parçalar örtüşüyor ({overlap:.3f} mm³)")

    is_.ilerle(55, "Önizlemeler çiziliyor")
    p = d.palet
    renk = " · ".join(f"{i + 1} {A.COLOUR_NAMES[f]}" for i, f in enumerate(filaments))
    noz = plate.nozzle_map
    info = [f"{len(plate.instances)} takım · panel 120 × 90 mm, {O.AD[p.govde]} gövde 1 cm · yazılar ve süsler "
            f"{B.RELIEF:.0f} mm kabartma · QR yüzeyle aynı hizada · tasarım {kod} ({d.duzen})",
            f"AMS: {renk} · ana nozul: {', '.join(O.AD[c] for c in noz if noz[c] == 1)} · yardımcı nozul: "
            f"{', '.join(O.AD[c] for c in noz if noz[c] == 2)}",
            "Bambu standart 0,20 mm · ütüleme kapalı · destek yok · Textured PEI · panel yüzü yukarı, sehpa yanında",
            f"{g_txt}QR {c.url} {'okunuyor' if all(qr) else 'SORUNLU'} · harf içi en az 0,7 mm "
            f"{'tamam' if not sorun else 'SORUNLU'} · yerleşim {'tamam' if ok_place else 'SORUNLU'}"]
    B.preview(plate, parts, os.path.join(out, "tabla.png"), info,
              title=f"{O.tr_upper(ad(b))} – GÜZELLİK İSİMLİĞİ 9 × 12 ({kod}) · X2D BASKI DOSYASI")
    _musteri_onizleme(d, plate.panel, os.path.join(out, "onizleme.png"), ad(b),
                      "12 × 9 cm · 1 cm kalın · kabartma yazı ve çiçekler · masa sehpası dahil · BOYDE LABS",
                      ust="GÜZELLİK İSİMLİĞİ 12 × 9")

    is_.ilerle(70, "Randevu sayfası hazırlanıyor")
    site_cikti = sayfa(is_, b, ad(b), c.marka, c.hizmet, d, adi, uyar)
    is_.ilerle(96, "Bitti")
    return {"ciktilar": [{"ad": f"X2D baskı dosyası (3MF, iki takım) · {kod}", "yol": is_.goreli(path), "tur": "3mf"},
                         {"ad": "Müşteri önizlemesi", "yol": is_.goreli(os.path.join(out, "onizleme.png")),
                          "tur": "resim"},
                         {"ad": "Tabla yerleşimi ve kontroller", "yol": is_.goreli(os.path.join(out, "tabla.png")),
                          "tur": "resim"}] + site_cikti,
            "uyarilar": uyar}
