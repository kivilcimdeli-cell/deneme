"""Claude köprüsü: algoritmanın karşılamadığı özel istekler ("logo daha büyük olsun", "arka yüze adres ekle")
bilgisayardaki Claude Code'a (claude CLI) tek seferlik iş olarak gider. Claude depoda (scripts/, atolye/) çalışır,
müşterinin klasörüne yazar; iş bitince klasöre eklenen yeni dosyalar müşterinin çıktılarına kaydedilir.

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


def bul():
    yol = os.environ.get("BOYDE_CLAUDE") or shutil.which("claude") or shutil.which("claude.cmd")
    return yol if yol and os.path.exists(yol) else None


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
- Sonuç dosyalarını müşterinin klasöründe cikti/ altına yaz (eski dosyanın üstüne değil, yeni adla: ..._v2.3mf).
- Depodaki üreticileri kullan (scripts/, atolye/urunler/); baskıya uygunluk kontrollerini (QR okuma, harf içi ve ara)
  atlama. Renk paletini ve marka kurallarını (CLAUDE.md) koru.
- İstek ürün eklentisinde kalıcı bir iyileştirme gerektiriyorsa eklentiyi de düzelt ve bunu tek satırla belirt.
- Bitince ne yaptığını en fazla 3 satırla yaz.
"""


def main():
    utf8_cikti()
    kimlik, istek = sys.argv[1], sys.argv[2]
    m = kayit.oku(kimlik)
    klasor = kayit.klasor(kimlik)
    once = {os.path.join(d, f) for d, _, fs in os.walk(klasor) for f in fs}
    print("@@ 5 Claude çalışıyor (bu iş birkaç dakika sürebilir)", flush=True)
    cli = bul()
    onek = ["cmd", "/c"] if cli.lower().endswith((".cmd", ".bat")) else []   # Windows'ta npm kurulumu claude.cmd
    p = subprocess.run(onek + [cli, "-p", istem(m, istek), "--permission-mode", "acceptEdits", "--add-dir", klasor],
                       cwd=KOK, text=True, encoding="utf-8", errors="replace", capture_output=True,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))     # Windows'ta konsol açılmasın
    print(p.stdout)
    if p.returncode:
        print(p.stderr)
        sys.exit(p.returncode)
    yeni = sorted({os.path.join(d, f) for d, _, fs in os.walk(klasor) for f in fs} - once)
    m = kayit.oku(kimlik)
    for y in yeni:
        rel = os.path.relpath(y, klasor).replace(os.sep, "/")
        if rel.startswith(("cikti/", "katalog")) and not rel.endswith((".json", ".tmp")):
            tur = "resim" if rel.lower().endswith((".png", ".jpg", ".jpeg")) else rel.rsplit(".", 1)[-1]
            m["ciktilar"].append({"ad": f"Claude: {os.path.basename(rel)}", "yol": rel, "tur": tur,
                                  "tarih": kayit.simdi()})
    ozet = p.stdout.strip().splitlines()[-3:]
    kayit.not_ekle(m, "Claude: " + " ".join(ozet)[:400])
    kayit.yaz(m)
    print("@@ 100 Claude bitirdi", flush=True)


if __name__ == "__main__":
    main()
