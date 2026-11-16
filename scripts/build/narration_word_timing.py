"""旁白逐字時間（2.30.0）：已知旁白文字，找出每個字在配音裡的開口時間，讓畫面落在「關鍵詞」而不是句首。

用法：
  python narration_word_timing.py --audio 旁白.wav --script 旁白.txt --out words.json
  python narration_word_timing.py --audio 旁白.wav --script 旁白.txt --out words.json --offset 4.0   # 旁白前有 4 秒片頭
  python narration_word_timing.py --whisper-json 既有.json --script 旁白.txt --out words.json      # 已跑過 whisper -ojf
  python narration_word_timing.py --words words.json --cue S03@沉積物 --cue S05@一層一層#2          # 查落點秒數

旁白.txt：一句一行，行首可寫句 ID（`S03 這時候只能叫沉積物。`）；沒寫 ID 的行自動編 S01、S02…；空行與 # 開頭略過。
文字必須是定稿旁白（和配音一字不差），不是 whisper 聽出來的字。

做法：whisper.cpp（medium，`-ojf` 逐 token 時間）先聽一次，再用序列比對把聽到的字對回旁白文字；
對不上的字（同音錯字、漏聽）用前後對上的字線性內插，並在報告列出來。不需要另外下載模型：
預設用 %USERPROFILE%\\AI-Video-Tools\\motion-explainer\\whisper\\cpp 的 main.exe 與 ggml-medium.bin。
精度約 0.1–0.2 秒（token 層級）；需要更準時，改用 mv-director 的 Qwen3 強制對齊（見
motion-explainer-workflow/references/narration-sync-components.md「逐字時間」）。

輸出 words.json：
  {"offset": 秒, "engine": "...", "match_ratio": 0.97,
   "sentences": [{"id": "S03", "text": "...", "start": 秒, "end": 秒,
                  "chars": [{"c": "沉", "t": 秒, "end": 秒, "matched": true}, ...]}]}
所有秒數已加上 --offset（＝成片時間軸）。落點寫法：`S03`（句首）、`S03@沉積物`（該詞第一個字開口）、
`S03@一層#2`（同句第二次出現）、`S03$`（句尾）。動畫頁面用同一套寫法查時間（template/narration-sync-components）。
"""
import argparse, codecs, difflib, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
WHISPER_DIR = Path(os.path.expanduser('~')) / 'AI-Video-Tools' / 'motion-explainer' / 'whisper' / 'cpp'
KEEP = re.compile(r'[一-鿿㐀-䶿0-9A-Za-z]')     # 只對齊文字和數字，標點空白跳過
ANCHOR = re.compile(r'^(?P<id>[^@$#]+?)(?:(?P<end>\$)|@(?P<word>[^#]+)(?:#(?P<n>\d+))?)?$')


def read_script(path):
    rows, n = [], 0
    for line in Path(path).read_text(encoding='utf-8-sig').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        m = re.match(r'^([A-Za-z]+\d+[a-z]?)[\s\t｜|]+(.+)$', line)
        n += 1
        rows.append({'id': m.group(1), 'text': m.group(2).strip()} if m else {'id': f'S{n:02d}', 'text': line})
    if not rows:
        sys.exit(f'{path} 沒有旁白文字')
    return rows


def run_whisper(audio, rows, wdir):
    exe, model = wdir / 'main.exe', wdir / 'ggml-medium.bin'
    for p in (exe, model):
        if not p.exists():
            sys.exit(f'找不到 {p}；用 --whisper-dir 指定 whisper.cpp 資料夾，或先自行跑 whisper -ojf 再用 --whisper-json')
    ff = shutil.which('ffmpeg') or sys.exit('找不到 ffmpeg')
    tmp = Path(tempfile.mkdtemp(prefix='wordtiming_'))
    wav = tmp / 'a16k.wav'
    subprocess.run([ff, '-y', '-v', 'error', '-i', str(audio), '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', str(wav)], check=True)
    prompt = ''.join(r['text'] for r in rows)[:200]      # 用定稿文字當提示，減少同音錯字
    cmd = [str(exe), '-m', str(model), '-l', 'zh', '-ojf', '-of', str(tmp / 'w'), '-f', str(wav), '--prompt', prompt]
    print('whisper.cpp 辨識中（medium，CPU 約為音長的 1–2 倍）…', flush=True)
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0 or not (tmp / 'w.json').exists():
        sys.exit('whisper.cpp 失敗：\n' + r.stderr.decode('utf-8', 'replace')[-1500:])
    return tmp / 'w.json'


def asr_chars(wjson):
    """whisper.cpp 的 JSON 會把多位元組字切在 token 中間，先當 latin-1 讀，再逐 token 還原成 UTF-8。"""
    data = json.loads(Path(wjson).read_bytes().decode('latin-1'))
    out = []
    for seg in data['transcription']:
        dec = codecs.getincrementaldecoder('utf-8')('replace')
        for tok in seg.get('tokens', []):
            raw = tok['text'].encode('latin-1')
            if raw.startswith(b'[_'):
                continue
            cs = [c for c in dec.decode(raw) if KEEP.match(c)]
            a, b = tok['offsets']['from'] / 1000, tok['offsets']['to'] / 1000
            for i, c in enumerate(cs):
                out.append((c, a + (b - a) * i / len(cs), a + (b - a) * (i + 1) / len(cs)))
    if not out:
        sys.exit('whisper 結果沒有可用的 token 時間（要用 -ojf 輸出）')
    return out


