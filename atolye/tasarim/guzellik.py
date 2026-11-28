"""Güzellik koleksiyonu (kuaför, güzellik salonu, tırnak, kirpik, cilt bakım, lazer, makyaj, spa, gelin başı):
müşterinin bilgileriyle 9 × 12 ve 10 × 20 isimlik düzenleri.

Düzenler Shopier'deki örneklerden (scripts/boyde_guzellik.py: G01–G10, K01–K10) genelleştirildi: ad el yazısı ya
da yumuşak serif (büyük-küçük harfle), çiçek, papatya, gül, şakayık, nilüfer, dal, çelenk, parıltı süsleri; simge
güzellik dalına göre (makas, oje, kirpik, ruj, nilüfer, taç...). Renkler güzellik paletlerinden: pudra, ten rengi,
krem, lila, adaçayı, fuşya, siyah ya da beyaz gövde; mürdüm, moka, gül kurusu, rose gold yazı ve süsler.

9 × 12: lastikçi isimlikleriyle aynı yapı (gövde 1 cm, yazı ve süsler 2 mm kabartma). El yazısı ad harfleri birbirine
bağlı kalsın diye harf aralığı açılmadan yazılır (noktalar ayrılır); küçük satırlar (iş türü, hizmetler, telefon,
QR yazısı) isimlik9'daki gibi Outfit'le (kabartmada harf içi ≥ 0,7 mm). Renkli gövdede QR beyaz karoda.
10 × 20: isimlik20'nin yapısı (gövde 5 mm, sehpa gövde renginde); yazı ve süsler yüzeyle aynı hizada renkli dolgu
(örneklerdeki gibi; ince el yazıları da basılır: dolguda çizgi ≥ 0,5 mm). Önce isimlik20.olcu() çağrılmalı.
"""
import functools
import math
import re

from . import ortak as O                                       # önce: scripts/ yolu ve QR'ların çalışması
from . import isimlik9 as T
import boyde_guzellik as G  # noqa: E402  (motifler; örnek moduna geçirmez: boyde_urunler zaten yüklü)
from .ortak import (A, ADACAYI, BLACK, FUSYA, GUL, J, KREM, LILA, MOKA, MURDUM, NUDE, PUDRA, ROSE, S, WHITE,
                    YELLOW)

S.FONTS.update(G.S.FONTS)                                     # el yazısı tipleri (boyde_guzellik ekledi)
O.YAZI_AD.update({"pacifico": "Pacifico", "kaushan": "Kaushan Script", "yester": "Yesteryear", "norican": "Norican",
                  "frauncesi": "Fraunces italik", "frauncesy": "Fraunces italik", "dancing": "Dancing Script",
                  "playball": "Playball", "marcellus": "Marcellus", "josefin": "Josefin Sans",
                  "quick": "Quicksand", "caveat": "Caveat"})
# el yazısı adın en küçük boyu (mm): kabartmada (9 × 12) çizgi ve harf içi ≥ 0,7 mm kalsın; dolguda (10 × 20) ≥ 0,5
MIN_KABARTMA = {"pacifico": 8.0, "kaushan": 9.0, "yester": 14.0, "norican": 9.5, "fraunces": 8.0,
                "frauncesi": 8.0, "caveat": 9.0}
# harfleri birbirine bağlı el yazıları: harf aralığı açılmaz, harflerin değdiği yerde ara ölçülmez (dilimleyicide
# birleşir, el yazısında zaten bitişik); harf içi ölçülür. Öbürleri (Fraunces, Marcellus) isimlik9'daki gibi yazılır:
# dar düşen harf çiftleri açılır, noktalar ayrılır.
BITISIK = {"pacifico", "kaushan", "yester", "norican", "caveat", "dancing", "playball"}
MIN_DOLGU = {"pacifico": 6.0, "kaushan": 8.0, "yester": 10.0, "norican": 10.0, "fraunces": 6.0, "frauncesi": 6.0,
             "dancing": 10.0, "playball": 10.0, "marcellus": 5.5, "frauncesy": 6.0}

# güzellik dalları: (ad, simge)
DALLAR = {
    "kuafor": ("Kuaför", "makas"),
    "guzellik": ("Güzellik salonu", "sakayik"),
    "tirnak": ("Tırnak stüdyosu, nail art", "oje"),
    "kirpik": ("Kirpik, kaş, kalıcı makyaj", "kirpik"),
    "makyaj": ("Makyaj", "ruj"),
    "cilt": ("Cilt bakım, estetisyen", "gul"),
    "lazer": ("Lazer epilasyon", "parilti"),
    "spa": ("Spa, masaj", "lotus"),
    "gelin": ("Gelin başı, gelinlik", "tac"),
    "genel": ("Genel (çiçek)", "cicek"),
}

# paletler: (gövde, yazı, vurgu, süs) — yazı gövdede okunur (kontrast ≥ 2), süs çiçeklerin taç yaprakları
PALETLER = {
    "beyaz_murdum": (WHITE, MURDUM, GUL, PUDRA),
    "pudra": (PUDRA, MURDUM, MURDUM, WHITE),
    "nude": (NUDE, MOKA, FUSYA, WHITE),
    "siyah_rose": (BLACK, WHITE, ROSE, PUDRA),
    "krem": (KREM, MOKA, GUL, ADACAYI),
    "lila": (LILA, MURDUM, WHITE, WHITE),
    "beyaz_siyah": (WHITE, BLACK, ROSE, PUDRA),
    "adacayi": (ADACAYI, WHITE, MOKA, WHITE),
    "fusya": (FUSYA, WHITE, YELLOW, WHITE),
}
GOVDELER = [WHITE, PUDRA, NUDE, KREM, LILA, ADACAYI, FUSYA, BLACK]
YAZILAR = [MURDUM, MOKA, BLACK, WHITE, GUL, ROSE, FUSYA]
VURGULAR = [GUL, ROSE, FUSYA, MURDUM, MOKA, PUDRA, WHITE, ADACAYI, YELLOW, LILA]


def palet(govde, yazi, vurgu, sus):
    return O.Palet(govde, vurgu, sus, yazi)


def paletler(zemin=0, yazi=0, vurgu=0):
    """Formda seçilen renklere uyan paletler: {ad: (gövde, yazı, vurgu, süs)} ve uyarılar. Seçilen gövdeye hazır palet
    yoksa kurulur (açık gövdede mürdüm ya da moka yazı, koyuda beyaz)."""
    uyar, out = [], {}
    for ad, (g, y, v, s) in PALETLER.items():
        if zemin and g != zemin:
            continue
        out[ad] = (g, yazi or y, vurgu or v, s)
    if not out and zemin:
        koyu = O.Palet(zemin, WHITE).koyu
        y = yazi or (WHITE if koyu else (MURDUM if O.kontrast(zemin, MURDUM) >= 4 else BLACK))
        v = vurgu or next(c for c in (ROSE, GUL, FUSYA, YELLOW, PUDRA, WHITE) if c not in (zemin, y) and
                          O.kontrast(zemin, c) >= 1.4)
        s = next(c for c in (WHITE, PUDRA, ROSE, ADACAYI) if c not in (zemin, v) and O.kontrast(zemin, c) >= 1.2)
        out[O.AD[zemin]] = (zemin, y, v, s)
    for ad, (g, y, v, s) in out.items():
        if O.kontrast(g, y) < O.OKUNUR:
            uyar.append(f"Yazı rengi ({O.AD[y]}) {O.AD[g]} gövdede zor okunur; yine de seçildiği gibi yapıldı.")
            break
    return out, uyar


