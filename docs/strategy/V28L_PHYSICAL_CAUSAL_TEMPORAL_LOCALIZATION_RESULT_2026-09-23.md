# V28L — Physical Causal Temporal Localization Result

Date: 2026-09-23

Binding workflow: `35827398179`

## Decision

**`V28L_NO_ROBUST_PHYSICAL_TEMPORAL_HEADROOM`**

Mechanical PASS. Failures: 0. All 66 immutable V28F ALL3 residual-loss contexts were evaluated under BASE plus the three frozen windows. BASE terminal replay parity was exact as required.

## Frozen-window results

| Mode | Loss→win flips | Flip sources | Flip seeds | Flip seats | Mean score delta | Mean margin delta | Median margin delta | Pass |
|---|---:|---:|---:|---|---:|---:|---:|---|
| BASE | 0 | 0 | 0 | — | 0 | 0 | 0 | no |
| EARLY 0–191 | 0 | 0 | 0 | — | 0 | -685.73 | 0 | no |
| PRE_MID 192–383 | 4 | 2 | 1 | 0,1 | +0.060606 | -4598.21 | 0 | no |
| LATE 480–719 | 4 | 2 | 1 | 0,1 | +0.060606 | -213.79 | +180 | no |

The frozen robustness rule required at least 4 loss-to-win flips across at least 2 sources **and at least 2 seeds**, with positive mean score delta. PRE_MID and LATE each reach the flip/source/score conditions but both concentrate every flip in one seed, so neither passes. EARLY has no W/L headroom.

## Binding interpretation

V28K and V28L together exhaust the opponent-action physical-imitation rescue hypothesis across the complete episode partition: MIDGAME 384–479 failed in V28K, and EARLY/PRE_MID/LATE fail here. The repeated four-flip signal is real enough to record but not robust enough to justify weakening the preregistered seed-diversity gate.

Per the frozen V28L routing, opponent-action physical imitation is closed as a practical rescue path for the V28F hard core. Subsequent work must return to broader first-party mechanism discovery/final competition strategy. No classifier retuning, window resizing, boundary search, source-conditioned runtime feature, or threshold relaxation is authorized by this result.

Opponent source/rank/SHA remains offline forensic metadata only and is forbidden as a runtime policy feature.

Hosted pair remains exactly V47 submission `56466970` + ALL3 submission `56367770`. No Kaggle submission, deletion, or reordering was performed or authorized.
