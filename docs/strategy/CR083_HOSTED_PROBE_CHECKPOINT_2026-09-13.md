# CR083 hosted probe checkpoint — 2026-09-13

Status: **ACTIVE / STILL CONVERGING / NO RETUNING / NO NEW SUBMISSION**

## Identity and provenance

- Kaggle submission: `56199767`
- File: `CR083.tar.gz`
- Description: `CR083_FROZEN_PROBE_648FBCDB`
- Frozen SHA-256: `648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`
- Canonical local promotion workflow: `34715575445`
- Hosted submit workflow: `34740104210`
- Hosted forensic workflow: `34745898829`
- Forensic artifact: `cr083-hosted-forensics-v2-teamname`, artifact `10314660085`
- Fresh full-leaderboard artifact: `kaggle-api-current-frontier-refresh-v2-lightweight`, artifact `10313912424`
- Full leaderboard snapshot time: `2026-09-13T07:47:09 UTC`

The hosted probe is byte-identical to the locally promoted candidate. No CR083A/B/C exists and no nearby variant is authorized.

## Critical rating-system correction

Kaggle simulation submissions do **not** inherit the rating of the prior submission. A valid new submission is initialized at `mu_0 = 600` with high uncertainty and repeatedly matched against similarly rated opponents. Wins/losses/ties update the skill estimate and uncertainty shrinks with accumulated evidence. Money margin does not affect the rating update.

Therefore the first comparison `CR083 1563.9` versus mature `CR071M 1647.2` was not a valid maturity-equivalent verdict.

Observed live progression already supports this correction:

- early checkpoint: CR083 `1563.9`, CR071M `1647.2`, apparent gap `-83.3`;
- later authenticated checkpoint (`34745664559`, rerun job `103694087017`): CR083 **`1596.2`**, CR071M **`1642.4`**, gap narrowed to **`-46.2`**;
- the later checkpoint contains at least one public episode beyond the 36-replay forensic freeze.

CR083 is still climbing; its current live rating is not yet a terminal architecture verdict.

## 36-game hosted forensic freeze

The forensic run froze and downloaded 36 completed public CR083 replays, all successfully resolved from the official replay schema using `info.TeamNames` only for offline seat attribution and top-level `rewards` for final money.

Results:

- games: **36**
- wins: **27**
- losses: **9**
- ties: **0**
- raw hosted win rate: **75.0%**
- mean money margin: **+14,703.14**
- median money margin: **+6,385**
- min margin: **-38,184**
- max margin: **+108,140**
- seat 0: 14W–4L over 18 games
- seat 1: 13W–5L over 18 games

Seat balance is not the obvious failure mode. Money margins are diagnostic only; Kaggle rating is driven by episode result, not margin size.

## Fresh population cross-match

All **36/36** opponent team names matched exactly to the fresh full Kaggriculture leaderboard snapshot at `2026-09-13T07:47:09 UTC`.

Current-rating stratification:

| Opponent rating band | Games | CR083 W-L | Win rate | Mean opponent rating | Mean money margin |
|---|---:|---:|---:|---:|---:|
| `<1200` | 6 | 6-0 | 100.0% | 876.2 | +61,798.7 |
| `1200-1499` | 10 | 8-2 | 80.0% | 1,412.8 | +10,026.5 |
| `1500-1699` | 13 | 10-3 | 76.9% | 1,562.6 | +4,200.6 |
| `1700-1999` | 2 | 2-0 | 100.0% | 1,746.7 | +18,092.5 |
| `2000-2299` | 1 | 1-0 | 100.0% | 2,129.5 | +12,577.0 |
| `2300-2599` | 3 | 0-3 | 0.0% | 2,573.7 | -2,310.0 |
| `2600+` | 1 | 0-1 | 0.0% | 2,744.3 | -38,184.0 |

At this snapshot, rating `2300.8` is approximately rank 1000. Thus the most relevant current warning for prize-range transfer is:

**CR083 is 0-4 against the four opponents in this sample currently above 2300 / roughly top-1000 strength.**

Those four games are:

| Opponent | Current rank | Current rating | Result | Money margin |
|---|---:|---:|---:|---:|
| Annsatz | 145 | 2744.3 | L | -38,184 |
| Roshan Roy | 461 | 2589.7 | L | -3,243 |
| Veerakrishna | 479 | 2584.4 | L | -3,487 |
| Clement Lau | 584 | 2546.9 | L | -200 |

This is a **small sample** and cannot by itself close CR083. It is, however, much more relevant to the top-10 objective than unweighted W/L over mostly lower-rated opponents.

For comparison:

- opponents in CR083 wins have mean current rating about **1390.1**;
- opponents in CR083 losses have mean current rating about **2028.2**;
- against current rating `>=2000`, CR083 is **1-4** over 5 games;
- against current rating `>=2300`, CR083 is **0-4** over 4 games.

## Current frontier context

Fresh leaderboard snapshot:

1. Majkel1337 — `3217.2`
2. Mengfei Li — `3068.7`
3. THIRD FARM CLUB — `3034.7`
4. ymg_aq — `3034.2`
5. Artem The Farmer — `3028.0`
6. SpaTaro — `3021.9`
7. feel the agi — `3002.8`
8. Otter Vibe — `2990.0`
9. Subramanya N — `2974.9`
10. binghua — `2970.8`

Useful population thresholds in the same snapshot:

- rank 100: `2782.8`
- rank 500: `2578.1`
- rank 1000: `2300.8`
- rank 2000: `1679.7`

The top-10 problem is therefore not solved by beating the current 1200–1700 population reliably; the architecture must retain positive transfer as opponent strength rises.

## Frozen maturity rule

Kaggle does not publish a fixed episode count at which a simulation submission is fully converged. To prevent subjective score-watching, this project adopts the following **operational heuristic**, not an official Kaggle rule:

1. Do not make the final CR083 hosted verdict before **100 completed public episodes**.
2. At/after 100 episodes, re-freeze all public replays and recompute:
   - current rating and trend;
   - overall W/L/T;
   - W/L against current `>=2000`, `>=2300`, top-1000 and top-500 opponents;
   - seat split;
   - opponent-strength distribution.
3. If CR083 reaches mature CR071M rating before 100 games, that is encouraging but **not sufficient** to promote a derivative architecture; high-strength transfer remains mandatory evidence.
4. No CR083 parameter may be retuned from these hosted outcomes.

## Proxy-gap conclusion

The old local promotion panel answered: *does this mechanics-valid intervention improve CR071M and preserve legacy-anchor performance?*

It did **not** answer: *does the resulting policy remain strong against the upper live population?*

That missing question is now binding. Future promotion protocols must add an independent population-strength gate before hosted submission. The population gate must be based on legal offline analysis / current-observation regimes and may never make team identity, hidden seed, EpisodeId, future state or opponent-private state available to the runtime agent.

## Decision

**KEEP_CR083_LIVE_AND_IMMUTABLE_UNTIL_100_PUBLIC_EPISODE_CHECKPOINT**

In parallel, build the next evaluation layer around high-strength live-population regimes. Do not submit another candidate merely to obtain another live roll.
