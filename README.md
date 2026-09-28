# papaya-style-video

> 以「Papaya 電腦教室」風格規劃與製作 **不露臉、AI 配音、以螢幕錄影為主** 的軟體與 AI 工具教學影片的 Claude Skill。
> A Claude Skill for planning faceless, AI-narrated, screen-recording software/AI tutorial videos in the style of the Taiwanese YouTube channel "Papaya 電腦教室".

**Version:** 1.2.0（2026-09-29）

---

## 這個技能能做什麼

從一個教學主題開始，一路帶你走完：

| 階段 | 產出 |
|------|------|
| 0. 建立專案 | `1_製作前 / 2_製作中 / 3_製作後` 資料夾與專案卡 |
| 1. 選題評估 | 6 項指標評分、一句話承諾、敘事模式（A 圖層巡禮 / B 技巧清單 / C 故事主角 / D 從零建置） |
| 2. 操作步驟 | 收集真實操作步驟與踩坑紀錄（不編造功能） |
| 3. 腳本 | 章節表加上逐句稿（每句 ≤16 字，每分鐘約 310 字，用「好，」切段，結尾是固定句） |
| 3.5 英文逐字稿 | 中英對照逐字稿（一行對一行）、英文 SRT（時間碼沿用中文版） |
| 4. 分鏡 | 畫面類型、鏡頭推拉、網址標籤、TIP 角標、音效；40 秒法則 |
| 5. 上架文案 | 標題 × 5、說明欄（🔹 格式）、標籤、縮圖文案 × 3、主視覺生圖提示詞 |
| 6. 配音 | TTS 友善稿、聲線設定（不使用對嘴角色） |
| 6.5 多語言配音 | 英文（可換成其他語言）音軌：M&E、受時間限制的配音稿、逐句 TTS、對齊、上傳 YouTube 多語言音軌，讓觀眾切換 |
| 7. 發布 | 剪輯規範、免費授權的柔和配樂、中英雙字幕上傳、發布檢查、成效復盤 |

## Papaya 風格 30 秒速記

- 片頭約 4.5 秒 Logo → 「嗨，大家好」→ 20 秒內講完「是什麼、能做什麼、今天做什麼」
- 每分鐘約 310 字、每句 12–13 字、用「好，」切段、以「…就能…囉」收尾
- 螢幕錄影持續推拉；右下角網址標籤、TIP 角標；AI 插畫讓畫面換氣
- 高潮放在最後；固定結尾「我們下回再見，拜拜」；不喊訂閱
- 縮圖無人臉：工具名加一行好處（黃色模板或 AI 主視覺）

## 檔案結構

```
papaya-style-video/
├── SKILL.md                 技能主檔（工作流程 + 核心規則）
├── README.md                本檔
├── CHANGELOG.md             版本紀錄
├── VERSION                  目前版本號
└── references/
    ├── style-guide.md       完整風格規範（定位、標題、縮圖、片頭、結構、語氣詞庫、畫面、音樂）
    ├── templates.md         專案卡、選題、腳本、分鏡、剪輯、上架、發布、復盤範本
    └── prompts.md           縮圖與插畫生圖、TTS 聲線、英文逐字稿、多語言配音提示詞
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
```
幫這支影片做英文配音音軌，讓觀眾可以在 YouTube 切換成英文。
```

## 聲明

本技能只歸納公開影片的**結構、節奏與風格規律**，供學習與創作參考。
不包含也不應使用 Papaya 電腦教室的 Logo、片頭動畫、音樂或縮圖素材；請建立自己的品牌資產。

## 版本

請見 [CHANGELOG.md](CHANGELOG.md)。
