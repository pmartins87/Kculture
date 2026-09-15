# CR091 — hierarchical market option result

Date: 2026-09-15  
Authoritative branch: `fix/kaggle-parity-v1`

## Verdict

**PASS — `CR091_LATENT_OPTION_TRANSFER_PASS_ADVANCE_ROUTER`.**

The binding rerun is GitHub Actions run `34990757344`, head commit `f49bff2e7adde626b01b9fa3c0413f7fc97d9649` on `research/first-principles-economy-v1`.

Artifact: `cr091-hierarchical-market-option-gate-v1`, artifact ID `10406926564`, ZIP SHA-256 `d6d9a5a7cb187e48dc4cb187e348adb7fff4d10666f18f27b4030ccc8ad2f3d0`.

The earlier run `34987640694` is explicitly **invalid/non-binding** because its direct `exec()` harness did not reproduce package execution semantics for CR052. It produced no strategic verdict. See `docs/strategy/CR091_RUN1_INVALID_2026-09-15.md`.

## Frozen question

Does the exact CR086 latent-supply SELL-priority operator add competitive option value when transplanted onto the exact hosted-proven CR053 physical/macro host, without changing farmer actions, hand actions, market-order products or quantities?

Treatments:

1. `CR053_BASE` — exact CR053 package;
2. `CR053_LATENT_PRIORITY` — exact CR053 action with only the sequence of its existing market orders changed by the exact CR086 latent-supply cash-risk priority operator.

Opponent panel:

- `CR052_REAL`;
- `CR053_REAL`;
- `CR083`;
- `CR086`.

Seeds `91301..91308`, both seats, 16 games per edge, 64 games per treatment, 128 total episodes.

## Corrected hosted-faithful execution

All submission packages were executed through the already validated exact-runtime path:

- `kaggle-environments==1.32.7`;
- fresh spawned process per package per episode;
- `kaggle_environments.agent.Agent` wrapper;
- shared-state observation reconstructed through the official environment path;
- no silent invalid-action/PASS substitution;
- exact CR053 package action generated first, then the frozen O1 transformation applied;
- official-style overage accounting retained.

This was a runner-semantics repair only. Seeds, panel, candidate logic and preregistered decision thresholds were unchanged.

## Mechanics

CR091 passed every mandatory separability check:

- execution/non-DONE failures: **0**;
- parity violations: **0**;
- CR053 farmer/hand parity: exact on every call;
- normalized market-order multiset parity: exact on every call;
- `CR053_BASE` exact-action parity: exact on every call;
- O1 was active: **1,075** market reorder events.

Therefore the treatment isolated order priority rather than smuggling in a physical-route, quantity or product-selection change.

## Competitive W/L transfer

Seat-balanced edge-score deltas, `CR053_LATENT_PRIORITY - CR053_BASE`:

- `CR052_REAL`: **0.0000**;
- `CR053_REAL`: **+0.1875**;
- `CR083`: **0.0000**;
- `CR086`: **0.0000**.

Summary:

- nonnegative edges: **4/4**;
- maximum improvement: **+0.1875**;
- worst regression: **0.0000**;
- mean edge-score delta: **+0.046875**;
- no catastrophe edge was created.

The predeclared broad-transfer rule therefore passed.

Terminal money remains diagnostic only. Promotion is based on competitive W/L option value plus exact mechanics.

## Binding interpretation

CR086 itself remains a weaker hosted backbone than CR053, but one of its internal mechanisms transfers positively when used as a **separable option** on CR053. This is exactly the architectural distinction CR091 was designed to test.

Promote the frozen latent-priority operator to **O1**. Do not retune its thresholds after seeing this result.

CR091 does **not** establish that O1 is prize-class, that local numeric scores predict Kaggle rating, or that O1 should already be submitted hosted. It establishes that the hierarchical `strong host + separable option` architecture has a first causal competitive survivor.

## Next gate

Advance to **CR092 — broad heterogeneous O1 transfer and counterfactual label gate**.

CR092 must:

1. keep exact CR053 and O1 frozen;
2. expand to the same seven current-top macro representatives already frozen in CR089, while retaining the four exact anchors for calibration;
3. use fresh seeds and both seats;
4. preserve exact physical/multiset parity;
5. record the legal public state immediately before O1's first actual reorder opportunity and pair it with the matched `O1 - BASE` W/L outcome label;
6. decide whether O1 is broadly safe always-on, genuinely heterogeneous and router-worthy, or fails broader transfer.

No Kaggle submission is authorized by CR091. Original final holdout remains sealed.
