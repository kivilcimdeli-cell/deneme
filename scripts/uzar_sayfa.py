"""UZAR OTO LASTİK – isimlikteki "TARA" QR'ı ile açılan işletme sayfası (kırmızı, siyah, beyaz; telefona göre).

Sayfada: Hemen Ara, WhatsApp (hazır mesajlı), Instagram, Google'da değerlendir (yorum, konum, yol tarifi),
ödeme bilgileri (alıcı, banka, IBAN + tek dokunuşla kopyala, banka karekodu: kaydedip banka uygulamasında
galeriden okutulur) ve Rehbere Kaydet (vCard). Dış bağlantı yok: yazı tipleri ve simgeler sayfanın içinde.

Bilgiler `uzar_isimlik/bilgiler.json`dan okunur (scripts/qr_sistemi.py doğrular); bilgi değişince sayfa bu
komutla yeniden üretilir. Sayfa adresi değişmediği sürece basılmış isimlik aynen çalışır.

Yayın: işletmenin kendi (ücretsiz) hesabıyla, bu depodan bağımsız. Netlify Drop: app.netlify.com/drop sayfasına
`uzar_isimlik/site` klasörü sürüklenir, hesap açılıp site sahiplenilir, site adı `uzarotolastik` yapılır →
https://uzarotolastik.netlify.app/ (Cloudflare Pages "Direct Upload" de olur: uzarotolastik.pages.dev). Kesin adres
`bilgiler.json` → `sayfa_url`a yazılır; isimlikteki QR o adresten üretilir.

Çıktı : uzar_isimlik/site/ (index.html, karekod.png, uzar.vcf, og.png, fonts/*.woff), uzar_isimlik/uzar_site.zip,
        uzar_isimlik/sayfa_onizleme.png

Kullanım:
  pip install segno zxing-cpp playwright fonttools
  python3 scripts/uzar_sayfa.py
"""
import html
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import qr_sistemi as Q  # noqa: E402

OUT = os.path.join(A.ROOT, "uzar_isimlik", "site")
ZIP = os.path.join(A.ROOT, "uzar_isimlik", "uzar_site.zip")
PREVIEW = os.path.join(A.ROOT, "uzar_isimlik", "sayfa_onizleme.png")
STANDALONE = os.path.join(A.ROOT, "uzar_isimlik", "sayfa_onizleme.html")
RED, INK = "#d01c26", "#0d0d0f"
FONTS = {"barlow-black": "BarlowCondensed-Black.ttf", "barlow-xbold": "BarlowCondensed-ExtraBold.ttf",
         "outfit": "Outfit-SemiBold.ttf"}
CHARS = ("".join(chr(c) for c in range(0x20, 0x7F)) + "ÇçĞğİıÖöŞşÜüÂâÎîÛû·–—’‘“”…•₺→©")

# simgeler: WhatsApp ve Instagram Simple Icons (CC0), diğerleri Material Icons (Apache 2.0)
LOGOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logolar")
ICON = {
    "phone": "M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 "
             "0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 "
             "3.57.11.35.03.74-.25 1.02l-2.2 2.2z",
    "star": "M12 17.27 18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z",
    "bank": "M4 10v7h3v-7H4zm6 0v7h3v-7h-3zM2 22h19v-3H2v3zm14-12v7h3v-7h-3zm-4.5-9L2 6v2h19V6l-9.5-5z",
    "copy": "M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-"
            ".9-2-2-2zm0 16H8V7h11v14z",
    "person": "M15 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm-9-2V7H4v3H1v2h3v3h2v-3h3v-2H6zm9 4c-2.67 "
              "0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z",
    "qr": "M3 11h8V3H3v8zm2-6h4v4H5V5zM3 21h8v-8H3v8zm2-6h4v4H5v-4zM13 3v8h8V3h-8zm6 6h-4V5h4v4zM19 19h2v2h-2zM13 13h2v2"
          "h-2zM15 15h2v2h-2zM13 17h2v2h-2zM15 19h2v2h-2zM17 17h2v2h-2zM17 13h2v2h-2zM19 15h2v2h-2z",
    "download": "M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z",
}
BOLT = "-12,-50 28,-50 6,-10 38,-10 -28,50 -10,4 -38,4"     # isimlikteki şimşekle aynı çokgen


def logo_path(name):
    return re.search(r' d="([^"]+)"', open(os.path.join(LOGOS, name + ".svg")).read()).group(1)


