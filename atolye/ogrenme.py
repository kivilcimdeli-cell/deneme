"""Tercihlerden öğrenme: kataloglarda gösterilen ve müşterinin seçtiği tasarımların özellikleri sayılır.

Her tasarımın özellikleri bir sözlük: {"sablon": "yan_yana", "palet": "siyah-kirmizi", "simge": "lastik", ...}.
Her özellik değeri için gösterim ve seçim sayısı tutulur (atolye_veri/tercihler.json, ürün başına). Bir değerin puanı
(seçim + 1) / (gösterim + 4) × 4: hiç gösterilmemiş değer 1 puandan başlar (yeni şeyler de denenir), seçildikçe
yükselir, seçilmeden çok gösterildikçe düşer. Tasarımın ağırlığı özellik puanlarının çarpımı (geometrik ortalaması).

Katalog seçimi: adayların yaklaşık %70'i ağırlıkla, %30'u rastgele (keşif) seçilir; böylece katalog beğenilen
tarza kayar ama hep aynı şeyleri göstermez.
"""
import json
import math
import os
import random
import threading

from . import VERI

YOL = os.path.join(VERI, "tercihler.json")
_KILIT = threading.Lock()
KESIF = 0.3


def _oku():
    try:
        with open(YOL, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _yaz(d):
    os.makedirs(VERI, exist_ok=True)
    tmp = YOL + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    os.replace(tmp, YOL)


def _say(urun, ozellik_listesi, alan):
    with _KILIT:
        d = _oku()
        u = d.setdefault(urun, {})
        for oz in ozellik_listesi:
            for k, v in oz.items():
                s = u.setdefault(k, {}).setdefault(str(v), {"goster": 0, "sec": 0})
                s[alan] += 1
        _yaz(d)


def gosterildi(urun, ozellik_listesi):
    _say(urun, ozellik_listesi, "goster")


def secildi(urun, ozellikler):
    _say(urun, [ozellikler], "sec")


def puan(urun, ozellikler, d=None):
    u = (d if d is not None else _oku()).get(urun, {})
    p = [((u.get(k, {}).get(str(v), {}).get("sec", 0) + 1) /
          (u.get(k, {}).get(str(v), {}).get("goster", 0) + 4) * 4) for k, v in ozellikler.items()]
    return math.exp(sum(math.log(x) for x in p) / len(p)) if p else 1.0


def sec(urun, adaylar, adet, haric=(), tohum=None, uygun=None, agirlik=None):
    """adaylar: [(imza, ozellikler)]; haric: bu müşteriye daha önce gösterilen imzalar (yeni katalogda tekrar
    edilmez, aday yetmezse kullanılır). uygun(seçilenler, aday): katalog kuralı (aynı düzenden en çok iki gibi);
    uyan aday kalmazsa kural gevşer. agirlik(imza): öğrenme puanıyla çarpılan ek ağırlık (tasarımın bu müşteriye
    uygunluğu gibi). Döner: seçilen imzalar (adet kadar), seçiliş sırasıyla."""
    rnd = random.Random(tohum)
    d = _oku()
    taze = [a for a in adaylar if a[0] not in set(haric)]
    havuz = taze if len(taze) >= adet else taze + [a for a in adaylar if a[0] in set(haric)]
    secilen = []
    while havuz and len(secilen) < adet:
        aday = [i for i, a in enumerate(havuz) if uygun is None or uygun(secilen, a)] or list(range(len(havuz)))
        if rnd.random() < KESIF:
            i = rnd.choice(aday)
        else:
            w = [puan(urun, havuz[i][1], d) * (agirlik(havuz[i][0]) if agirlik else 1.0) for i in aday]
            i = rnd.choices(aday, weights=w)[0]
        secilen.append(havuz.pop(i))
    return [imza for imza, _ in secilen]


def ozet(urun):
    """Arayüz için: her özellikte en çok seçilen değerler."""
    u = _oku().get(urun, {})
    out = {}
    for k, vals in u.items():
        top = sorted(vals.items(), key=lambda kv: (-kv[1]["sec"], -kv[1]["goster"]))[:3]
        out[k] = [{"deger": v, **c} for v, c in top]
    return out
