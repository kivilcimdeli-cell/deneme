"""QR'lı masa isimliği 9 × 12: müşterinin bilgileriyle 10 düzen.

Yapı lastikçi isimlikleriyle aynı (scripts/uzar_isimlik_baski.py): panel 120 × 90 mm, gövde 1 cm, köşeler R8, yazı
ve şekiller 2 mm kabartma, QR yüzeyle aynı hizada dolgu, 15° eğik sehpa (alt 7,5 mm sehpanın yuvasında).
Düzenler boyde_sektor'deki örneklerden (telefoncu, berber, güzellik, kuaför, emlak, kuyumcu, optik, veteriner, spor)
ve BOYDE B07'den (QR solda) genelleştirildi: ad uzunsa küçülür ya da iki satıra bölünür, iş türü ve hizmetler yer
kaldıkça yazılır, simge sektöre göre ya da müşterinin logosu; genel sektörde simge yok (ad ve yazılar simgenin
yerine kayar; baş harf kullanılmaz).

Katalogda değişenler (öğrenmenin saydığı özellikler): düzen, zemin (siyah / beyaz), vurgu rengi, adın yazı tipi,
simge türü. Her tasarım baskıya uygunluk denetiminden geçer (ortak.olc); geçemeyen katalogda gösterilmez.

Simgesi olan her sektörde katalogun yarısı simgesiz (standart), yarısı simgeli (YARI_SIMGESIZ, 5 + 5). Lastik
sektörü: simge lastik izi (İnce Oto Lastik'in sitesindeki diş baskısı; jantın yerine) ve yalnız lastikte "Lastik izi"
düzeni (eğik, uçları solan diş bandı; SEKTOR_DUZENI).
"""
from dataclasses import dataclass, field

from . import ortak as O
from .ortak import A, BLACK, BLUE, GOLD, GRAY, GREEN, J, NAVY, ORANGE, PINK, PURPLE, RED, S, TURQ, YELLOW

X0, X1 = -54.0, 54.0
GUVENLI = O.I.outline().offset(-3.0, J) ^ A.rect(-70, 9.5, 70, 100)    # sehpa alt şeridi örter

# sektör: (ad, simge, çağrı, vurgu renkleri — ilki en uygun)
SEKTORLER = {
    "genel": ("Genel (simgesiz)", "yok", "HEMEN ARA", [ORANGE, RED, TURQ, GOLD, GREEN, BLUE]),
    "lastik": ("Oto lastik", "iz", "HEMEN ARA", [RED, YELLOW, ORANGE, BLUE]),
    "oto": ("Oto servis, yıkama, kaporta", "araba", "HEMEN ARA", [RED, YELLOW, GOLD, TURQ, BLUE]),
    "usta": ("Usta, tamir, teknik servis", "anahtar", "HEMEN ARA", [ORANGE, YELLOW, RED, BLUE]),
    "telefon": ("Telefoncu", "telefon", "HEMEN ARA", [TURQ, ORANGE, RED, BLUE]),
    "berber": ("Berber", "direk", "RANDEVU", [RED, GOLD, BLUE]),
    "kuafor": ("Kuaför", "makas", "RANDEVU", [PURPLE, PINK, GOLD, TURQ]),
    "guzellik": ("Güzellik, estetik", "hilal", "RANDEVU", [PINK, PURPLE, GOLD]),
    "emlak": ("Emlak", "ev", "HEMEN ARA", [BLUE, ORANGE, NAVY, RED, GREEN]),
    "kuyumcu": ("Kuyumcu", "pirlanta", "HEMEN ARA", [GOLD, GRAY]),
    "optik": ("Optik", "gozluk", "HEMEN ARA", [TURQ, BLUE, ORANGE, PURPLE]),
    "veteriner": ("Veteriner, pet shop", "pati", "RANDEVU", [GREEN, ORANGE, TURQ, PURPLE]),
    "spor": ("Spor salonu", "dambil", "HEMEN ARA", [ORANGE, RED, YELLOW, TURQ]),
    "kafe": ("Kafe, pastane", "fincan", "SİPARİŞ", [ORANGE, GOLD, RED, GREEN]),
    "saglik": ("Diş, sağlık", "dis", "RANDEVU", [TURQ, BLUE, GREEN]),
    "cicek": ("Çiçekçi, aktar", "yaprak", "SİPARİŞ", [GREEN, PINK, GOLD]),
}


@dataclass
class Icerik:
    marka: str                                   # büyük yazılan ad
    hizmet: str = ""                             # adın altındaki iş türü (OTO LASTİK, KUAFÖR...)
    hizmetler: list = field(default_factory=list)
    telefon: str = ""
    cagri: str = "HEMEN ARA"
    qr_yazi: str = "TARA"
    simge: str = "yok"                           # ortak.SIMGE anahtarı, "logo", "monogram" ya da "yok" (simgesiz)
    logo: object = None                          # CrossSection (logo.izle), simge "logo" iken
    url: str = "https://boyde.qrsistem.workers.dev/"


# ---------------------------------------------------------------- yardımcılar

UST = 86.5                                                   # simgenin üst sınırı (kenara 3,5 mm)
MIN_AD = {"bebas": 7.5, "oswald": 7.0, "anton": 8.0, "sairai": 9.0, "playfair": 9.0, "fraunces": 9.0}


