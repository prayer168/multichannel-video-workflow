# multichannel-video-workflow

> 以案例式、生活化和可跟做的教學結構，規劃與製作「黑熊老師的自然教室」或「AI 觀測站（AI Watch）」影片。使用獨立的頻道設定檔管理受眾、選題、查證、語氣與品牌影音。
> A channel-aware YouTube production skill for Black Bear Teacher's Nature Classroom and AI Watch.

**Version:** 2.18.0（2026-10-31）

## 2.18.0：自然教室選題雷達五類延伸題材

「黑熊老師的自然教室」選題雷達除了自然月曆，每輪再檢查五類題材：

| 類別 | 例子 |
|---|---|
| 🎐 自然科學相關節慶 | 中秋月亮、七夕織女星、世界濕地日、世界海洋日、黑琵保育季 |
| 🔭 天文大事 | 日月食、流星雨、行星合月、彗星、太空任務 |
| 🌏 環境生態最新議題 | 新種與新紀錄、外來種、珊瑚白化、保育成果 |
| 🧪 自然科學相關最新研究 | 近 90 天能連到國小自然概念的新論文 |
| 📚 有趣的自然科學小故事 | 科學史、生物奇聞、台灣自然史、迷思從哪裡來 |

另加入自然相關國際日月表、各類優先來源與查證規則（研究回到原始論文、預印本標示、軼事至少一個可靠來源）。細節見 [profiles/blackbear-science.md](profiles/blackbear-science.md) 與 [references/topic-radar.md](references/topic-radar.md)。

## 2.17.0：聲線一致性檢核

`scripts/build/voice_consistency_check.py` 逐句比對 Gemini 旁白的音高、亮度（頻譜重心）與音色（MFCC），標出偏離全片基準的句子，並把偏離句與不同次產生的接縫列成人工聆聽清單；是篩選工具，最後以使用者聆聽為準。

## 2.16.0：旁白驅動畫面設計

新增 `references/narration-led-visuals.md`：將定稿旁白逐句映射成畫面目的、主視覺動作、關鍵詞落點、停留與轉場，並附可直接交接動畫／剪輯代理的提示詞。文件含六支使用者提供影片的來源資訊與證據限制；以取得字幕或實際播放觀察的片段做深入分析，其他影片只列已核實的頁面資訊。

## 2.12.0：九套擴充材質

`references/advanced-animation.md` 新增 4.1 節：光影皮影戲、黑板粉筆、藍晒日光圖、立體翻翻書、桌面實物定格、燈箱沙畫、復古天文圖鑑、夜光星空、毛線刺繡。九套皆為**提案狀態**，配色、動作與成本為初估，第一次採用前先做一鏡測試，通過後再改為「已測試」。逐步引導的風格選單同步擴充為核心六套＋擴充九套。

## 2.11.0：黑熊老師的自然教室頻道定位

- 三句定位並存：主標語（頻道簡介）、身分標語（社群與片頭字卡）、選題標語（每次選題的檢核問句）
- 八個內容系列：黑熊實驗室、自然月曆、黑熊散步、一張白板看懂、自然故事屋、家裡的科學、黑熊的 AI 教具箱、老師的另一面
- 台灣自然月曆：每月季節錨點，選題先看接下來 1–2 個月
- 每月節奏（時令＋長青＋故事／老師／AI）與固定元素「考考你」「黑熊觀察任務」「迷思破解」
- 選題以時序與季節性為主，不以各校教科書版本或教學進度表排序

細節見 [profiles/blackbear-science.md](profiles/blackbear-science.md)。

## 2.13.0：動態圖文子技能與字幕改為不燒錄

新增子技能 [motion-explainer-workflow/SKILL.md](motion-explainer-workflow/SKILL.md)：旁白定稿後負責「畫面怎麼做」（定調風格卡與鎖定清單、委派任務卡、實證比例、靜幀條審片），渲染工具 Remotion 與 HyperFrames 都安裝，依分鏡選用。本版完成第 1 步：骨架、分工、`scripts/setup_windows.bat`（Windows 一次安裝）與 `scripts/preflight.py`（環境檢查）；方法文件、審片工具、樣片庫、實測與模板依建置順序補上。

