# CR090 — H9 public-shop adaptive fifth-animal result

Date: 2026-09-15  
Authoritative branch: `fix/kaggle-parity-v1`

## Verdict

**CLOSED / CAUSAL FAIL**

Binding decision: `CR090_H9_CAUSAL_FAIL_CLOSE_SIMPLE_SPECIES_ADAPTATION`.

The simple rule “at first public-shop reveal, choose SHEEP iff expected remaining WOOL demand exceeds MILK; otherwise choose COW” is mechanically correct but not causally valuable. Do not rescue it with threshold tuning.

## Authoritative execution

- workflow run: `34979280512`
- job: `104415027137`
- research commit: `abe2829ab553fc7cc2b854d3df80f7eee3f89027`
- artifact: `cr090-h9-adaptive-fifth-phase1-v1`
- artifact ID: `10401171740`
- artifact ZIP SHA-256: `407769891c9f8ab7c240c8bb08fd10bfa606a890436cc320d5de6508ba2971ec`
- engine: `kaggle-environments==1.32.7`
- seeds: `90201..90264`
- both seats
- 128 cases/policy; 384 full episodes across `DELAY_COW`, `DELAY_SHEEP`, `H9_ADAPT`
- original final holdout untouched
- no hosted submission

## Mechanics

All mechanics gates passed:

- failures: `0`
- pre-reveal prefix parity: `128/128`
- first-shop parity: `128/128`
- selector exact full-trajectory match to its selected fixed control: `128/128`
- final fifth animal exactly matched intent: `128/128`
- natural support: YARN `24`, MILK `28`, NEUTRAL `76`

Therefore the negative result is economic/causal, not an execution artifact.

## Causal results

### YARN regime — selector chose SHEEP

`H9_ADAPT - DELAY_COW`:

- n = `24`
- mean = **-174.46**
- median = **-451**
- wins/losses = **7/17**
- positive rate = **29.17%**
- CI95 = `[-808.02, +459.10]`

Despite the first `YARN_STORE` implying much larger expected remaining WOOL demand than MILK demand, switching the marginal fifth animal from COW to SHEEP did not improve realized value.

### MILK regime — selector chose COW

`H9_ADAPT - DELAY_SHEEP`:

- n = `28`
- mean = **+2,119.39**
- median = **+2,151**
- wins/losses = **28/0**
- positive rate = **100%**
- CI95 = `[+1,940.25, +2,298.53]`

This confirms COW's strong physical/economic advantage in milk-demand regimes, but does not rescue the adaptive rule because its differentiated YARN branch failed.

### Natural distribution

`H9_ADAPT - DELAY_COW`:

- mean = **-32.71**
- median = `0`
- signs = `7W / 104T / 17L`
- CI95 = `[-150.06, +84.64]`

`H9_ADAPT - DELAY_SHEEP`:

- mean = **+598.98**
- median = **+939**
- signs = `77W / 24T / 27L`

Checks:

- `causal_pass = false`
- `natural_robustness_pass = false`

## Interpretation

H9 remains valid as a **demand representation**: the public town shop sequence changes expected future product demand. CR090 falsifies the stronger inference that this demand statistic alone determines the optimal marginal species.

This distinction is now binding:

`public demand signal != optimal action rule`.

Animal choice interacts with production rate, CARE, feeding, action capacity, purchase timing, prices, future shops, inventory, market competition and opportunity cost. The next controller must value options by realized competitive outcomes, not by a single economic proxy.

## What remains reusable

Preserve:

- H9 public-shop demand features as legal state information;
- H8/B3 animal economics;
- H10 compact routing/batching;
- CARE;
- M6S1/H11 as validated economic modules;
- CR086 latent-supply market estimator/operator;
- CR053 and elite/top-lineage macro knowledge.

Close:

- simple first-shop `WOOL > MILK => SHEEP else COW` routing;
- any post-result threshold ladder on that rule;
- CR090 Phase 2 H9+M6S1, because its prerequisite failed.

## Next binding direction

Proceed to **CR091 — hierarchical competitive option controller**, beginning conservatively on the exact hosted-proven CR053 backbone. The first option gate must preserve CR053 physical actions and test a separable adaptive market option using population W/L, not terminal money, as the promotion objective.
