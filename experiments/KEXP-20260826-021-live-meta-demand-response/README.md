# KEXP-20260826-021 — live-meta late demand response

Status: **COMPLETE / STRONG OBSERVATIONAL SUPPORT / NO POLICY PROMOTION YET**

> Renumbering note: this study was initially written under `KEXP-019`, but that identifier was already occupied by the earlier late-animal longitudinal study. `KEXP-021` is the canonical identity; the original path remains only as a historical alias.

## Prize-first question

The first hosted Kculture agent is valid but has fallen to a displayed rating of 135.7, while the frozen local panel is 81-15. KEXP-018 showed that the current high-Elo live meta is much more diverse than the three fixed public benchmarks and that top winners visibly rotate crops under the rebalanced scarcity market.

This study asked:

> Once all eight public shop instances are visible, is late crop allocation strongly associated with public demand intensity and winning behavior in the current high-Elo ladder?

## Source / run

Official public Kaggle datasets only:

- `kaggle/kaggriculture-episodes-index`;
- daily dataset `kaggle/kaggriculture-episodes-2026-08-25`;
- top 20 episodes by `avg_score` = 40 player-games.

Actions run: **`33019276166` — SUCCESS**.
Artifact: **`9625868747`**, ZIP SHA-256 `0a0c9028ce33b177b61a41fe4da691f6de6b7740c4729a0108ad4991e33dd821`.

No competition credentials, private code, validation seeds or held-out seeds were used.

## Measurement boundary

At step 600 / day 25, record the complete public shop multiset and compute per-product shop-demand weights using the official shop consumption rule (single-product shops count double per tick). For both players in every selected episode record:

- terminal W/L and money;
- BUY_SEED quantities during steps 600-671;
- SELL quantities during 600-718 and 696-718;
- demand intensity for WHEAT/CARROT/TOMATO/STRAWBERRY/MELON/EGG/MILK/WOOL;
- team name for descriptive stratification only.

The deployment policy, if one is later tested, may use only legal public state such as unlocked shops and current prices. Team identity, episode ID and seed ID are forbidden deployment features.

## Main result — CARROT is the standout late-horizon signal

Across all 40 player-games, CARROT demand weight versus CARROT seed purchases during 600-671 had Pearson correlation **+0.46156**.

Overall:

| Group | Mean CARROT seed buy 600-671 | Mean final-day CARROT sell 696-718 |
|---|---:|---:|
| Winners | **14.20** | **50.95** |
| Losers | **2.95** | **4.85** |

By public carrot-demand weight (`2 × PET_CAFE + FARMERS_MARKET`):

| Demand weight | Player-games | Winner mean seed buy | Loser mean seed buy | Winner mean final-day sell | Loser mean final-day sell |
|---:|---:|---:|---:|---:|---:|
| 0 | 2 | 0 | 0 | 0 | 0 |
| 1 | 10 | 4.4 | 0 | 7.8 | 0 |
| 2 | 8 | 11.75 | 1.75 | 36.0 | 4.75 |
| 3 | 4 | 12.0 | 4.5 | 64.5 | 7.0 |
| 4 | 10 | 21.0 | 5.0 | 73.6 | 2.8 |
| 5 | 2 | 31.0 | 4.0 | 78.0 | 11.0 |
| 7 | 2 | 24.0 | 8.0 | 144.0 | 30.0 |
| 10 | 2 | 31.0 | 6.0 | 117.0 | 9.0 |

The relationship is striking and mechanically coherent: CARROT has a 2-day first-yield horizon, its current scarcity curve is `hinge`, and by this point the full eight-shop multiset is public.

## Important confounder

The Aug-25 top-20 set contains only two teams:

- **Crop Dusta:** 20 games, 14 wins, mean CARROT seed buy 600-671 = **15.3**, WHEAT = 9.65;
- **Ryo Hasegawa:** 20 games, 6 wins, CARROT = **1.85**, WHEAT = 23.05.

Thus the same-day winner relationship is also strongly team-correlated. This prevents direct policy promotion from this sample alone.

## Secondary results

WHEAT shows the opposite descriptive pattern:

- demand→late-seed-buy Pearson only **+0.065**;
- winners buy mean **11.25** WHEAT seeds during 600-671;
- losers buy **21.45**;
- winners sell mean **72.05** WHEAT on the final day;
- losers sell **96.45**.

This is consistent with a possible late overcommitment to static wheat production while current winners pivot toward short-horizon carrot in carrot-demand regimes.

No player bought TOMATO, STRAWBERRY or MELON seeds during 600-671 in this sample. That is mechanically sensible: those crops have much longer first-yield horizons than CARROT and are poor candidates for a day-25 pivot. TOMATO final-day sales therefore come from earlier planting decisions and need a separate earlier-horizon study.

## Relationship to COK/R4B

The exact COK V8 route audit shows the base typically buys only **0-3 CARROT seeds** during 600-671 while buying roughly **28-32 WHEAT seeds**, depending on route. COK route choice is largely committed from the first three shop observations, so it does not explicitly exploit the complete eight-shop late demand state.

This is a larger structural gap than the previously tested terminal-sale completeness and existing-route macro selector.

## Decision

**Do not promote code yet.** KEXP-021 gives strong observational/mechanical support for a late public-demand-responsive CARROT pivot, but the two-team confounder is too large to ignore.

Next exact test is KEXP-022: repeat the same analysis over several preceding daily ladder datasets. A candidate is justified only if the signal survives the longitudinal/multi-team check.

## Reproducibility

Tool: `tools/live_meta_demand_response.py`
Workflow: `.github/workflows/live-meta-demand-response.yml`
Actions run: `33019276166`.
