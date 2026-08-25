# Public benchmark research — 2026-08-25

This note separates **public external evidence** from Kculture-owned strategy conclusions. Public agents are benchmarks/opponents unless explicitly promoted through Kculture's own validation gates.

## 1. COK-ZhangZiliang/Kaggriculture — strongest current public benchmark found

Source repository: `https://github.com/COK-ZhangZiliang/Kaggriculture`

Frozen benchmark used by Kculture:

- public agent: V8 at commit `779caaec88a441345871e2d62eb5de93606b7b52`;
- `main.py` SHA-256: `faf57412e2c56dcc669043865a185324bab9952d865abccc2203284e854eceb3`;
- license: Apache-2.0;
- upstream repository status commit reviewed: `c3e2e89a06c9f7874f3ecf73163b07e00e3517e8` (2026-08-24);
- upstream reports 66 passing tests and full starter/random smoke on `kaggle-environments==1.32.7`;
- upstream leaderboard snapshot at 2026-08-23T15:45:18Z: V7 dynamic score 2626.4, rank 53/6021;
- upstream fixed-tape comparison reports V7 140-1-59 and V8 145-1-54 over 200 games, with mean-margin improvement +822.085;
- upstream closed-loop targeted panel reports V7 56/88 versus V8 84/88 on its selected failure-trigger cases.

The ranking/rating are dynamic historical snapshots, not guarantees of present or final strength.

### Public strategy shape

The V8 documentation describes several shop-conditioned production experts, choosing among cow/sheep mixes such as 6C/12S, 10C/4S, 6C/8S, and 8C/6S. It uses visible farm-state divergence to disambiguate one shop-prefix case. It also documents weed recovery, purchase/placement reconciliation, seed-feasibility guards, market sell ordering, action caching, and terminal liquidation.

**Kculture interpretation:** high-performing play appears to depend on a long-horizon production route plus robust execution/recovery and public-demand adaptation. This is a research hypothesis, not an official mechanic.

## 2. lonespear/kaggriculture — useful historical public benchmark

Source: `https://github.com/lonespear/kaggriculture`

The repository handoff dated 2026-08-07 reported a live V18 rating that reached 1000 and later settled around 921 after 24 rated episodes (13–11). Its tuning notes favored approximately 8 cows, 24 strawberries, 10 wheat tiles, 2 quadrants, and 11 hands; a more aggressive three-quadrant/44-strawberry/14-hand route lost heavily because of added hire cost.

**Kculture interpretation:** simply scaling land/workers/crop count can destroy profitability even when action throughput rises. Hiring needs cash-runway and marginal-return logic, not a fixed “more is better” rule.

Version caveat: this evidence predates the 2026-08-15 environment market-curve change and must not be treated as current calibration.

## 3. Seyamalam/Kaggriculture — public route/recovery evidence

Source: `https://github.com/Seyamalam/Kaggriculture`

Public documentation describes a route with three quadrants, 12 hands, eight cows, six sheep, wheat/melon/strawberry production, market-aware crop scoring, seed-accounting guards, demand-matched premium sales, terminal liquidation, and defensive fallback/recovery behavior.

**Kculture interpretation:** independent public projects converge on a similar architecture: deterministic route planning + livestock + premium crops + parallel labor + explicit recovery + terminal cash conversion.

## 4. Competition metagame risk: trajectory copying

A public Kaggle discussion raised concern that agents can copy/replay strong visible trajectories because direct interaction is limited and a major common random driver is town-shop unlock order. Whether or not that critique fully captures the game, it exposes a real evaluation risk: fixed open-loop routes can look excellent against narrow tests and still be exploitable or fail under demand-path variation.

Kculture response:

- test both seats;
- keep development/validation/held-out environment seeds separate;
- include strong public policies as closed-loop opponents, not only fixed action tapes;
- measure exact money margins and failure modes, not just a scalar rating;
- prefer policies that condition on current public shop/market/farm state over blind replay where the adaptation has held-out value;
- preserve strategic diversity in the final two submissions.

## 5. Research priorities implied by the public evidence

1. Reproduce at least one strong public 1.32.7 policy locally as a hash-pinned opponent.
2. Quantify what creates the large earnings gap over the starter: labor count/timing, land expansion, crop mix, livestock mix, town demand routing, market timing, and terminal liquidation.
3. Build Kculture's own deterministic economic route before adding opponent-reactive logic.
4. Test route-conditioned adaptations on held-out shop sequences and strong closed-loop opponents.
5. Only reuse third-party implementation details when license/attribution and competition rules permit; keep provenance explicit.

## Provenance rule

Kculture's own `main.py` must never silently absorb public code. Any copied/derived portion must have an explicit source, license, exact upstream revision, modification note, and independent local evidence. Public artifacts fetched solely as opponents remain under `artifacts/` and are hash-verified against `configs/public_opponents.json`.
