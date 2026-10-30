"""Toptan anahtarlık: müşterinin markasıyla 20 tasarımlık katalog → seçilen kod → X2D 3MF (dolu tabla ve tek deneme).

Tasarımlar atolye/tasarim/anahtarlik.py'deki 8 biçimden (klasik, dikey, kare, bar, kesik köşe, kapsül, yuvarlak, bavul
etiketi) ve 3 dizilimden (simge solda, simge üstte, yalnız ad) kurulur: ön yüz kabartma, arka yüz gömme yazı (telefon,
Instagram, adres...). Katalogda bir biçim en çok üç kez; gövde, renk ve yazı tipi öğrenmeye göre (beğenilenler öne
çıkar, %30 keşif); bu müşteriye gösterilenler yeni katalogda tekrar edilmez. Ad bir biçime küçük kalıyorsa o biçim
geri düşer, sığmıyorsa hiç gösterilmez; her tasarım baskıya uygunluk denetiminden geçer.

Seçilen kodla (müşteri klasöründe, cikti/):
  anahtarlik_<ad>_<kod>_tabla.3mf    dolu tabla (iki nozulun ortak alanında ızgara, kule sol arkada)
  anahtarlik_<ad>_<kod>_deneme.3mf   tek adet (önce bir deneme basmak için)
  onizleme.png                       müşteriye: ön ve arka yüz
  tabla.png                          tabla yerleşimi; tabla başına adet, sipariş için kaç tabla, filament
"""
import os

KOD = "anahtarlik"
AD = "Toptan anahtarlık"
SIMGE = "🔑"
ACIKLAMA = ("Müşterinin markasıyla arkalı önlü anahtarlık: ön yüz kabartma, arka yüz gömme yazı. 20 tasarımlık "
            "katalog; seçilen tasarımın dolu tabla X2D 3MF'i ve sipariş adedine göre kaç tabla gerektiği.")
KATALOG_ADET = 20
YAZI_TIPLERI = ["outfit", "bebas", "mont", "oswald", "sora", "archivo"]


def _secenekler():
    from atolye.tasarim import isimlik9 as T
    from atolye.tasarim import ortak as O
    sektor = [(k, v[0]) for k, v in T.SEKTORLER.items()]
    renkler = (O.RED, O.ORANGE, O.YELLOW, O.GOLD, O.TURQ, O.BLUE, O.NAVY, O.GREEN, O.PINK, O.PURPLE, O.GRAY)
    zemin = [("otomatik", "Otomatik (katalogda farklı gövdeler)"), ("siyah", "Siyah"), ("beyaz", "Beyaz")] + [
        (O.AD[c], O.AD[c].capitalize()) for c in renkler]
    yazi = [("otomatik", "Otomatik (koyu gövdede beyaz, açıkta siyah)"), ("siyah", "Siyah"), ("beyaz", "Beyaz")] + [
        (O.AD[c], O.AD[c].capitalize()) for c in renkler]
    renk = [("otomatik", "Otomatik")] + [(O.AD[c], O.AD[c].capitalize()) for c in renkler + (O.WHITE, O.BLACK)]
    return sektor, zemin, yazi, renk


try:
    _SEKTOR, _ZEMIN, _YAZI, _RENK = _secenekler()
except Exception:                                      # noqa: BLE001 (tasarım modülleri yüklenemezse form yine açılır)
    _SEKTOR, _ZEMIN, _YAZI, _RENK = [("genel", "Genel")], *[[("otomatik", "Otomatik")]] * 3

