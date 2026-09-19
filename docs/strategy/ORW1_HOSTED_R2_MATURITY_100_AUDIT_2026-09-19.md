# O-RW1 Hosted R2 Maturity Audit — ~100 Episodes — 2026-09-19

Workflow `35417548071`.

Snapshot submission ratings:
- CONTROL `56336025`: **2429.1**;
- O-RW1 TREATMENT `56336027`: **2506.7**.

Complete available public histories at the audit:

CONTROL:
- 103 listed episodes;
- 102 externally resolved games;
- 76 wins, 24 losses, 2 ties;
- raw score rate **0.7549019608**;
- 99 unique opponents;
- mean margin **+4692.54**;
- median margin **+1543.5**.

O-RW1 TREATMENT:
- 106 listed episodes;
- 105 externally resolved games;
- 60 wins, 44 losses, 1 tie;
- raw score rate **0.5761904762**;
- 97 unique opponents;
- mean margin **+6121.92**;
- median margin **+17**.

## Interpretation

This is a mature hosted exposure snapshot, but it is **not a matched A/B population**.
The treatment has the higher Bradley-Terry live rating despite a lower raw score rate,
which demonstrates that opponent strength/order is materially different across the two
histories. Therefore raw W/L must not be used as a direct treatment-vs-control causal
estimate.

The binding causal evidence for O-RW1 remains the hosted-faithful offline causal/runtime
gates. Hosted evidence says the treatment can sustain a rating around ~2500 in the live
arena after >100 episodes, not that its unadjusted 60-44-1 record is directly comparable
to CONTROL's 76-24-2.

No third Kaggle submission is authorized by this audit. Preserve both active slots while
offline option-value/selector work proceeds.
