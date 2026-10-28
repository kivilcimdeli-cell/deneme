"""AUTO TUFAN – Hasar Onarım (Kepez, Antalya): isimlikteki QR ile açılan işletme sayfası. 4. sürüm.

1. sürüm (sakin, tek kart) beğenilmedi: "lastikçilere yaptığımız gibi, havalı olsun". 2. sürüm (çizgi araba) için:
"hizalamalar iyi değil, arabayı sil, boyama animasyonu ekle". 3. sürüm (boya tabancası, damlayan altın bant) için:
"mantık çok iyi ama daha profesyonel olsun, çocuk işi gibi kalmış". Bu sürüm aynı yapıda, kurumsal bir oto stüdyosu
diliyle:
  * Başlık, boya kabini: parlak siyah boyalı bir kaportada kabin ışıklarının yansıması (WebGL). Açılışta ışıklar
    birer birer, titreyerek yanar; yansımalar kaportanın kıvrımı ve bel çizgisi boyunca eğilir, yavaşça kayar;
    ışığa yakın metalik boya pulları parlar. Logodaki altın fırça T, fırça darbesiyle boyanır (önce üst kol, sonra
    gövde), üstünden bir parlama geçer; "Auto Tufan" (logodaki yazı tipi), HASAR ONARIM ve kısa açıklama gelir.
  * Ara ve WhatsApp başlıkta; bağlantılar (Instagram, Google yorumları, konum, web sitesi) tek listede. Hepsi aynı
    iskelette (simge, başlık ve alt satır, ok): simgeler ve yazılar sayfa boyunca aynı hizada (önizlemede denetlenir).
  * Ödeme bilgileri banka kartı gibi bir kartta: IBAN, Kopyala, Karekod (açılır: kaydedilir, banka uygulamasında
    galeriden okutulur). IBAN şimdilik örnek (`iban_ornek`). Kartvizit: Rehbere ekle, Paylaş (isimlikteki QR).
  * Tek yazı tipi (Poppins, logodaki), eğik ve kalın yazı yok; tek vurgu rengi (şampanya altını), ince çizgiler.
Bağlantılar aynı sekmede açılır (yeni sekme QR okuyucuların iç tarayıcılarında ve önizlemelerde çoğu zaman
açılmaz). Açılır kutular JavaScript'siz de açılır (#karekod, #paylas bağlantısı, CSS :target).
Kabin ışıklarının zamanı başlıktaki CSS saatinden okunur: T'nin boyanması ve ışıklar hep aynı anda; tur kaydında
animasyonlar durdurulup ilerletilince ışıklar da aynı kare. "Hareketi azalt" açıksa ya da WebGL yoksa aynı
görüntünün durgun hâli (boya.jpg, aynı çiziciyle üretilir) görünür, sayfa son hâliyle açılır.

Yayın: ortak Cloudflare hesabında (`qrsistem`) `deneme123` adlı Worker'a `autotufan_site.zip` yüklenir; adres
`https://deneme123.qrsistem.workers.dev` (isimlikteki QR bu adresi açar).

Çıktı : autotufan_isimlik/site/, autotufan_site.zip, sayfa_onizleme.png (ilk ekran, tüm sayfa), sayfa_tur.gif,
        sayfa_deneme.html (denemelik tek dosya: her şey içinde)

Kullanım:
  python3 scripts/autotufan_sayfa.py            # site, zip, önizleme ve tur
  python3 scripts/autotufan_sayfa.py --hizli    # GIF'siz
"""
import contextlib
import html
import io
import json
import os
import re
import shutil
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import autotufan_isimlik as AT  # noqa: E402
import autotufan_logo as L  # noqa: E402
import qr_sistemi as Q  # noqa: E402
from ince_sayfa import _seek  # noqa: E402

BASE = os.path.join(A.ROOT, "autotufan_isimlik")
OUT = os.path.join(BASE, "site")
ZIP = os.path.join(BASE, "autotufan_site.zip")
PREVIEW = os.path.join(BASE, "sayfa_onizleme.png")
TOUR = os.path.join(BASE, "sayfa_tur.gif")
STANDALONE = os.path.join(BASE, "sayfa_deneme.html")
CHROMIUM = "/opt/pw-browsers/chromium"
FONTS = {"p4": ("Poppins-Regular.ttf", 400), "p5": ("Poppins-Medium.ttf", 500), "p6": ("Poppins-SemiBold.ttf", 600)}
LICENSES = ("OFL-poppins.txt",)
VCF = "auto-tufan.vcf"
OG = "paylas.jpg"
ICON_PNG = "simge.png"
KAREKOD = "karekod.png"
POSTER = "boya.jpg"
LOGO = json.load(open(L.JSON, encoding="utf-8"))
GOLD = ((242, 214, 147), (217, 174, 92), (168, 122, 50))       # T'nin altını: üst, orta, alt
STILL = 7.0                                                     # durgun görüntünün (boya.jpg) zamanı, sn

ICON = {
    "phone": '<path d="M6.6 3.5h2.6l1.4 4.2-2 1.4a12 12 0 0 0 6.3 6.3l1.4-2 4.2 1.4v2.6a2 2 0 0 1-2.2 2A16.5 16.5 0 0 1 '
             '4.6 5.7a2 2 0 0 1 2-2.2z"/>',
    "whatsapp": '<path d="M4.5 19.5l1.2-4A8 8 0 1 1 9 18.6z"/><path fill="currentColor" stroke="none" '
                'd="M9.2 8.6c.2-.5.6-.6.9-.6.4 0 .6.6.9 1.4.2.5-.4.9-.6 1.2.6 1.2 1.6 2.2 2.9 2.8.3-.3.7-.9 1.2-.7.8.3 '
                '1.4.6 1.4 1 0 .3-.1.7-.6.9-.7.4-1.7.4-3-.2a8 8 0 0 1-3.4-3.3c-.5-1.1-.5-1.9.3-2.5z"/>',
    "instagram": '<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/>'
                 '<circle fill="currentColor" stroke="none" cx="17.2" cy="6.8" r="1.1"/>',
    "globe": '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.5 2.6 3.6 5.4 3.6 8.5s-1.1 5.9-3.6 8.5M12 '
             '3.5C9.5 6.1 8.4 8.9 8.4 12s1.1 5.9 3.6 8.5"/>',
    "pin": '<path d="M12 21s-6.5-6-6.5-11a6.5 6.5 0 0 1 13 0c0 5-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.4"/>',
    "star": '<path fill="currentColor" stroke="none" d="M12 3.8l2.5 5.2 5.6.7-4.1 3.9 1 5.6L12 16.5l-5 2.7 1-5.6-4.1-3.9 '
            '5.6-.7z"/>',
    "review": '<path d="M12 3.8l2.5 5.2 5.6.7-4.1 3.9 1 5.6L12 16.5l-5 2.7 1-5.6-4.1-3.9 5.6-.7z"/>',
    "save": '<circle cx="9" cy="8.5" r="3.5"/><path d="M3.5 19c.8-3.2 3-4.8 5.5-4.8 1.4 0 2.7.4 3.7 1.3M17.5 13v7M14 16.5h7"/>',
    "share": '<circle cx="17.5" cy="5.5" r="2.5"/><circle cx="6.5" cy="12" r="2.5"/><circle cx="17.5" cy="18.5" r="2.5"/>'
             '<path d="M8.7 10.8l6.6-4M8.7 13.2l6.6 4"/>',
    "qr": '<rect x="4" y="4" width="6" height="6" rx="1"/><rect x="14" y="4" width="6" height="6" rx="1"/>'
          '<rect x="4" y="14" width="6" height="6" rx="1"/><path d="M14 14h2.5v2.5M20 14v.5M14 20h.5M17.5 17.5H20V20"/>',
    "copy": '<rect x="8.5" y="8.5" width="11.5" height="11.5" rx="2.5"/><path d="M15.5 5.5A2 2 0 0 0 13.5 4H6a2 2 0 0 0-2 '
            '2v7.5a2 2 0 0 0 1.5 1.94"/>',
    "chev": '<path d="M9.5 6l6 6-6 6"/>',
    "down": '<path d="M12 4v12M6 11l6 6 6-6M5 20h14"/>',
}


