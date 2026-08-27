"""CR-012 diagnostic: attribute CR-011 terminal effects to adaptive action changes.

Replays CR-011 and frozen R4B on the exact CR-011 exploratory field. For each
(opponent, seed, seat), identify candidate action divergences with the established
Kaggriculture replay alignment (observation state t -> action stored at frame t+1),
then summarize terminal self/relative effect by opponent, product, trigger count,
quantity and state. Diagnostic only: no candidate/gate is tuned here.
"""
from __future__ import annotations

import argparse, collections, importlib.util, json, statistics, sys, time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
SEEDS_PATH=ROOT/'configs/cr011_fresh_exploratory_seeds_v1.json'

def load_agent(path):
    path=Path(path)
    if not path.is_absolute(): path=ROOT/path
    spec=importlib.util.spec_from_file_location(f'cr012_{path.stem}_{time.time_ns()}',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m.agent

def run(candidate_path,opponent_path,seed,seat):
    c=load_agent(candidate_path);o=load_agent(opponent_path)
    agents=[c,o] if seat==0 else [o,c]
    env=make('kaggriculture',configuration={'episodeSteps':720,'seed':int(seed)},debug=True)
    env.run(agents);return env.toJSON()

def final_rewards(rep,seat):
    f=rep['steps'][-1];a=f[seat].get('reward');b=f[1-seat].get('reward')
    return float(a),float(b),float(a)-float(b)

def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def counter(xs):return collections.Counter(canon(x) for x in (xs or []))

def action_at(rep,seat,t):
    if t+1>=len(rep.get('steps') or []):return {}
    x=rep['steps'][t+1][seat].get('action')
    return x if isinstance(x,dict) else {}

def obs_at(rep,seat,t):
    try:return rep['steps'][t][seat].get('observation') or {}
    except Exception:return {}

def added_orders(a,b):
    # Orders in a beyond multiset in b.
    ca,cb=counter(a.get('market')),counter(b.get('market'));out=[]
    for s,n in (ca-cb).items():
        try:o=json.loads(s)
        except Exception:continue
        out.extend([o]*n)
    return out

def summarize(rows,keyfn):
    groups={}
    for r in rows:groups.setdefault(keyfn(r),[]).append(r)
    out={}
    for k,xs in groups.items():
        out[str(k)]={
            'pairs':len(xs),
            'mean_self_gain':statistics.mean(r['self_gain'] for r in xs),
            'mean_relative_gain':statistics.mean(r['relative_gain'] for r in xs),
            'positive_self_fraction':sum(r['self_gain']>0 for r in xs)/len(xs),
            'positive_relative_fraction':sum(r['relative_gain']>0 for r in xs)/len(xs),
            'mean_trigger_count':statistics.mean(r['trigger_count'] for r in xs),
            'mean_added_quantity':statistics.mean(r['total_added_quantity'] for r in xs),
        }
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--opponent',action='append',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
    seeds=json.loads(SEEDS_PATH.read_text())['seeds'];rows=[]
    for opp in args.opponent:
      for seed in seeds:
       for seat in (0,1):
        j=run('candidates/cr011_adaptive_early_order.py',opp,seed,seat)
        b=run('candidates/r4b_ablation_market_only.py',opp,seed,seat)
        jr,jo,jd=final_rewards(j,seat);br,bo,bd=final_rewards(b,seat)
        diffs=[];product_qty=collections.Counter()
        for t in range(min(719,len(j['steps'])-1,len(b['steps'])-1)):
            ja=action_at(j,seat,t);ba=action_at(b,seat,t)
            if ja==ba:continue
            add=added_orders(ja,ba)
            adaptive=[o for o in add if isinstance(o,list) and len(o)>=3 and o[0]=='SELL' and o[1] in ('CARROT','STRAWBERRY')]
            if not adaptive:continue
            obs=obs_at(j,seat,t);market=obs.get('market') or {};prices=market.get('prices') or {};inv=market.get('inventory') or {}
            for o in adaptive:
                try:q=max(0,int(o[2] or 0))
                except Exception:q=0
                product_qty[o[1]]+=q
                diffs.append({'state':t,'item':o[1],'qty':q,'price':prices.get(o[1]),'market_inventory':inv.get(o[1]),'cr011_slot':(ja.get('market') or []).index(o),'base_market_count':len(ba.get('market') or [])})
        products=sorted(product_qty)
        rows.append({'opponent':opp,'seed':seed,'seat':seat,'cr011_reward':jr,'base_reward':br,'self_gain':jr-br,'cr011_delta':jd,'base_delta':bd,'relative_gain':jd-bd,'trigger_count':len(diffs),'products':products,'product_quantities':dict(product_qty),'total_added_quantity':sum(product_qty.values()),'first_trigger':diffs[0] if diffs else None,'triggers':diffs})
    affected=[r for r in rows if r['trigger_count']>0]
    payload={
      'experiment':'CR-012','status':'DIAGNOSTIC_COMPLETE','pairs':len(rows),'affected_pairs':len(affected),
      'overall_affected':{
        'mean_self_gain':statistics.mean(r['self_gain'] for r in affected) if affected else None,
        'mean_relative_gain':statistics.mean(r['relative_gain'] for r in affected) if affected else None,
        'positive_self_fraction':sum(r['self_gain']>0 for r in affected)/len(affected) if affected else None,
        'positive_relative_fraction':sum(r['relative_gain']>0 for r in affected)/len(affected) if affected else None,
      },
      'by_opponent':summarize(affected,lambda r:r['opponent']),
      'by_product_signature':summarize(affected,lambda r:'+'.join(r['products']) if r['products'] else 'none'),
      'by_first_product':summarize([r for r in affected if r['first_trigger']],lambda r:r['first_trigger']['item']),
      'rows':rows,
      'interpretation_rule':'Use this only to choose the next diagnostic axis; do not promote or tune a hosted candidate directly on these already-observed CR-011 field outcomes.'
    }
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True));print(json.dumps({k:v for k,v in payload.items() if k!='rows'},indent=2,sort_keys=True))
if __name__=='__main__':main()
