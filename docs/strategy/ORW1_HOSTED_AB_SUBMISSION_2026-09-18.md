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

## Subsequent authenticated status checkpoints

- `2026-09-18 15:22:16 UTC`: CONTROL `PENDING`; TREATMENT `COMPLETE`, rating field `600.0`.
- `2026-09-18 15:23:11 UTC`: CONTROL `PENDING`; TREATMENT `COMPLETE`, rating field `600.0`.

This asymmetric processing state is **not interpretable as an A/B result**. The protocol remains frozen: do not compare ratings until CONTROL has also left PENDING. The treatment's initial `600.0` field is recorded only as API state, not as a competitive verdict.

## Mechanical invalidation

Subsequent hosted-loader and replay audit invalidated the TREATMENT arm.

Official loader names from the actual submission workflow:
- CONTROL: `_y_agent_shopherd` — correct exact V47 hosted entrypoint.
- TREATMENT: `_kc_orw1_wool` — helper function, **not** the intended O-RW1 wrapper.

Replay `110482337` confirms the treatment side emitted PASS-only actions from step 0
through the end and finished at reward 3000. Replay `110481069` was a same-team
PASS-only 3000-3000 game.

The later rating checkpoint CONTROL `714.8` vs TREATMENT `503.9` is therefore
**not an O-RW1 A/B result**.

Binding state:
`ORW1_HOSTED_AB_INVALID_ENTRYPOINT_DO_NOT_INTERPRET`.

See:
`docs/strategy/HOSTED_ENTRYPOINT_PARITY_CORRECTION_2026-09-18.md`.
