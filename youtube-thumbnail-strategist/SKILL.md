---
name: youtube-thumbnail-strategist
description: 為黑熊老師的自然教室與 AI 觀測站製作成片後的全部縮圖：主影片 YouTube 縮圖三款候選、三支 Shorts 封面，以及主片與各支 Shorts 的 Facebook 分享圖，一律交由 Codex 調用 Images 2.6 生成，並驗收後交接上架。
---

# YouTube Thumbnail Strategist v2.0（Codex × Images 2.6）

## 多頻道影片流程

- 2026-11-15 使用者定案：主影片與三支 Shorts 剪輯完成後，**主影片縮圖、三支 Shorts 封面、四張 Facebook 分享圖全部交由 Codex 調用 Images 2.6 完成**。不再以 FFmpeg 截幀或 `fb_cover.py` 當成品，也沒有本機渲染備援。
- 在正式成片驗收後、上架前使用。主技能的 [頻道規則](../references/channel-routing.md) 與對應設定檔優先，縮圖設計參考 [頻道縮圖建議](references/brand-profiles.md)。
- 每批要交付 8 張成品（規格見 [Codex 生圖交接](references/codex-images-handoff.md)）：

| 影片 | YouTube | Facebook |
|---|---|---|
| `01_主影片` | `製作後/縮圖.jpg`，1280×720（16:9），A/B/C 三款候選選一 | `製作後/臉書宣傳/臉書分享圖_1200x630.png` |
| `02_/03_/04_Shorts_…` 各一支 | `製作後/縮圖.jpg`，1080×1920（9:16） | `製作後/臉書宣傳/臉書分享圖_1080x1350.png`（4:5） |

- 候選、提示詞、參考影格、manifest 和檢核都放在該支影片的 `製作後/縮圖候選/`。沿用使用者已選定或已授權代選的範圍，保留既有核定圖；只製作縮圖時交付圖檔即可。
- 只有腳本或逐字稿時，可先交付概念與提示詞（`planned`），待成片確認後再交給 Codex 生成。

## 分工

| 角色 | 工作 |
|---|---|
| 規劃端（Claude Code 或 Codex 本身） | 看成片與逐字稿、取參考影格、寫概念與評分、產出 `codex_images_brief.md` |
| Codex | 依 brief 調用 Images 2.6 生成每張圖、存到指定路徑、逐字核對中文、不合格就重生成 |
| 規劃端 | 尺寸檢查、手機預覽、事實／版權／品牌檢核、更新 manifest、交接上架 |

在 Claude Code 中執行時，brief 寫好後直接在本對話以 `codex exec` 把 brief 交給 Codex，不必切換到 Codex 視窗；**要在本機純英文路徑的工作資料夾執行**（雲端硬碟路徑會讓 Codex 沙箱失敗），先用一行測試確認額度，產出後回 Claude Code 驗收再複製到交付資料夾（流程見交接文件「從 Claude Code 交給 Codex」）；使用者直接在 Codex 開啟本技能時，Codex 自己走完全部步驟。**沒有成功的 Images 2.6 輸出檔，就不能說圖已完成。**

## Read supporting files as needed
1. `references/codex-images-handoff.md` — 8 張圖的規格、brief 範本、提示詞範本、`codex exec` 指令、重生成規則。
2. `references/strategy-and-scoring.md` — hooks, concepts, scoring, selection.
3. `references/brand-profiles.md` — natural science and AI Watch brand presets.
4. `references/production-and-safety.md` — real footage references, generated art, typography, output quality.
5. `references/publishing-contract.md` — manifest format and downstream integration.
6. `assets/input-template.json` — structured invocation input.
7. `assets/manifest-example.json` — machine-readable example.

## Workflow

### 0. Discover assets and capabilities
- Locate each video's final MP4 in `製作後/`, `最終逐字稿.txt`, `上架文案.txt`, channel profile, and any approved brand assets. Use only the authorized project. Do not crawl an unrelated project.
- Confirm Codex is reachable (`codex --version`, or the current session is Codex) and that Images 2.6 is available to it. If not, deliver the brief and manifest as `planned` and report what is missing; do not substitute frame grabs or local renders as finished art.

