"""BOYDE Atölye'nin indirme paketi: uygulamanın çalışması için gereken dosyalar tek ZIP'te (depo tamamı ~370 MB; paket
~15 MB). Eski işlerin görselleri, fotoğraflar ve kataloglar pakette yok.

İçerik: atolye/, scripts/ (yazı tipleri dahil; Blender betikleri de, kullanılmasalar da küçükler), 3MF şablonu,
BOYDE logoları (katalog başlığı), site şablonlarının sırası, Uzar'ın bilgiler.json'u (uzar_isimlik modülü yüklenirken
okur), Windows dosyaları ve belgeler. Müşteri verileri (atolye_veri) pakete girmez.

Çıktı : dist/BOYDE_Atolye.zip (git'e girmez)
Kullanım: python3 scripts/atolye_paket.py
"""
import os
import zipfile

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KLASORLER = ["atolye", "scripts"]
DOSYALAR = ["isimlik/orijinal/Two_line_Customizable_Name_Plate.3mf", "uzar_isimlik/bilgiler.json",
            "site_sablonlari/sira.json", "site_sablonlari/README.md", "kurulum.bat", "BOYDE_Atolye.bat",
            "guncelle.bat", "CLAUDE.md"]
LOGO = "boyde_labs/logo"
ATLA = ("__pycache__", ".pyc", ".npz")


def dosyalar():
    out = []
    for k in KLASORLER:
        for d, dirs, fs in os.walk(os.path.join(KOK, k)):
            dirs[:] = [x for x in dirs if x != "__pycache__"]
            out += [os.path.join(d, f) for f in fs if not f.endswith(ATLA)]
    out += [os.path.join(KOK, f) for f in DOSYALAR]
    out += [os.path.join(KOK, LOGO, f) for f in os.listdir(os.path.join(KOK, LOGO)) if f.endswith(".png")]
    return sorted(out)


OKU_BENI = """BOYDE Atolye - kurulum (Windows)

1. Python 3.11'i kurun: https://www.python.org/downloads/
   Kurulumun ilk ekraninda "Add python.exe to PATH" kutusunu isaretleyin.
2. Bu klasorde kurulum.bat dosyasina cift tiklayin (bir kez; birkac dakika surer).
3. Her gun BOYDE_Atolye.bat ile acin. Panel tarayicida acilir: http://127.0.0.1:8765
   Pencereyi kapatinca uygulama kapanir.

Musteri kayitlari ve uretilen dosyalar: Belgeler\\BOYDE Atolye
Guncelleme: yeni BOYDE_Atolye.zip'i bu klasorun uzerine acip kurulum.bat'i bir kez calistirin.
Ayrinti: atolye\\README.md
"""


def main():
    os.makedirs(os.path.join(KOK, "dist"), exist_ok=True)
    yol = os.path.join(KOK, "dist", "BOYDE_Atolye.zip")
    with zipfile.ZipFile(yol, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in dosyalar():
            z.write(f, os.path.join("BOYDE_Atolye", os.path.relpath(f, KOK)))
        z.writestr("BOYDE_Atolye/OKU_BENI.txt", OKU_BENI.replace("\n", "\r\n"))
    print(f"{os.path.relpath(yol, KOK)}  {len(dosyalar())} dosya, {os.path.getsize(yol) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
