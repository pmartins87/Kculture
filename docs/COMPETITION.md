# Competition facts — Kculture

Verified against the Kaggle competition pages on 2026-08-25.

## Task

Build an autonomous agent for a 30-day farming simulation. Two players manage separate farms and compete to finish the season with the most money.

## Episode structure

- 24 turns per in-game day
- 30 days per season
- 720 total turns
- Each turn supports farmer/farm-hand actions such as movement, planting, watering, harvesting, animal care, inventory movement, purchasing, selling, and expansion subject to game rules.
- Farms are separate, but opponent farm state is observable enough to support strategic adaptation; some private inventory information is hidden.

## Submission contract

- `main.py` must be at the submission archive root.
- `main.py` exposes an `agent` function.
- Single-file or multi-file tar.gz submissions are supported by the competition instructions.
- A validation episode runs the submission against a copy of itself before ladder entry.

## Ladder/evaluation behavior

- Up to 5 agents may be submitted per day.
- Bots play episodes against similarly rated opponents.
- Ratings move with wins/losses/ties.
- Only the latest 2 submissions remain tracked.
- Those latest 2 submissions are also used for final leaderboard evaluation.
- The leaderboard displays the best-scoring tracked bot.
- Newer bots receive more frequent games.
- Final games continue after the submission deadline until the ladder converges.

This makes submission order strategically important: replacing one of the latest two slots can remove an older agent from final tracking.

## Timeline

- Start: 2026-07-29
- Entry deadline: 2026-09-23 23:59 UTC
- Team merger deadline: 2026-09-23 23:59 UTC
- Final submission: 2026-09-30 23:59 UTC
- Final evaluation games: approximately 2026-10-01 through 2026-10-15, or until convergence

## Prizes

US$50,000 total: places 1 through 10 each receive US$5,000.

## Strategic implications

- Optimize for head-to-head win probability, not merely raw farm profit in isolation.
- Ladder rating is a noisy observation of skill and matchup mix.
- Two final tracked agents can be treated as a portfolio with complementary matchup profiles.
- Validation and crash resistance are prerequisites; a strategically strong agent that errors cannot enter the ladder.

## Official source

https://www.kaggle.com/competitions/kaggriculture
