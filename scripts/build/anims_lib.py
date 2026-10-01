"""教學模擬動畫庫：依「畫面規格.yaml」的 type: anim 畫出逐格畫面（1920×1080）
用法（由 build.py 呼叫）：frame(p, t, dur, ev) → PIL RGB
- p：畫面參數（anim＝動畫名稱，其餘為參數）
- t：從這個鏡頭開始經過的秒數；dur：鏡頭長度；ev：steps 對應的事件時間（相對秒數，依旁白句子）
- 規則：上下各留 110 px 給電影黑邊（內容放在 y 130–950）；右下角留白給浮水印；不用 emoji
- 靜態底圖會快取，每格只畫會動的部分
"""
import math, random
from PIL import Image, ImageDraw, ImageFilter
import cards_lib as C
from cards_lib import W, H, font, tw, ctext, mtext, NAVY, NAVY2, WHITE, INK, GOLD, CYAN, CYAN_D, ORANGE, GREEN, RED, BLUE, PURPLE, GRAY, LGRAY

_cache = {}


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x); return x * x * (3 - 2 * x)


def back(x):
    """回彈（超過一點再回來）"""
    if x <= 0: return 0.0
    x = clamp(x); c = 0.9                             # 回彈幅度（原 1.70 太晃）
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def prog(t, e, d=0.6):
    return ease((t - e) / d)


def ev_at(ev, i, default):
    return ev[i] if i < len(ev) else default


def dark_bg(key, glow=(40, 90, 150)):
    """深藍漸層＋中央柔光＋淡格線（品牌深色底）"""
    k = ("bg", key)
    if k not in _cache:
        im = Image.new("RGB", (W, H), NAVY)
        g = Image.radial_gradient("L").resize((W, H), Image.BICUBIC).point(lambda v: int(max(0, 255 - v) * 0.55))
        im.paste(Image.new("RGB", (W, H), glow), (0, 0), g)
        d = ImageDraw.Draw(im)
        for x in range(0, W, 80): d.line([(x, 0), (x, H)], fill=(18, 42, 76))
        for y in range(0, H, 80): d.line([(0, y), (W, y)], fill=(18, 42, 76))
        _cache[k] = im
    return _cache[k].copy()


def text_layer(s, f, fill, stroke=0):
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    l, t, r, b = d.textbbox((0, 0), s, font=f, stroke_width=stroke)
    lay = Image.new("RGBA", (r - l + 20, b - t + 20), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((10 - l, 10 - t), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=INK)
    return lay


def paste_alpha(im, lay, xy, a):
    if a <= 0: return
    if a < 1:
        lay = lay.copy(); lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    im.paste(lay, (int(xy[0]), int(xy[1])), lay)


def title_bar(im, d, s, a=1.0, y=150):
    """動畫上方標題（淡入）"""
    lay = _cache.setdefault(("tt", s), text_layer(s, font(60), WHITE))
    paste_alpha(im, lay, (W / 2 - lay.width / 2, y - 10 + 14 * (1 - a)), a)


# ======================= 1. 預告片式標題 =======================
def a_title_reveal(p, t, dur, ev):
    """黑底 → 金線展開 → 主標由下浮現＋光束掃過 → 小標、副標淡入；結尾可淡出"""
    im = dark_bg("title", (30, 70, 120))
    im = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), im, prog(t, 0, 0.8))
    d = ImageDraw.Draw(im)
    cy = p.get("y", 470)
    lw = 1000 * ease((t - 0.3) / 0.9)
    if lw > 2: d.rectangle([W / 2 - lw / 2, cy + 150, W / 2 + lw / 2, cy + 154], fill=GOLD)
    lines = p.get("lines") or [p["title"]]
    for i, s in enumerate(lines):
        f = C.fit(d, s, p.get("size", 150 if len(lines) == 1 else 110), W - 240)
        k = ("tl", s, f.size)
        if k not in _cache: _cache[k] = text_layer(s, f, GOLD if i in p.get("hl", []) else WHITE)
        lay = _cache[k]
        a = prog(t, 0.5 + i * 0.35, 0.9)
        y = cy - (len(lines) - 1) * 70 + i * 140 - lay.height / 2 + 40 * (1 - a)
        paste_alpha(im, lay, (W / 2 - lay.width / 2, y), a)
        sx = (t - 1.1 - i * 0.35) / 1.2                   # 光束掃過
        if 0 < sx < 1:
            band = Image.new("L", lay.size, 0); bd = ImageDraw.Draw(band)
            x = -300 + sx * (lay.width + 600)
            bd.polygon([(x, 0), (x + 120, 0), (x + 40, lay.height), (x - 80, lay.height)], fill=200)
            band = band.filter(ImageFilter.GaussianBlur(18))
            m = Image.fromarray(__import__("numpy").minimum(__import__("numpy").array(band), __import__("numpy").array(lay.getchannel("A"))))
            im.paste(Image.new("RGB", lay.size, (255, 250, 230)), (int(W / 2 - lay.width / 2), int(y)), m)
    if p.get("kicker"):
        a = prog(t, 1.3, 0.8); ctext(ImageDraw.Draw(im), W / 2, cy - 80 - len(lines) * 70 - 20 * (1 - a), p["kicker"], font(56), tuple(int(v * a) for v in CYAN))
    if p.get("sub"):
        a = prog(t, 1.8, 0.8); f = C.fit(d, p["sub"], 44, W - 300, False)
        ctext(ImageDraw.Draw(im), W / 2, cy + 190, p["sub"], f, tuple(int(185 * a) for _ in range(3)))
    out = p.get("fade_out")
    if out: im = Image.blend(im, Image.new("RGB", (W, H), (0, 0, 0)), prog(t, dur - out, out))
    return im


