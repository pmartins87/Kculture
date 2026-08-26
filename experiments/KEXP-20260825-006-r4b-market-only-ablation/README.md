# KEXP-20260825-006 — R4B market-only terminal ablation

## Result

The market-only candidate keeps all physical R4A actions unchanged and modifies only final-step market liquidation.

GitHub Actions run `32915111893` tested source commit `148cc81fed390fd75c0cba00ceb779efaa17a46f`; candidate Git blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

| Matchup | W-L-T | Score rate | Mean delta |
|---|---:|---:|---:|
| Market-only vs Seyamalam V21 | 16-0-0 | 1.0000 | +22,541.500 |
| Market-only vs R4A | 5-3-8 | 0.5625 | +12.000 |
| Full R4B vs market-only | 5-11-0 | 0.3125 | -3.125 |

All 48 executions finished with zero runtime errors. The result isolates final sale completeness as the useful component and extra terminal `DROP` replacement as harmful on this development panel.

Artifacts from run `32915111893`:
- vs R4A: `9587953165`, SHA-256 `ef0b9a89f364176fb7fabe77561fb79bcc3bb6a3564b08d0c68e4e37b239f15b`;
- vs Seyamalam: `9588135603`, SHA-256 `ef9ceb2d92f40ff87ea79b9ab3abb0bf38e3ffd7f248753c8d61eed736201a50`;
- full R4B vs market-only: `9588042346`, SHA-256 `820ef27b8ad8c87d78f1b9bcd4f2501cdfbf949d233c32b052cb157b9eac52f1`.

## Decision

**DEVELOPMENT SCREEN PASS.** Freeze this exact candidate for `KEXP-20260825-007-r4b-market-only-validation`. Validation will use all 16 validation seeds, both seats. Held-out remains sealed. This is not yet an R4 promotion.
