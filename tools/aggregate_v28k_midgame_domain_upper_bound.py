#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

MODES=("BASE","MARKET_WINDOW","PHYSICAL_WINDOW","FULL_WINDOW")

def summarize(rows):
    wins=[r for r in rows if float(r["treatment_score"])==1.0]
    ties=[r for r in rows if float(r["treatment_score"])==0.5]
    md=[float(r["margin_delta"]) for r in rows]
    return {
      "contexts":len(rows),
      "loss_to_win_flips":len(wins),
      "loss_to_tie_flips":len(ties),
      "still_losses":sum(float(r["treatment_score"])==0.0 for r in rows),
      "mean_score_delta":statistics.fmean(float(r["score_delta"]) for r in rows),
      "mean_margin_delta":statistics.fmean(md),
      "median_margin_delta":statistics.median(md),
      "positive_margin_delta_contexts":sum(x>0 for x in md),
      "negative_margin_delta_contexts":sum(x<0 for x in md),
      "flip_source_shas":sorted({str(r["main_sha256"]) for r in wins}),
      "flip_sources":len({str(r["main_sha256"]) for r in wins}),
      "flip_seeds":sorted({int(r["seed"]) for r in wins}),
      "flip_seed_count":len({int(r["seed"]) for r in wins}),
      "flip_seats":sorted({int(r["seat"]) for r in wins}),
    }

def domain_pass(s):
    return bool(s) and s["loss_to_win_flips"]>=4 and s["flip_sources"]>=2 and s["flip_seed_count"]>=2 and s["mean_score_delta"]>0

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    docs=[]
    for p in sorted(Path(a.input_dir).rglob("*.json")):
        try:d=json.loads(p.read_text())
        except Exception:continue
        if d.get("schema")=="kculture-v28k-midgame-domain-upper-bound-shard-v1":docs.append(d)
    rows=[r for d in docs for r in d.get("rows",[])]
    fail=[x for d in docs for x in d.get("failures",[])]
    expected={(str(r["main_sha256"]),int(r["seed"]),int(r["seat"]),m)
              for r in rows if r["mode"]=="BASE" for m in MODES}
    actual={(str(r["main_sha256"]),int(r["seed"]),int(r["seat"]),str(r["mode"])) for r in rows}
    mech=(len(docs)==4 and all(bool(d.get("mechanical_pass")) for d in docs) and not fail
          and all(bool(d.get("immutable_snapshot_used")) and not bool(d.get("live_kaggle_reacquisition_used")) for d in docs)
          and len({(str(r["main_sha256"]),int(r["seed"]),int(r["seat"])) for r in rows if r["mode"]=="BASE"})==66
          and len(rows)==264 and actual==expected)

    by={m:summarize([r for r in rows if r["mode"]==m]) for m in MODES}
    market=domain_pass(by["MARKET_WINDOW"]);physical=domain_pass(by["PHYSICAL_WINDOW"]);full=domain_pass(by["FULL_WINDOW"])

    # interaction-exclusive = FULL wins, neither single-domain mode wins
    ctx={}
    for r in rows:
        key=(str(r["main_sha256"]),int(r["seed"]),int(r["seat"]))
        ctx.setdefault(key,{})[str(r["mode"])]=r
    ix=[]
    if mech:
        for key,v in ctx.items():
            if (float(v["FULL_WINDOW"]["treatment_score"])==1.0
                and float(v["MARKET_WINDOW"]["treatment_score"])<1.0
                and float(v["PHYSICAL_WINDOW"]["treatment_score"])<1.0):
                ix.append({"main_sha256":key[0],"seed":key[1],"seat":key[2],
                           "full_margin":float(v["FULL_WINDOW"]["treatment_margin"]),
                           "market_score":float(v["MARKET_WINDOW"]["treatment_score"]),
                           "physical_score":float(v["PHYSICAL_WINDOW"]["treatment_score"])})

    if not mech:decision="V28K_MECHANICS_INVALID"
    elif market and not physical:decision="V28K_MARKET_WINDOW_HEADROOM"
    elif physical and not market:decision="V28K_PHYSICAL_WINDOW_HEADROOM"
    elif market and physical:decision="V28K_BOTH_DOMAINS_WINDOW_HEADROOM"
    elif full:decision="V28K_CROSS_DOMAIN_WINDOW_INTERACTION_HEADROOM"
    else:decision="V28K_NO_MIDGAME_WINDOW_WL_HEADROOM"

    out={"schema":"kculture-v28k-midgame-domain-upper-bound-v1","mechanical_pass":mech,
         "decision":decision,"hard_contexts":66,"window":[384,479],
         "by_mode":by,"market_pass":market,"physical_pass":physical,"full_pass":full,
         "interaction_exclusive_contexts":len(ix),
         "interaction_exclusive_sources":len({x["main_sha256"] for x in ix}),
         "interaction_exclusive_seeds":len({x["seed"] for x in ix}),
         "interaction_exclusive_rows":ix,
         "rows":rows,"failures":fail,"automatic_kaggle_submission":False}
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V28K_RESULT",json.dumps({"mechanical_pass":mech,"decision":decision,"by_mode":by,
          "market_pass":market,"physical_pass":physical,"full_pass":full,
          "interaction_exclusive_contexts":len(ix),"interaction_exclusive_sources":out["interaction_exclusive_sources"],
          "interaction_exclusive_seeds":out["interaction_exclusive_seeds"],"failures":len(fail)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":
    main()
