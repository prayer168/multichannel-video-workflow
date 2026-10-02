"""Create original vector-based channel drafts; no external imagery or music.

Requires Pillow, ffmpeg and Microsoft JhengHei (override --font).
Writes a new output directory only, never overwrites existing assets.
"""
import argparse
from array import array
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import wave

from PIL import Image, ImageDraw, ImageFont

W, H, FPS, SR = 960, 540, 30, 48000
AI = {'bg': '#101626', 'fg': '#F5F8FF', 'accent': '#58E0CF', 'muted': '#A5B2CB'}
SCI = {'bg': '#091D38', 'fg': '#FFFFFF', 'accent': '#FFD166', 'muted': '#BED6DD'}


def text(d, xy, value, size, color, font, anchor='mm'):
    d.text(xy, value, font=ImageFont.truetype(str(font), size), fill=color, anchor=anchor)


def lens(d, x, y, radius, color, progress=1):
    d.ellipse((x-radius, y-radius, x+radius, y+radius), outline=color, width=5)
    r = radius * .55
    d.ellipse((x-r, y-r, x+r, y+r), outline=color, width=3)
    d.arc((x-radius*1.35, y-radius*.72, x+radius*1.35, y+radius*.72),
          195, 195 + 300 * progress, fill=color, width=4)
    d.line((x+radius*.7, y-radius*.7, x+radius*1.13, y-radius*1.13), fill=color, width=4)
    for i in range(3):
        px = x + radius * 1.13 + i * 12
        py = y - radius * 1.13
        d.ellipse((px-3, py-3, px+3, py+3), fill=color)


def leaf(d, x, y, color):
    # Original leaf/observation motif; does not replace the approved paw logo.
    d.ellipse((x-33, y-64, x+33, y+24), outline=color, width=4)
    d.line((x, y+45, x, y-42), fill=color, width=4)
    d.line((x, y-5, x-19, y-24), fill=color, width=3)
    d.line((x, y-22, x+19, y-40), fill=color, width=3)


def frame(channel, kind, t, duration, font):
    c = AI if channel == 'ai-watch' else SCI
    im = Image.new('RGB', (W, H), c['bg'])
    d = ImageDraw.Draw(im)
    d.line((64, 64, 200, 64), fill=c['accent'], width=4)
    d.line((760, 476, 896, 476), fill=c['accent'], width=4)
    if channel == 'ai-watch':
        lens(d, 480, 166, 47, c['accent'], min(1, t/.9))
        title, subtitle = 'AI 觀測站', 'AI WATCH'
        message = '看懂 AI 變化，親手做出能用的工具' if kind == 'intro' else '把概念變成作品，下一次一起實測'
        cta = '留言分享：你想測試哪個工具或專案？'
    else:
        leaf(d, 480, 168, c['accent'])
        title, subtitle = '黑熊老師的自然教室', '觀察 · 提問 · 探究'
        message = '把今天的發現，帶回生活裡'
        cta = '留言分享：你觀察到了什麼？'
    shift = int(12 * max(0, 1-t/.8))
    text(d, (480, 274+shift), title, 44 if channel == 'ai-watch' else 37, c['fg'], font)
    text(d, (480, 322), subtitle, 19, c['accent'], font)
    text(d, (480, 373), message, 24, c['fg'], font)
    if kind == 'outro':
        text(d, (480, 420), cta, 19, c['muted'], font)
    text(d, (896, 505), 'DRAFT / 待核定', 13, c['muted'], font, 'rm')
    fade = min(1, t/.25, (duration-t)/.4)
    if fade < 1:
        im = Image.blend(Image.new('RGB', im.size, c['bg']), im, max(0, fade))
    return im


def sound(path, duration, notes=None, bgm=False):
    data = array('h')
    notes = notes or []
    for i in range(round(duration*SR)):
        t = i/SR
        val = 0.
        if bgm:
            # Quiet original two-note ambient bed with a seamless 16-second period.
            env = .06 * (.5-.5*math.cos(2*math.pi*t/duration))
            val = env * (.65*math.sin(2*math.pi*220*t) + .35*math.sin(2*math.pi*330*t))
        else:
            for at, hz in notes:
                age = t-at
                if 0 <= age < .85:
                    env = min(1, age/.025) * math.exp(-age*5) * .11
                    val += env*(math.sin(2*math.pi*hz*age)+.15*math.sin(2*math.pi*hz*2*age))
        data.append(round(max(-1, min(1, val))*32767))
    if sys.byteorder != 'little':
        data.byteswap()
    with wave.open(str(path), 'wb') as out:
        out.setparams((1, 2, SR, 0, 'NONE', 'not compressed'))
        out.writeframes(data.tobytes())


