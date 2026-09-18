# Prize Solver Roadmap — 2026-09-16

## Current solver handoff — 2026-09-18

Active branch: `research/prize-solver-v0`.

The standalone programme router is closed. The synthetic one-turn SELL reorder/deferral
family is closed. The active Prize-Solver line is the first-party ready-WOOL option O-RW1.

### V2b wrapper-proposal oracle — PASS

Workflow `35310754131`:
- BASE score rate `0.500`;
- exact oracle score rate `0.625`;
- W/L delta **+0.125**;
- four non-win -> win flips;
- all promoted proposals came from Ready Stock;
- useful proposal: exact V47 market empty -> `SELL WOOL 2`.

### O-RW1 first-party causal isolation — PASS SAFE OPTION

Workflow `35311750191`:
- 48 valid branch states / zero failures;
- mean score delta **+0.1666667**;
- **16 non-win -> win flips**;
- **0 negative-W/L states**;
- mean margin delta **+14.9583**;
- **0 negative-margin states**.

Frozen first-party option:
```
if V47 market == []
and own private shed.WOOL >= 2
and step <= 671:
    proposal = SELL WOOL 2
```

### O-RW1 one-shot runtime transfer — PASS

Workflow `35313204723`, artifact `10534778422`, exact engine `1.32.7`:
- 64 paired matchups / 128 complete episodes;
- zero mechanical failures;
- BASE score rate **0.5000**;
- V47 + O-RW1 score rate **0.6875**;
- W/L delta **+0.1875**;
- **28 non-win -> win flips**;
- **0 win -> non-win regressions**;
- all 4 opponent blocks nonnegative in W/L;
- worst block W/L delta `0.0`.

Per opponent:
- V47 mirror: `0.500 -> 0.875`, delta **+0.375**;
- V48: `0.500 -> 0.875`, delta **+0.375**;
- Tactical Memory: `1.000 -> 1.000`;
- Ready Stock: `0.000 -> 0.000`.

Important diagnostic: mean money-margin delta was `-743.5` because of a few large
negative-margin Tactical Memory episodes that still remained wins. Primary objective
remains W/L; do not optimize this option using money alone.

Binding runtime result:
`docs/strategy/READY_WOOL_ONESHOT_RUNTIME_RESULT_2026-09-18.md`.
Machine-readable:
`data/programme_teacher/2026-09-18/READY_WOOL_RUNTIME_GATE_SUMMARY.json`.

### Current binding gate — reproducible hosted package

O-RW1 is frozen exactly; no quantity/product/step/threshold tuning.

The package builder:
- downloads the exact current V47 output package transiently;
- requires V47 `main.py` SHA
  `f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842`;
- appends only the frozen O-RW1 one-shot wrapper;
- builds a deterministic archive and provenance receipt;
- does not persist upstream source in the repository.

The package parity gate compares the archive **action-for-action and reward-for-reward**
against the reference OneShotReadyWool implementation on fresh seeds.

Active workflow: **`35359994519`**.

A mechanical package PASS makes the artifact technically ready for a hosted-probe
decision. No automatic Kaggle submission is authorized.

No Ryzen action and no manual Kaggle submission are currently required.

The FP001_STATUS/FP001_ROADMAP files are absent on this branch; do not silently create
competing copies or change other branches as part of this solver update.

## Historical record (superseded where inconsistent with the current handoff)

## Objective
Build and submit a competitive Kaggriculture agent based on **Solver + Opponent Model + Value Learning**, optimizing for hosted Kaggle performance and prize probability. The roadmap is frozen unless empirical evidence shows a milestone is infeasible.

## Core operating rule
Hosted Kaggle submissions are part of the experimental loop, not a final ceremony. Intermediate solver versions will be submitted deliberately to measure real hosted transfer while offline training continues.

## Frozen architecture
1. **Exact-engine solver/search**: branch-and-rollout from cloneable intermediate states.
2. **Opponent model**: legal public-state inference, including CR086-derived hidden-stock pressure estimates.
3. **Value/policy learning**: learn `V(s)` and/or `Q(s, macro)` from exact-engine counterfactual outcomes.
4. **Hosted calibration**: Kaggle results decide whether changes transfer; local strength alone never proves hosted strength.

## Milestones to first full trained-solver submission

### PS1 — Executor correctness and economic viability
**Current stage.**

Deliverable: Prize Solver V4 with valid end-to-end play for 720 turns.

