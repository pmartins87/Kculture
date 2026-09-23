#!/usr/bin/env python3
from __future__ import annotations
import argparse,collections,copy,json,math,os,statistics,sys
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,action_key
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.o_pc1_dev_shard import BASE

CHECKPOINTS=(0,96,192,288,384,480,576,648,696,719)
WINDOWS=((0,95),(96,191),(192,287),(288,383),(384,479),(480,575),(576,647),(648,695),(696,718))
ITEMS=("COW","SHEEP","GOOSE","WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","WEED")

def mean(xs): return statistics.fmean(xs) if xs else None
def median(xs): return statistics.median(xs) if xs else None

def board_comp(farm):
    c=collections.Counter()
    for row in farm.get("tiles",[]) or []:
        for t in row or []:
            if not isinstance(t,dict): continue
            if t.get("animal"): c[str(t["animal"])]+=1
            elif t.get("kind")=="PLANT": c[str(t.get("crop"))]+=1
            elif t.get("kind")=="WEED": c["WEED"]+=1
    out={"hands":len(farm.get("hands",[]) or []),"quads":len(farm.get("unlocked_quadrants",[]) or [])}
    out.update({k:int(c.get(k,0)) for k in ITEMS})
    return out

def checkpoint(rep,seat,t):
    steps=rep.get("steps") or []
    if t>=len(steps): raise RuntimeError(f"missing checkpoint {t}")
    obs=steps[t][seat].get("observation") or {}
    farms=obs.get("farms") or []
    if len(farms)<2: raise RuntimeError("missing farms")
    own=farms[seat] or {}; opp=farms[1-seat] or {}
    private=obs.get("private") or {}
    shed={str(k):int(v) for k,v in (private.get("shed") or {}).items() if int(v)}
    seeds={str(k):int(v) for k,v in (private.get("seeds") or {}).items() if int(v)}
    return {
      "money":float(own.get("money",0) or 0),
      "opp_money":float(opp.get("money",0) or 0),
      "money_gap":float(own.get("money",0) or 0)-float(opp.get("money",0) or 0),
      "own_public":board_comp(own),"opp_public":board_comp(opp),
      "own_private":{"shed":shed,"seeds":seeds},
    }

def phase_actions(rep,p,a,b):
    unit=collections.Counter();market=collections.Counter()
    steps=rep.get("steps") or []
    for t in range(a,min(b+1,len(steps)-1)):
        ac=steps[t+1][p].get("action") or {}
        for op in [ac.get("farmer")]+list(ac.get("hands") or []):
            if isinstance(op,list) and op:
                unit[str(op[0])]+=1
        for order in list(ac.get("market") or []):
            if not (isinstance(order,list) and order): continue
            verb=str(order[0]);item=str(order[1]) if len(order)>1 else None
            key=f"{verb}:{item}" if item is not None and verb in ("BUY_ANIMAL","BUY_SEED","SELL") else verb
            qty=1
            if len(order)>=3:
                try: qty=max(0,int(order[2] or 0))
                except Exception: qty=1
            market[key]+=qty
    return {"unit":dict(unit),"market":dict(market)}

