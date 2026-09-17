# Native Teacher Bootstrap V0 Result — 2026-09-17

## Status

PASS as an infrastructure/search gate.

This is **not** evidence of hosted Kaggle rating. It proves that the exact native arena can search a 32-dimensional adaptive controller at high throughput and find a controller that generalizes materially better than the bootstrap baseline to fresh seeds inside the native opponent family.

## Measured result

Bootstrap search:
- generations: 4
- population: 96
- searched candidates: 384
- total exact episodes: 28,944
- wall time: 5.66 s
- search throughput: roughly 5,776–5,905 episodes/s across generations

Fresh holdout:
- seeds: 12
- final league size: 11
- games/candidate: 264
- baseline win rate: 0.4015
- champion win rate: 0.8712
- baseline mean margin: -5,471.6
- champion mean margin: +21,131.0
- baseline mean bank: 21,462.0
- champion mean bank: 42,473.7
- baseline worst margin: -44,515
- champion worst margin: -20,231
- baseline dead actions/game: 42.33
- champion dead actions/game: 4.16
- baseline hand-pass turns/game: 128.29
- champion hand-pass turns/game: 23.06
- baseline dry plants/game: 25.33
- champion dry plants/game: 10.06
- holdout objective delta: +1.7878

The champion is not simply minimizing telemetry: escaped animals were slightly worse than baseline (8.996 vs 8.008), while win rate, bank, margin and most mechanical-loss indicators improved strongly.

## Structural interpretation

The search found a materially different economy rather than merely nudging the seed prior. Approximate decoded targets from the champion vector include:
- cows: ~5
- sheep: ~4
- geese: ~0
- wheat tiles: ~7
- tomato tiles: ~3
- strawberry tiles: ~1
- melon tiles: ~2
- hands: ~6
- land target: ~1 quadrant
- cash reserve: ~391
- stronger opponent-pressure sensitivity
- aggressive early fertilizer liquidation
- later terminal transition than the baseline

This broadly agrees with prior evidence that livestock + care + wheat/feed are central, but the tomato allocation and low fertilizer hold threshold emerged from search rather than being hard-coded as a named macro plan.

## Limitation discovered

The current opponent bank contains only strategies represented by the same 32-parameter controller family. Therefore the 87.1% holdout win rate can still reflect family-specific overfitting.

The next gate must inject historical strong behaviours that are outside the controller family. The seven frozen public replay tapes collected in CR089 are the first anchor because previous experiments established them as a difficult benchmark for the old fixed strategies.

## Next stage

Native Teacher V1 adds exact replay-tape evaluation in C++ and a hybrid CEM objective:
- 50% adaptive parametric league
- 50% frozen top replay family
- explicit worst-tape robustness term
- fresh train/holdout seeds
- reuse of the already searched bootstrap candidates

This remains a short bridge. The fixed 32-vector is not the final solver. Its role is to produce a stronger seed controller before state-conditioned suffix search / policy-value distillation.
