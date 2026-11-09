"""Kişiye özel plakalı anahtarlık (Türk plakası biçiminde): plaka, alttaki yazı ve TR bandının rengi girilir; X2D 3MF
hazır. Katalog yok (tasarım sabit; Shopier'deki ürün, scripts/boyde_plakali_anahtarlik.py).

70 × 22 × 3 mm: siyah çerçeve ve alt şerit, beyaz plaka zemini, kırmızı ya da mavi TR bandı (beyaz TR); plaka yazısı
1,3 mm, alttaki yazı 1 mm kabartma. Arka yüz tamamen siyah (zeminin ve bandın altında 0,4 mm siyah taban). Plaka büyük harfe çevrilir ve 34 ABC 123 biçimine getirilir (boşluksuz yazılsa da);
alışılmış biçimde değilse yazıldığı gibi basılır, uyarı verilir. Uzun yazı şeride sığacak kadar küçülür; çok küçülüp
ince kalırsa (0,7 mm'den ince yerler) uyarı verilir.

Çıktılar (müşteri klasöründe, cikti/):
  plakali_<plaka>_tabla.3mf    sipariş adedi kadar (tablaya sığmıyorsa dolu tabla: iki nozulun ortak alanında ızgara,
                               kule sol arkada); AMS siyah, beyaz, bant rengi · siyah ve bant ana nozulda, beyaz
                               yardımcıda. Tek adetlik siparişte yalnız bu dosya (adı _tek).
  plakali_<plaka>_deneme.3mf   tek adet (önce bir deneme basmak için; birden çok adette)
  onizleme.png                 müşteriye: ön ve arka yüz
  tabla.png                    tabla yerleşimi; tabla başına adet, sipariş için kaç tabla, filament
"""
import os
import re

KOD = "plakali"
KATEGORI = "anahtarlik"                     # arayüzde ürünün bölümü (Yeni sipariş, Müşteriler süzgeci)
AD = "Plakalı anahtarlık"
SIMGE = "🚘"
ACIKLAMA = ("Kişiye özel Türk plakası: plaka ve altında ad ya da söz kabartma, kırmızı ya da mavi TR bandı "
            "(70 × 22 mm). Plakayı yazın; sipariş adedi kadar X2D 3MF hemen hazırlanır.")
KATALOG_ADET = 0
BANTLAR = [("kirmizi", "Kırmızı"), ("mavi", "Mavi")]
ALANLAR = [
    {"ad": "plaka", "etiket": "Plaka", "tur": "text", "zorunlu": True, "grup": "Anahtarlık", "ornek": "34 ABC 123",
     "ipucu": "Boşluksuz yazılsa da 34 ABC 123 biçimine getirilir."},
    {"ad": "yazi", "etiket": "Alttaki yazı (ad soyad ya da söz)", "tur": "text", "ornek": "ADINIZ SOYADINIZ",
     "ipucu": "İsteğe bağlı; büyük harfle yazılır. 16 harfe kadar tam boy, uzun yazı küçülür."},
    {"ad": "bant", "etiket": "TR bandının rengi", "tur": "select", "secenekler": BANTLAR, "varsayilan": "kirmizi",
     "zorunlu": True},
    {"ad": "adet", "etiket": "Adet", "tur": "sayi", "zorunlu": True, "varsayilan": "1", "min": 1,
     "ipucu": "Aynı plakadan kaç tane; tablaya sığmayan adetler için kaç tabla gerektiği hesaplanır."},

    {"ad": "musteri", "etiket": "Müşterinin adı", "tur": "text", "grup": "Kayıt (anahtarlığa yazılmaz)"},
    {"ad": "telefon", "etiket": "Müşterinin telefonu", "tur": "tel"},
    {"ad": "not", "etiket": "Sipariş notu", "tur": "textarea", "ornek": "Shopier sipariş no, kargo bilgisi..."},
]
MIN_AD = 4.0                  # alttaki yazının boyu (mm; işaretler dahil) bundan küçükse uyarı
INCE = 4.0                    # 0,7 mm'den ince kalan alan (mm²) bundan çoksa uyarı (Ş, Ç çengelleri tek başına değil)