# ---------------------------------------------------------------- simge (güzellik dalı), süsler

def _merkez(parcalar, cx, cy):
    b = A.union(*[cs for cs, _ in parcalar]).bounds()
    dx, dy = cx - (b[0] + b[2]) / 2, cy - (b[1] + b[3]) / 2
    return [(cs.translate((dx, dy)), r) for cs, r in parcalar]


def simge_parcalari(key, boy):
    """Dalın simgesi, yüksekliği ~boy (mm), ortası (0, 0): [(şekil, rol)] (rol: vurgu, sus, yazi)."""
    if key == "makas":
        p = [(G.makas(0, 0, boy * 1.05, -28.0), "vurgu")]
    elif key == "sakayik":
        p = [(G.sakayik(0, 0, boy / 2, 0.8), "vurgu")]
    elif key == "oje":
        sise, kapak = G.oje(0, 0, boy)
        p = [(sise, "vurgu"), (kapak, "yazi")]
    elif key == "kirpik":
        p = [(G.kirpik(0, 0, boy * 1.5, kas=True), "vurgu")]
    elif key == "ruj":
        uc, govde = G.ruj(0, 0, boy)
        p = [(uc, "sus"), (govde, "vurgu")]
    elif key == "gul":
        p = [(G.gul(0, 0, boy / 2), "vurgu")]
    elif key == "parilti":
        p = [(G.parilti(-boy * 0.12, 0, boy * 0.42), "vurgu"), (G.parilti(boy * 0.34, boy * 0.28, boy * 0.2), "vurgu"),
             (G.parilti(boy * 0.32, -boy * 0.3, boy * 0.14), "vurgu")]
    elif key == "lotus":
        p = [(G.lotus(0, 0, boy), "vurgu")]
    elif key == "tac":
        p = [(G.tac(0, 0, boy * 2.2), "vurgu")]
    else:
        yap, gob = G.cicek(0, 0, boy / 2)
        p = [(yap, "sus"), (gob, "vurgu")]
    return _merkez(p, 0.0, 0.0)


def _rol(p, rol):
    return {"vurgu": p.vurgu, "sus": p.vurgu2 or p.vurgu, "yazi": p.yazi}[rol]


# simgelerin en küçük boyu (mm): çizgileri boyla incelir (makas 21 mm'de çizilmiş); yuva küçükse çiçek konur
SIMGE_EN_AZ = {"makas": 20.0, "kirpik": 14.0, "oje": 15.0, "ruj": 16.0, "lotus": 14.0, "tac": 6.0, "parilti": 12.0,
               "gul": 9.0, "sakayik": 16.0, "cicek": 8.0}


def yuvarla(cs, en=0.9):
    """Kabartma süste `en` mm'den ince uçlar (yaprak ve parıltı uçları) yuvarlanır: basılmayan kılcal kalmaz."""
    return cs.offset(-en / 2, J).offset(en / 2, J)


def simge(d, c, p, cx, cy, boy, dolgu=False, esnek=1.15):
    """Dalın simgesi, ortası (cx, cy). Simge en küçük boyundan küçük yuvaya sığmıyorsa (esnek: yuvadan en çok bu kadar
    büyüyebilir) yerine çiçek konur. Döner sınır kutusu."""
    key = c.simge
    if SIMGE_EN_AZ.get(key, 0.0) > boy * esnek:
        key = "cicek"
    boy = max(boy, SIMGE_EN_AZ.get(key, 0.0))
    parts = [(cs.translate((cx, cy)), r) for cs, r in simge_parcalari(key, boy)]
    for cs, r in parts:
        sus(d, cs, _rol(p, r), dolgu)
    return A.union(*[cs for cs, _ in parts]).bounds()


def sus(d, cs, renk, dolgu=False):
    if dolgu:
        d.flat(None, cs, renk)
    else:
        cs = yuvarla(cs)
        d.add(None, cs, renk)
    return cs


def _alt(*cs):
    """Süslerin alt kenarı (adın üstü bundan aşağıda kalır)."""
    return min(x.bounds()[1] for x in cs)


# ---------------------------------------------------------------- yazı

# güzellikte sık geçen, içinde i olan İngilizce kelimeler: büyük harfte noktasız (NAIL ARTIST, MAKEUP STUDIO; örnekler
# gibi), baş harfte Nail Artist; öbür kelimeler Türkçe kuralla (GÜZELLİK, Kirpik)
INGILIZCE = {"nail", "nails", "artist", "artists", "studio", "studios", "design", "designer", "designs", "skin",
             "stylist", "lift", "lifting", "boutique", "hair", "lip", "lips", "microblading", "pink", "mini", "bridal",
             "white", "line", "liner", "prime", "shine", "tint", "with", "in", "this", "kids", "spirit", "aesthetic",
             "aesthetics", "clinic", "aesthetician", "esthetician", "facial", "brightening", "piercing", "nailart",
             "nailbar", "fix", "silk", "glitter", "artistry", "victoria", "vip", "living", "inn", "time", "nice",
             "chic", "kiss", "miss", "diva", "girl", "girls", "his", "her", "shiny", "it"}


def buyuk_harf(s):
    return re.sub(r"\w+", lambda m: m.group().upper() if m.group().lower() in INGILIZCE else O.tr_upper(m.group()), s)


def baslik(s):
    def kelime(m):
        w = m.group()
        return w[:1].upper() + w[1:].lower() if w.lower() in INGILIZCE else O.tr_title(w)
    return re.sub(r"\w+", kelime, s)


def _ad_metni(s):
    """El yazısı ad: büyük harfle yazıldıysa baş harfler büyük (DEFNE → Defne), yoksa yazıldığı gibi."""
    s = " ".join(s.split())
    return O.tr_title(s) if s == O.tr_upper(s) else s


def _bol(c, k, cap, max_w, dolgu=False, buyuk=False, tr=0.0, iki=True):
    """Adın yazılışı: (metin, harf aralığı, en küçük boy, satırlar, boy). Tek satırda çok küçülürse iki satır."""
    s = buyuk_harf(" ".join(c.marka.split())) if buyuk else _ad_metni(c.marka)
    if not tr and k in ("fraunces", "frauncesi", "frauncesy"):
        tr = 0.3                                              # serifli ad: harf arası ≥ 0,7 mm
    en_az = (MIN_DOLGU if dolgu else MIN_KABARTMA).get(k, 6.0 if dolgu else 8.0)
    tek = O.sigan(k, s, cap, max_w, tr)
    satirlar, cc = [s], tek
    w = s.split()
    if iki and tek < max(en_az, cap * 0.7) and len(w) > 1:
        best = None
        for i in range(1, len(w)):
            a, b = " ".join(w[:i]), " ".join(w[i:])
            ab = min(O.sigan(k, a, cap * 0.8, max_w, tr), O.sigan(k, b, cap * 0.8, max_w, tr))
            if best is None or ab > best[1]:
                best = ([a, b], ab)
        if best[1] > tek * 1.12:
            satirlar, cc = best
    return s, tr, en_az, satirlar, cc


