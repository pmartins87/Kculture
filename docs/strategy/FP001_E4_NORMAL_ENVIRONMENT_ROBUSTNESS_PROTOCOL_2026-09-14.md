# FP001 E4 — normal-environment robustness gate

Date: 2026-09-14
Branch: `research/first-principles-economy-v1`

## Frozen candidate

Exactly the E3 winner:

- backbone: `COW5_DAILY`;
- crop block: `M6S1` = 6 MELON + 1 STRAWBERRY;
- at most one first-cost hand per day;
- MELON receives no fertilizer;
- STRAWBERRY uses H11 fertilizer ages 9 and 13;
- no post-E3 density, routing, timing, rescue or market retuning.

E3 deterministic-town gain was +9,533 final-bank units over animal-only while preserving the exact animal fingerprint.

## Why this gate exists

E3 was deliberately causal and removed stochastic shops/weeds. E4 asks whether the frozen production module remains valuable in the actual default environment, where:

- weeds spawn normally;
- shops unlock randomly every three days;
- crop occupancy changes the RNG stream used by later town-shop selection;
- market prices therefore vary substantially across seeds.

Because crop occupancy itself changes the later RNG path, a same-seed candidate/base pair is **not the same realized external environment**. Per-seed deltas may be shown descriptively, but they must not be interpreted as a controlled causal decomposition. Expected performance over the seed distribution is the target.

## Frozen evaluation

Policies:

1. exact `COW5_DAILY` animal-only base;
2. exact E3 `M6S1` overlay on the same backbone.

Environment:

- official default `weedSpawnChance`;
- official default `townShopUnlockInterval`;
- 720 steps;
- starting money 3000;
- passive opponent to isolate self-economics and environment robustness;
- exact `kaggle-environments==1.32.7`;
- 40 fresh episode seeds `69601..69640`;
- both seats for each seed/policy.

Primary statistical unit is one episode seed after averaging the two seat placements. Thus the initial gate contains 40 seed-level candidate outcomes and 40 seed-level base outcomes, each backed by both seats.

## Metrics

Record for base and M6S1:

- mean / median final-bank delta;
- p10 / p25 / p75 / p90, min and max;
- seed-level mean difference M6S1 minus BASE;
- standard error and approximate 95% CI for the mean seed-level difference;
- count of seeds with positive / zero / negative descriptive difference;
- candidate/base p10 difference;
- COW survival;
- main FEED/CARE/MILK fingerprint;
- crop units sold;
- HIRE count;
- engine/non-DONE failures.

## Frozen decision rule

### Strong PASS

Advance M6S1 if all are true:

- zero engine/non-DONE failures;
- 5/5 COW survival in every candidate case;
- animal output/control work shows no structural degradation;
- mean seed-level final-bank difference >= **+2,000**;
- median seed-level difference > 0;
- approximate 95% CI lower bound for mean difference > 0;
- candidate p10 final-bank is no worse than BASE p10 by more than 2,000.

### Strong FAIL

Close fixed M6S1 if either:

- mean seed-level difference <= 0; or
- median seed-level difference <= -2,000; or
- mechanical/animal failures reveal a structural incompatibility with the normal environment.

### INCONCLUSIVE

If neither Strong PASS nor Strong FAIL fires, do **one** sample-size extension only, to 96 total fresh seeds, with candidate bytes and protocol unchanged. No parameter retuning is permitted between samples.

## After PASS

Do not submit hosted yet. The next integration gate must test whether the crop/labor module transfers into an elite-informed mixed-animal macro family, especially the CR087 recurring COW/SHEEP + MELON structures, and then against heterogeneous population representatives.

## Stop rule

No seed-specific patching. No M5/M7/M8 density ladder. No fertilizer-on-MELON tuning in this branch. A failure sends the project to the next architectural prior (mixed COW/SHEEP / elite macro), not back into post-hoc crop threshold search.
