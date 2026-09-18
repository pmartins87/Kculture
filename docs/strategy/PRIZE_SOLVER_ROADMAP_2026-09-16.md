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

### O-RW1 hosted-faithful offline evidence

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

Corrected package `35372969031`:
- candidate archive SHA
  `997aa273cb64c6acf933f8d719bd358c47d07871f6e42ac056003155499c68c9`;
- hosted entrypoint `_kc_orw1_entrypoint`;
- 8/8 exact action parity;
- 8/8 exact reward parity;
- 0 failures.

### Corrected O-RW1 hosted A/B R2 — balanced early exposure, still immature

CONTROL:
- submission **56336025**;
- exact V47;
- entrypoint `_y_agent_shopherd`.

TREATMENT:
- submission **56336027**;
- corrected V47 + O-RW1;
- entrypoint `_kc_orw1_entrypoint`.

Registered only **1.677 seconds** apart and SHA/loader checked immediately before submit.

Latest replay/status checkpoint around `2026-09-18 18:01 UTC`:

CONTROL:
- rating **1457.7**;
- listed episodes **9**;
- externally resolved games **8**;
- W-L-T **8-0-0**;
- mean margin **+36,006.875**;
- median margin **+32,461.5**;
- unique external opponents **8**.

TREATMENT:
- rating **1458.2**;
- listed episodes **10**;
- externally resolved games **9**;
- W-L-T **9-0-0**;
- mean margin **+47,125.222**;
- median margin **+40,053**;
- unique external opponents **9**.

The earlier exposure asymmetry has largely disappeared. Both arms are undefeated and
nearly equal in rating, so there is no early catastrophic hosted signal against O-RW1.
However, the frozen informative threshold has **not** been reached.

Binding hosted state:
`ORW1_HOSTED_AB_R2_BALANCED_EARLY_EXPOSURE_AWAIT_32_PER_ARM`.

Frozen maturity rule:
- first informative hosted comparison only after **>=32 externally resolved games per arm**;
- promotion/regression verdict only after **>=100 public episodes per arm**;
- no O-RW1 tuning from intermediate hosted results;
- preserve the fifth daily submission slot.

### New orthogonal option — O-TW1 town-WHEAT pulse hold

To avoid idling while R2 matures, the solver opened the next separable timing family
already frozen by CR092/H1/H1B. This is **not** an O-RW1 variant.

Historical priors:
- H1 runtime causal proof commit
  `ab951727a195dce2992a07bf3e8b08992187fdf6`;
- H1B exact-engine proof commit
  `a00d2ffce9656b83df263f407ed9b92a718502db`.

Frozen O-TW1 operator:
- host exact hosted-faithful V47;
- if the current public town state implies WHEAT consumption this turn and exact V47
  intends to `SELL WHEAT` already owned in the current shed;
- suppress only those current-turn `SELL WHEAT` orders;
- preserve exact V47 farmer, hands and every other market order;
- exact V47 resumes next turn with no forced follow-up sale.

Fresh causal panel:
- seeds `67001..67004`;
- both seats;
- V47 mirror, V48 and Tactical Memory;
- max 2 selected events/matchup, separated by >=72 turns;
- minimum 12 valid branch states;
- no automatic hosted submission.

Protocol:
`docs/strategy/FIRST_PARTY_TOWN_WHEAT_DEFERRAL_CAUSAL_GATE_2026-09-18.md`.

Implementation:
`tools/first_party_town_wheat_deferral_causal_gate.py`.

Active binding workflow:
**`35378191104`**, head
`c06114f4c519a64e752989a2b58f880e9e5ecb1a`.

Current run state:
- install PASS;
- syntax PASS;
- causal gate **in progress**.

No 5th Kaggle slot is authorized by O-TW1.
No Ryzen action is required.

The FP001_STATUS/FP001_ROADMAP files are absent on this branch; do not silently create
competing copies or change other branches as part of this solver update.


### HOSTED SLOT PRESERVATION — BINDING

Kaggriculture keeps only the two most recent submissions active. A third submission retires the oldest active bot, and retired bots do not remain in the final active pair. Therefore hosted submissions are scarce state, not cheap experiments.

Historical lesson: exact V47 submission `56333577` retired at **2387.9** after only **35 external games** (29-5-1). It had passed the 32-game informative threshold but had not reached the 100-episode maturity standard. Retiring it was strategically premature; its later trajectory is unknowable.

Current policy:
- do not use hosted for exploratory variants;
- do all causal/runtime/package screening offline;
- do not voluntarily replace a strong or record-setting active bot before >=100 public episodes and a materially calmer rating trajectory, unless deadline/critical-bug pressure requires it;
- 32 games is informative only, not a replacement trigger;
- current active pair `56336025` + `56336027` is protected while maturing;
- O-TW1 remains offline even after causal PASS until it earns the right to displace an active slot.

Policy: `docs/strategy/HOSTED_SLOT_PRESERVATION_POLICY_2026-09-18.md`.

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
