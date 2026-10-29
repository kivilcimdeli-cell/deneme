"""BOYDE LABS – katalog ve Shopier için örnek ürünler: önceki işlerden isimlikler, iki ölçü kategorisinde.

Kategoriler (kullanıcı isteği: "9 × 12 ve 10 × 20 olarak 2 ürün kategorisi"):
  9x12   QR'lı masa / tezgâh isimliği, 120 × 90 mm, 1 cm siyah gövde, 2 mm kabartma, 15° sehpa
         (Uzar, İnce, Çalık, Soylu, Auto Tufan'ın basılan isimlikleriyle aynı yapı)
  10x20  Kurumsal isimlik (ad soyad, görev, logo, kartvizit QR'ı), 200 × 100 mm, 5 mm gövde, yüzeyle aynı hizada
         renkli dolgu ya da kabartma yazı, sehpa (Paloma Grida'nın basılan isimliği)

Ürünler (URUNLER, tur):
  musteri  müşterilerin seçip bastırdığı isimlikler (Uzar, İnce, Çalık, Soylu, Auto Tufan, Paloma Grida)
  oneri    o müşterilere çizilen önerilerden beğenilenler (en çok 10)
  ornek    başka sektörlere örnek isimlikler, uydurma işletmeler (scripts/boyde_sektor.py): "sadece lastikçi
           olmasın; sanayici, galerici, restoran hariç; telefoncu ve başka ne geliyorsa", "kuaförlere de"

Örnek modu (bu modül ürün betiklerinden ÖNCE yüklenir):
  * QR'lar çalışmaz: segno'nun ürettiği her QR'da bulucu kareler, zamanlama ve hizalama desenleri kalır, geri kalan
    bütün kareler (biçim bilgisi dahil) rastgele: QR gibi görünür ama hiçbir okuyucu çözemez (urun_parcalari()
    okumayı dener; okunursa hata verir).
  * Telefonlar BOYDE LABS'in numarası: 0546 475 45 08.
  * Kişi adları örnek: Paloma isimliğinde gerçek kişinin adı yerine "Ayşe Yılmaz · Ön Büro Müdürü".
  İşletme adları ve logoları kalır: referans iş olarak gösterilir.

Kullanım: python3 scripts/boyde_urunler.py [anahtar ...]   # ürünleri kurar, QR denetler, kaynak/ altına aktarır
"""
import hashlib
import os
import sys
from dataclasses import dataclass

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TEL = "905464754508"                                  # BOYDE LABS: 0546 475 45 08
ORNEK_AD, ORNEK_SOYAD, ORNEK_GOREV = "Ayşe", "Yılmaz", "Ön Büro Müdürü"


# ---------------------------------------------------------------- örnek modu: çalışmayan QR, BOYDE telefonu

def _function_mask(version, _cache={}):
    """QR'ın sabit desenleri (bulucu, ayraç, zamanlama, hizalama, sürüm bilgisi): aynı sürümde içerik, hata düzeyi ve
    maske değişince değişmeyen kareler."""
    if version not in _cache:
        mats = []
        for k, err in enumerate("lmqh"):
            for mask in range(8):
                q = _segno_make(f"BOYDE-{k}-{mask}-{version}", error=err, version=version, mask=mask,
                                micro=False, boost_error=False)
                mats.append(np.array(q.matrix, bool))
        mats = np.array(mats)
        _cache[version] = (mats == mats[0]).all(0)
    return _cache[version]


class BrokenQR:
    """QR gibi görünen, okunmayan desen: sabit desenler gerçek QR'dan, öbür kareler (veri, hata düzeltme, biçim
    bilgisi) içerikten türetilen tohumla rastgele."""

    def __init__(self, q, content):
        self._q = q
        m = np.array(q.matrix, bool)
        fixed = _function_mask(q.version)
        seed = int.from_bytes(hashlib.sha256(str(content).encode()).digest()[:8], "big")
        noise = np.random.default_rng(seed).random(m.shape) < 0.5
        self.matrix = tuple(tuple(int(v) for v in row) for row in np.where(fixed, m, noise))

    def __getattr__(self, k):
        return getattr(self._q, k)


