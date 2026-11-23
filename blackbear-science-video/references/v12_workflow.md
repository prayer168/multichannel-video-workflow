# BlackBear Science Video V1.2 — C3 reference workflow

## Asset and science traceability
Each `shots.csv` row links `claim_ids`, `source_ids`, and `asset_ids`. Trace source links from `research/sources.csv` and `source_checks_20261123.csv`. `shot_fact_review.csv` does not itself assert a shot is scientifically true; its `review_status` requires an evidence-based editor sign-off. Any text overlays are editorial overlays, not generated text. Fictional and educational illustrations must not be passed off as scientific observations.

## Prompt completeness
Count existing bilingual legacy prompt pairs directly from `original/shot_list_108.csv` before using the normalized schema. In the Nemo regression 16 complete originals are preserved exactly; 92 new pairs are written to `shots.csv` and logged in `prompts/prompt_provenance.csv`. Never silently overwrite original CSV, script, JSON, HTML or timelines. Retain old English prompts even if editorial improvements might be desirable; propose separate errata for new editions.

## Gate definitions
- `handoff`: structural validity, immutable original checks, full prompt coverage, trace rows and rights audit present. Pending science/rights are explicit non-blocking warnings.
- `poc`: handoff plus CH01 S01–S04 exactly 0–27s and an offline original-vector placeholder renderer. No third-party media included.
- `production`: no pending scientific approval, no missing media, no unapproved asset rights, valid source trace. Use previous V1.1 production gate too.
- `release`: production plus human editorial approval and actual audio/video/subtitle output verification. Unfinished videos must remain blocked.

## Three key prohibitions
1. Do not take NASA/ESA/NOAA website visibility as final license clearance for an exact media file; check credit, original author and rights notice per item.
2. Do not generate realistic deepfake historical news or authentic-looking ISS/Mir documentary footage; use labelled CGI placeholders until rights cleared.
3. Do not edit historical script during this regression. Open future errata with a separate diff and human consent.

## Engineering handoff
First read `README_Handoff.md`, `README_V12.md`, `CLAUDE.md`/`AGENTS.md`, `reports/v12_*` and `production/ch01_poc/TASKS.md`; run integrity tests. POC uses entirely original shapes/text placeholders with optional silence; not a final film. Record remotion install, FFmpeg version, render checks, media license changes in test logs.
