# ALL3 V25A Shadow Prefix State-Basin Horizon — Result — 2026-09-21

## Binding result

Workflow: **`35645830010`**  
Aggregate job: `106504353595`  
Final artifact: `10661899016`  
Digest: `sha256:e0d5190ffe6a8aded7b7df4610514bd616f04e9e744371bbc0b1aac9700b7d45`

Mechanical:
- 4/4 shards PASS;
- 93 hard contexts;
- 9 frozen horizons per context;
- **837/837 rows**;
- 0 failures;
- H=0 exactly reproduced V23B BASE;
- H=720 exactly reproduced V23B FULL_SHADOW.

Decision:

**`V25A_PERSISTENT_POLICY_REQUIRED`**

## Frozen horizon outcomes

No finite horizon in `[4,8,16,32,64,128,256]` produced a single score improvement.

| H | Improved score contexts | Mean score delta | Mean margin delta |
|---:|---:|---:|---:|
| 4 | 0/93 | 0.0 | -25.3226 |
| 8 | 0/93 | 0.0 | -6652.7204 |
| 16 | 0/93 | 0.0 | -6652.7204 |
| 32 | 0/93 | 0.0 | -6652.7204 |
| 64 | 0/93 | 0.0 | -3541.8172 |
| 128 | 0/93 | 0.0 | +18.8280 |
| 256 | 0/93 | 0.0 | -1943.1505 |

Only H=720 recovers the V23B FULL_SHADOW headroom:

- improved-score contexts: **81/93**;
- improved source SHAs: **9**;
- improved functional clusters: **6**;
- improved seeds: **5/5 hard seeds**;
- mean score delta: **+0.4838709677**;
- mean margin delta: **+3246.3226**;
- regressions: 0.

## Interpretation

The advantage cannot be transferred as:
- a compact option;
- an opening macro;
- a finite shadow prefix followed by ALL3;
- a MARKET-only patch;
- a PHYSICAL-only patch.

The stronger policies win because their **persistent whole-episode policy** keeps producing a different trajectory. Returning to ALL3 at any tested finite horizon <=256 erases all W/L improvement.

Per the frozen V25A router, this closes additive option mining around exact V47+ALL3.

Next:
**`V26A_FIRST_PARTY_BASE_ARCHITECTURE_BENCHMARK`**.

No Kaggle submission is authorized.
