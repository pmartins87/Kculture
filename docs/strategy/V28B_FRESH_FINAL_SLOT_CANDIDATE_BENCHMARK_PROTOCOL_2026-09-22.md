# V28B — Fresh Final-Slot Candidate Benchmark Protocol — 2026-09-22

## Status

PRE-REGISTERED after V27C2 closed fast rank-1 distillation and after the read-only V28A Kaggle audit, before any V28B causal outcome.

No Kaggle submission is authorized.

## Strategic question

Among the three currently reproducible first-party candidates:

1. exact V47;
2. exact V47 + O-RW1 only;
3. exact V47 + ALL3 = O-RW1 + O-TW1 + O-LQ2;

which one should be the primary final-slot candidate, and which one is the best hedge?

CR053 is retained as historical calibration but is not included in this fresh benchmark because:
- its best preserved hosted score (2064.8) is materially below the historical exact-V47 scores (2344.6 / 2387.9);
- it is a static replay route rather than a current adaptive base;
- the final benchmark is intended to discriminate among the strongest mechanically current V47-family candidates.

## Current competition facts frozen before V28B

Read-only V28A audit:
- workflow: `35683053247`;
- artifact: `10675491726`;
- audit timestamp: 2026-09-22 ~03:25 UTC.

Current team:
- rank: 1629;
- displayed score: 2050.6;
- active/latest submissions:
  - ALL3 `56367770`: 2050.6;
  - O-RW1 `56336027`: 2014.4.

Historical exact-V47 submissions:
- `56336025`: 2344.6;
- `56333577`: 2387.9.

These historical ratings are calibration evidence only, not directly comparable to a later ladder without a fresh common panel.

## Candidates

### V47
Exact public V47 base.

### ORW1
Exact V47 plus only O-RW1:
- `use_rw=True`;
- `use_tw=False`;
- `use_lq2=False`.

### ALL3
Exact V47 plus:
- O-RW1;
- O-TW1;
- O-LQ2.

All use independent fresh state per episode.

## Fresh frontier

At workflow start:

1. query current public Kaggriculture Top-30 once;
2. acquire serially with bounded retry;
3. SHA-deduplicate;
4. both-seat smoke against starter;
5. exclude exact V47 identity;
6. select up to 12 unique executable sources by representative rank only;
7. minimum selected: 8;
8. freeze exact V47 base + selected source packages in one immutable artifact;
9. remove Kaggle credentials before candidate/opponent execution.

No source reacquisition after snapshot.

## Fresh seeds

Exactly:
`80301,80302,80303,80304,80305,80306`.

Both seats.

With 12 sources:
- 144 common contexts;
- each of the 3 candidates runs on every identical context.

## Mechanical validity

Require:
- >=8 selected unique sources;
- all selected sources smoke PASS both seats;
- exact SHA snapshot verification;
- all candidate/context cells DONE/DONE, 720 steps, finite rewards;
- no duplicate/missing candidate/context cells;
- no live source acquisition during episodes.

Failure =>
`V28B_MECHANICS_INVALID`.

## Candidate metrics

For each candidate report:
- score rate;
- wins/ties/losses;
- mean/median margin;
- source-level score rates;
- seed-level score rates.

For each pair report:
- contexts where A score > B score;
- contexts where A score < B score;
- score-rate delta;
- margin delta.

## Frozen primary selector

Select primary by this order:

1. greater overall score rate;
2. greater number of source SHAs with score rate >=0.5;
3. greater number of seeds with score rate >=0.5;
4. greater mean margin;
5. lexical candidate key.

No hosted/public rating enters this selector.

## Frozen hedge selector

Among the two non-primary candidates, select the hedge by:

1. greater number of contexts where primary score <1.0 and hedge score ==1.0;
2. greater total score rate;
3. greater source breadth with score rate >=0.5;
4. greater mean margin;
5. lexical candidate key.

The hedge metric is intentionally complementary because the official final team score uses the better of the two active agents.

## Decisions

### `V28B_FINAL_PAIR_RECOMMENDATION_READY`
Mechanical pass and all three candidates complete.

Output exactly:
- primary candidate;
- hedge candidate;
- evidence table;
- current-vs-recommended active-slot change.

This is a recommendation only. Any Kaggle submission still requires explicit user authorization.

### `V28B_MECHANICS_INVALID`
Repair mechanics only; rerun exact same candidates/frontier snapshot/seeds.

## Anti-overfit

After outcomes:
- no candidate code changes;
- no seed filtering;
- no source filtering;
- no weighted source selection;
- no public leaderboard submission to decide V28B.

No Kaggle submission is authorized.
