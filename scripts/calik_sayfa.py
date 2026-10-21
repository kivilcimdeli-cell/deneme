"""ÇALIK OTO LASTİK – işletme sayfası (koyu tema, sarı vurgu; telefona göre).

Uzar ve İnce'nin sayfalarıyla aynı işler, ayrı tasarım: sade ve kurumsal. Koyu zemin, tek yazı tipi (Manrope),
her şey aynı sol hizada; sarı yalnız vurgu: ÇALIK'ın sonundaki nokta, OTO LASTİK, Hemen Ara düğmesi, IBAN çizgisi.
İsimliklerdeki ikaz şeridi sayfanın en üstünde ve altbilgide ince bir şerit olarak.

Animasyon:
  açılış   ikaz şeridi kayarak gelir, arkada sarı ışık süzülür, ÇALIK harf harf maskeden yükselir, sarı nokta belirir,
           OTO LASTİK harf aralığı daralarak oturur, düğmeler sırayla gelir
  kaydırma ikaz şeritleri kaydırdıkça akar; ödeme kartı görünce IBAN çizgisi uzar; Hemen Ara ekrandan çıkınca altta
           arama şeridi belirir
  sürekli  Hemen Ara birkaç saniyede bir hafifçe parlar ve telefon simgesi çalar
"Hareketi azalt" açıksa hiçbiri oynamaz.

Sayfada: Hemen Ara, WhatsApp (hazır mesajlı), Instagram, Google yorumları (işletmenin paylaşım bağlantısı), ödeme
bilgileri (alıcı, banka, IBAN + tek dokunuşla kopyala, banka karekodu: kaydedip banka uygulamasında galeriden
okutulur) ve Rehbere Kaydet (vCard). Dış bağlantı yok: yazı tipleri ve simgeler sayfanın içinde.

Bilgiler `calik_isimlik/bilgiler.json`dan okunur (scripts/qr_sistemi.py doğrular). Banka karekodu bankanın
verdiğiyle aynı baytlarla ve aynı hata düzeltmeyle (H) yeniden çizilir.

Yayın: ortak Cloudflare hesabında (`qrsistem`) `calikotolastik` adlı Worker'a `calik_site.zip` yüklenir; kesin adres
`bilgiler.json` → `sayfa_url`a yazılır ve bu komut yeniden çalıştırılır (paylaşım kartı adresi kullanır).

Çıktı : calik_isimlik/site/, calik_isimlik/calik_site.zip, sayfa_onizleme.png, sayfa_tur.gif, sayfa_onizleme.html,
        sayfa_artifact.html (Claude önizlemesi)

Kullanım:
  python3 scripts/calik_sayfa.py
"""
import base64
import html
import io
import os
import sys
import zipfile

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import qr_sistemi as Q  # noqa: E402
import uzar_sayfa as S  # noqa: E402
from ince_sayfa import _finish, _gif, _seek  # noqa: E402

BASE = os.path.join(A.ROOT, "calik_isimlik")
DATA = os.path.join(BASE, "bilgiler.json")
OUT = os.path.join(BASE, "site")
ZIP = os.path.join(BASE, "calik_site.zip")
PREVIEW = os.path.join(BASE, "sayfa_onizleme.png")
TOUR = os.path.join(BASE, "sayfa_tur.gif")
STANDALONE = os.path.join(BASE, "sayfa_onizleme.html")
ARTIFACT = os.path.join(BASE, "sayfa_artifact.html")
# Manrope (OFL): değişken yazı tipinden sabit kesimler, latin + latin-ext birleşik
FONTS = {"text": "Manrope-Medium.ttf", "text-sb": "Manrope-SemiBold.ttf", "text-xb": "Manrope-ExtraBold.ttf"}
LICENSES = ("OFL-manrope.txt",)
CHROMIUM = "/opt/pw-browsers/chromium"
NAME = "ÇALIK"


# ---------------------------------------------------------------- dosyalar

