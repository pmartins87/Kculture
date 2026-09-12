# ROADMAP — Kculture live plan

Updated: 2026-09-11 local / 2026-09-12 UTC boundary

Objective: maximize probability of a prize-winning / top-10 Kaggriculture finish. Working source of truth is branch `fix/kaggle-parity-v1`, together with `STATUS.md` and the current frozen experiment protocols. Historical roadmap versions remain in Git history and are not operational instructions.

## Invariants

1. Hosted/live evidence and exact-reference W/L both matter; neither replaces the other.
2. Five daily submissions are a cap, not a quota. Do not retire an active slot for an unqualified candidate.
3. Every candidate family gets a predeclared gate before its validation result is observed.
4. Failed validation data may diagnose failure but may not be used to retune the same candidate until it passes.
5. No use of seed, team identity, episode ID, future state or opponent-private state as an agent feature.
6. Authenticated official Kaggle API is the default current-meta source.
7. Original final holdout remains sealed.

## Completed / closed

- CR071M hosted as submission `56124705`; it is now an incumbent/calibration reference, not the main research path.
- CR078 late mirror breaker: closed.
- CR079 simple SpaTaro nearest-neighbor clone: closed after OOT generalization failure.
- CR080 Mengfei daily-route bridge: closed after independent confirmation run `34655496708` failed its frozen direct and guardrail gates. No CR080A/B/C retuning.

## Stage 1 — explain CR080 failure without rescuing it

**CURRENT RUN:** `34668446703`.

Purpose: determine whether CR080 failed mainly through labor-plan drift, position-repair cascades, day-to-day route stitching/economic drift, or because the Mengfei route family itself is strategically inadequate.

Decision:

- strong labor/repair/stitching signal -> eliminate replay-route follower architecture and require explicit state-aware labor/production modeling;
- weak mechanical signal -> treat failure as strategic and eliminate Mengfei bridge directly.

This diagnostic cannot promote CR080 and uses already-spent confirmation seeds only descriptively.

## Stage 2 — current-frontier target selection

**COMPLETE:** authenticated frontier refresh run `34668645531`.

Snapshot top:

1. Majkel1337 3181.9 (`56156662`)
2. ymg_aq 3075.1 (`56161578`)
3. Unknown Mother-Goose 3056.5 (`56169353`)
4. Artem The Farmer 3029.3
5. SpaTaro 3029.0

Selection rule applied before deep-corpus inspection: target Unknown Mother-Goose because it is the strongest current agent with a demonstrated bridge to the CR071M lineage. Recent CR071M losses against a related family show ~90% farmer / 74.5% hands / 78.8% market equality to sampled UMG over steps 0–191 while still losing by roughly 4k–9.6k reward.

## Stage 3 — CR081 deep corpus and Gate A

**CURRENT RUN:** `34669006417`.

Frozen collection:

- UMG `56169353`: newest 128 episodes — primary;
- Majkel `56156662`: newest 64 — context;
- ymg_aq `56161578`: newest 64 — context.

Protocol: `docs/strategy/CR081_CURRENT_3056_BRIDGE_PROTOCOL_2026-09-11.md`.

CR081 Gate A passes only if the newest-25% UMG holdout preserves enough of the known physical lineage and exposes a reproducible market/economy transformation. Required first-192 similarity to the frozen bridge-family reference: median farmer >=0.80, hands >=0.60; market must either have exact step-modal coverage >=0.65 or a legal state-conditioned semantic model must beat step-only market fidelity by >=0.10 absolute.

If Gate A fails, no CR081A/B/C threshold rescue. Move to a state-adaptive macro-economic policy using current-frontier corpora.

## Stage 4 — one CR081 executable candidate, only if Gate A passes

Architecture constraints:

- preserve CR071M physical backbone where the current 3056 lineage demonstrably agrees;
- port stable market/economic semantics, plus only physical actions strictly required by current state;
- reconstruct all actions from legal current observation;
- no nearest-replay route stitching;
- no opponent-name classifier.

Before any H2H result is seen, freeze a fresh paired-seed promotion panel against CR071M and relevant current-lineage anchors. Require material direct improvement plus guardrail preservation and zero execution failures.

## Stage 5 — hosted probe decision

Only if the fresh frozen CR081 promotion gate passes:

1. identify which of the two active submissions is rational to retire;
2. package/hash the exact tested candidate;
3. submit exactly once;
4. collect hosted episodes through authenticated API;
5. compare current-meta W/L and rating trajectory against incumbents without reacting to tiny early samples.

If CR081 fails the fresh gate, close it and advance to the predeclared state-adaptive macro-economic architecture rather than threshold-tuning the failed bridge.

## Stop / escalation criteria

- Never reopen PRESALE1 microvariants, CR078, CR079 simple 1-NN, or CR080 route stitching without genuinely new evidence that invalidates their failure reason.
- A current-frontier candidate that cannot generalize chronologically or survive fresh paired seeds is closed even if its source agent has a high Kaggle rating.
- If two architecture families in succession fail for the same mechanical reason, stop building derivatives and redesign the representation/runtime around that failure mode.
- If a candidate passes a frozen fresh gate with material uplift, do not keep it local indefinitely for optional tests; move to one controlled hosted probe.
