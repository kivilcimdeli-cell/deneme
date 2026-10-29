"""Şablon 3 · İkaz – Çalık Oto Lastik'in sitesinden (scripts/calik_sayfa.py).

Sade ve düzenli: tek yazı tipi (Manrope), her şey aynı sol hizada; vurgu rengi yalnız büyük adın sonundaki noktada,
hizmet yazısında, Hemen Ara'da ve IBAN çizgisinde. En üstte ve altbilgide ikaz şeridi. Bağlantılar 2 sütun
kutucuk (Rehbere kaydet de içinde). Açılış: ikaz şeridi kayarak gelir, arkada ışık süzülür, ad harf harf maskeden
yükselir, nokta belirir, hizmetin harf aralığı daralarak oturur; Hemen Ara ekrandan çıkınca altta arama şeridi.
"""
from .ortak import e, fit, svg, tr_title

NO, AD, SLUG = 3, "İkaz", "ikaz"
KAYNAK = "Çalık Oto Lastik"
RENK, BG = "#ffc814", "#0b0b0c"
FONTS = {"text": ("Manrope-Medium.ttf", "Manrope", 500, "normal"),
         "text-sb": ("Manrope-SemiBold.ttf", "Manrope", 600, "normal"),
         "text-xb": ("Manrope-ExtraBold.ttf", "Manrope", 800, "normal")}
LICENSES = ("OFL-manrope.txt",)
MARK_FONT = ("Manrope-ExtraBold.ttf", -0.04)
MARK = ".mark .ln"
FITS = ".iban,.call b,.tile b,.tile small,.rows dd,.btn,.kind"
INTRO_MS = 2300
ORNEK = ("calik_isimlik", {"marka": "ÇALIK", "hizmet": "OTO LASTİK",
                           "aciklama": "Lastikle ilgili her konuda bize tek dokunuşla ulaşın.", "karekod_hata": "h"})
ARROW = "M7 17L17 7M9 7h8v8"


def favicon(site):
    c = site.renk or RENK
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='14' "
            f"fill='#0b0b0c'/><rect x='38' y='38' width='12' height='12' fill='{c}'/>"
            "<path d='M14 32a16 16 0 0 1 27-11.6' stroke='#f4f4f1' stroke-width='8' fill='none'/>"
            "<path d='M41 43.6A16 16 0 0 1 14 32' stroke='#f4f4f1' stroke-width='8' fill='none'/></svg>")


