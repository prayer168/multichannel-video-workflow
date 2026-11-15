# Machine-readable publishing contract

Create one `thumbnail_manifest.json` per video in its `製作後/縮圖候選/`; see `assets/manifest-example.json`:

- `schema_version`: `2.0`
- `channel_name`, `video_title`, `source_evidence`: simple strings and array
- `video_kind`: `long` or `short`
- `generator`: `{ "agent": "Codex", "model": "Images 2.6" }`
- `status`: `planned`, `generated`, `qa_passed`, or `approved`
- `selected_candidate`: candidate `id` or null
- `candidates`: `long` has exactly three items `A`/`B`/`C`; `short` has one to three items (`A` first). Each item has `id`, `type`, `hook`, `thumbnail_text` (exact text on the image), `paired_title`, `main_subject`, `layout`, `source_type` (`authentic_reference`, `licensed_reference`, `illustration`), `source_reference` (reference frame path and timestamp), `prompt`, `score` (0–100), `image_file` (path or null), `attempts` (generation count), `qa_status` (`pass`, `fail`, `not_tested`)
- `facebook_image`: `{ "file": "../臉書宣傳/臉書分享圖_1200x630.png" or "..._1080x1350.png" or null, "thumbnail_text": "...", "prompt": "...", "attempts": 0, "qa_status": "not_tested" }`
- `publishing`: `{ "authorized": false, "youtube_video_id": null, "ab_test_notes": "..." }`

Status meanings:
- `planned`: brief and prompts exist; no completed Images 2.6 output claimed.
- `generated`: files exist, not necessarily reviewed.
- `qa_passed`: all images intended for upload, including the Facebook image, passed checks.
- `approved`: the user selected the art or delegated final selection and the chosen image passed visual QA. Record the basis for selection in the QA notes. `publishing.authorized` records authorization to upload separately.

Only choose the most recently authorized selected candidate; do not let automatic score override a user choice. Editorial score is not predicted CTR. `validate_manifest.py` checks file paths relative to the manifest directory.

## MultiChannel Video Workflow handoff

- Keep candidate PNGs, reference frames, brief, Codex report, previews and manifest in the video's `製作後/縮圖候選/`. Use relative paths in the manifest.
- Export the approved candidate as an actual JPEG (RGB, quality 90 or higher) to `製作後/縮圖.jpg`, for the main video and for each Short. Respect an existing user selection and preserve an existing approved JPEG unless replacement was requested.
- Facebook share images go to `製作後/臉書宣傳/` under the exact names `fb_post.py` expects.
- When the user has not delegated or made a selection, return the candidates for review. Existing publishing authorization and the publishing skill govern the upload scope.
