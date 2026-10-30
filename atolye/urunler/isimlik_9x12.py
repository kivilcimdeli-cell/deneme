"""QR'lı masa isimliği 9 × 12: 10 tasarımlık katalog → müşterinin seçtiği kod → X2D 3MF (iki takım) ve web sayfası.

Tasarımlar atolye/tasarim/isimlik9.py'deki 10 düzenden müşterinin bilgileriyle kurulur (ad, iş türü, hizmetler,
telefon, sektör simgesi ya da logo). Katalogda her düzenden bir tasarım (yenilemede en çok iki), zemin, vurgu rengi
ve yazı tipi öğrenmeye göre (beğenilenler öne çıkar, %30 keşif); bu müşteriye gösterilenler yeni katalogda tekrar
edilmez. Her tasarım baskıya uygunluk denetiminden geçer; geçemeyen gösterilmez.

Seçilen kodla:
  cikti/isimlik_<ad>_<kod>_x2d.3mf   tablada iki takım (panel + sehpa), Bambu standart 0,20 mm, ütüleme ve destek
                                     yok, Textured PEI; gövde ve vurgu ana nozulda, yazı rengi yardımcı nozulda
  cikti/onizleme.png                 müşteriye: önden ve masada
  cikti/tabla.png                    tabla yerleşimi ve kontroller
  web/<ad>_site.zip                  işletmenin sayfası (5 şablondan sıradaki), QR bu sayfayı açar
  web/sayfa_onizleme.png, web/sayfa_deneme.html
Kontroller: QR üstten görünüşte ve baskı hatası benzetiminde okunuyor; yazılarda harf içi ve ara ≥ 0,7 mm; parçalar
iki nozulun ortak alanında; PrusaSlicer kuruluysa dilimleyicide yazıların kendi renginde basıldığı.
"""
import os
import re

KOD = "isimlik_9x12"
AD = "QR'lı masa isimliği 9 × 12"
SIMGE = "🔳"
ACIKLAMA = ("120 × 90 mm, 1 cm gövde, 2 mm kabartma yazı, sehpalı; QR işletmenin sayfasını açar. 10 tasarımlık "
            "katalog, seçilen tasarımın X2D 3MF'i (iki takım) ve web sayfası.")
KATALOG_ADET = 10


def _secenekler():
    from atolye.tasarim import isimlik9 as T
    from atolye.tasarim import ortak as O
    sektor = [(k, v[0]) for k, v in T.SEKTORLER.items()]
    renk = [("otomatik", "Otomatik (katalogda farklı renkler)")] + [
        (O.AD[c], O.AD[c].capitalize()) for c in (O.RED, O.ORANGE, O.YELLOW, O.GOLD, O.TURQ, O.BLUE, O.NAVY,
                                                    O.GREEN, O.PINK, O.PURPLE, O.GRAY)]
    return sektor, renk


try:
    _SEKTOR, _RENK = _secenekler()
except Exception:                                      # noqa: BLE001 (tasarım modülleri yüklenemezse form yine açılır)
    _SEKTOR, _RENK = [("genel", "Genel")], [("otomatik", "Otomatik")]

