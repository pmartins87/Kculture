# CR-010 — Kaggriculture order-sequence value audit

Status: **COMPLETE / PASS / CAUSAL AGENT TEST AUTHORIZED**

Canonical run: **33106343741** (run 2)  
Artifact: **9660715804**  
Artifact digest: **sha256:03dd6a8ac64f12e02b8ba89ebc756569c923386093211f0e76cd80f2e8b12fea**

Run 1 (`33106060268`) is **MECHANICAL_NULL**: frozen tool identity passed, then execution stopped before analysis because `kagglehub` was not installed. Run 2 changed only the workflow dependency installation; tool, model family, thresholds and gates remained frozen.

CR-008 proved that a high-confidence same-turn SELL forecast is not sufficient when the adaptive order is appended after the frozen base market list. CR-009 then showed that forecast timing itself is not the problem: the other player's sale is usually immediate.

CR-010 tests the exact Kaggriculture transaction sequence. The official engine resolves market positions sequentially. When both players SELL the same product in the same position, each unit is quoted from the same pre-commit inventory and committed lockstep. A later position sees inventory already changed by earlier positions.

## Result

Strict Aug-26 top-episode replays, frozen CR-007 signals:

- same-turn high-confidence events: **138**;
- other player's first same-product SELL in position 0: **120/138 = 86.9565%**;
- mean position-0 revenue gain: **+139.9565**;
- median gain: **+72**;
- positive gain: **137/138 = 99.2754%**;
- gain >=10: **86.2319%**;
- summed conditional position-0 headroom: **+19,314**.

Per product:

- CARROT: 14 events, mean +27.57, median +15.5, positive 92.86%, total +386;
- STRAWBERRY: 124 events, mean +152.65, median +80.5, positive 100%, total +18,928.

## Frozen gate

All five gates PASS:

- support >=50: PASS;
- position-0 fraction >=0.75: PASS;
- mean gain >=20: PASS;
- median gain >=10: PASS;
- positive gain fraction >=0.80: PASS.

Formal result: **`ORDER_SEQUENCE_VALUE_SUPPORTED`**.

This authorizes exactly one bounded causal agent test that keeps the frozen CR-007 prediction model/thresholds and changes only how an otherwise identical adaptive sale is positioned relative to the base market-order list. It does not authorize hosted submission, validation, or held-out access by itself.
