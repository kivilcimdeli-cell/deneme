"""Şablon 1 · Şimşek – Uzar Oto Lastik'in sitesinden (scripts/uzar_sayfa.py).

Dar kalın büyük ad (Barlow Condensed) ve yanında şimşek (işletmenin logo işareti varsa o), sağ üstte üç eğik şerit,
altında akan ok dişli şerit; büyük liste düğmeleri (Hemen Ara renkli), açık renk ödeme kartı (köşesinde eğik şerit),
Rehbere Kaydet. Açılış: şeritler sağdan gelir, şimşek çakar, harf aralığı açılır, düğmeler sırayla yükselir;
sürekli: şimşek arada titrer, Hemen Ara parlar ve telefon çalar.
"""
from .ortak import e, fit, svg

NO, AD, SLUG = 1, "Şimşek", "simsek"
KAYNAK = "Uzar Oto Lastik"
RENK, BG = "#d01c26", "#0d0d0f"
FONTS = {"barlow-black": ("BarlowCondensed-Black.ttf", "Barlow Condensed", 900, "normal"),
         "barlow-xbold": ("BarlowCondensed-ExtraBold.ttf", "Barlow Condensed", 800, "normal"),
         "outfit": ("Outfit-SemiBold.ttf", "Outfit", 600, "normal")}
LICENSES = ("OFL-barlowcondensed.txt", "OFL-outfit.txt")
MARK_FONT = ("BarlowCondensed-Black.ttf", 0.01)
MARK = ".logo .nm"
FITS = ".btn b,.btn small,.iban,.kind,.city,.rows dd,.copy,.kk-open,.ghost"
INTRO_MS = 1800
ORNEK = ("uzar_isimlik", {"marka": "UZAR", "hizmet": "OTO LASTİK", "etiket": "ANTALYA",
                          "aciklama": "Bize tek dokunuşla ulaşın.", "karekod_hata": "m"})
BOLT = "-12,-50 28,-50 6,-10 38,-10 -28,50 -10,4 -38,4"     # Uzar'ın isimliğindeki şimşek


def mark_svg(site, cls="bolt"):
    if site.isaret:
        return f'<svg class="{cls} own" viewBox="{site.isaret_box}" aria-hidden="true">{site.isaret}</svg>'
    return f'<svg class="{cls}" viewBox="-40 -50 80 100" aria-hidden="true"><polygon points="{BOLT}"/></svg>'


def _mark_em(site):
    if site.isaret:
        _, _, w, h = (float(v) for v in site.isaret_box.split())
        return 0.6 * w / h + 0.12
    return 0.73


def favicon(site):
    if site.isaret:
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{site.isaret_box}"><g fill="{site.renk or RENK}">'
                f'{site.isaret}</g></svg>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-40 -50 80 100"><polygon fill="{site.renk or RENK}" '
            f'points="{BOLT}"/></svg>')


def tread_svg():
    """Lastik dişi şeridi (isimlikteki gibi ok biçimli bloklar)."""
    blocks = "".join(f'<polygon points="{x},0 {x + 7},0 {x + 14},7 {x + 7},14 {x},14 {x + 7},7"/>'
                     for x in range(-18, 436, 18))
    return (f'<svg class="tread" viewBox="0 0 400 14" preserveAspectRatio="xMidYMid slice" aria-hidden="true">'
            f'<g class="roll">{blocks}</g></svg>')


