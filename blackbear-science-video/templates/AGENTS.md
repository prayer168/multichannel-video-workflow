# Codex | BlackBear Science Video V1.3

This folder contains a traceable science-video handoff. Operate as engineering agent, **not** scientific reviewer, rights attorney, or final publisher. Never change original/ or fabricate source citations/license evidence.

## Verification before coding
- `python scripts/workflow_v13.py status .`
- `python scripts/audit_v13.py . --gate handoff`
- Inspect `shots.csv` and `research/claims.csv`, `research/sources.csv` + `assets/rights_decisions.csv`.
- For a reversible POC: `python scripts/render_smoke_v13.py .` (Pillow/FFmpeg optional; 720p original geometric placeholder).
- Treat `--gate production` and `--gate release` blockers as mandatory.

## Implementation contract
Build only a 20–30s technical sequence using **original** vectors/placeholders while review is pending; do not produce fake authentic agency footage. Log actual executed commands, tool versions, traces, ffprobe frame count, and limitations. Return artifacts under `production/poc/out/` and `reports/`. Do not claim Remotion has been installed or Claude Code was run merely because TSX source or an MP4 exists.
