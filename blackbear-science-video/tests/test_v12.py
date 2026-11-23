#!/usr/bin/env python3
"""Local V1.2 regression and negative tests. Run with path to Nemo project."""
import csv,json,hashlib,tempfile,sys,shutil,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_v12 import audit
PROJECT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else None
sys.argv=sys.argv[:1]
class V12Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if not PROJECT or not PROJECT.exists():raise unittest.SkipTest('Pass a test project directory')
 def test_handoff(self):
  r=audit(PROJECT,'handoff');self.assertEqual('PASS_WITH_WARNINGS',r['status'],r['blockers']);self.assertEqual(92,r['counts']['prompts_filled_v12']);self.assertEqual(16,r['counts']['original_prompts_preserved'])
 def test_poc_gate(self):
  r=audit(PROJECT,'poc');self.assertEqual('PASS_WITH_WARNINGS',r['status'],r['blockers'])
 def test_production_blocks(self):
  r=audit(PROJECT,'production');self.assertEqual('BLOCKED',r['status'])
 def test_original_tampering_fails(self):
  with tempfile.TemporaryDirectory() as td:
   copy=Path(td)/'project';shutil.copytree(PROJECT,copy)
   p=copy/'original/point_nemo_script_v1.md'
   p.write_bytes(p.read_bytes()+b'\nTEST TAMPER\n')
   r=audit(copy,'handoff');self.assertEqual('BLOCKED',r['status']);self.assertTrue(any(b['code']=='ORIGINAL_CHANGED' for b in r['blockers']))
 def test_legacy_prompt_tampering_fails(self):
  with tempfile.TemporaryDirectory() as td:
   copy=Path(td)/'project';shutil.copytree(PROJECT,copy)
   p=copy/'shots.csv'
   with p.open(encoding='utf-8-sig',newline='') as f: rd=csv.DictReader(f);fieldnames=rd.fieldnames;rs=list(rd)
   r=next(x for x in rs if x['shot_id']=='CH01_S03');r['prompt_en']+=' EXTRA'
   with p.open('w',encoding='utf-8-sig',newline='') as f:wr=csv.DictWriter(f,fieldnames=fieldnames);wr.writeheader();wr.writerows(rs)
   result=audit(copy,'handoff');self.assertEqual('BLOCKED',result['status']);self.assertTrue(any(b['code']=='EXISTING_PROMPT_CHANGED' for b in result['blockers']))
 def test_rights_cannot_self_approve(self):
  with tempfile.TemporaryDirectory() as td:
   copy=Path(td)/'project';shutil.copytree(PROJECT,copy)
   p=copy/'assets/rights_decisions.csv'
   with p.open(encoding='utf-8-sig',newline='') as f: rd=csv.DictReader(f);cols=rd.fieldnames;rs=list(rd)
   rs[0]['rights_decision']='APPROVED'
   with p.open('w',encoding='utf-8-sig',newline='') as f:wr=csv.DictWriter(f,fieldnames=cols);wr.writeheader();wr.writerows(rs)
   res=audit(copy,'handoff');self.assertEqual('BLOCKED',res['status']);self.assertTrue(any(b['code']=='BAD_RIGHTS_APPROVAL' for b in res['blockers']))
if __name__=='__main__':unittest.main(verbosity=2)
