# Fast Engine Gate — 2026-09-17

## Decision

Use `destbreso/kaggriculture-cppsim` as the candidate exact-engine foundation for the full-solver campaign, pinned initially to:

`f0084b916343c37bbcbdc7de9d833dc96caff78f`

License: Apache-2.0.

Do **not** treat the advertised 24k episodes/sec as RL throughput. That number is L0 fixed-stream throughput on the author's 10-core Mac mini M4. The current public engine has:

- L0 fixed-vs-fixed `Stream` / `run_many`, multithreaded;
- L1 `Game(seed) / observe(player) / step(a,b)` for live Python agents;
- exact 1.32.7 parity claims backed by bundled traces and negative-control 1.32.6 failures;
- extensive settle/farm/efficiency telemetry;
- **no L2 vectorized tensor API yet**.

The upstream roadmap explicitly identifies L2 `VecGame` + batched tensor observations as the missing layer for RL at scale. That maps directly to our need. Therefore the campaign order is:

1. pin and install upstream;
2. run upstream golden/L1 validation;
3. run our own V4 exact-bank parity on fresh seeds;
4. benchmark Ryzen L0 core scaling and L1 adaptive throughput;
5. freeze a tensor schema derived from the intended policy/value network;
6. build or vendor a local L2 vectorized layer;
7. only then start continuous actor/learner training.

## Why this is a regime change, not another V4 tweak

S0 and S1 both sit at roughly 485 hosted. The S1 value model improved regret inside a five-macro V4 self-play world but did not transfer materially to the Kaggle ladder. The failure is not a reason to tune the five macros harder; it is evidence that the training world and action space are too small.

The full-solver campaign will use the exact engine to generate a much larger state/action distribution, with search and league opponents. The Ryzen should eventually run continuously with checkpoints, not in isolated 10–20 minute rollout batches.

## Important limitation discovered from the fast-engine source

The 24k headline is **not** immediately available to an adaptive Python policy. L1 still crosses Python and constructs dict observations each turn, and upstream reports that a heavy Python agent is only around 15x faster than the official environment. This is still useful for validation and adaptive arenas, but it is not enough for the desired continuous RL scale.

The key engineering target is therefore L2 or equivalent: keep many `Sim` states in C++, advance them in parallel, expose compact tensors in batches, run policy/value inference once per batch, and return compact encoded actions. The network representation and L2 schema must be designed together.

## Upstream facts audited

The downloaded Kaggle notebooks identify the maintained repo as `destbreso/kaggriculture-cppsim`. The current repo states:

- engine target `1.32.7`;
- bit-exact lineage from nikital7's public C++ port;
- 6/6 bundled traces exact through 719 steps;
- negative control: pristine 1.32.6 fails all 1.32.7 traces;
- L1 lockstep observation validation plus adaptive-agent bank parity;
- L0 work-stealing pool; author measurement 4,139 eps/s single-thread and 24,442 eps/s all-core on Mac mini M4;
- telemetry for silent refusals, starvation, drought, rot, dead actions, idle capacity and stranded terminal stock.

These are upstream claims until reproduced on the Ryzen. `tools/prize_solver_fast_engine_gate.py` is our independent adoption gate.

## PASS criteria before multi-day training

- `kaggle-environments == 1.32.7`;
- `kagsim.ENGINE_VERSION == 1.32.7`;
- upstream golden/L1 tests pass on the Ryzen;
- V4 final banks are exact between official and kagsim L1 on fresh seeds;
- L0 results are identical across thread counts;
- Ryzen L0 and L1 throughput are recorded with multiple repetitions;
- no divergence is tolerated: wrong-but-fast is FAIL.

After the gate passes, use measured L0:L1 gap to decide how aggressively L2 must remove Python/dict overhead. No PPO or other RL algorithm is launched before this infrastructure decision is grounded in actual Ryzen numbers.
