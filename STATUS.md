# STATUS — Kculture live source of truth

## Binding update — 2026-09-20 — V8C PASS-NARROW / V8D ACTIVE

**This block supersedes lower stale current-action sections.**

### V8C — COMPLETE

Binding workflow: **`35516167350`**  
Head: `b528ac9dafedefd17b65dfa7407b1b793adb6046`

Decision: **`V8C_CONDITIONAL_ORDER_HEADROOM_NARROW`**.

Mechanical:
- PASS;
- 46 exact baseline-discovered one-shot branches;
- expected branches 46;
- failures 0.

Strategic:
- 1 loss->win flip;
- 6 positive-margin states across all 4 hard contexts;
- 37 negative-margin states;
- mean margin delta -113.1522.

Repeated strongest structural state:
- exact post-LQ2 nonempty market shape = **4 SELL + 6 HIRE**;
- no BUY / no other nonempty operation;
- MILK, WOOL and FERTILIZER all present;
- unchanged O-LQ3 would alter their relative order.

The only two V8C states with this exact shape were both positive:
- V48 75103/seat1: -86 -> +10 (**LOSS -> WIN**, +96);
- V48 75110/seat0: -484 -> -220 (+264).

### O-LQ3C — FROZEN

Candidate eligibility is the structural 4-SELL + 6-HIRE signature above. No seed, opponent identity, turn number, price threshold, rating, EpisodeId, future state or opponent-private state is used.

Treatment:
apply the unchanged O-LQ3 stable priority `MILK -> WOOL -> FERTILIZER` for eligible turns only.

Module:
`tools/first_party_lq3c_conditional_sell_order.py`.

### V8D — ACTIVE

Workflow: **`35516560425`**  
Launch commit: `6afd5dd1a4ab4776437c49aae9807e948d032d8f`.

Fresh frozen validation:
- seeds `76001..76012`;
- both seats;
- V48 primary;
- V47 mirror control;
- Ready Stock control;
- 72 paired contexts total.

Frozen PASS requires:
- all 72 contexts mechanically clean;
- >=4 V48 fire contexts;
- >=2 combined control fire contexts;
- V48 mean score delta >0;
- >=1 positive-score V48 context;
- zero win->nonwin regressions overall;
- zero negative-score contexts in V47 mirror;
- zero negative-score contexts in Ready Stock.

If activation is underpowered, only more untouched seeds may be added with the same frozen rule. If activation is sufficient but no W/L confirmation, O-LQ3C closes and pre-registered V9A activates. Any W/L regression closes O-LQ3C.

A V8D PASS does **not** automatically authorize Kaggle submission; it advances to broader regression/package readiness.

V9 remains pre-registered and dormant unless V8D closes O-LQ3C.

Preserve hosted pair:
- O-RW1 `56336027`;
- ALL3 `56367770`.

**Binding immediate action:** resolve workflow **`35516560425`**. No manual Kaggle submission.


## Binding update — 2026-09-20 — O-LQ3 CLOSED / V8C ACTIVE

**This block supersedes any lower stale "current", "binding next steps", or "immediate action" section.**

O-LQ3 Stage A workflow **`35480144515`** completed mechanically clean and is closed as **`O_LQ3_STAGE_A_FAIL`**:
- 4/4 frozen hard contexts replayed with zero failures;
- 12 O-LQ3 fires per context;
- loss->win flips: **0**;
- mean margin delta: **-1304.25**;
- V47 mirror 75113/seat1: -263 -> -374;
- V48 75103/seat1: -86 -> -2366;
- V48 75110/seat0: -484 -> -3187;
- V48 75113/seat1: -794 -> -917.

The V8B local direction **MILK -> WOOL -> FERTILIZER** is therefore **not** a globally safe priority. No post-result threshold/frequency rescue of O-LQ3 is permitted.

Initial V8C run **`35514319440`** is non-binding: it incorrectly inherited the 12-fires-per-context count from the cumulatively treated O-LQ3 trajectory. A first correction run **`35514495824`** is also non-binding because it preceded the aggregate-gate correction. No strategic branch outcome was used for this amendment. Baseline ALL3 discovery showed 11 fires in two seat-1 contexts, proving treated-trajectory fire count cannot define one-shot branch count.\n\nRun **`35514497453`** is also non-binding because the aggregate file contained a literal `\\n`, causing Python `SyntaxError` during the syntax step before any strategic simulation ran. The repaired binding execution is `35516167350`.\n\nThe binding next experiment is **V8C — Local Priority Value Atlas**, binding workflow **`35516167350`**, head commit **`b528ac9dafedefd17b65dfa7407b1b793adb6046`**.

