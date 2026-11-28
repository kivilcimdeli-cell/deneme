"""Müşteri kayıtları: her müşteri bir klasör (atolye_veri/musteriler/<kimlik>/), içinde musteri.json ve çıktılar.

musteri.json:
  kimlik, urun, bilgiler{alan: değer}, olusturma, guncelleme
  kataloglar: [{no, tarih, tasarimlar: [{kod, ad, ozellikler, onizleme}], pdf, sayfalar}]
  secimler:   [{katalog, kod, tarih}]
  ciktilar:   [{ad, yol (klasöre göre), tur, tarih}]
  notlar:     [{tarih, metin}]  (işlem geçmişi ve Claude'a iletilen istekler)
"""
import datetime
import json
import os
import re
import threading

from . import VERI

MUSTERILER = os.path.join(VERI, "musteriler")
_KILIT = threading.Lock()
TR = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")


def simdi():
    return datetime.datetime.now().isoformat(timespec="seconds")


def slug(metin, uzunluk=40):
    s = re.sub(r"[^a-z0-9]+", "-", metin.translate(TR).lower()).strip("-")
    return s[:uzunluk].strip("-") or "musteri"


def klasor(kimlik):
    return os.path.join(MUSTERILER, kimlik)


def oku(kimlik):
    with open(os.path.join(klasor(kimlik), "musteri.json"), encoding="utf-8") as f:
        return json.load(f)


def yaz(m):
    m["guncelleme"] = simdi()
    yol = os.path.join(klasor(m["kimlik"]), "musteri.json")
    with _KILIT:
        tmp = yol + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(m, f, ensure_ascii=False, indent=2)
        os.replace(tmp, yol)
    return m


def olustur(urun, bilgiler, ad):
    """Yeni müşteri: kimlik tarih + addan; aynı gün aynı ad varsa sona sayı eklenir."""
    os.makedirs(MUSTERILER, exist_ok=True)
    taban = f"{datetime.date.today().isoformat()}_{slug(ad)}"
    kimlik, n = taban, 2
    while os.path.exists(klasor(kimlik)):
        kimlik, n = f"{taban}-{n}", n + 1
    os.makedirs(klasor(kimlik))
    m = {"kimlik": kimlik, "urun": urun, "ad": ad, "bilgiler": bilgiler, "olusturma": simdi(),
         "kataloglar": [], "secimler": [], "ciktilar": [], "notlar": []}
    return yaz(m)


def liste():
    """Bütün müşteriler, en son güncellenen önce (özet)."""
    if not os.path.isdir(MUSTERILER):
        return []
    out = []
    for k in os.listdir(MUSTERILER):
        try:
            m = oku(k)
        except (OSError, ValueError):
            continue
        out.append({"kimlik": k, "ad": m.get("ad", k), "urun": m["urun"], "guncelleme": m.get("guncelleme", ""),
                    "katalog": len(m.get("kataloglar", [])), "secim": (m.get("secimler") or [{}])[-1].get("kod"),
                    "cikti": len(m.get("ciktilar", []))})
    return sorted(out, key=lambda r: r["guncelleme"], reverse=True)


def not_ekle(m, metin):
    m.setdefault("notlar", []).append({"tarih": simdi(), "metin": metin})
