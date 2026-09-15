# HANDOFF — Kculture

> **Current update — 2026-09-15:** CR090 is closed after causal failure. CR091 is the current binding gate. Its first run `34987640694` is **invalid for strategic inference** because CR052 was executed through a non-package-faithful harness. The corrected hosted-faithful rerun is **`34990757344`** on commit `f49bff2e7adde626b01b9fa3c0413f7fc97d9649`.

## Mission

Win / maximize prize probability in Kaggriculture. Novelty is irrelevant unless it improves competitive strength. All accumulated legal knowledge remains usable.

## Authoritative branches

- competition/source of truth: `fix/kaggle-parity-v1`
- experimental integration: `research/first-principles-economy-v1`

Read first:

1. `STATUS.md`
2. `ROADMAP.md`
3. `docs/strategy/CR090_H9_PUBLIC_SHOP_ADAPTIVE_RESULT_2026-09-15.md`
4. `docs/strategy/CR091_HIERARCHICAL_MARKET_OPTION_PROTOCOL_2026-09-15.md`
5. `docs/strategy/CR091_RUN1_INVALID_2026-09-15.md`
6. experimental `docs/strategy/FP001_STATUS.md` / `FP001_ROADMAP.md`

## Competitive anchors

- **CR053_REAL**: strongest exact project-hosted anchor; submission `56073870`, checkpoint ~`2064.8`, SHA `095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15`.
- CR052_REAL ~`1749.2`, SHA `b650a31d091323f2510aede0265937d3193a82a99109eadc8ab39c6e85db278d`.
- CR083 ~`1619.9`, SHA `648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`.
- CR086 ~`1612.6`, SHA `11296a4e658f37c109a2cc953be0ea7db8e2fbde6286ac483e0466f52f4af888`.
- frozen external frontier 2026-09-14: top ~3191; rank 10 ~2958; target remains ~3000+.

Critical calibration: exact-byte local H2H reverses hosted order. Use local tests for mechanics, causal interventions, catastrophe and diversity, not as a direct hosted-rating predictor.

## Closed major routes

Keep closed absent new evidence changing the failure mechanism: CR078/079; CR080 replay stitching; CR081 static market-prefix transplant; CR082 1-NN imitation; CR084 FEED rescue; CR085 Pareto gating; direct CR088 tapes; static C5/C5+M6S1; fixed C3S2/C2S3; CR090 simple first-shop species selector.

## Retained modules / knowledge

CR053 macro/physical route; CR086 latent-supply estimator + SELL priority; CR087/088 elite macro/replay corpus; H1 WHEAT carry; H1B sale deferral; H8/B3+DAILY CARE; H9 public-shop demand representation; H10 compact routing/batching; H11 fertilizer conversion; M6S1 as economic module.

## CR089 final

Run `34923802262`: C5_BASE and C5_M6S1 each 0W–132L. M6S1 improved monetary margins but zero W/L coverage. Static C5 backbone closed; M6S1 retained only as a module.

## CR090 final

Run `34979280512`: mechanics exact. YARN SHEEP-minus-COW mean `-174.46`, median `-451`, 7W/17L. MILK COW-minus-SHEEP mean `+2119.39`, 28/28 positive. Overall adaptive-minus-delayed-COW mean `-32.71`.

Binding verdict: `CR090_H9_CAUSAL_FAIL_CLOSE_SIMPLE_SPECIES_ADAPTATION`. Lesson: correct demand representation is not automatically an action-value rule.

## Current binding experiment — CR091

Protocol: `docs/strategy/CR091_HIERARCHICAL_MARKET_OPTION_PROTOCOL_2026-09-15.md`.

Treatments:

1. exact `CR053_BASE`;
2. `CR053_LATENT_PRIORITY`: exact CR053 farmer/hands and exact market-order multiset, with only order sequence changed by CR086 latent-supply cash-risk priority.

Frozen panel: CR052_REAL, CR053_REAL, CR083, CR086; seeds `91301..91308`; both seats; 128 total episodes. W/L edge-score delta is primary; terminal money diagnostic only.

### Run 1 `34987640694` — INVALID

The first harness executed package `main.py` via direct Python `exec()`. CR052 requires the hosted package context and all 32 CR052 treatment episodes failed. Therefore the run has **no CR091 PASS/FAIL verdict**.

Non-binding three-edge diagnostic only: +0.1875 W/L score delta vs CR053, zero score delta vs CR083/CR086, with exact physical/order-multiset parity on executable calls.

Do not promote this partial result.

### Corrected rerun — ACTIVE / AUTHORITATIVE

- research commit: `f49bff2e7adde626b01b9fa3c0413f7fc97d9649`
- workflow: **`34990757344`**

Only execution semantics changed. Frozen seeds, opponents, treatments, option logic and thresholds are unchanged.

The repaired harness uses the validated hosted-faithful path:

- `kaggle_exact_runtime.AgentProcess`
- fresh spawned process per package per episode
- official `kaggle_environments.agent.Agent`
- shared-state observation reconstruction
- official reference stepping/overage accounting
- no falsy-action PASS substitution
- exact CR053 package produces the candidate base action; market option is applied to that exact action
- failures now retain phase, step and traceback diagnostics

Frozen outcomes after mechanics pass:

- broad positive transfer -> retain O1 and advance router;
- positive + negative edges -> heterogeneous option value and public-state router discovery;
- neither -> close option without threshold tuning, move to H1/H1B timing on exact CR053;
- mechanics failure -> diagnose semantics only, no strategic inference.

## Non-negotiable legality / evaluation

Engine `kaggle-environments==1.32.7`; no identity/rating/EpisodeId/hidden seed/future/direct opponent-private runtime features; `town.unlocked_shops` legal shared state; final holdout sealed; no automatic CR091 hosted submission.

## Immediate next action

Query rerun `34990757344` once. If complete, read the frozen result and follow its declared branch. Do not use run `34987640694` for promotion and do not submit anything manually to Kaggle while the corrected gate is unresolved.
