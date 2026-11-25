"""旁白摩擦聲／爆音／句中換氣檢核（2.15.0；2.41.0 加句中換氣）：找出配音中「不在說話」卻很大聲的短促雜音，選擇性把它們靜音。

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
  5. 2.41.0：相隔不到 60 ms 的爆音併成一段再判斷（檔尾爆音常被一格靜音切成兩半，舊版因此漏抓）。
  6. 2.41.0「句中換氣／擦聲」：兩個說話段之間、比人聲低 14–42 dB、連續 0.12 秒以上而且不是濁音（沒有音高）的聲響，
     多半是吸氣或唇齒擦聲。Gemini 快語速時句間停頓只有約 0.2 秒，換氣緊貼前後的字，tidy() 與第 2 條都抓不到；
     2026-11-25《尼莫點》CH01 使用者聽出。--fix 會把它靜音，但前後各留 30 ms 給字的收尾與起音。
     有音高的輕聲字（句尾「嗎」「了」）列為「其他」不動。
不改原檔；修正版另存。修完要重跑一次確認「摩擦／爆音」「句中換氣／擦聲」都是 0 處；只做靜音不剪長度，時間軸不變。
"""
import argparse, json, sys
import numpy as np
import soundfile as sf


FIXABLE = ("摩擦／爆音", "句中換氣／擦聲")


def voiced_ratio(seg, sr):
    """30 ms 一窗，自相關在 70–400 Hz 有明顯峰值的窗所占比例（濁音＝有音高的語音）。"""
    w = int(0.03 * sr); lo, hi = int(sr / 400), int(sr / 70); v = t = 0
    for k in range(0, len(seg) - w, w // 2):
        s = seg[k:k + w] - seg[k:k + w].mean(); ac = np.correlate(s, s, "full")[w - 1:]
        if ac[0] <= 0:
            continue
        t += 1; v += ac[lo:hi].max() / ac[0] > 0.5
    return v / t if t else 0.0


def breaths(y, sr, speech_med):
    """句中換氣／擦聲：說話段之間、低於人聲 14 dB 的谷裡，高於 −42 dB 的部分連續 ≥ 0.12 秒且不是濁音。"""
    hop = int(sr * 0.01); n = len(y) // hop
    db = 20 * np.log10(np.sqrt((y[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    speech = db >= speech_med - 14; audible = db > speech_med - 42
    out, i = [], 0
    while i < n:
        if speech[i]:
            i += 1; continue
        j = i
        while j < n and not speech[j]:
            j += 1
        a = i + 3 if i > 0 else i; b = j - 3 if j < n else j       # 前後各留 30 ms
        k = a
        while k < b:                                              # 連續的聲響（中間斷不到 30 ms 視為同一段）
            if not audible[k]:
                k += 1; continue
            t0 = t1 = k
            while k < b and (audible[k] or audible[k:min(b, k + 3)].any()):
                if audible[k]: t1 = k + 1
                k += 1
            if (t1 - t0) * 0.01 >= 0.12:
                kind = "其他" if voiced_ratio(y[t0 * hop:t1 * hop], sr) > 0.4 else "句中換氣／擦聲"
                out.append({"t0": round(t0 * 0.01, 2), "t1": round(t1 * 0.01, 2), "dur": round((t1 - t0) * 0.01, 2),
                            "peak_rel_db": round(float(db[t0:t1].max() - speech_med), 1), "kind": kind})
        i = j
    return out


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
            while j < n and (not quiet[j] or not quiet[j:j + 3].all()):   # 相隔 ≤ 60 ms 的爆音併成一段
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
    events += breaths(y, sr, speech_med)
    events.sort(key=lambda e: e["t0"])
    return events, float(speech_med)


def mute(y, sr, ev):
    """把「摩擦／爆音」「句中換氣／擦聲」靜音（20 ms 淡入淡出），長度不變。y 可為單聲道或多聲道。"""
    out = y.copy(); fade = int(sr * 0.02); fixed = 0
    ramp = lambda a, b: np.linspace(a, b, fade) if out.ndim == 1 else np.linspace(a, b, fade)[:, None]
    for e in ev:
        if e["kind"] not in FIXABLE:
            continue
        pad = 0.03 if e["kind"] == "摩擦／爆音" else 0.0
        a0 = max(0, int((e["t0"] - pad) * sr)); a1 = min(len(out), int((e["t1"] + pad) * sr))
        out[a0:a1] = 0
        if a0 - fade > 0: out[a0 - fade:a0] *= ramp(1, 0)
        if a1 + fade < len(out): out[a1:a1 + fade] *= ramp(0, 1)
        fixed += 1
    return out, fixed


def clean(y, sr):
    """給其他程式呼叫：單聲道 float 陣列 → (去雜音後的陣列, 靜音處數)。"""
    ev, _ = analyse(y, sr)
    return mute(y, sr, ev)


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
        out, fixed = mute(y, sr, ev)
        sf.write(a.fix, out if out.shape[1] > 1 else out[:, 0], sr, subtype="PCM_16")
        print(f"已靜音 {fixed} 處 → {a.fix}（「其他」類請人工聽過再處理）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
