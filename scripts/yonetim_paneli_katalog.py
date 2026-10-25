"""Menü yönetim paneli – müşteri kataloğu.

QR masalıkların arkasındaki sistemin yönetim paneli: gösterge paneli (okutma, menü görüntüleme, Google yorumuna
yönlendirme), menü düzenleme (ürün, fotoğraf, fiyat, tükendi, toplu zam, dil), işletme bilgileri ve tema, masalar ve
QR'lar, sipariş ekranı (sipariş paketi). Ekranlar tasarım prototipidir (HTML); örnek işletme katalogdaki Palmiye
beach club, ürünler ve rakamlar örnektir.

Çıktı : yonetim_paneli/katalog.pdf, katalog_01..NN.jpg, ekranlar/*.html ve *.png

Kullanım:
  python3 scripts/yonetim_paneli_katalog.py
"""
import html
import os
import sys

import segno
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import menu_siteleri as MS  # noqa: E402
import restoran_masalik as R  # noqa: E402

ROOT = MS.ROOT
OUT = os.path.join(ROOT, "yonetim_paneli")
SCR = os.path.join(OUT, "ekranlar")
SITES = os.path.relpath(MS.OUT, SCR)                       # ekranlar/ → restoran_masalik/siteler
FONTS = MS.FONTS.replace("url(../fonts/", f"url({SITES}/fonts/")
PANEL_URL = "panel.qrsistem.workers.dev"
BIZ_URL = "palmiye.qrsistem.workers.dev"


def img(name):
    return f"{SITES}/img/{name}.jpg"


def e(s):
    return html.escape(str(s))


ICON = dict(MS.ICON)
ICON.update({
    "grid": '<rect x="4" y="4" width="7" height="7" rx="2"/><rect x="13" y="4" width="7" height="7" rx="2"/>'
            '<rect x="4" y="13" width="7" height="7" rx="2"/><rect x="13" y="13" width="7" height="7" rx="2"/>',
    "qr": '<rect x="4" y="4" width="6" height="6" rx="1"/><rect x="14" y="4" width="6" height="6" rx="1"/>'
          '<rect x="4" y="14" width="6" height="6" rx="1"/><path d="M14 14h2v2h-2zM18 18h2v2h-2zM14 19h2M19 14v2"/>',
    "palette": '<path d="M12 3.5a8.5 8.5 0 1 0 0 17c1.2 0 1.8-.8 1.8-1.7 0-1.3-1.2-1.6-1.2-2.8 0-1 .8-1.8 1.9-1.8h2.2'
               'a3.8 3.8 0 0 0 3.8-3.8C20.5 6.6 16.7 3.5 12 3.5z"/><circle cx="7.8" cy="11" r="1"/>'
               '<circle cx="10.5" cy="7.5" r="1"/><circle cx="15" cy="7.8" r="1"/>',
    "cog": '<circle cx="12" cy="12" r="3"/><path d="M12 3v2.5M12 18.5V21M3 12h2.5M18.5 12H21M5.6 5.6l1.8 1.8'
           'M16.6 16.6l1.8 1.8M5.6 18.4l1.8-1.8M16.6 7.4l1.8-1.8"/>',
    "chart": '<path d="M5 20V11M11 20V5M17 20v-7M3 20h18"/>',
    "store": '<path d="M4 9l1.5-5h13L20 9M4 9v11h16V9M4 9h16M9.5 20v-6h5v6"/>',
    "drag": '<circle cx="9" cy="6" r="1.3" fill="currentColor"/><circle cx="15" cy="6" r="1.3" fill="currentColor"/>'
            '<circle cx="9" cy="12" r="1.3" fill="currentColor"/><circle cx="15" cy="12" r="1.3" fill="currentColor"/>'
            '<circle cx="9" cy="18" r="1.3" fill="currentColor"/><circle cx="15" cy="18" r="1.3" fill="currentColor"/>',
    "edit": '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="M13.5 6.5l4 4"/>',
    "upload": '<path d="M12 16V4M7 9l5-5 5 5M4 20h16"/>',
    "globe": '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.6 2.6 2.6 14.4 0 17M12 3.5c-2.6 2.6-2.6 '
             '14.4 0 17"/>',
    "lock": '<rect x="5" y="10.5" width="14" height="10" rx="2.5"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/>',
    "eye": '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/>',
    "download": '<path d="M12 4v12M7 11l5 5 5-5M4 20h16"/>',
    "back": '<path d="M15 5l-7 7 7 7"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "percent": '<path d="M19 5L5 19"/><circle cx="7" cy="7" r="2.5"/><circle cx="17" cy="17" r="2.5"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "sound": '<path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z"/><path d="M15.5 9a4 4 0 0 1 0 6M18 6.5a7.5 7.5 0 0 1 0 11"/>',
    "down": '<path d="M6 9l6 6 6-6"/>',
    "bolt": '<path d="M13 3L5 13.5h6L10 21l9-11h-6z"/>',
    "image": '<rect x="3.5" y="5" width="17" height="14" rx="2.5"/><circle cx="9" cy="10" r="1.8"/>'
             '<path d="M4 17l5-4.5 4 3.5 3-2.5 4 3.5"/>',
    "users": '<circle cx="9" cy="8.5" r="3.2"/><path d="M3.5 19c.8-3.3 3-4.8 5.5-4.8s4.7 1.5 5.5 4.8"/>'
             '<path d="M15.5 5.5a3 3 0 0 1 0 6M17.5 14.5c1.6.6 2.6 2 3 4.5"/>',
    "shield": '<path d="M12 3.5l7 2.8v5.2c0 4.4-3 7.8-7 9-4-1.2-7-4.6-7-9V6.3z"/><path d="M8.8 12l2.2 2.2 4.2-4.4"/>',
})


def ic(k, cls="", sw=1.8):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICON[k]}</svg>')


# ================================================================ panel arayüzü

PANEL_CSS = """
:root{--ink:#17191F;--bg:#F4F1EA;--line:#E6E0D4;--muted:#7D776C;--acc:#C8963E;--navy:#1D2742;--ok:#2E8B57;
  --bad:#C4473B;--soft:#FBF8F2}
body{background:var(--bg);color:var(--ink);font-size:15px}
.app{display:grid;grid-template-columns:250px 1fr;height:900px;overflow:hidden}
.side{background:#15171C;color:#D9D3C7;padding:22px 16px;display:flex;flex-direction:column}
.logo{display:flex;align-items:center;gap:10px;font-family:Fraunces;font-weight:700;font-size:21px;color:#fff;padding:0 6px}
.logo i{width:36px;height:36px;border-radius:11px;background:var(--acc);display:grid;place-items:center;color:#15171C}
.logo i svg{width:22px;height:22px}
.biz{margin:22px 0 14px;padding:11px 12px;border-radius:14px;background:#1F2229;display:flex;align-items:center;gap:11px}
.av{width:38px;height:38px;border-radius:50%;background:linear-gradient(#2B3A6B,#C9667A 60%,#F2A86C);display:grid;
  place-items:center;font-family:Norican;font-size:21px;color:#fff;flex:none}
.biz b{display:block;color:#fff;font-weight:600;font-size:14.5px}
.biz small{font-size:12px;color:#9C968A}
.biz svg{margin-left:auto;width:16px;height:16px;color:#9C968A}
.nav{display:grid;gap:3px}
.nav h6{font-size:10.5px;letter-spacing:.2em;color:#6E695F;margin:14px 12px 6px;font-weight:600}
.nav a{display:flex;align-items:center;gap:12px;padding:10px 12px;border-radius:10px;font-size:15px;color:#B5AFA3}
.nav a svg{width:20px;height:20px}
.nav a.on{background:#2A2E37;color:#fff}
.nav a em{margin-left:auto;font-style:normal;background:var(--bad);color:#fff;border-radius:999px;font-size:11.5px;
  font-weight:600;padding:1px 8px}
.me{margin-top:auto;display:flex;gap:10px;align-items:center;padding:12px 8px 0;border-top:1px solid #262930;font-size:13.5px}
.me .a2{width:34px;height:34px;border-radius:50%;background:var(--acc);color:#15171C;display:grid;place-items:center;
  font-weight:700}
.me small{display:block;color:#8C8679;font-size:12px}
.main{padding:22px 30px;overflow:hidden}
.top{display:flex;align-items:center;gap:12px;margin-bottom:18px}
.top h1{font-family:Fraunces;font-weight:700;font-size:30px;letter-spacing:-.01em;line-height:1.1}
.top .sub{color:var(--muted);font-size:14px;margin-top:3px}
.sp{flex:1}
.btn{display:inline-flex;align-items:center;gap:8px;padding:10px 16px;border-radius:12px;border:1px solid var(--line);
  background:#fff;font-weight:500;font-size:14.5px;white-space:nowrap}
.btn svg{width:18px;height:18px}
.btn.p{background:var(--ink);color:#fff;border-color:var(--ink)}
.btn.a{background:var(--acc);color:#fff;border-color:var(--acc)}
.card{background:#fff;border:1px solid var(--line);border-radius:18px;padding:18px 20px}
.card h3{font-size:15.5px;font-weight:600;display:flex;align-items:center;gap:8px;margin-bottom:12px}
.card h3 small{margin-left:auto;font-weight:400;color:var(--muted);font-size:13px}
.card h3 svg{width:19px;height:19px;color:var(--acc);flex:none}
.chip{display:inline-block;padding:3px 9px;border-radius:999px;font-size:11.5px;font-weight:600;background:#F2ECE0;
  color:#7A5A22;margin-right:4px}
.chip.g{background:#E5F2EA;color:#24704A}.chip.r{background:#F8E4E1;color:#A3372D}.chip.n{background:#E6E9F2;color:#1D2742}
.tog{width:42px;height:24px;border-radius:999px;background:var(--ok);position:relative;flex:none;display:inline-block}
.tog:after{content:"";position:absolute;right:3px;top:3px;width:18px;height:18px;border-radius:50%;background:#fff}
.tog.off{background:#CFC8BA}.tog.off:after{right:auto;left:3px}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.kpi .l{color:var(--muted);font-size:13.5px;display:flex;align-items:center;gap:8px}
.kpi .l svg{width:18px;height:18px;color:var(--acc)}
.kpi .v{font-family:Manrope;font-weight:600;font-size:32px;margin-top:6px;letter-spacing:-.01em}
.kpi .d{font-size:12.5px;color:var(--ok);margin-top:2px}
.g2{display:grid;grid-template-columns:1.55fr 1fr;gap:14px;margin-top:14px}
.heat{display:grid;grid-template-columns:repeat(6,1fr);gap:6px}
.heat span{border-radius:8px;height:40px;display:grid;place-items:center;font-size:11.5px;font-weight:600}
.top5 .r{display:flex;align-items:center;gap:12px;padding:7px 0}
.top5 img{width:42px;height:42px;border-radius:10px;object-fit:cover}
.top5 b{font-weight:600;font-size:14.5px;display:block}
.top5 i{display:block;height:6px;border-radius:3px;background:#F0EADF;margin-top:5px;width:150px}
.top5 i u{display:block;height:100%;border-radius:3px;background:var(--acc)}
.top5 .num{margin-left:auto;font-size:14px}
.log .r{display:flex;gap:10px;align-items:flex-start;padding:7px 0;border-bottom:1px solid #F0EBE1;font-size:13.5px}
.log .r:last-child{border:0}
.log .d{width:8px;height:8px;border-radius:50%;background:var(--acc);margin-top:6px;flex:none}
.log small{display:block;color:var(--muted);font-size:12px}
.banner{display:flex;align-items:center;gap:14px;background:var(--navy);color:#F4EDE1;border-radius:18px;padding:14px 20px;
  margin-top:14px}
.banner b{font-family:Fraunces;font-size:26px}.banner span{color:#E2B86A;letter-spacing:2px}
.banner small{color:#C9C5D6}
"""