ALANLAR = [
    {"ad": "marka", "etiket": "Ön yüzdeki ad (marka)", "tur": "text", "zorunlu": True, "grup": "Anahtarlık",
     "ornek": "KARDEŞLER", "ipucu": "Kısa ad büyük yazılır; uzun adlar dar yazı tipleriyle ya da iki satırla sığar."},
    {"ad": "alt", "etiket": "Adın altında küçük yazı", "tur": "text", "ornek": "OTO YIKAMA",
     "ipucu": "İsteğe bağlı; sığmayan biçimlerde yazılmaz."},
    {"ad": "sektor", "etiket": "Sektör (simge ve renkler)", "tur": "select", "secenekler": _SEKTOR,
     "varsayilan": "genel", "zorunlu": True},
    {"ad": "logo", "etiket": "Logo (isteğe bağlı)", "tur": "dosya", "kabul": "image/png,image/jpeg",
     "ipucu": "Düz zeminde tek renk logo en iyisi; simgenin yerine kabartma olur."},
    {"ad": "arka", "etiket": "Arka yüz yazıları", "tur": "textarea",
     "ornek": "0532 123 45 67\n@kullaniciadi\nKepez · Antalya",
     "ipucu": "Satır satır, en çok 3. Biçime sığmayan satır yazılmaz (uyarı verilir)."},
    {"ad": "adet", "etiket": "Sipariş adedi", "tur": "sayi", "zorunlu": True, "varsayilan": "100", "min": 1},
    {"ad": "zemin", "etiket": "1. renk: gövde", "tur": "select", "secenekler": _ZEMIN, "varsayilan": "otomatik",
     "grup": "Renkler (3 renk)"},
    {"ad": "yazi_renk", "etiket": "2. renk: yazı (ad ve arka yüz)", "tur": "select", "secenekler": _YAZI,
     "varsayilan": "otomatik", "ipucu": "Gövdede okunmayan yazı rengi (sarı gövdede beyaz gibi) seçilirse uyarı çıkar."},
    {"ad": "renk", "etiket": "3. renk: vurgu (simge, alt yazı)", "tur": "select", "secenekler": _RENK,
     "varsayilan": "otomatik"},

    {"ad": "yetkili", "etiket": "Yetkili", "tur": "text", "grup": "Kayıt (anahtarlığa yazılmaz)"},
    {"ad": "yetkili_tel", "etiket": "Yetkilinin telefonu", "tur": "tel"},
    {"ad": "not", "etiket": "Sipariş notu", "tur": "textarea"},
]


def ad(b):
    return " ".join(b["marka"].split())


class _Icerik:
    def __init__(self, marka, alt, simge, logo):
        self.marka, self.alt, self.simge, self.logo = marka, alt, simge, logo


def _icerik(is_, b):
    from atolye.tasarim import isimlik9 as T
    from atolye.tasarim import logo as L
    from atolye.tasarim import ortak as O
    uyar = []
    _, simge, _, renkler = T.SEKTORLER.get(b.get("sektor") or "genel", T.SEKTORLER["genel"])
    logo = None
    if b.get("logo"):
        try:
            logo, _ = L.izle(os.path.join(is_.klasor, b["logo"]))
            simge = "logo"
        except Exception as e:                       # noqa: BLE001
            uyar.append(f"Logo okunamadı, sektör simgesi kullanıldı: {e}")
    alt = O.tr_upper(" ".join((b.get("alt") or "").split()))
    arka = [" ".join(x.split()) for x in (b.get("arka") or "").splitlines() if x.strip()][:3]
    return _Icerik(ad(b), alt, simge, logo), renkler, arka, uyar


def _paletler(b, renkler):
    """3 renk: [(gövde, yazı, vurgu)] ve uyarılar. Seçilen renkler sabit. Gövde seçilmediyse siyah, beyaz, gri ve
    sektörün ilk rengi; yazı seçilmediyse gövdeye göre siyah ya da beyaz (seçilen yazı rengi bir gövdede okunmuyorsa o
    gövde atlanır); vurgu seçilmediyse sektörün renkleri (renkli gövdede gövdeye zıt siyah ya da beyaz)."""
    from atolye.tasarim import ortak as O
    zemin = O.KIMLIK.get(b.get("zemin") or "otomatik")
    yazi = O.KIMLIK.get(b.get("yazi_renk") or "otomatik")
    sabit = O.KIMLIK.get(b.get("renk") or "otomatik")
    uyar = []
    if zemin and yazi and O.kontrast(zemin, yazi) < O.OKUNUR:
        uyar.append(f"Yazı rengi ({O.AD[yazi]}) {O.AD[zemin]} gövdede zor okunur; yine de seçildiği gibi yapıldı.")
    govdeler = [zemin] if zemin else [O.BLACK, O.WHITE, O.GRAY, renkler[0]]
    out = []
    for g in govdeler:
        p = O.Palet(g, O.WHITE, yazi=yazi or 0)
        if yazi and not zemin and O.kontrast(g, yazi) < O.OKUNUR:
            continue
        if sabit:
            vurgular = [sabit]
        elif g in (O.BLACK, O.WHITE, O.GRAY):
            uygun = O.KOYUDA if p.koyu else [r for r in O.ACIKTA if g != O.GRAY or r not in (O.GOLD, O.TURQ)]
            vurgular = [r for r in renkler if r in uygun and r not in (g, p.yazi)][:2] or [O.ORANGE]
        else:                                                   # renkli gövdede vurgu gövdeye zıt
            vurgular = [x for x in ((O.BLACK, O.WHITE) if p.koyu else (O.WHITE, O.BLACK)) if x != p.yazi][:1]
        out += [(g, p.yazi, v) for v in vurgular if v != g and (sabit or v != p.yazi)]
    if not out and yazi:
        uyar.append(f"Yazı rengi ({O.AD[yazi]}) gövdelerin hiçbirinde okunmuyor; yazı rengi otomatik seçildi.")
        return _paletler({**b, "yazi_renk": "otomatik"}, renkler)[0], uyar
    return out or [(O.BLACK, O.WHITE, O.ORANGE)], uyar


