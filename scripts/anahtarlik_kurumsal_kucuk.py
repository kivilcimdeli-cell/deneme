"""AUTO FIRAT TUYGUN kurumsal anahtarlıklar, KÜÇÜK boy (~45-50 mm): seçilen 6 tasarım (1, 2, 3, 6, 7, 9).

Büyük dosyaları Bambu Studio'da küçültmek yazıları bulanıklaştırıyor: harf çizgileri 0,4 nozulun basabileceğinden
(~0,5-0,6 mm) inceliyor, A/O/8 gibi harflerin içi kapanıyor. Bu yüzden küçük boy yeniden çizildi (ölçeklenmedi):
  * bütün yazılar Outfit ExtraBold, en az 3,0 mm (ANTALYA 2,8 mm): çizgiler ~0,6 mm ve üstü
  * hiçbir yazı çıkarılmadı; dar tasarımlarda isim ve telefon iki satır
  * baskı yapısı büyük boyla aynı (scripts/anahtarlik_kurumsal.py): ön yüz 0,8 mm kabartma, arka yazılar ilk 3 katmanda
    tek renk gömme, 3 renkli dosyalarda tek filament değişimi

Çıktı : anahtarlik/kurumsal_baski/kucuk/<tasarım>.3mf, anahtarlik/kurumsal_baski/kucuk/onizleme/*.png

Kullanım:
  python3 scripts/anahtarlik_kurumsal_kucuk.py            # hepsi
  python3 scripts/anahtarlik_kurumsal_kucuk.py kapsul     # yalnız adında "kapsul" geçen
"""
import os
import sys
import zipfile

import manifold3d as m3
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import anahtarlik_konsept as K  # noqa: E402
import anahtarlik_kurumsal as P  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "anahtarlik", "kurumsal_baski", "kucuk")
NAME, PHONE, CITY = A.NAME, A.PHONE, A.CITY
PHONE_1, PHONE_2 = "0535 278", "35 29"
BLACK, WHITE, GOLD = K.BLACK, K.WHITE, K.GOLD
HOLE_R = 2.2                     # anahtarlık deliği Ø4,4 mm
J = m3.JoinType.Round


def ob():
    return K.outfit()


def name(cap, x, y, align="c", text=NAME):
    return ob().text(text, cap, x, y, align=align, tracking=cap * 0.1)


def phone(cap, x, y, align="c", text=PHONE):
    return ob().text(text, cap, x, y, align=align, tracking=0.3)


def city(cap, x, y, align="c"):
    return ob().text(CITY, cap, x, y, align=align, tracking=cap * 0.3)


def concept(key, title, desc, outline, holes, body=BLACK):
    return K.Concept(key, title, desc, outline, holes, body)


# ---------------------------------------------------------------- tasarımlar

def s1_kapsul():
    W, H = 58.0, 16.0
    c = concept("1_kapsul", "Kapsül", "Hap biçimi; altın FT, altın AUTO, beyaz isim.",
                A.rrect(W, H, H / 2), A.circle(HOLE_R, -W / 2 + 5.8, 0))
    x = -W / 2 + 21.0
    c.front += [(K.ft_mark(7.6, -W / 2 + 14.2, 0), GOLD),
                (K.auto_word(3.4, x + 0.1, 2.6), GOLD),
                (name(3.0, x, -2.8, align="l"), WHITE)]
    c.back += [(phone(3.2, -3.4, 2.4), WHITE), (city(2.8, -3.4, -3.0), GOLD)]
    return c


def s2_logo_kare():
    S = 34.0
    c = concept("2_logo_kare", "Logo kare", "Yuvarlak kare; büyük altın FT, altında beyaz AUTO.",
                A.rrect(S, S, 9.0), A.circle(HOLE_R, -S / 2 + 6.6, S / 2 - 6.6))
    c.front += [(K.ft_mark(13.0, 1.0, 3.2), GOLD), (K.auto_word(3.6, 0, -9.6, align="c"), WHITE)]
    c.back += [(name(3.0, 0, 10.8, text="FIRAT"), WHITE), (name(3.0, 0, 6.4, text="TUYGUN"), WHITE),
               (A.rect(-6.0, 2.7, 6.0, 3.5), GOLD),
               (phone(3.0, 0, -1.0, text=PHONE_1), WHITE), (phone(3.0, 0, -5.4, text=PHONE_2), WHITE),
               (city(2.8, 0, -10.2), GOLD)]
    return c


