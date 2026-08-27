# KEXP-20260827-034 — mechanics-first late crop value margin

Status: **RUNNING / DIAGNOSTIC ONLY**

## Why this follows KEXP-029/031

KEXP-029 and KEXP-031 showed that action imitation is not temporally stable enough to justify a deployable CARROT rule. The crop branch therefore moves from **predicting what a top agent buys** to **estimating whether a WHEAT slot has positive counterfactual economic value if converted to CARROT**.

This experiment uses no top-player action labels.

## Frozen protocol

Run unchanged `R4B-market-only-validated-v1` against deterministic `starter` on:

- all 16 development seeds;
- all 20 exploratory live-meta environmental seeds.

Use the corrected replay convention: observation/state frame `t` is paired with submitted action frame `t+1`.

Only R4B WHEAT plants in KEXP-023's mechanically clean windows are audited:

- 614–618;
- 620–623;
- 636–647.

For each such WHEAT plant, replay the **same same-tile physical schedule** on a counterfactual CARROT tile:

- identical WATER timing;
- identical FERTILIZE timing;
- identical HARVEST timing;
- exact official carrot watering bonus window, fertilizer duration, cap, and two-missed-days death rule.

The observed R4B WHEAT `yield_units` immediately before its actual HARVEST are retained as the baseline route yield.

## Value measurements

Three distinct quantities are kept separate.

1. **Deployable simple current-price proxy**

   `3 * CARROT_price_now - 20 - (4 * WHEAT_price_now - 10)`

   This assumes ordinary unfertilized maxima and uses only current legal public prices.

2. **Same-route current-price diagnostic**

   Uses the exact simulated carrot yield and observed R4B wheat yield, but still prices both at the plant-time market.

3. **Future-price oracle diagnostic**

   Uses those same route yields but prices both at R4B's later harvest state. This is forbidden as a deployable feature; it exists only to test whether current-price triggers preserve the sign of later comparative economics.

Seed cost difference is included in every comparison.

The audit also measures R4B WHEAT seed purchases during 600–635, because KEXP-026 proved that there is no idle CARROT stock: any future candidate must fund CARROT by deliberately reallocating existing WHEAT seed purchases.

## Frozen trigger and predeclared gate

No threshold search is allowed. The fixed candidate trigger being tested is:

`simple current-price margin >= +20 coins`.

A bounded seed-reallocation candidate becomes eligible only if all are true:

- development: trigger occurs in >=4/16 episodes and >=8 events;
- exploratory live-meta: trigger occurs in >=5/20 episodes and >=10 events;
- in **each pool**, >=70% of triggered events have positive future-price oracle margin;
- mean future-price oracle margin among triggered events is positive in each pool;
- median R4B WHEAT seed purchases during 600–635 are >=4 in each pool.

Passing authorizes only a tightly capped development candidate, initially at most two one-for-one WHEAT-seed→CARROT-seed reallocations per episode followed by safe-window plant conversion. It does not authorize validation or hosted submission.

If the gate fails, stop fixed margin tuning and move the crop branch to a bounded rollout/value controller.

No validation or held-out seeds are accessed. Opponent/team/episode/seed identity is forbidden as a deployable feature.

Tool: `tools/audit_late_crop_value_margin.py`  
Frozen tool blob: `bdb99ef47251f9d3a8d46bb923d4eea0f13c38d1`
