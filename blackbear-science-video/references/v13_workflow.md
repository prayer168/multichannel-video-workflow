# BlackBear V1.3 workflow and gate contract

## Minimal stage evidence
- A: `research/brief.md` plus `research/sources.csv` / `research/claims.csv`
- B: `script/script.md` (approved or preserved; do not erase an existing B original)
- C1: `visual/style_bible.md`
- C2: `shots.csv`, integer `start_ms/end_ms/duration_ms`, bilingual `prompt_zh/prompt_en`, IDs linked
- C2_5: `research/fact_review.csv` + `assets/rights_decisions.csv`
- C3: `README_Handoff.md`, `CLAUDE.md`, `AGENTS.md`, integrity-verifiable ZIP
- D: rendered production movie and independent production evidence (requires `production` gate PASS)
- E: signed release evidence + all QC passed (requires `release` gate PASS)

Completion marks a file present, time-ordered, hash-tracked preproduction artifact; it does not silently imply license or scientific expert approval. The CLI refuses phase skipping and provides explicit checkpoint restore. Original source folders are read-only.

## Gate meaning
- `handoff`: validates schema, timeline, SHA lock, reference integrity, prompt completeness and saved phase-evidence hashes. Missing formal scientific approvals/media rights can be **warnings**.
- `poc`: checks suitable technical test artifacts. For legacy Nemo includes the original C1/27s four-shot POC range check.
- `production`: additionally requires all fact and media rights to be signed off. For legacy projects V1.2 gate remains authoritative.
- `release`: additionally needs independent output, subtitle, sound timing, science and rights checks.

All reports are JSON + Markdown in `reports/v13_<gate>`. Audit is deterministic/offline; a topic URL appearing in a registry never establishes its scientific truth or license terms.

## Important compatibility notes
The V1.2 Point Nemo package is an explicit **legacy adapter** because its 108-shot structure is user-approved. The V1.3 generic workflow supports other topics and shot counts; it does not hardcode 108 in generic mode. Do not migrate original script into auto-generated text.

## Implementation and security limitations
- Checkpoints capture derivative text files and small documents; not large video render files, API secrets or original footage.
- Recovery validates stored SHA and original lock; it produces a dry-run first; `--apply` is explicit.
- Local SHA proves change detection versus a stored baseline, not external notarization. Backup/version-control originals separately.
- ffmpeg smoke has no narration or licensed assets, hence never satisfies D or E.
- External agent execution evidence should record exact `claude` / `codex` CLI version, commands, dependency installation result, render hash and responsible reviewer.
