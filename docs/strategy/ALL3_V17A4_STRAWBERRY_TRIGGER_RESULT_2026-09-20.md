# ALL3 V17A3/V17A4 STRAWBERRY Runtime Trigger — Binding Result — 2026-09-20

## V17A3 stateless audit

Workflow: **`35539020930`**.

Decision:
**`V17A3_STRAWBERRY_TRIGGER_NOT_COMPRESSIBLE`**.

The best stateless rule was T3_CARRIED20_OR_SHED2:
- recall: 1.0;
- precision: 0.4565;
- fires: 92;
- TP: 42;
- FP: 50.

The main false positives were persistent consecutive turns 494/495 after the true turn-493 event.

## V17A4 rising-edge audit

Workflow: **`35539277486`**.

Decision:
**`V17A4_STRAWBERRY_EDGE_TRIGGER_READY`**.

Selected trigger:

**`E3_CARRIED20_OR_SHED2_RISING`**

Definition:
- base stateless condition:
  - W2;
  - exact ALL3 market has no nonempty order;
  - total own STRAWBERRY >=2;
  - carried STRAWBERRY >=20 OR shed STRAWBERRY >=2;
- fire only on false -> true transition of that full condition.

Binding metrics:
- targets: 42;
- fires: **44**;
- TP: **42**;
- FP: **2**;
- FN: **0**;
- recall: **1.0**;
- precision: **0.954545...**;
- contexts: **24/24**;
- source SHAs: **10/10**.

The two false positives are:
- v13c_hard_20 turn 503;
- v13c_hard_21 turn 503.

No game outcome was used to derive or rank this edge trigger.

## Binding candidate

V17B may activate O-LQ6S with exactly this edge trigger.

Action transformation remains:
- insert SELL STRAWBERRY qty2;
- first semantic free market slot;
- preserve all other market orders/quantities;
- preserve farmer/hands.

No exact-turn whitelist.
No identity/runtime opponent feature.
