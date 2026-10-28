"""Şablon 2 · Lastik izi – İnce Oto Lastik'in sitesinden (scripts/ince_sayfa.py).

Eğik dar kalın büyük ad (Saira Condensed Black Italic, gümüş degrade), arkasından çapraz geçen lastik izi bandı,
üstte yanıp sönen nokta ve etiket; Hemen Ara'da ok biçimli diş baskısı, kutucuklar (3'erli sıra), koyu banka kartı,
sağ altta ara düğmesi. Açılış: bant yuvarlanarak gelir, harfler sırayla yükselir, hizmet soldan açılır; kaydırınca
desenler akar, kart görününce üzerinden ışık geçer.
"""
from .ortak import e, fit, svg, tr_title

NO, AD, SLUG = 2, "Lastik izi", "lastik_izi"
KAYNAK = "İnce Oto Lastik"
RENK, BG = "#e3241b", "#0a0a0a"
FONTS = {"display": ("Saira-CondensedBlackItalic.ttf", "Saira Condensed", 900, "italic"),
         "cond": ("Saira-CondensedBoldItalic.ttf", "Saira Condensed", 700, "italic"),
         "text": ("Saira-Medium.ttf", "Saira", 500, "normal"),
         "text-sb": ("Saira-SemiBold.ttf", "Saira", 600, "normal")}
LICENSES = ("OFL-saira.txt",)
MARK_FONT = ("Saira-CondensedBlackItalic.ttf", 0.03)
MARK = ".mark .ln"
FITS = ".iban,.call b,.tile b,.tile small,.card .who b,.btn,.sub span"
INTRO_MS = 2300
ORNEK = ("ince_isimlik", {"marka": "İNCE", "hizmet": "OTO LASTİK", "etiket": "7/24 HİZMET",
                          "aciklama": "Günün her saati hizmetinizdeyiz.", "karekod_hata": "q"})
STAR = "M12 2.5l2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.3 6.1 20.6l1.3-6.6L2.5 9.4l6.6-.8z"
ARROW = "M7 17L17 7M9 7h8v8"


def tread(kind, color):
    """Diş baskısı karosu (CSS url, döşenir). 'small': tek ok biçimli diş (düğmeler); 'band': ok biçimli orta diş
    ve iki yanda omuz blokları (büyük bant, kart, altbilgi). Oklar gidiş yönüne (sağa) bakar."""
    c = color.replace("#", "%23")
    if kind == "small":
        body = (f"<svg xmlns='http://www.w3.org/2000/svg' width='22' height='30'>"
                f"<path d='M3 3h6l8 12-8 12H3l8-12z' fill='{c}'/></svg>")
    else:
        body = (f"<svg xmlns='http://www.w3.org/2000/svg' width='40' height='120'><g fill='{c}'>"
                "<path d='M5 24h12l15 36-15 36H5l15-36z'/><rect x='9' y='4' width='18' height='12' rx='2'/>"
                "<rect x='9' y='104' width='18' height='12' rx='2'/></g></svg>")
    return f'url("data:image/svg+xml,{body}")'


def favicon(site):
    c = site.renk or RENK
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='14' "
            f"fill='#0a0a0a'/><path d='M16 14h9l13 18-13 18h-9l13-18z' fill='{c}'/>"
            "<path d='M34 14h9l13 18-13 18h-9l13-18z' fill='#f5f5f2'/></svg>")


