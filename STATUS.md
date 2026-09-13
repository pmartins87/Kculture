# STATUS — Kculture live source of truth

Updated: 2026-09-13

Authoritative branch: `fix/kaggle-parity-v1`.

## Mission

Maximize probability of a prize-winning / top-10 Kaggriculture finish before 2026-09-30 23:59 UTC. No hosted submission without a passed frozen promotion gate.

## Hosted live state

Authenticated hosted-status run `34745664559` (2026-09-13 07:37 UTC):

- **CR083** — submission `56199767`, `CR083.tar.gz`, description `CR083_FROZEN_PROBE_648FBCDB`, status `COMPLETE`, current API public score **1563.9**. Submitted 2026-09-13 05:21:53 UTC. The hosted package is byte-identical to frozen SHA-256 `648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`.
- **CR071M control** — submission `56124705`, current API public score **1647.2**.
- CR083 is therefore **-83.3 rating points** behind CR071M at this early checkpoint.
- CR083 has **34 listed completed episodes: 33 public + 1 validation**. CR071M has 361 listed completed episodes at the same checkpoint.
- CR070A — submission `56091951`, current API public score `1637.9`; it is now older than the two live recent submissions CR083 + CR071M.

This is **negative hosted evidence but still provisional** because CR083 is much less mature than CR071M. No CR083 retuning and no additional hosted submission is authorized from this checkpoint alone.

## Current hosted frontier snapshot

Same authenticated run `34745664559`:

1. Majkel1337 `3214.8`
2. Mengfei Li `3071.1`
3. Artem The Farmer `3032.6`
4. THIRD FARM CLUB `3031.1`
5. ymg_aq `3023.1`
6. SpaTaro `3018.2`
7. feel the agi `3002.8`
8. Otter Vibe `2986.1`
9. Subramanya N `2974.5`
10. binghua `2967.2`

The current top-10 frontier remains roughly **1400 rating points above CR083**. Closing that gap requires a representation/proxy breakthrough rather than incremental hosted probing.

## Closed / quarantined

- CR078: closed.
- CR079 SpaTaro 1-NN clone: closed / FAIL.
- CR080 Mengfei route stitching: closed / FAIL; economic-state aliasing.
- CR081 v1/v2: invalid and quarantined before score interpretation.
- CR081 v3 run `34694092039`, master `9120813`: valid catastrophic FAIL / CLOSED.
- **CR082 state-adaptive Majkel 1-NN: VALID / FAIL / CLOSED.** Canonical workflow `34708795892`, master `9120821`, candidate SHA-256 `199d32fdda64d4c8d4334f7174d1532147b75837c51104eab9a7c78aec302c2a`. It lost 0–64 directly to CR071M and 0–64 to CR053/CR061/CR065 with zero errors/non-DONE. No CR082A/B/C. Final result: `docs/strategy/CR082_FINAL_RESULT_2026-09-12.md`.

CR082 duplicate run `34708837989` is non-canonical and permanently ignored.

## Architectural conclusion

CR080/081 showed that trajectories/tapes do not port across mismatched states. CR082 showed that even correctly predicting a leader's same-step action from current state is not equivalent to economic value for our backbone. Behavioral imitation is closed as the primary representation.

CR083 now adds a new warning: a mechanism can strongly dominate CR071M on fresh exact local H2H and still start below CR071M in the live population. Therefore **local H2H against our anchor panel is not by itself a sufficient proxy for hosted metagame value**. Hosted replay forensics is active to identify the missing population signal.

## ACTIVE — CR083 explicit economic value

Boundary: `docs/strategy/CR083_EXPLICIT_VALUE_ARCHITECTURE_BOUNDARY_2026-09-12.md`.

Phase 0 mechanics audit: `docs/strategy/CR083_PHASE0_MECHANICS_RESULT_2026-09-12.md`, run `34709053070`.

### Phase 1 — COMPLETE causal market-family ablation

Canonical run `34715158344`, exploratory master `9130830`, 8 fresh seeds × both seats =16 games/variant. Every broad deletion lost 0–16 to exact CR071M. Broad family deletion remains closed.

### Phase 2 — LOCAL PROMOTION PASS / HOSTED PROBE ACTIVE

Protocol: `docs/strategy/CR083_PHASE2_SEED_DEMAND_CLAMP_PROTOCOL_2026-09-12.md`.

Canonical promotion run: **`34715575445`**.

Frozen package artifact: `cr083-phase2-frozen-packages-v1`, artifact ID `10304915100`.

Frozen candidate SHA-256: **`648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`**.

Fresh local promotion result:

- CR083 vs CR071M: **45W–1L–18T = 0.84375** over 64 games;
- direct median money margin: **+240**;
- direct mean money margin: **+172.5**;
- guardrail score delta vs CR053/CR061/CR065: **0 / 0 / 0**;
- zero execution errors and zero incomplete games.

Frozen hosted probe workflow `34740104210` re-downloaded artifact `10304915100`, verified exact SHA-256, confirmed no duplicate probe, and submitted exactly once. Kaggle registered submission **`56199767`** and reported `4 submissions remaining today` after the upload.

Hosted checkpoint workflow `34745664559` now shows `COMPLETE`, score `1563.9`, 33 public episodes, versus CR071M `1647.2`. This is a **provisional hosted underperformance of -83.3 points**.

Read-only hosted replay forensics run `34745733865` is active against the public CR083 episodes. Its purpose is diagnostic only: quantify actual hosted W/L/margins/opponent mix and identify why local promotion evidence failed to transfer. No runtime identity/opponent-private/hidden-seed information may be introduced from this analysis.

## Binding policies

- Authenticated Kaggle API first.
- Exact H2H uses `kaggle-environments==1.32.7`, isolated package processes and both seats.
- Original final holdout remains sealed.
- Invalid/duplicate evaluations are quarantined before score interpretation.
- Closed hypotheses stay closed unless genuinely new evidence invalidates their closure.
- Runtime features/actions may use only legal current observation plus frozen public mechanics/constants; hidden seed/future state/opponent-private state remain forbidden.
- CR083 hosted package remains immutable at SHA-256 `648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`.
- **No new hosted submission and no CR083 retuning while the current hosted probe is being diagnosed.**
