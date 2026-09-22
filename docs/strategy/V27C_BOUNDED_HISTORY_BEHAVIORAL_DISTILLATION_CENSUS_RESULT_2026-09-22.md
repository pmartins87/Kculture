# V27C Bounded-History Behavioral Distillation Census — Result — 2026-09-22

## Binding result

Workflow: **`35725924827`**  
Final artifact: `10693458739`  
Digest: `sha256:9749f31649e7a6b41a192220f0c90580b4df63e71b3c0b22f0b1e032c5da9799`

Mechanical:
- 12/12 shards PASS;
- 96/96 teacher trajectories;
- **69,024** labeled turns;
- failures 0;
- immutable V26A snapshot only;
- frozen history window H=256;
- frozen 1254-dimensional legal representation.

Decision:

**`V27C_BEHAVIORAL_DISTILLATION_DATA_TOO_COMPLEX`**

## What worked

The representation is deterministic when an exact feature vector repeats:
- complete-action duplicate-feature conflict rate: **0.0**;
- MARKET conflict rate: **0.0**;
- FARMER conflict rate: **0.0**;
- HANDS conflict rate: **0.0**;
- exact feature matches from train to validation/test have **100% label agreement**.

Thus the problem is not contradictory labels for the same legal state/history representation.

## Why the fast clone gate failed

The policy has very large cross-seed/action support:

- unique complete actions: **2597**;
- unique MARKET labels: **887**;
- unique FARMER labels: **50**;
- unique HANDS labels: **1839**.

Training saw:
- 1826 complete labels;
- 627 MARKET labels;
- 49 FARMER labels;
- 1479 HANDS labels.

Untouched test contains:
- 481 complete labels unseen in training;
- 145 MARKET labels unseen in training;
- 1 FARMER label unseen in training;
- 266 HANDS labels unseen in training.

Component-decomposable coverage:
- validation: **0.6358368104**;
- test: **0.6021094112**;
- frozen requirement: >=0.98.

Step-modal complete-action test accuracy:
- **0.3561659713**;
- frozen compactness floor: >=0.70.

Other step-modal test accuracies:
- MARKET: 0.5085767269;
- FARMER: 0.6787204451;
- HANDS: 0.4282568382.

Only about **10.01%** of validation/test rows exactly match a training feature vector, although those matches are perfectly deterministic.

## Interpretation

The rank-1 teacher is legally reconstructible from a 256-observation history, but its action space is too combinatorial and cross-seed generalization too sparse for the pre-registered fast component-wise tree clone.

This is a different failure from V27A/V27B:
- V27A: state-only representation insufficient;
- V27B: bounded legal history solves teacher hidden-state reconstruction;
- V27C: the resulting behavior still has too many novel structured actions to distill safely with the fast fixed model family before the competition deadline.

Per the frozen protocol:
- do not activate V27D;
- do not tune history features;
- do not change model family post-hoc;
- close fast rank-1 behavioral distillation;
- move to final-slot / competition strategy.

No Kaggle submission is authorized.
