"""Şablon 8 · Gece – güzellik: koyu zemin, rose gold el yazısı ad, parıltılar, ince altın çerçeveli satırlar.

Kirpik ve kaş stüdyoları, makyaj ve lüks güzellik için (güzellik koleksiyonu; örnek: Ela Lash & Brow). Siyaha yakın
sıcak zemin; ortada logo (rose gold, çizilerek gelir), vurgu renginden türeyen rose gold geçişli el yazısı ad
(Yesteryear; yazılır gibi açılır, üstünden ışık geçer), yanlarında parıltılar, iki yanı çizgili hizmet; rose gold
Hemen Ara, bağlantılar ince altın çerçeveli ayrı satırlar, koyu ödeme kartı.
"""
from . import g_ortak as G
from .ortak import DRAW_CSS, drawn_mark, e, svg

NO, AD, SLUG = 8, "Gece", "gece"
KAYNAK = "güzellik (Ela Lash & Brow)"
RENK, BG = "#d99a88", "#120e10"
FONTS = {"ad": ("Yesteryear-Regular.ttf", "Yesteryear", 400, "normal"),
         "baslik": ("Marcellus-Regular.ttf", "Marcellus", 400, "normal"),
         "text": ("Figtree_400Regular.ttf", "Figtree", 400, "normal"),
         "text-sb": ("Figtree_600SemiBold.ttf", "Figtree", 600, "normal"),
         "text-xb": ("Figtree_800ExtraBold.ttf", "Figtree", 800, "normal")}
LICENSES = ("OFL-yesteryear.txt", "OFL-marcellus.txt", "OFL-figtree.txt")
MARK_FONT = ("Yesteryear-Regular.ttf", 0.0)
MARK = ".mark .ln"
FITS = ".iban,.call b,.row b,.row small,.rows dd,.btn,.eyebrow,.kind span"
INTRO_MS = 2800
ORNEK = ("boyde_labs/guzellik/siteler/ela", {})
ARROW = "M9 6l6 6-6 6"


def favicon(site):
    c = site.renk or RENK
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='16' "
            f"fill='#120e10'/>{G.parilti(32, 32, 22, c)}</svg>")


CSS = """
:root{color-scheme:dark;--bg:#120e10;--surface:#1b1517;--raise:#231b1e;--line:#33282c;--line2:#4a3a3f;
  --text:#f6ece8;--muted:#b49f99;--dim:#7c6a66;--ok:#3fae7a;--r:20px;--bar:rgba(18,14,16,.86);
  --g1:color-mix(in srgb,var(--ac) 60%,#fff3ec);--g2:var(--ac);--g3:color-mix(in srgb,var(--ac) 70%,#5a2d22);
  --gold:linear-gradient(115deg,var(--g3) 0%,var(--g1) 28%,var(--g2) 52%,var(--g1) 74%,var(--g3) 100%);
  --ui:"Figtree",system-ui,-apple-system,"Segoe UI",sans-serif;--caps:"Marcellus",Georgia,serif}
.hero{position:relative;isolation:isolate;padding-block:46px 30px;text-align:center;
  --avail:calc(min(100vw,480px) - 64px)}
.hero::before{content:"";position:absolute;z-index:-1;inset:-46px -20px 0;pointer-events:none;
  background:radial-gradient(60% 45% at 50% 30%,rgba(var(--ac-rgb),.16),transparent 70%)}
.eyebrow{font:400 12.5px/1.3 var(--caps);letter-spacing:.24em;color:var(--muted)}
.own{display:block;height:58px;width:auto;margin:24px auto 0;fill:var(--g1);color:var(--g1);overflow:visible;
  filter:drop-shadow(0 6px 18px rgba(var(--ac-rgb),.35))}
.namewrap{position:relative;display:flex;justify-content:center;margin-top:8px}
.sp{position:absolute;width:22px;height:22px;color:var(--g1);animation:twinkle 3.6s ease-in-out infinite}
.sp.a{left:2%;top:18%}.sp.b{right:4%;top:6%;width:15px;height:15px;animation-delay:1.2s}
.sp.c{right:10%;bottom:4%;width:12px;height:12px;animation-delay:2.1s}
.mark{display:flex;flex-direction:column;align-items:center;
  font:400 min(clamp(68px,22vw,110px),calc(var(--avail) * var(--mk)))/1.12 "Yesteryear",cursive}
.mark .ln{display:block;width:max-content;padding-inline:.1em;background:var(--gold);background-size:220% 100%;
  -webkit-background-clip:text;background-clip:text;color:transparent}
.kind{display:flex;align-items:center;justify-content:center;gap:14px;margin-top:10px}
.kind::before,.kind::after{content:"";width:34px;height:1px;background:var(--gold)}
.kind span{font:400 15px/1 var(--caps);letter-spacing:.34em;padding-left:.34em;color:var(--g1);white-space:nowrap}
.lead{margin:16px auto 0;max-width:30ch;color:var(--muted);font-size:15.5px}
.call{display:flex;align-items:center;gap:14px;padding:16px 18px 16px 22px;border-radius:var(--r);
  background:var(--gold);background-size:200% 100%;color:#2a1510;text-decoration:none;
  box-shadow:0 22px 44px -26px rgba(var(--ac-rgb),.9);transition:transform .15s}
.call:active{transform:scale(.985)}
.call .t{flex:1;min-width:0}
.call small{display:block;font:400 12px/1 var(--caps);letter-spacing:.26em;opacity:.8}
.call b{display:block;margin-top:8px;font:800 clamp(24px,7.2vw,30px)/1 var(--ui);font-variant-numeric:tabular-nums;
  white-space:nowrap}
.call .ib{flex:none;display:grid;place-items:center;width:50px;height:50px;border-radius:50%;background:#1a1012}
.call .ib .ic{width:23px;height:23px;fill:var(--g1)}
.list{display:grid;gap:10px;margin-top:14px}
.row{position:relative;display:grid;grid-template-columns:42px minmax(0,1fr) 16px;align-items:center;gap:14px;
  padding:13px 16px;border-radius:16px;background:var(--surface);text-decoration:none;
  border:1px solid transparent;background:linear-gradient(var(--surface),var(--surface)) padding-box,
  linear-gradient(120deg,rgba(var(--ac-rgb),.55),rgba(var(--ac-rgb),.12) 40%,rgba(var(--ac-rgb),.45)) border-box;
  transition:transform .15s}
.row:active{transform:scale(.985)}
.row .ib{display:grid;place-items:center;width:42px;height:42px;border-radius:50%;border:1px solid rgba(var(--ac-rgb),.45)}
.row .ic{width:20px;height:20px;fill:var(--g1)}
.row b{display:block;font:700 16px/1.25 var(--ui);white-space:nowrap}
.row small{display:block;margin-top:2px;font-size:13.5px;line-height:1.3;color:var(--muted);overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
.row .go{width:16px;height:16px;fill:none;stroke:var(--g2);stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.sec{font-family:var(--caps);font-weight:400;letter-spacing:.3em;color:var(--g1)}
.sec::after{background:linear-gradient(90deg,rgba(var(--ac-rgb),.5),transparent)}
.pay{border-color:rgba(var(--ac-rgb),.3)}
.copy{background:var(--gold);background-size:200% 100%;color:#2a1510}.copy .ic{fill:#2a1510}
footer{margin-top:48px;text-align:center;color:var(--dim);font-size:13px}
footer b{display:block;font:400 40px/1.1 "Yesteryear",cursive;background:var(--gold);-webkit-background-clip:text;
  background-clip:text;color:transparent}
@keyframes twinkle{0%,100%{opacity:.25;transform:scale(.7) rotate(0)}50%{opacity:1;transform:scale(1) rotate(45deg)}}
@keyframes sheen{0%,70%{background-position:100% 0}100%{background-position:0 0}}
.eyebrow{animation:fade .6s .1s both}
.mark .ln{animation:write 1.2s cubic-bezier(.45,.05,.3,1) both,sheen 6s 2.6s ease-in-out infinite}
.kind{animation:fade .8s both}
.lead{animation:fade .7s both}
.call{animation:rise .6s cubic-bezier(.2,.8,.2,1) both,sheen 6s 3s ease-in-out infinite}
.row{animation:rise .5s cubic-bezier(.2,.8,.2,1) both}
""" + G.BASE_CSS + DRAW_CSS

