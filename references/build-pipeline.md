# 一鍵產生影片（build.py）

> 2.1.0 起：Windows 用 `scripts/build/build_video.bat`（build.py → bear_presenter.py → append_outro.py）。片頭、配音、配樂、黑熊老師講課等固定設定見 `fixed-settings.md`。

> 程式：`scripts/build/`（`build.py` 主流程、`cards_lib.py` 圖卡範本庫、`say_batch.ps1` Windows 暫定配音）
> 第一支實作：《老師也能懂的 GitHub》（20 幕、80 個畫面、289 句）

## 一、使用者只需要做的事
| 時機 | 使用者 | AI |
|------|--------|----|
| 開始 | 給主題 | 一次產出腳本（`旁白稿_分場.md`）＋畫面規格（`畫面規格.yaml`） |
| 中間 | — | 跑 `build.py`，輸出影片、字幕、章節、品質報告 |
| 結尾 | 看成品與報告，確認後上架 | 依意見改規格或腳本，重跑（只重做有改的部分） |
| 只需一次 | 開通 Gemini API 帳單、建立金鑰，**自己**存成環境變數 `GEMINI_API_KEY` | 不經手金鑰 |

## 二、指令
```bash
# 需要：ffmpeg、Python 3（numpy、soundfile、pillow、pyyaml）、Windows（Zhiwei 暫定配音）、微軟正黑體
python scripts/build/build.py <影片專案資料夾>                  # 自動選配音
python scripts/build/build.py <影片專案資料夾> --voice zhiwei   # 強制暫定配音
python scripts/build/build.py <影片專案資料夾> --only 60        # 只輸出前 60 秒預覽（約 2 分鐘）
```
- 專案資料夾放在 `<工作區>/05_影片專案/<專案>/`；品牌素材路徑以工作區根目錄為準
- 已完成的中間檔會沿用：配音、切句、圖卡（依內容雜湊命名，改了哪張就只重畫哪張）
- 輸出不覆寫：同名時自動加 `_2`、`_3`

## 三、配音
| `--voice` | 行為 |
|-----------|------|
| `auto`（預設） | `配音/Gemini/` 有全部分場音檔 → 用 Gemini；缺的幕若有 `GEMINI_API_KEY` 就用 API 補齊；否則改用 Zhiwei 並寫進報告 |
| `gemini` | 一定要 Gemini，不完整就停止 |
| `zhiwei` | Windows 臺灣國語 Zhiwei 逐句暫定配音（免費、幾秒完成） |

- Gemini API：請求格式依 AI Studio「Get code」（`## Style:` 風格段落＋`## Transcript:` 旁白；`speechConfig.voiceConfig.prebuiltVoiceConfig.voiceName`），回傳 24 kHz 16-bit PCM
- **免費方案額度（2026-09-29 查 AI Studio Rate Limit 頁）：Gemini 3.8 Flash TTS 每分鐘 3 次、每天 10 次**（依專案計算，換電腦也一樣）；程式每次間隔 21 秒，遇到額度用完會停下，隔天重跑會從缺的幕接續
- `scenes_per_request: 2`：一次產生相鄰兩幕（存成 `S03-S04.wav`），請求次數減半；切句時自動把多幕音檔一起切。單次能產生多長的語音尚未實測，若切句時停頓不足會停下並提示
- **免費方案也能用 API**：AI Studio 的「API Keys」頁面可以建立免費金鑰（不用開帳單），額度和網頁版相同
- AI Studio 顯示的 403「Link a paid API key」其實是額度用完（Rate Limit 頁寫著 You have reached a rate limit）
- 分場音檔 → 逐句：依停頓位置＋每句字數，用動態規劃找切點；長度異常的句子會寫進報告

## 品牌設定的實際支援（2026-10-02 原始碼檢查）

`build.py` 不讀取 profiles，也沒有 channel_id 路由；品牌隔離由企劃與人工檢查完成。

