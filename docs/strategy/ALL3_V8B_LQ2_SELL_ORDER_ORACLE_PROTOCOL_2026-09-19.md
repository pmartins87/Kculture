# ALL3 V8B LQ2 SELL-Order Pairwise Transposition Oracle — Protocol — 2026-09-19

## Prerequisite

V8A binding result:
- workflow `35479557496`;
- decision **`V8A_ORDER_SEARCH_READY`**;
- 170 eligible post-LQ2 multi-product SELL-run states;
- all 4 frozen hard contexts represented.

## Frozen state selection

Per frozen hard context:

1. rank V8A eligible states by:
   - more distinct products;
   - more non-empty SELL orders;
   - larger total SELL quantity;
   - earlier step;

2. choose the first state;

3. choose at most one additional state whose step differs by at least 48 turns from every already
   selected state.

Maximum:
- 2 states per hard context;
- 8 states total.

The selected state set is frozen before any V8B branch result is observed.

## Intervention family

For each frozen state:

- reproduce exact ALL3;
- require exact post-LQ2 market equality at the frozen target step;
- identify the frozen contiguous SELL run;
- for every unordered pair of SELL positions `i < j` inside that run:
  - swap the two complete SELL orders;
  - preserve every product quantity exactly;
  - preserve every market slot outside the run exactly;
  - preserve farmer and hands exactly;
  - change only that target turn;
  - exact ALL3 resumes immediately next turn.

No new order is invented:
V8B only tests pairwise transpositions of existing LQ2-emitted orders.

For a run of n products, branches = n(n-1)/2.

## Frozen selected states

The exact selected states are stored in:
`configs/all3_v8b_lq2_order_states.json`.

Expected selection:
- context 0: steps 673 and 577;
- context 1: steps 673 and 600;
- context 2: steps 673 and 600;
- context 3: steps 673 and 577.

## Objective

Primary:
- loss -> win.

Secondary:
- terminal margin only within the same W/T/L class.

Per hard context:
- best branch over all selected states and transpositions.

## Mechanical PASS

Requires:
- exact ALL3 base replay equals the frozen V6 hard-context result;
- exact target post-LQ2 market equals V8A frozen state;
- only two SELL slots exchange position;
- multiset of market orders is unchanged;
- farmer/hands unchanged;
- zero episode/acquisition failures.

## Strategic classification

### V8B_ORDER_HEADROOM_REPEATABLE
- >=2 distinct frozen hard contexts become wins under at least one pairwise transposition.

Next:
inspect winning product-pair direction and legal public state; derive a first-party product-priority
rule and validate on fresh seeds.

### V8B_ORDER_HEADROOM_NARROW
- exactly 1 frozen hard context becomes a win.

Next:
inspect winning pair and run fresh targeted confirmation before generalizing.

### V8B_ORDER_MARGIN_ONLY
- zero W/L flips;
- positive mean best-branch margin delta across hard contexts.

### V8B_ORDER_NO_HEADROOM
- zero W/L flips;
- no positive aggregate margin headroom.

## Constraints

- no opponent identity in deployable runtime logic;
- no third-party code;
- no automatic Kaggle submission;
- no threshold or state reselection after branch outcomes.
