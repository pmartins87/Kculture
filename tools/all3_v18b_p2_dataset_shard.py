#!/usr/bin/env python3
"""V18B P2 dataset shard: exact ALL3 gameplay + offline shadow market labels."""
from __future__ import annotations
import argparse,collections,json,math,os,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,acquire_public_main,load_public_agent,purge_package_modules,sha256_bytes
from tools.o_pc1_dev_shard import BASE
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,plain,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.all3_v14b_market_phenotype_atlas import PRODUCTS,state_features,diff_event,order_parts

START=464
END_EXCLUSIVE=592
SIDES=("SELL","BUY_SEED","BUY_PRODUCT")
REAL_PRODUCTS=tuple(PRODUCTS)

def acquire_exact(ref,expected,tmp,attempts=10):
    last=None
    for i in range(attempts):
        try:
            main,receipt=acquire_public_main(ref,tmp/f"try{i}")
            h=sha256_bytes(main.read_bytes())
            if h!=expected:raise RuntimeError(f"source SHA drift {h} != {expected}")
            return main,receipt
        except Exception as exc:
            last=exc
            if i+1<attempts:time.sleep(min(24.0,2.0*(i+1)))
    raise last

def numeric_features(obs,seat,turn,all3):
    raw=state_features(obs,seat,turn)
    f={}
    for k,v in raw.items():
        if isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(float(v)):
            f[k]=float(v)
    f["p2_progress"]=float((int(turn)-START)/(END_EXCLUSIVE-START-1))
    p=plain(obs)
    market_public=p.get("market") or {}
    inv=market_public.get("inventory") or {}
    for product in REAL_PRODUCTS:
        try:f[f"public_market_inv_{product}"]=float(inv.get(product,0) or 0)
        except:f[f"public_market_inv_{product}"]=0.0
        f[f"available_{product}"]=float(f.get(f"shed_{product}",0.0)+f.get(f"carried_{product}",0.0))
    shops=((p.get("town") or {}).get("unlocked_shops") or [])
    f["unlocked_shops_count"]=float(len(shops))

    m=list(all3.get("market") or [])
    f["all3_market_len"]=float(len(m))
    f["all3_market_nonempty"]=float(sum(bool(list(x or [])) for x in m))
    f["all3_market_empty"]=float(sum(not bool(list(x or [])) for x in m))
    agg_qty=collections.Counter();agg_count=collections.Counter()
    hire=0
    for o in m:
        side,product,qty=order_parts(o)
        if side=="HIRE":hire+=1
        if side in SIDES and product in REAL_PRODUCTS:
            agg_qty[(side,product)]+=int(qty)
            agg_count[(side,product)]+=1
    for side in SIDES:
        for product in REAL_PRODUCTS:
            f[f"all3_{side}_{product}_qty"]=float(agg_qty[(side,product)])
            f[f"all3_{side}_{product}_count"]=float(agg_count[(side,product)])
    f["all3_HIRE_count"]=float(hire)
    f["all3_sell_units_total"]=float(sum(v for (s,_),v in agg_qty.items() if s=="SELL"))
    f["all3_buy_units_total"]=float(sum(v for (s,_),v in agg_qty.items() if s.startswith("BUY")))
    return dict(sorted(f.items()))

def labels_from_event(ev):
    if ev is None:return []
    out=[]
    for e in ev.get("elementary") or []:
        out.append({
          "family_id":f"{e.get('group_key')}||{e.get('direction')}",
          "group_key":str(e.get("group_key")),
          "direction":str(e.get("direction")),
          "kind":str(e.get("kind")),
          "side":str(e.get("side","")),
          "product":str(e.get("product","")),
          "magnitude_bucket":str(e.get("magnitude_bucket","")),
        })
    return out

class Collector:
    def __init__(self,base_main,teacher_main,ctx):
        purge_package_modules(base_main.parent);purge_package_modules(teacher_main.parent)
        self.base=load_public_agent(base_main)
        purge_package_modules(teacher_main.parent)
        self.shadow=load_public_agent(teacher_main)
        self.host=OptionHostState()
        self.turn=0;self.seat=int(ctx["seat"]);self.context_id=str(ctx["context_id"]);self.rows=[]
    def __call__(self,obs,config=None):
        t=self.turn;self.turn+=1
        exact=canonical_action(call_agent(self.base,obs,config))
        all3=apply_option_host(obs,config,exact,self.host,use_rw=True,use_tw=True,use_lq2=True)
        shadow=canonical_action(call_agent(self.shadow,obs,config))
        if START<=t<END_EXCLUSIVE:
            ev=diff_event(all3,shadow,obs,self.seat,t)
            self.rows.append({
              "context_id":self.context_id,
              "turn":int(t),
              "features":numeric_features(obs,self.seat,t,all3),
              "labels":labels_from_event(ev),
              "base_action":all3,
              "teacher_market":shadow.get("market") or [],
            })
        return all3