def _koy(cs, y_ust):
    """Şeklin üstünü (noktalar dahil) y_ust'e taşır. Döner (şekil, alt kenarın y'si)."""
    b = cs.bounds()
    return cs.translate((0.0, y_ust - b[3])), y_ust - (b[3] - b[1])


def _simge(d, c, p, cx, cy, w, h, oyma=False, hiza="c", ust=None):
    """Simge (w × h) kutuya, ortası (cx, cy); hiza "l": sol kenarı cx'te. oyma: tek parça şekil döner (bant ya da
    bloktan oyulur); değilse eklenir, sınırı döner. Simgeler istenen boyda yeniden çizilir (çizgiler incelmez);
    kutudan uzun kalırsa üstü UST'u geçmeyecek kadar aşağı iner. Simge "yok"sa (genel) hiçbir şey eklenmez: oymada
    None, değilse simgenin üst sınırında sıfır boyutlu kutu döner (altına konan ad en üste çıkar)."""
    key = "makas" if c.simge == "direk" else c.simge           # direk uzun: yalnız şerit düzeninde
    if key == "yok":
        if oyma:
            return None
        t = (ust or UST) - 1.5
        return (cx, t, cx, t)
    if key == "logo" and c.logo is not None:
        parts = [(O.temizle(cs), r) for cs, r in O.olcekle([(c.logo, "vurgu")], 0.0, 0.0, w, h)]
    elif key in O.SIMGE:
        parts = O.simge_kur(key, w, h)
    else:
        s = min(w, h)
        if oyma:
            txt = O.oyma("mont", O.monogram_harfleri(c.marka), s * 0.62, 0.0, 0.0, "c", 0.6, w)
            b = txt.bounds()
            parts = [(txt.translate((-(b[0] + b[2]) / 2, -(b[1] + b[3]) / 2)), "vurgu")]
        else:
            parts, txt = O.monogram(O.monogram_harfleri(c.marka), 0.0, 0.0, s)
            d.lines["baş harfler"] = txt
    b = A.union(*[cs for cs, _ in parts]).bounds()
    dx = cx - b[0] if hiza == "l" else cx
    dy = min(cy, (ust or UST) - b[3])
    parts = [(cs.translate((dx, dy)), r) for cs, r in parts]
    if "baş harfler" in d.lines and not oyma:
        d.lines["baş harfler"] = d.lines["baş harfler"].translate((dx, dy))
    if oyma:
        return A.union(*[cs for cs, _ in parts])
    for cs, rol in parts:
        d.add(None, cs, p.renk(rol))
    return A.union(*[cs for cs, _ in parts]).bounds()


def simge_eni(c, w, h):
    """Simge kutuya konunca eni (eklemeden): düzen adın yerini buna göre seçer."""
    key = "makas" if c.simge == "direk" else c.simge
    if key == "yok":
        return 0.0
    if key == "logo" and c.logo is not None:
        b = c.logo.bounds()
        return min(w, h * (b[2] - b[0]) / (b[3] - b[1]))
    if key in O.SIMGE:
        b = A.union(*[cs for cs, _ in O.simge_kur(key, w, h)]).bounds()
        return b[2] - b[0]
    return min(w, h)


def ad_satirlari(marka, k, cap, max_w, tr=0.0, min_cap=None, iki=True, buyuk=None):
    """Adın satırları ve büyük harf boyu: tek satırda min_cap'in altına inen çok kelimeli ad iki satır."""
    s = O.ad_metni(marka, k, buyuk)
    c1 = O.sigan(k, s, cap, max_w, tr)
    words = s.split()
    if c1 >= (min_cap or cap * 0.62) or len(words) < 2 or not iki:
        return [s], c1
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        cc = min(O.sigan(k, a, cap, max_w, tr), O.sigan(k, b, cap, max_w, tr))
        if best is None or cc > best[1]:
            best = ([a, b], cc)
    return best if best[1] > c1 * 1.15 else ([s], c1)


def ad_yaz(d, c, p, k, x, y_ust, cap, max_w, align="l", tr=0.0, min_cap=None, cap2=None, renk=None, oyma=False,
           y_orta=None):
    """Ad: üstü (noktalar dahil) y_ust'te ya da ortası y_orta'da; bir ya da iki satır (iki satırda boy en çok cap2).
    Yazı tipinin harf içi daralmasın diye boy MIN_AD'ın altına inmez (taşarsa kontrol yakalar).
    Döner (şekil, alt kenarın y'si, boy)."""
    sik = getattr(c, "olcek", 1.0)                         # 10 × 20: yazılar sığmazsa ad küçülür
    cap, cap2 = cap * sik, cap2 and cap2 * sik
    lines, cc = ad_satirlari(c.marka, k, cap, max_w, tr, min_cap, buyuk=getattr(c, "buyuk", None))
    if len(lines) == 2:
        cc = min(cc, cap2 or cap * 0.72)
    d.ad_oran = min(1.0, cc * len(lines) / cap)              # adın düzendeki ideal boyuna oranı (kalite)
    if cc < (min_cap or cap * 0.62) * (0.85 if len(lines) == 2 else 1.0):
        d.zayif.append(f"ad küçük kaldı ({cc:.1f} mm)")
    fn = O.oyma if oyma else O.yazi
    shapes, y = [], 0.0
    for s in lines:
        cs, y = _koy(fn(k, s, cc, x, 0.0, align, tr, max_w, min_cap=MIN_AD.get(k, 5.5)), y)
        shapes.append(cs)
        y -= max(1.2, 0.2 * cc)
    cs = A.union(*shapes)
    b = cs.bounds()
    top = y_orta + (b[3] - b[1]) / 2 if y_orta is not None else y_ust
    cs = cs.translate((0.0, top - b[3]))
    if not oyma:
        d.add("ad", cs, renk if renk is not None else p.yazi)
    return cs, top - (b[3] - b[1]), cc


