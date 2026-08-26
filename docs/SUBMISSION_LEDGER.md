# Submission ledger — Kculture

Record every Kaggle agent submission here. The ordering matters because only the latest two submissions remain tracked for final evaluation.

| ID | UTC timestamp | Git SHA | Agent/version | Local win rate | Ladder rating | Episodes | Tracked slot | Notes |
|---|---|---|---|---:|---:|---:|---|---|
| unknown | 2026-08-26 04:37 snapshot | `29a883aba3df6347d72e321c9970c9694e0b6fa0` | `R4B-market-only-validated-v1` | 81-15-0 / 96 vs current public strong panel (development, descriptive) | **161.6** | unknown | latest / yes | Kaggle UI shows green check and `Complete`; filename `Kculture_R4B_market_only_validated_v1_submission.tar.gz`; first hosted rating snapshot is far below the simulation default initialization of 600 and is treated as a live-score anomaly requiring episode-level diagnosis, not as a normal ~3000 starting value. |

## Submission 1 identity

User-visible Kaggle evidence captured at approximately **2026-08-26 04:37 UTC** (phone local time 2026-08-25 23:37 -05:00):

- status: **Complete** / green validation check;
- filename: `Kculture_R4B_market_only_validated_v1_submission.tar.gz`;
- description: `Kculture R4B market-only validated v1`;
- displayed score: **161.6**;
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

Kaggle simulation submissions are initialized at a default rating of **600** after the validation episode. Ratings then move with win/loss/tie outcomes; coin margin does not determine rating movement. Therefore **161.6 is a real post-initialization downward movement**, not an expected first display value and not directly comparable to the ~2900–3100 mature public-agent benchmark scores as though all submissions start there.

The first hosted contradiction is now a first-class research signal. Do not assume the agent will automatically climb to ~3000. Diagnose hosted W/L/replays as soon as submission ID/episode access is available, while continuing reproducible local development.

## Required notes per submission

- exact source/config
- strategy family
- local validation summary
- expected matchup strengths/weaknesses
- validation-episode result
- hosted errors/anomalies
- whether it is currently one of the latest two tracked agents
- whether it remains a final candidate
