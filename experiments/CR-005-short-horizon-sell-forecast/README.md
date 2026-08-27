# CR-005 — Short-horizon opponent SELL forecast

Status: **COMPLETE / SHORT_HORIZON_SELL_SIGNAL_PASS**

## Question

CR-004 proved that opponent-public state materially improves 24-turn forecasts of several economic actions. Can the same information predict the opponent's **imminent product sales** closely enough to support a market best response?

## Frozen targets

Primary targets:

- `SELL_CARROT`;
- `SELL_TOMATO`;
- `SELL_STRAWBERRY`;
- `SELL_MELON`.

## Data split

- train: 2026-08-23, 24, 25;
- strict temporal test: 2026-08-26;
- top 20 complete official episodes per day;
- both players;
- states 96..695, sampled every turn;
- prediction horizon: opponent performs the target SELL at least once during states `t..t+3`;
- action alignment: state `t` -> replay action frame `t+1`;
- no identity/seed/episode features.

## Models

Same fixed model family for both feature sets:

`DecisionTreeClassifier(max_depth=7, min_samples_leaf=40, random_state=20260827)`.

Baseline: environment + self-public state + 24-turn deltas.

Adaptive: same baseline plus opponent-public state, opponent 24-turn deltas and public gaps.

## Predeclared gate

`SHORT_HORIZON_SELL_SIGNAL_PASS` required:

1. at least 2 eligible targets;
2. at least 2 eligible targets improve Brier score by >=10%;
3. median relative Brier improvement across eligible targets >=8%;
4. at least 2 eligible adaptive models have ROC-AUC >=0.85;
5. no more than 1 eligible target worsens Brier by >5%.

## Canonical result

GitHub Actions run **33090163855 — SUCCESS**.  
Artifact **9654113569**, ZIP digest **SHA-256 `a055b11dd822cbebe2015e219dd09e1296c4b96255a7f1e2ad154929ecb4cf9f`**.

All frozen gate components passed.

- eligible targets: **4/4**;
- median relative Brier improvement from opponent-public features: **14.31%**;
- targets improving Brier by >=10%: **2**;
- adaptive ROC-AUC >=0.85: **3/4**;
- targets worsening Brier by >5%: **0**.

Per-target adaptive improvement / ROC-AUC:

- `SELL_MELON`: **+30.88%**, AUC **0.9779**;
- `SELL_CARROT`: **+21.41%**, AUC **0.9609**;
- `SELL_TOMATO`: **+7.21%**, AUC **0.9520**;
- `SELL_STRAWBERRY`: **+6.19%**, AUC **0.8485**.

For imminent CARROT sale, the strongest adaptive feature was the **24-turn change in opponent CARROT crop count** (`dopp_crop_carrot`). MELON similarly relied heavily on the change in opponent MELON crop count.

## Decision

**PASS.** Four-turn opponent SELL forecasts contain enough identity-free public-state signal to justify CR-006 market best-response value tests.

Prediction accuracy alone does not authorize a candidate or hosted submission. CR-006 must estimate whether acting on the forecast creates material economic headroom after market impact and false-positive opportunity cost; a later exact counterfactual/action-tape test is required before promotion.

Tool: `tools/cr005_short_horizon_sell_forecast.py`.
