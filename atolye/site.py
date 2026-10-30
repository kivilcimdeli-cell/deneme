"""İşletmenin web sayfası (isimlikteki QR'ın açtığı dijital kartvizit): scripts/sablon_site.py'nin beş şablonu.

Kural (CLAUDE.md): sayfa lastikçi tarzındaki 5 şablondan biriyle yapılır, şablonlar sırayla döner (1 → 2 → … → 5 → 1);
bir işletme bir kez şablon aldıysa yeniden üretimde aynı şablonda kalır. Depoda yapılanların sırası
site_sablonlari/sira.json'da; uygulamanın yaptıkları atolye_veri/site_sirasi.json'da (müşteri bilgisi: git'e girmez).
Sıradaki şablon ikisinin en son kaydından devam eder.

Adres: https://<sayfa adı>.qrsistem.workers.dev/ (ortak Cloudflare hesabı; QR bu adresi açar). Yayın elle: Workers'ta
sayfa adıyla bir Worker, içine zip.
"""
import datetime
import json
import os
import re
import sys

from . import SCRIPTS, VERI

if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

SIRA = os.path.join(VERI, "site_sirasi.json")
HESAP = "qrsistem"
EN_UZUN = 20                                            # sayfa adı: 4. sürüm QR'a sığsın (kare ≥ 0,9 mm)


def sayfa_adi(metin):
    """Türkçe harfler sadeleşir, yalnız a-z ve 0-9 (Cloudflare Worker adı)."""
    from sablonlar.ortak import tr_upper
    s = tr_upper(metin).translate(str.maketrans("ÇĞİÖŞÜÂÎÛ", "CGIOSUAIU")).lower()
    return re.sub(r"[^a-z0-9]+", "", s)[:EN_UZUN] or "isletme"


def sayfa_url(ad):
    return f"https://{ad}.{HESAP}.workers.dev/"


def _depo_sirasi():
    import sablon_site
    return [dict(r, kaynak="depo") for r in sablon_site.order()]


