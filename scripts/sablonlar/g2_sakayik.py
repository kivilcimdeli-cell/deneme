"""Şablon 7 · Şakayık – güzellik: pembe zemin, sağ üstte iri beyaz şakayık, sola yaslı eğik serif ad, kutucuklar.

Güzellik salonları için (güzellik koleksiyonu; örnek: Şakayık Güzellik Salonu). Vurgu renginin açık tonunda zemin;
başlıkta sağ üst köşeden taşan beyaz şakayık ve yaprakları (açarak gelir), sola yaslı Fraunces italik ad (yazılır gibi
açılır), koyu Hemen Ara kartı, bağlantılar iki sütun beyaz kutucuk, ödeme kartı, altta küçük şakayıkla imza.
"""
from . import g_ortak as G
from .ortak import DRAW_CSS, drawn_mark, e, svg

NO, AD, SLUG = 7, "Şakayık", "sakayik"
KAYNAK = "güzellik (Şakayık Güzellik)"
RENK, BG = "#7a2850", "#f9e4e8"
FONTS = {"ad": ("Fraunces-SemiBoldItalic.ttf", "Fraunces", 600, "italic"),
         "text": ("Figtree_400Regular.ttf", "Figtree", 400, "normal"),
         "text-sb": ("Figtree_600SemiBold.ttf", "Figtree", 600, "normal"),
         "text-xb": ("Figtree_800ExtraBold.ttf", "Figtree", 800, "normal")}
LICENSES = ("OFL-fraunces.txt", "OFL-figtree.txt")
MARK_FONT = ("Fraunces-SemiBoldItalic.ttf", -0.01)
MARK = ".mark .ln"
FITS = ".iban,.call b,.tile b,.tile small,.rows dd,.btn,.eyebrow,.kind"
INTRO_MS = 2600
ORNEK = ("boyde_labs/guzellik/siteler/sakayik", {})


def _sakayik(cls="peony"):
    """Başlığın sağ üstünde, kenardan taşan şakayık (taşan kısım .deco'da kırpılır: yatay kaydırma olmasın)."""
    yap = "".join(G.yaprak(x, y, L, a, "var(--lf)") for x, y, L, a in
                  ((70, 150, 70, 160), (82, 176, 62, 125), (150, 182, 66, 75), (178, 150, 56, 40)))
    ic = G.sv(cls, "0 0 260 260", f'<g class="lv">{yap}</g><g class="pf">{G.sakayik(130, 110, 96)}</g>')
    return f'<div class="deco">{ic}</div>'


def favicon(site):
    c = site.renk or RENK
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='16' "
            f"fill='{c}'/>{G.sakayik(32, 32, 26, dolgu='#fff', cizgi=c)}</svg>")


CSS = """
:root{color-scheme:light;--bg:color-mix(in srgb,var(--ac) 9%,#fff4f6);--surface:#fff;
  --raise:color-mix(in srgb,var(--ac) 6%,#fff);--line:color-mix(in srgb,var(--ac) 14%,#fff);
  --line2:color-mix(in srgb,var(--ac) 26%,#fff);--text:#33141f;--muted:#866671;--dim:#ad929c;--ok:#2f9e6a;--r:24px;
  --bar:color-mix(in srgb,var(--ac) 9%,rgba(255,244,246,.86));--fl:color-mix(in srgb,var(--ac) 45%,#f6b9c8);
  --lf:#fff;--name:color-mix(in srgb,var(--ac) 80%,#1d0610);
  --ui:"Figtree",system-ui,-apple-system,"Segoe UI",sans-serif}
.hero{position:relative;isolation:isolate;padding-block:34px 26px;--avail:calc(min(100vw,480px) - 44px)}
.deco{position:absolute;z-index:-1;inset:0 -20px 0;overflow:hidden;pointer-events:none}
.peony{position:absolute;top:-34px;right:-54px;width:min(66vw,290px);height:auto;overflow:visible;
  filter:drop-shadow(0 16px 26px rgba(var(--ac-rgb),.18))}
.peony .pf{transform-box:fill-box;transform-origin:center;animation:bloom 1s cubic-bezier(.2,.9,.3,1.1) both}
.peony .lv{animation:fade .8s .5s both}
.eyebrow{display:inline-block;max-width:58%;padding:8px 13px;border-radius:14px;background:rgba(255,255,255,.72);
  font:700 11px/1.45 var(--ui);letter-spacing:.16em;color:var(--name)}
.own{display:block;height:44px;width:auto;margin-top:22px;fill:var(--name);color:var(--name);overflow:visible}
.mark{display:flex;flex-direction:column;margin-top:14px;color:var(--name);
  font:italic 600 min(clamp(56px,17vw,88px),calc(var(--avail) * var(--mk)))/1 "Fraunces",Georgia,serif;
  letter-spacing:-.01em}
.mark .ln{display:block;width:max-content;padding-right:.08em}
.kind{display:flex;align-items:center;gap:10px;margin-top:16px;font:800 13px/1 var(--ui);letter-spacing:.3em;
  color:var(--ac);white-space:nowrap}
.kind::before{content:"";width:26px;height:2px;border-radius:2px;background:var(--ac)}
.lead{margin-top:14px;max-width:30ch;color:var(--muted);font-size:15.5px}
.call{display:flex;align-items:center;gap:14px;padding:18px 18px 18px 22px;border-radius:var(--r);
  background:var(--name);color:#fff;text-decoration:none;box-shadow:0 22px 40px -24px rgba(var(--ac-rgb),.9);
  transition:transform .15s}
.call:active{transform:scale(.985)}
.call .t{flex:1;min-width:0}
.call small{display:block;font:800 11.5px/1 var(--ui);letter-spacing:.22em;color:var(--fl)}
.call b{display:block;margin-top:8px;font:800 clamp(24px,7.2vw,30px)/1 var(--ui);font-variant-numeric:tabular-nums;
  white-space:nowrap}
.call .ib{flex:none;display:grid;place-items:center;width:50px;height:50px;border-radius:50%;background:var(--fl)}
.call .ib .ic{width:23px;height:23px;fill:var(--name)}
.tiles{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}
.tile{display:flex;flex-direction:column;gap:12px;min-width:0;padding:16px;border-radius:var(--r);background:var(--surface);
  text-decoration:none;box-shadow:0 14px 30px -26px rgba(60,10,30,.5);transition:transform .15s}
.tile:active{transform:scale(.97)}
.tile:last-child:nth-child(odd){grid-column:span 2;flex-direction:row;align-items:center}
.tile .ib{display:grid;place-items:center;width:44px;height:44px;border-radius:50%;background:var(--raise);
  border:1px solid var(--line)}
.tile .ic{width:21px;height:21px;fill:var(--ac)}
.tile span:last-child{min-width:0}
.tile b{display:block;font:800 15.5px/1.2 var(--ui);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tile small{display:-webkit-box;margin-top:3px;font-size:13px;line-height:1.3;color:var(--muted);overflow:hidden;
  -webkit-line-clamp:2;-webkit-box-orient:vertical;overflow-wrap:break-word}
footer{display:flex;align-items:center;gap:12px;margin-top:44px;padding-top:18px;border-top:1px solid var(--line2);
  color:var(--dim);font-size:13px}
footer svg{width:42px;height:42px;flex:none}
footer b{flex:1;font:italic 600 22px/1 "Fraunces",Georgia,serif;color:var(--name)}
.eyebrow{animation:fade .6s .1s both}
.mark .ln{animation:write 1.1s cubic-bezier(.45,.05,.3,1) both}
.kind{animation:rise .6s both}
.lead{animation:fade .7s both}
.call{animation:rise .6s cubic-bezier(.2,.8,.2,1) both}
.tile{animation:rise .5s cubic-bezier(.2,.8,.2,1) both}
""" + G.BASE_CSS + DRAW_CSS

