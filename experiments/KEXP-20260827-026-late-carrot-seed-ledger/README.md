# KEXP-20260827-026 — exact late CARROT seed ledger

Status: **RUNNING / CORRECTIVE DIAGNOSTIC ONLY**

## Why this replaces the stock-only interpretation of KEXP-025

KEXP-025 correctly found repeated late snapshots with positive CARROT seed stock, but its per-episode `stock_only_swap_capacity` summed those snapshots. That can count the **same physical seed multiple times**. A concrete replay pattern contains one CARROT seed visible across many safe WHEAT-plant steps and later consumed by the frozen base route.

Therefore the KEXP-025 claim that the median episode had nine stock-only substitutions available is **withdrawn**. Its raw seed-stock/seed-buy observations remain useful; its summed stock-only capacity is not a valid deployable capacity estimate.

## Corrected question

Across the same 16 development + 20 exploratory-live-meta environmental seeds, with frozen R4B unchanged vs `starter`:

1. Is the replay observation/action alignment consistent with an exact seed ledger?
2. At a KEXP-023 mechanically safe WHEAT-plant step, is any positive CARROT stock truly **unreserved by all later frozen-base CARROT plant intents**?

The conservative deployable-safe criterion requires:

- step in 614–618, 620–623 or 636–647;
- frozen base submits at least one WHEAT `PLANT` intent there;
- current CARROT stock is positive;
- **zero later CARROT `PLANT` intents** through the end of the episode.

This deliberately refuses to treat later seed purchases as restoring equivalence: consuming a seed early shifts the seed ledger and can invalidate a later base plant.

## Gate

No policy is promoted by this diagnostic.

- First, `alignment_bad_total` must be zero in both pools. If not, repair the ledger model before any crop candidate.
- A no-purchase stock-only candidate is eligible only if at least **50% of episodes in both pools** contain at least one truly-unreserved safe candidate step.
- Otherwise, stock-only substitution is rejected and the next crop candidate must explicitly reallocate a bounded number of WHEAT seed purchases into CARROT purchases before the safe planting window.

No validation or held-out seeds are accessed. No seed/opponent/episode identity may be used by a later policy.

Tool: `tools/inspect_late_carrot_seed_ledger.py`
Frozen tool blob: `cdcc957737e689713c37b52cb60e9602ae88819e`
