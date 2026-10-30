"""BOYDE Atölye duman testi: uygulamayı gerçek sunucusuyla, panelin kullandığı API üzerinden baştan sona dener.
Dört ürün: müşteri kaydı → katalog → katalogdaki ilk kodla baskı dosyaları; işler hatasız bitiyor mu, çıktı dosyaları
diskte var mı. Windows kurulum derlemesinde (CI) gömülü Python'la çalışır; geliştirirken de kullanılır.

Örnek bilgiler uydurma (gerçek işletme ya da kişi yok); telefon örnek numara. Anahtarlıkta üç renk seçili.

Kullanım: python scripts/atolye_duman.py [ürün kodu ...]    (boşsa hepsi; veri klasörü geçici, port 8790)
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8790
ADRES = f"http://127.0.0.1:{PORT}/api/"
TEL = "0546 475 45 08"
ORNEK = {
    "isimlik_9x12": {"isletme": "Deneme Oto Yıkama", "hizmet": "OTO YIKAMA", "sektor": "genel", "telefon": TEL,
                     "hizmetler": "İç dış yıkama, Pasta cila", "site_adi": "denemeoto"},
    "kurumsal_10x20": {"ad_soyad": "Deniz Yılmaz", "unvan": "Mali Müşavir", "kurum": "Deneme Danışmanlık",
                       "telefon": TEL, "sektor": "genel", "site_adi": "denizyilmaz"},
    "bayrakli": {"ad_soyad": "Deniz Yılmaz"},
    "anahtarlik": {"marka": "DENEME", "alt": "OTO YIKAMA", "sektor": "genel", "arka": TEL, "adet": "100",
                   "zemin": "siyah", "yazi_renk": "beyaz", "renk": "turuncu"},
}
SURE = 20 * 60                                            # bir iş için en çok (saniye)


def api(yol, govde=None):
    veri = json.dumps(govde).encode() if govde is not None else None
    istek = urllib.request.Request(ADRES + yol, data=veri, headers={"Content-Type": "application/json"},
                                   method="POST" if veri is not None else "GET")
    with urllib.request.urlopen(istek, timeout=60) as r:
        return json.loads(r.read())


def bekle(k, ad):
    """Müşterinin son işi bitene kadar bekler; hata olursa günlüğüyle durur."""
    t = time.time()
    while time.time() - t < SURE:
        m = api(f"musteri/{k}")
        isler = m.get("isler") or []
        if isler and isler[-1]["durum"] in ("bitti", "hata"):
            j = isler[-1]
            print(f"  {ad}: {j['durum']} ({time.time() - t:.0f} sn) {j['mesaj']}", flush=True)
            if j["durum"] == "hata":
                print("\n".join(j.get("gunluk") or []))
                sys.exit(f"HATA: {ad}")
            return m
        time.sleep(3)
    sys.exit(f"HATA: {ad} {SURE} sn'de bitmedi")


def dene(urun, veri):
    print(f"== {urun}", flush=True)
    m = api("musteri", {"urun": urun, "bilgiler": ORNEK[urun]})
    k = m["kimlik"]
    u = next(x for x in api("urunler") if x["kod"] == urun)
    kod = ""
    if u["katalog_adet"]:
        api(f"musteri/{k}/katalog", {})
        m = bekle(k, "katalog")
        kat = m["kataloglar"][-1]
        if len(kat["tasarimlar"]) < u["katalog_adet"] // 2:
            sys.exit(f"HATA: katalogda {len(kat['tasarimlar'])} tasarım var")
        for s in kat["sayfalar"] + [kat["pdf"]]:
            if not os.path.isfile(os.path.join(veri, "musteriler", k, s)):
                sys.exit(f"HATA: katalog dosyası yok: {s}")
        kod = kat["tasarimlar"][0]["kod"]
        print(f"  {len(kat['tasarimlar'])} tasarım, {len(kat['sayfalar'])} sayfa; seçilen {kod}", flush=True)
    api(f"musteri/{k}/uret", {"kod": kod})
    m = bekle(k, f"üretim {kod}".strip())
    yollar = [c["yol"] for c in m.get("ciktilar", [])]
    eksik = [y for y in yollar if not os.path.isfile(os.path.join(veri, "musteriler", k, y))]
    if not any(y.endswith(".3mf") for y in yollar) or eksik:
        sys.exit(f"HATA: çıktılar eksik: {yollar} (diskte yok: {eksik})")
    print(f"  çıktılar: {', '.join(os.path.basename(y) for y in yollar)}", flush=True)
    for w in m.get("uyarilar", [])[:4]:
        print(f"  uyarı: {w}")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)   # Windows konsolu ve CI günlüğü
    urunler = sys.argv[1:] or list(ORNEK)
    veri = tempfile.mkdtemp(prefix="boyde_duman_")
    env = dict(os.environ, BOYDE_VERI=veri, BOYDE_PORT=str(PORT))
    sunucu = subprocess.Popen([sys.executable, "-m", "atolye", "--acma"], cwd=KOK, env=env)
    try:
        for _ in range(60):
            try:
                api("urunler")
                break
            except (urllib.error.URLError, ConnectionError):
                time.sleep(1)
        else:
            sys.exit("HATA: sunucu açılmadı")
        bas = time.time()
        for urun in urunler:
            dene(urun, veri)
        print(f"TAMAM: {len(urunler)} ürün, {time.time() - bas:.0f} sn")
    finally:
        sunucu.terminate()


if __name__ == "__main__":
    main()
