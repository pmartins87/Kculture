# STATUS — Kculture live source of truth

## Current solver handoff — 2026-09-19

Active branch: `research/prize-solver-v0`.

### Hosted pair — preserve both slots

Maturity snapshot around 100 episodes:
- CONTROL `56336025`: rating **2429.1**, 103 listed / 102 resolved external, 76-24-2;
- O-RW1 `56336027`: rating **2506.7**, 106 listed / 105 resolved external, 60-44-1.

These are not matched opponent populations. Raw W/L is not a causal A/B comparison.
The hosted treatment remains higher-rated; do not replace either slot while offline
selector/value work proceeds.

Audit:
`docs/strategy/ORW1_HOSTED_R2_MATURITY_100_AUDIT_2026-09-19.md`.

### Option-value Ryzen V1 — production PASS

User Ryzen run completed on exact engine `1.32.7`:
- 250/250 fresh seeds;
- 1,500 BASE matchups;
- **3,000 counterfactual option labels**;
- **584 unique state hashes**;
- **0 failures**;
- opponents: V47 mirror, V48, Tactical Memory;
- both seats.

O-RW1:
- 1,500 rows;
- mean score delta **+0.096**;
- 370 positive / 82 negative / 1,048 neutral;
- mean margin delta **-161.6493**.

O-TW1:
- 1,500 rows;
- mean score delta **+0.14**;
- 436 positive / 16 negative / 1,048 neutral;
- mean margin delta **+35.7173**.

Population decomposition:
- V47 mirror: mean score delta **+0.354**, 806 positive / 98 negative;
- V48: W/L delta 0 throughout;
- Tactical Memory: W/L delta 0 throughout.

Conclusion:
the options have real large-sample headroom, but W/L signal is currently concentrated in
V47-mirror states. Do **not** train/deploy a production selector until learnability and
population generalization are audited.

Result:
`docs/strategy/OPTION_VALUE_RYZEN_V1_RESULT_2026-09-19.md`.

### Current gate — OPTION_VALUE_SELECTOR_AUDIT_V1

Tool:
`tools/option_value_selector_audit_v1.py`

One-command runner:
`tools/run_option_value_selector_audit_v1.sh`

The audit measures:
- repeated state+option label conflicts;
- legal-feature alias conflicts;
- grouped train/dev/test split with state-hash isolation;
- ridge selector realized delta versus BASE / always-fire / row-oracle;
- leave-one-opponent-out transfer.

No opponent identity, seed, seat, rating, hidden/future state is a model feature.

### V2 opponent league preflight

Workflow `35420988150` is validating a more diverse seven-agent public league:
- V47 mirror;
- Ready Stock;
- V48;
- V39 legacy;
- Conditional Memory;
- Tactical Memory;
- Best Market Agent.

This preflight is cloud-only and does not consume Ryzen or Kaggle submission slots.

### Binding rules

- No new Kaggle submission yet.
- Preserve both hosted slots.
- No further heavy Ryzen batch until selector audit is read.
- If V1 selector generalizes, fit a conservative selector and validate offline.
- If V1 signal is population-bound, expand labels with the validated V2 league first.
- FP001_STATUS/FP001_ROADMAP remain absent; do not create competing copies.

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
