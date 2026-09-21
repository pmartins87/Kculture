#!/usr/bin/env python3
"""V24A coupled divergence trace shard over immutable V23 hard contexts."""
from __future__ import annotations
import argparse, collections, copy, json, math, os, sys
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from solver.programme_features import features as programme_features
from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE, load_public_agent, purge_package_modules, sha256_bytes
from tools.bounded_transaction_oracle_v1 import action_key, call_agent, canonical_action, plain, score
from tools.first_party_option_host_v1 import OptionHostState, apply_option_host
from tools.o_pc1_dev_shard import BASE

MAX_LAG=3

def physical_kind(a,b):
    farmer=a["farmer"]!=b["farmer"]
    hands=a["hands"]!=b["hands"]
    if farmer and hands:return "farmer+hands"
    if farmer:return "farmer"
    if hands:return "hands"
    return "same"

def verb_profile(orders):
    c=collections.Counter()
    for o in list(orders or []):
        verb=str(o[0]) if o else "EMPTY"
        c[verb]+=1
    return dict(sorted(c.items()))

def action_snapshot(a):
    return {
      "action_key":action_key(a),
      "market":copy.deepcopy(a["market"]),
      "farmer":copy.deepcopy(a["farmer"]),
      "hands":copy.deepcopy(a["hands"]),
      "market_verb_profile":verb_profile(a["market"]),
    }

class TraceCandidate:
    def __init__(self,base_main,teacher_main,cluster,annotation):
        purge_package_modules(base_main.parent);purge_package_modules(teacher_main.parent)
        self.base=load_public_agent(base_main)
        purge_package_modules(teacher_main.parent)
        self.teacher=load_public_agent(teacher_main)
        self.host=OptionHostState()
        self.cluster=cluster
        self.annotation=annotation
        self.turn=0
        self.first_events={}
        self.recent_market_only=[]
        self.recent_physical_only=[]

    def _record(self,family,topology,kind,lag,start,end):
        if family in self.first_events:return
        self.first_events[family]={
          "family":family,"topology":topology,"physical_kind":kind,"lag":int(lag),
          "start_step":int(start["step"]),"end_step":int(end["step"]),
          "start_base":start["base"],"start_shadow":start["shadow"],
          "end_base":end["base"],"end_shadow":end["shadow"],
          "end_state_features_114":end["features"],
          "cluster":self.cluster,"annotation":self.annotation,
        }

    def __call__(self,obs,config=None):
        step=int(plain(obs).get("step",self.turn));self.turn+=1
        exact=canonical_action(call_agent(self.base,obs,config))
        all3=apply_option_host(obs,config,exact,self.host,use_rw=True,use_tw=True,use_lq2=True)
        shadow=canonical_action(call_agent(self.teacher,obs,config))
        m=all3["market"]!=shadow["market"]
        kind=physical_kind(all3,shadow)
        p=kind!="same"
        row={
          "step":step,
          "base":action_snapshot(all3),
          "shadow":action_snapshot(shadow),
          "features":[float(x) for x in programme_features(plain(obs)).tolist()],
        }

        if m and p:
            self._record(f"SAME|{kind}|0","SAME",kind,0,row,row)

        if p:
            for prev in reversed(self.recent_market_only):
                lag=step-int(prev["step"])
                if lag>MAX_LAG:break
                if 1<=lag<=MAX_LAG:
                    self._record(f"M_TO_P|{kind}|{lag}","M_TO_P",kind,lag,prev,row)

        if m:
            for prev in reversed(self.recent_physical_only):
                lag=step-int(prev["step"])
                if lag>MAX_LAG:break
                if 1<=lag<=MAX_LAG:
                    pk=str(prev["kind"])
                    self._record(f"P_TO_M|{pk}|{lag}","P_TO_M",pk,lag,prev["row"],row)

        if m and not p:
            self.recent_market_only.append(row)
            self.recent_market_only=[x for x in self.recent_market_only if step-int(x["step"])<=MAX_LAG]
        if p and not m:
            self.recent_physical_only.append({"step":step,"kind":kind,"row":row})
            self.recent_physical_only=[x for x in self.recent_physical_only if step-int(x["step"])<=MAX_LAG]

        return shadow

