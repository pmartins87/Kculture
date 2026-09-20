# ALL3 V13B Current Top-30 Executable Refresh Protocol — 2026-09-20

## Purpose

V13A found moderate public-frontier drift: only 15/30 current refs overlap the frozen 2026-09-18 Top-30.

V13B refreshes the source identity and **mechanical executability** of all 30 current score-sorted public notebooks.

This is infrastructure/benchmark preparation only. Local win rate is not used as a proxy for hosted strength.

## Frozen input

`configs/all3_v13b_current_top30_refs.json`

Exactly 30 refs, ranks 1..30, frozen from V13A workflow `35520373817`.

## Acquisition

For each ref:

1. prefer a unique public notebook output package containing root `main.py`;
2. if no unique package exists, statically recover the submission source from notebook code using the existing Top-30 extractor;
3. preserve required support files only in the ephemeral workflow workspace;
4. compute `main.py` SHA-256;
5. deduplicate by exact `main.py` SHA.

Public third-party code is **not committed back to the repository** and is **not uploaded as an artifact**.

## Secret isolation

All downloads occur before executing any third-party code.

Before any source is imported/executed:
- remove `KAGGLE_API_TOKEN` from the process environment;
- no Kaggle mutation command is permitted.

## Mechanical smoke

For one representative of every unique source SHA:

- load the exact hosted-faithful callable using Kaggle's official `get_last_callable`;
- run exact `kaggle-environments==1.32.7`;
- seed `78001`;
- one episode as seat 0 vs `starter`;
- one episode as seat 1 vs `starter`.

Record:
- acquisition status;
- source SHA;
- current rank aliases sharing that source;
- official callable name if available;
- both-seat DONE status/rewards;
- any import/runtime failure.

These games are **smoke only**. Their W/L is strategically meaningless.

## Gate

`V13B_EXECUTABLE_FRONTIER_READY` if all:

- >=24/30 refs acquired;
- >=12 unique source SHAs acquired;
- >=10 unique sources pass both-seat smoke;
- >=5 current Top-10 refs belong to a both-seat-smoke-passing source.

Otherwise:
- acquisition adequate but smoke coverage insufficient:
  `V13B_EXECUTABLE_FRONTIER_PARTIAL`;
- <24 refs acquired or mechanics infrastructure fails:
  `V13B_FRONTIER_REFRESH_INCOMPLETE`.

## Next stage

If READY:
- freeze one representative ref per mechanically executable unique source;
- V13C runs exact ALL3 against that current frontier only as a **hard-context/mechanism discovery census**, never as a hosted-rating estimator;
- hosted evidence remains the strategic calibration source.

No Kaggle submission.
