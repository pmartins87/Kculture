# CR083 Phase 2 — route-aware future-seed-demand clamp protocol

Status: **frozen before candidate construction or evaluation**.

This is the first executable CR083 mechanism after Phase-1 proved that broad deletion of any market family is catastrophic. It is intentionally narrow and mechanics-derived.

## Hypothesis

After CR071M's final route-switch checkpoint has passed, purchasing crop seeds beyond the maximum number of future `PLANT` commands the already-selected own route can execute is weakly dominated.

Seeds:

- are private and do not alter public market inventory/prices;
- do not occupy shed capacity;
- cannot be sold or liquidated at episode end;
- create value only by being consumed by a future `PLANT` action.

Therefore excess seeds above remaining route plant demand can only reduce money.

## Frozen intervention

Base package: exact CR071M SHA-256
`dbc6fc2b2c3673b1d9fc36e103b8369a53c7f2cc33381e11a3cb5f769bebe652`.

Preserve all CR071M route logic, farmer/hands, public route switching, weed repair, room guard, CR053 counter-market, sell clamping, dead-stock logic and every non-seed market order.

The clamp activates only **after the last possible CR071M route switch has been resolved**. The known checkpoints are at runtime steps 226, 360 and 433, so the clamp is active for `step >= 434` only.

For each `BUY_SEED crop qty` in the final market queue:

1. compute `future_plant_demand(crop, step+1)` from the already-selected own route, counting all future `PLANT crop` unit commands after the current turn;
2. project current seed stock after this turn's own physical `PLANT` requests:
   - because physical actions execute before market, a same-turn seed purchase cannot fund a same-turn plant;
   - if current same-turn PLANT demand for the crop is <= current private seed stock, subtract that demand;
   - if it exceeds stock, Kaggriculture atomic PLANT validation blocks all same-crop PLANT requests, so subtract zero;
3. account for any earlier accepted `BUY_SEED` orders for the same crop in the same market queue;
4. define `needed = max(0, future_plant_demand - projected_future_seed_stock)`;
5. keep `min(original_qty, needed)`; drop the order if the kept quantity is zero.

No seed quantity may ever be increased. No crop type, timing, route, physical action or other market order may be changed.

This is a deterministic mechanics invariant, not a learned model and not a teacher-action imitation.

## Mandatory source/mechanical self-audit

Before any score is read, candidate construction must prove:

- exact base SHA matches frozen CR071M;
- farmer/hands generation is untouched;
- route-switch code is untouched;
- clamp activation is `step >= 434` exactly;
- the patch only modifies final `BUY_SEED` quantities/removes zero-needed seed orders;
- all non-`BUY_SEED` market orders are identical for the same observation;
- kept seed quantity is never greater than baseline;
- for audited baseline observations, the clamp never leaves projected seeds below the selected route's maximum remaining PLANT demand solely because of the clamp.

Package build must be deterministic and hash-frozen.

## Gate A — fresh direct falsification

Gate A uses exact runtime `kaggle-environments==1.32.7`, isolated packages, both seats.

Reserved Gate-A master: **9130831**.

Use 16 fresh seeds × both seats = **32 games**: CR083 Phase-2 candidate vs exact CR071M.

Seed firewall must exclude all documented earlier masters including CR082 `9120821` and Phase-1 exploratory `9130830`.

Gate A PASS requires all:

1. exactly 32 games / 16 fresh seeds;
2. zero execution errors and zero non-DONE games;
3. seat-balanced score rate vs CR071M >= **0.5625**;
4. mean final-money margin > 0;
5. candidate package/self-audit hash is unchanged from pre-score freeze.

If Gate A fails: close this seed-demand-clamp mechanism. Do not move step 434, alter the demand formula or tune crop-specific exceptions on master `9130831`.

## Conditional promotion panel

Only if Gate A passes, the **same exact candidate SHA** advances without modification to a second fresh master **9130832**.

Panel, each 32 seeds × both seats = 64 games:

1. CR083 vs CR071M;
2. CR083 vs CR053;
3. CR083 vs CR061;
4. CR083 vs CR065;
5. CR071M vs CR053;
6. CR071M vs CR061;
7. CR071M vs CR065.

Promotion PASS requires:

- complete panel;
- exactly 64 games / 32 fresh seeds per row;
- zero errors/non-DONE;
- direct CR083 vs CR071M score rate >= **0.5625**;
- aggregate guardrail delta >= 0;
- every individual guardrail delta >= **-0.0625**.

PASS freezes the hash and authorizes authenticated hosted slot refresh followed by exactly one controlled hosted probe if capacity permits. FAIL closes this mechanism without retuning on `9130832`.

Original final holdout remains sealed. No automatic hosted submission is part of these workflows.