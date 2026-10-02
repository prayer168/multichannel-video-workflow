# 品牌素材草案 v1（2026-10-02）

後續修訂：自然教室葉片片尾已依使用者要求淘汰，必須換成影片右下角相同的熊掌原素材。AI Watch 的主題片尾見 ../v2/README.md。此資料夾保留歷史草案，不代表核定素材。

**全部待使用者核定，尚非正式品牌素材。** 影片與浮水印保留 DRAFT 標示；核定後另存正式檔案，不自動啟用草案。

## AI 觀測站（AI Watch）

觀測鏡頭／訊號軌道提案：夜藍 `#101626`、薄荷青 `#58E0CF`、白 `#F5F8FF`、灰藍 `#A5B2CB`。不使用熊掌、自然教室音樂或其他創作者素材。

- `ai-watch/logo_draft.svg`、`logo_draft.png`：同一觀測概念的向量與 512×512 透明點陣圖。
- `ai-watch/intro_draft.mp4`：4 秒；「看懂 AI 變化，親手做出能用的工具」。
- `ai-watch/outro_draft.mp4`：6 秒；CTA「留言分享：你想測試哪個工具或專案？」。
- `ai-watch/intro_audio_draft.wav`、`outro_audio_draft.wav`：獨立原創合成音訊，亦嵌入對應影片。
- `ai-watch/watermark_draft.png`：1920×1080 RGBA，右下角 AI WATCH／DRAFT，其餘透明。
- `ai-watch/bgm_draft.wav`：16 秒原創雙音環境音床，可循環，尚需試聽核定。
- 聲線提案：清楚自然的台灣國語，依術語與操作密度調整速度；未合成真人或 TTS 旁白，不模仿他人聲音。聲線與招呼待核定。

## 黑熊老師的自然教室

- `blackbear-science/outro_draft.mp4`：6 秒，以原創葉片表達觀察意象，沿用既有記錄的海軍藍／金黃，不冒充核定熊掌 Logo。
- 文案「把今天的發現，帶回生活裡」；CTA「留言分享：你觀察到了什麼？」。
- `blackbear-science/outro_audio_draft.wav`：原創三音收尾，已嵌入影片，不宣稱沿用既有品牌音樂。
- 既有核定片頭保留，其實檔與授權仍需在原品牌工作區確認。

## 規格、來源與接入

影片為 1920×1080、30fps、H.264／AAC；WAV 為 48kHz、16-bit、mono。`review_draft.png` 為概覽，各 `*_still_draft.png` 可單獨預覽。

`manifest.json` 以此資料夾為根記錄頻道與路徑，是交付清單，**不是 build.py 會自動讀取的設定**。AI Watch 預覽時將 intro、intro_audio、watermark、bgm 轉成實際絕對路徑，填入專案 video 設定，`intro_len: 4`；thanks 圖卡明確填本頻道姓名。完整片尾影音後製接入，程式沒有 outro／outro_audio 欄位。自然教室不得借用 AI Watch 草案補自己的片頭或浮水印。

圖形為 `scripts/create_brand_drafts.py` 原創幾何排版，音訊為數學波形原創合成，無外部圖片、音樂取樣或學生資料。文字以本機 Microsoft JhengHei 渲染，不散布字型檔；使用者依所用字型授權評估用途。來源記錄不代表商標獨占性保證。

重製需要 Python、Pillow、ffmpeg 與中文字型；必須輸出至新目錄，避免覆蓋：

```powershell
python -X utf8 scripts/create_brand_drafts.py --out assets/brand-drafts/v2
```

核定後移除 DRAFT、另存正式版本並更新 profiles 的核定狀態與路徑。正式發布前需完成這一步。
