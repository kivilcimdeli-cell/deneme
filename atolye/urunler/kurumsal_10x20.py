"""Kurumsal isimlik 10 × 20 (kişi): 10 tasarımlık katalog → seçilen kod → X2D 3MF ve dijital kartvizit sayfası.

Tasarımlar atolye/tasarim/isimlik20.py'deki 10 düzenden kişinin bilgileriyle kurulur: ad soyad, unvan, kurum,
telefon, simge (sektör, logo ya da baş harfler). Panel 200 × 100 mm, gövde 5 mm, yazılar 2 mm kabartma, QR yüzeyle
aynı hizada; sehpa 170 mm gövde renginde (BOYDE B07 10 × 20 gibi). Uzun ad, unvan ya da kurumda ad küçülür; yine
sığmazsa telefon isimlikten çıkar (sayfada kalır). Katalogda her düzenden bir tasarım (yenilemede en çok iki); gövde,
renk ve yazı tipi öğrenmeye göre; bu kişiye gösterilenler tekrar edilmez; denetimden geçemeyen gösterilmez.

Seçilen kodla (kişinin klasöründe):
  cikti/kurumsal_<ad>_<kod>_x2d.3mf   tek takım (panel + sehpa), Bambu standart 0,20 mm, ütüleme ve destek yok
  cikti/onizleme.png, cikti/tabla.png
  web/<ad>_site.zip                   dijital kartvizit (5 şablondan sıradaki; Rehbere kaydet kişiyi kurumuyla ekler)
"""
import os
import re

KOD = "kurumsal_10x20"
AD = "Kurumsal isimlik 10 × 20"
SIMGE = "🪪"
ACIKLAMA = ("200 × 100 mm kişiye özel isimlik: ad soyad, unvan, kurum; yazılar kabartma, QR dijital kartviziti açar, "
            "sehpalı. 10 tasarımlık katalog, seçilen tasarımın X2D 3MF'i ve kartvizit sayfası.")
KATALOG_ADET = 10


def _secenekler():
    from atolye.tasarim import isimlik9 as T
    from atolye.tasarim import ortak as O
    sektor = [(k, v[0]) for k, v in T.SEKTORLER.items()]
    renk = [("otomatik", "Otomatik (katalogda farklı renkler)")] + [
        (O.AD[c], O.AD[c].capitalize()) for c in (O.NAVY, O.GOLD, O.RED, O.ORANGE, O.TURQ, O.BLUE, O.GREEN, O.PINK,
                                                    O.PURPLE, O.GRAY)]
    return sektor, renk


try:
    _SEKTOR, _RENK = _secenekler()
    from atolye.tasarim.ortak import yazi_secenekleri as _ys
    _YAZI = _ys()
except Exception:                                      # noqa: BLE001 (tasarım modülleri yüklenemezse form yine açılır)
    _SEKTOR, _RENK, _YAZI = [("genel", "Genel")], [("otomatik", "Otomatik")], [("otomatik", "Otomatik")]

