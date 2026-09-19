# ALL3 V6 Bounded Physical Continuation Oracle — Protocol — 2026-09-19

## Prerequisite

Run only after V6A produces `V6A_HARD_CONTEXTS_READY`.

The exact list of V6 hard contexts must be frozen from the V6A artifact before any V6 branch
outcome is observed.

If V6A returns `V6A_EXPAND_HARD_CENSUS`, V6 remains dormant.

## Motivation

V5 proved:
- one-turn localized physical substitutions can improve margin in already-won games;
- they produced **zero W/L flips**;
- the only V5 loss, V48 seed 75002 seat 0 (-26), was unchanged by every one-turn branch.

The next bounded escalation is therefore a short continuation rather than a full-policy swap.

## Executed organism

Exact ALL3:
- hosted-faithful V47;
- O-RW1;
- O-TW1;
- O-LQ2.

At every V6 branch turn:
- exact ALL3 market action is preserved;
- exact ALL3 physical actions for every non-selected actor are preserved.

## Shadow proposer panel

Same transient SHA-pinned proposer panel as V5:
- Ready Stock;
- Market Smart;
- V46 Microstructure;
- V48 Queue;
- router_2715;
- Conditional Memory;
- Tactical Memory;
- Best Market.

Third-party code is offline discovery-only.

## Mechanical amendment — hired-hand day boundary

Added before any V6 result is allowed to bind.

Official Kaggriculture mechanics remove all hired hands at the end of each day. Therefore a
continuation on a `hand:i` locus cannot represent the same actor across a day boundary.

Deterministic eligibility rule:
- farmer continuations may cross a day boundary;
- a `hand:i` H2/H3 candidate is eligible only if
  `floor(target_step / turnsPerDay) == floor((target_step + horizon - 1) / turnsPerDay)`;
- an ineligible hand/day-boundary candidate is skipped **before rollout** and is not counted as an
  episode/mechanical failure.

This amendment does not use outcomes and does not alter:
- frozen hard contexts;
- event ranking;
- proposer ranking;
- source/locus identity;
- H2/H3 horizons;
- strategic gate.

Run `35473389439` is non-binding because the initial harness treated these lifecycle-ineligible
candidates as continuation-length failures.

## Candidate continuation

A candidate is:
`(target_step, source, locus, horizon)`.

Where:
- locus is either `farmer` or one exact `hand:i`;
- horizon is **2 or 3 consecutive turns**.

At target step:
- source and ALL3 must disagree at that locus;
- the selected source/locus action must be validly constructible as a one-locus hybrid.

For each branch turn in
`target_step .. target_step + horizon - 1`:
1. compute exact ALL3 on the branched observation;
2. compute the selected source on the same branched observation;
3. substitute only the selected locus with the source's current physical action;
4. preserve exact ALL3 market;
5. preserve every other ALL3 physical locus.

After the horizon, exact ALL3 resumes completely.

If the selected locus no longer exists in the source output during the continuation, the branch is a
mechanical failure and cannot contribute strategic evidence.

## Event discovery within each frozen hard context

Replay the exact hard context with ALL3 plus all shadow proposers.

Eligible disagreement steps:
`120..600`.

Rank states by:
1. highest proposer support for an identical localized action;
2. number of distinct localized proposals;
3. earlier step.

Select at most **2** event states, separated by at least **120 steps**.

At each selected event:
- rank localized source/locus proposals by first-action consensus support;
- preserve source identity for continuation, even when several sources share the same first action;
- retain at most **4** source/locus candidates.

For each candidate evaluate horizons:
- H2;
- H3.

Maximum:
16 branch episodes per frozen hard context.

## Objective

Competition objective:
1. WIN > TIE > LOSS;
2. terminal margin only breaks ties inside the same outcome class.

Primary discovery metric:
**nonwin -> win flip** relative to exact ALL3 in the same hard context.

## Mechanical PASS

Requires:
- exact base replay reproduces the V6A frozen result;
- discovery shadow replay has exact final parity with base;
- every evaluated target step is reproduced;
- exact ALL3 market is preserved on every continuation turn;
- only one physical locus differs per branch turn;
- zero acquisition/episode failures.

## Strategic classification

### V6_CONTINUATION_HEADROOM_PASS
- >=2 distinct frozen hard contexts become wins;
- winning contexts span >=2 opponent families.

### V6_CONTINUATION_HEADROOM_NARROW
- >=1 frozen hard context becomes a win.

### V6_CONTINUATION_MARGIN_ONLY
- zero W/L flips but positive mean oracle margin delta across hard contexts.

### V6_CONTINUATION_NO_HEADROOM
- no W/L flips and no positive aggregate margin headroom.

## After PASS / NARROW

Do not deploy third-party continuation.

Instead:
1. inspect winning continuations turn-by-turn;
2. identify recurring first-party state/action mechanism;
3. freeze a minimal legal-state option;
4. fresh paired causal validation;
5. broad seven-family regression gate;
6. hosted submission only if those gates pass.

## After MARGIN_ONLY / NO_HEADROOM

Close bounded one-locus 2–3-turn continuation as a W/L source.

The next escalation must be reconsidered from the hard-context evidence rather than automatically
increasing horizon.

No Kaggle submission is authorized by V6.
