# Submission ledger — Kculture

Record every Kaggle agent submission here. The ordering matters because only the latest two submissions remain tracked for final evaluation.

| ID | UTC timestamp | Git SHA | Agent/version | Local win rate | Ladder rating | Episodes | Tracked slot | Notes |
|---|---|---|---|---:|---:|---:|---|---|
| unknown | 2026-08-26 12:00 snapshot | `29a883aba3df6347d72e321c9970c9694e0b6fa0` | `R4B-market-only-validated-v1` | 81-15-0 / 96 vs current public strong panel (development, descriptive) | **135.7** | unknown | latest / yes | User-visible Kaggle screenshot, status `Complete` / green check. Rating declined further from the earlier 161.6 snapshot, strengthening the conclusion that hosted calibration/matchups materially disagree with the local public-agent panel. |
| unknown | 2026-08-26 04:37 snapshot | `29a883aba3df6347d72e321c9970c9694e0b6fa0` | `R4B-market-only-validated-v1` | 81-15-0 / 96 vs current public strong panel (development, descriptive) | **161.6** | unknown | latest / yes | First observed hosted rating snapshot. |

## Submission 1 identity

User-visible Kaggle evidence:

- status: **Complete** / green validation check;
- filename: `Kculture_R4B_market_only_validated_v1_submission.tar.gz`;
- description: `Kculture R4B market-only validated v1`;
- displayed score progression observed so far: **161.6 → 135.7**;
- latest screenshot: phone time 2026-08-26 07:00 at UTC-05:00, approximately **2026-08-26 12:00 UTC**;
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

Kaggle simulation submissions initialize around rating **600** after validation and then move with win/loss/tie outcomes; terminal coin margin does not directly determine rating movement. The sequence **161.6 → 135.7** is therefore meaningful evidence of continued poor hosted results, not a package-validation error and not a harmless difference in score scale.

This makes hosted calibration a first-class research signal. We should not assume automatic recovery and should not spend a second submission slot on an unvalidated reaction. Continue exact local development while seeking episode-level hosted evidence.

## Required notes per submission

- exact source/config
- strategy family
- local validation summary
- expected matchup strengths/weaknesses
- validation-episode result
- hosted errors/anomalies
- whether it is currently one of the latest two tracked agents
- whether it remains a final candidate
