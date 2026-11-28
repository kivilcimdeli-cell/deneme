"""Güzellik şablonlarının (6–10) ortak parçaları: süs çizimleri (çiçek, papatya, şakayık, yaprak, dal, parıltı),
el yazısı adın sığdırılması, bağlantılar, ödeme bölümü, alttaki arama şeridi ve bildirim.

Kullanıcı isteği: "kuaför, beauty salonları, tırnakçılar için ... 5 adet farklı internet sitesi tasarla bu
ürünlerimize uygun" (güzellik koleksiyonu isimlikleri: scripts/boyde_guzellik.py). İçerik ve davranış lastikçi
şablonlarıyla aynı (Hemen Ara, WhatsApp, Instagram, Google, konum, rehber, IBAN, karekod; dış bağlantı yok, hareketi
azalt); WhatsApp satırı güzellikte randevu için: "Randevu al".
"""
import math
import os

from PIL import ImageFont

from .ortak import FONT_DIR, e, svg, tr_title

# ---------------------------------------------------------------- süsler (SVG; renkler CSS değişkeniyle)


def _p(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def cicek(cx, cy, r, n=5, yaprak="var(--fl)", gobek="var(--fl2)", aci=-90.0, en=0.62):
    """Yapraklı çiçek: n elips taç yaprak ve göbek."""
    out = []
    for k in range(n):
        a = aci + k * 360.0 / n
        x, y = cx + r * 0.52 * math.cos(math.radians(a)), cy + r * 0.52 * math.sin(math.radians(a))
        out.append(f'<ellipse cx="{_p(x)}" cy="{_p(y)}" rx="{_p(r * 0.46)}" ry="{_p(r * en / 2)}" '
                   f'transform="rotate({_p(a)} {_p(x)} {_p(y)})" fill="{yaprak}"/>')
    out.append(f'<circle cx="{_p(cx)}" cy="{_p(cy)}" r="{_p(r * 0.24)}" fill="{gobek}"/>')
    return "".join(out)


def papatya(cx, cy, r, n=14, yaprak="#fff", gobek="var(--sari)"):
    out = []
    for k in range(n):
        a = k * 360.0 / n
        x, y = cx + r * 0.6 * math.cos(math.radians(a)), cy + r * 0.6 * math.sin(math.radians(a))
        out.append(f'<ellipse cx="{_p(x)}" cy="{_p(y)}" rx="{_p(r * 0.4)}" ry="{_p(r * 0.13)}" '
                   f'transform="rotate({_p(a)} {_p(x)} {_p(y)})" fill="{yaprak}"/>')
    out.append(f'<circle cx="{_p(cx)}" cy="{_p(cy)}" r="{_p(r * 0.3)}" fill="{gobek}"/>')
    return "".join(out)


def yaprak(x, y, L, aci, renk="var(--lf)", en=0.42):
    """Sapı (x, y)'de, aci yönünde uzanan yaprak (iki yaydan)."""
    w = L * en
    return (f'<path d="M0 0Q{_p(w * 0.9)} {_p(-L * 0.5)} 0 {_p(-L)}Q{_p(-w * 0.9)} {_p(-L * 0.5)} 0 0Z" '
            f'transform="translate({_p(x)} {_p(y)}) rotate({_p(aci + 90)})" fill="{renk}"/>')


def dal(pts, yapraklar, L, renk="var(--lf)", en=1.6):
    """Kıvrık sap (noktalardan geçen eğri) ve iki yanında yapraklar: [(t, taraf)] t sap boyunca 0..1."""
    d = f"M{_p(pts[0][0])} {_p(pts[0][1])}"
    for i in range(1, len(pts) - 1, 2):
        d += f"Q{_p(pts[i][0])} {_p(pts[i][1])} {_p(pts[i + 1][0])} {_p(pts[i + 1][1])}"
    out = [f'<path d="{d}" fill="none" stroke="{renk}" stroke-width="{en}" stroke-linecap="round"/>']
    seg = [(pts[i], pts[i + 1], pts[i + 2]) for i in range(0, len(pts) - 2, 2)]
    for t, taraf in yapraklar:
        k = min(int(t * len(seg)), len(seg) - 1)
        u = t * len(seg) - k
        (x0, y0), (x1, y1), (x2, y2) = seg[k]
        x = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * x1 + u * u * x2
        y = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * y1 + u * u * y2
        tx, ty = 2 * (1 - u) * (x1 - x0) + 2 * u * (x2 - x1), 2 * (1 - u) * (y1 - y0) + 2 * u * (y2 - y1)
        out.append(yaprak(x, y, L, math.degrees(math.atan2(ty, tx)) + taraf * 48, renk))
    return "".join(out)


def sakayik(cx, cy, r, dolgu="#fff", cizgi="var(--fl)", ic="var(--fl3,#fde8ee)"):
    """Şakayık: üç kat yuvarlak taç yaprak (dışta beyaz, içe doğru pembeleşir; kenarları ince çizgi) ve göbek."""
    out, sw = [], _p(r * 0.025)
    for n, R, d, renk, faz in ((8, .40, .60, dolgu, 0), (6, .31, .36, dolgu, 18), (5, .22, .17, ic, 40)):
        for k in range(n):
            a = math.radians(faz + k * 360.0 / n)
            out.append(f'<circle cx="{_p(cx + r * d * math.cos(a))}" cy="{_p(cy + r * d * math.sin(a))}" '
                       f'r="{_p(r * R)}" fill="{renk}" stroke="{cizgi}" stroke-width="{sw}"/>')
    out.append(f'<circle cx="{_p(cx)}" cy="{_p(cy)}" r="{_p(r * 0.1)}" fill="{cizgi}"/>')
    return "".join(out)


def parilti(cx, cy, r, renk="currentColor", k=0.22):
    pts = [(0, -r), (r * k, -r * k), (r, 0), (r * k, r * k), (0, r), (-r * k, r * k), (-r, 0), (-r * k, -r * k)]
    return '<path d="M' + "L".join(f"{_p(cx + x)} {_p(cy + y)}" for x, y in pts) + f'Z" fill="{renk}"/>'


def kalp(cx, cy, w, renk="currentColor"):
    k = w / 32.0
    pts = [(16 * math.sin(a) ** 3, -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)))
           for a in [2 * math.pi * i / 48 for i in range(48)]]
    return '<path d="M' + "L".join(f"{_p(cx + x * k)} {_p(cy + y * k)}" for x, y in pts) + f'Z" fill="{renk}"/>'