CSS = """
:root{color-scheme:dark;--bg:#0a0a0a;--card:#141415;--card2:#1b1b1d;--line:#28282b;--line2:#3a3a3e;
  --text:#f5f5f2;--muted:#9d9da4;--dim:#67676d;--ok:#1f9d55;--white:#fff;--star:#f5b400;
  --display:"Saira Condensed","Saira","Arial Narrow",sans-serif;
  --ui:"Saira",system-ui,-apple-system,"Segoe UI",sans-serif;
  --tread-dark:TREAD_SMALL_DARK;--tread-band:TREAD_BAND_GREY;--tread-light:TREAD_BAND_LIGHT}
*{box-sizing:border-box;margin:0}
html{background:var(--bg);-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--text);font:500 16px/1.45 var(--ui);min-height:100vh;overflow-x:hidden;
  padding-bottom:env(safe-area-inset-bottom)}
.wrap{--gl:max(16px,env(safe-area-inset-left,0px));--gr:max(16px,env(safe-area-inset-right,0px));
  max-width:480px;margin:0 auto;padding-left:var(--gl);padding-right:var(--gr);padding-block:0 92px}
a{color:inherit;-webkit-tap-highlight-color:transparent}
button{font:inherit;color:inherit}
:focus-visible{outline:2px solid var(--ac);outline-offset:3px}
.bleed{margin-left:calc(var(--gl) * -1);margin-right:calc(var(--gr) * -1)}
/* ---- başlık ---- */
.hero{position:relative;overflow:hidden;isolation:isolate;padding:44px var(--gr) 34px var(--gl);
  background:radial-gradient(80% 60% at 100% 0%,rgba(var(--ac-rgb),.22),transparent 65%),var(--bg);
  --avail:calc(min(100vw,480px) - 36px)}
.band{position:absolute;z-index:-1;left:-40%;right:-40%;top:118px;height:150px;transform:rotate(-12deg);
  overflow:hidden;background:#111112;box-shadow:inset 0 1px 0 rgba(255,255,255,.05),inset 0 -1px 0 rgba(255,255,255,.05);
  -webkit-mask-image:linear-gradient(90deg,transparent 14%,#000 34%,#000 74%,transparent 92%);
  mask-image:linear-gradient(90deg,transparent 14%,#000 34%,#000 74%,transparent 92%)}
.band i{position:absolute;inset:0 -400px;background:var(--tread-band) 0 0/auto 100% repeat-x;
  background-position:calc(var(--sc) * -.8) 0}
.tag{display:inline-flex;align-items:center;gap:9px;font:700 italic 15px/1 var(--display);letter-spacing:.14em}
.live{width:8px;height:8px;border-radius:50%;background:var(--ac);box-shadow:0 0 0 0 rgba(var(--ac-rgb),.7)}
.mark{display:flex;flex-direction:column;margin:14px 0 0 -.03em;
  font:900 italic min(200px,49vw,calc(var(--avail) * var(--mk)))/.8 var(--display);letter-spacing:-.01em;
  filter:drop-shadow(0 14px 22px rgba(0,0,0,.6))}
.mark .ln{display:flex}
.mark .l{display:block;padding:.1em .02em 0;background:linear-gradient(180deg,#fff 30%,#c9c9c9);
  -webkit-background-clip:text;background-clip:text;color:transparent}
.sub{display:flex;align-items:center;gap:14px;margin-top:12px}
.sub span{font:900 italic 34px/1 var(--display);letter-spacing:.03em;color:var(--ac);white-space:nowrap}
.sub::after{content:"";flex:1;height:3px;background:linear-gradient(90deg,var(--ac),transparent);transform:skewX(-20deg)}
.lead{margin-top:10px;color:var(--muted);font-size:16px}
/* ---- Hemen Ara ---- */
.call{position:relative;overflow:hidden;isolation:isolate;display:flex;align-items:center;gap:14px;margin-top:6px;
  padding:20px 18px 20px 22px;border-radius:16px;text-decoration:none;color:var(--ac-ink);
  background:linear-gradient(115deg,var(--ac),var(--ac2));box-shadow:0 22px 44px -24px rgba(var(--ac-rgb),.9);
  transition:transform .15s}
.call::before{content:"";position:absolute;inset:-2px;z-index:-1;background:var(--tread-dark) 0 0/22px 30px;opacity:.2;
  -webkit-mask-image:linear-gradient(100deg,transparent 30%,#000 90%);mask-image:linear-gradient(100deg,transparent 30%,#000 90%)}
.call::after{content:"";position:absolute;top:0;bottom:0;left:0;width:38%;z-index:-1;pointer-events:none;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.28),transparent);transform:translateX(-140%) skewX(-20deg)}
.call:active{transform:scale(.985)}
.call .t{flex:1;min-width:0}
.call small{display:block;font:700 italic 15px/1 var(--display);letter-spacing:.16em;color:var(--ac-ink2)}
.call b{display:block;margin-top:6px;font:900 italic clamp(30px,9.4vw,40px)/1 var(--display);letter-spacing:.01em;
  font-variant-numeric:tabular-nums;white-space:nowrap}
.call .ib{flex:none;display:grid;place-items:center;width:52px;height:52px;border-radius:50%;background:var(--ac-ink);
  box-shadow:0 0 0 7px rgba(255,255,255,.14)}
.call .ib .ic{width:24px;height:24px;fill:var(--ac)}
/* ---- kutucuklar ---- */
.tiles{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;margin-top:10px}
.tile{position:relative;overflow:hidden;isolation:isolate;display:flex;flex-direction:column;justify-content:space-between;
  gap:18px;min-height:112px;padding:14px 12px 13px;border-radius:14px;background:var(--card);border:1px solid var(--line);
  text-decoration:none;transition:transform .15s,border-color .15s;grid-column:span var(--span,2)}
.tile::after{content:"";position:absolute;z-index:-1;right:-12px;bottom:-22px;width:64px;height:120px;
  background:var(--tread-light) 0 0/auto 60px;opacity:.06;transform:rotate(-12deg)}
.tile:active{transform:scale(.97);border-color:var(--line2)}
.tile .ic{width:24px;height:24px;fill:var(--text)}
.tile .go{position:absolute;top:12px;right:11px;width:16px;height:16px;fill:none;stroke:var(--dim);stroke-width:2.2;
  stroke-linecap:round;stroke-linejoin:round}
.tile b{display:block;font:700 italic 18px/1 var(--display);letter-spacing:.03em;text-transform:uppercase;white-space:nowrap}
.tile small{display:block;margin-top:4px;font-size:12px;line-height:1.2;color:var(--muted);overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
.stars{display:flex;gap:1px;margin-top:5px}
.stars svg{width:12px;height:12px;fill:var(--star)}
/* ---- ödeme ---- */
.sec{display:flex;align-items:center;gap:12px;margin:34px 0 14px;font:900 italic 22px/1 var(--display);
  letter-spacing:.05em}
.sec::before{content:"";width:14px;height:22px;background:var(--ac);transform:skewX(-16deg)}
.sec::after{content:"";flex:1;height:1px;background:var(--line)}
.card{position:relative;overflow:hidden;isolation:isolate;display:flex;flex-direction:column;gap:22px;
  padding:20px 20px 18px;border-radius:18px;container-type:inline-size;
  background:radial-gradient(120% 90% at 0% 0%,rgba(var(--ac-rgb),.16),transparent 55%),
             linear-gradient(140deg,#1f1f22,#121214 60%,#0c0c0d);
  border:1px solid var(--line2);box-shadow:0 30px 50px -32px #000,inset 0 1px 0 rgba(255,255,255,.07)}
.card::before{content:"";position:absolute;z-index:-1;top:-60px;right:-36px;width:92px;height:340px;
  background:var(--tread-light) 0 0/auto 92px;background-position:0 calc(var(--sc) * -.32);opacity:.07;
  transform:rotate(-24deg)}
.card::after{content:"";position:absolute;inset:0;z-index:1;pointer-events:none;
  background:linear-gradient(105deg,transparent 35%,rgba(255,255,255,.16) 50%,transparent 65%);transform:translateX(-120%)}
.card .top{display:flex;justify-content:space-between;align-items:center}
.card .bank{font:600 16px/1 var(--ui)}
.card .kind{font:700 italic 13px/1 var(--display);letter-spacing:.2em;color:var(--muted)}
.iban{font:600 18px/1.1 var(--ui);font-size:min(20px,5cqi);letter-spacing:.025em;word-spacing:.06em;
  font-variant-numeric:tabular-nums;white-space:nowrap;user-select:all;-webkit-user-select:all}
.card .who small{display:block;font:700 italic 11px/1 var(--display);letter-spacing:.22em;color:var(--dim)}
.card .who b{display:block;margin-top:6px;font:900 italic 21px/1 var(--display);letter-spacing:.04em;white-space:nowrap}
.acts{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px}
.acts.one{grid-template-columns:1fr}
.btn{display:flex;align-items:center;justify-content:center;gap:9px;width:100%;min-height:54px;border-radius:13px;
  font:700 italic 17px/1 var(--display);letter-spacing:.06em;text-transform:uppercase;cursor:pointer;white-space:nowrap;
  text-decoration:none;transition:transform .15s,background .2s}
.btn:active{transform:scale(.97)}
.btn .ic{width:19px;height:19px}
.copy{border:0;background:var(--white);color:#0a0a0a}
.copy .ic{fill:#0a0a0a}
.copy.ok{background:var(--ok);color:#fff}
.copy.ok .ic{fill:#fff}
.ghost{border:1px solid var(--line2);background:transparent;color:var(--text)}
.ghost .ic{fill:var(--text)}
.ghost[aria-expanded="true"]{background:var(--card2)}
.kk{margin-top:12px;padding:18px 16px 16px;border-radius:16px;background:var(--card);border:1px solid var(--line);
  text-align:center}
.kk .qr{display:inline-block;padding:12px;border-radius:12px;background:var(--white)}
.kk img{display:block;width:min(230px,62vw);height:auto;image-rendering:pixelated}
.kk p{margin:12px 4px 8px;font-size:14px;color:var(--muted)}
.kk p b{color:var(--text);font-weight:600}
.kk a{color:var(--text);font-weight:600;text-underline-offset:3px}
.note{margin-top:10px;font-size:12px;color:var(--dim);text-align:center}
.save{margin-top:12px}
/* ---- altbilgi ---- */
footer{margin-top:38px}
.strip{height:26px;background:var(--tread-light) 0 0/auto 100% repeat-x;opacity:.08;
  background-position:calc(var(--sc) * -.48) 0;
  -webkit-mask-image:linear-gradient(90deg,transparent,#000 15%,#000 85%,transparent);
  mask-image:linear-gradient(90deg,transparent,#000 15%,#000 85%,transparent)}
footer p{display:flex;justify-content:space-between;align-items:baseline;gap:12px;margin-top:16px;color:var(--dim);
  font-size:13px}
footer b{font:900 italic 17px/1 var(--display);letter-spacing:.05em;color:var(--text)}
footer b span{color:var(--ac)}
/* ---- kayan ara düğmesi, bildirim ---- */
.fab{position:fixed;z-index:20;right:calc(16px + env(safe-area-inset-right,0px));
  bottom:calc(18px + env(safe-area-inset-bottom,0px));display:grid;place-items:center;width:58px;height:58px;
  border-radius:50%;background:var(--ac);box-shadow:0 14px 30px -8px rgba(var(--ac-rgb),.75),0 0 0 6px rgba(var(--ac-rgb),.18);
  transform:scale(0);transition:transform .35s cubic-bezier(.3,1.5,.5,1);text-decoration:none}
.fab.show{transform:scale(1)}
.fab .ic{width:26px;height:26px;fill:var(--ac-ink)}
.toast{position:fixed;z-index:30;left:50%;bottom:calc(90px + env(safe-area-inset-bottom));transform:translate(-50%,40px);
  width:max-content;max-width:calc(100vw - 32px);text-align:center;background:var(--card2);color:var(--text);
  border:1px solid var(--line2);border-left:4px solid var(--ac);padding:12px 18px;border-radius:12px;font-weight:600;
  box-shadow:0 14px 34px rgba(0,0,0,.6);transition:transform .25s,opacity .25s;opacity:0;pointer-events:none}
.toast.show{transform:translate(-50%,0);opacity:1}
/* ---- animasyonlar ---- */
@keyframes bandin{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
@keyframes rollin{from{transform:translateX(-360px)}to{transform:none}}
@keyframes letter{from{opacity:0;transform:translateY(46%)}to{opacity:1;transform:none}}
@keyframes wipe{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 -10% 0 0)}}
@keyframes grow{from{transform:scaleX(0) skewX(-20deg)}to{transform:skewX(-20deg)}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes rise{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:none}}
@keyframes treadin{from{background-position:-220px 0}to{background-position:0 0}}
@keyframes shine{0%,70%{transform:translateX(-140%) skewX(-20deg)}100%{transform:translateX(300%) skewX(-20deg)}}
@keyframes ring{0%,84%,100%{transform:none}86%,90%,94%{transform:rotate(-15deg)}88%,92%,96%{transform:rotate(15deg)}}
@keyframes ringonce{0%,100%{transform:none}15%,45%,75%{transform:rotate(-15deg)}30%,60%,90%{transform:rotate(15deg)}}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(var(--ac-rgb),.7)}75%,100%{box-shadow:0 0 0 10px rgba(var(--ac-rgb),0)}}
@keyframes sweep{from{transform:translateX(-120%)}to{transform:translateX(120%)}}
@keyframes flash{0%{color:var(--ac)}100%{color:var(--text)}}
@keyframes open{from{opacity:0;transform:translateY(-8px) scale(.98)}to{opacity:1;transform:none}}
.band{animation:bandin 1.1s .05s cubic-bezier(.5,0,.2,1) both}
.band i{animation:rollin 1.7s .05s cubic-bezier(.1,.6,.2,1) both}
.tag{animation:fade .5s .25s both}
.live{animation:pulse 2s 1.5s infinite}
.mark .l{animation:letter .75s cubic-bezier(.2,1.25,.35,1) both}
.sub span{animation:wipe .6s .8s cubic-bezier(.6,0,.2,1) both}
.sub::after{transform-origin:left;animation:grow .7s .95s cubic-bezier(.2,.8,.2,1) both}
.lead{animation:fade .6s 1.05s both}
.call{animation:rise .6s 1.05s cubic-bezier(.2,.8,.2,1) both}
.call::before{animation:treadin 1.6s 1.05s cubic-bezier(.1,.6,.2,1) both}
.call::after{animation:shine 6s 2.6s infinite}
.call .ib .ic{animation:ringonce .8s 1.8s,ring 6s 2.6s infinite}
.tile{animation:rise .55s cubic-bezier(.2,.8,.2,1) both}
.card.in::after{animation:sweep 1.1s .15s cubic-bezier(.4,0,.2,1)}
.card.in .iban{animation:flash 1.2s .3s}
.strip.in{animation:treadin 1.4s cubic-bezier(.1,.6,.2,1)}
.iban.flash{animation:flash .9s ease-out}
.kk.on,.kk:target{animation:open .35s cubic-bezier(.2,.8,.2,1)}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
"""
CSS = (CSS.replace("TREAD_SMALL_DARK", tread("small", "#000")).replace("TREAD_BAND_GREY", tread("band", "#202023"))
       .replace("TREAD_BAND_LIGHT", tread("band", "#ffffff")))