| 項目 | 真實行為 |
|---|---|
| `video.intro` | 必填影片檔案；`intro_len` 預設 4 秒，須與核定片頭長度一致 |
| `video.intro_audio` | 必填音訊檔，混音直接讀取；不使用片頭影片內建音訊 |
| `video.watermark` | 必填 PNG；沒有省略／false 代表全片停用的介面。無品牌預覽用實際透明 1920×1080 PNG |
| `video.bgm` | 必填音訊；依需求用核定配樂或實際靜音檔，不能填空字串 |
| `outro`／`outro_audio` | 不支援；填入不會自動處理 |
| 片尾接入 | 最後一幕可設 `type: video`、`src`、`ss`、`watermark: false`；片尾長度受旁白時間軸限制，來源影片音訊不保留。完整核定片尾影音優先後製接入，再核對總長、字幕、章節與音量 |
| `type: thanks` | `cards_lib.py` 預設 name 是黑熊老師；AI Watch 明確指定 `name: AI 觀測站（AI Watch）` |

`intro`、`watermark`、`intro_audio`、`bgm` 的相對路徑以 `<專案>/../..` 為根；絕對路徑可直接使用。圖卡圖片先找專案再找工作區；不要把圖片解析方式誤套到品牌音訊。例示素材是自然教室外部資產，不隨 repo 附上，AI Watch 不可直接複製下列 YAML。專案卡記錄完整解析路徑、核定狀態、檔案存在與授權檢查。

尚缺 AI Watch 識別時只交付企劃、腳本與分鏡；無品牌粗剪需先建立實際中性片頭、靜音 WAV、透明 PNG 和所需授權配樂檔案。`--voice timing` 只替代旁白，仍需要上述品牌欄位與檔案，不代表免素材模式。正式發布前補齊所選頻道核定片頭片尾。

## 四、畫面規格（`2_製作中/畫面規格.yaml`）
```yaml
video:
  name: 影片檔名
  voice: Achird
  model: gemini-3.8-flash-tts
  style: 聲音風格說明（貼到 Gemini 的 Style）
  intro: 04_品牌資產/片頭動畫/延伸版本/黑熊老師片頭_4s_縮到角落.mp4
  intro_audio: 04_品牌資產/配樂音效/片頭音訊_定案_M1＋粉筆_4秒.wav
  watermark: 04_品牌資產/片頭動畫/延伸版本/浮水印/浮水印_疊加用_1920x1080.png
  bgm: 04_品牌資產/配樂音效/<背景音樂>
  bgm_lufs: -33
scenes:
  S01:
    - {at: 1, type: title, kicker: 老師也能懂的, title: GitHub, sub: 副標}
    - {at: 10, type: icons_plus, title: 五件事, items: [A, B, C, D, E], steps: [10, 11, 12, 13, 14]}
    - {at: 16, type: video, src: 相對路徑.mp4, ss: 30, watermark: false}   # ss＝從第幾秒開始播（不循環）
```
- `at`：這個畫面從第幾句開始（每幕第一個畫面從換幕處開始，其餘提早 0.15 秒）
- `steps`：**逐步出現**；第 i 個項目在第幾句出現（同一個畫面只寫一次，程式自動產生各個狀態，並以 0.25 秒淡入）
- 顏色：`blue`、`orange`、`green`、`cyan`、`gold`、`gray`、`navy`、`purple`、`red`，或 `[R, G, B]`
- YAML 技巧：重複的畫面用錨點（`&名稱`／`<<: *名稱`）只改不同的欄位
- 規則：圖卡裡不放熊掌徽章；右下角留白給浮水印；不用 emoji（微軟正黑體沒有）

