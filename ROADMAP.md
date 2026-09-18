# ROADMAP — Kculture live plan

## Current solver handoff — 2026-09-18

Active branch: `research/prize-solver-v0`.

### Hosted slot preservation remains binding

Kaggriculture keeps only the two newest submissions active. Do not submit a third agent
while the current pair is still maturing.

Current active pair:

CONTROL:
- submission `56336025`;
- exact public V47;
- latest authenticated rating snapshot: **2399.6**;
- current listed episodes at `2026-09-18 22:16:32 UTC`: **80**.

TREATMENT:
- submission `56336027`;
- hosted-faithful V47 + O-RW1;
- latest authenticated rating snapshot: **2536.2**;
- current listed episodes at `2026-09-18 22:16:32 UTC`: **83**.

The pair has already crossed the first informative 32/32 external-game threshold.
The normal maturity target remains **>=100 public episodes per arm plus a materially
calmer rating trajectory** before any voluntary replacement.

Historical exact V47 submission `56333577` froze at **2387.9** after 36 listed /
35 external games (29-5-1). It was retired too early; current policy prevents repeating
that mistake.

### O-RW1 hosted-faithful evidence

Causal gate `35363453097`:
- score delta +0.0833333;
- 8 positive flips;
- 0 win->nonwin regressions.

Autonomous runtime gate `35367785929`:
- 64 pairs / 128 episodes;
- `0.6250 -> 0.71875`;
- score delta **+0.09375**;
- 14 non-win -> win flips;
- 0 win -> nonwin regressions.

Corrected package parity `35372969031`:
- hosted entrypoint `_kc_orw1_entrypoint`;
- 8/8 exact action parity;
- 8/8 exact reward parity.

### O-TW1 — SECOND INDEPENDENT OPTION / RUNTIME PASS

Causal gate `35378191104`:
- 48 branch states;
- mean score delta **+0.125**;
- 14 non-win -> win flips;
- 0 win -> nonwin regressions.

Autonomous runtime gate:
**`35395548699`**, artifact `10569241095`.

Fresh panel:
- seeds `68001..68008`;
- both seats;
- V47 mirror, V48, Tactical Memory, Ready Stock;
- 64 paired matchups / 128 episodes.

Results:
- BASE score rate **0.6250**;
- O-TW1 score rate **0.71875**;
- score delta **+0.09375**;
- 14 non-win -> win flips;
- 0 win -> nonwin regressions;
- 14 positive-score pairs;
- 2 negative-score pairs;
- 48 neutral pairs;
- all 4 opponent blocks nonnegative mean W/L;
- worst block delta 0.0;
- mean margin delta +9.28125;
- median margin delta +18.

Binding verdict:
`TOWN_WHEAT_RUNTIME_PASS`.

O-TW1 is promoted into the **offline option library**, not to Kaggle.

Result:
`docs/strategy/TOWN_WHEAT_ONESHOT_RUNTIME_RESULT_2026-09-18.md`.

### Current development gate — unified option-value dataset V0

The project now has two independently proven first-party options on hosted-faithful V47:
- O-RW1: ready-WOOL sale;
- O-TW1: town-WHEAT pulse hold.

Next architecture:
```
legal current state + eligible option
        -> counterfactual ΔW/L label
        -> value dataset
        -> state-conditioned selector/value model
        -> later bounded search
```

Frozen pilot:
`docs/strategy/OPTION_VALUE_DATASET_V0_PILOT_2026-09-18.md`.

Implementation:
`tools/option_value_dataset_v0_pilot.py`.

Active workflow:
**`35401011776`**, head
`3e60477caa17d42675529a8e04be5bd91ac91165`.

Pilot uses fresh seeds `69001,69002`, both seats, V47/V48/Tactical Memory, and requires:
- exact hosted V47 entrypoint;
- discovery/base reward parity;
- legal feature contract only;
- no seed/opponent/rating/hidden/future metadata inside model features;
- at least 8 labeled rows and >=2 rows/option.

A PASS validates the data pipeline only. Only after PASS should a resumable Ryzen-scale
multiprocessing label generator be built and run.

No Kaggle submission is authorized.
No Ryzen action is required yet.

The FP001_STATUS/FP001_ROADMAP files are absent on this branch; do not create competing
copies.

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