def sigar(c, k, cap, max_w, dolgu=False, iki=True, buyuk=False):
    """Ad bu yuvaya en küçük boyundan büyük sığar mı (gerekirse iki satır)."""
    _, _, en_az, _, cc = _bol(c, k, cap, max_w, dolgu, buyuk, 0.0, iki)
    return cc >= en_az


def isim(d, c, p, k, x, y_orta, cap, max_w, align="l", renk=None, dolgu=False, buyuk=False, tr=0.0, iki=True,
         ust=None, alt=None):
    """Ad, ortası y_orta'da; üstü `ust`ü geçmez (iki satır olunca aşağı uzar), altı `alt`ın altına inmez (alttaki
    satırlara yer kalsın; sığmazsa küçülür). Genişliğe sığmazsa küçülür, çok küçülürse iki satıra bölünür (satırlar
    birbirine değmez). El yazısında harf aralığı açılmaz (harfler bağlı kalır). Döner (alt kenar, üst kenar)."""
    s, tr, en_az, satirlar, cc = _bol(c, k, cap, max_w, dolgu, buyuk, tr, iki)
    if cc < en_az:
        d.zayif.append(f"ad küçük kaldı ({cc:.1f} mm)")
        cc = en_az
    for _ in range(12):
        cs = _ad_blok(k, satirlar, cc, x, align, tr, max_w, dolgu)
        b = cs.bounds()
        dy = y_orta - (b[1] + b[3]) / 2
        if ust is not None:
            dy = min(dy, ust - b[3])
        if alt is None or b[1] + dy >= alt:
            break
        if ust is None or b[3] - b[1] <= ust - alt:            # yukarı kaydırmak yeter
            dy = alt - b[1]
            break
        if cc * 0.94 < en_az:                                  # daha küçülemez: yazılar sıkışık kalır (kontrol)
            d.zayif.append(f"ad küçük kaldı ({cc * 0.94:.1f} mm)")
            break
        cc *= 0.94
    d.ad_oran = min(1.0, cc * len(satirlar) / cap)
    if k in BITISIK:
        d.bitisik.add("ad")
    cs = cs.translate((0.0, dy))
    (d.flat if dolgu else d.add)("ad", cs, renk if renk is not None else p.yazi)
    b = cs.bounds()
    return b[1], b[3]


def _ad_blok(k, satirlar, cc, x, align, tr, max_w, dolgu):
    parcalar = []
    for t in satirlar:
        if k in BITISIK:
            cs = S.t(k, t, cc, x, 0.0, align, tr)
        else:
            cs = O.yazi(k, t, cc, x, 0.0, align, tr, max_w, kabartma=not dolgu, min_cap=cc * 0.92)
        if parcalar:                                          # alt satır: kuyruklar ve noktalar arasında ≥ 1 mm
            ust_ = A.union(*parcalar)
            for i in range(40):
                aday = cs.translate((0.0, -cc * (1.15 + 0.05 * i)))
                if (ust_.offset(0.5 if dolgu else 0.6, J) ^ aday.offset(0.5 if dolgu else 0.6, J)).is_empty():
                    break
            cs = aday
        parcalar.append(cs)
    return A.union(*parcalar)


def _yer(c, tel_y, tel_cap=5.2, hizmet=True, ek=0.0, w=None):
    """Adın altı en az buraya: altında iş türü (varsa; w genişliğe sığmazsa iki satır) ve telefona yer kalsın."""
    n = len(_bolunmus(c.hizmet, 4.6, w, 1.0)) if hizmet and c.hizmet and w else 1
    return tel_y + tel_cap / 2 + 3.2 + (8.4 + 6.6 * (n - 1) if hizmet and c.hizmet else 0.0) + ek


@functools.lru_cache(maxsize=256)
def _bolunmus(s, cap, max_w, tr):
    """Satır en küçük boyda da genişliğe sığmıyorsa kelimelerinden iki satır (GÜZELLİK / SALONU)."""
    cc, tt = O.sigdir(O.SATIR, s, cap, max_w, tr)
    b = O.yazi(O.SATIR, s, cc, 0.0, 0.0, "l", tt, max_w, min_cap=O.MIN_BOY).bounds()
    w = s.split()
    if b[2] - b[0] <= max_w + 0.2 or len(w) < 2:
        return (s,)
    i = min(range(1, len(w)), key=lambda i: abs(len(" ".join(w[:i])) - len(" ".join(w[i:]))))
    return " ".join(w[:i]), " ".join(w[i:])


def satir(d, ad, s, x, y_ust, cap, max_w, align, tr, renk):
    """isimlik9.satir; sığmazsa iki satır. Döner alt kenar."""
    for i, t in enumerate(_bolunmus(s, cap, max_w, tr)):
        y_ust = T.satir(d, ad if i == 0 else f"{ad} 2", t, x, y_ust - (1.8 if i else 0.0), cap, max_w, align, tr, renk)
    return y_ust


def duz(d, ad, k, s, cap, x, y, align="l", tr=0.0, max_w=None, renk=None):
    """Dolgu yazı (10 × 20), y büyük harflerin ortası; el yazısı değilse dar düşen harf çiftleri açılır (ara ≥ 0,6 mm),
    noktalar ayrılır. Döner şekil."""
    if not s:
        return None
    cs = _dolgu_yazi(k, s, cap, x, y, align, tr, max_w)
    d.flat(ad, cs, renk)
    return cs


def _dolgu_yazi(k, s, cap, x, y, align="l", tr=0.0, max_w=None):
    if k in BITISIK:
        return S.t(k, s, cap, x, y, align, tr, max_w)
    return O.yazi(k, s, cap, x, y, align, tr, max_w, ara=0.6, kabartma=False, min_cap=min(cap, 4.0))


# ---------------------------------------------------------------- QR