ALANLAR = [
    {"ad": "ad_soyad", "etiket": "Ad soyad", "tur": "text", "zorunlu": True, "grup": "İsimlik", "ornek": "Mehmet Kaya",
     "ipucu": "Yazıldığı gibi (büyük-küçük harf); bazı tasarımlarda büyük harfle."},
    {"ad": "unvan", "etiket": "Unvan / görev", "tur": "text", "ornek": "Avukat · Arabulucu"},
    {"ad": "kurum", "etiket": "Kurum / şirket", "tur": "text", "ornek": "Kaya Hukuk Bürosu"},
    {"ad": "telefon", "etiket": "Telefon", "tur": "tel", "zorunlu": True, "ornek": "0532 123 45 67",
     "ipucu": "İsimlikte (sığarsa) ve kartvizit sayfasında."},
    {"ad": "eposta", "etiket": "E-posta (sayfada)", "tur": "text", "ornek": "ad@kurum.com"},
    {"ad": "sektor", "etiket": "Sektör (simge ve renkler)", "tur": "select", "secenekler": _SEKTOR,
     "varsayilan": "genel", "zorunlu": True, "ipucu": "Genel: kişinin baş harfleri."},
    {"ad": "qr_yazi", "etiket": "QR'ın altındaki yazı", "tur": "text", "varsayilan": "KARTVİZİT"},
    {"ad": "zemin", "etiket": "Gövde rengi", "tur": "select", "varsayilan": "otomatik",
     "secenekler": [("otomatik", "Otomatik (siyah ve beyaz karışık)"), ("siyah", "Siyah"), ("beyaz", "Beyaz")]},
    {"ad": "yazi_renk", "etiket": "Yazı rengi (ad, unvan, kurum, telefon)", "tur": "select", "secenekler": _YAZI,
     "varsayilan": "otomatik", "ipucu": "QR her zaman siyah-beyaz kalır (okunsun diye)."},
    {"ad": "renk", "etiket": "Vurgu rengi (simge, çizgiler)", "tur": "select", "secenekler": _RENK,
     "varsayilan": "otomatik"},
    {"ad": "logo", "etiket": "Kurum logosu (isteğe bağlı)", "tur": "dosya", "kabul": "image/png,image/jpeg",
     "ipucu": "Düz zeminde tek renk logo en iyisi; simgenin yerine kabartma, sayfada işaret olur."},

    {"ad": "whatsapp", "etiket": "WhatsApp numarası", "tur": "tel", "grup": "Kartvizit sayfası",
     "ipucu": "Boşsa telefon."},
    {"ad": "whatsapp_mesaj", "etiket": "WhatsApp hazır mesajı", "tur": "text",
     "varsayilan": "Merhaba, bilgi almak istiyorum."},
    {"ad": "instagram", "etiket": "Instagram", "tur": "text", "ornek": "@kullaniciadi"},
    {"ad": "web", "etiket": "Web sitesi", "tur": "text"},
    {"ad": "konum", "etiket": "Semt, şehir", "tur": "text", "ornek": "Muratpaşa, Antalya"},
    {"ad": "harita", "etiket": "Konum bağlantısı (Haritalar)", "tur": "text"},
    {"ad": "aciklama", "etiket": "Sayfadaki kısa tanıtım", "tur": "textarea"},
    {"ad": "site_adi", "etiket": "Sayfa adresi (Worker adı)", "tur": "text", "ornek": "mehmetkaya",
     "ipucu": "https://<ad>.qrsistem.workers.dev/ · boşsa ad soyaddan (en çok 20 harf, a-z ve rakam)."},
    {"ad": "sablon", "etiket": "Site şablonu", "tur": "select", "varsayilan": "0",
     "secenekler": [("0", "Sıradaki (otomatik)"), ("1", "1 · Şimşek"), ("2", "2 · Lastik izi"), ("3", "3 · İkaz"),
                    ("4", "4 · Kurumsal"), ("5", "5 · Sade")]},
    {"ad": "iban", "etiket": "IBAN (isteğe bağlı)", "tur": "text", "grup": "Ödeme bilgileri (sayfada, isteğe bağlı)"},
    {"ad": "iban_alici", "etiket": "Alıcı adı", "tur": "text"},
    {"ad": "banka", "etiket": "Banka", "tur": "text"},
    {"ad": "karekod", "etiket": "Banka karekodu (ekran görüntüsü)", "tur": "dosya", "kabul": "image/*"},

    {"ad": "not", "etiket": "Sipariş notu", "tur": "textarea", "grup": "Kayıt"},
]


def ad(b):
    return " ".join(b["ad_soyad"].split())


def _icerik(is_, b):
    """Döner (Icerik20, sektörün renkleri, sayfa adı, uyarılar). Panel ölçüleri 10 × 20'ye çevrilir."""
    from atolye import site
    from atolye.tasarim import isimlik20 as T
    from atolye.tasarim import isimlik9 as T9
    from atolye.tasarim import logo as L
    from atolye.tasarim import ortak as O
    T.olcu()
    uyar = []
    _, simge, _, renkler = T9.SEKTORLER.get(b.get("sektor") or "genel", T9.SEKTORLER["genel"])
    if simge == "direk":
        simge = "makas"
    logo = None
    if b.get("logo"):
        try:
            logo, svg = L.izle(os.path.join(is_.klasor, b["logo"]))
            simge = "logo"
            with open(is_.yol("web", "logo", "isaret.svg"), "w", encoding="utf-8") as f:
                f.write(svg)
        except Exception as e:                       # noqa: BLE001
            uyar.append(f"Logo okunamadı, simge kullanıldı: {e}")
    adi = site.sayfa_adi(b.get("site_adi") or ad(b))
    if b.get("site_adi") and adi != b["site_adi"].strip().lower():
        uyar.append(f"Sayfa adı '{adi}' olarak düzeltildi (yalnız a-z ve rakam, en çok {site.EN_UZUN} harf)")
    c = T.Icerik20(marka=ad(b), hizmet=" ".join((b.get("unvan") or "").split()), hizmetler=[],
                   telefon=O.telefon_yazisi(b["telefon"]), cagri="", qr_yazi=(b.get("qr_yazi") or "KARTVİZİT").strip(),
                   simge=simge, logo=logo, url=site.sayfa_url(adi), kurum=" ".join((b.get("kurum") or "").split()))
    navy = [O.NAVY, O.GOLD]                            # kurumsal: lacivert ve altın her sektörde aday
    return c, list(dict.fromkeys(renkler + navy)), adi, uyar