def svg(path, cls="ic"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true"><path d="{path}"/></svg>'


def bolt_svg(cls="bolt"):
    return f'<svg class="{cls}" viewBox="-40 -50 80 100" aria-hidden="true"><polygon points="{BOLT}"/></svg>'


def tread_svg():
    """Lastik dişi şeridi (isimlikteki gibi ok biçimli bloklar)."""
    blocks = "".join(f'<polygon points="{x},0 {x + 7},0 {x + 14},7 {x + 7},14 {x},14 {x + 7},7"/>'
                     for x in range(0, 400, 18))
    return (f'<svg class="tread" viewBox="0 0 400 14" preserveAspectRatio="xMidYMid slice" aria-hidden="true">'
            f'{blocks}</svg>')


def subset_fonts():
    from fontTools import subset
    os.makedirs(os.path.join(OUT, "fonts"), exist_ok=True)
    for key, fn in FONTS.items():
        opts = subset.Options()
        opts.flavor = "woff"
        opts.layout_features = ["kern", "liga", "locl"]
        f = subset.load_font(os.path.join(A.FONT_DIR, fn), opts)
        s = subset.Subsetter(opts)
        s.populate(text=CHARS)
        s.subset(f)
        subset.save_font(f, os.path.join(OUT, "fonts", key + ".woff"), opts)
    for lic in ("OFL-barlowcondensed.txt", "OFL-outfit.txt"):
        with open(os.path.join(A.FONT_DIR, lic), "rb") as src, open(os.path.join(OUT, "fonts", lic), "wb") as dst:
            dst.write(src.read())


def karekod_png(info):
    """Banka karekodu: aynı içerik, siyah-beyaz, kaydedilip banka uygulamasında galeriden okutulur."""
    import segno
    path = os.path.join(OUT, "karekod.png")
    segno.make(info.karekod, error="m", micro=False).save(path, scale=12, border=4)
    assert Q.decode(Image.open(path).convert("L")) == [info.karekod]
    return path


def vcard(info):
    lines = ["BEGIN:VCARD", "VERSION:3.0", "N:;Uzar Oto Lastik;;;", "FN:Uzar Oto Lastik", "ORG:Uzar Oto Lastik",
             f"TEL;TYPE=CELL,VOICE:+{info.tel}", f"URL:{info.page}",
             f"ADR;TYPE=WORK:;;;{info.city.title()};;;Türkiye",
             f"X-SOCIALPROFILE;TYPE=instagram:https://www.instagram.com/{info.instagram}/",
             f"NOTE:IBAN {Q.iban_display(info.iban)} ({info.holder.title()}\\, {info.bank})", "END:VCARD"]
    with open(os.path.join(OUT, "uzar.vcf"), "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(lines) + "\n")


def og_image(info):
    """Bağlantı paylaşılınca (WhatsApp vb.) görünen kapak görseli, 1200 × 630."""
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), (13, 13, 15))
    dr = ImageDraw.Draw(im)
    for i, w in enumerate((70, 34, 16)):
        x = 800 + i * 120
        dr.polygon([(x, 0), (x + w, 0), (x + w - 330, H), (x - 330, H)], fill=(208, 28, 38))
    big = ImageFont.truetype(os.path.join(A.FONT_DIR, FONTS["barlow-black"]), 300)
    mid = ImageFont.truetype(os.path.join(A.FONT_DIR, FONTS["barlow-xbold"]), 64)
    dr.text((80, 70), "UZAR", font=big, fill=(244, 244, 242))
    dr.text((86, 420), "O T O   L A S T İ K", font=mid, fill=(208, 28, 38))
    dr.text((86, 500), "A N T A L Y A", font=ImageFont.truetype(os.path.join(A.FONT_DIR, FONTS["outfit"]), 34),
            fill=(162, 162, 168))
    im.save(os.path.join(OUT, "og.png"), optimize=True)


