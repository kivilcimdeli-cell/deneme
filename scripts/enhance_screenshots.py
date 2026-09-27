"""Mağaza ekran görüntülerini yeniden oluşturur.

Her görsel için:
  * canlı degrade + güneş ışınları + bokeh + pati izli yeni arka plan
  * telefon/karakter katmanının arkasına parıltı ve yumuşak gölge
  * 3D efektli, degrade dolgulu, vurgulu kelimeli yeni başlık
  * kısa bir alt başlık etiketi ve parıltı süslemeleri

Girdi : screenshots/layers/0N_foreground.png  (arka planı ayrılmış ön plan)
Çıktı : screenshots/enhanced/0N.png           (1080x1920, RGB)

Kullanım: python3 scripts/enhance_screenshots.py
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "scripts", "fonts", "Baloo2-Variable.ttf")
W, H = 1080, 1920
SS = 2  # yazılar için süper örnekleme
HEAD_TOP = 34

SLIDES = [
    dict(
        name="01",
        bg=["#dff4ff", "#7cc4fa", "#2f78dc"],
        stroke="#f26a1b", extrude="#b9470b", shadow="#16407f",
        accent=["#fff27a", "#ffb31f"],
        lines=[[("Oyuncağın", "main")], [("canlanıyor!", "accent")]],
        subtitle="QR'ı okut, dostun yumurtadan çıksın!",
        sub_color="#1f5bb5", fg_dy=80,
        paw="#ffffff",
    ),
    dict(
        name="02",
        bg=["#fff0f6", "#ff9cc6", "#e64a8b"],
        stroke="#c2185b", extrude="#850d3d", shadow="#7d0f3b",
        accent=["#fff27a", "#ffb31f"],
        lines=[[("Besle, yıka,", "main")], [("sev!", "accent")]],
        subtitle="Mama, köpüklü banyo ve bol sevgi!",
        sub_color="#c2185b", fg_dy=0,
        paw="#ffffff",
    ),
    dict(
        name="03",
        bg=["#f1e8ff", "#b48cff", "#6c3fdc"],
        stroke="#5b21b6", extrude="#36107a", shadow="#2c0f6b",
        accent=["#fff27a", "#ffb31f"],
        lines=[[("9", "accent", 1.18), (" eğlenceli", "main")], [("mini oyun!", "main")]],
        subtitle="Koşu, Balon Uçuşu, Meyve Kes ve dahası!",
        sub_color="#5b21b6", fg_dy=0,
        paw="#ffffff",
    ),
    dict(
        name="04",
        bg=["#eaffdf", "#86dc72", "#2c9a4c"],
        stroke="#1b7a3a", extrude="#0d5024", shadow="#0d4a22",
        accent=["#fff27a", "#ffb31f"],
        lines=[[("Oyna,", "main")], [("altın", "accent"), (" kazan!", "main")]],
        subtitle="Kazandığın altınlarla dostlarını şımart!",
        sub_color="#1b7a3a", fg_dy=0,
        paw="#ffffff",
    ),
    dict(
        name="05",
        bg=["#fff7d6", "#ffc653", "#f2761b"],
        stroke="#6d28c9", extrude="#43138a", shadow="#7a3408",
        accent=["#fff27a", "#ffb31f"],
        lines=[[("Efsanevi", "accent"), (" dostlar", "main")], [("seni bekliyor!", "main")]],
        subtitle="Ejderha, tek boynuzlu at ve dahası!",
        sub_color="#6d28c9", fg_dy=0,
        paw="#ffffff",
    ),
]


# ---------------------------------------------------------------- yardımcılar
def rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def font(size, weight=800):
    f = ImageFont.truetype(FONT, int(size))
    f.set_variation_by_axes([weight])
    return f


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def shift(mask, dx, dy):
    """L-modu maskeyi kaydırır (taşan kısım kırpılır)."""
    out = Image.new("L", mask.size, 0)
    out.paste(mask, (dx, dy))
    return out


def solid(color, alpha_mask, opacity=1.0):
    """Tek renkli RGBA katman; alfa = maske * opaklık."""
    layer = Image.new("RGBA", alpha_mask.size, tuple(int(c) for c in rgb(color)) + (0,))
    a = alpha_mask if opacity == 1.0 else alpha_mask.point(lambda v: int(v * opacity))
    layer.putalpha(a)
    return layer


# ---------------------------------------------------------------- arka plan
def paw_print(size, color, alpha):
    s = size * 4
    im = Image.new("L", (s, s), 0)
    d = ImageDraw.Draw(im)
    d.ellipse((s * .22, s * .42, s * .78, s * .92), fill=255)        # taban
    for cx, cy in ((.16, .40), (.36, .18), (.64, .18), (.84, .40)):  # parmaklar
        r = s * .12
        d.ellipse((s * cx - r, s * cy - r * 1.15, s * cx + r, s * cy + r * 1.15), fill=255)
    im = im.resize((size, size), Image.LANCZOS)
    return solid(color, im, alpha)


def sparkle(size, color=(255, 255, 255)):
    """4 kollu parıltı yıldızı + hale."""
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    glow = Image.new("L", (s, s), 0)
    ImageDraw.Draw(glow).ellipse((s * .3, s * .3, s * .7, s * .7), fill=150)
    glow = glow.filter(ImageFilter.GaussianBlur(s * .08))
    im.paste(Image.new("RGBA", (s, s), color + (255,)), (0, 0), glow)
    pts = []
    for k in range(8):
        ang = k * math.pi / 4 - math.pi / 2
        r = s * .5 if k % 2 == 0 else s * .075
        pts.append((s / 2 + r * math.cos(ang), s / 2 + r * math.sin(ang)))
    star = Image.new("L", (s, s), 0)
    ImageDraw.Draw(star).polygon(pts, fill=255)
    im.paste(Image.new("RGBA", (s, s), color + (255,)), (0, 0), star)
    return im.resize((size, size), Image.LANCZOS)


def background(cfg, rng, center):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = center
    dx, dy = (xx - cx) / W, (yy - cy) / W
    r = np.sqrt(dx * dx + dy * dy)
    t = np.clip(r / 1.05, 0, 1)

    c0, c1, c2 = (rgb(c) for c in cfg["bg"])
    k1 = smoothstep(0.0, 0.45, t)[..., None]
    k2 = smoothstep(0.35, 1.0, t)[..., None]
    img = c0 * (1 - k1) + c1 * k1
    img = img * (1 - k2) + c2 * k2

    # güneş ışınları
    th = np.arctan2(dy, dx)
    rays = np.clip((np.cos(18 * th + 0.3) - 0.05) * 2.2, 0, 1)
    ray_a = rays * 0.16 * smoothstep(0.05, 0.25, r) * (1 - 0.55 * t)
    img = img + (255 - img) * ray_a[..., None]

    # kenar kararması
    img = img * (1 - 0.16 * smoothstep(0.55, 1.15, r))[..., None]
    bg = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").convert("RGBA")

    # bokeh
    bok = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(bok)
    for _ in range(34):
        x, y = rng.uniform(0, W), rng.uniform(300, H)
        rad = rng.uniform(10, 46)
        d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=(255, 255, 255, int(rng.uniform(22, 60))))
    bg.alpha_composite(bok.filter(ImageFilter.GaussianBlur(5)))

    # pati izleri
    for _ in range(16):
        size = int(rng.uniform(60, 110))
        p = paw_print(size, cfg["paw"], rng.uniform(0.13, 0.20)).rotate(
            rng.uniform(-40, 40), resample=Image.BICUBIC, expand=True)
        bg.alpha_composite(p, (int(rng.uniform(-20, W - 60)), int(rng.uniform(380, H - 80))))
    return bg


# ---------------------------------------------------------------- başlık
def gradient_fill(mask, top_rgb, bot_rgb, y0, y1):
    """Maskeyi y0→y1 arasında dikey degrade ile boyar."""
    w, h = mask.size
    t = np.clip((np.arange(h, dtype=np.float32) - y0) / max(1, y1 - y0), 0, 1)[:, None, None]
    col = rgb(top_rgb) * (1 - t) + rgb(bot_rgb) * t
    arr = np.broadcast_to(col, (h, w, 3)).astype(np.uint8)
    layer = Image.fromarray(arr, "RGB").convert("RGBA")
    layer.putalpha(mask)
    return layer


def headline(cfg, max_width=990, cap=150, tilt=-2.0):
    # yazı boyutunu en geniş satıra göre sığdır
    def line_width(line, size):
        return sum(font(size * (seg[2] if len(seg) > 2 else 1)).getlength(seg[0]) for seg in line)

    size = cap
    while max(line_width(l, size) for l in cfg["lines"]) + 2 * 0.1 * size > max_width:
        size -= 2

    S = SS
    fs = size * S
    stroke_w = int(fs * 0.10)
    extrude = int(fs * 0.09)
    lead = fs * 0.90
    cw, ch = W * S, int(len(cfg["lines"]) * lead + fs * 0.9 + extrude + stroke_w * 2)
    main_m = Image.new("L", (cw, ch), 0)
    acc_m = Image.new("L", (cw, ch), 0)
    stroke_m = Image.new("L", (cw, ch), 0)
    line_boxes = []
    for li, line in enumerate(cfg["lines"]):
        base = stroke_w + fs * 0.78 + li * lead
        x = (cw - line_width(line, fs)) / 2
        for seg in line:
            text, kind = seg[0], seg[1]
            f = font(fs * (seg[2] if len(seg) > 2 else 1))
            ImageDraw.Draw(acc_m if kind == "accent" else main_m).text((x, base), text, font=f, anchor="ls", fill=255)
            ImageDraw.Draw(stroke_m).text((x, base), text, font=f, anchor="ls", fill=255,
                                          stroke_width=stroke_w, stroke_fill=255)
            x += f.getlength(text)
        line_boxes.append((base - fs * 0.62, base + fs * 0.05))

    fill_m = Image.fromarray(np.maximum(np.asarray(main_m), np.asarray(acc_m)))

    # 3D gövde: kontur maskesini aşağı doğru üst üste yığ
    ext = np.asarray(stroke_m).copy()
    sm = np.asarray(stroke_m)
    for k in range(1, extrude + 1):
        ext[k:] = np.maximum(ext[k:], sm[:-k])
    ext_m = Image.fromarray(ext)

    out = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    shadow = shift(ext_m, 0, int(fs * 0.05)).filter(ImageFilter.GaussianBlur(fs * 0.05))
    out.alpha_composite(solid(cfg["shadow"], shadow, 0.45))
    out.alpha_composite(solid(cfg["extrude"], ext_m))
    out.alpha_composite(solid(cfg["stroke"], stroke_m))

    for (y0, y1) in line_boxes:
        band = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(band).rectangle((0, y0 - fs * 0.35, cw, y1 + fs * 0.3), fill=255)
        m = Image.fromarray(np.minimum(np.asarray(main_m), np.asarray(band)))
        a = Image.fromarray(np.minimum(np.asarray(acc_m), np.asarray(band)))
        out.alpha_composite(gradient_fill(m, "#ffffff", "#fff1e6", y0, y1))
        out.alpha_composite(gradient_fill(a, cfg["accent"][0], cfg["accent"][1], y0, y1))

    # harflerin alt kenarına iç gölge, üst kenarına parlama
    fm = np.asarray(fill_m).astype(np.int16)
    up = np.zeros_like(fm); up[:-int(fs * 0.03)] = fm[int(fs * 0.03):]
    inner = Image.fromarray(np.clip(fm - up, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(S))
    out.alpha_composite(solid(cfg["extrude"], inner, 0.22))
    dn = np.zeros_like(fm); dn[int(fs * 0.025):] = fm[:-int(fs * 0.025)]
    gloss = Image.fromarray(np.clip(fm - dn, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(S))
    out.alpha_composite(solid("#ffffff", gloss, 0.75))

    out = out.resize((cw // S, ch // S), Image.LANCZOS)
    out = out.rotate(tilt, resample=Image.BICUBIC, expand=True)
    return out.crop(out.getchannel("A").getbbox())


def subtitle_pill(cfg, size=36):
    S = SS
    f = font(size * S, 700)
    tw = f.getlength(cfg["subtitle"])
    padx, h = 34 * S, int(size * S * 1.6)
    w = int(tw + 2 * padx)
    m = int(24 * S)
    im = Image.new("RGBA", (w + 2 * m, h + 2 * m), (0, 0, 0, 0))
    sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle((m, m + 6 * S, m + w, m + h + 6 * S), radius=h // 2, fill=255)
    im.alpha_composite(solid(cfg["shadow"], sh.filter(ImageFilter.GaussianBlur(9 * S)), 0.35))
    pill = Image.new("L", im.size, 0)
    ImageDraw.Draw(pill).rounded_rectangle((m, m, m + w, m + h), radius=h // 2, fill=255)
    im.alpha_composite(solid("#ffffff", pill, 0.96))
    ImageDraw.Draw(im).text((m + w / 2, m + h / 2 + size * S * 0.08), cfg["subtitle"], font=f,
                            anchor="mm", fill=tuple(int(c) for c in rgb(cfg["sub_color"])) + (255,))
    return im.resize((im.width // S, im.height // S), Image.LANCZOS)


# ---------------------------------------------------------------- birleştirme
def build(cfg, seed):
    rng = random.Random(seed)
    fg = Image.open(os.path.join(ROOT, "screenshots", "layers", f"{cfg['name']}_foreground.png")).convert("RGBA")
    if cfg["fg_dy"]:
        moved = Image.new("RGBA", fg.size, (0, 0, 0, 0))
        moved.paste(fg, (0, cfg["fg_dy"]))
        fg = moved

    # ön plan rengini hafifçe canlandır
    rgb_part = fg.convert("RGB")
    rgb_part = ImageEnhance.Color(rgb_part).enhance(1.10)
    rgb_part = ImageEnhance.Contrast(rgb_part).enhance(1.04)
    rgb_part = rgb_part.filter(ImageFilter.UnsharpMask(radius=1.2, percent=40, threshold=2))
    alpha = fg.getchannel("A")
    fg = rgb_part.convert("RGBA")
    fg.putalpha(alpha)

    bx0, by0, bx1, by1 = alpha.getbbox()
    center = ((bx0 + bx1) / 2, (by0 + by1) / 2 + 40)
    canvas = background(cfg, rng, center)

    # telefonun arkasında parıltı
    glow = Image.new("L", (W, H), 0)
    gx, gy = center
    ImageDraw.Draw(glow).ellipse((gx - 440, gy - 640, gx + 440, gy + 640), fill=255)
    canvas.alpha_composite(solid("#ffffff", glow.filter(ImageFilter.GaussianBlur(110)), 0.55))

    # parıltılar (ön planın arkasında)
    for (x, y, s) in [(70, 470, 70), (1010, 700, 54), (60, 1060, 48), (1020, 1250, 64),
                      (130, 1880, 40), (960, 1880, 46), (40, 1500, 36), (1040, 420, 40)]:
        sp = sparkle(int(s * rng.uniform(0.9, 1.2)))
        canvas.alpha_composite(sp, (int(x - sp.width / 2), int(y - sp.height / 2)))

    # yumuşak gölge + beyaz kontur hâlesi
    shadow = shift(alpha, 0, 22).filter(ImageFilter.GaussianBlur(24))
    canvas.alpha_composite(solid(cfg["shadow"], shadow, 0.42))
    rim = alpha.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(4))
    canvas.alpha_composite(solid("#ffffff", rim, 0.35))
    canvas.alpha_composite(fg)

    # ön planın üstünde birkaç küçük parıltı
    for (x, y, s) in [(fg.width * 0.5 + 330, 520 + cfg["fg_dy"], 44), (bx0 + 40, by1 - 360, 34)]:
        sp = sparkle(int(s))
        canvas.alpha_composite(sp, (int(x - sp.width / 2), int(y - sp.height / 2)))

    head = headline(cfg)
    canvas.alpha_composite(head, ((W - head.width) // 2, HEAD_TOP))
    pill = subtitle_pill(cfg)
    px, py = (W - pill.width) // 2, HEAD_TOP + head.height - 20
    canvas.alpha_composite(pill, (px, py))
    print(f"  {cfg['name']}: başlık {head.size}, etiket y={py + 24}-{py + pill.height - 24}, "
          f"x={px + 24}-{px + pill.width - 24}")
    return canvas.convert("RGB")


def main():
    out_dir = os.path.join(ROOT, "screenshots", "enhanced")
    os.makedirs(out_dir, exist_ok=True)
    for i, cfg in enumerate(SLIDES):
        img = build(cfg, seed=17 + i)
        path = os.path.join(out_dir, f"{cfg['name']}.png")
        img.save(path, optimize=True)
        print("yazıldı:", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main()
