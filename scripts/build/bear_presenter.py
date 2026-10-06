"""黑熊老師講課角色疊加：把分層 SVG 角色（04_品牌資產/貼圖角色/黑熊老師_SVG）放在畫面右下角，依配音音量對嘴、眨眼、呼吸、換手勢。
build.py 不支援角色圖層，所以在 build.py 輸出後、接片尾前執行。

用法：
  python bear_presenter.py <影片專案資料夾> --character <黑熊老師_SVG 資料夾> [--video 主片.mp4] [--height 330] [--fps 15]
需要：pip install playwright numpy soundfile；python -m playwright install chromium（只需一次）；ffmpeg

輸入（預設自動找）：
  3_製作後/輸出成品/<name>_<配音>.mp4         build.py 主片（不含片尾）
  2_製作中/剪輯專案/build/narration_norm.wav  build.py 的旁白軌（與主片同時間軸，含片頭留白）
  2_製作中/剪輯專案/build/timeline.json       片頭長度、每幕開始時間
輸出：同資料夾 <主片名>_黑熊講課.mp4（不覆寫原檔）

手勢規則（可用 --gestures 覆寫，格式 S01=wave,S03=point）：
  每幕開頭 2.5 秒做手勢（第一幕 wave、最後一幕結尾 3 秒 wave、其餘 point），其餘時間 idle；
  有聲音時表情 talking、嘴型依音量（level < 0.08 閉嘴、< 0.30 小開、其餘 A／O，由 character.js 決定）。
片頭與片尾不出現角色。
"""
import argparse, asyncio, glob, http.server, json, os, shutil, socketserver, subprocess, sys, threading
import numpy as np
import soundfile as sf

RENDER_HTML = """<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="character.css">
<style>html,body{margin:0;background:transparent}#stage{width:560px;height:530px}</style></head>
<body><div id="stage"></div><script src="character.js"></script>
<script>window.ready=BlackBearTeacher.mount("#stage","character.svg").then(()=>{try{BlackBearTeacher.stopAutoBlink()}catch(e){};BlackBearTeacher.useManualClock(true);return true;});</script>
</body></html>"""


def levels(wav, fps, n):
    y, sr = sf.read(wav, dtype="float32")
    if y.ndim > 1: y = y.mean(1)
    hop = sr / fps; out = np.zeros(n, np.float32)
    for i in range(n):
        a, b = int(i * hop), int((i + 1) * hop)
        seg = y[a:b]
        out[i] = np.sqrt(np.mean(seg ** 2)) if len(seg) else 0
    ref = np.percentile(out[out > 1e-4], 95) if np.any(out > 1e-4) else 1
    lv = np.clip(out / max(ref, 1e-6), 0, 1)
    sm = np.convolve(lv, [0.25, 0.5, 0.25], "same")       # 輕微平滑，避免嘴巴抖動
    return sm


def scene_starts(tl, proj, intro):
    """每幕開始秒數：timeline.json 的 scene_starts（build.py 2.1.0 起）；舊版則讀 章節_*.txt"""
    if tl.get("scene_starts"): return tl["scene_starts"]
    import re
    chs = sorted(glob.glob(os.path.join(proj, "3_製作後", "輸出成品", "章節_*.txt")), key=os.path.getmtime)
    if not chs: return [intro]
    out = []
    for l in open(chs[-1], encoding="utf-8"):
        m = re.match(r"(\d+):(\d\d)", l.strip())
        if m: out.append(int(m.group(1)) * 60 + int(m.group(2)))
    if out: out[0] = intro
    return out


def gesture_plan(starts, n, fps, override):
    g = ["idle"] * n
    for k, t0 in enumerate(starts):
        name = override.get(f"S{k + 1:02d}", "wave" if k == 0 else "point")
        for i in range(int(t0 * fps), min(n, int((t0 + 2.5) * fps))): g[i] = name
    for i in range(max(0, n - 3 * fps), n): g[i] = "wave"
    return g


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


async def render(chardir, frames_dir, plan, lv, fps, t_from):
    from playwright.async_api import async_playwright
    os.chdir(chardir)
    srv = socketserver.TCPServer(("127.0.0.1", 0), Quiet); port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width": 560, "height": 530})
        await pg.goto(f"http://127.0.0.1:{port}/_render.html"); await pg.evaluate("window.ready")
        stage = pg.locator("#stage")
        for i in range(len(plan)):
            talking = "true" if lv[i] > 0.05 else "false"
            expr = "talking" if lv[i] > 0.05 else "normal"
            await pg.evaluate(f"BlackBearTeacher.pose({{expression:'{expr}',gesture:'{plan[i]}',talking:{talking},level:{float(lv[i]):.3f}}});"
                              f"BlackBearTeacher.tick({t_from + i / fps:.4f})")
            await stage.screenshot(path=os.path.join(frames_dir, f"f{i:06d}.png"), omit_background=True)
            if i % 500 == 0: print(f"角色畫格 {i}/{len(plan)}", flush=True)
        await b.close()
    srv.shutdown()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project"); ap.add_argument("--character", required=True)
    ap.add_argument("--video"); ap.add_argument("--height", type=int, default=330); ap.add_argument("--fps", type=int, default=15)
    ap.add_argument("--margin", type=int, default=20); ap.add_argument("--gestures", default="")
    a = ap.parse_args()
    proj = os.path.abspath(a.project); chardir = os.path.abspath(a.character)
    build = os.path.join(proj, "2_製作中", "剪輯專案", "build")
    tl = json.load(open(os.path.join(build, "timeline.json"), encoding="utf-8"))
    video = a.video or max([p for p in glob.glob(os.path.join(proj, "3_製作後", "輸出成品", "*.mp4"))
                            if "完整版" not in p and "黑熊講課" not in p], key=os.path.getmtime)
    intro = tl["shots"][0]["t1"] if tl["shots"][0].get("kind") == "video" else 4.0
    total = tl["total"]
    n_all = int(total * a.fps)
    lv_all = levels(os.path.join(build, "narration_norm.wav"), a.fps, n_all)
    override = dict(x.split("=") for x in a.gestures.split(",") if "=" in x)
    plan_all = gesture_plan(scene_starts(tl, proj, intro), n_all, a.fps, override)
    i0 = int(np.ceil(intro * a.fps)); plan, lv = plan_all[i0:], lv_all[i0:]
    frames = os.path.join(build, "bear_frames"); shutil.rmtree(frames, ignore_errors=True); os.makedirs(frames)
    open(os.path.join(chardir, "_render.html"), "w", encoding="utf-8").write(RENDER_HTML)
    cwd = os.getcwd()
    try:
        asyncio.run(render(chardir, frames, plan, lv, a.fps, i0 / a.fps))
    finally:
        os.chdir(cwd)
        try: os.remove(os.path.join(chardir, "_render.html"))
        except OSError: pass
    h = a.height; w = int(round(h * 560 / 530 / 2)) * 2
    out = video[:-4] + "_黑熊講課.mp4"
    fc = (f"[1:v]scale={w}:{h}:flags=lanczos,format=rgba,setpts=PTS-STARTPTS+{i0 / a.fps:.4f}/TB[bear];"
          f"[0:v][bear]overlay=W-w-{a.margin}:H-h-{a.margin // 2}:eof_action=pass:enable='gte(t,{intro:.3f})'[v]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", video, "-framerate", str(a.fps), "-i", os.path.join(frames, "f%06d.png"),
                    "-filter_complex", fc, "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", out], check=True)
    print("黑熊講課版：", out)


if __name__ == "__main__":
    main()
