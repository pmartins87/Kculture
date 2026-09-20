# ALL3 V7 Option Composition Attribution — Protocol — 2026-09-19

## Purpose

V6 closed bounded one-locus H2/H3 physical continuation as a W/L source.

The next question is first-party and causal:

**Are the four residual ALL3 losses caused or aggravated by one of the three existing first-party
options (O-RW1, O-TW1, O-LQ2), and does suppressing an option recover W/L?**

No new heuristic is introduced in V7.

## Frozen hard contexts

Use exactly the four V6A frozen contexts from:
`configs/all3_v6_hard_contexts.json`.

1. V47 mirror — seed 75113, seat 1, ALL3 margin -263;
2. V48 — seed 75103, seat 1, ALL3 margin -86;
3. V48 — seed 75110, seat 0, ALL3 margin -484;
4. V48 — seed 75113, seat 1, ALL3 margin -794.

No close-win context may be added.

## Exact base

Hosted-faithful V47.

## Frozen compositions

Evaluate exactly these 8 static compositions:

1. `V47` — RW=0, TW=0, LQ2=0;
2. `RW` — 1,0,0;
3. `TW` — 0,1,0;
4. `LQ2` — 0,0,1;
5. `RW_TW` — 1,1,0;
6. `RW_LQ2` — 1,0,1;
7. `TW_LQ2` — 0,1,1;
8. `ALL3` — 1,1,1.

Each composition is static for the whole episode.

The exact frozen one-shot semantics of RW1/TW1 and the exact current LQ2 implementation must be
used through `apply_option_host(..., use_rw=..., use_tw=..., use_lq2=...)`.

## Mechanical requirements

For every hard context and composition:
- exact SHA-pinned base/opponent acquisition;
- engine `kaggle-environments==1.32.7`;
- 720-step completed episode;
- no third-party proposer;
- no opponent identity inside candidate runtime logic;
- exact V47 physical farmer/hands unchanged by option host;
- ALL3 replay must reproduce the frozen hard-context margin exactly.

Zero failures required.

## Primary analysis

Per hard context:
- terminal W/T/L;
- terminal margin;
- winning composition(s);
- best composition by W/T/L then margin.

Across contexts:
- W/T/L for each static composition;
- mean margin for each composition;
- leave-one-out comparison against ALL3:
  - no RW = TW_LQ2;
  - no TW = RW_LQ2;
  - no LQ2 = RW_TW.

## Strategic classification

### V7_STATIC_COMPOSITION_HEADROOM_REPEATABLE
A single static composition other than ALL3:
- converts >=2 frozen ALL3 losses into wins.

Next:
run a fresh broad paired regression gate for that exact static composition vs ALL3.

### V7_STATIC_COMPOSITION_HEADROOM_NARROW
At least one non-ALL3 composition:
- converts >=1 frozen ALL3 loss into a win,
but no single composition rescues >=2.

Next:
inspect option firing/state traces in rescued vs non-rescued contexts and derive a legal-state
suppression hypothesis before fresh validation.

### V7_STATIC_COMPOSITION_MARGIN_ONLY
- zero loss->win flips;
- at least one non-ALL3 composition improves aggregate margin vs ALL3.

### V7_STATIC_COMPOSITION_NO_HEADROOM
- no W/L rescue;
- no aggregate margin improvement vs ALL3.

## Interpretation constraints

This is residual-loss discovery, not deployment validation.

Even a repeatable hard-context rescue does not authorize:
- opponent-identity routing;
- a Kaggle submission;
- a learned selector trained only on these four contexts.

A candidate must next pass fresh paired evidence and broad unrelated-family regression checks.

No Kaggle submission is authorized by V7.
