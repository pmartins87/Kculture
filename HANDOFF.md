# HANDOFF — Kculture

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

### V2 opponent league — preflight + smoke PASS

The full seven-agent diverse league is frozen and mechanically validated:
- V47 mirror;
- Ready Stock;
- V48;
- `2715.6` multi-program router;
- Conditional Memory;
- Tactical Memory;
- Best Market Agent.

Hosted-faithful package/entrypoint preflight: **7/7 PASS**.

Binding smoke:
- workflow **`35421692326`**;
- conclusion **SUCCESS**;
- pinned `kaggle-environments==1.32.7`;
- syntax PASS;
- one-seed seven-opponent generator execution PASS;
- artifact upload PASS.

### Binding next steps

1. Run the resumable Ryzen V2 production dataset:
   **150 fresh seeds × 7 opponents × 2 seats × 2 options**, maximum about **4,200 labels**.
2. Do not fit/freeze a production selector merely because V1 passed.
3. After V2 completes, rerun train/dev/test with whole-seed isolation and add leave-family-out
   evaluation over the expanded league.
4. Promote a selector to autonomous runtime gates only if V2 held-out value remains positive
   and cross-family behavior is defensible; otherwise expand/revise the option/feature set rather
   than brute-force more training.
5. No new Kaggle submission; preserve both active hosted slots while this offline work proceeds.

## Historical record (superseded where inconsistent with the current handoff)

> **Current update — 2026-09-15:** CR091 completed with a valid PASS. The frozen CR086 latent-supply SELL-priority mechanism is now option **O1** on exact CR053. The current binding gate is **CR092 — broad O1 transfer + counterfactual router labels**, workflow `35015135956`.

## Mission

Win / maximize prize probability in Kaggriculture. Novelty is irrelevant unless it improves competitive strength. All accumulated legal competitive, replay, mechanics and economic knowledge remains usable unless stronger evidence supersedes it.

## Authoritative branches

- competition/source of truth: `fix/kaggle-parity-v1`
- experimental integration: `research/first-principles-economy-v1`

Read first:

1. `STATUS.md`
2. `ROADMAP.md`
3. `docs/strategy/CR091_HIERARCHICAL_MARKET_OPTION_RESULT_2026-09-15.md`
4. `docs/strategy/CR092_BROAD_OPTION_ROUTER_LABEL_PROTOCOL_2026-09-15.md`
5. `docs/strategy/CR091_RUN1_INVALID_2026-09-15.md` only for the invalid-run warning
6. experimental `docs/strategy/FP001_STATUS.md` / `FP001_ROADMAP.md`

## Competitive anchors / calibration

- **CR053_REAL**: strongest exact project-hosted anchor; submission `56073870`, checkpoint ~`2064.8`, SHA `095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15`.
- CR052_REAL ~`1749.2`.
- CR083 ~`1619.9`.
- CR086 ~`1612.6`.
- frozen external frontier 2026-09-14: top ~3191; rank 10 ~2958; target remains ~3000+.

Critical calibration: exact-byte local H2H can reverse hosted order. Use local exact-engine work for mechanics, causal intervention, catastrophe and diversity, not as a direct hosted-rating predictor.

## Closed major routes

Keep closed absent new causal evidence changing the failure mechanism: CR078/079; CR080 replay stitching; CR081 static market-prefix transplant; CR082 1-NN imitation; CR084 FEED rescue; CR085 Pareto gating; direct CR088 tape backbones; static C5/C5+M6S1; fixed C3S2/C2S3; CR090 simple first-shop species selector.

## Retained modules / knowledge

CR053 macro/physical route; CR086 latent-supply estimator + SELL priority; CR087/CR088 elite macro/replay corpus; H1 WHEAT carry; H1B sale deferral; H8/B3+DAILY CARE; H9 public-shop demand representation; H10 compact routing/batching; H11 fertilizer conversion; M6S1 as an economic module.

## CR089 / CR090

CR089 run `34923802262`: C5_BASE and C5_M6S1 each 0W–132L. Static C5 closed; M6S1 retained as a module.

CR090 run `34979280512`: simple H9 COW/SHEEP rule failed causally despite a strong MILK/COW contrast. Binding verdict `CR090_H9_CAUSAL_FAIL_CLOSE_SIMPLE_SPECIES_ADAPTATION`; H9 remains a state representation, not a standalone action rule.

