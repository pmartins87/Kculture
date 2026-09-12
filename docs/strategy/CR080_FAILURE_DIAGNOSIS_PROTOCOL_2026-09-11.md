# CR080 failure diagnosis — frozen protocol

Frozen after CR080 independent confirmation run `34655496708` failed its predeclared gate and before inspecting any post-failure telemetry.

## Confirmed failure

CR080 is closed as a candidate. The independent confirmation used 32 fresh paired seeds / 64 games per H2H in the exact `kaggle-environments==1.32.7` runtime.

- CR080 vs CR071M: 33-31, score 0.515625; required >=0.5625.
- CR080 vs CR053: 34-30, score 0.53125 versus CR071M 0.59375; delta -0.0625.
- CR080 vs CR061: 33-31, score 0.515625 versus CR071M 1.00000; delta -0.484375.
- CR080 vs CR065: 39-25, score 0.609375 versus CR071M 0.890625; delta -0.28125.
- Zero errors/non-DONE. The gate decision is `CLOSE_CR080_NO_RETUNING`.

No CR080A/B/C rescue, selector-weight retuning, route-bank pruning or threshold change is permitted on these seeds.

## Purpose of the diagnostic

The already-used confirmation seeds may now be reused only to explain the failure mechanism and choose a materially different architecture. They are not validation data for a repaired CR080.

The frozen diagnostic replays the exact frozen CR080 package against CR071M, CR061 and CR065 and measures, without changing actions:

1. day-start route-match quality (farm structure, shops and economy);
2. end-of-day drift from the route selected at the prior day boundary;
3. hand-count shortfall/excess relative to the selected source route;
4. source hand actions omitted because the live game has fewer workers than the route expects;
5. position mismatches and productive source actions replaced by movement repair;
6. weed repair candidates;
7. route switching / number of unique source trajectories used;
8. market-action parity with the frozen source route.

Win/loss splits and day-level profiles are descriptive diagnostics only.

## Pre-result hypotheses

H1 — **labor-plan drift:** a source route's HIRE sequence does not reproduce the expected hand count in closed loop, causing source hand actions to be omitted later in the same day.

H2 — **position-repair cascade:** current worker positions diverge from the selected source trajectory, replacing productive actions with corrective movement often enough to destroy the replay economics.

H3 — **route stitching drift:** day-boundary selection repeatedly jumps between source trajectories whose physical state is locally compatible but whose accumulated economy/inventory path is not, causing end-of-day drift and unstable production.

H4 — if H1-H3 are weak or similar in wins and losses, the failure is strategic rather than mechanical: Mengfei's historical route family itself is no longer a robust current-meta bridge.

## Decision use

- Strong H1/H2/H3 evidence closes the *route-replay follower architecture* as currently represented; the next candidate must model labor/production state directly rather than patch CR080 on these seeds.
- Weak H1/H2/H3 evidence closes the Mengfei bridge on strategic grounds and sends research back to current hosted/top-agent state-adaptive mechanisms.
- In neither branch is a CR080 retune allowed.

Original final held-out seeds remain sealed. No Kaggle submission is part of this diagnostic.
