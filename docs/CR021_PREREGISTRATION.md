# CR-021 — sparse TOMATO demand response preregistration

Frozen before candidate implementation outcomes.

## Motivation

CR-016 found a recurrent public supply gap under engine 1.32.7: high-price demanded TOMATO states occurred 644 times in the diagnostic panel and self TOMATO producer count was zero in all 644. Public Apache-2.0 agents independently use unlocked town shops as forward demand signals and apply sparse crop diversion only under material value gaps. This experiment tests the smallest compatible intervention over Kculture's strong hosted adaptive-sale baseline.

## Candidate family

**CR021A: one-slot TOMATO diversion over CR008.**

Frozen physical slot: R4B recurring safe slot `state 310 @ position (9,7)`, originally a `PLANT WHEAT` opportunity and previously audited as long-lived enough for TOMATO maturity.

The candidate delegates to CR008 everywhere except the following identity-free public-state rule.

### Trigger at state 309

Append exactly one `BUY_SEED TOMATO 1` only if all are true:

1. the public town contains `PIZZA_SHOP` or `FARMERS_MARKET`;
2. current TOMATO market price is at least **90** (1.50x official base price 60);
3. the player's public farm has **zero existing TOMATO plants**;
4. the base action has a free market-order slot (<10);
5. the extra-seed ledger can be tracked without consuming seed stock reserved by CR008/R4B;
6. tile `(9,7)` is currently empty and the state-309 CR008 unit action leaves or moves at least one own unit onto `(9,7)`, making the next-state planting opportunity physically visible before the purchase.

Condition 6 was added before candidate implementation/outcomes to prevent orphan seed purchases on route variants where the audited slot is not actually approached.

The 90 threshold is deliberately conservative and mechanics-derived, not fit on CR-016 outcomes: at price 90, four TOMATO units gross 360 against a 50 seed cost, while the official base price is 60. The town-demand requirement prevents pure transient-price chasing.

### Plant at state 310

Only if the extra TOMATO seed is actually observed above the conservative frozen-base expectation, replace **one** base `PLANT WHEAT` intent by `PLANT TOMATO`, and only for a unit actually standing at `(9,7)`. If the exact base opportunity is absent, do nothing.

### Harvest preservation

If this specific diverted tile later contains TOMATO with `yield_units >= 4` and CR008/R4B asks a unit standing on `(9,7)` to `WATER`, replace that one `WATER` by `HARVEST` once. This waits for the full official lifetime production cap before harvesting and prevents a late base harvest from losing accumulated output to decay. Otherwise all unit and market actions remain CR008.

## Prohibited adaptation

- no opponent identity;
- no seed/episode identity;
- no future information;
- no threshold tuning after Stage A;
- no EGG branch in CR021A;
- no changes to the CR008 adaptive-sale model or thresholds;
- no held-out access.

## Fresh data split

`configs/cr021_demand_response_preregistered_seeds_v1.json`

- Stage A: 12 fresh seeds;
- Stage B: 12 different fresh seeds;
- exact nine current-meta opponent packages from `configs/cr015_current_meta_opponents_v1.json`;
- both seats;
- Stage B only for the byte-identical candidate if Stage A supports it.

## Baselines and gates

Primary baseline: **CR008** (canonical hosted adaptive baseline after the 2026-08-29 calibration).
Secondary safety baseline: **CR015**.

Stage A support requires:

- zero mechanical errors;
- no net unfavorable W/L change vs CR008;
- no net unfavorable W/L change vs CR015;
- at least one actual CR021 trigger somewhere in the 216-pair panel;
- positive mean relative delta vs CR008 on triggered pairs;
- broad mean relative delta vs CR008 not negative by more than 25 coins/game;
- candidate unchanged before Stage B.

Promotion relevance is W/L first, relative money second. A candidate that merely earns more money but introduces unfavorable W/L flips is rejected.

**Held-out remains 32/32 sealed.**
