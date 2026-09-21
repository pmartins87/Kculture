# ALL3 V18B P2 Cumulative Market Controller — Binding Result — 2026-09-20

Binding trainer-recovery workflow: **`35552606264`**.

Decision: **`V18B_CONTROLLER_NOT_DISTILLABLE`**.

## Dataset

The four dataset shards from workflow `35552335995` were mechanically valid:

- 24 hard contexts;
- P2 turns 464..591;
- 128 rows/context;
- **3072 total decision rows**;
- 10 unique source SHAs;
- zero replay/source failures.

The first trainer attempt failed before fitting because a metadata-name guard incorrectly treated legitimate game features such as `seed_WHEAT` and `BUY_SEED_WHEAT` as prohibited episode-seed metadata.

Workflow `35552606264` reused the already-passed dataset artifacts and corrected only that name guard.

## Distillation result

Actionable recurrent SELL families considered: **19**.

Retained under the frozen leave-one-source-out gate: **0**.

Therefore:
- retained kinds: none;
- JSON parity: PASS for the infrastructure;
- compiler structural validation: PASS;
- no causal V18C is activated.

Best near-miss OOF families:

1. `W3|QTY|SELL|FERTILIZER|1||INC`
   - positive rows 96;
   - positive sources 10;
   - precision 0.56098;
   - recall 0.95833;
   - F1 0.70769.

2. `W3|PRESENCE|SELL|FERTILIZER||ADD`
   - positive rows 96;
   - positive sources 10;
   - precision 0.56098;
   - recall 0.95833;
   - F1 0.70769.

3. `W2|QTY|SELL|STRAWBERRY|5+||INC`
   - positive rows 40;
   - positive sources 7;
   - precision 0.54054;
   - recall 1.0;
   - F1 0.70175.

The characteristic failure is high recall with low precision: shallow current-state trees identify broad state regions but not the precise sparse action pulses.

## Binding interpretation

Do not lower V18B precision/recall/F1 thresholds and do not increase tree depth post-hoc.

The P2 dataset instead shows strong cross-source **turn-program consensus**: many turns share exactly the same teacher market across 8–10 unique source SHAs.

The next architecture is therefore not a relaxed tree. It is a source-balanced, identity-free **temporal consensus market schedule** distilled from the same P2 dataset.

No Kaggle submission.
