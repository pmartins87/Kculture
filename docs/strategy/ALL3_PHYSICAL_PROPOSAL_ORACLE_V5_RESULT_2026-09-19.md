# ALL3 Physical Proposal Oracle V5 — Result — 2026-09-19

## Binding corrected executions

Corrected original-layout run:
- workflow `35470046629`;
- SUCCESS.

Corrected opponent×seed parallel run:
- workflow `35470051852`;
- SUCCESS;
- aggregate artifact ID `10592852959`;
- artifact digest `sha256:09a13fe68980091b3b8fd199c0f21c141cc84d31871021a93096ba88bd096833`.

The initial runs `35469830232` / `35469942461` are NON-BINDING because their shard-local
branch-state minima were stricter/inconsistent with the frozen aggregate-only >=12 rule.

Both corrected aggregates agree exactly.

## Verdict

**`V5_PHYSICAL_MARGIN_ONLY`**

Mechanical:
- PASS;
- failures: 0;
- branch states: 32;
- exact discovery/base replay parity preserved.

Overall:
- base score rate: **0.9375**;
- oracle score rate: **0.9375**;
- score delta: **0.0**;
- nonwin->win flips: **0**;
- loss->win flips: **0**;
- mean oracle margin delta: **+505.65625**;
- median margin delta: **0**;
- positive-margin states: **14/32**.

By opponent:
- router_2715: score delta 0; mean margin +1,317.625;
- Tactical Memory: score delta 0; mean margin +694;
- V47 mirror: score delta 0; mean margin +11;
- V48: score delta 0; mean margin **0**.

The only base non-win in the discovery matchups was:
- opponent: V48;
- seed: `75002`;
- seat: `0`;
- final margin: **-26**.

This one losing trajectory generated two selected branch states (steps 191 and 287). No one-turn
localized physical proposal changed its W/L or margin.

## Oracle transform pattern

Most frequent margin-only oracle transforms include:
- hand:5 `NORTH -> PASS`: 8 states;
- hand:0 `PLANT WHEAT -> PASS`: 4;
- hand:2 `WATER -> PASS`: 3;
- other PASS/movement substitutions.

These are not promotion candidates because none produced competition-relevant W/L headroom.

## Interpretation

One-turn localized physical substitutions can improve terminal money in already-winning games, but
the tested action family has **zero demonstrated ability to repair ALL3 non-wins**.

Therefore:
- do not first-party/casualize the margin-only transforms;
- do not add PASS/movement micro-patches to ALL3;
- close one-turn physical substitution as the next option source.

The next bounded escalation is a 2–3-turn localized physical continuation oracle.

Before running expensive continuation branches, locate fresh ALL3 non-win contexts across the diverse
seven-family V2 league. This avoids spending branch compute on already-won games and avoids
overfitting V48 seed 75002.

No Kaggle submission is authorized by V5.
