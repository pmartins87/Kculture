# V28I — Legal-State Residual-Risk Identifiability Result — 2026-09-23

## Binding run

Workflow: `35818084144`.

Decision: **`V28I_LEGAL_STATE_RISK_PHENOTYPE_NOT_IDENTIFIABLE`**.

Mechanical status: **PASS**.

## Frozen-contract validation

The run used the immutable V28F snapshot and binding V28F/V28G/V28H artifacts. It replayed all 144 V28F ALL3 contexts, required exact terminal score+margin parity, extracted exactly the 114 legal `solver.programme_features` at the V28H-selected checkpoint **480**, used the frozen source-held-out 8-source train / 4-source holdout split, and fit exactly the pre-registered deterministic depth-3 decision tree (`min_samples_leaf=8`, balanced class weight, `random_state=20260922`). Opponent identity/source/rank/SHA was retained only as offline audit metadata and did not enter the feature matrix.

Binding prevalence reproduced exactly: **66 residual-loss positives / 144 contexts**.

## Metrics

Train:
- balanced accuracy: **0.9582608696**;
- precision: **0.9565217391**;
- recall: **0.9565217391**;
- specificity: **0.9600000000**;
- confusion matrix: `[[48,2],[2,44]]`.

Source-held-out:
- balanced accuracy: **0.7857142857**;
- precision: **0.6250000000**;
- recall: **1.0000000000**;
- specificity: **0.5714285714**;
- positive prediction rate: **0.6666666667**;
- confusion matrix: `[[16,12],[0,20]]`;
- n: **48**.

Tree:
- depth: **3**;
- leaves: **4**;
- used legal features: `opp_money`, `market_inventory:FERTILIZER`, `opp_consecutive_need`.

## Gate interpretation

The frozen gate fails because holdout precision **0.625 < 0.70** and specificity **0.5714** is too weak, despite perfect holdout recall and balanced accuracy above 0.75. The legal state at a single checkpoint therefore over-flags easy contexts and is not a sufficiently transferable phenotype.

No threshold, split, depth, feature set, or model family is retuned after observing this result.

## Binding route

Per the pre-registered V28I protocol, single-state phenotype discovery is closed. The next gate is a **bounded legal-history/stateful phenotype** test using the V28H explanatory window. It must remain source-held-out, runtime-legal, and source-identity-free.

Current hosted pair remains unchanged: exact V47 `56466970` + ALL3 `56367770`. No Kaggle submission, deletion, or reordering is authorized.