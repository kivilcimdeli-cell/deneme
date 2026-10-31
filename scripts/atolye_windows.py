"""BOYDE Atölye Windows kurulumu: kurulum klasörünü hazırlar. GitHub Actions'ta Windows'ta çalışır
(.github/workflows/atolye-windows.yml); kurulum exe'sini sonra Inno Setup yapar (paket/windows/atolye.iss).

Kullanıcı: "hiç bunlarla uğraşmayıp direkt PC'mde duracak bir uygulama yapabilir miyiz": Python kurmadan, bat
dosyası çalıştırmadan; kur, masaüstündeki simgeyle aç.

Klasör (build/BOYDE_Atolye; kurulunca %LOCALAPPDATA%\\Programs\\BOYDE Atolye):
  atolye/, scripts/, şablon, logolar   uygulama: indirme paketiyle aynı dosyalar (scripts/atolye_paket.py), bat'sız
  python/                              gömülü Python 3.11 (python.org "embeddable") ve paketler (Lib/site-packages)
  tarayici/                            site önizlemeleri için Chromium (Playwright; atolye/__init__.py yerini söyler)
  BOYDE_Atolye.ico
Simge: python\\pythonw.exe -m atolye.masaustu (konsolsuz pencere: atolye/masaustu.py).

Kullanım (Windows, Python 3.11): python scripts/atolye_windows.py
"""
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import atolye_paket as P  # noqa: E402

GOMULU = "3.11.9"                                           # python.org'un hazır Windows paketi olan son 3.11
URL = f"https://www.python.org/ftp/python/{GOMULU}/python-{GOMULU}-embed-amd64.zip"
HEDEF = os.path.join(P.KOK, "build", "BOYDE_Atolye")
BAT = {"kurulum.bat", "BOYDE_Atolye.bat", "guncelle.bat"}   # kurulumda gerekmez
# gömülü Python'un arama yolu (._pth: PYTHONPATH'i yok sayar): standart kitaplık, uygulama kökü ve scripts/
# (alt süreçler de bulsun: isler.py), sonra paketler
PTH = ["python311.zip", ".", "..", r"..\scripts", r"Lib\site-packages", "import site"]


def boyut(yol):
    return sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(yol) for f in fs) / 1e6


def uygulama():
    for f in P.dosyalar():
        rel = os.path.relpath(f, P.KOK)
        if rel in BAT:
            continue
        hedef = os.path.join(HEDEF, rel)
        os.makedirs(os.path.dirname(hedef), exist_ok=True)
        shutil.copy2(f, hedef)
    shutil.copy2(os.path.join(P.KOK, "paket", "windows", "BOYDE_Atolye.ico"), HEDEF)
    with open(os.path.join(HEDEF, "surum.txt"), "w", encoding="utf-8") as f:   # arayüzde görünür (atolye.SURUM)
        f.write(os.environ.get("SURUM", "yerel"))


def python():
    py = os.path.join(HEDEF, "python")
    zp = os.path.join(P.KOK, "build", os.path.basename(URL))
    if not os.path.exists(zp):
        urllib.request.urlretrieve(URL, zp)
    zipfile.ZipFile(zp).extractall(py)
    with open(os.path.join(py, "python311._pth"), "w", encoding="utf-8") as f:
        f.write("\n".join(PTH) + "\n")
    subprocess.run([sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "--only-binary=:all:",
                    "--target", os.path.join(py, "Lib", "site-packages"),
                    "-r", os.path.join(P.KOK, "atolye", "requirements.txt")], check=True)
    return os.path.join(py, "python.exe")


def chromium(exe):
    env = dict(os.environ, PLAYWRIGHT_BROWSERS_PATH=os.path.join(HEDEF, "tarayici"))
    subprocess.run([exe, "-m", "playwright", "install", "chromium", "--only-shell"], check=True, env=env)


def main():
    if sys.platform != "win32" or sys.version_info[:2] != (3, 11):
        sys.exit("Windows'ta Python 3.11 ile çalışır (paketler gömülü Python 3.11'e uymalı)")
    shutil.rmtree(HEDEF, ignore_errors=True)
    uygulama()
    exe = python()
    chromium(exe)
    subprocess.run([exe, "-c", "import atolye.sunucu, atolye.masaustu, manifold3d, cv2, zxingcpp, playwright; "
                               "print('içe aktarma tamam')"], check=True, cwd=HEDEF)
    for k in ("python", "tarayici", "scripts", "atolye"):
        print(f"{k:10s} {boyut(os.path.join(HEDEF, k)):7.0f} MB")
    print(f"toplam     {boyut(HEDEF):7.0f} MB  ({os.path.relpath(HEDEF, P.KOK)})")


if __name__ == "__main__":
    main()
