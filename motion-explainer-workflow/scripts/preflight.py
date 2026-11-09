"""動態圖文工作環境檢查（motion-explainer-workflow 第 1 步）。

檢查 Node.js（≥22）、FFmpeg／FFprobe、中文字體（Noto Sans TC）、Remotion 專案、HyperFrames（含渲染用無頭 Chrome）。
只讀取、不安裝；缺必要項目時回傳 1，全部通過回傳 0。

用法：
  python preflight.py                                  # 預設根目錄 %USERPROFILE%\\AI-Video-Tools\\motion-explainer
  python preflight.py --root D:\\某處\\motion-explainer
  python preflight.py --json                           # 輸出 JSON（給 AI 讀）
  python preflight.py --skip-hyperframes-doctor        # 跳過較慢的 hyperframes doctor

根目錄結構（setup_windows.bat 建立）：
  remotion/      Remotion 4 專案（package.json＋node_modules）
  hyperframes/   HyperFrames 專案（package.json 內固定版本，例如 hyperframes@0.8.183）
  fonts/         Noto Sans TC（OFL）＋OFL.txt，隨專案打包
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys

NODE_MIN = 22
WIN = sys.platform.startswith("win")


def run(cmd, timeout=60):
    """執行指令，回傳 (returncode, stdout+stderr)。找不到程式回傳 (None, 訊息)。"""
    exe = shutil.which(cmd[0])
    if not exe:
        return None, f"找不到 {cmd[0]}"
    try:
        p = subprocess.run([exe] + cmd[1:], capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return None, f"{cmd[0]} 逾時（{timeout} 秒）"
    except OSError as e:
        return None, str(e)


def item(name, ok, detail, required=True, hint=""):
    return {"name": name, "ok": bool(ok), "required": required, "detail": detail, "hint": hint}


def check_node():
    rc, out = run(["node", "-v"])
    if rc != 0:
        return item("Node.js", False, out.strip(), hint="安裝 Node 22 LTS 以上：https://nodejs.org/")
    m = re.search(r"v(\d+)\.(\d+)\.(\d+)", out)
    major = int(m.group(1)) if m else 0
    return item("Node.js", major >= NODE_MIN, out.strip(),
                hint="" if major >= NODE_MIN else f"HyperFrames 需要 Node {NODE_MIN} 以上，請升級到 Node 22 LTS")


def check_tool(name):
    rc, out = run([name, "-version"])
    first = out.strip().splitlines()[0] if out.strip() else out
    return item(name, rc == 0, first if rc == 0 else out.strip(),
                hint="" if rc == 0 else "安裝 FFmpeg 並加入 PATH（Windows：winget install Gyan.FFmpeg）")


def check_fonts(root):
    proj = sorted(glob.glob(os.path.join(root, "fonts", "NotoSansTC*.*tf")))
    found = [os.path.relpath(p, root) for p in proj]
    sysdirs = []
    if WIN:
        sysdirs = [r"C:\Windows\Fonts", os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts")]
    else:
        sysdirs = ["/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.local/share/fonts"),
                   os.path.expanduser("~/.fonts")]
    sysfound = []
    for d in sysdirs:
        if os.path.isdir(d):
            for p in glob.glob(os.path.join(d, "**", "NotoSans*TC*"), recursive=True) + \
                     glob.glob(os.path.join(d, "**", "NotoSansCJK*"), recursive=True):
                sysfound.append(os.path.basename(p))
    lic = os.path.exists(os.path.join(root, "fonts", "OFL.txt"))
    if found:
        detail = "專案字體：" + "、".join(found) + ("（含 OFL.txt）" if lic else "（缺 OFL.txt 授權檔）")
        return item("中文字體（專案內）", True, detail, hint="" if lic else "把 OFL.txt 放進 fonts/ 一起打包")
    detail = "fonts/ 沒有 Noto Sans TC" + (f"；系統有 {', '.join(sorted(set(sysfound))[:3])}" if sysfound else "")
    return item("中文字體（專案內）", False, detail,
                hint="把 NotoSansTC 字體檔與 OFL.txt 放進 <root>/fonts/；渲染機器沒有字體時中文會變方框")


def read_json(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def check_remotion(root):
    proj = os.path.join(root, "remotion")
    pkg = read_json(os.path.join(proj, "package.json"))
    if not pkg:
        return item("Remotion 專案", False, f"找不到 {proj}\\package.json", hint="執行 setup_windows.bat")
    mods = {}
    for name in ("remotion", "@remotion/cli"):
        mp = read_json(os.path.join(proj, "node_modules", *name.split("/"), "package.json"))
        mods[name] = mp.get("version") if mp else None
    if not all(mods.values()):
        missing = [k for k, v in mods.items() if not v]
        return item("Remotion 專案", False, "尚未 npm install（缺 " + "、".join(missing) + "）",
                    hint=f"在 {proj} 執行 npm install")
    ver = mods["remotion"]
    ok = ver.split(".")[0] == "4"
    return item("Remotion 專案", ok, f"remotion {ver}、@remotion/cli {mods['@remotion/cli']}",
                hint="" if ok else "本技能以 Remotion 4 撰寫")


def hyperframes_version(root):
    pkg = read_json(os.path.join(root, "hyperframes", "package.json")) or {}
    for v in (pkg.get("scripts") or {}).values():
        m = re.search(r"hyperframes@([\w.\-]+)", v)
        if m:
            return m.group(1)
    return None


def check_hyperframes(root, doctor=True):
    out = []
    ver = hyperframes_version(root)
    if not ver:
        return [item("HyperFrames 專案", False, f"找不到 {os.path.join(root, 'hyperframes', 'package.json')} 或其中的固定版本",
                     hint="執行 setup_windows.bat")]
    rc, txt = run(["npx", "--yes", f"hyperframes@{ver}", "--version"], timeout=240)
    got = txt.strip().splitlines()[-1] if txt.strip() else ""
    out.append(item("HyperFrames CLI", rc == 0 and ver in got, f"固定版本 {ver}；npx 回報 {got or txt.strip()}",
                    hint="" if rc == 0 else "確認網路可連 npm registry，或在 Windows 重跑 setup_windows.bat"))
    if doctor and rc == 0:
        rc2, txt2 = run(["npx", "--yes", f"hyperframes@{ver}", "doctor", "--json"], timeout=240)
        m = re.search(r"\{.*\}", txt2, re.S)
        data = None
        if m:
            try:
                data = json.loads(m.group(0))
            except ValueError:
                data = None
        rows = [r for v in (data or {}).values() if isinstance(v, list) for r in v if isinstance(r, dict)]
        chrome = next((r for r in rows if r.get("name") == "Chrome"), None)
        if chrome:
            out.append(item("HyperFrames 無頭 Chrome", chrome.get("ok"), chrome.get("detail", ""),
                            hint=chrome.get("hint", "") or "npx hyperframes browser ensure"))
        else:
            out.append(item("HyperFrames 無頭 Chrome", False, "無法解析 hyperframes doctor 輸出", required=False,
                            hint="手動執行 npx hyperframes doctor"))
    return out


SHOWREEL_PINNED = "2b9a893"


def check_showreel(root):
    """Motion Showreel（garden-skills）：選用；動態圖文的三停點流程與成片硬指標會用到"""
    repo = os.path.join(root, "ecosystem", "garden-skills")
    scripts = os.path.join(repo, "skills", "motion-showreel", "scripts")
    hint = "執行 motion-explainer-workflow/scripts/install_motion_showreel.ps1"
    if not os.path.isfile(os.path.join(scripts, "render.mjs")):
        return item("Motion Showreel", False, f"找不到 {scripts}", required=False, hint=hint)
    rc, out = run(["git", "-C", repo, "rev-parse", "--short=7", "HEAD"])
    head = out.strip() if rc == 0 else "未知"
    has_pw = os.path.isdir(os.path.join(scripts, "node_modules", "playwright"))
    ok = has_pw and head == SHOWREEL_PINNED
    detail = f"{head}（釘選 {SHOWREEL_PINNED}）；playwright {'已安裝' if has_pw else '未安裝'}"
    return item("Motion Showreel", ok, detail, required=False, hint="" if ok else hint)


MV_PINNED = {"mv-director": "79af43a", "huashu-art-motion": "8a0d7d7", "lemo-opuscar": "143f387"}
MV_PROBE = """import importlib.util as u, importlib.metadata as md, sys
print(sys.version.split()[0])
for n in ('numpy', 'playwright', 'cv2', 'torch', 'transformers', 'demucs'):
    print(n, bool(u.find_spec(n)))
