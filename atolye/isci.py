"""Alt süreç: bir müşterinin kataloğunu ya da baskı dosyalarını üretir. Sunucu (isler.py) bunu ayrı bir Python
sürecinde çalıştırır; böylece ağır üretim (geometri, dilimleme, katalog) paneli dondurmaz, modüllerin genel
ayarları (10 × 20 ölçüleri gibi) ürünler arasında karışmaz.

Kullanım: python -m atolye.isci katalog|uret <müşteri kimliği> [kod]
Çıktı: "@@ <yüzde> <mesaj>" satırları ilerlemedir; sonuç musteri.json'a yazılır, öğrenme kaydı güncellenir.
"""
import os
import sys
import traceback

from . import SCRIPTS, kayit, ogrenme, urunler

sys.path.insert(0, SCRIPTS)


class Is:
    def __init__(self, musteri, no=0, haric=()):
        self.musteri = musteri
        self.bilgiler = musteri["bilgiler"]
        self.klasor = kayit.klasor(musteri["kimlik"])
        self.no = no
        self.haric = list(haric)

    def ilerle(self, yuzde, mesaj):
        print(f"@@ {int(yuzde)} {mesaj}", flush=True)

    def yol(self, *parca):
        """Müşteri klasöründe bir yol (klasörler oluşturulur)."""
        p = os.path.join(self.klasor, *parca)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        return p

    def goreli(self, yol):
        return os.path.relpath(yol, self.klasor).replace(os.sep, "/")


def katalog(kimlik):
    m = kayit.oku(kimlik)
    u = urunler.bul(m["urun"])
    no = len(m["kataloglar"]) + 1
    haric = [t.get("imza", t["kod"]) for k in m["kataloglar"] for t in k["tasarimlar"]]
    is_ = Is(m, no, haric)
    is_.ilerle(2, f"{no}. katalog hazırlanıyor")
    sonuc = u.katalog(is_)
    m = kayit.oku(kimlik)                                   # üretim sırasında değişmiş olabilir
    m["kataloglar"].append({"no": no, "tarih": kayit.simdi(), **sonuc})
    kayit.not_ekle(m, f"{no}. katalog üretildi ({len(sonuc['tasarimlar'])} tasarım)")
    kayit.yaz(m)
    ogrenme.gosterildi(u.KOD, [t["ozellikler"] for t in sonuc["tasarimlar"]])
    is_.ilerle(100, f"{no}. katalog hazır")


def uret(kimlik, kod=None):
    m = kayit.oku(kimlik)
    u = urunler.bul(m["urun"])
    secilen = None
    if kod:
        for k in reversed(m["kataloglar"]):
            secilen = next((t for t in k["tasarimlar"] if t["kod"] == kod), None)
            if secilen:
                break
        if not secilen:
            raise SystemExit(f"Katalogda {kod} kodlu tasarım yok")
    is_ = Is(m)
    is_.ilerle(2, f"{kod or u.AD} için dosyalar hazırlanıyor")
    sonuc = u.uret(is_, secilen)
    m = kayit.oku(kimlik)
    if secilen:
        m["secimler"].append({"kod": kod, "tarih": kayit.simdi()})
        ogrenme.secildi(u.KOD, secilen["ozellikler"])
    for c in sonuc["ciktilar"]:
        c["tarih"] = kayit.simdi()
    eski = {c["yol"] for c in sonuc["ciktilar"]}
    m["ciktilar"] = [c for c in m["ciktilar"] if c["yol"] not in eski] + sonuc["ciktilar"]
    for w in sonuc.get("uyarilar", []):
        kayit.not_ekle(m, "Uyarı: " + w)
    kayit.not_ekle(m, f"Dosyalar üretildi{f' ({kod})' if kod else ''}: " + ", ".join(c["ad"] for c in sonuc["ciktilar"]))
    kayit.yaz(m)
    is_.ilerle(100, "Dosyalar hazır")


def main():
    eylem, kimlik = sys.argv[1], sys.argv[2]
    try:
        if eylem == "katalog":
            katalog(kimlik)
        elif eylem == "uret":
            uret(kimlik, sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else None)
        else:
            raise SystemExit(f"bilinmeyen eylem: {eylem}")
    except SystemExit:
        raise
    except Exception:                                      # noqa: BLE001 (hata metni panele gider)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
