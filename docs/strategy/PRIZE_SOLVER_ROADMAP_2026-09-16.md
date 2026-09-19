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

### G1 — option-library composition: BINDING RESULT

Binding evidence comes from the seven successful shards of workflow **`35426256016`**.
The aggregate job failed only because the lightweight aggregate environment omitted
`kaggle-environments`; the seven strategy shards themselves were all mechanically clean.

56 matched contexts total:
- BASE score rate: **0.7857143**;
- O-RW1: **0.8392857**;
- O-TW1: **0.8392857**;
- BOTH: **0.8392857**;
- BOTH vs BASE: **+0.0535714**;
- score-regressing opponent blocks: **0/7**.

Mirror block:
- BASE **0.500**;
- RW1/TW1/BOTH **0.875**.

Binding decision: **`OPTION_LIBRARY_COMBO_ADVANCE`**.

Interpretation:
- retain O-RW1 + O-TW1 together as the current **offline option-library host**;
- composition is W/L-safe on this gate;
- BOTH adds no W/L over the best single option in this sample;
- no hosted Kaggle submission follows from this alone.

Result doc:
`docs/strategy/OPTION_LIBRARY_COMBO_RUNTIME_V0_RESULT_2026-09-19.md`.

### G2 — adaptive wrapper proposal oracle V3: BINDING RESULT

Valid workflow **`35426189093`**:
- 56 branch states;
- 84 exact candidate rollouts;
- zero failures;
- exact engine `1.32.7`;
- mechanical PASS.

Decision: **`WRAPPER_PROPOSAL_OUTSIDE_MARGIN_ONLY`**.

Overall:
- score delta **0.0**;
- nonwin→win flips **0**;
- 8 positive-margin states;
- mean oracle margin delta **+393.39**.

Outside modern41:
- BASE and oracle score rate both **1.0**;
- score delta **0.0**;
- 8/32 positive-margin states;
- mean oracle margin delta **+688.44**.

All promoted proposals came from `router_2715`, at step 0:
- V47: `BUY_PRODUCT WHEAT 7; SELL WHEAT 2`;
- router proposal: `BUY_PRODUCT WHEAT 13; SELL WHEAT 13; BUY_PRODUCT WHEAT 13`.

That proposal improved margin against weaker outside blocks but was harmful against the
hard strata V47 mirror, Ready Stock and V48. It is **not** a promotable generic option.

Result doc:
`docs/strategy/ADAPTIVE_WRAPPER_PROPOSAL_V3_RESULT_2026-09-19.md`.

### V4 activation — hard-stratum discovery

The conditional V4 protocol is now **activated in staged form** because valid V3 produced
no W/L headroom.

Evidence-driven amendment made before V4 execution:
- discovery now targets hard BASE non-win strata rather than arbitrary family diversity;
- highest priority is **V48**, where valid V3 lost by small margins and one-turn proposals
  did not flip the result;
- broad family testing moves to the regression/generalization stage after a causal option
  is discovered.

Protocol:
`docs/strategy/ADAPTIVE_TRANSACTION_SEARCH_V4_PROTOCOL_2026-09-19.md`.

### V47×V48 divergence census: BINDING RESULT

Workflow **`35439729714`** completed SUCCESS on fresh seeds `73001..73004`, both seats.

Decision: **`V48_CENSUS_MARKET_SEARCHABLE`**.

Hard-block result:
- V47 score rate vs V48: **0.0**;
- **0W / 0T / 8L**;
- mean margin **-454.0**;
- **458** same-farmer/hands market divergences;
- **0** farmer/hands divergences;
- zero failures.

The first market divergence appears around step 253/323, with many recurrent later
divergences. The observed V48 pattern repeatedly clears impossible/stale SELL slots or caps
huge V47 quantities (for example `SELL WHEAT 1000`) to feasible current inventory.

Result doc:
`docs/strategy/V47_V48_DIVERGENCE_CENSUS_V1_RESULT_2026-09-19.md`.

### O-CQ1 Queue Clamp/Clear — CLOSED AT PARITY

Workflow **`35439945148`** completed mechanically clean.

Binding decision: **`CQ1_PARITY_FAIL`**.

Against exact V48 action output on fresh audit seeds:
- V48 market-divergence rows: **456**;
- CQ1 changed rows: **1,356**;
- exact V48 matches: **288**;
- false-positive changes: **900**;
- changed-but-not-exact: **168**;
- missed V48 changes: **0**;
- precision: **0.21239**;
- recall: **0.63158**;
- failures: **0**.

The prepared O-CQ1 causal workflow is **NOT RUN** and remains dormant/non-binding.

Mechanistic diagnosis:
- current pre-action shed alone is the wrong availability state;
- Kaggriculture resolves farmer/hand actions before market;
- `DROP`, shed-adjacent `PLACE`, and `PICKUP` can alter shed before SELL;
- market slots execute in order, so an earlier `BUY_PRODUCT` can feed a later SELL;
- V48 also selectively clears/compacts the queue rather than applying a universal clamp.

### O-CQ2 — projected queue sanitation

