#!/usr/bin/env python3
"""V14B MARKET phenotype atlas over all frozen V13C hard contexts.

Observational localization only.  Exact ALL3 is returned to the environment; the exact
hash-pinned hard-source policy is evaluated as an independent shadow teacher on the
candidate observation.  Opponent identity is metadata and never a candidate feature.
"""
from __future__ import annotations
import argparse,collections,json,math,os,statistics,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import (
    EXPECTED_ENGINE,acquire_public_main,load_public_agent,purge_package_modules,sha256_bytes
)
from tools.o_pc1_dev_shard import BASE
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,plain,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.cr087_top_macro_profile import public_counts

CROPS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON")
PRODUCTS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")
QTY_OPS={"SELL","BUY_SEED","BUY_PRODUCT","BUY_ANIMAL"}

def acquire_exact(ref,expected,tmp,attempts=8):
    last=None
    for i in range(attempts):
        try:
            main,receipt=acquire_public_main(ref,tmp/f"try{i}")
            h=sha256_bytes(main.read_bytes())
            if h!=expected:raise RuntimeError(f"source SHA drift {h} != {expected}")
            return main,receipt
        except Exception as exc:
            last=exc
            if i+1<attempts:time.sleep(min(18.0,2.0*(i+1)))
    raise last

def phase(turn):
    if turn<336:return "EARLY"
    if turn<504:return "W2"
    if turn<624:return "W3"
    return "TERMINAL"

def mag_bucket(v):
    a=abs(int(v))
    if a<=1:return "1"
    if a==2:return "2"
    if a<=4:return "3-4"
    return "5+"

def money_bucket(v):
    v=float(v)
    if v<=-5000:return "<=-5000"
    if v<=-1000:return "-4999..-1000"
    if v<1000:return "-999..999"
    if v<5000:return "1000..4999"
    return ">=5000"

def inv_bucket(v):
    v=int(v)
    if v<=0:return "0"
    if v==1:return "1"
    if v<=3:return "2-3"
    return "4+"

def order_parts(order):
    o=list(order or [])
    side=str(o[0]) if o else "EMPTY"
    product=str(o[1]) if len(o)>1 else "_"
    qty=1
    if side in QTY_OPS and len(o)>2:
        try:qty=int(o[2])
        except:qty=1
    return side,product,qty

def market_agg(market):
    qty=collections.Counter();counts=collections.Counter()
    for o in list(market or []):
        side,product,q=order_parts(o)
        qty[(side,product)]+=q
        counts[(side,product)]+=1
    return qty,counts

def sequence_key(market):
    return tuple((order_parts(o)[0],order_parts(o)[1],order_parts(o)[2]) for o in list(market or []))

def kind_counts(farm):
    q=collections.Counter()
    for row in farm.get("tiles",[]) or []:
        for tile in row:
            if isinstance(tile,dict):
                q[str(tile.get("kind"))]+=1
    return q

def state_features(obs,seat,turn):
    p=plain(obs)
    farms=p.get("farms") or []
    own=farms[int(seat)] if len(farms)>int(seat) else {}
    opp=farms[1-int(seat)] if len(farms)>1-int(seat) else {}
    oc=public_counts(own);pc=public_counts(opp);ok=kind_counts(own);pk=kind_counts(opp)
    private=p.get("private") or {}
    shed=private.get("shed") or {}
    seeds=private.get("seeds") or {}
    inventories=private.get("inventories") or []
    carried=collections.Counter()
    for bag in inventories:
        if isinstance(bag,dict):
            for k,v in bag.items():
                try:carried[str(k)]+=int(v or 0)
                except:pass
    prices=((p.get("market") or {}).get("prices") or {})
    money_gap=float(own.get("money",0) or 0)-float(opp.get("money",0) or 0)
    f={
      "turn":int(turn),"phase":phase(turn),
      "own_money":float(own.get("money",0) or 0),"opp_money":float(opp.get("money",0) or 0),
      "money_gap":money_gap,"money_gap_bucket":money_bucket(money_gap),
      "own_quads":len(own.get("unlocked_quadrants") or []),
      "opp_quads":len(opp.get("unlocked_quadrants") or []),
      "own_hands_count":len(own.get("hands") or []),
      "opp_hands_count":len(opp.get("hands") or []),
      "own_hands_state":plain(own.get("hands") or []),
      "own_plants":int(ok.get("PLANT",0)),"opp_plants":int(pk.get("PLANT",0)),
      "own_pastures":int(ok.get("PASTURE",0)+ok.get("COOP",0)),
      "opp_pastures":int(pk.get("PASTURE",0)+pk.get("COOP",0)),
    }
    for x in CROPS:
        a=int(oc.get(f"crop_{x}",0));b=int(pc.get(f"crop_{x}",0))
        f[f"own_crop_{x}"]=a;f[f"opp_crop_{x}"]=b;f[f"crop_gap_{x}"]=a-b
    for x in PRODUCTS:
        sv=int(shed.get(x,0) or 0);cv=int(carried.get(x,0));seed=int(seeds.get(x,0) or 0)
        f[f"shed_{x}"]=sv;f[f"shed_bucket_{x}"]=inv_bucket(sv)
        f[f"carried_{x}"]=cv;f[f"carried_bucket_{x}"]=inv_bucket(cv)
        f[f"seed_{x}"]=seed;f[f"seed_bucket_{x}"]=inv_bucket(seed)
        try:f[f"price_{x}"]=float(prices.get(x,0) or 0)
        except:f[f"price_{x}"]=0.0
    return f