def movie(directory, channel, kind, duration, font):
    audio = directory / f'{kind}_audio_draft.wav'
    frequencies = [440, 660, 880] if channel == 'ai-watch' else [392, 494, 587]
    sound(audio, duration, list(zip([.35, .62, .9], frequencies)))
    output = directory / f'{kind}_draft.mp4'
    cmd = ['ffmpeg', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', str(audio),
           '-vf', 'scale=1920:1080:flags=lanczos', '-c:v', 'libx264', '-preset', 'fast',
           '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
           '-shortest', '-movflags', '+faststart', str(output)]
    with subprocess.Popen(cmd, stdin=subprocess.PIPE) as proc:
        try:
            for n in range(round(duration*FPS)):
                proc.stdin.write(frame(channel, kind, n/FPS, duration, font).tobytes())
        finally:
            proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError(f'ffmpeg failed: {output}')
    still = frame(channel, kind, 2, duration, font).resize((1920, 1080), Image.Resampling.LANCZOS)
    still.save(directory / f'{kind}_still_draft.png')
    print(output, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--font', type=Path, default=Path('C:/Windows/Fonts/msjhbd.ttc'))
    args = ap.parse_args()
    if args.out.exists():
        ap.error('Output directory already exists; choose a new versioned path.')
    if not shutil.which('ffmpeg') or not args.font.is_file():
        ap.error('ffmpeg and a valid font are required.')
    args.out.mkdir(parents=True)
    ai, sci = args.out/'ai-watch', args.out/'blackbear-science'
    ai.mkdir(); sci.mkdir()
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><g fill="none" stroke="#58E0CF" stroke-width="18"><circle cx="240" cy="260" r="130"/><circle cx="240" cy="260" r="70"/><path d="M64 276C40 150 449 133 413 287M332 168l76-76"/></g><g fill="#58E0CF"><circle cx="408" cy="92" r="9"/><circle cx="445" cy="92" r="9"/><circle cx="482" cy="92" r="9"/></g></svg>'''
    (ai/'logo_draft.svg').write_text(svg, encoding='utf-8')
    logo = Image.new('RGBA', (512, 512))
    lens(ImageDraw.Draw(logo), 235, 270, 130, AI['accent'])
    logo.save(ai/'logo_draft.png')
    wm = Image.new('RGBA', (1920, 1080))
    d = ImageDraw.Draw(wm)
    lens(d, 1694, 957, 25, AI['accent'])
    text(d, (1750, 945), 'AI WATCH', 25, AI['fg'], args.font, 'lm')
    text(d, (1750, 979), 'DRAFT', 14, AI['muted'], args.font, 'lm')
    wm.save(ai/'watermark_draft.png')
    movie(ai, 'ai-watch', 'intro', 4, args.font)
    movie(ai, 'ai-watch', 'outro', 6, args.font)
    movie(sci, 'blackbear-science', 'outro', 6, args.font)
    sound(ai/'bgm_draft.wav', 16, bgm=True)
    manifest = {'status': 'draft_pending_approval', 'created': '2026-10-02',
                'provenance': 'Original code-native graphics and synthesized audio; no third-party assets',
                'ai-watch': {'intro': 'ai-watch/intro_draft.mp4', 'intro_len': 4,
                             'intro_audio': 'ai-watch/intro_audio_draft.wav',
                             'watermark': 'ai-watch/watermark_draft.png', 'bgm': 'ai-watch/bgm_draft.wav',
                             'outro_postproduction': 'ai-watch/outro_draft.mp4'},
                'blackbear-science': {'outro_postproduction': 'blackbear-science/outro_draft.mp4',
                                     'intro': 'Existing approved intro remains external; file not confirmed'}}
    (args.out/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    sheet = Image.new('RGB', (960, 900), '#EFF2F6')
    for i, (ch, kind, seconds) in enumerate([('ai-watch','intro',4), ('ai-watch','outro',6), ('blackbear-science','outro',6)]):
        panel = frame(ch, kind, 2, seconds, args.font).resize((480, 270))
        sheet.paste(panel, (240, 20+i*295))
    sheet.save(args.out/'review_draft.png')


if __name__ == '__main__':
    main()
