"""Restoran masalıkları için 10 örnek menü sitesi (telefon görünümü) – katalogda gösterilir.

Masalıktaki QR / NFC bu sayfayı açar. Her site masalığıyla aynı renk ve yazı tipinde ama düzeni kendine özgü:
klasik saray menüsü, fotoğraflı balık listesi, pizza kart ızgarası, burger posteri, uygulama gibi kahveci, Japon
minimali, kara tahta çay bahçesi, tam ekran fotoğraflı et lokantası, gün batımı plaj kulübü, gece terası.
Yemek fotoğrafları scripts/menu_yemek_foto.py ile çizilir (img/). İsimler, ürünler ve fiyatlar örnek.

Çıktı : restoran_masalik/siteler/<ad>/index.html, menu.html, ekran_ana.png, ekran_menu.png (390 × 844, 2×)

Kullanım:
  python3 scripts/menu_siteleri.py [ad ...]
"""
import html
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "restoran_masalik", "siteler")

FONTS = """
@font-face{font-family:Jost;src:url(../fonts/Jost.ttf);font-weight:100 900}
@font-face{font-family:Fraunces;src:url(../fonts/Fraunces.ttf);font-weight:100 900}
@font-face{font-family:Fraunces;src:url(../fonts/Fraunces-Italic.ttf);font-weight:100 900;font-style:italic}
@font-face{font-family:Playfair;src:url(../fonts/PlayfairDisplay.ttf);font-weight:400 900}
@font-face{font-family:Playfair;src:url(../fonts/PlayfairDisplay-Italic.ttf);font-weight:400 900;font-style:italic}
@font-face{font-family:Cinzel;src:url(../fonts/Cinzel.ttf);font-weight:400 900}
@font-face{font-family:Syne;src:url(../fonts/Syne.ttf);font-weight:400 800}
@font-face{font-family:Unbounded;src:url(../fonts/Unbounded.ttf);font-weight:200 900}
@font-face{font-family:Bodoni;src:url(../fonts/BodoniModa.ttf);font-weight:400 900}
@font-face{font-family:Anton;src:url(../fonts/Anton-Regular.ttf)}
@font-face{font-family:Norican;src:url(../fonts/Norican-Regular.ttf)}
@font-face{font-family:Caveat;src:url(../fonts/Caveat-Bold.ttf)}
@font-face{font-family:Manrope;src:url(../fonts/Manrope-SemiBold.ttf);font-weight:600}
"""

