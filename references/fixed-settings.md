# 固定製作設定（2026-10-06 使用者定案）

> 使用者指示：以下設定「固定都要寫到技能裡」，兩個頻道（黑熊老師的自然教室、AI 觀測站）的正式影片一律照做，不再每支重新挑選或另寫。
> 規則優先順序仍是：使用者本次指示 → 本檔固定設定 → 頻道設定檔 → 共用流程。本檔取代先前「AI Watch 不得使用熊掌／黑熊素材」的限制。

## 一、配音（固定，不得換成其他 TTS）

| 項目 | 固定值 |
|---|---|
| 正式配音 | Google AI Studio（Generate speech）／ Gemini API，模型 `gemini-3.8-flash-tts`，聲音 **Achird**（單一講者），`scenes_per_request: 2` |
| 語速 | 每分鐘約 240～260 字 |
| 暫定配音 | 只能用 Windows 臺灣國語 **Zhiwei**（`build.py --voice zhiwei`）；**禁止**改用 Kokoro、espeak、Edge TTS 等其他聲音當暫定或正式配音（2026-10-06 使用者退件：大陸腔、不是黑熊老師的聲音） |
| 雲端環境 | 雲端容器連不到 Gemini 也沒有 Zhiwei → 不要在雲端自行產生配音；改請使用者在 Windows 執行 `scripts/build/build_video.bat`（整支影片）或 `scripts/build/make_narration.bat`（只產生旁白，讀 `旁白資料.json`，2026-10-10 起），或用 AI Studio 網頁產生後存進 `2_製作中/配音/Gemini/Sxx-Syy.wav` |

Style 一字不改，只替換最後一行的「本片術語清單」：

```
自然的臺灣國語男聲，一位四十歲左右的自然科老師，在教師研習中耐心講解：溫暖、厚實、穩重，帶著親切的微笑感。
是「講」不是「唸」：句子流暢連貫，語速中等（每分鐘約 240 到 260 字），重要概念前稍微停頓，「……」處停頓約 0.8 秒，
每一行結尾停頓約半秒，「好，」開頭的句子前停頓稍長。重點詞自然加重，尾音自然收住不拖長。不要播報腔、廣告腔、朗誦腔。
英文術語用自然的英文發音，不要逐字母拼讀：<本片術語清單>。
```

- AI Studio 網頁版：Speaker 1 選 Achird → Style 貼上全文 → 每次貼兩幕旁白（一行一句）→ Run → 下載 WAV，依幕號改名（`S01-S02.wav`）。下載是 24 kHz 單聲道，build.py 會自動清頭尾雜訊、切句。
### AI Studio 產生與下載 WAV 一律由 AI 操作（2026-10-21 使用者固定要求）

使用者已開好 Google AI Studio（或已連上 Claude in Chrome）時，**產生配音、按下載、取回 WAV、改名歸檔全部由 AI 操作**，不再請使用者自己點下載或改名。使用者這項授權涵蓋本流程所有 WAV 下載，不必每段再問一次。

1. 在使用者 Chrome 開新分頁到 `aistudio.google.com/generate-speech` →「Create new dialog」→ Speaker 1 搜尋並選 **Achird** → Style 貼上本節固定 Style（只換最後一行術語清單）。
2. 每次貼兩幕旁白（一行一句）→ Run → 等播放器出現總長度。
3. 先暫停播放器，再按播放器上的「Download」（找不到座標時用 find 取得按鈕 ref 再點）。
4. **每段下載後立即在使用者電腦確認檔案真的存在**（`device_bash` 列出下載資料夾最新的 `Generated Audio …wav`，比對大小／長度：24 kHz 16-bit 單聲道約 48,000 bytes／秒）。沒出現就重按一次，不要假設已下載。
5. 依產生順序改名為 `S01-S02.wav`、`S03-S04.wav`…，複製到單支影片 `製作中/配音/Gemini/`（工具工作區為 `2_製作中/配音/Gemini/`），再傳回雲端給 build.py。原始下載檔不刪除。

踩坑紀錄（2026-10-21《Nano Banana 2.1 做教材插圖》）：
- 播放器停在中途（暫停或剛下載完）時，「Run」會變成 `aria-disabled=true`，按了沒反應；把進度條拖到最後、讓它播完，Run 才會恢復。
- 連續操作時，Speaker 面板或 Style 選單偶爾沒打開，文字會被打進旁白框；每個開選單動作後先截圖確認再輸入。
- Chrome 會沿用「上次存檔位置」：前兩段 WAV 存進了專案資料夾，不在「下載」。找不到檔案時兩處都查，誤放的檔案移到 `配音/Gemini/_未使用的舊版/`。
- 網頁版重新整理或重開 Playground 後，Achird 與 Style 會重設，要重新選。