## 五、版型一覽（`cards_lib.py`）
| 版型 | 用途 | 主要參數（支援 `steps` 的標 ★） |
|------|------|------|
| `title` | 片名卡（深色） | kicker、title、sub |
| `statement` | 大字句子（深色） | lines、hl（強調的行號）、sub、dark |
| `word` | 單一術語大字 | kicker、word、sub、strike（劃掉 sub）、note |
| `chapter` | 章節卡 | level、total、title、sub |
| `check` | 完成卡（綠勾） | title、sub |
| `bubbles` ★ | 人物＋問號＋術語泡泡 | items、colors |
| `split_code` | 左程式碼／右資料夾對照 | left_title、code、right_title、folders |
| `icons_plus` ★ | 編號圓圈＋「＋」 | title、items |
| `levels` ★ | 三層階梯預告 | title、items [{level, name, sub}] |
| `versus` | 左右兩個圖示對照 | left/right {icon, label, caption, nodes}、sep |
| `numbered` ★ | 編號清單 | title、sub、items |
| `versions` ★ | 版本卡片＋時間軸 | title、items、captions |
| `hub` | 雲端連接多台裝置 | title、labels |
| `cards` ★ | 並排卡片（2–4 張） | title 或 kicker、items [{head, body, color}]、sep、arrows、tag、term、dark |
| `tree` ★ | 資料夾樹狀圖 | title、rows [[文字, 說明]]、frame_label |
| `transfer` | 兩端傳送（Push/Pull/Clone） | left/right {icon, label}、dir、label、nodes、note、term、empty |
| `todo_screen` ★ | 教材編輯畫面＋待辦打勾 | title、screen_title、button、list_title、items |
| `timeline` ★ | 直式版本時間軸 | title、items、cursor、cursor_label、term |
| `input_box` | 輸入框示範 | title、label、text、button、note |
| `day_night` | 白天／晚上對照 | left/right {title, icon, label, steps, colors}、center |
| `files` | 檔案卡（可放進籃子） | title、files [{name, ok, note, note_out}]、basket |
| `flow` ★ | 一列流程（★ 依序亮起） | title、sub、boxes、colors、fs、h、y、chips、term |
| `four_places` ★ | Git 四個位置 | title、sub、pull（回流說明）、zones、actions |
| `git_graph` | 分支圖（stage 0–3） | title、stage、branch、captions、term |
| `form` ★ | 申請單 | title、head、items、term |
| `pr_page` ★ | PR Files changed 模擬 | title、diff [[符號, 內容]]、checks、lock_on、term |
| `conflict` | 合併衝突（stage 0–3） | title、stage、a、b、note、term |
| `ai_chat` | 對話框＋程式碼 | title、prompt、code、note |
| `warnings` ★ | 風險清單（可加盾牌） | title、items、shield、note |
| `flow_rows` ★ | 多列流程（★ 逐列亮起） | title、rows [{label, steps, colors, mark, then}]、legend、note、x1、gap |
| `columns` ★ | 左右分欄職責 | title、cols [{head, color, items}]、stamp |
| `duo` | 兩個角色結論 | kicker、items [{icon, text, sub, color}] |
| `sync_cycle` | 兩台電腦同步循環 | title、left_steps、right_steps、left_colors、right_colors |
| `stairs` | 學習地圖三級階梯 | title、sub、levels、show、term、badge、flag |
| `ring` ★ | 中心圖示＋環狀標籤 | title、center、items |
| `thanks` | 結尾感謝 | name、text |
| `cta_comment` | 留言邀請 | title、text、note |
| `image` | 截圖或素材圖（自動縮放置中） | title、sub、image（工作區相對路徑）、caption、crop |
| `code` ★ | 程式碼／終端機視窗（★ 逐行出現） | title、window、lines、hl（標亮行號）、note |
| `line_chart` | 折線圖（上下分開比較） | title、series [{label, color, values}]、ymax、xlabel、stacked |

- 影片片段：`ss` 指定起點；自己的成品片段通常已有浮水印，要設 `watermark: false`
- YAML 字串要換行時寫成 `"第一行\n第二行"`（雙引號＋`\n`）；直接斷行會被合併成空格
- 用 shell 的 heredoc 改檔時，`\\n` 可能被吃成真的換行 → 改用編輯工具，或在 Python 裡用 `chr(92)` 產生反斜線

新增版型：在 `cards_lib.py` 寫一個 `t_名稱(im, d, p)`，加進 `TYPES`，再補進這張表。