| 項目 | 設定 |
|---|---|
| 分工 | 主技能：選題、腳本、配音、品牌、上架；本子技能：動態圖文畫面；`video-editing-workflow`：實拍剪輯 |
| 工作資料夾 | `%USERPROFILE%\AI-Video-Tools\motion-explainer\`（remotion／hyperframes／fonts） |
| 幀率 | 依風格在定調時鎖定：圖文與攝影機 60 fps、手作材質 30 fps、實拍為主跟隨素材 |
| 字幕 | **所有影片不燒錄**，只交付單行 SRT；`subs_oneline.py --burn` 僅在使用者要求時使用 |

## 2.10.0：嵌入字幕固定樣式與字幕安全區

字幕寫成固定設定，兩個頻道都照做，細節見 [references/subtitle-style.md](references/subtitle-style.md)：

| 項目 | 設定 |
|---|---|
| 行數 | 一次一行；橫式 ≤ 17 字、Shorts ≤ 12 字 |
| 樣式 | 白字＋黑框、淡陰影，不加底色；微軟正黑體粗體 58 級（Shorts 72 級） |
| 位置 | 水平置中、離下緣 96 px（Shorts 約在畫面高度 65%） |
| 時間 | 換行點對齊旁白停頓，每行至少 0.7 秒 |
| 字幕安全區 | y 880–1000 不放內容；`build.py` 預設 `subtitle_safe: true`，圖卡與動畫自動縮到 y 880 以上 |
| 程式 | `scripts/build/subs_oneline.py`；`build_video.bat` 最後自動產生單行 SRT 與 `_單行字幕.mp4` |
| 交付 | 無字幕版＋嵌入字幕版；YouTube 建議上無字幕版＋單行 SRT |

## 2.9.1：AI Studio 配音下載由 AI 操作

在 Google AI Studio 產生配音後，下載 WAV、確認檔案已存到電腦、改名 `S01-S02.wav` 並放進 `配音/Gemini/`，全部由 AI 操作，不再請使用者手動下載。流程與踩坑紀錄見 [references/fixed-settings.md](references/fixed-settings.md) 第一節。

## 2.9.0：觸動人心與留存的腳本規則

點閱率主要靠標題與縮圖，腳本負責讓觀眾看下去，留存再帶動推薦。新增 [references/style-guide.md](references/style-guide.md) 十條共用腳本規則與自我檢查表，並在 [profiles/ai-watch.md](profiles/ai-watch.md) 寫入 AI Watch 的套用方式：

| 規則 | 重點 |
|---|---|
| 三拍開場 | 前 30 秒：結果或衝突畫面 → 觀眾痛點 → 承諾與路線圖，招呼放在後面 |
| 觀眾當主角 | 功能是配角，「你終於可以＿＿」才是主角 |
| 懸念並兌現 | 章節結尾留鉤子；每個懸念都要在片中回答 |
| 真實卡關 | 「預期 → 實際 → 修正」段落，必須來自錄影或實驗紀錄 |
| 教學現場故事 | 有時間、地點、動作、情緒的真實小故事 |
| 節奏轉換 | 約每 45–60 秒換一次，腳本以 `[節奏轉換]` 標註 |
| 情緒弧線 | 好奇 → 期待 → 挫折 → 解決 → 成就感 |
| 結尾回扣 | 回到開場畫面、給今天能做的小行動、預告下一支 |
| 前 10 秒對上縮圖 | 縮圖承諾的東西，第一個畫面就給證據 |
| 具體留言問題 | 問得出答案的問題，回填選題雷達的需求證據 |

發布後用「觀眾續看率」曲線找下滑點，對照當下的腳本句子，把有效與無效的寫法回寫技能。這些是製作假設，不保證流量，也不能凌駕真實與可查證的原則。

---

## 2.8.0：AI 觀測站選題雷達擴充

依 2026-10-21 實際掃描的經驗，擴充 [references/topic-radar.md](references/topic-radar.md)：

| 項目 | 內容 |
|---|---|
| 新增三類題材 | 價格、方案與免費開放變動；安全、隱私與爭議澄清；教育與教師應用（AI Watch 由五類變八類） |
| 需求端訊號 | 本頻道留言、YouTube 搜尋建議、社群提問、Google Trends、研習問題；與 stars／新聞熱度分開記錄 |
| 附加評分 | 台灣可用性、需求證據、Shorts 延伸潛力各 0–2 分；核心 6 項 /12 保留，AI Watch 合計 /18 |
| 時效類型 | 每筆標示時事／長青，每輪保留 2–3 筆長青題 |
| 量化來源備援 | 雲端抓不到 GitHub／HF／HN／YouTube 時，改在使用者電腦跑腳本或用彙整來源補足，報告註明並標【待補】；`topic_radar.py` 失敗時自動附提示 |

---

## 2.7.0：AI 輔助剪輯與程式化動畫剪輯銜接

新增 `video-editing-workflow/SKILL.md` 作為可獨立使用的剪輯技能，並由本技能按素材量與剪輯任務路由。新增 [references/editing-workflow-methods.md](references/editing-workflow-methods.md) 與 [references/three-video-editing-analysis.md](references/three-video-editing-analysis.md)：彙整三份使用者提供逐字稿中的故事與分鏡設計、角色／場景連續性、素材盤點、AI 輔助粗剪、Remotion 動畫與 DaVinci 後製分工。

影片中的工具示範屬個別案例；技能把 AI 放在可檢查的粗剪和重複操作位置，保留人工確認鏡頭適用性、故事連貫、音訊與輸出的關卡。LibTV、DaVinci MCP、Remotion 等工具介面和可用能力須依當前官方資料與本機環境核對。

---

## 2.6.0：元件動畫與旁白逐句對齊

新增 [references/ui-narration-animation.md](references/ui-narration-animation.md)：UI 中有操作或教學用途的元件要有實際狀態變化；角色、鍵盤、螢幕、連動機關與遊戲角色各自有動作，語意事件依實際旁白時間觸發。加入木質程式模擬與真實錄屏的界線、左側放大黑熊講者／右側動畫版型、Flow 補段回退，以及逐句、逐元件與實際編碼影格驗收。解說文字以字幕為主。

此版整合製作與驗收契約；單集可外掛渲染。通用 JSON 轉接器和所有材質的共用渲染器尚未完成，不宣稱既有 build.py 能直接執行新契約。品牌造型、聲線及核定影音保持既有設定。

## 2.5.1：先選擇，再製作

新增 [references/guided-production.md](references/guided-production.md)：先選頻道，接受自訂題目或查證後推薦候選，再選材質、形式與時長、片頭，確認故事腳本及代表預覽後才製作完整影片。最新AI選題可依要求列10題附日期、來源、切入點與門檻。每輪只處理目前選擇，保留已選項；明確授權自行完成時不額外加關卡。未選風格不生成大量素材，預览未確認不製作全片。

## 2.5.0：進階動畫模組與溫馨材質模板

新增 [references/advanced-animation.md](references/advanced-animation.md)，整合雙頻道共用的導演、剪輯、動畫與教學規格：
- 六套核心材質：暖紙小劇場、晴日繪本、布布陪你學、木桌小世界、慢慢捏出來、暖光工作室。
- 九套擴充材質（2.12.0，提案狀態）：光影皮影戲、黑板粉筆、藍晒日光圖、立體翻翻書、桌面實物定格、燈箱沙畫、復古天文圖鑑、夜光星空、毛線刺繡。
- 九種動畫模組契約、資料分層與參數範例、字幕與主持安全區、錄屏混合、分鏡和品質驗收。
- 原版黑熊片頭繼續使用；繪本、紙藝、木作與科技桌片頭列為變體提案，保留核定Logo與角色。
- 同一18秒內容的三材質文字分鏡、相對成本、MVP及擴充順序。

**完成狀態：**工作流與規格已整合；新渲染器、JSON轉接器、新材質素材與片頭預覽尚未實作。不能直接把範例JSON送入既有build.py。片頭、配音、配樂、主持角色與頻道片尾沿用既有核定設定。

## 2.4.1：正式影片交付結構

主題根目錄下分主影片與三支Shorts，各有製作前／製作中／製作後；正式片使用台灣時間戳，上架文案整合為單一TXT，最終逐字稿獨立。詳見 [references/project-layout.md](references/project-layout.md)。

## 2.4.0：實測錄屏影片、AI 影片生成工具、旁白產生器

| 項目 | 內容 |
|---|---|
| 實測錄屏流程 | [references/real-test-workflow.md](references/real-test-workflow.md)：判定 AI 行為前一定回看錄影、先確認方案權限、實測當天檢查表、`--permission-mode default`、卡片框合成、片段表與抽格核對、分享版壓縮 |
| AI 影片生成工具 | [references/ai-animation.md](references/ai-animation.md)：Google Flow／Veo 等工具的建立角色、英文提示詞、挑選與命名；資訊動畫由程式繪製（角色表與素材 ID 依 animation-handoff.md） |
| 旁白產生器 | `scripts/build/make_narration.bat`＋`make_narration.py`：在使用者 Windows 依 `旁白資料.json` 以 Gemini Achird 兩幕一組產生 `配音/Sxx-Syy.wav`；只用標準函式庫、自動間隔 21 秒、額度用完可隔天接續 |
| 開發歷程 | [History.md](History.md)：每個版本的背景、實作案例與學到的事 |

實作案例：《AI 觀測站｜實測 Claude Mods》（2026-10-09～10）。

## 2.3.0：以證據驅動的 YouTube 成長與實測流程

新增 [references/youtube-growth-experiment.md](references/youtube-growth-experiment.md)，要求把「觀眾需求 → 產品能力查證 → 固定資料的三關公平實測 → 長片與 Shorts → 24h／72h／7d／28d 成效複盤」串成閉環。不得憑觀看數斷定推薦來源、虛構操作成果或預寫比較勝負；保留既有固定品牌與配音設定。

## 固定製作設定（2.1.0 起，兩頻道通用）

使用者 2026-10-06 定案，詳見 [references/fixed-settings.md](references/fixed-settings.md)：

| 項目 | 固定做法 |
|---|---|
| 片頭 | 黑熊老師片頭 4 秒＋定案片頭音訊（`assets/brand-approved/v1/blackbear-science/intro/`） |
| 配音 | Gemini `gemini-3.8-flash-tts`／**Achird**＋固定 Style（只換術語清單）；暫定只用 Windows Zhiwei，不用其他 TTS |
| 背景音樂 | 原創 lo-fi（`music/make_music.py` 產生），不用 Pixabay 曲當 BGM |
| 講課角色 | 核定黑熊老師依配音對嘴；一般沿用右下，動畫講解可採左側放大講者／右側動畫，需明確合成 |
| 片尾 | AI Watch 四種主題核定片尾／自然教室熊掌片尾（`scripts/build/append_outro.py`） |
| 字幕 | 2.13.0 起不燒錄：只交付單行字幕軌 SRT（對齊旁白停頓）；y 880–1000 為字幕安全區（`scripts/build/subs_oneline.py`、`references/subtitle-style.md`） |
| 一鍵產生 | Windows：`scripts/build/build_video.bat` 複製到專案資料夾雙擊，進度寫入 `產生紀錄.log` |
| 只產生旁白 | Windows：`scripts/build/make_narration.bat`＋`旁白資料.json`（2.4.0 起） |

## 頻道模式

本技能保留原有選題、影片生成與發布流程，新增兩個互斥的頻道設定檔。每個專案先選一個頻道，避免品牌、受眾和語氣混用。

| 設定檔 | 主要內容 | 品牌規則 |
|---|---|---|
| `profiles/blackbear-science.md` | 自然科教學、AI 數位教材、教學紀錄、科展與 STEAM | 使用自然教室核定片頭片尾與黑熊老師品牌素材 |
| `profiles/ai-watch.md` | AI 趨勢、AI Coding、開源軟體、軟體／網站／App 開發 | 沿用固定設定的黑熊片頭、主持人、Achird 與原創配樂，片尾依 AI Watch 主題選擇 |

兩個頻道共用案例式教學、生活例子、術語白話解釋、操作查證、分鏡、製作與復盤。PAPAYA 電腦教室只作為公開教學結構的研究參考，不使用其 Logo、音樂、片頭、原句或縮圖素材。

## 這個技能能做什麼

從一個教學主題開始，一路帶你走完：

| 階段 | 產出 |
|------|------|
| 0. 頻道路由與選題雷達 | 先選頻道設定檔，再依自然教育或 AI／軟體內容調整來源與評分；AI Watch 掃描八類題材、加計台灣可用性／需求證據／Shorts 潛力；候選附來源、日期、時效類型、重複檢查與推薦理由 |
| 0.5 建立專案 | 主影片與三支Shorts各自的製作前／製作中／製作後；舊工具結構只留在內部工作區 |
| 0.8 SEO 關鍵字研究 | YouTube 搜尋建議（需求）＋搜尋結果競爭分析（供給）→ 機會判斷、主要與次要關鍵字 |
| 1. 選題評估 | 依頻道設定檔評估受眾需求、可信度、成果、展示、差異化與可行性，並提出一句話承諾和敘事模式 |
| 2. 操作步驟 | 收集真實操作步驟與踩坑紀錄（不編造功能） |
| 3. 腳本 | 章節表加上逐句稿（語氣、句長、語速、開場與結尾依頻道設定檔） |
| 3.5 英文逐字稿 | 依頻道與使用者需求產出中英逐字稿或字幕 |
| 4. 分鏡 | 畫面類型、鏡頭推拉、網址標籤、TIP 角標、音效；依內容調整節奏 |
| 4.5 動畫與角色預覽 | 生活例子、原創配角、逐鏡動畫提示詞與多格場景預覽；核定黑熊角色保持原設定 |
| 4.6 進階動畫模組 | 六材質、九模組、片頭變體提案、配置與驗收；獨立影片和插段分開；新渲染器待實作 |
| 4.6.5 動態圖文 | 腳本定稿後，動態圖文類影片轉讀 `motion-explainer-workflow/SKILL.md`（風格卡、鎖定清單、Remotion／HyperFrames、靜幀條審片、實證比例） |
| 4.7 剪輯工作流 | 另用 `video-editing-workflow/SKILL.md` 處理大量素材、AI 輔助粗剪、動畫／錄屏混剪和成片驗收；本技能傳遞故事、旁白、分鏡、品牌和素材來源 |
| 5. 上架文案（SEO 版） | 依搜尋意圖與頻道語氣提出標題、說明欄、章節、Hashtag、標籤、需要時的英文文案、置頂留言與縮圖文案 |
| 6. 配音 | TTS 友善稿、固定 Achird 聲線與 Style；核定黑熊主持人依配音對嘴 |
| 6.5 一鍵產生影片 | `scripts/build/build.py`：依腳本＋畫面規格一次輸出影片（Gemini TTS 配音並自動清除頭尾雜訊、41 種圖卡含全幅照片、9 種教學模擬動畫、運鏡、7 種電影轉場、電影黑邊、配樂依相似度剪接、中英字幕、章節、品質報告）；`--voice timing` 可在沒有配音時先看畫面預覽 |
| 7. 發布 | 依頻道品牌與授權條款檢查配樂、字幕、播放清單、結束畫面導流與發布設定 |
| 7.2 製作素材包 | README、START_HERE、白名單素材清單、實測驗收資料與已有圖片；ZIP 附缺件清單、CRC 和 SHA-256 驗證 |
| 7.5 臉書宣傳文 | 影片完成時一併製作符合所選頻道品牌的宣傳文與分享圖；熊掌版 `fb_cover.py` 僅用於自然教室，AI Watch 使用核定素材或無品牌暫代版 |
| 8. 發布後 SEO 優化 | 點閱率、流量來源、搜尋字詞報表 → 調整標題、說明欄、縮圖 |

## 共用教學方法與頻道識別

- 兩頻道片頭、配音、配樂與黑熊主持人依固定設定；片尾按頻道與 AI Watch 主題選核定素材
- 共同方法是白話、循序、帶觀眾完成一個具體成果；速度、句長、口頭禪依頻道和主題調整
- 依頻道設定檔使用自己的開場、結尾、CTA、縮圖色彩和品牌元素；不套用另一頻道的固定台詞或視覺模板

## 頻道設定檔與路由

- `references/channel-routing.md`：頻道判定、規則優先順序與共用品質要求
- `profiles/blackbear-science.md`：自然教室專屬規格
- `profiles/ai-watch.md`：AI 觀測站專屬規格
- 若兩個頻道片頭、片尾或聲音資產尚未備齊，技能仍可完成選題、腳本與分鏡，並將缺少的素材列入交付清單。
- 素材剪輯、AI 時間軸與程式動畫任務另讀 [video-editing-workflow/SKILL.md](video-editing-workflow/SKILL.md)；完整方法與三份字幕分析見 `references/editing-workflow-methods.md`、`references/three-video-editing-analysis.md`。

## 檔案結構

```
multichannel-video-workflow/
├── SKILL.md                 技能主檔（工作流程 + 核心規則）
├── video-editing-workflow/SKILL.md  獨立剪輯技能（與企劃技能共用交接契約）
├── motion-explainer-workflow/       動態圖文子技能（2.13.0）：SKILL.md、scripts/preflight.py、scripts/setup_windows.bat；references／template 依建置順序補上
├── README.md                本檔
├── CHANGELOG.md             版本紀錄（Keep a Changelog 格式）
├── History.md               開發歷程：每版的背景、實作案例與學到的事
├── VERSION                  目前版本號
├── tests/test_fb_post.py     Facebook 頻道隔離、選用英文與保留原稿的 CLI 回歸測試
├── scripts/
│   ├── topic_radar.py       抓 GitHub、Hugging Face、Hacker News 熱度原始資料
│   ├── seo_keywords.py      YouTube 搜尋建議＋競爭分析（SEO 關鍵字研究）
│   ├── pack_video_bundle.py 白名單素材 ZIP、缺件清單與完整性驗證
│   ├── md2txt.py            上架文案 .txt＋YouTube標記.txt＋置頂留言.txt
│   ├── fb_cover.py          臉書分享圖 1200×630
│   ├── fb_post.py           臉書文一鍵複製頁（中英雙語；上傳後可代入 YouTube 網址）
│   └── build/               一鍵產生影片：build.py、cards_lib.py（41 種圖卡版型）、anims_lib.py（教學模擬動畫）、say_batch.ps1、
│                            bear_presenter.py（黑熊老師講課）、append_outro.py（接片尾）、subs_oneline.py（單行字幕軌；--burn 才燒錄）、narration_noise_check.py（去除摩擦聲／爆音檢核）、build_video.bat、make_narration.bat／make_narration.py（Gemini 旁白）
├── profiles/              自然教室與 AI 觀測站頻道設定
│   ├── blackbear-science.md
│   └── ai-watch.md
└── references/
    ├── build-pipeline.md    一鍵產生影片：指令、畫面規格格式、版型一覽、配音與額度、電影預告片風格、雜音／晃動／重疊的檢查方法
    ├── intro-spec.md        黑熊老師品牌片頭規格（含透明版、縮到角落版、浮水印）
    ├── production-notes.md  自動粗剪、浮水印規則、常見陷阱與品質檢查
    ├── topic-radar.md       選題雷達：來源清單、八類題材、需求訊號、附加評分、備援、報告格式
    ├── seo.md               YouTube SEO 規範
    ├── style-guide.md       完整風格規範（定位、標題、縮圖、片頭、結構、語氣詞庫、畫面、音樂）
    ├── fixed-settings.md    固定製作設定（片頭、Achird 配音、原創配樂、講課角色、片尾、一鍵檔、字幕）
    ├── subtitle-style.md    單行字幕、字幕安全區與 Shorts 字幕（2.10.0；2.13.0 起不燒錄）
    ├── real-test-workflow.md 實測錄屏影片流程（錄影為準、卡片框合成、片段表、旁白產生）
    ├── ai-animation.md      AI 影片生成工具操作（Google Flow 建立角色、英文提示詞、挑選命名）
    ├── guided-production.md 逐步引導選題、風格、形式、腳本、預覽與製作
    ├── advanced-animation.md 進階動畫模組：六材質、九模組、片頭選項、配置、分鏡、驗收與MVP
    ├── project-layout.md    正式主片與Shorts目錄、時間戳與整合上架文案
    ├── animation-handoff.md 生活化角色動畫、實測旁白分支、素材包與代理交接
    ├── templates.md         專案卡、選題、腳本、分鏡、剪輯、上架、發布、復盤範本
    └── prompts.md           縮圖與插畫生圖、TTS 聲線、英文逐字稿、選題雷達、SEO 提示詞