V8C freezes the same four hard contexts and applies the unchanged O-LQ3 transform on **exactly one firing turn at a time**, then immediately resumes exact ALL3. Binding aggregate size is the exact sum of O-LQ3 firing states discovered on the untouched ALL3 baseline trajectories; every discovered state must be branched exactly once.

Frozen V8C decision:
- mechanics invalid, any context with zero baseline events, or branch count != exact baseline-discovered event count -> `V8C_MECHANICS_INVALID`;
- loss->win in >=2 distinct hard contexts -> `V8C_CONDITIONAL_ORDER_HEADROOM_REPEATABLE`;
- >=1 loss->win plus positive-margin states in >=2 contexts -> `V8C_CONDITIONAL_ORDER_HEADROOM_NARROW`;
- positive-margin states in >=2 contexts without a win flip -> `V8C_CONDITIONAL_ORDER_MARGIN_HETEROGENEOUS`;
- otherwise -> `V8C_CONDITIONAL_ORDER_NO_REUSABLE_HEADROOM`.

Only the first two strategic W/L branches may justify deriving **one** compact opponent-identity-free public-state condition, frozen before fresh-seed V8D validation. Margin-only evidence does not authorize a hosted candidate. If V8C finds no reusable W/L headroom, close this simple SELL-priority family rather than retune it.

Runtime robustness note: a community report suggested `obs["step"]` can be absent for seat 1, but our exact-engine V8A binding runs on `kaggle-environments==1.32.7` showed LQ2 firing normally in seat-1 contexts (97, 115 and 97 changed turns, with observed turns 577/600/673 etc.). Treat the report as an external portability warning, **not** as evidence of a current ALL3 failure. V8C targeting itself uses an internal deterministic turn counter.

V9 fallback is now pre-registered and **dormant** before the V8C result: `docs/strategy/ALL3_V9_RESIDUAL_STRUCTURAL_DECOMPOSITION_PROTOCOL_2026-09-20.md`. It activates only if binding V8C closes without reusable W/L headroom; otherwise it remains dormant.\n\nPreserve hosted pair:
- O-RW1 submission `56336027`;
- ALL3 submission `56367770`.

**Binding immediate action:** resolve binding workflow **`35516167350`** once complete; do not submit a new Kaggle candidate from O-LQ3/V8C discovery alone.


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

### ALL3 — HOSTED STATE

Current intended active pair:
1. O-RW1 `56336027`;
2. ALL3 `56367770`.

Latest hosted snapshot:
- ALL3 **2412.1**;
- O-RW1 **2361.6**.

These live ratings are observational and come from different histories/populations.

ALL3 first-informative checkpoint remains:
- 35 listed public episodes;
- 34 resolved external games;
- 28W / 6L / 0T;
- raw score rate 0.8235294;
- 33 unique opponents;
- mean margin +13,626.97.

### O-HV1 — CLOSED

Binding:
`O_HV1_DEV_CLOSE`.

No threshold/product rescue.

Result:
`docs/strategy/O_HV1_HIGH_VALUE_STOCK_FLUSH_RESULT_2026-09-19.md`.

### O-PC1 — CLOSED

Binding:
`O_PC1_DEV_CLOSE`.

Fresh paired result:
- mean score delta -0.25;
- 6 negative-score contexts;
- 0 positive-score contexts.

No ratio/start-step/yield rescue.

Result:
`docs/strategy/O_PC1_PROFIT_DOMINANT_CROP_ROTATION_RESULT_2026-09-19.md`.

### V5 Physical Proposal Oracle — CLOSED MARGIN-ONLY

Corrected binding runs:
- `35470046629`;
- `35470051852`.

Both agree exactly:
**`V5_PHYSICAL_MARGIN_ONLY`**.

Overall:
- 32 branch states;
- base score rate 0.9375;
- oracle score rate 0.9375;
- score delta 0;
- nonwin->win flips 0;
- loss->win flips 0;
- mean oracle margin delta +505.65625;
- median 0;
- 14 positive-margin states.

By opponent:
- router_2715: +1,317.625 mean margin, no W/L gain;
- Tactical Memory: +694, no W/L gain;
- V47 mirror: +11, no W/L gain;
- V48: 0 margin gain, no W/L gain.

