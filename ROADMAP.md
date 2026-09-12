# ROADMAP — Kculture live plan

Updated: 2026-09-12

Objective: maximize probability of a prize-winning / top-10 Kaggriculture finish. Working source of truth is branch `fix/kaggle-parity-v1`, `STATUS.md`, and current frozen experiment protocols.

## Invariants

1. Hosted/live evidence and exact-reference W/L both matter.
2. Submission allowance is a cap, not a quota.
3. Every candidate family gets a predeclared gate before valid validation results are interpreted.
4. Mechanically or semantically invalid runs are quarantined; their scores are not strategy evidence.
5. No seed, team identity, episode ID, future state or opponent-private state as agent features.
6. Authenticated Kaggle API is the default current-meta source.
7. Original final holdout remains sealed.
8. Do not tune a failed architecture on spent validation evidence; change representation instead.

## Closed architecture classes

- CR078 late mirror breaker: closed.
- CR079 simple SpaTaro 1-NN: closed after OOT failure.
- CR080 nearest-route/day replay stitching: closed; economic-state aliasing.
- **CR081 time-indexed UMG market transplant: closed.** Valid v3 run `34694092039` lost 0–64 directly to CR071M and suffered huge guardrail regressions despite zero execution errors. Exact final results: `docs/strategy/CR081_FINAL_RESULT_2026-09-12.md`.

Combined conclusion: copying a stable action trajectory does not transport the economic state that makes those actions good. The next representation must be state-conditioned and one-step causal, not trajectory/tape imitation.

## Current frontier

Authenticated snapshot `34668645531`: Majkel 3181.9, ymg_aq 3075.1, UMG 3056.5, Artem 3029.3, SpaTaro 3029.0.

## ACTIVE — CR082 state-adaptive macro economics

Protocol: `docs/strategy/CR082_STATE_ADAPTIVE_MACRO_PROTOCOL_2026-09-12.md`.

Primary teacher: **Majkel1337**, current #1 in the frozen snapshot.

Frozen policy representation:

- same runtime step only;
- legal current economic state only: day/hour, own money, labor/hires, unlocked quadrants, own shed/seed inventory, public prices and market inventory;
- development-standardized features;
- exactly one nearest teacher state from the same step;
- copy only that step's market queue;
- no replay continuation and no farmer/hands copying;
- OOD fallback to development per-step modal queue above leave-one-out p95 distance;
- prefix fixed at runtime 0–287;
- only mechanical capacity/legality repairs inside prefix.

Old-corpus exploration is hypothesis-forming only. GitHub run `34694384742` reproduced Majkel improvement of roughly +5.49 p.p. exact and +5.45 p.p. semantic market fidelity over the step-modal baseline.

## CR082 fresh Gate A

A first fresh collection run `34694479980` loosely treated every EpisodeId absent from the original old64 as fresh and reported PASS. Audit found that 38/64 such IDs were actually older unseen episodes. This result is quarantined as **not promotion evidence**.

The old64 maximum EpisodeId is `108032343`; the current newest128 corpus contains **26 strictly later episodes**, satisfying the frozen minimum of 24.

**CURRENT RUN: `34694852503`** — strict-forward Gate A. No model or threshold changed; only the evidence filter was tightened to `EpisodeId > 108032343`.

PASS requires both on those strictly later episodes:

- state-conditioned exact market fidelity improvement over step-modal >= **+0.03 absolute**;
- state-conditioned semantic market fidelity improvement >= **+0.03 absolute**.

### If strict-forward Gate A PASS

1. build exactly one CR082 executable candidate using the already-frozen old48 Majkel development set;
2. keep CR071M physical backbone unchanged;
3. freeze package hash and a completely fresh H2H promotion panel **before results**;
4. run direct vs CR071M plus guardrails, with fresh non-overlapping seeds;
5. only a passed H2H gate can become a hosted probe.

### If strict-forward Gate A FAIL

Close CR082 1-NN without tuning k/features/p95/prefix on that evidence. Advance to **explicit economic-value / macro-selection modeling** based on game mechanics and legal current state rather than behavior imitation.

## Escalation rule

When a valid candidate passes a frozen fresh gate with material uplift, move to one controlled hosted probe rather than accumulating optional local tests. When it fails, change representation rather than optimize against spent validation seeds.