def qr_karo(d, c, p, cx, cy, s, cerceve=False, yazi=None, dolgu=False, kalp=False):
    """QR yüzeyle aynı hizada. Siyah ve beyaz gövdede isimlik9'daki gibi; öbür gövdelerde kareler yazı renginde
    (koyuysa) doğrudan gövdede ya da beyaz karoda. Altında yazı (RANDEVU) vurgu renginde."""
    n0 = len(d.inlay)
    if p.govde in (BLACK, WHITE) and not dolgu:
        tile = T.qr(d, c, p, cx, cy, s, cerceve, yazi)
        d.qr_ids.update(id(cs) for cs, _ in d.inlay[n0:])
    else:
        import qr_sistemi as Q
        koyu_kare = p.yazi if O.kontrast(WHITE, p.yazi) >= 7 else BLACK
        dogrudan = O.kontrast(p.govde, koyu_kare) >= 8 and p.govde != BLACK
        e = O.qr_girdi(c.url, False)
        _, dark, _ = Q.shapes(e, Q.module_for(e, s), cx, cy)
        tile = A.rrect(s, s, 1.6, cx, cy)
        if p.govde == BLACK:
            d.inlay.append((tile - dark, WHITE))
        elif dogrudan:
            d.inlay.append((dark ^ tile, koyu_kare))
        else:
            d.inlay.append((tile - dark, WHITE))
            d.inlay.append((dark ^ tile, koyu_kare))
        d.qr_ids.update(id(cs) for cs, _ in d.inlay[n0:])
        d.lines["QR"] = tile
        d.qr_entry, d.qr_side = e, s
        alt = tile.bounds()[1]
        if cerceve:
            g, w = 1.8, 1.2
            ring = A.rrect(s + 2 * (g + w), s + 2 * (g + w), 2.8, cx, cy) - A.rrect(s + 2 * g, s + 2 * g, 2.0, cx, cy)
            (d.flat if dolgu else d.add)("çerçeve", ring, p.vurgu)
            alt = ring.bounds()[1]
        yazi = c.qr_yazi if yazi is None else yazi
        if yazi:
            s_ = O.tr_upper(yazi)
            if dolgu:
                duz(d, "alt yazı", "josefin", s_, 4.4, cx, alt - 6.0, "c", 1.8, s + 6.0, p.vurgu)
            else:
                cc, tt = O.sigdir(O.SATIR, s_, 4.4, s + 2.0, 1.8)
                cs, _ = T._koy(O.yazi(O.SATIR, s_, cc, cx, 0.0, "c", tt, s + 2.0, min_cap=O.MIN_BOY), alt - 2.8)
                d.add("alt yazı", cs, p.vurgu)
    if kalp and "alt yazı" in d.lines:
        y = d.lines["alt yazı"].bounds()[1] - 4.6
        sus(d, G.kalp(cx, y, 4.2), p.vurgu2 or p.vurgu, dolgu)
    return tile


# ---------------------------------------------------------------- 9 × 12 (x −54..54, y ~12..86; kabartma)

X0 = -54.0


def _alt_satirlar(d, c, p, x, y, w, align="l", y_alt=27.0, tel_y=18.5, tel_cap=5.2, tr=1.2):
    """İş türü, hizmetler ve telefon (y: adın alt kenarı)."""
    if c.hizmet:
        y = satir(d, "iş türü", c.hizmet, x, y - 3.2, 4.6, w, align, tr, p.vurgu)
    T.hizmetler(d, c, p, x, y - 3.2, w, align, 4.4, n_max=2, y_alt=y_alt)
    T.telefon(d, c, p, x, tel_y, tel_cap, align, w)


def g_dal(d, c, p, k):
    """Sol üstte çiçekli dal (pudra çiçekler, gül kurusu sap), el yazısı ad, iş türü, hizmetler, telefon; QR sağda,
    altında RANDEVU ve kalp (G01 Defne)."""
    susler = [sus(d, G.dal([(-51.0, 73.5), (-45.0, 77.5), (-34.0, 80.5), (-22.0, 80.5)], 4, 4.6), p.vurgu)]
    for x, y, r in ((-47.5, 80.0, 4.8), (-33.5, 83.0, 3.6), (-22.0, 80.5, 4.2)):
        yap, gob = G.cicek(x, y, r)
        susler += [sus(d, yap, p.vurgu2), sus(d, gob, p.vurgu)]
    alt, _ = isim(d, c, p, k, X0, 59.5, 14.0, 62.0, ust=_alt(*susler) - 2.0, alt=_yer(c, 18.5, w=62.0))
    _alt_satirlar(d, c, p, X0, alt, 62.0)
    qr_karo(d, c, p, 34.0, 52.0, 36.0, kalp=True)


def g_sakayik(d, c, p, k):
    """Solda iri şakayık ve yaprakları, yanında ad ve iş türü; hizmetler, çizgi, telefon; QR sağda (G02)."""
    cx, cy, r = -43.0, 73.0, 10.5
    sus(d, G.sakayik(cx, cy, r, 0.8), p.vurgu2)
    for a in (225.0, 315.0):
        sus(d, G.yaprak(cx + (r - 0.8) * math.cos(math.radians(a)), cy + (r - 0.8) * math.sin(math.radians(a)), 6.5,
                        a, 3.2), p.vurgu2)
    x = cx + r + 3.5
    alt, _ = isim(d, c, p, k, x, 74.0, 11.0, 14.0 - x, iki=True, ust=85.0)
    y = min(alt, cy - r - 4.0)
    if c.hizmet:
        y = satir(d, "iş türü", c.hizmet, X0, y - 3.0, 4.6, 64.0, "l", 1.0, p.vurgu)
    y = T.hizmetler(d, c, p, X0, y - 3.2, 64.0, "l", 4.4, n_max=1, y_alt=29.0)
    d.add(None, O.bar(X0, -12.0, min(y - 3.6, 27.6), 1.2), p.vurgu2)
    T.telefon(d, c, p, X0, 18.8, 5.2, "l", 62.0)
    qr_karo(d, c, p, 36.0, 49.0, 34.0)


def g_oje(d, c, p, k):
    """QR solda; sağda simge ve parıltılar, el yazısı ad, iş türü, hizmetler, telefon (G03 Lâl)."""
    qr_karo(d, c, p, -34.0, 50.0, 36.0)
    x, w = -9.0, 63.0
    ib = simge(d, c, p, x + 8.0, 73.0, 17.0)
    for px, py, r, rol in ((ib[2] + 4.0, 82.0, 3.0, "vurgu"), (ib[0] - 3.5, 80.0, 2.2, "vurgu")):
        if px - r > -14.0:
            sus(d, G.parilti(px, py, r), _rol(p, rol))
    yan = ib[2] + 4.5
    if O.sigan(k, _ad_metni(c.marka), 14.0, 54.0 - yan) >= 10.0:
        alt, _ = isim(d, c, p, k, yan, 70.0, 14.0, 54.0 - yan, iki=False)
        alt = min(alt, ib[1])
    else:
        alt, _ = isim(d, c, p, k, x, ib[1] - 7.5, 12.0, w, ust=ib[1] - 2.0, alt=_yer(c, 19.0, w=w))
    _alt_satirlar(d, c, p, x, alt, w, y_alt=27.0, tel_y=19.0)


def g_kirpik(d, c, p, k):
    """Solda ortalı sütun: simge (kirpik), el yazısı ad, iş türü, hizmet, telefon; QR sağda (G04 Ela)."""
    cx, w = -24.0, 58.0
    ib = simge(d, c, p, cx, 76.0, 14.0)
    alt, _ = isim(d, c, p, k, cx, ib[1] - 10.5, 16.0, w, "c", ust=ib[1] - 2.0, alt=_yer(c, 19.0, w=w))
    _alt_satirlar(d, c, p, cx, alt, w, "c", y_alt=26.5, tel_y=19.0)
    qr_karo(d, c, p, 33.0, 51.0, 36.0)


