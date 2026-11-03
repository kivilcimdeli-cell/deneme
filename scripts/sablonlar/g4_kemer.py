"""Şablon 9 · Kemer – güzellik: ten rengi (nude) zemin, kemer biçimli çerçeve, fırça yazısıyla ad, kemer kutucuklar.

Tırnak stüdyoları, cilt bakım ve sade güzellik markaları için (güzellik koleksiyonu; örnek: Lâl Nails). Sıcak nude
zemin ve moka yazı; başlıkta kemer biçimli (üstü yarım daire) çerçevede logo ve parıltılar, kemerin altına taşan
fırça yazısıyla ad (Kaushan Script; yazılır gibi açılır), yuvarlak hatlı hizmet; vurgu renginde Hemen Ara,
bağlantılar üçerli kemer kutucuklar (simge ve kısa ad), ödeme kartı.
"""
from . import g_ortak as G
from .ortak import DRAW_CSS, drawn_mark, e, svg

NO, AD, SLUG = 9, "Kemer", "kemer"
KAYNAK = "güzellik (Lâl Nails)"
RENK, BG = "#c8326b", "#f4eae2"
FONTS = {"ad": ("KaushanScript-Regular.ttf", "Kaushan Script", 400, "normal"),
         "baslik": ("Quicksand-Bold.ttf", "Quicksand", 700, "normal"),
         "text": ("Figtree_400Regular.ttf", "Figtree", 400, "normal"),
         "text-sb": ("Figtree_600SemiBold.ttf", "Figtree", 600, "normal"),
         "text-xb": ("Figtree_800ExtraBold.ttf", "Figtree", 800, "normal")}
LICENSES = ("OFL-kaushanscript.txt", "OFL-quicksand.txt", "OFL-figtree.txt")
MARK_FONT = ("KaushanScript-Regular.ttf", 0.0)
MARK = ".mark .ln"
FITS = ".iban,.call b,.arch b,.rows dd,.btn,.eyebrow,.kind"
INTRO_MS = 2600
ORNEK = ("boyde_labs/guzellik/siteler/lal", {})


def favicon(site):
    c = site.renk or RENK
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><path d='M8 60V30a24 24 0 0 1 48 0v30Z' "
            f"fill='#e9d6c8'/>{G.parilti(32, 34, 14, c)}</svg>")


CSS = """
:root{color-scheme:light;--bg:#f4eae2;--surface:#fbf6f2;--raise:#efe1d6;--line:#e6d4c7;--line2:#d8c0b0;
  --text:#3e2a22;--muted:#8a7366;--dim:#b09888;--ok:#2f9e6a;--r:22px;--bar:rgba(244,234,226,.88);
  --arch:#e9d6c8;--moka:#3e2a22;
  --ui:"Figtree",system-ui,-apple-system,"Segoe UI",sans-serif;--round:"Quicksand",var(--ui)}
.hero{position:relative;padding-block:30px 26px;text-align:center;--avail:calc(min(100vw,480px) - 52px)}
.eyebrow{font:700 12px/1.3 var(--round);letter-spacing:.2em;color:var(--muted)}
.archf{position:relative;width:min(62vw,236px);aspect-ratio:4/5;margin:20px auto 0;border-radius:999px 999px 28px 28px;
  background:var(--arch);display:grid;place-items:center;
  box-shadow:inset 0 0 0 8px var(--bg),inset 0 0 0 9.5px var(--line2)}
.archf .own{height:42%;width:auto;fill:var(--ac);color:var(--ac);overflow:visible;margin-top:-8%}
.archf .sp{position:absolute;color:var(--ac);animation:twinkle 3.4s ease-in-out infinite}
.archf .sp.a{width:20px;height:20px;left:20%;top:24%}.archf .sp.b{width:13px;height:13px;right:22%;top:18%;
  animation-delay:1.1s}.archf .sp.c{width:16px;height:16px;right:16%;bottom:30%;animation-delay:2s}
.mark{position:relative;display:flex;flex-direction:column;align-items:center;margin-top:-.62em;color:var(--moka);
  font:400 min(clamp(62px,19vw,96px),calc(var(--avail) * var(--mk)))/1.1 "Kaushan Script",cursive}
.mark .ln{display:block;width:max-content;padding-inline:.12em}
.kind{margin-top:12px;font:700 14px/1 var(--round);letter-spacing:.32em;padding-left:.32em;color:var(--ac);
  white-space:nowrap}
.lead{margin:14px auto 0;max-width:30ch;color:var(--muted);font-size:15.5px}
.call{display:flex;align-items:center;gap:14px;margin-top:4px;padding:12px 22px 12px 12px;border-radius:999px;
  background:var(--moka);color:#fbf6f2;text-decoration:none;box-shadow:0 20px 40px -24px rgba(62,42,34,.8);
  transition:transform .15s}
.call:active{transform:scale(.985)}
.call .ib{flex:none;display:grid;place-items:center;width:52px;height:52px;border-radius:50%;background:var(--ac)}
.call .ib .ic{width:23px;height:23px;fill:var(--ac-ink)}
.call .t{flex:1;min-width:0}
.call small{display:block;font:700 11.5px/1 var(--round);letter-spacing:.24em;color:var(--dim)}
.call b{display:block;margin-top:7px;font:800 clamp(23px,6.8vw,28px)/1 var(--ui);font-variant-numeric:tabular-nums;
  white-space:nowrap}
.arches{display:flex;flex-wrap:wrap;justify-content:center;gap:12px;margin-top:16px}
.arch{flex:0 0 calc((100% - 24px) / 3);display:flex;flex-direction:column;align-items:center;gap:10px;min-width:0;
  padding:20px 6px 14px;border-radius:999px 999px 20px 20px;background:var(--surface);border:1px solid var(--line);
  text-decoration:none;text-align:center;transition:transform .15s,background .15s}
.arch:active{transform:scale(.96);background:var(--raise)}
.arch .ib{display:grid;place-items:center;width:46px;height:46px;border-radius:50%;background:rgba(var(--ac-rgb),.12)}
.arch .ic{width:22px;height:22px;fill:var(--ac)}
.arch b{display:block;max-width:100%;font:700 13px/1.2 var(--round);color:var(--text);white-space:nowrap}
.sec{font-family:var(--round)}
.pay{border-radius:28px}
footer{margin-top:46px;text-align:center;color:var(--dim);font-size:13px}
footer b{display:block;font:400 34px/1.15 "Kaushan Script",cursive;color:var(--moka)}
@keyframes twinkle{0%,100%{opacity:.3;transform:scale(.7)}50%{opacity:1;transform:scale(1)}}
@keyframes archin{from{opacity:0;transform:translateY(16px) scaleY(.9)}to{opacity:1;transform:none}}
.eyebrow{animation:fade .6s .1s both}
.archf{animation:archin .8s cubic-bezier(.2,.8,.2,1) .15s both;transform-origin:bottom}
.mark .ln{animation:write 1.1s cubic-bezier(.45,.05,.3,1) both}
.kind{animation:track .9s cubic-bezier(.2,.8,.2,1) both}
.lead{animation:fade .7s both}
.call{animation:rise .6s cubic-bezier(.2,.8,.2,1) both}
.arch{animation:rise .5s cubic-bezier(.2,.8,.2,1) both}
""" + G.BASE_CSS + DRAW_CSS

