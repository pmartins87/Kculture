# FP001 E2D — deterministic-town causal protocol — 2026-09-14

## Purpose

Obtain a clean causal estimate of the exact frozen E2 dedicated-hand STRAWBERRY module after E2C proved that policy-dependent tile occupancy changes the daily RNG stream and therefore random town-shop unlocks, contaminating product prices.

This is an attribution environment, not a hosted-performance environment.

## Frozen policy

Use `candidates/fp001_e2_dedicated_strawberry_hand.py` exactly as committed before E2/E2B result inspection. No candidate parameter or decision rule may change.

## Environment

- exact `kaggle-environments==1.32.7`;
- `episodeSteps=720` (30 days);
- `startingMoney=3000`;
- `weedSpawnChance=0`;
- `townShopUnlockInterval=999`, which prevents random shop unlocks during the 30-day season;
- deterministic town-center demand remains at the ordinary `townCenterSellInterval=24`;
- ordinary market mechanics/prices remain active;
- pass opponent;
- fresh nominal seeds `69401..69404` × both seats.

With both weed outcomes and shop RNG removed, seed should no longer materially alter these deterministic production programs. Repetition across seeds/seats is therefore a determinism/symmetry audit as well as a paired gate.

## Architectures

For each backbone:

- COW4_DAILY `S0H0` animal-only;
- COW4_DAILY `S1H0` exact E1 crop/no-hand;
- COW4_DAILY `S1H1` exact E2 crop + dedicated hand;
- COW5_SURVIVAL same three states;
- COW5_DAILY same three states.

## Primary comparisons

The decisive comparison is **S1H1 − S0H0**: total value of the labor-enabled crop module against the unchanged animal-only backbone.

Secondary comparison **S1H1 − S1H0** measures the incremental value of dedicated labor versus the inherited E1/no-hand crop state. It must not substitute for the primary total-module test.

## Required checks

- DONE/DONE;
- all expected cows survive;
- S1H1 establishes and harvests crop;
- exactly intended H11 crop maintenance approximately 17 WATER + 2 FERTILIZE + 4 HARVEST per episode;
- 8 STRAWBERRY realized/sold per S1H1 episode;
- main-farmer animal action totals and MILK volume remain consistent with backbone;
- paired deltas are economically plausible and stable after stochastic-shop removal.

## Promotion rule

A backbone preserves the one-hand/one-STRAWBERRY module only if:

1. `S1H1 − S0H0 > 0` in a clear majority and positive mean;
2. the magnitude is consistent with observed crop/labor/fertilizer cashflows rather than a hidden stochastic amplification;
3. full expected cow survival and intended crop realization hold.

Failure closes this exact crop-module/backbone combination without threshold rescue.

Success does **not** authorize hosted submission. It authorizes the next integration gate: improve utilization of the same hand and compare the premium-crop portfolio against elite-informed MELON/COW-SHEEP structures before heterogeneous population/default-environment testing.
