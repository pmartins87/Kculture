# CR080 failure diagnosis — frozen protocol + result

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

## Result — run `34668446703`

All three 64-game diagnostic panels completed successfully. Across CR071M, CR061 and CR065:

- mean hand shortfall worker-steps = **0.0**;
- mean omitted reference-hand actions = **0.0**;
- mean position-mismatch worker-steps = **0.0**;
- mean market-action mismatch steps = **0.0**;
- actual worker-action mutations were negligible (~0.11–0.14 per game, almost entirely weed repair).

Therefore H1 and H2 are falsified as material causes. The runtime is reproducing the selected source route mechanically; the confirmation failure is not explained by missing hands or movement-repair cascades.

The consistent separation is economic-state mismatch. In all three panels losses begin a day farther from the selected route's economic state and finish farther from it than wins:

| Opponent | selection economy L1, wins | selection economy L1, losses | end-drift economy L1, wins | end-drift economy L1, losses |
|---|---:|---:|---:|---:|
| CR071M | 1.744 | 3.489 | 1.817 | 3.601 |
| CR061 | 2.375 | 3.887 | 2.472 | 4.023 |
| CR065 | 1.989 | 3.495 | 2.071 | 3.592 |

The effect grows particularly in the mid/late game. Against CR071M, for example, loss-side selected economy L1 rises from roughly 1.3 around day 13 to ~3.9 on day 15 and >5 by days 17–18, while wins remain materially closer for most of that interval.

Route switching itself is common in both wins and losses (roughly 5.5–7 switches/game), so switch count alone is not the explanation. The important failure is **state aliasing**: the selector finds a trajectory that looks locally compatible in public/physical features, but the accumulated economic path is not causally interchangeable with that source trajectory. Following it for the next day can therefore preserve visible mechanics while producing a different economic state. Repeating this process compounds the mismatch.

## Decision

**H3 is supported; H1 and H2 are rejected. H4 may also contribute, but is not needed to close the architecture.**

The route-replay follower / daily nearest-route stitching architecture is closed. We will not repair CR080 by changing selector weights, adding more Mengfei routes or lowering thresholds on the same evidence. The next architecture must transfer current-meta mechanisms at the semantic/state level — especially market/economic decisions — rather than treat whole replay trajectories as interchangeable continuations.

This directly motivates CR081's current-3056-lineage market/economy bridge. CR081 may preserve a physical backbone where independently supported, but it must not perform nearest-replay route stitching.

Original final held-out seeds remain sealed. No Kaggle submission was made from this diagnostic.
