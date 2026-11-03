"""BOYDE LABS – güzellik koleksiyonunun görselleri (Shopier ve tanıtım), 1200 × 1200 JPG.

Görsel dil BOYDE'nin öbür ürün görselleriyle aynı (scripts/boyde_katalog.py: logo, turuncu model kodu, buzlu cam
şerit; renk paleti değişmez); ürünlerin pembe, nude, lila tonları fotoğraflardan gelir.

Çıktı (boyde_labs/guzellik/shopier/):
  9x12/01_G01_<ürün>.jpg … 10    BOYDE çerçevesinde stüdyo fotoğrafı: kod, tasarım, sektör, renkler
  10x20/01_K01_<ürün>.jpg … 10
  <kat>/ek/kapak.jpg             kategori kapağı (masada birkaç isimlik, başlık)
  <kat>/ek/modeller.jpg          10 model bir arada (düz görünüşler, kodlarıyla)
  siteler/0N_<işletme>.jpg       5 site şablonu (6–10): isimliğin fotoğrafı ve telefonda QR'ın açtığı sayfa
Girdi : boyde_labs/guzellik/fotograf (scripts/boyde_guzellik.py --foto), kaynak/<ürün>_duz.png,
        boyde_labs/guzellik/siteler/<işletme>/ (örnek işletmelerin bilgileri; sablon_site ile kurulur)
Örneklerdeki işletme ve kişi adları, telefon (BOYDE'nin), IBAN ve QR'lar örnektir (QR'lar okunmaz).

Kullanım: python3 scripts/boyde_guzellik_gorsel.py
"""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_guzellik as G  # noqa: E402  (örnek modu: QR'lar okunmaz)
import boyde_katalog as K  # noqa: E402
import boyde_marka as BM  # noqa: E402

INK, PAPER, ORANGE, SAND = K.INK, K.PAPER, K.ORANGE, K.SAND
OUT = os.path.join(G.OUT, "shopier")
KAT = {"9x12": {"ad": "QR'lı masa isimliği", "olcu": "9 × 12 cm", "kisa": "Kuaför, güzellik salonu, tırnak, kirpik, "
                "cilt bakım, spa: masaya, tezgâha, kasaya.", "on": "g_"},
       "10x20": {"ad": "Kurumsal isimlik", "olcu": "10 × 20 cm", "kisa": "Saç tasarımcısı, nail artist, estetisyen, "
                 "makyaj ve kirpik uzmanı: ad soyad, görev, kartvizit QR'ı.", "on": "p_"}}
# örnek siteler: (işletme klasörü, şablon, isimliği)
SITELER = [("defne", 6, "g_defne"), ("sakayik", 7, "g_sakayik"), ("ela", 8, "g_ela"), ("lal", 9, "g_lal"),
           ("papatya", 10, "g_papatya")]


def foto(key, view="studyo", maxw=1200):
    return K.uri(os.path.join(G.FOTO, f"{key}_{view}.jpg"), maxw)


def acik_mi(key, view="studyo"):
    return K.light(os.path.join(G.FOTO, f"{key}_{view}.jpg"))


def cerceve(P, cat, u, path, view="studyo"):
    """BOYDE çerçevesi (boyde_katalog.framed ile aynı düzen): fotoğraf tam kadraj, sol üstte logo, sağ üstte ölçü,
    altta buzlu cam şeritte turuncu kod, tasarım ve sektör, renkler."""
    key, kod, kim, sektor, tasarim, renk = u
    acik = acik_mi(key, view)
    fg, sub = (INK, "#55575c") if acik else (PAPER, "rgba(244,241,234,.72)")
    glass, edge = ("rgba(255,255,255,.62)", "rgba(18,19,22,.08)") if acik else \
        ("rgba(18,19,22,.55)", "rgba(244,241,234,.12)")
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;overflow:hidden">
      <img src="{foto(key, view)}" style="position:absolute;inset:0;width:100%;height:100%;display:block">
      <div style="position:absolute;left:44px;top:40px">{K.logo("acik" if acik else "koyu", 260, 58)}</div>
      <span style="position:absolute;right:44px;top:44px;font-size:15px;font-weight:700;letter-spacing:.2em;
        color:{fg};opacity:.75">GÜZELLİK · {KAT[cat]['olcu'].upper()}</span>
      <div style="position:absolute;left:28px;right:28px;bottom:28px;display:flex;align-items:center;gap:22px;
        padding:18px 26px 18px 18px;border-radius:26px;background:{glass};backdrop-filter:blur(22px) saturate(1.3);
        box-shadow:inset 0 0 0 1.5px {edge};color:{fg}">
        <span class="code" style="flex:none;display:grid;place-items:center;width:84px;height:84px;border-radius:18px;
          background:{ORANGE};color:#fff;font-size:26px">{kod}</span>
        <div style="flex:1;min-width:0">
          <p class="u" style="font-size:27px;line-height:1.15;white-space:nowrap;overflow:hidden;
            text-overflow:ellipsis">{sektor} · {tasarim}</p>
          <p style="margin-top:7px;font-size:18px;color:{sub};white-space:nowrap;overflow:hidden;
            text-overflow:ellipsis">{renk} · örnek: {kim}</p></div>
        <p style="flex:none;text-align:right;font-size:14px;font-weight:700;letter-spacing:.14em;line-height:1.5;
          color:{sub}">TASARIM VE<br>3D BASKI <b style="color:{ORANGE}">BOYDE</b></p></div></div>""", path)


