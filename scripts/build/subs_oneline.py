"""單行字幕（2.10.0 樣式；2.13.0 起預設不燒錄）：依旁白停頓切成一行一行，產生 SRT／ASS；加 --burn 才燒錄進影片。

用法：
  python subs_oneline.py <影片專案資料夾>                      # 橫式主片：自動找字幕、配音與最新完整版影片
  python subs_oneline.py <影片專案資料夾> --format shorts      # Shorts（直式 1080×1920）
  python subs_oneline.py <專案> --burn                         # 另外燒錄 _單行字幕.mp4（僅使用者要求時）
  （--no-burn 保留相容，現為預設行為）
  python subs_oneline.py <專案> --srt X.srt --narration X.wav --video X.mp4   # 指定檔案

輸入（預設位置，舊工作區結構）：
  2_製作中/字幕/字幕_zh-TW_<配音>.srt         build.py 的逐句字幕（Gemini 優先）
  2_製作中/剪輯專案/build/narration_norm.wav   與影片同時間軸的旁白音軌
  3_製作後/輸出成品/*_完整版.mp4               最新的完整版（含黑熊老師與片尾）
輸出：
  2_製作中/字幕/字幕_zh-TW_單行.srt／.ass      上傳 YouTube 用 SRT；ASS 為燒錄樣式
  3_製作後/輸出成品/<影片>_單行字幕.mp4         燒錄版（不覆寫）

規則見 references/subtitle-style.md：一次一行、白字黑框無底色、水平置中、離下緣 96 px（1080p），
橫式每行 ≤17 字、Shorts 每行 ≤12 字；換行點對齊旁白停頓；只在標點、頓號、詞與詞之間換行，產品名不拆。"""
import argparse, glob, os, re, subprocess, sys
import numpy as np, soundfile as sf

FORMATS = {
    # 橫式 1920×1080：58 級、白字黑框 4.5、陰影 1.5、置中、底部 96 px；左右邊界 120（17 字約 990 px，碰不到右下角黑熊老師）
    "landscape": dict(res=(1920, 1080), size=58, maxl=17, outline=4.5, shadow=1.5, ml=120, mr=120, mv=96),
    # Shorts 1080×1920：72 級、每行 ≤12 字；字幕中心約在畫面高度 65%，避開下方標題列與右側按鈕
    "shorts": dict(res=(1080, 1920), size=72, maxl=12, outline=5.5, shadow=2, ml=70, mr=140, mv=620),
}
MIN_DUR = 0.7          # 每行最短顯示秒數；太短時與同句相鄰行合併（合併後不超過字數上限）
TOK = re.compile(r'Nano Banana(?: 2\.1| Pro)?|Google AI Studio|Gemini App|Claude Code|[A-Za-z0-9.+#_-]+|\s+|[，、：；？！。「」]|.')
PUNCT = '，：；？！。'                                  # 子句斷點（頓號不當斷點）
SAFE = set('的了是在用把到就都也要會讓給說時後前裡上中再等著過、')   # 可以在這些字之後換行
BEFORE = set('和與及或但並')                                         # 連接詞放到下一行開頭


def wlen(s): return sum(0.55 if c.isascii() else 1 for c in s)


def ts(x):
    h, m, s = x.replace(',', '.').split(':'); return int(h) * 3600 + int(m) * 60 + float(s)


