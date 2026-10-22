"""旁白摩擦聲／爆音檢核（2.15.0）：找出配音中「不在說話」卻很大聲的短促雜音，選擇性把它們靜音。

背景：Gemini TTS 的 WAV 在檔尾（有時檔頭）常帶一段 0.1–0.2 秒的寬頻爆音（聽起來像摩擦聲、紙張擦過），
音量可能比人聲還大；頭尾只做幾十毫秒淡出蓋不掉。2026-10-22《地球離太陽最近，為什麼是冬天？》三段配音的檔尾都有。

用法：
  python narration_noise_check.py <旁白.wav>                     # 只檢查，列出可疑時間點
  python narration_noise_check.py <旁白.wav> --fix 輸出.wav       # 把可疑段落靜音（前後 20 ms 淡入淡出）後另存
  python narration_noise_check.py <旁白.wav> --json               # 機器可讀輸出
選項：--min-gap 0.2（判定「不在說話」所需的前後靜音秒數）、--rel -30（比人聲中位數低多少 dB 以內才算可疑）

判定規則：
  1. 以 20 ms 為一格算音量，人聲中位數為基準。
  2. 「孤立聲響」：音量 ≥ 人聲中位數 + rel，持續 0.04–0.6 秒，而且前後各至少 min-gap 秒是安靜的（不是句子的一部分）。
  3. 頻譜高頻占比高（2.5 kHz 以上能量 > 1 kHz 以下）者標為「摩擦／爆音」；低頻為主者標為「其他（可能是換氣或語助詞）」。
  4. 只自動修「摩擦／爆音」；「其他」只列出，請人工聽過再決定，避免誤刪真正的語音。
不改原檔；修正版另存。修完要重跑一次確認 0 處，並重新檢查字幕時間（本工具不改時間軸）。
"""
import argparse, json, sys
import numpy as np
import soundfile as sf


def analyse(y, sr, min_gap=0.2, rel=-30.0):
    hop = int(sr * 0.02)
    n = len(y) // hop
    fr = y[: n * hop].reshape(n, hop)
    db = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
    loud = db > -60
    speech_med = np.median(db[loud]) if loud.any() else -30
    thr = speech_med + rel
    quiet = db < max(thr - 6, -62)
    events, i = [], 0
    g = int(round(min_gap / 0.02))
    while i < n:
        if db[i] >= thr and not quiet[i]:
            j = i
            while j < n and not quiet[j]:
                j += 1
            dur = (j - i) * 0.02
            before = quiet[max(0, i - g):i].all() if i >= g else (i == 0 or quiet[:i].all())
            after = quiet[j:j + g].all() if j + g <= n else quiet[j:].all()
            if 0.04 <= dur <= 0.6 and before and after:
                seg = y[i * hop:j * hop]
                spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2
                f = np.fft.rfftfreq(len(seg), 1 / sr)
                hi, lo = spec[f > 2500].sum(), spec[(f > 80) & (f < 1000)].sum()
                kind = "摩擦／爆音" if hi > lo else "其他"
                events.append({"t0": round(i * 0.02, 2), "t1": round(j * 0.02, 2), "dur": round(dur, 2),
                               "peak_rel_db": round(float(db[i:j].max() - speech_med), 1), "kind": kind})
            i = j
        else:
            i += 1
    return events, float(speech_med)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("wav"); ap.add_argument("--fix"); ap.add_argument("--json", action="store_true")
    ap.add_argument("--min-gap", type=float, default=0.2); ap.add_argument("--rel", type=float, default=-30.0)
    a = ap.parse_args()
    y, sr = sf.read(a.wav, always_2d=True)
    mono = y.mean(1)
    ev, med = analyse(mono, sr, a.min_gap, a.rel)
    if a.json:
        print(json.dumps({"speech_median_db": round(med, 1), "events": ev}, ensure_ascii=False, indent=1))
    else:
        print(f"人聲中位數 {med:.1f} dB；可疑聲響 {len(ev)} 處")
        for e in ev:
            m, s = divmod(e["t0"], 60)
            print(f"  {int(m)}:{s:05.2f}  長 {e['dur']:.2f} 秒  比人聲 {e['peak_rel_db']:+.1f} dB  {e['kind']}")
    if a.fix:
        out = y.copy(); fade = int(sr * 0.02); fixed = 0
        for e in ev:
            if e["kind"] != "摩擦／爆音":
                continue
            a0 = max(0, int((e["t0"] - 0.03) * sr)); a1 = min(len(out), int((e["t1"] + 0.03) * sr))
            out[a0:a1] = 0
            if a0 - fade > 0: out[a0 - fade:a0] *= np.linspace(1, 0, fade)[:, None]
            if a1 + fade < len(out): out[a1:a1 + fade] *= np.linspace(0, 1, fade)[:, None]
            fixed += 1
        sf.write(a.fix, out if out.shape[1] > 1 else out[:, 0], sr, subtype="PCM_16")
        print(f"已靜音 {fixed} 處 → {a.fix}（「其他」類請人工聽過再處理）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