CSS = """
/* koyu, tek sütun, sol hizalı; vurgu rengi yalnız nokta, çizgi, Hemen Ara. Ölçek: 12 · 14 · 16 · 20 · 26 · büyük */
:root{color-scheme:dark;--bg:#0b0b0c;--surface:#141416;--raise:#1b1b1e;--line:#26262a;--line2:#36363b;
  --text:#f4f4f1;--muted:#9a9aa1;--dim:#66666d;--ok:#1f9d55;--white:#fff;
  --ui:"Manrope",system-ui,-apple-system,"Segoe UI",sans-serif;
  --stripe:repeating-linear-gradient(-45deg,#0b0b0c 0 9px,var(--ac) 9px 18px)}
*{box-sizing:border-box;margin:0}
html{background:var(--bg);-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--text);font:500 16px/1.5 var(--ui);min-height:100vh;overflow-x:hidden}
a{color:inherit;-webkit-tap-highlight-color:transparent}
button{font:inherit;color:inherit}
:focus-visible{outline:2px solid var(--ac);outline-offset:3px}
.wrap{max-width:480px;margin:0 auto;padding-left:max(20px,env(safe-area-inset-left,0px));
  padding-right:max(20px,env(safe-area-inset-right,0px));padding-block:0 calc(110px + env(safe-area-inset-bottom,0px))}
.stripe{height:6px;background:var(--stripe);background-position:calc(var(--sc) * -.6) 0}
/* ---- başlık ---- */
.hero{position:relative;isolation:isolate;padding-block:40px 34px;--avail:calc(min(100vw,480px) - 44px)}
.hero::before{content:"";position:absolute;z-index:-1;inset:-40px -20px 0;pointer-events:none;
  background:radial-gradient(55% 55% at 85% 20%,rgba(var(--ac-rgb),.16),transparent 70%)}
.mark{display:flex;flex-direction:column;margin-top:0;
  font:800 min(clamp(78px,25vw,112px),calc(var(--avail) * var(--mk)))/.86 var(--ui);letter-spacing:-.04em}
.mark .ln{display:flex;align-items:flex-end}
.mark .ch{display:block;overflow:hidden;padding-top:.06em;padding-bottom:.2em;margin-bottom:-.2em}
.mark .ch span{display:block}
.mark .dot{width:.16em;height:.16em;margin:0 0 .02em .06em;background:var(--ac);flex:none}
.kind{display:flex;align-items:center;gap:14px;margin-top:max(26px,.3em);font:800 15px/1 var(--ui);letter-spacing:.5em;
  color:var(--ac);white-space:nowrap}
.kind::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--line2),transparent)}
.lead{margin-top:18px;max-width:30ch;color:var(--muted);font-size:16px}
/* ---- Hemen Ara ---- */
.call{position:relative;display:flex;align-items:center;gap:14px;margin-top:6px;padding:18px 16px 18px 22px;
  border-radius:16px;background:var(--ac);color:var(--ac-ink);text-decoration:none;
  box-shadow:0 18px 40px -22px rgba(var(--ac-rgb),.7);transition:transform .15s,filter .15s}
.call:active{transform:scale(.985);filter:brightness(.96)}
.call .t{flex:1;min-width:0}
.call small{display:block;font:800 12px/1 var(--ui);letter-spacing:.22em;opacity:.72}
.call b{display:block;margin-top:8px;font:800 clamp(25px,7.6vw,31px)/1 var(--ui);letter-spacing:-.01em;
  font-variant-numeric:tabular-nums;white-space:nowrap}
.call .ib{flex:none;display:grid;place-items:center;width:50px;height:50px;border-radius:50%;background:var(--bg)}
.call .ib .ic{width:23px;height:23px;fill:var(--ac)}
/* ---- bağlantılar ---- */
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}
.tile{position:relative;display:flex;flex-direction:column;justify-content:space-between;gap:26px;min-height:124px;
  padding:16px;border-radius:16px;background:var(--surface);border:1px solid var(--line);text-decoration:none;
  min-width:0;transition:background .15s,border-color .15s,transform .15s}
.tile.wide{grid-column:span 2}
.tile:active{transform:scale(.98);background:var(--raise);border-color:var(--line2)}
.tile .ib{display:grid;place-items:center;width:40px;height:40px;border-radius:11px;background:var(--raise);
  border:1px solid var(--line2)}
.tile .ic{width:21px;height:21px;fill:var(--ac)}
.tile .go{position:absolute;top:16px;right:16px;width:16px;height:16px;fill:none;stroke:var(--dim);stroke-width:2;
  stroke-linecap:round;stroke-linejoin:round;transition:stroke .15s,transform .15s}
.tile:active .go{stroke:var(--ac);transform:translate(2px,-2px)}
.tile b{display:block;font:800 16px/1.2 var(--ui);white-space:nowrap}
.tile small{display:block;margin-top:3px;font-size:13px;line-height:1.3;color:var(--muted);overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
/* ---- ödeme ---- */
.sec{display:flex;align-items:center;gap:12px;margin:40px 0 14px;font:800 12px/1 var(--ui);letter-spacing:.32em;
  color:var(--muted)}
.sec::after{content:"";flex:1;height:1px;background:var(--line)}
.pay{padding:20px;border-radius:18px;background:var(--surface);border:1px solid var(--line);container-type:inline-size}
.rows{display:grid;grid-template-columns:auto 1fr;gap:10px 20px;font-size:15px;margin-bottom:18px}
.rows dt{color:var(--muted)}
.rows dd{font-weight:800;text-align:right;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ibanbox{position:relative;padding:14px 14px 15px 18px;border-radius:12px;background:var(--bg);
  border:1px solid var(--line2);overflow:hidden}
.ibanbox::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--ac);transform-origin:top}
.ibanbox span{display:block;font:800 11px/1 var(--ui);letter-spacing:.3em;color:var(--dim)}
.iban{display:block;margin-top:8px;font:800 18px/1.2 var(--ui);font-size:min(19px,4.85cqi);letter-spacing:.005em;
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
footer{margin-top:44px}
footer .row{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-top:18px;color:var(--dim);font-size:13px}
footer b{display:flex;align-items:flex-end;font:800 18px/1 var(--ui);letter-spacing:-.02em;color:var(--text)}
footer b i{width:.22em;height:.22em;margin-left:.08em;background:var(--ac)}
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
/* ---- animasyonlar ---- */
@keyframes up{from{transform:translateY(105%)}to{transform:none}}
@keyframes dot{0%{transform:scale(0)}70%{transform:scale(1.25)}100%{transform:none}}
@keyframes track{from{letter-spacing:1.1em;opacity:0}to{letter-spacing:.5em;opacity:1}}
@keyframes line{from{transform:scaleX(0)}to{transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@keyframes glow{from{opacity:0;transform:translateX(-45%)}to{opacity:1;transform:none}}
@keyframes stripes{from{background-position:-120px 0}to{background-position:0 0}}
@keyframes pulse{0%,78%,100%{box-shadow:0 18px 40px -22px rgba(var(--ac-rgb),.7),0 0 0 0 rgba(var(--ac-rgb),.45)}
  90%{box-shadow:0 18px 40px -22px rgba(var(--ac-rgb),.7),0 0 0 10px rgba(var(--ac-rgb),0)}}
@keyframes ring{0%,84%,100%{transform:none}86%,90%,94%{transform:rotate(-14deg)}88%,92%,96%{transform:rotate(14deg)}}
@keyframes bar{from{transform:scaleY(0)}to{transform:none}}
@keyframes flash{0%{color:var(--ac)}100%{color:var(--text)}}
@keyframes open{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}
.stripe.top{animation:stripes 1.6s cubic-bezier(.1,.6,.2,1) both}
.hero::before{animation:glow 1.8s .1s cubic-bezier(.2,.7,.2,1) both}
.mark .ch span{animation:up .9s cubic-bezier(.2,.8,.15,1) both}
.mark .dot{animation:dot .5s 1s cubic-bezier(.3,1.4,.5,1) both}
.kind{animation:track 1s .7s cubic-bezier(.2,.8,.2,1) both}
.kind::after{transform-origin:left;animation:line .9s 1s cubic-bezier(.2,.8,.2,1) both}
.lead{animation:fade .7s 1.05s both}
.call{animation:rise .6s 1.15s cubic-bezier(.2,.8,.2,1) both,pulse 5s 2.6s infinite}
.call .ib .ic{animation:ring 5s 2.6s infinite}
.tile{animation:rise .55s cubic-bezier(.2,.8,.2,1) both}
.pay.in .ibanbox::before{animation:bar .7s .1s cubic-bezier(.2,.8,.2,1) both}
.pay.in .iban{animation:flash 1.4s .3s ease-out}
.iban.flash{animation:flash .9s ease-out}
.kk.on,.kk:target{animation:open .35s cubic-bezier(.2,.8,.2,1)}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
"""

