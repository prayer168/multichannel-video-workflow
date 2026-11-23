#!/usr/bin/env python3
"""V1.3 CLI, integrity, recovery, audit and archive regression tests."""
import csv,hashlib,json,shutil,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from workflow_v13 import init_project,stage_complete,create_checkpoint,restore,pack,check_locked,WorkflowError,load
from audit_v13 import audit
from verify_zip_v13 import verify
DEMO=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else None
NEMO=Path(sys.argv[2]).resolve() if len(sys.argv)>2 else None
sys.argv=sys.argv[:1]

class V13Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if not DEMO or not DEMO.exists() or not NEMO or not NEMO.exists():raise unittest.SkipTest('Provide demo and Nemo test project paths')
 def test_generic_A_to_C3_passes(self):
  r=audit(DEMO,'handoff')
  self.assertEqual('PASS_WITH_WARNINGS',r['status'],r['blockers']);self.assertEqual('GENERIC_V13',r['metrics']['mode']);self.assertEqual(3,r['metrics']['shots'])
  s=load(DEMO/'workflow_state.json')
  self.assertTrue(all(s['phase_status'][p]=='COMPLETE' for p in ('A','B','C1','C2','C2_5','C3')))
  self.assertTrue(s['handoff_verified']);self.assertFalse(s['official_agent_e2e_verified'])
 def test_generic_production_and_release_block(self):
  for gate in ('production','release'):
   r=audit(DEMO,gate);self.assertEqual('BLOCKED',r['status']);self.assertTrue(len(r['blockers'])>=2)
 def test_nemo_108_16_92_no_source_overwrite(self):
  r=audit(NEMO,'handoff');self.assertEqual('PASS_WITH_WARNINGS',r['status'],r['blockers']);self.assertEqual(108,r['metrics']['shots'])
  self.assertEqual(16,r['metrics']['original_prompts_preserved']);self.assertEqual(92,r['metrics']['prompts_filled_v12']);self.assertEqual(5,r['metrics']['original_files_locked']);self.assertEqual([],check_locked(NEMO)[:0])
 def test_nemo_production_is_blocked(self):
  self.assertEqual('BLOCKED',audit(NEMO,'production')['status'])
 def test_phase_order_rejects_skip(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'fresh';init_project(p,'fresh_science','全新測試')
   with self.assertRaises(WorkflowError):stage_complete(p,'B','script/script.md')
 def test_modified_approved_evidence_is_detected(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'p';shutil.copytree(DEMO,p)
   (p/'script/script.md').write_text((p/'script/script.md').read_text()+'\nDrift!\n')
   r=audit(p,'handoff');self.assertEqual('BLOCKED',r['status'])
   self.assertIn('PHASE_EVIDENCE_DRIFT',[x['code'] for x in r['blockers']])
 def test_checkpoint_dry_run_and_safe_restore(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'p';shutil.copytree(DEMO,p)
   original=(p/'script/script.md').read_bytes();(p/'script/script.md').write_bytes(original+b'\nBAD EDIT\n')
   checkpoint=load(p/'workflow_state.json')['latest_checkpoint'];dry=restore(p,checkpoint,False);self.assertIn('script/script.md',dry['modified'])
   self.assertNotEqual((p/'script/script.md').read_bytes(),original)
   done=restore(p,checkpoint,True)
   self.assertEqual((p/'script/script.md').read_bytes(),original)
   self.assertEqual('PASS_WITH_WARNINGS',audit(p,'handoff')['status'])
 def test_checkpoint_corruption_blocks_restore(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'p';shutil.copytree(DEMO,p)
   checkpoint=load(p/'workflow_state.json')['latest_checkpoint'];f=p/'state/checkpoints'/checkpoint/'files/shots.csv';f.write_bytes(f.read_bytes()+b'\nCORRUPT\n')
   with self.assertRaises(WorkflowError):restore(p,checkpoint,True)
 def test_nemo_original_changed_blocks_all(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'n';shutil.copytree(NEMO,p)
   f=p/'original/point_nemo_script_v1.md';f.write_bytes(f.read_bytes()+b'\nCHANGED\n')
   self.assertEqual('BLOCKED',audit(p,'handoff')['status'])
   with self.assertRaises(WorkflowError):restore(p,'cp_0001',True)
 def test_falsified_rights_claim_is_blocked(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'p';shutil.copytree(DEMO,p)
   f=p/'assets/rights_decisions.csv'
   with f.open(encoding='utf-8-sig',newline='') as r:reader=csv.DictReader(r);cols=reader.fieldnames;rows=list(reader)
   rows[0]['decision']='APPROVED'
   with f.open('w',encoding='utf-8-sig',newline='') as r:w=csv.DictWriter(r,fieldnames=cols);w.writeheader();w.writerows(rows)
   r=audit(p,'handoff');self.assertEqual('BLOCKED',r['status'])
   self.assertIn('FALSE_RIGHTS_APPROVAL',[x['code'] for x in r['blockers']])
 def test_zip_rechecks_after_extract(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'p';shutil.copytree(DEMO,p)
   z=Path(td)/'demo.zip';data=pack(p,z)
   result=verify(z)
   self.assertTrue(result['sha256_verified']);self.assertEqual(0,result['handoff_exit_code']);self.assertGreater(data['files'],15)
 def test_smoke_video_frames_and_no_approval(self):
  evidence=load(DEMO/'production/poc/out/poc_qa.json')
  p=DEMO/evidence['video'];self.assertTrue(p.is_file());self.assertEqual(600,evidence['frames']);self.assertEqual(20,evidence['duration_seconds'])
  self.assertFalse(evidence['publishable']);self.assertFalse(evidence['external_claude_or_codex_used'])
  self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),evidence['video_sha256'])
 def test_independent_agent_contract_present(self):
  for p in (DEMO,NEMO):
   for rel in ('CLAUDE.md','AGENTS.md'):
    s=(p/rel).read_text(encoding='utf-8')
    self.assertIn('audit_v13.py',s, f'{p}/{rel}')
   self.assertTrue((p/'scripts/audit_v13.py').exists())

if __name__=='__main__':unittest.main(verbosity=2)
