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
from PIL import Image, ImageDraw, ImageFont

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


def s9_kose_serit_v2():
    """Müşterinin seçtiği köşe şerit, düzenlenmiş ve küçültülmüş (43 × 25 mm): AUTO ile isim arasında ince altın çizgi,
    arka yüzde de aynı köşede altın şerit (ön şeridin tam arkasında). İsim ve telefon 3,2 mm, AUTO 3,8 mm:
    tek satırda net basılan en büyük boy; daha küçük kartta yazı küçülmek zorunda kalır."""
    W, H = 43.0, 25.0
    card = A.rrect(W, H, 4.0)
    lo, hi = W / 2 + H / 2 - 9.6, W / 2 + H / 2 - 4.6        # şerit sağ üst köşede: lo ≤ x + y ≤ hi
    band = A.polygon([(lo + 30, -30), (hi + 30, -30), (-30, hi + 30), (-30, lo + 30)])
    c = concept("9_kose_serit_v2", "Köşe şerit – düzenlenmiş",
                "AUTO ile isim arasında ince altın çizgi; arka yüzde de aynı köşede altın şerit. 43 × 25 mm.",
                card, A.circle(HOLE_R, -W / 2 + 5.3, H / 2 - 5.3))
    x0 = -W / 2 + 3.6                                         # yazıların sol kenarı (görünen harf kenarı)
    left = lambda cs: cs.translate((x0 - cs.bounds()[0], 0))  # noqa: E731
    nm = left(name(3.2, 0, -6.9, align="l"))
    c.front += [(band ^ card, GOLD),
                (left(K.auto_word(3.8, 0, -0.2)), GOLD),
                (A.rect(x0, -4.1, nm.bounds()[2], -3.3), GOLD),          # 0,8 mm ince çizgi, isim kadar
                (nm, WHITE)]
    c.back += [(band.mirror((1, 0)) ^ card, GOLD),                      # arkadan bakınca sol üst köşe
               (left(phone(3.2, 0, -2.4, align="l")), WHITE),
               (left(city(2.8, 0, -7.6, align="l")), GOLD)]
    return c


def s9_kose_serit_v3():
    """Köşe şerit, düzenlenmiş, %15 büyütülmüş (49,5 × 28,75 mm; 43 × 25'in 1,15 katı). Baskı denemesinde yazılar
    bulanık, arka yazılar kötü çıktı: ön yazılar %15, arka (ilk katmanda basılan) yazılar %19-21 büyütüldü ve harf
    aralığı açıldı. Ön: AUTO 4,4 · isim 3,7 · çizgi 0,9. Arka: telefon 3,8 · ANTALYA 3,4.
    Köşe şeridi (ön ve arka) inceltildi: 3,0 mm; köşeye bakan kenarı yerinde, iç kenarı köşeye yaklaştı."""
    W, H = 49.5, 28.75
    card = A.rrect(W, H, 4.6)
    lo, hi = W / 2 + H / 2 - 9.5, W / 2 + H / 2 - 5.3         # şerit sağ üst köşede: lo ≤ x + y ≤ hi (3,0 mm)
    band = A.polygon([(lo + 30, -30), (hi + 30, -30), (-30, hi + 30), (-30, lo + 30)])
    c = concept("9_kose_serit_v3", "Köşe şerit – düzenlenmiş",
                "AUTO ile isim arasında ince altın çizgi; arka yüzde de aynı köşede altın şerit. 49,5 × 28,75 mm.",
                card, A.circle(HOLE_R, -W / 2 + 5.8, H / 2 - 5.8))
    x0 = -W / 2 + 4.2                                         # yazıların sol kenarı (görünen harf kenarı)
    left = lambda cs: cs.translate((x0 - cs.bounds()[0], 0))  # noqa: E731
    nm = left(name(3.7, 0, -7.55, align="l"))
    c.front += [(band ^ card, GOLD),
                (left(K.auto_word(4.4, 0, 0.2)), GOLD),
                (A.rect(x0, -4.3, nm.bounds()[2], -3.4), GOLD),          # 0,9 mm ince çizgi, isim kadar
                (nm, WHITE)]
    c.back += [(band.mirror((1, 0)) ^ card, GOLD),                      # arkadan bakınca sol üst köşe
               (left(K.outfit().text(PHONE, 3.8, 0, -2.6, align="l", tracking=0.45)), WHITE),
               (left(K.outfit().text(CITY, 3.4, 0, -8.6, align="l", tracking=3.4 * 0.35)), GOLD)]
    return c