OG_CSS = """
body.og{margin:0;width:1200px;height:630px;overflow:hidden}
.og .wrap{max-width:none;padding:0 100px}.og .hero{padding-block:110px 0}.og .stripe{height:14px}
.og .mark{font-size:min(250px,calc(1000px * var(--mk)));margin-top:0}.og .kind{font-size:34px;margin-top:34px}
"""


def css(site):
    tiles = len(site.links())
    return (CSS + f":root{{--mk:{fit(MARK_FONT, site, 0.22):.4f}}}\n"
            + "".join(f".tile:nth-child({k + 1}){{animation-delay:{1.25 + .07 * k:.2f}s}}" for k in range(tiles)) + "\n")


def _mark(site):
    k, lines = 0, []
    for j, t in enumerate(site.lines):
        chars = ""
        for c in t:
            chars += (f'<span class="ch"><span style="animation-delay:{.25 + .06 * k:.2f}s">{e(c)}</span></span>'
                      if c != " " else '<span class="ch"><span>&nbsp;</span></span>')
            k += 1
        dot = '<i class="dot"></i>' if j == len(site.lines) - 1 else ""
        lines.append(f'<span class="ln">{chars}{dot}</span>')
    return "".join(lines)


def og(site):
    return (f'<div class="stripe"></div><div class="wrap"><header class="hero"><h1 class="mark">{_mark(site)}</h1>'
            f'<p class="kind">{e(site.hizmet)}</p></header></div>')