def subset_fonts():
    from fontTools import subset
    os.makedirs(os.path.join(OUT, "fonts"), exist_ok=True)
    for fn in os.listdir(os.path.join(OUT, "fonts")):           # eski yazı tipleri zip'e girmesin
        os.remove(os.path.join(OUT, "fonts", fn))
    for key, fn in FONTS.items():
        opts = subset.Options()
        opts.flavor = "woff"
        opts.layout_features = ["kern", "liga", "locl", "tnum"]
        f = subset.load_font(os.path.join(A.FONT_DIR, fn), opts)
        s = subset.Subsetter(opts)
        s.populate(text=S.CHARS)
        s.subset(f)
        subset.save_font(f, os.path.join(OUT, "fonts", key + ".woff"), opts)
    for lic in LICENSES:
        with open(os.path.join(A.FONT_DIR, lic), "rb") as src, open(os.path.join(OUT, "fonts", lic), "wb") as dst:
            dst.write(src.read())


def karekod_png(info):
    """Banka karekodu: bankanınkiyle aynı baytlar (ECI yok) ve aynı hata düzeltme (Enpara: H)."""
    import segno
    import zxingcpp
    path = os.path.join(OUT, "karekod.png")
    segno.make(info.karekod, error="h", mode="byte", encoding="utf-8", eci=False, micro=False,
               boost_error=False).save(path, scale=12, border=4)
    r = zxingcpp.read_barcodes(Image.open(path).convert("L"))
    assert len(r) == 1 and r[0].text == info.karekod and r[0].bytes == info.karekod.encode("utf-8"), "karekod"
    return path


