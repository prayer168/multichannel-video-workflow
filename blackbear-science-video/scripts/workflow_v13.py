#!/usr/bin/env python3
"""BlackBear V1.3 local project lifecycle: init, stage, checkpoint, safe restore, export.
Stdlib-only; never edits user-approved original/; no external networks or paid APIs.
"""
import argparse,csv,hashlib,json,re,shutil,sys,zipfile
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath

VERSION='1.3.0'
PHASES=['A','B','C1','C2','C2_5','C3','D','E']
PHASE_ARTIFACTS={
 'A':['research/brief.md','research/sources.csv','research/claims.csv'],
 'B':['script/script.md'],
 'C1':['visual/style_bible.md'],
 'C2':['shots.csv'],
 'C2_5':['research/fact_review.csv','assets/rights_decisions.csv'],
 'C3':['README_Handoff.md','CLAUDE.md','AGENTS.md'],
 'D':['production/final_render.mp4','reports/production_evidence.json'],
 'E':['reports/release_evidence.json']}
SNAP_PREFIX=('project_manifest.json','workflow_state.json','shots.csv','script/','research/','visual/','prompts/','assets/','README_Handoff.md','CLAUDE.md','AGENTS.md')
SKIP_SUFFIX={'.mp4','.mov','.zip','.exe','.dll','.pyc','.woff','.woff2','.ttf','.otf'}

class WorkflowError(Exception):pass

def now():return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def safe_rel(s):
 p=PurePosixPath(str(s).replace('\\','/'))
 if p.is_absolute() or not p.parts or any(x in ('.','..') for x in p.parts):raise WorkflowError('Unsafe relative path: '+str(s))
 return p.as_posix()
def within(p,root):
 root=root.resolve(); v=p.resolve();return v==root or root in v.parents

def event(p,kind,details=None):
 path=p/'state/workflow_events.jsonl';path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('a',encoding='utf-8') as f:f.write(json.dumps({'at':now(),'type':kind,'details':details or {}},ensure_ascii=False)+'\n')

def default_state(slug):
 return {'workflow_version':VERSION,'project_slug':slug,'phase_status':{s:'NOT_STARTED' for s in PHASES},'current_phase':'A','handoff_verified':False,'official_agent_e2e_verified':False,'latest_checkpoint':None,'history_notes':[]}

def init_project(project,slug,title,duration_ms=20000,fps=30):
 if not re.fullmatch(r'[a-z0-9][a-z0-9_\-]{1,70}',slug):raise WorkflowError('slug must be 2-71 ASCII lowercase, digits, _ or -')
 if duration_ms<=0 or fps<=0:raise WorkflowError('positive duration and fps required')
 if duration_ms % 1000 !=0:raise WorkflowError('demo default expects whole-second duration')
 if project.exists() and any(project.iterdir()):raise WorkflowError('Refuse to init nonempty project: '+str(project))
 project.mkdir(parents=True,exist_ok=True)
 for d in ('state','original','research','script','visual','prompts','assets','reports','production','handoff','scripts'):(project/d).mkdir(exist_ok=True)
 dump(project/'project_manifest.json',{'project_slug':slug,'title_zh':title,'skill_version':VERSION,'schema_version':'1.3','project_kind':'generic','created_on':now()[:10],'target_duration_ms':duration_ms,'video':{'width':3840,'height':2160,'fps':fps,'color':'Rec.709 SDR','aspect_ratio':'16:9'},'language':'zh-TW','audience':['國小高年級','國中','一般大眾'],'science_humor_ratio':'70:30','production_release_status':'NOT_APPROVED'})
 dump(project/'workflow_state.json',default_state(slug))
 (project/'research/brief.md').write_text('# 科學研究與企劃\n\n待撰寫。核對資料來源後才能完成 A 階段。\n',encoding='utf-8')
 (project/'script/script.md').write_text('# 影片腳本\n\n待撰寫。勿將推測描述成事實。\n',encoding='utf-8')
 (project/'visual/style_bible.md').write_text('# 視覺規格\n\n待撰寫。真實影像與示意圖需分開標示。\n',encoding='utf-8')
 tables={
 'research/sources.csv':['source_id','title','url','publisher','verification_status','checked_on'],
 'research/claims.csv':['claim_id','claim_text','source_ids','evidence_level','review_status','reviewer','review_date'],
 'research/fact_review.csv':['shot_id','claim_ids','source_ids','status','reviewer','review_date','evidence_note'],
 'assets/asset_register.csv':['asset_id','local_path','media_type','rights_status','license_evidence','usage_scope'],
 'assets/rights_decisions.csv':['asset_id','asset_file','sha256','origin','license_evidence','commercial_use','decision','reviewer','review_date'],
 'shots.csv':['shot_id','chapter','start_ms','end_ms','duration_ms','visual_type','visual_description','camera_movement','narration','onscreen_text','audio_sfx','claim_ids','source_ids','asset_ids','rights_status','prompt_zh','prompt_en','priority','status']}
 for rel,fields in tables.items():
  with (project/rel).open('w',encoding='utf-8-sig',newline='') as f:csv.writer(f).writerow(fields)
 for template in ('CLAUDE.md','AGENTS.md','README_Handoff.md'):
  source=Path(__file__).resolve().parents[1]/'templates'/template
  if source.is_file():shutil.copy2(source,project/template)
  else:(project/template).write_text('# '+template+'\nSee scripts/audit_v13.py\n',encoding='utf-8')
 for script in ('workflow_v13.py','audit_v13.py','audit_v12.py','audit_v11.py','render_smoke_v13.py','validate_handoff.py'):
  shutil.copy2(Path(__file__).resolve().parent/script,project/'scripts'/script)
 event(project,'PROJECT_CREATED',{'slug':slug,'target_duration_ms':duration_ms})
 return project

