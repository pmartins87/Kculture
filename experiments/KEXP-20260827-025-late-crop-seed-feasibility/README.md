# KEXP-20260827-025 — late crop seed feasibility

Status: **RUNNING / DIAGNOSTIC ONLY**

## Prize-first question

KEXP-023 showed that a blanket late WHEAT→CARROT swap is mechanically unsafe, but three observed step blocks were clean across both the frozen development pool and exploratory live-meta environmental seeds: **614–618, 620–623, 636–647**.

Before building a crop-response candidate, measure whether those safe WHEAT plant slots can actually be converted using seed stock already available before unit actions. This matters because official execution resolves PLANT before same-turn market BUY_SEED orders.

## Frozen protocol

Run unchanged `R4B-market-only-validated-v1` against deterministic `starter` on:

- all 16 development seeds;
- all 20 exploratory live-meta environmental seeds from the Aug-25 pool.

No policy action is modified.

At the KEXP-023 safe steps, record:

- base WHEAT and CARROT plant counts;
- private WHEAT/CARROT seed stock before the action;
- stock-only WHEAT→CARROT swap capacity after reserving seeds for any base CARROT plants in the same step;
- current public shop multiset and derived WHEAT/CARROT demand weights;
- current WHEAT/CARROT prices;
- current BUY_SEED WHEAT/CARROT quantities.

Also total base BUY_SEED WHEAT/CARROT orders during steps 600–635 to measure whether a bounded one-for-one seed reallocation could fund later safe substitutions.

Diagnostic script: `tools/inspect_late_crop_seed_feasibility.py`.
Frozen script blob: `468d72a14c35a9b379963217e6a9b1e127b389c5`.

## Predeclared interpretation

This experiment does **not** promote a policy.

- A **stock-only** crop candidate is eligible only if, in both development and exploratory pools, the median stock-only capacity is at least **2 substitutions per episode** and at least **50% of episodes** have nonzero capacity.
- If that fails, a bounded **seed-reallocation** candidate remains mechanically eligible only if the median base BUY_SEED WHEAT quantity during steps 600–635 is at least **4 seeds per episode in both pools**. Such a candidate must convert seeds one-for-one, cap the number of substitutions, and still pass W/L gates later.
- If both conditions fail, simple late substitution is deprioritized and a real crop lifecycle controller is required.

No validation or held-out seeds are accessed. Seed/episode/opponent identity is forbidden as a deployable feature.