import segno  # noqa: E402

if not hasattr(segno, "make_gercek"):                    # bir kez (modül iki adla yüklenebilir: betik ve modül)
    segno.make_gercek = segno.make
    segno.make = lambda content, *a, **kw: BrokenQR(segno.make_gercek(content, *a, **kw), content)
_segno_make = segno.make_gercek

import qr_sistemi as Q  # noqa: E402

Q.phone_e164 = lambda s: TEL

import anahtarlik as A  # noqa: E402

# PLA tonları (fotoğraf): Bambu PLA Basic'e yakın
RGB = {A.BLACK: (30, 31, 35), A.WHITE: (238, 238, 233), A.RED: (196, 30, 38), A.YELLOW: (246, 194, 24),
       A.GOLD: (205, 160, 78), A.BLUE: (105, 161, 186)}
METAL = {A.GOLD}

KATEGORI = {
    "9x12": {"ad": "QR'lı masa isimliği", "olcu": "9 × 12 cm", "boy": "120 × 90 mm",
             "kisa": "İşletmeler için: masaya, tezgâha, kasaya.",
             "ozellik": ["120 × 90 mm, 1 cm kalın siyah gövde", "Yazı ve logo 2 mm kabartma, renkli",
                         "QR yüzeyle aynı hizada: keskin, kolay okunur", "15° eğik sehpa dahil, tutkal gerekmez",
                         "QR işletmenize özel sayfayı açar: ara, WhatsApp, konum, yorum, IBAN"]},
    "10x20": {"ad": "Kurumsal isimlik", "olcu": "10 × 20 cm", "boy": "200 × 100 mm",
              "kisa": "Yönetici ve personel için: ad soyad, görev, logo, kartvizit QR'ı.",
              "ozellik": ["200 × 100 mm, 5 mm gövde", "Yazılar yüzeyle aynı hizada renkli ya da 2 mm kabartma",
                          "Kurum logosu ve renkleri", "Sehpa dahil",
                          "QR dijital kartvizit sayfasını açar: telefon, e-posta, adres, rehbere kaydet"]},
}


@dataclass
class Urun:
    key: str
    kat: str
    ad: str                  # tasarımın adı
    musteri: str             # kimin için yapıldı (ornek: uydurma işletme)
    tur: str                 # musteri, oneri, ornek
    aciklama: str
    renk: str                # renkler (katalog)
    sektor: str = ""


