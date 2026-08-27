# KEXP-20260827-033 — bounded final-day collector

Status: **RUNNING / DIAGNOSTIC RESULT ONLY / ORIGINAL WATER PREMISE INVALIDATED**

## Important mechanics correction after launch

KEXP-033 was launched under the same incomplete WATER premise as KEXP-032. KEXP-032 has since disproved it decisively.

There is no daily refresh after step 695, but **one-time crop WATER can still increase `yield_units` immediately when the WATER action executes inside its bonus window**. Therefore the statement that WATER cannot create product during 696..718 is false.

The KEXP-033 run is allowed to finish because its cross-family and direct results are still useful diagnostics. However **it is not promotable even if it happens to score well** until every WATER it suppresses is re-audited against the corrected marginal-value mechanic. KEXP-035 performs that audit.

PLANT is also not blanket terminally useless: a newly planted one-time crop begins with base `yield_units=1`, so a same-day plant/harvest path can in principle have economic value if routing and seed cost permit it. FEED/CARE remain different mechanics and should be evaluated separately rather than grouped with WATER/PLANT.

## Candidate as originally tested

`candidates/r4d_terminal_collector.py`

Frozen R4B is unchanged through step 695. During 696..718 the candidate attempts to solve a bounded collection/routing problem:

1. actors carrying sellable inventory route by Manhattan distance to the nearest official shed-access tile and DROP;
2. empty actors standing on positive `yield_units` HARVEST immediately;
3. empty actors standing on collectible fertilizer collect it;
4. remaining empty actors are greedily assigned to distinct positive-yield crop/animal tiles only when travel + HARVEST + return-to-shed + DROP all fit before step 718;
5. target priority is current public market value per required action, with gross value and shorter plans as tie-breakers;
6. when no feasible collection job exists, only already-useful base movement/HARVEST/DROP/COLLECT_FERTILIZER is preserved;
7. the original candidate suppresses terminal maintenance/investment actions, including WATER, using the now-invalid blanket premise;
8. on step 718 frozen R4B liquidation is recomputed after the planner's unit rewrite so same-turn DROPs are included in projected shed sales.

The route-planning pieces remain potentially useful. The blanket suppression pieces do not.

Official mechanics still valid for the routing subproblem:

- board movement has no blocking and locked tiles are passable;
- units may share cells;
- default 10×10 shed-access tiles are the four center cells, generalized from board size;
- terminal reward is bank money only.

No opponent/team/episode/seed identity is used.

Candidate blob: `dc01e2abba24d67e575344b1720a7991cb05772c`.  
Base R4B blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

## Original frozen development gate

The launched run uses all 16 development seeds in both seats against Kaito V27, Rayk V11 and Andrew V12, plus direct candidate-vs-R4B on the same 32 seat-seed games.

The original gate was:

- zero runtime/status errors;
- combined modern-panel W/L no worse than R4B's **81-15**;
- no opponent family loses more than one win versus its R4B reference;
- direct candidate-vs-R4B score rate >= **0.53125**;
- direct mean terminal delta > 0.

After the mechanics correction, passing those numerical gates would be **diagnostic only**, not sufficient for promotion. Any successor must preserve state-specific WATER with positive delivered marginal value, as established by KEXP-035.

No validation or held-out seeds are accessed.