class Line:
    """一句旁白的切行：先依標點分子句，逗號後可合併；過長子句在頓號／詞界切開，優先選最接近停頓的位置"""
    def __init__(self, text, t0, t1, pauses, maxl):
        self.text, self.t0, self.t1, self.ps, self.maxl = text, t0, t1, pauses, maxl

    def split_long(self, c, offset):
        toks = TOK.findall(c); cands = []; acc = ''
        for i, t in enumerate(toks[:-1]):
            acc += t; nxt = toks[i + 1]
            ok = (t.isspace() or t in SAFE or nxt in BEFORE or (t[-1].isascii() and t[-1].isalnum() and not nxt[0].isascii())
                  or (nxt[0].isascii() and nxt[0].isalnum() and not t[-1].isascii()))
            if ok and wlen(acc) <= self.maxl and wlen(c) - wlen(acc) > 2: cands.append(acc)
        if not cands:
            acc = ''
            for t in toks:
                if wlen(acc + t) > max(self.maxl / 2, wlen(c) / 2): break
                acc += t
            return acc or toks[0]
        total = wlen(self.text)
        def score(head):
            tm = self.t0 + (self.t1 - self.t0) * (offset + wlen(head)) / total
            near = min([abs(e - tm) for _, e in self.ps] or [9])
            return (0 if head.endswith('、') else 1, 0 if near < 0.35 else 1, abs(wlen(head) - wlen(c) / 2))
        return min(cands, key=score)

    def phrases(self):
        clauses, cur = [], ''
        for t in TOK.findall(self.text):
            cur += t
            if t in PUNCT: clauses.append(cur); cur = ''
        if cur.strip(): clauses.append(cur)
        lines = []
        for c in clauses:
            if lines and wlen(lines[-1] + c) <= self.maxl and (lines[-1].endswith('，') or wlen(lines[-1]) <= 3):
                lines[-1] += c; continue
            if lines and wlen(lines[-1]) <= 3: c = lines.pop() + c
            while wlen(c) > self.maxl:
                head = self.split_long(c, sum(wlen(l) for l in lines)); lines.append(head); c = c[len(head):]
            if c.strip(): lines.append(c)
        return [l for l in lines if l.strip()]


def clean(s):
    s = re.sub(r'[，、。；：]$', '', s.strip())
    return re.sub(r'[，；]', '　', s).strip()


def make_cues(srt, wav, maxl):
    y, sr = sf.read(wav); y = y if y.ndim == 1 else y.mean(1)
    hop = int(sr * 0.01)
    db = 20 * np.log10(np.sqrt(np.convolve(y ** 2, np.ones(hop * 3) / (hop * 3), mode='same'))[::hop] + 1e-9)

    def pauses(t0, t1):   # 句中停頓：比該句中位數低 18 dB、持續 ≥ 80 ms；回傳 (開始, 結束)
        a, b = int(t0 * 100), int(t1 * 100); seg = db[a:b]
        if len(seg) < 10 or not (seg > -80).any(): return []
        low = seg < np.median(seg[seg > -80]) - 18; res = []; i = 0
        while i < len(low):
            if low[i]:
                j = i
                while j < len(low) and low[j]: j += 1
                if j - i >= 8 and i > 5 and j < len(low) - 5: res.append((t0 + i / 100, t0 + j / 100))
                i = j
            else: i += 1
        return res

    cues, aligned, est = [], 0, 0
    for b in re.split(r'\n\s*\n', open(srt, encoding='utf-8-sig').read().strip()):
        L = b.split('\n'); t0, t1 = [ts(x) for x in L[1].split(' --> ')]; text = ''.join(L[2:])
        ps = pauses(t0, t1); ph = Line(text, t0, t1, ps, maxl).phrases()
        tot = sum(wlen(p) for p in ph); used = set(); starts = [t0]; acc = 0
        for p in ph[:-1]:
            acc += wlen(p); e0 = t0 + (t1 - t0) * acc / tot
            cand = [(abs(e - e0), k, e) for k, (_, e) in enumerate(ps) if k not in used and abs(e - e0) < 0.9 and e > starts[-1] + 0.4]
            if cand: _, k, e = min(cand); used.add(k); starts.append(e - 0.05); aligned += 1
            else: starts.append(max(e0, starts[-1] + 0.4)); est += 1
        starts.append(t1)
        seg = [[starts[i], starts[i + 1], p] for i, p in enumerate(ph)]
        i = 0
        while i < len(seg):                      # 太短的行與相鄰行合併（不超過字數上限）
            if seg[i][1] - seg[i][0] < MIN_DUR and len(seg) > 1:
                j = i - 1 if i > 0 and (i == len(seg) - 1 or seg[i - 1][1] - seg[i - 1][0] < seg[i + 1][1] - seg[i + 1][0]) else i + 1
                a_, b_ = sorted((i, j)); merged = seg[a_][2] + seg[b_][2]
                if wlen(clean(merged)) <= maxl:
                    seg[a_:b_ + 1] = [[seg[a_][0], seg[b_][1], merged]]; i = a_; continue
            i += 1
        cues += [[x, y, clean(t)] for x, y, t in seg]
    return cues, aligned, est


