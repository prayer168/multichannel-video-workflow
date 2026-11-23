# Claude Code Handoff — BlackBear Science Video Skill V1.3

## Scope and release boundary

This directory is the **V1.3 A–C3 preproduction technical release**. It covers scientific research workflow, script and storyboard handoff formats, per-shot evidence and rights gating, project state/checkpoint/restore, and local FFmpeg placeholders.

**Not yet verified:** a live Claude Code/Codex agent session, Remotion runtime render in the target system, science editor signoff, or publish-ready output. Never claim these are passed without actual logs.

## Claude Code installation (Windows PowerShell)

From this repository root:

```powershell
$skillDir = Join-Path $HOME ".claude/skills/blackbear-science-video"
New-Item -ItemType Directory -Path $skillDir -Force | Out-Null
Copy-Item -Path ".\skills\blackbear-science-video\*" -Destination $skillDir -Recurse -Force
```

Or use project-local `.claude/skills/blackbear-science-video/` as supported by your Claude Code version. Keep `SKILL.md`, `scripts/`, `references/`, and `templates/` together.

## First Claude Code task

1. Read `SKILL.md`, `INSTALL.md`, `references/v13_workflow.md`, and `V13_TEST_REPORT.md`.
2. Report available Python, Node, npm, FFmpeg, FFprobe, and Remotion versions, **without installing or buying anything automatically**.
3. Run `python scripts/workflow_v13.py --help` and a disposable new-project initialization, stage/status/checkpoint/restore/pack verification as documented.
4. If the user separately provides the private/working `point_nemo_c3_v1_3.zip`, unzip outside the skill directory; run `python scripts/audit_v13.py PATH_TO_NEMO --gate handoff` and check original file hashes.
5. Render only a short **original placeholder** CH01 smoke clip; inspect with FFprobe. Try Remotion only after dependency availability is confirmed.
6. Write `runlog.md`, `qa_results.json`, and `remaining_gaps.md`. Do not rewrite existing Nemo script/shotlist or change science and rights approvals.

## Safety and production gates

- `handoff`: may be PASS_WITH_WARNINGS as an engineering transfer.
- `production`: blocked until per-shot scientific reviews and rights decision proofs are approved by a named reviewer.
- `release`: blocked until editorial, license, output, captions, credits and final review are documented.
- Never publish fabricated scientific claims, real-location-looking AI footage as documentary reality, or unlicensed media.

## Repository placement

This V1.3 Skill is stored in an independent subdirectory to avoid replacing the existing unrelated video-from-photos root `SKILL.md`.

Source archive in ChatGPT (not in this repository): `blackbear_science_video_skill_v1_3.zip`.
Reference video project separately: `point_nemo_c3_v1_3.zip`.