- Gemini 語音是生成的：音色固定，但每次語氣、停頓略有差異；同一支影片同一天用同一組設定一次產生完。
- **生成後一定要用語音辨識核對內容（2026-10-22《地球離太陽最近，為什麼是冬天？》）**：API 一次產生 S05-S06 得到 173.8 秒，比文字應有長度多 70 秒；用離線語音辨識（sherpa-onnx＋SenseVoice）逐段轉寫，發現開頭 74 秒是模型自己編的、與腳本無關的研習口白，74 秒之後才完全照稿。判斷方法：實際長度比「字數 ÷ 每分鐘 250 字」多出 30% 以上，或停頓數遠多於句數，就先轉寫核對；只裁掉離稿段，不整段重生成（重生成可能換語氣）。
- **使用者不在電腦前時**：AI Studio 網頁版的「Download」會跳出 Chrome「另存新檔」視窗，AI 無法代按，下載會卡住。改用 `make_narration.bat`（Gemini API，使用者電腦已有 GEMINI_API_KEY）：把旁白資料.json 放進專案的 `製作中/配音/旁白產生器/`，從檔案總管雙擊（電腦操作只能點按），三組約 1 分鐘完成；輸出長度寫進 log，AI 從雲端讀檔核對。
- 免費額度每天 10 次、每分鐘 3 次（API）；403／429 代表額度用完，隔天重跑會從缺的幕接續。`make_narration.py` 已內建 21 秒間隔與接續。

## 二、片頭（固定）

| 項目 | 檔案（repo） |
|---|---|
| 片頭影片 4 秒 | `assets/brand-approved/v1/blackbear-science/intro/blackbear_intro_4s.mp4` |
| 片頭音訊 4 秒 | `assets/brand-approved/v1/blackbear-science/intro/intro_audio_final_M1_chalk_4s.wav` |

- 兩個頻道都用黑熊老師片頭（2026-10-06 使用者：AI Watch「片頭還是用黑熊的 logo 來做」，並選用原有黑熊老師片頭）。
- build.py 的 `intro`／`intro_audio` 以工作區根目錄解析：先把兩個檔案複製到工作區 `04_品牌資產/黑熊老師_共用/`，YAML 填相對路徑；或直接填 repo 內的絕對路徑。

## 三、背景音樂（固定）

- 一律用**原創合成配樂**，不用 Pixabay 曲當 BGM（2026-10-02 事件：EP1 用 M1、M2 被第三方 Content ID 聲明）。
- 章節鋪底：`原創_章節鋪底_lofi.wav`（84 BPM lo-fi，約 12 分鐘，不循環）。由 `assets/brand-approved/v1/blackbear-science/music/make_music.py` 產生：`python make_music.py 720`。
- YAML：`bgm: 04_品牌資產/黑熊老師_共用/原創_章節鋪底_lofi.wav`、`bgm_lufs: -33`、`sfx: false`。
- 授權紀錄：`assets/brand-approved/v1/blackbear-science/music/license-record.md`。片頭音訊內含 M1（Pixabay，查證時未登記 Content ID），只在片頭 4 秒使用。

## 四、黑熊老師講課角色（固定）

- 每支影片疊加核定黑熊老師講課角色；一般影片沿用**右下角**，進階動畫講解可改用2026-10-15確認的**左側放大講者／右側動畫**配置（見 [ui-narration-animation.md](ui-narration-animation.md)），依配音音量對嘴、眨眼、呼吸；舊管線每幕開頭2.5秒做手勢；進階動畫依實際旁白事件與目標安排指向、解說及回應，不用固定開場手勢取代語意同步。片頭、片尾不出現。
- 角色來源：`assets/brand-approved/v1/blackbear-science/character/`（分層 SVG＋`character.js` 手動時鐘 API；造型依使用者的《黑熊老師角色表情與姿勢圖鑑》）。不得自行重畫或換造型。
- 程式：`scripts/build/bear_presenter.py <專案> --character <character 資料夾>`；預設高度 330 px、15 fps、右下距邊 20 px。需要 `pip install playwright` 與 `python -m playwright install chromium`。
- 圖卡右下角原本保留給浮水印；有黑熊老師時不再疊浮水印（AI Watch 用透明 PNG）。

## 五、片尾（依頻道）

