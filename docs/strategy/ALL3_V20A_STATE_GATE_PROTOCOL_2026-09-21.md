# ALL3 V20A State-Conditioned Consensus Gate Discovery Protocol — 2026-09-21

## Status

Frozen after V19C closed unconditional O-TM1 and before any V20 discovery outcomes.

## Hypothesis

The frozen V19A P2 consensus schedule has real W/L headroom in some environmental regimes and harmful effects in others.

V20 does **not** change the schedule.

It learns one identity-free binary gate at turn 464:
- gate OFF -> exact ALL3 for the episode;
- gate ON -> apply the unchanged frozen O-TM1 schedule during P2.

The gate is decided once at turn 464 and remains fixed through P2.

## Strict separation from V19C

V19C seeds 78601..78604 are descriptive nomination evidence only.

They are **not used** to fit, threshold, select, or validate the V20 gate.

## Frozen discovery population

Sources:
the same 10 exact source SHAs from the current hard-source set.

Discovery seeds:
- 78711
- 78712
- 78713
- 78714
- 78715
- 78716

Both seats.

Expected:
- 10 sources × 6 seeds × 2 seats = **120 paired contexts**;
- each context runs BASE exact ALL3 and TREATMENT unconditional frozen O-TM1.

Training seeds:
- 78711..78714 = 80 contexts.

Internal holdout seeds:
- 78715..78716 = 40 contexts.

No seed migration after outcomes.

## Frozen legal gate snapshot

At turns 463 and 464, before any O-TM1 market replacement:

1. compute exact ALL3;
2. derive the existing legal V18B numeric state/action features;
3. exclude constant turn/progress fields from prediction;
4. create:
   - `cur__feature` from turn 464;
   - `prev__feature` from turn 463;
   - `delta__feature = cur-prev`;
   - `absdelta__feature`.

No source/ref/rank/context/seed/seat/outcome/reward/future-state feature.

The actual numeric seed is provenance only and never enters the feature vector.

BASE and unconditional-treatment snapshots must be exactly identical in every pair.

## Label

For each discovery context:
- positive label = unconditional O-TM1 `score_delta > 0`;
- negative label = `score_delta <= 0`.

Thus neutral contexts are conservatively treated as non-benefit during gate training.

Margins are never used as a training label.

## Trainability gate

Before fitting:
- training positives >=8;
- training non-positives >=8;
- positive labels occur in >=2 training seeds;
- non-positive labels occur in >=2 training seeds.

If not:
`V20A_GATE_NOT_TRAINABLE`.

## Frozen classifier

One `DecisionTreeClassifier`:
- max_depth = 3;
- min_samples_leaf = 8;
- class_weight = "balanced";
- random_state = 20260921;
- no hyperparameter search.

Runtime activation:
- obtain leaf probability `P(benefit)`;
- gate ON iff **P(benefit) >= 0.80**.

Threshold 0.80 is frozen before discovery outcomes.

Export to pure JSON.
JSON prediction/probability must exactly match sklearn on all 120 discovery contexts.

## Internal holdout gate

Evaluate the frozen gate only on seeds 78715/78716.

Define gated-policy delta:
- if gate ON: use the paired unconditional O-TM1 delta;
- if gate OFF: delta = 0 (BASE retained).

READY requires:
- activated holdout contexts >=4;
- activated positive-score contexts >=2;
- activated positive-score source SHAs >=2;
- activated negative-score contexts =0;
- BASE-win -> treatment-nonwin among activated =0;
- mean gated score delta across all 40 holdout contexts >0;
- mean gated margin delta across all 40 holdout contexts >=0;
- JSON parity PASS;
- no prohibited feature.

Decision:
- `V20A_STATE_GATE_READY`;
- `V20A_STATE_GATE_NOT_READY`;
- `V20A_MECHANICS_INVALID`.

## Untouched validation if READY

Only V20A_STATE_GATE_READY activates V20B.

V20B seeds:
- 78801
- 78802
- 78803
- 78804

Same 10 exact source SHAs; both seats; 80 paired contexts.

V20B candidate uses the exported gate + unchanged frozen V19A schedule.

No Kaggle submission is authorized by V20A.