def satir(d, ad, s, x, y_ust, cap, max_w, align, tr, renk, k=O.SATIR):
    """Tek satır, üstü (noktalar dahil) y_ust'te; sığmazsa önce harf aralığı, sonra boy daralır (en az 4,4 mm).
    Döner alt kenarın y'si."""
    cc, tt = O.sigdir(k, s, cap, max_w, tr)
    cs, alt = _koy(O.yazi(k, s, cc, x, 0.0, align, tt, max_w, min_cap=O.MIN_BOY), y_ust)
    d.add(ad, cs, renk)
    return alt


def hizmetler(d, c, p, x, y_ust, max_w, align="l", cap=4.4, n_max=2, y_alt=None, renk=None, ara=1.8):
    """Hizmet maddeleri (araları yuvarlak nokta), satırlar arası `ara` mm; ilk satırın üstü y_ust, son satırın altı
    y_alt'ın altına inmez (düzenlerde y_alt, çağrının üstünden en az 2,6 mm yukarıda: satır arasından belirgin
    büyük, yazılar birbirine yapışık görünmesin). Sığmayan maddeler için uyarı. Döner son satırın alt kenarı."""
    if not c.hizmetler:
        d.gosterilen = 0
        return y_ust
    y, alt, shown = y_ust, y_ust, 0
    f = O.S.font(O.SATIR)                           # tek başına sığmayan madde varsa önce harf aralığı daralır
    tr = next((t for t in (0.8, 0.6, 0.5) if all(f.width(m, cap, t) * 1.03 <= max_w for m in c.hizmetler)), 0.8)
    for i, items in enumerate(O.maddeleri_diz(c.hizmetler, cap, max_w, n_max, tr=tr)):
        cs, a = _koy(O.madde_satiri(items, cap, x, 0.0, align, tr, max_w), y)
        if y_alt is not None and a < y_alt:
            break
        d.add(f"hizmet {i + 1}", cs, renk if renk is not None else p.yazi)
        shown += len(items)
        alt, y = a, a - ara
    d.gosterilen = shown
    if shown < len(c.hizmetler):
        d.uyarilar.append(f"hizmetlerin {shown}/{len(c.hizmetler)} tanesi sığdı")
    return alt


def _tek(d, ad, s, x, y, cap, align, max_w, tr, renk):
    """Yeri sabit tek satır (y büyük harflerin ortası): çağrı, telefon, QR yazısı."""
    cc, tt = O.sigdir(O.SATIR, s, cap, max_w, tr)
    d.add(ad, O.yazi(O.SATIR, s, cc, x, y, align, tt, max_w, min_cap=O.MIN_BOY), renk)


def cagri(d, c, p, x, y, cap=4.4, align="l", max_w=60.0, tr=1.2, renk=None):
    if c.cagri:
        _tek(d, "çağrı", O.tr_upper(c.cagri), x, y, cap, align, max_w, tr, renk if renk is not None else p.vurgu)


def telefon(d, c, p, x, y, cap=5.2, align="l", max_w=60.0, renk=None):
    if c.telefon:
        _tek(d, "telefon", c.telefon, x, y, cap, align, max_w, 0.5, renk if renk is not None else p.yazi)


def qr(d, c, p, cx, cy, s, cerceve=False, yazi=None, cap=4.4, tr=1.8):
    """QR yüzeyle aynı hizada (siyah gövdede beyaz karo, beyaz gövdede siyah kareler); altında yazı (TARA). Yazının
    üstü (İ'nin noktası dahil) karonun ya da çerçevenin 2,8 mm altında."""
    e = O.qr_girdi(c.url, p.koyu)
    tile = d.qr(e, cx, cy, s, sq=BLACK)
    d.qr_entry, d.qr_side = e, s
    alt = tile.bounds()[1]
    if cerceve:
        g, w = 1.8, 1.2
        ring = A.rrect(s + 2 * (g + w), s + 2 * (g + w), 2.8, cx, cy) - A.rrect(s + 2 * g, s + 2 * g, 2.0, cx, cy)
        d.add("çerçeve", ring, p.vurgu)
        alt = ring.bounds()[1]
    yazi = c.qr_yazi if yazi is None else yazi
    if yazi:
        s_ = O.tr_upper(yazi)
        cc, tt = O.sigdir(O.SATIR, s_, cap, s + 2.0, tr)
        cs, _ = _koy(O.yazi(O.SATIR, s_, cc, cx, 0.0, "c", tt, s + 2.0, min_cap=O.MIN_BOY), alt - 2.8)
        d.add("alt yazı", cs, p.vurgu)
    return tile


