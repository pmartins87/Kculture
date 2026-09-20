# ALL3 V16B O-LQ5F W2 Fertilizer Queue +2 — Binding Result — 2026-09-20

Workflow: **`35533510437`**.

Decision: **`V16B_LQ5F_MARGIN_ONLY_CLOSE`**.

## Mechanical

- 24/24 binding hard contexts;
- failures: 0;
- BASE exact replay PASS;
- fire coverage: **24/24 contexts**;
- source coverage: **10/10 unique source SHAs**;
- one fire per treatment episode;
- all fires in W2;
- exact +2 quantity-only mutation;
- no physical changes.

Observed treatment fire timing generalized to the first eligible W2 SELL FERTILIZER:
- turn 337 for most seed-78101 contexts;
- turn 336 for seed-78102 rank-14/rank-23 contexts.

## Strategic

- loss-to-win flips: **0**;
- positive-score contexts: **0**;
- negative-score contexts: **0**;
- mean score delta: **0.0**;
- mean margin delta: **+11.5**.

Every context had a positive paired margin improvement:
- most contexts: +13;
- rank-14/rank-23 subsets: +6 or +11.

## Binding interpretation

The W2 FERTILIZER +2 quantity signal is real but too weak to explain the V14A W/L headroom.

O-LQ5F is therefore closed under the frozen gate:
- do not activate V16C fresh validation;
- do not retune the increment;
- do not add exact-turn whitelists;
- do not select another single-product quantity family post-hoc under the same gate.

The next orthogonal hypothesis is **coordinated W2 market edits**: the full teacher market may gain W/L through a bundle of simultaneously co-occurring quantity/presence/structure changes rather than one isolated scalar edit.

No Kaggle submission.
