# ALL3 V18B P2 Cumulative Market Controller — Binding Result — 2026-09-21

Binding recovery workflow: **`35552606264`**.

Initial workflow `35552335995` produced a non-binding mechanical feature-name guard failure before training because the validator incorrectly treated legitimate game features such as `seed_WHEAT` and `BUY_SEED_WHEAT` as forbidden episode-seed metadata. The recovery reused the four already-PASS dataset shards and changed only that metadata-name guard.

Decision:
**`V18B_CONTROLLER_NOT_DISTILLABLE`**.

## Dataset / mechanics

- exact P2 scope: turns 464..591;
- 24 hard contexts;
- 10 source SHAs;
- exactly **3072** rows;
- zero replay/source failures;
- 19 actionable recurrent SELL residual families;
- prohibited predictive metadata features: none after corrected guard;
- JSON/sklearn parity: PASS;
- compiler structural validity: PASS.

## Generalization result

Retained families: **0 / 19**.

No family simultaneously passed the frozen leave-one-source-out gates:
- positive examples span >=4 source SHAs;
- precision >=0.80;
- recall >=0.70;
- F1 >=0.75.

Best families were high-recall but low-precision:
- W3 PRESENCE SELL FERTILIZER ADD: precision 0.5610, recall 0.9583, F1 0.7077;
- W3 QTY SELL FERTILIZER +1: same metrics;
- W2 QTY SELL STRAWBERRY 5+: precision 0.5405, recall 1.0, F1 0.7018;
- W3 QTY SELL STRAWBERRY +2: precision 0.4667, recall 1.0, F1 0.6364.

## Temporal diagnosis

Offline diagnostic on the already-frozen 3072-row dataset found that the eligible residual labels are predominantly event-like pulses rather than persistent regimes.

Examples:
- W2 STRAWBERRY 5+ INC: 40/40 positive rows are singleton 1-turn runs;
- W2 EGG +2 INC: 40/40 singleton;
- W2 MILK -1 DEC: 16/16 singleton;
- W3 STRAWBERRY +2 INC: 28/28 singleton;
- W2 STRAWBERRY +2 INC: 42 runs over 48 rows, mostly singleton.

All examined positive rows occur on a turn where the exact ALL3 market changed relative to the previous turn, and their legal-state numeric feature vectors also changed.

Binding interpretation:
V18B failed as a **state classifier**, not because the labels lack reproducible temporal structure. The next test may change the representation from persistent-state classification to transition/event classification, but may not relax the precision/recall/F1 gates or use outcomes.

No causal game was run.
No Kaggle submission.
