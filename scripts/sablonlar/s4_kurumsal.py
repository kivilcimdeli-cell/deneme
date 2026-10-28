"""Şablon 4 · Kurumsal – Soylu Oto Lastik'in sitesinden (scripts/soylu_sayfa.py).

Kurumsal ve düzenli: tek yazı tipi (Sora), ince çizgiler, arkada silik ızgara; vurgu rengi yalnız sağ üstteki eğik
şeritte, büyük adın altındaki çizgide, Hemen Ara'da, bağlantı numaralarında ve ödeme kartının üst çizgisinde.
Bağlantılar numaralı liste (01, 02 …). Açılış: şerit sağdan kayarak gelir, adı renkli bir blok soldan kapatıp sağa
açarak gösterir, çizgi uzar, hizmet harfleri sırayla oturur, düğme ve satırlar sırayla gelir; ödeme kartı görününce
üst çizgisi uzar ve IBAN dörtlü gruplar hâlinde belirir; Hemen Ara ekrandan çıkınca altta arama şeridi.
"""
from .ortak import e, fit, svg

NO, AD, SLUG = 4, "Kurumsal", "kurumsal"
KAYNAK = "Soylu Oto Lastik"
RENK, BG = "#e0202e", "#0a0a0b"
FONTS = {"text": ("Sora-Regular.ttf", "Sora", 400, "normal"),
         "text-sb": ("Sora-SemiBold.ttf", "Sora", 600, "normal"),
         "text-xb": ("Sora-ExtraBold.ttf", "Sora", 800, "normal")}
LICENSES = ("OFL-sora.txt",)
MARK_FONT = ("Sora-ExtraBold.ttf", -0.035)
MARK = ".mark .w"
FITS = ".iban,.call b,.row b,.row small,.rows dd,.btn,.eyebrow"
INTRO_MS = 2900
ORNEK = ("soylu_isimlik", {"marka": "SOYLU", "hizmet": "OTO LASTİK", "etiket": "ANTALYA · LASTİK SERVİSİ",
                           "aciklama": "Mobil lastik tamir ve servis. Tek dokunuşla arayın, yazın.",
                           "karekod_hata": "h"})
ARROW = "M5 12h14M13 6l6 6-6 6"


def favicon(site):
    c = site.renk or RENK
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='14' "
            f"fill='#0a0a0b'/><path d='M44 0h20v64H22z' fill='{c}'/>"
            "<rect x='12' y='44' width='18' height='5' fill='#f5f5f2'/><rect x='12' y='15' width='18' height='5' "
            "fill='#f5f5f2'/><rect x='12' y='29.5' width='18' height='5' fill='#f5f5f2'/></svg>")


