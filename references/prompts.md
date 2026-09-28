# 提示詞集

---

# 04 縮圖與插畫生圖提示詞

## A. 請 AI 設計縮圖主視覺的生圖提示詞
```
請為 YouTube 教學影片縮圖設計 3 個「無文字」主視覺的生圖提示詞（英文），主題：{{工具名／概念}}。
要求：16:9、電影感產品攝影或柔和 3D、單一主色調（配合 {{品牌色}}）、主體放在畫面右側 40%、左側保留乾淨的空白給文字、景深柔和、沒有任何文字或 Logo、沒有人臉。
每個提示詞附上：主體隱喻說明（例如「場記板＝動畫」「3D 地球 HUD＝全球監控」）。
```

## B. 主視覺生圖模板（直接貼到 Midjourney、Nano Banana、GPT-Image）
```
Cinematic product-style 3D render of {{象徵物件，例如 a glossy clapperboard with a play icon}}, placed on the right third of the frame, {{主色}} monochrome color palette, soft studio lighting, subtle floating particles, shallow depth of field, clean empty negative space on the left for title text, minimal, premium, high detail, 16:9, no text, no letters, no logo, no people
```

## C. 版型 A（黃色 Ep. 縮圖）的排版指示（給 Canva AI 或設計師）
```
1280×720 YouTube 縮圖。背景 #FFC72C 黃色，右下角有一個較淺的 #FFD95A 大圓弧色塊。左上角放 {{App 名稱}} 的圓角方形圖示（帶陰影）。
正中央偏左放主標「{{主標}}」：圓潤粗黑體、顏色 #2B2B2B、白色描邊 8px、再加一層外陰影。
主標右下方放黑色圓角膠囊，白字寫副標「{{副標}}」。
裝飾：右上角兩個深灰細線膠囊外框加短橫線、左下角兩條短橫線、底部一條細長橫線，線寬 2px。不要人臉、不要箭頭、不要 emoji。
```

## D. 影片內插畫（概念解釋、故事主角）
```
Soft 3D animated film style illustration (Pixar-like, gentle pastel palette, warm natural window light), {{場景描述，例如 a Taiwanese high-school boy in a navy-white track jacket reading a history book at a classroom desk}}, calm cozy atmosphere, clean composition, 16:9, no text
```
**角色一致性**：第一張生成後當作角色參考圖（character reference），之後的每一張都加上「same character as reference」。

## E. 動態化（image-to-video：Kling、Veo、Runway）
```
Subtle motion only: slow camera push-in, character blinks and turns a page gently, soft light flicker, 4 seconds, no scene change, no camera shake
```

## F. 工具標題卡
```
Dark navy background with floating glowing data particles and faint numbers, soft bokeh, centered empty space for a title, cinematic, 16:9, no text
```
（後製時再疊上工具 Logo 與名稱）

---

# 06 AI 配音提示詞

## A. 聲線描述（ElevenLabs Voice Design、MiniMax、OpenAI TTS 的 instructions 欄）
```
A warm, calm, friendly Taiwanese Mandarin male narrator in his 30s. Mid-low pitch, clear standard Taiwanese pronunciation (no retroflex exaggeration). Speaks like a patient computer teacher guiding a beginner step by step: steady pace around 310 Chinese characters per minute, slight smile in the voice, gentle rising tone on sentence-final particles like 囉 and 喔. Short natural pauses between sentences, a slightly longer pause after "好，". Never excited, never salesy, no dramatic emphasis.
```

## B. 中文版（給支援中文指令的 TTS）
```
台灣國語男聲，30 多歲，中低音，溫和、沉穩、帶微笑感，像一位很有耐心的電腦老師一步一步帶新手操作。語速平穩（每分鐘約 310 字），句尾的「囉、喔」輕輕上揚，句與句之間自然停頓，「好，」之後停頓稍長。不要激動、不要推銷感、不要戲劇化的重音。
```

## C. TTS 前的文稿處理提示詞
```
請把以下腳本整理成 TTS 友善格式：
1. 保留一行一句
2. 英文專有名詞若容易唸錯，在後面用【發音：…】標註（例如 Obsidian【發音：歐比迪恩】）
3. 數字轉成口語（2.5 → 二點五；10 至 15 美元 → 十到十五美元）
4. 括號中文 (努力) 只保留在字幕，TTS 版本改寫成「Effort，也就是努力」
5. 依章節切成多段，每段標示檔名，例如 03_人造衛星.txt
腳本：{{貼上}}
```

---

# 08 英文逐字稿（同步生成）提示詞

> 用途：中文逐句腳本定稿後，**同步產生一行對一行的英文逐字稿**，用來：
> ① 上傳英文 CC 字幕（en） ② 提供英文版說明欄或標題 ③ 日後製作英文配音版本
> 原則：**行數與中文完全一致、一行對一行**，這樣就能直接沿用中文字幕的時間碼。

