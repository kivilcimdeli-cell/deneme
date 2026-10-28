"""Şablonların ortak parçaları: simgeler, yazı yardımcıları, büyük adın sığdırılması."""
import html
import os
import re

from PIL import ImageFont

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")
CHARS = "".join(chr(c) for c in range(0x20, 0x7F)) + "ÇçĞğİıÖöŞşÜüÂâÎîÛû·–—’‘“”…•₺→©"
LOGOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logolar")

# simgeler: WhatsApp ve Instagram Simple Icons (CC0), diğerleri Material Icons (Apache 2.0)
ICON = {
    "phone": "M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 "
             "0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 "
             "3.57.11.35.03.74-.25 1.02l-2.2 2.2z",
    "star": "M12 17.27 18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z",
    "bank": "M4 10v7h3v-7H4zm6 0v7h3v-7h-3zM2 22h19v-3H2v3zm14-12v7h3v-7h-3zm-4.5-9L2 6v2h19V6l-9.5-5z",
    "copy": "M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-"
            ".9-2-2-2zm0 16H8V7h11v14z",
    "person": "M15 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm-9-2V7H4v3H1v2h3v3h2v-3h3v-2H6zm9 4c-2.67 "
              "0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z",
    "qr": "M3 11h8V3H3v8zm2-6h4v4H5V5zM3 21h8v-8H3v8zm2-6h4v4H5v-4zM13 3v8h8V3h-8zm6 6h-4V5h4v4zM19 19h2v2h-2zM13 13h2v2"
          "h-2zM15 15h2v2h-2zM13 17h2v2h-2zM15 19h2v2h-2zM17 17h2v2h-2zM17 13h2v2h-2zM19 15h2v2h-2z",
    "pin": "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12"
           "-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z",
    "globe": "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62"
             ".08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c"
             ".55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z",
}
for _k in ("whatsapp", "instagram"):
    ICON[_k] = re.search(r' d="([^"]+)"', open(os.path.join(LOGOS, _k + ".svg")).read()).group(1)


def svg(key, cls="ic"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true"><path d="{ICON[key]}"/></svg>'


def e(s):
    return html.escape(str(s))


def tr_upper(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


def tr_title(s):
    """Türkçe baş harfler: SOYLU OTO LASTİK → Soylu Oto Lastik (Python'un title()'ı I'yı i yapar)."""
    low = s.replace("I", "ı").replace("İ", "i").lower()
    return " ".join(w[:1].replace("i", "İ").replace("ı", "I").upper() + w[1:] for w in low.split())


def fit(mark_font, site, extra_em=0.0):
    """Büyük adın genişliğe sığması için em başına düşen genişlik oranı (CSS: font-size = kullanılabilir × oran).
    mark_font: (yazı tipi dosyası, harf aralığı em)."""
    fn, tracking = mark_font
    f = ImageFont.truetype(os.path.join(FONT_DIR, fn), 1000)
    w = max(f.getlength(t) / 1000 + tracking * (len(t) - 1) for t in site.lines) + extra_em
    return 0.97 / w


def smooth(pts):
    """Noktalardan geçen yumuşak SVG yolu (Catmull-Rom → kübik Bézier)."""
    p = [pts[0]] + list(pts) + [pts[-1]]
    d = f"M{p[1][0]:g} {p[1][1]:g}"
    for i in range(1, len(p) - 2):
        c1 = (p[i][0] + (p[i + 1][0] - p[i - 1][0]) / 6, p[i][1] + (p[i + 1][1] - p[i - 1][1]) / 6)
        c2 = (p[i + 1][0] - (p[i + 2][0] - p[i][0]) / 6, p[i + 1][1] - (p[i + 2][1] - p[i][1]) / 6)
        d += f"C{c1[0]:.0f} {c1[1]:.0f} {c2[0]:.0f} {c2[1]:.0f} {p[i + 1][0]:g} {p[i + 1][1]:g}"
    return d


# Çizilerek gelen logo: .br fırça darbesi (maskede, yazılır gibi), .tr dış hat (çizilir), .fl iç (sonra dolar).
# Hareketi azalt açıkken şablonların kuralı animasyonu kapatır: darbeler tam, logo son hâliyle görünür.
DRAW_CSS = """
.drawn .br{fill:none;stroke:#fff;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1 2;stroke-dashoffset:0;
  animation:draw .7s cubic-bezier(.5,.05,.3,1) both}
.drawn .tr{fill:none;stroke:currentColor;stroke-linejoin:round;stroke-dasharray:1 2;stroke-dashoffset:0;
  animation:draw 1.2s cubic-bezier(.45,0,.3,1) both}
.drawn .fl{animation:fillin .6s ease-out both}
@keyframes draw{from{stroke-dashoffset:1.02}to{stroke-dashoffset:0}}
@keyframes fillin{from{opacity:0}to{opacity:1}}
"""


def drawn_mark(site, cls, start=0.2):
    """Logo işareti çizilerek gelir. Fırça darbeleri (isaret_cizgi) varsa logo yazılır gibi açılır (darbeler sırayla,
    uzunluğuyla orantılı sürede); yoksa önce dış hattı çizilir, sonra içi dolar. Döner: (svg, bitiş anı sn)."""
    if not site.isaret:
        return "", start
    x0, y0, w, h = (float(v) for v in site.isaret_box.split())
    box = f'viewBox="{site.isaret_box}"'
    if site.isaret_cizgi:
        t, strokes = start, []
        for wd, pts in site.isaret_cizgi:
            n = sum(((pts[i + 1][0] - pts[i][0]) ** 2 + (pts[i + 1][1] - pts[i][1]) ** 2) ** .5
                    for i in range(len(pts) - 1))
            dur = 0.25 + n / (1.6 * max(w, h))
            strokes.append(f'<path class="br" pathLength="1" d="{smooth(pts)}" stroke-width="{wd}" '
                           f'style="animation-delay:{t:.2f}s;animation-duration:{dur:.2f}s"/>')
            t += dur * 0.85
        mid = f"dm-{cls}"
        pad = max(w, h) * 0.15
        return (f'<svg class="{cls} drawn" {box} aria-hidden="true"><defs><mask id="{mid}" maskUnits="userSpaceOnUse" '
                f'x="{x0 - pad:g}" y="{y0 - pad:g}" width="{w + 2 * pad:g}" height="{h + 2 * pad:g}">{"".join(strokes)}'
                f'</mask></defs><g mask="url(#{mid})">{site.isaret}</g></svg>'), t + 0.15
    outline = site.isaret.replace("<path ", f'<path class="tr" pathLength="1" stroke-width="{max(w, h) * .012:.1f}" '
                                            f'style="animation-delay:{start:.2f}s" ')
    return (f'<svg class="{cls} drawn" {box} aria-hidden="true"><g class="fl" style="animation-delay:{start + .9:.2f}s">'
            f'{site.isaret}</g>{outline}</svg>'), start + 1.5
