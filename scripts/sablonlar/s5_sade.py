"""Şablon 5 · Sade – lastikçi sitelerinin ailesinden, süssüz ve modern.

İlk denenen 5. şablon (Gösterge: devir göstergesi, konsol tuşları, sayaç gibi dönen IBAN) için: "diğerleri gibi
olsun, sade modern; değişik şeyler ekliyorsun". Bu yüzden ek süs yok; düzen öbür dördüyle aynı: koyu zemin, solda
büyük ad (Figtree), altında kısa renkli çizgi ve hizmet, renkli Hemen Ara, bağlantılar tek kartta liste (simge,
başlık ve alt satır, ok), ödeme bilgileri kartı, altbilgi, Hemen Ara ekrandan çıkınca altta arama şeridi.
Logo işareti varsa adın üstünde.
Açılış ("animasyonu biraz artıralım, logo çizim gibi gelsin"): logo çizilerek gelir (fırça darbeleri verilmişse
yazılır gibi, yoksa dış hattı çizilip içi dolar); adın harfleri sırayla yükselir, çizgi uzar, hizmetin harf aralığı
daralarak oturur, Hemen Ara ve bağlantı satırları sırayla gelir; birkaç saniyede bir Hemen Ara'nın üstünden ışık
geçer ve telefon simgesi çalar.
"""
from .ortak import DRAW_CSS, drawn_mark, e, fit, svg

NO, AD, SLUG = 5, "Sade", "sade"
KAYNAK = "yeni"
RENK, BG = "#2f7cf6", "#0b0b0c"
FONTS = {"text": ("Figtree_400Regular.ttf", "Figtree", 400, "normal"),
         "text-sb": ("Figtree_600SemiBold.ttf", "Figtree", 600, "normal"),
         "text-xb": ("Figtree_800ExtraBold.ttf", "Figtree", 800, "normal")}
LICENSES = ("OFL-figtree.txt",)
MARK_FONT = ("Figtree_800ExtraBold.ttf", -0.035)
MARK = ".mark .ln"
FITS = ".iban,.call b,.row b,.row small,.rows dd,.btn,.eyebrow,.kind"
INTRO_MS = 2600
ORNEK = ("autotufan_isimlik", {})
ARROW = "M9 6l6 6-6 6"


def favicon(site):
    c = site.renk or RENK
    if site.isaret:
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{site.isaret_box}"><g fill="{c}">'
                f'{site.isaret}</g></svg>')
    letter = e(site.marka[:1])
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='14' "
            f"fill='#0b0b0c'/><text x='32' y='44' text-anchor='middle' font-family='Arial' font-weight='700' "
            f"font-size='34' fill='#f4f4f1'>{letter}</text><rect x='18' y='50' width='28' height='4' fill='{c}'/></svg>")


