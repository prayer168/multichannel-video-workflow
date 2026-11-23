#!/usr/bin/env python3
"""V1.3 scope-explicit gate audit: generalized projects + Nemo V1.2 legacy adapter.
Structural checks are not expert signoff or proof of external Claude/Codex execution.
"""
from pathlib import Path
import argparse,csv,json,sys,shutil,hashlib,re
from workflow_v13 import VERSION,PHASES,check_locked,WorkflowError,load,dump,sha,safe_rel,within

def read_csv(p):
 if not p.is_file():return None
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def ids(s):return [x.strip() for x in (s or '').split(';') if x.strip()]
def audit(project,gate='handoff'):
 project=Path(project);blocks=[];warns=[];stats={};
 def issue(level,code,detail,shot_id=''):(blocks if level=='BLOCKER' else warns).append({'code':code,'message':detail,'shot_id':shot_id})
 try:locked=check_locked(project)
 except WorkflowError as ex:locked=[];issue('BLOCKER','ORIGINAL_LOCK_MISMATCH',str(ex))
 try:m=load(project/'project_manifest.json')
 except (OSError,ValueError) as ex:m={};issue('BLOCKER','MANIFEST_INVALID',str(ex))
 kind=m.get('project_kind','legacy_nemo' if (project/'original/shot_list_108.csv').exists() else 'generic')
 try:state=load(project/'workflow_state.json')
 except (OSError,ValueError) as ex:state={};issue('BLOCKER','WORKFLOW_STATE_INVALID',str(ex))
 for stage in PHASES:
  if stage not in state.get('phase_status',{}):issue('BLOCKER','STAGE_STATUS_MISSING',stage)
 for stage,entry in state.get('phase_evidence',{}).items():
  rel=entry.get('path','')
  try:
   p=project/rel
   if not p.is_file() or sha(p)!=entry.get('sha256'):
    issue('BLOCKER','PHASE_EVIDENCE_DRIFT',f'{stage}: {rel} differs from approved checkpoint')
  except (OSError,ValueError):issue('BLOCKER','PHASE_EVIDENCE_INVALID',f'{stage}: {rel}')
 if state.get('official_agent_e2e_verified') is True and not (project/'reports/agent_execution_evidence.json').exists():
  issue('BLOCKER','AGENT_VERIFIED_WITHOUT_PROOF','Do not claim external agent executed without logs')
 if not isinstance(m.get('target_duration_ms'),int) or m.get('target_duration_ms',0)<=0:issue('BLOCKER','DURATION_INVALID','target_duration_ms positive integer')
 if not re.fullmatch('[a-z0-9][a-z0-9_-]+',m.get('project_slug','')):issue('BLOCKER','SLUG_INVALID','ASCII project slug')
 if kind=='legacy_nemo':
  sys.path.insert(0,str(Path(__file__).resolve().parent))
  from audit_v12 import audit as legacy
  gate1='poc' if gate=='poc' else gate
  prev=legacy(project,gate1)
  blocks.extend(prev['blockers']);warns.extend(prev['warnings']);stats.update(prev['counts'])
  stats['mode']='NEMO_V12_ADAPTER'
  if state.get('phase_status',{}).get('C3')=='COMPLETE' and not state.get('handoff_verified'):
   issue('BLOCKER','COMPLETION_FLAG_INCONSISTENT','C3 marked complete but no handoff flag')
 else:
  needed=['research/sources.csv','research/claims.csv','research/fact_review.csv','assets/asset_register.csv','assets/rights_decisions.csv','shots.csv']
  for p in needed:
   if not (project/p).is_file():issue('BLOCKER','REQUIRED_FILE_MISSING',p)
  sources=read_csv(project/'research/sources.csv') or []
  claims=read_csv(project/'research/claims.csv') or []
  facts=read_csv(project/'research/fact_review.csv') or []
  assets=read_csv(project/'assets/asset_register.csv') or []
  rights=read_csv(project/'assets/rights_decisions.csv') or []
  shots=read_csv(project/'shots.csv') or []
  source_by={r.get('source_id'):r for r in sources}
  claim_by={r.get('claim_id'):r for r in claims}
  assets_by={r.get('asset_id'):r for r in assets}
  fact_by={r.get('shot_id'):r for r in facts}
  rights_by={r.get('asset_id'):r for r in rights}
  for label,collection,key in [('sources',sources,'source_id'),('claims',claims,'claim_id'),('shots',shots,'shot_id'),('assets',assets,'asset_id'),('fact_review',facts,'shot_id'),('rights_decisions',rights,'asset_id')]:
   vs=[x.get(key) for x in collection]
   if any(not x for x in vs) or len(set(vs))!=len(vs):issue('BLOCKER','DUPLICATE_OR_EMPTY_ID',label)
  if not shots:issue('BLOCKER','SHOTS_MISSING','At least one shot required for handoff')
  if not sources:issue('BLOCKER','SOURCE_REGISTER_EMPTY','No scientific sources')
  prev_end=0;missing_prompt=missing_asset=claims_pending=rights_pending=0;bad_evidence=0
  for r in shots:
   shotid=r.get('shot_id','')
   try:
    start,end,dur=map(int,[r.get('start_ms'),r.get('end_ms'),r.get('duration_ms')])
    if start!=prev_end or end<=start or dur!=end-start:issue('BLOCKER','SHOT_TIME_INVALID','Timeline has gap/overlap or wrong duration',shotid)
    prev_end=end
   except (ValueError,TypeError):issue('BLOCKER','SHOT_TIME_NOT_INTEGER','Expected milliseconds',shotid)
   if not r.get('visual_description','').strip() or not r.get('visual_type','').strip():issue('BLOCKER','SHOT_VISUAL_BLANK','No visual',shotid)
   if not r.get('prompt_zh','').strip() or not r.get('prompt_en','').strip():missing_prompt+=1
   claim_refs=ids(r.get('claim_ids',''));source_refs=ids(r.get('source_ids',''));asset_refs=ids(r.get('asset_ids',''))
   for cid in claim_refs:
    if cid not in claim_by:issue('BLOCKER','CLAIM_REF_MISSING',cid,shotid)
    elif claim_by[cid].get('review_status') not in ('VERIFIED','APPROVED','已驗證'):claims_pending+=1
   for sourceid in source_refs:
    if sourceid not in source_by:issue('BLOCKER','SOURCE_REF_MISSING',sourceid,shotid)
    elif not source_by[sourceid].get('url','').startswith(('http://','https://')):issue('BLOCKER','SOURCE_URL_INVALID',sourceid,shotid)
   for aid in asset_refs:
    if aid not in assets_by:issue('BLOCKER','ASSET_REF_MISSING',aid,shotid);continue
    a=assets_by[aid];rel=a.get('local_path','')
    assetp=None;safe_asset=False
    if rel:
     try: assetp=project/safe_rel(rel);safe_asset=within(assetp,project)
     except WorkflowError: safe_asset=False
     if not safe_asset:issue('BLOCKER','ASSET_PATH_UNSAFE',str(rel),shotid)
    if not safe_asset or not assetp.is_file():missing_asset+=1
    right=rights_by.get(aid)
    if not right:issue('BLOCKER','RIGHTS_ROW_MISSING',aid,shotid)
    elif right.get('decision')!='APPROVED':rights_pending+=1
    elif not all([right.get('asset_file'),right.get('sha256'),right.get('license_evidence'),right.get('reviewer'),right.get('review_date'),right.get('commercial_use')=='YES']):
     bad_evidence+=1;issue('BLOCKER','FALSE_RIGHTS_APPROVAL',aid,shotid)
    else:
     try:
      f=project/safe_rel(right['asset_file'])
      if not within(f,project):raise WorkflowError('outside project')
      if not f.is_file() or sha(f)!=right['sha256']:issue('BLOCKER','RIGHTS_FILE_HASH_INVALID',aid,shotid)
     except WorkflowError:issue('BLOCKER','RIGHTS_PATH_UNSAFE',aid,shotid)
   f=fact_by.get(shotid)
   if not f:issue('BLOCKER','FACT_ROW_MISSING',shotid)
   elif f.get('claim_ids','')!=r.get('claim_ids','') or f.get('source_ids','')!=r.get('source_ids',''):
    issue('BLOCKER','FACT_MAPPING_DRIFT',shotid)
   elif f.get('status') not in ('APPROVED','VERIFIED'):claims_pending+=1
   elif not f.get('reviewer') or not f.get('review_date') or not f.get('evidence_note'):
    issue('BLOCKER','FALSE_SCIENCE_APPROVAL','Claim signed without reviewer/evidence',shotid)
  if shots and prev_end!=m.get('target_duration_ms'):issue('BLOCKER','TOTAL_DURATION_MISMATCH',f'{prev_end}!={m.get("target_duration_ms")}')
  if missing_prompt:issue('BLOCKER','PROMPTS_MISSING',f'{missing_prompt} shots missing bilingual prompt')
  if claims_pending:issue('WARNING','SCIENCE_PENDING',f'{claims_pending} review links are not approved')
  if missing_asset:issue('WARNING','MEDIA_PENDING',f'{missing_asset} shot assets not created')
  if rights_pending:issue('WARNING','RIGHTS_PENDING',f'{rights_pending} license links pending')
  if gate in ('production','release'):
   if claims_pending:issue('BLOCKER','SCIENCE_GATE_BLOCKED','Human scientific review pending')
   if missing_asset:issue('BLOCKER','MEDIA_GATE_BLOCKED','Production asset missing')
   if rights_pending:issue('BLOCKER','RIGHTS_GATE_BLOCKED','Unapproved asset rights')
   if bad_evidence:issue('BLOCKER','LICENSE_EVIDENCE_INVALID','Missing proof of rights')
  if gate=='release':
   evidence=project/'reports/release_evidence.json'
   if not evidence.is_file():issue('BLOCKER','RELEASE_EVIDENCE_MISSING','Expert / copyright / render / subtitle approval missing')
   else:
    try:
     ev=load(evidence)
     for key in ('science_editor_approved','media_rights_approved','audio_timing_verified','render_output_verified','subtitle_verified'):
      if ev.get(key) is not True:issue('BLOCKER','RELEASE_SIGNOFF_MISSING',key)
    except Exception:issue('BLOCKER','RELEASE_EVIDENCE_INVALID','Unreadable release evidence')
  stats.update({'mode':'GENERIC_V13','shots':len(shots),'sources':len(sources),'claims':len(claims),'missing_prompts':missing_prompt,'science_pending_links':claims_pending,'missing_assets':missing_asset,'rights_pending':rights_pending})
 stats['original_files_locked']=len(locked)
 status='BLOCKED' if blocks else 'PASS_WITH_WARNINGS' if warns else 'PASS'
 return {'skill_version':VERSION,'project_slug':m.get('project_slug'),'project_kind':kind,'gate':gate,'status':status,'metrics':stats,'blockers':blocks,'warnings':warns,'state':{'current_phase':state.get('current_phase'),'phase_status':state.get('phase_status'),'official_agent_e2e_verified':state.get('official_agent_e2e_verified',False)},'limitations':['Handoff PASS does not imply science accuracy or commercial use rights','Technical smoke render is not actual Claude Code/Codex integration test','Release remains BLOCKED without independent signoff']}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('project');ap.add_argument('--gate',choices=['handoff','poc','production','release'],default='handoff');ap.add_argument('--out');args=ap.parse_args()
 r=audit(Path(args.project),args.gate)
 output=Path(args.out) if args.out else Path(args.project)/('reports/v13_'+args.gate)
 output.mkdir(parents=True,exist_ok=True);dump(output/'audit_v13.json',r)
 lines=['# BlackBear V1.3 '+args.gate+' 品質閘門','',f"**{r['status']}**",'','## 數據']+[f'- {k}: {v}' for k,v in r['metrics'].items()]+['','## 阻擋']+[f"- {a['code']}: {a['message']} ({a['shot_id']})" for a in r['blockers']]+['','## 注意']+[f"- {a['code']}: {a['message']}" for a in r['warnings']]+['','此處的技術通過不等於科學及清權正式批准。']
 (output/'audit_v13.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 print(f"{r['status']} | {args.gate} | {r['metrics']}")
 return 2 if r['blockers'] else 0
if __name__=='__main__':sys.exit(main())
