"""依 Remotion 時間軸把一章的配音疊成「純人聲軌」，給 narration_noise_check.py 做整章擦聲複檢（2.41.0）。

成片有背景音樂與音效，直接檢查成片會把音樂當雜音；逐檔檢查又看不到檔與檔接起來的地方。
所以每章做完，用同一份時間軸把配音照實際影格位置、實際音量疊成一軌，再跑檢查工具。

用法：
  python voice_stem_from_timing.py <timing_full.json> <章節 id> <remotion/public> <輸出.wav> [--cub-gain 0.63] [--fps 30]
  python narration_noise_check.py <輸出.wav>      # 「摩擦／爆音」「句中換氣／擦聲」都要 0 處，才做下一章

時間軸格式：{章節 id: {"total": 影格數, "shots": [{"events": [{"kind": "teacher"|"cub", "file": "voice_full/x.wav", "from": 影格}]}]}}
（《尼莫點》build_timing_full.py 的輸出）。沒有 file 的事件（只有字卡）略過。
"""
import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("timing"); ap.add_argument("chapter"); ap.add_argument("public"); ap.add_argument("out")
    ap.add_argument("--cub-gain", type=float, default=0.63, help="小熊配音在 Remotion 的音量（預設 0.63）")
    ap.add_argument("--fps", type=float, default=30)
    a = ap.parse_args()
    ch = json.loads(Path(a.timing).read_text(encoding="utf-8"))[a.chapter]
    sr, out, n = None, None, 0
    for shot in ch["shots"]:
        for e in shot["events"]:
            if not e.get("file"):
                continue
            y, r = sf.read(str(Path(a.public) / e["file"]), always_2d=True)
            y = y.mean(1)
            if sr is None:
                sr = r; out = np.zeros(int(ch["total"] / a.fps * sr) + sr)
            if r != sr:
                raise SystemExit(f"取樣率不一致：{e['file']} 是 {r} Hz，其他是 {sr} Hz")
            s = int(e["from"] / a.fps * sr)
            out[s:s + len(y)] += y * (a.cub_gain if e["kind"] == "cub" else 1.0)
            n += 1
    if out is None:
        raise SystemExit("這一章沒有配音檔")
    sf.write(a.out, out, sr, subtype="PCM_16")
    print(f"{a.chapter}：疊了 {n} 個配音檔 → {a.out}")


if __name__ == "__main__":
    main()
