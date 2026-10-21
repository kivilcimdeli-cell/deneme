"""QR sistemi: işletme bilgilerinden (sayfa, banka karekodu, telefon, WhatsApp, Instagram, Google, IBAN) baskıya
uygun, doğrulanmış QR kodlar.

Bilgiler `uzar_isimlik/bilgiler.json` dosyasında; bilgi değişince yalnız o dosya değişir, isimlik ve sayfa aynı
koddan yeniden çıkar.

  * sayfa     : isimliğin ana QR'ı; okutunca kırmızı-siyah-beyaz işletme sayfası açılır (ara, WhatsApp, Instagram,
                Google, IBAN kopyala, karekod, rehbere kaydet). Sayfa: scripts/uzar_sayfa.py → uzar_isimlik/site/
  * karekod   : bankanın "karekod ile para transferi" kodu (TCMB karekod, alıcı + IBAN). Ekran görüntüsünden
                okunur (`oku`), CRC'si ve içindeki IBAN doğrulanır, aynı içerik siyah-beyaz yeniden çizilir: banka
                uygulamasıyla okutunca alıcısı ve IBAN'ı dolu para gönderme ekranı açılır.
  * iban      : TR + 24 hane, mod-97 kontrol hanesi doğrulanır (tek hane yanlışsa reddedilir)
  * telefon   : "+90 542 611 69 87" → TEL:+905426116987 (okutunca arama ekranı)
  * whatsapp  : https://wa.me/905426116987 (sayfada hazır mesajlı)
  * instagram : https://instagram.com/<kullanıcı adı>; "@ad", tam bağlantı ya da yalnız ad yazılabilir
  * google    : Google arama bağlantısı izleme parametrelerinden arındırılır (yalnız q kalır)

Bir isimlikte birlikte kullanılan kısa QR'lar (sürüm ≤ 4) aynı sürüme eşitlenir: eş boyda durur, boş kalan
kapasite hata düzeltmesine gider. Kare boyu en az MIN_MODULE (0,9 mm ≈ 0,4 nozulun iki çizgisi); çevresinde
QUIET kare beyaz sessiz bölge.

Doğrulama: her QR şekli (baskıya giden geometri) rasterleştirilip zxing ile okunur; ayrıca baskı ve okutma
hatası benzetiminde: siyah karelerin ±0,15 mm taşması / incelmesi, bulanıklık, 35° eğik bakış, döndürme,
uzaktan (kare başına 2,5 piksel), gölge ve gürültü, hepsi birden; temiz hâl ikinci okuyucuyla (OpenCV) da.

Çıktı : uzar_isimlik/qr_kontrol.png (kare boyu varsayılan 0,9 mm; `--kare 1.0`)

Kullanım:
  pip install segno zxing-cpp opencv-python-headless
  python3 scripts/qr_sistemi.py [--kare 0.9]
  python3 scripts/qr_sistemi.py oku resim.png        # banka karekodu ekran görüntüsünün içeriği
"""
import copy
import json
import os
import re
import sys
import urllib.parse
from dataclasses import dataclass, field

import manifold3d as m3
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402

DATA = os.path.join(A.ROOT, "uzar_isimlik", "bilgiler.json")
OUT = os.path.join(A.ROOT, "uzar_isimlik", "qr_kontrol.png")
MIN_MODULE = 0.9
QUIET = 2
SAME_VERSION_UP_TO = 4                            # bu sürüme kadar olanlar eşitlenir (daha uzunu kendi sürümünde)
UI = os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf")


class QRError(ValueError):
    pass


# ---------------------------------------------------------------- bilgilerin doğrulanması

def iban_normalize(s):
    """Boşluksuz büyük harf TR IBAN; biçim ya da mod-97 kontrol hanesi tutmazsa QRError."""
    s = re.sub(r"[\s-]+", "", s).upper()
    if not re.fullmatch(r"TR\d{24}", s):
        raise QRError(f"IBAN 'TR' + 24 rakam (26 karakter) olmalı: {s!r} ({len(s)} karakter)")
    if int("".join(str(int(ch, 36)) for ch in s[4:] + s[:4])) % 97 != 1:
        raise QRError(f"IBAN kontrol hanesi tutmuyor (yanlış yazılmış): {s}")
    return s


def iban_display(s):
    return " ".join(s[i:i + 4] for i in range(0, len(s), 4))


