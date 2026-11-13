#!/usr/bin/env python3
"""Inspect thumbnails' dimensions and make 160x90 previews if Pillow exists."""
from pathlib import Path
import sys
try:
    from PIL import Image
except ImportError:
    print("Pillow not installed: pip install Pillow to enable image checks")
    sys.exit(2)
if len(sys.argv)!=2:
    print("Usage: python inspect_images.py <output-directory>")
    sys.exit(2)
folder = Path(sys.argv[1])
images = sorted(
    path for path in folder.glob('thumbnail_*')
    if path.is_file()
    and path.suffix.lower() in {'.png', '.jpg', '.jpeg'}
    and path.stem != 'thumbnail_contact_sheet'
    and not path.stem.endswith(('_mobile', '_mobile_preview'))
)
if not images:
    print("No rendered thumbnail images found. Manifest remains planned.");sys.exit(1)
issues=[]
for file in images:
    with Image.open(file) as im:
        w,h=im.size
        print(f"{file.name}: {w}x{h} ({file.stat().st_size/1024/1024:.2f}MB)")
        if abs(w/h-16/9)>0.015: issues.append(f"{file.name}: ratio not 16:9")
        im.convert('RGB').resize((160,90)).save(file.with_name(file.stem+'_mobile_preview.jpg'),quality=90)
if issues:
    print("FAIL:",*issues,sep='\n- ');sys.exit(1)
print("PASS: dimensions inspected; mobile previews written (visual approval still required)")