# ---------------------------------------------------------------- düzenler (x −54..54, y ~12..86)

def l_yan_yana(d, c, p, k):
    """Simge solda üstte, yanında ad ve iş türü; çizgi, hizmetler, çağrı ve telefon; QR sağda (telefoncu). Ad
    simgenin yanına sığmazsa simge küçülür, iş türü yanına, ad altına boydan yazılır."""
    x = X0 + simge_eni(c, 18.0, 21.0) + 4.5
    if c.simge == "yok":                                    # simgesiz: ad sol üstte, boydan
        _, y, _ = ad_yaz(d, c, p, k, X0, 82.0, 12.5, 65.0, min_cap=6.5, cap2=9.0)
        if c.hizmet:
            y = is_turu(d, c.hizmet, X0, y - 3.0, 5.0, 65.0, "l", 1.6, p.vurgu)
    elif ad_satirlari(c.marka, k, 11.0, 11.0 - x, 0.0, 6.5)[1] >= 6.5:
        ib = _simge(d, c, p, X0, 71.0, 18.0, 21.0, hiza="l")
        _, y, _ = ad_yaz(d, c, p, k, x, 81.5, 11.0, 11.0 - x, min_cap=6.5, cap2=8.0)
        if c.hizmet:
            y = is_turu(d, c.hizmet, x, y - 3.0, 5.0, 11.0 - x, "l", 1.6, p.vurgu)
        y = min(y, ib[1])
    else:
        ib = _simge(d, c, p, X0, 79.5, 16.0, 13.0, hiza="l")
        x = ib[2] + 4.0
        if c.hizmet:
            is_turu(d, c.hizmet, x, (ib[1] + ib[3]) / 2 + 2.6, 5.0, 11.0 - x, "l", 1.6, p.vurgu)
        _, y, _ = ad_yaz(d, c, p, k, X0, ib[1] - 3.4, 11.0, 65.0, min_cap=6.5, cap2=8.0)
    y -= 3.6
    d.add(None, O.bar(X0, -26.0, y - 0.8, 1.6), p.vurgu)
    hizmetler(d, c, p, X0, y - 1.6 - 3.2, 62.0, y_alt=31.2)
    cagri(d, c, p, X0, 26.0)
    telefon(d, c, p, X0, 17.0, 5.4)
    qr(d, c, p, 34.0, 48.0, 38.0)


def l_serit(d, c, p, k):
    """Solda boydan şerit (berberde direk), dar ve büyük ad, iş türü harf aralıklı; QR sağda (berber)."""
    if c.simge == "direk":
        for cs, rol in O.olcekle(O.SIMGE["direk"](62.0), -47.0, 49.0, 14.0, 62.0):
            d.add(None, cs, p.renk(rol))
        x = -36.0
    else:
        d.add(None, A.rrect(4.0, 66.0, 2.0, -52.0, 49.0), p.vurgu)
        x = -45.0
    w = 12.0 - x
    _, y, _ = ad_yaz(d, c, p, k, x, 82.0, 19.0, w, min_cap=10.0, cap2=13.0)
    if c.hizmet:
        y = is_turu(d, c.hizmet, x, y - 3.6, 5.2, w, "l", 2.6, p.vurgu)
    hizmetler(d, c, p, x, y - 3.4, w, y_alt=33.8)
    cagri(d, c, p, x, 29.0, max_w=w, tr=1.4)
    telefon(d, c, p, x, 20.0, 4.8, max_w=w)
    qr(d, c, p, 34.0, 50.0, 36.0)


def l_ortali(d, c, p, k):
    """Solda ortalı sütun: simge, ad, iş türü, kısa çizgi, hizmetler, telefon; QR sağda, altında çağrı (güzellik)."""
    cx, w = -24.0, 58.0
    ib = _simge(d, c, p, cx, 78.5, 22.0, 13.0)
    _, y, _ = ad_yaz(d, c, p, k, cx, ib[1] - 3.0, 14.0, w, "c", 0.2, min_cap=8.0, cap2=9.5)
    if c.hizmet:
        y = is_turu(d, c.hizmet, cx, y - 3.2, 4.6, w, "c", 1.0, p.vurgu)
    d.add(None, O.bar(cx - 6.0, cx + 6.0, y - 3.0, 1.3), p.vurgu)
    hizmetler(d, c, p, cx, y - 3.65 - 3.0, w, "c", y_alt=24.0)
    telefon(d, c, p, cx, 19.0, 5.0, "c", max_w=w)
    qr(d, c, p, 33.0, 50.0, 36.0, yazi=c.cagri or c.qr_yazi, tr=1.4)


