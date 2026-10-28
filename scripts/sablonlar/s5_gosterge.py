"""Şablon 5 · Gösterge – yeni; lastikçi sitelerinin ailesinden (koyu zemin, dev ad, tek vurgu rengi, renkli Hemen Ara,
ödeme kartı), dili araç göstergesi.

Sağ üstte büyük devir göstergesi (çentikler, rakamlar, renkli kırmızı bölge); geniş kalın büyük ad (Archivo
Expanded), hizmetin yanında cetvel çizgisi. Bağlantılar konsol tuşları gibi (simge kutusu, köşesinde gösterge
ışığı, altında ad); IBAN kilometre sayacı gibi bir pencerede. Açılış: gösterge yayı çizilir, ibre kontak açılınca
olduğu gibi kırmızı bölgeye kadar çıkıp rölantiye iner, ad soldan kayarak gelir, tuşların ışıkları sırayla yanar;
kaydırınca ibre yükselir, ödeme kartı görününce IBAN grupları sayaç gibi döner; birkaç saniyede bir ibre gaza
basılmış gibi kıpırdar, Hemen Ara parlar; Hemen Ara ekrandan çıkınca sağ altta ara düğmesi.
"""
import math

from .ortak import e, fit, svg, tr_title

NO, AD, SLUG = 5, "Gösterge", "gosterge"
KAYNAK = "yeni"
RENK, BG = "#ff6a1a", "#0b0b0c"
FONTS = {"wide": ("Archivo-ExpandedBold.ttf", "Archivo Expanded", 700, "normal"),
         "text": ("Figtree_400Regular.ttf", "Figtree", 400, "normal"),
         "text-sb": ("Figtree_600SemiBold.ttf", "Figtree", 600, "normal"),
         "text-xb": ("Figtree_800ExtraBold.ttf", "Figtree", 800, "normal")}
LICENSES = ("OFL-archivo.txt", "OFL-figtree.txt")
MARK_FONT = ("Archivo-ExpandedBold.ttf", -0.01)
MARK = ".mark .ln"
FITS = ".iban,.call b,.key b,.rows dd,.btn,.eyebrow,.kind span"
INTRO_MS = 2400
ORNEK = ("autotufan_isimlik", {})
ARROW = "M7 17L17 7M9 7h8v8"
STEPS = 8                                     # göstergede 0 … 8 (× 1000 devir)


def _pt(r, a):
    """Tepeden saat yönünde a derece, r yarıçap: SVG noktası."""
    t = math.radians(a)
    return r * math.sin(t), -r * math.cos(t)


def _ang(v):
    return -135 + 270 * v / STEPS


def gauge():
    ticks = []
    for k in range(STEPS * 4 + 1):
        v = k / 4
        major = k % 4 == 0
        x1, y1 = _pt(126 if major else 133, _ang(v))
        x2, y2 = _pt(141, _ang(v))
        ticks.append(f'<line class="{"mj" if major else "mn"}{" hot" if v >= 6.5 else ""}" x1="{x1:.1f}" y1="{y1:.1f}" '
                     f'x2="{x2:.1f}" y2="{y2:.1f}"/>')
    nums = "".join(f'<text x="{_pt(108, _ang(v))[0]:.1f}" y="{_pt(108, _ang(v))[1] + 5:.1f}">{v}</text>'
                   for v in range(STEPS + 1))
    (ax, ay), (bx, by) = _pt(141, _ang(6.5)), _pt(141, _ang(STEPS))
    red = f'<path class="red" d="M{ax:.1f} {ay:.1f}A141 141 0 0 1 {bx:.1f} {by:.1f}"/>'
    return (f'<svg class="gauge" viewBox="-160 -160 320 320" aria-hidden="true">'
            f'<circle class="track" r="141" transform="rotate(135)" pathLength="360"/>{red}'
            f'<g class="ticks">{"".join(ticks)}</g><g class="nums">{nums}</g>'
            f'<text class="unit" y="54">x1000 d/d</text>'
            f'<g class="tilt"><g class="needle"><path d="M-4 16L0 -128L4 16Z"/><circle r="11"/>'
            f'<circle class="cap" r="4"/></g></g></svg>')


