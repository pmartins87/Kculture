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
- **Direct public-backbone adoption for CR086: CLOSED / DO NOT RETUNE.** Frozen characterization run `34798209070` swept all three public executable agents 0–32 versus exact CR083.

Behavioral imitation/replay stitching, CR084 FEED rescue, CR085 Pareto gating and direct adoption/retuning of the three screened public backbones remain closed.

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

## CR086 — public strong-backbone characterization COMPLETE / FAIL FOR DIRECT ADOPTION

Acquisition run `34790801576`, artifact `10327672303`, froze three deterministic executable public packages plus one analytical notebook.

Frozen benchmark run **`34798209070`**, master `9160861`, 16 fresh seeds × both seats, exact reference runtime, zero execution errors:

| Public agent | Frozen package SHA-256 | W-L-T vs CR083 | Score rate | Mean margin |
|---|---|---:|---:|---:|
| `shape_shop_top10` | `fa9e7eb1a0174a1bf292fb4d47bd209defed929758214d3506e050a68ee5f98f` | **0-32-0** | **0.0000** | **-9416.34375** |
| `adaptive_market_hysteresis` | `8dc512911c0173483211314f63cbf1d7e460cad33dfbc02f0f77d023f6d809fe` | **0-32-0** | **0.0000** | **-10710.0** |
| `farming_score_v3` | `5cde13b09e9506f24b2f5df05719b597fe07ebbb6dead7da12894beda203e419` | **0-32-0** | **0.0000** | **-8996.1875** |

All three lost 16/16 from each candidate seat. Decision: **`CLOSE_DIRECT_PUBLIC_BACKBONE_ADOPTION_MOVE_TO_CLEANROOM_MARKET_VALUE_LAYER`**.

Result record: `docs/strategy/CR086_PUBLIC_BACKBONE_BENCHMARK_RESULT_2026-09-14.md`.

Interpretation: public/historical hosted score is not a substitute for our exact paired H2H, and CR083 is extremely strong locally against these route/heuristic agents. At the same time, CR083 remains far from the hosted ~3000 frontier, so the local-vs-hosted proxy gap is now even more explicit.

The public notebooks remain architecture research evidence only:

- Adaptive Market Hysteresis: public-flow memory, reserves and bounded selling tranches;
- Shape Shop: structural production adaptation/capacity activation;
- Farming Score V3: budget guarding.

Do not retune these packages on the spent benchmark.

## Active CR086 direction — clean-room latent-supply value layer

CR086 now stays on the exact CR083 physical backbone and uses the independently validated opponent-stock representation as a first-class state variable.

Before a candidate is frozen:

1. audit official market transition, pricing and execution-order mechanics;
2. audit CR083's current SELL / counterplay / room-guard / dead-stock behavior;
3. derive an explicit economic value quantity from **latent opponent supply**, not another fitted route threshold;
4. prefer mechanics-derived sell-now/hold, saturation-risk or scarcity/glut logic;
5. freeze the value rule and fresh evaluation boundaries before testing performance.

No CR086 policy candidate is frozen yet and no hosted submission is authorized.

## Binding policies

- Authenticated Kaggle API first.
- Exact H2H uses `kaggle-environments==1.32.7`, isolated packages and both seats.
- Original final holdout remains sealed.
- Closed hypotheses remain closed unless genuinely new evidence invalidates closure.
- No identity/EpisodeId/rating/hidden seed/future/opponent-private runtime features.
- CR083 remains immutable at its frozen SHA.
- **No repeated live or CI polling.**
- **No hosted submission until a genuinely independent architecture passes direct, legacy-guardrail and high-strength-population layers plus provenance/license review where applicable.**
