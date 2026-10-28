"""AUTO TUFAN – Hasar Onarım (Kepez, Antalya): dijital kartvizit sayfası (isimlikteki QR bu sayfayı açar).

Paloma'nın 4. sürümü gibi tek parça: her bilgi bir kez geçer. Renkler isimlikteki gibi siyah, altın ve beyaz; yazı
tipi logodaki Poppins, logo fırça T (scripts/autotufan_logo.py).
  * Arka plan canlı: araba boyası gibi parlak siyah yüzey (WebGL). İçinde altın metalik pullar ışıkta yanıp söner,
    üzerinden yavaşça ışık bandı geçer (galeride kaportaya vuran ışık gibi). Telefon "hareketi azalt" diyorsa tek
    kare, durağan; WebGL yoksa koyu degrade.
  * Üstte ortada: altın fırça T (açılışta fırçayla çizilir gibi açılır, ara ara üstünden parıltı geçer), Auto
    Tufan, HASAR ONARIM, Kepez · Antalya.
  * Altta tek kart: telefon (ara + WhatsApp), Instagram, web sitesi, konum, Google yorumları (beş altın yıldız),
    IBAN (dokununca kopyalanır; QR düğmesi ödeme penceresini açar). Rehbere kaydet ve Paylaş.
  * Paylaş: alttan açılan pencerede isimlikteki QR (DİJİTAL | KARTVİZİT), Kopyala / Gönder.
  * Ödeme: IBAN karekodu (bilgiler.json'da `iban_karekod` varsa bankanın karekodu, yoksa IBAN'ın kendisi) ve IBAN.
  * Pencereler <dialog> değil: JavaScript açar (geri tuşu kapatır); JavaScript yoksa (Android'in HTML
    görüntüleyicisi gibi) #qr / #odeme bağlantısı CSS :target ile açar. Uygulama içi önizlemede de çalışır.
IBAN şimdilik örnek (`iban_ornek`); gerçeği gelince bilgiler.json'a yazılıp betik yeniden çalıştırılır.

Yayın: ortak Cloudflare hesabında (`qrsistem`) `deneme123` adlı Worker'a `autotufan_site.zip` yüklenir; adres
`https://deneme123.qrsistem.workers.dev` (isimlikteki QR bu adresi açar). `#qr` Paylaş, `#odeme` ödeme penceresini
açık getirir.

Çıktı : autotufan_isimlik/site/, autotufan_site.zip, sayfa_onizleme.png (sayfa, Paylaş, Ödeme), sayfa_tur.gif,
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
from PIL import Image, ImageDraw, ImageFilter, ImageFont

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
FONTS = {"p4": "Poppins-Regular.ttf", "p5": "Poppins-Medium.ttf", "p6": "Poppins-SemiBold.ttf",
         "p7": "Poppins-Bold.ttf"}
LICENSES = ("OFL-poppins.txt",)
VCF = "auto-tufan.vcf"
OG = "paylas.jpg"
ICON_PNG = "simge.png"
LOGO = json.load(open(L.JSON, encoding="utf-8"))
GOLD = (232, 182, 90)

ICON = {
    "phone": '<path d="M6.6 3.5h2.6l1.4 4.2-2 1.4a12 12 0 0 0 6.3 6.3l1.4-2 4.2 1.4v2.6a2 2 0 0 1-2.2 2A16.5 16.5 0 0 1 '
             '4.6 5.7a2 2 0 0 1 2-2.2z"/>',
    "whatsapp": '<path d="M4.5 19.5l1.2-4A8 8 0 1 1 9 18.6z"/><path class="f" fill="currentColor" stroke="none" '
                'd="M9.2 8.6c.2-.5.6-.6.9-.6.4 0 .6.6.9 1.4.2.5-.4.9-.6 1.2.6 1.2 1.6 2.2 2.9 2.8.3-.3.7-.9 1.2-.7.8.3 '
                '1.4.6 1.4 1 0 .3-.1.7-.6.9-.7.4-1.7.4-3-.2a8 8 0 0 1-3.4-3.3c-.5-1.1-.5-1.9.3-2.5z"/>',
    "instagram": '<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/>'
                 '<circle class="f" fill="currentColor" stroke="none" cx="17.2" cy="6.8" r="1.1"/>',
    "globe": '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.5 2.6 3.6 5.4 3.6 8.5s-1.1 5.9-3.6 8.5M12 '
             '3.5C9.5 6.1 8.4 8.9 8.4 12s1.1 5.9 3.6 8.5"/>',
    "pin": '<path d="M12 21s-6.5-6-6.5-11a6.5 6.5 0 0 1 13 0c0 5-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.4"/>',
    "star": '<path d="M12 3.8l2.5 5.2 5.6.7-4.1 3.9 1 5.6L12 16.5l-5 2.7 1-5.6-4.1-3.9 5.6-.7z"/>',
    "bank": '<path d="M3.5 9.5L12 4.5l8.5 5M5.5 10.5v6.5M9.8 10.5v6.5M14.2 10.5v6.5M18.5 10.5v6.5M3.5 19.5h17"/>',
    "save": '<circle cx="9" cy="8.5" r="3.5"/><path d="M3.5 19c.8-3.2 3-4.8 5.5-4.8 1.4 0 2.7.4 3.7 1.3M17.5 13v7M14 16.5h7"/>',
    "share": '<circle cx="17.5" cy="5.5" r="2.5"/><circle cx="6.5" cy="12" r="2.5"/><circle cx="17.5" cy="18.5" r="2.5"/>'
             '<path d="M8.7 10.8l6.6-4M8.7 13.2l6.6 4"/>',
    "qr": '<rect x="4" y="4" width="6" height="6" rx="1"/><rect x="14" y="4" width="6" height="6" rx="1"/>'
          '<rect x="4" y="14" width="6" height="6" rx="1"/><path d="M14 14h2.5v2.5M20 14v.5M14 20h.5M17.5 17.5H20V20"/>',
    "copy": '<rect x="8.5" y="8.5" width="11.5" height="11.5" rx="2.5"/><path d="M15.5 5.5A2 2 0 0 0 13.5 4H6a2 2 0 0 0-2 '
            '2v7.5a2 2 0 0 0 1.5 1.94"/>',
    "close": '<path d="M6.5 6.5l11 11M17.5 6.5l-11 11"/>',
}


def icon(k, draw=False, width=1.4):
    """draw: çizgiler açılışta çizilsin diye her çizgi parçasına pathLength=1 (dolgulu parça, class="f", hariç)."""
    body = ICON[k]
    if draw:
        for tag in ("<path ", "<rect ", "<circle "):
            body = body.replace(tag + "d=", tag + 'pathLength="1" d=').replace(tag + "x=", tag + 'pathLength="1" x=')
            body = body.replace(tag + "cx=", tag + 'pathLength="1" cx=')
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{width}" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{body}</svg>')


def e(s):
    return html.escape(str(s))


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
    return d


# ---------------------------------------------------------------- dosyalar

def _has_brotli():
    """woff2 için fontTools brotli ister; yoksa woff."""
    import importlib.util
    return importlib.util.find_spec("brotli") is not None


def subset_fonts(text):
    from fontTools import subset
    fdir = os.path.join(OUT, "fonts")
    os.makedirs(fdir, exist_ok=True)
    chars = text + "ABCÇDEFGĞHIİJKLMNOÖPQRSŞTUÜVWXYZabcçdefgğhıijklmnoöpqrsştuüvwxyz0123456789 .,:;·+-–—/@&()'\"!?→"
    for key, fn in FONTS.items():
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
             f"TITLE:{d['hizmet'].title()}", f"TEL;TYPE=WORK,CELL,VOICE:+{d['tel_e164']}",
             f"ADR;TYPE=WORK:;;;{d['konum'].split(',')[0].strip()};{d['sehir'].title()};;Türkiye",
             f"URL:{d['web']}", f"URL:{d['sayfa_url']}", f"X-SOCIALPROFILE;TYPE=instagram:https://instagram.com/{d['insta']}",
             "END:VCARD"]
    with open(os.path.join(OUT, VCF), "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(lines) + "\n")


def flakes_bg(W, H, seed=4):
    """Koyu, altın pullu boya yüzeyi (paylaşım görseli ve simge için durağan)."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:H, 0:W]
    base = 14 + 10 * np.exp(-(((x - W * 0.5) / (W * 0.55)) ** 2 + ((y - H * 0.3) / (H * 0.7)) ** 2))
    band = np.exp(-(((x * 0.55 + y) / H - 0.9) / 0.22) ** 2)
    img = np.stack([base + 40 * band * 0.95, base + 40 * band * 0.72, base + 40 * band * 0.32], -1)
    n = int(W * H / 90)
    px, py = rng.integers(0, W, n), rng.integers(0, H, n)
    k = rng.random(n) ** 6 * (0.3 + band[py, px] * 1.5)
    for c, g in enumerate(GOLD):
        np.add.at(img[..., c], (py, px), k * g)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    return im.filter(ImageFilter.GaussianBlur(0.6))


