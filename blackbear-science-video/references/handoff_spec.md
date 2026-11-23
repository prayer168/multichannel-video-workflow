# C3 製片包契約 v1.0

## Standard structure
```
project_slug/
  README.md
  CLAUDE.md
  AGENTS.md
  TASKS.md
  project_manifest.json
  CHANGELOG.md
  outline.md
  script.md
  visual_bible.md
  shots.csv
  qa_report.md
  research/sources.csv
  research/claims.csv
  assets/asset_register.csv
  prompts/shot_prompts.md
  production/render_spec.md
  production/acceptance.md
```

## Required CSVs
`sources.csv`: source_id,title,author_or_org,published_date,url,source_type,accessed_date,verification_status,notes
`claims.csv`: claim_id,claim_text,source_ids,evidence_level,scientific_guardrail,review_status
`shots.csv`: shot_id,chapter,start_ms,end_ms,duration_ms,visual_type,visual_description,camera_movement,narration,onscreen_text,audio_sfx,claim_ids,source_ids,asset_ids,rights_status,prompt_zh,prompt_en,priority,status
`asset_register.csv`: asset_id,asset_type,origin_url,author,license,license_evidence,attribution_required,usage_scope,local_path,rights_status,notes

### License statuses
`CLEARED`, `PENDING`, `BLOCKED`, `ORIGINAL` (經核驗自行創作)；使用者聲稱授權不等於授權文件已核實。`PENDING`/`BLOCKED` 的素材不得用於正式公開版。

## Timing
- All start_ms/end_ms integers; start_ms >=0, end_ms > start_ms; duration_ms=end_ms-start_ms.
- Shots sorted and contiguous, no overlaps or gaps unless explicitly represented as shots.
- Sum equals manifest `target_duration_ms`; if runtime intentionally flexible, revise manifest with recorded approval.
- fps 30 by default. Audio, subtitles and transitions must conform.

## Handoff gate
Ready for engineering preview: schemas/timing pass; placeholders are disclosed.
Ready for public final: all critical science claims checked; rights statuses cleared/original, no unresolved blocking item; separate human quality review.

## Examples
- 《仿生科技實驗室》：建立生物機制→工程模仿→應用限制的單元結構；勿把概念展示誤稱量產產品。
- 《尼莫點》：確認座標、最近陸地距離、ISS 比較之條件、航太器受控再入範圍，不得把概念化敘事當持續現況。
