# CR083 Phase 1 — causal market-family ablation protocol

Status: **pre-registered architecture research**, frozen before any Phase-1 score is observed.

This study activates after the valid CR082 failure and follows the CR083 explicit-value architecture boundary. It is **not** a promotion gate and cannot authorize a hosted submission.

## Question

For the existing CR071M physical/runtime backbone, which market-action families causally contribute to final money / H2H strength, and which are expendable or harmful?

The study deliberately avoids teacher imitation. Every variant is derived from CR071M itself and differs by removing exactly one economic action family from the already-produced final market queue.

## Frozen variants

Baseline: exact CR071M package from the frozen CR080/CR082 anchor corpus.

Six ablations:

- `CR083_NO_SELL`: remove all `SELL` orders;
- `CR083_NO_BUY_SEED`: remove all `BUY_SEED` orders;
- `CR083_NO_BUY_PRODUCT`: remove all `BUY_PRODUCT` orders;
- `CR083_NO_BUY_ANIMAL`: remove all `BUY_ANIMAL` orders;
- `CR083_NO_HIRE`: remove all `HIRE` orders;
- `CR083_NO_BUY_LAND`: remove all `BUY_LAND` orders.

Nothing else may change. Farmer/hands, route switching, weed repair, room guard, CR053 counter logic, sell clamping, dead-stock logic and every non-ablated market order remain byte-for-byte behaviorally inherited from CR071M.

The filter is applied **after** CR071M has constructed its final market queue. This makes each variant a clean causal deletion rather than a rewritten strategy.

## Exact evaluation

Runtime: `kaggle-environments==1.32.7`, isolated package processes, both seats.

Exploratory master seed: **9130830**.

Use 8 fresh seeds × both seats = 16 games for each direct matchup:

- each ablation vs exact CR071M.

The seed firewall must verify zero overlap with all registered CR080, CR081 and CR082 masters, including `9120821`.

No result from master `9130830` may later serve as a CR083 promotion gate. It is architecture-forming evidence only.

## Readout

For each ablation record:

- W/L/tie and seat-balanced score rate;
- mean/median/min/max final-money margin;
- execution errors / non-DONE games.

Interpretation is directional, not a thresholded PASS/FAIL:

- large negative ablation effect => family is essential/value-creating for this backbone;
- near-zero effect => family is a candidate for simplification or state-conditional suppression;
- positive ablation effect => family is a high-priority target for explicit-value replacement.

Do **not** tune quantities or timing on these seeds.

## Next step after Phase 1

Use the causal ranking to choose the narrowest high-value mechanism for CR083 Phase 2. Phase 2 must then pre-register an explicit mechanics-derived value representation and fresh Gate A before any executable CR083 candidate is evaluated.

Original final holdout remains sealed. No Kaggle hosted submission is allowed from this study.