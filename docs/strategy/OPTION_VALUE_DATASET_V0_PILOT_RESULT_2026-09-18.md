# Option-Value Dataset V0 Pilot Result — 2026-09-18

Workflow `35401131591`.

Binding verdict:
**`OPTION_VALUE_DATASET_V0_PILOT_PASS`**.

## Mechanical/data-contract result

- 24 labeled counterfactual rows;
- 12 O-RW1 rows;
- 12 O-TW1 rows;
- 0 failures;
- discovery/base replay parity: PASS;
- feature contract: PASS;
- all model features finite;
- seed/opponent/rating/hidden/future metadata excluded from model-facing features.

Pilot label summary:

O-RW1:
- mean score delta **+0.1666667**;
- 4 positive, 0 negative, 8 neutral;
- mean margin delta **+5.6667**.

O-TW1:
- mean score delta **+0.1666667**;
- 4 positive, 0 negative, 8 neutral;
- mean margin delta **+29.0**.

These pilot values are data-pipeline diagnostics, not new promotion evidence; the
independent frozen causal/runtime gates remain the binding option-strength evidence.

## Consequence

The project is now allowed to scale the same state-option-value schema on the Ryzen.

Production generator:
`tools/option_value_dataset_ryzen_v1.py`

Resumable runner:
`tools/run_option_value_v1_ryzen.sh`

The first production batch must remain offline. No Kaggle submission is authorized by
this dataset work.
