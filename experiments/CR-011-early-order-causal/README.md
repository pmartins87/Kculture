# CR-011 — Early-order adaptive SELL causal test

Status: **FROZEN / RUNNING**

CR-010 proved strong conditional game-value headroom from moving the same high-confidence CARROT/STRAWBERRY sale ahead of the other player's same-turn order. CR-011 tests that mechanism causally in complete games.

## Frozen candidate

`candidates/cr011_adaptive_early_order.py`

The candidate keeps CR-008's:

- frozen R4B physical/base policy;
- CR-007 pure prediction model;
- CARROT threshold 0.90;
- STRAWBERRY threshold 0.85;
- eligible products;
- full current shed quantity;
- skip when the base already sells the same product;
- free-slot capacity constraint.

The only intended action-level change is sequence placement. The exact adaptive orders that CR-008 appends after base market orders are instead prefixed before the base list, preserving the adaptive CARROT->STRAWBERRY relative order. No base market order may be removed.

A mandatory mechanical audit feeds CR-008 and CR-011 identical observation streams and requires identical non-market actions and identical market-order multisets, with at least one sequence difference.

## Fresh exploratory field

12 seeds are frozen in `configs/cr011_fresh_exploratory_seeds_v1.json`, generated independently from master seed `2026082711` and excluding development, validation, held-out and all CR-008 fresh exploratory seeds.

CR-011, CR-008 and R4B each play the same four contemporaneous public reference packages, all 12 seeds, both seats: **96 games per policy / 288 paired field games total**.

No validation or held-out outcome is accessed.

## Frozen causal gate

`EARLY_ORDER_CAUSAL_PASS` requires:

- complete paired coverage across all three policies;
- zero environment/action errors;
- versus R4B: positive mean own terminal-money gain;
- versus R4B: positive mean relative-money-delta gain;
- versus R4B: positive own-money effect in at least 2/4 opponent families;
- versus R4B: overall score-rate regression no worse than -0.02;
- versus R4B: no family score-rate regression worse than -0.08;
- versus CR-008: positive mean own terminal-money gain;
- versus CR-008: positive mean relative-money-delta gain;
- versus CR-008: positive own-money effect in at least 2/4 opponent families;
- versus CR-008: overall score-rate regression no worse than -0.02.

A PASS proves only that earlier placement repairs enough of CR-008's causal value loss on this fresh current-meta exploratory field. It still does not authorize held-out access or hosted submission by itself; broader/current-meta replication and package parity would follow.