CSS = """
/* siyah, tek sütun; vurgu rengi yalnız vurgu. Ölçek: 11 · 13 · 15 · 16 · 30 · büyük */
:root{color-scheme:dark;--bg:#0a0a0b;--surface:#131315;--raise:#1a1a1d;--line:#242428;--line2:#35353b;
  --text:#f5f5f2;--muted:#a1a1a8;--dim:#6b6b73;--ok:#1f9d55;--white:#fff;
  --ui:"Sora",system-ui,-apple-system,"Segoe UI",sans-serif}
*{box-sizing:border-box;margin:0}
html{background:var(--bg);-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--text);font:400 16px/1.55 var(--ui);min-height:100vh;overflow-x:hidden}
a{color:inherit;-webkit-tap-highlight-color:transparent}
button{font:inherit;color:inherit}
:focus-visible{outline:2px solid var(--ac);outline-offset:3px}
.topline{height:4px;background:var(--ac);transform-origin:left}
.wrap{max-width:480px;margin:0 auto;padding-left:max(20px,env(safe-area-inset-left,0px));
  padding-right:max(20px,env(safe-area-inset-right,0px));padding-block:0 calc(110px + env(safe-area-inset-bottom,0px))}
/* ---- başlık ---- */
/* başlık kenardan kenara (şerit ekran kenarında kesilir, yatay taşma olmaz) */
.hero{position:relative;isolation:isolate;overflow:hidden;padding-block:34px 30px;
  margin-left:calc(-1 * max(20px,env(safe-area-inset-left,0px)));margin-right:calc(-1 * max(20px,env(safe-area-inset-right,0px)));
  padding-left:max(20px,env(safe-area-inset-left,0px));padding-right:max(20px,env(safe-area-inset-right,0px));
  --avail:calc(min(100vw,480px) - 110px)}
.hero::before{content:"";position:absolute;z-index:-2;inset:0;pointer-events:none;
  background-image:linear-gradient(var(--line) 1px,transparent 1px),linear-gradient(90deg,var(--line) 1px,transparent 1px);
  background-size:30px 30px;background-position:-1px -1px;opacity:.55;
  -webkit-mask-image:radial-gradient(80% 70% at 70% 30%,#000,transparent 75%);mask-image:radial-gradient(80% 70% at 70% 30%,#000,transparent 75%)}
.slash{position:absolute;z-index:-1;top:-30px;right:-112px;width:150px;height:340px;background:var(--ac);
  transform:skewX(20deg);translate:0 calc(min(var(--sc),400px) * -.25);pointer-events:none}
.slash::before{content:"";position:absolute;top:0;bottom:0;left:-30px;width:12px;background:var(--ac);opacity:.5}
.eyebrow{display:flex;align-items:center;gap:10px;font:600 12px/1 var(--ui);letter-spacing:.26em;color:var(--muted);
  white-space:nowrap}
.eyebrow::before{content:"";width:18px;height:2px;background:var(--ac);flex:none}
.mark{position:relative;display:inline-block;margin-top:24px;
  font:800 min(clamp(70px,22vw,104px),calc(var(--avail) * var(--mk)))/.9 var(--ui);letter-spacing:-.035em}
.mark .w{display:block;width:max-content}
.mark .wipe{position:absolute;inset:-.02em -.06em -.06em;background:var(--ac);transform:scaleX(0);transform-origin:left}
.rule{width:96px;height:4px;margin-top:22px;background:var(--ac);transform-origin:left}
.kind{display:flex;margin-top:18px;font:600 15px/1 var(--ui);letter-spacing:.5em;white-space:nowrap}
.kind span{display:inline-block}
.lead{margin-top:18px;max-width:30ch;color:var(--muted);font-size:15px}
/* ---- Hemen Ara ---- */
.call{position:relative;overflow:hidden;display:flex;align-items:center;gap:14px;margin-top:6px;
  padding:18px 18px 18px 22px;border-radius:14px;background:var(--ac);color:var(--ac-ink);text-decoration:none;
  box-shadow:0 20px 40px -24px rgba(var(--ac-rgb),.85);transition:transform .15s,filter .15s}
.call::after{content:"";position:absolute;top:-20%;bottom:-20%;left:-45%;width:30%;pointer-events:none;
  background:linear-gradient(100deg,transparent,rgba(255,255,255,.32),transparent);transform:skewX(-20deg)}
.call:active{transform:scale(.985);filter:brightness(.95)}
.call .t{flex:1;min-width:0}
.call small{display:block;font:600 12px/1 var(--ui);letter-spacing:.24em;opacity:.85}
.call b{display:block;margin-top:9px;font:800 clamp(24px,7.4vw,30px)/1 var(--ui);letter-spacing:-.01em;
  font-variant-numeric:tabular-nums;white-space:nowrap}
.call .ib{flex:none;display:grid;place-items:center;width:48px;height:48px;border-radius:50%;background:rgba(0,0,0,.2)}
.call .ic{width:22px;height:22px;fill:var(--ac-ink)}
/* ---- bağlantılar: numaralı liste ---- */
.list{margin-top:18px;border-top:1px solid var(--line)}
.row{position:relative;display:grid;grid-template-columns:26px 40px minmax(0,1fr) 18px;align-items:center;gap:12px;
  padding:15px 2px;border-bottom:1px solid var(--line);text-decoration:none}
.row::after{content:"";position:absolute;left:0;right:0;bottom:-1px;height:1px;background:var(--ac);transform:scaleX(0);
  transform-origin:left;transition:transform .35s cubic-bezier(.2,.8,.2,1)}
.row:active::after,.row:hover::after{transform:none}
.row .n{font:600 12px/1 var(--ui);letter-spacing:.06em;color:var(--ac);font-variant-numeric:tabular-nums}
.row .ib{display:grid;place-items:center;width:40px;height:40px;border-radius:10px;background:var(--surface);
  border:1px solid var(--line2)}
.row .ic{width:20px;height:20px;fill:var(--text)}
.row b{display:block;font:600 16px/1.2 var(--ui);white-space:nowrap}
.row small{display:block;margin-top:4px;font-size:13px;line-height:1.3;color:var(--muted);overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
.row .go{width:18px;height:18px;fill:none;stroke:var(--dim);stroke-width:2;stroke-linecap:round;stroke-linejoin:round;
  transition:stroke .2s,transform .2s}
.row:active .go,.row:hover .go{stroke:var(--ac);transform:translateX(3px)}
/* ---- ödeme ---- */
.sec{display:flex;align-items:center;gap:12px;margin:42px 0 14px;font:600 12px/1 var(--ui);letter-spacing:.3em;
  color:var(--muted)}
.sec::before{content:"";width:8px;height:8px;background:var(--ac)}
.sec::after{content:"";flex:1;height:1px;background:var(--line)}
.pay{position:relative;overflow:hidden;padding:22px 20px 20px;border-radius:16px;background:var(--surface);
  border:1px solid var(--line);container-type:inline-size}
.pay::before{content:"";position:absolute;left:0;right:0;top:0;height:3px;background:var(--ac);transform-origin:left}
.rows{display:grid;grid-template-columns:auto 1fr;gap:10px 20px;font-size:15px;margin-bottom:18px}
.rows dt{color:var(--muted)}
.rows dd{font-weight:600;text-align:right;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ibanbox{padding:14px 16px 15px;border-radius:12px;background:var(--bg);border:1px solid var(--line2)}
.ibanbox span{display:block;font:600 11px/1 var(--ui);letter-spacing:.3em;color:var(--dim)}
.iban{display:block;margin-top:9px;font:800 17px/1.2 var(--ui);font-size:min(17px,4.45cqi);letter-spacing:-.01em;
  word-spacing:-.02em;font-variant-numeric:tabular-nums;white-space:nowrap;user-select:all;-webkit-user-select:all}
.iban i{font-style:normal;display:inline-block}
.acts{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px}
.acts.one{grid-template-columns:1fr}
.btn{display:flex;align-items:center;justify-content:center;gap:9px;min-height:52px;border-radius:12px;cursor:pointer;
  font:600 15px/1 var(--ui);text-decoration:none;white-space:nowrap;transition:transform .15s,background .2s,border-color .2s}
.btn:active{transform:scale(.97)}
.btn .ic{width:19px;height:19px}
.btn span{white-space:nowrap}
.copy{border:0;background:var(--ac);color:var(--ac-ink)}
.copy .ic{fill:var(--ac-ink)}
.copy.ok{background:var(--ok);color:#fff}
.copy.ok .ic{fill:#fff}
.ghost{border:1px solid var(--line2);background:transparent;color:var(--text)}
.ghost .ic{fill:var(--text)}
.ghost[aria-expanded="true"]{border-color:var(--ac)}
.kk{margin-top:12px;padding:18px 16px 14px;border-radius:14px;background:var(--raise);border:1px solid var(--line);
  text-align:center}
.kk .qr{display:inline-block;padding:12px;border-radius:12px;background:var(--white)}
.kk img{display:block;width:min(220px,58vw);height:auto;image-rendering:pixelated}
.kk p{margin:12px 4px 8px;font-size:14px;color:var(--muted)}
.kk p b{color:var(--text);font-weight:600}
.kk a{color:var(--text);font-weight:600;text-decoration-color:var(--ac);text-underline-offset:4px}
.note{margin-top:12px;font-size:12px;color:var(--dim);text-align:center}
/* ---- altbilgi ---- */
footer{display:flex;justify-content:space-between;align-items:flex-end;gap:12px;margin-top:48px;padding-top:22px;
  border-top:1px solid var(--line);color:var(--dim);font-size:13px}
footer b{display:block;font:800 22px/1 var(--ui);letter-spacing:-.03em;color:var(--text)}
footer b i{display:block;width:34px;height:3px;margin-top:9px;background:var(--ac)}
/* ---- alttaki arama şeridi, bildirim ---- */
.callbar{position:fixed;z-index:20;left:0;right:0;bottom:0;display:flex;justify-content:center;
  padding:12px max(16px,env(safe-area-inset-right,0px)) calc(12px + env(safe-area-inset-bottom,0px)) max(16px,env(safe-area-inset-left,0px));
  background:rgba(10,10,11,.86);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);border-top:1px solid var(--line);
  transform:translateY(110%);transition:transform .35s cubic-bezier(.2,.8,.2,1)}
.callbar.show{transform:none}
.callbar a{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;max-width:440px;min-height:52px;
  border-radius:12px;background:var(--ac);color:var(--ac-ink);text-decoration:none;font:600 16px/1 var(--ui)}
.callbar .ic{width:20px;height:20px;fill:var(--ac-ink)}
.callbar span{font-variant-numeric:tabular-nums}
.toast{position:fixed;z-index:30;left:50%;bottom:calc(92px + env(safe-area-inset-bottom));transform:translate(-50%,40px);
  width:max-content;max-width:calc(100vw - 32px);text-align:center;background:var(--raise);color:var(--text);
  border:1px solid var(--line2);border-left:4px solid var(--ac);padding:12px 18px;border-radius:12px;font-weight:600;
  box-shadow:0 14px 34px rgba(0,0,0,.6);transition:transform .25s,opacity .25s;opacity:0;pointer-events:none}
.toast.show{transform:translate(-50%,0);opacity:1}
/* ---- animasyonlar ---- */
@keyframes grow{from{transform:scaleX(0)}to{transform:none}}
@keyframes slash{from{transform:translateX(160%) skewX(20deg)}to{transform:skewX(20deg)}}
@keyframes wipe{0%{transform:scaleX(0);transform-origin:left}45%,55%{transform:scaleX(1);transform-origin:left}
  56%{transform:scaleX(1);transform-origin:right}100%{transform:scaleX(0);transform-origin:right}}
@keyframes show{0%,49%{opacity:0}50%,100%{opacity:1}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes up{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
@keyframes grp{from{opacity:.15;transform:translateY(8px)}to{opacity:1;transform:none}}
@keyframes left{from{opacity:0;transform:translateX(-16px)}to{opacity:1;transform:none}}
@keyframes shine{0%,82%{left:-45%}100%{left:125%}}
@keyframes ring{0%,84%,100%{transform:none}86%,90%,94%{transform:rotate(-14deg)}88%,92%,96%{transform:rotate(14deg)}}
@keyframes flash{0%{color:var(--ac)}100%{color:var(--text)}}
@keyframes open{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}
.topline{animation:grow .8s cubic-bezier(.6,0,.2,1) both}
.slash{animation:slash 1.1s .15s cubic-bezier(.2,.8,.2,1) both}
.eyebrow{animation:fade .6s .35s both}
.mark .wipe{animation:wipe 1.15s .45s cubic-bezier(.7,0,.2,1) both}
.mark .w{animation:show 1.15s .45s both}
.rule{animation:grow .7s 1.35s cubic-bezier(.2,.8,.2,1) both}
.kind span{animation:up .5s cubic-bezier(.2,.8,.2,1) both}
.lead{animation:fade .7s 2s both}
.call{animation:up .6s 2.05s cubic-bezier(.2,.8,.2,1) both}
.call::after{animation:shine 5s 3s infinite}
.call .ic{animation:ring 5s 3s infinite}
.row{animation:left .55s cubic-bezier(.2,.8,.2,1) both}
.pay::before{transform:scaleX(0)}
.pay.in::before{animation:grow .8s .1s cubic-bezier(.2,.8,.2,1) both}
.pay.in .iban i{animation:grp .45s cubic-bezier(.2,.8,.2,1) both}
.iban.flash{animation:flash .9s ease-out}
.kk.on,.kk:target{animation:open .35s cubic-bezier(.2,.8,.2,1)}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}
  .pay::before{transform:none}}
"""
# hizmet harfleri, satırlar ve IBAN grupları: sırayla
CSS += "".join(f".kind span:nth-child({k + 1}){{animation-delay:{1.55 + 0.04 * k:.2f}s}}" for k in range(24))
CSS += "".join(f".row:nth-child({k + 1}){{animation-delay:{2.15 + 0.08 * k:.2f}s}}" for k in range(8))
CSS += "".join(f".pay.in .iban i:nth-child({k + 1}){{animation-delay:{0.2 + 0.07 * k:.2f}s}}" for k in range(8)) + "\n"