def favicon(site):
    c = site.renk or RENK
    (ax, ay), (bx, by) = _pt(22, -135), _pt(22, 135)
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='-32 -32 64 64'><rect x='-32' y='-32' width='64' "
            f"height='64' rx='14' fill='#0b0b0c'/><path d='M{ax:.1f} {ay:.1f}A22 22 0 1 1 {bx:.1f} {by:.1f}' "
            "fill='none' stroke='#f3f3f0' stroke-width='5' stroke-linecap='round'/>"
            f"<path d='M-3 4L12 -15L3 6Z' fill='{c}'/><circle r='5' fill='{c}'/></svg>")


CSS = """
:root{color-scheme:dark;--bg:#0b0b0c;--surface:#141416;--raise:#1b1b1e;--line:#26262b;--line2:#36363c;
  --text:#f3f3f0;--muted:#9b9ba2;--dim:#64646b;--ok:#1f9d55;--white:#fff;
  --wide:"Archivo Expanded","Archivo",system-ui,sans-serif;--ui:"Figtree",system-ui,-apple-system,"Segoe UI",sans-serif;
  --ruler:repeating-linear-gradient(90deg,var(--line2) 0 1px,transparent 1px 8px);--scn:0}
*{box-sizing:border-box;margin:0}
html{background:var(--bg);-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--text);font:400 16px/1.5 var(--ui);min-height:100vh;overflow-x:hidden}
a{color:inherit;-webkit-tap-highlight-color:transparent}
button{font:inherit;color:inherit}
:focus-visible{outline:2px solid var(--ac);outline-offset:3px}
.wrap{max-width:480px;margin:0 auto;padding-left:max(20px,env(safe-area-inset-left,0px));
  padding-right:max(20px,env(safe-area-inset-right,0px));padding-block:0 calc(100px + env(safe-area-inset-bottom,0px))}
/* ---- başlık: sağ üstte devir göstergesi ---- */
.hero{position:relative;isolation:isolate;overflow:hidden;padding:38px max(20px,env(safe-area-inset-right,0px)) 30px
  max(20px,env(safe-area-inset-left,0px));margin:0 calc(-1 * max(20px,env(safe-area-inset-right,0px))) 0
  calc(-1 * max(20px,env(safe-area-inset-left,0px)));--avail:calc(min(100vw,480px) - 44px)}
.hero::before{content:"";position:absolute;z-index:-2;inset:0;pointer-events:none;
  background:radial-gradient(60% 55% at 92% 18%,rgba(var(--ac-rgb),.14),transparent 70%)}
.gauge{position:absolute;z-index:-1;top:-34px;right:-128px;width:330px;height:330px;overflow:visible}
.gauge .track{fill:none;stroke:#18181c;stroke-width:8;stroke-dasharray:270 360}
.gauge .red{fill:none;stroke:var(--ac);stroke-width:8;opacity:.55}
.gauge line{stroke:#34343a;stroke-width:2;stroke-linecap:round}
.gauge line.mj{stroke:#55555d;stroke-width:3.5}
.gauge line.hot{stroke:var(--ac)}
.gauge .nums text{font:600 15px var(--ui);fill:#4d4d55;text-anchor:middle}
.gauge .unit{font:600 10px var(--ui);fill:#3d3d44;text-anchor:middle;letter-spacing:.12em}
.gauge .tilt{transform-box:view-box;transform-origin:0 0;rotate:calc(min(var(--scn),500) * .22deg)}
.gauge .needle{transform-box:view-box;transform-origin:0 0;transform:rotate(-78deg)}
.gauge .needle path,.gauge .needle circle{fill:var(--ac)}
.gauge .needle path{filter:drop-shadow(0 0 6px rgba(var(--ac-rgb),.8))}
.gauge .needle .cap{fill:var(--bg)}
.eyebrow{display:flex;align-items:center;gap:10px;font:800 12px/1 var(--ui);letter-spacing:.26em;color:var(--muted);
  white-space:nowrap}
.led{flex:none;width:8px;height:8px;border-radius:50%;background:var(--ac);box-shadow:0 0 10px 1px rgba(var(--ac-rgb),.8)}
.own{display:block;height:34px;width:auto;margin-top:22px;fill:var(--ac);filter:drop-shadow(0 4px 14px rgba(var(--ac-rgb),.3))}
.mark{display:flex;flex-direction:column;margin-top:18px;
  font:700 min(clamp(54px,17vw,86px),calc(var(--avail) * var(--mk)))/.94 var(--wide);letter-spacing:-.01em}
.mark .ln{display:block;width:max-content}
.kind{display:flex;align-items:center;gap:14px;margin-top:18px}
.kind span{font:800 14px/1 var(--ui);letter-spacing:.42em;color:var(--ac);white-space:nowrap}
.kind::after{content:"";flex:1;height:9px;background:var(--ruler);transform-origin:left;
  -webkit-mask-image:linear-gradient(90deg,#000,transparent);mask-image:linear-gradient(90deg,#000,transparent)}
.lead{margin-top:16px;max-width:32ch;color:var(--muted);font-size:15.5px}
/* ---- Hemen Ara ---- */
.call{position:relative;overflow:hidden;isolation:isolate;display:flex;align-items:center;gap:14px;margin-top:6px;
  padding:18px 16px 18px 22px;border-radius:16px;background:linear-gradient(115deg,var(--ac),var(--ac2));
  color:var(--ac-ink);text-decoration:none;box-shadow:0 20px 40px -22px rgba(var(--ac-rgb),.85);transition:transform .15s}
.call::before{content:"";position:absolute;z-index:-1;right:76px;top:0;bottom:0;width:120px;opacity:.1;
  background:repeating-linear-gradient(90deg,currentColor 0 2px,transparent 2px 9px);
  -webkit-mask-image:linear-gradient(90deg,transparent,#000);mask-image:linear-gradient(90deg,transparent,#000)}
.call::after{content:"";position:absolute;top:0;bottom:0;left:0;width:36%;z-index:-1;pointer-events:none;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.3),transparent);transform:translateX(-140%) skewX(-20deg)}
.call:active{transform:scale(.985)}
.call .t{flex:1;min-width:0}
.call small{display:block;font:800 12px/1 var(--ui);letter-spacing:.24em;color:var(--ac-ink2)}
.call b{display:block;margin-top:9px;font:700 clamp(19px,5.9vw,25px)/1 var(--wide);letter-spacing:-.01em;
  font-variant-numeric:tabular-nums;white-space:nowrap}
.call .ib{position:relative;flex:none;display:grid;place-items:center;width:52px;height:52px;border-radius:50%;
  background:var(--bg)}
.call .ib::before{content:"";position:absolute;inset:-6px;border-radius:50%;border:2px solid var(--bg);
  border-right-color:transparent;border-bottom-color:transparent;opacity:.35;transform:rotate(-45deg)}
.call .ib .ic{width:23px;height:23px;fill:var(--ac)}
/* ---- bağlantılar: konsol tuşları ---- */
.keys{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:12px 10px;margin-top:14px}
.key{grid-column:span var(--span,4);display:flex;flex-direction:column;align-items:center;gap:8px;text-decoration:none;
  min-width:0}
.key .kb{position:relative;display:grid;place-items:center;width:100%;height:64px;border-radius:16px;
  background:linear-gradient(180deg,#1c1c20,#121214);border:1px solid var(--line2);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.06),0 6px 0 -2px #070708,0 10px 18px -10px #000;
  transition:transform .12s,box-shadow .12s}
.key .ic{width:24px;height:24px;fill:var(--text)}
.key .kb i{position:absolute;top:9px;right:10px;width:6px;height:6px;border-radius:50%;background:var(--ac);opacity:.28;
  transition:opacity .2s,box-shadow .2s}
.key b{display:block;max-width:100%;font:600 13px/1.2 var(--ui);color:var(--muted);text-align:center;white-space:nowrap}
.key:active .kb{transform:translateY(3px);box-shadow:inset 0 1px 0 rgba(255,255,255,.04),0 3px 0 -2px #070708}
.key:active .kb i,.key:hover .kb i{opacity:1;box-shadow:0 0 8px rgba(var(--ac-rgb),.9)}
.key:active b{color:var(--text)}
/* ---- ödeme: sayaç penceresi ---- */
.sec{display:flex;align-items:center;gap:12px;margin:40px 0 14px;font:800 12px/1 var(--ui);letter-spacing:.32em;
  color:var(--muted)}
.sec::before{content:"";width:8px;height:8px;border-radius:50%;background:var(--ac);box-shadow:0 0 8px rgba(var(--ac-rgb),.7)}
.sec::after{content:"";flex:1;height:9px;background:var(--ruler);opacity:.8;
  -webkit-mask-image:linear-gradient(90deg,#000,transparent);mask-image:linear-gradient(90deg,#000,transparent)}
.pay{position:relative;overflow:hidden;padding:20px;border-radius:18px;container-type:inline-size;
  background:radial-gradient(120% 80% at 100% 0%,rgba(var(--ac-rgb),.1),transparent 60%),var(--surface);
  border:1px solid var(--line)}
.rows{display:grid;grid-template-columns:auto 1fr;gap:10px 20px;font-size:15px;margin-bottom:16px}
.rows dt{color:var(--muted)}
.rows dd{font-weight:800;text-align:right;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.odo{padding:12px 14px 14px;border-radius:12px;background:#070708;border:1px solid var(--line2);
  box-shadow:inset 0 2px 10px rgba(0,0,0,.8)}
.odo>span{display:flex;justify-content:space-between;font:800 11px/1 var(--ui);letter-spacing:.3em;color:var(--dim)}
.odo>span em{font-style:normal;color:var(--ac);letter-spacing:.1em}
.iban{display:block;margin-top:10px;font:800 18px/1.25 var(--ui);font-size:min(19px,4.9cqi);letter-spacing:.01em;
  word-spacing:.04em;font-variant-numeric:tabular-nums;white-space:nowrap;user-select:all;-webkit-user-select:all}
.iban i{display:inline-block;overflow:hidden;vertical-align:bottom;font-style:normal}
.iban i b{display:inline-block;font-weight:inherit}
.acts{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px}
.acts.one{grid-template-columns:1fr}
.btn{display:flex;align-items:center;justify-content:center;gap:9px;min-height:52px;border-radius:12px;cursor:pointer;
  font:800 15px/1 var(--ui);text-decoration:none;white-space:nowrap;transition:transform .15s,background .2s,border-color .2s}
.btn:active{transform:scale(.97)}
.btn .ic{width:19px;height:19px}
.copy{border:0;background:var(--ac);color:var(--ac-ink)}
.copy .ic{fill:var(--ac-ink)}
.copy.ok{background:var(--ok);color:#fff}
.copy.ok .ic{fill:#fff}
.ghost{border:1px solid var(--line2);background:transparent;color:var(--text)}
.ghost .ic{fill:var(--text)}
.ghost[aria-expanded="true"]{border-color:var(--ac);color:var(--ac)}
.ghost[aria-expanded="true"] .ic{fill:var(--ac)}
.kk{margin-top:12px;padding:18px 16px 14px;border-radius:14px;background:var(--raise);border:1px solid var(--line);
  text-align:center}
.kk .qr{display:inline-block;padding:12px;border-radius:12px;background:var(--white)}
.kk img{display:block;width:min(220px,58vw);height:auto;image-rendering:pixelated}
.kk p{margin:12px 4px 8px;font-size:14px;color:var(--muted)}
.kk p b{color:var(--text)}
.kk a{color:var(--ac);font-weight:800;text-underline-offset:3px}
.note{margin-top:12px;font-size:12px;color:var(--dim);text-align:center}
/* ---- altbilgi ---- */
footer{margin-top:46px;padding-top:20px;border-top:1px solid var(--line);display:flex;justify-content:space-between;
  align-items:center;gap:12px;color:var(--dim);font-size:13px}
footer b{display:flex;align-items:center;gap:10px;font:700 15px/1 var(--wide);letter-spacing:-.01em;color:var(--text)}
footer b svg{width:22px;height:22px}
/* ---- kayan ara düğmesi, bildirim ---- */
.fab{position:fixed;z-index:20;right:calc(16px + env(safe-area-inset-right,0px));
  bottom:calc(18px + env(safe-area-inset-bottom,0px));display:grid;place-items:center;width:58px;height:58px;
  border-radius:50%;background:var(--ac);box-shadow:0 14px 30px -8px rgba(var(--ac-rgb),.75),0 0 0 6px rgba(var(--ac-rgb),.16);
  transform:scale(0);transition:transform .35s cubic-bezier(.3,1.5,.5,1);text-decoration:none}
.fab.show{transform:scale(1)}
.fab .ic{width:26px;height:26px;fill:var(--ac-ink)}
.toast{position:fixed;z-index:30;left:50%;bottom:calc(92px + env(safe-area-inset-bottom));transform:translate(-50%,40px);
  width:max-content;max-width:calc(100vw - 32px);text-align:center;background:var(--raise);color:var(--text);
  border:1px solid var(--line2);border-left:4px solid var(--ac);padding:12px 18px;border-radius:12px;font-weight:600;
  box-shadow:0 14px 34px rgba(0,0,0,.6);transition:transform .25s,opacity .25s;opacity:0;pointer-events:none}
.toast.show{transform:translate(-50%,0);opacity:1}
/* ---- animasyonlar ---- */
@keyframes arc{from{stroke-dasharray:0 360}to{stroke-dasharray:270 360}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes sweep{0%{transform:rotate(-135deg)}42%{transform:rotate(118deg)}55%{transform:rotate(108deg)}
  100%{transform:rotate(-78deg)}}
@keyframes rev{0%,86%,100%{transform:rotate(-78deg)}90%{transform:rotate(-20deg)}94%{transform:rotate(-48deg)}}
@keyframes slide{from{opacity:0;transform:translateX(-36px) skewX(-14deg);filter:blur(5px)}
  to{opacity:1;transform:none;filter:blur(0)}}
@keyframes track{from{letter-spacing:1em;opacity:0}to{letter-spacing:.42em;opacity:1}}
@keyframes grow{from{transform:scaleX(0)}to{transform:none}}
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes led{0%{opacity:.28}30%{opacity:1;box-shadow:0 0 10px rgba(var(--ac-rgb),1)}100%{opacity:.28}}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.35}}
@keyframes shine{0%,72%{transform:translateX(-140%) skewX(-20deg)}100%{transform:translateX(300%) skewX(-20deg)}}
@keyframes roll{from{transform:translateY(110%)}to{transform:none}}
@keyframes flash{0%{color:var(--ac)}100%{color:var(--text)}}
@keyframes open{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}
.gauge .track{animation:arc .7s .05s cubic-bezier(.4,0,.2,1) both}
.gauge .ticks,.gauge .nums,.gauge .red,.gauge .unit{animation:fade .6s .25s both}
.gauge .needle{animation:sweep 1.25s .35s cubic-bezier(.45,0,.25,1) both,rev 6s 3s infinite}
.eyebrow{animation:fade .5s .2s both}
.led{animation:blink 1.6s 1.6s 3}
.own{animation:fade .6s .35s both}
.mark .ln{animation:slide .7s cubic-bezier(.2,.8,.2,1) both}
.mark .ln:nth-child(1){animation-delay:.45s}.mark .ln:nth-child(2){animation-delay:.56s}
.kind span{animation:track .9s .85s cubic-bezier(.2,.8,.2,1) both}
.kind::after{animation:grow .8s 1s cubic-bezier(.2,.8,.2,1) both}
.lead{animation:fade .7s 1.05s both}
.call{animation:rise .6s 1.15s cubic-bezier(.2,.8,.2,1) both}
.call::after{animation:shine 6s 3s infinite}
.key{animation:rise .5s cubic-bezier(.2,.8,.2,1) both}
.sec,.pay{animation:rise .6s 1.55s cubic-bezier(.2,.8,.2,1) both}
.key .kb i{animation:led .9s both}
.pay.in .iban i b{animation:roll .55s cubic-bezier(.2,.9,.25,1.15) both}
.iban.flash{animation:flash .9s ease-out}
.kk.on,.kk:target{animation:open .35s cubic-bezier(.2,.8,.2,1)}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}
  .gauge .tilt{rotate:none}}
"""
CSS += "".join(f".pay.in .iban i:nth-child({k + 1}) b{{animation-delay:{.15 + .08 * k:.2f}s}}" for k in range(8)) + "\n"