# ======================= 2. 月亮觀測模擬 =======================
def _moon_disk(r, theta, lit=(250, 246, 225), dark=(45, 55, 75)):
    """月相：theta＝0 新月、π/2 上弦、π 滿月（盈月，右側亮）"""
    import numpy as np
    n = int(r * 2 + 4); yy, xx = np.mgrid[0:n, 0:n] - (n / 2)
    inside = xx ** 2 + yy ** 2 <= r * r
    xt = r * math.cos(theta) * np.sqrt(np.clip(1 - (yy / r) ** 2, 0, 1))
    litm = inside & (xx > xt)
    img = np.zeros((n, n, 4), np.uint8)
    img[inside] = dark + (255,); img[litm] = lit + (255,)
    im = Image.fromarray(img, "RGBA")
    glow = Image.new("RGBA", (n + 80, n + 80), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([40, 40, n + 40, n + 40], fill=(255, 240, 200, 90 if theta > 0.6 else 50))
    glow = glow.filter(ImageFilter.GaussianBlur(22)); glow.alpha_composite(im, (40, 40))
    return glow


def _sky():
    if "sky" in _cache: return _cache["sky"].copy()
    import numpy as np
    hy = 800
    top, mid, low = np.array([10, 22, 58]), np.array([38, 60, 120]), np.array([235, 150, 90])
    y = np.linspace(0, 1, hy)[:, None]
    col = np.where(y < 0.65, top + (mid - top) * (y / 0.65), mid + (low - mid) * ((y - 0.65) / 0.35))
    sky = np.repeat(col[:, None, :], W, axis=1).reshape(hy, W, 3)
    xx = np.linspace(0, 1, W)[None, :, None]                 # 西邊（右）比較亮
    sky = sky + np.clip((xx - 0.6) / 0.4, 0, 1) * np.clip((y[:, :, None] - 0.5) / 0.5, 0, 1) * np.array([60, 30, 0])
    im = Image.new("RGB", (W, H), (14, 20, 30)); im.paste(Image.fromarray(np.clip(sky, 0, 255).astype("uint8")), (0, 0))
    d = ImageDraw.Draw(im); rnd = random.Random(3)
    for _ in range(140):
        x, yy = rnd.randrange(W), rnd.randrange(40, 520); v = rnd.randrange(120, 230)
        d.ellipse([x, yy, x + 2, yy + 2], fill=(v, v, v))
    # 校園剪影：樹、教學大樓
    sil = (14, 20, 30)
    for x0, w, h in [(0, 260, 120), (240, 520, 180), (760, 160, 90), (1180, 420, 150), (1600, 320, 110)]:
        d.rectangle([x0, hy - h, x0 + w, hy], fill=sil)
        for k in range(x0 + 20, x0 + w - 20, 46):
            for j in range(hy - h + 22, hy - 20, 40):
                if rnd.random() < 0.45: d.rectangle([k, j, k + 18, j + 16], fill=(90, 80, 50))
    for x in range(0, W, 90):
        r = rnd.randrange(40, 80); d.ellipse([x - r, hy - r - rnd.randrange(0, 40), x + r, hy + r], fill=sil)
    d.rectangle([0, hy, W, H], fill=sil)
    for lab, x in [("東", 200), ("南", W / 2), ("西", W - 420)]:       # 西避開右下角浮水印
        ctext(d, x, hy + 30, lab, font(52), (200, 210, 230))
    _cache["sky"] = im
    return im.copy()


def _moon_pos(age):
    """黃昏 18:00（台南，北緯 23°）盈月的位置：離太陽角距約 12.2°×月齡；近似赤緯 0"""
    e = math.radians(12.2 * age); lat = math.radians(23)
    ha = math.pi / 2 - e                                        # 太陽剛落時時角約 +6h
    alt = math.asin(math.cos(lat) * math.cos(ha))
    az = math.atan2(math.sin(ha), math.cos(ha) * math.sin(lat))  # 由南往西量
    x = W / 2 + math.degrees(az) / 95 * (W / 2 - 170)
    y = 800 - math.degrees(alt) / 75 * 600
    return x, y, e


def a_moon(p, t, dur, ev):
    im = _sky(); d = ImageDraw.Draw(im)
    ages = p.get("ages", [3, 5, 7, 9])
    start = ev_at(ev, 0, 1.2); gap = p.get("gap", min(1.3, max(0.6, (dur - start - 1.5) / max(1, len(ages)))))
    box = [120, 150, 700, 250]
    d.rounded_rectangle(box, radius=24, fill=(10, 24, 50)); d.text((150, 168), p.get("label", "每天 18:00，面向南方觀察"), font=font(46), fill=WHITE)
    pts = [_moon_pos(a) for a in ages]
    shown_n = 1 + sum(1 for i in range(1, len(ages)) if t >= start + (i - 1) * gap)
    for i in range(1, shown_n):                                  # 虛線軌跡
        a = prog(t, start + (i - 1) * gap, gap * 0.8)
        (x0, y0, _), (x1, y1, _) = pts[i - 1], pts[i]
        for k in range(0, 20):
            if k / 20 > a: break
            if k % 2 == 0:
                d.line([(x0 + (x1 - x0) * k / 20, y0 + (y1 - y0) * k / 20), (x0 + (x1 - x0) * (k + 1) / 20, y0 + (y1 - y0) * (k + 1) / 20)], fill=GOLD, width=5)
    for i in range(shown_n):
        x, y, e = pts[i]
        a = 1 if i == 0 else prog(t, start + (i - 1) * gap + gap * 0.5, 0.5)
        mk = ("moon", i)
        if mk not in _cache: _cache[mk] = _moon_disk(46, e)
        m = _cache[mk]
        paste_alpha(im, m, (x - m.width / 2, y - m.height / 2), a if i == shown_n - 1 else 0.55 + 0.45 * a * 0)
        lab = _cache.setdefault(("daylab", i), text_layer(f"第 {1 + ages[i] - ages[0]} 天", font(36), (230, 235, 245)))
        paste_alpha(im, lab, (x - lab.width / 2, y + 48), a)          # 用透明度淡入（從黑色淡入會在天空上變成黑字）
    if shown_n < len(ages) and t < start:
        ctext(d, W / 2, 330, "？", font(160), (255, 209, 102))
    fin = start + (len(ages) - 1) * gap + 0.4
    a = prog(t, fin, 0.7)
    if a > 0:
        d = ImageDraw.Draw(im)
        rs = p.get("result", ["同一時間觀察：", "月亮每天往東移約 12°，亮面越來越大"])
        f = font(44); wdt = max(tw(d, x, f)[0] for x in rs)
        d.rounded_rectangle([120, 280, 180 + wdt, 300 + 66 * len(rs)], radius=24, fill=(255, 209, 102))
        for k, x in enumerate(rs): d.text((150, 296 + k * 62), x, font=f, fill=INK)
        ax = pts[-1][0] - 20
        C.arrow(d, (pts[0][0] - 60, 700), (ax - 60, 700), GOLD, w=8, head=26)
        ctext(d, (pts[0][0] + ax) / 2 - 60, 632, "向東移動", font(40), GOLD)
    return im


# ======================= 3. Kahoot 式即時作答分布 =======================
KCOL = [(226, 27, 60), (19, 104, 206), (216, 158, 0), (38, 137, 12)]


def _shape(d, i, cx, cy, r, fill=WHITE):
    if i == 0: d.polygon([(cx, cy - r), (cx + r, cy + r * .8), (cx - r, cy + r * .8)], fill=fill)
    elif i == 1: d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=fill)
    elif i == 2: d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    else: d.rectangle([cx - r * .85, cy - r * .85, cx + r * .85, cy + r * .85], fill=fill)


