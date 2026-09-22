from pathlib import Path
import json
block='''## Binding update — 2026-09-22 — V28D COMPLETE / ACTIVE PAIR PRESERVED

**This block supersedes lower current-action sections.**

Binding workflow `35781539795` completed SUCCESS. Decision: **`V28D_NO_CURRENT_META_V47_UNDERPERFORMANCE_SIGNAL`**.

Current-window evidence: exact V47 `56466970` had 89 games, score rate `0.5280898876`, mean margin `+6198.47`; ALL3 `56367770` aligned to the exact V47 Episode-ID window had 23 games, score rate `0.3913043478`, mean margin `-1362.61`. V47 minus aligned ALL3: score rate `+0.1367855398`, mean margin `+7561.08`. Common-opponent overlap was only one opponent, too sparse for broad matchup inference; on it both were 1-0 and V47 margin was +423.

Result: `docs/strategy/V28D_CURRENT_HOSTED_PAIR_FORENSICS_RESULT_2026-09-22.md`.

Per frozen routing, preserve latest-two exactly: ALL3 `56367770` primary + exact V47 `56466970` hedge. O-RW1 `56336027` remains outside latest two. Do not open the CR053/stale-rating candidate branch because its prerequisite (robust current-meta V47 underperformance) did not occur.

Continue read-only maturity/status monitoring. Notify on latest-two drift, V47 error/disappearance, or V47 maturity >=100 / >=169 episodes. No Kaggle submission, deletion, or reordering is authorized.

'''
for name in ('STATUS.md','ROADMAP.md','HANDOFF.md'):
    p=Path(name); s=p.read_text(); i=s.find('\n')+1; p.write_text(s[:i]+'\n'+block+s[i:])
p=Path('data/programme_teacher/2026-09-18/OPTION_LIBRARY_V0.json')
d=json.loads(p.read_text())
d['v28d_current_hosted_pair_forensics']={'workflow':35781539795,'status':'COMPLETE','mechanical_pass':True,'decision':'V28D_NO_CURRENT_META_V47_UNDERPERFORMANCE_SIGNAL','v47_submission_id':56466970,'all3_submission_id':56367770,'v47_games':89,'v47_score_rate':0.5280898876404494,'v47_mean_margin':6198.471910112359,'all3_aligned_games':23,'all3_aligned_score_rate':0.391304347826087,'all3_aligned_mean_margin':-1362.608695652174,'common_opponent_count':1,'active_pair_preserved':['ALL3 56367770','exact V47 56466970'],'result_document':'docs/strategy/V28D_CURRENT_HOSTED_PAIR_FORENSICS_RESULT_2026-09-22.md','automatic_kaggle_submission':False}
d['next_stage']='Preserve ALL3 56367770 + exact V47 56466970; continue read-only maturity/status monitoring to V47 >=100 then >=169 episodes or any latest-two/mechanical drift; no Kaggle mutation without explicit authorization.'
p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