def sv(cls, box, ic, aria=True):
    return f'<svg class="{cls}" viewBox="{box}"{" aria-hidden=" + chr(34) + "true" + chr(34) if aria else ""}>{ic}</svg>'


# ---------------------------------------------------------------- ad

def isim(site):
    """El yazısı ad: büyük harfle kayıtlı adın baş harfleri (DEFNE → Defne); iki kelimeli uzun adlar alt alta."""
    return [tr_title(t) for t in site.lines]


def sigdir(font, site, buyuk=False, ekstra=0.0):
    """Adın genişliğe sığması için em başına oran (CSS: font-size = kullanılabilir × oran)."""
    fn, tracking = font
    f = ImageFont.truetype(os.path.join(FONT_DIR, fn), 1000)
    lines = site.lines if buyuk else isim(site)
    w = max(f.getlength(t) / 1000 + tracking * (len(t) - 1) for t in lines) + ekstra
    return 0.97 / w


def d(t):
    return f' style="animation-delay:{t:.2f}s"'


# ---------------------------------------------------------------- bağlantılar, ödeme, alt şerit

def baglantilar(site, ctx):
    """Güzellikte WhatsApp randevu içindir: başlığı "Randevu al"."""
    out = []
    for L in site.links(vcf_href=ctx.vcf):
        if L.key == "whatsapp":
            L.title, L.sub, L.short = "Randevu al", "WhatsApp'tan yazın", "Randevu"
        out.append(L)
    return out


