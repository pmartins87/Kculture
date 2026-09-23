# V28J — Bounded Legal-History Residual-Risk Identifiability Protocol — 2026-09-23

## Status

PRE-REGISTERED after the binding V28I decision and **before any V28J outcome is observed**.

V28I mechanically passed but failed its frozen single-state acceptance gate because source-held-out precision/specificity were insufficient. V28J implements exactly the pre-registered V28I fallback: bounded legal-history/stateful phenotype discovery inside the V28H explanatory window.

V28J is an identifiability gate only. It cannot mutate ALL3 or Kaggle slots.

## Binding inputs and population

Use only immutable artifacts from V28F `35807910104`, V28G `35812527508`, V28H-R2 `35813287407`, and the binding V28I result `35818084144`.

Replay all **144** V28F ALL3 contexts: 12 immutable source SHAs × seeds `80401..80406` × both seats. Every replay must exactly reproduce V28F ALL3 terminal score and margin. Any mismatch is mechanics invalid.

Label remains exactly V28I: positive iff V28F ALL3 terminal score is `0.0`; expected prevalence 66/144.

## Frozen bounded legal history

V28H selected checkpoint S=480 and explanatory window 384–479. Capture the same 114 legal `solver.programme_features` at exactly four pre-action checkpoints:

`384, 416, 448, 480`.

These are fixed before V28J outcomes. No horizon/checkpoint sweep is permitted.

The model matrix contains only runtime-legal values derived from those observations:
1. the 114 raw features at each of the four checkpoints (456 columns);
2. for each feature, three adjacent differences: `416-384`, `448-416`, `480-448` (342 columns).

Total: **798 legal state/history columns**.

No source/rank/ref/SHA, opponent identity, seed, seat, terminal outcome, future state, rating, EpisodeId, or hidden opponent-private state may enter the matrix. Seed/seat/source may exist only as offline audit metadata.

## Frozen source-held-out split

Reuse **exactly** the V28I source split. No source moves sides. This preserves the same 8-source train / 4-source holdout test and the same 4-hard+4-easy train / 2-hard+2-easy holdout structure.

## Frozen model family

Use one deterministic decision tree, deliberately keeping V28I capacity fixed so V28J isolates the value of legal history rather than extra model complexity:
- `max_depth=3`;
- `min_samples_leaf=8`;
- `class_weight="balanced"`;
- `random_state=20260922`.

No hyperparameter sweep, threshold search, feature selection, pruning search, or post-outcome checkpoint choice.

## Metrics and acceptance

Report the same train, aggregate holdout, and per-held-out-source metrics as V28I.

Decision **`V28J_BOUNDED_LEGAL_HISTORY_RISK_PHENOTYPE_IDENTIFIABLE`** only if all hold:
1. mechanics PASS;
2. holdout precision >= 0.70;
3. holdout recall >= 0.60;
4. holdout balanced accuracy >= 0.75;
5. each held-out HARD source recall >= 0.50;
6. each held-out EASY source specificity >= 0.75;
7. tree depth <=3 and min leaf exactly 8.

Otherwise: **`V28J_BOUNDED_LEGAL_HISTORY_RISK_PHENOTYPE_NOT_IDENTIFIABLE`**.

Mechanical failure: **`V28J_MECHANICS_INVALID`**.

## Frozen routing

If identifiable: freeze the compact history phenotype and open a mechanism/action-discovery gate only within phenotype-positive states. Runtime source identity remains forbidden.

If not identifiable: close simple classifier-based risk gating on the V28H window. Preserve the forensic evidence, and route to direct mechanism/action discovery from matched hard-vs-control trajectories rather than tuning this classifier family.

No V28J outcome authorizes Kaggle mutation.