def g_gul(d, c, p, k):
    """Solda boydan güllü dal (adaçayı sap, güller), yanında ad, iş türü, hizmetler, telefon; QR sağda (G05 Gülce)."""
    sus(d, G.dal([(-51.0, 14.0), (-49.0, 34.0), (-52.0, 54.0), (-49.5, 71.0)], 6, 6.0, uc=False), p.vurgu2)
    for x, y, r in ((-49.0, 78.5, 6.2), (-52.0, 57.0, 4.4), (-48.0, 36.5, 4.8)):
        sus(d, G.gul(x, y, r), p.vurgu)
    x, w = -38.5, 57.5
    alt, _ = isim(d, c, p, k, x, 71.0, 13.0, 50.0, ust=85.0, alt=_yer(c, 19.5, 5.0, w=w))
    _alt_satirlar(d, c, p, x, alt, w, y_alt=27.0, tel_y=19.5, tel_cap=5.0, tr=0.6)
    qr_karo(d, c, p, 38.5, 50.0, 34.0)


def g_parilti(d, c, p, k):
    """Ortalı el yazısı ad ve parıltılar, iş türü, kısa çizgi, hizmet, telefon; QR sağda (G06 İpek)."""
    cx, w = -26.0, 56.0
    for px, py, r in ((-50.0, 81.5, 4.2), (-43.0, 76.0, 2.4), (-3.0, 81.5, 3.4)):
        sus(d, G.parilti(px, py, r, 0.28), p.vurgu2)
    alt, ust = isim(d, c, p, k, cx, 63.0, 14.0, 50.0, "c", ust=72.5, alt=_yer(c, 18.0, ek=5.0, w=w))
    y = alt
    if c.hizmet:
        y = satir(d, "iş türü", c.hizmet, cx, y - 3.2, 4.6, w, "c", 0.8, p.vurgu)
    d.add(None, O.bar(cx - 11.0, cx + 11.0, y - 4.4, 1.2), p.vurgu2)
    T.hizmetler(d, c, p, cx, y - 7.6, w, "c", 4.4, n_max=1, y_alt=25.0)
    T.telefon(d, c, p, cx, 18.0, 5.2, "c", w)
    qr_karo(d, c, p, 33.0, 53.0, 36.0)


def g_ruj(d, c, p, k):
    """Solda simge (ruj), yanında el yazısı ad; iş türü, hizmetler, telefon; QR renkli çerçeveli, üstünde fiyonk
    (G07 Duru)."""
    ib = simge(d, c, p, -46.5, 68.0, 17.0)
    yan = ib[2] + 3.5
    if sigar(c, k, 17.0, 9.0 - yan):
        alt, _ = isim(d, c, p, k, yan, 67.0, 17.0, 9.0 - yan, ust=84.0)
        alt = min(alt, ib[1] + 1.0)
    else:                                                     # uzun ad: simgenin altında boydan
        alt, _ = isim(d, c, p, k, X0, ib[1] - 8.0, 12.0, 62.0, ust=ib[1] - 2.0, alt=_yer(c, 18.8, 5.4, w=62.0))
    _alt_satirlar(d, c, p, X0, alt, 62.0, y_alt=26.0, tel_y=18.8, tel_cap=5.4)
    tile = qr_karo(d, c, p, 34.0, 49.5, 34.0, cerceve=True)
    sus(d, G.fiyonk(34.0, tile.bounds()[3] + 3.0 + 9.5, 13.0), p.vurgu2)


def g_lotus(d, c, p, k):
    """Ortalı sütun: simge (nilüfer) ve altında çizgi, ad, iş türü, hizmet, telefon; QR sağda (G08 Lotus)."""
    cx, w = -25.0, 58.0
    ib = simge(d, c, p, cx, 74.0, 16.0)
    d.add(None, O.bar(cx - 13.0, cx + 13.0, ib[1] - 2.2, 1.2), p.vurgu)
    alt, _ = isim(d, c, p, k, cx, ib[1] - 11.5, 12.5, w, "c", ust=ib[1] - 4.6, alt=_yer(c, 19.0, w=w))
    _alt_satirlar(d, c, p, cx, alt, w, "c", y_alt=26.5, tel_y=19.0)
    qr_karo(d, c, p, 33.0, 51.0, 36.0)


def g_celenk(d, c, p, k):
    """Solda çelenkli rozet: üstte simge, içinde ad, altta çiçek; altında iş türü ve telefon; QR sağda, altında kalp
    (G09 Zarif)."""
    cx, cy, R = -28.0, 60.5, 19.5
    sus(d, G.celenk(cx, cy, R, adet=6, L=5.4, bosluk=66.0), p.vurgu)
    yap, gob = G.cicek(cx, cy - R, 4.4)
    sus(d, yap, p.vurgu2)
    sus(d, gob, p.vurgu)
    simge(d, c, p, cx, cy + R + 1.0, 7.0)
    dolgu = k == "dancing"
    y = cy - R - 6.5
    if sigar(c, k, 10.0, 2 * R - 11.0, dolgu):
        isim(d, c, p, k, cx - 0.5, cy + 0.5, 10.0, 2 * R - 11.0, "c", dolgu=dolgu)
    else:                                                     # uzun ad: çelenkte baş harfler, ad altında
        harf = O.monogram_harfleri(c.marka)
        cs = O.yazi("fraunces", harf, 11.0 if len(harf) == 1 else 9.5, cx, cy, "c", 0.6, 2 * R - 13.0)
        b = cs.bounds()
        d.add("monogram", cs.translate((cx - (b[0] + b[2]) / 2, cy - (b[1] + b[3]) / 2)), p.yazi)
        y, _ = isim(d, c, p, k, cx, y - 2.0, 9.0, 56.0, "c", dolgu=dolgu, iki=False, ust=cy - R - 4.0,
                    alt=_yer(c, 17.5, 5.0, w=50.0))
        y -= 3.0
    if c.hizmet:
        y = satir(d, "iş türü", c.hizmet, cx, y, 4.4, 50.0, "c", 0.8, p.vurgu)
    T.hizmetler(d, c, p, cx, y - 3.0, 50.0, "c", 4.4, n_max=1, y_alt=24.0)
    T.telefon(d, c, p, cx, 17.5, 5.0, "c", 50.0)
    qr_karo(d, c, p, 34.0, 53.0, 36.0, kalp=True)


def g_papatya(d, c, p, k):
    """Köşelerde papatyalar (beyaz taç yaprak, sarı göbek), el yazısı ad, iş türü, hizmetler, telefon; QR sağda
    (G10 Papatya)."""
    susler = []
    for x, y, r in ((-49.5, 79.5, 6.6), (-38.5, 82.5, 4.2), (5.0, 18.5, 5.0)):
        yap, gob = G.papatya(x, y, r)
        susler += [sus(d, yap, p.vurgu2), sus(d, gob, p.vurgu)]
    alt, _ = isim(d, c, p, k, X0, 62.0, 12.5, 62.0, ust=_alt(*susler[:4]) - 2.0, alt=_yer(c, 26.0, w=60.0))
    if c.hizmet:
        alt = satir(d, "iş türü", c.hizmet, X0, alt - 3.2, 4.6, 60.0, "l", 0.6, p.vurgu)
    T.hizmetler(d, c, p, X0, alt - 3.2, 60.0, "l", 4.4, n_max=2, y_alt=31.0)
    T.telefon(d, c, p, X0, 26.0, 5.2, "l", 48.0)
    qr_karo(d, c, p, 34.0, 53.0, 36.0)


