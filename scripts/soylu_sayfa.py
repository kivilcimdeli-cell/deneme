"""SOYLU OTO LASTİK – işletme sayfası (siyah, beyaz, kırmızı; kurumsal; telefona göre).

Uzar, İnce ve Çalık'ın sayfalarıyla aynı işler, ayrı tasarım: kurumsal ve düzenli. Siyah zemin, tek yazı tipi
(Sora), ince çizgiler; kırmızı yalnız vurgu: sağ üstteki eğik kırmızı şerit, SOYLU'nun altındaki çizgi, Hemen Ara,
bağlantı numaraları ve ödeme kartının üst çizgisi. Bağlantılar kurumsal bir liste (01–04), kutu değil.

Animasyon:
  açılış   kırmızı eğik şerit sağdan kayarak gelir; SOYLU'yu kırmızı bir blok soldan kapatıp sağa açarak gösterir;
           kırmızı çizgi uzar, OTO LASTİK harfleri sırayla oturur; düğme ve liste satırları sırayla gelir
  kaydırma şerit kaydırdıkça hafifçe kayar; ödeme kartı görününce üst çizgisi uzar ve IBAN dörtlü gruplar hâlinde
           belirir; Hemen Ara ekrandan çıkınca altta arama şeridi belirir
  sürekli  Hemen Ara'nın üstünden birkaç saniyede bir ışık geçer, telefon simgesi çalar
"Hareketi azalt" açıksa hiçbiri oynamaz.

Sayfada: Hemen Ara, WhatsApp (hazır mesajlı), Instagram, Google yorumları, Rehbere Kaydet (vCard), ödeme bilgileri
(banka, alıcı, IBAN + tek dokunuşla kopyala; banka karekodu bilgiler.json'a yazılınca Karekod düğmesi de çıkar).
Dış bağlantı yok: yazı tipleri ve simgeler sayfanın içinde.

Bilgiler `soylu_isimlik/bilgiler.json`dan okunur (scripts/qr_sistemi.py doğrular).

Yayın: ortak Cloudflare hesabında (`qrsistem`) `soyluotolastik` adlı Worker'a `soylu_site.zip` yüklenir; adres
`https://soyluotolastik.qrsistem.workers.dev/` (isimliklerdeki QR bu adresi açar).

Çıktı : soylu_isimlik/site/, soylu_isimlik/soylu_site.zip, sayfa_onizleme.png, sayfa_tur.gif, sayfa_onizleme.html,
        sayfa_artifact.html (Claude önizlemesi)

Kullanım:
  python3 scripts/soylu_sayfa.py
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

BASE = os.path.join(A.ROOT, "soylu_isimlik")
DATA = os.path.join(BASE, "bilgiler.json")
OUT = os.path.join(BASE, "site")
ZIP = os.path.join(BASE, "soylu_site.zip")
PREVIEW = os.path.join(BASE, "sayfa_onizleme.png")
TOUR = os.path.join(BASE, "sayfa_tur.gif")
STANDALONE = os.path.join(BASE, "sayfa_onizleme.html")
ARTIFACT = os.path.join(BASE, "sayfa_artifact.html")
# Sora (OFL): değişken yazı tipinden sabit kesimler (400, 600, 800)
FONTS = {"text": "Sora-Regular.ttf", "text-sb": "Sora-SemiBold.ttf", "text-xb": "Sora-ExtraBold.ttf"}
LICENSES = ("OFL-sora.txt",)
CHROMIUM = "/opt/pw-browsers/chromium"
NAME = "SOYLU"
LEAD = "Mobil lastik tamir ve servis. Tek dokunuşla arayın, yazın."


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


def karekod_png(info, error="h"):
    """Banka karekodu (varsa): bankanınkiyle aynı baytlar (ECI yok) ve aynı hata düzeltme (İş Bankası: H)."""
    import segno
    import zxingcpp
    path = os.path.join(OUT, "karekod.png")
    if not info.karekod:
        if os.path.exists(path):
            os.remove(path)
        return None
    segno.make(info.karekod, error=error, mode="byte", encoding="utf-8", eci=False, micro=False,
               boost_error=False).save(path, scale=12, border=4)
    r = zxingcpp.read_barcodes(Image.open(path).convert("L"))
    assert len(r) == 1 and r[0].text == info.karekod and r[0].bytes == info.karekod.encode("utf-8"), "karekod"
    return path


def vcard(info):
    lines = ["BEGIN:VCARD", "VERSION:3.0", "N:;Soylu Oto Lastik;;;", "FN:Soylu Oto Lastik", "ORG:Soylu Oto Lastik",
             f"TEL;TYPE=CELL,VOICE:+{info.tel}"] + ([f"URL:{info.page}"] if info.page else []) + [
             f"X-SOCIALPROFILE;TYPE=instagram:https://www.instagram.com/{info.instagram}/",
             f"NOTE:IBAN {Q.iban_display(info.iban)} ({info.holder.title()}\\, {info.bank})", "END:VCARD"]
    with open(os.path.join(OUT, "soylu.vcf"), "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(lines) + "\n")


def data_uri(fn, mime):
    return f"data:{mime};base64," + base64.b64encode(open(os.path.join(OUT, fn), "rb").read()).decode()


def embed_fonts(css):
    for key in FONTS:
        css = css.replace(f"url(fonts/{key}.woff)", f"url({data_uri('fonts/' + key + '.woff', 'font/woff')})")
    return css


def letters(text, cls=""):
    """Harf harf (sırayla oturan animasyon için); boşluk korunur."""
    return "".join(f'<span{cls}>{"&nbsp;" if c == " " else html.escape(c)}</span>' for c in text)


def iban_groups(iban):
    """IBAN dörtlü gruplar (ödeme kartı görününce sırayla belirir)."""
    return " ".join(f"<i>{g}</i>" for g in Q.iban_display(iban).split())


# ---------------------------------------------------------------- sayfa

CSS = """
@font-face{font-family:"Sora";font-weight:400;font-display:swap;src:url(fonts/text.woff) format("woff")}
@font-face{font-family:"Sora";font-weight:600;font-display:swap;src:url(fonts/text-sb.woff) format("woff")}
@font-face{font-family:"Sora";font-weight:800;font-display:swap;src:url(fonts/text-xb.woff) format("woff")}
/* siyah, tek sütun; kırmızı yalnız vurgu. Ölçek: 11 · 13 · 15 · 16 · 30 · büyük */
:root{color-scheme:dark;--bg:#0a0a0b;--surface:#131315;--raise:#1a1a1d;--line:#242428;--line2:#35353b;
  --text:#f5f5f2;--muted:#a1a1a8;--dim:#6b6b73;--red:#e0202e;--red-ink:#fff;--ok:#1f9d55;--white:#fff;
  --ui:"Sora",system-ui,-apple-system,"Segoe UI",sans-serif;--sy:0px}