try: print('tfver', md.version('transformers'))
except md.PackageNotFoundError: print('tfver', '')
"""


def check_mv_tools(root):
    """音樂 MV／藝術動畫工具（install_mv_tools.ps1）：選用；做 MV 或借 huashu 解說語法時才需要"""
    eco = os.path.join(root, "ecosystem")
    hint = "執行 motion-explainer-workflow/scripts/install_mv_tools.ps1"
    out = []
    for name, pinned in MV_PINNED.items():
        repo = os.path.join(eco, name)
        if not os.path.isdir(os.path.join(repo, ".git")):
            out.append(item(name, False, f"找不到 {repo}", required=False, hint=hint))
            continue
        rc, txt = run(["git", "-C", repo, "rev-parse", "--short=7", "HEAD"])
        head = txt.strip() if rc == 0 else "未知"
        out.append(item(name, head == pinned, f"{head}（釘選 {pinned}）", required=False,
                        hint="" if head == pinned else "不是釘選版；換版前先審閱"))
    py = os.path.join(eco, "mv-venv", *(("Scripts", "python.exe") if WIN else ("bin", "python")))
    if not os.path.isfile(py):
        out.append(item("MV venv", False, f"找不到 {py}", required=False, hint=hint))
        return out
    rc, txt = run([py, "-I", "-c", MV_PROBE])
    lines = txt.strip().splitlines()
    got = dict(l.split(" ", 1) if " " in l else (l, "") for l in lines[1:])
    base = all(got.get(n) == "True" for n in ("numpy", "playwright", "cv2"))
    out.append(item("MV venv 基本套件", base, f"Python {lines[0] if lines else '?'}；numpy／playwright／opencv "
                    + ("已安裝" if base else "不齊"), required=False, hint="" if base else hint))
    tf = got.get("tfver", "")
    align = got.get("torch") == "True" and tf.split(".")[0].isdigit() and int(tf.split(".")[0]) >= 5
    out.append(item("MV 逐字對齊（torch＋transformers 5）", align,
                    f"torch {'已安裝' if got.get('torch') == 'True' else '未安裝'}；transformers {tf or '未安裝'}",
                    required=False, hint="" if align else "install_mv_tools.ps1 -WithAligner"))
    stems = got.get("demucs") == "True"
    out.append(item("MV 分軌（demucs）", stems, "已安裝" if stems else "未安裝", required=False,
                    hint="" if stems else "install_mv_tools.ps1 -WithStems"))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    default_root = os.path.join(os.path.expanduser("~"), "AI-Video-Tools", "motion-explainer")
    ap.add_argument("--root", default=default_root)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--skip-hyperframes-doctor", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)

    checks = [check_node(), check_tool("ffmpeg"), check_tool("ffprobe"), check_fonts(root), check_remotion(root)]
    checks += check_hyperframes(root, doctor=not a.skip_hyperframes_doctor)
    checks.append(check_showreel(root))
    checks += check_mv_tools(root)
    failed = [c for c in checks if c["required"] and not c["ok"]]
    result = {"root": root, "platform": sys.platform, "ok": not failed, "checks": checks}

    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"動態圖文環境檢查｜根目錄：{root}｜平台：{sys.platform}")
        for c in checks:
            mark = "✅" if c["ok"] else ("❌" if c["required"] else "⚠️")
            print(f"{mark} {c['name']}：{c['detail']}")
            if not c["ok"] and c["hint"]:
                print(f"   → {c['hint']}")
        print("結果：" + ("全部通過" if not failed else f"{len(failed)} 項必要項目未通過"))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
