# ROADMAP — Kculture live plan

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

## North star

Reach prize/top-10 class and maximize probability of 1st place. Frozen external target: ~`2958+` top 10 and ~`3000+` frontier class.

Optimize **competitive W/L/population value**, not novelty, terminal money or local single-panel rating.

## Binding methodological rules

1. Preserve successful historical knowledge unless stronger evidence supersedes it.
2. Economic/mechanics module validity does not imply competitive-backbone validity.
3. Exact-engine tests govern mechanics and causal interventions; local H2H ordering is not a hosted-rating oracle.
4. No post-result threshold ladder for failed architectures without new causal evidence.
5. Use exact hosted/frozen packages whenever possible.
6. No identity/rating/EpisodeId/hidden seed/future/direct opponent-private runtime features.
7. Original final holdout remains sealed.
8. Hosted slots answer high-information transfer questions only.
9. Execution/mechanics failures cannot be interpreted as strategic failures.
10. Router labels must be counterfactual W/L labels or a defensible competitive surrogate, never terminal money alone.

## Completed foundation

Competitive: CR053_REAL remains the strongest exact hosted anchor (~2064.8); CR086 estimator/operator retained; CR087/088 elite macro/replay knowledge retained while direct tape backbones stay closed.

FP001: retain H1, H1B, H8/B3+CARE, H9 representation, H10, H11 and M6S1 as reusable primitives/modules.

Closed integration failures: CR089 static C5/C5+M6S1; CR090 simple H9 species selector.

## R6 — hierarchical competitive controller

Target architecture:

`legal runtime state -> option value -> best separable market/macro option`

Use hosted-proven CR053 as the initial host organism instead of repeatedly replacing the whole agent.

## CR091 — Gate 1 COMPLETE / PASS

Binding run `34990757344`, result `CR091_LATENT_OPTION_TRANSFER_PASS_ADVANCE_ROUTER`.

Exact CR053 plus the exact CR086 latent-supply market-priority operator passed mechanics and population transfer on the four-anchor panel:

- failures 0;
- violations 0;
- exact physical and market-multiset parity;
- 1,075 O1 reorders;
- edge deltas: CR052 `0`, CR053 `+0.1875`, CR083 `0`, CR086 `0`;
- mean edge delta `+0.046875`, worst regression `0`.

Freeze this CR086 priority mechanism as option **O1**. Do not retune it.

Result doc: `docs/strategy/CR091_HIERARCHICAL_MARKET_OPTION_RESULT_2026-09-15.md`.

## CR092 — broad O1 transfer + router-label gate CURRENT

Protocol: `docs/strategy/CR092_BROAD_OPTION_ROUTER_LABEL_PROTOCOL_2026-09-15.md`.

### Question

Does frozen O1 survive the broader 11-edge heterogeneous population, and does its value vary enough across hash-matched public states to justify a learned router?

### Frozen population / execution

Use the exact CR089 frozen population artifact `10378299284`:

- anchors: CR053_REAL, CR052_REAL, CR083, CR086;
- seven macro reps: Majkel/r01, SpaTaro/r02, ymg-Howard/r03, Orbital/r06, feel/r07, Otter/r09, redblack/r10.

Evaluation:

- seeds `91401..91406`;
- both seats;
- BASE and frozen O1;
- 12 games/treatment/edge;
- 264 total episodes;
- 11 edge jobs in parallel;
- hosted-faithful `kaggle-environments==1.32.7` execution.

### Counterfactual dataset

At O1's first actual market reorder, freeze the legal strategic observation and CR086 derived state. The label is admissible only if BASE has the exact same strategic-state hash at the same step for the same opponent/seed/seat.

Primary label: `W/L(O1) - W/L(BASE)`.

Opponent name and seed are offline stratification metadata only; never runtime router features.

### Frozen broad-survival rule

Require all:

- mechanics pass;
- mean edge delta >= `+0.02`;
- >=8/11 nonnegative edges;
- worst regression >= `-0.125`;
- seven-macro mean delta >= `0`;
- no BASE edge >=0.25 becomes O1 score 0.

### Frozen routing signal

Require all:

- branch-state hash-valid labels only;
- >=8 positive labels;
- >=8 negative labels;
- positives from >=2 opponent strata;
- negatives from >=2 opponent strata.

### Frozen outcomes

1. `CR092_BROAD_PASS_HETEROGENEOUS_ADVANCE_ROUTER`  
   Freeze dataset and advance CR093 router(BASE/O1).

2. `CR092_BROAD_PASS_O1_ADVANCE_NEXT_OPTION`  
   O1 is broadly safe but lacks sufficient downside heterogeneity; retain it and add next separable option, initially H1/H1B timing.

3. `CR092_BROAD_FAIL_HETEROGENEOUS_ADVANCE_ROUTER_DISCOVERY`  
   Always-on O1 unsafe, but enough positive/negative causal value exists to justify conditional routing.

4. `CR092_BROAD_FAIL_CLOSE_ALWAYS_ON_O1`  
   Close always-on O1 without tuning; move to H1/H1B option family.

Mechanics failure means no strategic verdict.

### Active implementation

Research branch:

- `tools/cr092_broad_option_edge.py`
- `tools/cr092_aggregate.py`
- `.github/workflows/cr092-broad-option-router-label.yml`
- head commit `b42347617a6967eeb2862fde23737c7538d3b9d3`
- active workflow **`35015135956`**
- prepare job PASS; all 11 frozen packages SHA-verified; edge matrix launched.

## CR093 — public-state router CONDITIONAL

Only if CR092 exposes heterogeneous causal support.

Requirements:

- small auditable feature set frozen before final validation;
- no opponent identity or hidden metadata;
- train only on CR092 admissible hash-matched labels;
- fresh seeds/opponent instances for evaluation;
- controls: always BASE, always O1, router(BASE/O1);
- feature ablations;
- no catastrophe edge.

If CR092 shows O1 is broadly beneficial without meaningful negative support, skip an unnecessary binary router and first add H1/H1B as O2 so routing has a real choice.

## Later separable options

Evaluate one at a time after the current gate:

- H1 town-pulse WHEAT carry;
- H1B owned-sale deferral;
- elite/CR088 market timing/competition handling;
- H11 fertilizer opportunity-cost actions where separable;
- state-compatible production macro options using CR087/088 priors and FP001 modules.

Never reintroduce raw tape splicing without complete state preconditions.

## Hosted calibration

Hosted-worthy only after exact mechanics, fresh broad W/L survival, no major catastrophe edge and a strategically distinct transfer question. CR092 itself does not automatically authorize submission.

## Permanent stop list absent new evidence

CR080 replay stitching; CR081 static market-prefix transplant; CR082 1-NN imitation; CR084 FEED rescue; CR085 Pareto gating; direct CR088 tape backbones; static C5/C5+M6S1; fixed C3S2/C2S3; CR090 simple first-shop species rule.

## Immediate action

Let CR092 workflow `35015135956` complete. On the next status check, read its aggregate result once and obey the frozen branch. No manual Kaggle submission.
