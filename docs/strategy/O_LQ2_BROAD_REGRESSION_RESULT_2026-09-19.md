# O-LQ2 Broad Fresh Regression — Result — 2026-09-19

## Binding run

Workflow: **`35456201059`**  
Head: `7a85e31ec5a60c8381cfd808e76d632a33f0e378`  
Aggregate artifact: `10588138237`  
Digest: `sha256:75de909996f62b8498aaff6511cf3f981059dca91e010d4c9eafff372249c97f`.

Mechanical PASS:
- 7/7 opponent shards;
- 56/56 paired contexts;
- zero failures;
- pre-trigger parity PASS.

## Binding decision

**`O_LQ2_BROAD_SAFE_PASS`**

Overall:
- mean score delta: **+0.1607143**;
- mean margin delta: **+212.82**;
- positive-score contexts: **12**;
- negative-score contexts: **0**.

By opponent:
- V48: score **0.125 -> 0.875**, delta **+0.75**, margin delta +720;
- V47 mirror: score **0.500 -> 0.875**, delta **+0.375**, margin delta +721;
- Ready Stock: score unchanged 0.875, margin +8.875;
- router_2715: score unchanged 1.0, margin +9.625;
- conditional_memory: score unchanged 1.0, margin +4;
- tactical_memory: score unchanged 1.0, margin +24.25;
- best_market: score unchanged 1.0, margin +2.

No opponent block regressed in W/L.

## Interpretation

O-LQ2 is not merely a V48 exploit:
- it strongly improves the exact V47 mirror block;
- it preserves W/L against five unrelated families;
- it has no observed negative-score contexts in the broad fresh league.

O-LQ2 is now eligible for:
1. composition with O-RW1 + O-TW1;
2. integrated runtime/package parity;
3. option-library admission if composition remains safe.

No Kaggle submission is authorized yet.
