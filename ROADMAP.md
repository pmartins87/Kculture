# ROADMAP — Kculture live plan

Updated: 2026-09-12

Objective: maximize probability of a prize-winning / top-10 Kaggriculture finish. Working source of truth is branch `fix/kaggle-parity-v1`, `STATUS.md`, and current frozen experiment protocols.

## Invariants

1. Hosted/live evidence and exact-reference W/L both matter.
2. Submission allowance is a cap, not a quota.
3. Every candidate family gets a predeclared gate before valid validation results are interpreted.
4. Mechanically or semantically invalid runs are quarantined; their scores are not strategy evidence.
5. No seed, team identity, EpisodeId, future state or opponent-private state as agent features.
6. Authenticated Kaggle API is the default current-meta source.
7. Original final holdout remains sealed.
8. Do not tune a failed architecture on spent validation evidence; change representation instead.

## Closed architecture classes

- CR078 late mirror breaker: closed.
- CR079 simple SpaTaro 1-NN: closed after OOT failure.
- CR080 nearest-route/day replay stitching: closed; economic-state aliasing.
- CR081 time-indexed UMG market transplant: closed after valid v3 catastrophic H2H failure.

Combined conclusion: copying a stable action trajectory does not transport the economic state that makes those actions good. Economic decisions must be conditioned on current legal state rather than trajectory identity.

## Current frontier

Authenticated snapshot `34668645531`: Majkel 3181.9, ymg_aq 3075.1, UMG 3056.5, Artem 3029.3, SpaTaro 3029.0.

## ACTIVE — CR082 state-adaptive Majkel 1-NN

The strict-forward fresh Gate A is complete and **PASS** in canonical run `34694852503` using 26 episodes strictly later than the original 64-episode corpus.

Observed fresh uplift over step-modal baseline:

- exact: **+0.055823** absolute;
- semantic: **+0.058627** absolute;
- frozen requirement for each: +0.03.

Exactly one executable candidate is therefore authorized and frozen:

- CR071M same-step physical backbone unchanged;
- market steps 0–287 only;
- teacher = oldest 48 of the fixed original Majkel64 corpus;
- 41 legal current-state features;
- per-step z-score Euclidean 1-NN, `k=1`;
- leave-one-out p95 OOD threshold with step-modal fallback;
- only mechanical legality/capacity transforms allowed inside prefix.

Candidate SHA-256:
`199d32fdda64d4c8d4334f7174d1532147b75837c51104eab9a7c78aec302c2a`

Canonical frozen H2H workflow: **`34708795892`**, master **`9120821`**. Prepare/self-audit/deterministic-rebuild/seed-firewall all PASS. Duplicate run `34708837989` is non-canonical and ignored.

### Frozen H2H promotion gate

Seven rows, each 32 fresh seeds × both seats = 64 games:

1. CR082 vs CR071M;
2. CR082 vs CR053;
3. CR082 vs CR061;
4. CR082 vs CR065;
5. CR071M vs CR053;
6. CR071M vs CR061;
7. CR071M vs CR065.

PASS requires all of:

- complete panel and zero errors/non-DONE;
- direct CR082 vs CR071M score rate >= **0.5625**;
- aggregate guardrail delta >= 0;
- each individual guardrail delta >= **-0.0625**.

### If CR082 H2H PASS

Freeze exact tested hash, refresh authenticated hosted slot/submission state, then make **exactly one controlled hosted probe** if slot accounting permits. Do not add optional local tuning first.

### If CR082 H2H FAIL

Close CR082 1-NN. No CR082A/B/C, no k/feature/p95/prefix/teacher tuning on the spent seeds. Advance directly to **CR083 explicit economic-value / macro-selection modeling** from legal current game state and mechanics, rather than behavior imitation.

## Escalation rule

When a valid candidate passes a frozen fresh gate with material uplift, move to one controlled hosted probe rather than accumulating optional local tests. When it fails, change representation rather than optimize against spent validation seeds.
