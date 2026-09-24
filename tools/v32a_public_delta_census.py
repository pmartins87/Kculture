#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--old",required=True);ap.add_argument("--new",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
    old=json.loads((Path(a.old)/"MANIFEST.json").read_text());new=json.loads((Path(a.new)/"MANIFEST.json").read_text())
    oldsha={str(s["sha"]) for s in old["sources"]}
    newc=[s for s in new["sources"] if str(s["sha"]) not in oldsha]
    out={"schema":"kculture-v32a-public-delta-v1","old_unique":len(oldsha),"new_snapshot_unique":len(new["sources"]),
         "new_candidates":[{"sha":str(s["sha"]),"ref":str(s["representative_ref"]),"rank":int(s["representative_rank"]),"path":str(s["path"])} for s in newc],
         "new_candidate_count":len(newc)}
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V32A_DELTA",json.dumps(out,sort_keys=True))
if __name__=="__main__":main()