OG_CSS = """
body.og{margin:0;width:1200px;height:630px;overflow:hidden}
.og .wrap{max-width:none;padding:0 100px}.og .hero{display:grid;grid-template-columns:330px 1fr;align-items:center;
  gap:40px;padding-block:60px 0;text-align:left;--avail:640px}
.og .archf{width:330px;margin:0;grid-row:span 3}.og .eyebrow{display:none}
.og .mark{align-items:flex-start;margin-top:0;font-size:min(150px,calc(640px * var(--mk)))}
.og .kind{font-size:26px}
"""


def css(site):
    return CSS + f":root{{--mk:{G.sigdir(MARK_FONT, site, ekstra=0.24):.4f}}}\n"


def _ad(site, t0):
    return "".join(f'<span class="ln"{G.d(t0 + .25 * k)}>{e(t)}</span>' for k, t in enumerate(G.isim(site)))


def _kemer(site, logo):
    sp = "".join(G.sv(f"sp {c}", "0 0 24 24", G.parilti(12, 12, 11)) for c in "abc")
    if not logo:
        logo = G.sv("own", "0 0 40 40", G.cicek(20, 20, 18, yaprak="var(--ac)", gobek="var(--arch)"))
    return f'<div class="archf" aria-hidden="true">{sp}{logo}</div>'


def og(site):
    logo, _ = drawn_mark(site, "own")
    return (f'<div class="wrap"><header class="hero">{_kemer(site, logo)}<p class="eyebrow">{e(site.etiket)}</p>'
            f'<h1 class="mark">{_ad(site, 0)}</h1><p class="kind">{e(site.hizmet)}</p></header></div>')


def body(site, ctx):
    logo, _ = drawn_mark(site, "own", 0.5)
    base = 0.35 if site.isaret else 0.0
    arches = "\n  ".join(f'<a class="arch" {G.a_attr(L)} aria-label="{e(L.title)}: {e(L.sub)}"'
                         f'{G.d(1.5 + base + .07 * k)}><span class="ib">{svg(L.icon)}</span><b>{e(L.short)}</b></a>'
                         for k, L in enumerate(G.baglantilar(site, ctx)))
    right = f"@{site.instagram}" if site.instagram else e(site.etiket)
    return f"""<div class="wrap">
<header class="hero">
  <p class="eyebrow">{e(site.etiket)}</p>
  {_kemer(site, logo)}
  <h1 class="mark" aria-label="{e(site.isletme)}">{_ad(site, .65 + base)}</h1>
  <p class="kind"{G.d(1.05 + base)}>{e(site.hizmet)}</p>
  <p class="lead"{G.d(1.2 + base)}>{e(site.aciklama)}</p>
</header>
<main>
<a class="call" href="tel:+{site.tel}"{G.d(1.35 + base)}><span class="ib">{svg("phone")}</span>
  <span class="t"><small>RANDEVU · HEMEN ARA</small><b>{e(site.phone)}</b></span></a>
<nav class="arches" aria-label="Bağlantılar">
  {arches}
</nav>
{G.odeme(site, ctx)}
</main>
<footer><b>{e(" ".join(G.isim(site)))}</b><span>{right}</span></footer>
</div>
{G.alt_serit(site)}"""


JS = ""