## A. 腳本階段：中英對照逐字稿
```
請把以下中文逐句腳本翻譯成英文逐字稿，規則如下：
1. 一行中文對應一行英文，行數必須完全相同，不可以合併或拆行
2. 輸出成 Markdown 表格：| # | 中文 | English |
3. 語氣：friendly, calm, clear tutorial English（像耐心的電腦老師），不要逐字直譯
4. 每行英文 ≤ 42 個字元（字幕單行上限）；若太長就精簡用詞，但仍然維持一行
5. 固定句的英文對照：
   - 嗨，大家好 → Hi everyone
   - 好，那… → Alright, so… / OK, now…
   - 過了一會兒 → After a moment
   - 稍待片刻後 → Shortly after
   - …就 OK 了 → …and you're all set
   - …就能…囉 → …and you'll be able to…
   - 舉例來說 → For example
   - 也就是所謂的「X」→ which is what we call "X"
   - 你可以把它想成是… → Think of it as…
   - 那今天關於 X 的介紹，我們就聊到這邊 → That's all for today's introduction to X
   - 我們下回再見，拜拜 → See you next time, bye!
6. UI 按鈕名稱：用軟體的**英文原始介面名稱**，並加上雙引號，例如 點擊「儲存」→ click "Save"
7. 產品名、專有名詞保留原文；中文括號補充 (努力) 在英文版中刪除
8. 台灣在地的內容（地名、機構）使用官方英文名稱，例如 台北 101 → Taipei 101、桃園機場 → Taoyuan Airport

中文腳本：
{{貼上 02_腳本.md 的逐句稿}}
```

## B. 字幕階段：由中文 SRT 產生英文 SRT
```
以下是中文 SRT 字幕檔。請產生英文 SRT：
- 序號與時間碼完全保留，不做任何更動
- 只把每一條字幕的文字翻譯成英文（規則同 A 的 3–8 點）
- 輸出完整 SRT，不要省略
{{貼上 zh-TW.srt}}
```

## C. 上架階段：英文標題與說明欄（選用）
```
請為這支影片產生英文版上架文案：
1. English title × 3（≤ 100 字元；結構：hook + tool name + concrete benefit）
2. English description：用同樣的 🔹 區塊格式（Contents / Links / Support），時間碼沿用中文版
請參考中文版內容：{{貼上中文標題與說明欄}}
```

## 檔案命名
| 檔案 | 位置 |
|------|------|
| `02_腳本_中英對照.md` | `專案/1_製作前/` |
| `字幕_zh-TW.srt`、`字幕_en.srt` | `專案/2_製作中/字幕/` |
| `英文逐字稿.txt`（純文字、無時間碼） | `專案/3_製作後/` |

---

# 09 選題雷達提示詞

> 需要**有網路搜尋功能**的 AI（ChatGPT 搜尋或深度研究、Gemini、Claude 網頁搜尋、Perplexity…）。
> 完整規範：`03_影片製作工作流/1_製作前/00_選題雷達.md`

```
你是 Papaya 電腦教室風格教學頻道的選題研究員。今天是 {{今天日期}}。
請搜尋近 {{14}} 天國內外最新的：
1. AI 模型（新模型、版本升級、排行榜變動；LLM、生圖、影片、語音、本地模型）
2. AI 工具或新功能（ChatGPT、Claude、Gemini、Copilot、Notion、Canva、Adobe…）
3. 爆紅的開源專案（GitHub trending、Hugging Face trending、Hacker News）
4. 電腦軟體（生產力、系統工具、免費替代品）
5. 組合技或工作流（MCP、Skills、Agent、自動化串接）

請至少查以下來源：
- 國外：官方部落格或更新日誌（OpenAI、Anthropic、Google、Microsoft、Apple、Adobe）、GitHub Trending、Hugging Face、Hacker News、Product Hunt、Reddit（r/LocalLLaMA、r/ChatGPT、r/selfhosted）、The Verge、TechCrunch
- 國內與中文圈：iThome、數位時代、INSIDE、T客邦、電腦王阿達、Threads 科技圈、少數派、機器之心
- 重複檢查：YouTube 頻道 @papayaclass 最近的影片，以及 YouTube 上「工具名＋教學」的中文影片

篩選規則：
- 排除純論文、純開發者函式庫、加密貨幣、台灣無法使用的服務、沒有畫面可以展示的東西
- 優先：台灣可以使用、有免費方案、有 GUI、新手能在 15 分鐘內成功
- 近 3 個月已有中文教學的，標示「已有」；除非有新角度，否則淘汰

評分（每項 0–2 分，滿分 12）：熱度、省錢（免費、開源、取代訂閱）、具體成果（看完能帶走一個東西）、視覺衝擊、組合拳、門檻（越低越高分）

輸出格式：
# 選題雷達 {{日期}}（近 14 天）
## 本期重點（3 句話）
## 候選清單（15–25 筆）
| # | 名稱 | 類別 | 發布日 | 一句話說明 | 熱度證據 | 免費/開源 | 可展示畫面 | 重複檢查 | 熱度 | 省錢 | 成果 | 視覺 | 組合 | 門檻 | 總分 | 來源連結 |
## 推薦前 3 名（不要全部同一類）
每一名附上：為什麼現在拍、一句話承諾（看完你將能夠＿＿，而且不需要＿＿）、敘事模式（A 圖層巡禮／B 技巧清單／C 故事主角／D 從零建置）、暫定標題（Papaya 句型）、縮圖主標（≤6 字）與副標（≤12 字）、風險
## 放入選題庫
## 資料來源（名稱、網址、日期）

嚴格規則：每一筆都要有可以點開的來源連結與絕對日期；不確定的標示【待確認】；不可以編造產品、版本或功能。
```
