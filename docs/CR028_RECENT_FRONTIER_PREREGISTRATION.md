# CR028 — current-engine recent-frontier preregistration

Date: 2026-09-05

## Why the search target changed

The earlier historical `rating >= 3000` lineage result mixed Kaggriculture engine versions. Joining `episode_features.csv` showed **zero** rated seat-games at or above 3000 on engine `1.32.7`. Therefore historical pre-patch 3000+ routes are not valid current parents.

Across all `1.32.7` public dataset observations available at this freeze:

- 91,346 rated seat-games;
- 19,028 unique submissions;
- max observed rating: **2953.3258**;
- only 5 seat-games >= 2900;
- 116 seat-games >= 2800.

Those peaks are concentrated near the August 15 balance transition. In the most recent seven-day window ending at the dataset anchor `2026-09-05T08:03:45Z`, the highest observed rating is **2645.2715**. The recent field is therefore materially different from the early post-patch peaks.

## Recent source frozen before CR028 outcomes

The strongest recent route is public episode `105248818`, seat 0, submission `55992804`, observed rating `2645.271463984536`, engine `1.32.7`.

Public action-stream hashes:

| turn | hash |
|---:|---|
| 24 | `ae831dd2ed69073e` |
| 48 | `cc0dff4cf858cc09` |
| 100 | `1aa8a3c99592537e` |
| 136 | `a9930ef499dd88bd` |
| 200 | `04ed6bf3e90b511b` |
| 400 | `40170920482303b2` |
| 719 | `ab5995ca8d95f3a7` |

The exact complete stream is independently present in episode `105254265`, seat 0, submission `55993805`, observed rating `2597.9588428109187`. This replication is selection evidence only; it is not counted as a CR028 test outcome.

The same recent family is widespread: in the last three days `04ed6bf3e90b511b` through turn 200 appears in 23 distinct submissions/teams among the top-100-submission cohort and reaches the recent maximum 2645.27. In the last seven days it remains the most repeated h200 lineage in that cohort.

CR024's own h24 lineage `9f797cd4cc189a84` is also present among recent viable agents (13 submissions / 12 teams in the seven-day top-100 cohort, max about 2504). This argues against assuming the first 24 turns alone are CR024's principal defect.

## Frozen Stage-A variants

Configuration: `configs/cr028_recent_top_splice_screen.json`.

1. `full_recent_top`: exact source route through all 719 actions.
2. `prefix24_then_cr024`: source first 24 actions, CR024 thereafter.
3. `prefix48_then_cr024`.
4. `prefix100_then_cr024`.
5. `prefix136_then_cr024`.
6. `prefix200_then_cr024`.

Prefix splices are diagnostic. They can fail because the suffix was generated for a different state trajectory; no splice is presumed coherent or superior.

## Fresh Stage-A evaluation

Fresh seeds, frozen before outcomes:

`1849673021, 1849673071, 1849673119, 1849673189`

The preparation script enforces disjointness from all seed values in the CR023 preregistered config and CR027 frontier config.

Every variant is tested:

- head-to-head versus CR024 on all four seeds and both seats (8 games);
- paired CR024-versus-candidate comparisons against exact Rayk V23, Boatlee V2 and Prvsiyan V10 on the same four seeds and both seats (24 paired rows / 48 environment runs per variant).

Stage-A screen checks:

- zero runtime errors / complete rows;
- direct score >= 4/8;
- reactive paired score gain >= 0;
- reactive regressions <= 4.

Passing variants are ranked by reactive W/L gain, fewer regressions, direct score, reactive mean margin, then direct mean margin. No threshold rescue after results.

## What Stage A does not authorize

- No Kaggle submission.
- No final held-out seeds are touched.
- No team/rating/lineage identity becomes a runtime feature.
- A Stage-A winner still requires fresh hosted/live-meta calibration before packaging.

Workflow: `cr028-recent-top-stage-a.yml`.
