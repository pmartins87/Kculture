# Hosted calibration — 2026-08-29

This file freezes the Kaggle UI snapshot observed on 2026-08-29. Kaggriculture ratings drift as episodes accumulate, so these are calibration snapshots, not permanent scores.

## Valid hosted arms

| Arm | Submission ID | Observed score | Role |
|---|---:|---:|---|
| R4B_A | prior frozen control | 205.9 | opening temporal control |
| CR008 adaptive append | fixed hosted package | 1705.6 | adaptation arm |
| CR011 adaptive early | fixed hosted package | 1723.3 | queue-position arm |
| R4B_B | 55868963 | 188.4 | closing temporal control; byte-identical to R4B_A |
| Kaito V43 public reference | 55868969 | 1211.7 | same-window public high-score architecture reference |

Two earlier CR008/CR011 uploads failed before evaluation and did not consume valid daily slots in the Kaggle UI.

## Frozen interpretation

- R4B temporal bracket: `205.9 - 188.4 = 17.5` points.
- R4B midpoint: `197.15`.
- CR008 vs R4B midpoint: `+1508.45`.
- CR011 vs R4B midpoint: `+1526.15`.
- CR011 vs CR008: `+17.7`, essentially the same magnitude as the 17.5-point temporal control drift.
- Kaito V43 vs R4B midpoint: `+1014.55`; Kaito is materially stronger than R4B in the same window, but below CR008/CR011 in this snapshot.

Direct hosted evidence therefore establishes a very large value for the high-confidence opponent-aware adaptive-sale mechanism. It does **not** establish a hosted advantage for early queue placement over append placement.

Local causal decomposition CR-014B independently shows that the adaptation itself caused no W/L flips in the five critical cases, while early queue placement caused four catastrophic W->L flips and one favorable L->W flip. Because the hosted CR011-minus-CR008 difference is noise-scale, **CR008 append adaptation is the canonical hosted baseline after this calibration**.

## Candidate decisions

- **CR008:** canonical hosted adaptive baseline.
- **CR011:** retain as causal research arm; do not promote solely from the +17.7 snapshot.
- **CR015:** validated on 432 fresh pairs, 2 favorable / 0 unfavorable W/L changes vs R4B, package parity and official entrypoint PASS; next hosted-eligible candidate.
- **CR020:** rejected after Stage A. 216/216 mechanical PASS but mean relative gain `-70.84` vs CR015; no Stage B and no hosted slot.
- **CR016:** opens a production-demand architecture line. High-price demanded states with no self producer occurred in 100% of TOMATO and EGG cases measured; TOMATO is the first minimal-response target.

## Submission policy after the next daily reset

Use fresh CR008 controls around materially different validated arms. Provisional design:

1. CR008_A exact repeat;
2. CR015 fixed;
3. CR021 only if it passes its preregistered fresh gate unchanged;
4. CR008_B exact repeat;
5. one separately justified information arm, selected before partial scores can bias interpretation.

CR020 is ineligible. CR011 is not worth a slot merely to chase a noise-scale difference.

**Held-out remains 32/32 sealed.**