def a_poll(p, t, dur, ev):
    im = dark_bg("poll"); d = ImageDraw.Draw(im)
    title_bar(im, d, p.get("title", "課前診斷"), prog(t, 0, 0.6))
    opts = p.get("options", ["向東移動", "向西移動", "位置不變", "不確定"]); cnt = p.get("counts", [9, 8, 7, 4])
    mx = max(cnt); bw, gap = 190, 70; x0 = 170; base = 720
    for i, (o, c) in enumerate(zip(opts, cnt)):
        a = back((t - 0.4 - i * 0.18) / 0.9)
        h = 380 * c / mx * a
        x = x0 + i * (bw + gap)
        d.rounded_rectangle([x, base - h, x + bw, base], radius=10, fill=KCOL[i])
        if a > 0.3: ctext(d, x + bw / 2, base - h - 64, str(round(c * clamp(a))), font(52), WHITE)
        d.rounded_rectangle([x, base + 20, x + bw, base + 110], radius=12, fill=KCOL[i])
        _shape(d, i, x + 34, base + 65, 18)
        d.text((x + 62, base + 42), o, font=C.fit(d, o, 40, bw - 70), fill=WHITE)
    ctext(d, x0 + 2 * (bw + gap) - gap / 2, base + 150, "全班 28 人作答（不顯示姓名）", font(34, False), (170, 190, 215))
    # 追問：為什麼？
    e1 = ev_at(ev, 0, dur * 0.35)
    reasons = p.get("reasons", ["「月亮會跟著我走」", "「每天都在同一個地方」", "「我看過它慢慢移動」"])
    for i, r in enumerate(reasons):
        a = back((t - e1 - i * 0.45) / 0.6)
        if a <= 0: continue
        bx, by = 1250, 300 + i * 150
        s = 0.6 + 0.4 * a
        d.rounded_rectangle([bx, by, bx + 560 * s, by + 110 * s], radius=int(40 * s), fill=(255, 255, 255))
        d.polygon([(bx + 20, by + 80 * s), (bx - 30, by + 120 * s), (bx + 70, by + 100 * s)], fill=WHITE)
        d.text((bx + 30, by + 26 * s), r, font=font(int(44 * s)), fill=INK)
    if t > e1:
        ctext(d, 1530, 200, "他為什麼這樣想？", font(56), GOLD)
    # 即時溫度計
    e2 = ev_at(ev, 1, dur * 0.7)
    a = clamp((t - e2) / 0.36)                        # 先淡出舊版面、再淡入新版面（不同時疊在一起）
    if a > 0:
        im2 = dark_bg("poll").copy(); d2 = ImageDraw.Draw(im2)
        tx = 1500
        d2.rounded_rectangle([tx - 38, 250, tx + 38, 820], radius=38, fill=(230, 236, 245))
        d2.ellipse([tx - 80, 780, tx + 80, 940], fill=(230, 236, 245))
        lvl = ease((t - e2 - 0.3) / 1.8)
        top = 800 - 500 * 0.78 * lvl
        d2.rounded_rectangle([tx - 22, top, tx + 22, 850], radius=22, fill=RED); d2.ellipse([tx - 62, 798, tx + 62, 922], fill=RED)
        for k in range(6): d2.line([(tx + 50, 300 + k * 90), (tx + 80, 300 + k * 90)], fill=(170, 190, 215), width=4)
        for i, (s, y) in enumerate([("直覺想法", 420), ("迷思概念", 560), ("下一步追問", 700)]):
            aa = prog(t, e2 + 0.8 + i * 0.5, 0.5)
            d2.text((tx - 420, y - 30 + 10 * (1 - aa)), s, font=font(56), fill=tuple(int(v * aa) for v in WHITE))
        ctext(d2, 720, 170, "Kahoot＝課堂的即時溫度計", font(64), GOLD)
        # 左半邊縮小保留長條圖
        small = im.crop((100, 260, 1200, 900)).resize((770, 448), Image.LANCZOS)
        im2.paste(small, (120, 330))
        bg = dark_bg("poll")
        im = Image.blend(im, bg, a * 2) if a < 0.5 else Image.blend(bg, im2, (a - 0.5) * 2)
    return im