Gate:
- no crash or illegal action;
- crops actually appear after PLANT;
- animals bought are deployable rather than trapped in shed;
- positive economy against basic baselines;
- packageable hosted wrapper.

**Hosted sensor S0:** as soon as PS1 passes, build and submit the V4 solver-only package. It is not the final solver; it establishes the first hosted anchor for this architecture.

### PS2 — Exact counterfactual rollout dataset
Use the exact engine to clone states and compare strategic macros from the same branch state.

Staged dataset sizes:
- Pilot: ~2,000 branch states;
- Scale 1: ~10,000 states;
- Scale 2: ~50,000+ states only if the learning curve continues improving.

Each state stores legal runtime features, macro returns, terminal rewards/margins, oracle macro, and heuristic regret.

Gate:
- zero engine/parity failures;
- diverse seeds, phases and opponent families;
- train/validation split by seed/opponent family rather than random row leakage.

**Ryzen 9:** preferred machine for bulk rollout generation once PS1 is frozen. GitHub Actions remains useful for reproducible smoke/gates, not necessarily for the bulk compute.

### PS3 — Value/Policy Model V1
Train a model to estimate `Q(s, macro)` or rank candidate macros from current legal state.

Initial model progression:
- linear/tree baseline;
- compact MLP only if it materially improves held-out ranking/regret;
- no large neural network merely for complexity.

Gate:
- beats `money_diff` and heuristic-plan baselines on held-out states;
- materially lowers mean held-out macro regret;
- inference fast enough for Kaggle runtime.

**Hosted sensor S1:** submit Solver + Value V1, keeping the opponent model disabled so the hosted delta isolates value learning.

### PS4 — Online Solver/Search V1
At runtime, generate admissible strategic macros and use learned value to evaluate/prune them. Exact deep rollouts remain offline training machinery; hosted runtime uses bounded search compatible with competition limits.

Gate:
- deterministic/legal runtime;
- no future/private forbidden information;
- latency and package size within hosted constraints;
- local exact-engine regression suite passes.

**Hosted sensor S2:** submit Search + Value V1.

### PS5 — Opponent Model integration
Feed legal opponent-pressure estimates into state representation/search, including the preserved CR086 latent inventory estimator and public behavioral features.

Gate:
- opponent-conditioned value/search improves held-out regret over PS4;
- ablation proves gain comes from opponent features, not accidental policy drift.

**Hosted sensor S3:** submit full **Solver + Opponent Model + Value Learning** agent.

### PS6 — Hosted-calibrated training loop
Use hosted results from S0/S1/S2/S3 to decide where offline objective diverges from Kaggle reality. Do not replace the architecture; calibrate data mixture, macro set, opponent families and value target.

Loop:
`hosted evidence -> targeted new rollout data -> retrain -> ablation -> new hosted candidate`.

Use the daily submission budget intentionally. Whenever there are mature single-factor candidates, prefer contemporaneous control/treatment submissions instead of leaving the budget unused for days.

## Definition of the first "solver-ready" Kaggle file
A package counts as the first full trained-solver candidate when all are true:
1. strong programmes may serve as proposals/priors; current-state selection must be active;
2. current-state solver/search is active;
3. learned value/policy is active;
4. opponent model is active;
5. legal/parity/runtime gates pass;
6. package is frozen with SHA/provenance;
7. it is actually submitted to Kaggle and receives a hosted submission ID.

This corresponds to **S3**. S0-S2 are deliberate development submissions and should occur before S3.

## Submission ladder
- **S0:** V4 solver-only — first hosted architecture anchor.
- **S1:** V4 + Value V1 — isolate value-learning effect.
- **S2:** Search + Value V1 — isolate online solver/search effect.
- **S3:** Search + Value + Opponent Model — first full trained Prize Solver.
- **S4+**: hosted-calibrated iterations, one major change at a time where possible.

## Stop conditions / anti-infinite-work rules
- No milestone can remain in 'research' indefinitely: it must end in PASS, FAIL/CLOSE, or a hosted submission.
- Do not enlarge datasets if validation learning has saturated.
- Do not add model complexity without held-out improvement.
- Do not postpone a hosted submission merely because a later model may be better.
- Do not redesign the architecture in response to one bad local result or one user comment; change only from reproducible evidence.

## Immediate next action
Finish PS1 V4 smoke + economic trace. If PASS, freeze/package S0 immediately and prepare its Kaggle submission while PS2 rollout generation is being prepared for the Ryzen 9.