OG_CSS = """
body.og{margin:0;width:1200px;height:630px;overflow:hidden}
.og .wrap{max-width:none;padding:0 100px}.og .hero{padding-block:90px 0;--avail:760px}
.og .deco{inset:0 -100px 0}.og .peony{width:560px;top:-40px;right:-60px}.og .eyebrow{font-size:20px;padding:12px 20px}
.og .mark{font-size:min(160px,calc(760px * var(--mk)));margin-top:40px}.og .kind{font-size:24px;margin-top:30px}
"""


def css(site):
    return CSS + f":root{{--mk:{G.sigdir(MARK_FONT, site, ekstra=0.1):.4f}}}\n"


def _ad(site, t0):
    return "".join(f'<span class="ln"{G.d(t0 + .25 * k)}>{e(t)}</span>' for k, t in enumerate(G.isim(site)))


def _kir(L):
    """Dar kutucukta e-posta "@"tan sonra alta geçer (harf ortasından bölünmesin)."""
    return e(L.sub).replace("@", "@<wbr>") if L.key == "eposta" else e(L.sub)


def og(site):
    return (f'<div class="wrap"><header class="hero">{_sakayik()}<p class="eyebrow">{e(site.etiket)}</p>'
            f'<h1 class="mark">{_ad(site, 0)}</h1><p class="kind">{e(site.hizmet)}</p></header></div>')


def body(site, ctx):
    logo, _ = drawn_mark(site, "own", 0.4)
    base = 0.3 if site.isaret else 0.0
    tiles = "\n  ".join(f'<a class="tile" {G.a_attr(L)}{G.d(1.45 + base + .07 * k)}><span class="ib">'
                        f'{svg(L.icon)}</span><span><b>{e(L.title)}</b><small>{_kir(L)}</small></span></a>'
                        for k, L in enumerate(G.baglantilar(site, ctx)))
    right = f"@{site.instagram}" if site.instagram else ""
    mini = G.sv("", "0 0 60 60", G.sakayik(30, 30, 27, dolgu="#fff", cizgi="var(--fl)"))
    return f"""<div class="wrap">
<header class="hero">
  {_sakayik()}
  <p class="eyebrow">{e(site.etiket)}</p>{logo}
  <h1 class="mark" aria-label="{e(site.isletme)}">{_ad(site, .5 + base)}</h1>
  <p class="kind"{G.d(1.0 + base)}>{e(site.hizmet)}</p>
  <p class="lead"{G.d(1.15 + base)}>{e(site.aciklama)}</p>
</header>
<main>
<a class="call" href="tel:+{site.tel}"{G.d(1.3 + base)}><span class="t"><small>RANDEVU · HEMEN ARA</small>
  <b>{e(site.phone)}</b></span><span class="ib">{svg("phone")}</span></a>
<nav class="tiles" aria-label="Bağlantılar">
  {tiles}
</nav>
{G.odeme(site, ctx)}
</main>
<footer>{mini}<b>{e(" ".join(G.isim(site)))}</b><span>{right}</span></footer>
</div>
{G.alt_serit(site)}"""


JS = ""
