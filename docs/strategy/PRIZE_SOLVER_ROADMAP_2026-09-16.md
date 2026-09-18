# Prize Solver Roadmap — 2026-09-16

## Current solver handoff — 2026-09-18

Active branch: `research/prize-solver-v0`.

### Hosted-entrypoint correction remains binding

Public agents must be loaded with:
`kaggle_environments.agent.get_last_callable`.

Exact public V47 hosted entrypoint:
`_y_agent_shopherd`.

Hosted treatment submission `56333579` from the first A/B is mechanically invalid and
must never be interpreted as O-RW1 competitive evidence.

### O-RW1 hosted-faithful causal gate — PASS

Workflow `35363453097`, artifact `10555907821`:
- 48 valid branch states;
- mean score delta **+0.0833333**;
- 8 non-win -> win flips;
- 0 win -> non-win regressions;
- 0 negative-W/L states;
- mean margin delta +14.9583.

### O-RW1 hosted-faithful autonomous runtime — PASS

Workflow `35367785929`, artifact `10558221804`, exact engine `1.32.7`.

BASE is exact public V47 resolved through the official hosted loader to
`_y_agent_shopherd`.

Results:
- 64 paired matchups / 128 complete episodes;
- zero failures;
- BASE score rate **0.6250**;
- V47 + O-RW1 score rate **0.71875**;
- W/L delta **+0.09375**;
- **14 non-win -> win flips**;
- **0 win -> non-win regressions**;
- 14 positive-score pairs;
- 2 negative-score pairs;
- 48 neutral pairs;
- all 4 opponent blocks had nonnegative mean score delta;
- worst block mean score delta 0.0.

Per opponent:
- V47 mirror: `0.500 -> 0.875`, delta **+0.375**;
- V48: `0.000 -> 0.000`;
- Tactical Memory: `1.000 -> 1.000`;
- Ready Stock: `1.000 -> 1.000`.

Important: O-RW1 is **not universally safe**. Seed 65008 versus V47 mirror produced two
tie->loss regressions. It is nevertheless positive on the frozen aggregate gate and had
no win->non-win regressions.

Money margin is diagnostic only:
- mean margin delta -805.78125;
- median +10;
- Tactical Memory generated large negative money deltas without changing W/L wins.

Binding verdict:
`READY_WOOL_RUNTIME_PASS`.

Result:
`docs/strategy/READY_WOOL_RUNTIME_HOSTED_FAITHFUL_RESULT_2026-09-18.md`.
Machine-readable:
`data/programme_teacher/2026-09-18/READY_WOOL_RUNTIME_HOSTED_FAITHFUL_SUMMARY.json`.

Frozen O-RW1 remains unchanged:
```
if not used
and hosted-faithful V47 market == []
and own private shed.WOOL >= 2
and step <= 671:
    execute SELL WOOL 2
    used = True
```

### Current binding gate — corrected hosted package parity

Active workflow:
**`35372564746`**, head
`a8830bef5b930f5178c836e9f9c8dbedbc4e5245`.

The package gate now requires:
- exact base hosted entrypoint `_y_agent_shopherd`;
- exact candidate hosted entrypoint `_kc_orw1_entrypoint`;
- exact action parity vs the hosted-faithful reference implementation;
- exact reward parity;
- deterministic archive/SHA manifest.

No new Kaggle submission is authorized until this package gate passes.

No O-RW1 retuning is authorized.
No Ryzen action is required.

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