### 1. Evidence + hook extraction
- Watch or sample each final video. Record what the footage establishes versus inference, and pick 1 primary hook and a paired title promise per video.
- Extract 1–3 real reference frames per image with `ffmpeg -ss <秒數> -i "<正式版.mp4>" -frames:v 1 -q:v 2 "<縮圖候選>/ref_<用途>_<秒數>s.jpg"`. These are **reference inputs for Images 2.6**, not deliverables. Exclude intro/outro frames that do not match the topic.
- Mark any scientific claim or number that still needs verification; it may not appear on an image until verified.

### 2. Concepts
- **主影片**：3 distinct concepts A/B/C that differ in visual thesis and composition, not just wording/color. Candidate kinds: wow, why, experiment, result, contrast, problem-solution, verification, tutorial.
- **每支 Shorts**：1 cover concept based on that Short's own hook (not the main video's). The three Shorts must not repeat each other's text or composition.
- **Facebook**：the main-video share image reuses the selected main concept, re-composed for 1200×630; each Shorts share image reuses that Short's concept, re-composed for 4:5. Text may be slightly longer than YouTube (kicker + title) but follows the 7.5 Facebook copy for that video.
- Each concept records: target viewer, hook, subject, layout, emotion, exact Traditional Chinese text (主標 2–6 字，副標 ≤12 字), paired title, truth note, reference frames, rights note.

### 3. Score before generating
- Score main-video A/B/C out of 100 using `references/strategy-and-scoring.md`. Scores are editorial heuristics, **not** predicted CTR.
- Reject concepts with false claims, unsupported numbers or unlicensed third-party imagery regardless of score.

### 4. Hand off to Codex → Images 2.6
- Write `製作後/縮圖候選/codex_images_brief.md` per video folder (or one batch brief at the topic root listing all 8 images) following `references/codex-images-handoff.md`: output path, exact pixel size, aspect ratio, reference frames, full prompt, exact text string, brand rules, negative constraints.
- Images 2.6 renders the Traditional Chinese text **directly in the image**. The prompt quotes the exact string; Codex compares every character of the output with it and regenerates on any wrong, missing, simplified or extra glyph (max 3 attempts per image, then report `fail`).
- If Images 2.6 cannot output the exact pixel size, generate at the matching aspect ratio and resize/crop to the spec without cutting text or subject.
- Never claim images were rendered without a successful Codex/Images 2.6 output file.

### 5. Validate and report
- `python scripts/inspect_images.py <縮圖候選或製作後資料夾>`：checks size/ratio of thumbnail, Shorts cover and Facebook files and writes small previews (160×90 for 16:9).
- `python scripts/validate_manifest.py <thumbnail_manifest.json>`。
- Visual QA on each image at full size and phone size: Chinese text exactly matches the brief, legible, not clipped; subject clear; lower-right duration badge area kept clear on 16:9; Shorts cover keeps text out of the top/bottom UI zones; nothing contradicts the footage.
- Record per-file existence, generation attempts, QA result, and remaining human checks.

### 6. Hand off
Produce per video in `製作後/縮圖候選/`:
- `thumbnail_strategy.md`: evidence, hook, concepts, scorecard (main video), chosen concept, uncertainties.
- `codex_images_brief.md`: what Codex was asked to generate.
- `thumbnail_manifest.json`: matching `references/publishing-contract.md`.
- `thumbnail_QA.md`: text/truth/rights/mobile/brand checks with PASS, FAIL or NOT_TESTED.
- Generated images; approved ones copied to their final paths (`製作後/縮圖.jpg`, `製作後/臉書宣傳/臉書分享圖_*.png`).

## Non-negotiable behavior
1. Do not change the video or title promise to chase clicks without checking factual fit.
2. No invented measurements, before/after results, endorsements, copyrighted imagery, fabricated likenesses, or false depictions of a scientific phenomenon. A generated image may stylize what the footage shows; it may not show a result the footage does not.
3. No forecast CTR or guaranteed virality.
4. Status stays explicit. A brief or prompt file does not equal an image file.
5. Do not upload or publish without authorization. Follow the selection authority in the handoff contract.
6. Respond in Traditional Chinese to this user's publishing workflow.
