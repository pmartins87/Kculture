# KEXP-20260826-019 — live-meta late demand response

Status: **PREDECLARED / OBSERVATIONAL / NO POLICY PROMOTION**

## Prize-first question

The first hosted Kculture agent is valid but has fallen to a displayed rating of 135.7, while the frozen local panel is 81-15. KEXP-018 showed that the current high-Elo live meta is much more diverse than the three fixed public benchmarks and that top winners visibly rotate into carrots/tomatoes under the rebalanced scarcity market.

This study asks a narrow question before any R4D implementation:

> Once all eight public shop instances are visible, is late crop allocation strongly associated with public demand intensity and winning behavior in the current high-Elo ladder?

## Source

Official public Kaggle datasets only:

- `kaggle/kaggriculture-episodes-index`;
- latest available daily episode dataset unless an exact date is passed;
- top 20 episodes by `avg_score` for this first study.

No competition credentials, private code, validation seeds or held-out seeds are used.

## Measurement boundary

At step 600 / day 25, record the complete public shop multiset and compute per-product shop-demand weights using the official shop consumption rule (single-product shops count double per tick). For both players in every selected episode record:

- terminal W/L and money;
- BUY_SEED quantities during steps 600-671;
- SELL quantities during 600-718 and 696-718;
- demand intensity for WHEAT/CARROT/TOMATO/STRAWBERRY/MELON/EGG/MILK/WOOL;
- team name for descriptive stratification only.

The deployment policy, if one is later tested, may use only legal public state such as unlocked shops and current prices. Team identity, episode ID and seed ID are forbidden deployment features.

## Why this is higher priority than the macro solver

KEXP-017 proved that perfect ex-post selection among the three existing COK route branches moves 81-15 only to 83-13. The current route set therefore has low solver headroom.

KEXP-018 and the frozen engine instead expose a structural opportunity that the fixed COK route family largely misses:

- CARROT has a 2-day first yield / 3-day max-yield horizon, making it suitable for a day-24/25 late pivot;
- CARROT and TOMATO now use the official `hinge` scarcity curve;
- COK largely commits its strategic route from the first three shops, while eight shop instances are public by late season;
- top live winners buy substantially more late CARROT seed than top live losers in the initial KEXP-018 sample.

## Decision rule

This study does **not** promote code. It can only justify a bounded development candidate if:

1. the demand→crop-response relationship is mechanically coherent with the frozen engine;
2. the signal is not merely one team identity proxy;
3. a proposed candidate can be expressed using legal public observables;
4. it can be tested on development across multiple opponent families before any fresh validation access.

If the relationship is weak/confounded, reject the late crop-pivot hypothesis and continue searching.

## Reproducibility

Tool: `tools/live_meta_demand_response.py`
Workflow: `.github/workflows/live-meta-demand-response.yml`
Actions run: `33019276166` (first run, pending at predeclaration time).
