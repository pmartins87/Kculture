# ALL3 V20B State-Gated Consensus Fresh Validation Protocol — 2026-09-21

## Status

DORMANT / PRE-REGISTERED BEFORE V20A RESULT.

Activate only if:
`V20A_STATE_GATE_READY`.

## Candidate

**O-TM2 — State-Gated P2 Consensus Schedule**.

Runtime:
- exact ALL3 through turn 463;
- store legal turn-463 gate features;
- at turn 464 compute exact ALL3 and legal turn-464 gate features;
- apply the exact V20A exported JSON gate transform/model;
- gate ON iff frozen `P(benefit) >= 0.80`;
- gate decision is made once and remains fixed;
- gate OFF -> exact ALL3;
- gate ON -> unchanged frozen V19A O-TM1 schedule during P2;
- exact ALL3 outside P2.

No source/ref/rank/context/seed/seat/outcome/reward/future-state runtime feature.

## Untouched population

Exact same 10 source SHAs.

Seeds:
- 78801
- 78802
- 78803
- 78804

Both seats.

Expected:
- 10 × 4 × 2 = **80 paired BASE vs O-TM2 contexts**.

These seeds were frozen before V20A outcomes and are not used for V20A training/holdout.

## Mechanical gate

PASS requires:
- 80/80 unique pairs;
- zero failures/source drift;
- V20A artifact decision = READY;
- exact binding V19A schedule SHA;
- exact gate tree/feature schema loaded from binding V20A artifact;
- gate decision made exactly once at turn 464;
- no candidate action difference before turn 464;
- farmer/hands never changed by O-TM2;
- no prohibited runtime feature.

## Coverage

Coverage PASS requires:
- gate ON in >=8 contexts;
- gate-ON contexts span >=2 discovery-independent validation seeds;
- gate-ON contexts span >=2 source SHAs;
- changed-market treatment fires in >=8 contexts.

## Fresh strategic PASS

**`V20B_STATE_GATE_FRESH_PASS`** iff:
- mechanical PASS;
- coverage PASS;
- positive-score contexts >=2;
- positive-score contexts span >=2 source SHAs;
- negative-score contexts =0;
- BASE-win -> treatment-nonwin regressions =0;
- mean score delta across all 80 contexts >0;
- mean margin delta across all 80 contexts >=0.

Otherwise:
- `V20B_STATE_GATE_FRESH_FAIL_CLOSE`;
- `V20B_STATE_GATE_UNDERPOWERED`;
- `V20B_MECHANICS_INVALID`.

No Kaggle submission is authorized by V20B alone.
