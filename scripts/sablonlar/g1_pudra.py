"""Şablon 6 · Pudra – güzellik: açık pudra zemin, köşelerde çiçekli dallar, ortalı el yazısı ad.

Kuaför ve güzellik salonları için (güzellik koleksiyonu; örnek: Defne Kuaför). Krem-pudra zemin, iki üst köşede
pembe çiçekli ve adaçayı yapraklı dal (çiçekler açarak gelir), ortada logo, el yazısıyla ad (Dancing Script; yazılır
gibi soldan açılır), harf aralıklı hizmet, açıklama; yuvarlak Hemen Ara, bağlantılar beyaz kartta liste, ödeme kartı,
altta küçük çiçekle imza.
"""
from . import g_ortak as G
from .ortak import DRAW_CSS, drawn_mark, e, svg

NO, AD, SLUG = 6, "Pudra", "pudra"
KAYNAK = "güzellik (Defne Kuaför)"
RENK, BG = "#c2607a", "#fbf5f2"
FONTS = {"ad": ("DancingScript-Bold.ttf", "Dancing Script", 700, "normal"),
         "baslik": ("JosefinSans-SemiBold.ttf", "Josefin Sans", 600, "normal"),
         "text": ("Figtree_400Regular.ttf", "Figtree", 400, "normal"),
         "text-sb": ("Figtree_600SemiBold.ttf", "Figtree", 600, "normal"),
         "text-xb": ("Figtree_800ExtraBold.ttf", "Figtree", 800, "normal")}
LICENSES = ("OFL-dancingscript.txt", "OFL-josefinsans.txt", "OFL-figtree.txt")
MARK_FONT = ("DancingScript-Bold.ttf", 0.0)
MARK = ".mark .ln"
FITS = ".iban,.call b,.row b,.row small,.rows dd,.btn,.eyebrow,.kind"
INTRO_MS = 2600
ORNEK = ("boyde_labs/guzellik/siteler/defne", {})
ARROW = "M9 6l6 6-6 6"


def _dal(ters=False):
    ic = G.dal([(4, 8), (40, 30), (70, 44), (100, 58), (136, 60)], [(.2, 1), (.38, -1), (.56, 1), (.74, -1), (.9, 1)],
               15)
    cic = "".join(f'<g class="fl"{G.d(.25 + .18 * k)}>{G.cicek(x, y, r)}</g>'
                  for k, (x, y, r) in enumerate(((22, 16, 13), (74, 40, 10), (128, 58, 12))))
    return G.sv("dal" + (" sag" if ters else ""), "0 0 150 80", ic + cic)


def favicon(site):
    c = site.renk or RENK
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='32' "
            f"fill='#fbf5f2'/>{G.cicek(32, 32, 26, yaprak=c, gobek='#fbf5f2')}</svg>")


CSS = """
:root{color-scheme:light;--bg:#fbf5f2;--surface:#fff;--raise:#fdf1f1;--line:#f1e1e1;--line2:#e9cfd3;
  --text:#3b2230;--muted:#8d7380;--dim:#b49aa6;--ok:#2f9e6a;--r:22px;--bar:rgba(251,245,242,.86);
  --fl:#f3b8c7;--fl2:var(--ac);--lf:#a9bea2;--name:color-mix(in srgb,var(--ac) 52%,#2b0e1f);
  --ui:"Figtree",system-ui,-apple-system,"Segoe UI",sans-serif;--caps:"Josefin Sans",var(--ui)}
.hero{position:relative;isolation:isolate;padding-block:30px 26px;text-align:center;
  --avail:calc(min(100vw,480px) - 52px)}
.hero::before{content:"";position:absolute;z-index:-1;inset:-30px -20px 0;pointer-events:none;
  background:radial-gradient(80% 55% at 50% 0%,rgba(var(--ac-rgb),.14),transparent 72%)}
.dal{position:absolute;top:4px;left:-12px;width:min(42vw,170px);height:auto;overflow:visible}
.dal.sag{left:auto;right:-12px;transform:scaleX(-1)}
.dal .fl{transform-box:fill-box;transform-origin:center;animation:bloom .7s cubic-bezier(.2,.9,.3,1.2) both}
.eyebrow{position:relative;margin-top:92px;font:600 11.5px/1 var(--caps);letter-spacing:.26em;color:var(--muted);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.own{display:block;height:52px;width:auto;margin:18px auto 0;fill:var(--ac);color:var(--ac);overflow:visible}
.mark{display:flex;flex-direction:column;align-items:center;margin-top:10px;color:var(--name);
  font:700 min(clamp(64px,21vw,104px),calc(var(--avail) * var(--mk)))/1.05 "Dancing Script",cursive}
.mark .ln{display:block;width:max-content;padding-inline:.06em}
.kind{margin-top:12px;font:600 14px/1 var(--caps);letter-spacing:.42em;color:var(--ac);white-space:nowrap;
  padding-left:.42em}
.lead{margin:14px auto 0;max-width:30ch;color:var(--muted);font-size:15.5px}
.call{display:flex;align-items:center;gap:14px;margin-top:6px;padding:12px 22px 12px 12px;border-radius:999px;
  background:var(--ac);color:var(--ac-ink);text-decoration:none;box-shadow:0 18px 36px -20px rgba(var(--ac-rgb),.8);
  transition:transform .15s}
.call:active{transform:scale(.985)}
.call .ib{flex:none;display:grid;place-items:center;width:52px;height:52px;border-radius:50%;background:#fff}
.call .ib .ic{width:23px;height:23px;fill:var(--ac)}
.call .t{flex:1;min-width:0}
.call small{display:block;font:600 11.5px/1 var(--caps);letter-spacing:.24em;opacity:.8}
.call b{display:block;margin-top:7px;font:800 clamp(23px,6.8vw,28px)/1 var(--ui);font-variant-numeric:tabular-nums;
  white-space:nowrap}
.list{margin-top:14px;border-radius:var(--r);background:var(--surface);border:1px solid var(--line);overflow:hidden;
  box-shadow:0 20px 40px -32px rgba(90,30,60,.35)}
.row{position:relative;display:grid;grid-template-columns:44px minmax(0,1fr) 16px;align-items:center;gap:14px;
  padding:14px 16px;text-decoration:none;transition:background .15s}
.row+.row::before{content:"";position:absolute;left:74px;right:16px;top:0;height:1px;background:var(--line)}
.row:active{background:var(--raise)}
.row .ib{display:grid;place-items:center;width:44px;height:44px;border-radius:50%;background:rgba(var(--ac-rgb),.12)}
.row .ic{width:21px;height:21px;fill:var(--ac)}
.row b{display:block;font:700 16px/1.25 var(--ui);white-space:nowrap}
.row small{display:-webkit-box;margin-top:2px;font-size:13.5px;line-height:1.3;color:var(--muted);overflow:hidden;
  -webkit-line-clamp:2;-webkit-box-orient:vertical;overflow-wrap:anywhere}
.row .go{width:16px;height:16px;fill:none;stroke:var(--dim);stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
.pay{border-top:3px solid rgba(var(--ac-rgb),.35)}
footer{margin-top:46px;text-align:center;color:var(--dim);font-size:13px}
footer .imza{display:block;font:700 34px/1.1 "Dancing Script",cursive;color:var(--name)}
footer svg{width:34px;height:34px;margin-bottom:6px}
.eyebrow{animation:fade .6s .1s both}
.mark .ln{animation:write 1.1s cubic-bezier(.45,.05,.3,1) both}
.kind{animation:track .9s cubic-bezier(.2,.8,.2,1) both}
.lead{animation:fade .7s both}
.call{animation:rise .6s cubic-bezier(.2,.8,.2,1) both}
.row{animation:rise .5s cubic-bezier(.2,.8,.2,1) both}
""" + G.BASE_CSS + DRAW_CSS