```

## 技能名稱與既有安裝遷移

自 2.0.0 起，GitHub repo、SKILL.md 的 `name`、新安裝資料夾與技能呼叫名稱統一為 **`multichannel-video-workflow`**。請以新名稱呼叫技能；具體呼叫語法依所用工具而定。

先前技能識別為 `papaya-style-video`；此名稱只保留在歷史紀錄與遷移說明，不再作為有效技能識別。改名不會自動搬動既有本機資料夾。

既有安裝遷移：
1. 檢查舊資料夾 `~/.claude/skills/papaya-style-video`（或專案 `.claude/skills/papaya-style-video`）的 git status，保留未提交變更與自訂素材。
2. 確認目的資料夾 `multichannel-video-workflow` 尚不存在，將原資料夾改名；若目的地已有安裝，先比對／備份，不覆蓋或直接刪除。
3. 將 remote 設為 `https://github.com/prayer168/multichannel-video-workflow.git`，以 `git pull --ff-only` 更新。遇到本地變更或分歧時先處理，不能 reset 丟棄工作。
4. 更新提示詞、快捷指令及外部引用為新技能名稱；Claude Code 重新開啟工作階段後確認新技能可用。其他工具同樣更新其 skills 根目錄中的資料夾名稱。
5. 不同時保留兩份完整技能供自動發現；舊呼叫不設隱藏別名，改用新呼叫方式。

