# STATUS — Kculture live source of truth

## Current solver handoff — 2026-09-18

Active branch: `research/prize-solver-v0`.

### Critical hosted-entrypoint correction

The first authorized O-RW1 hosted A/B exposed a loader mismatch.

Exact public V47 CONTROL submission `56333577` loaded as the true hosted entrypoint:
`_y_agent_shopherd`.

The O-RW1 TREATMENT submission `56333579` loaded as:
`_kc_orw1_wool`
instead of the intended wrapper. Its hosted replay emitted PASS-only actions and therefore
is mechanically invalid as an O-RW1 competitive sensor.

The root cause is broader than packaging: Kculture helper
`tools.programme_adaptive_expert_gate.load_public_agent()` used `mod.agent`, while
Kaggle uses `kaggle_environments.agent.get_last_callable`. Public V47 retains an older
`agent` symbol and appends later wrappers, so `mod.agent` is not hosted-faithful.

Correction commit:
`b78477bdd80d51bfb63333ab2017c6242131d6d2`.

Correction record:
`docs/strategy/HOSTED_ENTRYPOINT_PARITY_CORRECTION_2026-09-18.md`.

Until rerun with the official hosted loader, the following are **not valid promotion
evidence**:
- Wrapper Proposal Oracle V2b run `35310754131`;
- O-RW1 causal run `35311750191`;
- O-RW1 runtime run `35313204723`;
- O-RW1 package parity run `35360173417`;
- hosted treatment submission `56333579`.

Exact public V47 CONTROL submission `56333577` remains valid as a hosted sensor.

### Current recovery gate

No O-RW1 tuning is allowed.

Frozen O-RW1 hypothesis remains:
```
if V47 hosted base market == []
and own private shed.WOOL >= 2
and step <= 671:
    one-turn proposal = SELL WOOL 2
```

Recovery order:
1. causal gate with official `get_last_callable`;
2. only if PASS, autonomous one-shot runtime transfer with official loader;
3. only if PASS, corrected package with unique final callable
   `_kc_orw1_entrypoint` and exact official-loader parity;
4. only then consider another hosted sensor.

Active corrected causal workflow:
**`35363269856`**, head
`807dc922751120fd3bea375793f9ff3fa9ff0172`.

### Current hosted A/B evidence

Submission pair:
- CONTROL `56333577` — exact public V47;
- TREATMENT `56333579` — invalid treatment entrypoint.

First comparable rating checkpoint:
- CONTROL `714.8`;
- TREATMENT `503.9`.

Do **not** interpret this as an O-RW1 A/B result.

Replay forensics workflow `35362899791` found only 2 listed episodes per arm at the
checkpoint and only one externally-attributable game each:
- CONTROL: 1W-0L, margin +78,354 vs Cedoque BAGBONON;
- invalid TREATMENT: 0W-1L, margin -119,601 vs Kiệt Lưu.
The treatment replay was PASS-only from step 0, confirming mechanical invalidity.

No new Kaggle submission is authorized during recovery.
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
