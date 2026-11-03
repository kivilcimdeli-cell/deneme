"""İşletme sitesi şablonları; her modül bir şablon. Üretici: scripts/sablon_site.py.

Lastikçi tarzı (sırayla döner, varsayılan): 1 Şimşek (Uzar), 2 Lastik izi (İnce), 3 İkaz (Çalık), 4 Kurumsal (Soylu),
5 Sade (yeni).
Güzellik (kuaför, güzellik salonu, tırnak, kirpik, spa…; kendi içinde sırayla, --guzellik): 6 Pudra, 7 Şakayık,
8 Gece, 9 Kemer, 10 Papatya.
"""
import importlib

from . import s1_simsek, s2_lastik_izi, s3_ikaz, s4_kurumsal, s5_sade

ALL = [s1_simsek, s2_lastik_izi, s3_ikaz, s4_kurumsal, s5_sade]
_GUZELLIK = ["g1_pudra", "g2_sakayik", "g3_gece", "g4_kemer", "g5_papatya"]
GUZELLIK = []
for _ad in _GUZELLIK:
    try:
        GUZELLIK.append(importlib.import_module(f".{_ad}", __name__))
    except ModuleNotFoundError as _e:
        if _e.name != f"{__name__}.{_ad}":
            raise


def get(n):
    return ALL[n - 1] if n <= len(ALL) else GUZELLIK[n - len(ALL) - 1]
