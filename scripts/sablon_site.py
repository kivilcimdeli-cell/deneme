"""İşletme sitesi şablonları: isimlikteki QR ile açılan dijital kartvizit sayfaları, lastikçi tarzında.

Kural (kullanıcının isteği): aksi söylenmedikçe her yeni işletmenin sitesi bu beş şablondan biriyle yapılır ve
şablonlar sırayla döndürülür (1 → 2 → … → 5 → 1). Sıra `site_sablonlari/sira.json`da tutulur: bir işletme bir kez
şablon aldıysa yeniden üretimde aynı şablonda kalır.

  1 Şimşek      Uzar Oto Lastik'in sitesi: dar kalın yazı, eğik şeritler, ok dişli şerit, büyük liste düğmeleri,
                açık renk ödeme kartı
  2 Lastik izi  İnce Oto Lastik'in sitesi: eğik dar yazı, lastik izi bandı, Hemen Ara'da diş baskısı, kutucuklar,
                koyu banka kartı, sağ altta ara düğmesi
  3 İkaz        Çalık Oto Lastik'in sitesi: ikaz şeridi, harf harf yükselen ad ve renkli nokta, 2 sütun kutucuk,
                altta arama şeridi
  4 Kurumsal    Soylu Oto Lastik'in sitesi: sağ üstte eğik renkli şerit, ızgara, numaralı liste (01–04), üst
                çizgili ödeme kartı, altta arama şeridi
  5 Sade        yeni, aynı aileden ve süssüz: solda büyük ad, kısa renkli çizgi, bağlantılar tek kartta liste

Hepsinde aynı işler: Hemen Ara, WhatsApp (hazır mesajlı), Instagram, Google yorumları, konum ve web sitesi (varsa),
Rehbere kaydet (vCard), ödeme bilgileri (banka, alıcı, IBAN + tek dokunuşla kopyala, banka karekodu: kaydedilip
banka uygulamasında galeriden okutulur). Dış bağlantı yok: yazı tipleri ve simgeler sayfanın içinde. Bağlantılar
aynı sekmede açılır; karekod kutusu JavaScript'siz de açılır (#kk, CSS :target). "Hareketi azalt" açıksa
animasyon oynamaz.

Bilgiler işletme klasöründeki `bilgiler.json`dan okunur:
  isletme (ya da isim), telefon, whatsapp, whatsapp_mesaj, instagram, google, harita, web, iban, iban_alici, banka,
  iban_karekod, sayfa_url; isteğe bağlı: marka (büyük yazılan ad), hizmet (OTO LASTİK, HASAR ONARIM …), etiket
  (üstteki küçük yazı), aciklama, sehir, konum, renk (vurgu rengi), isaret (logo işareti SVG'si, klasöre göre),
  karekod_hata (bankanın karekodundaki hata düzeltme: m/q/h), iban_ornek (gerçek IBAN gelene kadar), sablon.
  Dijital kartvizit (10 × 20 kurumsal isimlik): isletme yerine kişinin adı, hizmet görevi, kurum (vCard ORG),
  eposta (E-posta bağlantısı); iban verilmezse ödeme bölümü çıkmaz.

Çıktı (işletme klasöründe): site/, <ad>_site.zip (Cloudflare'e yüklenir), sayfa_onizleme.png, sayfa_tur.gif,
        sayfa_deneme.html (denemelik tek dosya)
Katalog: site_sablonlari/ (her şablon kendi örnek işletmesiyle; katalog.png)

Kullanım:
  python3 scripts/sablon_site.py autotufan_isimlik            # sıradaki ya da kayıtlı şablonla
  python3 scripts/sablon_site.py autotufan_isimlik --sablon 3 # şablonu elle seç (kayıt güncellenir)
  python3 scripts/sablon_site.py autotufan_isimlik --hizli    # GIF'siz
  python3 scripts/sablon_site.py --katalog                    # beş şablonun örnekleri ve katalog görseli
  python3 scripts/sablon_site.py --sira                       # kayıtlı işletmeler ve sıradaki şablon
"""
import base64
import contextlib
import datetime
import io
import json
import os
import re
import shutil
import sys
import zipfile
from dataclasses import dataclass, field

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anahtarlik as A  # noqa: E402
import qr_sistemi as Q  # noqa: E402
import sablonlar  # noqa: E402
from sablonlar.ortak import CHARS, e, tr_title, tr_upper  # noqa: E402

