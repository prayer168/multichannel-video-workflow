"""一鍵產生影片：python build.py <影片專案資料夾> [--voice auto|gemini|zhiwei] [--only 秒數]
輸入（都在專案資料夾內）：
  2_製作中/配音/旁白稿_分場.md        每幕「## S01 標題」＋一行一句
  2_製作中/畫面規格.yaml             影片設定＋每幕的畫面（見 references/build-pipeline.md）
  2_製作中/字幕/英文字幕稿.tsv        （選用）id<TAB>英文
流程：配音 → 切成逐句 → 時間軸 → 圖卡 → 逐格畫面（次像素推近、逐步出現、溶接）→ 混音 → 字幕 → 輸出 → 品質報告
已完成的中間檔會沿用（改了哪張圖卡就只重畫那張）；輸出檔不覆寫，自動加上 _2、_3…
"""
import argparse, hashlib, math, json, os, re, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import soundfile as sf
import yaml
from PIL import Image, ImageChops, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cards_lib
import anims_lib

FPS, W, H, SR = 30, 1920, 1080, 48000
GAP, GAP_STOP, SCENE_HEAD, SCENE_TAIL, END_PAD = 0.22, 0.45, 0.5, 0.6, 2.0
ZOOM, XFADE, DISSOLVE = 0.035, 0.25, 0.30


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore", **kw)
    if r.returncode != 0:
        print(r.stderr[-2000:]); raise SystemExit(f"指令失敗：{cmd[:4]}")
    return r


def free_path(p):
    base, ext = os.path.splitext(p); k = 2
    while os.path.exists(p): p = f"{base}_{k}{ext}"; k += 1
    return p


# ======================= 0. 讀取專案 =======================
def load_project(proj):
    root = os.path.abspath(os.path.join(proj, "..", ".."))           # 工作區根目錄（含 04_品牌資產）
    mid = os.path.join(proj, "2_製作中")
    spec = yaml.safe_load(open(os.path.join(mid, "畫面規格.yaml"), encoding="utf-8"))
    src = open(os.path.join(mid, "配音", "旁白稿_分場.md"), encoding="utf-8").read()
    lines, titles = [], {}
    for s in re.split(r"^## ", src, flags=re.M)[1:]:
        head, body = s.split("\n", 1)
        sid, title = (head.split(None, 1) + [""])[:2]
        titles[sid] = title.strip()
        for i, l in enumerate([x.strip() for x in body.strip().split("\n") if x.strip()], 1):
            lines.append(dict(id=f"{sid}_{i:02d}", scene=sid, idx=i, text=l))
    return root, mid, spec, lines, titles


# ======================= 1. 配音 =======================
def voice_zhiwei(lines, out, rate):
    os.makedirs(out, exist_ok=True)
    todo = [L for L in lines if not os.path.exists(os.path.join(out, L["id"] + ".wav"))]
    if not todo: return
    log(f"Zhiwei 暫定配音：{len(todo)} 句")
    tsv = os.path.join(out, "_todo.tsv")
    open(tsv, "w", encoding="utf-8-sig").write("".join(f"{L['id']}\t{L['text']}\n" for L in todo))
    run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", os.path.join(HERE, "say_batch.ps1"),
         "-Tsv", tsv, "-OutDir", out, "-Voice", "Zhiwei", "-Rate", str(rate)])
    os.remove(tsv)


def gemini_scene(text, style, voice, model, key):
    """呼叫 Gemini API 產生一幕的語音，回傳 (PCM 位元組, 取樣率)。格式依 AI Studio「Get code」"""
    import urllib.request, base64
    prompt = (f"## Style:\n{style}\n\n" if style else "") + f"## Transcript:\n{text}"
    body = dict(contents=[dict(role="user", parts=[dict(text=prompt)])],
                generationConfig=dict(temperature=1, responseModalities=["audio"],
                                      speechConfig=dict(voiceConfig=dict(prebuiltVoiceConfig=dict(voiceName=voice)))))
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key})
    with urllib.request.urlopen(req, timeout=600) as r:
        resp = json.load(r)
    part = resp["candidates"][0]["content"]["parts"][0]["inlineData"]
    # 註：有時資料前面帶 WAV 標頭、或頭尾有非語音的位元組，會變成喀聲／滿格雜訊 → 在 clean_tts() 清掉
    rate = int(re.search(r"rate=(\d+)", part.get("mimeType", "")).group(1)) if "rate=" in part.get("mimeType", "") else 24000
    return base64.b64decode(part["data"]), rate


def scene_files(scene_dir, titles):
    """每一幕對應的音檔：Sxx.wav，或一次產生多幕的 Sxx-Syy.wav"""
    order = list(titles); m = {}
    for s in order:
        p = os.path.join(scene_dir, s + ".wav")
        if os.path.exists(p): m[s] = (p, [s])
    for f in os.listdir(scene_dir) if os.path.isdir(scene_dir) else []:
        g = re.fullmatch(r"(S\d+)-(S\d+)\.wav", f)
        if g and g.group(1) in order and g.group(2) in order:
            grp = order[order.index(g.group(1)): order.index(g.group(2)) + 1]
            for s in grp: m.setdefault(s, (os.path.join(scene_dir, f), grp))
    return m


def voice_gemini(lines, titles, scene_dir, cfg):
    """缺少的分場音檔用 API 補齊（需要環境變數 GEMINI_API_KEY）；免費方案每分鐘 3 次、每天 10 次
    scenes_per_request: 2 → 一次產生相鄰兩幕（存成 S03-S04.wav），請求次數減半"""
    os.makedirs(scene_dir, exist_ok=True)
    have = scene_files(scene_dir, titles)
    missing = [s for s in titles if s not in have]
    if not missing: return True
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        log(f"缺少 {len(missing)} 幕 Gemini 配音（{', '.join(missing)}），也沒有 GEMINI_API_KEY"); return False
    per, order, groups = cfg.get("scenes_per_request", 1), list(titles), []
    for s in missing:
        if groups and len(groups[-1]) < per and order.index(s) == order.index(groups[-1][-1]) + 1: groups[-1].append(s)
        else: groups.append([s])
    for k, grp in enumerate(groups):
        sid = grp[0] if len(grp) == 1 else f"{grp[0]}-{grp[-1]}"
        text = "\n".join(L["text"] for L in lines if L["scene"] in grp)
        for attempt in range(5):
            try:
                pcm, rate = gemini_scene(text, cfg.get("style"), cfg.get("voice", "Achird"), cfg.get("model", "gemini-3.8-flash-tts"), key)
                break
            except Exception as e:
                msg = str(e); log(f"{sid} 失敗（{msg[:80]}），{60 * (attempt + 1)} 秒後重試")
                if "403" in msg or attempt == 4:
                    log("額度用完或權限不足，先停在這裡；明天或開通付費後重跑即可接續"); return False
                time.sleep(60 * (attempt + 1))
        y = np.frombuffer(pcm, "<i2").astype(np.float32) / 32768
        sf.write(os.path.join(scene_dir, sid + ".wav"), y, rate, subtype="PCM_16")
        log(f"Gemini 配音 {sid}：{len(y) / rate:.1f} 秒")
        if k < len(groups) - 1: time.sleep(cfg.get("api_interval", 21))
    return True


