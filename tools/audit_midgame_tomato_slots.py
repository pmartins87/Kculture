"""KEXP-053: audit whether frozen R4B has physical slots compatible with TOMATO.

TOMATO needs roughly eight in-game days (192 turns at 24 turns/day) before its
first yield. For each R4B PLANT WHEAT/CARROT action in states 240..527, locate
the next HARVEST action on the same tile and count same-tile WATER actions and
distinct watered days before that harvest. This tests whether the existing
physical tape contains long-lived maintained slots that could accept TOMATO
without a route rewrite.

Development + exploratory environmental seeds only; no validation/held-out.
"""
from __future__ import annotations
import argparse, json, statistics, sys
from pathlib import Path
from kaggle_environments import make
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tools.run_episode import resolve_agent
CAND='file:candidates/r4b_ablation_market_only.py:agent'
START,END=240,527
MIN_TOMATO_DELAY=192


def live_seeds(path):
    obj=json.loads(path.read_text(encoding='utf-8'));out=[]
    def walk(v):
        if isinstance(v,dict):
            if isinstance(v.get('seed'),int):out.append(v['seed'])
            for x in v.values():walk(x)
        elif isinstance(v,list):
            for x in v:walk(x)
    walk(obj);return list(dict.fromkeys(out))


def obs(rep,t): return rep['steps'][t][0].get('observation') or {}
def action(rep,t): return (rep['steps'][t+1][0].get('action') or {}) if t+1<len(rep['steps']) else {}

def units_at(o):
    fs=o.get('farms') or []; f=fs[0] if fs else {}
    return [tuple(f.get('farmer') or (-1,-1))]+[tuple(x) for x in (f.get('hands') or [])]

def unit_ops(a): return [a.get('farmer')]+list(a.get('hands') or [])

def events(rep):
    out=[]
    for t in range(0,len(rep.get('steps') or [])-1):
        o=obs(rep,t); positions=units_at(o); ops=unit_ops(action(rep,t)); day=int(o.get('day',t//24) or 0)
        for i,op in enumerate(ops):
            if not(isinstance(op,list) and op): continue
            if i>=len(positions): continue
            out.append({'state':t,'day':day,'unit':i,'pos':positions[i],'op':str(op[0]),'arg':str(op[1]) if len(op)>1 else None})
    return out

def analyze(rep,seed,source):
    ev=events(rep); rows=[]
    by_pos={}
    for e in ev: by_pos.setdefault(e['pos'],[]).append(e)
    for e in ev:
        if not(START<=e['state']<=END and e['op']=='PLANT' and e['arg'] in {'WHEAT','CARROT'}): continue
        future=[x for x in by_pos.get(e['pos'],[]) if x['state']>e['state']]
        harvest=next((x for x in future if x['op']=='HARVEST'),None)
        if harvest:
            between=[x for x in future if x['state']<harvest['state']]
            waters=[x for x in between if x['op']=='WATER']
            delay=harvest['state']-e['state']
            water_days=len({x['day'] for x in waters})
        else:
            delay=None;waters=[];water_days=0
        rows.append({'seed':int(seed),'source':source,'plant_state':e['state'],'plant_day':e['day'],'crop':e['arg'],'pos':list(e['pos']),'next_harvest_state':harvest['state'] if harvest else None,'delay_to_harvest':delay,'water_actions_before_harvest':len(waters),'distinct_water_days_before_harvest':water_days,'tomato_delay_compatible':bool(delay is not None and delay>=MIN_TOMATO_DELAY)})
    return rows

def summary(rr):
    ds=[r['delay_to_harvest'] for r in rr if isinstance(r['delay_to_harvest'],int)]
    compat=[r for r in rr if r['tomato_delay_compatible']]
    return {'plant_events':len(rr),'with_future_harvest':len(ds),'tomato_delay_compatible':len(compat),'compatible_fraction':len(compat)/len(rr) if rr else None,'delay_mean':statistics.mean(ds) if ds else None,'delay_median':statistics.median(ds) if ds else None,'delay_max':max(ds) if ds else None,'compatible_mean_water_days':statistics.mean(r['distinct_water_days_before_harvest'] for r in compat) if compat else None,'episodes_with_compatible_slot':len({r['seed'] for r in compat})}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args()
    dev=json.loads((ROOT/'configs/seed_partitions.json').read_text(encoding='utf-8'))['development'];live=live_seeds(ROOT/'configs/exploratory_live_meta_seeds_20260825.json')
    rows=[]
    for seed,source in [(s,'development') for s in dev]+[(s,'live_meta') for s in live]:
        a=resolve_agent(CAND);env=make('kaggriculture',configuration={'episodeSteps':720,'seed':int(seed)},debug=True);env.run([a,'starter']);rows+=analyze(env.toJSON(),seed,source)
    sm={'development':summary([r for r in rows if r['source']=='development']),'live_meta':summary([r for r in rows if r['source']=='live_meta']),'all':summary(rows)}
    gate={'natural_tomato_slots_exist':sm['development']['episodes_with_compatible_slot']>=4 and sm['live_meta']['episodes_with_compatible_slot']>=5}
    payload={'schema_version':'midgame-tomato-slot-audit-v1','window':[START,END],'minimum_tomato_delay':MIN_TOMATO_DELAY,'summary':sm,'gate':gate,'rows':rows}
    out=ROOT/args.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding='utf-8');print(json.dumps({'summary':sm,'gate':gate},indent=2,sort_keys=True))
if __name__=='__main__':main()
