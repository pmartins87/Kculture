# V4A Bounded Multi-Turn V48 Market Oracle — Result — 2026-09-19

## Binding run

Workflow: **`35444529719`**  
Head: `eceee84deda3321b5df2e5d4078ea1c5a354595b`  
Artifact: `10585248046`  
Artifact digest: `sha256:ae2a8cf19a85ca7f4e716fb3d227f23157790a04f89cbc28b39509d60cd2fcaa`.

Mechanical PASS:
- 12 fresh contexts;
- 11 hard BASE non-wins;
- zero failures;
- exact V47 physical actions preserved;
- horizons 1, 2, 3 turns tested at up to three replay-verified divergence events.

## Binding decision

**`V48_V4A_MARGIN_ONLY`**

Aggregate:
- BASE score rate: **0.0833333**;
- oracle score rate: **0.0833333**;
- score delta: **0.0**;
- nonwin→win flips: **0**;
- positive-score contexts: **0**;
- negative-score contexts: **0**;
- mean oracle margin delta: **+0.25**.

Only one hard context preferred a non-BASE candidate:
- seed 74003, seat 1;
- event step 409;
- horizon 1;
- margin improved only **-238 -> -235**;
- W/L remained a loss.

All other hard contexts selected BASE as the oracle winner.

## Interpretation

Short bounded imitation of exact V48 market output does **not** expose meaningful competitive headroom.
The result is stronger than the failed compact queue rules:
- CQ1/CQ2 could not reproduce V48 precisely enough;
- V4A bypassed that approximation problem by using V48's exact market output directly for 1-3 turns;
- even that exact local substitution failed to change W/L.

Therefore the missing advantage is not a single local queue correction or a short 1-3-turn sequence.

The pre-registered next diagnostic is V4B:
- keep exact V47 farmer/hands;
- allow V48 market substitution across the remaining episode whenever physical actions still match;
- measure whether cumulative market-state control can recover W/L.

If V4B produces W/L headroom, the relevant mechanism is long-horizon/cumulative market state.
If V4B also fails, simple V48-market imitation under a fixed V47 physical policy should be closed.

No Kaggle submission is authorized by V4A.
