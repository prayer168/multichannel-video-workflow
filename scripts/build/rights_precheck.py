"""素材權利自動預審（2.42.0）：把 rights_audit.csv 裡待審（HOLD）的素材分成三級，只把「人工看」那一級交給使用者。

用法：
  python rights_precheck.py --audit output/rights_audit.csv --sources assets/licensed/sources.json \
      --licensed assets/licensed --report 權利預審報告.md [--apply]

每一項自動做的事：
  1. 檔案指紋：重算 assets/licensed/<檔> 的 SHA-256，和 sources.json 登記值比對（防拿錯檔、檔案被換）。
  2. 授權重查：Wikimedia Commons 用 API 重抓授權、作者、說明；images.nasa.gov 用 NASA API 確認條目存在並讀說明。
  3. 旗標：說明／標題／用途中出現人物（太空人、人潮、肖像…）、標誌（logo、標誌、贊助、船身塗裝…）、
     第三方（NASA 說明裡的 Credit:／©）；非政府作者卻標公有領域；授權與登記不符；檔案指紋不符。
     有 OpenCV（cv2）時另做人臉偵測（找到正臉就加旗標）；沒有就只靠文字旗標，報告會註明。
分級：
  T0 免審：自有原創（ORIGINAL）；美國聯邦機構（NASA、NOAA、USGS…）公有領域且無旗標。
  T1 自動通過：CC0／CC BY 授權已在原頁重查相符、CREDITS.md 有署名；年代久遠（1900 年前）的公有領域作品；無旗標。
  T2 人工看：有任一旗標、查不到、或授權有疑義。
--apply：T0／T1 改為 decision=APPROVED、reviewer=「自動預審（分級規則 v1，使用者授權）」、寫入日期與理由；
  T2 保持 HOLD，notes 前面加「[自動預審] 需人工：…」。執行前自動備份 CSV（.bak_日期）。
規則依據：references/rights-tiered-review.md（2026-11-25 使用者同意以分級預審取代逐項人工審查）。
"""
import argparse, csv, hashlib, io, json, os, re, shutil, time, urllib.error, urllib.parse, urllib.request

UA = {'User-Agent': 'NemoEduVideo/1.0 (educational research)'}
FED_HOSTS = ('images.nasa.gov', 'science.nasa.gov', 'www.nasa.gov', 'nasa.gov', 'svs.gsfc.nasa.gov', 'noaa.gov', 'oceanexplorer.noaa.gov', 'usgs.gov')
FED_NAMES = re.compile(r'\bNASA\b|NOAA|National Oceanic|USGS|Geological Survey|NASA Goddard|Scientific Visualization Studio|U\.S\. (Navy|Fish)', re.I)
# 只抓「畫面裡有人」的字眼；「太空人拍攝」「組員拍攝」是拍攝者，不算
PEOPLE = re.compile(r'portrait|crowd|poses|smiles|selfie|人潮|肖像|路人|艙內工作|艙內生活', re.I)
LOGO = re.compile(r'logo|insignia|sponsor|trademark|標誌|贊助|商標|NOAA ship|NOAAS ', re.I)
# 第三方：說明裡出現版權符號，或署名含非 NASA 的機構／商業公司（NASA/Roscosmos 這類合作署名不算）
THIRD = re.compile(r'©|copyright|Credit:[^.]*\b(ESA|JAXA|CSA|SpaceX|Boeing|Getty|Reuters|AP Photo|AFP)\b', re.I)
DATA_PD = ('naturalearthdata.com',)   # 公有領域資料集白名單
OLD_YEAR = re.compile(r'\b1[5-8]\d\d\b')


def get(url):
    for wait in (0, 5, 15, 40):  # Commons 限流（429）時退避重試
        time.sleep(wait)
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40))
        except urllib.error.HTTPError as e:
            if e.code != 429 or wait == 40:
                raise


def commons(title):
    q = urllib.parse.urlencode({'action': 'query', 'prop': 'imageinfo', 'iiprop': 'extmetadata', 'format': 'json', 'titles': title})
    p = list(get('https://commons.wikimedia.org/w/api.php?' + q)['query']['pages'].values())[0]
    if 'imageinfo' not in p:
        return None
    m = p['imageinfo'][0]['extmetadata']
    g = lambda k: re.sub(r'<[^>]+>', '', m.get(k, {}).get('value', '') or '').strip()
    return {'license': g('LicenseShortName'), 'author': g('Artist'), 'credit': g('Credit'), 'desc': g('ImageDescription')}


