"""旁白聲線一致性檢核（2.17.0）：逐句比對音高、音色亮度與頻譜特徵，找出跟全片其他句子不像的句子，並列出要人工聽的時間點。

背景：Gemini TTS（Achird）每次產生的語氣、音高略有不同，一段產生得較長時，後半段偶爾會「聲線飄掉」；
不同次產生的段落接在一起，也可能聽得出換了一個人。2026-10-30《免費 AI 大洗牌》使用者在 2:40、4:18、6:24 聽出不一致。

重要限制（請照實告訴使用者）：這是「篩選工具」，不是判決。2026-10-30 用它檢查上述那一版時，使用者聽出的三處都沒有被判為偏離；
它抓得到的是整句平均音高、亮度、音色明顯偏掉的句子，抓不到句子內的細微變化或聽感上的「換人」。
所以流程一律是：工具篩選 → 修掉偏離句 → 把「工具標記的句子＋不同次產生的接縫」列給使用者實際聽 → 使用者聽到不一致的幕整幕重做，直到使用者確認一致。

用法：
  python voice_consistency_check.py <旁白.wav> --timing <timing.json> [--offset 4] [--threshold 2.5] [--json] [--report 報告.md]
  python voice_consistency_check.py <旁白.wav> --srt <字幕.srt> [--offset 0] ...
  python voice_consistency_check.py <旁白.wav> --timing <timing.json> --joints 171.8,228.4  # 另外列出接縫時間點
輸入：
  --timing  JSON：{"S01": [[開始秒, 結束秒], ...], "S02": [...]}（旁白軌時間；motion-explainer 的 timing_global.json 即此格式）
  --srt     改用字幕的每一行當作一句（時間為字幕時間，請配合 --offset 換算回旁白軌）
  --offset  報告顯示時間＝旁白時間＋offset（例如正片前有 4 秒片頭就填 4），方便直接對照成片時間
  --joints  不同次產生的旁白接在一起的位置（旁白軌秒數，逗號分隔）；報告會把前後各一句列入人工聆聽清單
需要：pip install numpy soundfile librosa

判定方法（每句，至少 0.8 秒才算）：
  1. 音高：librosa.yin 估計 F0（60–300 Hz），只取較大聲的一半畫格，取中位數。
  2. 亮度：頻譜重心（spectral centroid）中位數，只取較大聲的 60% 畫格。
  3. 音色：MFCC 第 1–7 維平均值。
  以全片所有句子的中位數與 MAD（中位數絕對離差 ×1.4826）當基準，算每句的穩健 z 分數；
  音高、亮度取絕對值，音色取 7 維 z 的均方根；三者取最大值為「偏離分數」，超過 threshold（預設 2.5）標記 <<<。
"""
import argparse, json, re, sys
import numpy as np
import soundfile as sf


def load_srt(path):
    out = []
    for blk in re.split(r"\n\s*\n", open(path, encoding="utf-8-sig").read().strip()):
        lines = blk.strip().splitlines()
        if len(lines) < 2 or "-->" not in lines[1]:
            continue
        a, b = [x.strip() for x in lines[1].split("-->")]
        def sec(x):
            h, m, r = x.replace(",", ".").split(":")
            return int(h) * 3600 + int(m) * 60 + float(r)
        out.append(("SRT", len(out), sec(a), sec(b), " ".join(lines[2:])))
    return out


def load_timing(path):
    T = json.load(open(path, encoding="utf-8"))
    out = []
    for sc in sorted(k for k in T if isinstance(T[k], list)):
        for i, (a, b) in enumerate(T[sc]):
            out.append((sc, i, float(a), float(b), ""))
    return out


def features(seg, sr):
    import librosa
    S = np.abs(librosa.stft(seg, n_fft=1024, hop_length=256))
    rms = librosa.feature.rms(S=S, frame_length=1024)[0]
    loud = rms > np.percentile(rms, 40)
    cen = librosa.feature.spectral_centroid(S=S, sr=sr)[0]
    mf = librosa.feature.mfcc(S=librosa.power_to_db(librosa.feature.melspectrogram(S=S ** 2, sr=sr)), n_mfcc=13)
    f0 = librosa.yin(seg, fmin=60, fmax=300, sr=sr, frame_length=1024, hop_length=256)
    n = min(len(f0), len(rms))
    f0 = f0[:n][rms[:n] > np.percentile(rms[:n], 50)]
    return float(np.median(f0)), float(np.median(cen[loud])), mf[:, loud].mean(1)


def robust_z(x, ref):
    med = np.median(ref, 0)
    mad = np.median(np.abs(ref - med), 0) * 1.4826 + 1e-6
    return (x - med) / mad