ALANLAR = [
    {"ad": "isletme", "etiket": "İşletme adı", "tur": "text", "zorunlu": True, "grup": "İsimlik",
     "ornek": "Kardeşler Oto Yıkama", "ipucu": "Tam adı (sitede ve kayıtta)."},
    {"ad": "marka", "etiket": "İsimlikte büyük yazılacak ad", "tur": "text", "ornek": "KARDEŞLER",
     "ipucu": "Boşsa işletme adından iş türü çıkarılır."},
    {"ad": "hizmet", "etiket": "İş türü (adın altında)", "tur": "text", "ornek": "OTO YIKAMA"},
    {"ad": "sektor", "etiket": "Sektör (simge ve renkler)", "tur": "select", "secenekler": _SEKTOR,
     "varsayilan": "genel", "zorunlu": True},
    {"ad": "telefon", "etiket": "Telefon", "tur": "tel", "zorunlu": True, "ornek": "0532 123 45 67",
     "ipucu": "İsimlikte ve sitede (Hemen Ara)."},
    {"ad": "hizmetler", "etiket": "Hizmetler", "tur": "textarea", "ornek": "İç dış yıkama, Pasta cila, Seramik kaplama",
     "ipucu": "Virgülle ya da satır satır. İsimliğe sığanlar yazılır (genelde 2–4 madde)."},
    {"ad": "cagri", "etiket": "Çağrı yazısı", "tur": "text", "ornek": "HEMEN ARA",
     "ipucu": "Boşsa sektöre göre: HEMEN ARA, RANDEVU ya da SİPARİŞ."},
    {"ad": "qr_yazi", "etiket": "QR'ın altındaki yazı", "tur": "text", "varsayilan": "TARA"},
    {"ad": "zemin", "etiket": "Gövde rengi", "tur": "select", "varsayilan": "otomatik",
     "secenekler": [("otomatik", "Otomatik (siyah ve beyaz karışık)"), ("siyah", "Siyah"), ("beyaz", "Beyaz")]},
    {"ad": "renk", "etiket": "Vurgu rengi (filament)", "tur": "select", "secenekler": _RENK, "varsayilan": "otomatik"},
    {"ad": "logo", "etiket": "Logo (isteğe bağlı)", "tur": "dosya", "kabul": "image/png,image/jpeg",
     "ipucu": "Düz zeminde tek renk logo en iyisi. İsimlikte simgenin yerine kabartma, sitede işaret olur."},

    {"ad": "whatsapp", "etiket": "WhatsApp numarası", "tur": "tel", "grup": "Web sayfası",
     "ipucu": "Boşsa telefon."},
    {"ad": "whatsapp_mesaj", "etiket": "WhatsApp hazır mesajı", "tur": "text",
     "varsayilan": "Merhaba, bilgi almak istiyorum."},
    {"ad": "instagram", "etiket": "Instagram", "tur": "text", "ornek": "@kullaniciadi"},
    {"ad": "google", "etiket": "Google yorum bağlantısı", "tur": "text", "ornek": "https://g.page/r/…/review"},
    {"ad": "harita", "etiket": "Konum bağlantısı (Haritalar)", "tur": "text", "ornek": "https://maps.app.goo.gl/…"},
    {"ad": "konum", "etiket": "Semt, şehir", "tur": "text", "ornek": "Kepez, Antalya"},
    {"ad": "web", "etiket": "Web sitesi", "tur": "text"},
    {"ad": "aciklama", "etiket": "Sayfadaki kısa tanıtım", "tur": "textarea",
     "ornek": "Aracınız pırıl pırıl. Tek dokunuşla arayın, yazın."},
    {"ad": "site_adi", "etiket": "Sayfa adresi (Worker adı)", "tur": "text", "ornek": "kardesler",
     "ipucu": "https://<ad>.qrsistem.workers.dev/ · boşsa isimlikteki addan (en çok 20 harf, a-z ve rakam)."},
    {"ad": "sablon", "etiket": "Site şablonu", "tur": "select", "varsayilan": "0",
     "secenekler": [("0", "Sıradaki (otomatik)"), ("1", "1 · Şimşek"), ("2", "2 · Lastik izi"), ("3", "3 · İkaz"),
                    ("4", "4 · Kurumsal"), ("5", "5 · Sade")]},

    {"ad": "iban", "etiket": "IBAN", "tur": "text", "grup": "Ödeme bilgileri (sayfada)", "ornek": "TR…"},
    {"ad": "iban_alici", "etiket": "Alıcı adı", "tur": "text"},
    {"ad": "banka", "etiket": "Banka", "tur": "text"},
    {"ad": "karekod", "etiket": "Banka karekodu (ekran görüntüsü)", "tur": "dosya", "kabul": "image/*",
     "ipucu": "Bankanın IBAN karekodu: okunup sayfaya eklenir (müşteri galeriden okutur)."},

    {"ad": "yetkili", "etiket": "Yetkili", "tur": "text", "grup": "Kayıt (isimliğe ve sayfaya yazılmaz)"},
    {"ad": "yetkili_tel", "etiket": "Yetkilinin telefonu", "tur": "tel"},
    {"ad": "not", "etiket": "Sipariş notu", "tur": "textarea"},
]


def ad(b):
    return " ".join(b["isletme"].split())


# ---------------------------------------------------------------- içerik ve adaylar

