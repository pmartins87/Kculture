# CR092 — broad O1 transfer and counterfactual router-label gate

Date: 2026-09-15  
Authoritative branch: `fix/kaggle-parity-v1`

## Objective

Test whether the exact CR091 survivor O1 — CR086 latent-supply SELL-priority ordering applied to exact CR053 — retains competitive W/L value on a broader heterogeneous population, and collect causally clean public-state labels for a future option-value router.

This is **not** a parameter-tuning gate. O1 is frozen exactly as validated in CR091.

## Frozen treatments

1. `CR053_BASE`: exact hosted CR053 package, SHA `095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15`;
2. `CR053_O1`: the same exact CR053 package action with only the sequence of existing market orders changed by the exact CR086 latent-supply cash-risk priority operator from SHA `11296a4e658f37c109a2cc953be0ea7db8e2fbde6286ac483e0466f52f4af888`.

No farmer, hand, market product or market quantity may change. No O1 threshold or estimator constant may be modified after CR091.

## Frozen population

Reuse the exact 11-opponent CR089 population artifact `cr089-frozen-population-packages-v1`, artifact ID `10378299284`, ZIP SHA-256 `5c84b0d2428b60fedb25d237ddba50f480d747099092b25e02cb837bd5178a33`.

Exact hosted anchors:

- `CR053_REAL`;
- `CR052_REAL`;
- `CR083`;
- `CR086`.

Seven coherent current-top macro representatives:

- `r01_e108766633_s56156662` — Majkel family;
- `r02_e108761464_s56114097` — SpaTaro family;
- `r03_e108766659_s56209748` — ymg/Howard family;
- `r06_e108754069_s56205640` — Orbital family;
- `r07_e108766657_s56132899` — feel family;
- `r09_e108766659_s56097405` — Otter family;
- `r10_e108754200_s56210228` — redblack family.

The seven macro packages are interaction-path representatives, not claims of exact hidden top-agent code or hosted ratings.

## Fresh evaluation

- official runtime: `kaggle-environments==1.32.7`;
- hosted-faithful spawned package execution via the existing `kaggle_exact_runtime.AgentProcess` path;
- fresh seeds: `91401..91406`;
- both seats;
- 12 games per treatment per edge;
- 132 games per treatment;
- 264 episodes total;
- original final holdout remains sealed;
- no automatic Kaggle submission.

Edges should run independently/parallel where possible; aggregation is performed only after all edge artifacts exist.

## Mandatory mechanics gate

CR092 is strategically interpretable only if all are true:

- all 264 episodes finish validly with zero execution/non-DONE errors;
- exact CR053 farmer and hand parity on every candidate call;
- exact normalized CR053 market-order multiset parity on every candidate call;
- `CR053_BASE` has exact full-action parity with the exact CR053 package;
- O1 actually reorders at least one market call;
- no candidate uses runtime identity, rating, EpisodeId, hidden seed, future state or opponent-private state.

A mechanics failure produces no strategic verdict; repair runner semantics only.

## Counterfactual label design

For each `(opponent, seed, seat)` pair, BASE and O1 are run from the same environment seed and seat.

For O1, record the **legal observation immediately before the first call on which O1 changes the ordering of CR053's market orders**. Until that point, BASE and O1 actions should be identical, so the state is intended to be a common causal branch point.

To prove that premise rather than assume it, both treatments must record a hash of the strategic observation at each controlled-agent call. The strategic hash excludes only framework timing bookkeeping such as `remainingOverageTime`; it retains the game state visible to the agent. An O1 branch label is admissible only if the O1 first-reorder strategic-state hash exactly equals the BASE strategic-state hash at the same step for the same `(opponent, seed, seat)` pair.

Pair each hash-validated branch state with:

- `wl_delta = outcome(O1) - outcome(BASE)` as the primary label;
- terminal-margin delta as diagnostic only;
- first-reorder step;
- frozen CR086 derived estimator state where serializable;
- opponent identifier retained **only as offline stratification metadata**, never as a runtime router feature.

