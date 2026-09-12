# STATUS — Kculture live source of truth

Updated: 2026-09-12

Authoritative branch: `fix/kaggle-parity-v1`.

## Mission

Maximize probability of a prize-winning / top-10 Kaggriculture finish before 2026-09-30 23:59 UTC. No hosted submission without a passed frozen promotion gate.

## Hosted incumbents

- CR071M — submission `56124705`; last authenticated checkpoint rating 1731.8. Incumbent/calibration reference only.
- CR070A — submission `56091951`; last authenticated checkpoint rating 1724.0.

## Closed / quarantined

- CR078: closed.
- CR079 SpaTaro 1-NN clone: closed / FAIL.
- CR080 Mengfei route stitching: closed / FAIL; economic-state aliasing.
- CR081 v1/v2: invalid and quarantined before score interpretation.
- CR081 v3 run `34694092039`, master `9120813`: valid catastrophic FAIL / CLOSED; no retuning or hosted submission.
- **CR082 state-adaptive Majkel 1-NN: VALID / FAIL / CLOSED.** Canonical workflow `34708795892`, master `9120821`, candidate SHA-256 `199d32fdda64d4c8d4334f7174d1532147b75837c51104eab9a7c78aec302c2a`. Complete panel, zero errors/non-DONE:
  - vs CR071M: **0–64 = 0.0000**;
  - vs CR053: **0–64 = 0.0000**, CR071M control 32–32 = 0.5000, delta -0.5000;
  - vs CR061: **0–64 = 0.0000**, CR071M control 62–2 = 0.96875, delta -0.96875;
  - vs CR065: **0–64 = 0.0000**, CR071M control 62–2 = 0.96875, delta -0.96875.
  Mean direct reward margin `-128488.703125`; median `-129738.5`; best game still `-72758`. Frozen decision: `CLOSE_CR082_1NN_MOVE_TO_EXPLICIT_ECONOMIC_VALUE_MODEL`. No CR082A/B/C or tuning on `9120821`. Final result: `docs/strategy/CR082_FINAL_RESULT_2026-09-12.md`.

A mechanically duplicate CR082 run `34708837989` is non-canonical and permanently ignored as evidence.

## Current frontier snapshot

Authenticated run `34668645531`:

1. Majkel1337 3181.9 (`56156662`)
2. ymg_aq 3075.1 (`56161578`)
3. Unknown Mother-Goose 3056.5 (`56169353`)
4. Artem The Farmer 3029.3
5. SpaTaro 3029.0

## Architectural conclusion

CR080/081 showed that trajectories/tapes do not transport across mismatched economic states. CR082 then showed something stronger: even **correctly predicting a leader's current-step market action from current state is not equivalent to economic value for our backbone**. Behavioral fidelity is therefore closed as the primary representation.

## ACTIVE — CR083 explicit economic value

Boundary: `docs/strategy/CR083_EXPLICIT_VALUE_ARCHITECTURE_BOUNDARY_2026-09-12.md`.

Phase 0 mechanics audit: `docs/strategy/CR083_PHASE0_MECHANICS_RESULT_2026-09-12.md`, canonical run `34709053070`, exact `kaggle-environments==1.32.7`.

Phase 0 established:

- terminal reward = final money only;
- exact environment `deepcopy`/branching is supported and deterministic for identical actions;
- divergent clone actions change only the clone, not source state;
- market queues are ordered and lockstep across players;
- unsold inventory has zero terminal value;
- buy→sell same-product round trip is explicitly zero-arbitrage;
- future town-shop unlocks depend on hidden seed, so hidden future/seed cannot be a runtime feature or clairvoyant label shortcut.

CR083 must rank legal economic macros by mechanics-derived expected value under legal current observation, with opponent-action uncertainty and hidden future randomness marginalized/robustly handled. No teacher 1-NN/action oracle is allowed.

### Immediate CR083 research

Next active study is a fresh-seed **causal ablation of CR071M market-action families** to determine which investment/liquidation components materially create value for the existing physical backbone before freezing an explicit-value candidate. This study is architecture research only, not a promotion gate; it must not use master `9120821`.

## Binding policies

- Authenticated Kaggle API first.
- Exact H2H uses `kaggle-environments==1.32.7`, isolated package processes and both seats.
- Original final holdout remains sealed.
- Invalid/duplicate evaluations are quarantined before score interpretation.
- Closed hypotheses stay closed unless genuinely new evidence invalidates their closure.
- CR083 runtime features/actions may use only legal current observation plus frozen public mechanics/constants; hidden seed/future state/opponent-private state remain forbidden.
