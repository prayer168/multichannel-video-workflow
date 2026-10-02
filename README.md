# multichannel-video-workflow

> 以案例式、生活化和可跟做的教學結構，規劃與製作「黑熊老師的自然教室」或「AI 觀測站（AI Watch）」影片。使用獨立的頻道設定檔管理受眾、選題、查證、語氣與品牌影音。
> A channel-aware YouTube production skill for Black Bear Teacher's Nature Classroom and AI Watch.

**Version:** 1.14.3（2026-10-02）

---

## 頻道模式

本技能保留原有選題、影片生成與發布流程，新增兩個互斥的頻道設定檔。每個專案先選一個頻道，避免品牌、受眾和語氣混用。

| 設定檔 | 主要內容 | 品牌規則 |
|---|---|---|
| `profiles/blackbear-science.md` | 自然科教學、AI 數位教材、教學紀錄、科展與 STEAM | 使用自然教室核定片頭片尾與黑熊老師品牌素材 |
| `profiles/ai-watch.md` | AI 趨勢、AI Coding、開源軟體、軟體／網站／App 開發 | 使用 AI Watch 專屬品牌影音；尚未提供的素材列為待建立，不借用自然教室素材 |

兩個頻道共用案例式教學、生活例子、術語白話解釋、操作查證、分鏡、製作與復盤。PAPAYA 電腦教室只作為公開教學結構的研究參考，不使用其 Logo、音樂、片頭、原句或縮圖素材。

## 這個技能能做什麼

從一個教學主題開始，一路帶你走完：

| 階段 | 產出 |
|------|------|
| 0. 頻道路由與選題雷達 | 先選頻道設定檔，再依自然教育或 AI／軟體內容調整來源與評分；候選附來源、日期、重複檢查與推薦理由 |
| 0.5 建立專案 | `1_製作前 / 2_製作中 / 3_製作後` 資料夾與專案卡 |
| 0.8 SEO 關鍵字研究 | YouTube 搜尋建議（需求）＋搜尋結果競爭分析（供給）→ 機會判斷、主要與次要關鍵字 |
| 1. 選題評估 | 依頻道設定檔評估受眾需求、可信度、成果、展示、差異化與可行性，並提出一句話承諾和敘事模式 |
| 2. 操作步驟 | 收集真實操作步驟與踩坑紀錄（不編造功能） |
| 3. 腳本 | 章節表加上逐句稿（語氣、句長、語速、開場與結尾依頻道設定檔） |
| 3.5 英文逐字稿 | 依頻道與使用者需求產出中英逐字稿或字幕 |
| 4. 分鏡 | 畫面類型、鏡頭推拉、網址標籤、TIP 角標、音效；依內容調整節奏 |
| 5. 上架文案（SEO 版） | 依搜尋意圖與頻道語氣提出標題、說明欄、章節、Hashtag、標籤、需要時的英文文案、置頂留言與縮圖文案 |
| 6. 配音 | TTS 友善稿、聲線設定（不使用對嘴角色） |
| 6.5 一鍵產生影片 | `scripts/build/build.py`：依腳本＋畫面規格一次輸出影片（Gemini TTS 配音並自動清除頭尾雜訊、41 種圖卡含全幅照片、9 種教學模擬動畫、運鏡、7 種電影轉場、電影黑邊、配樂依相似度剪接、中英字幕、章節、品質報告）；`--voice timing` 可在沒有配音時先看畫面預覽 |
| 7. 發布 | 依頻道品牌與授權條款檢查配樂、字幕、播放清單、結束畫面導流與發布設定 |
| 7.5 臉書宣傳文 | 影片完成時一併製作符合所選頻道品牌的宣傳文與分享圖；熊掌版 `fb_cover.py` 僅用於自然教室，AI Watch 使用核定素材或無品牌暫代版 |
| 8. 發布後 SEO 優化 | 點閱率、流量來源、搜尋字詞報表 → 調整標題、說明欄、縮圖 |

## 共用教學方法與頻道識別

- 各頻道使用自己的固定片頭與片尾；黑熊老師自然教室可使用既有熊掌片頭，AI Watch 使用專屬素材（尚未提供時標示待建立）
- 共同方法是白話、循序、帶觀眾完成一個具體成果；速度、句長、口頭禪依頻道和主題調整
- 依頻道設定檔使用自己的開場、結尾、CTA、縮圖色彩和品牌元素；不套用另一頻道的固定台詞或視覺模板

## 頻道設定檔與路由

- `references/channel-routing.md`：頻道判定、規則優先順序與共用品質要求
- `profiles/blackbear-science.md`：自然教室專屬規格
- `profiles/ai-watch.md`：AI 觀測站專屬規格
- 若兩個頻道片頭、片尾或聲音資產尚未備齊，技能仍可完成選題、腳本與分鏡，並將缺少的素材列入交付清單。

## 檔案結構

