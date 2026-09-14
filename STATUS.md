# STATUS — Kculture live source of truth

Updated: 2026-09-13

Authoritative branch: `fix/kaggle-parity-v1`.

## Mission

Maximize probability of a prize-winning / top-10 Kaggriculture finish before 2026-09-30 23:59 UTC. No hosted submission without a passed frozen promotion gate.

## Hosted live state

### CR083 — ACTIVE / IMMUTABLE / STILL CONVERGING

- submission: **`56199767`**
- frozen SHA-256: **`648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`**
- submitted: `2026-09-13 05:21:53 UTC`
- latest authenticated checkpoint already frozen in this work session: **1660.3**
- CR071M control at same checkpoint: **1638.8**
- observed CR083 lead: **+21.5**
- about **76 public completed episodes** plus validation at that checkpoint.

No repeated polling. The predeclared maturity rule remains: make the next hosted checkpoint only at/after 100 public completed episodes or another material decision boundary.

Earlier 36-replay forensic freeze `34745898829`: 27W–9L, but 0–4 versus the sampled >=2300 cohort. This motivated high-strength validation and CR086 representation work, not CR083 retuning.

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
- CR080 replay-route stitching: FAIL / closed; economic-state aliasing.
- CR081 market-prefix transplant: valid catastrophic FAIL / closed.
- CR082 state-conditioned teacher 1-NN: valid catastrophic FAIL / closed.
- CR084 critical late-livestock rescue: **CLOSED / DO NOT RETUNE**. Promotion `34758417896`: CR084 vs CR083 12W–10L–42T = `0.515625`, mean `-106.625`; temporal proxy found zero actual rescue opportunities.
- CR085 Pareto-guarded adaptive switch: **CLOSED / DO NOT RETUNE**. SHA `eb7bac5c5619e70d1ef81dd18f28b642b96326be31ae50354cdca7770531bdf7`; Gate A `34761593920`: 3W–3L–26T = `0.5000`, mean `-147.46875` versus CR083.

Behavioral imitation/replay stitching, CR084 FEED rescue and CR085 Pareto switch gating remain closed.

## CR083 local evidence

Canonical promotion `34715575445`:

- CR083 vs CR071M: 45W–1L–18T = `0.84375`;
- mean margin `+172.5`;
- guardrail score delta vs CR053/CR061/CR065: `0 / 0 / 0`;
- zero execution errors.

A fresh same-master row in the CR084 panel reconfirmed CR083 vs CR071M: 57W–1L–6T = `0.9375`.

## CR086 discovery — major representation result

### Opponent private-inventory estimator: FEASIBILITY PASS

The new legal representation estimates opponent private stock for premium/sell-only commodities from public state transitions, our own private state and frozen mechanics. Runtime does **not** use opponent private state/actions, identity, rating, EpisodeId, hidden seed or future state.

Primary commodities:
`CARROT, TOMATO, STRAWBERRY, MELON, EGG, MILK, WOOL`.

Key mechanics:

- before first observed commodity price `$1`, conservation gives a strong point estimate;
- at/after `$1`, invisible floor sales destroy point identifiability, so point becomes `0` and uncertainty interval is maintained;
- separate zero-loss upper accounting handles harvest+production ambiguity and same-turn WATER→HARVEST possibilities mechanically.

The first top-10 holdout was spent after revealing an incomplete upper-bound implementation. It was not reused for certification. A mechanics-only correction was frozen and tested on a **different, preselected second replay from each of the same top-10 teams**, both seats.

Independent confirmation result over **100,660 commodity-step observations**:

- MAE: **1.25005** units — PASS (`<=3`);
- p95 absolute error: **9** — PASS (`<=10`);
- interval coverage: **0.969462** — PASS (`>=0.95`);
- `stock >= 10` classification accuracy: **0.956338** — PASS (`>=0.90`);
- signed bias: `-0.76501`;
- mean interval width: `7.41434`, median `0`.

Decision: **`OPPONENT_INVENTORY_REPRESENTATION_FEASIBILITY_PASS`**.

Records:

- `docs/strategy/CR086_OPPONENT_INVENTORY_ESTIMATOR_FEASIBILITY_2026-09-13.md`
- `docs/strategy/CR086_OPPONENT_INVENTORY_ESTIMATOR_V2_FROZEN_BEFORE_HOLDOUT_2026-09-13.md`
- `docs/strategy/CR086_INVENTORY_ESTIMATOR_V2B_MECHANICS_FIX_AND_CONFIRMATION_HOLDOUT_2026-09-13.md`
- `docs/strategy/CR086_OPPONENT_INVENTORY_ESTIMATOR_CONFIRMATION_RESULT_2026-09-13.md`
- reproducible evaluator: `tools/cr086_opponent_inventory_estimator_eval.py`

This PASS makes the representation eligible for later policy research. It does **not** prove that using it improves W/L and does not authorize a hosted submission.

### Public strong-backbone acquisition

Read-only workflow: `34790801576`, created from commit `0635ee727f0b99c1ee21c55c9c4ead39d3ba4ab6`.

Targets include public high-scoring Kaggriculture notebooks such as `shape-the-shop-work-the-pasture-top-10`, `adaptive-market-hysteresis` and `farming-score-v3-replay-revised`.

The workflow was checked exactly once in this response and was `in_progress`. **Do not poll it again until the next user turn/material decision boundary.** No submission command exists in the workflow.

## Active research direction

CR086 should now combine evidence from two independent sources before a candidate is frozen:

1. audit/benchmark public strong backbones and their licensing/provenance;
2. design a market-value policy that can actually exploit the now-validated opponent-stock estimate/bounds.

Do not turn the estimator directly into an arbitrary threshold patch. It needs an explicit value mechanism (market pressure, liquidation timing, scarcity/glut response, or strong-backbone integration) and a predeclared gate.

## Binding policies

- Authenticated Kaggle API first.
- Exact H2H: `kaggle-environments==1.32.7`, isolated packages, both seats.
- Original final holdout remains sealed.
- Closed hypotheses remain closed unless genuinely new evidence invalidates closure.
- No identity/EpisodeId/rating/hidden seed/future/opponent-private runtime features.
- CR083 remains immutable at its frozen SHA.
- **No repeated live polling.**
- **No new hosted submission until a genuinely independent architecture passes direct, legacy-guardrail and high-strength-population layers plus provenance/license checks where applicable.**
