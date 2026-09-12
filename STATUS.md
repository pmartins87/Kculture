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
- CR081 v3 run `34694092039`, master `9120813`: valid catastrophic FAIL / CLOSED.
- **CR082 state-adaptive Majkel 1-NN: VALID / FAIL / CLOSED.** Canonical workflow `34708795892`, master `9120821`, candidate SHA-256 `199d32fdda64d4c8d4334f7174d1532147b75837c51104eab9a7c78aec302c2a`. It lost 0–64 directly to CR071M and 0–64 to CR053/CR061/CR065 with zero errors/non-DONE. No CR082A/B/C. Final result: `docs/strategy/CR082_FINAL_RESULT_2026-09-12.md`.

CR082 duplicate run `34708837989` is non-canonical and permanently ignored.

## Current frontier snapshot

Authenticated run `34668645531`: Majkel1337 3181.9, ymg_aq 3075.1, Unknown Mother-Goose 3056.5, Artem 3029.3, SpaTaro 3029.0.

## Architectural conclusion

CR080/081 showed that trajectories/tapes do not port across mismatched states. CR082 showed that even correctly predicting a leader's same-step action from current state is not equivalent to economic value for our backbone. Behavioral imitation is closed as the primary representation.

## ACTIVE — CR083 explicit economic value

Boundary: `docs/strategy/CR083_EXPLICIT_VALUE_ARCHITECTURE_BOUNDARY_2026-09-12.md`.

Phase 0 mechanics audit: `docs/strategy/CR083_PHASE0_MECHANICS_RESULT_2026-09-12.md`, run `34709053070`. Exact branching is available offline; terminal reward is final money; hidden seed/future shop draws remain prohibited from runtime features/clairvoyant labels.

### Phase 1 — COMPLETE causal market-family ablation

Canonical run `34715158344`, exploratory master `9130830`, 8 fresh seeds × both seats =16 games/variant. Architecture evidence only; never promotion evidence.

Every broad deletion lost **0–16** to exact CR071M with zero execution failures:

- NO_HIRE mean margin `-155494.1`;
- NO_BUY_ANIMAL `-153976.4`;
- NO_BUY_SEED `-152182.4`;
- NO_BUY_PRODUCT `-139142.0`;
- NO_SELL `-138184.8`;
- NO_BUY_LAND `-70241.5`.

Conclusion: there is no expendable market family. CR071M's economy is tightly coupled to its physical route; CR083 must make narrow within-family interventions only. Result: `docs/strategy/CR083_PHASE1_CAUSAL_ABLATION_RESULT_2026-09-12.md`.

### Phase 2 — ACTIVE route-aware future-seed-demand clamp

Protocol frozen before candidate evaluation: `docs/strategy/CR083_PHASE2_SEED_DEMAND_CLAMP_PROTOCOL_2026-09-12.md`.

Mechanics invariant:

- after the final route-switch checkpoint (`step 433`), current route is fixed;
- seeds are private, not sellable, do not occupy shed capacity and have zero terminal value;
- a seed above the selected route's remaining maximum `PLANT` demand cannot create value;
- candidate therefore clamps only final `BUY_SEED` quantities for `step >= 434` to remaining route PLANT demand minus projected post-current-turn seed stock;
- same-turn atomic PLANT validation is mirrored exactly;
- farmer/hands, route selection, all non-seed market orders and all CR071M safety logic remain unchanged;
- seed quantity can only decrease, never increase.

Canonical workflow launched: **`34715575445`**.

Evaluation is automatic and frozen:

1. deterministic build + score-blind exact-observation shadow audit;
2. Gate A master `9130831`: 16 fresh seeds × both seats =32 direct games vs CR071M; PASS requires score >=0.5625, positive mean margin, zero failures;
3. only if Gate A PASS, unchanged hash advances automatically to promotion master `9130832`, seven-row 64-game direct+guardrail panel;
4. no hosted submission occurs automatically.

Phase-1 master `9130830`, CR082 master `9120821`, and all earlier masters are excluded by firewall.

## Binding policies

- Authenticated Kaggle API first.
- Exact H2H uses `kaggle-environments==1.32.7`, isolated package processes and both seats.
- Original final holdout remains sealed.
- Invalid/duplicate evaluations are quarantined before score interpretation.
- Closed hypotheses stay closed unless genuinely new evidence invalidates their closure.
- Runtime features/actions may use only legal current observation plus frozen public mechanics/constants; hidden seed/future state/opponent-private state remain forbidden.
