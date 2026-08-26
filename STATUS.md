# STATUS — Kculture

Last updated: 2026-08-25

## Mission status

**Goal: top-10 final finish in Kaggriculture; each top-10 position pays US$5,000.**

- **R1 PASS** — official starter parity and 720-turn reproduction.
- **R2 PASS** — deterministic tournament laboratory and frozen seed partitions.
- **R3 pending** — first hosted ladder submission / account-side Kaggle confirmation.
- **R4 ACTIVE** — strong economic baseline and Kculture improvements.
- **R4A frozen** — COK V8 selected as `R4A-public-base-v1`.
- **Full R4B REJECTED** — terminal physical-DROP optimizer failed direct development gate.
- **R4B market-only VALIDATION PASS** — frozen as `R4B-market-only-validated-v1` and selected as first hosted-submission candidate.
- **Package parity running** — Actions run `32919305800`.
- **Held-out sealed** — all 32 held-out seeds remain unopened.

## Competition constraints

- Entry/team-merger deadline: 2026-09-23 23:59 UTC.
- Final submission deadline: 2026-09-30 23:59 UTC.
- 720 turns = 30 in-game days × 24 turns.
- Submission: root `main.py` or `submission.tar.gz` with `main.py` at root, <=100 MiB.
- Up to 5 submissions/day; latest 2 remain tracked for final evaluation.
- Hosted self-play validation occurs before ladder entry.
- Default hosted action timeout: 1 second.
- Final evaluation is based on head-to-head outcomes / Bradley-Terry rather than raw bank alone.

## Environment freeze

- `kaggle-environments==1.32.7`.
- engine-changing intake commit `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`.
- terminal reward is exactly `farm.money`.
- step 718 is the last executable action.
- valid SELL orders are unit-by-unit and have positive price floor $1.

## R1 / R2

- R1 run `32858531629`: exact starter parity and full-turn completion.
- R2 run `32859938870`: 16 development / 16 validation / 32 held-out deterministic seeds, both-seat evaluation, fresh module loading, reference/public opponent provenance and zero closure-smoke errors.

## R4A

COK V8 (`COK-ZhangZiliang/Kaggriculture`, commit `779caaec...`, SHA-256 `faf57412...`, Apache-2.0) beat Seyamalam V21 **14-2** on the first 8 development seeds × both seats, mean `+21,063.875`, zero errors. It is frozen as `R4A-public-base-v1`.

## KEXP-005 — full R4B: REJECTED

Run `32913752287`:

- R4A control vs Seyamalam: **14-2**, mean `+21,063.875`.
- full R4B vs Seyamalam: **16-0**, mean `+22,541.500`.
- full R4B vs R4A: **5-11**, score `0.3125`, mean `-1.625`.

Extra terminal physical `DROP` replacement was therefore rejected before validation.

## KEXP-006 — market-only development screen: PASS

Frozen candidate Git blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

Run `32915111893`:

- market-only vs Seyamalam: **16-0**, mean `+22,541.500`.
- market-only vs R4A: **5-3-8**, score `0.5625`, mean `+12.000`.
- full R4B vs market-only: full R4B **5-11**, mean `-3.125`.

The useful component was isolated as complete final-step market liquidation while preserving every physical COK action.

## KEXP-007 — market-only validation: PASS

Run `32918640409`, exact frozen candidate verified before every matchup, all 16 validation seeds × both seats:

| Matchup | W-L-T | Score | Mean delta | Errors |
|---|---:|---:|---:|---:|
| R4A control vs Seyamalam | 30-2-0 | 0.9375 | +18,053.625 | 0 |
| Market-only vs Seyamalam | 32-0-0 | 1.0000 | +18,885.875 | 0 |
| Market-only vs R4A | 8-6-18 | 0.53125 | +165.03125 | 0 |

Every predeclared validation condition passed. Evidence and artifact hashes are preserved in `experiments/KEXP-20260825-007-r4b-market-only-validation/README.md`.

The exact artifact is now `R4B-market-only-validated-v1`: a **validated engineering / first hosted-submission candidate**, not yet a top-10 claim and not yet R4 overall PASS.

## Package parity

`tools/build_r4b_market_only_submission.py` embeds the exact hash-pinned COK V8 source plus only the validated Kculture market-only overlay into a deterministic self-contained archive with root `main.py`, Apache-2.0 license and notices.

Actions run `32919305800` is currently enforcing complete action-trajectory and terminal-result parity between the frozen laboratory wrapper and packaged agent on development seeds. A mismatch rejects the package.

## Strong public targets

Dated benchmark targets currently include Kaito V27 V4 (~3090.1 snapshot), Rayk V11 (~2990.4), Andrew V12 (~2915.2), and Flexona V59 (~2767.3). Exact Kaggle kernel acquisition remains authentication-gated through the prepared secret-only `KAGGLE_API_TOKEN` workflow.

## R4C / later development

`KEXP-20260825-008-r4c-guarded-ninth-cow` is prepared but not executed and remains development-only. Validation results from R4B must not be used to tune changed candidates.

## Immediate continuation

1. Finish package parity run `32919305800`.
2. If PASS, preserve the deterministic `.tar.gz` and manifest as hosted-submission-ready.
3. Confirm Kaggle account entered status / authenticated access and make the first ladder submission, completing R3 once hosted behavior is reconciled.
4. Continue development-only R4/R5 work against stronger public opponents.
5. Keep all 32 held-out seeds sealed until a later formal promotion/final-selection gate.
