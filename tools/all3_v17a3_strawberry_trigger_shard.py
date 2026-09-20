#!/usr/bin/env python3
"""V17A3 baseline-only trigger audit shard for selected STRAWBERRY bundle."""
from __future__ import annotations
import argparse,json,math,os,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,acquire_public_main,load_public_agent,purge_package_modules,sha256_bytes
from tools.o_pc1_dev_shard import BASE
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,plain,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host

REAL_PRODUCTS={"WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER"}

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

def normalize_element(e):
    kind=str(e.get("kind",""));direction=str(e.get("direction",""))
    if kind=="QTY":
        side=str(e.get("side",""));product=str(e.get("product",""));bucket=str(e.get("magnitude_bucket",""))
        if side!="SELL" or product not in REAL_PRODUCTS:return None
        return f"QTY|SELL|{product}|{bucket}|{direction}"
    if kind=="PRESENCE":
        side=str(e.get("side",""));product=str(e.get("product",""))
        if side!="SELL" or product not in REAL_PRODUCTS:return None
        return f"PRESENCE|SELL|{product}|{direction}"
    if kind=="DUPLICATE":
        side=str(e.get("side",""));product=str(e.get("product",""))
        if side!="SELL" or product not in REAL_PRODUCTS:return None
        return f"DUPLICATE|SELL|{product}|{direction}"
    if kind=="ORDER_COUNT":
        return f"ORDER_COUNT|{e.get('magnitude_bucket')}|{direction}"
    if kind=="REORDER":
        return f"REORDER|{direction}"
    return None

def selected_target_keys(atlas):
    recurrent_groups={str(x["group_key"]) for x in atlas.get("recurrent_families",[]) if x.get("recurrent")}
    target=set()
    for row in atlas.get("event_rows") or []:
        ev=row.get("event") or {}
        if ev.get("phase")!="W2":continue
        sigs=[]
        for e in ev.get("elementary") or []:
            if str(e.get("group_key","")) not in recurrent_groups:continue
            n=normalize_element(e)
            if n:sigs.append(n)
        sigs=sorted(set(sigs))
        if sigs==["PRESENCE|SELL|STRAWBERRY|ADD","QTY|SELL|STRAWBERRY|2|INC"]:
            target.add((str(row["context_id"]),int(ev["turn"])))
    if len(target)!=42:
        raise RuntimeError(f"binding target set mismatch {len(target)} != 42")
    return target

def own_strawberry(obs):
    p=plain(obs)
    private=p.get("private") or {}
    shed=private.get("shed") or {}
    try:shed_q=int(shed.get("STRAWBERRY",0) or 0)
    except:shed_q=0
    carried=0
    for bag in private.get("inventories") or []:
        if isinstance(bag,dict):
            try:carried+=int(bag.get("STRAWBERRY",0) or 0)
            except:pass
    return shed_q,carried

def market_has_nonempty(action):
    return any(bool(list(x or [])) for x in (action.get("market") or []))

class Candidate:
    def __init__(self,base_main,context_id):
        purge_package_modules(base_main.parent)
        self.agent=load_public_agent(base_main)
        self.host=OptionHostState()
        self.turn=0
        self.context_id=context_id
        self.hits={k:[] for k in ("T0_AVAILABLE","T1_CARRIED20","T2_SHED2","T3_CARRIED20_OR_SHED2")}
        self.audit=[]
    def __call__(self,obs,config=None):
        t=self.turn;self.turn+=1
        exact=canonical_action(call_agent(self.agent,obs,config))
        all3=apply_option_host(obs,config,exact,self.host,use_rw=True,use_tw=True,use_lq2=True)
        if 336<=t<504:
            shed,carried=own_strawberry(obs)
            total=shed+carried
            empty=not market_has_nonempty(all3)
            common=empty and total>=2
            flags={
              "T0_AVAILABLE":common,
              "T1_CARRIED20":common and carried>=20,
              "T2_SHED2":common and shed>=2,
              "T3_CARRIED20_OR_SHED2":common and (carried>=20 or shed>=2),
            }
            for name,v in flags.items():
                if v:self.hits[name].append([self.context_id,t])
            if any(flags.values()):
                self.audit.append({
                  "turn":t,"shed_strawberry":shed,"carried_strawberry":carried,
                  "total_strawberry":total,"market":all3.get("market") or [],
                  "flags":flags,
                })
        return all3

