"""KEXP-042: full-game phase divergence atlas against recent official winners.

Observational/calibration diagnostic. Profiles official top-episode winners and
frozen R4B on the same environmental seeds (R4B vs starter) across coarse game
phases. This does not treat the replayed winner as a counterfactual opponent and
never uses team/episode/seed identity as a deployable feature.
"""
from __future__ import annotations

import argparse, collections, csv, json, statistics, tempfile, sys
from pathlib import Path
import kagglehub
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tools.run_episode import resolve_agent

DATES=("2026-08-24","2026-08-25","2026-08-26")
CHECKPOINTS=(0,96,192,288,384,480,576,648,696,719)
WINDOWS=((0,95),(96,191),(192,287),(288,383),(384,479),(480,575),(576,647),(648,695),(696,718))


def download(handle,filename,out):
    out.mkdir(parents=True,exist_ok=True)
    p=Path(kagglehub.dataset_download(handle,path=filename,output_dir=str(out),force_download=True))
    if not p.is_file(): raise FileNotFoundError(f"missing {handle}:{filename}: {p}")
    return p


def read_csv(path):
    with path.open("r",encoding="utf-8-sig",newline="") as fh:return list(csv.DictReader(fh))


def comp(farm):
    c=collections.Counter()
    for row in farm.get("tiles",[]) or []:
        for t in row or []:
            if not isinstance(t,dict): continue
            if t.get("animal"): c[str(t["animal"])]+=1
            elif t.get("kind")=="PLANT": c[str(t.get("crop"))]+=1
            elif t.get("kind")=="WEED": c["WEED"]+=1
    return c


def checkpoint(rep,p,t):
    steps=rep.get("steps") or []
    if t>=len(steps):return None
    o=steps[t][p].get("observation") or {}; fs=o.get("farms") or []
    if p>=len(fs):return None
    f=fs[p]; c=comp(f)
    return {"money":float(f.get("money",0) or 0),"hands":len(f.get("hands",[]) or []),"quads":len(f.get("unlocked_quadrants",[]) or []),
            "cows":c["COW"],"sheep":c["SHEEP"],"geese":c["GOOSE"],"wheat":c["WHEAT"],"carrot":c["CARROT"],"tomato":c["TOMATO"],"strawberry":c["STRAWBERRY"],"melon":c["MELON"],"weeds":c["WEED"]}


def phase_actions(rep,p,a,b):
    u=collections.Counter(); m=collections.Counter(); mq=collections.Counter()
    steps=rep.get("steps") or []
    # Replay convention: action chosen at state t lives on frame t+1.
    for t in range(a,min(b+1,len(steps)-1)):
        ac=steps[t+1][p].get("action") or {}
        ops=[ac.get("farmer")]+list(ac.get("hands") or [])
        for op in ops:
            if isinstance(op,list) and op:u[str(op[0])]+=1
        for order in list(ac.get("market") or []):
            if not (isinstance(order,list) and order):continue
            typ=str(order[0]); item=str(order[1]) if len(order)>1 else "?"; m[typ]+=1
            if len(order)>=3:
                try:mq[f"{typ}:{item}"]+=int(order[2] or 0)
                except Exception:pass
    return {"unit":dict(u),"market_orders":dict(m),"market_qty":dict(mq)}


def profile(rep,p,label,meta):
    cps={str(t):checkpoint(rep,p,t) for t in CHECKPOINTS}
    phases={f"{a}_{b}":phase_actions(rep,p,a,b) for a,b in WINDOWS}
    final=rep["steps"][-1][p]
    return {"label":label,**meta,"reward":final.get("reward"),"status":final.get("status"),"checkpoints":cps,"phases":phases}


def run_r4b(seed):
    a=resolve_agent("file:candidates/r4b_ablation_market_only.py:agent")
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=True)
    env.run([a,"starter"]);return env.toJSON()


def mean_dict(rows,path,keys):
    out={}
    for k in keys:
        vals=[]
        for r in rows:
            x=r
            try:
                for q in path:x=x[q]
                v=x.get(k,0) if isinstance(x,dict) else 0
                if isinstance(v,(int,float)):vals.append(float(v))
            except Exception:pass
        out[k]=statistics.mean(vals) if vals else None
    return out


def summarize(rows,label):
    rr=[r for r in rows if r["label"]==label]
    cp_keys=("money","hands","quads","cows","sheep","geese","wheat","carrot","tomato","strawberry","melon","weeds")
    market_keys=("BUY_LAND","HIRE","BUY_ANIMAL:COW","BUY_ANIMAL:SHEEP","BUY_ANIMAL:GOOSE","BUY_SEED:WHEAT","BUY_SEED:CARROT","BUY_SEED:TOMATO","BUY_SEED:STRAWBERRY","BUY_SEED:MELON","SELL:WHEAT","SELL:CARROT","SELL:TOMATO","SELL:STRAWBERRY","SELL:EGG","SELL:MILK","SELL:WOOL")
    cps={}
    for t in map(str,CHECKPOINTS):cps[t]=mean_dict(rr,("checkpoints",t),cp_keys)
    phases={}
    for a,b in WINDOWS:
        key=f"{a}_{b}"; vals={}
        for mk in market_keys:
            if ":" in mk:
                vals[mk]=mean_dict(rr,("phases",key,"market_qty"),(mk,))[mk]
            else:
                vals[mk]=mean_dict(rr,("phases",key,"market_orders"),(mk,))[mk]
        for uk in ("PLANT","WATER","HARVEST","DROP","FEED","CARE","PASS"):
            vals[f"UNIT:{uk}"]=mean_dict(rr,("phases",key,"unit"),(uk,))[uk]
        phases[key]=vals
    rewards=[float(r["reward"]) for r in rr if isinstance(r.get("reward"),(int,float))]
    return {"n":len(rr),"mean_reward":statistics.mean(rewards) if rewards else None,"checkpoints":cps,"phases":phases}


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--top",type=int,default=10);ap.add_argument("--output",required=True);args=ap.parse_args()
    rows=[]
    with tempfile.TemporaryDirectory(prefix="kculture-kexp042-") as tmp:
        root=Path(tmp)
        for date in DATES:
            h=f"kaggle/kaggriculture-episodes-{date}"
            man=sorted(read_csv(download(h,"manifest.csv",root/date/"manifest")),key=lambda r:-float(r["avg_score"]))[:args.top]
            for mr in man:
                eid=str(mr["episode_id"]); rep=json.loads(download(h,f"{eid}.json",root/date/eid).read_text(encoding="utf-8"))
                if len(rep.get("steps") or [])<720:continue
                rewards=[rep["steps"][-1][p].get("reward") for p in (0,1)]
                if not all(isinstance(x,(int,float)) for x in rewards):continue
                winner=0 if rewards[0]>=rewards[1] else 1
                seed=int((rep.get("info") or {}).get("seed"))
                rows.append(profile(rep,winner,"live_winner",{"date":date,"episode_id":eid,"seed":seed}))
                rr=run_r4b(seed)
                rows.append(profile(rr,0,"r4b_same_env",{"date":date,"episode_id":eid,"seed":seed}))
    payload={"schema_version":"live-phase-strategy-atlas-v1","dates":list(DATES),"top_n_per_date":args.top,"checkpoints":list(CHECKPOINTS),"windows":[list(x) for x in WINDOWS],"alignment":"state t -> action frame t+1","summary":{"live_winner":summarize(rows,"live_winner"),"r4b_same_env":summarize(rows,"r4b_same_env")},"rows":rows}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps(payload["summary"],indent=2,sort_keys=True))
if __name__=="__main__":main()
