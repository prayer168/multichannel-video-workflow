"""音畫同步檢查（不靠 whisper）：每句配音原檔與成片混音做互相關，量出配音在成片中的實際位置與時間軸的差。
用法：python check_sync.py <成片.mp4> <timing_CHxx.json> <remotion/public> [--out report.json]
混音裡有鋪底與音效，互相關仍以配音本身為主峰；|偏移| ≤ 0.05 s 視為同步。
2026-11-26：本機 whisper 轉寫 15 秒音檔需 11 分鐘，CH05 起改用此法驗同步。
"""
import json, subprocess, sys, wave
from pathlib import Path
import numpy as np

SR = 16000


def load_mix(mp4):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(mp4), '-vn', '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def load_wav(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def lag(seg, ref):
    n = len(seg) + len(ref)
    c = np.fft.irfft(np.fft.rfft(seg, n) * np.conj(np.fft.rfft(ref, n)), n)
    k = int(np.argmax(c[:len(seg)]))
    return k / SR, float(c[k] / (np.linalg.norm(seg) * np.linalg.norm(ref) + 1e-9))


def main():
    mp4, timing, pub = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    mix = load_mix(mp4)
    t = json.load(open(timing, encoding='utf-8'))
    rows = []
    for s in t['shots']:
        for e in s['events']:
            ref = load_wav(pub / e['file'])
            exp = e['from'] / 30
            a = max(0, int((exp - 1.0) * SR))
            seg = mix[a: a + len(ref) + 2 * SR]
            l, score = lag(seg, ref)
            off = a / SR + l - exp
            rows.append(dict(id=e['id'], expected_s=round(exp, 3), offset_s=round(off, 3), corr=round(score, 3)))
    worst = max(abs(r['offset_s']) for r in rows)
    rep = dict(file=str(mp4), max_abs_offset_s=worst, pass_=worst <= 0.05, rows=rows)
    if '--out' in sys.argv:
        json.dump(rep, open(sys.argv[sys.argv.index('--out') + 1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"{len(rows)} 句，最大偏移 {worst:.3f} s，{'PASS' if worst <= 0.05 else 'FAIL'}")
    for r in rows:
        if abs(r['offset_s']) > 0.05 or r['corr'] < 0.3:
            print('  注意', r)


if __name__ == '__main__':
    main()
