# ALL3 V21D Semantic Candidate Hosted Submission Protocol — 2026-09-21

## Status

DORMANT / PRE-REGISTERED BEFORE V21A OUTCOMES.

Activate only if:
- V21A = `V21A_SEMANTIC_WL_HEADROOM`;
- V21B = `V21B_SEMANTIC_FRESH_PASS`;
- V21C = `V21C_PACKAGE_PARITY_PASS`.

## Submission identity

Submit exactly the V21C binding archive:
`KCULTURE_V47_ALL3_SM1_V1.tar.gz`.

The archive SHA256 must equal the V21C receipt.

No rebuild, repack, source edit, threshold edit, schedule edit, category edit or mode edit after V21C.

## Hosted action

Exactly one hosted Kaggle submission.

Frozen description prefix:
`PS_ALL3_SM1_V1_`

Append only the exact V21A selected mode and the first eight characters of the binding archive SHA.

## Operational constraints

Before submit:
- confirm competition submission window is open;
- confirm daily submission cap leaves >=1 slot;
- confirm package receipt and selected mode;
- confirm no newer unvalidated candidate is substituted.

After submit:
- record submission id, timestamp, archive SHA, candidate SHA, selected mode and observed hosted rating/result;
- do not mutate V21D based on the first hosted observation;
- retain ALL3 control and prior hosted baselines for comparison.

## Decision

Hosted observation is evidence, not a license for post-hoc tuning.

A materially poor hosted result closes this exact candidate unless a separately pre-registered replication gate exists.

No second submission is authorized by this protocol.
