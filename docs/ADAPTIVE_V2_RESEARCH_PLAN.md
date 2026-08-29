# Adaptive V2 — frozen research plan

Date frozen: 2026-08-29, before inspecting the new current-top replay corpus.

## Why this is now primary

The 2026-08-29 hosted calibration established that CR008 opponent-aware adaptation is the first large live breakthrough in Kculture: CR008 scored 1705.6 while byte-identical R4B controls bracketed the same window at 205.9 and 188.4. The CR011 early-order variant was only +17.7 over CR008, essentially identical to the 17.5 control drift, while close-match diagnostics showed dangerous early-order tail risk.

CR021A sparse TOMATO response completed 216 fresh Stage-A pairs with zero errors but zero actual triggers. It is closed without threshold rescue. Research priority returns to opponent adaptation.

## Core hypothesis

A strong deterministic/replay backbone plus a **probabilistic opponent model and risk-aware shared-market controller** can outperform the current CR008 binary-trigger/full-inventory response without needing end-to-end RL.

The current CR008 separates poorly between two questions:

1. what will the opponent probably do?
2. given that forecast, what should we do?

Adaptive V2 separates them explicitly.

## Data source: current-top replay corpus

Build a rolling corpus from public Kaggriculture ladder replays:

leaderboard -> top team -> strongest current submission -> newest completed public episodes -> exact replay JSON.

Raw replay artifacts are not committed. Provenance includes rank snapshot, team/submission IDs, episode IDs, recorded seat and replay SHA256. Team/submission identity may be used for grouping, leakage prevention and reporting, never as an agent feature.

The first automated snapshot requests top 20 teams and up to 3 recent public episodes per team.

## Module A — behavioral atlas / route fingerprint

Measure, before fitting any challenger model:

- first-72 / first-144 / full-game action agreement across episodes from the same submission;
- opening action hashes and route-family clustering;
- phase action mix;
- crop/animal composition trajectories;
- SELL product, quantity and market-order position;
- divergence points from the submission's own modal route;
- state context at divergence: prices, inventories, shops, own/opponent public farm and money gap.

The purpose is to determine how much of the current top is open-loop backbone versus true state response.

## Module B — probabilistic opponent forecast

Current frozen baseline: CR007 exported decision trees used by CR008.

Challenger targets, each identity-free:

- P(opponent SELL product p within h turns), h in {0,1,2,3,4};
- conditional SELL quantity distribution / quantiles;
- likely order position conditional on selling;
- later, only if supported, other economically causal market actions.

Candidate model families to compare offline:

1. regularized logistic / hazard models;
2. calibrated boosted-tree ensembles;
3. route-fingerprint mixture of experts;
4. Bayesian/archetype posterior feeding a calibrated hazard model.

No scikit-learn dependency is required in the submitted agent: winning offline models must be exported to compact pure-Python/JSON form with exact parity tests.

### Route fingerprint posterior

Top agents often share deterministic or nearly deterministic openings. Use only observed public behavior/state to infer a latent strategy archetype z:

P(z | public trajectory through t).

Then predict actions via a mixture:

P(a_opp | x_t) = sum_z P(a_opp | x_t, z) P(z | history_t).

Opponent/team name is prohibited as a feature. The posterior must be reconstructible from legal public state/history only.

### Leakage controls

- episode-grouped splits;
- submission/lineage-grouped stress split when provenance permits;
- chronological out-of-time split;
- no future-state features;
- source identity only for grouping/reporting;
- current CR007 precision/coverage remains the frozen baseline.

Primary predictive metrics:

- precision at actionable coverage;
- PR-AUC for rare SELL events;
- Brier/log loss and calibration error;
- quantity MAE/quantile loss conditional on a sale;
- order-position accuracy.

High AUC alone cannot authorize a strategy candidate.

## Module C — forecast residual / surprise state

Learn or construct a baseline trajectory forecast from the strong route backbone. Track legal public residuals such as:

