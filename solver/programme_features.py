"""114 programme-router features built only from the player's observation."""
from collections import Counter
import numpy as np
ITEMS = 'WHEAT CARROT TOMATO STRAWBERRY MELON EGG MILK WOOL FERTILIZER GOOSE COW SHEEP'.split()
SHOPS = 'BAKERY BRUNCH_SPOT FARMERS_MARKET ICE_CREAM_SHOP PET_CAFE PIZZA_SHOP SMOOTHIE_SHOP YARN_STORE'.split()
KINDS = ['EMPTY','LOCKED','WEED','COOP','PASTURE','PLANT']
def features(obs):
    me=int(obs['player']); own=obs['farms'][me]; opp=obs['farms'][1-me]
    out=[obs['step'],obs['day'],obs['hour'],own['money'],opp['money'],
         1+len(own['hands']),1+len(opp['hands']),len(own['unlocked_quadrants']),
         len(opp['unlocked_quadrants']),own['hires_today'],opp['hires_today']]
    for field in ['inventory','prices']:
        out.extend(obs['market'][field][i] for i in ITEMS[:9])
    counts=Counter(obs['town']['unlocked_shops']);out.extend(counts[s] for s in SHOPS)
    for farm in [own,opp]:
        kinds=Counter();what=Counter();s=[0]*6
        for row in farm['tiles']:
            for t in row:
                kind='EMPTY' if t is None else t if isinstance(t,str) else t['kind']
                kinds[kind]+=1
                if not isinstance(t,dict):continue
                if kind=='PLANT':
                    what[t['crop']]+=1
                    s[0]+=t['yield_units'];s[1]+=t['consecutive_unwatered'];s[2]+=t['watered_today']
                elif kind in ['COOP','PASTURE'] and t.get('animal'):
                    what[t['animal']]+=1
                    for j,key in [(0,'yield_units'),(1,'consecutive_unfed'),(3,'fed_today'),(4,'cared_today'),(5,'fertilizer_available')]:s[j]+=t[key]
        out.extend(kinds[k] for k in KINDS);out.extend(what[i] for i in ITEMS);out.extend(s)
    private=obs['private']
    out.extend(private['shed'].get(i,0) for i in ITEMS)
    out.extend(private['seeds'].get(i,0) for i in ITEMS[:5])
    out.extend(sum(inv.get(i,0) for inv in private['inventories']) for i in ITEMS)
    assert len(out)==114
    return np.asarray(out,dtype=np.float32)
