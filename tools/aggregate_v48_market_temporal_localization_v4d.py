#!/usr/bin/env python3
"""Aggregate V4D temporal-localization shards without runtime dependencies."""
from __future__ import annotations
import argparse,json,statistics
from collections import Counter,defaultdict
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    files=sorted(Path(args.input_dir).rglob("*.json"))
    shards=[json.loads(p.read_text()) for p in files]
    rows=[]; failures=[]
    for s in shards:
        rows.extend(s.get("rows",[])); failures.extend(s.get("failures",[]))
    mech=(len(shards)==6 and len(rows)==12 and not failures and all(s.get("mechanical_pass") for s in shards))
    by_label=defaultdict(list)
    for r in rows:
        for c in r["candidates"]:
            by_label[c["label"]].append(c)
    summary={}
    for label,cs in by_label.items():
        summary[label]={
            "contexts":len(cs),
            "reproduced_contexts":sum(bool(c["reproduces_headroom"]) for c in cs),
            "score_rate":statistics.mean(float(c["score"]) for c in cs),
            "mean_score_delta":statistics.mean(float(c["score_delta"]) for c in cs),
            "mean_margin_delta":statistics.mean(float(c["margin_delta"]) for c in cs),
            "mean_applied_market_turns":statistics.mean(int(c["applied_market_turns"]) for c in cs),
            "planned_steps":int(cs[0]["planned_steps"]),
            "start":int(cs[0]["start"]),"end":int(cs[0]["end"]),
            "physical_fallback_turns":sum(int(c["physical_fallback_turns"]) for c in cs),
        }
    ranked=sorted(summary.items(),key=lambda kv:(
        kv[1]["reproduced_contexts"],
        kv[1]["score_rate"],
        -kv[1]["planned_steps"],
        -kv[1]["mean_applied_market_turns"],
        kv[1]["start"],
    ),reverse=True)
    minimal_labels=Counter(
        r["minimal_reproducer"]["label"]
        for r in rows if r.get("minimal_reproducer")
    )
    no_reproducer=sum(r.get("minimal_reproducer") is None for r in rows)
    full_repro=[(k,v) for k,v in summary.items() if v["reproduced_contexts"]==12]
    full_repro.sort(key=lambda kv:(kv[1]["planned_steps"],kv[1]["mean_applied_market_turns"],-kv[1]["start"]))
    if mech and full_repro:
        decision="V48_V4D_GLOBAL_INTERVAL_FOUND"
        global_min=full_repro[0]
    elif mech and any(v["reproduced_contexts"]>=6 for v in summary.values()):
        decision="V48_V4D_PARTIAL_LOCALIZATION"
        global_min=None
    elif mech:
        decision="V48_V4D_HEADROOM_DISTRIBUTED_NO_LOCAL_INTERVAL"
        global_min=None
    else:
        decision="V48_V4D_MECHANICS_INVALID"
        global_min=None
    result={
        "schema":"kculture-v48-market-temporal-localization-v4d",
        "mechanical_pass":mech,"shards":len(shards),"contexts":len(rows),
        "decision":decision,"summary_by_label":summary,"ranking":ranked,
        "minimal_reproducer_label_counts":dict(minimal_labels),
        "contexts_without_reproducer":no_reproducer,
        "global_minimal_full_reproducer":global_min,
        "rows":rows,"failures":failures,
        "automatic_kaggle_submission":False,
    }
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V48_V4D_RESULT",json.dumps({
        "decision":decision,"mechanical_pass":mech,
        "minimal_reproducer_label_counts":dict(minimal_labels),
        "contexts_without_reproducer":no_reproducer,
        "global_minimal_full_reproducer":global_min,
        "top3":ranked[:3]
    },sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)

if __name__=="__main__":
    main()
