# STATUS — Kculture live source of truth

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
