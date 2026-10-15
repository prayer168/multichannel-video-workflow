# AI 影片生成動畫（Google Flow／Veo 等）

> 2026-10-10 首次用於《實測 Claude Mods》，使用者用 Google Flow（PRO 帳號）。其他工具（Gemini、Kling、Runway）流程相同，只是按鈕名稱不同；先請使用者截圖工具首頁再帶操作，不要憑記憶描述介面。
> 本檔是 `references/animation-handoff.md` 的工具操作補充：角色表、素材 ID、逐鏡提示詞內容與素材包依 animation-handoff.md；本檔只講在影片生成工具裡怎麼做。
> 動畫屬於影片素材，**不得**用來偽造軟體介面、測試結果或數字。

## 一、分工

| 類型 | 誰做 | 例子 |
|---|---|---|
| 角色動畫（有表情、動作） | 依可用工具由助理操作或引導使用者生成，提供提示詞與參考圖 | 開場情境、角色登場、收尾笑點 |
| 圖示／資訊動畫（箭頭、計數、紙張疊合） | Claude 用程式繪製（cards_lib／anims_lib／cairo） | 進度條、計數器、比對示意 |

不要為了「全部 AI 生成」而讓資訊動畫交給生成工具；數字與文字由後製加入才不會錯。

## 二、角色一致性

1. Claude 從分鏡參考圖裁出每個角色的乾淨半身圖（≥ 400 px、只含單一角色），存成 `角色_<名字>.png`。
2. 工具有「建立角色」（Flow：Create a character）時，每個角色建一次：上傳參考圖＋一段英文外觀描述（物種、配件、服裝、個性、畫風）。之後每段用同一組角色。
3. 外觀描述在所有段落一字不改；服裝或配件改了就重建角色，不在單段提示詞裡改。

## 三、提示詞結構（英文，整段貼上）

```
<這段的動作：誰、在哪裡、依序做哪 2～3 件事、最後的反應>
Style: hand-drawn 2D anime illustration, warm cozy wooden workshop, soft afternoon light, gentle paper texture,
warm cream, navy, orange, forest green and yellow accents. Static camera unless noted. Expressive but not exaggerated acting.
No text, no letters, no numbers, no logos, no subtitles, no real software screens anywhere.
Characters keep the exact same look and outfit as their references. 16:9.
Avoid: text, captions, numbers, watermarks, logos, extra limbs, warped faces, morphing characters, constant bouncing, flashing lights.
```

- 每段 5～8 秒、最多三個動作（準備 → 動作 → 反應）；長段落拆成數段再剪接，不要求一次生成 20 秒以上。
- 畫面要留給後製標籤的位置，在提示詞寫明（例：Keep the right third of the frame calm and empty）。
- 卡片、紙張一律寫 blank；文字、數字全部後製。
- 有場景參考圖時用「圖生影片」：先上傳場景參考，再貼動作提示詞。

## 四、挑選與交付

- 每段生成 2～4 個版本，挑角色不變形、沒有字、動作完整的一個；有亂碼文字、多手多腳、臉變了就重生成，不勉強使用。
- 下載 MP4，依素材 ID 命名（`A01.mp4`、`A13-1.mp4`），放到專案的 `動畫/` 資料夾（或 `2_製作中/B-roll與插圖/`）。
- Claude 取回後：裁頭尾半秒、統一 30 fps／1920×1080、放進對應鏡的動畫插槽（全幅），標籤與字幕後製疊加。
- 生成工具的使用條款與額度由使用者帳號負責；不替使用者購買點數或升級方案。

## 五、交付給使用者的檔案

放在使用者的錄屏／專案資料夾 `動畫參考/`：
- `角色_*.png`（建立角色用）
- `場景參考_Axx.png`（圖生影片用）
- `Flow動畫提示詞.txt`：角色描述、共用 Style、每段動作提示詞、命名規則


## 元件動畫與旁白同步

角色分件達不到自然動作品質時，可用Google Flow補短段；精確UI、數字與機關仍由程式控制。依 [ui-narration-animation.md](ui-narration-animation.md) 按實際旁白對齊動作、避免生成另一個主持人，下載與驗收後才整合。未取得原始影片列缺件，不宣稱已加入。
