#!/usr/bin/env python3
"""BlackBear Science Video V1.2: deterministic gate audit. No network or external deps."""
from pathlib import Path
import argparse,csv,hashlib,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_v11 import audit as audit_v11

def rows(path):
    with path.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def fingerprint(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def link_ids(value):return [x.strip() for x in (value or '').split(';') if x.strip()]
def audit(project,gate):
    project=Path(project); base=audit_v11(project,'handoff');blockers=list(base['blockers']);warnings=list(base['warnings']);metrics={};details=[]
    def issue(level,code,msg,shot=''):(blockers if level=='BLOCKER' else warnings).append({'code':code,'message':msg,'shot_id':shot})
    original=project/'original/shot_list_108.csv';derived=project/'shots.csv'
    required=['original/point_nemo_script_v1.md','original/shot_list_108.csv','original/shot_list_108.json','original/chapter_timeline_v1.csv','original/storyboard_preview.html','shots.csv','prompts/prompt_provenance.csv','research/shot_fact_review.csv','assets/rights_decisions.csv','research/source_checks_20261123.csv']
    for path in required:
        if not (project/path).is_file():issue('BLOCKER','REQUIRED_FILE_MISSING',path)
    if not original.exists() or not derived.exists():return {'status':'BLOCKED','gate':gate,'blockers':blockers,'warnings':warnings,'counts':metrics,'shots':[]}
    src=rows(original);new=rows(derived)
    origin={r['shot_id']:r for r in src};current={r['shot_id']:r for r in new}
    if len(src)!=108 or len(new)!=108 or len(current)!=108:issue('BLOCKER','SHOT_COUNT_CHANGED','expected 108 original and derived unique shots')
    prov=rows(project/'prompts/prompt_provenance.csv') if (project/'prompts/prompt_provenance.csv').is_file() else []
    provenance={r['shot_id']:r for r in prov}
    fact=rows(project/'research/shot_fact_review.csv') if (project/'research/shot_fact_review.csv').is_file() else []
    fact_by={r['shot_id']:r for r in fact}
    rights=rows(project/'assets/rights_decisions.csv') if (project/'assets/rights_decisions.csv').is_file() else []
    rights_by={r['shot_id']:r for r in rights}
    source_list=rows(project/'research/source_checks_20261123.csv') if (project/'research/source_checks_20261123.csv').is_file() else []
    check_sources={r['source_id'] for r in source_list}
    read_only_fields={
        'chapter':'chapter_id','start_ms':'start_sec','end_ms':'end_sec','duration_ms':'duration_sec',
        'visual_type':'visual_mode','visual_description':'scene_description','camera_movement':'camera_move',
        'narration':'narration_excerpt','onscreen_text':'text_overlay','audio_sfx':'sfx_music_cue',
        'source_ids':'source_ids','priority':'asset_priority','status':'status'
    }
    originals_retained=created=missing=changed=0;rights_hold=0;science_pending=0;storyboard_drift=0
    for sid,r in current.items():
        old=origin.get(sid);pm=provenance.get(sid);f=fact_by.get(sid);asset=rights_by.get(sid)
        if not old:issue('BLOCKER','NEW_SHOT_UNKNOWN','A new shot is not in locked original',sid);continue
        for field,original_field in read_only_fields.items():
            if original_field in ('start_sec','end_sec','duration_sec'):
                try:equal=int(r[field])==int(old[original_field])*1000
                except (KeyError,ValueError,TypeError):equal=False
            else:equal=(r.get(field,'')==old.get(original_field,''))
            if not equal:
                storyboard_drift+=1;issue('BLOCKER','EDITORIAL_FIELD_CHANGED',field,sid)
        if r.get('claim_ids')!='CLAIM_'+sid or r.get('asset_ids')!='ASSET_'+sid:
            issue('BLOCKER','TRACE_ID_CHANGED','claim/asset mapping has changed',sid)
        zh=r.get('prompt_zh','').strip();en=r.get('prompt_en','').strip()
        was_complete=bool(old['ai_prompt_zh'].strip() and old['ai_prompt_en'].strip())
        if was_complete:
            originals_retained+=1
            if r.get('prompt_zh')!=old['ai_prompt_zh'] or r.get('prompt_en')!=old['ai_prompt_en']:
                changed+=1;issue('BLOCKER','EXISTING_PROMPT_CHANGED','Legacy prompt modified rather than preserved',sid)
            if not pm or pm.get('prompt_origin')!='RETAINED_V1':issue('BLOCKER','PROMPT_PROVENANCE_BAD','Wrong origin flag',sid)
        else:
            if not zh or not en:missing+=1;issue('BLOCKER','NEW_PROMPT_MISSING','Chinese or English prompt missing',sid)
            else:created+=1
            if not pm or pm.get('prompt_origin')!='FILLED_V12':issue('BLOCKER','PROMPT_PROVENANCE_BAD','Wrong origin flag',sid)
            if zh and old.get('science_guardrail','') not in zh:issue('BLOCKER','SCIENCE_GUARDRAIL_DROPPED','Original science guardrail absent from new prompt',sid)
            if en and ('Shot '+sid) not in en:issue('BLOCKER','ENGLISH_PROMPT_NOT_SPECIFIC','Missing stable shot identity',sid)
        if not f or f.get('science_guardrail')!=old.get('science_guardrail') or f.get('original_narration')!=old.get('narration_excerpt'):
            issue('BLOCKER','SCIENCE_TRACE_BROKEN','Fact review differs from original source',sid)
        if not f or f.get('review_status')!='APPROVED':science_pending+=1
        for sid2 in link_ids(old.get('source_ids','')):
            if sid2 not in check_sources:issue('BLOCKER','SOURCE_CHECK_MISSING',sid2,sid)
        if not asset:issue('BLOCKER','RIGHTS_ROW_MISSING','Missing asset rights audit',sid)
        else:
            if asset.get('rights_decision')!='APPROVED':rights_hold+=1
            elif not all(asset.get(k) for k in ('origin_url','actual_file_sha256','rights_evidence_url_or_path')) or asset.get('commercial_use_reviewed')!='YES' or asset.get('license_terms_reviewed')!='YES':
                issue('BLOCKER','BAD_RIGHTS_APPROVAL','Rights approval without sufficient evidence',sid)
        details.append({'shot_id':sid,'prompt_origin':pm.get('prompt_origin','UNKNOWN') if pm else '', 'fact_status':f.get('review_status','MISSING') if f else '', 'rights_decision':asset.get('rights_decision','MISSING') if asset else ''})
    metrics={'shots':len(new),'original_prompts_preserved':originals_retained,'prompts_filled_v12':created,'prompts_missing':missing,'legacy_prompts_changed':changed,'original_editorial_fields_changed':storyboard_drift,'claims_awaiting_editor_approval':science_pending,'rights_on_hold':rights_hold,'sources_in_registry':len(check_sources),'original_hashes_protected':base.get('counts',{}).get('original_files_locked',0)}
    if originals_retained!=16 or created!=92:issue('BLOCKER','EXPECTED_PROMPT_DISTRIBUTION_CHANGED',f'preserved={originals_retained} filled={created}')
    if len(fact)!=108:issue('BLOCKER','FACT_ROW_COUNT','fact review must cover all 108 shots')
    if len(rights)!=108:issue('BLOCKER','RIGHTS_ROW_COUNT','rights review must cover all 108 shots')
    if gate=='poc':
        take=[r for r in new if r.get('chapter')=='CH01' and int(r.get('end_ms','0'))<=27000]
        if len(take)!=4 or int(take[0]['start_ms'])!=0 or int(take[-1]['end_ms'])!=27000:issue('BLOCKER','POC_SHOT_RANGE','POC must cover CH01 S01–S04 exactly 00:00–00:27')
        if not (project/'production/ch01_poc/scripts/render_ffmpeg_placeholder.py').is_file():issue('BLOCKER','POC_SCRIPT_MISSING','No offline placeholder renderer')
    if gate in ('production','release'):
        # The old V1.1 workflow refuses missing material assets and unsigned claims/rights.
        for msg,number in [('SCIENCE_SIGNOFF_PENDING',science_pending),('RIGHTS_APPROVAL_PENDING',rights_hold)]:
            if number:issue('BLOCKER',msg,f'{number} shots still pending')
        for b in audit_v11(project,'production')['blockers']:
            if b not in blockers:blockers.append(b)
    if gate=='release':
        for b in audit_v11(project,'release')['blockers']:
            if b not in blockers:blockers.append(b)
    if science_pending:issue('WARNING','SCIENCE_REVIEW_NOT_COMPLETE',f'{science_pending} shots need editor review')
    if rights_hold:issue('WARNING','RIGHTS_NOT_APPROVED',f'{rights_hold} shots need asset license evidence')
    # V1.1 handoff reported asset and claim warnings; those remain honest and visible.
    return {'skill_version':'1.2.0','gate':gate,'status':'BLOCKED' if blockers else 'PASS_WITH_WARNINGS' if warnings else 'PASS','counts':metrics,'blockers':blockers,'warnings':warnings,'shot_details':details,'note':'Technical pass never means scientific accuracy, asset rights approval or finished video.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('project',type=Path);ap.add_argument('--gate',choices=['handoff','poc','production','release'],default='handoff');ap.add_argument('--report-dir',type=Path)
    a=ap.parse_args(); r=audit(a.project,a.gate);out=a.report_dir or a.project/'reports/v12_'+a.gate;out.mkdir(parents=True,exist_ok=True)
    (out/'audit_v12.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# V1.2 '+a.gate+' 品質閘門', '',f"**結果：{r['status']}**",'','## 統計']+[f'- {k}: {v}' for k,v in r['counts'].items()]+['','## 阻斷']+[f"- {x['code']}: {x['message']} {x['shot_id']}" for x in r['blockers']]+['','## 注意']+[f"- {x['code']}: {x['message']}" for x in r['warnings']]+['','人工科學查證、逐檔權利判定、成片聲畫品質需另行簽核。']
    (out/'audit_v12.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f"{a.gate}: {r['status']} | {json.dumps(r['counts'],ensure_ascii=False)}")
    return 2 if r['blockers'] else 0
if __name__=='__main__':sys.exit(main())