CSS = """
:root{color-scheme:dark;--ink:#0d0d0f;--card:#18181b;--line:#2b2b30;--text:#f4f4f2;--muted:#a2a2a8;
  --paper:#f4f4f2;--cond:"Barlow Condensed","Arial Narrow",sans-serif;--ui:"Outfit",system-ui,-apple-system,"Segoe UI",sans-serif}
*{box-sizing:border-box;margin:0}
html{background:var(--ink);-webkit-text-size-adjust:100%}
body{background:var(--ink);color:var(--text);font:600 16px/1.35 var(--ui);min-height:100vh;overflow-x:hidden;
  padding-bottom:env(safe-area-inset-bottom)}
.wrap{--gl:max(16px,env(safe-area-inset-left,0px));--gr:max(16px,env(safe-area-inset-right,0px));
  max-width:460px;margin:0 auto;padding-left:var(--gl);padding-right:var(--gr);padding-block:0 28px}
a{color:inherit;-webkit-tap-highlight-color:transparent}
button{font:inherit;color:inherit}
:focus-visible{outline:2px solid var(--ac);outline-offset:3px}
.hero{position:relative;overflow:hidden;padding:44px 22px 30px;margin:0 calc(var(--gr) * -1) 0 calc(var(--gl) * -1);
  isolation:isolate;--avail:calc(min(100vw,460px) - 84px)}
.hero::before,.hero::after,.hero i{content:"";position:absolute;top:-40px;bottom:-40px;background:var(--ac);
  transform:skewX(-28deg);z-index:-1}
.hero::before{right:-34px;width:58px}
.hero::after{right:54px;width:22px}
.hero i{right:104px;width:9px}
.logo{display:flex;align-items:center;font:900 min(clamp(84px,30vw,128px),calc(var(--avail) * var(--mk)))/.82 var(--cond);
  letter-spacing:.01em;text-transform:uppercase}
.logo .nm{display:flex;flex-direction:column;gap:.04em}
.logo .bolt{flex:none;height:.86em;width:auto;margin-left:.04em;fill:var(--ac);
  filter:drop-shadow(0 0 18px rgba(var(--ac-rgb),.45))}
.logo .bolt.own{height:.6em;margin-left:.12em}
.kind{margin-top:12px;font:800 26px/1 var(--cond);letter-spacing:.34em;color:var(--ac);white-space:nowrap}
.city{margin-top:8px;font-size:13px;letter-spacing:.42em;color:var(--muted);white-space:nowrap}
.tread{display:block;width:calc(100% + var(--gl) + var(--gr));height:14px;
  margin:0 calc(var(--gr) * -1) 22px calc(var(--gl) * -1);fill:var(--ac)}
.lead{color:var(--muted);font-size:15px;margin:0 2px 14px}
.list{display:grid;gap:12px}
.btn{display:flex;align-items:center;gap:14px;min-height:72px;padding:12px 14px;border-radius:18px;
  background:var(--card);border:1px solid var(--line);text-decoration:none;transition:transform .12s,background .12s}
.btn:active{transform:scale(.98)}
.btn .ib{flex:none;display:grid;place-items:center;width:46px;height:46px;border-radius:14px;background:var(--ac)}
.btn .ic{width:24px;height:24px;fill:var(--ac-ink)}
.btn .t{flex:1;min-width:0}
.btn b{display:block;font:800 22px/1.05 var(--cond);letter-spacing:.03em;text-transform:uppercase;white-space:nowrap;
  overflow:hidden;text-overflow:ellipsis}
.btn small{display:block;margin-top:3px;font-size:14px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;
  white-space:nowrap}
.btn .chev{flex:none;width:10px;height:10px;border:solid var(--muted);border-width:2.5px 2.5px 0 0;
  transform:rotate(45deg);margin-right:6px}
.btn.primary{background:linear-gradient(115deg,var(--ac),var(--ac2));border-color:transparent;color:var(--ac-ink);
  box-shadow:0 10px 30px -12px rgba(var(--ac-rgb),.7)}
.btn.primary .ib{background:var(--ac-ink)}
.btn.primary .ic{fill:var(--ac)}
.btn.primary small{color:var(--ac-ink2)}
.btn.primary .chev{border-color:var(--ac-ink2)}
.pay{margin-top:22px;background:var(--paper);color:var(--ink);border-radius:22px;padding:20px 18px 18px;
  position:relative;overflow:hidden;container-type:inline-size}
.pay::after{content:"";position:absolute;right:-18px;top:-30px;width:34px;height:110px;background:var(--ac);
  transform:skewX(-28deg)}
.pay h2{display:flex;align-items:center;gap:8px;font:800 15px/1 var(--ui);letter-spacing:.2em;color:var(--ac-deep)}
.pay h2 .ic{width:20px;height:20px;fill:var(--ac-deep)}
.rows{margin:16px 0 4px;display:grid;grid-template-columns:auto 1fr;gap:6px 14px;font-size:15px}
.rows dt{color:#6b6b72}
.rows dd{font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.iban{margin:12px 0 14px;padding:14px 8px;border-radius:12px;background:#fff;border:1.5px dashed #c9c9cf;
  font:800 18px/1.1 var(--cond);font-size:min(27px,6.6cqi);letter-spacing:.03em;word-spacing:.08em;
  text-align:center;white-space:nowrap;user-select:all;-webkit-user-select:all}
.copy,.kk-open,.ghost{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;min-height:54px;
  border-radius:14px;font:800 20px/1 var(--cond);letter-spacing:.06em;text-transform:uppercase;cursor:pointer;
  text-decoration:none;white-space:nowrap}
.copy{border:0;background:var(--ink);color:#fff}
.copy .ic{width:20px;height:20px;fill:#fff}
.copy.ok{background:#1d7a3a}
.kk-open{margin-top:10px;border:2px solid var(--ink);background:transparent;color:var(--ink)}
.kk-open .ic{width:20px;height:20px;fill:var(--ink)}
.kk-body{padding-top:14px;text-align:center}
.kk-body img{width:min(240px,70vw);height:auto;image-rendering:pixelated;border-radius:8px}
.kk-body p{margin:10px 4px 12px;font-size:14px;color:#4a4a52}
.kk-body a{color:var(--ac-deep);font-weight:600}
.note{margin-top:12px;font-size:12px;color:#7a7a82;text-align:center}
.ghost{margin-top:14px;border:1.5px solid #3a3a40;color:var(--text);background:transparent}
.ghost .ic{width:22px;height:22px;fill:var(--text)}
footer{margin-top:26px;text-align:center;color:#6b6b72;font-size:12px;letter-spacing:.3em}
footer .bolt{height:14px;width:auto;fill:var(--ac);vertical-align:-2px;margin:0 6px}
.toast{position:fixed;left:50%;bottom:calc(22px + env(safe-area-inset-bottom));transform:translate(-50%,140%);
  background:#fff;color:var(--ink);border-left:6px solid var(--ac);padding:12px 18px;border-radius:12px;
  font-weight:600;box-shadow:0 12px 30px rgba(0,0,0,.45);transition:transform .25s,opacity .25s;white-space:nowrap;
  opacity:0;pointer-events:none}
.toast.show{transform:translate(-50%,0);opacity:1}
/* ---- animasyonlar: açılışta sırayla gelir, şimşek arada çakar, lastik dişi döner ---- */
@keyframes stripe{from{transform:translateX(170px) skewX(-28deg)}to{transform:skewX(-28deg)}}
@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes strike{0%{opacity:0;transform:translateY(-40%) scale(.5) rotate(-14deg)}
  55%{opacity:1;transform:translateY(4%) scale(1.12) rotate(3deg);filter:drop-shadow(0 0 34px rgba(var(--ac-rgb),.95)) brightness(1.6)}
  100%{opacity:1;transform:none}}
@keyframes flicker{0%,88%,100%{opacity:1}89%{opacity:.25}90%{opacity:1;filter:drop-shadow(0 0 30px rgba(var(--ac-rgb),.95)) brightness(1.5)}
  92%{opacity:.4}93.5%{opacity:1}}
@keyframes spread{from{opacity:0;letter-spacing:.05em}to{opacity:1;letter-spacing:.34em}}
@keyframes roll{to{transform:translateX(-18px)}}
@keyframes shine{0%{transform:translateX(-130%) skewX(-20deg)}28%,100%{transform:translateX(230%) skewX(-20deg)}}
@keyframes ring{0%,8%,100%{transform:none}1%,5%{transform:rotate(-16deg)}3%,7%{transform:rotate(16deg)}}
@keyframes pop{0%{transform:scale(1)}40%{transform:scale(1.05)}100%{transform:scale(1)}}
@keyframes flash{0%{background:rgba(var(--ac-rgb),.18);border-color:var(--ac)}100%{background:#fff}}
@keyframes open{from{opacity:0;transform:translateY(-8px) scale(.96)}to{opacity:1;transform:none}}
.hero::before{animation:stripe .7s cubic-bezier(.2,.8,.2,1) both}
.hero::after{animation:stripe .7s .07s cubic-bezier(.2,.8,.2,1) both}
.hero i{animation:stripe .7s .14s cubic-bezier(.2,.8,.2,1) both}
.logo{animation:rise .6s .05s cubic-bezier(.2,.8,.2,1) both}
.logo .bolt{transform-origin:50% 60%;animation:strike .55s .3s cubic-bezier(.3,1.4,.5,1) both,flicker 5.5s 2.2s infinite}
.kind{animation:spread .8s .35s cubic-bezier(.2,.8,.2,1) both}
.city,.lead{animation:fade .6s .5s both}
.tread{animation:fade .5s .45s both}
.tread .roll{animation:roll 1.1s linear infinite}
.list .btn{animation:rise .5s cubic-bezier(.2,.8,.2,1) both}
.btn.primary{position:relative;overflow:hidden}
.btn.primary::after{content:"";position:absolute;top:0;bottom:0;left:0;width:45%;pointer-events:none;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.28),transparent);animation:shine 4.5s 1.4s infinite}
.btn.primary .ic{animation:ring 4.5s 1.4s infinite}
.btn:active .ib{transform:scale(.9)}
.btn .ib{transition:transform .12s}
.copy.ok{animation:pop .35s}
.iban.flash{animation:flash .9s ease-out}
.kk-body.on,.kk-body:target{animation:open .35s cubic-bezier(.2,.8,.2,1)}
@keyframes slash{from{transform:translateX(90px) skewX(-28deg)}to{transform:skewX(-28deg)}}
.reveal{animation:rise .6s .7s cubic-bezier(.2,.8,.2,1) both}
.pay::after{animation:slash .7s 1s cubic-bezier(.2,.8,.2,1) both}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
"""