OG_CSS = """
body.og{margin:0;width:1200px;height:630px;overflow:hidden}
.og .wrap{max-width:none;padding:0 100px}.og .hero{padding-block:120px 0}
.og .topline{height:10px}.og .hero{margin:0;padding-inline:0;overflow:visible}
.og .slash{right:-60px;top:-60px;width:330px;height:900px}.og .slash::before{left:-70px;width:28px}
.og .eyebrow{font-size:26px}.og .mark{font-size:min(210px,calc(820px * var(--mk)));margin-top:40px}
.og .rule{width:220px;height:10px;margin-top:40px}.og .kind{font-size:34px;margin-top:36px}
"""


def css(site):
    return CSS + f":root{{--mk:{fit(MARK_FONT, site, 0.12):.4f}}}\n"


def letters(text):
    """Harf harf (sırayla oturan animasyon için); boşluk korunur."""
    return "".join(f'<span>{"&nbsp;" if c == " " else e(c)}</span>' for c in text)


def _mark(site):
    return "".join(f'<span class="w">{e(t)}</span>' for t in site.lines)


def og(site):
    return (f'<div class="topline"></div><div class="wrap"><header class="hero"><div class="slash"></div>'
            f'<p class="eyebrow">{e(site.etiket)}</p><h1 class="mark">{_mark(site)}</h1><div class="rule"></div>'
            f'<p class="kind">{letters(site.hizmet)}</p></header></div>')