def sidebar(active, orders=3):
    items = [("home", "Gösterge paneli"), ("menu", "Menü"), ("qr", "Masalar ve QR"), ("store", "İşletme bilgileri"),
             ("palette", "Tema"), ("chart", "İstatistik")]
    nav = "".join(f'<a class="{"on" if t == active else ""}">{ic(k)}{e(t)}</a>' for k, t in items)
    nav += (f'<h6>SİPARİŞ PAKETİ</h6><a class="{"on" if active == "Siparişler" else ""}">{ic("bag")}Siparişler'
            f'<em>{orders}</em></a><a>{ic("bell")}Garson çağrıları</a>'
            f'<h6>HESAP</h6><a>{ic("users")}Kullanıcılar</a><a>{ic("cog")}Ayarlar</a>')
    return (f'<aside class="side"><div class="logo"><i>{ic("qr", sw=2.2)}</i>QR Sistem</div>'
            f'<div class="biz"><span class="av">P</span><span><b>Palmiye</b><small>Beach club · Lara</small></span>'
            f'{ic("down")}</div><nav class="nav">{nav}</nav>'
            f'<div class="me"><span class="a2">E</span><span>Elif Kaya<small>Yönetici</small></span></div></aside>')


def panel_page(title, css, body):
    return (f'<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>{e(title)}</title><style>{FONTS}'
            f'{MS.RESET}{PANEL_CSS}{css}</style></head><body>{body}</body></html>')


def bars_svg(vals, labels, w=560, h=190, peak=None):
    n = len(vals)
    mx = max(vals)
    bw = w / n
    out = [f'<svg viewBox="0 -24 {w} {h + 50}" width="100%" height="{h + 50}">']
    for k, (v, lab) in enumerate(zip(vals, labels)):
        bh = (h - 10) * v / mx
        x = k * bw + bw * 0.18
        col = "#C8963E" if k == peak else "#E8DCC4"
        out.append(f'<rect x="{x:.1f}" y="{h - bh:.1f}" width="{bw * 0.64:.1f}" height="{bh:.1f}" rx="5" fill="{col}"/>')
        if k % 2 == 0:
            out.append(f'<text x="{x + bw * 0.32:.1f}" y="{h + 18}" font-size="11.5" fill="#7D776C" '
                       f'text-anchor="middle" font-family="Jost">{lab}</text>')
    if peak is not None:
        x = peak * bw + bw / 2
        out.append(f'<text x="{x:.1f}" y="{h - (h - 10) * vals[peak] / mx - 8:.1f}" font-size="12.5" fill="#17191F" '
                   f'text-anchor="middle" font-family="Manrope" font-weight="600">{vals[peak]}</text>')
    return "".join(out) + "</svg>"


def dashboard():
    hours = list(range(9, 25))
    vals = [6, 9, 14, 22, 31, 38, 35, 29, 27, 33, 41, 46, 39, 24, 15, 9]
    kpis = [("qr", "Bugün QR okutma", "342", "▲ %18 geçen haftaya göre"),
            ("eye", "Menü görüntüleme", "1.208", "▲ %11"),
            ("star", "Google yorumuna giden", "46", "bu ay 381"),
            ("clock", "Ortalama inceleme", "2 dk 40 sn", "menüde geçen süre")]
    k = "".join(f'<div class="card kpi"><div class="l">{ic(i)}{e(a)}</div><div class="v">{e(b)}</div>'
                f'<div class="d">{e(c)}</div></div>' for i, a, b, c in kpis)
    heat_vals = [4, 9, 14, 21, 18, 7, 12, 25, 31, 16, 8, 5, 11, 19, 27, 22, 13, 6, 3, 8, 15, 10, 6, 2]
    cells = []
    for i, v in enumerate(heat_vals, 1):
        a = v / 31
        bg = f"rgba(200,150,62,{0.12 + 0.88 * a:.2f})"
        fg = "#fff" if a > 0.55 else "#5C4A2A"
        cells.append(f'<span style="background:{bg};color:{fg}">{i:02d}</span>')
    tops = [("icki_aperol", "Aperol spritz", 412), ("poke_bowl", "Poke bowl", 296), ("icki_mojito", "Mojito", 251),
            ("pizza_margherita", "Margherita", 188), ("kahve_cheesecake", "San Sebastian", 142)]
    t = "".join(f'<div class="r"><img src="{img(i)}"><span><b>{e(n)}</b><i><u style="width:{v / 4.12:.0f}%"></u></i>'
                f'</span><span class="num">{v}</span></div>' for i, n, v in tops)
    logs = [("Mojito → Tükendi", "Elif · bugün 14:05"), ("Kokteyl fiyatları %10 güncellendi", "Mert · dün 11:20"),
            ("Yeni ürün: Poke bowl (fotoğraflı)", "Elif · 2 gün önce"), ("Wi-Fi şifresi değişti", "Mert · 5 gün önce")]
    lg = "".join(f'<div class="r"><span class="d"></span><span>{e(a)}<small>{e(b)}</small></span></div>' for a, b in logs)
    body = (f'<div class="app">{sidebar("Gösterge paneli")}<main class="main">'
            f'<div class="top"><div><h1>Günaydın, Elif</h1><div class="sub">Cumartesi, 14 Haziran · Palmiye bugün '
            f'09:00–01:00 açık</div></div><span class="sp"></span><span class="btn">{ic("eye")}Siteyi gör</span>'
            f'<span class="btn a">{ic("plus", sw=2.2)}Ürün ekle</span></div>'
            f'<div class="kpis">{k}</div>'
            f'<div class="g2"><div class="card"><h3>Saatlere göre okutma<small>bugün · en yoğun 20:00</small></h3>'
            f'{bars_svg(vals, [f"{h_:02d}" for h_ in hours], peak=11)}</div>'
            f'<div class="card"><h3>Şezlonglara göre<small>bugün</small></h3><div class="heat">{"".join(cells)}</div>'
            f'</div></div>'
            f'<div class="g2"><div class="card top5"><h3>En çok bakılan ürünler<small>son 7 gün</small></h3>{t}</div>'
            f'<div class="card log"><h3>Son değişiklikler</h3>{lg}</div></div>'
            f'</main></div>')
    return panel_page("Gösterge paneli", "", body)