def diff_event(all3,shadow,obs,seat,turn):
    bm=list(all3.get("market") or []);tm=list(shadow.get("market") or [])
    if bm==tm:return None
    bq,bc=market_agg(bm);tq,tc=market_agg(tm)
    keys=sorted(set(bq)|set(tq))
    qty_delta=[]
    presence=[]
    duplicate=[]
    elementary=[]

    count_delta=len(tm)-len(bm)
    if count_delta:
        direction="INC" if count_delta>0 else "DEC"
        group=f"{phase(turn)}|ORDER_COUNT|{mag_bucket(count_delta)}"
        elementary.append({"group_key":group,"direction":direction,"kind":"ORDER_COUNT",
                           "magnitude_bucket":mag_bucket(count_delta),"raw_delta":count_delta})

    for side,product in keys:
        bd=int(bq.get((side,product),0));td=int(tq.get((side,product),0));delta=td-bd
        if delta:
            direction="INC" if delta>0 else "DEC"
            group=f"{phase(turn)}|QTY|{side}|{product}|{mag_bucket(delta)}"
            e={"group_key":group,"direction":direction,"kind":"QTY","side":side,"product":product,
               "magnitude_bucket":mag_bucket(delta),"raw_delta":delta}
            elementary.append(e);qty_delta.append(e)
        bp=bd!=0;tp=td!=0
        if bp!=tp:
            direction="ADD" if tp else "REMOVE"
            group=f"{phase(turn)}|PRESENCE|{side}|{product}"
            e={"group_key":group,"direction":direction,"kind":"PRESENCE","side":side,"product":product}
            elementary.append(e);presence.append(e)
        bdup=max(0,int(bc.get((side,product),0))-1);tdup=max(0,int(tc.get((side,product),0))-1)
        if bdup!=tdup:
            direction="SPLIT" if tdup>bdup else "COMPACT"
            group=f"{phase(turn)}|DUPLICATE|{side}|{product}"
            e={"group_key":group,"direction":direction,"kind":"DUPLICATE","side":side,"product":product,
               "base_extra_duplicates":bdup,"teacher_extra_duplicates":tdup}
            elementary.append(e);duplicate.append(e)

    same_aggregate=(bq==tq)
    reordered=(same_aggregate and sequence_key(bm)!=sequence_key(tm))
    if reordered:
        elementary.append({"group_key":f"{phase(turn)}|REORDER","direction":"REORDER","kind":"REORDER"})

    base_sell=sum(q for (s,_p),q in bq.items() if s=="SELL")
    teacher_sell=sum(q for (s,_p),q in tq.items() if s=="SELL")
    base_buy=sum(q for (s,_p),q in bq.items() if s.startswith("BUY"))
    teacher_buy=sum(q for (s,_p),q in tq.items() if s.startswith("BUY"))
    return {
      "turn":int(turn),"phase":phase(turn),
      "base_market":bm,"teacher_market":tm,
      "base_sequence":list(sequence_key(bm)),"teacher_sequence":list(sequence_key(tm)),
      "base_order_count":len(bm),"teacher_order_count":len(tm),"order_count_delta":count_delta,
      "base_sell_units":base_sell,"teacher_sell_units":teacher_sell,
      "base_buy_units":base_buy,"teacher_buy_units":teacher_buy,
      "same_aggregate":same_aggregate,"reordered_only":reordered,
      "qty_deltas":qty_delta,"presence_deltas":presence,"duplicate_deltas":duplicate,
      "elementary":elementary,
      "state":state_features(obs,seat,turn),
    }

