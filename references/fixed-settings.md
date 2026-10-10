# 固定製作設定（2026-10-06 使用者定案）

> 使用者指示：以下設定「固定都要寫到技能裡」，兩個頻道（黑熊老師的自然教室、AI 觀測站）的正式影片一律照做，不再每支重新挑選或另寫。
> 規則優先順序仍是：使用者本次指示 → 本檔固定設定 → 頻道設定檔 → 共用流程。本檔取代先前「AI Watch 不得使用熊掌／黑熊素材」的限制。

## 一、配音（固定，不得換成其他 TTS）

| 項目 | 固定值 |
|---|---|
| 正式配音 | Google AI Studio（Generate speech）／ Gemini API，模型 `gemini-3.8-flash-tts`，聲音 **Achird**（單一講者），`scenes_per_request: 2` |
| 語速 | 每分鐘約 240～260 字 |
| 暫定配音 | 只能用 Windows 臺灣國語 **Zhiwei**（`build.py --voice zhiwei`）；**禁止**改用 Kokoro、espeak、Edge TTS 等其他聲音當暫定或正式配音（2026-10-06 使用者退件：大陸腔、不是黑熊老師的聲音） |
| 雲端環境 | 雲端容器連不到 Gemini 也沒有 Zhiwei → 不要在雲端自行產生配音；改請使用者在 Windows 執行 `scripts/build/產生影片.bat`（整支影片）或 `scripts/build/產生旁白.bat`（只產生旁白，讀 `旁白資料.json`，2026-10-10 起），或用 AI Studio 網頁產生後存進 `2_製作中/配音/Gemini/Sxx-Syy.wav` |

Style 一字不改，只替換最後一行的「本片術語清單」：

```
自然的臺灣國語男聲，一位四十歲左右的自然科老師，在教師研習中耐心講解：溫暖、厚實、穩重，帶著親切的微笑感。
是「講」不是「唸」：句子流暢連貫，語速中等（每分鐘約 240 到 260 字），重要概念前稍微停頓，「……」處停頓約 0.8 秒，
每一行結尾停頓約半秒，「好，」開頭的句子前停頓稍長。重點詞自然加重，尾音自然收住不拖長。不要播報腔、廣告腔、朗誦腔。
英文術語用自然的英文發音，不要逐字母拼讀：<本片術語清單>。
```

- AI Studio 網頁版：Speaker 1 選 Achird → Style 貼上全文 → 每次貼兩幕旁白（一行一句）→ Run → 下載 WAV，依幕號改名（`S01-S02.wav`）。下載是 24 kHz 單聲道，build.py 會自動清頭尾雜訊、切句。
- Gemini 語音是生成的：音色固定，但每次語氣、停頓略有差異；同一支影片同一天用同一組設定一次產生完。
- 免費額度每天 10 次、每分鐘 3 次（API）；403／429 代表額度用完，隔天重跑會從缺的幕接續。`產生旁白.py` 已內建 21 秒間隔與接續。

## 二、片頭（固定）

| 項目 | 檔案（repo） |
|---|---|
| 片頭影片 4 秒 | `assets/brand-approved/v1/blackbear-science/intro/黑熊老師片頭_4s.mp4` |
| 片頭音訊 4 秒 | `assets/brand-approved/v1/blackbear-science/intro/片頭音訊_定案_M1＋粉筆_4秒.wav` |

- 兩個頻道都用黑熊老師片頭（2026-10-06 使用者：AI Watch「片頭還是用黑熊的 logo 來做」，並選用原有黑熊老師片頭）。
- build.py 的 `intro`／`intro_audio` 以工作區根目錄解析：先把兩個檔案複製到工作區 `04_品牌資產/黑熊老師_共用/`，YAML 填相對路徑；或直接填 repo 內的絕對路徑。

## 三、背景音樂（固定）

- 一律用**原創合成配樂**，不用 Pixabay 曲當 BGM（2026-10-02 事件：EP1 用 M1、M2 被第三方 Content ID 聲明）。
- 章節鋪底：`原創_章節鋪底_lofi.wav`（84 BPM lo-fi，約 12 分鐘，不循環）。由 `assets/brand-approved/v1/blackbear-science/music/make_music.py` 產生：`python make_music.py 720`。
- YAML：`bgm: 04_品牌資產/黑熊老師_共用/原創_章節鋪底_lofi.wav`、`bgm_lufs: -33`、`sfx: false`。
- 授權紀錄：`assets/brand-approved/v1/blackbear-science/music/授權紀錄.md`。片頭音訊內含 M1（Pixabay，查證時未登記 Content ID），只在片頭 4 秒使用。

## 四、黑熊老師講課角色（固定）

- 每支影片在**畫面右下角**放黑熊老師講課，依配音音量對嘴、眨眼、呼吸；每幕開頭 2.5 秒做手勢（第一幕揮手、其餘指向、片尾前 3 秒揮手），其他時間 idle。片頭、片尾不出現。
- 角色來源：`assets/brand-approved/v1/blackbear-science/character/`（分層 SVG＋`character.js` 手動時鐘 API；造型依使用者的《黑熊老師角色表情與姿勢圖鑑》）。不得自行重畫或換造型。
- 程式：`scripts/build/bear_presenter.py <專案> --character <character 資料夾>`；預設高度 330 px、15 fps、右下距邊 20 px。需要 `pip install playwright` 與 `python -m playwright install chromium`。
- 圖卡右下角原本保留給浮水印；有黑熊老師時不再疊浮水印（AI Watch 用透明 PNG）。

## 五、片尾（依頻道）

- AI Watch：已核定四種主題片尾（trends／tools／coding／opensource），依主題選一支。
- 自然教室：`assets/brand-approved/v1/blackbear-science/outro.mp4`。
- `scripts/build/append_outro.py <專案> <outro.mp4>` 後製接入（build.py 沒有 outro 欄位）。

## 六、一鍵產生（Windows）

把 `scripts/build/產生影片.bat` 複製到影片專案資料夾，雙擊即可：

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
