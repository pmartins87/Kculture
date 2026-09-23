#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from collections import defaultdict,Counter
from pathlib import Path

CANDS=("ALL3","V47","ORW1","CR053","CR029")

def mean(xs): return statistics.fmean(xs) if xs else None
def med(xs): return statistics.median(xs) if xs else None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    d=json.loads(Path(a.input).read_text())
    if d.get("decision")!="V28F_NO_MATERIAL_HEDGE_REPLACEMENT" or not d.get("mechanical_pass"):
        raise SystemExit("V28F aggregate not binding/valid")
    rows=list(d.get("rows") or [])
    ctx=defaultdict(dict)
    for r in rows:
        key=(str(r["main_sha256"]),int(r["seed"]),int(r["seat"]))
        ctx[key][str(r["candidate"])]=r
    if len(ctx)!=144 or any(set(v)!=set(CANDS) for v in ctx.values()):
        raise SystemExit(f"context matrix invalid contexts={len(ctx)}")

    losses=[]
    for key,vals in ctx.items():
        p=vals["ALL3"]
        if float(p["score"])==0.0:
            losses.append((key,vals))
    if len(losses)!=66:
        raise SystemExit(f"expected 66 ALL3 losses, found {len(losses)}")

    source=defaultdict(list)
    for key,vals in ctx.items():
        source[key[0]].append(vals)
    source_rows=[]
    for sha,groups in source.items():
        all3=[v["ALL3"] for v in groups]
        l=[r for r in all3 if float(r["score"])==0.0]
        example=groups[0]["ALL3"]
        lm=[float(r["margin"]) for r in l]
        source_rows.append({
          "main_sha256":sha,
          "representative_ref":example.get("ref"),
          "representative_rank":int(example.get("source_rank")),
          "contexts":len(all3),
          "wins":sum(float(r["score"])==1.0 for r in all3),
          "losses":len(l),
          "loss_rate":len(l)/len(all3),
          "mean_margin":mean([float(r["margin"]) for r in all3]),
          "median_loss_margin":med(lm),
          "losses_by_seat":{str(seat):sum(int(r["seat"])==seat for r in l) for seat in (0,1)},
          "distinct_losing_seeds":len({int(r["seed"]) for r in l}),
          "close_losses":sum(float(r["margin"])>=-2000 for r in l),
          "medium_losses":sum(-10000<float(r["margin"])<-2000 for r in l),
          "severe_losses":sum(float(r["margin"])<=-10000 for r in l),
        })
    source_rows.sort(key=lambda x:(-x["losses"],x["representative_rank"],x["main_sha256"]))
    total_losses=len(losses)
    def share(n): return sum(x["losses"] for x in source_rows[:n])/total_losses

    seats={}
    for seat in (0,1):
        gs=[v["ALL3"] for (sha,seed,s),v in ctx.items() if s==seat]
        seats[str(seat)]={"contexts":len(gs),"losses":sum(float(r["score"])==0.0 for r in gs),"loss_rate":sum(float(r["score"])==0.0 for r in gs)/len(gs)}
    seeds={}
    for seed in sorted({k[1] for k in ctx}):
        gs=[v["ALL3"] for (sha,se,s),v in ctx.items() if se==seed]
        seeds[str(seed)]={"contexts":len(gs),"losses":sum(float(r["score"])==0.0 for r in gs),"loss_rate":sum(float(r["score"])==0.0 for r in gs)/len(gs)}

    universal=0
    delta={}
    for h in ("V47","ORW1"):
        ds=[]; better=equal=worse=0
        for _,vals in losses:
            x=float(vals["ALL3"]["margin"])-float(vals[h]["margin"])
            ds.append(x)
            if x>0: better+=1
            elif x<0: worse+=1
            else: equal+=1
        delta[h]={"mean_all3_minus_hedge_margin":mean(ds),"median_delta":med(ds),"all3_better":better,"equal":equal,"all3_worse":worse}
    for _,vals in losses:
        if all(float(vals[h]["score"])==0.0 for h in ("V47","ORW1","CR053","CR029")):
            universal+=1

    # deterministic diverse selection helper
    def diverse_pick(items,limit,reverse):
        # items tuples (margin, key, vals), already losses only
        ordered=sorted(items,key=lambda z:((-z[0]) if reverse else z[0],int(z[2]["ALL3"]["source_rank"]),z[1][1],z[1][2]))
        picked=[]; used=Counter()
        # first pass source diversity
        for item in ordered:
            sha=item[0+1][0]
            if used[sha]==0:
                picked.append(item); used[sha]+=1
                if len(picked)>=limit:return picked
        # second pass allow second etc
        for item in ordered:
            if item in picked: continue
            picked.append(item)
            if len(picked)>=limit:return picked
        return picked

    items=[(float(vals["ALL3"]["margin"]),key,vals) for key,vals in losses]
    close=diverse_pick(items,6,True)
    severe=diverse_pick(items,6,False)
    chosen=[]; seen=set()
    for label,arr in (("close",close),("severe",severe)):
        for margin,key,vals in arr:
            ident=(key[0],key[1],key[2])
            if ident in seen: continue
            seen.add(ident)
            p=vals["ALL3"]
            chosen.append({
              "bucket":label,"main_sha256":key[0],"representative_ref":p.get("ref"),"representative_rank":int(p.get("source_rank")),
              "seed":key[1],"seat":key[2],"all3_margin":margin,
              "candidate_margins":{c:float(vals[c]["margin"]) for c in CANDS},
              "candidate_scores":{c:float(vals[c]["score"]) for c in CANDS},
            })

    clustered=share(4)>=0.60
    decision="V28G_SOURCE_CLUSTERED_HARD_CORE" if clustered else "V28G_BROAD_HARD_CORE"
    out={
      "schema":"kculture-v28g-residual-hard-core-census-v1",
      "source_v28f_workflow":35807910104,
      "mechanical_pass":True,
      "decision":decision,
      "contexts":len(ctx),"all3_residual_losses":total_losses,
      "universal_hard_losses":universal,"all_expected_losses_universal_hard":universal==total_losses,
      "loss_severity":{
        "close":sum(float(vals["ALL3"]["margin"])>=-2000 for _,vals in losses),
        "medium":sum(-10000<float(vals["ALL3"]["margin"])<-2000 for _,vals in losses),
        "severe":sum(float(vals["ALL3"]["margin"])<=-10000 for _,vals in losses),
      },
      "source_concentration":{
        "top1_share":share(1),"top2_share":share(2),"top4_share":share(4),
        "systematic_sources_ge9_losses":sum(x["losses"]>=9 for x in source_rows),
        "moderate_sources_6_to_8_losses":sum(6<=x["losses"]<=8 for x in source_rows),
        "low_sources_1_to_5_losses":sum(1<=x["losses"]<=5 for x in source_rows),
        "zero_loss_sources":sum(x["losses"]==0 for x in source_rows),
      },
      "by_source":source_rows,
      "by_seat":seats,"by_seed":seeds,
      "overlay_margin_effect_on_all3_losses":delta,
      "trace_targets":chosen,
      "automatic_kaggle_submission":False,
    }
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V28G_RESULT",json.dumps({
      "decision":decision,"all3_residual_losses":total_losses,"universal_hard_losses":universal,
      "loss_severity":out["loss_severity"],"source_concentration":out["source_concentration"],
      "top_sources":source_rows[:6],"by_seat":seats,"by_seed":seeds,
      "overlay_margin_effect":delta,"trace_targets":chosen
    },sort_keys=True),flush=True)

if __name__=="__main__": main()
