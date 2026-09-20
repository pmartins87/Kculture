# ALL3 V14A Current-Frontier Domain Upper Bound — Binding Result — 2026-09-20

Binding mechanical-completion workflow: **`35526276641`**.

Decision: **`V14A_MARKET_DOMAIN_HEADROOM`**.

## Mechanical completeness

The original parallel workflow `35525689199` produced 126/144 valid mode-context rows and three acquisition-only HTTP 429 failures:
- `v13c_hard_14`;
- `v13c_hard_16`;
- `v13c_hard_18`.

Workflow `35526276641` reran exactly those three missing contexts in all six pre-registered modes and verified the complete:
- 24 hard contexts;
- 6 modes;
- **144 unique context-mode rows**.

No strategic population, mode, threshold, or decision rule changed.

## Binding domain result

### BASE
- improved-score contexts: 0/24;
- mean score delta: 0;
- mean margin delta: 0.

### MARKET_ALL
- improved-score contexts: **12/24**;
- improved unique source SHAs: **5**;
- mean score delta: **+0.50**;
- mean margin delta: **+1812.83**;
- regressed-score contexts: **0**.

### MARKET_W2PLUS
- improved-score contexts: **18/24**;
- improved unique source SHAs: **7**;
- mean score delta: **+0.75**;
- mean margin delta: **+1858.50**;
- regressed-score contexts: **0**.

### PHYSICAL_ALL
- improved-score contexts: **0/24**;
- mean score delta: **0**;
- mean margin delta: **-113.42**.

### PHYSICAL_W2PLUS
- improved-score contexts: **0/24**;
- mean score delta: **0**;
- mean margin delta: **-265.33**.

### FULL_ALL
- improved-score contexts: **24/24**;
- improved unique sources: **10**;
- mean score delta: **+0.50**;
- mean margin delta: **+1364.75**.

The FULL shadow ceiling produced ties from the original losses in these paired self-teacher contexts; it is an offline ceiling/control only.

## Binding interpretation

The recoverable W/L headroom in the current hard-context population is overwhelmingly a **market-domain** effect.

The evidence is especially strong for the post-turn-336 market behavior:
- 18/24 loss-to-win flips;
- 7 source families;
- zero W/L regressions.

Physical/farm action substitution does not carry reusable W/L headroom in this population.

Therefore:
- activate the pre-registered **V14B MARKET phenotype branch**;
- do not reopen generic physical/macro imitation;
- do not copy complete public opponent policies;
- do not use opponent identity as a runtime feature.

V14B must compress recurrent market differences into legal, opponent-independent phenotypes before any new first-party option rule is created.

No Kaggle submission is authorized.
