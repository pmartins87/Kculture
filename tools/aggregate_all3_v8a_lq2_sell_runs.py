#!/usr/bin/env python3
"""Aggregate V8A residual LQ2 SELL-run census."""
from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    docs=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    failures=[f for d in docs for f in d.get("failures",[])]
    mech=len(docs)==4 and not failures and all(d.get("mechanical_pass") for d in docs)
    states=[s for d in docs for s in d.get("eligible_states",[])]
    contexts_with=len({int(s["index"]) for s in states})
    states.sort(key=lambda x:(-x["distinct_products"],-x["nonempty_sell_orders"],-x["total_sell_qty"],x["index"],x["step"]))
    decision="V8A_MECHANICS_INVALID" if not mech else ("V8A_ORDER_SEARCH_READY" if states else "V8A_NO_ORDER_HEADROOM")
    result={
      "schema":"kculture-v8a-lq2-residual-sell-run-census-v1",
      "mechanical_pass":mech,"decision":decision,
      "eligible_state_count":len(states),"contexts_with_eligible_state":contexts_with,
      "lq2_changed_turns_total":sum(int(d.get("lq2_changed_turns",0)) for d in docs),
      "eligible_states":states,"context_docs":docs,"failures":failures,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V8A_RESULT",json.dumps({
      "decision":decision,"mechanical_pass":mech,
      "eligible_state_count":len(states),"contexts_with_eligible_state":contexts_with,
      "lq2_changed_turns_total":result["lq2_changed_turns_total"],
      "top_states":[{k:x[k] for k in ("index","opponent","seed","seat","step","start","end","distinct_products","nonempty_sell_orders","total_sell_qty","products","quantities")} for x in states[:16]],
      "failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