def _mm(v):
    return f"{v:.1f}".replace(".", ",")


def plaka_yazisi(s):
    """Plakayı büyük harfe çevirip il kodu, harfler ve rakamlar arasına boşluk koyar. Döner (yazı, alışılmış mı):
    il kodu 01–81, 1–3 harf, 2–4 rakam."""
    from atolye.tasarim import ortak as O
    ham = " ".join(O.tr_upper(s or "").replace("İ", "I").split())
    m = re.fullmatch(r"(\d{2})([A-Z]{1,3})(\d{2,4})", ham.replace(" ", ""))
    if not m:
        return ham, False
    il, harf, no = m.groups()
    return f"{il} {harf} {no}", 1 <= int(il) <= 81


def alt_yazi(s):
    from atolye.tasarim import ortak as O
    return " ".join(O.tr_upper(s or "").split())


def ad(b):
    plaka = plaka_yazisi(b.get("plaka", ""))[0]
    kim = alt_yazi(b.get("yazi", "")) or " ".join((b.get("musteri") or "").split())
    return f"{plaka} · {kim}" if kim else plaka


class _Tasarim:
    """Baskı yönünde, tablada ortalanmış parçalar: [(ad, Manifold, renk)] (renk başına bir parça)."""

    def __init__(self, plaka, yazi, bant):
        import manifold3d as m3

        import boyde_plakali_anahtarlik as PA
        parcalar, self.olcu = PA.tasarla(plaka, yazi, bant)
        self.W, self.H = PA.W, PA.H
        self.siyah, self.beyaz, self.bant = PA.SIYAH, PA.BEYAZ, PA.BANT[bant]
        adlar = {self.siyah: "cerceve_plaka", self.beyaz: "zemin_tr_yazi", self.bant: "tr_bandi"}
        self.parcalar = []
        for c in (self.siyah, self.beyaz, self.bant):
            m = m3.Manifold.batch_boolean([p for _, p, r in parcalar if r == c], m3.OpType.Add)
            self.parcalar.append((adlar[c], m.translate((-PA.W / 2, -PA.H / 2, 0)), c))

    def solids(self):
        return self.parcalar


def _baski(t, key, title, yerler):
    from atolye.tasarim import anahtarlik as K
    from atolye.tasarim import ortak as O
    A = O.A

    class Plaka:
        pass

    p = Plaka()
    p.key, p.title, p.instances = key, title, yerler
    p.solids = t.solids
    p.nozzle_map = {t.siyah: 1, t.bant: 1, t.beyaz: 2}     # siyah ve bant ana nozulda, beyaz yardımcıda
    p.filament_profiles = {c: A.GENERIC_PLA for c in p.nozzle_map}
    p.object_settings = {"enable_support": "0", "ironing_type": "no ironing"}
    p.tower_xy = K.KULE
    p.project_overrides = {"curr_bed_type": "Textured PEI Plate",
                           "wipe_tower_x": [f"{K.KULE[0]:g}"], "wipe_tower_y": [f"{K.KULE[1]:g}"]}
    return p