def l_zarif(d, c, p, k):
    """Simge ve zarif ad yan yana, iş türü geniş aralıklı; QR renkli çerçeveli (kuaför). Ad yanına sığmazsa simge
    küçülüp üste, ad altına boydan."""
    x = X0 + simge_eni(c, 14.0, 20.0) + 4.0
    if c.simge == "yok":                                    # simgesiz: ad sol üstte, boydan
        _, y, _ = ad_yaz(d, c, p, k, X0, 82.0, 15.0, 63.0, "l", 0.3, min_cap=9.0, cap2=10.0)
        y -= 3.4
    elif ad_satirlari(c.marka, k, 15.0, 9.0 - x, 0.3, 9.0)[1] >= 9.0:
        ib = _simge(d, c, p, X0, 72.0, 14.0, 20.0, hiza="l")
        _, y, _ = ad_yaz(d, c, p, k, x, 81.0, 15.0, 9.0 - x, "l", 0.3, min_cap=9.0, cap2=10.0)
        y = min(y, ib[1]) - 3.6
    else:
        ib = _simge(d, c, p, X0, 80.0, 20.0, 12.0, hiza="l")
        _, y, _ = ad_yaz(d, c, p, k, X0, ib[1] - 3.2, 15.0, 63.0, "l", 0.3, min_cap=9.0, cap2=10.0)
        y -= 3.4
    if c.hizmet:
        y = is_turu(d, c.hizmet, X0, y, 5.2, 62.0, "l", 3.2, p.vurgu) - 3.4
    hizmetler(d, c, p, X0, y, 62.0, y_alt=31.8)
    cagri(d, c, p, X0, 27.0, tr=1.4)
    telefon(d, c, p, X0, 18.4, 5.2)
    qr(d, c, p, 34.0, 49.0, 36.0, cerceve=True, tr=1.6)


def l_bant(d, c, p, k):
    """Üstte boydan renkli bant: içinden oyma simge ve ad (gövde rengi görünür); altında iş türü, hizmetler,
    çağrı, telefon; QR sağ altta (emlak)."""
    band = A.rrect(112.0, 24.0, 4.0, 0.0, 73.0)
    icon = _simge(d, c, p, -50.0, 73.0, 16.0, 15.0, oyma=True, hiza="l")
    x = icon.bounds()[2] + 4.0 if icon is not None else -50.0
    txt, _, _ = ad_yaz(d, c, p, k, x, 0.0, 9.0, 52.0 - x, "l", 0.6, min_cap=5.5, cap2=6.6, oyma=True, y_orta=73.0)
    d.lines["bant yazısı"] = txt
    d.add(None, band - A.union(*[cs for cs in (icon, txt) if cs is not None]).offset(0.0, J), p.vurgu)
    y = 57.6
    if c.hizmet:
        y = is_turu(d, c.hizmet, X0, y, 4.6, 66.0, "l", 0.8, p.vurgu) - 3.0
    hizmetler(d, c, p, X0, y, 66.0, y_alt=34.4)
    cagri(d, c, p, X0, 29.6)
    telefon(d, c, p, X0, 20.4, 5.4)
    qr(d, c, p, 36.0, 40.0, 34.0, tr=1.4)


def l_baslik(d, c, p, k):
    """Ortalı başlık: simge, geniş aralıklı ad, iki yanında çizgiler arasında iş türü; altta solda hizmetler,
    çağrı ve telefon, sağda QR (kuyumcu)."""
    ib = _simge(d, c, p, 0.0, 80.5, 22.0, 11.0)
    _, y, _ = ad_yaz(d, c, p, k, 0.0, ib[1] - 3.0, 12.0, 96.0, "c", 2.4, min_cap=7.0, cap2=8.0)
    if c.hizmet:
        cc, tt = O.sigdir(O.SATIR, c.hizmet, 4.4, 76.0, 2.4)
        sub, alt = _koy(O.yazi(O.SATIR, c.hizmet, cc, 0.0, 0.0, "c", tt, 76.0, min_cap=O.MIN_BOY), y - 3.4)
        d.add("iş türü", sub, p.vurgu)
        b = sub.bounds()
        hw, yc = (b[2] - b[0]) / 2, alt + cc / 2
        x_end = 50.0 if alt > 49.5 else 14.0                # QR'ın üstünde değilse çizgiler QR'a uzanmasın
        if x_end - hw - 4.0 >= 6.0:
            d.add(None, O.bar(-x_end, -hw - 4.0, yc, 1.3) + O.bar(hw + 4.0, x_end, yc, 1.3), p.vurgu)
        y = alt
    hizmetler(d, c, p, X0, min(y - 4.0, 45.0), 64.0, y_alt=33.8)
    cagri(d, c, p, X0, 29.0)
    telefon(d, c, p, X0, 20.0, 5.2, max_w=62.0)
    qr(d, c, p, 36.0, 29.5, 34.0, yazi="")


def l_cerceve(d, c, p, k):
    """Simge üstte solda, büyük ad, iş türü harf aralıklı; QR renkli çerçeveli, altında yazı (optik)."""
    ib = _simge(d, c, p, X0, 78.5, 28.0, 13.0, hiza="l")
    _, y, _ = ad_yaz(d, c, p, k, X0, ib[1] - 3.0, 17.0, 60.0, "l", 0.4, min_cap=9.0, cap2=10.5)
    if c.hizmet:
        y = is_turu(d, c.hizmet, X0, y - 3.4, 6.0, 60.0, "l", 2.6, p.vurgu)
    hizmetler(d, c, p, X0, y - 3.4, 62.0, y_alt=24.8)
    telefon(d, c, p, X0, 19.5, 5.2)
    qr(d, c, p, 33.0, 50.0, 34.0, cerceve=True, tr=1.6)