# anahtar: (ad, kurucu, adın yazı tipleri — ilki örnekteki, kendi paleti)
DUZEN9 = {
    "dal": ("Çiçekli dal", g_dal, ["pacifico", "frauncesi"], "beyaz_murdum"),
    "sakayik": ("Şakayık", g_sakayik, ["pacifico", "fraunces"], "pudra"),
    "oje": ("Simge ve parıltı", g_oje, ["kaushan", "pacifico"], "nude"),
    "kirpik": ("Ortalı simge", g_kirpik, ["yester", "pacifico"], "siyah_rose"),
    "gul": ("Güllü dal", g_gul, ["fraunces", "frauncesi"], "krem"),
    "parilti": ("Parıltı", g_parilti, ["pacifico", "kaushan"], "lila"),
    "ruj": ("Çerçeveli QR ve fiyonk", g_ruj, ["kaushan", "norican"], "beyaz_siyah"),
    "lotus": ("Simge ve çizgi", g_lotus, ["fraunces", "frauncesi"], "adacayi"),
    "celenk": ("Çelenkli rozet", g_celenk, ["pacifico", "dancing"], "beyaz_murdum"),
    "papatya": ("Papatyalar", g_papatya, ["pacifico", "kaushan"], "fusya"),
}


# ---------------------------------------------------------------- 10 × 20 (x −90..90, y ~12..94; dolgu)

def _kisi_alt(d, c, p, x, y, w, align="l", kurum_k="josefin", tel_y=None):
    """Unvan, kurum ve telefon (dolgu); y: adın alt kenarı. Döner son satırın alt kenarı."""
    if c.hizmet:
        cs = duz(d, "unvan", "josefin", buyuk_harf(c.hizmet), 5.4, x, y - 6.2, align, 1.6, w, p.vurgu)
        y = cs.bounds()[1]
    if c.kurum:
        cs = duz(d, "kurum", kurum_k, buyuk_harf(c.kurum) if kurum_k == "josefin" else c.kurum, 4.6, x, y - 7.0,
                 align, 1.0 if kurum_k == "josefin" else 0.2, w, p.yazi)
        y = cs.bounds()[1]
    if c.telefon:
        duz(d, "telefon", "josefin", c.telefon, 5.6, x, tel_y if tel_y else y - 8.0, align, 0.6, w, p.yazi)
    return y


def _yer20(c, tel=True):
    """10 × 20: adın altı en az buraya (altında unvan, kurum ve telefon sehpanın örttüğü şeridin üstünde kalsın)."""
    return 11.0 + (10.8 if tel and c.telefon else 0.0) + (9.3 if c.kurum else 0.0) + (8.9 if c.hizmet else 0.0)


def k_dal(d, c, p, k):
    """Üstte boydan çiçekli dal, el yazısı ad, unvan, çizgi, kurum, telefon; QR sağda çerçeveli (K01 Aylin)."""
    sus(d, G.dal([(-88.0, 84.0), (-60.0, 89.0), (-30.0, 86.0), (-2.0, 90.0), (24.0, 87.0)], 8, 6.0, en=1.0),
        p.vurgu, True)
    for x, y, r in ((-74.0, 87.5, 4.6), (-44.0, 88.5, 3.6), (-16.0, 87.5, 4.2), (24.0, 87.0, 5.0)):
        yap, gob = G.cicek(x, y, r, ara=0.6)
        sus(d, yap, p.vurgu2, True)
        sus(d, gob, p.vurgu, True)
    alt, _ = isim(d, c, p, k, -86.0, 64.0, 16.0, 112.0, dolgu=True)
    if c.hizmet:
        alt = duz(d, "unvan", "josefin", buyuk_harf(c.hizmet), 5.6, -86.0, alt - 6.0, "l", 2.0, 112.0,
                  p.vurgu).bounds()[1]
    d.flat(None, O.bar(-86.0, -56.0, alt - 4.0, 1.0), p.vurgu2)
    y = alt - 4.0
    if c.kurum:
        y = duz(d, "kurum", "josefin", buyuk_harf(c.kurum), 4.8, -86.0, y - 6.4, "l", 1.4, 112.0, p.yazi).bounds()[1]
    duz(d, "telefon", "josefin", c.telefon, 5.6, -86.0, min(y - 8.0, 21.0), "l", 0.6, 112.0, p.yazi)
    simge(d, c, p, 14.0, 26.0, 12.0, dolgu=True)
    qr_karo(d, c, p, 66.0, 50.0, 38.0, cerceve=True, dolgu=True)


def k_oje(d, c, p, k):
    """Sol üstte simge ve parıltılar, el yazısı ad, unvan, kurum, telefon; QR sağda beyaz karoda (K02 Buse)."""
    ib = simge(d, c, p, -76.0, 78.0, 16.0, dolgu=True)
    sus(d, G.parilti(ib[2] + 6.0, 84.0, 3.6) + G.parilti(ib[2] + 11.5, 77.0, 2.2), p.vurgu2, True)
    alt, _ = isim(d, c, p, k, -86.0, 54.0, 15.0, 118.0, dolgu=True, ust=ib[1] - 2.5, alt=_yer20(c))
    _kisi_alt(d, c, p, -86.0, alt, 112.0, kurum_k="quick")
    qr_karo(d, c, p, 66.0, 56.0, 38.0, dolgu=True)


def k_sakayik(d, c, p, k):
    """Solda iri şakayık ve yaprakları; yanında büyük harfle ad, italik unvan, çizgi, kurum, telefon; QR sağda
    (K03 Gizem)."""
    sus(d, G.sakayik(-68.0, 56.0, 19.0, 0.7), p.vurgu2, True)
    for a in (200.0, 240.0, 320.0, 140.0):
        sus(d, G.yaprak(-68.0 + 18.0 * math.cos(math.radians(a)), 56.0 + 18.0 * math.sin(math.radians(a)), 11.0, a,
                        5.0), p.vurgu2, True)
    x, w = -40.0, 80.0
    alt, _ = isim(d, c, p, "marcellus", x, 72.0, 10.0, w, buyuk=True, tr=0.8, dolgu=True)
    if c.hizmet:
        alt = duz(d, "unvan", "frauncesy", c.hizmet if c.hizmet != buyuk_harf(c.hizmet) else baslik(c.hizmet),
                  7.0, x, alt - 7.0, "l", 0.0, w, p.yazi).bounds()[1]
    d.flat(None, O.bar(x, x + 26.0, alt - 4.4, 1.0), p.vurgu2)
    y = alt - 4.4
    if c.kurum:
        y = duz(d, "kurum", "josefin", buyuk_harf(c.kurum), 4.6, x, y - 6.0, "l", 0.6, w, p.yazi).bounds()[1]
    duz(d, "telefon", "josefin", c.telefon, 5.6, x, min(y - 8.0, 25.0), "l", 0.6, w, p.yazi)
    qr_karo(d, c, p, 66.0, 56.0, 36.0, dolgu=True)


