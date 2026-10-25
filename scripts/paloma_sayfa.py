"""PALOMA GRIDA – Süleyman Boylu'nun dijital kartviziti (isimlikteki QR bu sayfayı açar).

Paloma mavisi ve beyaz, otelin kimliğinde tek sayfa: üstte Paloma Hotels logosu, GRIDA ve dalgalanan deniz;
altında tek dokunuşla ara (cep ve şirket hattı), WhatsApp, e-posta, konum, rehbere kaydet (vCard) ve paylaş.
Dış bağlantı yok: yazı tipleri sayfanın yanında (OFL), simgeler sayfanın içinde. "Hareketi azalt" açıksa dalga ve
giriş hareketleri durur.

Logo: paloma_isimlik/logo/paloma_hotels.svg (scripts/paloma_logo.py). Yazı tipleri isimliklerle aynı: Montserrat ve
Lora (ad soyad).
Bilgiler `paloma_isimlik/bilgiler.json`dan okunur.

Yayın: ortak Cloudflare hesabında (`qrsistem`) `suleymanboylu` adlı Worker'a `paloma_site.zip` yüklenir; adres
`https://suleymanboylu.qrsistem.workers.dev/` (isimliklerdeki QR bu adresi açar).

Çıktı : paloma_isimlik/site/, paloma_isimlik/paloma_site.zip, sayfa_onizleme.png

Kullanım:
  python3 scripts/paloma_sayfa.py
"""
import html
import json
import math
import os
import shutil
import sys
import zipfile

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import qr_sistemi as Q  # noqa: E402

BASE = os.path.join(A.ROOT, "paloma_isimlik")
OUT = os.path.join(BASE, "site")
ZIP = os.path.join(BASE, "paloma_site.zip")
PREVIEW = os.path.join(BASE, "sayfa_onizleme.png")
CHROMIUM = "/opt/pw-browsers/chromium"
FONTS = {"sans": "Montserrat_600SemiBold.ttf", "sans-b": "Montserrat_700Bold.ttf", "serif": "Lora_700Bold.ttf"}
LICENSES = ("OFL-montserrat.txt", "OFL-lora.txt")
LOGO_SVG = os.path.join(BASE, "logo", "paloma_hotels.svg")
VCF = "suleyman-boylu.vcf"

ICON = {
    "phone": '<path d="M6.6 3.5h2.6l1.4 4.2-2 1.4a12 12 0 0 0 6.3 6.3l1.4-2 4.2 1.4v2.6a2 2 0 0 1-2.2 2A16.5 16.5 0 0 1 '
             '4.6 5.7a2 2 0 0 1 2-2.2z"/>',
    "office": '<path d="M4 20V6.5L12 3l8 3.5V20"/><path d="M9 20v-5h6v5M8 9h1M11.5 9h1M15 9h1M8 12h1M11.5 12h1M15 12h1"/>',
    "whatsapp": '<path d="M4.5 19.5l1.2-4A8 8 0 1 1 9 18.6z"/><path d="M9.2 8.6c.2-.5.6-.6.9-.6.4 0 .6.6.9 1.4.2.5-.4.9-.6'
                ' 1.2.6 1.2 1.6 2.2 2.9 2.8.3-.3.7-.9 1.2-.7.8.3 1.4.6 1.4 1 0 .3-.1.7-.6.9-.7.4-1.7.4-3-.2a8 8 0 0 1-3.4-3.3'
                'c-.5-1.1-.5-1.9.3-2.5z" fill="currentColor" stroke="none"/>',
    "mail": '<rect x="3.5" y="5.5" width="17" height="13" rx="2.5"/><path d="M4 7l8 6 8-6"/>',
    "pin": '<path d="M12 21s-6.5-6-6.5-11a6.5 6.5 0 0 1 13 0c0 5-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.4"/>',
    "save": '<circle cx="9" cy="8.5" r="3.5"/><path d="M3.5 19c.8-3.2 3-4.8 5.5-4.8 1.4 0 2.7.4 3.7 1.3M17.5 13v7M14 16.5h7"/>',
    "share": '<circle cx="17.5" cy="5.5" r="2.5"/><circle cx="6.5" cy="12" r="2.5"/><circle cx="17.5" cy="18.5" r="2.5"/>'
             '<path d="M8.7 10.8l6.6-4M8.7 13.2l6.6 4"/>',
    "arrow": '<path d="M9 5l7 7-7 7"/>',
}


def icon(k):
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{ICON[k]}</svg>')


def e(s):
    return html.escape(str(s))


