# FP001 STATUS — mechanics/economics integration track

Updated: 2026-09-15

Authoritative experimental branch: `research/first-principles-economy-v1`.  
Competition source of truth: `STATUS.md` / `ROADMAP.md` on `fix/kaggle-parity-v1`.

## Mission

Discover causally defensible mechanics, economic primitives and higher-level options that improve prize probability when integrated with accumulated competitive knowledge. FP001 is additive; it does not replace CR053/CR086/CR087/CR088 knowledge.

## Proven primitives retained

- H1 WHEAT carry — PASS `34843184110`, +916.875 paired mean.
- H1B sale deferral — PASS `34843556192`, 104/104 positive exact cases.
- H8/B3 animals — COW strongest in tested physical baseline; DAILY CARE strongly positive (`34844919444`, `34847600991`).
- H9 public-town demand — representation PASS `34847099631`; public shops alter expected MILK/WOOL/EGG demand.
- H10 compact routing + threshold-6 batching — PASS `34848106237`.
- H11 fertilizer conversion — PASS `34848464648`; STRAWBERRY strong, TOMATO positive regions.
- B4 scale×CARE — fifth COW marginal; sixth beyond action/opportunity-cost frontier (`34848633407`).
- M6S1 remains a genuine economic module, not a competitive backbone by itself.

## Closed integration failures

CR089 run `34923802262`: C5_BASE and C5_M6S1 both 0W–132L. Static C5/C5+M6S1 closed as backbones; M6S1 preserved.

CR090 run `34979280512`: simple first-shop H9 species adaptation failed causally. H9 remains a legal state representation only; no threshold tuning.

## CR091 hierarchical market option — COMPLETE / PASS

Architecture tested: hosted-proven exact CR053 backbone + separable CR086 latent-supply SELL-priority option, valued by W/L.

The initial run `34987640694` is invalid/non-binding because its direct-`exec()` runner failed CR052 package semantics.

The authoritative hosted-faithful rerun is `34990757344`, commit `f49bff2e7adde626b01b9fa3c0413f7fc97d9649`.

Mechanics:

- zero failures;
- zero parity violations;
- exact CR053 farmer/hand parity;
- exact normalized market-order multiset parity;
- exact BASE full-action parity;
- option active with 1,075 reorders.

W/L edge-score deltas `O1 - BASE`:

- CR052 `0`
- CR053 `+0.1875`
- CR083 `0`
- CR086 `0`

Mean edge delta `+0.046875`, 4/4 nonnegative, worst regression `0`.

Binding verdict: **`CR091_LATENT_OPTION_TRANSFER_PASS_ADVANCE_ROUTER`**.

The exact latent-priority mechanism is frozen as option **O1**. No post-result threshold retuning.

Competition result: `docs/strategy/CR091_HIERARCHICAL_MARKET_OPTION_RESULT_2026-09-15.md` on `fix/kaggle-parity-v1`.

## Current experiment — CR092 broad O1 transfer / router labels

CR092 tests whether frozen O1 survives a broader population and whether its competitive value is heterogeneous enough to justify a public-state router.

Population: the exact 11-opponent CR089 frozen artifact `10378299284` — four exact anchors plus seven current-top macro representatives.

Evaluation:

- seeds `91401..91406`;
- both seats;
- BASE vs O1;
- 264 episodes total;
- hosted-faithful `kaggle-environments==1.32.7` execution;
- edge matrix parallelized.

Router-label discipline:

- capture O1's legal state immediately before its first actual reorder;
- record strategic-state hash for both BASE and O1;
- a label is admissible only if BASE has the identical strategic-state hash at the same step for the matched opponent/seed/seat;
- primary label is `outcome(O1) - outcome(BASE)`;
- opponent identity and seed are offline metadata only, never runtime features;
- terminal money is diagnostic only.

Research implementation:

- `tools/cr092_broad_option_edge.py`
- `tools/cr092_aggregate.py`
- `.github/workflows/cr092-broad-option-router-label.yml`
- head commit `b42347617a6967eeb2862fde23737c7538d3b9d3`
- active workflow **`35015135956`**
- prepare stage PASS; all 11 packages were SHA-verified before the evaluation matrix.

Frozen branches:

- broad survivor + heterogeneous labels -> advance CR093 router;
- broad survivor without sufficient downside heterogeneity -> retain O1 and add next separable option, initially H1/H1B timing;
- broad fail but strong positive/negative option value -> conditional router discovery;
- otherwise close always-on O1 without threshold tuning;
- mechanics failure -> no strategic inference.

## Hosted policy

No CR092 Kaggle submission is authorized automatically. Original final holdout remains sealed. Hosted slots remain reserved for mechanically exact state-adaptive/multi-option candidates that survive meaningful fresh-seed population-transfer questions.