def kapak(P, cat, path):
    k = KAT[cat]
    src = os.path.join(G.FOTO, f"kapak_{cat}.jpg")
    acik = K.light(src)
    fg, sub = (INK, "#3b3d42") if acik else (PAPER, "rgba(244,241,234,.82)")
    golge = "" if acik else """<div style="position:absolute;inset:0;background:linear-gradient(180deg,
      rgba(18,19,22,.6) 0,rgba(18,19,22,0) 24%,rgba(18,19,22,0) 58%,rgba(18,19,22,.9) 100%)"></div>"""
    cips = "".join(f'<span class="chip" style="background:{"#fff" if acik else "rgba(244,241,234,.12)"};color:{fg};'
                   f'font-size:19px;padding:8px 14px">{x}</span>' for x in
                   ("10 tasarım", "çiçek motifleri", "pembe · nude · lila", "el yazısı", "QR'lı"))
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;overflow:hidden">
      <img src="{K.uri(src, 1200)}" style="position:absolute;inset:0;width:100%;height:100%;display:block">{golge}
      <div style="position:absolute;left:60px;top:52px">{K.logo("acik" if acik else "koyu", 300, 62)}</div>
      <div style="position:absolute;left:60px;right:60px;bottom:58px;color:{fg}">
        <p class="k">GÜZELLİK KOLEKSİYONU · {k['olcu'].upper()}</p>
        <h1 class="u" style="margin-top:14px;font-size:70px;line-height:1.02;letter-spacing:-.02em">{k['ad']}</h1>
        <p style="margin-top:16px;font-size:27px;line-height:1.35;color:{sub}">{k['kisa']}</p>
        <div style="margin-top:22px;display:flex;flex-wrap:wrap;gap:10px">{cips}</div></div></div>""", path)


def modeller(P, cat, path):
    us = [u for u in G.URUNLER if u[0].startswith(KAT[cat]["on"])]
    sut = 4 if cat == "9x12" else 3
    w = (1200 - 2 * 56 - (sut - 1) * 22) // sut
    kart = "".join(f"""<div style="width:{w}px;text-align:center">
      <div style="height:{w * (0.78 if cat == '9x12' else 0.56):.0f}px;display:grid;place-items:center">
        <img src="{K.uri(os.path.join(G.SRC, f'{key}_duz.png'), 700, 'PNG')}" style="max-width:100%;max-height:100%;
        filter:drop-shadow(0 10px 16px rgba(18,19,22,.18))"></div>
      <p style="margin-top:10px;font-size:17px;font-weight:700"><span class="code" style="color:{ORANGE}">{kod}</span>
        &nbsp;{sektor}</p></div>""" for key, kod, _, sektor, _, _ in us)
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:{PAPER};padding:56px;color:{INK}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <div><p class="k">GÜZELLİK KOLEKSİYONU · {KAT[cat]['olcu'].upper()}</p>
        <h2 class="u" style="margin-top:12px;font-size:44px;line-height:1.08">10 tasarım, hepsi size özel<br>
          renk ve yazıyla.</h2></div>{K.logo("acik", 220, 44)}</div>
      <div style="margin-top:40px;display:flex;flex-wrap:wrap;justify-content:center;gap:30px 22px">{kart}</div>
      <p style="position:absolute;left:56px;right:56px;bottom:40px;font-size:16px;color:#55575c">
        Örneklerdeki işletme ve kişi adları, telefon ve QR'lar örnektir; tasarım sizin bilgilerinizle hazırlanır.</p>
      </div>""", path)


