# ROADMAP — Kculture live plan

## Current solver handoff — 2026-09-18

Active branch: `research/prize-solver-v0`.

The active Prize-Solver line is frozen first-party option **O-RW1** on exact public V47.

### Offline / exact-engine evidence

1. Wrapper-proposal oracle V2b — PASS:
   - BASE `0.500` -> oracle `0.625`;
   - W/L delta **+0.125**;
   - useful proposal was V47 market empty -> `SELL WOOL 2`.

2. First-party causal O-RW1 — PASS SAFE OPTION:
   - 48 branch states;
   - mean score delta **+0.1666667**;
   - 16 non-win -> win flips;
   - 0 negative-W/L states.

3. Autonomous one-shot runtime transfer — PASS:
   - 64 paired matchups / 128 episodes;
   - BASE `0.5000`;
   - V47 + O-RW1 `0.6875`;
   - W/L delta **+0.1875**;
   - 28 non-win -> win flips;
   - 0 win -> non-win regressions;
   - all 4 opponent blocks nonnegative in W/L.

Frozen O-RW1:
```
if not used
and V47 current market == []
and own private shed.WOOL >= 2
and step <= 671:
    execute SELL WOOL 2
    used = True
```

### Hosted package — PASS

Workflow `35360173417`, artifact `10554278438`.

Candidate:
`KCULTURE_V47_ORW1_ONESHOT_V1.tar.gz`

Archive SHA-256:
`b994e00d7adba05827eb8839b806211c2c8199dd0ad09a28b63815b58479c80f`

Candidate `main.py` SHA:
`f65be27b47839eb0cb6b44b217fc1edb33f63796bf5bc0bdd4f0bd311d3c2ff4`

Exact V47 base main SHA:
`f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842`

Fresh package smoke:
- 8 package/reference pairs;
- 16 complete episodes;
- exact action parity 8/8;
- exact reward parity 8/8;
- 0 failures.

The packaged source retains the upstream Apache-2.0 license text, SPDX notice and V47
attribution/modification notice.

Binding package result:
`docs/strategy/ORW1_HOSTED_PACKAGE_RESULT_2026-09-18.md`.
Machine-readable:
`data/programme_teacher/2026-09-18/ORW1_HOSTED_PACKAGE_SUMMARY.json`.

### Current next step — explicit authorization required

Frozen hosted sensor:
`docs/strategy/ORW1_HOSTED_AB_PROBE_PROTOCOL_2026-09-18.md`.

Submit in the same operational window:
- CONTROL: exact public V47 output archive, SHA
  `08e56c43ecf28253605b61066dd769334d96262056b8cd337489f1f4f909ad01`;
- TREATMENT: exact frozen O-RW1 archive, SHA
  `b994e00d7adba05827eb8839b806211c2c8199dd0ad09a28b63815b58479c80f`.

No other variant between the pair. Hosted result is a population sensor; do not retune
O-RW1 from one noisy rating.

**No Kaggle submission has been sent. Await explicit user authorization for the A/B
hosted probe.**

No Ryzen action is required.

The FP001_STATUS/FP001_ROADMAP files are absent on this branch; do not silently create
competing copies or change other branches as part of this solver update.

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
