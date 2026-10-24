"""Restoran masalıkları için 10 örnek menü sitesi (telefon görünümü) – katalogda gösterilir.

Masalıktaki QR / NFC bu sayfayı açar: üstte işletme ve masa numarası, altında düğmeler (menü, Google yorumu, Wi-Fi,
Instagram, rezervasyon, garson çağır, hesap). Menü sayfasında kategoriler, açıklamalı ürünler ve fiyatlar. Her site
masalığıyla aynı renk ve yazı tipinde. İsimler, ürünler ve fiyatlar örnek.

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
@font-face{font-family:Manrope;src:url(../fonts/Manrope-SemiBold.ttf);font-weight:600}
"""

BASE = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:var(--bg)}
body{font-family:Jost,'Noto Sans',sans-serif;color:var(--fg);-webkit-font-smoothing:antialiased;font-size:16px}
a{color:inherit;text-decoration:none}
.hero{background:var(--hero);color:var(--hero-fg);padding:60px 26px 34px;position:relative;overflow:hidden;
  text-align:center}
.hero svg.motif{position:absolute;left:0;top:0;width:100%;height:100%}
.hero>*{position:relative}
.mark{width:64px;height:64px;margin:0 auto 14px;display:block}
.brand{font-family:var(--display);font-weight:var(--dw);font-style:var(--ds);font-size:var(--bs,46px);line-height:1.02;
  letter-spacing:var(--bls,0)}
.tag{font-size:12.5px;letter-spacing:.3em;text-transform:uppercase;opacity:.86;margin-top:12px}
.table{display:inline-flex;gap:10px;align-items:center;margin-top:22px;padding:8px 18px;border-radius:999px;
  border:1px solid var(--table-line,currentColor);font-size:12.5px;letter-spacing:.2em;text-transform:uppercase}
.table b{font-family:var(--display);font-size:17px;letter-spacing:.04em;font-weight:var(--dw)}
.hi{padding:20px 22px 0;font-size:14.5px;color:var(--muted);text-align:center}
main.btns{padding:16px 18px 10px;display:grid;gap:11px}
.btn{display:flex;align-items:center;gap:14px;padding:15px 16px;border-radius:var(--r,18px);background:var(--card);
  color:var(--card-fg);border:1px solid var(--line);box-shadow:var(--shadow,0 8px 22px rgba(0,0,0,.05))}
.btn .ic{width:42px;height:42px;border-radius:calc(var(--r,18px) - 6px);display:grid;place-items:center;
  background:var(--chip);color:var(--chip-fg);flex:none}