CSS = """
/* koyu, tek sütun, sol hizalı; vurgu rengi yalnız çizgide, hizmette, Hemen Ara'da ve simgelerde */
:root{color-scheme:dark;--bg:#0b0b0c;--surface:#141416;--raise:#1b1b1e;--line:#26262a;--line2:#36363b;
  --text:#f4f4f1;--muted:#9a9aa1;--dim:#66666d;--ok:#1f9d55;--white:#fff;
  --ui:"Figtree",system-ui,-apple-system,"Segoe UI",sans-serif}
*{box-sizing:border-box;margin:0}
html{background:var(--bg);-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--text);font:400 16px/1.5 var(--ui);min-height:100vh;overflow-x:hidden}
a{color:inherit;-webkit-tap-highlight-color:transparent}
button{font:inherit;color:inherit}
:focus-visible{outline:2px solid var(--ac);outline-offset:3px}
.wrap{max-width:480px;margin:0 auto;padding-left:max(20px,env(safe-area-inset-left,0px));
  padding-right:max(20px,env(safe-area-inset-right,0px));padding-block:0 calc(110px + env(safe-area-inset-bottom,0px))}
/* ---- başlık ---- */
.hero{position:relative;isolation:isolate;padding-block:44px 30px;--avail:calc(min(100vw,480px) - 44px)}
.hero::before{content:"";position:absolute;z-index:-1;inset:-44px -20px 0;pointer-events:none;
  background:radial-gradient(70% 60% at 100% 0%,rgba(var(--ac-rgb),.12),transparent 70%)}
.eyebrow{display:flex;align-items:center;gap:10px;font:600 12px/1 var(--ui);letter-spacing:.24em;color:var(--muted);
  white-space:nowrap}
.eyebrow::before{content:"";flex:none;width:6px;height:6px;border-radius:50%;background:var(--ac)}
.own{display:block;height:56px;width:auto;margin-top:24px;fill:var(--ac);color:var(--ac);overflow:visible;
  filter:drop-shadow(0 6px 18px rgba(var(--ac-rgb),.25))}
.mark{display:flex;flex-direction:column;margin-top:16px;
  font:800 min(clamp(64px,20vw,96px),calc(var(--avail) * var(--mk)))/.92 var(--ui);letter-spacing:-.035em}
.mark .ln{display:block;width:max-content}
.mark .ch{display:inline-block}
.bar{width:56px;height:4px;margin-top:22px;border-radius:2px;background:var(--ac);transform-origin:left}
.kind{margin-top:16px;font:800 14px/1 var(--ui);letter-spacing:.38em;color:var(--ac);white-space:nowrap}
.lead{margin-top:14px;max-width:32ch;color:var(--muted);font-size:15.5px}
/* ---- Hemen Ara ---- */
.call{position:relative;overflow:hidden;display:flex;align-items:center;gap:14px;margin-top:4px;
  padding:18px 16px 18px 22px;border-radius:16px;
  background:var(--ac);color:var(--ac-ink);text-decoration:none;box-shadow:0 18px 40px -22px rgba(var(--ac-rgb),.7);
  transition:transform .15s,filter .15s}
.call::after{content:"";position:absolute;top:-20%;bottom:-20%;left:-45%;width:30%;pointer-events:none;
  background:linear-gradient(100deg,transparent,rgba(255,255,255,.35),transparent);transform:skewX(-20deg)}
.call:active{transform:scale(.985);filter:brightness(.96)}
.call .t{flex:1;min-width:0}
.call small{display:block;font:800 12px/1 var(--ui);letter-spacing:.22em;opacity:.72}
.call b{display:block;margin-top:8px;font:800 clamp(25px,7.6vw,31px)/1 var(--ui);letter-spacing:-.01em;
  font-variant-numeric:tabular-nums;white-space:nowrap}
.call .ib{flex:none;display:grid;place-items:center;width:50px;height:50px;border-radius:50%;background:var(--bg)}
.call .ib .ic{width:23px;height:23px;fill:var(--ac)}
/* ---- bağlantılar: tek kartta liste ---- */
.list{margin-top:12px;border-radius:18px;background:var(--surface);border:1px solid var(--line);overflow:hidden}
.row{position:relative;display:grid;grid-template-columns:42px minmax(0,1fr) 16px;align-items:center;gap:14px;
  padding:14px 16px;text-decoration:none;transition:background .15s}
.row+.row::before{content:"";position:absolute;left:72px;right:0;top:0;height:1px;background:var(--line)}
.row:active{background:var(--raise)}
.row .ib{display:grid;place-items:center;width:42px;height:42px;border-radius:12px;background:rgba(var(--ac-rgb),.12)}
.row .ic{width:21px;height:21px;fill:var(--ac)}
.row b{display:block;font:700 16px/1.25 var(--ui);white-space:nowrap}
.row small{display:block;margin-top:2px;font-size:13.5px;line-height:1.3;color:var(--muted);overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
.row .go{width:16px;height:16px;fill:none;stroke:var(--dim);stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
/* ---- ödeme ---- */
.sec{display:flex;align-items:center;gap:12px;margin:40px 0 14px;font:800 12px/1 var(--ui);letter-spacing:.3em;
  color:var(--muted)}
.sec::after{content:"";flex:1;height:1px;background:var(--line)}
.pay{padding:20px;border-radius:18px;background:var(--surface);border:1px solid var(--line);container-type:inline-size}
.rows{display:grid;grid-template-columns:auto 1fr;gap:10px 20px;font-size:15px;margin-bottom:16px}
.rows dt{color:var(--muted)}
.rows dd{font-weight:700;text-align:right;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ibanbox{padding:14px 16px 15px;border-radius:12px;background:var(--bg);border:1px solid var(--line2)}
.ibanbox span{display:block;font:800 11px/1 var(--ui);letter-spacing:.3em;color:var(--dim)}
.iban{display:block;margin-top:8px;font:700 18px/1.2 var(--ui);font-size:min(19px,4.6cqi);letter-spacing:0;
  word-spacing:.05em;font-variant-numeric:tabular-nums;white-space:nowrap;user-select:all;-webkit-user-select:all}
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
footer{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-top:44px;padding-top:20px;
  border-top:1px solid var(--line);color:var(--dim);font-size:13px}
footer b{font:800 18px/1 var(--ui);letter-spacing:-.02em;color:var(--text)}
/* ---- alttaki arama şeridi, bildirim ---- */
.callbar{position:fixed;z-index:20;left:0;right:0;bottom:0;display:flex;justify-content:center;
  padding:12px max(16px,env(safe-area-inset-right,0px)) calc(12px + env(safe-area-inset-bottom,0px)) max(16px,env(safe-area-inset-left,0px));
  background:rgba(11,11,12,.86);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);border-top:1px solid var(--line);
  transform:translateY(110%);transition:transform .35s cubic-bezier(.2,.8,.2,1)}
.callbar.show{transform:none}
.callbar a{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;max-width:440px;min-height:52px;
  border-radius:14px;background:var(--ac);color:var(--ac-ink);text-decoration:none;font:800 16px/1 var(--ui)}
.callbar .ic{width:20px;height:20px;fill:var(--ac-ink)}
.callbar span{font-variant-numeric:tabular-nums}
.toast{position:fixed;z-index:30;left:50%;bottom:calc(92px + env(safe-area-inset-bottom));transform:translate(-50%,40px);
  width:max-content;max-width:calc(100vw - 32px);text-align:center;background:var(--raise);color:var(--text);
  border:1px solid var(--line2);border-left:4px solid var(--ac);padding:12px 18px;border-radius:12px;font-weight:600;
  box-shadow:0 14px 34px rgba(0,0,0,.6);transition:transform .25s,opacity .25s;opacity:0;pointer-events:none}
.toast.show{transform:translate(-50%,0);opacity:1}
/* ---- animasyonlar: logo çizilir, harfler sırayla yükselir; gecikmeler satır içinde (sırayla) ---- */
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes up{from{opacity:0;transform:translateY(55%)}to{opacity:1;transform:none}}
@keyframes left{from{opacity:0;transform:translateX(-14px)}to{opacity:1;transform:none}}
@keyframes track{from{letter-spacing:.9em;opacity:0}to{letter-spacing:.38em;opacity:1}}
@keyframes grow{from{transform:scaleX(0)}to{transform:none}}
@keyframes shine{0%,82%{left:-45%}100%{left:125%}}
@keyframes ring{0%,84%,100%{transform:none}86%,90%,94%{transform:rotate(-14deg)}88%,92%,96%{transform:rotate(14deg)}}
@keyframes flash{0%{color:var(--ac)}100%{color:var(--text)}}
@keyframes open{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}
.eyebrow{animation:fade .6s .1s both}
.mark .ch{animation:up .65s cubic-bezier(.2,.9,.25,1.1) both}
.bar{animation:grow .7s cubic-bezier(.2,.8,.2,1) both}
.kind{animation:track .9s cubic-bezier(.2,.8,.2,1) both}
.lead{animation:fade .7s both}
.call{animation:rise .6s cubic-bezier(.2,.8,.2,1) both}
.call::after{animation:shine 5s 3.2s infinite}
.call .ib .ic{animation:ring 5s 3.2s infinite}
.row{animation:left .5s cubic-bezier(.2,.8,.2,1) both}
.pay.in .iban{animation:flash 1.2s .2s ease-out}
.iban.flash{animation:flash .9s ease-out}
.kk.on,.kk:target{animation:open .35s cubic-bezier(.2,.8,.2,1)}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
""" + DRAW_CSS

