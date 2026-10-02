# 提示詞集

所有提示詞先代入頻道 ID、受眾與本集成果，讀取對應 `profiles/`；英文與 TTS 範例僅在有需求時使用。視覺模板依本頻道核定品牌調整，不沿用其他創作者縮圖。

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

## C. 本頻道縮圖的排版指示（給 Canva AI 或設計師）
```
為 {{頻道 ID}} 製作 1280×720 縮圖，使用 {{本頻道核定品牌色與素材}}。
以 {{本集真實成果或觀察問題}} 為主視覺，主標「{{主標}}」、副標「{{副標}}」簡短、手機可讀。
未核定識別時交付無品牌草稿，列出待建立素材；不套用另一頻道或 Papaya 的縮圖模板。
自然教室照片確認學生個資與授權；AI Watch 截圖遮蔽金鑰及帳號資料。
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
A warm, calm, friendly Taiwanese Mandarin male narrator in his 30s. Mid-low pitch, clear standard Taiwanese pronunciation (no retroflex exaggeration). Speaks like a patient computer teacher guiding a beginner step by step: a pace appropriate to the selected audience and topic, slight smile in the voice, gentle rising tone on sentence-final particles like 囉 and 喔. Short natural pauses between sentences, a slightly longer pause after "好，". Never excited, never salesy, no dramatic emphasis.
```

## B. 中文版（給支援中文指令的 TTS）
```
台灣國語男聲，30 多歲，中低音，溫和、沉穩、帶微笑感，像一位很有耐心的電腦老師一步一步帶新手操作。語速依所選頻道觀眾與內容調整，句尾的「囉、喔」輕輕上揚，句與句之間自然停頓，「好，」之後停頓稍長。不要激動、不要推銷感、不要戲劇化的重音。
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

# 08 英文逐字稿（依需求生成）提示詞

> 用途：中文逐句腳本定稿後，**同步產生一行對一行的英文逐字稿**，用來：
> ① 上傳英文 CC 字幕（en） ② 提供英文版說明欄或標題 ③ 日後製作英文配音版本
> 原則：**行數與中文完全一致、一行對一行**，這樣就能直接沿用中文字幕的時間碼。

## A. 腳本階段：中英對照逐字稿
```
請把以下中文逐句腳本翻譯成英文逐字稿，規則如下：
1. 一行中文對應一行英文，行數必須完全相同，不可以合併或拆行
2. 輸出成 Markdown 表格：| # | 中文 | English |
3. 語氣：friendly, calm, clear tutorial English（像耐心的電腦老師），不要逐字直譯
4. 保留必要資訊；逐字稿以句子 ID 對齊，字幕可在同一時間區段換行，不用固定行長刪除內容
5. 以下固定句對照僅自然教室適用；AI Watch 依自己的核定招呼與 CTA，不借用姓名：
   - 哈囉，大家好，我是黑熊老師 → Hi everyone, I'm Black Bear Teacher（英文名稱暫定）
   - 好，那… → Alright, so… / OK, now…
   - 過了一會兒 → After a moment
   - 稍待片刻後 → Shortly after
   - …就 OK 了 → …and you're all set
   - …就能…囉 → …and you'll be able to…
   - 舉例來說 → For example
   - 也就是所謂的「X」→ which is what we call "X"
   - 你可以把它想成是… → Think of it as…
   - 好，今天關於 X 的介紹，就到這裡 → That's all for today's introduction to X
   - 我是黑熊老師，感謝大家觀看這部影片 → I'm Black Bear Teacher, thank you for watching
   - 如果你希望黑熊老師接下來拍什麼影片，請在底下的留言區留言告訴我 → If there's a video you'd like me to make next, let me know in the comments below
   - 我們下次見，掰掰！ → See you next time, bye!
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
> 完整規範：`references/topic-radar.md`