def site_ekrani(klasor, n):
    """Örnek işletmenin sitesi (sablon_site, kayda yazılmaz) ve telefondaki ilk ekranı. Playwright'ı kendisi açar:
    görseller çizilmeden önce çağrılır. Döner (işletme, şablon adı, ekran görüntüsü PNG yolu, zemin rengi)."""
    import boyde_site_gorsel as SG
    import sablon_site as SS
    tmp = tempfile.mkdtemp()
    try:
        site, T, _ = SS.build(os.path.join(G.OUT, "siteler", klasor), n, out=tmp, previews=False, record=False)
        ekran = SG.capture(os.path.join(tmp, "site"))[0]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    yol = os.path.join(G.OUT, "siteler", klasor, "ekran_ust.png")
    ekran.save(yol, optimize=True)
    return site.isletme, T.AD, yol, SG.bg_of(yol)


def site_gorseli(P, i, ekran, key, path):
    """İsimlikten siteye: solda isimliğin fotoğrafı (karşıdan), sağda telefonda QR'ın açtığı sayfa (ilk ekran)."""
    import boyde_site_gorsel as SG
    isletme, sablon, yol, zemin = ekran
    tel = SG.phone(K.uri(yol, 780, "PNG"), 330, zemin)
    cips = "".join(f'<span class="chip" style="background:#fff;color:{INK};font-size:18px;padding:8px 13px">{x}</span>'
                   for x in ("Ara", "Randevu (WhatsApp)", "Instagram", "Google yorum", "Konum", "IBAN", "Rehbere kaydet"))
    K.sq(P, f"""<div style="position:relative;width:1200px;height:1200px;background:{PAPER};overflow:hidden;color:{INK}">
      <div style="position:absolute;left:56px;top:50px;right:56px;display:flex;justify-content:space-between">
        <div><p class="k">ÖRNEK SİTE · GÜZELLİK · {i}/{len(SITELER)}</p>
          <h1 class="u" style="margin-top:12px;font-size:44px;line-height:1.08">{isletme}</h1>
          <p style="margin-top:10px;font-size:22px;color:#55575c">Şablon: <b style="color:{INK}">{sablon}</b></p></div>
        {K.logo("acik", 210, 44)}</div>
      <div style="position:absolute;left:56px;top:250px;width:620px;height:620px;border-radius:34px;overflow:hidden;
        box-shadow:0 30px 60px -30px rgba(18,19,22,.45)">
        <img src="{foto(key, 'on', 900)}" style="width:100%;height:100%;object-fit:cover;display:block"></div>
      <div style="position:absolute;right:70px;top:196px">{tel}</div>
      <div style="position:absolute;left:56px;right:56px;bottom:52px">
        <p style="font-size:24px;line-height:1.4;color:#3b3d42;max-width:640px">İsimlikteki QR'ı okutan müşteri bu
          sayfayı açar. Her şey tek dokunuşla:</p>
        <div style="margin-top:16px;display:flex;flex-wrap:wrap;gap:10px">{cips}</div></div></div>""", path)


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    ekranlar = [site_ekrani(klasor, n) for klasor, n, _ in SITELER]
    with BM.painter() as P:
        for cat in KAT:
            out = os.path.join(OUT, cat)
            os.makedirs(os.path.join(out, "ek"))
            us = [u for u in G.URUNLER if u[0].startswith(KAT[cat]["on"])]
            for k, u in enumerate(us, 1):
                cerceve(P, cat, u, os.path.join(out, f"{k:02d}_{u[1]}_{u[0][2:]}.jpg"))
            kapak(P, cat, os.path.join(out, "ek", "kapak.jpg"))
            modeller(P, cat, os.path.join(out, "ek", "modeller.jpg"))
            print(f"shopier/{cat}: {len(us)} model, kapak, modeller", flush=True)
        os.makedirs(os.path.join(OUT, "siteler"))
        for i, ((klasor, _, key), ekran) in enumerate(zip(SITELER, ekranlar), 1):
            site_gorseli(P, i, ekran, key, os.path.join(OUT, "siteler", f"{i:02d}_{klasor}.jpg"))
            print(f"siteler/{i:02d}_{klasor}.jpg: {ekran[0]} · {ekran[1]}", flush=True)


if __name__ == "__main__":
    main()
