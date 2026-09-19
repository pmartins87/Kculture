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

### Selector Audit V1 — whole-seed PASS; cross-family gate still OPEN

Binding local rerun on 2026-09-19:
`OPTION_VALUE_SELECTOR_AUDIT_PASS_LEARNABLE_SEED_HOLDOUT`.

Whole-seed held-out test:
- 492 rows;
- selector realized delta **+0.1341463**;
- always-fire delta **+0.1138211**;
- row oracle **+0.1382114**;
- **132/136** positive rows captured;
- **0/24** negative rows fired;
- nonzero sign accuracy **0.9625**;
- selected ridge lambda **0.1**, threshold **0.1**.

The state-grouped diagnostic remains strong:
- selector realized delta **+0.1372981**;
- **187/187** positive rows captured;
- **0/17** negative rows fired.

This establishes learnability across fresh whole seeds in the V1 sampled population. It does **not**
yet establish transfer to an unseen opponent family: the original leave-one-opponent-out diagnostic
still failed to recover the V47-mirror gains when that family was fully withheld.

### Ryzen V2 option-value production — COMPLETE / MECHANICS PASS / COVERAGE LIMIT FOUND

Binding user Ryzen run from source commit
`2c402f54462bb31be4f1061c64efe11613b24253`:

- 150/150 fresh seeds;
- 7 opponents;
- both seats;
- O-RW1 + O-TW1;
- 2,100 base matchups;
- **4,200 counterfactual labels**;
- **1,238 unique state hashes**;
- **0 failures**;
- exact engine `1.32.7`.

O-RW1:
- mean score delta **+0.0352381**;
- 208 positive / 60 negative / 1,832 neutral;
- mean margin delta **-88.5776**.

O-TW1:
- mean score delta **+0.0571429**;
- 253 positive / 16 negative / 1,831 neutral;
- mean margin delta **+85.7710**.

Critical population result:
- V47 mirror: **458 positive / 76 negative**, mean score delta **+0.3183333**;
- Ready Stock: 2 positive / 0 negative;
- `2715.6`: 1 positive / 0 negative;
- V48, Conditional Memory, Tactical Memory, Best Market: W/L-neutral.

Thus **458/461 positive labels (99.35%) are V47-mirror labels**.
Outside V47 there are only **3 positives in 3,600 rows** and no negative W/L labels.

Binding interpretation:
- V1 seed-holdout learnability was real;
- more seeds on the same two-option library are **not** the current bottleneck;
- a production multi-family selector is blocked by **option coverage**, not raw model capacity;
- do not scale this exact dataset merely by brute force.

Result:
`docs/strategy/OPTION_VALUE_RYZEN_V2_RESULT_2026-09-19.md`.

### Current parallel gates

#### G1 — option-library composition

Question: do frozen O-RW1 and O-TW1 stack safely on one V47 organism?

Original serial workflow **`35424958961`** remains in progress:
`option-library-combo-runtime-v0`.

Because the serial official-engine run is long, an **exactly equivalent execution-only
parallelization** was launched, without changing seeds, variants, opponents or thresholds:

- parallel workflow **`35426256016`**;
- 7 shards, one per opponent;
- each shard uses the same fresh seeds `71001..71004`, both seats, and variants
  BASE / O-RW1 / O-TW1 / BOTH;
- aggregator applies the same frozen decision rule.

The first mechanically valid completed execution is binding; if both complete validly,
their summaries must agree.

#### G2 — diverse wrapper proposal oracle V3

Question: can real market proposals from a larger strong-agent panel expose one-turn
counterfactual W/L headroom **outside the modern V47 family**?

Two earlier attempts are **mechanically invalid / non-binding**:
- `35425004728`: import bootstrap failure before hypothesis execution;
- `35426094440`: package acquisition stopped on inaccessible Shop-Aware (403) before
  any branch state was evaluated.

No strategic conclusion may be drawn from those runs.

Current binding attempt:
- workflow **`35426189093`**;
- identical seeds/opponents/thresholds;
- inaccessible Shop-Aware removed only as an unavailable proposal source;
- remaining proposer panel: Ready Stock, Market Smart, V46 Microstructure, V48 Queue,
  `2715.6`, Conditional Memory, Tactical Memory and Best Market;
- state: in progress at this handoff.

#### Conditional fallback — V4 multi-turn transaction search

Protocol frozen at:
`docs/strategy/ADAPTIVE_TRANSACTION_SEARCH_V4_PROTOCOL_2026-09-19.md`.

It is **dormant**. Activate only after V3 is mechanically valid and fails to show
meaningful W/L headroom outside modern V47-family opponents.

V4 permits bounded market-only transaction sequences of up to 3 turns, with exact V47
farmer/hands preservation and mandatory exact-engine counterfactual evaluation.
Promotion requires gains in at least two unrelated non-V47 opponent families.

### Binding next steps

1. Obtain a mechanically valid G1 result; prefer the parallel equivalent if it finishes first.
2. Obtain the mechanically valid V3 result from `35426189093`.
3. If G1 shows safe incremental composition, retain BOTH as the current option-library host.
4. If V3 shows non-modern41 W/L headroom, causalize the recurring winning transformation(s)
   as first-party options on fresh seeds before any model training.
5. If valid V3 is mirror-only/no-headroom, activate the already-frozen V4 protocol.
6. Resume whole-seed + leave-family-out selector training only after the option library has
   meaningful W/L support across multiple unrelated opponent families.
7. No new Kaggle submission; preserve both currently active hosted slots.

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
