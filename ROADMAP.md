# ROADMAP — Kculture live plan

Updated: 2026-09-13

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

Causal deletion run `34715158344`, master `9130830`, removed one final market family at a time from exact CR071M. Every variant lost 0–16. Therefore all broad market families are essential and whole-family disabling is closed.

### Phase 2 — local promotion complete / one hosted probe next

Protocol: `docs/strategy/CR083_PHASE2_SEED_DEMAND_CLAMP_PROTOCOL_2026-09-12.md`.

Canonical promotion workflow: **`34715575445`**.

Frozen candidate SHA-256: **`648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`** from artifact `10304915100` (`CR083.tar.gz`).

Fresh promotion result:

- direct vs CR071M: **45W–1L–18T = 0.84375**;
- median margin `+240`, mean margin `+172.5`;
- guardrail score deltas vs CR053/CR061/CR065: **0 / 0 / 0**;
- zero execution errors and zero incomplete games.

Frozen decision: **`ELIGIBLE_FOR_ONE_HOSTED_PROBE_AFTER_SLOT_ACCOUNTING`**.

Fresh authenticated slot accounting run `34740003554` lists no team submissions after 2026-09-09, so current daily allowance is unused. The next action is exactly one hosted submission of the byte-identical frozen candidate. Before submission the workflow must re-check the SHA and abort if an identical CR083 probe is already present.

No parameter, crop exception, activation boundary, rebuild, CR083A/B/C or other retuning is allowed before this hosted probe.

## After the hosted probe

- Record submission ID, status, filename, exact SHA and timestamps immediately.
- Refresh authenticated own submissions/frontier.
- Do not judge the bot from an immature live rating; keep local promotion evidence separate from live rating convergence.
- Preserve CR071M as calibration/control and treat CR083 as the only newly authorized live experiment.
- Any next architecture change requires a new independent mechanism and fresh preregistered evidence; do not tune Phase 2 on its spent validation panel.

## Escalation rule

When a frozen mechanism passes fresh direct and broad guardrail evidence, move to one controlled hosted probe rather than accumulating optional local tests. When it fails, preserve the backbone and move to another mechanically independent value invariant rather than tuning the failed rule.
