---
name: youtube-thumbnail-strategist
description: 為黑熊老師的自然教室與 AI 觀測站製作成片後的 YouTube 縮圖。依成片畫面與逐字稿設計三款長片候選、輸出手機預覽，或從各支 Shorts 選封面影格，並把核定圖交接上架。
---

# YouTube Thumbnail Strategist v1.1

## 多頻道影片流程

- 在正式成片驗收後、上架前使用。主技能的 [頻道規則](../references/channel-routing.md) 與對應設定檔優先，縮圖設計參考 [頻道縮圖建議](references/brand-profiles.md)。`blackbear-science` 對應渲染參數 `natural`，`ai-watch` 對應 `aiwatch`。
- 長片讀取 `製作後/` 的正式 MP4、最終逐字稿及上架文案。先看原始影格、排除片頭片尾等不符主題的畫面，再替三款概念各填實際時間碼 `timestamp_sec`。同一個時間點只有在畫面確實支撐各概念時才可共用。
- Shorts 各自回看直式成片，挑可辨識主題的真實影格，記錄時間碼並以原顯示比例輸出封面預覽。可用 `ffmpeg -ss <秒數> -i "<Shorts正式版.mp4>" -frames:v 1 -q:v 2 "<候選資料夾>/shorts_cover.jpg"`。需要備選時另取影格。發布端依當時介面支援處理。
- 每支的候選、概念與檢核放在該支 `製作後/縮圖候選/`。正式圖按 [交接規格](references/publishing-contract.md) 存成 `製作後/縮圖.jpg`。沿用使用者已選定或已授權代選的範圍，保留既有核定圖；只製作縮圖時交付圖檔即可。
- 只有腳本或逐字稿時，可先交付長片概念與提示詞，待成片確認後再選幀。

## Mission
Turn a completed video, script, storyboard, or transcript into **three differentiated, factual, mobile-legible thumbnail candidates** for YouTube, with a machine-readable plan and auditable QA. Optimize for viewer understanding and curiosity, **never promise CTR or subscriber growth**.

## When to invoke
- A user asks to generate, improve, review, or A/B-test a YouTube thumbnail.
- A publishing pipeline finishes a video and needs thumbnail artwork + upload copy coordination.
- User explicitly invokes `/youtube-thumbnail-strategist` (Claude Code) or `$youtube-thumbnail-strategist` (Codex, if exposed as a skill).
Do not invoke for unrelated image requests.

## Read supporting files as needed
1. `references/strategy-and-scoring.md` — hooks, concepts, scoring, selection.
2. `references/brand-profiles.md` — natural science and AI Watch brand presets.
3. `references/production-and-safety.md` — real footage, generated art, typography, output quality.
4. `references/publishing-contract.md` — manifest format and downstream integration.
5. `assets/input-template.json` — structured invocation input.
6. `assets/manifest-example.json` — machine-readable example.

## Workflow

### 0. Discover assets and capabilities
- Ask for or locate `video_path`, `transcript_path`, `script_path`, `working_title`, `description`, `channel_name`, and any existing brand asset or thumbnails in the project. Use only provided/authorized local paths. Do not crawl an unrelated project.
- If a video is supplied and tools permit, sample a few relevant frames or use existing frames. Use FFmpeg and Pillow for footage-based production. Report a missing capability when it prevents a requested deliverable.
- If no usable input exists, request the title plus synopsis; otherwise continue with available evidence, labeling inferences.
- Match the channel profile from `references/brand-profiles.md`.

### 1. Evidence + hook extraction
- Record what is directly established by footage/script versus inferred. Select 1 primary hook and a complementary title promise. Identify any claims or numbers requiring verification.
- For factual science footage, mark synthesized or conceptual visuals as illustration. Never assert imagined experiments or timings occurred.

### 2. Create 3 DISTINCT concepts
- A/B/C must differ in **visual thesis and composition**, not just wording/color.
- Candidate kinds: wow, why, experiment, result, contrast, problem-solution, verification, tutorial.
- Each candidate: target viewer, hook, subject, secondary elements, layout, emotion, 2–5 Traditional Chinese characters suggested (up to 8 if essential), recommended paired title, truth note, rights/source note, generation prompt, and constraints.

