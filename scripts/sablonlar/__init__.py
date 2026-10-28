"""İşletme sitesi şablonları (lastikçi tarzı); her modül bir şablon. Üretici: scripts/sablon_site.py.

Sıra: 1 Şimşek (Uzar), 2 Lastik izi (İnce), 3 İkaz (Çalık), 4 Kurumsal (Soylu), 5 Gösterge (yeni).
"""
from . import s1_simsek, s2_lastik_izi, s3_ikaz, s4_kurumsal, s5_gosterge

ALL = [s1_simsek, s2_lastik_izi, s3_ikaz, s4_kurumsal, s5_gosterge]


def get(n):
    return ALL[n - 1]
