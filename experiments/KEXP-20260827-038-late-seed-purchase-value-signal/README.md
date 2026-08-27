# KEXP-20260827-038 — purchase-time late crop value signal

Status: **RUNNING / DIAGNOSTIC ONLY**

## Why this follows KEXP-034

KEXP-034 rejected its deliberately conservative `+20` generic crop proxy, but discovered a stronger mechanics fact: in the audited safe late route slots, WHEAT and same-route CARROT have equal unit yield — 3 vs 3 in the earlier safe block and 2 vs 2 in the later block.

For an audited route yield `q`, the legal current-state comparative value therefore reduces to:

`q * (CARROT_price - WHEAT_price) - 10`

where 10 is the additional CARROT seed cost.

The practical problem is timing. KEXP-026 proved there is no idle CARROT seed; a deployable policy must reallocate an earlier R4B WHEAT seed purchase. KEXP-038 asks whether the exact route-value sign is already informative at that purchase state.

## Frozen protocol

Run unchanged `R4B-market-only-validated-v1` against deterministic `starter` on:

- all 16 development seeds;
- all 20 exploratory live-meta environmental seeds.

Use corrected replay alignment (`state t -> action frame t+1`).

For every R4B WHEAT plant in KEXP-023's mechanically safe windows (614–618, 620–623, 636–647):

1. find the latest preceding R4B `BUY_SEED WHEAT` during steps 580–635;
2. trace the actual same-tile WHEAT HARVEST and record its route yield `q`;
3. compute the exact equal-yield value margin at the preceding purchase state;
4. compute the same margin again at plant time;
5. use harvest-time prices only as a forbidden diagnostic oracle to test whether the purchase-time sign survives to monetization.

No top-agent behavior or identity is used.

## Predeclared rule and gate

There is no threshold search. The tested deployable sign is exactly:

`q * (CARROT_price - WHEAT_price) - 10 > 0`

A bounded purchase-reallocation candidate becomes eligible only if all are true:

- development: sign-positive purchase states appear in >=4 episodes and >=10 mapped safe-plant events;
- exploratory live-meta: sign-positive purchase states appear in >=5 episodes and >=10 events;
- in each pool, >=70% of sign-positive purchase events remain positive under the later harvest-price oracle;
- mean later oracle margin among sign-positive purchase events is positive in each pool.

Passing authorizes a development-only candidate that reallocates at most **two** seeds from an existing R4B WHEAT purchase into CARROT and converts only mechanically safe WHEAT plant slots when the value condition remains favorable. It does not authorize validation or hosted submission.

If the gate fails, purchase-time current prices are too unstable for this simple controller and the crop branch must move to a richer bounded forecast/rollout model.

No validation or held-out seeds are accessed.

Tool: `tools/audit_late_seed_purchase_value_signal.py`  
Frozen tool blob: `41419bf62924da4b2dc585641d0569c936243f8f`