MENU_CSS = """
.cols{display:grid;grid-template-columns:230px 1fr 300px;gap:14px;height:770px}
.cats .c{display:flex;align-items:center;gap:10px;padding:11px 10px;border-radius:12px;font-size:15px}
.cats .c svg{width:16px;height:16px;color:#B3AC9E}
.cats .c small{margin-left:auto;color:var(--muted);font-family:Manrope;font-weight:600}
.cats .c.on{background:#F6EFE2;font-weight:600}
.cats .add{color:var(--acc);font-weight:600;padding:12px 10px;font-size:14.5px}
.items .hd{display:flex;align-items:center;gap:10px;margin-bottom:6px}
.items .hd b{font-family:Fraunces;font-size:22px}
.items .hd .lang{margin-left:auto;display:flex;gap:4px}
.items .hd .lang span{padding:5px 9px;border-radius:8px;font-size:12.5px;font-weight:600;color:var(--muted)}
.items .hd .lang span.on{background:var(--ink);color:#fff}
.it{display:flex;align-items:center;gap:14px;padding:11px 4px;border-bottom:1px solid #F0EBE1}
.it>svg{width:18px;height:18px;color:#C1BAAC;flex:none}
.it img{width:58px;height:58px;border-radius:12px;object-fit:cover;flex:none}
.it .t{flex:1;min-width:0}
.it .t b{font-weight:600;font-size:15.5px}
.it .t p{color:var(--muted);font-size:13px;margin:2px 0 4px}
.it .pr{width:104px;border:1px solid var(--line);border-radius:10px;padding:8px 10px;font-family:Manrope;font-weight:600;
  font-size:14.5px;text-align:right;flex:none}
.it .st{width:92px;font-size:12px;color:var(--muted);display:flex;flex-direction:column;align-items:center;gap:4px;flex:none}
.it .ed{width:36px;height:36px;border-radius:10px;border:1px solid var(--line);display:grid;place-items:center;flex:none}
.it .ed svg{width:17px;height:17px}
.it.out img{filter:grayscale(1);opacity:.6}
.prev{display:flex;flex-direction:column;align-items:center}
.prev h3{width:100%}
.ph{width:262px;height:566px;border-radius:38px;background:#16161A;padding:9px;box-shadow:0 18px 40px rgba(0,0,0,.18)}
.ph .sc{width:244px;height:548px;border-radius:30px;overflow:hidden;position:relative}
.ph iframe{width:390px;height:877px;border:0;transform:scale(.6256);transform-origin:0 0}
.live{margin-top:12px;display:flex;align-items:center;gap:8px;font-size:13px;color:var(--ok);font-weight:600}
.live i{width:9px;height:9px;border-radius:50%;background:var(--ok);box-shadow:0 0 0 4px rgba(46,139,87,.18)}
"""

COCKTAILS = [("icki_aperol", "Aperol spritz", "Prosecco, soda, portakal", "420", ["Çok satan"], True),
             ("icki_mojito", "Mojito", "Taze nane, lime, kırık buz", "380", [], False),
             ("icki_colada", "Virgin colada", "Ananas, hindistancevizi", "260", ["Alkolsüz"], True),
             ("icki_negroni", "Negroni", "Gin, vermut, bitter", "520", [], True),
             ("icki_gunbatimi", "Gün batımı", "Tekila, kan portakalı, agave", "450", ["Yeni"], True),
             ("icki_oldfashioned", "Old fashioned", "Burbon, akçaağaç, portakal", "480", [], True)]


def menu_admin():
    cats = [("Kokteyller", 6), ("Bowl", 3), ("Pizza", 4), ("Burger", 2), ("Tatlı", 3), ("Kahve", 4)]
    c = "".join(f'<div class="c{" on" if k == 0 else ""}">{ic("drag")}{e(n)}<small>{v}</small></div>'
                for k, (n, v) in enumerate(cats))
    rows = []
    for im, n, d, p, tags, on in COCKTAILS:
        tg = "".join(f'<span class="chip{" g" if t == "Alkolsüz" else ""}">{e(t)}</span>' for t in tags)
        if not on:
            tg += '<span class="chip r">Tükendi</span>'
        rows.append(f'<div class="it{"" if on else " out"}">{ic("drag")}<img src="{img(im)}"><div class="t"><b>{e(n)}</b>'
                    f'<p>{e(d)}</p>{tg}</div><span class="pr">{p} ₺</span><span class="st"><span class="tog'
                    f'{"" if on else " off"}"></span>{"Satışta" if on else "Tükendi"}</span>'
                    f'<span class="ed">{ic("edit")}</span></div>')
    body = (f'<div class="app">{sidebar("Menü")}<main class="main">'
            f'<div class="top"><div><h1>Menü</h1><div class="sub">6 kategori · 22 ürün · son güncelleme 14:05</div>'
            f'</div><span class="sp"></span><span class="btn">{ic("percent")}Toplu fiyat</span>'
            f'<span class="btn">{ic("upload")}Menü içe aktar</span>'
            f'<span class="btn a">{ic("plus", sw=2.2)}Ürün ekle</span></div>'
            f'<div class="cols"><div class="card cats"><h3>Kategoriler</h3>{c}<div class="add">+ Kategori ekle</div>'
            f'</div><div class="card items"><div class="hd"><b>Kokteyller</b><span class="chip n">'
            f'12:00–01:00 arası</span><span class="lang"><span class="on">TR</span><span>EN</span><span>RU</span>'
            f'<span>DE</span></span></div>{"".join(rows)}</div>'
            f'<div class="card prev"><h3>Canlı önizleme</h3><div class="ph"><div class="sc">'
            f'<iframe src="palmiye_tukendi.html" scrolling="no"></iframe></div></div>'
            f'<div class="live"><i></i>Yayında · anında görünür</div></div></div>'
            f'</main></div>')
    return panel_page("Menü", MENU_CSS, body)


MOBILE_CSS = """
body{background:#fff}
.mt{display:flex;align-items:center;justify-content:space-between;padding:16px 18px;border-bottom:1px solid var(--line)}
.mt a{display:flex;align-items:center;gap:4px;color:var(--muted);font-size:15px}
.mt a svg{width:20px;height:20px}
.mt b{font-weight:600;font-size:16.5px}
.mt span{color:var(--acc);font-weight:600}
.fm{padding:16px 18px 120px}
.photo{position:relative;border-radius:18px;overflow:hidden;height:150px}
.photo img{width:100%;height:100%;object-fit:cover}
.photo span{position:absolute;right:12px;bottom:12px;background:rgba(23,25,31,.78);color:#fff;border-radius:10px;
  padding:8px 12px;font-size:13.5px;display:flex;gap:6px;align-items:center}
.photo span svg{width:16px;height:16px}
label{display:block;font-size:12.5px;color:var(--muted);margin:14px 0 6px;font-weight:500}
.in{border:1px solid var(--line);border-radius:12px;padding:12px 14px;font-size:15.5px;background:var(--soft)}
.in.ta{min-height:64px;line-height:1.4}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.chips span{display:inline-block;padding:7px 12px;border-radius:999px;border:1px solid var(--line);font-size:13.5px;
  margin:0 6px 6px 0}
.chips span.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.sw{display:flex;align-items:center;justify-content:space-between;border:1px solid var(--line);border-radius:14px;
  padding:13px 14px;margin-top:14px;font-size:15px}
.sw small{display:block;color:var(--muted);font-size:12.5px}
.save{position:fixed;left:16px;right:16px;bottom:22px;background:var(--ink);color:#fff;border-radius:16px;padding:16px;
  text-align:center;font-weight:600;font-size:16px}
.lng{display:flex;gap:6px}
.lng span{flex:1;text-align:center;padding:8px 0;border-radius:10px;border:1px solid var(--line);font-size:13px;font-weight:600}
.lng span.on{background:var(--acc);border-color:var(--acc);color:#fff}
.pct{display:flex;align-items:center;justify-content:space-between;border:1px solid var(--line);border-radius:16px;padding:6px}
.pct span{width:52px;height:52px;border-radius:12px;background:var(--soft);display:grid;place-items:center;font-size:24px}
.pct b{font-family:Manrope;font-weight:600;font-size:34px}
.pv .r{display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid #F0EBE1}
.pv img{width:44px;height:44px;border-radius:10px;object-fit:cover}
.pv b{flex:1;font-weight:600;font-size:15px}
.pv s{color:var(--muted);font-family:Manrope;font-size:14px}
.pv .num{font-size:15px;color:var(--ok)}
.pv .ar{color:#C1BAAC}
"""


def item_edit():
    body = (f'<div class="mt"><a>{ic("back")}Kokteyller</a><b>Ürünü düzenle</b><span>Kaydet</span></div>'
            f'<div class="fm"><div class="photo"><img src="{img("icki_aperol")}"><span>{ic("image")}Fotoğrafı değiştir'
            f'</span></div><label>Dil</label><div class="lng"><span class="on">TR</span><span>EN</span><span>RU</span>'
            f'<span>DE</span></div>'
            f'<label>Ürün adı</label><div class="in">Aperol spritz</div>'
            f'<label>Açıklama</label><div class="in ta">Prosecco, soda, portakal dilimi. Gün batımında en çok tercih '
            f'edilen.</div><div class="row2"><div><label>Fiyat</label><div class="in num">420 ₺</div></div>'
            f'<div><label>Kategori</label><div class="in">Kokteyller</div></div></div>'
            f'<label>Etiketler</label><div class="chips"><span class="on">Çok satan</span><span>Yeni</span>'
            f'<span>Şefin önerisi</span><span>Alkolsüz</span><span>Vegan</span></div>'
            f'<label>Alerjenler</label><div class="chips"><span>Gluten</span><span>Süt</span><span class="on">Sülfit</span>'
            f'<span>Kuruyemiş</span></div>'
            f'<div class="sw"><span>Satışta<small>Kapatınca menüde “Tükendi” yazar</small></span><span class="tog"></span>'
            f'</div></div><div class="save">Kaydet ve yayınla</div>')
    return panel_page("Ürünü düzenle", MOBILE_CSS, body)


