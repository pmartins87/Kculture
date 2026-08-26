# STATUS — Kculture

Last updated: 2026-08-25/26

## Mission status

**Goal: top-10 final finish in Kaggriculture; each top-10 position pays US$5,000.**

- **R0 complete for working purposes** — technical intake complete and competition entry is user-confirmed; API-side reconciliation will occur with the first authenticated submission.
- **R1 PASS** — official starter parity and 720-turn reproduction.
- **R2 PASS** — deterministic tournament laboratory and frozen seed partitions.
- **R3 READY TO SUBMIT** — first hosted ladder package is validated and deterministic; authenticated Kaggle upload remains.
- **R4 ACTIVE** — strong economic baseline and Kculture improvements.
- **R4A frozen** — COK V8 selected as `R4A-public-base-v1`.
- **Full R4B REJECTED** — terminal physical-DROP optimizer failed direct development gate.
- **R4B market-only VALIDATION PASS** — frozen as `R4B-market-only-validated-v1` and selected as first hosted-submission candidate.
- **Package parity PASS** — exact self-contained hosted package reproduced the frozen wrapper action-for-action.
- **Kaito V18 generalization support** — market-only improved the same-seed development result from 14-2 to 16-0.
- **R4C ninth-cow NO PROMOTION** — neutral external result and zero paired aggregate advantage.
- **KEXP-010 failure atlas running** — 160 development games across COK/Seyamalam/Kaito.
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

Extra terminal physical `DROP` replacement was rejected before validation.

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

Every predeclared validation condition passed. Evidence is preserved in `experiments/KEXP-20260825-007-r4b-market-only-validation/README.md`.

The exact artifact is `R4B-market-only-validated-v1`: a **validated engineering / first hosted-submission candidate**, not a top-10 claim and not yet R4 overall PASS.

## Package parity: PASS

Actions run `32919305800`:

- exact frozen candidate Git blob verified;
- exact COK V8 source hash verified;
- deterministic self-contained archive built;
- 4/4 tested full trajectories had identical actions from start to finish;
- terminal statuses/rewards matched exactly.

Hosted package:

- archive SHA-256: `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`;
- size: `101557` bytes;
- packaged `main.py` SHA-256: `07bda5229dec0e50b56df8e76523188169213ba7cea4d2e118be61491fdc0cd1`.

`.github/workflows/r3-first-hosted-submission.yml` rebuilds and hash-checks this exact archive before sending it. Competition entry is user-confirmed; authenticated Kaggle access is the remaining R3 execution dependency.

## KEXP-008 — guarded ninth cow: NO PROMOTION

Run `32919545606`, first 8 development seeds × both seats:

- R4A vs Seyamalam: **14-2**, mean `+21,063.875`.
- R4C vs Seyamalam: **14-2**, mean `+21,063.875` — exact non-improvement.
- R4C vs R4A: **4-4-8**, score `0.500`, mean `0.000`.

The dormant switch can create small differences but showed no external advantage. It is not part of the hosted candidate.

## KEXP-009 — Kaito V18 strong-panel preservation: GENERALIZATION SUPPORT

Public Kaito V18/C20 exact-replication mirror is hash-pinned at SHA-256 `603175d39f2857cbd618dc8f5ac9411e9fd234e3142777ec203342172f05a50e`, Apache-2.0.

Run `32919635267`, first 8 development seeds × both seats:

| Matchup | W-L-T | Score | Mean delta | Errors |
|---|---:|---:|---:|---:|
| R4A vs Kaito V18 | 14-2-0 | 0.875 | +20,732.750 | 0 |
| Market-only vs Kaito V18 | **16-0-0** | **1.000** | **+22,210.375** | 0 |

The market-only change flipped both R4A losses on seed `583180324` into wins while preserving the other wins. This is development-only generalization evidence, not a new validation claim.

## KEXP-010 — development failure atlas: RUNNING

Actions run `32920250892` uses all 16 development seeds, both seats, across five blocks: market-only vs R4A/Seyamalam/Kaito and same-seed R4A controls vs Seyamalam/Kaito. Total 160 games. Its purpose is failure localization and next-hypothesis generation only.

## Strong public targets

Dated benchmark targets include Kaito V27/V42+, Rayk V11, Andrew V12, and Flexona V59. Exact newer Kaggle kernel acquisition remains authentication-gated through the prepared secret-only `KAGGLE_API_TOKEN` workflow.

## Immediate continuation

1. Complete and interpret `KEXP-010` strictly as development diagnostics.
2. Form the next one-change candidate only from a recurring failure pattern in that atlas.
3. Make the first authenticated hosted submission of the frozen R4B package and reconcile hosted behavior/rating, completing R3.
4. Acquire newer strong public agents once authenticated Kaggle API access is available.
5. Keep all 32 held-out seeds sealed until a later formal promotion/final-selection gate.
