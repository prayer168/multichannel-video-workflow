# Changelog

格式參考 [Keep a Changelog](https://keepachangelog.com/)，版本號遵循 [SemVer](https://semver.org/)。

## [1.4.0] - 2026-09-29
### Added
- 階段 0.8「SEO 關鍵字研究」：`scripts/seo_keywords.py` 抓 YouTube 搜尋建議（需求）與搜尋結果前 N 支影片（供給：繁中比例、近 90 天數量、觀看數中位數），給出 🟢/🟡/⚪/🔴 機會判斷
- 階段 8「發布後 SEO 優化」：點閱率、流量來源、搜尋字詞報表 → 調整標題、說明欄、縮圖
- `references/seo.md`：YouTube SEO 規範（各項目的影響程度、關鍵字研究、標題、說明欄、章節、Hashtag、標籤、導流、發布後優化、禁止事項）
- `references/prompts.md` 新增 SEO 提示詞（關鍵字研究、SEO 版上架文案、發布後優化）
### Changed
- 標題：主要關鍵字必須在前 40 字內
- 說明欄：開頭加上 1–2 句含關鍵字的摘要（與 Papaya 刻意不同）
- 章節名稱使用觀眾的搜尋詞；Hashtag 3–5 個；標籤包含中英文、簡體與錯字寫法
- 腳本：開場 30 秒內旁白自然唸出主要關鍵字
- 選題雷達：推薦前 3 名後，加上搜尋需求檢查
- 發布清單：新增播放清單、結束畫面、資訊卡、英文標題與說明、置頂留言

## [1.3.0] - 2026-09-29
### Added
- 階段 0「選題雷達」：搜尋近 14 天國內外最新的 AI 模型、AI 工具或功能、開源專案、電腦軟體、組合技 → 15–25 筆候選（附來源與日期）→ 重複檢查（Papaya、YouTube 中文教學）→ 6 項評分 → 推薦前 3 名
- `references/topic-radar.md`：國外量化來源、國外產品與新聞、國內與中文圈、競品檢查的來源清單，以及報告格式與品質規則
- `scripts/topic_radar.py`：用公開 API 抓 GitHub 新興 repo、Hugging Face trending 模型與 Spaces、Hacker News 高分討論
### Changed
- 建立專案資料夾改為階段 0.5（題目選定後才建立）
- 選題評估新增「題目來源」與「重複檢查」欄位

> 1.2.0（多語言配音）已回滾，版本號不再使用。

## [1.1.0] - 2026-09-29
### Added
- 階段 3.5「同步英文逐字稿」：中英對照逐字稿（一行對一行）、英文 SRT（時間碼沿用中文版）、英文逐字稿.txt、英文上架文案（選用）
- `references/prompts.md` 新增英文逐字稿提示詞（含固定句英譯對照表）
- 專案結構新增 `2_製作中/字幕/`、`02_腳本_中英對照.md`
### Changed
- 音樂與音效：只用免費、非商用授權素材（YouTube 音效庫、Pixabay、Freesound CC0），風格柔和、輕鬆、簡單；需記錄授權
- 品牌尚未定案時使用暫代方案，並參照品牌待建立清單
### Removed
- 對嘴角色與虛擬主播模組（全片只用畫外音旁白）

## [1.0.0] - 2026-09-29
### Added
- `SKILL.md`：7 階段工作流程（專案建立 → 選題 → 步驟 → 腳本 → 分鏡 → 上架文案 → 配音 → 發布）
- `references/style-guide.md`：根據 6 支影片（逐字稿、說明欄、章節、影格）與 40 張縮圖歸納的風格規範
- `references/templates.md`：專案卡、選題評估、腳本、分鏡、剪輯、上架、發布、復盤範本
- `references/prompts.md`：縮圖與插畫生圖、TTS 聲線、對嘴吉祥物提示詞
- `README.md`、`VERSION`、`CHANGELOG.md`
