# Motion Showreel 整合（2.28.0／子技能 0.8.0，2026-11-04）

把公開影片〈【經驗開源】AI 做動畫影片完全指南：原理、技巧、Skill 一次給全〉（Code 秘密花園／花園老師，使用者提供逐字稿，2026-11-04）的方法，以及影片開源的 **Motion Showreel** skill，接進本子技能。上游原始碼為 [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills) 的 `skills/motion-showreel`（MIT；審閱版本 `2b9a893`，2026-10-25，manifest 0.2.0）。

**整合方式（使用者 2026-11-04 決定）**：上游裝在使用者電腦的工具資料夾，由本技能**叫用它的腳本**（渲染、確定性、文字框景、成片硬指標、工作區預覽、混音），**不把上游的 SKILL、風格檔或程式碼複製進本 repo**。本文件以自己的話記錄做法、衝突時以誰為準和試跑結果；上游換版前先重新審閱，再改安裝腳本裡的釘選版本。

## 1. 逐字稿分析與採納判斷

| 影片內容 | 本技能原本已有 | 本次採納 |
|---|---|---|
| 影片＝一疊圖；網頁暴露「給時間就畫出那一刻」的函式，無頭瀏覽器逐格截圖，ffmpeg 合成；任何一秒都要能單獨畫出（並行渲染） | 有（`setT(t)`、固定種子） | 改用上游 `render.mjs --determinism` **實際驗證**，不再只靠寫法約定 |
| 依效果選技術：HTML/CSS、SVG 描線、Canvas 粒子、WebGL 質感後製、Three.js 3D、p5.brush 手繪 | 只有 repo 清單 | 新增「渲染層對照表」（`motion-graphics-ecosystem.md` 末節），附自然科例子 |
| 手繪線條的隨機抖動要固定；每隔幾格換種子，線條就會「活著」 | 只有固定種子 | 寫進對照表與試跑範本（每 4 格換一次種子） |
| 聲音也是程式算的；畫面和聲音讀同一張時間表，卡點比剪輯軟體準；有旁白時配樂與音效讓開；重擊前留一口氣 | 原創配樂＋ducking | 新增 `CUES` 音效提示表規則（本文件第 6 節）；`DROPS` 呼吸檢查只用在無旁白片頭／Shorts 開場 |
| 有旁白的片：先配好旁白，量出每句起訖，畫面照時間排 | 有（timing.json） | 匯入方式改用上游 `narration.mjs import`（帶時間戳） |
| 給對標作品，說清楚學什麼、不學什麼；先想三種講法再選 | 部分（風格卡） | 寫進 brief 必填欄（`studio-style-production.md`） |
| BPM 拍點網格、疏密起伏、高潮位置 | 只有 MV 分支 | 用在無旁白片頭與 Shorts 開場；有旁白時拍點服從旁白 |
| 好轉場是下一鏡從上一鏡長出來；同一時間只給一個焦點 | 部分 | 寫進 `../../references/image-led-motion-graphics.md` 製作原則 |
| 最常見的失敗是把旁白逐句做成標題卡，再用彈入和粒子包裝；**藏起字幕看一遍，光看畫面也懂才算** | 有「完整視覺覆蓋」 | 新增「反 PPT 檢查」為分鏡與成片驗收項 |
| 產品片：在 repo 內讓 AI 讀程式碼找賣點；給真實 logo／截圖／網址／品牌色；示範時加游標移動與點擊回饋 | 無 | 寫進 `../../profiles/ai-watch.md`「開源專案／產品介紹片」 |
| 要求 AI 以專業動態設計師身分質疑自己的方案；但要給可檢查的方法 | 有第三方看片 | 採「可檢查的方法」：抽幀表、手機尺寸抽幀、動作報告、文字框景、音訊圖；子 agent 獨立審片 |
| 先出幾張關鍵幀，方向對了再做動畫，節奏定了再渲高畫質 | 有（先靜幀後動態） | 併入三停點流程 |
| Skill 的三個停點：需求確認、風格幀、匯出前；其餘自己做 | 逐階段確認 | **動態圖文類影片改用三停點**（使用者 2026-11-04 決定，第 4 節） |
| 43 種風格檔（辨識信號、最俗的版本、配色、動法、聲音、踩坑） | 自有材質模板 | 依頻道挑候選（第 5 節）；只讀選中的 1–2 份 |
| 白板手繪＋人像縮在角落、概念形變講數學、蠟筆繪本講故事 | — | 對應自然教室的黑熊講課版型、概念解說、故事屋 |
| 「其他模型追不上 Opus」等模型比較說法 | — | 只當影片作者當時的個人說法，不當能力基準 |

