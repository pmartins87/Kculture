# O-RW1 One-Shot Runtime Transfer Gate — 2026-09-18

## Purpose

The first-party causal gate proved that a single legal ready-WOOL sale has positive W/L
value and no observed downside when inserted into exact V47 at matched states.

Now test the actual runtime form of the option, without offline branch selection.

## Base and treatment

BASE: exact current V47.

Treatment: exact V47 plus frozen first-party option **O-RW1**.

O-RW1 eligibility is unchanged:
- current V47 market list is exactly empty;
- current own private shed contains at least 2 WOOL;
- step <= 671.

Treatment action at the **first eligible state only**:

`[] -> [["SELL","WOOL",2]]`

After firing once, O-RW1 is disabled for the rest of the episode. Farmer/hands and every
other V47 action remain unchanged.

No quantity, step, product, threshold or eligibility tuning is allowed from prior results.

## Fresh evaluation panel

Exact `kaggle-environments==1.32.7`.

Fresh seeds:
`65001..65008`.

Both seats.

Opponents:
1. V47 mirror — SHA
   `f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842`
2. V48 Clear-the-Queue — SHA
   `4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96`
3. Tactical Memory — SHA
   `630125b3f592fdb773f1fac6532b08e97e829ae188180ea17540b702b606a054`
4. Ready Stock / Earlier Sales — SHA
   `45628c719dc967f81655c19f70e579c55a5758b9fe75a5fcdad9193eebf6a017`

64 paired matchups, 128 complete episodes.

## Mechanical parity

For each paired BASE/treatment matchup:
- both episodes must complete DONE/DONE;
- before the treatment trigger, candidate and BASE own observations must hash identically;
- V47 pre-transform base actions must hash identically through the trigger step;
- O-RW1 may fire at most once;
- if O-RW1 never fires, treatment and BASE final rewards must be identical.

Any violation invalidates the gate.

## Primary metric

Seat-balanced paired W/L score:
`treatment_score - base_score`.

Secondary:
- paired terminal margin delta;
- non-win -> win flips;
- win -> non-win regressions;
- trigger rate / trigger step;
- per-opponent block deltas.

## Frozen promotion gate

`READY_WOOL_RUNTIME_PASS` requires all:
- mechanical PASS;
- overall score-rate delta > 0;
- at least 4 non-win -> win flips;
- at most 1 win -> non-win regression;
- at least 3/4 opponent blocks have nonnegative score delta;
- worst opponent-block score delta >= -0.0625.

`READY_WOOL_RUNTIME_HETEROGENEOUS` if there is both positive and negative W/L evidence,
or a block regression below the safe threshold. Freeze labels and move to a selector.

`READY_WOOL_RUNTIME_MARGIN_ONLY` if W/L is neutral but mean margin delta is positive and
there is no material block regression.

`READY_WOOL_RUNTIME_FAIL` otherwise.

A PASS freezes O-RW1 as a runtime-safe first-party solver option. It authorizes building
a reproducible candidate package and a hosted-probe proposal, but **does not automatically
submit to Kaggle**.