def load():
    d = json.load(open(os.path.join(BASE, "bilgiler.json"), encoding="utf-8"))
    d["cep_e164"] = Q.phone_e164(d["cep"])
    d["sirket_e164"] = Q.phone_e164(d["sirket_tel"])
    d["cep_txt"] = Q.phone_display(d["cep_e164"])
    d["sirket_txt"] = Q.phone_display(d["sirket_e164"])
    return d


# ---------------------------------------------------------------- dosyalar

def subset_fonts(text):
    from fontTools import subset
    fdir = os.path.join(OUT, "fonts")
    shutil.rmtree(fdir, ignore_errors=True)
    os.makedirs(fdir)
    chars = text + "ABCÇDEFGĞHIİJKLMNOÖPQRSŞTUÜVWXYZabcçdefgğhıijklmnoöpqrsştuüvwxyz0123456789 .,:;·+-–—/@&()'\"!?"
    for key, fn in FONTS.items():
        opts = subset.Options()
        opts.flavor = "woff"
        opts.layout_features = ["kern", "liga", "locl", "tnum"]
        f = subset.load_font(os.path.join(A.FONT_DIR, fn), opts)
        s = subset.Subsetter(opts)
        s.populate(text=chars)
        s.subset(f)
        subset.save_font(f, os.path.join(fdir, key + ".woff"), opts)
    for lic in LICENSES:
        shutil.copy(os.path.join(A.FONT_DIR, lic), os.path.join(fdir, lic))


