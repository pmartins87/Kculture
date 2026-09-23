# V28N — Final-Week Competition Strategy Audit Result — 2026-09-23

## Binding audit

Workflow: `35875524017`.

The core read-only audit completed and printed a complete `V28N_RESULT`. The workflow conclusion was FAILURE only because artifact upload attempted to archive a Kaggle leaderboard filename containing colon characters, which GitHub artifact upload rejects for cross-platform compatibility. The Kaggle queries, parsing, current scores, episode counts, full leaderboard parse, and ranking calculations all completed successfully before that archival-only failure.

No Kaggle mutation occurred.

Snapshot UTC:
`2026-09-23T14:37:35.015940+00:00`.

## Active pair

Latest two remained exactly:
1. exact V47 `56466970`;
2. ALL3 `56367770`.

Pair drift:
**false**.

### ALL3

Submission:
`56367770`.

Status:
COMPLETE.

Current public score:
**1862.4**.

Listed public episodes:
**482**.

### exact V47

Submission:
`56466970`.

Status:
COMPLETE.

Current public score:
**1828.7**.

Listed public episodes:
**175**.

Therefore V47 has crossed the previously frozen >=169-episode maturity checkpoint.

## Current leaderboard

Parsed teams:
**9910**.

Our better active score:
**1862.4**.

Exact matching leaderboard row:
- team: **Paulo Martins**;
- rank: **1916**;
- score: **1862.4**.

Current Top 10:

1. Boey — 3094.4
2. M & M & P & Q — 3069.7
3. DSM — 3048.3
4. Unknown Mother-Goose — 3044.9
5. DECEM — 3018.6
6. Vadim Vasilenko — 3015.0
7. 吃白饭的大肥鱼 — 3006.3
8. Kaggledew Valley 🏆 — 3002.4
9. mtmr_s1 — 2997.1
10. Fourth Quadrant — **2959.8**

Gap from our better active score:
- to #1: **1232.0 rating points**;
- to #10: **1097.4 rating points**.

## Timeline

Official competition timeline states:
- entry/team-merger deadline: September 23, 2026;
- final submission deadline: **September 30, 2026 at 23:59 UTC**;
- post-deadline games continue into approximately October 15 for convergence/final Bradley-Terry evaluation.

Thus approximately one week remains for new submission development.

## Binding strategic conclusion

The protected ALL3 + V47 pair is mechanically stable but **not prize-contending at the current ladder state**. Preserving it alone is not a rational prize strategy given a >1000-point gap to the current Top-10 threshold.

The final-week research route must therefore be a genuinely higher-ceiling persistent-policy architecture, while keeping ALL3+V47 protected until a new candidate passes offline and fresh closed-loop gates.

V29A recurrent structural teacher distillation is opened as that final-week architecture branch.

No Kaggle submission, deletion, or reordering is authorized by V28N.
