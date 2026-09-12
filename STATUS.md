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
- CR080 Mengfei route stitching: closed / FAIL. Post-failure diagnosis identified economic-state aliasing; nearest-route/day replay stitching is closed.
- CR081 v1 run `34671122716`, master `9120811`: INVALID replay/runtime indexing.
- CR081 v2 run `34671446692`, master `9120812`: INVALID because inherited strategic market transforms remained active inside the UMG overlay. Both were quarantined before score interpretation.
- **CR081 v3 run `34694092039`, master `9120813`: VALID / FAIL / CLOSED.** Exact package SHA-256 `b608b8a46a67e7dbbf2c53e5f36e25a19cad708aeeab30a6e28c93321d78ec40`. Complete seven-H2H panel, zero errors/non-DONE:
  - vs CR071M: **0–64 = 0.0000**;
  - vs CR053: **0–64 = 0.0000** vs CR071M 40–24 = 0.6250, delta -0.6250;
  - vs CR061: **6–58 = 0.09375** vs CR071M 64–0 = 1.0000, delta -0.90625;
  - vs CR065: **4–60 = 0.06250** vs CR071M 60–4 = 0.9375, delta -0.8750.
  Frozen decision: `CLOSE_CR081_BRIDGE_MOVE_TO_STATE_ADAPTIVE_MACRO_POLICY`. No CR081A/B/C, no boundary or quantity retuning, no hosted submission. Final analysis: `docs/strategy/CR081_FINAL_RESULT_2026-09-12.md`.

## Current frontier snapshot

Authenticated run `34668645531`:

1. Majkel1337 3181.9 (`56156662`)
2. ymg_aq 3075.1 (`56161578`)
3. Unknown Mother-Goose 3056.5 (`56169353`)
4. Artem The Farmer 3029.3
5. SpaTaro 3029.0

## Architectural conclusion

CR080 and CR081 fail through the same deeper issue from different directions: action trajectories are not portable across mismatched economic states. CR081 Gate A proved UMG's market tape is chronologically stable (~94.96% exact holdout fidelity), yet faithfully transplanting that tape onto CR071M caused catastrophic losses. Temporal predictability is therefore not causal portability.

The active research path must condition economic actions on the **legal current economic state**, one step at a time, rather than copy a route or market tape.

## ACTIVE — CR082 state-adaptive macro economics

Protocol: `docs/strategy/CR082_STATE_ADAPTIVE_MACRO_PROTOCOL_2026-09-12.md`.

Frozen representation:

- primary teacher = current #1 Majkel1337;
- same runtime step only;
- legal current-state features: day/hour, own money, labor count/hires, unlocked quadrants, own shed and seed inventory, public prices and market inventory;
- standardized on frozen teacher development data;
- one nearest teacher state from the same runtime step supplies **only that step's market queue**;
- OOD fallback to per-step modal market when distance exceeds development leave-one-out p95;
- no replay continuation, no farmer/hands copying, no identity/private-opponent features;
- active prefix fixed at runtime 0–287;
- only capacity/legality repairs permitted inside prefix.

Old-corpus exploration (hypothesis-forming only) found Majkel exact market fidelity 0.7949 -> 0.8498 (+0.0549) and semantic fidelity 0.8162 -> 0.8707 (+0.0545), reproduced in GitHub run `34694384742`.

### Fresh Gate A audit

Loose fresh-gate run `34694479980` initially reported PASS using 64 EpisodeIds absent from old64, but audit found 38 were older unseen episodes. That result is **not promotion evidence**.

The original old64 maximum EpisodeId is `108032343`. The current newest128 corpus contains **26 strictly later episodes** (`EpisodeId > 108032343`), enough to meet the frozen minimum of 24.

**Current valid Gate A run: `34694852503`**, strict-forward filter only. No model, feature, k, p95, prefix or threshold changed. It must beat step-modal by >= +0.03 absolute in both exact and semantic fidelity on those strictly later episodes. Only PASS makes one executable CR082 candidate eligible to be built.

## Binding policies

- Authenticated Kaggle API first.
- Exact H2H uses `kaggle-environments==1.32.7`, isolated package processes and both seats.
- Original final holdout remains sealed.
- Invalid evaluations are quarantined before score interpretation.
- Closed hypotheses stay closed unless genuinely new evidence invalidates their closure.