CATALOG = os.path.join(A.ROOT, "site_sablonlari")
ORDER = os.path.join(CATALOG, "sira.json")
CHROMIUM = "/opt/pw-browsers/chromium"                    # bulut ortamı; yoksa (Windows) Playwright'ın kendi
CHROMIUM = CHROMIUM if os.path.exists(CHROMIUM) else None  # tarayıcısı (playwright install chromium)
# ---------------------------------------------------------------- bilgiler

@dataclass
class Link:
    key: str          # whatsapp, instagram, google, konum, web, rehber
    href: str
    icon: str         # ICON anahtarı
    title: str        # uzun başlık (liste)
    sub: str          # alt satır
    short: str        # kısa ad (kutucuk, konsol tuşu)
    download: str = ""


@dataclass
class Site:
    folder: str
    slug: str
    isletme: str      # Soylu Oto Lastik
    marka: str        # SOYLU (büyük yazılan ad)
    hizmet: str       # OTO LASTİK
    etiket: str       # üstteki küçük yazı
    aciklama: str
    sehir: str
    konum: str
    renk: str
    tel: str          # 905414873003
    wa: str           # hazır mesajlı WhatsApp bağlantısı
    instagram: str    # kullanıcı adı ya da ""
    google: str
    harita: str
    web: str
    iban: str         # boşluksuz
    iban_ornek: bool
    alici: str
    banka: str
    karekod: str      # karekodun içeriği ("" ise karekod düğmesi yok)
    karekod_hata: str
    sayfa: str
    isaret: str       # logo işareti: <svg> içeriği ve viewBox ("" ise yok)
    isaret_box: str
    isaret_cizgi: list = field(default_factory=list)   # fırça darbeleri [(kalınlık, [(x, y) …])]: logo yazılır gibi
    sablon: int = 0
    extra: dict = field(default_factory=dict)
    eposta: str = ""  # dijital kartvizit (10 × 20 kurumsal isimlik): e-posta bağlantısı
    kurum: str = ""   # kartvizit: kişinin çalıştığı kurum (vCard ORG); doluysa sayfa kişinin kartvizitidir

    @property
    def phone(self):
        return Q.phone_display(self.tel)

    @property
    def iban_txt(self):
        return Q.iban_display(self.iban)

    @property
    def vcf(self):
        return self.slug + ".vcf"

    @property
    def lines(self):
        """Büyük adın satırları: iki kelimeli uzun adlar alt alta."""
        w = self.marka.split()
        return w if len(w) > 1 and len(self.marka) > 7 else [self.marka]

    @property
    def web_txt(self):
        return re.sub(r"^https?://(www\.)?", "", self.web).rstrip("/")

    def links(self, rehber=True, vcf_href=None):
        L = [Link("whatsapp", self.wa, "whatsapp", "WhatsApp", "Mesaj gönderin", "WhatsApp")]
        if self.eposta:
            L.append(Link("eposta", f"mailto:{self.eposta}", "mail", "E-posta", self.eposta, "E-posta"))
        if self.instagram:
            L.append(Link("instagram", f"https://www.instagram.com/{self.instagram}/", "instagram", "Instagram",
                          "@" + self.instagram, "Instagram"))
        if self.google:
            L.append(Link("google", self.google, "star", "Google", "Yorumları görün, yorum yapın", "Yorumlar"))
        if self.harita:
            L.append(Link("konum", self.harita, "pin", "Konum", f"{self.konum or tr_title(self.sehir)} · Yol tarifi",
                          "Konum"))
        if self.web:
            L.append(Link("web", self.web, "globe", "Web sitesi", self.web_txt, "Web sitesi"))
        if rehber:
            L.append(Link("rehber", vcf_href or self.vcf, "person", "Rehbere kaydet",
                          "Kartviziti ekleyin" if self.kurum else "Numarayı ekleyin", "Rehbere ekle",
                          f"{self.isletme}.vcf"))
        return L