def _blok_is_turu(s):
    """Renk bloktaki iş türü: sığarsa tek satır, sığmazsa kelimelerden en iyi ikiye bölünüş (eskiden maddeleri_diz
    kelimeleri madde gibi dizip ikinci satıra sığmayanı düşürüyordu: OTO BAKIM SERVİSİ → OTO / BAKIM)."""
    cc, tt = O.sigdir(O.SATIR, s, 4.4, 40.0, 0.8)
    if len(s.split()) < 2 or O.genislik(O.SATIR, s, cc, tt) <= 40.0:
        return [s]
    return list(_iki_satir(s, 4.4, 40.0, 0.8))


def l_blok(d, c, p, k):
    """Solda renkli blok: içinden oyma simge, ad ve iş türü; sağda çağrı, QR ve telefon (veteriner)."""
    cx = -30.0
    block = A.rrect(48.0, 74.0, 5.0, cx, 49.0)
    icon = _simge(d, c, p, cx, 75.5, 22.0, 15.0, oyma=True)
    yok = icon is None                               # simgesiz: ad büyür, yazılar blokta ortalanır
    ust = icon.bounds()[1] - 3.4 if not yok else 80.0
    txt, y, _ = ad_yaz(d, c, p, k, cx, ust, 14.0 if yok else 12.5, 40.0, "c", 0.5, min_cap=7.0, cap2=9.5,
                       oyma=True)
    cuts = [txt]
    if c.hizmet:                                     # iş türü en çok iki satır (VETERİNER / KLİNİĞİ)
        for r in _blok_is_turu(c.hizmet):               # kelime düşmez (OTO BAKIM / SERVİSİ)
            cs, y = _koy(O.oyma(O.SATIR, r, 4.4, cx, 0.0, "c", 0.8, 40.0, min_cap=O.MIN_BOY), y - 3.0)
            cuts.append(cs)
    if c.hizmetler and y > 27.0:
        cs, _ = _koy(O.oyma(O.SATIR, O.tr_upper(c.hizmetler[0]), 4.4, cx, 0.0, "c", 0.8, 40.0, min_cap=O.MIN_BOY),
                     y - 6.0 if yok else 22.0)
        if cs.bounds()[2] - cs.bounds()[0] <= 41.0:          # sığmayan madde bloktan taşmasın
            cuts.append(cs)
    if yok:                                          # yazı öbeği bloğun ortasında
        b = A.union(*cuts).bounds()
        dy = 49.0 - (b[1] + b[3]) / 2
        cuts = [cs.translate((0.0, dy)) for cs in cuts]
    d.gosterilen = len(cuts) - 1 - (len(_blok_is_turu(c.hizmet)) if c.hizmet else 0)
    d.lines["blok yazısı"] = A.union(*cuts)
    d.add(None, block - A.union(*[cs for cs in [icon] + cuts if cs is not None]).offset(0.0, J), p.vurgu)
    cagri(d, c, p, 30.0, 80.0, align="c", max_w=44.0, tr=1.4)
    qr(d, c, p, 30.0, 55.0, 38.0, yazi="")
    telefon(d, c, p, 30.0, 23.0, 4.8, "c", max_w=47.0)


def l_egik(d, c, p, k):
    """Eğik, dar ve büyük ad; simge üstte solda; QR sağda (spor)."""
    ib = _simge(d, c, p, X0, 80.0, 26.0, 11.0, hiza="l")
    _, y, _ = ad_yaz(d, c, p, k, X0, ib[1] - 3.0, 17.0, 64.0, "l", 0.3, min_cap=9.0, cap2=11.0)
    if c.hizmet:
        y = is_turu(d, c.hizmet, X0, y - 3.4, 4.6, 62.0, "l", 1.6, p.vurgu)
    hizmetler(d, c, p, X0, y - 3.2, 62.0, y_alt=32.8)
    cagri(d, c, p, X0, 28.0)
    telefon(d, c, p, X0, 19.0, 5.2)
    qr(d, c, p, 35.0, 50.0, 36.0)


def l_qr_solda(d, c, p, k):
    """QR solda, altında yazı; sağda ortalı sütun: simge, ad, iş türü, hizmetler, çağrı, telefon (B07)."""
    qr(d, c, p, -33.0, 48.0, 38.0)
    cx, w = 27.0, 52.0
    ib = _simge(d, c, p, cx, 79.0, 24.0, 14.0)
    _, y, _ = ad_yaz(d, c, p, k, cx, ib[1] - 3.0, 9.0, w, "c", 0.3, min_cap=6.0, cap2=7.0)
    if c.hizmet:
        y = is_turu(d, c.hizmet, cx, y - 3.0, 4.6, w, "c", 1.2, p.vurgu)
    hizmetler(d, c, p, cx, y - 3.4, w, "c", n_max=3, y_alt=29.8)
    cagri(d, c, p, cx, 25.0, align="c", max_w=w)
    telefon(d, c, p, cx, 16.5, 4.8, "c", max_w=w)