CSS = """
@font-face{font-family:"Barlow Condensed";font-weight:900;font-display:swap;src:url(fonts/barlow-black.woff) format("woff")}
@font-face{font-family:"Barlow Condensed";font-weight:800;font-display:swap;src:url(fonts/barlow-xbold.woff) format("woff")}
@font-face{font-family:"Outfit";font-weight:600;font-display:swap;src:url(fonts/outfit.woff) format("woff")}
:root{--red:#d01c26;--red2:#a5121b;--ink:#0d0d0f;--card:#18181b;--line:#2b2b30;--text:#f4f4f2;--muted:#a2a2a8;
  --paper:#f4f4f2;--cond:"Barlow Condensed","Arial Narrow",sans-serif;--ui:"Outfit",system-ui,-apple-system,"Segoe UI",sans-serif}
*{box-sizing:border-box;margin:0}
html{background:var(--ink);-webkit-text-size-adjust:100%}
body{background:var(--ink);color:var(--text);font:600 16px/1.35 var(--ui);min-height:100vh;
  padding-bottom:env(safe-area-inset-bottom)}
.wrap{max-width:460px;margin:0 auto;padding:0 16px 28px}
a{color:inherit;-webkit-tap-highlight-color:transparent}
.hero{position:relative;overflow:hidden;padding:44px 22px 30px;margin:0 -16px;isolation:isolate}
.hero::before,.hero::after,.hero i{content:"";position:absolute;top:-40px;bottom:-40px;background:var(--red);
  transform:skewX(-28deg);z-index:-1}
.hero::before{right:-34px;width:58px}
.hero::after{right:54px;width:22px}
.hero i{right:104px;width:9px}
.logo{display:flex;align-items:center;font:900 clamp(84px,30vw,128px)/.82 var(--cond);letter-spacing:.01em;
  text-transform:uppercase}
.logo .bolt{height:.86em;width:auto;margin-left:.04em;fill:var(--red);filter:drop-shadow(0 0 18px rgba(208,28,38,.45))}
.kind{margin-top:12px;font:800 26px/1 var(--cond);letter-spacing:.34em;color:var(--red)}
.city{margin-top:8px;font-size:13px;letter-spacing:.42em;color:var(--muted)}
.tread{display:block;width:calc(100% + 32px);height:14px;margin:0 -16px 22px;fill:var(--red)}
.lead{color:var(--muted);font-size:15px;margin:0 2px 14px}
.list{display:grid;gap:12px}
.btn{display:flex;align-items:center;gap:14px;min-height:72px;padding:12px 14px;border-radius:18px;
  background:var(--card);border:1px solid var(--line);text-decoration:none;transition:transform .12s,background .12s}
.btn:active{transform:scale(.98)}
.btn .ib{flex:none;display:grid;place-items:center;width:46px;height:46px;border-radius:14px;background:var(--red)}
.btn .ic{width:24px;height:24px;fill:#fff}
.btn .t{flex:1;min-width:0}
.btn b{display:block;font:800 22px/1.05 var(--cond);letter-spacing:.03em;text-transform:uppercase}
.btn small{display:block;margin-top:3px;font-size:14px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;
  white-space:nowrap}
.btn .chev{flex:none;width:10px;height:10px;border:solid var(--muted);border-width:2.5px 2.5px 0 0;
  transform:rotate(45deg);margin-right:6px}
.btn.primary{background:linear-gradient(115deg,var(--red),var(--red2));border-color:transparent;
  box-shadow:0 10px 30px -12px rgba(208,28,38,.7)}
.btn.primary .ib{background:#fff}
.btn.primary .ic{fill:var(--red)}
.btn.primary small,.btn.primary .chev{color:#ffe1e3;border-color:#ffe1e3}
.pay{margin-top:22px;background:var(--paper);color:var(--ink);border-radius:22px;padding:20px 18px 18px;
  position:relative;overflow:hidden;container-type:inline-size}
.pay::after{content:"";position:absolute;right:-18px;top:-30px;width:34px;height:110px;background:var(--red);
  transform:skewX(-28deg)}
.pay h2{display:flex;align-items:center;gap:8px;font:800 15px/1 var(--ui);letter-spacing:.2em;color:var(--red)}
.pay h2 .ic{width:20px;height:20px;fill:var(--red)}
.rows{margin:16px 0 4px;display:grid;grid-template-columns:auto 1fr;gap:6px 14px;font-size:15px}
.rows dt{color:#6b6b72}
.rows dd{font-weight:600}
.iban{margin:12px 0 14px;padding:14px 8px;border-radius:12px;background:#fff;border:1.5px dashed #c9c9cf;
  font:800 18px/1.1 var(--cond);font-size:min(27px,6.6cqi);letter-spacing:.03em;word-spacing:.08em;
  text-align:center;white-space:nowrap;user-select:all;-webkit-user-select:all}
.copy,.kk-open,.ghost{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;min-height:54px;
  border-radius:14px;font:800 20px/1 var(--cond);letter-spacing:.06em;text-transform:uppercase;cursor:pointer;
  text-decoration:none}
.copy{border:0;background:var(--ink);color:#fff}
.copy .ic{width:20px;height:20px;fill:#fff}
.copy.ok{background:#1d7a3a}
details.kk{margin-top:10px}
details.kk summary{list-style:none}
details.kk summary::-webkit-details-marker{display:none}
.kk-open{border:2px solid var(--ink);background:transparent;color:var(--ink)}
.kk-open .ic{width:20px;height:20px;fill:var(--ink)}
.kk-body{padding-top:14px;text-align:center}
.kk-body img{width:min(240px,70vw);height:auto;image-rendering:pixelated;border-radius:8px}
.kk-body p{margin:10px 4px 12px;font-size:14px;color:#4a4a52}
.kk-body a{color:var(--red);font-weight:600}
.ghost{margin-top:14px;border:1.5px solid #3a3a40;color:var(--text);background:transparent}
.ghost .ic{width:22px;height:22px;fill:var(--text)}
footer{margin-top:26px;text-align:center;color:#6b6b72;font-size:12px;letter-spacing:.3em}
footer .bolt{height:14px;width:auto;fill:var(--red);vertical-align:-2px;margin:0 6px}
.toast{position:fixed;left:50%;bottom:calc(22px + env(safe-area-inset-bottom));transform:translate(-50%,140%);
  background:#fff;color:var(--ink);border-left:6px solid var(--red);padding:12px 18px;border-radius:12px;
  font-weight:600;box-shadow:0 12px 30px rgba(0,0,0,.45);transition:transform .25s,opacity .25s;white-space:nowrap;
  opacity:0;pointer-events:none}
.toast.show{transform:translate(-50%,0);opacity:1}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""

JS = """
const toast=document.querySelector('.toast');let tt;
function say(m){toast.textContent=m;toast.classList.add('show');clearTimeout(tt);tt=setTimeout(()=>toast.classList.remove('show'),2200)}
async function copy(t){
  try{await navigator.clipboard.writeText(t);return true}catch(e){}
  const a=document.createElement('textarea');a.value=t;a.setAttribute('readonly','');a.style.position='fixed';a.style.opacity='0';
  document.body.appendChild(a);a.select();a.setSelectionRange(0,99);let ok=false;try{ok=document.execCommand('copy')}catch(e){}
  a.remove();return ok}