def fmt(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("wav")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--timing"); g.add_argument("--srt")
    ap.add_argument("--offset", type=float, default=0.0)
    ap.add_argument("--threshold", type=float, default=2.5)
    ap.add_argument("--joints", default="")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--report")
    a = ap.parse_args()

    y, sr = sf.read(a.wav)
    if y.ndim > 1:
        y = y.mean(1)
    items = load_timing(a.timing) if a.timing else load_srt(a.srt)
    rows = []
    for sc, i, s, e, txt in items:
        seg = y[int(s * sr):int(e * sr)]
        if len(seg) < sr * 0.8:
            continue
        f0, cen, mf = features(seg.astype(np.float32), sr)
        rows.append(dict(scene=sc, idx=i, start=s, end=e, text=txt, f0=f0, centroid=cen, mfcc=mf))
    if len(rows) < 5:
        sys.exit("句子太少（少於 5 句），無法建立基準。")
    F0 = np.array([r["f0"] for r in rows]); C = np.array([r["centroid"] for r in rows]); M = np.array([r["mfcc"] for r in rows])
    zf, zc, zm = robust_z(F0, F0), robust_z(C, C), robust_z(M, M)
    for r, a1, a2, a3 in zip(rows, zf, zc, zm):
        r["z_f0"] = float(a1); r["z_centroid"] = float(a2); r["z_mfcc"] = float(np.sqrt(np.mean(a3[1:8] ** 2)))
        r["score"] = max(abs(r["z_f0"]), abs(r["z_centroid"]), r["z_mfcc"])
        r["flag"] = r["score"] > a.threshold
        del r["mfcc"]

    joints = [float(x) for x in a.joints.split(",") if x.strip()]
    listen = [r for r in rows if r["flag"]]
    for j in joints:
        before = [r for r in rows if r["end"] <= j + 0.05]
        after = [r for r in rows if r["start"] >= j - 0.05]
        listen += ([before[-1]] if before else []) + ([after[0]] if after else [])
    seen = set(); listen_u = []
    for r in sorted(listen, key=lambda r: r["start"]):
        k = (r["scene"], r["idx"])
        if k not in seen:
            seen.add(k); listen_u.append(r)

    if a.json:
        print(json.dumps(dict(rows=rows, listen=[(fmt(r["start"] + a.offset), r["scene"], r["idx"]) for r in listen_u]), ensure_ascii=False, indent=1))
    else:
        print(f"共 {len(rows)} 句；基準音高中位數 {np.median(F0):.0f} Hz、亮度中位數 {np.median(C):.0f} Hz；門檻 {a.threshold}")
        for r in rows:
            mark = "  <<< 偏離" if r["flag"] else ""
            print(f"{fmt(r['start'] + a.offset)}  {r['scene']}-{r['idx']}  音高 {r['f0']:.0f}({r['z_f0']:+.1f})  亮度 {r['centroid']:.0f}({r['z_centroid']:+.1f})  音色 {r['z_mfcc']:.1f}{mark}")
        print(f"\n偏離句 {sum(r['flag'] for r in rows)} 句；人工聆聽清單 {len(listen_u)} 處：")
        for r in listen_u:
            why = "偏離" if r["flag"] else "接縫"
            print(f"  {fmt(r['start'] + a.offset)}  {r['scene']}-{r['idx']}（{why}）")
    if a.report:
        with open(a.report, "w", encoding="utf-8") as f:
            f.write("# 聲線一致性檢核\n\n> 工具篩選結果，不是判決；最後以人工聆聽為準。\n\n")
            f.write(f"- 檔案：{a.wav}\n- 句數：{len(rows)}；門檻：{a.threshold}；時間已加 offset {a.offset} 秒\n\n")
            f.write("## 人工聆聽清單\n\n| 時間 | 句子 | 原因 |\n|---|---|---|\n")
            for r in listen_u:
                f.write(f"| {fmt(r['start'] + a.offset)} | {r['scene']}-{r['idx']} | {'偏離（分數 %.1f）' % r['score'] if r['flag'] else '不同次產生的接縫'} |\n")
            f.write("\n## 逐句數值\n\n| 時間 | 句子 | 音高 Hz (z) | 亮度 Hz (z) | 音色 z | 標記 |\n|---|---|---|---|---|---|\n")
            for r in rows:
                f.write(f"| {fmt(r['start'] + a.offset)} | {r['scene']}-{r['idx']} | {r['f0']:.0f} ({r['z_f0']:+.1f}) | {r['centroid']:.0f} ({r['z_centroid']:+.1f}) | {r['z_mfcc']:.1f} | {'偏離' if r['flag'] else ''} |\n")
    return 1 if any(r["flag"] for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
