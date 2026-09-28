# papaya-style-video

> 以「Papaya 電腦教室」風格規劃與製作 **不露臉、AI 配音、以螢幕錄影為主** 的軟體與 AI 工具教學影片的 Claude Skill。
> A Claude Skill for planning faceless, AI-narrated, screen-recording software/AI tutorial videos in the style of the Taiwanese YouTube channel "Papaya 電腦教室".

**Version:** 1.6.1（2026-09-29）

---

## 這個技能能做什麼

從一個教學主題開始，一路帶你走完：

| 階段 | 產出 |
|------|------|
| 0. 選題雷達 | 搜尋近 14 天國內外最新的 AI 模型、AI 新功能、爆紅開源專案、電腦軟體；15–25 筆候選（附來源）、重複檢查、評分、推薦前 3 名 |
| 0.5 建立專案 | `1_製作前 / 2_製作中 / 3_製作後` 資料夾與專案卡 |
| 0.8 SEO 關鍵字研究 | YouTube 搜尋建議（需求）＋搜尋結果競爭分析（供給）→ 機會判斷、主要與次要關鍵字 |
| 1. 選題評估 | 6 項指標評分、一句話承諾、敘事模式（A 圖層巡禮 / B 技巧清單 / C 故事主角 / D 從零建置） |
| 2. 操作步驟 | 收集真實操作步驟與踩坑紀錄（不編造功能） |
| 3. 腳本 | 章節表加上逐句稿（每句 ≤16 字，每分鐘約 310 字，用「好，」切段，結尾是固定句） |
| 3.5 英文逐字稿 | 中英對照逐字稿（一行對一行）、英文 SRT（時間碼沿用中文版） |
| 4. 分鏡 | 畫面類型、鏡頭推拉、網址標籤、TIP 角標、音效；40 秒法則 |
| 5. 上架文案（SEO 版） | 關鍵字在前 40 字內的標題 × 5、含摘要的說明欄、章節、Hashtag、標籤、英文標題與說明、置頂留言、縮圖文案 × 3 |
| 6. 配音 | TTS 友善稿、聲線設定（不使用對嘴角色） |
| 7. 發布 | 剪輯規範、免費授權的柔和配樂、中英雙字幕上傳、播放清單與結束畫面導流、發布檢查 |
| 8. 發布後 SEO 優化 | 點閱率、流量來源、搜尋字詞報表 → 調整標題、說明欄、縮圖 |

## Papaya 風格 30 秒速記

- 黑熊老師品牌片頭（約 4 秒，動畫＋配音口號）→ 「哈囉，大家好，我是黑熊老師」→ 20 秒內講完「是什麼、能做什麼、今天做什麼」
- 每分鐘約 310 字、每句 12–13 字、用「好，」切段、以「…就能…囉」收尾
- 螢幕錄影持續推拉；右下角網址標籤、TIP 角標；AI 插畫讓畫面換氣
- 高潮放在最後；固定結語「感謝大家觀看…想看什麼影片請在留言區留言…我們下次見，掰掰！」（黑熊老師版本，不用 Papaya 原句）；不喊訂閱
- 縮圖無人臉：工具名加一行好處（黃色模板或 AI 主視覺）

## 檔案結構

```
papaya-style-video/
├── SKILL.md                 技能主檔（工作流程 + 核心規則）
├── README.md                本檔
├── CHANGELOG.md             版本紀錄
├── VERSION                  目前版本號
├── scripts/
│   ├── topic_radar.py       抓 GitHub、Hugging Face、Hacker News 熱度原始資料
│   └── seo_keywords.py      YouTube 搜尋建議＋競爭分析（SEO 關鍵字研究）
└── references/
    ├── intro-spec.md        黑熊老師品牌片頭規格
    ├── topic-radar.md       選題雷達：來源清單、步驟、報告格式
    ├── seo.md               YouTube SEO 規範
    ├── style-guide.md       完整風格規範（定位、標題、縮圖、片頭、結構、語氣詞庫、畫面、音樂）
    ├── templates.md         專案卡、選題、腳本、分鏡、剪輯、上架、發布、復盤範本
    └── prompts.md           縮圖與插畫生圖、TTS 聲線、英文逐字稿、選題雷達、SEO 提示詞
```

## 安裝

**Claude Code（全域）**
```bash
git clone https://github.com/prayer168/papaya-style-video.git ~/.claude/skills/papaya-style-video
```

**Claude Code（單一專案）**：clone 到專案的 `.claude/skills/papaya-style-video`

**Claude.ai / Claude 桌面版**：把整個資料夾壓縮成 zip → 設定 → Capabilities → Skills → 上傳

**ChatGPT GPTs / Gemini Gem / Coze / Dify**：把 `SKILL.md` 的內容貼到指令欄，`references/` 的三個檔案上傳到知識庫

## 使用範例

```
幫我跑一輪選題雷達，看看最近兩週有什麼值得拍的。
```
```
幫我做「Claude Skills」的 SEO 關鍵字研究，看看有沒有機會。
```
```
我想用 Papaya 風格做一支 Obsidian 入門教學，對象是國中老師，長度大約 12 分鐘。
```
```
幫我把這份操作步驟寫成 Papaya 風格的逐句腳本，用故事主角型。
```
```
幫這支影片產生 5 個標題、說明欄和 3 組縮圖文案。
```
```
把定稿腳本同步產生中英對照逐字稿，再把 zh-TW.srt 轉成英文 SRT。
```

## 聲明

本技能只歸納公開影片的**結構、節奏與風格規律**，供學習與創作參考。
不包含也不應使用 Papaya 電腦教室的 Logo、片頭動畫、音樂或縮圖素材；請建立自己的品牌資產。

## 版本

請見 [CHANGELOG.md](CHANGELOG.md)。
