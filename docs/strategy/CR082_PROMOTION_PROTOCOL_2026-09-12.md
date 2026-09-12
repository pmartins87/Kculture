# CR082 — conditional promotion protocol

Frozen **before** the strict-forward CR082 Gate A result and before any executable CR082 package exists.

This protocol activates only if `CR082 Majkel fresh Gate A v2 strict forward` passes. If Gate A fails, no CR082 executable is built and this H2H protocol is unused.

## Candidate architecture if Gate A passes

Exactly one CR082 implementation is permitted:

- exact CR071M physical/runtime backbone, same-step and unchanged;
- market policy active only on runtime steps 0–287;
- teacher corpus fixed to the **oldest 48 episodes (75%) of the original 64 Majkel corpus** collected in run `34669006417`;
- at each runtime step `t`, compare the legal current state only against teacher examples from the same runtime step `t`;
- frozen features exactly as in the CR082 protocol: day/hour; own money; hand count; hires_today; unlocked-quadrant count; own shed products/animals; own seeds; public market prices; public market inventory;
- per-step standardization learned from the frozen teacher development examples only;
- `k=1` exactly;
- per-step OOD threshold = 95th percentile of leave-one-out nearest-neighbor distance among frozen teacher development examples;
- if current state distance <= threshold: copy only the nearest example's current-step market queue;
- otherwise use the teacher-development per-step modal market queue;
- no replay continuation, farmer/hands copying, team identity, EpisodeId, seed, future state or opponent-private feature;
- retain only mechanical capacity/legality repairs (`room_guard`, SELL clamping, and same-turn BUY_PRODUCT->later-SELL accounting);
- inherited `_cr053_counter_market` and `dead_stock` are disabled inside runtime 0–287 and resume with normal CR071M after the prefix.

No feature, k, threshold percentile, teacher set, prefix or market quantity may be changed in response to H2H results.

## Fresh exact H2H panel

Runtime: `kaggle-environments==1.32.7`, isolated package processes, both seats.

Reserved master seed: **9120821**.

Seed firewall must exclude all CR080 masters and CR081 masters `9120811`, `9120812`, `9120813`, plus every previously documented local master used for candidate selection.

Panel:

1. CR082 vs CR071M;
2. CR082 vs CR053;
3. CR082 vs CR061;
4. CR082 vs CR065;
5. CR071M vs CR053;
6. CR071M vs CR061;
7. CR071M vs CR065.

Each matchup: **32 fresh seeds × two seats = 64 games**.

## Frozen promotion gate

All conditions are required:

1. complete seven-matchup panel;
2. exactly 64 games / 32 reserved fresh seeds in every row;
3. zero agent errors and zero non-DONE games;
4. CR082 direct seat-balanced score rate vs CR071M >= **0.5625**;
5. aggregate guardrail delta `sum(score(CR082,g)-score(CR071M,g)) >= 0` for `g in {CR053,CR061,CR065}`;
6. every individual guardrail delta >= **-0.0625**.

Primary metric is seat-balanced W/L score rate. Reward margin is diagnostic only.

## Decision

- **PASS:** freeze exact tested SHA-256, refresh authenticated hosted slot/submission state, then make exactly one controlled Kaggle hosted probe if slot accounting permits. Do not continue optional local tuning first.
- **FAIL:** close CR082 1-NN. No CR082A/B/C, no k tuning, no feature pruning/addition, no p95 adjustment, no prefix change and no teacher-set change on these seeds. Advance to explicit economic-value / macro-selection modeling from legal current game state.

Original final holdout remains sealed. No automatic hosted submission is part of the H2H workflow itself.
