#!/usr/bin/env python3
"""Check sizes of Codex/Images 2.6 outputs and write small phone previews (needs Pillow).

Usage: python inspect_images.py <folder> [<folder> ...]
Checks thumbnail_*.png/jpg and 縮圖.jpg against 16:9 or 9:16 (decided by orientation),
shorts_cover* against 1080x1920, and 臉書分享圖_<W>x<H>.png against the size in its name.
"""
from pathlib import Path
import re
import sys
try:
    from PIL import Image
except ImportError:
    print("Pillow not installed: pip install Pillow to enable image checks")
    sys.exit(2)

IMAGE_EXT = {'.png', '.jpg', '.jpeg'}
SKIP_SUFFIX = ('_mobile', '_mobile_preview')

def expected_size(path, w, h):
    name = path.stem
    m = re.search(r'臉書分享圖_(\d+)x(\d+)', name)
    if m:
        return int(m.group(1)), int(m.group(2))
    if name.startswith('shorts_cover'):
        return 1080, 1920
    if name.startswith('thumbnail_') or name == '縮圖':
        return (1280, 720) if w >= h else (1080, 1920)
    return None

def collect(folder):
    for path in sorted(folder.rglob('*')):
        if path.is_file() and path.suffix.lower() in IMAGE_EXT and not path.stem.endswith(SKIP_SUFFIX):
            yield path

if len(sys.argv) < 2:
    print(__doc__.strip())
    sys.exit(2)
issues = []
checked = 0
for arg in sys.argv[1:]:
    for file in collect(Path(arg)):
        with Image.open(file) as im:
            w, h = im.size
            spec = expected_size(file, w, h)
            if spec is None:
                continue
            checked += 1
            ew, eh = spec
            print(f"{file}: {w}x{h} (expected {ew}x{eh}, {file.stat().st_size/1024/1024:.2f}MB)")
            if (w, h) != (ew, eh):
                issues.append(f"{file.name}: {w}x{h}, expected {ew}x{eh}")
            if file.stem == '縮圖' and im.format != 'JPEG':
                issues.append(f"{file.name}: not a real JPEG ({im.format})")
            preview_w = 160 if w >= h else 120
            im.convert('RGB').resize((preview_w, round(preview_w * h / w))).save(
                file.with_name(file.stem + '_mobile_preview.jpg'), quality=90)
if not checked:
    print("No generated thumbnail, Shorts cover or Facebook image found. Manifest remains planned.")
    sys.exit(1)
if issues:
    print("FAIL:", *issues, sep='\n- ')
    sys.exit(1)
print(f"PASS: {checked} image(s) inspected; mobile previews written (visual approval still required)")
