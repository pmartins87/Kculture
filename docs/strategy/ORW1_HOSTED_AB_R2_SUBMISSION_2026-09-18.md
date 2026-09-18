# O-RW1 Hosted A/B R2 — Corrected Hosted-Faithful Submission — 2026-09-18

## Corrected pair

Submission workflow:
`35373555439`.

This is the **first valid hosted O-RW1 A/B pair**. The earlier treatment submission
`56333579` is mechanically invalid and must not be compared as O-RW1.

### CONTROL

- submission ID: **56336025**
- exact public V47;
- archive SHA:
  `08e56c43ecf28253605b61066dd769334d96262056b8cd337489f1f4f909ad01`;
- hosted entrypoint verified immediately before submit:
  **`_y_agent_shopherd`**;
- registered:
  `2026-09-18 17:19:39.130000 UTC`;
- initial status:
  `PENDING`.

### TREATMENT

- submission ID: **56336027**
- corrected hosted-faithful V47 + O-RW1 package;
- archive SHA:
  `997aa273cb64c6acf933f8d719bd358c47d07871f6e42ac056003155499c68c9`;
- hosted entrypoint verified immediately before submit:
  **`_kc_orw1_entrypoint`**;
- registered:
  `2026-09-18 17:19:40.807000 UTC`;
- initial status:
  `PENDING`.

Registration separation:
**1.677 seconds**.

## Pre-submit proof chain

Hosted-faithful causal gate:
- run `35363453097`;
- score delta +0.0833333;
- 8 positive flips;
- no negative-W/L states.

Hosted-faithful runtime:
- run `35367785929`;
- 64 pairs / 128 episodes;
- `0.625 -> 0.71875`;
- score delta **+0.09375**;
- 14 non-win -> win flips;
- 0 win -> non-win regressions.

Corrected package:
- run `35372969031`;
- entrypoint `_kc_orw1_entrypoint`;
- 8/8 exact action parity;
- 8/8 exact reward parity;
- 0 failures.

## Quota

Authenticated preflight observed 2 previous submissions on 2026-09-18 UTC.
This corrected pair moved the day to **4/5** allowed slots.

Do not submit another candidate today without explicit information-value justification.

## Current state

`ORW1_HOSTED_AB_R2_SUBMITTED_AWAIT_BOTH_RESULTS`.

Do not interpret one arm alone and do not tune O-RW1 while either arm remains PENDING.

## First comparable hosted checkpoint and replay maturity

Authenticated status at `2026-09-18 17:24:36 UTC`:
- CONTROL `56336025`: `COMPLETE`, rating field `600.0`;
- TREATMENT `56336027`: `COMPLETE`, rating field `600.0`.

This equality is **not evidence of neutrality**.

Replay forensics:
- workflow `35374217511`;
- artifact `10559931321`;
- CONTROL listed episodes: **1**;
- TREATMENT listed episodes: **1**;
- externally attributable resolved games: **0 / 0**.

Therefore there is currently no hosted W/L evidence with which to compare the valid R2
arms. The displayed 600.0 values are initial/immature rating state only.

Binding state:
`ORW1_HOSTED_AB_R2_COMPLETE_BUT_UNMATURE_NO_EXTERNAL_EVIDENCE`.

Preserve the fifth daily submission slot. Do not tune O-RW1 or open a nearby hosted
variant from this checkpoint.

## Exposure-asymmetry checkpoint

Authenticated status at approximately `2026-09-18 17:28:18 UTC`:
- CONTROL: `COMPLETE`, rating `718.3`;
- TREATMENT: `COMPLETE`, rating `600.0`.

Replay refresh at approximately `17:28:59 UTC` explains the gap:
- CONTROL listed episodes: **2**;
- CONTROL externally resolved games: **1**;
- CONTROL W-L: **1-0**;
- CONTROL mean/median margin: **+57,846**;
- TREATMENT listed episodes: **1**;
- TREATMENT externally resolved games: **0**.

Therefore the current rating difference is **exposure asymmetry**, not evidence of an
O-RW1 regression. The treatment has not yet received an externally attributable game.

Binding state:
`ORW1_HOSTED_AB_R2_VALID_BUT_EXPOSURE_ASYMMETRIC_AWAIT_BALANCED_EXTERNAL_GAMES`.

Do not poll minute-by-minute. The next informative checkpoint remains frozen at at least
32 externally attributable completed public games per arm. Preserve the fifth daily
submission slot.

## Balanced early-exposure checkpoint

Authenticated/replay snapshot at approximately `2026-09-18 18:01 UTC`:

CONTROL `56336025`:
- rating `1457.7`;
- listed episodes: **9**;
- externally resolved games: **8**;
- record: **8-0-0**;
- mean margin: **+36,006.875**;
- median margin: **+32,461.5**;
- unique external opponents: **8**.

TREATMENT `56336027`:
- rating `1458.2`;
- listed episodes: **10**;
- externally resolved games: **9**;
- record: **9-0-0**;
- mean margin: **+47,125.222**;
- median margin: **+40,053**;
- unique external opponents: **9**.

The exposure asymmetry has largely disappeared and both arms are undefeated in the
small early sample. The treatment is not showing an early catastrophic hosted failure.

However, the frozen informative threshold of **32 externally resolved games per arm has
not been reached**, so this checkpoint does **not** authorize promotion, tuning or a fifth
submission.

Binding state:
`ORW1_HOSTED_AB_R2_BALANCED_EARLY_EXPOSURE_AWAIT_32_PER_ARM`.
