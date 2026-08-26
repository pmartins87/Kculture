# STATUS — Kculture

Last updated: 2026-08-25

## Mission status

**Goal: top-10 final finish in Kaggriculture; each top-10 position pays US$5,000.**

- **R1 PASS** — official starter parity and 720-turn reproduction.
- **R2 PASS** — deterministic tournament laboratory, frozen seed partitions and public-opponent provenance.
- **R3 pending** — first hosted ladder submission/account-side entry confirmation.
- **R4 ACTIVE** — strong economic baseline and Kculture improvements.
- **R4A frozen** — COK V8 selected as `R4A-public-base-v1`.
- **Full R4B REJECTED** — extra terminal `DROP` optimizer failed its direct development gate.
- **Market-only R4B frozen for validation** — development screen passed; `KEXP-20260825-007` validation is running.
- **Held-out remains sealed** — none of the 32 held-out seeds has been opened for the active candidate.

## Competition constraints

- Entry/team-merger deadline: 2026-09-23 23:59 UTC.
- Final submission deadline: 2026-09-30 23:59 UTC.
- Final games continue approximately through 2026-10-15.
- 720 turns = 30 in-game days × 24 turns.
- Submission exposes `agent` from root `main.py`.
- Up to 5 submissions/day; latest 2 remain tracked for final evaluation.
- Hosted self-play validation occurs before ladder entry.
- Default hosted action timeout: 1 second.

## Official environment freeze

- `kaggle-environments==1.32.7`, released 2026-08-15.
- engine-changing intake commit: `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`.
- official hashes: `official/UPSTREAM_LOCK.md`.
- mechanics snapshot: `docs/OFFICIAL_MECHANICS_SNAPSHOT.md`.

Important verified terminal mechanics: final reward is `farm.money`; step 718 is the last executable action; market sales are processed unit-by-unit and every valid sale has positive price with floor $1. Inventory has no direct residual terminal reward.

## R1/R2 evidence

- R1 Actions run `32858531629`: exact starter parity on seeds 101/202/303 and 720-turn self-play on 404.
- R2 Actions run `32859938870`: 64 disjoint seeds (16 development / 16 validation / 32 held-out), both-seat evaluation, 7 deterministic references, fresh module loading and zero closure-smoke errors.

## R4A — frozen public base

`KEXP-20260825-004-r4-public-base-screen` screened two attributed Apache-2.0 public architectures:

- COK V8 — `COK-ZhangZiliang/Kaggriculture`, commit `779caaec88a441345871e2d62eb5de93606b7b52`, SHA-256 `faf57412e2c56dcc669043865a185324bab9952d865abccc2203284e854eceb3`.
- Seyamalam V21 — commit `8b8c421eb10634c756583ce10c75189f50c83a72`, SHA-256 `0cd14b653102d276c4f902fa3b8c6bd81d869b8ab64c422cb881b9d2346ec639`.

First 8 development seeds × both seats: COK V8 **14-2**, mean delta **+21,063.875**, zero errors. COK became `R4A-public-base-v1`.

## KEXP-005 — full terminal-capacity R4B: REJECTED

The full candidate changed only step 718 but additionally replaced selected physical actions with capacity-aware `DROP`s.

Actions run `32913752287`:

- R4A control vs Seyamalam: **14-2**, mean `+21,063.875`.
- full R4B vs Seyamalam: **16-0**, mean `+22,541.500`.
- full R4B vs R4A: **5-11**, score `0.3125`, mean `-1.625`.

It failed the predeclared direct score and direct mean gates, so it was rejected before validation. Artifact `9587959717`, SHA-256 `949e6bdf94c6356aae6af398c6bce17769997255f04a18c59eb5ba2c58245dcf`.

## KEXP-006 — market-only ablation: DEVELOPMENT SCREEN PASS

`candidates/r4b_ablation_market_only.py` preserves every physical COK action and changes only final-step market liquidation.

Actions run `32915111893`, source commit `148cc81fed390fd75c0cba00ceb779efaa17a46f`, candidate Git blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`:

- market-only vs Seyamalam: **16-0**, mean `+22,541.500`.
- market-only vs R4A: **5-3-8**, score `0.5625`, mean `+12.000`.
- full R4B vs market-only: full R4B **5-11**, mean `-3.125`.

Conclusion: final sale completeness is the useful component; extra physical `DROP` replacement was harmful on development. Exact freeze metadata is in `configs/r4b_market_only_candidate.json`.

## KEXP-007 — frozen market-only validation: RUNNING

GitHub Actions run `32918640409` is the predeclared validation gate. It opens all 16 validation seeds for this exact frozen candidate, both seats, in three independent blocks:

1. R4A vs Seyamalam validation control;
2. market-only vs Seyamalam;
3. market-only vs R4A.

PASS requires zero errors, direct score vs R4A >= 0.50, direct mean >= 0, and no regression versus the R4A control against Seyamalam in either wins or mean delta.

**No validation result has been interpreted yet. Held-out remains sealed.**

## Packaging readiness

`tools/build_r4b_market_only_submission.py` is prepared to turn the laboratory wrapper into a self-contained deterministic archive with root `main.py`, Apache-2.0 license and upstream notices. If validation passes, packaged-vs-wrapper trajectory parity must pass before any hosted submission.

## Strong public targets

Current dated benchmark targets include:

- Kaito Fukami V27 V4 — score snapshot 3090.1, Apache-2.0.
- Rayk V11 — best snapshot 2990.4.
- Andrew Breaking the Tie V12 — best snapshot 2915.2.
- FlexonaFFt V59 — best snapshot 2767.3.

Exact Kaggle kernel acquisition is auth-gated and prepared via the manual workflow using repository secret `KAGGLE_API_TOKEN`; credentials are never committed.

## R4C prepared, not executed

`KEXP-20260825-008-r4c-guarded-ninth-cow` is a separate development-only hypothesis enabling one dormant guarded ninth-cow branch. It was renumbered from a duplicate KEXP-006 identifier and has not been executed. It must not use validation or held-out seeds.

## Immediate continuation

1. Finish and interpret `KEXP-007` strictly against its predeclared gate.
2. If PASS, preserve evidence and prove packaged `main.py` parity with the frozen wrapper.
3. Prepare the first hosted ladder submission and complete R3 once account-side Kaggle access is confirmed.
4. Continue development-only R4/R5 improvements against stronger opponents; do not tune on validation results.
5. Keep all 32 held-out seeds sealed until a later formal promotion/final-selection gate.