def bulk_price():
    def r10(p):
        return int(p * 1.1 / 10 + 0.5) * 10
    rows = "".join(f'<div class="r"><img src="{img(im)}"><b>{e(n)}</b><s>{p} ₺</s><span class="ar">→</span>'
                   f'<span class="num">{r10(int(p))} ₺</span></div>' for im, n, _, p, _, _ in COCKTAILS)
    body = (f'<div class="mt"><a>{ic("back")}Menü</a><b>Toplu fiyat</b><span></span></div>'
            f'<div class="fm"><label>Kategoriler</label><div class="chips"><span class="on">✓ Kokteyller</span>'
            f'<span>Bowl</span><span>Pizza</span><span>Burger</span><span>Tatlı</span><span>Kahve</span></div>'
            f'<label>Değişim</label><div class="pct"><span>−</span><b>+ %10</b><span>+</span></div>'
            f'<label>Yuvarlama</label><div class="chips"><span>Yok</span><span>5 ₺</span><span class="on">10 ₺</span>'
            f'<span>,90</span></div><label>Önizleme · 6 ürün</label><div class="pv">{rows}</div></div>'
            f'<div class="save">6 ürüne uygula</div>')
    return panel_page("Toplu fiyat", MOBILE_CSS, body)


def login():
    css = """
.lg{padding:70px 26px 0;text-align:center}
.lg .logo{justify-content:center;color:var(--ink);font-size:26px}
.lg .logo i{width:46px;height:46px;border-radius:14px}
.lg h1{font-family:Fraunces;font-size:30px;margin-top:40px}
.lg p{color:var(--muted);margin-top:6px}
.lg .in{text-align:left;margin-top:14px}
.lg .btn2{margin-top:18px;background:var(--ink);color:#fff;border-radius:14px;padding:16px;font-weight:600}
.lg .two{margin-top:22px;display:flex;align-items:center;gap:10px;justify-content:center;color:var(--muted);font-size:13.5px}
.lg .two svg{width:18px;height:18px;color:var(--ok)}
.lg .code{display:flex;gap:10px;justify-content:center;margin-top:12px}
.lg .code span{width:44px;height:54px;border-radius:12px;border:1px solid var(--line);display:grid;place-items:center;
  font-family:Manrope;font-weight:600;font-size:22px;background:var(--soft)}
"""
    body = (f'<div class="lg"><div class="logo"><i>{ic("qr", sw=2.2)}</i>QR Sistem</div><h1>İşletme paneli</h1>'
            f'<p>Palmiye · Beach club</p><div class="in">elif@palmiye.com</div><div class="in">••••••••••</div>'
            f'<div class="btn2">Giriş yap</div><div class="two">{ic("shield")}Telefonunuza gelen kodla iki adımlı '
            f'giriş</div><div class="code"><span>4</span><span>8</span><span>1</span><span>9</span><span></span>'
            f'<span></span></div></div>')
    return panel_page("Giriş", MOBILE_CSS + css, body)


SET_CSS = """
.g3{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.f label{display:block;font-size:12.5px;color:var(--muted);margin:10px 0 5px}
.f .in{border:1px solid var(--line);border-radius:11px;padding:10px 12px;font-size:14.5px;background:var(--soft)}
.f .two{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.hrs .r{display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid #F0EBE1;font-size:14px}
.hrs .r b{font-weight:500}
.th{display:grid;grid-template-columns:repeat(5,1fr);gap:10px}
.th div{border-radius:12px;overflow:hidden;border:2px solid transparent;position:relative;height:150px}
.th div.on{border-color:var(--acc)}
.th img{width:100%;height:100%;object-fit:cover;object-position:top}
.th span{position:absolute;left:6px;bottom:6px;background:rgba(255,255,255,.92);border-radius:8px;padding:2px 7px;
  font-size:11.5px;font-weight:600}
.th div.on:after{content:"✓";position:absolute;right:6px;top:6px;width:22px;height:22px;border-radius:50%;
  background:var(--acc);color:#fff;display:grid;place-items:center;font-size:13px;font-weight:700}
.sw{display:flex;gap:8px;margin-top:10px}
.sw i{width:30px;height:30px;border-radius:50%;display:block;border:2px solid #fff;box-shadow:0 0 0 1px var(--line)}
"""


def settings():
    themes = [("kaleici", "Saray"), ("lagun", "Deniz"), ("forno", "Kartlar"), ("garaj", "Poster"), ("kopuk", "Uygulama"),
              ("koi", "Minimal"), ("asma", "Kara tahta"), ("kasap", "Tam foto"), ("palmiye", "Gün batımı"),
              ("r360", "Gece")]
    th = "".join(f'<div class="{"on" if s == "palmiye" else ""}"><img src="{SITES}/{s}/ekran_ana.png"><span>{e(n)}</span>'
                 f'</div>' for s, n in themes)
    days = [("Pazartesi – Cuma", "10:00 – 01:00"), ("Cumartesi", "09:00 – 02:00"), ("Pazar", "09:00 – 01:00"),
            ("Mutfak kapanış", "23:30"), ("Gün batımı DJ", "17:00")]
    hr = "".join(f'<div class="r"><b>{e(a)}</b><span class="num">{e(b)}</span></div>' for a, b in days)
    body = (f'<div class="app">{sidebar("İşletme bilgileri")}<main class="main">'
            f'<div class="top"><div><h1>İşletme bilgileri</h1><div class="sub">Sayfanızda ve Google yönlendirmesinde '
            f'kullanılır</div></div><span class="sp"></span><span class="btn p">{ic("check", sw=2.2)}Kaydet</span>'
            f'</div><div class="g3"><div class="card f"><h3>{ic("store")}İşletme</h3>'
            f'<div class="two"><div><label>Ad</label><div class="in">Palmiye</div></div><div><label>Alt başlık</label>'
            f'<div class="in">Beach club · Lara</div></div></div>'
            f'<div class="two"><div><label>Telefon</label><div class="in">0242 000 00 00</div></div><div><label>Instagram'
            f'</label><div class="in">@palmiyebeach</div></div></div>'
            f'<label>Google yorum bağlantısı</label><div class="in">g.page/r/palmiye-lara/review</div>'
            f'<div class="two"><div><label>Wi-Fi ağı</label><div class="in">Palmiye_Beach</div></div><div><label>'
            f'Wi-Fi şifresi</label><div class="in">••••••••</div></div></div></div>'
            f'<div class="card hrs"><h3>{ic("clock")}Çalışma saatleri</h3>{hr}'
            f'<h3 style="margin-top:16px">{ic("palette")}Renkler ve logo</h3><div class="sw">'
            + "".join(f'<i style="background:{c}"></i>' for c in ("#1D2742", "#F2A86C", "#C9667A", "#F4EDE1", "#B98A4A"))
            + f'<span class="btn" style="margin-left:auto">{ic("upload")}Logo yükle</span></div></div></div>'
            f'<div class="card" style="margin-top:14px"><h3>{ic("palette")}Tema<small>10 hazır tasarım · '
            f'renkler işletmenize göre</small></h3><div class="th">{th}</div></div>'
            f'</main></div>')
    return panel_page("İşletme bilgileri", SET_CSS, body)


TBL_CSS = """
.info{display:flex;gap:16px;align-items:center;background:#FFF8EA;border:1px solid #EFD9AE;border-radius:16px;
  padding:14px 18px;margin-bottom:14px;font-size:14px}
.info svg{width:26px;height:26px;color:var(--acc);flex:none}
.info b{font-weight:600}
.split{display:grid;grid-template-columns:1fr 330px;gap:14px}
table{width:100%;border-collapse:collapse;font-size:14.5px}
th{text-align:left;font-size:12px;letter-spacing:.06em;color:var(--muted);font-weight:500;padding:6px 8px;
  border-bottom:1px solid var(--line)}
td{padding:9px 8px;border-bottom:1px solid #F0EBE1;vertical-align:middle}
td img{width:40px;height:40px;display:block}
td .num{font-size:14.5px}
td small{color:var(--muted)}
tr.on td{background:#FBF5E8}
.dl{display:inline-flex;gap:6px;align-items:center;color:var(--acc);font-weight:600;font-size:13.5px}
.dl svg{width:16px;height:16px}
.big{text-align:center}
.big img{width:210px;height:210px;margin:6px auto 8px;display:block}
.big b{font-family:Fraunces;font-size:24px;display:block}
.big code{font-size:12.5px;color:var(--muted)}
.big .tg{display:flex;flex-direction:column;gap:8px;margin-top:14px;text-align:left}
.big .tg div{border:1px solid var(--line);border-radius:12px;padding:10px 12px;font-size:13.5px}
.big .tg small{display:block;color:var(--muted);font-size:12px}
"""


def qr_svg(url, name):
    path = os.path.join(SCR, name)
    segno.make(url, error="m").save(path, scale=6, border=2, dark="#17191F")
    return name