OG_CSS = """
body.og{margin:0;width:1200px;height:630px;overflow:hidden}
.og .wrap{max-width:none;padding:0 100px}.og .hero{padding-block:90px 0}
.og .eyebrow{font-size:24px;gap:16px}.og .eyebrow::before{width:12px;height:12px}.og .own{height:60px;margin-top:36px}
.og .mark{font-size:min(170px,calc(1000px * var(--mk)));margin-top:24px}
.og .bar{width:110px;height:8px;margin-top:36px}.og .kind{font-size:28px;margin-top:28px}
"""


def css(site):
    return CSS + f":root{{--mk:{fit(MARK_FONT, site, 0.04):.4f}}}\n"


def _d(t):
    return f' style="animation-delay:{t:.2f}s"'


def _mark(site, t0):
    """Adın harfleri: sırayla yükselir (t0'dan başlayarak)."""
    k, lines = 0, []
    for t in site.lines:
        chars = ""
        for c in t:
            chars += f'<span class="ch"{_d(t0 + .045 * k)}>{"&nbsp;" if c == " " else e(c)}</span>'
            k += 1
        lines.append(f'<span class="ln">{chars}</span>')
    return "".join(lines), t0 + .045 * k


def og(site):
    logo, _ = drawn_mark(site, "own")
    name, _ = _mark(site, 0)
    return (f'<div class="wrap"><header class="hero"><p class="eyebrow">{e(site.etiket)}</p>{logo}'
            f'<h1 class="mark">{name}</h1><div class="bar"></div><p class="kind">{e(site.hizmet)}</p>'
            f'</header></div>')