### 3. Score before generating
- Score 100 points using `references/strategy-and-scoring.md`: subject clarity 20, curiosity 20, mobile legibility 15, title synergy 15, factual fit 15, channel fit 15.
- These scores are an editorial heuristic, **not** predicted CTR or YouTube-proven outcomes.
- Reject any concept with false factual claims, unsupported numeric outcomes, or unlicensed third-party imagery regardless of score.
- Pick primary and backup. If all fail, revise concepts.

### 4. Produce artwork (when image tools exist)
- Prefer approved, authentic video frames or authorized footage for real-world science demonstrations.
- Use the image tool available in the user's runtime; **never claim images were rendered without a successful file/tool output**. If no image tool is available, deliver exact render prompts and a production-ready manifest as `planned`, not `generated`.
- For Traditional Chinese accuracy: render imagery **without embedded text**, then composite the final Traditional Chinese text as a separate layer using a properly licensed locally available CJK font. Do not fabricate typography or modify an observed scientific result.
- For standard video thumbnails, prefer 16:9; V1.1 renderer outputs 1280×720 PNG plus 160×90 preview; higher-resolution masters require a separately configured production pipeline. Check upload limits against the current official policy before publishing.
- Export three named long-form candidates where supported: `thumbnail_A.png`, `thumbnail_B.png`, `thumbnail_C.png`; and an optional `thumbnail_selected.png`. Do not silently overwrite human-selected art.

### 5. Validate and report
- Run `python scripts/validate_manifest.py <path-to-manifest.json>` from the skill folder (standard library only). Run `python scripts/inspect_images.py <path-to-output-folder>` when images exist (uses Pillow if installed).
- Perform a visual QA at roughly 160×90 px: subject distinct? Chinese text legible? duration overlay safe? excessive clutter? false representation?
- Record per-file existence, output status, licenses/approvals, dimensions, and remaining human checks.
- Hand off any authorized publication to the separate publishing skill.

### 6. Hand off
Produce:
- `thumbnail_strategy.md`: evidence, key hook, concept A/B/C, scorecard, chosen concept, uncertainties.
- `thumbnail_manifest.json`: machine-readable candidates and downstream fields, matching `references/publishing-contract.md`.
- `thumbnail_prompts.md`: one prompt per candidate plus negative constraints, intended text, and title pairing.
- `thumbnail_QA.md`: truth/rights/mobile/brand/final checks with PASS, FAIL, or NOT_TESTED.
- `thumbnail_A/B/C.png` only if images were actually rendered.

## Non-negotiable behavior
1. Do not change the video or title promise merely to chase clicks without checking factual fit.
2. No invented measurements, before/after results, endorsements, copyrighted imagery, or false depictions of a scientific phenomenon.
3. No claim of forecast CTR or guaranteed virality. Concept scores are design judgments only.
4. Keep image rendering optional and status explicit. A prompt file does not equal an image file.
5. Do not upload or publish without authorization. Follow the selection authority in the handoff contract.
6. Respond in Traditional Chinese to this user's publishing workflow.


## V1.1 executable thumbnail renderer

**Start with real footage.** Never say that AI images exist unless the renderer successfully produced them.

1. Read `references/v1_1-rendering.md` before generating.
2. Verify `ffmpeg`, `ffprobe`, Python 3 and Pillow. If any are unavailable, report the missing dependency.
3. Execute `python scripts/render_thumbnails.py --video "<actual-video>" --title "<title>" --channel natural --output "<output-directory>"` (use `--channel aiwatch` for AI Watch). This runs **real-footage mode by default** and exports 3 PNGs, a preview contact sheet, and machine-readable JSON. This does not require an API key.
4. Prefer a prepared `--concepts-json` with three evidence-based concepts (template `assets/v1_1-concepts-example.json`), with verified `timestamp_sec` values after inspecting footage. Short text must not misstate actual footage.
5. To request **optional generative backgrounds**, use `--ai-provider openai --allow-illustration` and a configured `OPENAI_API_KEY`. Generated background is a conceptual illustration and the renderer labels it `示意圖`; do not use for fake documentary evidence. AI mode requires network + paid API. If it fails, don't conceal failure or silently pretend that frames are AI images.
6. Review `thumbnail_report.json`, `thumbnail_contact_sheet.jpg`, three full PNGs and the 160px previews; check safety and publication permission. The renderer never uploads or publishes.
7. CLI command `python scripts/render_thumbnails.py --help` documents all options. This version does NOT perform image semantic understanding itself: visual choice is a heuristic over footage plus agent-supplied concepts; manual/agent review remains required.
