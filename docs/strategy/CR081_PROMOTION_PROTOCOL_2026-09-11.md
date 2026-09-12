# CR081 promotion protocol — fidelity-correct v3 freeze

Candidate family is fixed by `CR081_GATE_A_RESULT_2026-09-11.md`. Strategic thresholds and the 288-step boundary remain exactly those frozen before H2H. Two implementation-only defects were discovered **before reading their H2H scores** and are quarantined below.

## Invalid implementations

### v1 — run `34671122716` — INVALID / SUPERSEDED

Replay action index `s` was incorrectly interpreted as runtime step `s`, delaying the CR071M physical backbone by one turn. Kaggle replay `steps[s].action` corresponds to runtime step `s-1`. Master seed `9120811` is permanently burned.

### v2 — run `34671446692` — INVALID / SUPERSEDED

The replay/runtime offset was fixed, but two inherited CR071M **strategic** market transforms remained active after the UMG overlay inside steps 0–287:

- `_cr053_counter_market`, which can alter market behavior specifically on a CR053-like public trajectory;
- `dead_stock`, which appends additional economic SELL orders.

This was detected before any v2 score was read. Concrete pre-score audit evidence: UMG holdout episode `107956535` produced 20 extra market actions over runtime steps 267–287; isolating the runtime showed they disappear when `dead_stock` alone is disabled. These are not legality/capacity repairs, so v2 does not faithfully implement the frozen market-replacement hypothesis. Master seed `9120812` is permanently burned. No v1/v2 score may be used for strategic inference.

## Correct v3 candidate

Exactly one fidelity-correct CR081 implementation is allowed:

- exact CR071M source as base;
- CR071M physical/runtime backbone remains same-step and unchanged;
- runtime steps **0–287** replace the base market queue with the UMG development-only per-step modal queue learned from replay action indices **1–288**;
- same-turn `BUY_PRODUCT` is credited before a later `SELL` during legality clamping, required by the UMG runtime-step-0 buy→buy→sell mechanism;
- `room_guard` remains inside the prefix because it is a shed-capacity safety repair;
- `clamp_sells` remains because it prevents impossible/partially impossible SELL orders and preserves order-slot legality;
- `_cr053_counter_market` is disabled inside steps 0–287 and resumes after the prefix;
- `dead_stock` is disabled inside steps 0–287 and resumes after the prefix;
- after runtime step 287, normal same-step CR071M behavior resumes;
- no replay route stitching, team identity, episode ID, seed, future state or opponent-private feature.

The runtime-aligned development support remains approximately 0.970 / 0.942 / 0.914 for the three 96-step blocks and drops to ~0.683 in the next block. The 288-step boundary is not changed.

## Exact evaluation panel

Runtime: `kaggle-environments==1.32.7`, isolated package processes, both seats.

Fresh v3 master seed: **9120813**.

- 32 seeds × 2 seats = 64 games per H2H;
- direct: CR081 vs CR071M;
- guardrails: CR081 vs CR053, CR061, CR065;
- same-seed incumbents: CR071M vs CR053, CR061, CR065.

Seed firewall must exclude all earlier CR080 masters plus invalid CR081 masters `9120811` and `9120812`.

## Frozen promotion gate

All checks must pass:

1. complete seven-H2H panel, exactly 64 games / 32 fresh seeds each;
2. zero agent errors and zero non-DONE games;
3. CR081 direct score rate vs CR071M >= **0.5625**;
4. aggregate guardrail delta `sum(score(CR081, guard) - score(CR071M, guard)) >= 0`;
5. every individual guardrail delta >= **-0.0625**.

Primary metric is seat-balanced W/L score rate. Reward margin is diagnostic only.

## Decision tree

- **PASS:** freeze exact candidate hash, account for active hosted slots, then submit exactly one hosted CR081 probe.
- **FAIL:** close CR081. No CR081A/B/C, no boundary movement, no market-quantity edits and no retuning on these seeds. Advance to the already-predeclared state-adaptive macro-economic architecture using the current-frontier corpora.

The original final holdout remains sealed. No automatic Kaggle submission is part of this workflow.
