"""BOYDE LABS – kişiye özel plakalı anahtarlığın Shopier görselleri (scripts/boyde_plakali_anahtarlik.py --shopier ile
çağrılır). Görsel dil anahtarlıklarınkiyle aynı (boyde_anahtarlik_katalog: çerçeve, logo, renkler).

1200 × 1200 JPG, yükleme sırasıyla:
  01 kapak (altı plaka, kırmızı ve mavi) · 02 renk seçenekleri (aynı plaka kırmızı ve mavi, tek görselde) ·
  03 üç örnek · 04–06 örnekler önlü arkalı · 07 zincirli halka takımıyla ·
  08 ölçü ve özellikler (ön görünüş, 70 × 22 mm, renkler) · 09 nasıl sipariş verilir

Çıktı : boyde_labs/anahtarlik_plaka/shopier/*.jpg
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boyde_anahtarlik_katalog as KT  # noqa: E402
import boyde_katalog as K  # noqa: E402
import boyde_marka as BM  # noqa: E402
import boyde_plakali_anahtarlik as P  # noqa: E402

INK, PAPER, ORANGE, GRAY = K.INK, K.PAPER, K.ORANGE, K.GRAY
ETIKET = "KİŞİYE ÖZEL PLAKA"
OZELLIK = [("Plakanız ve yazınız", "Plaka 1,3 mm, alttaki ad ya da söz 1 mm kabartma; elle hissedilir."),
           ("Türk plakası görünümü", "Kırmızı ya da mavi TR bandı, beyaz plaka zemini, siyah çerçeve."),
           ("Sizin yazınız", "Ad soyad, lakap ya da kısa bir söz; Türkçe karakterlerle (İ, Ş, Ğ…)."),
           ("Sağlam ve hafif", "70 × 22 × 3 mm, 3D baskı PLA; 2 mm çerçeve, arka yüz düz."),
           ("Zincirli halka takımı", "Çelik halka, kısa zincir ve ara halka takılı gelir.")]
ADIM = [("01", "Plakanızı ve yazınızı yazın", "Sipariş notuna plaka, altına yazılacak ad ya da söz, bant rengi."),
        ("02", "Önizleme gönderiyoruz", "Anahtarlığınızın görüntüsünü WhatsApp'tan iletiyoruz."),
        ("03", "Onaylayın", "Beğendiyseniz onaylıyorsunuz; isterseniz yazıyı değiştiriyoruz."),
        ("04", "Basıp gönderiyoruz", "Kendi atölyemizde basıp kargoya veriyoruz.")]


def shopier(Pn):
    out = os.path.join(P.OUT, "shopier")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    name = lambda i, s: os.path.join(out, f"{i:02d}_{s}.jpg")              # noqa: E731
    foto = KT.foto

    # 01 kapak: altı plaka masada, beyaz fonda koyu yazı
    K.sq(Pn, f"""<div style="position:relative;width:1200px;height:1200px;background:#fff">
      <img src="{foto('kapak', 1200)}" style="width:1200px;height:1200px;display:block">
      <div style="position:absolute;left:64px;top:56px">{K.logo("acik", 330, 66)}</div>
      <div style="position:absolute;left:64px;right:64px;bottom:64px;color:{INK}">
        <p class="k">KİŞİYE ÖZEL · PLAKANIZ VE ADINIZ · KABARTMA</p>
        <h1 class="u" style="margin-top:14px;font-size:76px;line-height:1.02;letter-spacing:-.02em">Plakalı<br>
          anahtarlık</h1>
        <p style="margin-top:18px;font-size:30px;line-height:1.35;color:#3b3d42">Kendi plakanız, altında adınız; kırmızı
          ya da mavi TR bandı.</p></div></div>""", name(1, "kapak"))

    # 02 renk seçenekleri: aynı plaka kırmızı ve mavi bantla, tek görselde
    renk = "".join(f'<span class="chip" style="background:#fff;color:{INK};font-size:21px;padding:10px 16px;'
                   f'box-shadow:0 0 0 1.5px rgba(18,19,22,.08)"><i style="width:20px;height:20px;border-radius:6px;'
                   f'background:{r}"></i>&nbsp;{t}</span>' for r, t in (("#c41e26", "Kırmızı TR bandı"),
                                                                       ("#1c42a8", "Mavi TR bandı")))
    K.sq(Pn, f"""<div style="position:relative;width:1200px;height:1200px;overflow:hidden;background:#fff">
      <img src="{foto('renk', 1200)}" style="position:absolute;inset:0;width:1200px;height:1200px;display:block">
      <div style="position:absolute;left:64px;top:56px">{K.logo("acik", 260, 52)}</div>
      <div style="position:absolute;right:64px;top:62px;text-align:right;color:{INK}">
        <p class="k">RENK SEÇENEKLERİ</p>
        <h2 class="u" style="margin-top:10px;font-size:40px;line-height:1.08">Kırmızı ya da mavi,<br>siz seçin.</h2></div>
      <div style="position:absolute;left:64px;right:64px;bottom:56px;display:flex;flex-wrap:wrap;gap:12px">{renk}
      </div></div>""", name(2, "renk_secenek"))

    # 03 üç örnek: fotoğraf tam kadraj (fonu sayfanın fonu), üstte başlık, altta plakalar
    cipler = "".join(f'<span class="chip" style="background:#fff;color:{INK};font-size:19px;padding:8px 14px;'
                     f'box-shadow:0 0 0 1.5px rgba(18,19,22,.08)"><b>{plaka}</b>&nbsp;<span style="color:{GRAY}">·'
                     f'&nbsp;{ad}</span></span>' for _, plaka, ad, _ in P.ORNEK)
    K.sq(Pn, f"""<div style="position:relative;width:1200px;height:1200px;overflow:hidden;background:#fff">
      <img src="{foto('uc', 1200)}" style="position:absolute;inset:0;width:1200px;height:1200px;display:block">
      <div style="position:absolute;left:64px;top:56px">{K.logo("acik", 260, 52)}</div>
      <div style="position:absolute;right:64px;top:62px;text-align:right;color:{INK}">
        <p class="k">ÖRNEKLER</p>
        <h2 class="u" style="margin-top:10px;font-size:40px;line-height:1.08">Her plakaya,<br>her isme.</h2></div>
      <div style="position:absolute;left:64px;right:64px;bottom:56px;display:flex;flex-wrap:wrap;gap:10px">{cipler}
      </div></div>""", name(3, "uc_ornek"))

    # 04–06 önlü arkalı, 07 halka takımıyla
    for i, (a, plaka, ad, bant) in enumerate(P.ORNEK):
        KT.framed(Pn, f"{a}_iki", plaka[:2], f"{plaka} · {ad}", f"70 × 22 mm · {P.BANT_AD[bant]} TR bandı · önde "
                  "plaka ve yazı kabartma, arka yüz düz", name(4 + i, f"{a}_onlu_arkali"), ETIKET)
    a, plaka, ad, _ = P.ORNEK[0]
    KT.framed(Pn, f"{a}_halka", plaka[:2], "Zincirli halka takımıyla", "Çelik halka, kısa zincir ve ara halka; "
              "delik TR bandının üstünde", name(7, "halka"), ETIKET)

    # 08 ölçü ve özellikler: ön görünüş ölçülü (14,5 px/mm)
    px = 14.5
    on = K.uri(os.path.join(P.SRC, f"{a}_on.png"), 1100, "PNG")
    w, h = P.W * px, P.H * px
    feats = "".join(f"""<li style="display:flex;gap:12px"><b style="color:{ORANGE}">—</b><span><b>{x}.</b> {y}</span></li>"""
                    for x, y in OZELLIK)
    katman = "".join(f"""<div style="display:flex;align-items:center;gap:10px"><i style="width:18px;height:18px;
      border-radius:5px;background:{r};box-shadow:inset 0 0 0 1.5px rgba(18,19,22,.15)"></i><span>{t}</span></div>"""
                     for r, t in (("#1e1f23", "Siyah: çerçeve, alt şerit, plaka yazısı"),
                                  ("#eeeee9", "Beyaz: plaka zemini, TR, ad"),
                                  ("linear-gradient(135deg,#c41e26 50%,#1c42a8 50%)", "Kırmızı ya da mavi: TR bandı")))
    K.sq(Pn, f"""<div style="position:relative;width:1200px;height:1200px;background:{PAPER};padding:56px;color:{INK}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <div><p class="k">ÖLÇÜ VE ÖZELLİKLER</p>
        <h2 class="u" style="margin-top:12px;font-size:44px;line-height:1.08">Gerçek plaka gibi,<br>avucunuzda.</h2></div>
        {K.logo("acik", 220, 44)}</div>
      <div style="position:relative;margin-top:96px;width:{w:.0f}px;height:{h:.0f}px">
        <img src="{on}" style="width:100%;height:100%;display:block;filter:drop-shadow(0 14px 22px rgba(0,0,0,.2))">
        <div style="position:absolute;left:0;right:0;top:-34px;border-top:2px solid {GRAY};height:0"></div>
        <span style="position:absolute;left:50%;top:-56px;transform:translateX(-50%);padding:0 10px;background:{PAPER};
          font-size:20px;font-weight:700">70 mm</span>
        <div style="position:absolute;top:0;bottom:0;right:-34px;border-right:2px solid {GRAY};width:0"></div>
        <span style="position:absolute;top:50%;right:-92px;transform:translateY(-50%);font-size:20px;font-weight:700">
          22 mm</span></div>
      <div style="margin-top:26px;width:{w:.0f}px;display:flex;justify-content:space-between;font-size:17px;
        color:#55575c">{katman}</div>
      <ul style="margin-top:56px;list-style:none;display:grid;gap:18px;font-size:24px;line-height:1.35">{feats}</ul>
      </div>""", name(8, "olcu_ozellik"))

    # 09 nasıl sipariş verilir
    rows = "".join(f"""<div style="display:flex;gap:28px;padding:18px 0;border-top:2px solid rgba(244,241,234,.14)">
      <b class="u" style="font-size:44px;color:{ORANGE};width:90px">{a_}</b><div><p style="font-size:32px;
      font-weight:700">{b}</p><p style="margin-top:8px;font-size:23px;color:rgba(244,241,234,.72)">{c}</p></div>
      </div>""" for a_, b, c in ADIM)
    K.sq(Pn, f"""<div style="position:relative;width:1200px;height:1200px;background:{INK};color:{PAPER};padding:64px;
      background-image:{BM.stripes_bg(PAPER, .035, 30)}">
      <p class="k">NASIL SİPARİŞ VERİLİR</p>
      <h2 class="u" style="margin-top:12px;font-size:48px;line-height:1.1">Plakanızı yazın,<br>gerisini biz yapalım.</h2>
      <div style="margin-top:30px">{rows}</div>
      <img src="{foto('kapak', 1200)}" style="margin-top:14px;width:100%;height:230px;object-fit:cover;
        object-position:50% 30%;border-radius:22px;display:block">
      <div style="position:absolute;left:64px;bottom:50px">{K.logo("koyu", 300, 60)}</div>
      <p style="position:absolute;right:64px;bottom:60px;font-size:26px;font-weight:700">{K.TEL}</p></div>""",
         name(9, "nasil_siparis"))
    return out


def main():
    P.bagla()
    with BM.painter() as Pn:
        out = shopier(Pn)
    print(f"{os.path.relpath(out, P.A.ROOT)}: {len(os.listdir(out))} görsel")


if __name__ == "__main__":
    main()
