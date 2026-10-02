# 已核定片尾 v1

使用者於 2026-10-02 明確回覆「五版全部核定」。核定範圍：AI Watch 趨勢、工具實測、Coding、開源四支主題片尾，以及自然教室熊掌片尾的畫面、文案與音樂。正式版本移除 DRAFT，保留六秒節奏、Logo、文字與原音訊；歷史草案不覆蓋。

| 頻道／題材 | 正式影片（相對本資料夾） |
|---|---|
| AI Watch 趨勢 | ai-watch/outros/trends/outro.mp4 |
| AI Watch 工具實測 | ai-watch/outros/tools/outro.mp4 |
| AI Watch Coding | ai-watch/outros/coding/outro.mp4 |
| AI Watch 開源 | ai-watch/outros/opensource/outro.mp4 |
| 自然教室 | blackbear-science/outro.mp4 |

各影片皆有同資料夾的 outro_audio.wav 與 outro_still.png。manifest.json 記錄核定日期與頻道路徑，validation.json 記錄實際影音驗證。

自然教室 paw_approved.png 是使用者核定的截圖參考重建徽章，來源沿用草案 v3；不是原始高解析 Logo。原始圖檔日後可另版替換，不能悄悄改動已核定視覺。AI Watch 原創圖形與合成音訊來源沿用草案 v1／v2。

本次核定不包含 AI Watch 獨立片頭、浮水印、通用片尾、背景音床或旁白聲線。它們仍依原狀態待核定；不可把片尾核定擴大為全部品牌資產核定。

製作時依主要題材選一支核定片尾，完整影音以後製接入；build.py 沒有 outro／outro_audio 欄位，manifest 也不會自動載入。正式片尾來源已含音樂，不再重複疊加 outro_audio.wav；若分軌剪輯才另用 WAV。
