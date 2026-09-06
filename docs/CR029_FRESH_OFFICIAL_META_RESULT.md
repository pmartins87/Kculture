# CR029 — Fresh official-meta calibration result

Date: 2026-09-06
Workflow run: `34005573907`
Frozen workflow head: `daa30bd1870d8df7bb42bfc755cb0fea6b21850f`

## Mechanical result

- workflow: SUCCESS
- benchmark errors: 0
- official-meta rows: 72 / 72
- independent pairwise rows: 36 / 36
- unique exact official winner scenarios: 12
- held-out touched: false
- runtime identity features: false
- automatic Kaggle submission: false

## Official-meta panel

Each candidate was tested in both seats against 12 unique exactly reproducible official winner tapes from 2026-09-05.

### CR024 control

- games: 24
- W/L: 2 / 22
- score: 2.0 / 24
- score rate: 0.0833
- mean delta: -14236.875

### full_recent_top

- games: 24
- W/L: 12 / 12
- score: 12.0 / 24
- score rate: 0.5000
- mean delta: +10673.5833
- paired vs CR024 improvements: 12
- paired vs CR024 regressions: 2
- paired W/L score gain vs CR024: +10.0
- paired mean delta gain vs CR024: +24910.4583
- positive paired-margin rows: 18 / 24
- negative paired-margin rows: 6 / 24

### indar_v1

- games: 24
- W/L: 2 / 22
- score: 2.0 / 24
- score rate: 0.0833
- mean delta: -14749.5417
- paired vs CR024 improvements: 0
- paired vs CR024 regressions: 0
- paired W/L score gain vs CR024: 0.0
- paired mean delta gain vs CR024: -512.6667

## Independent fresh pairwise panel

Six frozen previously unused seeds, both seats.

### full_recent_top vs CR024

- games: 12
- W/L: 8 / 4
- score: 8.0 / 12
- score rate: 0.6667
- mean delta: +3256.5

### indar_v1 vs CR024

- games: 12
- W/L: 2 / 10
- score: 2.0 / 12
- score rate: 0.1667
- mean delta: +87.3333
- median delta: -1572.0

### indar_v1 vs full_recent_top

- games: 12
- W/L: 0 / 12
- score: 0.0 / 12
- score rate: 0.0
- mean delta: -3196.8333

## Frozen gate outcome

`full_recent_top` passed every frozen CR029 promotion check.

`indar_v1` failed the independent fresh-pairwise gate against CR024.

Passing finalists:

- `full_recent_top`

Decision:

`SHORTLIST_FULL_RECENT_TOP_FOR_KAGGLE_PACKAGE_PREFLIGHT`

## Interpretation

CR029 is a strong generalization filter. Indar V1 looked credible in the prior corrected CR027 screen, but failed badly on the independent fresh-pairwise panel and lost all 12 direct games against `full_recent_top`. This is exactly the type of apparent-local-strength / weak-generalization failure that should be eliminated before hosted Kaggle calibration.

`full_recent_top`, by contrast, improved the official-meta W/L score by +10 against CR024, won 8/12 on completely fresh pairwise games against CR024, and dominated Indar 12/12.

This authorizes package preflight only. It does not yet authorize treating `full_recent_top` as the final competition solution. The untouched final distribution-shift stress block remains reserved for later final selection.