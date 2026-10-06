"""build.py 輸出後，把已核定的 AI Watch 片尾接到主片後面（build.py 沒有 outro 欄位）
用法：python append_outro.py <專案資料夾> <outro.mp4>
→ 取 3_製作後/輸出成品/ 裡最新、檔名不含「完整版」的 mp4（先跑 bear_presenter.py 時就是「_黑熊講課」版），輸出 <原檔名>_完整版.mp4"""
import glob, os, subprocess, sys
proj, outro = sys.argv[1], sys.argv[2]
d = os.path.join(proj, "3_製作後", "輸出成品")
cands = [p for p in glob.glob(os.path.join(d, "*.mp4")) if "完整版" not in os.path.basename(p)]
if not cands: sys.exit("找不到 build.py 輸出的影片")
main = max(cands, key=os.path.getmtime)   # 疊上黑熊講課後，最新的就是「_黑熊講課」版
out = main[:-4] + "_完整版.mp4"
fc = ("[0:v]fps=30,format=yuv420p,setsar=1[v0];[1:v]scale=1920:1080,fps=30,format=yuv420p,setsar=1[v1];"
      "[0:a]aresample=48000,aformat=channel_layouts=stereo[a0];[1:a]aresample=48000,aformat=channel_layouts=stereo[a1];"
      "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", main, "-i", outro, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out], check=True)
print("完整版：", out)
