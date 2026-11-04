# 白板手繪＋右下黑熊：Motion Showreel 試跑範本（2026-11-04）

自寫的試跑頁面，用來驗證「Achird 旁白 → Motion Showreel 渲染與驗收 → 疊黑熊」整條管線。說明與結果見 `../../references/motion-showreel-integration.md` 第 8 節。

使用方式（`S` 為 Motion Showreel 的 scripts 路徑）：

```sh
sh S/scaffold.sh <新專案> --audio synth             # 先產生 motion.js、preview.js、build.sh
cp index.html timeline.js score.mjs <新專案>/        # 再蓋上本範本
node S/narration.mjs import <新專案> --audio <旁白總軌.wav> --timestamps <句段.json>
node S/audio.mjs build <新專案>/score.mjs && mv <新專案>/audio/music.wav <新專案>/audio/sfx.wav
node S/narration.mjs mix <新專案> --bgm <原創鋪底.wav或none> --bgm-source <user或none> --sfx <新專案>/audio/sfx.wav --sfx-source ai --duration <秒>
cd <新專案> && FPS=60 SIZE=1920x1080 AUDIO=file AUDIO_FILE=audio/final.wav sh build.sh
python <repo>/motion-explainer-workflow/scripts/showreel_to_bear.py <新專案> --out <輸出_黑熊講課.mp4>
```

- `timeline.js` 的 `SEG` 是試跑樣本的停頓偵測句段，換片時改成實際逐句 timing。
- 畫面內容（黑面琵鷺、示意路線）只為驗證管線，未依該片定稿腳本逐字對齊；路線標為示意，不代表實際航跡。
- `pilot_contact_sheet.png`：疊黑熊後成片的抽幀表。
