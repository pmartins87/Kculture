#!/usr/bin/env python3
"""Aggregate V9B frozen one-turn structural category branches."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path
CATS=("INSERT_DROP","QTY_UP")
def summ(rows):
    if not rows:return {}
    flips=[r for r in rows if r["loss_to_win"]]
    pos=[r for r in rows if float(r["margin_delta"])>0]
    return {
      "branches":len(rows),
      "mean_margin_delta":statistics.fmean(float(r["margin_delta"]) for r in rows),
      "positive_margin_states":len(pos),
      "positive_margin_contexts":sorted({int(r["index"]) for r in pos}),
      "loss_to_win_flips":len(flips),
      "flip_contexts":sorted({int(r["index"]) for r in flips}),
      "top_positive":sorted(
        [{"state_id":r["state_id"],"index":r["index"],"turn":r["turn"],"margin_delta":r["margin_delta"],
          "base_margin":r["base_margin"],"treatment_margin":r["treatment_margin"],"loss_to_win":r["loss_to_win"]} for r in rows],
        key=lambda x:float(x["margin_delta"]),reverse=True)[:8],
    }
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    docs=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    failures=[d.get("failure") for d in docs if d.get("failure")]
    rows=[d["row"] for d in docs if d.get("row") is not None]
    mech=len(docs)==16 and len(rows)==16 and not failures and all(d.get("mechanical_pass") for d in docs)
    by={c:summ([r for r in rows if r["category"]==c]) for c in CATS}
    repeat=[c for c in CATS if len(by[c].get("flip_contexts",[]))>=2]
    narrow=[c for c in CATS if by[c].get("loss_to_win_flips",0)>=1 and len(by[c].get("positive_margin_contexts",[]))>=2]
    total_flips=sum(by[c].get("loss_to_win_flips",0) for c in CATS)
    if not mech:decision="V9B_MECHANICS_INVALID"
    elif repeat:decision="V9B_CATEGORY_WL_REPEATABLE"
    elif narrow:decision="V9B_CATEGORY_WL_NARROW"
    elif total_flips==0:decision="V9B_NO_WL_HEADROOM_CLOSE_ONE_TURN_STRUCTURAL"
    else:decision="V9B_SINGLE_FLIP_UNSUPPORTED"
    result={"schema":"kculture-v9b-causal-structural-isolation-v1","mechanical_pass":mech,
      "decision":decision,"advancing_categories":repeat or narrow,"by_category":by,
      "rows":rows,"failures":failures,"automatic_kaggle_submission":False}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V9B_RESULT",json.dumps({"decision":decision,"mechanical_pass":mech,
      "advancing_categories":result["advancing_categories"],"by_category":by,"failures":len(failures)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)
if __name__=="__main__":main()
