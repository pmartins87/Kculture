# KEXP-20260827-029 — late crop decision surface

Status: **RUNNING / DIAGNOSTIC ONLY**

## Prize-first question

KEXP-022 established a longitudinal live-meta relationship between full public shop demand and late CARROT allocation. KEXP-023 found mechanically clean CARROT substitution windows in the frozen R4B tape. KEXP-026 V3 then proved that R4B has **zero truly unreserved CARROT seed capacity** in those windows across all 36 audited development/exploratory episodes.

Therefore a meaningful crop-response candidate must deliberately reallocate seed purchases rather than merely spend idle CARROT stock.

Before mutating the agent, this experiment asks the narrower question: **can a small, public-state rule using CARROT demand and the current CARROT/WHEAT market-price relationship identify states in which current top-meta winners actually buy CARROT seed?**

## Frozen protocol

Official high-Elo daily episode datasets only.

Training days:

- 2026-08-22;
- 2026-08-23;
- 2026-08-24;
- 2026-08-25.

Temporal test day:

- 2026-08-26.

For each date use the top 20 episodes by official `avg_score`. For each winning player, inspect states 600..647 where the next submitted action buys WHEAT and/or CARROT seed.

Replay alignment is explicit: **observation frame `t` is paired with action frame `t+1`**.

Legal public features only:

- full unlocked shop multiset;
- CARROT demand weight;
- WHEAT demand weight;
- current CARROT market price;
- current WHEAT market price;
- CARROT/WHEAT price ratio;
- demand-adjusted opportunity index.

Team, episode and seed identity are retained only for research provenance and are forbidden as deployable features.

The binary target is whether the successful player buys a positive quantity of CARROT seed at that event.

## Rule search

Two compact interpretable families are searched on the four training days only:

1. `demand_carrot >= D AND price_carrot/price_wheat >= R`;
2. `((demand_carrot+0.5)/(demand_wheat+0.5)) * price_ratio >= Q`.

A training rule is eligible for selection only with at least 12 predicted-positive winner events spanning at least 3 training dates. Selection prioritizes precision, then recall, then support.

## Predeclared gate

The selected rule becomes eligible for a controlled R4D crop-response prototype only if:

- training winner precision >= **0.75**;
- Aug-26 winner predicted-positive support >= **3** events;
- Aug-26 winner precision >= **0.70**.

Passing this gate does **not** authorize validation or Kaggle submission. It only authorizes one bounded development candidate that reallocates a small number of existing late WHEAT seed-buy/plant slots to CARROT inside KEXP-023's mechanically clean subwindows.

If the gate fails, do not force a threshold. Move to a richer state controller/value model instead.

No validation or held-out seeds are accessed.