本 repo 沒有 agents metadata、套件 manifest 或 CI 設定；SKILL metadata、安裝指令和 topic_radar.py 的 User-Agent 已同步使用新名稱。工作用 clone 的本機資料夾可以保留原路徑，不影響新安裝的技能名稱。

## 品牌素材與程式限制

2026-10-02 使用者已核定 AI Watch 四種主題片尾與自然教室熊掌片尾。正式檔案、核定範圍與來源見 [已核定片尾](assets/brand-approved/v1/README.md)，五支正式影片皆移除 DRAFT。片尾核定範圍不推導到其他資產；2026-10-06 新增的片頭、聲線、原創配樂與主持人固定設定以 `references/fixed-settings.md` 為準。歷史草案保留在 assets/brand-drafts/。

`build.py` 實際要求 `intro`、`intro_audio`、`watermark`、`bgm` 檔案，不支援 `outro`／`outro_audio` 或自動讀取 profiles。片尾可作最後一幕的畫面，但完整影音／長度需後製接入。無品牌預覽也須建立真實中性或靜音／透明檔案；不能拿待建立文字當路徑。詳見 `references/build-pipeline.md`。

`fb_cover.py` 有熊掌自動尋找邏輯，沒有無品牌開關，只用於自然教室。AI Watch 另製核定或無品牌分享圖。`fb_post.py --channel ai-watch`／`--channel blackbear-science` 指定頁尾；不指定為中性頁尾，英文文案可省略。之後用 `--url` 更新時仍帶相同 channel。所有宣傳文案、標籤與 CTA 依本頻道。

