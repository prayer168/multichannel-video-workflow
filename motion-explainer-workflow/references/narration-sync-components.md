# 旁白逐字時間與同步元件（2.32.0）

讓畫面動作落在**關鍵詞開口的那一刻**，而不是句首。兩個部件：

| 部件 | 位置 | 做什麼 |
|---|---|---|
| 逐字時間 | `../../scripts/build/narration_word_timing.py` | 已知定稿旁白，用 whisper.cpp 聽一次，把每個字對回旁白文字，輸出 `words.json`（每句、每字的開口秒數） |
| 同步元件庫 | `../template/narration-sync-components/components.js` | 「給時間 t 就回傳那一刻 SVG 字串」的純函式：`tabs`、`slots`、`tag`、`stamp`、`label` 等，時間只從 `words.json` 的落點來 |

示範頁 `../template/narration-sync-components/index.html` 是自然教室 Shorts〈海邊的沙子是岩石嗎〉N01–N04（約 21 秒）的試片。

## 1. 產生 words.json

```
python scripts/build/narration_word_timing.py --audio 旁白.wav --script 旁白.txt --out words.json
python scripts/build/narration_word_timing.py --audio 旁白.wav --script 旁白.txt --out words.json --offset 4.0   # 旁白前有 4 秒片頭
python scripts/build/narration_word_timing.py --words words.json --cue S03@沉積物 --cue S05@一層一層#2          # 查落點秒數
```

- `旁白.txt`：一句一行，必須和配音**一字不差**（定稿旁白，不是 whisper 聽到的字）。行首可寫句 ID；沒寫就自動編 S01、S02…
- 預設使用 `%USERPROFILE%\AI-Video-Tools\motion-explainer\whisper\cpp\` 的 `main.exe` 與 `ggml-medium.bin`，不另外下載模型。
- 精度約 0.1–0.2 秒（token 層級）。對不上的字用前後對上的字內插，報告會標「⚠ 內插」。
- 需要更準的時間時，改用 mv-director 的 Qwen3 強制對齊（見 `music-mv-tools-integration.md`）。

輸出格式：

```json
{"offset": 0.0, "engine": "...", "match_ratio": 0.97,
 "sentences": [{"id": "S03", "text": "...", "start": 12.3, "end": 15.8,
                "chars": [{"c": "沉", "t": 14.1, "end": 14.3, "matched": true}, ...]}]}
```

## 2. 兼作配音內容核對

同一支工具也是固定設定要求的「生成後用語音辨識核對內容」：

- 每句都依序對上、最後一句的結束時間接近音檔長度 → 沒有離稿。
- 報告最後的「辨識差異」多半是同音字（波→播、七股→七谷、臺→台），不是配音念錯。
- **比對率低於 0.85**：先確認音檔和旁白是同一版。若 whisper 輸出成簡體字，或出現跳句、重複句，可能是 whisper 自己的假象。

  **實例（2026-11-16《臺灣天空的守望者》）**：S11–S12 一度辨識出「颱風還在海上的時候」念了兩次，比對率也偏低。把音檔切成 10～25 秒的片段，帶時間碼（`-ml 1 -sow`）重新辨識後，確認只念了一次、而且照稿。再次證實：整段辨識異常時，先切段重聽，不要直接判定配音有問題。

## 3. 落點寫法（words.json → 秒數）

腳本與元件庫共用同一套落點語法，畫面程式裡**只寫句 ID＋旁白原詞，不寫秒數**：

| 寫法 | 意思 |
|---|---|
| `S03` | S03 句首 |
| `S03$` | S03 句尾 |
| `S03@沉積物` | S03 裡「沉積物」開口時 |
| `S03@一層#2` | S03 裡第 2 次出現「一層」時 |

換配音或重做某一幕後，只要重跑 `narration_word_timing.py`，所有動作自動跟著新的時間走。

## 4. 元件的時間規則

- 每個動作在落點前 `LEAD = 0.2` 秒起勢、落點後 `TAIL = 0.15` 秒完成，所以變化的中點正好在關鍵詞開口那一刻。
- `prog(t, at)` 回傳 0→1 的進度；`at` 還沒定義時永遠是 0，不會誤觸發。
- 頁面規則和 Motion Showreel、mv-director 相同：`window.render(t)`、`window.READY`；`window.CUE_TIMES` 列出所有落點，供逐幀渲染時做同步檢查。

| 元件 | 用途 |
|---|---|
| `tabs` | 常駐章節導覽：講過的打勾、正在講的亮起 |
| `slots` | 句子一提到「有幾樣」就先排好空位（問號），講到哪一樣才翻成內容，中途不重排 |
| `tag` | 問題標籤從主體上方彈出 |
| `stamp` | 印章從大縮到定位，略帶旋轉 |
| `label` | 一行標註在關鍵詞那一刻滑入 |

## 5. 未隨 repo 提供

- **字型**：示範頁讀 `fonts/NotoSansTC-VF.ttf`。字型不放進 repo；從 Google Fonts 下載 Noto Sans TC 可變字型放到 `template/narration-sync-components/fonts/`。
- **逐幀渲染腳本**：示範頁註解提到的 `render_frames.py` 不在本 repo。輸出 MP4 時改用 Motion Showreel 的渲染腳本或 HyperFrames（兩者都支援 `window.render(t)` 頁面，見 `motion-showreel-integration.md`、`tool-choice.md`）。
- Remotion 專案可直接讀 `words.json`，用 `start × fps` 換算成影格，不需要這個 JS 元件庫。
