# V27B Attempt 1 Mechanics Invalid — 2026-09-21

## Attempt 1

Workflow: `35672298198`.

Outcome:
- 4/4 shards failed mechanically;
- every episode itself finished `DONE/DONE`;
- each episode captured only 13/15 frozen checkpoints;
- 0 strategic V27B horizon result is binding.

## Root cause

The first implementation executed all legal-history reconstruction replays inside the live Kaggle agent callback.

At late checkpoints, especially with long/FULL history horizons, the callback performed hundreds of additional teacher calls before returning the real action. This contaminated the live per-turn runtime budget and prevented the candidate callback from being invoked at all late frozen checkpoints, even though the environment still finished the episode.

This is a measurement-instrumentation failure, not evidence about teacher history dependence.

## Mechanical correction

Binding semantics are unchanged.

The corrected runner:
1. runs the ongoing teacher normally during the episode;
2. records every legal candidate observation/configuration and the ongoing teacher action at frozen checkpoints;
3. after the episode ends, reconstructs each frozen history horizon offline from those recorded legal observations;
4. compares the reconstructed action to the ongoing binding action.

The correction changes only when the counterfactual replay is computed, never:
- teacher SHA;
- opponents;
- seeds;
- seats;
- checkpoints;
- history horizons;
- parity metrics;
- selection gates.

To reduce wall-clock time without changing the experiment, the corrected run uses 12 shards instead of 4.

Corrected binding workflow:
**`35676166396`**.

No Kaggle submission is authorized.
