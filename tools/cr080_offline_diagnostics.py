"""One-shot chronological action fidelity; descriptive, never a promotion gate."""
import argparse,copy,gzip,json,sys
from collections import Counter
from pathlib import Path
from cr080_build_mengfei_bridge import rt


def labels(a):
    return [a.get('farmer') or ['PASS'],a.get('hands') or [],a.get('market') or []]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--corpus',type=Path,required=True);ap.add_argument('--build',type=Path,required=True);a=ap.parse_args()
    bank=json.loads(gzip.decompress((a.build/'package/routes.json.gz').read_bytes()))
    split=json.loads((a.build/'split.json').read_text())
    rows=[];audits={'clock_fallback':True,'seat_covariance':True,'forbidden_fields_ignored':True}
    for j,ref in enumerate(split['holdout']):
        d=json.loads((a.corpus/'replays'/ref['file']).read_bytes());seat=ref['seat'];policy=rt.RouteBridge(bank)
        counts=Counter()
        for t in range(719):
            obs=d['steps'][t][seat]['observation'];pred=policy.act(obs);truth=d['steps'][t+1][seat]['action'];x,y=labels(pred),labels(truth)
            counts['n']+=1;counts['farmer']+=x[0]==y[0];counts['market']+=x[2]==y[2];counts['whole']+=pred==truth
            n=max(len(x[1]),len(y[1]));counts['hands_n']+=n
            counts['hands']+=sum(i<len(x[1]) and i<len(y[1]) and x[1][i]==y[1][i] for i in range(n))
            if t%24==0:
                original=rt.signature(obs);altered=copy.deepcopy(obs)
                altered['seed']=123;altered['episode_id']=999;altered['rewards']=[1,9];altered['remainingOverageTime']=-99
                altered['farms'][1-seat]={'private':'not legal'}
                audits['forbidden_fields_ignored'] &= original==rt.signature(altered)
                altered=copy.deepcopy(obs);altered['farms'].reverse();altered['player']=1-seat
                audits['seat_covariance'] &= original==rt.signature(altered)
                altered=copy.deepcopy(obs);altered['step']=None
                audits['clock_fallback'] &= rt.clock(altered)==t
        rows.append({'episode_id':ref['episode_id'],'counts':dict(counts),'runtime_stats':policy.stats})
        if (j+1)%8==0:print('holdout',j+1,flush=True)
    total=Counter()
    for row in rows: total.update(row['counts'])
    farmer=total['farmer']/total['n'];hands=total['hands']/total['hands_n'];market=total['market']/total['n']
    report={'role':'descriptive only; exact closed-loop W/L decides','episodes':len(rows),'counts':dict(total),'farmer_exact':farmer,'hands_slot':hands,'market_exact':market,'composite':.4*farmer+.35*hands+.25*market,'audits':audits,'rows':rows}
    (a.build/'offline_diagnostics.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
    if not all(audits.values()):raise SystemExit('legal-field/clock/seat audit failed')

if __name__=='__main__': main()
