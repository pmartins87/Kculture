# V26B — Teacher-Derived Persistent Policy Reconstruction Viability Protocol — 2026-09-21

## Status

DORMANT / PRE-REGISTERED while binding V26A workflow `35653189539` is still running.

Activate only if V26A returns:
`V26A_PRIZE_SOLVER_BASE_NOT_READY`.

Do not activate if PrizeSolverV4 passes its frozen architecture-headroom gate.

## Motivation

V25A proved that finite teacher prefixes do not transfer W/L headroom to ALL3; only persistent whole-episode teacher policy does.

V24B proved that exact per-source teacher imitation is not identity-free identifiable at turn 0: the same legal state can map to different teacher actions.

Therefore V26B does **not** try to recover source-specific policies.

It asks whether the current strong-policy bank contains a **source-agnostic persistent consensus policy** worth distilling.

## Binding source population

Use the exact immutable V26A current-frontier snapshot produced before V26A outcomes.

No live Kaggle source reacquisition.

All selected source SHAs are teachers. The same fixed teacher bank is used against every benchmark opponent.

Opponent identity, source rank, source SHA and functional cluster are prohibited as runtime routing inputs.

## Consensus teacher definition

At each candidate turn, evaluate every snapshot teacher on the same legal candidate observation.

Canonicalize each complete action.

Select the **modal complete canonical action**:
1. count exact complete action keys;
2. choose the action key with maximum support;
3. ties are broken lexically by canonical JSON action key.

The chosen action must be one of the teacher-emitted complete actions.

No component-level mixing.
No opponent-specific teacher subset.
No source-weighting.
No outcome-weighting.
No learned selector in V26B.

This defines one deterministic source-agnostic offline teacher ensemble.

## Viability benchmark

Fresh seeds:
`79601..79606`.

Both seats.

Use the same immutable current-frontier opponent snapshot as V26A.

Pair:
- CONTROL = exact V47+ALL3;
- CONSENSUS = persistent modal-teacher policy for all 720 turns.

Every opponent sees the same fixed teacher bank.

## Mechanical validity

Require:
- all benchmark contexts complete;
- exact snapshot SHAs;
- zero live Kaggle reacquisition;
- no teacher process failure;
- DONE/DONE, 720 steps, finite rewards;
- unique complete context grid.

Failure =>
`V26B_MECHANICS_INVALID`.

## Source-agnostic consensus headroom gate

CONSENSUS is viable only if all are true:

1. positive-score contexts >= 8;
2. positive contexts span >=3 opponent source SHAs;
3. positive contexts span >=3 fresh seeds;
4. mean score delta >0;
5. negative-score contexts <= positives/2;
6. CONTROL-win -> CONSENSUS-nonwin regressions <= positives/2;
7. positive contexts span >=2 CONTROL functional outcome clusters.

Decision:

### `V26B_CONSENSUS_POLICY_HEADROOM`
Gate passes.

Route:
- preserve the modal teacher ensemble as offline label oracle only;
- collect legal-state -> consensus-action data;
- distill one first-party persistent policy;
- split train/holdout by opponent functional cluster and seed;
- no source identity;
- fresh causal validation before any hosted package.

### `V26B_NO_SOURCE_AGNOSTIC_POLICY_HEADROOM`
Mechanics pass but gate fails.

Route:
- close teacher-imitation reconstruction from the current public policy bank;
- do not return to ALL3 option mining;
- do not brute-force PrizeSolverV4 training;
- move to competition-strategy reassessment:
  1. preserve strongest proven hosted candidate/control;
  2. finish paper/publication-quality solver evidence;
  3. only reopen solver work with a genuinely new learning/search architecture rather than another heuristic patch.

### `V26B_MECHANICS_INVALID`
Repair mechanics only; rerun exact same teacher bank, opponents, seeds and consensus rule.

## Anti-overfit rules

Forbidden after V26B outcomes:
- changing teacher weights;
- dropping teachers;
- opponent-conditioned teacher subsets;
- changing tie-break;
- changing seeds;
- changing W/L gate;
- using margin-only evidence to pass;
- source/rank/SHA runtime features.

## Kaggle

No V26B result directly authorizes submission.
