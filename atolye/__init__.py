"""BOYDE Atölye: siparişten baskı dosyasına yerel uygulama.

Kullanıcı ürünü seçer, müşteri bilgilerini girer; uygulama ürünün kataloğunu (QR'lı isimlikte 10, anahtarlıkta 20
örnek) ya da doğrudan baskı dosyasını üretir. Müşteri beğendiği örneğin kodunu söyleyince o tasarımın X2D 3MF'i
(QR'lı ürünlerde web sayfasıyla birlikte) hazırlanır. Seçimler öğrenilir: beğenilen şablon, renk ve simgeler sonraki
kataloglarda daha sık çıkar.

Yapı:
  sunucu.py   yerel web paneli (http://127.0.0.1:8765), JSON API ve arayüz dosyaları
  isler.py    iş kuyruğu: üretim ayrı bir Python sürecinde çalışır (isci.py), ilerleme satır satır okunur
  isci.py     alt süreç: ürün eklentisinin katalog / üret işlevini çağırır
  kayit.py    müşteri kayıtları (atolye_veri/musteriler/<kimlik>/musteri.json), çıktılar aynı klasörde
  ogrenme.py  tercihler: gösterilen ve seçilen tasarımların özellikleri; ağırlıklı seçim
  urunler/    ürün eklentileri (yeni ürün = yeni dosya; urunler/__init__.py'deki listeye eklenir)
  tasarim/    ürünlerin ortak parametrik tasarım parçaları
  arayuz/     index.html, app.js, stil.css

Başlatma: python -m atolye   (Windows'ta BOYDE_Atolye.bat)
"""
import os

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))      # depo kökü (scripts/, yazı tipleri)
# müşteri verileri (git'e girmez): Windows'ta Belgeler\BOYDE Atolye (yeni sürüm başka klasöre açılsa da kayıtlar kalır),
# başka yerde depo içinde atolye_veri; BOYDE_VERI ile değiştirilir
VERI = os.environ.get("BOYDE_VERI") or (os.path.join(os.path.expanduser("~"), "Documents", "BOYDE Atolye")
                                        if os.name == "nt" else os.path.join(KOK, "atolye_veri"))
SCRIPTS = os.path.join(KOK, "scripts")
PORT = int(os.environ.get("BOYDE_PORT", "8765"))
