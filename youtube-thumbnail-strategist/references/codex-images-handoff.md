# Codex × Images 2.6 生圖交接

2026-11-15 使用者定案：主影片與三支 Shorts 剪輯完成後，主影片縮圖、三支 Shorts 封面和四張 Facebook 分享圖，一律由 Codex 調用 Images 2.6 生成。繁體中文標題由 Images 2.6 直接畫在圖上。沒有本機截幀或 `fb_cover.py` 的備援；Codex 或 Images 2.6 不能用時，只交付 brief，狀態標為 `planned`，之後補做。

## 一批 8 張圖的規格

| # | 用途 | 輸出路徑（相對主題根目錄） | 像素 | 比例 | 安全區 |
|---|---|---|---|---|---|
| 1 | 主影片 YouTube 縮圖（A/B/C 三款，核定一款） | `01_主影片/製作後/縮圖候選/thumbnail_A.png`、`_B`、`_C` → 核定稿 `01_主影片/製作後/縮圖.jpg` | 1280×720 | 16:9 | 右下角約 18%×14% 留給片長標籤；文字離邊至少 5% |
| 2–4 | Shorts 01–03 YouTube 封面 | `0X_Shorts_…/製作後/縮圖候選/shorts_cover.png` → `0X_Shorts_…/製作後/縮圖.jpg` | 1080×1920 | 9:16 | 文字放在中間 1080×1350 範圍；上 15%、下 20% 避開 Shorts 介面 |
| 5 | 主影片 Facebook 分享圖 | `01_主影片/製作後/臉書宣傳/臉書分享圖_1200x630.png` | 1200×630 | 1.91:1 | 文字離邊至少 6%；預覽卡可能裁到 1:1 中央，主體與主標放中間 |
| 6–8 | Shorts 01–03 Facebook 分享圖 | `0X_Shorts_…/製作後/臉書宣傳/臉書分享圖_1080x1350.png` | 1080×1350 | 4:5 | 文字離邊至少 6% |

- YouTube 用的 `縮圖.jpg` 是 RGB JPEG、品質 90 以上，從核定的 PNG 轉出。Facebook 分享圖保留 PNG，`fb_post.py` 會自動顯示在複製頁。
- Images 2.6 不能直接輸出指定像素時，用最接近的同比例尺寸生成，再以 Pillow 等比縮放或居中裁切到規格，不可裁到文字或主體。裁切後重新做文字核對。
- 已有使用者核定的圖時保留，不覆寫；需要重做時另存 `_v2`。

## brief 範本（`codex_images_brief.md`）

規劃端每批寫一份，放在主題根目錄的 `縮圖候選_codex_images_brief.md`，或每支影片的 `製作後/縮圖候選/codex_images_brief.md`。每張圖一節：

```markdown
## 圖 1A：主影片 YouTube 縮圖候選 A
- 頻道：blackbear-science（黑熊老師的自然教室）
- 輸出：01_主影片/製作後/縮圖候選/thumbnail_A.png，1280×720，16:9
- 參考影格：01_主影片/製作後/縮圖候選/ref_A_83s.jpg（成片 01:23，水滴落在果莢上）
- 圖上文字（逐字照抄，不可增減）：主標「一滴就開？」；副標「消渴草果莢實驗」
- 字體與位置：粗黑體、白字深色描邊，主標放左側 1/3，高約畫面 22%；副標在主標下方
- 主體與構圖：依參考影格的真實果莢與水滴，放大置右，背景簡化
- 品牌：自然教室配色；不加 AI Watch 元素；熊掌徽章只用核定檔 <路徑>（沒有就不加）
- 不可出現：參考影格沒有的結果（例如爆開、噴水）、其他文字、浮水印、第三方 Logo、假 UI、簡體字
- 驗收：主標與副標逐字相符、手機 160 px 寬仍可讀、右下角留空
```

## 給 Images 2.6 的提示詞範本

```text
Create a {用途} image, exactly {寬}x{高} px ({比例}), for the Traditional Chinese YouTube channel "{頻道名}".
Base the subject on the attached reference frame: {參考影格描述}. Keep the real subject, materials and result exactly as shown in the reference; you may simplify the background, improve lighting and enlarge the subject.
Render this Traditional Chinese text exactly, character for character, and no other text:
  Title: 「{主標}」
  Subtitle: 「{副標}」
Typography: {字體與位置}. Use Traditional Chinese glyphs only (no Simplified forms). Text must be fully inside the safe area: {安全區}.
Composition: {構圖}. Brand: {品牌規則}.
Do not add: results not visible in the reference, extra words, numbers, watermarks, logos, fake UI, real people's likeness that is not in the reference.
```

## 從 Claude Code 交給 Codex

brief 和參考影格放好後，在主題根目錄執行（`<brief>` 換成實際檔名）：

```bash
codex exec -C "<主題根目錄>" -s workspace-write --skip-git-repo-check "讀取 <brief>，依每一節用 Images 2.6 生成圖片並存到指定路徑。每張生成後逐字核對圖上繁體中文與 brief 是否完全相同，不符就重生成，最多 3 次；完成後在 <brief> 同資料夾寫 codex_images_report.md，列出每張的路徑、像素、嘗試次數與核對結果。不要上傳或發布。"
```

- 參考影格也可用 `-i <檔案>` 附給 Codex；brief 裡已寫路徑時不必重複。
- 指令跑完後，規劃端讀 `codex_images_report.md`，並以 `Read` 或圖片檢視親自看每張圖，再進入驗收。Codex 回報成功但檔案不存在，以檔案為準，記為失敗。
- 使用者直接在 Codex 開啟本技能時，略過這段指令，Codex 依 brief 直接生成。

## 文字核對與重生成

每張圖都要：

1. 把圖上看到的每個字抄下來，與 brief 的字串逐字比對（含標點與問號全形半形）。
2. 出現錯字、缺字、多字、簡體字、亂碼或字被裁切，就用同一份提示詞再生成；可加一句「上次把『X』寫成『Y』，請修正」。
3. 同一張最多 3 次。3 次都不合格時記 `fail`，回報使用者，不改用截幀或本機疊字成品頂替。

## 狀態

- `planned`：brief 已完成，還沒有成功的 Images 2.6 輸出。
- `generated`：檔案已由 Images 2.6 產生，尚未驗收。
- `qa_passed`：尺寸、文字、事實、版權、品牌都通過。
- `approved`：使用者已選定或授權代選，核定稿已複製到最終路徑。
