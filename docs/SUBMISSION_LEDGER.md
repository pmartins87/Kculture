# Submission ledger — Kculture

Record every Kaggle agent submission here with exact provenance and observed hosted behavior.

**Important policy correction:** the repository previously treated “only the latest two submissions remain tracked for final evaluation” as a hard invariant. That claim is currently **unverified** and must not drive submission decisions. Current Kaggle simulation documentation and Kaggriculture staff guidance support treating hosted submissions as ongoing evaluation/calibration agents; the competition will continue episodes for two weeks after the submission deadline and then run a single Bradley-Terry tournament. Until a Kaggriculture-specific official source explicitly defines any retained-submission limit, preserve all submission history and decide calibration submissions by expected information value plus current competition limits.

| ID | UTC timestamp | Git SHA | Agent/version | Local win rate | Ladder rating | Episodes | Status | Notes |
|---|---|---|---|---:|---:|---:|---|---|
| unknown | 2026-08-27 user-visible snapshot | `29a883aba3df6347d72e321c9970c9694e0b6fa0` | `R4B-market-only-validated-v1` | 81-15-0 / 96 vs current public strong panel (development, descriptive) | **110.5** | unknown | Complete | User-visible Kaggle screenshot, green check. Rating declined again from 135.7. Strong hosted/local calibration contradiction. |
| unknown | 2026-08-26 12:00 snapshot | `29a883aba3df6347d72e321c9970c9694e0b6fa0` | `R4B-market-only-validated-v1` | 81-15-0 / 96 | **135.7** | unknown | Complete | Intermediate visible rating snapshot. |
| unknown | 2026-08-26 04:37 snapshot | `29a883aba3df6347d72e321c9970c9694e0b6fa0` | `R4B-market-only-validated-v1` | 81-15-0 / 96 | **161.6** | unknown | Complete | First observed hosted rating snapshot. |

## Submission 1 identity

User-visible Kaggle evidence:

- status: **Complete** / green validation check;
- filename: `Kculture_R4B_market_only_validated_v1_submission.tar.gz`;
- description: `Kculture R4B market-only validated v1`;
- displayed score progression observed so far: **161.6 → 135.7 → 110.5**;
- submission ID: not yet observed;
- hosted episode count: not yet observed.

Exact package provenance:

- package-build Git SHA: `29a883aba3df6347d72e321c9970c9694e0b6fa0`;
- frozen candidate Git blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`;
- archive SHA-256: `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`;
- archive size: 101557 bytes;
- packaged `main.py` SHA-256: `07bda5229dec0e50b56df8e76523188169213ba7cea4d2e118be61491fdc0cd1`;
- package parity Actions run: `32919305800`, PASS, 4/4 full trajectories identical to frozen candidate.

### Interpretation checkpoint

The sequence **161.6 → 135.7 → 110.5** is persistent evidence that R4B is performing poorly hosted despite strong local results. Packaging parity is already proven, so the primary issue is strategic calibration.

R4B is a reproducible baseline, not a likely final candidate. A future hosted calibration submission should test a **materially different, evidence-backed policy** and pass exact package parity. It need not be treated as sacred or hoarded merely because it is another submission; it should be sent when the expected information about the live field justifies it under the current Kaggle limits.

KEXP-041 is **not** such a candidate: development direct 20-12 did not replicate on exploratory live-meta environmental seeds (14-14-12, score 0.50, mean -21.35). It therefore does not justify a hosted submission.

## Required notes per future submission

- exact source/config and hashes;
- strategy family and material difference from previous hosted agents;
- development + exploratory evidence;
- fresh validation result when used for promotion;
- package parity result;
- expected matchup strengths/weaknesses;
- hosted errors/anomalies;
- observed rating/episode progression;
- whether it remains useful as calibration, champion or final candidate.
