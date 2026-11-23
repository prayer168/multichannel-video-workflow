#!/usr/bin/env python3
"""BlackBear Science Video V1.1 deterministic audit; standard library only."""
import argparse,csv,json,hashlib,re,sys
from pathlib import Path

def table(p):
 if not p.is_file():return [],['MISSING_TABLE:'+str(p)]
 try:
  with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f)),[]
 except (UnicodeError,csv.Error) as e:return [],['READ_ERROR:'+str(p)+':'+str(e)]
def links(s):return [x.strip() for x in (s or '').split(';') if x.strip()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def truth(s):return str(s or '').strip().lower() in ('true','yes','1','已完成','pass','passed')
def audit(project,gate='handoff'):
 E=[];W=[];detail=[]
 def issue(kind,code,msg,shot=''):
  (E if kind=='BLOCKER' else W).append(dict(code=code,message=msg,shot_id=shot))
 orig=project/'original'; lock=project/'reports/original_sha256.txt'; protected=0
 if not lock.exists():issue('BLOCKER','NO_ORIGINAL_LOCK','缺少原稿校驗基準 original_sha256.txt')
 else:
  for raw in lock.read_text(encoding='utf-8-sig').splitlines():
   parts=raw.split(maxsplit=1)
   if len(parts)!=2: issue('BLOCKER','INVALID_LOCK_LINE','無效鎖定列');continue
   expected,rel=parts; p=project/rel.strip(); protected+=1
   if not p.is_file():issue('BLOCKER','ORIGINAL_MISSING',rel)
   elif sha(p)!=expected:issue('BLOCKER','ORIGINAL_CHANGED',rel)
 for filename in ('shots.csv','research/claims.csv','research/sources.csv','assets/asset_register.csv','project_manifest.json'):
  if not (project/filename).is_file():issue('BLOCKER','REQUIRED_FILE_MISSING',filename)
 shots,err=table(project/'shots.csv'); claims,err2=table(project/'research/claims.csv'); sources,err3=table(project/'research/sources.csv'); assets,err4=table(project/'assets/asset_register.csv')
 for e in err+err2+err3+err4:issue('BLOCKER','TABLE_ERROR',e)
 cs={r.get('claim_id'):r for r in claims}; ss={r.get('source_id'):r for r in sources}; aa={r.get('asset_id'):r for r in assets}
 try:manifest=json.loads((project/'project_manifest.json').read_text(encoding='utf-8-sig'))
 except (FileNotFoundError,ValueError) as ex:manifest={};issue('BLOCKER','MANIFEST_INVALID',str(ex))
 prev=None; missing_prompt=0; missing_assets=0; rights_pending=0; claims_pending=0; unidentified_sources=0
 used_ids=set()
 for r in shots:
  sid=r.get('shot_id',''); start=r.get('start_ms','');end=r.get('end_ms','');dur=r.get('duration_ms','')
  problems=[]
  if not sid or sid in used_ids:issue('BLOCKER','INVALID_SHOT_ID','空 ID 或重複 ID',sid)
  used_ids.add(sid)
  try:
   a,b,d=map(int,(start,end,dur))
   if b<=a or d!=b-a:issue('BLOCKER','DURATION_MISMATCH',f'{start}/{end}/{dur}',sid)
   if prev is not None and a!=prev:issue('BLOCKER','TIMELINE_GAP_OVERLAP',f'預期 {prev}，實際 {a}',sid)
   prev=b
  except (TypeError,ValueError):issue('BLOCKER','INVALID_TIME','非整數毫秒時間碼',sid)
  for field in ('chapter','visual_description','visual_type'):
   if not r.get(field,'').strip():issue('BLOCKER','REQUIRED_SHOT_FIELD',field,sid)
  if not r.get('prompt_zh') or not r.get('prompt_en'):
   missing_prompt+=1; problems.append('PROMPT_INCOMPLETE')
  for cid in links(r.get('claim_ids')):
   if cid not in cs: issue('BLOCKER','CLAIM_ID_MISSING',cid,sid)
   else:
    c=cs[cid]
    if c.get('review_status') not in ('已驗證','VERIFIED','APPROVED') or c.get('evidence_level') in ('REVIEW_REQUIRED','TENTATIVE','UNKNOWN'):
     claims_pending+=1;problems.append('CLAIM_NOT_VERIFIED')
  for sid2 in links(r.get('source_ids')):
   if sid2 not in ss:issue('BLOCKER','SOURCE_ID_MISSING',sid2,sid)
   elif ss[sid2].get('verification_status','') not in ('CLAIM_LEVEL_VERIFIED','VERIFIED','APPROVED'):
    unidentified_sources+=1;problems.append('SOURCE_NOT_VERIFIED_AT_CLAIM_LEVEL')
  for aid in links(r.get('asset_ids')):
   if aid not in aa:issue('BLOCKER','ASSET_ID_MISSING',aid,sid);continue
   asset=aa[aid]; local=asset.get('local_path','').strip()
   if not local or not (project/local).is_file():missing_assets+=1;problems.append('ASSET_FILE_MISSING')
   rights=asset.get('rights_status','').strip().upper()
   if rights not in ('CLEARED','APPROVED') or not asset.get('license_evidence','').strip() or not asset.get('usage_scope','').strip():
    rights_pending+=1;problems.append('RIGHTS_NOT_CLEARED')
  detail.append({'shot_id':sid,'claim_ids':r.get('claim_ids',''),'source_ids':r.get('source_ids',''),'asset_ids':r.get('asset_ids',''),'flags':';'.join(sorted(set(problems)))})
 if shots and shots[0].get('start_ms')!='0':issue('BLOCKER','START_NOT_ZERO','第一鏡需從零開始')
 try:
  target=int(manifest.get('target_duration_ms',0))
  if prev!=target:issue('BLOCKER','TOTAL_DURATION_MISMATCH',f'最後 {prev} / 目標 {target}')
 except ValueError:issue('BLOCKER','BAD_TARGET_DURATION','無效目標片長')
 if missing_prompt:issue('WARNING' if gate=='handoff' else 'BLOCKER','PROMPT_INCOMPLETE',f'{missing_prompt} 鏡缺中英文提示詞')
 if claims_pending:issue('WARNING' if gate=='handoff' else 'BLOCKER','CLAIMS_NOT_REVIEWED',f'{claims_pending} 項鏡頭-主張關聯未通過逐句查核')
 if unidentified_sources:issue('WARNING' if gate=='handoff' else 'BLOCKER','SOURCES_NOT_CLAIM_VERIFIED',f'{unidentified_sources} 項鏡頭-來源關聯僅主題核對')
 if missing_assets:issue('WARNING' if gate=='handoff' else 'BLOCKER','ASSET_FILES_MISSING',f'{missing_assets} 項鏡頭-素材關聯檔案不存在')
 if rights_pending:issue('WARNING' if gate=='handoff' else 'BLOCKER','RIGHTS_PENDING',f'{rights_pending} 項素材關聯尚未完成清權')
 if gate=='release':
  evidence=project/'reports/release_evidence.json'
  if not evidence.is_file():issue('BLOCKER','RELEASE_EVIDENCE_MISSING','需要人工審查與影音 QC 的明確證據')
  else:
   try:
    ev=json.loads(evidence.read_text(encoding='utf-8'))
    for field in ('science_editor_approved','media_rights_approved','audio_timing_verified','render_output_verified','subtitle_verified'):
     if not truth(ev.get(field)):issue('BLOCKER','RELEASE_GATE_UNMET',field)
   except ValueError:issue('BLOCKER','RELEASE_EVIDENCE_BAD_JSON','無效 release_evidence.json')
 result=dict(skill_version='1.1.0',gate=gate,status='BLOCKED' if E else 'PASS_WITH_WARNINGS' if W else 'PASS',counts=dict(shots=len(shots),original_files_locked=protected,missing_prompts=missing_prompt,asset_file_missing=missing_assets,rights_pending=rights_pending,claim_links_unverified=claims_pending,source_links_not_claim_verified=unidentified_sources),blockers=E,warnings=W,shot_details=detail)
 return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('project',type=Path);ap.add_argument('--gate',choices=['handoff','production','release'],default='handoff');ap.add_argument('--report-dir',type=Path)
 args=ap.parse_args();r=audit(args.project,args.gate);out=args.report_dir or args.project/'reports';out.mkdir(parents=True,exist_ok=True)
 (out/'audit_v11.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
 with (out/'shot_evidence_audit.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['shot_id','claim_ids','source_ids','asset_ids','flags']);w.writeheader();w.writerows(r['shot_details'])
 summary=['# BlackBear V1.1 審核結果',f"- Gate: {r['gate']}",f"- Result: **{r['status']}**",f"- Counts: `{json.dumps(r['counts'],ensure_ascii=False)}`",'','## 阻斷']+[f"- {a['code']}: {a['message']} {a['shot_id']}" for a in r['blockers']]+['','## 提醒']+[f"- {a['code']}: {a['message']}" for a in r['warnings']]+['','此報告僅為靜態機械查核，不能取代外部網站查證、逐句人工審查及實際影音測試。']
 (out/'audit_v11.md').write_text('\n'.join(summary)+'\n',encoding='utf-8')
 print(f"{r['status']} | {r['gate']} | shots={r['counts']['shots']} | blockers={len(r['blockers'])} | warnings={len(r['warnings'])}")
 return 2 if r['blockers'] else 0
if __name__=='__main__':sys.exit(main())
