"""Türk bayraklı masa isimliği (çapraz blok + 12° eğik sehpa): ad soyad girilir, X2D 3MF hazır.

Katalog yok (tasarım sabit; Fırat Tuygun'a yapılan çapraz blok, scripts/capraz_blok_sehpa.py). Ad soyad Türkçe
büyük harfe çevrilir; Bebas Neue 21 mm'ye kadar, uzun adlarda 240 mm'lik bloğa sığacak kadar küçülür. 12 mm'nin
altına inerse uyarı verilir (okunur ama küçük; iki satırlı tasarım ya da kısaltma önerilir).

Çıktılar (müşteri klasöründe, cikti/):
  bayrakli_<ad>_x2d.3mf   blok (ön yüz yukarı) ve sehpa tek tablada; AMS 1 siyah · 2 beyaz · 3 kırmızı
  onizleme.png            müşteriye gönderilecek görünüş (sehpasında, önden ve 3/4)
  tabla.png               tabla yerleşimi (kontrol için)
"""
KOD = "bayrakli"
AD = "Türk bayraklı masa isimliği"
SIMGE = "🇹🇷"
ACIKLAMA = "Çapraz blok 240 × 56 mm, kırmızı bayrak, siyah zeminde beyaz kabartma ad soyad, 12° eğik sehpa. Ad soyadı " \
           "yazın; 3MF hemen hazırlanır."
KATALOG_ADET = 0
ALANLAR = [
    {"ad": "ad_soyad", "etiket": "Ad soyad", "tur": "text", "zorunlu": True,
     "ipucu": "Blokta büyük harfle yazılır. 12 harfe kadar en büyük boy (21 mm)."},
    {"ad": "telefon", "etiket": "Müşterinin telefonu", "tur": "tel", "ipucu": "Kayıt için; isimliğe yazılmaz."},
    {"ad": "not", "etiket": "Sipariş notu", "tur": "textarea"},
]
MIN_CAP = 12.0


def ad(b):
    return b["ad_soyad"].strip()


def uret(is_, secilen=None):
    import os
    import zipfile

    from PIL import Image, ImageDraw, ImageFont

    import anahtarlik as A
    import capraz_blok as CB
    from sablonlar.ortak import tr_upper
    from atolye.kayit import slug

    isim = " ".join(tr_upper(is_.bilgiler["ad_soyad"]).split())
    CB.NAME = isim
    import capraz_blok_sehpa as CS
    import masa_isimligi_yeni as Y
    from cift_tarafli_isimlik import render, rotation

    is_.ilerle(10, "Blok ve sehpa kuruluyor")
    plate = CS.Plate()
    plate.key = f"bayrakli_{slug(isim, 30).replace('-', '_')}_x2d"
    plate.title = f"BOYDE_bayrakli_isimlik_{slug(isim, 30)}"
    cap = plate.block.cap
    out = is_.yol("cikti", "x")[:-2]
    template = zipfile.ZipFile(A.TEMPLATE)
    is_.ilerle(35, "3MF yazılıyor")
    path, _, _ = A.write_design(plate, {n: template.read(n) for n in template.namelist()}, out)
    parts = plate.solids()
    ok_place = CS.checks(plate, parts)
    is_.ilerle(60, "Önizleme çiziliyor")
    CS.preview(plate, parts, os.path.join(out, "tabla.png"))

    # müşteriye: sehpasında önden ve 3/4 (masa_isimligi_yeni.y7 gibi)
    base, h_f = Y.block_stand(CB.D)
    col = {A.BLACK: (36, 36, 39), A.RED: (222, 22, 34), A.WHITE: (246, 246, 242)}
    stood = [(*A.mesh_arrays(base), col[A.BLACK])]
    stood += [(*A.mesh_arrays(Y.tilted(CB.standing(m), Y.BLOCK_TILT, h_f, 0.0)), col[e])
              for _, m, e in plate.block.flat_parts()]
    on = A.fit_into(render(stood, 1400, rotation(0, -86), margin=0.02), 1100, 330)
    iso = A.fit_into(render(stood, 1400, rotation(-28, -72), margin=0.02), 1100, 420)
    canvas = Image.new("RGB", (1200, 940), (244, 241, 234))
    dr = ImageDraw.Draw(canvas)
    font = os.path.join(A.FONT_DIR, "Outfit-ExtraBold.ttf")
    dr.text((50, 36), "TÜRK BAYRAKLI MASA İSİMLİĞİ", fill=(255, 90, 31), font=ImageFont.truetype(font, 22))
    dr.text((50, 70), isim, fill=(18, 19, 22), font=ImageFont.truetype(font, 46))
    canvas.paste(on, ((1200 - on.width) // 2, 140), on)
    canvas.paste(iso, ((1200 - iso.width) // 2, 480), iso)
    dr.text((50, 900), "240 × 56 mm · 12° eğik sehpa · BOYDE LABS", fill=(85, 87, 92),
            font=ImageFont.truetype(os.path.join(A.FONT_DIR, "Outfit-SemiBold.ttf"), 20))
    canvas.save(os.path.join(out, "onizleme.png"))
    is_.ilerle(95, "Bitti")

    uyarilar = []
    if cap < MIN_CAP:
        uyarilar.append(f"Ad soyad uzun: yazı {cap:.1f} mm'ye küçüldü (en büyük 21 mm). Kısaltma ya da iki satır "
                        "düşünülebilir.")
    if "SORUN" in ok_place:
        uyarilar.append("Tabla yerleşim kontrolü: " + ok_place)
    return {"ciktilar": [{"ad": "X2D baskı dosyası (3MF)", "yol": is_.goreli(path), "tur": "3mf"},
                         {"ad": "Müşteri önizlemesi", "yol": is_.goreli(os.path.join(out, "onizleme.png")),
                          "tur": "resim"},
                         {"ad": "Tabla yerleşimi", "yol": is_.goreli(os.path.join(out, "tabla.png")), "tur": "resim"}],
            "uyarilar": uyarilar, "bilgi": {"yazi_boyu_mm": round(cap, 1)}}