The raw branch-state record may include only legal runtime information visible to the controlled agent: clock/step, own private resources, public farms, public market, public town/shop state and mechanics-derived O1 estimator summaries.

This dataset is for CR093 router discovery. CR092 does not fit a router after observing these labels.

## Aggregate W/L measures

For every edge report:

- BASE score;
- O1 score;
- `O1 - BASE` score delta;
- wins/ties/losses;
- both seat scores;
- mean/median margin as secondary diagnostics;
- reorder counts and first-reorder-step distribution.

Also report:

- mean and median edge-score delta over all 11 edges;
- mean macro-only delta over the seven current-top representatives;
- number of positive/nonnegative/regressed edges;
- maximum improvement and worst regression;
- any new zero-score/catastrophe edge;
- paired counterfactual label counts (`positive`, `zero`, `negative`), distinct opponent strata contributing each sign, and count of rejected labels due to branch-state mismatch.

## Frozen broad-survival rule

`BROAD_SURVIVAL = true` only if all are true:

- mechanics pass;
- all 11 edge deltas are available;
- mean edge-score delta >= `+0.02`;
- at least `8/11` edges are nonnegative;
- worst edge regression >= `-0.125`;
- mean delta over the seven macro representatives >= `0.0`;
- no edge with BASE score >= `0.25` is converted to O1 score `0.0`.

These thresholds test broad safety/transfer, not hosted-rating prediction.

## Frozen routing-signal rule

`ROUTING_SIGNAL = true` only if all are true:

- every label used for routing passed branch-state hash parity;
- at least 8 hash-validated matched branch-state labels have `wl_delta > 0`;
- at least 8 have `wl_delta < 0`;
- positive labels occur in at least 2 distinct opponent strata;
- negative labels occur in at least 2 distinct opponent strata.

This merely establishes enough heterogeneous causal support to justify CR093. It does not authorize using opponent identity as a feature.

## Frozen outcomes

### A — broad survivor + heterogeneous value

If `BROAD_SURVIVAL` and `ROUTING_SIGNAL`:

`CR092_BROAD_PASS_HETEROGENEOUS_ADVANCE_ROUTER`

- retain O1;
- freeze CR092 branch-state dataset;
- advance CR093 to a small legal public-state router;
- CR093 must train/validate without opponent identity and compare router vs always-BASE vs always-O1 on fresh seeds.

### B — broad survivor without meaningful downside support

If `BROAD_SURVIVAL` and not `ROUTING_SIGNAL`:

`CR092_BROAD_PASS_O1_ADVANCE_NEXT_OPTION`

- retain O1 as an always-on candidate option;
- do not invent a selector for a treatment that shows insufficient heterogeneous causal support;
- add the next separable option family, initially H1/H1B sale timing on exact CR053/O1 host, then evaluate multi-option routing.

### C — not broadly safe, but strong heterogeneous option value

If not `BROAD_SURVIVAL`, but `ROUTING_SIGNAL` and both `max edge improvement >= +0.125` and `worst edge regression <= -0.125`:

`CR092_BROAD_FAIL_HETEROGENEOUS_ADVANCE_ROUTER_DISCOVERY`

- prohibit always-on O1 promotion;
- preserve O1 only as a conditional option;
- advance CR093 router discovery using public state only.

### D — broad option failure

Otherwise:

`CR092_BROAD_FAIL_CLOSE_ALWAYS_ON_O1`

- do not threshold-tune O1;
- preserve CR086 estimator knowledge and the CR091 causal result as historical evidence;
- close always-on O1 as the current route;
- move to H1/H1B timing as the next separable option family.

## Hosted policy

No CR092 outcome automatically submits to Kaggle. A hosted sensor is considered only after a state-adaptive or multi-option candidate survives fresh-seed broad population evaluation with exact mechanics and no major catastrophe edge.
