# CR-010 — Kaggriculture order-sequence value audit

Status: **RUNNING / DIAGNOSTIC ONLY**

CR-008 proved that a high-confidence same-turn SELL forecast is not sufficient when the adaptive order is appended after the frozen base market list. CR-009 then showed that forecast timing itself is not the problem: the other player's sale is usually immediate.

CR-010 tests the exact Kaggriculture transaction sequence. The official engine resolves market positions sequentially. When both players SELL the same product in the same position, each unit is quoted from the same pre-commit inventory and committed lockstep. A later position sees inventory already changed by earlier positions.

Using the frozen CR-007 model family and strict Aug-26 top-episode replays, this audit measures CARROT/STRAWBERRY events where the high-confidence signal and the other player's sale occur in the same turn. It compares game revenue from our SELL at position 0 with revenue after the other player's first same-product order.

## Frozen gate

`ORDER_SEQUENCE_VALUE_SUPPORTED` requires all of:

- at least 50 same-turn high-confidence events;
- other player's first same-product sale in position 0 in at least 75% of events;
- mean position-0 gain >= 20;
- median position-0 gain >= 10;
- positive position-0 gain in at least 80% of events.

A PASS authorizes one bounded causal agent test that changes only adaptive order placement. It does not authorize hosted submission or held-out access.