def run(base_main,opp_main,ctx):
    purge_package_modules(base_main.parent);purge_package_modules(opp_main.parent)
    cand=Candidate(base_main,str(ctx["context_id"]))
    purge_package_modules(opp_main.parent);opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(ctx["seed"])},debug=False)
    if int(ctx["seat"])==0:env.run([cand,opp])
    else:env.run([opp,cand])
    p=env.toJSON();st=[str(x) for x in p.get("statuses",[])];rw=[float(x) for x in p.get("rewards",[])];steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or steps<720 or not all(math.isfinite(x) for x in rw):
        raise RuntimeError(f"invalid episode {st} {rw} steps={steps}")
    mine,other=(rw[0],rw[1]) if int(ctx["seat"])==0 else (rw[1],rw[0]);m=mine-other
    if float(score(m))!=float(ctx["base_score"]) or float(m)!=float(ctx["base_margin"]):
        raise RuntimeError(f"BASE replay mismatch {(score(m),m)} != {(ctx['base_score'],ctx['base_margin'])}")
    return {"score":score(m),"margin":m,"hits":cand.hits,"audit":cand.audit}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--hard-config",required=True);ap.add_argument("--atlas",required=True)
    ap.add_argument("--shard-index",type=int,required=True);ap.add_argument("--num-shards",type=int,default=4)
    ap.add_argument("--out",required=True);args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")

    cfg=json.loads(Path(args.hard_config).read_text());all_ctx=list(cfg.get("hard_contexts") or [])
    atlas=json.loads(Path(args.atlas).read_text());targets=selected_target_keys(atlas)
    selected=[c for i,c in enumerate(all_ctx) if i%args.num_shards==args.shard_index]
    assigned_ids={str(c["context_id"]) for c in selected}
    assigned_targets=sorted([list(x) for x in targets if x[0] in assigned_ids])

    rows=[];failures=[];provenance={};started=time.perf_counter()
    with tempfile.TemporaryDirectory(prefix=f"v17a3-s{args.shard_index}-") as td:
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
                opp=teachers.get(str(c["main_sha256"]))
                if opp is None:continue
                try:
                    rr=run(base_main,opp,c)
                    row={
                      "context_id":c["context_id"],"rank":c.get("rank"),"ref":c["ref"],"main_sha256":c["main_sha256"],
                      "seed":c["seed"],"seat":c["seat"],"score":rr["score"],"margin":rr["margin"],
                      "hits":rr["hits"],"audit":rr["audit"],
                    }
                    rows.append(row)
                    print("V17A3_CONTEXT",json.dumps({
                      "context_id":c["context_id"],
                      "hits":{k:len(v) for k,v in rr["hits"].items()}
                    },sort_keys=True),flush=True)
                except Exception as exc:
                    failures.append({"phase":"context","context_id":c["context_id"],"error":f"{type(exc).__name__}: {exc}"})
                finally:
                    purge_package_modules(base_main.parent);purge_package_modules(opp.parent)

    mech=(not failures and len(rows)==len(selected))
    result={
      "schema":"kculture-all3-v17a3-trigger-audit-shard-v1","engine":EXPECTED_ENGINE,
      "mechanical_pass":mech,"shard_index":args.shard_index,"num_shards":args.num_shards,
      "assigned_contexts":len(selected),"rows":rows,"assigned_targets":assigned_targets,
      "failures":failures,"provenance":provenance,
      "automatic_kaggle_submission":False,"seconds":time.perf_counter()-started,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V17A3_SHARD_RESULT",json.dumps({
      "shard":args.shard_index,"mechanical_pass":mech,"contexts":len(rows),
      "targets":len(assigned_targets),"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
