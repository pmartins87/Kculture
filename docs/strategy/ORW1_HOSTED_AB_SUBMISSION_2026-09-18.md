# O-RW1 Hosted A/B Submission — 2026-09-18

## Frozen pair submitted

Authorized A/B protocol:
`docs/strategy/ORW1_HOSTED_AB_PROBE_PROTOCOL_2026-09-18.md`.

Workflow:
`35361531672`.

### CONTROL

- submission ID: **56333577**
- file: `CONTROL_EXACT_V47.tar.gz`
- registered at: `2026-09-18 15:18:48.850000 UTC`
- description: `PS_ORW1_CONTROL_EXACT_V47_08E56C43`
- exact archive SHA-256:
  `08e56c43ecf28253605b61066dd769334d96262056b8cd337489f1f4f909ad01`
- content: exact public V47 output archive, no rebuild/edit.

### TREATMENT

- submission ID: **56333579**
- file: `TREATMENT_V47_ORW1.tar.gz`
- registered at: `2026-09-18 15:18:50.740000 UTC`
- description: `PS_ORW1_TREATMENT_V47_ORW1_B994E00D`
- exact archive SHA-256:
  `b994e00d7adba05827eb8839b806211c2c8199dd0ad09a28b63815b58479c80f`
- content: exact frozen V47 + O-RW1 one-shot package.

Registration separation was approximately **1.89 seconds**.

## Preflight

Authenticated Kaggle preflight passed:
- competition entry verified;
- no duplicate descriptions;
- submissions already observed on 2026-09-18 UTC before pair: **0**;
- projected after pair: **2 / 5**;
- both exact archive hashes verified;
- both official entrypoint loader smokes passed.

## First authenticated status checkpoint

Snapshot workflow:
`35361737759`.

Snapshot time:
`2026-09-18 15:19:54 UTC`.

- CONTROL 56333577: `SubmissionStatus.PENDING`
- TREATMENT 56333579: `SubmissionStatus.PENDING`

No score/rating existed at this checkpoint. Do not interpret the pair until both hosted
evaluations have left PENDING and exposed comparable result fields.

## Decision state

`ORW1_HOSTED_AB_SUBMITTED_AWAIT_BOTH_RESULTS`

Do not submit another O-RW1 variant between these arms. Do not tune O-RW1 from partial
or one-arm results.
