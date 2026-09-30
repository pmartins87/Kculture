# V39 — Final Pair Submission — 2026-09-30

## Final decision

The project is closed to further Kaggle mutations.

Final pair:
1. V30B exact — submission `56693642`
2. V47 exact — submission `56693641`

No further submissions are authorized even though three daily submissions remained after this operation.

## Binding run

Workflow: `36655869236` — SUCCESS.

Preflight:
- latest-two before mutation: V37-C `56626986` + Ahmed `56619409`;
- `numAllowedNow=5`;
- `numTotal=38`;
- no slot drift.

## V47 exact

Submission:
- ID: `56693641`
- description: `PS_V39_FINAL_V47_EXACT_08E56C43`
- initial status: PENDING

Exact archive SHA-256:
`08e56c43ecf28253605b61066dd769334d96262056b8cd337489f1f4f909ad01`

Exact main.py SHA-256:
`f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842`

Historical hosted evidence:
- 2387.9 exact-control run
- 2344.6 exact-control run
- later reruns showed substantial ladder variance, so this is a hedge based on the strongest repeated hosted evidence, not a guaranteed score.

## V30B exact

Submission:
- ID: `56693642`
- description: `PS_V39_FINAL_V30B_EXACT_70D93426`
- initial status: PENDING

Exact archive SHA-256:
`70d93426baa309e3a13a6c837504e4d73b177cd05d7d2865c024844e1d2abe7b`

Exact main.py SHA-256:
`4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01`

Historical hosted score:
- 2010.0 on submission `56509591`.

## Final slot verification

Immediately after both registrations:
- newest: V30B `56693642`
- second: V47 `56693641`

This is the intended final pair.

Quota after final pair:
- `numAllowedNow=3`
- `numTotal=40`

Those three remaining submissions are intentionally unused.

## Closed hypotheses

V37-C completed at 1490.3 and is rejected.
Ahmed V36 completed at 1364.9 and is rejected.
V38-A MODELPX is not promoted: replay harness showed 28/30 vs 27/30, but MPX telemetry recorded zero fires, making the apparent gain inconsistent with the claimed mechanism.

## Binding state

**KCULTURE_FINAL_PAIR_LOCKED_V30B_PLUS_V47_NO_MORE_SUBMISSIONS**

Only read-only monitoring is allowed from this point.
