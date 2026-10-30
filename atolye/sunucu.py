"""Yerel web paneli: arayüz dosyaları ve JSON API (yalnız bu bilgisayardan erişilir: 127.0.0.1).

  GET  /                              arayüz
  GET  /api/urunler                   ürünler ve form alanları
  GET  /api/musteriler                müşteriler (son güncellenen önce)
  POST /api/musteri                   {urun, bilgiler} → yeni müşteri
  GET  /api/musteri/<k>               müşteri, katalogları, çıktıları, işleri
  POST /api/musteri/<k>/bilgi         {bilgiler} → bilgileri güncelle
  POST /api/musteri/<k>/dosya         {alan, ad, veri (base64)} → yüklenen dosya (logo gibi)
  POST /api/musteri/<k>/katalog       yeni katalog (iş kuyruğuna)
  POST /api/musteri/<k>/uret          {kod} → seçilen tasarımın dosyaları (iş kuyruğuna)
  POST /api/musteri/<k>/claude        {istek} → Claude'a özel istek (Claude Code kuruluysa)
  POST /api/musteri/<k>/klasor        müşteri klasörünü dosya gezgininde aç
  GET  /api/is/<no>, /api/isler       iş durumu
  GET  /api/ogrenme/<urun>            öğrenilen tercihler
  GET  /dosya/<k>/<yol>               müşteri klasöründeki bir dosya (katalog, 3MF, önizleme)
"""
import base64
import json
import mimetypes
import os
import re
import subprocess
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import PORT, isler, kayit, ogrenme, urunler

ARAYUZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arayuz")
mimetypes.add_type("model/3mf", ".3mf")
mimetypes.add_type("text/javascript", ".js")


class Hata(Exception):
    def __init__(self, kod, mesaj):
        super().__init__(mesaj)
        self.kod = kod


def _eksik(urun, bilgiler):
    return [a["etiket"] for a in urun.ALANLAR if a.get("zorunlu") and not str(bilgiler.get(a["ad"], "")).strip()]


def _musteri_tam(k):
    m = kayit.oku(k)
    m["isler"] = isler.musteri_isleri(k)
    m["urun_ad"] = urunler.bul(m["urun"]).AD
    return m


def _klasor_ac(yol):
    if sys.platform.startswith("win"):
        os.startfile(yol)                                  # noqa: S606 (yalnız yerel klasör)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", yol])
    else:
        subprocess.Popen(["xdg-open", yol])


def claude_komutu(m, istek):
    """Claude Code (claude CLI) varsa: müşterinin klasörü ve isteğiyle tek seferlik iş. Yoksa None."""
    from .claude import komut
    return komut(m, istek)