def _icerik(is_, b):
    """Formdan tasarım içeriği. Döner (Icerik, sektörün renkleri, sayfa adı, uyarılar)."""
    from atolye import site
    from atolye.tasarim import isimlik9 as T
    from atolye.tasarim import logo as L
    from atolye.tasarim import ortak as O
    uyar = []
    s_ad, simge, cagri, renkler = T.SEKTORLER.get(b.get("sektor") or "genel", T.SEKTORLER["genel"])
    isletme = ad(b)
    hizmet = O.tr_upper((b.get("hizmet") or "").strip())
    marka = " ".join((b.get("marka") or "").split())
    if not marka:
        u = O.tr_upper(isletme)
        marka = u[:-len(hizmet)].strip() if hizmet and u.endswith(hizmet) and u != hizmet else isletme
    maddeler = [O.tr_upper(x.strip(" .")) for x in re.split(r"[,;\n·•]+", b.get("hizmetler") or "") if x.strip(" .")]
    logo = None
    if b.get("logo"):
        try:
            logo, svg = L.izle(os.path.join(is_.klasor, b["logo"]))
            simge = "logo"
            with open(is_.yol("web", "logo", "isaret.svg"), "w", encoding="utf-8") as f:
                f.write(svg)
        except Exception as e:                       # noqa: BLE001
            uyar.append(f"Logo okunamadı, sektör simgesi kullanıldı: {e}")
    adi = site.sayfa_adi(b.get("site_adi") or marka)
    if b.get("site_adi") and adi != b["site_adi"].strip().lower():
        uyar.append(f"Sayfa adı '{adi}' olarak düzeltildi (yalnız a-z ve rakam, en çok {site.EN_UZUN} harf)")
    c = T.Icerik(marka=marka, hizmet=hizmet, hizmetler=maddeler, telefon=O.telefon_yazisi(b["telefon"]),
                 cagri=(b.get("cagri") or cagri).strip(), qr_yazi=(b.get("qr_yazi") or "TARA").strip(), simge=simge,
                 logo=logo, url=site.sayfa_url(adi))
    return c, renkler, adi, uyar


def _adaylar(b, c, renkler):
    """[(imza, özellikler, (düzen, gövde, vurgu, vurgu2, yazı tipi))]."""
    from atolye.tasarim import isimlik9 as T
    from atolye.tasarim import ortak as O
    zemin = b.get("zemin") or "otomatik"
    govdeler = [O.BLACK, O.WHITE] if zemin == "otomatik" else [O.KIMLIK[zemin]]
    sabit = O.KIMLIK.get(b.get("renk") or "otomatik")
    simge = c.simge if c.simge in ("logo", "monogram") else "simge"
    out = []
    for duzen, (_, _, fonts) in T.DUZENLER.items():
        for g in govdeler:
            uygun = O.KOYUDA if g == O.BLACK else O.ACIKTA
            vurgular = [sabit] if sabit else ([r for r in renkler if r in uygun][:3] or uygun[:2])
            for v in vurgular:
                v2 = (O.BLUE if v != O.BLUE else O.RED) if c.simge == "direk" and duzen == "serit" else 0
                for f in fonts:
                    oz = {"sablon": duzen, "zemin": O.AD[g], "renk": O.AD[v], "yazi": f, "simge": simge}
                    out.append((f"{duzen}|{O.AD[g]}|{O.AD[v]}|{f}", oz, (duzen, g, v, v2, f)))
    return out


def _parametre(p):
    duzen, g, v, v2, f = p
    return {"duzen": duzen, "govde": g, "vurgu": v, "vurgu2": v2, "yazi": f}


def _kur(c, par):
    from atolye.tasarim import isimlik9 as T
    from atolye.tasarim import ortak as O
    return T.tasarla(par["duzen"], c, O.Palet(par["govde"], par["vurgu"], par.get("vurgu2", 0)), par["yazi"])


# ---------------------------------------------------------------- katalog