def tables():
    rows = []
    stats = [(1, 18, "6 dk"), (2, 9, "21 dk"), (3, 25, "2 dk"), (4, 14, "48 dk"), (5, 31, "şimdi"), (6, 11, "1 sa"),
             (7, 22, "4 dk"), (8, 7, "2 sa"), (9, 16, "12 dk")]
    for n, c, last in stats:
        f = qr_svg(f"https://{BIZ_URL}/m/{n:02d}", f"qr_{n:02d}.png")
        rows.append(f'<tr class="{"on" if n == 5 else ""}"><td><img src="{f}"></td><td><b>Şezlong {n:02d}</b><br>'
                    f'<small>{BIZ_URL}/m/{n:02d}</small></td><td class="num">{c}</td><td>{last}</td>'
                    f'<td><span class="chip g">Aktif</span></td><td><span class="dl">{ic("download")}QR indir</span></td>'
                    f'</tr>')
    big = qr_svg(f"https://{BIZ_URL}/m/05", "qr_buyuk.png")
    body = (f'<div class="app">{sidebar("Masalar ve QR")}<main class="main">'
            f'<div class="top"><div><h1>Masalar ve QR</h1><div class="sub">24 şezlong · 12 masa · her birinin kendi '
            f'QR\'ı</div></div><span class="sp"></span><span class="btn">{ic("download")}Tümünü indir</span>'
            f'<span class="btn a">{ic("plus", sw=2.2)}Masa ekle</span></div>'
            f'<div class="info">{ic("bolt")}<span><b>QR\'lar sizin adresinizi açar, menü dosyasını ya da Google\'ı '
            f'değil.</b> Menü, fiyat ya da Google bağlantınız değişse de masalıklarınız aynı kalır; yeniden baskı '
            f'gerekmez.</span></div><div class="split"><div class="card"><table><tr><th>QR</th><th>MASA</th>'
            f'<th>BUGÜN OKUTMA</th><th>SON OKUTMA</th><th>DURUM</th><th></th></tr>{"".join(rows)}</table></div>'
            f'<div class="card big"><h3>Şezlong 05</h3><img src="{big}"><b>Şezlong 05</b>'
            f'<code>{BIZ_URL}/m/05</code><div class="tg"><div>Ön yüz QR\'ı<small>Menü · şezlong numarasıyla açılır'
            f'</small></div><div>Arka yüz QR\'ı<small>Google yorum · bağlantı panelden değişir</small></div>'
            f'<div>NFC etiketi<small>Aynı adres · telefonu dokundurmak yeter</small></div></div></div></div>'
            f'</main></div>')
    return panel_page("Masalar ve QR", TBL_CSS, body)


ORD_CSS = """
body{background:#121318;color:#EDE8DE}
.kh{display:flex;align-items:center;gap:14px;padding:18px 24px;border-bottom:1px solid #24262E}
.kh b{font-family:Fraunces;font-size:24px}
.kh small{color:#8F8A80}
.kh .clk{margin-left:auto;font-family:Manrope;font-weight:600;font-size:24px}
.kh svg{width:24px;height:24px;color:#C8963E}
.calls{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:16px 24px 4px}
.call{display:flex;align-items:center;gap:14px;border-radius:16px;padding:14px 16px}
.call.w{background:#C8963E;color:#17191F}
.call.h{background:#2B3A6B;color:#fff}
.call svg{width:30px;height:30px}
.call b{font-size:18px;display:block}
.call small{opacity:.8}
.call span.ok{margin-left:auto;background:rgba(0,0,0,.18);border-radius:10px;padding:8px 12px;font-weight:600}
.board{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;padding:14px 24px}
.col h4{font-size:13px;letter-spacing:.16em;color:#8F8A80;margin-bottom:10px;font-weight:600}
.col h4 em{font-style:normal;background:#2A2D36;color:#EDE8DE;border-radius:999px;padding:1px 8px;margin-left:6px}
.oc{background:#1D1F26;border:1px solid #2A2D36;border-radius:16px;padding:14px 16px;margin-bottom:12px}
.oc.n{border-color:#C8963E}
.oc .h{display:flex;justify-content:space-between;align-items:baseline}
.oc .h b{font-size:18px}
.oc .h small{color:#8F8A80}
.oc ul{list-style:none;margin:10px 0;font-size:14.5px}
.oc li{display:flex;justify-content:space-between;padding:3px 0}
.oc li i{font-style:normal;color:#8F8A80}
.oc .note{font-size:12.5px;color:#E2B86A;margin-bottom:10px}
.oc .f{display:flex;justify-content:space-between;align-items:center}
.oc .f .num{font-size:16px}
.oc .b{background:#C8963E;color:#17191F;border-radius:10px;padding:8px 14px;font-weight:600;font-size:14px}
.oc .b.s{background:#2E8B57;color:#fff}
.oc.d{opacity:.55}
"""


def orders():
    def card(t, ago, its, total, btn, cls="", note=""):
        li = "".join(f'<li><span>{e(a)}</span><i>× {q}</i></li>' for a, q in its)
        nt = f'<div class="note">{e(note)}</div>' if note else ""
        bt = f'<span class="b{" s" if btn == "Teslim edildi" else ""}">{e(btn)}</span>' if btn else ""
        return (f'<div class="oc {cls}"><div class="h"><b>{e(t)}</b><small>{e(ago)}</small></div><ul>{li}</ul>{nt}'
                f'<div class="f"><span class="num">{e(total)}</span>{bt}</div></div>')
    new = (card("Şezlong 12", "1 dk önce", [("Aperol spritz", 2), ("Poke bowl", 1)], "1.300 ₺", "Kabul et", "n") +
           card("Şezlong 04", "3 dk önce", [("Mojito", 1), ("Margherita", 1), ("Su", 2)], "860 ₺", "Kabul et", "n",
                "Not: pizza ikiye bölünsün"))
    prep = (card("Şezlong 09", "8 dk", [("Virgin colada", 2), ("Burger", 1)], "980 ₺", "Hazır") +
            card("Masa 03", "11 dk", [("Negroni", 2), ("San Sebastian", 1)], "1.250 ₺", "Hazır"))
    done = (card("Şezlong 17", "hazır · 2 dk", [("Gün batımı", 2)], "900 ₺", "Teslim edildi") +
            card("Şezlong 21", "teslim · 14 dk", [("Flat white", 2)], "280 ₺", "", "d"))
    body = (f'<div class="kh">{ic("bag")}<span><b>Siparişler</b><br><small>Palmiye · bar ve mutfak ekranı</small></span>'
            f'<span class="clk">18:42</span>{ic("sound")}</div>'
            f'<div class="calls"><div class="call w">{ic("bell", sw=2)}<span><b>Şezlong 07 garson çağırıyor</b>'
            f'<small>40 sn önce</small></span><span class="ok">Gidiyorum</span></div>'
            f'<div class="call h">{ic("card", sw=2)}<span><b>Şezlong 15 hesap istiyor</b><small>Kartla ödeyecek'
            f'</small></span><span class="ok">Tamam</span></div></div>'
            f'<div class="board"><div class="col"><h4>YENİ<em>2</em></h4>{new}</div>'
            f'<div class="col"><h4>HAZIRLANIYOR<em>2</em></h4>{prep}</div>'
            f'<div class="col"><h4>HAZIR / TESLİM<em>2</em></h4>{done}</div></div>')
    return panel_page("Siparişler", ORD_CSS, body)


# ---------------------------------------------------------------- müşterinin gördüğü menü (tükendi, İngilizce)

PALMIYE_EXTRA = """
.mc{position:relative}
.mc.out img{filter:grayscale(1);opacity:.55}
.mc .so{position:absolute;left:10px;top:10px;background:#C4473B;color:#fff;border-radius:999px;padding:4px 10px;
  font-size:11.5px;font-weight:600;letter-spacing:.04em}
.top .lg{display:flex;gap:2px;font-size:11px;border:1px solid #D8BE95;border-radius:999px;padding:3px}
.top .lg i{font-style:normal;padding:2px 8px;border-radius:999px}
.top .lg i.on{background:#D8BE95;color:#1D2742;font-weight:600}
.nw{display:inline-block;margin-left:6px;font-size:10.5px;color:#2E8B57;font-weight:600}
"""


def palmiye_menu(lang="tr"):
    tr = lang == "tr"
    data = [("icki_aperol", "Aperol spritz", "Prosecco, soda, portakal" if tr else "Prosecco, soda, orange", "420 ₺",
             "", True),
            ("icki_mojito", "Mojito", "Taze nane, lime, kırık buz" if tr else "Fresh mint, lime, crushed ice", "380 ₺",
             "", False),
            ("icki_colada", "Virgin colada", "Ananas, hindistancevizi" if tr else "Pineapple, coconut", "260 ₺",
             "Alkolsüz" if tr else "Alcohol-free", True),
            ("poke_bowl", "Poke bowl", "Somon, avokado, edamame, mango" if tr else "Salmon, avocado, edamame, mango",
             "460 ₺", "Yeni" if tr else "New", True)]
    hs = [236, 178, 200, 168]
    cards = []
    for k, (im, n, d, p, tg, on) in enumerate(data):
        so = "" if on else f'<span class="so">{"TÜKENDİ" if tr else "SOLD OUT"}</span>'
        cards.append(f'<div class="mc{"" if on else " out"}"><img src="{img(im)}" style="height:{hs[k]}px" alt="">{so}'
                     f'<div><b>{e(n)}{f"<em>{e(tg)}</em>" if tg else ""}</b><p>{e(d)}</p><span class="num">{e(p)}</span>'
                     f'</div></div>')
    tabs = ["Kokteyller", "Bowl", "Pizza", "Tatlı"] if tr else ["Cocktails", "Bowls", "Pizza", "Desserts"]
    pills = "".join(f'<span class="{"on" if k == 0 else ""}">{e(t)}</span>' for k, t in enumerate(tabs))
    lg = f'<span class="lg"><i class="{"on" if tr else ""}">TR</i><i class="{"" if tr else "on"}">EN</i></span>'
    body = (f'<div class="top"><b>Palmiye</b>{lg}<span>{"ŞEZLONG 12" if tr else "SUNBED 12"}</span></div>'
            f'<div class="pills">{pills}</div><div class="ms">{"".join(cards)}</div>')
    css = MS.PALMIYE_CSS + PALMIYE_EXTRA
    return (f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>Palmiye</title><style>{FONTS}'
            f'{MS.RESET}{css}</style></head><body>{body}</body></html>')


