# 品牌草案 v2（待核定）

AI Watch 使用同一 Logo、品牌色、六秒節奏與原創音訊，按題材切換片尾文案和 CTA；不是每次另換品牌。片尾影片均為 1920×1080／30fps、H.264／AAC，需後製接入，build.py 沒有獨立 outro 欄位。

| 題材 | 影片（相對本資料夾） | CTA |
|---|---|---|
| AI 趨勢 | ai-watch/outros/trends/outro_draft.mp4 | 下一個想追蹤的 AI 趨勢？ |
| 工具實測 | ai-watch/outros/tools/outro_draft.mp4 | 最想測試哪個功能？ |
| Coding／開發 | ai-watch/outros/coding/outro_draft.mp4 | 卡在哪個開發步驟？ |
| 開源專案 | ai-watch/outros/opensource/outro_draft.mp4 | 下一個想拆解的開源專案？ |

通用版仍為 ai-watch/outro_draft.mp4，各版本有對應獨立 WAV 與靜態圖；來源與音訊合成方式沿用 v1 的原創程式，不借用自然教室資產。theme_outros_review.png 是四題材概覽。

自然教室 v1 的葉片方案已淘汰。新片尾必須使用與影片右下角相同的熊掌原素材；目前未取得檔案，manifest 記錄 pending_approved_paw_logo_file，不產生替代 Logo 影片。收到原素材後使用：

```powershell
python -X utf8 scripts/create_brand_drafts.py --out assets/brand-drafts/v3 --blackbear-logo <原熊掌圖檔路徑>
```

沒有 --blackbear-logo 時只產生 AI Watch 草案；不會重新使用葉片替代。核定後另存無 DRAFT 正式版本，更新 profiles 核定路徑。
