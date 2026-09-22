# V27B Legal-History Reconstructibility — Result — 2026-09-22

## Binding result

Corrected binding shard workflow: **`35676166396`**  
Corrected aggregate-only workflow: **`35725538992`**  
Final artifact: `10693237472`  
Digest: `sha256:7c5ebff8e448c358096ffbfa63392900803a59b23504562709c1ca451515cd4e`

Mechanical:
- 12/12 corrected shards PASS;
- 72/72 episodes;
- all frozen checkpoints/horizons present;
- failures 0;
- immutable V26A snapshot only;
- no live Kaggle reacquisition.

Decision:

**`V27B_BOUNDED_LEGAL_HISTORY_DISTILLATION_VIABLE`**

Selected minimum finite history horizon:

**`H = 256`**

## Selected-horizon parity

H=256:
- complete-action parity: **0.9962962963**;
- MARKET parity: **0.9962962963**;
- FARMER parity: **1.0000000000**;
- HANDS parity: **1.0000000000**;
- minimum source complete-action parity: **0.9777777778**;
- minimum checkpoint complete-action parity: **0.9444444444**.

H=128 fails the frozen gate:
- complete-action parity: **0.9296296296**;
- MARKET parity: **0.9296296296**;
- minimum source parity: **0.9111111111**;
- minimum checkpoint parity: **0.0**.

FULL history:
- complete-action / MARKET / FARMER / HANDS parity: **1.0**.

H=0:
- complete-action parity: **0.7777777778**.

## Interpretation

The rank-1 V56 teacher is not adequately state-only, but its hidden runtime state is almost perfectly reconstructible from the previous **256 legal observations**.

This is a strong and specific result:
- the required memory is finite;
- the representation uses only legal player history;
- no source identity or hidden environment state is required;
- shorter H=128 is materially insufficient.

Therefore:
- freeze history window at 256;
- no further history-window sweep;
- open exactly one bounded-history behavioral-distillation viability branch.

Next:
**`V27C_BOUNDED_HISTORY_BEHAVIORAL_DISTILLATION_CENSUS`**.

No Kaggle submission is authorized.
