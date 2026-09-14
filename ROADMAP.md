# ROADMAP — Kculture live plan

Updated: 2026-09-14

Objective: maximize probability of a prize-winning / top-10 Kaggriculture finish. Source of truth: branch `fix/kaggle-parity-v1`, `STATUS.md`, and frozen protocols.

## Invariants

1. Hosted/live evidence and exact-reference W/L both matter.
2. Submission allowance is a cap, not a quota.
3. Every candidate family gets a predeclared gate.
4. Invalid evaluations are quarantined.
5. No seed, team identity, EpisodeId, future state or opponent-private state as runtime features.
6. Authenticated Kaggle API is the default current-meta source.
7. Original final holdout remains sealed.
8. Do not tune failed architectures on spent validation evidence.
9. Strong CR071M/legacy H2H is necessary but not sufficient.
10. Hosted promotion requires independent high-strength-population evidence.
11. **Do not enter polling loops.**

## Closed architecture classes

CR078, CR079, CR080, CR081, CR082, CR084 and CR085 remain closed. Direct adoption/retuning of the three screened public backbones is also closed after the frozen CR086 characterization sweep.

## ACTIVE — CR083 hosted maturation

Frozen SHA `648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`; submission `56199767`.

Latest already-frozen checkpoint: CR083 `1660.3`, CR071M `1638.8`, lead `+21.5`, about 76 public episodes plus validation.

Do not poll again before the 100-public-episode maturity boundary unless another material decision requires it.

## CR086 Stage 1A — opponent-stock representation COMPLETE / PASS

Independent confirmation over 100,660 commodity-step observations:

- MAE `1.25005`;
- p95 `9`;
- interval coverage `0.969462`;
- `stock >= 10` accuracy `0.956338`.

Decision: `OPPONENT_INVENTORY_REPRESENTATION_FEASIBILITY_PASS`.

Implementation/evaluation: `tools/cr086_opponent_inventory_estimator_eval.py`.

This is representation evidence only. No arbitrary stock threshold policy is allowed from this result.

## CR086 Stage 1B/1C — public source acquisition and direct-backbone benchmark COMPLETE

Read-only acquisition run `34790801576`, artifact `10327672303`.

Frozen direct benchmark run `34798209070`, master `9160861`, 16 fresh seeds × both seats per agent:

- `shape_shop_top10` vs CR083: **0W-32L**, score `0.0`, mean margin `-9416.34375`;
- `adaptive_market_hysteresis` vs CR083: **0W-32L**, score `0.0`, mean margin `-10710.0`;
- `farming_score_v3` vs CR083: **0W-32L**, score `0.0`, mean margin `-8996.1875`.

All rows had zero errors/non-DONE and lost 16/16 from both seats.

Decision: **`CLOSE_DIRECT_PUBLIC_BACKBONE_ADOPTION_MOVE_TO_CLEANROOM_MARKET_VALUE_LAYER`**.

Result: `docs/strategy/CR086_PUBLIC_BACKBONE_BENCHMARK_RESULT_2026-09-14.md`.

Do not retune those packages to beat CR083. Their mechanisms remain public research inputs only.

## CR086 Stage 2 — clean-room latent-supply market value

This is now the active architecture track.

### 2A — official mechanics audit

Before changing policy, establish exactly:

1. price as a function of market inventory / relevant market state;
2. whether and how premium-product market inventory can fall/reset/recover;
3. ordering and lockstep semantics when both players SELL in the same turn;
4. what information about current market order is known before actions;
5. terminal value and floor-price behavior;
6. constraints on product carry/shed pressure that affect hold value.

### 2B — CR083 SELL audit

Map every current CR083 mechanism that can affect premium SELL decisions:

- base route SELLs;
- CR053-like market counterplay;
- sell clamp;
- room guard;
- dead-stock liquidation;
- any endgame liquidation behavior.

Quantify where opponent latent stock can alter the economic choice without modifying CR083's physical route.

### 2C — derive value, do not fit a threshold

Candidate objective must be a mechanics-derived quantity such as:

- cash at risk from opponent latent supply entering before our next sale;
- robust sell-now versus hold value under opponent-stock interval;
- probability-free worst/best-case saturation envelope;
- floor-risk / terminal-liquidation loss avoided;
- scarcity persistence when opponent upper stock is near zero.

Do **not** use a replay-fitted `stock > X => SELL` rule as CR086.

### 2D — frozen policy protocol

Only after the value equation is fixed:

- freeze exact CR083 base SHA;
- freeze exact estimator implementation;
- freeze exact action scope and value rule;
- prove no physical-route modifications if market-only;
- predeclare fresh Gate A master and thresholds;
- predeclare independent high-strength stress cohort;
- freeze seed firewall.

## Public architecture ideas retained clean-room

The direct packages failed, but three mechanisms remain useful design evidence:

- Adaptive Market Hysteresis: temporal public-flow memory, reserves, price gates, bounded sale tranches;
- Shape Shop TOP 10: demand-aligned production structure and latent-capacity activation;
- Farming Score V3: affordability/budget guard.

They are not candidate backbones and should not be copied/tuned wholesale.

## Hosted escalation rule

A CR086 hosted probe requires all:

1. fresh direct improvement versus incumbent CR083;
2. broad legacy-anchor guardrails;
3. frozen high-strength-population stress PASS;
4. runtime-legality PASS;
5. provenance/license PASS for any reused public code (clean-room mechanics ideas alone do not require code reuse).

No hosted slot is spent merely because a public notebook has a high displayed score.

## Frontier target

Latest already-frozen top-10 checkpoint is roughly 2965–3240. The objective is a ~3000-class architecture, not incremental improvement around a 1600-class incumbent.