URUNLER = [
    Urun("uzar", "9x12", "Tek QR", "Uzar Oto Lastik", "musteri",
         "Solda kırmızı şimşek ve UZAR, altında telefon; sağda büyük QR.", "siyah · beyaz · kırmızı", "Lastikçi"),
    Urun("ince", "9x12", "Kırmızı köşe", "İnce Oto Lastik", "musteri",
         "Köşede kırmızı üçgen, içinde 7/24; ortalı İNCE, OTO LASTİK ve telefon; sağda QR.",
         "siyah · beyaz · kırmızı", "Lastikçi"),
    Urun("calik", "9x12", "Lastik izi", "Çalık Oto Lastik", "musteri",
         "Lastik izi okları, beş yıldız ve YORUM YAP; ÇALIK, HEMEN ARA ve telefon.", "siyah · beyaz · sarı",
         "Lastikçi"),
    Urun("soylu", "9x12", "S monogramı", "Soylu Oto Lastik", "musteri",
         "Solda QR; sağda kırmızı karede oyma S, geniş harfli SOYLU, HEMEN ARA ve telefon.",
         "siyah · beyaz · kırmızı", "Lastikçi"),
    Urun("tufan", "9x12", "Klasik logo", "Auto Tufan", "musteri",
         "Altın fırça T logosu, Auto Tufan ve HASAR ONARIM; altta telefon ve QR.", "siyah · beyaz · altın",
         "Kaporta ve boya"),
    Urun("ince_plaka", "9x12", "Plaka", "İnce Oto Lastik", "oneri",
         "Araç plakası gibi: siyah çerçeve, kırmızı şerit; beyaz gövde.", "beyaz · siyah · kırmızı", "Lastikçi"),
    Urun("calik_ikaz", "9x12", "İkaz şeridi", "Çalık Oto Lastik", "oneri",
         "Üstte ve altta sarı-siyah ikaz şeridi; geniş, sağlam yazılar.", "siyah · beyaz · sarı", "Lastikçi"),
    Urun("tufan_cerceve", "9x12", "Altın çerçeve", "Auto Tufan", "oneri",
         "İnce altın çerçeve, üst kenarında fırça T; ortalı yazılar, sağda QR.", "siyah · beyaz · altın",
         "Kaporta ve boya"),
    Urun("telefon", "9x12", "Akıllı telefon", "Çağrı İletişim", "ornek",
         "Turkuaz telefon simgesi ve ÇAĞRI; hizmetler, HEMEN ARA ve telefon; sağda QR.",
         "siyah · beyaz · turkuaz", "Telefoncu"),
    Urun("berber", "9x12", "Berber direği", "Makas Berber", "ornek",
         "Solda kırmızı-mavi berber direği; iri MAKAS, BERBER, randevu telefonu ve QR.",
         "siyah · beyaz · kırmızı · mavi", "Berber"),
    Urun("kuafor", "9x12", "Makas", "Mira Kuaför", "ornek",
         "Mor makas ve Mira; KUAFÖR, hizmetler, randevu telefonu; mor çerçeveli QR.", "beyaz · siyah · mor",
         "Kuaför"),
    Urun("guzellik", "9x12", "Hilal", "Luna Güzellik", "ornek",
         "Pembe hilal ve yıldız, zarif Luna; GÜZELLİK SALONU, hizmetler, telefon ve randevu QR'ı.",
         "beyaz · siyah · pembe", "Güzellik salonu"),
    Urun("emlak", "9x12", "Üst bant", "Anka Emlak", "ornek",
         "Mavi bantta oyma ev ve ANKA EMLAK; SATILIK · KİRALIK, telefon; mavi kareli QR.",
         "beyaz · mavi · turuncu", "Emlak"),
    Urun("kuyumcu", "9x12", "Pırlanta", "Sera Kuyumculuk", "ornek",
         "Altın pırlanta, klasik harfli SERA, iki yanı çizgili KUYUMCULUK; altta telefon ve QR.",
         "siyah · beyaz · altın", "Kuyumcu"),
    Urun("optik", "9x12", "Gözlük", "Net Optik", "ornek",
         "Turkuaz gözlük ve iri NET; OPTİK, hizmetler, telefon; turkuaz çerçeveli QR.",
         "beyaz · siyah · turkuaz", "Optik"),
    Urun("veteriner", "9x12", "Yeşil blok", "Pati Veteriner", "ornek",
         "Solda yeşil blok, içinde oyma pati ve PATİ VETERİNER KLİNİĞİ; sağda randevu QR'ı ve telefon.",
         "beyaz · siyah · yeşil", "Veteriner"),
    Urun("spor", "9x12", "Dambıl", "Forma Spor", "ornek",
         "Turuncu dambıl, eğik iri FORMA; SPOR SALONU, branşlar, telefon ve QR.", "siyah · beyaz · turuncu",
         "Spor salonu"),
    Urun("paloma", "10x20", "Mavi kart", "Paloma Grida", "musteri",
         "Solda ad soyad ve görev; sağda kurum renginde kart: logo, QR ve KARTVİZİT.", "beyaz · siyah · mavi",
         "Otel"),
    Urun("paloma_siyah", "10x20", "Mavi kart, siyah", "Paloma Grida", "oneri",
         "Aynı düzen siyah gövdede: beyaz yazı, mavi kart.", "siyah · beyaz · mavi", "Otel"),
    Urun("paloma_kabartma", "10x20", "Mavi kart, kabartmalı", "Paloma Grida", "oneri",
         "Ad soyad, görev ve logo 2 mm kabartma; elle dokununca hissedilir.", "beyaz · siyah · mavi", "Otel"),
    Urun("avukat", "10x20", "Terazi", "Kaya Hukuk Bürosu", "ornek",
         "Altın terazi, klasik harfli ad soyad; unvan, büro ve telefon; lacivert kareli QR.",
         "beyaz · lacivert · altın", "Avukat"),
    Urun("dis", "10x20", "Turkuaz blok", "Arslan Diş Kliniği", "ornek",
         "Solda turkuaz blok, içinde oyma diş ve klinik adı; iri ad soyad, unvan, randevu QR'ı.",
         "beyaz · siyah · turkuaz", "Diş hekimi"),
    Urun("musavir", "10x20", "Monogram", "Demir Mali Müşavirlik", "ornek",
         "Yeşil karede oyma monogram; ad soyad, unvan, büro ve telefon; beyaz karoda QR.",
         "siyah · beyaz · yeşil", "Mali müşavir"),
    Urun("mimar", "10x20", "Basamak", "Aydın Mimarlık", "ornek",
         "Turuncu basamak işareti ve çizgi; geniş harfli ad soyad, unvan, büro; portfolyo QR'ı.",
         "beyaz · siyah · turuncu", "Mimar"),
]
BY_KEY = {u.key: u for u in URUNLER}


