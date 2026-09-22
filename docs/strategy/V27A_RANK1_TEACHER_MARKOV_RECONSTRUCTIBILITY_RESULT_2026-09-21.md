# V27A — Rank-1 teacher Markov reconstructibility result

Binding workflow: `35665757174`; aggregate job `106552747115`; final artifact `10669517185`; artifact digest `sha256:40db6fd90ca310f17e8b53456570d4d8f96f284cc6a101e502f41897bfa73585`.

## Mechanical result
PASS. Four shards completed successfully. 72 episodes, 1080 comparisons, zero failures, immutable V26A snapshot, no live Kaggle reacquisition.

## Binding decision
`V27A_HISTORY_AWARE_DISTILLATION_REQUIRED`.

Metrics:
- complete-action parity: 0.9222222222;
- MARKET parity: 0.9296296296;
- FARMER parity: 1.0;
- HANDS parity: 0.9925925926;
- disagreements: 84/1080;
- minimum checkpoint complete-action parity: 0.6666666667;
- minimum source complete-action parity: 0.8666666667.

The state-only Markov gate fails despite high aggregate parity. The disagreement is concentrated enough that state-only cloning would erase behavior that may be competitively material, especially MARKET behavior. Per the frozen V27A route, do not train a state-only clone.

## Route
Open exactly one explicit legal-history reconstructibility gate, V27B, before any behavioral distillation. V27B must use legal observation history only and must remain identity-free at candidate runtime.

Protocol: `docs/strategy/V27B_LEGAL_HISTORY_RECONSTRUCTIBILITY_PROTOCOL_2026-09-21.md`.

No Kaggle submission is authorized.