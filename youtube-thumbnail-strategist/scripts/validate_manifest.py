#!/usr/bin/env python3
"""Validate the thumbnail manifest using Python's standard library only."""
import json, sys
from pathlib import Path

VALID_STATES = {"planned", "generated", "qa_passed", "approved"}
VALID_QA = {"pass", "fail", "not_tested"}
VALID_TYPES = {"authentic", "licensed", "illustration"}

def validate(path):
    obj=json.loads(path.read_text(encoding="utf-8"))
    errors=[]
    def check(test, message):
        if not test: errors.append(message)
    check(obj.get("schema_version")=="1.0", "schema_version must be 1.0")
    check(bool(obj.get("channel_name")), "channel_name missing")
    check(bool(obj.get("video_title")), "video_title missing")
    state=obj.get("status")
    check(state in VALID_STATES, "invalid status")
    candidates=obj.get("candidates",[])
    check(isinstance(candidates,list) and len(candidates)==3, "exactly 3 candidates required")
    if not isinstance(candidates,list): candidates=[]
    ids=[c.get("id") for c in candidates if isinstance(c,dict)]
    check(len(ids) == 3 and all(ids.count(label) == 1 for label in "ABC"), "candidate IDs must be A, B, C")
    for c in candidates:
        if not isinstance(c,dict): errors.append("non-dictionary candidate");continue
        name=c.get("id","?")
        for field in ("type","hook","thumbnail_text","paired_title","main_subject","layout","prompt","source_reference"):
            check(isinstance(c.get(field),str) and bool(c.get(field).strip()), f"{name}: missing {field}")
        score=c.get("score")
        check(isinstance(score,(int,float)) and not isinstance(score,bool) and 0<=score<=100, f"{name}: score invalid")
        check(c.get("source_type") in VALID_TYPES, f"{name}: source_type invalid")
        check(c.get("qa_status") in VALID_QA, f"{name}: qa_status invalid")
        fn=c.get("image_file")
        if fn and not Path(fn).is_absolute(): fn=str(path.parent / fn)
        if fn: check(Path(fn).is_file(), f"{name}: image file not found {fn}")
        if state in ("qa_passed","approved") and c.get("id")==obj.get("selected_candidate"):
            check(c.get("qa_status")=="pass", f"{name}: selected image QA must pass")
    selected=obj.get("selected_candidate")
    check(selected in (None,"A","B","C"), "selected_candidate invalid")
    if state!="planned" and selected in ("A","B","C"):
        match=next((c for c in candidates if isinstance(c,dict) and c.get("id")==selected), {})
        check(bool(match.get("image_file")), "selected image required for generated+ state")
    publishing=obj.get("publishing",{})
    check(isinstance(publishing,dict) and isinstance(publishing.get("authorized"),bool), "publishing.authorized must be boolean")
    if state in ("qa_passed", "approved"):
        check(selected in ("A", "B", "C"), "QA-passed and approved states require a selected candidate")
    return errors

if __name__=="__main__":
    if len(sys.argv)!=2:
        print("Usage: python validate_manifest.py path/to/thumbnail_manifest.json");sys.exit(2)
    try: issues=validate(Path(sys.argv[1]))
    except Exception as e: print(f"FAIL: {e}");sys.exit(2)
    if issues:
        print("FAIL:\n"+"\n".join("- "+v for v in issues));sys.exit(1)
    print("PASS: manifest structure and referenced files validated")