def nasa(nid):
    items = get('https://images-api.nasa.gov/search?nasa_id=' + urllib.parse.quote(nid))['collection']['items']
    if not items:
        return None
    d = items[0]['data'][0]
    return {'license': 'Public domain (NASA media guidelines)', 'author': d.get('photographer') or d.get('center') or 'NASA', 'credit': d.get('center', ''), 'desc': d.get('description', '')}


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def faces(path):
    try:
        import cv2
        cv2.CascadeClassifier  # OpenCV 5 移除了這個；需 opencv-python-headless<5
    except (ImportError, AttributeError):
        return None
    import numpy as np
    img = cv2.imdecode(np.fromfile(path, np.uint8), cv2.IMREAD_COLOR)  # imread 讀不了中文路徑
    if img is not None and max(img.shape[:2]) > 2400:
        k = 2400 / max(img.shape[:2]); img = cv2.resize(img, None, fx=k, fy=k)
    if img is None:
        return None
    casc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY); s = max(48, int(0.04 * min(g.shape)))  # 門檻依《尼莫點》實測：太鬆會把太空站、矽藻當成臉
    found = casc.detectMultiScale(g, 1.1, 10, minSize=(s, s))
    return len(found)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--audit', required=True); ap.add_argument('--sources', required=True); ap.add_argument('--licensed', required=True)
    ap.add_argument('--report', required=True); ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()
    src = {s['file']: s for s in json.load(open(a.sources, encoding='utf-8'))}
    credits = open(os.path.join(a.licensed, 'CREDITS.md'), encoding='utf-8').read() if os.path.exists(os.path.join(a.licensed, 'CREDITS.md')) else ''
    raw = open(a.audit, encoding='utf-8-sig').read()
    rows = list(csv.DictReader(io.StringIO(raw)))
    fields = list(rows[0].keys())
    today = time.strftime('%Y-%m-%d')
    results, face_note = [], False
    for r in rows:
        if r['decision'] != 'HOLD':
            continue
        flags, why = [], []
        m = re.search(r'assets/licensed/(\S+) \(sha256 ([0-9a-f]+)', r['asset_url'])
        rec = src.get(m.group(1)) if m else None
        local = os.path.join(a.licensed, m.group(1)) if m else None
        if m:
            if not os.path.exists(local):
                flags.append('找不到原檔')
            else:
                h = sha256(local)
                if rec and rec.get('sha256') and h != rec['sha256']:
                    flags.append('檔案指紋與登記不符')
                elif not h.startswith(m.group(2)):
                    flags.append('檔案指紋與審查表不符')
                else:
                    why.append('檔案指紋相符')
        url = r['source_url']; host = urllib.parse.urlparse(url).netloc.lower()
        info = None
        try:
            if 'commons.wikimedia.org/wiki/' in url:
                info = commons(urllib.parse.unquote(url.split('/wiki/', 1)[1]).replace('_', ' '))
            elif 'images.nasa.gov/details/' in url:
                info = nasa(url.rsplit('/', 1)[1])
            time.sleep(1.5)
        except Exception as e:  # 網路問題：不自動通過
            flags.append(f'授權重查失敗（{type(e).__name__}）')
        lic = (info or {}).get('license') or r['license_terms']
        author = ' '.join(filter(None, [(info or {}).get('author', ''), (info or {}).get('credit', ''), r['creator']]))
        text = ' '.join([(info or {}).get('desc', ''), r['notes'], r['shot_id'], rec.get('title', '') if rec else '', rec.get('used_for', '') if rec else ''])
        if info is None and ('commons.wikimedia.org' in url or 'images.nasa.gov' in url):
            flags.append('原頁查不到這個檔案')
        elif info:
            why.append(f'原頁授權：{lic}')
            reg = (rec or {}).get('license', r['license_terms'])
            norm = lambda s: re.sub(r'[^a-z0-9.]', '', s.lower())
            if reg and not (norm(lic)[:8] in norm(reg) or norm(reg)[:8] in norm(lic) or ('public domain' in lic.lower() and 'public domain' in reg.lower())):
                flags.append(f'授權與登記不符（原頁 {lic}／登記 {reg}）')
        old = bool(OLD_YEAR.search(text + ' ' + author))
        if PEOPLE.search(text) and not old:   # 1900 年前的歷史人物肖像不涉肖像權
            flags.append('畫面可能有可辨識人物')
        if LOGO.search(text):
            flags.append('畫面可能有標誌或商標')
        if info and 'images.nasa.gov' in url and THIRD.search(info.get('desc', '')):
            flags.append('NASA 說明提到第三方版權')
        federal = host.endswith(FED_HOSTS) or bool(FED_NAMES.search(author))
        # 作者不是政府、只是放在政府圖庫（例如 NOAA Corps Collection 收錄的大學教授照片）：要人工確認公有領域理由
        artist = (info or {}).get('author', '') or r['creator']
        if info and 'commons' in url and not FED_NAMES.search(artist) and FED_NAMES.search((info or {}).get('credit', '')):
            flags.append('作者非政府人員、由政府圖庫收錄，需確認公有領域理由')
        pd = 'public domain' in lic.lower() or '公有領域' in lic or '不受著作權保護' in lic
        ai = r['asset_id'].startswith('CODEX') or 'AI generated' in r['media_type']
        data_pd = host.endswith(DATA_PD)
        cc = re.search(r'CC0|CC BY(?!-SA| SA)', lic)
        if pd and not federal and not old and not ai and not data_pd:
            flags.append('非政府作者標公有領域，需確認理由')
        if cc and 'BY' in lic and not ai and r['creator'].split('（')[0].split(',')[0][:12] not in credits:
            flags.append('CC BY 署名未見於 CREDITS.md')
        if m and local and os.path.exists(local) and local.lower().endswith(('.jpg', '.jpeg', '.png', '.tif', '.tiff')):
            n = faces(local)
            if n is None:
                face_note = True
            elif n and not old:   # 1900 年前的歷史人物不涉肖像權
                flags.append(f'偵測到 {n} 張正臉')
        if ai:
            flags.append('AI 生成圖：確認服務條款允許商業使用')
        if not m and not federal and not info and not ai and not data_pd:
            flags.append('非逐檔素材或無原檔，需人工確認')
        if data_pd:
            why.append('公有領域資料集白名單')
        if r['asset_id'] == 'NASA_MIR_MEDIA' or '未逐檔' in r['license_terms']:
            flags.append('總括紀錄，已被逐檔紀錄取代時改為 WITHDRAWN')
        tier = 'T2' if flags else ('T0' if federal and pd else 'T1' if (cc or (pd and old) or data_pd) else 'T2')
        if tier == 'T2' and not flags:
            flags.append('授權類型無法自動判定')
        results.append((r, tier, flags, why))
        if a.apply:
            if tier in ('T0', 'T1'):
                r.update(decision='APPROVED', reviewer='自動預審（分級規則 v1，使用者授權）', verification_date=today,
                         notes=f'[自動預審 {tier}] ' + '；'.join(why) + '｜' + r['notes'])
            else:
                r['notes'] = '[自動預審] 需人工：' + '；'.join(flags) + '｜' + re.sub(r'^\[自動預審\] 需人工：[^｜]*｜', '', r['notes'])
    if a.apply:
        shutil.copy(a.audit, a.audit + '.bak_' + time.strftime('%Y%m%d_%H%M%S'))
        buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=fields, lineterminator='\n'); w.writeheader(); w.writerows(rows)
        open(a.audit, 'w', encoding='utf-8-sig', newline='').write(buf.getvalue())
    cnt = {t: sum(1 for x in results if x[1] == t) for t in ('T0', 'T1', 'T2')}
    out = [f'# 權利自動預審報告（{today}）', '',
           f'待審 {len(results)} 項：T0 免審 {cnt["T0"]}、T1 自動通過 {cnt["T1"]}、**T2 需人工 {cnt["T2"]}**。' + ('已寫回審查表（--apply）。' if a.apply else '未寫回審查表（試跑）。'),
           '人臉偵測：' + ('未安裝 OpenCV，只依文字旗標判斷人物。' if face_note else '已用 OpenCV 檢查照片。'), '',
           '## T2 需人工', '', '| 素材 | 用在 | 原因 |', '|---|---|---|']
    out += [f'| {r["asset_id"]} | {r["shot_id"]} | {"；".join(f)} |' for r, t, f, _ in results if t == 'T2']
    out += ['', '## T0／T1 自動通過', '', '| 素材 | 級別 | 依據 |', '|---|---|---|']
    out += [f'| {r["asset_id"]} | {t} | {"；".join(w)} |' for r, t, f, w in results if t != 'T2']
    open(a.report, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print(f'T0 {cnt["T0"]}／T1 {cnt["T1"]}／T2 {cnt["T2"]} → {a.report}')


if __name__ == '__main__':
    main()
