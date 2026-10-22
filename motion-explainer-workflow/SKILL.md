---
name: motion-explainer-workflow
description: 旁白定稿後，把「黑熊老師的自然教室」或「AI 觀測站」影片做成動態圖文（紙張畫布加虛擬攝影機、卡片與標註動效、資訊圖表、逐格揭示）的技能：定調風格卡與鎖定清單、委派任務卡、真實素材比例、靜幀條審片與第三方看片，並以 Remotion 或 HyperFrames 渲染。使用者要求動態圖文、程式動畫解說片、Remotion／HyperFrames 畫面、風格卡、靜幀條或實證比例檢查時使用。選題、腳本、配音、品牌與上架仍由 multichannel-video-workflow 負責；實拍素材剪輯由 video-editing-workflow 負責。
---

# 動態圖文剪輯工作流（motion-explainer-workflow）

版本 0.2.0（2026-10-22）。0.1.0 完成骨架、分工、安裝與環境檢查；0.2.0 以《地球離太陽最近，為什麼是冬天？》完成第一支實作（第 4 步），寫入工具選用實測與實作紀錄（見「第一支實作的經驗」）。第 2、3、5 步的方法文件與工具仍待建，尚未完成的項目不要假裝已存在。

## 分工

| 技能 | 負責 |
|---|---|
| `multichannel-video-workflow`（主技能，上一層資料夾） | 選題、腳本、配音（Achird）、品牌（黑熊片頭、黑熊老師講課角色、片尾、原創配樂）、標題縮圖、上架與復盤 |
| **本技能** | 旁白定稿後「畫面怎麼做」：定調、分鏡演法、委派、渲染、審片 |
| `video-editing-workflow` | 實拍素材盤點、粗剪、時間軸、混音與成片驗收 |

本技能不重新決定主技能的核定設定。共用設定直接讀主技能的檔案，不另存副本：

- `../references/fixed-settings.md`：配音、片頭、配樂、講課角色、片尾、字幕軌（規則優先順序：使用者本次指示 → fixed-settings → 頻道設定檔 → 本技能）
- `../profiles/blackbear-science.md`、`../profiles/ai-watch.md`：頻道受眾、語氣、查證與品牌
- `../references/subtitle-style.md`：字幕軌斷句與字幕安全區

## 什麼時候用

主技能階段 3 腳本定稿、且影片形式是動態圖文（畫面主要由程式產生的版面、卡片、圖表與攝影機運動構成）時轉來本技能。以下情況不用：整支是實拍或錄屏（用 `video-editing-workflow`）、只需要 `build.py` 現有圖卡就能完成（留在主技能）。

## 固定原則

- **不燒錄字幕**：字幕只輸出獨立字幕軌（SRT，沿用主技能 `subs_oneline.py`）。畫面中的文字是動態圖文的一部分（標題、標籤、圖表數字），不是逐句字幕；不要把旁白逐句打在畫面上。
- **幀率依風格決定**，在定調步驟寫進鎖定清單，之後全片不改：

  | 風格類型 | 幀率 |
  |---|---|
  | 紙張畫布加攝影機、大量圖文移動、資訊圖表 | 60 fps |
  | 手作材質（黏土、毛氈、皮影、定格、沙畫） | 30 fps 時間軸，角色動作 12–15 張／秒 |
  | 實拍為主、少量圖文 | 跟隨實拍素材（通常 30 fps） |

- **實證優先**：真實的東西（實拍、真實照片、真實介面錄屏、官方文件或資料圖表、真實檔案）才算實證；AI 生成插圖與示意動畫不算。各頻道下限見 `references/evidence-ratio.md`（第 2 步建立；建立前先用主技能交接單的初始值：自然教室一般 35%、故事屋／白板 15%、AI 觀測站 45%）。
- **示意不冒充證據**：示意動畫要標明示意；真實介面一律錄屏，不重畫成假 UI。
- **來源原則**：參考影片與文章的方法只當公開參考，以自己的話改寫並註明出處；不複製他人提示詞、Skill 原文或付費課程內容，也不仿製其品牌外觀。