def _accent(hexc):
    """Vurgu rengi: rgb, koyu tonu, üstündeki yazı rengi (açık renkte koyu yazı)."""
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    dark = "#{:02x}{:02x}{:02x}".format(*(int(c * .74) for c in (r, g, b)))
    deep = "#{:02x}{:02x}{:02x}".format(*(int(c * (.58 if lum > .55 else .9)) for c in (r, g, b)))
    ink = "#ffffff" if lum < .55 else "#{:02x}{:02x}{:02x}".format(*(int(c * .1) for c in (r, g, b)))
    ink2 = "rgba(255,255,255,.85)" if lum < .55 else "rgba(0,0,0,.62)"
    return (f":root{{--ac:{hexc};--ac-rgb:{r},{g},{b};--ac2:{dark};--ac-ink:{ink};--ac-ink2:{ink2};"
            f"--ac-deep:{deep};--ac-soft:rgba({r},{g},{b},.16);--sc:0px}}\n")


def load(folder, overrides=None):
    folder = folder if os.path.isabs(folder) else os.path.join(A.ROOT, folder)
    d = json.load(open(os.path.join(folder, "bilgiler.json"), encoding="utf-8"))
    d.update(overrides or {})
    name = tr_upper(d.get("isletme") or d.get("isim"))
    hizmet = tr_upper(d.get("hizmet") or ("OTO LASTİK" if name.endswith("OTO LASTİK") else ""))
    marka = tr_upper(d.get("marka") or (name[:-len(hizmet)].strip() if hizmet and name.endswith(hizmet) else name))
    konum = d.get("konum", "")
    sehir = tr_upper(d.get("sehir") or (konum.split(",")[-1].strip() if konum else ""))
    tel = Q.phone_e164(d["telefon"])
    wa_no = Q.phone_e164(d.get("whatsapp") or d["telefon"])
    import urllib.parse
    msg = d.get("whatsapp_mesaj", "")
    raw = re.sub(r"\s", "", d.get("iban", "")).upper()   # kartvizitte IBAN yok: ödeme bölümü çıkmaz
    ornek = bool(d.get("iban_ornek"))
    iban = raw if ornek or not raw else Q.iban_normalize(raw)
    karekod = d.get("iban_karekod", "").strip()
    if karekod:
        k = Q.karekod_check(karekod, None if ornek else iban)
        if not d.get("iban_alici") and k["alici"]:
            d["iban_alici"] = k["alici"]
    elif ornek and iban:
        karekod = iban                                   # örnek: karekod yalnız IBAN'ı taşır
    isaret, box = "", ""
    if d.get("isaret"):
        src = open(os.path.join(folder, d["isaret"]), encoding="utf-8").read()
        box = re.search(r'viewBox="([^"]+)"', src).group(1)
        isaret = "".join(re.findall(r"<path[^>]*/>", src))
        isaret = re.sub(r'\s(fill|class)="[^"]*"', "", isaret)
    cizgi = []
    if d.get("isaret_cizgi"):
        c = json.load(open(os.path.join(folder, d["isaret_cizgi"]), encoding="utf-8"))
        cizgi = [(k["genislik"], [tuple(p) for p in k["noktalar"]]) for k in c["darbeler"]]
    slug = re.sub(r"[^a-z0-9]+", "", tr_upper(marka).translate(str.maketrans("ÇĞİÖŞÜ", "CGIOSU")).lower()) or "site"
    return Site(folder=folder, slug=slug, isletme=tr_title(name), marka=marka, hizmet=hizmet,
                etiket=tr_upper(d.get("etiket") or (konum.replace(", ", " · ") if konum else sehir)),
                aciklama=d.get("aciklama") or "Bize tek dokunuşla ulaşın.", sehir=sehir, konum=konum,
                renk=d.get("renk", ""), tel=tel,
                wa=f"https://wa.me/{wa_no}" + ("?text=" + urllib.parse.quote(msg) if msg else ""),
                instagram=Q.instagram_handle(d["instagram"]) if d.get("instagram") else "",
                google=Q.google_url(d["google"]) if d.get("google") else "", harita=d.get("harita", ""),
                web=d.get("web", ""), iban=iban, iban_ornek=ornek, alici=tr_upper(d.get("iban_alici", "")),
                banka=d.get("banka", ""), karekod=karekod, karekod_hata=d.get("karekod_hata", "m"),
                sayfa=Q.https_url(d["sayfa_url"]) if d.get("sayfa_url") else "", isaret=isaret, isaret_box=box,
                isaret_cizgi=cizgi, sablon=int(d.get("sablon", 0)),
                extra={k: v for k, v in d.items() if k.startswith("sablon_")},
                eposta=d.get("eposta", ""), kurum=d.get("kurum", ""))


