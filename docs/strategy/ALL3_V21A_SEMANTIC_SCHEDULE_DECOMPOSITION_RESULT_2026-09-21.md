# ALL3 V21A Semantic Schedule Decomposition — Binding Result — 2026-09-21

Workflow: **`35558880526`**  
Launch commit: `a815ee73dad8fda5f1c6a587417e22415120ec87`  
Aggregate artifact: `all3-v21a-semantic-decomposition`  
Artifact ID: `10622146329`  
Artifact digest: `sha256:4e15b39d10a10c57feb8f5b071ecea10d532f379a16b4b519ac036b93fd3810b`

Decision: **`V21A_SEMANTIC_NO_WL_HEADROOM`**.

## Mechanical binding

- 10/10 shards SUCCESS;
- 120/120 frozen contexts;
- shard failures: 0;
- aggregate mechanical PASS;
- BASE binding mismatches versus V20A: **0**;
- FULL binding mismatches versus V20A: **0**;
- exact V19A schedule semantics preserved;
- no fresh V21B validation seed consumed.

## Strategic result

No tested semantic treatment changed W/L in any of the 120 contexts.

| Mode | Positive score contexts | Negative score contexts | Mean score delta | Mean margin delta | W/L eligible |
|---|---:|---:|---:|---:|---|
| FULL | 0 | 0 | 0.0 | -742.75 | no |
| EMPTY_ONLY | 0 | 0 | 0.0 | -146.68333333333334 | no |
| SELL_ONLY | 0 | 0 | 0.0 | **+176.91666666666666** | no |
| BUY_ONLY | 0 | 0 | 0.0 | -7.625 | no |
| HIRE_ONLY | 0 | 0 | 0.0 | -683.4916666666667 | no |
| FULL_MINUS_EMPTY | 0 | 0 | 0.0 | -467.2 | no |
| FULL_MINUS_SELL | 0 | 0 | 0.0 | -767.1166666666667 | no |
| FULL_MINUS_BUY | 0 | 0 | 0.0 | -760.2583333333333 | no |
| FULL_MINUS_HIRE | 0 | 0 | 0.0 | -1.225 | no |

All non-BASE modes fired in 120/120 contexts.

`SELL_ONLY` improved mean terminal margin by about +176.92, but produced:
- 0 positive-score contexts;
- 0 positive-score seeds;
- 0 positive-score source SHAs.

Per the pre-registered gate, this is margin-only evidence and cannot be promoted.

## Binding interpretation

The four outcome-independent semantic categories do not recover reusable competition-relevant W/L headroom from the V19A consensus schedule on the 120-context V20A discovery population.

This closes the entire V19A-derived schedule family under the pre-registered stop rule:

- do not run V21B;
- do not run V21C;
- do not run V21D;
- do not submit any V19A/V21 semantic candidate;
- do not create V21A2/V21A3 post-hoc category combinations;
- do not search arbitrary turn subsets;
- do not retune category definitions or support thresholds;
- do not promote SELL_ONLY on margin alone;
- do not reopen V20 state-gate tuning.

## Next gate

Activate the independent **V22 fresh-current-frontier branch** defined in:

`docs/strategy/V21_STOP_RULE_AND_V22_FRESH_FRONTIER_BRANCH_2026-09-21.md`.

V22 starts from a new current public frontier census and exact ALL3 hard-population refresh using untouched seeds `79101..79106`.

No Kaggle submission is authorized by V21A.
