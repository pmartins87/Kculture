"""Aggregate CR036 component-graft variants against exact CR029 control."""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "configs/cr036_rank5_component_graft.json"
OUT = ROOT / "artifacts/cr036_rank5_component_graft"


def load(root: Path) -> dict[int, dict]:
    found = {}
    for p in sorted(root.rglob("variant_*.json")):
        o = json.loads(p.read_text(encoding="utf-8")); vid = int(o["variant_id"])
        if vid in found: raise RuntimeError(f"duplicate variant {vid}")
        found[vid] = o
    return found


def key(r: dict) -> tuple[int,int]:
    return int(r["opponent_rank"]), int(r["seat"])


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--input-dir",default="artifacts/cr036_downloaded"); args=ap.parse_args()
    spec=json.loads(SPEC.read_text(encoding="utf-8")); shards=load(ROOT/args.input_dir); OUT.mkdir(parents=True,exist_ok=True)
    expected={int(v["id"]) for v in spec["variants"]}; missing=sorted(expected-set(shards))
    if missing: raise RuntimeError(f"missing CR036 variants: {missing}")
    control=shards[0]
    if not control.get("mechanical_complete") or len(control.get("rows") or [])!=24: raise RuntimeError("control incomplete")
    base={key(r):r for r in control["rows"]}
    gate=spec["screen_gate"]; reports=[]
    for v in spec["variants"]:
        vid=int(v["id"])
        if vid==0: continue
        s=shards[vid]; rows=s.get("rows") or []; paired=[]
        for r in rows:
            k=key(r)
            if k not in base: raise RuntimeError(f"unknown paired key {k}")
            paired.append((r,base[k]))
        favorable=sum(float(r["score"])>float(b["score"]) for r,b in paired)
        unfavorable=sum(float(r["score"])<float(b["score"]) for r,b in paired)
        score_gain=sum(float(r["score"])-float(b["score"]) for r,b in paired)
        gains=[float(r["delta"])-float(b["delta"]) for r,b in paired]
        mean_gain=statistics.mean(gains) if gains else None
        jesse=[(r,b) for r,b in paired if r["opponent_team"]=="Jesse Bullard"]
        keiz=[(r,b) for r,b in paired if r["opponent_team"]=="keiz"]
        jesse_conv=sum(float(r["score"])!=float(b["score"]) for r,b in jesse)
        kfav=sum(float(r["score"])>float(b["score"]) for r,b in keiz)
        kunfav=sum(float(r["score"])<float(b["score"]) for r,b in keiz)
        mechanical=bool(s.get("mechanical_complete")) and len(rows)==24 and not s.get("errors")
        classifier_ok=int(s.get("classifier_correct") or 0)==24 and int(s.get("classifier_total") or 0)==24
        passed=(mechanical and classifier_ok and score_gain>=float(gate["score_gain_vs_cr029_min"])
                and favorable>=int(gate["favorable_conversions_min"])
                and unfavorable<=int(gate["unfavorable_conversions_max"])
                and mean_gain is not None and mean_gain>float(gate["mean_paired_delta_gain_min_exclusive"])
                and jesse_conv==int(gate["jesse_conversions_required"]))
        reports.append({
            "variant_id":vid,"variant_name":v["name"],"components":v["components"],
            "mechanical_complete":mechanical,"classifier_correct":s.get("classifier_correct"),
            "score_total":s["all"]["score_total"],"control_score_total":control["all"]["score_total"],
            "score_gain_vs_cr029":score_gain,"favorable":favorable,"unfavorable":unfavorable,
            "net":favorable-unfavorable,"mean_paired_delta_gain":mean_gain,
            "worst_paired_delta_gain":min(gains) if gains else None,
            "keiz_favorable":kfav,"keiz_unfavorable":kunfav,"jesse_conversions":jesse_conv,
            "summary":s["all"],"screen_pass":passed,
        })
    reports.sort(key=lambda x:(bool(x["screen_pass"]),float(x["score_gain_vs_cr029"]),int(x["net"]),float(x["mean_paired_delta_gain"] or -1e30)),reverse=True)
    shortlist=[r["variant_id"] for r in reports if r["screen_pass"]]
    decision="CR036_SHORTLIST_READY" if shortlist else "CR036_NO_COMPONENT_GRAFT_PROMOTION"
    out={"experiment":"CR036_RANK5_COMPONENT_GRAFT_V1","decision":decision,"control":control["all"],"shortlist":shortlist,
         "ranking":reports,"gate":gate,"source_scenarios_already_open":True,"fresh_validation_touched":False,
         "held_out_touched":False,"runtime_identity_features":False}
    (OUT/"report.json").write_text(json.dumps(out,indent=2,sort_keys=True),encoding="utf-8")
    compact={"experiment":out["experiment"],"decision":decision,"control":out["control"],"shortlist":shortlist,
             "ranking":[{k:r[k] for k in ("variant_id","variant_name","components","score_gain_vs_cr029","favorable","unfavorable","net","mean_paired_delta_gain","worst_paired_delta_gain","keiz_favorable","keiz_unfavorable","jesse_conversions","screen_pass")} for r in reports],
             "fresh_validation_touched":False,"held_out_touched":False}
    (OUT/"summary.json").write_text(json.dumps(compact,indent=2,sort_keys=True),encoding="utf-8"); print(json.dumps(compact,indent=2,sort_keys=True))

if __name__=="__main__": main()