def icon(k, width=1.6, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON[k]}</svg>')


def e(s):
    return html.escape(str(s))


def tr_title(s):
    """Türkçe baş harfler: HASAR ONARIM → Hasar Onarım (Python'un title()'ı I'yı i yapar)."""
    low = s.replace("I", "ı").replace("İ", "i").lower()
    return " ".join(w[:1].replace("i", "İ").replace("ı", "I").upper() + w[1:] for w in low.split())


def load():
    d = json.load(open(os.path.join(BASE, "bilgiler.json"), encoding="utf-8"))
    d["tel_e164"] = Q.phone_e164(d["telefon"])
    d["tel_txt"] = Q.phone_display(d["tel_e164"])
    d["qr"] = Q.https_url(d["sayfa_url"]).rstrip("/")             # isimlikteki QR ile aynı içerik
    d["insta"] = Q.instagram_handle(d["instagram"])
    raw = re.sub(r"\s", "", d["iban"]).upper()
    if d.get("iban_ornek"):
        print(f"Not: IBAN örnek ({d['iban']}); gerçeği bilgiler.json'a yazılıp iban_ornek kaldırılmalı.")
        d["iban_raw"] = raw
    else:
        d["iban_raw"] = Q.iban_normalize(raw)                    # mod-97 doğrulanır
    d["iban_txt"] = " ".join(d["iban_raw"][i:i + 4] for i in range(0, len(d["iban_raw"]), 4))
    if d.get("iban_karekod"):
        Q.karekod_check(d["iban_karekod"], None if d.get("iban_ornek") else d["iban_raw"])
    d["pay_qr"] = d.get("iban_karekod") or d["iban_raw"]
    d["web_txt"] = re.sub(r"^https?://(www\.)?", "", d["web"]).rstrip("/")
    d["wa"] = f"https://wa.me/{d['tel_e164']}?text=" + d["whatsapp_mesaj"].replace(" ", "%20").replace(",", "%2C")
    return d


# ---------------------------------------------------------------- kabin ışıkları (WebGL)

BOOTH_VS = "attribute vec2 p;varying vec2 v;void main(){v=vec2(p.x*.5+.5,.5-p.y*.5);gl_Position=vec4(p,0.,1.);}"
# Parlak siyah kaporta: üstte bel çizgisi (kıvrım: üstü yukarı bakar, yansımalar sıkışır), sağda kapı aralığı.
# Kabinin uzun ışıkları (biri altın) yüzeyin eğimine göre eğilerek yansır; ışıklar sırayla titreyip yanar, yansımalar
# zamanla kayar (kamera kaportanın yanında yürür gibi). Işığa yakın metalik pullar pırıldar. v.y = 0 üstte.
BOOTH_FS = """#ifdef GL_FRAGMENT_PRECISION_HIGH
precision highp float;
#else
precision mediump float;
#endif
uniform vec2 r;uniform float t;varying vec2 v;
float h(vec2 p){p=fract(p*vec2(123.34,456.21));p+=dot(p,p+45.32);return fract(p.x*p.y);}
float ign(float d,float k){if(d<0.)return 0.;if(d>.42)return 1.;return(.12+.88*step(.5,fract(d*8.+k*.37)))*smoothstep(0.,.03,d);}
void main(){float a=r.x/r.y;vec2 q=vec2((v.x-.5)*a,v.y);
float xg=.34+.10*(q.y-.5),sd=step(xg,q.x),yc=.27+.06*q.x+.004*sd,s=q.y-yc;
float ph=(s<0.?s*3.-s*s*4.:s+s*s*1.4)+.28*q.x*q.x+.015*sd,u=q.x*1.05-s*.35+t*.05;
vec4 T[6];vec3 S[6];vec3 C[6];vec3 W=vec3(1.,.975,.94);
T[0]=vec4(-.30,.050,.13,.10);S[0]=vec3(5.,4.2,.1);C[0]=W;
T[1]=vec4(-.135,.0055,1.3,.25);S[1]=vec3(2.9,1.7,.55);C[1]=vec3(1.,.80,.46);
T[2]=vec4(.06,.013,1.25,.40);S[2]=vec3(3.8,2.8,.35);C[2]=W;
T[3]=vec4(.22,.007,.75,.55);S[3]=vec3(2.6,1.3,.8);C[3]=W;
T[4]=vec4(.40,.012,.8,.70);S[4]=vec3(3.3,2.2,.15);C[4]=W;
T[5]=vec4(.70,.030,.45,.85);S[5]=vec3(4.4,3.2,.6);C[5]=W;
vec3 Lc=vec3(0.);float G=0.,N=0.;
for(int k=0;k<6;k++){float f=fract(u/S[k].x+S[k].z)*S[k].x,n=S[k].y;
float m=smoothstep(0.,.35,f)*smoothstep(n,n-.5,f),tp=.55+.45*sin(3.1416*clamp(f/n,0.,1.));
float d=(ph-T[k].x)/(T[k].y*tp),b=m*T[k].z*ign(t-T[k].w,float(k));
Lc+=C[k]*b*(exp(-d*d)+.09*exp(-abs(d)*.3));G+=b*exp(-abs(d)*.1);N+=b*exp(-abs(d)*.4);}
float on=ign(t-.40,9.),cr=exp(-pow(s/.0024,2.))*.45*on*(.3+.7*smoothstep(-.7,.9,sin(u*1.7+1.3)));
vec3 c=vec3(.010,.010,.012)+vec3(.030,.028,.026)*smoothstep(0.,-.15,s)*on+vec3(.012)*smoothstep(.35,.05,s)*on;
c+=Lc+W*cr;
vec2 g=gl_FragCoord.xy/2.,ce=floor(g);float hv=h(ce),pd=length(fract(g)-vec2(h(ce+3.1),h(ce+7.7)));
c+=vec3(1.,.8,.45)*step(.988,hv)*smoothstep(.55,0.,pd)*(.5+.5*sin(t*2.1+hv*91.))*min(N,1.5)*1.4;
float gp=exp(-pow((q.x-xg)/.0015,2.));c*=1.-.9*gp;c+=exp(-pow((q.x-xg-.003)/.0011,2.))*.3*min(G,1.);
c=1.-exp(-c*1.6);c*=.6+.4*smoothstep(.9,.1,abs(v.x-.5)*1.1+abs(v.y-.38)*.55);
gl_FragColor=vec4(c,1.);}"""


