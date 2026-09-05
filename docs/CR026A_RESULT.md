# CR026A fresh-gate result — 2026-09-05

## Decision

**REJECT — do not submit CR026A.**

CR026A was the preregistered rank-5 recent production route selected by run `33973134213`. Follow-up workflow `33989861614` produced enough valid evidence to reject it before the third reactive shard could finish.

## Valid completed evidence

### Fresh direct replication vs CR024

- 8/8 wins-equivalent for CR026A.
- Mean direct margin: **+24,730.75**.

This confirms that the rank-5 route is mechanically strong against the CR024 control, but direct self-comparison is not sufficient for promotion.

### Actual hosted counterfactual panel

Twenty previously frozen CR024 hosted episodes reproduced exactly before replacement.

- CR024 score: **8/20**.
- CR026A score: **10/20**.
- Paired score gain: **+2**.
- Improvements: **7**.
- Regressions: **5**.
- Mean relative-margin gain: **+7,827.35**.

The frozen gate required hosted score gain `>= +6`, regressions `<= 2`, and positive mean margin gain. CR026A therefore **fails the hosted gate** despite the strong mean-margin improvement.

The opponents in these counterfactuals are recorded action tapes and cannot react to the replacement candidate; this evidence is calibration, not a live-rating estimate.

### Reactive Rayk V23

Four fresh seeds, both seats: 8 paired comparisons.

- Score gain vs CR024: **-2**.
- Regressions: **2**.
- Improvements: **0**.
- Mean relative-margin gain: **-1,498.375**.

This alone violates the required non-declining reactive score.

### Reactive Boatlee V2

Four fresh seeds, both seats: 8 paired comparisons.

- Score gain vs CR024: **-2**.
- Regressions: **2**.
- Improvements: **0**.
- Mean terminal margin is higher than CR024 in this shard, but W/L is worse; W/L has priority.

### Tetsu V2 infrastructure failure

The Tetsu notebook package download returned Kaggle HTTP 403, so that shard never executed. The aggregate job then failed because the frozen three-shard input was incomplete.

This is **not** a candidate execution failure. However, rerunning Tetsu is unnecessary for the CR026A decision: the already-completed hosted and reactive evidence independently fails the preregistered thresholds. No threshold rescue is allowed.

## Interpretation

The pure recent rank-5 route is much stronger than CR024 in direct tape-vs-tape tests and improves average margin on the hosted counterfactual panel, but it sacrifices too many W/L outcomes when opponents react. This is exactly the failure mode the fresh reactive gate was designed to detect.

The predeclared backup from the original screen is **rank 10** (`episode 105550817`, seat 0, team `keiz`, tape SHA256 `13a1ea6399ed192dc3251acb27a08f1ccf1b3e98f4f82c3d783900d55ac5f770`). It must receive independent validation and cannot inherit rank-5 evidence.

## Next action

Freeze CR026B as rank 10 and evaluate it with new seeds, accessible reactive opponents, and a deterministic fresh hosted sample that excludes all twenty CR026A hosted episodes.
