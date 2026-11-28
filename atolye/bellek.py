"""Bellek ve temizlik: uygulamanın zamanla biriktirdiği, işe yaramayan dosyaları ve kayıtları gösterir ve siler.

Kullanıcı: "bu sisteme bir bellek temizleme butonu getirmek gerekiyor gibi". Müşteri kayıtlarına, kataloglara, baskı
dosyalarına ve web sayfalarına dokunulmaz; yalnız şunlar temizlenir (arayüzde Bellek sayfası, her biri ayrı seçilir):

  silinenler  silinen müşterilerin klasörleri (silinenler/; silince geri alınabilsin diye tutulur): KALICI silinir
  gunlukler   müşterilerin iş günlükleri (gunluk.txt; her üretimde uzar): son 200 satırı kalır
  onbellek    uygulama penceresinin tarayıcı önbelleği (Windows'ta %LOCALAPPDATA%\\BOYDE Atolye\\pencere); pencere
              açıkken kilitli dosyalar atlanır, kalan bir sonraki açılışta silinir
  gecici      yarım kalmış yazmalardan kalan geçici dosyalar (*.tmp, *.part)
  isler       bitmiş ve hata vermiş işlerin hafızadaki kayıtları (İşler sayfası; RAM). Süren işler kalır.
"""
import os
import shutil

from . import VERI, isler, kayit

SILINENLER = os.path.join(VERI, "silinenler")
GUNLUK_KALAN = 200                                     # günlükte bırakılan son satır sayısı
# tarayıcı önbelleği: profil klasöründe yeniden oluşturulan klasörler (oturum, çerezler ve ayarlar kalır)
ONBELLEK = ["Default/Cache", "Default/Code Cache", "Default/GPUCache", "Default/DawnCache",
            "Default/DawnGraphiteCache", "Default/DawnWebGPUCache", "Default/Service Worker/CacheStorage",
            "Default/Service Worker/ScriptCache", "GrShaderCache", "GraphiteDawnCache", "ShaderCache",
            "Crashpad/reports", "component_crx_cache"]
SONRAKI = "temizle_sonra.txt"                          # pencere açıkken silinemeyenler: sonraki açılışta


def _profil():
    from .masaustu import PROFIL
    return PROFIL


def boyut(yol):
    """Dosya ya da klasörün boyu (bayt); okunamayanlar atlanır."""
    if os.path.isfile(yol):
        try:
            return os.path.getsize(yol)
        except OSError:
            return 0
    t = 0
    for d, _, fs in os.walk(yol):
        for f in fs:
            try:
                t += os.path.getsize(os.path.join(d, f))
            except OSError:
                pass
    return t


def _gunlukler():
    if not os.path.isdir(kayit.MUSTERILER):
        return []
    return [p for p in (os.path.join(kayit.MUSTERILER, k, "gunluk.txt") for k in os.listdir(kayit.MUSTERILER))
            if os.path.isfile(p)]


def _gecici():
    out = []
    for d, _, fs in os.walk(VERI):
        out += [os.path.join(d, f) for f in fs if f.endswith((".tmp", ".part"))]
    return out


def _gunluk_fazlasi(p):
    """Günlük kısaltılınca boşalacak bayt."""
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            satirlar = f.readlines()
    except OSError:
        return 0
    return sum(len(s.encode("utf-8")) for s in satirlar[:-GUNLUK_KALAN]) if len(satirlar) > GUNLUK_KALAN else 0


