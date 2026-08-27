"""KEXP-051: paired-world causal value audit for KEXP-045 double JIT CARROT.

For development and exploratory live-meta environmental seeds, both seats:
A = KEXP-045 vs frozen R4B
B = frozen R4B vs frozen R4B
Compare same-seat own reward, opponent reward and relative reward. Also record
whether the two 614->615 and 619->620 conversions actually triggered.
Diagnostic only; no validation or held-out access.
"""
from __future__ import annotations
import argparse, json, statistics, sys
from pathlib import Path
from kaggle_environments import make
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tools.run_episode import resolve_agent
CAND="file:candidates/r4d_jit_carrot_two.py:agent"
BASE="file:candidates/r4b_ablation_market_only.py:agent"
PAIRS=((614,615),(619,620))

def live_seeds(path):
    obj=json.loads(path.read_text(encoding="utf-8"));out=[]
    def walk(v):
        if isinstance(v,dict):
            if isinstance(v.get("seed"),int): out.append(v["seed"])
            for x in v.values(): walk(x)
        elif isinstance(v,list):
            for x in v: walk(x)
    walk(obj);return list(dict.fromkeys(out))

def run_world(seed,seat,candidate):
    c=resolve_agent(CAND if candidate else BASE);o=resolve_agent(BASE)
    agents=[c,o] if seat==0 else [o,c]
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=True);env.run(agents);return env.toJSON()

def action(rep,t,p): return (rep["steps"][t+1][p].get("action") or {}) if t+1<len(rep["steps"]) else {}
def mq(a,op,item):
    q=0
    for r in list((a or {}).get("market") or []):
        if isinstance(r,list) and len(r)>=3 and r[:2]==[op,item]:
            try:q+=max(0,int(r[2] or 0))
            except Exception:pass
    return q

def pc(a,crop):
    ops=[(a or {}).get("farmer"),*list((a or {}).get("hands") or [])]
    return sum(isinstance(o,list) and len(o)>=2 and o[:2]==["PLANT",crop] for o in ops)
def final(rep,p):
    x=rep["steps"][-1][p];return x.get("status"),x.get("reward")
def mean(xs):
    xs=[float(x) for x in xs if isinstance(x,(int,float))];return statistics.mean(xs) if xs else None
def median(xs):
    xs=[float(x) for x in xs if isinstance(x,(int,float))];return statistics.median(xs) if xs else None

def summarize(rows):
    valid=[r for r in rows if not r["error"]];tr=[r for r in valid if r["conversions"]>0];quiet=[r for r in valid if r["conversions"]==0]
    def block(rr):
        return {"n":len(rr),"mean_own_delta":mean([r["own_delta"] for r in rr]),"median_own_delta":median([r["own_delta"] for r in rr]),"mean_opponent_externality":mean([r["opponent_externality"] for r in rr]),"mean_relative_delta":mean([r["relative_delta"] for r in rr]),"positive_own_fraction":sum(r["own_delta"]>0 for r in rr)/len(rr) if rr else None,"positive_relative_fraction":sum(r["relative_delta"]>0 for r in rr)/len(rr) if rr else None}
    return {"n":len(rows),"errors":len(rows)-len(valid),"triggered_n":len(tr),"quiet_n":len(quiet),"all":block(valid),"triggered":block(tr),"seat0_triggered":block([r for r in tr if r["seat"]==0]),"seat1_triggered":block([r for r in tr if r["seat"]==1])}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--output",required=True);args=ap.parse_args()
    dev=json.loads((ROOT/"configs/seed_partitions.json").read_text(encoding="utf-8"))["development"]
    live=live_seeds(ROOT/"configs/exploratory_live_meta_seeds_20260825.json")
    rows=[]
    for seed,source in [(s,"development") for s in dev]+[(s,"live_meta") for s in live]:
        for seat in (0,1):
            a=run_world(seed,seat,True);b=run_world(seed,seat,False);opp=1-seat
            sa,ra=final(a,seat);soa,roa=final(a,opp);sb,rb=final(b,seat);sob,rob=final(b,opp)
            error=not(sa==soa==sb==sob=="DONE" and all(isinstance(x,(int,float)) for x in (ra,roa,rb,rob)))
            conv=0;details={}
            for buy,plant in PAIRS:
                ca,ba=action(a,buy,seat),action(b,buy,seat);cp,bp=action(a,plant,seat),action(b,plant,seat)
                added=mq(ca,"BUY_SEED","CARROT")-mq(ba,"BUY_SEED","CARROT");dc=pc(cp,"CARROT")-pc(bp,"CARROT");dw=pc(cp,"WHEAT")-pc(bp,"WHEAT")
                ok=added>0 and dc>0 and dw<0;conv+=int(ok);details[f"{buy}_{plant}"]={"added_buy":added,"delta_carrot_plants":dc,"delta_wheat_plants":dw,"converted":ok}
            if error: own=ext=rel=None
            else:
                own=float(ra)-float(rb);ext=float(roa)-float(rob);rel=(float(ra)-float(roa))-(float(rb)-float(rob))
            rows.append({"seed":int(seed),"source":source,"seat":seat,"conversions":conv,"pairs":details,"own_delta":own,"opponent_externality":ext,"relative_delta":rel,"error":error})
    summary={"development":summarize([r for r in rows if r["source"]=="development"]),"live_meta":summarize([r for r in rows if r["source"]=="live_meta"]),"all":summarize(rows)}
    out=ROOT/args.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps({"schema_version":"kexp045-causal-value-v1","summary":summary,"rows":rows},indent=2,sort_keys=True),encoding="utf-8");print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=="__main__":main()
