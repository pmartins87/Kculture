# Prize Solver Roadmap — 2026-09-16

## Current solver handoff — 2026-09-18

Active branch: `research/prize-solver-v0`.

The active Prize-Solver line is frozen first-party option **O-RW1** on exact public V47.

### Offline / exact-engine evidence

1. Wrapper-proposal oracle V2b — PASS:
   - BASE `0.500` -> oracle `0.625`;
   - W/L delta **+0.125**;
   - useful proposal was V47 market empty -> `SELL WOOL 2`.

2. First-party causal O-RW1 — PASS SAFE OPTION:
   - 48 branch states;
   - mean score delta **+0.1666667**;
   - 16 non-win -> win flips;
   - 0 negative-W/L states.

3. Autonomous one-shot runtime transfer — PASS:
   - 64 paired matchups / 128 episodes;
   - BASE `0.5000`;
   - V47 + O-RW1 `0.6875`;
   - W/L delta **+0.1875**;
   - 28 non-win -> win flips;
   - 0 win -> non-win regressions;
   - all 4 opponent blocks nonnegative in W/L.

Frozen O-RW1:
```
if not used
and V47 current market == []
and own private shed.WOOL >= 2
and step <= 671:
    execute SELL WOOL 2
    used = True
```

### Hosted package — PASS

Workflow `35360173417`, artifact `10554278438`.

Candidate:
`KCULTURE_V47_ORW1_ONESHOT_V1.tar.gz`

Archive SHA-256:
`b994e00d7adba05827eb8839b806211c2c8199dd0ad09a28b63815b58479c80f`

Candidate `main.py` SHA:
`f65be27b47839eb0cb6b44b217fc1edb33f63796bf5bc0bdd4f0bd311d3c2ff4`

Exact V47 base main SHA:
`f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842`

Fresh package smoke:
- 8 package/reference pairs;
- 16 complete episodes;
- exact action parity 8/8;
- exact reward parity 8/8;
- 0 failures.

The packaged source retains the upstream Apache-2.0 license text, SPDX notice and V47
attribution/modification notice.

Binding package result:
`docs/strategy/ORW1_HOSTED_PACKAGE_RESULT_2026-09-18.md`.
Machine-readable:
`data/programme_teacher/2026-09-18/ORW1_HOSTED_PACKAGE_SUMMARY.json`.

### Current next step — explicit authorization required

Frozen hosted sensor:
`docs/strategy/ORW1_HOSTED_AB_PROBE_PROTOCOL_2026-09-18.md`.

Submit in the same operational window:
- CONTROL: exact public V47 output archive, SHA
  `08e56c43ecf28253605b61066dd769334d96262056b8cd337489f1f4f909ad01`;
- TREATMENT: exact frozen O-RW1 archive, SHA
  `b994e00d7adba05827eb8839b806211c2c8199dd0ad09a28b63815b58479c80f`.

No other variant between the pair. Hosted result is a population sensor; do not retune
O-RW1 from one noisy rating.

**No Kaggle submission has been sent. Await explicit user authorization for the A/B
hosted probe.**

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
