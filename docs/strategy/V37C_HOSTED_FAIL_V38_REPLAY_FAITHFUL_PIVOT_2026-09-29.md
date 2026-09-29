# V37-C Hosted Failure / V38 Replay-Faithful Pivot — 2026-09-29

## Hosted failure

V37-C submission `56626986` completed at **1490.3**.

Fresh authenticated Kaggle snapshot run: `36520558712`.
Current latest-two at the snapshot:
1. V37-C `56626986` — 1490.3;
2. Ahmed `56619409` — 1364.9.

Sep-29 UTC submission capacity at the same snapshot:
- `numAllowedNow = 5`;
- `numTotal = 38`.

The previous user authorization covered Sep-28 UTC only. **No Sep-29 submission is authorized yet.**

## V37-C replay evidence

Replay collector workflow `36519927553` downloaded 30 newest episodes from submission `56626986`, selected from 100 listed episodes, with zero download failures.

Observed result in those 30 episodes:
- 8 wins;
- 22 losses;
- mean terminal margin about -2568.7;
- median terminal margin about -1569.5.

This is a clear hosted failure, not merely a low initial rating.

Opening-family fingerprint in those 30 games:
- herd-safe BUY8/SELL3 no-race family: 10 games, 1W/9L, mean margin about -2694.7;
- v4x BUY20/SELL15 no-race family: 8 games, 4W/4L, mean margin about +674.4;
- tetsutani BUY5+seed race family: 5 games, 2W/3L, mean margin about -598.6;
- other/unclassified: 7 games, 1W/6L.

Known no-race families therefore dominate this observed draw (18/30), making unconditional ADV12 a poor prior for this bracket.

Cash-gap analysis of losses:
- step 384: still about +1309 ahead on average;
- step 480: about -470;
- step 576: about -2103;
- step 696: about -3829;
- terminal: about -4166.

The dominant failure signature is mid/late-season conversion, not opening collapse.

## Methodology reset

Random local panels are no longer the primary selector.

V38 validation uses:
1. actual hosted V37-C episodes;
2. exact Kaggle environment seed from each replay;
3. exact opponent action tape from each hosted game;
4. same seat;
5. first rerun exact V37-C and REQUIRE exact hosted final rewards;
6. only after 30/30 parity, run counterfactual V30B/candidate on the identical seed/opponent tape.

This makes the screen replay-faithful to the observed ladder draw. It is still not final proof against adaptive opponents, but is much stronger than the old generic local tournament.

## V38 arms

### V38-A2 — MODELPX
Exact V30B base plus public-state model-based lead seller:
- MILK / STRAWBERRY / WOOL;
- steps 144..695;
- infer rival public supply cadence from market inventory deltas;
- project one-step engine price;
- sell early only when projected price is falling.

Binding corrected run: `36521021564`.
Earlier V38A runs are non-binding integration attempts.

### V38-B — ADV12
Exact V30B base plus bounded 12-step sale-advance race layer.

Run: `36520859375`.

This arm is an independent control, not the preferred hypothesis, because most observed V37-C opponents belong to no-race families.

### Parallel binding speed-up
Workflow run family: `v38-fast-sharded-real-replay-panel`.
Commit: `83b7614ce55227c7cf4472c7a5451a2f8c6eb56a`.

Five shards each evaluate six of the exact 30 hosted episodes. Aggregate compares V30B vs MPX vs ADV12 after exact V37-C replay parity.

## Submission governance

Do not submit V38 on Sep-29 UTC without a new explicit user authorization.
When a replay-faithful winner is identified, present exact package/hash and request one broad Sep-29 adaptive authorization, not repeated micro-authorizations.
