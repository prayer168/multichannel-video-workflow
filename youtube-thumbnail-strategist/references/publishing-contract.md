# Machine-readable publishing contract

Create `thumbnail_manifest.json` with this shape; see `assets/manifest-example.json`:

- `schema_version`: `1.0`
- `channel_name`, `video_title`, `source_evidence`: simple strings and array
- `status`: `planned`, `generated`, `qa_passed`, or `approved`
- `selected_candidate`: `A`, `B`, `C`, or null
- `candidates`: exactly three items each with `id`, `type`, `hook`, `thumbnail_text`, `paired_title`, `main_subject`, `layout`, `source_type` (`authentic`, `licensed`, `illustration`), `source_reference`, `prompt`, `score` (0–100), `image_file` (path or null), `qa_status` (`pass`, `fail`, `not_tested`)
- `publishing`: `{ "authorized": false, "youtube_video_id": null, "ab_test_notes": "..." }`

Status meanings:
- `planned`: prompts and plan exist; no completed images claimed.
- `generated`: files exist, not necessarily reviewed.
- `qa_passed`: all candidates/images intended for upload have passed checks.
- `approved`: the user selected the art or delegated final selection and the chosen image passed visual QA. Record the basis for selection in the QA notes. `publishing.authorized` records authorization to upload separately.

Only choose the most recently authorized selected candidate; do not let automatic score override a user choice. Do not treat editorial score as predicted CTR. If `status=generated` or higher, image_file for the selected candidate must exist; validation script checks file paths when invoked from the manifest directory.

## MultiChannel Video Workflow handoff

- Keep candidate PNGs, report, previews and manifest in the video's `製作後/縮圖候選/`. Use relative image paths within that directory in the manifest.
- Export the approved candidate as an actual JPEG (RGB, quality 90 or higher) to the sibling path `製作後/縮圖.jpg`. Respect the user's existing selection and preserve an existing approved JPEG unless replacement was requested. The publisher consumes this JPEG as usual.
- When the user has not delegated or made a selection, return the candidates for review. Existing publishing authorization and the publishing skill govern the upload scope.
- For Shorts, record the selected frame timestamp and deliver a preview JPEG for verification. The horizontal A/B/C manifest and renderer apply to long-form thumbnails.