- AI Watch：已核定四種主題片尾（trends／tools／coding／opensource），依主題選一支。
- 自然教室：`assets/brand-approved/v1/blackbear-science/outro.mp4`。
- `scripts/build/append_outro.py <專案> <outro.mp4>` 後製接入（build.py 沒有 outro 欄位）。

## 六、一鍵產生（Windows）

把 `scripts/build/build_video.bat` 複製到影片專案資料夾，雙擊即可：

1. 自動找技能資料夾（`%USERPROFILE%\multichannel-video-workflow` → `%USERPROFILE%\.claude\skills\multichannel-video-workflow`，或先 `set REPO=…`）
2. 自動安裝 numpy、soundfile、pyyaml、pillow、playwright；檢查 ffmpeg
3. build.py（有 `GEMINI_API_KEY` 用 Gemini，沒有用 Zhiwei）→ bear_presenter.py → append_outro.py
4. 全程寫入專案資料夾的 `產生紀錄.log`（雲端的 Claude 可以直接讀進度）；出錯時視窗印出紀錄並暫停

踩坑紀錄（2026-10-06）：
- .bat 必須是 **CRLF** 換行（`.gitattributes` 已設定）；LF 換行的 .bat 在 cmd 會整段失效、看起來像沒有執行。
- `setx GEMINI_API_KEY` 只對之後新開的視窗有效；設定後請關掉舊視窗，從檔案總管雙擊 .bat。
- 金鑰不要截圖或貼進對話；不小心外流就到 AI Studio 刪除重建。
- 新電腦第一次執行會缺 numpy 等套件（ModuleNotFoundError）→ .bat 已自動 pip install。
- 學校桌機與家裡筆電的 Google 雲端硬碟代號不同（D: ／ G:），專案資料夾內容相同；YAML 一律用相對路徑。

## 七、畫面規格.yaml 範本（video 區）

```yaml
video:
  name: 影片檔名
  voice: Achird
  model: gemini-3.8-flash-tts
  scenes_per_request: 2
  style: >-
    （貼上第一節 Style，最後一行換成本片術語）
  intro: 04_品牌資產/黑熊老師_共用/黑熊老師片頭_4s.mp4
  intro_len: 4.0
  intro_audio: 04_品牌資產/黑熊老師_共用/片頭音訊_定案_M1＋粉筆_4秒.wav
  watermark: 04_品牌資產/AIWatch_無品牌暫代/watermark_transparent_1920x1080.png   # 有黑熊老師講課時用透明 PNG
  bgm: 04_品牌資產/黑熊老師_共用/原創_章節鋪底_lofi.wav
  bgm_lufs: -33
  sfx: false
```


## 八、進階動畫與片頭變體（2.5.0）

依 [advanced-animation.md](advanced-animation.md) 選材質與模組。預設仍為核定4秒黑熊片頭；新增繪本、紙藝、木作、科技桌版本為設計提案，未選定前不替換。核定Logo、角色造型、Achird固定Style與原創音樂不因材質切換而改變。長片插段不內嵌片頭片尾，主持由主片疊一次。新配置與轉接器待實作，不等於既有build.py已支援。

## 九、字幕軌與字幕安全區（2.10.0 定案；2.13.0 改為不燒錄）

細節見 [subtitle-style.md](subtitle-style.md)。**2.13.0（2026-10-21）使用者改定：所有影片一律不燒錄字幕，只輸出獨立字幕軌（SRT）。**下表的樣式數值只在使用者特別要求燒錄版時使用。

| 項目 | 固定值 |
|---|---|
| 行數 | 一次只出現一行；橫式每行 ≤ 17 字，Shorts ≤ 12 字 |
| 樣式 | 白字＋黑框（外框 4.5 px、淡陰影 1.5 px），不加底色；微軟正黑體粗體 58 級（Shorts 72 級） |
| 位置 | 水平置中，離下緣 96 px（Shorts 在畫面高度約 65%） |
| 時間 | 換行點對齊旁白停頓（`scripts/build/subs_oneline.py`），每行至少 0.7 秒 |
| 安全區 | 製作畫面時 y 880–1000 不放重要內容；`build.py` 預設 `subtitle_safe: true` 自動把圖卡與動畫縮到 y 880 以上 |
| 交付 | 成片（不含字幕）＋`字幕_zh-TW_單行.srt`；上傳 YouTube 時另外上傳 SRT |

`build_video.bat` 最後一步只產生單行 SRT／ASS，不再燒錄；需要燒錄版時手動加 `subs_oneline.py --burn`。
