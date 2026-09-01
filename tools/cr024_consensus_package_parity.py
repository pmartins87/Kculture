"""Exact action-trace parity: research CR024 consensus vs generated package.

Uses only already-open raw Stage-A seeds, never reserved/held-out validation data.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import tarfile
import tempfile
import time
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr023_public_tape_preregistered_seeds_v1.json"


def load_module(path: Path, prefix: str):
    spec = importlib.util.spec_from_file_location(f"{prefix}_{time.time_ns()}", path)
    if spec is None or spec.loader is None: raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod


def trace(env, seat):
    out=[]
    for frame in env.toJSON()["steps"][1:]:
        action=(frame[seat] or {}).get("action") if isinstance(frame[seat],dict) else None
        out.append(json.dumps(action or {},sort_keys=True,separators=(",",":")))
    return out


def run(agent, opp_path, seed, seat):
    opp=load_module(opp_path,"cr024_consensus_parity_opp").agent
    agents=[agent,opp] if seat==0 else [opp,agent]
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=True);env.run(agents)
    final=env.toJSON()["steps"][-1]
    if [final[i].get("status") for i in range(2)] != ["DONE","DONE"]: raise RuntimeError("non-DONE")
    return {"trace":trace(env,seat),"self":float(final[seat].get("reward")),"opp":float(final[1-seat].get("reward"))}


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--archive",required=True);ap.add_argument("--opponent",required=True);ap.add_argument("--output",required=True);args=ap.parse_args()
    cfg=json.loads(CFG.read_text(encoding="utf-8"));open_seeds=[int(x) for x in cfg["raw_backbone_stage_a_seeds"]]
    seeds=[open_seeds[0],open_seeds[len(open_seeds)//2],open_seeds[-1]]
    reserved=set(int(x) for x in cfg["adaptive_overlay_stage_a_seeds_reserved"])|set(int(x) for x in cfg["adaptive_overlay_stage_b_seeds_reserved"])
    held=set(int(x) for x in cfg.get("held_out_seeds",[])) if isinstance(cfg.get("held_out_seeds"),list) else set()
    if set(seeds)&reserved or set(seeds)&held: raise SystemExit("seed firewall")
    opp=Path(args.opponent);opp=opp if opp.is_absolute() else ROOT/opp
    rows=[];errors=[]
    with tempfile.TemporaryDirectory(prefix="cr024-consensus-parity-") as td:
        td=Path(td)
        with tarfile.open(args.archive,"r:gz") as tf:
            fh=tf.extractfile(tf.getmember("main.py"));package_main=td/"main.py";package_main.write_bytes(fh.read() if fh else b"")
        builder=load_module(ROOT/"tools/build_cr024_consensus_submission.py","cr024_consensus_builder")
        from kaggle.api.kaggle_api_extended import KaggleApi
        api=KaggleApi();api.authenticate()
        t11,_=builder.download_tape(api,cfg["routes"]["top11_openloop"],td)
        t19,_=builder.download_tape(api,cfg["routes"]["top19_openloop"],td)
        consensus=builder.build_consensus(t11,t19)
        def research_agent(obs,config=None):
            try:
                raw=obs.get("step");step=int(raw) if raw is not None else int(obs.get("day") or 0)*24+int(obs.get("hour") or 0)
            except Exception: step=0
            import copy
            return copy.deepcopy(consensus[max(0,min(718,step))])
        for seed in seeds:
            for seat in (0,1):
                try:
                    package_agent=load_module(package_main,"cr024_consensus_package").agent
                    a=run(research_agent,opp,seed,seat);b=run(package_agent,opp,seed,seat)
                    same_trace=a["trace"]==b["trace"];same_rewards=a["self"]==b["self"] and a["opp"]==b["opp"]
                    first_diff=None
                    if not same_trace:
                        n=min(len(a["trace"]),len(b["trace"]));first_diff=next((i for i in range(n) if a["trace"][i]!=b["trace"][i]),n if len(a["trace"])!=len(b["trace"]) else None)
                    rows.append({"seed":seed,"seat":seat,"same_trace":same_trace,"same_rewards":same_rewards,"first_diff":first_diff})
                    if not same_trace or not same_rewards: errors.append(rows[-1])
                except Exception as exc: errors.append({"seed":seed,"seat":seat,"error":repr(exc)})
    report={"experiment":"CR024_CONSENSUS_V1_PACKAGE_PARITY","seed_class":"RAW_STAGE_A_ALREADY_OPEN_ONLY","seeds":seeds,"rows":rows,"row_count":len(rows),"error_count":len(errors),"errors":errors,"decision":"PASS" if len(rows)==len(seeds)*2 and not errors else "FAIL","reserved_touched":False,"held_out_touched":False}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2,sort_keys=True),encoding="utf-8");print(json.dumps(report,indent=2,sort_keys=True))
    if report["decision"]!="PASS": raise SystemExit(3)


if __name__=="__main__":main()