# ---------------------------------------------------------------- parçalar

@dataclass
class Parcalar:
    panel: list              # [(ad, manifold, renk)] panel baskı yönünde (yüzü +z)
    stand: object            # sehpa (manifold), yerinde
    stand_col: int
    mount: tuple             # (z0, y0): panelin sehpadaki yeri
    qr_top: object = None    # panelin üstten görünüşü (QR denetimi)


def _plate(mod_name):
    """Müşterinin bastırdığı isimlik: baskı dosyasındaki panel ve sehpa (siyah)."""
    import importlib
    pl = importlib.import_module(mod_name).Plate()
    return Parcalar(pl.panel, pl.stand, A.BLACK, pl.mount)


def _design(mod_name, fn):
    import importlib
    import uzar_isimlik_baski as B
    mod = importlib.import_module(mod_name)
    d = getattr(mod, fn)()
    stand, mount = B.stand()
    return Parcalar(mod.solids(d), stand, A.BLACK, mount)


def _paloma(sc_key, relief):
    import paloma_isimlik as P
    P.FIRST, P.LAST, P.NAME, P.TITLE = ORNEK_AD, ORNEK_SOYAD, f"{ORNEK_AD} {ORNEK_SOYAD}", ORNEK_GOREV
    import paloma_isimlik_baski as PB                   # panel 200 × 100 × 5 (modül ölçüleri değişir)
    import uzar_isimlik_baski as B
    if sc_key == "beyaz":
        pl = PB.Plate(relief)
        return Parcalar(pl.panel, pl.stand, pl.body, pl.mount)
    d = P.secilen_20(P.BLACK_SC)
    stand, mount = B.stand(length=PB.STAND_LEN)
    return Parcalar(P.solids(d), stand, A.BLACK, mount)


def _sektor(key):
    import boyde_sektor as S
    return S.build(key)


BUILDERS = {
    "uzar": lambda: _plate("uzar_isimlik_baski"),
    "ince": lambda: _plate("ince_isimlik_baski"),
    "calik": lambda: _plate("calik_isimlik_baski"),
    "soylu": lambda: _plate("soylu_isimlik_baski"),
    "tufan": lambda: _plate("autotufan_isimlik_baski"),
    "ince_plaka": lambda: _design("ince_isimlik", "d1_plaka"),
    "calik_ikaz": lambda: _design("calik_isimlik", "c4_ikaz"),
    "tufan_cerceve": lambda: _design("autotufan_isimlik", "d6_cerceve"),
    "paloma": lambda: _paloma("beyaz", False),
    "paloma_siyah": lambda: _paloma("siyah", False),
    "paloma_kabartma": lambda: _paloma("beyaz", True),
}
BUILDERS.update({u.key: (lambda k=u.key: _sektor(k)) for u in URUNLER if u.tur == "ornek"})


