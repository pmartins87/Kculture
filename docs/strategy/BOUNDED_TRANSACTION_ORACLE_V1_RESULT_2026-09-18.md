# Bounded Transaction Oracle V1 Result — 2026-09-18

Workflow `35309837210`, artifact `10532858435`, exact engine `1.32.7`.

## Result

Mechanical gate PASS:
- 16 valid branch states;
- 16 non-base candidate rollouts;
- fresh-replay parity exact;
- zero failures.

Strategic result:
- BASE score rate: `0.75`;
- oracle score rate: `0.75`;
- W/L delta: `0.0`;
- mean/median oracle margin delta: `0.0`;
- loss-to-win flips: `0`;
- positive-margin headroom states: `0`;
- no non-base proposal was ever selected.

Binding verdict: **`TRANSACTION_ORACLE_NO_HEADROOM`**.

## Interpretation

This closes the **simple current-turn SELL reorder / one-turn deferral family on complete
V47**. It does not close exact search.

The discovery trace revealed why most nominal proposal operators deduplicated away: at
the selected separated sale states V47 exposed only one effective SELL. The search
therefore reduced to BASE versus removing that sale for one turn, and V47's own choice
was terminally optimal in every tested branch under this proposal family.

The next proposal space must therefore come from richer adaptive wrapper behaviour rather
than synthetic permutation of a queue that is usually absent.

## Next gate

Use several exact public adaptive agents that share the modern 41-route chassis as
**shadow proposal generators** on the same V47 trajectory. At a state, retain only
proposal actions whose farmer/hands exactly equal V47 while the market action differs.
Exact replay evaluates each unique market proposal once; V47 resumes afterwards.

This tests whether the competitive public frontier already contains heterogeneous local
market decisions that exact search can select state-by-state. It is a stronger and more
data-driven proposal family while still preserving the strong physical programme.

No Kaggle submission is authorized by V1.
