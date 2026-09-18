# Prize Solver Roadmap — 2026-09-16

## Current solver handoff — 2026-09-18

Active branch: `research/prize-solver-v0`.

### Hosted slot preservation remains binding

Kaggriculture keeps only the two newest submissions active. Do not submit a third agent
while the current pair is still maturing.

Current active pair:

CONTROL:
- submission `56336025`;
- exact public V47;
- latest authenticated rating snapshot: **2399.6**;
- current listed episodes at `2026-09-18 22:16:32 UTC`: **80**.

TREATMENT:
- submission `56336027`;
- hosted-faithful V47 + O-RW1;
- latest authenticated rating snapshot: **2536.2**;
- current listed episodes at `2026-09-18 22:16:32 UTC`: **83**.

The pair has already crossed the first informative 32/32 external-game threshold.
The normal maturity target remains **>=100 public episodes per arm plus a materially
calmer rating trajectory** before any voluntary replacement.

Historical exact V47 submission `56333577` froze at **2387.9** after 36 listed /
35 external games (29-5-1). It was retired too early; current policy prevents repeating
that mistake.

### O-RW1 hosted-faithful evidence

Causal gate `35363453097`:
- score delta +0.0833333;
- 8 positive flips;
- 0 win->nonwin regressions.

Autonomous runtime gate `35367785929`:
- 64 pairs / 128 episodes;
- `0.6250 -> 0.71875`;
- score delta **+0.09375**;
- 14 non-win -> win flips;
- 0 win -> nonwin regressions.

Corrected package parity `35372969031`:
- hosted entrypoint `_kc_orw1_entrypoint`;
- 8/8 exact action parity;
- 8/8 exact reward parity.

### O-TW1 — SECOND INDEPENDENT OPTION / RUNTIME PASS

Causal gate `35378191104`:
- 48 branch states;
- mean score delta **+0.125**;
- 14 non-win -> win flips;
- 0 win -> nonwin regressions.

Autonomous runtime gate:
**`35395548699`**, artifact `10569241095`.

Fresh panel:
- seeds `68001..68008`;
- both seats;
- V47 mirror, V48, Tactical Memory, Ready Stock;
- 64 paired matchups / 128 episodes.

Results:
- BASE score rate **0.6250**;
- O-TW1 score rate **0.71875**;
- score delta **+0.09375**;
- 14 non-win -> win flips;
- 0 win -> nonwin regressions;
- 14 positive-score pairs;
- 2 negative-score pairs;
- 48 neutral pairs;
- all 4 opponent blocks nonnegative mean W/L;
- worst block delta 0.0;
- mean margin delta +9.28125;
- median margin delta +18.

Binding verdict:
`TOWN_WHEAT_RUNTIME_PASS`.

O-TW1 is promoted into the **offline option library**, not to Kaggle.

Result:
`docs/strategy/TOWN_WHEAT_ONESHOT_RUNTIME_RESULT_2026-09-18.md`.

### Current development gate — unified option-value dataset V0

The project now has two independently proven first-party options on hosted-faithful V47:
- O-RW1: ready-WOOL sale;
- O-TW1: town-WHEAT pulse hold.

Next architecture:
```
legal current state + eligible option
        -> counterfactual ΔW/L label
        -> value dataset
        -> state-conditioned selector/value model
        -> later bounded search
```

Frozen pilot:
`docs/strategy/OPTION_VALUE_DATASET_V0_PILOT_2026-09-18.md`.

Implementation:
`tools/option_value_dataset_v0_pilot.py`.

Active workflow:
**`35401011776`**, head
`3e60477caa17d42675529a8e04be5bd91ac91165`.

Pilot uses fresh seeds `69001,69002`, both seats, V47/V48/Tactical Memory, and requires:
- exact hosted V47 entrypoint;
- discovery/base reward parity;
- legal feature contract only;
- no seed/opponent/rating/hidden/future metadata inside model features;
- at least 8 labeled rows and >=2 rows/option.

A PASS validates the data pipeline only. Only after PASS should a resumable Ryzen-scale
multiprocessing label generator be built and run.

No Kaggle submission is authorized.
No Ryzen action is required yet.

The FP001_STATUS/FP001_ROADMAP files are absent on this branch; do not create competing
copies.

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