Only non-winning V5 base trajectory:
- V48;
- seed 75002;
- seat 0;
- final margin -26.

No one-turn physical branch changed that result.

Therefore:
- do not promote V5 transforms;
- do not first-party PASS/movement micro-patches;
- close one-turn localized physical substitution as an option source.

Result:
`docs/strategy/ALL3_PHYSICAL_PROPOSAL_ORACLE_V5_RESULT_2026-09-19.md`.

### V6A hard-context census — COMPLETE

Binding runs:
- Batch A `35472777632`;
- Batch B `35473134791`.

Combined:
- 224 exact ALL3 games;
- **220W / 4L / 0T**;
- mechanical PASS;
- decision **`V6A_HARD_CONTEXTS_READY`**.

Frozen hard contexts:
1. V47 mirror — seed `75113`, seat 1, margin -263;
2. V48 — seed `75103`, seat 1, margin -86;
3. V48 — seed `75110`, seat 0, margin -484;
4. V48 — seed `75113`, seat 1, margin -794.

Config:
`configs/all3_v6_hard_contexts.json`.

Result:
`docs/strategy/ALL3_V6A_HARD_CONTEXT_CENSUS_AB_RESULT_2026-09-19.md`.

### V6 bounded physical continuation — CLOSED

Binding lifecycle-corrected workflow:
`35473780009`.

Decision:
**`V6_CONTINUATION_MARGIN_ONLY`**.

Mechanical:
- PASS;
- failures 0;
- 4 frozen hard contexts.

Strategic:
- loss->win flips: 0;
- mean oracle margin delta: +68.5.

Best hard-context outcomes:
- V47 mirror -263 -> -96;
- V48 -86 -> -76;
- V48 -484 -> -484;
- V48 -794 -> -697.

Therefore:
- close one-locus H2/H3 continuation as a W/L source;
- do not extend horizon automatically;
- do not promote margin-only physical patches.

Result:
`docs/strategy/ALL3_V6_BOUNDED_PHYSICAL_CONTINUATION_RESULT_2026-09-19.md`.

### V7 option-composition attribution — CLOSED

Workflow:
`35479297555`.

Decision:
**`V7_STATIC_COMPOSITION_MARGIN_ONLY`**.

No non-ALL3 composition rescued any of the four hard losses.

Mean margins:
- ALL3 -406.75;
- best alternative TW_LQ2 -399.75;
- LQ2 -420.5;
- V47 -1520.25.

Interpretation:
LQ2 is the dominant value-producing mechanism; static suppression is not the residual W/L answer.

Result:
`docs/strategy/ALL3_V7_OPTION_COMPOSITION_ATTRIBUTION_RESULT_2026-09-19.md`.

### V8A LQ2 residual SELL-run census — COMPLETE

Workflow:
`35479557496`.

Decision:
**`V8A_ORDER_SEARCH_READY`**.

Aggregate:
- 424 LQ2-changed turns;
- 170 eligible post-LQ2 multi-product SELL-run states;
- all 4 hard contexts represented;
- max 6 distinct products in one SELL run.

Frozen V8B states:
- context 0: steps 673, 577;
- context 1: steps 673, 600;
- context 2: steps 673, 600;
- context 3: steps 673, 577.

Config:
`configs/all3_v8b_lq2_order_states.json`.

Result:
`docs/strategy/ALL3_V8A_LQ2_RESIDUAL_SELL_RUN_CENSUS_RESULT_2026-09-19.md`.

### V8B LQ2 SELL-order oracle — COMPLETE

Workflow:
`35479783995`.

Decision:
**`V8B_ORDER_HEADROOM_NARROW`**.

Mechanical:
- PASS;
- zero failures;
- 1 / 4 hard-context loss->win flip;
- mean best-branch margin delta +96.

Strongest results:
- V48 75103/seat1, step 600: FERTILIZER 11 <-> WOOL 7, **-86 -> +10**;
- V48 75110/seat0, step 600: WOOL 7 <-> MILK 16, **-484 -> -220**.

The shared local direction is:
**MILK -> WOOL -> FERTILIZER**.

Result:
`docs/strategy/ALL3_V8B_LQ2_SELL_ORDER_ORACLE_RESULT_2026-09-19.md`.

### O-LQ3 priority SELL ordering — STAGE A ACTIVE

Workflow:
**`35480144515`**.

