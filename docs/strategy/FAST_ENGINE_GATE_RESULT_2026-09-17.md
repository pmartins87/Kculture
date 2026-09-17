# Fast Engine Gate — Ryzen Result (2026-09-17)

Source: `FAST_ENGINE_GATE.json` generated on the user's Ryzen/WSL host.

## Result

`FAST_ENGINE_GATE_PASS`

Environment versions:

- CPU count: 32
- `kaggle-environments`: 1.32.7
- kagsim engine: 1.32.7
- pinned kagsim commit: `f0084b916343c37bbcbdc7de9d833dc96caff78f`
- platform: WSL2 Linux / Python 3.12.3

## Exact parity

V4-vs-V4 final banks were exact between official environment and kagsim L1 on all gate seeds:

- seed 11: `33188 / 34808`
- seed 23: `38160 / 22625`
- seed 47: `47756 / 35542`

All official runs completed 720 steps with status `DONE/DONE`.

## Throughput

Official adaptive loop:

- ~0.4442 episodes/s

kagsim L1 + Python V4:

- ~1.4700 episodes/s
- ~3.31x faster than official
- median ~0.681 s/episode

kagsim L0 fixed streams on Ryzen:

- 1 thread: ~4,943 eps/s
- 2 threads: ~10,099 eps/s
- 4 threads: ~20,234 eps/s
- 8 threads: ~39,905 eps/s
- 16 threads: ~72,409 eps/s
- 24 threads: ~82,219 eps/s
- 32 threads: ~86,763 eps/s
- auto threads: ~91,955 eps/s

The L0/L1 ratio is ~62,554x.

At 720 turns/episode, 91,955 episodes/s corresponds to about 66.2 million simulated game turns/s for fixed action streams. This does **not** mean an adaptive neural policy can achieve that number; it establishes the engine headroom and shows the Python callback path is the dominant bottleneck.

## Mechanical telemetry of current V4

The sampled V4 episode exposes severe execution inefficiency, confirming S0/S1 are unsuitable as the final architecture rather than merely under-tuned:

- 3 animals escaped;
- 29 plants dried;
- 23 animal-shed days;
- 26 animal-unfed days in one sampled side;
- 926 hand PASS turns (933 on the other side);
- 55 dead harvest actions (40 on the other side);
- 51 farmer PASS turns;
- 30/29 tile-cap units;
- 8/6 fertilizer opportunities forgone;
- 2,270 / 2,410 coins of silent capital/seed loss;
- hundreds of idle-tile days.

These metrics are training diagnostics only. They are not legal hosted observations and must never enter runtime policy state.

## Decision

1. Do not optimize V4/S1 incrementally.
2. Build L2 vectorized C++ simulation transport immediately.
3. Recover at least 100x over the L1 Python loop before adding neural inference.
4. Then build hierarchical policy/value + exact-state search + population/league training.
5. PPO remains optional and must pass an ablation against search/distillation, not be assumed as the core algorithm.

Next gate: `L2_VEC_GATE`.
