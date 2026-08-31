# CR024A guarded top19 — Stage B result

Run: GitHub Actions `33349303944`
Frozen workflow commit: `eb1d95c9130c7e732cc15326fd4a31e9048b61b4`

## Mechanical result

- 7 exact reproducible opponents
- 12 untouched raw Stage-B seeds
- both seats
- 168/168 paired rows complete
- 0 errors
- adaptive-reserved seeds untouched
- held-out seeds untouched

Mechanical gate: **PASS**.

## Paired W/L results versus frozen CR008

| Arm | Favorable | Unfavorable | Net | Total score |
|---|---:|---:|---:|---:|
| CR008 | — | — | — | 134.0 |
| raw top19 | 32 | 6 | +26 | 160.0 |
| CR024A guarded hybrid | 29 | 9 | +20 | 154.0 |

The raw top19 backbone therefore reproduced a large advantage on a seed block that had been untouched when the policy was frozen. The protective switch reduced that advantage and created more unfavorable conversions than raw top19.

## Frozen WOOL guard validation

Guard frozen before Stage B:

- clock 192
- `dmarket_price_wool >= 11.5`

Stage-B classification result:

- TP = 4
- FN = 2
- FP = 8
- TN = 154
- recall = 0.6666667
- false-positive rate = 0.0493827

The signal itself generalized enough to pass its classification thresholds. The failure was downstream: switching to the fallback did not reliably rescue the harmful top19 outcomes and created additional harms.

## Gate outcome

Passed:

- 168 rows / zero errors
- at least two raw harmful cases
- guard recall >= 0.50
- guard FPR <= 0.15
- hybrid net conversions >= +4
- hybrid total score >= CR008 +4

Failed:

- hybrid unfavorable conversions <= 60% of raw top19 unfavorable: **9 > allowed 4**
- hybrid total score no more than 2 below raw top19: **154 < 158 required**

Frozen decision:

`CR024A_STAGE_B_FAIL__BUILD_CONSENSUS_BACKBONE`

## Opponent-level signal

- `rayk`: raw top19 had 6 unfavorable conversions; guarded hybrid still had 6. The guard did not rescue the core harmful family.
- `boatlee`: raw top19 had 0 unfavorable; guarded hybrid introduced 2.
- `kaito_sparse`: raw top19 had 0 unfavorable; guarded hybrid introduced 1.
- `salem`: raw top19 retained 7 favorable / 0 unfavorable without guard activation.

## Interpretation

The major result is not that top19 failed. It is the opposite: **raw top19 generalized strongly** (+26 net conversions and +26 paired score points over CR008) on the untouched Stage-B block. The failed element is the clock-192 CR008 fallback controller.

This is consistent with the separately recorded R4B state-warming issue: the frozen CR024A candidate kept CR008 public-feature history warm but did not execute the stateful R4B/COK base before the switch, so its internal meta state entered cold. This may help explain why a correctly classified guard did not translate into successful rescue, but the current candidate must not be modified after the fact.

## Decision / next branch

Do **not** package or submit CR024A guarded hybrid.
Do **not** retune the 11.5 threshold on Stage B.
Do **not** submit CR008/CR011 calibration repeats.

Proceed to the already-frozen consensus/shrinkage branch:

1. preserve the strong top11/top19 common backbone;
2. use the already-open Stage-A causal component decomposition to identify whether the 35 `hands` disagreements or 50 `market` disagreements carry the gains/harms;
3. freeze a materially new consensus/shrinkage policy;
4. validate it on a fresh reserved seed block before package authorization.

Raw Stage B is now open development data for future diagnostics, but it is no longer eligible to serve as an untouched validation block for a successor designed after this result.