class AtlasCandidate:
    def __init__(self,base_main,teacher_main,ctx):
        purge_package_modules(base_main.parent);purge_package_modules(teacher_main.parent)
        self.base=load_public_agent(base_main)
        purge_package_modules(teacher_main.parent)
        self.shadow=load_public_agent(teacher_main)
        self.state=OptionHostState();self.turn=0;self.seat=int(ctx["seat"]);self.events=[]
    def __call__(self,obs,config=None):
        t=self.turn;self.turn+=1
        exact=canonical_action(call_agent(self.base,obs,config))
        all3=apply_option_host(obs,config,exact,self.state,use_rw=True,use_tw=True,use_lq2=True)
        shadow=canonical_action(call_agent(self.shadow,obs,config))
        ev=diff_event(all3,shadow,obs,self.seat,t)
        if ev is not None:self.events.append(ev)
        return all3

def run_context(base_main,teacher_main,ctx):
    cand=AtlasCandidate(base_main,teacher_main,ctx)
    purge_package_modules(teacher_main.parent)
    opp=load_public_agent(teacher_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(ctx["seed"])},debug=False)
    if int(ctx["seat"])==0:env.run([cand,opp])
    else:env.run([opp,cand])
    p=env.toJSON();st=[str(x) for x in p.get("statuses",[])];rw=[float(x) for x in p.get("rewards",[])];steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or steps<720 or not all(math.isfinite(x) for x in rw):
        raise RuntimeError(f"invalid episode {st} {rw} steps={steps}")
    mine,other=(rw[0],rw[1]) if int(ctx["seat"])==0 else (rw[1],rw[0]);m=mine-other
    if float(score(m))!=float(ctx["base_score"]) or float(m)!=float(ctx["base_margin"]):
        raise RuntimeError(f"BASE replay mismatch {(score(m),m)} != {(ctx['base_score'],ctx['base_margin'])}")
    return cand.events