def katalog(is_):
    import random

    from atolye import ogrenme
    from atolye.tasarim import isimlik9 as T
    from atolye.tasarim import katalog as KT
    from atolye.tasarim import ortak as O
    b = is_.bilgiler
    c, renkler, _, uyar = _icerik(is_, b)
    adaylar = _adaylar(b, c, renkler)
    by = {a[0]: a for a in adaylar}
    en_cok = 1 if is_.no == 1 else 2                 # ilk katalogda her düzenden bir tasarım

    # ön eleme: her düzen × yazı tipi bir kez kurulur (denetimsiz, hızlı); ad küçük kalan ya da hizmetleri sığmayan
    # eşleşmeler geri düşer (ağırlık kalite³), çok kötüler hiç gösterilmez
    is_.ilerle(4, "Düzenler bu bilgilere göre deneniyor")
    kal = {}
    for duzen, (_, _, fonts) in T.DUZENLER.items():
        for f in fonts:
            kal[(duzen, f)] = T.kalite(T.tasarla(duzen, c, O.Palet(O.BLACK, O.GOLD), f), c)
    eniyi = {dz: max(q for (d2, _), q in kal.items() if d2 == dz) for dz in T.DUZENLER}
    adaylar = [a for a in adaylar if kal[(a[2][0], a[2][4])] >= max(0.45, 0.8 * eniyi[a[2][0]])]

    def uygun(secilen, aday):
        return sum(1 for _, oz in secilen if oz["sablon"] == aday[1]["sablon"]) < en_cok

    sira = ogrenme.sec(KOD, [(i, oz) for i, oz, _ in adaylar], len(adaylar), haric=is_.haric,
                       tohum=random.randrange(1 << 30), uygun=uygun,
                       agirlik=lambda imza: kal[(by[imza][2][0], by[imza][2][4])] ** 3)
    is_.ilerle(12, f"{len(adaylar)} aday sıralandı; tasarımlar kuruluyor ve denetleniyor")
    kabul, denenen, denendi = [], 0, set()
    for sinir in (en_cok, en_cok + 1):                 # bir düzen hiç geçemezse eksik yer ikinci turda dolar
        for imza in sira:
            if len(kabul) >= KATALOG_ADET or denenen >= 36:
                break
            par = _parametre(by[imza][2])
            if imza in denendi or sum(1 for _, _, d in kabul if d.duzen == par["duzen"]) >= sinir:
                continue
            denendi.add(imza)
            denenen += 1
            d = _kur(c, par)
            sorun, _ = T.kontrol(d)
            if sorun:
                continue
            kabul.append((imza, par, d))
            is_.ilerle(12 + 38 * len(kabul) / KATALOG_ADET, f"{len(kabul)} tasarım hazır ({denenen} denendi)")
    if not kabul:
        raise SystemExit("Bu bilgilerle baskıya uygun tasarım çıkmadı (ad çok uzun olabilir): 'İsimlikte büyük "
                         "yazılacak ad' alanına kısa bir ad yazıp yeniden deneyin.")
    bas = len(is_.haric) + 1
    klasor = is_.yol(f"katalog_{is_.no}", "x")[:-2]
    tasarimlar, sayfa = [], []
    for i, (imza, par, d) in enumerate(kabul):
        kod = f"M{bas + i:02d}"
        is_.ilerle(50 + 40 * i / len(kabul), f"{kod} çiziliyor")
        im = T.gorunus(T.katilar(d), 760)
        yol = os.path.join(klasor, f"{kod}.png")
        im.save(yol)
        tasarimlar.append({"kod": kod, "ad": T.ad(d), "ozellikler": by[imza][1], "onizleme": is_.goreli(yol),
                           "imza": imza, "parametreler": par, "uyarilar": d.uyarilar + d.zayif})
        sayfa.append((kod, T.ad(d), im))
    is_.ilerle(92, "Katalog sayfaları yapılıyor")
    giris = (f"QR'ı telefonla okutunca {ad(b)} sayfası açılır: arama, WhatsApp, konum, yorumlar. Hepsi 12 × 9 cm, "
             "1 cm kalın, yazılar kabartma, masa sehpası dahil.")
    bilgi = ("Ürün", ["Ölçü 12 × 9 cm, gövde 1 cm, köşeler yuvarlak.",
                      "Yazılar ve şekiller 2 mm kabartma; QR düz ve keskin, her telefonda okunur.",
                      "Masa sehpası dahil: isimlik 15° eğik durur.",
                      "QR işletmenizin sayfasını açar: tek dokunuşla arama, WhatsApp, konum, Google yorumları, "
                      "IBAN.",
                      "Renkler değiştirilebilir, logonuz eklenebilir."])
    pdf, jpgs = KT.yap(klasor, "QR'lı masa isimliği", ad(b), is_.no, sayfa, giris, bilgi)
    return {"tasarimlar": tasarimlar, "pdf": is_.goreli(pdf), "sayfalar": [is_.goreli(j) for j in jpgs],
            "uyarilar": uyar}


