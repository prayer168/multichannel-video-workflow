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
> ① 上傳英文 CC 字幕（en） ② 提供英文版說明欄或標題 ③ 製作英文配音音軌（見 09_多語言配音提示詞.md）
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

# 09 多語言配音提示詞（YouTube 多語言音軌）

> 預設 `{{目標語言}}` = English（en）。要做日文、簡中等其他語言時，只要替換這個變數。
> 流程說明：`03_影片製作工作流/2_製作中/06_多語言配音.md`

## A. 配音稿（受時間限制的翻譯）
```
你是 YouTube 教學影片的配音翻譯。請把以下中文字幕翻譯成 {{目標語言}} 的「配音稿」，讓配音能放進原本中文每句的時間長度內。

規則：
1. 一條字幕對應一句配音，數量完全相同，不可以合併或拆開
2. 每句的「可用秒數」＝本句開始時間到下一句開始時間
3. 用這個語速估算：English 約每秒 2.7 個單字（日文約每秒 7 個假名、簡中約每秒 4.5 字）。若預估秒數大於可用秒數 × 0.95，就要精簡改寫：刪掉贅詞、改用短字，但保留操作步驟和按鈕名稱
4. 語氣：friendly, calm, patient computer teacher；口語、自然，不要逐字直譯
5. UI 按鈕名稱用軟體的 {{目標語言}} 原始介面名稱（English 加雙引號，例如 click "Save"）
6. 產品名、專有名詞保留原文
7. 若已經有中英對照逐字稿，請以它為基礎，只修改超時的句子
8. 固定句：開場「Hi everyone」、結尾「That's all for today's introduction to X. See you next time, bye!」（其他語言請用對應的自然說法）

輸出 Markdown 表格：
| # | 開始時間 | 可用秒數 | 中文 | {{目標語言}}（配音用） | 預估秒數 | 是否改寫 |

中文 SRT：
{{貼上 字幕_zh-TW.srt}}
（選用）既有的中英對照逐字稿：
{{貼上 02_腳本_中英對照.md}}
```

## B. 聲線設定（多語言版本，與中文版保持同一個講者）
```
Same narrator as the Mandarin version, speaking {{目標語言}}: warm, calm, friendly male voice in his 30s, mid-low pitch, clear and neutral accent. Sounds like a patient computer teacher guiding a beginner step by step. Steady pace, slight smile in the voice, natural short pauses between sentences. Never excited, never salesy.
```
建議工具：ElevenLabs（Multilingual 模型＋聲音複製），或其他支援跨語言保留音色的 TTS。

## C. 自動排列音檔的腳本（請 AI 撰寫）
```
請寫一個 Python 腳本（使用 ffmpeg），完成以下工作：
1. 讀取 字幕_zh-TW.srt 取得每句的開始時間
2. 讀取資料夾 逐句_{{語言代碼}}/ 裡的 001.wav、002.wav…（依序對應字幕的每一條）
3. 每個音檔依照開始時間用 adelay 放到正確位置；若某個音檔比可用秒數長，就用 atempo 加速，但最多 1.1 倍，並在終端機列出超時的句號
4. 把所有旁白混成一軌，再與 ME_音樂音效.wav 混音（旁白 -14 LUFS）
5. 輸出 音軌_{{語言代碼}}.wav，長度必須與 ME_音樂音效.wav 完全相同（用 apad/atrim 修正）
6. 最後輸出一份報告：總句數、加速的句子、超時仍無法放入的句子
```

## D. 檢查清單提示詞
```
以下是 {{目標語言}} 配音稿與每句實際 TTS 秒數。請找出：超過可用秒數的句子、加速超過 1.1 倍的句子、按鈕名稱和畫面可能不一致的句子，並提出改寫建議。
{{貼上表格}}
```
