# STATUS — Kculture

Last updated: 2026-08-25

## Mission status

**Phase: R0 active; R1 baseline reproduction and R2 runner scaffolded**

Goal: produce a **top-10 final result** in Kaggriculture, where each of the top 10 positions pays US$5,000.

## Confirmed competition constraints

- Entry deadline: 2026-09-23 23:59 UTC.
- Final submission deadline: 2026-09-30 23:59 UTC.
- Final games continue after close until leaderboard convergence, approximately through 2026-10-15.
- One match spans 30 in-game days × 24 turns = 720 turns.
- Submission must expose an `agent` function from `main.py` at the archive root.
- Up to 5 agents may be submitted per day.
- Only the latest 2 submissions remain tracked and are used for final leaderboard evaluation.
- Validation episode runs the agent against itself before ladder entry.
- Default hosted action timeout is 1 second.
- Submission resources documented by Kaggle: 6.5 GiB RAM, 1.6 vCPU, 8 GiB disk, 100 MiB submission limit.

## R0 acquisition completed

- Official environment source identified: `Kaggle/kaggle-environments`.
- Frozen PyPI package for reproduction: `kaggle-environments==1.32.7` (released 2026-08-15).
- Frozen latest engine-changing commit at intake: `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`.
- Upstream file blob hashes recorded in `official/UPSTREAM_LOCK.md`.
- Official advanced environment specification version captured as `0.1.0`.
- Current official mechanics/market snapshot captured in `docs/OFFICIAL_MECHANICS_SNAPSHOT.md`.
- Official built-in `starter_agent` behavior captured.

## R1/R2 bootstrap completed

- Root `main.py` contains a self-contained reference port of the official deterministic carrot starter.
- Automated 720-turn/parity smoke test added at `tools/smoke_baseline.py`.
- GitHub Actions smoke workflow added at `.github/workflows/baseline-smoke.yml`.
- Deterministic single-episode runner added at `tools/run_episode.py`; it records package version, git SHA, seed, agents, statuses, rewards, money delta, action counts, summary JSON, and full replay JSON.

## Remaining R0 blocker

Competition rule acceptance is account-side and is not yet independently verified in this repository. Confirm via Kaggle UI (`Join Competition` already accepted) or `kaggle competitions list --group entered`.

## Immediate next actions

1. Observe the baseline smoke workflow produced by the R0/R1 bootstrap commit.
2. If parity passes, record **R1 PASS**: Kculture reference baseline matches the official built-in starter on fixed seeds and completes full self-play.
3. Exercise `tools/run_episode.py` in CI and freeze its output schema; then expand toward multi-seed/multi-opponent tournament execution for **R2**.
4. Add controlled mechanics tests for crop yields/decay, animal feed/care, fertilizer, land unlocking, hire cost/placement, shed capacity, market order limits, market-price curves, and town demand.
5. Establish the first local opponent pool (`pass`, official `starter`, scripted crop loops, expansion/livestock variants).
6. Add tournament summaries with raw W/L/T, money delta, variance/tails, crash/no-op diagnostics, and optional Elo/Bradley-Terry summaries.
7. Submit the first ladder agent only after local validation and account-rule confirmation.
8. Track all ladder submissions and episodes in `docs/SUBMISSION_LEDGER.md`.

## Promotion gates

- **R0 PASS:** official mechanics, environment, submission contract, evaluation, and account entry captured/confirmed.
- **R1 PASS:** official/simple baseline reproduced locally with deterministic diagnostics.
- **R2 PASS:** reliable simulator/runner and episode logging established.
- **R3 PASS:** first valid ladder submission with local↔hosted behavior reconciled.
- **R4 PASS:** economically strong deterministic baseline beats simple strategy pool.
- **R5 PASS:** planning/resource-allocation agent beats R4 across diverse opponents/seeds.
- **R6 PASS:** market/opponent-aware adaptations produce robust incremental value.
- **R7 PASS:** automated strategy search/tuning produces held-out gains.
- **R8 PASS:** candidate pair selected for strategic diversity and final robustness.
- **R9 PASS:** final two submissions frozen, independently reproduced, and submitted.

## Known strategic risks

The ladder is adaptive and noisy. A high displayed rating can reflect matchup composition, recency, or metagame exploitation. Final promotion must therefore rely on controlled local tournaments, episode-level diagnostics, strategic diversity, and robustness rather than leaderboard rating alone.

A second risk is environment drift: the engine changed materially on 2026-08-15 to make underused resources (notably carrot, tomato, goose/egg) situational through demand-curve changes. Every promoted agent must be regression-tested whenever Kaggle updates the environment.
