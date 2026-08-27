# CR-007 — High-confidence opponent-aware front-running

Status: **FROZEN / READY TO RUN**

## Question

CR-004 and CR-005 proved that opponent-public state predicts near-future economic behavior, including imminent CARROT/MELON sales. CR-006 found substantial gross economic headroom but failed because a low 0.20 trigger created too many false positives. Can thresholds selected **without using the final test day** isolate only high-confidence situations that retain positive economic value?

## Frozen split

- model calibration train: 2026-08-23 and 2026-08-24;
- threshold-selection day: 2026-08-25;
- final model train: 2026-08-23..25;
- strict test: 2026-08-26;
- top 20 complete official episodes/day;
- identity-free public-state features only;
- same four-turn horizon and model family as CR-005.

## Threshold selection

For each CARROT/TOMATO/STRAWBERRY/MELON forecast, scan thresholds 0.20..0.90 in 0.05 increments using **only Aug-25**. A product is enabled only if the threshold has:

- >=20 stock-eligible triggers;
- precision >=0.55;
- mean isolated net proxy >=$5/trigger.

Among eligible thresholds choose the highest mean net proxy, then precision, then support. The Aug-26 outcome is never used to choose or modify thresholds.

## Predeclared final gate

`HIGH_CONFIDENCE_FRONTRUN_PASS` requires all:

1. >=2 products enabled by calibration;
2. >=40 total Aug-26 triggers;
3. Aug-26 precision >=0.55;
4. mean Aug-26 net proxy >=$10/trigger;
5. headroom / false-positive-regret >=1.50;
6. >=2 products with >=10 triggers, precision >=0.55 and positive net value.

A PASS still does **not** authorize hosted submission. It authorizes an exact causal wrapper/simulation test in which early sells actually modify the market trajectory.

Tool: `tools/cr007_high_confidence_frontrun.py`.
