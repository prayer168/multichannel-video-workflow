"""通用圖卡範本庫：依「畫面規格.yaml」的一個畫面（dict）畫出 1920×1080 圖卡
用法（由 build.py 呼叫）：render(spec_dict, out_png)
- 每個畫面用 type 指定版型，其餘欄位是版型參數；顏色可寫 blue / orange / green / cyan / gold / gray / navy / purple / red
- show：逐步出現用，只畫前 show 個項目（清單類隱藏其餘，進度類把其餘變淡）
- 規則：圖卡會做緩慢推近，所以不放熊掌徽章（避免和浮水印疊影）；右下角 260×200 留白給浮水印
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
NAVY, NAVY2 = (9, 29, 56), (20, 48, 88)
LIGHT, WHITE, INK, GRAY, LGRAY = (244, 246, 250), (255, 255, 255), (28, 36, 52), (120, 130, 148), (205, 212, 224)
DIMBG, DIMTX = (228, 232, 240), (165, 172, 188)
CYAN, CYAN_D = (62, 224, 255), (0, 150, 190)
GOLD, ORANGE, GREEN, RED, BLUE, PURPLE = (255, 209, 102), (242, 140, 40), (46, 170, 110), (220, 80, 80), (47, 111, 219), (150, 90, 200)
COLORS = dict(blue=BLUE, orange=ORANGE, green=GREEN, cyan=CYAN_D, gold=GOLD, gray=GRAY, navy=NAVY2, purple=PURPLE, red=RED, lightgray=LGRAY)
PALETTE = [BLUE, GREEN, ORANGE, CYAN_D, PURPLE, GOLD]
FB, FR, FC = "C:/Windows/Fonts/msjhbd.ttc", "C:/Windows/Fonts/msjh.ttc", "C:/Windows/Fonts/consola.ttf"
_fonts = {}


def font(size, bold=True):
    k = (int(size), bold)
    if k not in _fonts: _fonts[k] = ImageFont.truetype(FB if bold else FR, int(size))
    return _fonts[k]


def mono(size):
    k = (int(size), "mono")
    if k not in _fonts: _fonts[k] = ImageFont.truetype(FC, int(size))
    return _fonts[k]


def col(c, default=NAVY2):
    if c is None: return default
    if isinstance(c, str): return COLORS[c]
    return tuple(c)


def on_color(c):
    return INK if c in (GOLD, LGRAY, WHITE, DIMBG) else WHITE


def tw(d, s, f):
    l, t, r, b = d.textbbox((0, 0), s, font=f)
    return r - l, b - t


def ctext(d, cx, y, s, f, fill):
    w, _ = tw(d, s, f)
    d.text((cx - w / 2, y), s, font=f, fill=fill)


def mtext(d, cx, cy, s, f, fill):
    """以 (cx, cy) 為中心畫文字（可多行）"""
    lines = str(s).split("\n")
    lh = f.size * 1.3
    y = cy - lh * len(lines) / 2
    for l in lines:
        w, _ = tw(d, l, f)
        d.text((cx - w / 2, y + (lh - f.size) / 2 - f.size * 0.12), l, font=f, fill=fill)
        y += lh


def fit(d, s, size, maxw, bold=True):
    """字太長時自動縮小"""
    f = font(size, bold)
    while max(tw(d, l, f)[0] for l in str(s).split("\n")) > maxw and size > 20:
        size -= 2; f = font(size, bold)
    return f


def box(d, b, fill=WHITE, r=28, shadow=True, outline=None, ow=3):
    if shadow:
        d.rounded_rectangle([b[0] + 6, b[1] + 10, b[2] + 6, b[3] + 10], radius=r, fill=(215, 220, 230))
    d.rounded_rectangle(b, radius=r, fill=fill, outline=outline, width=ow if outline else 0)


def header(d, title, sub=None, dark=False):
    if not title: return
    d.rounded_rectangle([110, 88, 124, 158], radius=6, fill=CYAN if dark else ORANGE)
    d.text((150, 80), title, font=fit(d, title, 64, W - 330), fill=WHITE if dark else INK)
    if sub:
        d.text((152, 170), sub, font=font(36, False), fill=(170, 190, 215) if dark else GRAY)


def mark(d, cx, cy, r, ok, bg=None):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg or (GREEN if ok else RED))
    w = max(5, int(r * 0.22))
    if ok:
        d.line([(cx - r * .45, cy), (cx - r * .12, cy + r * .33), (cx + r * .5, cy - r * .35)], fill=WHITE, width=w, joint="curve")
    else:
        d.line([(cx - r * .38, cy - r * .38), (cx + r * .38, cy + r * .38)], fill=WHITE, width=w)
        d.line([(cx - r * .38, cy + r * .38), (cx + r * .38, cy - r * .38)], fill=WHITE, width=w)


def arrow(d, p0, p1, c, w=12, head=34, label=None, lf=None, lcol=None, loff=(0, -60)):
    (x0, y0), (x1, y1) = p0, p1
    a = math.atan2(y1 - y0, x1 - x0)
    d.line([(x0, y0), (x1 - head * math.cos(a) * 0.9, y1 - head * math.sin(a) * 0.9)], fill=c, width=w)
    d.polygon([(x1, y1), (x1 - head * math.cos(a) + head * .6 * math.sin(a), y1 - head * math.sin(a) - head * .6 * math.cos(a)),
               (x1 - head * math.cos(a) - head * .6 * math.sin(a), y1 - head * math.sin(a) + head * .6 * math.cos(a))], fill=c)
    if label:
        mtext(d, (x0 + x1) / 2 + loff[0], (y0 + y1) / 2 + loff[1], label, lf or font(44), lcol or c)


def dashed_rect(d, b, c, w=5, dash=24, gap=16):
    x0, y0, x1, y1 = b
    for (ax, ay, bx, by) in [(x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)]:
        L = math.hypot(bx - ax, by - ay); n = int(L // (dash + gap)) + 1
        for i in range(n):
            s, e = i * (dash + gap) / L, min(1, (i * (dash + gap) + dash) / L)
            d.line([(ax + (bx - ax) * s, ay + (by - ay) * s), (ax + (bx - ax) * e, ay + (by - ay) * e)], fill=c, width=w)


# ---------- 圖示（全部用線條與色塊畫，不用 emoji） ----------
def ic_computer(d, cx, cy, s=1.0, c=NAVY2, label=None, lcol=INK):
    w, h = 300 * s, 190 * s
    d.rounded_rectangle([cx - w / 2, cy - h / 2 - 40 * s, cx + w / 2, cy + h / 2 - 40 * s], radius=int(16 * s), fill=c)
    d.rectangle([cx - w / 2 + 16 * s, cy - h / 2 - 24 * s, cx + w / 2 - 16 * s, cy + h / 2 - 56 * s], fill=(225, 240, 255))
    d.rectangle([cx - 20 * s, cy + h / 2 - 40 * s, cx + 20 * s, cy + h / 2], fill=c)
    d.rounded_rectangle([cx - 90 * s, cy + h / 2 - 4 * s, cx + 90 * s, cy + h / 2 + 14 * s], radius=int(8 * s), fill=c)
    if label: ctext(d, cx, cy + h / 2 + 34 * s, label, font(44 * s), lcol)


def ic_laptop(d, cx, cy, s=1.0, c=NAVY2, label=None, lcol=INK):
    w, h = 280 * s, 175 * s
    d.rounded_rectangle([cx - w / 2, cy - h / 2 - 20 * s, cx + w / 2, cy + h / 2 - 20 * s], radius=int(14 * s), fill=c)
    d.rectangle([cx - w / 2 + 14 * s, cy - h / 2 - 6 * s, cx + w / 2 - 14 * s, cy + h / 2 - 34 * s], fill=(225, 240, 255))
    d.polygon([(cx - w / 2 - 30 * s, cy + h / 2 - 12 * s), (cx + w / 2 + 30 * s, cy + h / 2 - 12 * s),
               (cx + w / 2 + 10 * s, cy + h / 2 + 14 * s), (cx - w / 2 - 10 * s, cy + h / 2 + 14 * s)], fill=c)
    if label: ctext(d, cx, cy + h / 2 + 34 * s, label, font(44 * s), lcol)


def ic_cloud(d, cx, cy, s=1.0, c=CYAN_D, label=None, lcol=WHITE):
    for (dx, dy, r) in [(-95, 20, 70), (-25, -30, 95), (75, -5, 80), (120, 35, 55)]:
        d.ellipse([cx + (dx - r) * s, cy + (dy - r) * s, cx + (dx + r) * s, cy + (dy + r) * s], fill=c)
    d.rounded_rectangle([cx - 165 * s, cy + 10 * s, cx + 175 * s, cy + 90 * s], radius=int(40 * s), fill=c)
    if label: mtext(d, cx + 5 * s, cy + 25 * s, label, font(50 * s), lcol)


def ic_file(d, cx, cy, s=1.0, name=None, fs=34):
    w, h = 150 * s, 190 * s
    x0, y0 = cx - w / 2, cy - h / 2
    d.polygon([(x0, y0), (x0 + w - 40 * s, y0), (x0 + w, y0 + 40 * s), (x0 + w, y0 + h), (x0, y0 + h)], fill=WHITE, outline=LGRAY)
    d.polygon([(x0 + w - 40 * s, y0), (x0 + w - 40 * s, y0 + 40 * s), (x0 + w, y0 + 40 * s)], fill=LGRAY)
    for k in range(3):
        d.line([(x0 + 24 * s, y0 + (80 + k * 30) * s), (x0 + w - 24 * s, y0 + (80 + k * 30) * s)], fill=LGRAY, width=max(2, int(5 * s)))
    if name: ctext(d, cx, y0 + h + 14 * s, name, mono(fs * s) if "." in name else font(fs * s), INK)


def ic_folder(d, cx, cy, s=1.0, c=GOLD, label=None, lcol=INK):
    w, h = 240 * s, 170 * s
    x0, y0 = cx - w / 2, cy - h / 2
    d.rounded_rectangle([x0, y0, x0 + w * .45, y0 + 40 * s], radius=int(12 * s), fill=c)
    d.rounded_rectangle([x0, y0 + 24 * s, x0 + w, y0 + h], radius=int(16 * s), fill=c)
    if label: mtext(d, cx, y0 + h / 2 + 24 * s, label, font(38 * s), lcol)


def ic_person(d, cx, cy, s=1.0, c=BLUE, mood="smile"):
    r = 46 * s
    d.pieslice([cx - 95 * s, cy + 20 * s, cx + 95 * s, cy + 210 * s], 180, 360, fill=c)
    d.ellipse([cx - r, cy - r - 30 * s, cx + r, cy + r - 30 * s], fill=(255, 224, 196))
    ey = cy - 36 * s
    d.ellipse([cx - 20 * s, ey - 5 * s, cx - 10 * s, ey + 5 * s], fill=INK)
    d.ellipse([cx + 10 * s, ey - 5 * s, cx + 20 * s, ey + 5 * s], fill=INK)
    if mood == "smile":
        d.arc([cx - 20 * s, ey - 6 * s, cx + 20 * s, ey + 26 * s], 20, 160, fill=INK, width=max(2, int(4 * s)))
    else:
        d.arc([cx - 18 * s, ey + 16 * s, cx + 18 * s, ey + 40 * s], 200, 340, fill=INK, width=max(2, int(4 * s)))


def ic_robot(d, cx, cy, s=1.0, c=ORANGE):
    d.line([(cx, cy - 110 * s), (cx, cy - 75 * s)], fill=c, width=int(8 * s))
    d.ellipse([cx - 14 * s, cy - 128 * s, cx + 14 * s, cy - 100 * s], fill=c)
    d.rounded_rectangle([cx - 90 * s, cy - 75 * s, cx + 90 * s, cy + 55 * s], radius=int(30 * s), fill=c)
    d.rounded_rectangle([cx - 66 * s, cy - 50 * s, cx + 66 * s, cy + 30 * s], radius=int(20 * s), fill=WHITE)
    for ex in (-30, 30):
        d.ellipse([cx + (ex - 12) * s, cy - 22 * s, cx + (ex + 12) * s, cy + 2 * s], fill=INK)
    d.rounded_rectangle([cx - 70 * s, cy + 65 * s, cx + 70 * s, cy + 140 * s], radius=int(20 * s), fill=c)


def ic_shield(d, cx, cy, s=1.0, c=GREEN):
    d.polygon([(cx, cy - 130 * s), (cx + 110 * s, cy - 90 * s), (cx + 100 * s, cy + 20 * s), (cx, cy + 130 * s),
               (cx - 100 * s, cy + 20 * s), (cx - 110 * s, cy - 90 * s)], fill=c)
    mark(d, cx, cy - 5 * s, 56 * s, True, bg=c)


def ic_lock(d, cx, cy, s=1.0, c=ORANGE):
    d.arc([cx - 30 * s, cy - 70 * s, cx + 30 * s, cy - 10 * s], 180, 360, fill=c, width=int(12 * s))
    for x in (cx - 30 * s, cx + 30 * s):
        d.line([(x, cy - 40 * s), (x, cy - 12 * s)], fill=c, width=int(12 * s))
    d.rounded_rectangle([cx - 50 * s, cy - 18 * s, cx + 50 * s, cy + 55 * s], radius=int(12 * s), fill=c)


def icon(d, kind, cx, cy, s=1.0, label=None, lcol=INK):
    {"computer": lambda: ic_computer(d, cx, cy, s, label=label, lcol=lcol),
     "laptop": lambda: ic_laptop(d, cx, cy, s, label=label, lcol=lcol),
     "cloud": lambda: ic_cloud(d, cx, cy, s, label=label),
     "person": lambda: ic_person(d, cx, cy, s),
     "robot": lambda: ic_robot(d, cx, cy, s),
     "shield": lambda: ic_shield(d, cx, cy, s)}[kind]()


def node(d, cx, cy, r, c, label=None, lcol=WHITE, f=None):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    if label: mtext(d, cx, cy, label, f or font(r * .9), lcol)


def term_card(d, t, cx=W / 2, y=820):
    """術語卡：t = [英文, 白話]"""
    en, zh = t
    f1, f2 = font(64), font(44, False)
    w = max(tw(d, en, f1)[0], tw(d, zh, f2)[0]) + 140
    box(d, [cx - w / 2, y, cx + w / 2, y + 190], outline=ORANGE, ow=4)
    ctext(d, cx, y + 26, en, f1, NAVY)
    ctext(d, cx, y + 116, zh, f2, GRAY)


def pill(d, cx, cy, s, c, f=None, fcol=None, pad=46, h=110):
    f = f or font(52)
    w = tw(d, s, f)[0] + pad * 2
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=int(h / 2), fill=c)
    mtext(d, cx, cy, s, f, fcol or on_color(c))
    return w


def flow_row(d, steps, y, cols=None, h=120, fs=44, x0=150, x1=W - 150, gap=56, acol=GRAY, lit=None):
    """一列流程；lit＝亮起的步數（其餘變淡）"""
    n = len(steps)
    f = font(fs)
    widths = [max(tw(d, x, f)[0] for x in s.split("\n")) + 60 for s in steps]
    scale = min(1, (x1 - x0 - gap * (n - 1)) / sum(widths))
    widths = [w * scale for w in widths]
    x = x0 + ((x1 - x0) - sum(widths) - gap * (n - 1)) / 2
    for i, s in enumerate(steps):
        on = lit is None or i < lit
        c = (cols[i] if cols else NAVY2) if on else DIMBG
        d.rounded_rectangle([x, y, x + widths[i], y + h], radius=24, fill=c)
        mtext(d, x + widths[i] / 2, y + h / 2, s, font(fs * min(1, scale + .12)), on_color(c) if on else DIMTX)
        if i < n - 1:
            arrow(d, (x + widths[i] + 8, y + h / 2), (x + widths[i] + gap - 6, y + h / 2), acol if on else LGRAY, w=7, head=20)
        x += widths[i] + gap


def cols_of(p, n, key="colors"):
    cs = p.get(key)
    return [col(c) for c in cs] if cs else [PALETTE[i % len(PALETTE)] for i in range(n)]


def shown(p, n):
    s = p.get("show")
    return n if s is None else max(0, min(n, int(s)))


# ======================= 版型 =======================
def t_title(im, d, p):
    ctext(d, W / 2, 300, p.get("kicker", ""), font(80), CYAN)
    ctext(d, W / 2, 410, p["title"], fit(d, p["title"], 200, W - 200), WHITE)
    if p.get("sub"): ctext(d, W / 2, 690, p["sub"], font(46, False), (185, 200, 225))


def t_statement(im, d, p):
    lines, hl, dark = p["lines"], set(p.get("hl", [])), p.get("dark", True)
    y0 = H / 2 - len(lines) * 70 - (40 if p.get("sub") else 0)
    for i, l in enumerate(lines):
        c = (GOLD if dark else ORANGE) if i in hl else (WHITE if dark else INK)
        ctext(d, W / 2, y0 + i * 140, l, fit(d, l, 92, W - 200), c)
    if p.get("sub"): ctext(d, W / 2, y0 + len(lines) * 140 + 40, p["sub"], font(44, False), (175, 195, 220) if dark else GRAY)


def t_word(im, d, p):
    if p.get("kicker"): ctext(d, W / 2, 250, p["kicker"], font(56), CYAN)
    ctext(d, W / 2, 360, p["word"], fit(d, p["word"], 200, W - 200), WHITE)
    if p.get("sub"):
        f = font(80)
        ctext(d, W / 2, 620, p["sub"], f, (175, 195, 220) if p.get("strike") else GOLD)
        if p.get("strike"):
            w = tw(d, p["sub"], f)[0]
            d.line([(W / 2 - w / 2 - 20, 675), (W / 2 + w / 2 + 20, 675)], fill=RED, width=14)
    if p.get("note"): ctext(d, W / 2, 780, p["note"], font(56), GOLD)


def t_chapter(im, d, p):
    lv, total = p.get("level", 1), p.get("total", 3)
    ctext(d, W / 2, 330, p.get("label", f"第{'一二三四五'[lv - 1]}層"), font(52), CYAN)
    ctext(d, W / 2, 430, p["title"], font(120), WHITE)
    if p.get("sub"): ctext(d, W / 2, 630, p["sub"], font(46, False), (175, 195, 220))
    for i in range(total):
        x = W / 2 - total * 115 + i * 230
        d.rounded_rectangle([x + 15, 760, x + 215, 790], radius=15, fill=GOLD if i == lv - 1 else NAVY2)


def t_check(im, d, p):
    mark(d, W / 2, 380, 110, True)
    ctext(d, W / 2, 560, p["title"], font(110), WHITE)
    if p.get("sub"): ctext(d, W / 2, 730, p["sub"], font(48, False), CYAN)


def t_bubbles(im, d, p):
    items = p["items"]; n = shown(p, len(items))
    ic_person(d, W / 2, 560, 1.6, mood=p.get("mood", "confused"))
    d.text((W / 2 + 70, 250), "?", font=font(170), fill=ORANGE)
    pos = [(420, 300), (1480, 300), (330, 560), (1590, 560), (470, 820), (1440, 820), (960, 180), (960, 960)]
    cs = cols_of(p, len(items))
    for i in range(n):
        pill(d, *pos[i], items[i], cs[i], font(58))


def t_split_code(im, d, p):
    d.rectangle([0, 0, W / 2, H], fill=(24, 28, 36))
    for i, l in enumerate(p["code"]):
        d.text((110, 330 + i * 80), l, font=mono(46), fill=[(120, 220, 140), (230, 230, 230), (255, 120, 120)][i % 3])
    ctext(d, W / 4, 150, p["left_title"], font(60), WHITE)
    ctext(d, W * 3 / 4, 150, p["right_title"], font(60), INK)
    for i, lb in enumerate(p["folders"]):
        ic_folder(d, W * 3 / 4, 390 + i * 200, 0.9, c=PALETTE[i % 3], label=lb, lcol=WHITE)


def t_icons_plus(im, d, p):
    header(d, p.get("title"))
    items = p["items"]; k = len(items); n = shown(p, k); cs = cols_of(p, k)
    step = min(350, (W - 300) / k)
    x0 = W / 2 - step * (k - 1) / 2
    for i in range(n):
        cx = x0 + i * step
        d.ellipse([cx - 120, 390, cx + 120, 630], fill=cs[i])
        mtext(d, cx, 510, str(i + 1), font(110), WHITE)
        ctext(d, cx, 670, items[i], fit(d, items[i], 50, step - 20), INK)
        if i < k - 1 and i < n - 1: ctext(d, cx + step / 2, 470, "＋", font(64), GRAY)


def t_levels(im, d, p):
    header(d, p.get("title"))
    items = p["items"]; n = shown(p, len(items)); cs = cols_of(p, len(items))
    for i in range(n):
        it = items[i]
        x, y = 170 + i * 540, 760 - i * 170
        d.rounded_rectangle([x, y, x + 520, 960], radius=24, fill=cs[i])
        ctext(d, x + 260, y + 30, it.get("level", ""), font(40), WHITE)
        ctext(d, x + 260, y + 90, it["name"], font(64), WHITE)
        if it.get("sub"): ctext(d, x + 260, y - 70, it["sub"], font(40, False), INK)


def t_versus(im, d, p):
    header(d, p.get("title"))
    for side, cx in (("left", 480), ("right", 1440)):
        s = p[side]
        kind = s.get("icon", "computer")
        if kind == "cloud": ic_cloud(d, cx, 470, 1.4, label=s.get("label"))
        else: icon(d, kind, cx, 480, 1.4, label=s.get("label"), lcol=BLUE)
        for i in range(s.get("nodes", 0)):
            node(d, cx - 150 + i * 100, 420, 22, BLUE)
            if i < s["nodes"] - 1: d.line([(cx - 128 + i * 100, 420), (cx - 72 + i * 100, 420)], fill=BLUE, width=6)
        if s.get("caption"): ctext(d, cx, 800, s["caption"], font(46, False), GRAY)
    if p.get("sep"): ctext(d, W / 2, 380, p["sep"], font(220), RED)


def t_numbered(im, d, p):
    header(d, p.get("title"), p.get("sub"))
    items = p["items"]; n = shown(p, len(items)); cs = cols_of(p, len(items))
    step = min(190, 640 / len(items))
    for i in range(n):
        y = 330 + i * step
        box(d, [260, y, W - 260, y + step - 40])
        node(d, 360, y + (step - 40) / 2, min(50, (step - 40) / 2 - 6), cs[i], str(i + 1), f=font(52))
        d.text((450, y + (step - 40) / 2 - 36), items[i], font=fit(d, items[i], 60, W - 780), fill=INK)


def t_versions(im, d, p):
    header(d, p.get("title"))
    items = p["items"]; k = len(items); n = shown(p, k); caps = p.get("captions", [])
    d.line([(200, 600), (1720, 600)], fill=LGRAY, width=10)
    step = 1520 / k
    for i in range(n):
        cx = 200 + step * (i + .5)
        node(d, cx, 600, 30, BLUE)
        box(d, [cx - 160, 330, cx + 160, 530])
        ctext(d, cx, 360, items[i], font(60), NAVY)
        d.ellipse([cx + 100, 440, cx + 150, 490], outline=GRAY, width=5)
        d.line([(cx + 125, 465), (cx + 125, 448)], fill=GRAY, width=4); d.line([(cx + 125, 465), (cx + 138, 465)], fill=GRAY, width=4)
        if i < len(caps): ctext(d, cx, 660, caps[i], font(44, False), GRAY)


def t_hub(im, d, p):
    header(d, p.get("title"))
    ic_cloud(d, W / 2, 420, 1.6, label=p.get("center", "GitHub"))
    labels = p.get("labels", ["學校電腦", "家裡筆電", "一起合作的同事"])
    ic_computer(d, 420, 780, 0.9, label=labels[0])
    ic_laptop(d, W / 2, 790, 0.9, label=labels[1])
    ic_person(d, 1500, 700, 1.0, c=GREEN)
    ctext(d, 1500, 930, labels[2], font(40), INK)
    for x in (420, W / 2, 1500):
        d.line([(x, 640 if x != 1500 else 600), (W / 2 + (x - W / 2) * .35, 560)], fill=GREEN, width=6)


def t_cards(im, d, p):
    """並排卡片：items = [{head, body, color}]；可加 sep（前兩張之間的符號）、tag（右下角標籤）"""
    dark = p.get("dark", False)
    if p.get("kicker"): ctext(d, W / 2, 130, p["kicker"], font(64), GOLD if dark else ORANGE)
    else: header(d, p.get("title"), p.get("sub"), dark)
    items = p["items"]; k = len(items); n = shown(p, k); cs = cols_of(p, k)
    gap = 140 if p.get("sep") else 60
    cw = min(800, (W - 300 - gap * (k - 1)) / k)
    x0 = W / 2 - (k * cw + (k - 1) * gap) / 2
    top, bot = p.get("top", 300), p.get("bottom", 860)
    for i in range(n):
        x = x0 + i * (cw + gap); c = col(items[i].get("color"), cs[i])
        box(d, [x, top, x + cw, bot], shadow=not dark)
        d.rounded_rectangle([x, top, x + cw, top + 150], radius=28, fill=c); d.rectangle([x, top + 110, x + cw, top + 150], fill=c)
        mtext(d, x + cw / 2, top + 75, items[i]["head"], fit(d, items[i]["head"], 66, cw - 40), on_color(c))
        body = items[i].get("body", "")
        mtext(d, x + cw / 2, (top + 150 + bot) / 2, body, fit(d, body, p.get("body_size", 64), cw - 60), INK)
        if p.get("sep") and i == 0 and n > 1: ctext(d, x + cw + gap / 2, (top + bot) / 2 - 130, p["sep"], font(200), RED)
        if p.get("arrows") and i < k - 1 and i < n - 1:
            arrow(d, (x + cw + 10, (top + bot) / 2), (x + cw + gap - 10, (top + bot) / 2), GOLD if dark else ORANGE, w=10, head=24)
    if p.get("tag") and n == k:
        d.rounded_rectangle([1540, 900, 1760, 980], radius=20, fill=RED)
        ctext(d, 1650, 912, p["tag"], font(46), WHITE)
    if p.get("term"): term_card(d, p["term"], y=870)


def t_tree(im, d, p):
    header(d, p.get("title"))
    rows = p["rows"]; x, y = 420, 300
    box(d, [x - 60, y - 40, x + 1040, y + len(rows) * 95 + 20])
    for i, r in enumerate(rows[:shown(p, len(rows))]):
        txt, lb = (r + [None])[:2] if isinstance(r, list) else (r, None)
        d.text((x, y + i * 95), txt, font=mono(58), fill=NAVY if i == 0 else INK)
        if p.get("labels", True) and lb: d.text((x + 620, y + i * 95 + 4), "← " + lb, font=font(50), fill=ORANGE)
    if p.get("frame_label"):
        dashed_rect(d, [x - 100, y - 80, x + 1080, y + len(rows) * 95 + 60], BLUE, w=7)
        pill(d, x + 490, y + len(rows) * 95 + 110, p["frame_label"], BLUE, font(52))


def t_transfer(im, d, p):
    """兩端傳送：left/right = {icon, label}；dir = right（左→右）或 left；label＝箭頭文字"""
    header(d, p.get("title"), p.get("sub"))
    L, R = p.get("left", {"icon": "computer", "label": "我的電腦"}), p.get("right", {"icon": "cloud", "label": "GitHub"})
    for s, cx in ((L, 430), (R, 1480)):
        if s["icon"] == "cloud": ic_cloud(d, cx, 470, 1.6, label=s.get("label"))
        else: icon(d, s["icon"], cx, 540, 1.5, label=s.get("label"))
    nodes = p.get("nodes", 0)
    for i in range(nodes):
        node(d, 330 + i * 68, 470, 20, BLUE)
        if not p.get("empty") and p.get("copy_nodes", True): node(d, 1380 + i * 68, 600, 20, BLUE)
    c = LGRAY if p.get("empty") else GREEN
    a, b = ((720, 500), (1230, 500)) if p.get("dir", "right") == "right" else ((1230, 520), (720, 520))
    arrow(d, a, b, c, w=16, head=46, label=p.get("label"), lf=font(64), lcol=ORANGE if p.get("empty") else GREEN, loff=(0, -70))
    if p.get("empty"):
        d.ellipse([1400, 650, 1560, 810], fill=GOLD); ctext(d, 1480, 660, "!", font(120), INK)
        if p.get("empty_note"): ctext(d, 1480, 830, p["empty_note"], font(46), ORANGE)
    if p.get("note"): ctext(d, W / 2, 610, p["note"], font(50), ORANGE)
    if p.get("term"): term_card(d, p["term"], y=820)


def t_todo_screen(im, d, p):
    header(d, p.get("title"))
    box(d, [150, 280, 1000, 900])
    d.rectangle([150, 280, 1000, 350], fill=NAVY2)
    ctext(d, 575, 290, p.get("screen_title", ""), font(40), WHITE)
    for i, ph in enumerate([0, .25, .5, .75, 1]):
        cx, cy, r = 260 + i * 160, 520, 60
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 50, 70))
        if ph >= .5: d.chord([cx - r, cy - r, cx + r, cy + r], -90, 90, fill=GOLD)
        if 0 < ph < .5:
            d.chord([cx - r, cy - r, cx + r, cy + r], -90, 90, fill=GOLD)
            k = int(120 * ph); d.ellipse([cx - r + k, cy - r, cx + r - k, cy + r], fill=(40, 50, 70))
        if .5 < ph < 1:
            k = int(120 * (1 - ph)); d.ellipse([cx - r + k, cy - r, cx + r - k, cy + r], fill=GOLD)
        if ph == 1: d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD)
    if p.get("button"):
        d.rounded_rectangle([420, 700, 730, 790], radius=45, fill=ORANGE); ctext(d, 575, 718, p["button"], font(42), WHITE)
    d.text((1090, 300), p.get("list_title", ""), font=font(52), fill=INK)
    items = p["items"]; n = shown(p, len(items))
    for i in range(n):
        y = 420 + i * 150
        box(d, [1080, y, 1770, y + 115]); mark(d, 1145, y + 57, 36, True)
        d.text((1210, y + 30), items[i], font=fit(d, items[i], 50, 540), fill=INK)


def t_timeline(im, d, p):
    header(d, p.get("title"))
    items = p["items"]; k = len(items); n = shown(p, k)
    compact = bool(p.get("term"))
    x, y0, step = (300, 320, 130) if compact else (660, 260, 150)
    d.line([(x, y0), (x, y0 + step * (k - 1))], fill=LGRAY, width=10)
    for i, lb in enumerate(items):
        on = i < n
        node(d, x, y0 + i * step, 38, BLUE if on else LGRAY, str(i + 1), f=font(40))
        d.text((x + 80, y0 + i * step - 34), lb, font=font(58), fill=INK if on else LGRAY)
    if p.get("cursor") is not None:
        cy = y0 + p["cursor"] * step
        d.polygon([(x - 130, cy - 30), (x - 70, cy), (x - 130, cy + 30)], fill=ORANGE)
        lab = p.get("cursor_label", "")
        d.text((x - 150 - tw(d, lab, font(50))[0], cy - 32), lab, font=font(50), fill=ORANGE)
    if compact: term_card(d, p["term"], cx=1150, y=420)


def t_input_box(im, d, p):
    header(d, p.get("title"))
    box(d, [260, 330, 1660, 800])
    d.text((330, 380), p.get("label", ""), font=font(46), fill=GRAY)
    d.rounded_rectangle([330, 460, 1590, 580], radius=16, fill=LIGHT, outline=LGRAY, width=3)
    d.text((370, 480), p["text"], font=fit(d, p["text"], 62, 1180), fill=INK)
    if p.get("button"):
        d.rounded_rectangle([1250, 650, 1590, 750], radius=20, fill=GREEN); ctext(d, 1420, 668, p["button"], font(50), WHITE)
    if p.get("note"): ctext(d, W / 2, 870, p["note"], font(48, False), GRAY)


def t_day_night(im, d, p):
    L, R = p["left"], p["right"]
    d.rectangle([0, 0, W / 2, H], fill=(255, 244, 214)); d.rectangle([W / 2, 0, W, H], fill=(28, 40, 78))
    d.ellipse([120, 90, 250, 220], fill=(255, 196, 60))
    d.ellipse([1720, 90, 1830, 200], fill=(245, 245, 220)); d.ellipse([1690, 80, 1790, 180], fill=(28, 40, 78))
    ctext(d, W / 4, 110, L["title"], font(64), INK); ctext(d, W * 3 / 4, 110, R["title"], font(64), WHITE)
    icon(d, L.get("icon", "computer"), W / 4, 470, 1.2, label=L.get("label"))
    icon(d, R.get("icon", "laptop"), W * 3 / 4, 470, 1.2, label=R.get("label"), lcol=WHITE)
    flow_row(d, L["steps"], 740, cols=cols_of(L, len(L["steps"])), x0=90, x1=W / 2 - 60, fs=46)
    flow_row(d, R["steps"], 740, cols=cols_of(R, len(R["steps"])), x0=W / 2 + 60, x1=W - 280, fs=46, acol=WHITE)
    if p.get("center"): ic_cloud(d, W / 2, 330, 0.8, label=p["center"])


def t_files(im, d, p):
    header(d, p.get("title"))
    files = p["files"]
    if not p.get("basket"):
        for i, f in enumerate(files):
            ic_file(d, 460 + i * 500, 520, 1.5, name=f["name"], fs=44)
            if f.get("note"):
                d.rectangle([460 + i * 500 - 140, 330, 460 + i * 500 + 140, 430], fill=GOLD); mtext(d, 460 + i * 500, 380, f["note"], font(46), INK)
    else:
        d.rounded_rectangle([230, 330, 1150, 900], radius=36, fill=(225, 238, 255), outline=BLUE, width=5)
        ctext(d, 690, 360, p["basket"], font(56), BLUE)
        inb = [f for f in files if f.get("ok")]; out = [f for f in files if not f.get("ok")]
        for i, f in enumerate(inb):
            ic_file(d, 480 + i * 420, 620, 1.3, name=f["name"], fs=44); mark(d, 560 + i * 420, 500, 38, True)
        for i, f in enumerate(out):
            ic_file(d, 1540, 600, 1.3, name=f["name"], fs=44)
            if f.get("note_out"): d.rectangle([1420, 420, 1660, 500], fill=GOLD); mtext(d, 1540, 460, f["note_out"], font(40), INK)


def t_flow(im, d, p):
    header(d, p.get("title"), p.get("sub"))
    steps = p["boxes"]
    y = p.get("y", 480 if not p.get("term") else 420)
    flow_row(d, steps, y, cols=cols_of(p, len(steps)), h=p.get("h", 150), fs=p.get("fs", 60), lit=p.get("show"))
    for i, t in enumerate(p.get("chips", [])):
        k = len(p["chips"]); pill(d, W / 2 + (i - (k - 1) / 2) * 500, 720, t, NAVY2, font(46))
    if p.get("term"): term_card(d, p["term"], y=720)


def t_four_places(im, d, p):
    header(d, p.get("title"), p.get("sub"))
    zones = p.get("zones") or [["① 工作區", "Working Directory", "正在修改\n教材的地方", "gray"],
                               ["② 暫存區", "Staging Area", "準備放進\n下一個版本", "orange"],
                               ["③ 本機儲存庫", "Local Repository", "本機的\n版本歷史", "blue"],
                               ["④ 遠端儲存庫", "GitHub（Remote）", "放在雲端\n的版本", "green"]]
    acts = p.get("actions", ["Add", "Commit", "Push"])
    lit = shown(p, 4)
    bw, gap, y = 330, 150, 380
    x0 = (W - 4 * bw - 3 * gap) / 2
    for i, (zh, en, s, c) in enumerate(zones):
        x = x0 + i * (bw + gap); on = i < lit; c = col(c)
        d.rounded_rectangle([x, y, x + bw, y + 360], radius=28, fill=c if on else DIMBG)
        tc = WHITE if on else DIMTX
        ctext(d, x + bw / 2, y + 40, zh, font(50), tc); ctext(d, x + bw / 2, y + 120, en, font(32), tc)
        mtext(d, x + bw / 2, y + 265, s, font(40, False), tc)
        if i < 3:
            ac = col(zones[i + 1][3]) if i + 1 < lit else LGRAY
            arrow(d, (x + bw + 8, y + 180), (x + bw + gap - 8, y + 180), ac, w=10, head=26)
            ctext(d, x + bw + gap / 2, y + 115, acts[i], font(34), ac)
    if p.get("pull"):
        xa, xb = x0 + 3 * (bw + gap) + bw / 2, x0 + bw / 2
        d.line([(xa, y + 360), (xa, y + 470), (xb, y + 470)], fill=CYAN_D, width=12)
        arrow(d, (xb, y + 470), (xb, y + 372), CYAN_D, w=12, head=32)
        ctext(d, W / 2, y + 490, p["pull"], font(46), CYAN_D)


def t_git_graph(im, d, p):
    """stage：0 只有 main；1 直接改 main 壞掉；2 開分支；3 合併"""
    header(d, p.get("title"))
    stage = p.get("stage", 0); y = 400; xs = [260, 470, 680]
    d.line([(xs[0], y), (1240, y)], fill=BLUE, width=14)
    for i, lb in enumerate("ABC"): node(d, xs[i], y, 44, BLUE, lb, f=font(44))
    d.text((90, y - 32), p.get("main", "main"), font=mono(52), fill=BLUE)
    sx, sy = 1330, 250
    box(d, [sx, sy, sx + 460, sy + 250], outline=RED if stage == 1 else None, ow=5)
    d.rectangle([sx, sy, sx + 460, sy + 46], fill=NAVY2); ctext(d, sx + 230, sy + 4, p.get("site", "正式教材網站"), font(30), WHITE)
    if stage == 1:
        d.line([(sx + 90, sy + 80), (sx + 200, sy + 150), (sx + 160, sy + 190), (sx + 330, sy + 230)], fill=RED, width=8)
    elif stage == 3:
        d.ellipse([sx + 180, sy + 80, sx + 280, sy + 180], fill=GOLD); d.ellipse([sx + 215, sy + 80, sx + 305, sy + 180], fill=WHITE)
    for i in range(3):
        ic_person(d, sx + 100 + i * 130, sy + 380, 0.55, c=[GREEN, ORANGE, CYAN_D][i], mood="confused" if stage == 1 else "smile")
    caps = p.get("captions", {})
    cap = {1: (caps.get("broken", "學生看到壞掉的畫面"), RED), 3: (caps.get("merged", "多了新功能！"), GREEN)}.get(stage, (caps.get("normal", "學生正在使用"), GRAY))
    ctext(d, sx + 230, sy + 500, cap[0], font(42), cap[1])
    if stage == 1: node(d, 890, y, 44, RED, "!", f=font(56))
    if stage >= 2:
        bx, by = [880, 1080], y + 230
        d.line([(xs[2], y), (bx[0] - 40, by)], fill=ORANGE, width=14); d.line([(bx[0], by), (bx[1], by)], fill=ORANGE, width=14)
        for i, lb in enumerate("DE"): node(d, bx[i], by, 44, ORANGE, lb, f=font(44))
        d.text((560, by + 60), p.get("branch", "feature"), font=mono(46), fill=ORANGE)
        if stage == 3:
            fx = 1240
            d.line([(bx[1], by), (fx, y)], fill=ORANGE, width=14)
            d.ellipse([fx - 62, y - 62, fx + 62, y + 62], fill=GOLD); node(d, fx, y, 46, BLUE, "F", f=font(46))
            pill(d, 980, y - 120, p.get("merge_label", "測試 OK → Merge"), GREEN, font(40), h=80)
    if p.get("term"): term_card(d, p["term"], cx=660, y=820)


def t_form(im, d, p):
    header(d, p.get("title"))
    box(d, [560, 280, 1360, 900])
    d.rounded_rectangle([560, 280, 1360, 400], radius=28, fill=ORANGE); d.rectangle([560, 360, 1360, 400], fill=ORANGE)
    ctext(d, 960, 300, p.get("head", ""), font(62), WHITE)
    items = p["items"]
    for i in range(shown(p, len(items))):
        d.text((630, 470 + i * 120), f"{i + 1}. {items[i]}", font=fit(d, items[i], 48, 640), fill=INK)
    if p.get("term"): term_card(d, p["term"], y=860)


def t_pr_page(im, d, p):
    header(d, p.get("title"))
    checks = p.get("checks", [])
    lit = shown(p, len(checks)) if checks else 0
    right = 1100 if checks else 1810
    box(d, [110, 270, right, 960])
    tabs = "Conversation   Commits   "
    d.text((150, 295), tabs, font=font(36, False), fill=GRAY)
    tx = 150 + tw(d, tabs, font(36, False))[0]
    d.text((tx, 295), "Files changed", font=font(36), fill=INK)
    d.line([(tx, 345), (tx + tw(d, "Files changed", font(36))[0], 345)], fill=ORANGE, width=6)
    for i, (s, l) in enumerate(p["diff"]):
        y = 380 + i * 78
        d.rectangle([140, y, right - 40, y + 70], fill={"+": (218, 245, 226), "-": (252, 224, 224)}.get(s, WHITE))
        d.text((160, y + 12), s, font=mono(42), fill={"+": GREEN, "-": RED}.get(s, GRAY))
        d.text((220, y + 10), l, font=font(40, False), fill=INK)
    if not checks and p.get("legend", True):
        pill(d, 1500, 250, "綠色＝新增", GREEN, font(40), h=80); pill(d, 1170, 250, "紅色＝刪除", RED, font(40), h=80)
    for i, t in enumerate(checks):
        y = 290 + i * 92; on = i < lit
        mark(d, 1180, y + 38, 30, True, bg=GREEN if on else LGRAY)
        d.text((1230, y + 10), t, font=font(44), fill=INK if on else LGRAY)
        if on and p.get("lock_on") == i: ic_lock(d, 1740, y + 32, 0.55)
    if p.get("term"): term_card(d, p["term"], y=850)


def t_conflict(im, d, p):
    header(d, p.get("title"))
    stage = p.get("stage", 0); ya = 420
    for i, (x, t, code) in enumerate([(260, "版本 A", p["a"]), (1000, "版本 B", p["b"])]):
        dim = stage == 3 and i != p.get("keep", 0)
        box(d, [x, ya, x + 660, ya + 260], fill=WHITE if not dim else (236, 238, 242), outline=GREEN if stage == 3 and not dim else None, ow=6)
        d.text((x + 40, ya + 30), t, font=font(48), fill=[BLUE, ORANGE][i] if not dim else LGRAY)
        d.text((x + 40, ya + 130), code, font=fit(d, code, 46, 600, False), fill=INK if not dim else LGRAY)
    if stage < 3:
        c = GOLD if stage < 2 else GREEN
        pill(d, W / 2, 330, p.get("label", "Merge Conflict") if stage < 2 else p.get("decide", "請你決定要留哪一個"), c, font(52))
    if stage == 1:
        ic_person(d, 700, 790, 0.7); ic_robot(d, 1240, 790, 0.8)
        ctext(d, W / 2, 780, "同時修改", font(50), GRAY)
        ctext(d, W / 2, 950, p.get("who", "人和 AI 改了同一個地方"), font(46), GRAY)
    if stage == 2 and p.get("note"): ctext(d, W / 2, 800, p["note"], fit(d, p["note"], 48, W - 300), INK)
    if stage == 3:
        mark(d, 910 if p.get("keep", 0) == 0 else 1650, ya + 20, 44, True)
        node(d, W / 2, 850, 40, BLUE, "C", f=font(44))
        d.text((W / 2 + 70, 820), p.get("done", "再 Commit 一次，就解決了"), font=font(48), fill=BLUE)
        if p.get("term"): term_card(d, p["term"], cx=560, y=790)


def t_ai_chat(im, d, p):
    header(d, p.get("title"))
    ic_person(d, 280, 480, 1.2)
    box(d, [460, 360, 1500, 520], outline=LGRAY)
    d.text((510, 405), p["prompt"], font=fit(d, p["prompt"], 60, 960), fill=INK)
    ic_robot(d, 1650, 700, 1.1)
    box(d, [300, 640, 1450, 960], fill=(24, 28, 36), shadow=False)
    for i, l in enumerate(p.get("code", [])):
        d.text((340, 665 + i * 46), l, font=font(34, False) if re_cjk(l) else mono(36), fill=[(120, 220, 140), (230, 230, 230)][i % 2])
    if p.get("note"): ctext(d, 1650, 880, p["note"], font(40), ORANGE)


def t_warnings(im, d, p):
    safe = p.get("shield", False)
    header(d, p.get("title"))
    items = p["items"]; n = shown(p, len(items))
    for i in range(n):
        x, y = 180 + (i % 3) * 540, 330 + (i // 3) * 260
        c = LGRAY if safe else GOLD
        box(d, [x, y, x + 480, y + 190])
        d.ellipse([x + 30, y + 55, x + 110, y + 135], fill=c); ctext(d, x + 70, y + 52, "!", font(60), WHITE if safe else INK)
        d.text((x + 135, y + 65), items[i], font=fit(d, items[i], 46, 330), fill=LGRAY if safe else INK)
    if safe:
        ic_shield(d, 1450, 760, 1.2)
        if p.get("note"): d.text((180, 880), p["note"], font=font(48), fill=GREEN)


def t_flow_rows(im, d, p):
    """多列流程：rows = [{label, steps, colors, mark: ok/ng}]；show＝亮起的列數"""
    header(d, p.get("title"), p.get("sub"))
    rows = p["rows"]; n = shown(p, len(rows))
    step = p.get("row_step", 240 if any(r.get("label") for r in rows) else 230)
    y0 = p.get("y0", 300)
    for i, r in enumerate(rows):
        y = y0 + i * step; on = i < n
        x0 = 150
        if r.get("label"): d.text((150, y - 60), r["label"], font=font(50), fill=INK if on else LGRAY)
        if r.get("mark"):
            box(d, [150, y - 60, W - 150, y + 190]); mark(d, 260, y + 65, 60, r["mark"] == "ok"); x0 = 360
        flow_row(d, r["steps"], y + 10 if r.get("label") else y, cols=cols_of(r, len(r["steps"])) if on else [DIMBG] * len(r["steps"]),
                 x0=x0, x1=p.get("x1", W - 150), h=p.get("h", 110 if r.get("label") else 130), fs=p.get("fs", 40 if r.get("label") else 46),
                 gap=p.get("gap", 56), acol=GRAY if on else LGRAY)
        if r.get("then"): d.text((p.get("x1", W - 150) + 30, y + 36), r["then"], font=font(40), fill=GRAY)
    if p.get("note"): pill(d, p.get("note_x", 700), y0 + (len(rows) - 1) * step + 180, p["note"], ORANGE, font(40), h=76)
    for i, (t, c) in enumerate(p.get("legend", [])):
        d.rounded_rectangle([1400 + i * 230, 110, 1440 + i * 230, 150], radius=8, fill=col(c)); d.text((1455 + i * 230, 105), t, font=font(36), fill=INK)


def t_columns(im, d, p):
    header(d, p.get("title"))
    cs = p["cols"]; k = len(cs)
    cw = (W - 300 - 60 * (k - 1)) / k
    for i, c in enumerate(cs):
        x = 150 + i * (cw + 60); cc = col(c.get("color"), PALETTE[i])
        box(d, [x, 260, x + cw, 990])
        d.rounded_rectangle([x, 260, x + cw, 380], radius=28, fill=cc); d.rectangle([x, 340, x + cw, 380], fill=cc)
        ctext(d, x + cw / 2, 280, c["head"], font(64), WHITE)
        before = sum(len(x["items"]) for x in cs[:i])
        for j, it in enumerate(c["items"]):
            if p.get("show") is not None and before + j >= p["show"]: break
            d.ellipse([x + 50, 430 + j * 92, x + 80, 460 + j * 92], fill=cc)
            d.text((x + 105, 418 + j * 92), it, font=fit(d, it, 46, cw - 140, False), fill=INK)
    if p.get("stamp") and (p.get("show") is None or p["show"] >= len(cs[0]["items"])):
        d.ellipse([700, 760, 880, 940], outline=RED, width=10); ctext(d, 790, 815, p["stamp"], font(56), RED)


def t_duo(im, d, p):
    if p.get("kicker"): ctext(d, W / 2, 200, p["kicker"], font(60), (175, 195, 220))
    for i, s in enumerate(p["items"]):
        cx = 560 + i * 800
        if s["icon"] == "robot": ic_robot(d, cx, 520, 1.3)
        else: ic_person(d, cx, 470, 1.6)
        c = col(s.get("color"), [ORANGE, CYAN][i])
        ctext(d, cx, 750, s["text"], fit(d, s["text"], 72, 760), c)
        if s.get("sub"): ctext(d, cx, 850, s["sub"], font(56), c)


def t_sync_cycle(im, d, p):
    header(d, p.get("title"))
    ic_computer(d, 330, 470, 1.1, label=p.get("left_label", "學校電腦"))
    ic_cloud(d, W / 2, 330, 1.1, label=p.get("center", "GitHub"))
    ic_laptop(d, 1590, 470, 1.1, label=p.get("right_label", "家裡筆電"))
    L, R = p["left_steps"], p["right_steps"]
    flow_row(d, L, 720, cols=cols_of(p, len(L), "left_colors"), x0=110, x1=1000, fs=46)
    arrow(d, (480, 360), (720, 320), GREEN, w=10, head=28, label="Push", lf=font(44), loff=(0, -40))
    arrow(d, (1200, 320), (1440, 360), GREEN, w=10, head=28, label="Pull", lf=font(44), loff=(0, -40))
    flow_row(d, R, 720, cols=cols_of(p, len(R), "right_colors"), x0=1100, x1=1790, fs=46)


def t_stairs(im, d, p):
    header(d, p.get("title"), p.get("sub"))
    lv = p["levels"]; lit = shown(p, len(lv))
    for i, L in enumerate(lv):
        x, y = 150 + i * 330, 780 - i * 200; on = i < lit; c = col(L.get("color"), [BLUE, ORANGE, (160, 170, 190)][i])
        d.rectangle([x, y, W - 150, y + 200], fill=c if on else DIMBG)
        d.text((x + 40, y + 20), L["name"], font=font(48), fill=WHITE if on else (170, 176, 190))
        d.text((x + 40, y + 88), L["items"], font=font(36, False), fill=WHITE if on else (180, 186, 200), spacing=10)
    if p.get("term"): term_card(d, p["term"], cx=440, y=290)
    if p.get("badge"): pill(d, 1600, 330, p["badge"], GRAY, font(40), h=80)
    if p.get("flag"):
        ic_person(d, 280, 700, 0.7)
        d.line([(390, 600), (390, 780)], fill=INK, width=6); d.polygon([(390, 600), (460, 625), (390, 650)], fill=RED)
        ctext(d, 300, 470, p["flag"], font(48), BLUE)


def t_ring(im, d, p):
    header(d, p.get("title"))
    ic_cloud(d, W / 2, 560, 1.2, label=p.get("center"))
    items = p["items"]; k = len(items); cs = cols_of(p, k)
    for i in range(shown(p, k)):
        a = -math.pi / 2 + i * 2 * math.pi / k
        pill(d, W / 2 + 560 * math.cos(a), 590 + 330 * math.sin(a), items[i], cs[i], font(48))


def t_cta_comment(im, d, p):
    ctext(d, W / 2, 250, p["title"], font(76), WHITE)
    box(d, [460, 430, 1460, 640], shadow=False)
    d.polygon([(560, 640), (620, 640), (560, 700)], fill=WHITE)
    ctext(d, W / 2, 490, p["text"], fit(d, p["text"], 56, 900), NAVY)
    arrow(d, (W / 2, 740), (W / 2, 900), GOLD, w=16, head=44)
    if p.get("note"): ctext(d, W / 2 + 280, 790, p["note"], font(46), GOLD)


def t_thanks(im, d, p):
    ctext(d, W / 2, 330, p.get("name", "黑熊老師"), font(140), WHITE)
    ctext(d, W / 2, 540, p.get("text", "感謝大家觀看這部影片"), font(60), CYAN)


def t_image(im, d, p):
    """圖片卡：image＝圖檔路徑（build.py 會換成絕對路徑）；caption＝下方說明"""
    header(d, p.get("title"), p.get("sub"), p.get("dark", False))
    top = 260 if p.get("sub") else (220 if p.get("title") else 90)
    bottom = H - (150 if p.get("caption") else 90)
    src = Image.open(p["image"]).convert("RGB")
    if p.get("crop"): src = src.crop(tuple(p["crop"]))
    s = min((W - 240) / src.width, (bottom - top) / src.height)
    src = src.resize((int(src.width * s), int(src.height * s)), Image.LANCZOS)
    x, y = (W - src.width) // 2, int(top + (bottom - top - src.height) / 2)
    d.rounded_rectangle([x + 6, y + 10, x + src.width + 6, y + src.height + 10], radius=12, fill=(215, 220, 230) if not p.get("dark") else (4, 16, 34))
    im.paste(src, (x, y))
    if p.get("caption"): ctext(d, W / 2, H - 120, p["caption"], fit(d, p["caption"], 44, W - 300), GRAY if not p.get("dark") else CYAN)


def _shade(layer, box, fade, side, alpha=205):
    """在透明圖層上畫一塊深藍半透明區，fade＝往外漸淡的寬度；side＝left／right／bottom"""
    m = Image.new("L", (W, H), 0); md = ImageDraw.Draw(m)
    x0, y0, x1, y1 = box
    md.rectangle(box, fill=alpha)
    for i in range(fade):
        a = int(alpha * (1 - i / fade) ** 1.6)
        if side == "left": md.line([(x1 + i, y0), (x1 + i, y1)], fill=a)
        elif side == "right": md.line([(x0 - i, y0), (x0 - i, y1)], fill=a)
        else: md.line([(x0, y0 - i), (x1, y0 - i)], fill=a)
    sh = Image.new("RGBA", (W, H), NAVY + (0,)); sh.putalpha(m)
    layer.alpha_composite(sh)


_vig = None


def _vignette():
    """電影感暗角（中心透明、四角變暗）"""
    global _vig
    if _vig is None:
        g = Image.radial_gradient("L").resize((W, H), Image.BICUBIC)       # 中心 0、外圍 255
        _vig = g.point(lambda v: int(max(0, v - 120) * 0.95))
    return _vig


def photo_layers(p):
    """全幅照片分成兩層：bg＝照片（可運鏡）；fg＝文字與底色（RGBA，固定不動）"""
    src = Image.open(p["image"]).convert("RGB")
    s = max(W / src.width, H / src.height)
    src = src.resize((math.ceil(src.width * s), math.ceil(src.height * s)), Image.LANCZOS)
    fx, fy = p.get("focus", (0.5, 0.5))
    x, y = int((src.width - W) * fx), int((src.height - H) * fy)
    bg = src.crop((x, y, x + W, y + H))
    if p.get("vignette", True):
        bg.paste(Image.new("RGB", (W, H), (0, 0, 0)), (0, 0), _vignette())
    if p.get("fit") == "safe": bg = safe_fit(bg)   # 照片重點在下方時：整張縮到字幕區以上（四周延伸邊緣）
    fg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    side = p.get("side")
    if side:
        pw = p.get("panel_w", 780)
        _shade(fg, (0, 0, pw, H) if side == "left" else (W - pw, 0, W, H), 220, side)
    if p.get("lines"):
        _shade(fg, (0, H - 330, W, H), 240, "bottom", 190)
    if p.get("plate"):
        _shade(fg, (0, H - 470, 1100, H), 200, "left", 170)
    d = ImageDraw.Draw(fg)
    if side:
        x0 = 120 if side == "left" else W - p.get("panel_w", 780) + 60
        mw = p.get("panel_w", 780) - 180
        y = 190
        if p.get("kicker"):
            f = fit(d, p["kicker"], 50, mw); kw, kh = tw(d, p["kicker"], f)
            kc = col(p.get("color"), CYAN_D)
            d.rounded_rectangle([x0, y, x0 + kw + 56, y + 84], radius=42, fill=kc)
            d.text((x0 + 28, y + 42 - f.size * 0.62), p["kicker"], font=f, fill=on_color(kc))
            y += 130
        if p.get("title"):
            f = fit(d, p["title"], 74, mw)
            for l in str(p["title"]).split(chr(10)):
                d.text((x0, y), l, font=f, fill=WHITE); y += f.size * 1.3
            y += 40
        items = p.get("items", []); n = shown(p, len(items))
        for i in range(n):
            d.ellipse([x0 + 4, y + 22, x0 + 34, y + 52], fill=GOLD)
            d.text((x0 + 60, y), items[i], font=fit(d, items[i], 56, mw - 60), fill=WHITE); y += 92
    safe = p.get("_safe", True)            # 字幕安全區：下方字卡與名牌整體上移到 y 860 以上
    if p.get("lines"):
        ls = p["lines"]; n = shown(p, len(ls)); hl = set(p.get("hl", []))
        y0 = (SAFE_BOTTOM - 100 if safe else H - 150) - 104 * len(ls)
        for i in range(n):
            ctext(d, W / 2, y0 + i * 104, ls[i], fit(d, ls[i], 72, W - 520), GOLD if i in hl else WHITE)
    if p.get("plate"):
        pl = p["plate"]; y = (SAFE_BOTTOM - 130 - 70 * (len(pl) - 1) - 20) if safe else H - 410
        d.rounded_rectangle([110, y + 8, 124, y + 96], radius=6, fill=GOLD)
        d.text((156, y), pl[0], font=font(84), fill=WHITE); y += 130
        for l in pl[1:]:
            d.text((158, y), l, font=font(48, False), fill=(200, 225, 245)); y += 70
    return bg, fg


def t_photo(im, d, p):
    """全幅照片（課堂實景、分鏡圖）：image；focus＝裁切重心 [x, y]（0–1）；vignette＝暗角（預設開）
    side＋kicker/title/items：左或右的半透明面板，items 支援逐步出現（show）
    lines：下方字卡（hl＝金色行號，show＝顯示前幾行）；plate：左下名牌 [大字, 小字…]
    build.py 會分兩層處理：照片運鏡、文字固定並淡入（見 photo_layers）"""
    bg, fg = photo_layers(p)
    bg = bg.convert("RGBA"); bg.alpha_composite(fg); im.paste(bg.convert("RGB"))


def t_code(im, d, p):
    """程式碼／終端機視窗：lines；hl＝要標亮的行號（從 0 起）"""
    header(d, p.get("title"), p.get("sub"))
    lines = p["lines"]; n = shown(p, len(lines)); hl = set(p.get("hl", []))
    top = 250 if p.get("sub") else 220
    lh = min(84, (H - top - 170) / max(len(lines), 1))
    box(d, [150, top, W - 150, top + 90 + lh * len(lines)], fill=(24, 28, 36), r=20)
    for i, c in enumerate([(255, 95, 87), (255, 189, 46), (40, 200, 64)]):
        d.ellipse([190 + i * 40, top + 26, 214 + i * 40, top + 50], fill=c)
    if p.get("window"): d.text((330, top + 18), p["window"], font=font(32, False), fill=(150, 160, 180))
    for i in range(n):
        y = top + 75 + i * lh
        if i in hl: d.rectangle([160, y - 6, W - 160, y + lh - 10], fill=(50, 60, 90))
        l = lines[i]
        colr = (120, 220, 140) if l.lstrip().startswith(("$", ">")) else (140, 150, 170) if l.lstrip().startswith("#") else (235, 238, 245)
        d.text((200, y), l, font=fit(d, l, lh * 0.56, W - 400, False) if re_cjk(l) else mono(lh * 0.56), fill=colr)
    if p.get("note"): pill(d, W / 2, H - 90, p["note"], ORANGE, font(40), h=76)


def re_cjk(s):
    return any("一" <= ch <= "鿿" for ch in s)


def t_line_chart(im, d, p):
    """折線圖：series＝[{label, color, values}]，上下分開各畫一條（stacked: true）或疊在一起"""
    header(d, p.get("title"), p.get("sub"))
    ser = p["series"]; stacked = p.get("stacked", True)
    x0, x1, top, bottom = 260, W - 200, 280, H - 170
    rows = len(ser) if stacked else 1
    vmax = p.get("ymax") or max(max(s["values"]) for s in ser) * 1.1
    for k, s in enumerate(ser):
        r = k if stacked else 0
        h = (bottom - top) / rows; y1 = top + r * h + h - 30; y0 = top + r * h + 30
        if k == 0 or stacked:
            d.line([(x0, y1), (x1, y1)], fill=LGRAY, width=3)
        vals = s["values"]; c = col(s.get("color"), PALETTE[k])
        pts = [(x0 + (x1 - x0) * i / (len(vals) - 1), y1 - (y1 - y0) * min(v, vmax) / vmax) for i, v in enumerate(vals)]
        d.line(pts, fill=c, width=6, joint="curve")
        for pt in pts: d.ellipse([pt[0] - 5, pt[1] - 5, pt[0] + 5, pt[1] + 5], fill=c)
        d.text((80, (y0 + y1) / 2 - 30), s["label"], font=fit(d, s["label"], 44, 170), fill=c)
    if p.get("xlabel"): ctext(d, (x0 + x1) / 2, H - 140, p["xlabel"], font(38, False), GRAY)


TYPES = {  # 名稱：(函式, 預設深色背景)
    "title": (t_title, True), "statement": (t_statement, True), "word": (t_word, True), "chapter": (t_chapter, True),
    "check": (t_check, True), "bubbles": (t_bubbles, False), "split_code": (t_split_code, False), "icons_plus": (t_icons_plus, False),
    "levels": (t_levels, False), "versus": (t_versus, False), "numbered": (t_numbered, False), "versions": (t_versions, False),
    "hub": (t_hub, False), "cards": (t_cards, False), "tree": (t_tree, False), "transfer": (t_transfer, False),
    "todo_screen": (t_todo_screen, False), "timeline": (t_timeline, False), "input_box": (t_input_box, False),
    "day_night": (t_day_night, False), "files": (t_files, False), "flow": (t_flow, False), "four_places": (t_four_places, False),
    "git_graph": (t_git_graph, False), "form": (t_form, False), "pr_page": (t_pr_page, False), "conflict": (t_conflict, False),
    "ai_chat": (t_ai_chat, False), "warnings": (t_warnings, False), "flow_rows": (t_flow_rows, False), "columns": (t_columns, False),
    "duo": (t_duo, True), "sync_cycle": (t_sync_cycle, False), "stairs": (t_stairs, False), "ring": (t_ring, False),
    "cta_comment": (t_cta_comment, True), "thanks": (t_thanks, True),
    "image": (t_image, False), "code": (t_code, False), "line_chart": (t_line_chart, False),
    "photo": (t_photo, False),
}


# ---- 字幕安全區（2.10.0）：y 880–1000 留給嵌入字幕，畫面內容縮放到 y 16–880 之間 ----
SUB_TOP, SUB_BOTTOM = 880, 1000        # 字幕安全區（1080p）
SAFE_SCALE, SAFE_TOP = 0.80, 16        # 內容縮放比例與上緣；16 + 1080×0.80 = 880，任何版型都不會進入字幕區
SAFE_BOTTOM = 860                      # 照片文字面板等「自由排版」內容的下緣


def safe_fit(im, dark=None):
    """把整張 1920×1080 畫面等比縮到 80%，水平置中、上緣 16 px；四周補背景。
    dark=True：補上與縮放後同間距的深色格線（無接縫）；其他：以邊緣像素延伸（純色、漸層、左右分色都適用）"""
    import numpy as np
    sw, sh = round(W * SAFE_SCALE), round(H * SAFE_SCALE)
    x0, y0 = (W - sw) // 2, SAFE_TOP
    small = im.convert("RGB").resize((sw, sh), Image.LANCZOS)
    if dark:
        bg = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(bg); g = 80 * SAFE_SCALE
        k = -int(x0 // g) - 1
        while x0 + k * g < W: d.line([(x0 + k * g, 0), (x0 + k * g, H)], fill=(16, 38, 70)); k += 1
        k = -int(y0 // g) - 1
        while y0 + k * g < H: d.line([(0, y0 + k * g), (W, y0 + k * g)], fill=(16, 38, 70)); k += 1
        bg.paste(small, (x0, y0)); return bg
    a = np.asarray(small)
    a = np.pad(a, ((y0, H - sh - y0), (x0, W - sw - x0), (0, 0)), mode="edge")
    return Image.fromarray(a)


def render(p, out):
    fn, dark_default = TYPES[p["type"]]
    dark = p.get("dark", dark_default)
    im = Image.new("RGB", (W, H), NAVY if dark else LIGHT)
    d = ImageDraw.Draw(im)
    if dark:
        for x in range(0, W, 80): d.line([(x, 0), (x, H)], fill=(16, 38, 70))
        for y in range(0, H, 80): d.line([(0, y), (W, y)], fill=(16, 38, 70))
    fn(im, d, p)
    if p.get("_safe", True): im = safe_fit(im, dark)
    im.save(out)
