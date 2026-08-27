"""Direct candidate-vs-opponent screen on exploratory live-meta environmental seeds.

Development/calibration only. Uses configs/exploratory_live_meta_seeds_20260825.json,
runs both seats, fresh-loads file agents per game, and reports W/L/T + money delta.
Never use this tool with validation or held-out partitions.
"""
from __future__ import annotations

import argparse, json, statistics, sys
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tools.run_episode import resolve_agent


def live_seeds(path):
    x=json.loads(path.read_text(encoding="utf-8")); out=[]
    def walk(v):
        if isinstance(v,dict):
            if isinstance(v.get("seed"),int):out.append(v["seed"])
            for c in v.values():walk(c)
        elif isinstance(v,list):
            for c in v:walk(c)
    walk(x);return list(dict.fromkeys(out))


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--candidate",required=True);ap.add_argument("--opponent",required=True);ap.add_argument("--output",required=True);args=ap.parse_args()
    seeds=live_seeds(ROOT/"configs/exploratory_live_meta_seeds_20260825.json")
    rows=[]
    for seed in seeds:
        for cseat in (0,1):
            c=resolve_agent(args.candidate);o=resolve_agent(args.opponent)
            agents=[c,o] if cseat==0 else [o,c]
            env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=True);env.run(agents);rep=env.toJSON();final=rep["steps"][-1]
            cr=final[cseat].get("reward");orr=final[1-cseat].get("reward");cs=final[cseat].get("status");os=final[1-cseat].get("status")
            if cs!="DONE" or os!="DONE" or not isinstance(cr,(int,float)) or not isinstance(orr,(int,float)): outcome="ERROR";delta=None
            else:
                delta=float(cr)-float(orr);outcome="WIN" if delta>0 else "LOSS" if delta<0 else "TIE"
            rows.append({"seed":int(seed),"candidate_seat":cseat,"candidate_reward":cr,"opponent_reward":orr,"candidate_status":cs,"opponent_status":os,"terminal_delta":delta,"outcome":outcome})
    valid=[r for r in rows if r["outcome"]!="ERROR"];wins=sum(r["outcome"]=="WIN" for r in valid);losses=sum(r["outcome"]=="LOSS" for r in valid);ties=sum(r["outcome"]=="TIE" for r in valid)
    summary={"seeds":len(seeds),"games":len(rows),"wins":wins,"losses":losses,"ties":ties,"errors":len(rows)-len(valid),"score_rate_tie_half":(wins+0.5*ties)/len(valid) if valid else None,"mean_terminal_delta":statistics.mean(r["terminal_delta"] for r in valid) if valid else None,
             "seat0":{"wins":sum(r["outcome"]=="WIN" for r in valid if r["candidate_seat"]==0),"losses":sum(r["outcome"]=="LOSS" for r in valid if r["candidate_seat"]==0),"ties":sum(r["outcome"]=="TIE" for r in valid if r["candidate_seat"]==0)},
             "seat1":{"wins":sum(r["outcome"]=="WIN" for r in valid if r["candidate_seat"]==1),"losses":sum(r["outcome"]=="LOSS" for r in valid if r["candidate_seat"]==1),"ties":sum(r["outcome"]=="TIE" for r in valid if r["candidate_seat"]==1)}}
    payload={"schema_version":"exploratory-live-meta-direct-v1","candidate":args.candidate,"opponent":args.opponent,"summary":summary,"rows":rows}
    out=ROOT/args.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8");print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=="__main__":main()