def phone_e164(s):
    """'0542 611 69 87', '+90 542 …', '542…' → '905426116987'."""
    d = re.sub(r"\D", "", s)
    if len(d) == 12 and d.startswith("90"):
        d = d[2:]
    elif len(d) == 11 and d.startswith("0"):
        d = d[1:]
    if len(d) != 10 or d[0] not in "2345689":
        raise QRError(f"Türkiye telefon numarası değil: {s!r}")
    return "90" + d


def phone_display(e164):
    d = "0" + e164[2:]
    return f"{d[:4]} {d[4:7]} {d[7:9]} {d[9:]}"


def instagram_handle(s):
    h = re.sub(r"^(https?://)?(www\.)?instagram\.com/", "", s.strip(), flags=re.I).lstrip("@")
    h = h.split("?")[0].strip("/")
    if not re.fullmatch(r"[A-Za-z0-9._]{1,30}", h):
        raise QRError(f"Instagram kullanıcı adı yalnız harf, rakam, nokta, alt çizgi (en çok 30): {s!r}")
    return h.lower()


def google_url(s):
    """Google arama bağlantısından yalnız aramayı bırakır; Haritalar / kısa bağlantılar ve # ile belirli bir
    pencereyi (ör. işletmenin yorumları) açan arama bağlantıları olduğu gibi kalır."""
    u = urllib.parse.urlsplit(s.strip())
    if not u.scheme.startswith("http"):
        raise QRError(f"bağlantı değil: {s!r}")
    if u.path == "/search" and not u.fragment:
        q = urllib.parse.parse_qs(u.query).get("q", [""])[0].strip()
        if not q:
            raise QRError("Google bağlantısında arama (q) yok")
        return "https://www.google.com/search?q=" + urllib.parse.quote_plus(q)
    return s.strip()


def https_url(s):
    if not re.fullmatch(r"https://[^\s]+", s.strip()):
        raise QRError(f"sayfa bağlantısı https:// ile başlamalı: {s!r}")
    return s.strip()


def tlv(s):
    """İki haneli etiket, iki haneli uzunluk, değer (EMVCo / TCMB karekod) → {etiket: değer}."""
    out, i = {}, 0
    while i < len(s):
        if i + 4 > len(s) or not s[i:i + 4].isdigit() or i + 4 + int(s[i + 2:i + 4]) > len(s):
            raise QRError("karekod alanları okunamadı")
        tag, n = s[i:i + 2], int(s[i + 2:i + 4])
        out[tag] = s[i + 4:i + 4 + n]
        i += 4 + n
    return out


def crc16(data):
    """CRC-16/CCITT-FALSE (karekod alan 63)."""
    crc = 0xFFFF
    for b in data.encode("utf-8"):
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else crc << 1
            crc &= 0xFFFF
    return f"{crc:04X}"


def karekod_check(s, iban=None):
    """Banka karekodu: alanlar okunmalı, CRC (alan 63) tutmalı, içindeki IBAN verilen IBAN olmalı, sabit tutar
    (EMVCo alan 54) olmamalı. Döner: {"iban", "alici", "alanlar"}."""
    f = tlv(s)
    if "63" not in f or not s.endswith("6304" + f["63"]) or crc16(s[:-4]) != f["63"].upper():
        raise QRError("banka karekodu değil ya da bozuk (CRC tutmuyor)")
    if s.startswith("000201") and "54" in f:
        raise QRError(f"karekodda sabit tutar var ({f['54']} TL): uygulamadan tutarsız kod alınmalı")
    found = re.search(r"TR\d{24}", s)
    inner = {}
    for v in f.values():
        try:
            inner.update({k: w for k, w in tlv(v).items() if k not in inner})
        except QRError:
            pass
    out = {"iban": found.group(0) if found else None, "alici": inner.get("07") or f.get("59"), "alanlar": f}
    if iban and out["iban"] != iban:
        raise QRError(f"karekoddaki IBAN ({out['iban']}) yazılan IBAN'la ({iban}) aynı değil")
    return out


# ---------------------------------------------------------------- içerikler

@dataclass
class Entry:
    key: str                  # sayfa, karekod, telefon, whatsapp, instagram, google, iban
    label: str                # QR'ın etiketi
    content: str              # QR içeriği
    shown: str                # QR'ın yanında yazılabilecek metin
    qr: object = None         # segno QR
    tests: list = field(default_factory=list)

    @property
    def n(self):
        return len(self.qr.matrix)