def clean_tts(y, sr, name=""):
    """清掉 TTS 音檔頭尾的雜訊（2026-10-01 實測：Gemini 每個檔案開頭 10 ms 喀聲、結尾約 130 ms 滿格雜訊）
    做法：以 10 ms 為單位看峰值；開頭若一開始就很大聲、接著安靜 → 歸零；結尾連續大聲且前面是安靜 → 剪掉；再加 5 ms 淡入淡出"""
    h = int(0.01 * sr); n = len(y) // h
    pk = 20 * np.log10(np.abs(y[: n * h]).reshape(n, h).max(1) + 1e-9)
    notes = []
    k = 0
    while k < min(n, 5) and pk[k] > -12: k += 1                      # 開頭的喀聲／突波
    if 0 < k < 5 and pk[k] < -35:
        y = y.copy(); y[: (k + 1) * h] = 0; notes.append(f"開頭 {k * 10} ms 突波")
    j = n
    while j > 0 and pk[j - 1] > -6: j -= 1                          # 結尾的滿格雜訊
    if j < n and (n - j) <= 40 and j > 0 and pk[max(0, j - 5): j].max() < -30:
        y = y[: j * h]; notes.append(f"結尾 {(n - j) * 10} ms 滿格雜訊")
    f = int(0.005 * sr); r = np.linspace(0, 1, f, dtype=np.float32)
    y = y.astype(np.float32).copy(); y[:f] *= r; y[-f:] *= r[::-1]
    if notes: log(f"清理 TTS {name}：" + "、".join(notes))
    return y


