"""Claude köprüsü: algoritmanın karşılamadığı özel istekler ("logo daha büyük olsun", "arka yüze adres ekle")
bilgisayardaki Claude Code'a (claude CLI) tek seferlik iş olarak gider. Claude depoda (scripts/, atolye/) çalışır,
müşterinin klasörüne yazar; iş bitince cikti/, katalog ve web/ altında yeni ya da değişen dosyalar müşterinin
çıktılarına kaydedilir (sayfa değişikliği: web/bilgiler.json düzenlenip `python -m atolye.site <kimlik>` ile sayfa
aynı şablonla yeniden üretilir; zip, önizleme ve deneme dosyası aynı adla yenilenir, çıktılarda en üste çıkar).

Kurulum (bir kez): Claude Code'u kurun ve oturum açın (https://claude.com/claude-code). Komut `claude` yolda değilse
BOYDE_CLAUDE ortam değişkenine tam yolunu yazın.

Kullanım (sunucu çağırır): python -m atolye.claude <müşteri kimliği> <istek>
"""
import json
import os
import shutil
import subprocess
import sys

from . import KOK, PYTHON, kayit, urunler, utf8_cikti


def _arama_yolu():
    """Claude Code'un aranacağı klasörler: PATH; Windows'ta kayıt defterindeki güncel PATH (Claude Code uygulamadan
    sonra kurulduysa uygulamanın PATH'i eski kalır); bilinen kurulum yerleri (resmî kurulum ~/.local/bin, npm,
    winget). Claude'un sohbet (masaüstü) uygulaması aranmaz: o komut satırı değil."""
    yollar = [os.environ.get("PATH", "")]
    if os.name == "nt":
        import winreg
        for kok, anahtar in ((winreg.HKEY_CURRENT_USER, "Environment"),
                             (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment")):
            try:
                with winreg.OpenKey(kok, anahtar) as k:
                    yollar.append(os.path.expandvars(winreg.QueryValueEx(k, "Path")[0]))
            except OSError:
                pass
    ev = os.path.expanduser("~")
    yollar += [os.path.join(ev, ".local", "bin"), os.path.join(ev, ".claude", "local"),
               os.path.join(os.environ.get("APPDATA", ev), "npm"),
               os.path.join(os.environ.get("LOCALAPPDATA", ev), "Microsoft", "WinGet", "Links")]
    return os.pathsep.join(y for y in yollar if y)


def bul():
    yol = os.environ.get("BOYDE_CLAUDE")
    if yol and os.path.exists(yol):
        return yol
    ara = _arama_yolu()
    return shutil.which("claude", path=ara) or shutil.which("claude.cmd", path=ara)


def komut(m, istek):
    """Sunucu için iş komutu (Claude yoksa None)."""
    if not bul():
        return None
    return [PYTHON, "-m", "atolye.claude", m["kimlik"], istek]


def istem(m, istek):
    u = urunler.bul(m["urun"])
    klasor = kayit.klasor(m["kimlik"])
    son = (m.get("secimler") or [{}])[-1].get("kod")
    return f"""BOYDE Atölye uygulamasından özel istek. Kısa ve öz çalış; gereksiz açıklama yazma.

Ürün: {u.AD} (eklenti: atolye/urunler/{u.__name__.rsplit('.', 1)[-1]}.py)
Müşteri: {m['ad']} · klasör: {klasor}
Bilgiler: {json.dumps(m['bilgiler'], ensure_ascii=False)}
Son seçilen tasarım: {son or '-'}
Mevcut çıktılar: {', '.join(c['yol'] for c in m.get('ciktilar', [])) or '-'}

İstek: {istek}

Kurallar:
- Baskı dosyası (3MF, önizleme) değişikliği: sonuç dosyalarını müşterinin klasöründe cikti/ altına yaz (eski dosyanın
  üstüne değil, yeni adla: ..._v2.3mf).
- Web sayfası (QR'ın açtığı sayfa) değişikliği: {klasor}/web/bilgiler.json'u düzenle (alanlar: isletme, marka, hizmet,
  telefon, whatsapp, whatsapp_mesaj, instagram, google, harita, konum, web, aciklama, etiket, renk, iban...), sonra
  sayfayı aynı şablonla yeniden üret: `{PYTHON} -m atolye.site {m['kimlik']}` (şablonu değiştirmek istenirse sonuna
  `--sablon N`). Zip, sayfa_onizleme.png ve sayfa_deneme.html web/ altında yenilenir ve çıktılara kendiliğinden
  eklenir; zip'i elle başka yere koyma. Şablonun düzenini bu müşteri için değiştirme (CLAUDE.md: yalnız renk,
  etiket, açıklama, bağlantılar, logo işareti); düzen hatası varsa scripts/sablonlar/ altında düzelt.
- Depodaki üreticileri kullan (scripts/, atolye/urunler/); baskıya uygunluk kontrollerini (QR okuma, harf içi ve ara)
  atlama. Renk paletini ve marka kurallarını (CLAUDE.md) koru.
- Python: {PYTHON} (uygulamanın kendi Python'u; paketler bunda). Betikleri bununla, uygulama klasöründe ({KOK})
  çalıştır; başka Python kurmaya çalışma.
- İstek ürün eklentisinde kalıcı bir iyileştirme gerektiriyorsa eklentiyi de düzelt ve bunu tek satırla belirt.
- Bitince ne yaptığını en fazla 3 satırla yaz.
"""


def _durum(klasor):
    """Klasördeki dosyalar: {göreli yol: (değişme zamanı, boy)}."""
    out = {}
    for d, _, fs in os.walk(klasor):
        for f in fs:
            p = os.path.join(d, f)
            try:
                st = os.stat(p)
            except OSError:
                continue
            out[os.path.relpath(p, klasor).replace(os.sep, "/")] = (st.st_mtime_ns, st.st_size)
    return out


def _cikti_mi(rel):
    """Çıktı sayılan dosyalar: cikti/ ve katalog klasörlerindekiler; web/ altında yalnız sayfanın zip'i, önizlemesi,
    deneme dosyası ve turu (web/site/ iç dosyaları, bilgiler.json, logo değil)."""
    if rel.endswith((".json", ".tmp", ".log", ".npz")):
        return False
    if rel.startswith(("cikti/", "katalog")):
        return True
    if rel.startswith("web/") and rel.count("/") == 1:
        ad = rel[4:]
        return ad.endswith("_site.zip") or ad in ("sayfa_onizleme.png", "sayfa_deneme.html", "sayfa_tur.gif")
    return False


def main():
    utf8_cikti()
    kimlik, istek = sys.argv[1], sys.argv[2]
    m = kayit.oku(kimlik)
    klasor = kayit.klasor(kimlik)
    once = _durum(klasor)
    print("@@ 5 Claude çalışıyor (bu iş birkaç dakika sürebilir)", flush=True)
    cli = bul()
    onek = ["cmd", "/c"] if cli.lower().endswith((".cmd", ".bat")) else []   # Windows'ta npm kurulumu claude.cmd
    # tek seferlik iş, kimse onaylayamaz: dosya düzenleme ve komutlar (uygulamanın Python'u ile üreticiler) serbest
    p = subprocess.run(onek + [cli, "-p", istem(m, istek), "--permission-mode", "acceptEdits",
                               "--allowedTools", "Bash,Read,Edit,Write,Glob,Grep", "--add-dir", klasor],
                       cwd=KOK, text=True, encoding="utf-8", errors="replace", capture_output=True,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))     # Windows'ta konsol açılmasın
    print(p.stdout)
    if p.returncode:
        print(p.stderr)
        sys.exit(p.returncode)
    sonra = _durum(klasor)
    m = kayit.oku(kimlik)                                  # atolye.site çıktıları kaydetmiş olabilir
    eklenen = 0
    for rel in sorted(r for r, v in sonra.items() if once.get(r) != v and _cikti_mi(r)):
        tur = "resim" if rel.lower().endswith((".png", ".jpg", ".jpeg", ".gif")) else rel.rsplit(".", 1)[-1]
        var = next((c for c in m["ciktilar"] if c["yol"] == rel), None)
        if var:                                            # aynı adla yenilenen dosya: çıktılarda en üste
            var["tarih"] = kayit.simdi()
        else:
            m["ciktilar"].append({"ad": f"Claude: {os.path.basename(rel)}", "yol": rel, "tur": tur,
                                  "tarih": kayit.simdi()})
        eklenen += 1
    if not eklenen:
        kayit.not_ekle(m, "Claude yeni ya da değişen bir çıktı dosyası bırakmadı (açıklamasına bakın)")
    ozet = p.stdout.strip().splitlines()[-3:]
    kayit.not_ekle(m, "Claude: " + " ".join(ozet)[:400])
    kayit.yaz(m)
    print("@@ 100 Claude bitirdi", flush=True)


if __name__ == "__main__":
    main()
