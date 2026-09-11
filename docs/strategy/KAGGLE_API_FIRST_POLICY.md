# Kaggle API-First Policy

Status: ACTIVE / project-wide

For the Kculture/Kaggriculture competition, authenticated Kaggle API access is the primary data path whenever the API exposes the required information.

Operational rules:

1. Prefer authenticated Kaggle API/CLI access over browser screenshots for account-specific and competition-specific data.
2. Use the API proactively for the maximum useful evidence available: submissions, submission limits, episodes, replays, competition metadata, leaderboard/public standings when exposed, datasets, files and other competition resources.
3. Browser screenshots are secondary evidence/fallback for UI-only state or when an API endpoint does not expose a field.
4. Hosted episode/replay evidence from the user account must be frozen into artifacts and used in strategy diagnosis whenever relevant.
5. API-derived hosted evidence does not override the scientific promotion rules: W/L is primary; both seats and fresh validation remain required; no automatic Kaggle submission without user authorization.
6. Never omit authenticated API access merely because the public Kaggle webpage/API is sufficient for a subset of the task.
7. When an API-backed workflow returns an authentication/permission error, first verify that KAGGLE_API_TOKEN is actually passed to that workflow before concluding the data is unavailable.
8. Preserve API-derived findings, hashes, run IDs, artifacts, decisions and resulting strategy hypotheses in the repository so they survive chat boundaries.

Rationale: authenticated API access is a high-value project capability and should be treated as standard infrastructure, not an exceptional/manual fallback.

## 2026-09-11 operational repair

The legacy main-branch scheduled forensics had hardcoded R4B/KEXP050 IDs. Current
collection must resolve the latest two successful submissions through the API,
then take the newest explicitly ordered replay window; no old label may be
treated as the active candidate. A successful workflow does not imply current
data unless its submission IDs/timestamps were checked.
