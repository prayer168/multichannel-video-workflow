"""黑熊老師原創配樂（程式合成，無任何第三方素材 → 不會被 Content ID 認領）
python make_music.py [章節鋪底秒數=720]
輸出（48 kHz 立體聲 WAV）：
  原創_Hook_輕快節奏.wav     120 BPM、C–G–Am–F，撥弦琶音＋鼓組＋貝斯＋主旋律，約 40 秒
  原創_片頭樂句.wav          撥弦上行琶音＋鐘聲，約 4.5 秒（開場、片尾）
  原創_章節鋪底_lofi.wav     84 BPM、Fmaj7–Em7–Dm7–Cmaj7 電鋼琴 lo-fi，依秒數生成（每小節隨機變化，不是循環）
"""
import os, sys
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, lfilter, fftconvolve

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20261002)
NOTE = {n: i for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}
def hz(name):                       # "A4" → 440
    n, o = name[:-1], int(name[-1]); return 440 * 2 ** ((NOTE[n] + 12 * (o - 4) - 9) / 12)
def lp(x, fc, order=2): return sosfilt(butter(order, fc, "low", fs=SR, output="sos"), x)
def hp(x, fc, order=2): return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x)
def t_(d): return np.arange(int(d * SR)) / SR

class Track:
    def __init__(self, dur): self.L = np.zeros(int(dur * SR) + SR * 3); self.R = np.zeros_like(self.L)
    def add(self, x, at, gain=1.0, pan=0.0):
        i = int(at * SR); x = x[: max(0, len(self.L) - i)]
        self.L[i:i + len(x)] += x * gain * np.sqrt(0.5 * (1 - pan)); self.R[i:i + len(x)] += x * gain * np.sqrt(0.5 * (1 + pan))

# ---------- 樂器 ----------
def kick(d=0.35):
    t = t_(d); f = 45 + 90 * np.exp(-t * 28); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9) + 0.25 * np.sin(ph * 2) * np.exp(-t * 30)
def snare(d=0.22, soft=False):
    t = t_(d); n = hp(rng.standard_normal(len(t)), 1800) * np.exp(-t * (26 if soft else 18))
    return (0.6 * n + 0.4 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)) * (0.5 if soft else 1)
def hat(d=0.06, open_=False):
    t = t_(0.25 if open_ else d); return hp(rng.standard_normal(len(t)), 7000, 4) * np.exp(-t * (14 if open_ else 70))
def pluck(f, d=1.2, bright=0.5, decay=0.996):
    """Karplus-Strong 撥弦"""
    N = int(round(SR / f - 0.5)); n = int(d * SR)          # KS 實際週期約 N+0.5
    x = np.zeros(n); burst = rng.uniform(-1, 1, N); x[:N] = lp(burst, 2000 + 8000 * bright)
    a = np.zeros(N + 2); a[0] = 1; a[N] = -0.5 * decay; a[N + 1] = -0.5 * decay
    y = lfilter([1], a, x); return y / (np.abs(y).max() + 1e-9) * np.exp(-t_(d) * 1.2)
def bass(f, d):
    t = t_(d); env = np.minimum(1, t / 0.01) * np.exp(-t * 2.2)
    return lp((np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)) * env, 900)
def epiano(f, d):
    t = t_(d + 1.2); env = np.minimum(1, t / 0.006) * np.exp(-t * 1.3); trem = 1 + 0.08 * np.sin(2 * np.pi * 4.8 * t)
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 4) + 0.08 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 6)
    rel = np.ones_like(t); k = int(d * SR); rel[k:] = np.exp(-(t[k:] - d) * 5)
    return x * env * trem * rel
def bell(f, d=2.0):
    t = t_(d); return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 3) + 0.2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 6)) * np.exp(-t * 2.5) * np.minimum(1, t / 0.003)
def lead(f, d):
    t = t_(d); vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.3)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    x = np.sin(ph) + 0.3 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
    env = np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.08).clip(0) * (0.75 + 0.25 * np.exp(-t * 4))
    return lp(x * env, 3500)

def reverb(L, R, secs=1.6, mix=0.18):
    n = int(secs * SR); t = np.arange(n) / SR
    out = []
    for s in (L, R):
        ir = rng.standard_normal(n) * np.exp(-t * 4.2); ir = lp(ir, 5000); ir /= np.sqrt((ir ** 2).sum())
        out.append(s + mix * fftconvolve(s, ir)[: len(s)])
    return out

def finish(tr, name, rms_db=-18.0, fade_out=1.5, rev=0.18):
    L, R = reverb(tr.L, tr.R, mix=rev)
    nz = np.flatnonzero(np.abs(L) + np.abs(R) > 1e-5); end = nz[-1] + 1 if len(nz) else len(L)
    L, R = L[:end], R[:end]
    f = int(fade_out * SR); w = np.linspace(1, 0, f) ** 2; L[-f:] *= w; R[-f:] *= w
    y = np.stack([L, R], 1)
    rms = np.sqrt(np.mean(y[np.abs(y).max(1) > 1e-4] ** 2)); y *= 10 ** (rms_db / 20) / (rms + 1e-12)
    pk = np.abs(y).max()
    if pk > 0.7: y = np.where(np.abs(y) > 0.7, np.sign(y) * (0.7 + 0.2 * np.tanh((np.abs(y) - 0.7) / 0.2)), y)   # 柔和限幅（上限 0.9）
    sf.write(os.path.join(HERE, name), y.astype(np.float32), SR, subtype="PCM_16")
    print(f"{name}：{len(y) / SR:.1f} 秒")

