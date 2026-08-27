# KEXP-20260827-038 — purchase-time late crop value signal

Status: **COMPLETE / PASS / BOUNDED PURCHASE REALLOCATION AUTHORIZED**

## Why this follows KEXP-034

KEXP-034 rejected its deliberately conservative `+20` generic crop proxy, but discovered a stronger mechanics fact: in the audited safe late route slots, WHEAT and same-route CARROT have equal unit yield — 3 vs 3 in the earlier safe block and 2 vs 2 in the later block.

For an audited route yield `q`, the legal current-state comparative value reduces to:

`q * (CARROT_price - WHEAT_price) - 10`

where 10 is the additional CARROT seed cost.

KEXP-026 proved there is no idle CARROT seed, so a deployable policy must deliberately reallocate WHEAT seed purchasing. KEXP-038 tests whether this exact value sign is already informative at the preceding R4B WHEAT purchase state.

## Frozen protocol

Unchanged `R4B-market-only-validated-v1` vs deterministic `starter` on all 16 development seeds and all 20 exploratory live-meta environmental seeds. Corrected replay alignment is `state t -> action frame t+1`.

For every R4B WHEAT plant in KEXP-023's mechanically safe windows (614–618, 620–623, 636–647), the audit finds the latest preceding R4B `BUY_SEED WHEAT`, traces the actual later WHEAT HARVEST to get route yield `q`, and evaluates the exact equal-yield margin at purchase, plant and harvest pricing. Harvest-time pricing is diagnostic oracle only.

## Canonical result

Actions run **`33043517944` — SUCCESS**.  
Artifact **`9634809519`**, ZIP digest **SHA-256 `9d18dc5c152f6adbcc1a0830908d0b085320376711ca3e33215219a816dd4e9e`**.

Mapped safe plant events: **616** total.

Development:

- 272 mapped events;
- purchase-time sign positive in **94 events across 6/16 episodes**;
- positive-purchase -> positive plant-time value: **94/94 = 100%**;
- positive-purchase -> positive harvest-price oracle value: **94/94 = 100%**;
- mean later oracle margin: **+39.86**;
- median later oracle margin: **+30**.

Exploratory live-meta:

- 344 mapped events;
- purchase-time sign positive in **140 events across 8/20 episodes**;
- positive-purchase -> positive plant-time value: **140/140 = 100%**;
- positive-purchase -> positive harvest-price oracle value: **140/140 = 100%**;
- mean later oracle margin: **+77.25**;
- median later oracle margin: **+34.5**.

Combined: **234/234** sign-positive purchase events remained positive both at plant time and under the later harvest-price oracle.

The predeclared gate required support in >=4 development and >=5 live-meta episodes, >=10 events in each pool, >=70% oracle-positive precision and positive mean oracle margin. **Every condition passes.**

## Timing structure

The latest purchase feeding a safe route falls into a clean timing split in this audit:

- purchase states `599, 614, 616, 619, 620, 621` feed routes whose harvested WHEAT yield is **3**;
- purchase states `622, 623` feed routes whose harvested WHEAT yield is **2**.

Across all mapped events, route yields were 334 events at `q=3` and 282 at `q=2`. This makes `q` deployable from route timing rather than future observation.

## Decision

**PASS. Authorize one bounded development candidate.**

The candidate may:

1. inspect legal current WHEAT/CARROT market prices when R4B issues a mapped late WHEAT seed purchase;
2. use the mechanics-derived route yield `q` for that purchase timing;
3. when `q * (CARROT_price - WHEAT_price) - 10 > 0`, reallocate at most two WHEAT seed units into CARROT;
4. spend only those explicitly added CARROT credits by converting mechanically safe downstream R4B WHEAT plant intents;
5. preserve all other R4B behavior and re-check current value at the plant state when practical.

This PASS authorizes development W/L testing only. Validation, held-out seeds and hosted submission remain closed.

No threshold was fitted after seeing the data; the sign boundary is the exact equal-yield economic break-even condition.

Tool: `tools/audit_late_seed_purchase_value_signal.py`  
Frozen tool blob: `41419bf62924da4b2dc585641d0569c936243f8f`
