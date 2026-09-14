# ROADMAP — Kculture live plan

Updated: 2026-09-14

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

CR078, CR079, CR080, CR081, CR082, CR084 and CR085 remain closed. Do not retune their spent mechanisms.

## ACTIVE — CR083 hosted maturation

Frozen SHA `648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`; submission `56199767`.

Latest already-frozen checkpoint: CR083 `1660.3`, CR071M `1638.8`, lead `+21.5`, about 76 public episodes plus validation.

Do not poll again before the 100-public-episode maturity boundary unless another material decision requires it.

## CR086 Stage 1A — opponent-stock representation COMPLETE / PASS

Independent confirmation over 100,660 commodity-step observations:

- MAE `1.25005`;
- p95 `9`;
- interval coverage `0.969462`;
- `stock >= 10` accuracy `0.956338`.

Decision: `OPPONENT_INVENTORY_REPRESENTATION_FEASIBILITY_PASS`.

Implementation/evaluation: `tools/cr086_opponent_inventory_estimator_eval.py`.

This is representation evidence only. No arbitrary stock threshold policy is allowed from this result.

## CR086 Stage 1B — public-backbone acquisition COMPLETE

Read-only run `34790801576`, artifact `10327672303`.

Executable deterministic public agents frozen from notebook source:

- Shape the Shop Work the Pasture (TOP 10): archive SHA `fa9e7eb1a0174a1bf292fb4d47bd209defed929758214d3506e050a68ee5f98f`;
- V29-R1 Adaptive Market Hysteresis: archive SHA `8dc512911c0173483211314f63cbf1d7e460cad33dfbc02f0f77d023f6d809fe`;
- Farming Score V3 Replay Revised: archive SHA `5cde13b09e9506f24b2f5df05719b597fe07ebbb6dead7da12894beda203e419`.

Tetsutani's pulled notebook is analytical/visual and is not a direct H2H agent.

Static audit: `docs/strategy/CR086_PUBLIC_BACKBONE_ARCHITECTURE_AUDIT_2026-09-14.md`.

## CR086 Stage 1C — frozen public-backbone H2H ACTIVE

Protocol: `docs/strategy/CR086_PUBLIC_BACKBONE_BENCHMARK_PROTOCOL_2026-09-13.md`.

Run: **`34798209070`**.

Frozen benchmark:

- each of the three unmodified executable public agents versus exact CR083;
- 16 fresh seeds × both seats = 32 games per pair;
- master `9160861` with fresh-seed firewall;
- exact reference runtime 1.32.7 and isolated package processes;
- promising screen: zero errors/non-DONE, score rate `>=0.5625`, mean terminal-money margin `>0`;
- no retuning from partial results;
- no hosted submission.

The run was checked once immediately after creation and was queued. Do not check it again until the next user turn/material boundary.

## Architecture choices after benchmark

### If TOP 10 passes

Treat its productive-structure layer as the leading physical-backbone candidate. Audit provenance/license first. Then design a separately frozen test of whether the validated opponent-stock estimator improves its demand/sale choices. Do not alter the public agent based on benchmark-specific losses before that protocol is frozen.

### If Adaptive Market Hysteresis passes

This is the most natural host for the inventory representation. Its current controller estimates decaying **public flow pressure** but not hidden current opponent stock. A clean CR086 experiment can test whether inventory estimate/bounds improve sell-now vs hold, glut persistence and saturation risk without replacing its production route.

### If Farming Score V3 passes

Benchmark its 72-turn affordability guard and two-route design, but treat it as lower novelty because it is closest to the existing route architecture. Do not prioritize it over a passing structurally different backbone without stronger evidence.

### If no public backbone passes

Do not retune the public agents on this spent benchmark. Reimplement the useful mechanisms cleanly in our own architecture, with the opponent-stock representation as a first-class state variable, then freeze a new independent Gate A.

## CR086 Stage 2 — convert opponent stock into explicit economic value

A candidate must map inventory estimate/range to an economically justified action objective. Candidate mechanisms may include:

- expected market-price impact from latent opponent supply;
- scarcity/glut persistence;
- sell-now versus hold value;
- opponent saturation capacity;
- terminal liquidation/floor risk;
- demand-aligned production allocation.

Prefer causal action/value logic over another fixed route threshold.

## Candidate freeze requirements

Before any CR086 performance test, freeze:

- exact backbone SHA and provenance;
- exact inventory estimator implementation;
- exact value objective/action rule;
- development-data boundary if any;
- fresh Gate A and guardrail masters;
- independent high-strength stress cohort;
- runtime-legality audit;
- license/attribution obligations.

## Hosted escalation rule

A CR086 hosted probe requires all:

1. fresh direct improvement versus incumbent;
2. broad legacy-anchor guardrails;
3. frozen high-strength-population stress PASS;
4. runtime-legality PASS;
5. provenance/license PASS.

No hosted slot is spent merely because a public notebook has a high displayed score.

## Frontier target

Latest already-frozen top-10 checkpoint is roughly 2965–3240. The objective is a ~3000-class architecture, not incremental improvement around a 1600-class incumbent.
