# ROADMAP — Kculture live plan

Updated: 2026-09-12

Objective: maximize probability of a prize-winning / top-10 Kaggriculture finish. Working source of truth is branch `fix/kaggle-parity-v1` plus `STATUS.md` and the current frozen protocol.

## Invariants

1. Hosted/live evidence and exact-reference W/L both matter.
2. Submission allowance is a cap, not a quota.
3. Every candidate family gets a predeclared gate before valid validation scores are interpreted.
4. Mechanically or semantically invalid runs are quarantined and their scores are not strategy evidence.
5. No seed, team identity, episode ID, future state or opponent-private state as an agent feature.
6. Authenticated Kaggle API is the default current-meta source.
7. Original final holdout remains sealed.

## Closed architecture classes

- CR078 late mirror breaker: closed.
- CR079 simple SpaTaro 1-NN: closed after OOT failure.
- CR080 Mengfei nearest-route/day stitching: closed after independent gate failure; post-failure diagnosis identified economic-state aliasing.

## Current frontier

Authenticated snapshot `34668645531`: Majkel 3181.9, ymg_aq 3075.1, UMG 3056.5, Artem 3029.3, SpaTaro 3029.0.

UMG remains the bridge target because it is top-tier and structurally related to a family already beating CR071M while introducing a strongly reproducible market/economic transformation.

## CR081 Gate A — COMPLETE / PASS

Deep corpus `34669006417`: UMG 110 usable episodes = 82 development + 28 newest chronological holdout.

Runtime-aligned Gate A:

- farmer median 0.90104 >= 0.80;
- hands median 0.73958 >= 0.60;
- dev-only modal market holdout fidelity 0.94959 >= 0.65.

Stable runtime prefix stays 0–287.

## Implementation quarantine history

- v1 run `34671122716`, master `9120811`: invalid replay/runtime indexing; physical route delayed one turn.
- v2 run `34671446692`, master `9120812`: invalid because inherited strategic market logic remained active inside the overlay. The defect was discovered before any v2 score was read. `dead_stock` was directly isolated as the source of 20 extra actions in UMG episode `107956535`; `_cr053_counter_market` is also strategic and could contaminate the CR053 guardrail.

Both masters are permanently burned. Their scores must never influence strategic selection.

## CURRENT — CR081 v3 fidelity confirmation

Run **`34694092039`**, master **`9120813`**.

One candidate only:

- unchanged same-step CR071M physical/runtime backbone;
- runtime 0–287 UMG development-only modal market;
- retain `room_guard` and `clamp_sells` as mechanical safety/legality repairs;
- disable `_cr053_counter_market` and `dead_stock` only inside the UMG prefix;
- resume normal CR071M strategy after step 287;
- no replay stitching or hidden/identity features.

Frozen seven-H2H panel:

1. CR081 vs CR071M
2. CR081 vs CR053
3. CR081 vs CR061
4. CR081 vs CR065
5. CR071M vs CR053
6. CR071M vs CR061
7. CR071M vs CR065

Each uses 32 fresh seeds × two seats = 64 games.

Promotion requires:

- direct >=0.5625;
- aggregate guardrail delta >=0;
- each guardrail delta >=-0.0625;
- zero errors/non-DONE;
- complete panel.

## Conditional next path

### If v3 PASS

1. freeze exact tested SHA-256;
2. refresh active Kaggle slot/submission state through authenticated API;
3. retire only the rational incumbent if necessary;
4. submit exactly one hosted CR081 probe;
5. collect hosted episodes and evaluate live W/L/rating trajectory without reacting to tiny samples.

### If v3 FAIL

Close CR081 completely. Do not create CR081A/B/C, move the 288 boundary, edit individual market quantities or retune on v3 seeds.

Advance immediately to a **state-adaptive macro-economic policy** trained on the frozen current-frontier corpora. Current evidence already indicates that top agents have highly structured but distinct economic styles: UMG is market-intensive with frequent same-queue buy/sell cycles, Majkel is even more market-active with a different opening, and ymg_aq uses another economic macro. The next representation should infer legal economic macro from current state rather than copy a single time-indexed tape.

## Escalation rule

If a valid candidate passes a frozen fresh gate with material uplift, move to one controlled hosted probe rather than endlessly adding optional local tests. If it fails, change representation rather than tuning against spent validation seeds.
