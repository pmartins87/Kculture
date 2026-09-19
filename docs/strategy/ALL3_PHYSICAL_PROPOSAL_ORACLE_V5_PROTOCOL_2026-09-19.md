# ALL3 Physical Proposal Oracle V5 — Protocol — 2026-09-19

## Purpose

O-HV1 and O-PC1 both demonstrated the same failure mode:

- hosted replay observations expose plausible economic mechanisms;
- hand-written economic action rules built directly from those observations can still be causally
  harmful on fresh exact-engine tests.

V5 therefore changes method.

Instead of inventing another macro rule, V5 asks:

**Do strong public policies contain localized one-unit physical actions that causally improve exact
ALL3 on fresh paired games?**

V5 is an offline discovery oracle only.

## Executed organism

Base:
**exact hosted-faithful V47 + O-RW1 + O-TW1 + O-LQ2 (ALL3)**.

ALL3 market action remains exact and frozen for every proposal branch.

## Shadow proposer panel

Transient public agents already SHA-pinned in prior work:

- Ready Stock;
- Market Smart;
- V46 Microstructure;
- V48 Queue;
- router_2715;
- Conditional Memory;
- Tactical Memory;
- Best Market.

Third-party code is acquired transiently and never promoted directly.

## Proposal construction

At each live ALL3 observation:

1. execute exact ALL3 base action;
2. run every shadow proposer on the same current observation;
3. compare proposer physical actions to ALL3;
4. generate **single-unit physical hybrids only**:
   - farmer substitution: proposer farmer action + exact ALL3 hands + exact ALL3 market;
   - hand-i substitution: exact ALL3 farmer + one proposer hand-i action + all other ALL3 hands +
     exact ALL3 market;
5. deduplicate exact hybrid actions;
6. group identical hybrids by proposer sources;
7. never use proposer market actions.

This keeps every branch localized to one physical decision.

The engine determines whether a proposed physical action is feasible. No hidden feasibility oracle is
used.

## Event selection

Fresh ALL3 trajectory only.

Eligible steps:
`120..647`.

Per matchup:
- rank disagreement states by highest proposer consensus support;
- then by number of unique localized proposals;
- then earlier step;
- select at most **2** states;
- selected states must be at least **96 steps apart**.

Per selected event:
- retain at most **6** proposals;
- rank by source-support count descending, then deterministic locus/action key.

These rules are frozen before outcomes.

## Discovery population

Fresh seeds:
`75001, 75002`.

Both seats.

Opponent screen:
1. V47 mirror;
2. V48;
3. router_2715;
4. Tactical Memory.

This gives modern-family plus unrelated physical/programme coverage at manageable oracle cost.

## Branch evaluation

For each selected event/proposal:
- rerun the full episode from the beginning;
- reproduce exact ALL3 + shadow memories up to the branch step;
- execute the localized hybrid **once**;
- resume exact ALL3 immediately afterward.

Objective:
1. WIN > TIE > LOSS;
2. terminal margin only tie-breaks equal outcome class.

## Mechanical PASS

Requires:
- zero acquisition/episode failures;
- discovery replay final rewards exactly equal independent ALL3 base replay;
- every branch target reproduced exactly;
- >=12 selected branch states;
- no opponent identity/rating/EpisodeId/hidden seed/future/opponent-private deployment feature.

## Strategic classification

### V5_PHYSICAL_DIVERSE_WL_HEADROOM_PASS

Requires:
- >=2 nonwin->win branch-state flips;
- positive W/L headroom in >=2 opponent families.

### V5_PHYSICAL_WL_HEADROOM_WEAK

If:
- >=1 nonwin->win flip, or
- positive W/L headroom in exactly one family.

### V5_PHYSICAL_MARGIN_ONLY

If no W/L headroom but mean oracle margin delta >0.

### V5_PHYSICAL_NO_HEADROOM

Mechanically valid with no positive headroom.

## After PASS / WEAK

Do **not** deploy third-party actions.

Instead:
1. group winning localized substitutions by physical transform:
   - op -> op;
   - item/crop/species change;
   - actor/locus;
   - public/own-state context;
2. identify a recurring, legal-state first-party mechanism;
3. freeze that mechanism;
4. run fresh causal paired validation;
5. require broad multi-family safety;
6. only then consider option-library admission.

## After NO_HEADROOM

Close one-turn localized physical substitution as the next source.

Escalate only then to a bounded 2–3-turn physical macro oracle; do not jump directly to a new
full-game policy.

No Kaggle submission is authorized by V5.