def durum():
    """Arayüze: veri klasörünün boyu ve temizlenebilecekler [{anahtar, ad, aciklama, bayt, adet, uyari}]."""
    profil = _profil()
    sil = [os.path.join(SILINENLER, k) for k in os.listdir(SILINENLER)] if os.path.isdir(SILINENLER) else []
    gun = _gunlukler()
    musteri_say = len([k for k in os.listdir(kayit.MUSTERILER)]) if os.path.isdir(kayit.MUSTERILER) else 0
    bitmis = isler.bitmisler()
    kalemler = [
        {"anahtar": "silinenler", "ad": "Silinen müşteriler", "adet": len(sil), "bayt": sum(boyut(p) for p in sil),
         "aciklama": "Silinen müşterilerin klasörleri (geri alınabilsin diye tutuluyor).",
         "uyari": "Kalıcı olarak silinir, geri alınamaz."},
        {"anahtar": "gunlukler", "ad": "İş günlükleri", "adet": len(gun), "bayt": sum(_gunluk_fazlasi(p) for p in gun),
         "aciklama": f"Her üretimde uzayan iş kayıtları; her müşteride son {GUNLUK_KALAN} satır kalır."},
        {"anahtar": "onbellek", "ad": "Pencere önbelleği", "adet": 0,
         "bayt": sum(boyut(os.path.join(profil, y)) for y in ONBELLEK),
         "aciklama": "Uygulama penceresinin tarayıcı önbelleği; kendiliğinden yeniden oluşur."},
        {"anahtar": "gecici", "ad": "Geçici dosyalar", "adet": len(_gecici()), "bayt": sum(boyut(p) for p in _gecici()),
         "aciklama": "Yarım kalmış işlerden kalan dosyalar."},
        {"anahtar": "isler", "ad": "Bitmiş iş kayıtları (hafıza)", "adet": len(bitmis), "bayt": 0,
         "aciklama": "İşler sayfasındaki bitmiş ve hatalı işler; süren işler kalır."},
    ]
    return {"veri": VERI, "veri_bayt": boyut(VERI), "musteri": musteri_say,
            "musteri_bayt": boyut(kayit.MUSTERILER) if os.path.isdir(kayit.MUSTERILER) else 0,
            "kalemler": kalemler}


def _sil(yol):
    """Siler; silinemeyen (kilitli) dosyaların toplam boyunu döner."""
    kalan = [0]

    def hata(_f, p, _e):
        kalan[0] += boyut(p)
    if os.path.isdir(yol):
        shutil.rmtree(yol, onerror=hata)
    elif os.path.exists(yol):
        try:
            os.remove(yol)
        except OSError:
            kalan[0] += boyut(yol)
    return kalan[0]


def temizle(secim):
    """Seçilen kalemleri temizler. Döner {anahtar: boşalan bayt (isler: kaldırılan iş sayısı)}, toplam ve not."""
    out, notlar = {}, []
    if "silinenler" in secim and os.path.isdir(SILINENLER):
        once = boyut(SILINENLER)
        for k in os.listdir(SILINENLER):
            _sil(os.path.join(SILINENLER, k))
        out["silinenler"] = once - boyut(SILINENLER)
    if "gunlukler" in secim:
        t = 0
        for p in _gunlukler():
            fazla = _gunluk_fazlasi(p)
            if not fazla:
                continue
            with open(p, encoding="utf-8", errors="replace") as f:
                satirlar = f.readlines()
            with open(p, "w", encoding="utf-8") as f:
                f.writelines(satirlar[-GUNLUK_KALAN:])
            t += fazla
        out["gunlukler"] = t
    if "onbellek" in secim:
        profil = _profil()
        once = sum(boyut(os.path.join(profil, y)) for y in ONBELLEK)
        kilitli = sum(_sil(os.path.join(profil, y)) for y in ONBELLEK)
        out["onbellek"] = max(0, once - kilitli)
        if kilitli:
            os.makedirs(profil, exist_ok=True)
            with open(os.path.join(profil, SONRAKI), "w", encoding="utf-8") as f:
                f.write("pencere açıkken silinemeyen önbellek: sonraki açılışta silinir\n")
            notlar.append(f"Pencere açıkken kullanılan {kilitli / 1e6:.0f} MB önbellek, uygulama bir sonraki açılışta "
                          "silinecek.")
    if "gecici" in secim:
        out["gecici"] = sum(boyut(p) - _sil(p) for p in _gecici())
    if "isler" in secim:
        out["isler"] = isler.bitmisleri_temizle()
    return {"bosalan": out, "toplam": sum(v for k, v in out.items() if k != "isler"), "notlar": notlar}


def acilista():
    """Masaüstü başlatıcı pencereyi açmadan önce: önceki temizlikte kilitli kalan önbellek varsa siler."""
    profil = _profil()
    if os.path.exists(os.path.join(profil, SONRAKI)):
        for y in ONBELLEK:
            _sil(os.path.join(profil, y))
        _sil(os.path.join(profil, SONRAKI))