class TraceAll3:
    def __init__(self,base_main):
        purge_package_modules(base_main.parent)
        self.base=load_public_agent(base_main)
        self.host=OptionHostState()
        self.events=[]
    def __call__(self,obs,config=None):
        base=canonical_action(call_agent(self.base,obs,config))
        shadow_state=OptionHostState(rw_used=self.host.rw_used,tw_used=self.host.tw_used)
        pre_lq2=apply_option_host(obs,config,base,shadow_state,use_rw=True,use_tw=True,use_lq2=False)
        before_rw=self.host.rw_used;before_tw=self.host.tw_used
        out=apply_option_host(obs,config,base,self.host,use_rw=True,use_tw=True,use_lq2=True)
        kinds=[]
        if not before_rw and self.host.rw_used:kinds.append("O-RW1")
        if not before_tw and self.host.tw_used:kinds.append("O-TW1")
        if action_key(out)!=action_key(pre_lq2):kinds.append("O-LQ2")
        if action_key(out)!=action_key(base):
            po=obs if isinstance(obs,dict) else dict(obs)
            player=int(po.get("player",0));farms=po.get("farms") or []
            own=farms[player] if len(farms)>player else {};opp=farms[1-player] if len(farms)>1-player else {}
            private=po.get("private") or {}
            self.events.append({
              "step":int(po.get("step",-1)),"kinds":kinds,
              "base_action":copy.deepcopy(base),"all3_action":copy.deepcopy(out),
              "money":float(own.get("money",0) or 0),
              "money_gap":float(own.get("money",0) or 0)-float(opp.get("money",0) or 0),
              "shed":{str(k):int(v) for k,v in (private.get("shed") or {}).items() if int(v)},
              "seeds":{str(k):int(v) for k,v in (private.get("seeds") or {}).items() if int(v)},
            })
        return out

def run_one(base_main,opp_main,seed,seat):
    purge_package_modules(base_main.parent);purge_package_modules(opp_main.parent)
    cand=TraceAll3(base_main)
    purge_package_modules(opp_main.parent)
    opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if int(seat)==0:env.run([cand,opp])
    else:env.run([opp,cand])
    rep=env.toJSON()
    statuses=[str(x) for x in rep.get("statuses",[])]
    rewards=[float(x) for x in rep.get("rewards",[])]
    steps=len(rep.get("steps") or [])
    if statuses!=["DONE","DONE"] or len(rewards)!=2 or steps<720 or not all(math.isfinite(x) for x in rewards):
        raise RuntimeError(f"invalid episode statuses={statuses} rewards={rewards} steps={steps}")
    mine,other=(rewards[0],rewards[1]) if int(seat)==0 else (rewards[1],rewards[0])
    return {
      "score":1.0 if mine>other else 0.0 if mine<other else 0.5,
      "margin":mine-other,"rewards":rewards,
      "checkpoints":{str(t):checkpoint(rep,int(seat),t) for t in CHECKPOINTS},
      "phases":{f"{a}_{b}":{"all3":phase_actions(rep,int(seat),a,b),"opponent":phase_actions(rep,1-int(seat),a,b)} for a,b in WINDOWS},
      "option_events":cand.events,
    }

def flat_action(profile,phase,role):
    z=profile["phases"][phase][role]
    out={}
    for k,v in z["unit"].items():out[f"UNIT:{k}"]=float(v)
    for k,v in z["market"].items():out[f"MARKET:{k}"]=float(v)
    return out

def avg_diff(hard,ctrl,getter):
    vals=[]
    for h,c in zip(hard,ctrl):
        vals.append(float(getter(h))-float(getter(c)))
    return {"mean":mean(vals),"median":median(vals),"values":vals}