# ---------------------------------------------------------------- baskı dosyası ve site

def _plaka(d, key, title):
    from atolye.tasarim import ortak as O
    A, B = O.A, O.B

    class Plaka(B.Plate):
        def __init__(self):
            self.key, self.title, self.design = key, title, d
            self.panel = O.S.solids(d)
            self.module = O.qr_modul(d.qr_entry, d.qr_side)
            self.stand, self.mount = B.stand()
            p = d.palet
            self.nozzle_map = {p.govde: 1, p.vurgu: 1, p.yazi: 2}       # gövde, sonra vurgu ana nozulda
            if p.vurgu2:
                self.nozzle_map[p.vurgu2] = 1
            self.filament_profiles = {c: A.GENERIC_PLA for c in self.nozzle_map}
            self.object_settings = {"enable_support": "0", "ironing_type": "no ironing"}
            self.tower_xy = B.TOWER_XY
            self.project_overrides = {"curr_bed_type": "Textured PEI Plate",
                                      "wipe_tower_x": [f"{B.TOWER_XY[0]:g}"], "wipe_tower_y": [f"{B.TOWER_XY[1]:g}"]}

        def to_bed(self, parts):
            """Tasarım koordinatından ilk takımın tabla koordinatına (boyde_isimlik_baski.make_9x12 gibi)."""
            pb = parts[0][1].bounding_box()
            ob = O.I.outline().rotate(90).bounds()
            x, y, _ = self.instances[0]
            return lambda cs: cs.rotate(90).translate((pb[0] - ob[0] + x, pb[1] - ob[1] + y))

    return Plaka()