- opponent money minus forecast money;
- crop/animal count minus forecast;
- shed-flow proxy minus forecast;
- market price/inventory minus expected trajectory;
- town unlock/demand deviations.

These residuals encode "deviation from forecast" and may identify the moments where static-route assumptions become wrong.

## Module D — exact market counterfactual engine

For every replay state where an opponent sale is forecast, enumerate legal intervention candidates rather than automatically dumping all stock:

- abstain;
- SELL 25%, 50%, 75%, 100% of available stock, with integer-safe quantities;
- retain CR008 append placement;
- consider alternative order placement only in states that pass explicit downside gates;
- optionally wait 1–3 turns when forecast horizon/price scenarios justify it.

Use the exact Kaggriculture 1.32.7 shared-market mechanics to simulate immediate price/inventory consequences under forecast scenarios.

For replay-derived training labels, compute causal counterfactual values for before/after/partial/abstain decisions when exact mechanics permit. Do not treat final observed reward as if it causally belonged to one local action without a counterfactual audit.

## Module E — risk-aware MPC / decision objective

Adaptive V2 is a small model-predictive controller at sparse intervention points, not a full-game planner.

For candidate action a and forecast scenarios s:

J(a) = E_s[Delta_relative(a,s)] - lambda * CVaR_alpha(downside_relative) - mu * own_cash_risk - nu * intervention_cost.

Where:

- Delta_relative is our bank effect minus opponent bank effect over the modeled market horizon;
- CVaR penalizes rare destructive tails like the CR011 early-order pathology;
- own_cash_risk prevents denial plays that damage our own trajectory too much;
- intervention_cost favors abstention when expected advantage is marginal.

Near the estimated W/L boundary, an optional bounded term may reward probability of favorable outcome conversion. This term must be calibrated on fresh non-held-out data and cannot replace the no-harm gate.

No numerical lambda/mu/nu is frozen here. They must be selected using development data only, then frozen before fresh evaluation.

## Module F — conservative policy / abstention

The successful CR008 lesson is sparse high-confidence action. Preserve it.

Adaptive V2 should intervene only when both are true:

1. forecast uncertainty is low enough;
2. exact/model-based counterfactual EV clears a material margin after downside penalty.

Introduce hysteresis/intervention budgets only if causal diagnostics show repeated cascades are harmful. Do not add complexity solely because it is mathematically sophisticated.

## Why not end-to-end RL now

Current public evidence and our own results favor a strong scripted backbone with sparse online decisions. Full RL has a huge action/state space and would discard a backbone that already works. Offline RL/contextual bandits may later be tested **only at intervention points** after the forecast/counterfactual dataset exists.

## CR022 sequence

### CR022A — current-top behavioral atlas

No candidate. Collect and characterize current-top replays.

### CR022B — forecast tournament

Compare frozen CR007 trees with challenger probabilistic models under grouped/OOT splits. No hosted submission.

### CR022C — counterfactual response optimizer

Use exact market mechanics to label/score quantity and abstention decisions. No hosted submission.

### CR022D — first Adaptive V2 candidate

Parent must remain frozen CR008. Change only the adaptive overlay justified by A-C. Fresh preregistered seeds, current-meta families, both seats, W/L-first gate, package parity.

## Promotion gate for a first Adaptive V2 candidate

Before a Kaggle slot, require:

- zero mechanical errors;
- exact exported-model parity;
- fresh candidate-specific seeds frozen before results;
- no net unfavorable W/L conversion vs CR008;
- positive W/L signal or materially broader matchup coverage plus positive relative value;
- explicit tail-risk report, including worst paired deltas;
- hosted package entrypoint/parity pass.

A pure money-margin improvement with worse W/L tails is rejected.

## Invariants

- CR008 stays immutable as canonical hosted control.
- No opponent identity feature/gate.
- No replay future leakage.
- No post-hoc threshold rescue on the same validation seeds.
- Raw top replay data stays in ignored artifacts, not Git.
- Held-out remains 32/32 sealed.
