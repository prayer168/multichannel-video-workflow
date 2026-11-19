"""逐句旁白配音：Gemini（gemini-3.8-flash-tts／Achird＋固定 Style），整組產生後切回「一句一檔」。

用法（命令列）：
  python gemini_tts.py --lines 旁白逐句.json --out 配音/逐句 [--terms "Playwright、FFmpeg"]
  旁白逐句.json：{"lines": [["v01", "第一句。"], ["v02", "第二句！"]]}，可另加 "terms"。
  也可在 Python 裡呼叫 prepare(blocks, work)：blocks = [(組別 id, [(句 id, 稿子, 輸出 wav 路徑)])]，
  組別 id 第一個字母不同就分開請求（例：開場 c01…、正片 e01…）。

- 照 references/fixed-settings.md 第一節：模型、聲音、Style 一字不改，只換最後一行術語（style(terms)）。
- 每次請求一組（約 90 秒、400 字內），一句一行；同一組的句子一次產生，聲線最一致。
- 產生後用 whisper.cpp 逐字對齊（同資料夾 narration_word_timing.py），在相鄰兩句之間找音量最低處切開，
  每句再用 tidy() 去掉換氣與唇齒擦聲。對齊率、離稿字與「沒念到的句子」寫在 <out>/report.json。
- 需要環境變數 GEMINI_API_KEY（只在本機讀取，不寫進任何檔案；setx 設的也讀得到）。
  免費方案每分鐘 3 次、每天 10 次；已產生的組與句會跳過，隔天重跑從缺的接續。
- 跟 make_narration.py 的分工：make_narration 產生「兩幕一檔」交給 build.py；本工具產生「一句一檔」，
  給逐句排時間的剪輯（自寫合成程式、HyperFrames、計時賽之類需要把每句放在指定秒數的影片）。
- 來源：《水裡的橋》幕後教學（2026-11-17，去擦聲、跳句偵測在該片實測），2026-11-17 收進技能。
"""

import base64
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import narration_word_timing as nwt  # noqa: E402

MODEL = "gemini-3.8-flash-tts"
VOICE = "Achird"


def style(terms="YouTube"):
    """fixed-settings.md 第一節 Style 全文；只有最後一行的術語清單會換。"""
    return (
        "自然的臺灣國語男聲，一位四十歲左右的自然科老師，在教師研習中耐心講解：溫暖、厚實、穩重，帶著親切的微笑感。\n"
        "是「講」不是「唸」：句子流暢連貫，語速稍快、輕快有精神（每分鐘約 270 到 290 字），重要概念前稍微停頓，「……」處停頓約 0.8 秒，\n"
        "每一行結尾停頓約半秒，「好，」開頭的句子前停頓稍長。重點詞自然加重，尾音自然收住不拖長。不要播報腔、廣告腔、朗誦腔。\n"
        f"英文術語用自然的英文發音，不要逐字母拼讀：{terms}。"
    )


STYLE = style()
GROUP_CHARS = 400      # 每組字數上限（約 90 秒）
WAIT = 21.0            # 兩次請求間隔


def spoken_for_gemini(text):
    return text.replace("T T S", "TTS")


def groups(blocks):
    """blocks: [(nid, [(key, spoken, path)])] → 依序分組；開場（c）與正片（e）不同組。"""
    out, cur, n, prefix = [], [], 0, None
    for nid, chunks in blocks:
        size = sum(len(s) for _, s, _ in chunks)
        if cur and (nid[0] != prefix or n + size > GROUP_CHARS):
            out.append(cur)
            cur, n = [], 0
        cur.append((nid, chunks))
        n += size
        prefix = nid[0]
    if cur:
        out.append(cur)
    return out


def transcript(group):
    lines = []
    for _, chunks in group:
        line = ""
        for i, (_, s, _) in enumerate(chunks):
            line += spoken_for_gemini(s).strip()
            if line.endswith(("。", "？", "！")) or i == len(chunks) - 1:
                lines.append(line)
                line = ""
    return "\n".join(lines)