## 安裝

**Claude Code（全域）**
```bash
git clone https://github.com/prayer168/multichannel-video-workflow.git ~/.claude/skills/multichannel-video-workflow
```

**Claude Code（單一專案）**：clone 到專案的 `.claude/skills/multichannel-video-workflow`

**Claude.ai / Claude 桌面版**：把整個資料夾壓縮成 zip → 設定 → Capabilities → Skills → 上傳

**ChatGPT GPTs / Gemini Gem / Coze / Dify**：把 `SKILL.md` 的內容貼到指令欄，`profiles/` 兩個設定檔與 `references/` 需要的文件上傳到知識庫，保留相對路徑關係

## 使用範例

```
幫我為「黑熊老師的自然教室」設計一支四年級月相教學影片，生活例子要多，確認科學說法和適用年級。
```
```
幫我為「AI 觀測站（AI Watch）」評估這個開源專案，實際檢查 GitHub README、授權、安裝步驟和限制，再設計一支白話實測影片。
```

```
幫我跑一輪選題雷達，看看最近兩週有什麼值得拍的。
```
```
帶我一步一步實測 Claude Code 的這個新功能，錄下來剪成 AI 觀測站影片；結論要以錄影為準。
```
```
幫我把這幾段角色動畫的參考圖和 Google Flow 提示詞準備好。
```
```
幫我做「Claude Skills」的 SEO 關鍵字研究，看看有沒有機會。
```
```
幫我為「AI 觀測站（AI Watch）」規劃一支 Obsidian 教學影片，用生活工作案例帶觀眾完成一個可用的筆記流程。
```
```
幫我為「黑熊老師的自然教室」把月相觀察教材寫成逐句腳本，適合四年級學生，加入生活例子與科學查證。
```
```
幫這支影片產生 5 個標題、說明欄和 3 組縮圖文案。
```
```
用電影預告片的風格，加上教學模擬動畫，把這份腳本和分鏡圖做成影片。
```
```
影片做好了，幫我做臉書宣傳文。
```
```
把定稿腳本同步產生中英對照逐字稿，再把 zh-TW.srt 轉成英文 SRT。
```