## 流程總覽

1. **接收**：從主技能取得定稿腳本、旁白句 ID、正式配音（或暫定 Zhiwei）、頻道、品牌資產路徑。正式配音到齊前只做靜幀，時間軸以實際音檔為準，不以字數猜秒數。**接收配音時先跑主技能的去除摩擦聲檢核**（`../scripts/build/narration_noise_check.py`，修到「摩擦／爆音」0 處）；拼接多段配音時只取到每段最後一句結束後約 0.2 秒，不要保留到檔尾。
2. **定調**：依旁白提 4–6 個候選風格，每個用同一句旁白出樣幀，使用者對著樣幀挑；選定後寫風格卡（背景、色板、字體、進出場約定、不要清單）與鎖定清單（畫幅、解析度、幀率、字幕軌、品牌固定項）。主技能 `references/advanced-animation.md` 的材質模板可當候選來源。
3. **首段做到成片**：先把第一段（約 30–60 秒）做到可交付品質，確認風格卡可行再鋪開其餘段落。
4. **分鏡與委派**：每個分鏡（約 3 分鐘以內）寫任務卡：目的、風格卡、觀眾、可用素材與工具、樣片、紅線；只給框架，不規定每一格怎麼演。
5. **先靜幀後動態**：每個分鏡先輸出固定幀號的靜幀條審過，換掉最沒記憶點的三個時刻，再渲染；每個分鏡原則上只渲染一次。
6. **看片**：成片交給沒參與製作的另一個模型或人，像觀眾一樣看並回饋；不用程式替影片打分。
7. **成片前聲音檢核**：對最終旁白總軌再跑一次去除摩擦聲檢核，並抽聽每段配音的接縫（段落結尾＋下一段開頭）。
8. **交回主技能**：成片（不含字幕）＋單行 SRT＋分鏡表＋實證比例紀錄，由主技能接片頭片尾、講課角色、上架。

## 渲染工具

