# STATUS — Kculture live source of truth

Updated: 2026-09-13

Authoritative branch: `fix/kaggle-parity-v1`.

## Mission

Maximize probability of a prize-winning / top-10 Kaggriculture finish before 2026-09-30 23:59 UTC. No hosted submission without a passed frozen promotion gate.

## Hosted incumbents

Fresh authenticated own-submission accounting run `34740003554` (2026-09-13):

- CR071M — submission `56124705`, current API public score `1658.1`, submitted 2026-09-09 14:02:10 UTC.
- CR070A — submission `56091951`, current API public score `1640.8`, submitted 2026-09-08 06:01:30 UTC.
- No team submission has been made since CR071M; current daily submission allowance is therefore unused by this team.

The two most recent submissions are the live incumbents. CR083 has not yet been submitted at this checkpoint.

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

## ACTIVE — CR083 explicit economic value

Boundary: `docs/strategy/CR083_EXPLICIT_VALUE_ARCHITECTURE_BOUNDARY_2026-09-12.md`.

Phase 0 mechanics audit: `docs/strategy/CR083_PHASE0_MECHANICS_RESULT_2026-09-12.md`, run `34709053070`. Exact branching is available offline; terminal reward is final money; hidden seed/future shop draws remain prohibited from runtime features/clairvoyant labels.

### Phase 1 — COMPLETE causal market-family ablation

Canonical run `34715158344`, exploratory master `9130830`, 8 fresh seeds × both seats =16 games/variant. Architecture evidence only; never promotion evidence.

Every broad deletion lost **0–16** to exact CR071M with zero execution failures. Conclusion: there is no expendable market family. CR071M's economy is tightly coupled to its physical route; CR083 must make narrow within-family interventions only.

### Phase 2 — PROMOTION PASS / frozen hosted-probe candidate

Protocol: `docs/strategy/CR083_PHASE2_SEED_DEMAND_CLAMP_PROTOCOL_2026-09-12.md`.

Canonical run: **`34715575445`**.

Frozen package artifact: `cr083-phase2-frozen-packages-v1`, artifact ID `10304915100`.

Frozen candidate: `CR083.tar.gz`.

Frozen candidate SHA-256: **`648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`**.

Mechanism remains exactly the predeclared route-aware future-seed-demand clamp from `step >= 434`; farmer/hands, route selection, non-seed market actions and CR071M safety logic are unchanged.

Promotion result on fresh master `9130832`:

- CR083 vs CR071M: **45W–1L–18T = 0.84375** over 64 games;
- direct median money margin: **+240**;
- direct mean money margin: **+172.5**;
- guardrail score delta vs CR053: **0**;
- guardrail score delta vs CR061: **0**;
- guardrail score delta vs CR065: **0**;
- execution errors: **0**;
- incomplete/non-DONE: **0**.

Frozen gate decision: **`ELIGIBLE_FOR_ONE_HOSTED_PROBE_AFTER_SLOT_ACCOUNTING`**.

Fresh authenticated slot accounting: workflow run **`34740003554`**. It listed 19 historical team submissions and none after 2026-09-09, so the team has not spent any daily submission allowance today. Exactly one CR083 hosted probe is authorized. No CR083A/B/C and no retuning before that probe.

## Binding policies

- Authenticated Kaggle API first.
- Exact H2H uses `kaggle-environments==1.32.7`, isolated package processes and both seats.
- Original final holdout remains sealed.
- Invalid/duplicate evaluations are quarantined before score interpretation.
- Closed hypotheses stay closed unless genuinely new evidence invalidates their closure.
- Runtime features/actions may use only legal current observation plus frozen public mechanics/constants; hidden seed/future state/opponent-private state remain forbidden.
- Hosted CR083 probe must be byte-identical to SHA-256 `648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8` and may be submitted exactly once under this authorization.
