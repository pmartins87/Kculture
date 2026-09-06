# CR039 — State-adaptive exit from rank5 lineage

## Why
CR038 proved that no single global temporal cut preserved the full CR035 rank5 W/L gain. The full rank5 reference remains +3 W/L versus CR029 (15/24 vs 12/24), but with a large paired-margin cost. That points to path dependence: entering rank5 at clock 24 matters, but some public game states may later justify exiting back to CR029.

## Frozen question
Keep CR035 exactly through clock 24. Jesse-classified games remain CR029. Keiz-classified games enter the complete rank5 lineage at clock 24. At one later horizon, a single public-state decision stump may either remain in rank5 or exit permanently to CR029.

## Discovery data
Only the already-open CR035/CR036 12-scenario panel is used. The instrumented rank5 replay must exactly reproduce frozen CR036 variant 7 before any rule is evaluated. Fresh validation and held-out data remain sealed.

## Horizons and features
Horizons: 48, 72, 96, 120, 144, 168, 192, 216.

Candidate features are intentionally small and public/causal: own/opponent money, money gap, own/opponent yield, yield gap, pasture/cow/sheep counts, shop count, and selected live market prices. No identity, episode id, rank, seed, team name, or submission metadata exists in the deployable rule.

## Two-stage screen
1. Probe the exact full rank5 lineage once on the open panel.
2. Use frozen CR036 paired outcomes only to rank simple one-feature exit stumps. Preserve all known favorable W/L conversions first, capture known regression second, then target negative paired-margin mass. Simulate only the top 8 unique exit signatures on the full 24-row open panel.

## Promotion gate
A rule may advance to fresh validation only if either:
- it keeps at least +3 W/L vs CR029, preserves >=4 favorable conversions, has <=1 unfavorable conversion, and improves mean paired margin by >2,000 versus the full rank5 reference; or
- it reaches at least +4 W/L with <=1 unfavorable conversion and improves paired margin versus full rank5.

No threshold is retuned after the full-panel screen. If none passes, retire this state-exit idea and evolve the rank5 lineage itself rather than continuing temporal splicing.