## 聲明

本技能只歸納公開影片的**結構、節奏與風格規律**，供學習與創作參考。
不包含也不應使用 Papaya 電腦教室的 Logo、片頭動畫、音樂或縮圖素材；請建立自己的品牌資產。

## 最近更新

| 版本 | 日期 | 重點 |
|------|------|------|
| 2.18.0 | 2026-10-31 | 自然教室選題雷達五類延伸題材：自然科學相關節慶、天文大事、環境生態最新議題、自然科學相關最新研究、有趣的自然科學小故事；國際日月表、來源與查證規則 |
| 2.17.0 | 2026-10-30 | 聲線一致性檢核：`voice_consistency_check.py` 逐句比對音高、亮度與音色，列出偏離句與接縫交使用者聆聽 |
| 2.16.0 | 2026-10-23 | 旁白驅動畫面設計：`references/narration-led-visuals.md` 逐句映射畫面動作與交接提示詞 |
| 2.15.0 | 2026-10-22 | 去除摩擦聲／爆音檢核：`narration_noise_check.py`，配音到齊與成片前必跑 |
| 2.14.0 | 2026-10-22 | 動態圖文第一支實作（地球近日點）：Remotion／HyperFrames 同鏡實測與選用原則、實作經驗；TTS 產生後用語音辨識核對、使用者不在時改用 make_narration.bat |
| 2.13.0 | 2026-10-21 | 新增子技能 motion-explainer-workflow（動態圖文；Remotion＋HyperFrames、Windows 安裝檔、preflight 環境檢查）；所有影片改為不燒錄字幕，只交付成片＋單行 SRT |
| 2.12.0 | 2026-10-21 | 九套擴充材質（提案狀態）：皮影、黑板粉筆、藍晒、立體翻翻書、桌面實物定格、沙畫、復古天文圖鑑、夜光星空、毛線刺繡；風格選單同步 |
| 2.11.0 | 2026-10-21 | 自然教室頻道定位：三句定位標語、八個內容系列、台灣自然月曆、每月節奏與固定趣味元素；選題改以時序與季節性為主 |
| 2.10.0 | 2026-10-21 | 嵌入字幕固定樣式（一行、白字黑框、置中離下緣 96 px、對齊旁白停頓）、Shorts 字幕規格、字幕安全區（圖卡與動畫自動縮到 y 880 以上）、`subs_oneline.py` 與一鍵檔串接 |
| 2.9.1 | 2026-10-21 | AI Studio 產生與下載 WAV 一律由 AI 操作：五步流程、下載後確認檔案、改名歸檔；記錄 Run 被停用、下載位置等踩坑 |
| 2.9.0 | 2026-10-21 | 觸動人心與留存的十條腳本規則、腳本自我檢查表、AI Watch 套用範例、續看率曲線復盤；階段 3 開場改為三拍開場 |
| 2.8.0 | 2026-10-21 | AI Watch 選題雷達擴充：新增價格方案、安全爭議、教育應用三類；需求端訊號；台灣可用性／需求證據／Shorts 潛力附加評分；時事／長青標示；量化來源備援 |
| 2.7.0 | 2026-10-17 | 新增影片剪輯技能；整合素材盤點、AI粗剪、角色／場景連戲、Remotion與DaVinci分工及三份逐字稿時間碼分析 |
| 2.6.0 | 2026-10-15 | 元件狀態與旁白逐句對齊、持續角色與機關、木質UI模擬、左講者／右動畫、Flow回退與影格驗收 |
| 2.5.1 | 2026-10-14 | 加入逐步引導：頻道、自訂或推薦主題、風格、形式與時長、腳本、代表預覽，確認後製作；保留已選設定 |
| 2.5.0 | 2026-10-13 | 整合進階動畫規格：六種溫馨材質、九種模組契約、黑熊片頭變體提案、三材質文字分鏡、字幕與主持安全區、驗收與MVP；新渲染器待實作 |
| 2.4.1 | 2026-10-11 | 主片與三支Shorts交付結構、台灣時間戳、單一上架文案TXT與獨立最終逐字稿 |
| 2.4.0 | 2026-10-10 | 實測錄屏影片流程（錄影為準、卡片框合成、片段表與抽格核對）、AI 影片生成工具補充（Google Flow）、Windows 旁白產生器 `make_narration.bat`；新增 History.md；修正 2.3.0 字面 `\n` 換行；實作《AI 觀測站｜實測 Claude Mods》 |
| 2.3.0 | 2026-10-10 | YouTube 成長與實測驗證：流量來源、三關公平任務、短長影片導流、四時間點複盤 |
| 2.2.0 | 2026-10-08 | 生活化角色動畫、逐鏡動畫提示詞、分鏡預覽、實測旁白分支、Claude Code／Codex 製作交接與 ZIP 打包驗證 |
| 2.1.0 | 2026-10-06 | 固定製作設定寫入技能：黑熊老師片頭、Achird 固定 Style、原創配樂、右下角黑熊老師講課（bear_presenter.py）、片尾後製（append_outro.py）、Windows 一鍵檔；AI Watch 改用黑熊品牌；首支實作《Claude Mods vs ChatGPT Dots》 |
| 2.0.0 | 2026-10-02 | 技能識別與安裝資料夾統一改名 multichannel-video-workflow；提供既有安裝遷移說明 |
| 1.14.3 | 2026-10-02 | 五支片尾經使用者核定，正式版移除 DRAFT 並更新路徑 |
| 1.14.2 | 2026-10-02 | 依影片截圖完成熊掌片尾重建草案，待核定 |
| 1.14.1 | 2026-10-02 | AI Watch 四種主題片尾；自然教室改用原熊掌，等待素材 |
| 1.14.0 | 2026-10-02 | 新增分頻道原創品牌素材草案與重製腳本；待核定，保留正式素材缺口 |
| 1.13.1 | 2026-10-02 | 完成多頻道規則查漏、製作器實際素材欄位與片尾限制、品牌缺口及改名相容說明；Facebook 複製頁支援頻道識別與選用英文 |
| 1.13.0 | 2026-10-02 | 新增自然教室與 AI 觀測站兩個頻道設定檔、頻道路由與品牌資產隔離規則；標題、旁白節奏與英文素材改為依頻道設定，不再一律套用同一品牌 |
| 1.12.1 | 2026-10-01 | 臉書發文方式說明（避免貼出後沒有縮圖） |
| 1.12.0 | 2026-10-01 | 臉書宣傳文：影片完成時一起產生中英文案、分享圖、一鍵複製頁 |
| 1.11.1 | 2026-10-01 | 修正 TTS 頭尾雜訊、轉場凍結造成的頓挫、字卡與動畫重疊；配樂依頻譜相似度跳接 |
| 1.11.0 | 2026-10-01 | 電影預告片風格（運鏡、轉場、黑邊）、全幅照片版型、9 種教學模擬動畫、timing 預覽 |

