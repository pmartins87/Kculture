# O-HV1 High-Value Stock Flush — Development Result — 2026-09-19

## Binding executions

Original matrix:
- workflow `35465868923`;
- 3 opponent shards + aggregate;
- SUCCESS.

Execution-equivalent parallel matrix:
- workflow `35466170602`;
- 12 opponent×configuration shards + aggregate;
- SUCCESS.

Both aggregates agree exactly.

## Verdict

**`O_HV1_DEV_CLOSE`**

No configuration is eligible.

Across 24 paired development contexts:

| Config | Rule | Mean score delta | Negative score contexts | Positive score contexts | Mean margin delta |
|---|---|---:|---:|---:|---:|
| D1 | step>=240, price>=175 | -0.58333 | 14 | 0 | -30,170.67 |
| D2 | step>=240, price>=200 | -0.58333 | 14 | 0 | -28,698.42 |
| D3 | step>=336, price>=175 | -0.58333 | 14 | 0 | -29,900.46 |
| D4 | step>=336, price>=200 | -0.58333 | 14 | 0 | -28,424.46 |

By opponent in the parallel aggregate:
- V47 mirror: every firing configuration averages **-0.75 score**;
- V48: every firing configuration averages **-0.75 score**;
- Ready Stock: every firing configuration averages **-0.25 score**.

The most conservative D4 still causes 14 score regressions and no score improvements.

## Interpretation

The hosted-loss observation was real:
ALL3 sometimes holds finished goods while current public price is high.

But the causal rule
“sell remaining finished-goods stock whenever current price is high”
is strongly harmful.

Current unit price is not sufficient to value inventory liquidation because retained stock interacts
with:
- later town/shop demand;
- future price path;
- inventory timing;
- subsequent production;
- action/market ordering;
- opponent market interaction.

The negative result is broad and mechanically valid. Do not rescue O-HV1 with:
- a higher threshold ladder;
- a later-step ladder;
- product-by-product threshold tuning;
- opponent-specific enablement.

## Binding consequence

Close O-HV1.

Continue hosted ALL3 unchanged.

Next research should target the physical/macro divergence seen in actual ALL3 losses, especially
price-aware crop composition, using legal current public prices and own seed state.

No Kaggle submission is authorized by O-HV1.