*{box-sizing:border-box;margin:0}
html{background:var(--bg);-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--text);font:400 16px/1.55 var(--ui);min-height:100vh;overflow-x:hidden}
a{color:inherit;-webkit-tap-highlight-color:transparent}
button{font:inherit;color:inherit}
:focus-visible{outline:2px solid var(--red);outline-offset:3px}
.topline{height:4px;background:var(--red);transform-origin:left}
.wrap{max-width:480px;margin:0 auto;padding-left:max(20px,env(safe-area-inset-left,0px));
  padding-right:max(20px,env(safe-area-inset-right,0px));padding-block:0 calc(110px + env(safe-area-inset-bottom,0px))}
/* ---- başlık ---- */
/* başlık kenardan kenara (şerit ekran kenarında kesilir, yatay taşma olmaz) */
.hero{position:relative;isolation:isolate;overflow:hidden;padding-block:34px 30px;
  margin-left:calc(-1 * max(20px,env(safe-area-inset-left,0px)));margin-right:calc(-1 * max(20px,env(safe-area-inset-right,0px)));
  padding-left:max(20px,env(safe-area-inset-left,0px));padding-right:max(20px,env(safe-area-inset-right,0px))}
.hero::before{content:"";position:absolute;z-index:-2;inset:0;pointer-events:none;
  background-image:linear-gradient(var(--line) 1px,transparent 1px),linear-gradient(90deg,var(--line) 1px,transparent 1px);
  background-size:30px 30px;background-position:-1px -1px;opacity:.55;
  -webkit-mask-image:radial-gradient(80% 70% at 70% 30%,#000,transparent 75%);mask-image:radial-gradient(80% 70% at 70% 30%,#000,transparent 75%)}
.slash{position:absolute;z-index:-1;top:-30px;right:-112px;width:150px;height:340px;background:var(--red);
  transform:skewX(20deg);translate:0 calc(var(--sy) * -1);pointer-events:none}
.slash::before{content:"";position:absolute;top:0;bottom:0;left:-30px;width:12px;background:var(--red);opacity:.5}
.eyebrow{display:flex;align-items:center;gap:10px;font:600 12px/1 var(--ui);letter-spacing:.26em;color:var(--muted)}
.eyebrow::before{content:"";width:18px;height:2px;background:var(--red)}
.mark{position:relative;display:inline-block;margin-top:24px;font:800 clamp(70px,22vw,104px)/.9 var(--ui);
  letter-spacing:-.035em}
.mark .w{display:block}
.mark .wipe{position:absolute;inset:-.02em -.06em -.06em;background:var(--red);transform:scaleX(0);transform-origin:left}
.rule{width:96px;height:4px;margin-top:22px;background:var(--red);transform-origin:left}
.kind{display:flex;margin-top:18px;font:600 15px/1 var(--ui);letter-spacing:.5em}
.kind span{display:inline-block}
.lead{margin-top:18px;max-width:30ch;color:var(--muted);font-size:15px}
/* ---- Hemen Ara ---- */
.call{position:relative;overflow:hidden;display:flex;align-items:center;gap:14px;margin-top:6px;
  padding:18px 18px 18px 22px;border-radius:14px;background:var(--red);color:var(--red-ink);text-decoration:none;
  box-shadow:0 20px 40px -24px rgba(224,32,46,.85);transition:transform .15s,filter .15s}
.call::after{content:"";position:absolute;top:-20%;bottom:-20%;left:-45%;width:30%;pointer-events:none;
  background:linear-gradient(100deg,transparent,rgba(255,255,255,.32),transparent);transform:skewX(-20deg)}
.call:active{transform:scale(.985);filter:brightness(.95)}
.call .t{flex:1;min-width:0}
.call small{display:block;font:600 12px/1 var(--ui);letter-spacing:.24em;opacity:.85}
.call b{display:block;margin-top:9px;font:800 clamp(24px,7.4vw,30px)/1 var(--ui);letter-spacing:-.01em;
  font-variant-numeric:tabular-nums;white-space:nowrap}
.call .ib{flex:none;display:grid;place-items:center;width:48px;height:48px;border-radius:50%;background:rgba(0,0,0,.2)}
.call .ic{width:22px;height:22px;fill:var(--red-ink)}
/* ---- bağlantılar: numaralı liste ---- */
.list{margin-top:18px;border-top:1px solid var(--line)}
.row{position:relative;display:grid;grid-template-columns:26px 40px minmax(0,1fr) 18px;align-items:center;gap:12px;
  padding:15px 2px;border-bottom:1px solid var(--line);text-decoration:none}
.row::after{content:"";position:absolute;left:0;right:0;bottom:-1px;height:1px;background:var(--red);transform:scaleX(0);
  transform-origin:left;transition:transform .35s cubic-bezier(.2,.8,.2,1)}
.row:active::after,.row:hover::after{transform:none}
.row .n{font:600 12px/1 var(--ui);letter-spacing:.06em;color:var(--red);font-variant-numeric:tabular-nums}
.row .ib{display:grid;place-items:center;width:40px;height:40px;border-radius:10px;background:var(--surface);
  border:1px solid var(--line2)}
.row .ic{width:20px;height:20px;fill:var(--text)}
.row b{display:block;font:600 16px/1.2 var(--ui)}
.row small{display:block;margin-top:4px;font-size:13px;line-height:1.3;color:var(--muted);overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
.row .go{width:18px;height:18px;fill:none;stroke:var(--dim);stroke-width:2;stroke-linecap:round;stroke-linejoin:round;
  transition:stroke .2s,transform .2s}
.row:active .go,.row:hover .go{stroke:var(--red);transform:translateX(3px)}
/* ---- ödeme ---- */
.sec{display:flex;align-items:center;gap:12px;margin:42px 0 14px;font:600 12px/1 var(--ui);letter-spacing:.3em;
  color:var(--muted)}
.sec::before{content:"";width:8px;height:8px;background:var(--red)}
.sec::after{content:"";flex:1;height:1px;background:var(--line)}
.pay{position:relative;overflow:hidden;padding:22px 20px 20px;border-radius:16px;background:var(--surface);
  border:1px solid var(--line);container-type:inline-size}
.pay::before{content:"";position:absolute;left:0;right:0;top:0;height:3px;background:var(--red);transform-origin:left}
.rows{display:grid;grid-template-columns:auto 1fr;gap:10px 20px;font-size:15px}
.rows dt{color:var(--muted)}
.rows dd{font-weight:600;text-align:right}
.ibanbox{margin-top:18px;padding:14px 16px 15px;border-radius:12px;background:var(--bg);border:1px solid var(--line2)}
.ibanbox span{display:block;font:600 11px/1 var(--ui);letter-spacing:.3em;color:var(--dim)}
.iban{display:block;margin-top:9px;font:800 17px/1.2 var(--ui);font-size:min(17px,4.45cqi);letter-spacing:-.01em;
  word-spacing:-.02em;font-variant-numeric:tabular-nums;white-space:nowrap;user-select:all;-webkit-user-select:all}
.iban i{font-style:normal;display:inline-block}
.acts{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px}
.acts.one{grid-template-columns:1fr}
.btn{display:flex;align-items:center;justify-content:center;gap:9px;min-height:52px;border-radius:12px;cursor:pointer;
  font:600 15px/1 var(--ui);text-decoration:none;transition:transform .15s,background .2s,border-color .2s}
.btn:active{transform:scale(.97)}
.btn .ic{width:19px;height:19px}
.btn span{white-space:nowrap}
.copy{border:0;background:var(--red);color:var(--red-ink)}
.copy .ic{fill:var(--red-ink)}
.copy.ok{background:var(--ok)}
.ghost{border:1px solid var(--line2);background:transparent;color:var(--text)}
.ghost .ic{fill:var(--text)}
.ghost[aria-expanded="true"]{border-color:var(--red)}
.kk{margin-top:12px;padding:18px 16px 14px;border-radius:14px;background:var(--raise);border:1px solid var(--line);
  text-align:center}
.kk .qr{display:inline-block;padding:12px;border-radius:12px;background:var(--white)}
.kk img{display:block;width:min(220px,58vw);height:auto;image-rendering:pixelated}
.kk p{margin:12px 4px 8px;font-size:14px;color:var(--muted)}
.kk p b{color:var(--text);font-weight:600}
.kk a{color:var(--text);font-weight:600;text-decoration-color:var(--red);text-underline-offset:4px}
/* ---- altbilgi ---- */
footer{display:flex;justify-content:space-between;align-items:flex-end;gap:12px;margin-top:48px;padding-top:22px;
  border-top:1px solid var(--line);color:var(--dim);font-size:13px}
footer b{display:block;font:800 22px/1 var(--ui);letter-spacing:-.03em;color:var(--text)}
footer b i{display:block;width:34px;height:3px;margin-top:9px;background:var(--red)}
/* ---- alttaki arama şeridi, bildirim ---- */
.callbar{position:fixed;z-index:20;left:0;right:0;bottom:0;display:flex;justify-content:center;
  padding:12px max(16px,env(safe-area-inset-right,0px)) calc(12px + env(safe-area-inset-bottom,0px)) max(16px,env(safe-area-inset-left,0px));
  background:rgba(10,10,11,.86);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);border-top:1px solid var(--line);
  transform:translateY(110%);transition:transform .35s cubic-bezier(.2,.8,.2,1)}
.callbar.show{transform:none}
.callbar a{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;max-width:440px;min-height:52px;
  border-radius:12px;background:var(--red);color:var(--red-ink);text-decoration:none;font:600 16px/1 var(--ui)}
.callbar .ic{width:20px;height:20px;fill:var(--red-ink)}
.callbar span{font-variant-numeric:tabular-nums}
.toast{position:fixed;z-index:30;left:50%;bottom:calc(92px + env(safe-area-inset-bottom));transform:translate(-50%,40px);
  width:max-content;max-width:calc(100vw - 32px);text-align:center;background:var(--raise);color:var(--text);
  border:1px solid var(--line2);border-left:4px solid var(--red);padding:12px 18px;border-radius:12px;font-weight:600;
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
@keyframes flash{0%{color:var(--red)}100%{color:var(--text)}}
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
.row:nth-child(1){animation-delay:2.15s}.row:nth-child(2){animation-delay:2.23s}
.row:nth-child(3){animation-delay:2.31s}.row:nth-child(4){animation-delay:2.39s}
.pay::before{transform:scaleX(0)}
.pay.in::before{animation:grow .8s .1s cubic-bezier(.2,.8,.2,1) both}
.pay.in .iban i{animation:grp .45s cubic-bezier(.2,.8,.2,1) both}
.iban.flash{animation:flash .9s ease-out}
.kk:not([hidden]){animation:open .35s cubic-bezier(.2,.8,.2,1)}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}
  .pay::before{transform:none}}
"""
# OTO LASTİK harfleri ve IBAN grupları: sırayla
CSS += "".join(f".kind span:nth-child({k + 1}){{animation-delay:{1.55 + 0.04 * k:.2f}s}}" for k in range(12))
CSS += "".join(f".pay.in .iban i:nth-child({k + 1}){{animation-delay:{0.2 + 0.07 * k:.2f}s}}" for k in range(8)) + "\n"

JS = S.JS + """
(()=>{const R=document.documentElement,still=matchMedia('(prefers-reduced-motion: reduce)').matches;
if(document.hidden){const as=document.getAnimations();as.forEach(a=>a.pause());
  addEventListener('visibilitychange',()=>{if(!document.hidden)as.forEach(a=>a.play())},{once:true})}
if(!still){let q=0;addEventListener('scroll',()=>{if(!q)q=requestAnimationFrame(()=>{
  R.style.setProperty('--sy',(Math.min(scrollY,400)*.25).toFixed(1)+'px');q=0})},{passive:true})}
const p=document.querySelector('.pay');
if('IntersectionObserver' in window){
  const io=new IntersectionObserver(([e])=>{if(e.isIntersecting){p.classList.add('in');io.disconnect()}},{threshold:.35});
  io.observe(p);
  const bar=document.querySelector('.callbar'),call=document.querySelector('.call');
  new IntersectionObserver(([e])=>bar.classList.toggle('show',!e.isIntersecting&&e.boundingClientRect.top<0)).observe(call)}
else p.classList.add('in');
const kb=document.getElementById('kk-btn'),kk=document.getElementById('kk');
if(kb)kb.addEventListener('click',()=>{const o=kk.hidden;kk.hidden=!o;kb.setAttribute('aria-expanded',o);
  if(o)kk.scrollIntoView({behavior:still?'auto':'smooth',block:'nearest'})})})();
"""

ARROW = "M5 12h14M13 6l6 6-6 6"


def page(info, standalone=False, artifact=False):
    """Site (`soylu_isimlik/site`), tek dosya önizleme (standalone: yazı tipleri ve karekod gömülü) ya da Claude
    önizleme sayfası (artifact: belge iskeleti yayında eklenir; indirme bağlantısı yok; ara düğmeleri numarayı da
    kopyalar)."""
    standalone = standalone or artifact
    e = html.escape
    wa = Q.whatsapp_link(info)
    insta = f"https://www.instagram.com/{info.instagram}/"
    title = "Soylu Oto Lastik"
    desc = "Soylu Oto Lastik, Antalya: mobil lastik tamir ve servis. Hemen arayın, WhatsApp'tan yazın; ödeme bilgileri."
    css = embed_fonts(CSS) if standalone else CSS
    kk = (data_uri("karekod.png", "image/png") if standalone else "karekod.png") if info.karekod else ""
    tel = f' data-tel="{e(info.phone)}"' if artifact else ""
    go = f'<svg class="go" viewBox="0 0 24 24" aria-hidden="true"><path d="{ARROW}"/></svg>'
    rows = [(wa, S.svg(S.logo_path("whatsapp")), "WhatsApp", "Mesaj gönderin", ""),
            (insta, S.svg(S.logo_path("instagram")), "Instagram", "@" + info.instagram, ""),
            (info.google, S.svg(S.ICON["star"]), "Google", "Yorumları görün, yorum yapın", "")]
    if not artifact:
        rows.append(("soylu.vcf", S.svg(S.ICON["person"]), "Rehbere kaydet", "Numarayı ekleyin",
                     ' download="Soylu Oto Lastik.vcf"'))
    # aynı sekmede açılır: yeni sekme QR okuyucuların iç tarayıcılarında çoğu zaman açılmaz
    links = "\n  ".join(f'<a class="row" href="{e(h)}"{x}><span class="n">{k:02d}</span><span class="ib">{ic}</span>'
                        f'<span><b>{e(t)}</b><small>{e(s)}</small></span>{go}</a>'
                        for k, (h, ic, t, s, x) in enumerate(rows, 1))
    if info.karekod:
        save = "Karekoda basılı tutup kaydedin," if artifact else "Karekodu kaydedin,"
        save_link = "" if artifact else f'\n      <a href="{kk}" download="soylu-karekod.png">Karekodu kaydet</a>'
        kk_btn = (f'\n    <button class="btn ghost" type="button" id="kk-btn" aria-expanded="false" aria-controls="kk">'
                  f'{S.svg(S.ICON["qr"])}Karekod</button>')
        kk_box = f"""
  <div class="kk" id="kk" hidden>
    <span class="qr"><img src="{kk}" width="828" height="828" alt="{e(info.bank)} karekodu – {e(info.holder)}"></span>
    <p>{save} banka uygulamanızda <b>Karekod ile Öde</b>, ardından <b>Galeriden seç</b>.</p>{save_link}
  </div>"""
    else:
        kk_btn = kk_box = ""
    og = (f'<meta property="og:url" content="{e(info.page)}">\n<meta property="og:image" content="{e(info.page)}og.png">'
          if info.page else "")
    favicon = ("data:image/svg+xml," + "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>"
               "<rect width='64' height='64' rx='14' fill='%230a0a0b'/><path d='M44 0h20v64H22z' fill='%23e0202e'/>"
               "<rect x='12' y='44' width='18' height='5' fill='%23f5f5f2'/><rect x='12' y='15' width='18' height='5' "
               "fill='%23f5f5f2'/><rect x='12' y='29.5' width='18' height='5' fill='%23f5f5f2'/></svg>")
    body = f"""<div class="topline" aria-hidden="true"></div>
<div class="wrap">
<header class="hero">
  <div class="slash" aria-hidden="true"></div>
  <p class="eyebrow">ANTALYA · LASTİK SERVİSİ</p>
  <h1 class="mark" aria-label="Soylu"><span class="w">{NAME}</span><span class="wipe" aria-hidden="true"></span></h1>
  <div class="rule" aria-hidden="true"></div>
  <p class="kind" aria-label="Oto Lastik">{letters("OTO LASTİK")}</p>
  <p class="lead">{e(LEAD)}</p>
</header>
<main>
<a class="call" href="tel:+{info.tel}"{tel}><span class="t"><small>HEMEN ARA</small><b>{e(info.phone)}</b></span>
  <span class="ib">{S.svg(S.ICON["phone"])}</span></a>
<nav class="list" aria-label="Bağlantılar">
  {links}
</nav>
<h2 class="sec">ÖDEME BİLGİLERİ</h2>
<section class="pay" aria-label="Ödeme bilgileri">
  <dl class="rows"><dt>Banka</dt><dd>{e(info.bank)}</dd><dt>Alıcı</dt><dd>{e(info.holder)}</dd></dl>
  <div class="ibanbox"><span>IBAN</span><output class="iban">{iban_groups(info.iban)}</output></div>
  <div class="acts{'' if info.karekod else ' one'}">
    <button class="btn copy" type="button" data-copy="{e(info.iban)}">{S.svg(S.ICON["copy"])}<span>{"Kopyala" if info.karekod else "IBAN'ı kopyala"}</span></button>{kk_btn}
  </div>{kk_box}
</section>
</main>
<footer>
  <b>SOYLU<i></i></b><span>@{e(info.instagram)}</span>
</footer>
</div>
<div class="callbar"><a href="tel:+{info.tel}"{tel} aria-label="Hemen ara">{S.svg(S.ICON["phone"])}Hemen ara · <span>{e(info.phone)}</span></a></div>
<div class="toast" role="status" aria-live="polite"></div>
<script>{JS}</script>
"""
    if artifact:
        return f"""<title>Soylu Oto Lastik</title>
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
<meta name="theme-color" content="#0a0a0b">
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
body{{margin:0;overflow:hidden}} .wrap{{max-width:none;padding:0 100px}} .hero{{padding-block:120px 0}}
.topline{{height:10px}} .hero{{margin:0;padding-inline:0;overflow:visible}}
.slash{{right:-60px;top:-60px;width:330px;height:900px}} .slash::before{{left:-70px;width:28px}}
.eyebrow{{font-size:26px}} .mark{{font-size:210px;margin-top:40px}} .rule{{width:220px;height:10px;margin-top:40px}}
.kind{{font-size:34px;margin-top:36px}}</style>
<div class="topline"></div><div class="wrap"><header class="hero"><div class="slash"></div>
<p class="eyebrow">ANTALYA · LASTİK SERVİSİ</p><h1 class="mark"><span class="w">{NAME}</span></h1><div class="rule"></div>
<p class="kind">{letters("OTO LASTİK")}</p></header></div>"""
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        pg = b.new_page(viewport={"width": 1200, "height": 630}, reduced_motion="reduce")
        pg.set_content(doc)
        pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(OUT, "og.png"))
        b.close()


def screenshot(path=PREVIEW):
    """Telefon ekranında (390 px): üst görünüm ve tüm sayfa yan yana."""
    from playwright.sync_api import sync_playwright
    top, full = path.replace(".png", "_ust.png"), path.replace(".png", "_tam.png")
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, reduced_motion="reduce")
        pg.goto("file://" + os.path.join(OUT, "index.html"))
        pg.wait_for_timeout(400)
        assert pg.evaluate("document.fonts.check('800 20px \"Sora\"')"), "yazı tipi yüklenmedi"
        assert pg.evaluate("document.documentElement.scrollWidth") <= 390, "yatay taşma"
        assert pg.evaluate("[...document.querySelectorAll('.iban,.call b,.row b,.row small,.rows dd,.mark')]"
                           ".every(e=>e.scrollWidth<=e.clientWidth+1)"), "yazı sığmadı"
        pg.screenshot(path=top)
        pg.add_style_tag(content=".callbar{display:none}")          # tam sayfa görüntüde ortada kalmasın
        if pg.locator("#kk-btn").count():
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
    """Tam tur (390 × 844): açılış, aşağı kaydırma, IBAN'ı kopyala (ve varsa karekod); dokunulan yer halkayla."""
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
        for k in range(0, 2900, 70):                         # açılış: animasyonlar zamanda adım adım
            _seek(pg, k)
            shot(pg, 70)
        _finish(pg)
        shot(pg, 900)
        h = pg.evaluate("document.documentElement.scrollHeight - innerHeight")
        for y in range(0, h + 1, 38):
            pg.evaluate(f"scrollTo(0,{y})")
            pg.wait_for_timeout(40)
            shot(pg, 60)
        pg.evaluate(f"scrollTo(0,{h})")
        for _ in range(10):
            pg.wait_for_timeout(100)
            shot(pg, 100)
        tap = tap_on(pg, ".copy")
        shot(pg, 300, tap)
        pg.mouse.click(*tap)
        for _ in range(5):
            pg.wait_for_timeout(120)
            shot(pg, 160)
        durs[-1] = 1400
        if pg.locator("#kk-btn").count():
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
    print("karekod:", "var" if info.karekod else "yok (bilgiler.json → iban_karekod gelince eklenir)")
    print("önizleme:", *(os.path.relpath(f(), A.ROOT) for f in (screenshot, tour_gif)))


if __name__ == "__main__":
    main()
