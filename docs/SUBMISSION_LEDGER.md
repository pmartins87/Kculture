# Submission ledger — Kculture

Record every Kaggle agent submission here with exact provenance and observed hosted behavior.

**Submission policy:** preserve all submission history. The old repository assumption that only the latest two submissions matter for final evaluation is unverified and must not drive decisions. Hosted submissions are calibration evidence; the final Kaggriculture evaluation will be a later Bradley–Terry tournament after the submission window.

| ID | UTC timestamp | Git SHA | Agent/version | Local evidence | Ladder rating | Episodes | Status | Notes |
|---|---|---|---|---|---:|---:|---|---|
| **55882723** | 2026-08-30 user screenshot | `a3024d2af337bebd7cd1dcb107ccc420635756ef` | `CR015-liquidation-phase-early-order` | 432 fresh preregistered pairs; mean relative gain +149.62 vs R4B; favorable W/L 2, unfavorable 0; package parity 28,760 states / 0 mismatches; official entrypoint PASS both seats | **1024** | in progress | Hosted / still running | User reports only **1 loss so far** at this snapshot. Visible selected hosted episode `103060387` is a CR015 win versus Lakshmanan R; screenshot shows Paulo Martins 1056 (+120) vs Lakshmanan R 1092 (-4). Treat 1024 as an interim trajectory point, not a stabilized rating. Candidate blob `fabd4bc398e7eadcfd1d44add4d0e593315140e8`; archive SHA-256 `41d35a97ebe714a3cb71506e17ec1e629b4a9628cacd688be7e79d524fd75c54`. |
| **55818927** | 2026-08-27 ~16:20 UTC screenshot | `b8949a9c43ba9d667b043b3d39ab3e29a3fbaa48` | `KEXP-050-reallocate614-validation-v1` | dev 21-11; live-meta 15-11-14; fresh stress 87-47-58; validation direct 14-8-10 | **93.8** | unknown | Complete | Current hosted evidence is materially worse than R4B. User supplied Game History episode `100987834`; selected replay shows a loss to Atharva S. Naladkar. |
| **55784381** | 2026-08-27 ~16:20 UTC screenshot | `29a883aba3df6347d72e321c9970c9694e0b6fa0` | `R4B-market-only-validated-v1` | old public panel 81-15 / 96 | **143.2** | unknown | Complete | User supplied Game History episode `100996939`; selected replay is shown as a tie versus Sathisvaran Ragu. |
| **55818927** | 2026-08-27 ~14:06 UTC screenshot | `b8949a9c43ba9d667b043b3d39ab3e29a3fbaa48` | `KEXP-050-reallocate614-validation-v1` | dev 21-11; live-meta 15-11-14; fresh stress 87-47-58; validation direct 14-8-10 | **145.1** | unknown | Complete | Green check. Only +3.1 versus contemporaneous R4B 142.0. First hosted evidence says the locally validated micro-overlay line is not prize-grade. |
| **55784381** | 2026-08-27 ~14:06 UTC screenshot | `29a883aba3df6347d72e321c9970c9694e0b6fa0` | `R4B-market-only-validated-v1` | old public panel 81-15 / 96 | **142.0** | unknown | Complete | Same screenshot. Rating is dynamic and rebounded from prior 110.5 snapshot. |
| **55784381** | 2026-08-27 earlier snapshot | `29a883aba3df6347d72e321c9970c9694e0b6fa0` | `R4B-market-only-validated-v1` | old public panel 81-15 / 96 | **110.5** | unknown | Complete | Earlier user-visible score. |
| **55784381** | 2026-08-26 12:00 snapshot | `29a883aba3df6347d72e321c9970c9694e0b6fa0` | `R4B-market-only-validated-v1` | old public panel 81-15 / 96 | **135.7** | unknown | Complete | Intermediate snapshot. |
| **55784381** | 2026-08-26 04:37 snapshot | `29a883aba3df6347d72e321c9970c9694e0b6fa0` | `R4B-market-only-validated-v1` | old public panel 81-15 / 96 | **161.6** | unknown | Complete | First observed hosted snapshot. |

## Submission 1 — R4B

User-visible identity:

- submission ID: **`55784381`**;
- filename: `Kculture_R4B_market_only_validated_v1_submission.tar.gz`;
- description: `Kculture R4B market-only validated v1`;
- status: **Complete** / green check;
- observed ratings: **161.6 → 135.7 → 110.5 → 142.0 → 143.2**;
- user-supplied hosted episode example: **`100996939`**;
- hosted episode count not yet observed.

Exact package provenance:

