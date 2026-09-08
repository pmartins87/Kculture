# CR071 synthesis plan — exact-reference era

Status: preparation while `historical-reference-league-v1` is running on branch `fix/kaggle-parity-v1`.

## Governing evaluation policy

1. Promotion is driven by seat-balanced win/loss score rate on the exact Kaggle reference (`kaggle-environments==1.32.7`).
2. Mean/median money margin are diagnostic only and must not promote or veto a candidate by themselves.
3. Both seats are mandatory.
4. Pairwise uncertainty matters: if the paired 95% CI crosses 0.5, the matchup is unresolved and receives more seeds only when it can materially change the top ranking or component-selection decision.
5. Hosted Kaggle ratings remain an external reality check because one H2H does not reproduce the ladder population.
6. The accelerated `kagsim` backend may influence promotion only after candidate-specific closed-loop parity is proven against the exact Kaggle reference.

## Frozen six-agent historical corpus

The round-robin uses the exact authoritative artifacts recovered from their original GitHub Actions runs:

| Candidate | Frozen package | Strategy fingerprint |
|---|---|---|
| CR053 | `R4D_CR053_ROUTE106309334_V1.tar.gz` | Static public-replay route from episode 106309334. Coherent fixed trajectory; minimal online adaptation. |
| CR061 | `R4D_CR061_INDAR_TOP10_SEATSAFE_V1.tar.gz` | Frozen E776 Indar/Niklita lineage: six-trace consensus programme, visible-state execution guards, Kenjo medoid basis, demand-aligned pasture relabeling, terminal animal liquidation, guarded latent-pasture activation, engine-exact delivery repair. |
| CR065 | `R4D_CR065_FARMING_SCORE_V3_SEATSAFE_V1.tar.gz` | Two-route farming programme. Selects route from visible shop/market/opponent farming state and adds segment-boundary cash/budget sales to fund planned purchases. |
| CR068A | `R4D_CR068A_RANK_V11_SEATSAFE_V1.tar.gz` | Rank-agent trajectory with public clone-profile detection, conditional premium-sale front-running and terminal liquidation/safety logic. |
| CR068B | `R4D_CR068B_MATH_V4_SEATSAFE_V1.tar.gz` | Conservative 8-cow/4-sheep math route with sale-slot ranking, same-turn funding/stock guards, terminal banking/liquidation and an opponent-flow detector that conditionally pulls premium sales forward. |
| CR070A | `R4D_CR070A_TETSU_SHAPE_SHOP_SEATSAFE_V1.tar.gz` | Tetsu conserved route family with three visible-state route checkpoints, weed/no-op repair, same-turn shed projection, sell clamping, terminal/dead-stock liquidation and one-slot shed-capacity reserve. |

## Known exact-reference fact before the full league

The corrected exact-reference CR053 vs CR070A run used 32 paired seeds / 64 games and produced:

- CR053 29 wins, 35 losses, 0 ties.
- CR053 score rate 0.453125; CR070A score rate 0.546875.
- Paired uncertainty crosses 0.5, so the result is **not decisive**.
- Correct verdict: `CR070A_LEADS_BUT_MORE_SEEDS_REQUIRED`.

This replaces the earlier incorrect interpretation that CR053 had decisively beaten CR070A.

## Hosted-winner shape diagnostic (prior only, never a promotion gate)

The latest public-opponent meta radar contains 10 winner profiles. Comparing each candidate's frozen route/tape to the winner-mean action and market profile produces a useful *shape prior*.

CR053 is unusually close to the public winner archetype:

- worker-action normalized L1 deviation: about **0.041**;
- seed-purchase normalized L1 deviation: about **0.070**;
- sell-quantity normalized L1 deviation: about **0.273**.

For comparison, the main alternatives have worker-action deviation roughly 0.117–0.308 and seed-purchase deviation roughly 0.30–0.48. CR053's seed mix is especially close to the public winner mean: WHEAT 132 vs 140.9, CARROT 42 vs 44.1, STRAWBERRY 30 vs 27.7, TOMATO 11 vs 9.1, MELON 13 vs 14.4.

This is **not evidence that CR053 is strongest**. It is a diagnostic explanation for why a static replay-derived policy can remain hosted-competitive and a reason to preserve CR053 as a serious backbone/prior even if a specialized H2H favors another candidate. The exact-reference league and hosted results retain precedence.

## Why CR071 should not be a naive blend

The six policies differ primarily in *where* they add intelligence around a strong route backbone. Their useful components are not interchangeable:

- **Route-family selection:** CR065 and CR070A.
- **Execution/state guards and latent farm capacity:** CR061.
- **Opponent-aware market timing:** CR068A and CR068B.
- **Cash/funding safety:** CR065 and CR061 lineage.
- **Shed capacity / unfillable-order protection / dead-stock cleanup:** CR070A.
- **Terminal liquidation:** CR061, CR068A, CR068B and CR070A in different forms.
- **Pure coherent baseline:** CR053.

Therefore CR071 must preserve a winning backbone and transplant only components whose exact-reference ablations improve W/L. We must not concatenate all repairs or mix route actions turn-by-turn without proof; doing so can destroy trajectory coherence.

## CR071 build sequence after league completion

### Gate A — choose backbone

Use the full six-agent Bradley-Terry ranking plus aggregate score rate and hosted-rating reality check. If the top two remain statistically entangled, expand only their decisive cross-matchups and any matchup that changes first place.

### Gate B — identify complementarity

For each non-backbone candidate, classify its value as one of:

- backbone-quality evidence;
- opponent-specific specialist;
- robust guard/repair component;
- route selector;
- terminal-only improvement;
- likely redundant/noisy component.

A candidate that ranks poorly overall can still contribute a component if its losses are localized and the component has a clean visible-state trigger.

### Gate C — component ablations

Create one change at a time against the selected backbone. Initial ablation candidates, pending league evidence:

1. CR070A shed-capacity reserve + sell clamp/dead-stock logic.
2. CR068B opponent-flow premium front-run detector.
3. CR065 segment cash/budget guard.
4. CR061 terminal/latent-pasture guarded capacity additions.
5. CR065/CR070A visible-state route selector only if the league shows different matchup niches.

Each ablation receives exact-reference both-seat W/L against a representative opponent panel. No component is retained on money-margin improvement alone.

### Gate D — interaction tests

Only components that independently pass Gate C may be combined. Test pairwise interactions before a multi-component CR071 candidate. This prevents two individually useful repairs from conflicting on the same market slot, shed inventory, or route timing.

### Gate E — hosted submission

A CR071 package becomes Kaggle-submit-worthy only after:

- exact-reference package smoke passes;
- both-seat W/L evidence beats or meaningfully diversifies the current hosted frontier;
- no known seat-clock or observation-shape regression;
- package provenance and SHA256 are recorded;
- candidate-specific accelerated parity is proven if `kagsim` evidence was used.

## Current run

`historical-reference-league-v1`, run `34276243787`, commit `75cbf1bc305e780634f9777e4c5d866e10e626e4`.

It freezes all six authoritative packages and runs all 15 unique H2Hs directly on the exact Kaggle reference, 32 paired seeds / 64 games per pair (960 games total), then aggregates seat-balanced W/L and Bradley-Terry standings.