def a_attr(L):
    return f'href="{e(L.href)}"' + (f' download="{e(L.download)}"' if L.download else "")


def odeme(site, ctx, baslik="Ödeme bilgileri"):
    """IBAN kartı (kopyala, karekod). Kartvizitte IBAN yoksa boş."""
    if not site.iban:
        return ""
    who = "".join(f"<dt>{k}</dt><dd>{e(v)}</dd>" for k, v in (("Banka", site.banka), ("Alıcı", site.alici)) if v)
    kk_btn = kk_box = ""
    if ctx.kk:
        save = "" if ctx.standalone else f'\n      <a href="{ctx.kk}" download="{site.slug}-karekod.png">Karekodu kaydet</a>'
        kk_btn = (f'\n    <a class="btn ghost" href="#kk" data-toggle="kk" aria-controls="kk" aria-expanded="false">'
                  f'{svg("qr")}Karekod</a>')
        kk_box = f"""
  <div class="kk drop" id="kk">
    <span class="qr"><img src="{ctx.kk}" width="828" height="828" alt="Ödeme karekodu – {e(site.alici or site.isletme)}"></span>
    <p>Karekodu kaydedin, banka uygulamanızda <b>Karekod ile Öde</b>, ardından <b>Galeriden seç</b>.</p>{save}
  </div>"""
    note = '\n  <p class="note">Örnek IBAN: gerçek bilgiler eklenecek.</p>' if site.iban_ornek else ""
    return f"""<h2 class="sec">{e(baslik)}</h2>
<section class="pay" data-in aria-label="Ödeme bilgileri">
  {f'<dl class="rows">{who}</dl>' if who else ''}
  <div class="ibanbox"><span>IBAN</span><output class="iban">{e(site.iban_txt)}</output></div>
  <div class="acts{'' if ctx.kk else ' one'}">
    <button class="btn copy" type="button" data-copy="{e(site.iban)}" data-done="Kopyalandı">{svg("copy")}<span>{"Kopyala" if ctx.kk else "IBAN'ı kopyala"}</span></button>{kk_btn}
  </div>{kk_box}{note}
</section>"""


def alt_serit(site):
    return (f'<div class="callbar"><a href="tel:+{site.tel}" aria-label="Hemen ara">{svg("phone")}Hemen ara · '
            f'<span>{e(site.phone)}</span></a></div>')


