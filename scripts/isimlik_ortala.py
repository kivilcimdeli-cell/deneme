"""Hazır bir isimlik 3MF'inde sağ sütunun yazılarını dikeyde ortalar (gerisine dokunmaz).

İstek (Antalya 7/24 Oto Lastik Tamiri, uzar1 M06, sade hâli): "müşteri sade tasarımı istedi ama yazıları biraz
ortalayalım". Sağ sütunda iki öbek var: üstte ad ve iş türü (ANTALYA, OTO LASTİK TAMİRİ), altta çağrı ve telefon
(HEMEN ARA, 0542 …); aralarında 30 mm boşluk kalmıştı.

- Öbekler birbirine yaklaşır (aralarında `--ara` mm) ve sütun soldaki QR + TARA bloğuyla aynı hizada ortalanır.
- Yalnız kabartma parçalarındaki sağ sütun yazıları kayar; QR, TARA, panel ve sehpa yerinde kalır.
- Önizlemeler yeniden çizilir; ağ kapalı, QR okunuyor, yazılar panelin güvenli alanında (kenara 3 mm, sehpanın
  örttüğü alt şeride girmez).

Okuma yönü: u = y (soldan sağa), v = -x (aşağıdan yukarı).

Kullanım:
  python3 scripts/isimlik_ortala.py <giriş.3mf> <çıkış.3mf> [--ara 8] [--sinir 18] [--onizleme önden.png]
    --sinir: sağ sütunun sol sınırı (u, mm); solundakiler (QR, TARA) kaymaz
"""
import argparse
import os
import sys
import zipfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from isimlik_lastik_izi import oku, onizleme, parca_bilgisi, yaz_3mf  # noqa: E402

PANEL_UST, PANEL_ALT = 45.0 - 3.0, -45.0 + 9.5        # güvenli alan (v): üst kenara 3 mm, sehpa alt 9,5 mm'yi örter


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("giris")
    ap.add_argument("cikis")
    ap.add_argument("--ara", type=float, default=8.0, help="iki öbek arası (mm)")
    ap.add_argument("--sinir", type=float, default=18.0)
    ap.add_argument("--onizleme", default=None)
    a = ap.parse_args()

    z = zipfile.ZipFile(a.giris)
    obj_s, parts = oku(z)
    cfg = z.read("Metadata/model_settings.config").decode()
    bilgi = parca_bilgisi(cfg)
    kabartma = [no for no, ad, _ in bilgi if "Kabartma" in ad]
    dolgu = [no for no, ad, _ in bilgi if "Dolgu" in ad]

    # sağ sütunun noktaları ve öbekler arasındaki en büyük boşluk
    sag = {no: (parts[no][0][:, 1] > a.sinir) for no in kabartma}
    v_sag = np.concatenate([-parts[no][0][sag[no], 0] for no in kabartma])
    vs = np.unique(np.round(v_sag, 2))
    i = int(np.argmax(np.diff(vs)))
    ayrim, bosluk = (vs[i] + vs[i + 1]) / 2, vs[i + 1] - vs[i]
    ust = v_sag[v_sag > ayrim]
    alt = v_sag[v_sag < ayrim]
    # soldaki blok: QR karosu ve altındaki yazı
    v_sol = np.concatenate([-parts[no][0][:, 0] for no in dolgu] +
                           [-parts[no][0][~sag[no], 0] for no in kabartma])
    orta = (v_sol.min() + v_sol.max()) / 2
    toplam = (ust.max() - ust.min()) + a.ara + (alt.max() - alt.min())
    tepe = orta + toplam / 2
    d_ust = tepe - ust.max()
    d_alt = (tepe - (ust.max() - ust.min()) - a.ara) - alt.max()
    print(f"önce: üst öbek v {ust.min():.1f} … {ust.max():.1f}, alt öbek {alt.min():.1f} … {alt.max():.1f}, "
          f"ara {bosluk:.1f} mm; sol blok {v_sol.min():.1f} … {v_sol.max():.1f} (ortası {orta:.1f})")
    print(f"kayma: üst öbek {d_ust:+.1f} mm, alt öbek {d_alt:+.1f} mm → sütun {tepe - toplam:.1f} … {tepe:.1f}, "
          f"ara {a.ara:g} mm")
    assert tepe <= PANEL_UST and tepe - toplam >= PANEL_ALT, "yazılar panelin güvenli alanından taşıyor"

    for no in kabartma:
        V = parts[no][0].copy()
        v = -V[:, 0]
        m_ust = sag[no] & (v > ayrim)
        m_alt = sag[no] & (v < ayrim)
        V[m_ust, 0] -= d_ust                           # v = -x: v'yi d kadar artırmak x'i d kadar azaltır
        V[m_alt, 0] -= d_alt
        parts[no] = (V, parts[no][1])
    if a.onizleme:
        onizleme(parts, bilgi, [], a.onizleme)
    yaz_3mf(z, obj_s, cfg, parts, bilgi, kabartma, a.cikis)


if __name__ == "__main__":
    main()
