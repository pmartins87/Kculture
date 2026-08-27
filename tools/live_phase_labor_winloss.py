"""KEXP-044: winner-vs-loser phase labor utilization in official top episodes.
Observational only; corrected state t -> action frame t+1 alignment.
"""
from __future__ import annotations
import argparse, collections, csv, json, statistics, tempfile
from pathlib import Path
import kagglehub

DATES=("2026-08-24","2026-08-25","2026-08-26")
WINDOWS=((0,95),(96,191),(192,287),(288,383),(384,479),(480,575),(576,647),(648,695),(696,718))
MOVES={"NORTH","SOUTH","EAST","WEST"}

def dl(handle,name,out):
    out.mkdir(parents=True,exist_ok=True);p=Path(kagglehub.dataset_download(handle,path=name,output_dir=str(out),force_download=True))
    if not p.is_file():raise FileNotFoundError(name)
    return p

def csvrows(p):
    with p.open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))

def phase(rep,p,a,b):
    total=passes=moves=productive=hires=0; ops=collections.Counter()
    steps=rep.get("steps") or []
    for t in range(a,min(b+1,len(steps)-1)):
        ac=steps[t+1][p].get("action") or {}
        for op in [ac.get("farmer")]+list(ac.get("hands") or []):
            if not (isinstance(op,list) and op):continue
            name=str(op[0]);total+=1;ops[name]+=1
            if name=="PASS":passes+=1
            elif name in MOVES:moves+=1
            else:productive+=1
        for order in list(ac.get("market") or []):
            if isinstance(order,list) and order and order[0]=="HIRE":hires+=1
    return {"total":total,"pass":passes,"moves":moves,"productive":productive,"hires":hires,"nonpass_fraction":(total-passes)/total if total else None,"productive_fraction":productive/total if total else None,"pass_per_hire":passes/hires if hires else None,"ops":dict(ops)}

def summarize(rows,cohort):
    rr=[r for r in rows if r["cohort"]==cohort];out={"n":len(rr),"phases":{}}
    for a,b in WINDOWS:
        k=f"{a}_{b}";vals=[r["phases"][k] for r in rr];d={}
        for m in ("total","pass","moves","productive","hires","nonpass_fraction","productive_fraction","pass_per_hire"):
            xs=[float(v[m]) for v in vals if isinstance(v.get(m),(int,float))];d[m]=statistics.mean(xs) if xs else None
        out["phases"][k]=d
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--top",type=int,default=20);ap.add_argument("--output",required=True);args=ap.parse_args();rows=[]
    with tempfile.TemporaryDirectory(prefix="kculture-kexp044-") as tmp:
        root=Path(tmp)
        for date in DATES:
            h=f"kaggle/kaggriculture-episodes-{date}";man=sorted(csvrows(dl(h,"manifest.csv",root/date/"m")),key=lambda r:-float(r["avg_score"]))[:args.top]
            for mr in man:
                eid=str(mr["episode_id"]);rep=json.loads(dl(h,f"{eid}.json",root/date/eid).read_text(encoding="utf-8"));steps=rep.get("steps") or []
                if len(steps)<720:continue
                rew=[steps[-1][p].get("reward") for p in (0,1)]
                if not all(isinstance(x,(int,float)) for x in rew):continue
                best=max(rew)
                for p in (0,1):
                    cohort="winner" if rew[p]==best else "loser"
                    rows.append({"date":date,"episode_id":eid,"player":p,"cohort":cohort,"reward":rew[p],"phases":{f"{a}_{b}":phase(rep,p,a,b) for a,b in WINDOWS}})
    sm={c:summarize(rows,c) for c in ("winner","loser")}
    comparisons={}
    for a,b in WINDOWS:
        k=f"{a}_{b}";w=sm["winner"]["phases"][k];l=sm["loser"]["phases"][k]
        comparisons[k]={"winner_minus_loser_pass":w["pass"]-l["pass"],"winner_minus_loser_nonpass_fraction":w["nonpass_fraction"]-l["nonpass_fraction"],"winner_minus_loser_productive_fraction":w["productive_fraction"]-l["productive_fraction"],"winner_minus_loser_hires":w["hires"]-l["hires"]}
    payload={"schema_version":"live-phase-labor-winloss-v1","dates":list(DATES),"top_n":args.top,"alignment":"state t -> action frame t+1","summary":sm,"comparisons":comparisons,"rows":rows};out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8");print(json.dumps({"summary":sm,"comparisons":comparisons},indent=2,sort_keys=True))
if __name__=="__main__":main()
