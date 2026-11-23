#!/usr/bin/env python3
"""Offline verification of BlackBear v1.3 C3 export (safe paths, SHA256, gate)."""
import argparse,hashlib,json,sys,tempfile,zipfile,subprocess
from pathlib import Path,PurePosixPath

def verify(path,run_audit=True):
 path=Path(path);assert path.is_file(),path
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None,'corrupted zip'
  names=z.namelist()
  assert 'HANDOFF_CHECKSUMS.json' in names,'checksums missing'
  for name in names:
   rel=PurePosixPath(name)
   assert not rel.is_absolute() and all(x!='..' for x in rel.parts) and '\\' not in name,'unsafe zip entry: '+name
  data=json.loads(z.read('HANDOFF_CHECKSUMS.json'));expected=data['files']
  assert len(names)==len(set(names)),'duplicate zip members'
  assert set(names)==set(expected)|{'HANDOFF_CHECKSUMS.json'},'zip manifest unexpected/omitted files'
  for rel,sig in expected.items():assert hashlib.sha256(z.read(rel)).hexdigest()==sig,rel
  stat={'zip':str(path),'skill_version':data.get('skill_version'),'project_slug':data.get('project_slug'),'files_verified':len(expected),'zip_hash_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'sha256_verified':True}
  if run_audit:
   with tempfile.TemporaryDirectory() as td:
    z.extractall(td)
    audit=Path(td)/'scripts/audit_v13.py';assert audit.exists(),'portable audit script missing'
    p=subprocess.run([sys.executable,str(audit),td,'--gate','handoff'],capture_output=True,text=True)
    stat['handoff_exit_code']=p.returncode;stat['handoff_stdout']=p.stdout.strip();stat['handoff_stderr']=p.stderr[-500:]
    assert p.returncode==0,'handoff gate blocked after ZIP extraction'
 return stat

def main():
 parser=argparse.ArgumentParser();parser.add_argument('zip');args=parser.parse_args()
 try:print(json.dumps(verify(args.zip),ensure_ascii=False,indent=2))
 except Exception as e:print('VERIFY_ERROR:',repr(e),file=sys.stderr);return 2
 return 0
if __name__=='__main__':sys.exit(main())
