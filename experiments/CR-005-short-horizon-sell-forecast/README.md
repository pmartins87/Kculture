# CR-005 — Short-horizon opponent SELL forecast

Status: **FROZEN / READY TO RUN**

## Question

CR-004 proved that opponent-public state materially improves 24-turn forecasts of several economic actions. Can the same information predict the opponent's **imminent product sales** closely enough to support a market best response?

## Frozen targets

Primary targets:

- `SELL_CARROT`;
- `SELL_TOMATO`;
- `SELL_STRAWBERRY`;
- `SELL_MELON`.

These are the products for which CR-004 found positive opponent-information value, with especially large effects for CARROT and TOMATO.

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

## Eligibility

A target is eligible only with:

- >=100 positive and >=100 negative train samples;
- >=40 positive and >=40 negative test samples.

## Predeclared gate

`SHORT_HORIZON_SELL_SIGNAL_PASS` requires:

1. at least 2 eligible targets;
2. at least 2 eligible targets improve Brier score by >=10%;
3. median relative Brier improvement across eligible targets >=8%;
4. at least 2 eligible adaptive models have ROC-AUC >=0.85;
5. no more than 1 eligible target worsens Brier by >5%.

If this passes, proceed to CR-006 market best-response value tests. Prediction accuracy alone never authorizes promotion.

## Why four turns

The official market/town has important 4-turn cadence, and a four-turn warning is short enough to influence current/near-current liquidation while giving enough event support for temporal testing. A later CR may tighten to same-turn prediction if the value test proves that very short timing matters enough.

Tool: `tools/cr005_short_horizon_sell_forecast.py`.
