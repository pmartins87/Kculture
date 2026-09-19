# Option-Value Ryzen V1 Smoke Result — 2026-09-19

Workflow `35417513885`.

## Result

One fresh seed, V47 mirror, seat 0, one worker.

- completed seeds: 1/1;
- O-RW1 labels: 1;
- O-TW1 labels: 1;
- total labels: 2;
- unique state hashes: 2;
- failures: 0;
- resumable shard/aggregate path: PASS.

Smoke wall time for the seed on GitHub runner:
approximately 48 seconds from generator start to completion.

Binding verdict:
**`OPTION_VALUE_RYZEN_V1_SMOKE_PASS`**.

## First production batch

Use the validated local WSL/Ryzen environment:
- repo: `~/Kculture`;
- branch: `research/prize-solver-v0`;
- venv: `.venv-ps2`;
- first batch: 250 fresh seeds;
- opponents: V47 mirror, V48, Tactical Memory;
- both seats;
- options: O-RW1 + O-TW1;
- expected maximum labeled rows: 3,000;
- resumable one-shard-per-seed output: `runs/option_value_v1_250`.

No Kaggle submission is part of this run.
