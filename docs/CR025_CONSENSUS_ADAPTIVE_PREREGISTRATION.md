# CR025_CONSENSUS_ADAPTIVE — frozen test

Date: 2026-09-05

## Purpose

Test the highest-value next step after CR024_CONSENSUS_V1: keep the strong H11/M19 consensus backbone intact and add only the already-validated CR008 high-confidence market front-run overlay.

This is deliberately narrow. There is no dynamic fallback, no opponent identity, no backbone switching, no threshold retuning, and no new product. The CR024 consensus action remains unchanged except when the frozen CR008 public-state model authorizes an additional same-turn SELL of available CARROT or STRAWBERRY stock.

## Frozen policy

- base: CR024_CONSENSUS_V1 = top19 farmer shell + top11 hands + top19 market;
- adaptive feature encoder/model/thresholds: exactly the frozen CR008 implementation and `models/cr007_pure_models.json`;
- intervention: append only `SELL CARROT` and/or `SELL STRAWBERRY`, full current shed quantity, subject to the existing market-order cap and no duplicate SELL for the same item;
- public observations only;
- no username/team/submission/seed identity;
- no runtime network requirement in a future package.

## Fresh evaluation

Open exactly `adaptive_overlay_stage_b_seeds_reserved` from `configs/cr023_public_tape_preregistered_seeds_v1.json` for the first time for this candidate.

Panel: the same seven exact reproducible frozen opponents used by CR024 consensus: kaito_sparse, prvsiyan, salem, rayk, tactical, boatlee, and andrew. Both seats. Expected rows: 7 x 12 x 2 = 168.

Direct paired comparison: CR024_CONSENSUS_V1 control vs CR025_CONSENSUS_ADAPTIVE.

## Promotion rule

Mechanical: 168/168 rows, zero runtime errors, all DONE.

Strategic gate:

- score gain over CR024 >= +2.0;
- net favorable W/L conversions >= +2;
- unfavorable W/L conversions <= 4;
- mean margin gain > 0;
- overlay must actually fire on at least one evaluated game.

If all pass: `CR025_PASS__PACKAGE`.
Otherwise: `CR025_FAIL__RETIRE_OVERLAY_ON_CONSENSUS`.

The 32/32 final held-out seeds remain sealed. No threshold or product change is allowed after this Stage-B block is opened.
