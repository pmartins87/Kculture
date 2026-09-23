# V28E — Hosted Opponent-Strength Attribution Protocol — 2026-09-22

## Status

PRE-REGISTERED after V28D completed and after the >=100-episode maturity checkpoint.

No Kaggle submission, deletion, or slot reordering is authorized.

## Motivation

At the launch snapshot:
- exact V47 `56466970`: 119 listed episodes, publicScore 1861.4;
- ALL3 `56367770`: 430 listed episodes, publicScore 1923.4;
- latest-two remains V47 + ALL3.

V28D found:
- V47 current hosted replays: 45W / 4T / 40L over 89 resolved games, score rate 0.5281, mean margin +6198;
- ALL3 in the exact V47 Episode-ID window: 9W / 14L over 23 games, score rate 0.3913, mean margin -1363;
- only one common opponent.

The raw W/L evidence therefore does not explain why V47 has the lower public Bradley-Terry score.

## Question

Does current opponent strength / matchmaking composition materially explain the V47 vs ALL3 public-rating gap?

## Mechanical repair amendment after R2

R2 workflow `35807122446` successfully downloaded the full Kaggriculture leaderboard: **9873 CSV lines including the header**. The analysis then failed because the full-download schema uses a UTF-8 BOM and title-cased columns (`TeamName`, `Score`) whereas the R1 top-20 display used lower-camel columns (`teamName`, `score`).

R3 normalizes leaderboard header names case-insensitively and reads with `utf-8-sig`. Team-name **values** remain exact-match only. No threshold, temporal alignment, metric, population, or decision rule changes.

## Mechanical repair amendment after R1

R1 workflow `35806944875` returned `V28E_MAPPING_INSUFFICIENT` because the CLI `--show` surface exposed only the top 20 leaderboard rows, producing 0% exact-name coverage for both hosted populations.

This is a mechanical acquisition failure only. No threshold, alignment rule, mapping rule, metric, or interpretation rule below is changed.

R2 replaces only the leaderboard acquisition surface with the documented full download command:
`kaggle competitions leaderboard kaggriculture --download -p <dir> -q`.

## Frozen evidence

1. Reuse the immutable V28D replay/summary artifact from workflow `35781539795`.
2. Query the current Kaggriculture leaderboard once at V28E-R2 runtime using the full leaderboard download command above.
3. Use leaderboard columns `teamName` and `score`.
4. Team identity is OFFLINE FORENSIC metadata only and is forbidden as a runtime policy feature.

## Temporal alignment

Use the same exact V47 Episode-ID window derived in V28D.

For ALL3, include only games whose episode IDs lie inside the V47 min/max Episode-ID window.

## Mapping

Match replay `opponent_team` to leaderboard `teamName` by exact stripped string first.

Report:
- mapped games / total games;
- mapped unique opponents / total unique opponents;
- unmapped opponent names.

Do not fuzzy-match names.

If either aligned population has <60% game-level mapping coverage, decision is:
`V28E_MAPPING_INSUFFICIENT`.

## Metrics

For mapped opponents report separately for V47 and aligned ALL3:
- games;
- unique opponents;
- mean opponent public score;
- median opponent public score;
- p25 / p75 opponent public score;
- min / max opponent public score;
- score rate against mapped opponents;
- mean terminal margin against mapped opponents.

Primary difficulty deltas:
- mean opponent score: ALL3 minus V47;
- median opponent score: ALL3 minus V47.

Also report outcome by opponent-score bins:
- <1500
- 1500–1799.9
- 1800–2099.9
- >=2100

## Frozen interpretation

If mapping is sufficient:

- `V28E_ALL3_FACED_MATERIALLY_STRONGER_POPULATION` when both mean and median opponent-score deltas (ALL3 minus V47) are >=100.
- `V28E_V47_FACED_MATERIALLY_STRONGER_POPULATION` when both deltas are <=-100.
- otherwise `V28E_OPPONENT_STRENGTH_MIXED_OR_SMALL`.

This is attribution evidence only. It does not authorize a slot mutation.

## Next routing

- If ALL3 faced a materially stronger population, preserve pair and interpret much of the rating gap as matchmaking composition.
- If V47 faced a materially stronger population, preserve pair and treat the low V47 rating as even less consistent with simple weakness; continue maturity.
- If opponent-strength difference is mixed/small, preserve pair and treat public-score divergence as unresolved Bradley-Terry dynamics/sample path; continue maturity to >=169 and prefer fresh common-panel evidence for strategy decisions.

No new Kaggle submission is authorized.
