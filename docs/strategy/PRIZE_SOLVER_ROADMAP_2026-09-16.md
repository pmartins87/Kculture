# Prize Solver Roadmap — 2026-09-16

## Current solver handoff — 2026-09-18

Active branch: `research/prize-solver-v0`.

### Hosted-entrypoint correction is binding

All public-agent promotion work must use
`kaggle_environments.agent.get_last_callable`.

Exact public V47 hosted entrypoint:
`_y_agent_shopherd`.

The original treatment submission `56333579` is mechanically invalid and must never be
interpreted as O-RW1 competitive evidence.

### O-RW1 hosted-faithful evidence

Causal gate `35363453097`:
- score delta **+0.0833333**;
- 8 non-win -> win flips;
- 0 negative-W/L states.

Autonomous runtime gate `35367785929`:
- 64 pairs / 128 episodes;
- BASE `0.6250`;
- O-RW1 `0.71875`;
- score delta **+0.09375**;
- 14 non-win -> win flips;
- 0 win -> non-win regressions;
- 2 tie->loss pair regressions;
- all 4 opponent blocks nonnegative in mean W/L.

### Corrected hosted package — PASS

Workflow `35372969031`, artifact `10559606269`.

Candidate archive:
`KCULTURE_V47_ORW1_ONESHOT_V1.tar.gz`

SHA:
`997aa273cb64c6acf933f8d719bd358c47d07871f6e42ac056003155499c68c9`

Hosted entrypoint:
`_kc_orw1_entrypoint`.

Package parity:
- 8/8 exact action parity;
- 8/8 exact reward parity;
- 719 action calls per episode;
- 0 failures.

### Corrected hosted A/B R2 — VALID BUT IMMATURE

Submission workflow:
`35373555439`.

CONTROL:
- submission **56336025**;
- exact V47 archive;
- entrypoint `_y_agent_shopherd`;
- registered `2026-09-18 17:19:39.130000 UTC`.

TREATMENT:
- submission **56336027**;
- corrected O-RW1 archive SHA
  `997aa273cb64c6acf933f8d719bd358c47d07871f6e42ac056003155499c68c9`;
- entrypoint `_kc_orw1_entrypoint`;
- registered `2026-09-18 17:19:40.807000 UTC`.

Registration separation: **1.677 seconds**.

Both passed hashes and official-loader checks immediately before submit.
Daily usage after pair: **4/5**.

First joint COMPLETE checkpoint (`2026-09-18 17:24:36 UTC`):
- CONTROL: `COMPLETE`, rating field `600.0`;
- TREATMENT: `COMPLETE`, rating field `600.0`.

Replay forensics workflow `35374217511`, artifact `10559931321`:
- CONTROL listed episodes: **1**;
- TREATMENT listed episodes: **1**;
- externally attributable resolved games: **0 / 0**.

Therefore `600.0 vs 600.0` is **not evidence of neutrality or promotion**.

Binding state:
`ORW1_HOSTED_AB_R2_COMPLETE_BUT_UNMATURE_NO_EXTERNAL_EVIDENCE`.

### Frozen hosted maturity rule for R2

To prevent score-watching, freeze this before external outcomes accumulate:

1. First **informative** R2 hosted checkpoint requires at least **32 externally attributable
   completed public games per arm**. At that checkpoint compare rating, W/L/T, seat split,
   opponent-strength distribution and matched/current population context.
2. Final **promotion/regression** verdict must not be made before **100 completed public
   episodes per arm**, consistent with the project's earlier hosted maturity discipline.
3. A rating field without supporting episode maturity is diagnostic only.
4. Do not tune O-RW1 from intermediate hosted outcomes.
5. Preserve the fifth daily submission slot; no nearby O-RW1 variant is authorized.

Submission receipt:
`docs/strategy/ORW1_HOSTED_AB_R2_SUBMISSION_2026-09-18.md`.
Machine-readable:
`data/programme_teacher/2026-09-18/ORW1_HOSTED_AB_R2_SUBMISSION.json`.

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
