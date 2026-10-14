# Changelog

格式參考 [Keep a Changelog](https://keepachangelog.com/)，版本號遵循 [SemVer](https://semver.org/)。

## [2.5.1] - 2026-10-14
### Added
- references/guided-production.md：逐步引導模式、七階段選擇、最新AI候選搜尋、決策狀態與停止恢復規則。
### Changed
- 技能入口先路由引導模式：接受自訂或推薦主題，依序選風格、形式／時長、腳本、預覽，再製作。
- 未選設定不視為定案；已選項不重問；明確完整製作授權不額外插入關卡。

## [2.5.0] - 2026-10-13
### Added
- references/advanced-animation.md：雙頻道溫馨動畫工作流、六套材質模板、九種模組契約、片頭變體提案、需求表、生圖與動畫提示詞、分鏡與驗收。
- 同一18秒內容的紙藝／毛氈／數位插畫文字分鏡與相對成本，MVP及擴充順序。
### Changed
- SKILL.md加入進階動畫按需路由與階段4.6；animation-handoff與fixed-settings加入銜接說明。
- README補齊2.4.1交付目錄、版本紀錄及2.5.0可用範圍。
### Implementation status
- 新配置、渲染器與片頭仍為設計；既有品牌、聲線、配樂和影片管線保持核定設定。

## [2.4.1] - 2026-10-11
### Changed
- 主題根目錄以主影片名稱命名，下設主片及三支 Shorts，各有製作前／製作中／製作後。
- 正式 MP4 加上台灣時間 YYYYMMDD_HHMMSS；上架標題、說明欄、Tags、置頂留言整合為單一 TXT，最終逐字稿獨立。
- 新增 references/project-layout.md，交付目錄與舊工具工作區分開；現有專案不因技能更新自動搬移。

## [2.4.0] - 2026-10-10
### Added
- `references/real-test-workflow.md`：實測錄屏影片流程——結論只能來自錄影、開拍前確認方案權限、實測當天檢查表、`claude --permission-mode default`、乾淨資料夾與新對話、OBS 設定、卡片框合成（透明窗＋overlay）、片段表格式、抽格核對時間點、中斷 mkv 重新封裝、快轉標示、分享版壓縮、預覽版本與缺件清單。
- `references/ai-animation.md`：AI 影片生成工具操作補充（Google Flow／Veo 等）——角色動畫與資訊動畫分工、角色參考圖與「建立角色」、英文提示詞結構（共用 Style＋Avoid）、挑選與命名；角色表與素材 ID 仍依 `animation-handoff.md`。
- `scripts/build/產生旁白.py`、`產生旁白.bat`：在使用者 Windows 依 `旁白資料.json` 以 Gemini `gemini-3.8-flash-tts`／Achird 兩幕一組產生 `配音/Sxx-Syy.wav`；只用標準函式庫、可指定 `--data`／`--out`／`--model`／`--voice`／`--wait`、自動間隔 21 秒、已存在跳過、403／429 停下隔天接續。
- `History.md`：開發歷程（每版背景、實作案例、學到的事）。
### Changed
- SKILL.md：引用新文件；階段 2 加入「判定 AI 行為前一定回看錄影」；階段 4.5 加入 AI 影片生成工具補充；階段 6 加入旁白產生器。
- `references/fixed-settings.md`：雲端環境配音可用 `產生旁白.bat`；額度補上每分鐘 3 次。固定設定本身不變。
- `profiles/ai-watch.md`：補充實測集指引。
- README：2.4.0 摘要、檔案結構、使用範例、最近更新、本版檢查。
### Fixed
- 2.3.0 的 CHANGELOG、README、SKILL.md 有幾處把換行寫成字面 `\n`，導致標題與表格列黏在同一行；已改回真正換行。
- 記錄 2026-10-09 誤判：把使用者按 Tab 接受的灰色建議字當成 AI 自行 commit／push；改為以錄影判定並寫入技能規則。

## [2.3.0] - 2026-10-10
### Added
- `references/youtube-growth-experiment.md`：流量來源辨識、三關固定資料實測、影片和 Shorts 交接及 24h／72h／7d／28d 數據複盤。
### Changed
- SKILL 與 README 增加以證據驅動的成長閉環，保留原有固定配音、品牌、素材驗證規則。

## [2.2.0] - 2026-10-08
### Added
- `references/animation-handoff.md`：生活化故事、可愛原創配角、動畫提示詞、角色與分鏡預覽、類比邊界及製作交接。
- `scripts/pack_video_bundle.py`：白名單素材 ZIP、待補項目、CRC 與 SHA-256；拒絕危險路徑、符號連結與缺少的必填檔案。
- 實測前預寫成功／部分成功／失敗旁白；依證據選擇配音分支，不虛構 UI 或成果。
- README／START_HERE 製作包範本，交給 Claude Code／Codex 製作時間軸、預覽與缺件清單。
### Changed
- SKILL.md 新增動畫預覽與素材包交接階段，保留固定品牌、配音、配樂與影片建置流程。
- README.md、VERSION、SKILL.md 與本更新紀錄統一標示 2.2.0；首頁補齊功能表及新增資源。
- 修正 README 中與 2.1.0 固定設定衝突的 AI Watch 品牌與對嘴角色舊說明。
### Tests
- 已驗證中文路徑、ZIP／SHA-256 完整性、缺件報告、必填缺件失敗、危險路徑與符號連結拒絕。
- 以 Docker 影片題目驗證動畫、品牌設定、未實測分支與代理交接流程；未執行完整影片渲染或平台發布。

## [2.1.0] - 2026-10-06
### Added
- `references/fixed-settings.md`：使用者定案、兩頻道通用的固定製作設定——Gemini Achird＋固定 Style（暫定配音只用 Zhiwei，禁止其他 TTS）、黑熊老師片頭、原創 lo-fi 配樂、右下角黑熊老師講課、片尾、Windows 一鍵檔與踩坑紀錄。
- `scripts/build/bear_presenter.py`：分層 SVG 黑熊老師角色依配音音量對嘴、眨眼、手勢，疊加到主片右下角（Playwright 逐格、透明背景）。
- `scripts/build/append_outro.py`：把核定片尾（含音樂）接到主片後。
- `scripts/build/產生影片.bat`：Windows 一鍵檔（自動找技能資料夾、安裝套件、檢查 ffmpeg、build → 黑熊講課 → 接片尾，全程寫 `產生紀錄.log`）。
- 資產：`assets/brand-approved/v1/blackbear-science/intro/`（黑熊老師片頭與定案片頭音訊）、`character/`（黑熊老師分層 SVG 角色）、`music/`（原創配樂產生程式與授權紀錄）、`assets/common/watermark_transparent_1920x1080.png`。
- `.gitattributes`：.bat 固定 CRLF。
### Changed
- `build.py`：`timeline.json` 新增 `intro_len`、`scene_starts`。
- SKILL.md 規則優先順序加入固定製作設定；AI Watch 改用黑熊老師片頭與講課角色（取消「不借用自然教室素材」限制）；配音章節改為固定 Achird 設定。
- `profiles/ai-watch.md`、`profiles/blackbear-science.md`、`references/build-pipeline.md` 同步。
### Fixed
- 記錄 2026-10-06 實作踩坑：LF 換行的 .bat 不會執行、`setx` 需新視窗、新電腦缺 numpy、AI Studio 下載暫存檔被清掉、D:／G: 雲端硬碟代號不同。

## [2.0.0] - 2026-10-02
### Changed
- 使用者要求技能識別改名為 multichannel-video-workflow；同步 SKILL.md name、新安裝資料夾、呼叫方式及 topic_radar.py User-Agent。
- 舊識別不再使用；這是需要遷移的識別變更，因此升主版本。README 提供保留未提交工作、避免覆蓋與重複安裝的遷移步驟。
- 影片流程、兩頻道設定及五支核定片尾保留。

## [1.14.3] - 2026-10-02
### Changed
- 使用者核定五支片尾；正式版移除 DRAFT，保留畫面、文案、音樂與六秒節奏，另存 assets/brand-approved/v1。
- 更新頻道設定、README、核定清單及來源；核定範圍不擴大至其他獨立品牌資產。

## [1.14.2] - 2026-10-02
### Changed
- 依使用者影片截圖參考，透過影像工具清理重建熊掌徽章並合成六秒自然教室片尾；記錄重建來源與非原始檔限制，仍待核定。

## [1.14.1] - 2026-10-02
### Changed
- AI Watch 增加趨勢、工具實測、Coding、開源四種主題片尾，保留一致的品牌骨架。
- 自然教室片尾改為必須使用與右下角相同的熊掌原素材；v1 葉片草案淘汰，尚待原素材，不以替代圖示冒充。
- 生成腳本新增 --blackbear-logo，未提供時跳過自然教室片尾。

## [1.14.0] - 2026-10-02
### Added
- AI Watch 原創 Logo、4 秒片頭、6 秒片尾、獨立合成音訊、透明浮水印與 16 秒音床草案。
- 自然教室 6 秒片尾與獨立音訊草案，不取代核定片頭。
- scripts/create_brand_drafts.py、素材 manifest、視覺概覽與影音驗證記錄；所有草案待使用者核定，不自動啟用。
### Docs
- profiles 與 README 加入草案路徑、來源、用途及核定狀態；正式品牌素材缺口仍保留。

## [1.13.1] - 2026-10-02
### Fixed
- 修正共用選題評分、SEO、提示詞與範本中殘留的軟體限定、Papaya 標題套路、未驗證省錢承諾、固定句長／語速與強制英文產出。
- Facebook 文案標籤按頻道；`fb_post.py` 新增 `--channel`，未指定使用中性頁尾，英文文案改為選用，保留連結另存與複製能力。
### Docs
- 補齊兩頻道素材核定與缺口、生成器必填欄位、路徑解析、thanks 圖卡姓名與片尾後製限制。
- 將 style-guide 改為共用風格與精簡歷史研究摘要，不再保留其他創作者原句／縮圖範本作為生成規則。
- 依使用者授權將 GitHub repo 改名為 `multichannel-video-workflow`，更新文件與安裝網址；保留 `papaya-style-video` 技能識別與安裝路徑，記錄其他 clone 及外部引用遷移步驟。
### Tests
- 新增 Facebook CLI 回歸測試：三種頁尾、英文選用、HTML 跳脫、網址更新及多次匯出不覆蓋原稿。

## [1.13.0] - 2026-10-02
### Added
- `profiles/blackbear-science.md`：自然教室專屬受眾、選題、科學查證、課堂隱私與品牌影音規則
- `profiles/ai-watch.md`：AI 觀測站專屬受眾、趨勢與開源查證、實測、非聳動標題與品牌影音規則
- `references/channel-routing.md`：單一頻道路由、規則優先順序與跨頻道品牌隔離
### Changed
- `SKILL.md` 和 README 改為多頻道工作流；SEO 標題、語速、英文素材和社群宣傳依頻道設定檔及使用者指示調整
- 未備妥的 AI Watch 片頭／片尾標示待建立，不會套用自然教室熊掌與音樂

## [1.12.1] - 2026-10-01
### Docs
- 階段 7.5 加入發文方式：臉書連結預覽卡只在發文前產生（先貼網址等縮圖、分享偵錯工具「再次抓取」、已發出的貼文要刪掉重發）；用 YouTube oEmbed 檢查影片公開與縮圖
- `fb_post.py` 複製頁頁尾加上發文小技巧

## [1.12.0] - 2026-10-01
### Added
- 階段 7.5「臉書宣傳文」：使用者要求每支影片完成時一起產生，放在 `3_製作後/臉書宣傳/`
- `scripts/fb_cover.py`：臉書分享圖 1200×630（背景畫面、小標、兩行主標、工具膠囊、底部文字、熊掌徽章）
- `scripts/fb_post.py`：中英文案 → 一鍵複製頁 `facebook-post.html`；`--url` 代入 YouTube 網址並另存含連結的 .txt（不覆寫原稿）
### Changed
- 專案資料夾結構加入 `3_製作後/臉書宣傳/`；技能說明加入「臉書文」「宣傳文」「電影感」「預告片風格」「教學動畫」觸發詞
### Docs
- README：版本 1.12.0、階段表加入 7.5、檔案結構、使用範例、最近更新表

## [1.11.1] - 2026-10-01
使用者回報「有雜音、稍微晃動、重疊」→ 量測後修正
### Fixed
- `clean_tts()`：Gemini TTS 每個檔案開頭 10 ms 喀聲、結尾約 120 ms 滿格雜訊 → 自動清除；每句頭尾 5 ms 淡入淡出；旁白輕度去齒音（deesser）
- 轉場時舊鏡頭不再凍結在最後一格（繼續運鏡，位移限制在畫面內）；舊字卡在轉場前 1/3 淡出，不會和新照片重疊
- `zoom` 轉場只在中點交疊 2 格；`leak` 0.8 → 0.55 秒
- 動畫：回彈幅度 1.70 → 0.9；拖曳中的卡片畫在最上層；步驟排序改成側移→上下→歸位（重疊面積 0）；儀表板與投票版面切換改成先淡出再淡入
### Added
- `bgm_fit: {jumps: [[在第幾秒, 跳回第幾秒]]}`：在頻譜自我相似度最高的位置跳接（取代依小節循環，避免鼓點疊在一起）
### Docs
- build-pipeline.md 第十節：雜音與晃動的檢查方法

## [1.11.0] - 2026-10-01
第一次實作：《讓數位工具走進科學探究》（2026-10-07 蓮潭國小研習引起動機影片，電影預告片風格）
### Added
- 圖卡版型 `photo`：全幅照片（課堂實景、分鏡圖），左／右半透明面板（工具名稱膠囊＋標題＋逐步出現重點）、下方字卡、左下名牌、暗角；照片與文字分兩層（照片運鏡、文字固定並淡入滑上）
- `anims_lib.py`：教學模擬動畫 `type: anim`（依旁白句子觸發事件）：`title_reveal` 預告片片名、`moon` 月亮觀測（台南北緯 23°、月齡 ×12.2° 計算 18:00 位置與盈月相位）、`poll` 即時作答分布＋溫度計、`wall` 證據牆、`compare` 各組數據比較、`sort` 水生植物生活型分類、`variables` 步驟排序＋變因配對、`dashboard` 班級儀表板＋差異化分流、`cycle` 探究循環
- 運鏡 `cam`：push、pull、pan_l/r、tilt_up/down、push_l/r、still（次像素、照片沒指定時自動輪流）
- 轉場 `trans`：dissolve、whip_l/r（動態模糊）、flash、zoom、dip、leak（漏光）、cut
- 電影黑邊 `letterbox: true`（照片與動畫段；切到圖卡時 0.6 秒收合；浮水印自動上移）
- `pause_before`：某幕開始前的純音樂時間（片名動畫、段落呼吸）
- `bgm_fit`：依片長剪接配樂（開頭照原曲、中段依小節循環、最後一段對齊片尾，等功率交叉淡化）
- 合成音效開關 `sfx`／`sfx_whoosh`／`sfx_hit`（預設建議關閉：使用者不喜歡轉場音效）
- `--voice timing`：還沒有配音時依字數估長度輸出畫面預覽（旁白只拿來壓低配樂、不混進成品）；`--post` 指定輸出資料夾
- 圖片路徑先找影片專案資料夾、再找工作區（專案可以放在工作區外）
### Changed
- 總輸出加限幅（-3.6 dBFS）、AAC 改 256k：預告片配樂的密集鼓點在 192k 會過衝到 -0.2 dBTP，256k 實測 -2.8 dBTP
- 品質檢查的推近平順度抽樣避開進場轉場；x264 crf 19 → 18
### Fixed
- 回彈緩動在進度 ≤ 0 時有浮點誤差，元素提早露出

## [1.10.3] - 2026-09-30
### Added
- `md2txt.py` 同時產生 `置頂留言.txt`（取上架文案「置頂留言」段落，直接全選複製）

## [1.10.2] - 2026-09-30
### Added
- `md2txt.py` 同時產生 `YouTube標記.txt`：取上架文案「標籤」段落，去重複、檢查 YouTube 500 字元上限（有空白的標記多算 2 個引號），超過時從後面刪並列出

## [1.10.1] - 2026-09-30
### Added
- `scripts/md2txt.py`：上架文案 Markdown → 純文字 .txt（UTF-8＋Windows 換行，去掉 Markdown 符號，方便複製到 YouTube）
- `build.py` 輸出影片後自動把 `3_製作後/01_上架文案.md` 另存成 .txt
### Changed
- SKILL.md 階段 5：上架文案一律同時提供 .txt（使用者要求）

## [1.10.0] - 2026-09-30
### Added
- 圖卡版型 `image`（截圖／素材圖）、`code`（程式碼／終端機視窗，逐行出現）、`line_chart`（折線圖比較）→ 共 40 種
- 影片片段 `ss`：指定起點（不循環），可直接剪自己成品的片段
### Fixed
- 程式碼視窗與對話框的中文改用微軟正黑體（英文等寬字型沒有中文字，會變方框）
- 流程方塊依最長的一行計算寬度（支援兩行標籤）
### Docs
- build-pipeline.md：YAML 換行寫法與 shell 改檔時反斜線被吃掉的陷阱

## [1.9.0] - 2026-09-29
### Added
- **一鍵產生影片** `scripts/build/build.py`：一個指令完成配音 → 切句 → 時間軸 → 圖卡 → 逐格畫面 → 混音 → 字幕 → 輸出 → 品質報告；中間檔沿用，輸出不覆寫
- `scripts/build/cards_lib.py`：37 種通用圖卡版型，由 `畫面規格.yaml` 驅動；`steps` 讓項目隨旁白逐步出現（0.25 秒淡入）
- 配音：Gemini API（格式依 AI Studio「Get code」；免費方案每分鐘 3 次、每天 10 次，`scenes_per_request: 2` 可減半請求）或 Windows Zhiwei 暫定配音；分場音檔自動切成逐句
- 畫面：次像素推近、圖卡之間 0.3 秒溶接、浮水印逐格疊加（片頭與影片素材段關閉）、分段平行處理
- 品質報告：長度、解析度、響度、峰值、黑畫面、推近平順度（變異係數，上集實測 zoompan 1.2–1.9、次像素 0.05–0.35）
- `references/build-pipeline.md`：使用說明、規格格式、版型參數一覽
### Changed
- SKILL.md 階段 7：腳本定稿後優先使用一鍵產生

## [1.8.1] - 2026-09-29
### Fixed
- `references/production-notes.md`：圖卡慢速推近改用 Pillow 次像素逐格產生，不再用 ffmpeg zoompan（zoompan 每格取整數像素，慢速推近時「停約 12 格、跳 2 像素」，成品畫面輕微晃動）；新增檢查方法，以及「中間檔遺失時用 SRT＋段落表反推時間、只重做畫面」的修復做法

## [1.8.0] - 2026-09-29
### Added
- `references/production-notes.md`：沒有螢幕錄影時的自動粗剪流程（Windows Zhiwei 逐句暫定配音、品牌圖卡、自動組合）、浮水印規則、8 個常見陷阱與解法、輸出後品質檢查
### Changed
- `references/intro-spec.md` 同步：新增透明背景版、縮到角落版、深藍圓形徽章浮水印（1080p 疊加用、512、YouTube 150／300）
- SKILL.md 階段 7：浮水印擇一使用、影片素材段落關閉疊加浮水印；沒有螢幕錄影時可以先做粗剪

## [1.7.0] - 2026-09-29
### Changed
- 片頭畫面定案：白色熊掌 Logo＋深海軍藍底 #091D38 的「可愛揮手」動畫（腳掌落下回彈、趾頭依序彈出、爪子伸出、揮手、星星閃爍、「黑熊老師」浮出），取代原本規劃的「黑板＋粉筆＋V 字」
- `references/intro-spec.md` 改寫為定案版（視覺元素、分鏡時間軸、聲音、製作方式、剪輯規則、決策紀錄）
- 片頭影片與 Logo 屬於使用者品牌資產，存放在使用者工作區，不放進本 repo

## [1.6.2] - 2026-09-29
### Changed
- 片頭聲音定案：M1 尤克里里（Pixabay，ShidenBeatsMusic）＋C1 粉筆聲，**片頭無人聲**；取消配音口號
- 招呼語由主講旁白在片頭結束後說，避免重複打招呼
- `references/intro-spec.md` 改寫為定案版（分鏡與聲音時間對齊、檔案位置、剪輯規則）
- 音檔本身不放進本 repo（Pixabay 授權禁止單獨轉發素材）

## [1.6.1] - 2026-09-29
### Changed
- 開場白統一為「哈囉，大家好，我是黑熊老師。」（使用者確認），移除「觀眾是教師時改用各位老師大家好」的變體
- 結語五句經使用者確認定案

## [1.6.0] - 2026-09-29
### Added
- `references/intro-spec.md`：黑熊老師品牌片頭規格（約 4 秒：黑板、粉筆畫出黑熊老師、胸前白色 V 字亮起、有辨識度的配音口號；口號與聲音各三個方案）
### Changed
- 片頭不再沿用 Papaya 的做法（4.5 秒 Logo、旁白在第 2.5 秒疊上）：改為固定品牌片頭，主講旁白在片頭結束後才開始

## [1.5.0] - 2026-09-29
### Changed
- 開場白改為黑熊老師的問候語：「哈囉，大家好，我是黑熊老師。」（教師觀眾：「哈囉，各位老師大家好，我是黑熊老師。」）
- 結語改為：「好，今天關於 X 的介紹，就到這裡。我是黑熊老師，感謝大家觀看這部影片。如果你希望黑熊老師接下來拍什麼影片，請在底下的留言區留言告訴我。我們下次見，掰掰！」
- 明文禁止使用 Papaya 電腦教室的開場與結尾原句（避免版權與辨識度問題）；「不自我介紹」改為「只在開場與結語各說一次我是黑熊老師」
- 英文逐字稿的固定句對照同步更新（英文名稱暫定 Black Bear Teacher）
- 風格分析報告保留 Papaya 原句作為研究紀錄，並加註「我們的版本」

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