def _adaylar(b, c, renkler):
    from atolye.tasarim import isimlik20 as T
    from atolye.tasarim import ortak as O
    paletler, uyar = O.isimlik_paletleri(b, renkler, [O.WHITE, O.BLACK])
    simge = c.simge if c.simge in ("logo", "monogram") else "simge"
    out = []
    for duzen, (_, _, fonts, _) in T.DUZENLER.items():
        for g, y, v in paletler:
            oto = y == O.Palet(g, v).yazi                               # otomatik yazı rengi: eski imza
            for f in fonts:
                oz = {"sablon": duzen, "zemin": O.AD[g], "metin": O.AD[y], "renk": O.AD[v], "yazi": f, "simge": simge}
                out.append((f"{duzen}|{O.AD[g]}|{O.AD[v]}|{f}" + ("" if oto else f"|{O.AD[y]}"), oz,
                            {"duzen": duzen, "govde": g, "vurgu": v, "yazi": f, "metin": y}))
    return out, uyar


def _kur(c, par):
    from atolye.tasarim import isimlik20 as T
    from atolye.tasarim import ortak as O
    return T.tasarla(par["duzen"], c, O.Palet(par["govde"], par["vurgu"], yazi=par.get("metin", 0)), par["yazi"])


# ---------------------------------------------------------------- katalog

def katalog(is_):
    import random

    from atolye import ogrenme
    from atolye.tasarim import isimlik20 as T
    from atolye.tasarim import katalog as KT
    b = is_.bilgiler
    c, renkler, _, uyar = _icerik(is_, b)
    adaylar, renk_uyar = _adaylar(b, c, renkler)
    uyar += renk_uyar
    by = {a[0]: a for a in adaylar}
    en_cok = 1 if is_.no == 1 else 2

    def uygun(secilen, aday):
        return sum(1 for _, oz in secilen if oz["sablon"] == aday[1]["sablon"]) < en_cok

    sira = ogrenme.sec(KOD, [(i, oz) for i, oz, _ in adaylar], len(adaylar), haric=is_.haric,
                       tohum=random.randrange(1 << 30), uygun=uygun)
    is_.ilerle(5, f"{len(adaylar)} aday sıralandı; tasarımlar kuruluyor ve denetleniyor")
    kabul, yedek, denenen, denendi = [], [], 0, set()
    for sinir in (en_cok, en_cok + 1):                 # bir düzen hiç geçemezse eksik yer ikinci turda dolar
        for imza in sira:
            if len(kabul) + len(yedek) >= KATALOG_ADET or denenen >= 30:
                break
            par = by[imza][2]
            if imza in denendi or sum(1 for _, _, d in kabul + yedek if d.duzen == par["duzen"]) >= sinir:
                continue
            denendi.add(imza)
            denenen += 1
            d = _kur(c, par)
            sorun, _ = T.kontrol(d)
            if sorun:
                continue
            (yedek if d.zayif or T.kalite(d) < 0.7 else kabul).append((imza, par, d))
            is_.ilerle(5 + 50 * (len(kabul) + len(yedek)) / KATALOG_ADET,
                       f"{len(kabul) + len(yedek)} tasarım hazır ({denenen} denendi)")
    kabul += yedek[:KATALOG_ADET - len(kabul)]
    if not kabul:
        raise SystemExit("Bu bilgilerle baskıya uygun tasarım çıkmadı: unvan ya da kurum adını kısaltıp yeniden "
                         "deneyin.")
    bas = len(is_.haric) + 1
    klasor = is_.yol(f"katalog_{is_.no}", "x")[:-2]
    tasarimlar, sayfa = [], []
    for i, (imza, par, d) in enumerate(kabul):
        kod = f"K{bas + i:02d}"
        is_.ilerle(55 + 37 * i / len(kabul), f"{kod} çiziliyor")
        im = T.gorunus(T.S.solids(d), par["govde"], 900)
        yol = os.path.join(klasor, f"{kod}.png")
        im.save(yol)
        tasarimlar.append({"kod": kod, "ad": T.ad(d), "ozellikler": by[imza][1], "onizleme": is_.goreli(yol),
                           "imza": imza, "parametreler": par, "uyarilar": d.uyarilar + d.zayif})
        sayfa.append((kod, T.ad(d), im))
        uyar += [f"{kod}: {w}" for w in d.uyarilar if "sığmadı" in w][:1]
    is_.ilerle(93, "Katalog sayfaları yapılıyor")
    giris = (f"{ad(b)} için kurumsal isimlik önerileri: 20 × 10 cm, yazılar kabartma, QR telefonla okutunca dijital "
             "kartvizit sayfasını açar (arama, WhatsApp, e-posta, rehbere kaydet).")
    bilgi = ("Ürün", ["Ölçü 20 × 10 cm, gövde 5 mm, köşeler yuvarlak.",
                      "Yazılar ve logo 2 mm kabartma; QR düz ve keskin, her telefonda okunur.",
                      "Masa sehpası dahil (gövde renginde): isimlik 15° eğik durur.",
                      "QR dijital kartvizitinizi açar: tek dokunuşla arama, WhatsApp, e-posta, rehbere kaydet.",
                      "Renkler değiştirilebilir, kurum logonuz eklenebilir."])
    pdf, jpgs = KT.yap(klasor, "Kurumsal isimlik", ad(b), is_.no, sayfa, giris, bilgi,
                       alt_not="Beğendiğiniz tasarımın kodunu (ör. K03) yazmanız yeterli.")
    return {"tasarimlar": tasarimlar, "pdf": is_.goreli(pdf), "sayfalar": [is_.goreli(j) for j in jpgs],
            "uyarilar": sorted(set(uyar))[:6]}


