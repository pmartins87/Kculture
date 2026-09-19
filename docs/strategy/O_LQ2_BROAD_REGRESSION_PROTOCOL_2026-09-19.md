# O-LQ2 Broad Fresh Regression Protocol — 2026-09-19

## Entry evidence

Fresh causal V48 gate:
- workflow `35456018489`;
- decision **O_LQ2_V48_CAUSAL_PASS**;
- 16/16 BASE losses became treatment wins;
- score rate **0.0 -> 1.0**;
- mean score delta **+1.0**;
- mean margin delta **+567.0**;
- 0 negative-score contexts.

This authorizes broad regression only. It does not authorize hosted submission.

## Frozen league

Seven previously audited public families:

1. `v47_mirror` — modern41_v47
2. `ready_stock` — modern41_ready_stock
3. `v48` — modern41_queue
4. `router_2715` — multi_program_router
5. `conditional_memory` — literal_conditional_memory
6. `tactical_memory` — literal_tactical_memory
7. `best_market` — literal_market_strategy

Fresh seeds:
`74501..74504`, both seats.

Per opponent block:
4 seeds × 2 seats = **8 paired contexts**.

Total:
**56 paired contexts**, each with exact V47 BASE and exact V47 + O-LQ2.

## Mechanical requirements

- all 7 opponent shards complete;
- 56/56 paired contexts;
- DONE statuses;
- pre-trigger parity PASS;
- O-LQ2 never changes farmer/hands;
- pinned public-agent SHA identities.

## Frozen strategic classification

### O_LQ2_BROAD_SAFE_PASS

Requires all:
- V48 block mean score delta >= **+0.50**;
- overall mean score delta > 0;
- **0 negative-score contexts** across the league;
- every opponent block mean score delta >= 0;
- positive overall mean margin delta.

Interpretation:
O-LQ2 is safe enough to proceed toward runtime/package parity and composition testing.

### O_LQ2_BROAD_ROUTER_REQUIRED

Requires:
- V48 block mean score delta > 0;
- overall mean score delta > 0;
- but one or more negative contexts/blocks exist.

Interpretation:
the mechanism is real and may enter the option library as a conditional option, but must not be
enabled globally. Open legal-state value/router work.

### O_LQ2_BROAD_FAIL

If V48 benefit does not replicate or overall mean score delta <= 0.

## After SAFE PASS

1. package/runtime parity;
2. composition with O-RW1 + O-TW1;
3. fresh broad composition regression;
4. only then hosted consideration.

## After ROUTER REQUIRED

Return to value-learning/router only now, because O-LQ2 supplies the diverse W/L support previously
missing from the option library.

No Kaggle submission is authorized by this protocol.
