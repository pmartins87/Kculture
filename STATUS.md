# STATUS — Kculture live source of truth

Updated: 2026-09-14

Authoritative branch: `fix/kaggle-parity-v1`.

## Mission

Maximize probability of a prize-winning / top-10 Kaggriculture finish before 2026-09-30 23:59 UTC. No hosted submission without a passed frozen promotion gate.

## Hosted live state

### CR083 — ACTIVE / IMMUTABLE / STILL CONVERGING

- submission: **`56199767`**
- frozen SHA-256: **`648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`**
- latest already-frozen checkpoint: **1660.3** versus CR071M **1638.8** (`+21.5`), about 76 public episodes plus validation.

No repeated polling. The next hosted checkpoint remains the predeclared 100-public-episode maturity boundary or another material decision boundary.

Earlier 36-replay freeze `34745898829`: 27W–9L overall, 0–4 versus the sampled >=2300 cohort. That evidence motivated CR086 representation work, not CR083 retuning.

## Current hosted frontier

Latest already-frozen read-only top-10 checkpoint from this work session:

1. Majkel1337 `3239.9`
2. Mengfei Li `3065.9`
3. Artem The Farmer `3064.4`
4. ymg_aq `3020.9`
5. SpaTaro `3019.2`
6. Otter Vibe `3005.0`
7. redblackbst `2991.3`
8. feel the agi `2990.5`
9. binghua `2968.2`
10. Subramanya N `2965.4`

Approximate older full-snapshot thresholds: rank100 `2782.8`, rank500 `2578.1`, rank1000 `2300.8`, rank2000 `1679.7`.

## Closed / quarantined

- CR078: closed.
- CR079 SpaTaro 1-NN: FAIL / closed.
- CR080 replay-route stitching: FAIL / closed.
- CR081 market-prefix transplant: catastrophic FAIL / closed.
- CR082 state-conditioned teacher 1-NN: catastrophic FAIL / closed.
- CR084 critical late-livestock rescue: CLOSED / DO NOT RETUNE.
- CR085 Pareto-guarded adaptive switch: CLOSED / DO NOT RETUNE. Gate A `34761593920`: 3W–3L–26T = `0.5000`, mean `-147.46875` versus CR083.

Behavioral imitation/replay stitching, CR084 FEED rescue and CR085 Pareto gating remain closed.

## CR083 local evidence

Canonical promotion `34715575445`: CR083 vs CR071M 45W–1L–18T = `0.84375`, mean `+172.5`, neutral guardrail deltas versus CR053/CR061/CR065, zero execution errors.

## CR086 — opponent private-inventory representation

### FEASIBILITY PASS

The legal estimator represents opponent private premium-stock using public market/farm transitions, our own private state and frozen mechanics. No opponent-private observation/action, identity, rating, EpisodeId, hidden seed or future state is used at runtime.

Independent confirmation on a different preselected second replay from each of 10 strong teams, both seats, **100,660 commodity-step observations**:

- MAE **1.25005** — PASS (`<=3`);
- p95 absolute error **9** — PASS (`<=10`);
- interval coverage **0.969462** — PASS (`>=0.95`);
- `stock >= 10` classification accuracy **0.956338** — PASS (`>=0.90`).

Decision: **`OPPONENT_INVENTORY_REPRESENTATION_FEASIBILITY_PASS`**.

Evaluator: `tools/cr086_opponent_inventory_estimator_eval.py`.

This proves representation quality only; it does not prove W/L value.

## CR086 — public strong-backbone acquisition COMPLETE

Read-only acquisition run **`34790801576`**, artifact **`10327672303`**, artifact digest `sha256:69a8e038d50ed86c356243ddf34502ff84a100b5432bf5725c9ab57829823308`.

All four requested public notebooks were pulled successfully. Three generate deterministic executable agents:

1. **Shape the Shop Work the Pasture (TOP 10)** — deterministic 13-member package, archive SHA-256 `fa9e7eb1a0174a1bf292fb4d47bd209defed929758214d3506e050a68ee5f98f`, entrypoint `kaggriculture_e776_agent`.
2. **V29-R1 Adaptive Market Hysteresis** — standalone package SHA-256 `8dc512911c0173483211314f63cbf1d7e460cad33dfbc02f0f77d023f6d809fe`, `main.py` SHA `c4a6964cec3c1c99207c32bb1fd91e53c3ec01e6890da5734331cbeab1cc1267`.
3. **Farming Score V3: Replay Revised** — standalone package SHA-256 `5cde13b09e9506f24b2f5df05719b597fe07ebbb6dead7da12894beda203e419`, `main.py` SHA `d36ae976ad4a6316e6c1a27a5d04e9cc8e30300f21bdd31e749127c67a9311c4`.

The Tetsutani notebook is analytical/visual rather than a standalone agent builder and is excluded from direct H2H.

Static architecture audit: `docs/strategy/CR086_PUBLIC_BACKBONE_ARCHITECTURE_AUDIT_2026-09-14.md`.

## CR086 — frozen public-backbone H2H benchmark ACTIVE

Protocol frozen **before results**: `docs/strategy/CR086_PUBLIC_BACKBONE_BENCHMARK_PROTOCOL_2026-09-13.md`.

Workflow/run: **`34798209070`**, commit `bb4c89fbe1b6b91d673aee8f46bd27367c6ffd4b`.

Frozen design:

- exact `kaggle-environments==1.32.7`;
- 16 fresh seeds × both seats = 32 games per public agent;
- master `9160861` with seed firewall against all prior masters;
- each unmodified public package vs exact CR083;
- promising screen: zero errors, score rate `>=0.5625`, mean margin `>0`;
- no tuning from partial results and no hosted submission.

The run was checked exactly once after creation and was `queued`. **Do not poll again in this turn.**

## Static architecture result before H2H

- CR083: route/tape architecture with market counterplay, room guard, dead-stock liquidation and seed-demand clamp; no explicit opponent-stock model or hysteresis.
- Adaptive Market Hysteresis: stateful public-flow pressure, reserves, price gates and bounded tranches; natural complement to our hidden-stock estimator.
- Farming Score V3: two-route policy plus 72-turn affordability guard; closest to existing CR071M/CR083 architecture.
- TOP 10: structural production adaptation — demand-aligned COW/SHEEP substitution, sale reallocation, latent-pasture activation and extra animal/hand under fail-closed guards.

No CR086 candidate is frozen yet. If a public backbone passes the benchmark, inspect that exact architecture plus provenance/license before testing an inventory-aware value layer. If none passes, use the mechanisms as design evidence and build a fresh architecture rather than retuning the spent benchmark.

## Binding policies

- Authenticated Kaggle API first.
- Exact H2H uses `kaggle-environments==1.32.7`, isolated packages and both seats.
- Original final holdout remains sealed.
- Closed hypotheses remain closed unless genuinely new evidence invalidates closure.
- No identity/EpisodeId/rating/hidden seed/future/opponent-private runtime features.
- CR083 remains immutable at its frozen SHA.
- **No repeated live or CI polling.**
- **No hosted submission until a genuinely independent architecture passes direct, legacy-guardrail and high-strength-population layers plus provenance/license review where applicable.**
