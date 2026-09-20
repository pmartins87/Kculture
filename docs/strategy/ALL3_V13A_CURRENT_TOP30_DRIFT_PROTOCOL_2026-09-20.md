# ALL3 V13A Current Top-30 Drift Census Protocol — 2026-09-20

## Purpose

V12A showed the frozen seven-agent public league is no longer useful as a discovery population: exact ALL3 won 112/112 episodes.

Before downloading/executing a large new opponent bank, refresh the public Kaggriculture code frontier and quantify how much the current score-sorted Top-30 has drifted from the frozen 2026-09-18 Top-30 corpus.

This stage is metadata/source-reference discovery only. It executes **no third-party agent code**.

## Source

Authenticated Kaggle CLI:

`kaggle kernels list --competition kaggriculture --sort-by scoreDescending --page-size 100 -v`

Take the first 30 refs in returned order.

Frozen comparison source:
`data/programme_teacher/2026-09-18/PROGRAMME_CORPUS.json`.

## Outputs

Record:
- current rank 1..30 refs;
- overlap count with frozen Top-30 refs;
- entrants not present in frozen Top-30;
- frozen refs no longer in current Top-30;
- rank displacement for overlapping refs;
- coverage by frozen source SHA where known;
- count of current refs whose source identity is unknown until refreshed.

No numeric Kaggle score is inferred unless the CLI explicitly supplies it.

## Gate

- overlap >=24/30 and unknown/new refs <=6:
  **`V13A_FRONTIER_STABLE_INCREMENTAL_REFRESH`**
  — reuse frozen dedup map for overlapping refs and fetch only changed/new/current representatives plus strategically distinct frozen sources.

- overlap 15..23:
  **`V13A_FRONTIER_MODERATE_DRIFT_REFRESH_ALL_CURRENT`**
  — fetch/extract all current Top-30 and rebuild the executable dedup map.

- overlap <15:
  **`V13A_FRONTIER_HIGH_DRIFT_REBUILD`**
  — full frontier rebuild before causal discovery.

Mechanical invalidity:
`V13A_MECHANICS_INVALID`.

## Restrictions

- read-only Kaggle operations;
- no code execution from public notebooks;
- no submission;
- no opponent identity as future runtime feature.