def _kalite_tahmini(c, bicim, dizilim, yazi_tipi):
    """Adın bu biçimde alacağı boy, kurmadan (yalnız harf genişlikleri): 0..1."""
    from atolye.tasarim import anahtarlik as K
    from atolye.tasarim import ortak as O
    _, _, kutu, _ = K.BICIMLER[bicim][1]()
    W, H = kutu[2] - kutu[0], kutu[3] - kutu[1]
    aw = W - (min(H * 1.1, W * 0.3) + 2.4 if dizilim == "yan" else 0.0)
    pay = {"yazi": 0.56, "yan": 0.46, "ust": 0.3}[dizilim] * H * (0.82 if c.alt else 1.0)
    _, cap = K._ad_satirlari(O.ad_metni(c.marka, yazi_tipi), yazi_tipi, pay, aw)
    return min(1.0, cap / (0.8 * pay)) if cap else 0.0


def _kur(c, arka, par):
    from atolye.tasarim import anahtarlik as K
    from atolye.tasarim import ortak as O
    return K.tasarla(par["bicim"], par["dizilim"], c, O.Palet(par["govde"], par["vurgu"], yazi=par.get("metin", 0)),
                     par["yazi"], arka)


def _ad_kart(par):
    from atolye.tasarim import anahtarlik as K
    from atolye.tasarim import ortak as O
    yazi = O.Palet(par["govde"], par["vurgu"], yazi=par.get("metin", 0)).yazi
    return (f"{K.BICIMLER[par['bicim']][0]} · {O.AD[par['govde']]}, {O.AD[yazi]}, {O.AD[par['vurgu']]} · "
            f"{O.YAZI_AD.get(par['yazi'], par['yazi'])}")


def _resim(k, boy=520):
    """Ön ve arka yüz yan yana (RGBA)."""
    from PIL import Image

    from atolye.tasarim import anahtarlik as K
    on, ar = K.gorunus(k, boy), K.gorunus(k, boy, arka=True)
    im = Image.new("RGBA", (on.width + ar.width + 30, max(on.height, ar.height)), (0, 0, 0, 0))
    im.paste(on, (0, 0), on)
    im.paste(ar, (on.width + 30, 0), ar)
    return im


# ---------------------------------------------------------------- katalog