def vcard(info):
    lines = ["BEGIN:VCARD", "VERSION:3.0", "N:;Çalık Oto Lastik;;;", "FN:Çalık Oto Lastik", "ORG:Çalık Oto Lastik",
             f"TEL;TYPE=CELL,VOICE:+{info.tel}"] + ([f"URL:{info.page}"] if info.page else []) + [
             f"X-SOCIALPROFILE;TYPE=instagram:https://www.instagram.com/{info.instagram}/",
             f"NOTE:IBAN {Q.iban_display(info.iban)} ({info.holder.title()}\\, {info.bank})", "END:VCARD"]
    with open(os.path.join(OUT, "calik.vcf"), "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(lines) + "\n")


def data_uri(fn, mime):
    return f"data:{mime};base64," + base64.b64encode(open(os.path.join(OUT, fn), "rb").read()).decode()


def embed_fonts(css):
    for key in FONTS:
        css = css.replace(f"url(fonts/{key}.woff)", f"url({data_uri('fonts/' + key + '.woff', 'font/woff')})")
    return css


def wordmark(text=NAME):
    """ÇALIK: her harf maskenin altından yükselir; sonunda sarı nokta."""
    return "".join(f'<span class="ch"><span>{c}</span></span>' for c in text) + '<i class="dot"></i>'


# ---------------------------------------------------------------- sayfa

CSS = """
@font-face{font-family:"Manrope";font-weight:500;font-display:swap;src:url(fonts/text.woff) format("woff")}
@font-face{font-family:"Manrope";font-weight:600;font-display:swap;src:url(fonts/text-sb.woff) format("woff")}
@font-face{font-family:"Manrope";font-weight:800;font-display:swap;src:url(fonts/text-xb.woff) format("woff")}
/* koyu, tek sütun, sol hizalı; sarı yalnız vurgu (nokta, çizgi, Hemen Ara). Ölçek: 12 · 14 · 16 · 20 · 26 · büyük */
:root{color-scheme:dark;--bg:#0b0b0c;--surface:#141416;--raise:#1b1b1e;--line:#26262a;--line2:#36363b;
  --text:#f4f4f1;--muted:#9a9aa1;--dim:#66666d;--yellow:#ffc814;--yellow-ink:#1a1400;--ok:#1f9d55;--white:#fff;
  --ui:"Manrope",system-ui,-apple-system,"Segoe UI",sans-serif;
  --stripe:repeating-linear-gradient(-45deg,#0b0b0c 0 9px,var(--yellow) 9px 18px);--roll:0px}
*{box-sizing:border-box;margin:0}
html{background:var(--bg);-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--text);font:500 16px/1.5 var(--ui);min-height:100vh;overflow-x:hidden}
a{color:inherit;-webkit-tap-highlight-color:transparent}
button{font:inherit;color:inherit}
:focus-visible{outline:2px solid var(--yellow);outline-offset:3px}
.wrap{max-width:480px;margin:0 auto;padding-left:max(20px,env(safe-area-inset-left,0px));
  padding-right:max(20px,env(safe-area-inset-right,0px));padding-block:0 calc(110px + env(safe-area-inset-bottom,0px))}
.stripe{height:6px;background:var(--stripe);background-position:calc(var(--roll) * -1) 0}
/* ---- başlık ---- */
.hero{position:relative;isolation:isolate;padding-block:40px 34px}
.hero::before{content:"";position:absolute;z-index:-1;inset:-40px -20px 0;pointer-events:none;
  background:radial-gradient(55% 55% at 85% 20%,rgba(255,200,20,.16),transparent 70%)}
.mark{display:flex;align-items:flex-end;margin-top:0;font:800 clamp(78px,25vw,112px)/.86 var(--ui);
  letter-spacing:-.04em}
.mark .ch{display:block;overflow:hidden;padding-top:.06em;padding-bottom:.2em;margin-bottom:-.2em}
.mark .ch span{display:block}
.mark .dot{width:.16em;height:.16em;margin:0 0 .02em .06em;background:var(--yellow);flex:none}
.kind{display:flex;align-items:center;gap:14px;margin-top:max(26px,.3em);font:800 15px/1 var(--ui);letter-spacing:.5em;
  color:var(--yellow)}
.kind::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--line2),transparent)}
.lead{margin-top:18px;max-width:30ch;color:var(--muted);font-size:16px}
/* ---- Hemen Ara ---- */
.call{position:relative;display:flex;align-items:center;gap:14px;margin-top:6px;padding:18px 16px 18px 22px;
  border-radius:16px;background:var(--yellow);color:var(--yellow-ink);text-decoration:none;
  box-shadow:0 18px 40px -22px rgba(255,200,20,.7);transition:transform .15s,filter .15s}
.call:active{transform:scale(.985);filter:brightness(.96)}
.call .t{flex:1;min-width:0}
.call small{display:block;font:800 12px/1 var(--ui);letter-spacing:.22em;opacity:.72}
.call b{display:block;margin-top:8px;font:800 clamp(25px,7.6vw,31px)/1 var(--ui);letter-spacing:-.01em;
  font-variant-numeric:tabular-nums;white-space:nowrap}
.call .ib{flex:none;display:grid;place-items:center;width:50px;height:50px;border-radius:50%;background:var(--bg)}
.call .ib .ic{width:23px;height:23px;fill:var(--yellow)}
/* ---- bağlantılar ---- */
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}
.tile{position:relative;display:flex;flex-direction:column;justify-content:space-between;gap:26px;min-height:124px;
  padding:16px;border-radius:16px;background:var(--surface);border:1px solid var(--line);text-decoration:none;
  transition:background .15s,border-color .15s,transform .15s}
.tile:active{transform:scale(.98);background:var(--raise);border-color:var(--line2)}
.tile .ib{display:grid;place-items:center;width:40px;height:40px;border-radius:11px;background:var(--raise);
  border:1px solid var(--line2)}
.tile .ic{width:21px;height:21px;fill:var(--yellow)}
.tile .go{position:absolute;top:16px;right:16px;width:16px;height:16px;fill:none;stroke:var(--dim);stroke-width:2;
  stroke-linecap:round;stroke-linejoin:round;transition:stroke .15s,transform .15s}
.tile:active .go{stroke:var(--yellow);transform:translate(2px,-2px)}
.tile b{display:block;font:800 16px/1.2 var(--ui)}
.tile small{display:block;margin-top:3px;font-size:13px;line-height:1.3;color:var(--muted);overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
/* ---- ödeme ---- */
.sec{display:flex;align-items:center;gap:12px;margin:40px 0 14px;font:800 12px/1 var(--ui);letter-spacing:.32em;
  color:var(--muted)}
.sec::after{content:"";flex:1;height:1px;background:var(--line)}
.pay{padding:20px;border-radius:18px;background:var(--surface);border:1px solid var(--line);container-type:inline-size}
.rows{display:grid;grid-template-columns:auto 1fr;gap:10px 20px;font-size:15px}
.rows dt{color:var(--muted)}
.rows dd{font-weight:800;text-align:right}
.ibanbox{position:relative;margin-top:18px;padding:14px 14px 15px 18px;border-radius:12px;background:var(--bg);
  border:1px solid var(--line2);overflow:hidden}
.ibanbox::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--yellow);transform-origin:top}
.ibanbox span{display:block;font:800 11px/1 var(--ui);letter-spacing:.3em;color:var(--dim)}
.iban{display:block;margin-top:8px;font:800 18px/1.2 var(--ui);font-size:min(19px,4.85cqi);letter-spacing:.005em;
  word-spacing:.05em;font-variant-numeric:tabular-nums;white-space:nowrap;user-select:all;-webkit-user-select:all}
.acts{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px}
.btn{display:flex;align-items:center;justify-content:center;gap:9px;min-height:52px;border-radius:12px;cursor:pointer;
  font:800 15px/1 var(--ui);text-decoration:none;transition:transform .15s,background .2s,border-color .2s}
.btn:active{transform:scale(.97)}
.btn .ic{width:19px;height:19px}
.copy{border:0;background:var(--yellow);color:var(--yellow-ink)}
.copy .ic{fill:var(--yellow-ink)}
.copy.ok{background:var(--ok);color:#fff}
.copy.ok .ic{fill:#fff}
.ghost{border:1px solid var(--line2);background:transparent;color:var(--text)}
.ghost .ic{fill:var(--text)}
.ghost[aria-expanded="true"]{border-color:var(--yellow);color:var(--yellow)}
.ghost[aria-expanded="true"] .ic{fill:var(--yellow)}
.kk{margin-top:12px;padding:18px 16px 14px;border-radius:14px;background:var(--raise);border:1px solid var(--line);
  text-align:center}
.kk .qr{display:inline-block;padding:12px;border-radius:12px;background:var(--white)}
.kk img{display:block;width:min(220px,58vw);height:auto;image-rendering:pixelated}
.kk p{margin:12px 4px 8px;font-size:14px;color:var(--muted)}
.kk p b{color:var(--text)}
.kk a{color:var(--yellow);font-weight:800;text-underline-offset:3px}
/* ---- altbilgi ---- */
footer{margin-top:44px}
footer .row{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-top:18px;color:var(--dim);font-size:13px}
footer b{display:flex;align-items:flex-end;font:800 18px/1 var(--ui);letter-spacing:-.02em;color:var(--text)}
footer b i{width:.22em;height:.22em;margin-left:.08em;background:var(--yellow)}
/* ---- alttaki arama şeridi, bildirim ---- */
.callbar{position:fixed;z-index:20;left:0;right:0;bottom:0;display:flex;justify-content:center;
  padding:12px max(16px,env(safe-area-inset-right,0px)) calc(12px + env(safe-area-inset-bottom,0px)) max(16px,env(safe-area-inset-left,0px));
  background:rgba(11,11,12,.86);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);border-top:1px solid var(--line);
  transform:translateY(110%);transition:transform .35s cubic-bezier(.2,.8,.2,1)}
.callbar.show{transform:none}
.callbar a{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;max-width:440px;min-height:52px;
  border-radius:14px;background:var(--yellow);color:var(--yellow-ink);text-decoration:none;font:800 16px/1 var(--ui)}
.callbar .ic{width:20px;height:20px;fill:var(--yellow-ink)}
.callbar span{font-variant-numeric:tabular-nums}
.toast{position:fixed;z-index:30;left:50%;bottom:calc(92px + env(safe-area-inset-bottom));transform:translate(-50%,40px);
  width:max-content;max-width:calc(100vw - 32px);text-align:center;background:var(--raise);color:var(--text);
  border:1px solid var(--line2);border-left:4px solid var(--yellow);padding:12px 18px;border-radius:12px;font-weight:600;
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
@keyframes pulse{0%,78%,100%{box-shadow:0 18px 40px -22px rgba(255,200,20,.7),0 0 0 0 rgba(255,200,20,.45)}
  90%{box-shadow:0 18px 40px -22px rgba(255,200,20,.7),0 0 0 10px rgba(255,200,20,0)}}
@keyframes ring{0%,84%,100%{transform:none}86%,90%,94%{transform:rotate(-14deg)}88%,92%,96%{transform:rotate(14deg)}}
@keyframes bar{from{transform:scaleY(0)}to{transform:none}}
@keyframes flash{0%{color:var(--yellow)}100%{color:var(--text)}}
@keyframes open{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}
.stripe.top{animation:stripes 1.6s cubic-bezier(.1,.6,.2,1) both}
.hero::before{animation:glow 1.8s .1s cubic-bezier(.2,.7,.2,1) both}
.mark .ch span{animation:up .9s cubic-bezier(.2,.8,.15,1) both}
.mark .ch:nth-child(1) span{animation-delay:.25s}.mark .ch:nth-child(2) span{animation-delay:.31s}
.mark .ch:nth-child(3) span{animation-delay:.37s}.mark .ch:nth-child(4) span{animation-delay:.43s}
.mark .ch:nth-child(5) span{animation-delay:.49s}
.mark .dot{animation:dot .5s 1s cubic-bezier(.3,1.4,.5,1) both}
.kind{animation:track 1s .7s cubic-bezier(.2,.8,.2,1) both}
.kind::after{transform-origin:left;animation:line .9s 1s cubic-bezier(.2,.8,.2,1) both}
.lead{animation:fade .7s 1.05s both}
.call{animation:rise .6s 1.15s cubic-bezier(.2,.8,.2,1) both,pulse 5s 2.6s infinite}
.call .ib .ic{animation:ring 5s 2.6s infinite}
.tile{animation:rise .55s cubic-bezier(.2,.8,.2,1) both}
.tile:nth-child(1){animation-delay:1.25s}.tile:nth-child(2){animation-delay:1.32s}
.tile:nth-child(3){animation-delay:1.39s}.tile:nth-child(4){animation-delay:1.46s}
.pay.in .ibanbox::before{animation:bar .7s .1s cubic-bezier(.2,.8,.2,1) both}
.pay.in .iban{animation:flash 1.4s .3s ease-out}
.iban.flash{animation:flash .9s ease-out}
.kk:not([hidden]){animation:open .35s cubic-bezier(.2,.8,.2,1)}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
"""

JS = S.JS + """
(()=>{const R=document.documentElement,still=matchMedia('(prefers-reduced-motion: reduce)').matches;
if(document.hidden){const as=document.getAnimations();as.forEach(a=>a.pause());
  addEventListener('visibilitychange',()=>{if(!document.hidden)as.forEach(a=>a.play())},{once:true})}
if(!still){let q=0;addEventListener('scroll',()=>{if(!q)q=requestAnimationFrame(()=>{
  R.style.setProperty('--roll',(scrollY*.6).toFixed(1)+'px');q=0})},{passive:true})}
if('IntersectionObserver' in window){
  const p=document.querySelector('.pay');
  const io=new IntersectionObserver(([e])=>{if(e.isIntersecting){p.classList.add('in');io.disconnect()}},{threshold:.4});
  io.observe(p);
  const bar=document.querySelector('.callbar'),call=document.querySelector('.call');
  new IntersectionObserver(([e])=>bar.classList.toggle('show',!e.isIntersecting&&e.boundingClientRect.top<0)).observe(call)}
const kb=document.getElementById('kk-btn'),kk=document.getElementById('kk');
kb.addEventListener('click',()=>{const o=kk.hidden;kk.hidden=!o;kb.setAttribute('aria-expanded',o);
  if(o)kk.scrollIntoView({behavior:still?'auto':'smooth',block:'nearest'})})})();
"""

ARROW = "M7 17L17 7M9 7h8v8"


def page(info, standalone=False, artifact=False):
    """Site (`calik_isimlik/site`), tek dosya önizleme (standalone: yazı tipleri ve karekod gömülü) ya da Claude
    önizleme sayfası (artifact: belge iskeleti yayında eklenir; indirme bağlantısı yok; ara düğmeleri numarayı da
    kopyalar)."""
    standalone = standalone or artifact
    e = html.escape
    wa = Q.whatsapp_link(info)
    insta = f"https://www.instagram.com/{info.instagram}/"
    title = "Çalık Oto Lastik"
    desc = "Çalık Oto Lastik: hemen arayın, WhatsApp'tan yazın, Instagram, Google yorumları ve ödeme bilgileri."
    css, kk = (embed_fonts(CSS), data_uri("karekod.png", "image/png")) if standalone else (CSS, "karekod.png")
    tel = f' data-tel="{e(info.phone)}"' if artifact else ""
    go = f'<svg class="go" viewBox="0 0 24 24" aria-hidden="true"><path d="{ARROW}"/></svg>'
    # aynı sekmede açılır: yeni sekme QR okuyucuların iç tarayıcılarında çoğu zaman açılmaz
    tile = lambda href, icon, t, s, extra="": (  # noqa: E731
        f'<a class="tile" href="{e(href)}"{extra}><span class="ib">{icon}</span>{go}'
        f'<span><b>{e(t)}</b><small>{e(s)}</small></span></a>')
    save_tile = "" if artifact else tile("calik.vcf", S.svg(S.ICON["person"]), "Rehbere kaydet", "Numarayı ekleyin",
                                         ' download="Çalık Oto Lastik.vcf"')
    save = "Karekoda basılı tutup kaydedin," if artifact else "Karekodu kaydedin,"
    save_link = "" if artifact else f'\n      <a href="{kk}" download="calik-karekod.png">Karekodu kaydet</a>'
    og = (f'<meta property="og:url" content="{e(info.page)}">\n<meta property="og:image" content="{e(info.page)}og.png">'
          if info.page else "")
    favicon = ("data:image/svg+xml," + "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>"
               "<rect width='64' height='64' rx='14' fill='%230b0b0c'/><rect x='38' y='38' width='12' height='12' "
               "fill='%23ffc814'/><path d='M14 32a16 16 0 0 1 27-11.6' stroke='%23f4f4f1' stroke-width='8' "
               "fill='none'/><path d='M41 43.6A16 16 0 0 1 14 32' stroke='%23f4f4f1' stroke-width='8' fill='none'/></svg>")
    body = f"""<div class="stripe top" aria-hidden="true"></div>
<div class="wrap">
<header class="hero">
  <h1 class="mark" aria-label="Çalık">{wordmark()}</h1>
  <p class="kind">OTO LASTİK</p>
  <p class="lead">Lastikle ilgili her konuda bize tek dokunuşla ulaşın.</p>
</header>
<main>
<a class="call" href="tel:+{info.tel}"{tel}><span class="t"><small>HEMEN ARA</small><b>{e(info.phone)}</b></span>
  <span class="ib">{S.svg(S.ICON["phone"])}</span></a>
<nav class="grid" aria-label="Bağlantılar">
  {tile(wa, S.svg(S.logo_path("whatsapp")), "WhatsApp", "Mesaj gönderin")}
  {tile(insta, S.svg(S.logo_path("instagram")), "Instagram", "@" + info.instagram)}
  {tile(info.google, S.svg(S.ICON["star"]), "Google", "Yorum yapın")}
  {save_tile}
</nav>
<h2 class="sec">ÖDEME BİLGİLERİ</h2>
<section class="pay" aria-label="Ödeme bilgileri">
  <dl class="rows"><dt>Banka</dt><dd>{e(info.bank)}</dd><dt>Alıcı</dt><dd>{e(info.holder)}</dd></dl>
  <div class="ibanbox"><span>IBAN</span><output class="iban">{e(Q.iban_display(info.iban))}</output></div>
  <div class="acts">
    <button class="btn copy" type="button" data-copy="{e(info.iban)}">{S.svg(S.ICON["copy"])}<span>Kopyala</span></button>
    <button class="btn ghost" type="button" id="kk-btn" aria-expanded="false" aria-controls="kk">{S.svg(S.ICON["qr"])}Karekod</button>
  </div>
  <div class="kk" id="kk" hidden>
    <span class="qr"><img src="{kk}" width="828" height="828" alt="{e(info.bank)} karekodu – {e(info.holder)}"></span>
    <p>{save} banka uygulamanızda <b>Karekod ile Öde</b>, ardından <b>Galeriden seç</b>.</p>{save_link}
  </div>
</section>
</main>
<footer>
  <div class="stripe" aria-hidden="true"></div>
  <div class="row"><b>ÇALIK<i></i></b><span>@{e(info.instagram)}</span></div>
</footer>
</div>
<div class="callbar"><a href="tel:+{info.tel}"{tel} aria-label="Hemen ara">{S.svg(S.ICON["phone"])}Hemen ara · <span>{e(info.phone)}</span></a></div>
<div class="toast" role="status" aria-live="polite"></div>
<script>{JS}</script>
"""
    if artifact:
        return f"""<title>Çalık Oto Lastik</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>{css}</style>
{body}"""
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#0b0b0c">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
{og}
<link rel="icon" href="{favicon}">
<style>{css}</style>
</head>
<body>
{body}</body>
</html>
"""


# ---------------------------------------------------------------- görseller

def og_image():
    """Bağlantı paylaşılınca görünen kapak (1200 × 630): başlığın aynısı, büyük."""
    from playwright.sync_api import sync_playwright
    doc = f"""<!doctype html><meta charset="utf-8"><style>{embed_fonts(CSS)}
body{{margin:0}} .wrap{{max-width:none;padding:0 100px}} .hero{{padding-block:110px 0}} .stripe{{height:14px}}
.mark{{font-size:250px;margin-top:0}} .kind{{font-size:34px;margin-top:34px}}</style>
<div class="stripe"></div><div class="wrap"><header class="hero"><h1 class="mark">{wordmark()}</h1>
<p class="kind">OTO LASTİK</p></header></div>"""
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        pg = b.new_page(viewport={"width": 1200, "height": 630}, reduced_motion="reduce")
        pg.set_content(doc)
        pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(OUT, "og.png"))
        b.close()


def screenshot(path=PREVIEW):
    """Telefon ekranında (390 px): üst görünüm ve tüm sayfa (karekod açık) yan yana."""
    from playwright.sync_api import sync_playwright
    top, full = path.replace(".png", "_ust.png"), path.replace(".png", "_tam.png")
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, reduced_motion="reduce")
        pg.goto("file://" + os.path.join(OUT, "index.html"))
        pg.wait_for_timeout(400)
        assert pg.evaluate("document.fonts.check('800 20px \"Manrope\"')"), "yazı tipi yüklenmedi"
        assert pg.evaluate("document.documentElement.scrollWidth") <= 390, "yatay taşma"
        assert pg.evaluate("[...document.querySelectorAll('.iban,.call b,.tile b,.tile small,.rows dd')]"
                           ".every(e=>e.scrollWidth<=e.clientWidth+1)"), "yazı sığmadı"
        pg.screenshot(path=top)
        pg.click("#kk-btn")
        pg.wait_for_timeout(200)
        pg.screenshot(path=full, full_page=True)
        b.close()
    shots = [Image.open(top), Image.open(full)]
    h = max(s.height for s in shots)
    canvas = Image.new("RGB", (sum(s.width for s in shots) + 120, h + 120), (52, 52, 58))
    x = 40
    for s in shots:
        canvas.paste(s, (x, 60))
        x += s.width + 40
    canvas.save(path)
    for f in (top, full):
        os.remove(f)
    return path


def tour_gif(path=TOUR):
    """Tam tur (390 × 844): açılış, aşağı kaydırma, IBAN'ı kopyala, karekod; dokunulan yer halkayla gösterilir."""
    from playwright.sync_api import sync_playwright
    frames, durs = [], []

    def shot(pg, ms=100, tap=None):
        im = Image.open(io.BytesIO(pg.screenshot())).convert("RGB")
        if tap:
            d = ImageDraw.Draw(im, "RGBA")
            d.ellipse((tap[0] - 22, tap[1] - 22, tap[0] + 22, tap[1] + 22), fill=(255, 255, 255, 70),
                      outline=(13, 13, 13, 230), width=3)
        frames.append(im)
        durs.append(ms)

    def tap_on(pg, sel):
        box = pg.locator(sel).bounding_box()
        return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2

    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=1,
                            permissions=["clipboard-read", "clipboard-write"])
        pg = ctx.new_page()
        pg.goto("file://" + os.path.join(OUT, "index.html"))
        _seek(pg, 0)
        pg.wait_for_timeout(300)
        for k in range(0, 2300, 80):                         # açılış: animasyonlar zamanda adım adım
            _seek(pg, k)
            shot(pg, 80)
        _finish(pg)
        shot(pg, 900)
        h = pg.evaluate("document.documentElement.scrollHeight - innerHeight")
        for y in range(0, h + 1, 38):
            pg.evaluate(f"scrollTo(0,{y})")
            pg.wait_for_timeout(40)
            shot(pg, 60)
        pg.evaluate(f"scrollTo(0,{h})")
        for _ in range(8):
            pg.wait_for_timeout(100)
            shot(pg, 100)
        tap = tap_on(pg, ".copy")
        shot(pg, 300, tap)
        pg.mouse.click(*tap)
        for _ in range(5):
            pg.wait_for_timeout(120)
            shot(pg, 160)
        durs[-1] = 1000
        pg.wait_for_timeout(2300)
        tap = tap_on(pg, "#kk-btn")
        shot(pg, 300, tap)
        pg.mouse.click(*tap)
        for _ in range(8):
            pg.wait_for_timeout(90)
            shot(pg, 90)
        h2 = pg.evaluate("document.documentElement.scrollHeight - innerHeight")
        pg.evaluate(f"scrollTo(0,{h2})")
        pg.wait_for_timeout(300)
        shot(pg, 2400)
        b.close()
    return _gif(frames, durs, path)


def pack():
    """Yüklemeye hazır zip: index.html en üstte."""
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for d, _, files in os.walk(OUT):
            for fn in sorted(files):
                full = os.path.join(d, fn)
                z.write(full, os.path.relpath(full, OUT))


def main():
    info = Q.load(DATA)
    os.makedirs(OUT, exist_ok=True)
    subset_fonts()
    karekod_png(info)
    vcard(info)
    og_image()
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(page(info))
    with open(ARTIFACT, "w", encoding="utf-8") as f:
        f.write(page(info, artifact=True))
    with open(STANDALONE, "w", encoding="utf-8") as f:
        f.write(page(info, standalone=True))
    pack()
    print("sayfa:", os.path.relpath(os.path.join(OUT, "index.html"), A.ROOT), "→", info.page or "(adres yayından sonra)")
    print("önizleme:", *(os.path.relpath(f(), A.ROOT) for f in (screenshot, tour_gif)))


if __name__ == "__main__":
    main()