ICON_PAGE_KEYS = ["bolt", "qr", "eye", "edit", "percent", "image", "globe", "chart", "palette", "bag", "bell", "shield",
                  "lock", "clock", "star", "store", "check", "users"]


def icon_page():
    tiles = "".join(f'<div id="i_{k}" class="t">{ic(k, sw=1.9)}</div>' for k in ICON_PAGE_KEYS)
    css = (".t{width:96px;height:96px;border-radius:28px;background:#C8963E;color:#fff;display:grid;place-items:center;"
           "margin:8px;float:left}.t svg{width:52px;height:52px}body{background:transparent}")
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{MS.RESET}{css}</style></head><body>{tiles}</body></html>'


SCREENS = {  # ad: (üretici, görünüm genişliği, yüksekliği)
    "gosterge": (dashboard, 1440, 900), "menu": (menu_admin, 1440, 900), "ayarlar": (settings, 1440, 900),
    "masalar": (tables, 1440, 900), "urun": (item_edit, 390, 844), "toplu": (bulk_price, 390, 844),
    "giris": (login, 390, 844), "siparis": (orders, 1180, 820),
}


def shoot():
    from playwright.sync_api import sync_playwright
    os.makedirs(SCR, exist_ok=True)
    open(os.path.join(SCR, "palmiye_tukendi.html"), "w", encoding="utf-8").write(palmiye_menu("tr"))
    open(os.path.join(SCR, "palmiye_en.html"), "w", encoding="utf-8").write(palmiye_menu("en"))
    open(os.path.join(SCR, "simgeler.html"), "w", encoding="utf-8").write(icon_page())
    for k, (fn, _, _) in SCREENS.items():
        open(os.path.join(SCR, k + ".html"), "w", encoding="utf-8").write(fn())
    shots = {}
    with sync_playwright() as pw:
        exe = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
        br = pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()
        sizes = [(k, w, h) for k, (_, w, h) in SCREENS.items()] + [("palmiye_tukendi", 390, 844),
                                                                     ("palmiye_en", 390, 844)]
        for k, w, h in sizes:
            ctx = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=2)
            pg = ctx.new_page()
            pg.goto("file://" + os.path.join(SCR, k + ".html"))
            pg.wait_for_load_state("load")
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(400)
            path = os.path.join(SCR, k + ".png")
            pg.screenshot(path=path)
            shots[k] = Image.open(path).convert("RGB")
            ctx.close()
        ctx = br.new_context(viewport={"width": 1200, "height": 600}, device_scale_factor=2)
        pg = ctx.new_page()
        pg.goto("file://" + os.path.join(SCR, "simgeler.html"))
        pg.wait_for_load_state("load")
        icons = {}
        for k in ICON_PAGE_KEYS:
            path = os.path.join(SCR, f"simge_{k}.png")
            pg.locator(f"#i_{k}").screenshot(path=path, omit_background=True)
            icons[k] = Image.open(path).convert("RGBA")
        br.close()
    return shots, icons


# ================================================================ katalog sayfaları

PAGE, INK, MUTED, PAPER, GOLD = R.PAGE, R.INK, R.MUTED, R.PAPER, R.GOLD
TITLE = "Menü Yönetim Paneli"
F = R.font_ui


def browser(screen, w, url=PANEL_URL):
    """Ekran görüntüsünü tarayıcı penceresine koyar (RGBA)."""
    bar = int(w * 0.034)
    inner = screen.resize((w, int(screen.height * w / screen.width)), Image.LANCZOS)
    h = inner.height + bar
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    r = int(w * 0.012)
    dr.rounded_rectangle((0, 0, w - 1, h - 1), r, fill=(232, 228, 220, 255), outline=(206, 200, 188, 255))
    for k, c in enumerate(((236, 106, 94), (244, 190, 80), (98, 196, 98))):
        cx = bar * 0.7 + k * bar * 0.62
        dr.ellipse((cx - bar * 0.19, bar / 2 - bar * 0.19, cx + bar * 0.19, bar / 2 + bar * 0.19), fill=c)
    uw = w * 0.42
    dr.rounded_rectangle((w / 2 - uw / 2, bar * 0.2, w / 2 + uw / 2, bar * 0.8), bar * 0.3, fill=(250, 248, 244))
    f = F(int(bar * 0.38))
    dr.text((w / 2 - dr.textlength(url, font=f) / 2, bar * 0.27), url, font=f, fill=(110, 104, 94))
    im.paste(inner, (0, bar))
    mask = R.rounded(im, r)
    im.putalpha(mask)
    return im


def tablet(screen, w):
    bez = int(w * 0.03)
    inner = screen.resize((w - 2 * bez, int(screen.height * (w - 2 * bez) / screen.width)), Image.LANCZOS)
    h = inner.height + 2 * bez
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle((0, 0, w - 1, h - 1), int(w * 0.04), fill=(24, 24, 27, 255), outline=(70, 70, 76, 255), width=2)
    m = Image.new("L", inner.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, inner.width - 1, inner.height - 1), int(w * 0.018), fill=255)
    im.paste(inner, (bez, bez), m)
    return im


def put(canvas, frame, xy, blur=24, alpha=0.3):
    R.shadowed(canvas, frame, xy, blur=blur, off=(0, int(blur * 0.8)), alpha=alpha)


def feature(im, dr, icons, key, x, y, w, title, desc, size=78):
    ic_ = icons[key].resize((size, size), Image.LANCZOS)
    im.paste(ic_, (x, y), ic_)
    dr.text((x + size + 22, y + 2), title, font=F(30, "bold"), fill=INK)
    ty = y + 44
    for row in R.wrap(dr, desc, F(23), w - size - 22):
        dr.text((x + size + 22, ty), row, font=F(23), fill=MUTED)
        ty += 31
    return max(ty, y + size) + 26


def page_head(dr, kicker, title, sub=None, y=150):
    dr.text((80, y), kicker, font=F(22, "bold"), fill=GOLD)
    dr.text((80, y + 34), title, font=F(60, "serif_k"), fill=INK)
    if sub:
        yy = y + 118
        for row in R.wrap(dr, sub, F(26), PAGE[0] - 160):
            dr.text((82, yy), row, font=F(26), fill=MUTED)
            yy += 36
        return yy + 20
    return y + 120


def new_page(p, n):
    im = Image.new("RGB", PAGE, PAPER)
    dr = ImageDraw.Draw(im)
    R.header(im, dr, p, n, TITLE)
    return im, dr


FOOT = "Ekranlar tasarım örneğidir; işletme, ürünler ve rakamlar temsilîdir."


def p_cover(shots, icons, n):
    im = Image.new("RGB", PAGE, PAPER)
    dr = ImageDraw.Draw(im)
    dr.text((84, 96), "QR SİSTEM", font=F(26, "bold"), fill=GOLD)
    dr.text((80, 130), "Menü Yönetim", font=F(150, "serif_k"), fill=INK)
    dr.text((86, 310), "Paneli", font=F(104, "serif_i"), fill=GOLD)
    dr.text((90, 462), "Masalıklarınızın arkasındaki sistem: menü, fiyat, fotoğraf ve istatistik tek yerden.",
            font=F(31), fill=MUTED)
    b = browser(shots["gosterge"], 1330)
    put(im, b, (80, 560), blur=28, alpha=0.28)
    ph = R.phone(shots["palmiye_tukendi"], 330)
    put(im, ph, (PAGE[0] - 80 - 330, 820), blur=26, alpha=0.38)
    y = 560 + b.height + 90
    cols = [("bolt", "Anında yayında", "Fiyatı, fotoğrafı ya da “tükendi”yi değiştirin; müşteri bir sonraki okutmada "
                                       "yeni menüyü görür."),
            ("qr", "Masalık değişmez", "QR'lar sizin adresinizi açar. Menü ya da Google bağlantısı değişse de yeniden "
                                       "baskı gerekmez."),
            ("chart", "Ne işe yaradığını görün", "Hangi masadan kaç okutma, en çok bakılan ürünler, Google'a giden "
                                                 "müşteriler.")]
    cw = (PAGE[0] - 160 - 2 * 40) // 3
    for k, (key, t, d) in enumerate(cols):
        x = 80 + k * (cw + 40)
        ic_ = icons[key].resize((84, 84), Image.LANCZOS)
        im.paste(ic_, (x, y), ic_)
        dr.text((x, y + 108), t, font=F(36, "serif_k"), fill=INK)
        ty = y + 164
        for row in R.wrap(dr, d, F(24), cw):
            dr.text((x, ty), row, font=F(24), fill=MUTED)
            ty += 34
    y += 330
    dr.text((80, y), "Uygulama indirmek yok", font=F(36, "serif_k"), fill=INK)
    y += 60
    for line in ("Panel telefondan, tabletten ve bilgisayardan açılır; müşteriniz de yalnız QR okutur.",
                 "Menünüzü, fotoğraflarınızı ve masalarınızı ilk kurulumda biz gireriz; sonra dilediğiniz kadar "
                 "kendiniz güncellersiniz.",
                 "Türkçe, İngilizce, Rusça ve Almanca menü; her ürün için ayrı çeviri."):
        dr.ellipse((84, y + 12, 98, y + 26), fill=GOLD)
        ty = y
        for row in R.wrap(dr, line, F(26), 1430):
            dr.text((118, ty), row, font=F(26), fill=INK)
            ty += 36
        y = ty + 12
    kh = PAGE[1] - 170 - (y + 30)
    if kh > 200:
        ph = R.photo_box(Image.open(os.path.join(R.OUT_DIR, "foto", "kapak.png")).convert("RGB"), PAGE[0] - 160, kh, 0.55)
        R.shadowed(im, ph, (80, y + 30), R.rounded(ph, 28), blur=20, off=(0, 14), alpha=0.22)
    R.footer(dr, FOOT)
    return im


