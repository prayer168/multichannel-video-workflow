"""把旁白每個字的實際發音時間寫進時間軸（event.ct：相對該句配音起點的影格，長度＝句子字數）。
動畫用 kwAt() 找關鍵詞時改讀 ct，不再用字數比例估計（2026-11-26 使用者：旁白比動畫早約 1 秒）。

用法：
  python char_marks.py <timing_CHxx.json> mix <words.json>
      words.json 是對「成片混音」跑 narration_word_timing.py 的結果（章節絕對秒）
  python char_marks.py <timing_CHxx.json> raw <voice 資料夾> <raw1.wav> <words1.json> [<raw2.wav> <words2.json> ...]
      words 是對「整組原始配音」跑的結果；每句音檔在原始配音中的位置用互相關找出
whisper 常把句首幾個字攤到前段靜音（每字 ≥0.3 s）→ 句首改用第一個可信字往回以 0.2 s／字外推。
"""
import json, sys, wave
from pathlib import Path
import numpy as np

FPS = 30


def read(p):
    with wave.open(str(p)) as w:
        sr = w.getframerate()
        y = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        if w.getnchannels() == 2:
            y = y.reshape(-1, 2).mean(1)
    return y, sr


def locate(seg, raw):
    """seg 在 raw 中的起點（樣本）。"""
    n = len(raw) + len(seg)
    c = np.fft.irfft(np.fft.rfft(raw, n) * np.conj(np.fft.rfft(seg, n)), n)
    return int(np.argmax(c[: len(raw)]))


def per_char(sent, n, offset_s):
    """回傳長度 n 的秒數陣列（相對該句音檔起點）。"""
    pts = sorted((c['j'], c['t'] - offset_s) for c in sent['chars'] if c.get('matched') and c['j'] < n)
    if not pts:
        return None
    # 跳過被攤開的句首字：相鄰可信字間隔 ≥0.3 s 視為內插
    k = 0
    while k + 1 < len(pts) and pts[k + 1][1] - pts[k][1] >= 0.3 * (pts[k + 1][0] - pts[k][0]) and pts[k + 1][1] - pts[k][1] >= 0.3:
        k += 1
    pts = pts[k:]
    j0, t0 = pts[0]
    xs = [j for j, _ in pts]
    ts = [t for _, t in pts]
    out = np.interp(np.arange(n), xs, ts)
    for j in range(j0):
        out[j] = max(0.0, t0 - 0.2 * (j0 - j))
    return out


def main():
    timing = Path(sys.argv[1]); mode = sys.argv[2]
    t = json.load(open(timing, encoding='utf-8'))
    events = {e['id']: e for s in t['shots'] for e in s['events']}
    done = 0
    if mode == 'mix':
        sents = {s['id']: s for s in json.load(open(sys.argv[3], encoding='utf-8'))['sentences']}
        for k, e in events.items():
            if k in sents:
                arr = per_char(sents[k], len(e['text']), e['from'] / FPS)
                if arr is not None:
                    e['ct'] = [int(round(x * FPS)) for x in arr]; done += 1
    else:
        voice = Path(sys.argv[3]); pairs = sys.argv[4:]
        for raw_p, words_p in zip(pairs[::2], pairs[1::2]):
            raw, sr = read(raw_p)
            for s in json.load(open(words_p, encoding='utf-8'))['sentences']:
                e = events.get(s['id'])
                if not e:
                    continue
                seg, sr2 = read(voice / f"{s['id']}.wav")
                assert sr2 == sr
                off = locate(seg, raw) / sr
                arr = per_char(s, len(e['text']), off)
                if arr is not None:
                    e['ct'] = [int(round(x * FPS)) for x in arr]; done += 1
    json.dump(t, open(timing, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{timing.name}：{done}/{len(events)} 句寫入逐字時間')


if __name__ == '__main__':
    main()
