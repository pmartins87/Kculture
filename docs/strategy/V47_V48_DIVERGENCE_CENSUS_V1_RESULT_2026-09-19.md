# V47 × V48 Divergence Census V1 — Result — 2026-09-19

## Binding run

Workflow: **`35439729714`**  
Head: `eef56d2bb65f3a1bcf44a7499c3c35dcc70a32cd`  
Artifact: `10583990066`  
Artifact digest: `sha256:b9c32142647f28402d16223e59ade66a058f01e932520684e1b4d94313cc4f17`.

## Result

Decision: **`V48_CENSUS_MARKET_SEARCHABLE`**.

Fresh seeds `73001..73004`, both seats:
- 8/8 complete contexts;
- V47 wins: **0**;
- ties: **0**;
- losses: **8**;
- score rate: **0.0**;
- mean terminal margin: **-454.0**;
- failures: **0**.

Divergence surface:
- same-physical market divergences: **458**;
- physical farmer/hands divergences: **0**.

First market-only divergence:
- seed 73001: step 253;
- seed 73002: step 323;
- seed 73003: step 253;
- seed 73004: step 253.

Frequent shared divergence steps include:
`447, 529, 549, 573, 577, 669, 670, 671, 677, 685...`.

## Mechanistic pattern

The strongest recurring pattern is **queue sanitation**, not a different physical programme.

Examples:
- V47 `SELL MILK 3` while V48 emits `[]`;
- V47 `SELL WOOL 14` while V48 clears that slot;
- V47 `SELL WHEAT 1000` while V48 emits a feasible quantity such as `SELL WHEAT 5/6`;
- late V47 multi-product `SELL ... 1000` queues become either feasible current quantities
  or empty slots in V48.

Farmer and hands remain exactly identical in every observed divergence.

## Interpretation

This is unusually strong causal guidance:
- the competitive V47→V48 gap on these fresh seeds is entirely on the market/queue surface;
- a physical/macro route search is not justified yet;
- the generic multi-turn V4A remains available, but a simpler first-party hypothesis should be
  tested first.

New first-party hypothesis:
**O-CQ1 — Queue Clamp/Clear**.

Candidate rule:
- preserve exact V47 farmer/hands;
- preserve non-SELL market slots;
- sequentially cap each SELL quantity to currently available own shed inventory;
- if current available quantity is zero, replace that SELL slot with `[]`;
- preserve market slot structure.

The first gate is an action-parity audit against V48, measuring both precision and recall so the
rule cannot pass merely by matching a few hand-picked examples.

No Kaggle submission is authorized by the census.
