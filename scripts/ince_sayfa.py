"""İNCE OTO LASTİK – isimlikteki QR ile açılan işletme sayfası (siyah, motor sporu havası; telefona göre).

Uzar'ın sayfasıyla aynı işler, ayrı tasarım. Siyah zemin, eğik ve dar kalın yazı (Saira Condensed Black Italic),
tek vurgu rengi kırmızı. Lastik çizimi yok; tasarımın dili lastik izi: gidiş yönüne bakan ok biçimli diş baskısı
(Hemen Ara düğmesinde başlayan desen). Başlıkta logonun arkasından çapraz geçen büyük diş bandı, kutucukların ve
IBAN kartının köşesinde, altbilgide aynı baskı.

Animasyon belirgin ama dönen bir şey yok:
  açılış   bant yuvarlanarak gelip durur, İNCE harf harf yükselir, OTO LASTİK soldan açılır, düğmeler sırayla gelir;
           Hemen Ara'nın diş baskısı akıp durur, telefon bir kez çalar
  kaydırma diş bandı ve kart deseni kaydırdıkça akar; IBAN kartı göründüğünde üzerinden ışık geçer;
           Hemen Ara ekrandan çıkınca sağ altta kırmızı ara düğmesi belirir
  sürekli  yalnız ufak işaretler: 7/24 noktası atar, Hemen Ara birkaç saniyede bir parlar ve telefon çalar
Sayfa arka sekmede açılırsa açılış görünür olunca başlar; "hareketi azalt" açıksa hiçbiri oynamaz.

Sayfada: Hemen Ara, WhatsApp (hazır mesajlı), Instagram, Google yorumları (işletmenin paylaşım bağlantısı), ödeme
bilgileri (alıcı, banka, IBAN + tek dokunuşla kopyala, banka karekodu: kaydedip banka uygulamasında galeriden
okutulur) ve Rehbere Kaydet (vCard). Dış bağlantı yok: yazı tipleri ve simgeler sayfanın içinde.

Bilgiler `ince_isimlik/bilgiler.json`dan okunur (scripts/qr_sistemi.py doğrular: IBAN mod-97, karekodun CRC'si,
içindeki IBAN ve alıcı). Banka karekodu bankanın verdiğiyle aynı baytlarla (UTF-8, ECI'siz, hata düzeltme Q)
yeniden çizilir; "HAFİSE İNCE"deki İ harfleri banka uygulamasında da aynı okunur.

Yayın: Uzar'dan sonraki bütün işletmelerin sitelerinin durduğu ortak Cloudflare hesabında `ince` adlı Worker'a
`ince_site.zip` yüklenir (pages.dev Türkiye'de kapalı, workers.dev açık; adres `ince.<ortak alt alan>.workers.dev`).
Kesin adres `bilgiler.json` → `sayfa_url`a yazılır, bu komut yeniden çalıştırılır (paylaşım kartı adresi kullanır)
ve isimlikteki QR o adrese döner.

Çıktı : ince_isimlik/site/ (index.html, karekod.png, ince.vcf, og.png, fonts/*.woff), ince_isimlik/ince_site.zip,
        ince_isimlik/sayfa_onizleme.png (telefon ekranı), sayfa_animasyon.gif (açılış), sayfa_tur.gif (kaydırma,
        IBAN kopyala, karekod), sayfa_onizleme.html (tek dosya), sayfa_artifact.html (Claude önizlemesi)

Kullanım:
  pip install segno zxing-cpp playwright fonttools
  python3 scripts/ince_sayfa.py
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

BASE = os.path.join(A.ROOT, "ince_isimlik")
DATA = os.path.join(BASE, "bilgiler.json")
OUT = os.path.join(BASE, "site")
ZIP = os.path.join(BASE, "ince_site.zip")
PREVIEW = os.path.join(BASE, "sayfa_onizleme.png")
GIF = os.path.join(BASE, "sayfa_animasyon.gif")
TOUR = os.path.join(BASE, "sayfa_tur.gif")
STANDALONE = os.path.join(BASE, "sayfa_onizleme.html")
ARTIFACT = os.path.join(BASE, "sayfa_artifact.html")
# Saira (OFL): değişken yazı tipinden sabit kesimler, latin + latin-ext birleşik
FONTS = {"display": "Saira-CondensedBlackItalic.ttf", "cond": "Saira-CondensedBoldItalic.ttf",
         "text": "Saira-Medium.ttf", "text-sb": "Saira-SemiBold.ttf"}
CHROMIUM = "/opt/pw-browsers/chromium"


# ---------------------------------------------------------------- dosyalar

def subset_fonts():
    from fontTools import subset
    os.makedirs(os.path.join(OUT, "fonts"), exist_ok=True)
    for key, fn in FONTS.items():
        opts = subset.Options()
        opts.flavor = "woff"
        opts.layout_features = ["kern", "liga", "locl", "tnum"]
        f = subset.load_font(os.path.join(A.FONT_DIR, fn), opts)
        s = subset.Subsetter(opts)
        s.populate(text=S.CHARS)
        s.subset(f)
        subset.save_font(f, os.path.join(OUT, "fonts", key + ".woff"), opts)
    with open(os.path.join(A.FONT_DIR, "OFL-saira.txt"), "rb") as src, \
            open(os.path.join(OUT, "fonts", "OFL-saira.txt"), "wb") as dst:
        dst.write(src.read())


def karekod_png(info):
    """Banka karekodu: bankanınkiyle aynı baytlar (UTF-8, ECI yok) ve aynı hata düzeltme (Q)."""
    import segno
    import zxingcpp
    path = os.path.join(OUT, "karekod.png")
    segno.make(info.karekod, error="q", mode="byte", encoding="utf-8", eci=False, micro=False,
               boost_error=False).save(path, scale=12, border=4)
    r = zxingcpp.read_barcodes(Image.open(path).convert("L"))
    assert len(r) == 1 and r[0].text == info.karekod and r[0].bytes == info.karekod.encode("utf-8"), "karekod"
    return path


def vcard(info):
    lines = ["BEGIN:VCARD", "VERSION:3.0", "N:;İnce Oto Lastik;;;", "FN:İnce Oto Lastik", "ORG:İnce Oto Lastik",
             f"TEL;TYPE=CELL,VOICE:+{info.tel}"] + ([f"URL:{info.page}"] if info.page else []) + [
             f"X-SOCIALPROFILE;TYPE=instagram:https://www.instagram.com/{info.instagram}/",
             f"NOTE:7/24 hizmet. IBAN {Q.iban_display(info.iban)} ({info.holder.title()}\\, {info.bank})",
             "END:VCARD"]
    with open(os.path.join(OUT, "ince.vcf"), "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(lines) + "\n")


def data_uri(fn, mime):
    return f"data:{mime};base64," + base64.b64encode(open(os.path.join(OUT, fn), "rb").read()).decode()


def embed_fonts(css):
    for key in FONTS:
        css = css.replace(f"url(fonts/{key}.woff)", f"url({data_uri('fonts/' + key + '.woff', 'font/woff')})")
    return css


# ---------------------------------------------------------------- lastik izi deseni

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


STAR = "M12 2.5l2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.3 6.1 20.6l1.3-6.6L2.5 9.4l6.6-.8z"
ARROW = "M7 17L17 7M9 7h8v8"


# ---------------------------------------------------------------- sayfa

CSS = """
@font-face{font-family:"Saira Condensed";font-style:italic;font-weight:900;font-display:swap;src:url(fonts/display.woff) format("woff")}
@font-face{font-family:"Saira Condensed";font-style:italic;font-weight:700;font-display:swap;src:url(fonts/cond.woff) format("woff")}
@font-face{font-family:"Saira";font-weight:500;font-display:swap;src:url(fonts/text.woff) format("woff")}
@font-face{font-family:"Saira";font-weight:600;font-display:swap;src:url(fonts/text-sb.woff) format("woff")}
/* tek sütun, siyah; başlıkta logonun arkasından çapraz diş bandı, altında Hemen Ara, üç kutucuk, IBAN kartı */
:root{color-scheme:dark;--bg:#0a0a0a;--card:#141415;--card2:#1b1b1d;--line:#28282b;--line2:#3a3a3e;
  --text:#f5f5f2;--muted:#9d9da4;--dim:#67676d;--red:#e3241b;--ok:#1f9d55;--white:#fff;--star:#f5b400;
  --display:"Saira Condensed","Saira","Arial Narrow",sans-serif;
  --ui:"Saira",system-ui,-apple-system,"Segoe UI",sans-serif;
  --tread-red:TREAD_SMALL_DARK;--tread-band:TREAD_BAND_GREY;--tread-light:TREAD_BAND_LIGHT;--roll:0px}
