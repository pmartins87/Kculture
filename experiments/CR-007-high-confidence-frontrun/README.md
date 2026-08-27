# CR-007 — High-confidence opponent-aware front-running

Status: **COMPLETE / PASS**

## Question

CR-004 and CR-005 proved that opponent-public state predicts near-future economic behavior. CR-006 found substantial gross economic headroom but failed because a low 0.20 trigger created too many false positives. Can thresholds selected **without using the final test day** isolate only high-confidence situations that retain positive economic value?

## Frozen split

- model calibration train: 2026-08-23 and 2026-08-24;
- threshold-selection day: 2026-08-25;
- final model train: 2026-08-23..25;
- strict test: 2026-08-26;
- top 20 complete official episodes/day;
- identity-free public-state features only;
- same four-turn horizon and model family as CR-005.

## Threshold selection

For each CARROT/TOMATO/STRAWBERRY/MELON forecast, thresholds 0.20..0.90 in 0.05 increments were scanned using **only Aug-25**. A product was enabled only if the calibration threshold had >=20 stock-eligible triggers, precision >=0.55 and mean isolated net proxy >=$5/trigger.

## Canonical result

GitHub Actions run **33093144911 — SUCCESS**. Artifact **9655430101**, ZIP digest **SHA-256 `78562629ae026c5b83ab391f01576340c442be62a67ef66dda40eb947491ed4e`**.

Calibration enabled exactly two products:

- **CARROT threshold 0.90**;
- **STRAWBERRY threshold 0.85**.

TOMATO and MELON were disabled before the final test because they did not satisfy the frozen calibration support/value rule.

Strict Aug-26 test:

- total triggers: **257**;
- true positives: **250**;
- overall precision: **0.97276**;
- gross front-run headroom: **$46,021**;
- false-positive regret proxy: **$33**;
- net proxy: **+$45,988**;
- mean net proxy: **+$178.94/trigger**;
- headroom/regret ratio: **1394.58**.

Per enabled product:

- CARROT: 21 triggers, 18 true positives, **85.7% precision**, net **+$1,124**, mean +$53.52/trigger;
- STRAWBERRY: 236 triggers, 232 true positives, **98.3% precision**, net **+$44,864**, mean +$190.10/trigger.

Every predeclared final gate passed.

## Decision

**PASS for causal agent testing, not for hosted submission.** The high-confidence signal is strong enough to embed in a minimal identity-free wrapper and test with actual market trajectory changes. CR-008 performs that causal test.

The intended deployment behavior is selective: preserve the robust base unless the public opponent state produces one of the two calibrated high-confidence signals. No opponent name, team, agent, submission or episode identity is used.

Tool: `tools/cr007_high_confidence_frontrun.py`.
