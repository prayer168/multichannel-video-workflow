#!/usr/bin/env python3
"""Package an explicit project manifest into a verified video handoff ZIP."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tempfile
import zipfile


def safe_path(raw):
    if not isinstance(raw, str) or not raw or '\\' in raw or ':' in raw:
        raise ValueError('path must be a relative POSIX path')
    p = PurePosixPath(raw)
    if p.is_absolute() or '..' in p.parts or '.' in p.parts:
        raise ValueError('unsafe relative path: ' + raw)
    for part in p.parts:
        lower = part.lower()
        if lower.startswith('.') or lower in {'node_modules', '__pycache__'}:
            raise ValueError('hidden or transient path rejected: ' + raw)
        if lower in {'credentials.json', 'auth.json', 'id_rsa', 'id_ed25519'} or lower.endswith(('.pem', '.key')):
            raise ValueError('credential path rejected: ' + raw)
    return p.as_posix()


def package(project, manifest, output):
    root = project.resolve(strict=True)
    data = json.loads(manifest.read_text(encoding='utf-8'))
    name = safe_path(data['bundle_name'])
    if '/' in name:
        raise ValueError('bundle_name must be one directory name')
    if output.exists():
        raise ValueError('output already exists; choose a new filename')
    files = data['files']
    if not isinstance(files, list) or not files:
        raise ValueError('files must be a nonempty list')
    ready, missing, seen = [], [], set()
    for entry in files:
        rel = safe_path(entry['path'])
        if rel.casefold() in seen or rel in {'BUNDLE_MANIFEST.json', 'MISSING_ASSETS.md'}:
            raise ValueError('duplicate or reserved path: ' + rel)
        seen.add(rel.casefold())
        state = entry.get('status', 'ready')
        if state not in {'ready', 'pending'}:
            raise ValueError('unknown status: ' + str(state))
        if not isinstance(entry.get('required', False), bool):
            raise ValueError('required must be boolean')
        src = root.joinpath(*PurePosixPath(rel).parts)
        if any(p.is_symlink() for p in [src, *src.parents] if p != root and p.is_relative_to(root)):
            raise ValueError('symlink rejected: ' + rel)
        resolved = src.resolve()
        if not resolved.is_relative_to(root) or resolved == output.resolve():
            raise ValueError('path outside project or output included: ' + rel)
        if state == 'pending' or not src.is_file():
            if state == 'ready' and entry.get('required', False):
                raise ValueError('required file missing: ' + rel)
            missing.append(dict(entry, path=rel, reason='pending' if state == 'pending' else 'missing'))
            continue
        ready.append((src, dict(entry, path=rel)))
    if not {'README.md', 'START_HERE.md'}.issubset({e['path'] for _, e in ready}):
        raise ValueError('README.md and START_HERE.md must be ready')
    output.parent.mkdir(parents=True, exist_ok=True)
    index = {'bundle_name': name, 'files': [], 'missing': missing}
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix='.zip', delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        with zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as z:
            for src, entry in ready:
                payload = src.read_bytes()
                z.writestr(name + '/' + entry['path'], payload)
                index['files'].append(dict(entry, bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest()))
            z.writestr(name + '/BUNDLE_MANIFEST.json', json.dumps(index, ensure_ascii=False, indent=2))
            lines = ['# 素材缺件清單', ''] + [f"- {e['path']}：{e.get('role', '素材')}（{e['reason']}）" for e in missing]
            if not missing:
                lines.append('清單內無缺件；仍需按影片驗收條件確認可用性。')
            z.writestr(name + '/MISSING_ASSETS.md', '\n'.join(lines) + '\n')
        with zipfile.ZipFile(tmp_path) as z:
            if z.testzip() is not None:
                raise ValueError('ZIP verification failed')
            for entry in index['files']:
                payload = z.read(name + '/' + entry['path'])
                if hashlib.sha256(payload).hexdigest() != entry['sha256']:
                    raise ValueError('hash mismatch: ' + entry['path'])
        tmp_path.replace(output)
    finally:
        tmp_path.unlink(missing_ok=True)
    return {'output': str(output), 'packed': len(ready), 'pending': len(missing), 'verified': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(package(args.project, args.manifest, args.out), ensure_ascii=False))
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(1, 'Packaging failed: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
