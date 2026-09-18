# O-RW1 Hosted-Faithful Causal Result — 2026-09-18

## Binding result

Workflow `35363453097`, artifact `10555907821`, exact engine `1.32.7`.

This is the first O-RW1 causal gate that uses the same loader contract as Kaggle hosted:
`kaggle_environments.agent.get_last_callable`.

Exact public V47 hosted entrypoint:
`_y_agent_shopherd`.

Mechanical PASS:
- 48 valid branch states;
- zero failures;
- exact discovery/replay parity;
- both seats;
- fresh seeds `64001..64004`.

Strategic result:
- mean W/L score delta: **+0.0833333**;
- mean terminal-margin delta: **+14.9583**;
- median margin delta: **+4.5**;
- **8 non-win -> win flips**;
- **0 win -> non-win regressions**;
- **0 negative-W/L states**;
- 26 positive-margin states;
- **0 negative-margin states**.

By opponent:
- V47 mirror: mean score delta **+0.25**, 8 positive flips;
- V48: W/L delta **0.0**, mean margin delta **+4.875**;
- Tactical Memory: W/L delta **0.0**, mean margin delta **+35.125**.

Binding verdict:
**`READY_WOOL_CAUSAL_PASS_SAFE_OPTION`**.

## Correction versus the earlier run

The earlier O-RW1 causal run used `mod.agent` and therefore did not test the true hosted
V47 entrypoint. It reported a larger +0.1667 mean score delta and positive W/L effects
against both V47 and V48.

That result is superseded for promotion purposes.

The hosted-faithful effect is weaker and more concentrated:
- exact V47 mirror still benefits strongly;
- V48 no longer flips W/L;
- Tactical Memory remains W/L neutral;
- no tested state regressed in W/L or terminal margin.

## Decision

O-RW1 survives the entrypoint correction as a causal, apparently safe proposal option,
but its competitive strength is lower than the pre-correction evidence suggested.

Do not tune quantity, product, timing or thresholds.

Next binding gate: rerun the autonomous one-shot runtime transfer with the official
hosted loader. Only a runtime PASS permits rebuilding a corrected hosted package.
