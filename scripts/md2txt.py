"""把上架文案（Markdown）轉成純文字 .txt，方便直接複製貼到 YouTube
用法：python md2txt.py <來源.md> [輸出.txt]（省略輸出時，同名改副檔名）
- 去掉 Markdown 符號；程式碼框只留內容；表格改成全形空白分隔；UTF-8（含 BOM）＋Windows 換行
- 另外產生同資料夾的「YouTube標記.txt」：取「標籤」段落的程式碼框，去重複後存成一行（貼到 YouTube 工作室「標記」欄）
- 原本的 .md 保留不動
"""
import re, sys

YT_LIMIT = 500      # YouTube 標記欄上限（含逗號；有空白的標記會多算 2 個引號）


def to_txt(src, dst):
    out = []
    for line in open(src, encoding="utf-8").read().split("\n"):
        if line.strip().startswith("```"): continue
        if re.match(r"^\|[-| ]+\|$", line.strip()): continue
        m = re.match(r"^(#+)\s*(.*)", line)
        if m:
            t = m.group(2)
            out += (["", "=" * 40, t, "=" * 40] if len(m.group(1)) == 1 else ["", "【" + t + "】"])
            continue
        if line.startswith("|"):
            line = "　".join(c.strip() for c in line.strip().strip("|").split("|"))
        if line.startswith("> "): line = "※ " + line[2:]
        line = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
        line = re.sub(r"`([^`]+)`", r"\1", line)
        out.append(line)
    text = "\n".join(out).strip() + "\n"
    open(dst, "w", encoding="utf-8-sig", newline="\r\n").write(text)
    print(dst, len(text), "字")


def yt_length(tags):
    return sum(len(t) + (2 if " " in t else 0) for t in tags) + max(0, len(tags) - 1)


def to_tags(src, dst):
    """找「標籤」標題後的第一個程式碼框 → 逗號分隔 → 去重複（不分大小寫）→ 超過上限就從後面刪"""
    s = open(src, encoding="utf-8").read()
    m = re.search(r"標籤[^\n]*\n+```[^\n]*\n(.*?)\n```", s, re.S)
    if not m: return
    tags, seen = [], set()
    for t in re.split(r"[,，、\n]", m.group(1)):
        t = t.strip()
        if t and t.lower() not in seen:
            seen.add(t.lower()); tags.append(t)
    dropped = []
    while yt_length(tags) > YT_LIMIT: dropped.insert(0, tags.pop())
    open(dst, "w", encoding="utf-8-sig", newline="\r\n").write(", ".join(tags) + "\n")
    print(dst, f"{len(tags)} 個標記，{yt_length(tags)}/{YT_LIMIT} 字元" + (f"；超過上限，刪掉：{', '.join(dropped)}" if dropped else ""))


if __name__ == "__main__":
    src = sys.argv[1]
    to_txt(src, sys.argv[2] if len(sys.argv) > 2 else src[:-3] + ".txt")
    to_tags(src, re.sub(r"[^/\\]+$", "YouTube標記.txt", src))