def p_how(shots, icons, p, n):
    im, dr = new_page(p, n)
    y = page_head(dr, "NASIL ÇALIŞIR?", "Masadan panele, panelden masaya",
                  "Müşteri yalnız QR'ı okutur. Gördüğü sayfa her an sizin panelde yazdığınızdır.")
    steps = [
        ("1", "Müşteri QR'ı okutur", "Masalıktaki QR'ı telefonuyla okutur ya da NFC etiketine dokunur. Uygulama "
                                     "gerekmez; masa numarası da sayfaya gelir.", "masalik"),
        ("2", "Sizin sayfanız açılır", "Menü, fotoğraflar, fiyatlar, Google yorum düğmesi, Wi-Fi, Instagram; "
                                       "işletmenizin renklerinde.", "site"),
        ("3", "Siz panelden yönetirsiniz", "Ürün ekler, fiyat değiştirir, “tükendi” dersiniz. Kaydettiğiniz anda "
                                           "yayındadır; masalığa dokunmazsınız.", "panel"),
    ]
    row_h = 600
    for k, (num, t, d, kind) in enumerate(steps):
        y0 = y + k * row_h
        if kind == "masalik":
            ph = Image.open(os.path.join(R.OUT_DIR, "foto", "16_sorf_on.png")).convert("RGB")
            pb = R.photo_box(ph, 640, row_h - 60, 0.5)
            put(im, pb.convert("RGBA"), (80, y0), blur=18, alpha=0.22)
            im.paste(pb, (80, y0), R.rounded(pb, 26))
        elif kind == "site":
            ph = R.phone(MS_home("palmiye"), 236)
            put(im, ph, (80 + 320 - 118, y0 - 10), blur=18, alpha=0.3)
        else:
            b = browser(shots["menu"], 640)
            put(im, b, (80, y0 + 60), blur=18, alpha=0.25)
        tx = 80 + 640 + 70
        dr.ellipse((tx, y0 + 30, tx + 76, y0 + 106), fill=GOLD)
        fnum = F(44, "serif_k")
        dr.text((tx + 38 - dr.textlength(num, font=fnum) / 2, y0 + 38), num, font=fnum, fill=PAPER)
        dr.text((tx + 100, y0 + 40), t, font=F(40, "serif_k"), fill=INK)
        ty = y0 + 130
        for row in R.wrap(dr, d, F(27), PAGE[0] - 80 - tx):
            dr.text((tx, ty), row, font=F(27), fill=MUTED)
            ty += 38
        if k < 2:
            ax = tx + 38
            dr.line((ax, y0 + 120 + 200, ax, y0 + row_h - 10), fill=(214, 196, 160), width=4)
            dr.polygon([(ax - 12, y0 + row_h - 22), (ax + 12, y0 + row_h - 22), (ax, y0 + row_h - 2)],
                       fill=(214, 196, 160))
    R.footer(dr, FOOT)
    return im


def MS_home(slug):
    return Image.open(os.path.join(MS.OUT, slug, "ekran_ana.png")).convert("RGB")