def encode():
    """Encode Sans Condensed Black (OFL): tek satıra sığan en kalın ve harf içi en açık yazı tipi (ölçüldü:
    Outfit, Lexend, Rubik, Montserrat, Barlow, Roboto/Fira/Saira/Sofia/Asap/Oswald Condensed ile karşılaştırıldı)."""
    return A.Font("EncodeSansCondensed-Black.ttf")


def s9_kose_serit_v5():
    """Köşe şerit, son sürüm (49,5 × 28,75 mm), müşterinin onayladığı diziliş: önde AUTO / ince altın çizgi /
    FIRAT TUYGUN (tek satır), arkada telefon (tek satır) / ANTALYA. Outfit'in tek satırda harf çizgilerinin %26-42'si
    0,9 mm'den inceydi; Encode Sans Condensed Black ile harfler daha uzun (isim 4,33, telefon 4,29 mm) ve kalın:
    0,9 mm'den ince isim %6, telefon %13; rakam içleri en az 0,8 mm. Yazılar kenardan 3 mm içeride."""
    W, H = 49.5, 28.75
    card = A.rrect(W, H, 4.6)
    lo, hi = W / 2 + H / 2 - 9.5, W / 2 + H / 2 - 5.3         # şerit sağ üst köşede: lo ≤ x + y ≤ hi (3,0 mm)
    band = A.polygon([(lo + 30, -30), (hi + 30, -30), (-30, hi + 30), (-30, lo + 30)])
    hx, hy = -W / 2 + 5.8, H / 2 - 5.8
    c = concept("9_kose_serit_v5", "Köşe şerit – son",
                "AUTO / ince altın çizgi / FIRAT TUYGUN; arkada telefon / ANTALYA; iki yüzde köşe şeridi.",
                card, A.circle(2.5, hx, hy))                   # Ø5,0 delik: halka kolay geçsin (et payı 3,3 mm)
    f = encode()
    x0, x1 = -W / 2 + 3.0, W / 2 - 3.0                        # yazı alanı: 43,5 mm
    at = lambda cs: cs.translate((x0 - cs.bounds()[0], 0))    # noqa: E731  görünen sol kenar x0'da

    def fit(text, cap, y, trk):                                # 43,5 mm'ye sığan en büyük boy (en fazla `cap`)
        for _ in range(6):
            cap = min(cap, f.fit_cap(text, cap, x1 - x0, cap * trk))
        return at(f.text(text, cap, 0, y, align="l", tracking=cap * trk))
    nm = fit(NAME, 4.4, -7.6, 0.10)
    c.front += [(band ^ card, GOLD),
                (at(f.text("AUTO", 5.0, 0, 0.85, align="l", tracking=5.0 * 0.18)), GOLD),
                (A.rect(x0, -4.05, nm.bounds()[2], -3.05), GOLD),          # 1,0 mm ince çizgi, isim kadar
                (nm, WHITE)]
    c.back += [(band.mirror((1, 0)) ^ card, GOLD),                      # arkadan bakınca sol üst köşe
               (fit(PHONE, 4.4, -2.4, 0.12), WHITE),
               (at(f.text(CITY, 4.2, 0, -8.7, align="l", tracking=4.2 * 0.22)), GOLD)]
    return c


