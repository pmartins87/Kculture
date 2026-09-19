# O-PC1 Profit-Dominant Crop Rotation — Development Result — 2026-09-19

## Binding executions

Original development:
- workflow `35469344185`;
- SUCCESS;
- three opponent blocks + aggregate.

Execution-equivalent parallel development:
- workflow `35469497089`;
- 12 opponent×seed shards + aggregate;
- same frozen seeds/rule/gate.

Both aggregates agree exactly.

## Verdict

**`O_PC1_DEV_CLOSE`**

Mechanical PASS:
- 24/24 paired contexts;
- zero failures;
- pre-trigger ALL3 parity;
- deterministic result reproduced by the parallel execution.

Aggregate:
- firing contexts: **6/24**;
- mean fire count: **3.25**;
- plant replacements: **54**;
- WHEAT seed units redirected: **54**;
- mean score delta: **-0.25**;
- negative-score contexts: **6**;
- positive-score contexts: **0**;
- mean margin delta: **-217.83**.

By opponent:
- V47 mirror: mean score delta **-0.25**, 2 negative / 0 positive;
- V48: **-0.25**, 2 negative / 0 positive;
- Ready Stock: **-0.25**, 2 negative / 0 positive.

## Interpretation

The rule was deliberately not threshold-fit.

It used the official full-cycle nominal comparison:

`4 * P_carrot - 20 > 6 * P_wheat - 10`.

This signal is descriptively enriched in current ALL3 hosted losses and matched a concrete hosted
opponent's WHEAT->CARROT switch.

Nevertheless the causal intervention is harmful on fresh exact-engine paired tests.

The failure therefore reinforces the CR090 lesson:

**a valid public economic signal is not automatically a valid physical action rule.**

Crop choice also depends on:
- existing seed stock;
- exact field age/layout;
- future price/town demand;
- watering/fertilizer/action capacity;
- harvest timing;
- liquidity and downstream programme state.

## Binding stopping rule

Close O-PC1.

Do not rescue it with:
- a CARROT/WHEAT price-ratio ladder;
- later/earlier start steps;
- fitted yield multipliers;
- hosted-opponent-specific activation.

The next research step is a bounded physical-action proposal oracle on top of exact ALL3. It must
search localized causal physical substitutions and then rewrite any recurring survivor first-party.

No Kaggle submission is authorized.
