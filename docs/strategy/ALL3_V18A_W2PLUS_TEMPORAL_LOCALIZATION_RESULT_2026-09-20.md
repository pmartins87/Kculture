# ALL3 V18A MARKET_W2PLUS Temporal Localization — Binding Result — 2026-09-20

Workflow: **`35547247595`**.

Decision: **`V18A_SINGLE_PARTITION_HEADROOM`**.

Selected mode: **`MARKET_P2_ONLY`**.

## Mechanical

- 24 hard contexts × 7 modes complete;
- failures: 0;
- BASE exact replay PASS;
- **MARKET_P123 exactly reproduced all 24 binding V14A MARKET_W2PLUS treatment scores and margins**;
- V14A replication mismatches: **0**.

Therefore the temporal decomposition is binding and interpretable.

## Frozen partitions

- P1: turns 336..463;
- **P2: turns 464..591**;
- P3: turns 592..718.

## Results

### P1 only
- positive-score contexts: 0/24;
- improved sources: 0;
- mean score delta: 0.0;
- mean margin delta: +128.6667.

### P2 only
- positive-score contexts: **14/24**;
- improved sources: **7**;
- negative-score contexts: **0**;
- mean score delta: **+0.5833333**;
- mean margin delta: **+1384.25**.

### P3 only
- positive-score contexts: 0/24;
- improved sources: 0;
- mean score delta: 0.0;
- mean margin delta: +353.0833.

### P1+P2
- positive-score contexts: **20/24**;
- improved sources: **10**;
- negative-score contexts: 0;
- mean score delta: **+0.8333333**;
- mean margin delta: **+1571.1667**.

### P2+P3
- positive-score contexts: **22/24**;
- improved sources: **10**;
- negative-score contexts: 0;
- mean score delta: **+0.9166667**;
- mean margin delta: **+1785.6667**.

### P1+P2+P3
- positive-score contexts: **18/24**;
- improved sources: 7;
- negative-score contexts: 0;
- mean score delta: **+0.75**;
- mean margin delta: **+1858.5**.

This exactly matches the V14A MARKET_W2PLUS binding aggregate.

## Binding interpretation

A single fixed temporal partition, **P2 (464..591)**, contains reusable W/L headroom by itself.

P1 and P3 individually do not flip W/L, although both show positive interaction when combined with P2.
The pre-registered specificity rule selects P2 rather than the stronger but broader P23/P12 combinations.

Therefore V18B is activated on **turns 464..591 only**.

V18B will not hand-select another individual market edit. It will distill a cumulative first-party market controller over the selected P2 scope using legal current-state features and source-held-out validation.

No Kaggle submission.
