#!/usr/bin/env python3
"""Exact package/runtime parity gate for hosted-faithful V47 ALL3 candidate."""
from __future__ import annotations

import argparse
import json
import math
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from kaggle_environments import make

from tools.programme_adaptive_expert_gate import (
    acquire_public_main,load_public_agent,purge_package_modules,safe_extract,sha256_bytes,
)
from tools.bounded_transaction_oracle_v1 import action_key,call_agent,canonical_action
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host

BASE={
    "key":"v47",
    "handle":"ahmedberatozer/kaggriculture-v47-reactive-market-coordination",
    "sha":"f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842",
}
OPPONENTS=[
    {
        "key":"v47_mirror",
        "handle":BASE["handle"],
        "sha":BASE["sha"],
    },
    {
        "key":"v48",
        "handle":"ahmedberatozer/kaggriculture-v48-clear-the-queue",
        "sha":"4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96",
    },
    {
        "key":"tactical_memory",
        "handle":"web3cainiao/kaggriculture-v21-tactical-memory",
        "sha":"630125b3f592fdb773f1fac6532b08e97e829ae188180ea17540b702b606a054",
    },
]
SEEDS=[74701,74702]

class ReferenceAll3:
    def __init__(self,main_py:Path):
        self.agent=load_public_agent(main_py)
        self.state=OptionHostState()
    def __call__(self,obs,config=None):
        base=canonical_action(call_agent(self.agent,obs,config))
        return apply_option_host(obs,config,base,self.state)

class TraceAgent:
    def __init__(self,fn):
        self.fn=fn
        self.actions=[]
    def __call__(self,obs,config=None):
        a=self.fn(obs,config)
        self.actions.append(action_key(canonical_action(a)))
        return a

def run(agent_fn,opp_fn,seed:int,seat:int):
    a=TraceAgent(agent_fn)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0:
        env.run([a,opp_fn])
    else:
        env.run([opp_fn,a])
    p=env.toJSON()
    statuses=[str(x) for x in p.get("statuses",[])]
    rewards=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    if statuses!=["DONE","DONE"] or steps<720:
        raise RuntimeError(f"bad episode statuses={statuses} steps={steps}")
    if len(rewards)!=2 or not all(math.isfinite(x) for x in rewards):
        raise RuntimeError(f"bad rewards {rewards}")
    return {"statuses":statuses,"rewards":rewards,"actions":a.actions,"steps":steps}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidate",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    rows=[];failures=[]

    with tempfile.TemporaryDirectory(prefix="all3-package-parity-") as td:
        root=Path(td)
        base_main,base_rec=acquire_public_main(BASE["handle"],root/"base")
        if sha256_bytes(base_main.read_bytes())!=BASE["sha"]:
            raise RuntimeError("base V47 identity mismatch")

        cdir=root/"candidate";cdir.mkdir()
        with tarfile.open(args.candidate,"r:*") as tf:
            safe_extract(tf,cdir)
        candidate_main=cdir/"main.py"
        if not candidate_main.is_file():
            raise RuntimeError("candidate root main.py missing")

        purge_package_modules(base_main.parent)
        base_probe=load_public_agent(base_main)
        base_entrypoint=getattr(base_probe,"__name__",None)
        purge_package_modules(base_main.parent)
        if base_entrypoint!="_y_agent_shopherd":
            raise RuntimeError(f"unexpected V47 entrypoint {base_entrypoint}")

        purge_package_modules(candidate_main.parent)
        cand_probe=load_public_agent(candidate_main)
        candidate_entrypoint=getattr(cand_probe,"__name__",None)
        purge_package_modules(candidate_main.parent)
        if candidate_entrypoint!="_kc_all3_entrypoint":
            raise RuntimeError(f"candidate entrypoint mismatch {candidate_entrypoint}")

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
                        ref=ReferenceAll3(base_main)
                        opp1=load_public_agent(opp_main)
                        rr=run(ref,opp1,seed,seat)

                        purge_package_modules(candidate_main.parent)
                        purge_package_modules(opp_main.parent)
                        cand=load_public_agent(candidate_main)
                        opp2=load_public_agent(opp_main)
                        pp=run(cand,opp2,seed,seat)

                        action_equal=rr["actions"]==pp["actions"]
                        reward_equal=rr["rewards"]==pp["rewards"]
                        if not action_equal or not reward_equal:
                            first_mismatch=None
                            for i,(ra,pa) in enumerate(zip(rr["actions"],pp["actions"])):
                                if ra!=pa:
                                    first_mismatch=i
                                    break
                            if first_mismatch is None and len(rr["actions"])!=len(pp["actions"]):
                                first_mismatch=min(len(rr["actions"]),len(pp["actions"]))
                            raise RuntimeError(
                                f"package/reference mismatch action_equal={action_equal} "
                                f"reward_equal={reward_equal} first_mismatch={first_mismatch} "
                                f"reference_rewards={rr['rewards']} package_rewards={pp['rewards']}"
                            )
                        row={
                            **key,
                            "rewards":rr["rewards"],
                            "action_calls":len(rr["actions"]),
                            "exact_action_parity":True,
                            "exact_reward_parity":True,
                        }
                        rows.append(row)
                        print("ALL3_PACKAGE_PARITY_PAIR",json.dumps(row,sort_keys=True),flush=True)
                    except Exception as exc:
                        failures.append({**key,"error":f"{type(exc).__name__}: {exc}"})

    expected=len(OPPONENTS)*len(SEEDS)*2
    result={
        "schema":"kculture-all3-package-parity-v1",
        "candidate":Path(args.candidate).name,
        "base_hosted_entrypoint":base_entrypoint,
        "candidate_hosted_entrypoint":candidate_entrypoint,
        "fresh_seeds":SEEDS,
        "opponents":[x["key"] for x in OPPONENTS],
        "pairs":len(rows),
        "episodes":len(rows)*2,
        "failures":failures,
        "mechanical_pass":not failures and len(rows)==expected,
        "rows":rows,
        "automatic_kaggle_submission":False,
    }
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("ALL3_PACKAGE_PARITY_RESULT",json.dumps({
        "pairs":result["pairs"],"failures":len(failures),
        "mechanical_pass":result["mechanical_pass"],
        "candidate_hosted_entrypoint":candidate_entrypoint,
    },sort_keys=True),flush=True)
    if not result["mechanical_pass"]:
        raise SystemExit(2)

if __name__=="__main__":
    main()
