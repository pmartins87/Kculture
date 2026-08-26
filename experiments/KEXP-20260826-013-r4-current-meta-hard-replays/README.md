# KEXP-20260826-013 — current-meta hard-regime replays

## Purpose

Determine whether the late-collapse mechanism observed against exact Kaito V27 also appears in the hard regimes exposed by exact Rayk V11 and Andrew V12.

This is **diagnostic-only**. No code is promoted from this experiment and no validation/held-out seed is touched.

## Frozen candidate

`R4B-market-only-validated-v1`

- path: `candidates/r4b_ablation_market_only.py`
- Git blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`

## Exact opponents

### Rayk V11

- `raykkretzschmar/kaggriculture-rank-your-agent/versions/11`
- `main.py` SHA-256 `adc61ab15b3b4016e49efe525f4906e6ae3bbb66c4ff29ab795ae09df9fbaa5f`
- benchmark-only; no derivative use.

### Andrew V12

- `andrewsokolovsky/kaggriculture-breaking-the-tie/versions/12`
- `main.py` SHA-256 `df4e899ad535754cf2ddbd3c16e48085916b0cd2baa5182a1a2cfc6a856abae5`
- Apache-2.0.

Every replay job reacquired the exact notebook version and failed closed on the hash above.

## Protocol and evidence

Actions run: `32927303182` — **SUCCESS**.

Rayk artifact:

- artifact ID `9591994623`
- artifact ZIP SHA-256 `f78a3f400b698749ce60d1664bce3315c702e10bedd3f91690400474834d343a`.

Andrew artifact:

- artifact ID `9592011224`
- artifact ZIP SHA-256 `343e2dce16452dc0cb2e57b2da933253b5402a44e1a656624b0ed03127feb103`.

Captured exactly the predeclared set:

- Rayk `163219477`, both orientations;
- Andrew `150614441`, `393297156`, `598340816`, `1422177419`, both orientations.

Total: **10 complete development replays**, eight losses and two wins for R4B. No validation or held-out seed opened.

## Main result: multi-family late collapse confirmed

Every one of the **eight captured loss orientations** is still an R4B money lead at step 672.

| Opponent | Seed | R4B seat | delta @672 | first non-positive step | terminal delta | 672→terminal swing |
|---|---:|---:|---:|---:|---:|---:|
| Rayk V11 | 163219477 | 0 | +3,097 | 717 | -1,188 | -4,285 |
| Rayk V11 | 163219477 | 1 | +3,097 | 717 | -1,188 | -4,285 |
| Andrew V12 | 1422177419 | 0 | +2,152 | 681 | -1,678 | -3,830 |
| Andrew V12 | 1422177419 | 1 | +1,705 | 681 | -2,328 | -4,033 |
| Andrew V12 | 150614441 | 0 | +2,980 | 719 | -224 | -3,204 |
| Andrew V12 | 393297156 | 0 | +856 | 681 | -2,533 | -3,389 |
| Andrew V12 | 393297156 | 1 | +856 | 681 | -2,533 | -3,389 |
| Andrew V12 | 598340816 | 1 | +1,317 | 673 | -2,590 | -3,907 |

Across these eight losses:

- mean step-672 lead: **+2,007.5**;
- mean terminal result: **-1,782.75**;
- mean relative collapse from step 672 to terminal: **-3,790.25**.

Split by in-game day:

- step 672→696 (day 28): mean relative swing **-2,123.5**;
- step 696→terminal (day 29): mean relative swing **-1,666.75**.

Therefore the loss mechanism is not confined to the final action, final hour, one seat, one seed, or one opponent family.

## Throughput observations

These are descriptive, not causal proof.

Across the eight losing orientations during **day 28 (steps 672–695)**:

| Action/market quantity | R4B avg | opponent avg |
|---|---:|---:|
| HIRE | 10.0 | 10.0 |
| HARVEST actions | 30.5 | 17.25 |
| DROP actions | **0.0** | 2.75 |
| PASS actions | 49.5 | 22.0 |
| WATER actions | 25.75 | 39.25 |
| WHEAT sold | 26.0 | 61.0 |
| MILK sold | 21.0 | 16.375 |
| FERTILIZER sold | 13.5 | 26.75 |

At step 695, immediately before the day-28 end-of-day auto-drop, R4B carries on average **92.5 total shed+actor items** versus **54.25** for the opponent in these losses. R4B shed itself is generally empty at this point; most stock is still carried by farmer/hands and becomes available for market sale only after end-of-day auto-drop.

During **day 29 (steps 696–718)**:

| Action/market quantity | R4B avg | opponent avg |
|---|---:|---:|
| HIRE | 8.0 | 9.75 |
| HARVEST actions | 18.5 | 29.75 |
| DROP actions | 8.0 | 13.75 |
| PASS actions | **70.25** | 14.0 |
| WATER actions | 9.5 | 24.75 |
| WHEAT sold | 78.5 | 142.5 |
| MILK sold | 25.5 | 47.0 |
| FERTILIZER sold | 9.0 | 16.75 |

Again, these comparisons do not mean copying opponent action counts is optimal. They identify a recurring structural difference: R4B harvests aggressively during day 28 but realizes less of that production through shed/market before the horizon closes, then uses materially less active labor/harvest/drop throughput on the final day.

## Engine constraints that matter

From the frozen official engine:

- unit actions execute before market orders;
- SELL can access shed stock, not arbitrary actor inventory;
- end-of-day actor inventories auto-drop to the shed **after** the day's final market phase;
- shed capacity is 100 and DROP silently discards actor inventory that cannot fit;
- farm hands reset each day and must be rehired;
- hire costs follow the low Fibonacci sequence `1,1,2,3,5,8,13,...`;
- step 718 terminal market sales affect final money; leftover inventory has no terminal value.

This makes late **harvest → carry → shed → sell** throughput and final-day labor utilization economically meaningful independent of any opponent code.

## Interpretation

KEXP-013 confirms the V27 diagnosis across two additional current public families:

1. **late-phase continuation is a real multi-family weakness** of the current R4B/COK route family;
2. the problem begins during day 28, before the terminal market-only controller;
3. final-day under-utilization amplifies it;
4. the strong midgame remains valuable — wholesale route replacement is still unsupported;
5. the next candidate should improve cash conversion late while preserving the successful opening/midgame.

The two captured wins (`150614441` Andrew seat 1 and `598340816` Andrew seat 0) also show large structural differences from the opponent, so raw action-count matching is explicitly rejected as a design method.

## R4D eligibility decision

**R4D IS NOW ELIGIBLE FOR A DEVELOPMENT PROTOTYPE**, subject to these constraints:

- no seed-ID or opponent-ID logic;
- legal-state observable only;
- preserve frozen R4B terminal market completeness;
- target the late cash-conversion/continuation pipeline, not the opening;
- begin with the smallest mechanically justified intervention;
- test on all 16 development seeds, both seats, against a diverse current-meta panel before any validation.

The first prototype should prioritize a low-risk late conversion mechanism before attempting a full new planner.

## Status

**COMPLETE — MULTI-FAMILY LATE-COLLAPSE HYPOTHESIS CONFIRMED.**