def body(site, ctx):
    # zaman çizelgesi: logo çizilirken ad yükselir; ardından çizgi, hizmet, açıklama, Hemen Ara, satırlar
    logo, _ = drawn_mark(site, "own", 0.2)
    base = 0.2 if site.isaret else 0.0
    name, _ = _mark(site, 0.25 + base)
    go = f'<svg class="go" viewBox="0 0 24 24" aria-hidden="true"><path d="{ARROW}"/></svg>'
    rows = "\n  ".join(
        f'<a class="row" href="{e(L.href)}"{f" download={chr(34)}{e(L.download)}{chr(34)}" if L.download else ""}'
        f'{_d(1.3 + base + .07 * k)}><span class="ib">{svg(L.icon)}</span><span><b>{e(L.title)}</b>'
        f'<small>{e(L.sub)}</small></span>{go}</a>'
        for k, L in enumerate(site.links(vcf_href=ctx.vcf)))
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
    right = f"@{site.instagram}" if site.instagram else e(site.etiket)
    return f"""<div class="wrap">
<header class="hero">
  <p class="eyebrow">{e(site.etiket)}</p>{logo}
  <h1 class="mark" aria-label="{e(site.isletme)}">{name}</h1>
  <div class="bar" aria-hidden="true"{_d(.75 + base)}></div>
  <p class="kind"{_d(.85 + base)}>{e(site.hizmet)}</p>
  <p class="lead"{_d(1.05 + base)}>{e(site.aciklama)}</p>
</header>
<main>
<a class="call" href="tel:+{site.tel}"{_d(1.15 + base)}><span class="t"><small>HEMEN ARA</small><b>{e(site.phone)}</b></span>
  <span class="ib">{svg("phone")}</span></a>
<nav class="list" aria-label="Bağlantılar">
  {rows}
</nav>
<h2 class="sec">ÖDEME BİLGİLERİ</h2>
<section class="pay" data-in aria-label="Ödeme bilgileri">
  {f'<dl class="rows">{who}</dl>' if who else ''}
  <div class="ibanbox"><span>IBAN</span><output class="iban">{e(site.iban_txt)}</output></div>
  <div class="acts{'' if ctx.kk else ' one'}">
    <button class="btn copy" type="button" data-copy="{e(site.iban)}" data-done="Kopyalandı">{svg("copy")}<span>{"Kopyala" if ctx.kk else "IBAN'ı kopyala"}</span></button>{kk_btn}
  </div>{kk_box}{note}
</section>
</main>
<footer>
  <b>{e(" ".join(site.lines))}</b><span>{right}</span>
</footer>
</div>
<div class="callbar"><a href="tel:+{site.tel}" aria-label="Hemen ara">{svg("phone")}Hemen ara · <span>{e(site.phone)}</span></a></div>"""


JS = ""
