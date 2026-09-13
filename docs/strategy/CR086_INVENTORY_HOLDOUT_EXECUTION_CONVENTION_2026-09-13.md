# CR086 inventory estimator — holdout execution convention

Status: **FROZEN BEFORE HOLDOUT METRICS**

For each of the 10 replay IDs preselected in `CR086_OPPONENT_INVENTORY_ESTIMATOR_FEASIBILITY_2026-09-13.md`, evaluate the frozen v2 estimator twice:

1. seat 0 treated as the controlled player and seat 1 as opponent;
2. seat 1 treated as the controlled player and seat 0 as opponent.

Reason: the runtime estimator must be seat-symmetric and must not require team identity/rank to choose a perspective. Using both seats avoids any outcome-based or team-name-based selection.

Aggregate PASS metrics are computed over all commodity-step observations from all 20 controlled-player trajectories (10 replays x 2 seats) for the seven primary commodities.

No result, team identity, rank, rating, or money outcome is used to choose a seat.