實作範例：《讓數位工具走進科學探究》（2026-10-07 蓮潭國小研習引起動機影片）

## 版本

請見 [CHANGELOG.md](CHANGELOG.md)。

## 本版檢查

2.12.0：核對 advanced-animation.md 4.1、guided-production.md 階段 3 與 README 的材質清單一致，以及 README／SKILL.md／CHANGELOG.md／VERSION 版本；`git diff --check` 通過。九套擴充材質只有文字規格，尚未產生代表預覽或渲染測試。

2.11.0：核對 blackbear-science.md、topic-radar.md 與 SKILL.md 階段 0／1 的選題規則一致（不再以教學進度表排序、改看自然月曆與內容系列），以及 README／SKILL.md／CHANGELOG.md／VERSION 版本；`git diff --check` 通過。此版為頻道定位與選題規則，沒有新增程式；月曆中的確切日期每年選題時重新查證。

2.9.0：核對 style-guide.md、ai-watch.md、SKILL.md 階段 3／8 與 History.md 的規則一致，確認新開場規則與既有「不把高潮放最後當硬性規則」「頻道招呼方式」沒有衝突，以及 README／SKILL.md／CHANGELOG.md／VERSION 版本；`git diff --check` 通過。此版為寫作規則與檢查表，沒有新增程式，尚未用於完整影片並以續看率資料驗證。

