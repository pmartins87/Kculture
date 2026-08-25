# KEXP-20260825-002 — R2 laboratory smoke

## Question

Do the first deterministic episode logger and seed-and-seat tournament harness execute full 720-turn Kaggriculture games cleanly on the frozen environment and preserve enough raw evidence for R2?

## Setup

- Kculture commit: `6c59e6f66ed8c6eecc1a9272c0f891d488fdb031`
- Environment: `kaggle-environments==1.32.7`
- GitHub Actions run: `32858992202`
- Episode logger check: Kculture reference vs official `starter`, seed 505
- Tournament check: Kculture reference vs `pass` and official `starter`, seeds 501 and 502, both candidate seats

## Results

### Single episode logger

Seed 505 completed `DONE/DONE` at 3589–3589. Both sides produced the same action counts:

- HARVEST: 9
- PLANT: 10
- WATER: 30
- PASS: 671
- BUY_SEED: 11
- SELL: 9

### Tournament harness

Eight episodes completed with zero errors:

- vs `pass`: 4 wins, 0 losses, 0 ties; mean money delta +624;
- vs official `starter`: 0 wins, 0 losses, 4 ties; mean money delta 0;
- overall: 4 wins, 0 losses, 4 ties; tie-half score rate 0.75; mean money delta +312.

The artifact `local-lab-smoke` was preserved as ID `9567497530` with ZIP digest `sha256:1895a47b9ded8712a2ae0a0e00fac91df2ecbe9e69ce849a59d65f0fc3cb40f1`.

## Finding

The basic runner/logging path is valid. One methodological hardening remains before R2 can be called complete: file-based agents should be loaded into fresh module state for every episode so global state cannot leak between matches. Seed partitions and a versioned opponent pool should also be frozen and exercised in CI.

## Decision

**R2 core runner: PASS; R2 overall: continue.**

Next increment: fresh-per-episode file loading, disjoint development/validation/held-out seeds, deterministic crop opponent pool, and a hash-pinned strong public benchmark.