Candidate:
within each post-LQ2 SELL run, stable-sort only orders currently occupying MILK/WOOL/FERTILIZER
slots by fixed public priority:

`MILK -> WOOL -> FERTILIZER`.

Invariants:
- non-target products remain in their original slots;
- quantities unchanged;
- non-SELL slots unchanged;
- farmer/hands unchanged;
- market multiset unchanged;
- no opponent identity.

Stage A:
exact paired ALL3 vs ALL3+LQ3 replay on the four frozen hard contexts.

Gate:
- >=1 loss->win and positive mean margin delta -> Stage A PASS and fresh paired Stage B;
- zero flips but positive mean delta -> directional-only, narrow the legal-state condition;
- nonpositive mean or mechanics invalid -> fail.

No Kaggle submission is authorized by Stage A.

### Binding next steps

1. Resolve V6A `35472681958`.
2. If >=4 fresh nonwins: freeze selected hard-context list exactly.
3. Run bounded 2–3-turn localized physical continuation oracle only on those contexts.
4. If <4: expand untouched seed census before branching.
5. Preserve O-RW1 + ALL3 hosted pair.
6. No new Kaggle submission from V5/V6A discovery evidence.

## Historical record (superseded where inconsistent with the current handoff)

Updated: 2026-09-15

## Mission / objective

Maximize the probability of winning or reaching the prize frontier in Kaggriculture. Novelty is not the objective. Every legal piece of accumulated competitive, replay, mechanics and economic knowledge remains admissible unless stronger evidence supersedes it.

Authoritative branches:

- competitive source of truth: `fix/kaggle-parity-v1`
- experimental mechanics/integration: `research/first-principles-economy-v1`

## Engine / legality lock

- official evaluation path: `kaggle-environments==1.32.7`
- frozen upstream reference commit: `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`
- public `town.unlocked_shops` is shared/legal runtime state and may contain repeated shop names
- no runtime identity, rating, EpisodeId, hidden seed, future state or direct opponent-private features
- original final holdout remains sealed

## Competitive target / calibration

Frozen external snapshot 2026-09-14: leader ~`3191`, rank 10 ~`2958`; target remains roughly `3000+`.

Strongest exact project-hosted anchor:

- **CR053_REAL** — submission `56073870`, checkpoint ~`2064.8`
- exact SHA `095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15`
- source run `34105008373`, artifact `10012004237`

Other exact anchors: CR052_REAL ~`1749.2`; CR083 ~`1619.9`; CR086 ~`1612.6`.

Critical warning: exact-byte league `34802917553` locally ranked CR083/CR086 above CR053 although hosted Kaggle ranks CR053 materially higher. Local H2H is useful for mechanics, causal interventions, catastrophe and diversity, **not** as a hosted-rating oracle.

## Retained competitive / FP001 knowledge

- CR086 legal latent-opponent-supply estimator and SELL-priority operator are retained; CR086 itself is not the preferred backbone.
- CR087/CR088 elite macro/replay knowledge is retained; direct tape backbones remain closed.
- H1 WHEAT town-pulse carry, H1B sale deferral, H8/B3+DAILY CARE, H9 demand representation, H10 batching/routing, H11 fertilizer conversion and M6S1 remain reusable primitives/modules.
- M6S1 is a genuine economic module, not a standalone competitive backbone.

## CR089 — COMPLETE / FAIL

Run `34923802262`: C5_BASE and C5_M6S1 each **0W–132L**, 11/11 zero-score edges, zero mechanical failures. Static C5/C5+M6S1 are closed as competitive backbones; M6S1 survives as a module.

## CR090 — COMPLETE / FAIL

Run `34979280512`. Mechanics exact. YARN adaptive SHEEP minus delayed COW was negative; MILK adaptive COW minus delayed SHEEP strongly positive; natural adaptive policy did not beat delayed COW.

Binding verdict: `CR090_H9_CAUSAL_FAIL_CLOSE_SIMPLE_SPECIES_ADAPTATION`. No threshold rescue; H9 survives only as a state feature/prior.

## CR091 — COMPLETE / PASS

Binding rerun: **`34990757344`**, research commit `f49bff2e7adde626b01b9fa3c0413f7fc97d9649`.

Artifact: `cr091-hierarchical-market-option-gate-v1`, ID `10406926564`, ZIP SHA-256 `d6d9a5a7cb187e48dc4cb187e348adb7fff4d10666f18f27b4030ccc8ad2f3d0`.

