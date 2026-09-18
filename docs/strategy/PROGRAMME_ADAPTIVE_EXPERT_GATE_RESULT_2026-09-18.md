# Programme Adaptive Expert Gate Result — 2026-09-18

## Binding result

Workflow run: `35307879368`  
Head: `f8a78088263539ef62be621ced666dde96a684fd`  
Artifact: `10532661922`  
Artifact digest: `sha256:82527e65e8bd9d45e130e1fd0ee71676830e2bda298a21217ba46778ce57c341`

The gate completed mechanically clean on `kaggle-environments==1.32.7`:
- 64 paired matchups;
- 128 complete episodes;
- 16 fresh seeds, both seats;
- exact V47 and V39 source identities verified;
- no strategic result from the three earlier harness-only failures.

## Result

| Block | Static W/L | Router W/L | Static mean margin | Router mean margin | Paired margin delta |
|---|---:|---:|---:|---:|---:|
| Modern V47 | 0/32 | 0/32 | -9,784.625 | -6,970.750 | +2,813.875 |
| Legacy V39 | 5/32 | 5/32 | -7,807.219 | -5,080.156 | +2,727.063 |
| Overall | 5/64 | 5/64 | -8,795.922 | -6,025.453 | +2,770.469 |

Primary score rate stayed exactly `0.078125 -> 0.078125`; delta `0.0`.

## Binding decision

`CLOSE_STANDALONE_ROUTER_OPEN_BOUNDED_TRANSACTION_MARKET_SEARCH`

The pre-registered promotion threshold required at least +0.0625 W/L, positive paired
margin delta, and no material block regression. The router satisfied only the margin
condition.

Do not retune this tree, add depth, add seeds, or search another checkpoint merely to
rescue the standalone route router.

## Interpretation

This is not evidence against solver/search as the project architecture. It narrows the
search space.

The frozen router can identify economically better suffixes: it recovered about 2.8k
terminal margin per game against both adaptive lineages. But even that improvement never
converted a V47 loss into a win. Therefore the main missing competitive surface is not
which long programme to select after turn 144.

The public-frontier audit already identified the layers absent from pure programme tapes:
transaction guards, sale timing/queue microstructure, storage/funding repairs, bounded
state-conditioned substitutions and exact terminal handling. The adaptive gate now
provides direct empirical support for moving search to those layers.

## Next gate

Use a complete strong adaptive programme as the organism/base policy. Freeze physical
actions and the base policy except at one bounded transaction/market intervention.
Generate a small candidate set that preserves legality and provenance, exact-evaluate the
counterfactual candidates from matched episodes, and measure **oracle W/L headroom** before
training any selector.

If local transaction search has meaningful loss-to-win or W/L headroom, generate
observation-only targets and distill a compact proposal/value selector. If it only changes
money without W/L, close that transform family and advance to a richer transaction family.

No Kaggle submission is authorized by this result.