OG_CSS = """
body.og{margin:0;width:1200px;height:630px;overflow:hidden}
.og .hero{margin:0;height:630px;padding:90px 90px 0}
.og .hero::before{right:-60px;width:150px}.og .hero::after{right:150px;width:56px}.og .hero i{right:280px;width:24px}
.og .logo{font-size:min(300px,calc(780px * var(--mk)))}
.og .kind{font-size:62px;margin-top:30px}.og .city{font-size:32px;margin-top:22px}
"""


def css(site):
    delays = "".join(f".list .btn:nth-child({k + 1}){{animation-delay:{.4 + .08 * k:.2f}s}}" for k in range(8))
    return CSS + f":root{{--mk:{fit(MARK_FONT, site, _mark_em(site)):.4f}}}\n" + delays


def _name(site):
    return "".join(f"<span>{e(t)}</span>" for t in site.lines)


def og(site):
    return (f'<header class="hero"><i></i><h1 class="logo"><span class="nm">{_name(site)}</span>{mark_svg(site)}</h1>'
            f'<p class="kind">{e(site.hizmet)}</p><p class="city">{e(site.etiket)}</p></header>')


def body(site, ctx):
    btn = lambda href, icon, t, s, cls="", extra="": (  # noqa: E731
        f'<a class="btn {cls}" href="{e(href)}"{extra}>'
        f'<span class="ib">{svg(icon)}</span><span class="t"><b>{e(t)}</b><small>{e(s)}</small></span>'
        f'<span class="chev"></span></a>')
    titles = {"whatsapp": ("WhatsApp'tan Yaz", f"Mesaj gönderin · {site.phone}"),
              "google": ("Google'da Değerlendirin", "Yorumlar · yorum yapın")}
    rows = [btn("tel:+" + site.tel, "phone", "Hemen Ara", site.phone, "primary")]
    rows += [btn(L.href, L.icon, *titles.get(L.key, (L.title, L.sub))) for L in site.links(rehber=False)]
    who = "".join(f"<dt>{k}</dt><dd>{e(v)}</dd>" for k, v in (("Alıcı", site.alici), ("Banka", site.banka)) if v)
    kk = ""
    if ctx.kk:
        save = "" if ctx.standalone else f'\n      <a href="{ctx.kk}" download="{site.slug}-karekod.png">Karekodu kaydet</a>'
        kk = f"""
  <a class="kk-open" href="#kk" data-toggle="kk" aria-controls="kk" aria-expanded="false">{svg("qr")}Karekod ile Öde</a>
  <div class="kk-body drop" id="kk">
    <img src="{ctx.kk}" width="636" height="636" alt="Ödeme karekodu – {e(site.alici or site.isletme)}">
    <p>Karekodu kaydedin; banka uygulamanızda <b>Karekod ile Öde</b> → <b>Galeriden seç</b>.</p>{save}
  </div>"""
    note = '\n  <p class="note">Örnek IBAN: gerçek bilgiler eklenecek.</p>' if site.iban_ornek else ""
    return f"""<div class="wrap">
<header class="hero"><i></i>
  <h1 class="logo" aria-label="{e(site.isletme)}"><span class="nm">{_name(site)}</span>{mark_svg(site)}</h1>
  <p class="kind">{e(site.hizmet)}</p>
  <p class="city">{e(site.etiket)}</p>
</header>
{tread_svg()}
<p class="lead">{e(site.aciklama)}</p>
<nav class="list">
  {"".join(rows)}
</nav>
<section class="pay reveal" aria-labelledby="odeme">
  <h2 id="odeme">{svg("bank")}ÖDEME BİLGİLERİ</h2>
  {f'<dl class="rows">{who}</dl>' if who else ''}
  <div class="iban" aria-label="IBAN">{e(site.iban_txt)}</div>
  <button class="copy" type="button" data-copy="{e(site.iban)}" data-done="Kopyalandı">{svg("copy")}<span>IBAN'ı Kopyala</span></button>{kk}{note}
</section>
<a class="ghost reveal" href="{ctx.vcf}" download="{e(site.isletme)}.vcf">{svg("person")}Rehbere Kaydet</a>
<footer class="reveal">{e(" ".join(site.lines))}{mark_svg(site)}{e(site.hizmet)}{" · " + e(site.sehir) if site.sehir else ""}</footer>
</div>"""


JS = ""