def family_atlas(event_rows):
    occ=collections.defaultdict(list)
    for row in event_rows:
        for e in row["event"]["elementary"]:
            occ[e["group_key"]].append({
              "direction":e["direction"],"context_id":row["context_id"],"main_sha256":row["main_sha256"],
              "turn":row["event"]["turn"],"state":row["event"]["state"],"element":e
            })
    families=[]
    for group,rr in occ.items():
        dirs=collections.Counter(x["direction"] for x in rr)
        direction,count=sorted(dirs.items(),key=lambda kv:(-kv[1],kv[0]))[0]
        share=count/len(rr)
        dom=[x for x in rr if x["direction"]==direction]
        contexts=sorted({x["context_id"] for x in dom})
        sources=sorted({x["main_sha256"] for x in dom})
        turns=[int(x["turn"]) for x in dom]
        phases=collections.Counter(x["state"]["phase"] for x in dom)
        money=collections.Counter(x["state"]["money_gap_bucket"] for x in dom)
        fam={
          "group_key":group,"dominant_direction":direction,"direction_share":share,
          "occurrences":len(rr),"dominant_occurrences":len(dom),
          "context_support":len(contexts),"source_support":len(sources),
          "contexts":contexts,"source_shas":sources,
          "median_turn":statistics.median(turns) if turns else None,
          "phase_counts":dict(sorted(phases.items())),
          "money_gap_bucket_counts":dict(sorted(money.items())),
          "representative_element":dom[0]["element"] if dom else None,
        }
        fam["recurrent"]=(
          fam["context_support"]>=4 and fam["source_support"]>=2 and fam["direction_share"]>=0.75
        )
        families.append(fam)
    families.sort(key=lambda x:(-x["source_support"],-x["context_support"],
                                float(x["median_turn"] if x["median_turn"] is not None else 10**9),
                                x["group_key"],x["dominant_direction"]))
    recurrent=[x for x in families if x["recurrent"]]
    return families,recurrent

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hard-config",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    cfg=json.loads(Path(args.hard_config).read_text());contexts=list(cfg.get("hard_contexts") or [])
    if len(contexts)!=24:raise SystemExit("expected exactly 24 binding hard contexts")
    failures=[];event_rows=[];processed_contexts=[];provenance={};started=time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="v14b-market-atlas-") as td:
        root=Path(td)
        try:
            base_main,rec=acquire_exact(BASE["handle"],BASE["expected_main_sha256"],root/"base")
            provenance["base"]={"ref":BASE["handle"],"sha":BASE["expected_main_sha256"],"receipt":rec}
        except Exception as exc:
            base_main=None;failures.append({"phase":"base_acquire","error":f"{type(exc).__name__}: {exc}"})
        teachers={}
        source_ref={}
        if base_main is not None:
            for c in contexts:
                sha=str(c["main_sha256"])
                source_ref.setdefault(sha,str(c["ref"]))
            for i,(sha,ref) in enumerate(source_ref.items()):
                try:
                    main,rec=acquire_exact(ref,sha,root/f"teacher_{i}")
                    teachers[sha]=main;provenance[sha]={"ref":ref,"sha":sha,"receipt":rec}
                    print("V14B_ACQUIRE",json.dumps({"ref":ref,"sha":sha},sort_keys=True),flush=True)
                    time.sleep(1.0)
                except Exception as exc:
                    failures.append({"phase":"teacher_acquire","ref":ref,"sha":sha,"error":f"{type(exc).__name__}: {exc}"})
        for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):os.environ.pop(k,None)
        if base_main is not None:
            for c in contexts:
                teacher=teachers.get(str(c["main_sha256"]))
                if teacher is None:continue
                try:
                    events=run_context(base_main,teacher,c)
                    processed_contexts.append(c["context_id"])
                    for ev in events:
                        event_rows.append({
                          "context_id":c["context_id"],"rank":c.get("rank"),"ref":c["ref"],
                          "main_sha256":c["main_sha256"],"seed":c["seed"],"seat":c["seat"],"event":ev
                        })
                    print("V14B_CONTEXT",json.dumps({"context_id":c["context_id"],"rank":c.get("rank"),
                      "events":len(events),"first_turn":events[0]["turn"] if events else None},sort_keys=True),flush=True)
                except Exception as exc:
                    failures.append({"phase":"context","context_id":c["context_id"],"error":f"{type(exc).__name__}: {exc}"})
                finally:
                    purge_package_modules(base_main.parent);purge_package_modules(teacher.parent)

    families,recurrent=family_atlas(event_rows)
    mech=(not failures and len(set(processed_contexts))==24)
    if not mech:decision="V14B_MECHANICS_INVALID"
    elif recurrent:decision="V14B_RECURRENT_DOMAIN_PHENOTYPE_READY"
    else:decision="V14B_DOMAIN_HEADROOM_NOT_COMPRESSIBLE"
    selected=recurrent[0] if recurrent else None
    result={
      "schema":"kculture-all3-v14b-market-phenotype-atlas-v1","engine":EXPECTED_ENGINE,
      "mechanical_pass":mech,"decision":decision,"contexts":24,
      "processed_contexts":sorted(set(processed_contexts)),
      "contexts_with_divergence":len({r["context_id"] for r in event_rows}),
      "contexts_without_divergence":sorted(set(processed_contexts)-{r["context_id"] for r in event_rows}),
      "market_divergence_events":len(event_rows),
      "families":families,"recurrent_families":recurrent,"selected_phenotype":selected,
      "event_rows":event_rows,"failures":failures,"provenance":provenance,
      "runtime_identity_feature_allowed":False,"automatic_kaggle_submission":False,
      "seconds":time.perf_counter()-started,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V14B_RESULT",json.dumps({
      "decision":decision,"mechanical_pass":mech,"market_divergence_events":len(event_rows),
      "family_count":len(families),"recurrent_count":len(recurrent),
      "selected_phenotype":selected,
      "top_recurrent":recurrent[:10],"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
