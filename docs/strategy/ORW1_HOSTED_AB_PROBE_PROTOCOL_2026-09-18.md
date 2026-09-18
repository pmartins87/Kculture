# O-RW1 Hosted A/B Probe Protocol — 2026-09-18

## Question

Does the frozen first-party O-RW1 option improve **hosted Kaggle strength** relative to
the exact V47 base in the live competition population?

Offline evidence is already sufficient:
- wrapper-proposal oracle: +0.125 W/L headroom;
- first-party causal gate: +0.1667 mean score delta, no negative-W/L states;
- autonomous runtime gate: 0.5000 -> 0.6875 (+0.1875), 28 positive flips, no
  win->non-win regressions;
- final package parity: exact action/reward parity vs reference implementation.

Do not add further local retuning before this hosted sensor.

## Arms

### CONTROL — exact public V47

Handle:
`ahmedberatozer/kaggriculture-v47-reactive-market-coordination`

Required identities:
- output archive SHA-256:
  `08e56c43ecf28253605b61066dd769334d96262056b8cd337489f1f4f909ad01`;
- `main.py` SHA-256:
  `f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842`.

Submit the exact public output archive bytes. Do not rebuild, re-tar or edit it.

Suggested submission message:
`PS ORW1 CONTROL exact V47 2026-09-18`.

### TREATMENT — V47 + frozen O-RW1

Archive:
`KCULTURE_V47_ORW1_ONESHOT_V1.tar.gz`

SHA-256:
`b994e00d7adba05827eb8839b806211c2c8199dd0ad09a28b63815b58479c80f`.

Suggested submission message:
`PS ORW1 TREATMENT V47+one-shot ready WOOL 2026-09-18`.

## Submission discipline

1. Verify both archive hashes immediately before submit.
2. Submit CONTROL and TREATMENT in the same short operational window.
3. Record submission IDs and exact timestamps.
4. Do not submit another variant between the pair.
5. No post-result edits to O-RW1 quantity/product/trigger.
6. Wait for both hosted evaluations to complete before interpreting the pair.
7. Record public/private/rating fields exposed by the competition API exactly as returned.

## Interpretation

Hosted rating is not a deterministic paired test. Therefore the A/B is a **population
sensor**, not a proof from one number.

Primary evidence:
- treatment hosted score/rating relative to contemporaneous exact-base control.

Secondary:
- rank movement;
- episode count / uncertainty if exposed;
- whether either arm is still moving when queried.

### Advance

If treatment is materially above the contemporaneous control with both evaluations
complete/stable enough for interpretation:
- retain O-RW1 in the competitive nucleus;
- use hosted delta to calibrate the next proposal/value search;
- do not immediately tune O-RW1 itself.

### Neutral / ambiguous

If scores are close or still noisy:
- preserve O-RW1 as offline-PASS option;
- obtain another temporal sensor only if the information value justifies a slot;
- do not tune from noise.

### Regression

If treatment is materially below control:
- do not erase the causal offline result;
- mark O-RW1 as hosted-nontransferring on this population snapshot;
- inspect why the live population differs, especially same-lineage V47/V48 concentration
  and Tactical-Memory-style large margin dynamics;
- move solver search toward state-conditioned proposal value rather than threshold rescue.

## Authorization

This protocol is frozen and ready, but **no hosted submission is authorized until the
user explicitly approves the A/B probe**.
