# CR088 Phase 0 — current-top population seed screen

Frozen before any Phase-0 H2H result is observed.

## Why

The current top-10 discovery run `34803148700` recovered 30 coherent public
719-action tapes, three per top team.  Exact full-action Hamming distance is not
a useful lineage selector: every tape was unique, and even tapes from the same
active submission differed heavily.  The macro profile from run `34803658746`
nevertheless shows repeated production families, including a WHEAT/MELON ->
STRAWBERRY family and a second MELON-heavy family shared by multiple top teams.

The exact hosted-byte league also falsified local rank calibration: CR083 and
CR086 beat the real CR053 locally even though CR053 remains materially stronger
on Kaggle.  Therefore this phase uses local games only to detect broken or
catastrophic seeds and preserve diverse starting material for automatic search.

## Frozen population and data

- 30 tapes from artifact `cr087-current-top-lineage-discovery-v1`, run
  `34803148700`;
- exact source tape hashes are verified against the frozen metadata;
- exact hosted-byte anchors: CR053 real, CR052 real, CR083 and CR086;
- reference engine `kaggle-environments==1.32.7`;
- master `9220881`, three fresh derived seeds, both seats, four anchors;
- original final held-out remains sealed.

## Interpretation

Every candidate is a deterministic package containing only its public action
tape and a neutral clock fallback.  Source identity/rank/submission is retained
only as offline provenance and is not a runtime feature.

The reported robust local safety score is:

`0.50 * mean_anchor_score + 0.35 * worst_anchor_score + 0.15 * seat_floor`.

It is a safety-ranking diagnostic, not a promotion gate and not a hosted-rating
prediction.  Phase 1 must retain source-team/macro diversity; it may not simply
promote the highest local score.

## Stop and continuation rules

- no automatic Kaggle submission from Phase 0;
- mechanical failures are quarantined, not repaired on these seeds;
- no single-tape or tape-splicing retuning on the Phase-0 results;
- if mechanically valid seeds exist, build a state-coherent Phase-1 population
  around multiple macro families and test economically meaningful operators;
- Kaggle hosted probes, not local H2H alone, decide transfer.
