# CR026 continuation — 2026-09-05

> **Latest:** run 33973134213 completed. Rank 5 selected for CR026A: 16/16 direct, +2 paired score, zero regressions. Actual CR024 audit: 20/20 exact traces/rewards. Follow [CR026A_FROZEN_FOLLOWUP](CR026A_FROZEN_FOLLOWUP.md) and workflow `cr026a-fresh-gate.yml`; earlier active-screen instructions below are historical.

This is the current operational entrypoint; it supersedes the older continuation lists in HANDOFF, STATUS and ROADMAP.

## Confirmed state

- CR024 Consensus is Kaggle submission **56025052**, user screenshot around **1600**, selected loss episode **105806355**. This is a rating snapshot, not a proven final score.
- CR015 previously completed at **1577.6**, per Chat5 handoff supplied by user.
- CR025 closed: 168/168 pairs, no extra W/L, mean margin -114.69 vs CR024; do not submit.
- CR026 Phase 0 run **33948513661** succeeded: 10 exact source reproductions, 20 games, **8 wins / 12 losses**, mean margin **-1430.55**, zero errors.
- By source winner family: keiz 6-8; Crop Dusta 2-2; Jesse Bullard 0-2. These are action-tape opponents, NOT reruns of their adaptive programs.
- The old 168/168 regression panel is saturated and cannot select a competitive successor.
- Do not repeat CR008/CR015 for temporal controls: user explicitly rejected that direction. Use materially new strategies.

## Active work

`cr026-backbone-screen.yml` implements an exploratory ten-route screen plus exact hosted CR024 forensics.

1. Reproduce the ten highest-rated official 2026-09-04 source episodes before extracting winners.
2. Screen every winner route directly vs CR024 on 8 newly allocated development seeds, both seats (16 games per route).
3. Use two more development seeds, both seats, against the first-ranked source from each of the three winner families. Exclude the candidate's entire source family; compare candidate and CR024 on identical remaining rows (8 games per route).
4. Shortlist only if direct score >=10/16, positive mean direct margin, paired gain >=1 point, and <=2 paired regressions. This is a small exploratory filter, NOT validation or hosted authorization.
5. Rank eligible candidates by paired W/L gain, direct W/L, then margin. Candidate changes require fresh tests. If no candidate passes, use observed hosted failure mechanisms rather than relaxing this filter.
6. Before a new hosted package: test the frozen selected candidate against reactive opposition/fresh scenarios, inspect actual hosted loss mechanisms and package execution, and check current upstream/rules.

Research metadata (team/episode/seed) never enters runtime policy. Raw competition data stays transient or in CI artifacts, not repository source. Held-out remains 32/32 sealed.

## Hosted diagnostic

Official authenticated API lists public completed games of submission 56025052. Bounded sample: latest up to 12 losses, 8 wins, 4 ties/unknown. Counts describe returned API metadata, not necessarily all lifetime games. Sample win rate must not be interpreted as unbiased.

For each sampled replay: compare actual hosted actions against frozen CR024 tape; replay both recorded action streams in the frozen engine; measure phase money/production differences. Shared public observation fields are restored for seat 1 only where omitted; private inventories are never copied between players. Flags are observational, not causal proof.

## Continue without asking the user to operate their PC

Inspect the latest `cr026-backbone-screen` run, especially hosted diagnosis and aggregate. If a job fails mechanically, fix that cause without retuning strategic thresholds. Record the actual run ID and outcomes here. No candidate may inherit a previous pass after code changes.

The user should not submit CR025 or repeat old agents. Give a new exact package only after it is ready. If a remote experiment is still running at handoff, provide its link and a concrete next-check interval; do not imply the assistant continues working after its turn ends.
