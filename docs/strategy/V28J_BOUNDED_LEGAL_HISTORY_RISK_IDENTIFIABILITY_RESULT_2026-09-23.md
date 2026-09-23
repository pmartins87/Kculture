# V28J — Bounded Legal-History Risk Identifiability — Binding Result

Date: 2026-09-23

Binding workflow: `35822283032`.

## Decision

**`V28J_BOUNDED_LEGAL_HISTORY_RISK_PHENOTYPE_NOT_IDENTIFIABLE`**

Mechanical PASS.

The frozen V28J design was respected: all 144 V28F ALL3 contexts, exact V28I source-held-out split, checkpoints 384/416/448/480, 798 runtime-legal raw+adjacent-delta columns, deterministic decision tree with max_depth=3, min_samples_leaf=8, class_weight=balanced and random_state=20260922. Opponent/source identity was not a runtime feature.

## Binding holdout metrics

- n: 48
- precision: 0.5882352941
- recall: 1.0
- specificity: 0.5
- balanced accuracy: 0.75
- positive prediction rate: 0.7083333333
- confusion matrix: [[14,14],[0,20]]

Train metrics were precision 0.9583333333, recall 1.0, specificity 0.96 and balanced accuracy 0.98. The large train/held-out gap confirms that the simple legal-history classifier does not generalize sufficiently across held-out sources.

The fitted tree had depth 2 and 3 leaves, using only:
- `s416:market_inventory:FERTILIZER`;
- `s480:opp_tiles_kind:PASTURE`.

## Interpretation and frozen routing

Adding bounded legal history did not rescue the deployable phenotype. Precision and specificity are worse than V28I and fail the frozen acceptance gate. No retuning, threshold search, model-family expansion, or source-conditioned runtime rule is authorized from this result.

Therefore simple classifier-based risk gating on the 384–480 window is **closed**. Subsequent work routes to direct matched hard-vs-control mechanism/action discovery, while source/rank/SHA remain offline forensic metadata only.

No Kaggle mutation was performed or authorized. Hosted pair remains exact V47 `56466970` + ALL3 `56367770`.