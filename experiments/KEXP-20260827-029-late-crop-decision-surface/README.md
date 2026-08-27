# KEXP-20260827-029 — late crop decision surface

Status: **COMPLETE / SIMPLE RULE REJECTED**

## Prize-first question

KEXP-022 established a longitudinal live-meta relationship between full public shop demand and late CARROT allocation. KEXP-023 found mechanically clean CARROT substitution windows in frozen R4B. KEXP-026 V3 proved R4B has zero truly-unreserved CARROT seed capacity there, so adaptation must deliberately reallocate purchases.

KEXP-029 tested whether the smallest public-state rule — CARROT demand plus current CARROT/WHEAT price relation — was enough to identify top-meta CARROT purchases.

## Frozen protocol

Official top-20 episodes for 2026-08-22..26. Training days were Aug-22..25; Aug-26 was strict temporal test. Winner seed-buy events in states 600..647 were paired with actions from frame `t+1`, using only public shop demand and current market prices.

Two compact rule families were searched:

1. `demand_carrot >= D AND price_carrot/price_wheat >= R`;
2. a demand-adjusted CARROT/WHEAT opportunity threshold.

Predeclared promotion gate: training precision >=0.75, Aug-26 predicted-positive support >=3, Aug-26 precision >=0.70.

## Canonical result

Actions run **`33041072381` — SUCCESS**.
Artifact **`9633951575`**, ZIP digest **SHA-256 `07bdbf2400b43ebdc714a3f0dc714998374aa35b7be7460c327706baf747981d`**.

Selected rule:

- family: demand + price;
- `demand_carrot >= 0`;
- `price_carrot / price_wheat >= 1.70`.

Training winners (Aug-22..25):

- predicted positive: 58;
- TP 58 / FP 0;
- precision **1.000**;
- recall **0.1648**;
- positives span Aug-23/24/25.

Strict Aug-26 winners:

- predicted positive: 15;
- TP 10 / FP 5;
- precision **0.6667**;
- recall **0.0971**.

All-player Aug-26 descriptive check: 20/25 predicted positives matched a CARROT buy (precision 0.80), but the predeclared winner temporal gate is the controlling result.

## Decision

**NO POLICY PROTOTYPE from this simple threshold.**

The gate failed because Aug-26 winner precision 0.6667 < 0.70. Do not tune the 1.70 threshold after seeing the temporal test.

Interpretation: CARROT demand and current relative price contain real signal but are insufficient to explain the top-meta choice. The next experiment, KEXP-031, adds legal economic/productive context and uses leave-one-day-out model selection before the untouched Aug-26 temporal test.

No validation or held-out seeds were accessed. Team/episode/seed identity remains forbidden as a deployable feature.