def vcard(d):
    first, last = d["isim"].split(" ", 1)
    street, district, city, country = d["adres"]
    lines = ["BEGIN:VCARD", "VERSION:3.0", f"N:{last};{first};;;", f"FN:{d['isim']}",
             f"ORG:{d['grup']};{d['otel']}", f"TITLE:{d['gorev']}",
             f"TEL;TYPE=CELL,VOICE:+{d['cep_e164']}", f"TEL;TYPE=WORK,VOICE:+{d['sirket_e164']}",
             f"EMAIL;TYPE=INTERNET:{d['eposta']}",
             f"ADR;TYPE=WORK:;;{street};{district};{city};;{country}", f"URL:{d['sayfa_url']}", "END:VCARD"]
    with open(os.path.join(OUT, VCF), "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(lines) + "\n")


def logo_html():
    """Paloma Hotels logosu (scripts/paloma_logo.py ile çizilen vektör), sayfanın içinde: rengi CSS'ten gelir."""
    return f'<span class="logo">{open(LOGO_SVG, encoding="utf-8").read().strip()}</span>'


CSS = """
@font-face{font-family:Montserrat;src:url(fonts/sans.woff) format("woff");font-weight:600;font-display:swap}
@font-face{font-family:Montserrat;src:url(fonts/sans-b.woff) format("woff");font-weight:700;font-display:swap}
@font-face{font-family:Lora;src:url(fonts/serif.woff) format("woff");font-weight:700;font-display:swap}
:root{--pb:#69A1BA;--pb2:#5690AA;--pbd:#2F6F8C;--deep:#173543;--sand:#F2F5F6;--ink:#16222B;--muted:#66727B;
  --line:#E3E9EC;--tint:#EAF3F7}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:var(--sand)}
body{font-family:Montserrat,system-ui,sans-serif;font-weight:600;color:var(--ink);-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.wrap{max-width:440px;margin:0 auto;min-height:100vh;background:var(--sand)}
.hero{position:relative;overflow:hidden;color:#fff;text-align:center;padding:52px 24px 176px;
  background:linear-gradient(165deg,#86B8CD 0%,var(--pb) 42%,var(--pb2) 100%)}
.hero .glow{position:absolute;inset:-40% -20% auto;height:120%;background:radial-gradient(closest-side,#ffffff38,transparent);
  pointer-events:none}
.logo{display:block;width:212px;margin:0 auto;color:#fff;position:relative}
.logo svg{display:block;width:100%;height:auto}
.hotel{display:flex;align-items:center;justify-content:center;gap:12px;margin-top:16px;font-size:13px;font-weight:600;
  letter-spacing:.42em;padding-left:.42em;color:#fff;position:relative}
.hotel:before,.hotel:after{content:"";width:28px;height:1px;background:#ffffffaa}
.waves{position:absolute;left:0;right:0;bottom:-1px;height:110px}
.waves svg{position:absolute;bottom:0;width:200%;height:100%;left:0}
.waves .w1{animation:drift 14s linear infinite;opacity:.35}
.waves .w2{animation:drift 9s linear infinite reverse;opacity:.5}
.waves .w3{animation:drift 18s linear infinite}
@keyframes drift{from{transform:translateX(0)}to{transform:translateX(-50%)}}
.card{position:relative;margin:-84px 18px 0;background:#fff;border-radius:24px;padding:62px 22px 22px;text-align:center;
  box-shadow:0 18px 50px rgba(23,53,67,.16)}
.av{position:absolute;left:50%;top:-46px;width:92px;height:92px;margin-left:-46px;border-radius:50%;
  background:linear-gradient(140deg,#7DB1C8,var(--pbd));display:grid;place-items:center;color:#fff;
  font-family:Lora;font-weight:700;font-size:31px;letter-spacing:.04em;border:5px solid #fff;
  box-shadow:0 10px 26px rgba(47,111,140,.32)}
h1{font-family:Lora;font-weight:700;font-size:30px;line-height:1.15}
.role{margin-top:9px;color:var(--pbd);font-size:13.5px;letter-spacing:.2em;text-transform:uppercase}
.org{margin-top:7px;color:var(--muted);font-size:14.5px}
.acts{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:22px}
.acts a{display:flex;flex-direction:column;align-items:center;gap:7px;font-size:12.5px;color:var(--ink)}
.acts a span{width:56px;height:56px;border-radius:18px;display:grid;place-items:center;background:var(--tint);
  color:var(--pbd);transition:transform .15s}
.acts a:active span{transform:scale(.94)}
.acts a span svg{width:25px;height:25px}
.acts a.wa span{background:#E7F7EE;color:#1E9E5A}
.list{margin:18px 18px 0;background:#fff;border-radius:22px;padding:6px 18px;box-shadow:0 8px 24px rgba(23,53,67,.06)}
.row{display:flex;align-items:center;gap:14px;padding:14px 0;border-bottom:1px solid var(--line)}
.row:last-child{border-bottom:0}
.row .i{width:40px;height:40px;border-radius:12px;background:var(--tint);color:var(--pbd);display:grid;place-items:center;
  flex:none}
.row .i svg{width:20px;height:20px}
.row small{display:block;color:var(--muted);font-size:12px;letter-spacing:.04em}
.row b{display:block;font-weight:700;font-size:15.5px;font-variant-numeric:tabular-nums;word-break:break-word}
.row.em b{font-size:14px;letter-spacing:-.01em}
.row .go{margin-left:auto;color:#B3C0C7;width:18px;height:18px;flex:none}
.save{display:flex;align-items:center;justify-content:center;gap:10px;margin:18px 18px 0;padding:17px;border-radius:18px;
  background:var(--deep);color:#fff;font-weight:700;font-size:16px;box-shadow:0 12px 26px rgba(23,53,67,.25)}
.save svg{width:22px;height:22px}
.share{display:flex;align-items:center;justify-content:center;gap:8px;margin:12px 18px 0;padding:14px;border-radius:16px;
  border:1.5px solid var(--line);color:var(--deep);font-weight:700;font-size:15px;background:#fff;width:calc(100% - 36px);
  font-family:inherit;cursor:pointer}
.share svg{width:19px;height:19px}
.foot{display:flex;flex-direction:column;align-items:center;gap:10px;color:var(--muted);font-size:12px;padding:28px 0 32px;
  letter-spacing:.12em}
.foot .logo{width:96px;color:var(--pb)}
.in{opacity:0;transform:translateY(14px);animation:up .6s cubic-bezier(.2,.7,.2,1) forwards}
@keyframes up{to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){.waves svg{animation:none!important}.in{animation:none;opacity:1;transform:none}}
"""


def wave_svg(cls, color, amp, y):
    pts = []
    for k in range(0, 801, 20):
        pts.append(f"{k},{y + amp * math.sin(k / 400 * 2 * math.pi * 2):.1f}")
    return (f'<svg class="{cls}" viewBox="0 0 800 110" preserveAspectRatio="none"><path fill="{color}" '
            f'd="M0,110 L{" L".join(pts)} L800,110 Z"/></svg>')


def page(d):
    first, last = d["isim"].split(" ", 1)
    ini = first[0] + last[0]
    wa = f"https://wa.me/{d['cep_e164']}?text=" + d["whatsapp_mesaj"].replace(" ", "%20").replace(",", "%2C")
    addr = ", ".join(d["adres"][:2]) + " / " + d["adres"][2]
    acts = [("phone", "Ara", f"tel:+{d['cep_e164']}", ""), ("whatsapp", "WhatsApp", wa, "wa"),
            ("mail", "E-posta", f"mailto:{d['eposta']}", ""), ("pin", "Konum", d["harita"], "")]
    a = "".join(f'<a class="{c}" href="{e(h)}"{" target=_blank rel=noopener" if h.startswith("http") else ""}>'
                f'<span>{icon(k)}</span>{e(t)}</a>' for k, t, h, c in acts)
    rows = [("phone", "Cep telefonu", d["cep_txt"], f"tel:+{d['cep_e164']}"),
            ("office", "Şirket hattı", d["sirket_txt"], f"tel:+{d['sirket_e164']}"),
            ("mail", "E-posta", d["eposta"], f"mailto:{d['eposta']}"),
            ("pin", "Adres", addr, d["harita"])]
    r = "".join(f'<a class="row{" em" if k == "mail" else ""}" href="{e(h)}"><span class="i">{icon(k)}</span><span><small>{e(lab)}</small>'
                f'<b>{e(v)}</b></span><svg class="go" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                f'stroke-width="2" stroke-linecap="round">{ICON["arrow"]}</svg></a>' for k, lab, v, h in rows)
    waves = (wave_svg("w1", "#A9CEDD", 10, 40) + wave_svg("w2", "#4D86A0", 8, 58) +
             wave_svg("w3", "#F2F5F6", 7, 78))
    delay = lambda k: f' style="animation-delay:{k * 0.08:.2f}s"'  # noqa: E731
    body = (f'<div class="wrap"><header class="hero"><div class="glow"></div>{logo_html()}'
            f'<span class="hotel">{e(d["otel"].split()[-1].upper())}</span><div class="waves">{waves}</div></header>'
            f'<section class="card in"{delay(1)}><div class="av">{e(ini)}</div><h1>{e(d["isim"])}</h1>'
            f'<p class="role">{e(d["gorev"])}</p><p class="org">{e(d["otel"])} · {e(d["grup"])}</p>'
            f'<nav class="acts">{a}</nav></section>'
            f'<div class="list in"{delay(3)}>{r}</div>'
            f'<a class="save in"{delay(5)} href="{VCF}" download>{icon("save")}Rehbere kaydet</a>'
            f'<button class="share in"{delay(6)} id="share">{icon("share")}Kartviziti paylaş</button>'
            f'<footer class="foot">{logo_html()}<span>{e(d["otel"])} · Belek</span></footer></div>')
    js = ("document.getElementById('share').onclick=async()=>{const u=location.href,t=document.title;"
          "if(navigator.share){try{await navigator.share({title:t,url:u})}catch(e){}}else{"
          "try{await navigator.clipboard.writeText(u);event.target.closest('button').lastChild.textContent="
          "' Bağlantı kopyalandı'}catch(e){}}}")
    title = f"{d['isim']} · {d['gorev']} · {d['otel']}"
    return (f'<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" '
            f'content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#69A1BA">'
            f'<title>{e(title)}</title><meta name="description" content="{e(d["isim"])} – {e(d["gorev"])}, '
            f'{e(d["otel"])}. Ara, WhatsApp, e-posta, rehbere kaydet."><meta property="og:title" content="{e(title)}">'
            f'<style>{CSS}</style></head><body>{body}<script>{js}</script></body></html>')


def screenshot(path=PREVIEW):
    from playwright.sync_api import sync_playwright
    top, full = path.replace(".png", "_ust.png"), path.replace(".png", "_tam.png")
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, reduced_motion="reduce")
        pg.goto("file://" + os.path.join(OUT, "index.html"))
        pg.wait_for_timeout(500)
        assert pg.evaluate("document.fonts.check('700 20px \"Lora\"')"), "yazı tipi yüklenmedi"
        assert pg.evaluate("document.documentElement.scrollWidth") <= 390, "yatay taşma"
        pg.screenshot(path=top)
        pg.screenshot(path=full, full_page=True)
        b.close()
    shots = [Image.open(top), Image.open(full)]
    h = max(s.height for s in shots)
    canvas = Image.new("RGB", (sum(s.width for s in shots) + 120, h + 120), (52, 56, 70))
    x = 40
    for s in shots:
        canvas.paste(s, (x, 60))
        x += s.width + 40
    canvas.save(path)
    for f in (top, full):
        os.remove(f)
    return path


def pack():
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for d, _, files in os.walk(OUT):
            for fn in sorted(files):
                full = os.path.join(d, fn)
                z.write(full, os.path.relpath(full, OUT))


def main():
    d = load()
    os.makedirs(OUT, exist_ok=True)
    doc = page(d)
    subset_fonts(html.unescape(doc))
    vcard(d)
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(doc)
    pack()
    print("sayfa:", os.path.relpath(os.path.join(OUT, "index.html"), A.ROOT), "→", d["sayfa_url"])
    print("önizleme:", os.path.relpath(screenshot(), A.ROOT))


if __name__ == "__main__":
    main()
