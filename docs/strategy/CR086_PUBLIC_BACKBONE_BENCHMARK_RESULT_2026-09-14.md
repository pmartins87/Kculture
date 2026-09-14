# CR086 public-backbone benchmark result — 2026-09-14

## Decision

**CLOSE_DIRECT_PUBLIC_BACKBONE_ADOPTION_MOVE_TO_CLEANROOM_MARKET_VALUE_LAYER**

The frozen public-backbone characterization run `34798209070` completed cleanly under `kaggle-environments==1.32.7`, fresh spawned package processes, both seats, 16 fresh seeds (`master_seed=9160861`) and exact CR083 as the incumbent.

The predeclared promising screen required all of:

- exact 32 games / 16 fresh seeds;
- zero execution errors and zero non-DONE games;
- score rate >= 0.5625 versus CR083;
- positive mean terminal-money margin.

None of the three executable public agents passed. No retuning of the public packages is authorized from this screen.

## Exact results

| Public agent | Frozen package SHA-256 | W-L-T vs CR083 | Score rate | Mean margin | Decision |
|---|---|---:|---:|---:|---|
| `shape_shop_top10` | `fa9e7eb1a0174a1bf292fb4d47bd209defed929758214d3506e050a68ee5f98f` | **0-32-0** | **0.0000** | **-9416.34375** | `BENCHMARK_FAIL_NO_RETUNING` |
| `adaptive_market_hysteresis` | `8dc512911c0173483211314f63cbf1d7e460cad33dfbc02f0f77d023f6d809fe` | **0-32-0** | **0.0000** | **-10710.0** | `BENCHMARK_FAIL_NO_RETUNING` |
| `farming_score_v3` | `5cde13b09e9506f24b2f5df05719b597fe07ebbb6dead7da12894beda203e419` | **0-32-0** | **0.0000** | **-8996.1875** | `BENCHMARK_FAIL_NO_RETUNING` |

All three rows had zero execution errors and zero non-DONE games, and each lost 16/16 from each candidate seat. The failure is therefore strategic under this exact local population test, not an execution artifact.

Artifacts from run `34798209070`:

- `shape_shop_top10`: artifact `10330736808`;
- `adaptive_market_hysteresis`: artifact `10330522723`;
- `farming_score_v3`: artifact `10329714876`.

## Interpretation

1. A high displayed/public Kaggriculture rating does **not** imply dominance over the current CR083 exact-local backbone.
2. CR083 is extremely strong against these route/heuristic public agents in direct paired H2H, yet its hosted rating has historically been far below the ~3000 frontier. This widens, rather than closes, the known **local-proxy vs hosted-population gap**.
3. Direct adoption of any of these three packages as the CR086 backbone is closed.
4. Their architectural mechanisms remain useful as public research evidence. In particular:
   - adaptive market hysteresis demonstrates temporal public-flow memory, reserve and tranche ideas;
   - shape-shop demonstrates structural production adaptation and capacity activation;
   - farming-score demonstrates budget guarding.
5. The independently validated CR086 opponent-private-inventory estimator remains the strongest new representation result. It should now feed a **clean-room economic value layer**, not a third-party backbone.

## Binding next direction

CR086 must be our own policy architecture around an explicit economic quantity. Do not tune public agents to beat CR083 and do not action-clone their behavior.

Priority research question:

> Can estimated latent opponent supply improve the timing/quantity/value of premium-product market decisions under the official market mechanics, while preserving CR083's strong physical backbone?

Before any candidate is built, audit the exact official market transition/price mechanics and CR083's existing SELL logic. The next protocol must derive a value rule from mechanics rather than fit another arbitrary replay threshold.

No hosted submission is authorized by this result.
