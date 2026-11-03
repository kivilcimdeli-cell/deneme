"""Şablon 10 · Papatya – güzellik: canlı renkli dalgalı başlık, beyaz papatyalar, yuvarlak el yazısı ad, beyaz kartlar.

Neşeli, dikkat çekici kuaför ve güzellik merkezleri için (güzellik koleksiyonu; örnek: Papatya Kuaför & Güzellik).
Baştan sona vurgu renginde başlık (altı dalgalı), içinde sarı göbekli beyaz papatyalar (açarak gelir), ortada beyaz
yuvarlak el yazısıyla ad (Pacifico; yazılır gibi açılır), sarı hizmet; açık zeminde sarı Hemen Ara, bağlantılar beyaz
kartlarda (simge balonları vurgu ve sarı sırayla), ödeme kartı, altta papatyayla imza.
"""
from . import g_ortak as G
from .ortak import DRAW_CSS, drawn_mark, e, svg

NO, AD, SLUG = 10, "Papatya", "papatya"
KAYNAK = "güzellik (Papatya Kuaför & Güzellik)"
RENK, BG = "#de347c", "#fff7fa"
FONTS = {"ad": ("Pacifico-Regular.ttf", "Pacifico", 400, "normal"),
         "baslik": ("Quicksand-Bold.ttf", "Quicksand", 700, "normal"),
         "text": ("Figtree_400Regular.ttf", "Figtree", 400, "normal"),
         "text-sb": ("Figtree_600SemiBold.ttf", "Figtree", 600, "normal"),
         "text-xb": ("Figtree_800ExtraBold.ttf", "Figtree", 800, "normal")}
LICENSES = ("OFL-pacifico.txt", "OFL-quicksand.txt", "OFL-figtree.txt")
MARK_FONT = ("Pacifico-Regular.ttf", 0.0)
MARK = ".mark .ln"
FITS = ".iban,.call b,.card b,.card small,.rows dd,.btn,.eyebrow,.kind"
INTRO_MS = 2600
ORNEK = ("boyde_labs/guzellik/siteler/papatya", {})
ARROW = "M9 6l6 6-6 6"
# köşelerdeki papatyalar: (yer, genişlik px); yazıların üstüne gelmez
PAPATYALAR = (("left:-16px;top:16px", 66), ("left:48px;top:-8px", 30), ("right:-14px;top:10px", 58),
              ("right:46px;top:58px", 24), ("left:12px;bottom:34px", 30), ("right:18px;bottom:40px", 38))


def favicon(site):
    c = site.renk or RENK
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='16' "
            f"fill='{c}'/>{G.papatya(32, 32, 26, gobek='#ffd84d')}</svg>")


CSS = """
:root{color-scheme:light;--bg:#fff7fa;--surface:#fff;--raise:#fff0f5;--line:#f8dfe8;--line2:#efc6d5;
  --text:#3a1626;--muted:#8f6676;--dim:#bb98a6;--ok:#2f9e6a;--r:24px;--bar:rgba(255,247,250,.88);
  --sari:#ffd84d;--sari-ink:#3a2a00;
  --ui:"Figtree",system-ui,-apple-system,"Segoe UI",sans-serif;--round:"Quicksand",var(--ui)}
.top{position:relative;isolation:isolate;margin-inline:calc(-1 * max(20px,env(safe-area-inset-left,0px)));
  padding:40px 24px 74px;background:var(--ac);color:var(--ac-ink);text-align:center;overflow:hidden;
  --avail:calc(min(100vw,480px) - 56px)}
.top .wave{position:absolute;left:0;right:0;bottom:-1px;width:100%;height:44px;fill:var(--bg)}
.top .dz{position:absolute;z-index:-1;height:auto;animation:bloom .8s cubic-bezier(.2,.9,.3,1.2) both}
.eyebrow{display:inline-block;padding:7px 14px;border-radius:999px;background:rgba(255,255,255,.18);
  font:700 11.5px/1.3 var(--round);letter-spacing:.18em}
.own{display:block;height:50px;width:auto;margin:18px auto 0;fill:#fff;color:#fff;overflow:visible}
.mark{display:flex;flex-direction:column;align-items:center;margin-top:6px;color:#fff;
  font:400 min(clamp(56px,17vw,86px),calc(var(--avail) * var(--mk)))/1.35 "Pacifico",cursive;
  text-shadow:0 6px 0 rgba(0,0,0,.08)}
.mark .ln{display:block;width:max-content;padding-inline:.12em}
.kind{margin-top:16px;font:700 14px/1 var(--round);letter-spacing:.26em;padding-left:.26em;color:var(--sari);
  white-space:nowrap}
.lead{margin:12px auto 0;max-width:30ch;font-size:15.5px;color:var(--ac-ink2)}
.call{position:relative;z-index:2;display:flex;align-items:center;gap:14px;margin-top:-30px;padding:12px 22px 12px 12px;
  border-radius:999px;background:var(--sari);color:var(--sari-ink);text-decoration:none;
  box-shadow:0 18px 34px -18px rgba(150,110,0,.7);transition:transform .15s}
.call:active{transform:scale(.985)}
.call .ib{flex:none;display:grid;place-items:center;width:52px;height:52px;border-radius:50%;background:#fff}
.call .ib .ic{width:23px;height:23px;fill:var(--ac)}
.call .t{flex:1;min-width:0}
.call small{display:block;font:700 11.5px/1 var(--round);letter-spacing:.22em;opacity:.75}
.call b{display:block;margin-top:7px;font:800 clamp(23px,6.8vw,28px)/1 var(--ui);font-variant-numeric:tabular-nums;
  white-space:nowrap}
.cards{display:grid;gap:12px;margin-top:16px}
.card{display:grid;grid-template-columns:48px minmax(0,1fr) 16px;align-items:center;gap:14px;padding:14px 16px;
  border-radius:var(--r);background:var(--surface);text-decoration:none;box-shadow:0 14px 30px -24px rgba(120,20,60,.45);
  transition:transform .15s}
.card:active{transform:scale(.985)}
.card .ib{display:grid;place-items:center;width:48px;height:48px;border-radius:16px;background:var(--ac)}
.card .ic{width:22px;height:22px;fill:var(--ac-ink)}
.card:nth-child(even) .ib{background:var(--sari)}
.card:nth-child(even) .ic{fill:var(--sari-ink)}
.card b{display:block;font:700 16px/1.25 var(--ui);white-space:nowrap}
.card small{display:block;margin-top:2px;font-size:13.5px;line-height:1.3;color:var(--muted);overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
.card .go{width:16px;height:16px;fill:none;stroke:var(--ac);stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}
.sec{font-family:var(--round);color:var(--ac)}
.pay{border:2px dashed var(--line2)}
footer{margin-top:46px;text-align:center;color:var(--dim);font-size:13px}
footer svg{width:44px;height:44px}
footer b{display:block;margin:2px 0 10px;font:400 30px/1.5 "Pacifico",cursive;color:var(--ac)}
.eyebrow{animation:fade .6s .1s both}
.mark .ln{animation:write 1.1s cubic-bezier(.45,.05,.3,1) both}
.kind{animation:track .9s cubic-bezier(.2,.8,.2,1) both}
.lead{animation:fade .7s both}
.call{animation:rise .6s cubic-bezier(.2,.8,.2,1) both}
.card{animation:rise .5s cubic-bezier(.2,.8,.2,1) both}
""" + G.BASE_CSS + DRAW_CSS

