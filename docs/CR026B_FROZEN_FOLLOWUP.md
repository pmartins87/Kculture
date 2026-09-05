# CR026B rank-10 independent gate — 2026-09-05

## Why CR026B exists

CR026A/rank 5 was the first predeclared choice from the ten-route screen, but fresh follow-up evidence rejected it: hosted gain was only +2 with five regressions, while both completed reactive shards lost two paired W/L points versus CR024.

The original screen had already declared rank 10 as the backup before CR026A results were known. CR026B therefore tests that frozen alternative rather than retuning rank 5 after failure.

## Frozen identity

- Candidate: `CR026B_RANK10`.
- Source run: `33973134213`, artifact `cr026-screen-input`.
- Source official episode: `105550817`.
- Source seat: `0`.
- Source team metadata: `keiz` (research provenance only; never a runtime feature).
- Tape SHA256: `13a1ea6399ed192dc3251acb27a08f1ccf1b3e98f4f82c3d783900d55ac5f770`.
- Control: exact CR024 tape SHA256 `d2d253bd65de3658ec55e2fe16bdb85e3a9a51c0a13dee4a756b646cfeac307e`.

## Independent evidence

To avoid inheriting rank-5 validation:

- reactive seeds are new and were frozen before rank-10 results;
- direct seeds are new and were frozen before rank-10 results;
- reactive opponents are Rayk V23, Boatlee V2, and Prvsiyan V10, all exact packaged public agents with pinned hashes;
- Tetsu V2 is replaced because Kaggle now returns HTTP 403 for that notebook output;
- the hosted sample is not the twenty episodes used by CR026A;
- instead, from all currently completed public CR024 episodes, all CR026A episode IDs are excluded and twenty are selected deterministically by SHA256 order using salt `CR026B_RANK10_FRESH_V1`;
- each selected hosted game must reproduce the exact CR024 trace and original reward pair before candidate replacement.

## Frozen promotion rule

CR026B is eligible for one hosted Kaggle calibration only if all are true:

1. reactive aggregate paired score does not decline and total regressions are <=2;
2. fresh hosted paired score gain is >=+6, regressions <=2, and mean relative-margin gain is positive;
3. fresh direct score versus CR024 is >=6/8 with positive mean margin;
4. package/clock/file-entrypoint mechanics pass exactly.

No threshold rescue after results. No automatic Kaggle submission. If rejected, move to a genuinely different strategy architecture rather than repeatedly cloning nearby tapes.
