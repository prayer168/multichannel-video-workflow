"""Offline preflight only. Never uploads files or accesses credentials."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HEADINGS = ("YouTube 標題", "說明欄", "標記 Tags", "置頂留言")


def inspect(manifest_path):
    manifest_path = Path(manifest_path).resolve()
    data = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    errors, warnings, reports = [], [], []
    if not isinstance(data, dict):
        raise ValueError("Manifest must be a JSON object")
    if not isinstance(data.get("batch_id"), str) or not data["batch_id"].strip():
        errors.append("batch_id is required")
    channel = data.get("channel", {})
    if not isinstance(channel, dict) or not re.fullmatch(r"UC[A-Za-z0-9_-]{22}", str(channel.get("youtube_channel_id", ""))):
        errors.append("channel.youtube_channel_id must be a verified UC channel ID")
    if data.get("visibility") not in ("public", "private", "unlisted"):
        errors.append("visibility must be public, private or unlisted")
    items = data.get("items")
    if not isinstance(items, list) or any(not isinstance(i, dict) for i in items):
        raise ValueError("items must be an array of objects")
    if len(items) != 4 or sum(i.get("kind") == "long" for i in items) != 1 or sum(i.get("kind") == "short" for i in items) != 3:
        errors.append("Standard batch requires one long video and three Shorts")
    ids, fingerprints = set(), {}
    long_ids = {i.get("id") for i in items if i.get("kind") == "long" and isinstance(i.get("id"), str)}

    def file_path(value, label):
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{label}: missing file path")
            return None
        path = Path(value)
        path = (manifest_path.parent / path).resolve() if not path.is_absolute() else path.resolve()
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"{label}: file missing or empty: {path}")
            return None
        return path

    for index, item in enumerate(items):
        key = item.get("id")
        label = key if isinstance(key, str) and key else f"item[{index}]"
        if not isinstance(key, str) or not key or key in ids:
            errors.append(f"{label}: missing or duplicate item ID")
        else:
            ids.add(key)
        for field in ("made_for_kids", "altered_content"):
            if type(item.get(field)) is not bool:
                errors.append(f"{label}: {field} needs a supported true/false decision")
        if item.get("kind") == "short" and item.get("related_to") not in long_ids:
            errors.append(f"{label}: related_to must identify this batch's long video")
        report = {"id": label, "kind": item.get("kind")}
        video = file_path(item.get("video"), f"{label}.video")
        if video:
            digest = hashlib.sha256()
            with video.open("rb") as source:
                for chunk in iter(lambda: source.read(4 * 1024 * 1024), b""):
                    digest.update(chunk)
            sha = digest.hexdigest()
            if sha in fingerprints:
                errors.append(f"{label}: same video bytes as {fingerprints[sha]}")
            fingerprints[sha] = label
            report.update(source_path=str(video), sha256=sha, bytes=video.stat().st_size)
        copy = file_path(item.get("copy"), f"{label}.copy")
        if copy:
            text = copy.read_text(encoding="utf-8-sig")
            matches = list(re.finditer(r"^【(YouTube 標題|說明欄|標記 Tags|置頂留言)】\s*$", text, re.M))
            sections = {}
            for n, match in enumerate(matches):
                heading = match.group(1)
                if heading in sections:
                    errors.append(f"{label}: duplicate copy section {heading}")
                sections[heading] = text[match.end():matches[n+1].start() if n+1 < len(matches) else len(text)].strip()
            title, description = sections.get(HEADINGS[0], ""), sections.get(HEADINGS[1], "")
            if not title or len(title) > 100 or "<" in title or ">" in title:
                errors.append(f"{label}: title missing, over 100 characters, or contains angle brackets")
            # Conservative local length check; Studio remains authoritative.
            if not description or len(description) > 5000:
                errors.append(f"{label}: description missing or over 5000 characters")
            if len(sections.get(HEADINGS[2], "")) > 500:
                errors.append(f"{label}: tags over 500 characters; trim and verify in Studio")
            permitted = description.replace("{{LONG_VIDEO_URL}}", "") if item.get("kind") == "short" else description
            if re.search(r"\{\{.*?\}\}|待填|【(?:YouTube|長片|完整片)連結】", permitted):
                errors.append(f"{label}: unresolved placeholder in description")
            if "{{LONG_VIDEO_URL}}" in description:
                warnings.append(f"{label}: resolve LONG_VIDEO_URL after publishing long video, before publishing this Short")
            report["title"] = title
        if item.get("thumbnail"):
            file_path(item["thumbnail"], f"{label}.thumbnail")
        elif item.get("kind") == "long":
            warnings.append(f"{label}: no custom thumbnail supplied")
        subtitles = item.get("subtitles", [])
        if not isinstance(subtitles, list) or any(not isinstance(s, dict) for s in subtitles):
            errors.append(f"{label}: subtitles must be an array of objects")
        else:
            for s in subtitles:
                file_path(s.get("path"), f"{label}.subtitle")
                if not isinstance(s.get("language"), str) or not s["language"].strip():
                    errors.append(f"{label}: subtitle language missing")
            if not subtitles:
                warnings.append(f"{label}: no subtitle files supplied; check delivery package")
        reports.append(report)
    return {"ok": not errors, "errors": errors, "warnings": warnings,
            "items": reports, "requires_media_and_studio_verification": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        result = inspect(args.manifest)
    except (OSError, ValueError, TypeError) as exc:
        result = {"ok": False, "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