def katalog(is_):
    import random

    from atolye import ogrenme
    from atolye.tasarim import anahtarlik as K
    from atolye.tasarim import katalog as KT
    from atolye.tasarim import ortak as O
    b = is_.bilgiler
    c, renkler, arka, uyar = _icerik(is_, b)
    is_.ilerle(4, "Biçimler bu ada göre deneniyor")
    paletler, renk_uyar = _paletler(b, renkler)
    uyar += renk_uyar
    kal, adaylar = {}, []
    simge = c.simge if c.simge in ("logo", "monogram") else "simge"
    for bicim, (_, _, dizilimler) in K.BICIMLER.items():
        for dz in dizilimler:
            for f in YAZI_TIPLERI:
                q = kal[(bicim, dz, f)] = _kalite_tahmini(c, bicim, dz, f)
                if q < 0.45:
                    continue
                for g, y, v in paletler:
                    oz = {"bicim": bicim, "dizilim": dz, "zemin": O.AD[g], "metin": O.AD[y], "renk": O.AD[v],
                          "yazi": f, "simge": simge}
                    par = {"bicim": bicim, "dizilim": dz, "govde": g, "vurgu": v, "metin": y, "yazi": f}
                    oto = y == O.Palet(g, v).yazi                       # otomatik yazı rengi: eski imza
                    adaylar.append((f"{bicim}|{dz}|{O.AD[g]}|{O.AD[v]}|{f}" + ("" if oto else f"|{O.AD[y]}"), oz, par))
    if not adaylar:
        raise SystemExit("Ad hiçbir biçime okunur boyda sığmadı: 'Ön yüzdeki ad' alanına daha kısa bir ad yazın.")
    by = {a[0]: a for a in adaylar}

    def uygun(secilen, aday):
        oz = aday[1]
        return (sum(1 for _, o in secilen if o["bicim"] == oz["bicim"]) < 3 and
                sum(1 for _, o in secilen if (o["bicim"], o["dizilim"]) == (oz["bicim"], oz["dizilim"])) < 2)

    sira = ogrenme.sec(KOD, [(i, oz) for i, oz, _ in adaylar], len(adaylar), haric=is_.haric,
                       tohum=random.randrange(1 << 30), uygun=uygun,
                       agirlik=lambda imza: kal[(by[imza][2]["bicim"], by[imza][2]["dizilim"], by[imza][2]["yazi"])] ** 3)
    is_.ilerle(8, f"{len(adaylar)} aday sıralandı; tasarımlar kuruluyor ve denetleniyor")
    kabul, eksik, denenen = [], [], 0          # eksik: arka yüz satırlarından biri sığmamış (yedek)
    for imza in sira:
        if len(kabul) >= KATALOG_ADET or denenen >= 45:
            break
        par = by[imza][2]
        if sum(1 for _, p, _ in kabul if p["bicim"] == par["bicim"]) >= 3:
            continue
        denenen += 1
        k = _kur(c, arka, par)
        if not k.kalite or K.kontrol(k):
            continue
        if any(w.startswith("arka yüze") for w in k.uyarilar):
            eksik.append((imza, par, k))
            continue
        kabul.append((imza, par, k))
        is_.ilerle(8 + 42 * len(kabul) / KATALOG_ADET, f"{len(kabul)} tasarım hazır ({denenen} denendi)")
    for e in eksik:                            # tam tasarım yetmediyse arka yazısı eksik olanlar (uyarıyla)
        if len(kabul) < KATALOG_ADET and sum(1 for _, p, _ in kabul if p["bicim"] == e[1]["bicim"]) < 3:
            kabul.append(e)
    if not kabul:
        raise SystemExit("Bu bilgilerle baskıya uygun anahtarlık çıkmadı: daha kısa bir ad deneyin.")
    bas = len(is_.haric) + 1
    klasor = is_.yol(f"katalog_{is_.no}", "x")[:-2]
    tasarimlar, sayfa = [], []
    for i, (imza, par, k) in enumerate(kabul):
        kod = f"A{bas + i:02d}"
        is_.ilerle(50 + 42 * i / len(kabul), f"{kod} çiziliyor")
        im = _resim(k)
        yol = os.path.join(klasor, f"{kod}.png")
        im.save(yol)
        tasarimlar.append({"kod": kod, "ad": _ad_kart(par), "ozellikler": by[imza][1], "onizleme": is_.goreli(yol),
                           "imza": imza, "parametreler": par, "uyarilar": k.uyarilar})
        sayfa.append((kod, _ad_kart(par), im))
    is_.ilerle(93, "Katalog sayfaları yapılıyor")
    giris = (f"{ad(b)} için arkalı önlü anahtarlık önerileri: her kartta solda ön yüz (kabartma), sağda arka yüz "
             "(gömme yazı). Renkler ve yazılar değiştirilebilir.")
    bilgi = ("Ürün", ["3,2 mm gövde, kenarları pahlı; ön yüzde yazı ve simge 0,8 mm kabartma.",
                      "Arka yüzde yazılar yüzeyle aynı hizada, renkli ve keskin (silinmez).",
                      "Anahtarlık halkası ve zinciriyle teslim edilir.",
                      "Logonuz eklenebilir; toptan siparişte adet arttıkça fiyat düşer."])
    pdf, jpgs = KT.yap(klasor, "Toptan anahtarlık", ad(b), is_.no, sayfa, giris, bilgi, sutun=2, satir=5,
                       alt_not="Beğendiğiniz tasarımın kodunu (ör. A07) yazmanız yeterli.")
    for t in tasarimlar:
        uyar += [f"{t['kod']}: {w}" for w in t["uyarilar"] if "sığmadı" in w][:1]
    return {"tasarimlar": tasarimlar, "pdf": is_.goreli(pdf), "sayfalar": [is_.goreli(j) for j in jpgs],
            "uyarilar": sorted(set(uyar))[:6]}


