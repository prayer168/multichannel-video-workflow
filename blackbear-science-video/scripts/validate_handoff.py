#!/usr/bin/env python3
"""Basic structural QA for BlackBear handoff package (stdlib only)."""
import csv, json, sys
from pathlib import Path

def read_csv(path, required):
    if not path.exists():
        raise ValueError(f'missing file: {path}')
    with path.open(encoding='utf-8-sig', newline='') as f:
        r = csv.DictReader(f)
        if not r.fieldnames or not set(required).issubset(set(r.fieldnames)):
            raise ValueError(f'columns missing from {path}: {set(required)-set(r.fieldnames or [])}')
        return list(r)

def main(root):
    errors=[]; warnings=[]
    try:
        m=json.loads((root/'project_manifest.json').read_text(encoding='utf-8'))
        target=int(m['target_duration_ms'])
    except (OSError, ValueError, KeyError) as e:
        print('FAIL manifest:',e); return 2
    datasets={}
    specs={'shots.csv':['shot_id','start_ms','end_ms','duration_ms','claim_ids','source_ids','asset_ids','rights_status'],
           'research/claims.csv':['claim_id','source_ids','review_status'],
           'research/sources.csv':['source_id','url','verification_status'],
           'assets/asset_register.csv':['asset_id','rights_status']}
    for name,cols in specs.items():
        try: datasets[name]=read_csv(root/name,cols)
        except ValueError as e: errors.append(str(e)); datasets[name]=[]
    shots=datasets['shots.csv']; claims=datasets['research/claims.csv']; sources=datasets['research/sources.csv']; assets=datasets['assets/asset_register.csv']
    cids={x['claim_id'] for x in claims}; sids={x['source_id'] for x in sources}; aids={x['asset_id'] for x in assets}
    for name, ids in [('claims', [x['claim_id'] for x in claims]),('sources',[x['source_id'] for x in sources]),('assets',[x['asset_id'] for x in assets]),('shots',[x['shot_id'] for x in shots])]:
        if len(ids)!=len(set(ids)): errors.append(f'duplicate IDs: {name}')
    pos=0
    for idx,s in enumerate(shots,1):
        name=s['shot_id'] or f'row {idx}'
        try:
            start,end,dur=map(int,(s['start_ms'],s['end_ms'],s['duration_ms']))
            if start!=pos: errors.append(f'{name}: expected start {pos}, got {start}')
            if end<=start or end-start!=dur: errors.append(f'{name}: invalid duration')
            pos=end
        except ValueError: errors.append(f'{name}: invalid time integer')
        for column, known in [('claim_ids',cids),('source_ids',sids),('asset_ids',aids)]:
            for ident in filter(None,map(str.strip,s[column].split(';'))):
                if ident not in known: errors.append(f'{name}: unknown {column} {ident}')
        if s['rights_status'] in ('PENDING','BLOCKED',''):
            warnings.append(f'{name}: unresolved rights ({s["rights_status"] or "blank"})')
    if not shots: errors.append('no shots: incomplete package')
    if pos!=target: errors.append(f'timeline {pos} ms != target {target} ms')
    for c in claims:
        for ident in filter(None,map(str.strip,c['source_ids'].split(';'))):
            if ident not in sids: errors.append(f'{c["claim_id"]}: unknown source {ident}')
        if not c['source_ids'].strip() or c['review_status'] not in ('已驗證','CONFIRMED'):
            warnings.append(f'{c["claim_id"]}: science claim needs review')
    for a in assets:
        if a['rights_status'] not in ('CLEARED','ORIGINAL'):
            warnings.append(f'{a["asset_id"]}: asset rights unresolved')
    print('STRUCTURAL:', 'PASS' if not errors else 'FAIL')
    for e in errors: print('ERROR:', e)
    for w in warnings: print('WARNING:', w)
    print('This does not verify science truth, copyright permissions, or audiovisual quality.')
    return 1 if errors else (3 if warnings else 0)

if __name__=='__main__':
    sys.exit(main(Path(sys.argv[1]) if len(sys.argv)>1 else Path.cwd()))