SMALL = [s1_kapsul, s2_logo_kare, s3_madalyon, s6_tek_cizgi, s7_altigen, s9_kose_serit]
# küçük yazı için baskı ayarları (yalnız bu dosyaların proje ayarı)
NET_YAZI = {
    # ön yüz kabartma yazılar: yavaş, yumuşak dış duvar; ince harf içleri (boşluk dolgusu) yavaş; hassas duvar
    "outer_wall_speed": ["50", "50", "50", "50"], "outer_wall_acceleration": ["2000", "2000", "1000", "1000"],
    "inner_wall_speed": ["100", "100", "100", "100"], "gap_infill_speed": ["60", "60", "60", "60"],
    "top_surface_speed": ["80", "80", "80", "80"], "precise_outer_wall": "1", "reduce_crossing_wall": "1",
    # dikiş: dış duvarlarda kademeli (scarf) dikiş; yuvarlak harflerde (O, U) dikiş izi kalmaz. Köşelerde dikiş
    # hizalı kalır (köşede iz zaten saklanır). Önizlemedeki beyaz noktalar dikiş işaretidir, filament değil.
    "seam_slope_type": "external",
    # ütüleme: üst yüzeyler (harf üstleri ve siyah yüz) düz ve parlak çıkar
    "ironing_type": "top",
    # arka yüz yazıları ilk katmanda: ince hat (0,42), yavaş ilk katman; gövdede zaten 0,6 mm ilk katman pahı var
    "initial_layer_line_width": "0.42", "initial_layer_speed": ["30", "30", "30", "30"],
    "initial_layer_infill_speed": ["40", "40", "40", "40"], "elefant_foot_compensation": "0",
    # şablondaki Cool Plate (35 °C) yerine PEI tabla (PLA 55 °C); düz ya da dokulu PEI aynı sıcaklık
    "curr_bed_type": "Textured PEI Plate",
}
# gövde 3,2 -> 2,6 mm: çelik anahtarlık halkası 3,2 mm'lik gövdeyi kavrayamıyordu (kabartma 1,2 mm; toplam 3,8 mm)
V5 = {"keep_back_colours": True, "raise_h": 1.2, "body_h": 2.6}