def render_booth(w, h, t=STILL, scale=1.0):
    """Kabin ışıklarını tarayıcıda (sayfadaki çiziciyle) w × h boyutunda, t anında çizer: durgun görüntü ve
    paylaşım görseli için. Döner: RGB görüntü (w·scale × h·scale)."""
    from playwright.sync_api import sync_playwright
    doc = ("<!doctype html><body style='margin:0;background:#000'><canvas style='display:block'></canvas><script>"
           "const cv=document.querySelector('canvas'),gl=cv.getContext('webgl',{alpha:false,preserveDrawingBuffer:true});"
           f"cv.style.width='{w}px';cv.style.height='{h}px';cv.width={round(w * scale)};cv.height={round(h * scale)};"
           "const sh=(k,s)=>{const x=gl.createShader(k);gl.shaderSource(x,s);gl.compileShader(x);"
           "if(!gl.getShaderParameter(x,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(x));return x};"
           f"const pr=gl.createProgram();gl.attachShader(pr,sh(gl.VERTEX_SHADER,`{BOOTH_VS}`));"
           f"gl.attachShader(pr,sh(gl.FRAGMENT_SHADER,`{BOOTH_FS}`));gl.linkProgram(pr);gl.useProgram(pr);"
           "gl.bindBuffer(gl.ARRAY_BUFFER,gl.createBuffer());"
           "gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW);"
           "const ap=gl.getAttribLocation(pr,'p');gl.enableVertexAttribArray(ap);gl.vertexAttribPointer(ap,2,gl.FLOAT,false,0,0);"
           "gl.viewport(0,0,cv.width,cv.height);gl.uniform2f(gl.getUniformLocation(pr,'r'),cv.width,cv.height);"
           f"gl.uniform1f(gl.getUniformLocation(pr,'t'),{t});gl.drawArrays(gl.TRIANGLE_STRIP,0,4);</script></body>")
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=scale)
        pg.on("pageerror", lambda x: errors.append(str(x)))
        pg.set_content(doc)
        im = Image.open(io.BytesIO(pg.locator("canvas").screenshot())).convert("RGB")
        b.close()
    assert not errors, errors
    return im


# ---------------------------------------------------------------- dosyalar

def _has_brotli():
    """woff2 için fontTools brotli ister; yoksa woff."""
    import importlib.util
    return importlib.util.find_spec("brotli") is not None


def subset_fonts(text):
    from fontTools import subset
    fdir = os.path.join(OUT, "fonts")
    os.makedirs(fdir, exist_ok=True)
    chars = text + "ABCÇDEFGĞHIİJKLMNOÖPQRSŞTUÜVWXYZabcçdefgğhıijklmnoöpqrsştuüvwxyz0123456789 .,:;·+-–—/@&()'\"!?→©"
    for key, (fn, _) in FONTS.items():
        opts = subset.Options()
        opts.flavor = "woff2" if _has_brotli() else "woff"
        opts.layout_features = ["kern", "liga", "locl", "tnum", "lnum"]
        f = subset.load_font(os.path.join(A.FONT_DIR, fn), opts)
        s = subset.Subsetter(opts)
        s.populate(text=chars)
        s.subset(f)
        subset.save_font(f, os.path.join(fdir, f"{key}.{opts.flavor}"), opts)
    for lic in LICENSES:
        shutil.copy(os.path.join(A.FONT_DIR, lic), os.path.join(fdir, lic))