OG_CSS = """
body.og{margin:0;width:1200px;height:630px;overflow:hidden}
.og .wrap{max-width:none;padding:0 100px}.og .hero{padding-block:40px 0;--avail:1000px}
.og .dal{width:330px;top:10px;left:10px}.og .dal.sag{left:auto;right:10px}
.og .eyebrow{margin-top:150px;font-size:22px}.og .mark{font-size:min(170px,calc(1000px * var(--mk)))}
.og .kind{font-size:26px;margin-top:22px}
"""


def css(site):
    return CSS + f":root{{--mk:{G.sigdir(MARK_FONT, site, ekstra=0.12):.4f}}}\n"


def _ad(site, t0):
    return "".join(f'<span class="ln"{G.d(t0 + .25 * k)}>{e(t)}</span>' for k, t in enumerate(G.isim(site)))


def og(site):
    return (f'<div class="wrap"><header class="hero">{_dal()}{_dal(True)}<p class="eyebrow">{e(site.etiket)}</p>'
            f'<h1 class="mark">{_ad(site, 0)}</h1><p class="kind">{e(site.hizmet)}</p></header></div>')


def body(site, ctx):
    logo, _ = drawn_mark(site, "own", 0.5)
    base = 0.35 if site.isaret else 0.0
    go = f'<svg class="go" viewBox="0 0 24 24" aria-hidden="true"><path d="{ARROW}"/></svg>'
    rows = "\n  ".join(f'<a class="row" {G.a_attr(L)}{G.d(1.5 + base + .07 * k)}><span class="ib">{svg(L.icon)}'
                       f'</span><span><b>{e(L.title)}</b><small>{e(L.sub)}</small></span>{go}</a>'
                       for k, L in enumerate(G.baglantilar(site, ctx)))
    right = f"@{site.instagram}" if site.instagram else e(site.etiket)
    cicek = G.sv("", "0 0 40 40", G.cicek(20, 20, 17))
    return f"""<div class="wrap">
<header class="hero">
  {_dal()}{_dal(True)}
  <p class="eyebrow">{e(site.etiket)}</p>{logo}
  <h1 class="mark" aria-label="{e(site.isletme)}">{_ad(site, .45 + base)}</h1>
  <p class="kind"{G.d(1.0 + base)}>{e(site.hizmet)}</p>
  <p class="lead"{G.d(1.2 + base)}>{e(site.aciklama)}</p>
</header>
<main>
<a class="call" href="tel:+{site.tel}"{G.d(1.35 + base)}><span class="ib">{svg("phone")}</span>
  <span class="t"><small>RANDEVU · HEMEN ARA</small><b>{e(site.phone)}</b></span></a>
<nav class="list" aria-label="Bağlantılar">
  {rows}
</nav>
{G.odeme(site, ctx)}
</main>
<footer>{cicek}<span class="imza">{e(" ".join(G.isim(site)))}</span><span>{right}</span></footer>
</div>
{G.alt_serit(site)}"""


JS = ""
