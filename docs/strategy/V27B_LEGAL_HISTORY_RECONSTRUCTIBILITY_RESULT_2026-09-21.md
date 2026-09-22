# V27B Legal-History Reconstructibility — Result — 2026-09-21

## Binding result

Corrected episode workflow: **`35676166396`**  
Aggregate-only binding workflow: **`35678269956`**  
Aggregate artifact: `10673273774`  
Digest: `sha256:927a1f266329aa02965b3ed76c3ec3fe149a82429efbde519616c5b1ec99ec63`

Mechanical:
- 12/12 shards PASS;
- 72/72 episodes;
- all 15 frozen checkpoints per episode;
- zero failures;
- immutable V26A snapshot only;
- no live Kaggle source reacquisition.

Decision:

**`V27B_BOUNDED_LEGAL_HISTORY_DISTILLATION_VIABLE`**

Selected minimum viable history horizon:

**256 prior legal candidate observations**

## Key parity metrics

### H=0 — current-state-only reconstruction

- complete action: **0.7777778**
- MARKET: **0.7777778**
- FARMER: **1.0000000**
- HANDS: **1.0000000**
- minimum source complete-action parity: **0.7777778**
- minimum checkpoint complete-action parity: **0.0000000**

### H=256 — selected bounded history

- complete action: **0.9962963**
- MARKET: **0.9962963**
- FARMER: **1.0000000**
- HANDS: **1.0000000**
- minimum source complete-action parity: **0.9777778**
- minimum checkpoint complete-action parity: **0.9444444**

H=256 passes every frozen V27B gate.

### FULL legal history

- complete action: **1.0000000**
- MARKET: **1.0000000**
- FARMER: **1.0000000**
- HANDS: **1.0000000**
- minimum source parity: **1.0000000**
- minimum checkpoint parity: **1.0000000**

## Interpretation

The rank-1 teacher's important hidden episode state is not irreducibly private.

Current state alone is insufficient, but the behavior is almost perfectly reconstructible from a bounded legal observation history of 256 candidate calls.

The remaining state dependence is concentrated in MARKET; FARMER and HANDS reconstruct exactly in this audit.

This authorizes exactly one first-party behavioral-distillation gate using a fixed 256-step legal-history representation.

Next:
**`V27C_256_HISTORY_BEHAVIORAL_DISTILLATION`**.

No Kaggle submission is authorized.
