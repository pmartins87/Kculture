#!/usr/bin/env python3
from pathlib import Path
import json
BLOCK='''## Binding update — 2026-09-23 — V28H COMPLETE / V28I NOT IDENTIFIABLE / V28J BOUNDED HISTORY ACTIVE

**This block supersedes lower current-action sections.**

Hosted pair remains immutable without new user authorization: ALL3 `56367770` primary + exact V47 `56466970` hedge; O-RW1 `56336027` remains outside latest two. No Kaggle submission, deletion, or reordering is authorized. Latest binding hosted checkpoint: V47 127 episodes / 1864.7; ALL3 438 / 1932.0; latest-two `[56466970,56367770]`. Continue read-only monitoring to V47 >=169 and alert on drift/error/disappearance.

### V28H-R2 — COMPLETE
Workflow `35813287407`: mechanics PASS; `V28H_MIDGAME_STRUCTURAL_SEPARATION`; selected checkpoint 480; explanatory window 384–479. Attempt 1 `35812876571` is non-binding mechanical failure only. Result: `docs/strategy/V28H_MATCHED_HARD_EASY_TRACE_RESULT_2026-09-22.md`.

### V28I — COMPLETE
Workflow `35818084144`: mechanics PASS; 144/144 exact V28F terminal replays; 66 positives. Decision **`V28I_LEGAL_STATE_RISK_PHENOTYPE_NOT_IDENTIFIABLE`**. Holdout precision 0.625, recall 1.0, specificity 0.5714286, balanced accuracy 0.7857143. Frozen tree depth 3 / 4 leaves used `opp_money`, `market_inventory:FERTILIZER`, `opp_consecutive_need`. No post-outcome tuning. Result: `docs/strategy/V28I_LEGAL_STATE_RISK_IDENTIFIABILITY_RESULT_2026-09-23.md`.

### V28J — ACTIVE
The frozen V28I fallback is now `docs/strategy/V28J_BOUNDED_LEGAL_HISTORY_RISK_IDENTIFIABILITY_PROTOCOL_2026-09-23.md`: checkpoints 384/416/448/480, exact V28I source split, 798 runtime-legal raw+adjacent-delta columns, same deterministic depth-3 tree and acceptance thresholds. Source identity/rank/SHA remain forbidden runtime features.

**Binding immediate action:** resolve active V28J workflow; repair mechanics only if needed. No Kaggle mutation.

'''
for name in ('STATUS.md','ROADMAP.md','HANDOFF.md'):
 p=Path(name);t=p.read_text();k=t.find('\n');p.write_text(t[:k+1]+'\n'+BLOCK+t[k+1:])
p=Path('data/programme_teacher/2026-09-18/OPTION_LIBRARY_V0.json');d=json.loads(p.read_text())
d['v28h']={'status':'COMPLETE','binding_workflow':35813287407,'attempt1_workflow':35812876571,'attempt1_binding':False,'mechanical_pass':True,'decision':'V28H_MIDGAME_STRUCTURAL_SEPARATION','selected_checkpoint':480,'explanatory_window':[384,479],'result_doc':'docs/strategy/V28H_MATCHED_HARD_EASY_TRACE_RESULT_2026-09-22.md','automatic_kaggle_submission':False}
d['v28i']={'status':'COMPLETE','binding_workflow':35818084144,'mechanical_pass':True,'decision':'V28I_LEGAL_STATE_RISK_PHENOTYPE_NOT_IDENTIFIABLE','contexts':144,'positive_count':66,'selected_checkpoint':480,'holdout_precision':0.625,'holdout_recall':1.0,'holdout_specificity':0.5714285714285714,'holdout_balanced_accuracy':0.7857142857142857,'tree_depth':3,'tree_leaves':4,'used_features':['opp_money','market_inventory:FERTILIZER','opp_consecutive_need'],'result_doc':'docs/strategy/V28I_LEGAL_STATE_RISK_IDENTIFIABILITY_RESULT_2026-09-23.md','automatic_kaggle_submission':False}
d['v28j']={'status':'ACTIVE','protocol':'docs/strategy/V28J_BOUNDED_LEGAL_HISTORY_RISK_IDENTIFIABILITY_PROTOCOL_2026-09-23.md','binding_workflow':35822283032,'checkpoints':[384,416,448,480],'feature_count':798,'source_split':'exact V28I split','model':'deterministic depth-3 tree','automatic_kaggle_submission':False}
d['next_stage']='resolve V28J workflow 35822283032; continue V47 read-only maturity monitoring; never mutate Kaggle slots without explicit authorization'
p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
