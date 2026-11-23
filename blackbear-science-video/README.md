# BlackBear Science Video Skill V1.3.0

**Release scope:** stable science documentary **preproduction A–C3 + offline technical POC**. Claude Code/Codex external CLI execution and published video D/E approval remain unverified/blocked. See `V13_TEST_REPORT.md`.

## New features
- General `init` — creates independent topics, not tied to Point Nemo's 108 shots.
- Explicit A→B→C1→C2→C2.5→C3 workflow stage status and evidence signatures.
- Automatic checkpoints with SHA verification, dry-run recovery and explicit restore.
- Generic audits plus V1.2 Nemo source-protecting adapter.
- Self-contained handoff ZIP with SHA checks, verified after extraction.
- Offline all-original 720p technical video renderer (optional Pillow + FFmpeg).
- Independent Claude Code (`CLAUDE.md`) and Codex (`AGENTS.md`) contract templates.

## Quick start

```bash
python scripts/workflow_v13.py init ./new_project --slug new_project --title "你的科普主題" --duration-ms 1080000
python scripts/workflow_v13.py status ./new_project
python scripts/audit_v13.py ./new_project --gate handoff
```

A brand new empty project correctly FAILS handoff until researched and populated. Preserve original approved files; don't invent factual proof, asset rights, external tool execution or release authority. See `INSTALL.md` and `references/v13_workflow.md`.