def check_locked(project):
 lock=project/'reports/original_sha256.txt'; result=[]
 if not lock.exists():
  if any((project/'original').rglob('*')) and any(x.is_file() for x in (project/'original').rglob('*')):
   raise WorkflowError('Original source files found but hash lock absent')
  return result
 for row in lock.read_text(encoding='utf-8-sig').splitlines():
  if not row.strip():continue
  parts=row.split(maxsplit=1)
  if len(parts)!=2:raise WorkflowError('Malformed lock row')
  expect,rel=parts;p=project/safe_rel(rel)
  if not within(p,project) or not p.is_file() or sha(p)!=expect:raise WorkflowError('ORIGINAL_CHANGED_OR_MISSING: '+rel)
  result.append(rel)
 return result

def stage_complete(project,stage,evidence):
 state=load(project/'workflow_state.json');
 if stage not in PHASES:raise WorkflowError('Unknown stage: '+stage)
 idx=PHASES.index(stage)
 for prev in PHASES[:idx]:
  if state['phase_status'].get(prev)!='COMPLETE':raise WorkflowError('Previous phase not complete: '+prev)
 if state['phase_status'].get(stage)=='COMPLETE':raise WorkflowError('Phase already complete; create a new project revision to re-approve')
 check_locked(project)
 rel=safe_rel(evidence);p=project/rel
 if not within(p,project) or not p.is_file() or p.stat().st_size<20:raise WorkflowError('Evidence missing, too small or outside project: '+rel)
 for r in PHASE_ARTIFACTS[stage]:
  q=project/r
  if not q.is_file() or q.stat().st_size==0:raise WorkflowError('Missing required phase artifact: '+r)
 if stage in ('C2','C2_5','C3'):
  sys.path.insert(0,str(Path(__file__).resolve().parent))
  from audit_v13 import audit
  check=audit(project,'handoff')
  if check['status']=='BLOCKED':raise WorkflowError('Cannot approve phase with structural blockers: '+','.join(x['code'] for x in check['blockers'][:5]))
 if stage=='D':
  sys.path.insert(0,str(Path(__file__).resolve().parent))
  from audit_v13 import audit
  if audit(project,'production')['status']=='BLOCKED':raise WorkflowError('Production not approved; technical POC must stay separate from official D')
 if stage=='E':
  sys.path.insert(0,str(Path(__file__).resolve().parent))
  from audit_v13 import audit
  if audit(project,'release')['status']=='BLOCKED':raise WorkflowError('Release not approved')
 state['phase_status'][stage]='COMPLETE';state['current_phase']=PHASES[min(idx+1,len(PHASES)-1)];state.setdefault('phase_evidence',{})[stage]={'path':rel,'sha256':sha(p),'at':now()}
 if stage=='C3':state['handoff_verified']=True
 dump(project/'workflow_state.json',state);event(project,'PHASE_COMPLETED',{'stage':stage,'evidence':rel,'sha256':sha(p)})
 return create_checkpoint(project,label='after_'+stage)

