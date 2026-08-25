# Kculture

Competition workspace for **Kaggriculture** (Kaggle, 2026).

## Mission

Build a **top-10 prize-contending autonomous farming agent** through rigorous simulation, strategy search, opponent-aware evaluation, and disciplined submission iteration.

## Competition snapshot

- Host: Kaggle
- Prize pool: **US$50,000**
- Prize structure: **10 × US$5,000**
- Entry deadline: **2026-09-23 23:59 UTC**
- Final submission deadline: **2026-09-30 23:59 UTC**
- Final games continue after close until leaderboard convergence (approximately through 2026-10-15)
- Match length: **30 days × 24 turns = 720 turns**
- Submission: agent with `main.py` at archive root and an `agent` function
- Daily allowance: up to 5 submitted agents
- Only the latest 2 submissions remain tracked and are used for final leaderboard evaluation

## Repository map

- `STATUS.md` — current state and immediate next actions
- `ROADMAP.md` — milestone-based route to a top-10 final agent pair
- `HANDOFF.md` — starting point for a dedicated project chat
- `docs/COMPETITION.md` — mechanics, evaluation, constraints, deadlines
- `docs/EXPERIMENT_PROTOCOL.md` — reproducible agent evaluation discipline
- `docs/SUBMISSION_LEDGER.md` — submission/rating/episode log
- `research/README.md` — strategy hypotheses and metagame notes
- `src/README.md` — implementation architecture
- `experiments/README.md` — local experiments and tournament artifacts
- `submissions/README.md` — frozen competition agents

## Operating principle

Optimize for final competitive strength rather than a single noisy ladder rating. Every strategic change should be tested against controlled baselines, diverse opponents, and repeated seeds before promotion to a competition submission.

Official competition: https://www.kaggle.com/competitions/kaggriculture
