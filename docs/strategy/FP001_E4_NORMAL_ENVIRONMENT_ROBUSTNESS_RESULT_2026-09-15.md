# FP001 E4 — normal-environment robustness result

Date: 2026-09-15  
Run: `34869392514`  
Job: `104061255265`  
Conclusion: **STRONG PASS**

## Frozen comparison

- base: exact `COW5_DAILY` animal-only scheduler;
- candidate: exact E3 `M6S1` overlay — 6 MELON + 1 STRAWBERRY, one first-cost daily hand;
- default weeds and random three-day town-shop unlocks;
- 40 fresh seeds `69601..69640`, both seats;
- passive opponent; 720 steps; starting money 3000;
- exact `kaggle-environments==1.32.7`.

Crop occupancy changes the RNG stream used for later shop selection, so seed-level deltas are distributional contrasts, not a decomposition under identical realized shops.

## Result

| Metric | COW5_DAILY | M6S1 |
|---|---:|---:|
| mean final-bank delta | 36,810.8 | **46,405.3** |
| median | 38,609.5 | **48,594.5** |
| p10 | 25,030.2 | **33,000.8** |
| min | 14,302 | **28,923** |
| max | 48,619 | **57,639** |

Seed-level M6S1 minus base:

- mean **+9,594.5**;
- median **+8,643**;
- approximate CI95 **[+6,057.83, +13,131.17]**;
- signs **33 positive, 0 zero, 7 negative**;
- p10 gap **+7,970.6**;
- range `-13,819 .. +32,459`.

## Mechanical invariants

- zero engine/non-DONE failures;
- candidate COW survival **80/80 cases**;
- exact animal FEED/CARE/movement/MILK fingerprint **80/80**;
- full 36 MELON + 8 STRAWBERRY output **80/80**.

## Decision

Every frozen Strong-PASS condition fired. M6S1 is therefore a real, robust additive production module over COW5_DAILY, not a deterministic-town artifact.

This does **not** authorize a hosted submission. The next gate is the predeclared elite-macro transfer: port the same M6S1 workload onto fixed 3-COW/2-SHEEP and 2-COW/3-SHEEP compact DAILY-CARE backbones, compare them with the exact COW5 control, and preserve only mechanically sound/economically non-catastrophic mixed challengers for heterogeneous population testing.

No M5/M7/M8 or fertilizer-on-MELON retuning is authorized.