2.8.0：核對 topic-radar.md、ai-watch.md、SKILL.md、History.md 階段 0 的規則一致，以及 README／SKILL.md／CHANGELOG.md／VERSION 版本；`topic_radar.py` 通過語法檢查，並在雲端（GitHub／HF／HN 皆 403）實跑確認輸出附加備援提示；既有單元測試通過；`git diff --check` 通過。新評分欄位已用於 2026-10-21 AI 觀測站選題雷達的規則設計，但尚未以新格式完整重跑一輪。

2.7.0：核對三份 SRT 摘要與時間碼、技能路由、參考連結及 README／SKILL.md／CHANGELOG.md／VERSION 版本；`git diff --check` 通過。此版新增的是工作流程文件與技能說明，沒有新增程式或渲染功能，也未執行程式測試或完整影片剪輯驗收。

2.5.1：檢查技能格式、版本與新增參考鏈結；以不同階段的使用者訊息檢查流程銜接。未製作新的完整影片，2.5.0渲染器仍為待實作設計。

2.5.0：規格、路由與參考鏈結整合；核對既有產生器和品牌檔案，檢查版本一致性、技能格式與新JSON示例。未執行新動畫渲染或服務API，不將設計版宣稱為可執行模組庫。

2.4.0：`make_narration.py` 已做語法檢查與無金鑰路徑測試；同一份程式（固定路徑版）已交付使用者 Windows 使用，實際呼叫 Gemini 待使用者執行後確認。卡片框合成、片段表與分享版壓縮流程已用於《實測 Claude Mods》預覽 v0.1～v0.4（7:14，1920×1080）。Google Flow 流程為首次導入，以使用者截圖為準逐步帶操作。

2.2.0：素材打包已測試中文檔名、ZIP CRC 與 SHA-256、待補清單、必填缺件、危險路徑與符號連結拒絕；以 Docker 題目完成流程驗證。未執行本版完整影片渲染或平台發布。首頁版本、VERSION、SKILL.md 與 CHANGELOG 已同步。

2.1.0：`bear_presenter.py` 已在雲端容器以 45 秒片段實測（對嘴、手勢、片頭不出現角色）；`build_video.bat` 的 build／配音流程已在使用者 Windows 實跑。

執行 `python -X utf8 -m unittest discover -s tests -v` 驗證 Facebook 頻道頁尾、無英文輸入、HTML 跳脫、連結更新與原稿／多次匯出保留；執行 `python -X utf8 -m compileall -q scripts tests` 檢查 Python 語法。文件以版本比對、資源路徑／連結、表格欄位、程式碼區塊、舊規則搜尋與 `git diff --check` 檢查。

1.13.1 更新未執行 Gemini API 配音、完整教學影片渲染或平台發布；1.14.0 已實際生成並驗證三支品牌短片草案，未執行旁白 API 或發布。外部品牌素材未找到實檔，素材狀態已據實標示。原有 build、TTS、字幕、SEO、上架文字轉換與熊掌分享圖程式均保留。