def flatten_comp(cp,prefix):
    d={}
    for k,v in cp["own_public"].items():d[f"own_public:{k}"]=float(v)
    for k,v in cp["opp_public"].items():d[f"opp_public:{k}"]=float(v)
    for group in ("shed","seeds"):
        for k,v in cp["own_private"][group].items():d[f"own_private:{group}:{k}"]=float(v)
    d["money"]=float(cp["money"]);d["opp_money"]=float(cp["opp_money"]);d["money_gap"]=float(cp["money_gap"])
    return d

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot-dir",required=True)
    ap.add_argument("--v28g",required=True)
    ap.add_argument("--v28f",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    root=Path(a.snapshot_dir)
    manifest=json.loads((root/"MANIFEST.json").read_text())
    base_main=root/manifest["base"]["path"]
    if sha256_bytes(base_main.read_bytes())!=BASE["expected_main_sha256"]:
        raise SystemExit("V47 base snapshot SHA mismatch")
    paths={}
    meta={}
    for src in manifest["sources"]:
        p=root/src["path"]
        if sha256_bytes(p.read_bytes())!=str(src["sha"]):
            raise SystemExit(f"source SHA mismatch {src['sha']}")
        paths[str(src["sha"])]=p
        meta[str(src["sha"])]=src

    g=json.loads(Path(a.v28g).read_text())
    f=json.loads(Path(a.v28f).read_text())
    if g.get("decision")!="V28G_SOURCE_CLUSTERED_HARD_CORE" or not g.get("mechanical_pass"):
        raise SystemExit("V28G binding mismatch")
    if f.get("decision")!="V28F_NO_MATERIAL_HEDGE_REPLACEMENT" or not f.get("mechanical_pass"):
        raise SystemExit("V28F binding mismatch")

    all3={(str(r["main_sha256"]),int(r["seed"]),int(r["seat"])):r for r in f["rows"] if r["candidate"]=="ALL3"}
    zero=sorted([x for x in g["by_source"] if int(x["losses"])==0],key=lambda x:(int(x["representative_rank"]),str(x["main_sha256"])))
    targets=list(g["trace_targets"])
    if len(zero)!=6 or not targets:raise SystemExit(f"unexpected control/target counts zero={len(zero)} targets={len(targets)}")

    hard_rows=[];ctrl_rows=[];failures=[]
    for i,t in enumerate(targets):
        csrc=zero[i%len(zero)]
        specs=[
          ("hard",str(t["main_sha256"]),int(t["seed"]),int(t["seat"]),str(t.get("bucket","hard"))),
          ("control",str(csrc["main_sha256"]),int(t["seed"]),int(t["seat"]),"matched_zero_loss"),
        ]
        pair={}
        for cohort,sha,seed,seat,label in specs:
            try:
                rr=run_one(base_main,paths[sha],seed,seat)
                exp=all3[(sha,seed,seat)]
                if float(rr["score"])!=float(exp["score"]) or float(rr["margin"])!=float(exp["margin"]):
                    raise RuntimeError(f"V28F replay mismatch observed={(rr['score'],rr['margin'])} expected={(exp['score'],exp['margin'])}")
                row={"pair_index":i,"cohort":cohort,"label":label,"main_sha256":sha,
                     "representative_ref":meta[sha]["representative_ref"],"representative_rank":int(meta[sha]["representative_rank"]),
                     "seed":seed,"seat":seat,**rr}
                pair[cohort]=row
            except Exception as exc:
                failures.append({"pair_index":i,"cohort":cohort,"sha":sha,"seed":seed,"seat":seat,"error":f"{type(exc).__name__}: {exc}"})
            finally:
                purge_package_modules(base_main.parent)
                if sha in paths:purge_package_modules(paths[sha].parent)
        if "hard" in pair:hard_rows.append(pair["hard"])
        if "control" in pair:ctrl_rows.append(pair["control"])

    mech=not failures and len(hard_rows)==len(targets) and len(ctrl_rows)==len(targets)
    # align by pair index
    hard_rows=sorted(hard_rows,key=lambda x:x["pair_index"]);ctrl_rows=sorted(ctrl_rows,key=lambda x:x["pair_index"])

    checkpoint_diffs={}
    selected=None
    if mech:
        for t in CHECKPOINTS:
            tk=str(t)
            vals=[float(h["checkpoints"][tk]["money_gap"])-float(c["checkpoints"][tk]["money_gap"]) for h,c in zip(hard_rows,ctrl_rows)]
            checkpoint_diffs[tk]={"mean":mean(vals),"median":median(vals),"values":vals,
                                  "hard_negative":sum(float(h["checkpoints"][tk]["money_gap"])<0 for h in hard_rows),
                                  "control_negative":sum(float(c["checkpoints"][tk]["money_gap"])<0 for c in ctrl_rows)}
        eligible=[t for t in CHECKPOINTS if float(checkpoint_diffs[str(t)]["median"])<=-1000]
        if eligible:selected=min(eligible)
        else:selected=min(CHECKPOINTS,key=lambda t:(float(checkpoint_diffs[str(t)]["median"]),t))

    if selected is None:
        phase=None
    else:
        prior=[w for w in WINDOWS if w[1]<selected]
        phase=prior[-1] if prior else WINDOWS[0]
    phase_key=f"{phase[0]}_{phase[1]}" if phase else None

    comp_diffs=[];opp_action_diffs=[];all3_action_diffs=[];option_summary={}
    if mech:
        tk=str(selected)
        keys=set()
        hf=[flatten_comp(h["checkpoints"][tk],"") for h in hard_rows]
        cf=[flatten_comp(c["checkpoints"][tk],"") for c in ctrl_rows]
        for z in hf+cf:keys.update(z)
        for k in sorted(keys):
            vals=[float(hf[i].get(k,0))-float(cf[i].get(k,0)) for i in range(len(hf))]
            comp_diffs.append({"metric":k,"mean_hard_minus_control":mean(vals),"median":median(vals)})
        comp_diffs.sort(key=lambda x:(-abs(float(x["mean_hard_minus_control"])),x["metric"]))

        for role,out in (("opponent",opp_action_diffs),("all3",all3_action_diffs)):
            hd=[flat_action(h,phase_key,role) for h in hard_rows];cd=[flat_action(c,phase_key,role) for c in ctrl_rows]
            ks=set()
            for z in hd+cd:ks.update(z)
            for k in sorted(ks):
                vals=[hd[i].get(k,0)-cd[i].get(k,0) for i in range(len(hd))]
                out.append({"metric":k,"mean_hard_minus_control":mean(vals),"median":median(vals)})
            out.sort(key=lambda x:(-abs(float(x["mean_hard_minus_control"])),x["metric"]))

        def evsum(rows):
            kind=collections.Counter();first=collections.defaultdict(list)
            for r in rows:
                for e in r["option_events"]:
                    for k in e["kinds"]:
                        kind[k]+=1;first[k].append(int(e["step"]))
            return {"event_counts":dict(kind),"median_first_or_event_step":{k:median(v) for k,v in first.items()},
                    "contexts_with_any_event":sum(bool(r["option_events"]) for r in rows)}
        option_summary={"hard":evsum(hard_rows),"control":evsum(ctrl_rows)}

    if not mech:decision="V28H_MECHANICS_INVALID"
    elif selected<=288:decision="V28H_EARLY_STRUCTURAL_SEPARATION"
    elif selected<=576:decision="V28H_MIDGAME_STRUCTURAL_SEPARATION"
    else:decision="V28H_LATE_STRUCTURAL_SEPARATION"

    out={
      "schema":"kculture-v28h-matched-hard-easy-trajectory-trace-v1",
      "mechanical_pass":mech,"decision":decision,
      "hard_contexts":len(hard_rows),"control_contexts":len(ctrl_rows),
      "selected_checkpoint":selected,"explanatory_window":list(phase) if phase else None,
      "checkpoint_money_gap_diffs":checkpoint_diffs,
      "selected_checkpoint_composition_diffs":comp_diffs,
      "explanatory_opponent_action_diffs":opp_action_diffs,
      "explanatory_all3_action_diffs":all3_action_diffs,
      "option_event_summary":option_summary,
      "hard_rows":hard_rows,"control_rows":ctrl_rows,
      "failures":failures,"automatic_kaggle_submission":False,
    }
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V28H_RESULT",json.dumps({
      "decision":decision,"mechanical_pass":mech,"selected_checkpoint":selected,"explanatory_window":list(phase) if phase else None,
      "checkpoint_money_gap_diffs":checkpoint_diffs,
      "top_composition_diffs":comp_diffs[:15],
      "top_opponent_action_diffs":opp_action_diffs[:15],
      "top_all3_action_diffs":all3_action_diffs[:15],
      "option_event_summary":option_summary,
      "failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