# Ortak CSS: ödeme kartı, düğmeler, karekod, alt şerit, bildirim; renkler şablonun değişkenleriyle
# (--bg, --surface, --raise, --line, --line2, --text, --muted, --dim, --ok, --ui, --r: köşe).
BASE_CSS = """
*{box-sizing:border-box;margin:0}
html{background:var(--bg);-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--text);font:400 16px/1.5 var(--ui);min-height:100vh;overflow-x:hidden}
a{color:inherit;-webkit-tap-highlight-color:transparent}
button{font:inherit;color:inherit}
:focus-visible{outline:2px solid var(--ac);outline-offset:3px}
.wrap{max-width:480px;margin:0 auto;padding-left:max(20px,env(safe-area-inset-left,0px));
  padding-right:max(20px,env(safe-area-inset-right,0px));padding-block:0 calc(110px + env(safe-area-inset-bottom,0px))}
.sec{display:flex;align-items:center;gap:12px;margin:40px 0 14px;font:700 12px/1 var(--ui);letter-spacing:.28em;
  text-transform:uppercase;color:var(--muted)}
.sec::after{content:"";flex:1;height:1px;background:var(--line)}
.pay{padding:20px;border-radius:var(--r);background:var(--surface);border:1px solid var(--line);container-type:inline-size}
.rows{display:grid;grid-template-columns:auto 1fr;gap:10px 20px;font-size:15px;margin-bottom:16px}
.rows dt{color:var(--muted)}
.rows dd{font-weight:700;text-align:right;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ibanbox{padding:14px 16px 15px;border-radius:calc(var(--r) * .66);background:var(--raise);border:1px solid var(--line2)}
.ibanbox span{display:block;font:700 11px/1 var(--ui);letter-spacing:.3em;color:var(--dim)}
.iban{display:block;margin-top:8px;font:700 18px/1.2 var(--ui);font-size:min(19px,4.6cqi);letter-spacing:0;
  word-spacing:.05em;font-variant-numeric:tabular-nums;white-space:nowrap;user-select:all;-webkit-user-select:all}
.acts{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px}
.acts.one{grid-template-columns:1fr}
.btn{display:flex;align-items:center;justify-content:center;gap:9px;min-height:52px;border-radius:999px;cursor:pointer;
  font:700 15px/1 var(--ui);text-decoration:none;white-space:nowrap;transition:transform .15s,background .2s,border-color .2s}
.btn:active{transform:scale(.97)}
.btn .ic{width:19px;height:19px}
.copy{border:0;background:var(--ac);color:var(--ac-ink)}
.copy .ic{fill:var(--ac-ink)}
.copy.ok{background:var(--ok);color:#fff}
.copy.ok .ic{fill:#fff}
.ghost{border:1.5px solid var(--line2);background:transparent;color:var(--text)}
.ghost .ic{fill:var(--text)}
.ghost[aria-expanded="true"]{border-color:var(--ac);color:var(--ac)}
.ghost[aria-expanded="true"] .ic{fill:var(--ac)}
.kk{margin-top:12px;padding:18px 16px 14px;border-radius:calc(var(--r) * .8);background:var(--raise);
  border:1px solid var(--line);text-align:center}
.kk .qr{display:inline-block;padding:12px;border-radius:12px;background:#fff}
.kk img{display:block;width:min(220px,58vw);height:auto;image-rendering:pixelated}
.kk p{margin:12px 4px 8px;font-size:14px;color:var(--muted)}
.kk p b{color:var(--text)}
.kk a{color:var(--ac);font-weight:700;text-underline-offset:3px}
.note{margin-top:12px;font-size:12px;color:var(--dim);text-align:center}
.callbar{position:fixed;z-index:20;left:0;right:0;bottom:0;display:flex;justify-content:center;
  padding:12px max(16px,env(safe-area-inset-right,0px)) calc(12px + env(safe-area-inset-bottom,0px)) max(16px,env(safe-area-inset-left,0px));
  background:var(--bar);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);border-top:1px solid var(--line);
  transform:translateY(110%);transition:transform .35s cubic-bezier(.2,.8,.2,1)}
.callbar.show{transform:none}
.callbar a{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;max-width:440px;min-height:52px;
  border-radius:999px;background:var(--ac);color:var(--ac-ink);text-decoration:none;font:700 16px/1 var(--ui)}
.callbar .ic{width:20px;height:20px;fill:var(--ac-ink)}
.callbar span{font-variant-numeric:tabular-nums}
.toast{position:fixed;z-index:30;left:50%;bottom:calc(92px + env(safe-area-inset-bottom));transform:translate(-50%,40px);
  width:max-content;max-width:calc(100vw - 32px);text-align:center;background:var(--surface);color:var(--text);
  border:1px solid var(--line2);border-left:4px solid var(--ac);padding:12px 18px;border-radius:14px;font-weight:600;
  box-shadow:0 14px 34px rgba(0,0,0,.18);transition:transform .25s,opacity .25s;opacity:0;pointer-events:none}
.toast.show{transform:translate(-50%,0);opacity:1}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes write{from{clip-path:inset(-20% 100% -30% -6%)}to{clip-path:inset(-20% -6% -30% -6%)}}
@keyframes bloom{from{opacity:0;transform:scale(.4) rotate(-40deg)}to{opacity:1;transform:none}}
@keyframes track{from{letter-spacing:.8em;opacity:0}to{opacity:1}}
@keyframes flash{0%{color:var(--ac)}100%{color:var(--text)}}
@keyframes open{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}
.pay.in .iban{animation:flash 1.2s .2s ease-out}
.iban.flash{animation:flash .9s ease-out}
.kk.on,.kk:target{animation:open .35s cubic-bezier(.2,.8,.2,1)}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
"""
