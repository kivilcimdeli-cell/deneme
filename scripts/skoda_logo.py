"""Škoda amblemi (kanatlı ok) – siyah beyaz, tişört için ince yama: baskıya hazır Bambu Lab X2D 3MF.

Logo Simple Icons'tan (`scripts/logolar/skoda.svg`, CC0). Siyah: dış halka ve kanatlı ok; beyaz: halkanın içindeki
zemin ve okun gözü. BMW yamasıyla aynı yapı (`bmw_logo.py`): Ø80 mm, 0,6 mm (3 katman), renkler kalınlık boyunca,
1. katmandan sonra duraklatma (tül serilir). Siyah ana nozulda, beyaz yardımcı nozulda: filament değişimi yok.

Çıktı : skoda_logo/skoda_logo_tisort.3mf, skoda_logo/onizleme.png

Kullanım:
  pip install svgelements
  python3 scripts/skoda_logo.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import bmw_logo as B  # noqa: E402

OUT_DIR = os.path.join(A.ROOT, "skoda_logo")
SVG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logolar", "skoda.svg")
R_OUT, R_RING = 12.0, 10.964            # simgedeki dış halka (24 birimlik kutu)


def regions():
    """Halka tam çemberlerle, kanatlı ok simgeden; beyaz ikisinin tam tümleyeni (kılcal boşluk yok)."""
    k = B.D / 24.0
    circ = lambda r: A.circle(r * k, 0, 0, B.SEG)  # noqa: E731
    arrow = B.svg_fill(SVG) ^ circ(10.5)                   # ok r 4,2..9,7 arasında
    black = (circ(R_OUT) - circ(R_RING)) + arrow
    white = circ(R_RING) - arrow
    clean = lambda cs: A.union(*[p for p in cs.decompose() if p.area() > 0.2])  # noqa: E731
    return {A.BLACK: clean(black), A.WHITE: clean(white)}


def main():
    logo = B.Logo("skoda_logo_tisort", "SKODA_logo_tisort", regions(),
                  {A.BLACK: "Siyah (halka ve kanatlı ok)", A.WHITE: "Beyaz (zemin ve göz)"},
                  {A.BLACK: 1, A.WHITE: 2}, "ŠKODA LOGOSU (SİYAH BEYAZ) – TİŞÖRT İÇİN İNCE YAMA (X2D)",
                  "AMS: 1 siyah · 2 beyaz   ·   siyah: ana nozul, beyaz: yardımcı nozul (filament değişimi yok)")
    B.make(logo, OUT_DIR)


if __name__ == "__main__":
    main()
