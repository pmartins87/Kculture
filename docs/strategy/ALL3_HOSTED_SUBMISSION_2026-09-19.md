# ALL3 Hosted Submission — 2026-09-19

## Submission

Workflow: **`35459415491`**  
Artifact: `10589287442`  
Artifact digest: `sha256:6c755514d6426801616538c73ecedc55b6776aff1d630628013da31566db8240`.

Frozen candidate:
- file: `ALL3_V47_RW1_TW1_LQ2.tar.gz`;
- package source: `KCULTURE_V47_ALL3_V1.tar.gz`;
- SHA-256: **`204a9ed49579b8255343d6014e815d2512d2f37edea142eba082203e101ff7f8`**;
- hosted entrypoint: **`_kc_all3_entrypoint`**;
- description: `PS_ALL3_V1_RW1_TW1_LQ2_204A9ED4`.

Kaggle submission:
- **ID: `56367770`**;
- registered UTC: **2026-09-19 17:53:18.930000**;
- initial registration status: **PENDING**.

Preflight:
- authenticated Kaggle access PASS;
- exact tar SHA PASS;
- official loader PASS;
- current CONTROL/O-RW1 pair present;
- duplicate description absent;
- observed submissions today before ALL3: **0**;
- projected daily count after ALL3: **1/5**.

Retained mature treatment before submission:
- O-RW1 `56336027`;
- rating at preflight: **2383.9**.

Prior mature control before submission:
- V47 CONTROL `56336025`;
- rating at preflight: **2344.6**.

## Slot rationale

Readiness audit:
`docs/strategy/ALL3_HOSTED_READINESS_AUDIT_2026-09-19.md`.

Decision:
**`ALL3_HOSTED_READINESS_PASS_REPLACE_CONTROL`**.

The intended active pair is:
1. O-RW1 `56336027`;
2. ALL3 `56367770`.

No nearby variant is authorized.

## Initial hosted execution checkpoint

Workflow `35459613689` at 2026-09-19 17:56 UTC:

- ALL3 `56367770`: **SubmissionStatus.COMPLETE**;
- initial public rating: **600.0**;
- O-RW1 `56336027`: **COMPLETE**, rating **2383.9**;
- no hosted runtime error was observed.

This closes the hosted mechanics gate.

The 600.0 ALL3 rating is the initial field immediately after activation and is **not** a competitive
maturity estimate.

## Next checkpoint

Preserve O-RW1 + ALL3 and allow ALL3 to accumulate public exposure.

First informative threshold remains a substantial external-game sample (historically 32 resolved
external games for this project). Do not replace or reroll ALL3 based on the initial 600.0 field.
