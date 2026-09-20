# ALL3 V13B Current Top-30 Executable Refresh — Result — 2026-09-20

Workflow: **`35520463598`**  
Head: `79e14f85382c8f4d68fba2fab19bcae25c4d9437`

Decision: **`V13B_EXECUTABLE_FRONTIER_READY`**.

## Mechanical refresh

- current refs requested: **30**;
- refs acquired: **26**;
- acquisition failures: **4**;
- unique current source SHAs acquired: **19**;
- unique sources passing both-seat exact-engine smoke: **19/19**;
- current Top-10 refs mapped to smoke-passing sources: **10**.

The four acquisition failures were Kaggle HTTP **429 Too Many Requests** on ranks 27–30, not source/runtime failures.

## Security / provenance

- public code downloaded only into ephemeral workflow storage;
- Kaggle credentials removed before any third-party code execution;
- public code was not committed or uploaded as an artifact;
- exact hosted-faithful callable selected with Kaggle `get_last_callable`;
- engine `kaggle-environments==1.32.7`.

## Binding interpretation

The refreshed current public frontier is mechanically rich enough for a new hard-context discovery census.

Freeze exactly one representative per both-seat-smoke-passing unique source SHA. Do not choose representatives using local W/L.

Frozen V13C population:
`configs/all3_v13c_current_frontier_representatives.json`.

Local smoke W/L remains strategically meaningless and cannot be used as a hosted-rating estimator.

No Kaggle submission.
