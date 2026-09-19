# O-PC1 Profit-Dominant Crop Rotation — Development Protocol — 2026-09-19

## Motivation

ALL3 hosted first-informative losses show a physical/macro divergence not explained by O-HV1.

Concrete example against Timothy Adeyemi:
- at the divergence, public CARROT price = 59;
- public WHEAT price = 37;
- opponent had accumulated CARROT seeds and began replacing WHEAT planting with CARROT;
- ALL3 continued the scheduled WHEAT programme;
- by step 600 opponent had ~34 CARROT plants versus ALL3's 4.

Official engine mechanics (pinned Kaggriculture):
- WHEAT seed cost = 10, max yield = 6, max-yield day = 4;
- CARROT seed cost = 20, max yield = 4, max-yield day = 3;
- unit actions/PLANT execute before market orders;
- PLANT requests are atomically blocked when current private seed inventory is insufficient.

Therefore same-turn seed purchase cannot fund same-turn planting.

## First-party economic signal

Use current public market prices only.

Define full-cycle nominal crop value:
- `V_wheat = 6 * P_wheat - 10`;
- `V_carrot = 4 * P_carrot - 20`.

CARROT regime iff:

`V_carrot > V_wheat`.

This is not a fitted threshold. It follows directly from official seed costs and maximum non-ongoing
yield.

A planting must also have enough season remaining to reach CARROT max-yield age:
- `current_day + 3 <= final_day`.

## O-PC1 controller

Start from exact ALL3.

When CARROT regime is active and maturity is feasible:

### Seed acquisition
For every exact ALL3 `BUY_SEED WHEAT n` order:
- if n >= 2: rewrite it as `BUY_SEED WHEAT (n-1)` plus `BUY_SEED CARROT 1`;
- if n == 1: rewrite it as `BUY_SEED CARROT 1`.

Do not add more total seed units than ALL3 requested.
Do not exceed max market orders.

This changes crop composition without creating an unbounded extra-spend channel.

### Plant substitution
From current own private seed inventory only:
- count exact ALL3 `PLANT CARROT` requests;
- reserve those seeds first;
- let `carrot_surplus = current_carrot_seeds - reserved_carrot_plants`;
- replace up to `carrot_surplus` exact `PLANT WHEAT` actions with `PLANT CARROT`;
- preserve unit order and every non-PLANT physical action.

Because physical actions execute before market, current-turn rewritten seed purchases are never
counted as available for current-turn PLANT.

### Non-CARROT regime
Return exact ALL3 unchanged.
Previously accumulated CARROT seeds remain available for later native ALL3 carrot phase.

## Runtime legality

Inputs:
- current own observation/private seeds;
- current public market prices;
- current config;
- exact current ALL3 action.

Forbidden:
- opponent identity/rating;
- EpisodeId;
- hidden seed;
- future state;
- opponent-private state;
- replay labels.

Hosted names/replays were used only for offline mechanism discovery.

## Frozen development gate

Opponents:
- exact V47 mirror;
- exact V48;
- Ready Stock.

Fresh seeds:
`74901..74904`, both seats.

24 paired ALL3 vs ALL3+O-PC1 contexts.

Mechanical PASS:
- 24/24 paired contexts;
- all DONE;
- pre-trigger exact ALL3 parity;
- no invalid physical/market action;
- no hidden/future/private-opponent runtime input.

### Development PASS

Requires all:
- mean score delta > 0;
- zero negative-score contexts;
- positive mean margin delta;
- >=4 firing contexts.

### Development SAFE-MARGIN

If:
- mean score delta == 0;
- zero negative-score contexts;
- positive mean margin delta;
- >=4 firing contexts.

SAFE-MARGIN may proceed only to fresh seven-family validation; it is not an option-library PASS.

Otherwise:
**O_PC1_DEV_CLOSE**.

No ratio/start-step/yield threshold retuning is allowed after the development result.

## After development PASS or SAFE-MARGIN

Freeze O-PC1 exactly.

Run untouched fresh seeds across the seven-family V2 league.

Broad PASS requires:
- overall mean score delta > 0;
- zero negative-score contexts;
- every opponent block mean score delta >= 0;
- positive overall mean margin delta.

If only SAFE-MARGIN persists, close as non-W/L option source.

No Kaggle submission is authorized by this protocol.
