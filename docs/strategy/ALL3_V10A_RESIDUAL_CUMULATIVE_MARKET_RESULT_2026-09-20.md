# ALL3 V10A Residual Cumulative Market Upper Bound — Result — 2026-09-20

Workflow: **`35518110487`**  
Head: `291442310a0397da0d7a670a5b20954b8450c06b`

Decision: **`V10A_RESIDUAL_MARKET_UPPER_BOUND_CLOSED`**

Mechanical:
- PASS;
- 4/4 frozen ALL3 hard contexts;
- 7 modes per context;
- 28/28 mode-context runs;
- failures 0;
- physical fallback turns 0 in every mode.

## Results

BASE:
- mean score delta 0;
- mean margin delta 0.

FULL_ALL:
- positive-score contexts: **0/4**;
- mean score delta: **0**;
- mean margin delta: **-205.25**;
- mean substitutions: 59.25.

FULL_W2PLUS:
- positive-score contexts: **0/4**;
- mean score delta: **0**;
- mean margin delta: **-191.5**;
- mean substitutions: 55.25.

STRUCT_W2PLUS:
- positive-score contexts: **0/4**;
- mean score delta: **0**;
- mean margin delta: **-191.5**.

INSERT_W2PLUS:
- positive-score contexts: **0/4**;
- mean score delta: **0**;
- mean margin delta: **-191.5**.

QTY_W2PLUS:
- score/margin delta exactly 0.

REORDER_W2PLUS:
- score/margin delta exactly 0.

## Binding interpretation

The residual V48 market behavior that remains after ALL3/LQ2 has **no cumulative W/L upper-bound headroom** on the frozen residual hard contexts.

This closes:
- local V48 market imitation;
- one-turn structural residual imitation;
- long-horizon residual V48 market imitation;
- further V48-derived market threshold/order/quantity tuning as the next option source.

The historical V4B/V4D headroom was substantially captured by the mechanisms already absorbed into ALL3, especially O-LQ2. Applying V48's remaining market behavior now is neutral-to-harmful.

Next discovery must come from a different population/mechanism source rather than more V48 residual imitation.

No Kaggle submission is authorized.
