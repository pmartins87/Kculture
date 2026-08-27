# KEXP-20260827-033 — bounded final-day collector

Status: **RUNNING / DEVELOPMENT CANDIDATE**

## Prize-first mechanism

The official engine performs its final daily production refresh after step 695. States 696..718 therefore contain a finite terminal collection problem: existing crop/animal product can still be harvested, carried product can still be dropped and sold, but WATER/FEED/CARE/PLANT/FERTILIZE cannot create any new product before terminal scoring.

Frozen R4B still spends roughly 10 WATER actions per game in this window and its recent controlled reports show materially fewer final-day DROPs / sold units than current top-meta winners. KEXP-032 tests the smallest WATER-only rewrite. KEXP-033 tests the higher-ceiling bounded planner directly, in parallel, without waiting for a micro-ablation to succeed.

## Candidate

`candidates/r4d_terminal_collector.py`

Frozen R4B is unchanged through step 695. During 696..718 the candidate solves only the remaining collection/routing subproblem:

1. actors carrying sellable inventory route by Manhattan distance to the nearest official shed-access tile and DROP;
2. empty actors standing on positive `yield_units` HARVEST immediately;
3. empty actors standing on collectible fertilizer collect it;
4. remaining empty actors are greedily assigned to distinct positive-yield crop/animal tiles only when travel + HARVEST + return-to-shed + DROP all fit before step 718;
5. target priority is current public market value per required action, with gross value and shorter plans as tie-breakers;
6. when no feasible collection job exists, only already-useful base movement/HARVEST/DROP/COLLECT_FERTILIZER is preserved; terminal maintenance/investment unit actions become PASS;
7. terminally useless seed/animal/product/land purchases are removed in this window, while SELL and HIRE are retained;
8. on step 718 frozen R4B liquidation is recomputed after the planner's unit rewrite so same-turn DROPs are included in projected shed sales.

Official mechanics used by the planner:

- board movement has no blocking and locked tiles are passable;
- units may share cells;
- default 10×10 shed-access tiles are the four center cells, generalized from board size;
- terminal reward is bank money only.

No opponent/team/episode/seed identity is used.

Candidate blob: `dc01e2abba24d67e575344b1720a7991cb05772c`.
Base R4B blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

## Frozen development gate

Run all 16 development seeds in both seats against Kaito V27, Rayk V11 and Andrew V12, plus direct candidate-vs-R4B on the same 32 seat-seed games.

Promotion to exploratory distribution testing requires:

- zero runtime/status errors;
- combined modern-panel W/L no worse than R4B's **81-15**;
- no opponent family loses more than one win versus its R4B reference;
- direct candidate-vs-R4B score rate >= **0.53125**;
- direct mean terminal delta > 0.

For **hosted calibration**, the bar is deliberately higher than this development gate: the terminal planner should show a clear rather than marginal direct advantage and preserve cross-family W/L, or combine with another independently supported adaptive mechanism before consuming a Kaggle calibration submission.

No validation or held-out seeds are accessed.