def request(text, key):
    prompt = f"## Style:\n{STYLE}\n\n## Transcript:\n{text}"
    body = dict(contents=[dict(role="user", parts=[dict(text=prompt)])],
                generationConfig=dict(temperature=1, responseModalities=["audio"],
                                      speechConfig=dict(voiceConfig=dict(prebuiltVoiceConfig=dict(voiceName=VOICE)))))
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                resp = json.load(r)
            break
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                raise SystemExit(f"Gemini HTTP {e.code}：額度用完或權限不足，明天再執行會從缺的組接續。")
            if e.code < 500 or attempt == 2:
                raise SystemExit(f"Gemini HTTP {e.code}：{e.read()[:300]!r}")
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(WAIT)
    part = resp["candidates"][0]["content"]["parts"][0]["inlineData"]
    m = re.search(r"rate=(\d+)", part.get("mimeType", ""))
    pcm = base64.b64decode(part["data"])
    if pcm[:4] == b"RIFF":
        pcm = pcm[44:]
    return pcm, int(m.group(1)) if m else 24000


def clean(y, sr):
    """清頭尾雜訊（同 multichannel build.py clean_tts：開頭約 10 ms 喀聲、結尾約 130 ms 滿格雜訊）。"""
    h = int(0.01 * sr)
    n = len(y) // h
    pk = 20 * np.log10(np.abs(y[: n * h]).reshape(n, h).max(1) + 1e-9)
    k = 0
    while k < min(n, 5) and pk[k] > -12:
        k += 1
    if 0 < k < 5 and pk[k] < -35:
        y = y.copy()
        y[: (k + 1) * h] = 0
    j = n
    while j > 0 and pk[j - 1] > -6:
        j -= 1
    if j < n and (n - j) <= 40 and j > 0 and pk[max(0, j - 5): j].max() < -30:
        y = y[: j * h]
    return y


def read_wav(path):
    with wave.open(str(path)) as w:
        sr = w.getframerate()
        y = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return y, sr


def write_wav(path, y, sr):
    f = int(0.005 * sr)
    y = y.copy()
    if len(y) > 2 * f:
        r = np.linspace(0, 1, f, dtype=np.float32)
        y[:f] *= r
        y[-f:] *= r[::-1]
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