## 2. 安裝與路徑

- Windows：執行 `scripts/install_motion_showreel.ps1`。它會 clone 到 `%USERPROFILE%\AI-Video-Tools\motion-explainer\ecosystem\garden-skills\`、checkout `2b9a893`，並在 `skills\motion-showreel\scripts` 安裝 Playwright＋Chromium 與 Tone.js，最後跑 `check-env.mjs`。安裝紀錄寫在同層的 `motion-showreel-安裝紀錄.log`。
- **踩坑**：上游 `scripts/package-lock.json` 的套件網址指向 `bnpm.byted.org`（非公開鏡像），照上游 `setup.sh` 會 403。安裝腳本會把它改名為 `package-lock.upstream.json`，改從 `registry.npmjs.org` 安裝。
- 環境檢查：`python scripts/preflight.py` 已加入「Motion Showreel」選用項，會顯示是否為釘選版本、Playwright 是否已裝。
- 以下以 `S` 代表 `...\garden-skills\skills\motion-showreel\scripts`。
- 上游自帶測試 `cd S && npm test`：雲端 2026-11-04 結果為 105 項中 101 通過、3 略過（Tone 未裝時）、1 失敗。失敗那項測的是「唯讀資料夾寫不進去」，在 root 權限下必然失敗，屬環境因素，不影響功能。

## 3. 衝突時以誰為準

規則優先順序不變：使用者本次指示 → `../../references/fixed-settings.md` → 頻道設定檔 → 本子技能 → Motion Showreel 上游預設。

| 項目 | 上游預設 | 本頻道做法 |
|---|---|---|
| 配音 | 內建 Gemini／MiniMax TTS | **不用**。正式配音依 fixed-settings（Achird＋固定 Style，AI Studio 或 `make_narration.bat`），經去爆音、聲線一致性檢核後，用 `narration.mjs import --audio <總軌.wav> --timestamps <句段.json>` 匯入 |
| 句段時間 | ASR 或使用者提供 | 優先用 `build.py`／`make_narration.py` 產生的逐句 timing（每句一個 WAV，時間是實際累加），轉成 `[{id,text,start,end}]`；沒有逐句 timing 時才用停頓偵測，並標明「未逐字對齊」 |
| 字幕 | 畫面內文字自由 | 不燒錄字幕；旁白不逐句上畫面；只交 `字幕_zh-TW_單行.srt`。`render.mjs --text-check --safe 40,60,220,40` 的底部 220 px 等於 y 860 以下（含 y 880–1000 字幕帶） |
| 右下角 | 無 | 黑熊講課角色區（約 x>1520、y>700，以 1920×1080 計）不放重要內容；`--text-check` 不檢查這區，要看抽幀表 |
| 片頭／片尾／講課角色 | 無 | showreel 段落當正片插段，**不內嵌品牌**。成片用 `scripts/showreel_to_bear.py` 疊黑熊，再依主技能 `append_outro.py` 接片尾、片頭依 fixed-settings |
| 配樂 | AI 合成或使用者曲 | 教學片沿用頻道原創 lo-fi（`--bgm <原創鋪底.wav> --bgm-source user`）；`score.mjs` 只合成有資訊作用的音效（`--sfx-source ai`） |
| 幀率 | 30 fps | 依本子技能的幀率表（紙張畫布／白板／資訊圖 60 fps），寫進 brief 鎖定 |
| 響度 | −14 LUFS、真峰值 ≤ −1 dBTP | 相同（與 build-pipeline 一致） |
| 字體 | 自托管於專案 `fonts/` | Windows 渲染一律把 Noto Sans TC（OFL）放進專案 `fonts/` 並 `@font-face` 宣告；雲端可用系統 Noto Sans CJK TC |
| 確認節點 | 三停點 | 採用（下一節），但主技能的配音檢核與實證比例仍要做 |

## 4. 動態圖文類影片的三停點流程（2026-11-04 起預設）

適用：畫面主要由程式產生的版面、圖解、地圖、卡片與攝影機運動構成的影片（含長片中的動態圖文段落）。實拍／錄屏為主的影片仍依 `video-editing-workflow`；主技能其他類型仍逐階段確認。使用者明說「中間不用問」時依其指示，交付時一併附上未選的方向。

| 停點 | 停下來給使用者看什麼 | 使用者確認後我自己做什麼 |
|---|---|---|
| **① 需求確認** | 一頁摘要：頻道、主題、**腳本定稿版本**、片長（以實際旁白為準）、畫幅（橫／直／兩者）、解析度與幀率、旁白來源（Achird 總軌）、BGM 來源（頻道原創／關閉）、音效來源（AI 合成／關閉）、實證比例目標、是否要「邊做邊看」。已知的不重問，一次問完缺的 | 寫 brief（對標、三種講法擇一、鉤子、記憶點、禁止清單）、分鏡、素材查找與授權記錄、匯入旁白並跑 `narration.mjs check` |
| **② 風格幀** | 已定風格：開場鉤子、記憶點、結尾 3 張真程式靜幀（`render.mjs --still … --sheet`）。未定風格：3 個拉開差距的方向各 1 張（`render.mjs --directions a,b,c --at …` → `qa/directions.png`），每個附 3–5 行迷你 brief。靠動作取勝的方向，另附 6–10 秒動作片段 | 逐鏡製作（每鏡開頭／中段／結尾靜幀自查＋連續格 `inspect.mjs strip`）、`--determinism`、`--text-check`、音效提示表、混音（`narration.mjs mix`） |
| **③ 匯出前** | 工作區預覽（Windows 本機：`node S/editor.mjs <專案> --size 1920x1080 --fps 60`，可拖播放頭、分軌調音量）。雲端無法開本機網址時，改傳 720p 預覽 MP4＋抽幀表，並註明是預覽 | 匯出 → 成片硬指標（第 7 節）→ 疊黑熊 → 接片尾 → 字幕 SRT → 審片紀錄 → 交付 |

「邊做邊看」：使用者在需求確認時表示想看過程，就先開 `editor.mjs <專案> --progress`，每完成一個階段（brief、風格幀、每一鏡、混音）發布一次（`progress.mjs`）。不增加停點，也不觸發 MP4 合成。只在 Windows 本機 Claude Code 可用；雲端改為每鏡完成時傳靜幀表。

## 5. 風格庫：依頻道的候選

只讀選中的 1–2 份風格檔（`references/styles/<slug>.md`），每支挑 2–3 個辨識信號，至少一個不在該風格「最俗的版本」裡，並寫進 brief。

- **黑熊老師的自然教室**：
  - `whiteboard-explainer`：原理、流程、因果；**試跑已驗證可配右下黑熊**。
  - `concept-morph`：科學概念連續變形，例如相變、月相、力的分解。
  - `blueprint`：構造與剖面，例如器官、儀器、植物構造。
  - `isometric-infographic`：生態系、校園觀察地圖。
  - `data-motion`：氣象署或官方數據。
  - `paper-cut`：節慶與故事。
  - `crayon-storybook`：故事屋。
  - `copperplate-engraving`：圖鑑感，例如復古天文圖鑑。
  - `shadow-puppet`：與既有「光影皮影戲」材質對應。
- **AI 觀測站**：
  - `minimal-ui`：工具介面示範，但真實介面仍要錄屏。
  - `terminal-ascii`：CLI、AI Coding。
  - `data-motion`：價格、基準、星數。
  - `dark-keynote`：發表會與新模型。
  - `swiss-editorial`：趨勢整理。
  - `hologram-hud`：系統架構。
- 與主技能 `references/advanced-animation.md` 的材質模板並存：模板是本頻道核定方向；上游風格檔只是候選來源。採用新風格前，仍依三停點的 ② 確認。

## 6. 音效提示表（`timeline.js` 的 `CUES`）

- 畫面事件和音效寫在同一張表，頁面和 `score.mjs` 都從這裡 import，所以一定對在同一格。
- 有旁白時，音效**放在句段之間的停頓或句尾**，避開句首與關鍵詞；只保留有資訊作用的動作（圈注完成、箭頭落定、數字定格），不每個動作都配音。
- 刻意的停留寫進 `HOLDS`，驗收工具會把它當作刻意靜止，不判成冷場。無旁白的片頭或 Shorts 開場若有重擊，寫進 `DROPS`，`audio.mjs check` 會量重擊前有沒有留一口氣。
- 有旁白時，拍點只當參考，不移動已確認的旁白時間。

## 7. 驗收：程式判定的硬指標＋人看的審片材料

1. **確定性**：`node S/render.mjs <專案> --size … --fps … --determinism` 必須通過才渲染。
2. **技術硬指標**：`build.sh`（`FPS=60 SIZE=1920x1080 AUDIO=file AUDIO_FILE=audio/final.wav sh build.sh`）會自動跑；**疊黑熊、接片尾後的最終檔要再跑一次**：
   `node S/inspect.mjs qa <成片.mp4> --out qa/final --expect-size 1920x1080 --expect-fps 60 --expect-duration <秒> --audio required`
   檢查可解碼、尺寸、幀率、時長、幀數、音軌、黑格、−14±1.5 LUFS、真峰值 ≤ −1 dBTP。**任何一項 FAIL 不交付**；有「NOT CHECKED」也不算通過。
3. **審片材料**（人判斷，不打分）：抽幀表、手機尺寸抽幀、凍結段、切點、逐鏡動作報告與閃格、文字框景標記圖、音訊波形／頻譜。
4. **反 PPT 檢查**：關掉字幕看一遍抽幀表或成片，光看畫面能不能看懂這段在講什麼；看不懂的鏡頭改分鏡，不靠加字。
5. **本頻道既有檢核照做**：去爆音與聲線一致性（最終旁白軌）、實證比例紀錄、SRT 單行、字幕安全區、右下黑熊區。
6. **獨立審片**：宿主支援子 agent 時，派一個沒參與製作的 agent 只看上述材料挑毛病。審片結論不能代替使用者看片。

## 8. 試跑紀錄（2026-11-04，雲端）

範本存於 `template/showreel-whiteboard-pilot/`（`index.html`、`timeline.js`、`score.mjs`、抽幀表）。用法：先 `sh S/scaffold.sh <新專案> --audio synth`，再把這三個檔案蓋上去。

- **內容**：白板手繪風格，14.6 秒，1920×1080，60 fps。分筆畫出黑面琵鷺 → 紅筆圈湯匙嘴 → 鏡頭右移畫示意遷徙路線（虛線，箭頭最後落定，標「示意路線，非實際航跡」）→ 推近圈出台南曾文溪口 → 拉遠成一張關係圖。右下疊核定黑熊老師（`showreel_to_bear.py`）。
- **旁白**：核定 Achird 參考樣本前 14.3 秒（未拉速）。去爆音檢查 0 處。句段邊界來自停頓偵測（雲端下載不到 Whisper 模型），**未逐字轉寫**，所以畫面只對齊句段，不保證與字句內容一致；這是管線驗證，不是成片。
- **結果**：
  - 確定性檢查通過（6 個時間點、不同渲染順序結果一致）。
  - 硬指標 9 項全過：876 格、60.00 fps、14.600 秒、無黑格、−14.3 LUFS、真峰值 −1.3 dBTP；疊黑熊後再驗一次也全過。
  - 渲染（含檢查）在雲端 2 核心約 1 分 17 秒。
- **審片抓到並修正的問題**：
  - 右對齊沒實作，「台南」圓點壓到字。
  - 「冬天來這裡」與箭頭重疊。
  - 推近時「北方繁殖地」貼到上緣。
  - 「示意圖」標籤在平台 UI 遮擋區，是 `--text-check` 抓到的。
  - 鏡頭右移時白板空了約 1 秒：連續格檢查看到，已提早讓下一個元素在移動中出現。
- **音訊報告**：WARN「低頻偏薄」，因為只有旁白和兩個音效；正式片接入原創 lo-fi 後再看。
- **尚未驗證**：Windows 本機安裝與 `editor.mjs` 工作區（本次無法取得使用者電腦資料夾權限）、Achird 逐句 timing 匯入、Tone.js 二檔音色、長片 `build-long.mjs`。驗證後回寫 `tool-choice.md`。

## 9. 來源與授權

- 影片逐字稿由使用者提供，只以自己的話摘要方法，不轉載原文。
- 上游程式為 MIT，著作權聲明見其 `LICENSE`；本 repo 只存放自寫的轉接腳本與試跑範本。範本的程式碼由本次試跑自行撰寫，`index.html` 頁面契約（`render(t)`／`READY`）與 `motion.js` 工具函式來自上游 scaffold，執行時才由 scaffold 複製。
- 上游的風格檔與 SKILL 文字留在上游 checkout 中閱讀，不複製進本技能。