# ======================= 4. Padlet 式證據牆 =======================
def a_wall(p, t, dur, ev):
    im = dark_bg("wall", (60, 90, 110)); d = ImageDraw.Draw(im)
    title_bar(im, d, p.get("title", "全班共享的探究證據牆"), prog(t, 0, 0.6), 140)
    groups = 6; cw, gx, x0, y0 = 250, 28, 150, 250
    for g in range(groups):
        x = x0 + g * (cw + gx)
        d.rounded_rectangle([x, y0, x + cw, y0 + 64], radius=14, fill=(255, 255, 255))
        ctext(d, x + cw / 2, y0 + 10, f"第 {g + 1} 組", font(38), INK)
    if "wallcards" not in _cache:
        rnd = random.Random(7); cards = []
        imgs = p.get("images", [])
        for g in range(groups):
            for k in range(3):
                kind = ["photo", "data", "note"][(g + k) % 3]
                c = Image.new("RGBA", (cw, 190), (0, 0, 0, 0)); cd = ImageDraw.Draw(c)
                cd.rounded_rectangle([0, 0, cw - 1, 189], radius=16, fill=(250, 251, 253))
                if kind == "photo" and imgs:
                    ph = Image.open(imgs[(g * 3 + k) % len(imgs)]).convert("RGB")
                    ph = ph.resize((cw - 20, int((cw - 20) * ph.height / ph.width)))
                    ph = ph.crop((0, 0, cw - 20, 130)); c.paste(ph, (10, 10))
                    cd.text((14, 146), "實驗照片", font=font(28, False), fill=GRAY)
                elif kind == "data":
                    vals = [rnd.uniform(3, 12) for _ in range(5)]
                    for i, v in enumerate(vals):
                        cd.rectangle([22 + i * 42, 140 - v * 9, 50 + i * 42, 140], fill=C.PALETTE[g % 6])
                    cd.text((14, 146), f"高度 {vals[-1]:.1f} cm", font=font(28, False), fill=GRAY)
                else:
                    cd.text((16, 20), "我們發現", font=font(34), fill=INK)
                    for j in range(3): cd.rounded_rectangle([16, 80 + j * 30, cw - 30 - rnd.randrange(0, 70), 94 + j * 30], radius=7, fill=LGRAY)
                cards.append((g, k, c, rnd.uniform(-1, 1), rnd.uniform(0, 1)))
        _cache["wallcards"] = cards
    cards = _cache["wallcards"]
    span = max(1.0, dur - 1.8)
    order = sorted(range(len(cards)), key=lambda i: cards[i][4])
    for rank, i in enumerate(order):
        g, k, c, jx, _ = cards[i]
        e = 0.5 + rank * span / len(cards)
        a = back((t - e) / 0.6)
        if a <= 0: continue
        x = x0 + g * (cw + gx); y = y0 + 90 + k * 214
        sy = y + 120 * (1 - clamp(a)) ; sx = x + jx * 40 * (1 - clamp(a))
        cc = c if a >= 1 else c.resize((max(1, int(cw * (0.6 + 0.4 * min(a, 1.05)))), max(1, int(190 * (0.6 + 0.4 * min(a, 1.05))))))
        paste_alpha(im, cc, (sx + (cw - cc.width) / 2, sy + (190 - cc.height) / 2), clamp(a * 1.5))
    return im


