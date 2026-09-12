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
- **CR081 v3 run `34694092039`, master `9120813`: VALID / FAIL / CLOSED.** Exact package SHA-256 `b608b8a46a67e7dbbf2c53e5f36e25a19cad708aeeab30a6e28c93321d78ec40`. Complete seven-H2H panel, zero errors/non-DONE: direct vs CR071M 0–64; severe negative guardrail deltas vs CR053/061/065. Frozen decision: `CLOSE_CR081_BRIDGE_MOVE_TO_STATE_ADAPTIVE_MACRO_POLICY`. No CR081 retuning or hosted submission.

## Current frontier snapshot

Authenticated run `34668645531`:

1. Majkel1337 3181.9 (`56156662`)
2. ymg_aq 3075.1 (`56161578`)
3. Unknown Mother-Goose 3056.5 (`56169353`)
4. Artem The Farmer 3029.3
5. SpaTaro 3029.0

## Architectural conclusion

CR080 and CR081 fail through the same deeper issue: action trajectories are not portable across mismatched economic states. The active path therefore conditions economic action on the **legal current economic state**, one step at a time, rather than copying a route/tape.

## ACTIVE — CR082 state-adaptive Majkel 1-NN

Protocols:

- `docs/strategy/CR082_STATE_ADAPTIVE_MACRO_PROTOCOL_2026-09-12.md`
- `docs/strategy/CR082_PROMOTION_PROTOCOL_2026-09-12.md`

### Strict-forward Gate A — VALID PASS

Canonical run `34694852503` evaluated only 26 Majkel episodes strictly later than the original old64 maximum EpisodeId `108032343`.

- exact fidelity: step-modal `0.788996` → state-conditioned `0.844818`, delta **+0.055823**;
- semantic fidelity: `0.810363` → `0.868990`, delta **+0.058627**;
- OOD fallback rate `0.084535`;
- all frozen checks PASS;
- decision: `ELIGIBLE_TO_BUILD_ONE_CR082_CANDIDATE`.

Loose run `34694479980` remains invalid for promotion because its unseen-ID filter included older episodes.

### Single frozen executable candidate

Canonical confirmation workflow: **`34708795892`**, master seed **`9120821`**.

Candidate SHA-256:
`199d32fdda64d4c8d4334f7174d1532147b75837c51104eab9a7c78aec302c2a`

Base CR071M SHA-256:
`dbc6fc2b2c3673b1d9fc36e103b8369a53c7f2cc33381e11a3cb5f769bebe652`

Frozen implementation:

- exact CR071M physical/runtime backbone, same-step farmer/hands unchanged;
- runtime market policy only steps 0–287;
- oldest 48/64 original Majkel episodes as teacher;
- 41 legal current-state features;
- per-step z-score Euclidean `k=1`;
- per-step leave-one-out p95 OOD threshold; modal fallback;
- CR053 strategic counter-market and dead_stock disabled only inside prefix;
- room_guard, SELL clamping and same-turn BUY_PRODUCT→later SELL legality retained;
- no identity, EpisodeId, seed, future state, opponent-private state, or replay continuation.

Prepare gate passed before H2H:

- strict-forward Gate A reproduced;
- runtime predictor equivalence: **2304/2304**;
- CR071M farmer/hands equivalence: **1440/1440**;
- deterministic rebuild: byte-identical;
- 32 H2H seeds from master `9120821`, overlap **0** with registered prior masters.

Seven frozen H2Hs are active: CR082 vs CR071M/CR053/CR061/CR065 and same-seed CR071M guardrail controls. No hosted submission is part of this workflow.

A mechanically duplicate run `34708837989` was accidentally triggered while confirming workflow registration. It is **non-canonical and must never be counted as independent evidence**; only `34708795892` determines the frozen CR082 decision.

## Binding policies

- Authenticated Kaggle API first.
- Exact H2H uses `kaggle-environments==1.32.7`, isolated package processes and both seats.
- Original final holdout remains sealed.
- Invalid/duplicate evaluations are quarantined before score interpretation.
- Closed hypotheses stay closed unless genuinely new evidence invalidates their closure.
- CR082 FAIL means no CR082A/B/C or tuning on master `9120821`; change representation to explicit economic-value / macro-selection modeling.