def align(rows, chars, offset):
    scr, idx = [], []
    for r, row in enumerate(rows):
        for j, c in enumerate(row['text']):
            if KEEP.match(c):
                scr.append(c); idx.append((r, j))
    asr = [c for c, _, _ in chars]
    sm = difflib.SequenceMatcher(None, scr, asr, autojunk=False)
    hit, diffs = {}, []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1):
                hit[i1 + k] = j1 + k
        else:
            diffs.append((''.join(scr[i1:i2]), ''.join(asr[j1:j2])))
    keys = sorted(hit)
    if not keys:
        sys.exit('旁白文字和辨識結果完全對不上：確認音檔與旁白是同一版')

    def at(i):                                   # 對上的字直接取；對不上的用前後對上的字內插
        if i in hit:
            return chars[hit[i]][1], chars[hit[i]][2], True
        lo = max((k for k in keys if k < i), default=None)
        hi = min((k for k in keys if k > i), default=None)
        if lo is None:
            t = chars[hit[hi]][1]; return t, t, False
        if hi is None:
            t = chars[hit[lo]][2]; return t, t, False
        a, b = chars[hit[lo]][2], chars[hit[hi]][1]
        t = a + (b - a) * (i - lo) / (hi - lo)
        return t, t, False

    sents = [dict(id=row['id'], text=row['text'], chars=[]) for row in rows]
    for i, (r, j) in enumerate(idx):
        t0, t1, ok = at(i)
        sents[r]['chars'].append({'c': scr[i], 'j': j, 't': round(t0 + offset, 3), 'end': round(t1 + offset, 3), 'matched': ok})
    for s in sents:
        s['start'] = s['chars'][0]['t'] if s['chars'] else None
        s['end'] = s['chars'][-1]['end'] if s['chars'] else None
    return sents, round(sm.ratio(), 3), diffs


def resolve(words, anchor):
    """`S03`／`S03$`／`S03@詞`／`S03@詞#2` → 秒數（成片時間軸）。找不到就丟 KeyError。"""
    m = ANCHOR.match(anchor.strip())
    if not m:
        raise KeyError(f'看不懂的落點：{anchor}')
    s = next((x for x in words['sentences'] if x['id'] == m.group('id')), None)
    if s is None:
        raise KeyError(f'沒有句子 {m.group("id")}')
    if m.group('end'):
        return s['end']
    if not m.group('word'):
        return s['start']
    plain = ''.join(c['c'] for c in s['chars'])
    key = ''.join(c for c in m.group('word') if KEEP.match(c))
    n, k = int(m.group('n') or 1), -1
    for _ in range(n):
        k = plain.find(key, k + 1)
        if k < 0:
            raise KeyError(f'{s["id"]} 裡沒有第 {n} 個「{key}」：{s["text"]}')
    return s['chars'][k]['t']


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--audio'); ap.add_argument('--script'); ap.add_argument('--out')
    ap.add_argument('--whisper-json', help='已有的 whisper.cpp -ojf 結果，不再重跑')
    ap.add_argument('--whisper-dir', default=str(WHISPER_DIR))
    ap.add_argument('--offset', type=float, default=0.0, help='旁白在成片裡的起點秒數（例如片頭長度）')
    ap.add_argument('--words', help='查落點用：既有的 words.json')
    ap.add_argument('--cue', action='append', default=[], help='查落點，例如 S03@沉積物；可重複')
    a = ap.parse_args()

    if a.words:
        words = json.loads(Path(a.words).read_text(encoding='utf-8'))
    else:
        if not (a.script and a.out and (a.audio or a.whisper_json)):
            ap.error('要給 --script、--out，以及 --audio 或 --whisper-json')
        rows = read_script(a.script)
        wj = a.whisper_json or run_whisper(a.audio, rows, Path(a.whisper_dir))
        sents, ratio, diffs = align(rows, asr_chars(wj), a.offset)
        words = {'offset': a.offset, 'engine': 'whisper.cpp medium token timestamps + 定稿文字序列比對',
                 'audio': str(a.audio or ''), 'match_ratio': ratio, 'sentences': sents}
        Path(a.out).write_text(json.dumps(words, ensure_ascii=False, indent=1), encoding='utf-8')
        miss = sum(1 for s in sents for c in s['chars'] if not c['matched'])
        total = sum(len(s['chars']) for s in sents)
        print(f'寫好 {a.out}：{len(sents)} 句、{total} 字；比對率 {ratio}；內插 {miss} 字')
        for s in sents:
            bad = ''.join(c['c'] if not c['matched'] else '' for c in s['chars'])
            print(f'  {s["id"]} {s["start"]:7.2f}–{s["end"]:7.2f}  {s["text"]}' + (f'  ⚠ 內插：{bad}' if bad else ''))
        if diffs:
            print('辨識差異（旁白 → 聽到）：' + '；'.join(f'{x}→{y or "∅"}' for x, y in diffs[:30]))
        if ratio < 0.85:
            print('⚠ 比對率低於 0.85：確認音檔和旁白是同一版，或改用強制對齊')
    rc = 0
    for c in a.cue:
        try:
            print(f'{c}\t{resolve(words, c):.3f}')
        except KeyError as e:
            print(f'{c}\t✗ {e}'); rc = 1
    return rc


if __name__ == '__main__':
    sys.exit(main())
