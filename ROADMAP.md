# ROADMAP — Kculture live plan

Updated: 2026-09-13

Objective: maximize probability of a prize-winning / top-10 Kaggriculture finish. Source of truth: branch `fix/kaggle-parity-v1`, `STATUS.md`, and frozen protocols.

## Invariants

1. Hosted/live evidence and exact-reference W/L both matter.
2. Submission allowance is a cap, not a quota.
3. Every candidate family gets a predeclared gate.
4. Invalid evaluations are quarantined.
5. No seed, team identity, EpisodeId, future state or opponent-private state as runtime features.
6. Authenticated Kaggle API is the default current-meta source.
7. Original final holdout remains sealed.
8. Do not tune failed architectures on spent validation evidence.
9. Strong CR071M/legacy H2H is necessary but not sufficient.
10. Hosted promotion requires independent high-strength-population evidence.
11. **Do not enter polling loops.**

## Closed architecture classes

- CR078 late mirror breaker.
- CR079 SpaTaro 1-NN.
- CR080 replay/route stitching.
- CR081 time-indexed market transplant.
- CR082 same-step teacher 1-NN.
- CR084 critical late-livestock rescue.
- CR085 public-Pareto gated adaptive switch.

## ACTIVE — CR083 hosted maturation

Frozen SHA: `648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`.
Submission: `56199767`.
Latest already-frozen checkpoint: CR083 `1660.3`, CR071M `1638.8`, CR083 lead `+21.5`, ~76 public episodes.

Do not poll again before the 100-public-episode maturity boundary unless another material decision requires it.

## CLOSED — CR084 / CR085

CR084 promotion failed and its temporal proxy found zero real rescue opportunities. Decision `CLOSE_CR084_CRITICAL_FEED_RESCUE`.

CR085 Gate A `34761593920` on master `9150851`: 3W–3L–26T = `0.5000`, mean `-147.46875`. Decision `CLOSE_CR085_PARETO_GUARDED_SWITCH`.

No retuning of either family.

## CR086 — Stage 1A complete: opponent-stock representation feasibility

**PASS.** A legal opponent private-inventory estimator/bounds representation has generalized on an independent strong-agent cohort.

Frozen confirmation metrics over 100,660 commodity-step observations from 10 preselected top-team replays × both seats:

- MAE `1.25005`;
- p95 `9`;
- interval coverage `0.969462`;
- `stock >= 10` accuracy `0.956338`.

All frozen feasibility thresholds passed.

The estimator covers CARROT/TOMATO/STRAWBERRY/MELON/EGG/MILK/WOOL. Before price floor it uses conservation; once `$1` is observed it represents the loss of identifiability explicitly through point `0` plus a mechanics-derived uncertainty upper bound.

Implementation/evaluation source: `tools/cr086_opponent_inventory_estimator_eval.py`.

This is **representation evidence only**. Do not build an arbitrary stock threshold policy from it.

## CR086 — Stage 1B active: public strong-backbone acquisition

Read-only workflow `34790801576` pulls selected public Kaggriculture notebook sources and freezes hashes/provenance. It contains no submission command.

Targets:

- `indarkarhana/shape-the-shop-work-the-pasture-top-10`;
- `boatlee/v29-r1-adaptive-market-hysteresis`;
- `lynnsakurai/farming-score-v3-replay-revised`;
- `tetsutani/shape-the-shop-work-the-pasture-kaggriculture` if the slug is distinct/available.

The workflow was checked once and was still running. Do not poll again in the same turn.

### Next action when acquisition is available

1. freeze exact pulled files/hashes;
2. inspect notebook metadata/license/attribution;
3. locate executable `main.py`/submission package if publicly provided;
4. classify each architecture: static route, hysteresis, market policy, planning, terminal liquidation, state estimation;
5. run a **benchmark characterization** versus CR083 before modifying public code;
6. exclude any implementation that depends on forbidden/private runtime information.

## CR086 — Stage 2: convert representation into economic value

Only after public-backbone characterization, choose one architecture route:

### Route A — strong public backbone + legal inventory/value layer

Use a public executable backbone only if its license/provenance permits competition use and it materially dominates CR083 locally. Freeze the unmodified backbone first. Then add a separately justified inventory-aware market layer.

### Route B — clean-room architectural reimplementation

If public notebooks expose valuable mechanisms but direct code reuse is undesirable, reimplement the architecture in our own code using public mechanics and the validated opponent-stock representation.

Candidate policy should target an explicit economic quantity, e.g.:

- expected market-price impact of opponent latent supply;
- scarcity/glut persistence under estimated opponent stock;
- sell-now versus hold value under floor risk;
- terminal liquidation risk;
- opponent ability to saturate a premium market.

Do not revert to action imitation or another fixed route threshold.

## CR086 candidate freeze requirements

Before CR086 performance testing, freeze:

- exact backbone SHA/provenance;
- exact inventory estimator implementation;
- exact value objective/action rule;
- training/development data boundary if any;
- fresh Gate A master;
- fresh legacy-guardrail master;
- independent high-strength-population stress cohort;
- license/attribution obligations.

## Hosted escalation rule

A CR086 hosted probe requires all:

1. fresh direct improvement versus incumbent;
2. broad legacy-anchor guardrails;
3. frozen high-strength-population stress PASS;
4. runtime-legality audit;
5. provenance/license PASS.

No hosted slot is spent merely because a public notebook has a high displayed score.

## Frontier target

Latest already-frozen top-10 checkpoint is roughly 2965–3240. The goal is a ~3000-class architecture, not incremental improvement around a 1600-class incumbent.
