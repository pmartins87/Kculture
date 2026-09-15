# CR091 — hierarchical controller, gate 1: CR053 latent-supply market option

Date: 2026-09-15  
Authoritative branch: `fix/kaggle-parity-v1`

## Motivation

CR090 proved that a correct public-state representation does not imply a correct hand-written action rule. CR089 separately proved that large terminal-money gains can produce zero competitive W/L gain.

The next architecture therefore optimizes **competitive option value**, not an isolated economic proxy.

CR053 remains the strongest exact project-hosted anchor (~2064.8), but its policy is a static 719-step route. The first hierarchical-controller gate must not destroy that validated physical trajectory by splicing incompatible route fragments.

CR091 begins with the most separable subsystem: **market-order priority**. It preserves CR053 farmer/hand actions and the complete market-order multiset and tests whether a previously validated legal adaptive operator has positive or heterogeneous W/L value when transplanted onto CR053.

## Exact donor artifacts

### CR053 / CR052 hosted artifact

- workflow run `34105008373`
- artifact ID `10012004237`
- artifact name `cr052-cr053-hosted-candidates`
- archive digest reported by GitHub: `sha256:e450b776b36b2d0f20c2fe4df52800d06405cd85dfb9ae0b211b6d69f7e49bc7`
- exact CR053 package `R4D_CR053_ROUTE106309334_V1.tar.gz`
- CR053 SHA-256 `095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15`
- exact CR052 SHA-256 `b650a31d091323f2510aede0265937d3193a82a99109eadc8ab39c6e85db278d`

### CR086 / CR083 operator artifact

- workflow run `34800444746`
- artifact ID `10331022592`
- artifact name `cr086-latent-supply-gate-a-v1`
- archive digest reported by GitHub: `sha256:2b165c75e6147983ecd7ec5eee7f0a868b6add062368dfc64d77466ff5f5af96`
- exact CR083 SHA-256 `648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`
- exact CR086 SHA-256 `11296a4e658f37c109a2cc953be0ea7db8e2fbde6286ac483e0466f52f4af888`

The CR086 helper implementation itself is used as the donor for mechanics-based latent-supply estimation and cash-at-risk SELL ordering; no reimplementation drift is permitted in Phase 1.

## Treatments

### `CR053_BASE`

Exact CR053 package, byte-identified above.

### `CR053_LATENT_PRIORITY`

At every step:

1. obtain the exact CR053 action for the current clock;
2. update the exact CR086 mechanics-only latent-supply estimator from legal observation transitions;
3. leave `farmer` unchanged;
4. leave every `hands` action unchanged;
5. leave the complete market-order multiset unchanged: same operations, items and quantities;
6. only reorder existing market orders when the CR086 cash-at-risk priority operator identifies urgent SELLs.

The treatment cannot add, remove or resize an order.

Runtime features remain legal: public farms, public market, public `town.unlocked_shops`, own private state and mechanics-derived latent bounds. No identity, rating, EpisodeId, hidden seed, future state or direct opponent-private state is used.

## Phase 1 population panel

Use exact packages only:

- CR052_REAL (~1749 hosted checkpoint);
- CR053_REAL (~2064.8 hosted checkpoint);
- CR083 (~1619.9 hosted checkpoint);
- CR086 (~1612.6 hosted checkpoint).

The purpose is **causal option viability and heterogeneity**, not prediction of hosted rating. We already know local exact-byte ordering can reverse hosted ordering.

Evaluation:

- engine `kaggle-environments==1.32.7`;
- seeds `91301..91308`;
- both seats;
- 16 games per treatment/opponent edge;
- 4 opponent edges;
- 64 episodes per treatment, 128 total;
- fresh package/module state for every episode;
- original final holdout untouched;
- no automatic Kaggle submission.

## Mandatory mechanics gates

For every treatment action call:

- `farmer` must equal exact CR053;
- `hands` must equal exact CR053;
- normalized market-order multiset must equal exact CR053;
- all episodes must end `DONE/DONE`;
- treatment must produce at least one actual market-order reordering over the complete Phase-1 corpus.

Any violation is infrastructure/mechanics failure and carries no strategic interpretation.

## Primary metrics

For each opponent and treatment report:

- W/L/T;
- seat-balanced score `(W + 0.5*T)/N`;
- mean final reward margin;
- number of treatment reordering activations.

Then compute `CR053_LATENT_PRIORITY - CR053_BASE` edge-score deltas on identical opponent/seed/seat support.

Terminal money is diagnostic only. **W/L coverage is primary.**

## Frozen decisions

### A. Static option transfer PASS

`CR091_LATENT_OPTION_TRANSFER_PASS_ADVANCE_ROUTER`

Requires all mechanics gates plus:

- mean edge-score delta >= `+0.04`;
- at least 3/4 opponent edges have delta >= `0`;
- no opponent edge regresses by more than `0.125`;
- at least one edge improves by at least `0.125`.

Interpretation: the option is sufficiently transferable to retain as a first hierarchical action and advance to a broader population/router gate.

### B. Heterogeneous option value detected

`CR091_HETEROGENEOUS_OPTION_VALUE_ADVANCE_ROUTER_DISCOVERY`

If static PASS fails, but all mechanics gates pass and:

- at least one edge improves by >= `0.125`; and
- at least one edge regresses by <= `-0.125`.

Interpretation: always-on use is wrong, but the option has enough conditional value to justify learning a legal public-state router. Opponent identity itself cannot be a runtime feature; Phase 2 must discover state variables that explain the differential value.

### C. Option closed

`CR091_LATENT_OPTION_FAIL_CLOSE_OPTION`

If mechanics pass but neither A nor B occurs, close this transplanted CR086 ordering option on CR053. Do not tune its cash-risk threshold after seeing the result. Move to the next separable option family (H1/H1B timing or another elite-informed market option).

### D. Mechanics failure / dormant option

- `CR091_MECHANICS_FAIL`
- `CR091_OPTION_DORMANT`

Repair only infrastructure/semantic implementation errors. A genuinely dormant operator is not evidence for strategic value.

## Phase 2 if A or B advances

Phase 2 is a **public-state option-value router**, not an opponent-ID router.

Candidate state features may include only legal variables available at runtime, such as:

- CR086 latent-supply/cash-risk summaries;
- current prices/inventory;
- public shop sequence;
- day/hour;
- own cash/inventory;
- public crop/animal production state;
- action-capacity proxies.

The learning target is counterfactual W/L advantage of `LATENT_PRIORITY` versus `BASE` on matched episodes/states. Economic proxies may be features but cannot be the promotion target.

Only after an option/router survives broad heterogeneous population W/L testing should it be packaged for a hosted sensor.