OG_CSS = """
body.og{margin:0;width:1200px;height:630px;overflow:hidden;background:var(--ac)}
.og .wrap{max-width:none;padding:0}.og .top{margin:0;height:630px;padding:110px 100px 0;--avail:1000px}
.og .eyebrow{font-size:22px;padding:12px 24px}.og .mark{font-size:min(160px,calc(1000px * var(--mk)))}
.og .kind{font-size:28px}.og .wave{display:none}
"""


def css(site):
    return CSS + f":root{{--mk:{G.sigdir(MARK_FONT, site, ekstra=0.26):.4f}}}\n"


def _ad(site, t0):
    return "".join(f'<span class="ln"{G.d(t0 + .25 * k)}>{e(t)}</span>' for k, t in enumerate(G.isim(site)))


def _papatyalar():
    return "".join(f'<svg class="dz" viewBox="0 0 40 40" style="{yer};width:{w}px;animation-delay:{.15 + .12 * k:.2f}s" '
                   f'aria-hidden="true">{G.papatya(20, 20, 19)}</svg>' for k, (yer, w) in enumerate(PAPATYALAR))


def _dalga():
    return ('<svg class="wave" viewBox="0 0 390 44" preserveAspectRatio="none" aria-hidden="true"><path d="M0 26C48 '
            '6 98 6 146 22S244 44 292 28 362 6 390 18V44H0Z"/></svg>')


def og(site):
    return (f'<div class="wrap"><header class="top">{_papatyalar()}<p class="eyebrow">{e(site.etiket)}</p>'
            f'<h1 class="mark">{_ad(site, 0)}</h1><p class="kind">{e(site.hizmet)}</p></header></div>')


def body(site, ctx):
    logo, _ = drawn_mark(site, "own", 0.4)
    base = 0.3 if site.isaret else 0.0
    go = f'<svg class="go" viewBox="0 0 24 24" aria-hidden="true"><path d="{ARROW}"/></svg>'
    cards = "\n  ".join(f'<a class="card" {G.a_attr(L)}{G.d(1.5 + base + .07 * k)}><span class="ib">{svg(L.icon)}'
                        f'</span><span><b>{e(L.title)}</b><small>{e(L.sub)}</small></span>{go}</a>'
                        for k, L in enumerate(G.baglantilar(site, ctx)))
    right = f"@{site.instagram}" if site.instagram else e(site.etiket)
    mini = G.sv("", "0 0 44 44", G.papatya(22, 22, 20, yaprak="#fff", gobek="var(--sari)").replace(
        'fill="#fff"', 'fill="#fff" stroke="var(--line2)" stroke-width="1"'))
    return f"""<div class="wrap">
<header class="top">
  {_papatyalar()}
  <p class="eyebrow">{e(site.etiket)}</p>{logo}
  <h1 class="mark" aria-label="{e(site.isletme)}">{_ad(site, .5 + base)}</h1>
  <p class="kind"{G.d(1.0 + base)}>{e(site.hizmet)}</p>
  <p class="lead"{G.d(1.15 + base)}>{e(site.aciklama)}</p>
  {_dalga()}
</header>
<main>
<a class="call" href="tel:+{site.tel}"{G.d(1.3 + base)}><span class="ib">{svg("phone")}</span>
  <span class="t"><small>RANDEVU · HEMEN ARA</small><b>{e(site.phone)}</b></span></a>
<nav class="cards" aria-label="Bağlantılar">
  {cards}
</nav>
{G.odeme(site, ctx)}
</main>
<footer>{mini}<b>{e(" ".join(G.isim(site)))}</b><span>{right}</span></footer>
</div>
{G.alt_serit(site)}"""


JS = ""