def run_one(base_main,teacher_main,ctx,cluster,annotation):
    cand=TraceCandidate(base_main,teacher_main,cluster,annotation)
    purge_package_modules(teacher_main.parent)
    opp=load_public_agent(teacher_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(ctx["seed"])},debug=False)
    if int(ctx["seat"])==0:env.run([cand,opp])
    else:env.run([opp,cand])
    p=env.toJSON()
    statuses=[str(x) for x in p.get("statuses",[])]
    rewards=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    if statuses!=["DONE","DONE"] or len(rewards)!=2 or steps<720 or not all(math.isfinite(x) for x in rewards):
        raise RuntimeError(f"invalid episode statuses={statuses} rewards={rewards} steps={steps}")
    mine,other=(rewards[0],rewards[1]) if int(ctx["seat"])==0 else (rewards[1],rewards[0])
    margin=mine-other
    return {
      "score":float(score(margin)),"margin":float(margin),"rewards":rewards,"steps":steps,
      "events":sorted(cand.first_events.values(),key=lambda x:(x["end_step"],x["family"])),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--hard-config",required=True)
    ap.add_argument("--cluster-map",required=True)
    ap.add_argument("--v23b-aggregate",required=True)
    ap.add_argument("--snapshot-dir",required=True)
    ap.add_argument("--shard-index",type=int,required=True)
    ap.add_argument("--num-shards",type=int,default=4)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")

    cfg=json.loads(Path(args.hard_config).read_text())
    cmap=json.loads(Path(args.cluster_map).read_text())
    agg=json.loads(Path(args.v23b_aggregate).read_text())
    if agg.get("decision")!="V23B_CROSS_DOMAIN_INTERACTION_HEADROOM" or not agg.get("mechanical_pass"):
        raise SystemExit("binding V23B interaction result mismatch")

    full={str(r["context_id"]):r for r in agg["rows"] if r["mode"]=="FULL_SHADOW"}
    market={str(r["context_id"]):r for r in agg["rows"] if r["mode"]=="MARKET_ONLY"}
    physical={str(r["context_id"]):r for r in agg["rows"] if r["mode"]=="PHYSICAL_ONLY"}
    sha2cluster=dict(cmap["sha_to_cluster"])

    root=Path(args.snapshot_dir)
    manifest=json.loads((root/"MANIFEST.json").read_text())
    base_main=root/manifest["base"]["path"]
    if sha256_bytes(base_main.read_bytes())!=BASE["expected_main_sha256"]:raise SystemExit("base snapshot SHA mismatch")
    paths={}
    for src in manifest["sources"]:
        p=root/src["path"]
        if sha256_bytes(p.read_bytes())!=src["sha"]:raise SystemExit(f"snapshot SHA mismatch {src['sha']}")
        paths[src["sha"]]=p

    contexts=list(cfg["hard_contexts"])
    selected=[c for i,c in enumerate(contexts) if i%args.num_shards==args.shard_index]
    rows=[];failures=[]

    for key in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):os.environ.pop(key,None)

    for ctx in selected:
        cid=str(ctx["context_id"]);sha=str(ctx["main_sha256"])
        try:
            teacher=paths[sha]
            fr=full[cid];mr=market[cid];pr=physical[cid]
            annotation="INTERACTION_EXCLUSIVE" if float(fr["score_delta"])>0 and float(mr["score_delta"])<=0 and float(pr["score_delta"])<=0 else "OTHER_HARD"
            rr=run_one(base_main,teacher,ctx,sha2cluster[sha],annotation)
            if float(rr["score"])!=float(fr["treatment_score"]) or float(rr["margin"])!=float(fr["treatment_margin"]):
                raise RuntimeError(f"FULL_SHADOW replay mismatch {(rr['score'],rr['margin'])} != {(fr['treatment_score'],fr['treatment_margin'])}")
            row={
              "context_id":cid,"source_rank":ctx["rank"],"ref":ctx["ref"],"main_sha256":sha,
              "cluster":sha2cluster[sha],"seed":int(ctx["seed"]),"seat":int(ctx["seat"]),
              "annotation":annotation,"full_score":rr["score"],"full_margin":rr["margin"],
              "event_count":len(rr["events"]),"events":rr["events"],
            }
            rows.append(row)
            print("V24A_CONTEXT",json.dumps({"context_id":cid,"rank":ctx["rank"],"cluster":sha2cluster[sha],"seed":ctx["seed"],"seat":ctx["seat"],"annotation":annotation,"event_count":len(rr["events"])},sort_keys=True),flush=True)
        except Exception as exc:
            failures.append({"context_id":cid,"sha":sha,"seed":ctx["seed"],"seat":ctx["seat"],"error":f"{type(exc).__name__}: {exc}"})
        finally:
            purge_package_modules(base_main.parent)
            if sha in paths:purge_package_modules(paths[sha].parent)

    mechanical_pass=not failures and len(rows)==len(selected)
    result={
      "schema":"kculture-all3-v24a-coupled-divergence-trace-shard-v1",
      "mechanical_pass":mechanical_pass,"shard_index":args.shard_index,"num_shards":args.num_shards,
      "contexts_assigned":len(selected),"rows":rows,"failures":failures,
      "max_compact_lag":MAX_LAG,"immutable_snapshot_used":True,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V24A_SHARD_RESULT",json.dumps({"shard":args.shard_index,"mechanical_pass":mechanical_pass,"contexts":len(rows),"failures":len(failures)},sort_keys=True),flush=True)
    if not mechanical_pass:raise SystemExit(2)

if __name__=="__main__":
    main()