def s3_madalyon():
    R = 17.0
    outline = (A.circle(R, 0, 0, 160) + A.circle(5.4, 0, R + 2.0)).offset(1.2, J).offset(-1.2, J)
    c = concept("3_madalyon", "Madalyon", "Beyaz yuvarlak; ince siyah halka içinde siyah FT ve AUTO.",
                outline, A.circle(HOLE_R, 0, R + 1.9), body=WHITE)
    c.front += [(A.outline(A.circle(R, 0, 0, 160), 0.9, inset=1.7), BLACK), (K.ft_mark(10.5, 0.5, 2.6), BLACK),
                (K.auto_word(3.2, 0, -7.4, align="c"), BLACK)]
    c.back += [(name(3.0, 0, 9.0, text="FIRAT"), BLACK), (name(3.0, 0, 4.6, text="TUYGUN"), BLACK),
               (phone(3.0, 0, -0.2, text=PHONE_1), BLACK), (phone(3.0, 0, -4.6, text=PHONE_2), BLACK),
               (city(2.8, 0, -9.2), BLACK)]
    return c


def s6_tek_cizgi():
    W, H = 52.0, 20.0
    c = concept("6_tek_cizgi", "Tek çizgi", "Beyaz isim; altın çizgi sağda AUTO rozetinde biter.",
                A.rrect(W, H, 3.5), A.circle(HOLE_R, W / 2 - 5.3, H / 2 - 5.3))
    badge = K.auto_badge(3.2, W / 2 - 4.0, -4.6, align="r")
    bx0 = badge.bounds()[0]
    c.front += [(name(3.2, -W / 2 + 4.0, 3.6, align="l"), WHITE),
                (A.rect(-W / 2 + 4.0, -5.1, bx0 + 1.0, -4.1) + badge, GOLD)]
    # arkadan bakınca delik sol üstte: yazılar sağa yaslı
    c.back += [(phone(3.2, W / 2 - 4.0, 2.2, align="r"), WHITE), (city(2.8, W / 2 - 4.0, -3.6, align="r"), GOLD)]
    return c


def s7_altigen():
    R = 20.0
    hexa = A.polygon([(R * np.cos(np.radians(90 + 60 * i)), R * np.sin(np.radians(90 + 60 * i))) for i in range(6)])
    outline = hexa.offset(-2.2, J).offset(2.2, J)
    c = concept("7_altigen", "Altıgen", "Sivri tepeli altıgen; altın FT, beyaz AUTO, tepede delik.",
                outline, A.circle(HOLE_R, 0, R - 6.3))
    c.front += [(K.ft_mark(11.0, 0.5, 1.4), GOLD), (K.auto_word(3.4, 0, -8.6, align="c"), WHITE)]
    c.back += [(name(3.0, 0, 7.6, text="FIRAT"), WHITE), (name(3.0, 0, 3.2, text="TUYGUN"), WHITE),
               (phone(3.0, 0, -1.6, text=PHONE_1), WHITE), (phone(3.0, 0, -6.0, text=PHONE_2), WHITE),
               (city(2.8, 0, -10.4), GOLD)]
    return c


def s9_kose_serit():
    W, H = 50.0, 30.0
    card = A.rrect(W, H, 4.5)
    lo, hi = W / 2 + H / 2 - 11.5, W / 2 + H / 2 - 5.5     # şerit sağ üst köşede: lo ≤ x + y ≤ hi
    band = A.polygon([(lo + 30, -30), (hi + 30, -30), (-30, hi + 30), (-30, lo + 30)])
    c = concept("9_kose_serit", "Köşe şerit", "Kart; sağ üst köşede çapraz altın şerit, büyük altın AUTO, beyaz isim.",
                card, A.circle(HOLE_R, -W / 2 + 5.5, H / 2 - 5.5))
    c.front += [(band ^ card, GOLD),
                (K.auto_word(4.0, -W / 2 + 4.6, -1.6), GOLD),
                (name(3.0, -W / 2 + 4.5, -7.4, align="l"), WHITE)]
    c.back += [(phone(3.2, -W / 2 + 4.5, -2.6, align="l"), WHITE), (city(2.8, -W / 2 + 4.5, -8.0, align="l"), GOLD)]
    return c


