# Kculture strategic doctrine: robust baseline + shrinkage exploitation

Date frozen: 2026-08-30

## Executive idea

Treat the strongest robust current-meta policy as a practical **equilibrium proxy / baseline**, not as a proven GTO solution. Start close to that baseline when evidence about the opponent is weak. Infer the opponent's behavioral lineage from public game state and action history, estimate deviations from the lineage prior, and increase exploitation strength only as evidence accumulates.

This is analogous to poker play that begins from a strong GTO-like baseline and moves toward an exploitative best response with statistical confidence.

## What current evidence does and does not establish

The current ladder shows heavy lineage reuse and deterministic openings. This does **not** prove that Kaggriculture is solved or that any public route is a Nash/minimax strategy.

Evidence against the 'solved GTO' interpretation:

- CR004--CR010 found predictable opponent sale timing from public state/history and measurable causal economic value from acting on it.
- CR013/CR014 showed that aggressive ordering can create both unique wins and unique catastrophic losses; therefore policy details remain strategically consequential.
- CR023 raw Stage A found top-11/top-19 open-loop tapes with large broad gains over CR008 but nonzero harmful outcome flips and slight harm in the preregistered close subset. A true unexploitable GTO interpretation is therefore unsupported.
- Current leaders share openings/lineages, but the strongest leaders diverge later and use sparse feedback.

Operational conclusion: a common high-performing route should be treated as a **meta prior**, not as a proof of equilibrium.

## Architecture

### 1. Robust baseline

Use the strongest legally reproducible and independently validated backbone available under the current game/economic regime.

Requirements:
- strong paired W/L performance, not merely high bank value;
- both-seat robustness;
- current-regime validation;
- no dependence on opponent identity;
- low catastrophic tail risk.

The baseline is what the agent does when it has insufficient evidence to exploit.

### 2. Behavioral lineage posterior

Infer a distribution over opponent policy families from observable behavior only:

P(lineage | public farm state, action history, market actions, timing)

Useful signals can include:
- opening action sequence;
- crop/animal composition;
- hire/land timing;
- product sale timing and quantities;
- market order position;
- deviations from known route templates.

Opponent username/team/submission identity is evaluation metadata only and must never be a runtime feature or gate.

### 3. Deviation model

For the currently inferred lineage, compare actual actions with the lineage expectation. Maintain evidence for deviations that have strategic meaning, e.g.:

- sale probability and timing;
- likely sale quantity;
- production/capacity deviation;
- cash/land/crew trajectory;
- market-order ordering;
- route branch changes.

The target is not 'identify the player'; it is 'estimate the opponent policy conditional on what has actually been observed in this episode'.

### 4. Shrinkage / evidence-weighted exploitation

Do not switch from baseline to full exploit after one observation.

A simple first form is:

    lambda = reliability * n_eff / (n_eff + kappa)

where:
- `n_eff` is effective evidence/sample size for the relevant opponent behavior;
- `kappa` is prior strength / shrinkage constant;
- `reliability` captures model calibration / posterior confidence;
- `lambda` is constrained to [0, 1].

Interpretation:
- little evidence -> lambda near 0 -> baseline;
- accumulating consistent evidence -> lambda grows smoothly;
- strong contradictory/uncertain evidence -> lambda remains small;
- abundant reliable evidence -> lambda can approach the validated exploit strength.

A Bayesian version can use posterior probabilities or Beta-Binomial / hierarchical partial pooling instead of raw `n_eff`.

### 5. How lambda changes actions

Prefer bounded interventions rather than randomly mixing two entire policies.

Examples:
- adaptive sale quantity scales with lambda;
- threshold for acting can fall gradually with posterior confidence;
- timing adjustment can widen gradually;
- order-position changes require a much higher confidence/risk gate than quantity changes;
- route-level changes require stronger evidence than local market actions.

Conceptually:

    action = baseline_action + bounded_exploit(lambda, posterior, state)

not an unconditional replacement of the entire baseline.

CR022C Stage A already points in this direction: 25% adaptive liquidation beat 50/75/100% on the preregistered selection hierarchy while preserving every Stage-A W/L outcome. This is empirical evidence that **partial exploitation can be better than maximum exploitation**.

### 6. Risk/trust region

The exploit layer must be constrained by expected W/L value and tail risk.

Candidate interventions should be rejected or shrunk when:
- posterior uncertainty is high;
- close-game W/L risk worsens;
- CVaR/tail loss is unacceptable;
- the intervention changes downstream trajectory in an uncontrolled way;
- the policy begins authorizing its own future escalation (lesson from CR015).

A practical formulation is a trust region around the baseline: only allow actions whose validated exploit distance is bounded, with larger departures requiring proportionally stronger evidence.

## Evaluation hierarchy

1. Broad paired W/L vs diverse current lineages.
2. Close-game W/L.
3. Bradley-Terry-relevant outcome conversion.
4. Mean relative terminal margin.
5. Tail/CVaR and catastrophic flips.
6. Hosted calibration only after frozen offline evidence.

Bank/coin gain is diagnostic, not the final objective.

## Replay sampling policy

Do not sample blindly by team name. Sample by **behavioral lineage + current economic regime**.

The initial top-20 atlas (up to 3 games/team) is sufficient to detect deterministic openings and major shared lineages, but not sufficient to estimate rare branches or tail deviations.

Next replay expansion should prioritize:
- more episodes for the largest/current top lineages;
- distinct lineages rather than duplicate team names;
- recent current-balance episodes;
- late-game branches and rare deviations;
- enough observations to calibrate shrinkage/posterior reliability.

## Current decision rule

We will pursue three layers in parallel, without contaminating held-out data:

1. improve the robust baseline/backbone;
2. improve local opponent forecasting and exploit quantity/timing;
3. build behavior-based lineage inference with shrinkage-controlled exploitation.

We will not blindly clone a top tape, and we will not attempt a full best response from turn 1. The intended final architecture is **strong meta baseline + progressively earned exploit**.
