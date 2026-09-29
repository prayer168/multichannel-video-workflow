# 一鍵產生影片（build.py）

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
    - {at: 16, type: video, src: 相對路徑.mp4, watermark: false}
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
