"""只產生 Gemini 整組原始配音（不跑 gemini_tts 內建的無提示 whisper 切句）。
用法：python tts_raw.py <voice_lines.json> <輸出資料夾> [--pace fast]
模型、聲音、Style、分組與 gemini_tts.py 完全相同；輸出 raw_<組>.wav 與 groups.json（每組含哪些句）。
之後每組用 narration_word_timing.py（有旁白提示）對齊，再用 resplit_voice.py 切成逐句檔。
2026-11-26：本機 whisper 過慢，gemini_tts 內建對齊 900 s 逾時（CH05），CH06 起改走此路。
"""
import hashlib, json, os, sys, time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gemini_tts as g  # noqa: E402


def main():
    lines_p, out = Path(sys.argv[1]), Path(sys.argv[2])
    pace = sys.argv[sys.argv.index('--pace') + 1] if '--pace' in sys.argv else 'normal'
    data = json.loads(lines_p.read_text(encoding='utf-8'))
    g.STYLE = g.style(data.get('terms') or 'YouTube', pace)
    out.mkdir(parents=True, exist_ok=True)
    blocks = [(f'e{k:03d}', [(lid, text, out / f'{lid}.wav')]) for k, (lid, text) in enumerate(data['lines'])]
    key = os.environ.get('GEMINI_API_KEY') or g.user_env('GEMINI_API_KEY')
    manifest, called = [], False
    for group in g.groups(blocks):
        text = g.transcript(group)
        gid = f"{group[0][0]}-{group[-1][0]}_{hashlib.md5((g.MODEL + g.VOICE + g.STYLE + text).encode()).hexdigest()[:8]}"
        raw = out / f'raw_{gid}.wav'
        if not raw.exists():
            if called:
                time.sleep(g.WAIT)
            print(f'Gemini 配音 {gid}（{len(text)} 字）…', flush=True)
            pcm, sr = g.request(text, key)
            called = True
            y = np.frombuffer(pcm[: len(pcm) // 2 * 2], np.int16).astype(np.float32) / 32768
            g.write_wav(raw, g.clean(y, sr), sr)
        y, sr = g.read_wav(raw)
        ids = [lid for _, cs in group for lid, _, _ in cs]
        manifest.append(dict(raw=raw.name, ids=ids, seconds=round(len(y) / sr, 2), chars=len(text)))
        print(f'  {raw.name}：{len(y) / sr:.2f} s，{ids[0]}–{ids[-1]}', flush=True)
    (out / 'groups.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