def t_image(h, colour=GOLD):
    return AT.t_raster(h, colour)


def og_image(d):
    """Bağlantı paylaşılınca görünen görsel (1200 × 630): altın pullu siyah zemin, T, Auto Tufan, HASAR ONARIM."""
    W, H = 1200, 630
    im = flakes_bg(W, H).convert("RGBA")
    T = t_image(170)
    im.paste(T, ((W - T.width) // 2, 70), T)
    dr = ImageDraw.Draw(im)
    f = lambda k, n: ImageFont.truetype(os.path.join(A.FONT_DIR, FONTS[k]), n)  # noqa: E731
    big = f("p6", 92)
    dr.text((W / 2 - dr.textlength(d["isim"], font=big) / 2, 268), d["isim"], font=big, fill=(246, 246, 242))
    sm = f("p6", 30)
    s, gap = AT.SERVICE, 16
    w = sum(dr.textlength(ch, font=sm) for ch in s) + gap * (len(s) - 1)
    x = W / 2 - w / 2
    for ch in s:
        dr.text((x, 400), ch, font=sm, fill=GOLD)
        x += dr.textlength(ch, font=sm) + gap
    loc = f"{d['konum'].replace(', ', ' · ')}  ·  {d['tel_txt']}"
    dr.text((W / 2 - dr.textlength(loc, font=f("p4", 28)) / 2, 470), loc, font=f("p4", 28), fill=(200, 200, 204))
    im.convert("RGB").save(os.path.join(OUT, OG), "JPEG", quality=86, optimize=True)


def touch_icon():
    """Ana ekran / sekme simgesi (180 × 180): siyah zeminde altın fırça T."""
    im = flakes_bg(180, 180, 9).convert("RGBA")
    T = t_image(84)
    im.paste(T, ((180 - T.width) // 2, (180 - T.height) // 2), T)
    im.convert("RGB").save(os.path.join(OUT, ICON_PNG), optimize=True)


# ---------------------------------------------------------------- parçalar

def t_svg(cls):
    """Fırça T (altın degrade) ve üstünden geçen parıltı (T'nin içiyle kırpılır)."""
    w, h = LOGO["svg_boyut"]
    return (f'<svg class="{cls}" viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="Auto Tufan logosu">'
            f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F7CB72"/>'
            f'<stop offset=".55" stop-color="#E8AE4C"/><stop offset="1" stop-color="#D4902E"/></linearGradient>'
            f'<clipPath id="tc"><path d="{LOGO["d"]}" fill-rule="evenodd"/></clipPath></defs>'
            f'<path class="tp" d="{LOGO["d"]}" fill="url(#g)" fill-rule="evenodd"/>'
            f'<g clip-path="url(#tc)"><rect class="gleam" x="-400" y="-200" width="260" height="{h + 400:.0f}" '
            f'fill="#fff" opacity=".55" transform="skewX(-20)"/></g></svg>')


def stars_svg():
    one = "M12 3.8l2.5 5.2 5.6.7-4.1 3.9 1 5.6L12 16.5l-5 2.7 1-5.6-4.1-3.9 5.6-.7z"
    return ('<span class="stars" aria-label="5 yıldız">' + "".join(
        f'<svg viewBox="0 0 24 24" style="--s:{k}" aria-hidden="true"><path d="{one}"/></svg>' for k in range(5))
        + "</span>")


def qr_svg(content, label):
    """QR: koyu kareler ayrı ayrı; --d çapraz dalganın gecikmesi (ms)."""
    import segno
    q = segno.make(content, error="m", micro=False, boost_error=True)
    m = [[bool(v) for v in row] for row in q.matrix]
    n, qz = len(m), 2
    k = 1100 / (2 * n)
    rects = "".join(f'<rect class="m" x="{x + qz}" y="{y + qz}" width="1" height="1" style="--d:{(x + y) * k:.0f}"/>'
                    for y, row in enumerate(m) for x, v in enumerate(row) if v)
    s = n + 2 * qz
    return (f'<svg viewBox="0 0 {s} {s}" shape-rendering="crispEdges" role="img" aria-label="{e(label)}">'
            f'<rect width="{s}" height="{s}" fill="#fff"/>{rects}</svg>')


def letters(text, cls=""):
    return "".join(f'<span class="{cls}" style="--i:{k}">{e(ch) if ch != " " else "&nbsp;"}</span>'
                   for k, ch in enumerate(text))


CSS = """
@font-face{font-family:Poppins;src:url(fonts/p4.EXT) format("FMT");font-weight:400;font-display:swap}
@font-face{font-family:Poppins;src:url(fonts/p5.EXT) format("FMT");font-weight:500;font-display:swap}
@font-face{font-family:Poppins;src:url(fonts/p6.EXT) format("FMT");font-weight:600;font-display:swap}
@font-face{font-family:Poppins;src:url(fonts/p7.EXT) format("FMT");font-weight:700;font-display:swap}
:root{--gold:#E8B65A;--gold2:#F7CB72;--ink:#F4F2EE;--muted:#8E8C88;--line:rgba(255,255,255,.08);
  --card:rgba(17,17,19,.94);--edge:rgba(232,182,90,.22);--tint:rgba(232,182,90,.10);--wa:#3CC57F;
  --e:cubic-bezier(.2,.75,.2,1);color-scheme:dark}
*{box-sizing:border-box;margin:0;padding:0}
html{background:#08080A}
body{font-family:Poppins,system-ui,sans-serif;font-weight:400;color:var(--ink);-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
button{font:inherit;color:inherit;background:none;border:0;cursor:pointer;text-align:left}
[hidden]{display:none!important}
.wrap{position:relative;max-width:440px;margin:0 auto;min-height:100vh;min-height:100svh;display:flex;flex-direction:column}

/* ---------------- arka plan: parlak siyah boya, altın pullar, geçen ışık (WebGL); yoksa degrade */
.bg{position:fixed;top:0;left:50%;width:min(440px,100%);height:100vh;height:100lvh;transform:translateX(-50%);
  overflow:hidden;background:radial-gradient(120% 70% at 50% 25%,#26221c 0,#0f0f11 55%,#08080a 100%)}
.bg canvas{position:absolute;inset:0;width:100%;height:100%;display:block;opacity:0;transition:opacity 1.2s ease}
.bg canvas.on{opacity:1}

/* ---------------- üst: logo, ad, hizmet, yer */
.top{position:relative;flex:1 0 auto;min-height:300px;display:flex;flex-direction:column;align-items:center;
  justify-content:center;padding:34px 24px 58px;text-align:center}
.tlogo{width:142px;height:auto;display:block;overflow:visible;filter:drop-shadow(0 6px 18px rgba(232,170,70,.25))}
h1{margin-top:14px;font-weight:600;font-size:clamp(34px,10vw,42px);line-height:1.05;letter-spacing:.01em}
h1 span{display:inline-block}
.svc{margin-top:10px;font-weight:600;font-size:12.5px;letter-spacing:.42em;margin-right:-.42em;color:var(--gold)}
.loc{display:inline-flex;align-items:center;gap:7px;margin-top:14px;font-size:12px;letter-spacing:.14em;color:var(--muted)}
.loc svg{width:14px;height:14px;color:var(--gold)}
.rule{display:block;width:46px;height:1.5px;margin:16px auto 0;background:linear-gradient(90deg,transparent,var(--gold),transparent)}

/* ---------------- kart: her bilgi bir kez */
.card{position:relative;z-index:1;margin-top:-26px;background:var(--card);border-radius:26px 26px 0 0;
  border:1px solid var(--edge);border-bottom:0;padding:6px 22px calc(22px + env(safe-area-inset-bottom));
  box-shadow:0 -14px 40px rgba(0,0,0,.5);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px)}
.rows{list-style:none}
.rows li{position:relative;display:flex;align-items:center;gap:12px;padding:12px 0}
.rows li:after{content:"";position:absolute;left:0;right:0;bottom:0;height:1px;background:var(--line);transform-origin:left}
.v{flex:1;min-width:0;display:block}
.v:after{content:"";position:absolute;inset:0}
.v small{display:block;font-weight:500;font-size:9.5px;letter-spacing:.28em;color:var(--muted);text-transform:uppercase}
.v b{display:block;margin-top:3px;font-weight:400;font-size:19px;letter-spacing:.01em;white-space:nowrap;
  overflow:hidden;text-overflow:ellipsis;font-variant-numeric:lining-nums}
.tel b{font-size:22px;letter-spacing:.02em}
.ib b{font-size:15px;letter-spacing:.04em}
.acts{display:flex;gap:8px;flex:none}
.ic{position:relative;width:42px;height:42px;border-radius:50%;display:grid;place-items:center;
  border:1px solid rgba(232,182,90,.35);color:var(--gold);transition:transform .15s,background .15s}
span.ic{pointer-events:none}
a.ic,button.ic{z-index:1}
.ic svg{width:19px;height:19px}
.ic.wa{color:var(--wa);border-color:rgba(60,197,127,.4)}
.v:active~.acts span.ic,.ic:active{transform:scale(.92);background:var(--tint)}
@media (hover:hover){.rows li:hover span.ic,a.ic:hover,button.ic:hover{background:var(--tint)}}
.stars{display:inline-flex;gap:3px;vertical-align:-2px;margin-right:8px}
.stars svg{width:15px;height:15px;fill:var(--gold)}
.btns{display:grid;grid-template-columns:1.55fr 1fr;gap:10px;margin-top:18px}
.save,.share{position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;gap:10px;height:54px;
  border-radius:14px;font-weight:600;font-size:11px;letter-spacing:.22em;white-space:nowrap}
.save{background:linear-gradient(135deg,#F7CB72,#E3A447);color:#16120B}
.share{border:1px solid rgba(232,182,90,.45);color:var(--ink)}
.save svg{width:20px;height:20px}
.share svg{width:19px;height:19px}
.save b,.share b{font-weight:600;margin-right:-.22em}
.save:after{content:"";position:absolute;top:0;bottom:0;left:-45%;width:40%;
  background:linear-gradient(100deg,transparent,rgba(255,255,255,.45),transparent)}
.toast{position:fixed;left:50%;bottom:calc(24px + env(safe-area-inset-bottom));transform:translate(-50%,calc(100% + 60px));
  z-index:20;visibility:hidden;
  padding:12px 18px;border-radius:12px;background:#1b1a17;border:1px solid var(--edge);color:var(--ink);font-size:13px;
  box-shadow:0 10px 30px rgba(0,0,0,.5);transition:transform .35s var(--e),visibility .35s;white-space:nowrap}
.toast.on{transform:translate(-50%,0);visibility:visible}

/* ---------------- pencereler: Paylaş (site QR) ve Ödeme (IBAN karekodu) */
/* Pencere: JavaScript açar (.on; telefonun geri tuşu kapatır). JavaScript yoksa (ör. Android'in HTML
   görüntüleyicisi) #qr / #odeme bağlantısı :target ile açar, # kapatır. Kapanırken görünürlük gecikmeli kalkar. */
.sheet{position:fixed;top:0;right:0;bottom:0;left:0;z-index:30;visibility:hidden;transition:visibility 0s .5s}
.sheet:target,.sheet.on{visibility:visible;transition:none}
.scrim{position:absolute;top:0;right:0;bottom:0;left:0;background:rgba(0,0,0,.6);opacity:0;transition:opacity .35s ease}
.panel{position:absolute;left:50%;bottom:0;width:min(440px,100%);max-height:100%;overflow:auto;
  transform:translate(-50%,104%);transition:transform .5s var(--e);background:#121214;border:1px solid var(--edge);
  border-bottom:0;border-radius:26px 26px 0 0;padding:18px 22px calc(22px + env(safe-area-inset-bottom));
  box-shadow:0 -14px 40px rgba(0,0,0,.6)}
.sheet:target .scrim,.sheet.on .scrim{opacity:1}
.sheet:target .panel,.sheet.on .panel{transform:translate(-50%,0)}
.ph{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
.ph p{font-weight:700;font-size:12px;letter-spacing:.32em}
.x{width:40px;height:40px;margin-right:-8px;border-radius:50%;display:grid;place-items:center;color:var(--muted)}
.x svg{width:20px;height:20px}
.qcard{display:flex;flex-direction:column;align-items:center;padding:30px 20px 22px;border-radius:20px;
  background:radial-gradient(120% 90% at 50% 0,#2a2419,#141311 70%);border:1px solid rgba(232,182,90,.35)}
.tile{position:relative;width:196px;padding:10px;background:#fff;border-radius:10px}
.tile svg{display:block;width:100%;height:auto}
.tile .m{fill:#111;transform-box:fill-box;transform-origin:center}
.vf{position:absolute;inset:-12px;pointer-events:none}
.vf i{position:absolute;width:22px;height:22px;border:2px solid var(--gold)}
.vf i:nth-child(1){left:0;top:0;border-right:0;border-bottom:0}
.vf i:nth-child(2){right:0;top:0;border-left:0;border-bottom:0}
.vf i:nth-child(3){left:0;bottom:0;border-right:0;border-top:0}
.vf i:nth-child(4){right:0;bottom:0;border-left:0;border-top:0}
.qcap{display:flex;align-items:center;gap:14px;margin-top:24px;padding-left:.34em;font-weight:600;font-size:11px;
  letter-spacing:.34em;color:var(--gold)}
.qcap i{width:1.2px;height:15px;background:var(--gold)}
.hint{margin-top:14px;text-align:center;color:var(--muted);font-size:13px;line-height:1.5}
.hint b{display:block;font-weight:500;color:var(--ink);letter-spacing:.03em}
.sel{-webkit-user-select:all;user-select:all}
.pbtns{display:flex;gap:10px;margin-top:16px}
.pbtns>*{flex:1}

/* ---------------- açılış */
.mo .tp{animation:brush 1.1s cubic-bezier(.6,.05,.3,1) .25s both}
.mo .gleam{animation:gleam 6s ease-in-out 2.6s infinite}
h1 span{animation:rise .8s var(--e) calc(.95s + var(--i)*.04s) both}
.svc{animation:track 1.1s var(--e) 1.35s both}
.loc{animation:fade-up .8s var(--e) 1.6s both}
.rule{animation:grow-x .9s var(--e) 1.5s both}
.card{animation:up 1s var(--e) 1.35s both}
.rows li{animation:slide .65s var(--e) calc(1.8s + var(--i)*.08s) both}
.rows li:after{animation:grow-x .9s var(--e) calc(1.9s + var(--i)*.08s) both}
.mo .ic [pathLength]{stroke-dasharray:1;stroke-dashoffset:1;animation:draw .8s ease-out calc(2.05s + var(--i)*.08s) forwards}
.ic .f{animation:fade .4s ease-out calc(2.5s + var(--i)*.08s) both}
.stars svg{animation:pop .5s var(--e) calc(2.4s + var(--s)*.09s) both}
.btns{animation:fade-up .8s var(--e) 2.3s both}
.save:after{animation:shine 5s ease-in-out 3.4s infinite}
.ic.wa:before{content:"";position:absolute;inset:-1px;border-radius:50%;border:1.5px solid var(--wa);opacity:0;
  pointer-events:none}
.mo .ic.wa:before{animation:ring 5s ease-out 3.4s infinite}
.mo .sheet .m{opacity:0}
.mo .sheet:target .m,.mo .sheet.on .m{animation:px .45s var(--e) calc(.25s + var(--d)*1ms) both}
.vf i{animation:breathe 2.8s ease-in-out infinite}
.vf i:nth-child(2),.vf i:nth-child(3){animation-delay:.2s}

@keyframes brush{from{clip-path:inset(0 100% 0 0);opacity:.2}to{clip-path:inset(0 0 0 0);opacity:1}}
@keyframes gleam{0%,70%{transform:skewX(-20deg) translateX(0)}100%{transform:skewX(-20deg) translateX(1900px)}}
@keyframes rise{from{opacity:0;transform:translateY(60%)}to{opacity:1;transform:none}}
@keyframes track{from{opacity:0;letter-spacing:.9em}to{opacity:1;letter-spacing:.42em}}
@keyframes grow-x{from{transform:scaleX(0)}to{transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes fade-up{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes up{from{transform:translateY(100%)}to{transform:none}}
@keyframes slide{from{opacity:0;transform:translateX(-18px)}to{opacity:1;transform:none}}
@keyframes draw{to{stroke-dashoffset:0}}
@keyframes pop{from{opacity:0;transform:scale(.3)}to{opacity:1;transform:none}}
@keyframes px{from{opacity:0;transform:scale(.2)}to{opacity:1;transform:none}}
@keyframes breathe{0%,100%{transform:none;opacity:1}50%{transform:scale(1.12);opacity:.6}}
@keyframes shine{0%,78%{left:-45%}100%{left:125%}}
@keyframes ring{0%{opacity:.6;transform:scale(1)}40%,100%{opacity:0;transform:scale(1.6)}}
@media (prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}}
"""

SEA_VS = "attribute vec2 p;varying vec2 v;void main(){v=vec2(p.x*.5+.5,.5-p.y*.5);gl_Position=vec4(p,0.,1.);}"
# Boya: kaportanın kıvrımı (yavaş değişen gürültü) koyu yüzeyi aydınlatır; çapraz ışık bandı bu kıvrıma göre bükülerek
# geçer; ızgaradaki pulların her biri kendi hızında yanıp söner, ışık bandında daha parlak. k: css piksel → cihaz.
SEA_FS = """#ifdef GL_FRAGMENT_PRECISION_HIGH
precision highp float;
#else
precision mediump float;
#endif
uniform vec2 r;uniform float t,k;varying vec2 v;
float h(vec2 p){p=fract(p*vec2(123.34,456.21));p+=dot(p,p+45.32);return fract(p.x*p.y);}
float nz(vec2 p){vec2 i=floor(p),f=fract(p),u=f*f*(3.-2.*f);
return mix(mix(h(i),h(i+vec2(1,0)),u.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),u.x),u.y);}
void main(){vec2 fc=v*r;vec2 q=fc/r.y;
float c=nz(q*1.2+vec2(0.,t*.03))*.6+nz(q*2.6-vec2(t*.02,0.))*.4;
float s=dot(q,normalize(vec2(1.,.6)))+c*.45;float pos=mod(t*.075,2.6)-.7;
float band=exp(-pow((s-pos)/.16,2.)),glow=exp(-pow((s-pos)/.55,2.));
vec3 base=mix(vec3(.035,.034,.036),vec3(.11,.10,.09),c*c);
vec3 gold=vec3(.96,.73,.36);
vec3 col=base+gold*(band*.20+glow*.07)+vec3(.15,.12,.08)*smoothstep(.55,0.,length(v-vec2(.5,.22)));
vec2 g=fc/(k*2.6);vec2 id=floor(g);vec2 f=fract(g)-.5;float a=h(id),b=h(id+17.3);
float fl=smoothstep(.36,0.,length(f-(vec2(a,b)-.5)*.5))*step(.5,a);
float tw=pow(max(0.,sin(t*(.8+b*1.8)+a*40.)),14.);
col+=gold*fl*(.05+tw*(.35+band*2.2))+vec3(1.)*fl*tw*band*.5;
col*=1.-.3*pow(length((v-.5)*vec2(1.,.9)),1.8);
gl_FragColor=vec4(col,1.);}"""

JS = """
(()=>{const R=document.documentElement,mo=R.classList.contains('mo');
const bg=()=>{const cv=document.querySelector('.bg canvas');const gl=cv.getContext('webgl',{alpha:false,antialias:false});
  if(!gl)return;const sh=(x,src)=>{const s=gl.createShader(x);gl.shaderSource(s,src);gl.compileShader(s);
    return gl.getShaderParameter(s,gl.COMPILE_STATUS)?s:null},vs=sh(gl.VERTEX_SHADER,`__VS__`),fs=sh(gl.FRAGMENT_SHADER,`__FS__`);
  if(!vs||!fs)return;const pr=gl.createProgram();gl.attachShader(pr,vs);gl.attachShader(pr,fs);gl.linkProgram(pr);
  if(!gl.getProgramParameter(pr,gl.LINK_STATUS))return;gl.useProgram(pr);gl.bindBuffer(gl.ARRAY_BUFFER,gl.createBuffer());
  gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW);
  const ap=gl.getAttribLocation(pr,'p');gl.enableVertexAttribArray(ap);gl.vertexAttribPointer(ap,2,gl.FLOAT,false,0,0);
  const u=n=>gl.getUniformLocation(pr,n),ur=u('r'),ut=u('t'),uk=u('k');
  const draw=t=>{const k=Math.min(devicePixelRatio||1,2),w=Math.round(cv.clientWidth*k),hh=Math.round(cv.clientHeight*k);
    if(cv.width!==w||cv.height!==hh){cv.width=w;cv.height=hh;gl.viewport(0,0,w,hh)}
    gl.uniform2f(ur,w,hh);gl.uniform1f(uk,k);gl.uniform1f(ut,t);gl.drawArrays(gl.TRIANGLE_STRIP,0,4)};
  window.__bgDraw=draw;draw(6);cv.classList.add('on');if(!mo)return;
  let raf=0;const loop=now=>{draw(window.__bgT??6+now/1000);raf=document.hidden?0:requestAnimationFrame(loop)};
  addEventListener('visibilitychange',()=>{if(!document.hidden&&!raf)raf=requestAnimationFrame(loop)});
  raf=requestAnimationFrame(loop)};
try{bg()}catch(x){}
if(document.hidden){const as=document.getAnimations();as.forEach(a=>a.pause());
  addEventListener('visibilitychange',()=>{if(!document.hidden)as.forEach(a=>a.play())},{once:true})}
const toast=document.querySelector('.toast');let tt=0;
const say=s=>{toast.textContent=s;toast.classList.add('on');clearTimeout(tt);tt=setTimeout(()=>toast.classList.remove('on'),2000)};
const copy=async s=>{try{await navigator.clipboard.writeText(s);return true}catch(x){const t=document.createElement('textarea');
  t.value=s;t.setAttribute('readonly','');t.style.cssText='position:fixed;opacity:0';document.body.appendChild(t);t.select();
  let ok=false;try{ok=document.execCommand('copy')}catch(y){}t.remove();return ok}};
const sheets=[...document.querySelectorAll('.sheet')];
const open=id=>{const S=document.getElementById(id);if(S.classList.contains('on'))return;S.classList.add('on');
  try{history.pushState({s:id},'')}catch(x){}};
const close=()=>{const S=sheets.find(x=>x.classList.contains('on'));if(S){S.classList.remove('on');
  try{if(history.state&&history.state.s)history.back()}catch(x){}}
  if(/^#(qr|odeme)$/.test(location.hash))location.hash=''};
addEventListener('popstate',()=>sheets.forEach(x=>x.classList.remove('on')));
document.querySelectorAll('a[href="#qr"]:not([data-copy-iban]),a[href="#odeme"]:not([data-copy-iban])').forEach(a=>
  a.addEventListener('click',ev=>{ev.preventDefault();open(a.getAttribute('href').slice(1))}));
document.querySelectorAll('.sheet a[href="#"]').forEach(a=>a.addEventListener('click',ev=>{ev.preventDefault();close()}));
addEventListener('keydown',ev=>{if(ev.key==='Escape')close()});
const U=document.getElementById('qr').dataset.url,IB=document.getElementById('odeme').dataset.iban;
document.querySelectorAll('[data-copy-iban]').forEach(b=>b.addEventListener('click',async ev=>{
  if(b.tagName==='A')ev.preventDefault();if(await copy(IB))say('IBAN kopyalandı');else if(b.tagName==='A')open('odeme')}));
const send=document.getElementById('send');if(!navigator.share)send.hidden=true;
send.onclick=async()=>{try{await navigator.share({title:document.title,url:U})}catch(x){}};
document.getElementById('copy').onclick=async()=>{if(await copy(U))say('Bağlantı kopyalandı')};})();
"""


def page(d):
    wa = f"https://wa.me/{d['tel_e164']}?text=" + d["whatsapp_mesaj"].replace(" ", "%20").replace(",", "%2C")
    deco = lambda k: f'<span class="ic" aria-hidden="true">{icon(k, True)}</span>'  # noqa: E731
    ext = ' target=_blank rel=noopener'
    rows = [
        ("tel", f'<a class="v" href="tel:+{d["tel_e164"]}"><small>Telefon</small><b>{e(d["tel_txt"])}</b></a>',
         f'<a class="ic wa" href="{e(wa)}"{ext} aria-label="WhatsApp ile yazın">{icon("whatsapp", True)}</a>'
         + deco("phone")),
        ("", f'<a class="v" href="https://instagram.com/{e(d["insta"])}"{ext}><small>Instagram</small>'
             f'<b>@{e(d["insta"])}</b></a>', deco("instagram")),
        ("", f'<a class="v" href="{e(d["web"])}"{ext}><small>Web sitesi</small><b>{e(d["web_txt"])}</b></a>',
         deco("globe")),
        ("", f'<a class="v" href="{e(d["harita"])}"{ext}><small>Konum · yol tarifi</small>'
             f'<b>{e(d["konum"].replace(", ", " / "))}</b></a>', deco("pin")),
        ("", f'<a class="v" href="{e(d["google"])}"{ext}><small>Google yorumları</small><b>{stars_svg()}Bizi '
             f'değerlendirin</b></a>', deco("star")),
        ("ib", f'<a class="v" href="#odeme" data-copy-iban aria-label="IBAN\'ı kopyala"><small>IBAN · dokunun, '
               f'kopyalansın</small><b>{e(d["iban_txt"])}</b></a>',
         f'<a class="ic" id="payqr" href="#odeme" aria-label="Ödeme karekodu">{icon("qr", True)}</a>'),
    ]
    li = "".join(f'<li class="{c}" style="--i:{k}">{main}<span class="acts">{acts}</span></li>'
                 for k, (c, main, acts) in enumerate(rows))
    url = d["qr"]
    holder = (f'<b>{e(d["iban_alici"])}</b>' if d.get("iban_alici") else "")
    body = (
        f'<div class="bg" aria-hidden="true"><canvas></canvas></div>'
        f'<div class="wrap"><header class="top">{t_svg("tlogo")}'
        f'<h1 aria-label="{e(d["isim"])}">{letters(d["isim"])}</h1>'
        f'<p class="svc">{e(AT.SERVICE)}</p><i class="rule"></i>'
        f'<p class="loc">{icon("pin")}{e(d["konum"].replace(", ", " · ").upper())}</p></header>'
        f'<main class="card"><ul class="rows">{li}</ul>'
        f'<div class="btns"><a class="save" href="{VCF}" download>{icon("save")}<b>REHBERE KAYDET</b></a>'
        f'<a class="share" id="share" href="#qr">{icon("qr")}<b>PAYLAŞ</b></a>'
        f'</div></main></div><div class="toast" role="status" aria-live="polite"></div>'
        # Paylaş
        f'<div class="sheet" id="qr" role="dialog" aria-modal="true" aria-labelledby="qrt" data-url="{e(url)}">'
        f'<a class="scrim" href="#" aria-label="Kapat"></a>'
        f'<div class="panel"><div class="ph"><p id="qrt">KARTVİZİTİ PAYLAŞ</p>'
        f'<a class="x" href="#" aria-label="Kapat">{icon("close", width=1.6)}</a></div>'
        f'<div class="qcard"><div class="tile">{qr_svg(url, "Kartvizit QR kodu")}<span class="vf" aria-hidden="true">'
        f'<i></i><i></i><i></i><i></i></span></div><p class="qcap"><span>DİJİTAL</span><i></i><span>KARTVİZİT</span>'
        f'</p></div><p class="hint">Kodu kamerayla okutun ya da bağlantıyı gönderin.'
        f'<b>{e(url.replace("https://", ""))}</b></p>'
        f'<div class="pbtns"><button class="share" id="copy" type="button">{icon("copy")}<b>KOPYALA</b></button>'
        f'<button class="save" id="send" type="button">{icon("share")}<b>GÖNDER</b></button></div></div></div>'
        # Ödeme
        f'<div class="sheet" id="odeme" role="dialog" aria-modal="true" aria-labelledby="odt" '
        f'data-iban="{e(d["iban_raw"])}"><a class="scrim" href="#" aria-label="Kapat"></a>'
        f'<div class="panel"><div class="ph"><p id="odt">ÖDEME BİLGİLERİ</p>'
        f'<a class="x" href="#" aria-label="Kapat">{icon("close", width=1.6)}</a></div>'
        f'<div class="qcard"><div class="tile">{qr_svg(d["pay_qr"], "IBAN karekodu")}<span class="vf" '
        f'aria-hidden="true"><i></i><i></i><i></i><i></i></span></div><p class="qcap"><span>IBAN</span><i></i>'
        f'<span>KAREKOD</span></p></div>'
        f'<p class="hint">Banka uygulamanızla okutun ya da IBAN\'ı kopyalayın.{holder}<b class="sel">{e(d["iban_txt"])}</b></p>'
        f'<div class="pbtns"><button class="save" type="button" data-copy-iban>{icon("copy")}<b>IBAN\'I KOPYALA</b>'
        f'</button></div></div></div>')
    title = f"{d['isim']} · {AT.SERVICE.title()} · {d['konum']}"
    desc = f"{d['isim']} – hasar onarım, {d['konum']}. Ara, WhatsApp, Instagram, konum, Google yorumları, IBAN."
    og = d["sayfa_url"].rstrip("/") + "/" + OG
    ext_, fmt = ("woff2", "woff2") if _has_brotli() else ("woff", "woff")
    css = CSS.replace("EXT", ext_).replace("FMT", fmt)
    js = JS.replace("__VS__", SEA_VS).replace("__FS__", SEA_FS)
    return (f'<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" '
            f'content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#0B0B0D">'
            f'<title>{e(title)}</title><meta name="description" content="{e(desc)}">'
            f'<meta property="og:type" content="website"><meta property="og:title" content="{e(title)}">'
            f'<meta property="og:description" content="{e(desc)}"><meta property="og:image" content="{e(og)}">'
            f'<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
            f'<meta name="twitter:card" content="summary_large_image">'
            f'<link rel="icon" href="{ICON_PNG}"><link rel="apple-touch-icon" href="{ICON_PNG}">'
            f'<link rel="preload" as="font" type="font/{fmt}" href="fonts/p6.{ext_}" crossorigin>'
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


def screenshot(d, path=PREVIEW):
    """Telefon ekranında (390 × 844, "hareketi azalt": son hâli): sayfa, Paylaş penceresi, Ödeme penceresi.
    Kontroller: yazı tipleri yüklü, yatay taşma yok, yazılar sığıyor, kart tek ekrana sığıyor, iki QR okunuyor."""
    from playwright.sync_api import sync_playwright
    errors, shots = [], []
    fits = "[...document.querySelectorAll('SEL')].every(e=>e.offsetParent===null||e.scrollWidth<=e.clientWidth+1)"
    with sync_playwright() as p, served() as url:
        b = p.chromium.launch(executable_path=CHROMIUM)
        for which in ("", "share", "payqr"):
            pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, reduced_motion="reduce")
            pg.add_init_script("navigator.share=async()=>{}")
            pg.on("pageerror", lambda x: errors.append(str(x)))
            pg.goto(url)
            pg.wait_for_timeout(600)
            pg.evaluate("Promise.all([400,500,600,700].map(w=>document.fonts.load(w+' 20px Poppins')))")  # 700: pencerede
            assert pg.evaluate("[400,500,600,700].every(w=>document.fonts.check(w+' 20px Poppins'))"), \
                "yazı tipi yüklenmedi"
            assert pg.evaluate("document.documentElement.scrollWidth") <= 390, "yatay taşma"
            assert pg.evaluate(fits.replace("SEL", ".v b,.v small,h1,.svc,.save,.share")), "yazı sığmadı"
            assert pg.evaluate("document.querySelector('.card').getBoundingClientRect().bottom") <= 845, \
                "kart tek ekrana sığmadı"
            assert pg.evaluate("document.querySelector('.bg canvas').classList.contains('on')"), "arka plan çizilmedi"
            if which:
                pg.click("#" + which)
                pg.wait_for_timeout(300)
                dlg = "#qr" if which == "share" else "#odeme"
                assert pg.evaluate(fits.replace("SEL", f"{dlg} .ph p,{dlg} .qcap,{dlg} .hint b,{dlg} .pbtns button")), \
                    "pencerede yazı sığmadı"
                tile = Image.open(io.BytesIO(pg.locator(f"{dlg} .tile").screenshot()))
                want = d["qr"] if which == "share" else d["pay_qr"]
                assert want in Q.decode(tile), f"{dlg} QR okunmadı"
            shots.append(Image.open(io.BytesIO(pg.screenshot())))
            pg.close()
        b.close()
    assert not errors, errors
    h = max(s.height for s in shots)
    canvas = Image.new("RGB", (sum(s.width for s in shots) + 160, h + 120), (52, 52, 56))
    x = 40
    for s in shots:
        canvas.paste(s, (x, 60))
        x += s.width + 40
    canvas.save(path)
    return path


def tour_gif(path=TOUR):
    """Tur (390 × 844), zamanda adım adım: açılış, canlı arka plan (pullar, ışık, T'nin parıltısı), Ödeme penceresi."""
    from playwright.sync_api import sync_playwright
    frames, durs, errors = [], [], []
    with sync_playwright() as p, served() as url:
        b = p.chromium.launch(executable_path=CHROMIUM)
        pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
        pg.on("pageerror", lambda x: errors.append(str(x)))
        pg.add_init_script("navigator.share=async()=>{}")

        def shot(ms):
            frames.append(Image.open(io.BytesIO(pg.screenshot())).convert("RGB"))
            durs.append(ms)

        def at(ms):
            _seek(pg, ms)
            pg.evaluate(f"window.__bgT={6 + ms / 1000};window.__bgDraw&&__bgDraw(__bgT)")

        pg.goto(url)
        pg.wait_for_function("document.querySelector('.bg canvas').classList.contains('on')", timeout=15000)
        for k in range(0, 3000, 100):
            at(k)
            shot(100)
        for k in range(3000, 9600, 240):
            at(k)
            shot(240)
        pg.evaluate("document.getElementById('payqr').click();window._dl=document.getAnimations().filter(a=>{"
                    "const t=a.effect&&a.effect.target;return t&&t.closest&&t.closest('#odeme')});"
                    "_dl.forEach(a=>{a.pause();a.currentTime=0})")
        for k in range(0, 1700, 100):
            pg.evaluate(f"_dl.forEach(a=>a.currentTime={k});window.__bgT={15.6 + k / 1000};__bgDraw(__bgT)")
            shot(100)
        pg.evaluate("_dl.forEach(a=>{try{a.finish()}catch(e){a.play()}})")
        shot(2600)
        b.close()
    assert not errors, errors
    # pullar titreşimli renk dağıtmayla (dither) GIF'te sıkışmaz: ortak palet, dağıtmasız, biraz küçük
    frames = [f.resize((312, 675), Image.LANCZOS) for f in frames]
    pal = frames[len(frames) // 2].quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    out = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    out[0].save(path, save_all=True, append_images=out[1:], duration=durs, loop=0, optimize=True)
    return path


def standalone(doc, path=STANDALONE):
    """Denemelik tek dosya: yazı tipleri, simge ve rehber kartı (vCard) sayfanın içine gömülü."""
    import base64

    def data(rel, mime):
        with open(os.path.join(OUT, rel), "rb") as f:
            return f"data:{mime};base64," + base64.b64encode(f.read()).decode()

    doc = re.sub(r'<link rel="preload"[^>]*>', "", doc)
    for rel in sorted(set(re.findall(r"fonts/p\d\.woff2?", doc))):
        doc = doc.replace(f"url({rel})", f"url({data(rel, 'font/' + rel.rsplit('.', 1)[1])})")
    doc = doc.replace(f'href="{ICON_PNG}"', f'href="{data(ICON_PNG, "image/png")}"')
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
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    doc = page(d)
    subset_fonts(html.unescape(doc))
    vcard(d)
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