def lastik_izi(d, p, cx, w, y_ust, y_alt, rol="yazi"):
    """İnce Oto Lastik'in sitesindeki eğik lastik izi bandı (ortak.iz_bant): y_ust (üstteki yazının alt kenarı) ile
    y_alt (alttaki yazının üst kenarı) arasında, sütunun (cx, w) ortasında. Bant 12° eğik, uçları soluk (dişler
    küçülür); yazılara 2 mm'den, QR'a 3 mm'den yakın ya da güvenli alanın dışına düşen diş konmaz. Döner konan öğe
    sayısı; sığmazsa 0 (hiçbir şey eklenmez)."""
    boy = min(18.0, (y_ust - y_alt) - 12.0)
    if boy < 11.0:
        return 0
    engel = A.union(*[cs for cs, _ in d.raised]).offset(2.0, J)
    if "QR" in d.lines:
        engel = engel + d.lines["QR"].offset(3.0, J)
    ogeler = [cs for cs, _, _ in O.iz_bant(cx, (y_ust + y_alt) / 2, boy, cx - w / 2 - 19.0, cx + w / 2 + 17.0,
                                         min_cizgi=1.35)   # soluk dişler de 1,2 mm denetiminden geçsin
              if (cs - GUVENLI).area() < 0.01 and (cs ^ engel).area() < 0.01]
    if len(ogeler) < 9:
        return 0
    d.add(None, A.union(*ogeler), p.renk(rol))
    return len(ogeler)


def is_turu_satirlari(s, cap, w, tr):
    """İş türü bir ya da iki satır: tek satırda boy %90'ın altına inecekse kelimelerden en iyi ikiye bölünüş (iki
    satırın küçüğü en büyük olan; OTO LASTİK / TAMİRİ)."""
    if len(s.split()) < 2 or O.sigdir(O.SATIR, s, cap, w, tr)[0] >= cap * 0.9:
        return [s]
    return list(_iki_satir(s, cap, w, tr))


def _iki_satir(s, cap, w, tr):
    """Kelimelerden ikiye bölünüş: iki satırın küçük boyu en büyük olan; eşitse satır uzunlukları dengeli olan
    (OTO LASTİK / TAMİRİ, OTO / LASTİK TAMİRİ değil)."""
    kel = s.split()
    bolus = [(" ".join(kel[:i]), " ".join(kel[i:])) for i in range(1, len(kel))]
    return max(bolus, key=lambda ab: (round(min(O.sigdir(O.SATIR, t, cap, w, tr)[0] for t in ab), 1),
                                      -abs(len(ab[0]) - len(ab[1]))))


def is_turu(d, s, x, y_ust, cap, max_w, align, tr, renk, ara=1.4):
    """İş türü satırı (satir gibi). En küçük boyda da tek satıra sığmayan çok kelimeli iş türü iki satır olur
    (OTO LASTİK TAMİRİ → OTO LASTİK / TAMİRİ; eskiden kenara ya da QR'a taşıp tasarım elenirdi). Döner son satırın
    alt kenarı."""
    cc, tt = O.sigdir(O.SATIR, s, cap, max_w, tr)
    if len(s.split()) < 2 or O.genislik(O.SATIR, s, cc, tt) <= max_w * 1.01:
        return satir(d, "iş türü", s, x, y_ust, cap, max_w, align, tr, renk)
    a, b = _iki_satir(s, cap, max_w, tr)
    y = satir(d, "iş türü", a, x, y_ust, cap, max_w, align, tr, renk)
    return satir(d, "iş türü 2", b, x, y - ara, cap, max_w, align, tr, renk)


def l_lastik_izi(d, c, p, k):
    """QR solda; sağda ortalı sütun: ad, iş türü (en çok iki satır), araya İnce Oto Lastik'in sitesindeki eğik lastik
    izi bandı, altta çağrı ve telefon (lastikçi, Antalya 7/24 Oto Lastik Tamiri'nin isimliğinden). Simgesiz: bant
    simgenin yerini tutar; hizmetler yazılmaz (yerinde bant)."""
    qr(d, c, p, -33.0, 48.0, 38.0)
    cx, w = 27.0, 52.0
    _, y, _ = ad_yaz(d, c, p, k, cx, 84.5, 9.5, w, "c", 0.3, min_cap=6.0, cap2=7.0)
    if c.hizmet:
        for i, r in enumerate(is_turu_satirlari(c.hizmet, 5.2, w, 1.2)):
            y = satir(d, "iş türü" if i == 0 else "iş türü 2", r, cx, y - (2.6 if i == 0 else 1.4), 5.2, w, "c", 1.2,
                      p.vurgu)
    cagri(d, c, p, cx, 22.5, align="c", max_w=w, tr=1.6)          # çağrı ve telefon aşağıda: bant için yer
    telefon(d, c, p, cx, 14.2, 5.0, "c", max_w=w)
    alt = max((d.lines[n].bounds()[3] for n in ("çağrı", "telefon") if n in d.lines), default=12.0)
    if not lastik_izi(d, p, cx, w, y, alt):
        d.zayif.append("lastik izi sığmadı")
        d.ad_oran *= 0.5
    d.gosterilen = len(c.hizmetler)                        # hizmetlerin yerinde bant (bilerek yazılmaz)