def body(site, ctx):
    go = f'<svg class="go" viewBox="0 0 24 24" aria-hidden="true"><path d="{ARROW}"/></svg>'
    links = site.links(vcf_href=ctx.vcf)
    subs = {"google": "Yorum yapın", "konum": site.konum or tr_title(site.sehir)}
    tiles = "\n  ".join(
        f'<a class="tile{" wide" if k == len(links) - 1 and len(links) % 2 else ""}" href="{e(L.href)}"'
        f'{f" download={chr(34)}{e(L.download)}{chr(34)}" if L.download else ""}><span class="ib">{svg(L.icon)}</span>'
        f'{go}<span><b>{e(L.title)}</b><small>{e(subs.get(L.key, L.sub))}</small></span></a>'
        for k, L in enumerate(links))
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
    # kartvizitte (10 × 20 kurumsal isimlik) IBAN yok: ödeme bölümü de yok
    pay = f"""<h2 class="sec">ÖDEME BİLGİLERİ</h2>
<section class="pay" data-in aria-label="Ödeme bilgileri">
  {f'<dl class="rows">{who}</dl>' if who else ''}
  <div class="ibanbox"><span>IBAN</span><output class="iban">{e(site.iban_txt)}</output></div>
  <div class="acts{'' if ctx.kk else ' one'}">
    <button class="btn copy" type="button" data-copy="{e(site.iban)}" data-done="Kopyalandı">{svg("copy")}<span>{"Kopyala" if ctx.kk else "IBAN'ı kopyala"}</span></button>{kk_btn}
  </div>{kk_box}{note}
</section>""" if site.iban else ""
    return f"""<div class="stripe top" aria-hidden="true"></div>
<div class="wrap">
<header class="hero">
  <h1 class="mark" aria-label="{e(site.isletme)}">{_mark(site)}</h1>
  <p class="kind">{e(site.hizmet)}</p>
  <p class="lead">{e(site.aciklama)}</p>
</header>
<main>
<a class="call" href="tel:+{site.tel}"><span class="t"><small>HEMEN ARA</small><b>{e(site.phone)}</b></span>
  <span class="ib">{svg("phone")}</span></a>
<nav class="grid" aria-label="Bağlantılar">
  {tiles}
</nav>
{pay}
</main>
<footer>
  <div class="stripe" aria-hidden="true"></div>
  <div class="row"><b>{e(" ".join(site.lines))}<i></i></b><span>{right}</span></div>
</footer>
</div>
<div class="callbar"><a href="tel:+{site.tel}" aria-label="Hemen ara">{svg("phone")}Hemen ara · <span>{e(site.phone)}</span></a></div>"""


JS = ""
