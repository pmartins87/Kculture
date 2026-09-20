#!/usr/bin/env python3
"""V13A read-only current Top-30 public frontier drift census."""
from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from tools.kaggle_meta_scout_cli import csv_rows,normkey

def ref_value(row):
    for k,v in row.items():
        if normkey(k)=="ref" and str(v).strip():
            return str(v).strip()
    # Kaggle kernels list normally puts ref first; tolerate renamed first column.
    for _k,v in row.items():
        s=str(v or "").strip()
        if "/" in s and " " not in s:
            return s
    return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--frozen",default="data/programme_teacher/2026-09-18/PROGRAMME_CORPUS.json")
    ap.add_argument("--out",required=True)
    ap.add_argument("--raw",required=True)
    args=ap.parse_args()

    cmd=["kaggle","kernels","list","--competition","kaggriculture","--sort-by","scoreDescending","--page-size","100","-v"]
    p=subprocess.run(cmd,text=True,capture_output=True,check=False)
    raw=Path(args.raw);raw.parent.mkdir(parents=True,exist_ok=True)
    raw.write_text(p.stdout,encoding="utf-8")
    if p.returncode!=0:
        result={"schema":"kculture-v13a-current-top30-drift-v1","mechanical_pass":False,
                "decision":"V13A_MECHANICS_INVALID","returncode":p.returncode,
                "stderr":p.stderr[-4000:],"automatic_kaggle_submission":False}
        Path(args.out).parent.mkdir(parents=True,exist_ok=True)
        Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print("V13A_RESULT",json.dumps(result,sort_keys=True));raise SystemExit(2)

    rows=csv_rows(p.stdout)
    refs=[]
    seen=set()
    for row in rows:
        r=ref_value(row)
        if r and r not in seen:
            seen.add(r);refs.append(r)
        if len(refs)>=30:break

    frozen=json.loads((ROOT/args.frozen).read_text())
    fentries=frozen.get("entries") or []
    old=[str(x["ref"]) for x in sorted(fentries,key=lambda x:int(x["rank"]))]
    fmap={str(x["ref"]):x for x in fentries}
    old_rank={r:i+1 for i,r in enumerate(old)}
    cur_rank={r:i+1 for i,r in enumerate(refs)}
    overlap=[r for r in refs if r in old_rank]
    entrants=[r for r in refs if r not in old_rank]
    dropped=[r for r in old if r not in cur_rank]
    displacements=[{
      "ref":r,"old_rank":old_rank[r],"current_rank":cur_rank[r],
      "delta_current_minus_old":cur_rank[r]-old_rank[r],
      "frozen_source_sha256":fmap[r].get("source_sha256")
    } for r in overlap]
    known_source=[r for r in refs if r in fmap and fmap[r].get("source_sha256")]
    unknown=[r for r in refs if r not in fmap or not fmap[r].get("source_sha256")]

    mech=len(refs)==30
    if not mech:
        decision="V13A_MECHANICS_INVALID"
    elif len(overlap)>=24 and len(unknown)<=6:
        decision="V13A_FRONTIER_STABLE_INCREMENTAL_REFRESH"
    elif len(overlap)>=15:
        decision="V13A_FRONTIER_MODERATE_DRIFT_REFRESH_ALL_CURRENT"
    else:
        decision="V13A_FRONTIER_HIGH_DRIFT_REBUILD"

    result={
      "schema":"kculture-v13a-current-top30-drift-v1",
      "mechanical_pass":mech,
      "decision":decision,
      "current_top30":refs,
      "frozen_top30":old[:30],
      "overlap_count":len(overlap),
      "overlap_refs":overlap,
      "new_current_refs":entrants,
      "dropped_frozen_refs":dropped,
      "known_frozen_source_count":len(known_source),
      "unknown_source_identity_count":len(unknown),
      "unknown_source_identity_refs":unknown,
      "rank_displacements":displacements,
      "cli_rows_parsed":len(rows),
      "automatic_kaggle_submission":False,
      "third_party_code_executed":False,
    }
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V13A_RESULT",json.dumps({
      "decision":decision,"mechanical_pass":mech,
      "overlap_count":len(overlap),
      "new_current_refs":entrants,
      "dropped_frozen_refs":dropped,
      "unknown_source_identity_count":len(unknown),
      "current_top30":refs
    },sort_keys=True))
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