@dataclass
class Info:
    business: str
    city: str
    tel: str                  # 905426116987
    whatsapp: str
    whatsapp_message: str
    instagram: str            # kullanıcı adı
    google: str
    iban: str
    holder: str
    bank: str
    karekod: str
    page: str
    entries: dict

    @property
    def phone(self):
        return phone_display(self.tel)


def load(path=DATA):
    d = json.load(open(path, encoding="utf-8"))
    tel = phone_e164(d["telefon"])
    wa = phone_e164(d.get("whatsapp") or d["telefon"])
    handle = instagram_handle(d["instagram"])
    iban = iban_normalize(d["iban"])
    karekod = d.get("iban_karekod", "").strip()
    holder = d.get("iban_alici", "").strip().upper()
    if karekod:
        k = karekod_check(karekod, iban)
        fold = lambda x: x.upper().translate(str.maketrans("ÇĞİÖŞÜ", "CGIOSU"))  # noqa: E731  bankalar Ç yerine C yazabilir
        if k["alici"] and holder and fold(k["alici"]) != fold(holder):
            raise QRError(f"karekoddaki alıcı ({k['alici']}) ile iban_alici ({holder}) farklı")
    info = Info(d.get("isletme", ""), d.get("sehir", ""), tel, wa, d.get("whatsapp_mesaj", ""), handle,
                google_url(d["google"]), iban, holder, d.get("banka", ""), karekod,
                https_url(d["sayfa_url"]) if d.get("sayfa_url") else "", {})   # adres yayından sonra yazılır
    E = [Entry("sayfa", "TARA · BİZE ULAŞ", info.page, info.page.split("://")[-1]),
         Entry("karekod", "KAREKOD İLE ÖDE", karekod, holder),
         Entry("telefon", "ARA", f"TEL:+{tel}", phone_display(tel)),     # büyük harf: alfasayısal kip
         Entry("whatsapp", "WHATSAPP", f"https://wa.me/{wa}", phone_display(wa)),
         Entry("instagram", "INSTAGRAM", f"https://instagram.com/{handle}", "@" + handle),
         Entry("google", "GOOGLE", info.google, "Google"),
         Entry("iban", "IBAN", iban, iban_display(iban))]
    info.entries = {e.key: e for e in E if e.content}
    return info


def whatsapp_link(info):
    """Sayfadaki WhatsApp düğmesi: hazır mesajlı."""
    url = f"https://wa.me/{info.whatsapp}"
    return url + "?text=" + urllib.parse.quote(info.whatsapp_message) if info.whatsapp_message else url


# ---------------------------------------------------------------- QR üretimi

def qr_set(info, keys, error="m"):
    """İstenen QR'lar (kopya). Sürümü SAME_VERSION_UP_TO'ya kadar olanlar en büyüğüne eşitlenir; segno boş
    kapasiteyle hata düzeltmesini yükseltir (M → Q → H)."""
    import segno
    out = [copy.copy(info.entries[k]) for k in keys]
    natural = [segno.make(e.content, error=error, micro=False).version for e in out]
    base = max([v for v in natural if v <= SAME_VERSION_UP_TO] or [1])
    for e, v in zip(out, natural):
        e.qr = segno.make(e.content, error=error, version=max(v, base), micro=False, boost_error=True)
        e.tests = []
    return out


def side(entry, module, quiet=QUIET):
    return (entry.n + 2 * quiet) * module


def module_for(entry, side_mm, quiet=QUIET, step=0.01):
    """`side_mm` kareye (sessiz bölge dahil) sığan kare boyu, `step`e aşağı yuvarlanmış."""
    return np.floor(side_mm / (entry.n + 2 * quiet) / step + 1e-9) * step