.btn .ic svg{width:22px;height:22px}
.btn b{display:block;font-weight:600;font-size:16.5px}
.btn small{display:block;color:var(--muted);font-size:12.5px;margin-top:2px}
.btn .chev{margin-left:auto;opacity:.4;width:18px;height:18px}
.btn.primary{background:var(--accent);color:var(--accent-fg);border-color:transparent}
.btn.primary small{color:inherit;opacity:.78}
.btn.primary .ic{background:rgba(255,255,255,.16);color:inherit}
.row{display:grid;grid-template-columns:1fr 1fr;gap:11px}
.row .btn{flex-direction:column;align-items:flex-start;gap:10px}
.row .btn .chev{display:none}
.stars{color:var(--star,#E2A93B);letter-spacing:2px;font-size:13px}
.rate{margin:6px 18px 4px;padding:16px 18px;border-radius:var(--r,18px);border:1px solid var(--line);
  display:flex;align-items:center;gap:16px;background:var(--card);color:var(--card-fg)}
.rate .n{font-family:var(--display);font-weight:var(--dw);font-size:40px;line-height:1}
.rate small{display:block;color:var(--muted);font-size:12.5px;margin-top:3px}
.rate .bar{margin-left:auto;display:grid;gap:4px;width:92px}
.rate .bar i{display:block;height:5px;border-radius:3px;background:var(--line)}
.rate .bar i b{display:block;height:100%;border-radius:3px;background:var(--star,#E2A93B)}
.foot{padding:8px 22px 30px;text-align:center;color:var(--muted);font-size:12.5px;line-height:1.7}
.top{position:sticky;top:0;z-index:2;background:var(--hero);color:var(--hero-fg);padding:16px 18px;display:flex;
  align-items:center;justify-content:space-between}
.top .b{font-family:var(--display);font-weight:var(--dw);font-style:var(--ds);font-size:23px;letter-spacing:var(--bls,0)}
.top .t{font-size:11.5px;letter-spacing:.2em;border:1px solid var(--table-line,currentColor);border-radius:999px;
  padding:6px 12px;text-transform:uppercase}
.title{padding:22px 20px 4px;font-family:var(--display);font-weight:var(--dw);font-style:var(--ds);font-size:34px}
.lead{padding:0 20px;color:var(--muted);font-size:13.5px}
.tabs{display:flex;gap:8px;padding:14px 20px 8px;overflow:hidden;white-space:nowrap}
.tabs span{padding:9px 15px;border-radius:999px;background:var(--card);font-size:14px;border:1px solid var(--line)}
.tabs span.on{background:var(--accent);color:var(--accent-fg);border-color:transparent}
.feature{margin:12px 20px 4px;padding:16px 18px;border-radius:var(--r,18px);background:var(--feat,var(--accent));
  color:var(--feat-fg,var(--accent-fg));display:flex;justify-content:space-between;gap:12px;align-items:center}
.feature small{display:block;font-size:11px;letter-spacing:.22em;text-transform:uppercase;opacity:.8}
.feature b{display:block;font-family:var(--display);font-weight:var(--dw);font-style:var(--ds);font-size:21px;margin-top:3px}
.feature .price{color:inherit;font-size:18px}
section{padding:4px 20px 6px}
h2{font-family:var(--display);font-weight:var(--dw);font-style:var(--ds);font-size:21px;margin:16px 0 4px;display:flex;
  align-items:center;gap:12px;letter-spacing:var(--h2ls,0)}
h2:after{content:"";flex:1;height:1px;background:var(--line)}
.item{padding:13px 0;border-bottom:1px solid var(--line);display:grid;grid-template-columns:1fr auto;gap:3px 14px}
.item b{font-size:16.5px;font-weight:600}
.item p{grid-column:1;color:var(--muted);font-size:13.2px;line-height:1.45}
.price{font-family:Manrope,'Noto Sans',sans-serif;font-weight:600;font-size:15.5px;color:var(--price,var(--accent));
  white-space:nowrap;grid-row:1;grid-column:2}
.pill{display:inline-block;font-size:10.5px;letter-spacing:.06em;padding:3px 8px;border-radius:999px;
  background:var(--chip);color:var(--chip-fg);margin-left:6px;vertical-align:2px;font-weight:600}
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
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.8v2.4M12 18.8v2.4M2.8 12h2.4M18.8 12h2.4M5.5 5.5l1.7 1.7'
           'M16.8 16.8l1.7 1.7M5.5 18.5l1.7-1.7M16.8 7.2l1.7-1.7"/>',
}
CHEV = ('<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
        'stroke-linecap="round"><path d="M9 5l7 7-7 7"/></svg>')


def icon(k):
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
            f'stroke-linejoin="round">{ICON[k]}</svg>')


def e(s):
    return html.escape(s)


# ---------------------------------------------------------------- siteler

SITES = [
    dict(slug="kaleici", puan="4,8", yorum="2.316", name="Kaleiçi Sofrası", brand="KALEİÇİ", tag="Sofrası · Osmanlı mutfağı", masa="07", no=1,
         vars="--bg:#F6EFE3;--fg:#2B1A17;--muted:#8A7468;--line:#E6D8C3;--card:#FFFBF4;--card-fg:#2B1A17;"
              "--accent:#701E28;--accent-fg:#F3E6CC;--chip:#F2E3C9;--chip-fg:#701E28;--hero:#701E28;--hero-fg:#E9CF94;"
              "--display:Cinzel;--dw:800;--ds:normal;--bls:.06em;--price:#8C6A2E;--r:14px;--star:#C9A35C",
         extra=".hero{padding-top:70px}.tag{color:#F3E6CC}.brand{font-size:44px}",
         motif='<svg class="motif" viewBox="0 0 390 330" preserveAspectRatio="none" fill="none" stroke="#C9A35C" '
               'stroke-width="1.2" opacity=".55"><path d="M24 330V150C24 70 110 22 195 10 280 22 366 70 366 150V330"/>'
               '<path d="M34 330V152C34 78 116 34 195 22 274 34 356 78 356 152V330"/></svg>',
         mark='<svg class="mark" viewBox="0 0 64 64" fill="#C9A35C"><path d="M32 6c5 7 6 15 0 26-6-11-5-19 0-26z"/>'
              '<path d="M30 34C24 32 17 25 16 14c7 4 12 10 14 20zM34 34c6-2 13-9 14-20-7 4-12 10-14 20z"/>'
              '<rect x="31" y="32" width="2" height="22"/><path d="M32 52c-6-1-10-4-12-8 5 0 9 3 12 8zm0 0c6-1 10-4 '
              '12-8-5 0-9 3-12 8z"/></svg>',
         hi="Hoş geldiniz. Afiyet olsun.",
         buttons=[("menu", "Menü", "Kahvaltı, kebaplar, tatlılar", True), ("star", "Google'da değerlendirin", None, False),
                  ("bell", "Garson çağır", "Masa 07", False), ("wifi", "Wi-Fi", "Kaleici_Misafir", False),
                  ("cal", "Rezervasyon", "0242 000 00 00", False)],
         foot="Kaleiçi, Muratpaşa / Antalya · Her gün 08:00–24:00",
         feature=("Şefin önerisi", "Hünkâr beğendi", "540 ₺"),
         menu=[("Ana yemekler", [("Hünkâr beğendi", "Közlenmiş patlıcan beğendi, kuzu tandır", "540 ₺", "Şef"),
                                ("Kuzu tandır", "12 saat taş fırında, iç pilav ile", "620 ₺", None),
                                ("Ali Nazik", "Yoğurtlu közlenmiş patlıcan, kuzu kıyma", "480 ₺", None),
                                ("Etli yaprak sarma", "Ekşi erik ve tereyağı ile", "360 ₺", None)]),
               ("Tatlılar", [("Saray helvası", "Fıstıklı, kaymaklı", "220 ₺", None),
                             ("Kazandibi", "Tarçın ile", "180 ₺", None)])],
         tabs=["Ana yemekler", "Mezeler", "Tatlılar", "İçecekler"]),
    dict(slug="lagun", puan="4,7", yorum="1.184", name="Mavi Lagün", brand="Mavi Lagün", tag="Balık evi · Konyaaltı", masa="07", no=2,
         vars="--bg:#F3F1EC;--fg:#16213F;--muted:#6E7690;--line:#DDE0E6;--card:#FFFFFF;--card-fg:#16213F;"
              "--accent:#1E2A4A;--accent-fg:#F3EAD7;--chip:#E9EDF5;--chip-fg:#1E2A4A;--hero:#1E2A4A;--hero-fg:#F3EAD7;"
              "--display:Fraunces;--dw:600;--ds:italic;--price:#B4893F;--star:#CCA060",
         extra=".brand{font-size:50px}.tag{color:#CCA060}",
         motif='<svg class="motif" viewBox="0 0 390 320" preserveAspectRatio="none" fill="none" stroke="#CCA060" '
               'stroke-width="1.4" opacity=".45"><path d="M0 250c32-14 65-14 97 0s65 14 97 0 65-14 97 0 65 14 99 0"/>'
               '<path d="M0 272c32-14 65-14 97 0s65 14 97 0 65-14 97 0 65 14 99 0"/>'
               '<path d="M0 294c32-14 65-14 97 0s65 14 97 0 65-14 97 0 65 14 99 0"/></svg>',
         mark="", hi="Günün balığı tezgâhta. Afiyet olsun.",
         buttons=[("menu", "Menü", "Günün balığı, mezeler", True), ("star", "Google'da değerlendirin", None, False),
                  ("wifi", "Wi-Fi", "Lagun_Misafir", False), ("camera", "Instagram", "@mavilagun", False),
                  ("cal", "Rezervasyon", "Gün batımı masası", False)],
         foot="Konyaaltı Sahili / Antalya · 12:00–24:00",
         feature=("Bugün tezgâhta", "Levrek ızgara", "kg 1.400 ₺"),
         menu=[("Mezeler", [("Deniz börülcesi", "Zeytinyağı, sarımsak", "220 ₺", None),
                            ("Levrek marin", "Limon, roka, pembe biber", "340 ₺", "Şef"),
                            ("Fava", "Kırmızı soğan, dereotu", "180 ₺", None)]),
               ("Sıcaklar", [("Kalamar tava", "Tarator sos", "420 ₺", None),
                             ("Karides güveç", "Kaşarlı, tereyağlı", "480 ₺", None)])],
         tabs=["Mezeler", "Sıcaklar", "Balıklar", "Tatlı"]),
    dict(slug="forno", puan="4,9", yorum="862", name="Forno Rosso", brand="Forno Rosso", tag="Pizzeria napoletana", masa="07", no=3,
         vars="--bg:#F8F2E8;--fg:#3A1418;--muted:#8B6E66;--line:#EADCC8;--card:#FFFCF6;--card-fg:#3A1418;"
              "--accent:#8E2230;--accent-fg:#FFF4E2;--chip:#F6E7D2;--chip-fg:#8E2230;--hero:#F1E6D2;--hero-fg:#8E2230;"
              "--display:Playfair;--dw:900;--ds:normal;--price:#8E2230;--r:24px",
         extra=".hero{border-bottom:6px double #8E2230}.tag{color:#6A4C3C}.table{border-color:#8E2230}",
         motif='<svg class="motif" viewBox="0 0 390 330" fill="none" stroke="#8E2230" opacity=".13" stroke-width="2">'
               '<circle cx="195" cy="150" r="128"/><circle cx="195" cy="150" r="110"/></svg>',
         mark="", hi="Odun fırınında 90 saniye. Buon appetito!",
         buttons=[("menu", "Menü", "Pizzalar, makarnalar, tatlılar", True), ("star", "Yorum yap", None, False),
                  ("bag", "Paket sipariş", "Kapıya 30 dk", False), ("wifi", "Wi-Fi", "Forno_Misafir", False),
                  ("camera", "Instagram", "@fornorosso", False)],
         foot="Lara / Antalya · 12:00–23:30",
         feature=("Ayın pizzası", "Tartufo e funghi", "520 ₺"),
         menu=[("Pizzalar", [("Margherita", "San Marzano domates, fior di latte, fesleğen", "380 ₺", None),
                             ("Diavola", "Acı salam, mozzarella, kırmızı biber", "440 ₺", "Acı"),
                             ("Quattro formaggi", "Dört peynir, bal, ceviz", "460 ₺", None),
                             ("Tartufo e funghi", "Trüf kreması, mantar, parmesan", "520 ₺", "Yeni")])],
         tabs=["Pizzalar", "Makarnalar", "Salatalar", "Tatlılar"]),
    dict(slug="garaj", puan="4,7", yorum="1.507", name="Garaj Burger", brand="GARAJ", tag="Burger & Co.", masa="12", no=4,
         vars="--bg:#16161A;--fg:#F2EEE6;--muted:#9A968C;--line:#2C2C33;--card:#202026;--card-fg:#F2EEE6;"
              "--accent:#E0A436;--accent-fg:#16161A;--chip:#2C2C33;--chip-fg:#E0A436;--hero:#16161A;--hero-fg:#F2EEE6;"
              "--display:Anton;--dw:400;--ds:normal;--bls:.04em;--price:#E0A436;--r:8px;--shadow:none;--h2ls:.06em",
         extra=".brand{font-size:92px;line-height:.95}.tag{color:#E0A436}.hero{padding-top:54px;"
               "border-bottom:10px solid transparent;border-image:repeating-linear-gradient(-45deg,#E0A436 0 14px,"
               "#16161A 14px 28px) 10}.title,.top .b{text-transform:uppercase}h2{text-transform:uppercase}",
         motif="", mark="", hi="Siparişi masadan verin, biz getirelim.",
         buttons=[("menu", "Menü", "Burgerler, yanlar, shake", True), ("bag", "Masadan sipariş", "Masa 12", False),
                  ("star", "Puan ver", None, False), ("card", "Hesap öde", "Kart · QR", False),
                  ("wifi", "Wi-Fi", "Garaj_Misafir", False)],
         foot="Muratpaşa / Antalya · 12:00–02:00",
         feature=("Garajın klasiği", "Double smash", "460 ₺"),
         menu=[("Burgerler", [("Double smash", "2 × 90 g dana, cheddar, karamelize soğan, garaj sos", "460 ₺", "Klasik"),
                              ("Truffle", "180 g dana, trüf mayonez, mantar, gravyer", "520 ₺", None),
                              ("Hot chick", "Çıtır tavuk, acı bal, turşu", "390 ₺", "Acı"),
                              ("Veggie", "Nohut köftesi, avokado, turşu soğan", "360 ₺", "Vegan")])],
         tabs=["Burgerler", "Yanlar", "Shake", "İçecek"]),
    dict(slug="kopuk", puan="4,9", yorum="640", name="Köpük", brand="köpük", tag="Kahve & espresso", masa="03", no=6,
         vars="--bg:#F5EEE4;--fg:#3B2A22;--muted:#8F7B6C;--line:#E7D9C7;--card:#FFFBF5;--card-fg:#3B2A22;"
              "--accent:#4E3428;--accent-fg:#F5E9D8;--chip:#EFE2CF;--chip-fg:#4E3428;--hero:#C6A57F;--hero-fg:#3B2A22;"
              "--display:Fraunces;--dw:900;--ds:italic;--price:#4E3428;--r:26px",
         extra=".brand{font-size:72px}.hero{border-radius:0 0 40px 40px}",
         motif='<svg class="motif" viewBox="0 0 390 320" fill="none" stroke="#F5E9D8" stroke-width="5" '
               'stroke-linecap="round" opacity=".55"><path d="M150 40c12 14-12 22 0 38s-12 24 0 38"/>'
               '<path d="M195 30c12 14-12 22 0 38s-12 24 0 38"/><path d="M240 40c12 14-12 22 0 38s-12 24 0 38"/></svg>',
         mark="", hi="Wi-Fi şifresi arka yüzdeki QR'da.",
         buttons=[("menu", "Menü", "Kahveler, tatlılar, kahvaltı", True), ("wifi", "Wi-Fi'ye bağlan", "Tek dokunuş", False),
                  ("star", "Yorum yap", None, False), ("camera", "Instagram", "@kopukkahve", False)],
         foot="Kaleiçi / Antalya · 08:00–23:00",
         feature=("Bu hafta", "Fıstıklı latte", "165 ₺"),
         menu=[("Espresso bar", [("Espresso", "Tek ya da çift shot", "90 ₺", None),
                                 ("Flat white", "Çift ristretto, ipeksi süt", "140 ₺", None),
                                 ("Fıstıklı latte", "Antep fıstığı ezmesi", "165 ₺", "Yeni"),
                                 ("Türk kahvesi", "Lokum ile", "95 ₺", None)]),
               ("Tatlılar", [("San Sebastian", "Yanık cheesecake", "210 ₺", None)])],
         tabs=["Espresso bar", "Demleme", "Tatlılar", "Kahvaltı"]),
    dict(slug="koi", puan="4,8", yorum="498", name="Koi", brand="KOI", tag="Sushi & ramen", masa="08", no=10,
         vars="--bg:#F5F1E8;--fg:#141414;--muted:#77736A;--line:#E2DCCF;--card:#FFFDF8;--card-fg:#141414;"
              "--accent:#141414;--accent-fg:#F5F1E8;--chip:#F1E9DA;--chip-fg:#C0302C;--hero:#F5F1E8;--hero-fg:#141414;"
              "--display:Syne;--dw:800;--ds:normal;--bls:.18em;--price:#C0302C;--r:4px;--shadow:none",
         extra=".brand{font-size:62px}.hero{text-align:left;padding:74px 28px 30px}.tag{letter-spacing:.4em}"
               ".hero:after{content:'';position:absolute;right:28px;top:44px;width:74px;height:74px;border-radius:50%;"
               "background:#C0302C}.table{border-color:#141414}",
         motif="", mark="", hi="",
         buttons=[("menu", "Menü", "Sushi, ramen, izakaya", True), ("bag", "Masadan sipariş", "Masa 08", False),
                  ("star", "Yorum", None, False), ("wifi", "Wi-Fi", "Koi_Misafir", False)],
         foot="Lara / Antalya · 12:00–23:00",
         feature=("Omakase", "Şefin 12 parçası", "1.250 ₺"),
         menu=[("Sushi", [("Sake nigiri", "Somon, 2 adet", "220 ₺", None),
                          ("Dragon roll", "Karides tempura, avokado, unagi sos", "420 ₺", "Şef"),
                          ("Spicy tuna", "Ton balığı, acı mayonez", "380 ₺", "Acı")]),
               ("Ramen", [("Tonkotsu", "18 saat kemik suyu, chashu, yumurta", "460 ₺", None)])],
         tabs=["Sushi", "Ramen", "İzakaya", "Tatlı"]),
    dict(slug="asma", puan="4,6", yorum="2.904", name="Asmaaltı", brand="ASMAALTI", tag="Çay bahçesi", masa="11", no=13,
         vars="--bg:#F3F3EE;--fg:#2E1B1D;--muted:#7D7271;--line:#E1DDD4;--card:#FFFFFF;--card-fg:#2E1B1D;"
              "--accent:#6E1E2B;--accent-fg:#F7EBDD;--chip:#F1E7E2;--chip-fg:#6E1E2B;--hero:#6E1E2B;--hero-fg:#F7EBDD;"
              "--display:Playfair;--dw:900;--ds:normal;--bls:.05em;--price:#6E1E2B;--star:#CBA25E",
         extra=".brand{font-size:44px}.tag{color:#CBA25E}",
         motif='<svg class="motif" viewBox="0 0 390 320" fill="#CBA25E" opacity=".22"><path d="M30 40c30 0 50 20 52 50'
               '-30 0-50-20-52-50zM70 20c26 10 38 34 30 62-24-12-36-36-30-62zM330 270c-30 0-50-20-52-50 30 0 50 20 52 50z'
               'M360 240c-26-10-38-34-30-62 24 12 36 36 30 62z"/></svg>',
         mark="", hi="Semaverde taze çay, gölgede bir mola.",
         buttons=[("menu", "Menü", "Çay, gözleme, tost", True), ("bell", "Çay söyle", "Masa 11", False),
                  ("star", "Değerlendirin", None, False), ("wifi", "Wi-Fi", "Asma_Misafir", False)],
         foot="Düden / Antalya · 07:00–24:00",
         feature=("Semaver", "4 kişilik semaver çay", "260 ₺"),
         menu=[("Sıcak", [("Çay", "İnce belli bardakta", "25 ₺", None), ("Bitki çayı", "Ihlamur, adaçayı, kuşburnu", "60 ₺", None),
                          ("Sahlep", "Tarçınlı", "90 ₺", None)]),
               ("Atıştırmalık", [("Gözleme", "Peynirli, patatesli ya da kıymalı", "160 ₺", None),
                                 ("Kaşarlı tost", "Köy ekmeğiyle", "120 ₺", None)])],
         tabs=["Sıcak", "Soğuk", "Atıştırmalık", "Tatlı"]),
    dict(slug="kasap", puan="4,8", yorum="1.072", name="Kasaphane", brand="KASAPHANE", tag="Et lokantası · 1974'ten beri", masa="07", no=14,
         vars="--bg:#1C1714;--fg:#EFE6DA;--muted:#A49584;--line:#33291F;--card:#251E19;--card-fg:#EFE6DA;"
              "--accent:#B07C4F;--accent-fg:#1C1714;--chip:#33291F;--chip-fg:#D7A574;--hero:#1C1714;--hero-fg:#EFE6DA;"
              "--display:Bodoni;--dw:800;--ds:normal;--bls:.06em;--price:#D7A574;--r:6px;--shadow:none",
         extra=".brand{font-size:46px}.tag{color:#D7A574}.hero{border-bottom:1px solid #33291F}",
         motif="", mark='<svg class="mark" viewBox="0 0 64 64" fill="#D7A574"><path d="M14 22h30l6 6v12H14z"/>'
                        '<rect x="50" y="29" width="12" height="6" rx="3"/><circle cx="22" cy="28" r="2.2" fill="#1C1714"/>'
                        '</svg>',
         hi="Kesimler gramla, mangalda pişer.",
         buttons=[("menu", "Menü", "Kesimler, mezeler, şaraplar", True), ("star", "Google'da değerlendirin", None, False),
                  ("cal", "Rezervasyon", "Akşam 19:00–23:00", False), ("wifi", "Wi-Fi", "Kasaphane", False)],
         foot="Konyaaltı / Antalya · 12:00–24:00",
         feature=("Kasabın seçimi", "Dry-aged antrikot", "100 g 520 ₺"),
         menu=[("Kesimler", [("Dana antrikot", "28 gün dinlendirilmiş", "100 g 480 ₺", None),
                             ("Kuzu pirzola", "Kekik, deniz tuzu", "100 g 420 ₺", None),
                             ("Kasap köfte", "Elde çekilmiş, közlenmiş biber", "540 ₺", "Usta"),
                             ("Zırh kıyma Adana", "Kuyruk yağı, isot", "560 ₺", "Acı")])],
         tabs=["Kesimler", "Mezeler", "Yanlar", "Şarap"]),
    dict(slug="palmiye", puan="4,7", yorum="3.215", name="Palmiye", brand="Palmiye", tag="Beach club · Lara", masa="Şezlong 12", no=16,
         vars="--bg:#F4EDE1;--fg:#1D2742;--muted:#7C7F8F;--line:#E4D9C6;--card:#FFFDF8;--card-fg:#1D2742;"
              "--accent:#1D2742;--accent-fg:#F4EDE1;--chip:#EFE4D0;--chip-fg:#1D2742;--hero:#1D2742;--hero-fg:#F4EDE1;"
              "--display:Norican;--dw:400;--ds:normal;--price:#B98A4A;--r:22px",
         extra=".brand{font-size:66px}.tag{color:#D8BE95}.table b{font-family:Jost;font-weight:700}",
         motif='<svg class="motif" viewBox="0 0 390 320" fill="none"><circle cx="300" cy="70" r="36" fill="#D8BE95" '
               'opacity=".85"/><path d="M0 268c40-16 80-16 120 0s80 16 120 0 80-16 150 0V320H0z" fill="#26325A"/>'
               '<path d="M0 290c40-16 80-16 120 0s80 16 120 0 80-16 150 0V320H0z" fill="#2E3B66"/></svg>',
         mark="", hi="Şezlongunuza getirelim.",
         buttons=[("bag", "Şezlonga sipariş", "Şezlong 12", True), ("menu", "Menü", "Kokteyl, bowl, pizza", False),
                  ("sun", "Gün planı", "DJ 17:00 · Gün batımı 19:42", False), ("wifi", "Wi-Fi", "Palmiye_Beach", False)],
         foot="Lara Plajı / Antalya · 09:00–01:00",
         feature=("Gün batımı", "Aperol spritz", "420 ₺"),
         menu=[("Kokteyller", [("Aperol spritz", "Prosecco, soda, portakal", "420 ₺", None),
                               ("Mojito", "Taze nane, lime", "380 ₺", None),
                               ("Virgin colada", "Ananas, hindistancevizi", "260 ₺", "Alkolsüz")]),
               ("Bowl", [("Poke bowl", "Somon, avokado, edamame", "460 ₺", "Yeni")])],
         tabs=["Kokteyller", "Bowl", "Pizza", "Tatlı"]),
    dict(slug="r360", puan="4,8", yorum="1.390", name="Rooftop 360", brand="360°", tag="Rooftop · kokteyl & mutfak", masa="21", no=27,
         vars="--bg:#111112;--fg:#EEE8DC;--muted:#8E8A82;--line:#26262A;--card:#18181B;--card-fg:#EEE8DC;"
              "--accent:#C9A45E;--accent-fg:#111112;--chip:#232327;--chip-fg:#C9A45E;--hero:#111112;--hero-fg:#C9A45E;"
              "--display:Unbounded;--dw:800;--ds:normal;--price:#C9A45E;--r:10px;--shadow:none;--table-line:#C9A45E",
         extra=".brand{font-size:84px}.tag{color:#EEE8DC;letter-spacing:.42em}.hero{padding-top:66px}",
         motif='<svg class="motif" viewBox="0 0 390 330" fill="none" stroke="#C9A45E" stroke-width="1" opacity=".35">'
               '<path d="M0 300h40v-40h22v-60h30v80h26v-110h34v140h30v-70h28v40h36v-90h26v60h30v-30h22v60h30v20"/></svg>',
         mark="", hi="",
         buttons=[("menu", "Menü", "Kokteyller, tabaklar", True), ("cal", "Rezervasyon", "Teras · 18:00–02:00", False),
                  ("star", "Yorum", None, False), ("camera", "Instagram", "@rooftop360", False)],
         foot="Muratpaşa / Antalya · 18:00–02:00",
         feature=("İmza kokteyl", "360 Negroni", "560 ₺"),
         menu=[("İmza kokteyller", [("360 Negroni", "Gin, vermut, bitter, portakal dumanı", "560 ₺", "İmza"),
                                    ("Smoked old fashioned", "Burbon, akçaağaç, tütsü", "580 ₺", None),
                                    ("Gün batımı", "Tekila, kan portakalı, agave", "520 ₺", None)]),
               ("Tabaklar", [("Wagyu slider", "3 adet, trüf mayonez", "640 ₺", None)])],
         tabs=["Kokteyller", "Şarap", "Tabaklar", "Tatlı"]),
]


def page(site, body, title):
    return (f'<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" '
            f'content="width=device-width,initial-scale=1"><title>{e(title)}</title><style>{FONTS}'
            f':root{{{site["vars"]}}}{BASE}{site["extra"]}</style></head><body>{body}</body></html>')


def home(site):
    btns = []
    pending = []
    for ic, lab, sub, primary in site["buttons"]:
        sub_html = f"<small>{e(sub)}</small>" if sub else '<small class="stars">★★★★★</small>'
        btns.append(f'<a class="btn{" primary" if primary else ""}" href="{"menu.html" if ic == "menu" else "#"}">'
                    f'<span class="ic">{icon(ic)}</span><span><b>{e(lab)}</b>{sub_html}</span>{CHEV}</a>')
    first, rest = btns[:2], btns[2:]
    row = ""
    if len(rest) >= 2:
        row = '<div class="row">' + "".join(rest[:2]) + "</div>"
        rest = rest[2:]
    masa = site["masa"]
    table = (f'<span class="table">{e(masa)}</span>' if not masa[:1].isdigit() else
             f'<span class="table">Masa <b>{e(masa)}</b></span>')
    hi = f'<p class="hi">{e(site["hi"])}</p>' if site["hi"] else ""
    body = (f'<header class="hero">{site["motif"]}{site["mark"]}<div class="brand">{e(site["brand"])}</div>'
            f'<div class="tag">{e(site["tag"])}</div>{table}</header>{hi}'
            f'<main class="btns">{"".join(first)}{row}{"".join(rest)}</main>'
            f'<div class="rate"><span class="n">{site.get("puan", "4,8")}</span><span><span class="stars">★★★★★'
            f'</span><small>Google · {site.get("yorum", "1.240")} yorum</small></span><span class="bar">'
            + "".join(f'<i><b style="width:{w}%"></b></i>' for w in (86, 9, 3, 1, 1)) +
            f'</span></div><p class="foot">{e(site["foot"])}</p>')
    return page(site, body, site["name"])


def menu(site):
    tabs = "".join(f'<span class="{"on" if k == 0 else ""}">{e(t)}</span>' for k, t in enumerate(site["tabs"]))
    secs = []
    for cat, items in site["menu"]:
        rows = []
        for name, desc, price, pill in items:
            p = f'<span class="pill">{e(pill)}</span>' if pill else ""
            rows.append(f'<div class="item"><b>{e(name)}{p}</b><span class="price">{e(price)}</span>'
                        f'<p>{e(desc)}</p></div>')
        secs.append(f'<section><h2>{e(cat)}</h2>{"".join(rows)}</section>')
    small, big, price = site["feature"]
    masa = site["masa"]
    t = e(masa) if not masa[:1].isdigit() else f"Masa {e(masa)}"
    body = (f'<div class="top"><span class="b">{e(site["brand"])}</span><span class="t">{t}</span></div>'
            f'<h1 class="title">Menü</h1><p class="lead">Fiyatlara KDV dahildir.</p>'
            f'<div class="tabs">{tabs}</div>'
            f'<div class="feature"><span><small>{e(small)}</small><b>{e(big)}</b></span>'
            f'<span class="price">{e(price)}</span></div>{"".join(secs)}')
    return page(site, body, site["name"] + " · Menü")


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
                pg.wait_for_timeout(300)
                pg.evaluate("document.fonts.ready")
                pg.screenshot(path=os.path.join(d, out))
        br.close()


def main():
    only = sys.argv[1:]
    sites = [s for s in SITES if not only or s["slug"] in only]
    for s in sites:
        d = os.path.join(OUT, s["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(home(s))
        open(os.path.join(d, "menu.html"), "w", encoding="utf-8").write(menu(s))
    shoot(sites)
    print(f"{len(sites)} site yazıldı ve görüntülendi")


if __name__ == "__main__":
    main()
