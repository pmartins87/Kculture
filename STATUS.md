# STATUS — Kculture

Last updated: 2026-08-25

## Mission status

**Technical phase: R2 — local tournament laboratory.**  
**R1: PASS.**  
**R0 account-side confirmation still pending:** competition rule acceptance cannot be independently verified from the repository.

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

## R1 PASS evidence

Experiment: `KEXP-20260825-001-official-starter-parity`.

Kculture `main.py` is a self-contained port of the official deterministic carrot starter. On GitHub Actions run `32858531629`:

- seed 101: full terminal-state parity PASS; reward 3620;
- seed 202: full terminal-state parity PASS; reward 3601;
- seed 303: full terminal-state parity PASS; reward 3643;
- self-play seed 404: both agents `DONE`, 3771–3771;
- all workflow steps passed;
- smoke artifact ID `9567214356`, digest `sha256:734f1eed2211d8439da10b8c7414a36f2bc36f2e9f946aa3fe826a2075c54e67`.

The official starter is now frozen as the legal/reference baseline and should not be strategically modified in place.

## R2 infrastructure

- `tools/run_episode.py`: deterministic single-episode runner/logging with environment version, git SHA, seed, agents, terminal statuses/rewards, money delta, action counts, compact summary, and full replay.
- `tools/run_tournament.py`: multi-seed tournament harness; runs the candidate from both player seats by default, preserves raw episode outcomes, and aggregates W/L/T, score rate, money delta mean/median/dispersion/tails, and errors.
- Built-in `random` is explicitly unsuitable for deterministic promotion gates because the upstream random agent creates an unseeded RNG.
- CI is being expanded to exercise both the episode logger and seed-and-seat tournament harness after baseline parity.

## Remaining R0 blocker

Competition rule acceptance is account-side and is not yet independently verified in this repository. Confirm via Kaggle UI (`Join Competition` accepted) or `kaggle competitions list --group entered` before the first hosted submission.

## Immediate next actions

1. Validate `tools/run_episode.py` and `tools/run_tournament.py` in a clean GitHub Actions run.
2. Freeze the R2 output schema and establish deterministic development/validation/held-out seed partitions.
3. Add controlled mechanics regression tests for crop yields/decay, animal feed/care, fertilizer, land unlocking, hire cost/placement, shed capacity, market order limits, market-price curves, and town demand.
4. Establish the first versioned local opponent pool: `pass`, official `starter`, scripted crop loops, expansion-heavy, livestock-heavy, and market-responsive variants.
5. Add matchup matrix and tournament summaries while keeping raw W/L/T and money deltas primary; Elo/Bradley-Terry remain secondary summaries.
6. Build the first economically competent deterministic strategy family only after the lab is reliable.
7. Submit the first ladder agent after local validation and account-rule confirmation; record it in `docs/SUBMISSION_LEDGER.md`.

## Promotion gates

- **R0 PASS:** official mechanics, environment, submission contract, evaluation, and account entry captured/confirmed. Technical acquisition complete; account entry confirmation pending.
- **R1 PASS:** official/simple baseline reproduced locally with deterministic diagnostics. **PASS on 2026-08-25.**
- **R2 PASS:** reliable simulator/runner, deterministic seed partitions, opponent pool, and episode/tournament logging established.
- **R3 PASS:** first valid ladder submission with local↔hosted behavior reconciled.
- **R4 PASS:** economically strong deterministic baseline beats simple strategy pool.
- **R5 PASS:** planning/resource-allocation agent beats R4 across diverse opponents/seeds.
- **R6 PASS:** market/opponent-aware adaptations produce robust incremental value.
- **R7 PASS:** automated strategy search/tuning produces held-out gains.
- **R8 PASS:** candidate pair selected for strategic diversity and final robustness.
- **R9 PASS:** final two submissions frozen, independently reproduced, and submitted.

## Known strategic risks

The ladder is adaptive and noisy. A high displayed rating can reflect matchup composition, recency, or metagame exploitation. Final promotion must therefore rely on controlled local tournaments, episode-level diagnostics, strategic diversity, and robustness rather than leaderboard rating alone.

Environment drift is also material: the engine changed on 2026-08-15 to make underused resources (notably carrot, tomato, goose/egg) situational through demand-curve changes. Every promoted agent must be regression-tested whenever Kaggle updates the environment.