def shapes(entry, module, cx=0.0, cy=0.0, quiet=QUIET):
    """(açık, koyu, kenar): açık = sessiz bölge dahil kare eksi koyu kareler (beyaz); koyu = koyu kareler.
    Koyu kareler satır satır birleştirilir, köşeden değenler 0,01 mm ile kaynaşır."""
    if module < MIN_MODULE - 1e-9:
        raise QRError(f"{entry.key}: kare {module:.2f} mm < {MIN_MODULE} mm (0,4 nozul güvenle basmaz)")
    m = np.array(entry.qr.matrix, dtype=bool)
    n = m.shape[0]
    s = (n + 2 * quiet) * module
    x0, y1 = cx - n * module / 2, cy + n * module / 2
    runs = []
    for r, row in enumerate(m):
        c = 0
        while c < n:
            if row[c]:
                c1 = c
                while c1 < n and row[c1]:
                    c1 += 1
                runs.append(A.rect(x0 + c * module, y1 - (r + 1) * module, x0 + c1 * module, y1 - r * module))
                c = c1
            else:
                c += 1
    dark = A.union(*runs).offset(0.01, m3.JoinType.Miter)
    light = A.rect(cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2) - dark
    return light, dark, s


# ---------------------------------------------------------------- okuma ve baskı benzetimi

BODY, PAPER = 35, 232            # siyah ve beyaz filamentin gri tonu


def raster(light, ppm=20.0, pad=3.0):
    """Beyaz alanı siyah zemine çizer (çift-tek kuralı: her çokgen XOR)."""
    x0, y0, x1, y1 = light.bounds()
    x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    W, H = int(round((x1 - x0) * ppm)), int(round((y1 - y0) * ppm))
    acc = np.zeros((H, W), bool)
    for p in light.to_polygons():
        im = Image.new("1", (W, H), 0)
        ImageDraw.Draw(im).polygon([((u - x0) * ppm, (y1 - v) * ppm) for u, v in p], fill=1)
        acc ^= np.array(im)
    img = np.full((H, W), BODY, np.uint8)
    img[acc] = PAPER
    return Image.fromarray(img)


def _perspective(im, tilt):
    """Alt kenar etrafında `tilt` derece eğik bakış: dikey kısalma ve üst kenar daralması."""
    w, h = im.size
    k = 0.22 * np.sin(np.radians(tilt))
    h2 = max(1, int(h * np.cos(np.radians(tilt))))
    dst = [(w * k, 0), (w * (1 - k), 0), (w, h2), (0, h2)]
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    M = []
    for (x, y), (u, v) in zip(dst, src):
        M.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        M.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    coeffs = np.linalg.solve(np.array(M, float), np.array(src, float).reshape(8))
    return im.transform((w, h2), Image.PERSPECTIVE, tuple(coeffs), Image.BICUBIC, fillcolor=BODY)


def simulate(img, ppm, module, bleed=0.0, blur=0.0, tilt=0.0, rot=0.0, px_per_module=None, noise=0.0, shade=0.0,
             seed=7):
    im = img
    if bleed:                                     # + siyah taşar (beyaz kareler küçülür), − siyah incelir
        k = 2 * max(1, int(round(abs(bleed) * ppm))) + 1
        im = im.filter(ImageFilter.MinFilter(k) if bleed > 0 else ImageFilter.MaxFilter(k))
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur * ppm))
    if rot:
        im = im.rotate(rot, Image.BICUBIC, expand=True, fillcolor=BODY)
    if tilt:
        im = _perspective(im, tilt)
    if px_per_module:
        s = px_per_module / (module * ppm)
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BOX)
    if noise or shade:
        a = np.asarray(im, float)
        a = a * (1 - shade * np.linspace(0, 1, a.shape[1]))[None, :]
        a = a + np.random.default_rng(seed).normal(0, noise, a.shape)
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return im


SIM_CASES = [("temiz", {}),
             ("siyah taşması +0,15 mm", dict(bleed=0.15)),
             ("siyah incelmesi −0,15 mm", dict(bleed=-0.15)),
             ("bulanık (0,3 mm)", dict(blur=0.3)),
             ("35° eğik bakış", dict(tilt=35)),
             ("20° döndürülmüş", dict(rot=20)),
             ("uzaktan (kare 2,5 px)", dict(px_per_module=2.5)),
             ("gölge + gürültü", dict(shade=0.45, noise=18)),
             ("hepsi birden", dict(bleed=0.1, blur=0.2, tilt=25, rot=8, px_per_module=3.5, shade=0.3, noise=12))]


def decode(im):
    import zxingcpp
    return [r.text for r in zxingcpp.read_barcodes(im, formats=zxingcpp.BarcodeFormat.QRCode)]