New development hypothesis:
1. project own shed through the exact current V47 farmer/hands actions using only legal own state;
2. project earlier market inventory-changing slots before later SELLs;
3. test alternative SELL sanitation forms:
   - slotwise clamp;
   - clamp + compaction;
   - same-product shortage merge + compaction;
4. evaluate a small pre-frozen activation-threshold grid;
5. choose one configuration only on development seeds;
6. freeze it and validate on separate untouched seeds before any causal W/L gate.

This is still a **parity/mechanism** stage, not a performance-training stage.

The generic V4A multi-turn market oracle remains prepared but **dormant pending CQ2**.
It should run only if a compact first-party sanitation mechanism cannot explain enough of V48.

### Binding next steps

1. Run O-CQ2 development parity matrix.
2. Freeze exactly one sanitation rule + activation condition from that development result.
3. Validate the frozen rule on separate fresh seeds.
4. If validation parity is strong, open fresh causal V48 W/L gate.
5. If validation parity is weak, activate the already-prepared V4A bounded multi-turn oracle.
6. Keep O-RW1 + O-TW1 as current offline host.
7. No new Kaggle submission; preserve active hosted slots.

### ALL3 — CURRENT HOSTED STATE / FIRST INFORMATIVE CHECKPOINT

Current intended active pair:
1. O-RW1 `56336027`;
2. ALL3 `56367770`.

ALL3 package:
- exact hosted-faithful V47 + O-RW1 + O-TW1 + O-LQ2;
- package SHA-256 `204a9ed49579b8255343d6014e815d2512d2f37edea142eba082203e101ff7f8`;
- hosted entrypoint `_kc_all3_entrypoint`;
- package parity **12/12 exact actions + 12/12 exact rewards**.

Current hosted snapshot around 19:47 UTC:
- ALL3: **2395.4**;
- retained O-RW1: **2364.1**.

Do not compare these ratings causally; the live populations/histories differ.

Exposure:
- 35 listed ALL3 public episodes;
- **34 resolved external games**;
- **28W / 6L / 0T**;
- raw score rate **0.8235294**;
- 33 unique opponents;
- mean margin **+13,626.97**;
- median margin **+1,676.5**.

This clears the project's first-informative threshold (~32 resolved external games).

ALL3 observed losses:
- qinsuikang: -11,923;
- Timothy Adeyemi: -8,554;
- cooked: -1,863;
- Vishal Kishore: -1,499 and -288;
- Nat Bel ML Fun: -83.

Result:
`docs/strategy/ALL3_HOSTED_FIRST_INFORMATIVE_RESULT_2026-09-19.md`.

### Mature O-RW1 loss coverage — SECONDARY FORENSIC EVIDENCE

Workflow **`35465395838`** reconstructed ALL3 changes over 128 mature O-RW1 replays.

This is coverage-only, not a counterfactual outcome simulation.

Among 82 O-RW1 losses:
- mean reconstructed ALL3 changed turns: 152.02;
- zero losses with no ALL3 changes: 0;
- only **9/82** satisfy the conservative early residual-hard definition
  (already behind around step 336 with first ALL3 change at/after 336).

Therefore old O-RW1 losses are no longer the preferred ALL3 failure set.
The six actual ALL3 hosted losses are now primary.

Result:
`docs/strategy/ALL3_HOSTED_LOSS_COVERAGE_RESULT_2026-09-19.md`.

### O-HV1 High-Value Stock Flush — ACTIVE DEVELOPMENT

Hosted replay discovery identified repeated local missed-sale mechanics:

- Vishal Kishore step 348: own WOOL 11, public price 239, ALL3 no SELL;
- Vishal Kishore step 299: own MILK 6, public price 177, ALL3 no SELL;
- qinsuikang step 553: own MILK 15, public price 254, ALL3 does not sell MILK.

O-HV1 is a legal-state market-only proposal:
- preserve ALL3 farmer/hands;
- consider finished goods only:
  MILK, WOOL, EGG, CARROT, STRAWBERRY, MELON, TOMATO;
- reserve inventory already queued for ALL3 SELLs;
- select at most one remaining product by max `price * remaining_qty`;
- add one SELL only when the public unit price clears the frozen threshold;
- no opponent identity/rating/EpisodeId/hidden seed/future/private-opponent input.

Frozen development matrix:
- D1: step>=240, price>=175;
- D2: step>=240, price>=200;
- D3: step>=336, price>=175;
- D4: step>=336, price>=200.

Development opponents:
V47 mirror, V48, Ready Stock.

Seeds:
`74801..74804`, both seats.

Active workflow:
**`35465868923`**.

Protocol:
`docs/strategy/O_HV1_HIGH_VALUE_STOCK_FLUSH_PROTOCOL_2026-09-19.md`.

### Binding next steps

1. Resolve O-HV1 workflow `35465868923`.
2. If no frozen config satisfies the predeclared safety rule: close O-HV1 without threshold rescue.
3. If one config is selected: freeze exactly that config.
4. Run untouched seven-family fresh validation before option-library admission.
5. Do not submit O-HV1 or any ALL3 variant to Kaggle from development evidence.
6. Preserve O-RW1 + ALL3 while ALL3 hosted exposure continues.

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
