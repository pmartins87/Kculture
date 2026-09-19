# Prize Solver Roadmap — 2026-09-16

## Current solver handoff — 2026-09-19

Active branch: `research/prize-solver-v0`.

### Hosted pair — preserve both slots

Maturity snapshot around 100 episodes:
- CONTROL `56336025`: rating **2429.1**, 103 listed / 102 resolved external, 76-24-2;
- O-RW1 `56336027`: rating **2506.7**, 106 listed / 105 resolved external, 60-44-1.

These are not matched opponent populations. Raw W/L is not a causal A/B comparison.
The hosted treatment remains higher-rated; do not replace either slot while offline
selector/value work proceeds.

### Option-value Ryzen V1 — production PASS

User Ryzen run completed:
- 250/250 fresh seeds;
- 1,500 BASE matchups;
- **3,000 counterfactual option labels**;
- **584 unique state hashes**;
- **0 failures**.

O-RW1:
- mean score delta **+0.096**;
- 370 positive / 82 negative / 1,048 neutral;
- mean margin delta **-161.6493**.

O-TW1:
- mean score delta **+0.14**;
- 436 positive / 16 negative / 1,048 neutral;
- mean margin delta **+35.7173**.

Population decomposition:
- V47 mirror: mean score delta **+0.354**;
- V48: W/L delta 0;
- Tactical Memory: W/L delta 0.

### Selector Audit V1 — within-population learnability PASS, production gate still OPEN

Original grouped-state audit:
`OPTION_VALUE_SELECTOR_AUDIT_PASS_LEARNABLE`.

Held-out state-group test:
- 681 rows;
- selector realized delta **+0.1372981**;
- always-fire **+0.1248164**;
- row oracle **+0.1372981**;
- captured **187/187** positive rows;
- fired **0/17** negative rows;
- nonzero sign accuracy **0.9607843**.

Conflict diagnostics:
- exact state+option: 230/584 groups have some label disagreement, but only 2 have both positive and negative labels;
- feature aliases: 107/283 groups have some label disagreement, but only 1 has both positive and negative labels.

However leave-one-opponent-out shows **no demonstrated cross-family transfer**:
- V47 mirror held out: 0% fire, 0/806 positive captures;
- V48 held out: high fire rate but held-out W/L labels all neutral;
- Tactical Memory held out: high fire rate but held-out W/L labels all neutral.

Therefore the state-group PASS proves legal-feature learnability **inside the sampled mixed
population**, not deployable opponent-family generalization.

Result:
`docs/strategy/OPTION_VALUE_SELECTOR_AUDIT_V1_RESULT_2026-09-19.md`.

### Stricter selector gate — whole-seed holdout

`tools/option_value_selector_audit_v1.py` has been hardened:
- every seed belongs wholly to train, dev or test;
- no seed can appear across partitions;
- the binding decision now requires positive held-out value under the whole-seed split;
- the state-hash split remains diagnostic only.

The local audit must be rerun before any model is frozen.

### V2 opponent league

Six diverse public agents have already passed hosted-faithful package/entrypoint preflight:
- V47 mirror;
- Ready Stock;
- V48;
- Conditional Memory;
- Tactical Memory;
- Best Market Agent.

Old V39 and V38 legacy notebooks are no longer retrievable through the current Kaggle CLI path.
A seventh candidate, the rank-25 `2715.6` multi-program router, is currently being tested
as the diversity replacement.

### Binding next steps

1. Rerun the lightweight selector audit with whole-seed holdout.
2. Complete the V2 diverse-league preflight.
3. If seed-holdout remains positive, expand labels with the V2 league before fitting the
   production selector.
4. Only after V2 train/dev/test + leave-family-out PASS should a candidate selector enter
   autonomous runtime gates.
5. No new Kaggle submission.
6. Preserve both active hosted slots.

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