def verify(entry, module, ppm=20.0):
    """Baskıya giden şekli tüm benzetimlerde okur; entry.tests = [(durum, okundu mu)]."""
    import cv2
    light, _, _ = shapes(entry, module)
    img = raster(light, ppm)
    entry.tests = [(name, entry.content in decode(simulate(img, ppm, module, **kw))) for name, kw in SIM_CASES]
    text, _, _ = cv2.QRCodeDetector().detectAndDecode(np.array(img))
    entry.tests.append(("ikinci okuyucu (OpenCV)", text == entry.content))
    return all(ok for _, ok in entry.tests), img


def describe(entry, module):
    ec = {"L": "L %7", "M": "M %15", "Q": "Q %25", "H": "H %30"}[entry.qr.error.upper()]
    return (f"sürüm {entry.qr.version} ({entry.n}×{entry.n}), hata düzeltme {ec}, kare {module:.2f} mm, "
            f"QR {side(entry, module):.1f} mm (sessiz bölge dahil)")


# ---------------------------------------------------------------- rapor

REPORT_KEYS = ["sayfa", "karekod", "whatsapp", "instagram", "google", "telefon"]


def report(info, module, path=OUT, keys=REPORT_KEYS):
    f = lambda s: ImageFont.truetype(UI, s)  # noqa: E731
    cols, cw, ch = 3, 440, 760
    rows = (len(keys) + cols - 1) // cols
    W, H = cols * cw + (cols + 1) * 20, 100 + rows * (ch + 20)
    canvas = Image.new("RGB", (W, H), (244, 245, 247))
    dr = ImageDraw.Draw(canvas)
    dr.text((24, 20), f"{info.business} – QR SİSTEMİ KONTROLÜ", fill=(24, 26, 30), font=f(32))
    dr.text((24, 62), f"Kare {module:.2f} mm (en az {MIN_MODULE})  ·  baskıya giden şekil, baskı ve okutma hatası "
                      "benzetimiyle okundu", fill=(110, 114, 124), font=f(18))
    ok_all = True
    for i, e in enumerate(qr_set(info, keys)):
        ok, img = verify(e, module)
        ok_all &= ok
        x, y0 = 20 + (i % cols) * (cw + 20), 100 + (i // cols) * (ch + 20)
        dr.rounded_rectangle((x, y0, x + cw, y0 + ch), 22, fill=(226, 228, 232))
        q = img.resize((320, 320), Image.LANCZOS).convert("RGB")
        canvas.paste(q, (x + 60, y0 + 60))
        dr.text((x + 18, y0 + 14), e.label, fill=(24, 26, 30), font=f(26))
        y = y0 + 396
        text = e.content if len(e.content) <= 44 else e.content[:41] + "…"
        d1, d2 = describe(e, module).split(", kare")
        for line in (text, e.shown, d1, "kare" + d2):
            dr.text((x + 18, y), line, fill=(60, 64, 74), font=f(16))
            y += 24
        y += 6
        for name, good in e.tests:
            dr.text((x + 18, y), ("okundu   " if good else "OKUNMADI ") + name,
                    fill=(22, 120, 60) if good else (200, 30, 38), font=f(15))
            y += 22
    canvas.save(path)
    return ok_all


def main():
    args = sys.argv[1:]
    if args[:1] == ["oku"]:
        for p in args[1:]:
            texts = decode(Image.open(p).convert("L"))
            print(f"{p}: {texts or 'QR bulunamadı'}")
            for t in texts:
                try:
                    k = karekod_check(t)
                    print(f"  banka karekodu: alıcı {k['alici']}, IBAN {k['iban']}, CRC tamam ({len(t)} karakter)")
                except QRError as err:
                    print(f"  {err}")
        return
    module = float(args[args.index("--kare") + 1]) if "--kare" in args else MIN_MODULE
    info = load()
    ok = report(info, module)
    for e in qr_set(info, REPORT_KEYS):
        verify(e, module)
        bad = [n for n, good in e.tests if not good]
        text = e.content if len(e.content) <= 48 else e.content[:45] + "…"
        print(f"{e.key:10s} {text:48s} {describe(e, module)}  " +
              ("tüm testler okundu" if not bad else f"OKUNMADI: {bad}"))
    print(f"IBAN {iban_display(info.iban)} ({info.holder}, {info.bank}): mod-97 tamam, karekoddaki IBAN aynı  ·  "
          f"{os.path.relpath(OUT, A.ROOT)}  ·  {'HEPSİ OKUNDU' if ok else 'OKUNMAYAN VAR'}")


if __name__ == "__main__":
    main()
