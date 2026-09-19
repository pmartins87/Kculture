# V4D Temporal Localization — Result — 2026-09-19

## Binding run

Workflow: **`35449982864`**  
Head: `cc1e9b306af6482464594515f59df5c6928f1d8b`  
Aggregate artifact: `10585478991`  
Aggregate digest: `sha256:447c7ee3440819eec438fe8a9fbabac4e3572d713266db633047c5ef5fb28025`.

The earlier run `35449731037` is non-binding because seed 74102 failed during public-package
download with `ChunkedEncodingError` before any episode. The robust rerun changed only acquisition
retry logic; windows, seeds and decision rules were unchanged.

Mechanical PASS:
- 6/6 seed shards PASS;
- 12/12 contexts complete;
- aggregate PASS;
- zero physical fallback turns.

## Binding decision

**`V48_V4D_GLOBAL_INTERVAL_FOUND`**

Global smallest predeclared interval reproducing the V4B loss->tie gain in all 12 contexts:

**W2+ = steps 336–718**.

W2+:
- reproduced contexts: **12/12**;
- score rate: **0.5**;
- mean score delta: **+0.5**;
- mean margin delta: **+585.67**;
- mean V48-market substitutions: **49.0 turns**;
- physical fallback turns: **0**.

Comparison:
- W1+ (216–718): also 12/12, but strictly larger;
- W3+ (432–718): only **8/12**;
- W4+ (528–718): only a subset;
- isolated windows do not reproduce the global headroom.

Per-context minimal reproducer labels:
- W2+: **4 contexts**;
- W3+: **6 contexts**;
- W4+: **2 contexts**.

Therefore the effect is cumulative and tail-weighted, but four contexts require intervention beginning
by step 336.

## Transform analysis inside minimal winning suffixes

Across the binding 12 contexts, the dominant slot-level V47->V48 market transformations were:

- `CLEAR_SLOT`: **1,332**;
- `SAME_ORDER_QTY_DOWN`: **262**;
- unchanged slots: 706;
- SELL product replacement / slot movement effects: 88;
- quantity increases: 28.

Most common patterns are overwhelmingly queue sanitation:
- two SELL slots -> both empty;
- preserve one feasible SELL and clear later SELLs;
- `SELL product 1000` -> feasible smaller quantity or empty;
- late multi-product liquidation queues -> only currently feasible subset survives.

Examples repeated across all/most contexts:
- `SELL WHEAT 1000; SELL CARROT 1000` -> `[]; []`;
- same pair -> `SELL WHEAT 6; []`;
- nine-product `SELL ... 1000` liquidation -> all empty, or only a few feasible quantities retained.

## First-party hypothesis opened by V4D

V4D independently reopens a causal test of **late projected SELL sanitation**.

This is **not** promotion of CQ2 on parity grounds. CQ2 remains closed as a model of exact V48
behavior because its precision was too low.

New hypothesis **O-LQ1 — Late Queue Sanitation**:
- exact V47 farmer/hands always preserved;
- before step 336, exact V47 market is untouched;
- from step 336 onward, project own shed through exact current physical actions and earlier market
  inventory effects;
- process V47 SELL slots in order;
- cap each SELL to remaining projected own inventory;
- zero-available SELL becomes `[]`;
- preserve slot order and all non-SELL market orders.

V4D supplies two independent reasons for testing O-LQ1 causally:
1. the W/L headroom is globally localized to step 336 onward;
2. the winning V48 transformations are dominated by SELL clearing/quantity reduction.

O-LQ1 must now be tested on **fresh seeds** for actual score effect. No parity threshold is used as its
promotion criterion.

No Kaggle submission is authorized by V4D.