def k_ruj(d, c, p, k):
    """Sol üstte simge (ruj), yanında el yazısı ad; unvan harf aralıklı, kurum, telefon; QR çerçeveli, üstünde
    fiyonk (K04 Ceren)."""
    ib = simge(d, c, p, -79.0, 70.0, 22.0, dolgu=True)
    alt, _ = isim(d, c, p, k, ib[2] + 4.0, 70.0, 15.0, 34.0 - ib[2] - 4.0, dolgu=True, ust=93.0, alt=_yer20(c))
    alt = min(alt, ib[1])
    _kisi_alt(d, c, p, -86.0, alt + 1.0, 116.0)
    tile = qr_karo(d, c, p, 66.0, 50.0, 36.0, cerceve=True, dolgu=True)
    sus(d, G.fiyonk(66.0, tile.bounds()[3] + 16.0, 18.0), p.vurgu2, True)


def k_kirpik(d, c, p, k):
    """Solda ortalı sütun: simge (kirpik), el yazısı ad, unvan, kurum, telefon; QR sağda (K05 Melis)."""
    cx = -34.0
    ib = simge(d, c, p, cx, 82.0, 13.0, dolgu=True)
    alt, _ = isim(d, c, p, k, cx, ib[1] - 12.0, 16.0, 100.0, "c", dolgu=True, ust=ib[1] - 2.5,
                  alt=_yer20(c, tel=False) + 13.5)                   # telefon altta sabit (19,5)
    _kisi_alt(d, c, p, cx, alt, 104.0, "c", tel_y=19.5)
    qr_karo(d, c, p, 66.0, 54.0, 38.0, dolgu=True)


def k_celenk(d, c, p, k):
    """Solda çelenk içinde baş harfler, üstünde gül; yanında büyük harfle ad, italik unvan, kurum, telefon; QR sağda
    (K06 Derya)."""
    cx, cy = -70.0, 56.0
    sus(d, G.celenk(cx, cy, 17.0, adet=6, L=5.4, bosluk=56.0), p.vurgu2, True)
    sus(d, G.gul(cx, cy + 17.0, 4.4, 0.6), p.vurgu, True)
    duz(d, "monogram", "marcellus", O.monogram_harfleri(c.marka), 11.0, cx, cy - 1.0, "c", 0.6, 19.0, p.yazi)
    x, w = -46.0, 82.0
    alt, _ = isim(d, c, p, "marcellus", x, 72.0, 9.6, w, buyuk=True, tr=1.0, dolgu=True)
    if c.hizmet:
        alt = duz(d, "unvan", "frauncesy", c.hizmet if c.hizmet != buyuk_harf(c.hizmet) else baslik(c.hizmet),
                  6.8, x, alt - 7.0, "l", 0.0, w, p.vurgu2).bounds()[1]
    y = alt
    if c.kurum:
        y = duz(d, "kurum", "josefin", buyuk_harf(c.kurum), 4.4, x, y - 8.0, "l", 1.6, w, p.yazi).bounds()[1]
    duz(d, "telefon", "josefin", c.telefon, 5.6, x, min(y - 8.5, 26.0), "l", 0.6, w, p.yazi)
    qr_karo(d, c, p, 66.0, 56.0, 36.0, dolgu=True)


def k_parilti(d, c, p, k):
    """Parıltılar, el yazısı ad, unvan, kısa çizgi, kurum, telefon; QR sağda (K07 Nazlı)."""
    for px, py, r in ((-84.0, 86.0, 4.4), (-76.0, 80.0, 2.4), (28.0, 84.0, 3.4), (22.0, 40.0, 2.4)):
        sus(d, G.parilti(px, py, r), p.vurgu2, True)
    alt, _ = isim(d, c, p, k, -64.0, 72.0, 13.0, 90.0, dolgu=True)
    y = alt
    if c.hizmet:
        y = duz(d, "unvan", "josefin", buyuk_harf(c.hizmet), 5.2, -86.0, min(y - 8.0, 52.0), "l", 1.6, 110.0,
                p.vurgu).bounds()[1]
    d.flat(None, O.bar(-86.0, -56.0, y - 4.0, 1.0), p.vurgu2)
    y -= 4.0
    if c.kurum:
        y = duz(d, "kurum", "josefin", buyuk_harf(c.kurum), 4.4, -86.0, y - 6.0, "l", 1.0, 110.0, p.yazi).bounds()[1]
    duz(d, "telefon", "josefin", c.telefon, 5.6, -86.0, min(y - 8.0, 21.0), "l", 0.6, 110.0, p.yazi)
    qr_karo(d, c, p, 66.0, 56.0, 38.0, dolgu=True)


def k_bant(d, c, p, k):
    """Sol üstte simge (kaş ve göz), yanında el yazısı ad; unvan, çizgi; altta boydan koyu bant, içinde oyma kurum ve
    telefon; QR sağ üstte (K08 Pınar)."""
    band = A.rrect(184.0, 18.0, 4.0, 0.0, 20.0)
    yazi = [cs for cs in (_dolgu_yazi("josefin", buyuk_harf(c.kurum), 4.4, -84.0, 20.0, "l", 0.8, 104.0)
                          if c.kurum else None,
                          _dolgu_yazi("josefin", c.telefon, 4.8, 84.0, 20.0, "r", 0.6, 60.0) if c.telefon else None)
            if cs]
    if yazi:
        d.lines["bant"] = A.union(*yazi)
    d.flat(None, band - (A.union(*yazi).offset(0.0, J) if yazi else A.empty()), p.yazi)
    ib = simge(d, c, p, -74.0, 76.0, 12.0, dolgu=True)
    alt, _ = isim(d, c, p, k, ib[2] + 4.0, 72.0, 15.0, 36.0 - ib[2] - 4.0, dolgu=True)
    if c.hizmet:
        cs = duz(d, "unvan", "josefin", buyuk_harf(c.hizmet), 5.2, -86.0, min(alt, ib[1]) - 8.0, "l", 1.6, 112.0,
                 p.vurgu)
        d.flat(None, O.bar(-86.0, 30.0, cs.bounds()[1] - 5.0, 0.9), p.vurgu)
    qr_karo(d, c, p, 66.0, 63.0, 34.0, dolgu=True)


def k_lotus(d, c, p, k):
    """Sol üstte simge (nilüfer) ve altında çizgi, yanında ad; unvan; kurum ve telefon; QR sağda (K09 Ezgi)."""
    ib = simge(d, c, p, -74.0, 74.0, 18.0, dolgu=True)
    d.flat(None, O.bar(-90.0, -58.0, ib[1] - 2.0, 1.0), p.yazi)
    x = -52.0
    alt, _ = isim(d, c, p, k, x, 76.0, 11.5, 34.0 - x, dolgu=True)
    if c.hizmet:
        duz(d, "unvan", "josefin", buyuk_harf(c.hizmet), 5.0, x, alt - 6.0, "l", 1.6, 34.0 - x, p.vurgu)
    y = min(alt - 12.0, ib[1] - 8.0)
    if c.kurum:
        y = duz(d, "kurum", "josefin", buyuk_harf(c.kurum), 4.4, -86.0, y - 4.0, "l", 1.0, 110.0, p.vurgu).bounds()[1]
    duz(d, "telefon", "josefin", c.telefon, 5.6, -86.0, min(y - 8.5, 27.0), "l", 0.6, 110.0, p.yazi)
    qr_karo(d, c, p, 66.0, 56.0, 38.0, dolgu=True)


