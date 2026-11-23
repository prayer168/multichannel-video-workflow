# BlackBear Science Video Skill V1.3 — install/use

## ChatGPT / Codex
A Skill is a directory containing `SKILL.md`; optional `scripts/`, `references/`, `templates/`. In ChatGPT desktop / Codex supporting standalone Skills, import or place the folder as directed by that client, then select `blackbear-science-video`. To call via ChatGPT mobile or web where standalone skills are not exposed, use a supported Plugin or reuse the Skill files in the chat/project; a ZIP attached to a conversation does **not** by itself install or activate a Skill.

Codex repository-local path (when supported): `<repository>/.agents/skills/blackbear-science-video/SKILL.md`; personal scope: `~/.agents/skills/blackbear-science-video/SKILL.md`.

## Claude Code
Place extracted directory at `<repository>/.claude/skills/blackbear-science-video/` or `~/.claude/skills/blackbear-science-video/` (project/personal). Keep SKILL.md at root of that folder.

## Example new project

```bash
python scripts/workflow_v13.py init ./sky_explainer --slug sky_explainer --title "天空為什麼是藍色？" --duration-ms 20000
python scripts/workflow_v13.py status ./sky_explainer
```

Complete A,B,C1,C2,C2_5,C3 only after creating their evidence files; check `references/v13_workflow.md` for mapping. Export with `python scripts/workflow_v13.py pack ./sky_explainer --out ./sky_explainer_c3.zip` and verify with `python scripts/verify_zip_v13.py ./sky_explainer_c3.zip`.

## Prerequisites
- Required for static audits: Python 3.10+ (stdlib only).
- Optional for 720p original graphics smoke: Pillow, FFmpeg and FFprobe.
- Optional for actual Remotion render: Node.js/npm, Remotion dependencies, Chromium; **not included/guaranteed by the ZIP**.
- External Claude Code and Codex must be installed/authenticated separately; agent real-world validation is still pending in this release.

## References
- OpenAI Build Skills: https://learn.chatgpt.com/docs/build-skills
- Anthropic Agent Skills: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