OG_CSS = """
body.og{margin:0;width:1200px;height:630px;overflow:hidden}
.og .hero{width:1200px;height:630px;margin:0;padding:80px 90px 0}
.og .band{top:250px;height:260px}.og .tag{font-size:30px;gap:16px}.og .live{width:16px;height:16px}
.og .mark{font-size:min(330px,calc(1000px * var(--mk)));margin-top:26px}.og .sub span{font-size:70px}
.og .sub{margin-top:22px}.og .sub::after{height:6px}
"""


def _rows(n):
    """Kutucuklar 6 sütunluk ızgarada: sırada 3, 2 ya da 1 kutucuk (genişlik 2, 3 ya da 6)."""
    out = []
    while n > 0:
        k = 3 if n >= 5 or n == 3 else min(n, 2)
        out += [6 // k] * k
        n -= k
    return out


def css(site):
    tiles = len(site.links(rehber=False))
    return (CSS + f":root{{--mk:{fit(MARK_FONT, site, 0.08):.4f}}}\n"
            + "".join(f".tile:nth-child({k + 1}){{animation-delay:{1.2 + .08 * k:.2f}s}}" for k in range(tiles)) + "\n")


def _mark(site):
    k, lines = 0, []
    for t in site.lines:
        spans = []
        for c in t:
            spans.append(f'<span class="l" style="animation-delay:{.35 + .08 * k:.2f}s">{e(c)}</span>' if c != " "
                         else '<span class="l">&nbsp;</span>')
            k += 1
        lines.append(f'<span class="ln">{"".join(spans)}</span>')
    return "".join(lines)


def og(site):
    return (f'<div class="hero"><div class="band"><i></i></div><p class="tag"><span class="live"></span>'
            f'{e(site.etiket)}</p><h1 class="mark">{_mark(site)}</h1><p class="sub"><span>{e(site.hizmet)}</span></p></div>')


def body(site, ctx):
    go = f'<svg class="go" viewBox="0 0 24 24" aria-hidden="true"><path d="{ARROW}"/></svg>'
    stars = '<span class="stars" aria-label="5 yıldız">' + "".join(
        f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="{STAR}"/></svg>' for _ in range(5)) + "</span>"
    subs = {"konum": site.konum or tr_title(site.sehir)}
    links = site.links(rehber=False)
    tiles = "\n  ".join(
        f'<a class="tile" href="{e(L.href)}" style="--span:{s}">{svg(L.icon)}{go}<span><b>{e(L.title if L.key == "google" else L.short)}</b>'
        f'{stars if L.key == "google" else "<small>" + e(subs.get(L.key, L.sub)) + "</small>"}</span></a>'
        for L, s in zip(links, _rows(len(links))))
    kk_btn = kk_box = ""
    if ctx.kk:
        save = "" if ctx.standalone else f'\n    <a href="{ctx.kk}" download="{site.slug}-karekod.png">Karekodu kaydet</a>'
        kk_btn = (f'\n    <a class="btn ghost" href="#kk" data-toggle="kk" aria-controls="kk" aria-expanded="false">'
                  f'{svg("qr")}Karekod</a>')
        kk_box = f"""
  <div class="kk drop" id="kk">
    <span class="qr"><img src="{ctx.kk}" width="732" height="732" alt="Ödeme karekodu – {e(site.alici or site.isletme)}"></span>
    <p>Karekodu kaydedin, banka uygulamanızda <b>Karekod ile Öde</b>, ardından <b>Galeriden seç</b>.</p>{save}
  </div>"""
    who = f'\n    <div class="who"><small>ALICI</small><b>{e(site.alici)}</b></div>' if site.alici else ""
    note = '\n  <p class="note">Örnek IBAN: gerçek bilgiler eklenecek.</p>' if site.iban_ornek else ""
    right = f"@{site.instagram}" if site.instagram and not site.etiket else tr_title(site.etiket)
    return f"""<div class="wrap">
<header class="hero bleed">
  <div class="band" aria-hidden="true"><i></i></div>
  <p class="tag"><span class="live"></span>{e(site.etiket)}</p>
  <h1 class="mark" aria-label="{e(site.isletme)}">{_mark(site)}</h1>
  <p class="sub"><span>{e(site.hizmet)}</span></p>
  <p class="lead">{e(site.aciklama)}</p>
</header>
<main>
<a class="call" href="tel:+{site.tel}"><span class="t"><small>HEMEN ARA</small><b>{e(site.phone)}</b></span>
  <span class="ib">{svg("phone")}</span></a>
<nav class="tiles" aria-label="Bağlantılar">
  {tiles}
</nav>
<section aria-labelledby="odeme">
  <h2 class="sec" id="odeme">ÖDEME BİLGİLERİ</h2>
  <div class="card" data-in>
    <div class="top"><span class="bank">{e(site.banka or "Banka hesabı")}</span><span class="kind">IBAN</span></div>
    <div class="iban">{e(site.iban_txt)}</div>{who}
  </div>
  <div class="acts{'' if ctx.kk else ' one'}">
    <button class="btn copy" type="button" data-copy="{e(site.iban)}" data-done="Kopyalandı">{svg("copy")}<span>{"Kopyala" if ctx.kk else "IBAN'ı kopyala"}</span></button>{kk_btn}
  </div>{kk_box}{note}
</section>
<a class="btn ghost save" href="{ctx.vcf}" download="{e(site.isletme)}.vcf">{svg("person")}Rehbere kaydet</a>
</main>
<footer>
  <div class="strip bleed" data-in aria-hidden="true"></div>
  <p><b>{e(" ".join(site.lines))} <span>{e(site.hizmet)}</span></b><span>{e(right)}</span></p>
</footer>
</div>
<a class="fab" href="tel:+{site.tel}" aria-label="Hemen ara">{svg("phone")}</a>"""


JS = ""