def p_dashboard(shots, icons, p, n):
    im, dr = new_page(p, n)
    y = page_head(dr, "GÖSTERGE PANELİ", "Masalıklarınız ne işe yarıyor, görün",
                  "Panele girince günün özeti karşılar: kaç kişi okuttu, menüde ne kadar kaldı, kaç kişi Google'a "
                  "yorum yazmaya gitti.")
    b = browser(shots["gosterge"], PAGE[0] - 160)
    put(im, b, (80, y), blur=26, alpha=0.26)
    y += b.height + 80
    feats = [("qr", "Okutma sayıları", "Gün, hafta ve ay olarak; geçen döneme göre artış ya da azalış."),
             ("chart", "Saat ve masa bazında", "En yoğun saatler ve en çok okutulan masalar; personel ve "
                                               "yerleşim için ipucu."),
             ("eye", "En çok bakılan ürünler", "Hangi ürünler ilgi görüyor, hangileri menüde kayboluyor."),
             ("star", "Google yorumları", "Kaç müşteri yorum sayfanıza gitti; puanınızın gidişatı.")]
    cw = (PAGE[0] - 160 - 60) // 2
    for k, (key, t, d) in enumerate(feats):
        x = 80 + (k % 2) * (cw + 60)
        yy = y + (k // 2) * 200
        feature(im, dr, icons, key, x, yy, cw, t, d)
    R.footer(dr, FOOT)
    return im


def p_menu(shots, icons, p, n):
    im, dr = new_page(p, n)
    y = page_head(dr, "MENÜ", "Menünüz sizin elinizde",
                  "Ürün ekleyin, sürükleyip sıralayın, fotoğraf yükleyin. Sağdaki önizleme müşterinin telefonunda "
                  "göreceğinin aynısı.")
    b = browser(shots["menu"], PAGE[0] - 160)
    put(im, b, (80, y), blur=26, alpha=0.26)
    y += b.height + 70
    p1 = R.phone(shots["urun"], 300)
    p2 = R.phone(shots["toplu"], 300)
    put(im, p1, (80, y), blur=20, alpha=0.32)
    put(im, p2, (80 + 300 + 40, y + 40), blur=20, alpha=0.32)
    x = 80 + 640 + 70
    w = PAGE[0] - 80 - x
    yy = y + 10
    for key, t, d in (("edit", "Ürün ve fotoğraf", "Ad, açıklama, fiyat, etiket (yeni, şefin önerisi, acı, vegan), "
                                                   "alerjen; fotoğrafı telefonla çekip yükleyin."),
                      ("check", "Tek dokunuşla “tükendi”", "Ürün menüde kalır, “Tükendi” yazar; stok gelince geri açın."),
                      ("percent", "Toplu fiyat", "Bir kategoriye ya da tüm menüye %10 zam; 5 ya da 10 liraya "
                                                 "yuvarlama, uygulamadan önce önizleme."),
                      ("clock", "Saatli menü", "Kahvaltı, öğle ve akşam menüsü kendiliğinden değişir."),
                      ("globe", "Dört dil", "Türkçe, İngilizce, Rusça, Almanca; müşteri dilini kendi seçer.")):
        yy = feature(im, dr, icons, key, x, yy, w, t, d, size=70)
    R.footer(dr, FOOT)
    return im


def p_live(shots, icons, p, n):
    im, dr = new_page(p, n)
    y = page_head(dr, "MÜŞTERİNİN GÖRDÜĞÜ", "Kaydettiğiniz an menüde",
                  "Panelde Mojito'yu “tükendi” yaptınız: masadaki müşteri bir sonraki okutmada bunu görür. Yabancı "
                  "misafir menüyü kendi dilinde açar.")
    pw_ = 470
    gap = (PAGE[0] - 160 - 3 * pw_) // 2
    items = [(shots["palmiye_tukendi"], "Tükendi etiketi", "Ürün gizlenmez; soluk görünür, “Tükendi” yazar."),
             (shots["palmiye_en"], "Kendi dilinde", "TR / EN düğmesiyle; çeviriler panelden."),
             (MS_home("palmiye"), "Karşılama sayfası", "Masa numarası, sipariş, Google yorumu, Wi-Fi.")]
    for k, (scr, t, d) in enumerate(items):
        x = 80 + k * (pw_ + gap)
        ph = R.phone(scr, pw_)
        put(im, ph, (x, y + 10), blur=24, alpha=0.34)
        ty = y + ph.height + 60
        dr.text((x, ty), t, font=F(34, "serif_k"), fill=INK)
        ty += 52
        for row in R.wrap(dr, d, F(24), pw_):
            dr.text((x, ty), row, font=F(24), fill=MUTED)
            ty += 34
    y = y + R.phone(shots["palmiye_en"], pw_).height + 250
    box = (80, y, PAGE[0] - 80, y + 330)
    dr.rounded_rectangle(box, 30, fill=(255, 253, 249), outline=(226, 218, 204))
    dr.text((120, y + 36), "Masalıktaki menü ile panelin bağlantısı", font=F(36, "serif_k"), fill=INK)
    lines = ["QR, menü dosyasını değil işletmenizin adresini açar; içerik panelden gelir.",
             "Fiyat değişikliği için menü bastırmak, PDF yüklemek, masalığı değiştirmek yok.",
             "İnternet sayfası hızlıdır: telefon ekranına göre hazırlanmış hafif sayfalar, uygulama yok.",
             "Kaleiçi'nden Rooftop'a: masalıklarınızla aynı renk ve yazı tipinde 10 hazır tema."]
    ty = y + 100
    for line in lines:
        dr.ellipse((124, ty + 12, 138, ty + 26), fill=GOLD)
        dr.text((158, ty), line, font=F(25), fill=INK)
        ty += 52
    R.footer(dr, FOOT)
    return im


def p_settings(shots, icons, p, n):
    im, dr = new_page(p, n)
    y = page_head(dr, "İŞLETME VE TEMA", "Bilgileriniz, renkleriniz, temanız",
                  "Telefon, Instagram, Wi-Fi, çalışma saatleri ve Google yorum bağlantısı tek sayfada. Tema "
                  "değiştirmek bir dokunuş; renkler işletmenize göre ayarlanır.")
    b = browser(shots["ayarlar"], PAGE[0] - 160)
    put(im, b, (80, y), blur=26, alpha=0.26)
    y += b.height + 70
    dr.text((80, y), "10 hazır tema", font=F(40, "serif_k"), fill=INK)
    y += 70
    themes = [("kaleici", "Saray"), ("lagun", "Deniz"), ("forno", "Kartlar"), ("garaj", "Poster"),
              ("kopuk", "Uygulama"), ("koi", "Minimal"), ("asma", "Kara tahta"), ("kasap", "Tam fotoğraf"),
              ("palmiye", "Gün batımı"), ("r360", "Gece")]
    pw_ = 250
    gap = (PAGE[0] - 160 - 5 * pw_) // 4
    for k, (slug, name) in enumerate(themes):
        x = 80 + (k % 5) * (pw_ + gap)
        scr = MS_home(slug)
        crop = scr.crop((0, 0, scr.width, int(scr.width * 0.98)))
        ph = R.phone(crop, pw_)
        yy = y + (k // 5) * (ph.height + 80)
        put(im, ph, (x, yy), blur=14, alpha=0.3)
        f = F(24, "bold")
        dr.text((x + pw_ / 2 - dr.textlength(name, font=f) / 2, yy + ph.height + 22), name, font=f, fill=INK)
    R.footer(dr, FOOT)
    return im


def p_tables(shots, icons, p, n):
    im, dr = new_page(p, n)
    y = page_head(dr, "MASALAR VE QR", "Her masanın kendi QR'ı",
                  "Masa ya da şezlong ekleyin, QR'ını indirin; masalık o numarayla basılır. Hangi masadan ne zaman "
                  "okutulduğu da burada.")
    b = browser(shots["masalar"], PAGE[0] - 160)
    put(im, b, (80, y), blur=26, alpha=0.26)
    y += b.height + 80
    feats = [("qr", "Masa numaralı sayfa", "Müşteri okutunca “Şezlong 05” diye karşılanır; sipariş ve garson "
                                           "çağrısı doğru masaya gider."),
             ("bolt", "Bağlantıyı panelden değiştirin", "Google yorum sayfanız ya da menünüz değişse de QR aynı kalır; "
                                                         "masalıkları yeniden bastırmazsınız."),
             ("store", "Yeni masa, yeni QR", "Masa ekleyince QR'ı hazırdır; aynı tasarımla bastırıp masaya koyarsınız."),
             ("chart", "Masa masa istatistik", "Bugün, bu hafta, bu ay; hangi bölgenin daha çok kullanıldığını görün.")]
    cw = (PAGE[0] - 160 - 60) // 2
    for k, (key, t, d) in enumerate(feats):
        x = 80 + (k % 2) * (cw + 60)
        yy = y + (k // 2) * 210
        feature(im, dr, icons, key, x, yy, cw, t, d)
    R.footer(dr, FOOT)
    return im


def p_orders(shots, icons, p, n):
    im, dr = new_page(p, n)
    dr.text((80, 150), "SİPARİŞ PAKETİ", font=F(22, "bold"), fill=GOLD)
    f = F(20, "bold")
    tw = dr.textlength("YAKINDA", font=f)
    x0 = 80 + dr.textlength("SİPARİŞ PAKETİ", font=F(22, "bold")) + 22
    dr.rounded_rectangle((x0, 146, x0 + tw + 30, 180), 17, fill=(29, 39, 66))
    dr.text((x0 + 15, 150), "YAKINDA", font=f, fill=(244, 237, 225))
    dr.text((80, 184), "Masadan sipariş, garson çağır, hesap", font=F(60, "serif_k"), fill=INK)
    yy = 302
    for row in R.wrap(dr, "Müşteri menüden siparişini verir, garsonu çağırır ya da hesabı ister; bar ve mutfaktaki "
                          "tablette sesli uyarıyla düşer. Sipariş hangi masadan geldiğiyle birlikte görünür.",
                      F(26), PAGE[0] - 160):
        dr.text((82, yy), row, font=F(26), fill=MUTED)
        yy += 36
    y = yy + 40
    t = tablet(shots["siparis"], PAGE[0] - 160 - 120)
    put(im, t, (80, y), blur=28, alpha=0.32)
    ph = R.phone(MS_home("palmiye"), 280)
    put(im, ph, (PAGE[0] - 80 - 280, y + t.height - ph.height + 40), blur=24, alpha=0.4)
    y += t.height + 90
    feats = [("bag", "Masadan sipariş", "Sepet, not ekleme (“ikiye bölünsün”), sipariş durumu müşterinin "
                                        "telefonunda."),
             ("bell", "Garson çağır ve hesap", "Tek dokunuş; ekranda masa numarasıyla, sesli uyarıyla."),
             ("clock", "Bar ve mutfak ekranı", "Yeni, hazırlanıyor, hazır; kim ne zaman kabul etti."),
             ("users", "Personel hesapları", "Garson, bar, mutfak ve yönetici için ayrı yetkiler.")]
    cw = (PAGE[0] - 160 - 60) // 2
    for k, (key, t_, d) in enumerate(feats):
        x = 80 + (k % 2) * (cw + 60)
        feature(im, dr, icons, key, x, y + (k // 2) * 190, cw, t_, d)
    R.footer(dr, FOOT)
    return im


def p_packages(shots, icons, p, n):
    im, dr = new_page(p, n)
    y = page_head(dr, "PAKETLER", "İhtiyacınız kadarı",
                  "Masalıklarınızla birlikte menü paketi; isterseniz sipariş paketi de eklenir.")
    cw = (PAGE[0] - 160 - 50) // 2
    packs = [("Menü Paketi", "Masalık + sayfa + panel", [
        "İşletmeye özel sayfa, 10 temadan biri", "Panelden menü, fotoğraf, fiyat, “tükendi”",
        "Toplu fiyat güncelleme, saatli menü", "4 dil: TR, EN, RU, DE", "Google yorum, Wi-Fi, Instagram düğmeleri",
        "Masa numaralı QR'lar ve NFC", "Gösterge paneli ve istatistik", "İlk kurulumu biz yaparız"], (29, 39, 66)),
             ("Sipariş Paketi", "Menü Paketi'ne ek · yakında", [
        "Masadan sipariş ve sepet", "Garson çağır, hesap iste", "Bar ve mutfak ekranı (tablet)",
        "Sesli bildirim", "Personel hesapları ve yetkiler", "Sipariş raporları"], GOLD)]
    for k, (name, sub, feats, col) in enumerate(packs):
        x = 80 + k * (cw + 50)
        h = 980
        dr.rounded_rectangle((x, y, x + cw, y + h), 34, fill=(255, 253, 249), outline=(226, 218, 204), width=2)
        dr.rounded_rectangle((x, y, x + cw, y + 190), 34, fill=col)
        dr.rectangle((x, y + 150, x + cw, y + 190), fill=col)
        dr.text((x + 44, y + 44), name, font=F(52, "serif_k"), fill=(250, 246, 238))
        dr.text((x + 46, y + 118), sub, font=F(26), fill=(236, 226, 206))
        ty = y + 240
        for line in feats:
            ck = icons["check"].resize((46, 46), Image.LANCZOS)
            im.paste(ck, (x + 44, ty - 4), ck)
            for row in R.wrap(dr, line, F(27), cw - 140):
                dr.text((x + 112, ty), row, font=F(27), fill=INK)
                ty += 38
            ty += 30
    y += 980 + 70
    ph = R.phone(shots["giris"], 300)
    put(im, ph, (80, y), blur=20, alpha=0.32)
    x = 80 + 300 + 70
    w = PAGE[0] - 80 - x
    yy = y + 10
    dr.text((x, yy), "Güvenli ve bakımsız", font=F(40, "serif_k"), fill=INK)
    yy += 74
    for key, t, d in (("lock", "İşletmeye özel giriş", "Şifre ve telefona gelen kodla iki adımlı giriş; her personelin "
                                                       "kendi hesabı."),
                      ("shield", "Şifreli bağlantı ve yedek", "Sayfalar ve panel HTTPS; menünüz her gün yedeklenir, "
                                                              "değişiklik geçmişi tutulur."),
                      ("bolt", "Hızlı altyapı", "Cloudflare'in dünya çapındaki ağında; sunucu, bakım ya da "
                                                "güncelleme derdi sizde değil.")):
        yy = feature(im, dr, icons, key, x, yy, w, t, d, size=70)
    R.footer(dr, "Beğendiğiniz paketi yazmanız yeterli; kurulum, menü girişi ve QR'lar bizden.")
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    shots, icons = shoot()
    builders = [p_how, p_dashboard, p_menu, p_live, p_settings, p_tables, p_orders, p_packages]
    n = 1 + len(builders)
    pages = [p_cover(shots, icons, n)] + [b(shots, icons, k + 2, n) for k, b in enumerate(builders)]
    for f in os.listdir(OUT):
        if f.startswith("katalog_") and f.endswith(".jpg"):
            os.remove(os.path.join(OUT, f))
    for k, pg in enumerate(pages, 1):
        pg.save(os.path.join(OUT, f"katalog_{k:02d}.jpg"), "JPEG", quality=88, optimize=True)
    pages[0].save(os.path.join(OUT, "katalog.pdf"), save_all=True, append_images=pages[1:], resolution=200)
    print(f"{len(pages)} sayfa → {os.path.relpath(OUT, ROOT)}/katalog.pdf")


if __name__ == "__main__":
    main()
