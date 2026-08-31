"""CR024 contingency diagnostic: exact structural diff of public top11/top19 tapes.

This tool uses only the two already-known public CR023 source replays.  It does
not run any evaluation seed and therefore cannot touch raw Stage B, adaptive
reserved, or held-out data.  Its purpose is to identify the stable action core
shared by top11/top19 before any consensus/shrinkage policy is designed.
"""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr023_public_tape_preregistered_seeds_v1.json"
ROUTES = ("top11_openloop", "top19_openloop")
COMPONENTS = ("farmer", "hands", "market")


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def download_tape(api: KaggleApi, meta: dict, folder: Path):
    eid = int(meta["episode_id"]); seat = int(meta["source_seat"])
    api.competition_episode_replay(eid, path=str(folder), quiet=True)
    p = folder / f"episode-{eid}-replay.json"
    replay = json.loads(p.read_text(encoding="utf-8"))
    steps = replay.get("steps") or []
    if len(steps) < 720: raise RuntimeError(f"short replay {eid}: {len(steps)}")
    tape=[]
    for t in range(719):
        frame=steps[t+1][seat]
        action=frame.get("action") if isinstance(frame,dict) else None
        tape.append(copy.deepcopy(action or {}))
    return tape


def op_signature(action: dict, component: str):
    value=action.get(component)
    if component == "farmer":
        if isinstance(value,list) and value: return str(value[0])
        return "NONE"
    rows=value or []
    out=[]
    for row in rows:
        if isinstance(row,list) and row: out.append(str(row[0]))
        else: out.append(type(row).__name__)
    return tuple(out)


def main():
    cfg=json.loads(CFG.read_text(encoding="utf-8"))
    api=KaggleApi(); api.authenticate()
    with tempfile.TemporaryDirectory(prefix="cr024-consensus-") as td:
        tapes={r:download_tape(api,cfg["routes"][r],Path(td)) for r in ROUTES}

    a=tapes[ROUTES[0]]; b=tapes[ROUTES[1]]
    if len(a)!=719 or len(b)!=719: raise RuntimeError("tape length")

    exact_same=[]; exact_diff=[]
    component_same={k:[] for k in COMPONENTS}; component_diff={k:[] for k in COMPONENTS}
    diff_rows=[]; phase=defaultdict(lambda:{"steps":0,"same":0,"diff":0})
    operation_pairs={k:Counter() for k in COMPONENTS}

    for t,(x,y) in enumerate(zip(a,b)):
        same=canonical(x)==canonical(y)
        (exact_same if same else exact_diff).append(t)
        block=f"{(t//24)*24:03d}-{min(718,(t//24)*24+23):03d}"
        phase[block]["steps"]+=1; phase[block]["same" if same else "diff"]+=1
        changed=[]
        for c in COMPONENTS:
            xv=x.get(c); yv=y.get(c)
            cs=canonical(xv)==canonical(yv)
            (component_same[c] if cs else component_diff[c]).append(t)
            if not cs:
                changed.append(c)
                operation_pairs[c][(str(op_signature(x,c)),str(op_signature(y,c)))] += 1
        if not same:
            diff_rows.append({
                "step":t,
                "changed_components":changed,
                "top11":{c:x.get(c) for c in changed},
                "top19":{c:y.get(c) for c in changed},
            })

    # Consecutive disagreement runs are especially important because a long run
    # implies state coupling; isolated action substitutions are much safer to
    # consider for shrinkage than wholesale route splicing.
    runs=[]
    if exact_diff:
        start=prev=exact_diff[0]
        for t in exact_diff[1:]:
            if t==prev+1: prev=t; continue
            runs.append([start,prev,prev-start+1]); start=prev=t
        runs.append([start,prev,prev-start+1])

    payload={
        "experiment":"CR024_CONSENSUS_TAPE_DIFF",
        "routes":{
            r:{
                "episode_id":int(cfg["routes"][r]["episode_id"]),
                "source_seat":int(cfg["routes"][r]["source_seat"]),
                "canonical_tape_sha256":sha_text(canonical(tapes[r])),
            } for r in ROUTES
        },
        "evaluation_seeds_touched":False,
        "stage_b_touched":False,
        "adaptive_reserved_touched":False,
        "held_out_touched":False,
        "step_count":719,
        "exact_same_count":len(exact_same),
        "exact_diff_count":len(exact_diff),
        "exact_same_fraction":len(exact_same)/719.0,
        "component_summary":{
            c:{"same":len(component_same[c]),"diff":len(component_diff[c]),"same_fraction":len(component_same[c])/719.0}
            for c in COMPONENTS
        },
        "disagreement_runs":runs,
        "max_disagreement_run":max((r[2] for r in runs),default=0),
        "phase_summary":dict(sorted(phase.items())),
        "operation_pair_counts":{
            c:[{"top11_signature":k[0],"top19_signature":k[1],"count":n} for k,n in operation_pairs[c].most_common()]
            for c in COMPONENTS
        },
        "diff_rows":diff_rows,
        "policy_note":"Diagnostic only. Do not splice routes until state-coupling pattern is understood.",
    }
    out=ROOT/"artifacts/cr024_consensus_tape_diff/report.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps({
        "exact_same_count":payload["exact_same_count"],
        "exact_diff_count":payload["exact_diff_count"],
        "exact_same_fraction":payload["exact_same_fraction"],
        "component_summary":payload["component_summary"],
        "max_disagreement_run":payload["max_disagreement_run"],
        "disagreement_run_count":len(runs),
    },indent=2,sort_keys=True))


if __name__=="__main__": main()