def split_scenes(lines, titles, scene_dir, out):
    """分場音檔 → 逐句（依停頓位置＋每句字數，用動態規劃找切點）；一個音檔可以包含多幕"""
    os.makedirs(out, exist_ok=True)
    files = scene_files(scene_dir, titles)
    scenes = {}
    for L in lines:
        path, grp = files[L["scene"]]
        scenes.setdefault(path, []).append(L)
    warn = []
    for path, Ls in scenes.items():
        sid = os.path.splitext(os.path.basename(path))[0]
        if all(os.path.exists(os.path.join(out, L["id"] + ".wav")) for L in Ls): continue
        tmp = os.path.join(out, f"_{sid}.wav")
        run(["ffmpeg", "-y", "-v", "error", "-i", path, "-ar", str(SR), "-ac", "1", tmp])
        y, _ = sf.read(tmp, dtype="float32"); os.remove(tmp)
        y = clean_tts(y, SR, sid)
        hop = 0.01; h = int(hop * SR)
        db = 20 * np.log10(np.sqrt(np.mean(y[: len(y) // h * h].reshape(-1, h) ** 2, axis=1) + 1e-12))
        silent = db < max(db.max() - 38, -50); voiced = np.flatnonzero(~silent); lo, hi = voiced[0], voiced[-1]
        runs, k = [], lo
        while k <= hi:
            if silent[k]:
                j = k
                while j <= hi and silent[j]: j += 1
                if (j - k) * hop >= 0.10: runs.append(((k + j) / 2 * hop, (j - k) * hop))
                k = j
            else: k += 1
        n = len(Ls)
        if len(runs) < n - 1: raise SystemExit(f"{sid}：只找到 {len(runs)} 個停頓，但有 {n} 句")
        wt = lambda t: len(re.findall(r"[一-鿿]", t)) + 1.5 * len(re.findall(r"[A-Za-z]+", t)) + 1.3 * len(re.findall(r"[0-9]", t)) + .5
        w = np.array([wt(L["text"]) for L in Ls]); start, end = lo * hop, (hi + 1) * hop
        exp = w / w.sum() * (end - start - sum(r[1] for r in runs))
        pts = [(start, 0.0)] + runs + [(end, 0.0)]; M = len(pts); INF = float("inf")
        cost = np.full((n + 1, M), INF); back = np.zeros((n + 1, M), int); cost[0][0] = 0
        for i in range(1, n + 1):
            for b in range(1, M):
                if (i == n) != (b == M - 1): continue
                for a in range(b):
                    if cost[i - 1][a] == INF: continue
                    dur = (pts[b][0] - pts[b][1] / 2) - (pts[a][0] + pts[a][1] / 2)
                    c = cost[i - 1][a] + ((dur - exp[i - 1]) / max(exp[i - 1], .6)) ** 2 - 2.0 * min(pts[b][1], .8)
                    if c < cost[i][b]: cost[i][b], back[i][b] = c, a
        idx, b = [], M - 1
        for i in range(n, 0, -1): idx.append(b); b = back[i][b]
        idx = [0] + idx[::-1]
        for i, L in enumerate(Ls):
            a0, b0 = pts[idx[i]][0], pts[idx[i + 1]][0]
            sf.write(os.path.join(out, L["id"] + ".wav"), y[int(a0 * SR): int(b0 * SR)], SR, subtype="PCM_16")
            if not .4 < (b0 - a0) / exp[i] < 2.3: warn.append(f"{L['id']} 長度 {b0 - a0:.2f}s（預估 {exp[i]:.2f}s）")
        log(f"切句 {sid}：{n} 句")
    return warn


# ======================= 2. 時間軸＋配音軌 =======================
def build_narration(lines, line_dir, work, intro_len, pause=None):
    """pause＝{幕: 秒}：這一幕開始前多留的純音樂時間（片名動畫、段落呼吸）"""
    os.makedirs(os.path.join(work, "trim"), exist_ok=True)
    pause = pause or {}
    t = intro_len; audio = [np.zeros(int(intro_len * SR), np.float32)]; prev = None
    for L in lines:
        if L["scene"] != prev:
            if prev: audio.append(np.zeros(int(SCENE_TAIL * SR), np.float32)); t += SCENE_TAIL
            L["scene_start"] = t
            extra = SCENE_HEAD + pause.get(L["scene"], 0)
            audio.append(np.zeros(int(extra * SR), np.float32)); t += extra; prev = L["scene"]
        src = os.path.join(line_dir, L["id"] + ".wav"); tw_ = os.path.join(work, "trim", L["id"] + ".wav")
        if not os.path.exists(tw_) or os.path.getmtime(tw_) < os.path.getmtime(src):
            run(["ffmpeg", "-y", "-v", "error", "-i", src, "-af",
                 "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.03,areverse,"
                 "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.06,areverse", "-ar", str(SR), "-ac", "1", tw_])
        y, _ = sf.read(tw_, dtype="float32")
        fz = min(len(y) // 4, int(0.005 * SR))                    # 每句頭尾 5 ms 淡入淡出，避免接縫喀聲
        if fz > 0:
            rr = np.linspace(0, 1, fz, dtype=np.float32); y = y.copy(); y[:fz] *= rr; y[-fz:] *= rr[::-1]
        L["start"], L["end"] = t, t + len(y) / SR
        audio.append(y); t = L["end"]
        g = GAP_STOP if L["text"][-1] in "。！？" else GAP
        audio.append(np.zeros(int(g * SR), np.float32)); t += g
    audio.append(np.zeros(int(END_PAD * SR), np.float32)); t += END_PAD
    sf.write(os.path.join(work, "narration.wav"), np.concatenate(audio), SR, subtype="PCM_16")
    return t


# ======================= 3. 畫面：鏡頭表＋圖卡 =======================
def expand_shots(spec, lines, total, intro, cards_dir, root, proj=None):
    """把畫面規格展開成鏡頭表：每個鏡頭 = 一個畫面（含逐步出現的各狀態）或一段影片"""
    os.makedirs(cards_dir, exist_ok=True)
    by = {(L["scene"], L["idx"]): L for L in lines}
    first = {}
    for L in lines: first.setdefault(L["scene"], L)
    shots = [dict(kind="video", path=intro, t0=0.0, wm=False, loop=False)]
    jobs = []
    for sid in dict.fromkeys(L["scene"] for L in lines):
        beats = spec["scenes"].get(sid)
        if not beats: raise SystemExit(f"畫面規格缺少 {sid}")
        for k, b in enumerate(beats):
            at = b.get("at", 1)
            t0 = first[sid]["scene_start"] if k == 0 else by[(sid, at)]["start"] - 0.15
            fx = dict(cam=b.get("cam"), trans=b.get("trans"), lb=b.get("lb"))
            if b["type"] == "video":
                shots.append(dict(kind="video", path=b["src"], t0=t0, wm=b.get("watermark", False), loop=not b.get("ss"), ss=b.get("ss", 0), **fx)); continue
            if b["type"] == "anim":
                ap = {x: v for x, v in b.items() if x not in ("at", "steps", "cam", "trans", "lb", "type")}
                if ap.get("images"):
                    ap["images"] = [x if os.path.isabs(x) else os.path.join(proj or root, x) for x in ap["images"]]
                evl = [by[(sid, ln)]["start"] - 0.15 - t0 for ln in b.get("steps", [])]
                shots.append(dict(kind="anim", t0=t0, p=ap, ev=evl, wm=True, **fx)); continue
            params = {x: v for x, v in b.items() if x not in ("at", "steps", "cam", "trans", "lb")}
            if params.get("image") and not os.path.isabs(params["image"]):   # 先找影片專案資料夾，再找工作區根目錄
                cand = os.path.join(proj, params["image"]) if proj else None
                params["image"] = cand if cand and os.path.exists(cand) else os.path.join(root, params["image"])
            states = []
            if b.get("steps"):
                st = b["steps"]
                if st[0] > at: states.append((t0, 0))
                for i, ln in enumerate(st):
                    ts = t0 if ln <= at else by[(sid, ln)]["start"] - 0.15
                    if states and abs(states[-1][0] - ts) < 1e-6: states[-1] = (ts, i + 1)
                    else: states.append((ts, i + 1))
            else:
                states.append((t0, None))
            variants = []
            for ts, show in states:
                p = dict(params) if show is None else dict(params, show=show)
                h = hashlib.md5((json.dumps(p, ensure_ascii=False, sort_keys=True) +
                                 str(os.path.getmtime(cards_lib.__file__))).encode()).hexdigest()[:8]
                png = os.path.join(cards_dir, f"{sid}_{k + 1:02d}{'' if show is None else f'_s{show}'}_{h}.png")
                if not os.path.exists(png): jobs.append((p, png))
                variants.append((ts, png))
            shots.append(dict(kind="card", t0=t0, variants=variants, wm=True, photo=b["type"] == "photo", **fx))
    # 預設：照片依序換不同運鏡；照片與動畫加電影黑邊
    cams = ["push", "pan_r", "pull", "pan_l", "tilt_up", "push_r", "pull", "pan_l"]; ci = 0
    for s in shots:
        if s["kind"] == "card" and s.get("photo") and not s.get("cam"): s["cam"] = cams[ci % len(cams)]; ci += 1
        if s.get("lb") is None: s["lb"] = bool(spec["video"].get("letterbox")) and (s.get("photo") or s["kind"] == "anim")
        if not s.get("trans"): s["trans"] = "dissolve"
    for i, s in enumerate(shots):
        s["t1"] = shots[i + 1]["t0"] if i + 1 < len(shots) else total
        s["f0"], s["f1"] = round(s["t0"] * FPS), round(s["t1"] * FPS)
    return shots, jobs


def _card_job(a):
    p, png = a
    if p.get("type") == "photo":                    # 照片分兩層：照片（運鏡）＋文字（固定、淡入）
        bg, fg = cards_lib.photo_layers(p)
        bg.save(png); fg.save(png[:-4] + "_fg.png")
    else:
        cards_lib.render(p, png)
    return png


# ======================= 4. 逐格產生畫面（分段平行） =======================
_img_cache = {}


def _img(png):
    if png not in _img_cache:
        if len(_img_cache) > 12: _img_cache.clear()
        _img_cache[png] = Image.open(png).convert("RGB")
    return _img_cache[png]


def _zoomed(png, z):
    c = 1 - 1 / z
    return _img(png).transform((W, H), Image.AFFINE, (1 / z, 0, c * W / 2, 0, 1 / z, c * H / 2), Image.BICUBIC)


def _cam_params(cam, u):
    """運鏡：u＝鏡頭進度 0–1，回傳 (縮放, 水平位移, 垂直位移)；位移以像素計、不超出畫面"""
    u = u * 0.75 + (u * u * (3 - 2 * u)) * 0.25       # 大致等速，頭尾略緩
    if cam == "push": z, x, y = 1.0 + 0.09 * u, 0, 0
    elif cam == "pull": z, x, y = 1.11 - 0.09 * u, 0, 0
    elif cam in ("pan_r", "pan_l"):
        z = 1.12; m = (1 - 1 / z) * W / 2 * 0.92; x = (-m + 2 * m * u) * (1 if cam == "pan_r" else -1); y = 0
    elif cam in ("tilt_up", "tilt_down"):
        z = 1.12; m = (1 - 1 / z) * H / 2 * 0.92; y = (m - 2 * m * u) * (1 if cam == "tilt_up" else -1); x = 0
    elif cam in ("push_r", "push_l"):
        z = 1.03 + 0.08 * u; m = (1 - 1 / z) * W / 2 * 0.8; x = m * u * (1 if cam == "push_r" else -1); y = 0
    elif cam == "still": z, x, y = 1.0, 0, 0
    else: z, x, y = 1 + ZOOM * u, 0, 0               # 圖卡預設：緩慢推近
    mx, my = (1 - 1 / z) * W / 2, (1 - 1 / z) * H / 2   # 轉場延長時不能露出畫面外的黑邊
    return z, max(-mx, min(mx, x)), max(-my, min(my, y))


def _camera(png, z, dx, dy):
    c = 1 - 1 / z
    return _img(png).transform((W, H), Image.AFFINE, (1 / z, 0, c * W / 2 + dx, 0, 1 / z, c * H / 2 + dy), Image.BICUBIC)


def _fg(png):
    k = png + "#fg"
    if k not in _img_cache:
        if len(_img_cache) > 12: _img_cache.clear()
        _img_cache[k] = Image.open(png[:-4] + "_fg.png").convert("RGBA")
    return _img_cache[k]


def _fade_fg(fg, a, slide):
    """文字層淡入＋往上滑入"""
    if a >= 1: return fg
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lay.paste(fg, (0, int(slide * (1 - a))))
    al = lay.getchannel("A").point(lambda v: int(v * a)); lay.putalpha(al)
    return lay


def _card_frame(s, f, fg_alpha=1.0):
    n = s["f1"] - s["f0"]; i = f - s["f0"]; t = f / FPS
    u = i / max(n, 1)
    if u > 1: u = 1 + (u - 1) * 0.6                   # 轉場時稍微延續原本的運鏡（不凍結）
    z, dx, dy = _cam_params(s.get("cam"), min(u, 1.08))
    vs = s["variants"]; k = max(j for j, (ts, _) in enumerate(vs) if ts <= t + 1e-9) if t >= vs[0][0] else 0
    if s.get("photo"):                                # 照片運鏡、文字固定
        im = _camera(vs[0][1], z, dx, dy).convert("RGBA")
        a0 = (t - s["t0"] - 0.35) / 0.55              # 第一個狀態：鏡頭開始後淡入
        if fg_alpha <= 0: return im.convert("RGB")      # 轉場中舊鏡頭的文字已淡出
        if k == 0: im.alpha_composite(_fade_fg(_fg(vs[0][1]), max(0.0, min(1.0, a0)) * fg_alpha, 24))
        else:
            a = (t - vs[k][0]) / 0.45
            if a < 1: im.alpha_composite(_fade_fg(_fg(vs[k - 1][1]), fg_alpha, 0))
            im.alpha_composite(_fade_fg(_fg(vs[k][1]), max(0.0, min(1.0, a)) * fg_alpha, 18))
        return im.convert("RGB")
    im = _camera(vs[k][1], z, dx, dy)
    if k > 0 and t - vs[k][0] < XFADE:              # 逐步出現：新狀態淡入
        im = Image.blend(_camera(vs[k - 1][1], z, dx, dy), im, (t - vs[k][0]) / XFADE)
    return im


def _anim_frame(s, f):
    return anims_lib.frame(s["p"], f / FPS - s["t0"], s["t1"] - s["t0"], s["ev"])


def _shot_frame(s, f, fg_alpha=1.0):
    return _anim_frame(s, f) if s["kind"] == "anim" else _card_frame(s, f, fg_alpha)


def _video_frames(s):
    vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x091D38,fps={FPS}"
    n = s["f1"] - s["f0"]
    cmd = ["ffmpeg", "-v", "error"] + (["-stream_loop", "-1"] if s.get("loop") else []) + (["-ss", str(s["ss"])] if s.get("ss") else []) + ["-i", s["path"], "-vf", vf, "-frames:v", str(n),
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    last = None
    for _ in range(n):
        buf = p.stdout.read(W * H * 3)
        if len(buf) == W * H * 3: last = Image.frombuffer("RGB", (W, H), buf)
        yield last                                  # 影片比段落短時停在最後一格
    p.stdout.close(); p.wait()


TRANS_LEN = dict(dissolve=0.35, whip_l=0.42, whip_r=0.42, flash=0.45, zoom=0.5, dip=0.7, leak=0.55, cut=0)
LB_H, LB_RAMP = 112, 0.6
_leak_cache = {}


def _hblur(im, k):
    k = max(1.0, k)
    return im.resize((max(8, int(W / k)), H), Image.BILINEAR).resize((W, H), Image.BILINEAR)


def _leak(q):
    """暖色漏光：從左到右掃過的柔光"""
    key = "g"
    if key not in _leak_cache:
        g = Image.radial_gradient("L").resize((W, W), Image.BICUBIC).point(lambda v: max(0, 255 - v))
        _leak_cache[key] = g
    g = _leak_cache[key]
    lay = Image.new("L", (W, H), 0); x = int(-W * 0.6 + q * W * 1.2)
    lay.paste(g, (x, (H - W) // 2))
    a = math.sin(math.pi * q) * 0.85
    col = Image.new("RGB", (W, H), (255, 170, 80))
    return col, lay.point(lambda v: int(v * a))


def _transition(kind, prev, cur, q):
    """q：轉場進度 0–1"""
    if kind == "whip_l" or kind == "whip_r":
        d = -1 if kind == "whip_l" else 1
        e = q * q * (3 - 2 * q)
        can = Image.new("RGB", (W, H))
        can.paste(prev, (int(-d * e * W), 0)); can.paste(cur, (int(d * (1 - e) * W), 0))
        return _hblur(can, 1 + 40 * math.sin(math.pi * q))
    if kind == "flash":
        white = Image.new("RGB", (W, H), (255, 252, 240))
        return Image.blend(prev, white, min(1, q * 2.2)) if q < 0.45 else Image.blend(white, cur, min(1, (q - 0.45) / 0.55))
    if kind == "zoom":                                # 前半：舊畫面加速推進；後半：新畫面從放大退回；只在中點 2 格交疊
        def zc(img, z):
            z = max(1.0, z); a = img.resize((int(W * z), int(H * z)), Image.BILINEAR)
            return a.crop(((a.width - W) // 2, (a.height - H) // 2, (a.width - W) // 2 + W, (a.height - H) // 2 + H))
        if q < 0.45: return zc(prev, 1 + 0.35 * (q / 0.45) ** 2)
        if q > 0.55: return zc(cur, 1 + 0.25 * (1 - (q - 0.55) / 0.45) ** 2)
        return Image.blend(zc(prev, 1.35), zc(cur, 1.25), (q - 0.45) / 0.1)
    if kind == "dip":
        black = Image.new("RGB", (W, H))
        return Image.blend(prev, black, min(1, q * 2)) if q < 0.5 else Image.blend(black, cur, (q - 0.5) * 2)
    if kind == "leak":
        im = Image.blend(prev, cur, q * q * (3 - 2 * q))
        col, m = _leak(q)
        return Image.composite(ImageChops.screen(im, col), im, m)
    return Image.blend(prev, cur, q)


def _lb_value(shots, si, t):
    s = shots[si]; v = 1.0 if s.get("lb") else 0.0
    if si > 0:
        pv = 1.0 if shots[si - 1].get("lb") else 0.0
        if pv != v:
            q = max(0.0, min(1.0, (t - s["t0"]) / LB_RAMP)); q = q * q * (3 - 2 * q)
            return pv + (v - pv) * q
    return v


def render_part(args):
    shots, idxs, out, wm_path = args
    wm = Image.open(wm_path).convert("RGBA")
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-g", "60", out], stdin=subprocess.PIPE)
    for si in idxs:
        s = shots[si]; prev = shots[si - 1] if si > 0 else None
        kind = s.get("trans", "dissolve")
        can = prev is not None and prev["kind"] in ("card", "anim") and s["kind"] in ("card", "anim") and kind != "cut"
        if prev is not None and prev["kind"] == "video" and s["kind"] != "video" and kind != "cut": kind, can = "dissolve", True
        last_prev = None; prev_moving = False
        if can:
            if prev["kind"] == "video":
                last_prev = None
                for last_prev in _video_frames(dict(prev, f0=prev["f1"] - 1, ss=max(0, prev.get("ss", 0) + (prev["f1"] - prev["f0"] - 1) / FPS), loop=False)): pass
            else:
                last_prev = _shot_frame(prev, prev["f1"] - 1); prev_moving = True
        nt = int(TRANS_LEN.get(kind, 0.35) * FPS)
        frames = _video_frames(s) if s["kind"] == "video" else (_shot_frame(s, f) for f in range(s["f0"], s["f1"]))
        for j, im in enumerate(frames):
            if last_prev is not None and j < nt:
                q = (j + 1) / (nt + 1)
                pf = _shot_frame(prev, prev["f1"] + j, max(0.0, 1 - 3 * q)) if prev_moving else last_prev   # 舊鏡頭繼續運鏡；字卡在前 1/3 淡出，避免兩張字卡重疊
                im = _transition(kind, pf, im, (j + 1) / (nt + 1))
            lb = _lb_value(shots, si, (s["f0"] + j) / FPS)
            h = int(LB_H * lb)
            if lb > 0:
                d = ImageDraw.Draw(im)
                d.rectangle([0, 0, W, h], fill=(0, 0, 0)); d.rectangle([0, H - h, W, H], fill=(0, 0, 0))
            if s["wm"]:                                   # 浮水印最後疊，有黑邊時往上移到畫面內
                im = im.convert("RGBA"); im.alpha_composite(wm, (0, 0), (0, h, W, H)) if h else im.alpha_composite(wm); im = im.convert("RGB")
            enc.stdin.write(im.tobytes())
    enc.stdin.close(); enc.wait()
    return out


def render_video(shots, work, wm, workers):
    parts_dir = os.path.join(work, "parts"); os.makedirs(parts_dir, exist_ok=True)
    total = shots[-1]["f1"]; per = total / workers; groups, cur, acc = [], [], 0
    for i, s in enumerate(shots):
        cur.append(i); acc += s["f1"] - s["f0"]
        if acc >= per * (len(groups) + 1) and len(groups) < workers - 1: groups.append(cur); cur = []
    if cur: groups.append(cur)
    jobs = [(shots, g, os.path.join(parts_dir, f"part_{k:02d}.mp4"), wm) for k, g in enumerate(groups)]
    log(f"逐格產生畫面：{total} 格，分 {len(jobs)} 段平行處理")
    with ProcessPoolExecutor(len(jobs)) as ex:
        outs = list(ex.map(render_part, jobs))
    lst = os.path.join(parts_dir, "list.txt")
    open(lst, "w", encoding="utf-8").write("".join(f"file '{o}'\n".replace("\\", "/") for o in outs))
    return lst


# ======================= 5. 混音 =======================
def measure_i(path):
    r = run(["ffmpeg", "-i", path, "-af", "ebur128", "-f", "null", "-"])
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])


def fit_bgm(src, dst, length, fit, work):
    """把配樂剪成片長：開頭照原曲、中段循環 [loop_from, loop_to]、最後一段（tail_from 到曲尾）對齊片尾
    接點以 bar 秒數對齊拍子，並做 xfade 秒的等功率交叉淡化；多出來的零頭從前奏裁掉"""
    tmp = os.path.join(work, "_bgm_src.wav")
    run(["ffmpeg", "-y", "-v", "error", "-i", src, "-ar", str(SR), "-ac", "2", tmp])
    y, _ = sf.read(tmp, dtype="float32"); os.remove(tmp)
    bar, xf = fit.get("bar", 1.7266), fit.get("xfade", 1.2)
    dur = len(y) / SR
    if fit.get("jumps"):
        # 跳接模式：在「音樂真的重複」的位置跳回去（用頻譜自我相似度找到的接點），其餘照原曲播完
        # jumps: [[在第幾秒, 跳回第幾秒], ...]；多出／不足的長度用前奏補（開頭留白或從前奏中間開始）
        segs, cur = [], 0.0
        for a, b in fit["jumps"]:
            segs.append((cur, a)); cur = b
        segs.append((cur, dur))
        total_len = sum(e - s for s, e in segs)
        pad = length - total_len
        if pad < 0: segs[0] = (min(segs[0][1] - 1, -pad), segs[0][1]); pad = 0.0
    else:                                              # 循環模式（舊）：中段依小節循環、最後一段對齊片尾
        lf, lt, tf = fit["loop_from"], fit["loop_to"], fit["tail_from"]
        need = length - (dur - tf)
        if need <= tf:
            c = tf - math.ceil((tf - need) / bar) * bar
            segs, pad = [(0.0, c)], need - c
        else:
            segs, cur = [(0.0, lt)], lt
            while need - cur > lt - lf: segs.append((lf, lt)); cur += lt - lf
            k = int((need - cur) / bar)
            if k: segs.append((lt - k * bar, lt)); cur += k * bar
            pad = need - cur
        segs.append((tf, dur))
    n = int(xf * SR); ramp = np.sin(np.linspace(0, np.pi / 2, n))[:, None]
    out = y[int(segs[0][0] * SR): int(segs[0][1] * SR)]
    for s0, e0 in segs[1:]:
        seg = y[max(0, int(s0 * SR) - n): int(e0 * SR)]
        a, b = out[-n:] * ramp[::-1], seg[:n] * ramp
        out = np.concatenate([out[:-n], a + b, seg[n:]])
    out = np.concatenate([np.zeros((int(pad * SR), 2), np.float32), out])[: int(length * SR)]
    if len(out) < int(length * SR): out = np.concatenate([out, np.zeros((int(length * SR) - len(out), 2), np.float32)])
    sf.write(dst, out, SR, subtype="FLOAT")
    log(f"配樂剪接：前面留白 {pad:.2f}s＋" + " + ".join(f"{a:.1f}–{b:.1f}s" for a, b in segs))


def make_sfx(shots, total, whoosh_on=True, hit_on=True):
    """自製音效（不需授權）：whoosh（甩鏡、推進轉場）、hit（閃白、片名）"""
    rng = np.random.default_rng(5); out = np.zeros((int(total * SR) + SR, 2), np.float32)

    def lowpass(x, fc):
        """二階低通（兩次一階），fc 可以是陣列（隨時間變化）"""
        fc = np.broadcast_to(np.asarray(fc, np.float64), x.shape)
        k = 2 * np.pi * fc / SR; k = k / (1 + k)
        y1 = np.zeros_like(x); y2 = np.zeros_like(x); a1 = a2 = 0.0
        for i in range(len(x)):
            a1 += k[i] * (x[i] - a1); a2 += k[i] * (a1 - a2); y2[i] = a2
        return y2

    def whoosh(d=0.6):
        """柔和的「咻」：布朗雜訊（能量集中低頻）＋低通掃頻 200→900→200 Hz，沒有高頻沙沙聲"""
        n = int(d * SR); t = np.linspace(0, 1, n)
        x = np.cumsum(rng.standard_normal(n)); x -= np.convolve(x, np.ones(2001) / 2001, "same")   # 布朗雜訊去直流
        y = lowpass(x, 200 + 700 * np.sin(np.pi * t) ** 2)
        y = y - lowpass(y, 110)                                                                      # 去掉聽不到的超低頻
        y += 0.35 * np.sin(2 * np.pi * np.cumsum(90 + 110 * np.sin(np.pi * t)) / SR)                # 低頻音高滑動，增加「掠過」感
        env = np.sin(np.pi * t) ** 3
        y = y / (np.abs(y).max() + 1e-9) * env
        pan = np.sin(np.pi * (t - 0.5)) * 0.5
        return np.stack([y * (1 - pan), y * (1 + pan)], 1).astype(np.float32) * 0.55

    def hit(d=1.8):
        """低頻重擊（純正弦下滑＋很短的低通撞擊，不含高頻雜訊）"""
        n = int(d * SR); t = np.arange(n) / SR
        f = 50 + 70 * np.exp(-t * 16)
        y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.4)
        y += lowpass(rng.standard_normal(n), 300) * np.exp(-t * 40) * 3
        y = y / np.abs(y).max()
        return np.stack([y, y], 1).astype(np.float32) * 0.9

    W_, H_ = whoosh(), hit()
    for s in shots:
        k = s.get("trans"); at = None; snd = None
        if k in ("whip_l", "whip_r", "zoom") and whoosh_on: snd, at = W_, s["t0"] - 0.12
        elif k == "flash" and hit_on: snd, at = H_, s["t0"] + 0.1
        if s["kind"] == "anim" and s["p"].get("anim") == "title_reveal" and hit_on: snd, at = H_, s["t0"] + 0.45
        if snd is None or at is None or at < 0: continue
        i = int(at * SR); j = min(len(out), i + len(snd)); out[i:j] += snd[: j - i]
    return out


def mix_audio(root, work, cfg, total, intro_len, sfx=None):
    nar, norm = os.path.join(work, "narration.wav"), os.path.join(work, "narration_norm.wav")
    gain = -14 - measure_i(nar)
    for _ in range(2):
        run(["ffmpeg", "-y", "-v", "error", "-i", nar, "-af", f"volume={gain:.2f}dB,deesser=i=0.35:m=0.5:f=0.5,alimiter=limit=0.84:level=false", "-ar", str(SR), norm])   # 輕度去齒音（ㄙ、ㄕ太亮會刺耳）
        gain += -14 - measure_i(norm)
    body = total - intro_len
    bgm = os.path.join(work, "bgm.wav")
    if cfg.get("bgm_fit"):
        fit_bgm(os.path.join(root, cfg["bgm"]), bgm, body, cfg["bgm_fit"], work)
    else:
        run(["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", os.path.join(root, cfg["bgm"]), "-t", f"{body:.3f}", "-ar", str(SR), "-ac", "2", bgm])
    bgain = cfg.get("bgm_lufs", -33) - measure_i(bgm)
    if sfx is not None:                               # 音效混進配樂軌（一起被旁白壓低前先加上）
        yb, _ = sf.read(bgm, dtype="float32")
        g = 10 ** (bgain / 20); ys = np.zeros_like(yb); n = min(len(ys), len(sfx) - int(intro_len * SR))
        if n > 0: ys[:n] = sfx[int(intro_len * SR): int(intro_len * SR) + n]
        sf.write(bgm, yb * g + ys * 10 ** (cfg.get("sfx_db", -16) / 20), SR, subtype="FLOAT"); bgain = 0.0
    out = os.path.join(work, "mix.m4a")
    # 最後的 alimiter：總輸出限幅在 -3.6 dBFS（密集配樂經 AAC 編碼會往上衝約 2 dB；實測真峰值 -1.4 dBFS）（預告片配樂較大聲，旁白重疊時避免破音）
    fc = ("[0:a]apad[ia];[1:a]atrim=start=%.3f,asetpts=PTS-STARTPTS,adelay=%d|%d[na];[na]asplit[na1][na2];"
          "[2:a]volume=%.2fdB,afade=t=in:d=1.5,afade=t=out:st=%.2f:d=4,adelay=%d|%d[bg];"
          "[bg][na2]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=600[bgd];"
          + ("[na1]volume=0[nz];[ia][nz]" if cfg.get("_mute_narration") else "[ia][na1]")      # 預覽模式：旁白只用來壓低配樂
          + "[bgd]amix=inputs=3:normalize=0:duration=longest[m];[m]alimiter=limit=0.66:attack=3:release=80:level=false[a]") % (intro_len, intro_len * 1000, intro_len * 1000, bgain, body - 4, intro_len * 1000, intro_len * 1000)
    run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(root, cfg["intro_audio"]), "-i", norm, "-i", bgm, "-filter_complex", fc,
         "-map", "[a]", "-t", f"{total:.3f}", "-c:a", "aac", "-b:a", "256k", out])   # 192k 遇到密集鼓點會過衝到 -0.2 dBTP；256k 實測 -2.8
    return out


# ======================= 6. 字幕、章節 =======================
def ts(x):
    h, m, s = int(x // 3600), int(x % 3600 // 60), x % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)) % 1000:03d}"


def write_subs(lines, titles, mid, post, tag):
    sub_dir = os.path.join(mid, "字幕"); os.makedirs(sub_dir, exist_ok=True)
    srt = []
    for k, L in enumerate(lines, 1):
        srt += [str(k), f"{ts(L['start'])} --> {ts(L['end'] + 0.1)}", re.sub(r"[，。；：、]$", "", L["text"]), ""]
    zh = os.path.join(sub_dir, f"字幕_zh-TW_{tag}.srt"); open(zh, "w", encoding="utf-8").write("\n".join(srt))
    out = [zh]
    en_tsv = os.path.join(sub_dir, "英文字幕稿.tsv")
    if os.path.exists(en_tsv):
        en = dict(l.rstrip("\n").split("\t", 1) for l in open(en_tsv, encoding="utf-8") if "\t" in l)
        if all(L["id"] in en for L in lines):
            e = []
            for k, L in enumerate(lines, 1): e += [str(k), f"{ts(L['start'])} --> {ts(L['end'] + 0.1)}", en[L["id"]], ""]
            p = os.path.join(sub_dir, f"字幕_en_{tag}.srt"); open(p, "w", encoding="utf-8").write("\n".join(e)); out.append(p)
    ch = []
    for L in lines:
        if "scene_start" in L:
            t = 0 if not ch else L["scene_start"]
            ch.append(f"{int(t // 60)}:{int(t % 60):02d} {titles[L['scene']]}")
    cp = os.path.join(post, f"章節_{tag}.txt"); open(cp, "w", encoding="utf-8").write("\n".join(ch) + "\n"); out.append(cp)
    return out


# ======================= 7. 品質檢查 =======================
def qc(out, shots, total, report_path, notes):
    info = json.loads(run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,r_frame_rate",
                           "-of", "json", out]).stdout)
    r = run(["ffmpeg", "-i", out, "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
    lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1]); peak = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)[-1])
    bd = run(["ffmpeg", "-i", out, "-vf", "blackdetect=d=0.5:pix_th=0.05", "-an", "-f", "null", "-"]).stderr.count("black_start")
    # 推近平順度：抽查最長、沒有逐步出現的圖卡段；平順時逐格變化量穩定（變異係數小），整數像素取整時會「0、0、0、跳」
    cands = [s for s in shots if s["kind"] == "card" and len(s["variants"]) == 1] or [s for s in shots if s["kind"] == "card"]
    card = max(cands, key=lambda s: s["f1"] - s["f0"])
    skip = 0.5 + TRANS_LEN.get(card.get("trans"), 0.35)     # 避開進場轉場
    a = card["f0"] / FPS + skip; dur = min(5, (card["f1"] - card["f0"]) / FPS - skip - 0.5)
    raw = run_bytes(["ffmpeg", "-v", "error", "-ss", f"{a:.2f}", "-i", out, "-t", f"{dur:.2f}", "-vf", "format=gray", "-f", "rawvideo", "-"])
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.int16)
    dd = np.abs(fr[1:] - fr[:-1]).mean((1, 2))
    cv = dd.std() / max(dd.mean(), 1e-6)
    smooth = dd.mean() > 0.01 and cv < 0.6
    v = [s for s in info["streams"] if s["codec_type"] == "video"][0]
    rows = [("長度", f"{float(info['format']['duration']):.1f} 秒（預期 {total:.1f}）", abs(float(info['format']['duration']) - total) < 0.5),
            ("解析度／影格率", f"{v['width']}×{v['height']}／{v['r_frame_rate']}", v["width"] == W and v["height"] == H),
            ("整體響度", f"{lufs:.1f} LUFS（目標 -14 ± 1.5）", abs(lufs + 14) <= 1.5),
            ("峰值", f"{peak:.1f} dBFS（< -1）", peak < -1),
            ("意外的黑畫面（> 0.5 秒）", f"{bd} 處", bd == 0),
            ("推近是否平順（抽查一段圖卡）", f"{card['f0'] / FPS:.1f} 秒起 {len(dd)} 格：逐格變化 {dd.mean():.3f}，變異係數 {cv:.2f}（< 0.6）", smooth)]
    md = ["# 品質檢查報告", "", f"- 檔案：`{os.path.basename(out)}`", f"- 產生時間：{time.strftime('%Y-%m-%d %H:%M')}", "",
          "| 項目 | 結果 | 通過 |", "|------|------|------|"] + [f"| {a} | {b} | {'✅' if c else '⚠️'} |" for a, b, c in rows]
    if notes: md += ["", "## 需要注意", ""] + [f"- {n}" for n in notes]
    md += ["", "## 還需要人工抽查", "", "- 片頭、每幕第一張圖卡、影片素材段落、結尾", "- 右下角浮水印有沒有重複或疊影", "- 配音是否有唸錯或怪腔調"]
    open(report_path, "w", encoding="utf-8").write("\n".join(md) + "\n")
    return all(c for _, _, c in rows)


def run_bytes(cmd):
    return subprocess.run(cmd, capture_output=True).stdout


# ======================= 主流程 =======================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project"); ap.add_argument("--voice", default="auto", choices=["auto", "gemini", "zhiwei", "timing"])
    ap.add_argument("--post", default=None, help="輸出資料夾（預設 3_製作後/輸出成品；timing 預覽建議指定到暫存資料夾）")
    ap.add_argument("--workers", type=int, default=max(2, min(8, (os.cpu_count() or 4) // 2)))
    ap.add_argument("--only", type=float, default=None, help="只輸出前 N 秒（快速預覽）")
    a = ap.parse_args()
    proj = os.path.abspath(a.project)
    root, mid, spec, lines, titles = load_project(proj)
    cfg = spec["video"]; V = lambda p: os.path.join(root, p)
    work = os.path.join(mid, "剪輯專案", "build"); os.makedirs(work, exist_ok=True)
    post = os.path.abspath(a.post) if a.post else os.path.join(proj, "3_製作後", "輸出成品"); os.makedirs(post, exist_ok=True)
    notes = []
    t_start = time.time()

    # 1. 配音
    scene_dir = os.path.join(mid, "配音", "Gemini")
    engine = a.voice
    if engine in ("auto", "gemini"):
        ok = voice_gemini(lines, titles, scene_dir, cfg)
        if not ok and engine == "gemini": raise SystemExit("Gemini 配音不完整")
        engine = "gemini" if ok else "zhiwei"
        if not ok: notes.append("Gemini 配音不完整，本次使用 Zhiwei 暫定配音")
    if engine == "timing":                          # 沒有配音時的畫面預覽：依字數估長度，用極小聲的雜訊代替旁白
        work = os.path.join(mid, "剪輯專案", "build_timing"); os.makedirs(work, exist_ok=True)
        cfg["_mute_narration"] = True
        line_dir = os.path.join(work, "逐句_timing"); os.makedirs(line_dir, exist_ok=True)
        rng = np.random.default_rng(1)
        for L in lines:
            n = len(re.findall(r"[一-鿿]", L["text"])) + 1.5 * len(re.findall(r"[A-Za-z]+", L["text"]))
            sf.write(os.path.join(line_dir, L["id"] + ".wav"), (rng.standard_normal(int(n / 4.5 * SR)) * 0.02).astype(np.float32), SR, subtype="PCM_16")
    elif engine == "gemini":
        line_dir = os.path.join(mid, "配音", "逐句_gemini")
        notes += split_scenes(lines, titles, scene_dir, line_dir)
    else:
        line_dir = os.path.join(mid, "配音", "逐句_zhiwei")
        voice_zhiwei(lines, line_dir, cfg.get("zhiwei_rate", 1.2))
    log(f"配音：{engine}")

    # 2. 時間軸
    intro_len = cfg.get("intro_len", 4.0)
    total = build_narration(lines, line_dir, work, intro_len, cfg.get("pause_before"))
    if a.only: total = min(total, a.only)
    log(f"總長 {total / 60:.2f} 分鐘，{len(lines)} 句，{len(titles)} 幕")

    # 3. 圖卡
    shots, jobs = expand_shots(spec, [L for L in lines], total, V(cfg["intro"]), os.path.join(work, "cards"), root, proj)
    shots = [s for s in shots if s["t0"] < total]; shots[-1]["t1"] = total; shots[-1]["f1"] = round(total * FPS)
    for s in shots:
        if s["kind"] == "video" and not os.path.isabs(s["path"]): s["path"] = V(s["path"])
    if jobs:
        log(f"產生圖卡：{len(jobs)} 張")
        with ProcessPoolExecutor(a.workers) as ex: list(ex.map(_card_job, jobs))

    # 4. 畫面
    lst = render_video(shots, work, V(cfg["watermark"]), a.workers)

    # 5. 混音＋輸出
    sfx = make_sfx(shots, total, cfg.get("sfx_whoosh", True), cfg.get("sfx_hit", True)) if cfg.get("sfx", True) else None
    mix = mix_audio(root, work, cfg, total, intro_len, sfx)
    tag = engine if not a.only else f"{engine}_預覽"
    out = free_path(os.path.join(post, f"{cfg['name']}_{tag}.mp4"))
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", mix, "-map", "0:v", "-map", "1:a",
         "-c", "copy", "-t", f"{total:.3f}", "-movflags", "+faststart", out])
    log("輸出：", out)

    # 6. 字幕、章節
    for p in write_subs([L for L in lines if L["start"] < total], titles, mid, post, tag): log("字幕／章節：", p)
    json.dump(dict(total=total, engine=engine, intro_len=intro_len, scene_starts=[L["scene_start"] for L in lines if "scene_start" in L and L["scene_start"] < total], shots=[{k: v for k, v in s.items() if k != "variants"} | {"n": len(s.get("variants", []))} for s in shots]),
              open(os.path.join(work, "timeline.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # 7. 品質檢查
    rep = os.path.splitext(out)[0] + "_品質檢查報告.md"
    ok = qc(out, shots, total, rep, notes)
    log(("品質檢查全部通過" if ok else "品質檢查有項目要注意"), "→", rep)

    # 8. 上架文案另存純文字 .txt（使用者要求：以後都要有 .txt，方便複製到 YouTube）
    copy_md = os.path.join(proj, "3_製作後", "01_上架文案.md")
    if os.path.exists(copy_md):
        run([sys.executable, os.path.join(HERE, "..", "md2txt.py"), copy_md])
        log("上架文案 .txt：", copy_md[:-3] + ".txt")
    log(f"完成，共花 {(time.time() - t_start) / 60:.1f} 分鐘")


if __name__ == "__main__":
    main()
