# ALL3 Hosted Readiness / Slot Replacement Audit — 2026-09-19

## Decision

**`ALL3_HOSTED_READINESS_PASS_REPLACE_CONTROL`**

The ALL3 challenger has earned the right to consume one hosted slot.

The slot to be displaced is the older exact-V47 CONTROL submission `56336025`.
The O-RW1 treatment `56336027` is retained.

## Current active pair maturity

Earlier ~100-episode maturity audit:
- CONTROL `56336025`: 103 listed / 102 resolved external;
- O-RW1 `56336027`: 106 listed / 105 resolved external.

Therefore both exceed the project's normal 100-public-episode maturity threshold.

Authenticated current checkpoints:

Checkpoint 1 — workflow `35459274901`:
- CONTROL: **2344.6**;
- O-RW1: **2383.9**.

Checkpoint 2 — workflow `35459326579`:
- CONTROL: **2344.6**;
- O-RW1: **2383.9**.

The successive checkpoints are unchanged. The pair is no longer in the rapid rating-discovery phase.

## Challenger evidence

### Causal evidence

O-LQ2 fresh V48 gate, workflow `35456018489`:
- 16/16 BASE losses -> ALL O-LQ2 wins;
- mean score delta **+1.0**;
- mean margin delta **+567**;
- negative contexts **0**.

### Broad safety

Workflow `35456201059`:
- 56 fresh contexts;
- seven opponent families;
- mean score delta **+0.1607143**;
- negative-score contexts **0**;
- V48 +0.75;
- V47 mirror +0.375;
- five unrelated families W/L-neutral.

### Integrated composition

Workflow `35456535323`:
- decision **TRIPLE_COMBO_SAFE_ADVANCE**;
- ALL3 score rate **0.9464286**;
- BASE **0.7857143**;
- old RW1+TW1 host **0.8392857**;
- ALL3 negative-score contexts vs BASE **0**;
- ALL3 preserves LQ2 W/L and improves aggregate terminal margin.

### Hosted-faithful package

Workflow `35457146455`:
- decision **ALL3_HOSTED_PACKAGE_PARITY_PASS**;
- 12/12 exact action parity;
- 12/12 exact reward parity;
- fresh seeds;
- V47 mirror, V48 and Tactical Memory;
- both seats;
- official Kaggle last-callable loader;
- candidate entrypoint `_kc_all3_entrypoint`.

Frozen package:
- `KCULTURE_V47_ALL3_V1.tar.gz`;
- SHA-256 **`204a9ed49579b8255343d6014e815d2512d2f37edea142eba082203e101ff7f8`**;
- candidate main SHA-256 `92cffec54646e04e4e019bbc623564705038264b8ce7719b589095c1804d3e2f`.

## Slot choice

Current live rating:
- CONTROL 2344.6;
- O-RW1 2383.9.

ALL3 contains the O-RW1 mechanism plus O-TW1 and the broad-safe O-LQ2 mechanism.

Offline:
- ALL3 materially dominates BASE/CONTROL;
- ALL3 is never worse than O-RW1+TW1 on the fresh seven-family composition gate;
- O-RW1 currently has the higher live rating.

Therefore the most defensible next active pair is:

1. **O-RW1 `56336027`** — retain;
2. **ALL3 V1** — submit as challenger.

Because Kaggriculture retains the two most recent active submissions, one new ALL3 submission should
retire the older CONTROL `56336025`.

## Submission guardrails

Before submitting ALL3:
- authenticate Kaggle;
- verify exact tar SHA;
- verify official loader selects `_kc_all3_entrypoint`;
- verify current CONTROL/O-RW1 rows still exist;
- verify no duplicate ALL3 description;
- verify daily submission cap;
- submit exactly one ALL3 package;
- capture its registered submission ID/status.

Do not submit any nearby variant in the same operation.

After registration:
- preserve O-RW1 + ALL3;
- monitor ALL3 to first informative exposure;
- do not reroll based on early rating noise.