def _uygulama_sirasi():
    try:
        with open(SIRA, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return []


def siradaki():
    rows = sorted(_depo_sirasi() + _uygulama_sirasi(), key=lambda r: r.get("tarih", ""))
    return rows[-1]["sablon"] % 5 + 1 if rows else 1


def sablon_sec(kimlik, isletme, istenen=0):
    """Bu müşterinin şablonu: elle seçilen > kayıtlı > sıradaki. Kaydeder, döner numara."""
    rows = _uygulama_sirasi()
    kayitli = next((r for r in rows if r["kimlik"] == kimlik), None)
    n = int(istenen or 0) or (kayitli and kayitli["sablon"]) or siradaki()
    if not kayitli or kayitli["sablon"] != n:
        rows = [r for r in rows if r["kimlik"] != kimlik] + [
            {"isletme": isletme, "kimlik": kimlik, "sablon": n,
             "tarih": datetime.datetime.now().isoformat(timespec="seconds")}]
        os.makedirs(VERI, exist_ok=True)
        with open(SIRA, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
    return n


def karekod_oku(yol):
    """Bankanın IBAN karekodu (ekran görüntüsü) → içeriği; okunmazsa None."""
    import zxingcpp
    from PIL import Image
    r = zxingcpp.read_barcodes(Image.open(yol).convert("L"))
    return r[0].text if r else None


def bilgiler(b, klasor, marka, hizmet, renk_hex, ad, isaret=None):
    """Formdaki bilgilerden sablon_site'ın bilgiler.json'u. Geçersiz alanlar düşer, uyarı olur. Döner (sözlük,
    uyarılar)."""
    import qr_sistemi as Q
    uyar = []
    d = {"isletme": " ".join(b["isletme"].split()), "marka": marka, "hizmet": hizmet, "telefon": b["telefon"],
         "renk": renk_hex, "sayfa_url": sayfa_url(ad),
         "whatsapp_mesaj": b.get("whatsapp_mesaj") or "Merhaba, bilgi almak istiyorum."}
    for k in ("whatsapp", "konum", "web", "aciklama", "harita", "etiket"):
        if (b.get(k) or "").strip():
            d[k] = b[k].strip()
    if d.get("web") and not d["web"].startswith("http"):
        d["web"] = "https://" + d["web"]
    for k, fn, ad_ in (("instagram", Q.instagram_handle, "Instagram"), ("google", Q.google_url, "Google yorum")):
        v = (b.get(k) or "").strip()
        if v:
            try:
                fn(v)
                d[k] = v
            except Q.QRError as e:
                uyar.append(f"{ad_} bağlantısı sayfaya konmadı: {e}")
    if d.get("whatsapp"):
        try:
            Q.phone_e164(d["whatsapp"])
        except Q.QRError:
            uyar.append("WhatsApp numarası geçersiz; telefon kullanıldı")
            d.pop("whatsapp")
    iban = re.sub(r"\s", "", b.get("iban") or "").upper()
    if iban:
        try:
            d["iban"] = Q.iban_normalize(iban)
            d["iban_alici"] = (b.get("iban_alici") or "").strip()
            d["banka"] = (b.get("banka") or "").strip()
        except Q.QRError as e:
            uyar.append(f"IBAN sayfaya konmadı: {e}")
    if d.get("iban") and b.get("karekod"):
        icerik = karekod_oku(os.path.join(klasor, b["karekod"]))
        if icerik:
            try:
                Q.karekod_check(icerik, d["iban"])
                d["iban_karekod"] = icerik
            except Q.QRError as e:
                uyar.append(f"Banka karekodu IBAN'la uyuşmadı, konmadı: {e}")
        else:
            uyar.append("Banka karekodu görselden okunamadı (net bir ekran görüntüsü yükleyin)")
    if isaret:
        d["isaret"] = isaret
    return d, uyar


def yap(is_, d, sablon=0, gif=False):
    """Siteyi müşteri klasörünün web/ altında üretir. Döner {"sablon", "ad", "url", "ciktilar"}."""
    import sablon_site
    klasor = is_.yol("web", "bilgiler.json")[:-len("bilgiler.json") - 1]
    n = sablon_sec(is_.musteri["kimlik"], d["isletme"], sablon)
    uyarilar = []
    for i, dd in enumerate(_kisaltmalar(d)):            # şablonda yazı sığmazsa (uzun unvan) kısaltılır
        with open(os.path.join(klasor, "bilgiler.json"), "w", encoding="utf-8") as f:
            json.dump(dd, f, ensure_ascii=False, indent=2)
        try:
            site, T, _ = sablon_site.build(klasor, n, previews=True, gif=gif, record=False)
            break
        except AssertionError as e:
            if "sığmadı" not in str(e) and "taştı" not in str(e):
                raise
            uyarilar.append(str(e))
    else:
        raise RuntimeError("sayfada yazılar sığmadı: " + "; ".join(uyarilar))
    if i:
        uyarilar = [f"Sayfa şablonuna sığmadığı için iş türü / unvan sayfada '{dd['hizmet']}' olarak yazıldı"
                    if dd.get("hizmet") else "Sayfa şablonuna sığmadığı için iş türü / unvan sayfada yazılmadı"]
    d = dd
    ad = re.match(r"https://([^.]+)\.", d["sayfa_url"]).group(1)
    zip_yol = os.path.join(klasor, f"{site.slug}_site.zip")
    hedef = os.path.join(klasor, f"{ad}_site.zip")
    if zip_yol != hedef:
        os.replace(zip_yol, hedef)
    ciktilar = [{"ad": f"Web sayfası (Cloudflare'e yüklenecek zip · Worker adı: {ad})", "yol": is_.goreli(hedef),
                 "tur": "zip"},
                {"ad": f"Sayfanın önizlemesi (şablon {n} · {T.AD})",
                 "yol": is_.goreli(os.path.join(klasor, "sayfa_onizleme.png")), "tur": "resim"},
                {"ad": "Sayfayı dene (tek dosya: telefonda ya da tarayıcıda açılır)",
                 "yol": is_.goreli(os.path.join(klasor, "sayfa_deneme.html")), "tur": "html"}]
    if gif:
        ciktilar.append({"ad": "Sayfa turu (GIF)", "yol": is_.goreli(os.path.join(klasor, "sayfa_tur.gif")),
                         "tur": "resim"})
    return {"sablon": n, "sablon_ad": T.AD, "ad": ad, "url": d["sayfa_url"], "ciktilar": ciktilar,
            "uyarilar": uyarilar if i else []}


def _kisaltmalar(d):
    """Sayfanın denenecek hâlleri: olduğu gibi; unvan (hizmet) ilk parçasına ("AVUKAT · ARABULUCU" → "AVUKAT") ya da
    ilk iki kelimesine; unvansız."""
    yield d
    h = d.get("hizmet") or ""
    if not h:
        return
    kisa = re.split(r"\s*[·,/|-]\s*", h)[0].strip()
    if kisa == h:
        kisa = " ".join(h.split()[:2])
    if kisa and kisa != h:
        yield dict(d, hizmet=kisa)
    yield {k: v for k, v in d.items() if k != "hizmet"}
