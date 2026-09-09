# CR071 initial-regime result — 2026-09-09

## Scope

This closes the preregistered step-0 CR053↔CR070A route-selector hypothesis.

Source run: GitHub Actions `34282785524` (`cr071-cr053-initial-regime-forensics-v1`).
Reference backend: `kaggle-environments==1.32.7`.
Corpus: 64 paired seeds × both seats = 128 official-reference games.

## H2H expansion

Across the full 128-game forensic corpus:

- CR053: 62 wins, 66 losses, 0 ties.
- CR070A: 66 wins, 62 losses, 0 ties.
- CR053 seat 0: 31-33.
- CR053 seat 1: 31-33.

This materially weakens the earlier impression that CR053 was a large CR070A-specific weakness. On the expanded sample the pair is near-even and perfectly seat-balanced.

## Preregistered step-0 selector test

The legal features were restricted before opening the fresh validation set to:

- shared step-0 market prices;
- shared step-0 market inventories;
- step-0 unlocked-shop count.

The first 32 paired seeds were discovery. The last 32 paired seeds were one-shot fresh validation. Only a one-variable, one-threshold stump was allowed.

### Result

All legal step-0 features are constant across seeds in this environment snapshot:

- prices are identical;
- inventories are identical;
- shop count is identical.

Consequently no two-branch causal route selector can exist at step 0 using the preregistered legal feature set.

The frozen stump degenerates to a constant choice and fails the minimum-branch and improvement gates. Decision: `NO_INITIAL_STUMP_SIGNAL`.

## Design implication

Do not tune or broaden the step-0 selector after seeing validation. That hypothesis is closed.

CR053 and CR070A diverge behaviorally before useful environment regime information is available, so whole-agent late switching remains unsafe. The next research line is behavioral trajectory decomposition: observe the exact official actions produced by the opaque CR053 and the inspectable CR070A, identify small structural blocks associated with wins, and test only prefix-compatible/local transplants against the full panel.

## Promotion policy remains unchanged

- Primary metric: seat-balanced W/L / score rate.
- Money margin: diagnostic only.
- Exact Kaggle reference is source of truth for local promotion.
- No Kaggle submission from this result alone.