```
multichannel-video-workflow/
├── SKILL.md                 技能主檔（工作流程 + 核心規則）
├── README.md                本檔
├── CHANGELOG.md             版本紀錄
├── VERSION                  目前版本號
├── tests/test_fb_post.py     Facebook 頻道隔離、選用英文與保留原稿的 CLI 回歸測試
├── scripts/
│   ├── topic_radar.py       抓 GitHub、Hugging Face、Hacker News 熱度原始資料
│   ├── seo_keywords.py      YouTube 搜尋建議＋競爭分析（SEO 關鍵字研究）
│   ├── md2txt.py            上架文案 .txt＋YouTube標記.txt＋置頂留言.txt
│   ├── fb_cover.py          臉書分享圖 1200×630
│   ├── fb_post.py           臉書文一鍵複製頁（中英雙語；上傳後可代入 YouTube 網址）
│   └── build/               一鍵產生影片：build.py、cards_lib.py（41 種圖卡版型）、anims_lib.py（教學模擬動畫）、say_batch.ps1
├── profiles/              自然教室與 AI 觀測站頻道設定
│   ├── blackbear-science.md
│   └── ai-watch.md
└── references/
    ├── build-pipeline.md    一鍵產生影片：指令、畫面規格格式、版型一覽、配音與額度、電影預告片風格、雜音／晃動／重疊的檢查方法
    ├── intro-spec.md        黑熊老師品牌片頭規格（含透明版、縮到角落版、浮水印）
    ├── production-notes.md  自動粗剪、浮水印規則、常見陷阱與品質檢查
    ├── topic-radar.md       選題雷達：來源清單、步驟、報告格式
    ├── seo.md               YouTube SEO 規範
    ├── style-guide.md       完整風格規範（定位、標題、縮圖、片頭、結構、語氣詞庫、畫面、音樂）
    ├── templates.md         專案卡、選題、腳本、分鏡、剪輯、上架、發布、復盤範本
    └── prompts.md           縮圖與插畫生圖、TTS 聲線、英文逐字稿、選題雷達、SEO 提示詞
```

## Repo 名稱與技能識別相容性

GitHub repo 已於 2026-10-02 從 `papaya-style-video` 改名為 **`multichannel-video-workflow`**。文件與安裝指令使用新網址。

repo 名稱與技能 frontmatter `name: papaya-style-video` 是兩件事。為維持既有安裝與 `$papaya-style-video` 使用方式，本版保留技能識別、安裝資料夾與 `topic_radar.py` User-Agent。若日後只改 repo 名稱，仍 clone 到舊技能資料夾，不自動改技能名稱。

既有 clone 與外部引用遷移：
1. GitHub repo 改名已完成；既有草稿 PR #1 位於 `https://github.com/prayer168/multichannel-video-workflow/pull/1`。
2. 各 clone 執行 `git remote set-url origin https://github.com/prayer168/multichannel-video-workflow.git`。
3. 本 README 的標題、結構根目錄與安裝網址已更新；其他外部文件／書籤請改用新網址。搜尋 `papaya-style-video` 時區分 repo URL 和保留的技能識別，不做全域替換。
4. 本 README 全域 clone 指令的目的資料夾仍為 `~/.claude/skills/papaya-style-video`。本地既有 clone 不需搬動。檢查外部安裝器、書籤、CI 與發布文件。
5. 若另要改技能識別，視為獨立遷移：更新 SKILL.md frontmatter、安裝目的資料夾、呼叫方式與外部技能目錄；保留舊安裝／呼叫的轉接說明，避免同時安裝兩份自動發現的完整技能。另版公告後再遷移，不能假設 GitHub 改名會完成上述工作。

本 repo 沒有 agents metadata、套件 manifest 或 CI 設定；現有名稱引用集中於 README 安裝／結構、SKILL.md name 及 topic_radar.py User-Agent。

## 品牌素材與程式限制

2026-10-02 使用者已核定 AI Watch 四種主題片尾與自然教室熊掌片尾。正式檔案、核定範圍與來源見 [已核定片尾](assets/brand-approved/v1/README.md)，五支正式影片皆移除 DRAFT。獨立片頭、浮水印、通用片尾、背景音床與旁白聲線沒有因這次片尾核定而自動核定；自然教室既有片頭實檔與授權仍需確認。歷史草案保留在 assets/brand-drafts/。

`build.py` 實際要求 `intro`、`intro_audio`、`watermark`、`bgm` 檔案，不支援 `outro`／`outro_audio` 或自動讀取 profiles。片尾可作最後一幕的畫面，但完整影音／長度需後製接入。無品牌預覽也須建立真實中性或靜音／透明檔案；不能拿待建立文字當路徑。詳見 `references/build-pipeline.md`。

`fb_cover.py` 有熊掌自動尋找邏輯，沒有無品牌開關，只用於自然教室。AI Watch 另製核定或無品牌分享圖。`fb_post.py --channel ai-watch`／`--channel blackbear-science` 指定頁尾；不指定為中性頁尾，英文文案可省略。之後用 `--url` 更新時仍帶相同 channel。所有宣傳文案、標籤與 CTA 依本頻道。

## 安裝

**Claude Code（全域）**
```bash
git clone https://github.com/prayer168/multichannel-video-workflow.git ~/.claude/skills/papaya-style-video
```

**Claude Code（單一專案）**：clone 到專案的 `.claude/skills/papaya-style-video`

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

執行 `python -X utf8 -m unittest discover -s tests -v` 驗證 Facebook 頻道頁尾、無英文輸入、HTML 跳脫、連結更新與原稿／多次匯出保留；執行 `python -X utf8 -m compileall -q scripts tests` 檢查 Python 語法。文件以版本比對、資源路徑／連結、表格欄位、程式碼區塊、舊規則搜尋與 `git diff --check` 檢查。

1.13.1 更新未執行 Gemini API 配音、完整教學影片渲染或平台發布；1.14.0 已實際生成並驗證三支品牌短片草案，未執行旁白 API 或發布。外部品牌素材未找到實檔，素材狀態已據實標示。原有 build、TTS、字幕、SEO、上架文字轉換與熊掌分享圖程式均保留。
