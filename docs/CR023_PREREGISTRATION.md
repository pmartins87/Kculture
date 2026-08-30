# CR023 — Public top-ladder backbone preregistration

Frozen **before any reward-based evaluation** of the three selected public action tapes.

The only completed evidence before this document is a mechanical probe: each frozen 719-action tape completed three old probe seeds in both seats (6/6 DONE per route), and the probe explicitly did not inspect/report rewards. Mechanical run: `33286607721`.

## Research question

CR008 produced the largest hosted improvement so far, but it is still built on the old R4B/COK backbone. The authenticated current-top atlas found several strong current submissions whose complete 719-action behavior is exactly repeated across three observed public games. CR023 asks whether one such **public, mechanically robust open-loop backbone** is a materially stronger base than frozen CR008 before any opponent-adaptive overlay is added.

This raw-backbone experiment does **not** add CR008 adaptation, opponent identity, route switching, classifier changes, MELON prediction, production response, or queue-position changes. It isolates the backbone.

## Frozen public routes

The exact replay provenance is frozen in `configs/cr023_public_tape_preregistered_seeds_v1.json`:

- `top11_openloop`: submission `55858273`, episode `102908981`, source seat `1`;
- `top16_openloop`: submission `55847696`, episode `102915518`, source seat `1`;
- `top19_openloop`: submission `55872138`, episode `102895545`, source seat `1`.

The raw replay is downloaded transiently from Kaggle at evaluation/build time. Raw replay/tape bytes are not committed to this repository or intentionally published as experiment artifacts. Provenance, code, aggregate metrics and derived candidate behavior may be preserved.

## Frozen control

`CR008` is the exact canonical hosted baseline:

- `candidates/cr008_adaptive_frontrun.py`;
- blob `8e1c26202c3101c19668bf61edf2ae51d4329d5d`.

Although CR008 includes its adaptive overlay, it is the relevant current agent to beat. This raw-tape Stage A therefore answers the practical question: **is this backbone already better than our current full agent?**

## Frozen evaluation population

Seed config: `configs/cr023_public_tape_preregistered_seeds_v1.json`.

### Raw-backbone Stage A

12 fresh seeds × exact nine frozen current-meta opponents × both seats = **216 paired conditions per route**.

### Raw-backbone Stage B

12 disjoint fresh seeds × same nine opponents × both seats = **216 paired conditions** for the single Stage-A winner only.

Exact opponent population: `configs/cr015_current_meta_opponents_v1.json`.

All **32/32 held-out seeds remain sealed and forbidden**.

A completely separate pair of Stage-A/Stage-B seed banks is already reserved for the later adaptive-overlay phase. Those reserved seeds are forbidden until one raw backbone has passed both raw Stage A and raw Stage B and the overlay candidate has been frozen.

## Metrics

For each tape vs exact CR008, paired on seed/opponent/seat:

- terminal own-money gain;
- terminal relative-money gain (`self - opponent`);
- W/L score gain, where win=1, tie=.5, loss=0;
- favorable and unfavorable W/L conversions;
- mean paired score gain;
- positive-relative-gain fraction;
- 10% lower-tail CVaR of paired relative gain;
- minimum paired relative gain.

A close-boundary subset of **40** conditions is chosen only by smallest absolute terminal CR008 relative delta. Tape outcomes may not influence close-set membership.

## Stage-A eligibility

A route is eligible only if all are true:

1. zero mechanical errors and all expected pairs complete;
2. broad unfavorable W/L conversions <= broad favorable conversions;
3. close-subset unfavorable conversions <= close favorable conversions;
4. broad mean W/L score gain **> 0**;
5. at least one broad favorable W/L conversion exists;
6. broad mean relative-money gain > 0.

The strict positive W/L requirements are intentional. A new backbone must demonstrate outcome value, not merely more coins.

If no route is eligible, the raw CR023 branch closes with no Stage B.

## Frozen Stage-A selection

At most one route may advance. Among eligible routes, select lexicographically, largest first, by:

1. broad `(favorable - unfavorable)` W/L conversions;
2. close `(favorable - unfavorable)` W/L conversions;
3. broad mean W/L score gain;
4. close mean W/L score gain;
5. broad mean relative-money gain;
6. broad 10% lower-tail CVaR of paired relative gain.

No second-place substitution, route modification, tape editing or seed reuse is allowed after seeing Stage A.

## Raw Stage-B confirmation

Only the unchanged Stage-A winner may be evaluated on raw Stage B.

It passes raw Stage B only if:

1. zero errors and all pairs complete;
2. broad Stage-B unfavorable W/L conversions <= favorable conversions;
3. close Stage-B unfavorable conversions <= favorable conversions;
4. Stage-B mean W/L score gain >= 0;
5. combined Stage A+B net broad W/L conversions > 0;
6. combined Stage A+B mean W/L score gain > 0;
7. combined Stage A+B mean relative-money gain > 0.

Failure closes the raw-backbone branch. Stage-A or Stage-B seeds may not be reused to choose a different route.

## Adaptive-overlay firewall

Passing raw A+B does **not** automatically create a hosted submission.

Only after one raw backbone has passed A+B may we freeze a new candidate that applies the **existing CR008 opponent-adaptation semantics** to that selected backbone, plus behavior-neutral clock hardening if desired. The overlay candidate must be frozen before opening the already reserved adaptive-overlay Stage-A seed bank.

The later adaptive phase must compare at least:

- selected raw backbone;
- selected backbone + frozen adaptation;
- exact CR008 baseline.

No team/opponent identity may be used as a runtime feature or gate.

## Interpretation

Public replay/tape evidence is treated as competition data/provenance, not as an excuse for post-hoc route hunting. Three routes were frozen from the authenticated atlas because they were fully open-loop and mechanically testable; rewards were intentionally not inspected before this preregistration.

The experiment is successful only if a route improves paired game outcomes across fresh opponent/seed coverage. A high leaderboard rating, one attractive replay, immediate coin production, or resemblance to a top team is insufficient.