*{box-sizing:border-box;margin:0}
html{background:var(--bg);-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--text);font:500 16px/1.45 var(--ui);min-height:100vh;overflow-x:hidden;
  padding-bottom:env(safe-area-inset-bottom)}
.wrap{--gl:max(16px,env(safe-area-inset-left,0px));--gr:max(16px,env(safe-area-inset-right,0px));
  max-width:480px;margin:0 auto;padding-left:var(--gl);padding-right:var(--gr);padding-block:0 92px}
a{color:inherit;-webkit-tap-highlight-color:transparent}
button{font:inherit;color:inherit}
:focus-visible{outline:2px solid var(--red);outline-offset:3px}
.bleed{margin-left:calc(var(--gl) * -1);margin-right:calc(var(--gr) * -1)}
/* ---- başlık ---- */
.hero{position:relative;overflow:hidden;isolation:isolate;padding:44px var(--gr) 34px var(--gl);
  background:radial-gradient(80% 60% at 100% 0%,rgba(227,36,27,.22),transparent 65%),var(--bg)}
.band{position:absolute;z-index:-1;left:-40%;right:-40%;top:118px;height:150px;transform:rotate(-12deg);
  overflow:hidden;background:#111112;box-shadow:inset 0 1px 0 rgba(255,255,255,.05),inset 0 -1px 0 rgba(255,255,255,.05);
  -webkit-mask-image:linear-gradient(90deg,transparent 14%,#000 34%,#000 74%,transparent 92%);
  mask-image:linear-gradient(90deg,transparent 14%,#000 34%,#000 74%,transparent 92%)}
.band i{position:absolute;inset:0 -400px;background:var(--tread-band) 0 0/auto 100% repeat-x;
  background-position:calc(var(--roll) * -1) 0}
.tag{display:inline-flex;align-items:center;gap:9px;font:700 italic 15px/1 var(--display);letter-spacing:.14em}
.live{width:8px;height:8px;border-radius:50%;background:var(--red);box-shadow:0 0 0 0 rgba(227,36,27,.7)}
.mark{display:flex;margin:14px 0 0 -.03em;font:900 italic min(200px,49vw)/.8 var(--display);letter-spacing:-.01em;
  filter:drop-shadow(0 14px 22px rgba(0,0,0,.6))}
.mark .l{display:block;padding:.1em .02em 0;background:linear-gradient(180deg,#fff 30%,#c9c9c9);
  -webkit-background-clip:text;background-clip:text;color:transparent}
.sub{display:flex;align-items:center;gap:14px;margin-top:12px}
.sub span{font:900 italic 34px/1 var(--display);letter-spacing:.03em;color:var(--red)}
.sub::after{content:"";flex:1;height:3px;background:linear-gradient(90deg,var(--red),transparent);transform:skewX(-20deg)}
.lead{margin-top:10px;color:var(--muted);font-size:16px}
/* ---- Hemen Ara ---- */
.call{position:relative;overflow:hidden;isolation:isolate;display:flex;align-items:center;gap:14px;margin-top:6px;
  padding:20px 18px 20px 22px;border-radius:16px;text-decoration:none;color:#fff;
  background:linear-gradient(115deg,#ec2b21,#b3130e);box-shadow:0 22px 44px -24px rgba(227,36,27,.9);
  transition:transform .15s}
.call::before{content:"";position:absolute;inset:-2px;z-index:-1;background:var(--tread-red) 0 0/22px 30px;opacity:.2;
  -webkit-mask-image:linear-gradient(100deg,transparent 30%,#000 90%);mask-image:linear-gradient(100deg,transparent 30%,#000 90%)}
.call::after{content:"";position:absolute;top:0;bottom:0;left:0;width:38%;z-index:-1;pointer-events:none;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.28),transparent);transform:translateX(-140%) skewX(-20deg)}
.call:active{transform:scale(.985)}
.call .t{flex:1;min-width:0}
.call small{display:block;font:700 italic 15px/1 var(--display);letter-spacing:.16em;color:rgba(255,255,255,.85)}
.call b{display:block;margin-top:6px;font:900 italic clamp(30px,9.4vw,40px)/1 var(--display);letter-spacing:.01em;
  font-variant-numeric:tabular-nums;white-space:nowrap}
.call .ib{flex:none;display:grid;place-items:center;width:52px;height:52px;border-radius:50%;background:#fff;
  box-shadow:0 0 0 7px rgba(255,255,255,.14)}
.call .ib .ic{width:24px;height:24px;fill:var(--red)}
/* ---- kutucuklar ---- */
.tiles{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:10px}
.tile{position:relative;overflow:hidden;isolation:isolate;display:flex;flex-direction:column;justify-content:space-between;
  gap:18px;min-height:112px;padding:14px 12px 13px;border-radius:14px;background:var(--card);border:1px solid var(--line);
  text-decoration:none;transition:transform .15s,border-color .15s}
.tile::after{content:"";position:absolute;z-index:-1;right:-12px;bottom:-22px;width:64px;height:120px;
  background:var(--tread-light) 0 0/auto 60px;opacity:.06;transform:rotate(-12deg)}
.tile:active{transform:scale(.97);border-color:var(--line2)}
.tile .ic{width:24px;height:24px;fill:var(--text)}
.tile .go{position:absolute;top:12px;right:11px;width:16px;height:16px;fill:none;stroke:var(--dim);stroke-width:2.2;
  stroke-linecap:round;stroke-linejoin:round}
.tile b{display:block;font:700 italic 18px/1 var(--display);letter-spacing:.03em;text-transform:uppercase}
.tile small{display:block;margin-top:4px;font-size:12px;line-height:1.2;color:var(--muted);overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
.stars{display:flex;gap:1px;margin-top:5px}
.stars svg{width:12px;height:12px;fill:var(--star)}
/* ---- ödeme ---- */
.sec{display:flex;align-items:center;gap:12px;margin:34px 0 14px;font:900 italic 22px/1 var(--display);
  letter-spacing:.05em}
.sec::before{content:"";width:14px;height:22px;background:var(--red);transform:skewX(-16deg)}
.sec::after{content:"";flex:1;height:1px;background:var(--line)}
.card{position:relative;overflow:hidden;isolation:isolate;display:flex;flex-direction:column;gap:22px;
  padding:20px 20px 18px;border-radius:18px;container-type:inline-size;
  background:radial-gradient(120% 90% at 0% 0%,rgba(227,36,27,.16),transparent 55%),
             linear-gradient(140deg,#1f1f22,#121214 60%,#0c0c0d);
  border:1px solid var(--line2);box-shadow:0 30px 50px -32px #000,inset 0 1px 0 rgba(255,255,255,.07)}
.card::before{content:"";position:absolute;z-index:-1;top:-60px;right:-36px;width:92px;height:340px;
  background:var(--tread-light) 0 0/auto 92px;background-position:0 calc(var(--roll) * -.4);opacity:.07;
  transform:rotate(-24deg)}
.card::after{content:"";position:absolute;inset:0;z-index:1;pointer-events:none;
  background:linear-gradient(105deg,transparent 35%,rgba(255,255,255,.16) 50%,transparent 65%);transform:translateX(-120%)}
.card .top{display:flex;justify-content:space-between;align-items:center}
.card .bank{font:600 16px/1 var(--ui)}
.card .kind{font:700 italic 13px/1 var(--display);letter-spacing:.2em;color:var(--muted)}
.iban{font:600 18px/1.1 var(--ui);font-size:min(20px,5cqi);letter-spacing:.025em;word-spacing:.06em;
  font-variant-numeric:tabular-nums;white-space:nowrap;user-select:all;-webkit-user-select:all}
.card .who small{display:block;font:700 italic 11px/1 var(--display);letter-spacing:.22em;color:var(--dim)}
.card .who b{display:block;margin-top:6px;font:900 italic 21px/1 var(--display);letter-spacing:.04em}
.acts{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px}
.btn{display:flex;align-items:center;justify-content:center;gap:9px;width:100%;min-height:54px;border-radius:13px;
  font:700 italic 17px/1 var(--display);letter-spacing:.06em;text-transform:uppercase;cursor:pointer;
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
.save{margin-top:12px}
/* ---- altbilgi ---- */
footer{margin-top:38px}
.strip{height:26px;background:var(--tread-light) 0 0/auto 100% repeat-x;opacity:.08;
  background-position:calc(var(--roll) * -.6) 0;
  -webkit-mask-image:linear-gradient(90deg,transparent,#000 15%,#000 85%,transparent);
  mask-image:linear-gradient(90deg,transparent,#000 15%,#000 85%,transparent)}
footer p{display:flex;justify-content:space-between;align-items:baseline;gap:12px;margin-top:16px;color:var(--dim);
  font-size:13px}
footer b{font:900 italic 17px/1 var(--display);letter-spacing:.05em;color:var(--text)}
footer b span{color:var(--red)}
/* ---- kayan ara düğmesi, bildirim ---- */
.fab{position:fixed;z-index:20;right:calc(16px + env(safe-area-inset-right,0px));
  bottom:calc(18px + env(safe-area-inset-bottom,0px));display:grid;place-items:center;width:58px;height:58px;
  border-radius:50%;background:var(--red);box-shadow:0 14px 30px -8px rgba(227,36,27,.75),0 0 0 6px rgba(227,36,27,.18);
  transform:scale(0);transition:transform .35s cubic-bezier(.3,1.5,.5,1);text-decoration:none}
.fab.show{transform:scale(1)}
.fab .ic{width:26px;height:26px;fill:#fff}
.toast{position:fixed;z-index:30;left:50%;bottom:calc(90px + env(safe-area-inset-bottom));transform:translate(-50%,40px);
  width:max-content;max-width:calc(100vw - 32px);text-align:center;background:var(--card2);color:var(--text);
  border:1px solid var(--line2);border-left:4px solid var(--red);padding:12px 18px;border-radius:12px;font-weight:600;
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
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(227,36,27,.7)}75%,100%{box-shadow:0 0 0 10px rgba(227,36,27,0)}}
@keyframes sweep{from{transform:translateX(-120%)}to{transform:translateX(120%)}}
@keyframes flash{0%{color:var(--red)}100%{color:var(--text)}}
@keyframes open{from{opacity:0;transform:translateY(-8px) scale(.98)}to{opacity:1;transform:none}}
.band{animation:bandin 1.1s .05s cubic-bezier(.5,0,.2,1) both}
.band i{animation:rollin 1.7s .05s cubic-bezier(.1,.6,.2,1) both}
.tag{animation:fade .5s .25s both}
.live{animation:pulse 2s 1.5s infinite}
.mark .l{animation:letter .75s cubic-bezier(.2,1.25,.35,1) both}
.mark .l:nth-child(1){animation-delay:.35s}.mark .l:nth-child(2){animation-delay:.43s}
.mark .l:nth-child(3){animation-delay:.51s}.mark .l:nth-child(4){animation-delay:.59s}
.sub span{animation:wipe .6s .8s cubic-bezier(.6,0,.2,1) both}
.sub::after{transform-origin:left;animation:grow .7s .95s cubic-bezier(.2,.8,.2,1) both}
.lead{animation:fade .6s 1.05s both}
.call{animation:rise .6s 1.05s cubic-bezier(.2,.8,.2,1) both}
.call::before{animation:treadin 1.6s 1.05s cubic-bezier(.1,.6,.2,1) both}
.call::after{animation:shine 6s 2.6s infinite}
.call .ib .ic{animation:ringonce .8s 1.8s,ring 6s 2.6s infinite}
.tile{animation:rise .55s cubic-bezier(.2,.8,.2,1) both}
.tile:nth-child(1){animation-delay:1.2s}.tile:nth-child(2){animation-delay:1.28s}.tile:nth-child(3){animation-delay:1.36s}
.card.in::after{animation:sweep 1.1s .15s cubic-bezier(.4,0,.2,1)}
.card.in .iban{animation:flash 1.2s .3s}
.strip.in{animation:treadin 1.4s cubic-bezier(.1,.6,.2,1)}
.iban.flash{animation:flash .9s ease-out}
.kk:not([hidden]){animation:open .35s cubic-bezier(.2,.8,.2,1)}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
"""
CSS = (CSS.replace("TREAD_SMALL_DARK", tread("small", "#000")).replace("TREAD_BAND_GREY", tread("band", "#202023"))
       .replace("TREAD_BAND_LIGHT", tread("band", "#ffffff")))

JS = S.JS + """
(()=>{const R=document.documentElement,still=matchMedia('(prefers-reduced-motion: reduce)').matches;
if(document.hidden){const as=document.getAnimations();as.forEach(a=>a.pause());
  addEventListener('visibilitychange',()=>{if(!document.hidden)as.forEach(a=>a.play())},{once:true})}
if(!still){let f=0;addEventListener('scroll',()=>{if(!f)f=requestAnimationFrame(()=>{
  R.style.setProperty('--roll',(scrollY*.8).toFixed(1)+'px');f=0})},{passive:true})}
if('IntersectionObserver' in window){
  const seen=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');
    seen.unobserve(e.target)}}),{threshold:.45});
  document.querySelectorAll('.card,.strip').forEach(el=>seen.observe(el));
  const fab=document.querySelector('.fab'),call=document.querySelector('.call');
  new IntersectionObserver(([e])=>fab.classList.toggle('show',!e.isIntersecting&&e.boundingClientRect.top<0)).observe(call)}
const kb=document.getElementById('kk-btn'),kk=document.getElementById('kk');
kb.addEventListener('click',()=>{const o=kk.hidden;kk.hidden=!o;kb.setAttribute('aria-expanded',o);
  if(o)kk.scrollIntoView({behavior:still?'auto':'smooth',block:'nearest'})})})();
"""


def page(info, standalone=False, artifact=False):
    """Site (`ince_isimlik/site`), tek dosya önizleme (standalone: yazı tipleri ve karekod gömülü) ya da Claude
    önizleme sayfası (artifact: belge iskeleti yayında eklenir; oradaki çerçeve indirmeyi engellediği için
    karekod ve rehber indirme bağlantısı yok; telefon bağlantısı her izleyicide çalışmayabildiği için ara
    düğmeleri numarayı da kopyalar)."""
    standalone = standalone or artifact
    e = html.escape
    wa = Q.whatsapp_link(info)
    insta = f"https://www.instagram.com/{info.instagram}/"
    title = "İnce Oto Lastik – 7/24 Hizmet"
    desc = "İnce Oto Lastik: hemen arayın, WhatsApp'tan yazın, Instagram, Google yorumları ve ödeme bilgileri."
    css, kk = (embed_fonts(CSS), data_uri("karekod.png", "image/png")) if standalone else (CSS, "karekod.png")
    go = f'<svg class="go" viewBox="0 0 24 24" aria-hidden="true"><path d="{ARROW}"/></svg>'
    stars = '<span class="stars" aria-label="5 yıldız">' + "".join(
        f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="{STAR}"/></svg>' for _ in range(5)) + "</span>"
    # aynı sekmede açılır: yeni sekme QR okuyucuların iç tarayıcılarında çoğu zaman açılmaz
    tile = lambda href, icon, t, s: (  # noqa: E731
        f'<a class="tile" href="{e(href)}">{icon}{go}<span><b>{e(t)}</b>{s}</span></a>')
    tel = f' data-tel="{e(info.phone)}"' if artifact else ""
    save = "Karekoda basılı tutup kaydedin," if artifact else "Karekodu kaydedin,"
    save_link = "" if artifact else f'\n    <a href="{kk}" download="ince-karekod.png">Karekodu kaydet</a>'
    vcf = "" if artifact else (f'<a class="btn ghost save" href="ince.vcf" download="İnce Oto Lastik.vcf">'
                               f'{S.svg(S.ICON["person"])}Rehbere kaydet</a>\n')
    og = (f'<meta property="og:url" content="{e(info.page)}">\n<meta property="og:image" content="{e(info.page)}og.png">'
          if info.page else "")
    favicon = ("data:image/svg+xml," + "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>"
               "<rect width='64' height='64' rx='14' fill='%230a0a0a'/>"
               "<path d='M16 14h9l13 18-13 18h-9l13-18z' fill='%23e3241b'/>"
               "<path d='M34 14h9l13 18-13 18h-9l13-18z' fill='%23f5f5f2'/></svg>")
    body = f"""<div class="wrap">
<header class="hero bleed">
  <div class="band" aria-hidden="true"><i></i></div>
  <p class="tag"><span class="live"></span>7/24 HİZMET</p>
  <h1 class="mark" aria-label="İnce"><span class="l">İ</span><span class="l">N</span><span class="l">C</span><span class="l">E</span></h1>
  <p class="sub"><span>OTO LASTİK</span></p>
  <p class="lead">Günün her saati hizmetinizdeyiz.</p>
</header>
<main>
<a class="call" href="tel:+{info.tel}"{tel}><span class="t"><small>HEMEN ARA</small><b>{e(info.phone)}</b></span>
  <span class="ib">{S.svg(S.ICON["phone"])}</span></a>
<nav class="tiles" aria-label="Bağlantılar">
  {tile(wa, S.svg(S.logo_path("whatsapp")), "WhatsApp", "<small>Mesaj gönderin</small>")}
  {tile(insta, S.svg(S.logo_path("instagram")), "Instagram", f"<small>@{e(info.instagram)}</small>")}
  {tile(info.google, S.svg(S.ICON["star"]), "Google", stars)}
</nav>
<section aria-labelledby="odeme">
  <h2 class="sec" id="odeme">ÖDEME BİLGİLERİ</h2>
  <div class="card">
    <div class="top"><span class="bank">{e(info.bank)}</span><span class="kind">IBAN</span></div>
    <div class="iban">{e(Q.iban_display(info.iban))}</div>
    <div class="who"><small>ALICI</small><b>{e(info.holder)}</b></div>
  </div>
  <div class="acts">
    <button class="btn copy" type="button" data-copy="{e(info.iban)}">{S.svg(S.ICON["copy"])}<span>Kopyala</span></button>
    <button class="btn ghost" type="button" id="kk-btn" aria-expanded="false" aria-controls="kk">{S.svg(S.ICON["qr"])}Karekod</button>
  </div>
  <div class="kk" id="kk" hidden>
    <span class="qr"><img src="{kk}" width="732" height="732" alt="{e(info.bank)} karekodu – {e(info.holder)}"></span>
    <p>{save} banka uygulamanızda <b>Karekod ile Öde</b>, ardından <b>Galeriden seç</b>.</p>{save_link}
  </div>
</section>
{vcf}</main>
<footer>
  <div class="strip bleed" aria-hidden="true"></div>
  <p><b>İNCE <span>OTO LASTİK</span></b><span>7/24 hizmet</span></p>
</footer>
</div>
<a class="fab" href="tel:+{info.tel}"{tel} aria-label="Hemen ara">{S.svg(S.ICON["phone"])}</a>
<div class="toast" role="status" aria-live="polite"></div>
<script>{JS}</script>
"""
    if artifact:
        return f"""<title>İnce Oto Lastik</title>
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
<meta name="theme-color" content="#0a0a0a">
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
body{{margin:0}} .hero{{width:1200px;height:630px;margin:0;padding:80px 90px 0}}
.band{{top:250px;height:260px}} .tag{{font-size:30px;gap:16px}} .live{{width:16px;height:16px}}
.mark{{font-size:330px;margin-top:26px}} .sub span{{font-size:70px}} .sub{{margin-top:22px}} .sub::after{{height:6px}}
</style><div class="hero"><div class="band"><i></i></div><p class="tag"><span class="live"></span>7/24 HİZMET</p>
<h1 class="mark"><span class="l">İ</span><span class="l">N</span><span class="l">C</span><span class="l">E</span></h1>
<p class="sub"><span>OTO LASTİK</span></p></div>"""
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
        assert pg.evaluate("document.fonts.check('italic 900 20px \"Saira Condensed\"')"), "yazı tipi yüklenmedi"
        assert pg.evaluate("document.documentElement.scrollWidth") <= 390, "yatay taşma"
        assert pg.evaluate("[...document.querySelectorAll('.iban,.call b,.tile b,.tile small,.mark')]"
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


def _gif(frames, durs, path):
    pal = [f.quantize(colors=160, method=Image.Quantize.MEDIANCUT) for f in frames]
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=durs, loop=0, optimize=True)
    return path


def _seek(pg, ms):
    pg.evaluate(f"document.getAnimations().forEach(a=>{{a.pause();a.currentTime={ms:.0f}}})")


def _finish(pg):
    pg.evaluate("document.getAnimations().forEach(a=>{try{a.finish()}catch(e){a.play()}})")


def animation_gif(path=GIF, seconds=2.4, step=0.06):
    """Açılış: tüm animasyonlar durdurulup zamanda adım adım ilerletilerek çekilir (kare kare aynı)."""
    from playwright.sync_api import sync_playwright
    frames = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        pg = b.new_page(viewport={"width": 390, "height": 700}, device_scale_factor=1)
        pg.goto("file://" + os.path.join(OUT, "index.html"))
        _seek(pg, 0)
        pg.wait_for_timeout(300)
        for k in range(int(seconds / step) + 1):
            _seek(pg, k * step * 1000)
            frames.append(Image.open(io.BytesIO(pg.screenshot())).convert("RGB"))
        b.close()
    durs = [int(step * 1000)] * len(frames)
    durs[-1] = 1800
    return _gif(frames, durs, path)


def tour_gif(path=TOUR):
    """Tam tur (390 × 844): açılış, aşağı kaydırma, IBAN'ı kopyala, karekod; dokunulan yer halkayla gösterilir."""
    from playwright.sync_api import sync_playwright
    frames, durs = [], []

    def shot(pg, ms=100, tap=None):
        im = Image.open(io.BytesIO(pg.screenshot())).convert("RGB")
        if tap:
            d = ImageDraw.Draw(im, "RGBA")
            d.ellipse((tap[0] - 22, tap[1] - 22, tap[0] + 22, tap[1] + 22), fill=(255, 255, 255, 70),
                      outline=(255, 255, 255, 230), width=3)
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
        for k in range(0, 2300, 80):
            _seek(pg, k)
            shot(pg, 80)
        _finish(pg)
        shot(pg, 900)
        h = pg.evaluate("document.documentElement.scrollHeight - innerHeight")
        for y in range(0, h + 1, 36):
            pg.evaluate(f"scrollTo(0,{y})")
            pg.wait_for_timeout(45)
            shot(pg, 60)
        pg.evaluate(f"scrollTo(0,{h})")
        for _ in range(8):                                   # kart görünür olunca üzerinden ışık geçer
            pg.wait_for_timeout(110)
            shot(pg, 110)
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
    if os.path.isdir(os.path.join(OUT, "fonts")):           # eski yazı tipleri zip'e girmesin
        for fn in os.listdir(os.path.join(OUT, "fonts")):
            os.remove(os.path.join(OUT, "fonts", fn))
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
    print("önizleme:", *(os.path.relpath(f(), A.ROOT) for f in (screenshot, animation_gif, tour_gif)))


if __name__ == "__main__":
    main()
