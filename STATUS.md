# STATUS — Kculture

Last updated: 2026-08-29

## Mission

**Goal: maximize probability of a top-10 final finish in Kaggriculture; each top-10 position pays US$5,000.**

Repository `pmartins87/Kculture` is the source of truth. Hosted/live evidence outranks local proxy stories when they conflict.

**Held-out remains 32/32 sealed.**

## Hosted reality — 2026-08-29 calibration

Frozen snapshot and interpretation: `docs/HOSTED_CALIBRATION_2026-08-29.md`.

Latest observed Kaggle UI snapshot:

- R4B_A control: **205.9**;
- CR008 adaptive append: **1705.6**;
- CR011 adaptive early: **1723.3**;
- R4B_B byte-identical repeat, submission `55868963`: **188.4**;
- Kaito V43 public reference, submission `55868969`: **1211.7**.

Key calibration:

- R4B temporal-control spread = **17.5**;
- CR011 − CR008 = **17.7**, therefore noise-scale in this window;
- CR008 − R4B midpoint = **+1508.45**.

**Decision:** CR008 append adaptation is the canonical hosted baseline. Opponent-aware response is the strongest demonstrated improvement in Kculture. Early queue placement has no hosted advantage beyond measured noise and has severe local tail risk.

## Frozen / relevant candidates

### CR008 — canonical hosted baseline

- `candidates/cr008_adaptive_frontrun.py`
- blob `8e1c26202c3101c19668bf61edf2ae51d4329d5d`
- high-confidence identity-free public-opponent-state SELL forecast;
- deployed products CARROT/STRAWBERRY;
- appends full available same-turn sale;
- latest observed hosted score **1705.6**.

### CR011 — research arm only

- `candidates/cr011_adaptive_early_order.py`
- blob `c4f1cb79f3c20b8229ab09e00a6878289cf9648d`
- same forecast as CR008 but early queue placement.

CR014B/C decomposition showed the critical five close outcome flips were caused by early positioning: four W→L vs one L→W. Hosted CR011−CR008 is only noise-scale, so CR008 remains preferred.

### CR015 — VALIDATED / HOSTED ELIGIBLE

- `candidates/cr015_liquidation_phase_early_order.py`
- blob `fabd4bc398e7eadcfd1d44add4d0e593315140e8`
- 432 fresh preregistered pairs, zero errors;
- vs R4B combined mean relative gain **+149.62**;
- favorable W/L **2**, unfavorable **0**;
- package parity 28,760 states / zero mismatches;
- official Kaggle entrypoint PASS both seats.

Hosted-ready archive SHA256: `41d35a97ebe714a3cb71506e17ec1e629b4a9628cacd688be7e79d524fd75c54`.

### CR020 — REJECTED

Stage A 216/216, zero errors; one favorable / zero unfavorable vs R4B, but mean relative **-70.84/game** vs CR015. No Stage B, no hosted slot.

### CR021A — CLOSED / NO-TRIGGER FAIL

Run `33261563880`, aggregate job `99126072218`, artifact `9717580986`.

- 216/216 fresh Stage-A pairs;
- zero mechanical errors;
- **0 triggers, 0 TOMATO plants, 0 harvest interventions**;
- therefore scientific gate failed;
- no Stage B and no threshold rescue on the same seeds.

CR016 remains useful architecture evidence (TOMATO/EGG demand-supply gaps), but this one-slot conservative TOMATO implementation is closed. Research priority returns to opponent adaptation.

## Opponent-adaptation evidence chain

- CR004: opponent public state improves OOT prediction; median error improvement **7.10%**.
- CR005: strong four-turn SELL forecasts.
- CR006: broad low-threshold reaction failed on precision.
- CR007: high-confidence CARROT/STRAWBERRY triggers reached **97.3%** combined precision.
- CR008: append adaptation produced the major hosted breakthrough.
- CR009: forecast timing already correct.
- CR010: in-turn order is economically causal.
- CR011: early placement can improve money but creates severe boundary pathologies.
- CR012/013/014/014B/014C: attributed the pathology to early positioning/state cascade rather than opponent identity.
- CR015: validated conservative placement refinement, hosted eligible.
- CR020: rejected.

## CR022 — ADAPTIVE V2 — PRIMARY RESEARCH

Frozen research design: `docs/ADAPTIVE_V2_RESEARCH_PLAN.md`.
Exact public-agent review: `docs/TOP_PUBLIC_ARCHITECTURE_REVIEW_2026-08-29.md`.

### Why

Exact public package inspection shows strong current agents generally use a **strong route/replay backbone + sparse heuristics**:

