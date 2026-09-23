# V28H — Matched Hard-vs-Easy Trajectory Trace — Binding Result — 2026-09-22

## Binding execution

Corrected binding workflow: `35813287407` (V28H-R2), SUCCESS.

Attempt 1 `35812876571` is non-binding mechanics-invalid only because the post-episode summary referenced `defaultdict` without the `collections.` qualifier. R2 changed only that summary reference to `collections.defaultdict`; no scientific rule, target, control, replay, checkpoint, selector, or threshold changed.

## Mechanical validity

**PASS**.

R2 reused:
- immutable V28F snapshot from workflow `35807910104`;
- exact V28F ALL3 aggregate rows;
- exact V28G deterministic `trace_targets` from workflow `35812527508`;
- zero-loss controls matched at the same seed and seat;
- exact V28F terminal score and margin as the replay contract.

Failures: **0**.

## Binding result

Decision: **`V28H_MIDGAME_STRUCTURAL_SEPARATION`**.

Selected checkpoint: **480**.

Frozen explanatory window selected by the protocol: **steps 384–479**.

The earliest checkpoint whose median paired hard-minus-control money-gap difference crossed the frozen -1000 threshold was 480:

| checkpoint | mean hard-control money-gap diff | median |
|---:|---:|---:|
| 0 | 0.0 | 0.0 |
| 96 | -12.0 | -13.5 |
| 192 | -62.67 | -18.5 |
| 288 | -885.67 | -876.5 |
| 384 | -518.83 | -227.5 |
| **480** | **-1763.58** | **-1016.0** |
| 576 | -5912.42 | -6223.0 |
| 648 | -7346.58 | -8511.0 |
| 696 | -9502.25 | -9808.5 |
| 719 | -11249.08 | -12473.0 |

At checkpoint 480 the largest composition differences were opponent money **+1635.17 mean / +803 median**, own money **-128.42 mean / -119.5 median**, and opponent COW count **+1.083 mean / +1.5 median**. ALL3's own action allocation in the preceding explanatory window was almost unchanged; the dominant separation was in opponent behavior/economics rather than an obvious ALL3 option-event timing shift.

Option timing was essentially identical between cohorts: median first O-RW1 event step 155, O-TW1 step 80, and O-LQ2 about 599–600.

## Interpretation and route

The residual hard regime becomes economically distinguishable in the **midgame**, with the frozen selector locating the first material separation at step 480. This does not justify an opponent-specific runtime rule.

V28I was pre-registered before this result in `docs/strategy/V28I_LEGAL_STATE_RISK_IDENTIFIABILITY_PROTOCOL_2026-09-22.md`. Because V28H mechanics PASS, the binding next action is to execute V28I exactly as frozen using all 144 V28F ALL3 contexts and only the 114 legal `solver.programme_features` at checkpoint 480.

Current hosted pair remains unchanged:
- primary ALL3 `56367770`;
- hedge exact V47 `56466970`.

No Kaggle submission, deletion, or reordering is authorized.