def k_papatya(d, c, p, k):
    """Köşelerde papatyalar, el yazısı ad, unvan, kurum, telefon; QR sağda (K10 Burcu)."""
    for x, y, r in ((-82.0, 84.0, 7.4), (-68.0, 88.0, 4.6), (36.0, 18.0, 5.6), (24.0, 14.5, 3.6)):
        yap, gob = G.papatya(x, y, r, ara=0.6)
        sus(d, yap, p.vurgu2, True)
        sus(d, gob, p.vurgu, True)
    alt, _ = isim(d, c, p, k, -86.0, 62.0, 12.0, 116.0, dolgu=True, ust=76.0, alt=_yer20(c))
    _kisi_alt(d, c, p, -86.0, alt, 116.0)
    qr_karo(d, c, p, 66.0, 58.0, 38.0, dolgu=True)


DUZEN20 = {
    "dal": ("Çiçekli dal", k_dal, ["dancing", "playball"], "beyaz_murdum"),
    "oje": ("Simge ve parıltı", k_oje, ["playball", "dancing"], "nude"),
    "sakayik": ("Şakayık", k_sakayik, ["marcellus"], "pudra"),
    "ruj": ("Çerçeveli QR ve fiyonk", k_ruj, ["norican", "dancing"], "beyaz_siyah"),
    "kirpik": ("Ortalı simge", k_kirpik, ["dancing", "playball"], "siyah_rose"),
    "celenk": ("Çelenk monogram", k_celenk, ["marcellus"], "krem"),
    "parilti": ("Parıltı", k_parilti, ["pacifico", "dancing"], "lila"),
    "bant": ("Alt bant", k_bant, ["playball", "norican"], "krem"),
    "lotus": ("Simge ve çizgi", k_lotus, ["fraunces", "frauncesi"], "adacayi"),
    "papatya": ("Papatyalar", k_papatya, ["pacifico", "playball"], "fusya"),
}


# ---------------------------------------------------------------- tasarım, kontrol, görünüş

def tasarla(olcu, duzen, c, p, yazi_tipi):
    """olcu "9x12" ya da "10x20". Döner boyde_sektor.Design (isimlik9'daki ek alanlarla)."""
    d = S.Design(duzen, p.sc)
    d.duzen, d.palet, d.yazi_tipi, d.uyarilar, d.zayif = duzen, p, yazi_tipi, [], []
    d.ad_oran, d.gosterilen = 1.0, len(c.hizmetler)
    d.qr_entry = d.qr_side = None
    d.olcu, d.bitisik, d.qr_ids = olcu, set(), set()
    (DUZEN9 if olcu == "9x12" else DUZEN20)[duzen][1](d, c, p, yazi_tipi)
    return d


def kalite(d, c):
    return T.kalite(d, c) if d.olcu == "9x12" else d.ad_oran


def kontrol(d):
    """Baskıya uygunluk: (sorunlar, ölçüler). Kabartma yazıda harf içi ve ara ≥ 0,7 mm, dolgu yazıda ≥ 0,45;
    simgelerde ince alan az; kenara ve sehpanın örttüğü şeride taşma yok, kabartmalar birbirine yapışık değil."""
    from . import isimlik20 as T20
    from .ortak import B
    guvenli = T.GUVENLI if d.olcu == "9x12" else T20.guvenli()
    dolgular = {id(cs) for cs, _ in d.inlay}
    olcu, sorun = {}, []
    for k, cs in d.lines.items():
        if k in ("QR", "çerçeve"):
            continue
        inner, gap, _ = B.line_metrics(cs)
        olcu[k] = (inner, gap)
        sinir = 0.45 if id(cs) in dolgular or k == "bant" else O.MIN_IC
        if inner < sinir or (gap < sinir and k not in d.bitisik):
            sorun.append(f"{k}: harf içi {inner:.2f}, ara {gap:.2f} mm")
    ince = O.ince_alan(d, 0.9) if d.raised else 0.0       # süsler yuvarlatıldı (yuvarla): en ince yer 0,9 mm
    if ince > 12.0:
        sorun.append(f"süslerde 0,9 mm'den ince alan %{ince}")
    if d.raised:
        sorun += O.sikisik(d, guvenli)
    else:                                                 # dolgu: öğeler adlarıyla (sikisik dolguyu QR sayar)
        from types import SimpleNamespace
        sorun += O.sikisik(SimpleNamespace(
            lines=d.lines, raised=[(cs, c) for cs, c in d.inlay if id(cs) not in d.qr_ids],
            inlay=[(cs, c) for cs, c in d.inlay if id(cs) in d.qr_ids]), guvenli)
    return sorun, olcu


def ad(d):
    p = d.palet
    duzen = (DUZEN9 if d.olcu == "9x12" else DUZEN20)[d.duzen][0]
    sus_ = f", {O.AD[p.vurgu2]}" if p.vurgu2 and p.vurgu2 != p.vurgu else ""
    return (f"{duzen} · {O.AD[p.govde]} zemin, {O.AD[p.yazi]} yazı, {O.AD[p.vurgu]}{sus_} · "
            f"{O.YAZI_AD.get(d.yazi_tipi, d.yazi_tipi)}")


def renkler(d):
    return sorted({c for _, _, c in S.solids(d)})


def katilar(d):
    """Panel baskı yönünde: 9 × 12'de gövde, QR dolgusu ve kabartmalar; 10 × 20'de gövde ve yüzeyle aynı hizada
    dolgular."""
    return S.solids(d) if d.olcu == "9x12" else S.solids_20(d)


def sus_rengi(govde, vurgu, sus_):
    """Renk değişince süs (çiçeklerin taç yaprağı) gövdede kaybolmasın."""
    if sus_ and sus_ != govde and O.kontrast(govde, sus_) >= 1.15:
        return sus_
    return next(c for c in (WHITE, PUDRA, ROSE, ADACAYI, GUL, MOKA) if c not in (govde, vurgu) and
                O.kontrast(govde, c) >= 1.15)


def site_rengi(p):
    """Sayfanın vurgu rengi (web tonu): isimliğin renklerinden güzellik şablonuna yakışan; yoksa şablonunki."""
    for c in (p.vurgu, p.yazi, p.vurgu2):
        if c in (GUL, ROSE, FUSYA, MURDUM, MOKA, LILA, ADACAYI, NUDE):
            return O.WEB[c]
    return ""


def dilim_tasarimi(d):
    """Dilimleyici denetimi (boyde_isimlik_baski.slice_check) adsız dolguyu QR sayar: süs dolgularına ad verilir."""
    import copy
    d2 = copy.copy(d)
    d2.lines = dict(d.lines)
    adli = {id(v) for v in d.lines.values()}
    for i, (cs, _) in enumerate(d.inlay):
        if id(cs) not in d.qr_ids and id(cs) not in adli:
            d2.lines[f"süs {i + 1}"] = cs
    return d2