```
你是 {{頻道 ID}} 的選題研究員。今天是 {{查證日期}}。
先讀取本頻道設定檔與 references/topic-radar.md，只搜尋相關題材。
自然教室以課綱、科學權威來源、觀察和課堂問題為主；AI Watch 以官方文件、公告、原始 GitHub、版本紀錄、論文及可重現實測為主，熱度僅供參考。
廣泛掃描可列較多候選，聚焦型不硬湊筆數。每筆附頻道、來源、發布與查證日期、觀眾需求、成果、重複檢查、評分理由與限制。
重複檢查以本頻道影片、選題庫與同類內容為主；Papaya 僅可能是 AI／軟體案例，不是自然教室淘汰條件。
各 0–2 分：受眾需求、可信度、具體成果、展示方式、差異化、製作可行性；補充本頻道適切性。
推薦至多三題，交代承諾、案例、暫定標題、縮圖、風險與為何適合本頻道。
有明確搜尋意圖才使用 SEO 工具；否則記錄學習或工作需求證據。
不能查證的資訊標示待確認，不編造功能、日期或實測。
```

---

# 10 SEO 提示詞

> 完整規範：`references/seo.md`
> A 段需要有網路搜尋功能的 AI；B、C 段任何 AI 都可以用。

## A. 關鍵字研究（沒有執行 seo_keywords.py 時使用）
```
我要做一支關於 {{工具名}} 的中文教學影片（台灣觀眾，繁體中文）。
請幫我做 YouTube 關鍵字研究：
1. 列出觀眾可能搜尋的關鍵字 15–20 個（中文、英文、中英混合、簡體寫法、常見錯字），並標示哪些是新手詞（教學、安裝、免費、中文、怎麼用）
2. 在 YouTube 搜尋「{{工具名}} 教學」，列出前 10 支影片：標題、頻道、觀看數、上傳日期、是不是繁中
3. 判斷機會：🟢 高（有需求、繁中教學少）/ 🟡 中（需要差異化）/ ⚪ 需求低 / 🔴 競爭高，並說明理由
4. 建議主要關鍵字 1 個、次要關鍵字 3–5 個，以及差異化角度
每一筆都要附上來源連結；不確定的標示【待確認】。
```

## B. SEO 版上架文案
```
請讀取 {{頻道 ID}} 設定檔，依本頻道語氣與適用的 SEO 規則產生上架文案。

【主要關鍵字】{{例如 Claude Skills 教學}}
【次要關鍵字】{{3–5 個}}
【影片腳本或重點】{{貼上}}
【章節與時間碼】{{貼上}}

規則：
1. 標題 × 5：清楚、可信、具體，準確反映成果；有搜尋意圖才自然加入關鍵字，不硬湊字數，不使用未經量測的數字承諾；推薦 1 個並說明理由
2. 說明欄：開頭 1–2 句摘要（150 字以內，自然融入主要與次要關鍵字）→ 🔹 內容綱要（章節名稱盡量包含觀眾會搜尋的詞）→ 🔹 提示詞連結 → 🔹 網站連結 → 🔹 支持 → 🔹 會員目錄 → Hashtag 3–5 個（依重要性排序，前 3 個會顯示在標題上方）
3. 標籤：主要關鍵字、次要關鍵字、工具名的各種寫法（英文、中文、簡體、常見錯字），總長 500 字元以內
4. 英文版（依需求）：English title（≤100 字元，關鍵字在前）與 English description 摘要
5. 置頂留言：重點摘要＋提示詞連結＋一個引導留言的問題
6. 禁止關鍵字堆疊、誤導性標題
```

## C. 發布後優化
```
這是我的影片發布 {{7}} 天後的數據：
- 標題：{{…}}
- 點閱率：{{…%}}，平均觀看百分比：{{…%}}
- 流量來源：YouTube 搜尋 {{…%}}、推薦 {{…%}}、外部 {{…%}}
- YouTube 搜尋字詞前 10 名：{{貼上}}

請分析：
1. 觀眾實際搜尋的詞與標題、說明欄的關鍵字是否一致？要不要修改？請給出新的標題 2 個、說明欄開頭摘要 1 個
2. 點閱率是否偏低？建議用「測試與比較」測試哪 2–3 種縮圖方向？
3. 有沒有新的關鍵字值得做成下一支影片（放入選題庫）？
```
