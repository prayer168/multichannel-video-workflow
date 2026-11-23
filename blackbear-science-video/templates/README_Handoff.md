# C3 Handoff — BlackBear V1.3

This is a cross-tool portable science-video preproduction package. The audited **handoff** gate checks structural completeness; **production** and **release** require separate scientific/media rights and publishable output approvals.

Run:

```bash
python scripts/workflow_v13.py status .
python scripts/audit_v13.py . --gate handoff
python scripts/audit_v13.py . --gate production
```

Only the first two are expected to pass while rights and scientific review are pending. For an offline nonpublishable test (optional Pillow and FFmpeg): `python scripts/render_smoke_v13.py .`. Do not rewrite original approved scripts. Read `CLAUDE.md` or `AGENTS.md` for tool-specific tasks.
