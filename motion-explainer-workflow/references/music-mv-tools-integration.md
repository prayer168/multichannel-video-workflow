# 音樂 MV 與藝術動畫工具整合（2.29.0／子技能 0.9.0，2026-11-10）

整合影片〈14 个开源项目、将近 160 种画风：AI 写代码做音乐 MV 教程〉（亞里，https://www.youtube.com/watch?v=jrkfL0V9-oM）推薦的三個 repo。2026-11-10 在 GitHub 逐一核對 README、程式與授權，並在使用者 Windows 本機安裝與試跑。

**整合方式**：和 Motion Showreel 相同——上游 clone 到使用者電腦的工具資料夾、釘選已審閱版本，本技能**叫用它們的腳本或只讀選中的風格檔**；不把上游的 SKILL.md 複製進本技能，也**不裝成 Claude Code skill／plugin**（會在使用者說「做 MV」「做片」時被觸發，搶走本技能的流程與固定設定）。

## 1. 三個 repo 的角色

| Repo（釘選） | 本技能怎麼用 | 不用的部分 |
|---|---|---|
| [Yari-tuber/mv-director](https://github.com/Yari-tuber/mv-director) `79af43a`（66★） | **叫用腳本**做音樂 MV：`new_project.py`（分軌、測拍、逐字對齊）→ `cue_lint.py`（卡點表檢查）→ `render.py`（逐句／逐小節靜幀、草稿、成片）→ `check.py`（從成片量歌詞與拍點）。流程對照見 `../../references/music-video-workflow.md` | 它的 SKILL.md 只當方法參考；交付、品牌、署名依本技能 |
| [alchaincyf/huashu-art-motion](https://github.com/alchaincyf/huashu-art-motion) `8a0d7d7`（6.6k★） | ① **解說語法**：`scripts/engine/render.py --spec <clip.json>` 產生長度精確到格的片段（`--alpha` 出 ProRes 4444 透明底），語法有 3Blue1Brown、keynote UI、財經圖表、Kurzgesagt、Vox、白板、Storytime、動態文字；② **成片門禁** `scripts/film_gate.py`：只讀 mp4，任何來源的成片都能量 | 花叔角色形象、角色幀、Clawd 片段與總覽圖**不在 MIT 範圍**，一律不用；風格配方卡只讀選中的 |
| [lemomo-ai/lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) `143f387`（14.1k★） | **只當風格參考**：`styles/<風格>/STYLE.md`（66 種），每支片只讀選中的 1–2 份，把規則抄成本技能的風格卡 | 不跑它的 plugin 安裝（會建 `~/lemo-opuscar`）；不用它的 TTS；樣片是 **CC BY 4.0**，要用畫面必須署名 LemoLab |

和頻道的對應（候選，首次採用前先做一鏡測試）：

- 自然教室：huashu 的 `y3_whiteboard`（白板，對應黑熊講課版型）、`t1_3b1b`（一個物體形變成下一個，講概念）、`y1_kurzgesagt`（尺度穿行，講宇宙／微觀）；lemo 的 `chalkboard`、`whiteboard`、`microscope`、`crayon-book`、`isometric-picture-book`。
- AI 觀測站：huashu 的 `t2_keynote_ui`、`y2_vox`、`t3_finance_chart`、`y5_kinetic_type`；lemo 的 `living-screencast`、`desktop-flythrough`、`dataviz`、`swiss-motion`。
- 音樂 MV：只在使用者明確要做 MV 或歌詞動畫時用 mv-director（見第 5 節的音樂授權）。

## 2. 安裝與路徑

- Windows：執行 `scripts/install_mv_tools.ps1`。clone 到 `%USERPROFILE%\AI-Video-Tools\motion-explainer\ecosystem\{mv-director,huashu-art-motion,lemo-opuscar}`，建立共用 venv `ecosystem\mv-venv`（Python 3.12，numpy／scipy／matplotlib／pillow／playwright／opencv），並安裝 Playwright Chromium。
  - `-WithStems`：加 demucs 分軌（含 torch）。
  - `-WithAligner`：加 torch＋transformers 5.x 做逐字對齊。有 NVIDIA 顯示卡裝 CUDA 版（cu128），沒有裝 CPU 版。
  - **不會自動下載對齊模型**（`Qwen/Qwen3-ForcedAligner-0.6B-hf`，約 1.8 GB，Apache-2.0）；腳本結尾印出下載指令，下載後設 `MV_ALIGNER_MODEL` 指到本機資料夾。
- 環境檢查：`python scripts/preflight.py` 會顯示三個 repo 是否在釘選版、venv 基本套件、對齊與分軌是否可用（都是選用項，不影響「全部通過」）。
- 以下以 `E` 代表 `...\ecosystem`，`PY` 代表 `E\mv-venv\Scripts\python.exe`。
- 審閱結果（2026-11-10）：mv-director 的網路存取只有 Hugging Face 模型下載；兩個 repo 的渲染器都只在 `127.0.0.1` 開本機伺服器給無頭瀏覽器讀頁面；沒有其他上傳或遠端執行。

### 踩坑

- **Python 版本**：這台電腦只有 Python 3.15，torch 不一定有對應 wheel，所以 venv 固定用 uv 下載的 3.12。
- **uv 0.13.7 的次版本連結錯誤**：`uv python install 3.12` 報 `Missing expected target directory for Python minor version link`，但直譯器其實已裝好。安裝腳本因此不看這一步的結束碼，改用 `uv python find 3.12` 取得路徑再建 venv。
- **PowerShell 5.1**：`$ErrorActionPreference='Stop'` 加 `2>&1` 時，uv／git 寫到 stderr 的進度訊息會被當成錯誤中止。安裝腳本用 `Native {}` 包住原生指令，只看結束碼。
- **`-I` 會忽略 `PYTHONUTF8`**：上游說「Windows 報編碼錯就設 PYTHONUTF8=1」，但它的指令都帶 `-I`，環境變數無效。繁中 Windows（cp950）印 `✓` 會 `UnicodeEncodeError`。一律寫成 `PY -I -X utf8 scripts\xxx.py`；huashu 的腳本也加 `-X utf8`。

## 3. 衝突時以誰為準

規則優先順序不變：使用者本次指示 → `../../references/fixed-settings.md` → 頻道設定檔 → 本子技能 → 上游預設。

| 項目 | 上游預設 | 本頻道做法 |
|---|---|---|
| 配音 | lemo 用 TTS；huashu 有語音複刻 | 只用 fixed-settings 的核定聲線（Achird＋固定 Style） |
| 配樂 | lemo／huashu 程式合成；mv-director 用使用者給的歌 | 一般影片用頻道原創配樂；MV 只用原創或已授權的歌（第 5 節） |
| 字幕 | mv-director 把歌詞畫進畫面；huashu 片段可帶字 | 旁白片不燒錄字幕、只交 SRT；MV 的歌詞是畫面本身，另交 SRT（第 6 節） |
| 片頭片尾、角色 | 無或自帶 | 黑熊片頭、核定片尾、黑熊講課角色由主技能接上，不在上游畫面裡重做 |
| 簡體文字與字型 | 兩個 repo 都只附簡體字型子集 | 一律繁體，先處理字型（第 4 節） |
| 畫面規格 | mv-director 1080p60；huashu 片段依 spec（範例多為 30fps） | 依本技能：1920×1080、60fps；huashu spec 的 `fps` 改成 60 |
| 停點 | mv-director 在選畫風時停一次 | 照本技能三停點；mv-director 的「選畫風」併進停點 ② 風格幀 |

## 4. 繁體中文字型（必做）

- **huashu**：內建的霞鶩文楷與思源黑體都是 **GB2312 子集**，繁體字會缺字。2026-11-10 實測：把白板範例改成繁體後，渲染器回報「LXGWWenKai-500 缺字：鐘這時間換鈴響」，缺的字改用系統字型補，同一行出現兩種字體（畫面明顯不一致）。渲染時只顯示警告、結束碼仍為 0，**不會自動失敗**，要看輸出訊息。
  修法：下載完整的霞鶩文楷（`https://github.com/lxgw/LxgwWenKai/releases`，OFL）或思源黑體 TC，用上游工具把本片所有文字補進子集：
  `PY -X utf8 E\huashu-art-motion\scripts\font_subset.py --font <LXGWWenKai-Medium.ttf> --text "<本片所有字>"`
  這會改寫 checkout 裡的 woff（git 會顯示已修改）；換釘選版前先記下來重做。**此修法尚未實測。**
- **mv-director**：預設歌詞字型是 `NotoSansSC-900`（`runtime/mv.js` 的 `DEFSTYLE`）。不改上游，在專案的 `scene.js` 用 `fonts` 欄位載入本技能的 `fonts/NotoSansTC`，並在歌詞樣式的 `font` 指定它。
- 逐字對齊：`--lang` 預設 `Chinese`。對齊模型對繁體歌詞的準確度**尚未實測**；先用一段已知時間的歌詞比對，不準再試「轉成簡體對齊、對回繁體」。

## 5. 音樂授權

- 只用**原創**或**已取得公開影片使用授權**的歌。網路上可下載、標示免費，不代表可以公開發布。
- 參考影片的示範歌、各 repo 的樣片配樂，都不能拿來用。
- 本次整合依使用者指示（2026-11-10）**不創作歌曲**；mv-director 的完整流程要等使用者提供有授權的歌才試跑。
- 成片 `NOTES.md` 與上架說明欄都要寫清楚：歌曲版權、借用的畫風（例：lemo-opuscar `ink-wash`，LemoLab，CC BY 4.0／MIT）、字型與參考程式。

## 6. 和主流程的銜接

1. **時間只從量測資料來**：mv-director 的 `song.json`（拍點、小節、逐字時間）就是 MV 的時間表；旁白片仍用旁白 timing.json。
2. **頁面規則相同**：mv-director 頁面是 `window.render(t)`＋`window.READY`，和 Motion Showreel `render.mjs` 一致；huashu 片段頁面用 `window.renderFrame(t)`。都屬「給時間就畫出那一刻」，可以和本技能的 `setT(t)` 互換外殼。
3. **品牌接合**：成片後依 `showreel_to_bear.py` 的做法疊黑熊講課角色（MV 一般不疊）、用 ffmpeg 接黑熊片頭與片尾。
4. **SRT**：MV 從 `song.json` 每句第一個字的開唱時間到該句最後一個字結束，轉成單行 SRT（依 `../../references/subtitle-style.md`）。轉換腳本待第一支 MV 實作時補。
5. **huashu 片段放進旁白片**：spec 的 `duration` 對齊該句旁白長度；超過 8 秒 render.py 會警告「讀成一頁 PPT」，照它的建議拆鏡。透明底片段用 `--alpha` 出 .mov 再合成。

## 7. 驗收

成片都要過三關，任一關不過不交付：

1. **技術硬指標**：Motion Showreel `inspect.mjs qa`（見 `motion-showreel-integration.md` 第 7 節）。
2. **反 PPT 門禁**：`PY -X utf8 E\huashu-art-motion\scripts\film_gate.py <成片.mp4>`。**紅燈**（結束碼 2）不交付：
   - 鏡頭內快速運動幀占比 < 3.5%（黃燈 < 6%）
   - 中段近乎空白的畫面連續 ≥ 0.3 秒
   - 藍紫底畫面占比 ≥ 30%（黃燈 ≥ 12%；題材本身需要時用 `--allow-blue-purple "理由"`）

   黃燈可以交付，但要在交付說明逐條寫為什麼可以。片長短於 20 秒時，快動門禁只提示不擋；拼進成片後在成片上再跑一次。門檻是上游作者用 13 支自己的片標定的，只當參考線，不代表本頻道觀眾的偏好。
3. **MV 專用**：`PY -I -X utf8 E\mv-director\scripts\check.py <專案>`（草稿加 `--draft`）。門檻見 `../../references/music-video-workflow.md`「用 mv-director 執行」。

## 8. 試跑紀錄（2026-11-10，使用者 Windows 本機）

環境：Windows 11、NVIDIA 顯示卡、Python 3.15（系統）＋uv 0.13.7 建的 3.12.16 venv、ffmpeg 9.0.2、Node 24。

| 項目 | 結果 | 耗時 |
|---|---|---|
| `install_mv_tools.ps1`（不含 torch） | 通過。三個 repo 已在釘選版；venv 套件與 Playwright Chromium（約 330 MB）裝好 | 約 74 秒（不含 clone） |
| `preflight.py` | 三個 repo ✅、venv 基本套件 ✅；逐字對齊、分軌顯示 ⚠️ 未安裝（選用） | — |
| mv-director `doctor.py` | 通過：numpy、scipy、matplotlib、PIL、playwright、ffmpeg、ffprobe 都有；demucs、逐字對齊為建議項，未裝 | 數秒 |
| huashu `render.py --spec examples/y3_whiteboard.json` | 通過：10 秒、1920×1080、30fps、H.264。上游提醒片段超過 8 秒 | 16 秒 |
| `film_gate.py`（同一支） | **黃燈**：鏡頭內快動 0%、80% 的幀在慢漂、72% 是不變的空底；因短於 20 秒只提示。結論和上游提醒一致：單一白板片段要拆鏡、加推近 | 5 秒 |
| 繁體文字測試（同一個 spec 改繁體，出 9.5 秒靜幀） | 字型缺字，退回系統字型（第 4 節） | 數秒 |

**未試跑**：mv-director 的完整 MV 流程（需要有授權的歌，本次依指示不創作）、torch／demucs／對齊模型安裝、繁體逐字對齊、huashu 字型補字、60fps 片段、lemo 風格轉成本技能風格卡。

## 9. 來源與授權

- mv-director：MIT，© 2026 亞里（Yari-tuber）。對齊模型 Qwen3-ForcedAligner-0.6B（Apache-2.0，用時下載）；分軌 demucs（Meta，MIT）；附帶字型均為 SIL OFL 1.1（見其 `fonts/字体授权.md`）；`参考代码/剪纸木偶/` 為 cyborggirl963 的 MIT 程式。
- huashu-art-motion：程式與文件 MIT（© 花叔）；筆順資料沿用 Arphic Public License；字型 OFL；花叔角色形象、角色幀與 Clawd 示範片不在 MIT 範圍。
- lemo-opuscar：程式 MIT；樣片 CC BY 4.0；作者註明風格是為 Claude Opus 5.5 調整的，其他模型效果不保證。
- 影片中的星數、畫風數、成效說法只代表影片與 repo 當時的狀況；換版前重新核對 README 與 LICENSE，再更新本文件和安裝腳本的釘選版。