# ======================= 5. 各組數據比較 =======================
def a_compare(p, t, dur, ev):
    im = dark_bg("cmp"); d = ImageDraw.Draw(im)
    title_bar(im, d, p.get("title", "為什麼各組的數據不一樣？"), prog(t, 0, 0.6), 140)
    vals = p.get("values", [12.4, 8.1, 12.9, 6.3, 12.1, 11.8]); unit = p.get("unit", "cm")
    x0, base, bw, gap = 220, 830, 130, 70
    d.line([(x0 - 40, base), (x0 + 6 * (bw + gap), base)], fill=(170, 190, 215), width=4)
    d.text((x0 - 40, 230), p.get("ylabel", "第 7 天植物高度（cm）"), font=font(36, False), fill=(170, 190, 215))
    odd = p.get("odd", [1, 3])
    for i, v in enumerate(vals):
        a = back((t - 0.3 - i * 0.15) / 0.8); h = v / 14 * 480 * a
        x = x0 + i * (bw + gap)
        c = (RED if i in odd and t > ev_at(ev, 0, 2.5) else BLUE)
        d.rounded_rectangle([x, base - h, x + bw, base], radius=10, fill=c)
        if a > .5: ctext(d, x + bw / 2, base - h - 56, f"{v:.1f}", font(42), WHITE)
        ctext(d, x + bw / 2, base + 16, f"第{i + 1}組", font(36), (200, 210, 230))
        if i in odd and t > ev_at(ev, 0, 2.5):
            pulse = 1 + 0.12 * math.sin((t - ev_at(ev, 0, 2.5)) * 6)
            ctext(d, x + bw / 2, base - h - 170, "？", font(int(90 * pulse)), GOLD)
    chips = p.get("chips", ["材料不同？", "測量方式不同？", "控制變因出了問題？"])
    for i, s in enumerate(chips):
        e = ev_at(ev, i + 1, ev_at(ev, 0, 2.5) + 1 + i * 1.2)
        a = back((t - e) / 0.5)
        if a <= 0: continue
        y = 330 + i * 170; x = 1380
        f = font(44); wdt = tw(d, s, f)[0]
        d.rounded_rectangle([x - 20 * a, y, x + wdt + 60, y + 110], radius=55, fill=[ORANGE, PURPLE, GREEN][i])
        d.text((x + 30 - 20 * (1 - a), y + 26), s, font=f, fill=WHITE)
    return im


# ======================= 6. Wordwall 式分類：水生植物 =======================
BINS = [("挺水植物", "emergent"), ("浮葉植物", "floating_leaf"), ("漂浮植物", "floating"), ("沉水植物", "submerged")]


def _bin_icon(d, kind, x, y, w, h):
    """水生植物生活型示意：水面線＋植物位置（依生活型正確擺放）"""
    wl = y + h * 0.35; bot = y + h - 8
    d.rectangle([x, wl, x + w, bot], fill=(120, 190, 230)); d.rectangle([x, bot, x + w, y + h], fill=(120, 90, 60))
    cx = x + w / 2; G = (40, 140, 60)
    if kind == "emergent":        # 根在底泥，莖葉伸出水面
        d.line([(cx, bot), (cx, y + 10)], fill=G, width=6); d.ellipse([cx - 34, y + 2, cx + 34, y + 30], fill=G)
    elif kind == "floating_leaf":  # 根在底泥，葉片浮在水面
        d.line([(cx, bot), (cx - 10, wl)], fill=G, width=4); d.ellipse([cx - 44, wl - 10, cx + 30, wl + 6], fill=G)
    elif kind == "floating":       # 整株漂在水面，根懸在水中、不著底
        d.ellipse([cx - 40, wl - 16, cx + 40, wl + 6], fill=G)
        for k in (-18, 0, 18): d.line([(cx + k, wl + 4), (cx + k, wl + (bot - wl) * 0.55)], fill=(220, 230, 240), width=3)
    else:                           # 整株在水面下
        d.line([(cx, bot), (cx, wl + 14)], fill=G, width=5)
        for k in range(4): d.line([(cx, bot - 12 - k * 16), (cx + (18 if k % 2 else -18), bot - 24 - k * 16)], fill=G, width=4)