def quietest(y, sr, a, b):
    """a–b 秒之間，30 ms 平滑後音量最低的位置（秒）。"""
    h = int(0.01 * sr)
    i0, i1 = max(0, int(a * sr) // h), min(len(y) // h, int(b * sr) // h)
    if i1 - i0 < 2:
        return (a + b) / 2
    e = np.sqrt((y[i0 * h: i1 * h].reshape(-1, h) ** 2).mean(1))
    e = np.convolve(e, np.ones(3) / 3, mode="same")
    return (i0 + int(np.argmin(e)) + 0.5) * h / sr


def simplified(s):
    """whisper 中文輸出是簡體：比對前把稿子轉成簡體（Windows LCMapStringEx，逐字一對一，不改長度）。"""
    import ctypes
    n = len(s)
    buf = ctypes.create_unicode_buffer(n + 1)
    ctypes.windll.kernel32.LCMapStringEx("zh-CN", 0x02000000, s, n, buf, n + 1, None, None, 0)
    return buf.value if len(buf.value) == n else s


def run_whisper(raw, work):
    """不給提示詞：實測加了定稿提示，句中逗號處的 token 時間會偏 0.5 秒以上（切到「第一版｜試拍」中間）。"""
    import subprocess
    exe, model = nwt.WHISPER_DIR / "main.exe", nwt.WHISPER_DIR / "ggml-medium.bin"
    wav, out = work / "_asr16k.wav", work / f"asr_{Path(raw).stem}"
    if out.with_suffix(".json").exists():
        return out.with_suffix(".json")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-ar", "16000", "-ac", "1", str(wav)], check=True)
    subprocess.run([str(exe), "-m", str(model), "-l", "zh", "-ojf", "-dtw", "medium", "-of", str(out), "-f", str(wav)],
                   check=True, capture_output=True)
    return out.with_suffix(".json")


def tidy(y, sr):
    """去掉逐句檔裡的換氣與擦聲（2026-11-17 使用者聽出「擦聲」）。

    以 10 ms 為一格，把相隔不到 60 ms 的有聲格併成「段」。說話段：峰值在句中位數 −6 dB 以內，
    或在 −14 dB 以內且以低頻為主（輕聲的句尾字）。其他段（吸氣、唇齒擦聲，高頻為主、比人聲低 8–30 dB）
    以及短於 80 ms 的碎片（切到的下一個字開頭）一律靜音；頭尾只留到第一個／最後一個說話段。
    句首的擦音子音與後面的母音相連，屬同一段，不受影響。"""
    h = int(0.01 * sr)
    n = len(y) // h
    if n < 5:
        return y
    d = 20 * np.log10(np.sqrt((y[: n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)
    med = np.median(d[d > d.max() - 30])
    act = d > med - 35
    segs, i = [], 0
    while i < n:
        if not act[i]:
            i += 1
            continue
        j = i
        while j < n and (act[j] or act[j: j + 6].any()):
            j += 1
        seg = y[i * h: j * h]
        sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2
        f = np.fft.rfftfreq(len(seg), 1 / sr)
        hf = sp[f > 2500].sum() / (sp[f < 1000].sum() + 1e-12)
        peak = d[i:j].max() - med
        speech = (j - i) >= 8 and (peak >= -6 or (peak >= -14 and hf < 0.5))
        segs.append((i, j, speech))
        i = j
    keep = [(a, b) for a, b, s in segs if s]
    if not keep:
        return y
    out = np.zeros_like(y)
    fade = int(0.012 * sr)
    for a, b in keep:
        s, e = max(0, a * h - fade), min(len(y), b * h + fade)
        piece = y[s:e].copy()
        r = np.linspace(0, 1, min(fade, len(piece) // 2), dtype=np.float32)
        piece[: len(r)] *= r
        piece[len(piece) - len(r):] *= r[::-1]
        out[s:e] = piece
    s0 = max(0, keep[0][0] * h - int(0.03 * sr))
    e0 = min(len(y), keep[-1][1] * h + int(0.06 * sr))
    return out[s0:e0]


def split(raw, group, sr_y, report):
    y, sr = sr_y
    chunks = [c for _, cs in group for c in cs]
    rows = [{"id": key, "text": simplified(spoken_for_gemini(s))} for key, s, _ in chunks]
    asr = [(simplified(c), a, b) for c, a, b in nwt.asr_chars(run_whisper(raw, work=Path(raw).parent))]
    sents, ratio, diffs = nwt.align(rows, asr, 0)
    report.update(match_ratio=ratio, diffs=[d for d in diffs if len(d[0]) + len(d[1]) > 1][:40])
    missing = [d[0] for d in diffs if len(d[0]) >= 6 and not d[1]]
    if missing:   # 2026-11-17 實測：e11–e23 組整句「師父阿沅要在洪水裡，把徒弟阿行帶回岸邊。」沒念
        report["missing"] = missing
        print(f"  ⚠ 辨識不到的稿子：{missing}；刪掉 raw_*.wav 重新產生", flush=True)
    dur = len(y) / sr
    cuts = [max(0.0, sents[0]["start"] - 0.25)]
    for k in range(len(sents) - 1):
        e, s = sents[k]["end"], sents[k + 1]["start"]
        lo, hi = min(e, s) - 0.12, max(e, s) + 0.12
        lo = max(lo, sents[k]["start"] + 0.1)
        hi = min(hi, sents[k + 1]["end"] - 0.1)
        cuts.append(quietest(y, sr, lo, hi) if hi > lo else (e + s) / 2)
    cuts.append(min(dur, sents[-1]["end"] + 0.35))
    for k, (_, _, path) in enumerate(chunks):
        write_wav(path, tidy(y[int(cuts[k] * sr): int(cuts[k + 1] * sr)], sr), sr)
    report["chunks"] = [dict(key=c[0], start=round(cuts[k], 2), end=round(cuts[k + 1], 2))
                        for k, c in enumerate(chunks)]


def user_env(name):
    """setx 設定的變數要重開視窗才會出現在環境裡；直接讀 Windows 使用者環境變數。"""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            return winreg.QueryValueEx(k, name)[0]
    except (ImportError, OSError):
        return None


def prepare(blocks, work):
    """blocks: [(nid, [(key, spoken, path)])]；缺的逐句檔才會呼叫 API。"""
    work.mkdir(parents=True, exist_ok=True)
    rep_path = work / "report.json"
    reports = json.loads(rep_path.read_text(encoding="utf-8")) if rep_path.exists() else {}
    key = os.environ.get("GEMINI_API_KEY") or user_env("GEMINI_API_KEY")
    called = False
    for group in groups(blocks):
        if all(p.exists() for _, cs in group for _, _, p in cs):
            continue
        text = transcript(group)
        gid = f"{group[0][0]}-{group[-1][0]}_{hashlib.md5((MODEL + VOICE + STYLE + text).encode()).hexdigest()[:8]}"
        raw = work / f"raw_{gid}.wav"
        if not raw.exists():
            if not key:
                raise SystemExit("找不到 GEMINI_API_KEY，無法產生 Gemini 配音。")
            if called:
                time.sleep(WAIT)
            print(f"Gemini 配音 {gid}（{len(text)} 字）…", flush=True)
            pcm, sr = request(text, key)
            called = True
            y = np.frombuffer(pcm[: len(pcm) // 2 * 2], np.int16).astype(np.float32) / 32768
            write_wav(raw, clean(y, sr), sr)
        y, sr = read_wav(raw)
        chars = len(re.sub(r"[^一-鿿A-Za-z0-9]", "", text))
        rep = dict(chars=chars, seconds=round(len(y) / sr, 2), cpm=round(chars / (len(y) / sr) * 60))
        if len(y) / sr > chars / 250 * 60 * 1.3:
            rep["warning"] = "長度比字數應有的多 30% 以上，可能有離稿內容"
        split(raw, group, (y, sr), rep)
        reports[gid] = rep
        print(f"  {rep['seconds']} 秒，約 {rep['cpm']} 字／分，對齊率 {rep['match_ratio']}", flush=True)
        rep_path.write_text(json.dumps(reports, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    import argparse
    global STYLE
    ap = argparse.ArgumentParser(description="Gemini（Achird）逐句旁白：一組產生、對齊後切成一句一檔")
    ap.add_argument("--lines", required=True, help='JSON：{"lines": [["v01", "第一句。"], ...], "terms": "可省略"}')
    ap.add_argument("--out", required=True, help="輸出資料夾（<句 id>.wav、raw_*.wav、report.json）")
    ap.add_argument("--terms", help="Style 最後一行的英文術語清單（覆蓋 JSON 的 terms）")
    a = ap.parse_args()
    data = json.loads(Path(a.lines).read_text(encoding="utf-8"))
    STYLE = style(a.terms or data.get("terms") or "YouTube")
    out = Path(a.out)
    blocks = [(f"e{k:03d}", [(lid, text, out / f"{lid}.wav")]) for k, (lid, text) in enumerate(data["lines"])]
    prepare(blocks, out)
    missing = [p.name for _, cs in blocks for _, _, p in cs if not p.exists()]
    print("全部完成" if not missing else f"缺：{missing}")


if __name__ == "__main__":
    main()