SMALL = [s1_kapsul, s2_logo_kare, s3_madalyon, s6_tek_cizgi, s7_altigen, s9_kose_serit]


# ---------------------------------------------------------------- kontrol

def thin_and_gaps(cs, w, g):
    """`w`'den ince çizgi oranı (%) ve `g`'den dar boşluk alanı (mm²)."""
    if cs.is_empty():
        return 0.0, 0.0
    thin = cs - cs.offset(-w / 2, J).offset(w / 2, J)
    gap = cs.offset(g / 2, J).offset(-g / 2, J) - cs
    s = lambda x: sum(p.area() for p in x.decompose() if p.area() > 0.05)  # noqa: E731
    return 100 * s(thin) / cs.area(), s(gap)


def small_checks(kc):
    front = A.union(*kc.regions(kc.front).values())
    back = A.union(*kc.regions(kc.back).values())
    ft, fg = thin_and_gaps(front, 0.6, 0.5)              # kabartma: çizgi ≥ 0,6, boşluk ≥ 0,5
    bt, bg = thin_and_gaps(back, 0.5, 0.45)              # ilk katman (0,5 mm hat): çizgi ≥ 0,5, boşluk ≥ 0,45
    lost = [i for i, (cs, _) in enumerate(kc.front + kc.back) if (cs ^ kc.keep).area() + 0.01 < cs.area() * 0.98]
    d = A.Design(kc.key, kc.title, kc.outline, kc.front, kc.holes)
    return {"ön ince%": ft, "ön dar": fg, "arka ince%": bt, "arka dar": bg, "yakın öğe": d.check_pairs(),
            "delik et payı": d.hole_wall(), "kırpılan": lost}


def main():
    only = sys.argv[1:]
    template = zipfile.ZipFile(A.TEMPLATE)
    template_files = {n: template.read(n) for n in template.namelist()}
    os.makedirs(os.path.join(OUT_DIR, "onizleme"), exist_ok=True)
    sheets = []
    for fn in SMALL:
        kc = P.Keychain(fn())
        if only and not any(o in kc.key for o in only):
            continue
        kc.title = "AUTO_FIRAT_TUYGUN_kucuk_" + kc.key
        path, _, filaments = A.write_design(kc, template_files, OUT_DIR)
        parts = kc.solids()
        mans = [m for _, m, _ in parts]
        union = m3.Manifold.batch_boolean(mans, m3.OpType.Add)
        overlap = max((mans[i] ^ mans[j]).volume() for i in range(len(mans)) for j in range(i + 1, len(mans)))
        _, changes, flush = kc.colour_changes()
        print(f"{os.path.relpath(path, A.ROOT)}  {kc.size()[0]:.0f}×{kc.size()[1]:.0f} mm  "
              f"AMS: {', '.join(A.COLOUR_NAMES[f] for f in filaments)}")
        print("  " + "  ".join(f"{k}: {v:.1f}" if isinstance(v, float) else f"{k}: {v}" for k, v in small_checks(kc).items()))
        print(f"  sağlam: {all(str(m.status()).endswith('NoError') for m in mans)}  örtüşme: {overlap:.4f} mm³  "
              f"tek gövde: {len(union.decompose()) == 1}  filament değişimi: {changes} (~{flush} mm³)")
        sheets.append(P.preview(kc, parts, filaments, os.path.join(OUT_DIR, "onizleme", kc.key + ".png"),
                                title=kc.concept.title.upper() + " (KÜÇÜK) – BASKIYA HAZIR"))
    if not only:
        K.stack(sheets, os.path.join(OUT_DIR, "onizleme", "hepsi.png"))


if __name__ == "__main__":
    main()