def a_sort(p, t, dur, ev):
    im = dark_bg("sort", (40, 100, 110)); d = ImageDraw.Draw(im)
    title_bar(im, d, p.get("title", "水生植物分類：依生長位置"), prog(t, 0, 0.6), 140)
    items = p.get("items", [["荷花", 0], ["睡蓮", 1], ["布袋蓮", 2], ["金魚藻", 3], ["香蒲", 0], ["台灣萍蓬草", 1], ["浮萍", 2], ["水蘊草", 3]])
    bw, bx0, by = 380, 150, 560
    for i, (name, kind) in enumerate(BINS):
        x = bx0 + i * (bw + 40)
        d.rounded_rectangle([x, by, x + bw, 950], radius=22, fill=(245, 248, 252))
        d.rounded_rectangle([x, by, x + bw, by + 80], radius=22, fill=C.PALETTE[i]); d.rectangle([x, by + 50, x + bw, by + 80], fill=C.PALETTE[i])
        ctext(d, x + bw / 2, by + 12, name, font(48), WHITE)
        _bin_icon(d, kind, x + 30, by + 100, bw - 60, 120)
    placed = [0] * 4
    start = 0.8; step = max(0.55, (dur - start - 1.0) / len(items))
    flying = [j for j in range(len(items)) if 0 < ease((t - start - j * step) / (step * 0.8)) < 1]
    order = [j for j in range(len(items)) if j not in flying] + flying
    slot = {}
    for j, (name, b) in enumerate(items):               # 先算好每張卡落點（依原順序）
        if ease((t - start - j * step) / (step * 0.8)) >= 1 or j in flying: slot[j] = placed[b]; placed[b] += 1
    placed = [0] * 4
    for j in order:
        name, b = items[j]
        e = start + j * step; a = ease((t - e) / (step * 0.8))
        sx, sy = 240 + (j % 4) * 400, 250 + (j // 4) * 120
        sl = slot.get(j, 0)
        tx, ty = bx0 + b * (bw + 40) + 40 + (sl % 2) * 160, by + 250 + (sl // 2) * 80
        x = sx + (tx - sx) * a; y = sy + (ty - sy) * a - math.sin(a * math.pi) * 120
        f = font(40 if a < 1 else 34); wdt = tw(d, name, f)[0] + 40
        d.rounded_rectangle([x, y, x + wdt, y + 64], radius=16, fill=WHITE if a < 1 else (230, 245, 235), outline=C.PALETTE[b] if a >= 1 else LGRAY, width=4)
        d.text((x + 20, y + 10), name, font=f, fill=INK)
        if 0 < a < 1:                                    # 拖曳中的手指游標
            d.ellipse([x + wdt - 20, y + 40, x + wdt + 14, y + 74], fill=(255, 255, 255), outline=INK, width=3)
        if a >= 1 and t - e - step * 0.8 < 0.5: C.mark(d, x + wdt + 5, y + 5, 22, True)
    return im


# ======================= 7. 實驗步驟排序＋變因配對 =======================
def a_variables(p, t, dur, ev):
    im = dark_bg("var"); d = ImageDraw.Draw(im)
    e0 = ev_at(ev, 0, dur * 0.45)
    steps = p.get("steps_text", ["準備三盆相同的植物", "分別照光 0、4、8 小時", "每天澆相同的水量", "七天後測量植物高度"])
    shuffled = p.get("shuffled", [2, 0, 3, 1])
    a_out = prog(t, e0, 0.5)
    if a_out < 1:
        title_bar(im, d, "重新排列實驗步驟", prog(t, 0, 0.6) * (1 - a_out), 140)
        # 所有卡片同時移動：往上的從右側繞、往下的從左側繞、不動的留在原位 → 卡片不會互相重疊
        k = ease((t - 0.9) / max(0.8, e0 - 1.6))
        cw = 760; x0 = (W - cw) / 2
        for idx, s in enumerate(steps):
            y_from = 280 + shuffled.index(idx) * 150; y_to = 280 + idx * 150
            side = 0 if y_to == y_from else (1 if y_to < y_from else -1)
            ka, kb, kc = ease(k / 0.3), ease((k - 0.3) / 0.4), ease((k - 0.7) / 0.3)   # 側移 → 上下 → 歸位
            y = y_from + (y_to - y_from) * kb
            x = x0 + side * 430 * (ka - kc)
            done = k >= 1
            d.rounded_rectangle([x, y, x + cw, y + 120], radius=24, fill=(250, 251, 253), outline=GREEN if done else LGRAY, width=5)
            d.ellipse([x + 24, y + 24, x + 96, y + 96], fill=GREEN if done else GRAY)
            ctext(d, x + 60, y + 30, str(idx + 1) if done else "?", font(44), WHITE)
            d.text((x + 130, y + 30), s, font=C.fit(d, s, 52, cw - 160), fill=INK)
        if a_out > 0: im = Image.blend(im, dark_bg("var"), a_out)
    if t >= e0:
        d = ImageDraw.Draw(im)
        title_bar(im, d, p.get("title", "光照時間會影響植物長高嗎？"), prog(t, e0, 0.6), 140)
        slots = [("操縱變因", BLUE, "我改變的"), ("控制變因", GRAY, "保持相同的"), ("應變變因", ORANGE, "我測量的")]
        for i, (s, c, sub) in enumerate(slots):
            x = 150 + i * 560
            a = prog(t, e0 + 0.2 + i * 0.15, 0.5)
            d.rounded_rectangle([x, 300, x + 500, 930], radius=26, fill=tuple(int(245 * a + 14 * (1 - a)) for _ in range(3)))
            d.rounded_rectangle([x, 300, x + 500, 400], radius=26, fill=c); d.rectangle([x, 370, x + 500, 400], fill=c)
            ctext(d, x + 250, 312, s, font(56), WHITE); ctext(d, x + 250, 420, sub, font(38, False), GRAY)
        cards = p.get("cards", [["光照時間", 0], ["水量", 1], ["土壤", 1], ["溫度", 1], ["植物長高多少", 2]])
        place = [0, 0, 0]; st = max(0.45, (dur - e0 - 1.2) / len(cards))
        for j, (s, b) in enumerate(cards):
            e = e0 + 0.9 + j * st; a = ease((t - e) / (st * 0.8))
            if t < e: continue
            tx, ty = 150 + b * 560 + 50, 500 + place[b] * 105
            sx, sy = W / 2 - 150, 980
            x = sx + (tx - sx) * a; y = sy + (ty - sy) * a
            d.rounded_rectangle([x, y, x + 400, y + 86], radius=18, fill=WHITE, outline=[BLUE, GRAY, ORANGE][b], width=5)
            ctext(d, x + 200, y + 14, s, font(48), INK)
            place[b] += 1
    return im


# ======================= 8. Wayground 式班級儀表板 =======================
def a_dashboard(p, t, dur, ev):
    im = dark_bg("dash"); d = ImageDraw.Draw(im)
    title_bar(im, d, p.get("title", "班級作答情形：看見下一步"), prog(t, 0, 0.6), 140)
    cols = p.get("concepts", ["月相變化", "東升西落", "觀察方法", "資料判讀", "證據推論"])
    n = 18; rnd = random.Random(11)
    if "dash" not in _cache:
        lv = []
        for s in range(n):
            base = 0.3 + rnd.random() * 0.7
            lv.append([clamp(base + rnd.uniform(-.35, .35) - (0.35 if c == 1 else 0)) for c in range(len(cols))])
        _cache["dash"] = lv
    lv = _cache["dash"]
    e0, e1, e2 = ev_at(ev, 0, dur * .3), ev_at(ev, 1, dur * .5), ev_at(ev, 2, dur * .7)
    x0, y0, cw, rh = 330, 300, 170, 34
    mv = prog(t, e2, 1.2)
    for c, s in enumerate(cols): ctext(d, x0 + c * cw + cw / 2, y0 - 60, s, font(34), tuple(int(v * (1 - mv)) for v in WHITE))
    group = lambda s: 0 if sum(lv[s]) / len(cols) < .38 else (2 if sum(lv[s]) / len(cols) > .66 else 1)
    gcol = [RED, GOLD, GREEN]; gname = ["補強任務", "練習任務", "挑戰任務"]
    for s in range(n):
        y = y0 + s * rh
        for c in range(len(cols)):
            a = prog(t, 0.3 + (s * len(cols) + c) * 0.012, 0.3)
            v = lv[s][c]; colr = RED if v < .4 else (GOLD if v < .7 else GREEN)
            colr = tuple(int(30 + (q - 30) * a) for q in colr)
            fade = clamp(1 - mv * 2.5)                     # 學生開始分流時，熱度圖先淡出
            if fade > 0: d.rectangle([x0 + c * cw + 4, y + 3, x0 + (c + 1) * cw - 4, y + rh - 3], fill=tuple(int(14 + (q - 14) * fade) for q in colr))
        if mv < 0.4: d.text((x0 - 120, y - 2), f"{s + 1:02d} 號", font=font(26, False), fill=tuple(int(v * clamp(1 - mv * 2.5)) for v in (170, 190, 215)))
    if t > e0 and mv < 0.4:                                 # 需要重新說明的概念
        weak = min(range(len(cols)), key=lambda c: sum(lv[s][c] for s in range(n)))
        pul = 4 + 2 * math.sin((t - e0) * 6)
        d.rounded_rectangle([x0 + weak * cw - 6, y0 - 70, x0 + (weak + 1) * cw + 6, y0 + n * rh + 6], radius=10, outline=GOLD, width=int(pul))
        ctext(d, x0 + weak * cw + cw / 2, y0 + n * rh + 20, "需要重新說明", font(38), GOLD)
    if t > e1 and mv < 0.4:
        for s in range(n):
            if group(s) == 0: d.rectangle([x0 - 130, y0 + s * rh + 2, x0 - 10, y0 + (s + 1) * rh - 2], outline=RED, width=3)
    if mv > 0:                                               # 學生分流到差異化任務
        gx = [1260, 1260, 1260]; gy = [250, 490, 730]
        for g in range(3):
            d.rounded_rectangle([gx[g], gy[g], gx[g] + 520, gy[g] + 200], radius=24, fill=(245, 248, 252))
            d.rounded_rectangle([gx[g], gy[g], gx[g] + 520, gy[g] + 64], radius=24, fill=gcol[g]); d.rectangle([gx[g], gy[g] + 40, gx[g] + 520, gy[g] + 64], fill=gcol[g])
            ctext(d, gx[g] + 260, gy[g] + 6, gname[g], font(42), WHITE if g != 1 else INK)
        cnt = [0, 0, 0]
        for s in range(n):
            g = group(s); k = cnt[g]; cnt[g] += 1
            sx, sy = x0 - 120, y0 + s * rh
            tx, ty = gx[g] + 30 + (k % 6) * 80, gy[g] + 84 + (k // 6) * 50
            a = ease((mv * 1.4) - s * 0.02)
            x, y = sx + (tx - sx) * a, sy + (ty - sy) * a
            d.rounded_rectangle([x, y, x + 70, y + 38], radius=12, fill=gcol[g])
            ctext(d, x + 35, y + 2, f"{s + 1}", font(26), WHITE if g != 1 else INK)
        if mv >= 1:                                       # 熱度圖完全消失、學生都到位後才出現結論字
            aa = prog(t, e2 + 1.25, 0.5)
            ctext(d, 640, 520, "同一個概念", font(64), tuple(int(v * aa) for v in WHITE))
            ctext(d, 640, 620, "不同的下一步", font(64), tuple(int(v * aa) for v in GOLD))
    return im


# ======================= 9. 探究循環 =======================
def a_cycle(p, t, dur, ev):
    im = dark_bg("cycle", (30, 80, 130)); d = ImageDraw.Draw(im)
    title_bar(im, d, p.get("title", "工具不同，服務的是同一段探究歷程"), prog(t, 0, 0.6), 140)
    steps = p.get("boxes", ["發現問題", "提出預測", "動手探究", "蒐集證據", "分享解釋", "修正想法"])
    cx, cy, R = W / 2, 600, 280
    n = len(steps); e0 = ev_at(ev, 0, 0.5)
    sweep = ease((t - e0) / max(1.5, min(4.5, dur - e0 - 1)))
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(60, 90, 130), width=10)
    if sweep > 0: d.arc([cx - R, cy - R, cx + R, cy + R], -90, -90 + 360 * sweep, fill=GOLD, width=12)
    for i, s in enumerate(steps):
        ang = -math.pi / 2 + 2 * math.pi * i / n
        x, y = cx + R * math.cos(ang), cy + R * math.sin(ang)
        lit = sweep * n >= i + 0.01 or i == 0 and sweep > 0
        a = back((t - 0.2 - i * 0.12) / 0.6)
        r = 92 * clamp(a, 0, 1.1)
        c = C.PALETTE[i % 6] if lit else (40, 60, 95)
        d.ellipse([x - r, y - r, x + r, y + r], fill=c, outline=WHITE if lit else (80, 110, 150), width=4)
        if a > .5: mtext(d, x, y, s[:2] + "\n" + s[2:], font(38), WHITE)
    tools = p.get("tools", [["Kahoot", 0.5, PURPLE], ["Padlet", 2.5, CYAN_D], ["Wordwall", 4, ORANGE], ["Wayground", 5, GREEN]])
    for j, (name, pos, c) in enumerate(tools):
        e = ev_at(ev, 1, e0 + 1.5) + j * 0.35
        a = back((t - e) / 0.6)
        if a <= 0: continue
        ang = -math.pi / 2 + 2 * math.pi * pos / n
        x, y = cx + (R + 300) * math.cos(ang), cy + (R + 70) * math.sin(ang)
        f = font(44); wdt = tw(d, name, f)[0] + 50
        s = clamp(a, 0, 1.1)
        d.rounded_rectangle([x - wdt / 2 * s, y - 36 * s, x + wdt / 2 * s, y + 36 * s], radius=int(36 * s), fill=c if not isinstance(c, str) else C.col(c))
        if a > .6: ctext(d, x, y - 28, name, f, WHITE)
    a = prog(t, dur - 1.6, 0.8)
    if a > 0: ctext(d, cx, cy - 40, "探究", font(90), tuple(int(v * a) for v in GOLD))
    return im


ANIMS = {"title_reveal": a_title_reveal, "moon": a_moon, "poll": a_poll, "wall": a_wall, "compare": a_compare,
         "sort": a_sort, "variables": a_variables, "dashboard": a_dashboard, "cycle": a_cycle}


def frame(p, t, dur, ev):
    return ANIMS[p["anim"]](p, t, dur, ev)
