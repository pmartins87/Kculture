# HANDOFF — Kculture

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
