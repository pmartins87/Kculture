"""KEXP-056: audit R4B visits to safe long-lived crop slots after TOMATO maturity.

KEXP-053/055 identified five recurring WHEAT slots that last >=192 turns and do
not later require a same-tile replant. For each occurrence, record same-tile
actions after the 192-turn TOMATO first-yield threshold and before the original
R4B HARVEST. A post-threshold WATER/tile action can become a state-gated TOMATO
HARVEST opportunity without waiting for the very late one-shot WHEAT harvest.

Development + exploratory live-meta only; validation/held-out are untouched.
"""
from __future__ import annotations

import argparse, collections, json, statistics, sys
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tools.run_episode import resolve_agent

AGENT='file:candidates/r4b_ablation_market_only.py:agent'
MATURE_DELAY=192
SAFE_SLOTS={(262,(0,4)),(310,(9,7)),(334,(5,9)),(451,(7,3)),(477,(0,9))}
IGNORE={'NORTH','SOUTH','EAST','WEST','PASS'}


def live_seeds(path):
    obj=json.loads(path.read_text(encoding='utf-8'));out=[]
    def walk(v):
        if isinstance(v,dict):
            if isinstance(v.get('seed'),int):out.append(v['seed'])
            for x in v.values():walk(x)
        elif isinstance(v,list):
            for x in v:walk(x)
    walk(obj);return list(dict.fromkeys(out))

def obs(rep,t):return rep['steps'][t][0].get('observation') or {}
def act(rep,t):return (rep['steps'][t+1][0].get('action') or {}) if t+1<len(rep['steps']) else {}
def positions(o):
    fs=o.get('farms') or [];f=fs[0] if fs else {}
    return [tuple(f.get('farmer') or (-1,-1))]+[tuple(x) for x in (f.get('hands') or [])]
def ops(a):return [a.get('farmer')]+list(a.get('hands') or [])

def events(rep):
    out=[]
    for t in range(len(rep.get('steps') or [])-1):
        ps=positions(obs(rep,t)); aa=ops(act(rep,t))
        for i,op in enumerate(aa):
            if i>=len(ps) or not(isinstance(op,list) and op):continue
            name=str(op[0])
            if name in IGNORE:continue
            out.append({'state':t,'pos':ps[i],'op':name,'arg':str(op[1]) if len(op)>1 else None,'unit':i})
    return out

def analyze(rep,seed,source):
    ev=events(rep);by=collections.defaultdict(list)
    for e in ev:by[e['pos']].append(e)
    rows=[]
    for e in ev:
        key=(e['state'],e['pos'])
        if key not in SAFE_SLOTS or e['op']!='PLANT' or e['arg']!='WHEAT':continue
        same=by[e['pos']]
        h=next((x for x in same if x['state']>e['state'] and x['op']=='HARVEST'),None)
        if not h or h['state']-e['state']<MATURE_DELAY:continue
        mature=e['state']+MATURE_DELAY
        window=[x for x in same if mature<=x['state']<h['state']]
        waters=[x for x in window if x['op']=='WATER']
        tile_actions=[x for x in window if x['op'] not in IGNORE]
        first=tile_actions[0] if tile_actions else None
        first_water=waters[0] if waters else None
        rows.append({
            'seed':int(seed),'source':source,'plant_state':e['state'],'pos':list(e['pos']),
            'maturity_state':mature,'base_harvest_state':h['state'],'base_delay':h['state']-e['state'],
            'postmaturity_tile_actions':[{'state':x['state'],'op':x['op'],'arg':x['arg']} for x in tile_actions],
            'postmaturity_water_states':[x['state'] for x in waters],
            'first_postmaturity_action_state':first['state'] if first else None,
            'first_postmaturity_action':first['op'] if first else None,
            'first_postmaturity_water_state':first_water['state'] if first_water else None,
            'lead_from_first_water_to_base_harvest':(h['state']-first_water['state']) if first_water else None,
            'has_early_harvest_opportunity':bool(first_water and h['state']-first_water['state']>=24),
        })
    return rows

def summarize(rr):
    leads=[r['lead_from_first_water_to_base_harvest'] for r in rr if isinstance(r['lead_from_first_water_to_base_harvest'],int)]
    byslot={}
    for state,pos in sorted(SAFE_SLOTS):
        x=[r for r in rr if r['plant_state']==state and tuple(r['pos'])==pos]
        byslot[f'{state}@{pos[0]},{pos[1]}']={
            'n':len(x),'with_postmaturity_water':sum(r['first_postmaturity_water_state'] is not None for r in x),
            'early_opportunity':sum(r['has_early_harvest_opportunity'] for r in x),
            'first_water_states':sorted({r['first_postmaturity_water_state'] for r in x if r['first_postmaturity_water_state'] is not None}),
            'base_harvest_states':sorted({r['base_harvest_state'] for r in x}),
        }
    return {'slots':len(rr),'episodes':len({r['seed'] for r in rr}),'with_postmaturity_water':sum(r['first_postmaturity_water_state'] is not None for r in rr),'early_harvest_opportunity':sum(r['has_early_harvest_opportunity'] for r in rr),'mean_lead_to_base_harvest':statistics.mean(leads) if leads else None,'by_slot':byslot}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args()
    dev=json.loads((ROOT/'configs/seed_partitions.json').read_text(encoding='utf-8'))['development'];live=live_seeds(ROOT/'configs/exploratory_live_meta_seeds_20260825.json')
    rows=[]
    for seed,source in [(s,'development') for s in dev]+[(s,'live_meta') for s in live]:
        a=resolve_agent(AGENT);env=make('kaggriculture',configuration={'episodeSteps':720,'seed':int(seed)},debug=True);env.run([a,'starter']);rows+=analyze(env.toJSON(),seed,source)
    summary={'development':summarize([r for r in rows if r['source']=='development']),'live_meta':summarize([r for r in rows if r['source']=='live_meta']),'all':summarize(rows)}
    # Require the same structural slot family to show an early post-maturity
    # WATER opportunity in both open distributions before a candidate is built.
    eligible=[]
    for key in summary['all']['by_slot']:
        d=summary['development']['by_slot'][key];l=summary['live_meta']['by_slot'][key]
        if d['early_opportunity']>0 and l['early_opportunity']>0:eligible.append(key)
    gate={'cross_distribution_early_harvest_slots':eligible,'candidate_authorized':bool(eligible)}
    payload={'schema_version':'tomato-postyield-visits-v1','maturity_delay':MATURE_DELAY,'safe_slots':[{'state':s,'pos':list(p)} for s,p in sorted(SAFE_SLOTS)],'summary':summary,'gate':gate,'rows':rows}
    out=ROOT/args.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding='utf-8');print(json.dumps({'summary':summary,'gate':gate},indent=2,sort_keys=True))
if __name__=='__main__':main()
