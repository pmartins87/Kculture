# V28D — Current Hosted Pair Forensics — Result — 2026-09-22

## Binding run

Workflow `35781539795` completed SUCCESS. Artifact `v28d-current-hosted-pair-forensics` digest `sha256:ab7fd49996e8b6ee26c837494564737302fdd4ab59f7a3f18812c5f0128150f5`.

Mechanical result: valid. Exact submissions were V47 `56466970` and ALL3 `56367770`; replay collection and the pre-registered Episode-ID alignment completed without workflow failure.

## Binding decision

`V28D_NO_CURRENT_META_V47_UNDERPERFORMANCE_SIGNAL`

The current hosted evidence does **not** satisfy the frozen robust-underperformance branch for V47.

### V47 overall in its current episode window
- 89 games: 45 wins / 4 ties / 40 losses;
- score rate: `0.5280898876`;
- mean margin: `+6198.47`;
- median margin: `+42`;
- 86 unique opponents;
- Episode-ID window: `112051391..112150695`.

### ALL3 aligned to the exact V47 Episode-ID window
- 23 games: 9 wins / 0 ties / 14 losses;
- score rate: `0.3913043478`;
- mean margin: `-1362.61`;
- median margin: `-1089`;
- 23 unique opponents.

Overall delta V47 minus aligned ALL3:
- score rate: `+0.1367855398`;
- mean margin: `+7561.08`.

### Common-opponent evidence
Only one opponent (`Chiranjith`) was common in the aligned samples, so this comparison is too sparse to establish broad matchup superiority. On that one common opponent both were 1-0; V47 margin was `+2228`, ALL3 `+1805` (V47 delta `+423`).

The weak common-opponent overlap is an important limitation, but it cannot support a claim of robust V47 underperformance. The broader contemporaneous window points in the opposite direction.

## Route

Per the frozen V28D protocol, preserve the active pair:
- primary: ALL3 `56367770`;
- hedge: exact V47 `56466970`.

O-RW1 `56336027` remains outside the latest two.

Do **not** launch the stale-rating hedge-candidate reopening branch (CR053 etc.), because its prerequisite — robust current-meta V47 underperformance — did not occur.

Continue read-only maturity/status monitoring. No Kaggle submission, deletion, or reordering is authorized.