def top_view(panel, size=1600):
    """Panelin üstten görünüşü (renkli, ışıksız): QR denetimi ve katalogdaki düz görünüş için."""
    from cift_tarafli_isimlik import render
    return render([(*A.mesh_arrays(m), RGB[c]) for _, m, c in panel], size, A.R_TOP, light=False, margin=0.03)


def qr_reads(im):
    """Görüntüde okunan QR'lar (zxing ve OpenCV)."""
    import cv2
    from PIL import Image
    bg = Image.new("RGB", im.size, (150, 152, 158))
    bg.paste(im, (0, 0), im if im.mode == "RGBA" else None)
    g = bg.convert("L")
    found = Q.decode(g)
    for scale in (1.0, 0.5):
        arr = np.array(g.resize((int(g.width * scale), int(g.height * scale))))
        text, _, _ = cv2.QRCodeDetector().detectAndDecode(arr)
        if text:
            found.append(text)
    return found


def urun_parcalari(key, check=True):
    """Ürünün parçaları; check: üstten görünüşte hiçbir QR okunmamalı (örnek modu)."""
    p = BUILDERS[key]()
    if check:
        p.qr_top = top_view(p.panel)
        reads = qr_reads(p.qr_top)
        if reads:
            raise RuntimeError(f"{key}: QR okundu {reads!r} – örnekte QR çalışmamalı")
    return p


OUT = os.path.join(A.ROOT, "boyde_labs", "urunler")
SRC = os.path.join(OUT, "kaynak")                       # ara dosyalar (git'e girmez)


def export(key):
    """Ürünü fotoğraf için dışa aktarır (kendi sürecinde: Paloma modülü ölçüleri değiştirir):
    kaynak/<key>.npz  sehpasında duran panel ve sehpa (mm; yüz −y'ye bakar), her parçanın rengi
    kaynak/<key>_duz.png  panelin düz görünüşü (saydam; katalog)."""
    import json
    import uzar_isimlik_baski as B
    p = urun_parcalari(key)
    z0, y0 = p.mount
    parts = B.assembled(p.panel, z0, y0) + [("Sehpa", p.stand, p.stand_col)]
    arrays = {}
    for i, (name, man, col) in enumerate(parts):
        V, T = A.mesh_arrays(man)
        arrays[f"v{i}"], arrays[f"f{i}"] = V.astype(np.float32), T.astype(np.int32)
    meta = [{"ad": n, "renk": list(RGB[c]), "metal": c in METAL, "panel": n != "Sehpa"} for n, _, c in parts]
    os.makedirs(SRC, exist_ok=True)
    np.savez_compressed(os.path.join(SRC, f"{key}.npz"), meta=json.dumps(meta, ensure_ascii=False), **arrays)
    im = p.qr_top
    im.crop(im.getbbox()).save(os.path.join(SRC, f"{key}_duz.png"), optimize=True)
    body = p.panel[0][2]
    return key, body == A.WHITE


def main():
    import multiprocessing as mp
    keys = [k for k in sys.argv[1:] if not k.startswith("-")] or [u.key for u in URUNLER]
    with mp.get_context("spawn").Pool(4, maxtasksperchild=1) as pool:      # her ürün kendi sürecinde
        for key, _ in pool.imap_unordered(export, keys):
            print(f"{key:16s} dışa aktarıldı, QR okunmuyor ✓", flush=True)


if __name__ == "__main__":
    import boyde_urunler                                 # tek modül nesnesi: boyde_sektor de bunu kullanır
    boyde_urunler.main()