class Panel(BaseHTTPRequestHandler):
    server_version = "BOYDE-Atolye/1"

    def log_message(self, fmt, *args):                    # konsolu sessiz tut
        pass

    # ------------------------------------------------------------ yardımcılar
    def _json(self, veri, kod=200):
        b = json.dumps(veri, ensure_ascii=False).encode("utf-8")
        self.send_response(kod)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def _dosya(self, yol, indir=False):
        if not os.path.isfile(yol):
            raise Hata(404, "Dosya yok")
        tur = mimetypes.guess_type(yol)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", tur + ("; charset=utf-8" if tur.startswith("text/") else ""))
        self.send_header("Content-Length", str(os.path.getsize(yol)))
        self.send_header("Cache-Control", "no-store")
        if indir:
            ad = urllib.parse.quote(os.path.basename(yol))
            self.send_header("Content-Disposition", f"attachment; filename*=UTF-8''{ad}")
        self.end_headers()
        with open(yol, "rb") as f:
            while True:
                parca = f.read(1 << 16)
                if not parca:
                    break
                self.wfile.write(parca)

    def _govde(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n).decode("utf-8") or "{}") if n else {}

    def _guvenli(self, kok, goreli):
        yol = os.path.realpath(os.path.join(kok, goreli))
        if not yol.startswith(os.path.realpath(kok) + os.sep):
            raise Hata(403, "İzin yok")
        return yol

    # ------------------------------------------------------------ istekler
    def do_GET(self):
        self._yonlendir("GET")

    def do_POST(self):
        self._yonlendir("POST")

    def _yonlendir(self, yontem):
        u = urllib.parse.urlparse(self.path)
        parca = [urllib.parse.unquote(p) for p in u.path.strip("/").split("/") if p]
        q = urllib.parse.parse_qs(u.query)
        try:
            if yontem == "GET" and not parca:
                return self._dosya(os.path.join(ARAYUZ, "index.html"))
            if yontem == "GET" and parca[0] == "arayuz":
                return self._dosya(self._guvenli(ARAYUZ, "/".join(parca[1:])))
            if yontem == "GET" and parca[0] == "dosya" and len(parca) >= 3:
                kok = kayit.klasor(parca[1])
                return self._dosya(self._guvenli(kok, "/".join(parca[2:])), indir="indir" in q)
            if parca[0] != "api":
                raise Hata(404, "Bulunamadı")
            return self._json(self._api(yontem, parca[1:]))
        except Hata as e:
            self._json({"hata": str(e)}, e.kod)
        except (FileNotFoundError, KeyError) as e:
            self._json({"hata": f"Bulunamadı: {e}"}, 404)
        except RuntimeError as e:
            self._json({"hata": str(e)}, 409)
        except Exception as e:                                  # noqa: BLE001
            self._json({"hata": f"{type(e).__name__}: {e}"}, 500)

    def _api(self, yontem, p):
        if yontem == "GET" and p == ["urunler"]:
            return [urunler.tanim(m) for m in urunler.hepsi()]
        if yontem == "GET" and p == ["musteriler"]:
            return kayit.liste()
        if yontem == "GET" and p == ["isler"]:
            return isler.hepsi()
        if yontem == "GET" and len(p) == 2 and p[0] == "is":
            return isler.durum(p[1]) or {}
        if yontem == "GET" and len(p) == 2 and p[0] == "ogrenme":
            return ogrenme.ozet(p[1])
        if yontem == "POST" and p == ["musteri"]:
            g = self._govde()
            u = urunler.bul(g["urun"])
            b = {k: v for k, v in (g.get("bilgiler") or {}).items() if isinstance(v, (str, int, float, bool))}
            eksik = _eksik(u, b)
            if eksik:
                raise Hata(400, "Eksik: " + ", ".join(eksik))
            m = kayit.olustur(u.KOD, b, u.ad(b))
            return _musteri_tam(m["kimlik"])
        if len(p) >= 2 and p[0] == "musteri":
            k = p[1]
            if not os.path.isdir(kayit.klasor(k)):
                raise Hata(404, "Müşteri yok")
            if yontem == "GET" and len(p) == 2:
                return _musteri_tam(k)
            eylem = p[2] if len(p) > 2 else ""
            if yontem == "POST":
                return self._musteri_eylem(k, eylem)
        raise Hata(404, "Bilinmeyen istek")

    def _musteri_eylem(self, k, eylem):
        g = self._govde()
        m = kayit.oku(k)
        u = urunler.bul(m["urun"])
        if eylem == "bilgi":
            if isler.musteri_isleri(k) and any(j["durum"] in ("bekliyor", "calisiyor") for j in isler.musteri_isleri(k)):
                raise Hata(409, "İş sürerken bilgiler değiştirilemez")
            b = dict(m["bilgiler"])
            b.update({kk: v for kk, v in (g.get("bilgiler") or {}).items() if isinstance(v, (str, int, float, bool))})
            eksik = _eksik(u, b)
            if eksik:
                raise Hata(400, "Eksik: " + ", ".join(eksik))
            m["bilgiler"], m["ad"] = b, u.ad(b)
            kayit.not_ekle(m, "Bilgiler güncellendi")
            kayit.yaz(m)
            return _musteri_tam(k)
        if eylem == "dosya":
            ad = re.sub(r"[^\w.\-]+", "_", os.path.basename(g.get("ad") or "dosya"))
            yol = os.path.join(kayit.klasor(k), "yuklenen", ad)
            os.makedirs(os.path.dirname(yol), exist_ok=True)
            with open(yol, "wb") as f:
                f.write(base64.b64decode(g["veri"].split(",")[-1]))
            m["bilgiler"][g["alan"]] = f"yuklenen/{ad}"
            kayit.yaz(m)
            return _musteri_tam(k)
        if eylem == "katalog":
            if not u.KATALOG_ADET:
                raise Hata(400, "Bu ürünün kataloğu yok; doğrudan üretilir")
            isler.ekle(k, "katalog", baslik=f"{len(m['kataloglar']) + 1}. katalog")
            return _musteri_tam(k)
        if eylem == "uret":
            kod = (g.get("kod") or "").strip().upper()
            if u.KATALOG_ADET and not kod:
                raise Hata(400, "Katalogdan bir tasarım kodu seçin")
            isler.ekle(k, "uret", kod, baslik=f"{kod or 'Baskı'} dosyaları")
            return _musteri_tam(k)
        if eylem == "claude":
            istek = (g.get("istek") or "").strip()
            if not istek:
                raise Hata(400, "İstek boş")
            komut = claude_komutu(m, istek)
            if not komut:
                raise Hata(400, "Claude Code bu bilgisayarda kurulu değil (README: Claude köprüsü)")
            kayit.not_ekle(m, "Claude'a iletildi: " + istek)
            kayit.yaz(m)
            isler.ekle(k, "claude", baslik="Claude: " + istek[:40], komut=komut)
            return _musteri_tam(k)
        if eylem == "klasor":
            _klasor_ac(kayit.klasor(k))
            return {"tamam": True}
        raise Hata(404, "Bilinmeyen eylem")


def calistir(ac=True):
    sunucu = ThreadingHTTPServer(("127.0.0.1", PORT), Panel)
    adres = f"http://127.0.0.1:{PORT}/"
    print(f"BOYDE Atölye çalışıyor: {adres}  (kapatmak için bu pencereyi kapatın)", flush=True)
    if ac:
        import webbrowser
        webbrowser.open(adres)
    try:
        sunucu.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    calistir()
