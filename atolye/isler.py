"""İş kuyruğu: katalog ve üretim işleri sırayla, ayrı Python süreçlerinde (isci.py) çalışır. Ağır işler aynı anda
çalışmaz (bilgisayarı yormasın); her işin durumu, yüzdesi ve günlüğü panele gider. Bir müşterinin işi sürerken ona
ikinci iş verilmez.
"""
import itertools
import os
import queue
import subprocess
import threading
import time

from . import KOK, PYTHON, SCRIPTS, kayit

_SAYAC = itertools.count(1)
_ISLER = {}
_KUYRUK = queue.Queue()
_KILIT = threading.Lock()


def _ortam():
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([KOK, SCRIPTS, env.get("PYTHONPATH", "")])
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"
    return env


def ekle(kimlik, eylem, arg="", baslik="", komut=None, ek=""):
    """Kuyruğa iş ekler. komut verilirse (Claude köprüsü gibi) o çalıştırılır, yoksa isci.py (ek: isci'ye ikinci
    argüman, ör. üretimde renk değişikliği JSON'u)."""
    with _KILIT:
        for j in _ISLER.values():
            if j["kimlik"] == kimlik and j["durum"] in ("bekliyor", "calisiyor"):
                raise RuntimeError("Bu müşterinin bir işi zaten sürüyor")
        no = next(_SAYAC)
        j = {"no": no, "kimlik": kimlik, "eylem": eylem, "arg": arg, "baslik": baslik or eylem,
             "durum": "bekliyor", "yuzde": 0, "mesaj": "Sırada", "gunluk": [], "eklendi": time.time(),
             "komut": komut or [PYTHON, "-m", "atolye.isci", eylem, kimlik, arg] + ([ek] if ek else [])}
        _ISLER[no] = j
    _KUYRUK.put(no)
    return _ozet(j)


def _ozet(j):
    return {k: v for k, v in j.items() if k not in ("komut",)}


def durum(no):
    j = _ISLER.get(int(no))
    return _ozet(j) if j else None


def musteri_isleri(kimlik):
    return [_ozet(j) for j in _ISLER.values() if j["kimlik"] == kimlik]


def mesgul():
    """Bekleyen ya da süren iş var mı (masaüstü başlatıcı kapanmadan önce bakar)."""
    return any(j["durum"] in ("bekliyor", "calisiyor") for j in _ISLER.values())


def hepsi():
    return [_ozet(j) for j in sorted(_ISLER.values(), key=lambda j: -j["no"])][:50]


def _calistir(j):
    j["durum"], j["mesaj"], j["basladi"] = "calisiyor", "Başladı", time.time()
    gunluk_yolu = os.path.join(kayit.klasor(j["kimlik"]), "gunluk.txt")
    p = subprocess.Popen(j["komut"], cwd=KOK, env=_ortam(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, encoding="utf-8", errors="replace",
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    with open(gunluk_yolu, "a", encoding="utf-8") as log:
        log.write(f"\n=== {kayit.simdi()} {j['baslik']} ===\n")
        for satir in p.stdout:
            satir = satir.rstrip()
            log.write(satir + "\n")
            if satir.startswith("@@ "):
                _, yuzde, *mesaj = satir.split(" ", 2) + [""]
                try:
                    j["yuzde"] = max(j["yuzde"], int(yuzde))
                except ValueError:
                    pass
                j["mesaj"] = " ".join(mesaj).strip() or j["mesaj"]
            elif satir:
                j["gunluk"] = (j["gunluk"] + [satir])[-200:]
    kod = p.wait()
    j["bitti"] = time.time()
    if kod == 0:
        j["durum"], j["yuzde"] = "bitti", 100
    else:
        j["durum"] = "hata"
        son = [s for s in j["gunluk"] if s.strip()][-3:]
        j["mesaj"] = "Hata: " + (son[-1] if son else f"çıkış kodu {kod}")


def _isci():
    while True:
        no = _KUYRUK.get()
        try:
            _calistir(_ISLER[no])
        except Exception as e:                               # noqa: BLE001
            _ISLER[no].update(durum="hata", mesaj=f"Hata: {e}")


threading.Thread(target=_isci, daemon=True, name="isler").start()
