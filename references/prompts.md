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

# 05 分鏡與剪輯指示提示詞

```
請把以下 Papaya 風格腳本轉成分鏡表（Markdown 表格）。

【腳本】{{貼上腳本}}

表格欄位：# | 預估時間 | 旁白（逐句）| 畫面類型（錄影/插畫/動態插畫/B-roll/標題卡/提示詞卡/角色）| 畫面內容 | 鏡頭（全景/推近×2/拉遠/平移/Ken Burns）| 標註（網址標籤/TIP 角標/紅箭頭/圈選）| 音效或音樂

規則：
- 0:00–0:05 是片頭 Logo，旁白從 0:03 開始
- 前 20 秒使用成果蒙太奇（插畫、B-roll、標題卡），不放安裝畫面
- 旁白提到「點擊、按下」的句子要推近到該按鈕；操作完成後拉遠
- 每個網站第一次出現時，右下角加網址標籤（停留 4 秒）
- 技巧型影片每個技巧開頭加「TIP N 主題」角標（停留 5 秒）
- 「過了一會兒」處標示【跳剪】
- 任何 40 秒內一定要有推拉、標註或換畫面；若沒有，請主動補上
- 概念解釋段落建議插入 AI 插畫，並附上一句英文生圖提示詞
- 最後輸出一份「素材清單」：需要錄的畫面、需要生成的插畫、需要的 B-roll
```

---

# 06 AI 配音與角色提示詞

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

## D. 對嘴吉祥物（選用）
**角色生成**
```
Cute mascot character for a computer-tutorial YouTube channel: {{例如 a friendly black bear teacher wearing round glasses and a hoodie}}, front-facing, mouth closed, neutral happy expression, soft 3D style, plain light background, full upper body, centered, 1:1, no text
```
**表情貼圖組**（同一角色）
```
Same character as reference, sticker sheet of 8 expressions: surprised, thumbs up, thinking, OK hand sign, confused with question mark, excited, waving goodbye, pointing right. White outline sticker style, transparent background, consistent design.
```
**對嘴影片**：把角色正面圖和配音音檔上傳到 HeyGen（Photo Avatar）、Hedra 或 Kling Avatar，輸出後去背，當成子母畫面使用。
