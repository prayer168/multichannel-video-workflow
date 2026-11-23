#!/usr/bin/env python3
"""Safely restore curated prompt fields into a copied derived shots.csv, never originals.
For Point Nemo V1.2 canonical prompt artifacts; configurable for new work with editorial approvals.
"""
from pathlib import Path
import argparse,csv,json,shutil,tempfile,sys

def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:
  d=csv.DictReader(f);return d.fieldnames,list(d)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('project',type=Path);ap.add_argument('--apply',action='store_true');ap.add_argument('--output',type=Path,default=None)
 args=ap.parse_args();p=args.project
 src=p/'original/shot_list_108.csv';derived=p/'shots.csv'; briefs=p/'prompts/english_scene_briefs.json';prov=p/'prompts/prompt_provenance.csv'
 for f in [src,derived,briefs,prov]:
  if not f.is_file():print('Missing '+str(f),file=sys.stderr);return 2
 osf,o=read(src);df,d=read(derived); _,pv=read(prov)
 original={r['shot_id']:r for r in o};meta={r['shot_id']:r for r in pv};brief=json.loads(briefs.read_text(encoding='utf-8'))
 failures=[]
 for r in d:
  sid=r['shot_id'];old=original.get(sid)
  if not old:failures.append('unknown shot '+sid);continue
  if old['ai_prompt_zh'].strip() and old['ai_prompt_en'].strip():
   if r['prompt_zh']!=old['ai_prompt_zh'] or r['prompt_en']!=old['ai_prompt_en']:failures.append('legacy prompt modified '+sid)
  else:
   if not r['prompt_zh'].strip() or not r['prompt_en'].strip() or sid not in brief or not meta.get(sid):failures.append('missing generated prompt '+sid)
 if failures:
  print('\n'.join(failures),file=sys.stderr);return 2
 print(f'PROMPTS VALID: {len(o)} shots; originals protected. Nothing rewritten.')
 if args.apply:
  output=args.output or p/'prompts/revalidated_shots.csv'
  if output.resolve()==src.resolve() or 'original' in output.parts:print('Cannot write into original/',file=sys.stderr);return 2
  output.parent.mkdir(parents=True,exist_ok=True)
  with output.open('w',encoding='utf-8-sig',newline='') as f:
   w=csv.DictWriter(f,fieldnames=df);w.writeheader();w.writerows(d)
  print('Independent copy saved:',output)
 return 0
if __name__=='__main__':sys.exit(main())