# ---------------------------------------------------------------- sıra

def order():
    return json.load(open(ORDER, encoding="utf-8")) if os.path.exists(ORDER) else []


def pick(site, forced=0):
    """Şablon: elle seçilen > bilgiler.json'daki > kayıtlı > sıradaki. Yeni ya da değişen seçim kaydedilir."""
    rows = order()
    rel = os.path.relpath(site.folder, A.ROOT)
    known = next((r for r in rows if r["klasor"] == rel), None)
    n = forced or site.sablon or (known and known["sablon"]) or (rows[-1]["sablon"] % len(sablonlar.ALL) + 1 if rows
                                                                  else 1)
    if not known or known["sablon"] != n:
        rows = [r for r in rows if r["klasor"] != rel] + [{"isletme": site.isletme, "klasor": rel, "sablon": n,
                                                            "tarih": datetime.date.today().isoformat()}]
        os.makedirs(CATALOG, exist_ok=True)
        with open(ORDER, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
            f.write("\n")
    return n


# ---------------------------------------------------------------- sayfa

COMMON_CSS = """
/* açılır kutular (karekod): JavaScript .on ile açar; JavaScript yoksa bağlantı (#kk) :target ile */
.drop{display:none}.drop:target,.drop.on{display:block}
"""

COMMON_JS = """
(()=>{const R=document.documentElement,still=matchMedia('(prefers-reduced-motion: reduce)').matches;
if(document.hidden){const as=document.getAnimations();as.forEach(a=>a.pause());
  addEventListener('visibilitychange',()=>{if(!document.hidden)as.forEach(a=>a.play())},{once:true})}
const toast=document.querySelector('.toast');let tt;
const say=m=>{toast.textContent=m;toast.classList.add('show');clearTimeout(tt);tt=setTimeout(()=>toast.classList.remove('show'),2200)};
const copy=async t=>{try{await navigator.clipboard.writeText(t);return true}catch(x){}
  const a=document.createElement('textarea');a.value=t;a.setAttribute('readonly','');a.style.cssText='position:fixed;opacity:0';
  document.body.appendChild(a);a.select();a.setSelectionRange(0,99);let ok=false;try{ok=document.execCommand('copy')}catch(x){}
  a.remove();return ok};
document.querySelectorAll('[data-copy]').forEach(b=>b.addEventListener('click',async ev=>{ev.preventDefault();
  const ok=await copy(b.dataset.copy),l=b.querySelector('span'),o=l&&l.textContent;
  if(ok){b.classList.add('ok');if(l)l.textContent=b.dataset.done;say('IBAN kopyalandı – banka uygulamanıza yapıştırın');
    const f=document.querySelector('.iban');if(f){f.classList.remove('flash');void f.offsetWidth;f.classList.add('flash')}}
  else say('Kopyalanamadı: IBAN yazısına basılı tutun');
  setTimeout(()=>{b.classList.remove('ok');if(l)l.textContent=o},2000)}));
document.querySelectorAll('[data-toggle]').forEach(a=>a.addEventListener('click',ev=>{ev.preventDefault();
  const el=document.getElementById(a.dataset.toggle),on=el.classList.toggle('on');a.setAttribute('aria-expanded',on);
  if(on)el.scrollIntoView({behavior:still?'auto':'smooth',block:'nearest'})}));
if(!still){let q=0;addEventListener('scroll',()=>{if(!q)q=requestAnimationFrame(()=>{
  R.style.setProperty('--sc',Math.min(scrollY,2000).toFixed(0)+'px');q=0})},{passive:true})}
if('IntersectionObserver' in window){
  const seen=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting){x.target.classList.add('in');
    seen.unobserve(x.target)}}),{threshold:.35});
  document.querySelectorAll('[data-in]').forEach(el=>seen.observe(el));
  const call=document.querySelector('.call'),bar=document.querySelector('.callbar,.fab');
  if(call&&bar)new IntersectionObserver(([x])=>bar.classList.toggle('show',!x.isIntersecting&&
    x.boundingClientRect.top<0)).observe(call)}
else document.querySelectorAll('[data-in]').forEach(el=>el.classList.add('in'))})();
"""


@dataclass
class Ctx:
    """Sayfanın dosyalara giden adresleri: sitede dosya adı, deneme dosyasında gömülü (data:)."""
    kk: str
    vcf: str
    standalone: bool = False


def font_faces(T, out, standalone):
    css = ""
    for key, (fn, fam, wt, st) in T.FONTS.items():
        url = f"fonts/{key}.woff"
        if standalone:
            url = "data:font/woff;base64," + base64.b64encode(open(os.path.join(out, url), "rb").read()).decode()
        css += (f'@font-face{{font-family:"{fam}";font-weight:{wt};font-style:{st};font-display:swap;'
                f'src:url({url}) format("woff")}}\n')
    return css


def page(site, T, out, standalone=False):
    def data(fn, mime):
        return f"data:{mime};base64," + base64.b64encode(open(os.path.join(out, fn), "rb").read()).decode()

    ctx = Ctx(kk=(data("karekod.png", "image/png") if standalone else "karekod.png") if site.karekod else "",
              vcf=data(site.vcf, "text/vcard") if standalone else site.vcf, standalone=standalone)
    css = font_faces(T, out, standalone) + _accent(site.renk or T.RENK) + T.css(site) + COMMON_CSS
    title = f"{site.isletme} – {tr_title(site.hizmet)}" if site.hizmet else site.isletme
    if site.sehir:
        title += f" · {tr_title(site.sehir)}"
    desc = (f"{site.isletme}{', ' + tr_title(site.sehir) if site.sehir else ''}: hemen arayın, WhatsApp'tan yazın"
            + (", Instagram" if site.instagram else "") + (", Google yorumları" if site.google else "")
            + ", ödeme bilgileri.")
    og = (f'<meta property="og:url" content="{e(site.sayfa)}">\n<meta property="og:image" content="'
          f'{e(site.sayfa)}og.png">\n<meta property="og:image:width" content="1200">\n'
          f'<meta property="og:image:height" content="630">\n<meta name="twitter:card" content="summary_large_image">'
          if site.sayfa else "")
    fav = "data:image/svg+xml," + T.favicon(site).replace("#", "%23").replace('"', "'")
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="{T.BG}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
{og}
<link rel="icon" href="{fav}">
<style>{css}</style>
</head>
<body>
{T.body(site, ctx)}
<div class="toast" role="status" aria-live="polite"></div>
<script>{COMMON_JS}{T.JS}</script>
</body>
</html>
"""


# ---------------------------------------------------------------- dosyalar

def subset_fonts(T, out):
    from fontTools import subset
    fdir = os.path.join(out, "fonts")
    shutil.rmtree(fdir, ignore_errors=True)
    os.makedirs(fdir)
    for key, (fn, *_) in T.FONTS.items():
        opts = subset.Options()
        opts.flavor = "woff"
        opts.layout_features = ["kern", "liga", "locl", "tnum"]
        f = subset.load_font(os.path.join(A.FONT_DIR, fn), opts)
        s = subset.Subsetter(opts)
        s.populate(text=CHARS)
        s.subset(f)
        subset.save_font(f, os.path.join(fdir, key + ".woff"), opts)
    for lic in T.LICENSES:
        shutil.copy(os.path.join(A.FONT_DIR, lic), os.path.join(fdir, lic))


def karekod_png(site, out):
    """Banka karekodu: bankanınkiyle aynı baytlar (ECI yok) ve aynı hata düzeltme; okunarak denetlenir."""
    import segno
    import zxingcpp
    path = os.path.join(out, "karekod.png")
    if not site.karekod:
        return None
    segno.make(site.karekod, error=site.karekod_hata, mode="byte", encoding="utf-8", eci=False, micro=False,
               boost_error=False).save(path, scale=12, border=4)
    r = zxingcpp.read_barcodes(Image.open(path).convert("L"))
    assert len(r) == 1 and r[0].text == site.karekod, "karekod okunmadı"
    return path


def vcard(site, out):
    if site.kurum:                                       # kişinin kartviziti: soyadı, adı; kurum ayrı
        first, _, last = site.isletme.rpartition(" ")
        name = [f"N:{last};{first};;;", f"FN:{site.isletme}", f"ORG:{site.kurum}"]
    else:
        name = [f"N:;{site.isletme};;;", f"FN:{site.isletme}", f"ORG:{site.isletme}"]
    lines = ["BEGIN:VCARD", "VERSION:3.0", *name, f"TEL;TYPE=CELL,VOICE:+{site.tel}"]
    if site.eposta:
        lines.append(f"EMAIL;TYPE=WORK:{site.eposta}")
    if site.hizmet:
        lines.append(f"TITLE:{tr_title(site.hizmet)}")
    if site.sehir:
        lines.append(f"ADR;TYPE=WORK:;;;{(site.konum.split(',')[0].strip() if site.konum else '')};"
                     f"{tr_title(site.sehir)};;Türkiye")
    lines += [f"URL:{u}" for u in (site.web, site.sayfa) if u]
    if site.instagram:
        lines.append(f"X-SOCIALPROFILE;TYPE=instagram:https://www.instagram.com/{site.instagram}/")
    if site.iban and not site.iban_ornek:
        who = ", ".join(x for x in (tr_title(site.alici), site.banka) if x).replace(",", "\\,")
        lines.append(f"NOTE:IBAN {site.iban_txt}" + (f" ({who})" if who else ""))
    lines.append("END:VCARD")
    with open(os.path.join(out, site.vcf), "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(lines) + "\n")


def og_image(site, T, out):
    """Bağlantı paylaşılınca görünen kapak (1200 × 630): başlığın aynısı, büyük."""
    from playwright.sync_api import sync_playwright
    css = font_faces(T, out, True) + _accent(site.renk or T.RENK) + T.css(site) + T.OG_CSS
    doc = f'<!doctype html><meta charset="utf-8"><style>{css}</style><body class="og">{T.og(site)}</body>'
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        pg = b.new_page(viewport={"width": 1200, "height": 630}, reduced_motion="reduce")
        pg.set_content(doc)
        pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(out, "og.png"))
        b.close()


def pack(out, path):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for d, _, files in os.walk(out):
            for fn in sorted(files):
                full = os.path.join(d, fn)
                z.write(full, os.path.relpath(full, out))


# ---------------------------------------------------------------- önizlemeler

@contextlib.contextmanager
def served(out):
    """site/ yerel sunucuda (telefondaki gibi http)."""
    import functools
    import http.server
    import threading

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=out))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{srv.server_port}/index.html"
    finally:
        srv.shutdown()


def check_page(pg, site, T):
    """Yazı tipleri yüklü, yatay taşma yok, yazılar sığıyor, büyük ad başlığa sığıyor."""
    fams = {f'{st} {wt} 20px "{fam}"' for _, fam, wt, st in T.FONTS.values()}
    pg.evaluate(f"Promise.all({json.dumps(sorted(fams))}.map(f=>document.fonts.load(f)))")
    for f in fams:
        assert pg.evaluate(f"document.fonts.check({json.dumps(f)})"), f"yazı tipi yüklenmedi: {f}"
    w = pg.evaluate("innerWidth")
    assert pg.evaluate("document.documentElement.scrollWidth") <= w, "yatay taşma"
    bad = pg.evaluate(f"[...document.querySelectorAll({json.dumps(T.FITS)})].filter(x=>x.offsetParent!==null&&"
                      "x.scrollWidth>x.clientWidth+1).map(x=>x.className+': '+x.textContent.trim().slice(0,30))")
    assert not bad, f"yazı sığmadı: {bad}"
    right = pg.evaluate(f"Math.max(...[...document.querySelectorAll({json.dumps(T.MARK)})].map(x=>"
                        "x.getBoundingClientRect().right))")
    assert right <= w - 8, f"büyük ad taştı ({right:.0f} > {w - 8})"
    if pg.locator("svg.drawn g[mask]").count():                    # fırça darbeleri logonun tamamını örtüyor mu
        import numpy as np
        el = pg.locator("svg.drawn").first
        a = np.asarray(Image.open(io.BytesIO(el.screenshot())).convert("L"), float)
        pg.evaluate("document.querySelectorAll('svg.drawn g[mask]').forEach(g=>{g.dataset.m=g.getAttribute('mask');"
                    "g.removeAttribute('mask')})")
        b = np.asarray(Image.open(io.BytesIO(el.screenshot())).convert("L"), float)
        pg.evaluate("document.querySelectorAll('svg.drawn g[data-m]').forEach(g=>g.setAttribute('mask',g.dataset.m))")
        miss = (np.abs(a - b) > 40).mean()
        assert miss < 0.002, f"logo çizimi eksik kalıyor (%{100 * miss:.2f})"


def screenshot(site, T, out, path):
    """Telefon ekranında (390 × 844, son hâli): üst görünüm ve tüm sayfa (karekod açık) yan yana."""
    from playwright.sync_api import sync_playwright
    errors, shots = [], []
    with sync_playwright() as p, served(out) as url:
        b = p.chromium.launch(executable_path=CHROMIUM)
        for full in (False, True):
            pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, reduced_motion="reduce")
            pg.on("pageerror", lambda x: errors.append(str(x)))
            pg.goto(url)
            pg.wait_for_timeout(500)
            check_page(pg, site, T)
            if full:
                pg.add_style_tag(content=".callbar,.fab{display:none!important}")
                if site.karekod:
                    pg.click("[data-toggle=kk]")
                    pg.wait_for_timeout(300)
                    im = Image.open(io.BytesIO(pg.locator("#kk img").screenshot()))
                    assert site.karekod in Q.decode(im), "sayfadaki karekod okunmadı"
            shots.append(Image.open(io.BytesIO(pg.screenshot(full_page=full))))
            pg.close()
        b.close()
    assert not errors, errors
    h = max(s.height for s in shots)
    canvas = Image.new("RGB", (sum(s.width for s in shots) + 120, h + 120), (52, 52, 58))
    x = 40
    for s in shots:
        canvas.paste(s, (x, 60))
        x += s.width + 40
    canvas.save(path)
    return shots[0]


def _seek(pg, ms):
    pg.evaluate(f"document.getAnimations().forEach(a=>{{a.pause();a.currentTime={ms:.0f}}})")


def _finish(pg):
    pg.evaluate("document.getAnimations().forEach(a=>{try{a.finish()}catch(x){a.play()}})")


def tour_gif(site, T, out, path):
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

    with sync_playwright() as p, served(out) as url:
        b = p.chromium.launch(executable_path=CHROMIUM)
        ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=1,
                            permissions=["clipboard-read", "clipboard-write"])
        pg = ctx.new_page()
        pg.goto(url)
        _seek(pg, 0)
        pg.wait_for_timeout(300)
        for k in range(0, T.INTRO_MS, 70):
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
        for _ in range(8):
            pg.wait_for_timeout(110)
            shot(pg, 110)
        pg.locator(".copy").scroll_into_view_if_needed()
        tap = tap_on(pg, ".copy")
        shot(pg, 300, tap)
        pg.mouse.click(*tap)
        for _ in range(5):
            pg.wait_for_timeout(120)
            shot(pg, 160)
        durs[-1] = 1000
        if site.karekod:
            pg.wait_for_timeout(2300)
            tap = tap_on(pg, "[data-toggle=kk]")
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
    frames = [f.resize((312, 675), Image.LANCZOS) for f in frames]
    pal = frames[len(frames) // 3].quantize(colors=160, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=True)
    return path


# ---------------------------------------------------------------- üretim

def build(folder, n=0, out=None, previews=True, gif=True, overrides=None, record=True):
    """İşletmenin sitesi: site/, zip, deneme dosyası; önizleme ve tur. Döner: (site, şablon, ilk ekran görüntüsü)."""
    site = load(folder, overrides)
    n = pick(site, n) if record else (n or site.sablon or 1)
    T = sablonlar.get(n)
    base = out or site.folder
    out = os.path.join(base, "site")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    subset_fonts(T, out)
    karekod_png(site, out)
    vcard(site, out)
    og_image(site, T, out)
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(page(site, T, out))
    with open(os.path.join(base, "sayfa_deneme.html"), "w", encoding="utf-8") as f:
        f.write(page(site, T, out, standalone=True))
    pack(out, os.path.join(base, f"{site.slug}_site.zip"))
    size = sum(os.path.getsize(os.path.join(d, fn)) for d, _, fs in os.walk(out) for fn in fs)
    print(f"{site.isletme}: şablon {n} · {T.AD}  site/ {size // 1024} KB → {site.sayfa or '(adres yayından sonra)'}")
    first = None
    if previews:
        first = screenshot(site, T, out, os.path.join(base, "sayfa_onizleme.png"))
        print("  önizleme:", os.path.relpath(os.path.join(base, "sayfa_onizleme.png"), A.ROOT))
        if gif:
            print("  tur:", os.path.relpath(tour_gif(site, T, out, os.path.join(base, "sayfa_tur.gif")), A.ROOT))
    return site, T, first


def catalog():
    """Beş şablonun her biri kendi örnek işletmesiyle (1–4 lastikçilerin kendileri, 5 Auto Tufan),
    site_sablonlari/<no>_<ad>/ altında önizleme ve deneme dosyası; katalog.png: ilk ekranları yan yana."""
    tiles = []
    for T in sablonlar.ALL:
        folder, over = T.ORNEK
        base = os.path.join(CATALOG, f"{T.NO}_{T.SLUG}")
        os.makedirs(base, exist_ok=True)
        site, _, first = build(folder, T.NO, out=base, gif=False, overrides=over, record=False)
        shutil.rmtree(os.path.join(base, "site"))                    # katalogda önizleme ve deneme dosyası kalır
        os.remove(os.path.join(base, f"{site.slug}_site.zip"))
        tiles.append((T, site, first))
    W = 390
    font = lambda n, b=True: ImageFont.truetype(os.path.join(A.FONT_DIR, "Poppins-SemiBold.ttf" if b  # noqa: E731
                                                             else "Poppins-Regular.ttf"), n)
    gap, top = 40, 150
    sheet = Image.new("RGB", (len(tiles) * (W + gap) + gap, top + 844 + 60), (236, 238, 242))
    dr = ImageDraw.Draw(sheet)
    dr.text((gap, 34), "SİTE ŞABLONLARI · lastikçi tarzı · sırayla", font=font(34), fill=(20, 20, 24))
    for k, (T, site, first) in enumerate(tiles):
        x = gap + k * (W + gap)
        dr.text((x, 96), f"{T.NO} · {T.AD}", font=font(24), fill=(20, 20, 24))
        dr.text((x, 126), f"örnek: {site.isletme}", font=font(17, False), fill=(96, 98, 106))
        shot = first.resize((W, 844), Image.LANCZOS)
        sheet.paste(shot, (x, top + 20))
    sheet.save(os.path.join(CATALOG, "katalog.png"), optimize=True)
    print("katalog:", os.path.relpath(os.path.join(CATALOG, "katalog.png"), A.ROOT))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--katalog" in sys.argv:
        catalog()
        return
    if "--sira" in sys.argv or not args:
        rows = order()
        for r in rows:
            print(f"  {r['sablon']} · {sablonlar.get(r['sablon']).AD:11s} {r['isletme']} ({r['klasor']}, {r['tarih']})")
        nxt = rows[-1]["sablon"] % len(sablonlar.ALL) + 1 if rows else 1
        print(f"sıradaki şablon: {nxt} · {sablonlar.get(nxt).AD}")
        return
    n = int(sys.argv[sys.argv.index("--sablon") + 1]) if "--sablon" in sys.argv else 0
    if n:
        args = [a for a in args if a != str(n)]
    build(args[0], n, gif="--hizli" not in sys.argv)


if __name__ == "__main__":
    main()
