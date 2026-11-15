#!/usr/bin/env python3
"""Validate the thumbnail manifest using Python's standard library only."""
import json, sys
from pathlib import Path

VALID_STATES = {"planned", "generated", "qa_passed", "approved"}
VALID_QA = {"pass", "fail", "not_tested"}
VALID_TYPES = {"authentic_reference", "licensed_reference", "illustration"}
VALID_KINDS = {"long", "short"}

def validate(path):
    obj=json.loads(path.read_text(encoding="utf-8"))
    errors=[]
    def check(test, message):
        if not test: errors.append(message)
    def file_exists(fn):
        if not Path(fn).is_absolute(): fn=str(path.parent / fn)
        return Path(fn).is_file(), fn
    check(obj.get("schema_version")=="2.0", "schema_version must be 2.0")
    check(bool(obj.get("channel_name")), "channel_name missing")
    check(bool(obj.get("video_title")), "video_title missing")
    kind=obj.get("video_kind")
    check(kind in VALID_KINDS, "video_kind must be long or short")
    generator=obj.get("generator")
    check(isinstance(generator,dict) and generator.get("agent")=="Codex" and generator.get("model")=="Images 2.6",
          "generator must be Codex / Images 2.6")
    state=obj.get("status")
    check(state in VALID_STATES, "invalid status")
    candidates=obj.get("candidates",[])
    if not isinstance(candidates,list):
        errors.append("candidates must be a list"); candidates=[]
    ids=[c.get("id") for c in candidates if isinstance(c,dict)]
    if kind=="short":
        check(1<=len(ids)<=3 and ids==list("ABC"[:len(ids)]), "short needs 1-3 candidates with IDs A, B, C in order")
    else:
        check(len(ids)==3 and all(ids.count(label)==1 for label in "ABC"), "long needs exactly 3 candidates A, B, C")
    for c in candidates:
        if not isinstance(c,dict): errors.append("non-dictionary candidate");continue
        name=c.get("id","?")
        for field in ("type","hook","thumbnail_text","paired_title","main_subject","layout","prompt","source_reference"):
            check(isinstance(c.get(field),str) and bool(c.get(field).strip()), f"{name}: missing {field}")
        score=c.get("score")
        check(isinstance(score,(int,float)) and not isinstance(score,bool) and 0<=score<=100, f"{name}: score invalid")
        check(c.get("source_type") in VALID_TYPES, f"{name}: source_type invalid")
        check(c.get("qa_status") in VALID_QA, f"{name}: qa_status invalid")
        attempts=c.get("attempts",0)
        check(isinstance(attempts,int) and not isinstance(attempts,bool) and 0<=attempts<=3, f"{name}: attempts must be 0-3")
        fn=c.get("image_file")
        if fn:
            ok,full=file_exists(fn)
            check(ok, f"{name}: image file not found {full}")
        if state in ("qa_passed","approved") and c.get("id")==obj.get("selected_candidate"):
            check(c.get("qa_status")=="pass", f"{name}: selected image QA must pass")
    selected=obj.get("selected_candidate")
    check(selected is None or selected in ids, "selected_candidate invalid")
    if state!="planned" and selected in ids:
        match=next((c for c in candidates if isinstance(c,dict) and c.get("id")==selected), {})
        check(bool(match.get("image_file")), "selected image required for generated+ state")
    fb=obj.get("facebook_image")
    check(isinstance(fb,dict), "facebook_image missing")
    if isinstance(fb,dict):
        check(fb.get("qa_status") in VALID_QA, "facebook_image: qa_status invalid")
        check(isinstance(fb.get("thumbnail_text"),str) and bool(fb.get("thumbnail_text").strip()), "facebook_image: missing thumbnail_text")
        if fb.get("file"):
            ok,full=file_exists(fb["file"])
            check(ok, f"facebook_image: file not found {full}")
            expected="1200x630" if kind=="long" else "1080x1350"
            check(expected in Path(fb["file"]).name, f"facebook_image: {kind} file name must contain {expected}")
        if state in ("qa_passed","approved"):
            check(bool(fb.get("file")) and fb.get("qa_status")=="pass", "facebook_image must exist and pass QA for qa_passed+")
    publishing=obj.get("publishing",{})
    check(isinstance(publishing,dict) and isinstance(publishing.get("authorized"),bool), "publishing.authorized must be boolean")
    if state in ("qa_passed", "approved"):
        check(selected in ids, "QA-passed and approved states require a selected candidate")
    return errors

if __name__=="__main__":
    if len(sys.argv)!=2:
        print("Usage: python validate_manifest.py path/to/thumbnail_manifest.json");sys.exit(2)
    try: issues=validate(Path(sys.argv[1]))
    except Exception as e: print(f"FAIL: {e}");sys.exit(2)
    if issues:
        print("FAIL:\n"+"\n".join("- "+v for v in issues));sys.exit(1)
    print("PASS: manifest structure and referenced files validated")