## 六、畫面與聲音的處理
- 圖卡推近：1.0 → 1.035，Pillow 次像素逐格產生（**不用 zoompan**）
- 畫面切換：圖卡之間 0.3 秒溶接；影片素材段直接切換
- 浮水印：直接疊在每一格；片頭與設定 `watermark: false` 的影片段不疊
- 平行處理：依段落分成數組同時產生（預設 CPU 核心數的一半，最多 8），最後無損串接
- 聲音：旁白 -14 LUFS（先量測、補增益、限幅，量兩次）；背景音樂 -33 LUFS、旁白出現時自動壓低、開頭淡入、結尾淡出；片頭音訊 4 秒

## 七、輸出
| 檔案 | 位置 |
|------|------|
| 影片 | `3_製作後/輸出成品/<name>_<配音>.mp4` |
| 品質檢查報告 | 同名 `_品質檢查報告.md`：長度、解析度、響度、峰值、黑畫面、推近平順度（變異係數 < 0.6） |
| 章節 | `3_製作後/輸出成品/章節_<配音>.txt`（可直接貼到說明欄） |
| 字幕 | `2_製作中/字幕/字幕_zh-TW_<配音>.srt`；有 `英文字幕稿.tsv` 時另出 `字幕_en_<配音>.srt` |
| 中間檔 | `2_製作中/剪輯專案/build/`（圖卡、逐句修剪、配音軌、分段影片、timeline.json） |

## 八、推近平順度的判斷依據
上集實測（同一段圖卡、5 秒）：zoompan 版變異係數 1.23–1.91（停 12 格、跳 2 像素）；次像素版 0.05–0.35。報告以 < 0.6 為通過。


## 九、電影預告片風格（v1.11.0）
第一次實作：《讓數位工具走進科學探究》（畫面規格範例在該專案 `2_製作中/畫面規格.yaml`）

```yaml
video:
  letterbox: true              # 照片與動畫段加上下黑邊
  pause_before: {S01: 3.8, S07: 1.6}   # 幕前純音樂時間
  bgm_fit: {loop_from: 16, loop_to: 112, tail_from: 112, bar: 1.7266, xfade: 1.2}
  sfx: false                   # 不加轉場音效（使用者偏好）
scenes:
  S03:
    - {at: 1, type: photo, image: 分鏡圖/05.png, cam: push, trans: zoom, side: left, color: purple, kicker: Kahoot｜探究前, title: "在探究前\n看見學生的想法", items: [課前診斷, 迷思概念], steps: [2, 2]}
    - {at: 4, type: anim, anim: moon, trans: dissolve, steps: [5]}
```

| 參數 | 值 |
|------|----|
| `type: photo` | image、focus、side＋kicker/title/items/color、lines＋hl、plate、vignette |
| `type: anim` | anim（title_reveal、moon、poll、wall、compare、sort、variables、dashboard、cycle）＋各自參數；steps＝動畫事件的句號 |
| `cam` | push、pull、pan_l、pan_r、tilt_up、tilt_down、push_l、push_r、still |
| `trans` | dissolve、whip_l、whip_r、flash、zoom、dip、leak、cut |

- **配樂剪接 `bgm_fit`**：先量每 2 秒響度找出曲子的段落（前奏、漸強、斷點、再起飛）；`tail_from` 設在斷點前，讓高潮落在最後幾幕
- **選配樂**：Pixabay 預告片類幾乎都有登記 Content ID（2026-09-30 掃 990 首只有 17 首沒有）→ 逐頁檢查「Content ID Registered」
- **預覽**：`build.py <專案> --voice timing --post <暫存資料夾>`（約 5 分鐘輸出整支無旁白預覽）
- **動畫規則**：內容放在 y 130–950（上下黑邊）、右下角留給浮水印；2.10.0 起 `subtitle_safe` 預設開，動畫畫面整體縮到 y 880 以上，y 880–1000 留給嵌入字幕（見 subtitle-style.md）；回彈動畫進度 ≤ 0 時要回傳 0
- **峰值**：預告片配樂較大聲，總輸出限幅＋AAC 256k，否則密集鼓點會過衝


