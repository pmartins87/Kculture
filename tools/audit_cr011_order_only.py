"""Mechanical equivalence gate for CR-011 versus frozen CR-008.

Feed both policies the exact same observation stream from frozen R4B replays.
Require every non-market action to be identical and every market-order multiset
to be identical. At least one market sequence must differ, proving CR-011 is
active and that ordering is the only observed action-level change.
"""
from __future__ import annotations

import collections,json,sys
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.run_episode import resolve_agent
from candidates import cr008_adaptive_frontrun as A
from candidates import cr011_adaptive_early_order as B

SEEDS_PATH=ROOT/'configs/cr011_fresh_exploratory_seeds_v1.json'

def canon_order(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'))

def market_counter(a):
    return collections.Counter(canon_order(x) for x in (a.get('market') or []))

def nonmarket(a):
    return {k:v for k,v in a.items() if k!='market'}

def reset():
    for p in (0,1):
        A._HISTORY[p].clear();A._LAST_STEP[p]=-1
        B._HISTORY[p].clear();B._LAST_STEP[p]=-1

def main():
    seeds=json.loads(SEEDS_PATH.read_text(encoding='utf-8'))['seeds']
    mismatches=[];sequence_changes=[];states=0
    for seed in seeds:
        reset();base=resolve_agent('file:candidates/r4b_ablation_market_only.py:agent')
        env=make('kaggriculture',configuration={'episodeSteps':720,'seed':int(seed)},debug=True)
        env.run([base,'starter']);rep=env.toJSON();steps=rep.get('steps') or []
        for t in range(min(719,len(steps))):
            for player in (0,1):
                try:obs=steps[t][player].get('observation') or {}
                except Exception:continue
                aa=A.agent(obs,None);bb=B.agent(obs,None);states+=1
                problems=[]
                if nonmarket(aa)!=nonmarket(bb):problems.append('nonmarket')
                if market_counter(aa)!=market_counter(bb):problems.append('market_multiset')
                if problems:
                    mismatches.append({'seed':seed,'state':t,'player':player,'problems':problems,'cr008':aa,'cr011':bb})
                    if len(mismatches)>=20:break
                if (aa.get('market') or [])!=(bb.get('market') or []):
                    sequence_changes.append({'seed':seed,'state':t,'player':player,'cr008_market':aa.get('market') or [],'cr011_market':bb.get('market') or []})
            if len(mismatches)>=20:break
        if len(mismatches)>=20:break
    payload={'schema_version':'cr011-order-only-v1','states_compared':states,'mismatch_count':len(mismatches),'sequence_change_count':len(sequence_changes),'passed':len(mismatches)==0 and len(sequence_changes)>0,'mismatches':mismatches,'sequence_changes':sequence_changes[:100]}
    out=ROOT/'artifacts/cr011/order-only.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding='utf-8');print(json.dumps({k:v for k,v in payload.items() if k not in ('mismatches','sequence_changes')},indent=2))
    if not payload['passed']:raise SystemExit(2)
if __name__=='__main__':main()