RESET = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{min-height:100%}
body{-webkit-font-smoothing:antialiased;font-family:Jost,'Noto Sans',sans-serif;font-size:16px;overflow-x:hidden}
a{color:inherit;text-decoration:none}
img{display:block;max-width:100%}
.num{font-family:Manrope,'Noto Sans',sans-serif;font-weight:600;white-space:nowrap}
"""

ICON = {
    "menu": '<path d="M4 5.5C6.5 4 9.5 4 12 5.8 14.5 4 17.5 4 20 5.5V19c-2.5-1.4-5.5-1.4-8 .4-2.5-1.8-5.5-1.8-8-.4z"/>'
            '<path d="M12 5.8v13.6"/>',
    "star": '<path d="M12 3.6l2.5 5.3 5.8.7-4.3 4 1.1 5.8L12 16.6l-5.1 2.8 1.1-5.8-4.3-4 5.8-.7z"/>',
    "wifi": '<path d="M3.5 9.5a12 12 0 0 1 17 0M6.5 12.6a7.7 7.7 0 0 1 11 0M9.4 15.6a3.6 3.6 0 0 1 5.2 0"/>'
            '<circle cx="12" cy="18.6" r="1.1" fill="currentColor"/>',
    "camera": '<rect x="4" y="4" width="16" height="16" rx="5"/><circle cx="12" cy="12" r="3.8"/>'
              '<circle cx="16.9" cy="7.1" r=".9" fill="currentColor"/>',
    "cal": '<rect x="4" y="5.5" width="16" height="14.5" rx="3"/><path d="M4 10h16M8.5 3.5v4M15.5 3.5v4"/>',
    "bell": '<path d="M6 16.5V11a6 6 0 0 1 12 0v5.5l1.5 2h-15z"/><path d="M10 20.5a2 2 0 0 0 4 0"/>',
    "card": '<rect x="3.5" y="6" width="17" height="12.5" rx="2.5"/><path d="M3.5 10h17M7 15h4"/>',
    "pin": '<path d="M12 21s-6.5-6-6.5-11a6.5 6.5 0 0 1 13 0c0 5-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.4"/>',
    "bag": '<path d="M5.5 8h13l-1 12h-11z"/><path d="M9 8V6.5a3 3 0 0 1 6 0V8"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/>',
    "home": '<path d="M4 11l8-6.5 8 6.5V20h-5.5v-5.5h-5V20H4z"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "fish": '<path d="M3 12c3-4.5 9.5-6 14-2l3.5-2.5v9L17 14c-4.5 4-11 2.5-14-2z"/><circle cx="8" cy="11" r=".9" '
            'fill="currentColor"/>',
}


def icon(k, cls="", sw=1.7):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICON[k]}</svg>')


def e(s):
    return html.escape(s)


def tr_upper(t):
    return t.replace("i", "İ").replace("ı", "I").upper()


def img(name):
    return f"../img/{name}.jpg"


def page(title, css, body):
    return (f'<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" '
            f'content="width=device-width,initial-scale=1"><title>{e(title)}</title><style>{FONTS}{RESET}{css}'
            f'</style></head><body>{body}</body></html>')


def items(site):
    for cat, rows in site["menu"]:
        for r in rows:
            yield cat, r


def tabs(site, cls="on", up=False):
    return "".join(f'<span class="{cls if k == 0 else ""}">{e(tr_upper(c) if up else c)}</span>'
                   for k, c in enumerate(site["tabs"]))


# ================================================================ 1 · Kaleiçi Sofrası: saray menüsü (kemer, noktalı fiyat)

KALEICI_CSS = """
body{background:#F6EFE3;color:#2B1A17}
.hero{background:#701E28;color:#E9CF94;text-align:center;padding:48px 24px 92px;position:relative;overflow:hidden}
.hero svg.m{position:absolute;inset:0;width:100%;height:100%}
.hero>*{position:relative}
.mark{width:50px;height:50px;margin:0 auto 10px;display:block}
.brand{font-family:Cinzel;font-weight:800;font-size:44px;letter-spacing:.06em;line-height:1}
.tag{font-size:12px;letter-spacing:.32em;text-transform:uppercase;color:#F3E6CC;margin-top:12px}
.pill{display:inline-flex;gap:8px;align-items:center;margin-top:16px;padding:7px 16px;border:1px solid #C9A35C;
  border-radius:999px;font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:#F3E6CC}
.pill b{font-family:Cinzel;font-size:16px;color:#E9CF94}
.arch{width:232px;height:214px;margin:-76px auto 0;position:relative;border-radius:116px 116px 10px 10px;padding:6px;
  background:linear-gradient(#E5C98C,#B58A45);box-shadow:0 18px 40px rgba(60,20,20,.25)}
.arch img{width:100%;height:100%;object-fit:cover;border-radius:110px 110px 6px 6px}
.cap{text-align:center;margin:10px 0 0;font-family:Fraunces;font-style:italic;font-size:16px;color:#701E28}
.cap small{display:block;font-family:Jost;font-style:normal;font-size:10.5px;letter-spacing:.3em;color:#8C6A2E;
  text-transform:uppercase;margin-bottom:1px}
.list{margin:10px 20px 0;border-top:1px solid #E1CFAF}
.list a{display:flex;align-items:center;gap:14px;padding:11px 4px;border-bottom:1px solid #E1CFAF}
.list .i{width:36px;height:36px;border-radius:50%;border:1px solid #C9A35C;display:grid;place-items:center;
  color:#701E28;flex:none}
.list .i svg{width:18px;height:18px}
.list b{font-family:Cinzel;font-weight:700;font-size:15px;letter-spacing:.05em;display:block}
.list small{color:#8A7468;font-size:12.5px}
.list .go{margin-left:auto;color:#C9A35C;width:18px;height:18px}
.list a.p{background:#701E28;color:#F3E6CC;border-radius:12px;padding:12px 14px;border:0;margin:10px 0 2px}
.list a.p .i{border-color:#E9CF94;color:#E9CF94}
.list a.p small{color:#E9CF94}
.rate{display:flex;justify-content:center;gap:10px;align-items:center;margin:12px 0 4px;color:#8A7468;font-size:12.5px}
.rate b{font-family:Cinzel;font-size:22px;color:#701E28}
.rate span{color:#C9A35C;letter-spacing:2px}
.foot{text-align:center;color:#8A7468;font-size:12px;padding:2px 0 24px}
.paper{background:#F8F2E6;min-height:100vh}
.top{background:#701E28;color:#E9CF94;display:flex;justify-content:space-between;align-items:center;padding:14px 18px}
.top b{font-family:Cinzel;font-size:20px;letter-spacing:.08em}
.top span{font-size:11px;letter-spacing:.2em;border:1px solid #C9A35C;border-radius:999px;padding:5px 11px}
.mh{text-align:center;padding:20px 0 4px}
.mh h1{font-family:Cinzel;font-weight:800;font-size:30px;letter-spacing:.24em;color:#701E28}
.orn{display:flex;align-items:center;justify-content:center;gap:10px;color:#C9A35C;font-size:15px;margin-top:2px}
.orn:before,.orn:after{content:"";width:64px;height:1px;background:#C9A35C}
.chef{margin:12px 20px 0;display:flex;gap:14px;align-items:center;padding:12px;border:1px solid #E1CFAF;
  border-radius:16px;background:#FFFBF4}
.chef img{width:92px;height:92px;border-radius:50%;object-fit:cover;border:3px solid #E5C98C;flex:none}
.chef small{font-size:10.5px;letter-spacing:.26em;color:#8C6A2E;text-transform:uppercase}
.chef b{display:block;font-family:Cinzel;font-size:18px;color:#701E28;margin:2px 0}
.chef p{font-family:Fraunces;font-style:italic;font-size:13px;color:#7A6458}
.chef .num{color:#701E28;font-size:15px;margin-top:4px;display:block}
.sec{padding:0 22px}
.sec h2{font-family:Cinzel;font-size:14.5px;letter-spacing:.3em;text-align:center;color:#701E28;margin:18px 0 4px}
.it{padding:8px 0}
.it .r{display:flex;align-items:baseline;gap:8px}
.it .r b{font-family:Cinzel;font-weight:700;font-size:14.5px;letter-spacing:.03em}
.it .r i{flex:1;border-bottom:1.5px dotted #C9A35C;transform:translateY(-4px)}
.it .r .num{color:#701E28;font-size:14.5px}
.it p{font-family:Fraunces;font-style:italic;font-size:13px;color:#8A7468;margin-top:1px}
"""

KALEICI_MOTIF = ('<svg class="m" viewBox="0 0 390 330" preserveAspectRatio="none" fill="none" stroke="#C9A35C" '
                 'stroke-width="1.2" opacity=".5"><path d="M24 330V150C24 70 110 22 195 10 280 22 366 70 366 150V330"/>'
                 '<path d="M34 330V152C34 78 116 34 195 22 274 34 356 78 356 152V330"/></svg>')
KALEICI_MARK = ('<svg class="mark" viewBox="0 0 64 64" fill="#C9A35C"><path d="M32 6c5 7 6 15 0 26-6-11-5-19 0-26z"/>'
                '<path d="M30 34C24 32 17 25 16 14c7 4 12 10 14 20zM34 34c6-2 13-9 14-20-7 4-12 10-14 20z"/>'
                '<rect x="31" y="32" width="2" height="22"/></svg>')


def home_kaleici(s):
    rows = [("menu", "Menü", "Ana yemekler, mezeler, tatlılar", True), ("star", "Google'da değerlendirin", "★★★★★", False),
            ("bell", "Garson çağır", "Masa 07", False), ("wifi", "Wi-Fi", "Kaleici_Misafir", False),
            ("cal", "Rezervasyon", "0242 000 00 00", False)]
    lst = "".join(f'<a class="{"p" if p else ""}" href="{"menu.html" if k == "menu" else "#"}"><span class="i">'
                  f'{icon(k)}</span><span><b>{e(t)}</b><small>{e(sub)}</small></span>{icon("arrow", "go")}</a>'
                  for k, t, sub, p in rows)
    body = (f'<header class="hero">{KALEICI_MOTIF}{KALEICI_MARK}<div class="brand">KALEİÇİ</div>'
            f'<div class="tag">Sofrası · Osmanlı mutfağı</div><div class="pill">Masa <b>07</b></div></header>'
            f'<div class="arch"><img src="{img("hunkar")}" alt=""></div>'
            f'<p class="cap"><small>Şefin önerisi</small>Hünkâr beğendi</p>'
            f'<nav class="list">{lst}</nav>'
            f'<div class="rate"><b>4,8</b><span>★★★★★</span>Google · 2.316 yorum</div>'
            f'<p class="foot">Kaleiçi, Muratpaşa / Antalya · Her gün 08:00–24:00</p>')
    return page(s["name"], KALEICI_CSS, body)


def menu_kaleici(s):
    secs = []
    for cat, rows in s["menu"]:
        its = "".join(f'<div class="it"><div class="r"><b>{e(n)}</b><i></i><span class="num">{e(p)}</span></div>'
                      f'<p>{e(d)}</p></div>' for n, d, p, *_ in rows)
        secs.append(f'<section class="sec"><h2>{e(tr_upper(cat))}</h2>{its}</section>')
    body = (f'<div class="paper"><div class="top"><b>KALEİÇİ</b><span>MASA 07</span></div>'
            f'<div class="mh"><h1>MENÜ</h1><div class="orn">❦</div></div>'
            f'<div class="chef"><img src="{img("hunkar")}" alt=""><div><small>Şefin önerisi</small>'
            f'<b>Hünkâr beğendi</b><p>Közlenmiş patlıcan beğendi, kuzu tas kebabı</p><span class="num">540 ₺</span>'
            f'</div></div>{"".join(secs)}</div>')
    return page(s["name"] + " · Menü", KALEICI_CSS, body)


# ================================================================ 2 · Mavi Lagün: üstte fotoğraf, küçük resimli liste

LAGUN_CSS = """
body{background:#16213F;color:#F3EAD7}
.ph{height:392px;position:relative;overflow:hidden}
.ph img{width:100%;height:100%;object-fit:cover;transform:scale(1.18)}
.ph:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(22,33,63,.2) 0%,
  rgba(22,33,63,0) 35%,rgba(22,33,63,.75) 78%,#16213F 100%)}
.chip{position:absolute;top:18px;right:16px;z-index:2;padding:8px 14px;border-radius:999px;font-size:12px;
  letter-spacing:.18em;background:rgba(255,255,255,.18);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,.4)}
.ttl{position:absolute;left:22px;bottom:18px;z-index:2}
.ttl b{font-family:Fraunces;font-style:italic;font-weight:600;font-size:54px;line-height:1;display:block}
.ttl span{font-size:12.5px;letter-spacing:.3em;text-transform:uppercase;color:#CCA060}
.today{margin:6px 18px 0;padding:13px 16px;border-radius:16px;background:#1E2A4A;border:1px solid #2C3A60;
  display:flex;align-items:center;gap:12px}
.today svg{width:28px;height:28px;color:#CCA060;flex:none}
.today small{display:block;font-size:11px;letter-spacing:.24em;color:#CCA060;text-transform:uppercase}
.today b{font-family:Fraunces;font-style:italic;font-weight:600;font-size:19px}
.today .num{margin-left:auto;color:#CCA060}
.qa{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;padding:18px 14px 6px;text-align:center;font-size:12px}
.qa a span{width:56px;height:56px;margin:0 auto 7px;border-radius:50%;display:grid;place-items:center;
  border:1px solid #CCA060;color:#CCA060}
.qa a span svg{width:24px;height:24px}
.big{display:flex;justify-content:space-between;align-items:center;margin:14px 18px 0;padding:18px 20px;
  border-radius:18px;background:#CCA060;color:#16213F;font-weight:600;font-size:17px}
.big svg{width:22px;height:22px}
.rt{display:flex;align-items:center;gap:10px;justify-content:center;margin:18px 0 6px;font-size:12.5px;color:#A9B0C6}
.rt b{font-family:Fraunces;font-size:22px;color:#F3EAD7}.rt span{color:#CCA060;letter-spacing:2px}
.foot{text-align:center;font-size:12px;color:#7E87A2;padding-bottom:24px}
.light{background:#F3F1EC;color:#16213F;min-height:100vh}
.bar{background:#16213F;color:#F3EAD7;display:flex;justify-content:space-between;align-items:center;padding:14px 18px}
.bar b{font-family:Fraunces;font-style:italic;font-size:23px}
.bar span{font-size:11px;letter-spacing:.2em;border:1px solid #CCA060;border-radius:999px;padding:5px 11px}
.feat{margin:16px 18px 0;border-radius:20px;overflow:hidden;position:relative;height:178px}
.feat img{width:100%;height:100%;object-fit:cover}
.feat div{position:absolute;inset:auto 0 0 0;padding:14px 16px;color:#fff;
  background:linear-gradient(transparent,rgba(16,24,48,.85))}
.feat small{font-size:10.5px;letter-spacing:.24em;text-transform:uppercase;color:#E8C989}
.feat b{display:block;font-family:Fraunces;font-style:italic;font-size:22px}
.feat .num{position:absolute;right:16px;bottom:16px;color:#E8C989}
.chips{display:flex;gap:8px;padding:16px 18px 4px;overflow:hidden;white-space:nowrap}
.chips span{padding:8px 14px;border-radius:999px;border:1px solid #DDE0E6;font-size:13.5px;background:#fff}
.chips span.on{background:#16213F;color:#F3EAD7;border-color:#16213F}
.cat{font-family:Fraunces;font-style:italic;font-weight:600;font-size:21px;padding:12px 18px 0}
.row{display:flex;gap:14px;align-items:center;margin:0 18px;padding:10px 0;border-bottom:1px solid #E1E3E8}
.row .th{width:72px;height:72px;border-radius:16px;overflow:hidden;flex:none;background:#1E2A4A;display:grid;
  place-items:center;color:#CCA060}
.row .th img{width:100%;height:100%;object-fit:cover}
.row .th svg{width:30px;height:30px}
.row b{font-weight:600;font-size:16px;display:block}
.row p{font-size:12.8px;color:#6E7690;line-height:1.35;margin-top:2px}
.row .num{margin-left:auto;color:#B4893F;font-size:15px;align-self:flex-start;padding-top:4px}
.tg{display:inline-block;font-size:10px;font-weight:600;letter-spacing:.06em;background:#E9EDF5;color:#1E2A4A;
  border-radius:999px;padding:2px 8px;margin-left:6px;vertical-align:2px}
"""


def home_lagun(s):
    qa = [("menu", "Menü"), ("star", "Yorum"), ("wifi", "Wi-Fi"), ("cal", "Rezervasyon")]
    q = "".join(f'<a href="{"menu.html" if k == "menu" else "#"}"><span>{icon(k)}</span>{e(t)}</a>' for k, t in qa)
    body = (f'<div class="ph"><img src="{img("balik_levrek")}" alt=""><span class="chip">MASA 07</span>'
            f'<div class="ttl"><b>Mavi Lagün</b><span>Balık evi · Konyaaltı</span></div></div>'
            f'<div class="today">{icon("fish")}<span><small>Bugün tezgâhta</small><b>Levrek ızgara</b></span>'
            f'<span class="num">kg 1.400 ₺</span></div><nav class="qa">{q}</nav>'
            f'<a class="big" href="menu.html">Menüyü görüntüle {icon("arrow")}</a>'
            f'<div class="rt"><b>4,7</b><span>★★★★★</span>Google · 1.184 yorum</div>'
            f'<p class="foot">Konyaaltı Sahili / Antalya · 12:00–24:00</p>')
    return page(s["name"], LAGUN_CSS, body)


def menu_lagun(s):
    secs = []
    for cat, rows in s["menu"]:
        r = []
        for n, d, p, tg, im in rows:
            th = f'<img src="{img(im)}" alt="">' if im else icon("fish")
            t = f'<span class="tg">{e(tg)}</span>' if tg else ""
            r.append(f'<div class="row"><span class="th">{th}</span><span><b>{e(n)}{t}</b><p>{e(d)}</p></span>'
                     f'<span class="num">{e(p)}</span></div>')
        secs.append(f'<div class="cat">{e(cat)}</div>{"".join(r)}')
    body = (f'<div class="light"><div class="bar"><b>Mavi Lagün</b><span>MASA 07</span></div>'
            f'<div class="feat"><img src="{img("balik_levrek")}" alt=""><div><small>Günün balığı</small>'
            f'<b>Levrek ızgara</b></div><span class="num">kg 1.400 ₺</span></div>'
            f'<div class="chips">{tabs(s)}</div>{"".join(secs)}</div>')
    return page(s["name"] + " · Menü", LAGUN_CSS, body)


# ================================================================ 3 · Forno Rosso: büyük kart + kare kart ızgarası

FORNO_CSS = """
body{background:#F8F2E8;color:#3A1418}
.hd{display:flex;justify-content:space-between;align-items:center;padding:22px 20px 6px}
.hd b{font-family:Playfair;font-weight:900;font-size:30px;color:#8E2230;line-height:1}
.hd b small{display:block;font-family:Jost;font-weight:500;font-size:11px;letter-spacing:.32em;color:#6A4C3C;
  margin-top:6px;text-transform:uppercase}
.hd>span{background:#8E2230;color:#FFF4E2;border-radius:14px;padding:7px 12px;text-align:center;font-size:10.5px;
  letter-spacing:.2em}
.hd>span b{display:block;font-family:Playfair;font-size:22px;color:#FFF4E2;letter-spacing:0}
.hc{margin:14px 18px 0;border-radius:30px;overflow:hidden;position:relative;height:300px;
  box-shadow:0 18px 40px rgba(90,30,30,.18)}
.hc img{width:100%;height:100%;object-fit:cover}
.hc .bd{position:absolute;left:14px;top:14px;background:#FFF4E2;color:#8E2230;border-radius:999px;padding:7px 13px;
  font-size:12px;font-weight:600}
.hc .tx{position:absolute;left:0;right:0;bottom:0;padding:40px 18px 16px;color:#fff;
  background:linear-gradient(transparent,rgba(40,12,12,.8))}
.hc .tx b{font-family:Playfair;font-weight:900;font-size:24px;display:block}
.hc .tx span{font-size:13px;opacity:.92}
.tiles{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:16px 18px 0}
.tiles a{background:#FFFCF6;border:1px solid #EADCC8;border-radius:24px;padding:16px;min-height:104px;display:flex;
  flex-direction:column;justify-content:space-between}
.tiles a svg{width:28px;height:28px;color:#8E2230}
.tiles a b{font-weight:600;font-size:16px}
.tiles a small{display:block;color:#8B6E66;font-size:12px}
.tiles a.p{background:#8E2230;color:#FFF4E2;border-color:#8E2230}
.tiles a.p svg{color:#FFF4E2}.tiles a.p small{color:#F3D6C0}
.rt{margin:14px 18px 20px;display:flex;align-items:center;gap:12px;font-size:12.5px;color:#8B6E66}
.rt b{font-family:Playfair;font-weight:900;font-size:26px;color:#3A1418}.rt i{font-style:normal;color:#E2A93B;letter-spacing:2px}
.tabs{display:flex;gap:8px;padding:12px 18px 4px;overflow:hidden;white-space:nowrap}
.tabs span{padding:9px 15px;border-radius:999px;background:#FFFCF6;border:1px solid #EADCC8;font-size:14px}
.tabs span.on{background:#8E2230;color:#FFF4E2;border-color:#8E2230}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:12px 18px 24px}
.card{background:#FFFCF6;border:1px solid #EADCC8;border-radius:22px;overflow:hidden;position:relative}
.card img{width:100%;aspect-ratio:1/1;object-fit:cover}
.card div{padding:10px 12px 12px}
.card b{font-family:Playfair;font-weight:900;font-size:16.5px;display:block;line-height:1.15}
.card p{font-size:11.8px;color:#8B6E66;line-height:1.35;margin:4px 0 8px;height:32px;overflow:hidden}
.card .ft{display:flex;justify-content:space-between;align-items:center;padding:0}
.card .num{color:#8E2230;font-size:15px}
.card .add{width:30px;height:30px;border-radius:50%;background:#8E2230;color:#fff;display:grid;place-items:center}
.card .add svg{width:16px;height:16px}
.card em{position:absolute;left:10px;top:10px;font-style:normal;font-size:11px;font-weight:600;background:#FFF4E2;
  color:#8E2230;border-radius:999px;padding:3px 9px}
"""


def home_forno(s):
    tl = [("menu", "Menü", "Pizzalar, makarnalar", True), ("bag", "Paket sipariş", "Kapıya 30 dk", False),
          ("star", "Yorum yap", "★★★★★", False), ("wifi", "Wi-Fi", "Forno_Misafir", False)]
    t = "".join(f'<a class="{"p" if p else ""}" href="{"menu.html" if k == "menu" else "#"}">{icon(k)}'
                f'<span><b>{e(a)}</b><small>{e(b)}</small></span></a>' for k, a, b, p in tl)
    body = (f'<div class="hd"><b>Forno Rosso<small>Pizzeria napoletana</small></b><span>MASA<b>07</b></span></div>'
            f'<div class="hc"><img src="{img("pizza_margherita")}" alt=""><span class="bd">Odun fırını · 90 sn</span>'
            f'<div class="tx"><b>Margherita</b><span>San Marzano, fior di latte, fesleğen · 380 ₺</span></div></div>'
            f'<div class="tiles">{t}</div>'
            f'<div class="rt"><b>4,9</b><span><i>★★★★★</i><br>Google · 862 yorum</span></div>')
    return page(s["name"], FORNO_CSS, body)


def menu_forno(s):
    cards = "".join(f'<div class="card"><img src="{img(im)}" alt="">{f"<em>{e(tg)}</em>" if tg else ""}<div>'
                    f'<b>{e(n)}</b><p>{e(d)}</p><div class="ft"><span class="num">{e(p)}</span>'
                    f'<span class="add">{icon("plus", sw=2.4)}</span></div></div></div>'
                    for _, (n, d, p, tg, im) in items(s) if im)
    body = (f'<div class="hd"><b>Menü<small>Fiyatlara KDV dahildir</small></b><span>MASA<b>07</b></span></div>'
            f'<div class="tabs">{tabs(s)}</div><div class="grid">{cards}</div>')
    return page(s["name"] + " · Menü", FORNO_CSS, body)


# ================================================================ 4 · Garaj Burger: poster, tam genişlikte kartlar

GARAJ_CSS = """
body{background:#111113;color:#F2EEE6}
.hz{height:14px;background:repeating-linear-gradient(-45deg,#E0A436 0 14px,#111113 14px 28px)}
.ps{position:relative;padding:18px 18px 0;height:430px;overflow:hidden}
.ps h1{font-family:Anton;font-weight:400;font-size:132px;line-height:.86;color:#E0A436;letter-spacing:.01em;
  position:relative;z-index:1}
.ps .sub{font-family:Anton;font-size:22px;letter-spacing:.12em;margin-top:10px;position:relative;z-index:1}
.ps img{position:absolute;right:-74px;bottom:-62px;width:360px;height:360px;object-fit:cover;z-index:2;
  -webkit-mask-image:radial-gradient(circle at 50% 50%,#000 44%,transparent 64%);
  mask-image:radial-gradient(circle at 50% 50%,#000 44%,transparent 64%)}
.ps .ms{position:absolute;left:18px;bottom:24px;z-index:3;background:#E0A436;color:#111;font-family:Anton;
  font-size:20px;letter-spacing:.06em;padding:8px 14px;transform:rotate(-3deg)}
.blk{padding:12px 16px 0;display:grid;gap:10px}
.blk a{display:flex;justify-content:space-between;align-items:center;padding:16px 18px;font-family:Anton;
  letter-spacing:.05em;font-size:22px;background:#1E1E22;border:2px solid #2C2C33}
.blk a small{display:block;font-family:Jost;font-size:12px;letter-spacing:.04em;color:#9A968C;margin-top:2px}
.blk a svg{width:26px;height:26px}
.blk a.y{background:#E0A436;color:#111;border-color:#E0A436;font-size:36px;padding:12px 18px}
.blk .two{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.blk .two a{font-size:18px;flex-direction:column;align-items:flex-start;gap:8px}
.st{display:flex;align-items:center;gap:10px;padding:14px 18px 22px;font-size:12.5px;color:#9A968C}
.st b{font-family:Anton;font-size:26px;color:#E0A436}.st span{color:#E0A436;letter-spacing:2px}
.tp{position:sticky;top:0;z-index:3;background:#111113;display:flex;justify-content:space-between;align-items:center;
  padding:14px 16px;border-bottom:2px solid #E0A436}
.tp b{font-family:Anton;font-size:28px;color:#E0A436;letter-spacing:.04em}
.tp span{font-family:Anton;font-size:15px;letter-spacing:.08em;background:#E0A436;color:#111;padding:5px 10px}
.tb{display:flex;gap:18px;padding:14px 16px 4px;font-family:Anton;font-size:18px;letter-spacing:.06em;color:#77736a}
.tb span.on{color:#F2EEE6;border-bottom:3px solid #E0A436;padding-bottom:3px}
.bc{margin:12px 16px 0;position:relative;height:236px;overflow:hidden;border:2px solid #2C2C33}
.bc img{width:100%;height:100%;object-fit:cover}
.bc .ov{position:absolute;inset:auto 0 0 0;padding:44px 14px 12px;background:linear-gradient(transparent,rgba(0,0,0,.85))}
.bc .ov b{font-family:Anton;font-size:30px;letter-spacing:.03em;display:block;line-height:1}
.bc .ov p{font-size:12.5px;color:#CFC9BD;margin-top:4px}
.bc .pr{position:absolute;right:12px;top:12px;background:#E0A436;color:#111;font-family:Anton;font-size:22px;
  padding:6px 12px;transform:rotate(-4deg)}
.bc .tg{position:absolute;left:12px;top:12px;background:#111;color:#E0A436;font-family:Anton;font-size:14px;
  letter-spacing:.08em;padding:4px 9px;border:1px solid #E0A436}
.cart{position:fixed;left:12px;right:12px;bottom:14px;z-index:4;background:#E0A436;color:#111;display:flex;
  justify-content:space-between;align-items:center;padding:15px 18px;font-family:Anton;font-size:20px;letter-spacing:.05em;
  box-shadow:0 10px 30px rgba(0,0,0,.5)}
.cart svg{width:24px;height:24px}
"""


def home_garaj(s):
    body = (f'<div class="hz"></div><div class="ps"><h1>GA<br>RAJ</h1><div class="sub">BURGER &amp; CO.</div>'
            f'<img src="{img("burger_smash")}" alt=""><span class="ms">MASA 12</span></div>'
            f'<nav class="blk"><a class="y" href="menu.html">MENÜ {icon("arrow", sw=2.4)}</a>'
            f'<div class="two"><a href="#">{icon("bag", sw=2)}<span>MASADAN SİPARİŞ<small>Masa 12</small></span></a>'
            f'<a href="#">{icon("card", sw=2)}<span>HESAP ÖDE<small>Kart · QR</small></span></a></div>'
            f'<a href="#"><span>PUAN VER<small>Google · 30 saniye</small></span><span style="color:#E0A436;'
            f'font-size:18px">★★★★★</span></a></nav>'
            f'<div class="st"><b>4,7</b><span>★★★★★</span>1.507 yorum · 12:00–02:00</div>')
    return page(s["name"], GARAJ_CSS, body)


def menu_garaj(s):
    cards = "".join(f'<div class="bc"><img src="{img(im)}" alt="">'
                    f'{f"<span class=tg>{e(tr_upper(tg))}</span>" if tg else ""}<span class="pr">{e(p)}</span>'
                    f'<div class="ov"><b>{e(tr_upper(n))}</b><p>{e(d)}</p></div></div>'
                    for _, (n, d, p, tg, im) in items(s) if im)
    body = (f'<div class="tp"><b>GARAJ</b><span>MASA 12</span></div><div class="tb">{tabs(s, up=True)}</div>{cards}'
            f'<div class="cart"><span>SEPET · 2 ÜRÜN · 920 ₺</span>{icon("arrow", sw=2.4)}</div>')
    return page(s["name"] + " · Menü", GARAJ_CSS, body)


# ================================================================ 5 · Köpük: uygulama (kaydırmalı kartlar, alt menü)

KOPUK_CSS = """
body{background:#F5EEE4;color:#3B2A22;padding-bottom:90px}
.hd{display:flex;justify-content:space-between;align-items:center;padding:20px 20px 0}
.hd b{font-family:Fraunces;font-style:italic;font-weight:900;font-size:32px}
.hd span{background:#4E3428;color:#F5E9D8;border-radius:999px;padding:7px 13px;font-size:12px;letter-spacing:.12em}
.hi{padding:14px 20px 0}
.hi small{font-size:13px;color:#8F7B6C}
.hi h1{font-family:Fraunces;font-weight:800;font-size:31px;line-height:1.1;margin-top:2px}
.sr{margin:14px 20px 0;display:flex;align-items:center;gap:10px;background:#FFFBF5;border:1px solid #E7D9C7;
  border-radius:999px;padding:12px 16px;color:#8F7B6C;font-size:14px}
.sr svg{width:20px;height:20px}
.sh{display:flex;justify-content:space-between;align-items:baseline;padding:18px 20px 10px}
.sh b{font-family:Fraunces;font-weight:800;font-size:20px}.sh a{font-size:13px;color:#8F7B6C}
.car{display:flex;gap:12px;padding-left:20px;overflow:hidden}
.cc{flex:none;width:158px;background:#FFFBF5;border-radius:24px;overflow:hidden;border:1px solid #E7D9C7}
.cc img{width:100%;height:150px;object-fit:cover}
.cc div{padding:10px 12px 12px}
.cc b{font-weight:600;font-size:15px;display:block}
.cc .num{color:#4E3428;font-size:14px}
.cc em{font-style:normal;font-size:10.5px;background:#4E3428;color:#F5E9D8;border-radius:999px;padding:2px 8px;
  margin-left:6px}
.cats{display:flex;justify-content:space-between;padding:18px 20px 0;text-align:center;font-size:12.5px}
.cats a{width:76px}
.cats img{width:60px;height:60px;border-radius:50%;object-fit:cover;margin:0 auto 6px;border:3px solid #FFFBF5;
  box-shadow:0 6px 14px rgba(60,40,20,.15)}
.wf{margin:16px 20px 0;display:flex;align-items:center;gap:12px;background:#4E3428;color:#F5E9D8;border-radius:22px;
  padding:14px 16px}
.wf svg{width:26px;height:26px}
.wf small{display:block;font-size:12px;opacity:.8}
.wf i{margin-left:auto;width:46px;height:26px;border-radius:999px;background:#C6A57F;position:relative;flex:none}
.wf i:after{content:"";position:absolute;right:3px;top:3px;width:20px;height:20px;border-radius:50%;background:#fff}
.nav{position:fixed;left:0;right:0;bottom:0;background:#FFFBF5;border-top:1px solid #E7D9C7;display:flex;
  justify-content:space-around;padding:10px 0 24px;font-size:11px;color:#8F7B6C;z-index:5}
.nav a{display:flex;flex-direction:column;align-items:center;gap:4px}
.nav svg{width:24px;height:24px}
.nav a.on{color:#4E3428;font-weight:600}
.tabs{display:flex;gap:8px;padding:14px 20px 6px;overflow:hidden;white-space:nowrap}
.tabs span{padding:9px 15px;border-radius:999px;background:#FFFBF5;border:1px solid #E7D9C7;font-size:14px}
.tabs span.on{background:#4E3428;color:#F5E9D8;border-color:#4E3428}
.li{display:flex;align-items:center;gap:14px;margin:0 20px;padding:11px 0;border-bottom:1px solid #E7D9C7}
.li img{width:66px;height:66px;border-radius:50%;object-fit:cover;flex:none}
.li b{font-weight:600;font-size:16px;display:block}
.li p{font-size:12.6px;color:#8F7B6C;line-height:1.35}
.li .num{display:block;color:#4E3428;margin-top:3px;font-size:14.5px}
.li .add{margin-left:auto;flex:none;width:34px;height:34px;border-radius:50%;border:1.5px solid #4E3428;display:grid;
  place-items:center;color:#4E3428}
.li .add.on{background:#4E3428;color:#F5E9D8}
.li .add svg{width:16px;height:16px}
.ct{position:fixed;left:14px;right:14px;bottom:16px;background:#4E3428;color:#F5E9D8;border-radius:22px;display:flex;
  justify-content:space-between;align-items:center;padding:16px 20px;z-index:5;box-shadow:0 12px 30px rgba(60,30,20,.35)}
.ct b{font-weight:600}.ct span{background:#C6A57F;color:#3B2A22;border-radius:999px;padding:7px 14px;font-weight:600;
  font-size:14px}
"""


def home_kopuk(s):
    car = [("kahve_fistik", "Fıstıklı latte", "165 ₺", "Yeni"), ("kahve_flatwhite", "Flat white", "140 ₺", ""),
           ("kahve_cheesecake", "San Sebastian", "210 ₺", "")]
    c = "".join(f'<div class="cc"><img src="{img(i)}" alt=""><div><b>{e(n)}</b><span class="num">{e(p)}</span>'
                f'{f"<em>{e(t)}</em>" if t else ""}</div></div>' for i, n, p, t in car)
    cats = [("kahve_espresso", "Espresso"), ("kahve_turk", "Türk kahvesi"), ("kahve_flatwhite", "Sütlü"),
            ("kahve_cheesecake", "Tatlı")]
    ct = "".join(f'<a href="menu.html"><img src="{img(i)}" alt="">{e(n)}</a>' for i, n in cats)
    nav = [("home", "Ana sayfa", True), ("menu", "Menü", False), ("bag", "Sipariş", False), ("star", "Yorum", False)]
    nv = "".join(f'<a class="{"on" if o else ""}" href="{"menu.html" if k == "menu" else "#"}">{icon(k)}{e(t)}</a>'
                 for k, t, o in nav)
    body = (f'<div class="hd"><b>köpük</b><span>MASA 03</span></div>'
            f'<div class="hi"><small>Günaydın ☀</small><h1>Bugün ne içelim?</h1></div>'
            f'<div class="sr">{icon("search")}Kahve, tatlı, kahvaltı ara</div>'
            f'<div class="sh"><b>Bu hafta</b><a href="menu.html">Tümü</a></div><div class="car">{c}</div>'
            f'<div class="cats">{ct}</div>'
            f'<div class="wf">{icon("wifi")}<span><b>Wi-Fi\'ye bağlan</b><small>Kopuk_Misafir · tek dokunuş</small></span>'
            f'<i></i></div><nav class="nav">{nv}</nav>')
    return page(s["name"], KOPUK_CSS, body)


def menu_kopuk(s):
    rows = []
    for k, (_, (n, d, p, tg, im)) in enumerate(items(s)):
        rows.append(f'<div class="li"><img src="{img(im)}" alt=""><span><b>{e(n)}</b><p>{e(d)}</p>'
                    f'<span class="num">{e(p)}</span></span><span class="add{" on" if k in (1, 2) else ""}">'
                    f'{icon("plus", sw=2.4)}</span></div>')
    body = (f'<div class="hd"><b>köpük</b><span>MASA 03</span></div><div class="hi"><h1>Menü</h1></div>'
            f'<div class="tabs">{tabs(s)}</div>{"".join(rows)}'
            f'<div class="ct"><b>2 ürün · 305 ₺</b><span>Siparişi gönder</span></div>')
    return page(s["name"] + " · Menü", KOPUK_CSS, body)


# ================================================================ 6 · Koi: Japon minimali (numaralı satırlar, zikzak)

KOI_CSS = """
body{background:#F5F1E8;color:#141414}
.wrap{padding:30px 26px 20px;position:relative}
.sun{position:absolute;right:26px;top:26px;width:84px;height:84px;border-radius:50%;background:#C0302C}
.koi{font-family:Syne;font-weight:800;font-size:104px;letter-spacing:.14em;line-height:1;margin-top:96px}
.tg{font-size:12px;letter-spacing:.5em;margin-top:6px}
.ms{display:inline-block;margin-top:16px;font-size:12px;letter-spacing:.3em;border:1px solid #141414;padding:7px 12px}
.ft{display:flex;gap:16px;margin-top:22px;align-items:flex-end}
.ft img{width:56%;height:164px;object-fit:cover}
.ft p{font-size:12px;line-height:1.6;color:#77736A}
.ft p b{display:block;font-family:Syne;font-weight:800;font-size:15px;color:#141414;letter-spacing:.06em}
.ln{margin-top:20px;border-top:1px solid #141414}
.ln a{display:flex;align-items:center;gap:16px;padding:15px 0;border-bottom:1px solid #D8D1C2;font-family:Syne;
  font-weight:700;font-size:19px;letter-spacing:.04em}
.ln a i{font-style:normal;font-size:12px;color:#C0302C;letter-spacing:.1em;width:22px}
.ln a small{margin-left:auto;font-family:Jost;font-weight:400;font-size:12px;color:#77736A;letter-spacing:.06em}
.ln a svg{width:18px;height:18px}
.ft2{font-size:11.5px;letter-spacing:.2em;color:#77736A;margin-top:16px}
.mt{display:flex;justify-content:space-between;align-items:center;padding:20px 22px 0}
.mt b{font-family:Syne;font-weight:800;font-size:26px;letter-spacing:.2em}
.mt span{font-size:11px;letter-spacing:.3em}
.mt i{display:inline-block;width:14px;height:14px;border-radius:50%;background:#C0302C;margin-right:8px;
  vertical-align:-2px}
.tb{display:flex;gap:20px;padding:20px 22px 6px;font-size:13px;letter-spacing:.24em;text-transform:uppercase;color:#77736A}
.tb span.on{color:#141414;border-bottom:2px solid #C0302C;padding-bottom:4px}
.z{display:flex;gap:16px;align-items:center;padding:16px 22px;border-bottom:1px solid #E2DCCF}
.z.r{flex-direction:row-reverse;text-align:right}
.z img{width:52%;aspect-ratio:1/1;object-fit:cover}
.z i{font-style:normal;font-family:Syne;font-weight:800;font-size:38px;color:#C0302C;line-height:1;display:block}
.z b{font-family:Syne;font-weight:800;font-size:17px;letter-spacing:.04em;display:block;margin-top:6px}
.z p{font-size:12.4px;color:#77736A;line-height:1.45;margin-top:4px}
.z .num{display:block;margin-top:8px;font-size:15px}
.z em{font-style:normal;font-size:10px;letter-spacing:.2em;color:#C0302C;border:1px solid #C0302C;padding:2px 6px;
  display:inline-block;margin-top:6px}
"""


def home_koi(s):
    ln = [("01", "Menü", "sushi · ramen", "menu.html"), ("02", "Masadan sipariş", "masa 08", "#"),
          ("03", "Yorum", "google", "#"), ("04", "Wi-Fi", "Koi_Misafir", "#")]
    lk = "".join(f'<a href="{h}"><i>{n}</i>{e(t)}<small>{e(sub)}</small>{icon("arrow")}</a>' for n, t, sub, h in ln)
    body = (f'<div class="wrap"><span class="sun"></span><div class="koi">KOI</div><div class="tg">SUSHI &amp; RAMEN</div>'
            f'<span class="ms">MASA 08</span><div class="ft"><img src="{img("susi_nigiri")}" alt="">'
            f'<p><b>OMAKASE</b>Şefin seçtiği 12 parça.<br>1.250 ₺</p></div><nav class="ln">{lk}</nav>'
            f'<p class="ft2">LARA / ANTALYA · 12:00–23:00 · 4,8 ★ GOOGLE</p></div>')
    return page(s["name"], KOI_CSS, body)


def menu_koi(s):
    z = "".join(f'<div class="z{" r" if k % 2 else ""}"><img src="{img(im)}" alt=""><div><i>{k + 1:02d}</i>'
                f'<b>{e(tr_upper(n))}</b><p>{e(d)}</p>{f"<em>{e(tr_upper(tg))}</em>" if tg else ""}'
                f'<span class="num">{e(p)}</span></div></div>'
                for k, (_, (n, d, p, tg, im)) in enumerate(items(s)))
    body = f'<div class="mt"><b>KOI</b><span><i></i>MASA 08</span></div><div class="tb">{tabs(s)}</div>{z}'
    return page(s["name"] + " · Menü", KOI_CSS, body)


# ================================================================ 7 · Asmaaltı: kara tahta, el yazısı, polaroid

ASMA_CSS = """
body{background:#5B3A22;color:#F4F1E6}
.bd{margin:10px;min-height:824px;border-radius:6px;padding:24px 22px 22px;position:relative;
  background:radial-gradient(ellipse at 30% 20%,rgba(255,255,255,.08),transparent 50%),
  radial-gradient(ellipse at 80% 70%,rgba(255,255,255,.05),transparent 45%),#26362B;
  box-shadow:inset 0 0 40px rgba(0,0,0,.55),0 0 0 6px #7A5532,0 0 0 8px #4A2F1B}
.hand{font-family:Caveat;font-weight:700}
h1.hand{font-size:68px;line-height:.9;text-align:center}
.sub{text-align:center;font-family:Caveat;font-size:25px;color:#F2D27A;margin-top:4px}
.ms{display:block;width:max-content;margin:8px auto 0;font-family:Caveat;font-size:25px;border:2px dashed
  rgba(244,241,230,.7);border-radius:12px;padding:0 16px}
.cup{width:196px;height:196px;margin:16px auto 0;border-radius:50%;padding:6px;border:2px dashed rgba(244,241,230,.6)}
.cup img{width:100%;height:100%;object-fit:cover;border-radius:50%}
.lf{position:absolute;width:84px;height:84px;opacity:.55}
.bx{display:grid;gap:12px;margin-top:20px}
.bx a{display:flex;justify-content:space-between;align-items:center;font-family:Caveat;font-size:29px;padding:4px 16px;
  border:2px solid rgba(244,241,230,.85);border-radius:14px 10px 16px 9px}
.bx a small{font-family:Caveat;font-size:21px;color:#C9D3C0}
.bx a.y{border-color:#F2D27A;color:#F2D27A}
.bx .two{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.bx .two a{font-size:25px;justify-content:center}
.ft{text-align:center;font-family:Caveat;font-size:22px;color:#C9D3C0;margin-top:16px}
.mh{display:flex;justify-content:space-between;align-items:baseline}
.mh h1{font-size:56px}
.mh span{font-family:Caveat;font-size:24px;color:#F2D27A}
.pol{display:flex;gap:16px;justify-content:center;margin:12px 0 4px}
.pol div{background:#F7F3E8;padding:7px 7px 28px;width:150px;box-shadow:0 8px 18px rgba(0,0,0,.4);position:relative}
.pol div:first-child{transform:rotate(-4deg)}.pol div:last-child{transform:rotate(3deg);margin-top:8px}
.pol img{width:100%;height:122px;object-fit:cover}
.pol span{position:absolute;left:0;right:0;bottom:2px;text-align:center;font-family:Caveat;font-size:21px;color:#3A2A20}
.pol div:before{content:"";position:absolute;left:50%;top:-10px;width:56px;height:18px;margin-left:-28px;z-index:2;
  background:rgba(240,226,180,.75);transform:rotate(-3deg)}
.sc h2{font-family:Caveat;font-size:35px;color:#F2D27A;margin:10px 0 0;text-decoration:underline;
  text-decoration-thickness:2px;text-underline-offset:6px}
.ci{display:flex;align-items:baseline;gap:8px;font-family:Caveat;font-size:28px;line-height:1.2}
.ci i{flex:1;border-bottom:2px dotted rgba(244,241,230,.5);transform:translateY(-6px)}
.cd{font-family:Caveat;font-size:20px;color:#C9D3C0;margin:-2px 0 4px}
"""

ASMA_LEAF = ('<svg class="lf" style="{}" viewBox="0 0 80 80" fill="none" stroke="#B9D39A" stroke-width="2" '
             'stroke-linecap="round"><path d="M10 70C20 40 40 20 72 10"/><path d="M26 46c-8-2-14-8-14-18 8 2 13 8 '
             '14 18zM40 32c-2-8 0-15 8-21 3 8 1 15-8 21zM34 40c8 0 15 4 18 12-9 1-15-3-18-12zM50 24c8 0 14 4 17 '
             '11-9 1-14-3-17-11z"/></svg>')


def home_asma(s):
    body = (f'<div class="bd">{ASMA_LEAF.format("left:-4px;top:-2px")}'
            f'{ASMA_LEAF.format("right:-4px;top:-2px;transform:scaleX(-1)")}'
            f'<h1 class="hand">Asmaaltı</h1><div class="sub">çay bahçesi · Düden</div>'
            f'<span class="ms">Masa 11</span><div class="cup"><img src="{img("cay")}" alt=""></div>'
            f'<nav class="bx"><a href="menu.html">Menüye bak <small>çay · gözleme · tost →</small></a>'
            f'<a class="y" href="#">Çay söyle! <small style="color:#F2D27A">tek dokunuş</small></a>'
            f'<div class="two"><a href="#">★ Değerlendir</a><a href="#">Wi-Fi</a></div></nav>'
            f'<p class="ft">Google 4,6 ★ · 2.904 yorum · 07:00–24:00</p></div>')
    return page(s["name"], ASMA_CSS, body)


def menu_asma(s):
    pol = "".join(f'<div><img src="{img(i)}" alt=""><span>{e(n)}</span></div>'
                  for i, n in (("gozleme", "Gözleme"), ("tost", "Kaşarlı tost")))
    secs = []
    for cat, rows in s["menu"]:
        r = "".join(f'<div class="ci"><span>{e(n)}</span><i></i><span>{e(p)}</span></div><div class="cd">{e(d)}</div>'
                    for n, d, p, *_ in rows)
        secs.append(f'<section class="sc"><h2>{e(cat)}</h2>{r}</section>')
    body = (f'<div class="bd"><div class="mh"><h1 class="hand">Menü</h1><span>Masa 11</span></div>'
            f'<div class="pol">{pol}</div>{"".join(secs)}</div>')
    return page(s["name"] + " · Menü", ASMA_CSS, body)


# ================================================================ 8 · Kasaphane: tam ekran fotoğraf, dergi menüsü

KASAP_CSS = """
body{background:#1C1714;color:#EFE6DA}
.fs{position:relative;height:844px;overflow:hidden}
.fs>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform:scale(1.3) translateY(3%)}
.fs:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(18,14,12,.92) 0%,
  rgba(18,14,12,.35) 30%,rgba(18,14,12,.15) 46%,rgba(18,14,12,.88) 68%,#1C1714 100%)}
.fs .t{position:absolute;top:40px;left:0;right:0;text-align:center;z-index:2}
.fs .t svg{width:56px;height:56px;margin:0 auto 8px;display:block}
.fs .t b{font-family:Bodoni;font-weight:800;font-size:44px;letter-spacing:.08em;display:block}
.fs .t span{font-size:12px;letter-spacing:.32em;color:#D7A574;text-transform:uppercase}
.fs .t em{display:inline-block;margin-top:14px;font-style:normal;font-size:11.5px;letter-spacing:.24em;
  border:1px solid #D7A574;padding:6px 12px}
.gl{position:absolute;left:16px;right:16px;bottom:24px;z-index:2;display:grid;grid-template-columns:1fr 1fr;gap:10px}
.gl a{padding:14px;background:rgba(40,32,26,.55);backdrop-filter:blur(14px);border:1px solid rgba(215,165,116,.35);
  display:flex;flex-direction:column;gap:8px;font-size:15px}
.gl a svg{width:22px;height:22px;color:#D7A574}
.gl a small{color:#B9AA98;font-size:12px}
.gl a.p{grid-column:1/3;flex-direction:row;justify-content:space-between;align-items:center;background:#B07C4F;
  color:#1C1714;border-color:#B07C4F;font-family:Bodoni;font-weight:800;font-size:24px;letter-spacing:.06em}
.gl a.p svg{color:#1C1714}
.gl .rt{grid-column:1/3;text-align:center;font-size:12.5px;color:#B9AA98;margin-top:2px}
.gl .rt b{font-family:Bodoni;color:#EFE6DA;font-size:19px}.gl .rt i{font-style:normal;color:#D7A574;letter-spacing:2px}
.tp{display:flex;justify-content:space-between;align-items:center;padding:16px 18px;border-bottom:1px solid #33291F}
.tp b{font-family:Bodoni;font-weight:800;font-size:22px;letter-spacing:.1em}
.tp span{font-size:11px;letter-spacing:.24em;color:#D7A574}
.hero{position:relative;height:250px;overflow:hidden}
.hero img{width:100%;height:100%;object-fit:cover;transform:scale(1.2)}
.hero div{position:absolute;inset:auto 0 0 0;padding:40px 18px 14px;background:linear-gradient(transparent,#1C1714)}
.hero small{font-size:10.5px;letter-spacing:.3em;color:#D7A574;text-transform:uppercase}
.hero b{display:block;font-family:Bodoni;font-weight:800;font-size:28px;line-height:1.1}
.hero .num{color:#D7A574}
.cap{font-family:Bodoni;font-style:italic;font-size:14px;color:#B9AA98;padding:4px 18px 0}
.tb{margin:14px 18px 0}
.tb h2{font-family:Bodoni;font-weight:800;font-size:13px;letter-spacing:.34em;color:#D7A574;
  border-bottom:1px solid #D7A574;padding-bottom:6px}
.tb .r{display:grid;grid-template-columns:1fr auto;gap:2px 10px;padding:10px 0;border-bottom:1px solid #33291F}
.tb .r b{font-family:Bodoni;font-weight:700;font-size:17px}
.tb .r p{font-size:12.4px;color:#A49584;grid-column:1}
.tb .r .num{color:#D7A574;grid-row:1;grid-column:2;font-size:14px}
.three{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding:16px 18px 26px}
.three img{width:100%;aspect-ratio:3/4;object-fit:cover}
.three span{display:block;font-family:Bodoni;font-size:13px;margin-top:5px}
"""

KASAP_MARK = ('<svg viewBox="0 0 64 64" fill="#D7A574"><path d="M10 22h32l8 7v12H10z"/>'
              '<rect x="50" y="29" width="12" height="6" rx="3"/><circle cx="18" cy="28" r="2.4" fill="#1C1714"/></svg>')


def home_kasap(s):
    body = (f'<div class="fs"><img src="{img("et_antrikot")}" alt=""><div class="t">{KASAP_MARK}<b>KASAPHANE</b>'
            f'<span>Et lokantası · 1974\'ten beri</span><br><em>MASA 07</em></div>'
            f'<nav class="gl"><a class="p" href="menu.html">MENÜ {icon("arrow", sw=2)}</a>'
            f'<a href="#">{icon("cal")}<span>Rezervasyon<br><small>19:00–23:00</small></span></a>'
            f'<a href="#">{icon("star")}<span>Google yorumu<br><small>★★★★★</small></span></a>'
            f'<a href="#">{icon("wifi")}<span>Wi-Fi<br><small>Kasaphane</small></span></a>'
            f'<a href="#">{icon("pin")}<span>Yol tarifi<br><small>Konyaaltı</small></span></a>'
            f'<p class="rt"><b>4,8</b> <i>★★★★★</i> · 1.072 yorum</p></nav></div>')
    return page(s["name"], KASAP_CSS, body)


def menu_kasap(s):
    cuts, grill = s["menu"][0][1], s["menu"][1][1]
    rows = "".join(f'<div class="r"><b>{e(n)}</b><span class="num">{e(p)}</span><p>{e(d)}</p></div>'
                   for n, d, p, *_ in cuts)
    three = "".join(f'<div><img src="{img(im)}" alt=""><span>{e(n)} · {e(p)}</span></div>' for n, d, p, tg, im in grill)
    body = (f'<div class="tp"><b>KASAPHANE</b><span>MASA 07</span></div>'
            f'<div class="hero"><img src="{img("et_antrikot")}" alt=""><div><small>Kasabın seçimi</small>'
            f'<b>Dry-aged antrikot</b><span class="num">100 g · 520 ₺</span></div></div>'
            f'<p class="cap">28 gün dinlendirildi, meşe kömüründe pişer.</p>'
            f'<div class="tb"><h2>KESİMLER · GRAMLA</h2>{rows}</div><div class="three">{three}</div>')
    return page(s["name"] + " · Menü", KASAP_CSS, body)


# ================================================================ 9 · Palmiye: gün batımı, taşlı (masonry) kartlar

PALMIYE_CSS = """
body{background:#F4EDE1;color:#1D2742}
.sky{position:relative;height:330px;overflow:hidden;color:#fff;text-align:center;
  background:linear-gradient(180deg,#2B3A6B 0%,#C9667A 46%,#F2A86C 76%,#F7CB8E 100%)}
.sky .sun{position:absolute;left:50%;bottom:50px;width:160px;height:160px;margin-left:-80px;border-radius:50%;
  background:radial-gradient(circle,#FFE3A8 0%,#FFC777 58%,rgba(255,199,119,0) 72%)}
.sky svg.w{position:absolute;bottom:0;left:0;width:100%}
.sky .pl{position:absolute;right:-6px;bottom:28px;width:150px;height:200px}
.sky .tt{position:relative;padding-top:44px}
.sky b{font-family:Norican;font-weight:400;font-size:76px;line-height:1}
.sky span{display:block;font-size:12px;letter-spacing:.34em;text-transform:uppercase;margin-top:4px}
.sky em{display:inline-block;margin-top:12px;font-style:normal;font-size:12px;letter-spacing:.16em;padding:7px 14px;
  border-radius:999px;background:rgba(255,255,255,.22);backdrop-filter:blur(8px)}
.dr{display:flex;gap:12px;padding:0 18px;margin-top:-30px;position:relative}
.dr a{flex:1;background:#fff;border-radius:22px;overflow:hidden;box-shadow:0 12px 26px rgba(29,39,66,.16)}
.dr img{width:100%;height:118px;object-fit:cover}
.dr span{display:block;padding:8px 10px 10px;font-size:12.5px;font-weight:600}
.dr span i{display:block;font-style:normal;font-weight:400;color:#B98A4A}
.pr{display:flex;justify-content:space-between;align-items:center;margin:16px 18px 0;padding:18px 20px;
  border-radius:22px;background:#1D2742;color:#F4EDE1;font-size:17px;font-weight:600}
.pr small{display:block;font-weight:400;font-size:12.5px;color:#D8BE95}
.pr svg{width:24px;height:24px}
.pl2{display:flex;gap:10px;padding:12px 18px 0}
.pl2 a{flex:1;display:flex;align-items:center;gap:8px;padding:12px;border-radius:18px;border:1px solid #E4D9C6;
  background:#FFFDF8;font-size:13px}
.pl2 svg{width:20px;height:20px;color:#B98A4A}
.day{margin:14px 18px 20px;padding:14px 16px;border-radius:18px;background:#EFE4D0;display:flex;
  justify-content:space-between;font-size:12.5px}
.day b{display:block;font-size:16px}
.top{background:#1D2742;color:#F4EDE1;padding:16px 18px;display:flex;justify-content:space-between;align-items:center}
.top b{font-family:Norican;font-weight:400;font-size:34px;line-height:1}
.top span{font-size:11px;letter-spacing:.18em;border:1px solid #D8BE95;border-radius:999px;padding:5px 11px}
.pills{display:flex;gap:8px;padding:14px 18px 6px;overflow:hidden;white-space:nowrap}
.pills span{padding:9px 16px;border-radius:999px;background:#FFFDF8;border:1px solid #E4D9C6;font-size:14px}
.pills span.on{background:#F2A86C;border-color:#F2A86C;color:#1D2742;font-weight:600}
.ms{columns:2;column-gap:12px;padding:8px 18px 24px}
.mc{break-inside:avoid;margin-bottom:12px;background:#FFFDF8;border-radius:24px;overflow:hidden;
  box-shadow:0 8px 20px rgba(29,39,66,.08)}
.mc img{width:100%;object-fit:cover}
.mc div{padding:10px 12px 12px}
.mc b{font-weight:600;font-size:15px;display:block}
.mc p{font-size:12px;color:#7C7F8F;line-height:1.35;margin-top:2px}
.mc .num{display:inline-block;margin-top:8px;background:#1D2742;color:#F4EDE1;border-radius:999px;padding:4px 11px;
  font-size:13px}
.mc em{font-style:normal;font-size:10.5px;color:#B98A4A;margin-left:6px}
"""

PALM = ('<svg class="pl" viewBox="0 0 150 200" fill="#1D2742"><path d="M92 200c-4-50-2-90 10-128l6 2c-10 36-12 76-8 126z"/>'
        '<path d="M104 70C80 40 50 38 24 52c30-2 52 4 76 26zM104 70c4-30 20-50 46-56-18 16-30 34-38 58zM104 70'
        'c26-14 40-14 46-10-18 0-32 6-42 16zM104 70C90 50 74 32 52 26c22 14 34 30 44 50zM104 70c-24-6-44 2-60 22 '
        '22-12 40-14 58-16z"/></svg>')
WAVE = ('<svg class="w" viewBox="0 0 390 60" preserveAspectRatio="none" height="60"><path d="M0 30c40-16 80-16 120 '
        '0s80 16 120 0 80-16 150 0V60H0z" fill="#F4EDE1"/></svg>')


def home_palmiye(s):
    dr = "".join(f'<a href="menu.html"><img src="{img(i)}" alt=""><span>{e(n)}<i>{e(p)}</i></span></a>'
                 for i, n, p in (("icki_aperol", "Aperol spritz", "420 ₺"), ("icki_mojito", "Mojito", "380 ₺"),
                                 ("poke_bowl", "Poke bowl", "460 ₺")))
    body = (f'<div class="sky"><span class="sun"></span>{PALM}{WAVE}<div class="tt"><b>Palmiye</b>'
            f'<span>Beach club · Lara</span><em>ŞEZLONG 12</em></div></div><div class="dr">{dr}</div>'
            f'<a class="pr" href="#"><span>Şezlonga sipariş<small>Ortalama 12 dakikada gelir</small></span>'
            f'{icon("arrow", sw=2)}</a>'
            f'<div class="pl2"><a href="menu.html">{icon("menu")}Menü</a><a href="#">{icon("star")}Yorum</a>'
            f'<a href="#">{icon("wifi")}Wi-Fi</a></div>'
            f'<div class="day"><span><b>17:00</b>DJ set</span><span><b>19:42</b>Gün batımı</span>'
            f'<span><b>4,7 ★</b>3.215 yorum</span></div>')
    return page(s["name"], PALMIYE_CSS, body)


def menu_palmiye(s):
    hs = [236, 178, 200, 168]
    cards = "".join(f'<div class="mc"><img src="{img(im)}" style="height:{hs[k % 4]}px" alt=""><div><b>{e(n)}'
                    f'{f"<em>{e(tg)}</em>" if tg else ""}</b><p>{e(d)}</p><span class="num">{e(p)}</span></div></div>'
                    for k, (_, (n, d, p, tg, im)) in enumerate(items(s)))
    body = (f'<div class="top"><b>Palmiye</b><span>ŞEZLONG 12</span></div><div class="pills">{tabs(s)}</div>'
            f'<div class="ms">{cards}</div>')
    return page(s["name"] + " · Menü", PALMIYE_CSS, body)


# ================================================================ 10 · Rooftop 360: gece, cam düğmeler, hikâye kartları

R360_CSS = """
body{background:#0E0E10;color:#EEE8DC}
.nt{position:relative;min-height:844px;overflow:hidden;
  background:radial-gradient(circle at 15% 12%,rgba(201,164,94,.35),transparent 14%),
  radial-gradient(circle at 85% 22%,rgba(150,110,220,.28),transparent 16%),
  radial-gradient(circle at 70% 6%,rgba(255,190,120,.3),transparent 10%),
  radial-gradient(circle at 30% 40%,rgba(201,164,94,.12),transparent 22%),#0E0E10}
.sk{position:absolute;left:0;right:0;top:290px;width:100%;opacity:.35}
.tt{text-align:center;padding-top:46px;position:relative}
.tt b{font-family:Unbounded;font-weight:800;font-size:92px;color:#C9A45E;line-height:1;letter-spacing:-.02em}
.tt span{display:block;font-size:11.5px;letter-spacing:.44em;margin-top:8px}
.ring{width:214px;height:214px;margin:26px auto 0;border-radius:50%;padding:5px;position:relative;
  background:conic-gradient(#C9A45E,#6E5A30,#C9A45E,#E9D3A0,#C9A45E);box-shadow:0 0 60px rgba(201,164,94,.35)}
.ring img{width:100%;height:100%;border-radius:50%;object-fit:cover}
.ring em{position:absolute;right:-6px;bottom:18px;font-style:normal;background:#C9A45E;color:#0E0E10;font-size:11px;
  font-weight:600;letter-spacing:.14em;padding:6px 10px;border-radius:999px}
.gb{display:grid;gap:10px;padding:26px 18px 0;position:relative}
.gb a{display:flex;align-items:center;gap:14px;padding:15px 16px;border-radius:16px;background:rgba(255,255,255,.06);
  border:1px solid rgba(201,164,94,.3);backdrop-filter:blur(12px)}
.gb a svg{width:22px;height:22px;color:#C9A45E}
.gb a b{font-weight:600}.gb a small{margin-left:auto;font-size:12px;color:#8E8A82}
.gb a.p{background:#C9A45E;color:#0E0E10;border-color:#C9A45E;font-family:Unbounded;font-weight:700;font-size:15px;
  letter-spacing:.06em}
.gb a.p svg{color:#0E0E10}.gb a.p small{color:#3a3020}
.mt{display:flex;justify-content:space-between;align-items:center;padding:16px 18px}
.mt b{font-family:Unbounded;font-weight:800;font-size:28px;color:#C9A45E}
.mt span{font-size:11px;letter-spacing:.24em;border:1px solid #C9A45E;border-radius:999px;padding:5px 11px;color:#C9A45E}
.st{display:flex;gap:16px;padding:2px 18px 14px;overflow:hidden}
.st a{text-align:center;font-size:11.5px;color:#BDB6A8;flex:none}
.st a span{display:block;width:66px;height:66px;border-radius:50%;padding:3px;margin-bottom:6px;
  background:conic-gradient(#C9A45E,#8A6FD0,#C9A45E)}
.st a span img{width:100%;height:100%;border-radius:50%;object-fit:cover;border:2px solid #0E0E10}
.sc{position:relative;margin:0 14px 12px;height:300px;border-radius:22px;overflow:hidden}
.sc img{width:100%;height:100%;object-fit:cover}
.sc .ov{position:absolute;inset:auto 0 0 0;padding:60px 16px 16px;background:linear-gradient(transparent,rgba(8,8,10,.92))}
.sc .ov b{font-family:Unbounded;font-weight:700;font-size:21px;display:block}
.sc .ov p{font-size:12.8px;color:#C8C1B3;margin-top:4px}
.sc .pr{position:absolute;right:14px;top:14px;background:rgba(14,14,16,.6);backdrop-filter:blur(8px);color:#C9A45E;
  border:1px solid rgba(201,164,94,.5);border-radius:999px;padding:6px 12px;font-size:14px}
.sc .tg{position:absolute;left:14px;top:14px;background:#C9A45E;color:#0E0E10;border-radius:999px;padding:5px 11px;
  font-size:11px;font-weight:600;letter-spacing:.14em}
"""

SKYLINE = ('<svg class="sk" viewBox="0 0 390 120" fill="none" stroke="#C9A45E" stroke-width="1">'
           '<path d="M0 118h40V78h22V18h30v80h26V-12h34v130h30V48h28v40h36V-2h26v60h30V28h22v90h30"/></svg>')


def home_r360(s):
    gb = [("cal", "Rezervasyon", "Teras · 18:00–02:00"), ("star", "Yorum", "4,8 ★ · 1.390"),
          ("camera", "Instagram", "@rooftop360")]
    g = "".join(f'<a href="#">{icon(k)}<b>{e(t)}</b><small>{e(sub)}</small></a>' for k, t, sub in gb)
    body = (f'<div class="nt">{SKYLINE}<div class="tt"><b>360°</b><span>ROOFTOP · KOKTEYL &amp; MUTFAK</span></div>'
            f'<div class="ring"><img src="{img("icki_negroni")}" alt=""><em>MASA 21</em></div>'
            f'<nav class="gb"><a class="p" href="menu.html">{icon("menu")}<b>MENÜ</b><small>İmza kokteyller</small></a>'
            f'{g}</nav></div>')
    return page(s["name"], R360_CSS, body)


def menu_r360(s):
    stc = [("icki_negroni", "İmza"), ("icki_gunbatimi", "Klasik"), ("icki_oldfashioned", "Viski"),
           ("slider", "Tabaklar"), ("icki_aperol", "Spritz")]
    st = "".join(f'<a><span><img src="{img(i)}" alt=""></span>{e(n)}</a>' for i, n in stc)
    cards = "".join(f'<div class="sc"><img src="{img(im)}" alt="">'
                    f'{f"<span class=tg>{e(tr_upper(tg))}</span>" if tg else ""}<span class="pr num">{e(p)}</span>'
                    f'<div class="ov"><b>{e(n)}</b><p>{e(d)}</p></div></div>' for _, (n, d, p, tg, im) in items(s))
    body = f'<div class="mt"><b>360°</b><span>MASA 21</span></div><div class="st">{st}</div>{cards}'
    return page(s["name"] + " · Menü", R360_CSS, body)


# ================================================================ veriler (ad, açıklama, fiyat, etiket, fotoğraf)

SITES = [
    dict(slug="kaleici", name="Kaleiçi Sofrası", no=1, home=home_kaleici, menu_fn=menu_kaleici,
         stil="saray menüsü, kemerli fotoğraf", tabs=[],
         menu=[("Ana yemekler", [("Hünkâr beğendi", "Közlenmiş patlıcan beğendi, kuzu tas kebabı", "540 ₺", "Şef", "hunkar"),
                                 ("Kuzu tandır", "12 saat taş fırında, iç pilav ile", "620 ₺", None, None),
                                 ("Ali Nazik", "Yoğurtlu közlenmiş patlıcan, kuzu kıyma", "480 ₺", None, None),
                                 ("Etli yaprak sarma", "Ekşi erik ve tereyağı ile", "360 ₺", None, None)]),
               ("Mezeler", [("Haydari", "Süzme yoğurt, nane, sarımsak", "140 ₺", None, None),
                            ("Muhammara", "Ceviz, közlenmiş biber, nar ekşisi", "160 ₺", None, None)]),
               ("Tatlılar", [("Saray helvası", "Fıstıklı, kaymaklı", "220 ₺", None, None),
                             ("Kazandibi", "Tarçın ile", "180 ₺", None, None)])]),
    dict(slug="lagun", name="Mavi Lagün", no=2, home=home_lagun, menu_fn=menu_lagun,
         stil="tam genişlikte fotoğraf, resimli liste", tabs=["Sıcaklar", "Mezeler", "Balıklar", "Tatlı"],
         menu=[("Sıcaklar", [("Kalamar tava", "Çıtır halka, tarator sos", "420 ₺", None, "balik_kalamar"),
                             ("Karides güveç", "Kaşarlı, tereyağlı, toprak kapta", "480 ₺", "Şef", "balik_guvec")]),
               ("Mezeler", [("Deniz börülcesi", "Zeytinyağı, sarımsak", "220 ₺", None, None),
                            ("Levrek marin", "Limon, roka, pembe biber", "340 ₺", None, None),
                            ("Fava", "Kırmızı soğan, dereotu", "180 ₺", None, None)])]),
    dict(slug="forno", name="Forno Rosso", no=3, home=home_forno, menu_fn=menu_forno,
         stil="büyük kart, fotoğraflı ızgara", tabs=["Pizzalar", "Makarnalar", "Salatalar", "Tatlılar"],
         menu=[("Pizzalar", [("Margherita", "San Marzano domates, fior di latte, fesleğen", "380 ₺", None,
                              "pizza_margherita"),
                             ("Diavola", "Acı salam, mozzarella, pul biber", "440 ₺", "Acı", "pizza_diavola"),
                             ("Quattro formaggi", "Dört peynir, bal, ceviz", "460 ₺", None, "pizza_formaggi"),
                             ("Tartufo e funghi", "Trüf kreması, mantar, parmesan", "520 ₺", "Yeni", "pizza_tartufo")])]),
    dict(slug="garaj", name="Garaj Burger", no=4, home=home_garaj, menu_fn=menu_garaj,
         stil="poster, büyük fotoğraf kartları", tabs=["Burgerler", "Yanlar", "Shake", "İçecek"],
         menu=[("Burgerler", [("Double smash", "2 × 90 g dana, cheddar, karamelize soğan, turşu", "460 ₺", "Klasik",
                               "burger_smash"),
                              ("Truffle", "180 g dana, trüf mayonez, mantar, gravyer", "520 ₺", None, "burger_truffle"),
                              ("Hot chick", "Çıtır tavuk, acı bal, turşu", "390 ₺", "Acı", "burger_chick"),
                              ("Veggie", "Nohut köftesi, avokado, mor soğan", "360 ₺", "Vegan", "burger_veggie")])]),
    dict(slug="kopuk", name="Köpük", no=6, home=home_kopuk, menu_fn=menu_kopuk,
         stil="uygulama: kaydırmalı kartlar, sepet", tabs=["Espresso bar", "Demleme", "Tatlılar", "Kahvaltı"],
         menu=[("Espresso bar", [("Espresso", "Tek ya da çift shot", "90 ₺", None, "kahve_espresso"),
                                 ("Flat white", "Çift ristretto, ipeksi süt", "140 ₺", None, "kahve_flatwhite"),
                                 ("Fıstıklı latte", "Antep fıstığı ezmesi", "165 ₺", "Yeni", "kahve_fistik"),
                                 ("Türk kahvesi", "Lokum ve su ile", "95 ₺", None, "kahve_turk")]),
               ("Tatlılar", [("San Sebastian", "Yanık cheesecake, böğürtlen sos", "210 ₺", None, "kahve_cheesecake")])]),
    dict(slug="koi", name="Koi", no=10, home=home_koi, menu_fn=menu_koi,
         stil="Japon minimali, zikzak fotoğraflar", tabs=["Sushi", "Ramen", "İzakaya", "Tatlı"],
         menu=[("Sushi", [("Sake nigiri", "Somon, 3 adet, wasabi ve zencefil", "220 ₺", None, "susi_nigiri"),
                          ("Dragon roll", "Karides tempura, avokado, unagi sos", "420 ₺", "Şef", "susi_dragon"),
                          ("Spicy tuna", "Ton balığı, acı mayonez, 6 adet", "380 ₺", "Acı", "susi_spicy")]),
               ("Ramen", [("Tonkotsu", "18 saat kemik suyu, chashu, yumurta", "460 ₺", None, "susi_ramen")])]),
    dict(slug="asma", name="Asmaaltı", no=13, home=home_asma, menu_fn=menu_asma,
         stil="kara tahta, el yazısı, polaroid", tabs=[],
         menu=[("Sıcak", [("Çay", "ince belli bardakta", "25 ₺", None, "cay"),
                          ("Bitki çayı", "ıhlamur, adaçayı, kuşburnu", "60 ₺", None, None),
                          ("Sahlep", "tarçınlı", "90 ₺", None, None)]),
               ("Atıştırmalık", [("Gözleme", "peynirli, ıspanaklı ya da kıymalı", "160 ₺", None, "gozleme"),
                                 ("Kaşarlı tost", "köy ekmeğiyle", "120 ₺", None, "tost")])]),
    dict(slug="kasap", name="Kasaphane", no=14, home=home_kasap, menu_fn=menu_kasap,
         stil="tam ekran fotoğraf, dergi menüsü", tabs=[],
         menu=[("Kesimler", [("Dana antrikot", "28 gün dinlendirilmiş", "100 g 480 ₺", None, "et_antrikot"),
                             ("Bonfile", "Tereyağı, kekik", "100 g 560 ₺", None, None),
                             ("Kuzu pirzola", "Kekik, deniz tuzu", "100 g 420 ₺", None, None)]),
               ("Izgara", [("Pirzola", "", "420 ₺", None, "et_pirzola"),
                           ("Köfte", "", "540 ₺", None, "et_kofte"),
                           ("Adana", "", "560 ₺", None, "et_adana")])]),
    dict(slug="palmiye", name="Palmiye", no=16, home=home_palmiye, menu_fn=menu_palmiye,
         stil="gün batımı, taşlı kartlar", tabs=["Kokteyller", "Bowl", "Pizza", "Tatlı"],
         menu=[("Kokteyller", [("Aperol spritz", "Prosecco, soda, portakal", "420 ₺", None, "icki_aperol"),
                               ("Mojito", "Taze nane, lime, kırık buz", "380 ₺", None, "icki_mojito"),
                               ("Virgin colada", "Ananas, hindistancevizi", "260 ₺", "Alkolsüz", "icki_colada")]),
               ("Bowl", [("Poke bowl", "Somon, avokado, edamame, mango", "460 ₺", "Yeni", "poke_bowl")])]),
    dict(slug="r360", name="Rooftop 360", no=27, home=home_r360, menu_fn=menu_r360,
         stil="gece, cam düğmeler, hikâye kartları", tabs=[],
         menu=[("İmza kokteyller", [("360 Negroni", "Gin, vermut, bitter, portakal kabuğu", "560 ₺", "İmza",
                                     "icki_negroni"),
                                    ("Smoked old fashioned", "Burbon, akçaağaç, tütsü", "580 ₺", None, "icki_oldfashioned"),
                                    ("Gün batımı", "Tekila, kan portakalı, agave", "520 ₺", None, "icki_gunbatimi")]),
               ("Tabaklar", [("Wagyu slider", "3 adet, trüf mayonez", "640 ₺", None, "slider")])]),
]


def shoot(sites):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        exe = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
        br = pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()
        ctx = br.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        pg = ctx.new_page()
        for s in sites:
            d = os.path.join(OUT, s["slug"])
            for f, out in (("index.html", "ekran_ana.png"), ("menu.html", "ekran_menu.png")):
                pg.goto("file://" + os.path.join(d, f))
                pg.wait_for_load_state("load")
                pg.evaluate("document.fonts.ready")
                pg.wait_for_timeout(250)
                pg.screenshot(path=os.path.join(d, out))
        br.close()


def main():
    only = sys.argv[1:]
    sites = [s for s in SITES if not only or s["slug"] in only]
    for s in sites:
        d = os.path.join(OUT, s["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(s["home"](s))
        open(os.path.join(d, "menu.html"), "w", encoding="utf-8").write(s["menu_fn"](s))
    shoot(sites)
    print(f"{len(sites)} site yazıldı ve görüntülendi")


if __name__ == "__main__":
    main()