兩個都已安裝在使用者的 Windows 電腦（`%USERPROFILE%\AI-Video-Tools\motion-explainer\`）。**2026-10-22 實測結論見 `references/tool-choice.md`**：畫面程式先寫成「給時間 t 就畫出畫面」的純函式，兩個工具包同一個函式畫面幾乎相同；預設用 HyperFrames（記得 `--fps 60`），需要 React 元件重用時用 Remotion。原暫定比較：

| 工具 | 寫法 | 暫定適用 |
|---|---|---|
| Remotion 4 | React 元件，逐幀計算（`useCurrentFrame`） | 資料驅動、需要精確數值或大量重複元件的分鏡；授權：個人（含商業）、3 人以下團隊、非營利免費，若日後以學校名義製作先再確認一次 |
| HyperFrames | HTML／CSS＋可尋幀動畫（GSAP、CSS、Lottie），無建置步驟，Apache 2.0 | 版面設計導向、要快速迭代樣幀的分鏡 |

兩者都要把中文字體放進專案資料夾一起打包（Noto Sans TC，OFL），否則渲染機器沒有字體時中文會變方框。

## 安裝與環境檢查

- Windows 一次安裝：把 `scripts/setup_windows.bat` 雙擊執行（或在 repo 內直接執行）。它會檢查 Node（需 22 以上）與 FFmpeg、在 `AI-Video-Tools\motion-explainer\remotion` 執行 `npm install`、為 HyperFrames 安裝無頭 Chrome（`npx hyperframes browser ensure`）、選擇性安裝 HyperFrames 的 Claude Code 外掛，最後跑 preflight 並寫入 `安裝紀錄.log`。
- 檢查：`python scripts/preflight.py [--root <motion-explainer 資料夾>] [--json]`。檢查 Node、FFmpeg、中文字體、Remotion 專案與 HyperFrames；缺必要項目時回傳非 0。
- **一鍵複製安裝提示詞**：換電腦或要重裝時，把下面整段貼進該台 Windows 的 Claude Code（或 Codex）執行；它與 `setup_windows.bat` 同流程，跑完留下 `安裝紀錄.log` 與 `preflight.json` 供核對。工作資料夾不在預設位置時，先改第一段的路徑。

  ```text
  請在這台 Windows 電腦幫我安裝「動態圖文」影片工具環境，並在每一步確認結果。工作資料夾是 %USERPROFILE%\AI-Video-Tools\motion-explainer（裡面已有 remotion\、hyperframes\、fonts\、preflight.py、setup_windows.bat）。

  規則：
  - 用 PowerShell 執行；不要刪除任何既有檔案或資料夾，也不要改動 remotion\src 與 hyperframes\index.html 的內容。
  - 已經裝好的項目就跳過，不要重裝或升級。
  - 每一步的指令輸出都附加寫進 motion-explainer\安裝紀錄.log。
  - 任何一步失敗就停下來，告訴我錯誤訊息和建議的修法，不要自行換其他工具替代。

  步驟：
  1. 檢查 node -v（需要 22 以上）、npm -v、ffmpeg -version。Node 低於 22 才用 winget install OpenJS.NodeJS.LTS；沒有 FFmpeg 才用 winget install Gyan.FFmpeg（裝完要開新視窗讓 PATH 生效）。
  2. 進入 motion-explainer\remotion，執行 npm install，再執行 npx remotion browser ensure。
  3. 進入 motion-explainer\hyperframes，執行 npx --yes hyperframes@0.8.183 browser ensure。
  4. 若有 claude 指令，執行 claude plugin marketplace add heygen-com/hyperframes 和 claude plugin install hyperframes@hyperframes；沒有就略過並記錄。接著執行 git -C "$env:USERPROFILE\.claude\plugins\marketplaces\hyperframes" lfs pull 補抓 LFS 檔案（失敗不中斷，記錄即可）。
  5. 回到 motion-explainer，執行 python preflight.py --root . ，再執行 python preflight.py --root . --json > preflight.json。
  6. 用一張表回報：每個檢查項目 ✅／❌、版本號、還缺什麼。最後確認 fonts\ 裡有 NotoSansTC 字體檔與 OFL.txt。
  ```

  不用 AI 時，也可以在 PowerShell 貼上：`& "$env:USERPROFILE\AI-Video-Tools\motion-explainer\setup_windows.bat"`。
  新電腦的 motion-explainer 資料夾還沒建立時，先從 repo 複製 `scripts/preflight.py`、`scripts/setup_windows.bat`，並準備 `remotion/`（Remotion 4 起步專案）、`hyperframes/`（`npx hyperframes@0.8.183 init`）與 `fonts/`（Noto Sans TC＋OFL.txt）。
- **HyperFrames 外掛的 Git LFS 檔案**：`claude plugin marketplace add heygen-com/hyperframes` 只會取得 Git LFS 佔位檔（2026-10-22 實跑時有 84 個），Claude Code 不會自動下載內容。外掛本身照常可用；HyperFrames 範例素材、圖片或字型打不開時，執行：

  ```powershell
  git -C C:/Users/user/.claude/plugins/marketplaces/hyperframes lfs pull
  ```

  （換電腦時把 `user` 換成該電腦的使用者名稱，或用 `"$env:USERPROFILE\.claude\plugins\marketplaces\hyperframes"`。）`install_windows.ps1` 與 `setup_windows.bat` 已在安裝外掛後自動補抓；外掛市集更新（`claude plugin marketplace update`）後若又出現佔位檔，再跑一次。
- 2026-10-22 已在使用者 Windows 實跑（`install_windows.ps1`）：Node 24.15.0、FFmpeg 8.1.2、Remotion 4.0.537、HyperFrames 0.8.183＋無頭 Chrome 152、HyperFrames Claude Code 外掛，preflight 全部通過。
- 雲端容器或使用者電腦的 Linux 工作區不等於 Windows 本機：在那裡跑通的結果只代表程式可行，Windows 的安裝狀態以 Windows 上執行 preflight 的紀錄為準。

## 第一支實作的經驗（2026-10-22）
- **畫面**：整片寫成一個 `comp.html`（大畫布＋站點卡片＋攝影機關鍵影格，`setT(t)` 可尋幀），依 `timing.json` 的逐句時間排出每張卡片出現時間；雲端 Playwright 4 個並行逐幀擷取 60 fps。改哪一段就只刪那段幀重渲。
- **卡片疊放**：後出現的元素要在上層（`z-index` 依出現時間），否則後加的卡片背景會蓋掉先排好的字。
- **先出靜幀表再渲染**：每輪改版先輸出 12 張關鍵時刻靜幀拼成縮圖表檢查；第一輪就抓到文字沒定位、太陽太大擋字、長條圖文字被切等問題。
- **第三方看片有用**：另一個模型看縮圖表＋逐字稿，指出開場空白卡、畫面比旁白慢、地軸圖缺陽光方向等，修正後再輸出。
- **實證比例**：實拍改模擬後實證掉到約 26%；靠讓鏡頭在真實素材（NASA/SDO、CC 授權照片、中央氣象署官方表格）停留更久補到約 42%，但最長無實證空窗仍約 55 秒（示意＋兩段模擬連在一起）。實驗類題目要盡量真的拍，模擬只當補充。
- **公開素材取得**：雲端容器連不到 Wikimedia／NASA／氣象署；用使用者 Chrome 讀 Commons API 找檔與授權。Chrome 連續下載會被擋、而且會跳另存新檔視窗（使用者不在時沒人能按），改用「在分頁把圖片放大分塊顯示＋截圖拼接」取得約 1570 px 的版本，足夠做照片卡；官方 PDF 表格直接在 Chrome 檢視器截圖。
- **交付**：成品寫回使用者電腦時，平台會在 MP4 加入 C2PA 內容憑證（uuid 區塊，約 6 KB），檔案仍可正常播放；不要繞過或移除這個標記。單檔超過 30 MB 時分割傳送，到電腦上再接回並核對雜湊。

## 檔案（建置進度）

| 檔案 | 狀態 |
|---|---|
| `SKILL.md`、`scripts/preflight.py`、`scripts/setup_windows.bat`、`scripts/install_windows.ps1`（PowerShell 版；雙擊 `scripts/啟動安裝_PowerShell.bat` 即可執行） | 第 1 步完成 |
| `references/style-card.md`、`task-card.md`、`evidence-ratio.md` | 第 2 步待建 |
| `scripts/still_strip.py`、`contact_sheet.py`、`references/still-strip-review.md`、`sample-library.md`、`motion-vocabulary.md` | 第 3 步待建 |
| `references/tool-choice.md`（Remotion 與 HyperFrames 同鏡比較） | 第 4 步完成（2026-10-22） |
| `template/remotion/`、`template/hyperframes/`、`scripts/evidence_check.py` | 第 5 步待建 |

## 參考來源

- 翔宇工作流〈AI 視頻剪輯實戰：用 Claude Opus 5.5 剪口播長視頻〉（2026-10-21）https://www.youtube.com/watch?v=cRsNCh_HvsA ；配套免費文章 https://xiangyugongzuoliu.com/42-ai-video-editing-skill/ 。本技能的委派任務卡、風格卡／鎖定清單、靜幀條審片與實證比例概念參考此來源，全部以自己的話改寫，數值依本頻道另訂。
- Remotion 授權 FAQ：https://www.remotion.dev/docs/license/faq
- HyperFrames（HeyGen，Apache 2.0）：https://github.com/heygen-com/hyperframes
