# ALL3 V19E O-TM1 Hosted Submission Protocol — 2026-09-21

## Status

DORMANT / PRE-REGISTERED BEFORE V19C RESULT.

Exactly one hosted submission is authorized only if both conditions hold:

1. `V19C_CONSENSUS_FRESH_PASS`;
2. `V19D_PACKAGE_PARITY_PASS`.

## Frozen candidate identity

Description:
**`PS_ALL3_TM1_V1_P2_CONSENSUS_C68D8575`**

Candidate package:
`KCULTURE_V47_ALL3_TM1_V1.tar.gz`.

Binding schedule SHA prefix in description:
`c68d8575`.

The exact archive SHA is taken only from the binding V19D PACKAGE_RECEIPT and must match the downloaded package bytes before submission.

## Submission preflight

Before submitting:
- authenticated Kaggle access to `kaggriculture`;
- V19D artifact exists and parity PASS;
- package loader selects `_kc_tm1_entrypoint`;
- package archive SHA matches V19D receipt;
- target description does not already exist;
- daily submission cap after this submission <=5.

## Action

Submit exactly once with:
`kaggle competitions submit -c kaggriculture -f KCULTURE_V47_ALL3_TM1_V1.tar.gz -m PS_ALL3_TM1_V1_P2_CONSENSUS_C68D8575`.

Then confirm registration through authenticated submissions list and record:
- submission id/ref;
- status;
- description;
- package SHA;
- submission timestamp.

## Interpretation

This is an external hosted validation of an already-frozen candidate.

Do not mutate the package after observing the hosted result. Any later change requires a new candidate/version and new offline gates.