def run_context(base_main,teacher_main,ctx):
    cand=Collector(base_main,teacher_main,ctx)
    purge_package_modules(teacher_main.parent);opp=load_public_agent(teacher_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(ctx["seed"])},debug=False)
    if int(ctx["seat"])==0:env.run([cand,opp])
    else:env.run([opp,cand])
    p=env.toJSON();st=[str(x) for x in p.get("statuses",[])];rw=[float(x) for x in p.get("rewards",[])];steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or steps<720 or not all(math.isfinite(x) for x in rw):
        raise RuntimeError(f"invalid episode {st} {rw} steps={steps}")
    mine,other=(rw[0],rw[1]) if int(ctx["seat"])==0 else (rw[1],rw[0]);m=mine-other
    if float(score(m))!=float(ctx["base_score"]) or float(m)!=float(ctx["base_margin"]):
        raise RuntimeError(f"BASE replay mismatch {(score(m),m)} != {(ctx['base_score'],ctx['base_margin'])}")
    if len(cand.rows)!=(END_EXCLUSIVE-START):
        raise RuntimeError(f"dataset row count {len(cand.rows)} != {END_EXCLUSIVE-START}")
    return cand.rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--hard-config",required=True);ap.add_argument("--shard-index",type=int,required=True)
    ap.add_argument("--num-shards",type=int,default=4);ap.add_argument("--out",required=True);args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    cfg=json.loads(Path(args.hard_config).read_text());all_ctx=list(cfg.get("hard_contexts") or [])
    selected=[c for i,c in enumerate(all_ctx) if i%args.num_shards==args.shard_index]
    rows=[];failures=[];provenance={};started=time.perf_counter()
    with tempfile.TemporaryDirectory(prefix=f"v18b-ds-s{args.shard_index}-") as td:
        root=Path(td)
        try:
            base_main,rec=acquire_exact(BASE["handle"],BASE["expected_main_sha256"],root/"base")
            provenance["base"]={"ref":BASE["handle"],"sha":BASE["expected_main_sha256"],"receipt":rec}
        except Exception as exc:
            base_main=None;failures.append({"phase":"base_acquire","error":f"{type(exc).__name__}: {exc}"})
        teachers={}
        if base_main is not None:
            uniq={}
            for c in selected:uniq.setdefault(str(c["main_sha256"]),str(c["ref"]))
            for i,(sha,ref) in enumerate(uniq.items()):
                try:
                    main,rec=acquire_exact(ref,sha,root/f"teacher_{i}")
                    teachers[sha]=main;provenance[sha]={"ref":ref,"sha":sha,"receipt":rec}
                    time.sleep(1.0)
                except Exception as exc:
                    failures.append({"phase":"teacher_acquire","ref":ref,"sha":sha,"error":f"{type(exc).__name__}: {exc}"})
        for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):os.environ.pop(k,None)
        if base_main is not None:
            for c in selected:
                teacher=teachers.get(str(c["main_sha256"]))
                if teacher is None:continue
                try:
                    rr=run_context(base_main,teacher,c)
                    for row in rr:
                        row.update({
                          "rank":c.get("rank"),"ref":c["ref"],"main_sha256":c["main_sha256"],
                        })
                    rows.extend(rr)
                    print("V18B_DATA_CONTEXT",json.dumps({"context_id":c["context_id"],"rows":len(rr)},sort_keys=True),flush=True)
                except Exception as exc:
                    failures.append({"phase":"context","context_id":c["context_id"],"error":f"{type(exc).__name__}: {exc}"})
                finally:
                    purge_package_modules(base_main.parent);purge_package_modules(teacher.parent)
    expected=len(selected)*(END_EXCLUSIVE-START)
    mech=(not failures and len(rows)==expected)
    result={
      "schema":"kculture-all3-v18b-p2-dataset-shard-v1","engine":EXPECTED_ENGINE,
      "scope":[START,END_EXCLUSIVE-1],"mechanical_pass":mech,
      "shard_index":args.shard_index,"num_shards":args.num_shards,
      "contexts":len(selected),"expected_rows":expected,"rows":rows,"failures":failures,"provenance":provenance,
      "credentials_removed_before_third_party_execution":True,"automatic_kaggle_submission":False,
      "seconds":time.perf_counter()-started,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V18B_DATA_SHARD_RESULT",json.dumps({"shard":args.shard_index,"mechanical_pass":mech,"rows":len(rows),"failures":len(failures)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