document.querySelectorAll('[data-copy]').forEach(b=>b.addEventListener('click',async()=>{
  const ok=await copy(b.dataset.copy);const l=b.querySelector('span');const o=l.textContent;
  if(ok){b.classList.add('ok');l.textContent='KOPYALANDI';say('IBAN kopyalandı – banka uygulamanıza yapıştırın')}
  else say('Kopyalanamadı: IBAN yazısına basılı tutun');
  setTimeout(()=>{b.classList.remove('ok');l.textContent=o},2000)}));
"""


def page(info):
    e = html.escape
    wa = Q.whatsapp_link(info)
    insta = f"https://www.instagram.com/{info.instagram}/"
    title = "Uzar Oto Lastik – Antalya"
    desc = "Uzar Oto Lastik, Antalya: hemen arayın, WhatsApp'tan yazın, Instagram'da takip edin, ödeme bilgileri."
    blank = ' target="_blank" rel="noopener"'
    btn = lambda href, icon, t, s, cls="", ext=True: (  # noqa: E731
        f'<a class="btn {cls}" href="{e(href)}"{blank if ext else ""}>'
        f'<span class="ib">{icon}</span><span class="t"><b>{e(t)}</b><small>{e(s)}</small></span>'
        f'<span class="chev"></span></a>')
    favicon = ("data:image/svg+xml," + f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='-40 -50 80 100'>"
               f"<polygon fill='%23d01c26' points='{BOLT}'/></svg>")
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="{INK}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(info.page)}">
<meta property="og:image" content="{e(info.page)}og.png">
<link rel="icon" href="{favicon}">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header class="hero"><i></i>
  <h1 class="logo" aria-label="Uzar">UZAR{bolt_svg()}</h1>
  <p class="kind">OTO LASTİK</p>
  <p class="city">{e(info.city.upper())}</p>
</header>
{tread_svg()}
<p class="lead">Bize tek dokunuşla ulaşın.</p>
<nav class="list">
  {btn("tel:+" + info.tel, svg(ICON["phone"]), "Hemen Ara", info.phone, "primary", ext=False)}
  {btn(wa, svg(logo_path("whatsapp")), "WhatsApp'tan Yaz", "Mesaj gönderin · " + info.phone)}
  {btn(insta, svg(logo_path("instagram")), "Instagram", "@" + info.instagram)}
  {btn(info.google, svg(ICON["star"]), "Google'da Değerlendirin", "Yorumlar · konum · yol tarifi")}
</nav>
<section class="pay" aria-labelledby="odeme">
  <h2 id="odeme">{svg(ICON["bank"])}ÖDEME BİLGİLERİ</h2>
  <dl class="rows"><dt>Alıcı</dt><dd>{e(info.holder)}</dd><dt>Banka</dt><dd>{e(info.bank)}</dd></dl>
  <div class="iban" aria-label="IBAN">{e(Q.iban_display(info.iban))}</div>
  <button class="copy" type="button" data-copy="{e(info.iban)}">{svg(ICON["copy"])}<span>IBAN'ı Kopyala</span></button>
  <details class="kk">
    <summary class="kk-open">{svg(ICON["qr"])}Karekod ile Öde</summary>
    <div class="kk-body">
      <img src="karekod.png" width="636" height="636" alt="{e(info.bank)} karekodu – {e(info.holder)}">
      <p>Karekodu kaydedin; banka uygulamanızda <b>Karekod ile Öde</b> → <b>Galeriden seç</b>.
         Dükkândaysanız isimlikteki <b>KAREKOD İLE ÖDE</b> kodunu doğrudan okutun.</p>
      <a href="karekod.png" download="uzar-karekod.png">Karekodu kaydet</a>
    </div>
  </details>
</section>
<a class="ghost" href="uzar.vcf" download="Uzar Oto Lastik.vcf">{svg(ICON["person"])}Rehbere Kaydet</a>
<footer>UZAR{bolt_svg()}OTO LASTİK · {e(info.city.upper())}</footer>
</div>
<div class="toast" role="status" aria-live="polite"></div>
<script>{JS}</script>
</body>
</html>
"""