- package-build Git SHA: `29a883aba3df6347d72e321c9970c9694e0b6fa0`;
- frozen candidate blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`;
- archive SHA-256: `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`;
- archive size: 101557 bytes;
- packaged `main.py` SHA-256: `07bda5229dec0e50b56df8e76523188169213ba7cea4d2e118be61491fdc0cd1`;
- package parity run `32919305800`: PASS, 4/4 exact trajectories.

## Submission 2 — KEXP-050

User-visible identity:

- submission ID: **`55818927`**;
- filename: `Kculture_KEXP050_reallocate614_validated_v1_submission.tar.gz`;
- description: `Kculture KEXP050 reallocate614 validated v1`;
- status: **Complete** / green check;
- observed ratings: **145.1 → 93.8**;
- contemporaneous R4B latest rating: **143.2**;
- user-supplied hosted episode example: **`100987834`**, shown as a loss to Atharva S. Naladkar;
- hosted episode count not yet observed.

Exact provenance:

- frozen candidate: `candidates/r4d_reallocate_614_carrot.py`;
- candidate blob: `61b77be136836328917441cb03f89bc6665c4c27`;
- parent R4B blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`;
- KEXP-054 correct validation run: `33073517302`, PASS;
- validation direct vs R4B: **14-8-10**, score 0.59375, mean money delta +31.06, zero errors;
- validation public controls: Kaito 25-7 vs 25-7, Rayk 32-0 vs 32-0, Andrew 21-11 vs 21-11;
- formal package run: `33074434495`, PASS;
- archive SHA-256: `59a45adf283f2f4dd1f9272150786c014585aa08c9b31b3348cf992ebe3bb64c`;
- archive size: 102524 bytes;
- packaged `main.py` SHA-256: `10b904ef9c26c7e87462e1f033c8e6d92bee5984e96a23e67a18804f3034e2d9`;
- source/package parity: 8/8 full trajectories exact.

## Submission 3 — CR015

User-visible identity:

- submission ID: **`55882723`**;
- Kaggle submission link: `https://www.kaggle.com/competitions/kaggriculture/submissions?submissionId=55882723`;
- candidate: `CR015-liquidation-phase-early-order`;
- status: **hosted games in progress**;
- observed interim rating: **1024** on 2026-08-30 screenshot;
- user-reported result count at that snapshot: **only one loss so far**;
- visible hosted episode example: **`103060387`**, shown as a win versus Lakshmanan R;
- screenshot-selected game display: Paulo Martins **1056 (+120)** vs Lakshmanan R **1092 (-4)**;
- hosted episode count: still in progress / not frozen.

Interpretation: the trajectory is encouraging and confirms CR015 is mechanically functioning in the hosted environment, but 1024 is an interim rating while games are still being added. Do not compare it as a stabilized endpoint against completed CR008/CR011 snapshots yet.

Exact provenance:

- candidate path: `candidates/cr015_liquidation_phase_early_order.py`;
- candidate freeze commit: `a3024d2af337bebd7cd1dcb107ccc420635756ef`;
- candidate blob: `fabd4bc398e7eadcfd1d44add4d0e593315140e8`;
- local validation: 432 fresh preregistered pairs, zero errors;
- combined mean relative gain vs R4B: **+149.62**;
- favorable W/L: **2**; unfavorable: **0**;
- package parity: **28,760 states / zero mismatches**;
- official Kaggle entrypoint: **PASS both seats**;
- archive SHA-256: `41d35a97ebe714a3cb71506e17ec1e629b4a9628cacd688be7e79d524fd75c54`.

## 2026-08-27 competitive-reset interpretation

The hosted trajectory now makes the micro-overlay failure clearer: KEXP-050 fell from 145.1 to **93.8** while R4B sat at **143.2**. The locally validated R4B→KEXP-050 line is therefore closed as a prize-scale architecture direction; KEXP-050 remains useful only as calibration evidence.

CR-001 subsequently proved that Kaito/Rayk/Andrew package identities were not the problem. CR-002 then showed the old historical public-opponent laboratory was structurally miscalibrated: R4B/KEXP-050 could dominate many historically high-scoring public agents locally while remaining weak hosted. Current work therefore prioritizes current-meta calibration plus identity-free opponent adaptation and exact hosted-loss forensics.

The user supplied exact hosted submission IDs and episode IDs on 2026-08-27. Same-day official episode datasets are not yet anonymously downloadable while the current daily dataset is unpublished/permission-gated; the exact replays will be fetched automatically once the public daily dataset becomes available.

## Required notes per future submission

- exact source/config and hashes;
- strategy family and material difference from previous hosted agents;
- development + exploratory evidence;
- benchmark identity proof against exact scored package;
- fresh validation result when used for promotion;
- package parity result;
- hosted errors/anomalies;
- observed rating/episode progression;
- whether it remains useful as calibration, champion or final candidate.