def a_t(x): h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60; return f"{h}:{m:02d}:{s:05.2f}"
def s_t(x):
    ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def write(cues, fmt, out_ass, out_srt, font):
    F = FORMATS[fmt]; W, H = F["res"]
    hdr = (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\nWrapStyle: 2\n\n[V4+ Styles]\n"
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
           "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
           f"Style: Default,{font},{F['size']},&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,1,0,1,"
           f"{F['outline']},{F['shadow']},2,{F['ml']},{F['mr']},{F['mv']},1\n\n[Events]\n"
           "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    open(out_ass, 'w', encoding='utf-8').write(hdr + ''.join(f"Dialogue: 0,{a_t(a)},{a_t(b)},Default,,0,0,0,,{t}\n" for a, b, t in cues))
    open(out_srt, 'w', encoding='utf-8').write(''.join(f"{i}\n{s_t(a)} --> {s_t(b)}\n{t}\n\n" for i, (a, b, t) in enumerate(cues, 1)))


def ff_path(p):   # ffmpeg 濾鏡參數裡的路徑：Windows 磁碟代號的冒號要跳脫
    return p.replace('\\', '/').replace(':', '\\:').replace("'", "\\'")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proj"); ap.add_argument("--format", default="landscape", choices=list(FORMATS))
    ap.add_argument("--srt"); ap.add_argument("--narration"); ap.add_argument("--video"); ap.add_argument("--no-burn", action="store_true", help="相容舊指令；2.13.0 起預設即不燒錄")
    ap.add_argument("--burn", action="store_true", help="另外燒錄嵌入字幕版（僅使用者要求時）")
    a = ap.parse_args(); proj = os.path.abspath(a.proj); mid = os.path.join(proj, "2_製作中")
    srt = a.srt or (sorted(glob.glob(os.path.join(mid, "字幕", "字幕_zh-TW_gemini.srt"))) or
                    sorted(glob.glob(os.path.join(mid, "字幕", "字幕_zh-TW_*.srt")), key=os.path.getmtime))[-1]
    wav = a.narration or os.path.join(mid, "剪輯專案", "build", "narration_norm.wav")
    win = sys.platform.startswith("win")
    font, fdir = ("Microsoft JhengHei", "C:/Windows/Fonts") if win else ("Noto Sans CJK TC", "/usr/share/fonts/opentype/noto")
    F = FORMATS[a.format]
    cues, aligned, est = make_cues(srt, wav, F["maxl"])
    base = os.path.join(mid, "字幕", "字幕_zh-TW_單行" + ("_shorts" if a.format == "shorts" else ""))
    write(cues, a.format, base + ".ass", base + ".srt", font)
    print(f"單行字幕 {len(cues)} 行（對齊停頓 {aligned}、字數估計 {est}；最長 {max(wlen(t) for _, _, t in cues):.0f} 字）→ {base}.srt")
    if a.no_burn or not a.burn: return
    video = a.video or max([p for p in glob.glob(os.path.join(proj, "3_製作後", "輸出成品", "*_完整版.mp4"))], key=os.path.getmtime)
    out = video[:-4] + "_單行字幕.mp4"; k = 2
    while os.path.exists(out): out = video[:-4] + f"_單行字幕_{k}.mp4"; k += 1
    vf = f"subtitles='{ff_path(base + '.ass')}':fontsdir='{ff_path(fdir)}'"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", out], check=True)
    print("燒錄版：", out)


if __name__ == "__main__":
    main()