def _onizleme(t, plaka, yazi, bant_ad, path):
    from PIL import Image, ImageDraw, ImageFont

    from atolye.tasarim import ortak as O
    from cift_tarafli_isimlik import render, rotation
    A = O.A
    mesh = [(*A.mesh_arrays(m), O.TON[c]) for _, m, c in t.solids()]
    on = A.fit_into(render(mesh, 1600, A.R_TOP, margin=0.02, ambient=0.62), 1240, 400)
    arka = A.fit_into(render(mesh, 1000, rotation(180, 180), margin=0.02, ambient=0.62), 560, 180)
    canvas = Image.new("RGB", (1400, 140 + on.height + 70 + arka.height + 110), (244, 241, 234))
    dr = ImageDraw.Draw(canvas)
    f = os.path.join(A.FONT_DIR, "SpaceGrotesk_700Bold.ttf")
    f2 = os.path.join(A.FONT_DIR, "SpaceGrotesk_500Medium.ttf")
    dr.text((50, 30), "PLAKALI ANAHTARLIK · ÖN VE ARKA YÜZ", fill=(255, 90, 31), font=ImageFont.truetype(f, 24))
    dr.text((50, 64), f"{plaka}" + (f" · {yazi}" if yazi else ""), fill=(18, 19, 22), font=ImageFont.truetype(f, 40))
    y = 140
    canvas.paste(on, ((1400 - on.width) // 2, y), on)
    y += on.height + 30
    dr.text(((1400 - arka.width) // 2, y), "Arka yüz (düz, siyah)", fill=(85, 87, 92), font=ImageFont.truetype(f2, 20))
    canvas.paste(arka, ((1400 - arka.width) // 2, y + 40), arka)
    dr.text((50, canvas.height - 50), f"70 × 22 × 3 mm · {bant_ad} TR bandı · plaka ve yazı kabartma · BOYDE LABS",
            fill=(85, 87, 92), font=ImageFont.truetype(f2, 22))
    canvas.save(path)


def uret(is_, secilen=None):
    import zipfile

    from atolye.kayit import slug
    from atolye.tasarim import anahtarlik as K
    from atolye.tasarim import ortak as O
    from atolye.urunler.anahtarlik import _tabla_resmi
    A = O.A
    b = is_.bilgiler
    plaka, olagan = plaka_yazisi(b.get("plaka", ""))
    if not plaka:
        raise SystemExit("Plaka boş")
    yazi = alt_yazi(b.get("yazi", ""))
    bant = b.get("bant") if b.get("bant") in dict(BANTLAR) else "kirmizi"
    bant_ad = dict(BANTLAR)[bant].lower()
    adet = max(1, int(float(b.get("adet") or 1)))

    is_.ilerle(8, "Plaka kuruluyor")
    t = _Tasarim(plaka, yazi, bant)
    adi = slug(plaka, 16).replace("-", "_")
    out = is_.yol("cikti", "x")[:-2]
    izgara = K.tabla_yerleri(t.W, t.H)
    tabla_basi = len(izgara)
    tabla = K.kac_tabla(adet, tabla_basi)
    if adet == 1:
        yerler = [(128.0, 128.0, 0)]
    elif adet < tabla_basi:                    # az adet: ızgaranın ortasına yakın yerler (kuleden uzak)
        ox = sum(x for x, _, _ in izgara) / tabla_basi
        oy = sum(y for _, y, _ in izgara) / tabla_basi
        yerler = sorted(sorted(izgara, key=lambda p: (p[0] - ox) ** 2 + (p[1] - oy) ** 2)[:adet],
                        key=lambda p: (p[1], p[0]))
    else:
        yerler = izgara
    template = zipfile.ZipFile(A.TEMPLATE)
    tf = {n: template.read(n) for n in template.namelist()}
    is_.ilerle(20, f"Tabla 3MF'i yazılıyor ({len(yerler)} adet)")
    ek = "tek" if adet == 1 else "tabla"
    dolu, _, filaments = A.write_design(_baski(t, f"plakali_{adi}_{ek}", f"BOYDE_plakali_{adi}_{ek}", yerler),
                                        tf, out)
    deneme = None
    if adet > 1:
        is_.ilerle(55, "Tek adetlik deneme 3MF'i yazılıyor")
        deneme, _, _ = A.write_design(_baski(t, f"plakali_{adi}_deneme", f"BOYDE_plakali_{adi}_deneme",
                                             [(128.0, 128.0, 0)]), tf, out)
    g = K.gram(t.solids(), len(yerler))
    g_txt = ", ".join(f"{O.AD[c]} {v:.0f} g" for c, v in g.items())
    renk = " · ".join(f"{i + 1} {A.COLOUR_NAMES[f]}" for i, f in enumerate(filaments))
    is_.ilerle(72, "Önizlemeler çiziliyor")
    satirlar = [f"{plaka} – PLAKALI ANAHTARLIK · X2D " + ("DOLU TABLA" if len(yerler) == tabla_basi else
                                                          f"TABLA ({len(yerler)} ADET)"),
                (f"70 × 22 × 3 mm · siyah çerçeve ve alt şerit 2 mm · beyaz plaka zemini · {bant_ad} TR bandı · "
                 "plaka 1,3 mm, alttaki yazı 1 mm kabartma · arka yüz siyah"),
                (f"Tabla başına {tabla_basi} adet · {adet} adet için {tabla} tabla "
                 f"(son tablada {adet - (tabla - 1) * tabla_basi} adet yeter; fazlası yedek)" if adet > tabla_basi
                 else f"Dosyada {len(yerler)} adet (sipariş: {adet}) · dolu tablaya {tabla_basi} adet sığar"),
                f"AMS: {renk} · ana nozul: siyah, {bant_ad} · yardımcı nozul: beyaz",
                f"Filament (bu tabla, tahmini): {g_txt} + kule",
                "Bambu standart 0,20 mm · ütüleme kapalı · destek yok · Textured PEI · arka yüz tablada",
                "Önce tek adetlik deneme dosyasını basıp renkleri ve yazıları kontrol edin." if deneme else
                "Tek adet: renkleri ve yazıları önizlemeden kontrol edin."]
    _tabla_resmi(t, yerler, os.path.join(out, "tabla.png"), satirlar)
    _onizleme(t, plaka, yazi, bant_ad, os.path.join(out, "onizleme.png"))
    is_.ilerle(96, "Bitti")

    o = t.olcu
    uyar = []
    if not olagan:
        uyar.append(f"Plaka alışılmış biçimde değil (34 ABC 123 gibi): \"{plaka}\" yazıldığı gibi basılır")
    if yazi and o["ad_boy"] < MIN_AD:
        uyar.append(f"Alttaki yazı uzun: {_mm(o['ad_boy'])} mm'ye küçüldü (tam boy 4,3 mm); kısaltmak daha okunur "
                    "olur")
    if o["ince"] > INCE:
        uyar.append(f"Yazının bazı yerleri 0,7 mm'den ince ({o['ince']:.0f} mm²); baskıda silik çıkabilir, önce "
                    "deneme basın ya da yazıyı kısaltın")
    if o["kirpilan"] > 0.05:
        uyar.append(f"Yazının bir kısmı ({_mm(o['kirpilan'])} mm²) alanından taşıyor; önizlemeyi kontrol edin")
    if adet > tabla_basi:
        uyar.append(f"Tabla başına {tabla_basi} adet; {adet} adet için {tabla} tabla basılır")
    ad_3mf = ("X2D dolu tabla" if len(yerler) == tabla_basi else "X2D tabla" if adet > 1 else "X2D baskı dosyası") + \
        f" ({len(yerler)} adet)"
    ciktilar = [{"ad": ad_3mf, "yol": is_.goreli(dolu), "tur": "3mf"}]
    if deneme:
        ciktilar.append({"ad": "X2D tek adet (deneme baskısı)", "yol": is_.goreli(deneme), "tur": "3mf"})
    ciktilar += [{"ad": "Müşteri önizlemesi (ön ve arka)", "yol": is_.goreli(os.path.join(out, "onizleme.png")),
                  "tur": "resim"},
                 {"ad": "Tabla yerleşimi ve hesap", "yol": is_.goreli(os.path.join(out, "tabla.png")), "tur": "resim"}]
    return {"ciktilar": ciktilar,
            "uyarilar": uyar, "bilgi": {"plaka": plaka, "tabla_basi": tabla_basi, "tabla": tabla, "gram": g,
                                         "yazi_boyu_mm": round(o["ad_boy"], 1)}}
