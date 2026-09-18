#!/usr/bin/env python3
"""Mechanical parity gate for the packaged V47+O-RW1 candidate.

Compare the packaged agent action-for-action and reward-for-reward against the
reference in-process OneShotReadyWool wrapper on fresh seeds/opponents.
"""
from __future__ import annotations

import argparse
import json
import math
import tempfile
from pathlib import Path

from kaggle_environments import make

from tools.programme_adaptive_expert_gate import (
    acquire_public_main,
    load_public_agent,
    purge_package_modules,
    safe_extract,
    sha256_bytes,
)
from tools.bounded_transaction_oracle_v1 import action_key, canonical_action
from tools.ready_wool_oneshot_runtime_gate import OneShotReadyWool

BASE = {
    "handle": "ahmedberatozer/kaggriculture-v47-reactive-market-coordination",
    "sha": "f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842",
}
OPPONENTS = [
    {
        "key":"v47",
        "handle":BASE["handle"],
        "sha":BASE["sha"],
    },
    {
        "key":"tactical_memory",
        "handle":"web3cainiao/kaggriculture-v21-tactical-memory",
        "sha":"630125b3f592fdb773f1fac6532b08e97e829ae188180ea17540b702b606a054",
    },
]
SEEDS=[66001,66002]


class TraceAgent:
    def __init__(self, fn):
        self.fn=fn
        self.actions=[]

    def __call__(self, obs, config=None):
        a=self.fn(obs,config)
        self.actions.append(action_key(canonical_action(a)))
        return a


def run(agent_fn, opp_fn, seed:int, seat:int):
    a=TraceAgent(agent_fn)
    b=opp_fn
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0:
        env.run([a,b])
    else:
        env.run([b,a])
    p=env.toJSON()
    st=[str(x) for x in p.get("statuses",[])]
    rw=[float(x) for x in p.get("rewards",[])]
    if st!=["DONE","DONE"]:
        raise RuntimeError(f"status failure {st}")
    if len(rw)!=2 or not all(math.isfinite(x) for x in rw):
        raise RuntimeError(f"invalid rewards {rw}")
    return {"statuses":st,"rewards":rw,"actions":a.actions}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidate",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    rows=[]
    failures=[]

    with tempfile.TemporaryDirectory(prefix="orw1-package-parity-") as td:
        root=Path(td)
        base_main,base_rec=acquire_public_main(BASE["handle"],root/"base")
        if sha256_bytes(base_main.read_bytes())!=BASE["sha"]:
            raise RuntimeError("base V47 identity mismatch")

        import tarfile
        cdir=root/"candidate"
        cdir.mkdir()
        with tarfile.open(args.candidate,"r:*") as tf:
            safe_extract(tf,cdir)
        candidate_main=cdir/"main.py"
        if not candidate_main.is_file():
            raise RuntimeError("candidate root main.py missing")

        opp_paths={}
        provenance={"base":base_rec}
        for spec in OPPONENTS:
            if spec["sha"]==BASE["sha"]:
                opp_paths[spec["key"]]=base_main
                continue
            p,rec=acquire_public_main(spec["handle"],root/f"opp_{spec['key']}")
            if sha256_bytes(p.read_bytes())!=spec["sha"]:
                raise RuntimeError(f"{spec['key']} identity mismatch")
            opp_paths[spec["key"]]=p
            provenance[spec["key"]]=rec

        for spec in OPPONENTS:
            opp_main=opp_paths[spec["key"]]
            for seed in SEEDS:
                for seat in (0,1):
                    key={"opponent":spec["key"],"seed":seed,"seat":seat}
                    try:
                        purge_package_modules(base_main.parent)
                        purge_package_modules(opp_main.parent)
                        ref=OneShotReadyWool(base_main)
                        opp1=load_public_agent(opp_main)
                        rr=run(ref,opp1,seed,seat)

                        purge_package_modules(candidate_main.parent)
                        purge_package_modules(opp_main.parent)
                        cand=load_public_agent(candidate_main)
                        opp2=load_public_agent(opp_main)
                        pp=run(cand,opp2,seed,seat)

                        ok=(rr["rewards"]==pp["rewards"] and rr["actions"]==pp["actions"])
                        if not ok:
                            raise RuntimeError(
                                f"package/reference mismatch rewards {rr['rewards']} vs {pp['rewards']} "
                                f"action_equal={rr['actions']==pp['actions']}"
                            )
                        rows.append({
                            **key,
                            "rewards":rr["rewards"],
                            "action_calls":len(rr["actions"]),
                            "exact_action_parity":True,
                            "exact_reward_parity":True,
                        })
                        print("ORW1_PACKAGE_PARITY_PAIR",json.dumps(rows[-1],sort_keys=True),flush=True)
                    except Exception as exc:
                        failures.append({**key,"error":f"{type(exc).__name__}: {exc}"})

    result={
        "schema":"kculture-orw1-package-parity-v1",
        "candidate":Path(args.candidate).name,
        "fresh_seeds":SEEDS,
        "opponents":[x["key"] for x in OPPONENTS],
        "pairs":len(rows),
        "episodes":len(rows)*2,
        "failures":failures,
        "mechanical_pass":not failures and len(rows)==len(SEEDS)*2*len(OPPONENTS),
        "rows":rows,
        "automatic_kaggle_submission":False,
    }
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("ORW1_PACKAGE_PARITY_RESULT",json.dumps({
        "pairs":result["pairs"],
        "failures":len(failures),
        "mechanical_pass":result["mechanical_pass"],
    },sort_keys=True),flush=True)
    if not result["mechanical_pass"]:
        raise SystemExit(2)


if __name__=="__main__":
    main()
