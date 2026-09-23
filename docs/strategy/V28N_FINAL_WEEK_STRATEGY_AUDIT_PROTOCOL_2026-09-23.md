# V28N — Final-Week Competition Strategy Audit Protocol — 2026-09-23

## Purpose

Run a read-only final-week audit before committing compute to any new persistent-policy architecture.

Questions:
1. Is the protected latest-two pair still exactly V47 + ALL3?
2. How mature are V47 and ALL3 in listed public episodes?
3. What are their current hosted ratings?
4. What is the current Top-10 leaderboard threshold and gap from the better active submission?
5. Is there still enough calendar time before the September 30, 2026 final submission deadline to justify a new architecture branch?

## Inputs

Authenticated Kaggle CLI via the existing repository secret, read-only only.

Fixed active submission IDs:
- V47: `56466970`
- ALL3: `56367770`

## Outputs

- current submissions rows and latest-two;
- V47 and ALL3 listed episode counts;
- full current leaderboard row count;
- Top-10 scores/names;
- best active rating;
- gap to current #1 and #10;
- exact-score leaderboard candidate rows for our current best active rating;
- competition-list metadata snapshot.

No submission, deletion, or slot reordering is authorized.
