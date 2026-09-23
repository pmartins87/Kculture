# V29A — Recurrent Structural Teacher Distillation Result — 2026-09-23

## Binding result

**Decision:** `V29A_RECURRENT_STRUCTURAL_DISTILLATION_FAIL`

Binding workflow: `35876362346`  
Head SHA: `ec9535d8a03d97f0e7e67b1bba4831ebdf72a174`

## Mechanical validation

PASS. Workflow completed successfully and uploaded artifact `v29a-recurrent-structural-distillation`.

The run used only the immutable V27C2 artifacts from workflow `35682535729`, preserved the frozen V27C2 split, used the 114 legal recurrent features, one-layer GRU hidden size 64, structural UNIT and 10-slot MARKET decoders, AdamW lr 1e-3 / weight_decay 1e-4, gradient clip 1.0, exactly 8 epochs and seed 20260923. Kaggle credentials were explicitly unset during training/evaluation. No runtime identity/source/rank/SHA feature and no teacher call at inference were used.

Training loss decreased monotonically from 5.500810 at epoch 1 to 1.527170 at the frozen epoch 8; this does not override the frozen holdout gates.

## Frozen holdout result

- episodes: 48
- turns: 34,512
- complete-action parity: **0.0712795549**
- minimum source complete-action parity: **0.0702364395**
- minimum 120-turn-stage complete-action parity: **0.0034722222**
- farmer parity: **0.7450741771**
- hands parity: **0.1500927214**
- market parity: **0.3729717200**
- market-slot accuracy: **0.9000811312**
- unit-sample accuracy: **0.6661316014**
- unseen market-slot truth labels: **66**
- unseen unit truth labels: **0**
- strong_pass: **false**
- causal_eligible: **false**

Complete-action parity by 120-turn stage was 0.28785, 0.05000, 0.05556, 0.01771, 0.00347 and 0.01261 for stages 0..5. The recurrent structural model therefore fails especially badly on whole-action reconstruction and late-episode behavior despite high individual market-slot accuracy.

## Binding interpretation

The frozen recurrent structural teacher-distillation route does **not** meet either the strong-pass or causal-eligibility gate. Per preregistration, do not launch V29B and do not tune hidden size, epoch count, learning rate, loss weights, holdout split or architecture against this outcome. Close this V29A teacher-distillation family.

The protected hosted Kaggle pair remains exactly exact V47 submission `56466970` plus ALL3 submission `56367770`. No Kaggle submission, deletion or reordering is authorized or performed.
