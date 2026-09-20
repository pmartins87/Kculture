#!/usr/bin/env python3
"""Mechanically complete V13C by combining the 72 valid original rows with the
exact four-row rank-14 supplement after immutable source pinning.

No strategic selection is performed here.  The full frozen context key-set is verified
before the original V13C decision rule is applied.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--original",required=True)
    ap.add_argument("--supplement",required=True)
    ap.add_argument("--full-config",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    orig=json.loads(Path(args.original).read_text())
    sup=json.loads(Path(args.supplement).read_text())
    cfg=json.loads(Path(args.full_config).read_text())

    reps=list(cfg.get("representatives") or [])
    seeds=[int(x) for x in cfg.get("seeds") or []]
    seats=[int(x) for x in cfg.get("seats") or []]
    if len(reps)!=19 or seeds!=[78101,78102] or seats!=[0,1]:
        raise RuntimeError("full frozen V13C config identity mismatch")

    # Original run must be exactly the known single-source mechanical failure.
    of=list(orig.get("failures") or [])
    if len(of)!=1:
        raise RuntimeError(f"expected exactly one original failure, got {of}")
    f=of[0]
    if not (
        f.get("phase")=="acquire"
        and int(f.get("rank"))==14
        and f.get("ref")=="tetsutani/demand-preserving-turn-sale-timing"
        and "source SHA drift" in str(f.get("error"))
    ):
        raise RuntimeError(f"unexpected original failure: {f}")
    orows=list(orig.get("rows") or [])
    if len(orows)!=72 or int(orig.get("completed_games") or -1)!=72:
        raise RuntimeError(f"original valid-row count mismatch {len(orows)} / {orig.get('completed_games')}")

    if not sup.get("mechanical_pass"):
        raise RuntimeError(f"supplement mechanically invalid: {sup.get('failures')}")
    srows=list(sup.get("rows") or [])
    if len(srows)!=4:
        raise RuntimeError(f"expected four supplement rows, got {len(srows)}")
    expected_r14="1aa3717b3201997a95920c80cf5612c23f78f8716c7b1084b6a345ca4eae7e4f"
    if any(r.get("main_sha256")!=expected_r14 or int(r.get("rank"))!=14 for r in srows):
        raise RuntimeError("supplement does not contain only frozen rank-14 source")

    rows=orows+srows
    expected={
      (str(r["main_sha256"]),int(seed),int(seat))
      for r in reps for seed in seeds for seat in seats
    }
    actual=[(str(r["main_sha256"]),int(r["seed"]),int(r["seat"])) for r in rows]
    aset=set(actual)
    if len(rows)!=76 or len(aset)!=76:
        raise RuntimeError(f"combined rows not unique/complete: rows={len(rows)} unique={len(aset)}")
    missing=sorted(expected-aset)
    extra=sorted(aset-expected)
    if missing or extra:
        raise RuntimeError(f"combined key-set mismatch missing={missing} extra={extra}")

    hard=[r for r in rows if float(r["score"])<1.0]
    hard_shas=sorted({str(r["main_sha256"]) for r in hard})
    if len(hard)>=4 and len(hard_shas)>=2:
        decision="V13C_CURRENT_FRONTIER_HARD_CONTEXTS_READY"
    elif hard:
        decision="V13C_CURRENT_FRONTIER_HARD_CONTEXTS_NARROW"
    else:
        decision="V13C_LOCAL_FRONTIER_TOO_EASY"

    by_source=[]
    for rep in reps:
        sha=str(rep["main_sha256"])
        rr=[x for x in rows if str(x["main_sha256"])==sha]
        if len(rr)!=4:
            raise RuntimeError(f"source {sha} expected 4 rows, got {len(rr)}")
        by_source.append({
          "rank":int(rep["rank"]),"ref":rep["ref"],"sha":sha,"games":4,
          "wins":sum(x["result"]=="W" for x in rr),
          "losses":sum(x["result"]=="L" for x in rr),
          "ties":sum(x["result"]=="T" for x in rr),
          "score_rate":sum(float(x["score"]) for x in rr)/4.0,
          "mean_margin":sum(float(x["margin"]) for x in rr)/4.0,
        })

    result={
      "schema":"kculture-all3-v13c-current-frontier-hard-context-composite-v1",
      "mechanical_pass":True,
      "decision":decision,
      "expected_games":76,
      "completed_games":76,
      "hard_contexts":len(hard),
      "hard_source_shas":hard_shas,
      "hard_sources":len(hard_shas),
      "by_source":by_source,
      "hard_rows":hard,
      "rows":rows,
      "failures":[],
      "composite_provenance":{
        "original_run":35520875702,
        "original_valid_rows":72,
        "original_known_failure":"rank14 mutable-ref SHA drift",
        "rank14_pin_resolution_run":35523343530,
        "rank14_pinned_handle":"tetsutani/demand-preserving-turn-sale-timing/versions/4",
        "rank14_supplement_rows":4,
        "full_config":args.full_config,
      },
      "strategic_population_changed":False,
      "strategic_gate_changed":False,
      "local_h2h_is_not_hosted_rating_estimator":True,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V13C_COMPOSITE_RESULT",json.dumps({
      "mechanical_pass":True,"decision":decision,"completed_games":76,
      "hard_contexts":len(hard),"hard_sources":len(hard_shas),
      "hard_source_shas":hard_shas,"by_source":by_source
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