## 十、雜音、晃動、重疊的檢查方法（v1.11.1）
| 問題 | 量測方法 | 判斷 |
|------|---------|------|
| 配音雜音 | 每 10 ms 峰值；削波樣本數；相鄰樣本跳動 > 0.5 | 頭尾滿格＝TTS 雜訊（clean_tts 會清）；跳點若 ±10 ms 都有高頻＝嘶音（正常），能量集中 ±1 ms＝喀聲 |
| 配樂接點 | 4 秒視窗頻譜相似度（STFT 24 頻帶）找最像的兩點 | 相似度 > 0.7 再接；不要跨在漸強高點或斷點 |
| 峰值 | ebur128 真峰值 | 預告片配樂要限幅＋AAC 256k |
| 晃動 | 相位相關法量每格位移，和 9 格平滑比較 | 運鏡 < 0.05 px 不平順；轉場時舊鏡頭不能凍結 |
| 重疊 | 每個轉場逐格條＋全片每 4 秒一格；動畫用參數算卡片框的重疊面積 | 字卡殘影、拖曳卡片被蓋、兩個版面同時出現 |

- 語音核對：faster-whisper（small、CPU int8）逐句辨識，平均相似度 ≥ 0.95；低分句先看是不是同音字（變因／變音、評量／平良）


## 十一、黑熊老師講課與片尾後製（v2.1.0）
| 程式 | 作用 |
|------|------|
| `bear_presenter.py <專案> --character <角色資料夾>` | 讀 `build/timeline.json`（片頭長度、`scene_starts`）與 `build/narration_norm.wav`，用 Playwright 逐格算出角色畫格（15 fps、透明背景），依音量對嘴，疊到主片右下角 → `<主片>_黑熊講課.mp4`。舊版 timeline 沒有 `scene_starts` 時改讀 `章節_*.txt` |
| `append_outro.py <專案> <outro.mp4>` | 取輸出成品中最新、非「完整版」的 mp4，接上片尾（含片尾原音樂）→ `_完整版.mp4` |
| `build_video.bat` | 上面三步一次完成；CRLF；自動安裝套件；`產生紀錄.log` |

- `timeline.json` 新增 `intro_len`、`scene_starts`（每幕開始秒數），供角色手勢與後製對齊。
- 2 核心雲端容器實測：角色畫格約 9 格／秒；8 分鐘影片約 13 分鐘＋重新編碼。

## 十二、字幕安全區與單行字幕（v2.10.0）

| 設定／程式 | 行為 |
|---|---|
| `video.subtitle_safe`（預設 `true`） | 每張圖卡與 `type: anim` 畫面等比縮到 80%、水平置中、上緣 16 px，內容全部落在 y 880 以上；深色卡補同間距格線、淺色卡延伸邊緣，無接縫。設 `false` 恢復滿版 |
| `type: photo` | 預設滿版（課堂實景等背景照片）；**插圖、圖解、截圖、有標籤的圖加 `fit: safe`** 縮到字幕區以上；`side` 面板、`lines` 字卡、`plate` 名牌一律上移到 y 860 以上 |
| `type: video` | 不縮放；錄屏時把重點留在畫面上方 |
| `subs_oneline.py <專案>` | 讀 `2_製作中/字幕/字幕_zh-TW_<配音>.srt` 與 `build/narration_norm.wav`，切成一行一行並對齊旁白停頓，輸出 `字幕_zh-TW_單行.srt／.ass`，再把字幕燒進最新 `_完整版.mp4` → `_完整版_單行字幕.mp4`；`--format shorts`、`--no-burn` |

- 字幕樣式、字數與位置見 `references/subtitle-style.md`；Windows 用微軟正黑體（`C:/Windows/Fonts`），雲端用 Noto Sans CJK TC。
- 圖卡雜湊包含 `_safe`，切換設定後會自動重畫。
- 2026-10-21 驗證：本專案 15 種版型（含 photo 與 moon 動畫）在 y 882–1000 的內容只有背景（淺色卡零變化、深色卡只有格線）。