def tower_size(n_fil=3, prime=45.0, change_len=10.0, layer=0.2, gap=1.5, rib=8.0, height=3.8):
    """Bambu Studio'nun prime kulesi tahmini (PartPlate::estimate_wipe_tower_size; X2D, kaburgalı kule): kare kule
    kenarı (mm) ve otomatik kenar (brim) genişliği. `prime`: en büyük filament_prime_volume (Generic PLA 45 mm³),
    `change_len`: en büyük filament_change_length (10 mm)."""
    volume = prime * n_fil + change_len * np.pi * 1.75 ** 2 / 4 * (n_fil // 2)
    d = np.sqrt(volume / layer * gap)
    d0 = max(5.0, d)                                       # 5 mm'den alçak kulede en az 5 mm
    return min(rib, d0 / 2) / np.sqrt(2) + max(d0, d), height / 100 * 8


TOWER, TOWER_BRIM = tower_size()                           # ~40,2 mm kare, 0,3 mm kenar
TOWER_MARGIN = 15.0                                        # Bambu kuleyi tabla kenarından en az 15 mm içeride tutar
X_AUX = 20.5                                               # X2D yardımcı nozul x < 20,5 mm'ye ulaşamaz


def plate_layout(w=49.5, h=28.75, gap=4.0, x_hi=256.0, y0=6.0):
    """Dolu tabla, 27 adet: önde 3 sıra × 7 dik kart (90° döndürülmüş; en `h`, boy `w`), arkada solda prime kulesi,
    sağında 2 sıra × 3 yatık kart. Kartlar ve kule iki nozulun ortak alanında (x ≥ 20,5). Kule arkadaki boş şeride
    sığmaz: Bambu onu kenardan 15 mm içeri çeker, kartların üstüne biner."""
    cols = 7
    x1 = (X_AUX + x_hi) / 2 - (cols * h + (cols - 1) * gap) / 2       # dik kartların sol kenarı
    right = x1 + cols * h + (cols - 1) * gap
    out = [(x1 + h / 2 + c * (h + gap), y0 + w / 2 + r * (w + gap), 90) for r in range(3) for c in range(cols)]
    yb = y0 + 3 * (w + gap)                                           # arka bölümün ön kenarı
    out += [(right - w / 2 - c * (w + gap), yb + h / 2 + r * (h + gap), 0) for r in range(2) for c in range(3)]
    tower = (max(X_AUX, TOWER_MARGIN) + 1.5, yb + gap)
    return [(round(x, 3), round(y, 3), a) for x, y, a in out], tuple(round(v, 3) for v in tower)


PLATE, TOWER_XY = plate_layout()
# Dolu tabla: baskı ayarları Bambu standart profili (önceki dosya en iyi sonucu verdi), yalnız tabla tipi ve kule yeri.
TABLA = {"curr_bed_type": "Textured PEI Plate",
         "wipe_tower_x": [f"{TOWER_XY[0]:g}"], "wipe_tower_y": [f"{TOWER_XY[1]:g}"]}
# Siyah gövde ana nozulda (doğrudan sürücü): yardımcı nozul Bowden beslemeli, geri çekmesi zayıf; gövdenin hızlı ve
# çok basılan siyahında ipliklenme ve tozlu yüzey yapıyordu. Beyaz da ana nozulda (aynı Elas PLA Pro), az basılan silk
# altın yardımcı nozulda. Elas PLA Pro (siyah, beyaz) için Bambu'nun başka marka PLA profili (eritme hızı 12 mm³/s).
DOLU_TABLA = dict(V5, project_overrides=TABLA, instances=PLATE, suffix="_dolu_tabla",
                  nozzle_map={A.BLACK: 1, A.WHITE: 1, A.GOLD: 2},
                  filament_profiles={A.BLACK: A.GENERIC_PLA, A.WHITE: A.GENERIC_PLA})
FINAL = [(s9_kose_serit_v5, dict(V5, project_overrides=NET_YAZI)), (s9_kose_serit_v5, DOLU_TABLA)]


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
    out = {"ön ince%": ft, "ön dar": fg, "arka ince%": bt, "arka dar": bg, "yakın öğe": d.check_pairs(),
           "delik et payı": d.hole_wall(), "kırpılan": lost}
    if kc.lug:                                           # ön kabartmalar inceltilen kulağa en az 0,6 mm uzak olmalı
        out["kulağa yakın ön öğe"] = [i for i, (cs, _) in enumerate(kc.front)
                                      if (cs ^ kc.lug[0].offset(0.6, J)).area() > 0.01]
    return out


def plate_footprints(kc, parts):
    """Tabladaki her kopyanın taban izi (x0, y0, x1, y1)."""
    V = np.vstack([A.mesh_arrays(m)[0] for _, m, _ in parts])
    out = []
    for inst in kc.instances:
        P_ = A.placed(V, *inst)
        out.append((*P_[:, :2].min(0), *P_[:, :2].max(0)))
    return out


def plate_checks(kc, parts, min_clear=5.0):
    """Kopyalar iki nozulun ortak alanında mı, birbirine ve kuleye ne kadar yakın; kule Bambu'nun izin verdiği yerde mi
    (yoksa Bambu onu kaydırır ve kartlara bindirir)."""
    boxes = plate_footprints(kc, parts)
    inside = all(b[0] >= X_AUX and b[1] >= 0 and b[2] <= 256 and b[3] <= 256 for b in boxes)
    sep = lambda a, b: max(b[0] - a[2], a[0] - b[2], b[1] - a[3], a[1] - b[3])  # noqa: E731
    gap = min(sep(bi, bj) for i, bi in enumerate(boxes) for bj in boxes[i + 1:])
    tx, ty = TOWER_XY
    lim = 256 - TOWER - TOWER_MARGIN - TOWER_BRIM                  # eski sürümler kenarı da düşer
    allowed = TOWER_MARGIN <= tx <= lim and TOWER_MARGIN <= ty <= lim and tx - TOWER_BRIM >= X_AUX
    tower = (tx - TOWER_BRIM, ty - TOWER_BRIM, tx + TOWER + TOWER_BRIM, ty + TOWER + TOWER_BRIM)
    clear = min(sep(tower, b) for b in boxes)
    ok = inside and gap >= 3.9 and allowed and clear >= min_clear
    return (f"tabla: {len(boxes)} adet, ortak alanda: {inside}, en yakın iki kart arası: {gap:.2f} mm, "
            f"kule {TOWER:.1f} mm kare ({tx:g}, {ty:g}), Bambu sınırında: {allowed}, kartlara {clear:.2f} mm -> "
            f"{'TAMAM' if ok else 'SORUN'}")


def plate_preview(kc, parts, path):
    """Tablanın üstten görünüşü: 256 × 256 tabla, kartlar ve prime kulesi."""
    bed = m3.Manifold.cube((256, 256, 0.2)).translate((0, 0, -0.4))
    tx, ty = TOWER_XY
    tower = m3.Manifold.cube((TOWER, TOWER, 3.8)).translate((tx, ty, 0))
    items = [(*A.mesh_arrays(bed), (205, 208, 214)), (*A.mesh_arrays(tower), (150, 156, 168))]
    for inst in kc.instances:
        for _, m, e in parts:
            V, T = A.mesh_arrays(m)
            items.append((A.placed(V, *inst), T, A.SHOW[e]))
    im = A.render(items, 900, A.R_TOP, flat=0.75, margin=0.02)
    canvas = Image.new("RGB", (im.width + 80, im.height + 120), (236, 239, 244))
    canvas.paste(im, (40, 90), im)
    dr = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(os.path.join(A.FONT_DIR, "Lexend-ExtraBold.ttf"), 30)
    fs = ImageFont.truetype(os.path.join(A.FONT_DIR, "Lexend-ExtraBold.ttf"), 19)
    dr.text((40, 18), f"DOLU TABLA – {len(kc.instances)} ADET (X2D 256 × 256)", fill=(30, 33, 40), font=f)
    dr.text((40, 58), "siyah + beyaz: ana nozul · altın: yardımcı nozul · gri: prime kulesi (Bambu tahmini, ~40 mm)",
            fill=(70, 76, 88), font=fs)
    canvas.save(path)


def main():
    only = sys.argv[1:]
    template = zipfile.ZipFile(A.TEMPLATE)
    template_files = {n: template.read(n) for n in template.namelist()}
    os.makedirs(os.path.join(OUT_DIR, "onizleme"), exist_ok=True)
    sheets = []
    for fn, opts in [(fn, {}) for fn in SMALL] + FINAL:
        c = fn()
        kc = P.Keychain(c, keep_back_colours=opts.get("keep_back_colours", False),
                        raise_h=opts.get("raise_h", P.RAISE), lug=getattr(c, "lug", None),
                        body_h=opts.get("body_h", P.BODY_H))
        kc.key += opts.get("suffix", "")
        if only and not any(o in kc.key for o in only):
            continue
        kc.title = "AUTO_FIRAT_TUYGUN_kucuk_" + kc.key
        for k in ("project_overrides", "instances", "nozzle_map", "filament_profiles"):
            setattr(kc, k, opts.get(k))
        path, _, filaments = A.write_design(kc, template_files, OUT_DIR)
        parts = kc.solids()
        mans = [m for _, m, _ in parts]
        union = m3.Manifold.batch_boolean(mans, m3.OpType.Add)
        overlap = max((mans[i] ^ mans[j]).volume() for i in range(len(mans)) for j in range(i + 1, len(mans)))
        _, changes, flush = kc.colour_changes(kc.nozzle_map)
        print(f"{os.path.relpath(path, A.ROOT)}  {kc.size()[0]:.0f}×{kc.size()[1]:.0f} mm  "
              f"AMS: {', '.join(A.COLOUR_NAMES[f] for f in filaments)}")
        print("  " + "  ".join(f"{k}: {v:.1f}" if isinstance(v, float) else f"{k}: {v}" for k, v in small_checks(kc).items()))
        print(f"  sağlam: {all(str(m.status()).endswith('NoError') for m in mans)}  örtüşme: {overlap:.4f} mm³  "
              f"tek gövde: {len(union.decompose()) == 1}  filament değişimi: {changes} (~{flush} mm³)")
        if kc.instances:
            print("  " + plate_checks(kc, parts))
            plate_preview(kc, parts, os.path.join(OUT_DIR, "onizleme", kc.key + ".png"))
            continue
        sheets.append(P.preview(kc, parts, filaments, os.path.join(OUT_DIR, "onizleme", kc.key + ".png"),
                                title=kc.concept.title.replace("i", "İ").upper() + " (KÜÇÜK) – BASKIYA HAZIR"))
    if not only:
        K.stack(sheets[:len(SMALL)], os.path.join(OUT_DIR, "onizleme", "hepsi.png"))


if __name__ == "__main__":
    main()
