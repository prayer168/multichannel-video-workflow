# V1.1 thumbnail rendering guidance

## Hard capabilities
- Requires FFmpeg + FFprobe, Python 3 and Pillow. On this Windows setup, use `$env:LOCALAPPDATA/AI-Video-Tools/youtube-thumbnail/.venv/Scripts/python.exe` if it exists. Otherwise use a Python environment with Pillow installed.
- The default renderer extracts 18 time-distributed frames and selects one from each third of the video by a simple sharpness/brightness heuristic. **This is not semantic highlight detection**. The agent must review frames and replace concept/capture selections as needed.
- Each exported thumbnail is **1280×720 PNG** and comes with a **160×90 JPEG** smartphone readability preview. YouTube upload constraints may change; check official guidelines before uploads.
- Supply each candidate's `timestamp_sec` in `--concepts-json` to use an exact source moment. Candidates without that field use the sampled suggestion for their third of the video. The report records the timestamps actually used.
- Accurate Chinese text is drawn with a local licensed CJK font. The image generation model never renders lettering.
- Optional `--ai-provider openai --allow-illustration` generates **conceptual** backgrounds using an API request, not evidence photographs; outputs are visibly labeled 示意圖. Calls require paid API access and are NOT made in the default pathway. If API outputs cannot be obtained, the script fails clearly.
- No direct YouTube upload, no automatic A/B test creation, and no claim of measured CTR or successful real experiment. Review the candidates and apply the selection authority in the publishing contract.

## Workflow commands
```powershell
python -m pip install Pillow
python scripts/render_thumbnails.py --video "D:\\Videos\\final.mp4" --title "水滴會發電嗎？" --channel natural --output "D:\\Videos\\thumbnails" --concepts-json assets/v1_1-concepts-example.json
```
If no concepts JSON supplied, the renderer uses generic placeholders; the agent **must** prepare specific truthful concepts for release quality.

### Optional illustrated AI backgrounds
```powershell
$env:OPENAI_API_KEY = 'your-key-in-local-env'  # never commit the key
python scripts/render_thumbnails.py --video "D:\\Videos\\final.mp4" --title "AI 自己操作電腦？" --channel aiwatch --output "D:\\Videos\\thumbnails-ai" --concepts-json assets/v1_1-concepts-example.json --ai-provider openai --allow-illustration
```
OpenAI account/model support and API pricing are separate. To avoid depicting fabricated real experiments, use the authentic-frame mode for scientific evidence.

## Truth & publishing gate
- Agent reads actual transcript/footage and maps each hook to a video timestamp or a verified claim.
- Distinct concepts must have different **hooks and compositions**, not just typographic variations. The renderer provides three layouts but content-level distinctness depends on `--concepts-json`.
- Do not use figures, celebrities, logos, demonstrations, or any third-party visual without legal/rights review.
- Use `thumbnail_report.json` as an integration artifact. The renderer writes `PENDING_HUMAN_REVIEW`; record any later selection and authority in the manifest and handoff, separately from render metadata.
- Automated high visual scores never imply a high CTR. Validate through YouTube analytics and controlled experiments.
