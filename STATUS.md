# STATUS — Kculture live source of truth

## Current solver handoff — 2026-09-18

Active branch: `research/prize-solver-v0`.

### Hosted-entrypoint correction remains binding

Public agents must be loaded with:
`kaggle_environments.agent.get_last_callable`.

Exact public V47 hosted entrypoint:
`_y_agent_shopherd`.

Hosted treatment submission `56333579` from the first A/B is mechanically invalid and
must never be interpreted as O-RW1 competitive evidence.

### O-RW1 hosted-faithful causal gate — PASS

Workflow `35363453097`, artifact `10555907821`:
- 48 valid branch states;
- mean score delta **+0.0833333**;
- 8 non-win -> win flips;
- 0 win -> non-win regressions;
- 0 negative-W/L states;
- mean margin delta +14.9583.

### O-RW1 hosted-faithful autonomous runtime — PASS

Workflow `35367785929`, artifact `10558221804`, exact engine `1.32.7`.

BASE is exact public V47 resolved through the official hosted loader to
`_y_agent_shopherd`.

Results:
- 64 paired matchups / 128 complete episodes;
- zero failures;
- BASE score rate **0.6250**;
- V47 + O-RW1 score rate **0.71875**;
- W/L delta **+0.09375**;
- **14 non-win -> win flips**;
- **0 win -> non-win regressions**;
- 14 positive-score pairs;
- 2 negative-score pairs;
- 48 neutral pairs;
- all 4 opponent blocks had nonnegative mean score delta;
- worst block mean score delta 0.0.

Per opponent:
- V47 mirror: `0.500 -> 0.875`, delta **+0.375**;
- V48: `0.000 -> 0.000`;
- Tactical Memory: `1.000 -> 1.000`;
- Ready Stock: `1.000 -> 1.000`.

Important: O-RW1 is **not universally safe**. Seed 65008 versus V47 mirror produced two
tie->loss regressions. It is nevertheless positive on the frozen aggregate gate and had
no win->non-win regressions.

Money margin is diagnostic only:
- mean margin delta -805.78125;
- median +10;
- Tactical Memory generated large negative money deltas without changing W/L wins.

Binding verdict:
`READY_WOOL_RUNTIME_PASS`.

Result:
`docs/strategy/READY_WOOL_RUNTIME_HOSTED_FAITHFUL_RESULT_2026-09-18.md`.
Machine-readable:
`data/programme_teacher/2026-09-18/READY_WOOL_RUNTIME_HOSTED_FAITHFUL_SUMMARY.json`.

Frozen O-RW1 remains unchanged:
```
if not used
and hosted-faithful V47 market == []
and own private shed.WOOL >= 2
and step <= 671:
    execute SELL WOOL 2
    used = True
```

### Current binding gate — corrected hosted package parity

Active workflow:
**`35372564746`**, head
`a8830bef5b930f5178c836e9f9c8dbedbc4e5245`.

The package gate now requires:
- exact base hosted entrypoint `_y_agent_shopherd`;
- exact candidate hosted entrypoint `_kc_orw1_entrypoint`;
- exact action parity vs the hosted-faithful reference implementation;
- exact reward parity;
- deterministic archive/SHA manifest.

No new Kaggle submission is authorized until this package gate passes.

No O-RW1 retuning is authorized.
No Ryzen action is required.

The FP001_STATUS/FP001_ROADMAP files are absent on this branch; do not silently create
competing copies or change other branches as part of this solver update.

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