# anahtar: (ad, kurucu, adın yazı tipleri — ilki en uygun)
DUZENLER = {
    "yan_yana": ("Yan yana", l_yan_yana, ["outfit", "sora", "lexend", "oswald"]),
    "serit": ("Dikey şerit", l_serit, ["bebas", "oswald", "anton"]),
    "ortali": ("Ortalı", l_ortali, ["lora", "playfair", "outfit"]),
    "zarif": ("Zarif", l_zarif, ["playfair", "lora", "fraunces"]),
    "bant": ("Üst bant", l_bant, ["mont", "lexend", "archivo"]),
    "baslik": ("Başlık", l_baslik, ["cinzel", "mont", "lora"]),
    "cerceve": ("Çerçeveli QR", l_cerceve, ["sora", "outfit", "unbounded", "oswald"]),
    "blok": ("Renk blok", l_blok, ["righteous", "outfit", "bebas"]),
    "egik": ("Eğik", l_egik, ["sairai", "poppins_i"]),
    "qr_solda": ("QR solda", l_qr_solda, ["outfit", "manrope", "lexend", "oswald"]),
    "lastik_izi": ("Lastik izi", l_lastik_izi, ["sairai", "outfit", "oswald"]),
}
# yalnız bazı sektörlerde gösterilen düzenler (öbürleri her sektörde)
SEKTOR_DUZENI = {"lastik_izi": {"lastik"}}
# katalogun yarısı simgesiz (standart), yarısı sektör simgeli olan sektörler: lastikte hepsi simgeli çıkıyordu
# (önce yalnız lastik; kullanıcı: "diğer sektörlere de ekle": simgesi olan her sektör)
YARI_SIMGESIZ = {k for k, v in SEKTORLER.items() if v[1] != "yok"}
SIMGESIZ_DUZEN = {"lastik_izi", "serit"}               # simge çizmeyen düzenler: yalnız simgesiz sayılır
ONE_CIKAN = {"lastik": "lastik_izi"}                   # sektörün katalogunda (gösterilmediyse) hep bulunan düzen


def duzenler(sektor):
    """Sektörde kullanılan düzenler: {anahtar: (ad, kurucu, yazı tipleri)}."""
    return {k: v for k, v in DUZENLER.items() if k not in SEKTOR_DUZENI or sektor in SEKTOR_DUZENI[k]}


def simge_secenekleri(sektor, c, duzen):
    """Düzenin katalogdaki simge seçenekleri: [""] (içeriğin simgesi) ya da yarı simgesiz sektörde ["", "yok"]
    (simge çizmeyen düzende yalnız ["yok"]). Logo ya da simgesiz içerikte hep [""]."""
    if sektor not in YARI_SIMGESIZ or c.simge in ("logo", "monogram", "yok"):
        return [""]
    if duzen == "serit" and c.simge == "direk":          # berberde şerit düzeni direği çizer: simgeli de olur
        return ["", "yok"]
    return ["yok"] if duzen in SIMGESIZ_DUZEN else ["", "yok"]


# ---------------------------------------------------------------- tasarım, kontrol, katılar, görünüş

def tasarla(duzen, c, palet, yazi_tipi):
    """Döner boyde_sektor.Design; ek alanlar: duzen, palet, yazi_tipi, qr_entry, qr_side, uyarilar."""
    d = S.Design(duzen, palet.sc)
    d.duzen, d.palet, d.yazi_tipi, d.uyarilar, d.zayif = duzen, palet, yazi_tipi, [], []
    d.ad_oran, d.gosterilen = 1.0, len(c.hizmetler)
    d.qr_entry = d.qr_side = None
    DUZENLER[duzen][1](d, c, palet, yazi_tipi)
    return d


def kalite(d, c):
    """0..1: adın düzendeki ideal boyuna oranı (ağırlık 0,65) ve hizmetlerin sığan oranı (0,35)."""
    h = d.gosterilen / len(c.hizmetler) if c.hizmetler else 1.0
    return 0.65 * d.ad_oran + 0.35 * h


def ozellikler(d, c):
    return {"sablon": d.duzen, "zemin": O.AD[d.palet.govde], "renk": O.AD[d.palet.vurgu], "yazi": d.yazi_tipi,
            "simge": c.simge if c.simge in ("logo", "monogram", "yok") else "simge"}


def ad(d):
    p = d.palet
    return f"{DUZENLER[d.duzen][0]} · {O.AD[p.govde]} zemin, {O.AD[p.yazi]} yazı, {O.AD[p.vurgu]} · {O.YAZI_AD[d.yazi_tipi]}"


def kontrol(d):
    """Baskıya uygunluk: (sorunlar, ölçüler)."""
    return O.olc(d, GUVENLI)


def katilar(d):
    """Panel baskı yönünde (yüzü yukarı): gövde, dolgular, kabartmalar (boyde_sektor.solids)."""
    return S.solids(d)


def renkler(d):
    return sorted({c for _, _, c in katilar(d)} | {BLACK})


def gorunus(parcalar, boy=900, aci=(0, -90), duz=0.85):
    """Sehpasında, önden (varsayılan) ya da açıyla: RGBA görüntü."""
    from cift_tarafli_isimlik import render, rotation
    stand, (z0, y0) = O.B.stand()
    shown = O.B.assembled(parcalar, z0, y0) + [("Sehpa", stand, BLACK)]
    mesh = [(*A.mesh_arrays(m), O.TON[c]) for _, m, c in shown]
    return render(mesh, boy, rotation(*aci), flat=duz, margin=0.02)
