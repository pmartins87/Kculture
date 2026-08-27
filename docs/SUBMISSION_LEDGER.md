# Submission ledger — Kculture

Record every Kaggle agent submission here with exact provenance and observed hosted behavior.

**Submission policy:** preserve all submission history. The old repository assumption that only the latest two submissions matter for final evaluation is unverified and must not drive decisions. Hosted submissions are calibration evidence; the final Kaggriculture evaluation will be a later Bradley–Terry tournament after the submission window.

| ID | UTC timestamp | Git SHA | Agent/version | Local evidence | Ladder rating | Episodes | Status | Notes |
|---|---|---|---|---|---:|---:|---|---|
| unknown | 2026-08-27 ~14:06 UTC screenshot | `b8949a9c43ba9d667b043b3d39ab3e29a3fbaa48` | `KEXP-050-reallocate614-validation-v1` | dev 21-11; live-meta 15-11-14; fresh stress 87-47-58; validation direct 14-8-10 | **145.1** | unknown | Complete | Green check. Only +3.1 versus contemporaneous R4B 142.0. First hosted evidence says the locally validated micro-overlay line is not prize-grade. |
| unknown | 2026-08-27 ~14:06 UTC screenshot | `29a883aba3df6347d72e321c9970c9694e0b6fa0` | `R4B-market-only-validated-v1` | old public panel 81-15 / 96 | **142.0** | unknown | Complete | Same screenshot. Rating is dynamic and rebounded from prior 110.5 snapshot. |
| unknown | 2026-08-27 earlier snapshot | `29a883aba3df6347d72e321c9970c9694e0b6fa0` | `R4B-market-only-validated-v1` | old public panel 81-15 / 96 | **110.5** | unknown | Complete | Earlier user-visible score. |
| unknown | 2026-08-26 12:00 snapshot | `29a883aba3df6347d72e321c9970c9694e0b6fa0` | `R4B-market-only-validated-v1` | old public panel 81-15 / 96 | **135.7** | unknown | Complete | Intermediate snapshot. |
| unknown | 2026-08-26 04:37 snapshot | `29a883aba3df6347d72e321c9970c9694e0b6fa0` | `R4B-market-only-validated-v1` | old public panel 81-15 / 96 | **161.6** | unknown | Complete | First observed hosted snapshot. |

## Submission 1 — R4B

User-visible identity:

- filename: `Kculture_R4B_market_only_validated_v1_submission.tar.gz`;
- description: `Kculture R4B market-only validated v1`;
- status: **Complete** / green check;
- observed ratings: **161.6 → 135.7 → 110.5 → 142.0**;
- submission ID and hosted episode count not yet observed.

Exact package provenance:

- package-build Git SHA: `29a883aba3df6347d72e321c9970c9694e0b6fa0`;
- frozen candidate blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`;
- archive SHA-256: `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`;
- archive size: 101557 bytes;
- packaged `main.py` SHA-256: `07bda5229dec0e50b56df8e76523188169213ba7cea4d2e118be61491fdc0cd1`;
- package parity run `32919305800`: PASS, 4/4 exact trajectories.

## Submission 2 — KEXP-050

User-visible identity:

- filename: `Kculture_KEXP050_reallocate614_validated_v1_submission.tar.gz`;
- description: `Kculture KEXP050 reallocate614 validated v1`;
- status: **Complete** / green check;
- first observed rating: **145.1** about one hour after submission;
- contemporaneous R4B rating: **142.0**;
- submission ID and hosted episode count not yet observed.

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

## 2026-08-27 competitive-reset interpretation

The 145.1 vs 142.0 hosted snapshot is decisive evidence that the R4B→KEXP-050 micro-overlay program is not closing the prize-scale gap. The local promotion chain was executed correctly, so the failure is informative rather than a packaging bug.

More importantly, the old local strong panel is now considered **identity-unproven**. Historical high-scoring public Kaggle notebooks often publish both a top-level `main.py` and a separate `submission.tar.gz`; previous Kculture workflows benchmarked the top-level `main.py`. Until we prove that this file is byte/behavior equivalent to the exact packaged agent that earned the reported ladder score, old results such as 32-0 versus “Rayk V11” or 25-7 versus “Kaito V27” must not be treated as calibrated strength evidence.

**Competitive Reset CR-001:** freeze R4B/KEXP-050 as calibration references; audit the exact public submission packages for Kaito V4, Rayk V11, Andrew V12 and Flexonafft V59; rebuild the local benchmark around identity-proven scored packages; then establish a true 2000–3000-class public baseline before further micro-optimization.

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
