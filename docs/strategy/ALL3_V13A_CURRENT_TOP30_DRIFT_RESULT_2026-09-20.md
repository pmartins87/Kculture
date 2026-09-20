# ALL3 V13A Current Top-30 Drift Census — Result — 2026-09-20

Workflow: **`35520373817`**  
Binding head: `9fb21773f4b7318dbc12605d49e680296de3898a`.

The earlier run `35520312252` is mechanically invalid/non-binding because the script did not place the repository root on `sys.path`; it failed before reading strategic data.

Decision: **`V13A_FRONTIER_MODERATE_DRIFT_REFRESH_ALL_CURRENT`**.

## Current frontier drift

Compared with the frozen 2026-09-18 Top-30 public-code corpus:

- overlap: **15/30** refs;
- new/current refs absent from the frozen Top-30: **15**;
- frozen Top-30 refs no longer present: **15**;
- unknown current source identities requiring refresh: **15**.

Therefore the public code frontier has changed materially enough that incremental reuse is not justified.

## Binding interpretation

Refresh/extract **all current Top-30 refs** before constructing a new executable opponent bank.

The 2026-09-18 `PROGRAMME_CORPUS.json` remains useful for provenance and duplicate recognition, but it is not sufficient as the current executable frontier.

Frozen current refs:
`configs/all3_v13b_current_top30_refs.json`.

No third-party agent code was executed by V13A.
No Kaggle submission is authorized.
