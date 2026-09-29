"""把上架文案（Markdown）轉成純文字 .txt，方便直接複製貼到 YouTube
用法：python md2txt.py <來源.md> [輸出.txt]（省略輸出時，同名改副檔名）
- 去掉 Markdown 符號；程式碼框只留內容；表格改成全形空白分隔；UTF-8（含 BOM）＋Windows 換行
- 原本的 .md 保留不動
"""
import re, sys
src = sys.argv[1]
dst = sys.argv[2] if len(sys.argv) > 2 else src[:-3] + ".txt"
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
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        line = "　".join(cells)
    if line.startswith("> "): line = "※ " + line[2:]
    line = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
    line = re.sub(r"`([^`]+)`", r"\1", line)
    out.append(line)
text = "\n".join(out).strip() + "\n"
open(dst, "w", encoding="utf-8-sig", newline="\r\n").write(text)
print(dst, len(text), "字")
