"""Run one frozen CR028 recent-top variant on fresh direct/reactive games."""
from __future__ import annotations

import argparse
import json
import math
import statistics
import tempfile
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr028_recent_top_splice_screen.json"


def score(delta: float) -> float:
    return 1.0 if delta > 0 else 0.0 if delta < 0 else 0.5


def runtime_source(actions: list[dict], label: str) -> str:
    payload = json.dumps(actions, separators=(",", ":"), sort_keys=True)
    return f'''"""{label} deterministic action-tape entrypoint for local CR028 screen."""\nimport copy as _copy\nimport json as _json\n_T=_json.loads({payload!r})\ndef _clock(obs):\n    try:\n        raw=obs.get("step")\n        if raw is not None:return max(0,int(raw))\n    except Exception:pass\n    try:return max(0,int(obs.get("day") or 0))*24+max(0,int(obs.get("hour") or 0))\n    except Exception:return 0\ndef agent(obs,config=None):\n    return _copy.deepcopy(_T[max(0,min(718,_clock(obs)))])\n'''


def play(own: Path, opp: Path, seed: int, seat: int) -> dict:
    agents = [str(own), str(opp)] if seat == 0 else [str(opp), str(own)]
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=True)
    env.run(agents)
    rep = env.toJSON(); steps = rep.get("steps") or []
    if len(steps) != 720: raise RuntimeError(f"short game: {len(steps)}")
    final=steps[-1]; statuses=[final[p].get("status") for p in (0,1)]
    if statuses != ["DONE","DONE"]: raise RuntimeError(f"statuses={statuses}")
    rewards=[]
    for p in (0,1):
        x=float(final[p].get("reward"))
        if not math.isfinite(x): raise RuntimeError("non-finite reward")
        rewards.append(x)
    delta=rewards[seat]-rewards[1-seat]
    return {"rewards":rewards,"delta":delta,"score":score(delta)}


def paired_metrics(rows: list[dict]) -> dict:
    diffs=[r["candidate"]["delta"]-r["control"]["delta"] for r in rows]
    return {
        "score_gain": sum(r["candidate"]["score"]-r["control"]["score"] for r in rows),
        "regressions": sum(r["candidate"]["score"] < r["control"]["score"] for r in rows),
        "improvements": sum(r["candidate"]["score"] > r["control"]["score"] for r in rows),
        "mean_delta_gain": statistics.mean(diffs) if diffs else None,
        "median_delta_gain": statistics.median(diffs) if diffs else None,
        "positive_margin_rows": sum(x>0 for x in diffs),
        "negative_margin_rows": sum(x<0 for x in diffs),
        "same_margin_rows": sum(x==0 for x in diffs),
    }


def main() -> None:
    ap=argparse.ArgumentParser();ap.add_argument("--variant-id",required=True);ap.add_argument("--prepared-dir",required=True);ap.add_argument("--opponent-dir",required=True);ap.add_argument("--output",required=True);args=ap.parse_args()
    cfg=json.loads(CFG.read_text(encoding="utf-8")); vm=next((v for v in cfg["variants"] if v["id"]==args.variant_id),None)
    if vm is None: raise SystemExit("unknown variant")
    prepared=Path(args.prepared_dir); manifest=json.loads((prepared/"manifest.json").read_text(encoding="utf-8")); mvm=next(v for v in manifest["variants"] if v["id"]==args.variant_id)
    actions=json.loads((prepared/mvm["file"]).read_text(encoding="utf-8"));cr024=json.loads((prepared/"cr024_actions.json").read_text(encoding="utf-8"))
    if len(actions)!=719 or len(cr024)!=719: raise RuntimeError("tape length")
    seeds=[int(x) for x in cfg["fresh_seeds"]];opdir=Path(args.opponent_dir)
    direct=[];reactive=[];errors=[];per={}
    with tempfile.TemporaryDirectory(prefix=f"cr028-{args.variant_id}-") as td:
        tmp=Path(td);cand=tmp/"candidate.py";base=tmp/"cr024.py"
        cand.write_text(runtime_source(actions,args.variant_id),encoding="utf-8");base.write_text(runtime_source(cr024,"CR024_CONTROL"),encoding="utf-8")
        for seed in seeds:
            for seat in (0,1):
                try: direct.append({"seed":seed,"seat":seat,"candidate":play(cand,base,seed,seat)})
                except Exception as exc: errors.append({"phase":"direct","seed":seed,"seat":seat,"error":repr(exc)[:500]})
        for om in cfg["opponents"]:
            rows=[];opp=opdir/f"{om['id']}.py"
            for seed in seeds:
                for seat in (0,1):
                    try:
                        control=play(base,opp,seed,seat); candidate=play(cand,opp,seed,seat)
                        row={"opponent":om["id"],"seed":seed,"seat":seat,"control":control,"candidate":candidate};rows.append(row);reactive.append(row)
                    except Exception as exc:errors.append({"phase":"reactive","opponent":om["id"],"seed":seed,"seat":seat,"error":repr(exc)[:500]})
            if rows:per[om["id"]]=paired_metrics(rows)
    exp_direct=len(seeds)*2;exp_reactive=len(seeds)*2*len(cfg["opponents"]);mechanical=len(direct)==exp_direct and len(reactive)==exp_reactive and not errors
    direct_score=sum(r["candidate"]["score"] for r in direct);direct_mean=statistics.mean(r["candidate"]["delta"] for r in direct) if direct else None;paired=paired_metrics(reactive) if reactive else {}
    g=cfg["screen_gate"]
    checks={
        "mechanical":mechanical,
        "direct_score":mechanical and direct_score>=float(g["direct_min_score"]),
        "reactive_score":mechanical and paired["score_gain"]>=float(g["reactive_min_score_gain"]),
        "reactive_regressions":mechanical and paired["regressions"]<=int(g["reactive_max_regressions"]),
    }
    payload={"experiment":cfg["experiment"],"variant":mvm,"source":cfg["source"],"fresh_seeds":seeds,"completed_direct":len(direct),"expected_direct":exp_direct,"completed_reactive":len(reactive),"expected_reactive":exp_reactive,"errors":errors,"direct_score":direct_score,"direct_mean_delta":direct_mean,"reactive":paired,"per_opponent":per,"checks":checks,"screen_pass":all(checks.values()),"held_out_touched":False,"automatic_kaggle_submission":False,"direct_rows":direct,"reactive_rows":reactive}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps({k:v for k,v in payload.items() if k not in ("direct_rows","reactive_rows")},indent=2,sort_keys=True))
    if not mechanical: raise SystemExit(3)

if __name__=="__main__":main()