## CR091 — COMPLETE / PASS

The first run `34987640694` is invalid/non-binding because direct `exec()` did not reproduce CR052 package semantics.

The authoritative hosted-faithful rerun is **`34990757344`**, head commit `f49bff2e7adde626b01b9fa3c0413f7fc97d9649`.

Artifact `cr091-hierarchical-market-option-gate-v1`, ID `10406926564`, ZIP SHA-256 `d6d9a5a7cb187e48dc4cb187e348adb7fff4d10666f18f27b4030ccc8ad2f3d0`.

Mechanics:

- 128 valid episodes;
- failures 0;
- parity violations 0;
- exact CR053 farmer/hand parity;
- exact normalized market-order multiset parity;
- exact BASE full-action parity;
- O1 active with 1,075 reorders.

Seat-balanced W/L edge deltas `O1 - BASE`:

- CR052_REAL: `0.0000`
- CR053_REAL: `+0.1875`
- CR083: `0.0000`
- CR086: `0.0000`

Mean edge delta `+0.046875`, 4/4 nonnegative, worst regression `0`.

Binding verdict: **`CR091_LATENT_OPTION_TRANSFER_PASS_ADVANCE_ROUTER`**.

Promote the exact CR086 latent-priority mechanism to frozen option **O1** on exact CR053. Do not retune it. CR086 itself is not promoted as the backbone.

## Current binding experiment — CR092

Protocol: `docs/strategy/CR092_BROAD_OPTION_ROUTER_LABEL_PROTOCOL_2026-09-15.md`.

Purpose: test frozen O1 on the broader frozen CR089 population and collect hash-validated public-state counterfactual labels for a future router.

Population:

- exact anchors: CR053_REAL, CR052_REAL, CR083, CR086;
- current-top macro representatives: r01/Majkel, r02/SpaTaro, r03/ymg-Howard, r06/Orbital, r07/feel, r09/Otter, r10/redblack;
- exact CR089 frozen population artifact `10378299284`.

Evaluation:

- fresh seeds `91401..91406`;
- both seats;
- exact BASE vs frozen O1;
- 12 games/treatment/edge;
- 264 episodes total;
- 11 edge jobs parallelized;
- exact `kaggle-environments==1.32.7` hosted-faithful package execution.

Counterfactual labels:

- at O1's first actual reorder, capture the legal strategic observation;
- accept the label only if BASE has the identical strategic-state hash at the same step for the same opponent/seed/seat;
- primary label is `W/L(O1) - W/L(BASE)`;
- terminal money is diagnostic only;
- opponent identity and seed are offline metadata only and may not be router features.

Frozen decision branches:

- broad survivor + heterogeneous causal labels -> `CR092_BROAD_PASS_HETEROGENEOUS_ADVANCE_ROUTER`;
- broad survivor without meaningful downside support -> `CR092_BROAD_PASS_O1_ADVANCE_NEXT_OPTION`;
- broad fail but strong heterogeneous option value -> `CR092_BROAD_FAIL_HETEROGENEOUS_ADVANCE_ROUTER_DISCOVERY`;
- otherwise -> `CR092_BROAD_FAIL_CLOSE_ALWAYS_ON_O1`;
- mechanics failure -> no strategic verdict.

Implementation:

- `tools/cr092_broad_option_edge.py`
- `tools/cr092_aggregate.py`
- `.github/workflows/cr092-broad-option-router-label.yml`
- workflow/head commit `b42347617a6967eeb2862fde23737c7538d3b9d3`
- active workflow **`35015135956`**
- prepare job already PASS: all 11 packages downloaded and SHA-verified.

## Non-negotiable legality / evaluation

Engine `kaggle-environments==1.32.7`; no identity/rating/EpisodeId/hidden seed/future/direct opponent-private runtime features; `town.unlocked_shops` legal shared state; original final holdout sealed; no automatic CR092 hosted submission.

## Immediate next action

Query workflow `35015135956` once on the next continuation. If complete, read the frozen aggregate and follow its declared branch immediately. Do not manually submit anything to Kaggle while CR092 is unresolved.
