# KEXP-20260825-001 — Official starter parity

## Question

Does the Kculture root `main.py` reproduce the frozen official Kaggriculture `starter_agent` closely enough to establish the R1 reference baseline?

## Frozen setup

- Kculture commit under test: `ecb9839ef8937496144a92289062f121c5d80210`
- Environment: `kaggle-environments==1.32.7`
- Upstream engine change commit: `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`
- Candidate: Kculture `main:agent`
- Reference: official built-in `starter`
- Opponent for parity runs: built-in `pass`
- Parity seeds: 101, 202, 303
- Self-play seed: 404
- Episode length: 720 turns

For each parity seed, the Kculture port and official starter were run independently against `pass`. The test compared player-0 terminal status, reward, public farm state, private state, market, town, day, and hour.

## Results

| Seed | Kculture/reference terminal reward | Full terminal-state parity |
|---:|---:|---|
| 101 | 3620 | PASS |
| 202 | 3601 | PASS |
| 303 | 3643 | PASS |

Self-play at seed 404 completed with both agents `DONE` and a 3771–3771 tie.

GitHub Actions run `32858531629` completed successfully. Artifact `baseline-smoke` was preserved with artifact ID `9567214356` and ZIP digest `sha256:734f1eed2211d8439da10b8c7414a36f2bc36f2e9f946aa3fe826a2075c54e67`.

## Decision

**R1 PASS.**

The official carrot starter is now the frozen legal/reference baseline. Strategy improvements must be evaluated against this known-good behavior rather than modifying the reference in place.

Proceed to R2: deterministic episode logging, seed-and-seat tournament execution, mechanics regression tests, and a versioned opponent pool.
