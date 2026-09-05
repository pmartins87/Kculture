# CR025 — CR024 consensus + frozen CR008 adaptive overlay

Date: 2026-09-05
GitHub Actions run: `33945891874`
Final artifact: `cr025-stageb-final`

## Result

The experiment completed all 168 paired rows (7 frozen opponents × 12 untouched adaptive Stage-B seeds × both seats) with zero errors. All 32 final held-out seeds remained untouched.

Final decision:

`CR025_FAIL__RETIRE_OVERLAY_ON_CONSENSUS`

### CR025 vs frozen CR024 consensus

- CR024 total W/L score: **168.0 / 168**
- CR025 total W/L score: **168.0 / 168**
- W/L score gain: **0.0**
- favorable conversions: **0**
- unfavorable conversions: **0**
- net favorable conversions: **0**
- mean terminal relative-margin gain: **-114.690476**
- positive-margin rows: 14
- negative-margin rows: 96
- unchanged-margin rows: 58

### Overlay activity

- triggered games: **134 / 168**
- triggered orders: **264**
- CARROT orders: 24
- STRAWBERRY orders: 240

The overlay therefore fired frequently and materially changed trajectories, but produced no W/L benefit and worsened mean margin substantially.

## Interpretation

The CR008 full-stock CARROT/STRAWBERRY front-run was valuable on the old R4B backbone, but does not transfer as-is to the much stronger CR024 consensus backbone. The intervention is now mostly redundant or harmful.

A second important conclusion is that the legacy seven-opponent panel is saturated: CR024 won every one of the 168 rows. It is no longer discriminative enough for successor selection.

## Decision

1. **Do not package or submit CR025.**
2. Retire the full frozen CR008 overlay on top of CR024 consensus.
3. Do not retune its thresholds/quantities on these now-open Stage-B rows to rescue the same candidate.
4. Move CR026 development to a stronger current live-meta panel built from recent official winner action tapes.
5. Keep the final 32 held-out seeds sealed.
