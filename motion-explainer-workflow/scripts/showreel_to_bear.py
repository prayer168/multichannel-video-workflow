"""把 Motion Showreel 的成片（out/final.mp4 或工作區匯出版）疊上核定黑熊老師講課角色。

bear_presenter.py 讀的是 build.py 的資料夾配置；本腳本在暫存資料夾建立它要的最小配置
（3_製作後/輸出成品/、2_製作中/剪輯專案/build/timeline.json、narration_norm.wav），再呼叫它，
把 <名稱>_黑熊講課.mp4 複製到指定位置。不改動 showreel 專案或主技能檔案。

用法：
  python showreel_to_bear.py <showreel 專案> --out <輸出.mp4> [--video out/final.mp4]
         [--scenes 0,3.8,12.6] [--gestures S01=wave] [--height 330]

- 旁白取 <專案>/audio/narration.wav（narration.mjs import 產生），補靜音到成片長度後驅動對嘴。
- --scenes：每幕開始秒數（決定手勢；第一幕 wave、其餘 point、最後 3 秒 wave）。預設讀 timeline.js 的 SHOTS 起點。
- 片頭不在本腳本處理：showreel 段落是正片插段，片頭／片尾依主技能 append_outro.py 與 fixed-settings 接入。
需要：ffmpeg、python 的 playwright／numpy／soundfile（與 bear_presenter.py 相同）。
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
BEAR = os.path.join(REPO, "scripts", "build", "bear_presenter.py")
CHAR = os.path.join(REPO, "assets", "brand-approved", "v1", "blackbear-science", "character")


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def shot_starts(proj):
    p = os.path.join(proj, "timeline.js")
    if not os.path.isfile(p): return [0.0]
    txt = open(p, encoding="utf-8").read()
    m = re.search(r"SHOTS\s*=\s*\[(.*?)\];", txt, re.S)
    vals = [float(x) for x in re.findall(r"t0\s*:\s*([\d.]+)", m.group(1))] if m else []
    return vals or [0.0]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project"); ap.add_argument("--out", required=True)
    ap.add_argument("--video"); ap.add_argument("--scenes"); ap.add_argument("--gestures", default="")
    ap.add_argument("--height", type=int, default=330); ap.add_argument("--character", default=CHAR)
    a = ap.parse_args()
    proj = os.path.abspath(a.project)
    video = os.path.abspath(a.video) if a.video else os.path.join(proj, "out", "final.mp4")
    voice = os.path.join(proj, "audio", "narration.wav")
    for p in (video, voice, BEAR):
        if not os.path.isfile(p): sys.exit(f"找不到 {p}")
    total = duration(video)
    scenes = [float(x) for x in a.scenes.split(",")] if a.scenes else shot_starts(proj)

    tmp = tempfile.mkdtemp(prefix="showreel_bear_")
    try:
        build = os.path.join(tmp, "2_製作中", "剪輯專案", "build"); outdir = os.path.join(tmp, "3_製作後", "輸出成品")
        os.makedirs(build); os.makedirs(outdir)
        shutil.copy(video, os.path.join(outdir, "showreel.mp4"))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", voice, "-af", f"apad=whole_dur={total:.3f}", "-t", f"{total:.3f}",
                        os.path.join(build, "narration_norm.wav")], check=True)
        # kind=video 且 t1=0：讓 bear_presenter 從第 0 秒就顯示角色（showreel 插段沒有片頭）
        json.dump({"total": total, "shots": [{"kind": "video", "t0": 0, "t1": 0}], "scene_starts": scenes},
                  open(os.path.join(build, "timeline.json"), "w", encoding="utf-8"))
        cmd = [sys.executable, BEAR, tmp, "--character", os.path.abspath(a.character), "--video", os.path.join(outdir, "showreel.mp4"),
               "--height", str(a.height)]
        if a.gestures: cmd += ["--gestures", a.gestures]
        subprocess.run(cmd, check=True)
        os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
        shutil.copy(os.path.join(outdir, "showreel_黑熊講課.mp4"), a.out)
        print("輸出：", a.out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
