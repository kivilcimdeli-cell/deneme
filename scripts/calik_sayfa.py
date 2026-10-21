"""ÇALIK OTO LASTİK – işletme sayfası (sarı, siyah, beyaz; telefona göre).

Uzar ve İnce'nin sayfalarıyla aynı işler, ayrı tasarım: tabela. Sarı başlıkta havalimanı panosu gibi harf harf
dönen ÇALIK (siyah kapaklar, beyaz harfler), altında ikaz şeridi. İletişim beyaz zeminde kalın siyah çerçeveli,
gölgeli düğmeler (basınca içeri göçer); ödeme siyah zeminde sarı bilet: IBAN, alıcı, banka.

Animasyon:
  açılış   pano kapakları rastgele harflerden geçip ÇALIK'ta durur, OTO LASTİK soldan açılır, düğmeler sırayla gelir
  kaydırma ikaz şeritleri kaydırdıkça akar; bilet göründüğünde yazar makineden çıkar gibi açılır; Hemen Ara ekrandan
           çıkınca altta sarı arama şeridi belirir
  sürekli  birkaç saniyede bir panoda tek bir kapak dönüp geri gelir, Hemen Ara'daki telefon çalar; panoya dokununca
           harfler yeniden karışır
"Hareketi azalt" açıksa hiçbiri oynamaz; JavaScript olmasa da sayfa tam görünür.

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
from ince_sayfa import _finish, _gif  # noqa: E402

BASE = os.path.join(A.ROOT, "calik_isimlik")
DATA = os.path.join(BASE, "bilgiler.json")
OUT = os.path.join(BASE, "site")
ZIP = os.path.join(BASE, "calik_site.zip")
PREVIEW = os.path.join(BASE, "sayfa_onizleme.png")
TOUR = os.path.join(BASE, "sayfa_tur.gif")
STANDALONE = os.path.join(BASE, "sayfa_onizleme.html")
ARTIFACT = os.path.join(BASE, "sayfa_artifact.html")
# Oswald ve Manrope (OFL): değişken yazı tiplerinden sabit kesimler, latin + latin-ext birleşik
FONTS = {"display": "Oswald-Bold.ttf", "display-sb": "Oswald-SemiBold.ttf", "text": "Manrope-SemiBold.ttf",
         "text-xb": "Manrope-ExtraBold.ttf"}
LICENSES = ("OFL-oswald.txt", "OFL-manrope.txt")
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


def board(text=NAME):
    """Pano: her harf bir kapak (üst ve alt yarım). JavaScript yoksa harfler olduğu gibi görünür."""
    return "".join(f'<span class="flap" data-ch="{c}"><span class="half top"><b>{c}</b></span>'
                   f'<span class="half bot"><b>{c}</b></span></span>' for c in text)


# ---------------------------------------------------------------- sayfa

CSS = """
@font-face{font-family:"Oswald";font-weight:700;font-display:swap;src:url(fonts/display.woff) format("woff")}
@font-face{font-family:"Oswald";font-weight:600;font-display:swap;src:url(fonts/display-sb.woff) format("woff")}
@font-face{font-family:"Manrope";font-weight:600;font-display:swap;src:url(fonts/text.woff) format("woff")}
@font-face{font-family:"Manrope";font-weight:800;font-display:swap;src:url(fonts/text-xb.woff) format("woff")}
/* tabela: sarı başlık (dönen harf panosu), beyaz iletişim (kalın çerçeveli düğmeler), siyah ödeme (sarı bilet) */
:root{color-scheme:light;--yellow:#ffc814;--yellow2:#f0b400;--ink:#0d0d0d;--ink2:#1a1a1a;--paper:#ffffff;
  --cream:#fff7d6;--muted:#5d5a52;--onink:#b9b6ad;--line:#2a2a2a;--ok:#1f9d55;
  --display:"Oswald","Arial Narrow",sans-serif;--ui:"Manrope",system-ui,-apple-system,"Segoe UI",sans-serif;
  --stripe:repeating-linear-gradient(-45deg,var(--ink) 0 13px,var(--yellow) 13px 26px);--roll:0px}
