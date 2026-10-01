"""臉書分享圖（1200x630）：背景照片靠右，左側深藍漸層＋上下細黑邊；小標、兩行主標、工具膠囊、底部一行、熊掌徽章
用法：python fb_cover.py <影片專案資料夾> --image 圖檔 --kicker 小標 --title 第一行 --title2 第二行 [--chips A B C] [--footer 底部文字]
  --image：專案資料夾內的相對路徑或絕對路徑（建議用最溫暖、有人物的那張畫面）
輸出：3_製作後/臉書宣傳/臉書分享圖_1200x630.png（不覆寫，已存在時加 _2）
"""
import argparse, os, sys
from PIL import Image, ImageDraw, ImageFont
sys.stdout.reconfigure(encoding="utf-8")
W, H = 1200, 630
NAVY, WHITE, GOLD, CYAN, INK = (9, 29, 56), (255, 255, 255), (255, 209, 102), (62, 224, 255), (4, 14, 30)
CHIP = [(150, 90, 200), (0, 150, 190), (242, 140, 40), (46, 170, 110), (47, 111, 219), (220, 80, 80)]
F = lambda s: ImageFont.truetype("C:/Windows/Fonts/msjhbd.ttc", s)
HERE = os.path.dirname(os.path.abspath(__file__))
BADGE_REL = "04_品牌資產/片頭動畫/延伸版本/浮水印/浮水印_徽章_512.png"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project"); ap.add_argument("--image", required=True); ap.add_argument("--kicker", default="")
    ap.add_argument("--title", required=True); ap.add_argument("--title2", default=""); ap.add_argument("--chips", nargs="*", default=[])
    ap.add_argument("--footer", default=""); ap.add_argument("--badge", default=None)
    a = ap.parse_args()
    proj = os.path.abspath(a.project); out_dir = os.path.join(proj, "3_製作後", "臉書宣傳"); os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "臉書分享圖_1200x630.png"); k = 2
    while os.path.exists(out): out = os.path.join(out_dir, f"臉書分享圖_1200x630_{k}.png"); k += 1
    img = a.image if os.path.isabs(a.image) else os.path.join(proj, a.image)
    src = Image.open(img).convert("RGB")
    s = max(W / src.width, H / src.height); src = src.resize((round(src.width * s), round(src.height * s)), Image.LANCZOS)
    im = src.crop((src.width - W, (src.height - H) // 2, src.width, (src.height - H) // 2 + H))
    m = Image.new("L", (W, H)); md = ImageDraw.Draw(m)
    for x in range(W):
        md.line([(x, 0), (x, H)], fill=235 if x < 470 else max(0, int(235 * (1 - (x - 470) / 330) ** 1.5)) if x < 800 else 0)
    im.paste(Image.new("RGB", (W, H), NAVY), (0, 0), m)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 34], fill=(0, 0, 0)); d.rectangle([0, H - 34, W, H], fill=(0, 0, 0))

    def ol(xy, t, size, fill, st=5):
        f = F(size)
        while d.textbbox((0, 0), t, font=f)[2] > 640 and size > 40: size -= 4; f = F(size)
        d.text(xy, t, font=f, fill=fill, stroke_width=st, stroke_fill=INK)
    if a.kicker:
        d.rounded_rectangle([52, 70, 64, 128], radius=5, fill=GOLD); ol((84, 64), a.kicker, 40, CYAN, 3)
    ol((48, 140), a.title, 92, WHITE)
    if a.title2: ol((48, 248), a.title2, 92, GOLD)
    x, y = 52, 380
    for i, t in enumerate(a.chips):
        f = F(32); l, tp, r, b = d.textbbox((0, 0), t, font=f); w = r - l + 40
        if x + w > 640: x, y = 52, y + 66
        c = CHIP[i % len(CHIP)]
        d.rounded_rectangle([x, y, x + w, y + 54], radius=27, fill=c); d.text((x + 20 - l, y + 27 - (b - tp) / 2 - tp), t, font=f, fill=WHITE); x += w + 12
    if a.footer: ol((52, 528), a.footer, 30, WHITE, 3)
    badge = a.badge or next((p for p in [os.path.join(proj, "..", "..", BADGE_REL), os.path.join(HERE, "..", "..", "..", BADGE_REL)] if os.path.exists(p)), None)
    if badge:
        bd = Image.open(badge).convert("RGBA").resize((96, 96)); im.paste(bd, (W - 124, H - 34 - 112), bd)
    im.save(out); print("分享圖：", out)


if __name__ == "__main__":
    main()