- Rayk/Tetsu: hard public-farm clone distance + own future route sale schedule + exact market-impact/demand ordering;
- Tactical: static hazard-by-step, 0.55 threshold, fixed 50% median quantity, cap 30, cooldown 8;
- Boatlee: public-state route portfolio selected from shops/opponent money/spending and market overlays;
- Kaito V43: strong backbone + sparse shop feedback; sophisticated quantity/MPC components exist in library but are conservatively not deployed when grouped holdouts do not support them.

**Adaptive V2 headroom:** replace clone distance / static hazards / fixed fractions with calibrated state-conditioned opponent forecasts, quantity/order-position distributions, route-archetype belief, exact market counterfactuals and downside-aware abstention.

### Frozen Adaptive V2 modules

1. **Behavior atlas / route fingerprint** — quantify open-loop rigidity vs real adaptation.
2. **Probabilistic forecast** — P(SELL product within h), h=0..4; quantity and order-position distribution.
3. **Forecast residual / surprise state** — deviation from expected route/economy.
4. **Exact market counterfactual engine** — abstain vs 25/50/75/100% and timing/order alternatives.
5. **Risk-aware sparse MPC** — maximize expected relative value while penalizing CVaR/downside and own-cash risk.
6. **Conservative abstention** — sophistication only when it survives grouped/OOT evidence.

No opponent/team identity is permitted as an agent feature or gate.

### CR022A — current-top replay atlas

Created:

- `tools/collect_top_ladder_snapshot.py`;
- `tools/top_ladder_behavior_atlas.py`;
- automated top-20 × up to 3 recent public episodes workflow.

First authenticated run safely stopped because GitHub repository secret `KAGGLE_API_TOKEN` is not configured. No credential was exposed. This is a data-access task only, not a strategic blocker: official daily top-episode datasets remain publicly downloadable via `kagglehub`.

### CR022B — recent official top-episode forecast tournament — RUNNING

Workflow run: **33272910444**.

Protocol frozen before results:

- attempts official 2026-08-27/28/29 episode datasets;
- newest available date = chronological OOT test;
- top 20 episodes/date;
- episode-grouped fit/calibration split;
- compare frozen CR007 with regularized logistic and calibrated histogram gradient boosting;
- targets CARROT/TOMATO/STRAWBERRY/MELON SELL within four turns;
- also records first-sale delay, quantity and order position for CR022C.

No strategy candidate may be built from predictive metrics alone. Response counterfactual evidence is required.

### Clock/seat diagnostic — separate robustness line

A Kaggle discussion reports stored seat-1 `observation.step=None` under 1.32.7. Our direct agent-input probe run `33272723362` saw **719/719 numeric steps in both seats**, with zero day/hour mismatch. Therefore an engine-level bug is **not reproduced in the object actually delivered to our probe agent**.

COK/R4B does depend directly on raw `step`, so a neutral fallback derivative was created for fault injection only:

- `candidates/cr022_clock_safe_cr008.py`;
- normal behavior must be exactly CR008 when `step` exists;
- only R4B/COK backbone clock is reconstructed from day/hour if raw step is missing;
- CR008 learned feature semantics remain unchanged.

Audit run **33273005851** is testing normal parity plus forced `step=None` recovery. This is not Adaptive V2 strategy evidence.

## Next hosted-reset policy

Five valid daily slots remain a perishable information budget. Current priority order is provisional until active diagnostics close:

1. **CR008_A exact control**;
2. **CR015**;
3. strongest newly validated Adaptive V2 / high-information diagnostic arm, if one exists;
4. **CR008_B exact control**;
5. second predeclared high-information arm.

Do not use CR020 or CR021. Do not spend a slot on CR011 solely because it is ~17.7 above CR008 in the current snapshot.

A clock-safe CR008 arm is eligible only if its fault-injection audit passes and we decide hosted seat behavior is worth one information slot; local parity alone is not evidence of strength.

## Exact continuation

1. Finish CR022B and determine whether current top-episode data supports a stronger probabilistic opponent model than CR007.
2. Use the same recent replay corpus to model sale quantity and order position; build CR022C exact response counterfactuals.
3. Do **not** promote a model because of AUC alone: require calibration, actionable precision/coverage and causal response value.
4. Finish clock-safe audit; keep it operationally separate from strategic Adaptive V2 work.
5. When convenient, configure GitHub Actions secret `KAGGLE_API_TOKEN` once, then run exact current top-20 replay atlas.
6. First Adaptive V2 candidate must remain a sparse overlay over frozen CR008, use fresh preregistered data and report worst-tail paired deltas/CVaR.
7. Keep all **32/32 held-out sealed**.

## Frozen environment / evaluation facts

- `kaggle-environments==1.32.7`;
- official terminal reward = own bank money;
- winner = higher final bank balance;
- final ranking = Bradley–Terry tournament after the submission deadline/run-on window;
- market/town economy is shared and market-order sequence is economically causal;
- W/L conversion and broad matchup coverage outrank isolated coin-margin optimization.
