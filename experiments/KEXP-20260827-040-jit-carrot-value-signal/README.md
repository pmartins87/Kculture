# KEXP-20260827-040 — one-step-ahead JIT CARROT value signal

Status: **RUNNING / DIAGNOSTIC ONLY**

## Why this branch exists

KEXP-034 established equal same-route WHEAT/CARROT yields in the audited safe late route slots. KEXP-038 asks whether an earlier existing WHEAT purchase can be partially reallocated. KEXP-040 tests a simpler fallback that does not depend on reversing old purchases: buy one new CARROT seed exactly one state before a safe WHEAT plant and treat the already-owned WHEAT seed as sunk cost.

For equal route yield `q`, the incremental comparison is therefore:

`q * (CARROT_price - WHEAT_price) - 20`

where 20 is the full new CARROT seed cost.

## Frozen protocol

Run unchanged `R4B-market-only-validated-v1` vs deterministic `starter` on all 16 development seeds and all 20 exploratory live-meta environmental seeds.

For each R4B WHEAT plant in the safe windows 614–618, 620–623 and 636–647:

1. trace the actual later same-tile WHEAT HARVEST and route yield `q`;
2. evaluate the exact JIT margin at state `t-1`;
3. evaluate it again at the plant state `t`;
4. use later harvest-time prices only as a forbidden oracle diagnostic.

No top-player labels or identity features are used.

## Predeclared gate

The rule is fixed and contains no fitted threshold:

`at t-1: q * (CARROT_price - WHEAT_price) - 20 > 0`.

A JIT development candidate is eligible only if:

- development: >=4 episodes and >=10 sign-positive events;
- exploratory live-meta: >=5 episodes and >=10 sign-positive events;
- >=70% of sign-positive t-1 events remain positive under the later harvest-price oracle in each pool;
- mean oracle margin among those events is positive in each pool.

Passing authorizes only a tightly capped candidate: buy at most one CARROT on `t-1` and convert the corresponding safe WHEAT PLANT on `t`, initially capped at two conversions per episode. It does not authorize validation or hosted submission.

If the gate fails, one-step current price is insufficient and this branch closes in favor of the richer purchase-time/forecast controller.

No validation or held-out seeds are accessed.

Tool: `tools/audit_jit_carrot_value_signal.py`  
Frozen tool blob: `71c3db1dcb9dfd0264087fe37de3d41e59b8d3d9`