def _musteri_onizleme(d, parts, path, baslik, alt):
    """Müşteriye: önden (sehpasında) ve masada 3/4."""
    from PIL import Image, ImageDraw, ImageFont

    from atolye.tasarim import isimlik9 as T
    from atolye.tasarim import ortak as O
    on = O.A.fit_into(T.gorunus(parts, 1300), 1100, 560)
    iso = O.A.fit_into(T.gorunus(parts, 1200, (-28, -68), None), 760, 520)
    canvas = Image.new("RGB", (1200, 1300), (244, 241, 234))
    dr = ImageDraw.Draw(canvas)
    f = os.path.join(O.A.FONT_DIR, "SpaceGrotesk_700Bold.ttf")
    dr.text((60, 40), "QR'LI MASA İSİMLİĞİ", fill=(255, 90, 31), font=ImageFont.truetype(f, 24))
    dr.text((60, 76), baslik, fill=(18, 19, 22), font=ImageFont.truetype(f, 44))
    canvas.paste(on, ((1200 - on.width) // 2, 160), on)
    canvas.paste(iso, ((1200 - iso.width) // 2, 740), iso)
    dr.text((60, 1250), alt, fill=(85, 87, 92),
            font=ImageFont.truetype(os.path.join(O.A.FONT_DIR, "SpaceGrotesk_500Medium.ttf"), 22))
    canvas.save(path)


def uret(is_, secilen):
    import shutil
    import zipfile

    from atolye import site
    from atolye.tasarim import isimlik9 as T
    from atolye.tasarim import ortak as O
    import boyde_isimlik_baski as BI
    A, B = O.A, O.B
    b = is_.bilgiler
    kod = secilen["kod"]
    c, _, adi, uyar = _icerik(is_, b)
    d = _kur(c, secilen["parametreler"])
    sorun, _ = T.kontrol(d)
    if sorun:
        uyar.append("Baskıya uygunluk: " + "; ".join(sorun))

    is_.ilerle(8, "3MF yazılıyor")
    plate = _plaka(d, f"isimlik_9x12_{adi}_{kod.lower()}_x2d", f"BOYDE_isimlik_9x12_{adi}_{kod}")
    out = is_.yol("cikti", "x")[:-2]
    template = zipfile.ZipFile(A.TEMPLATE)
    path, _, filaments = A.write_design(plate, {n: template.read(n) for n in template.namelist()}, out)
    parts = plate.solids()
    ok_place, place = B.checks(plate, parts)
    is_.ilerle(30, "QR okunuyor (üstten görünüş ve baskı hatası benzetimi)")
    qr = BI.qr_check(plate, c.url)
    mans = [m for _, m, _ in parts]
    overlap = max((mans[i] ^ mans[j]).volume() for i in range(len(mans)) for j in range(i + 1, len(mans)))
    g_txt, dilim_ok = "", None
    if shutil.which("prusa-slicer"):
        is_.ilerle(40, "Dilimleyicide deneniyor (PrusaSlicer)")
        raised_z = [(round(B.T + 0.2, 2), "kenar"), (round(B.T + B.RELIEF, 2), "yüzey")]
        g, sure, rows, dilim_ok = BI.slice_check(plate, path, filaments, plate.to_bed(parts), raised_z, round(B.T, 2),
                                                 os.path.join(out, "olcum.json"))
        g_txt = f"Filament (iki takım) ~{sum(g.values()):.0f} g + kule · ~{sure} · "
        if not dilim_ok:
            bad = [r[0] for r in rows if not BI.row_ok(r[0], r[2], r[3], r[4], r[6])]
            uyar.append("Dilimleyici: şu yazılar tam basılmıyor olabilir: " + ", ".join(sorted(set(bad))))
    else:
        uyar.append("PrusaSlicer kurulu değil: dilimleyici denetimi atlandı (harf ölçüleri ve QR denetlendi)")
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
    info = [f"{len(plate.instances)} takım · panel 120 × 90 mm, {O.AD[p.govde]} gövde 1 cm · yazılar {B.RELIEF:.0f} mm "
            f"kabartma · QR yüzeyle aynı hizada · tasarım {kod} ({d.duzen})",
            f"AMS: {renk} · ana nozul: {O.AD[p.govde]}, {O.AD[p.vurgu]}"
            f"{', ' + O.AD[p.vurgu2] if p.vurgu2 else ''} · yardımcı nozul: {O.AD[p.yazi]}",
            "Bambu standart 0,20 mm · ütüleme kapalı · destek yok · Textured PEI · panel yüzü yukarı, sehpa yanında",
            f"{g_txt}QR {c.url} {'okunuyor' if all(qr) else 'SORUNLU'} · harf içi ve ara en az 0,7 mm "
            f"{'tamam' if not sorun else 'SORUNLU'} · yerleşim {'tamam' if ok_place else 'SORUNLU'}"]
    B.preview(plate, parts, os.path.join(out, "tabla.png"), info,
              title=f"{ad(b).upper()} – İSİMLİK 9 × 12 ({kod}) · X2D BASKI DOSYASI")
    _musteri_onizleme(d, plate.panel, os.path.join(out, "onizleme.png"), ad(b),
                      "12 × 9 cm · 1 cm kalın · kabartma yazı · masa sehpası dahil · BOYDE LABS")

    is_.ilerle(70, "Web sayfası hazırlanıyor")
    isaret = "logo/isaret.svg" if c.simge == "logo" and os.path.exists(is_.yol("web", "logo", "isaret.svg")) else None
    sb, uy = site.bilgiler(b, is_.klasor, c.marka, c.hizmet, O.WEB[p.vurgu], adi, isaret)
    uyar += uy
    try:
        ws = site.yap(is_, sb, int(b.get("sablon") or 0))
        site_cikti = ws["ciktilar"]
        uyar += ws["uyarilar"]
        uyar.append(f"Yayın: Cloudflare'de (hesap {site.HESAP}) '{ws['ad']}' adlı Worker'a zip'i yükleyin → {ws['url']} "
                    f"(QR bu adresi açar; şablon {ws['sablon']} · {ws['sablon_ad']})")
    except Exception as e:                           # noqa: BLE001 (site olmadan da 3MF teslim edilir)
        site_cikti = []
        uyar.append(f"Web sayfası üretilemedi: {e}")
    is_.ilerle(96, "Bitti")
    return {"ciktilar": [{"ad": f"X2D baskı dosyası (3MF, iki takım) · {kod}", "yol": is_.goreli(path), "tur": "3mf"},
                         {"ad": "Müşteri önizlemesi", "yol": is_.goreli(os.path.join(out, "onizleme.png")),
                          "tur": "resim"},
                         {"ad": "Tabla yerleşimi ve kontroller", "yol": is_.goreli(os.path.join(out, "tabla.png")),
                          "tur": "resim"}] + site_cikti,
            "uyarilar": uyar}