def body(site, ctx):
    go = f'<svg class="go" viewBox="0 0 24 24" aria-hidden="true"><path d="{ARROW}"/></svg>'
    links = site.links(vcf_href=ctx.vcf)
    rows = "\n  ".join(
        f'<a class="row" href="{e(L.href)}"{f" download={chr(34)}{e(L.download)}{chr(34)}" if L.download else ""}>'
        f'<span class="n">{k:02d}</span><span class="ib">{svg(L.icon)}</span>'
        f'<span><b>{e(L.title)}</b><small>{e(L.sub)}</small></span>{go}</a>' for k, L in enumerate(links, 1))
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
    groups = " ".join(f"<i>{g}</i>" for g in site.iban_txt.split())
    right = f"@{site.instagram}" if site.instagram else e(site.etiket)
    return f"""<div class="topline" aria-hidden="true"></div>
<div class="wrap">
<header class="hero">
  <div class="slash" aria-hidden="true"></div>
  <p class="eyebrow">{e(site.etiket)}</p>
  <h1 class="mark" aria-label="{e(site.isletme)}">{_mark(site)}<span class="wipe" aria-hidden="true"></span></h1>
  <div class="rule" aria-hidden="true"></div>
  <p class="kind" aria-label="{e(site.hizmet)}">{letters(site.hizmet)}</p>
  <p class="lead">{e(site.aciklama)}</p>
</header>
<main>
<a class="call" href="tel:+{site.tel}"><span class="t"><small>HEMEN ARA</small><b>{e(site.phone)}</b></span>
  <span class="ib">{svg("phone")}</span></a>
<nav class="list" aria-label="Bağlantılar">
  {rows}
</nav>
<h2 class="sec">ÖDEME BİLGİLERİ</h2>
<section class="pay" data-in aria-label="Ödeme bilgileri">
  {f'<dl class="rows">{who}</dl>' if who else ''}
  <div class="ibanbox"><span>IBAN</span><output class="iban">{groups}</output></div>
  <div class="acts{'' if ctx.kk else ' one'}">
    <button class="btn copy" type="button" data-copy="{e(site.iban)}" data-done="Kopyalandı">{svg("copy")}<span>{"Kopyala" if ctx.kk else "IBAN'ı kopyala"}</span></button>{kk_btn}
  </div>{kk_box}{note}
</section>
</main>
<footer>
  <b>{e(" ".join(site.lines))}<i></i></b><span>{right}</span>
</footer>
</div>
<div class="callbar"><a href="tel:+{site.tel}" aria-label="Hemen ara">{svg("phone")}Hemen ara · <span>{e(site.phone)}</span></a></div>"""


JS = ""