OG_CSS = """
body.og{margin:0;width:1200px;height:630px;overflow:hidden}
.og .hero{margin:0;width:1200px;height:630px;padding:90px 100px 0}
.og .gauge{top:-60px;right:-120px;width:760px;height:760px}
.og .eyebrow{font-size:24px;gap:18px}.og .led{width:16px;height:16px}.og .own{height:64px;margin-top:34px}
.og .mark{font-size:min(150px,calc(760px * var(--mk)));margin-top:26px}
.og .kind{margin-top:30px}.og .kind span{font-size:30px}.og .kind::after{height:18px}
"""


def _rows(n):
    """Tuşlar 12 sütunluk ızgarada: sırada en çok 4 tuş (genişlik 12 / sıradaki tuş sayısı)."""
    if n <= 4:
        return [12 // n] * n
    first = 3 if n in (5, 6) else 4
    return [12 // first] * first + _rows(n - first)


def css(site):
    n = len(site.links())
    return (CSS + f":root{{--mk:{fit(MARK_FONT, site, 0.04):.4f}}}\n"
            + "".join(f".key:nth-child({k + 1}){{animation-delay:{1.25 + .07 * k:.2f}s}}"
                      f".key:nth-child({k + 1}) .kb i{{animation-delay:{1.5 + .12 * k:.2f}s}}" for k in range(n)) + "\n")


def _own(site):
    if not site.isaret:
        return ""
    return f'<svg class="own" viewBox="{site.isaret_box}" aria-hidden="true">{site.isaret}</svg>'


def _mark(site):
    return "".join(f'<span class="ln">{e(t)}</span>' for t in site.lines)


def og(site):
    return (f'<header class="hero">{gauge()}<p class="eyebrow"><i class="led"></i>{e(site.etiket)}</p>{_own(site)}'
            f'<h1 class="mark">{_mark(site)}</h1><p class="kind"><span>{e(site.hizmet)}</span></p></header>')


def body(site, ctx):
    links = site.links(vcf_href=ctx.vcf)
    keys = "\n  ".join(
        f'<a class="key" href="{e(L.href)}" style="--span:{s}"'
        f'{f" download={chr(34)}{e(L.download)}{chr(34)}" if L.download else ""} aria-label="{e(L.title)}: {e(L.sub)}">'
        f'<span class="kb">{svg(L.icon)}<i></i></span><b>{e(L.short)}</b></a>'
        for L, s in zip(links, _rows(len(links))))
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
    groups = " ".join(f"<i><b>{g}</b></i>" for g in site.iban_txt.split())
    right = f"@{site.instagram}" if site.instagram else tr_title(site.etiket)
    mini = favicon(site).replace("<svg xmlns='http://www.w3.org/2000/svg'", "<svg aria-hidden='true'")
    return f"""<div class="wrap">
<header class="hero">
  {gauge()}
  <p class="eyebrow"><i class="led"></i>{e(site.etiket)}</p>{_own(site)}
  <h1 class="mark" aria-label="{e(site.isletme)}">{_mark(site)}</h1>
  <p class="kind"><span>{e(site.hizmet)}</span></p>
  <p class="lead">{e(site.aciklama)}</p>
</header>
<main>
<a class="call" href="tel:+{site.tel}"><span class="t"><small>HEMEN ARA</small><b>{e(site.phone)}</b></span>
  <span class="ib">{svg("phone")}</span></a>
<nav class="keys" aria-label="Bağlantılar">
  {keys}
</nav>
<h2 class="sec">ÖDEME BİLGİLERİ</h2>
<section class="pay" aria-label="Ödeme bilgileri">
  {f'<dl class="rows">{who}</dl>' if who else ''}
  <div class="odo"><span>IBAN<em>TR</em></span><output class="iban">{groups}</output></div>
  <div class="acts{'' if ctx.kk else ' one'}">
    <button class="btn copy" type="button" data-copy="{e(site.iban)}" data-done="Kopyalandı">{svg("copy")}<span>{"Kopyala" if ctx.kk else "IBAN'ı kopyala"}</span></button>{kk_btn}
  </div>{kk_box}{note}
</section>
</main>
<footer>
  <b>{mini}{e(" ".join(site.lines))}</b><span>{e(right)}</span>
</footer>
</div>
<a class="fab" href="tel:+{site.tel}" aria-label="Hemen ara">{svg("phone")}</a>"""


# ödeme kartı açılış bitince izlenir: ilk ekrandaysa sayaç açılıştan sonra döner
JS = """
(()=>{const p=document.querySelector('.pay'),still=matchMedia('(prefers-reduced-motion: reduce)').matches;
if(!('IntersectionObserver' in window))p.classList.add('in');
else setTimeout(()=>{const io=new IntersectionObserver(([x])=>{if(x.isIntersecting){p.classList.add('in');
  io.disconnect()}},{threshold:.35});io.observe(p)},still?0:1700);
if(still)return;let q=0;
addEventListener('scroll',()=>{if(!q)q=requestAnimationFrame(()=>{document.documentElement.style.setProperty('--scn',
  Math.min(scrollY,500).toFixed(0));q=0})},{passive:true})})();
"""