def files_to_snapshot(project):
 for p in sorted(project.rglob('*')):
  if not p.is_file() or p.is_symlink():continue
  rel=p.relative_to(project).as_posix()
  if rel.startswith(('state/','reports/','original/','production/','handoff/')):continue
  if not any(rel==x or (x.endswith('/') and rel.startswith(x)) for x in SNAP_PREFIX):continue
  if p.suffix.lower() in SKIP_SUFFIX or p.stat().st_size>5_000_000:continue
  yield rel,p

def create_checkpoint(project,label='manual'):
 check_locked(project)
 base=project/'state/checkpoints';base.mkdir(parents=True,exist_ok=True)
 nums=[int(p.name[3:]) for p in base.iterdir() if p.is_dir() and re.fullmatch(r'cp_\d{4}',p.name)]
 ident=f'cp_{max(nums,default=0)+1:04d}'; folder=base/ident; folder.mkdir()
 data={}
 for rel,p in files_to_snapshot(project):
  dest=folder/'files'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
  data[rel]=sha(p)
 manifest={'checkpoint_id':ident,'at':now(),'label':label,'files':data,'original_locked':check_locked(project)}
 dump(folder/'checkpoint.json',manifest)
 s=load(project/'workflow_state.json');s['latest_checkpoint']=ident;dump(project/'workflow_state.json',s)
 event(project,'CHECKPOINT_CREATED',{'id':ident,'label':label,'file_count':len(data)})
 return ident

def restore(project,ident=None,apply=False):
 state=load(project/'workflow_state.json');ident=ident or state.get('latest_checkpoint')
 if not ident or not re.fullmatch(r'cp_\d{4}',ident):raise WorkflowError('Invalid checkpoint identifier')
 check_locked(project)
 checkpoint=project/'state/checkpoints'/ident
 manifest=load(checkpoint/'checkpoint.json')
 validated=[]
 for rel,want in manifest['files'].items():
  safe_rel(rel)
  if rel.startswith(('state/','reports/','original/','production/','handoff/')):raise WorkflowError('Checkpoint contains forbidden path')
  src=checkpoint/'files'/rel;dest=project/rel
  if not within(src,checkpoint) or not within(dest,project) or not src.is_file() or sha(src)!=want:raise WorkflowError('CHECKPOINT_CORRUPTED: '+rel)
  validated.append((rel,src,dest))
 report={'checkpoint':ident,'mode':'apply' if apply else 'dry_run','files':len(validated),'modified':[rel for rel,_,dest in validated if not dest.exists() or sha(dest)!=manifest['files'][rel]]}
 if not apply:return report
 backup=project/'state/recovery_backups'/now().replace(':','-')
 for rel,src,dest in validated:
  if dest.exists():
   old=backup/rel;old.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,old)
  dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
 state_restored=load(project/'workflow_state.json');state_restored['latest_checkpoint']=ident;dump(project/'workflow_state.json',state_restored)
 event(project,'RESTORED_CHECKPOINT',{'checkpoint':ident,'modified':report['modified'],'backup':str(backup.relative_to(project))})
 return report

def import_v12(project):
 check_locked(project)
 if not (project/'shots.csv').exists():raise WorkflowError('Missing shots.csv')
 if (project/'workflow_state.json').exists():raise WorkflowError('Already initialized')
 slug=load(project/'project_manifest.json')['project_slug']
 s=default_state(slug)
 for p in PHASES[:6]:s['phase_status'][p]='IMPORTED_UNVERIFIED'
 s['current_phase']='C3';s['history_notes']=['V1.2 existing A-C3 files imported as non-validated phase completion. Mechanical Nemo v12 gates remain authoritative. Human signoffs are NOT implied.']
 dump(project/'workflow_state.json',s)
 (project/'scripts').mkdir(exist_ok=True)
 for script in ('workflow_v13.py','audit_v13.py','audit_v12.py','audit_v11.py','render_smoke_v13.py','validate_handoff.py'):
  shutil.copy2(Path(__file__).resolve().parent/script,project/'scripts'/script)
 event(project,'V12_IMPORTED',{'phase_status':'IMPORTED_UNVERIFIED','rights_approved':False})
 return create_checkpoint(project,'v12_import_baseline')