OG_CSS = """
body.og{margin:0;width:1200px;height:630px;overflow:hidden}
.og .wrap{max-width:none;padding:0 100px}.og .hero{padding-block:70px 0;--avail:900px}
.og .eyebrow{font-size:24px}.og .mark{font-size:min(190px,calc(900px * var(--mk)))}
.og .kind span{font-size:28px}.og .kind::before,.og .kind::after{width:80px}.og .sp{width:44px;height:44px}
"""


def css(site):
    return CSS + f":root{{--mk:{G.sigdir(MARK_FONT, site, ekstra=0.2):.4f}}}\n"


def _ad(site, t0):
    return "".join(f'<span class="ln"{G.d(t0 + .25 * k)}>{e(t)}</span>' for k, t in enumerate(G.isim(site)))


def _isim(site, t0):
    sp = "".join(G.sv(f"sp {c}", "0 0 24 24", G.parilti(12, 12, 11)) for c in "abc")
    return f'<div class="namewrap">{sp}<h1 class="mark" aria-label="{e(site.isletme)}">{_ad(site, t0)}</h1></div>'


def og(site):
    return (f'<div class="wrap"><header class="hero"><p class="eyebrow">{e(site.etiket)}</p>{_isim(site, 0)}'
            f'<p class="kind"><span>{e(site.hizmet)}</span></p></header></div>')


def body(site, ctx):
    logo, _ = drawn_mark(site, "own", 0.3)
    base = 0.45 if site.isaret else 0.0
    go = f'<svg class="go" viewBox="0 0 24 24" aria-hidden="true"><path d="{ARROW}"/></svg>'
    rows = "\n  ".join(f'<a class="row" {G.a_attr(L)}{G.d(1.55 + base + .07 * k)}><span class="ib">{svg(L.icon)}'
                       f'</span><span><b>{e(L.title)}</b><small>{e(L.sub)}</small></span>{go}</a>'
                       for k, L in enumerate(G.baglantilar(site, ctx)))
    right = f"@{site.instagram}" if site.instagram else e(site.etiket)
    return f"""<div class="wrap">
<header class="hero">
  <p class="eyebrow">{e(site.etiket)}</p>{logo}
  {_isim(site, .4 + base)}
  <p class="kind"{G.d(1.1 + base)}><span>{e(site.hizmet)}</span></p>
  <p class="lead"{G.d(1.25 + base)}>{e(site.aciklama)}</p>
</header>
<main>
<a class="call" href="tel:+{site.tel}"{G.d(1.4 + base)}><span class="t"><small>RANDEVU · HEMEN ARA</small>
  <b>{e(site.phone)}</b></span><span class="ib">{svg("phone")}</span></a>
<nav class="list" aria-label="Bağlantılar">
  {rows}
</nav>
{G.odeme(site, ctx)}
</main>
<footer><b>{e(" ".join(G.isim(site)))}</b><span>{right}</span></footer>
</div>
{G.alt_serit(site)}"""


JS = ""
