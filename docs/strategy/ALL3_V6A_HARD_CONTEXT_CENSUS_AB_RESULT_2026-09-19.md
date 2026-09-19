# ALL3 V6A Hard-Context Census — Combined A+B Result — 2026-09-19

## Binding runs

Batch A:
- workflow `35472777632`;
- seeds `75101..75108`;
- 112 games.

Batch B:
- workflow `35473134791`;
- seeds `75109..75116`;
- 112 games.

Both use:
- exact ALL3;
- exact seven-family V2 panel;
- both seats;
- no intervention.

## Combined verdict

**`V6A_HARD_CONTEXTS_READY`**

Mechanical:
- PASS;
- 224 total exact-engine games;
- zero failures.

Combined:
- **220 wins**;
- **4 losses**;
- **0 ties**.

Hard contexts frozen for V6:

1. V47 mirror — seed `75113`, seat 1, margin **-263**;
2. V48 — seed `75103`, seat 1, margin **-86**;
3. V48 — seed `75110`, seat 0, margin **-484**;
4. V48 — seed `75113`, seat 1, margin **-794**.

No close win was substituted for a hard context.

## Population interpretation

Across 32 games per opponent family:

- Best Market: 32-0;
- Conditional Memory: 32-0;
- Ready Stock: 32-0;
- router_2715: 32-0;
- Tactical Memory: 32-0;
- V47 mirror: **31-1**;
- V48: **29-3**.

Thus the local residual W/L problem is concentrated in the two Modern41-adjacent families,
especially V48 queue behavior.

This concentration is discovery evidence only. Opponent identity is not a deployable feature.

## Frozen continuation input

Config:
`configs/all3_v6_hard_contexts.json`.

Commit:
`983091b36c15108b68952ab382b624fab6627c44`.

The config creation automatically launches the pre-frozen V6 bounded 2–3-turn one-locus physical
continuation oracle.

No Kaggle submission is authorized by this census.