# ---------- 1. Hook：120 BPM ----------
def hook():
    bpm = 120; b = 60 / bpm; bar = 4 * b
    prog = [["C3", "E3", "G3", "C4"], ["G2", "D3", "G3", "B3"], ["A2", "E3", "A3", "C4"], ["F2", "C3", "F3", "A3"]]
    roots = ["C2", "G1", "A1", "F1"]
    mel = [  # (拍, 音, 長度拍) 每 4 小節一句
        (0, "E5", 1), (1, "G5", 1), (2, "C6", 1.5), (3.5, "B5", 0.5), (4, "D5", 1), (5, "G5", 1), (6, "B5", 2),
        (8, "C5", 1), (9, "E5", 1), (10, "A5", 1.5), (11.5, "G5", 0.5), (12, "F5", 1), (13, "A5", 1), (14, "C6", 2)]
    bars = 18; tr = Track(bars * bar)
    for k in range(bars):
        t0 = k * bar; ch = prog[k % 4]
        for i in range(8):                                   # 八分音符琶音
            n = ch[[0, 1, 2, 3, 2, 1, 2, 3][i]]; tr.add(pluck(hz(n[:-1] + str(int(n[-1]) + 1)), 0.7, 0.6), t0 + i * b / 2, 0.22, -0.35 + 0.1 * (i % 2))
        if k >= 2:
            for i in range(4): tr.add(kick(), t0 + i * b, 0.9)
            for i in (1, 3): tr.add(snare(), t0 + i * b, 0.45, 0.1)
            for i in range(8): tr.add(hat(), t0 + i * b / 2, 0.16 if i % 2 else 0.24, 0.3)
            for i in range(4): tr.add(bass(hz(roots[k % 4]), b * 0.9), t0 + i * b, 0.55)
        else:
            tr.add(kick(), t0, 0.6); tr.add(kick(), t0 + 2 * b, 0.6)
        if k >= 4:
            for beat, n, ln in mel:
                if (k - 4) % 4 == int(beat // 4): tr.add(lead(hz(n), ln * b * 0.95), t0 + (beat % 4) * b, 0.16, 0.15)
        if k % 4 == 3 and k >= 2: tr.add(snare(0.12, True), t0 + 3.5 * b, 0.3); tr.add(snare(0.12, True), t0 + 3.75 * b, 0.35)
    finish(tr, "原創_Hook_輕快節奏.wav", rms_db=-17, fade_out=2.0, rev=0.14)

# ---------- 2. 片頭小樂句 ----------
def jingle():
    tr = Track(5)
    for i, n in enumerate(["C4", "E4", "G4", "C5", "E5"]): tr.add(pluck(hz(n), 1.8, 0.7), 0.05 + i * 0.11, 0.35, -0.4 + 0.2 * i)
    for n in ["G3", "B3", "D4", "F4"]: tr.add(pluck(hz(n), 1.2, 0.5), 0.75, 0.22)
    for n in ["C4", "E4", "G4", "C5"]: tr.add(pluck(hz(n), 2.8, 0.6), 1.2, 0.26)
    tr.add(bell(hz("C6"), 2.5), 1.2, 0.18, 0.3); tr.add(bell(hz("G6"), 2.0), 1.45, 0.1, -0.3)
    tr.add(bass(hz("C2"), 2.0), 1.2, 0.5); tr.add(kick(), 1.2, 0.5)
    finish(tr, "原創_片頭樂句.wav", rms_db=-17, fade_out=0.8, rev=0.22)

# ---------- 3. 章節鋪底 lo-fi ----------
def bed(total):
    bpm = 84; b = 60 / bpm; bar = 4 * b; sw = 0.06
    prog = [["F3", "A3", "C4", "E4"], ["E3", "G3", "B3", "D4"], ["D3", "F3", "A3", "C4"], ["C3", "E3", "G3", "B3"]]
    roots = ["F1", "E1", "D1", "C2"]
    penta = ["C5", "D5", "E5", "G5", "A5", "C6"]
    bars = int(total / bar) + 2; tr = Track(bars * bar)
    for k in range(bars):
        t0 = k * bar; ch = prog[k % 4]
        for j, n in enumerate(ch): tr.add(epiano(hz(n), bar * 0.95), t0 + j * 0.012, 0.11, -0.25 + 0.17 * j)
        tr.add(bass(hz(roots[k % 4]), b * 1.8), t0, 0.42); tr.add(bass(hz(roots[k % 4]), b * 1.2), t0 + 2.5 * b, 0.32)
        tr.add(kick(0.3), t0, 0.5); tr.add(kick(0.3), t0 + 2.5 * b, 0.4)
        if rng.random() < 0.4: tr.add(kick(0.3), t0 + 1.75 * b, 0.25)
        for i in (1, 3): tr.add(snare(0.18, True), t0 + i * b, 0.32, 0.15)
        for i in range(8):
            off = (sw * b if i % 2 else 0); tr.add(hat(), t0 + i * b / 2 + off, (0.07 if i % 2 else 0.11) * (0.8 + 0.4 * rng.random()), 0.35)
        if k % 2 == 1 and rng.random() < 0.7:                   # 隨機撥弦點綴
            for q in range(rng.integers(2, 5)):
                tr.add(pluck(hz(penta[rng.integers(len(penta))]), 1.0, 0.4), t0 + (rng.integers(0, 8)) * b / 2, 0.07, 0.4)
    L, R = lp(tr.L, 6500), lp(tr.R, 6500); tr.L, tr.R = L, R
    finish(tr, "原創_章節鋪底_lofi.wav", rms_db=-19, fade_out=3.0, rev=0.2)

if __name__ == "__main__":
    total = float(sys.argv[1]) if len(sys.argv) > 1 else 720
    hook(); jingle(); bed(total)
