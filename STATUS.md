# STATUS — Kculture live source of truth

Updated: 2026-09-12

Authoritative branch: `fix/kaggle-parity-v1`.

## Mission

Maximize probability of a prize-winning / top-10 Kaggriculture finish before 2026-09-30 23:59 UTC. No hosted submission without a passed frozen gate.

## Hosted incumbents

- CR071M — submission `56124705`; last authenticated checkpoint rating 1731.8. Incumbent/calibration reference only.
- CR070A — submission `56091951`; last authenticated checkpoint rating 1724.0.

## Closed / quarantined

- CR078: closed.
- CR079 SpaTaro 1-NN clone: closed / FAIL.
- CR080 Mengfei route stitching: closed / FAIL. Post-failure diagnostic showed economic-state aliasing, so nearest-route/day replay stitching is closed.
- CR081 v1 — run `34671122716`, seed master `9120811`: **INVALID**. Replay-storage offset was misread and the CR071M physical backbone was delayed one runtime turn.
- CR081 v2 — run `34671446692`, seed master `9120812`: **INVALID**. Correct replay/runtime offset, but inherited strategic market transforms remained active inside the frozen UMG prefix. This was discovered before any v2 score was read. Pre-score audit on UMG episode `107956535` isolated 20 extra market actions at runtime steps 267–287 to `dead_stock`; `_cr053_counter_market` was also identified as an inherited strategic transform that could fire in the CR053 guardrail. No v1/v2 score may be used as strategy evidence.

## Current frontier snapshot

Authenticated run `34668645531`:

1. Majkel1337 3181.9 (`56156662`)
2. ymg_aq 3075.1 (`56161578`)
3. Unknown Mother-Goose 3056.5 (`56169353`)
4. Artem The Farmer 3029.3
5. SpaTaro 3029.0

## CR081 Gate A — PASS

Deep corpus run `34669006417`: 111 UMG episodes downloaded; one UMG-vs-UMG replay excluded as seat-ambiguous; **110 usable = 82 development + 28 newest holdout**.

Runtime-aligned newest-28 results:

- farmer median similarity to frozen bridge family: **0.90104** (gate >=0.80);
- hands median similarity: **0.73958** (gate >=0.60);
- development-only modal market -> holdout exact fidelity: **0.94959** (gate >=0.65).

Kaggle replay action index `s+1` maps to runtime step `s`. The frozen market prefix remains runtime steps **0–287**, with development support ~0.970 / 0.942 / 0.914 across the first three 96-step blocks and ~0.683 in the next block.

## ACTIVE — CR081 v3 fidelity confirmation

Workflow run: **`34694092039`**.
Fresh master seed: **`9120813`**, firewalled against prior CR080 masters and burned CR081 masters `9120811`/`9120812`.

Exact candidate architecture:

- same-step CR071M physical/runtime backbone unchanged;
- runtime steps 0–287 use the UMG development-only modal market learned from replay indices 1–288;
- `room_guard` retained inside prefix as shed-capacity safety repair;
- `clamp_sells` retained as legality/order-slot protection, including same-turn BUY_PRODUCT -> later SELL accounting;
- `_cr053_counter_market` disabled inside prefix because it is strategy, not safety;
- `dead_stock` disabled inside prefix because it is strategy, not safety;
- both inherited strategies resume after step 287 with normal CR071M behavior;
- no replay stitching, team identity, episode ID, seed, future state or opponent-private feature.

Frozen v3 promotion panel: CR081 vs CR071M/CR053/CR061/CR065 plus same-seed CR071M guardrail controls; 32 fresh seeds x two seats = 64 games/H2H.

Promotion requires all:

- direct CR081 vs CR071M >= **0.5625**;
- aggregate guardrail delta >= 0;
- every individual guardrail delta >= **-0.0625**;
- complete panel, zero errors and zero non-DONE.

PASS -> exact tested hash eligible for one hosted probe after slot accounting. FAIL -> close CR081 and move directly to the predeclared state-adaptive macro-economic architecture; no CR081A/B/C retuning.

## Binding policies

- Kaggle authenticated API first.
- Exact H2H uses `kaggle-environments==1.32.7`, isolated package processes and both seats.
- Original final holdout remains sealed.
- Mechanically/semantically invalid runs are quarantined before score interpretation.
- Closed hypotheses remain closed unless genuinely new evidence invalidates their failure reason.
