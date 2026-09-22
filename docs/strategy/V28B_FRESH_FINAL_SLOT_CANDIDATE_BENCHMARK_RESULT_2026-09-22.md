# V28B — Fresh Final-Slot Candidate Benchmark Result

Date: 2026-09-22
Binding workflow: `35683424225`
Launch commit: `405335b3c031df3ab0357822b117021bcc362c98`
Final artifact: `10676502357`
Artifact digest: `sha256:1e9d4f6164eca71a654a315392d764ae8850223351e723896c210c1d6269f588`

## Binding decision

`V28B_FINAL_PAIR_RECOMMENDATION_READY`

Mechanical status: PASS. Failures: 0. Selected fresh frontier sources: 12. Fresh seeds: `80301..80306`, both seats. Contexts per candidate: 144.

## Frozen-selector result

Recommended primary: **ALL3**.
Recommended hedge: **V47**.
Recommended active pair: **ALL3 + V47**.
Current active pair at the V28A/V28B audit: **ALL3 + ORW1**.

The selector therefore recommends preserving ALL3 as primary and replacing ORW1 with exact V47 as the hedge, subject to explicit user authorization before any Kaggle submission.

## Fresh common-panel metrics

All three candidates had identical binary score rate and breadth on the frozen common panel:

| Candidate | Score rate | W-L-T | Sources >= 0.5 | Seeds >= 0.5 | Mean margin | Median margin |
|---|---:|---:|---:|---:|---:|---:|
| ALL3 | 0.4444444 | 64-80-0 | 4/12 | 1/6 | **+26.3750** | -615.0 |
| V47 | 0.4444444 | 64-80-0 | 4/12 | 1/6 | -62.7986 | -943.5 |
| ORW1 | 0.4444444 | 64-80-0 | 4/12 | 1/6 | -70.3681 | -943.5 |

Primary selection follows the pre-registered ordering: overall score rate -> source breadth -> seed breadth -> mean margin -> lexical. The first three criteria tie exactly, so ALL3 wins on mean margin.

For the hedge criterion, both V47 and ORW1 convert 0 primary non-wins into wins and then tie on overall score rate and breadth. V47 wins the next applicable tie-break on mean margin (-62.7986 versus -70.3681).

Pairwise score-rate deltas are 0 throughout. Mean-margin deltas: V47 over ORW1 +7.5694; ALL3 over V47 +89.1736; ALL3 over ORW1 +96.7431.

## Competition context preserved from V28A

At the read-only audit immediately preceding V28B, the current team rank was 1629/9795 and displayed score 2050.6. The active/latest pair was ALL3 submission `56367770` (2050.6) plus ORW1 submission `56336027` (2014.4). Historical exact-V47 submissions `56336025` and `56333577` had displayed scores 2344.6 and 2387.9 respectively. Under the audited final-evaluation rule, only the latest two submissions remain active/tracked, the team score is the better of the two, and the second slot acts as a hedge.

## Binding route

No further autonomous Kaggle action is permitted. **No Kaggle submission has been made.**

The next action is a genuine user decision: explicitly authorize or reject changing the active pair from `ALL3 + ORW1` to the frozen-selector recommendation `ALL3 + V47`. If authorized, submission mechanics must preserve the intended ordering/active-pair semantics and must not add any unapproved candidate.
