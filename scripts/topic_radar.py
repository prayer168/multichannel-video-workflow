"""選題雷達：抓取國外熱門開源專案、AI 模型、科技討論的原始清單。

資料來源（皆為公開 API，不需要金鑰）：
  - GitHub：近 N 天新建、依星數排序的熱門 repo（GitHub Search API）
  - Hugging Face：目前 trending 的模型與 Spaces
  - Hacker News：近 N 天高分的貼文（Algolia API）

用法：
  python topic_radar.py                 # 預設近 14 天，輸出 Markdown 到終端機
  python topic_radar.py --days 7 --out 選題雷達_raw.md

說明：
  這支程式只負責「國外量化熱度」的原始資料。國內新聞（iThome、數位時代…）、
  官方更新公告、Product Hunt、Reddit、YouTube 競品等，要由 AI 另外用網路搜尋補齊，
  最後依照 references/topic-radar.md 的格式彙整與評分。
"""
import argparse
import datetime as dt
import json
import sys
import urllib.parse
import urllib.request

UA = {"User-Agent": "multichannel-video-workflow-topic-radar"}


def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def github(days, n=20):
    since = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    q = urllib.parse.quote(f"created:>{since}")
    d = get_json(f"https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page={n}")
    rows = []
    for r in d.get("items", []):
        desc = (r.get("description") or "").replace("|", "/")[:90]
        rows.append(f"| [{r['full_name']}]({r['html_url']}) | ⭐ {r['stargazers_count']:,} | {r.get('language') or '-'} | {r['created_at'][:10]} | {desc} |")
    return "| Repo | Stars | 語言 | 建立日 | 說明 |\n|---|---|---|---|---|\n" + "\n".join(rows)


def huggingface(kind, n=15):
    d = get_json(f"https://huggingface.co/api/{kind}?sort=trendingScore&direction=-1&limit={n}")
    rows = []
    for m in d:
        mid = m.get("id") or m.get("modelId")
        url = f"https://huggingface.co/{'spaces/' if kind == 'spaces' else ''}{mid}"
        extra = m.get("pipeline_tag") or m.get("sdk") or "-"
        rows.append(f"| [{mid}]({url}) | ❤ {m.get('likes', 0):,} | {extra} | {(m.get('createdAt') or '')[:10]} |")
    return "| 名稱 | Likes | 類型 | 建立日 |\n|---|---|---|---|\n" + "\n".join(rows)


def hackernews(days, n=20):
    ts = int((dt.datetime.now() - dt.timedelta(days=days)).timestamp())
    url = ("https://hn.algolia.com/api/v1/search?tags=story"
           f"&numericFilters=created_at_i>{ts},points>150&hitsPerPage=100")
    hits = sorted(get_json(url).get("hits", []), key=lambda h: -h.get("points", 0))[:n]
    rows = []
    for h in hits:
        title = (h.get("title") or "").replace("|", "/")
        link = h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}"
        rows.append(f"| [{title}]({link}) | ▲ {h.get('points', 0)} | {h.get('num_comments', 0)} | {h.get('created_at', '')[:10]} |")
    return "| 標題 | 分數 | 留言 | 日期 |\n|---|---|---|---|\n" + "\n".join(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--out")
    a = ap.parse_args()
    parts = [f"# 選題雷達原始資料（{dt.date.today()}，近 {a.days} 天）"]
    for title, fn in [
        ("GitHub 新興熱門 repo", lambda: github(a.days)),
        ("Hugging Face 熱門模型", lambda: huggingface("models")),
        ("Hugging Face 熱門 Spaces", lambda: huggingface("spaces")),
        ("Hacker News 高分討論", lambda: hackernews(a.days)),
    ]:
        try:
            parts.append(f"## {title}\n\n{fn()}")
        except Exception as e:  # 單一來源失敗不影響其他來源
            parts.append(f"## {title}\n\n⚠️ 抓取失敗：{e}")
    failed = sum("⚠️ 抓取失敗" in p for p in parts)
    if failed:
        parts.append(
            "## 備援提示\n\n"
            f"有 {failed} 個來源抓取失敗（常見原因：雲端網路代理回 403）。"
            "請依 references/topic-radar.md「量化來源備援」：改在本機電腦執行本腳本，"
            "或以每日 AI 新聞彙整、OSS Insight／Trendshift 與官方文件補足，"
            "並在報告開頭註明失敗來源，熱度欄位標【待補】。"
        )
    md = "\n\n".join(parts) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(md)
        print(f"已輸出 {a.out}")
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(md)


if __name__ == "__main__":
    main()