The earlier run `34987640694` remains invalid/non-binding because its direct-`exec()` harness failed CR052 package semantics.

CR091 compared exact CR053 against exact CR053 plus the exact CR086 latent-supply SELL-priority operator, changing only the order of existing market orders.

Mechanics on the valid rerun:

- 128/128 episodes valid;
- failures: **0**;
- parity violations: **0**;
- exact farmer/hand parity every call;
- exact normalized market-order multiset parity every call;
- exact BASE full-action parity every call;
- O1 active with **1,075** market reorders.

Seat-balanced edge-score deltas `O1 - BASE`:

- CR052_REAL: `0.0000`
- CR053_REAL: `+0.1875`
- CR083: `0.0000`
- CR086: `0.0000`

Summary: 4/4 nonnegative edges, mean delta `+0.046875`, maximum `+0.1875`, worst regression `0.0`.

Binding verdict: **`CR091_LATENT_OPTION_TRANSFER_PASS_ADVANCE_ROUTER`**.

Interpretation: CR086 is not promoted as a backbone. Its latent-priority mechanism is promoted as frozen separable option **O1** on exact CR053. No threshold retuning.

Result: `docs/strategy/CR091_HIERARCHICAL_MARKET_OPTION_RESULT_2026-09-15.md`.

## Current binding gate — CR092 broad O1 transfer / router labels

Protocol: `docs/strategy/CR092_BROAD_OPTION_ROUTER_LABEL_PROTOCOL_2026-09-15.md`.

Purpose: test frozen O1 on the broader 11-edge CR089 population and collect causally clean public-state labels for a later router.

Frozen population:

- exact anchors: CR053_REAL, CR052_REAL, CR083, CR086;
- macro reps: `r01`, `r02`, `r03`, `r06`, `r07`, `r09`, `r10` from the exact CR089 frozen population artifact `10378299284`.

Fresh evaluation:

- seeds `91401..91406`;
- both seats;
- 12 games/treatment/edge;
- 132 games per treatment, 264 total;
- exact hosted-faithful package runner;
- no hosted submission.

Counterfactual label rule: for each matched BASE/O1 episode, record O1's legal state immediately before its first actual market reorder. A label is admissible only if that strategic-state hash exactly matches BASE's state hash at the same step. Primary label is `outcome(O1) - outcome(BASE)`; terminal money is diagnostic only. Opponent ID is offline stratification metadata only and is forbidden as a router feature.

Frozen broad-survival gate requires mean edge delta >= `+0.02`, >=8/11 nonnegative edges, worst regression >= `-0.125`, macro mean delta >=0 and no new zero-score catastrophe from a BASE edge >=0.25.

Frozen routing signal requires at least 8 positive and 8 negative hash-valid labels spanning at least two opponent strata per sign.

Implementation on research branch:

- `tools/cr092_broad_option_edge.py`
- `tools/cr092_aggregate.py`
- `.github/workflows/cr092-broad-option-router-label.yml`
- workflow/head commit `b42347617a6967eeb2862fde23737c7538d3b9d3`
- active run **`35015135956`**
- prepare job already PASS: all 11 opponent packages downloaded and SHA-verified.

Frozen outcomes:

- broad survivor + heterogeneous labels -> `CR092_BROAD_PASS_HETEROGENEOUS_ADVANCE_ROUTER`
- broad survivor without downside support -> `CR092_BROAD_PASS_O1_ADVANCE_NEXT_OPTION`
- broad fail but strong heterogeneous option value -> `CR092_BROAD_FAIL_HETEROGENEOUS_ADVANCE_ROUTER_DISCOVERY`
- otherwise -> `CR092_BROAD_FAIL_CLOSE_ALWAYS_ON_O1`
- mechanics failure -> no strategic verdict.

## Closed / do-not-retune absent new evidence

CR078/079, CR080 replay stitching, CR081 static market-prefix transplant, CR082 1-NN imitation, CR084 FEED rescue, CR085 Pareto gating, direct CR088 tapes, static C5/C5+M6S1, fixed C3S2/C2S3, simple CR090 first-shop species rule.

## Hosted policy

No CR092 outcome automatically authorizes a Kaggle submission. Hosted slots remain high-information population sensors, used only after a mechanically exact state-adaptive or multi-option candidate survives broad fresh-seed evaluation without a major catastrophe edge.
