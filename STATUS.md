# STATUS — Kculture

Last updated: 2026-08-25

## Mission status

**Phase: R0 — repository and competition intake**

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

## Immediate next actions

1. Confirm competition rules have been accepted.
2. Acquire the official environment, starter agent, rules/mechanics, and example submissions.
3. Reproduce a legal baseline locally.
4. Build a deterministic local episode runner and logging schema.
5. Reverse-engineer/verify all economically relevant mechanics from official rules and controlled experiments.
6. Create baseline strategy families and a local opponent pool.
7. Establish Elo/Bradley-Terry-style local tournament analysis plus raw profit/win diagnostics.
8. Submit the first valid agent only after local validation.
9. Track all ladder submissions and episodes in `docs/SUBMISSION_LEDGER.md`.

## Promotion gates

- **R0 PASS:** official mechanics, environment, submission contract, and evaluation captured.
- **R1 PASS:** official/simple baseline reproduced locally.
- **R2 PASS:** reliable simulator/runner and episode logging established.
- **R3 PASS:** first valid ladder submission with local↔hosted behavior reconciled.
- **R4 PASS:** economically strong deterministic baseline beats simple strategy pool.
- **R5 PASS:** planning/resource-allocation agent beats R4 across diverse opponents/seeds.
- **R6 PASS:** market/opponent-aware adaptations produce robust incremental value.
- **R7 PASS:** automated strategy search/tuning produces held-out gains.
- **R8 PASS:** candidate pair selected for strategic diversity and final robustness.
- **R9 PASS:** final two submissions frozen, independently reproduced, and submitted.

## Known strategic risk

The ladder is adaptive and noisy. A high displayed rating can reflect matchup composition, recency, or metagame exploitation. Final promotion must therefore rely on controlled local tournaments, episode-level diagnostics, strategic diversity, and robustness rather than leaderboard rating alone.
