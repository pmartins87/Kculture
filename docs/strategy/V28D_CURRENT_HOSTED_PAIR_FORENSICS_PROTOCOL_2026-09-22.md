# V28D — Current Hosted Pair Forensics Protocol — 2026-09-22

## Purpose

Determine whether the new exact-V47 hedge is genuinely underperforming in the current hosted population, rather than merely carrying a lower early Bradley-Terry rating because of matchmaking/population mix.

This stage is strictly read-only. It cannot submit, delete, reorder, or otherwise mutate Kaggle submissions.

## Active pair under audit

- exact V47: submission `56466970`;
- ALL3: submission `56367770`.

O-RW1 `56336027` is historical/inactive and is not treated as a current-population control.

## Evidence

Collect:
- all currently listed public replays for V47, capped only above 192;
- newest 256 public replays for ALL3.

For each replay, resolve:
- episode ID;
- target seat;
- opponent team;
- W/L/T;
- terminal reward margin.

## Temporal alignment

Episode IDs are used only offline as a recency ordering/index.

Let:
- `v47_min_episode` = minimum V47 episode ID in the collected V47 corpus;
- `v47_max_episode` = maximum V47 episode ID.

Primary aligned ALL3 population:
- ALL3 episodes whose IDs fall in `[v47_min_episode, v47_max_episode]`.

Fallback if fewer than 20 ALL3 games fall in this exact range:
- newest ALL3 games with episode ID >= `v47_min_episode`;
- if still fewer than 20, newest 96 ALL3 games.

The fallback must be reported explicitly.

## Comparisons

Report:
1. overall V47 score rate and mean/median margin;
2. aligned ALL3 score rate and mean/median margin;
3. opponent-mix distribution for each;
4. common opponents;
5. per-common-opponent W/L/T and margins;
6. macro-average score rate and mean margin across common opponents, weighting each opponent equally;
7. micro-average common-opponent score rate and margin;
8. V47-only and ALL3-only opponents.

No opponent identity may be used as a runtime policy feature. Identity is offline forensic metadata only.

## Interpretation

This is a diagnostic, not an automatic slot mutation.

Evidence of current-meta weakness is materially stronger if:
- V47 trails aligned ALL3 overall;
- V47 also trails on common-opponent macro averages;
- the gap persists across multiple common opponents rather than being driven by one opponent.

A lower hosted score alone is insufficient because the two submissions may have faced different populations.

No new Kaggle submission is authorized by V28D regardless of result. Any slot mutation requires a separate gate and explicit user authorization.
