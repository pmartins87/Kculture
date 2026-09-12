# ROADMAP — Kculture live plan

Updated: 2026-09-12

Objective: maximize probability of a prize-winning / top-10 Kaggriculture finish. Working source of truth is branch `fix/kaggle-parity-v1`, `STATUS.md`, and frozen experiment protocols.

## Invariants

1. Hosted/live evidence and exact-reference W/L both matter.
2. Submission allowance is a cap, not a quota.
3. Every candidate family gets a predeclared gate before validation results are interpreted.
4. Invalid evaluations are quarantined; their scores are not strategy evidence.
5. No seed, team identity, EpisodeId, future state or opponent-private state as runtime features.
6. Authenticated Kaggle API is the default current-meta source.
7. Original final holdout remains sealed.
8. Do not tune a failed architecture on spent validation evidence; change representation instead.

## Closed architecture classes

- CR078 late mirror breaker.
- CR079 SpaTaro 1-NN.
- CR080 replay/route stitching.
- CR081 time-indexed market transplant.
- CR082 same-step state-conditioned teacher 1-NN.

Combined conclusion: neither trajectory imitation nor behavioral prediction establishes causal economic value for CR071M. The active representation is mechanics-derived value with a very small intervention surface.

## ACTIVE — CR083 explicit economic value

Phase 0 (`34709053070`) established exact mechanics and offline branching.

### Phase 1 — complete

Causal deletion run `34715158344`, master `9130830`, removed one final market family at a time from exact CR071M. Every variant lost 0–16. Therefore **all broad market families are essential** and whole-family disabling is closed. See `docs/strategy/CR083_PHASE1_CAUSAL_ABLATION_RESULT_2026-09-12.md`.

### Phase 2 — route-aware future-seed-demand clamp

Protocol: `docs/strategy/CR083_PHASE2_SEED_DEMAND_CLAMP_PROTOCOL_2026-09-12.md`.

This is not a broad BUY_SEED reduction. It removes only seed quantity that is mechanically unusable by the already-selected own route after the last route switch:

- active only from `step >= 434`;
- compute selected-route future PLANT demand by crop from `step+1` onward;
- project current seed stock after same-turn physical PLANT requests using exact atomic validation semantics;
- clamp each final `BUY_SEED` order to the remaining maximum usable quantity;
- preserve farmer/hands, route switches, all non-seed orders and all CR071M safety logic.

Why this is admissible: seeds cannot be sold, do not affect the public market/shed, and have zero terminal value unless consumed by a later PLANT command.

Canonical workflow: **`34715575445`**.

Frozen sequence:

1. deterministic candidate build;
2. score-blind shadow audit on exact official observations; any difference outside allowed BUY_SEED reduction aborts before scoring;
3. fresh Gate A master `9130831`: 32 direct games vs CR071M; PASS requires >=0.5625 score rate, positive mean margin and zero failures;
4. only on PASS, the identical candidate hash automatically advances to master `9130832` seven-row promotion panel;
5. promotion PASS requires direct >=0.5625, aggregate guardrail delta >=0 and every guardrail delta >=-0.0625;
6. only then refresh authenticated hosted slots and consider exactly one hosted probe.

No parameter, crop exception or activation boundary may be retuned on `9130831`/`9130832` if this mechanism fails.

## Escalation rule

When a frozen mechanism passes fresh direct and broad guardrail evidence, move to one controlled hosted probe rather than accumulating optional local tests. When it fails, preserve the backbone and move to another mechanically independent value invariant rather than tuning the failed rule.
