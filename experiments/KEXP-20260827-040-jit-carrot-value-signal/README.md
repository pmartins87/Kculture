# KEXP-20260827-040 — one-step-ahead JIT CARROT value signal

Status: **COMPLETE / PASS / JIT CANDIDATE AUTHORIZED**

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

## Canonical result

GitHub Actions run **33043747146 — SUCCESS**.  
Artifact **9634912985**, ZIP digest **SHA-256 `b910f42108c1466879231bae053d4bfe9d2c65878b2e3811a38b8ef8713970aa`**.

Development pool:

- 16 episodes / 272 mapped safe WHEAT events;
- 6/16 episodes contain a positive one-step-ahead JIT signal;
- 92 positive events;
- later-harvest oracle sign precision: **92/92 = 100%**;
- plant-state sign precision: **91/92 = 98.91%**;
- mean later oracle margin: **+30.42**;
- median later oracle margin: **+20.0**.

Exploratory live-meta environmental pool:

- 20 episodes / 344 mapped events;
- 8/20 episodes contain a positive signal;
- 140 positive events;
- later-harvest oracle sign precision: **140/140 = 100%**;
- plant-state sign precision: **140/140 = 100%**;
- mean later oracle margin: **+67.25**;
- median later oracle margin: **+24.5**.

Combined: 232 sign-positive events, **232/232 later-oracle positive**.

Route yields are structurally simple in the audited windows: 334 mapped events yield 3 and 282 yield 2.

## Decision

**PASS.** The predeclared gate is exceeded by a wide margin in both environmental pools.

This authorizes a tightly bounded development candidate. KEXP-041 implements the lowest-risk first intervention: only the 614→615 block, exactly one extra CARROT purchase and at most one WHEAT→CARROT plant conversion, with an observed seed-ledger guard so a failed added purchase cannot consume R4B-reserved CARROT stock.

Passing KEXP-040 does not authorize validation or hosted submission by itself. W/L remains the primary promotion criterion.

No validation or held-out seeds were accessed.

Tool: `tools/audit_jit_carrot_value_signal.py`  
Frozen tool blob: `71c3db1dcb9dfd0264087fe37de3d41e59b8d3d9`