def vcard(d):
    lines = ["BEGIN:VCARD", "VERSION:3.0", f"N:;{d['isim']};;;", f"FN:{d['isim']}", f"ORG:{d['isim']}",
             f"TITLE:{tr_title(d['hizmet'])}", f"TEL;TYPE=WORK,CELL,VOICE:+{d['tel_e164']}",
             f"ADR;TYPE=WORK:;;;{d['konum'].split(',')[0].strip()};{d['sehir'].title()};;Türkiye",
             f"URL:{d['web']}", f"URL:{d['sayfa_url']}",
             f"X-SOCIALPROFILE;TYPE=instagram:https://instagram.com/{d['insta']}", "END:VCARD"]
    with open(os.path.join(OUT, VCF), "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(lines) + "\n")


def karekod_png(d):
    """Ödeme karekodu PNG (kaydedilip banka uygulamasında galeriden okutulur)."""
    import segno
    segno.make(d["pay_qr"], error="m", micro=False).save(os.path.join(OUT, KAREKOD), scale=12, border=3)


def gold_t(h):
    """Fırça T, h piksel yüksekliğinde, yukarıdan aşağı altın degrade (RGBA)."""
    a = AT.t_raster(h, (0, 0, 0)).getchannel("A")
    y = np.linspace(0, 1, h)[:, None, None]
    top, mid, low = (np.array(c, float) for c in GOLD)
    col = np.where(y < .5, top + (mid - top) * y / .5, mid + (low - mid) * (y - .5) / .5)
    im = Image.fromarray(np.repeat(col, a.width, 1).astype(np.uint8), "RGB").convert("RGBA")
    im.putalpha(a)
    return im


def poster():
    """Durgun görüntü (hareketi azalt açıkken ya da WebGL yoksa başlığın arkası): kabin ışıkları, son hâli."""
    render_booth(440, 640, STILL, 1.5).save(os.path.join(OUT, POSTER), "JPEG", quality=80, optimize=True,
                                            progressive=True)


def og_image(d):
    """Bağlantı paylaşılınca görünen görsel (1200 × 630): kabin ışıkları, altın T, Auto Tufan, HASAR ONARIM."""
    W, H = 1200, 630
    im = render_booth(W, H, STILL).convert("RGBA")
    shade = np.zeros((H, W, 4), np.uint8)
    shade[..., :3] = (10, 10, 11)
    x = np.linspace(0, 1, W)[None, :]
    yy = np.linspace(0, 1, H)[:, None]
    shade[..., 3] = (255 * np.clip(.92 - .9 * np.clip((x - .38) / .5, 0, 1) + .35 * (yy - .5), 0, .94)).astype(np.uint8)
    im = Image.alpha_composite(im, Image.fromarray(shade, "RGBA"))
    T = gold_t(118)
    im.paste(T, (84, 92), T)
    dr = ImageDraw.Draw(im)
    f = lambda fn, n: ImageFont.truetype(os.path.join(A.FONT_DIR, fn), n)  # noqa: E731
    dr.text((80, 236), d["isim"], font=f("Poppins-SemiBold.ttf", 104), fill=(244, 242, 237))
    gold, x0 = GOLD[0], 86
    dr.line([(x0, 412), (x0 + 44, 412)], fill=GOLD[1], width=2)
    x0 += 64
    font = f("Poppins-Medium.ttf", 28)
    for ch in AT.SERVICE:                                          # harf aralıklı (0,42 em)
        dr.text((x0, 394), ch, font=font, fill=gold)
        x0 += font.getlength(ch) + 0.42 * 28
    dr.text((86, 476), f"{d['konum']}  ·  {d['tel_txt']}", font=f("Poppins-Regular.ttf", 30), fill=(176, 172, 164))
    im.convert("RGB").save(os.path.join(OUT, OG), "JPEG", quality=86, optimize=True)


def touch_icon():
    """Ana ekran / sekme simgesi (180 × 180): koyu zeminde altın fırça T."""
    y = np.linspace(0, 1, 180)[:, None, None]
    bg = np.array((28, 28, 31), float) + (np.array((10, 10, 11), float) - (28, 28, 31)) * y
    im = Image.fromarray(np.repeat(bg, 180, 1).astype(np.uint8), "RGB").convert("RGBA")
    T = gold_t(68)
    im.paste(T, ((180 - T.width) // 2, (180 - T.height) // 2 + 2), T)
    im.convert("RGB").save(os.path.join(OUT, ICON_PNG), optimize=True)


# ---------------------------------------------------------------- çizimler

# Fırça T'nin iki darbesinin orta çizgisi (logo koordinatı, 1694 × 1000, y aşağı): önce üst kol (soldaki kıvrımdan
# sağ uca), sonra gövde (üstten aşağı, en altta sağa kıvrılan uç). Maske bu çizgileri kalın fırçayla çizer; ikisi
# birlikte T'nin tamamını örter (önizlemede denetlenir).
STROKES = (
    (150, [(150, 478), (85, 450), (55, 400), (60, 340), (100, 290), (160, 250), (221, 215), (300, 170), (400, 134),
           (500, 106), (600, 85), (700, 70), (800, 57), (900, 47), (1000, 40), (1100, 37), (1200, 37), (1300, 42),
           (1400, 50), (1500, 64), (1600, 89), (1650, 115), (1672, 160)]),
    (175, [(1150, 50), (1105, 80), (1069, 100), (987, 200), (877, 300), (780, 400), (687, 500), (605, 600), (531, 700),
           (469, 800), (435, 880), (432, 950), (462, 978), (530, 905), (600, 830), (668, 772)]))


def _smooth(pts):
    """Noktalardan geçen yumuşak SVG yolu (Catmull-Rom → kübik Bézier)."""
    p = [pts[0]] + list(pts) + [pts[-1]]
    d = f"M{p[1][0]} {p[1][1]}"
    for i in range(1, len(p) - 2):
        c1 = (p[i][0] + (p[i + 1][0] - p[i - 1][0]) / 6, p[i][1] + (p[i + 1][1] - p[i - 1][1]) / 6)
        c2 = (p[i + 1][0] - (p[i + 2][0] - p[i][0]) / 6, p[i + 1][1] - (p[i + 2][1] - p[i][1]) / 6)
        d += f"C{c1[0]:.0f} {c1[1]:.0f} {c2[0]:.0f} {c2[1]:.0f} {p[i + 1][0]} {p[i + 1][1]}"
    return d


def _grad(gid):
    return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
            + "".join(f'<stop offset="{o}" stop-color="#{c[0]:02X}{c[1]:02X}{c[2]:02X}"/>'
                      for o, c in zip((0, .5, 1), GOLD)) + "</linearGradient>")


def t_svg(cls):
    """Fırça T (altın degrade), durgun: altbilgi ve ödeme kartı için."""
    w, h = LOGO["svg_boyut"]
    return (f'<svg class="{cls}" viewBox="0 0 {w:.0f} {h:.0f}" aria-hidden="true"><defs>{_grad("g" + cls)}</defs>'
            f'<path d="{LOGO["d"]}" fill="url(#g{cls})"/></svg>')


def t_paint():
    """Başlıktaki fırça T: maskedeki iki fırça darbesi sırayla çizilir (T boyanır), sonra üstünden parlama geçer."""
    w, h = LOGO["svg_boyut"]
    strokes = "".join(f'<path class="br br{k}" pathLength="1" d="{_smooth(pts)}" fill="none" stroke="#fff" '
                      f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
                      for k, (sw, pts) in enumerate(STROKES, 1))
    return (f'<svg class="tlogo" viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="Auto Tufan logosu"><defs>'
            f'{_grad("gt")}<linearGradient id="gl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" '
            f'stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".8"/><stop offset="1" '
            f'stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="tm" maskUnits="userSpaceOnUse" x="-120" y="-120" width="{w + 240:.0f}" height="{h + 240:.0f}">'
            f'{strokes}</mask><clipPath id="tc"><path d="{LOGO["d"]}"/></clipPath></defs>'
            f'<g mask="url(#tm)"><path d="{LOGO["d"]}" fill="url(#gt)"/><g clip-path="url(#tc)">'
            f'<g transform="skewX(-22)"><rect class="glint" x="-560" y="-80" width="420" height="1160" '
            f'fill="url(#gl)"/></g></g></g></svg>')


def stars(n=5):
    return '<span class="stars">' + "".join(icon("star", 0) for _ in range(n)) + "</span>"


def qr_svg(content, label):
    import segno
    q = segno.make(content, error="m", micro=False, boost_error=True)
    m = [[bool(v) for v in row] for row in q.matrix]
    n, qz = len(m), 2
    rects = "".join(f'<rect x="{x + qz}" y="{y + qz}" width="1" height="1"/>'
                    for y, row in enumerate(m) for x, v in enumerate(row) if v)
    s = n + 2 * qz
    return (f'<svg viewBox="0 0 {s} {s}" shape-rendering="crispEdges" role="img" aria-label="{e(label)}">'
            f'<rect width="{s}" height="{s}" fill="#fff"/><g fill="#111">{rects}</g></svg>')


# ---------------------------------------------------------------- sayfa

CSS = """
FONTFACES
:root{--bg:#0A0A0B;--s1:#111113;--line:rgba(255,255,255,.075);--line2:rgba(255,255,255,.13);--ink:#F4F2ED;
  --mut:#9D9990;--dim:#64615B;--au:#D9B66C;--au2:#F0D69C;--dark:#15120C;--wa:#36C47C;--g:20px;
  --gold:linear-gradient(180deg,#EACB86,#CDA35A);--e:cubic-bezier(.2,.7,.2,1);color-scheme:dark}
*{box-sizing:border-box;margin:0;padding:0}
html{background:#050506}
body{font-family:Poppins,system-ui,sans-serif;color:var(--ink);background:var(--bg);-webkit-font-smoothing:antialiased;
  -webkit-tap-highlight-color:transparent}
a{color:inherit;text-decoration:none}
button{font:inherit;color:inherit;background:none;border:0;cursor:pointer}
.wrap{position:relative;max-width:440px;margin:0 auto;min-height:100vh;background:var(--bg);overflow:hidden}
@media (min-width:480px){.wrap{box-shadow:0 0 0 1px var(--line),0 40px 120px rgba(0,0,0,.7)}}

/* ---------------- başlık: boya kabini (kaportada kabin ışıklarının yansıması), fırça T, Auto Tufan */
.hero{position:relative;padding:clamp(150px,25vh,220px) var(--g) 4px;text-align:center}
.booth{position:absolute;left:0;right:0;top:0;height:min(80%,640px);z-index:0;background:#0A0A0B}
.booth canvas{position:absolute;inset:0;width:100%;height:100%;display:block;opacity:0}
.booth canvas.on{opacity:1}
html:not(.mo) .booth,.nogl .booth{background:#0A0A0B url(POSTER) 50% 0/cover no-repeat}
.nogl .booth canvas{display:none}
.booth:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,10,11,0) 28%,
  rgba(10,10,11,.6) 56%,var(--bg) 100%)}
.hero>:not(.booth){position:relative;z-index:1}
.tlogo{display:block;width:120px;height:auto;margin:0 auto;overflow:visible;
  filter:drop-shadow(0 8px 26px rgba(217,182,108,.22))}
.word{margin-top:18px;font-weight:600;font-size:clamp(36px,10.6vw,44px);line-height:1.1;letter-spacing:-.012em;
  white-space:nowrap}
.svc{display:flex;align-items:center;justify-content:center;gap:14px;margin-top:12px;font-weight:500;font-size:11.5px;
  letter-spacing:.42em;color:var(--au2);white-space:nowrap}
.svc span{margin-right:-.42em}
.svc i{width:26px;height:1px;background:var(--au)}
.svc i:first-child{transform-origin:right}.svc i:last-child{transform-origin:left}
.tag{max-width:300px;margin:14px auto 0;font-size:14px;line-height:1.6;color:var(--mut)}
.cta{display:grid;gap:10px;margin-top:28px}

/* ---------------- satır: simge, başlık ve alt satır, ok. Ara, WhatsApp ve bağlantılar aynı iskelette: simgeler ve
   yazılar sayfa boyunca aynı hizada */
.act{position:relative;display:grid;grid-template-columns:40px minmax(0,1fr) 18px;align-items:center;column-gap:14px;
  min-height:68px;padding:12px 16px 12px 12px;border:1px solid transparent;border-radius:16px;text-align:left;
  transition:transform .2s var(--e),background-color .2s}
.act .ic{width:40px;height:40px;border-radius:50%;display:grid;place-items:center}
.act .ic svg{width:20px;height:20px}
.act .tx{min-width:0}
.act b,.act small{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.act b{font-weight:500;font-size:15px;line-height:1.35}
.act small{margin-top:1px;font-size:12.5px;line-height:1.35;color:var(--mut)}
.act .go{width:18px;height:18px;color:var(--dim)}
.act:active{transform:scale(.985)}
.call{background:var(--gold);color:var(--dark);box-shadow:inset 0 1px 0 rgba(255,255,255,.4),0 14px 34px rgba(217,182,108,.15)}
.call .ic{background:var(--dark);color:var(--au2)}
.call small{margin:0 0 1px;font-weight:500;font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
  color:rgba(21,18,12,.62)}
.call b{font-weight:600;font-size:19px;letter-spacing:.01em;font-variant-numeric:tabular-nums}
.call .go{color:var(--dark)}
.wa{background:rgba(255,255,255,.035);border-color:var(--line2);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px)}
.wa .ic{background:rgba(54,196,124,.12);color:var(--wa)}

/* ---------------- bölümler */
.sl{display:flex;align-items:center;gap:12px;margin:44px var(--g) 14px;font-weight:500;font-size:11px;letter-spacing:.22em;
  text-transform:uppercase;color:var(--mut);white-space:nowrap}
.sl em{font-style:normal;letter-spacing:.06em;color:var(--au)}
.sl:after{content:"";flex:1;height:1px;background:var(--line)}
.list{margin:0 var(--g);border:1px solid var(--line);border-radius:18px;background:var(--s1);overflow:hidden}
.list .act{border:0;border-radius:0}
.list .act+.act:before{content:"";position:absolute;left:66px;right:0;top:0;height:1px;background:var(--line)}
.list .ic{background:rgba(217,182,108,.07);box-shadow:inset 0 0 0 1px rgba(217,182,108,.22);color:var(--au)}
.list .act:active{transform:none;background:rgba(255,255,255,.03)}
.stars{display:inline-flex;gap:1px;margin-right:6px;vertical-align:-1px}
.stars svg{width:11px;height:11px;color:var(--au)}

/* ---------------- ödeme: banka kartı gibi */
.card{position:relative;margin:0 var(--g);padding:20px 18px 18px;border-radius:20px;overflow:hidden;
  background:radial-gradient(140% 100% at 0 0,rgba(217,182,108,.11),transparent 50%),linear-gradient(155deg,#1B1B1E,#0F0F11 70%);
  border:1px solid var(--line2);box-shadow:0 20px 50px rgba(0,0,0,.35)}
.card:before{content:"";position:absolute;inset:0;background:linear-gradient(115deg,transparent 35%,rgba(255,255,255,.05) 48%,
  transparent 60%);pointer-events:none}
.card>*{position:relative}
.card .hd{display:flex;align-items:center;justify-content:space-between}
.card .lab{font-weight:500;font-size:10.5px;letter-spacing:.24em;color:var(--mut)}
.card .tm{width:34px;height:auto}
.card .num{margin-top:12px;font-weight:500;font-size:clamp(14px,4.15vw,16.5px);letter-spacing:.05em;white-space:nowrap;
  font-variant-numeric:tabular-nums;-webkit-user-select:all;user-select:all}
.card .who{margin-top:6px;font-size:12.5px;color:var(--mut)}
.card .who b{color:var(--ink);font-weight:500}
.btns{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:10px;margin-top:18px}
.btn{display:flex;align-items:center;justify-content:center;gap:8px;height:48px;border-radius:12px;font-weight:500;
  font-size:14px;white-space:nowrap}
.btn svg{width:18px;height:18px;flex:none}
.btn.pri{background:var(--gold);color:var(--dark);box-shadow:inset 0 1px 0 rgba(255,255,255,.4)}
.btn.sec{background:rgba(255,255,255,.035);border:1px solid var(--line2)}
.btn.open{border-color:rgba(217,182,108,.55);color:var(--au2)}
/* açılır kutular: JavaScript .on ile açar; JavaScript yoksa bağlantı (#karekod, #paylas) :target ile */
.drop{display:none;grid-column:1/-1}
.drop:target,.drop.on{display:block}
.qrbox{padding:18px 16px;border-radius:14px;background:#0B0B0D;border:1px solid var(--line);text-align:center}
.qrbox>img,.qrbox>svg{display:block;width:180px;height:auto;margin:0 auto;border-radius:10px;background:#fff;padding:8px}
.qrbox p{margin-top:12px;font-size:12.5px;line-height:1.55;color:var(--mut)}
.qrbox p b{color:var(--ink);font-weight:500}
.qrbox a.dl{display:inline-flex;align-items:center;gap:6px;margin-top:10px;font-weight:500;font-size:13px;color:var(--au2)}
.qrbox a.dl svg{width:16px;height:16px}
.qrbox .btns{margin-top:14px}
.note{margin-top:12px;font-size:11px;color:var(--dim);text-align:center}

/* ---------------- kartvizit, altbilgi */
.duo{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:10px;margin:0 var(--g)}
.duo>.btn{height:52px}
footer{margin:52px var(--g) 0;padding:30px 0 calc(36px + env(safe-area-inset-bottom));border-top:1px solid var(--line);
  display:flex;flex-direction:column;align-items:center;gap:3px;text-align:center}
footer svg{width:46px;height:auto;margin-bottom:10px}
footer p{font-weight:600;font-size:16px}
footer small{font-size:12.5px;color:var(--mut)}
footer .c{margin-top:10px;font-size:11px;color:var(--dim)}
.fab{position:fixed;right:max(18px,calc(50vw - 202px));bottom:calc(18px + env(safe-area-inset-bottom));z-index:9;
  width:56px;height:56px;border-radius:50%;display:grid;place-items:center;color:var(--dark);background:var(--gold);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.4),0 10px 30px rgba(0,0,0,.5);transform:scale(0);transition:transform .35s var(--e)}
.fab.on{transform:none}
.fab svg{width:24px;height:24px}
.toast{position:fixed;left:50%;bottom:calc(92px + env(safe-area-inset-bottom));z-index:20;transform:translate(-50%,20px);
  opacity:0;visibility:hidden;padding:12px 18px;border-radius:12px;background:#18181B;border:1px solid var(--line2);
  font-size:13px;white-space:nowrap;box-shadow:0 12px 30px rgba(0,0,0,.5);transition:all .3s var(--e)}
.toast.on{opacity:1;visibility:visible;transform:translate(-50%,0)}

/* ---------------- açılış: ışıklar yanar (WebGL, saat .booth'ta), T boyanır ve parlar, yazılar ve düğmeler gelir */
.mo .booth{animation:clock 86400s linear both}
.br{stroke-dasharray:1 2;stroke-dashoffset:0}
.br1{animation:brush .7s cubic-bezier(.5,.05,.3,1) .45s both}
.br2{animation:brush .55s cubic-bezier(.5,.05,.3,1) 1.05s both}
.glint{animation:glint 1.1s cubic-bezier(.4,0,.2,1) 1.55s both}
.word{animation:word 1s var(--e) 1.2s both}
.svc i{animation:grow .8s var(--e) 1.5s both}
.svc span{animation:fade .8s ease-out 1.55s both}
.tag{animation:up .8s var(--e) 1.7s both}
.cta>*{animation:up .8s var(--e) calc(1.85s + var(--i)*.1s) both}
.mo .rv{opacity:0;transform:translateY(18px);transition:opacity .8s var(--e),transform .8s var(--e)}
.mo .rv.in{opacity:1;transform:none}
@keyframes clock{to{outline-color:transparent}}
@keyframes brush{from{stroke-dashoffset:1.02}to{stroke-dashoffset:0}}
@keyframes glint{from{transform:translateX(0)}to{transform:translateX(2600px)}}
@keyframes word{from{opacity:0;letter-spacing:.2em;filter:blur(6px)}to{opacity:1;letter-spacing:-.012em;filter:blur(0)}}
@keyframes grow{from{transform:scaleX(0)}to{transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes up{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}
  .mo .rv{opacity:1;transform:none}}
"""

JS = """
(()=>{const R=document.documentElement,mo=R.classList.contains('mo');
if(document.hidden){const as=document.getAnimations();as.forEach(a=>a.pause());
  addEventListener('visibilitychange',()=>{if(!document.hidden)as.forEach(a=>a.play())},{once:true})}
const toast=document.querySelector('.toast');let tt=0;
const say=s=>{toast.textContent=s;toast.classList.add('on');clearTimeout(tt);tt=setTimeout(()=>toast.classList.remove('on'),2200)};
const copy=async s=>{try{await navigator.clipboard.writeText(s);return true}catch(x){}const t=document.createElement('textarea');
  t.value=s;t.setAttribute('readonly','');t.style.cssText='position:fixed;opacity:0';document.body.appendChild(t);t.select();
  let ok=false;try{ok=document.execCommand('copy')}catch(y){}t.remove();return ok};
document.querySelectorAll('[data-copy]').forEach(b=>b.addEventListener('click',async ev=>{ev.preventDefault();
  if(await copy(b.dataset.copy))say(b.dataset.msg);else say('Kopyalanamadı: yazıya basılı tutun')}));
document.querySelectorAll('[data-toggle]').forEach(a=>a.addEventListener('click',ev=>{ev.preventDefault();
  const el=document.getElementById(a.dataset.toggle),on=el.classList.toggle('on');a.classList.toggle('open',on);
  if(on)el.scrollIntoView({block:'nearest',behavior:mo?'smooth':'auto'})}));
const sh=document.getElementById('send');if(sh&&!navigator.share)sh.hidden=true;
if(sh)sh.onclick=async()=>{try{await navigator.share({title:document.title,url:sh.dataset.url})}catch(x){}};
const fab=document.querySelector('.fab'),call=document.querySelector('.call');
if('IntersectionObserver' in window){new IntersectionObserver(([x])=>fab.classList.toggle('on',!x.isIntersecting&&
  x.boundingClientRect.top<0)).observe(call);
  const rv=[...document.querySelectorAll('.rv')];
  if(mo){const io=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting){x.target.classList.add('in');
    io.unobserve(x.target)}}),{threshold:.15});
    rv.forEach(el=>{if(el.getBoundingClientRect().top<innerHeight)el.style.transitionDelay='2.1s';io.observe(el)})}
  else rv.forEach(el=>el.classList.add('in'))}
else document.querySelectorAll('.rv').forEach(el=>el.classList.add('in'));
if(!mo)return;
const bo=document.querySelector('.booth'),cv=bo.querySelector('canvas');
try{const gl=cv.getContext('webgl',{alpha:false,antialias:false,depth:false,powerPreference:'low-power'});if(!gl)throw 0;
  const mk=(k,s)=>{const x=gl.createShader(k);gl.shaderSource(x,s);gl.compileShader(x);
    if(!gl.getShaderParameter(x,gl.COMPILE_STATUS))throw 0;return x};
  const pr=gl.createProgram();gl.attachShader(pr,mk(gl.VERTEX_SHADER,`__VS__`));gl.attachShader(pr,mk(gl.FRAGMENT_SHADER,`__FS__`));
  gl.linkProgram(pr);if(!gl.getProgramParameter(pr,gl.LINK_STATUS))throw 0;gl.useProgram(pr);
  gl.bindBuffer(gl.ARRAY_BUFFER,gl.createBuffer());
  gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW);
  const ap=gl.getAttribLocation(pr,'p');gl.enableVertexAttribArray(ap);gl.vertexAttribPointer(ap,2,gl.FLOAT,false,0,0);
  const ur=gl.getUniformLocation(pr,'r'),ut=gl.getUniformLocation(pr,'t'),clk=bo.getAnimations()[0];
  const now=()=>clk&&clk.currentTime!=null?clk.currentTime/1000:performance.now()/1000;
  const draw=t=>{const k=Math.min(devicePixelRatio||1,1.75),w=Math.round(cv.clientWidth*k),h=Math.round(cv.clientHeight*k);
    if(cv.width!==w||cv.height!==h){cv.width=w;cv.height=h;gl.viewport(0,0,w,h)}
    gl.uniform2f(ur,w,h);gl.uniform1f(ut,t);gl.drawArrays(gl.TRIANGLE_STRIP,0,4)};
  let raf=0,vis=true;const go=()=>{if(!raf&&vis&&!document.hidden)raf=requestAnimationFrame(loop)},
    loop=()=>{raf=0;draw(now());go()};
  if('IntersectionObserver' in window)new IntersectionObserver(([x])=>{vis=x.isIntersecting;go()}).observe(bo);
  addEventListener('visibilitychange',go);
  cv.addEventListener('webglcontextlost',ev=>{ev.preventDefault();R.classList.add('nogl')});
  window.__boothDraw=()=>draw(now());draw(now());cv.classList.add('on');go()}
catch(x){R.classList.add('nogl')}})();
"""


def row(cls, href, ic, title, sub, extra="", sub_first=False):
    """Satır: simge, başlık ve alt satır, ok (ara, WhatsApp ve bağlantılar aynı iskelette)."""
    s = f"<small>{sub}</small>"
    t = f"<b>{e(title)}</b>"
    return (f'<a class="act {cls}" href="{e(href)}"{extra}><span class="ic">{icon(ic, 1.7)}</span>'
            f'<span class="tx">{s + t if sub_first else t + s}</span>{icon("chev", 1.8, "go")}</a>')


def page(d):
    ext_, fmt = ("woff2", "woff2") if _has_brotli() else ("woff", "woff")
    faces = "".join(f'@font-face{{font-family:Poppins;src:url(fonts/{k}.{ext_}) format("{fmt}");font-weight:{w};'
                    f'font-display:swap}}' for k, (_, w) in FONTS.items())
    css = CSS.replace("FONTFACES", faces).replace("POSTER", POSTER)
    js = JS.replace("__VS__", BOOTH_VS).replace("__FS__", BOOTH_FS)
    tel = f"tel:+{d['tel_e164']}"
    cta = (row("call", tel, "phone", d["tel_txt"], "Hemen arayın", ' style="--i:0"', sub_first=True)
           + row("wa", d["wa"], "whatsapp", "WhatsApp", "Mesaj gönderin", ' style="--i:1"'))
    links = (row("", f"https://instagram.com/{d['insta']}", "instagram", "Instagram", f"@{e(d['insta'])}")
             + row("", d["google"], "review", "Google yorumları", f"{stars()}Yorum yazın, puan verin")
             + row("", d["harita"], "pin", "Konum", f"{e(d['konum'].replace(', ', ' / '))} · Yol tarifi")
             + row("", d["web"], "globe", "Web sitesi", e(d["web_txt"])))
    holder = (f'<p class="who">Alıcı <b>{e(d["iban_alici"])}</b></p>' if d.get("iban_alici") else "")
    note = '<p class="note">Örnek IBAN: gerçek bilgiler eklenecek.</p>' if d.get("iban_ornek") else ""
    url = d["qr"]
    body = (
        f'<div class="wrap"><header class="hero"><div class="booth" aria-hidden="true"><canvas></canvas></div>'
        f'{t_paint()}<h1 class="word">{e(d["isim"])}</h1>'
        f'<p class="svc"><i></i><span>{e(AT.SERVICE)}</span><i></i></p>'
        f'<p class="tag">Aracınızdaki hasarı titizlikle onarıyor, ilk günkü görünümüne kavuşturuyoruz.</p>'
        f'<nav class="cta" aria-label="Hemen ulaşın">{cta}</nav></header>'
        f'<h2 class="sl rv"><em>01</em>Bağlantılar</h2><nav class="list rv" aria-label="Bağlantılar">{links}</nav>'
        f'<h2 class="sl rv"><em>02</em>Ödeme bilgileri</h2>'
        f'<section class="card rv"><div class="hd"><span class="lab">IBAN</span>{t_svg("tm")}</div>'
        f'<p class="num" id="iban">{e(d["iban_txt"])}</p>{holder}'
        f'<div class="btns"><a class="btn pri" href="#iban" data-copy="{e(d["iban_raw"])}" data-msg="IBAN kopyalandı – '
        f'banka uygulamanıza yapıştırın">{icon("copy", 1.7)}Kopyala</a>'
        f'<a class="btn sec" href="#karekod" data-toggle="karekod">{icon("qr", 1.7)}Karekod</a>'
        f'<div class="qrbox drop" id="karekod"><img src="{KAREKOD}" alt="IBAN karekodu" width="180" height="180">'
        f'<p>Karekodu kaydedin, banka uygulamanızda <b>Karekod ile Öde</b>, ardından <b>Galeriden seç</b>.</p>'
        f'<a class="dl" href="{KAREKOD}" download="auto-tufan-karekod.png">{icon("down", 1.7)}Karekodu kaydet</a>'
        f'</div></div>{note}</section>'
        f'<h2 class="sl rv"><em>03</em>Kartvizit</h2>'
        f'<div class="duo rv"><a class="btn sec" href="{VCF}" download>{icon("save", 1.7)}Rehbere ekle</a>'
        f'<a class="btn sec" href="#paylas" data-toggle="paylas">{icon("share", 1.7)}Paylaş</a>'
        f'<div class="qrbox drop" id="paylas">{qr_svg(url, "Kartvizit QR kodu")}<p>Kodu kamerayla okutun ya da bağlantıyı '
        f'gönderin.<br><b>{e(url.replace("https://", ""))}</b></p><div class="btns"><a class="btn sec" href="{e(url)}" '
        f'data-copy="{e(url)}" data-msg="Bağlantı kopyalandı">{icon("copy", 1.7)}Kopyala</a>'
        f'<button class="btn pri" id="send" type="button" data-url="{e(url)}">{icon("share", 1.7)}Gönder</button>'
        f'</div></div></div>'
        f'<footer class="rv">{t_svg("ft")}<p>{e(d["isim"])}</p><small>{e(tr_title(AT.SERVICE))} · '
        f'{e(d["konum"])}</small><span class="c">© 2026 {e(d["isim"])}</span></footer></div>'
        f'<a class="fab" href="{tel}" aria-label="Hemen ara">{icon("phone", 1.9)}</a>'
        f'<div class="toast" role="status" aria-live="polite"></div>')
    title = f"{d['isim']} · {tr_title(AT.SERVICE)} · {d['konum']}"
    desc = f"{d['isim']} – hasar onarım, {d['konum']}. Hemen arayın, WhatsApp'tan yazın, Instagram, konum, ödeme."
    og = d["sayfa_url"].rstrip("/") + "/" + OG
    return (f'<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" '
            f'content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#0A0A0B">'
            f'<title>{e(title)}</title><meta name="description" content="{e(desc)}">'
            f'<meta property="og:type" content="website"><meta property="og:title" content="{e(title)}">'
            f'<meta property="og:description" content="{e(desc)}"><meta property="og:image" content="{e(og)}">'
            f'<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
            f'<meta name="twitter:card" content="summary_large_image">'
            f'<link rel="icon" href="{ICON_PNG}"><link rel="apple-touch-icon" href="{ICON_PNG}">'
            f'<link rel="preload" as="font" type="font/{fmt}" href="fonts/p6.{ext_}" crossorigin>'
            f'<link rel="preload" as="font" type="font/{fmt}" href="fonts/p5.{ext_}" crossorigin>'
            f"<script>matchMedia('(prefers-reduced-motion: reduce)').matches||"
            f"document.documentElement.classList.add('mo')</script>"
            f'<style>{css}</style></head><body>{body}<script>{js}</script></body></html>')


# ---------------------------------------------------------------- önizlemeler

@contextlib.contextmanager
def served():
    """site/ yerel sunucuda (telefondaki gibi http)."""
    import functools
    import http.server
    import threading

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=OUT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{srv.server_port}/index.html"
    finally:
        srv.shutdown()


def strokes_cover():
    """Maskedeki iki fırça darbesi T'nin tamamını örtüyor mu (boyama bitince T eksiksiz görünmeli)."""
    s = 0.5
    W, H = (round(v * s) + 2 for v in LOGO["svg_boyut"])
    t = Image.new("1", (W, H), 0)
    ImageDraw.Draw(t).polygon([(x * 1000 * s, (1 - y) * 1000 * s) for x, y in LOGO["t"][0]], fill=1)
    m = Image.new("1", (W, H), 0)
    dr = ImageDraw.Draw(m)
    for sw, pts in STROKES:                       # kırık çizgi, yumuşak yoldan biraz içte kalır: güvenli taraf
        p = [(x * s, y * s) for x, y in pts]
        dr.line(p, fill=1, width=round(sw * s), joint="curve")
        for x, y in (p[0], p[-1]):
            dr.ellipse([x - sw * s / 2, y - sw * s / 2, x + sw * s / 2, y + sw * s / 2], fill=1)
    return int((np.asarray(t) & ~np.asarray(m)).sum())


def screenshot(d, path=PREVIEW):
    """Telefon ekranında (390 × 844, son hâli): ilk ekran ve tüm sayfa (karekod ve paylaş kutuları açık).
    Kontroller: yazı tipleri yüklü, yatay taşma yok, yazılar sığıyor, satırların simgeleri ve yazıları aynı hizada,
    durgun görüntü yüklü, iki QR okunuyor, sayfa hatası yok."""
    from playwright.sync_api import sync_playwright
    errors, shots = [], []
    fits = "[...document.querySelectorAll('SEL')].every(e=>e.offsetParent===null||e.scrollWidth<=e.clientWidth+1)"
    with sync_playwright() as p, served() as url:
        b = p.chromium.launch(executable_path=CHROMIUM)
        for full in (False, True):
            pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, reduced_motion="reduce")
            pg.add_init_script("navigator.share=async()=>{}")
            pg.on("pageerror", lambda x: errors.append(str(x)))
            pg.goto(url)
            pg.wait_for_timeout(600)
            pg.evaluate("Promise.all(['400','500','600'].map(w=>document.fonts.load(w+' 20px Poppins')))")
            assert pg.evaluate("['400','500','600'].every(w=>document.fonts.check(w+' 20px Poppins'))"), \
                "yazı tipi yüklenmedi"
            assert pg.evaluate("document.documentElement.scrollWidth") <= 390, "yatay taşma"
            assert pg.evaluate(fits.replace("SEL", ".word,.svc,.act b,.act small,.card .num,.btn,.sl")), "yazı sığmadı"
            for part in ("ic", "tx", "go"):
                xs = pg.evaluate(f"[...new Set([...document.querySelectorAll('.act .{part}')].map(e=>"
                                 f"Math.round(e.getBoundingClientRect().left)))]")
                assert len(xs) == 1, f"satırlar hizasız ({part}: {xs})"
            assert pg.evaluate("new Promise(r=>{const i=new Image();i.onload=()=>r(i.naturalWidth>0);"
                               f"i.onerror=()=>r(false);i.src='{POSTER}'}})"), "durgun görüntü yok"
            if full:
                pg.evaluate("document.querySelectorAll('.drop').forEach(x=>x.classList.add('on'))")
                pg.wait_for_timeout(300)
                img = Image.open(io.BytesIO(pg.locator("#karekod img").screenshot()))
                assert d["pay_qr"] in Q.decode(img), "karekod okunmadı"
                svg = Image.open(io.BytesIO(pg.locator("#paylas > svg").screenshot()))
                assert d["qr"] in Q.decode(svg), "paylaş QR'ı okunmadı"
            shots.append(Image.open(io.BytesIO(pg.screenshot(full_page=full))))
            pg.close()
        b.close()
    assert not errors, errors
    h = max(s.height for s in shots)
    canvas = Image.new("RGB", (sum(s.width for s in shots) + 120, h + 120), (52, 52, 56))
    x = 40
    for s in shots:
        canvas.paste(s, (x, 60))
        x += s.width + 40
    canvas.save(path)
    return path


def tour_gif(path=TOUR):
    """Tur (390 × 844), zamanda adım adım: açılış (ışıklar yanar, T boyanır, yazılar gelir), aşağı kaydırma,
    karekod açılır."""
    from playwright.sync_api import sync_playwright
    frames, durs, errors = [], [], []
    with sync_playwright() as p, served() as url:
        b = p.chromium.launch(executable_path=CHROMIUM)
        pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
        pg.on("pageerror", lambda x: errors.append(str(x)))

        def shot(ms):
            frames.append(Image.open(io.BytesIO(pg.screenshot())).convert("RGB"))
            durs.append(ms)

        pg.goto(url)
        pg.wait_for_timeout(300)
        assert pg.evaluate("!!window.__boothDraw"), "kabin ışıkları (WebGL) çalışmadı"
        for k in list(range(0, 3000, 60)) + list(range(3000, 7200, 300)):
            _seek(pg, k)
            pg.evaluate("__boothDraw()")
            shot(60 if k < 3000 else 300)
        pg.evaluate("document.getAnimations().forEach(a=>a.play())")
        h = pg.evaluate("document.documentElement.scrollHeight - innerHeight")
        for y in range(0, h + 1, 60):
            pg.evaluate(f"scrollTo(0,{y})")
            pg.wait_for_timeout(60)
            shot(70)
        pg.evaluate("document.querySelector('.card').scrollIntoView({block:'center'})")
        pg.wait_for_timeout(500)
        pg.evaluate("document.getElementById('karekod').classList.add('on');"
                    "document.querySelector('[data-toggle=karekod]').classList.add('open');"
                    "document.getElementById('karekod').scrollIntoView({block:'center'})")
        pg.wait_for_timeout(400)
        shot(2600)
        b.close()
    assert not errors, errors
    # ortak palet, dağıtmasız (dither'sız): GIF küçük kalır
    frames = [f.resize((312, 675), Image.LANCZOS) for f in frames]
    pal = frames[45].quantize(colors=200, method=Image.Quantize.MEDIANCUT)
    out = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    out[0].save(path, save_all=True, append_images=out[1:], duration=durs, loop=0, optimize=True)
    return path


def standalone(doc, path=STANDALONE):
    """Denemelik tek dosya: yazı tipleri, durgun görüntü, karekod, simge ve rehber kartı sayfanın içine gömülü."""
    import base64

    def data(rel, mime):
        with open(os.path.join(OUT, rel), "rb") as f:
            return f"data:{mime};base64," + base64.b64encode(f.read()).decode()

    doc = re.sub(r'<link rel="preload"[^>]*>', "", doc)
    for rel in sorted(set(re.findall(r"fonts/p\d\.woff2?", doc))):
        doc = doc.replace(f"url({rel})", f"url({data(rel, 'font/' + rel.rsplit('.', 1)[1])})")
    doc = doc.replace(f"url({POSTER})", f"url({data(POSTER, 'image/jpeg')})")
    doc = doc.replace(f'href="{ICON_PNG}"', f'href="{data(ICON_PNG, "image/png")}"')
    doc = doc.replace(f'src="{KAREKOD}"', f'src="{data(KAREKOD, "image/png")}"')
    doc = doc.replace(f'href="{KAREKOD}"', f'href="{data(KAREKOD, "image/png")}"')
    doc = doc.replace(f'href="{VCF}" download', f'href="{data(VCF, "text/vcard")}" download="{VCF}"')
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    return path


def pack():
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for dp, _, files in os.walk(OUT):
            for fn in sorted(files):
                full = os.path.join(dp, fn)
                z.write(full, os.path.relpath(full, OUT))


def main():
    d = load()
    missed = strokes_cover()
    assert missed == 0, f"fırça darbeleri T'yi örtmüyor ({missed} piksel)"
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    doc = page(d)
    subset_fonts(html.unescape(doc))
    vcard(d)
    karekod_png(d)
    poster()
    og_image(d)
    touch_icon()
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(doc)
    pack()
    standalone(doc)
    size = sum(os.path.getsize(os.path.join(dp, fn)) for dp, _, fs in os.walk(OUT) for fn in fs)
    print("sayfa:", os.path.relpath(os.path.join(OUT, "index.html"), A.ROOT), f"(toplam {size // 1024} KB) →",
          d["sayfa_url"])
    print("deneme:", os.path.relpath(STANDALONE, A.ROOT), f"({os.path.getsize(STANDALONE) // 1024} KB, tek dosya)")
    print("önizleme:", os.path.relpath(screenshot(d), A.ROOT))
    if "--hizli" not in sys.argv:
        print("tur:", os.path.relpath(tour_gif(), A.ROOT))


if __name__ == "__main__":
    main()