def pack(project,output,include_preview=False):
 sys.path.insert(0,str(Path(__file__).resolve().parent));from audit_v13 import audit
 result=audit(project,'handoff');
 if result['status']=='BLOCKED':raise WorkflowError('Handoff blocked: '+repr(result['blockers'][:4]))
 report=project/'reports/v13_handoff';report.mkdir(parents=True,exist_ok=True)
 dump(report/'audit_v13.json',result)
 data=[]
 for p in sorted(project.rglob('*')):
  if not p.is_file() or p.is_symlink():continue
  rel=p.relative_to(project).as_posix()
  if rel.startswith(('state/recovery_backups/','handoff/')):continue
  if p.suffix.lower() in ('.pyc','.zip'):continue
  if '/__pycache__/' in rel:continue
  if p.suffix.lower() in ('.mp4','.mov') and not include_preview:continue
  data.append((rel,p))
 checks={rel:sha(p) for rel,p in data}
 content=json.dumps({'skill_version':VERSION,'project_slug':load(project/'project_manifest.json').get('project_slug'),'files':checks},ensure_ascii=False,indent=2)+'\n'
 output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for rel,p in data:z.write(p,rel)
  z.writestr('HANDOFF_CHECKSUMS.json',content)
 with zipfile.ZipFile(output) as z:
  if z.testzip():raise WorkflowError('ZIP integrity failed')
  chk=json.loads(z.read('HANDOFF_CHECKSUMS.json'))
  for rel,h in chk['files'].items():
   if hashlib.sha256(z.read(rel)).hexdigest()!=h:raise WorkflowError('ZIP content sha mismatch '+rel)
 event(project,'HANDOFF_EXPORTED',{'zip':str(output),'files':len(data),'status':result['status']})
 return {'file':str(output),'files':len(data),'size':output.stat().st_size,'status':result['status']}

def main():
 ap=argparse.ArgumentParser(description='BlackBear V1.3 workflow manager');sp=ap.add_subparsers(dest='command',required=True)
 s=sp.add_parser('init');s.add_argument('project');s.add_argument('--slug',required=True);s.add_argument('--title',required=True);s.add_argument('--duration-ms',type=int,default=20000);s.add_argument('--fps',type=int,default=30)
 s=sp.add_parser('import-v12');s.add_argument('project')
 s=sp.add_parser('status');s.add_argument('project')
 s=sp.add_parser('complete');s.add_argument('project');s.add_argument('--stage',required=True,choices=PHASES);s.add_argument('--evidence',required=True)
 s=sp.add_parser('checkpoint');s.add_argument('project');s.add_argument('--label',default='manual')
 s=sp.add_parser('restore');s.add_argument('project');s.add_argument('--checkpoint');s.add_argument('--apply',action='store_true')
 s=sp.add_parser('pack');s.add_argument('project');s.add_argument('--out',required=True);s.add_argument('--include-preview',action='store_true')
 args=ap.parse_args(); p=Path(args.project).resolve()
 try:
  if args.command=='init':value={'project':str(init_project(p,args.slug,args.title,args.duration_ms,args.fps))}
  elif args.command=='import-v12':value={'checkpoint':import_v12(p)}
  elif args.command=='status':value={'state':load(p/'workflow_state.json'),'original_files_checked':check_locked(p)}
  elif args.command=='complete':value={'checkpoint':stage_complete(p,args.stage,args.evidence),'stage':args.stage}
  elif args.command=='checkpoint':value={'checkpoint':create_checkpoint(p,args.label)}
  elif args.command=='restore':value=restore(p,args.checkpoint,args.apply)
  else:value=pack(p,args.out,args.include_preview)
  print(json.dumps(value,ensure_ascii=False,indent=2))
 except (WorkflowError,OSError,ValueError,KeyError,json.JSONDecodeError) as ex:
  print('WORKFLOW_ERROR: '+str(ex),file=sys.stderr);return 2
 return 0
if __name__=='__main__':sys.exit(main())
