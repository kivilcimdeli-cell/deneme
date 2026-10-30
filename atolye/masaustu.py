"""Masaüstü başlatıcı: Windows kurulumundaki BOYDE Atölye simgesi (pythonw -m atolye.masaustu).

Konsol penceresi açılmaz. Sunucu arka planda başlar; panel Edge'in (yoksa Chrome'un) uygulama penceresinde, adres
çubuğu olmadan açılır (kendi profiliyle: kullanıcının tarayıcısına karışmaz). Pencere kapanınca uygulama da kapanır;
o sırada süren ya da sırada bekleyen iş varsa bitmesi beklenir. Uygulama zaten açıksa yalnız yeni pencere açılır.
Hatalar veri klasöründe atolye_gunluk.txt'ye yazılır; açılmazsa ekrana uyarı çıkar.
"""
import os
import subprocess
import sys
import threading
import time
import traceback
import urllib.request
import webbrowser

from . import PORT, VERI

ADRES = f"http://127.0.0.1:{PORT}/"
PROFIL = os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "BOYDE Atolye", "pencere")
SESSIZ = 180            # pencere kapanışı anlaşılamadıysa: arayüzden bu kadar saniye istek gelmezse kapanır


def calisiyor():
    try:
        with urllib.request.urlopen(ADRES + "api/urunler", timeout=2) as r:
            return r.status == 200
    except OSError:
        return False


def tarayici():
    """Uygulama penceresi için Edge, yoksa Chrome; bulunamazsa None."""
    kokler = [os.environ.get(k) for k in ("ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA")]
    for alt in (r"Microsoft\Edge\Application\msedge.exe", r"Google\Chrome\Application\chrome.exe"):
        for k in kokler:
            if k and os.path.exists(os.path.join(k, alt)):
                return os.path.join(k, alt)
    return None


def pencere():
    """Paneli açar. Döner: uygulama penceresinin süreci ya da None (varsayılan tarayıcıda açıldı)."""
    exe = tarayici()
    if not exe:
        webbrowser.open(ADRES)
        return None
    os.makedirs(PROFIL, exist_ok=True)
    return subprocess.Popen([exe, f"--app={ADRES}", f"--user-data-dir={PROFIL}", "--no-first-run",
                             "--no-default-browser-check", "--window-size=1360,900"])


def uyari(metin):
    """Konsolsuz çalışırken ekrana uyarı kutusu (Windows); başka yerde günlüğe."""
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, metin, "BOYDE Atölye", 0x10)
    except Exception:                                    # noqa: BLE001
        print(metin, flush=True)


def main():
    os.makedirs(VERI, exist_ok=True)
    gunluk = os.path.join(VERI, "atolye_gunluk.txt")
    if sys.stdout is None or os.path.basename(sys.executable).lower() == "pythonw.exe":
        sys.stdout = sys.stderr = open(gunluk, "a", encoding="utf-8", buffering=1)
    print(f"\n=== {time.strftime('%Y-%m-%d %H:%M:%S')} açılıyor", flush=True)
    if calisiyor():                                      # zaten açık: yalnız pencere
        pencere()
        return
    try:
        from http.server import ThreadingHTTPServer

        from . import isler, sunucu
        srv = ThreadingHTTPServer(("127.0.0.1", PORT), sunucu.Panel)
    except Exception:                                    # noqa: BLE001
        traceback.print_exc()
        uyari(f"BOYDE Atölye açılamadı.\n\nAyrıntı: {gunluk}")
        return
    threading.Thread(target=srv.serve_forever, daemon=True, name="sunucu").start()
    print(f"çalışıyor: {ADRES}", flush=True)
    basla = time.time()
    p = pencere()
    kapandi = False
    if p is not None:
        p.wait()
        kapandi = time.time() - basla > 8                # hemen döndüyse açık bir tarayıcıya devretti: isteklere bak
    while not kapandi:
        time.sleep(5)
        kapandi = time.time() - max(sunucu.NABIZ[0], basla) > SESSIZ
    while isler.mesgul():                                # pencere kapandı; süren iş bitsin
        time.sleep(3)
    srv.shutdown()
    print("kapandı", flush=True)


if __name__ == "__main__":
    main()
