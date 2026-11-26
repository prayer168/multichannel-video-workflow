"""用「有旁白提示」的逐字對齊重切 Gemini 整組配音（gemini_tts.py 的 split 用無提示 whisper，遇到罕見詞會整組切偏）。
用法：python resplit_voice.py <raw_*.wav> <words.json（narration_word_timing.py 對 raw 的結果）> <輸出資料夾>
切法與 gemini_tts.split 相同：句間 ±0.12 s 找最安靜處下刀 → tidy() 去換氣 → narration_noise_check.clean() → 5 ms 淡入淡出。
2026-11-25 CH03 第一組：原切點把 S034 結尾「不同顏色的食用色素」切掉、開頭混進 S033「與鹽度」。
"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gemini_tts as g  # noqa: E402
import narration_noise_check as nnc  # noqa: E402


def main():
    raw, words, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    y, sr = g.read_wav(raw)
    sents = json.load(open(words, encoding='utf-8'))['sentences']
    dur = len(y) / sr
    cuts = [max(0.0, sents[0]['start'] - 0.25)]
    for k in range(len(sents) - 1):
        e, s = sents[k]['end'], sents[k + 1]['start']
        lo, hi = max(min(e, s) - 0.12, sents[k]['start'] + 0.1), min(max(e, s) + 0.12, sents[k + 1]['end'] - 0.1)
        cuts.append(g.quietest(y, sr, lo, hi) if hi > lo else (e + s) / 2)
    cuts.append(min(dur, sents[-1]['end'] + 0.35))
    rep = []
    for k, s in enumerate(sents):
        seg, n = nnc.clean(g.tidy(y[int(cuts[k] * sr): int(cuts[k + 1] * sr)], sr), sr)
        g.write_wav(out / f"{s['id']}.wav", seg, sr)
        rep.append(dict(key=s['id'], start=round(cuts[k], 2), end=round(cuts[k + 1], 2), muted=n))
    json.dump(rep, open(out / f'resplit_{raw.stem}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\n'.join(f"{r['key']} {r['start']:.2f}–{r['end']:.2f} muted={r['muted']}" for r in rep))


if __name__ == '__main__':
    main()
