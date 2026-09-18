# First-Party Ready-Wool Causal Gate Result — 2026-09-18

## Binding result

Workflow `35311750191`, artifact `10533792019`, exact engine `1.32.7`.

Mechanical PASS:
- 48 valid branch states;
- zero runtime/action-identity failures;
- exact discovery/replay parity;
- all treatments completed DONE/DONE.

Strategic result:
- mean W/L score delta: **+0.1666667**;
- mean terminal-margin delta: **+14.9583**;
- median margin delta: **+4.5**;
- 16 positive-W/L states;
- 32 W/L-neutral states;
- **0 negative-W/L states**;
- **16 non-win -> win flips**;
- **0 win -> non-win regressions**;
- 26 positive-margin states;
- **0 negative-margin states**.

By opponent:
- V47 mirror: W/L delta **+0.25**, 8 non-win -> win flips;
- V48: W/L delta **+0.25**, 8 non-win -> win flips;
- Tactical Memory: W/L delta **0.0**, margin **+35.125**, no regression.

Binding verdict: **`READY_WOOL_CAUSAL_PASS_SAFE_OPTION`**.

## What was proved

The V2b headroom was not merely an artifact of executing the Ready Stock wrapper.
A first-party rule using only legal current own state reproduced the competitive effect:

```
if V47 current market == []
and own private shed.WOOL >= 2:
    candidate market = [["SELL","WOOL",2]]
```

The counterfactual changes no farmer action and no hand action, uses no future route,
no seed, no opponent identity, no hidden opponent state, and no third-party proposal
generator at runtime.

The early eligible event appeared around steps 151–155 and converted ties to wins against
both modern strong opponents across all four fresh seeds. A later eligible state around
step 344 was usually W/L neutral; against Tactical Memory it was often strongly positive
in money while W/L remained a win.

## Relation to CR071 PRESALE1

O-RW1 is economically related to the earlier PRESALE1 line but is not the same operator.

PRESALE1 required:
- a CR053-like opponent;
- predicted opponent dump within a short lead;
- own route already planning to sell the item within the next ~25 actions.

O-RW1 requires only current own stock and an empty V47 market. Therefore the new causal
PASS is independent evidence that ready-stock liquidation itself is a useful proposal
surface on V47.

## Next binding step

Freeze O-RW1 exactly. Do not tune quantity, product, step or thresholds.

Evaluate a conservative **one-shot runtime candidate**:
- O-RW1 is enabled for the whole episode;
- it fires exactly once, at the first legal eligible state;
- afterwards the candidate is exact V47 for the rest of the episode.

This preserves the strongest causal event while avoiding an untested repeated-liquidation
policy.

Use fresh seeds and a multi-opponent panel. If the one-shot candidate transfers without
material regression, O-RW1 becomes a runtime-safe first-party solver option and is ready
to join the broader proposal/value architecture.

No Kaggle submission is authorized by this causal result alone.