# ---------------------------------------------------------------- baskı dosyaları

def _plaka(k, key, title, yerler):
    from atolye.tasarim import anahtarlik as K
    from atolye.tasarim import ortak as O
    A = O.A

    class Plaka:
        pass

    p = Plaka()
    p.key, p.title, p.instances = key, title, yerler
    parca = k.solids()
    p.solids = lambda: parca
    pal = k.palet
    p.nozzle_map = {pal.govde: 1, pal.vurgu: 1, pal.yazi: 2}   # gövde ve vurgu ana nozulda, yazı rengi yardımcıda
    p.filament_profiles = {c: A.GENERIC_PLA for c in p.nozzle_map}
    p.object_settings = {"enable_support": "0", "ironing_type": "no ironing"}
    p.tower_xy = K.KULE
    p.project_overrides = {"curr_bed_type": "Textured PEI Plate",
                           "wipe_tower_x": [f"{K.KULE[0]:g}"], "wipe_tower_y": [f"{K.KULE[1]:g}"]}
    return p


def _tabla_resmi(k, yerler, path, satirlar):
    from PIL import Image, ImageDraw, ImageFont

    from atolye.tasarim import anahtarlik as K
    from atolye.tasarim import ortak as O
    from cift_tarafli_isimlik import render
    import manifold3d as m3
    A = O.A
    bed = m3.Manifold.cube((256, 256, 0.2)).translate((0, 0, -0.4))
    kule = m3.Manifold.cube((40, 40, 4)).translate((K.KULE[0], K.KULE[1], 0))
    mesh = [(*A.mesh_arrays(bed), (205, 208, 214)), (*A.mesh_arrays(kule), (150, 156, 168))]
    for _, m, c in k.solids():
        V, T = A.mesh_arrays(m)
        mesh += [(A.placed(V, *y), T, O.TON[c]) for y in yerler]
    im = A.fit_into(render(mesh, 1100, A.R_TOP, flat=0.75, margin=0.02), 760, 760)
    canvas = Image.new("RGB", (1400, 860), (236, 239, 244))
    canvas.paste(im, (30, 70), im)
    dr = ImageDraw.Draw(canvas)
    f = os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf")
    dr.text((30, 18), satirlar[0], fill=(24, 26, 30), font=ImageFont.truetype(f, 30))
    y = 90
    for s in satirlar[1:]:
        for line in _sar(s, 46):
            dr.text((830, y), line, fill=(60, 64, 72), font=ImageFont.truetype(f, 21))
            y += 30
        y += 10
    canvas.save(path)


def _sar(s, n):
    out, cur = [], ""
    for w in s.split():
        if cur and len(cur) + len(w) + 1 > n:
            out.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    return out + ([cur] if cur else [])