*{box-sizing:border-box;margin:0}
html{background:var(--ink);-webkit-text-size-adjust:100%}
body{background:var(--ink);color:var(--ink);font:600 16px/1.45 var(--ui);min-height:100vh;overflow-x:hidden}
a{color:inherit;-webkit-tap-highlight-color:transparent}
button{font:inherit;color:inherit}
:focus-visible{outline:3px solid var(--ink);outline-offset:3px}
.band{padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.in{max-width:460px;margin:0 auto}
/* ---- başlık: sarı tabela ---- */
.hero{background:var(--yellow);padding-block:34px 30px;position:relative;overflow:hidden}
.hero::before{content:"";position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(120% 70% at 0% 0%,rgba(255,255,255,.35),transparent 60%)}
.hero .in{position:relative}
.top{display:flex;justify-content:space-between;align-items:center;font:600 13px/1 var(--display);letter-spacing:.24em}
.top span:last-child{display:inline-flex;align-items:center;gap:7px}
.top span:last-child::before{content:"";width:9px;height:9px;background:var(--ink);transform:rotate(45deg)}
.board{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:7px;margin-top:20px;cursor:pointer;
  -webkit-tap-highlight-color:transparent}
.flap{position:relative;height:clamp(92px,29vw,128px);border-radius:9px;perspective:420px;
  box-shadow:0 7px 0 rgba(0,0,0,.28),0 14px 24px -12px rgba(0,0,0,.5)}
.half{position:absolute;left:0;right:0;height:50%;overflow:hidden;backface-visibility:hidden;-webkit-backface-visibility:hidden}
.half.top{top:0;border-radius:9px 9px 0 0;background:linear-gradient(#232323,#191919)}
.half.bot{bottom:0;border-radius:0 0 9px 9px;background:linear-gradient(#141414,#0f0f0f)}
.half b{position:absolute;left:0;right:0;height:200%;display:flex;align-items:center;justify-content:center;
  font:700 clamp(66px,21vw,92px)/1 var(--display);color:#fbfbf7}
.half.top b{top:0}
.half.bot b{bottom:0}
.flap::after{content:"";position:absolute;left:0;right:0;top:50%;height:2px;margin-top:-1px;background:#000;z-index:4;
  box-shadow:0 1px 0 rgba(255,255,255,.06)}
.flap::before{content:"";position:absolute;z-index:5;top:calc(50% - 5px);left:-2px;right:-2px;height:10px;
  background:linear-gradient(90deg,var(--yellow2) 0 4px,transparent 4px calc(100% - 4px),var(--yellow2) calc(100% - 4px))}
.leaf{z-index:3}
.leaf.top{transform-origin:50% 100%}
.leaf.bot{transform-origin:50% 0}
.sub{display:flex;align-items:center;gap:12px;margin-top:22px}
.sub b{font:700 clamp(34px,11.5vw,50px)/1 var(--display);letter-spacing:.015em}
.sub::after{content:"";flex:1;height:6px;background:var(--ink)}
.stripe{height:18px;background:var(--stripe);background-position:calc(var(--roll) * -1) 0;border-block:3px solid var(--ink)}
/* ---- iletişim: beyaz, kalın çerçeve ---- */
.contact{background:var(--paper);padding-block:30px 34px}
.label{font:600 14px/1 var(--display);letter-spacing:.24em;margin-bottom:14px;display:flex;align-items:center;gap:10px}
.label::before{content:"";width:14px;height:14px;background:var(--yellow);border:3px solid var(--ink)}
.box{border:3px solid var(--ink);border-radius:12px;box-shadow:6px 6px 0 var(--ink);
  transition:transform .12s cubic-bezier(.3,.7,.3,1),box-shadow .12s cubic-bezier(.3,.7,.3,1)}
.box:active{transform:translate(5px,5px);box-shadow:1px 1px 0 var(--ink)}
.call{display:flex;align-items:center;gap:14px;padding:18px 16px 18px 20px;text-decoration:none;background:var(--yellow)}
.call .t{flex:1;min-width:0}
.call small{display:block;font:600 14px/1 var(--display);letter-spacing:.2em}
.call b{display:block;margin-top:7px;font:700 clamp(30px,9.2vw,40px)/1 var(--display);letter-spacing:.01em;
  font-variant-numeric:tabular-nums;white-space:nowrap}
.call .ib{flex:none;display:grid;place-items:center;width:54px;height:54px;border-radius:50%;background:var(--ink)}
.call .ib .ic{width:25px;height:25px;fill:var(--yellow)}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:18px}
.tile{position:relative;display:flex;flex-direction:column;gap:22px;min-height:118px;padding:14px 14px 13px;
  text-decoration:none;background:var(--paper);overflow:hidden}
.tile::after{content:"";position:absolute;top:0;right:0;width:26px;height:26px;background:var(--yellow);
  border-left:3px solid var(--ink);border-bottom:3px solid var(--ink);border-bottom-left-radius:8px}
.tile .ib{display:grid;place-items:center;width:42px;height:42px;border-radius:9px;background:var(--ink)}
.tile .ic{width:22px;height:22px;fill:var(--yellow)}
.tile b{display:block;font:600 20px/1 var(--display);letter-spacing:.03em;text-transform:uppercase}
.tile small{display:block;margin-top:5px;font-size:12.5px;line-height:1.2;color:var(--muted);overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
.tile.save{background:var(--cream)}
/* ---- ödeme: siyah zemin, sarı bilet ---- */
.pay{background:var(--ink);color:var(--paper);padding-block:34px 36px}
.pay .label{color:var(--paper)}
.pay .label::before{border-color:var(--yellow)}
.ticket{position:relative;padding:22px 22px 20px;border-radius:14px;background:var(--yellow);color:var(--ink);
  container-type:inline-size;
  -webkit-mask:radial-gradient(circle 13px at 0 66%,transparent 12px,#000 13px) left/51% 100% no-repeat,
               radial-gradient(circle 13px at 100% 66%,transparent 12px,#000 13px) right/51% 100% no-repeat;
          mask:radial-gradient(circle 13px at 0 66%,transparent 12px,#000 13px) left/51% 100% no-repeat,
               radial-gradient(circle 13px at 100% 66%,transparent 12px,#000 13px) right/51% 100% no-repeat}
.ticket .head{display:flex;justify-content:space-between;align-items:baseline}
.ticket .head b{font:700 22px/1 var(--display);letter-spacing:.04em}
.ticket .head span{font:600 14px/1 var(--display);letter-spacing:.16em}
.iban-l{margin-top:20px;font:600 11px/1 var(--display);letter-spacing:.3em;opacity:.7}
.iban{margin-top:8px;font:800 18px/1.15 var(--ui);font-size:min(21px,5.2cqi);letter-spacing:.015em;word-spacing:.06em;
  font-variant-numeric:tabular-nums;white-space:nowrap;user-select:all;-webkit-user-select:all}
.perf{margin:18px -22px 14px;border-top:3px dashed rgba(13,13,13,.55)}
.who{display:flex;justify-content:space-between;align-items:baseline;gap:10px}
.who small{font:600 11px/1 var(--display);letter-spacing:.3em;opacity:.7}
.who b{font:700 22px/1 var(--display);letter-spacing:.05em}
.acts{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px}
.btn{display:flex;align-items:center;justify-content:center;gap:9px;min-height:56px;border-radius:12px;cursor:pointer;
  font:600 17px/1 var(--display);letter-spacing:.1em;text-transform:uppercase;text-decoration:none;
  transition:transform .12s,box-shadow .12s,background .2s}
.btn .ic{width:20px;height:20px}
.copy{border:3px solid var(--paper);background:var(--paper);color:var(--ink);box-shadow:5px 5px 0 var(--yellow)}
.copy .ic{fill:var(--ink)}
.copy:active,.ghost:active{transform:translate(4px,4px);box-shadow:1px 1px 0 var(--yellow)}
.copy.ok{background:var(--ok);border-color:var(--ok);color:#fff}
.copy.ok .ic{fill:#fff}
.ghost{border:3px solid var(--yellow);background:transparent;color:var(--yellow);box-shadow:5px 5px 0 var(--yellow2)}
.ghost .ic{fill:var(--yellow)}
.ghost[aria-expanded="true"]{background:var(--yellow);color:var(--ink)}
.ghost[aria-expanded="true"] .ic{fill:var(--ink)}
.kk{margin-top:18px;padding:18px 16px 16px;border-radius:14px;background:var(--paper);color:var(--ink);text-align:center}
.kk img{display:block;width:min(240px,64vw);height:auto;margin:0 auto;image-rendering:pixelated}
.kk p{margin:12px 4px 8px;font-size:14px;color:var(--muted)}
.kk p b{color:var(--ink)}
.kk a{font-weight:800;text-underline-offset:3px}
/* ---- altbilgi ---- */
footer{background:var(--ink);color:var(--onink);padding-block:0 calc(96px + env(safe-area-inset-bottom))}
footer .row{display:flex;justify-content:space-between;align-items:baseline;gap:10px;padding-top:18px;font-size:13px}
footer b{font:700 18px/1 var(--display);letter-spacing:.06em;color:var(--paper)}
footer b span{color:var(--yellow)}
/* ---- alttaki arama şeridi, bildirim ---- */
.callbar{position:fixed;z-index:20;left:0;right:0;bottom:0;display:flex;align-items:center;justify-content:center;gap:12px;
  padding:14px max(16px,env(safe-area-inset-right,0px)) calc(14px + env(safe-area-inset-bottom,0px)) max(16px,env(safe-area-inset-left,0px));
  background:var(--yellow);border-top:3px solid var(--ink);text-decoration:none;font:700 21px/1 var(--display);letter-spacing:.04em;
  transform:translateY(110%);transition:transform .35s cubic-bezier(.2,.8,.2,1)}
.callbar.show{transform:none}
.callbar .ic{width:22px;height:22px;fill:var(--ink)}
.callbar span{font-variant-numeric:tabular-nums}
.toast{position:fixed;z-index:30;left:50%;bottom:calc(92px + env(safe-area-inset-bottom));transform:translate(-50%,40px);
  width:max-content;max-width:calc(100vw - 32px);text-align:center;background:var(--paper);color:var(--ink);
  border:3px solid var(--ink);box-shadow:5px 5px 0 var(--yellow);padding:12px 16px;border-radius:12px;font-weight:800;
  transition:transform .25s,opacity .25s;opacity:0;pointer-events:none}
.toast.show{transform:translate(-50%,0);opacity:1}
/* ---- animasyonlar ---- */
@keyframes wipe{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
@keyframes grow{from{transform:scaleX(0)}to{transform:none}}
@keyframes rise{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:none}}
@keyframes pop{0%{opacity:0;transform:translateY(16px) rotate(-2deg) scale(.96)}100%{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes stripes{from{background-position:-160px 0}to{background-position:0 0}}
@keyframes ring{0%,84%,100%{transform:none}86%,90%,94%{transform:rotate(-15deg)}88%,92%,96%{transform:rotate(15deg)}}
@keyframes print{from{clip-path:inset(0 0 100% 0);transform:translateY(-14px)}to{clip-path:inset(0 0 0 0);transform:none}}
@keyframes flash{0%{background:var(--ink);color:var(--yellow)}100%{background:transparent;color:inherit}}
@keyframes open{from{opacity:0;transform:translateY(-8px) scale(.98)}to{opacity:1;transform:none}}
.top{animation:fade .5s .1s both}
.sub b{animation:wipe .65s .95s cubic-bezier(.6,0,.2,1) both}
.sub::after{transform-origin:left;animation:grow .7s 1.1s cubic-bezier(.2,.8,.2,1) both}
.hero+.stripe{animation:stripes 1.4s .2s cubic-bezier(.1,.6,.2,1) both}
.contact .label{animation:rise .5s 1.1s both}
.call{animation:rise .6s 1.18s cubic-bezier(.2,.8,.2,1) both}
.call .ib .ic{animation:ring 6s 2.4s infinite}
.tile{animation:pop .55s cubic-bezier(.2,1.2,.4,1) both}
.tile:nth-child(1){animation-delay:1.3s}.tile:nth-child(2){animation-delay:1.38s}
.tile:nth-child(3){animation-delay:1.46s}.tile:nth-child(4){animation-delay:1.54s}
.ticket.go{animation:print .8s cubic-bezier(.3,.7,.2,1)}
.iban.flash{animation:flash .9s ease-out;border-radius:4px}
.kk:not([hidden]){animation:open .35s cubic-bezier(.2,.8,.2,1)}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
"""

JS = S.JS + """
(()=>{const R=document.documentElement,still=matchMedia('(prefers-reduced-motion: reduce)').matches;
/* pano: kapak üst yarısı düşer, yeni harfin alt yarısı iner */
const SET='ABCDEFGHIJKLMNOPRSTUVYZÇĞİÖŞÜ0123456789';
const rnd=()=>SET[Math.floor(Math.random()*SET.length)];
function flip(el,ch,ms){const old=el.dataset.cur||el.dataset.ch;if(old===ch)return Promise.resolve();
  const tb=el.querySelector('.half.top:not(.leaf) b'),bb=el.querySelector('.half.bot:not(.leaf) b');
  tb.textContent=ch;
  const lt=document.createElement('span'),lb=document.createElement('span');
  lt.className='half top leaf';lb.className='half bot leaf';lt.innerHTML='<b></b>';lb.innerHTML='<b></b>';
  lt.firstChild.textContent=old;lb.firstChild.textContent=ch;lb.style.transform='rotateX(90deg)';el.append(lt,lb);
  return lt.animate([{transform:'rotateX(0)',filter:'brightness(1)'},{transform:'rotateX(-90deg)',filter:'brightness(.55)'}],
      {duration:ms/2,easing:'ease-in',fill:'forwards'}).finished
    .then(()=>lb.animate([{transform:'rotateX(90deg)',filter:'brightness(1.5)'},{transform:'rotateX(0)',filter:'brightness(1)'}],
      {duration:ms/2,easing:'cubic-bezier(.3,1.4,.5,1)',fill:'forwards'}).finished)
    .then(()=>{bb.textContent=ch;lt.remove();lb.remove();el.dataset.cur=ch})}
async function spin(el,n,ms,wait){await new Promise(r=>setTimeout(r,wait));
  for(let k=0;k<n;k++)await flip(el,rnd(),ms);await flip(el,el.dataset.ch,ms*1.4)}
const flaps=[...document.querySelectorAll('.flap')];let busy=false;
function shuffle(start){if(still||busy)return;busy=true;
  Promise.all(flaps.map((f,i)=>spin(f,4+i*2,96,start+i*70))).then(()=>busy=false)}
const go=()=>shuffle(220);
if(document.hidden)addEventListener('visibilitychange',go,{once:true});else go();
document.querySelector('.board').addEventListener('click',()=>shuffle(0));
if(!still)setInterval(()=>{if(busy||document.hidden)return;const f=flaps[Math.floor(Math.random()*flaps.length)];
  busy=true;flip(f,rnd(),180).then(()=>flip(f,f.dataset.ch,240)).then(()=>busy=false)},7000);
if(!still){let q=0;addEventListener('scroll',()=>{if(!q)q=requestAnimationFrame(()=>{
  R.style.setProperty('--roll',(scrollY*.7).toFixed(1)+'px');q=0})},{passive:true})}
if('IntersectionObserver' in window){
  const t=document.querySelector('.ticket');
  const io=new IntersectionObserver(([e])=>{if(e.isIntersecting){t.classList.add('go');io.disconnect()}},{threshold:.2});
  io.observe(t);
  const bar=document.querySelector('.callbar'),call=document.querySelector('.call');
  new IntersectionObserver(([e])=>bar.classList.toggle('show',!e.isIntersecting&&e.boundingClientRect.top<0)).observe(call)}
const kb=document.getElementById('kk-btn'),kk=document.getElementById('kk');
kb.addEventListener('click',()=>{const o=kk.hidden;kk.hidden=!o;kb.setAttribute('aria-expanded',o);
  if(o)kk.scrollIntoView({behavior:still?'auto':'smooth',block:'nearest'})})})();
"""


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
    # aynı sekmede açılır: yeni sekme QR okuyucuların iç tarayıcılarında çoğu zaman açılmaz
    tile = lambda href, icon, t, s, cls="", extra="": (  # noqa: E731
        f'<a class="tile box{cls}" href="{e(href)}"{extra}><span class="ib">{icon}</span>'
        f'<span><b>{e(t)}</b><small>{e(s)}</small></span></a>')
    save_tile = "" if artifact else tile("calik.vcf", S.svg(S.ICON["person"]), "Rehber", "Numarayı kaydedin",
                                         " save", ' download="Çalık Oto Lastik.vcf"')
    save = "Karekoda basılı tutup kaydedin," if artifact else "Karekodu kaydedin,"
    save_link = "" if artifact else f'\n      <a href="{kk}" download="calik-karekod.png">Karekodu kaydet</a>'
    og = (f'<meta property="og:url" content="{e(info.page)}">\n<meta property="og:image" content="{e(info.page)}og.png">'
          if info.page else "")
    favicon = ("data:image/svg+xml," + "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>"
               "<rect width='64' height='64' rx='14' fill='%23ffc814'/><rect x='14' y='12' width='36' height='40' rx='6' "
               "fill='%230d0d0d'/><rect x='14' y='31' width='36' height='2' fill='%23ffc814'/></svg>")
    body = f"""<header class="hero band">
  <div class="in">
    <p class="top"><span>OTO LASTİK</span><span>{e(info.phone)}</span></p>
    <div class="board" role="img" aria-label="Çalık">{board()}</div>
    <p class="sub"><b>OTO LASTİK</b></p>
  </div>
</header>
<div class="stripe" aria-hidden="true"></div>
<main>
<section class="contact band" aria-label="İletişim">
  <div class="in">
    <p class="label">BİZE ULAŞIN</p>
    <a class="call box" href="tel:+{info.tel}"{tel}><span class="t"><small>HEMEN ARA</small><b>{e(info.phone)}</b></span>
      <span class="ib">{S.svg(S.ICON["phone"])}</span></a>
    <nav class="grid" aria-label="Bağlantılar">
      {tile(wa, S.svg(S.logo_path("whatsapp")), "WhatsApp", "Mesaj gönderin")}
      {tile(insta, S.svg(S.logo_path("instagram")), "Instagram", "@" + info.instagram)}
      {tile(info.google, S.svg(S.ICON["star"]), "Google", "Yorum yapın")}
      {save_tile}
    </nav>
  </div>
</section>
<section class="pay band" aria-labelledby="odeme">
  <div class="in">
    <p class="label" id="odeme">ÖDEME</p>
    <div class="ticket">
      <div class="head"><b>ÖDEME BİLGİLERİ</b><span>{e(info.bank.upper())}</span></div>
      <p class="iban-l">IBAN</p>
      <div class="iban">{e(Q.iban_display(info.iban))}</div>
      <div class="perf"></div>
      <div class="who"><small>ALICI</small><b>{e(info.holder)}</b></div>
    </div>
    <div class="acts">
      <button class="btn copy" type="button" data-copy="{e(info.iban)}">{S.svg(S.ICON["copy"])}<span>Kopyala</span></button>
      <button class="btn ghost" type="button" id="kk-btn" aria-expanded="false" aria-controls="kk">{S.svg(S.ICON["qr"])}Karekod</button>
    </div>
    <div class="kk" id="kk" hidden>
      <img src="{kk}" width="828" height="828" alt="{e(info.bank)} karekodu – {e(info.holder)}">
      <p>{save} banka uygulamanızda <b>Karekod ile Öde</b>, ardından <b>Galeriden seç</b>.</p>{save_link}
    </div>
  </div>
</section>
</main>
<footer class="band">
  <div class="stripe" aria-hidden="true" style="margin-inline:calc(max(16px,env(safe-area-inset-left,0px)) * -1)"></div>
  <div class="in row"><b>ÇALIK <span>OTO LASTİK</span></b><span>@{e(info.instagram)}</span></div>
</footer>
<a class="callbar" href="tel:+{info.tel}"{tel} aria-label="Hemen ara">{S.svg(S.ICON["phone"])}HEMEN ARA · <span>{e(info.phone)}</span></a>
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
<meta name="theme-color" content="#ffc814">
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
    """Bağlantı paylaşılınca görünen kapak (1200 × 630): sarı tabela, pano."""
    from playwright.sync_api import sync_playwright
    doc = f"""<!doctype html><meta charset="utf-8"><style>{embed_fonts(CSS)}
body{{margin:0;background:#ffc814}} .hero{{width:1200px;height:600px;padding:70px 120px 0}} .in{{max-width:none}}
.top{{font-size:26px}} .board{{gap:18px;margin-top:40px}} .flap{{height:300px}} .half b{{font-size:230px}}
.sub{{margin-top:44px}} .sub b{{font-size:84px}} .sub::after{{height:12px}} .stripe{{height:30px}}</style>
<header class="hero"><div class="in"><p class="top"><span>OTO LASTİK</span><span></span></p>
<div class="board">{board()}</div><p class="sub"><b>OTO LASTİK</b></p></div></header><div class="stripe"></div>"""
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
        assert pg.evaluate("document.fonts.check('700 20px \"Oswald\"')"), "yazı tipi yüklenmedi"
        assert pg.evaluate("document.documentElement.scrollWidth") <= 390, "yatay taşma"
        assert pg.evaluate("[...document.querySelectorAll('.iban,.call b,.tile b,.tile small,.who b')]"
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
    """Tam tur (390 × 844, gerçek zamanlı): pano dönüşü, aşağı kaydırma, bilet, IBAN'ı kopyala, karekod."""
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
        for _ in range(34):                                  # açılış (gerçek zaman, ~2,6 sn)
            pg.wait_for_timeout(30)
            shot(pg, 75)
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
