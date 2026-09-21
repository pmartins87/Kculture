#!/usr/bin/env python3
"""V19D exact package/runtime parity for frozen ALL3+O-TM1 hosted candidate."""
from __future__ import annotations
import argparse,json,math,sys,tarfile,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

from kaggle_environments import make
from tools.programme_adaptive_expert_gate import acquire_public_main,load_public_agent,purge_package_modules,safe_extract,sha256_bytes
from tools.bounded_transaction_oracle_v1 import action_key,call_agent,canonical_action
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.first_party_tm1_p2_consensus_schedule import schedule_action
from tools.build_all3_hosted_candidate import BASE_HANDLE,BASE_MAIN_SHA256

OPPONENTS=[
 {"key":"v47_mirror","handle":BASE_HANDLE,"sha":BASE_MAIN_SHA256},
 {"key":"v48","handle":"ahmedberatozer/kaggriculture-v48-clear-the-queue","sha":"4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96"},
 {"key":"tactical_memory","handle":"web3cainiao/kaggriculture-v21-tactical-memory","sha":"630125b3f592fdb773f1fac6532b08e97e829ae188180ea17540b702b606a054"},
]
SEEDS=[78701,78702]

class Reference:
    def __init__(self,main,schedule):
        self.agent=load_public_agent(main);self.state=OptionHostState();self.schedule=schedule;self.turn=0
    def __call__(self,obs,config=None):
        t=self.turn;self.turn+=1
        base=canonical_action(call_agent(self.agent,obs,config))
        all3=apply_option_host(obs,config,base,self.state,use_rw=True,use_tw=True,use_lq2=True)
        out,_=schedule_action(obs,all3,t,self.schedule)
        return out

class Trace:
    def __init__(self,fn):self.fn=fn;self.actions=[]
    def __call__(self,obs,config=None):
        a=self.fn(obs,config);self.actions.append(action_key(canonical_action(a)));return a

def run(agent,opp,seed,seat):
    ta=Trace(agent);env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0:env.run([ta,opp])
    else:env.run([opp,ta])
    p=env.toJSON();st=[str(x) for x in p.get("statuses",[])];rw=[float(x) for x in p.get("rewards",[])];steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or steps<720 or len(rw)!=2 or not all(math.isfinite(x) for x in rw):
        raise RuntimeError(f"bad episode {st} {rw} steps={steps}")
    return {"actions":ta.actions,"rewards":rw}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--candidate",required=True);ap.add_argument("--schedule",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    sd=json.loads(Path(args.schedule).read_text());schedule=sd.get("schedule") or {}
    rows=[];failures=[]
    with tempfile.TemporaryDirectory(prefix="v19d-parity-") as td:
        root=Path(td)
        base_main,base_rec=acquire_public_main(BASE_HANDLE,root/"base")
        if sha256_bytes(base_main.read_bytes())!=BASE_MAIN_SHA256:raise RuntimeError("base identity mismatch")
        cdir=root/"candidate";cdir.mkdir()
        with tarfile.open(args.candidate,"r:*") as tf:safe_extract(tf,cdir)
        candidate_main=cdir/"main.py"
        if not candidate_main.is_file():raise RuntimeError("candidate main.py missing")
        purge_package_modules(candidate_main.parent)
        probe=load_public_agent(candidate_main);entry=getattr(probe,"__name__",None)
        if entry!="_kc_tm1_entrypoint":raise RuntimeError(f"candidate entrypoint mismatch {entry}")
        purge_package_modules(candidate_main.parent)

        opp_paths={};prov={"base":base_rec}
        for spec in OPPONENTS:
            if spec["sha"]==BASE_MAIN_SHA256:opp_paths[spec["key"]]=base_main;continue
            p,rec=acquire_public_main(spec["handle"],root/f"opp_{spec['key']}")
            if sha256_bytes(p.read_bytes())!=spec["sha"]:raise RuntimeError(f"{spec['key']} identity mismatch")
            opp_paths[spec["key"]]=p;prov[spec["key"]]=rec

        for spec in OPPONENTS:
            opp_main=opp_paths[spec["key"]]
            for seed in SEEDS:
                for seat in (0,1):
                    key={"opponent":spec["key"],"seed":seed,"seat":seat}
                    try:
                        purge_package_modules(base_main.parent);purge_package_modules(opp_main.parent)
                        ref=Reference(base_main,schedule);opp1=load_public_agent(opp_main)
                        rr=run(ref,opp1,seed,seat)
                        purge_package_modules(candidate_main.parent);purge_package_modules(opp_main.parent)
                        cand=load_public_agent(candidate_main);opp2=load_public_agent(opp_main)
                        pp=run(cand,opp2,seed,seat)
                        if rr["actions"]!=pp["actions"] or rr["rewards"]!=pp["rewards"]:
                            first=None
                            for i,(a,b) in enumerate(zip(rr["actions"],pp["actions"])):
                                if a!=b:first=i;break
                            raise RuntimeError(f"parity mismatch first={first} ref_rewards={rr['rewards']} pkg_rewards={pp['rewards']}")
                        rows.append({**key,"rewards":rr["rewards"],"action_calls":len(rr["actions"]),
                                     "exact_action_parity":True,"exact_reward_parity":True})
                    except Exception as exc:
                        failures.append({**key,"error":f"{type(exc).__name__}: {exc}"})
    result={"schema":"kculture-v19d-package-parity-v1","pairs":len(rows),"expected_pairs":12,
      "failures":failures,"mechanical_pass":not failures and len(rows)==12,
      "candidate_hosted_entrypoint":"_kc_tm1_entrypoint","fresh_seeds":SEEDS,
      "opponents":[x["key"] for x in OPPONENTS],"rows":rows,"automatic_kaggle_submission":False}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V19D_PACKAGE_PARITY_RESULT",json.dumps({"pairs":len(rows),"failures":len(failures),"mechanical_pass":result["mechanical_pass"]},sort_keys=True),flush=True)
    if not result["mechanical_pass"]:raise SystemExit(2)

if __name__=="__main__":main()