def uret(is_, secilen):
    import zipfile

    from PIL import Image, ImageDraw, ImageFont

    from atolye.kayit import slug
    from atolye.tasarim import anahtarlik as K
    from atolye.tasarim import ortak as O
    A = O.A
    b = is_.bilgiler
    kod = secilen["kod"]
    c, _, arka, uyar = _icerik(is_, b)
    k = _kur(c, arka, secilen["parametreler"])
    sorun = K.kontrol(k) if k.kalite else ["ad bu biçime sığmadı"]
    if sorun:
        uyar.append("Baskıya uygunluk: " + "; ".join(sorun))
    uyar += k.uyarilar
    adi = slug(ad(b), 24).replace("-", "_")
    out = is_.yol("cikti", "x")[:-2]
    w, h = k.size()
    yerler = K.tabla_yerleri(w, h)
    adet = max(1, int(float(b.get("adet") or 1)))
    tabla = K.kac_tabla(adet, len(yerler))
    template = zipfile.ZipFile(A.TEMPLATE)
    tf = {n: template.read(n) for n in template.namelist()}
    is_.ilerle(15, f"Dolu tabla 3MF'i yazılıyor ({len(yerler)} adet)")
    dolu, _, filaments = A.write_design(_plaka(k, f"anahtarlik_{adi}_{kod.lower()}_tabla",
                                               f"BOYDE_anahtarlik_{adi}_{kod}_tabla", yerler), tf, out)
    is_.ilerle(55, "Tek adetlik deneme 3MF'i yazılıyor")
    deneme, _, _ = A.write_design(_plaka(k, f"anahtarlik_{adi}_{kod.lower()}_deneme",
                                         f"BOYDE_anahtarlik_{adi}_{kod}_deneme", [(128.0, 128.0, 0)]), tf, out)
    g = K.gram(k.solids(), len(yerler))
    g_txt = ", ".join(f"{O.AD[c_]} {v:.0f} g" for c_, v in g.items())
    renk = " · ".join(f"{i + 1} {A.COLOUR_NAMES[f]}" for i, f in enumerate(filaments))
    pal = k.palet
    is_.ilerle(75, "Önizlemeler çiziliyor")
    satirlar = [f"{ad(b).upper()} – ANAHTARLIK {kod} · X2D DOLU TABLA",
                f"{K.BICIMLER[k.bicim][0]} mm · gövde {O.AD[pal.govde]} 3,2 mm · ön kabartma 0,8 mm "
                f"({O.AD[pal.yazi]}, {O.AD[pal.vurgu]}) · arka gömme yazı {O.AD[pal.yazi]}",
                f"Tabla başına {len(yerler)} adet · {adet} adet için {tabla} tabla "
                f"(son tablada {adet - (tabla - 1) * len(yerler)} adet yeter; fazlası yedek)",
                f"AMS: {renk} · ana nozul: {O.AD[pal.govde]}, {O.AD[pal.vurgu]} · yardımcı nozul: {O.AD[pal.yazi]}",
                f"Filament (bir tabla, tahmini): {g_txt} + kule",
                "Bambu standart 0,20 mm · ütüleme kapalı · destek yok · Textured PEI · arka yüz tablada",
                "Önce tek adetlik deneme dosyasını basıp renkleri ve yazıları kontrol edin."]
    _tabla_resmi(k, yerler, os.path.join(out, "tabla.png"), satirlar)
    im = _resim(k, 900)
    fit = A.fit_into(im, 1300, 520)
    canvas = Image.new("RGB", (1400, fit.height + 230), (244, 241, 234))
    canvas.paste(fit, ((1400 - fit.width) // 2, 130), fit)
    dr = ImageDraw.Draw(canvas)
    f = os.path.join(A.FONT_DIR, "SpaceGrotesk_700Bold.ttf")
    dr.text((50, 30), "ANAHTARLIK · ÖN VE ARKA YÜZ", fill=(255, 90, 31), font=ImageFont.truetype(f, 24))
    dr.text((50, 64), f"{ad(b)} · {kod}", fill=(18, 19, 22), font=ImageFont.truetype(f, 40))
    dr.text((50, canvas.height - 50), f"{K.BICIMLER[k.bicim][0]} mm · ön yüz kabartma, arka yüz gömme yazı · BOYDE LABS",
            fill=(85, 87, 92), font=ImageFont.truetype(os.path.join(A.FONT_DIR, "SpaceGrotesk_500Medium.ttf"), 22))
    canvas.save(os.path.join(out, "onizleme.png"))
    uyar.append(f"Tabla başına {len(yerler)} adet; {adet} adet için {tabla} tabla basılır")
    is_.ilerle(96, "Bitti")
    return {"ciktilar": [{"ad": f"X2D dolu tabla ({len(yerler)} adet) · {kod}", "yol": is_.goreli(dolu), "tur": "3mf"},
                         {"ad": "X2D tek adet (deneme baskısı)", "yol": is_.goreli(deneme), "tur": "3mf"},
                         {"ad": "Müşteri önizlemesi (ön ve arka)", "yol": is_.goreli(os.path.join(out, "onizleme.png")),
                          "tur": "resim"},
                         {"ad": "Tabla yerleşimi ve hesap", "yol": is_.goreli(os.path.join(out, "tabla.png")),
                          "tur": "resim"}],
            "uyarilar": uyar, "bilgi": {"tabla_basi": len(yerler), "tabla": tabla, "gram": g}}