# ---------------------------------------------------------------- baskı dosyası ve kartvizit sayfası

def _musteri_onizleme(d, parts, path, baslik, alt):
    from PIL import Image, ImageDraw, ImageFont

    from atolye.tasarim import isimlik20 as T
    from atolye.tasarim import ortak as O
    on = O.A.fit_into(T.gorunus(parts, d.palet.govde, 1400), 1100, 520)
    iso = O.A.fit_into(T.gorunus(parts, d.palet.govde, 1300, (-28, -68), None), 900, 460)
    canvas = Image.new("RGB", (1200, 1240), (244, 241, 234))
    dr = ImageDraw.Draw(canvas)
    f = os.path.join(O.A.FONT_DIR, "SpaceGrotesk_700Bold.ttf")
    dr.text((60, 40), "KURUMSAL İSİMLİK 20 × 10", fill=(255, 90, 31), font=ImageFont.truetype(f, 24))
    dr.text((60, 76), baslik, fill=(18, 19, 22), font=ImageFont.truetype(f, 44))
    canvas.paste(on, ((1200 - on.width) // 2, 160), on)
    canvas.paste(iso, ((1200 - iso.width) // 2, 700), iso)
    dr.text((60, 1190), alt, fill=(85, 87, 92),
            font=ImageFont.truetype(os.path.join(O.A.FONT_DIR, "SpaceGrotesk_500Medium.ttf"), 22))
    canvas.save(path)


def uret(is_, secilen):
    import shutil
    import zipfile

    from atolye import site
    from atolye.tasarim import isimlik20 as T
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
    uyar += d.uyarilar

    is_.ilerle(10, "3MF yazılıyor")
    plate = T.Plaka(d, f"kurumsal_{adi}_{kod.lower()}_x2d", f"BOYDE_kurumsal_isimlik_{adi}_{kod}")
    out = is_.yol("cikti", "x")[:-2]
    template = zipfile.ZipFile(A.TEMPLATE)
    path, _, filaments = A.write_design(plate, {n: template.read(n) for n in template.namelist()}, out)
    parts = plate.solids()
    ok_place, place = T.tabla_kontrol(plate, parts)
    is_.ilerle(30, "QR okunuyor (üstten görünüş ve baskı hatası benzetimi)")
    qr = BI.qr_check(plate, c.url)
    g_txt = ""
    if shutil.which("prusa-slicer"):
        is_.ilerle(40, "Dilimleyicide deneniyor (PrusaSlicer)")
        dx, dy = plate.offset
        raised_z = [(round(B.T + 0.2, 2), "kenar"), (round(B.T + B.RELIEF, 2), "yüzey")]
        g, sure, rows, ok = BI.slice_check(plate, path, filaments, lambda cs: cs.translate((dx, dy)), raised_z,
                                           round(B.T, 2), os.path.join(out, "olcum.json"))
        g_txt = f"Filament ~{sum(g.values()):.0f} g + kule · ~{sure} · "
        if not ok:
            bad = [r[0] for r in rows if not BI.row_ok(r[0], r[2], r[3], r[4], r[6])]
            uyar.append("Dilimleyici: şu yazılar tam basılmıyor olabilir: " + ", ".join(sorted(set(bad))))
    else:
        uyar.append("PrusaSlicer kurulu değil: dilimleyici denetimi atlandı (harf ölçüleri ve QR denetlendi)")
    if not all(qr):
        uyar.append(f"QR denetimi: okundu {qr[0]}, baskı hatası benzetiminde {qr[1]} — önizlemeyi okutun")
    if not ok_place:
        uyar.append("Tabla yerleşimi: " + place)

    is_.ilerle(55, "Önizlemeler çiziliyor")
    p = d.palet
    renk = " · ".join(f"{i + 1} {A.COLOUR_NAMES[f]}" for i, f in enumerate(filaments))
    info = [f"Tek takım (panel + sehpa) · panel 200 × 100 mm, {O.AD[p.govde]} gövde 5 mm · yazılar {B.RELIEF:.0f} mm "
            f"kabartma · QR yüzeyle aynı hizada · tasarım {kod} ({d.duzen})",
            f"AMS: {renk} · ana nozul: {O.AD[p.govde]} (gövde, sehpa) · yardımcı nozul: {O.AD[p.yazi]}, "
            f"{O.AD[p.vurgu]}",
            "Bambu standart 0,20 mm · ütüleme kapalı · destek yok · Textured PEI · panel yüzü yukarı, sehpa önünde",
            f"{g_txt}QR {c.url} {'okunuyor' if all(qr) else 'SORUNLU'} · harf içi ve ara en az 0,7 mm "
            f"{'tamam' if not sorun else 'SORUNLU'} · yerleşim {'tamam' if ok_place else 'SORUNLU'}"]
    T.tabla_resmi(plate, parts, os.path.join(out, "tabla.png"), info,
                  f"{ad(b).upper()} – KURUMSAL İSİMLİK 20 × 10 ({kod}) · X2D BASKI DOSYASI")
    _musteri_onizleme(d, plate.panel, os.path.join(out, "onizleme.png"), ad(b),
                      "20 × 10 cm · 5 mm gövde · kabartma yazı · masa sehpası dahil · BOYDE LABS")

    is_.ilerle(70, "Kartvizit sayfası hazırlanıyor")
    isaret = "logo/isaret.svg" if c.simge == "logo" and os.path.exists(is_.yol("web", "logo", "isaret.svg")) else None
    sb, uy = site.bilgiler(dict(b, isletme=ad(b)), is_.klasor, ad(b), O.tr_upper(c.hizmet), O.WEB[p.vurgu], adi,
                           isaret)
    uyar += uy
    if c.kurum:
        sb["kurum"] = c.kurum
        sb["etiket"] = O.tr_upper(c.kurum)
    eposta = (b.get("eposta") or "").strip()
    if eposta:
        if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", eposta):
            sb["eposta"] = eposta
        else:
            uyar.append(f"E-posta geçersiz, sayfaya konmadı: {eposta}")
    try:
        ws = site.yap(is_, sb, int(b.get("sablon") or 0))
        site_cikti = ws["ciktilar"]
        uyar += ws["uyarilar"]
        uyar.append(f"Yayın: Cloudflare'de (hesap {site.HESAP}) '{ws['ad']}' adlı Worker'a zip'i yükleyin → {ws['url']} "
                    f"(QR bu adresi açar; şablon {ws['sablon']} · {ws['sablon_ad']})")
    except Exception as e:                           # noqa: BLE001 (site olmadan da 3MF teslim edilir)
        site_cikti = []
        uyar.append(f"Kartvizit sayfası üretilemedi: {e}")
    is_.ilerle(96, "Bitti")
    return {"ciktilar": [{"ad": f"X2D baskı dosyası (3MF, tek takım) · {kod}", "yol": is_.goreli(path), "tur": "3mf"},
                         {"ad": "Müşteri önizlemesi", "yol": is_.goreli(os.path.join(out, "onizleme.png")),
                          "tur": "resim"},
                         {"ad": "Tabla yerleşimi ve kontroller", "yol": is_.goreli(os.path.join(out, "tabla.png")),
                          "tur": "resim"}] + site_cikti,
            "uyarilar": uyar}
