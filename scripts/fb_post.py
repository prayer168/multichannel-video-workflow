"""影片完成後的臉書宣傳套件：把 3_製作後/臉書宣傳/ 裡的中英文案做成「一鍵複製」頁
用法：python fb_post.py <影片專案資料夾> [--title 影片名稱] [--url YouTube網址]
輸入（AI 先寫好）：
  3_製作後/臉書宣傳/臉書文_中文.txt、臉書文_英文.txt
  3_製作後/臉書宣傳/臉書分享圖_1200x630.png（選用；貼文時當圖片上傳）
輸出：
  3_製作後/臉書宣傳/facebook-post.html（中英雙語、「複製」「複製全部」按鈕；雙擊用瀏覽器開啟即可）
--url：把文案裡的【YouTube 連結】／[YouTube link] 換成正式網址（.txt 另存新檔，不覆寫原稿）
"""
import argparse, html, os, sys
sys.stdout.reconfigure(encoding="utf-8")

PAGE = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>臉書文案 · {title}</title>
<meta property="og:type" content="website">
<meta property="og:title" content="臉書文案 · {title}">
<meta property="og:image" content="臉書分享圖_1200x630.png">
<style>
  :root {{ --bg: #f4f3ee; --card: #ffffff; --surface: #f1efe8; --text: #2c2c2a; --muted: #5f5e5a;
          --info-bg: #e3ecf7; --info-text: #0b2a52; --border: rgba(0,0,0,0.12); --radius: 12px; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg: #10161f; --card: #182130; --surface: #1f2a3b; --text: #ededeb; --muted: #b4b2a9;
            --info-bg: #091d38; --info-text: #ffd166; --border: rgba(255,255,255,0.14); }} }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--bg); color: var(--text); line-height: 1.7; padding: 24px 16px;
         font-family: -apple-system, "Segoe UI", "Noto Sans TC", "Microsoft JhengHei", sans-serif; }}
  .wrap {{ max-width: 680px; margin: 0 auto; }}
  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px 20px 24px; }}
  .head {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 16px; }}
  .title {{ font-size: 17px; font-weight: 600; }}
  .cover {{ width: 100%; border-radius: 8px; margin-bottom: 16px; display: block; }}
  button {{ font: inherit; font-size: 14px; cursor: pointer; color: var(--text); background: transparent;
           border: 1px solid var(--border); border-radius: 8px; padding: 6px 14px; min-height: 36px; }}
  button:hover {{ background: var(--surface); }}
  .seg {{ margin-bottom: 20px; }} .seg:last-child {{ margin-bottom: 0; }}
  .seg-head {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }}
  .tag {{ font-size: 13px; font-weight: 500; color: var(--info-text); background: var(--info-bg); padding: 3px 10px; border-radius: 8px; }}
  .post {{ white-space: pre-wrap; font-size: 15px; background: var(--surface); border-radius: 8px; padding: 16px 18px; word-break: break-word; }}
  .small {{ font-size: 13px; padding: 4px 10px; }}
  .foot {{ max-width: 680px; margin: 14px auto 0; font-size: 12px; color: var(--muted); text-align: center; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="card">
    <div class="head"><span class="title">臉書文案 · {title}</span><button id="copy-all">複製全部</button></div>
    {cover}
    <div class="seg"><div class="seg-head"><span class="tag">中文</span><button class="copy-one small" data-target="zh">複製</button></div>
      <div id="zh" class="post">{zh}</div></div>
    <div class="seg"><div class="seg-head"><span class="tag">English</span><button class="copy-one small" data-target="en">Copy</button></div>
      <div id="en" class="post">{en}</div></div>
  </div>
  <p class="foot">黑熊老師 · 點按鈕即可複製文案<br>發文小技巧：先只貼 YouTube 網址、等預覽縮圖出現，再貼上文案（不要關掉預覽卡）；沒有出現就到 <a href="https://developers.facebook.com/tools/debug/" style="color:inherit">分享偵錯工具</a> 按「再次抓取」</p>
</div>
<script>
(function () {{
  function flash(b, ok) {{ var p = b.textContent; b.textContent = ok; setTimeout(function () {{ b.textContent = p; }}, 1600); }}
  function fallback(t, b, ok) {{ var ta = document.createElement('textarea'); ta.value = t; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select(); try {{ document.execCommand('copy'); flash(b, ok); }} catch (e) {{}} document.body.removeChild(ta); }}
  function copy(t, b, ok) {{ if (navigator.clipboard && navigator.clipboard.writeText) {{
      navigator.clipboard.writeText(t).then(function () {{ flash(b, ok); }}).catch(function () {{ fallback(t, b, ok); }}); }} else {{ fallback(t, b, ok); }} }}
  var zh = document.getElementById('zh').textContent, en = document.getElementById('en').textContent;
  document.getElementById('copy-all').addEventListener('click', function () {{ copy(zh + '\\n\\n— — —\\n\\n' + en, this, '已複製！'); }});
  document.querySelectorAll('.copy-one').forEach(function (b) {{ b.addEventListener('click', function () {{
    var t = this.getAttribute('data-target'); copy(document.getElementById(t).textContent, this, t === 'zh' ? '已複製！' : 'Copied!'); }}); }});
}})();
</script>
</body>
</html>
"""


def free_path(p):
    base, ext = os.path.splitext(p); k = 2
    while os.path.exists(p): p = f"{base}_{k}{ext}"; k += 1
    return p


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--title", default=None); ap.add_argument("--url", default=None)
    a = ap.parse_args()
    d = os.path.join(os.path.abspath(a.project), "3_製作後", "臉書宣傳")
    zh = open(os.path.join(d, "臉書文_中文.txt"), encoding="utf-8-sig").read().strip()
    en = open(os.path.join(d, "臉書文_英文.txt"), encoding="utf-8-sig").read().strip()
    if a.url:
        zh, en = zh.replace("【YouTube 連結】", a.url), en.replace("[YouTube link]", a.url)
        for name, txt in (("臉書文_中文_含連結.txt", zh), ("臉書文_英文_含連結.txt", en)):
            p = free_path(os.path.join(d, name)); open(p, "w", encoding="utf-8").write(txt + "\n"); print("另存：", p)
    title = a.title or os.path.basename(os.path.abspath(a.project))
    cover = '<img class="cover" src="臉書分享圖_1200x630.png" alt="分享圖">' if os.path.exists(os.path.join(d, "臉書分享圖_1200x630.png")) else ""
    out = os.path.join(d, "facebook-post.html")
    if os.path.exists(out) and not a.url: out = free_path(out)
    open(out, "w", encoding="utf-8").write(PAGE.format(title=html.escape(title), cover=cover, zh=html.escape(zh), en=html.escape(en)))
    print("一鍵複製頁：", out)
    left = [x for x in ("【YouTube 連結】", "[YouTube link]") if x in zh + en]
    if left: print("提醒：文案裡還有連結佔位字", left, "→ 上傳 YouTube 後用 --url 重跑")


if __name__ == "__main__":
    main()
