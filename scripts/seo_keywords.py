"""SEO 關鍵字研究：YouTube 搜尋建議（需求）＋ 搜尋結果競爭分析（供給）。

用法：
  python seo_keywords.py "Claude Skills"
  python seo_keywords.py "Claude Skills" "Obsidian" --top 20 --dates --out seo.md

輸出（Markdown）：
  1. 搜尋建議：種子詞加上常見修飾詞（教學、免費、安裝…）之後，YouTube 自動完成給的建議詞
     → 出現在建議中＝真的有人在搜尋；直接相關的建議詞越多，需求越明確
  2. 競爭分析：用「種子詞＋教學」搜尋 YouTube 前 N 支影片的標題、頻道、觀看數、長度
     （加 --dates 會逐支抓上傳日期，比較慢），並統計繁中影片數與近 90 天影片數
  3. 機會判斷：需求（相關建議詞數）與供給（繁中影片數）的簡單評語

需要：yt-dlp（pip install yt-dlp）。建議詞使用公開的自動完成端點，不需要金鑰。
"""
import argparse
import datetime as dt
import json
import statistics
import sys
import urllib.parse
import urllib.request

MODIFIERS = ["", " 教學", " 免費", " 中文", " 安裝", " 怎麼用", " 入門", " 推薦", " vs", " 替代"]
# 常見的簡體專用字，用來粗略判斷標題是不是簡中（啟發式，不保證精確）
SIMPLIFIED = set("这个们来说时为对会过还没发实现应数据库软视频开关门问题图习网页设计书线车东间长点"
                 "础厂级优览让边产务资讯录闻标热认识详细节钟从进写读动启样种无亿万两战场讲")


def suggest(q):
    url = ("https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&hl=zh-TW&gl=TW&q="
           + urllib.parse.quote(q))
    raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20).read()
    try:
        return json.loads(raw.decode("utf-8"))[1]
    except UnicodeDecodeError:
        return json.loads(raw.decode("big5", errors="ignore"))[1]


def expand(seed):
    """回傳 (相關建議詞, 其他延伸詞)。相關＝包含種子詞的每一個字詞（不分大小寫）。"""
    counts = {}
    for m in MODIFIERS:
        try:
            for i, s in enumerate(suggest(seed + m)):
                c = counts.setdefault(s, [0, 99])
                c[0] += 1
                c[1] = min(c[1], i + 1)
        except Exception as e:
            print(f"⚠️ 建議詞抓取失敗（{seed + m}）：{e}", file=sys.stderr)
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1][0], kv[1][1]))
    tokens = [w.lower() for w in seed.split()]
    related = [kv for kv in ranked if all(w in kv[0].lower() for w in tokens)]
    others = [kv for kv in ranked if kv not in related]
    return related, others


def is_traditional(title):
    has_cjk = any("一" <= ch <= "鿿" for ch in title)
    return has_cjk and not any(ch in SIMPLIFIED for ch in title)


def competition(keyword, top, with_dates):
    import yt_dlp
    base = {"quiet": True, "no_warnings": True, "skip_download": True, "extract_flat": True}
    zh = dict(base, extractor_args={"youtube": {"lang": ["zh-TW"]}})
    # 繁中語系拿得到原始中文標題；預設語系才拿得到觀看數 → 搜尋兩次後依影片 ID 合併
    with yt_dlp.YoutubeDL(zh) as y:
        entries = y.extract_info(f"ytsearch{top}:{keyword}", download=False).get("entries", [])
    with yt_dlp.YoutubeDL(base) as y:
        views = {e["id"]: e.get("view_count") for e in
                 y.extract_info(f"ytsearch{top}:{keyword}", download=False).get("entries", [])}
    for e in entries:
        e["view_count"] = e.get("view_count") or views.get(e["id"])
    if with_dates:
        full = {"quiet": True, "no_warnings": True, "skip_download": True}
        with yt_dlp.YoutubeDL(full) as y:
            for e in entries:
                try:
                    info = y.extract_info(e["url"], download=False)
                    e["upload_date"] = info.get("upload_date")
                    e["view_count"] = e.get("view_count") or info.get("view_count")
                except Exception:
                    e["upload_date"] = None
    return entries


def report(seed, top, with_dates):
    out = [f"## 關鍵字：{seed}"]
    sug, others = expand(seed)
    out.append(f"\n### 搜尋建議（需求）：與「{seed}」直接相關的建議詞共 {len(sug)} 個\n")
    out.append("| 建議詞 | 出現次數 | 最佳排名 |\n|---|---|---|")
    out += [f"| {s} | {c} | {r} |" for s, (c, r) in sug[:30]]
    if others:
        out.append("\n其他延伸詞（可能相關，需要人工判斷）：" + "、".join(s for s, _ in others[:12]))

    ents = competition(seed + " 教學", top, with_dates)
    today = dt.date.today()
    views = [e.get("view_count") or 0 for e in ents]
    trad_ids = {e["id"] for e in ents if is_traditional(e.get("title") or "")}
    recent = 0
    out.append(f"\n### 競爭分析（供給）：搜尋「{seed} 教學」前 {len(ents)} 支\n")
    out.append("| # | 標題 | 頻道 | 觀看 | 長度 | 上傳日 | 繁中 |\n|---|---|---|---|---|---|---|")
    for i, e in enumerate(ents, 1):
        ud = e.get("upload_date")
        date_s = f"{ud[:4]}-{ud[4:6]}-{ud[6:]}" if ud else "-"
        if ud and (today - dt.date(int(ud[:4]), int(ud[4:6]), int(ud[6:]))).days <= 90:
            recent += 1
        title = (e.get("title") or "").replace("|", "/")[:60]
        channel = (e.get("channel") or "-").replace("|", "/")
        dur = int(e.get("duration") or 0)
        out.append(f"| {i} | [{title}]({e.get('url')}) | {channel} | {e.get('view_count') or 0:,} "
                   f"| {dur // 60}:{dur % 60:02d} | {date_s} | {'✓' if e['id'] in trad_ids else ''} |")
    med = int(statistics.median(views)) if views else 0
    out.append(f"\n- 觀看數中位數：{med:,}")
    out.append(f"- 繁中影片：{len(trad_ids)}/{len(ents)}")
    if with_dates:
        out.append(f"- 近 90 天影片：{recent}/{len(ents)}")

    demand, supply_tw = len(sug), len(trad_ids)
    if demand >= 15 and supply_tw <= 3:
        verdict = "🟢 機會高：有人在搜尋，而且繁中教學少"
    elif demand >= 8 and supply_tw <= 6:
        verdict = "🟡 機會中：需要差異化角度（更新版本、新手向、組合技）"
    elif demand < 8:
        verdict = "⚪ 搜尋需求低：適合當成趨勢題（靠推薦流量），不要期待搜尋流量"
    else:
        verdict = "🔴 競爭高：繁中教學已經很多，要有明確的新角度才拍"
    out.append(f"- **機會判斷：{verdict}**（啟發式參考，最後仍然由人判斷）")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seeds", nargs="+", help="種子關鍵字，例如 \"Claude Skills\"")
    ap.add_argument("--top", type=int, default=20, help="競爭分析要看幾支影片（預設 20）")
    ap.add_argument("--dates", action="store_true", help="逐支抓上傳日期（較慢）")
    ap.add_argument("--out")
    a = ap.parse_args()
    md = f"# SEO 關鍵字研究（{dt.date.today()}）\n\n" + "\n\n".join(report(s, a.top, a.dates) for s in a.seeds) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(md)
        print(f"已輸出 {a.out}")
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(md)


if __name__ == "__main__":
    main()