def screenshot(path=PREVIEW):
    """Telefon ekranında (390 px) üst görünüm ve tüm sayfa (karekod açık) yan yana."""
    from playwright.sync_api import sync_playwright
    url = "file://" + os.path.join(OUT, "index.html")
    shots = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        pg.goto(url)
        pg.wait_for_timeout(300)
        top = path.replace(".png", "_ust.png")
        pg.screenshot(path=top)
        pg.click("details.kk summary")
        pg.wait_for_timeout(200)
        full = path.replace(".png", "_tam.png")
        pg.screenshot(path=full, full_page=True)
        assert pg.evaluate("document.fonts.check('900 20px \"Barlow Condensed\"')")
        b.close()
    shots = [Image.open(top), Image.open(full)]
    h = max(s.height for s in shots)
    canvas = Image.new("RGB", (sum(s.width for s in shots) + 120, h + 120), (226, 228, 232))
    x = 40
    for s in shots:
        canvas.paste(s, (x, 60))
        x += s.width + 40
    canvas.save(path)
    for f in (top, full):
        os.remove(f)
    return path


def pack():
    """Yüklemeye hazır zip: içinde `uzar_site/` klasörü (index.html en üstte)."""
    import zipfile
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for d, _, files in os.walk(OUT):
            for fn in sorted(files):
                full = os.path.join(d, fn)
                z.write(full, os.path.join("uzar_site", os.path.relpath(full, OUT)))


def standalone(path=STANDALONE):
    """Tek dosyalık önizleme: yazı tipleri, karekod ve kartvizit sayfanın içine gömülü (yayın için değil)."""
    import base64
    import urllib.parse
    data = lambda fn, mime: f"data:{mime};base64," + base64.b64encode(  # noqa: E731
        open(os.path.join(OUT, fn), "rb").read()).decode()
    page_html = open(os.path.join(OUT, "index.html"), encoding="utf-8").read()
    for key in FONTS:
        page_html = page_html.replace(f"url(fonts/{key}.woff)", f"url({data('fonts/' + key + '.woff', 'font/woff')})")
    kk = data("karekod.png", "image/png")
    page_html = page_html.replace('src="karekod.png"', f'src="{kk}"').replace('href="karekod.png"', f'href="{kk}"')
    vcf = "data:text/vcard;charset=utf-8," + urllib.parse.quote(open(os.path.join(OUT, "uzar.vcf"), encoding="utf-8").read())
    page_html = page_html.replace('href="uzar.vcf"', f'href="{vcf}"')
    with open(path, "w", encoding="utf-8") as f:
        f.write(page_html)
    return path


def main():
    info = Q.load()
    os.makedirs(OUT, exist_ok=True)
    subset_fonts()
    karekod_png(info)
    vcard(info)
    og_image(info)
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(page(info))
    pack()
    standalone()
    print("sayfa:", os.path.relpath(os.path.join(OUT, "index.html"), A.ROOT), "→", info.page)
    print("önizleme:", os.path.relpath(screenshot(), A.ROOT))


if __name__ == "__main__":
    main()
